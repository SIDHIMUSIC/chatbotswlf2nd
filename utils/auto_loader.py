import importlib
import os
import pkgutil
import traceback


def _load_pkg(app, package, folder, priority=None):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), folder)
    loaded = []
    priority = priority or []
    for name in priority:
        try:
            module = importlib.import_module(f"{package}.{name}")
            if hasattr(module, "register"):
                module.register(app)
                loaded.append(name)
                print(f"OK {folder}/{name}")
        except ModuleNotFoundError:
            pass
        except Exception as e:
            print(f"FAIL {folder}/{name}: {e}")
            traceback.print_exc()
    for _, name, _ in pkgutil.iter_modules([path]):
        if name.startswith("_") or name in loaded:
            continue
        try:
            module = importlib.import_module(f"{package}.{name}")
            if hasattr(module, "register"):
                module.register(app)
                loaded.append(name)
                print(f"OK {folder}/{name}")
        except Exception as e:
            print(f"FAIL {folder}/{name}: {e}")
            traceback.print_exc()
    print(f"Loaded {len(loaded)} from {folder}")
    return loaded


def load_tools(app):
    return _load_pkg(app, "tools", "tools")


def load_modules(app):
    return _load_pkg(
        app,
        "modules",
        "modules",
        priority=["start", "help", "chat", "image", "models", "owner", "clone"],
    )
