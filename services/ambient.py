import time

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