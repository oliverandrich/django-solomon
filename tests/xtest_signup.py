import pytest
from pytest_django.asserts import assertTemplateUsed

from solomon.conf import settings
from solomon.forms import (
    SignupForm,
    SignupFormWithName,
)


@pytest.mark.django_db
def test_loading_view_with_name_required(client, signup_view_url):
    settings.SOLOMON_SIGNUP_REQUIRE_NAME = True

    response = client.get(signup_view_url)
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], SignupFormWithName)
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_TEMPLATE_NAME)


@pytest.mark.django_db
def test_loading_view_without_name_and_username_required(client, signup_view_url, settings):
    settings.SOLOMON_SIGNUP_REQUIRE_NAME = False

    response = client.get(signup_view_url)
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], SignupForm)
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_TEMPLATE_NAME)


@pytest.mark.django_db
def test_signup_without_input_data(client, signup_view_url, settings):
    settings.SOLOMON_SIGNUP_REQUIRE_NAME = True

    response = client.post(signup_view_url, {})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], SignupFormWithName)
    assert "name" in response.context["form"].errors
    assert "email" in response.context["form"].errors
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_TEMPLATE_NAME)

    settings.SOLOMON_SIGNUP_REQUIRE_NAME = False

    response = client.post(signup_view_url, {})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], SignupForm)
    assert "email" in response.context["form"].errors
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_TEMPLATE_NAME)


@pytest.mark.django_db
def test_signup_with_valid_input_data(client, signup_view_url, settings, faker):
    settings.SOLOMON_SIGNUP_REQUIRE_NAME = True

    response = client.post(signup_view_url, {"name": faker.name(), "email": faker.email()})
    assert response.status_code == 200
    assert "form" not in response.context
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_DONE_TEMPLATE_NAME)

    settings.SOLOMON_SIGNUP_REQUIRE_NAME = False

    response = client.post(signup_view_url, {"username": faker.user_name(), "email": faker.email()})
    assert response.status_code == 200
    assert "form" not in response.context
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_DONE_TEMPLATE_NAME)

    settings.SOLOMON_SIGNUP_REQUIRE_NAME = True

    response = client.post(
        signup_view_url,
        {"name": faker.name(), "username": faker.user_name(), "email": faker.email()},
    )
    assert response.status_code == 200
    assert "form" not in response.context
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_DONE_TEMPLATE_NAME)

    settings.SOLOMON_SIGNUP_REQUIRE_NAME = False

    response = client.post(signup_view_url, {"email": "test@example.com"})
    assert response.status_code == 200
    assert "form" not in response.context
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_DONE_TEMPLATE_NAME)


@pytest.mark.django_db
def test_signup_with_valid_name_and_invalid_email(client, signup_view_url, settings, faker):
    settings.SOLOMON_SIGNUP_REQUIRE_NAME = True

    response = client.post(signup_view_url, {"name": faker.name(), "email": "test@example"})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], SignupFormWithName)
    assert "email" in response.context["form"].errors
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_TEMPLATE_NAME)


@pytest.mark.django_db
def test_signup_with_empty_name_and_valid_email(client, signup_view_url, settings):
    settings.SOLOMON_SIGNUP_REQUIRE_NAME = True

    response = client.post(signup_view_url, {"name": "", "email": "test@example.com"})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], SignupFormWithName)
    assert "name" in response.context["form"].errors
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_TEMPLATE_NAME)


@pytest.mark.django_db
def test_signup_with_already_registered_email(
    client, signup_view_url, settings, faker, active_user
):
    settings.SOLOMON_SIGNUP_REQUIRE_NAME = True

    response = client.post(signup_view_url, {"name": faker.name(), "email": active_user.email})
    assert response.status_code == 200
    assert "form" in response.context
    assert isinstance(response.context["form"], SignupFormWithName)
    assert "email" in response.context["form"].errors
    assert (
        "Email address is already linked to an account." in response.context["form"].errors["email"]
    )
    assertTemplateUsed(response, settings.SOLOMON_SIGNUP_TEMPLATE_NAME)
