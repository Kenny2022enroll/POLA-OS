from core.app import App
from ui.theme import Theme
from core.event import (
    BUTTON_A,
    BUTTON_B,
    UP,
)

class Launcher(App):
    name = "Launcher"
    def __init__(self, manager, navigation):
        self.manager = manager
        self.navigation = navigation
        self.index = 0

    def on_event(self, event):
        apps = self.manager.get_apps()

        # B 单击 = 下一项（循环）
        if event.type == BUTTON_B:
            self.index += 1
            if self.index >= len(apps):
                self.index = 0

        # B 双击 = 上一项（循环）
        elif event.type == UP:
            self.index -= 1
            if self.index < 0:
                self.index = len(apps) - 1

        # A = 确认 → 打开选中的应用
        elif event.type == BUTTON_A:
            app = apps[self.index]
            self.navigation.push(app)

    def draw(self, display):
        display.text("POLA OS", 25, Theme.TITLE_Y)

        apps = self.manager.get_apps()
        y = Theme.CONTENT_Y

        for i, app in enumerate(apps):
            name = app.name
            if i == self.index:
                name = "> " + name
            display.text(name, 15, y)
            y += 12