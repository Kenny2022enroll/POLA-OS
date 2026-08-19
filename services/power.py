class PowerService:
    ACTIVE = "active"
    DIMMED = "dimmed"
    SLEEP = "sleep"
    def __init__(self):
        self.state = self.ACTIVE
        self.idle_ms = 0

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

    def dim(self):
        self.state = self.DIMMED

    def sleep(self):
        self.state = self.SLEEP

    def wake(self):
        self.state = self.ACTIVE

    def is_sleeping(self):
        return self.state == self.SLEEP