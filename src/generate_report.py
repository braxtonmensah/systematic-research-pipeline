from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def format_candidate_table(rows: list[dict[str, str]], limit: int = 8) -> list[str]:
    lines = [
        "| Rank | Candidate | Family | Action | Score | Sharpe | Fitness | Self-Corr | Novelty | Main Reason |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for index, row in enumerate(rows[:limit], 1):
        first_reason = row["gate_reasons"].split(";")[0]
        lines.append(
            f"| {index} | {row['candidate_id']} | {row['formula_family']} | {row['action']} | "
            f"{row['score']} | {row['sharpe']} | {row['fitness']} | {row['self_correlation']} | "
            f"{row['novelty']} | `{first_reason}` |"
        )
    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranked", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chart", type=Path, default=Path("reports/action_mix.svg"))
    return parser.parse_args()


def write_action_chart(counts: Counter[str], path: Path) -> None:
    labels = ["promote", "review", "refine", "block"]
    colors = {
        "promote": "#2f7d32",
        "review": "#1565c0",
        "refine": "#ef6c00",
        "block": "#9e1b32",
    }
    max_count = max(counts.values() or [1])
    rows = []
    for index, label in enumerate(labels):
        count = counts[label]
        width = int((count / max_count) * 420) if max_count else 0
        y = 42 + index * 42
        rows.append(f'<text x="20" y="{y + 16}" font-size="14" fill="#1f2937">{label}</text>')
        rows.append(f'<rect x="100" y="{y}" width="{width}" height="24" rx="3" fill="{colors[label]}"/>')
        rows.append(f'<text x="{110 + width}" y="{y + 17}" font-size="13" fill="#1f2937">{count}</text>')
    svg = "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" width="620" height="240" viewBox="0 0 620 240">',
        '<rect width="620" height="240" fill="#ffffff"/>',
        '<text x="20" y="28" font-size="18" font-weight="700" fill="#111827">Candidate Action Mix</text>',
        *rows,
        '</svg>',
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    ranked = read_csv(args.ranked)
    counts = Counter(row["action"] for row in ranked)
    reasons = Counter(
        reason
        for row in ranked
        for reason in row["gate_reasons"].split(";")
        if reason and reason != "pass"
    )
    promote_or_review = [row for row in ranked if row["action"] in {"promote", "review"}]
    blocked = [row for row in ranked if row["action"] == "block"]
    write_action_chart(counts, args.chart)

    lines = [
        "# Research Memo",
        "",
        "## Executive Readout",
        "",
        f"- Screened `{len(ranked)}` synthetic-but-realistic signal candidates across `{len(set(row['formula_family'] for row in ranked))}` formula families.",
        f"- Promoted `{counts['promote']}` candidates, kept `{counts['review']}` for review, sent `{counts['refine']}` to refinement, and blocked `{counts['block']}`.",
        "- The workflow optimizes for useful research throughput, not raw idea count.",
        "- Main controls: self-correlation, active-book similarity, family saturation, OOS decay, margin, and coverage.",
        "",
        f"![Candidate action mix](action_mix.svg)",
        "",
        "## Top Candidates",
        "",
        *format_candidate_table(promote_or_review, limit=10),
        "",
        "## Blocked Candidates Worth Learning From",
        "",
        *format_candidate_table(blocked, limit=6),
        "",
        "## Main Gate Pressure",
        "",
    ]
    for reason, count in reasons.most_common(10):
        lines.append(f"- `{reason}`: {count}")

    lines.extend([
        "",
        "## Validation Evidence",
        "",
        args.validation.read_text(encoding="utf-8").strip(),
        "",
        "## Decision Rule",
        "",
        "A candidate only moves forward if it has enough edge, enough novelty, and low enough self-correlation to justify more research time. Strong-looking candidates are still blocked when they are too crowded or when the validation pattern suggests duplicated evidence.",
        "",
        "## Next Research Action",
        "",
        "Inspect the top promoted family manually, then run a targeted refinement pass on `refine` candidates with self-correlation watch flags. Do not expand blocked families until the binding gate is addressed.",
    ])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote research memo to {args.output}")
    print(f"Wrote action chart to {args.chart}")


if __name__ == "__main__":
    main()
