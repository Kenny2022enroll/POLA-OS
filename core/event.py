class Event:
    def __init__(self, type):
        self.type = type
# 按键事件
BUTTON_A = "button_a"
BUTTON_B = "button_b"

# 方向事件
BUTTON_UP = "button_up"
BUTTON_DOWN = "button_down"
BUTTON_LEFT = "button_left"
BUTTON_RIGHT = "button_right"

class EventManager:
    def __init__(self):
        self.queue = []

    def emit(self,event):
        self.queue.append(event)

    def poll(self):
        if self.queue:
            return self.queue.pop(0)
        return None