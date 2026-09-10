"""Hat cosmetics for the Store's HATS tab.

Each hat is defined ONCE as a side-profile ``draw_hat(surf, cx, base_y,
head_w, facing)`` in its own ``hat_<id>`` module — sized to a head of width
``head_w`` whose crown-top sits at ``base_y`` — and reused two ways:

  * ICONS[id]  — a big product-shot surface (the hat itself) shown on the
                 store card and the Prize-Machine hero, so the model reads at a
                 glance instead of being lost on a 40px bird.
  * BUILDERS[id] — the in-game look: the base macaw with the same hat drawn
                 small, seated on its head, via store_skins._make_skin.

One draw function feeds both, so a hat's look lives in a single place: the
product shot is the recognisable hero, the head render is the in-game flex.
"""

import pygame

from game import parrot
from game.store_skins import _make_skin, HX, CROWN_Y

from game import (
    hat_nycap, hat_snapback, hat_trucker, hat_buckethat, hat_beanie,
    hat_beret, hat_fedora, hat_flatcap, hat_bowler, hat_partyhat, hat_santa,
    hat_gradcap, hat_propeller, hat_chef, hat_sombrero, hat_strawhat,
)

# id -> the single side-profile drawer that defines the hat.
_DRAW = {
    "skin_hat_nycap":     hat_nycap.draw_hat,
    "skin_hat_snapback":  hat_snapback.draw_hat,
    "skin_hat_trucker":   hat_trucker.draw_hat,
    "skin_hat_buckethat": hat_buckethat.draw_hat,
    "skin_hat_beanie":    hat_beanie.draw_hat,
    "skin_hat_beret":     hat_beret.draw_hat,
    "skin_hat_fedora":    hat_fedora.draw_hat,
    "skin_hat_flatcap":   hat_flatcap.draw_hat,
    "skin_hat_bowler":    hat_bowler.draw_hat,
    "skin_hat_partyhat":  hat_partyhat.draw_hat,
    "skin_hat_santa":     hat_santa.draw_hat,
    "skin_hat_gradcap":   hat_gradcap.draw_hat,
    "skin_hat_propeller": hat_propeller.draw_hat,
    "skin_hat_chef":      hat_chef.draw_hat,
    "skin_hat_sombrero":  hat_sombrero.draw_hat,
    "skin_hat_strawhat":  hat_strawhat.draw_hat,
}


# ── product-shot icon ────────────────────────────────────────────────────────
# Drawn big on a square canvas with headroom on every side so the tall hats
# (party/chef cones) and the wide brims (sombrero) aren't clipped. The
# store/hero crop to the opaque content, so generous padding here is free.
_ICON_HW = 78          # product-shot head width
_ICON_CANVAS = 208
_ICON_CX = _ICON_CANVAS // 2
_ICON_BASE_Y = 138     # crown line low enough that tall cones clear the top


def _build_icon(draw_hat) -> pygame.Surface:
    surf = pygame.Surface((_ICON_CANVAS, _ICON_CANVAS), pygame.SRCALPHA)
    draw_hat(surf, _ICON_CX, _ICON_BASE_Y, _ICON_HW, 1)
    return parrot._add_outline(surf)


# ── in-game look: Pip wearing the hat ────────────────────────────────────────
# The base macaw's head centres on HX with its crown-top at CROWN_Y. Seating
# the hat a hair below the crown (base_y) with a head width a touch wider than
# the skull lets the band wrap the round head instead of perching on its apex.
_HEAD_CX = HX
_HEAD_BASE_Y = CROWN_Y + 3
_HEAD_HW = 30

# Per-hat seating trim for the IN-GAME look only (the product-shot ICONS keep
# the canonical anchor). Each ``draw_hat`` module measures its geometry from a
# different reference — some treat ``base_y`` as a band that wraps well below
# the crown (so they perch high), others as the brim line (so they slip over
# the brow) — so the right seat is per-hat, not one global anchor:
#   dx  +right/forward (toward the beak)   dy  +down (toward the head)
#   hw  head width the hat is sized to     facing  +1 bill points forward
# Tuned against an on-Pip render with the crown anchor + head circle overlaid.
_SEAT = {
    "skin_hat_partyhat":  {"hw": 24, "dx": 2, "dy": -3},
    "skin_hat_strawhat":  {"dy": 6},
    "skin_hat_beanie":    {"dx": -1, "dy": -3},
    "skin_hat_beret":     {"dx": -2, "dy": 2},
    "skin_hat_buckethat": {"dy": -1},
    "skin_hat_flatcap":   {"dy": -3},
    "skin_hat_propeller": {"hw": 34, "dx": 1, "dy": 3},
    "skin_hat_trucker":   {"dy": 2},
    "skin_hat_snapback":  {"dy": 5},
    "skin_hat_gradcap":   {"dx": 3, "dy": 2},
    "skin_hat_chef":      {"hw": 27, "dx": 2, "dy": 2},
    "skin_hat_bowler":    {"dy": 2},
    "skin_hat_fedora":    {"dy": -1},
    "skin_hat_sombrero":  {"hw": 28, "dy": 6},
    "skin_hat_santa":     {"dy": -3},
    "skin_hat_nycap":     {"dy": -4},
}


def _head_paint(draw_hat, sid):
    s = _SEAT.get(sid, {})
    cx = _HEAD_CX + s.get("dx", 0)
    base_y = _HEAD_BASE_Y + s.get("dy", 0)
    head_w = s.get("hw", _HEAD_HW)
    facing = s.get("facing", 1)

    def paint(comp, _wing_angle_deg):  # head is stationary across wing frames
        draw_hat(comp, cx, base_y, head_w, facing)
    return paint


# ── registries consumed by parrot.py ─────────────────────────────────────────
ICONS = {sid: _build_icon(fn) for sid, fn in _DRAW.items()}
BUILDERS = {sid: _make_skin(_head_paint(fn, sid)) for sid, fn in _DRAW.items()}
