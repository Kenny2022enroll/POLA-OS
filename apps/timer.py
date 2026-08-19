from core.app import App
from ui.window import Window
from ui.label import Label
from ui.theme import Theme
from core.event import BACK
import time

class Timer(App):
    name = "Timer"
    def open(self):
        self.window = Window()
        self.title = Label("Timer", 45, Theme.TITLE_Y)
        self.number = Label("0", 60, Theme.CONTENT_Y + 10)
        self.window.add(self.title)
        self.window.add(self.number)
        self.start = time.time()
        self.last_value = "0"

    def update(self, delta_ms=0):
        value = str(int(time.time() - self.start))
        changed = value != self.last_value
        self.number.text = value
        self.last_value = value
        self.window.update(delta_ms)
        if changed:
            return (54, Theme.CONTENT_Y, 74, 20)
        return False

    def on_event(self, event):
        if event.type == BACK:
            return BACK

    def draw(self, display):
        self.window.draw(display)

    def draw_dirty(self, display, regions):
        self.number.draw(display)