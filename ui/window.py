from ui.widget import Widget

class Window(Widget):
    """容器组件，持有子 Widget 并统一更新和绘制。"""
    def __init__(self, x=0, y=0, width=128, height=64):
        super().__init__(x, y, width, height)
        self.children = []

    def add(self, widget):
        self.children.append(widget)

    def remove(self, widget):
        if widget in self.children:
            self.children.remove(widget)

    def clear(self):
        self.children = []

    def update(self):
        for child in self.children:
            if hasattr(child, "update"):
                child.update()

    def draw(self, display):
        for child in self.children:
            child.draw(display)