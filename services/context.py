from services.clock import ClockService
from services.config import ConfigService
from services.power import PowerService

class SystemContext:
    def __init__(self):
        self.clock = ClockService()
        self.config = ConfigService()
        self.power = PowerService()