from core.app import App

class Settings(App):
    name="Settings"
    def draw(self,display):
        display.text(
            "Settings",
            30,
            30
        )