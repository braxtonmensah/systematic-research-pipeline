from __future__ import annotations

import argparse
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

from .score_candidates import load_candidates, rank_candidates


def family_fold(family: str, folds: int) -> int:
    digest = hashlib.sha256(family.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % folds


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--folds", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    candidates = load_candidates(args.input)
    ranked = rank_candidates(candidates)
    by_id = {row["candidate_id"]: row for row in ranked}

    fold_rows: dict[int, list[str]] = defaultdict(list)
    for candidate in candidates:
        fold_rows[family_fold(candidate.formula_family, args.folds)].append(candidate.candidate_id)

    lines = [
        "# Validation Report",
        "",
        "Grouped validation keeps formula families together so near-duplicate ideas do not leak across train/test.",
        "",
        f"- Candidates: {len(candidates)}",
        f"- Formula families: {len(set(c.formula_family for c in candidates))}",
        f"- Folds: {args.folds}",
        "",
        "## Fold Summary",
        "",
        "| Fold | Candidates | Review | Blocked | Avg Score |",
        "|---:|---:|---:|---:|---:|",
    ]

    for fold in range(args.folds):
        ids = fold_rows[fold]
        rows = [by_id[item] for item in ids]
        decisions = Counter(row["decision"] for row in rows)
        avg_score = sum(float(row["score"]) for row in rows) / max(len(rows), 1)
        lines.append(
            f"| {fold} | {len(rows)} | {decisions['review']} | {decisions['blocked']} | {avg_score:.4f} |"
        )

    review_rows = [row for row in ranked if row["decision"] == "review"]
    blocked_rows = [row for row in ranked if row["decision"] == "blocked"]
    lines.extend([
        "",
        "## Decision Quality",
        "",
        f"- Review candidates: {len(review_rows)}",
        f"- Blocked candidates: {len(blocked_rows)}",
        f"- Top review candidate: {review_rows[0]['candidate_id'] if review_rows else 'none'}",
        "",
        "The point of the validation loop is not to maximize a single score. It is to make sure the top candidates remain reasonable after duplicate families are held out.",
    ])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote validation report to {args.output}")


if __name__ == "__main__":
    main()
