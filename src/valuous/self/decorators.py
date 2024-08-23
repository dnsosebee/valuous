

import logging
from functools import wraps


def trace(goal: str = "unknown"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            info = {"module": func.__module__, "qualified_name": func.__qualname__,
                    "goal": goal, "args": args, "kwargs": kwargs, "result": result}
            logging.info(f"Trace: {info}")
            return result
        return wrapper
    return decorator
