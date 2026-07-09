from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


FAMILIES = [
    ("quality_revision", "fundamental", 0.25),
    ("accrual_quality", "fundamental", 0.18),
    ("capital_efficiency", "fundamental", 0.28),
    ("volume_reversal", "price_volume", 0.12),
    ("event_pressure", "news_event", 0.20),
    ("options_pressure", "derivatives", 0.16),
    ("analyst_revision", "estimates", 0.14),
    ("liquidity_need", "price_volume", -0.02),
    ("crowded_momentum", "price_volume", 0.05),
    ("asset_light_reinvestment", "fundamental", 0.22),
    ("earnings_response", "news_event", 0.11),
    ("short_interest_stress", "short_interest", 0.09),
]

FIELDNAMES = [
    "candidate_id",
    "formula_family",
    "data_theme",
    "sharpe",
    "fitness",
    "turnover",
    "drawdown",
    "margin_bps",
    "self_correlation",
    "novelty",
    "active_similarity",
    "family_saturation",
    "live_status",
    "oos_decay",
    "coverage",
    "complexity",
    "operator_count",
    "validation_window",
    "notes",
]


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def make_row(index: int, rng: random.Random) -> dict[str, str]:
    family, theme, family_edge = rng.choice(FAMILIES)
    quality_noise = rng.gauss(0, 0.24)
    novelty_base = rng.uniform(0.25, 0.92)
    saturation = clamp(rng.betavariate(2.1, 3.4) + (0.24 if family == "crowded_momentum" else 0), 0.08, 0.94)
    self_corr = clamp(0.22 + 0.42 * saturation + rng.gauss(0, 0.10), 0.08, 0.92)
    active_similarity = clamp(0.18 + 0.52 * saturation + rng.gauss(0, 0.11), 0.05, 0.93)
    novelty = clamp(novelty_base - 0.34 * saturation + rng.gauss(0, 0.06), 0.06, 0.96)
    turnover = clamp(rng.uniform(0.12, 0.58) + (0.10 if theme == "price_volume" else 0), 0.08, 0.76)
    drawdown = clamp(rng.uniform(0.025, 0.075) + 0.020 * max(turnover - 0.45, 0), 0.018, 0.110)
    coverage = clamp(rng.uniform(0.70, 0.99) - 0.10 * (theme == "derivatives"), 0.55, 0.99)
    complexity = clamp(rng.betavariate(2.8, 2.4), 0.12, 0.98)
    oos_decay = clamp(rng.betavariate(2.0, 5.0) + 0.18 * max(complexity - 0.68, 0), 0.02, 0.72)
    sharpe = clamp(0.76 + family_edge + quality_noise + 0.32 * novelty - 0.24 * self_corr - 0.22 * oos_decay, 0.05, 1.95)
    fitness = clamp(0.58 + 0.55 * sharpe - 0.28 * turnover - 0.55 * drawdown - 0.12 * complexity + rng.gauss(0, 0.07), 0.05, 1.70)
    margin_bps = clamp(2.1 + 3.5 * sharpe - 1.4 * turnover - 1.1 * oos_decay + rng.gauss(0, 0.55), 0.5, 9.5)
    operator_count = int(clamp(round(2 + 8 * complexity + rng.gauss(0, 1.0)), 2, 12))

    live_status = "ok"
    if self_corr >= 0.72 or margin_bps < 3.5 or coverage < 0.68:
        live_status = "blocked"
    elif self_corr >= 0.60 or oos_decay >= 0.38 or active_similarity >= 0.55:
        live_status = "watch"

    note = "promising if novelty survives family holdout"
    if live_status == "blocked":
        note = "blocked until risk or crowding improves"
    elif live_status == "watch":
        note = "needs refinement before promotion"

    return {
        "candidate_id": f"C{index:04d}",
        "formula_family": family,
        "data_theme": theme,
        "sharpe": f"{sharpe:.3f}",
        "fitness": f"{fitness:.3f}",
        "turnover": f"{turnover:.3f}",
        "drawdown": f"{drawdown:.4f}",
        "margin_bps": f"{margin_bps:.2f}",
        "self_correlation": f"{self_corr:.3f}",
        "novelty": f"{novelty:.3f}",
        "active_similarity": f"{active_similarity:.3f}",
        "family_saturation": f"{saturation:.3f}",
        "live_status": live_status,
        "oos_decay": f"{oos_decay:.3f}",
        "coverage": f"{coverage:.3f}",
        "complexity": f"{complexity:.3f}",
        "operator_count": str(operator_count),
        "validation_window": "recent_family_holdout",
        "notes": note,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n", type=int, default=240)
    parser.add_argument("--seed", type=int, default=20260710)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    rows = [make_row(index, rng) for index in range(1, args.n + 1)]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic candidates to {args.output}")


if __name__ == "__main__":
    main()
