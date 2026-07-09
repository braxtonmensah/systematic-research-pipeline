from __future__ import annotations

import argparse
import csv
import hashlib
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from .score_candidates import load_candidates, rank_candidates


def stable_bucket(value: str, buckets: int) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % buckets


def empirical_success(row: dict[str, str]) -> bool:
    return (
        float(row["sharpe"]) >= 1.05
        and float(row["fitness"]) >= 0.85
        and float(row["margin_bps"]) >= 4.5
        and float(row["self_correlation"]) < 0.62
        and float(row["oos_decay"]) < 0.38
        and row["action"] in {"promote", "review", "refine"}
    )


def precision_at(rows: list[dict[str, str]], k: int) -> float:
    top = rows[:k]
    if not top:
        return 0.0
    return sum(1 for row in top if empirical_success(row)) / len(top)


def mean_score(rows: list[dict[str, str]]) -> float:
    if not rows:
        return 0.0
    return statistics.fmean(float(row["score"]) for row in rows)


def summarize_folds(rows: list[dict[str, str]], fold_key: str, folds: int) -> list[dict[str, str]]:
    buckets: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        buckets[stable_bucket(row[fold_key], folds)].append(row)

    summaries = []
    for fold in range(folds):
        fold_rows = sorted(buckets[fold], key=lambda item: float(item["score"]), reverse=True)
        actions = Counter(row["action"] for row in fold_rows)
        summaries.append({
            "fold": str(fold),
            "candidates": str(len(fold_rows)),
            "promote": str(actions["promote"]),
            "review": str(actions["review"]),
            "refine": str(actions["refine"]),
            "block": str(actions["block"]),
            "precision_at_10": f"{precision_at(fold_rows, 10):.3f}",
            "mean_score": f"{mean_score(fold_rows):.4f}",
        })
    return summaries


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--fold-csv", type=Path, default=Path("reports/fold_metrics.csv"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ranked = rank_candidates(load_candidates(args.input))
    ranked_by_score = sorted(ranked, key=lambda row: float(row["score"]), reverse=True)
    group_summary = summarize_folds(ranked_by_score, "formula_family", args.folds)
    randomish_summary = summarize_folds(ranked_by_score, "candidate_id", args.folds)

    write_csv(group_summary, args.fold_csv)

    action_counts = Counter(row["action"] for row in ranked)
    family_counts = Counter(row["formula_family"] for row in ranked)
    reason_counts = Counter(
        reason
        for row in ranked
        for reason in row["gate_reasons"].split(";")
        if reason and reason != "pass"
    )

    group_p10 = statistics.fmean(float(row["precision_at_10"]) for row in group_summary)
    random_p10 = statistics.fmean(float(row["precision_at_10"]) for row in randomish_summary)
    optimism_gap = random_p10 - group_p10

    lines = [
        "# Validation Report",
        "",
        "This validation is designed around the main failure mode in signal research: near-duplicate formula families can make random splits look better than they are.",
        "",
        "## Dataset",
        "",
        f"- Candidates: {len(ranked)}",
        f"- Formula families: {len(family_counts)}",
        f"- Promote/review/refine/block: {action_counts['promote']} / {action_counts['review']} / {action_counts['refine']} / {action_counts['block']}",
        "",
        "## Leakage Check",
        "",
        f"- Random-id split average precision@10: `{random_p10:.3f}`",
        f"- Formula-family holdout average precision@10: `{group_p10:.3f}`",
        f"- Optimism gap: `{optimism_gap:+.3f}`",
        "",
        "If the random split is meaningfully better, the workflow treats that as a warning that candidates may be repeating the same idea rather than discovering independent evidence.",
        "",
        "## Family Holdout Folds",
        "",
        "| Fold | Candidates | Promote | Review | Refine | Block | Precision@10 | Mean Score |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in group_summary:
        lines.append(
            f"| {row['fold']} | {row['candidates']} | {row['promote']} | {row['review']} | "
            f"{row['refine']} | {row['block']} | {row['precision_at_10']} | {row['mean_score']} |"
        )

    lines.extend([
        "",
        "## Main Gate Pressure",
        "",
    ])
    for reason, count in reason_counts.most_common(8):
        lines.append(f"- `{reason}`: {count}")

    lines.extend([
        "",
        "## Interpretation",
        "",
        "A good research system should not only rank candidates. It should explain which constraints are binding. Here, the most useful output is the combination of action labels, gate reasons, and family-holdout precision.",
    ])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote validation report to {args.output}")
    print(f"Wrote fold metrics to {args.fold_csv}")


if __name__ == "__main__":
    main()
