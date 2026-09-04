import os

def load_plugins():
    result = []
    try:
        names = os.listdir("plugins")
    except Exception:
        return result

    for name in names:
        if name.startswith("_") or name == "loader.py":
            continue
        try:
            manifest = __import__("plugins.%s.manifest" % name,
                                  None, None, ["PLUGIN"])
            # The app module is imported lazily on first launch (see
            # AppManager) so unused plugins stay out of RAM. A broken
            # plugin cannot block startup; Home silently ignores a
            # launch that fails to import.
            result.append((manifest.PLUGIN, "plugins.%s.app" % name))
        except Exception:
            # Optional plugin errors must not block system startup.
            continue
    return result
