from apps.timer import Timer
class Launcher:
    def __init__(
        self,
        display
    ):
        self.display=display
        self.apps=[
            Timer()
        ]

    def run(self):
        while True:
            self.show_home()
            # 测试直接打开第一个App
            self.apps[0].draw(
                self.display
            )

    def show_home(self):
        self.display.clear()
        self.display.text(
            "POLA OS",
            25,
            0
        )
        self.display.text(
            "Timer",
            40,
            30
        )
        self.display.update()