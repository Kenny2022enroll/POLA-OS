import sys

from core.page import Page

class App(Page):
    """Application page loaded by the application manager."""

    name = "APP"

    def update(self, delta_ms=0):
        pass

    def on_leave(self):
        self.close()
        # Unload the module this app was launched from so its bytecode
        # becomes collectable; AppManager re-imports it on the next
        # launch. The kernel force-collects after the exit transition.
        info = getattr(self, "app_info", None)
        if info is not None and info.module_path:
            try:
                del sys.modules[info.module_path]
            except KeyError:
                pass
            # Importing a.b.c binds c on package a.b; clear that too or
            # the module stays reachable through its parent.
            dot = info.module_path.rfind(".")
            if dot > 0:
                parent = sys.modules.get(info.module_path[:dot])
                if parent is not None:
                    leaf = info.module_path[dot + 1:]
                    try:
                        delattr(parent, leaf)
                    except AttributeError:
                        setattr(parent, leaf, None)
            info.app_class = None
