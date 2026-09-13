"""Bespoke per-achievement center-glyph drawers, one module per category.

Each module defines `_glyph_<id>(surf, cx, cy, r, col)` drawers in the engraved
relief idiom of ``achievement_icons`` plus a ``GLYPHS`` dict keyed by the
achievement id. They are aggregated here and merged into
``achievement_icons._GLYPHS`` at import so every achievement renders its own
emblem. ``MYSTERY_KEYS`` are the amethyst secret tier — their ids route through
the ``_HIDDEN_KEYS`` amethyst path.
"""
from game.emblems import (
    flight_log, riches, power_player, stormchaser,
    skater, mysteries, blooper_reel, lifetime_lows,
    # Bespoke emblems for the later Hall-of-Fame additions (milestones, the
    # Oddities/quirk badges, and the loyalty/Dedication tier).
    milestones, quirks, loyalty,
    # Bespoke tarnished glyphs for the Hall-of-Shame expansion (Blooper Reel +
    # Wasted Opportunity, and the Cosmic Joke + Lifetime Lows tiers).
    shame_blooper_wasted, shame_cosmic_lows,
)

_MODULES = (flight_log, riches, power_player, stormchaser,
            skater, mysteries, blooper_reel, lifetime_lows,
            milestones, quirks, loyalty,
            shame_blooper_wasted, shame_cosmic_lows)

EMBLEM_GLYPHS: dict = {}
for _m in _MODULES:
    EMBLEM_GLYPHS.update(_m.GLYPHS)

MYSTERY_KEYS = frozenset(mysteries.GLYPHS)
