"""Five dollar-glasses treatments for the parrot under the triple power-up.

Each `_draw_glasses_<name>(surf, cx, cy)` replaces only the sunglasses layer
of the normal parrot sprite — body, wing, beak, tail are identical.

`build_dollar_frames(glasses_fn)` returns 4 outlined parrot surfaces (one per
wing angle) ready to drop into the rotation cache.

Preview-only — nothing in the game imports this yet.
"""
import math
import pathlib
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H,
    SHADE_FRAME,
    _WING_ANGLES, _build_wing, _aaellipse, _add_outline,
)
from game.draw import (
    BIRD_RED, BIRD_RED_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
    BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D, WHITE, NEAR_BLACK,
    COIN_GOLD, COIN_DARK,
)
from game.dollar_variants import BILL_GREEN, BILL_GREEN_DK, BILL_GREEN_LT

_FONT_PATH = str(pathlib.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf")
_font_cache: dict = {}


def _gfont(size):
    f = _font_cache.get(size)
    if f is None:
        f = pygame.font.Font(_FONT_PATH, size)
        _font_cache[size] = f
    return f


def _blit_outlined(surf, text, font, center, fill, outline, outline_w=1):
    body = font.render(text, True, fill)
    edge = font.render(text, True, outline)
    rect = body.get_rect(center=center)
    for dx, dy in ((-outline_w, 0), (outline_w, 0),
                   (0, -outline_w), (0, outline_w),
                   (-outline_w, -outline_w), (outline_w, -outline_w),
                   (-outline_w, outline_w), (outline_w, outline_w)):
        surf.blit(edge, (rect.x + dx, rect.y + dy))
    surf.blit(body, rect.topleft)


# ── V1 — Font $ on black lens (clean baseline) ──────────────────────────────

def _draw_glasses_font_dollar(surf, cx, cy):
    """Gold aviator frame, dark lens, bold green $ via font."""
    r = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)

    for lc in (left, right):
        pygame.draw.circle(surf, SHADE_FRAME, lc, r + 1)
        pygame.draw.circle(surf, (18, 20, 35), lc, r)

    f = _gfont(9)
    for lc in (left, right):
        _blit_outlined(surf, "$", f, (lc[0], lc[1] + 1),
                       BILL_GREEN, BILL_GREEN_DK, outline_w=1)

    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] + r, left[1]), (right[0] - r, right[1]), 2)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] - r + 1, left[1] - r + 2),
                     (right[0] + r - 1, right[1] - r + 2), 1)


# ── V2 — Coin lenses (gold disc + green $, mirrors power-up icon) ────────────

def _draw_glasses_coin_lens(surf, cx, cy):
    """Each lens is a tiny gold coin — matches the triple power-up icon."""
    r = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)

    for lc in (left, right):
        pygame.draw.circle(surf, COIN_DARK, lc, r + 1)
        pygame.draw.circle(surf, COIN_GOLD, lc, r)
        pygame.draw.circle(surf, (255, 235, 110), lc, r - 2, 1)

    f = _gfont(8)
    for lc in (left, right):
        _blit_outlined(surf, "$", f, (lc[0], lc[1] + 1),
                       BILL_GREEN, BILL_GREEN_DK, outline_w=1)

    # Dark coin-rim bridge
    pygame.draw.line(surf, COIN_DARK,
                     (left[0] + r, left[1]), (right[0] - r, right[1]), 2)
    pygame.draw.line(surf, COIN_GOLD,
                     (left[0] + r, left[1]), (right[0] - r, right[1]), 1)


# ── V3 — Neon glow $ (cyberpunk / electric) ──────────────────────────────────

def _draw_glasses_neon_dollar(surf, cx, cy):
    """Cyan frame, dark lens, neon-green glowing $ inside."""
    r = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)
    NEON_FRAME = (30, 200, 140)
    NEON_FILL  = (80, 255, 160)

    for lc in (left, right):
        pygame.draw.circle(surf, NEON_FRAME, lc, r + 1)
        pygame.draw.circle(surf, (8, 18, 14), lc, r)

        # Soft glow halo behind the $
        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        gc = (r * 2, r * 2)
        pygame.draw.circle(glow, (*NEON_FRAME, 55), gc, r + 2)
        pygame.draw.circle(glow, (*NEON_FRAME, 80), gc, r - 1)
        surf.blit(glow, (lc[0] - r * 2, lc[1] - r * 2))

    f = _gfont(9)
    for lc in (left, right):
        _blit_outlined(surf, "$", f, (lc[0], lc[1] + 1),
                       NEON_FILL, (10, 80, 50), outline_w=1)

    pygame.draw.line(surf, NEON_FRAME,
                     (left[0] + r, left[1]), (right[0] - r, right[1]), 2)
    pygame.draw.line(surf, NEON_FRAME,
                     (left[0] - r + 1, left[1] - r + 2),
                     (right[0] + r - 1, right[1] - r + 2), 1)


# ── V4 — Big chunky $ (cartoonish, oversized frame) ──────────────────────────

def _draw_glasses_big_dollar(surf, cx, cy):
    """Thick gold frames (r=7), large $ filling the whole lens — comically bold."""
    r = 7
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)

    for lc in (left, right):
        # Triple-ring frame gives a thick "chunky" look
        pygame.draw.circle(surf, BILL_GREEN_DK, lc, r + 2)
        pygame.draw.circle(surf, SHADE_FRAME,   lc, r + 1)
        pygame.draw.circle(surf, (22, 24, 42),  lc, r)

    f = _gfont(11)
    for lc in (left, right):
        _blit_outlined(surf, "$", f, (lc[0], lc[1] + 1),
                       (255, 235, 120), BILL_GREEN_DK, outline_w=1)

    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] + r, left[1]), (right[0] - r, right[1]), 3)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] - r + 1, left[1] - r + 2),
                     (right[0] + r - 1, right[1] - r + 2), 2)


# ── V5 — Money-green lens (all-green, light-green $) ─────────────────────────

def _draw_glasses_green_dollar(surf, cx, cy):
    """Vivid green frame and dark-green lens — money-coloured throughout."""
    r = 6
    left  = (cx - 4, cy)
    right = (cx + 6, cy - 1)
    FRAME  = BILL_GREEN
    LENS   = (14, 48, 30)
    GLINT  = (180, 255, 200)

    for lc in (left, right):
        pygame.draw.circle(surf, BILL_GREEN_DK, lc, r + 2)
        pygame.draw.circle(surf, FRAME,         lc, r + 1)
        pygame.draw.circle(surf, LENS,          lc, r)

    f = _gfont(9)
    for lc in (left, right):
        _blit_outlined(surf, "$", f, (lc[0], lc[1] + 1),
                       BILL_GREEN_LT, BILL_GREEN_DK, outline_w=1)

    # Tiny specular glint on each lens (upper-left)
    for lc in (left, right):
        pygame.draw.circle(surf, GLINT, (lc[0] - 2, lc[1] - 2), 1)

    pygame.draw.line(surf, FRAME,
                     (left[0] + r, left[1]), (right[0] - r, right[1]), 2)
    pygame.draw.line(surf, BILL_GREEN_LT,
                     (left[0] - r + 1, left[1] - r + 2),
                     (right[0] + r - 1, right[1] - r + 2), 1)


# ── Frame builder ────────────────────────────────────────────────────────────

def _build_dollar_frame(wing_angle_deg, glasses_fn):
    """Build a full parrot sprite frame using `glasses_fn` instead of sunglasses."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail
    tail_colors = [
        (200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80),
    ]
    for i, c in enumerate(tail_colors):
        pts = [(2 + i*3, 26 + i*2), (14 + i, 24 + i),
               (20 + i, 30 + i*2), (6 + i*3, 36 + i*2)]
        pygame.draw.polygon(surf, c, pts)
    pygame.draw.line(surf, BIRD_RED_D, (4, 27), (18, 31), 1)
    pygame.draw.line(surf, BIRD_RED_D, (6, 33), (20, 35), 1)

    # Body
    _aaellipse(surf, (120, 20, 25), (34, 35), 19, 14)
    _aaellipse(surf, BIRD_RED,      (32, 32), 19, 14)
    _aaellipse(surf, (255, 100, 100), (30, 29), 13, 8)
    _aaellipse(surf, BIRD_BELLY,    (28, 38), 12, 6)
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    # Wing
    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head
    _aaellipse(surf, (150, 15, 20), (48, 23), 12, 11)
    _aaellipse(surf, BIRD_RED,      (47, 21), 12, 11)
    _aaellipse(surf, (255, 130, 130), (44, 24), 4, 3)
    _aaellipse(surf, (255, 170, 170), (46, 16), 7, 3)

    # Dollar glasses (variant-specific)
    glasses_fn(surf, 50, 20)

    # Beak
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK, beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    pygame.draw.line(surf, BIRD_BEAK_D, (52, 24), (58, 25), 1)

    # Feet
    pygame.draw.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    return surf


def build_dollar_frames(glasses_fn) -> list:
    """Return 4 outlined parrot surfaces for the given glasses variant."""
    return [_add_outline(_build_dollar_frame(a, glasses_fn)) for a in _WING_ANGLES]


# ── Registry ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("FONT $",   _draw_glasses_font_dollar),
    ("COIN $",   _draw_glasses_coin_lens),
    ("NEON $",   _draw_glasses_neon_dollar),
    ("BIG $",    _draw_glasses_big_dollar),
    ("GREEN $",  _draw_glasses_green_dollar),
]
