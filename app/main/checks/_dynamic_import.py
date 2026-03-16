import pkgutil
import importlib
import inspect
from pathlib import Path


def setup_dynamic_import(module_globals, base_class, current_file, exclude_startswith='_'):
    package_path = Path(current_file).parent
    package_name = module_globals['__name__']
    class_to_module = {}
    class_cache = {}

    for (_, module_name, _) in pkgutil.iter_modules([str(package_path)]):
        if module_name.startswith(exclude_startswith):
            continue

        module = importlib.import_module(f'.{module_name}', package=package_name)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__ and issubclass(obj, base_class):
                class_to_module[name] = module_name

    def __getattr__(name):
        if name in class_cache:
            return class_cache[name]
        if name in class_to_module:
            mod_name = class_to_module[name]
            module = importlib.import_module(f'.{mod_name}', package=package_name)
            cls = getattr(module, name)
            class_cache[name] = cls
            return cls
        raise AttributeError(f"Module {package_name!r} has no attribute {name!r}")

    def __dir__():
        return list(class_to_module.keys()) + list(module_globals.keys())

    module_globals['__getattr__'] = __getattr__
    module_globals['__dir__'] = __dir__

    return list(class_to_module.keys())
