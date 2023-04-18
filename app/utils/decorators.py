def decorator_assertion(decorator, condition):
    if not condition:
        def inner(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return inner
    return decorator
