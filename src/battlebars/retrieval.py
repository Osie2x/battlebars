"""Small TF-IDF/cosine baseline whose matched terms can be inspected."""

import math
from collections import Counter

from battlebars.text import tokens


class LexicalIndex:
    def __init__(self, bars: list[dict]):
        self.bars = bars
        counts = [Counter(tokens(bar["text"])) for bar in bars]
        frequencies = Counter(term for row in counts for term in row)
        self.idf = {term: math.log((1 + len(bars)) / (1 + count)) + 1 for term, count in frequencies.items()}
        self.vectors = [self._vector(row) for row in counts]

    def _vector(self, counts: Counter) -> dict[str, float]:
        # Terms absent from this corpus contribute no information to this index.
        weights = {term: count * self.idf[term] for term, count in counts.items() if term in self.idf}
        norm = math.sqrt(sum(weight * weight for weight in weights.values()))
        return {term: weight / norm for term, weight in weights.items()} if norm else {}

    def search(self, query: str, k: int = 5) -> list[dict]:
        if k < 1:
            raise ValueError("k must be positive")
        query_vector = self._vector(Counter(tokens(query)))
        matches = []
        for bar, vector in zip(self.bars, self.vectors):
            shared = sorted(query_vector.keys() & vector.keys())
            score = sum(query_vector[term] * vector[term] for term in shared)
            if score > 0:
                matches.append({**bar, "cosine_similarity": round(min(score, 1.0), 8), "matched_terms": shared})
        return sorted(matches, key=lambda row: (-row["cosine_similarity"], row["id"]))[:k]
