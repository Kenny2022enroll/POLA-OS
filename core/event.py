class Event:
    def __init__(self, event_type, value=None):
        self.type = event_type
        self.value = value

SELECT = "select"
BACK = "back"
NAV_NEXT = "nav_next"
NAV_PREVIOUS = "nav_previous"
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"

# Legacy names remain available for existing apps.
BUTTON_A = SELECT
BUTTON_B = NAV_NEXT
BUTTON_UP = UP
BUTTON_DOWN = DOWN
BUTTON_LEFT = LEFT
BUTTON_RIGHT = RIGHT


class EventManager:
    """Small fixed-size FIFO without list shifting on every event."""

    def __init__(self, max_size=32):
        self.max_size = max_size
        self.buffer = [None] * max_size
        self.head = 0
        self.tail = 0
        self.size = 0

    def emit(self, event):
        # Drop the oldest event when input temporarily outpaces the kernel.
        if self.size == self.max_size:
            self.head = (self.head + 1) % self.max_size
            self.size -= 1
        self.buffer[self.tail] = event
        self.tail = (self.tail + 1) % self.max_size
        self.size += 1

    def poll(self):
        if self.size == 0:
            return None
        event = self.buffer[self.head]
        self.buffer[self.head] = None
        self.head = (self.head + 1) % self.max_size
        self.size -= 1
        return event

    def clear(self):
        self.buffer = [None] * self.max_size
        self.head = 0
        self.tail = 0
        self.size = 0