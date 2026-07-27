class AppManager:
    def __init__(self):
        self.apps=[]

    def load(self,apps):
        self.apps=apps

    def get_apps(self):
        return self.apps