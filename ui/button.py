from ui.widget import Widget

class Button(Widget):
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
        self.selected=False

    def draw(self,display):
        if self.selected:
            display.text(
                ">"+self.text,
                self.x,
                self.y
            )
        else:
            display.text(
                self.text,
                self.x,
                self.y
            )