class AppInfo:
    def __init__(self, app_class, name=None, version="0.1"):
        self.app_class = app_class
        self.name = name or getattr(app_class, "name", app_class.__name__)
        self.version = version

class AppManager:
    def __init__(self):
        self.apps = []

    def load(self, apps):
        for app in apps:
            self.register(app)

    def register(self, app_class, name=None, version="0.1"):
        if isinstance(app_class, AppInfo):
            self.apps.append(app_class)
        else:
            self.apps.append(AppInfo(app_class, name, version))

    def register_plugin(self, info, app_class):
        self.register(app_class, info.get("name"), info.get("version", "0.1"))

    def get_apps(self):
        return self.apps

    def create(self, index, context=None):
        info = self.apps[index]
        app = info.app_class()
        app.context = context
        return app