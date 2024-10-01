set export
set dotenv-load

DJANGO_SETTINGS_MODULE := "tests.settings"

@_default:
    just --list

[private]
@check_uv:
    if ! command -v uv &> /dev/null; then \
        echo "uv could not be found. Exiting."; \
        exit; \
    fi

    if ! command -v uvx &> /dev/null; then \
        echo "uvx could not be found. Exiting."; \
        exit; \
    fi


# setup development environment
@bootstrap:
    if [ -x .env ]; then \
        echo "Already bootstraped. Exiting."; \
        exit; \
    fi

    echo "Creating .env file"
    echo "# Required for unittest discovery in VSCode." >> .env
    echo "MANAGE_PY_PATH='manage.py'" >> .env

    echo "Creating .envrc file for direnv"
    echo "test -d .venv || uv sync --frozen" >> .envrc
    echo "source .venv/bin/activate" >> .envrc
    test -x "$(command -v direnv)" && direnv allow

    echo "Installing dependencies"
    just upgrade

@makemigrations: check_uv
    uv run -m django makemigrations --settings=$DJANGO_SETTINGS_MODULE

# build release
@build: check_uv
    uv build

# publish release
@publish: check_uv build
    uv publish

# upgrade/install all dependencies defined in pyproject.toml
@upgrade: check_uv
    uv sync --all-extras

# run pre-commit rules on all files
@lint: check_uv
    uvx --with pre-commit-uv pre-commit run --all-files

# run test suite
@test: check_uv
    uv run -m coverage run -m django test --settings=$DJANGO_SETTINGS_MODULE --failfast
    uv run -m coverage report
    uv run -m coverage html

# run test suite
@test-all: check_uv
    uvx --with tox-uv tox

# serve docs during development
@serve-docs: check_uv
    uvx --with mkdocs-material mkdocs serve

# build documenation
@build-docs: check_uv
    uvx --with mkdocs-material mkdocs build

# publish documentation on github
@publish-docs: check_uv build-docs
    uvx --with mkdocs-material mkdocs gh-deploy --force
