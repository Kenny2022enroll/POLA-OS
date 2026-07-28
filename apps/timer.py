from core.app import App
from ui.window import Window
from ui.label import Label
import time

class Timer(App):
    name="Timer"
    def open(self):
        self.window=Window()
        self.title=Label(
            "Timer",
            45,
            5
        )
        self.number=Label(
            "0",
            60,
            30
        )
        self.window.add(
            self.title
        )
        self.window.add(
            self.number
        )
        self.start=time.time()

    def update(self):
        value=str(
            int(
                time.time()
                -
                self.start
            )
        )
        self.number.text=value

    def draw(self,display):
        self.window.draw(
            display
        )