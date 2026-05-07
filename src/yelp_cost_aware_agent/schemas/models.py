from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class FailureType(str, Enum):
    RETRIEVAL_FAILURE = "retrieval_failure"
    RANKING_FAILURE = "ranking_failure"
    GROUNDING_FAILURE = "grounding_failure"
    CONSTRAINT_FAILURE = "constraint_failure"
    TOOL_ROUTING_FAILURE = "tool_routing_failure"
    ORCHESTRATION_FAILURE = "orchestration_failure"


class StageName(str, Enum):
    PARSE_INTENT = "parse_intent"
    FIND_BUSINESSES = "find_businesses"
    GET_REVIEWS = "get_reviews"
    RANK_BUSINESSES = "rank_businesses"
    GENERATE_RECOMMENDATION = "generate_recommendation"
    RUN_EVAL = "run_eval"


class PolicyConfig(BaseModel):
    name: str = "baseline"
    planner_model: str = "heuristic-cheap"
    synthesis_model: str = "heuristic-strong"
    validation_mode: str = "risky_only"
    retrieval_depth: int = 5
    review_limit_per_business: int = 5
    max_context_reviews: int = 12
    expose_all_tools: bool = False
    enable_validation: bool = True
    fixed_tool_cost: float = 0.002
    fixed_retrieval_cost_per_item: float = 0.0001
    fixed_compute_cost_per_stage: float = 0.0005
    token_cost_in: float = 0.000001
    token_cost_out: float = 0.000002
    retry_overhead_cost: float = 0.001


class UserQuery(BaseModel):
    text: str
    city: str | None = None
    category: str | None = None
    constraints: dict[str, Any] = Field(default_factory=dict)


class ParsedIntent(BaseModel):
    query_text: str
    city: str | None = None
    category: str | None = None
    target_count: int = 3
    wants_comparison: bool = False
    wants_complaints: bool = False
    constraints: dict[str, Any] = Field(default_factory=dict)
    risk_flags: list[str] = Field(default_factory=list)


class Business(BaseModel):
    business_id: str
    name: str
    city: str
    state: str | None = None
    categories: list[str] = Field(default_factory=list)
    stars: float = 0.0
    review_count: int = 0
    price: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class Review(BaseModel):
    review_id: str
    business_id: str
    stars: float
    text: str
    useful: int = 0


class RankingScore(BaseModel):
    business_id: str
    total: float
    components: dict[str, float]
    rationale: list[str] = Field(default_factory=list)


class RankedBusiness(BaseModel):
    business: Business
    score: RankingScore
    supporting_reviews: list[Review] = Field(default_factory=list)


class Recommendation(BaseModel):
    summary: str
    recommendations: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    warnings: list[str] = Field(default_factory=list)


class QualityScore(BaseModel):
    relevance: float
    constraint_satisfaction: float
    grounding: float
    usefulness: float
    total: float
    notes: list[str] = Field(default_factory=list)


class StepCost(BaseModel):
    stage: StageName
    model_cost: float = 0.0
    retrieval_cost: float = 0.0
    tool_cost: float = 0.0
    compute_cost: float = 0.0
    retry_overhead: float = 0.0
    total: float = 0.0


class StageMetrics(BaseModel):
    stage: StageName
    input_tokens: int = 0
    output_tokens: int = 0
    model_calls: int = 0
    retrieval_depth: int = 0
    candidate_businesses: int = 0
    retrieved_reviews: int = 0
    tools_exposed: int = 0
    retries: int = 0
    latency_ms: float = 0.0
    cost: StepCost


class StageEvent(BaseModel):
    run_id: str
    trace_id: str
    event_id: str = Field(default_factory=lambda: new_id("evt"))
    stage: StageName
    started_at: datetime = Field(default_factory=utc_now)
    ended_at: datetime = Field(default_factory=utc_now)
    success: bool = True
    failure_type: FailureType | None = None
    metrics: StageMetrics
    payload: dict[str, Any] = Field(default_factory=dict)


class RunResult(BaseModel):
    run_id: str
    trace_id: str
    policy: str
    query: UserQuery
    parsed_intent: ParsedIntent
    ranked_businesses: list[RankedBusiness]
    recommendation: Recommendation
    quality: QualityScore
    events: list[StageEvent]
    total_cost: float
    total_latency_ms: float
    success: bool
    failure_type: FailureType | None = None


class ExperimentQuery(BaseModel):
    query: str
    city: str | None = None
    category: str | None = None
    constraints: dict[str, Any] = Field(default_factory=dict)


class ExperimentAggregate(BaseModel):
    policy_name: str
    runs: int
    average_cost: float
    average_latency_ms: float
    average_quality: float
    cost_per_successful_run: float
    success_rate: float
    failure_breakdown: dict[str, int]


class ExperimentReport(BaseModel):
    aggregate: ExperimentAggregate
    runs: list[RunResult]
