from core.event import Event

class Input:
    def __init__(
        self,
        event_manager
    ):
        self.events=event_manager

    def update(self):
        # 这里以后接真实按键
        pass