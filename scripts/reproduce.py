"""Record exact resource identity and fixture behavior, never corpus accuracy."""

import hashlib
import importlib.metadata
import json
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import cmudict

from battlebars.corpus import load_corpus
from battlebars.retrieval import LexicalIndex
from battlebars.rhyme import analyze, dictionary

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    corpus_file = ROOT / "data/fixtures/bars.json"
    corpus = load_corpus(corpus_file)
    index = LexicalIndex(corpus["bars"])
    start = time.perf_counter()
    lexicon = dictionary()
    cold_load_ms = 1000 * (time.perf_counter() - start)
    elapsed = []
    for _ in range(30):
        start = time.perf_counter()
        index.search("bridge river", 2)
        elapsed.append(1000 * (time.perf_counter() - start))
    dict_path = Path(cmudict.__file__).parent / "data/cmudict.dict"
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "resource": {
            "package": "cmudict", "version": importlib.metadata.version("cmudict"),
            "dictionary_bytes": dict_path.stat().st_size,
            "dictionary_sha256": sha256(dict_path),
            "unique_dictionary_keys": len(lexicon),
            "pronunciation_entries": sum(map(len, lexicon.values())),
            "role": "real pronunciation resource, NOT a battle-rap corpus",
        },
        "fixture": {"sha256": sha256(corpus_file), "kind": corpus["corpus_kind"], "bars": len(corpus["bars"])},
        "retrieval_example": index.search("bridge river", 2),
        "rhyme_example": analyze((ROOT / "data/fixtures/verse.txt").read_text()),
        "timing": {
            "dictionary_first_load_ms": cold_load_ms,
            "retrieval_warm_runs": 30,
            "retrieval_median_ms": statistics.median(elapsed),
            "scope": "single local process; six synthetic bars; excludes dictionary load and CLI startup; not service latency",
        },
        "real_battle_corpus_records_ingested": 0,
        "human_reviewed_evaluation_cases": 0,
        "real_data_quality_metrics": None,
    }
    output = ROOT / "reports/baseline-2026-10-15.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(output.name)


if __name__ == "__main__":
    main()
