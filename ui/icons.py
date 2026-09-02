# Procedurally rendered 24x24 monochrome app icons for Cover Flow.

ICON_SIZE = 24

_cache = {}
_column_cache = {}


class _Canvas:
    """24x24 1-bit canvas with integer rows (MSB = leftmost px)."""

    def __init__(self, size=ICON_SIZE):
        self.size = size
        self.rows = [0] * size

    def pixel(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.rows[y] |= 1 << (self.size - 1 - x)

    def clear_pixel(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            self.rows[y] &= ~(1 << (self.size - 1 - x))

    def hline(self, x, y, width):
        for i in range(width):
            self.pixel(x + i, y)

    def vline(self, x, y, height):
        for i in range(height):
            self.pixel(x, y + i)

    def rect(self, x, y, width, height):
        self.hline(x, y, width)
        self.hline(x, y + height - 1, width)
        self.vline(x, y, height)
        self.vline(x + width - 1, y, height)

    def line(self, x0, y0, x1, y1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.pixel(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r):
        x = r
        y = 0
        err = 1 - r
        while x >= y:
            self.pixel(cx + x, cy + y)
            self.pixel(cx + y, cy + x)
            self.pixel(cx - y, cy + x)
            self.pixel(cx - x, cy + y)
            self.pixel(cx - x, cy - y)
            self.pixel(cx - y, cy - x)
            self.pixel(cx + y, cy - x)
            self.pixel(cx + x, cy - y)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1

    def fill_circle(self, cx, cy, r):
        r2 = r * r
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r2:
                    self.pixel(cx + dx, cy + dy)

    def clear_circle(self, cx, cy, r):
        r2 = r * r
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r2:
                    self.clear_pixel(cx + dx, cy + dy)

    def to_bytes(self):
        out = bytearray()
        for row in self.rows:
            out.append((row >> 16) & 0xFF)
            out.append((row >> 8) & 0xFF)
            out.append(row & 0xFF)
        return out


def _draw_timer(c):
    c.circle(12, 12, 9)
    c.vline(12, 3, 2)
    c.vline(12, 19, 2)
    c.hline(3, 12, 2)
    c.hline(19, 12, 2)
    c.line(12, 12, 12, 6)
    c.line(12, 12, 16, 12)
    c.pixel(12, 12)


def _draw_stopwatch(c):
    c.circle(12, 13, 8)
    c.vline(11, 3, 2)
    c.vline(12, 3, 2)
    c.hline(9, 2, 6)
    c.line(18, 6, 20, 4)
    c.line(12, 13, 15, 9)
    c.pixel(12, 13)


def _draw_settings(c):
    c.fill_circle(12, 12, 7)
    c.clear_circle(12, 12, 3)
    for dx, dy in ((8, 0), (6, 6), (0, 8), (-6, 6),
                   (-8, 0), (-6, -6), (0, -8), (6, -6)):
        cx = 12 + dx
        cy = 12 + dy
        for ty in range(cy - 1, cy + 2):
            for tx in range(cx - 1, cx + 2):
                c.pixel(tx, ty)


def _draw_default(c):
    c.rect(4, 4, 6, 6)
    c.rect(14, 4, 6, 6)
    c.rect(4, 14, 6, 6)
    c.rect(14, 14, 6, 6)


_BUILDERS = {
    "timer": _draw_timer,
    "stopwatch": _draw_stopwatch,
    "settings": _draw_settings,
}


def get_icon(name):
    key = (name or "").strip().lower()
    icon = _cache.get(key)
    if icon is None:
        canvas = _Canvas()
        builder = _BUILDERS.get(key, _draw_default)
        builder(canvas)
        icon = (canvas.to_bytes(), ICON_SIZE, ICON_SIZE)
        _cache[key] = icon
    return icon


def get_columns(name):
    key = (name or "").strip().lower()
    cols = _column_cache.get(key)
    if cols is None:
        data, width, height = get_icon(key)
        cols = [0] * width
        for x in range(width):
            column = 0
            for y in range(height):
                byte = data[y * 3 + (x >> 3)]
                if byte & (0x80 >> (x & 7)):
                    column |= 1 << (height - 1 - y)
            cols[x] = column
        _column_cache[key] = cols
    return cols