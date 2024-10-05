import pytest

from solomon.forms import LoginForm
from solomon.models import SolomonToken


@pytest.mark.django_db
def test_login_form_with_valid_data(faker):
    form = LoginForm(
        {
            "email": faker.email(),
            "ip_address": faker.ipv4(),
            "redirect_url": "/" + faker.uri_path(deep=3),
        }
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_login_form_with_inactive_user(faker, inactive_user):
    form = LoginForm(
        {
            "email": inactive_user.email,
            "ip_address": faker.ipv4(),
            "redirect_url": "/" + faker.uri_path(deep=3),
        }
    )
    assert not form.is_valid()


@pytest.mark.django_db
def test_saving_form(faker):
    form = LoginForm(
        {
            "email": faker.email(),
            "ip_address": faker.ipv4(),
            "redirect_url": "/" + faker.uri_path(deep=3),
        }
    )
    if form.is_valid():
        form.save()
    assert SolomonToken.objects.count() == 1
