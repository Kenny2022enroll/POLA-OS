from ui.widget import Widget
from ui.theme import Theme

PAD_LABELS = "PYTHON"
KEYS_X = 41
KEYS_COUNT = 6
LOW_PERCENT = 10
BLINK_MS = 500

# "On external power / level unknown" glyph drawn when the board has
# no battery voltage sensing circuit.
BOLT_ROWS = (
    "...XX.",
    "..XX..",
    ".XX...",
    "XXXXXX",
    "..XX..",
    ".XX...",
    "XX....",
    "X.....",
)


class StatusBar(Widget):
    """Kernel-owned chrome strip: clock, touch highlight, battery."""

    def __init__(self, clock=None, battery=None, input=None, text="POLA-OS"):
        super().__init__(0, 0, 128, Theme.STRIP_HEIGHT)
        self.clock = clock
        self.battery = battery
        self.input = input
        self.text = text
        self.current_text = None
        self.current_states = 0
        self.current_batt = None
        self.blink_on = True
        self._blink_ms = 0

    def update(self, delta_ms=0):
        changed = False
        value = self._time_text()
        if value != self.current_text:
            self.current_text = value
            changed = True
        states = self.input.states if self.input is not None else 0
        if states != self.current_states:
            self.current_states = states
            changed = True
        batt = self._battery_state()
        if batt != self.current_batt:
            self.current_batt = batt
            changed = True
        if isinstance(self.current_batt, int) and self.current_batt <= LOW_PERCENT:
            self._blink_ms += delta_ms
            if self._blink_ms >= BLINK_MS * 2:
                self._blink_ms = 0
            on = self._blink_ms < BLINK_MS
            if on != self.blink_on:
                self.blink_on = on
                changed = True
        else:
            self._blink_ms = 0
            if not self.blink_on:
                self.blink_on = True
                changed = True
        return changed

    def _time_text(self):
        if self.clock is None:
            return self.text
        return self.clock.format_time()

    def _battery_state(self):
        if self.battery is None:
            return None
        if not self.battery.available():
            return "pwr"
        return self.battery.percent()

    def draw(self, display):
        display.text_small(self.current_text or self._time_text(), 0, 1)
        self._draw_keys(display)
        self._draw_battery(display)

    def _draw_keys(self, display):
        states = self.current_states
        x = KEYS_X
        for i in range(KEYS_COUNT):
            if states & (1 << i):
                display.fill_rect(x - 1, 0, 9, Theme.STRIP_HEIGHT, 1)
                display.text_small(PAD_LABELS[i], x, 1, 0)
            else:
                display.text_small(PAD_LABELS[i], x, 1)
            x += 8

    def _draw_battery(self, display):
        batt = self.current_batt
        if batt is None:
            return
        if batt == "pwr":
            self._draw_bolt(display, 121, 1)
            return
        if batt <= LOW_PERCENT and not self.blink_on:
            return
        text = "%d%%" % batt
        display.text_small(text, 128 - len(text) * 8, 1)

    @staticmethod
    def _draw_bolt(display, x, y):
        for row in range(len(BOLT_ROWS)):
            bits = BOLT_ROWS[row]
            for col in range(len(bits)):
                if bits[col] == "X":
                    display.pixel(x + col, y + row)