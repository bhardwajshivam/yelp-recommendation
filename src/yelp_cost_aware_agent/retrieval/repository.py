from __future__ import annotations

from functools import lru_cache
# lru_cache

from yelp_cost_aware_agent.schemas.models import Business, ParsedIntent, Review


SAMPLE_BUSINESSES = [
    Business(
        business_id="phoenix-sushi-1",
        name="Sakura Budget Sushi",
        city="Phoenix",
        state="AZ",
        categories=["Sushi Bars", "Japanese"],
        stars=4.4,
        review_count=182,
        price="$",
        attributes={"good_for_laptop": False, "noise_level": "medium"},
    ),
    Business(
        business_id="phoenix-sushi-2",
        name="Desert Omakase Express",
        city="Phoenix",
        state="AZ",
        categories=["Sushi Bars"],
        stars=4.1,
        review_count=96,
        price="$$",
        attributes={"good_for_laptop": False, "noise_level": "quiet"},
    ),
    Business(
        business_id="vegas-coffee-1",
        name="Mojave Work Cafe",
        city="Las Vegas",
        state="NV",
        categories=["Coffee & Tea", "Cafes"],
        stars=4.7,
        review_count=210,
        price="$$",
        attributes={"good_for_laptop": True, "wifi": "free", "noise_level": "quiet"},
    ),
    Business(
        business_id="vegas-coffee-2",
        name="Neon Roasters",
        city="Las Vegas",
        state="NV",
        categories=["Coffee & Tea"],
        stars=4.5,
        review_count=154,
        price="$",
        attributes={"good_for_laptop": True, "wifi": "free", "noise_level": "medium"},
    ),
    Business(
        business_id="vegas-coffee-3",
        name="Late Checkout Coffee",
        city="Las Vegas",
        state="NV",
        categories=["Coffee & Tea", "Breakfast & Brunch"],
        stars=4.2,
        review_count=88,
        price="$$",
        attributes={"good_for_laptop": True, "wifi": "free", "noise_level": "quiet"},
    ),
    Business(
        business_id="phoenix-mexican-1",
        name="Barrio Hidden Kitchen",
        city="Phoenix",
        state="AZ",
        categories=["Mexican"],
        stars=4.8,
        review_count=41,
        price="$",
        attributes={"good_for_laptop": False},
    ),
    Business(
        business_id="phoenix-mexican-2",
        name="Southwest Masa House",
        city="Phoenix",
        state="AZ",
        categories=["Mexican"],
        stars=4.6,
        review_count=55,
        price="$$",
        attributes={"good_for_laptop": False},
    ),
    Business(
        business_id="tempe-gym-1",
        name="Cactus Strength Club",
        city="Tempe",
        state="AZ",
        categories=["Gyms", "Fitness & Instruction"],
        stars=3.8,
        review_count=133,
        price="$$",
        attributes={"open_late": True},
    ),
    Business(
        business_id="tempe-gym-2",
        name="Sun Devil Fitness Hub",
        city="Tempe",
        state="AZ",
        categories=["Gyms"],
        stars=3.6,
        review_count=84,
        price="$",
        attributes={"open_late": False},
    ),
]


SAMPLE_REVIEWS = [
    Review(review_id="r1", business_id="phoenix-sushi-1", stars=5, text="Fresh fish, fast service, and low prices.", useful=4),
    Review(review_id="r2", business_id="phoenix-sushi-1", stars=4, text="Great lunch special. Seating is simple but worth it.", useful=2),
    Review(review_id="r3", business_id="phoenix-sushi-2", stars=4, text="Good quality but a little pricier than budget spots.", useful=1),
    Review(review_id="r4", business_id="vegas-coffee-1", stars=5, text="Excellent wifi, lots of outlets, and calm remote work vibe.", useful=7),
    Review(review_id="r5", business_id="vegas-coffee-2", stars=4, text="Solid espresso and enough space to work for a few hours.", useful=5),
    Review(review_id="r6", business_id="vegas-coffee-3", stars=4, text="Quiet in the mornings, gets crowded after lunch.", useful=3),
    Review(review_id="r7", business_id="phoenix-mexican-1", stars=5, text="Small place with standout tacos and almost no wait.", useful=6),
    Review(review_id="r8", business_id="phoenix-mexican-2", stars=4, text="Very strong flavors and friendly staff.", useful=4),
    Review(review_id="r9", business_id="tempe-gym-1", stars=2, text="Main complaint is equipment downtime during peak hours.", useful=8),
    Review(review_id="r10", business_id="tempe-gym-1", stars=3, text="Locker rooms need better cleaning consistency.", useful=5),
    Review(review_id="r11", business_id="tempe-gym-2", stars=2, text="Members complain about crowding and short weekend hours.", useful=4),
]


class YelpRepository:
    """Simple local repository with deterministic sample data for the first vertical slice."""

    @lru_cache(maxsize=1)
    def list_businesses(self) -> list[Business]:
        return SAMPLE_BUSINESSES

    @lru_cache(maxsize=1)
    def list_reviews(self) -> list[Review]:
        return SAMPLE_REVIEWS

    def find_businesses(self, intent: ParsedIntent, limit: int) -> list[Business]:
        businesses = []
        category_term = (intent.category or "").lower()
        city_term = (intent.city or "").lower()
        for business in self.list_businesses():
            category_match = not category_term or any(
                category_term in category.lower() for category in business.categories
            )
            city_match = not city_term or business.city.lower() == city_term
            if category_match and city_match:
                businesses.append(business)
        return businesses[:limit]

    def get_reviews(self, business_ids: list[str], limit_per_business: int) -> list[Review]:
        buckets: dict[str, int] = {business_id: 0 for business_id in business_ids}
        selected: list[Review] = []
        for review in self.list_reviews():
            if review.business_id not in buckets:
                continue
            if buckets[review.business_id] >= limit_per_business:
                continue
            selected.append(review)
            buckets[review.business_id] += 1
        return selected
