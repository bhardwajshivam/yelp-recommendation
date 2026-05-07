from __future__ import annotations

from pathlib import Path

import duckdb


class DuckDBStore:
    """Minimal local storage helper for future Yelp ingestion and experiment logging."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> duckdb.DuckDBPyConnection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(str(self.path))

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                create table if not exists experiment_runs (
                    run_id varchar,
                    trace_id varchar,
                    policy varchar,
                    query_text varchar,
                    total_cost double,
                    total_latency_ms double,
                    quality double,
                    success boolean
                )
                """
            )
