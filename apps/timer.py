from core.app import App
import time

class Timer(App):
    name="Timer"
    def open(self):
        self.start=time.time()
        self.value=0

    def update(self):
        self.value=int(
            time.time()-self.start
        )

    def draw(self,display):
        display.text(
            "Timer",
            40,
            20
        )
        display.text(
            str(self.value),
            55,
            40
        )

    def on_event(self,event):
        from core.event import BUTTON_B
        if event.type==BUTTON_B:
            return "BACK"