"""Shoe cosmetics for the Store's SHOES tab.

Each shoe is defined ONCE as a side-profile ``draw_shoe(surf, x, y, w, h,
facing)`` in its own ``shoe_<id>`` module, and reused two ways:

  * ICONS[id]  — a big product-shot surface (the sneaker itself) shown on the
                 store card and the Prize-Machine hero, so the model reads at a
                 glance instead of being lost on a 40px bird.
  * BUILDERS[id] — the in-game look: the base macaw with the same shoe drawn
                 small at both feet, via store_skins._make_skin.

Keeping the icon and the foot render off one draw function means a shoe's look
lives in a single place. The product shot is the recognisable hero; the foot
render is a subtle flex that reads as colour at gameplay scale.
"""

import pygame

from game import parrot
from game.store_skins import _make_skin, COMPOSITE_W, COMPOSITE_H, PARROT_DY

from game import (
    shoe_airflyer, shoe_retro1, shoe_airbubble, shoe_shelltoe, shoe_courtgreen,
    shoe_boostknit, shoe_canvashigh, shoe_checkerslip, shoe_poolslides,
    shoe_flipflops, shoe_megadad, shoe_jellycore, shoe_neoncircuit,
    shoe_wingboots, shoe_afterburner,
)

# id -> the single side-profile drawer that defines the shoe.
_DRAW = {
    "skin_shoe_airflyer":   shoe_airflyer.draw_shoe,
    "skin_shoe_retro1":     shoe_retro1.draw_shoe,
    "skin_shoe_airbubble":  shoe_airbubble.draw_shoe,
    "skin_shoe_shelltoe":   shoe_shelltoe.draw_shoe,
    "skin_shoe_courtgreen": shoe_courtgreen.draw_shoe,
    "skin_shoe_boostknit":  shoe_boostknit.draw_shoe,
    "skin_shoe_canvashigh": shoe_canvashigh.draw_shoe,
    "skin_shoe_checkerslip": shoe_checkerslip.draw_shoe,
    "skin_shoe_poolslides": shoe_poolslides.draw_shoe,
    "skin_shoe_flipflops":  shoe_flipflops.draw_shoe,
    "skin_shoe_megadad":    shoe_megadad.draw_shoe,
    "skin_shoe_jellycore":  shoe_jellycore.draw_shoe,
    "skin_shoe_neoncircuit": shoe_neoncircuit.draw_shoe,
    "skin_shoe_wingboots":  shoe_wingboots.draw_shoe,
    "skin_shoe_afterburner": shoe_afterburner.draw_shoe,
}


# ── product-shot icon ────────────────────────────────────────────────────────
# Drawn big on a canvas with headroom above the box so the high-tops (which
# rise past the box top by design) aren't clipped. The store/hero crop to the
# opaque content, so generous padding here is free.
_ICON_W, _ICON_H = 104, 58
_ICON_PAD_X, _ICON_TOP = 20, 36


def _build_icon(draw_shoe) -> pygame.Surface:
    surf = pygame.Surface((_ICON_W + 2 * _ICON_PAD_X, _ICON_H + _ICON_TOP + 14),
                          pygame.SRCALPHA)
    draw_shoe(surf, _ICON_PAD_X, _ICON_TOP, _ICON_W, _ICON_H, 1)
    return parrot._add_outline(surf)


# ── in-game look: Pip wearing the shoes ──────────────────────────────────────
# The base macaw's bare feet sit at roughly x 26-36, y 65-69 in COMPOSITE space
# (base feet + PARROT_DY). The shoes drop just below the belly underside as a
# slightly split pair — low enough to clear the belly silhouette and read as
# feet, not so low they dangle like landing gear.
_FOOT_W, _FOOT_H = 17, 11
_BACK_FOOT = (17, 63)
_FRONT_FOOT = (31, 65)


def _foot_paint(draw_shoe):
    def paint(comp, _wing_angle_deg):
        draw_shoe(comp, _BACK_FOOT[0], _BACK_FOOT[1], _FOOT_W, _FOOT_H, 1)
        draw_shoe(comp, _FRONT_FOOT[0], _FRONT_FOOT[1], _FOOT_W, _FOOT_H, 1)
    return paint


# ── registries consumed by parrot.py ─────────────────────────────────────────
ICONS = {sid: _build_icon(fn) for sid, fn in _DRAW.items()}
BUILDERS = {sid: _make_skin(_foot_paint(fn)) for sid, fn in _DRAW.items()}
