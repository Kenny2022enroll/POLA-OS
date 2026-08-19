from ui.widget import Widget

class Window(Widget):
    """Container that forwards update, event and draw to child widgets."""
    def __init__(self, x=0, y=0, width=128, height=64):
        super().__init__(x, y, width, height)
        self.children = []

    def add(self, widget):
        self.children.append(widget)
        return widget

    def remove(self, widget):
        if widget in self.children:
            self.children.remove(widget)

    def clear(self):
        self.children = []

    def update(self, delta_ms=0):
        changed = False
        for child in self.children:
            if child.visible and child.update(delta_ms):
                changed = True
        return changed

    def on_event(self, event):
        for child in reversed(self.children):
            result = child.on_event(event)
            if result is not None:
                return result
        return None

    def draw(self, display):
        for child in self.children:
            if child.visible:
                child.draw(display)