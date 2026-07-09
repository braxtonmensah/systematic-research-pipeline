# Research Memo

## Summary

- Total candidates screened: 12
- Candidates for review: 9
- Candidates blocked: 3

## Top Review Candidates

| Rank | Candidate | Family | Score | Sharpe | Fitness | Self-Corr | Novelty |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | F011 | capital_efficiency | 1.1949 | 1.51 | 1.29 | 0.39 | 0.73 |
| 2 | F001 | quality_revision | 1.0923 | 1.42 | 1.21 | 0.41 | 0.74 |
| 3 | F007 | accrual_quality | 1.0176 | 1.36 | 1.17 | 0.48 | 0.69 |
| 4 | F005 | event_pressure | 0.9537 | 1.18 | 1.00 | 0.35 | 0.81 |
| 5 | F009 | options_pressure | 0.8540 | 1.24 | 1.04 | 0.44 | 0.77 |

## Main Block Reasons

- `live_status_blocked`: 3
- `thin_margin`: 3
- `self_correlation_block`: 2
- `too_close_to_active_book`: 2
- `weak_sharpe`: 2
- `weak_fitness`: 2
- `drawdown_risk`: 1
- `self_correlation_watch`: 1

## Validation

# Validation Report

Grouped validation keeps formula families together so near-duplicate ideas do not leak across train/test.

- Candidates: 12
- Formula families: 6
- Folds: 3

## Fold Summary

| Fold | Candidates | Review | Blocked | Avg Score |
|---:|---:|---:|---:|---:|
| 0 | 2 | 1 | 1 | 0.1914 |
| 1 | 8 | 6 | 2 | 0.4956 |
| 2 | 2 | 2 | 0 | 0.4773 |

## Decision Quality

- Review candidates: 9
- Blocked candidates: 3
- Top review candidate: F011

The point of the validation loop is not to maximize a single score. It is to make sure the top candidates remain reasonable after duplicate families are held out.

## Next Action

Review the top candidates manually, inspect family overlap, and only promote candidates that remain useful after novelty and self-correlation checks.
