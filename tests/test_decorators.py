import django
import pytest


@pytest.mark.skipif(django.VERSION >= (5, 1), reason="login_not_required decorator is available in Django >= 5.1")
def test_login_not_required_decorator_django_less_then_5_0():
    from solomon.decorators import login_not_required

    def view(request):
        return "view"

    decorated_view = login_not_required(view)
    assert not hasattr(decorated_view, "login_required")


@pytest.mark.skipif(django.VERSION < (5, 1), reason="login_not_required decorator is not available in Django < 5.1")
def test_login_not_required_decorator_django_5_1():
    from solomon.decorators import login_not_required

    def view(request):
        return "view"

    decorated_view = login_not_required(view)
    assert hasattr(decorated_view, "login_required")
    assert decorated_view.login_required is False
