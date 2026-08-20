from core.page import Page
from core.event import BACK, SELECT

class ErrorPage(Page):
    """Dialog shown when an application raises an unhandled exception.

    It replaces the crashed page in the navigation stack, so pressing BACK
    returns to whatever healthy page was underneath.
    """
    name = "Error"
    def __init__(self, app_name, exc):
        super().__init__()
        self.app_name = self._clip(app_name or "App")
        self.exc_type, self.exc_msg = self._describe(exc)

    @staticmethod
    def _describe(exc):
        # Best-effort extraction that must never raise itself.
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
        # 128px wide at ~8px per glyph fits 16 characters per row.
        return text[:16]

    def on_event(self, event):
        # Confirm or back both dismiss the dialog.
        if event.type == BACK or event.type == SELECT:
            return BACK
        return None

    def draw(self, display):
        display.text("! App error", 0, 2)
        display.text(self._clip(self.app_name), 0, 14)
        display.text(self._clip(self.exc_type), 0, 26)
        display.text(self.exc_msg[:16], 0, 38)
        display.text(self.exc_msg[16:32], 0, 50)