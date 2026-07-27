from drivers.display import Display
from core.scheduler import Scheduler
from core.app_manager import AppManager
from apps.registry import load_apps
from ui.launcher import Launcher

class Boot:
    def __init__(self):
        self.display = Display()
        self.scheduler = Scheduler(
            fps=10
        )
        self.app_manager = AppManager()
        self.app_manager.load(
            load_apps()
        )
        self.launcher = Launcher(
            self.display,
            self.scheduler,
            self.app_manager
        )

    def start(self):
        self.launcher.run()