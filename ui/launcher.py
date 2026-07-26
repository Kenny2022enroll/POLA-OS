from apps.timer import Timer

class Launcher:
    def __init__(self, display):
        self.display = display
        self.app = Timer()

    def run(self):
        while True:
            self.display.clear()
            self.draw_home()
            self.app.draw(
                self.display
            )
            self.display.update()

    def draw_home(self):
        self.display.text(
            "POLA OS",
            25,
            0
        )
        self.display.text(
            "Timer",
            40,
            20
        )