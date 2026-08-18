class Event:
    def __init__(self, event_type, value=None):
        self.type = event_type
        self.value = value

# Semantic events used by pages instead of hardware button names.
SELECT = "select"
NAV_NEXT = "nav_next"
NAV_PREVIOUS = "nav_previous"
BACK = "back"
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

# Compatibility aliases for code that still imports the old names.
BUTTON_A = SELECT
BUTTON_B = NAV_NEXT
BUTTON_UP = UP
BUTTON_DOWN = DOWN
BUTTON_LEFT = LEFT
BUTTON_RIGHT = RIGHT

class EventManager:
    def __init__(self):
        self.queue = []

    def emit(self, event):
        self.queue.append(event)

    def poll(self):
        if len(self.queue) > 0:
            return self.queue.pop(0)
        return None