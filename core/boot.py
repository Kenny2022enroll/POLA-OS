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
from ui.status_bar import StatusBar

class Boot:
    def __init__(self):
        self.context = SystemContext()
        self.display = Display()
        self.context.display = self.display
        # 25 FPS keeps animations smooth while the dirty-region renderer
        # keeps idle frames nearly free.
        self.scheduler = Scheduler(fps=25)
        self.events = EventManager()
        self.input = Input(self.events)
        # Kernel-owned chrome: time, touch highlight and battery gauge.
        self.status_bar = StatusBar(self.context.clock,
                                    self.context.battery, self.input)
        self.app_manager = AppManager()
        self.app_manager.load(load_apps())
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
        level = self.context.config.get("brightness", 80)
        self.context.power.set_brightness(level)
        self.display.set_brightness(level)

    def start(self):
        self.kernel.run()