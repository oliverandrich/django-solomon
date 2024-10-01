import pytest
from pytest_django.asserts import assertTemplateUsed

from solomon.conf import settings
from solomon.forms import LoginForm


@pytest.mark.django_db
def test_login_get_page(client, login_view_url):
    response = client.get(login_view_url)
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE_NAME)


@pytest.mark.django_db
def test_login_with_empty_formdata(client, login_view_url, faker):
    response = client.post(login_view_url, {})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)
    assert "email" in response.context["form"].errors
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE_NAME)


@pytest.mark.django_db
def test_login_with_invalid_formdata(client, login_view_url, faker):
    response = client.post(login_view_url, {"email": faker.pystr()})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)
    assert "email" in response.context["form"].errors
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE_NAME)


@pytest.mark.django_db
def test_login_with_an_inactive_user(client, login_view_url, inactive_user):
    response = client.post(login_view_url, {"email": inactive_user.email})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)
    assert "email" in response.context["form"].errors
    assert "This user has been deactivated." in response.context["form"].errors["email"]
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE_NAME)


@pytest.mark.django_db
def test_login_with_a_nonexisting_email_when_signup_is_required(
    client, login_view_url, faker, settings
):
    settings.SOLOMON_SIGNUP_REQUIRED = True
    response = client.post(login_view_url, {"email": faker.email()})
    assert response.status_code == 200
    assert "form" in response.context
    assert "email" in response.context["form"].errors
    assert (
        "We could not find a user with that email address."
        in response.context["form"].errors["email"]
    )
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_TEMPLATE_NAME)


@pytest.mark.django_db
def test_login_with_a_nonexisting_email_when_signup_is_not_required(
    client, login_view_url, faker, settings
):
    settings.SOLOMON_SIGNUP_REQUIRED = False
    response = client.post(login_view_url, {"email": faker.email()})
    assert response.status_code == 200
    assert "form" not in response.context
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_DONE_TEMPLATE_NAME)


@pytest.mark.django_db
def test_login_with_an_active_user(client, login_view_url, active_user):
    response = client.post(login_view_url, {"email": active_user.email})
    assert response.status_code == 200
    assert "form" not in response.context
    assertTemplateUsed(response, settings.SOLOMON_LOGIN_DONE_TEMPLATE_NAME)
