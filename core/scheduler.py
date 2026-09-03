import time

class Scheduler:
    """Adaptive frame scheduler.

    The kernel keeps two rates: a fast one for animations, transitions
    and active touch, and a slow idle one when nothing on screen is
    changing. Switching is done with ``set_idle()``; ``wait()`` always
    paces against whichever interval is currently selected, so idle
    frames cost the CPU far less than a fixed 25 FPS loop.
    """
    def __init__(self, fps=25, idle_fps=10):
        self.fast_interval = 1000 // fps
        self.idle_interval = 1000 // idle_fps
        self.interval = self.fast_interval
        self.last = time.ticks_ms()

    def set_idle(self, idle):
        self.interval = self.idle_interval if idle else self.fast_interval

    def wait(self):
        now = time.ticks_ms()
        delta = time.ticks_diff(now, self.last)
        if delta < self.interval:
            time.sleep_ms(self.interval - delta)
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, self.last)
        self.last = now
        return elapsed