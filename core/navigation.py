class Navigation:
    def __init__(self, transition_ms=120):
        self.stack = []
        self.transition_ms = transition_ms
        self.transition = None

    def _start_transition(self, old_page, new_page, direction):
        if not old_page or not new_page or self.transition_ms <= 0:
            self.transition = None
            return
        self.transition = {
            "old": old_page,
            "new": new_page,
            "elapsed": 0,
            "direction": direction,
        }

    def push(self, page):
        current = self.current()
        if current:
            current.on_pause()
        self.stack.append(page)
        page.on_enter()
        self._start_transition(current, page, 1)

    def pop(self):
        if len(self.stack) <= 1:
            return None
        old = self.stack.pop()
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

    def update(self, delta_ms):
        if not self.transition:
            return False
        self.transition["elapsed"] += delta_ms
        if self.transition["elapsed"] >= self.transition_ms:
            self.transition = None
            return False
        return True

    def transition_progress(self):
        if not self.transition:
            return 1.0
        return min(1.0, self.transition["elapsed"] /
                   float(self.transition_ms))

    def current(self):
        if self.stack:
            return self.stack[-1]
        return None

    def can_go_back(self):
        return len(self.stack) > 1