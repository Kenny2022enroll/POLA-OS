from apps.timer import Timer
from apps.settings import Settings

def load_apps():
    return [
        Timer(),
        Settings()
    ]