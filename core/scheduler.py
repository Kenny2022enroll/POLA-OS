import time

class Scheduler:
    def __init__(self, fps=10):
        self.interval = 1000 // fps
        self.last = time.ticks_ms()

    def wait(self):
        now = time.ticks_ms()
        delta = time.ticks_diff(
            now,
            self.last
        )
        if delta < self.interval:
            time.sleep_ms(
                self.interval-delta
            )
        self.last = time.ticks_ms()