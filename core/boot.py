from drivers.display import Display
from drivers.input import Input
from core.scheduler import Scheduler
from core.event import EventManager
from core.app_manager import AppManager
from core.navigation import Navigation
from core.kernel import Kernel
from apps.registry import load_apps
from apps.home import Home
from services.context import SystemContext

class Boot:
    def __init__(self):
        self.context = SystemContext()
        self.display = Display()
        # Let services and apps reach the display (e.g. brightness control).
        self.context.display = self.display
        self.scheduler = Scheduler(fps=20)
        self.events = EventManager()
        self.input = Input(self.events)
        self.app_manager = AppManager()
        self.app_manager.load(load_apps())
        # Keep startup deterministic and small; optional plugins are not
        # imported or scanned on the hot boot path.
        self.navigation = Navigation(transition_ms=90)
        self.navigation.push(Home(self.app_manager, self.navigation,
                                  self.context))
        self.kernel = Kernel(
            self.display,
            self.scheduler,
            self.input,
            self.events,
            self.navigation,
            self.context,
        )
        self._apply_boot_brightness()
    def _apply_boot_brightness(self):
        level = self.context.config.get("brightness", 80)
        self.context.power.set_brightness(level)
        self.display.set_brightness(level)

    def start(self):
        self.kernel.run()