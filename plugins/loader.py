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
            module = __import__("plugins.%s.app" % name,
                                None, None, ["APP_CLASS"])
            result.append((manifest.PLUGIN, module.APP_CLASS))
        except Exception:
            # Optional plugin errors must not block system startup.
            continue
    return result