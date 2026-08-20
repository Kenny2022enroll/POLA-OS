class Navigation:
    def __init__(self, transition_ms=120, max_depth=8):
        self.stack = []
        self.transition_ms = transition_ms
        # Bound the page stack so deeply nested navigation cannot exhaust
        # RAM. A value <= 0 disables the limit.
        self.max_depth = max_depth
        self.transition_old = None
        self.transition_new = None
        self.transition_elapsed = 0
        self.transition_direction = 0

    def _start_transition(self, old_page, new_page, direction):
        if not old_page or not new_page or self.transition_ms <= 0:
            self.transition_old = None
            self.transition_new = None
            return
        self.transition_old = old_page
        self.transition_new = new_page
        self.transition_elapsed = 0
        self.transition_direction = direction

    def _clear_transition_refs(self, page):
        if self.transition_old is page:
            self.transition_old = None
        if self.transition_new is page:
            self.transition_new = None

    def _enforce_depth(self):
        if self.max_depth <= 0:
            return
        # Never evict the root (index 0) or the page currently on top.
        # Evict the oldest page above the root so its memory can be freed.
        while len(self.stack) > self.max_depth and len(self.stack) >= 3:
            victim = self.stack[1]
            del self.stack[1]
            self._clear_transition_refs(victim)
            try:
                victim.on_leave()
            except Exception:
                pass

    def push(self, page):
        current = self.current()
        if current:
            current.on_pause()
        self.stack.append(page)
        self._enforce_depth()
        if current is not None and current not in self.stack:
            # The depth limit evicted the previous page; skip the transition.
            current = None
        page.on_enter()
        self._start_transition(current, page, 1)

    def pop(self):
        if len(self.stack) <= 1:
            return None
        old = self.stack.pop()
        self._clear_transition_refs(old)
        old.on_leave()
        current = self.current()
        if current:
            current.on_resume()
        self._start_transition(old, current, -1)
        return old

    def replace(self, page):
        old = self.current()
        if self.stack:
            self.stack.pop()
            old.on_leave()
        self.stack.append(page)
        page.on_enter()
        self._start_transition(old, page, 1)

    def remove(self, page):
        """Remove a specific page (e.g. one that crashed) from the stack."""
        if page not in self.stack:
            return
        index = self.stack.index(page)
        is_top = index == len(self.stack) - 1
        del self.stack[index]
        self._clear_transition_refs(page)
        try:
            page.on_leave()
        except Exception:
            pass
        if is_top:
            current = self.current()
            if current:
                current.on_resume()
                current.invalidate()

    def update(self, delta_ms):
        if self.transition_old is None:
            return False
        self.transition_elapsed += delta_ms
        if self.transition_elapsed >= self.transition_ms:
            self.transition_old = None
            self.transition_new = None
            return False
        return True

    def transition_progress(self):
        if self.transition_old is None:
            return 1024
        progress = (self.transition_elapsed * 1024) // self.transition_ms
        return min(1024, progress)

    def current(self):
        if self.stack:
            return self.stack[-1]
        return None

    def can_go_back(self):
        return len(self.stack) > 1