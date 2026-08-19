# POLA-OS

POLA-OS 是运行在 mPython 掌控板上的轻量级嵌入式桌面系统原型。它直接使用 `.py` 文件运行，不要求本项目提供 `.mpy` 编译或刷入工具。

## 当前能力

- Home 桌面与 Applications 应用菜单
- P+Y 同时触摸：返回 `BACK`
- T+H 同时触摸：确认 `SELECT`
- O：上一个项目 `NAV_PREVIOUS`
- N：下一个项目 `NAV_NEXT`
- 页面生命周期：进入、暂停、恢复、离开
- UI 组件：`Window`、`Label`、`Button`、`ListView`、`Menu`、`Selector`、`Dialog`、`StatusBar`
- 系统服务：时钟、配置、电源状态
- JSON 配置持久化：主页样式、睡眠时间、声音开关
- 内置 `Timer`、`Stopwatch`、`Settings`
- 可选插件目录与示例插件

## 输入约定

掌控板六个金手指从左到右通常为 `P Y T H O N`：

| 触摸 | 事件 | 用途 |
| --- | --- | --- |
| `P + Y` | `BACK` | 返回上一级页面 |
| `T + H` | `SELECT` | 进入、确认、开始/暂停 |
| `O` | `NAV_PREVIOUS` | 列表上移 |
| `N` | `NAV_NEXT` | 列表下移 |

触摸阈值在 `drivers/input.py` 中由 `TOUCH_PRESS_THRESHOLD` 和 `TOUCH_RELEASE_THRESHOLD` 控制，当前默认值分别为 `260` 和 `330`。不同掌控板、环境湿度和触摸力度会影响读数，必要时应根据实际读数调整这两个值。

页面切换使用短时横向过渡，默认持续约 `90ms`，并采用整数定点缓动，避免动画热路径中的浮点计算。若实际固件整屏刷新速度不足，可在 `core/boot.py` 将 `transition_ms` 改为 `0`。

系统使用脏渲染：页面无变化时不会重复调用 `oled.show()`；支持 `fill_rect()` 的固件还会对计时器和秒表进行局部刷新。没有局部清屏 API 时会安全回退为整屏刷新。

睡眠唤醒需要检测到持续约 `60ms` 的触摸活动，唤醒时会清空旧事件并锁定当前触摸，必须先释放金手指，避免长按直接误触发返回或确认。

## 启动流程

```text
main.py
  -> Boot
     -> SystemContext
     -> Input / EventManager
     -> AppManager + plugins
     -> Home
     -> Kernel
```

页面切换使用 Navigation 页面栈：

```text
Home
  -> SELECT
Home, AppMenu
  -> SELECT
Home, AppMenu, Stopwatch
  -> BACK
Home, AppMenu
```

## 目录结构

```text
POLA-OS/
├── main.py
├── apps/                  页面和内置应用
│   ├── home.py            系统主页
│   ├── app_menu.py        应用菜单
│   ├── settings.py        配置选择页
│   ├── stopwatch.py       秒表
│   └── timer.py           计时器
├── core/                  内核、事件、导航和应用管理
├── drivers/               OLED 和触摸驱动
├── services/              时钟、配置、电源和系统上下文
├── ui/                    可复用 UI 组件
├── plugins/               可选插件及示例
├── data/config.json       默认配置文件
└── assets/                宣传图等资源
```

## 设置

进入 `Settings` 后：

- `O` / `N`：选择设置项
- `T + H`：循环修改当前设置并立即保存
- `P + Y`：返回

当前设置项：

- Home：`default` / `minimal`
- Sleep：`off` / `30s` / `60s`
- Sound：`on` / `off`

配置存储在 `data/config.json`。设备重启后会自动读取。

## 新增应用

应用继承 `core.app.App`，实现 `open()`、`update(delta_ms)`、`on_event(event)` 和 `draw(display)`：

```python
from core.app import App
from core.event import BACK


class Example(App):
    name = "Example"

    def on_event(self, event):
        if event.type == BACK:
            return BACK
```

然后在 `apps/registry.py` 中注册应用类。

## 插件

插件放在 `plugins/<name>/`：

```text
plugins/HelloWorld/
├── manifest.py
└── app.py
```

`manifest.py` 提供 `PLUGIN` 字典，`app.py` 提供 `APP_CLASS`。插件目录保留为可选扩展，但为了降低启动时间和运行内存，系统默认不会扫描或导入插件。需要启用插件时，应在启动流程中显式调用 `plugins.loader.load_plugins()`。

当前示例插件位于 `plugins/sample/`，默认不加载。

## 许可证

本项目遵循仓库中的 [LICENSE](LICENSE) 文件。
