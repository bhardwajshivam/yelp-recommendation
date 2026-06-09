FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
COPY data/benchmark_queries.jsonl ./data/benchmark_queries.jsonl

RUN python -m pip install --upgrade pip \
    && python -m pip install ".[dev]"

EXPOSE 8000

CMD ["uvicorn", "yelp_cost_aware_agent.app:app", "--host", "0.0.0.0", "--port", "8000"]
