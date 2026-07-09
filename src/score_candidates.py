from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Candidate:
    candidate_id: str
    formula_family: str
    data_theme: str
    sharpe: float
    fitness: float
    turnover: float
    drawdown: float
    margin_bps: float
    self_correlation: float
    novelty: float
    active_similarity: float
    family_saturation: float
    live_status: str


def as_float(row: dict[str, str], key: str) -> float:
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Missing or invalid numeric field {key!r} in {row}") from exc


def load_candidates(path: Path) -> list[Candidate]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [
            Candidate(
                candidate_id=row["candidate_id"],
                formula_family=row["formula_family"],
                data_theme=row["data_theme"],
                sharpe=as_float(row, "sharpe"),
                fitness=as_float(row, "fitness"),
                turnover=as_float(row, "turnover"),
                drawdown=as_float(row, "drawdown"),
                margin_bps=as_float(row, "margin_bps"),
                self_correlation=as_float(row, "self_correlation"),
                novelty=as_float(row, "novelty"),
                active_similarity=as_float(row, "active_similarity"),
                family_saturation=as_float(row, "family_saturation"),
                live_status=row["live_status"].strip().lower(),
            )
            for row in reader
        ]


def gate_reasons(candidate: Candidate) -> list[str]:
    reasons = []
    if candidate.live_status == "blocked":
        reasons.append("live_status_blocked")
    if candidate.sharpe < 0.90:
        reasons.append("weak_sharpe")
    if candidate.fitness < 0.70:
        reasons.append("weak_fitness")
    if candidate.margin_bps < 4.0:
        reasons.append("thin_margin")
    if candidate.drawdown > 0.075:
        reasons.append("drawdown_risk")
    if candidate.self_correlation >= 0.70:
        reasons.append("self_correlation_block")
    elif candidate.self_correlation >= 0.62:
        reasons.append("self_correlation_watch")
    if candidate.active_similarity >= 0.60:
        reasons.append("too_close_to_active_book")
    return reasons


def score_candidate(candidate: Candidate) -> float:
    quality = (0.34 * candidate.sharpe) + (0.24 * candidate.fitness) + (0.08 * candidate.margin_bps)
    risk_penalty = (0.80 * candidate.drawdown) + (0.42 * candidate.turnover)
    crowding_penalty = (0.55 * candidate.self_correlation) + (0.40 * candidate.active_similarity)
    novelty_credit = 0.42 * candidate.novelty
    family_penalty = 0.28 * candidate.family_saturation
    status_penalty = 0.35 if candidate.live_status == "watch" else 0.0
    return round(quality + novelty_credit - risk_penalty - crowding_penalty - family_penalty - status_penalty, 4)


def rank_candidates(candidates: list[Candidate]) -> list[dict[str, str]]:
    rows = []
    for candidate in candidates:
        reasons = gate_reasons(candidate)
        hard_blocked = any(
            reason in reasons
            for reason in {
                "live_status_blocked",
                "weak_sharpe",
                "weak_fitness",
                "thin_margin",
                "drawdown_risk",
                "self_correlation_block",
                "too_close_to_active_book",
            }
        )
        rows.append({
            "candidate_id": candidate.candidate_id,
            "formula_family": candidate.formula_family,
            "data_theme": candidate.data_theme,
            "score": f"{score_candidate(candidate):.4f}",
            "decision": "blocked" if hard_blocked else "review",
            "gate_reasons": ";".join(reasons) if reasons else "pass",
            "sharpe": f"{candidate.sharpe:.2f}",
            "fitness": f"{candidate.fitness:.2f}",
            "self_correlation": f"{candidate.self_correlation:.2f}",
            "novelty": f"{candidate.novelty:.2f}",
            "margin_bps": f"{candidate.margin_bps:.1f}",
        })
    return sorted(rows, key=lambda row: float(row["score"]), reverse=True)


def write_ranked(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ranked = rank_candidates(load_candidates(args.input))
    write_ranked(ranked, args.output)
    print(f"Wrote {len(ranked)} ranked candidates to {args.output}")


if __name__ == "__main__":
    main()
