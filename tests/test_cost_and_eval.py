from yelp_cost_aware_agent.cost.model import estimate_step_cost
from yelp_cost_aware_agent.evaluation.scoring import score_run
from yelp_cost_aware_agent.schemas.models import (
    ParsedIntent,
    PolicyConfig,
    Recommendation,
    Review,
    StageMetrics,
    StageName,
    StepCost,
)
from yelp_cost_aware_agent.retrieval.repository import SAMPLE_BUSINESSES
from yelp_cost_aware_agent.ranking.scorer import rank_businesses


def test_estimate_step_cost_has_positive_total() -> None:
    metrics = StageMetrics(
        stage=StageName.FIND_BUSINESSES,
        input_tokens=100,
        output_tokens=20,
        model_calls=1,
        retrieval_depth=5,
        candidate_businesses=5,
        retrieved_reviews=10,
        tools_exposed=1,
        retries=1,
        latency_ms=10.0,
        cost=StepCost(stage=StageName.FIND_BUSINESSES),
    )
    cost = estimate_step_cost(PolicyConfig(), metrics)
    assert cost.total > 0
    assert cost.retrieval_cost > 0


def test_quality_score_uses_weighted_components() -> None:
    intent = ParsedIntent(
        query_text="Compare coffee shops",
        city="Las Vegas",
        category="coffee",
        wants_comparison=True,
        constraints={"remote_work": True},
    )
    reviews = [
        Review(review_id="a", business_id="vegas-coffee-1", stars=5, text="Great wifi", useful=1),
        Review(review_id="b", business_id="vegas-coffee-2", stars=4, text="Good for work", useful=1),
    ]
    ranked = rank_businesses(SAMPLE_BUSINESSES[2:5], reviews, intent, top_k=3)
    recommendation = Recommendation(
        summary="Compared a few coffee shops.",
        recommendations=[{"name": item.business.name} for item in ranked],
        evidence=[{"review_snippets": ["Great wifi"]} for _ in ranked],
    )
    quality = score_run(intent, ranked, recommendation)
    assert 0 <= quality.total <= 1
    assert quality.usefulness == 1.0
