import time
from mpython import touchPad_P, touchPad_Y, touchPad_T, touchPad_H
from mpython import touchPad_O, touchPad_N
from core.event import Event, SELECT, BACK, NAV_NEXT, NAV_PREVIOUS

TOUCH_PRESS_THRESHOLD = 260
TOUCH_RELEASE_THRESHOLD = 330
CHORD_WINDOW_MS = 260

PAD_P = 0
PAD_Y = 1
PAD_T = 2
PAD_H = 3
PAD_O = 4
PAD_N = 5

class Input:
    """Convert touch pads into one-shot semantic events."""
    def __init__(self, event_manager):
        self.events = event_manager
        self.pads = (touchPad_P, touchPad_Y, touchPad_T,
                     touchPad_H, touchPad_O, touchPad_N)
        self.states = 0
        self.started = [0, 0, 0, 0, 0, 0]
        self.back_active = False
        self.back_rejected = False
        self.select_active = False
        self.select_rejected = False
        self.previous_edge = False
        self.next_edge = False
        self.wake_lock = False

    def _pressed(self, index, now):
        mask = 1 << index
        value = self.pads[index].read()
        was_pressed = bool(self.states & mask)
        threshold = (TOUCH_RELEASE_THRESHOLD if was_pressed
                     else TOUCH_PRESS_THRESHOLD)
        pressed = value < threshold
        if pressed:
            if not was_pressed:
                self.started[index] = now
            self.states |= mask
        else:
            self.states &= ~mask
            self.started[index] = 0
        return pressed

    def _chord(self, first, second, event_type, now, active, rejected):
        mask = (1 << first) | (1 << second)
        both = (self.states & mask) == mask
        either = bool(self.states & mask)

        if not either:
            return False, False
        if active or rejected:
            return active, rejected

        first_at = self.started[first]
        second_at = self.started[second]
        if both and first_at is not None and second_at is not None:
            if abs(time.ticks_diff(first_at, second_at)) <= CHORD_WINDOW_MS:
                if not self.wake_lock:
                    self.events.emit(Event(event_type))
                return True, False
            return False, True
        return False, False

    def reset(self):
        """Forget held contacts so wake-up cannot replay the old gesture."""
        self.states = 0
        self.started[PAD_P] = 0
        self.started[PAD_Y] = 0
        self.started[PAD_T] = 0
        self.started[PAD_H] = 0
        self.started[PAD_O] = 0
        self.started[PAD_N] = 0
        self.back_active = False
        self.back_rejected = False
        self.select_active = False
        self.select_rejected = False
        self.previous_edge = False
        self.next_edge = False
        self.wake_lock = True

    def release_wake_lock(self):
        if self.states == 0:
            self.wake_lock = False

    def _edge(self, pressed, previous, event_type, allowed):
        if allowed and pressed and not previous and not self.wake_lock:
            self.events.emit(Event(event_type))
        return pressed

    def update(self):
        now = time.ticks_ms()
        p = self._pressed(PAD_P, now)
        y = self._pressed(PAD_Y, now)
        t = self._pressed(PAD_T, now)
        h = self._pressed(PAD_H, now)
        o = self._pressed(PAD_O, now)
        n = self._pressed(PAD_N, now)

        self.back_active, self.back_rejected = self._chord(
            PAD_P, PAD_Y, BACK, now, self.back_active, self.back_rejected)
        self.select_active, self.select_rejected = self._chord(
            PAD_T, PAD_H, SELECT, now,
            self.select_active, self.select_rejected)

        chord_active = self.back_active or self.select_active or (p and y) or (t and h)
        self.previous_edge = self._edge(
            o, self.previous_edge, NAV_PREVIOUS, not chord_active)
        self.next_edge = self._edge(
            n, self.next_edge, NAV_NEXT, not chord_active)
        if self.wake_lock and self.states == 0:
            self.wake_lock = False
        return self.states != 0