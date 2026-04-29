"""Five iterations on the CLASSIC red-gift-box treatment.

Round 2: every variant keeps the red-box-with-bow theme but tries a
different ribbon layout, so the "?" can sit large and centred on the
front face. Drawn into a 64×64 scratch surface (a 2× of the in-game
2 * POWERUP_R = 28-px footprint) so curves and the glyph stay sharp;
the in-game integration is expected to smoothscale the surface down to
28 px when wired into PowerUp._draw_surprise.

Each `draw_<name>(surf, cx, cy, t=0.0)` paints a wrapped present
centred at (cx, cy). `t` is reserved for an optional bob; default 0 =
static for the preview.

Preview-only — nothing in the game imports this yet."""
import math
import pathlib
import pygame

from game.draw import UI_GOLD, UI_CREAM, UI_RED, NEAR_BLACK, WHITE, lerp_color


# ── shared palette ──────────────────────────────────────────────────────────

RED_BASE   = (210,  40,  48)
RED_SHADE  = (140,  18,  26)
RED_HI     = (250,  95,  85)
CREAM      = (245, 230, 200)
DK_OUTLINE = ( 26,  10,  12)
GOLD_HI    = (255, 235, 150)


# ── font cache ──────────────────────────────────────────────────────────────

_font_cache: dict = {}
_FONT_PATH = pathlib.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf"


def _font(size):
    f = _font_cache.get(size)
    if f is None:
        f = pygame.font.Font(str(_FONT_PATH), size)
        _font_cache[size] = f
    return f


# ── shared helpers (sized for the 64-px / 56-footprint canvas) ──────────────

def _drop_shadow(surf, cx, cy, w):
    sh = pygame.Surface((w + 8, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 22, 130), sh.get_rect())
    surf.blit(sh, (cx - (w + 8) // 2, cy))


def _draw_box_body(surf, rect, base, shade, hi, *, radius=6):
    """Rounded box face: dark frame, vertical-gradient fill, top highlight."""
    pygame.draw.rect(surf, DK_OUTLINE, rect.inflate(4, 4),
                     border_radius=radius + 2)
    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        col = lerp_color(base, shade, t) + (255,)
        body.fill(col, pygame.Rect(0, y, rect.w, 1))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=radius)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, rect.topleft)
    # Top sheen line
    pygame.draw.line(surf, hi,
                     (rect.x + 4, rect.y + 3),
                     (rect.right - 5, rect.y + 3), 2)


def _draw_bow(surf, cx, cy, fill, hi):
    """Puffy bow at 2× scale: outlined side loops + knot + trailing tails."""
    # Side loops — outline first, then fill
    pygame.draw.ellipse(surf, DK_OUTLINE,
                        pygame.Rect(cx - 13, cy - 6, 13, 12))
    pygame.draw.ellipse(surf, fill,
                        pygame.Rect(cx - 12, cy - 5, 11, 10))
    pygame.draw.ellipse(surf, DK_OUTLINE,
                        pygame.Rect(cx,       cy - 6, 13, 12))
    pygame.draw.ellipse(surf, fill,
                        pygame.Rect(cx + 1,   cy - 5, 11, 10))
    # Inner highlights on each loop
    pygame.draw.ellipse(surf, hi, pygame.Rect(cx - 10, cy - 4,  4, 3))
    pygame.draw.ellipse(surf, hi, pygame.Rect(cx + 6,  cy - 4,  4, 3))
    # Centre knot
    pygame.draw.rect(surf, DK_OUTLINE, pygame.Rect(cx - 4, cy - 6, 9, 12),
                     border_radius=2)
    pygame.draw.rect(surf, fill,      pygame.Rect(cx - 3, cy - 5, 7, 10),
                     border_radius=2)
    pygame.draw.line(surf, hi, (cx - 1, cy - 4), (cx - 1, cy + 3), 1)
    # Trailing tails (V shape descending into the box)
    pygame.draw.line(surf, DK_OUTLINE, (cx - 2, cy + 4), (cx - 7, cy + 11), 4)
    pygame.draw.line(surf, DK_OUTLINE, (cx + 2, cy + 4), (cx + 7, cy + 11), 4)
    pygame.draw.line(surf, fill,      (cx - 2, cy + 4), (cx - 6, cy + 10), 2)
    pygame.draw.line(surf, fill,      (cx + 2, cy + 4), (cx + 6, cy + 10), 2)


def _draw_qmark(surf, cx, cy, size, fill, outline, *, thick=2):
    """Bold '?' with an evenly-stamped dark outline, centred on (cx, cy)."""
    f = _font(size)
    body = f.render("?", True, fill)
    edge = f.render("?", True, outline)
    r = body.get_rect(center=(cx, cy))
    for dx in range(-thick, thick + 1):
        for dy in range(-thick, thick + 1):
            if dx * dx + dy * dy <= thick * thick and (dx or dy):
                surf.blit(edge, (r.x + dx, r.y + dy))
    surf.blit(body, r.topleft)


# ── shared box geometry ─────────────────────────────────────────────────────
# Designed for a 64-px scratch surface (16-px margin around a 48-wide box).

BOX_W  = 46
BOX_H  = 40
BOW_DY = 6   # bow centre this many px above the box top edge


def _box_rect(cx, cy):
    return pygame.Rect(cx - BOX_W // 2, cy - BOX_H // 2 + 4, BOX_W, BOX_H)


def _ribbon_h(surf, rect, w=8):
    """Horizontal gold ribbon across the box mid-line."""
    ry = rect.y + rect.h // 2 - w // 2
    pygame.draw.rect(surf, UI_GOLD, (rect.x, ry, rect.w, w))
    pygame.draw.line(surf, GOLD_HI, (rect.x, ry + 1),
                     (rect.right - 1, ry + 1), 1)


def _ribbon_v(surf, rect, w=8):
    """Vertical gold ribbon down the box centre."""
    rx = rect.centerx - w // 2
    pygame.draw.rect(surf, UI_GOLD, (rx, rect.y, w, rect.h))
    pygame.draw.line(surf, GOLD_HI, (rx + 1, rect.y),
                     (rx + 1, rect.bottom - 1), 1)


# ── Variant 1: classic cross + big centre "?" over the intersection ─────────

def draw_cross(surf, cx, cy, t=0.0):
    rect = _box_rect(cx, cy)
    _drop_shadow(surf, cx, rect.bottom - 4, BOX_W + 4)
    _draw_box_body(surf, rect, RED_BASE, RED_SHADE, RED_HI)
    _ribbon_v(surf, rect, w=8)
    _ribbon_h(surf, rect, w=8)
    _draw_bow(surf, cx, rect.y - BOW_DY, UI_GOLD, GOLD_HI)
    _draw_qmark(surf, rect.centerx, rect.centery, 32, UI_CREAM, NEAR_BLACK)


# ── Variant 2: diagonal X ribbon + big centre "?" ───────────────────────────

def draw_diagonal(surf, cx, cy, t=0.0):
    rect = _box_rect(cx, cy)
    _drop_shadow(surf, cx, rect.bottom - 4, BOX_W + 4)
    _draw_box_body(surf, rect, RED_BASE, RED_SHADE, RED_HI)

    # Two diagonal ribbons clipped to the rounded box, drawn into a mask
    rib = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pad = 6
    pygame.draw.line(rib, UI_GOLD,
                     (-pad, -pad), (rect.w + pad, rect.h + pad), 8)
    pygame.draw.line(rib, UI_GOLD,
                     (rect.w + pad, -pad), (-pad, rect.h + pad), 8)
    pygame.draw.line(rib, GOLD_HI,
                     (-pad, -pad + 2), (rect.w + pad, rect.h + pad + 2), 1)
    pygame.draw.line(rib, GOLD_HI,
                     (rect.w + pad, -pad + 2), (-pad, rect.h + pad + 2), 1)
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=6)
    rib.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(rib, rect.topleft)

    _draw_bow(surf, cx, rect.y - BOW_DY, UI_GOLD, GOLD_HI)
    _draw_qmark(surf, rect.centerx, rect.centery, 32, UI_CREAM, NEAR_BLACK)


# ── Variant 3: single horizontal ribbon + big centre "?" ────────────────────

def draw_horizontal(surf, cx, cy, t=0.0):
    rect = _box_rect(cx, cy)
    _drop_shadow(surf, cx, rect.bottom - 4, BOX_W + 4)
    _draw_box_body(surf, rect, RED_BASE, RED_SHADE, RED_HI)
    # Ribbon thicker than CROSS's, since it's the only one
    _ribbon_h(surf, rect, w=10)
    _draw_bow(surf, cx, rect.y - BOW_DY, UI_GOLD, GOLD_HI)
    _draw_qmark(surf, rect.centerx, rect.centery, 32, UI_CREAM, NEAR_BLACK)


# ── Variant 4: no ribbon at all, just box + bow + huge "?" ──────────────────

def draw_no_ribbon(surf, cx, cy, t=0.0):
    rect = _box_rect(cx, cy)
    _drop_shadow(surf, cx, rect.bottom - 4, BOX_W + 4)
    _draw_box_body(surf, rect, RED_BASE, RED_SHADE, RED_HI)
    _draw_bow(surf, cx, rect.y - BOW_DY, UI_GOLD, GOLD_HI)
    # Bigger glyph since nothing competes with it
    _draw_qmark(surf, rect.centerx, rect.centery + 1, 38, UI_CREAM,
                NEAR_BLACK, thick=3)


# ── Variant 5: cross ribbon + cream medallion with red "?" inside ───────────

def draw_badge(surf, cx, cy, t=0.0):
    rect = _box_rect(cx, cy)
    _drop_shadow(surf, cx, rect.bottom - 4, BOX_W + 4)
    _draw_box_body(surf, rect, RED_BASE, RED_SHADE, RED_HI)
    _ribbon_v(surf, rect, w=6)
    _ribbon_h(surf, rect, w=6)
    _draw_bow(surf, cx, rect.y - BOW_DY, UI_GOLD, GOLD_HI)

    # Cream medallion centred on the cross intersection
    R = 13
    pygame.draw.circle(surf, DK_OUTLINE, (rect.centerx, rect.centery), R + 1)
    pygame.draw.circle(surf, CREAM,      (rect.centerx, rect.centery), R)
    # Top sheen on the medallion
    pygame.draw.arc(surf, WHITE,
                    pygame.Rect(rect.centerx - R + 2, rect.centery - R + 2,
                                (R - 2) * 2, (R - 2) * 2),
                    math.radians(40), math.radians(140), 2)
    # "?" in deep red on the cream medallion
    _draw_qmark(surf, rect.centerx, rect.centery + 1, 24, RED_SHADE,
                NEAR_BLACK, thick=1)


# ── Registry ────────────────────────────────────────────────────────────────

VARIANTS = [
    ("CROSS",      draw_cross),
    ("DIAGONAL",   draw_diagonal),
    ("HORIZONTAL", draw_horizontal),
    ("NO_RIBBON",  draw_no_ribbon),
    ("BADGE",      draw_badge),
]
