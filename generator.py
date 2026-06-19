MK_ALPHABET = "абвгдѓежзѕијклљмнњопрстќуфхцчџш"
VOWELS = set("аеиоу")
RARE_CHARS = set("ѓѕљњќџ")

def load_corpus(path):
    """Return a list of words (one per line) from path."""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def mask(word):
    """Return 'V'/'C' mask (length 5)."""
    return "".join("V" if ch in VOWELS else "C" for ch in word)

def build_stats(words):
    """
    Build small stats used for generation:
      - pos_bigrams[pos][char] -> set(next_chars)   (pos 0..3 for bigrams)
      - pos_trigrams[pos][char1][char2] -> set(next_chars) (pos 0..2)
      - masks: set of masks seen in corpus
      - start_letters: set of letters that appear as first char in corpus
    Return a dict with those entries.
    """
    # bigrams: pos -> char -> set(next)
    pos_bigrams = [{c: set() for c in MK_ALPHABET} for _ in range(4)]
    # trigrams: pos -> char1 -> char2 -> set(next)
    pos_trigrams = []
    for pos in range(3):
        m = {c1: {c2: set() for c2 in MK_ALPHABET} for c1 in MK_ALPHABET}
        pos_trigrams.append(m)

    masks = set()
    start_letters = set()

    for w in words:
        if len(w) != 5:
            continue
        start_letters.add(w[0])
        masks.add(mask(w))
        # build bigrams
        for p in range(4):
            a, b = w[p], w[p+1]
            pos_bigrams[p][a].add(b)
        # build trigrams
        for p in range(3):
            a, b, c = w[p], w[p+1], w[p+2]
            pos_trigrams[p][a][b].add(c)

    return {
        "pos_bigrams": pos_bigrams,
        "pos_trigrams": pos_trigrams,
        "masks": masks,
        "start_letters": start_letters,
    }

# Small rule checks
def has_vowel(word):
    return any(ch in VOWELS for ch in word)

def rare_count_ok(word, max_rare=1):
    return sum(1 for ch in word if ch in RARE_CHARS) <= max_rare

def valid_mask(word, masks):
    return mask(word) in masks

def valid_by_bigrams(word, pos_bigrams):
    for p in range(4):
        if word[p+1] not in pos_bigrams[p].get(word[p], set()):
            return False
    return True

def valid_by_trigrams(word, pos_trigrams):
    for p in range(3):
        if word[p+2] not in pos_trigrams[p].get(word[p], {}).get(word[p+1], set()):
            return False
    return True

def is_valid(word, stats):
    return (
        len(word) == 5
        and has_vowel(word)
        and rare_count_ok(word)
        and valid_mask(word, stats["masks"])
        and valid_by_bigrams(word, stats["pos_bigrams"])
        and valid_by_trigrams(word, stats["pos_trigrams"])
    )

def generate_candidates(stats):
    """
    Grow sequences position-by-position using adjacency maps.
    Returns a sorted list of candidate 5-letter strings.
    """
    # start from allowed first letters (keeps work small)
    sequences = [c for c in MK_ALPHABET if c in stats["start_letters"]]

    for pos in range(1, 5):
        new_seqs = []
        if pos == 1:
            # use bigram map at position 0
            for seq in sequences:
                nexts = stats["pos_bigrams"][0].get(seq[-1], set())
                for n in nexts:
                    new_seqs.append(seq + n)
        else:
            # use trigram map at pos-2
            idx = pos - 2
            for seq in sequences:
                a, b = seq[-2], seq[-1]
                nexts = stats["pos_trigrams"][idx].get(a, {}).get(b, set())
                for n in nexts:
                    new_seqs.append(seq + n)
        sequences = new_seqs
        if not sequences:
            return []

    # final filtering by simple rules
    candidates = []
    for s in sequences:
        if has_vowel(s) and rare_count_ok(s) and valid_mask(s, stats["masks"]):
            candidates.append(s)
    candidates.sort()
    return candidates

# Small CLI helper (optional)
if __name__ == "__main__":
    words = load_corpus("words-mk-main/all")
    stats = build_stats(words)
    cands = generate_candidates(stats)
    with open("candidates.txt", "w", encoding="utf-8") as f:
        for w in cands:
            f.write(w + "\n")
    print("Wrote", len(cands), "candidates")