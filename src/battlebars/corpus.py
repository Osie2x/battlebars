"""Load locally supplied, explicitly labeled corpora; never scrape lyrics."""

import json
from pathlib import Path


def load_corpus(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("corpus_kind") not in {"synthetic_fixture", "permissioned_real"}:
        raise ValueError("corpus_kind must be synthetic_fixture or permissioned_real")
    source = data.get("source")
    if not isinstance(source, dict) or any(
        not isinstance(source.get(key), str) or not source[key].strip()
        for key in ("origin", "license_or_permission", "reviewed_on", "permission_note")
    ):
        raise ValueError("source must record origin, license_or_permission, reviewed_on and permission_note")
    bars = data.get("bars")
    if not isinstance(bars, list):
        raise ValueError("bars must be a list")
    ids = set()
    for bar in bars:
        if not isinstance(bar, dict) or any(
            not isinstance(bar.get(key), str) or not bar[key].strip()
            for key in ("id", "text", "battle_id", "performer_id")
        ):
            raise ValueError("each bar needs nonempty id, text, battle_id and performer_id")
        if bar["id"] in ids:
            raise ValueError("duplicate bar id")
        ids.add(bar["id"])
    return data
