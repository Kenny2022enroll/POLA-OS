import time
from mpython import button_a, button_b
from core.event import (
    Event,
    BUTTON_A,
    BUTTON_B,
    UP,
)

# 双击间隔阈值（毫秒），两次 B 键按下间隔小于此值视为双击
DOUBLE_CLICK_MS = 300

class Input:
    def __init__(self, event_manager):
        self.events = event_manager
        self.last_a = 1
        self.last_b = 1
        self.b_click_count = 0
        self.b_reset_timer = 0

    def update(self):
        a = button_a.value()
        b = button_b.value()
        now = time.ticks_ms()

        # A 键下降沿 → 确认
        if self.last_a == 1 and a == 0:
            self.events.emit(Event(BUTTON_A))

        # B 键下降沿 → 判断单击/双击
        if self.last_b == 1 and b == 0:
            if self.b_click_count == 0:
                # 第一次按下，等待是否第二次
                self.b_click_count = 1
                self.b_reset_timer = now + DOUBLE_CLICK_MS
            else:
                # 第二次按下在阈值内 → 双击 = 上移
                self.events.emit(Event(UP))
                self.b_click_count = 0

        # B 键超时未第二次按下 → 单击 = BUTTON_B
        if self.b_click_count == 1 and now > self.b_reset_timer:
            self.events.emit(Event(BUTTON_B))
            self.b_click_count = 0

        self.last_a = a
        self.last_b = b