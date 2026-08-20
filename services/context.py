from services.clock import ClockService
from services.config import ConfigService
from services.power import PowerService
from services.memory import MemoryService

class SystemContext:
    def __init__(self):
        self.clock = ClockService()
        self.config = ConfigService()
        self.power = PowerService()
        self.memory = MemoryService()
        # Filled in by Boot once the display driver exists, so services and
        # apps can reach it (e.g. for brightness control).
        self.display = None