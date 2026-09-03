from core.app import App
from core.event import SELECT, BACK, NAV_NEXT
from ui.theme import Theme
from ui.window import Window
from ui.label import Label
import time

class Stopwatch(App):
    """Count-up stopwatch. T+H starts/pauses; N resets while paused."""

    name = "Stopwatch"
    def open(self):
        self.window = Window()
        self.title = Label("Stopwatch", 25, Theme.TITLE_Y)
        self.value_label = Label("0", 55, Theme.CONTENT_Y + 8)
        self.status = Label("Ready", 45, Theme.FOOTER_Y)
        self.window.add(self.title)
        self.window.add(self.value_label)
        self.window.add(self.status)
        self.elapsed = 0
        self.started_at = None
        self.last_value = "0"

    def _elapsed(self):
        if self.started_at is None:
            return self.elapsed
        return self.elapsed + time.ticks_diff(time.ticks_ms(),
                                              self.started_at) // 1000

    def update(self, delta_ms=0):
        value = str(self._elapsed())
        changed = value != self.last_value
        self.value_label.text = value
        self.last_value = value
        self.window.update(delta_ms)
        if changed:
            return (45, Theme.CONTENT_Y + 8, 84, 18)
        return False

    def on_event(self, event):
        if event.type == SELECT:
            if self.started_at is None:
                self.started_at = time.ticks_ms()
                self.status.text = "Running"
            else:
                self.elapsed = self._elapsed()
                self.started_at = None
                self.status.text = "Paused"
            return (40, Theme.CONTENT_Y, 88, 34)
        if event.type == NAV_NEXT and self.started_at is None and self.elapsed:
            self.elapsed = 0
            self.last_value = "0"
            self.value_label.text = "0"
            self.status.text = "Ready"
            return (40, Theme.CONTENT_Y, 88, 34)
        if event.type == BACK:
            return BACK

    def draw(self, display):
        self.window.draw(display)

    def draw_dirty(self, display, regions):
        self.value_label.draw(display)
        self.status.draw(display)


def _icon(canvas):
    canvas.circle(12, 13, 8)
    canvas.vline(11, 3, 2)
    canvas.vline(12, 3, 2)
    canvas.hline(9, 2, 6)
    canvas.line(18, 6, 20, 4)
    canvas.line(12, 13, 15, 9)
    canvas.pixel(12, 13)


MANIFEST = {
    "name": "Stopwatch",
    "version": "0.2",
    "description": "Stopwatch with pause and reset",
    "icon": _icon,
}

APP_CLASS = Stopwatch
