# zborle-solver

A Wordle-style solver and candidate generator for Macedonian 5-letter words.

Generates plausible candidate words from a corpus using positional bigram/trigram
adjacency rules and phonotactic filters (no hardcoded answer list), then uses an
entropy-based solver to pick the most informative guess at each step, based on game
feedback (green/yellow/gray).

### Features

- Rule-based candidate generator (bigrams/trigrams, vowel & rare-letter filters)
- Entropy-based solver with positional-frequency prior
- Interactive mode — play guesses against a real Zborle/Wordle game
- Simulation mode — benchmark solver performance across the full answer list
- Pytest suite for generator and solver
- CI via GitHub Actions

## Tech Stack

|             |                                     |
| ----------- | ----------------------------------- |
| Language    | Python 3.8+                         |
| Dependencies| None (standard library only)        |
| Corpus      | `words-mk-main` Macedonian word list |
| Testing     | `pytest`                            |
| CI          | GitHub Actions                      |

## Prerequisites

- [Python](https://www.python.org) 3.8+
- `pytest` (optional, only needed to run tests)

## Run

```bash
git clone https://github.com/syreone/zborle-solver.git
cd zborle-solver

# build candidates.txt from the corpus
python cli_build.py --corpus words-mk-main/all --out candidates.txt

# play interactively
python solver.py interactive --answers words-mk-main/all --candidates candidates.txt

# or benchmark the solver across all answers
python solver.py simulate --answers words-mk-main/all --candidates candidates.txt --max 200
```

Run tests with:

```bash
python -m pytest -q
```