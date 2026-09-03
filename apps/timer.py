import time

from core.app import App
from core.event import BACK, NAV_NEXT, NAV_PREVIOUS, SELECT
from ui.label import Label
from ui.theme import Theme
from ui.window import Window

PRESETS = (("10s", 10), ("30s", 30), ("1m", 60), ("2m", 120),
           ("5m", 300), ("10m", 600))
DEFAULT_PRESET = 2

SETUP, RUNNING, PAUSED, DONE = 0, 1, 2, 3


def _fmt(seconds):
    return "%d:%02d" % (seconds // 60, seconds % 60)


class Timer(App):
    """Countdown timer.

    SETUP   O/N pick a preset, T+H starts
    RUNNING T+H pauses
    PAUSED  T+H resumes, N resets to preset picker
    DONE    "Done!" blinks, T+H or N returns to preset picker
    """

    name = "Timer"
    BLINK_MS = 500

    def open(self):
        self.window = Window()
        self.title = Label("Timer", 45, Theme.TITLE_Y)
        self.number = Label("1:00", 45, Theme.CONTENT_Y + 8)
        self.hint = Label("", 4, Theme.FOOTER_Y)
        self.window.add(self.title)
        self.window.add(self.number)
        self.window.add(self.hint)
        self.state = SETUP
        self.preset_index = DEFAULT_PRESET
        self.end_at = 0
        self.remaining_ms = 0
        self.last_value = None
        self._blink_ms = 0
        self._blink_on = True
        self._sync()

    def _sync(self):
        if self.state == SETUP:
            self.number.text = _fmt(PRESETS[self.preset_index][1])
            self.hint.text = "O/N pick T+H run"
        elif self.state == RUNNING:
            self.hint.text = "T+H pause"
        elif self.state == PAUSED:
            self.hint.text = "T+H run N reset"
        else:
            self.number.text = "Done!"
            self.hint.text = "T+H/N reset"
        self.number.visible = True
        self._blink_ms = 0
        self._blink_on = True

    def update(self, delta_ms=0):
        if self.state == RUNNING:
            ms = time.ticks_diff(self.end_at, time.ticks_ms())
            if ms <= 0:
                self.state = DONE
                self._sync()
                return True
            seconds = (ms + 999) // 1000
            value = _fmt(seconds)
            if value != self.last_value:
                self.number.text = value
                self.last_value = value
                self.window.update(delta_ms)
                return (40, Theme.CONTENT_Y + 8, 88, 18)
            return False
        if self.state == DONE:
            self._blink_ms += delta_ms
            if self._blink_ms >= self.BLINK_MS:
                self._blink_ms -= self.BLINK_MS
                self._blink_on = not self._blink_on
                self.number.visible = self._blink_on
                return True
            return False
        return False

    def on_event(self, event):
        if event.type == BACK:
            return BACK
        if self.state == SETUP:
            if event.type == NAV_NEXT:
                self.preset_index = (self.preset_index + 1) % len(PRESETS)
                self._sync()
                return True
            if event.type == NAV_PREVIOUS:
                self.preset_index = (self.preset_index - 1) % len(PRESETS)
                self._sync()
                return True
            if event.type == SELECT:
                self.end_at = time.ticks_add(
                    time.ticks_ms(), PRESETS[self.preset_index][1] * 1000)
                self.last_value = None
                self.state = RUNNING
                self._sync()
                return True
        elif self.state == RUNNING:
            if event.type == SELECT:
                self.remaining_ms = time.ticks_diff(
                    self.end_at, time.ticks_ms())
                self.state = PAUSED
                self._sync()
                return True
        elif self.state == PAUSED:
            if event.type == SELECT:
                self.end_at = time.ticks_add(time.ticks_ms(),
                                             self.remaining_ms)
                self.last_value = None
                self.state = RUNNING
                self._sync()
                return True
            if event.type == NAV_NEXT:
                self.state = SETUP
                self._sync()
                return True
        elif self.state == DONE:
            if event.type in (SELECT, NAV_NEXT, NAV_PREVIOUS):
                self.state = SETUP
                self._sync()
                return True
        return None

    def draw(self, display):
        self.window.draw(display)

    def draw_dirty(self, display, regions):
        self.number.draw(display)


def _icon(canvas):
    canvas.circle(12, 12, 9)
    canvas.vline(12, 3, 2)
    canvas.vline(12, 19, 2)
    canvas.hline(3, 12, 2)
    canvas.hline(19, 12, 2)
    canvas.line(12, 12, 12, 6)
    canvas.line(12, 12, 16, 12)
    canvas.pixel(12, 12)


MANIFEST = {
    "name": "Timer",
    "version": "0.2",
    "description": "Countdown timer with presets",
    "icon": _icon,
}

APP_CLASS = Timer
