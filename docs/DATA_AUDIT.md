# Data audit - October 15, 2026

## Accepted resource: pronunciation dictionary

Original source: [CMUdict](https://github.com/cmusphinx/cmudict), maintained by Carnegie Mellon University's Speech Group. Installed via [python-cmudict](https://github.com/prosegrinder/python-cmudict), package **1.1.3**, from PyPI. Original upstream snapshot inside this wrapper is identified by its file checksum rather than an inferred upstream commit.

Actual installed `cmudict.dict`: **3,618,488 bytes**, SHA-256 `81917843c7f44ce2b094ac63873c2c7a4cf802040792c455ba3ca406891c3d22`. Parsed by the wrapper: **126,052 unique keys**, **135,166 pronunciation entries**. Recompute using `python scripts/reproduce.py`.

The original dictionary [license](https://github.com/cmusphinx/cmudict/blob/master/LICENSE) allows source/binary redistribution with its notices and disclaimer retained (BSD-style). Its [README](https://github.com/cmusphinx/cmudict/blob/master/README) requests attribution and explicitly acknowledges errors/omissions. The Python wrapper is separately GPL-3.0-or-later; it is not BSD merely because the dictionary is. See third-party notices and the installed packages' licenses. This resource supplies word pronunciations; it supplies **no real battle bars**.

## Candidate sources not ingested

| Source | Observed evidence | Decision |
| --- | --- | --- |
| [DopeLearning repository](https://github.com/ekQ/dopelearning) | README lists anonymized usage logs and 100 generated verses for the published experiments; repository displays an MIT license. | Prior work, not an authenticated corpus of human battle transcripts. No archive ingested. Repository code license is not assumed to establish redistribution permission for every underlying lyric. |
| [Entropy of Sounds: Sonnets to Battle Rap](https://escholarship.org/uc/item/8906q5vt) | Search metadata describes transcribed battle rap; direct article page requires browser verification. | Research lead only. No corpus archive, version, accessible record count or corpus-specific redistribution permission verified. No text ingested. A paper's license does not automatically license its source transcripts. |
| General online lyric/transcript pages | Search surfaced transcript and generated-battle pages. | Neither visibility nor automatic captions establishes corpus rights or transcription quality. No scraping or redistribution. |

This is a bounded source search, not proof that no suitable public corpus exists. Current accepted real battle corpus count is **0**.

## Fixtures and contribution path

`data/fixtures/bars.json` has six original AI-authored demonstration lines across three fictional battles. It is marked `synthetic_fixture` in the file and in every search result. There are no copied artist lyrics, real performers or human relevance judgments. Its checksum is in the baseline report. These lines validate plumbing only.

For real material, start with explicitly permissioned original human-written battle/practice bars. Contributors must identify that they own the words and whether they permit public code-repository redistribution and evaluation. Do not infer permission to publish from permission to process privately. Keep contributed text in ignored `data/private/` until that distinction is resolved; never commit personal contact information. No outreach is authorized by this plan.

The corpus loader expects the same JSON structure as the fixture, with `corpus_kind: permissioned_real` and source `origin`, `license_or_permission`, `reviewed_on`, `permission_note`. Each bar needs an ID, original text, battle ID and pseudonymous performer ID. Validation checks presence/shape, not the legal truth of a declaration. Preserve provenance and permission evidence separately and review them before import/publication.

## Evaluation before model claims

1. Record permission, source version/date and checksums; inspect transcription and preserve dialect/slang. Record uncertain pronunciations instead of automatically correcting them.
2. Have humans independently review rhyme candidates and query/bar relevance; reconcile disagreements separately from the initial judgments. Never use an LLM's agreement as gold accuracy.
3. Freeze a development/test separation by whole battle, audit duplicate and near-duplicate lines, and avoid performer overlap for a separate performer-generalization check where feasible. If connected shared performers make a clean split impossible at this size, report that limitation rather than inventing a disjoint test set.
4. Only then compute task metrics: rhyme precision/recall with unknown coverage, retrieval Recall@k or MRR with actual relevance labels. Record dataset sizes and split membership. No such metrics exist today.
