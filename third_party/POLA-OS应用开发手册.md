# POLA-OS 应用开发手册

版本：v1.0（Takla_rc2_beta）  
适用硬件：mPython 掌控板  
适用固件：支持 xtensawin 的 MicroPython 固件  
适用人群：学生、教师、创客、MicroPython 开发者

## 目录

1. 开发环境准备
2. 理解 POLA-OS 应用模型
3. 创建你的第一个应用
4. 应用生命周期详解
5. 事件处理机制
6. UI 组件使用指南
7. 页面导航与返回
8. 配置管理
9. 插件开发指南
10. 调试与错误处理
11. 性能优化建议
12. 发布与部署
13. 附录：API 速查表

## 1. 开发环境准备

### 1.1 硬件要求
mPython 掌控板
USB 数据线

### 1.2 软件要求（任选）
mPython 官方编辑器
Pyrite IDE 第三方编辑器

### 1.3 固件要求

- 掌控板必须刷入 盛思掌控板专用 MicroPython 固件（支持 xtensawin）
- 为获得更加设备性能，本项目使用第三方的 devlib 库代替官方 mpython 库

### 1.4 项目文件结构

掌控板根目录/
├── main.py              ← 系统入口（勿删）
├── devlib.py           ← 核心驱动库（必须存在）
├── core/                ← 系统内核
├── drivers/             ← 硬件驱动
├── services/            ← 系统服务
├── ui/                  ← UI 组件
├── apps/                ← 内置应用 ← 【你的应用放这里】
├── plugins/             ← 插件目录
└── data/
    └── config.json      ← 系统配置

### 1.5 首次上传清单

确保以下文件/目录已上传到掌控板根目录：

✅ devlib.py
✅ main.py
✅ core/（整个目录）
✅ drivers/（整个目录）
✅ services/（整个目录）
✅ ui/（整个目录）
✅ apps/（整个目录）
✅ data/config.json

## 2. 理解 POLA-OS 应用模型

### 2.1 什么是 POLA-OS 应用？

在 POLA-OS 中，一个应用（App）就是一个继承自 core.app.App 的 Python 类。每个应用负责：

- 显示自己的界面
- 响应用户的触摸事件
- 管理自己的状态
- 在适当的时候返回上一页

### 2.2 应用与系统的关系

┌─────────────────────────────────────┐
│           POLA-OS 内核              │
│  ┌─────────┐  ┌──────────────────┐  │
│  │ 事件管理 │  │   页面导航栈      │  │
│  └────┬────┘  └────────┬─────────┘  │
│       │                │             │
│  ┌────▼────────────────▼──────────┐  │
│  │         你的 App               │  │
│  │  open() / update() / draw()    │  │
│  │  on_event()                    │  │
│  └────────────────────────────────┘  │
└─────────────────────────────────────┘

- 内核负责：事件分发、页面切换、内存管理、错误处理
- 你的 App负责：业务逻辑、界面绘制、事件响应

### 2.3 应用的最小结构

from core.app import App

class MyApp(App):
    name = "我的应用"

    def open(self, display):
        """页面进入时调用"""
        pass

    def update(self, delta_ms):
        """每帧更新时调用"""
        pass

    def on_event(self, event):
        """收到事件时调用"""
        return None

    def draw(self, display):
        """绘制界面"""
        pass

## 3. 创建你的第一个应用

### 3.1 目标：创建一个 "Hello POLA" 应用

功能：在屏幕上显示 "Hello POLA"，按返回键退出。

### 3.2 步骤一：创建应用文件

在 apps/ 目录下创建 hello.py：

from core.app import App
from core.event import BACK

class HelloApp(App):
    name = "Hello POLA"

    def open(self, display):
        # 保存 display 引用，供 draw() 使用
        self.display = display
        # 首次绘制
        self.draw(display)

    def update(self, delta_ms):
        # 本应用无动态内容，留空即可
        pass

    def on_event(self, event):
        if event.type == BACK:
            return BACK  # 告诉系统：返回上一页
        return None

    def draw(self, display):
        display.clear()
        display.text("Hello POLA", 16, 24)
        display.text("Welcome!", 24, 40)
        display.show()

### 3.3 步骤二：注册应用

编辑 apps/registry.py（或 apps/__init__.py，取决于项目版本），将你的应用加入列表：

from apps.home import Home
from apps.app_menu import AppMenu
from apps.settings import Settings
from apps.stopwatch import Stopwatch
from apps.timer import Timer
from apps.hello import HelloApp  # ← 新增这行

APPS = [
    Home,
    AppMenu,
    Settings,
    Stopwatch,
    Timer,
    HelloApp,  # ← 新增这行
]

### 3.4 步骤三：上传到掌控板

使用 mPython 或 PyriteIDE：

1. 连接掌控板
2. 打开 apps/hello.py → 右键 → "上传到设备"
3. 打开 apps/registry.py → 右键 → "上传到设备"
4. 重启掌控板

### 3.5 步骤四：测试

1. 开机进入 Home 页面
2. 按 T + H（SELECT）进入 App Menu
3. 在列表中找到 "Hello POLA"
4. 按 T + H 打开
5. 屏幕显示 "Hello POLA"
6. 按 P + Y（BACK）返回

✅ 恭喜！你完成了第一个 POLA-OS 应用！

## 4. 应用生命周期详解

### 4.1 生命周期方法
方法   调用时机   用途
open(display)   应用被打开时   初始化状态、首次绘制
update(delta_ms)   每帧循环时   更新动画、计时器、状态
on_event(event)   收到输入事件时   处理按键/触摸
draw(display)   需要重绘时   绘制界面
close()   应用被关闭时   清理资源（可选）

### 4.2 调用顺序

用户打开应用
    → open(display)
    → draw(display)

主循环运行中
    → update(delta_ms)  ← 每帧调用
    → 如有变化 → draw(display)

用户按返回键
    → on_event(event)  ← 返回 BACK
    → close()
    → 系统弹出页面栈

### 4.3 注意事项

- open() 只在应用首次打开时调用一次
- update() 每帧都会调用，不要在其中做耗时操作
- draw() 只在内容变化时调用（脏渲染机制）
- 如果应用需要定时刷新，在 update() 中设置标志，触发 draw()

## 5. 事件处理机制

### 5.1 事件类型速查
触摸操作   事件类型   常量   作用
P + Y 同时触摸   返回   BACK   返回上一页
T + H 同时触摸   确认   SELECT   确认/进入
O 触摸   上一项   NAV_PREVIOUS   列表上移
N 触摸   下一项   NAV_NEXT   列表下移

### 5.2 事件导入

from core.event import BACK, SELECT, NAV_PREVIOUS, NAV_NEXT

### 5.3 事件处理示例

def on_event(self, event):
    if event.type == BACK:
        return BACK  # 返回上一页

    elif event.type == SELECT:
        # 处理确认操作
        self.selected = True
        self.dirty = True  # 标记需要重绘
        return None

    elif event.type == NAV_NEXT:
        # 列表下移
        self.index = min(self.index + 1, len(self.items) - 1)
        self.dirty = True
        return None

    elif event.type == NAV_PREVIOUS:
        # 列表上移
        self.index = max(self.index - 1, 0)
        self.dirty = True
        return None

    return None

### 5.4 事件返回值含义
返回值   含义
None   事件已处理，不传递给系统
BACK   请求返回上一页
其他值   视具体实现而定

## 6. UI 组件使用指南

POLA-OS 提供了开箱即用的 UI 组件，位于 ui/ 目录。

### 6.1 基础绘制 API

所有绘制操作通过 display 对象完成：

清屏：display.clear()
绘制文字（x, y 为左上角坐标）：display.text("Hello", 0, 0)
绘制矩形：display.rect(x, y, w, h, color)
填充矩形：display.fill_rect(x, y, w, h, color)
绘制像素点：display.pixel(x, y, color)
刷新屏幕（脏渲染模式下自动调用）：display.show()

### 6.2 Label 标签

from ui.label import Label

# 创建标签
title = Label("设置", x=0, y=0, font_size=16)

# 绘制
title.draw(display)

### 6.3 Button 按钮

from ui.button import Button

btn = Button("确定", x=10, y=40, w=60, h=20)
btn.draw(display)

# 检测选中状态
if btn.is_selected:
    btn.draw(display, selected=True)

### 6.4 ListView 列表

from ui.list_view import ListView

items = ["秒表", "计时器", "设置"]
lv = ListView(items, x=0, y=16, w=128, h=48)

# 设置选中项
lv.set_selected(index)

# 绘制
lv.draw(display)

### 6.5 Menu 菜单

from ui.menu import Menu

menu = Menu([
    ("亮度", lambda: self.adjust_brightness()),
    ("声音", lambda: self.adjust_sound()),
    ("关于", lambda: self.show_about()),
])
menu.draw(display)

### 6.6 Dialog 对话框

from ui.dialog import Dialog

dlg = Dialog("提示", "确定要退出吗？")
dlg.draw(display)

### 6.7 Selector 选择器

from ui.selector import Selector

sel = Selector(["关闭", "低", "中", "高"], default=2)
sel.draw(display)

### 6.8 屏幕尺寸参考

mPython 掌控板 OLED 屏幕尺寸：128 × 64 像素
区域   建议范围   用途
标题栏   y: 0~15   显示应用名称
内容区   y: 16~63   显示主要内容
底部提示   y: 56~63   显示操作提示

## 7. 页面导航与返回

### 7.1 页面栈原理

POLA-OS 使用页面栈管理多页面：

[Home] → [AppMenu] → [Stopwatch]
   ↑         ↑           ↑
 栈底      中间        栈顶（当前页面）

- 打开新页面：压入栈顶
- 按 BACK：弹出栈顶，回到上一页
- 栈深度默认限制：8 层

### 7.2 从应用内返回

在 on_event() 中返回 BACK 即可：

def on_event(self, event):
    if event.type == BACK:
        return BACK
    return None

### 7.3 打开新页面（高级）

如果需要在应用内打开子页面，可通过系统导航接口：

# 具体 API 视版本而定，通常通过 Navigation 服务
from services.navigation import Navigation

Navigation.push(NewPage)

⚠️ 注意：页面栈深度有限，避免无限嵌套。

## 8. 配置管理

### 8.1 配置文件位置

系统配置保存在 data/config.json：

{
    "brightness": 80,
    "volume": 50,
    "theme": "default",
    "sleep_timeout": 60
}

### 8.2 读取配置

from services.config import ConfigService

config = ConfigService()
brightness = config.get("brightness", default=100)

### 8.3 保存配置

config.set("brightness", 80)
config.save()  # 写入文件

### 8.4 注意事项

- 配置文件读写会占用 Flash 寿命，不要频繁写入
- 建议在用户确认修改后再调用 save()
- 配置项尽量使用简单类型（int / str / bool）

## 9. 插件开发指南

### 9.1 插件目录结构

插件放在 plugins/ 目录下，每个插件一个文件夹：

plugins/
└── my_plugin/
    ├── manifest.py    ← 插件描述
    └── app.py         ← 插件应用代码

### 9.2 manifest.py 模板

# plugins/my_plugin/manifest.py

PLUGIN_NAME = "我的插件"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "你的名字"
PLUGIN_DESCRIPTION = "插件功能描述"
PLUGIN_ENTRY = "app.MyPluginApp"  # 入口类

### 9.3 app.py 模板

# plugins/my_plugin/app.py
from core.app import App
from core.event import BACK

class MyPluginApp(App):
    name = "我的插件"

    def open(self, display):
        self.display = display
        self.draw(display)

    def update(self, delta_ms):
        pass

    def on_event(self, event):
        if event.type == BACK:
            return BACK
        return None

    def draw(self, display):
        display.clear()
        display.text("My Plugin", 16, 24)
        display.show()

### 9.4 插件加载机制

系统启动时会自动扫描 plugins/ 目录：

1. 读取每个子目录的 manifest.py
2. 根据 PLUGIN_ENTRY 加载入口类
3. 注册到应用菜单

### 9.5 插件开发注意事项

- 插件不能修改系统核心文件
- 插件应尽量节省内存
- 插件命名避免与内置应用冲突
- 建议在 manifest.py 中声明依赖

## 10. 调试与错误处理

### 10.1 常见错误及解决方案
错误现象   可能原因   解决方案
开机黑屏   devlib.py 缺失   上传 devlib.py 到根目录
OLED 显示偏移   主题常量不匹配   调整 ui/theme.py 中的 Y 坐标
触摸无响应   阈值不合适   调整 drivers/input.py 中的阈值
内存不足 (MemoryError)   页面栈过深或大对象   减少页面嵌套，手动调用 gc.collect()
应用不显示   未注册到 registry   检查 apps/registry.py
配置不保存   config.json 路径错误   确认 data/config.json 存在

### 10.2 调试技巧

技巧一：屏幕调试输出

def draw(self, display):
    display.clear()
    display.text(f"state={self.state}", 0, 0)
    display.text(f"index={self.index}", 0, 12)
    display.show()

技巧二：内存检查

import gc
display.text(f"free={gc.mem_free()}", 0, 50)

技巧三：事件日志

def on_event(self, event):
    print(f"[MyApp] event: {event.type}")
    # ...

⚠️ 注意：print() 会输出到串口，需通过软件内串口监视器查看。

### 10.3 系统错误对话框

POLA-OS 内置了错误捕获机制。当应用崩溃时，系统会：

1. 捕获异常
2. 显示错误对话框（异常类型 + 摘要）
3. 等待用户按 BACK 返回主页

开发者无需自行处理未捕获异常。

## 11. 性能优化建议

### 11.1 内存优化

掌控板 RAM 极其有限，务必注意：

# ✅ 好：使用局部变量
def draw(self, display):
    text = self.title  # 局部引用
    display.text(text, 0, 0)

# ❌ 坏：创建大列表
big_list = [i for i in range(1000)]  # 不要这样做！

### 11.2 渲染优化

# ✅ 好：只在变化时重绘
def update(self, delta_ms):
    if self.changed:
        self.draw(self.display)
        self.changed = False

# ❌ 坏：每帧都重绘
def update(self, delta_ms):
    self.draw(self.display)  # 浪费资源！

### 11.3 动画优化

# ✅ 好：控制帧率
def update(self, delta_ms):
    self.frame_timer += delta_ms
    if self.frame_timer >= 100:  # 每 100ms 更新一次
        self.frame_timer = 0
        self.animate()
        self.dirty = True

### 11.4 关闭动画（提升响应速度）

在 core/boot.py 中：

transition_ms = 0  # 关闭页面过渡动画

## 12. 发布与部署

### 12.1 开发完成检查清单

在发布你的应用/插件前，请确认：

- [ ] 应用能正常打开和关闭
- [ ] 所有触摸事件响应正确
- [ ] 返回键能正常返回
- [ ] 界面在 128×64 屏幕上显示正常
- [ ] 无内存泄漏（长时间运行不崩溃）
- [ ] 配置文件读写正常
- [ ] 代码有基本注释

### 12.2 文件上传清单

开发完成后，只需上传修改过的文件：

apps/your_app.py       ← 你的应用代码
apps/registry.py       ← 更新后的注册表
plugins/your_plugin/   ← 插件目录（如有）

### 12.3 分享你的作品

推荐分享方式：

1. GitHub 仓库：fork POLA-OS，添加你的应用，提交 PR
2. 插件包：将 plugins/your_plugin/ 打包分享
3. 教学案例：编写使用说明，适合课堂分享

## 13. 附录：API 速查表

### 13.1 App 基类方法
方法   必须实现   说明
open(display)   ✅   应用打开时调用
update(delta_ms)   ✅   每帧更新
on_event(event)   ✅   事件处理
draw(display)   ✅   界面绘制
close()   ❌   应用关闭时调用

### 13.2 事件常量

from core.event import BACK, SELECT, NAV_PREVIOUS, NAV_NEXT

### 13.3 Display API

display.clear()
display.text(str, x, y)
display.rect(x, y, w, h, color)
display.fill_rect(x, y, w, h, color)
display.pixel(x, y, color)
display.show()

### 13.4 屏幕常量

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

### 13.5 配置服务

from services.config import ConfigService
config = ConfigService()
config.get(key, default=None)
config.set(key, value)
config.save()

### 13.6 内存管理

import gc
gc.collect()       # 手动垃圾回收
gc.mem_free()      # 查看剩余内存
gc.mem_alloc()     # 查看已分配内存

快速参考卡片

┌─────────────────────────────────────────────────┐
│              POLA-OS 应用开发速查                │
├─────────────────────────────────────────────────┤
│  屏幕尺寸：128 × 64 像素                        │
│  触摸返回：P + Y                                │
│  触摸确认：T + H                                │
│  上一项：O                                      │
│  下一项：N                                      │
├─────────────────────────────────────────────────┤
│  应用文件：apps/your_app.py                     │
│  注册位置：apps/registry.py                     │
│  插件目录：plugins/your_plugin/                 │
│  配置文件：data/config.json                     │
├─────────────────────────────────────────────────┤
│  必须实现：open / update / on_event / draw      │
│  返回上页：return BACK                          │
│  标记重绘：self.dirty = True                    │
│  内存回收：gc.collect()                         │
└─────────────────────────────────────────────────┘

📝 本手册基于 POLA-OS Takla_rc2_beta 分支编写。  
如有 API 变更，请以项目源码为准。  
欢迎提交 Issue 或 PR 完善本手册。