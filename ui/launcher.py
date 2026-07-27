from core.event import (
    BUTTON_A,
    BUTTON_B
)

class Launcher:
    def __init__(
        self,
        display,
        scheduler,
        manager,
        events,
        input
    ):
        self.display = display
        self.scheduler = scheduler
        self.manager = manager
        self.events = events
        self.input = input
        self.index = 0

    def run(self):
        while True:
            self.scheduler.wait()
            # 输入检测
            self.input.update()
            # 处理事件
            self.handle_event()
            # 绘制
            self.display.clear()
            self.draw()
            self.display.update()

    def handle_event(self):
        event = self.events.poll()
        if event:
            if event.type == BUTTON_A:
                self.open_app()

    def open_app(self):
        apps = self.manager.get_apps()
        app = apps[self.index]
        app.open()
        while True:
            self.display.clear()
            app.update()
            app.draw(
                self.display
            )
            self.display.update()
            self.scheduler.wait()

    def draw(self):
        self.display.text(
            "POLA OS",
            25,
            0
        )
        apps = self.manager.get_apps()
        y = 20
        for i,app in enumerate(apps):
            prefix="> " if i==self.index else "  "
            self.display.text(
                prefix+app.name,
                20,
                y
            )
            y+=12