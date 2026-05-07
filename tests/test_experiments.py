from yelp_cost_aware_agent.experiments.run import run_experiment
from yelp_cost_aware_agent.schemas.models import ExperimentQuery, PolicyConfig


def test_experiment_aggregate_fields_present() -> None:
    report = run_experiment(
        [
            ExperimentQuery(
                query="Find affordable sushi in Phoenix and explain why.",
                city="Phoenix",
                category="sushi",
                constraints={"price_preference": "affordable"},
            ),
            ExperimentQuery(
                query="Compare 3 coffee shops for remote work in Las Vegas.",
                city="Las Vegas",
                category="coffee",
                constraints={"remote_work": True, "count": 3},
            ),
        ],
        PolicyConfig(name="baseline"),
    )
    assert report.aggregate.policy_name == "baseline"
    assert report.aggregate.runs == 2
    assert report.aggregate.average_cost > 0
