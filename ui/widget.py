class Widget:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True

    def update(self, delta_ms=0):
        pass

    def draw(self, display):
        pass

    def on_event(self, event):
        return None