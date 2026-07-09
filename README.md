# AI-Assisted Systematic Research Factory

Public-safe case study of how I structure systematic research: generate candidates, reject weak ones early, control self-correlation, validate without leakage, and turn the result into a reviewable research memo.

This repo is adapted from my personal research workflow as a WorldQuant Research Consultant. It is intentionally sanitized: no proprietary formulas, credentials, platform endpoints, live submission scripts, private datasets, or internal state. The point is to show process quality, not expose private alpha work.

## Snapshot

The sample pipeline builds a synthetic candidate book and produces:

- `reports/ranked_candidates.csv` - ranked candidates with score components and gate reasons.
- `reports/validation_report.md` - random split vs formula-family holdout validation.
- `reports/fold_metrics.csv` - fold-level validation metrics.
- `reports/action_mix.svg` - action mix chart.
- `reports/research_memo.md` - final decision memo for human review.

## What This Demonstrates

- Candidate scoring across edge, risk, novelty, crowding, and feasibility.
- Hard gates for weak or crowded ideas before wasting research time.
- Self-correlation and active-book similarity controls.
- Formula-family holdout validation to avoid duplicate-family leakage.
- Decision artifacts that a human or AI assistant can inspect and continue.

## Workflow

```mermaid
flowchart LR
    A["Candidate Book"] --> B["Score Components"]
    B --> C["Hard Gates"]
    C --> D["Action Labels"]
    D --> E["Family Holdout Validation"]
    E --> F["Research Memo"]
```

## Quick Start

```bash
python -m src.run_pipeline
```

Or run the steps manually:

```bash
python -m src.simulate_candidates --output sample_data/candidates.csv --n 240
python -m src.score_candidates --input sample_data/candidates.csv --output reports/ranked_candidates.csv
python -m src.validate_ranker --input sample_data/candidates.csv --output reports/validation_report.md --fold-csv reports/fold_metrics.csv
python -m src.generate_report --ranked reports/ranked_candidates.csv --validation reports/validation_report.md --output reports/research_memo.md
```

## Files

| Path | Purpose |
|---|---|
| `src/simulate_candidates.py` | Builds a deterministic synthetic candidate book. |
| `src/score_candidates.py` | Scores and gates candidate signals. |
| `src/validate_ranker.py` | Compares random-id validation with formula-family holdout validation. |
| `src/generate_report.py` | Builds a concise research memo from ranked candidates and validation output. |
| `src/run_pipeline.py` | Runs the full case-study pipeline. |
| `sample_data/candidates.csv` | Synthetic public-safe candidate metrics with 240 rows. |
| `docs/workflow.md` | Research workflow and gate rationale. |
| `docs/architecture.md` | Pipeline architecture and design choices. |
| `docs/reviewer_notes.md` | How to read this as a portfolio artifact. |
| `docs/privacy.md` | What was intentionally excluded from this public version. |

## Why This Matters

In systematic research, the hard part is not producing many ideas. The hard part is refusing weak ideas early, avoiding duplicate/crowded signals, and keeping a record of why a candidate deserved more work.

That same operating loop transfers to investment workflows: sourcing lists, market maps, diligence screens, KPI tracking, and memo prep all benefit from clear gates, validation, and reviewable outputs.

## Tests

```bash
python -m unittest discover -s tests
```

## Disclaimer

This is an independent portfolio project. It is not affiliated with, endorsed by, or connected to WorldQuant. All data here is synthetic or sanitized for public demonstration.
