from ui.widget import Widget

class Dialog(Widget):
    def __init__(self, title, message, options=None, x=0, y=12):
        super().__init__(x, y, 128, 42)
        self.title = title
        self.message = message
        self.options = options or ["OK"]
        self.index = 0

    def next(self):
        self.index = (self.index + 1) % len(self.options)

    def previous(self):
        self.index = (self.index - 1) % len(self.options)

    def selected(self):
        return self.options[self.index]

    def draw(self, display):
        display.text(self.title, self.x, self.y)
        display.text(self.message, self.x, self.y + 12)
        text = ""
        for i, option in enumerate(self.options):
            prefix = ">" if i == self.index else " "
            text += "%s%s " % (prefix, option)
        display.text(text, self.x, self.y + 28)