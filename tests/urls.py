from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import include, path


@login_required
def protected(request):
    return HttpResponse()


def unprotected(request):
    return HttpResponse()


urlpatterns = [
    path("auth/", include("solomon.urls")),
    path("unprotected-route/", unprotected, name="unprotected"),
    path("protected-route/", protected, name="protected"),
]
