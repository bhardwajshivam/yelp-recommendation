from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from yelp_cost_aware_agent.cost.model import estimate_step_cost
from yelp_cost_aware_agent.schemas.models import (
    FailureType,
    PolicyConfig,
    StageEvent,
    StageMetrics,
    StageName,
    new_id,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def estimate_tokens(value: Any) -> int:
    if value is None:
        return 0
    text = str(value)
    return max(1, len(text) // 4)


@dataclass
class RunTracer:
    policy: PolicyConfig
    run_id: str = field(default_factory=lambda: new_id("run"))
    trace_id: str = field(default_factory=lambda: new_id("trace"))
    events: list[StageEvent] = field(default_factory=list)

    def stage_context(self, stage: StageName) -> "StageTracker":
        return StageTracker(tracer=self, stage=stage)


@dataclass
class StageTracker:
    tracer: RunTracer
    stage: StageName
    start_time: float = field(default_factory=perf_counter)
    started_at: datetime = field(default_factory=utc_now)

    def finish(
        self,
        payload: dict[str, Any],
        *,
        success: bool = True,
        failure_type: FailureType | None = None,
        model_calls: int = 0,
        retrieval_depth: int = 0,
        candidate_businesses: int = 0,
        retrieved_reviews: int = 0,
        tools_exposed: int = 0,
        retries: int = 0,
        input_obj: Any = None,
        output_obj: Any = None,
    ) -> StageEvent:
        latency_ms = (perf_counter() - self.start_time) * 1000
        metrics = StageMetrics(
            stage=self.stage,
            input_tokens=estimate_tokens(input_obj),
            output_tokens=estimate_tokens(output_obj),
            model_calls=model_calls,
            retrieval_depth=retrieval_depth,
            candidate_businesses=candidate_businesses,
            retrieved_reviews=retrieved_reviews,
            tools_exposed=tools_exposed,
            retries=retries,
            latency_ms=latency_ms,
            cost=None,  # type: ignore[arg-type]
        )
        metrics.cost = estimate_step_cost(self.tracer.policy, metrics)
        event = StageEvent(
            run_id=self.tracer.run_id,
            trace_id=self.tracer.trace_id,
            stage=self.stage,
            started_at=self.started_at,
            ended_at=utc_now(),
            success=success,
            failure_type=failure_type,
            metrics=metrics,
            payload=payload,
        )
        self.tracer.events.append(event)
        return event
