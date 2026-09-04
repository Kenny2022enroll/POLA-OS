"""Built-in application registry.

Every built-in app is registered here as a lightweight spec: display
name, version, icon builder and the module path that carries the
``APP_CLASS``. The app module itself is only imported when the app is
actually launched (see ``AppManager.create``), so unused apps do not
occupy RAM on the embedded target. Icon builders therefore live here
instead of inside the app modules.
"""


def _timer_icon(canvas):
    canvas.circle(12, 12, 9)
    canvas.vline(12, 3, 2)
    canvas.vline(12, 19, 2)
    canvas.hline(3, 12, 2)
    canvas.hline(19, 12, 2)
    canvas.line(12, 12, 12, 6)
    canvas.line(12, 12, 16, 12)
    canvas.pixel(12, 12)


def _stopwatch_icon(canvas):
    canvas.circle(12, 13, 8)
    canvas.vline(11, 3, 2)
    canvas.vline(12, 3, 2)
    canvas.hline(9, 2, 6)
    canvas.line(18, 6, 20, 4)
    canvas.line(12, 13, 15, 9)
    canvas.pixel(12, 13)


def _files_icon(canvas):
    canvas.rect(3, 5, 9, 5)
    canvas.rect(3, 9, 18, 10)


def _settings_icon(canvas):
    canvas.fill_circle(12, 12, 7)
    canvas.clear_circle(12, 12, 3)
    for dx, dy in ((8, 0), (6, 6), (0, 8), (-6, 6),
                   (-8, 0), (-6, -6), (0, -8), (6, -6)):
        cx = 12 + dx
        cy = 12 + dy
        for ty in range(cy - 1, cy + 2):
            for tx in range(cx - 1, cx + 2):
                canvas.pixel(tx, ty)


_APPS = (
    ("Timer", "0.2", _timer_icon, "apps.timer"),
    ("Stopwatch", "0.2", _stopwatch_icon, "apps.stopwatch"),
    ("Files", "0.1", _files_icon, "apps.filemanager"),
    ("Settings", "0.2", _settings_icon, "apps.settings"),
)


def load_apps():
    return [({"name": name, "version": version, "icon": icon}, module)
            for name, version, icon, module in _APPS]
