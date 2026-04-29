"""Five gift-box treatments for the SURPRISE power-up's `?` icon.

Each `draw_<name>(surf, cx, cy, t=0.0)` paints a wrapped present centred
at (cx, cy) into the existing 2 * POWERUP_R = 28 px footprint. The `t`
parameter is for an optional later bob; default 0 = static for the
preview.

Preview-only — nothing in the game imports this yet. Once the user picks
a variant, `entities.PowerUp._draw_surprise` gets rewired to call the
chosen function (or absorb its body)."""
import math
import pathlib
import pygame

from game.draw import UI_GOLD, UI_CREAM, UI_RED, NEAR_BLACK, WHITE, lerp_color


# ── shared palette ──────────────────────────────────────────────────────────

RED_BASE   = (210,  40,  48)
RED_SHADE  = (140,  18,  26)
RED_HI     = (250,  95,  85)
TEAL_BASE  = ( 38, 168, 178)
TEAL_SHADE = ( 18, 110, 122)
TEAL_HI    = (110, 230, 230)
CREAM      = (245, 230, 200)
DK_OUTLINE = ( 26,  10,  12)
GOLD_HI    = (255, 235, 150)
TAG_TAN    = (240, 215, 160)
TAG_DK     = (160, 120,  60)


# ── font cache (shared by every variant for the "?" glyph) ──────────────────

_font_cache: dict = {}
_FONT_PATH = pathlib.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf"


def _font(size):
    f = _font_cache.get(size)
    if f is None:
        f = pygame.font.Font(str(_FONT_PATH), size)
        _font_cache[size] = f
    return f


# ── shared helpers ──────────────────────────────────────────────────────────

def _drop_shadow(surf, cx, cy, w):
    sh = pygame.Surface((w + 4, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (8, 4, 22, 130), sh.get_rect())
    surf.blit(sh, (cx - (w + 4) // 2, cy))


def _draw_box_body(surf, rect, base, shade, hi, *, radius=3, outline=True):
    """Rounded box face: dark frame, vertical-gradient fill, top highlight."""
    if outline:
        pygame.draw.rect(surf, DK_OUTLINE, rect.inflate(2, 2),
                         border_radius=radius + 1)
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
    pygame.draw.line(surf, hi,
                     (rect.x + 2, rect.y + 2),
                     (rect.right - 3, rect.y + 2), 1)


def _draw_bow(surf, cx, cy, fill, hi, sz=4):
    """Small puffy bow: two side loops + centre knot + two trailing tails."""
    # Side loops (oval halves)
    pygame.draw.ellipse(surf, DK_OUTLINE,
                        pygame.Rect(cx - sz - 2, cy - 3, sz + 2, 6))
    pygame.draw.ellipse(surf, fill,
                        pygame.Rect(cx - sz - 1, cy - 2, sz + 1, 4))
    pygame.draw.ellipse(surf, DK_OUTLINE,
                        pygame.Rect(cx, cy - 3, sz + 2, 6))
    pygame.draw.ellipse(surf, fill,
                        pygame.Rect(cx + 1, cy - 2, sz + 1, 4))
    # Inner highlight on each loop
    surf.set_at((cx - sz, cy - 1), hi)
    surf.set_at((cx + sz, cy - 1), hi)
    # Centre knot
    pygame.draw.rect(surf, DK_OUTLINE, pygame.Rect(cx - 2, cy - 3, 5, 6))
    pygame.draw.rect(surf, fill,      pygame.Rect(cx - 1, cy - 2, 3, 4))
    # Trailing tails (V at bottom)
    pygame.draw.line(surf, fill, (cx - 1, cy + 2), (cx - 3, cy + 5), 2)
    pygame.draw.line(surf, fill, (cx + 1, cy + 2), (cx + 3, cy + 5), 2)


def _draw_qmark(surf, cx, cy, size, fill, outline):
    f = _font(size)
    body = f.render("?", True, fill)
    edge = f.render("?", True, outline)
    r = body.get_rect(center=(cx, cy))
    for dx, dy in ((-1,  0), (1,  0), (0, -1), (0,  1),
                   (-1, -1), (1, -1), (-1, 1), (1,  1)):
        surf.blit(edge, (r.x + dx, r.y + dy))
    surf.blit(body, r.topleft)


# ── Variant 1: classic flat front-on present ────────────────────────────────

def draw_classic(surf, cx, cy, t=0.0):
    BOX_W, BOX_H = 22, 18
    rect = pygame.Rect(cx - BOX_W // 2, cy - BOX_H // 2 + 2, BOX_W, BOX_H)
    _drop_shadow(surf, cx, rect.bottom - 2, BOX_W + 2)
    _draw_box_body(surf, rect, RED_BASE, RED_SHADE, RED_HI)

    # Vertical gold ribbon
    pygame.draw.rect(surf, UI_GOLD, (cx - 2, rect.y, 4, rect.h))
    pygame.draw.line(surf, GOLD_HI, (cx - 1, rect.y),
                     (cx - 1, rect.bottom - 1), 1)
    # Horizontal gold ribbon
    ry = rect.y + rect.h // 2 - 1
    pygame.draw.rect(surf, UI_GOLD, (rect.x, ry, rect.w, 3))
    pygame.draw.line(surf, GOLD_HI, (rect.x, ry),
                     (rect.right - 1, ry), 1)
    # Bow at top-centre, sitting just above the box
    _draw_bow(surf, cx, rect.y - 2, UI_GOLD, GOLD_HI)
    # "?" in the lower-right quadrant of the cross-ribbon split
    _draw_qmark(surf, rect.x + rect.w * 3 // 4 - 1,
                rect.y + rect.h * 3 // 4, 11, UI_CREAM, NEAR_BLACK)


# ── Variant 2: 3/4 isometric box with bow on top ────────────────────────────

def draw_bow_top(surf, cx, cy, t=0.0):
    """Lid-on-top isometric — separate lid (lighter) sits on the box body,
    parted by a thin shadow line. Easier to read as 3D than a parallelogram."""
    BOX_W   = 22
    BODY_H  = 13
    LID_H   = 5
    body_rect = pygame.Rect(cx - BOX_W // 2, cy - BODY_H // 2 + 4,
                            BOX_W, BODY_H)
    lid_rect  = pygame.Rect(body_rect.x - 1, body_rect.y - LID_H,
                            BOX_W + 2, LID_H)
    _drop_shadow(surf, cx, body_rect.bottom - 2, BOX_W + 2)

    # Body (deeper red)
    _draw_box_body(surf, body_rect, RED_BASE, RED_SHADE, RED_HI)
    # Shadow under the lid lip
    pygame.draw.line(surf, DK_OUTLINE,
                     (body_rect.x + 1, body_rect.y),
                     (body_rect.right - 2, body_rect.y), 1)

    # Lid — slightly lighter / overhangs by 1px each side for a real "lid" feel
    lid_base  = lerp_color(RED_BASE, RED_HI, 0.20)
    lid_shade = lerp_color(RED_BASE, RED_SHADE, 0.30)
    pygame.draw.rect(surf, DK_OUTLINE, lid_rect.inflate(2, 2), border_radius=3)
    lid_face = pygame.Surface((lid_rect.w, lid_rect.h), pygame.SRCALPHA)
    for y in range(lid_rect.h):
        t_y = y / max(1, lid_rect.h - 1)
        col = lerp_color(lid_base, lid_shade, t_y) + (255,)
        lid_face.fill(col, pygame.Rect(0, y, lid_rect.w, 1))
    mask = pygame.Surface((lid_rect.w, lid_rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=2)
    lid_face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lid_face, lid_rect.topleft)
    # Lid top highlight
    pygame.draw.line(surf, RED_HI,
                     (lid_rect.x + 2, lid_rect.y + 1),
                     (lid_rect.right - 3, lid_rect.y + 1), 1)

    # Vertical gold ribbon over the lid + body
    pygame.draw.rect(surf, UI_GOLD, (cx - 2, lid_rect.y, 4, lid_rect.h))
    pygame.draw.rect(surf, UI_GOLD, (cx - 2, body_rect.y, 4, body_rect.h))
    pygame.draw.line(surf, GOLD_HI,
                     (cx - 1, lid_rect.y), (cx - 1, body_rect.bottom - 1), 1)

    # Bow centred on the lid
    _draw_bow(surf, cx, lid_rect.y - 1, UI_GOLD, GOLD_HI, sz=4)

    # "?" centred on the body face
    _draw_qmark(surf, cx + 5, body_rect.y + body_rect.h // 2 + 1,
                11, UI_CREAM, NEAR_BLACK)


# ── Variant 3: polka-dot wrapping paper ─────────────────────────────────────

def draw_polka(surf, cx, cy, t=0.0):
    BOX_W, BOX_H = 22, 20
    rect = pygame.Rect(cx - BOX_W // 2, cy - BOX_H // 2 + 1, BOX_W, BOX_H)
    _drop_shadow(surf, cx, rect.bottom - 2, BOX_W + 2)
    _draw_box_body(surf, rect, TEAL_BASE, TEAL_SHADE, TEAL_HI)

    # Polka dots — fixed positions, deterministic so the icon stays stable
    dot_positions = (
        (rect.x + 4,  rect.y + 3),
        (rect.x + 14, rect.y + 5),
        (rect.x + 7,  rect.y + 11),
        (rect.x + 17, rect.y + 12),
        (rect.x + 4,  rect.y + 16),
        (rect.x + 14, rect.y + 17),
    )
    for dx, dy in dot_positions:
        pygame.draw.circle(surf, CREAM, (dx, dy), 1)

    # Cream ribbon: vertical + horizontal cross
    pygame.draw.rect(surf, CREAM, (cx - 2, rect.y, 4, rect.h))
    ry = rect.y + rect.h // 2 - 1
    pygame.draw.rect(surf, CREAM, (rect.x, ry, rect.w, 3))
    pygame.draw.line(surf, WHITE, (cx - 1, rect.y),
                     (cx - 1, rect.bottom - 1), 1)
    # Bow at top centre — small + clean
    _draw_bow(surf, cx, rect.y - 2, CREAM, WHITE, sz=3)
    # "?" in the lower-right quadrant (deep red on cream wrap)
    _draw_qmark(surf, rect.x + rect.w * 3 // 4 - 1,
                rect.y + rect.h * 3 // 4, 11, UI_RED, NEAR_BLACK)


# ── Variant 4: diagonal candy-cane stripes ──────────────────────────────────

def draw_stripes(surf, cx, cy, t=0.0):
    BOX_W, BOX_H = 22, 20
    rect = pygame.Rect(cx - BOX_W // 2, cy - BOX_H // 2 + 1, BOX_W, BOX_H)
    _drop_shadow(surf, cx, rect.bottom - 2, BOX_W + 2)

    # Frame + cream base
    pygame.draw.rect(surf, DK_OUTLINE, rect.inflate(2, 2), border_radius=4)
    pygame.draw.rect(surf, CREAM,      rect, border_radius=3)

    # Diagonal red stripes — clipped to the box rect via SRCALPHA mask
    stripe = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    spacing = 6
    for off in range(-rect.h, rect.w + rect.h, spacing):
        pts = [
            (off,           0),
            (off + 3,       0),
            (off + 3 + rect.h, rect.h),
            (off + rect.h,     rect.h),
        ]
        pygame.draw.polygon(stripe, RED_BASE, pts)
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=3)
    stripe.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(stripe, rect.topleft)

    # Top highlight stripe (subtle — over the stripes)
    pygame.draw.line(surf, (255, 245, 220),
                     (rect.x + 2, rect.y + 2),
                     (rect.right - 3, rect.y + 2), 1)

    # Small bow tucked at the top-right corner
    _draw_bow(surf, rect.right - 4, rect.y - 1, RED_BASE, RED_HI, sz=3)
    # "?" centred in the box
    _draw_qmark(surf, cx, cy + 1, 13, RED_BASE, NEAR_BLACK)


# ── Variant 5: plain box with a "?" gift tag on a string ────────────────────

def draw_tag(surf, cx, cy, t=0.0):
    BOX_W, BOX_H = 20, 17
    # Shift box down + left to leave room for the tag at upper-right
    rect = pygame.Rect(cx - BOX_W // 2 - 1, cy - BOX_H // 2 + 4, BOX_W, BOX_H)
    _drop_shadow(surf, rect.centerx, rect.bottom - 2, BOX_W + 2)
    _draw_box_body(surf, rect, RED_BASE, RED_SHADE, RED_HI)

    # Centre cross-ribbon, slim
    pygame.draw.rect(surf, UI_GOLD,
                     (rect.centerx - 1, rect.y, 2, rect.h))
    ry = rect.y + rect.h // 2 - 1
    pygame.draw.rect(surf, UI_GOLD, (rect.x, ry, rect.w, 2))

    # Bow tucked on top-centre of the box
    _draw_bow(surf, rect.centerx, rect.y - 1, UI_GOLD, GOLD_HI, sz=3)

    # String rising diagonally from the bow up to the tag
    str_x0, str_y0 = rect.centerx + 2, rect.y - 2
    str_x1, str_y1 = cx + 9,           cy - 9
    # Curl: render as 3 short segments
    pygame.draw.line(surf, NEAR_BLACK, (str_x0, str_y0),
                     ((str_x0 + str_x1) // 2, str_y0 - 1), 1)
    pygame.draw.line(surf, NEAR_BLACK,
                     ((str_x0 + str_x1) // 2, str_y0 - 1),
                     (str_x1, str_y1), 1)

    # Gift tag — render at 4× internally so the rotation stays crisp,
    # then smoothscale back down to icon resolution.
    SCALE  = 4
    tag_w, tag_h = 14, 12
    tag = pygame.Surface(((tag_w + 2) * SCALE, (tag_h + 2) * SCALE),
                         pygame.SRCALPHA)
    tag_rect = pygame.Rect(SCALE, SCALE, tag_w * SCALE, tag_h * SCALE)
    pygame.draw.rect(tag, DK_OUTLINE,
                     tag_rect.inflate(2 * SCALE, 2 * SCALE),
                     border_radius=3 * SCALE)
    pygame.draw.rect(tag, TAG_TAN, tag_rect, border_radius=2 * SCALE)
    # Notched left edge (hole-punch shape)
    pygame.draw.polygon(tag, DK_OUTLINE, [
        (SCALE,             tag_h * SCALE // 2 + SCALE),
        (3 * SCALE,         tag_h * SCALE // 2 + SCALE - 2 * SCALE),
        (3 * SCALE,         tag_h * SCALE // 2 + SCALE + 2 * SCALE),
    ])
    pygame.draw.polygon(tag, TAG_TAN, [
        (2 * SCALE,         tag_h * SCALE // 2 + SCALE),
        (4 * SCALE,         tag_h * SCALE // 2 + SCALE - SCALE),
        (4 * SCALE,         tag_h * SCALE // 2 + SCALE + SCALE),
    ])
    # Highlight along the top
    pygame.draw.line(tag, (255, 245, 215),
                     (3 * SCALE, 3 * SCALE),
                     (tag_w * SCALE, 3 * SCALE), SCALE)
    # "?" rendered at 4× too so it stays crisp after the rotate+downscale
    f = _font(28)
    body = f.render("?", True, RED_SHADE)
    edge = f.render("?", True, NEAR_BLACK)
    qr = body.get_rect(center=((tag_w + 2) * SCALE // 2 + SCALE,
                               (tag_h + 2) * SCALE // 2 + SCALE // 2))
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        tag.blit(edge, (qr.x + dx, qr.y + dy))
    tag.blit(body, qr.topleft)

    rotated = pygame.transform.rotate(tag, -18)
    final = pygame.transform.smoothscale(
        rotated, (rotated.get_width() // SCALE, rotated.get_height() // SCALE))
    rr = final.get_rect(center=(str_x1 + 2, str_y1 + 2))
    surf.blit(final, rr.topleft)


# ── Registry ────────────────────────────────────────────────────────────────

VARIANTS = [
    ("CLASSIC", draw_classic),
    ("BOW_TOP", draw_bow_top),
    ("POLKA",   draw_polka),
    ("STRIPES", draw_stripes),
    ("TAG",     draw_tag),
]
