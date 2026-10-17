# First weekend review - 15 minutes

This review covers the current Python baseline and the data-source distinction. No new model or subsystem is needed. Agent-run tests and this outline do not establish your understanding.

## Minutes 0-3: say what exists

Open the README and `progress.json`. Explain the difference between the six synthetic fixture bars, the CMU pronunciation resource, and the newly located 36 transcript-file candidate. None supplies a completed human-reviewed battle-rap evaluation. Describe what would still be needed before putting an accuracy claim on your resume.

## Minutes 3-7: trace one input

Use `LEARN_01.md` to trace the fixture's `write/light` pair from the command to the final-word lookup, pronunciation sets, shared sound tail and JSON result. Say why spelling alone is inadequate, why multiple pronunciations matter, and why a missing slang pronunciation is reported as unknown. Refer to the actual functions in `text.py` and `rhyme.py`.

Then trace `bridge river` through `LexicalIndex`. Explain why fixture-05 ranks first using its returned `matched_terms`. Distinguish shared vocabulary from a clever rebuttal. You can use the saved baseline report if running the commands is inconvenient.

## Minutes 7-11: attempt the existing changed exercise

Attempt the `exclude_battle_id` search argument described in `LEARN_01.md`. Work in a separate learning branch or scratch copy. Keep the original behavior when no filter is supplied and test two battles. Do not read an answer before making an attempt. The project has not implemented that exercise for you.

If prerequisite syntax blocks you, identify the first confusing line rather than copying a finished solution. A partial attempt is useful evidence for choosing the next explanation.

## Minutes 11-15: interview explanation

Answer in your own words: “Why start with TF-IDF and a pronunciation dictionary, and what evidence would justify a neural model?” Give the problem, the implementation choice, one alternative, one failure case and an actual test result with its limits. Use the AI-assistance disclosure accurately. Then explain why blank independent labels are needed before measuring real-data quality.

Share your explanation, attempted code and first confusing step when ready. The current learning ledger has no evidence of user review or mastery. Sunday's checkpoint will hold feature expansion until actual review and practice are recorded; the same projects remain active.
