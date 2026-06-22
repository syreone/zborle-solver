# zborle-solver

A Wordle-style solver for Macedonian (Zborle). This educational project generates candidate 5-letter words from a corpus using positional adjacency and mask rules, then uses an entropy-based solver to pick informative guesses. It includes an interactive terminal UI with Wordle-style colored feedback blocks and an explanation mode for why a guess was chosen.

## Highlights
- Rule-based candidate generation (bigrams/trigrams and mask filtering)
- Entropy-driven guess selection (expected posterior entropy)
- Interactive terminal UI with colored blocks and explainability
- Simulation harness with per-answer CSV export and per-run memoization for speed

## Quick Start
1. Clone the repository and cd into it:
   ```bash
   git clone https://github.com/syreone/zborle-solver.git
   cd zborle-solver
   ```

2. Create a virtual environment and activate it :
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
- After each guess the CLI prints remaining candidate count and a Wordle-style colored board of past guesses.
- Feedback format: enter 5 digits (2=green, 1=yellow, 0=gray). Example: `21002`.
- Enter `s` at the feedback prompt to display an explanation for the current guess (top feedback buckets with probabilities and example answers).

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


## Requirements
- Python 3.10+ recommended
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Tests
- Run the test suite with:
  ```bash
  python -m pytest -q
  ```
