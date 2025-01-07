FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry@1.8.5

COPY poetry.lock pyproject.toml README.md /app/

RUN poetry install --with dev

COPY . /app/
