from mpython import *
from core.event import Event
from core.event import BUTTON_A, BUTTON_B

class Input:
    def __init__(
        self,
        event_manager
    ):
        self.events = event_manager

    def update(self):
        if button_a.value()==0:
            self.events.emit(
                Event(BUTTON_A)
            )
        if button_b.value()==0:
            self.events.emit(
                Event(BUTTON_B)
            )