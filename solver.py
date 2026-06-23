import argparse
import math
import statistics
from collections import Counter
from functools import lru_cache
from typing import Dict, Iterable, List, Tuple
import sys
import os
try:
    import colorama
    colorama.init(autoreset=True)
    COLORAMA_AVAILABLE = True
except Exception:
    colorama = None
    COLORAMA_AVAILABLE = False

def detect_color_support() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("PYCHARM_HOSTED"):
        return False
    if os.environ.get("CI"):
        return False
    if not sys.stdout.isatty():
        return False
    if os.name == "nt":
        return COLORAMA_AVAILABLE
    return True

COLOR_ALLOWED = detect_color_support()
def set_color_allowed(val: bool):
    global COLOR_ALLOWED
    COLOR_ALLOWED = bool(val)

try:
    from generator import load_corpus, build_stats, generate_candidates
except Exception:
    load_corpus = None
    build_stats = None
    generate_candidates = None

DEFAULT_ANSWERS = "words-mk-main/all"
DEFAULT_CANDIDATES_FILE = "candidates.txt"


@lru_cache(maxsize=None)
def feedback(guess: str, target: str) -> Tuple[int, int, int, int, int]:
    """Wordle feedback tuple (2=green,1=yellow,0=gray)."""
    res = [0] * 5
    remaining = []
    for i in range(5):
        if guess[i] == target[i]:
            res[i] = 2
        else:
            remaining.append(target[i])
    for i in range(5):
        if res[i] != 2:
            if guess[i] in remaining:
                res[i] = 1
                remaining.remove(guess[i])
    return tuple(res)


def encode_feedback(pat: Tuple[int, int, int, int, int]) -> int:
    """Encode 5-digit base-3 pattern to integer."""
    code = 0
    for i, v in enumerate(pat):
        code += v * (3 ** i)
    return code


def compute_positional_freq(words: Iterable[str]) -> List[Dict[str, int]]:
    pos_freq = [Counter() for _ in range(5)]
    for w in words:
        if len(w) != 5:
            continue
        for i, ch in enumerate(w):
            pos_freq[i][ch] += 1
    return [dict(d) for d in pos_freq]


def compute_positional_priors(candidates: List[str], answers: List[str]) -> Dict[str, float]:
    pos_freq = compute_positional_freq(answers)
    scores = {}
    for w in candidates:
        s = sum(pos_freq[i].get(w[i], 0) for i in range(5))
        scores[w] = s
    total = sum(scores.values()) or 1
    return {w: float(scores[w]) / total for w in candidates}


def expected_posterior_entropy(guess: str, possible_answers: List[str], priors: Dict[str, float]) -> float:
    pattern_weights = {}
    for t in possible_answers:
        pat = feedback(guess, t)
        code = encode_feedback(pat)
        pattern_weights[code] = pattern_weights.get(code, 0.0) + priors.get(t, 0.0)
    total_prior = sum(priors.get(t, 0.0) for t in possible_answers) or 1.0

    exp_entropy = 0.0
    for code, p_weight in pattern_weights.items():
        p_prob = p_weight / total_prior
        # collect weights for this pattern
        weights = []
        for t in possible_answers:
            if encode_feedback(feedback(guess, t)) == code:
                weights.append(priors.get(t, 0.0))
        wsum = sum(weights) or 1.0
        h = 0.0
        for w in weights:
            q = w / wsum
            if q > 0:
                h -= q * math.log2(q)
        exp_entropy += p_prob * h
    return exp_entropy


def pretty_feedback_display(pat: Tuple[int, int, int, int, int], letters: str = "") -> str:
    """Return colored or ASCII-feedback display depending on COLOR_ALLOWED."""
    # ASCII fallback
    if not COLOR_ALLOWED:
        out = []
        for i, v in enumerate(pat):
            ch = letters[i] if letters and i < len(letters) else " "
            if v == 2:
                out.append(f"[G]{ch}")
            elif v == 1:
                out.append(f"[Y]{ch}")
            else:
                out.append(f"[ ]{ch}")
        return " ".join(out)

    GREEN_BG = "\x1b[42m"
    YELLOW_BG = "\x1b[43m"
    GRAY_BG = "\x1b[100m"
    RESET = "\x1b[0m"
    out = []
    for i, v in enumerate(pat):
        ch = letters[i] if letters and i < len(letters) else " "
        if v == 2:
            out.append(f"{GREEN_BG} {ch} {RESET}")
        elif v == 1:
            out.append(f"{YELLOW_BG} {ch} {RESET}")
        else:
            out.append(f"{GRAY_BG} {ch} {RESET}")
    return "".join(out)


def choose_best_guess(possible_answers: List[str], guess_pool: List[str], priors: Dict[str, float], top_k: int = 200, fixed_letters: Dict[int, str] = None, history: List[Tuple[str, Tuple[int, int, int, int, int]]] = None) -> str:
    """
    Choose best guess minimizing expected posterior entropy.
    If fixed_letters is provided, prefer guesses that agree with those known green positions.
    """
    if fixed_letters is None:
        fixed_letters = {}

    # If the set of possible answers is small, only consider them as guesses.
    # This avoids proposing guesses outside the current posterior when we're close to the answer.
    if len(possible_answers) <= top_k:
        guess_pool = possible_answers[:]
    else:
        # restrict guess pool by prior top_k for speed
        if len(guess_pool) > top_k:
            guess_pool = sorted(guess_pool, key=lambda w: priors.get(w, 0.0), reverse=True)[:top_k]

    # If a history of (guess,pattern) is provided, filter the guess pool to words
    # that are consistent with all previously observed feedback. This enforces
    # all constraints implied by the user's (assumed correct) feedback.
    if history:
        filtered = []
        for candidate in guess_pool:
            ok = True
            for g, p in history:
                if feedback(g, candidate) != p:
                    ok = False
                    break
            if ok:
                filtered.append(candidate)
        if filtered:
            guess_pool = filtered

    # prefer guesses consistent with fixed (green) letters
    def matches_fixed(word: str) -> bool:
        for idx, ch in fixed_letters.items():
            if word[idx] != ch:
                return False
        return True

    filtered_pool = [w for w in guess_pool if matches_fixed(w)]
    # fallback: if none match (rare), use original pool
    if filtered_pool:
        candidate_pool = filtered_pool
    else:
        candidate_pool = guess_pool

    best = None
    best_score = float("inf")
    for g in candidate_pool:
        e = expected_posterior_entropy(g, possible_answers, priors)
        if e < best_score:
            best_score = e
            best = g
    return best


def filter_answers(possible: List[str], guess: str, pat: Tuple[int, int, int, int, int]) -> List[str]:
    return [w for w in possible if feedback(guess, w) == pat]


def interactive_mode(answers_path: str = DEFAULT_ANSWERS, candidates_file: str = DEFAULT_CANDIDATES_FILE):
    if load_corpus is None:
        raise RuntimeError("generator module not available. Please keep generator.py in the same folder.")
    answers = load_corpus(answers_path)
    try:
        with open(candidates_file, "r", encoding="utf-8") as f:
            candidates = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        stats = build_stats(answers)
        candidates = generate_candidates(stats)

    priors = compute_positional_priors(candidates, answers)

    pos_freq = compute_positional_freq(answers)
    def positional_score(w):
        return sum(pos_freq[i].get(w[i], 0) for i in range(5))
    top_first = sorted(candidates, key=positional_score, reverse=True)[:10]

    possible = answers[:]
    first_move = True
    # accumulate explicit green-letter constraints from user feedback
    green_map = {}
    # keep confirmed history of (guess, pattern) to enforce all constraints
    history: List[Tuple[str, Tuple[int, int, int, int, int]]] = []

    print("=== Zborle Solver ===")
    print("Одговори: %d | Кандидати: %d" % (len(answers), len(candidates)))
    print()

    while True:
        if len(possible) == 1:
            guess = possible[0]
        elif first_move:
            print("Препорачани први потези (според позициона честота):")
            for i, g in enumerate(top_first[:5], start=1):
                print(f"  {i}. {g}")
            izbor = input("Избери број (1-5) или Enter за прв: ").strip()
            if izbor == "" or izbor == "1":
                guess = top_first[0]
            else:
                try:
                    idx = int(izbor) - 1
                    guess = top_first[idx] if 0 <= idx < 5 else top_first[0]
                except ValueError:
                    guess = top_first[0]
            first_move = False
        else:
            # prefer guesses that match explicit green constraints stored in green_map
            guess = choose_best_guess(possible, candidates, priors, fixed_letters=green_map, history=history)

        print(f"Преостанати: {len(possible)}")
        if len(possible) <= 10:
            print("Можни: %s" % " ".join(possible))
        print(f"Погоди: {guess}")

        if len(possible) == 1 and guess == possible[0]:
            print("Го погодивте зборот!")
            break

        # read feedback and validate format
        while True:
            v = input("Feedback (2=зелен 1=жолт 0=сив): ").strip()
            if len(v) == 5 and all(ch in "012" for ch in v):
                break
            v = input("Внеси 5 цифри (2/1/0): ").strip()
        pat = tuple(int(ch) for ch in v)
        if all(x == 2 for x in pat):
            print("Погодок!")
            break

        # filter possible answers according to entered feedback
        new_possible = filter_answers(possible, guess, pat)
        if not new_possible:
            print("Грешка: нема можни зборови за тој feedback.")
            break

        # accept the filtered set (we assume the user input is correct)
        possible = new_possible
        # update explicit green map from the confirmed pattern
        for idx, val in enumerate(pat):
            if val == 2:
                green_map[idx] = guess[idx]
        # confirmed feedback already recorded in history above


def simulate(answers_path: str = DEFAULT_ANSWERS, candidates_file: str = DEFAULT_CANDIDATES_FILE, max_answers: int = None):
    if load_corpus is None:
        raise RuntimeError("generator module not available.")
    answers = load_corpus(answers_path)
    if max_answers:
        answers = answers[:max_answers]
    try:
        with open(candidates_file, "r", encoding="utf-8") as f:
            candidates = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        stats = build_stats(answers)
        candidates = generate_candidates(stats)

    priors = compute_positional_priors(candidates, answers)

    results = []
    for target in answers:
        possible = answers[:]
        n = 0
        green_map = {}
        history: List[Tuple[str, Tuple[int, int, int, int, int]]] = []
        while True:
            n += 1
            if len(possible) == 1:
                guess = possible[0]
            elif n == 1:
                pos_freq = compute_positional_freq(answers)
                def score(w): return sum(pos_freq[i].get(w[i], 0) for i in range(5))
                guess = sorted(candidates, key=score, reverse=True)[0]
            else:
                guess = choose_best_guess(possible, candidates, priors, fixed_letters=green_map, history=history)
            if guess == target:
                results.append(n)
                break
            pat = feedback(guess, target)
            # update green_map with newly discovered greens
            for idx, val in enumerate(pat):
                if val == 2:
                    green_map[idx] = guess[idx]
            # add confirmed feedback to history
            for idx, val in enumerate(pat):
                # already handled greens; store the full pattern in history
                pass
            history.append((guess, pat))
            possible = filter_answers(possible, guess, pat)
            if not possible:
                results.append(999)
                break

    print("Games:", len(results))
    print("Avg guesses:", statistics.mean(results))
    print("Median guesses:", statistics.median(results))
    print("Max guesses:", max(results))
    hist = Counter(results)
    print("Histogram (guesses -> count):")
    for k in sorted(hist):
        print(f"  {k}: {hist[k]}")


def main():
    p = argparse.ArgumentParser(description="Zborle solver - interactive and simulate modes")
    sub = p.add_subparsers(dest="cmd", required=False)
    p_int = sub.add_parser("interactive", help="Run interactive solver")
    p_int.add_argument("--answers", default=DEFAULT_ANSWERS)
    p_int.add_argument("--candidates", default=DEFAULT_CANDIDATES_FILE)
    p_int.add_argument("--force-color", action="store_true", help="Force-enable ANSI colors in output")
    p_sim = sub.add_parser("simulate", help="Run automatic simulation over answers")
    p_sim.add_argument("--answers", default=DEFAULT_ANSWERS)
    p_sim.add_argument("--candidates", default=DEFAULT_CANDIDATES_FILE)
    p_sim.add_argument("--max", type=int, default=None, help="Limit number of answers (for quick tests)")

    args = p.parse_args()
    if args.cmd == "simulate":
        simulate(answers_path=args.answers, candidates_file=args.candidates, max_answers=args.max)
    else:
        if getattr(args, 'force_color', False):
            set_color_allowed(True)
        interactive_mode(answers_path=getattr(args, "answers", DEFAULT_ANSWERS), candidates_file=getattr(args, "candidates", DEFAULT_CANDIDATES_FILE))


if __name__ == "__main__":
    main()
