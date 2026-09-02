import time

class ClockService:
    def __init__(self):
        # Rebuild the rendered string only when the minute actually changes.
        self._key = None
        self._text = ""

    def now_ms(self):
        return time.ticks_ms()

    def now_seconds(self):
        return time.time()

    def format_time(self):
        current = time.localtime()
        key = (current[3], current[4])
        if key != self._key:
            self._key = key
            self._text = "%02d:%02d" % key
        return self._text