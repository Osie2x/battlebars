"""Prepare unlabelled rhyme-pair sheets; never invent human judgments."""

import hashlib
import itertools
import json
import random
from collections import defaultdict
from pathlib import Path

from battlebars.corpus import load_corpus
from battlebars.text import tokens

MAX_BARS = 500


def prepare_review(path: Path, reviewer: str, limit: int = 50, seed: int = 17) -> dict:
    """Select the same cases for both reviewers; shuffle their presentation order.

    Pairs are sampled from all bar combinations, not only model-positive pairs.
    The cap bounds this deliberately simple O(n^2) preparation baseline.
    """
    if reviewer not in {"A", "B"}:
        raise ValueError("reviewer must be A or B")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    corpus = load_corpus(path)
    bars = sorted(corpus["bars"], key=lambda row: row["id"])
    if not 2 <= len(bars) <= MAX_BARS:
        raise ValueError(f"review preparation requires 2 to {MAX_BARS} bars")

    # Hash exactly the same source bytes whose contents load_corpus validated.
    # Re-read detection avoids silently binding labels to a changed file.
    content = path.read_bytes()
    if json.loads(content) != corpus:
        raise ValueError("corpus changed during review preparation; retry")
    fingerprint = hashlib.sha256(content).hexdigest()
    normalized = defaultdict(list)
    tokenless = []
    for bar in bars:
        key = " ".join(tokens(bar["text"]))
        if key:
            normalized[key].append(bar["id"])
        else:
            tokenless.append(bar["id"])

    # Reservoir sampling retains at most 'limit' pairs in memory, with uniform
    # inclusion probabilities. Sorting IDs makes selection independent of row order.
    rng = random.Random(seed)
    selected = []
    total = 0
    for index, pair in enumerate(itertools.combinations(bars, 2)):
        total = index + 1
        if index < limit:
            selected.append(pair)
        else:
            slot = rng.randrange(index + 1)
            if slot < limit:
                selected[slot] = pair
    items = []
    for left, right in selected:
        identity = json.dumps([fingerprint, left["id"], right["id"]], ensure_ascii=False)
        items.append({
            "case_id": hashlib.sha256(identity.encode()).hexdigest(),
            "left": {key: left[key] for key in ("id", "text", "battle_id", "performer_id")},
            "right": {key: right[key] for key in ("id", "text", "battle_id", "performer_id")},
            "human_label": None,
            "notes": "",
        })
    # Separate RNG: reviewer order cannot affect which pairs were selected.
    random.Random(f"{seed}:{reviewer}").shuffle(items)
    return {
        "schema_version": 1,
        "task": "end_rhyme_pair_review",
        "reviewer": reviewer,
        "corpus_kind": corpus["corpus_kind"],
        "corpus_sha256": fingerprint,
        "source_declaration": corpus["source"],
        "seed": seed,
        "population_pairs": total,
        "selected_pairs": len(items),
        "sampling": "uniform reservoir over all unordered pairs; no model-based selection",
        "allowed_labels": ["rhyme", "no_rhyme", "uncertain", "repeated_word"],
        "instructions": "Judge ending sounds, not artistic quality. Label uncertain when text cannot establish pronunciation. Work independently; do not inspect model output or the other reviewer's labels.",
        "quality_flags": {
            "normalized_duplicate_groups": sorted(group for group in normalized.values() if len(group) > 1),
            "tokenless_bar_ids": tokenless,
            "scope": "exact duplicates after lookup token normalization only; near-duplicates and split leakage still need review",
        },
        "human_labels_completed": 0,
        "quality_metrics": None,
        "items": items,
    }
