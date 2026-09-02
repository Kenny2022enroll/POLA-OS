from core.app import App
from core.event import SELECT, BACK, NAV_NEXT, NAV_PREVIOUS
from ui.theme import Theme
from ui.window import Window
from ui.label import Label
from ui.selector import Selector

BRIGHTNESS_OPTIONS = ["25", "50", "80", "100"]
# "icon" selects the iPod Cover Flow desktop.
HOME_OPTIONS = ["default", "minimal", "icon"]

class Settings(App):
    name = "Settings"
    def __init__(self):
        super().__init__()
        self.index = 0
        self.selectors = []

    def open(self):
        config = self.context.config if self.context else None
        home_style = config.get("home_style", "default") if config else "default"
        sound = config.get("sound_enabled", True) if config else True
        timeout = config.get("sleep_timeout", 60) if config else 60
        brightness = config.get("brightness", 80) if config else 80
        if home_style not in HOME_OPTIONS:
            home_style = "default"
        self.selectors = [
            Selector("Home", HOME_OPTIONS,
                     HOME_OPTIONS.index(home_style), 5, 22),
            Selector("Bright", BRIGHTNESS_OPTIONS,
                     self._brightness_index(brightness), 5, 32),
            Selector("Sleep", ["off", "30s", "60s"],
                     {0: 0, 30: 1, 60: 2}.get(timeout, 2), 5, 42),
            Selector("Sound", ["on", "off"], 0 if sound else 1, 5, 52),
        ]
        self.window = Window()
        self.window.add(Label("Settings", 30, Theme.TITLE_Y))
        for selector in self.selectors:
            self.window.add(selector)
        self._sync_selection()

    @staticmethod
    def _brightness_index(value):
        best = 0
        best_gap = None
        for i, option in enumerate(BRIGHTNESS_OPTIONS):
            gap = abs(int(option) - value)
            if best_gap is None or gap < best_gap:
                best_gap = gap
                best = i
        return best

    def _sync_selection(self):
        for i, selector in enumerate(self.selectors):
            selector.selected = i == self.index

    def _change_value(self, direction):
        if not self.selectors:
            return
        selector = self.selectors[self.index]
        if direction > 0:
            selector.next()
        else:
            selector.previous()

    def _save(self):
        if not self.context or not self.selectors:
            return
        home, bright, sleep, sound = [item.value for item in self.selectors]
        timeout = {"off": 0, "30s": 30, "60s": 60}[sleep]
        brightness = int(bright)
        self.context.config.update({
            "home_style": home,
            "brightness": brightness,
            "sleep_timeout": timeout,
            "sound_enabled": sound == "on",
        })
        self.context.power.set_brightness(brightness)
        if self.context.display:
            self.context.display.set_brightness(brightness)

    def on_event(self, event):
        if event.type == BACK:
            return BACK
        if not self.selectors:
            return
        if event.type == NAV_NEXT:
            self.index = (self.index + 1) % len(self.selectors)
            self._sync_selection()
        elif event.type == NAV_PREVIOUS:
            self.index = (self.index - 1) % len(self.selectors)
            self._sync_selection()
        elif event.type == SELECT:
            self._change_value(1)
            self._save()
        return (0, Theme.CONTENT_Y, 128,
                Theme.FOOTER_Y - Theme.CONTENT_Y + 8)

    def update(self, delta_ms=0):
        return self.window.update(delta_ms)

    def draw(self, display):
        display.text("*", 0, self.selectors[self.index].y)
        self.window.draw(display)