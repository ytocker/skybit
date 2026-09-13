"""PARCEL skins — swappable looks for the gift Pip carries below him.

The default parcel (the kraft box + red bow) lives in ``parrot.get_parcel``;
this module adds the purchasable parcel cosmetics for the PARCELS store tab.

Each builder returns a ``PARCEL_SIZE`` square sprite, built procedurally and
**mode-agnostic** — the cosmetic shows its own look across every power-up while
the existing draw code (entities.Bird.draw) still applies the tilt rotation,
grow-scale, ghost alpha-breath and snow overlay on top. Mirrors the
shoe/hat/glasses cosmetic modules so it auto-merges via parrot:

  * ``BUILDERS = {parcel_id: build(mode="normal") -> Surface}``  (in-game look)
  * ``ICONS    = {parcel_id: Surface}``  (store card — populated lazily by get_icon)

Designed parcel looks (Sack, Takeout, Jar, … Comet, Snowglobe) fold in here as
``build_<name>`` once their design loops land.
"""
from functools import partial as _partial
import pygame

from game import parrot
from game.store_catalog import PARCEL_BASE
from game.parcel_designs import (
    takeout, picnic,
    chest,
    snowglobe,
    airmail, love_letter, post_office,
    plastic_bottle, tumbler, coconut, mini_pip, diamond, coin,
    ball_soccer, ball_basketball, ball_tennis, ball_baseball, ball_football,
)


# The default kraft box reuses parrot's legacy palette parcel.
def _build_base(mode: str = "normal", icon_size: int = 0) -> pygame.Surface:
    if icon_size:
        return parrot.get_parcel_icon(icon_size)
    return parrot.get_parcel(mode)


# NO PARCEL — the empty-handed look. The in-game sprite is fully transparent so
# nothing is drawn below Pip. His parcel collision-hitbox (PARCEL_R) is left
# untouched in world.py, so equipping this changes only the look, never the
# difficulty — the same cosmetic-parity rule every other parcel obeys.
def _build_none(mode: str = "normal", icon_size: int = 0) -> pygame.Surface:
    size = icon_size if icon_size else parrot.PARCEL_SIZE
    return pygame.Surface((size, size), pygame.SRCALPHA)


def _none_icon(box: int = 88) -> pygame.Surface:
    """Store-card glyph for NO PARCEL: a faint grey ghost of the kraft box, so
    the card reads as 'the parcel slot, empty'. Parcels are shown by an icon
    (the test contract), so unlike NO SHADES it can't fall back to a blank."""
    ghost = parrot.get_parcel_icon(box).copy()
    ghost.fill((148, 154, 168, 255), special_flags=pygame.BLEND_RGB_MULT)
    ghost.fill((255, 255, 255, 105), special_flags=pygame.BLEND_RGBA_MULT)
    return ghost


# id -> design module. Each module's ``build`` is mode-agnostic (the cosmetic
# shows its own look across every power-up); tilt/grow/ghost/snow still apply
# in entities.Bird.draw on top of whatever surface comes back.
_DESIGNS = {
    "parcel_takeout":   takeout,
    "parcel_airmail":   airmail,
    "parcel_love":      love_letter,
    "parcel_postmark":  post_office,
    "parcel_plastic":   plastic_bottle,
    "parcel_tumbler":   tumbler,
    "parcel_coconut":   coconut,
    "parcel_minipip":   mini_pip,
    "parcel_diamond":   diamond,
    "parcel_coin":      coin,
    "parcel_soccer":     ball_soccer,
    "parcel_basketball": ball_basketball,
    "parcel_tennis":     ball_tennis,
    "parcel_baseball":   ball_baseball,
    "parcel_football":   ball_football,
    "parcel_picnic":    picnic,
    "parcel_chest":     chest,
    "parcel_snowglobe": snowglobe,
}

# FINEST WHISKEY is a single mystery parcel whose look is one of four drams,
# rolled at unlock (the build reads the persisted variant from store_data).
from game import parcel_whiskey

BUILDERS: "dict[str, object]" = {
    PARCEL_BASE: _build_base,
    "parcel_none": _build_none,
    "parcel_whiskey": parcel_whiskey.build,
    **{pid: mod.build for pid, mod in _DESIGNS.items()},
}

# Callables only — no surface creation at import time.
_ICON_BUILDERS: "dict[str, object]" = {
    PARCEL_BASE:      lambda: parrot.get_parcel_icon(88),
    "parcel_none":    lambda: _none_icon(88),
    "parcel_whiskey": lambda: parcel_whiskey.build("normal", icon_size=88),
    **{pid: _partial(mod.build, "normal", icon_size=88) for pid, mod in _DESIGNS.items()},
}

# Populated on demand by get_icon() — never pre-built at import time.
ICONS: "dict[str, pygame.Surface]" = {}


def get_icon(sid: str) -> "pygame.Surface | None":
    """88 px parcel store icon — built lazily on first call, cached thereafter."""
    if sid not in ICONS:
        builder = _ICON_BUILDERS.get(sid)
        if builder is None:
            return None
        ICONS[sid] = builder()
    return ICONS.get(sid)
