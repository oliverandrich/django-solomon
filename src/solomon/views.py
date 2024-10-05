from typing import Optional

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from solomon.conf import settings
from solomon.decorators import login_not_required
from solomon.forms import LoginForm
from solomon.models import SolomonToken
from solomon.utils import get_ip_address

User = get_user_model()


@csrf_exempt
@never_cache
@login_not_required
def login_view(request: HttpRequest) -> HttpResponse:
    """
    Handles the login view for the application.

    This view processes both GET and POST requests. For POST requests, it validates
    the login form, logs out the current user, saves the token, sends an email with
    the token, and renders the login done template. If the setting SOLOMON_REQUIRE_SAME_BROWSER
    is enabled, it sets a cookie with the token value.

    For GET requests, it initializes the login form with the redirect URL and the
    anonymized IP address if the setting SOLOMON_ANONYMIZE_IP_ADDRESS is enabled.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object with the rendered template.
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            logout(request)

            token = form.save()
            token.send_email(request)

            response = render(request, settings.SOLOMON_LOGIN_DONE_TEMPLATE)
            if settings.SOLOMON_REQUIRE_SAME_BROWSER:
                response.set_cookie(settings.SOLOMON_COOKIE_NAME, token.cookie_value)
            return response
    else:
        ip_address = get_ip_address(request)
        form = LoginForm(
            initial={
                "redirect_url": get_token_redirect_url(request),
                "ip_address": ip_address,
            }
        )

    context = {"form": form}
    return render(request, settings.SOLOMON_LOGIN_TEMPLATE, context)


def get_token_redirect_url(request: HttpRequest) -> Optional[str]:
    """
    Determines a safe redirect URL from the request.

    This method checks the 'next' parameter in both POST and GET requests to
    determine the URL to redirect to. It ensures that the URL is safe by
    verifying it against the allowed hosts specified in the settings.

    Returns:
        Optional[str]: The safe redirect URL if it is valid and allowed, otherwise None.
    """

    if not (redirect_to := request.POST.get("redirect_url")):
        return settings.LOGIN_REDIRECT_URL

    allowed_hosts = settings.ALLOWED_HOSTS
    if "*" in allowed_hosts:
        allowed_hosts = [request.get_host()]

    url_is_safe = url_has_allowed_host_and_scheme(
        url=redirect_to,
        allowed_hosts=allowed_hosts,
        require_https=request.is_secure(),
    )

    return redirect_to if url_is_safe else settings.LOGIN_REDIRECT_URL


@csrf_exempt
@never_cache
@login_not_required
def verify_view(request: HttpRequest, pk: int, token_string: str) -> HttpResponse:
    """
    Handles the verification view for the application.

    This view validates the token based on the primary key and the token string.
    If the token is valid, it logs in the user and redirects to the token's redirect URL.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the token.
        token_string (str): The token string of the token.

    Returns:
        HttpResponse: The HTTP response object with the rendered template.
    """
    if not (user := authenticate(request, token_pk=pk, token_string=token_string)):
        return render(request, settings.SOLOMON_LOGIN_FAILED_TEMPLATE, {})

    login(request, user)

    token = SolomonToken.objects.get(pk=pk)
    return redirect(token.redirect_url)


def logout_view(request: HttpRequest) -> HttpResponse:
    return render(request, settings.SOLOMON_LOGOUT_TEMPLATE_NAME)
