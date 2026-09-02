import devlib

try:
    import framebuf
except ImportError:
    framebuf = None

try:
    oled = devlib.oled
except AttributeError:
    raise RuntimeError("OLED not found on I2C bus (devlib)")

class Display:
    """OLED adapter with dirty-frame, dirty-region and brightness support."""
    WIDTH = 128
    HEIGHT = 64
    DEFAULT_I2C_ADDR = 60

    def __init__(self):
        self.dirty = True
        self.offset_x = 0
        self.offset_y = 0
        self.supports_partial = hasattr(oled, "fill_rect")
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

    def text_small(self, text, x, y, color=1):
        """8px built-in framebuf font; used by the chrome strip and
        dense UI where the 16px DispChar font is too large."""
        oled.text(text, x + self.offset_x, y + self.offset_y, color)
        self.dirty = True

    def text_small_width(self, text):
        return len(text) * 8

    # --- drawing primitives (respect the transition offset) ---

    def pixel(self, x, y, color=1):
        oled.pixel(x + self.offset_x, y + self.offset_y, color)
        self.dirty = True

    def hline(self, x, y, width, color=1):
        oled.hline(x + self.offset_x, y + self.offset_y, width, color)
        self.dirty = True

    def vline(self, x, y, height, color=1):
        oled.vline(x + self.offset_x, y + self.offset_y, height, color)
        self.dirty = True

    def rect(self, x, y, width, height, color=1):
        oled.rect(x + self.offset_x, y + self.offset_y, width, height, color)
        self.dirty = True

    def fill_rect(self, x, y, width, height, color=1):
        oled.fill_rect(x + self.offset_x, y + self.offset_y, width, height, color)
        self.dirty = True

    def blit(self, buf, x, y, width, height, key=-1):
        """Blit a MONO_HLSB buffer. key=-1 keeps the background."""
        sprite = framebuf.FrameBuffer(buf, width, height, framebuf.MONO_HLSB)
        if key < 0:
            oled.blit(sprite, x + self.offset_x, y + self.offset_y)
        else:
            oled.blit(sprite, x + self.offset_x, y + self.offset_y, key)
        self.dirty = True

    def update(self):
        if not self.dirty:
            return False
        oled.show()
        self.dirty = False
        return True

    def set_brightness(self, percent):
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
            if hasattr(oled, "contrast"):
                oled.contrast(level)
                self.supports_brightness = True
                return True
            if hasattr(oled, "brightness"):
                oled.brightness(level)
                self.supports_brightness = True
                return True
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