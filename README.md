# zborle-solver

A Wordle-style solver for Macedonian (Zborle). This educational project generates
candidate 5-letter words from a corpus using positional adjacency and mask rules,
then uses an entropy-based solver to pick informative guesses. It includes an
interactive terminal UI with Wordle-style colored feedback blocks and an
explanation mode for why a guess was chosen.

## Highlights
- Rule-based candidate generation (bigrams/trigrams and mask filtering)
- Entropy-driven guess selection (expected posterior entropy)
- Interactive terminal UI with colored blocks and explainability
- Simulation harness with per-answer CSV export and per-run memoization for speed

## Status
- Prototype with an interactive CLI and test coverage. Active work includes
  benchmarking, memoization, and UI polish.

## Quick Start
1. Clone the repository and cd into it:
   ```bash
   git clone https://github.com/syreone/zborle-solver.git
   cd zborle-solver
   ```

2. Create a virtual environment and activate it (Windows example):
   ```powershell
   py -3 -m venv .venv
   .venv\Scripts\activate
   ```

3. Install runtime and test dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   If you don't have `requirements.txt`, install minimal deps directly:
   ```bash
   pip install colorama pytest
   ```

4. (Optional) If you don't have `candidates.txt`, generate it from the corpus:
   ```bash
   python cli_build.py --corpus words-mk-main/all --out candidates.txt
   ```

5. Run the interactive solver:
   ```bash
   python solver.py interactive --answers words-mk-main/all --candidates candidates.txt
   ```

## Interactive usage
- On start you will see randomized first-move suggestions sampled from a top pool.
- Pick a suggestion by entering its number (1–5) or press Enter to accept the default.
- After each guess the CLI prints remaining candidate count and a Wordle-style
  colored board of past guesses.
- Feedback format: enter 5 digits (2=green, 1=yellow, 0=gray). Example: `21002`.
- Enter `s` at the feedback prompt to display an explanation for the current guess
  (top feedback buckets with probabilities and example answers).

## Examples
- Interactive play:
  ```bash
  python solver.py interactive --answers words-mk-main/all --candidates candidates.txt
  ```

- Run a small simulation (first 200 answers):
  ```bash
  python -c "from solver import simulate; simulate(answers_path='words-mk-main/all', candidates_file='candidates.txt', max_answers=200)"
  ```

- Write per-answer results to CSV for benchmarking:
  ```bash
  python - <<'PY'
  from solver import simulate_with_csv
  simulate_with_csv('words-mk-main/all', 'candidates.txt', max_answers=500, out_csv='results.csv')
  PY
  ```

## Developer notes
- Candidate generation (`generator.py`): grows sequences using pos-specific bigrams
  and trigrams, and filters by simple phonotactics (vowel presence, rare-letter
  limits, and mask patterns seen in the corpus).
- Solver (`solver.py`): correct Wordle feedback semantics, expected-posterior-entropy
  scoring with per-run memoization, and interactive UI with colored board and
  explainability.
- Tests: run `python -m pytest -q`.

## Requirements
- Python 3.10+ recommended
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
  or at minimum:
  ```bash
  pip install colorama pytest
  ```

## Roadmap & ideas
- Use the CSV harness to compare strategies (IG-only vs IG+prior vs heuristics).
- Expand the guess pool to the full corpus or a curated high-information set and
  re-run experiments (memoization helps performance).
- Improve candidate hygiene (filter or blacklist non-words found in generator output).
- Add a simple web UI for clickable play and visualization (Flask/Streamlit).

## Troubleshooting
- If colored blocks don't render: use Windows Terminal or PowerShell, and ensure
  `colorama` is installed in your active venv (`pip install colorama`).
- If `python` is not found: install Python 3.10+ and add it to PATH; on Windows
  you can also use the `py` launcher.

## Contributing
- Fork → branch → PR. Keep changes small and add tests for behavioral changes.

## License
- Add your chosen license (e.g., MIT) and include a LICENSE file at the repo root.

## Acknowledgements
- Educational project inspired by Wordle; thanks to contributors and language data sources.
