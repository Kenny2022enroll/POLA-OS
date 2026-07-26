from mpython import oled

class Display:
    def clear(self):
        oled.fill(0)
        oled.show()

    def text(
        self,
        content,
        x,
        y
    ):
        oled.DispChar(
            content,
            x,
            y
        )

    def update(self):
        oled.show()