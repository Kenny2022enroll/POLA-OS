class AppManager:
    def __init__(self):
        self.apps = []

    def load(
        self,
        apps
    ):
        self.apps = apps

    def register(
        self,
        app
    ):
        self.apps.append(app)

    def get_apps(self):
        return self.apps

    def get(
        self,
        name
    ):
        for app in self.apps:
            if app.name == name:
                return app
        return None