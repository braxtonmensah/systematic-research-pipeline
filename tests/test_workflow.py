from __future__ import annotations

import csv
import random
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.score_candidates import Candidate, gate_reasons, load_candidates, rank_candidates
from src.simulate_candidates import FIELDNAMES, make_row


class WorkflowTests(unittest.TestCase):
    def test_self_correlation_block_is_hard_gate(self) -> None:
        candidate = Candidate(
            candidate_id="T001",
            formula_family="quality_revision",
            data_theme="fundamental",
            sharpe=1.45,
            fitness=1.10,
            turnover=0.20,
            drawdown=0.035,
            margin_bps=6.2,
            self_correlation=0.74,
            novelty=0.82,
            active_similarity=0.25,
            family_saturation=0.30,
            live_status="ok",
            oos_decay=0.14,
            coverage=0.95,
            complexity=0.40,
            operator_count=4,
            validation_window="recent_family_holdout",
            notes="test",
        )

        ranked = rank_candidates([candidate])

        self.assertIn("self_correlation_block", gate_reasons(candidate))
        self.assertEqual(ranked[0]["action"], "block")

    def test_strong_uncrowded_candidate_promotes(self) -> None:
        candidate = Candidate(
            candidate_id="T002",
            formula_family="capital_efficiency",
            data_theme="fundamental",
            sharpe=1.65,
            fitness=1.30,
            turnover=0.18,
            drawdown=0.030,
            margin_bps=7.6,
            self_correlation=0.34,
            novelty=0.86,
            active_similarity=0.22,
            family_saturation=0.24,
            live_status="ok",
            oos_decay=0.10,
            coverage=0.98,
            complexity=0.42,
            operator_count=5,
            validation_window="recent_family_holdout",
            notes="test",
        )

        ranked = rank_candidates([candidate])

        self.assertEqual(ranked[0]["action"], "promote")
        self.assertGreater(float(ranked[0]["score"]), 0.95)

    def test_simulated_rows_keep_public_schema(self) -> None:
        row = make_row(1, random.Random(7))

        self.assertEqual(set(row), set(FIELDNAMES))
        self.assertEqual(row["candidate_id"], "C0001")
        self.assertIn(row["live_status"], {"ok", "watch", "blocked"})

    def test_ranked_csv_shape(self) -> None:
        rows = [make_row(index, random.Random(index)) for index in range(1, 8)]
        with TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "candidates.csv"
            with input_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
                writer.writeheader()
                writer.writerows(rows)

            ranked = rank_candidates(load_candidates(input_path))

        self.assertEqual(len(ranked), 7)
        self.assertTrue({"score", "action", "gate_reasons", "quality_component"}.issubset(ranked[0]))


if __name__ == "__main__":
    unittest.main()
