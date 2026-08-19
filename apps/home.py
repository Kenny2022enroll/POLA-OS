from core.app import App
from core.event import SELECT
from ui.theme import Theme
from ui.window import Window
from ui.label import Label
from ui.status_bar import StatusBar

class Home(App):
    name = "Home"
    def __init__(self, app_manager, navigation, context):
        super().__init__()
        self.app_manager = app_manager
        self.navigation = navigation
        self.context = context
        self.window = Window()
        self.status = StatusBar(context.clock)
        self.title = Label("POLA OS", 25, Theme.TITLE_Y)
        self.subtitle = Label("Touch T+H: Apps", 8, Theme.CONTENT_Y + 12)
        self.window.add(self.status)
        self.window.add(self.title)
        self.window.add(self.subtitle)

    def open(self):
        style = self.context.config.get("home_style", "default")
        if style == "minimal":
            self.title.text = "POLA-OS"
            self.title.x = 42
            self.subtitle.text = "T+H: Apps"
            self.subtitle.x = 35
        else:
            self.title.text = "POLA OS"
            self.title.x = 25
            self.subtitle.text = "Touch T+H: Apps"
            self.subtitle.x = 8

    def on_event(self, event):
        if event.type == SELECT:
            from apps.app_menu import AppMenu
            self.navigation.push(AppMenu(self.app_manager,
                                         self.navigation,
                                         self.context))

    def on_resume(self):
        self.open()
        self.invalidate()

    def update(self, delta_ms=0):
        return self.window.update(delta_ms)

    def draw(self, display):
        self.window.draw(display)