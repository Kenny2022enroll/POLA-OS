ICON_SIZE = 24

# One cache entry per icon: [bitmap bytes, column index or None].
# Columns are derived on demand for the Cover Flow side rendering.
_cache = {}


class _Canvas:
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


def render_icon(builder):
    canvas = _Canvas()
    if callable(builder):
        try:
            builder(canvas)
        except Exception:
            canvas = _Canvas()
    return canvas.to_bytes()


def _entry(name, builder):
    key = (name or "").strip().lower()
    entry = _cache.get(key)
    if entry is None:
        entry = [render_icon(builder), None]
        _cache[key] = entry
    return entry


def get_icon(name, builder=None):
    entry = _entry(name, builder)
    return entry[0], ICON_SIZE, ICON_SIZE


def get_columns(name, builder=None):
    entry = _entry(name, builder)
    cols = entry[1]
    if cols is None:
        data = entry[0]
        width = ICON_SIZE
        height = ICON_SIZE
        cols = [0] * width
        for x in range(width):
            column = 0
            for y in range(height):
                byte = data[y * 3 + (x >> 3)]
                if byte & (0x80 >> (x & 7)):
                    column |= 1 << (height - 1 - y)
            cols[x] = column
        entry[1] = cols
    return cols