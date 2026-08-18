from ui.widget import Widget

class ListView(Widget):
    """Vertical selectable list for the 128x64 display."""
    def __init__(self, x=0, y=0, row_height=12, visible_rows=3):
        super().__init__(x, y)
        self.row_height = row_height
        self.visible_rows = visible_rows
        self.items = []
        self.index = 0

    def set_items(self, items):
        self.items = items
        if self.items:
            self.index %= len(self.items)
        else:
            self.index = 0
        self._sync_selection()

    def _sync_selection(self):
        first = max(0, self.index - self.visible_rows + 1)
        for offset, item in enumerate(self.items[first:first + self.visible_rows]):
            item.selected = first + offset == self.index
            item.x = self.x
            item.y = self.y + offset * self.row_height

    def next(self):
        if self.items:
            self.index = (self.index + 1) % len(self.items)
            self._sync_selection()

    def previous(self):
        if self.items:
            self.index = (self.index - 1) % len(self.items)
            self._sync_selection()

    def selected(self):
        if not self.items:
            return None
        return self.items[self.index]

    def draw(self, display):
        first = max(0, self.index - self.visible_rows + 1)
        for item in self.items[first:first + self.visible_rows]:
            item.draw(display)