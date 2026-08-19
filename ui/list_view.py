from ui.widget import Widget

class ListView(Widget):
    """Selectable vertical list with a bounded visible window."""
    def __init__(self, x=0, y=0, row_height=12, visible_rows=3):
        super().__init__(x, y)
        self.row_height = row_height
        self.visible_rows = visible_rows
        self.items = []
        self.index = 0
        self.offset = 0

    def set_items(self, items):
        self.items = items
        self.index = min(self.index, max(0, len(items) - 1))
        self._sync_selection()

    def _sync_selection(self):
        if not self.items:
            self.index = 0
            self.offset = 0
            return
        if self.index < self.offset:
            self.offset = self.index
        if self.index >= self.offset + self.visible_rows:
            self.offset = self.index - self.visible_rows + 1
        for i, item in enumerate(self.items):
            item.selected = i == self.index
            item.visible = self.offset <= i < self.offset + self.visible_rows
            item.x = self.x
            item.y = self.y + (i - self.offset) * self.row_height

    def next(self):
        if self.items:
            self.index = (self.index + 1) % len(self.items)
            self._sync_selection()

    def previous(self):
        if self.items:
            self.index = (self.index - 1) % len(self.items)
            self._sync_selection()

    def selected(self):
        return self.items[self.index] if self.items else None

    def draw(self, display):
        for item in self.items:
            if item.visible:
                item.draw(display)