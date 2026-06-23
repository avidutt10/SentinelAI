# SentinelAI

SentinelAI is a development-first incident investigation backend. It ingests incidents, retrieves relevant operational knowledge, runs a lightweight multi-agent workflow, and returns a structured investigation report.

## Features

- FastAPI API for incident, knowledge, and report workflows
- SQLAlchemy models for incidents, knowledge documents, reports, and traces
- Retrieval service with an in-memory fallback and optional Qdrant integration
- Sequential agent pipeline with optional LangGraph wiring
- Synthetic fixtures plus an eval runner
- Docker Compose for PostgreSQL and Qdrant

## Quick Start

1. Create a virtual environment and install dependencies.
2. Copy `.env.example` to `.env` and adjust values if needed.
3. Run the API:

```bash
uvicorn sentinelai.api.main:app --reload
```

4. Seed sample knowledge and incidents:

```bash
python -m scripts.seed_knowledge
python -m scripts.seed_incidents
```

5. Open `http://127.0.0.1:8000/docs`.

## Default Authentication

All non-health endpoints expect the header:

```text
x-api-key: sentinel-dev-key
```

## Docker Services

```bash
docker compose up -d postgres qdrant
```

The app defaults to a temp-directory SQLite file for local development, but can be pointed at PostgreSQL with `DATABASE_URL`.

## Eval

```bash
python -m eval.run_eval
python -m eval.score_eval
```
