from apps.timer import Timer
from apps.settings import Settings

def load_apps():
    apps = []
    apps.append(
        Timer()
    )
    apps.append(
        Settings()
    )
    return apps