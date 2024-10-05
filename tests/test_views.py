from pytest_django.asserts import assertTemplateUsed

from solomon.conf import settings
from solomon.forms import LoginForm
from solomon.models import SolomonToken
from solomon.views import get_token_redirect_url


def test_get_login_page(client, login_view_url):
    response = client.get(login_view_url)
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE)


def test_post_login_page_with_empty_form_data(client, login_view_url):
    response = client.post(login_view_url, {})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)
    assert "email" in response.context["form"].errors
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE)


def test_post_login_page_with_invalid_form_data(client, login_view_url, faker):
    response = client.post(login_view_url, {"email": faker.pystr()})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)
    assert "email" in response.context["form"].errors
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE)


def test_post_login_page_with_inactive_user(client, login_view_url, inactive_user):
    response = client.post(login_view_url, {"email": inactive_user.email})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)
    assert "email" in response.context["form"].errors
    assert "This user has been deactivated." in response.context["form"].errors["email"]
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE)


def test_post_login_page_with_active_user(client, login_view_url, active_user, faker, settings):
    settings.SOLOMON_REQUIRE_SAME_BROWSER = True
    response = client.post(
        login_view_url,
        {
            "email": active_user.email,
            "ip_address": faker.ipv4(),
            "redirect_url": "/" + faker.uri_path(deep=3),
        },
    )
    assert response.status_code == 200
    assert response.cookies.get(settings.SOLOMON_COOKIE_NAME) is not None
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_DONE_TEMPLATE)
    assert SolomonToken.objects.count() == 1


def test_post_login_page_with_active_user_same_browser_not_required(
    client, login_view_url, active_user, faker, settings
):
    settings.SOLOMON_REQUIRE_SAME_BROWSER = False
    response = client.post(
        login_view_url,
        {
            "email": active_user.email,
            "ip_address": faker.ipv4(),
            "redirect_url": "/" + faker.uri_path(deep=3),
        },
    )
    assert response.status_code == 200
    assert response.cookies.get(settings.SOLOMON_COOKIE_NAME) is None
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_DONE_TEMPLATE)
    assert SolomonToken.objects.count() == 1


def test_get_token_redirect_url_without_redirect_url(rf, token):
    request = rf.post(token.redirect_url)
    assert get_token_redirect_url(request) == settings.LOGIN_REDIRECT_URL


def test_get_token_redirect_url_with_redirect_url(rf, token):
    request = rf.post(token.redirect_url, {"redirect_url": "/dashboard/"})
    assert get_token_redirect_url(request) == "/dashboard/"


def test_get_token_redirect_url_with_empty_redirect_url(rf, token):
    request = rf.post(token.redirect_url, {"redirect_url": ""})
    assert get_token_redirect_url(request) == settings.LOGIN_REDIRECT_URL


def test_get_token_redirect_url_with_changed_allowed_hosts(rf, token, settings):
    settings.ALLOWED_HOSTS = ["example.com"]
    request = rf.post(token.redirect_url, {"redirect_url": "http://example.com/dashboard/"})
    assert get_token_redirect_url(request) == "http://example.com/dashboard/"


def test_post_verify_page_with_valid_token(settings, rf, client, token, faker):
    settings.SOLOMON_REQUIRE_SAME_IP = False
    settings.SOLOMON_REQUIRE_SAME_BROWSER = False
    request = rf.get("/")
    response = client.get(token.get_verify_url(request))
    assert response.status_code == 302
    assert response.url == token.redirect_url


def test_post_verify_page_with_invalid_token(settings, rf, client, invalid_token, faker):
    settings.SOLOMON_REQUIRE_SAME_IP = False
    settings.SOLOMON_REQUIRE_SAME_BROWSER = False
    request = rf.get("/")
    response = client.get(invalid_token.get_verify_url(request))
    assert response.status_code == 200
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_FAILED_TEMPLATE)
