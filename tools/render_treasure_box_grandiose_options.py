"""Treasure Box — grandiose + wooden, round 3 (per-cell distinctness polish).

Round 2's "festive" sheet (gift bow / confetti / party hat / rainbow /
carnival) read as party rather than treasure — the user asked for
"something really beautiful and grandiose" instead. This round explores
TWO families on one sheet so the choice is clear:

  Top row (5x)  GRANDIOSE — jewel-tone / precious-material directions,
                 "expensive heirloom" feel.  One crest jewel + lock plate
                 + corner trim is the refined-ornament budget; no party
                 trims, no confetti, no carnival colour.

  Bottom row (5x) WOODEN — iterations of B1 (the original pirate chest
                 from round_1). Same silhouette + 2 metal bands + central
                 lock; what changes is the wood species and the metallurgy
                 (iron / brass / copper / polished-gold).

Each cell keeps the round-1/-2 idioms: real pickup ~56x46 px on the LEFT,
3x zoom on the RIGHT, dawn sky + sparkle backdrop, thick ink outline,
baked idle bob, the unified 1-px warm-gold lid-rim light + 4 cream corner
sparkles (round-2 unifiers).

Round-3 polish keeps the 5+5 user-requested split intact; each cell now
carries a small per-cell visibility tweak (lid shadow, jewel swap, nail
heads, star crest, nameplate, etc.) so the 10 thumbnails no longer pair
up at pickup scale.

Chest geometry + palette neutrals + the dawn swatch all import from the
sibling round-2 tool so this sheet looks like it belongs to the same
exploration family.

Output: docs/treasure_box/grandiose_round_2.png   (doc-only; not shipped)
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))
sys.path.insert(0, THIS_DIR)

pygame.init()
pygame.display.set_mode((1, 1))

# Reuse every shared draw helper + palette constant from the round-2 tool
# so the new directions sit in the same chest family rather than diverging
# silhouettes mid-loop.
from render_treasure_box_options import (         # type: ignore
    PICKUP_W, PICKUP_H, SS, BOB_PULSE,
    INK, INK_SOFT, CREAM,
    GOLD_HI, GOLD_MID, GOLD_LO, GOLD_INK,
    WOOD_HI, WOOD_MID, WOOD_LO, WOOD_GRAIN,
    IRON_HI, IRON_MID, IRON_LO,
    _lerp, _vgrad_rect,
    _chest_body, _curved_lid, _iron_band, _gold_lock,
    _new_big, _finish, _common_layout,
    _dawn_sparkle_swatch,
)


# ---------------------------------------------------------------------------
# Round-3 palette additions — grandiose jewel tones + wood species.
# Each triplet is (HI, MID, LO) feeding _chest_body's vertical gradient.
# Ink stays the family default so the silhouette outline never shifts.
# ---------------------------------------------------------------------------
# G1 — Sapphire & gold (royal blue heirloom).
SAPPHIRE_HI  = ( 42,  82, 168)
SAPPHIRE_MID = ( 28,  58, 130)
SAPPHIRE_LO  = ( 14,  31,  74)
# 1-step-darker band tucked under G1's gold lid-rim light so the lid pops
# as a separate volume from the body at thumbnail scale.
SAPPHIRE_SHADOW = ( 18,  44, 100)
DIAMOND_HI   = (250, 252, 255)
DIAMOND_MID  = (210, 224, 244)
DIAMOND_BLU  = (138, 178, 232)
# Pale-blue sapphire cabochon — sits on G2's silver lock plate in place of
# the red ruby, so the chest never collides with the poison-vial pickup.
LIGHT_SAPPHIRE_HI  = (190, 220, 248)
LIGHT_SAPPHIRE_MID = (155, 196, 240)
LIGHT_SAPPHIRE_LO  = ( 90, 147, 204)

# G2 — Emerald & silver (forest-king treasury).
EMERALD_HI   = ( 40, 147,  76)
EMERALD_MID  = ( 26, 106,  58)
EMERALD_LO   = ( 12,  58,  31)
SILVER_HI    = (232, 236, 244)
SILVER_MID   = (178, 186, 200)
SILVER_LO    = (108, 116, 134)
SILVER_INK   = ( 50,  56,  70)
RUBY_HI      = (244, 120, 134)
RUBY_MID     = (200,  52,  72)
RUBY_LO      = (132,  22,  40)

# G3 — Obsidian & rose-gold (refined modern heirloom).
# Mid + HI lifted another ~10 R/G/B in round 3 (on top of the round-2
# lift) so the near-black body stops sinking into the dawn sky's lower
# band at thumbnail scale.
OBSIDIAN_HI  = ( 62,  62,  84)
OBSIDIAN_MID = ( 46,  46,  64)
OBSIDIAN_LO  = ( 14,  14,  22)
ROSEGOLD_HI  = (250, 196, 176)
ROSEGOLD_MID = (216, 138, 118)
ROSEGOLD_LO  = (148,  78,  60)
ROSEGOLD_INK = ( 96,  46,  34)
AMETHYST_HI  = (208, 158, 244)
AMETHYST_MID = (146,  86, 196)
AMETHYST_LO  = ( 78,  32, 124)

# G4 — White marble & gold (museum-piece).
MARBLE_HI    = (244, 236, 214)
MARBLE_MID   = (230, 218, 184)
MARBLE_LO    = (190, 169, 116)
MARBLE_VEIN  = (155, 142, 106)
TOPAZ_HI     = (255, 214, 134)
TOPAZ_MID    = (236, 166,  56)
TOPAZ_LO     = (164,  98,  16)

# G5 — Midnight starfield (astronomer's hoard).
# Pushed one step cooler / bluer than G1's sapphire so the two deep-blue
# chests don't share a silhouette at pickup scale — G5 is the saturated
# cyan-blue (low R, low G, strong B), G1 the warmer royal-blue.
# Hex target: #162852 / #0a1840 / #020618 (mapped HI / MID / LO).
MIDNIGHT_HI  = ( 22,  40,  82)
MIDNIGHT_MID = ( 10,  24,  64)
MIDNIGHT_LO  = (  2,   6,  24)
STAR_CREAM   = (244, 240, 218)
MOON_HI      = (250, 248, 224)
MOON_LO      = (188, 192, 210)

# Wooden row — fresh species + metallurgy variants of B1.
# W1 — Classic mahogany (B1 baseline, slightly polished).
MAHOG_HI     = (122,  58,  34)
MAHOG_MID    = ( 90,  41,  24)
MAHOG_LO     = ( 58,  22,  16)
MAHOG_GRAIN  = ( 38,  14,   8)
DARK_IRON_HI = ( 70,  72,  86)
DARK_IRON_MID = ( 42,  42,  48)
DARK_IRON_LO = ( 22,  22,  28)

# W2 — Ebony with gold bands (rich and dark).
EBONY_HI     = ( 42,  30,  22)
EBONY_MID    = ( 26,  18,  12)
EBONY_LO     = ( 10,   8,   5)
EBONY_GRAIN  = (  6,   4,   2)

# W3 — Weathered driftwood + brass + copper (sea-pirate salvage).
DRIFT_HI     = (138, 148, 158)
DRIFT_MID    = (106, 114, 128)
DRIFT_LO     = ( 62,  70,  78)
DRIFT_GRAIN  = ( 44,  50,  58)
# Warmer / more golden brass so W3 reads as patinated metal at pickup
# scale, not as cool steel-grey colliding with knight-armour palettes.
# Hex target: HI ~ honey highlight, MID #caa454, then a darker shadow —
# saturated honey-gold, not the cooler ochre we shipped in round 2.
BRASS_HI     = (236, 204, 132)
BRASS_MID    = (202, 164,  84)
BRASS_LO     = (140, 108,  44)
BRASS_INK    = ( 90,  62,  18)
PATINA       = (110, 158, 122)
COPPER_HI    = (232, 138,  92)
COPPER_MID   = (184,  90,  48)
COPPER_LO    = (118,  52,  24)
COPPER_INK   = ( 78,  30,  12)

# W4 — Polished walnut + brass (captain's quarters).
WALNUT_HI    = (154,  98,  56)
WALNUT_MID   = (124,  74,  40)
WALNUT_LO    = ( 78,  42,  20)
WALNUT_GRAIN = ( 52,  26,  10)

# W5 — Honey oak + iron (friendliest reading).
OAK_HI       = (216, 176, 106)
OAK_MID      = (200, 156,  90)
OAK_LO       = (138, 106,  58)
OAK_GRAIN    = ( 96,  68,  30)


# ---------------------------------------------------------------------------
# Local draw helpers — each one stays small and tactical so the chest body
# helper from the sibling tool still does the silhouette heavy-lifting.
# ---------------------------------------------------------------------------
def _l_bracket(big, corner, sx, sy, arm_len, thick,
               col_hi, col_lo, ink_col=None, ink_w=1):
    """Short gold/silver/brass L-bracket at a corner. (corner) is the chest
    corner pixel; sx/sy are signs picking the arm direction (+1/-1)."""
    cx, cy = corner
    # Horizontal arm
    arm_h = pygame.Rect(0, 0, arm_len, thick)
    arm_h.topleft = (cx if sx > 0 else cx - arm_len,
                     cy if sy > 0 else cy - thick)
    _vgrad_rect(big, arm_h, col_hi, col_lo,
                radius=max(1, thick // 2))
    if ink_col is not None:
        pygame.draw.rect(big, ink_col, arm_h,
                         max(1, ink_w // 2), border_radius=max(1, thick // 2))
    # Vertical arm
    arm_v = pygame.Rect(0, 0, thick, arm_len)
    arm_v.topleft = (cx if sx > 0 else cx - thick,
                     cy if sy > 0 else cy - arm_len)
    _vgrad_rect(big, arm_v, col_hi, col_lo,
                radius=max(1, thick // 2))
    if ink_col is not None:
        pygame.draw.rect(big, ink_col, arm_v,
                         max(1, ink_w // 2), border_radius=max(1, thick // 2))


def _facet_diamond(big, cx, cy, w, h, ink_w):
    """Faceted clear diamond — bright kite polygon + cool blue undershadow
    + crisp white top-glint. Used as the sapphire-chest crest jewel."""
    pts = [
        (cx,          cy - h // 2),
        (cx + w // 2, cy),
        (cx,          cy + h // 2),
        (cx - w // 2, cy),
    ]
    pygame.draw.polygon(big, DIAMOND_MID, pts)
    pygame.draw.polygon(big, DIAMOND_BLU,
                        [(cx - w // 2, cy),
                         (cx,          cy + h // 2),
                         (cx + w // 2, cy),
                         (cx,          cy + h // 6)])
    pygame.draw.polygon(big, DIAMOND_HI,
                        [(cx,          cy - h // 2),
                         (cx + w // 3, cy - h // 8),
                         (cx,          cy - h // 6),
                         (cx - w // 3, cy - h // 8)])
    pygame.draw.polygon(big, INK, pts, ink_w)
    # Top-edge specular spark.
    pygame.draw.line(big, (255, 255, 255),
                     (cx - w // 6, cy - h // 3),
                     (cx + w // 6, cy - h // 3),
                     max(1, ink_w // 2))


def _round_cabochon(big, cx, cy, r, col_hi, col_mid, col_lo, ink_w,
                    ink_col=INK):
    """Smooth round cabochon (ruby/topaz). Three concentric circles + glint."""
    pygame.draw.circle(big, col_lo, (cx, cy + max(1, r // 5)), r)
    pygame.draw.circle(big, col_mid, (cx, cy), r)
    pygame.draw.circle(big, col_hi, (cx - r // 4, cy - r // 4),
                       max(2, r * 2 // 3))
    pygame.draw.circle(big, ink_col, (cx, cy), r, max(1, ink_w // 2))
    pygame.draw.circle(big, (255, 255, 255),
                       (cx - r // 3, cy - r // 3),
                       max(1, ink_w // 2))


def _marble_veining(big, rect, vein_col, ink_w, seed=11):
    """A handful of thin diagonal veins inside a marble body. Drawn as
    short polylines so the marble doesn't feel uniform at zoom."""
    rng = (seed * 2654435761) & 0xFFFFFFFF
    def rnd():
        nonlocal rng
        rng = (1103515245 * rng + 12345) & 0x7FFFFFFF
        return rng / 0x7FFFFFFF
    # Build 5 short veins; each is a slightly noisy polyline.
    for _ in range(5):
        x0 = rect.left + int(rnd() * rect.width)
        y0 = rect.top + int(rnd() * rect.height)
        ang = (rnd() - 0.5) * math.pi          # roughly horizontal-ish
        length = int(rect.width * (0.30 + rnd() * 0.35))
        pts = [(x0, y0)]
        steps = 6
        for i in range(1, steps + 1):
            t = i / steps
            jitter = (rnd() - 0.5) * rect.height * 0.06
            x = x0 + math.cos(ang) * length * t
            y = y0 + math.sin(ang) * length * t + jitter
            pts.append((x, y))
        pygame.draw.lines(big, vein_col, False, pts, max(1, ink_w // 2))


def _silver_stud(big, cx, cy, r, ink_w):
    """A tiny silver rivet — used for G2's lid-seam studs."""
    pygame.draw.circle(big, SILVER_LO, (cx, cy + max(1, r // 4)), r)
    pygame.draw.circle(big, SILVER_HI, (cx, cy), r)
    pygame.draw.circle(big, SILVER_MID, (cx, cy),
                       max(1, int(r * 0.7)))
    pygame.draw.circle(big, SILVER_INK, (cx, cy), r, max(1, ink_w // 2))


def _gem_lock(big, cx, cy, w, h, ink_w, trim_hi, trim_lo, trim_ink,
              jewel_fn=None):
    """A coloured-metal lock plate. Same footprint as _gold_lock but the
    plate metal swaps with the chest's trim metal, and the centre carries
    a jewel (callable taking (big, cx, cy) — drawn after the plate)."""
    lock = pygame.Rect(0, 0, w, h)
    lock.center = (cx, cy)
    _vgrad_rect(big, lock, trim_hi, trim_lo, radius=max(2, w // 8))
    pygame.draw.rect(big, trim_ink, lock, ink_w,
                     border_radius=max(2, w // 8))
    if jewel_fn is not None:
        jewel_fn(big, cx, cy + h // 12)


def _crest_shield(big, cx, cy, w, h, ink_w, fill_hi, fill_lo, ink_col):
    """A tiny embossed shield silhouette on the lock plate. Used by W4."""
    pts = [
        (cx - w // 2, cy - h // 2),
        (cx + w // 2, cy - h // 2),
        (cx + w // 2, cy + h // 6),
        (cx,          cy + h // 2),
        (cx - w // 2, cy + h // 6),
    ]
    pygame.draw.polygon(big, fill_lo, pts)
    pygame.draw.polygon(big, fill_hi,
                        [(cx - w // 2, cy - h // 2),
                         (cx + w // 2, cy - h // 2),
                         (cx + w // 4, cy - h // 8),
                         (cx - w // 4, cy - h // 8)])
    pygame.draw.polygon(big, ink_col, pts, max(1, ink_w // 2))


def _crescent_moon(big, cx, cy, r, ink_w):
    """A small silver crescent — solid circle minus a clipped circle. Sits
    on the lock plate of G5 in place of a keyhole/jewel."""
    moon = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    mcx = moon.get_width() // 2
    mcy = moon.get_height() // 2
    pygame.draw.circle(moon, MOON_HI, (mcx, mcy), r)
    pygame.draw.circle(moon, MOON_LO, (mcx, mcy), r, max(1, ink_w // 2))
    # Clip out the inner circle to leave a crescent.
    pygame.draw.circle(moon, (0, 0, 0, 0),
                       (mcx + int(r * 0.55), mcy - int(r * 0.10)),
                       int(r * 0.92))
    big.blit(moon, moon.get_rect(center=(cx, cy)))


def _lid_rim_shadow(big, lid, shadow_col, ss):
    """A 1-px darker band riding the lid arc, drawn just before the
    unifier's warm-gold rim. The result reads as a thin "shadow line" right
    underneath the rim light, separating the lid as its own volume from
    the body — same arc as the unifier so the two stay parallel."""
    arc_h = int(lid.height * 0.65)
    cx = lid.centerx
    half_w = lid.width // 2
    pts = []
    n = 24
    # Inset a little further than the unifier so the shadow line sits
    # one pixel INSIDE the rim light, not on top of it.
    inset = max(2, ss // 3) + max(1, ss // 3)
    for i in range(n + 1):
        t = i / n
        ang = math.pi * (1 - t)
        ax = cx + math.cos(ang) * (half_w - inset)
        ay = lid.top - math.sin(ang) * (arc_h - inset)
        pts.append((ax, ay))
    if len(pts) >= 2:
        pygame.draw.lines(big, shadow_col, False, pts, max(1, ss // 3))


def _hairline_engraving(big, lid_pts, lid_top_y, lid_rect, col, ink_w):
    """A faint 1-px engraving line riding just inside the lid seam — adds
    "engraved" texture without breaking silhouette. Drawn as a polyline a
    couple SS-pixels above the lid bottom."""
    inset = max(2, ink_w)
    y = lid_rect.bottom - inset * 2
    pygame.draw.line(big, col,
                     (lid_rect.left + inset * 2, y),
                     (lid_rect.right - inset * 2, y),
                     max(1, ink_w // 3))


# ---------------------------------------------------------------------------
# Unified post-pass — every cell gets the round-2 unifiers: a 1-px warm
# gold lid-rim light and 4 cream corner sparkles. Applied AFTER the icon
# is drawn so it sits on top of any silhouette.
# ---------------------------------------------------------------------------
def _apply_unifiers(big, body, lid):
    """Warm-gold rim along the lid arc + 4 cream corner sparkles."""
    arc_h = int(lid.height * 0.65)
    cx = lid.centerx
    half_w = lid.width // 2
    pts = []
    n = 24
    for i in range(n + 1):
        t = i / n
        ang = math.pi * (1 - t)
        ax = cx + math.cos(ang) * (half_w - max(1, SS // 3))
        ay = lid.top - math.sin(ang) * (arc_h - max(1, SS // 3))
        pts.append((ax, ay))
    if len(pts) >= 2:
        pygame.draw.lines(big, (255, 226, 158), False, pts,
                          max(1, SS // 3))

    # Four cream corner sparkles around the chest silhouette.
    L = max(2, int(SS * 0.9))
    for (px, py) in (
        (body.left  + int(body.width * 0.10), body.top  + int(body.height * 0.10)),
        (body.right - int(body.width * 0.10), body.top  + int(body.height * 0.10)),
        (body.left  + int(body.width * 0.10), body.bottom - int(body.height * 0.18)),
        (body.right - int(body.width * 0.10), body.bottom - int(body.height * 0.18)),
    ):
        pygame.draw.circle(big, CREAM, (px, py), max(1, L // 2))
        pygame.draw.line(big, CREAM, (px - L, py), (px + L, py),
                         max(1, SS // 3))
        pygame.draw.line(big, CREAM, (px, py - L), (px, py + L),
                         max(1, SS // 3))


# ---------------------------------------------------------------------------
# Grandiose row — G1..G5.
# ---------------------------------------------------------------------------
def icon_g1():
    """G1 — Sapphire & gold. Deep royal sapphire body, brushed-gold L-
    bracket corner trims, gold lock plate carrying a faceted clear DIAMOND."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, SAPPHIRE_HI, SAPPHIRE_MID, SAPPHIRE_LO)
    pts, _ = _curved_lid(big, lid, ink,
                         SAPPHIRE_HI, SAPPHIRE_MID, SAPPHIRE_LO,
                         grain=False, sheen=True)
    # Hairline gold engraving along the lid bottom seam.
    _hairline_engraving(big, pts, lid.top, lid, GOLD_MID, ink)

    # Gold L-brackets at all four body corners (refined ornament budget).
    arm = int(body.width * 0.16)
    thick = max(2, SS)
    _l_bracket(big, (body.left,  body.top),    +1, +1, arm, thick,
               GOLD_HI, GOLD_LO, GOLD_INK, ink)
    _l_bracket(big, (body.right, body.top),    -1, +1, arm, thick,
               GOLD_HI, GOLD_LO, GOLD_INK, ink)
    _l_bracket(big, (body.left,  body.bottom), +1, -1, arm, thick,
               GOLD_HI, GOLD_LO, GOLD_INK, ink)
    _l_bracket(big, (body.right, body.bottom), -1, -1, arm, thick,
               GOLD_HI, GOLD_LO, GOLD_INK, ink)

    # Gold lock plate on the seam, diamond crest in the centre.
    lock_w = int(body.width * 0.32)
    lock_h = int(body.height * 0.52)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.06)

    def _diamond(b, jx, jy):
        _facet_diamond(b, jx, jy, int(lock_w * 0.50),
                       int(lock_h * 0.62), ink)

    _gem_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink,
              GOLD_HI, GOLD_LO, GOLD_INK, jewel_fn=_diamond)

    # Darker sapphire shadow band tucked under the lid-rim light — the lid
    # then reads as a separate volume sitting on top of the body.
    _lid_rim_shadow(big, lid, SAPPHIRE_SHADOW, SS)
    _apply_unifiers(big, body, lid)
    return _finish(big)


def icon_g2():
    """G2 — Emerald & silver. Deep emerald body, silver corner brackets +
    silver lock plate, ruby cabochon in the lock centre, 4 silver studs
    spaced evenly along the lid/body seam."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, EMERALD_HI, EMERALD_MID, EMERALD_LO)
    _curved_lid(big, lid, ink, EMERALD_HI, EMERALD_MID, EMERALD_LO,
                grain=False, sheen=True)

    arm = int(body.width * 0.16)
    thick = max(2, SS)
    _l_bracket(big, (body.left,  body.top),    +1, +1, arm, thick,
               SILVER_HI, SILVER_LO, SILVER_INK, ink)
    _l_bracket(big, (body.right, body.top),    -1, +1, arm, thick,
               SILVER_HI, SILVER_LO, SILVER_INK, ink)
    _l_bracket(big, (body.left,  body.bottom), +1, -1, arm, thick,
               SILVER_HI, SILVER_LO, SILVER_INK, ink)
    _l_bracket(big, (body.right, body.bottom), -1, -1, arm, thick,
               SILVER_HI, SILVER_LO, SILVER_INK, ink)

    # 4 silver studs running along the seam, just below the lid.
    stud_r = max(2, int(SS * 0.7))
    seam_y = body.top + int(body.height * 0.06)
    for k in range(4):
        sx = body.left + int(body.width * (0.18 + 0.21 * k))
        # Skip the centre where the lock plate sits.
        if abs(sx - body.centerx) < body.width * 0.16:
            continue
        _silver_stud(big, sx, seam_y, stud_r, ink)

    # Silver lock plate with a ruby cabochon centred.
    lock_w = int(body.width * 0.30)
    lock_h = int(body.height * 0.50)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.06)

    def _pale_sapphire(b, jx, jy):
        # Pale-blue sapphire cabochon — replaces the original ruby because
        # red-on-emerald collided with the poison-vial pickup silhouette.
        _round_cabochon(b, jx, jy, max(3, int(lock_h * 0.28)),
                        LIGHT_SAPPHIRE_HI, LIGHT_SAPPHIRE_MID,
                        LIGHT_SAPPHIRE_LO, ink)

    _gem_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink,
              SILVER_HI, SILVER_LO, SILVER_INK, jewel_fn=_pale_sapphire)

    _apply_unifiers(big, body, lid)
    return _finish(big)


def icon_g3():
    """G3 — Obsidian & rose-gold. Near-black body with cool blue undertone,
    rose-gold L-brackets + lock plate, a sliver of AMETHYST on the lock face."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, OBSIDIAN_HI, OBSIDIAN_MID, OBSIDIAN_LO)
    pts, _ = _curved_lid(big, lid, ink,
                         OBSIDIAN_HI, OBSIDIAN_MID, OBSIDIAN_LO,
                         grain=False, sheen=True)
    # Hairline rose-gold engraving along the lid bottom seam.
    _hairline_engraving(big, pts, lid.top, lid, ROSEGOLD_MID, ink)

    arm = int(body.width * 0.16)
    thick = max(2, SS)
    _l_bracket(big, (body.left,  body.top),    +1, +1, arm, thick,
               ROSEGOLD_HI, ROSEGOLD_LO, ROSEGOLD_INK, ink)
    _l_bracket(big, (body.right, body.top),    -1, +1, arm, thick,
               ROSEGOLD_HI, ROSEGOLD_LO, ROSEGOLD_INK, ink)
    _l_bracket(big, (body.left,  body.bottom), +1, -1, arm, thick,
               ROSEGOLD_HI, ROSEGOLD_LO, ROSEGOLD_INK, ink)
    _l_bracket(big, (body.right, body.bottom), -1, -1, arm, thick,
               ROSEGOLD_HI, ROSEGOLD_LO, ROSEGOLD_INK, ink)

    # Rose-gold lock plate; amethyst sliver (small faceted kite) on the face.
    lock_w = int(body.width * 0.30)
    lock_h = int(body.height * 0.50)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.06)

    def _rosegold_boss(b, jx, jy):
        # A small round rose-gold boss (no jewel) — the amethyst sliver it
        # replaced read as a colour speck that competed with the rim light.
        # SS=7 supersample, so a ~4 source-px disc maps to roughly 2.4*SS
        # in big-space; round 3 nudges the radius a hair so the boss is
        # clearly readable as a centred ornament at pickup scale.
        r = max(4, int(SS * 2.4))
        pygame.draw.circle(b, ROSEGOLD_LO, (jx, jy + max(1, r // 4)), r)
        pygame.draw.circle(b, ROSEGOLD_MID, (jx, jy), r)
        pygame.draw.circle(b, ROSEGOLD_HI,
                           (jx - r // 3, jy - r // 3),
                           max(2, r * 2 // 3))
        pygame.draw.circle(b, ROSEGOLD_INK, (jx, jy), r, max(1, ink // 2))

    _gem_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink,
              ROSEGOLD_HI, ROSEGOLD_LO, ROSEGOLD_INK,
              jewel_fn=_rosegold_boss)

    _apply_unifiers(big, body, lid)
    return _finish(big)


def icon_g4():
    """G4 — White marble & gold. Ivory marble body with thin grey veins,
    thick gold-leaf trim, gold lock plate with a TOPAZ (amber) crest jewel."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, MARBLE_HI, MARBLE_MID, MARBLE_LO)
    # Veining inside the body before the lid sits down — body veins only.
    _marble_veining(big, body, MARBLE_VEIN, ink, seed=4)

    pts, _ = _curved_lid(big, lid, ink, MARBLE_HI, MARBLE_MID, MARBLE_LO,
                         grain=False, sheen=True)
    # A second short vein sweep on the lid for continuity.
    _marble_veining(big, lid, MARBLE_VEIN, ink, seed=9)

    # An additional FAINTER, shorter vein on the lid only — slightly
    # different angle from the seed=9 pass so the marble stops reading
    # as a single decorative sticker glued to the body.
    faint_vein_col = (
        (MARBLE_VEIN[0] + MARBLE_HI[0]) // 2,
        (MARBLE_VEIN[1] + MARBLE_HI[1]) // 2,
        (MARBLE_VEIN[2] + MARBLE_HI[2]) // 2,
    )
    fv_len = int(lid.width * 0.28)
    fv_x0 = lid.left + int(lid.width * 0.18)
    fv_y0 = lid.top + int(lid.height * 0.55)
    fv_ang = -math.pi * 0.18                # a softer diagonal
    fv_pts = []
    for i in range(5):
        t = i / 4
        jx = fv_x0 + math.cos(fv_ang) * fv_len * t
        jy = fv_y0 + math.sin(fv_ang) * fv_len * t
        fv_pts.append((jx, jy))
    pygame.draw.lines(big, faint_vein_col, False, fv_pts,
                      max(1, ink // 3))

    # Gold-leaf trim — thicker L-brackets than the other grandiose entries
    # so it reads as "museum-piece" rather than "minimal modern".
    arm = int(body.width * 0.20)
    thick = max(3, int(SS * 1.3))
    _l_bracket(big, (body.left,  body.top),    +1, +1, arm, thick,
               GOLD_HI, GOLD_LO, GOLD_INK, ink)
    _l_bracket(big, (body.right, body.top),    -1, +1, arm, thick,
               GOLD_HI, GOLD_LO, GOLD_INK, ink)
    _l_bracket(big, (body.left,  body.bottom), +1, -1, arm, thick,
               GOLD_HI, GOLD_LO, GOLD_INK, ink)
    _l_bracket(big, (body.right, body.bottom), -1, -1, arm, thick,
               GOLD_HI, GOLD_LO, GOLD_INK, ink)

    # Gold lock plate; topaz cabochon in the centre.
    lock_w = int(body.width * 0.32)
    lock_h = int(body.height * 0.52)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.06)

    def _topaz(b, jx, jy):
        _round_cabochon(b, jx, jy, max(3, int(lock_h * 0.30)),
                        TOPAZ_HI, TOPAZ_MID, TOPAZ_LO, ink)

    _gem_lock(big, lock_cx, lock_cy, lock_w, lock_h, ink,
              GOLD_HI, GOLD_LO, GOLD_INK, jewel_fn=_topaz)

    _apply_unifiers(big, body, lid)
    return _finish(big)


def icon_g5():
    """G5 — Midnight starfield. Deep midnight body, a constellation of tiny
    silver stars baked into the body fill, silver L-brackets, silver lock
    plate with a CRESCENT MOON emblem (no keyhole, no jewel)."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))
    body, lid = _common_layout()

    _chest_body(big, body, ink, MIDNIGHT_HI, MIDNIGHT_MID, MIDNIGHT_LO)

    # A small constellation baked into the body — mix of tiny "+" stars and
    # single-pixel pips. Hand-placed (not random) so the pattern reads as a
    # composed constellation rather than noise.
    plus_specs = (
        (-0.30, -0.30, 1.0),
        ( 0.28, -0.20, 0.85),
        (-0.05,  0.22, 0.85),
        ( 0.32,  0.30, 0.75),
    )
    pip_specs = (
        (-0.40,  0.10),
        (-0.18, -0.06),
        ( 0.12, -0.32),
        ( 0.18,  0.05),
        ( 0.40, -0.04),
        (-0.32,  0.30),
    )
    for (ox, oy, sc) in plus_specs:
        sx = body.centerx + int(body.width * 0.5 * ox)
        sy = body.centery + int(body.height * 0.5 * oy)
        L = max(1, int(SS * 0.9 * sc))
        pygame.draw.circle(big, STAR_CREAM, (sx, sy), max(1, L // 2))
        pygame.draw.line(big, STAR_CREAM, (sx - L, sy), (sx + L, sy),
                         max(1, SS // 3))
        pygame.draw.line(big, STAR_CREAM, (sx, sy - L), (sx, sy + L),
                         max(1, SS // 3))
    for (ox, oy) in pip_specs:
        sx = body.centerx + int(body.width * 0.5 * ox)
        sy = body.centery + int(body.height * 0.5 * oy)
        pygame.draw.circle(big, STAR_CREAM, (sx, sy), max(1, SS // 3))

    _curved_lid(big, lid, ink, MIDNIGHT_HI, MIDNIGHT_MID, MIDNIGHT_LO,
                grain=False, sheen=True)

    arm = int(body.width * 0.16)
    thick = max(2, SS)
    _l_bracket(big, (body.left,  body.top),    +1, +1, arm, thick,
               SILVER_HI, SILVER_LO, SILVER_INK, ink)
    _l_bracket(big, (body.right, body.top),    -1, +1, arm, thick,
               SILVER_HI, SILVER_LO, SILVER_INK, ink)
    _l_bracket(big, (body.left,  body.bottom), +1, -1, arm, thick,
               SILVER_HI, SILVER_LO, SILVER_INK, ink)
    _l_bracket(big, (body.right, body.bottom), -1, -1, arm, thick,
               SILVER_HI, SILVER_LO, SILVER_INK, ink)

    # Silver lock plate with a crescent moon emblem in place of a keyhole.
    lock_w = int(body.width * 0.30)
    lock_h = int(body.height * 0.50)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.06)
    lock = pygame.Rect(0, 0, lock_w, lock_h)
    lock.center = (lock_cx, lock_cy)
    _vgrad_rect(big, lock, SILVER_HI, SILVER_LO,
                radius=max(2, lock_w // 8))
    pygame.draw.rect(big, SILVER_INK, lock, ink,
                     border_radius=max(2, lock_w // 8))
    _crescent_moon(big, lock_cx, lock_cy + lock_h // 12,
                   max(3, int(lock_h * 0.28)), ink)

    _apply_unifiers(big, body, lid)
    return _finish(big)


# ---------------------------------------------------------------------------
# Wooden row — W1..W5.  All five share the B1 silhouette: chest body with
# two iron-style bands + central gold-ish lock plate + curved lid + central
# lid strap.  What changes is wood species + band/lock metallurgy.
# ---------------------------------------------------------------------------
def _wooden_chest(big, ink,
                  wood_hi, wood_mid, wood_lo, wood_grain,
                  band_hi, band_mid, band_lo, band_ink,
                  lock_hi, lock_mid, lock_lo, lock_ink,
                  *,
                  lock_decoration=None,
                  body_decoration=None,
                  strap_col_mid=None,
                  strap_col_ink=None):
    """Shared wooden-chest draw routine — keeps the W1..W5 silhouettes
    identical so the round reads as a metallurgy ladder, not five different
    chests. lock_decoration is an optional callable taking (big, cx, cy,
    w, h, ink_w) drawn after the lock plate (e.g. crest shield, larger
    keyhole). body_decoration is an optional callable taking (big, body,
    lid, ink_w) drawn after the lock + clasp but BEFORE the unifiers — it
    is round 3's hook for the per-cell distinctness touches (W1 nails,
    W2 glint, W5 nameplate). strap_col_* default to the band colour so
    the lid strap matches the bands."""
    body, lid = _common_layout()

    _chest_body(big, body, ink, wood_hi, wood_mid, wood_lo)

    # Two metallurgical bands across the body (left + right).
    bw = int(body.width * 0.10)
    band_h = body.height - int(body.height * 0.20)
    left_band = pygame.Rect(body.left + int(body.width * 0.08),
                            body.top + int(body.height * 0.10),
                            bw, band_h)
    right_band = pygame.Rect(body.right - int(body.width * 0.08) - bw,
                             body.top + int(body.height * 0.10),
                             bw, band_h)
    for r in (left_band, right_band):
        _vgrad_rect(big, r, band_hi, band_lo, radius=max(1, ink))
        pygame.draw.rect(big, band_ink, r, ink, border_radius=max(1, ink))
        # Rivets at the band ends.
        rivet_r = max(2, int(r.height * 0.06))
        for ry in (r.top + r.height // 12, r.bottom - r.height // 12):
            cx = r.centerx
            pygame.draw.circle(big, band_hi, (cx, ry), rivet_r)
            pygame.draw.circle(big, band_ink, (cx, ry), rivet_r,
                               max(1, ink // 2))

    # Faint wood grain ticks across the body (uses the species' grain hue).
    n = 3
    for i in range(1, n + 1):
        gy = body.top + int(body.height * (i / (n + 1)))
        x0 = body.left + int(body.width * 0.10)
        x1 = body.right - int(body.width * 0.10)
        pygame.draw.line(big, wood_grain, (x0, gy), (x1, gy),
                         max(1, ink // 2))

    # Curved lid in the same wood species.
    _curved_lid(big, lid, ink, wood_hi, wood_mid, wood_lo,
                grain=True, sheen=True)

    # Lid central strap matching the band metal.
    strap_y = lid.top + int(lid.height * 0.10)
    smid = strap_col_mid if strap_col_mid is not None else band_mid
    sink = strap_col_ink if strap_col_ink is not None else band_ink
    pygame.draw.line(big, smid,
                     (lid.left + int(lid.width * 0.04), strap_y),
                     (lid.right - int(lid.width * 0.04), strap_y),
                     max(3, ink))
    pygame.draw.line(big, sink,
                     (lid.left + int(lid.width * 0.04), strap_y),
                     (lid.right - int(lid.width * 0.04), strap_y),
                     max(1, ink // 2))

    # Central lock plate.
    lock_w = int(body.width * 0.30)
    lock_h = int(body.height * 0.55)
    lock_cx = body.centerx
    lock_cy = body.top + lock_h // 2 - int(body.height * 0.08)
    lock = pygame.Rect(0, 0, lock_w, lock_h)
    lock.center = (lock_cx, lock_cy)
    _vgrad_rect(big, lock, lock_hi, lock_lo,
                radius=max(2, lock_w // 8))
    pygame.draw.rect(big, lock_ink, lock, ink,
                     border_radius=max(2, lock_w // 8))

    if lock_decoration is not None:
        lock_decoration(big, lock_cx, lock_cy, lock_w, lock_h, ink)
    else:
        # Default round keyhole + tail slot (same shape as _gold_lock).
        khr = max(2, int(lock_h * 0.18))
        pygame.draw.circle(big, INK, (lock_cx, lock_cy - lock_h // 8), khr)
        pygame.draw.polygon(big, INK,
                            [(lock_cx - khr // 2, lock_cy - lock_h // 8),
                             (lock_cx + khr // 2, lock_cy - lock_h // 8),
                             (lock_cx + khr // 3, lock_cy + lock_h // 4),
                             (lock_cx - khr // 3, lock_cy + lock_h // 4)])

    # Small lid clasp tab descending into the lock — same hardware as B1.
    clasp = pygame.Rect(0, 0, int(lock_w * 0.35), int(lock_h * 0.45))
    clasp.midbottom = (lock_cx, body.top + int(lock_h * 0.18))
    _vgrad_rect(big, clasp, lock_hi, lock_lo,
                radius=max(2, clasp.width // 6))
    pygame.draw.rect(big, lock_ink, clasp, max(1, ink // 2),
                     border_radius=max(2, clasp.width // 6))

    # Per-cell distinctness hook — drawn AFTER hardware so nails / nameplates
    # sit on top of bands, BEFORE the unifier rim so they don't overdraw it.
    if body_decoration is not None:
        body_decoration(big, body, lid, ink)

    _apply_unifiers(big, body, lid)


def icon_w1():
    """W1 — Classic mahogany. Warm mahogany body, dark iron bands,
    traditional gold lock + standard keyhole. Round 3 adds four dark-iron
    nail heads at the body corners — historical hardware that gives W1 its
    own silhouette texture so it no longer pairs with W5 at thumbnail."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))

    def _corner_nails(b, body, lid, ink_w):
        # Four small dark-iron nails — ~2 source-px discs (SS supersample),
        # inset from each body corner so they read as hammered hardware.
        nail_r = max(2, int(SS * 0.9))
        inset_x = int(body.width * 0.04)
        inset_y = int(body.height * 0.06)
        for (nx, ny) in (
            (body.left  + inset_x, body.top    + inset_y),
            (body.right - inset_x, body.top    + inset_y),
            (body.left  + inset_x, body.bottom - inset_y),
            (body.right - inset_x, body.bottom - inset_y),
        ):
            pygame.draw.circle(b, DARK_IRON_LO,
                               (nx, ny + max(1, nail_r // 3)), nail_r)
            pygame.draw.circle(b, DARK_IRON_MID, (nx, ny), nail_r)
            pygame.draw.circle(b, DARK_IRON_HI,
                               (nx - nail_r // 3, ny - nail_r // 3),
                               max(1, nail_r // 2))
            pygame.draw.circle(b, INK, (nx, ny), nail_r,
                               max(1, ink_w // 2))

    _wooden_chest(big, ink,
                  MAHOG_HI, MAHOG_MID, MAHOG_LO, MAHOG_GRAIN,
                  DARK_IRON_HI, DARK_IRON_MID, DARK_IRON_LO, INK,
                  GOLD_HI, GOLD_MID, GOLD_LO, GOLD_INK,
                  body_decoration=_corner_nails)
    return _finish(big)


def icon_w2():
    """W2 — Ebony with gold bands. Very dark wood + polished-gold bands
    (matches the lock); grain reads as near-black ticks. Round 3 adds a
    1-px cream glint on the gold lock plate's top-left corner, mirroring
    G1's diamond glint discipline so W2 stops feeling like an unornamented
    sister of W4."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))

    def _gold_glint(b, body, lid, ink_w):
        # Recompute the lock rect to land the glint exactly on its top-left.
        lock_w = int(body.width * 0.30)
        lock_h = int(body.height * 0.55)
        lock_cx = body.centerx
        lock_cy = body.top + lock_h // 2 - int(body.height * 0.08)
        gx = lock_cx - lock_w // 2 + max(2, ink_w)
        gy = lock_cy - lock_h // 2 + max(2, ink_w)
        L = max(1, int(SS * 0.7))
        pygame.draw.line(b, CREAM, (gx, gy), (gx + L, gy + L),
                         max(1, ink_w // 2))
        pygame.draw.circle(b, (255, 255, 255), (gx, gy),
                           max(1, ink_w // 3))

    _wooden_chest(big, ink,
                  EBONY_HI, EBONY_MID, EBONY_LO, EBONY_GRAIN,
                  GOLD_HI, GOLD_MID, GOLD_LO, GOLD_INK,
                  GOLD_HI, GOLD_MID, GOLD_LO, GOLD_INK,
                  body_decoration=_gold_glint)
    return _finish(big)


def icon_w3():
    """W3 — Weathered driftwood + brass + copper. Cool grey-blue wood with
    brass bands (faint patina hint) + a copper lock + copper keyhole."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))

    def _copper_keyhole(b, cx, cy, w, h, ink_w):
        # Slightly chunkier keyhole + a patina sheen tick on the lock face.
        khr = max(2, int(h * 0.22))
        pygame.draw.circle(b, COPPER_INK, (cx, cy - h // 8), khr)
        pygame.draw.polygon(b, COPPER_INK,
                            [(cx - khr // 2, cy - h // 8),
                             (cx + khr // 2, cy - h // 8),
                             (cx + khr // 3, cy + h // 4),
                             (cx - khr // 3, cy + h // 4)])
        # Faint patina-green tick top-left.
        pygame.draw.line(b, PATINA,
                         (cx - w // 3, cy - h // 3),
                         (cx - w // 6, cy - h // 3),
                         max(1, ink_w // 2))

    _wooden_chest(big, ink,
                  DRIFT_HI, DRIFT_MID, DRIFT_LO, DRIFT_GRAIN,
                  BRASS_HI, BRASS_MID, BRASS_LO, BRASS_INK,
                  COPPER_HI, COPPER_MID, COPPER_LO, COPPER_INK,
                  lock_decoration=_copper_keyhole)
    return _finish(big)


def icon_w4():
    """W4 — Polished walnut + brass + ornate brass lock carrying a 5-pointed
    brass star (no keyhole). Round 3 swaps the shield-crest (which vanished
    at 1x) for a star ornament that survives the supersample down to pickup
    scale and clearly separates W4 from W2's plain plate."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))

    def _brass_star(b, cx, cy, w, h, ink_w):
        # 5-pointed star centred on the lock plate. Outer radius targets a
        # ~4 source-px star (~2*SS in big-space) so the silhouette reads at
        # 1x; stroke uses the warm brass HI so it pops against the plate's
        # mid-tone fill.
        r_out = max(4, int(SS * 2.6))
        r_in  = max(2, int(r_out * 0.42))
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * (math.pi / 5)
            rr = r_out if k % 2 == 0 else r_in
            pts.append((cx + math.cos(ang) * rr,
                        cy + math.sin(ang) * rr))
        pygame.draw.polygon(b, BRASS_HI, pts)
        pygame.draw.polygon(b, BRASS_INK, pts, max(1, ink_w // 2))

    _wooden_chest(big, ink,
                  WALNUT_HI, WALNUT_MID, WALNUT_LO, WALNUT_GRAIN,
                  BRASS_HI, BRASS_MID, BRASS_LO, BRASS_INK,
                  BRASS_HI, BRASS_MID, BRASS_LO, BRASS_INK,
                  lock_decoration=_brass_star)
    return _finish(big)


def icon_w5():
    """W5 — Honey oak + iron + copper lock with a normal-sized keyhole and a
    horizontal brass nameplate across the lower body. Round 3 shrinks the
    oversized round-2 keyhole back to W1's size (the chunky version made W5
    feel cartoonish) and bolts a captain's nameplate above the bottom iron
    band so the silhouette carries a clear detail W1 doesn't."""
    big = _new_big()
    ink = max(3, int(SS * 1.05))

    def _nameplate(b, body, lid, ink_w):
        # Brass strip ~10 source-px wide, ~2 source-px tall, centred on the
        # body, sitting just above the lower band. Two-tone fill + INK
        # outline keeps it readable against honey oak at thumbnail scale.
        plate_w = int(body.width * 0.42)
        plate_h = max(3, int(SS * 1.6))
        plate = pygame.Rect(0, 0, plate_w, plate_h)
        plate.center = (body.centerx,
                        body.bottom - int(body.height * 0.18))
        _vgrad_rect(b, plate, BRASS_HI, BRASS_LO,
                    radius=max(1, plate_h // 3))
        pygame.draw.rect(b, BRASS_INK, plate, max(1, ink_w // 2),
                         border_radius=max(1, plate_h // 3))
        # Tiny engraved-line tick for the "captain's-name" affordance.
        pygame.draw.line(b, BRASS_INK,
                         (plate.left + plate_w // 6, plate.centery),
                         (plate.right - plate_w // 6, plate.centery),
                         max(1, ink_w // 3))

    def _std_keyhole(b, cx, cy, w, h, ink_w):
        # Matches W1's keyhole footprint exactly (h * 0.18 radius + tail).
        khr = max(2, int(h * 0.18))
        pygame.draw.circle(b, INK, (cx, cy - h // 8), khr)
        pygame.draw.polygon(b, INK,
                            [(cx - khr // 2, cy - h // 8),
                             (cx + khr // 2, cy - h // 8),
                             (cx + khr // 3, cy + h // 4),
                             (cx - khr // 3, cy + h // 4)])

    _wooden_chest(big, ink,
                  OAK_HI, OAK_MID, OAK_LO, OAK_GRAIN,
                  DARK_IRON_HI, DARK_IRON_MID, DARK_IRON_LO, INK,
                  COPPER_HI, COPPER_MID, COPPER_LO, COPPER_INK,
                  lock_decoration=_std_keyhole,
                  body_decoration=_nameplate)
    return _finish(big)


# ---------------------------------------------------------------------------
# Sheet assembly — 5 cols x 2 rows; grandiose on top, wooden on bottom.
# ---------------------------------------------------------------------------
GRANDIOSE = [
    ("G1", "Sapphire & gold (lead)",   icon_g1),
    ("G2", "Emerald & sapphire",       icon_g2),
    ("G3", "Obsidian & rose-gold",     icon_g3),
    ("G4", "Marble & gold + topaz",    icon_g4),
    ("G5", "Midnight starfield",       icon_g5),
]

WOODEN = [
    ("W1", "Mahogany + iron nails",      icon_w1),
    ("W2", "Ebony + polished gold",      icon_w2),
    ("W3", "Driftwood + brass + copper", icon_w3),
    ("W4", "Walnut + brass star",        icon_w4),
    ("W5", "Honey oak + nameplate",      icon_w5),
]


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "treasure_box")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "grandiose_round_2.png")

    # Baked float-bob shift, same convention as the round-2 sheet.
    bob = int(round(math.sin(BOB_PULSE * 0.8) * 2))

    cell_w, cell_h = 320, 340
    cols = 5
    rows = 2
    pad = 16
    header_h = 90
    cap_h = 34

    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * pad
    sheet_h = header_h + rows * (cell_h + cap_h) + (rows - 1) * pad + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 30))

    def font(sz, bold=False):
        return pygame.font.SysFont("Arial", sz, bold=bold)

    title = font(26, bold=True).render(
        "TREASURE BOX  grandiose + wooden  -  round 2 (10 directions)",
        True, (240, 240, 246))
    sheet.blit(title, (pad, pad))
    sub = font(14).render(
        "round 2 — per-cell visibility + distinctness polish",
        True, (170, 178, 192))
    sheet.blit(sub, (pad, pad + 32))
    sub2 = font(13).render(
        "Left = real pickup (~56x46 px, float-bobbed);  right = 3x zoom.  "
        "Dawn sky + sparkle backdrop per cell.",
        True, (200, 180, 150))
    sheet.blit(sub2, (pad, pad + 54))

    rows_data = [GRANDIOSE, WOODEN]
    for row_idx, row in enumerate(rows_data):
        row_y = header_h + pad + row_idx * (cell_h + cap_h + pad)
        for col, (tag, name, fn) in enumerate(row):
            x = pad + col * (cell_w + pad)
            # Distinct sparkle seed per cell so the backdrop varies subtly.
            swatch = _dawn_sparkle_swatch(cell_w, cell_h,
                                          seed=col + 7 * (row_idx + 1))
            sheet.blit(swatch, (x, row_y))
            pygame.draw.rect(sheet, (60, 66, 84),
                             (x, row_y, cell_w, cell_h), 1)

            icon = fn()

            # Real pickup, left half of the cell.
            true_cx = x + cell_w // 4 - PICKUP_W // 2
            true_cy = row_y + cell_h // 2 - PICKUP_H // 2 + bob
            sheet.blit(icon, (true_cx, true_cy))
            pygame.draw.rect(sheet, (255, 255, 255),
                             (true_cx - 3, true_cy - bob - 3,
                              PICKUP_W + 6, PICKUP_H + 6), 1)
            lbl = font(12).render(f"real pickup ~{PICKUP_W}x{PICKUP_H} px",
                                  True, (210, 220, 235))
            sheet.blit(lbl, (x + 10, row_y + cell_h - 24))

            # 3x zoom on the right.
            zoom = pygame.transform.smoothscale(
                icon, (PICKUP_W * 3, PICKUP_H * 3))
            zx = x + cell_w - PICKUP_W * 3 - 18
            zy = row_y + cell_h // 2 - (PICKUP_H * 3) // 2
            sheet.blit(zoom, (zx, zy))
            zl = font(12).render("3x zoom", True, (210, 220, 235))
            sheet.blit(zl, (zx + PICKUP_W * 3 - 56, zy - 18))

            # Caption strip below the cell.
            cap = font(16, bold=True).render(f"{tag}  {name}", True,
                                             (245, 240, 230))
            sheet.blit(cap, (x + 8, row_y + cell_h + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
