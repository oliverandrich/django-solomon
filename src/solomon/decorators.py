import django


def login_not_required(view):
    """
    Wrapper for the login_not_required decorator introduced in Django 5.1.
    If the decorator is not available, it returns the view unchanged.

    Args:
        view (View): The view to be decorated.

    Returns:
        View: The decorated view if the decorator is available, otherwise the original view.
    """
    if django.VERSION >= (5, 1):  # pragma: no cover
        from django.contrib.auth.decorators import login_not_required as decorator  # type: ignore

        return decorator(view)
    return view
