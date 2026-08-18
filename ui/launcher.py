from core.app import App
from ui.theme import Theme
from core.event import SELECT, NAV_NEXT, NAV_PREVIOUS
from ui.window import Window
from ui.label import Label
from ui.button import Button

class Launcher(App):
    name = "Launcher"
    def __init__(self, manager, navigation):
        self.manager = manager
        self.navigation = navigation
        self.index = 0
        self.window = Window()
        self.title = Label("POLA OS", 25, Theme.TITLE_Y)
        self.window.add(self.title)
        self.items = []

    def open(self):
        self._rebuild_items()

    def _rebuild_items(self):
        self.items = []
        for app in self.manager.get_apps():
            self.items.append(Button(app.name, 15, Theme.CONTENT_Y))
        self._sync_selection()

    def _sync_selection(self):
        for i, item in enumerate(self.items):
            item.selected = i == self.index
            item.y = Theme.CONTENT_Y + i * 12

    def on_event(self, event):
        apps = self.manager.get_apps()
        if not apps:
            return

        if event.type == NAV_NEXT:
            self.index = (self.index + 1) % len(apps)
            self._sync_selection()
        elif event.type == NAV_PREVIOUS:
            self.index = (self.index - 1) % len(apps)
            self._sync_selection()
        elif event.type == SELECT:
            self.navigation.push(apps[self.index])

    def update(self):
        self.window.update()

    def draw(self, display):
        if not self.items:
            self.title.draw(display)
            display.text("No apps", 15, Theme.CONTENT_Y)
            return
        self.window.draw(display)
