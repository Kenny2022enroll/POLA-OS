from core.app import App
from core.event import BACK
from ui.window import Window
from ui.label import Label
from ui.theme import Theme

class Sample(App):
    name = "Sample"
    def open(self):
        self.window = Window()
        self.window.add(Label("Sample plugin", 15, Theme.TITLE_Y))
        self.window.add(Label("P+Y: Back", 15, Theme.CONTENT_Y))

    def update(self, delta_ms=0):
        self.window.update(delta_ms)

    def draw(self, display):
        self.window.draw(display)

    def on_event(self, event):
        if event.type == BACK:
            return BACK

APP_CLASS = Sample