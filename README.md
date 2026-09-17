# AI-Assisted Systematic Research Factory

[![Tests](https://github.com/braxtonmensah/systematic-research-factory/actions/workflows/tests.yml/badge.svg)](https://github.com/braxtonmensah/systematic-research-factory/actions/workflows/tests.yml)

**Software status:** the automated test suite checks the complete sample workflow on every push. Documented rejections and limitations are research findings, not unresolved runtime errors.

This is a public-safe case study of how I structure systematic research: generate candidates, reject weak ones early, control self-correlation, validate without leakage, and turn the result into a reviewable research memo.

I built it after noticing that a long candidate list can create false confidence. Many "different" signals are only small variations of the same formula family. This project treats rejection as a useful result and tests whether a ranking still works when an entire family is held out.

This repo is adapted from my personal research workflow as a WorldQuant Research Consultant. It is intentionally sanitized: no proprietary formulas, credentials, platform endpoints, live submission scripts, private datasets, or internal state. The point is to show process quality, not expose private alpha work.

## Snapshot

The sample pipeline builds a synthetic candidate book and produces:

- `reports/ranked_candidates.csv` - ranked candidates with score components and gate reasons.
- `reports/validation_report.md` - random split vs formula-family holdout validation.
- `reports/fold_metrics.csv` - fold-level validation metrics.
- `reports/action_mix.svg` - action mix chart.
- `reports/research_memo.md` - final decision memo for human review.

In the included deterministic run, random-id validation produced `0.580` precision@10, while formula-family holdout produced `0.520`. The six-point gap is the warning: a random split made the ranker look better because related formulas appeared on both sides of the split.

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

## Limits

- The candidate data is synthetic, so this is evidence about research process rather than evidence of a tradable strategy.
- The scoring weights and gate thresholds are illustrative; they are not calibrated to live returns.
- Precision@10 measures agreement with the case-study labels, not economic value.
- A real deployment would need time-indexed out-of-sample tests, transaction costs, capacity checks, and independent review before capital is involved.

## Tests

```bash
python -m unittest discover -s tests
```

## Disclaimer

This is an independent portfolio project. It is not affiliated with, endorsed by, or connected to WorldQuant. All data here is synthetic or sanitized for public demonstration.
