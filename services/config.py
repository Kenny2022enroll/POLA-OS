try:
    import ujson as json
except ImportError:
    import json
import os

DEFAULTS = {
    # Brightness is automatic (light sensor) and the desktop is always
    # Cover Flow, so neither appears here anymore.
    "sleep_timeout": 60,
    "sound_enabled": True,
}

class ConfigService:
    def __init__(self, path="data/config.json"):
        self.path = path
        self.values = dict(DEFAULTS)
        self.load()

    def _ensure_parent(self):
        parent = self.path.rsplit("/", 1)[0] if "/" in self.path else ""
        if parent:
            try:
                os.stat(parent)
            except OSError:
                try:
                    os.mkdir(parent)
                except OSError:
                    pass

    def load(self):
        try:
            with open(self.path, "r") as stream:
                loaded = json.load(stream)
            for key in DEFAULTS:
                if key in loaded:
                    self.values[key] = loaded[key]
        except Exception:
            self.save()

    def get(self, key, default=None):
        return self.values[key] if key in self.values else default

    def set(self, key, value, save=True):
        self.values[key] = value
        if save:
            return self.save()
        return True

    def update(self, values):
        for key, value in values.items():
            self.values[key] = value
        return self.save()

    def save(self):
        try:
            self._ensure_parent()
            with open(self.path, "w") as stream:
                json.dump(self.values, stream)
            return True
        except Exception:
            return False