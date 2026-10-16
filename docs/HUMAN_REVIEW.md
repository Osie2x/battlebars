# Prepare human review without manufacturing gold data

The October 16 addition prepares a small **end-rhyme pair** annotation task. It does not evaluate retrieval, sequence coherence, artistic quality, or who won a battle. No human judgments have been collected.

## Workflow

First use the six synthetic fixture bars to inspect the format:

```sh
battlebars review data/fixtures/bars.json --reviewer A --limit 3
```

After installation, it runs locally and makes no network calls. It returns JSON with original bar text, corpus kind and checksum, two bar IDs per case, a blank `human_label` and `notes`. Model predictions and scores are deliberately absent. The command writes only to stdout; it does not publish, contact reviewers, or edit the corpus.

For permissioned real bars, inspect the provenance and ownership/redistribution permission first. Use a separate corpus file for each source/permission declaration; the current schema has one declaration per corpus. Private processing permission does not imply public redistribution permission. The loader cannot verify that a declaration is truthful.

Prepare sheets locally, keeping the same corpus bytes, seed and limit for both:

```sh
mkdir -p data/private/reviews
battlebars review data/private/bars.json --reviewer A --seed 17 --limit 50 > data/private/reviews/reviewer-a.json
battlebars review data/private/bars.json --reviewer B --seed 17 --limit 50 > data/private/reviews/reviewer-b.json
```

These commands require an actual `data/private/bars.json`; none is supplied or inferred. `data/private/` is ignored by Git. Shell redirection replaces an existing file, so use new filenames for each version and never rerun over completed labels. Keep sheets separate when reviewers work. Preparing them does not authorize sending them to anyone.

## Label rubric

Decide before reviewing whether the final stressed vowel and following sounds form an end rhyme under a plausible reading. Use text and, only if available and permitted, the corresponding audio. Do not force dictionary pronunciation on dialect or slang.

- `rhyme`: ending sounds rhyme under the recorded reading. Note that reading when ambiguous.
- `no_rhyme`: clearly different ending sounds under that reading.
- `uncertain`: pronunciation, missing audio, slant rhyme or ambiguity prevents a firm judgment; explain why. Do not silently count uncertainty as a negative.
- `repeated_word`: the same lexical ending is repeated; keep separate from distinct-word rhymes.

Each reviewer fills only their own sheet, without inspecting model output or the other's labels. Preserve the original independent labels; create a separate reconciliation record for disagreements. Human agreement measures consistency, not accuracy. The model's prediction cannot supply a missing human answer.

## What the sample means

The command considers **all unordered pairs** among at most 500 bars, including different battles and performers; these are comparison cases, not claims of adjacent performance lines. A uniform reservoir sample selects at most 100 pairs without selecting on dictionary output. The six-bar fixture has 15 possible pairs. Each reviewer gets the same selected cases, independently shuffled; tiny samples can coincidentally have the same order. Matching case IDs, not row positions, link their labels.

All-pair sampling can be dominated by obvious negatives and is not a representative estimate of adjacent in-battle rhyme quality. A later benchmark should define its target population, intentionally include challenging/unknown cases, and report each stratum separately. Do not call the generated packet a balanced or representative benchmark.

Duplicate flags group text equal after lookup token normalization (case/apostrophe/punctuation handling). They do not detect all near-duplicates. Review tokenless lines and duplicate flags manually; do not discard dialectal spelling or genuine repeated quotations automatically. Freeze whole-battle development/test boundaries and audit performer/duplicate overlap before model tuning. Review preparation does not create those splits or prove that leakage is absent.

Any corpus-byte change produces a new checksum and new case IDs. Keep the original corpus immutable during annotation. A checksum establishes which bytes were used; it proves neither permission nor correctness. The command checks for changes between loading and fingerprinting.

## Trace and practice: 10-15 minutes

Trace `cli.py` to `prepare_review()` in `review.py`: validation -> sorted IDs -> file fingerprint -> duplicate flags -> pair sampling -> blank cases -> reviewer-specific ordering. `itertools.combinations` enumerates each pair once. A seeded random generator makes a selection reproducible. Reservoir sampling keeps the sample small while scanning the candidate stream; a second random generator changes presentation order without changing selected membership.

Run the command twice with reviewer A, then once with B, using identical seed/limit. Explain which fields should stay identical and which may change. Predict the number of possible pairs if you supplied **four** bars before running a changed fixture in a temporary file. Leave human labels blank for this format exercise.

Interview prompt: “Why would evaluating only the pairs your rhyme detector flags make the results misleading?” Explain false negatives and what independent labels add. Then explain why two humans agreeing still does not establish an objective answer.

Your previous independent coding exercise in `LEARN_01.md` remains pending; this command does not implement its answer or count as your practice. User review and mastery remain unverified.
