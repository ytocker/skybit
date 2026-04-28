"""Five dollar-glasses treatments for the parrot under the triple power-up.

Rendering is split into two phases so the beak sits correctly in the stack:
  1. glasses_fn(surf, cx, cy, "fill")  — lens fills + reflections
  2. beak is drawn here (visible through the right lens opening)
  3. glasses_fn(surf, cx, cy, "frame") — frame rings + $ on top of beak

All variants share oversized lenses (r=9) spread wide across the face.

Preview-only — nothing in the game imports this yet.
"""
import math
import pathlib
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H,
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


def _lens_reflection(surf, lc, r, tint, alpha=90):
    """Semi-transparent sky-tint in the upper half of the lens."""
    rw, rh = r * 2, r
    ts = pygame.Surface((rw, rh), pygame.SRCALPHA)
    pygame.draw.ellipse(ts, (*tint, alpha), ts.get_rect())
    surf.blit(ts, (lc[0] - r, lc[1] - r + 2))


def _frame_highlight(surf, lc, r, color):
    """Bright arc on the upper rim — gives the frame a rounded 3-D look."""
    rect = pygame.Rect(lc[0] - r - 1, lc[1] - r - 1, (r + 1) * 2, (r + 1) * 2)
    pygame.draw.arc(surf, color, rect, math.radians(35), math.radians(155), 1)


# Lens centres: deliberately wide-spaced and oversized so the glasses look
# hilariously big on the parrot's face.
# L = (cx-11, cy+1), R = (cx+9, cy), r = 9
def _lenses(cx, cy):
    return (cx - 11, cy + 1), (cx + 9, cy)


# ── V1 — Chrome Gold ─────────────────────────────────────────────────────────

def _draw_glasses_chrome(surf, cx, cy, phase="fill"):
    L, R = _lenses(cx, cy)
    r = 9
    FRAME_SH = (160,  95,  10)
    FRAME    = (255, 200,  50)
    FRAME_HI = (255, 240, 160)
    LENS     = ( 15,  18,  35)
    TINT     = ( 60, 100, 180)

    if phase == "fill":
        for lc in (L, R):
            pygame.draw.circle(surf, FRAME_SH, lc, r + 2)
            pygame.draw.circle(surf, FRAME,    lc, r + 1)
            pygame.draw.circle(surf, LENS,     lc, r)
            _lens_reflection(surf, lc, r, TINT, alpha=100)

    elif phase == "frame":
        for lc in (L, R):
            pygame.draw.circle(surf, FRAME_SH, lc, r + 2, 3)
            pygame.draw.circle(surf, FRAME,    lc, r + 1, 2)
            _frame_highlight(surf, lc, r, FRAME_HI)
            pygame.draw.circle(surf, WHITE, (lc[0] - 3, lc[1] - 3), 1)
        f = _gfont(14)
        for lc in (L, R):
            _blit_outlined(surf, "$", f, (lc[0], lc[1] + 1), BILL_GREEN, BILL_GREEN_DK)
        pygame.draw.line(surf, FRAME_SH, (L[0]+r, L[1]), (R[0]-r, R[1]), 3)
        pygame.draw.line(surf, FRAME,    (L[0]+r, L[1]), (R[0]-r, R[1]), 1)
        pygame.draw.line(surf, FRAME,
                         (L[0]-r+2, L[1]-r+2), (R[0]+r-2, R[1]-r+2), 1)


# ── V2 — Power Coin ───────────────────────────────────────────────────────────

def _draw_glasses_coin(surf, cx, cy, phase="fill"):
    L, R = _lenses(cx, cy)
    r = 9
    INNER = (255, 235, 110)
    HI    = (255, 245, 180)

    if phase == "fill":
        for lc in (L, R):
            pygame.draw.circle(surf, COIN_DARK, lc, r + 2)
            pygame.draw.circle(surf, COIN_GOLD, lc, r + 1)
            pygame.draw.circle(surf, COIN_GOLD, lc, r)
            pygame.draw.circle(surf, INNER,     lc, r - 3, 1)
            _lens_reflection(surf, lc, r, (255, 250, 200), alpha=70)

    elif phase == "frame":
        for lc in (L, R):
            pygame.draw.circle(surf, COIN_DARK, lc, r + 2, 3)
            pygame.draw.circle(surf, COIN_GOLD, lc, r + 1, 2)
            _frame_highlight(surf, lc, r, HI)
            pygame.draw.circle(surf, WHITE, (lc[0] - 3, lc[1] - 3), 2)
        f = _gfont(14)
        for lc in (L, R):
            _blit_outlined(surf, "$", f, (lc[0], lc[1] + 1), BILL_GREEN, BILL_GREEN_DK)
        pygame.draw.line(surf, COIN_DARK, (L[0]+r, L[1]), (R[0]-r, R[1]), 3)
        pygame.draw.line(surf, COIN_GOLD, (L[0]+r, L[1]), (R[0]-r, R[1]), 1)
        pygame.draw.line(surf, COIN_DARK,
                         (L[0]-r+2, L[1]-r+2), (R[0]+r-2, R[1]-r+2), 1)


# ── V3 — Neon Blast ───────────────────────────────────────────────────────────

def _draw_glasses_neon(surf, cx, cy, phase="fill"):
    L, R = _lenses(cx, cy)
    r = 9
    NEON     = ( 80, 255, 160)
    NEON_DIM = ( 30, 160,  85)
    NEON_DRK = (  8,  20,  14)
    LENS     = (  5,  10,   8)

    if phase == "fill":
        for lc in (L, R):
            glow = pygame.Surface(((r+5)*2, (r+5)*2), pygame.SRCALPHA)
            gc   = (r+5, r+5)
            pygame.draw.circle(glow, (*NEON, 25), gc, r+5)
            pygame.draw.circle(glow, (*NEON, 50), gc, r+3)
            surf.blit(glow, (lc[0]-r-5, lc[1]-r-5))
            pygame.draw.circle(surf, NEON_DIM,  lc, r+2)
            pygame.draw.circle(surf, NEON,      lc, r+1)
            pygame.draw.circle(surf, LENS,      lc, r)

    elif phase == "frame":
        for lc in (L, R):
            pygame.draw.circle(surf, NEON_DIM, lc, r+2, 3)
            pygame.draw.circle(surf, NEON,     lc, r+1, 2)
            _frame_highlight(surf, lc, r, (200, 255, 220))
            gs = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*NEON, 55), (r, r), r-2)
            pygame.draw.circle(gs, (*NEON, 85), (r, r), r-5)
            surf.blit(gs, (lc[0]-r, lc[1]-r))
        f = _gfont(14)
        for lc in (L, R):
            _blit_outlined(surf, "$", f, (lc[0], lc[1]+1), NEON, NEON_DIM)
        pygame.draw.line(surf, NEON,    (L[0]+r, L[1]), (R[0]-r, R[1]), 2)
        pygame.draw.line(surf, NEON_DIM,(L[0]-r+2, L[1]-r+2),
                                        (R[0]+r-2, R[1]-r+2), 1)


# ── V4 — Gunmetal Embossed ────────────────────────────────────────────────────

def _draw_glasses_gunmetal(surf, cx, cy, phase="fill"):
    L, R = _lenses(cx, cy)
    r = 9
    STEEL_SH = ( 30,  30,  45)
    STEEL    = ( 80,  85, 110)
    STEEL_HI = (155, 160, 195)
    LENS     = ( 18,  20,  32)
    TINT     = ( 50,  60, 120)

    if phase == "fill":
        for lc in (L, R):
            pygame.draw.circle(surf, STEEL_SH, lc, r+2)
            pygame.draw.circle(surf, STEEL,    lc, r+1)
            pygame.draw.circle(surf, LENS,     lc, r)
            _lens_reflection(surf, lc, r, TINT, alpha=80)

    elif phase == "frame":
        for lc in (L, R):
            pygame.draw.circle(surf, STEEL_SH, lc, r+2, 3)
            pygame.draw.circle(surf, STEEL,    lc, r+1, 2)
            _frame_highlight(surf, lc, r, STEEL_HI)
            pygame.draw.circle(surf, (220, 225, 255), (lc[0]-3, lc[1]-3), 1)
        f = _gfont(14)
        for lc in (L, R):
            sh   = f.render("$", True, (10, 10, 20))
            hi   = f.render("$", True, (255, 245, 200))
            body = f.render("$", True, COIN_GOLD)
            cx2, cy2 = lc[0], lc[1]+1
            surf.blit(sh,   sh.get_rect(center=(cx2+1, cy2+1)).topleft)
            surf.blit(hi,   hi.get_rect(center=(cx2-1, cy2-1)).topleft)
            surf.blit(body, body.get_rect(center=(cx2,  cy2  )).topleft)
        pygame.draw.line(surf, STEEL,    (L[0]+r, L[1]), (R[0]-r, R[1]), 3)
        pygame.draw.line(surf, STEEL_HI, (L[0]+r, L[1]), (R[0]-r, R[1]), 1)
        pygame.draw.line(surf, STEEL_HI,
                         (L[0]-r+2, L[1]-r+2), (R[0]+r-2, R[1]-r+2), 1)


# ── V5 — Emerald Rich ────────────────────────────────────────────────────────

def _draw_glasses_emerald(surf, cx, cy, phase="fill"):
    L, R = _lenses(cx, cy)
    r = 9
    FRAME_SH = ( 20,  72,  42)
    FRAME    = ( 50, 160,  90)
    FRAME_HI = (130, 235, 165)
    LENS     = ( 10,  38,  22)
    TINT     = ( 40, 130,  80)

    if phase == "fill":
        for lc in (L, R):
            pygame.draw.circle(surf, FRAME_SH, lc, r+2)
            pygame.draw.circle(surf, FRAME,    lc, r+1)
            pygame.draw.circle(surf, LENS,     lc, r)
            _lens_reflection(surf, lc, r, TINT, alpha=90)

    elif phase == "frame":
        for lc in (L, R):
            pygame.draw.circle(surf, FRAME_SH, lc, r+2, 3)
            pygame.draw.circle(surf, FRAME,    lc, r+1, 2)
            _frame_highlight(surf, lc, r, FRAME_HI)
            pygame.draw.circle(surf, (200, 255, 215), (lc[0]-3, lc[1]-3), 1)
        f = _gfont(14)
        for lc in (L, R):
            _blit_outlined(surf, "$", f, (lc[0], lc[1]+1),
                           (215, 255, 225), BILL_GREEN_DK)
        pygame.draw.line(surf, FRAME_SH, (L[0]+r, L[1]), (R[0]-r, R[1]), 3)
        pygame.draw.line(surf, FRAME_HI, (L[0]+r, L[1]), (R[0]-r, R[1]), 1)
        pygame.draw.line(surf, FRAME_HI,
                         (L[0]-r+2, L[1]-r+2), (R[0]+r-2, R[1]-r+2), 1)


# ── Frame builder ─────────────────────────────────────────────────────────────

def _build_dollar_frame(wing_angle_deg, glasses_fn):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail
    for i, c in enumerate([(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)]):
        pts = [(2+i*3, 26+i*2), (14+i, 24+i), (20+i, 30+i*2), (6+i*3, 36+i*2)]
        pygame.draw.polygon(surf, c, pts)
    pygame.draw.line(surf, BIRD_RED_D, (4, 27), (18, 31), 1)
    pygame.draw.line(surf, BIRD_RED_D, (6, 33), (20, 35), 1)

    # Body
    _aaellipse(surf, (120, 20, 25),   (34, 35), 19, 14)
    _aaellipse(surf, BIRD_RED,         (32, 32), 19, 14)
    _aaellipse(surf, (255, 100, 100),  (30, 29), 13,  8)
    _aaellipse(surf, BIRD_BELLY,       (28, 38), 12,  6)
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21))

    # Wing
    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head
    _aaellipse(surf, (150, 15, 20),   (48, 23), 12, 11)
    _aaellipse(surf, BIRD_RED,         (47, 21), 12, 11)
    _aaellipse(surf, (255, 130, 130),  (44, 24),  4,  3)
    _aaellipse(surf, (255, 170, 170),  (46, 16),  7,  3)

    # Phase 1: lens fills (beak will render on top of these)
    glasses_fn(surf, 50, 20, "fill")

    # Beak — drawn after lens fills so it's visible through the right lens opening.
    # The frame rings (phase 2) will then wrap cleanly around it.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BIRD_BEAK,   beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, (255, 230, 150), (55, 22), (59, 24), 1)
    pygame.draw.line(surf, BIRD_BEAK_D,    (52, 24), (58, 25), 1)

    # Phase 2: frame rings + $ (sit on top of the beak where they overlap)
    glasses_fn(surf, 50, 20, "frame")

    # Feet
    pygame.draw.line(surf, BIRD_BEAK_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BIRD_BEAK_D, (34, 45), (36, 49), 2)

    return surf


def build_dollar_frames(glasses_fn) -> list:
    """Return 4 outlined parrot surfaces for the given glasses variant."""
    return [_add_outline(_build_dollar_frame(a, glasses_fn)) for a in _WING_ANGLES]


# ── Registry ──────────────────────────────────────────────────────────────────

VARIANTS = [
    ("CHROME",   _draw_glasses_chrome),
    ("COIN",     _draw_glasses_coin),
    ("NEON",     _draw_glasses_neon),
    ("GUNMETAL", _draw_glasses_gunmetal),
    ("EMERALD",  _draw_glasses_emerald),
]
