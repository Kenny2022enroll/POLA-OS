class Page:
    """页面基类，是 App 的父类。统一内核中的页面抽象。"""
    def __init__(self):
        self.running = True

    def open(self):
        """页面入栈时调用。"""
        pass

    def close(self):
        """页面出栈时调用。"""
        pass

    def update(self):
        """每帧调用，更新逻辑。"""
        pass

    def on_event(self, event):
        """处理事件，返回 'BACK' 则内核执行出栈。"""
        pass

    def draw(self, display):
        """每帧调用，绘制到 display。"""
        pass

    def exit(self):
        self.running = False