from typing import Any, Optional

from django.contrib.auth import get_user_model, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView

from solomon.conf import settings
from solomon.forms import LoginForm
from solomon.models import SolomonToken

User = get_user_model()


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(never_cache, name="dispatch")
class LoginView(FormView):
    template_name = settings.SOLOMON_LOGIN_TEMPLATE
    form_class = LoginForm

    def form_valid(self, form):
        logout(self.request)
        email = form.cleaned_data["email"]
        redirect_url = form.cleaned_data["redirect_url"]

        solomon_token = SolomonToken.objects.create_from_email(
            email,
            redirect_url=redirect_url,
            ip_address=self.get_ip_address(),
        )
        solomon_token.send_email(self.request)

        return render(self.request, settings.SOLOMON_LOGIN_DONE_TEMPLATE)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["initial"]["redirect_url"] = self.get_token_redirect_url()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        redirect_to = self.request.GET.get("next")

        if not redirect_to:
            return settings.LOGIN_REDIRECT_URL

        allowed_hosts = settings.ALLOWED_HOSTS
        if "*" in allowed_hosts:
            allowed_hosts = [self.request.get_host()]

        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=allowed_hosts,
            require_https=self.request.is_secure(),
        )

        return redirect_to if url_is_safe else settings.LOGIN_REDIRECT_URL

    def get_ip_address(self) -> str:
        """
        Returns the IP address of the request.

        Returns:
            str: The IP address of the request.
        """
        ip_address = self.request.headers.get("x-forwarded-for", "")
        if ip_address:
            return ip_address.split(",")[-1].strip()

        return self.request.META.get("REMOTE_ADDR", "")


def verify_view(request: HttpRequest, jwt_token: str) -> HttpResponse:  # noqa: ARG001
    return render(request, settings.SOLOMON_VERIFY_TEMPLATE_NAME)


def logout_view(request: HttpRequest) -> HttpResponse:
    return render(request, settings.SOLOMON_LOGOUT_TEMPLATE_NAME)
