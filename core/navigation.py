class Navigation:
    def __init__(self, transition_ms=120):
        self.stack = []
        self.transition_ms = transition_ms
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