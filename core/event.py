class Event:
    def __init__(self, type):
        self.type = type

# 系统事件类型
BUTTON_A = "button_a"
BUTTON_B = "button_b"
UP = "up"
DOWN = "down"

class EventManager:
    def __init__(self):
        self.queue = []

    def emit(self,event):
        self.queue.append(event)

    def poll(self):
        if len(self.queue)>0:
            return self.queue.pop(0)
        return None