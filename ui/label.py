from ui.widget import Widget

class Label(Widget):
    def __init__(
        self,
        text,
        x,
        y
    ):
        super().__init__(
            x,
            y
        )
        self.text=text

    def draw(self,display):
        display.text(
            self.text,
            self.x,
            self.y
        )