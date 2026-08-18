from core.app import App
from ui.theme import Theme
from core.event import SELECT, NAV_NEXT, NAV_PREVIOUS
from ui.window import Window
from ui.label import Label
from ui.button import Button
from ui.list_view import ListView

class Launcher(App):
    name = "Launcher"
    def __init__(self, manager, navigation):
        self.manager = manager
        self.navigation = navigation
        self.window = Window()
        self.title = Label("POLA OS", 25, Theme.TITLE_Y)
        self.list_view = ListView(15, Theme.CONTENT_Y)
        self.window.add(self.title)
        self.window.add(self.list_view)

    def open(self):
        self._rebuild_items()

    def _rebuild_items(self):
        self.list_view.set_items([
            Button(app.name, 15, Theme.CONTENT_Y)
            for app in self.manager.get_apps()
        ])

    def on_event(self, event):
        apps = self.manager.get_apps()
        if not apps:
            return

        if event.type == NAV_NEXT:
            self.list_view.next()
        elif event.type == NAV_PREVIOUS:
            self.list_view.previous()
        elif event.type == SELECT:
            self.navigation.push(apps[self.list_view.index])

    def update(self):
        self.window.update()

    def draw(self, display):
        self.title.draw(display)
        if not self.list_view.items:
            display.text("No apps", 15, Theme.CONTENT_Y)
        else:
            self.list_view.draw(display)