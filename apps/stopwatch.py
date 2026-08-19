from core.app import App
from core.event import SELECT, BACK
from ui.theme import Theme
from ui.window import Window
from ui.label import Label
import time

class Stopwatch(App):
    name = "Stopwatch"
    def open(self):
        self.window = Window()
        self.title = Label("Stopwatch", 25, Theme.TITLE_Y)
        self.value_label = Label("0", 55, Theme.CONTENT_Y + 10)
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
            return (45, Theme.CONTENT_Y, 84, 20)
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
        if event.type == BACK:
            return BACK

    def draw(self, display):
        self.window.draw(display)

    def draw_dirty(self, display, regions):
        self.value_label.draw(display)
        self.status.draw(display)