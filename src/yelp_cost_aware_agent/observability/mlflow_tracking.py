from __future__ import annotations

from typing import Any

from yelp_cost_aware_agent.config import AppConfig
from yelp_cost_aware_agent.schemas.models import RunResult


def log_run_to_mlflow(result: RunResult, config: AppConfig) -> None:
    if not config.enable_mlflow:
        return

    try:
        import mlflow
    except ImportError:
        return

    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment(config.mlflow_experiment_name)

    with mlflow.start_run(run_name=result.run_id):
        mlflow.set_tags(
            {
                "run_id": result.run_id,
                "trace_id": result.trace_id,
                "policy": result.policy,
                "environment": config.environment,
                "success": str(result.success).lower(),
                "failure_type": result.failure_type.value if result.failure_type else "none",
            }
        )
        mlflow.log_params(
            {
                "query_city": result.query.city or "",
                "query_category": result.query.category or "",
                "parsed_category": result.parsed_intent.category or "",
                "target_count": result.parsed_intent.target_count,
            }
        )
        mlflow.log_metrics(
            {
                "total_cost": result.total_cost,
                "total_latency_ms": result.total_latency_ms,
                "quality_total": result.quality.total,
                "quality_relevance": result.quality.relevance,
                "quality_constraint_satisfaction": result.quality.constraint_satisfaction,
                "quality_grounding": result.quality.grounding,
                "quality_usefulness": result.quality.usefulness,
            }
        )

        for event in result.events:
            prefix = f"stage_{event.stage.value}"
            mlflow.log_metrics(
                {
                    f"{prefix}_latency_ms": event.metrics.latency_ms,
                    f"{prefix}_cost": event.metrics.cost.total,
                    f"{prefix}_input_tokens": event.metrics.input_tokens,
                    f"{prefix}_output_tokens": event.metrics.output_tokens,
                    f"{prefix}_model_calls": event.metrics.model_calls,
                    f"{prefix}_retrieved_reviews": event.metrics.retrieved_reviews,
                }
            )

        mlflow.log_dict(_artifact_payload(result), "run_result.json")


def _artifact_payload(result: RunResult) -> dict[str, Any]:
    return result.model_dump(mode="json")
