from ui.theme import Theme
from ui.icons import get_icon, get_columns, ICON_SIZE

CENTER_X = 64
ICON_TOP = 12
ICON_CENTER_Y = ICON_TOP + ICON_SIZE // 2
NAME_Y = 47
NAME_MAX_CHARS = 15
SIDE_X = 34
EXTRA_X = 16
SIDE_W = 14
SIDE_NEAR_H = 21
SIDE_FAR_H = 13
CULL_D = 2400
EASE_TC_MS = 140
MAX_STEPS_PER_S = 4
SNAP_DIST = 32
STEP = 1024


def _band_masks(h):
    """Per-output-row source-band bitmasks for vertical scale 24 -> h.

    Computed on demand (h only spans a handful of values) instead of
    being cached forever, keeping the desktop's idle RAM lower.
    """
    masks = []
    for j in range(h):
        y0 = (j * ICON_SIZE) // h
        y1 = (((j + 1) * ICON_SIZE) // h) - 1
        top = ICON_SIZE - 1 - y0
        lo = ICON_SIZE - 1 - y1
        masks.append(((1 << (top - lo + 1)) - 1) << lo)
    return masks


class CoverFlow:
    """iPod Cover Flow style app carousel for the system desktop.

    ``items`` is a list of ``AppInfo`` entries; each app supplies its
    own icon builder through its manifest, so the desktop never ships
    icons of its own.
    """

    def __init__(self, items):
        self.items = list(items)
        self.target = 0
        self.pos = 0
        # Pre-allocated buffers to avoid per-frame heap allocation.
        # The culling window shows at most 5 icons (center + 2 per side).
        self._sort_buf = [[0, 0, 0] for _ in range(5)]
        self._union_cols = [0] * ICON_SIZE

    def count(self):
        return len(self.items)

    def selected(self):
        if not self.items:
            return 0
        index = self.target // STEP
        if index < 0:
            return 0
        if index >= len(self.items):
            return len(self.items) - 1
        return index

    def next(self):
        limit = (len(self.items) - 1) * STEP
        if self.target < limit:
            self.target += STEP

    def previous(self):
        if self.target > 0:
            self.target -= STEP

    def update(self, delta_ms=0):
        if self.pos == self.target:
            return False
        remaining = self.target - self.pos
        if -SNAP_DIST < remaining < SNAP_DIST:
            self.pos = self.target
            return True
        step = (remaining * delta_ms) // EASE_TC_MS
        if step == 0:
            step = 1 if remaining > 0 else -1
        max_step = (MAX_STEPS_PER_S * STEP * delta_ms) // 1000
        if max_step <= 0:
            max_step = 1
        if step > max_step:
            step = max_step
        elif step < -max_step:
            step = -max_step
        if remaining > 0:
            self.pos += min(step, remaining)
        else:
            self.pos += max(step, remaining)
        return True

    def settled(self):
        return self.pos == self.target

    def draw(self, display):
        if not self.items:
            return
        # Pre-allocated buffer: max 5 visible icons (center + 2 each side)
        # Each entry: [abs_d, index, signed_d]
        count = 0
        for i in range(len(self.items)):
            d = self.pos - i * STEP
            if -CULL_D < d < CULL_D:
                if count < len(self._sort_buf):
                    self._sort_buf[count][0] = abs(d)
                    self._sort_buf[count][1] = i
                    self._sort_buf[count][2] = d
                else:
                    self._sort_buf.append([abs(d), i, d])
                count += 1
        # Sort only the active slice (in-place, no allocation)
        for i in range(count - 1):
            for j in range(i + 1, count):
                if self._sort_buf[i][0] < self._sort_buf[j][0]:
                    self._sort_buf[i], self._sort_buf[j] = self._sort_buf[j], self._sort_buf[i]
        for k in range(count):
            _, i, d = self._sort_buf[k]
            if d == 0:
                self._draw_center(display, i)
            else:
                self._draw_side(display, i, d)
        self._draw_caption(display)

    def _draw_center(self, display, index):
        info = self.items[index]
        data, width, height = get_icon(info.name, info.icon)
        x = CENTER_X - width // 2
        display.rect(x - 2, ICON_TOP - 2, width + 4, height + 4)
        display.blit(data, x, ICON_TOP, width, height)
        rows = 5
        for k in range(rows):
            src_row = height - 1 - k
            y = ICON_TOP + height + 2 + k
            base = src_row * 3
            for c in range(width):
                if data[base + (c >> 3)] & (0x80 >> (c & 7)):
                    if ((c + k) & 1) == 0:
                        display.pixel(x + c, y)

    def _draw_side(self, display, index, d):
        info = self.items[index]
        cols = get_columns(info.name, info.icon)
        sigma = -1 if d > 0 else 1
        ad = d if d > 0 else -d
        s = ad if ad < STEP else STEP
        extra = ad - STEP if ad > STEP else 0
        x_off = ((SIDE_X * s) >> 10) + ((EXTRA_X * extra) >> 10)
        width = ICON_SIZE - (((ICON_SIZE - SIDE_W) * s) >> 10)
        near_h = ICON_SIZE - (((ICON_SIZE - SIDE_NEAR_H) * s) >> 10)
        far_h = ICON_SIZE - (((ICON_SIZE - SIDE_FAR_H) * s) >> 10)
        if width <= 0 or near_h <= 0 or far_h <= 0:
            return
        # Reuse pre-allocated _union_cols array (size = ICON_SIZE)
        uc = self._union_cols
        for c in range(ICON_SIZE):
            uc[c] = 0
        for c in range(ICON_SIZE):
            uc[(c * width) // ICON_SIZE] |= cols[c]
        union_cols = uc  # local alias for readability below
        x_left = CENTER_X + sigma * x_off - width // 2
        if x_left >= Theme.SCREEN_WIDTH or x_left + width <= 0:
            return
        span = width - 1 if width > 1 else 1
        for sx in range(width):
            column = union_cols[sx]
            if column == 0:
                continue
            if sigma > 0:
                h = near_h - ((near_h - far_h) * sx) // span
            else:
                h = far_h + ((near_h - far_h) * sx) // span
            if h <= 0:
                continue
            x = x_left + sx
            y_top = ICON_CENTER_Y - h // 2
            self._draw_column(display, column, x, y_top, h)

    @staticmethod
    def _draw_column(display, column, x, y_top, h):
        masks = _band_masks(h)
        j = 0
        while j < h:
            if column & masks[j]:
                run = 1
                while j + run < h and column & masks[j + run]:
                    run += 1
                display.vline(x, y_top + j, run)
                j += run
            else:
                j += 1

    def _draw_caption(self, display):
        name = self.items[self.selected()].name
        if len(name) > NAME_MAX_CHARS:
            name = name[:NAME_MAX_CHARS]
        width = len(name) * 8
        display.text_small(name, CENTER_X - width // 2, NAME_Y)