"""FINEST WHISKEY — a single SECRET parcel whose look is a random 1-of-4 dram,
locked at unlock.

Mirrors ``animal_jet_fighter``: the store sells ONE mystery item
(``parcel_whiskey``); ``store_data`` rolls a uniform index into ``_POOL`` at
purchase and persists it, so every run shows the SAME bottle the player
unlocked. ``POOL_SIZE`` is the single source of truth for the roll range that
``store_data`` reads back. The four looks are NOT separately catalogued — the
mystery roll is the only way to get one, so the surprise stays intact.
"""
import random

from game import store_data
from game.parcel_designs import (
    whiskey_decanter, whiskey_scotch, whiskey_bourbon, whiskey_cask,
)


# The four drams the unlock can roll (uniform). Order is the persisted index.
_POOL = (
    whiskey_decanter.build,   # 0 — CRYSTAL DECANTER
    whiskey_scotch.build,     # 1 — SCOTCH FIFTH
    whiskey_bourbon.build,    # 2 — SQUARE BOURBON
    whiskey_cask.build,       # 3 — CASKED DRAM
)
POOL_SIZE = len(_POOL)

# Bound lazily on first render (and refreshed right after an unlock) from the
# index persisted by store_data — never re-rolled per launch.
_chosen = None


def _apply(idx) -> None:
    global _chosen
    if idx is None or not (0 <= int(idx) < POOL_SIZE):
        # No persisted roll yet (store preview, legacy save, or a render before
        # the unlock lands): fall back to a uniform pick so a bottle always shows.
        idx = random.randrange(POOL_SIZE)
    _chosen = _POOL[int(idx)]


def sync_from_store() -> None:
    """Lock the look to the index rolled at unlock (persisted in store_data).
    Call right after a fresh purchase so the store card and the next run both
    show the same dram the player just unlocked, and refresh the card icon."""
    try:
        _apply(store_data.skin_variant("parcel_whiskey"))
    except Exception:
        _apply(None)
    # Drop the cached icon and thumbnail so the next render rebuilds from the
    # newly-rolled _chosen (lazy imports avoid an import cycle).
    try:
        from game import parcel_skins, parrot
        parcel_skins.ICONS.pop("parcel_whiskey", None)
        parrot._SKIN_ICONS = None
    except Exception:
        pass
    try:
        from game import store_cards
        store_cards._thumb_cache.pop(("parcel_whiskey", 60), None)
    except Exception:
        pass


def build(mode: str = "normal", icon_size: int = 0):
    if _chosen is None:
        sync_from_store()
    return _chosen(mode, icon_size)


BUILDERS = {"parcel_whiskey": build}
