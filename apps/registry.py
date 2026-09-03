"""Built-in application registry.

Every built-in app module exposes a ``MANIFEST`` dict and an
``APP_CLASS``. The manifest carries the display name, version and the
app's icon builder, so icons live with their apps instead of inside the
system framework.
"""
from apps import filemanager
from apps import settings
from apps import stopwatch
from apps import timer

_MODULES = (timer, stopwatch, filemanager, settings)


def load_apps():
    return [(module.MANIFEST, module.APP_CLASS) for module in _MODULES]
