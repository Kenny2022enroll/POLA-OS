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

    def reset_wake(self):
        self.wake_ms = 0

    def dim(self):
        self.state = self.DIMMED

    def sleep(self):
        self.state = self.SLEEP
        self.wake_ms = 0

    def wake(self):
        self.state = self.ACTIVE
        self.wake_ms = 0

    def is_sleeping(self):
        return self.state == self.SLEEP