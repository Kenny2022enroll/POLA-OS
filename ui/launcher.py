from apps.timer import Timer

class Launcher:
    def __init__(
        self,
        display,
        scheduler
    ):
        self.display = display
        self.scheduler = scheduler
        self.app = Timer()

    def run(self):
        while True:
            # 控制帧率
            self.scheduler.wait()
            # 清屏
            self.display.clear()
            # 更新
            self.app.update()
            # 绘制
            self.draw()
            # 一次刷新
            self.display.update()

    def draw(self):
        self.display.text(
            "POLA OS",
            25,
            0
        )
        self.app.draw(
            self.display
        )