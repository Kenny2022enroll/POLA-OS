import time

class BatteryService:
    """Battery voltage sampling and percentage estimation.

    Honest-by-design: a percentage is only reported when a real, stable
    voltage source is detected. Boards without a battery divider report
    ``available() == False`` and the UI shows a plain "on external power"
    glyph instead of a fake number.

    Probe order:
      1. ``devlib.battery`` (when a devlib build exposes it).
      2. ADC on BATTERY_ADC_PIN (GPIO35 default) with a 2:1 divider.

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
        self.hardware_kind = None
        self.state = "probing"
        self.mv_ema = None
        self.last_sample_ms = 0
        self._probe_samples = []
        self._probe_last_ms = 0
        self._init_hardware()

    def _init_hardware(self):
        try:
            import devlib
            source = getattr(devlib, "battery", None)
            if source is not None and hasattr(source, "read"):
                self.hardware = source.read
                self.hardware_kind = "devlib"
                return
        except Exception:
            pass
        try:
            from machine import ADC, Pin
            adc = ADC(Pin(self.BATTERY_ADC_PIN))
            try:
                adc.atten(ADC.ATTN_11DB)
            except Exception:
                pass
            self.hardware = adc.read
            self.hardware_kind = "adc"
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

    def voltage_mv(self):
        if self.mv_ema is None:
            return None
        return self.mv_ema

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