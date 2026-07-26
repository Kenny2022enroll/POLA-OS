from core.app import App
import time

class Timer(App):

    name="Timer"

    def __init__(self):
        self.start=time.time()
        self.value=0

    def update(self):
        self.value=int(
            time.time()-self.start
        )

    def draw(
        self,
        display
    ):
        display.text(
            "Timer",
            40,
            25
        )
        display.text(
            str(self.value),
            55,
            40
        )