from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def read_ranked(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranked", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ranked = read_ranked(args.ranked)
    review = [row for row in ranked if row["decision"] == "review"]
    blocked = [row for row in ranked if row["decision"] == "blocked"]
    reasons = Counter(
        reason
        for row in blocked
        for reason in row["gate_reasons"].split(";")
        if reason and reason != "pass"
    )

    top = review[:5]
    lines = [
        "# Research Memo",
        "",
        "## Summary",
        "",
        f"- Total candidates screened: {len(ranked)}",
        f"- Candidates for review: {len(review)}",
        f"- Candidates blocked: {len(blocked)}",
        "",
        "## Top Review Candidates",
        "",
        "| Rank | Candidate | Family | Score | Sharpe | Fitness | Self-Corr | Novelty |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for index, row in enumerate(top, 1):
        lines.append(
            f"| {index} | {row['candidate_id']} | {row['formula_family']} | {row['score']} | "
            f"{row['sharpe']} | {row['fitness']} | {row['self_correlation']} | {row['novelty']} |"
        )

    lines.extend([
        "",
        "## Main Block Reasons",
        "",
    ])
    for reason, count in reasons.most_common():
        lines.append(f"- `{reason}`: {count}")

    lines.extend([
        "",
        "## Validation",
        "",
        args.validation.read_text(encoding="utf-8").strip(),
        "",
        "## Next Action",
        "",
        "Review the top candidates manually, inspect family overlap, and only promote candidates that remain useful after novelty and self-correlation checks.",
    ])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote research memo to {args.output}")


if __name__ == "__main__":
    main()
