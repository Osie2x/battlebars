"""Local commands: JSON output keeps explanations and data labels visible."""

import argparse
import json
from pathlib import Path

from battlebars.corpus import load_corpus
from battlebars.retrieval import LexicalIndex
from battlebars.rhyme import analyze


def main() -> None:
    parser = argparse.ArgumentParser(description="BattleBars transparent NLP baselines")
    commands = parser.add_subparsers(dest="command", required=True)
    rhyme = commands.add_parser("rhyme", help="Analyze end rhymes in a UTF-8 text file")
    rhyme.add_argument("file", type=Path)
    search = commands.add_parser("search", help="Retrieve bars by shared vocabulary")
    search.add_argument("corpus", type=Path)
    search.add_argument("query")
    search.add_argument("--k", type=int, default=5)
    args = parser.parse_args()
    try:
        if args.command == "rhyme":
            result = analyze(args.file.read_text(encoding="utf-8"))
        else:
            corpus = load_corpus(args.corpus)
            result = {
                "corpus_kind": corpus["corpus_kind"],
                "source": corpus["source"],
                "method": "TF-IDF cosine; lexical overlap, not semantic relevance or probability",
                "matches": LexicalIndex(corpus["bars"]).search(args.query, args.k),
            }
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
