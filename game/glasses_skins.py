"""Eyewear cosmetics for the Store's SHADES tab.

Each style is defined ONCE as a side-profile ``draw_shades(surf, cx, cy,
eye_w, facing)`` in its own ``shades_<id>`` module — centred on the eye at
``(cx, cy)`` and sized to an eye span of ``eye_w`` px — and reused two ways:

  * ICONS[id]   — a big product-shot of the glasses themselves, shown on the
                  store card and Prize-Machine hero so the model reads at a
                  glance instead of being lost on a 40px bird.
  * BUILDERS[id] — the in-game look: the base macaw rebuilt with a PLAIN eye
                  (``parrot._build_frame_bare``) and the chosen shades painted
                  over the eye anchor via ``store_skins._make_skin``.

Starting every styled look from the bare-eyed build (rather than the default
aviator build) is what lets thin/clear frames — round, nerd, monocle — sit on
the eye without the baked gold aviators peeking through. ``skin_shades_none``
paints nothing, so it ships the bare-eyed Pip: the "remove your shades" option.
"""

import pygame

from game import parrot
from game.store_skins import _make_skin

from game import (
    shades_nerd, shades_round, shades_heart, shades_star, shades_black,
    shades_white, shades_3d, shades_pixel, shades_ski, shades_monocle,
    shades_cyber,
)

# id -> the single side-profile drawer that defines the eyewear. NO SHADES is
# absent here on purpose: it has no lenses, only the bare-eyed base build.
_DRAW = {
    "skin_shades_nerd":    shades_nerd.draw_shades,
    "skin_shades_round":   shades_round.draw_shades,
    "skin_shades_heart":   shades_heart.draw_shades,
    "skin_shades_star":    shades_star.draw_shades,
    "skin_shades_black":   shades_black.draw_shades,
    "skin_shades_white":   shades_white.draw_shades,
    "skin_shades_3d":      shades_3d.draw_shades,
    "skin_shades_pixel":   shades_pixel.draw_shades,
    "skin_shades_ski":     shades_ski.draw_shades,
    "skin_shades_monocle": shades_monocle.draw_shades,
    "skin_shades_cyber":   shades_cyber.draw_shades,
}

# The remove-your-shades look: bare-eyed Pip, no lenses, no product shot.
SKIN_NONE = "skin_shades_none"


# ── product-shot icon ────────────────────────────────────────────────────────
# Drawn big on a roomy canvas with headroom on every side so wide goggles
# (ski/cyber), tall novelty lenses (heart/star points) and the left-reaching
# temple aren't clipped. The store/hero crop to the opaque content, so the
# generous padding here is free.
_ICON_W, _ICON_H = 200, 140
_ICON_EYE_W = 92
_ICON_CX = 110        # nudged right so the temple toward -facing has room
_ICON_CY = 72


def _build_icon(draw_shades) -> pygame.Surface:
    surf = pygame.Surface((_ICON_W, _ICON_H), pygame.SRCALPHA)
    draw_shades(surf, _ICON_CX, _ICON_CY, _ICON_EYE_W, 1)
    return parrot._add_outline(surf)


# ── in-game look: Pip wearing the shades ─────────────────────────────────────
# The bare-eyed build draws the plain eye at sprite (50, 20); _compose blits the
# body at PARROT_DY=20, so the eye anchors at composite (50, 40). eye_w≈24
# matches the span of the default aviators it replaces. The anchor rides a couple
# px forward of the eye centre so every style laps the beak base — worn eyewear
# grips the face toward the front rather than floating back over the ear.
_EYE_CX, _EYE_CY = 55, 40
_EYE_W = 22


def _eye_paint(draw_shades):
    def paint(comp, _wing_angle_deg):  # head is stationary across wing frames
        draw_shades(comp, _EYE_CX, _EYE_CY, _EYE_W, 1)
    return paint


# ── registries consumed by parrot.py ─────────────────────────────────────────
ICONS = {sid: _build_icon(fn) for sid, fn in _DRAW.items()}

BUILDERS = {
    sid: _make_skin(_eye_paint(fn), base_fn=parrot._build_frame_bare)
    for sid, fn in _DRAW.items()
}
# NO SHADES: the bare-eyed base with nothing painted over it.
BUILDERS[SKIN_NONE] = _make_skin(
    lambda _comp, _wing_angle_deg: None, base_fn=parrot._build_frame_bare
)
