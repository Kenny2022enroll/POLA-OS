from ui.widget import Widget

class Selector(Widget):
    def __init__(self, label, values, value_index=0, x=0, y=0):
        super().__init__(x, y)
        self.label = label
        self.values = values
        self.value_index = value_index
        self.selected = False

    @property
    def value(self):
        if not self.values:
            return None
        return self.values[self.value_index]

    def next(self):
        if self.values:
            self.value_index = (self.value_index + 1) % len(self.values)

    def previous(self):
        if self.values:
            self.value_index = (self.value_index - 1) % len(self.values)

    def draw(self, display):
        prefix = ">" if self.selected else " "
        display.text("%s%s: %s" % (prefix, self.label, self.value),
                     self.x, self.y)