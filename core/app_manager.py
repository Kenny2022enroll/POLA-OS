class AppInfo:
    def __init__(self, app_class, name=None, version="0.1", icon=None,
                 module_path=None):
        self.app_class = app_class
        self.name = name or getattr(app_class, "name", app_class.__name__)
        self.version = version
        self.icon = icon
        # When app_class is None the class is imported from module_path
        # on first launch, keeping unused apps out of RAM.
        self.module_path = module_path

class AppManager:
    def __init__(self):
        self.apps = []

    def load(self, entries):
        for entry in entries:
            if isinstance(entry, tuple) and len(entry) == 2:
                self.register_plugin(entry[0], entry[1])
            else:
                self.register(entry)

    def register(self, app_class, name=None, version="0.1", icon=None,
                 module_path=None):
        if isinstance(app_class, AppInfo):
            self.apps.append(app_class)
        else:
            self.apps.append(AppInfo(app_class, name, version, icon,
                                     module_path))

    def register_plugin(self, info, app):
        # ``app`` is either a class (eager plugin) or a module path
        # string resolved lazily on first launch.
        if isinstance(app, str):
            self.register(None, info.get("name"),
                          info.get("version", "0.1"), info.get("icon"), app)
        else:
            self.register(app, info.get("name"),
                          info.get("version", "0.1"), info.get("icon"))

    def get_apps(self):
        return self.apps

    def _resolve(self, info):
        app_class = info.app_class
        if app_class is None:
            module = __import__(info.module_path, None, None, ["APP_CLASS"])
            app_class = module.APP_CLASS
            info.app_class = app_class
        return app_class

    def create(self, index, context=None):
        info = self.apps[index]
        app = self._resolve(info)()
        app.context = context
        # Remember the registry entry so App can unload the module on exit.
        app.app_info = info
        return app
