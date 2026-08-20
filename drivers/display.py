from mpython import oled

class Display:
    """OLED adapter with dirty-frame, dirty-region and brightness support."""
    WIDTH = 128
    HEIGHT = 64
    # Common SSD1306-family I2C address, used only as a raw-write fallback.
    DEFAULT_I2C_ADDR = 60
    def __init__(self):
        self.dirty = True
        self.offset_x = 0
        self.offset_y = 0
        self.supports_partial = hasattr(oled, "fill_rect")
        # Brightness support is probed lazily on first use.
        self.brightness = 100
        self.supports_brightness = None

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

    def set_brightness(self, percent):
        """Apply a 0..100 brightness level. Returns True if the OLED
        accepted it, False when the hardware exposes no contrast control."""
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        level = (percent * 255) // 100
        if self._apply_contrast(level):
            self.brightness = percent
            return True
        return False

    def _apply_contrast(self, level):
        if self.supports_brightness is False:
            return False
        try:
            # Preferred: the driver exposes a contrast() hook.
            if hasattr(oled, "contrast"):
                oled.contrast(level)
                self.supports_brightness = True
                return True
            # Some firmware builds name it brightness() instead.
            if hasattr(oled, "brightness"):
                oled.brightness(level)
                self.supports_brightness = True
                return True
            # Fallback: raw SSD1306 contrast command (0x81) over I2C.
            bus = getattr(oled, "i2c", None)
            addr = getattr(oled, "addr", self.DEFAULT_I2C_ADDR)
            if bus is not None and hasattr(bus, "writeto"):
                bus.writeto(addr, b"\x00\x81" + bytes((level,)))
                self.supports_brightness = True
                return True
        except Exception:
            pass
        self.supports_brightness = False
        return False