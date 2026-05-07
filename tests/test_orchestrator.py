from yelp_cost_aware_agent.orchestrator.service import RecommendationOrchestrator
from yelp_cost_aware_agent.schemas.models import PolicyConfig, StageName, UserQuery


def test_orchestrator_runs_full_pipeline() -> None:
    orchestrator = RecommendationOrchestrator()
    result = orchestrator.run(
        UserQuery(
            text="Find affordable sushi in Phoenix and explain why.",
            city="Phoenix",
            category="sushi",
            constraints={"price_preference": "affordable"},
        ),
        PolicyConfig(),
    )

    assert result.success is True
    assert result.recommendation.recommendations
    assert result.quality.total > 0
    assert [event.stage for event in result.events] == [
        StageName.PARSE_INTENT,
        StageName.FIND_BUSINESSES,
        StageName.GET_REVIEWS,
        StageName.RANK_BUSINESSES,
        StageName.GENERATE_RECOMMENDATION,
        StageName.RUN_EVAL,
    ]


def test_orchestrator_reports_retrieval_failure() -> None:
    orchestrator = RecommendationOrchestrator()
    result = orchestrator.run(
        UserQuery(
            text="Find barbecue in Boston.",
            city="Boston",
            category="barbecue",
            constraints={},
        ),
        PolicyConfig(),
    )

    assert result.success is False
    assert result.failure_type is not None
