from solver import feedback, encode_feedback, filter_answers

def test_feedback_basic():
    assert feedback("абвгд", "абвгд") == (2,2,2,2,2)
    # ensure function runs on a simple non-trivial case
    _ = feedback("абвга", "ааабв")

def test_encode_feedback():
    assert encode_feedback((0,0,0,0,0)) == 0
    assert isinstance(encode_feedback((1,2,0,1,2)), int)

def test_filter_answers_small():
    poss = ["ааааа", "абвгд", "абвге"]
    g = "абвгд"
    pat = feedback(g, "абвге")
    res = filter_answers(poss, g, pat)
    assert "абвге" in res
