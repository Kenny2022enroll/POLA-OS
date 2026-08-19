from ui.widget import Widget

class Button(Widget):
    def __init__(self, text, x, y):
        super().__init__(x, y)
        self.text = text
        self.selected = False

    def draw(self, display):
        prefix = ">" if self.selected else " "
        display.text(prefix + self.text, self.x, self.y)