# zborle-solver

A Wordle-style solver for Macedonian (Zborle). This small, educational project
generates candidate 5-letter words from a corpus using adjacency and mask rules,
and chooses informative guesses with an entropy-based solver. It includes an
interactive terminal UI with Wordle-style colored feedback and an explanation
mode for why each guess was chosen.

Highlights
- Rule-based candidate generator (bigrams/trigrams, masks)
- Entropy-driven guess selection (expected posterior entropy)
- Interactive terminal UI with colored blocks and explainable guesses
- Simulation harness with per-answer CSV export and per-run memoization

Quick Start
1. Clone the repo and enter the folder:
   git clone https://github.com/syreone/zborle-solver.git
   cd zborle-solver

2. Create and activate a virtual environment (Windows example):
   py -3 -m venv .venv
   .venv\Scripts\activate

3. Install minimal dependencies:
   pip install colorama pytest

   
Interactive Usage
- On start you'll see randomized first-move suggestions (sampled from a top-30 pool).
- Pick a suggestion by entering its number (1–5) or press Enter to accept the default.
- After each guess the program prints remaining candidate count and a Wordle-style
  colored board of past guesses.
- Feedback format: enter 5 digits (2=green, 1=yellow, 0=gray), e.g. `21002`.
- Enter `s` at the feedback prompt to see an explanation for the current guess
  (top feedback buckets, probabilities, example answers).
