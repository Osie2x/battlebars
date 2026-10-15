"""Tokenize without expanding slang or correcting dialect."""

import re

WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*['’]?", re.UNICODE)


def tokens(text: str) -> list[str]:
    """Keep original text elsewhere; normalize only case and apostrophe shape."""
    return [word.lower().replace("’", "'") for word in WORD.findall(text)]
