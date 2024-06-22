from data_gathering.models.task_base import Task

import importlib

module_path = "data_gathering.data.historical.historical_task.HistoricalDataTask"


def get_class(module_path):
    parts = module_path.strip(".").split(".")

    module_name = parts[-1]
    package_path = ".".join(parts[:-1])

    try:
        module = importlib.import_module(package_path)
        return getattr(module, module_name)
    except ModuleNotFoundError as e:
        raise ImportError(f"Module not found: {package_path}") from e


_class = get_class(module_path)
print(dir(_class))
