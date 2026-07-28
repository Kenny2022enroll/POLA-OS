from core.app import App
from core.event import (
    BUTTON_A,
    UP,
    DOWN
)

class Launcher(App):
    name = "Launcher"
    def __init__(
        self,
        manager,
        navigation
    ):
        self.manager = manager
        self.navigation = navigation
        self.index = 0

    def on_event(self,event):
        apps = self.manager.get_apps()
        if event.type == DOWN:
            self.index += 1
            if self.index >= len(apps):
                self.index = 0
        elif event.type == UP:
            self.index -= 1
            if self.index < 0:
                self.index = len(apps)-1
        elif event.type == BUTTON_A:
            app = apps[self.index]
            self.navigation.push(
                app
            )

    def draw(self,display):
        display.text(
            "POLA OS",
            25,
            0
        )
        apps=self.manager.get_apps()
        y=20
        for i,app in enumerate(apps):
            name=app.name
            if i==self.index:
                name="> "+name
            display.text(
                name,
                15,
                y
            )
            y+=12