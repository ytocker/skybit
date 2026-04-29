"""Player-name sanitization.

Defends against:
  * XSS / HTML injection if the leaderboard is ever rendered into the DOM
    (today: textContent only, but defense in depth matters).
  * Unicode bidi/RTL spoofing (U+202A‒U+202E, U+2066‒U+2069) which can
    flip a benign-looking name into something offensive when rendered.
  * Zero-width characters used for impersonation ("alice" vs. "al​ice").
  * NFKC tricks (full-width ASCII, ligature spoofs).
  * Control characters and newlines.
  * Empty / whitespace-only names.
  * A small profanity blocklist (English starter — extend as needed).

Usage
-----
    from game.security import sanitize_name
    safe = sanitize_name(raw)
    if safe is None:
        # reject / show error
        ...

Returns None for *anything* the game shouldn't accept; otherwise returns
the cleaned, length-clamped string.
"""
from __future__ import annotations

import unicodedata

MAX_LEN = 12

# Bidirectional formatting and isolate controls.
_BIDI_CHARS = {
    "‪", "‫", "‬", "‭", "‮",  # LRE/RLE/PDF/LRO/RLO
    "⁦", "⁧", "⁨", "⁩",            # LRI/RLI/FSI/PDI
    "‎", "‏",                                # LRM/RLM
}
# Zero-width / format characters used for impersonation.
_ZERO_WIDTH = {
    "​", "‌", "‍",                      # ZWSP, ZWNJ, ZWJ
    "⁠", "﻿",                                # word joiner, BOM
}

# Conservative blocklist. Compared against NFKC-folded lowercase. Extend
# in code review; deliberately small so we don't ship a profanity dictionary.
BLOCKLIST: frozenset[str] = frozenset({
    "admin", "root", "null", "undefined", "system", "skybit",
    "moderator", "anonymous",
})


def strip_zero_width_and_bidi(s: str) -> str:
    return "".join(ch for ch in s if ch not in _BIDI_CHARS and ch not in _ZERO_WIDTH)


def _strip_controls(s: str) -> str:
    """Drop C0/C1 controls, keep printable BMP."""
    out = []
    for ch in s:
        cat = unicodedata.category(ch)
        if cat.startswith("C"):  # Cc, Cf, Cn, Co, Cs
            continue
        out.append(ch)
    return "".join(out)


def is_clean(s: str) -> bool:
    """True if `s` survives sanitize unchanged (i.e., already safe)."""
    return sanitize_name(s) == s


def sanitize_name(raw: str | None, *, max_len: int = MAX_LEN) -> str | None:
    """Return a cleaned name suitable for submission, or None to reject.

    Pipeline: NFKC → drop bidi/ZW → drop controls → strip → length clamp →
    blocklist check → emptiness/whitespace check.
    """
    if not isinstance(raw, str):
        return None
    s = unicodedata.normalize("NFKC", raw)
    s = strip_zero_width_and_bidi(s)
    s = _strip_controls(s)
    s = s.strip()
    if not s:
        return None
    if len(s) > max_len:
        s = s[:max_len].rstrip()
        if not s:
            return None
    folded = s.casefold()
    if folded in BLOCKLIST:
        return None
    # Reject names that are pure punctuation / symbols (no letters or digits).
    if not any(ch.isalnum() for ch in s):
        return None
    return s
