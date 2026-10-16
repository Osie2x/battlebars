import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from battlebars.corpus import load_corpus
from battlebars.review import prepare_review

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data/fixtures/bars.json"


class ReviewTests(unittest.TestCase):
    def with_corpus(self, data, **kwargs):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bars.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return prepare_review(path, "A", **kwargs)

    def test_complete_population_and_no_self_pairs(self):
        packet = prepare_review(FIXTURE, "A", limit=50)
        self.assertEqual(packet["population_pairs"], 15)
        self.assertEqual(packet["selected_pairs"], 15)
        pairs = {(row["left"]["id"], row["right"]["id"]) for row in packet["items"]}
        self.assertEqual(len(pairs), 15)
        self.assertTrue(all(a != b for a, b in pairs))

    def test_same_sample_for_reviewers_and_independent_order(self):
        a = prepare_review(FIXTURE, "A", limit=8)
        b = prepare_review(FIXTURE, "B", limit=8)
        ids_a = [row["case_id"] for row in a["items"]]
        ids_b = [row["case_id"] for row in b["items"]]
        self.assertEqual(set(ids_a), set(ids_b))
        self.assertNotEqual(ids_a, ids_b)
        self.assertEqual(a, prepare_review(FIXTURE, "A", limit=8))

    def test_no_labels_predictions_or_accuracy_are_fabricated(self):
        packet = prepare_review(FIXTURE, "A")
        self.assertEqual(packet["corpus_kind"], "synthetic_fixture")
        self.assertEqual(packet["human_labels_completed"], 0)
        self.assertIsNone(packet["quality_metrics"])
        for row in packet["items"]:
            self.assertIsNone(row["human_label"])
            self.assertEqual(set(row), {"case_id", "left", "right", "human_label", "notes"})

    def test_exact_file_identity_and_original_text(self):
        packet = prepare_review(FIXTURE, "A")
        self.assertEqual(packet["corpus_sha256"], hashlib.sha256(FIXTURE.read_bytes()).hexdigest())
        originals = {row["id"]: row for row in load_corpus(FIXTURE)["bars"]}
        for item in packet["items"]:
            for side in ("left", "right"):
                self.assertEqual(item[side], originals[item[side]["id"]])

    def test_duplicate_and_tokenless_flags(self):
        corpus = load_corpus(FIXTURE)
        corpus["bars"][1]["text"] = corpus["bars"][0]["text"].upper() + "!!!"
        corpus["bars"][2]["text"] = "!!!"
        packet = self.with_corpus(corpus)
        self.assertEqual(packet["quality_flags"]["normalized_duplicate_groups"], [["fixture-01", "fixture-02"]])
        self.assertEqual(packet["quality_flags"]["tokenless_bar_ids"], ["fixture-03"])

    def test_invalid_bounds(self):
        for args in (("C", 5), ("A", 0), ("A", -1), ("A", 101)):
            with self.assertRaises(ValueError):
                prepare_review(FIXTURE, args[0], args[1])
        corpus = load_corpus(FIXTURE)
        for bars in ([], corpus["bars"][:1], [dict(corpus["bars"][0], id=str(i)) for i in range(501)]):
            data = copy.deepcopy(corpus)
            data["bars"] = bars
            with self.assertRaises(ValueError):
                self.with_corpus(data)

    def test_changed_corpus_has_new_case_identifiers(self):
        corpus = load_corpus(FIXTURE)
        before = self.with_corpus(corpus)
        corpus["bars"][0]["text"] += " changed"
        after = self.with_corpus(corpus)
        self.assertTrue({row["case_id"] for row in before["items"]}.isdisjoint(
            {row["case_id"] for row in after["items"]}))

    def test_source_change_during_preparation_is_rejected(self):
        altered = load_corpus(FIXTURE)
        altered["bars"][0]["text"] += " changed"
        with patch.object(Path, "read_bytes", return_value=json.dumps(altered).encode()):
            with self.assertRaisesRegex(ValueError, "changed during"):
                prepare_review(FIXTURE, "A")

    def test_extra_row_fields_are_not_copied_to_review_sheets(self):
        corpus = load_corpus(FIXTURE)
        corpus["bars"][0]["private_contact"] = "private fixture field"
        packet = self.with_corpus(corpus)
        for case in packet["items"]:
            for side in ("left", "right"):
                self.assertEqual(set(case[side]), {"id", "text", "battle_id", "performer_id"})

    def test_cli_can_prepare_both_sheets(self):
        for reviewer in ("A", "B"):
            result = subprocess.run([sys.executable, "-m", "battlebars.cli", "review", str(FIXTURE),
                                     "--reviewer", reviewer, "--limit", "3"], capture_output=True, text=True, check=True)
            packet = json.loads(result.stdout)
            self.assertEqual(packet["reviewer"], reviewer)
            self.assertEqual(packet["selected_pairs"], 3)

    def test_malformed_kind_is_a_clean_validation_error(self):
        corpus = load_corpus(FIXTURE)
        corpus["corpus_kind"] = ["permissioned_real"]
        with self.assertRaisesRegex(ValueError, "corpus_kind"):
            self.with_corpus(corpus)


if __name__ == "__main__":
    unittest.main()
