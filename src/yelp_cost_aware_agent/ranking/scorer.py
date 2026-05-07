from __future__ import annotations

from collections import defaultdict

from yelp_cost_aware_agent.schemas.models import Business, ParsedIntent, RankedBusiness, RankingScore, Review


def _price_score(price: str | None, constraints: dict) -> float:
    if constraints.get("price_preference") != "affordable":
        return 0.5
    if price == "$":
        return 1.0
    if price == "$$":
        return 0.6
    return 0.2


def _remote_work_score(business: Business, constraints: dict) -> float:
    if not constraints.get("remote_work"):
        return 0.5
    return 1.0 if business.attributes.get("good_for_laptop") else 0.0


def _underrated_score(business: Business, constraints: dict) -> float:
    if not constraints.get("underrated"):
        return 0.5
    if business.stars >= 4.5 and business.review_count <= 60:
        return 1.0
    if business.stars >= 4.0 and business.review_count <= 100:
        return 0.7
    return 0.2


def _complaint_score(reviews: list[Review], wants_complaints: bool) -> float:
    if not wants_complaints:
        return 0.5
    negative_markers = ("complaint", "crowd", "downtime", "dirty", "wait", "cleaning")
    matched = sum(
        1 for review in reviews if any(marker in review.text.lower() for marker in negative_markers)
    )
    return min(1.0, matched / max(1, len(reviews)))


def rank_businesses(
    businesses: list[Business],
    reviews: list[Review],
    intent: ParsedIntent,
    top_k: int,
) -> list[RankedBusiness]:
    reviews_by_business: dict[str, list[Review]] = defaultdict(list)
    for review in reviews:
        reviews_by_business[review.business_id].append(review)

    ranked: list[RankedBusiness] = []
    for business in businesses:
        business_reviews = reviews_by_business.get(business.business_id, [])
        components = {
            "rating": business.stars / 5.0,
            "price_fit": _price_score(business.price, intent.constraints),
            "remote_work_fit": _remote_work_score(business, intent.constraints),
            "underrated_fit": _underrated_score(business, intent.constraints),
            "complaint_fit": _complaint_score(business_reviews, intent.wants_complaints),
            "review_signal": min(1.0, len(business_reviews) / 3.0),
        }
        total = (
            0.30 * components["rating"]
            + 0.20 * components["price_fit"]
            + 0.15 * components["remote_work_fit"]
            + 0.15 * components["underrated_fit"]
            + 0.10 * components["complaint_fit"]
            + 0.10 * components["review_signal"]
        )
        rationale = [
            f"rating={business.stars:.1f}",
            f"reviews={business.review_count}",
            f"price={business.price or 'unknown'}",
        ]
        ranked.append(
            RankedBusiness(
                business=business,
                score=RankingScore(
                    business_id=business.business_id,
                    total=round(total, 4),
                    components={key: round(value, 4) for key, value in components.items()},
                    rationale=rationale,
                ),
                supporting_reviews=business_reviews,
            )
        )

    ranked.sort(key=lambda item: item.score.total, reverse=True)
    return ranked[:top_k]
