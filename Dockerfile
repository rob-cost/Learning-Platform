FROM python:3.13-slim-bookworm
LABEL maintanier="robertocostantino3@gmail.com"

COPY --from=ghcr.io/astral-sh/uv:0.8.18 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY src /app/src

WORKDIR /app/src

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
