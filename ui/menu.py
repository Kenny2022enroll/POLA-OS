from ui.widget import Widget
from ui.button import Button
from ui.list_view import ListView

class Menu(Widget):
    def __init__(self, x=0, y=0, visible_rows=3):
        super().__init__(x, y)
        self.list_view = ListView(x, y, visible_rows=visible_rows)

    def set_items(self, items):
        buttons = []
        for item in items:
            buttons.append(item if isinstance(item, Button)
                           else Button(str(item), self.x, self.y))
        self.list_view.set_items(buttons)

    @property
    def index(self):
        return self.list_view.index

    def next(self):
        self.list_view.next()

    def previous(self):
        self.list_view.previous()

    def selected(self):
        return self.list_view.selected()

    def draw(self, display):
        self.list_view.draw(display)