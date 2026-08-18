from core.app import App
from ui.theme import Theme
from ui.window import Window
from ui.label import Label
from core.event import NAV_NEXT, BACK

class Settings(App):
    name = "Settings"
    def open(self):
        self.window = Window()
        self.window.add(Label("Settings", 30, Theme.TITLE_Y))
        self.window.add(Label("v0.1 (Takla)", 30, Theme.CONTENT_Y))

    def update(self):
        self.window.update()

    def draw(self, display):
        self.window.draw(display)

    def on_event(self, event):
        if event.type == NAV_NEXT:
            return BACK