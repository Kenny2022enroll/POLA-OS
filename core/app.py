from ui.page import Page

class App(Page):
    """应用基类，继承自 Page，统一内核中的页面抽象。"""
    name = "APP"
    def open(self):
        """页面入栈时调用，用于初始化资源。"""
        pass

    def close(self):
        """页面出栈时调用，用于释放资源。"""
        pass

    def update(self):
        """每帧调用，更新逻辑状态。"""
        pass

    def on_event(self, event):
        """处理用户事件，返回 'BACK' 则内核执行出栈。"""
        pass

    def draw(self, display):
        """每帧调用，将内容绘制到 display。"""
        pass