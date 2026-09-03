from services.clock import ClockService
from services.config import ConfigService
from services.power import PowerService
from services.memory import MemoryService
from services.battery import BatteryService
from services.ambient import AmbientLightService

class SystemContext:
    def __init__(self):
        self.clock = ClockService()
        self.config = ConfigService()
        self.power = PowerService()
        self.memory = MemoryService()
        self.battery = BatteryService()
        self.ambient = AmbientLightService()
        self.display = None