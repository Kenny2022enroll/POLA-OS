from core.app import App
import time

class Timer(App):
    name = "Timer"
    def __init__(self):
        self.start = 0
        self.value = 0

    def open(self):
        self.start = time.time()

    def update(self):
        if self.start != 0:
            self.value = int(
                time.time() - self.start
            )

    def draw(self, display):
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

    def close(self):
        pass