"""Five french-fry coin treatments for the KFC power-up.

Each `draw_<name>(surf, cx, cy, t=0.0)` paints a fry centred at (cx, cy)
into the existing 2*COIN_R footprint (~22 px). The `t` parameter is for a
later optional bob; default 0 = static for the preview.

`build_*_frame` is intentionally not used — these are drawn directly per
coin per frame, just like the existing `Coin.draw`. Preview-only —
nothing in the game imports this yet.
"""
import math
import pygame

from game.parrot import (
    _CRISPY_GOLD, _CRISPY_DARK, _CRISPY_LIGHT, _CRISPY_SPOT,
)

# Carton accent colours — red carton with white band, KFC-style
KFC_RED    = (210,  35,  30)
KFC_RED_DK = (140,  15,  15)
KFC_WHITE  = (250, 248, 240)
SKIN_BROWN = (115,  70,  25)


# ── shared fry body ──────────────────────────────────────────────────────────

def _draw_fry_body(surf, x, y, w, h, *, crinkle=False, skin_side=None,
                   spots=None, drop_shadow=True):
    """Single fry body at (x,y) of bounding rect, size (w,h).
    Layers: drop shadow, dark crust, gold body, light ridge, dark shadow column,
    optional crinkle notches and potato-skin edge, plus a few crispy spots."""
    if drop_shadow:
        sh = pygame.Surface((w + 6, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 140), sh.get_rect())
        surf.blit(sh, (x - 3, y + h - 1))

    # Dark crust outline + gold body
    pygame.draw.rect(surf, _CRISPY_DARK, (x - 1, y, w + 2, h + 1))
    pygame.draw.rect(surf, _CRISPY_GOLD, (x, y + 1, w, h - 1))

    # Bright highlight ridge along the left
    pygame.draw.line(surf, _CRISPY_LIGHT,
                     (x + 1, y + 2), (x + 1, y + h - 2), 1)
    # Shadow column along the right
    pygame.draw.line(surf, _CRISPY_DARK,
                     (x + w - 2, y + 2), (x + w - 2, y + h - 1), 1)
    # Crispy top edge (slight knife-cut suggestion)
    pygame.draw.line(surf, _CRISPY_DARK,  (x, y + 1),     (x + w - 1, y + 1), 1)
    pygame.draw.line(surf, _CRISPY_LIGHT, (x + 1, y),     (x + w - 2, y),     1)

    # Crispy spots
    if spots is None:
        spots = [(x + 1, y + 5), (x + w - 2, y + 9),
                 (x + 2, y + 13), (x + w - 3, y + h - 4)]
    for sx, sy in spots:
        if 0 <= sx < surf.get_width() and 0 <= sy < surf.get_height():
            surf.set_at((sx, sy), _CRISPY_SPOT)

    # Crinkle: small alternating notches down both sides
    if crinkle:
        for i in range(2, h - 1, 3):
            # Left side: pull a 1-px crust notch inward every 3 px
            pygame.draw.line(surf, _CRISPY_DARK, (x, y + i), (x, y + i + 1), 1)
            pygame.draw.line(surf, _CRISPY_DARK,
                             (x + w - 1, y + i + 1), (x + w - 1, y + i + 2), 1)

    # Potato skin on one edge
    if skin_side == "left":
        pygame.draw.rect(surf, SKIN_BROWN, (x - 1, y + 2, 2, h - 2))
        pygame.draw.line(surf, _CRISPY_DARK, (x - 1, y + 2), (x - 1, y + h - 1), 1)
    elif skin_side == "right":
        pygame.draw.rect(surf, SKIN_BROWN, (x + w - 1, y + 2, 2, h - 2))


# ── V1 — Straight cut ────────────────────────────────────────────────────────

def draw_straight(surf, cx, cy, t=0.0):
    """Classic straight-cut fry — single vertical 5×18 piece."""
    w, h = 5, 18
    _draw_fry_body(surf, cx - w // 2, cy - h // 2, w, h)


# ── V2 — Crinkle cut ─────────────────────────────────────────────────────────

def draw_crinkle(surf, cx, cy, t=0.0):
    """Crinkle-cut fry — wavy zigzag side edges."""
    w, h = 6, 18
    _draw_fry_body(surf, cx - w // 2, cy - h // 2, w, h, crinkle=True)


# ── V3 — Steak wedge ─────────────────────────────────────────────────────────

def draw_wedge(surf, cx, cy, t=0.0):
    """Thick steak-fry wedge — trapezoidal with potato skin on the left."""
    h = 18
    top_y, bot_y = cy - h // 2, cy + h // 2
    top_half_w, bot_half_w = 3, 5

    # Drop shadow
    sh = pygame.Surface((bot_half_w * 2 + 6, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 140), sh.get_rect())
    surf.blit(sh, (cx - bot_half_w - 3, bot_y))

    # Dark crust trapezoid
    pygame.draw.polygon(surf, _CRISPY_DARK, [
        (cx - bot_half_w - 1, bot_y), (cx + bot_half_w + 1, bot_y),
        (cx + top_half_w + 1, top_y), (cx - top_half_w - 1, top_y),
    ])
    # Gold body
    pygame.draw.polygon(surf, _CRISPY_GOLD, [
        (cx - bot_half_w, bot_y - 1), (cx + bot_half_w, bot_y - 1),
        (cx + top_half_w, top_y + 1), (cx - top_half_w, top_y + 1),
    ])

    # Highlight ridge running diagonally up the left side
    pygame.draw.line(surf, _CRISPY_LIGHT,
                     (cx - top_half_w + 1, top_y + 2),
                     (cx - bot_half_w + 1, bot_y - 2), 1)
    # Shadow column on the right
    pygame.draw.line(surf, _CRISPY_DARK,
                     (cx + top_half_w - 1, top_y + 2),
                     (cx + bot_half_w - 1, bot_y - 2), 1)

    # Potato-skin strip on the left edge
    pygame.draw.polygon(surf, SKIN_BROWN, [
        (cx - bot_half_w - 1, bot_y - 1), (cx - top_half_w - 1, top_y + 1),
        (cx - top_half_w,     top_y + 1), (cx - bot_half_w,     bot_y - 1),
    ])

    # Spots
    for sx, sy in [(cx, cy - 3), (cx + 1, cy + 2), (cx - 1, cy + 5),
                   (cx + 2, cy - 6)]:
        surf.set_at((sx, sy), _CRISPY_SPOT)


# ── V4 — Crossed pair ────────────────────────────────────────────────────────

def _make_single_fry(w=5, h=18, pad=4):
    """Render a single straight fry onto its own padded surface for rotating."""
    sw, sh_ = w + pad * 2, h + pad * 2
    s = pygame.Surface((sw, sh_), pygame.SRCALPHA)
    _draw_fry_body(s, pad, pad, w, h, drop_shadow=False)
    return s


def draw_pair(surf, cx, cy, t=0.0):
    """Two fries crossed in an X — slightly overlapping at the centre."""
    f = _make_single_fry()
    left  = pygame.transform.rotate(f, 22)
    right = pygame.transform.rotate(f, -22)
    # Soft drop shadow under the pair
    sh = pygame.Surface((22, 5), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 140), sh.get_rect())
    surf.blit(sh, (cx - 11, cy + 8))
    # Back fry slightly behind
    surf.blit(left,  left.get_rect(center=(cx - 2, cy + 1)))
    surf.blit(right, right.get_rect(center=(cx + 2, cy)))


# ── V5 — Tilted single fry (single fry from PAIR, keeping the angle) ────────

def draw_tilted(surf, cx, cy, t=0.0):
    """Single straight-cut fry tilted +22° — same angle as the left fry
    in PAIR but on its own. Dynamic, casual feel."""
    f = _make_single_fry()
    rot = pygame.transform.rotate(f, 22)
    # Drop shadow under the fry
    sh = pygame.Surface((20, 5), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 140), sh.get_rect())
    surf.blit(sh, (cx - 10, cy + 8))
    surf.blit(rot, rot.get_rect(center=(cx, cy)))


# ── V6 — KFC carton ──────────────────────────────────────────────────────────

def draw_carton(surf, cx, cy, t=0.0):
    """Mini red KFC-style carton with three fry tops poking out."""
    cw = 14   # carton width at the top
    ch = 11   # carton height
    top_y = cy + 1
    bot_y = top_y + ch

    # Drop shadow
    sh = pygame.Surface((cw + 6, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 150), sh.get_rect())
    surf.blit(sh, (cx - cw // 2 - 3, bot_y - 1))

    # Carton trapezoid (wider at top, narrower at bottom — classic fry box)
    half_top = cw // 2
    half_bot = cw // 2 - 2
    pygame.draw.polygon(surf, KFC_RED_DK, [
        (cx - half_top - 1, top_y), (cx + half_top + 1, top_y),
        (cx + half_bot + 1, bot_y), (cx - half_bot - 1, bot_y),
    ])
    pygame.draw.polygon(surf, KFC_RED, [
        (cx - half_top, top_y + 1), (cx + half_top, top_y + 1),
        (cx + half_bot, bot_y - 1), (cx - half_bot, bot_y - 1),
    ])
    # Highlight ridge on the upper-left
    pygame.draw.line(surf, (240, 80, 70),
                     (cx - half_top + 2, top_y + 2),
                     (cx - half_bot + 2, bot_y - 2), 1)
    # White horizontal band across the middle
    band_y = top_y + ch // 2
    pygame.draw.rect(surf, KFC_WHITE,
                     (cx - half_top + 1, band_y, cw - 2, 2))

    # Three fry tops poking out the top of the carton
    for fx, fh in ((cx - 4, 10), (cx, 13), (cx + 4, 9)):
        fy = top_y - fh
        pygame.draw.rect(surf, _CRISPY_DARK, (fx - 1, fy, 3, fh + 1))
        pygame.draw.rect(surf, _CRISPY_GOLD, (fx, fy + 1, 1, fh - 1))
        pygame.draw.line(surf, _CRISPY_LIGHT, (fx, fy), (fx, fy + 2), 1)
        # Tiny dark spot on each
        surf.set_at((fx + 1, fy + fh // 2), _CRISPY_SPOT)


# ── Registry ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("STRAIGHT", draw_straight),
    ("CRINKLE",  draw_crinkle),
    ("WEDGE",    draw_wedge),
    ("PAIR",     draw_pair),
    ("TILTED",   draw_tilted),
    ("CARTON",   draw_carton),
]
