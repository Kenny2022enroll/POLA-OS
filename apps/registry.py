from apps.timer import Timer
from apps.settings import Settings
from apps.stopwatch import Stopwatch

def load_apps():
    return [
        Timer(),
        Stopwatch(),
        Settings()
    ]