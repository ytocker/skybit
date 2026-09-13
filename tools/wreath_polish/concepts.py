"""
Scratch composer for the achievement-badge WREATH polish round (5 laurel/leaf
variations, each a Fame/Shame pair). NOT shipped — lives under tools/ only.

Every wreath here is composed onto a real medallion built from
``game.achievement_icons`` internals (rim/step/face/glyph), so explorations look
exactly like the live badge. The HARD constraint that governs this whole round:
the badge square has only ~0.04*size of margin past the R=0.46*size medallion,
so EVERY leaf — pristine or fallen — must stay within ~0.49*size of center
(R*~1.065). The Shame degradation changes the SILHOUETTE (gaps/droops/shed
leaves scattered INSIDE the lower disc, never trailing off the bottom edge),
not just the colour.

Each variation owns its construction (its own leaf primitive + layout) per the
distinct-design-variants doctrine; only low-level helpers are shared.
"""
from __future__ import annotations

import math
import random
import pygame

import game.achievement_icons as ai
from game.draw import lerp_color, blit_glow

# Gold (Fame) and tarnished-bronze (Shame) leaf palettes, pulled from the live
# medallion so the wreaths read as the same struck metal as the rim.
_GOLD_HI, _GOLD_MID, _GOLD_LO = ai._RING_HI, ai._RING_MID, ai._RING_LO
_GOLD_SPEC = ai._SPEC_HOT
# Shame leaves: oxidised/wilted bronze — browned AND lifted in value so the
# wreath still reads against the cool pewter rim (a dark wilt vanished entirely
# against the medallion in round 1). Warm enough to read "dying", not "shadow".
_WILT_HI = (196, 158, 84)     # last warm catch-light on a dying leaf
_WILT_MID = (158, 116, 58)    # browning body
_WILT_LO = (104, 76, 40)      # rotted shadow side
_WILT_DEAD = (132, 98, 52)    # fully-curled fallen leaf

_LIGHT = ai._LIGHT


# ── shared low-level leaf primitives (geometry only; palette passed in) ───────

def _leaf_blade(surf, bx, by, ang, length, width, col, edge, vein=True):
    """A single laurel blade: a rounded 6-point lens (narrow stalk → full belly
    → point) along ``ang`` so it reads as a LEAF, not a thorn. ``width`` is the
    half-thickness at the belly. An optional centre vein adds an engraved seam."""
    ux, uy = math.cos(ang), math.sin(ang)        # along the leaf
    nx, ny = -uy, ux                             # across the leaf
    def P(t, w):
        return (bx + ux * length * t + nx * width * w,
                by + uy * length * t + ny * width * w)
    # base stalk thin, belly at ~0.42, taper to a soft point
    pts = [P(0.0, 0.18), P(0.30, 0.85), P(0.55, 1.0), P(0.82, 0.7),
           P(1.0, 0.0),
           P(0.82, -0.7), P(0.55, -1.0), P(0.30, -0.85)]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
    pygame.draw.polygon(surf, edge, [(int(x), int(y)) for x, y in pts], 1)
    if vein:
        tx = bx + ux * length
        ty = by + uy * length
        pygame.draw.line(surf, edge, (int(bx), int(by)), (int(tx), int(ty)), 1)


def _lit(d_col, l_col, ang):
    """Tone a leaf by its facing to the one upper-left light, like the rim."""
    d = (math.cos(ang - _LIGHT) + 1) * 0.5
    return lerp_color(d_col, l_col, d ** 1.2)


def _max_r(size):
    return size * 0.49


def _clamp_len(bx, by, ang, length, cx, cy, R, lim=1.05):
    """Shorten a blade so its tip stays within ``lim*R`` of centre — the hard
    badge-square constraint. Returns the safe length."""
    tx = bx + math.cos(ang) * length
    ty = by + math.sin(ang) * length
    tip_r = math.hypot(tx - cx, ty - cy)
    if tip_r > R * lim:
        return length * (R * lim) / tip_r
    return length


# ── the shared medallion body (rim + step + face + real glyph) ────────────────

def _medallion(surf, cx, cy, R, shame, icon_key):
    """Draw the struck medallion body the wreath wraps — identical palette path
    to the live ``_build`` so wreath explorations sit on the real badge."""
    if shame:
        rim_hi, rim_mid, rim_lo, spec = (ai._TARN_RIM_HI, ai._TARN_RIM_MID,
                                         ai._TARN_RIM_LO, ai._TARN_SPEC)
        face_top, face_bot, recess = ai._TARN_FACE_TOP, ai._TARN_FACE_BOT, ai._TARN_RECESS
        step_hi, step_lo = ai._TARN_STEP_HI, ai._TARN_STEP_LO
        gly, gly_sh = ai._TARN_GLY, ai._TARN_GLY_SH
        sheen = None
    else:
        rim_hi, rim_mid, rim_lo, spec = ai._RING_HI, ai._RING_MID, ai._RING_LO, ai._SPEC_HOT
        face_top, face_bot, recess = ai._FACE_TOP, ai._FACE_BOT, ai._RECESS
        step_hi, step_lo = ai._STEP_HI, ai._STEP_LO
        gly, gly_sh, sheen = ai._GLYPH, ai._GLYPH_SH, ai._GLYPH_SHEEN

    ai._draw_rim(surf, cx, cy, R, rim_hi, rim_mid, rim_lo, spec)


def _medallion_face(surf, cx, cy, R, shame, icon_key):
    """The step + recessed enamel + engraved glyph, drawn AFTER the wreath so the
    leaves sit on the rim band (their bellies read against the gold) while the
    centre emblem stays clean and unobscured."""
    if shame:
        face_top, face_bot, recess = ai._TARN_FACE_TOP, ai._TARN_FACE_BOT, ai._TARN_RECESS
        step_hi, step_lo = ai._TARN_STEP_HI, ai._TARN_STEP_LO
        gly, gly_sh, sheen = ai._TARN_GLY, ai._TARN_GLY_SH, None
    else:
        face_top, face_bot, recess = ai._FACE_TOP, ai._FACE_BOT, ai._RECESS
        step_hi, step_lo = ai._STEP_HI, ai._STEP_LO
        gly, gly_sh, sheen = ai._GLYPH, ai._GLYPH_SH, ai._GLYPH_SHEEN
    fr = int(R * 0.70)
    ai._draw_step(surf, cx, cy, fr + max(2, R // 16), step_hi, step_lo)
    ai._draw_face(surf, cx, cy, fr, face_top, face_bot, recess)
    gr = int(R * 0.56)
    ai._stamp_glyph(surf, icon_key, cx, cy, gr, gly, gly_sh, sheen)


def _leaf_cluster(surf, cx, cy, anchor_a, R, shame, n, spread, leaf_len,
                  width_f=0.075, base_rf=0.9, berry=False, shed_outer=0):
    """A DISCRETE tuft of ``n`` leaves fanning out from one anchor on the rim —
    the building block that keeps every wreath reading as LEAVES (not a gear)
    when shrunk: clusters are placed with clear bare-gold gaps between them, and
    a fan of a few leaves survives the shrink as a recognisable leaf clump where
    a continuous serrated band collapses to teeth. ``shed_outer`` drops that many
    outer leaves (Shame) so a gap opens in the silhouette."""
    ax = cx + math.cos(anchor_a) * R * base_rf
    ay = cy + math.sin(anchor_a) * R * base_rf
    droop = math.radians(20) if shame else 0
    drawn = n - (shed_outer if shame else 0)
    for i in range(n):
        if shame and i >= drawn:
            continue
        f = (i / max(1, n - 1)) - 0.5      # -0.5..0.5 across the fan
        la = anchor_a + f * spread + droop
        length = leaf_len * (1.0 - 0.10 * abs(f))
        width = R * width_f
        col = _lit(_WILT_LO, _WILT_HI, la) if shame else _lit(_GOLD_LO, _GOLD_HI, la)
        edge = _WILT_LO if shame else _GOLD_LO
        length = _clamp_len(ax, ay, la, length, cx, cy, R)
        _leaf_blade(surf, ax, ay, la, length, width, col, edge, vein=False)
    if berry:
        # a round gold berry nested at the cluster base — survives the shrink as
        # a bright dot where slim leaves would vanish
        br = max(2, int(R * (0.06 if not shame else 0.04)))
        if not (shame and shed_outer >= n):
            bcol = _WILT_LO if shame else _GOLD_MID
            bhi = _WILT_MID if shame else _GOLD_HI
            bxx = cx + math.cos(anchor_a) * R * 1.0
            byy = cy + math.sin(anchor_a) * R * 1.0
            pygame.draw.circle(surf, bcol, (int(bxx), int(byy)), br)
            pygame.draw.circle(surf, bhi, (int(bxx - br // 3), int(byy - br // 3)),
                               max(1, br // 2))


def _fallen_leaf(surf, cx, cy, ang_pos, dist, leaf_ang, length, width, R):
    """A shed leaf lying INSIDE the lower disc (clamped to stay within the
    badge square). Drawn in dead-bronze with a curl so it reads as fallen,
    not floating."""
    px = cx + math.cos(ang_pos) * dist
    py = cy + math.sin(ang_pos) * dist
    _leaf_blade(surf, px, py, leaf_ang, length, width, _WILT_DEAD, _WILT_LO,
                vein=True)
    # a tiny curl tick at the tip sells "withered, fallen"
    tx = px + math.cos(leaf_ang) * length
    ty = py + math.sin(leaf_ang) * length
    pygame.draw.line(surf, _WILT_LO, (int(tx), int(ty)),
                     (int(tx - math.sin(leaf_ang) * length * 0.3),
                      int(ty + math.cos(leaf_ang) * length * 0.3)), 1)


# ════════════════════════════════════════════════════════════════════════════
# VARIATION 1 — OLYMPIC CIRCLET
# A near-full ring of small laurel leaves around the rim, open at the TOP with a
# small ribbon/gap (the head-crown / Olympic victor's circlet). Two mirrored
# arcs of many small leaves climb from a bottom join to a top opening.
# Shame: the top opening yawns wider (leaves shed near the crown), the ring sags,
# and a few leaves drop INTO the lower disc.
# ════════════════════════════════════════════════════════════════════════════

def _v1_circlet(surf, cx, cy, R, shame, icon_key, phase="ring"):
    if phase == "fallen":
        rng = random.Random(11)
        for _ in range(4):
            ap = math.radians(rng.uniform(70, 110))
            dist = R * rng.uniform(0.5, 0.8)
            _fallen_leaf(surf, cx, cy, ap, dist, rng.uniform(0, math.tau),
                         R * 0.13, R * 0.05, R)
        return
    # A SEGMENTED victor's circlet: 4 evenly-spaced leaf clusters around the ring
    # with clear bare-gold gaps between them, open at the top with ribbon ties.
    # Discrete clusters (not a continuous band) survive the shrink as leaves; the
    # symmetric 4-cluster coverage + open-top tie is its signature vs. the sparse
    # 2-sprig take. Anchors: lower-left, mid-left, mid-right, lower-right (the top
    # is left open for the crown gap).
    anchors = [math.radians(d) for d in (118, 162, 18, 62)]
    # Shame sheds one whole cluster (a real gap in the crown) — drop the mid-left.
    for k, a in enumerate(anchors):
        if shame and k == 1:
            continue                       # a whole cluster has fallen away
        _leaf_cluster(surf, cx, cy, a, R, shame, n=5,
                      spread=math.radians(60), leaf_len=R * 0.24,
                      width_f=0.065, shed_outer=2)
    # ribbon ties dangling inward from the two crown tips (head-wreath signature)
    top_gap = math.radians(44 if not shame else 70)
    tie = _WILT_MID if shame else _GOLD_MID
    for sgn in (-1, 1):
        ta = math.radians(-90) + sgn * top_gap * 0.5
        tx = cx + math.cos(ta) * R * 0.92
        ty = cy + math.sin(ta) * R * 0.92
        droopx = sgn * R * (0.16 if shame else 0.06)
        end = (tx + droopx, ty + R * 0.16)
        pygame.draw.line(surf, tie, (int(tx), int(ty)),
                         (int(end[0]), int(end[1])), max(1, R // 24))


# ════════════════════════════════════════════════════════════════════════════
# VARIATION 2 — SPARSE BRANCHES
# A few TINY branches, each with only 3–4 leaves, in an elegant minimalist
# formation: one small sprig low-left, one low-right, plus a single accent leaf.
# Lots of breathing room — the badge reads almost bare.
# Shame: branches snap/droop, leaves fall off them, a lone leaf rests in the disc.
# ════════════════════════════════════════════════════════════════════════════

def _sprig_fan(surf, cx, cy, anchor_a, R, n, shame, spread, leaf_len):
    """A tiny branch anchored on the rim crest: a short stem riding along the
    rim with a FAN of a few large leaves splaying outward from it. Minimal —
    lots of air between sprigs."""
    stem_col = _WILT_LO if shame else _GOLD_LO
    # the sprig is anchored just inside the rim crest so leaf bellies show
    ax = cx + math.cos(anchor_a) * R * 0.9
    ay = cy + math.sin(anchor_a) * R * 0.9
    droop = math.radians(22) if shame else 0
    # short stem climbing radially outward; leaves spaced ALONG it (a real twig)
    sx = cx + math.cos(anchor_a) * R * 1.04
    sy = cy + math.sin(anchor_a) * R * 1.04
    if n > 1:
        pygame.draw.line(surf, stem_col, (int(ax), int(ay)), (int(sx), int(sy)),
                         max(1, R // 30))
    for i in range(n):
        if shame and i == n - 1:
            continue                      # outermost leaf has dropped off
        f = (i / max(1, n - 1)) - 0.5     # -0.5..0.5 across the fan
        # base walks up the stem so the fan reads as a branch, not a rosette
        t = (i + 1) / (n + 1) if n > 1 else 0.0
        bx = ax + (sx - ax) * t * 0.7
        by = ay + (sy - ay) * t * 0.7
        la = anchor_a + f * spread + droop
        length = leaf_len * (1.0 - 0.12 * abs(f))
        width = R * 0.075
        col = _lit(_WILT_LO, _WILT_HI, la) if shame else _lit(_GOLD_LO, _GOLD_HI, la)
        edge = _WILT_LO if shame else _GOLD_LO
        length = _clamp_len(bx, by, la, length, cx, cy, R)
        _leaf_blade(surf, bx, by, la, length, width, col, edge)
    pygame.draw.circle(surf, stem_col, (int(ax), int(ay)), max(1, R // 24))


def _v2_sparse(surf, cx, cy, R, shame, icon_key, phase="ring"):
    if phase == "fallen":
        # Shame loss reads at row size: the top accent + the right sprig have
        # dropped, so 3 browned leaves rest inside the lower disc.
        rng = random.Random(3)
        for _ in range(3):
            ap = math.radians(rng.uniform(72, 108))
            dist = R * rng.uniform(0.48, 0.78)
            _fallen_leaf(surf, cx, cy, ap, dist, rng.uniform(0, math.tau),
                         R * 0.17, R * 0.065, R)
        return
    # Two graceful 3-leaf sprigs low on the flanks + a single top accent leaf —
    # generous breathing room, the badge reads almost bare. Long, well-splayed
    # blades so each fan reads as a little branch, not a clump of buds.
    _sprig_fan(surf, cx, cy, math.radians(150), R, 3, shame,
               math.radians(64), R * 0.30)
    if not shame:
        # right sprig + top accent only on the pristine wreath; in Shame they've
        # shed, opening an obvious bare gap on the right + top (the loss reads).
        _sprig_fan(surf, cx, cy, math.radians(30), R, 3, False,
                   math.radians(64), R * 0.30)
        _sprig_fan(surf, cx, cy, math.radians(-90), R, 1, False,
                   math.radians(0), R * 0.16)
    else:
        # the right sprig is now just a bare snapped stem (browned), no leaves
        sx = cx + math.cos(math.radians(30)) * R * 0.9
        sy = cy + math.sin(math.radians(30)) * R * 0.9
        ex = cx + math.cos(math.radians(30)) * R * 1.0
        ey = cy + math.sin(math.radians(30)) * R * 1.0
        pygame.draw.line(surf, _WILT_LO, (int(sx), int(sy)), (int(ex), int(ey)),
                         max(1, R // 28))


# ════════════════════════════════════════════════════════════════════════════
# VARIATION 3 — TWIN SPRIGS (REFINED)
# Two laurel sprigs rising from a bottom bow/knot, meeting near the top — a
# polished version of the current concept #1. Fuller, graceful taper, paired
# leaves, a real ribbon bow at the base.
# Shame: the bow is untied (one dangling tail), sprigs wilt/gap, leaves shed.
# ════════════════════════════════════════════════════════════════════════════

def _v3_twin(surf, cx, cy, R, shame, icon_key, phase="ring"):
    if phase == "fallen":
        if shame:
            rng = random.Random(7)
            for _ in range(3):
                ap = math.radians(rng.uniform(72, 108))
                dist = R * rng.uniform(0.5, 0.8)
                _fallen_leaf(surf, cx, cy, ap, dist, rng.uniform(0, math.tau),
                             R * 0.16, R * 0.055, R)
        return
    # Two MIRRORED sprigs, each a chain of 3 discrete leaf clusters climbing the
    # flank from the bottom bow toward the top — symmetric left/right, with bare
    # gold between the clusters so it never fuses into a gear. Shame sheds the top
    # cluster of each sprig (the open top yawns) + droops.
    n_clusters = 3
    for sgn in (-1, 1):
        # cluster anchor angles up each flank (bottom → upper), symmetric
        base_a = math.radians(108 if sgn < 0 else 72)
        top_a = math.radians(-44) - sgn * math.radians(0)
        for k in range(n_clusters):
            f = k / (n_clusters - 1)
            a = base_a + (top_a - base_a) * f
            if shame and k == n_clusters - 1:
                continue                    # top cluster of each sprig shed
            leaf_len = R * (0.26 - 0.06 * f)
            _leaf_cluster(surf, cx, cy, a, R, shame, n=4,
                          spread=math.radians(58),
                          leaf_len=leaf_len, width_f=0.075,
                          shed_outer=1)
    # ribbon bow at the base (kept inside the rim so it never clips)
    knot_y = int(cy + R * 0.86)
    bow_col = _WILT_MID if shame else _GOLD_MID
    bow_lo = _WILT_LO if shame else _GOLD_LO
    pygame.draw.circle(surf, bow_col, (cx, knot_y), max(3, R // 12))
    pygame.draw.circle(surf, bow_lo, (cx, knot_y), max(3, R // 12), 1)
    if not shame:
        # two tidy loops + two short tails
        for sgn in (-1, 1):
            loop = pygame.Rect(cx + sgn * R * 0.04, knot_y - R * 0.10,
                               R * 0.18, R * 0.20)
            if sgn < 0:
                loop.right = cx - R * 0.04
            pygame.draw.ellipse(surf, bow_col, loop, max(1, R // 30))
            pygame.draw.line(surf, bow_col, (cx, knot_y),
                             (int(cx + sgn * R * 0.16), int(knot_y + R * 0.14)),
                             max(1, R // 26))
    else:
        # untied: one loop gone, one tail dangles loose (still inside the square)
        loop = pygame.Rect(cx - R * 0.04, knot_y - R * 0.10, R * 0.18, R * 0.20)
        loop.right = cx - R * 0.04
        pygame.draw.ellipse(surf, bow_lo, loop, max(1, R // 30))
        # the other tail hangs loose, untied (kept inside the lower disc)
        pygame.draw.line(surf, bow_lo, (cx, knot_y),
                         (int(cx + R * 0.18), int(knot_y + R * 0.04)),
                         max(1, R // 24))


# ════════════════════════════════════════════════════════════════════════════
# VARIATION 4 — OLIVE + BERRIES
# Olive/laurel leaves with small round berry clusters tucked along the sprigs —
# the Olympic OLIVE wreath. Slimmer, longer leaves; clustered berries at joints.
# Shame: berries shrivel/drop, leaves brown and shed, lopsided ring.
# ════════════════════════════════════════════════════════════════════════════

def _v4_olive(surf, cx, cy, R, shame, icon_key, phase="ring"):
    if phase == "fallen":
        rng = random.Random(23)
        # dropped berries + a couple of fallen leaves in the disc
        for _ in range(3):
            ap = math.radians(rng.uniform(74, 106))
            dist = R * rng.uniform(0.5, 0.78)
            px = cx + math.cos(ap) * dist
            py = cy + math.sin(ap) * dist
            pygame.draw.circle(surf, _WILT_LO, (int(px), int(py)), max(2, int(R * 0.04)))
        for _ in range(2):
            ap = math.radians(rng.uniform(72, 108))
            dist = R * rng.uniform(0.5, 0.8)
            _fallen_leaf(surf, cx, cy, ap, dist, rng.uniform(0, math.tau),
                         R * 0.15, R * 0.04, R)
        return
    # 3 spaced leaf+berry clusters per side (~half the old leaf count) with clear
    # bare gaps between them, so the GAPS survive the shrink and the gold berries
    # stay visible (the signature). Slim leaves, but few + grouped so they read as
    # clusters, not fused teeth. Shame: berries shrivel/drop, top clusters shed.
    for sgn in (-1, 1):
        base_a = math.radians(110 if sgn < 0 else 70)
        top_a = math.radians(-48)
        for k in range(3):
            f = k / 2
            a = base_a + (top_a - base_a) * f
            if shame and k == 2:
                continue                    # top cluster has shed
            _leaf_cluster(surf, cx, cy, a, R, shame, n=3,
                          spread=math.radians(34),
                          leaf_len=R * 0.27, width_f=0.045,
                          berry=not (shame and k >= 1), shed_outer=1)
    # base join
    jc = _WILT_MID if shame else _GOLD_MID
    pygame.draw.circle(surf, jc, (cx, int(cy + R * 0.86)), max(2, R // 14))


# ════════════════════════════════════════════════════════════════════════════
# VARIATION 5 — LUSH DENSE WREATH
# A full continuous leafy ring — dense, overlapping leaves all the way around,
# rich and heavy (a true full wreath, closed at the top).
# Shame: big bald patches where clumps shed, the ring droops lopsided, a heap of
# fallen leaves piles in the lower disc.
# ════════════════════════════════════════════════════════════════════════════

def _v5_lush(surf, cx, cy, R, shame, icon_key, phase="ring"):
    rng = random.Random(5)
    if phase == "fallen":
        if shame:
            # a heap of fallen leaves piled inside the lower disc
            for _ in range(7):
                ap = math.radians(rng.uniform(60, 120))
                dist = R * rng.uniform(0.45, 0.82)
                _fallen_leaf(surf, cx, cy, ap, dist, rng.uniform(0, math.tau),
                             R * rng.uniform(0.12, 0.17), R * 0.06, R)
        return
    # The "fullest" option, but still DISCRETE: 6 big leaf TUFTS at evenly-spaced
    # points (skipping the very top so the emblem reads), each a fat fan of bold
    # leaves pulled OFF the disc (base on the rim crest, tips outward) with clear
    # bare gold between tufts — so it never pinches the emblem or fuses to a gear,
    # yet has the biggest, boldest leaves of the set. Shame: two whole tufts shed.
    anchors = [math.radians(d) for d in (130, 90, 50, 230, 270, 310)]
    shed = {1, 4} if shame else set()       # drop a lower + upper tuft in Shame
    for k, a in enumerate(anchors):
        if k in shed:
            continue
        _leaf_cluster(surf, cx, cy, a, R, shame, n=5,
                      spread=math.radians(72), leaf_len=R * 0.27,
                      width_f=0.10, shed_outer=2)


VARIATIONS = [
    ("olympic_circlet", _v1_circlet),
    ("sparse_branches", _v2_sparse),
    ("twin_sprigs", _v3_twin),
    ("olive_berries", _v4_olive),
    ("lush_dense", _v5_lush),
]


def compose(size, wreath_fn, shame, icon_key):
    """Render one full badge (supersampled) — wreath behind, medallion on top."""
    S = ai._SS
    px = size * S
    surf = pygame.Surface((px, px), pygame.SRCALPHA)
    cx = cy = px // 2
    R = int(px * 0.46)
    glow_col = (120, 88, 56) if shame else (255, 200, 90)
    blit_glow(surf, cx, cy, int(R * 1.08), glow_col, 70 if shame else 95)
    # Order: fallen leaves (deep, behind everything) → rim → wreath ring (on the
    # rim band so leaf bellies read against the metal) → step+face+glyph (clean).
    if shame:
        wreath_fn(surf, cx, cy, R, shame, icon_key, phase="fallen")
    _medallion(surf, cx, cy, R, shame, icon_key)
    wreath_fn(surf, cx, cy, R, shame, icon_key, phase="ring")
    _medallion_face(surf, cx, cy, R, shame, icon_key)
    return pygame.transform.smoothscale(surf, (size, size))
