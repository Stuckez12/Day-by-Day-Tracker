FROM python:3.13
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

WORKDIR /api

RUN pip install uv

COPY ./backend ./backend
COPY uv.lock .
COPY pyproject.toml .
COPY alembic.ini .

RUN uv sync

ENV PATH="/api/.venv/bin:$PATH"
ENV PYTHONPATH="/api:$PYTHONPATH"
