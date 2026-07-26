from core.app import App
import time

class Timer(App):
    name="Timer"
    def __init__(self):
        self.start=time.time()

    def draw(self,display):
        t=int(
            time.time()
            -
            self.start
        )
        display.text(
            "Timer",
            40,
            10
        )
        display.text(
            str(t),
            55,
            30
        )
        display.update()