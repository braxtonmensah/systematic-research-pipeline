# Systematic Research Pipeline

[![Tests](https://github.com/braxtonmensah/systematic-research-pipeline/actions/workflows/tests.yml/badge.svg)](https://github.com/braxtonmensah/systematic-research-pipeline/actions/workflows/tests.yml)

A Python pipeline for ranking quantitative signal candidates, enforcing risk and correlation gates, and testing whether selection quality survives formula-family holdouts.

The repository uses deterministic synthetic data so the full workflow can be inspected and reproduced without exposing proprietary signals or datasets.

## Results

The included run evaluates 240 candidates and compares two validation designs:

| Validation design | Precision@10 |
|---|---:|
| Random candidate split | 0.580 |
| Formula-family holdout | 0.520 |

The six-point drop shows why random splits can overstate performance when closely related formulas appear in both the training and validation sets.

The pipeline produces a ranked candidate book, fold-level validation metrics, an action summary, and a decision memo. The committed outputs are generated from a fixed seed and covered by automated tests on Python 3.11 and 3.12.

## Pipeline

```mermaid
flowchart LR
    A["Candidate Book"] --> B["Score Components"]
    B --> C["Risk and Correlation Gates"]
    C --> D["Action Labels"]
    D --> E["Family Holdout Validation"]
    E --> F["Research Memo"]
```

The scoring layer combines estimated edge, risk, novelty, crowding, and implementation feasibility. Hard gates block candidates with weak economics or excessive similarity before they reach the final ranking.

## Reproduce

The project uses only the Python standard library.

```bash
python -m src.run_pipeline
python -m unittest discover -s tests -v
```

Individual stages can also be run separately:

```bash
python -m src.simulate_candidates --output sample_data/candidates.csv --n 240
python -m src.score_candidates --input sample_data/candidates.csv --output reports/ranked_candidates.csv
python -m src.validate_ranker --input sample_data/candidates.csv --output reports/validation_report.md --fold-csv reports/fold_metrics.csv
python -m src.generate_report --ranked reports/ranked_candidates.csv --validation reports/validation_report.md --output reports/research_memo.md
```

## Repository Guide

| Path | Purpose |
|---|---|
| `src/simulate_candidates.py` | Generates the deterministic candidate universe. |
| `src/score_candidates.py` | Applies component scores and hard gates. |
| `src/validate_ranker.py` | Compares random splits with formula-family holdouts. |
| `src/generate_report.py` | Produces the final research memo. |
| `reports/ranked_candidates.csv` | Candidate scores, decisions, and gate reasons. |
| `reports/validation_report.md` | Aggregate validation results. |
| `reports/fold_metrics.csv` | Fold-level performance. |
| `reports/research_memo.md` | Final decision record. |
| `docs/architecture.md` | Design and data-flow notes. |

## Scope

This project demonstrates research process, not a live trading strategy. The data is synthetic, the thresholds are illustrative, and precision@10 measures agreement with case-study labels rather than economic return. A production study would require time-indexed out-of-sample data, transaction-cost and capacity models, and independent review.

This is an independent project and is not affiliated with or endorsed by WorldQuant.
