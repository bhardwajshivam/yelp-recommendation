from __future__ import annotations

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

from yelp_cost_aware_agent.config import load_config
from yelp_cost_aware_agent.observability.metrics import record_run_metrics, render_prometheus_metrics
from yelp_cost_aware_agent.observability.mlflow_tracking import log_run_to_mlflow
from yelp_cost_aware_agent.orchestrator.service import RecommendationOrchestrator
from yelp_cost_aware_agent.schemas.models import PolicyConfig, RunResult, UserQuery

router = APIRouter()
orchestrator = RecommendationOrchestrator()


class RecommendRequest(BaseModel):
    query: str
    city: str | None = None
    category: str | None = None
    constraints: dict = Field(default_factory=dict)
    policy: PolicyConfig | None = None


@router.get("/health")
def health() -> dict[str, str]:
    config = load_config()
    return {"status": "ok", "app_name": config.app_name}


@router.get("/metrics")
def metrics() -> Response:
    body, content_type = render_prometheus_metrics()
    return Response(content=body, media_type=content_type)


@router.post("/recommend", response_model=RunResult)
def recommend(request: RecommendRequest) -> RunResult:
    config = load_config()
    policy = request.policy or config.policy
    user_query = UserQuery(
        text=request.query,
        city=request.city,
        category=request.category,
        constraints=request.constraints,
    )
    result = orchestrator.run(user_query, policy)
    if config.enable_prometheus_metrics:
        record_run_metrics(result)
    log_run_to_mlflow(result, config)
    return result
