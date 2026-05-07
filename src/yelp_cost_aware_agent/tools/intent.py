from __future__ import annotations

from yelp_cost_aware_agent.schemas.models import ParsedIntent, UserQuery


def parse_intent(query: UserQuery) -> ParsedIntent:
    text = query.text.lower()
    target_count = query.constraints.get("count", 3)
    wants_comparison = "compare" in text
    wants_complaints = "complaint" in text or query.constraints.get("complaints_only", False)
    risk_flags: list[str] = []
    if "underrated" in text:
        risk_flags.append("subjective_ranking")
    if wants_complaints:
        risk_flags.append("negative_sentiment_focus")
    if query.constraints:
        risk_flags.append("constraint_heavy")

    return ParsedIntent(
        query_text=query.text,
        city=query.city,
        category=query.category,
        target_count=target_count,
        wants_comparison=wants_comparison,
        wants_complaints=wants_complaints,
        constraints=query.constraints,
        risk_flags=risk_flags,
    )
