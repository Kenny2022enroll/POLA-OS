from core.page import Page
from core.event import BACK, SELECT

class ErrorPage(Page):
    """Dialog shown when an application raises an unhandled exception.
    Content starts below the kernel status strip (y >= 12)."""
    name = "Error"

    def __init__(self, app_name, exc):
        super().__init__()
        self.app_name = self._clip(app_name or "App")
        self.exc_type, self.exc_msg = self._describe(exc)

    @staticmethod
    def _describe(exc):
        try:
            etype = type(exc).__name__
        except Exception:
            etype = "Error"
        try:
            msg = str(exc)
        except Exception:
            msg = ""
        return etype, msg

    @staticmethod
    def _clip(text):
        return text[:16]

    def on_event(self, event):
        if event.type == BACK or event.type == SELECT:
            return BACK
        return None

    def draw(self, display):
        display.text("! App error", 0, 12)
        display.text(self._clip(self.app_name), 0, 23)
        display.text(self._clip(self.exc_type), 0, 34)
        display.text(self.exc_msg[:16], 0, 45)
        display.text(self.exc_msg[16:32], 0, 54)