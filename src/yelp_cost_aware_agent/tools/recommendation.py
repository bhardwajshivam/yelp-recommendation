from __future__ import annotations

from yelp_cost_aware_agent.schemas.models import ParsedIntent, RankedBusiness, Recommendation


def generate_recommendation(intent: ParsedIntent, ranked: list[RankedBusiness]) -> Recommendation:
    if not ranked:
        return Recommendation(
            summary="No matching businesses were found for the current query.",
            recommendations=[],
            evidence=[],
            warnings=["No candidates available."],
        )

    recommendation_items = []
    evidence = []
    for item in ranked:
        review_snippets = [review.text for review in item.supporting_reviews[:2]]
        recommendation_items.append(
            {
                "business_id": item.business.business_id,
                "name": item.business.name,
                "city": item.business.city,
                "score": item.score.total,
                "score_components": item.score.components,
                "why": item.score.rationale,
            }
        )
        evidence.append(
            {
                "business_id": item.business.business_id,
                "review_snippets": review_snippets,
            }
        )

    names = ", ".join(entry["name"] for entry in recommendation_items[: intent.target_count])
    if intent.wants_complaints:
        summary = f"Top complaint-focused findings for {intent.query_text}: {names}."
    elif intent.wants_comparison:
        summary = f"Compared {len(recommendation_items)} options for {intent.query_text}: {names}."
    else:
        summary = f"Recommended options for {intent.query_text}: {names}."

    return Recommendation(
        summary=summary,
        recommendations=recommendation_items,
        evidence=evidence,
    )
