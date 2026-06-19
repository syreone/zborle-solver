import argparse
from generator import load_corpus, build_stats, generate_candidates
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description="Build candidates.txt from corpus.")
    p.add_argument("--corpus", default="words-mk-main/all", help="Path to corpus file")
    p.add_argument("--out", default="candidates.txt", help="Output candidates file")
    args = p.parse_args()

    words = load_corpus(args.corpus)
    stats = build_stats(words)
    candidates = generate_candidates(stats)

    out_path = Path(args.out)
    with out_path.open("w", encoding="utf-8") as f:
        for w in candidates:
            f.write(w + "\n")
    print(f"Wrote {len(candidates)} candidates to {out_path}")

if __name__ == "__main__":
    main()
