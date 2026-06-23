import pathlib
from generator import load_corpus, mask, build_stats, generate_candidates

def test_load_and_mask(tmp_path):
    p = tmp_path / "corpus.txt"
    p.write_text("абвгд\nабвге\n", encoding="utf-8")
    words = load_corpus(str(p))
    assert words == ["абвгд", "абвге"]
    assert len(mask("абвгд")) == 5

def test_build_stats_and_generate_contains_corpus_words(tmp_path):
    p = tmp_path / "corpus2.txt"
    p.write_text("абвгд\nабвге\n", encoding="utf-8")
    words = load_corpus(str(p))
    stats = build_stats(words)
    cands = generate_candidates(stats)
    # corpus words should be generatable from the corpus itself
    assert "абвгд" in cands
    assert "абвге" in cands

def test_generate_candidates_non_empty_on_small_corpus(tmp_path):
    p = tmp_path / "c3.txt"
    p.write_text("\n".join(["абвгд", "бвгде", "вгдеж"]), encoding="utf-8")
    words = load_corpus(str(p))
    stats = build_stats(words)
    cands = generate_candidates(stats)
    assert isinstance(cands, list)
    assert len(cands) > 0