from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from yelp_cost_aware_agent.config import load_config
from yelp_cost_aware_agent.orchestrator.service import RecommendationOrchestrator
from yelp_cost_aware_agent.schemas.models import (
    ExperimentAggregate,
    ExperimentQuery,
    ExperimentReport,
    PolicyConfig,
    RunResult,
    UserQuery,
)


def load_queries(path: Path) -> list[ExperimentQuery]:
    queries = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            queries.append(ExperimentQuery.model_validate_json(line))
    return queries


def load_policy(policy_name: str, path: Path) -> PolicyConfig:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    for policy_data in data.get("policies", []):
        if policy_data.get("name") == policy_name:
            return PolicyConfig.model_validate(policy_data)
    raise ValueError(f"Policy '{policy_name}' not found in {path}")


def run_experiment(queries: list[ExperimentQuery], policy: PolicyConfig) -> ExperimentReport:
    orchestrator = RecommendationOrchestrator()
    runs: list[RunResult] = []
    for item in queries:
        run = orchestrator.run(
            UserQuery(
                text=item.query,
                city=item.city,
                category=item.category,
                constraints=item.constraints,
            ),
            policy,
        )
        runs.append(run)

    successes = [run for run in runs if run.success]
    failure_breakdown: dict[str, int] = {}
    for run in runs:
        if run.failure_type is None:
            continue
        failure_breakdown[run.failure_type.value] = failure_breakdown.get(run.failure_type.value, 0) + 1

    aggregate = ExperimentAggregate(
        policy_name=policy.name,
        runs=len(runs),
        average_cost=round(sum(run.total_cost for run in runs) / max(1, len(runs)), 6),
        average_latency_ms=round(sum(run.total_latency_ms for run in runs) / max(1, len(runs)), 3),
        average_quality=round(sum(run.quality.total for run in runs) / max(1, len(runs)), 4),
        cost_per_successful_run=round(
            sum(run.total_cost for run in runs) / max(1, len(successes)),
            6,
        ),
        success_rate=round(len(successes) / max(1, len(runs)), 4),
        failure_breakdown=failure_breakdown,
    )
    return ExperimentReport(aggregate=aggregate, runs=runs)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cost-aware Yelp recommendation experiments.")
    parser.add_argument("--queries", default="data/benchmark_queries.jsonl")
    parser.add_argument("--policy", default="baseline")
    parser.add_argument("--policies", default="configs/policies.yaml")
    args = parser.parse_args()

    config = load_config()
    queries = load_queries(Path(args.queries))
    policy = load_policy(args.policy, Path(args.policies))
    policy = config.policy.model_copy(update=policy.model_dump(exclude_unset=True))
    report = run_experiment(queries, policy)
    print(json.dumps(report.aggregate.model_dump(), indent=2))


if __name__ == "__main__":
    main()
