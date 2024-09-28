from typing import Optional

from django.contrib.auth import get_user_model, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView

from solomon.conf import settings
from solomon.forms import (
    LoginForm,
    SignupForm,
    SignupFormWithName,
)
from solomon.models import SolomonToken
from solomon.utils import get_or_create_user

User = get_user_model()


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(never_cache, name="dispatch")
class LoginView(FormView):
    template_name = settings.SOLOMON_LOGIN_TEMPLATE_NAME
    form_class = LoginForm

    def form_valid(self, form):
        logout(self.request)
        email = form.cleaned_data["email"]

        if not settings.SOLOMON_SIGNUP_REQUIRED:
            # No explicit signup required, create user with the provided email if not exists.
            get_or_create_user(email)

        solomon_token = SolomonToken.objects.create_from_email(
            email,
            redirect_url=self.get_token_redirect_url(),
        )
        solomon_token.send_email(self.request)

        return render(self.request, settings.SOLOMON_LOGIN_DONE_TEMPLATE_NAME)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["signup_required"] = settings.SOLOMON_SIGNUP_REQUIRED
        return context

    def get_token_redirect_url(self) -> Optional[str]:
        """
        Determines a safe redirect URL from the request.

        This method checks the 'next' parameter in both POST and GET requests to
        determine the URL to redirect to. It ensures that the URL is safe by
        verifying it against the allowed hosts specified in the settings.

        Returns:
            Optional[str]: The safe redirect URL if it is valid and allowed, otherwise None.
        """
        redirect_to = self.request.POST.get("next", self.request.GET.get("next"))

        if not redirect_to:
            return None

        allowed_hosts = settings.ALLOWED_HOSTS
        if "*" in allowed_hosts:
            allowed_hosts = [self.request.get_host()]

        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=allowed_hosts,
            require_https=self.request.is_secure(),
        )

        return redirect_to if url_is_safe else None


def verify_view(request: HttpRequest, jwt_token: str) -> HttpResponse:  # noqa: ARG001
    return render(request, settings.SOLOMON_VERIFY_TEMPLATE_NAME)


def logout_view(request: HttpRequest) -> HttpResponse:
    return render(request, settings.SOLOMON_LOGOUT_TEMPLATE_NAME)


@csrf_protect
def signup_view(request: HttpRequest) -> HttpResponse:
    # determine the form class based on the signup requirements
    form_class = SignupFormWithName if settings.SOLOMON_SIGNUP_REQUIRE_NAME else SignupForm

    # process request
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            return render(request, settings.SOLOMON_SIGNUP_DONE_TEMPLATE_NAME)
    else:
        form = form_class()

    return render(request, settings.SOLOMON_SIGNUP_TEMPLATE_NAME, {"form": form})
