from core.navigation import Navigation
from core.kernel import Kernel
from ui.launcher import Launcher

class Boot:
    def __init__(self):
        self.display=Display()
        self.scheduler=Scheduler(
            fps=10
        )
        self.events=EventManager()
        self.input=Input(
            self.events
        )
        self.app_manager=AppManager()
        self.app_manager.load(
            load_apps()
        )
        self.navigation=Navigation()
        launcher=Launcher(
            self.app_manager,
            self.navigation
        )
        self.navigation.push(
            launcher
        )
        self.kernel=Kernel(
            self.display,
            self.scheduler,
            self.input,
            self.events,
            self.navigation
        )

    def start(self):
        self.kernel.run()