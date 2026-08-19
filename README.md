# POLA-OS

![POLA-OS 宣传图](assets/pola-os-promo.jpg)

POLA-OS 是一个运行在 mPython 掌控板上的轻量级嵌入式桌面系统原型。项目提供 OLED 图形显示、金手指触摸输入、事件分发、页面导航、应用注册和可复用 UI 组件等基础能力。

> 当前分支：`Takla_beta`
>
> 项目仍处于早期开发阶段，API 和硬件交互方式可能发生变化。

## 功能概览

- OLED 128x64 图形界面
- 基于页面栈的应用导航
- 语义化事件系统：确认、返回、列表切换
- 金手指组合触摸输入
- 应用启动器
- `Timer` 计时器
- `Stopwatch` 秒表
- `Settings` 设置页面原型
- `Window`、`Label`、`Button`、`ListView` UI 组件

## 硬件输入

项目使用 mPython 掌控板正面的六个金手指。金手指从左到右通常对应：

```text
P   Y   T   H   O   N
```

当前输入约定：

| 触摸组合 | 语义事件 | 用途 |
| --- | --- | --- |
| `P + Y` 同时触摸 | `BACK` | 返回上一级页面 |
| `T + H` 同时触摸 | `SELECT` | 确认、进入、开始或暂停 |
| `O` | 暂未使用 | 预留 |
| `N` | 暂未使用 | 预留 |

输入驱动使用触摸值阈值判断是否按下，默认阈值为 `200`。如果实际硬件触摸不稳定，可以调整 `drivers/input.py` 中的 `TOUCH_THRESHOLD`。

## 运行流程

```text
main.py
  -> Boot
     -> Display
     -> Input
     -> EventManager
     -> AppManager
     -> Navigation
     -> Kernel
        -> 读取输入
        -> 分发事件
        -> 更新当前页面
        -> 绘制 OLED
```

系统启动后会加载应用并显示 Launcher。Launcher 负责显示应用列表，Navigation 负责在桌面和应用页面之间切换，Kernel 负责持续运行主循环。

## 项目结构

```text
POLA-OS/
├── main.py                 程序入口
├── assets/
│   └── pola-os-promo.jpg   项目宣传图
├── core/
│   ├── app.py              应用基类
│   ├── app_manager.py      应用管理器
│   ├── boot.py             系统初始化与组装
│   ├── event.py            事件类型与事件队列
│   ├── kernel.py           系统主循环
│   ├── navigation.py       页面栈导航
│   └── scheduler.py        帧率调度
├── drivers/
│   ├── display.py          OLED 显示驱动封装
│   └── input.py            金手指触摸输入驱动
├── apps/
│   ├── registry.py         应用注册表
│   ├── settings.py         设置页面
│   ├── stopwatch.py        秒表应用
│   └── timer.py            计时器应用
└── ui/
    ├── button.py           按钮组件
    ├── label.py            文本组件
    ├── launcher.py         应用启动器
    ├── list_view.py        可选择列表组件
    ├── page.py             页面基类
    ├── theme.py            UI 布局参数
    ├── widget.py           UI 组件基类
    └── window.py           UI 容器组件
```

## 核心设计

### 事件流

硬件输入不会直接操作应用，而是转换为语义事件：

```text
金手指触摸
  -> drivers/input.py
  -> Event(BACK / SELECT)
  -> EventManager
  -> 当前页面 on_event()
```

应用只需要处理语义事件，不需要知道具体使用了哪一个 GPIO 或触摸焊盘。

### 页面导航

Navigation 使用页面栈管理页面：

```text
[Launcher]
    -> SELECT
[Launcher, Stopwatch]
    -> BACK
[Launcher]
```

页面返回 `BACK` 时，由 Kernel 调用 Navigation 弹出当前页面。应用不直接操作主循环，也不直接操作硬件驱动。

### UI 组件

UI 组件统一通过 `draw(display)` 绘制，通过 `Window` 组合：

```text
Window
├── Label
├── Button
└── ListView
```

`ListView` 负责选中项、循环切换和屏幕可见范围；应用页面只负责提供数据和响应事件。


## 开发新应用

1. 在 `apps/` 下创建一个继承 `App` 的类。
2. 实现 `name`、`open()`、`update()`、`on_event()` 和 `draw()`。
3. 使用 `Window`、`Label`、`Button` 或 `ListView` 构建界面。
4. 在 `apps/registry.py` 的 `load_apps()` 中注册应用。

示例：

```python
from core.app import App
from core.event import BACK, SELECT


class Example(App):
    name = "Example"

    def on_event(self, event):
        if event.type == SELECT:
            pass
        elif event.type == BACK:
            return BACK
```

## 开发建议

建议按照以下顺序继续开发：

1. 为 `Input`、`Navigation`、`ListView` 和应用页面增加 FakeDisplay/FakeClock 测试。
2. 为 `O`、`N` 金手指定义列表上移和下移事件。
3. 完善 Launcher 的滚动和焦点显示。
4. 为 Settings 增加持久化配置。
5. 增加 Stopwatch 的重置功能和更高精度显示。
6. 再开发计算器、传感器、便签等应用。

## 部署

将项目文件复制到支持 mPython 固件的掌控板文件系统后，运行 `main.py`。项目依赖固件提供的：

- `mpython.oled`
- `mpython.touchPad_P`
- `mpython.touchPad_Y`
- `mpython.touchPad_T`
- `mpython.touchPad_H`
- MicroPython 的 `time.ticks_ms()`

不同固件版本的模块名称可能略有差异。如果启动时报导入错误，需要根据当前固件 API 调整 `drivers/input.py` 或 `drivers/display.py`。

## 许可证

本项目遵循仓库中的 [LICENSE](LICENSE) 文件。