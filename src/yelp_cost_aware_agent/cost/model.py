from __future__ import annotations

from yelp_cost_aware_agent.schemas.models import PolicyConfig, StageMetrics, StepCost


def estimate_step_cost(policy: PolicyConfig, metrics: StageMetrics) -> StepCost:
    model_cost = (
        metrics.input_tokens * policy.token_cost_in
        + metrics.output_tokens * policy.token_cost_out
    )
    retrieval_cost = (
        metrics.candidate_businesses + metrics.retrieved_reviews
    ) * policy.fixed_retrieval_cost_per_item
    tool_cost = metrics.tools_exposed * policy.fixed_tool_cost
    compute_cost = policy.fixed_compute_cost_per_stage
    retry_overhead = metrics.retries * policy.retry_overhead_cost
    total = model_cost + retrieval_cost + tool_cost + compute_cost + retry_overhead
    return StepCost(
        stage=metrics.stage,
        model_cost=model_cost,
        retrieval_cost=retrieval_cost,
        tool_cost=tool_cost,
        compute_cost=compute_cost,
        retry_overhead=retry_overhead,
        total=total,
    )
