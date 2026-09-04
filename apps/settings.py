from core.app import App
from core.event import SELECT, BACK, NAV_NEXT, NAV_PREVIOUS
from ui.theme import Theme
from ui.window import Window
from ui.label import Label
from ui.selector import Selector

# Brightness follows the light sensor automatically and the desktop is
# always the Cover Flow carousel, so neither has a setting here anymore.
SLEEP_OPTIONS = ["off", "30s", "60s"]
SOUND_OPTIONS = ["on", "off"]

class Settings(App):
    name = "Settings"
    def __init__(self):
        super().__init__()
        self.index = 0
        self.selectors = []

    def open(self):
        config = self.context.config if self.context else None
        timeout = config.get("sleep_timeout", 60) if config else 60
        sound = config.get("sound_enabled", True) if config else True
        self.selectors = [
            Selector("Sleep", SLEEP_OPTIONS,
                     {0: 0, 30: 1, 60: 2}.get(timeout, 2), 5, 26),
            Selector("Sound", SOUND_OPTIONS, 0 if sound else 1, 5, 40),
        ]
        self.window = Window()
        self.window.add(Label("Settings", 30, Theme.TITLE_Y))
        for selector in self.selectors:
            self.window.add(selector)
        self._sync_selection()

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
        sleep, sound = [item.value for item in self.selectors]
        timeout = {"off": 0, "30s": 30, "60s": 60}[sleep]
        self.context.config.update({
            "sleep_timeout": timeout,
            "sound_enabled": sound == "on",
        })

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


APP_CLASS = Settings
