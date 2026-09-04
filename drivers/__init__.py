"""Hardware drivers for the mPython board.

Display and input are consolidated in this single module so the
embedded target pays the per-module overhead only once.
"""
import time

import devlib

try:
    import framebuf
except ImportError:
    framebuf = None

from devlib import touchPad_P, touchPad_Y, touchPad_T, touchPad_H
from devlib import touchPad_O, touchPad_N

from core.event import Event, SELECT, BACK, NAV_NEXT, NAV_PREVIOUS

try:
    oled = devlib.oled
except AttributeError:
    raise RuntimeError("OLED not found on I2C bus (devlib)")


class Display:
    """OLED adapter with dirty-frame, dirty-region and brightness support."""
    WIDTH = 128
    HEIGHT = 64
    def __init__(self):
        self.dirty = True
        self.offset_x = 0
        self.offset_y = 0
        self.supports_partial = hasattr(oled, "fill_rect")
        self.brightness = 100
        self.supports_brightness = None

    def begin_frame(self):
        self.dirty = False

    def clear(self, rect=None):
        if rect and self.supports_partial:
            x, y, width, height = rect
            oled.fill_rect(x, y, width, height, 0)
        else:
            oled.fill(0)
        self.dirty = True

    def set_offset(self, x=0, y=0):
        self.offset_x = x
        self.offset_y = y

    def reset_offset(self):
        self.offset_x = 0
        self.offset_y = 0

    def text(self, text, x, y):
        oled.DispChar(text, x + self.offset_x, y + self.offset_y)
        self.dirty = True

    def text_small(self, text, x, y, color=1):
        """8px built-in framebuf font; used by the chrome strip and
        dense UI where the 16px DispChar font is too large."""
        oled.text(text, x + self.offset_x, y + self.offset_y, color)
        self.dirty = True

    # --- drawing primitives (respect the transition offset) ---

    def pixel(self, x, y, color=1):
        oled.pixel(x + self.offset_x, y + self.offset_y, color)
        self.dirty = True

    def hline(self, x, y, width, color=1):
        oled.hline(x + self.offset_x, y + self.offset_y, width, color)
        self.dirty = True

    def vline(self, x, y, height, color=1):
        oled.vline(x + self.offset_x, y + self.offset_y, height, color)
        self.dirty = True

    def rect(self, x, y, width, height, color=1):
        oled.rect(x + self.offset_x, y + self.offset_y, width, height, color)
        self.dirty = True

    def fill_rect(self, x, y, width, height, color=1):
        oled.fill_rect(x + self.offset_x, y + self.offset_y, width, height, color)
        self.dirty = True

    def blit(self, buf, x, y, width, height, key=-1):
        """Blit a MONO_HLSB buffer. key=-1 keeps the background."""
        sprite = framebuf.FrameBuffer(buf, width, height, framebuf.MONO_HLSB)
        if key < 0:
            oled.blit(sprite, x + self.offset_x, y + self.offset_y)
        else:
            oled.blit(sprite, x + self.offset_x, y + self.offset_y, key)
        self.dirty = True

    def update(self):
        if not self.dirty:
            return False
        oled.show()
        self.dirty = False
        return True

    def set_brightness(self, percent):
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        level = (percent * 255) // 100
        if self._apply_contrast(level):
            self.brightness = percent
            return True
        return False

    def _apply_contrast(self, level):
        if self.supports_brightness is False:
            return False
        try:
            oled.contrast(level)
            self.supports_brightness = True
            return True
        except Exception:
            self.supports_brightness = False
            return False


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
