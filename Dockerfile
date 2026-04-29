FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_PATH=/opt/poetry-venvs \
    PATH="/opt/poetry/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/poetry-venvs

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /workspace

COPY pyproject.toml README.md ./

RUN poetry install --no-root --without dev

FROM base AS dev

RUN poetry install --no-root --with dev

CMD ["sleep", "infinity"]

FROM base AS runtime

WORKDIR /workspace

COPY . /workspace
