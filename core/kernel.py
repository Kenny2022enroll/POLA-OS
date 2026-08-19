from core.event import BACK

class Kernel:
    def __init__(self, display, scheduler, input, events, navigation,
                 context=None):
        self.display = display
        self.scheduler = scheduler
        self.input = input
        self.events = events
        self.navigation = navigation
        self.context = context
        self.last_page = None
        self.sleep_drawn = False

    def _dispatch(self, event):
        if self.context and self.context.power.activity():
            return
        page = self.navigation.current()
        if not page:
            return
        result = page.on_event(event)
        if result == BACK:
            self.navigation.pop()
            current = self.navigation.current()
            if current:
                current.invalidate()
            return

        current = self.navigation.current()
        if not current:
            return
        if isinstance(result, tuple):
            current.invalidate(result)
        else:
            # Events can change arbitrary page state, so invalidate by default.
            current.invalidate()

    def _draw_full(self, page):
        self.display.begin_frame()
        self.display.clear()
        page.draw(self.display)
        page.validate()
        self.display.update()

    def _draw_dirty(self, page):
        full, regions = page.take_dirty()
        if full or self.last_page is not page:
            self._draw_full(page)
            return
        if not regions:
            return
        if not self.display.supports_partial:
            self._draw_full(page)
            return
        self.display.begin_frame()
        for rect in regions:
            self.display.clear_region(rect)
        page.draw_dirty(self.display, regions)
        page.validate()
        self.display.update()

    def _draw_transition(self):
        transition = self.navigation.transition
        old_page = transition["old"]
        new_page = transition["new"]
        progress = self.navigation.transition_progress()
        direction = transition["direction"]
        shift = int(self.display.WIDTH * progress)

        self.display.begin_frame()
        self.display.clear()
        self.display.set_offset(-shift if direction > 0 else shift, 0)
        old_page.draw(self.display)
        self.display.set_offset(
            self.display.WIDTH - shift if direction > 0 else
            shift - self.display.WIDTH,
            0,
        )
        new_page.draw(self.display)
        self.display.reset_offset()
        self.display.update()

    def _render(self, page, transition_active):
        if transition_active:
            self._draw_transition()
            return
        self._draw_dirty(page)
        self.last_page = page

    def run(self):
        while True:
            delta_ms = self.scheduler.wait()
            self.input.update()
            event = self.events.poll()
            if self.context:
                timeout = self.context.config.get("sleep_timeout", 60)
                self.context.power.update(delta_ms, timeout)
            if self.context and self.context.power.is_sleeping():
                if event:
                    self.context.power.activity()
                    self.sleep_drawn = False
                if not self.sleep_drawn:
                    self.display.begin_frame()
                    self.display.clear()
                    self.display.update()
                    self.sleep_drawn = True
                continue

            self.sleep_drawn = False
            while event:
                self._dispatch(event)
                event = self.events.poll()

            page = self.navigation.current()
            if not page:
                continue
            changed = page.update(delta_ms)
            if changed:
                page.invalidate(changed if isinstance(changed, tuple) else None)
            transition_active = self.navigation.update(delta_ms)
            self._render(page, transition_active)