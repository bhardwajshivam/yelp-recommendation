from __future__ import annotations

from yelp_cost_aware_agent.schemas.models import RunResult

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
except ImportError:  # pragma: no cover - exercised only when optional dependency is absent.
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
    Counter = Gauge = Histogram = None  # type: ignore[assignment]
    generate_latest = None  # type: ignore[assignment]


PROMETHEUS_AVAILABLE = Counter is not None

if PROMETHEUS_AVAILABLE:
    REQUESTS_TOTAL = Counter(
        "yca_requests_total",
        "Recommendation requests processed by the cost-aware agent.",
        ["policy", "success", "failure_type"],
    )
    RUN_COST = Histogram(
        "yca_run_cost",
        "Estimated total cost per recommendation run.",
        ["policy"],
        buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
    )
    RUN_LATENCY_MS = Histogram(
        "yca_run_latency_ms",
        "End-to-end recommendation latency in milliseconds.",
        ["policy"],
        buckets=(5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000),
    )
    QUALITY_SCORE = Histogram(
        "yca_quality_score",
        "Weighted quality score per recommendation run.",
        ["policy"],
        buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.65, 0.75, 0.85, 0.95, 1.0),
    )
    STAGE_LATENCY_MS = Histogram(
        "yca_stage_latency_ms",
        "Pipeline stage latency in milliseconds.",
        ["policy", "stage", "success", "failure_type"],
        buckets=(1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000),
    )
    STAGE_COST = Histogram(
        "yca_stage_cost",
        "Estimated stage cost.",
        ["policy", "stage"],
        buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1),
    )
    RETRIEVAL_DEPTH = Gauge(
        "yca_retrieval_depth",
        "Configured retrieval depth observed in the latest run.",
        ["policy"],
    )


def record_run_metrics(result: RunResult) -> None:
    if not PROMETHEUS_AVAILABLE:
        return

    failure_type = result.failure_type.value if result.failure_type else "none"
    success = str(result.success).lower()

    REQUESTS_TOTAL.labels(result.policy, success, failure_type).inc()
    RUN_COST.labels(result.policy).observe(result.total_cost)
    RUN_LATENCY_MS.labels(result.policy).observe(result.total_latency_ms)
    QUALITY_SCORE.labels(result.policy).observe(result.quality.total)

    for event in result.events:
        event_failure = event.failure_type.value if event.failure_type else "none"
        event_success = str(event.success).lower()
        STAGE_LATENCY_MS.labels(
            result.policy,
            event.stage.value,
            event_success,
            event_failure,
        ).observe(event.metrics.latency_ms)
        STAGE_COST.labels(result.policy, event.stage.value).observe(event.metrics.cost.total)
        if event.metrics.retrieval_depth:
            RETRIEVAL_DEPTH.labels(result.policy).set(event.metrics.retrieval_depth)


def render_prometheus_metrics() -> tuple[bytes, str]:
    if not PROMETHEUS_AVAILABLE:
        return b"# prometheus_client is not installed\n", CONTENT_TYPE_LATEST
    return generate_latest(), CONTENT_TYPE_LATEST
