import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from battlebars.corpus import load_corpus
from battlebars.retrieval import LexicalIndex
from battlebars.rhyme import analyze, compare
from battlebars.text import tokens

ROOT = Path(__file__).resolve().parents[1]


class RhymeTests(unittest.TestCase):
    def test_sound_not_spelling(self):
        self.assertEqual(compare("through", "blue")["status"], "dictionary_rhyme_candidate")
        self.assertEqual(compare("cough", "though")["status"], "no_exact_dictionary_rhyme")

    def test_all_pronunciation_variants_are_considered(self):
        self.assertEqual(compare("read", "red")["status"], "dictionary_rhyme_candidate")

    def test_repeated_word_is_not_counted_as_a_rhyme(self):
        self.assertEqual(compare("night", "NIGHT!")["status"], "repeated_word")

    def test_unknown_is_not_a_negative_judgment(self):
        result = compare("my zzzinventedbar", "your star")
        self.assertEqual(result["status"], "unknown_pronunciation")
        self.assertEqual(result["unknown_words"], ["zzzinventedbar"])

    def test_empty_and_punctuation_only(self):
        self.assertEqual(compare("!!!", "night")["status"], "empty_line")
        self.assertEqual(analyze("")["pairs"], [])

    def test_single_line_still_reports_unknown_ending(self):
        self.assertEqual(analyze("a zzzinventedbar")["unknown_end_words"], ["zzzinventedbar"])

    def test_original_lines_and_numbers_are_retained(self):
        result = analyze("Bright LIGHT!\n\nDark night")
        self.assertEqual(result["lines"][0]["text"], "Bright LIGHT!")
        self.assertEqual(result["pairs"][0]["line_numbers"], [1, 3])

    def test_dialect_not_rewritten(self):
        self.assertEqual(tokens("I ain’t changin' my WORDS"), ["i", "ain't", "changin'", "my", "words"])


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.index = LexicalIndex([
            {"id": "b", "text": "bridge river"},
            {"id": "a", "text": "clock beat"},
            {"id": "c", "text": "bridge river"},
        ])

    def test_exact_match_and_explanation(self):
        result = self.index.search("CLOCK beat", 1)[0]
        self.assertEqual(result["id"], "a")
        self.assertAlmostEqual(result["cosine_similarity"], 1.0)
        self.assertEqual(result["matched_terms"], ["beat", "clock"])

    def test_no_overlap_and_empty_queries_return_nothing(self):
        for query in ("", "!!!", "zzzinventedbar"):
            self.assertEqual(self.index.search(query), [])

    def test_stable_ties_and_k(self):
        self.assertEqual([row["id"] for row in self.index.search("bridge", 2)], ["b", "c"])

    def test_reject_nonpositive_k(self):
        with self.assertRaises(ValueError):
            self.index.search("bridge", 0)

    def test_empty_corpus_and_documents(self):
        self.assertEqual(LexicalIndex([]).search("bridge"), [])
        self.assertEqual(LexicalIndex([{"id": "x", "text": "!!!"}]).search("bridge"), [])

    def test_unknown_query_terms_do_not_create_fake_results(self):
        self.assertEqual(self.index.search("clock unknownnewterm"), self.index.search("clock"))


class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.corpus = load_corpus(ROOT / "data/fixtures/bars.json")

    def load_modified(self, corpus):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "corpus.json"
            path.write_text(json.dumps(corpus), encoding="utf-8")
            return load_corpus(path)

    def test_fixture_label_and_count(self):
        self.assertEqual(self.corpus["corpus_kind"], "synthetic_fixture")
        self.assertEqual(len(self.corpus["bars"]), 6)

    def test_reject_missing_provenance(self):
        del self.corpus["source"]["permission_note"]
        with self.assertRaises(ValueError):
            self.load_modified(self.corpus)

    def test_reject_unknown_kind(self):
        self.corpus["corpus_kind"] = "scraped_unreviewed"
        with self.assertRaises(ValueError):
            self.load_modified(self.corpus)

    def test_reject_duplicate_ids_and_invalid_rows(self):
        for key, value in (("id", "fixture-01"), ("text", ""), ("performer_id", None)):
            corpus = copy.deepcopy(self.corpus)
            corpus["bars"][1][key] = value
            with self.assertRaises(ValueError):
                self.load_modified(corpus)


class CommandTests(unittest.TestCase):
    def test_search_exposes_fixture_status(self):
        result = subprocess.run(
            [sys.executable, "-m", "battlebars.cli", "search", "data/fixtures/bars.json", "bridge"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["corpus_kind"], "synthetic_fixture")
        self.assertEqual(len(data["matches"]), 2)

    def test_invalid_k_is_clean_command_error(self):
        result = subprocess.run(
            [sys.executable, "-m", "battlebars.cli", "search", "data/fixtures/bars.json", "bridge", "--k", "0"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("k must be positive", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
