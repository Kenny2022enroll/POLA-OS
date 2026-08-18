import time
from mpython import touchPad_P, touchPad_Y, touchPad_T, touchPad_H
from core.event import Event, SELECT, BACK

TOUCH_THRESHOLD = 200

class Input:
    """Translate touchpad gestures into semantic application events."""
    def __init__(self, event_manager):
        self.events = event_manager
        self.last_back = False
        self.last_select = False

    def _pressed(self, pad):
        return pad.read() < TOUCH_THRESHOLD

    def update(self):
        back = self._pressed(touchPad_P) and self._pressed(touchPad_Y)
        select = self._pressed(touchPad_T) and self._pressed(touchPad_H)

        # Emit only on the transition into a simultaneous touch.
        if back and not self.last_back:
            self.events.emit(Event(BACK))
        if select and not self.last_select:
            self.events.emit(Event(SELECT))

        self.last_back = back
        self.last_select = select