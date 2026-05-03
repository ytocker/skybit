"""Five magician-hat treatments for the parrot under the triple power-up.

Each `draw_<name>(surf, hx, hy)` paints a large golden hat with a `$` on
top of the parrot. (hx, hy) is the brim's bottom-centre — the point where
the hat meets the head crown.

`build_hat_frames(hat_fn)` returns 4 outlined parrot surfaces (one per
wing angle) with the chosen hat composited on top of the normal parrot
sprite (which keeps its original aviator sunglasses).

Preview-only — nothing in the game imports this yet. The chosen hat
gets wired into `Bird.draw` in a follow-up.
"""
import math
import pathlib
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H,
    _WING_ANGLES, _build_frame, _build_fried_frame, _add_outline,
    _cyan_tint_in_place,
)
from game.draw import COIN_GOLD, COIN_DARK, WHITE, NEAR_BLACK
from game.dollar_variants import BILL_GREEN, BILL_GREEN_DK

# ── canvas ───────────────────────────────────────────────────────────────────
# Composite is tall enough for a magician hat AND keeps the parrot centred
# vertically (parrot at composite-y 20..80, with 20 px hat space above and
# 20 px empty space below). Centring the parrot means rotation in
# get_hat_parrot can re-use the existing center-blit pattern in Bird.draw.
COMPOSITE_W = SPRITE_W           # 64
COMPOSITE_H = 100                # parrot center stays at composite center (50)
PARROT_DY   = 20                 # parrot blitted at composite (0, 20)
HAT_HX      = 47                 # head centre x (matches parrot._build_frame)
HAT_HY      = 10 + PARROT_DY     # 30 — composite y of the head crown

# ── palette ──────────────────────────────────────────────────────────────────
GOLD_DK   = (160, 100,  20)
GOLD      = (255, 200,  50)
GOLD_MID  = (220, 165,  35)
GOLD_LT   = (255, 240, 130)
BAND_DK   = ( 35,  20,   8)
BAND_HI   = ( 85,  55,  20)

# ── font ─────────────────────────────────────────────────────────────────────
_FONT_PATH = str(pathlib.Path(__file__).parent / "assets" / "LiberationSans-Bold.ttf")
_font_cache: dict = {}


def _font(size):
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


# ── shared helpers ───────────────────────────────────────────────────────────

def _draw_brim(surf, hx, hy, half_w=18):
    """Wide ribbon-brim with a dark underside and gold top so it reads
    as a clear separate piece below the crown. (hx,hy) = brim top-centre
    (i.e. the line where the crown meets the brim)."""
    # Cast shadow on the head behind/below the brim
    sh = pygame.Surface((half_w * 2 + 8, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
    surf.blit(sh, (hx - half_w - 4, hy + 1))

    # Dark underside (full ellipse) — gives the brim visible thickness
    pygame.draw.ellipse(surf, BAND_DK,
                        (hx - half_w - 1, hy, (half_w + 1) * 2, 7))
    # Gold top (slightly inset so the dark underside shows on the bottom)
    pygame.draw.ellipse(surf, GOLD_DK,
                        (hx - half_w, hy - 1, half_w * 2, 6))
    pygame.draw.ellipse(surf, GOLD,
                        (hx - half_w + 1, hy, half_w * 2 - 2, 4))
    # Bright sheen across the brim top
    pygame.draw.line(surf, GOLD_LT,
                     (hx - half_w + 3, hy + 1), (hx + half_w - 3, hy + 1), 1)


def _draw_crown_cylinder(surf, hx, hy, half_w, height):
    """Cylindrical top-hat crown sitting on the brim. (hx, hy) = crown
    bottom-centre — the crown rises from there up by `height` px."""
    top_y  = hy - height
    left_x = hx - half_w
    w      = half_w * 2

    # Side body — drawn as ellipses at top and bottom plus a connecting rect
    # to suggest a true cylinder.
    pygame.draw.rect(surf, GOLD_DK,
                     (left_x - 1, top_y + 1, w + 2, height - 2))
    pygame.draw.rect(surf, GOLD,
                     (left_x, top_y + 2, w, height - 4))
    # Left highlight column
    pygame.draw.rect(surf, GOLD_LT, (left_x + 2, top_y + 3, 2, height - 8))
    # Right shadow column
    pygame.draw.rect(surf, GOLD_MID,(left_x + w - 3, top_y + 3, 2, height - 8))

    # Bottom rim of the cylinder (front-facing curve)
    pygame.draw.ellipse(surf, GOLD_DK,
                        (left_x - 1, hy - 4, w + 2, 7))
    pygame.draw.ellipse(surf, GOLD,
                        (left_x, hy - 3, w, 5))

    # Cylinder top — a clear ellipse so the hat reads as 3-D
    pygame.draw.ellipse(surf, GOLD_DK, (left_x - 1, top_y - 1, w + 2, 6))
    pygame.draw.ellipse(surf, GOLD,    (left_x + 1, top_y,     w - 2, 4))
    pygame.draw.ellipse(surf, GOLD_LT, (left_x + 3, top_y + 1, w - 6, 1))

    # Dark hatband at the base of the crown
    band_h = max(3, height // 7)
    pygame.draw.rect(surf, BAND_DK, (left_x, hy - band_h - 1, w, band_h))
    pygame.draw.line(surf, BAND_HI,
                     (left_x + 1, hy - band_h - 1),
                     (left_x + w - 2, hy - band_h - 1), 1)


def _draw_star(surf, cx, cy, r, color):
    """Simple 4-point sparkle star centred at (cx,cy)."""
    pygame.draw.polygon(surf, color,
                        [(cx, cy - r), (cx + r // 2, cy),
                         (cx, cy + r), (cx - r // 2, cy)])
    pygame.draw.polygon(surf, color,
                        [(cx - r, cy), (cx, cy - r // 2),
                         (cx + r, cy), (cx, cy + r // 2)])


# ── V1 — Classic top hat ─────────────────────────────────────────────────────

def draw_top_hat(surf, hx, hy):
    """Classic magician top hat: tall gold cylinder, wide dark-underside brim,
    bold green $ on the front of the crown."""
    crown_half = 11
    crown_h    = 24
    _draw_crown_cylinder(surf, hx, hy, crown_half, crown_h)
    _draw_brim(surf, hx, hy, half_w=16)

    f = _font(15)
    cy = hy - crown_h // 2 - 2
    _blit_outlined(surf, "$", f, (hx, cy), BILL_GREEN, BILL_GREEN_DK, outline_w=1)


# ── V2 — Wizard cone with stars ──────────────────────────────────────────────

def draw_wizard(surf, hx, hy):
    """Tall pointed wizard hat — conical gold body, sparkle stars, $ on the front."""
    h     = 26
    base_half = 13
    tip   = (hx + 2, hy - h)   # tip leans slightly right for character

    # Cone — outer dark outline then gold fill
    outer = [(hx - base_half - 1, hy - 1), (hx + base_half + 1, hy - 1), tip]
    inner = [(hx - base_half,     hy - 1), (hx + base_half,     hy - 1),
             (tip[0] - 1, tip[1] + 1)]
    pygame.draw.polygon(surf, GOLD_DK, outer)
    pygame.draw.polygon(surf, GOLD,    inner)

    # Vertical highlight ribbon down the left of the cone
    hi = [(hx - base_half + 2, hy - 3),
          (hx - base_half + 5, hy - 3),
          (tip[0] - 2,         tip[1] + 4)]
    pygame.draw.polygon(surf, GOLD_LT, hi)

    # Brim
    _draw_brim(surf, hx, hy, half_w=15)

    # Sparkle stars dotted around the cone
    _draw_star(surf, hx - base_half + 4, hy - 14, 2, GOLD_LT)
    _draw_star(surf, hx + base_half - 4, hy - 10, 2, GOLD_LT)
    _draw_star(surf, hx + 1,             hy - 23, 2, WHITE)

    # $ glyph mid-cone
    f = _font(13)
    _blit_outlined(surf, "$", f, (hx, hy - 12),
                   BILL_GREEN, BILL_GREEN_DK, outline_w=1)


# ── V3 — Tilted top hat ──────────────────────────────────────────────────────

def draw_tilt_top(surf, hx, hy):
    """Top hat rendered onto a scratch surface and rotated ~14° for whimsy."""
    SZ = 64
    scratch = pygame.Surface((SZ, SZ), pygame.SRCALPHA)
    cx, cy = SZ // 2, SZ - 10
    crown_half = 11
    crown_h    = 24
    _draw_crown_cylinder(scratch, cx, cy, crown_half, crown_h)
    _draw_brim(scratch, cx, cy, half_w=16)

    f = _font(15)
    _blit_outlined(scratch, "$", f, (cx, cy - crown_h // 2 - 2),
                   BILL_GREEN, BILL_GREEN_DK, outline_w=1)

    # Rotate (tilt right) — pygame.transform.rotate spins around the centre
    # of the source surface, so the brim anchor moves predictably.
    angle_deg = -14
    rotated = pygame.transform.rotate(scratch, angle_deg)
    rw, rh  = rotated.get_size()
    angle_rad = math.radians(angle_deg)
    sx = (cx - SZ / 2) * math.cos(angle_rad) - (cy - SZ / 2) * math.sin(angle_rad)
    sy = (cx - SZ / 2) * math.sin(angle_rad) + (cy - SZ / 2) * math.cos(angle_rad)
    new_cx = rw / 2 + sx
    new_cy = rh / 2 + sy
    surf.blit(rotated, (int(hx - new_cx), int(hy - new_cy)))


# ── V4 — Stars-on-band magician ──────────────────────────────────────────────

def draw_stars(surf, hx, hy):
    """Top hat with a thicker dark band sprinkled with sparkle stars."""
    crown_half = 11
    crown_h    = 24
    _draw_crown_cylinder(surf, hx, hy, crown_half, crown_h)

    # Override: thicker band over the bottom 7 px of the crown.
    band_top = hy - 8
    pygame.draw.rect(surf, BAND_DK,
                     (hx - crown_half, band_top, crown_half * 2, 7))
    pygame.draw.line(surf, BAND_HI,
                     (hx - crown_half + 1, band_top),
                     (hx + crown_half - 2, band_top), 1)
    # Stars decorating the side of the band (skip centre — that's the $)
    for sx in (hx - crown_half + 3, hx + crown_half - 4):
        _draw_star(surf, sx, band_top + 4, 2, GOLD_LT)

    _draw_brim(surf, hx, hy, half_w=16)

    # $ glyph in the upper portion of the crown, with two flanking stars
    f = _font(14)
    _blit_outlined(surf, "$", f, (hx, hy - crown_h // 2 - 3),
                   BILL_GREEN, BILL_GREEN_DK, outline_w=1)
    _draw_star(surf, hx - 7, hy - crown_h // 2 - 3, 1, WHITE)
    _draw_star(surf, hx + 7, hy - crown_h // 2 - 3, 1, WHITE)


# ── V5 — Stovepipe (extra-tall, slim) ────────────────────────────────────────

def draw_stovepipe(surf, hx, hy):
    """Extra-tall slim stovepipe — biggest $ dominating the front."""
    crown_half = 9
    crown_h    = 28
    _draw_crown_cylinder(surf, hx, hy, crown_half, crown_h)
    _draw_brim(surf, hx, hy, half_w=17)

    f = _font(18)
    _blit_outlined(surf, "$", f, (hx, hy - crown_h // 2 - 1),
                   BILL_GREEN, BILL_GREEN_DK, outline_w=1)


# ── Themed stovepipe palettes (for stacked-powerup combos) ──────────────────
# Each combo dresses the stovepipe in colours that match the underlying
# bird mode so the hat reads as part of the theme, not a foreign object.
# `dollar`/`dollar_dk`/`dollar_hi` style the `$` glyph; `spot`/`spot_hi`
# add fried-batter bumps (None = no bumps for non-fried hats).
HAT_PALETTE_KFC = {
    # Crispy fried-chicken tones — warm oranges/browns matching the
    # KFC bird's batter colours.
    "bright":     (245, 195, 110),
    "main":       (215, 145,  55),
    "mid":        (180, 110,  35),
    "dark":       (120,  70,  20),
    "band_dk":    ( 65,  35,  10),
    "band_hi":    (130,  80,  25),
    # `$` in the bird's darkest fried-brown tone — reads as branded /
    # burnt into the warm hat body, same colour as the bird's spots.
    "dollar":     ( 45,  22,   2),
    "dollar_dk":  ( 20,  10,   0),
    "dollar_hi":  (115,  70,  20),
    "spot":       ( 75,  40,   5),
    "spot_hi":    (245, 200, 130),
}
HAT_PALETTE_GHOST = {
    # Spectral cyans matching the ghost bird's body palette.
    "bright":     (220, 245, 255),
    "main":       (140, 200, 230),
    "mid":        (100, 170, 210),
    "dark":       ( 55, 105, 155),
    "band_dk":    ( 25,  55,  95),
    "band_hi":    ( 90, 140, 180),
    # Sky-blue `$` (user picked from the light-blue picker round).
    "dollar":     (115, 175, 230),
    "dollar_dk":  ( 50,  95, 165),
    "dollar_hi":  (185, 215, 250),
    "spot":       None,    # spectral hat has no fried texture
    "spot_hi":    None,
}


def _draw_brim_themed(surf, hx, hy, P, half_w=17):
    """Themed version of _draw_brim — same geometry, palette swappable."""
    sh = pygame.Surface((half_w * 2 + 8, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
    surf.blit(sh, (hx - half_w - 4, hy + 1))
    pygame.draw.ellipse(surf, P["band_dk"],
                        (hx - half_w - 1, hy, (half_w + 1) * 2, 7))
    pygame.draw.ellipse(surf, P["dark"],
                        (hx - half_w, hy - 1, half_w * 2, 6))
    pygame.draw.ellipse(surf, P["main"],
                        (hx - half_w + 1, hy, half_w * 2 - 2, 4))
    pygame.draw.line(surf, P["bright"],
                     (hx - half_w + 3, hy + 1), (hx + half_w - 3, hy + 1), 1)


def _draw_crown_cylinder_themed(surf, hx, hy, half_w, height, P):
    """Themed version of _draw_crown_cylinder."""
    top_y = hy - height
    left_x = hx - half_w
    w = half_w * 2

    pygame.draw.rect(surf, P["dark"], (left_x - 1, top_y + 1, w + 2, height - 2))
    pygame.draw.rect(surf, P["main"], (left_x, top_y + 2, w, height - 4))
    pygame.draw.rect(surf, P["bright"], (left_x + 2, top_y + 3, 2, height - 8))
    pygame.draw.rect(surf, P["mid"], (left_x + w - 3, top_y + 3, 2, height - 8))

    pygame.draw.ellipse(surf, P["dark"], (left_x - 1, hy - 4, w + 2, 7))
    pygame.draw.ellipse(surf, P["main"], (left_x, hy - 3, w, 5))

    pygame.draw.ellipse(surf, P["dark"], (left_x - 1, top_y - 1, w + 2, 6))
    pygame.draw.ellipse(surf, P["main"], (left_x + 1, top_y, w - 2, 4))
    pygame.draw.ellipse(surf, P["bright"], (left_x + 3, top_y + 1, w - 6, 1))

    band_h = max(3, height // 7)
    pygame.draw.rect(surf, P["band_dk"], (left_x, hy - band_h - 1, w, band_h))
    pygame.draw.line(surf, P["band_hi"],
                     (left_x + 1, hy - band_h - 1),
                     (left_x + w - 2, hy - band_h - 1), 1)


def _draw_fried_bumps(surf, hx, hy, crown_half, crown_h, P):
    """Two darker batter spots on the cylinder face — matches the KFC
    bird's spotty texture. Skipped when palette has spot=None."""
    if P.get("spot") is None:
        return
    # Bump 1 — top-left of the cylinder, clear of the `$` zone.
    b1_cx = hx - crown_half + 4
    b1_cy = hy - crown_h + 9
    pygame.draw.ellipse(surf, P["spot"], (b1_cx - 2, b1_cy - 2, 5, 4))
    pygame.draw.rect(surf, P["spot_hi"], (b1_cx - 1, b1_cy - 2, 2, 2))
    # Bump 2 — bottom-right, just above the band.
    b2_cx = hx + crown_half - 5
    b2_cy = hy - 8
    pygame.draw.ellipse(surf, P["spot"], (b2_cx - 2, b2_cy - 2, 5, 4))
    pygame.draw.rect(surf, P["spot_hi"], (b2_cx - 1, b2_cy - 2, 2, 2))


def _draw_stovepipe_themed(surf, hx, hy, P):
    """Themed stovepipe — same geometry as draw_stovepipe, palette swapped."""
    crown_half = 9
    crown_h = 28
    _draw_crown_cylinder_themed(surf, hx, hy, crown_half, crown_h, P)
    _draw_fried_bumps(surf, hx, hy, crown_half, crown_h, P)
    _draw_brim_themed(surf, hx, hy, P, half_w=17)

    # `$` glyph — outline 8-stamp, fill, then offset highlight stamp so
    # the glyph doesn't blend into a similar-tone hat body at native scale.
    f = _font(18)
    body = f.render("$", True, P["dollar"])
    edge = f.render("$", True, P["dollar_dk"])
    hi   = f.render("$", True, P["dollar_hi"])
    hi.set_alpha(160)
    cy = hy - crown_h // 2 - 1
    rect = body.get_rect(center=(hx, cy))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        surf.blit(edge, (rect.x + dx, rect.y + dy))
    surf.blit(body, rect.topleft)
    surf.blit(hi, (rect.x - 1, rect.y - 1))


def draw_stovepipe_kfc(surf, hx, hy):
    _draw_stovepipe_themed(surf, hx, hy, HAT_PALETTE_KFC)


def draw_stovepipe_ghost(surf, hx, hy):
    _draw_stovepipe_themed(surf, hx, hy, HAT_PALETTE_GHOST)


# ── Frame builder ────────────────────────────────────────────────────────────

def _build_hatted_frame(wing_angle_deg, hat_fn):
    """Compose normal parrot + hat onto the taller composite canvas."""
    composite = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Blit the unmodified parrot sprite (with original aviator sunglasses)
    parrot = _build_frame(wing_angle_deg)
    composite.blit(parrot, (0, PARROT_DY))
    # Draw the hat on top
    hat_fn(composite, HAT_HX, HAT_HY)
    return composite


def build_hat_frames(hat_fn) -> list:
    """Return 4 outlined hat-parrot surfaces (one per wing angle)."""
    return [_add_outline(_build_hatted_frame(a, hat_fn)) for a in _WING_ANGLES]


# ── Stacked-powerup combo frame builders ────────────────────────────────────
# When two or more bird-visual powerups are active simultaneously, the
# default Bird.draw cascade silently dropped all but the highest-priority
# mode. These builders compose the parrot bodies + themed hats so each
# reachable combo has a dedicated sprite.

def _build_combo_frame(parrot_sprite, hat_fn):
    """Generic version of _build_hatted_frame — accepts any pre-built
    parrot surface (fried, spectral, tinted) so we can plug it in instead
    of always calling _build_frame."""
    composite = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    composite.blit(parrot_sprite, (0, PARROT_DY))
    hat_fn(composite, HAT_HX, HAT_HY)
    return composite


def build_kfc_hat_frames() -> list:
    """KFC fried parrot + crispy KFC-themed stovepipe (warm hat with
    fried-batter bumps + dark fried-brown `$`)."""
    return [
        _add_outline(_build_combo_frame(
            _build_fried_frame(a), draw_stovepipe_kfc,
        ))
        for a in _WING_ANGLES
    ]


def build_ghost_hat_frames() -> list:
    """Spectral ghost parrot + ghost-themed stovepipe (cyan hat with
    sky-blue `$`)."""
    from game.dollar_parrot_ghost import build_spectral_frame
    return [
        _add_outline(_build_combo_frame(
            build_spectral_frame(a), draw_stovepipe_ghost,
        ))
        for a in _WING_ANGLES
    ]


def build_kfc_ghost_hat_frames() -> list:
    """Spectral-fried parrot + KFC hat, then cyan-tint the entire
    composite so bird + hat both read as a unified spectral-fried piece.
    Mirrors the cyan-tint-after-compose recipe from build_kfc_ghost in
    parrot.py."""
    frames = []
    for a in _WING_ANGLES:
        composite = _build_combo_frame(
            _build_fried_frame(a), draw_stovepipe_kfc,
        ).copy()
        _cyan_tint_in_place(composite)
        frames.append(_add_outline(composite))
    return frames


# ── Registry ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("TOP HAT",   draw_top_hat),
    ("WIZARD",    draw_wizard),
    ("TILT",      draw_tilt_top),
    ("STARS",     draw_stars),
    ("STOVEPIPE", draw_stovepipe),
]
