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
        self.wake_armed = False

    def _reclaim(self, force=False):
        """Reclaim large objects when the heap watchdog says so."""
        if self.context and hasattr(self.context, "memory"):
            self.context.memory.collect_if_needed(force=force)

    def _apply_brightness(self):
        if self.context and self.context.display:
            self.context.display.set_brightness(
                self.context.power.brightness)

    def _handle_crash(self, page, exc):
        """Replace a faulting app with an error dialog instead of halting."""
        from core.error_page import ErrorPage
        # If the error viewer itself faults, just drop it to avoid a loop.
        if isinstance(page, ErrorPage):
            self.navigation.remove(page)
            current = self.navigation.current()
            if current:
                current.invalidate()
            return
        try:
            name = getattr(page, "name", None) or page.__class__.__name__
        except Exception:
            name = "App"
        # Drop stale input and the faulting page, then surface the dialog.
        self.events.clear()
        try:
            self.input.reset()
        except Exception:
            pass
        self.navigation.remove(page)
        self.navigation.push(ErrorPage(name, exc))
        self.last_page = None
        self.sleep_drawn = False
        # Reclaim whatever the crashed app left behind.
        self._reclaim(force=True)

    def _dispatch(self, event):
        if self.context and self.context.power.activity():
            return False
        page = self.navigation.current()
        if not page:
            return False
        try:
            result = page.on_event(event)
        except Exception as exc:
            self._handle_crash(page, exc)
            return True
        if result == BACK:
            self.navigation.pop()
            current = self.navigation.current()
            if current:
                current.invalidate()
            self._reclaim()
            return False

        current = self.navigation.current()
        if not current:
            return False
        if isinstance(result, tuple):
            current.invalidate(result)
        else:
            current.invalidate()
        return False

    def _draw_full(self, page):
        self.display.begin_frame()
        self.display.clear()
        page.draw(self.display)
        page.validate()
        self.display.update()

    def _draw_dirty(self, page):
        full, rect = page.take_dirty()
        if full or self.last_page is not page:
            self._draw_full(page)
            return
        if rect is None:
            return
        if not self.display.supports_partial:
            self._draw_full(page)
            return
        self.display.begin_frame()
        self.display.clear_region(rect)
        page.draw_dirty(self.display, rect)
        page.validate()
        self.display.update()

    @staticmethod
    def _ease(progress):
        # Progress is fixed-point 0..1024; avoid float work per frame.
        if progress < 0:
            progress = 0
        elif progress > 1024:
            progress = 1024
        return (progress * progress * (3072 - 2 * progress)) // 1048576

    def _draw_transition(self):
        old_page = self.navigation.transition_old
        new_page = self.navigation.transition_new
        progress = self._ease(self.navigation.transition_progress())
        direction = self.navigation.transition_direction
        shift = (self.display.WIDTH * progress) // 1024

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
            active = self.input.update()
            event = self.events.poll()
            if self.context:
                power = self.context.power
                timeout = self.context.config.get("sleep_timeout", 60)
                power.update(delta_ms, timeout)
                if power.is_sleeping():
                    if power.observe_wake(active, delta_ms):
                        power.wake()
                        self.input.reset()
                        self.events.clear()
                        event = None
                        self.sleep_drawn = False
                        self._apply_brightness()
                    else:
                        if not self.sleep_drawn:
                            self.display.begin_frame()
                            self.display.clear()
                            self.display.update()
                            self.sleep_drawn = True
                        continue
                self._reclaim()

            while event:
                if self._dispatch(event):
                    # A crash swapped the page; stop draining stale input.
                    break
                event = self.events.poll()

            page = self.navigation.current()
            if not page:
                continue
            try:
                changed = page.update(delta_ms)
            except Exception as exc:
                self._handle_crash(page, exc)
                continue
            if changed:
                page.invalidate(changed if isinstance(changed, tuple) else None)
            transition_active = self.navigation.update(delta_ms)
            try:
                self._render(page, transition_active)
            except Exception as exc:
                self._handle_crash(page, exc)
                continue