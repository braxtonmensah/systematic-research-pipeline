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
