FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

WORKDIR /api

# Install needed OS packages
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/pgdg.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/pgdg.gpg] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client-17 \
    && apt-get purge -y curl gnupg \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY ./src ./src
COPY uv.lock .
COPY pyproject.toml .
COPY alembic.ini .
COPY alembic-backup.ini .

RUN uv sync

ENV PATH="/api/.venv/bin:$PATH"
ENV PYTHONPATH="/api:$PYTHONPATH"
