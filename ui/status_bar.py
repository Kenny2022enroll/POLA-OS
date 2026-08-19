from ui.widget import Widget

class StatusBar(Widget):
    def __init__(self, clock=None, text="POLA-OS"):
        super().__init__(0, 0, 128, 10)
        self.clock = clock
        self.text = text
        self.current_text = None

    def update(self, delta_ms=0):
        value = self._time_text()
        if value == self.current_text:
            return False
        self.current_text = value
        return True

    def _time_text(self):
        if self.clock is None:
            return self.text
        return self.clock.format_time()

    def draw(self, display):
        display.text(self.current_text or self._time_text(), self.x, self.y)