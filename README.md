# zborle-solver

Macedonian Wordle-style solver and candidate generator.

This project is a small, educational implementation that:

- Generates candidate 5-letter Macedonian strings from a corpus using bigram/tri-gram
  adjacency rules and simple phonotactic filters (no hard lookup table of answers).
- Scores candidates with a simple, interpretable positional prior and uses that prior
  inside an entropy-based solver to pick informative guesses.

Quick start
1. Build candidates (writes `candidates.txt`):
   ```
   python cli_build.py --corpus words-mk-main/all --out candidates.txt
   ```
2. Run the solver interactively:
   ```
   python solver.py interactive --answers words-mk-main/all --candidates candidates.txt
   ```

Tests
```
python -m pytest -q
```

Files of interest
- generator.py  - rule-based candidate generator (bigrams/trigrams, masks)
- solver.py     - interactive solver and simulate harness
- cli_build.py  - convenience script that writes candidates.txt from the corpus
- tests/        - pytest tests for generator and solver
