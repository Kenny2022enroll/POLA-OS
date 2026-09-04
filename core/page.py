class Page:
    """Base page with lifecycle, invalidation and transition hooks."""
    def __init__(self):
        self.context = None
        self.dirty = True
        self.full_redraw = True
        self.dirty_rect = None

    def invalidate(self, rect=None):
        self.dirty = True
        if rect is None:
            self.full_redraw = True
            self.dirty_rect = None
        elif not self.full_redraw:
            self.dirty_rect = rect

    def validate(self):
        self.dirty = False
        self.full_redraw = False
        self.dirty_rect = None

    def take_dirty(self):
        return self.full_redraw, self.dirty_rect

    def on_enter(self):
        self.open()
        self.invalidate()

    def on_leave(self):
        self.close()

    def on_resume(self):
        self.invalidate()

    # Default no-op hooks share one function object to save RAM; apps
    # override whichever they need.
    def _noop(self, *args):
        pass

    on_pause = _noop
    on_suspend = _noop
    on_restore = _noop
    open = _noop
    close = _noop
    update = _noop
    on_event = _noop
    draw = _noop

    def draw_dirty(self, display, rect):
        self.draw(display)
