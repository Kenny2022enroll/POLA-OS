from core.event import BACK

class Kernel:
    def __init__(
        self,
        display,
        scheduler,
        input,
        events,
        navigation
    ):
        self.display=display
        self.scheduler=scheduler
        self.input=input
        self.events=events
        self.navigation=navigation

    def run(self):
        while True:
            self.scheduler.wait()
            # 输入
            self.input.update()
            # 事件
            event=self.events.poll()
            if event:
                page=self.navigation.current()
                if page:
                    result = page.on_event(event)
                    if result == BACK:
                        self.navigation.pop()
            page=self.navigation.current()
            if page:
                page.update()
                self.display.clear()
                page.draw(
                    self.display
                )
                self.display.update()