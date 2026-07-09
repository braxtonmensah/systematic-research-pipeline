from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
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
    oos_decay: float
    coverage: float
    complexity: float
    operator_count: int
    validation_window: str
    notes: str


REQUIRED_FIELDS = {
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
}


def as_float(row: dict[str, str], key: str, default: float | None = None) -> float:
    value = row.get(key)
    if value in (None, "") and default is not None:
        return default
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Missing or invalid numeric field {key!r} in {row}") from exc


def as_int(row: dict[str, str], key: str, default: int = 0) -> int:
    value = row.get(key)
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Missing or invalid integer field {key!r} in {row}") from exc


def load_candidates(path: Path) -> list[Candidate]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_FIELDS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Input is missing required fields: {', '.join(sorted(missing))}")
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
                oos_decay=as_float(row, "oos_decay", 0.18),
                coverage=as_float(row, "coverage", 0.90),
                complexity=as_float(row, "complexity", 0.45),
                operator_count=as_int(row, "operator_count", 4),
                validation_window=row.get("validation_window", "recent_holdout").strip(),
                notes=row.get("notes", "").strip(),
            )
            for row in reader
        ]


def gate_reasons(candidate: Candidate) -> list[str]:
    reasons = []
    if candidate.live_status == "blocked":
        reasons.append("live_status_blocked")
    if candidate.sharpe < 0.85:
        reasons.append("weak_sharpe")
    if candidate.fitness < 0.68:
        reasons.append("weak_fitness")
    if candidate.margin_bps < 4.0:
        reasons.append("thin_margin")
    if candidate.drawdown > 0.080:
        reasons.append("drawdown_risk")
    if candidate.turnover > 0.58:
        reasons.append("turnover_risk")
    if candidate.self_correlation >= 0.70:
        reasons.append("self_correlation_block")
    elif candidate.self_correlation >= 0.62:
        reasons.append("self_correlation_watch")
    if candidate.active_similarity >= 0.62:
        reasons.append("too_close_to_active_book")
    if candidate.family_saturation >= 0.72:
        reasons.append("crowded_family")
    if candidate.oos_decay >= 0.42:
        reasons.append("oos_decay_risk")
    if candidate.coverage < 0.74:
        reasons.append("coverage_gap")
    if candidate.complexity >= 0.88 and candidate.sharpe < 1.25:
        reasons.append("complexity_without_edge")
    return reasons


def hard_blocked(reasons: list[str]) -> bool:
    hard_reasons = {
        "live_status_blocked",
        "weak_sharpe",
        "weak_fitness",
        "thin_margin",
        "drawdown_risk",
        "turnover_risk",
        "self_correlation_block",
        "too_close_to_active_book",
        "crowded_family",
        "oos_decay_risk",
        "coverage_gap",
        "complexity_without_edge",
    }
    return any(reason in hard_reasons for reason in reasons)


def score_components(candidate: Candidate) -> dict[str, float]:
    quality = (
        0.36 * candidate.sharpe
        + 0.28 * candidate.fitness
        + 0.045 * candidate.margin_bps
        + 0.12 * candidate.coverage
    )
    risk = (
        0.52 * candidate.turnover
        + 1.65 * candidate.drawdown
        + 0.34 * candidate.oos_decay
        + 0.08 * max(candidate.complexity - 0.55, 0)
    )
    crowding = (
        0.70 * candidate.self_correlation
        + 0.48 * candidate.active_similarity
        + 0.34 * candidate.family_saturation
    )
    novelty = 0.56 * candidate.novelty
    feasibility = (
        0.18 * candidate.coverage
        - (0.20 if candidate.live_status == "watch" else 0.0)
        - (0.55 if candidate.live_status == "blocked" else 0.0)
    )
    total = quality + novelty + feasibility - risk - crowding
    return {
        "quality_component": round(quality, 4),
        "risk_penalty": round(risk, 4),
        "crowding_penalty": round(crowding, 4),
        "novelty_component": round(novelty, 4),
        "feasibility_component": round(feasibility, 4),
        "score": round(total, 4),
    }


def action_for(candidate: Candidate, reasons: list[str], score: float) -> str:
    if hard_blocked(reasons):
        return "block"
    if score >= 0.95 and candidate.self_correlation < 0.55:
        return "promote"
    if "self_correlation_watch" in reasons or candidate.live_status == "watch":
        return "refine"
    return "review"


def rank_candidates(candidates: list[Candidate]) -> list[dict[str, str]]:
    rows = []
    for candidate in candidates:
        reasons = gate_reasons(candidate)
        components = score_components(candidate)
        score = components["score"]
        action = action_for(candidate, reasons, score)
        rows.append({
            "candidate_id": candidate.candidate_id,
            "formula_family": candidate.formula_family,
            "data_theme": candidate.data_theme,
            "score": f"{score:.4f}",
            "action": action,
            "gate_reasons": ";".join(reasons) if reasons else "pass",
            "quality_component": f"{components['quality_component']:.4f}",
            "risk_penalty": f"{components['risk_penalty']:.4f}",
            "crowding_penalty": f"{components['crowding_penalty']:.4f}",
            "novelty_component": f"{components['novelty_component']:.4f}",
            "feasibility_component": f"{components['feasibility_component']:.4f}",
            "sharpe": f"{candidate.sharpe:.2f}",
            "fitness": f"{candidate.fitness:.2f}",
            "turnover": f"{candidate.turnover:.2f}",
            "drawdown": f"{candidate.drawdown:.3f}",
            "margin_bps": f"{candidate.margin_bps:.1f}",
            "self_correlation": f"{candidate.self_correlation:.2f}",
            "novelty": f"{candidate.novelty:.2f}",
            "active_similarity": f"{candidate.active_similarity:.2f}",
            "family_saturation": f"{candidate.family_saturation:.2f}",
            "oos_decay": f"{candidate.oos_decay:.2f}",
            "coverage": f"{candidate.coverage:.2f}",
            "complexity": f"{candidate.complexity:.2f}",
            "operator_count": str(candidate.operator_count),
            "validation_window": candidate.validation_window,
            "notes": candidate.notes,
        })
    action_order = {"promote": 0, "review": 1, "refine": 2, "block": 3}
    return sorted(rows, key=lambda row: (action_order[row["action"]], -float(row["score"])))


def write_ranked(rows: list[dict[str, str]], path: Path) -> None:
    if not rows:
        raise ValueError("No candidates to write")
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
    counts: dict[str, int] = {}
    for row in ranked:
        counts[row["action"]] = counts.get(row["action"], 0) + 1
    print(f"Wrote {len(ranked)} ranked candidates to {args.output}")
    print("Actions:", ", ".join(f"{key}={counts[key]}" for key in sorted(counts)))


if __name__ == "__main__":
    main()
