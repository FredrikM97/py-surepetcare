from abc import ABC
from abc import abstractmethod
from datetime import datetime
from functools import wraps


def data_exist_validation(method):
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "_data") or self._raw_data is None:
            raise Exception("Data not fetched yet. Call fetch() first.")
        return method(self, *args, **kwargs)

    return wrapper


def validate_date_fields(*field_names):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            formats = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z"]
            # Combine args and kwargs into a dict with parameter names
            import inspect

            bound_args = inspect.signature(func).bind(self, *args, **kwargs)
            bound_args.apply_defaults()
            arguments = bound_args.arguments

            for field in field_names:
                date_str = arguments.get(field)
                if date_str is not None:
                    if not any(_try_parse_date(date_str, fmt) for fmt in formats):
                        raise ValueError(f"Date '{date_str}' for '{field}' is not in a valid format.")
            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


def _try_parse_date(date_str, fmt):
    try:
        datetime.strptime(date_str, fmt)
        return True
    except Exception:
        return False


class AbstractHasGet(ABC):
    @abstractmethod
    async def get(self, endpoint: str, params: dict | None = None):
        pass
