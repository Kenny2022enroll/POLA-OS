from drivers.display import Display
from ui.launcher import Launcher

class Boot:
    def __init__(self):
        self.display = Display()
        self.launcher = Launcher(
            self.display
        )

    def start(self):
        self.display.clear()
        self.launcher.run()