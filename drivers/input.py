import time
from mpython import button_a, button_b
from core.event import (
    Event,
    BUTTON_A,
    BUTTON_B
)

class Input:
    def __init__(self,event_manager):
        self.events = event_manager
        self.last_a = 1
        self.last_b = 1

    def update(self):
        a = button_a.value()
        b = button_b.value()
        # A键下降沿
        if self.last_a == 1 and a == 0:
            self.events.emit(
                Event(BUTTON_A)
            )
        # B键下降沿
        if self.last_b == 1 and b == 0:
            self.events.emit(
                Event(BUTTON_B)
            )
        self.last_a = a
        self.last_b = b