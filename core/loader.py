import importlib
import pkgutil

import modules


def load_modules():
    for module_info in pkgutil.iter_modules(modules.__path__):
        importlib.import_module(f"modules.{module_info.name}")
