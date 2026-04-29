"""Player-name sanitization tests."""
from game.security.sanitize import sanitize_name, BLOCKLIST


def test_basic_pass_through():
    assert sanitize_name("Alice") == "Alice"


def test_strips_zero_width_joiner():
    raw = "al‍ice"  # ZWJ
    assert sanitize_name(raw) == "alice"


def test_strips_rtl_override():
    # U+202E flips display direction — used to spoof "evil.exe" as "exe.live"
    raw = "abc‮def"
    assert sanitize_name(raw) == "abcdef"


def test_strips_control_chars():
    raw = "ab\x00\x07cd"
    assert sanitize_name(raw) == "abcd"


def test_nfkc_fullwidth_digits():
    # Fullwidth "Ｐｌａｙｅｒ１" → "Player1"
    raw = "Ｐｌａｙｅｒ１"
    assert sanitize_name(raw) == "Player1"


def test_length_clamp():
    raw = "A" * 50
    out = sanitize_name(raw)
    assert out is not None and len(out) <= 12


def test_empty_rejected():
    assert sanitize_name("") is None
    assert sanitize_name("   ") is None
    assert sanitize_name(None) is None


def test_pure_punctuation_rejected():
    assert sanitize_name("!!!") is None
    assert sanitize_name("...") is None


def test_blocklist():
    for word in BLOCKLIST:
        assert sanitize_name(word) is None, f"{word!r} should be blocked"
        assert sanitize_name(word.upper()) is None, f"{word.upper()!r} should be blocked"


def test_non_string_input():
    assert sanitize_name(42) is None  # type: ignore[arg-type]
    assert sanitize_name([]) is None  # type: ignore[arg-type]
