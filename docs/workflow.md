# Workflow

The full private workflow is larger, but the public version keeps the core decision structure.

## 1. Candidate Intake

Each candidate is represented by observable research metrics:

- `sharpe`
- `fitness`
- `turnover`
- `drawdown`
- `margin_bps`
- `self_correlation`
- `novelty`
- `active_similarity`
- `family_saturation`
- `live_status`

The scoring script treats these as evidence, not as a guarantee. A candidate can have a high score and still be blocked by a hard gate.

## 2. Quality Gates

The workflow rejects candidates that fail basic practical tests:

- Negative or weak risk-adjusted performance.
- Poor fitness after accounting for turnover and drawdown.
- Self-correlation that is too high relative to existing work.
- Low margin or poor live feasibility.
- Crowded formula families that are unlikely to add portfolio value.

## 3. Novelty Discipline

Novelty matters because duplicate signals waste research time. The score penalizes:

- High active-book similarity.
- High family saturation.
- Low structural novelty.

The best candidate is not always the highest Sharpe candidate; it is the candidate with the best evidence after crowding and implementation risk.

## 4. Grouped Validation

Random row splits can leak information when many candidates share formula families or settings. The validation script uses a deterministic formula-family holdout so related candidates stay together.

That is more conservative and closer to how the research process actually fails in practice.

## 5. Human Review

The scripts produce a short memo instead of a black-box score. The memo explains:

- Which candidates passed.
- Which candidates were blocked.
- Which families are overused.
- What should be reviewed next.

The intended user is a human researcher or AI assistant deciding what to inspect next.
