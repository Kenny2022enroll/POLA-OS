from core.app_manager import AppManager

from apps.timer import Timer
from apps.settings import Settings

class Boot:
    def __init__(self):
        self.display=Display()
        self.scheduler=Scheduler(
            fps=10
        )
        self.app_manager=AppManager()
        self.app_manager.register(
            Timer()
        )
        self.app_manager.register(
            Settings()
        )
        self.launcher=Launcher(
            self.display,
            self.scheduler,
            self.app_manager
        )