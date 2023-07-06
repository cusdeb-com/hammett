from importlib import import_module


def import_string(dotted_path):
    """Imports a dotted module path and returns the attribute/class
    designated by the last name in the path.
    Raises `ImportError` if the import failed.
    """

    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        msg = f"{dotted_path} doesn't look like a module path"
        raise ImportError(msg) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        msg = f'Module "{module_path}" does not define a "{class_name}" attribute/class'
        raise ImportError(msg) from err
