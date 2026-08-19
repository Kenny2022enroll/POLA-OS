from mpython import oled

class Display:
    """OLED adapter with dirty-frame and optional dirty-region tracking."""
    WIDTH = 128
    HEIGHT = 64
    def __init__(self):
        self.dirty = True
        self.offset_x = 0
        self.offset_y = 0
        self.supports_partial = hasattr(oled, "fill_rect")

    def begin_frame(self):
        self.dirty = False

    def clear(self, rect=None):
        if rect and self.supports_partial:
            x, y, width, height = rect
            oled.fill_rect(x, y, width, height, 0)
        else:
            oled.fill(0)
        self.dirty = True

    def clear_region(self, rect):
        self.clear(rect)

    def set_offset(self, x=0, y=0):
        self.offset_x = x
        self.offset_y = y

    def reset_offset(self):
        self.offset_x = 0
        self.offset_y = 0

    def text(self, text, x, y):
        oled.DispChar(text, x + self.offset_x, y + self.offset_y)
        self.dirty = True

    def update(self):
        if not self.dirty:
            return False
        oled.show()
        self.dirty = False
        return True