from core.app import App
from core.event import SELECT, BACK, NAV_NEXT, NAV_PREVIOUS
from ui.theme import Theme
from ui.window import Window
from ui.label import Label
from ui.menu import Menu

class AppMenu(App):
    name = "Apps"
    def __init__(self, manager, navigation, context):
        super().__init__()
        self.manager = manager
        self.navigation = navigation
        self.context = context
        self.window = Window()
        self.title = Label("Applications", 20, Theme.TITLE_Y)
        self.menu = Menu(10, Theme.CONTENT_Y, visible_rows=3)
        self.window.add(self.title)
        self.window.add(self.menu)

    def open(self):
        self.menu.set_items([app.name for app in self.manager.get_apps()])

    def on_event(self, event):
        apps = self.manager.get_apps()
        if event.type == BACK:
            return BACK
        if not apps:
            return
        if event.type == NAV_NEXT:
            self.menu.next()
        elif event.type == NAV_PREVIOUS:
            self.menu.previous()
        elif event.type == SELECT:
            self.navigation.push(self.manager.create(self.menu.index,
                                                     self.context))

    def update(self, delta_ms=0):
        return self.window.update(delta_ms)

    def draw(self, display):
        self.window.draw(display)