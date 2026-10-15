"""Dictionary-based exact end-rhyme candidates, not a performance score."""

from functools import lru_cache

import cmudict

from battlebars.text import tokens


@lru_cache(maxsize=1)
def dictionary() -> dict[str, list[list[str]]]:
    return cmudict.dict()


def rhyme_keys(word: str) -> set[tuple[str, ...]]:
    """All tails from the last stressed vowel, or last vowel if unstressed."""
    keys = set()
    for pronunciation in dictionary().get(word, []):
        stressed = [i for i, phone in enumerate(pronunciation) if phone[-1:] in {"1", "2"}]
        vowels = [i for i, phone in enumerate(pronunciation) if phone[-1:] in {"0", "1", "2"}]
        if stressed or vowels:
            index = (stressed or vowels)[-1]
            keys.add(tuple(phone.rstrip("012") for phone in pronunciation[index:]))
    return keys


def compare(left: str, right: str) -> dict:
    left_tokens, right_tokens = tokens(left), tokens(right)
    a = left_tokens[-1] if left_tokens else None
    b = right_tokens[-1] if right_tokens else None
    a_keys, b_keys = rhyme_keys(a) if a else set(), rhyme_keys(b) if b else set()
    shared = sorted(a_keys & b_keys)
    if a is None or b is None:
        status = "empty_line"
    elif not a_keys or not b_keys:
        status = "unknown_pronunciation"
    elif a == b:
        status = "repeated_word"
    elif shared:
        status = "dictionary_rhyme_candidate"
    else:
        status = "no_exact_dictionary_rhyme"
    return {
        "left_end": a,
        "right_end": b,
        "status": status,
        "shared_rhyme_tails": [list(key) for key in shared],
        "unknown_words": sorted({word for word, keys in [(a, a_keys), (b, b_keys)] if word and not keys}),
    }


def analyze(text: str) -> dict:
    lines = [{"line_number": i + 1, "text": line} for i, line in enumerate(text.splitlines()) if line.strip()]
    endings = {words[-1] for line in lines if (words := tokens(line["text"]))}
    pairs = [
        {"line_numbers": [a["line_number"], b["line_number"]], **compare(a["text"], b["text"])}
        for a, b in zip(lines, lines[1:])
    ]
    return {
        "method": "adjacent nonblank lines; dictionary end-rhyme candidates",
        "lines": lines,
        "pairs": pairs,
        "unknown_end_words": sorted(word for word in endings if not rhyme_keys(word)),
        "limitations": "Dictionary pronunciations may differ from delivery; no slant-rhyme, flow, punchline or winner score.",
    }
