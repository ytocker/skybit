"""Five elegant Olympic-LAUREL concepts where the WREATH IS THE RING.

A real victor's head-wreath is nothing but a circlet of leaves — so here the
medallion's whole outer border IS the laurel: two thin leaf-sprigs on a slim
branch curving around the PERIMETER (rising from a base ribbon up both flanks to
nearly meet, open, at the top), forming the circle. There is NO separate metal
rim band — the leaves themselves are the visible ring, sitting AT the edge
(branch ~0.86*R, leaf tips out to ~0.97*R), encircling a calm navy face + a
prominent center emblem. Elegant + narrow (thin branch, small refined leaves),
never bulky, never gear-teeth.

Fame↔Shame trade-off lives in the leaf-ring: Fame = pristine GOLD laurel forming
the ring; Shame = the SAME leaf-ring gently wilted (browned/drooping leaves, a
shed-leaf gap, loosened ribbon), still readable at 44px. NO diagonal crack.

The five stay distinct WITHIN the laurel theme (per ``distinct-design-variants``)
— different leaf shape, density and circlet topology:

  1) CLASSIC  bay-laurel twin sprigs of small almond leaves + a base ribbon.
  2) OLIVE    kotinos: paired lanceolate leaves + small olive drupes.
  3) CIRCLET  a single continuous ring of leaves (open top, no ribbon).
  4) MINIMAL  sparse, well-spaced leaves, maximum breathing space (the calmest).
  5) LAYERED  fuller twin sprigs with a subtle double leaf row — lush yet thin.

Center emblem is never redesigned — every composer stamps the live engraved glyph
through ``ai._stamp_glyph`` (``pillar_100`` Fame, ``goose_egg`` Shame).

WRITE-ONLY scratch under ``tools/`` — never bundled; imports ``game`` read-only.
Composers render at the REAL badge geometry (``R = 0.46 * px``); the leaf-ring's
outermost tips stay within the badge square so nothing clips at 44px.
"""
from __future__ import annotations

import math
import pygame

import game.achievement_icons as ai
from game.draw import lerp_color

_LIGHT = ai._LIGHT  # share the family's one upper-left light source

# ── shared geometry ───────────────────────────────────────────────────────────
# The navy face is the calm inner disc; the LEAF-RING is the outer border at the
# perimeter. Leaf tips are held within ~0.97*R so nothing clips the badge square
# under the real ``R = 0.46*px`` geometry (badge edge ~1.09*R on the axes).
_FACE_F   = 0.80    # navy face radius / R (the emblem's calm field)
_BRANCH_R = 0.86    # the laurel branch's centre radius / R (AT the perimeter)
_GLYPH_F  = 0.52    # glyph radius / R (the prominent, calm focal point)

# The circlet is open at the TOP so it reads as a crown the way a victor wears it.
# Angles are screen space (y-down): 90deg bottom (base ribbon), -90deg top (gap).
_TOP_GAP  = math.radians(32)    # half-angle of the open top between the sprigs
_BASE_A   = math.radians(90)    # bottom of the ring (where the ribbon ties)


# ── shared palettes ──────────────────────────────────────────────────────────
# Fame gold — the family's warm struck gold; the only fully saturated accent.
_G_HI   = (255, 232, 160)
_G_MID  = (232, 186,  74)
_G_LO   = (150, 102,  22)
_FACE_TOP = (44, 32, 92)
_FACE_BOT = (16, 10, 44)
_FACE_REC = (10,  6, 28)
_GLY    = (255, 236, 184)
_GLY_SH = ( 32,  18,  44)

# Fame leaf gold — lit vs shadowed gold foliage, tinted per-leaf by the light.
_LEAF_HI = (250, 216, 112)
_LEAF_LO = (156, 108,  28)
_LEAF_MR = (120,  82,  18)      # engraved midrib
_OLIVE   = (214, 176,  70)      # a small gold olive drupe
_OLIVE_HI = (255, 240, 190)

# Shame — the SAME wreath gently wilted. The face cools to muted navy-grey; the
# leaves go autumn tan/brown (lifted so a thin browned leaf still reads at 44px),
# never a flat grey blob. Restrained warmth is the only "colour", mirroring gold.
_P_FACE_TOP = (52, 54, 74)
_P_FACE_BOT = (28, 30, 48)
_P_FACE_REC = (14, 14, 26)
_P_GLY  = (196, 200, 214)
_P_GLY_SH = (16, 16, 26)
_P_STEP_HI = (150, 156, 172)
_P_STEP_LO = ( 74,  78,  94)

_WILT_HI = (198, 158,  92)      # dry tan leaf, lit
_WILT_LO = (122,  86,  46)      # rotted brown leaf, shadow
_WILT_MR = ( 78,  54,  28)      # dry midrib
_WILT_DEAD = (156, 130,  86)    # grey-brown fully-dead shed leaf
_OLIVE_D = (120, 102,  66)      # shrivelled dull olive
_BRANCH_D = ( 96,  84,  62)     # dull tarnished branch hairline


# ── shared low-level helpers ─────────────────────────────────────────────────

def _center(surf, glyph_key, cx, cy, R, gly, gly_sh, sheen=None):
    ai._stamp_glyph(surf, glyph_key, cx, cy, int(R * _GLYPH_F), gly, gly_sh, sheen)


def _face(surf, cx, cy, R, step_hi, step_lo, ftop, fbot, frec, gk, gly, gly_sh,
          sheen=None):
    """The calm inner center: a thin minted step keyline around the navy face,
    the recessed enamel field, and the live engraved emblem. No metal rim band —
    the leaf-ring is drawn OUTSIDE this, forming the badge's perimeter."""
    fr = int(R * _FACE_F)
    ai._draw_step(surf, cx, cy, fr + max(1, R // 20), step_hi, step_lo)
    ai._draw_face(surf, cx, cy, fr, ftop, fbot, frec)
    _center(surf, gk, cx, cy, R, gly, gly_sh, sheen)


def _leaf(surf, bx, by, ang, ln, wd, fill, edge, R, mr=None):
    """One small almond laurel leaf: a pointed lens swept along ``ang`` from a
    base at (bx, by), with an engraved midrib so it reads as foliage, not a
    spike. Small + refined by design (short ``ln``)."""
    ca, sa = math.cos(ang), math.sin(ang)
    nx, ny = -sa, ca
    pts = []
    for f, w in ((0.0, 0.0), (0.34, wd), (0.66, wd * 0.78), (1.0, 0.0)):
        pts.append((bx + ca * ln * f + nx * w, by + sa * ln * f + ny * w))
    for f, w in ((1.0, 0.0), (0.66, wd * 0.78), (0.34, wd), (0.0, 0.0)):
        pts.append((bx + ca * ln * f - nx * w, by + sa * ln * f - ny * w))
    pygame.draw.polygon(surf, fill, [(int(x), int(y)) for x, y in pts])
    pygame.draw.line(surf, mr if mr is not None else edge, (int(bx), int(by)),
                     (int(bx + ca * ln), int(by + sa * ln)), max(1, R // 64))


def _leaf_col(a, hi, lo):
    """Tint a leaf by its angle to the one upper-left light, like a real rim."""
    d = (math.cos(a - _LIGHT) + 1) * 0.5
    return lerp_color(lo, hi, d ** 1.2)


def _branch_arc(surf, cx, cy, R, col, sgn):
    """The slim branch the leaves ride on — a fine hairline arc up one flank, so
    the perimeter reads as a real bent stem even between leaves. Thin by design;
    the LEAVES remain the visible ring."""
    rc = int(R * _BRANCH_R)
    rect = pygame.Rect(cx - rc, cy - rc, rc * 2, rc * 2)
    if sgn > 0:
        a0, a1 = -math.pi / 2 + _TOP_GAP, _BASE_A - math.radians(6)
    else:
        a0, a1 = _BASE_A + math.radians(6), 3 * math.pi / 2 - _TOP_GAP
    pygame.draw.arc(surf, col, rect, -a1, -a0, max(1, R // 42))


def _ribbon(surf, cx, cy, R, hi, lo, loosened=False):
    """The small ribbon tie where the two sprigs meet at the base of the crown —
    the wreath's classic finishing knot. ``loosened`` lets the tails sag apart so
    the Shame wreath reads as gently coming undone (never torn to shreds)."""
    rc = R * _BRANCH_R
    bx = cx + int(math.cos(_BASE_A) * rc)
    by = cy + int(math.sin(_BASE_A) * rc)
    knot = max(2, R // 22)
    pygame.draw.circle(surf, lerp_color(hi, lo, 0.25), (bx, by), knot)
    pygame.draw.circle(surf, lo, (bx, by), knot, max(1, R // 60))
    for sgn in (-1, 1):
        spread = 0.40 if loosened else 0.24
        drop = 0.15 if loosened else 0.11
        tip = (bx + int(sgn * R * spread), by + int(R * drop))
        mid = (bx + int(sgn * R * (spread * 0.5)),
               by + int(R * (drop * 0.55 + (0.05 if loosened else 0.0))))
        pygame.draw.lines(surf, lerp_color(hi, lo, 0.35), False,
                          [(bx, by), mid, tip], max(2, R // 40))


# ── per-sprig placement ──────────────────────────────────────────────────────

def i_even(f, span=6):
    """True on alternate nodes along a sprig (``f`` is the 0..1 node fraction)."""
    return int(round(f * span)) % 2 == 0


def _sprig_angles(n, sgn):
    """``n`` evenly spaced branch angles on one flank, from just off the base
    ribbon up to just short of the top gap. ``sgn`` +1 = RIGHT flank (sweeping up
    through 0deg), -1 = LEFT flank (up through 180deg) — so the two sprigs frame
    the emblem symmetrically and meet, open, at the top."""
    if sgn > 0:
        a_base = _BASE_A - math.radians(6)
        a_top = -math.pi / 2 + _TOP_GAP
    else:
        a_base = _BASE_A + math.radians(6)
        a_top = 3 * math.pi / 2 - _TOP_GAP
    for i in range(n):
        f = i / (n - 1)
        yield f, a_base + (a_top - a_base) * f


def _place_leaf(surf, cx, cy, rc, a, sgn, ln, wd, hi, lo, R, mr,
                out_k=0.4, droop=0.0):
    """Place one leaf on the branch at angle ``a`` on flank ``sgn``. Each leaf
    lies back along the branch (tangent swept toward the TOP) with a slight
    radial lift ``out_k`` — overlapping laurel leaves fanning up the perimeter.
    ``droop`` bends the tip limply groundward for the wilt."""
    bx = cx + math.cos(a) * rc
    by = cy + math.sin(a) * rc
    tx, ty = sgn * math.sin(a), sgn * (-math.cos(a))     # tangent toward the top
    ox, oy = math.cos(a), math.sin(a)                    # radial outward
    dx = tx + out_k * ox
    dy = ty + out_k * oy + droop * 0.9                   # droop pulls tip down
    dx -= sgn * droop * 0.25
    ang = math.atan2(dy, dx)
    _leaf(surf, bx, by, ang, ln, wd, _leaf_col(a, hi, lo), lo, R, mr)


def _fallen_leaf(surf, cx, cy, R, fx, fy, fl, fa, col, edge):
    """A single shed leaf resting inside the lower field — small enough to stay a
    clean silhouette at 44px, close enough not to clip the badge square."""
    _leaf(surf, cx + R * fx, cy + R * fy, fa, R * fl, R * fl * 0.30, col, edge,
          R, _WILT_MR)


# ═══════════════════════════════════════════════════════════════════════════
# 1) CLASSIC — bay-laurel twin sprigs of small almond leaves + a base ribbon.
# ═══════════════════════════════════════════════════════════════════════════

def _classic_ring(surf, cx, cy, R, hi, lo, mr, branch, wilt=False):
    rc = R * _BRANCH_R
    n = 11
    for sgn in (-1, 1):
        _branch_arc(surf, cx, cy, R, branch, sgn)
        for f, a in _sprig_angles(n, sgn):
            droop = 0.9 * f if wilt else 0.0
            if wilt and sgn > 0 and f < 0.24:          # right flank sheds low leaves
                continue
            ln = R * (0.26 - 0.05 * f)
            wd = R * (0.092 - 0.016 * f)
            _place_leaf(surf, cx, cy, rc, a, sgn, ln, wd, hi, lo, R, mr,
                        out_k=0.42, droop=droop)


def fame_classic(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
          glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _classic_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR, _G_MID)
    _ribbon(surf, cx, cy, R, _G_HI, _G_LO)


def shame_classic(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _P_STEP_HI, _P_STEP_LO, _P_FACE_TOP, _P_FACE_BOT,
          _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _classic_ring(surf, cx, cy, R, _WILT_HI, _WILT_LO, _WILT_MR, _BRANCH_D,
                  wilt=True)
    _fallen_leaf(surf, cx, cy, R, 0.34, 0.60, 0.16, 2.5, _WILT_DEAD, _WILT_LO)
    _ribbon(surf, cx, cy, R, _WILT_HI, _WILT_LO, loosened=True)


# ═══════════════════════════════════════════════════════════════════════════
# 2) OLIVE — kotinos: paired lanceolate leaves + small olive drupes.
# ═══════════════════════════════════════════════════════════════════════════

def _olive_ring(surf, cx, cy, R, hi, lo, mr, branch, olive_col, olive_hi,
                wilt=False):
    rc = R * _BRANCH_R
    n = 7
    for sgn in (-1, 1):
        _branch_arc(surf, cx, cy, R, branch, sgn)
        for f, a in _sprig_angles(n, sgn):
            droop = 0.9 * f if wilt else 0.0
            if wilt and sgn < 0 and f < 0.28:          # left flank sheds low leaves
                continue
            bx = cx + math.cos(a) * rc
            by = cy + math.sin(a) * rc
            ln = R * (0.235 - 0.04 * f)
            wd = R * (0.05 - 0.008 * f)                 # narrower than bay laurel
            for ok in (0.7, -0.28):                     # opposite paired leaves
                _place_leaf(surf, cx, cy, rc, a, sgn, ln, wd, hi, lo, R, mr,
                            out_k=ok, droop=droop)
            if 0.12 < f < 0.92 and i_even(f) and not (wilt and f > 0.4):
                orad = max(2, int(R * 0.052))
                ox = bx - math.cos(a) * R * 0.07
                oy = by - math.sin(a) * R * 0.07
                pygame.draw.circle(surf, lo, (int(ox), int(oy)), orad + 1)
                pygame.draw.circle(surf, olive_col, (int(ox), int(oy)), orad)
                pygame.draw.circle(surf, olive_hi,
                                   (int(ox - orad * 0.32), int(oy - orad * 0.32)),
                                   max(1, orad // 2))


def fame_olive(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
          glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _olive_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR, _G_MID,
                _OLIVE, _OLIVE_HI)
    _ribbon(surf, cx, cy, R, _G_HI, _G_LO)


def shame_olive(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _P_STEP_HI, _P_STEP_LO, _P_FACE_TOP, _P_FACE_BOT,
          _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _olive_ring(surf, cx, cy, R, _WILT_HI, _WILT_LO, _WILT_MR, _BRANCH_D,
                _OLIVE_D, _WILT_DEAD, wilt=True)
    _fallen_leaf(surf, cx, cy, R, -0.32, 0.62, 0.14, 0.7, _WILT_DEAD, _WILT_LO)
    pygame.draw.circle(surf, _OLIVE_D,
                       (cx + int(R * 0.12), cy + int(R * 0.66)), max(2, int(R * 0.032)))
    _ribbon(surf, cx, cy, R, _WILT_HI, _WILT_LO, loosened=True)


# ═══════════════════════════════════════════════════════════════════════════
# 3) CIRCLET — a single continuous ring of leaves (open top, no ribbon).
# ═══════════════════════════════════════════════════════════════════════════

def _circlet_ring(surf, cx, cy, R, hi, lo, mr, branch, wilt=False):
    rc = R * _BRANCH_R
    n = 20
    a0 = -math.pi / 2 + _TOP_GAP
    a1 = -math.pi / 2 + math.tau - _TOP_GAP
    # a full hairline branch (broken at the top gap) the leaves ride on
    rect = pygame.Rect(int(cx - rc), int(cy - rc), int(rc * 2), int(rc * 2))
    pygame.draw.arc(surf, branch, rect, -a1, -a0, max(1, R // 42))
    brown_lo, brown_hi = math.radians(18), math.radians(96)
    for i in range(n):
        f = i / (n - 1)
        a = a0 + (a1 - a0) * f
        an = a % math.tau
        in_brown = wilt and (brown_lo <= an <= brown_hi)
        if wilt and math.radians(46) <= an <= math.radians(70):
            continue                                   # two adjacent leaves shed
        bx = cx + math.cos(a) * rc
        by = cy + math.sin(a) * rc
        tx, ty = math.sin(a), -math.cos(a)             # CCW tangent
        ox, oy = math.cos(a), math.sin(a)
        droop = 0.8 if in_brown else 0.0
        ang = math.atan2(ty + 0.4 * oy + droop * 0.9, tx + 0.4 * ox)
        ln, wd = R * 0.185, R * 0.055
        lh, ll = (_WILT_HI, _WILT_LO) if in_brown else (hi, lo)
        _leaf(surf, bx, by, ang, ln, wd, _leaf_col(a, lh, ll), ll, R, mr)


def fame_circlet(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
          glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _circlet_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR, _G_MID)


def shame_circlet(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _P_STEP_HI, _P_STEP_LO, _P_FACE_TOP, _P_FACE_BOT,
          _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _circlet_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR, _BRANCH_D,
                  wilt=True)
    _fallen_leaf(surf, cx, cy, R, 0.38, 0.56, 0.13, 2.4, _WILT_DEAD, _WILT_LO)


# ═══════════════════════════════════════════════════════════════════════════
# 4) MINIMAL — sparse, well-spaced leaves, maximum breathing space (calmest).
# ═══════════════════════════════════════════════════════════════════════════

def _minimal_ring(surf, cx, cy, R, hi, lo, mr, branch, wilt=False):
    rc = R * _BRANCH_R
    n = 5
    for sgn in (-1, 1):
        _branch_arc(surf, cx, cy, R, branch, sgn)
        for f, a in _sprig_angles(n, sgn):
            droop = 0.9 * f if wilt else 0.0
            if wilt and sgn > 0 and f < 0.30:          # right flank drops low leaf
                continue
            ln = R * (0.27 - 0.045 * f)
            wd = R * (0.098 - 0.012 * f)
            _place_leaf(surf, cx, cy, rc, a, sgn, ln, wd, hi, lo, R, mr,
                        out_k=0.42, droop=droop)


def fame_minimal(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
          glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _minimal_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR, _G_MID)
    _ribbon(surf, cx, cy, R, _G_HI, _G_LO)


def shame_minimal(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _P_STEP_HI, _P_STEP_LO, _P_FACE_TOP, _P_FACE_BOT,
          _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _minimal_ring(surf, cx, cy, R, _WILT_HI, _WILT_LO, _WILT_MR, _BRANCH_D,
                  wilt=True)
    _fallen_leaf(surf, cx, cy, R, 0.36, 0.58, 0.17, 2.5, _WILT_DEAD, _WILT_LO)
    _ribbon(surf, cx, cy, R, _WILT_HI, _WILT_LO, loosened=True)


# ═══════════════════════════════════════════════════════════════════════════
# 5) LAYERED — fuller twin sprigs with a subtle double leaf row — lush yet thin.
# ═══════════════════════════════════════════════════════════════════════════

def _layered_ring(surf, cx, cy, R, hi, lo, mr, branch, wilt=False):
    rc = R * _BRANCH_R
    n = 11
    for sgn in (-1, 1):
        _branch_arc(surf, cx, cy, R, branch, sgn)
        for f, a in _sprig_angles(n, sgn):
            droop = 0.85 * f if wilt else 0.0
            shed = wilt and sgn > 0 and 0.30 < f < 0.66     # outer row comes apart
            if not shed:
                ln = R * (0.245 - 0.045 * f)
                wd = R * (0.08 - 0.013 * f)
                _place_leaf(surf, cx, cy, rc + R * 0.02, a, sgn, ln, wd, hi, lo,
                            R, mr, out_k=0.55, droop=droop)
            ln2 = R * (0.17 - 0.028 * f)
            wd2 = R * (0.058 - 0.009 * f)
            _place_leaf(surf, cx, cy, rc - R * 0.06, a, sgn, ln2, wd2, hi, lo,
                        R, mr, out_k=0.28, droop=droop * 0.6)


def fame_layered(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _G_HI, _G_LO, _FACE_TOP, _FACE_BOT, _FACE_REC,
          glyph_key, _GLY, _GLY_SH, ai._GLYPH_SHEEN)
    _layered_ring(surf, cx, cy, R, _LEAF_HI, _LEAF_LO, _LEAF_MR, _G_MID)
    _ribbon(surf, cx, cy, R, _G_HI, _G_LO)


def shame_layered(surf, cx, cy, R, glyph_key):
    _face(surf, cx, cy, R, _P_STEP_HI, _P_STEP_LO, _P_FACE_TOP, _P_FACE_BOT,
          _P_FACE_REC, glyph_key, _P_GLY, _P_GLY_SH)
    _layered_ring(surf, cx, cy, R, _WILT_HI, _WILT_LO, _WILT_MR, _BRANCH_D,
                  wilt=True)
    _fallen_leaf(surf, cx, cy, R, 0.34, 0.60, 0.14, 2.4, _WILT_DEAD, _WILT_LO)
    _ribbon(surf, cx, cy, R, _WILT_HI, _WILT_LO, loosened=True)


# Each concept pairs a Fame composer with its gently-wilted Shame twin.
CONCEPTS = [
    ("classic", fame_classic, shame_classic),
    ("olive", fame_olive, shame_olive),
    ("circlet", fame_circlet, shame_circlet),
    ("minimal", fame_minimal, shame_minimal),
    ("layered", fame_layered, shame_layered),
]
