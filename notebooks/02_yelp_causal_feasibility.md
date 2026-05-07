# Yelp Causal Study Feasibility Audit

This note ties the proposed causal inference studies to the actual Yelp archive currently present in this repository:

- `/Users/shivambhardwaj/Desktop/git-projects/yelp-recommendation/Yelp_JSON/yelp_dataset.tar`

## Confirmed archive members

From direct archive inspection, the following core files are present:

- `yelp_academic_dataset_business.json`
- `yelp_academic_dataset_checkin.json`
- `yelp_academic_dataset_review.json`
- `yelp_academic_dataset_user.json`
- `yelp_academic_dataset_tip.json`

## Confirmed schema support

### Business

Observed fields from the first row:

- `business_id`
- `name`
- `address`
- `city`
- `state`
- `postal_code`
- `latitude`
- `longitude`
- `stars`
- `review_count`
- `is_open`
- `attributes`
- `categories`
- `hours`

### Review

Observed fields from the first row:

- `review_id`
- `user_id`
- `business_id`
- `stars`
- `useful`
- `funny`
- `cool`
- `text`
- `date`

### Checkin

Observed fields from the first row:

- `business_id`
- `date`

### User

Observed fields from the first row:

- `user_id`
- `name`
- `review_count`
- `yelping_since`
- `useful`
- `funny`
- `cool`
- `elite`
- `friends`
- `fans`
- `average_stars`
- `compliment_hot`
- `compliment_more`
- `compliment_profile`
- `compliment_cute`
- `compliment_list`
- `compliment_note`
- `compliment_plain`
- `compliment_cool`
- `compliment_funny`
- `compliment_writer`
- `compliment_photos`

### Tip

Observed fields from the first row:

- `user_id`
- `business_id`
- `text`
- `date`
- `compliment_count`

## Feasibility matrix

| # | Study | Treatment | Outcome | Actual schema support | Feasibility | Notes |
|---|---|---|---|---|---|---|
| 1 | Rating -> Future Popularity | Business rating at time `t` | Future review growth | `business.stars`, `review.date`, `review.business_id`, `business.city`, `business.categories`, `business.attributes` | High | Strongest starter study. Need business-time panel from reviews. |
| 2 | Early Review Volume -> Long-Run Success | Review count in early window | Later review growth, survival, rating stability | `review.date`, `review.business_id`, `business.review_count`, `business.is_open`, `business.city`, `business.categories` | High | Very feasible. Survival proxy can use `is_open`, with caution. |
| 3 | Price Level -> Demand | Price tier | Future review growth or ratings | `business.attributes` likely contains price information, plus `review.date`, `business.categories`, `business.city` | Medium | Feasible if price is consistently populated inside nested attributes. Needs parsing and missingness audit. |
| 4 | Attributes -> Outcomes | Attribute present: `WiFi`, `Delivery`, etc. | Review growth, ratings | `business.attributes`, `review.date`, `review.business_id`, `business.categories`, `business.city` | Medium-High | Strong candidate after attribute normalization. Main issue is confounding and sparse or messy nested fields. |
| 5 | Negative Review Shock -> Later Outcomes | Burst of low-star or negative-text reviews | Later review growth, later ratings | `review.stars`, `review.text`, `review.date`, `review.business_id` | High | Very feasible. Event-study framing is natural with dated reviews. |
| 6 | Competition Density -> Attention | Nearby same-category competitor count | Review growth or ratings | `business.latitude`, `business.longitude`, `business.categories`, `business.city`, `review.date` | Medium-High | Spatial support is good. Need careful local market controls. |
| 7 | Elite Reviewer Attention -> Visibility | Early elite user review | Future review growth | `review.user_id`, `review.date`, `review.business_id`, `user.elite` | High | Better than expected because elite status is confirmed in user data. Strong study candidate. |
| 8 | Review Narrative -> Future Demand | Early text theme exposure | Future review growth or ratings | `review.text`, `review.date`, `review.business_id`, `review.stars`, `business.categories`, `business.city` | Medium-High | Very feasible technically. Identification is harder than implementation. |

## Ranking by practical usefulness

### Best first studies

1. Rating -> Future Popularity
2. Early Review Volume -> Long-Run Success
3. Negative Review Shock -> Later Outcomes
4. Elite Reviewer Attention -> Visibility

These are the best starting points because they have:

- direct temporal structure in the data
- strong support from confirmed columns
- clear relevance to popularity bias and recommendation dynamics

### Good second-wave studies

5. Competition Density -> Attention
6. Attributes -> Outcomes
7. Review Narrative -> Future Demand

These look promising, but they need more feature engineering and stronger controls.

### Most fragile study

8. Price Level -> Demand

This may still be useful, but only if price metadata inside `business.attributes` is sufficiently complete and standardized.

## Recommended prototype order

### Prototype 1

`Rating -> Future Popularity`

Build a business-month panel:

- current cumulative average rating
- current cumulative review count
- future review count in next 3 months
- controls for city, category, and business characteristics

### Prototype 2

`Elite Reviewer Attention -> Visibility`

Event study around first elite-user review:

- pre-period review trend
- post-period review trend
- matched businesses without early elite exposure

### Prototype 3

`Negative Review Shock -> Later Outcomes`

Define a shock as:

- multiple low-star reviews in a short window
- or sharp drop in rolling average stars

Then estimate impact on future review growth.

## Immediate next data tasks

1. Parse and flatten `business.attributes`.
2. Load business, review, user, tip, and checkin into DuckDB.
3. Build a business-time panel from `review.date`.
4. Create category and city normalization helpers.
5. Audit missingness for price and key attributes.
