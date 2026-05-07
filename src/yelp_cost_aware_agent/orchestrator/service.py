from __future__ import annotations

from yelp_cost_aware_agent.evaluation.scoring import score_run
from yelp_cost_aware_agent.observability.tracer import RunTracer
from yelp_cost_aware_agent.ranking.scorer import rank_businesses
from yelp_cost_aware_agent.retrieval.repository import YelpRepository
from yelp_cost_aware_agent.schemas.models import (
    FailureType,
    PolicyConfig,
    RunResult,
    StageName,
    UserQuery,
)
from yelp_cost_aware_agent.tools.intent import parse_intent
from yelp_cost_aware_agent.tools.recommendation import generate_recommendation


class RecommendationOrchestrator:
    def __init__(self, repository: YelpRepository | None = None) -> None:
        self.repository = repository or YelpRepository()

    def run(self, query: UserQuery, policy: PolicyConfig) -> RunResult:
        tracer = RunTracer(policy=policy)
        failure_type = None
        success = True

        parse_tracker = tracer.stage_context(StageName.PARSE_INTENT)
        intent = parse_intent(query)
        parse_tracker.finish(
            {"intent": intent.model_dump()},
            model_calls=1,
            tools_exposed=1 if policy.expose_all_tools else 0,
            input_obj=query.model_dump(),
            output_obj=intent.model_dump(),
        )

        find_tracker = tracer.stage_context(StageName.FIND_BUSINESSES)
        businesses = self.repository.find_businesses(intent, limit=policy.retrieval_depth)
        if not businesses:
            success = False
            failure_type = FailureType.RETRIEVAL_FAILURE
        find_tracker.finish(
            {"business_ids": [business.business_id for business in businesses]},
            success=success,
            failure_type=failure_type,
            retrieval_depth=policy.retrieval_depth,
            candidate_businesses=len(businesses),
            tools_exposed=2 if policy.expose_all_tools else 1,
            input_obj=intent.model_dump(),
            output_obj=[business.model_dump() for business in businesses],
        )

        reviews = []
        if businesses:
            review_tracker = tracer.stage_context(StageName.GET_REVIEWS)
            reviews = self.repository.get_reviews(
                [business.business_id for business in businesses],
                limit_per_business=policy.review_limit_per_business,
            )
            review_tracker.finish(
                {"review_ids": [review.review_id for review in reviews]},
                retrieval_depth=policy.review_limit_per_business,
                candidate_businesses=len(businesses),
                retrieved_reviews=len(reviews),
                tools_exposed=2 if policy.expose_all_tools else 1,
                input_obj=[business.model_dump() for business in businesses],
                output_obj=[review.model_dump() for review in reviews],
            )
        else:
            reviews = []

        rank_tracker = tracer.stage_context(StageName.RANK_BUSINESSES)
        ranked = rank_businesses(
            businesses,
            reviews[: policy.max_context_reviews],
            intent,
            top_k=intent.target_count,
        )
        if businesses and not ranked:
            success = False
            failure_type = FailureType.RANKING_FAILURE
        rank_tracker.finish(
            {"ranked_business_ids": [item.business.business_id for item in ranked]},
            success=success,
            failure_type=failure_type,
            candidate_businesses=len(businesses),
            retrieved_reviews=len(reviews[: policy.max_context_reviews]),
            input_obj={"intent": intent.model_dump(), "reviews": [review.model_dump() for review in reviews]},
            output_obj=[item.model_dump() for item in ranked],
        )

        recommendation_tracker = tracer.stage_context(StageName.GENERATE_RECOMMENDATION)
        recommendation = generate_recommendation(intent, ranked)
        recommendation_tracker.finish(
            {"summary": recommendation.summary},
            model_calls=1,
            retrieved_reviews=sum(len(item.supporting_reviews) for item in ranked),
            tools_exposed=2 if policy.expose_all_tools else 1,
            input_obj=[item.model_dump() for item in ranked],
            output_obj=recommendation.model_dump(),
        )

        eval_tracker = tracer.stage_context(StageName.RUN_EVAL)
        quality = score_run(intent, ranked, recommendation)
        if quality.constraint_satisfaction < 0.5 and success:
            failure_type = FailureType.CONSTRAINT_FAILURE
        eval_tracker.finish(
            {"quality": quality.model_dump()},
            success=success,
            failure_type=failure_type,
            model_calls=1 if policy.enable_validation else 0,
            input_obj=recommendation.model_dump(),
            output_obj=quality.model_dump(),
        )

        total_cost = round(sum(event.metrics.cost.total for event in tracer.events), 6)
        total_latency = round(sum(event.metrics.latency_ms for event in tracer.events), 3)

        return RunResult(
            run_id=tracer.run_id,
            trace_id=tracer.trace_id,
            policy=policy.name,
            query=query,
            parsed_intent=intent,
            ranked_businesses=ranked,
            recommendation=recommendation,
            quality=quality,
            events=tracer.events,
            total_cost=total_cost,
            total_latency_ms=total_latency,
            success=success,
            failure_type=failure_type,
        )
