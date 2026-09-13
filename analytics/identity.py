"""
Anonymous device_id -> (nickname, hex color) for display.

The database stores opaque UUIDs. Showing "f4a9...c321" in a leaderboard
is unreadable; mapping to a stable two-word pet name + a hashed color
swatch makes the same player recognisable across views without us
storing or guessing any PII.

Deterministic: same UUID always yields the same (name, color). The
mapping is display-only — never written back to Supabase, never used
as a key. Regenerating the dictionary or library version changes the
names but not the underlying data.

We reuse petname's word lists (adjectives + names) but pick from them
with our own seeded RNG. petname.Generate() itself uses a SystemRandom
instance internally, which is unseedable, so we can't use it directly.
"""
from __future__ import annotations

import hashlib

import petname
from colorhash import ColorHash


_ADJECTIVES = tuple(petname.adjectives)
_NAMES = tuple(petname.names)


def _seed_int(device_id: str) -> int:
    """Stable, well-distributed integer from any UUID string. SHA-256
    is overkill but it's free and removes any worry about clustering
    from a naive hash() (which is also not stable across processes)."""
    return int(hashlib.sha256(device_id.encode("utf-8")).hexdigest(), 16)


def nickname(device_id: str) -> str:
    """Two-word adjective-animal name, stable per UUID."""
    h = _seed_int(device_id)
    adj = _ADJECTIVES[h % len(_ADJECTIVES)]
    nm = _NAMES[(h // len(_ADJECTIVES)) % len(_NAMES)]
    return f"{adj.title()}-{nm.title()}"


def color(device_id: str) -> str:
    """Hex color stable per UUID, clamped for legibility on light + dark
    Streamlit themes. Saturation and lightness ranges chosen so the
    swatch is visible against both backgrounds without washing out."""
    return ColorHash(
        device_id,
        lightness=(0.45, 0.55),
        saturation=(0.5, 0.7),
    ).hex


def for_device(device_id: str) -> tuple[str, str]:
    """Convenience: both at once."""
    return nickname(device_id), color(device_id)
