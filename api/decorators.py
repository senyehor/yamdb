from rest_framework.exceptions import MethodNotAllowed


def allowed_http_methods(allowed_methods=None):
    if not allowed_methods:
        allowed_methods = []

    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal allowed_methods
            request = args[1] if not kwargs.get('request', None) else kwargs.get('request')
            if request.method.lower() not in allowed_methods:
                raise MethodNotAllowed(method=request.method.lower())
            return func(*args, **kwargs)

        return wrapper

    return decorator
