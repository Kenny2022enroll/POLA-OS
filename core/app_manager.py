class AppInfo:
    def __init__(self, app_class, name=None, version="0.1", icon=None):
        self.app_class = app_class
        self.name = name or getattr(app_class, "name", app_class.__name__)
        self.version = version
        self.icon = icon

class AppManager:
    def __init__(self):
        self.apps = []

    def load(self, entries):
        for entry in entries:
            if isinstance(entry, tuple) and len(entry) == 2:
                self.register_plugin(entry[0], entry[1])
            else:
                self.register(entry)

    def register(self, app_class, name=None, version="0.1", icon=None):
        if isinstance(app_class, AppInfo):
            self.apps.append(app_class)
        else:
            self.apps.append(AppInfo(app_class, name, version, icon))

    def register_plugin(self, info, app_class):
        self.register(app_class, info.get("name"),
                      info.get("version", "0.1"), info.get("icon"))

    def get_apps(self):
        return self.apps

    def create(self, index, context=None):
        info = self.apps[index]
        app = info.app_class()
        app.context = context
        return app