"""System services: clock, config, power, memory, battery, ambient light.

Consolidated into a single module so the embedded target pays the
per-module overhead (module object, dict, qstrs) only once.
"""
import gc
import os
import time

try:
    import ujson as json
except ImportError:
    import json

class ClockService:
    def __init__(self):
        # Rebuild the rendered string only when the minute actually changes.
        self._key = None
        self._text = ""

    def format_time(self):
        current = time.localtime()
        key = (current[3], current[4])
        if key != self._key:
            self._key = key
            self._text = "%02d:%02d" % key
        return self._text


DEFAULTS = {
    # Brightness is automatic (light sensor) and the desktop is always
    # Cover Flow, so neither appears here anymore.
    "sleep_timeout": 60,
    "sound_enabled": True,
}

class ConfigService:
    def __init__(self, path="data/config.json"):
        self.path = path
        self.values = dict(DEFAULTS)
        self.load()

    def _ensure_parent(self):
        parent = self.path.rsplit("/", 1)[0] if "/" in self.path else ""
        if parent:
            try:
                os.stat(parent)
            except OSError:
                try:
                    os.mkdir(parent)
                except OSError:
                    pass

    def load(self):
        try:
            with open(self.path, "r") as stream:
                loaded = json.load(stream)
            for key in DEFAULTS:
                if key in loaded:
                    self.values[key] = loaded[key]
        except Exception:
            self.save()

    def get(self, key, default=None):
        return self.values[key] if key in self.values else default

    def set(self, key, value, save=True):
        self.values[key] = value
        if save:
            return self.save()
        return True

    def update(self, values):
        for key, value in values.items():
            self.values[key] = value
        return self.save()

    def save(self):
        try:
            self._ensure_parent()
            with open(self.path, "w") as stream:
                json.dump(self.values, stream)
            return True
        except Exception:
            return False


class PowerService:
    ACTIVE = "active"
    DIMMED = "dimmed"
    SLEEP = "sleep"
    # About two 20 FPS samples: responsive but resistant to noise.
    WAKE_CONFIRM_MS = 60
    def __init__(self):
        self.state = self.ACTIVE
        self.idle_ms = 0
        self.wake_ms = 0
        # Current brightness level in percent. Applied to the hardware by
        # Display.set_brightness(); kept here so power transitions (wake,
        # dim) can restore it.
        self.brightness = 80

    def set_brightness(self, percent):
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        self.brightness = percent
        return percent

    def activity(self):
        self.idle_ms = 0
        was_sleeping = self.is_sleeping()
        self.wake()
        return was_sleeping

    def update(self, delta_ms, timeout_seconds):
        if self.state == self.SLEEP or timeout_seconds <= 0:
            return
        self.idle_ms += delta_ms
        if self.idle_ms >= timeout_seconds * 1000:
            self.sleep()

    def observe_wake(self, active, delta_ms):
        if not self.is_sleeping():
            self.wake_ms = 0
            return False
        if active:
            self.wake_ms += delta_ms
        else:
            self.wake_ms = 0
        return self.wake_ms >= self.WAKE_CONFIRM_MS

    def sleep(self):
        self.state = self.SLEEP
        self.wake_ms = 0

    def wake(self):
        self.state = self.ACTIVE
        self.wake_ms = 0

    def is_sleeping(self):
        return self.state == self.SLEEP


class MemoryService:
    """Heap watchdog that reclaims large objects before they exhaust RAM.

    Embedded ESP32 heaps fragment easily when big pages (frame buffers,
    item lists) are created and destroyed. This service performs an
    explicit full collection when free memory falls below a low-water
    mark.
    """
    # Collect when free heap drops below this many bytes.
    LOW_WATER = 6144
    MIN_INTERVAL_MS = 1000
    def __init__(self, low_water=None):
        if low_water is not None:
            self.LOW_WATER = low_water
        self.last_collect_ms = time.ticks_ms()
        # No gc.threshold() here: it triggers a collection after N bytes
        # *allocated* since the last one (not a free-memory water mark)
        # and bypasses MIN_INTERVAL_MS, so the render loop would collect
        # every few frames. Low-water collection lives in
        # pressure()/collect_if_needed() below.

    def free(self):
        try:
            return gc.mem_free()
        except Exception:
            return 0

    def pressure(self):
        return self.free() < self.LOW_WATER

    def collect(self, force=False):
        """Run a full GC. Returns free bytes afterwards, or None if skipped."""
        now = time.ticks_ms()
        if not force and time.ticks_diff(
                now, self.last_collect_ms) < self.MIN_INTERVAL_MS:
            return None
        self.last_collect_ms = now
        try:
            gc.collect()
        except Exception:
            pass
        return self.free()

    def collect_if_needed(self, force=False):
        if force or self.pressure():
            return self.collect(force=True)
        return None


class BatteryService:
    """Battery voltage sampling and percentage estimation.

    Honest-by-design: a percentage is only reported when a real, stable
    voltage source is detected. Boards without a battery divider report
    ``available() == False`` and the UI shows a plain "on external power"
    glyph instead of a fake number.

    Probe: ADC on BATTERY_ADC_PIN (GPIO35 default) with a 2:1 divider.

    A floating ADC pin on ESP32 can drift into a plausible-looking range,
    so a battery is only accepted after a burst of samples is both
    plausible (voltage window) and stable (small spread). Otherwise the
    service latches into external-power mode.
    """
    SAMPLE_INTERVAL_MS = 1000
    PROBE_SAMPLES = 8
    PROBE_MAX_SPREAD_MV = 120
    MIN_MV = 3000
    MAX_MV = 4500
    DIVIDER = 2
    ADC_VREF_MV = 3300
    ADC_MAX = 4095
    BATTERY_ADC_PIN = 35
    EMA_DIV = 4
    LOW_PERCENT = 10
    CURVE = (
        (4200, 100), (4050, 90), (3950, 80), (3850, 70), (3750, 60),
        (3680, 50), (3600, 35), (3500, 20), (3400, 10), (3300, 0),
    )

    def __init__(self):
        self.hardware = None
        self.state = "probing"
        self.mv_ema = None
        self.last_sample_ms = 0
        self._probe_samples = []
        self._probe_last_ms = 0
        self._init_hardware()

    def _init_hardware(self):
        try:
            from machine import ADC, Pin
            adc = ADC(Pin(self.BATTERY_ADC_PIN))
            try:
                adc.atten(ADC.ATTN_11DB)
            except Exception:
                pass
            self.hardware = adc.read
        except Exception:
            self.hardware = None
            self.state = "external"

    def update(self, delta_ms=0, sleeping=False):
        if self.state == "external" or sleeping:
            return
        now = time.ticks_ms()
        if self.state == "probing":
            self._probe_step(now)
            return
        if time.ticks_diff(now, self.last_sample_ms) < self.SAMPLE_INTERVAL_MS:
            return
        self.last_sample_ms = now
        mv = self._read_mv()
        if mv is None:
            return
        if self.mv_ema is None:
            self.mv_ema = mv
        else:
            self.mv_ema += (mv - self.mv_ema) // self.EMA_DIV

    def _probe_step(self, now):
        if self._probe_samples and time.ticks_diff(now, self._probe_last_ms) < 120:
            return
        mv = self._read_mv()
        if mv is None:
            self.state = "external"
            return
        self._probe_last_ms = now
        self._probe_samples.append(mv)
        if len(self._probe_samples) < self.PROBE_SAMPLES:
            return
        lowest = min(self._probe_samples)
        highest = max(self._probe_samples)
        plausible = self.MIN_MV <= lowest and highest <= self.MAX_MV
        stable = (highest - lowest) <= self.PROBE_MAX_SPREAD_MV
        if plausible and stable:
            self.state = "battery"
            self.mv_ema = sum(self._probe_samples) // len(self._probe_samples)
        else:
            self.state = "external"
        self._probe_samples = []

    def _read_mv(self):
        try:
            raw = self.hardware()
        except Exception:
            return None
        mv = (raw * self.ADC_VREF_MV) // self.ADC_MAX
        if mv < 20:
            return None
        return mv * self.DIVIDER

    def available(self):
        return self.state == "battery"

    def percent(self):
        if self.state != "battery" or self.mv_ema is None:
            return None
        return self._curve_percent(self.mv_ema)

    @classmethod
    def _curve_percent(cls, mv):
        curve = cls.CURVE
        if mv >= curve[0][0]:
            return curve[0][1]
        if mv <= curve[-1][0]:
            return curve[-1][1]
        for i in range(len(curve) - 1):
            mv_hi, pct_hi = curve[i]
            mv_lo, pct_lo = curve[i + 1]
            if mv <= mv_hi and mv >= mv_lo:
                span_mv = mv_hi - mv_lo
                span_pct = pct_hi - pct_lo
                return pct_lo + ((mv - mv_lo) * span_pct) // span_mv
        return 0


class AmbientLightService:
    """Automatic screen brightness driven by the onboard light sensor.

    The sensor (``devlib.light``, an ADC on GPIO39) is sampled at a low
    rate and smoothed with an EMA so brief shadows (a hand passing over
    the board) do not flicker the display. Brightness only changes when
    the new target differs from the current level by more than a
    hysteresis band, which keeps OLED contrast writes rare.
    """
    SAMPLE_INTERVAL_MS = 500
    EMA_DIV = 4
    RAW_MAX = 4095
    MIN_BRIGHTNESS = 25
    MAX_BRIGHTNESS = 100
    HYSTERESIS = 5

    def __init__(self):
        self.hardware = None
        self.raw_ema = None
        self.last_sample_ms = 0
        self.brightness = None
        try:
            import devlib
            source = getattr(devlib, "light", None)
            if source is not None and hasattr(source, "read"):
                self.hardware = source.read
        except Exception:
            pass

    def available(self):
        return self.hardware is not None

    def _read_raw(self):
        try:
            value = self.hardware()
        except Exception:
            return None
        if value is None or value < 0:
            return None
        if value > self.RAW_MAX:
            value = self.RAW_MAX
        return value

    def update(self, delta_ms=0, sleeping=False):
        """Sample the sensor if due. Returns a new target brightness
        (percent) when the display should change, otherwise None."""
        if self.hardware is None or sleeping:
            return None
        now = time.ticks_ms()
        if self.last_sample_ms and time.ticks_diff(
                now, self.last_sample_ms) < self.SAMPLE_INTERVAL_MS:
            return None
        self.last_sample_ms = now
        raw = self._read_raw()
        if raw is None:
            return None
        if self.raw_ema is None:
            self.raw_ema = raw
        else:
            self.raw_ema += (raw - self.raw_ema) // self.EMA_DIV
        span = self.MAX_BRIGHTNESS - self.MIN_BRIGHTNESS
        target = self.MIN_BRIGHTNESS + (self.raw_ema * span) // self.RAW_MAX
        if target > self.MAX_BRIGHTNESS:
            target = self.MAX_BRIGHTNESS
        if self.brightness is None:
            self.brightness = target
            return target
        gap = target - self.brightness
        if -self.HYSTERESIS < gap < self.HYSTERESIS:
            return None
        self.brightness = target
        return target


class SystemContext:
    def __init__(self):
        self.clock = ClockService()
        self.config = ConfigService()
        self.power = PowerService()
        self.memory = MemoryService()
        self.battery = BatteryService()
        self.ambient = AmbientLightService()
        self.display = None
