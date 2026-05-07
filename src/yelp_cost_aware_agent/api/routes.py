from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from yelp_cost_aware_agent.config import load_config
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
    return orchestrator.run(user_query, policy)
