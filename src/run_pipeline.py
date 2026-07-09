from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(args: list[str]) -> None:
    subprocess.run([sys.executable, "-m", *args], check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=240)
    parser.add_argument("--seed", type=int, default=20260710)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run(["src.simulate_candidates", "--output", "sample_data/candidates.csv", "--n", str(args.n), "--seed", str(args.seed)])
    run(["src.score_candidates", "--input", "sample_data/candidates.csv", "--output", "reports/ranked_candidates.csv"])
    run([
        "src.validate_ranker",
        "--input",
        "sample_data/candidates.csv",
        "--output",
        "reports/validation_report.md",
        "--fold-csv",
        "reports/fold_metrics.csv",
    ])
    run([
        "src.generate_report",
        "--ranked",
        "reports/ranked_candidates.csv",
        "--validation",
        "reports/validation_report.md",
        "--output",
        "reports/research_memo.md",
        "--chart",
        "reports/action_mix.svg",
    ])
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
