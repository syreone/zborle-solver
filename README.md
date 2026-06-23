# zborle-solver

A Wordle-style solver for Macedonian (Zborle). This project generates candidate
5-letter words from a corpus and uses an entropy-based solver to pick
informative guesses. The interactive solver prints a Wordle-style board in the
terminal using rich for colored cells.

## Highlights

- Rule-based candidate generation (generator.py)
- Entropy-driven guess selection (expected posterior entropy)
- Terminal UI with colored feedback using rich (no colorama)
- Simulation harness for batch evaluation

## Quick Start

1. Clone the repository and enter it:

   git clone https://github.com/syreone/zborle-solver.git
   cd zborle-solver

2. Create a virtual environment (recommended):

   py -3 -m venv .venv
   .venv\Scripts\activate   (Windows cmd)
   .\.venv\Scripts\Activate.ps1   (PowerShell)

3. Install dependencies:

   pip install -r requirements.txt

4. Generate candidates (if you don't have candidates.txt):

   python cli_build.py --corpus words-mk-main/all --out candidates.txt

5. Run the interactive solver:

   python solver.py interactive --answers words-mk-main/all --candidates candidates.txt --force-color

## Notes about colors and terminals

- The solver uses rich to render colored cells (green/yellow/gray). rich works in
  Windows Terminal, VS Code integrated terminal, PyCharm Terminal, WSL shells,
  Git Bash, and most modern terminals.
- If you run in an environment that does not render colors (legacy PowerShell Run
  window, some CI runners), the solver falls back to an ASCII representation.
- If colors do not display in your terminal:
  - Use Windows Terminal, VS Code terminal, or PyCharm Terminal (Terminal pane).
  - Or enable virtual terminal processing (persistent on Windows):

    powershell -Command "Set-ItemProperty -Path HKCU:\Console -Name VirtualTerminalLevel -Type DWord -Value 1"

    Then restart your terminal.

## Interactive usage

- On start the solver shows a few recommended first moves (position-frequency
  heuristic).
- Select a recommendation by number (1–5) or press Enter for the default.
- After each guess, enter feedback as five digits:
  - 2 = green (correct position)
  - 1 = yellow (present but wrong position)
  - 0 = gray (not present)

  Example: 22001
- The solver prints a colored/ASCII row for the feedback and updates remaining
  candidates.
- Enter `--force-color` to force-enable color mode when testing.

## Testing

- Run unit tests:

  python -m pytest -q

## Security & repository hygiene

- Do not commit your virtual environment. The repository ignores .venv/ and
  common IDE files.
- requirements.txt lists runtime dependencies (rich) and test dependencies
  (pytest). Install them only inside a venv.

## Troubleshooting

- If python is not found on Windows, use the launcher: `py -3 -m venv .venv`.
- If colors show as raw escape sequences, use a different terminal (Windows
  Terminal or VS Code terminal) or run the color-test:

  python -c "from rich.console import Console; Console().print('[white on green] G [/]', style='bold')"

## Files of interest

- solver.py — main solver and interactive mode
- generator.py — candidate generator and corpus utilities
- cli_build.py — helper to produce candidates.txt from corpus
- tests/ — unit tests

## License

- MIT (see LICENSE.md)

If you want, I can make minor wording edits or apply this README.md update for
you. Reply with any changes you want, or say `approve` and I'll commit the
updated README locally so you can review before we push to GitHub.
