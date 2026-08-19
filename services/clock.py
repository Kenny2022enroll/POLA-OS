import time

class ClockService:
    def now_ms(self):
        return time.ticks_ms()

    def now_seconds(self):
        return time.time()

    def format_time(self):
        current = time.localtime()
        return "%02d:%02d" % (current[3], current[4])