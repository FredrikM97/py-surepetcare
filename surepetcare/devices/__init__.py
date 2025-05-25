import importlib


def load_device_class(product_id_enum):
    # Build the absolute module path
    module_name = f"surepetcare.devices.{product_id_enum.name.lower()}"
    class_name = "".join(word.capitalize() for word in product_id_enum.name.lower().split("_"))
    module = importlib.import_module(module_name)
    device_class = getattr(module, class_name)
    return device_class
