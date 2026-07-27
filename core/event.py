class Event:
    def __init__(self,type):
        self.type = type

BUTTON_A = "button_a"
BUTTON_B = "button_b"

class EventManager:
    def __init__(self):
        self.queue = []

    def emit(self,event):
        self.queue.append(event)

    def poll(self):
        if self.queue:
            return self.queue.pop(0)
        return None