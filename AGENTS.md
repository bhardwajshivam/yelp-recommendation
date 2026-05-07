# AGENTS.md

## Project Mission

This repository builds `yelp-cost-aware-agent`, a local-first recommendation agent and experiment harness focused on minimizing system cost while preserving recommendation quality.

Target objective:

`min E[C(pi)] subject to E[Q(pi)] >= Q_min`

This is not a generic Yelp app. Every implementation choice should support cost-aware experimentation, interpretable behavior, and structured observability.

## Engineering Priorities

1. Keep the first version simple, deterministic, and easy to run locally.
2. Optimize for cost-aware experimentation, not surface polish.
3. Every pipeline stage must emit structured events with `run_id` and `trace_id`.
4. Prefer interpretable heuristics and explicit score components over black-box ranking in v1.
5. Prefer code-enforced constraints over prompt-only behavior.
6. Keep prompts concise and explicit when LLM hooks are added.
7. Use config-driven policies so experiments can swap routing, context, retrieval depth, and validation behavior.
8. Treat observability as a means to study cost, quality, and failures.

## Required Pipeline Stages

- `parse_intent`
- `find_businesses`
- `get_reviews`
- `rank_businesses`
- `generate_recommendation`
- `run_eval`

## Observability Requirements

Each stage should log structured data for:

- stage name
- start and end timestamps
- latency
- retries
- tool exposure count
- retrieval depth
- candidate business count
- retrieved review count
- input token estimate
- output token estimate
- model call count
- estimated step cost
- failure type when applicable

## Cost Model Expectations

At minimum, approximate cost with:

- model calls
- token usage or token placeholders
- retrieval volume
- optional fixed step costs
- retries

Keep the model transparent and easy to adjust for experiments.

## Quality Framework

Per-run quality:

`Q_i = 0.30 R_i + 0.25 C_i + 0.25 G_i + 0.20 U_i`

Where:

- `R_i`: relevance
- `C_i`: constraint satisfaction
- `G_i`: grounding/evidence support
- `U_i`: usefulness

The codebase should store component scores, the weighted score, and supporting notes.

## Implementation Guidance

- Use Python with FastAPI.
- Use Pydantic models for API and event schemas.
- Use DuckDB or a similarly simple local storage option.
- Keep tool outputs structured.
- Add TODO hooks for future real LLM integration instead of hiding placeholders.
- Write tests for orchestration, ranking, cost aggregation, eval scoring, and experiments.
- Avoid unnecessary frontend work in v1.

## Collaboration Notes For Future Runs

- Inspect the local repository state before editing.
- Preserve deterministic behavior where possible.
- Do not replace interpretable scoring with opaque logic without strong justification.
- If a shortcut reduces measurement quality, document the tradeoff explicitly.
