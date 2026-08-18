import time
from mpython import button_a, button_b
from core.event import Event, SELECT, NAV_NEXT, NAV_PREVIOUS

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
            self.events.emit(Event(SELECT))

        # B 键下降沿 → 判断单击/双击
        if self.last_b == 1 and b == 0:
            elapsed = time.ticks_diff(now, self.b_reset_timer)
            if self.b_click_count == 1 and elapsed <= DOUBLE_CLICK_MS:
                # 第二次按下在阈值内：上一项。
                self.events.emit(Event(NAV_PREVIOUS))
                self.b_click_count = 0
            else:
                # 超时后的第二次按下：先结算旧单击，再开始新单击。
                if self.b_click_count == 1:
                    self.events.emit(Event(NAV_NEXT))
                self.b_click_count = 1
                self.b_reset_timer = now

        # 超时后才确认单击，避免把迟到的第二次按下识别为双击。
        if (self.b_click_count == 1 and
                time.ticks_diff(now, self.b_reset_timer) > DOUBLE_CLICK_MS):
            self.events.emit(Event(NAV_NEXT))
            self.b_click_count = 0

        self.last_a = a
        self.last_b = b