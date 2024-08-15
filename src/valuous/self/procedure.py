import functools


def procedure(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # TODO this might wanna trace beforehand
        print("got trace", func.__name__, func.__module__, args, kwargs, result)
        return result
    return wrapper
