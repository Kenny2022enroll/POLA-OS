from drivers.display import Display
from drivers.input import Input
from core.scheduler import Scheduler
from core.event import EventManager
from core.app_manager import AppManager
from apps.registry import load_apps
from ui.launcher import Launcher

class Boot:
    def __init__(self):
        # 显示驱动
        self.display=Display()
        # 帧率控制
        self.scheduler=Scheduler(
            fps=10
        )
        # 事件系统
        self.events=EventManager()
        # 输入驱动
        self.input=Input(
            self.events
        )
        # App管理
        self.app_manager=AppManager()
        self.app_manager.load(
            load_apps()
        )
        # 桌面
        self.launcher=Launcher(
            self.display,
            self.scheduler,
            self.app_manager,
            self.events,
            self.input
        )

    def start(self):
        self.launcher.run()