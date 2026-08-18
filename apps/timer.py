from core.app import App
from ui.window import Window
from ui.label import Label
from ui.theme import Theme
from core.event import NAV_NEXT, BACK
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

    def update(self):
        value = str(int(time.time() - self.start))
        self.number.text = value
        self.window.update()

    def on_event(self, event):
        if event.type == NAV_NEXT:
            return BACK

    def draw(self, display):
        self.window.draw(display)