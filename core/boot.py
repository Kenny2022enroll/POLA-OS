from drivers.display import Display
from ui.launcher import Launcher
from core.scheduler import Scheduler

class Boot:
    def __init__(self):
        self.display = Display()
        self.scheduler = Scheduler(
            fps=10
        )
        self.launcher = Launcher(
            self.display,
            self.scheduler
        )

    def start(self):
        self.display.clear()
        self.launcher.run()