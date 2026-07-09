# Validation Report

This validation is designed around the main failure mode in signal research: near-duplicate formula families can make random splits look better than they are.

## Dataset

- Candidates: 240
- Formula families: 12
- Promote/review/refine/block: 12 / 55 / 10 / 163

## Leakage Check

- Random-id split average precision@10: `0.580`
- Formula-family holdout average precision@10: `0.520`
- Optimism gap: `+0.060`

If the random split is meaningfully better, the workflow treats that as a warning that candidates may be repeating the same idea rather than discovering independent evidence.

## Family Holdout Folds

| Fold | Candidates | Promote | Review | Refine | Block | Precision@10 | Mean Score |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 18 | 1 | 7 | 0 | 10 | 0.200 | 0.1546 |
| 1 | 63 | 3 | 13 | 2 | 45 | 0.900 | 0.1007 |
| 2 | 58 | 0 | 8 | 3 | 47 | 0.300 | -0.1941 |
| 3 | 52 | 6 | 15 | 3 | 28 | 0.700 | 0.2367 |
| 4 | 49 | 2 | 12 | 2 | 33 | 0.500 | 0.2302 |

## Main Gate Pressure

- `weak_sharpe`: 108
- `thin_margin`: 90
- `live_status_blocked`: 66
- `oos_decay_risk`: 44
- `coverage_gap`: 43
- `weak_fitness`: 35
- `crowded_family`: 23
- `turnover_risk`: 15

## Interpretation

A good research system should not only rank candidates. It should explain which constraints are binding. Here, the most useful output is the combination of action labels, gate reasons, and family-holdout precision.
