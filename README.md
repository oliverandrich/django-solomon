# django-solomon

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/oliverandrich/django-solomon/test.yml?style=flat-square)
[![PyPI](https://img.shields.io/pypi/v/django-solomon.svg?style=flat-square)](https://pypi.org/project/django-solomon/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
![GitHub](https://img.shields.io/github/license/oliverandrich/django-solomon?style=flat-square)
![Django Versions](https://img.shields.io/pypi/frameworkversions/django/django-solomon)
![Python Versions](https://img.shields.io/pypi/pyversions/django-solomon)
[![Downloads](https://static.pepy.tech/badge/django-solomon)](https://pepy.tech/project/django-solomon)
[![Downloads / Month](https://pepy.tech/badge/django-solomon/month)](<https://pepy.tech/project/django-solomon>)

django-solomon is a magic link authentication library for the Django framework.

## Why is it named djngo-solomon?

Solomon is the unofficial name of the cat of Ernesto Blofeld. This library was started in autumn 2024. And autumn in my home means, that my beloved cat starts to spend his whole day on my desk [curled up in the crook of my arm](https://social.tchncs.de/@oliverandrich/113214196404673039). Being forced to code in a Ernesto-Blofeld-position, it was natural to pick this name.

## Installation

## Features

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
