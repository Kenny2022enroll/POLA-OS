from core.app import App
from ui.theme import Theme
from core.event import BUTTON_B

class Settings(App):
    name = "Settings"
    def draw(self, display):
        display.text("Settings", 30, Theme.TITLE_Y)
        display.text("v0.1 (Takla)", 30, Theme.CONTENT_Y)

    def on_event(self, event):
        if event.type == BUTTON_B:
            return "BACK"