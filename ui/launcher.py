from core.app import App
from core.event import (
    BUTTON_A,
    BUTTON_DOWN
)

class Launcher(App):
    name="Launcher"
    def __init__(
        self,
        manager,
        navigation
    ):
        self.manager=manager
        self.navigation=navigation
        self.index=0

    def on_event(self,event):
        if event.type==BUTTON_A:
            apps=self.manager.get_apps()
            app=apps[self.index]
            self.navigation.push(
                app
            )

    def update(self):
        pass

    def draw(self,display):
        display.text(
            "POLA OS",
            25,
            0
        )
        apps=self.manager.get_apps()
        y=20
        for i,app in enumerate(apps):
            text=app.name
            if i==self.index:
                text=">"+text
            display.text(
                text,
                20,
                y
            )
            y+=12