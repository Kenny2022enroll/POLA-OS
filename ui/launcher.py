from core.event import BUTTON_A

class Launcher:
    def __init__(
        self,
        display,
        scheduler,
        manager,
        events,
        input
    ):
        self.display=display
        self.scheduler=scheduler
        self.manager=manager
        self.events=events
        self.input=input
        self.index=0

    def run(self):
        while True:
            self.scheduler.wait()
            self.input.update()
            self.handle_event()
            self.display.clear()
            self.draw()
            self.display.update()

    def handle_event(self):
        event=self.events.poll()
        if event:
            if event.type==BUTTON_A:
                self.open_app()

    def open_app(self):
        apps=self.manager.get_apps()
        app=apps[self.index]
        app.open()
        while True:
            self.scheduler.wait()
            self.input.update()
            event=self.events.poll()
            if event:
                if event.type=="button_b":
                    app.close()
                    break
            self.display.clear()
            app.update()
            app.draw(
                self.display
            )
            self.display.update()

    def draw(self):
        self.display.text(
            "POLA OS",
            25,
            0
        )
        apps=self.manager.get_apps()
        y=20
        for i,app in enumerate(apps):
            text=app.name
            if i==self.index:
                text=">"+text
            self.display.text(
                text,
                20,
                y
            )
            y+=12