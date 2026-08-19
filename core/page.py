class Page:
    """Base page with lifecycle, invalidation and transition hooks."""

    def __init__(self):
        self.running = True
        self.context = None
        self.dirty = True
        self.full_redraw = True
        self.dirty_regions = []

    def invalidate(self, rect=None):
        self.dirty = True
        if rect is None:
            self.full_redraw = True
            self.dirty_regions = []
        elif not self.full_redraw:
            self.dirty_regions.append(rect)

    def validate(self):
        self.dirty = False
        self.full_redraw = False
        self.dirty_regions = []

    def take_dirty(self):
        full = self.full_redraw
        regions = self.dirty_regions[:]
        return full, regions

    def on_enter(self):
        self.open()
        self.invalidate()

    def on_leave(self):
        self.close()

    def on_pause(self):
        pass

    def on_resume(self):
        self.invalidate()

    def open(self):
        pass

    def close(self):
        pass

    def update(self, delta_ms=0):
        pass

    def on_event(self, event):
        pass

    def draw(self, display):
        pass

    def draw_dirty(self, display, regions):
        self.draw(display)

    def transition_in(self, progress):
        return None

    def transition_out(self, progress):
        return None

    def exit(self):
        self.running = False