from drivers import Display
from drivers import Input
from core.kernel import Scheduler
from core.event import EventManager
from core.app_manager import AppManager
from core.navigation import Navigation
from core.kernel import Kernel
from apps.registry import load_apps
from apps.home import Home
from plugins import load_plugins
from services import SystemContext
from ui.status_bar import StatusBar

class Boot:
    def __init__(self):
        self.context = SystemContext()
        self.display = Display()
        self.context.display = self.display
        self.scheduler = Scheduler(fps=25, idle_fps=10)
        self.events = EventManager()
        self.input = Input(self.events)
        self.status_bar = StatusBar(self.context.clock,
                                    self.context.battery, self.input)
        self.app_manager = AppManager()
        self.app_manager.load(load_apps() + load_plugins())
        self.navigation = Navigation(transition_ms=120)
        self.navigation.push(Home(self.app_manager, self.navigation, self.context))
        self.kernel = Kernel(
            self.display,
            self.scheduler,
            self.input,
            self.events,
            self.navigation,
            self.context,
            self.status_bar,
        )
        self._apply_boot_brightness()

    def _apply_boot_brightness(self):
        if self.context.ambient.available():
            return
        level = 80
        self.context.power.set_brightness(level)
        self.display.set_brightness(level)

    def start(self):
        self.kernel.run()