import time
from mpython import touchPad_P, touchPad_Y, touchPad_T, touchPad_H
from mpython import touchPad_O, touchPad_N
from core.event import Event, SELECT, BACK, NAV_NEXT, NAV_PREVIOUS

# Hysteresis avoids chatter around the capacitive touch threshold.
TOUCH_PRESS_THRESHOLD = 180
TOUCH_RELEASE_THRESHOLD = 240
CHORD_WINDOW_MS = 150

class Input:
    """Convert touch-pad states into one-shot semantic events."""
    def __init__(self, event_manager):
        self.events = event_manager
        self.pad_states = {
            "p": False, "y": False, "t": False,
            "h": False, "o": False, "n": False,
        }
        self.pad_started = {
            "p": None, "y": None, "t": None,
            "h": None, "o": None, "n": None,
        }
        self.chords = {
            "back": {"active": False, "rejected": False},
            "select": {"active": False, "rejected": False},
        }
        self.edge_states = {"previous": False, "next": False}

    def _read(self, name, pad, now):
        value = pad.read()
        was_pressed = self.pad_states[name]
        threshold = (TOUCH_RELEASE_THRESHOLD if was_pressed
                     else TOUCH_PRESS_THRESHOLD)
        pressed = value < threshold
        if pressed and not was_pressed:
            self.pad_started[name] = now
        elif not pressed:
            self.pad_started[name] = None
        self.pad_states[name] = pressed
        return pressed

    def _chord(self, name, first_name, second_name, event_type, both):
        state = self.chords[name]
        first_at = self.pad_started[first_name]
        second_at = self.pad_started[second_name]

        if not both:
            state["active"] = False
            if not (self.pad_states[first_name] or
                    self.pad_states[second_name]):
                state["rejected"] = False
            return False

        if state["active"] or state["rejected"]:
            return state["active"]

        if first_at is None or second_at is None:
            return False
        spread = abs(time.ticks_diff(first_at, second_at))
        if spread > CHORD_WINDOW_MS:
            # Do not accept a late second contact until the chord is released.
            state["rejected"] = True
            return False

        self.events.emit(Event(event_type))
        state["active"] = True
        return True

    def _edge(self, name, pressed, event_type, allowed=True):
        previous = self.edge_states[name]
        self.edge_states[name] = pressed
        if allowed and pressed and not previous:
            self.events.emit(Event(event_type))

    def update(self):
        now = time.ticks_ms()
        p = self._read("p", touchPad_P, now)
        y = self._read("y", touchPad_Y, now)
        t = self._read("t", touchPad_T, now)
        h = self._read("h", touchPad_H, now)
        o = self._read("o", touchPad_O, now)
        n = self._read("n", touchPad_N, now)

        back = self._chord("back", "p", "y", BACK, p and y)
        select = self._chord("select", "t", "h", SELECT, t and h)
        chord_active = back or select or (p and y) or (t and h)

        # Direction contacts are ignored while a two-pad command is active.
        self._edge("previous", o, NAV_PREVIOUS, not chord_active)
        self._edge("next", n, NAV_NEXT, not chord_active)