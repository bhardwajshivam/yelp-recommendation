from __future__ import annotations

from yelp_cost_aware_agent.schemas.models import ParsedIntent, QualityScore, Recommendation, RankedBusiness


def score_run(
    intent: ParsedIntent,
    ranked: list[RankedBusiness],
    recommendation: Recommendation,
) -> QualityScore:
    if not ranked:
        return QualityScore(
            relevance=0.0,
            constraint_satisfaction=0.0,
            grounding=0.0,
            usefulness=0.0,
            total=0.0,
            notes=["No ranked businesses available."],
        )

    relevance = min(1.0, sum(item.score.components.get("rating", 0.0) for item in ranked) / len(ranked))

    constraint_checks = []
    if intent.constraints.get("price_preference") == "affordable":
        constraint_checks.append(
            sum(item.score.components.get("price_fit", 0.0) for item in ranked) / len(ranked)
        )
    if intent.constraints.get("remote_work"):
        constraint_checks.append(
            sum(item.score.components.get("remote_work_fit", 0.0) for item in ranked) / len(ranked)
        )
    if intent.constraints.get("underrated"):
        constraint_checks.append(
            sum(item.score.components.get("underrated_fit", 0.0) for item in ranked) / len(ranked)
        )
    if intent.wants_complaints:
        constraint_checks.append(
            sum(item.score.components.get("complaint_fit", 0.0) for item in ranked) / len(ranked)
        )
    constraint_satisfaction = sum(constraint_checks) / len(constraint_checks) if constraint_checks else 0.85

    evidence_count = sum(len(entry.get("review_snippets", [])) for entry in recommendation.evidence)
    grounding = min(1.0, evidence_count / max(1, len(ranked) * 2))
    usefulness = 1.0 if recommendation.summary and recommendation.recommendations else 0.4

    total = (
        0.30 * relevance
        + 0.25 * constraint_satisfaction
        + 0.25 * grounding
        + 0.20 * usefulness
    )

    return QualityScore(
        relevance=round(relevance, 4),
        constraint_satisfaction=round(constraint_satisfaction, 4),
        grounding=round(grounding, 4),
        usefulness=round(usefulness, 4),
        total=round(total, 4),
        notes=["Heuristic v1 quality score."],
    )
