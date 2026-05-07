# yelp-cost-aware-agent

`yelp-cost-aware-agent` is a local-first FastAPI backend and experiment harness for studying how to reduce recommendation-system cost while preserving recommendation quality.

## Focus

The project optimizes for:

- interpretable recommendation logic
- structured observability per pipeline stage
- policy-driven experiments for cost, latency, and quality tradeoffs
- simple local setup

## Pipeline

- `parse_intent`
- `find_businesses`
- `get_reviews`
- `rank_businesses`
- `generate_recommendation`
- `run_eval`

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .[dev]
```

Run the API:

```bash
uvicorn yelp_cost_aware_agent.app:app --reload
```

Run tests:

```bash
python3 -m pytest
```

Run experiments:

```bash
python3 -m yelp_cost_aware_agent.experiments.run --queries data/benchmark_queries.jsonl --policy baseline
```

## Assumptions In V1

- The first version uses deterministic heuristics and placeholder token estimates where needed.
- The code includes TODO hooks for future real LLM integration.
- Yelp data loading is config-driven and local-first.

## Data

Place the Yelp dataset archive at:

`./Yelp JSON/yelp_dataset.tar`

The ingestion path is designed to stay simple and local.
