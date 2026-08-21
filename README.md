# POLA-OS

POLA-OS 是运行在 mPython 掌控板上的轻量级嵌入式桌面系统原型。
[`了解如何参与POLA OS应用/插件开发`](third_party/devlib/POLA-OS应用开发手册.md)

## 依赖库：devlib（替代官方 mpython.py）

本系统**不使用**官方固件的 `mpython.py`，而是使用第三方优化库 [devlib](https://github.com/emofalling/devlib)（作者 emofalling，MIT 协议）。devlib 大幅提升了 OLED 刷新与图像处理性能，并为 `oled` 提供原生 `contrast()` 亮度接口。

- **安装**：把 `third_party/devlib/devlib.mpy`（盛思掌控板用 `xtensawin` 发行版）上传到掌控板文件系统根目录，使 `import devlib` 可用。
- **互斥**：`devlib` 与 `mpython` **不能同时导入**（两者都会初始化 I2C 与引脚，会相互冲突）。本项目代码只导入 `devlib`，请勿再引入 `mpython`。
- **许可证**：devlib 为 MIT 协议，其版权声明见 [`third_party/devlib/LICENSE`](third_party/devlib/LICENSE)。分发本项目时须一并保留该声明。
- **注意**：devlib 的 `oled.DispChar` 默认使用 16px 高字体，且 OLED 驱动为 SSD1106。若在实机上发现行距重叠或显示偏移，请调整 `ui/theme.py` 中的 `TITLE_Y`/`CONTENT_Y`/`ROW_HEIGHT` 等常量。devlib 默认开启 I2C 超频（1250KHz），若外接设备不稳可在 devlib 源码中将 `overclock` 改为 `False`。

## 当前能力

- Home 桌面与 Applications 应用菜单
- P+Y 同时触摸：返回 `BACK`
- T+H 同时触摸：确认 `SELECT`
- O：上一个项目 `NAV_PREVIOUS`
- N：下一个项目 `NAV_NEXT`
- 页面生命周期：进入、暂停、恢复、离开
- UI 组件：`Window`、`Label`、`Button`、`ListView`、`Menu`、`Selector`、`Dialog`、`StatusBar`
- 系统服务：时钟、配置、电源状态、内存看门狗
- JSON 配置持久化：主页样式、亮度、睡眠时间、声音开关
- 内置 `Timer`、`Stopwatch`、`Settings`
- 可选插件目录与示例插件
- 页面栈深度限制（默认 8 层）与低水位大对象回收（`gc.collect()`）
- 应用崩溃捕获：异常时弹出错误对话框，`P+Y`/`T+H` 关闭并返回上一级
- 屏幕亮度调节（通过 devlib 的 `oled.contrast()` 原生支持，`Settings` 中可调）

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
├── core/                  内核、事件、导航、应用管理和错误对话框
├── drivers/               OLED 和触摸驱动
├── services/              时钟、配置、电源、内存和系统上下文
├── ui/                    可复用 UI 组件
├── plugins/               可选插件及示例
├── tests/                 宿主机回归测试（mock 硬件模块）
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
- Bright：`25` / `50` / `80` / `100`（亮度百分比，devlib 提供原生 `oled.contrast()`，修改即时生效）
- Sleep：`off` / `30s` / `60s`
- Sound：`on` / `off`

配置存储在 `data/config.json`。设备重启后会自动读取。

## 稳定性

- **页面栈深度限制**：`Navigation(max_depth=8)`。超过上限时淘汰根页面之上最旧的页面，防止深层导航耗尽内存。
- **大对象回收**：`services/memory.py` 的 `MemoryService` 通过 `gc.threshold()` 提前触发运行时 GC，并在空闲内存低于低水位（默认 4 KB）或应用崩溃后执行 `gc.collect()` 全量回收。
- **崩溃捕获**：内核包裹页面的事件、更新与绘制调用。应用抛出异常时，内核会移除出错页面、清空积压输入，并压入错误对话框页（显示应用名、异常类型与信息摘要）；按 `P+Y` 或 `T+H` 关闭对话框并回到出错页面之下的一级页面。

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

本项目代码遵循仓库中的 [LICENSE](LICENSE) 文件（MIT，Copyright (c) 2025 Kenny）。

第三方依赖：

- [devlib](https://github.com/emofalling/devlib) — MIT，Copyright (c) 2025 emofalling。声明见 [`third_party/devlib/LICENSE`](third_party/devlib/LICENSE)，随本项目分发时须保留。