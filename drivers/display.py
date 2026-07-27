from mpython import oled

class Display:
    def clear(self):
        oled.fill(0)

    def text(
        self,
        text,
        x,
        y
    ):
        oled.DispChar(
            text,
            x,
            y
        )

    def update(self):
        oled.show()