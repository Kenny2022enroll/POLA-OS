class Launcher:
    def __init__(
        self,
        display,
        scheduler,
        app_manager
    ):
        self.display=display
        self.scheduler=scheduler
        self.manager=app_manager

    def run(self):
        while True:
            self.scheduler.wait()
            self.display.clear()
            self.draw()
            self.display.update()

    def draw(self):
        self.display.text(
            "POLA OS",
            25,
            0
        )
        apps=self.manager.get_apps()
        y=20
        for app in apps:
            self.display.text(
                app.name,
                40,
                y
            )
            y+=12