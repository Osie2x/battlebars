# BattleBars

An explainable NLP prototype for battle-rap fans and writers: inspect end-rhyme candidates and find bars that share vocabulary with a query. The first milestone is a small Python command-line tool. It is not a deployed app or a trained battle-rap judge.

## Try it

Python 3.11+; no API key, cloud account or GPU required. From this repository:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m pip install --no-deps -e .
battlebars rhyme data/fixtures/verse.txt
battlebars search data/fixtures/bars.json 'bridge river' --k 2
python -m unittest discover -s tests -v
python scripts/reproduce.py
battlebars review data/fixtures/bars.json --reviewer A --limit 3
```

On Windows use `.venv\Scripts\activate` instead. Installation needs network access; analysis and retrieval then run locally. The examples use six **AI-authored synthetic fixtures**, never real artist lyrics. For your own verse, save a UTF-8 text file and pass its path to `battlebars rhyme`.

The sample finds `write/light` and `beat/street` as dictionary rhyme candidates. Searching `bridge river` ranks fixture-05 first, showing the matching words and cosine similarity. A similarity is not a probability. No-overlap queries return no matches.

## Where the battle-rap data stands

On October 17, the source search located [jordanmasters/rhyme-data](https://github.com/jordanmasters/rhyme-data), which lists **36 battle-transcript files** attributed to Battlerap.com. A [pinned metadata inventory](reports/source-candidate-rhyme-data-2026-10-17.json) records their names, sizes and Git blob hashes. One file was inspected outside this repository to verify access and its hash. No explicit corpus license/permission statement was found, so these transcripts have **not** been imported, redistributed or used for model evaluation. The six examples shipped here remain synthetic. See [the source audit](docs/DATA_AUDIT.md) for the distinction between a located source and an accepted dataset.

## How it works

```text
UTF-8 verse -> tokens -> last word -> all CMU pronunciations -> matching sound tails
                                              -> candidate / unknown / repeated word

Labeled local corpus -> source/row validation -> TF-IDF index
Query -> same tokenization -> cosine comparison -> ranked bars + matching words
```

Original text is retained. Lookup normalizes case/apostrophe shape but does not expand slang or rewrite dialect. Terminal apostrophes such as `changin'` survive; dictionary gaps are reported. Only adjacent nonblank lines are compared, including across blank separators. Quotation-mark apostrophes and hyphenated words can need manual inspection.

## Evidence and limits

- October 15 local baseline: **20 tests passed**. [Saved output](reports/tests-2026-10-15.txt).
- October 16 review preparation: **31 total tests passed**. [Saved output](reports/tests-2026-10-16.txt). The new `review` command prepares blank human-label sheets and flags normalized duplicate text; it does not run an evaluation.
- [Reproducible report](reports/baseline-2026-10-15.json) records resource hashes, actual dictionary size, fixture outputs and narrowly scoped local timing.
- Real battle-rap records ingested: **0**. Human-reviewed evaluation cases: **0**. No accuracy, retrieval-quality or artistic-quality result is established.
- CMUdict is a real pronunciation resource, not a real battle-rap dataset. Pronunciation, delivery, slant rhymes and context may disagree with this baseline. Unknown words are not bad rhymes. Text alone does not establish spoken flow or the winner.
- Lexical retrieval misses paraphrases. The present implementation scans all documents; it is a teaching baseline, not a scalable search service.
- CI configuration is included. Check actual Actions results before claiming hosted checks passed. No API, database, Docker image or public demo has been built yet.

## Read and learn

Start with [the first walkthrough](docs/LEARN_01.md), then [implementation decisions](docs/DECISIONS.md) and [the data audit](docs/DATA_AUDIT.md). The walkthrough includes one interview question and an independent coding exercise, with no answer shown.

[Preparing a human review](docs/HUMAN_REVIEW.md) explains two independent review sheets, source identity, sampling limitations and the short October 16 exercise. [Example output](reports/review-fixture-2026-10-16.json) is synthetic and unlabelled. Do not show it to reviewers of a real dataset as a source of answers.

For the first weekend, use [the 15-minute review outline](docs/WEEKEND_REVIEW.md). Human review and the independent exercise are still pending.

Next: obtain explicitly permissioned original battle bars, review annotations independently, and compare this baseline on held-out material before adding models or a web API. Keep one milestone small enough to explain. A weekly learning checkpoint gates feature expansion.

## Credits and assistance

Osie's project direction and learning goals; the initial implementation, fixtures, tests and documentation were generated by Codex on October 15, 2026. Human code review and independent practice remain pending. No private research data or collaborator code is included.

The pronunciation dictionary originates at Carnegie Mellon University. The Python `cmudict` wrapper is maintained by David L. Day. See [third-party notices](THIRD_PARTY_NOTICES.md). This software is provided under GPL-3.0-or-later; see [LICENSE](LICENSE). Incoming real data must retain its own verified permission and attribution.
