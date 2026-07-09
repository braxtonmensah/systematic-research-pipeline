# AI-Assisted Systematic Research Factory

Public-safe case study of a research workflow for generating, screening, validating, and tracking systematic equity signal candidates.

This repository is adapted from my personal research workflow as a WorldQuant Research Consultant. It is intentionally sanitized: it contains no proprietary formulas, credentials, platform endpoints, live submission scripts, private datasets, or internal state. The goal is to show the process discipline behind the workflow: candidate triage, validation gates, self-correlation control, and reportable research decisions.

## What This Demonstrates

- Candidate scoring across research quality, risk, novelty, and operational readiness.
- Hard gates for weak or crowded ideas before spending more time on them.
- Grouped validation logic to avoid formula-family leakage.
- A lightweight reporting loop that turns raw candidate metrics into a reviewable decision memo.
- AI-assisted workflow design: the system is built so a human or AI agent can inspect the next action, evidence, and stop rule.

## Workflow

1. Start with candidate metrics from research runs.
2. Apply quality gates: Sharpe, fitness, turnover, drawdown, margin, novelty, and self-correlation.
3. Penalize crowded families and candidates too close to active signals.
4. Rank the surviving ideas by expected research value.
5. Validate by formula-family holdout instead of random row splits.
6. Export a concise report for human review.

## Quick Start

```bash
python -m src.score_candidates --input sample_data/candidates.csv --output reports/ranked_candidates.csv
python -m src.validate_ranker --input sample_data/candidates.csv --output reports/validation_report.md
python -m src.generate_report --ranked reports/ranked_candidates.csv --validation reports/validation_report.md --output reports/research_memo.md
```

## Files

| Path | Purpose |
|---|---|
| `src/score_candidates.py` | Scores and gates candidate signals. |
| `src/validate_ranker.py` | Runs grouped holdout validation by formula family. |
| `src/generate_report.py` | Builds a concise research memo from ranked candidates and validation output. |
| `sample_data/candidates.csv` | Synthetic public-safe candidate metrics. |
| `docs/workflow.md` | Research workflow and gate rationale. |
| `docs/privacy.md` | What was intentionally excluded from this public version. |

## Why This Matters

In systematic research, the hard part is not producing many ideas. The hard part is refusing weak ideas early, avoiding duplicate/crowded signals, and keeping a record of why a candidate deserved more work. This repo shows that operating loop in a small, inspectable form.

## Disclaimer

This is an independent portfolio project. It is not affiliated with, endorsed by, or connected to WorldQuant. All data here is synthetic or sanitized for public demonstration.
