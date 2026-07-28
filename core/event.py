class Event:
    def __init__(self, event_type):
        self.type = event_type

BUTTON_A = "button_a"
BUTTON_B = "button_b"
UP = "up"
DOWN = "down"
BUTTON_UP = "button_up"
BUTTON_DOWN = "button_down"
BUTTON_LEFT = "button_left"
BUTTON_RIGHT = "button_right"

class EventManager:
    def __init__(self):
        self.queue = []

    def emit(self, event):
        self.queue.append(event)

    def poll(self):
        if len(self.queue) > 0:
            return self.queue.pop(0)
        return None