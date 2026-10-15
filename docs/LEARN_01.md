# First walkthrough: sounds and search

Allow 10-15 minutes. This is material to practice, not proof you already understand it.

## 1. The problem

A writer wants to inspect possible end rhymes and locate earlier lines about the same words. We need answers whose reasons can be inspected before trying a neural model. Two independent components serve these needs; a bar can be lexically relevant without rhyming.

## 2. Trace one rhyme

Run `battlebars rhyme data/fixtures/verse.txt`. In `cli.py`, the file is read as text and passed to `analyze` in `rhyme.py`.

1. `splitlines()` creates a list. `enumerate()` records each original line number, starting at zero; adding one gives human-readable numbers.
2. `tokens()` in `text.py` finds words and returns a Python list. `[-1]` selects the final item, after checking that the list is nonempty.
3. The dictionary maps a word to a list of possible pronunciations. `write` has sounds ending in `AY1 T`; `light` also ends in `AY1 T`.
4. `rhyme_keys()` starts at the last stressed vowel, removes stress numbers and stores each possible tail as a tuple inside a set. A tuple is immutable; a set makes membership and intersection convenient.
5. `a_keys & b_keys` is the set intersection: sounds available for both words. Here it contains `AY T`.
6. The JSON result says `dictionary_rhyme_candidate`, retaining the sound tail. It does not say the verse is good. `lru_cache` loads the large dictionary once per process, instead of once per comparison.

Pause and explain why comparing the last three letters would fail for `through/blue`. Then explain what the tool should do when a slang word is missing.

## 3. Trace one search

Run `battlebars search data/fixtures/bars.json 'bridge river' --k 2`.

`load_corpus()` first checks the corpus label, source metadata and bar IDs. A `Counter` then maps each word to how many times it occurs. A dictionary comprehension builds IDF weights based on how many indexed bars contain a word. Query words never change those weights.

Think of each bar as a vector: one coordinate per word. Repeated/common words and rare words get different weights. L2 normalization rescales each vector to length one, so long bars do not automatically win by having more words. Multiplying corresponding query/bar coordinates and summing gives cosine similarity.

Fixture-05 contains both `bridge` and `river`; fixture-01 contains `bridge`. Inspect the returned scores and `matched_terms`. They explain lexical overlap, not whether the bar is a clever rebuttal. A query with no shared words returns an empty list.

## 4. Why these choices, and where they fail

Python and small functions keep the implementation traceable. A pronunciation dictionary handles sounds better than spelling; embeddings could retrieve paraphrases but would add a model and require a real relevance benchmark. This baseline cannot hear delivery or infer punchlines. The dictionary can miss slang and actual pronunciation. A successful fixture test does not measure real-world accuracy.

## 5. Interview question

“Why begin with TF-IDF instead of a transformer, and what evidence would justify upgrading?”

Try answering in your own words: problem, simple baseline, one observed limitation, the held-out comparison you would need. Do not invent metrics or users. Also distinguish implementing this code with AI assistance from independently understanding it.

## 6. Your independent exercise

Add an optional `exclude_battle_id` argument to `LexicalIndex.search`. When supplied, results from that battle must be omitted. Missing `battle_id` should not make a result crash. Existing behavior with no argument should stay the same. Add a test with two bars from different battles and show which one remains.

Do not change TF-IDF fitting for this exercise: filtering results and rebuilding the index are different decisions. Before coding, predict where the condition belongs. Then explain your change and why this filter alone would not prevent train/test leakage in an evaluation.

The solution is intentionally not supplied. Share your first attempt for feedback on the first step that needs repair. Reading this guide or passing agent-run tests does not close the learning gate.
