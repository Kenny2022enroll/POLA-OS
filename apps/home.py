from core.app import App
from core.event import SELECT, NAV_NEXT, NAV_PREVIOUS
from ui.theme import Theme
from ui.window import Window
from ui.label import Label
from ui.coverflow import CoverFlow

HOME_STYLES = ("default", "minimal", "icon")


class Home(App):
    """System desktop.

    Styles (Settings -> Home):
      default  classic title card; T+H opens the application menu
      minimal  compact title card
      icon     iPod Cover Flow carousel; O/N browse, T+H launches
    """

    name = "Home"

    def __init__(self, app_manager, navigation, context):
        super().__init__()
        self.app_manager = app_manager
        self.navigation = navigation
        self.context = context
        self.style = "default"
        self.window = Window()
        self.coverflow = None
        self._last_index = 0

    def open(self):
        style = self.context.config.get("home_style", "default")
        self.style = style if style in HOME_STYLES else "default"
        self.window.clear()
        self.coverflow = None
        if self.style == "icon":
            names = [info.name for info in self.app_manager.get_apps()]
            flow = CoverFlow(names)
            index = self._last_index
            if index >= flow.count():
                index = max(0, flow.count() - 1)
            flow.target = index * 1024
            flow.pos = flow.target
            self.coverflow = flow
            return
        if self.style == "minimal":
            self.window.add(Label("POLA-OS", 42, Theme.TITLE_Y))
            self.window.add(Label("T+H: Apps", 35, Theme.CONTENT_Y + 12))
        else:
            self.window.add(Label("POLA OS", 25, Theme.TITLE_Y))
            self.window.add(Label("Touch T+H: Apps", 8, Theme.CONTENT_Y + 12))

    def on_event(self, event):
        if self.style == "icon":
            self._on_event_coverflow(event)
            return
        if event.type == SELECT:
            from apps.app_menu import AppMenu
            self.navigation.push(AppMenu(self.app_manager, self.navigation, self.context))

    def _on_event_coverflow(self, event):
        flow = self.coverflow
        if flow is None or flow.count() == 0:
            return
        if event.type == NAV_NEXT:
            flow.next()
        elif event.type == NAV_PREVIOUS:
            flow.previous()
        elif event.type == SELECT:
            self._last_index = flow.selected()
            self.navigation.push(
                self.app_manager.create(flow.selected(), self.context))

    def on_resume(self):
        style = self.context.config.get("home_style", "default")
        style = style if style in HOME_STYLES else "default"
        if style != self.style or (style == "icon" and self.coverflow is None):
            self._last_index = self.coverflow.selected() if self.coverflow else self._last_index
            self.open()
        self.invalidate()

    def update(self, delta_ms=0):
        if self.coverflow is not None:
            if self.coverflow.update(delta_ms):
                return (0, Theme.STRIP_HEIGHT, Theme.SCREEN_WIDTH,
                        Theme.SCREEN_HEIGHT - Theme.STRIP_HEIGHT)
            return False
        return self.window.update(delta_ms)

    def draw(self, display):
        if self.coverflow is not None:
            self.coverflow.draw(display)
            return
        self.window.draw(display)