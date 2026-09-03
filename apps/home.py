from core.app import App
from core.event import SELECT, NAV_NEXT, NAV_PREVIOUS
from ui.theme import Theme
from ui.coverflow import CoverFlow


class Home(App):
    """System desktop: a Cover Flow carousel of registered apps.

    O/N browse, T+H launches the selected app. App icons come from the
    icon builders registered in each app's manifest.
    """

    name = "Home"

    def __init__(self, app_manager, navigation, context):
        super().__init__()
        self.app_manager = app_manager
        self.navigation = navigation
        self.context = context
        self.coverflow = None
        self._last_index = 0

    def open(self):
        flow = CoverFlow(self.app_manager.get_apps())
        index = self._last_index
        if index >= flow.count():
            index = max(0, flow.count() - 1)
        flow.target = index * 1024
        flow.pos = flow.target
        self.coverflow = flow

    def on_event(self, event):
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
        if self.coverflow is None:
            self.open()
        self.invalidate()

    def update(self, delta_ms=0):
        if self.coverflow is not None:
            if self.coverflow.update(delta_ms):
                return (0, Theme.STRIP_HEIGHT, Theme.SCREEN_WIDTH,
                        Theme.SCREEN_HEIGHT - Theme.STRIP_HEIGHT)
        return False

    def draw(self, display):
        if self.coverflow is not None:
            self.coverflow.draw(display)
