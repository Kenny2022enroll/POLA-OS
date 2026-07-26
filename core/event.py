class Event:
    def __init__(
        self,
        name
    ):
        self.name=name

class EventManager:
    def __init__(self):
        self.queue=[]
        
    def emit(
        self,
        event
    ):
        self.queue.append(event)

    def get(self):
        if self.queue:
            return self.queue.pop(0)
        return None