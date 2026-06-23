FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY sentinelai /app/sentinelai
COPY scripts /app/scripts
COPY eval /app/eval
COPY static /app/static
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "sentinelai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
