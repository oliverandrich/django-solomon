# django-solomon

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/oliverandrich/django-solomon/test.yml?style=flat-square)
[![PyPI](https://img.shields.io/pypi/v/django-solomon.svg?style=flat-square)](https://pypi.org/project/django-solomon/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![GitHub](https://img.shields.io/github/license/oliverandrich/django-solomon?style=flat-square)
![Django Versions](https://img.shields.io/pypi/frameworkversions/django/django-solomon)
![Python Versions](https://img.shields.io/pypi/pyversions/django-solomon)
[![Downloads](https://static.pepy.tech/badge/django-solomon)](https://pepy.tech/project/django-solomon)
[![Downloads / Month](https://pepy.tech/badge/django-solomon/month)](<https://pepy.tech/project/django-solomon>)

django-solomon is a magic link authentication library for the Django framework, that combines ease of use, security, i18n and fully integrates into the `django.contrib.auth` workflow.

## Why is it named django-solomon?

Solomon is the unofficial name of the cat of Ernesto Blofeld. This library was started in autumn 2024. And autumn in my home means that my beloved cat starts to spend his whole day on my desk [curled up in the crook of my arm](https://social.tchncs.de/@oliverandrich/113214196404673039). Being forced to code in an Ernesto-Blofeld-position, it was natural to pick this name.

## Features

- Simple workflow for the user:
  - Enter email address on the login page.
  - Email with the verification link is sent to this address.
  - User clicks on the link and is immediately logged in.
- No seperate views for login and signup. This library believes that there is no difference. But if you need to collect further information after the first login of a new user, you can inject one of your views to collect this data.
- Secure defaults
  - Require same ip address for login and verification.
  - Require same browser for login and verification.
  - Magic expires after a configured timedelta. Default: 5 minutes.
  - If you need more relaxed settings, you can change the corresponding settings.
- Privacy settings
  - By default it stores the full ip address for the authentication process.
  - For increased privacy you can activate anonymisation. For IPv4 the last two octets are anonymized. For IPv6 only the first 64 bits are stored.
- The form label suffix can be changed by a setting.
- All forms and other user-facing strings are wrapped for proper i18n via the standard facilities of Django.
- All templates can be customized - for the web frontend and for the emails.

## Installation

1. Install the library.

   ```shell
   python -m pip install django-tailwind-cli
   ```

2. Add `solomon` to the `INSTALLED_APPS` in your `settings.py` file.

   ```python
   INSTALLED_APPS = [
       # other Django apps
       "solomon",
   ]
   ```

3. Add the authentication backend to the `AUTHENTICATION_BACKENDS` in your `settings.py` file.

   ```python
   AUTHENTICATION_BACKENDS = [
       "django.contrib.auth.backends.ModelBackend",
       "solomon.backends.SolomonBackend",
   ]
   ```

4. Add the url patterns to your `urls.py` file.

   ```python
   urlpatterns = [
       # other url definitions
       path("auth/", include("solomon.urls")),
   ]
   ```

5. Configure the authentication system point the login view of this library.

   ```python
   LOGIN_URL = "solomon:login"
   ```

6. Apply the migration of this library.

   ```shell
   python manage.py migrate
   ```

Enjoy!

Checkout the [documentation](https://django-solomon.andrich.me/) if you want to further tweak the login process.

## Requirements

Python 3.9 or newer with Django >= 4.2.

## Documentation

The documentation can be found at [https://django-solomon.andrich.me/](https://django-solomon.andrich.me/)

## Contributing

This package requires [uv](https://docs.astral.sh/uv/) for dependency management and tooling. So you have to [install it](https://docs.astral.sh/uv/getting-started/installation/) first. [just](https://github.com/casey/just) is used as a handy command runner to save some typing on the command line. Do yourself a favor and install it too.

```shell
# Setup development environment
just bootstrap

# Upgrade/install all dependencies defined in pyproject.toml
just upgrade

# Run pre-commit rules on all files
just lint

# Run test suite
just test

# Run test suite with different python and django versions
just test-all
```

### Without just, but using uv

```bash
# Create venv
uv venv

# Install dependencies
uv sync

# Run pre-commit rules on all files
uvx --with pre-commit-uv pre-commit run --all-files

# Run test suite
uv run pytest

# Run test suite with different python and django versions
uvx --with tox-uv tox
```

## License

This software is licensed under [MIT license](https://github.com/oliverandrich/django-solomon/blob/main/LICENSE).
