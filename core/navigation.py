class Navigation:
    def __init__(self):
        self.stack = []

    def push(self, page):
        self.stack.append(page)
        page.open()

    def pop(self):
        if len(self.stack) > 1:
            page = self.stack.pop()
            page.close()

    def current(self):
        if len(self.stack) > 0:
            return self.stack[-1]
        return None