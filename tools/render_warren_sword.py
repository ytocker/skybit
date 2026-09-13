"""Look-dev renderer (Round 6): the WARREN EVENT prop — BROADENED + RE-POSED.

ROUND 6 broadens the concept beyond swords and fixes the lean pose. Two changes
drove this round:
  (1) BROADEN — the clown can hold ANYTHING interesting. ~15 holistic props now
      span FOUR families (~4/4/4/3): A SWORDS & BLADES (the round-5 winners,
      re-posed), B STAFFS & SCEPTERS, C CLOWN PROPS, D MYSTIC & MENACING. Each
      is a COMPLETE, structurally distinct object, authored gap-facing-end UP so
      the route flip scaffolding plants it correctly.
  (2) FIX THE POSE — round 5 held the sword awkwardly upward behind the head. The
      new pose stands the prop VERTICALLY with its bottom tip resting ON THE
      GROUND beside the clown; the near/lower gloved hand grips it near the top
      (a relaxed showman LEAN, weight resting on the prop) while the OTHER hand
      still presents the floating power-up die up high. The pose is IDENTICAL
      every row; only the prop changes.

The three gameplay GATES still drive every prop at ROUTE scale (~30-40 px wide):
  1. GAP READABILITY — the gap-facing END is a clean readable terminus (point,
     finial, orb, hook, prongs, star) with a hard dark-body→bright-gap value
     break; even BLUNT-topped props (lollipop, orb, knob cane) are shaped + dark-
     rimmed so the sky-gap stays the brightest, sharpest band.
  2. DAY-SKY CONTRAST — median BODY luma under ~140 against the ~190 day sky
     (round-5 ran hot at 165-172; highlight ramps pulled down ~15-20%). Opaque
     dark cores; no pale-on-blue.
  3. DE-NOISE — 2-3 bold elements per prop in the route silhouette; the LEFT
     leaned hero shot may carry finer detail than the tiled RIGHT version.

Prior lineage (Round 5): the WARREN EVENT sword — CONCEPT REDESIGN.

Rounds 1-4 (35 swords) were ALL rejected for one root reason finally pinned
down: every version was the SAME silhouette recolored. The old code piped all
blades through one shared `_hilt_basic()` (crossguard + grip + pommel), so only
the BLADE re-colored — the handle and base never changed. The clown was never
shown holding the weapon, so the swords read as abstract pillars, not as the
ONE complete sword the clown carries and the route is filled with.

NEW DIRECTION: the clown holds a single COMPLETE believable weapon and the
route is that SAME weapon tiled. So each of the 12 designs is a HOLISTIC sword —
a distinct BLADE FORM **and** GUARD **and** GRIP **and** POMMEL composed as one
coherent weapon. NO two share a hilt or a profile; no recolors. The 12 span
three registers (~4 each):
  CARTOON   — playful, tied to the clown's Plum & Lime world.
  REALISTIC — four DIFFERENT real sword families (falchion / saber / leaf /
              greatsword), not one blade recolored.
  FANTASY   — dramatic hero/boss weapons.

The STRUCTURAL FIX: each sword has its OWN complete draw function that builds a
distinct blade silhouette + its OWN crossguard + grip + pommel. The small
reusable PRIMITIVES (`_vgrad_poly`, `_edge_glow`, `_glow_disc`, `_rivet`,
`_wrap_grip`, plus new `_disc_pommel`, `_ball_pommel`, `_facet_gem`,
`_ribbed_grip`, `_candy_twist`, `_bone_grip`, `_crossguard`) are COMPOSED into
12 genuinely different weapons — different guard TYPES (cross / basket / disc /
swept / winged / bell / jaw), grips (wrapped / ribbed / candy-twist / bone /
vertebra), pommels (round / faceted gem / crown / balloon / skull / horned).

The figure: 12 ROWS, each TWO panels.
  LEFT  — THE CLOWN HOLDING THIS SWORD. The REAL game jester (`build_jester`
          + `JESTERS[-1]`, exactly as `game/warren_demo.py` builds the hero
          clown) with THIS sword gripped in its raised gloved hand, a few
          fingers + thumb drawn OVER the hilt so it reads as truly held.
  RIGHT — THE ROUTE FILLED WITH IT. The true-geometry day-sky panorama: every
          pillar is THIS sword — bottom obstacle a full sword point-UP from the
          ground, top obstacle the same sword point-DOWN from the ceiling, a
          flyable sky-gap between the two tips.

The three gameplay GATES drive EVERY version at ROUTE scale (~30-40 px wide):
  1. GAP READABILITY — the sky-gap between the two tips is the brightest /
     sharpest band; a hard dark-body -> bright-gap value break; sharp tips.
  2. DAY-SKY CONTRAST — weapon BODY luma well under the ~173 day sky (aim <120);
     opaque dark cores, never pale/translucent on blue.
  3. DE-NOISE — 2-3 bold elements per weapon at route scale. Fine hilt ornament
     is fine on the LEFT clown hero shot but must NOT fizz in the RIGHT route
     panorama — the held version can carry more detail than the tiled version.

All art is procedural; supersampled then smoothscaled for crisp edges. The
box / flip / panorama scaffolding (`_box`, `_render_obstacle`, `_blit_pair`,
`_route_panel`) is carried from round 2/4 unchanged — only the 12 weapons + the
held-clown panel are new.

Run (headless):
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONPATH=. \
        python tools/render_warren_sword.py
Writes docs/warren_sword/round_6.png.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import hud  # noqa: E402  vendored bold TTF + cache
from game.draw import lerp_color, _shade_c  # noqa: E402

# ── true game footprint ──────────────────────────────────────────────────────
PIPE_W = 58
GROUND_Y = 595
PLAY_W = 360
PLAY_H = 640
GAP_H = 172
HALF_GAP = GAP_H // 2          # 86
SP = 72                        # route centre-to-centre spacing

# Day sky for contrast — a simple top→bottom blue (~173 luma).
SKY_TOP = (96, 165, 230)
SKY_BOT = (175, 215, 245)

# Plum & Lime clown world palette (so the cartoon swords tie to the hero clown).
PLUM = (96, 44, 150)
PLUM_DK = (66, 28, 110)
LIME = (132, 218, 116)
LIME_DK = (74, 150, 70)
GOLD = (250, 205, 72)
GOLD_HI = (255, 236, 150)
GOLD_DK = (176, 130, 30)
GOLD_SHADOW = (110, 78, 22)
CREAM = (255, 248, 224)
INK = (28, 22, 30)

# Neutral dark hilt metals (always hold value on blue).
IRON_DK = (40, 44, 52)
IRON_MD = (78, 84, 96)
IRON_HI = (150, 158, 172)
STEEL_DK = (52, 58, 70)
STEEL_MD = (104, 112, 128)
STEEL_HI = (176, 184, 200)
LEATHER = (74, 52, 38)
LEATHER_DK = (48, 34, 26)
LEATHER_HI = (118, 86, 58)
BRONZE_LO = (72, 46, 20)
BRONZE_MD = (132, 90, 40)
BRONZE_HI = (180, 134, 66)
BONE = (224, 214, 184)
BONE_DK = (150, 138, 108)


# ════════════════════════════════════════════════════════════════════════════
#  REUSABLE PRIMITIVES — kept small + composable. EACH sword COMPOSES these into
#  its OWN guard + grip + pommel; nothing routes through a shared hilt.
# ════════════════════════════════════════════════════════════════════════════

def _vgrad_poly(surf, pts, top_col, bot_col, *, outline=None, ow=2):
    """Fill a polygon with a vertical gradient via an alpha-masked gradient band,
    so a blade body reads as a lit volume rather than a flat fill."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)), int(min(ys))
    w = max(1, int(max(xs)) - x0 + 2)
    h = max(1, int(max(ys)) - y0 + 2)
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(h):
        grad.fill(lerp_color(top_col, bot_col, i / max(1, h - 1)) + (255,),
                  (0, i, w, 1))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    local = [(p[0] - x0, p[1] - y0) for p in pts]
    pygame.draw.polygon(mask, (255, 255, 255, 255), local)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (x0, y0))
    if outline is not None:
        pygame.draw.polygon(surf, outline, pts, max(1, ow))


def _edge_glow(surf, pts, col, ss, *, alpha=140, spread=5):
    """A soft emissive glow hugging a polyline; ADD-blended so the edge reads as
    lit on both day and night sky without a full glow-cache disc."""
    for k in range(spread, 0, -1):
        a = int(alpha * (k / spread) * 0.5)
        wln = max(1, int(k * 1.6 * ss))
        layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        if len(pts) >= 2:
            pygame.draw.lines(layer, col + (a,), False, pts, wln)
        surf.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)


def _glow_disc(surf, cx, cy, r, col, ss, *, alpha=150, falloff=1.8):
    """A radial ADD glow disc (for a gem / eye / rune highlight)."""
    rr = max(1, int(r))
    g = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
    for ri in range(rr, 0, -1):
        t = (ri / rr) ** falloff
        a = int(alpha * (1 - t))
        pygame.draw.circle(g, col + (max(0, a),), (rr + 1, rr + 1), ri)
    surf.blit(g, (int(cx) - rr - 1, int(cy) - rr - 1), special_flags=pygame.BLEND_ADD)


def _rivet(surf, x, y, r, col):
    pygame.draw.circle(surf, _shade_c(col, -40), (int(x), int(y)), int(r))
    pygame.draw.circle(surf, _shade_c(col, 50), (int(x - r * 0.3), int(y - r * 0.3)),
                       max(1, int(r * 0.45)))


def _wrap_grip(surf, cx, top, bot, hw, base_col, ss, *, diag=False):
    """A wrapped grip column drawn as bold bands (no fine cross-hatch). `diag`
    skews the band seams into leather-wrap diagonals for a corded read."""
    base_col_dk = _shade_c(base_col, -46)
    band_h = max(4, int(7 * ss))
    y = int(top)
    i = 0
    while y < bot:
        c = base_col if i % 2 == 0 else _shade_c(base_col, -26)
        pygame.draw.rect(surf, c, (int(cx - hw), y, int(hw * 2), band_h))
        if diag:
            pygame.draw.line(surf, base_col_dk, (int(cx - hw), y),
                             (int(cx + hw), y + band_h), max(1, int(ss)))
        else:
            pygame.draw.line(surf, base_col_dk, (int(cx - hw), y),
                             (int(cx + hw), y), max(1, int(ss)))
        y += band_h
        i += 1
    pygame.draw.line(surf, base_col_dk, (int(cx - hw), int(top)),
                     (int(cx - hw), int(bot)), max(1, int(ss)))
    pygame.draw.line(surf, base_col_dk, (int(cx + hw), int(top)),
                     (int(cx + hw), int(bot)), max(1, int(ss)))


def _ribbed_grip(surf, cx, top, bot, hw, base_col, ss):
    """A wire-bound RIBBED grip: a dark column ringed with bold lit bands, so the
    grip reads as twisted metal wire rather than flat leather."""
    pygame.draw.rect(surf, _shade_c(base_col, -40), (int(cx - hw), int(top),
                                                     int(hw * 2), int(bot - top)))
    band_h = max(3, int(5 * ss))
    y = int(top)
    while y < bot:
        pygame.draw.line(surf, _shade_c(base_col, 40), (int(cx - hw), y),
                         (int(cx + hw), y - max(1, int(2 * ss))), max(1, int(2 * ss)))
        y += band_h
    pygame.draw.line(surf, _shade_c(base_col, 60), (int(cx - hw * 0.5), int(top)),
                     (int(cx - hw * 0.5), int(bot)), max(1, int(ss)))


def _candy_twist(surf, cx, top, bot, hw, col_a, col_b, ss):
    """A barber-pole CANDY-TWIST grip: alternating diagonal stripes of two
    colours spiralling up the grip — the cartoon hero grip."""
    pygame.draw.rect(surf, _shade_c(col_a, -30), (int(cx - hw), int(top),
                                                  int(hw * 2), int(bot - top)))
    stripe = max(4, int(6 * ss))
    n = int((bot - top) / stripe) + 3
    for i in range(-2, n):
        y0 = top + i * stripe
        col = col_a if i % 2 == 0 else col_b
        quad = [(cx - hw, y0), (cx + hw, y0 - hw * 1.4),
                (cx + hw, y0 - hw * 1.4 + stripe), (cx - hw, y0 + stripe)]
        # Clip to the grip column via a mask so the diagonals stay inside.
        pygame.draw.polygon(surf, col, quad)
    # Re-clip: redraw the column outline so spill past the sides is hidden by a
    # second pass of side rails the blade base/pommel will overlap anyway.
    pygame.draw.rect(surf, _shade_c(col_a, -55), (int(cx - hw), int(top),
                                                  int(hw * 2), int(bot - top)),
                     max(1, int(1.6 * ss)))
    pygame.draw.line(surf, _shade_c(CREAM, 0), (int(cx - hw * 0.5), int(top)),
                     (int(cx - hw * 0.5), int(bot)), max(1, int(ss)))


def _bone_grip(surf, cx, top, bot, hw, ss, *, vertebra=False):
    """A carved BONE grip: a pale ivory column with dark sockets. `vertebra`
    stacks fat rounded bone segments (the demon-blade spine grip) instead of a
    smooth shaft."""
    if vertebra:
        seg_h = max(6, int(11 * ss))
        y = int(top)
        i = 0
        while y < bot:
            ch = min(seg_h, int(bot) - y)
            r = hw
            pygame.draw.ellipse(surf, BONE_DK, (int(cx - r), y, int(r * 2), ch + 2))
            pygame.draw.ellipse(surf, BONE, (int(cx - r + ss), y, int(r * 2 - 2 * ss), ch))
            pygame.draw.line(surf, _shade_c(BONE_DK, -30), (int(cx - r), y),
                             (int(cx + r), y), max(1, int(1.4 * ss)))
            y += seg_h
            i += 1
    else:
        pygame.draw.rect(surf, BONE_DK, (int(cx - hw), int(top),
                                         int(hw * 2), int(bot - top)))
        pygame.draw.rect(surf, BONE, (int(cx - hw + ss), int(top),
                                      int(hw * 2 - 2 * ss), int(bot - top)))
        for t in (0.28, 0.6):
            sy = top + (bot - top) * t
            pygame.draw.circle(surf, _shade_c(BONE_DK, -40), (int(cx), int(sy)),
                               max(2, int(hw * 0.35)))


def _crossguard(surf, cx, gy, ghw, thick, col, ss, *, curve=0.0, dk=None,
                quillon_r=0.55):
    """A horizontal crossguard centred at (cx, gy) spanning +-ghw, `thick` tall,
    with knobbed quillon ends. `curve` bows the bar; `quillon_r` scales the end
    knobs (0 disables them)."""
    dk = dk or _shade_c(col, -50)
    top = [(cx - ghw, gy - thick * 0.5)]
    bot = [(cx - ghw, gy + thick * 0.5)]
    n = 10
    for i in range(n + 1):
        t = i / n
        x = cx - ghw + 2 * ghw * t
        bow = math.sin(t * math.pi) * curve
        top.append((x, gy - thick * 0.5 + bow))
        bot.append((x, gy + thick * 0.5 + bow))
    poly = top + list(reversed(bot))
    pygame.draw.polygon(surf, col, poly)
    pygame.draw.polygon(surf, dk, poly, max(1, int(ss)))
    if quillon_r > 0:
        for sgn in (-1, 1):
            pygame.draw.circle(surf, col, (int(cx + sgn * ghw), int(gy)),
                               int(thick * quillon_r))
            pygame.draw.circle(surf, dk, (int(cx + sgn * ghw), int(gy)),
                               int(thick * quillon_r), max(1, int(ss)))
            pygame.draw.circle(surf, _shade_c(col, 50),
                               (int(cx + sgn * ghw - thick * 0.2),
                                int(gy - thick * 0.2)), max(1, int(thick * 0.22)))


def _ball_pommel(surf, cx, py, r, col, ss, *, dk=None, glossy=False):
    dk = dk or _shade_c(col, -55)
    pygame.draw.circle(surf, dk, (int(cx), int(py)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(py)), int(r - ss))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - r * 0.3), int(py - r * 0.3)), max(1, int(r * 0.4)))
    if glossy:
        # A hot specular spot + a soft crescent so it reads as a glossy balloon.
        pygame.draw.circle(surf, (255, 255, 255),
                           (int(cx - r * 0.34), int(py - r * 0.38)),
                           max(1, int(r * 0.2)))


def _disc_pommel(surf, cx, py, r, col, ss, *, dk=None):
    """A flat wheel/disc pommel seen edge-on — a squat oval, the realistic
    medieval pommel, distinct from the round ball."""
    dk = dk or _shade_c(col, -55)
    rect = pygame.Rect(int(cx - r), int(py - r * 0.62), int(r * 2), int(r * 1.24))
    pygame.draw.ellipse(surf, dk, rect)
    pygame.draw.ellipse(surf, col, rect.inflate(-int(2 * ss), -int(2 * ss)))
    pygame.draw.circle(surf, _shade_c(col, 45),
                       (int(cx - r * 0.3), int(py - r * 0.2)), max(1, int(r * 0.3)))
    pygame.draw.circle(surf, dk, (int(cx), int(py)), max(2, int(r * 0.22)))


def _facet_gem(surf, cx, cy, r, col, hi, dk, ss):
    """A faceted oval gem: a dark setting, two big facet halves, a hot glint."""
    pts = [(cx, cy - r), (cx + r * 0.85, cy - r * 0.4),
           (cx + r * 0.85, cy + r * 0.4), (cx, cy + r),
           (cx - r * 0.85, cy + r * 0.4), (cx - r * 0.85, cy - r * 0.4)]
    _glow_disc(surf, cx, cy, int(r * 1.2), col, ss, alpha=120)
    pygame.draw.polygon(surf, dk, pts)
    pygame.draw.polygon(surf, col,
                        [(cx, cy - r), (cx + r * 0.85, cy - r * 0.4),
                         (cx, cy + r * 0.2)])
    pygame.draw.polygon(surf, hi,
                        [(cx, cy - r), (cx - r * 0.85, cy - r * 0.4),
                         (cx, cy + r * 0.2)])
    pygame.draw.polygon(surf, (255, 255, 255), pts, max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, (255, 255, 255), (int(cx - r * 0.3), int(cy - r * 0.4)),
                       max(1, int(r * 0.16)))


# ── the sword frame (carried from round 2/4) ─────────────────────────────────
OVERHANG = 12                  # guards may spill this far past the 58-px column
HILT_PX = 138                  # nominal hilt height, true px
MIN_BLADE_PX = 40


def _box(H, ss):
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(H)) * ss
    return pygame.Surface((bw, bh), pygame.SRCALPHA), bw, bh


def _layout(bh, ss, *, hilt_px=HILT_PX):
    """Key y-coords (SS space) for a point-UP sword in a box of SS height bh:
    tip at top (y=0), pommel at the bottom. Returns
    (tip_y, blade_base_y, guard_y, grip_top_y, grip_bot_y, pommel_y)."""
    hilt = hilt_px * ss
    if hilt > bh - MIN_BLADE_PX * ss:
        hilt = max(0, bh - MIN_BLADE_PX * ss)
    tip_y = int(0)
    guard_y = int(bh - hilt + 0.30 * hilt)
    blade_base_y = guard_y
    grip_top_y = guard_y
    pommel_y = int(bh - max(6 * ss, hilt * 0.10))
    grip_bot_y = int(pommel_y - 4 * ss)
    return tip_y, blade_base_y, guard_y, grip_top_y, grip_bot_y, pommel_y


def _blade_hw(ss):
    return int((PIPE_W * 0.5 - 6) * ss)


def _guard_hw(ss):
    return int((PIPE_W * 0.5 + OVERHANG - 2) * ss)


def _straight_body(cx, tip_y, base_y, hw, *, taper=0.0):
    """The canonical hard-taper double-edged silhouette (apex == box top so the
    dark body meets bright sky as a single razor break — GATE 1)."""
    bw = hw * (1.0 + taper)
    return [(cx - bw, base_y), (cx, tip_y), (cx + bw, base_y)], bw


def _curved_body(cx, tip_y, base_y, hw, *, bow=0.30, edge=1.0):
    """A single-edged CURVED (saber/falchion) silhouette: the back spine bows
    one way, the cutting edge swells then sweeps to the same hard tip. `bow` is
    the sideways curve of the tip; `edge` swells the belly. Returns (pts, bw)."""
    span = base_y - tip_y
    bw = hw
    spine, edgep = [], []
    n = 14
    # The body keeps its original profile, but the back spine used to hold a fixed
    # offset while the edge only narrowed to ~0.08*hw, so the two sides never met
    # and the blade ended in a blunt FLAT edge. Over the last stretch (t > TIP_CLOSE)
    # ramp BOTH sides in to zero so they converge on the tip vertex — closing that
    # flat end into a sharp point without touching the rest of the silhouette.
    TIP_CLOSE = 0.74
    for i in range(n + 1):
        t = i / n                       # 0 at base, 1 at tip
        y = base_y - span * t
        arc = math.sin(t * math.pi)     # 0 at ends, 1 mid
        cxt = cx + bow * hw * (t ** 1.3)   # whole blade leans toward the tip side
        bwt = hw * (1.0 - t * 0.92) + edge * hw * 0.5 * arc * (1 - t * 0.4)
        close = 1.0 if t <= TIP_CLOSE else 1.0 - (t - TIP_CLOSE) / (1.0 - TIP_CLOSE)
        spine.append((cxt - (bw * 0.32 + bwt * 0.18) * close, y))  # back (spine)
        edgep.append((cxt + bwt * close, y))                       # cutting (belly)
    tip = (cx + bow * hw, tip_y)
    pts = spine + [tip] + list(reversed(edgep))
    return pts, bw


# ════════════════════════════════════════════════════════════════════════════
#  CARTOON REGISTER (tied to Plum & Lime) — 4 weapons
# ════════════════════════════════════════════════════════════════════════════

# ---- 1. Candy-Twist Cutlass -------------------------------------------------
# A fat curved TOON blade, a spiral red/cream barber-pole candy grip, a big
# round candy pommel, a curled-S brass guard. The grip + pommel are pure candy.
CANDY_RED = (214, 54, 64)
CANDY_RED_DK = (150, 28, 38)
CANDY_CREAM = (255, 244, 226)
# Toon steel keyed DARK at the core so the blade BODY clears the ~173 day sky
# (GATE 2) — the bright sheen lives only as a thin top-lit band + the fuller, so
# the body still reads as playful polished steel without washing out on blue.
TOON_STEEL_HI = (150, 170, 200)
TOON_STEEL_MD = (96, 116, 146)
TOON_STEEL_LO = (40, 54, 78)
BRASS = (236, 188, 86)
BRASS_DK = (170, 120, 40)


def sword_01(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.12)
    ghw = _guard_hw(ss)
    # A fat curved toon cutlass blade — bellied single edge to a hard tip.
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.34, edge=0.55)
    _vgrad_poly(surf, body, TOON_STEEL_HI, TOON_STEEL_LO, outline=(30, 40, 58),
                ow=max(2, int(2.2 * ss)))
    # One bold dark fuller groove following the curve (the single body accent).
    span = base_y - tip_y
    fuller = [(cx + 0.34 * hw * (t ** 1.3) - hw * 0.05, base_y - span * t)
              for t in (0.08, 0.4, 0.72, 0.92)]
    pygame.draw.lines(surf, TOON_STEEL_MD, False, fuller, max(2, int(2.2 * ss)))
    # Curled-S brass guard (a fat cartoon swoop, knobbed ends).
    _crossguard(surf, cx, gy, ghw, int(13 * ss), BRASS, ss, curve=int(7 * ss),
                dk=BRASS_DK, quillon_r=0.7)
    pygame.draw.arc(surf, BRASS, (int(cx - ghw), int(gy - 4 * ss),
                                  int(ghw * 1.1), int(20 * ss)),
                    math.pi * 0.1, math.pi * 0.9, max(2, int(3 * ss)))
    # Spiral red/cream BARBER-POLE candy grip.
    _candy_twist(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.42),
                 CANDY_RED, CANDY_CREAM, ss)
    # Big round glossy CANDY pommel (a peppermint swirl).
    pr = int(hw * 0.52)
    _ball_pommel(surf, cx, py, pr, CANDY_CREAM, ss, dk=CANDY_RED_DK, glossy=True)
    for k in range(5):
        a = k * math.tau / 5 - math.pi / 2
        pygame.draw.line(surf, CANDY_RED, (cx, py),
                         (cx + math.cos(a) * pr * 0.8, py + math.sin(a) * pr * 0.8),
                         max(2, int(2.2 * ss)))


# ---- 2. Jester-Bell Sabre ---------------------------------------------------
# A playful curved sabre whose GUARD is a row of gold jester bells; a lime
# tassel hangs off the pommel, the grip is plum-wrapped. Pure clown costume.
def sword_02(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.0)
    ghw = _guard_hw(ss)
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.26, edge=0.30)
    _vgrad_poly(surf, body, (150, 168, 196), (48, 64, 92), outline=(28, 38, 56),
                ow=max(2, int(2.0 * ss)))
    # Lit cutting edge sweeping to the hard tip (the bright back-edge beat) — kept
    # as a THIN bright sliver so the body luma stays dark on day-blue (GATE 2).
    span = base_y - tip_y
    edge = [(cx + 0.26 * hw * (t ** 1.3) + hw * (1.0 - t * 0.9), base_y - span * t)
            for t in (0.05, 0.4, 0.7, 0.95)]
    pygame.draw.lines(surf, (224, 234, 246), False, edge, max(1, int(1.6 * ss)))
    # GUARD = a row of gold jester BELLS strung across the crossguard.
    nb = 5
    pygame.draw.line(surf, GOLD_DK, (cx - ghw, gy), (cx + ghw, gy), max(2, int(3 * ss)))
    for i in range(nb):
        t = (i + 0.5) / nb
        bx = cx - ghw + 2 * ghw * t
        br = int(7 * ss)
        pygame.draw.circle(surf, GOLD_DK, (int(bx), int(gy + 3 * ss)), br + 1)
        pygame.draw.circle(surf, GOLD, (int(bx), int(gy + 3 * ss)), br)
        pygame.draw.circle(surf, GOLD_HI, (int(bx - br * 0.3), int(gy + 3 * ss - br * 0.3)),
                           max(1, int(br * 0.4)))
        pygame.draw.line(surf, GOLD_DK, (int(bx - br * 0.5), int(gy + 6 * ss)),
                         (int(bx + br * 0.5), int(gy + 6 * ss)), max(1, int(ss)))
    # Plum-wrapped grip.
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.38), PLUM, ss, diag=True)
    # Gold ball pommel with a LIME tassel hanging off it.
    pr = int(hw * 0.42)
    _ball_pommel(surf, cx, py, pr, GOLD, ss, dk=GOLD_DK)
    for k in (-1, 0, 1):
        tx = cx + k * int(4 * ss)
        pygame.draw.line(surf, LIME, (tx, py + pr), (tx + k * int(2 * ss), py + pr + int(16 * ss)),
                         max(2, int(2.4 * ss)))
    pygame.draw.circle(surf, LIME_DK, (cx, int(py + pr + 16 * ss)), int(5 * ss))
    pygame.draw.circle(surf, LIME, (cx, int(py + pr + 15 * ss)), int(4 * ss))


# ---- 3. Balloon-Pommel Shortsword -------------------------------------------
# A chunky toon shortsword: a short broad straight blade, a HUGE glossy balloon-
# round pommel (a clown's balloon), a gloved-friendly fat plum grip, lime guard.
def sword_03(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.16)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.06)
    _vgrad_poly(surf, body, (148, 166, 194), (46, 62, 90), outline=(26, 38, 56),
                ow=max(2, int(2.4 * ss)))
    # One NARROW bright centre stripe to a hard apex (chunky toon read) — kept
    # slim so most of the body stays dark against the day sky (GATE 2).
    pygame.draw.polygon(surf, (224, 234, 246),
                        [(cx - bwid * 0.12, base_y - int(6 * ss)),
                         (cx, tip_y + int(12 * ss)),
                         (cx + bwid * 0.12, base_y - int(6 * ss))])
    # A fat rounded LIME guard (a soft toon crossbar, balloon-knot ends).
    pygame.draw.rect(surf, LIME, (int(cx - ghw), int(gy - 8 * ss),
                                  int(ghw * 2), int(16 * ss)),
                     border_radius=int(8 * ss))
    pygame.draw.rect(surf, LIME_DK, (int(cx - ghw), int(gy - 8 * ss),
                                     int(ghw * 2), int(16 * ss)),
                     max(2, int(2 * ss)), border_radius=int(8 * ss))
    pygame.draw.line(surf, _shade_c(LIME, 40), (int(cx - ghw + 4 * ss), int(gy - 5 * ss)),
                     (int(cx + ghw - 4 * ss), int(gy - 5 * ss)), max(1, int(2 * ss)))
    # Fat plum gloved-friendly grip.
    _wrap_grip(surf, cx, gy + int(10 * ss), gbot - int(2 * ss), int(hw * 0.46), PLUM, ss)
    # HUGE glossy BALLOON pommel — the hero feature, with a tied knot beneath.
    pr = int(hw * 0.78)
    bcy = int(py + pr * 0.2)
    pygame.draw.circle(surf, _shade_c(CANDY_RED, -40), (cx, bcy), pr + int(ss))
    pygame.draw.circle(surf, CANDY_RED, (cx, bcy), pr)
    _glow_disc(surf, cx - pr * 0.3, bcy - pr * 0.3, int(pr * 0.7), (255, 220, 200),
               ss, alpha=90)
    pygame.draw.circle(surf, (255, 245, 240), (int(cx - pr * 0.34), int(bcy - pr * 0.38)),
                       max(2, int(pr * 0.24)))
    pygame.draw.polygon(surf, CANDY_RED_DK,
                        [(cx - int(4 * ss), bcy + pr - int(2 * ss)),
                         (cx + int(4 * ss), bcy + pr - int(2 * ss)),
                         (cx, bcy + pr + int(6 * ss))])


# ---- 4. Foam-Wobble Greatsword ----------------------------------------------
# An oversized SOFT wobbly cartoon greatsword: a bouncy bulged blade with rounded
# wobble edges, a plum-wrapped two-hand grip, lime ric-rac guard, gold gem
# pommel. Bouncy proportions, the playful "big foam prop" sword.
def sword_04(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss, hilt_px=150)
    hw = int(_blade_hw(ss) * 1.18)
    ghw = _guard_hw(ss)
    span = base_y - tip_y
    # A WOBBLY bulged blade: edges bow out then pinch, ending in a soft-but-
    # pointed tip. Built as a smooth wavy silhouette (kept low-frequency so it
    # reads as ONE bouncy shape, not fizz).
    left, right = [], []
    n = 12
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        wob = math.sin(t * math.pi * 1.5) * 0.16
        w = hw * (1.0 - t * 0.86) * (1.0 + wob)
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + [(cx, tip_y)] + list(reversed(right))
    _vgrad_poly(surf, body, (150, 168, 196), (52, 70, 100), outline=(30, 44, 64),
                ow=max(3, int(3.0 * ss)))
    # One NARROW soft highlight riding the upper blade (the foam-prop sheen) —
    # slim so the body luma stays dark on day-blue (GATE 2).
    pygame.draw.polygon(surf, (228, 238, 248),
                        [(cx - hw * 0.1, base_y - span * 0.35),
                         (cx, tip_y + int(16 * ss)),
                         (cx + hw * 0.1, base_y - span * 0.35)])
    # Lime ric-rac (wavy) guard — a soft scalloped crossbar.
    gy0 = gy
    pts_t, pts_b = [], []
    for i in range(9):
        t = i / 8
        x = cx - ghw + 2 * ghw * t
        yy = gy0 + math.sin(t * math.pi * 4) * int(4 * ss)
        pts_t.append((x, yy - int(7 * ss)))
        pts_b.append((x, yy + int(7 * ss)))
    pygame.draw.polygon(surf, LIME, pts_t + list(reversed(pts_b)))
    pygame.draw.polygon(surf, LIME_DK, pts_t + list(reversed(pts_b)), max(2, int(2 * ss)))
    # Plum two-hand wrapped grip (longer).
    _wrap_grip(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.40), PLUM, ss, diag=True)
    # Gold faceted-gem pommel.
    _ball_pommel(surf, cx, py, int(hw * 0.5), GOLD, ss, dk=GOLD_DK)
    _facet_gem(surf, cx, py, int(hw * 0.26), CANDY_RED, (255, 150, 150),
               CANDY_RED_DK, ss)


# ════════════════════════════════════════════════════════════════════════════
#  REALISTIC REGISTER — 4 DIFFERENT forged sword families
# ════════════════════════════════════════════════════════════════════════════

# ---- 5. Cleaver Falchion ----------------------------------------------------
# A broad single-edge FALCHION: a heavy clip-point chopping blade, a simple iron
# cross, a plain leather grip, a flat iron DISC pommel. Honest working steel.
def sword_05(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    # Narrowed ~15% from round 6 so the broad chopper threads as cleanly as its
    # blade siblings instead of eating into the sky-gap.
    hw = int(_blade_hw(ss) * 0.97)
    ghw = int(_guard_hw(ss) * 0.86)
    span = base_y - tip_y
    # Broad falchion: a near-straight back spine, a belly that swells toward the
    # tip then clips back to a hard point (the cleaver profile).
    spine, belly = [], []
    n = 12
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        # belly swells in the lower-mid, clips in near the tip
        bell = hw * (0.70 + 0.55 * math.sin(min(1, t * 1.15) * math.pi * 0.8))
        bell *= (1.0 - max(0, t - 0.78) * 3.2)
        spine.append((cx - hw * 0.48, y))
        belly.append((cx + max(0, bell), y))
    tip = (cx - hw * 0.10, tip_y)
    body = spine + [tip] + list(reversed(belly))
    _vgrad_poly(surf, body, STEEL_HI, STEEL_DK, outline=(26, 30, 38),
                ow=max(2, int(2.0 * ss)))
    # One bold fuller line near the spine + a lit back-edge (2 bold beats).
    pygame.draw.line(surf, STEEL_MD, (cx - hw * 0.30, base_y - int(8 * ss)),
                     (cx - hw * 0.18, tip_y + int(span * 0.22)), max(2, int(2.2 * ss)))
    pygame.draw.line(surf, (220, 228, 240), (cx - hw * 0.48, base_y),
                     (cx - hw * 0.10, tip_y + int(4 * ss)), max(2, int(2.0 * ss)))
    # Simple straight iron cross.
    _crossguard(surf, cx, gy, ghw, int(10 * ss), IRON_MD, ss, dk=IRON_DK,
                quillon_r=0.35)
    # Plain leather grip.
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.36), LEATHER, ss)
    # Flat iron DISC pommel.
    _disc_pommel(surf, cx, py, int(hw * 0.46), IRON_MD, ss, dk=IRON_DK)


# ---- 6. Basket-Hilt Saber ---------------------------------------------------
# A curved cavalry SABER with a woven steel BASKET guard wrapping the hand, a
# wire-RIBBED grip, a teardrop steel pommel. The guard is the signature.
def sword_06(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 0.92)
    ghw = _guard_hw(ss)
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.30, edge=0.18)
    _vgrad_poly(surf, body, STEEL_HI, STEEL_DK, outline=(26, 30, 38),
                ow=max(2, int(2.0 * ss)))
    span = base_y - tip_y
    edge = [(cx + 0.30 * hw * (t ** 1.3) + hw * (1.0 - t * 0.9), base_y - span * t)
            for t in (0.05, 0.4, 0.7, 0.95)]
    pygame.draw.lines(surf, (224, 232, 244), False, edge, max(2, int(2.0 * ss)))
    # The woven steel BASKET guard: a domed cage of bold curved bars wrapping the
    # grip from the crossbar down to the pommel. Kept to a few BOLD ribs (de-noise).
    pygame.draw.line(surf, IRON_DK, (cx - ghw, gy), (cx + ghw, gy), max(2, int(3 * ss)))
    cage_top, cage_bot = gy - int(2 * ss), gbot
    for sgn in (-1, 1):
        outer = pygame.Rect(int(cx - ghw if sgn < 0 else cx),
                            int(cage_top), int(ghw), int(cage_bot - cage_top))
        for k, col in ((0, IRON_DK), (1, IRON_MD)):
            r = outer.inflate(-int(k * 3 * ss), -int(k * 3 * ss))
            pygame.draw.arc(surf, col, r,
                            (math.pi * 1.5 if sgn < 0 else math.pi),
                            (math.tau if sgn < 0 else math.pi * 1.5),
                            max(2, int(3 * ss - k * ss)))
        # Two cross-ribs spanning the cage so it reads woven, not a single hoop.
        for t in (0.34, 0.66):
            ay = cage_top + (cage_bot - cage_top) * t
            ax = cx + sgn * ghw * (1.0 - t * 0.5)
            pygame.draw.line(surf, IRON_MD, (cx, ay), (ax, ay - int(3 * ss)),
                             max(1, int(1.8 * ss)))
    # Wire-RIBBED grip behind the basket.
    _ribbed_grip(surf, cx, gy + int(6 * ss), gbot, int(hw * 0.30), STEEL_MD, ss)
    # Teardrop steel pommel cap.
    pr = int(hw * 0.40)
    pygame.draw.polygon(surf, IRON_DK,
                        [(cx, py - pr), (cx + pr, py + pr * 0.3), (cx, py + pr),
                         (cx - pr, py + pr * 0.3)])
    pygame.draw.polygon(surf, IRON_MD,
                        [(cx, py - pr + ss), (cx + pr - ss, py + pr * 0.3), (cx, py + pr - ss),
                         (cx - pr + ss, py + pr * 0.3)])
    pygame.draw.circle(surf, IRON_HI, (int(cx - pr * 0.3), int(py - pr * 0.2)),
                       max(1, int(pr * 0.24)))


# ---- 7. Leaf-Blade Shortsword -----------------------------------------------
# A bronze-age LEAF blade: a wide leaf-shaped silhouette swelling mid-blade to a
# point, a small flared bronze guard, a riveted bronze grip, a crescent pommel.
def sword_07(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.06)
    ghw = int(_guard_hw(ss) * 0.78)
    span = base_y - tip_y
    # Leaf silhouette: narrow at the base, swelling to a wide belly ~60% up, then
    # a graceful taper to a hard point.
    left, right = [], []
    n = 14
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        leaf = math.sin(min(1, t * 1.04) * math.pi) ** 0.7
        w = hw * (0.34 + 0.72 * leaf)
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + [(cx, tip_y)] + list(reversed(right))
    # Tip-dark gradient so the gap-facing tip stays dark (GATE 1/2); the warm
    # bronze sheen lives on the raised midrib, not the broad body fill.
    _vgrad_poly(surf, body, BRONZE_LO, BRONZE_MD, outline=(48, 30, 14),
                ow=max(2, int(2.0 * ss)))
    # A bold raised midrib down the centre to a hard apex (the leaf's spine).
    pygame.draw.polygon(surf, BRONZE_HI,
                        [(cx - hw * 0.12, base_y), (cx, tip_y + int(6 * ss)),
                         (cx + hw * 0.12, base_y)])
    pygame.draw.line(surf, (230, 196, 120), (cx, base_y - int(8 * ss)),
                     (cx, tip_y + int(10 * ss)), max(1, int(1.4 * ss)))
    # Small flared bronze guard (a shallow crescent hugging the leaf base).
    pygame.draw.arc(surf, BRONZE_MD, (int(cx - ghw), int(gy - 9 * ss),
                                      int(ghw * 2), int(20 * ss)),
                    math.pi, math.tau, max(3, int(4 * ss)))
    pygame.draw.line(surf, BRONZE_LO, (cx - ghw, gy + int(2 * ss)),
                     (cx + ghw, gy + int(2 * ss)), max(2, int(2.4 * ss)))
    # Riveted bronze grip (two bold rivets).
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.34), BRONZE_LO, ss)
    for t in (0.3, 0.7):
        _rivet(surf, cx, gy + int(8 * ss) + (gbot - gy - int(8 * ss)) * t,
               int(hw * 0.14), BRONZE_HI)
    # Crescent bronze pommel cap.
    pr = int(hw * 0.44)
    pygame.draw.arc(surf, BRONZE_LO, (int(cx - pr), int(py - pr), int(pr * 2), int(pr * 2)),
                    math.pi * 0.1, math.pi * 0.9, max(3, int(5 * ss)))
    pygame.draw.circle(surf, BRONZE_MD, (cx, int(py - pr * 0.2)), int(pr * 0.5))
    pygame.draw.circle(surf, BRONZE_HI, (int(cx - pr * 0.2), int(py - pr * 0.4)),
                       max(1, int(pr * 0.22)))


# ---- 8. Two-Hand War-Blade --------------------------------------------------
# A long double-edge GREATSWORD: a long ricasso, parrying SIDE-RINGS above the
# guard, a long two-hand wrapped grip, a heavy pear pommel. Reads as the big
# longsword family, distinct from the other three.
def sword_08(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss, hilt_px=156)
    hw = int(_blade_hw(ss) * 0.96)
    ghw = _guard_hw(ss)
    span = base_y - tip_y
    # Long slender double-edge blade with a long ricasso (parallel near the base).
    ric = base_y - int(span * 0.14)
    body = [(cx - hw, base_y), (cx - hw, ric),
            (cx - hw * 1.02, base_y - span * 0.5), (cx, tip_y),
            (cx + hw * 1.02, base_y - span * 0.5), (cx + hw, ric),
            (cx + hw, base_y)]
    _vgrad_poly(surf, body, STEEL_HI, STEEL_DK, outline=(24, 28, 36),
                ow=max(2, int(2.0 * ss)))
    # Long central fuller groove + bright edges (2 bold beats).
    pygame.draw.line(surf, STEEL_MD, (cx, ric - int(4 * ss)),
                     (cx, tip_y + int(span * 0.30)), max(2, int(2.4 * ss)))
    pygame.draw.line(surf, (220, 228, 240), (cx - hw, ric),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, (220, 228, 240), (cx + hw, ric),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    # Parrying SIDE-RINGS above the straight guard (the longsword signature).
    for sgn in (-1, 1):
        rcx = cx + sgn * int(hw * 0.7)
        pygame.draw.circle(surf, IRON_DK, (rcx, gy - int(10 * ss)), int(8 * ss),
                           max(2, int(2.6 * ss)))
        pygame.draw.circle(surf, IRON_MD, (rcx, gy - int(10 * ss)), int(8 * ss),
                           max(1, int(1.4 * ss)))
    # Long straight steel cross.
    _crossguard(surf, cx, gy, ghw, int(9 * ss), IRON_MD, ss, dk=IRON_DK,
                quillon_r=0.4)
    # Long two-hand wrapped grip with a centre knot ring.
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.32), LEATHER_DK, ss, diag=True)
    midg = (gy + gbot) / 2
    pygame.draw.line(surf, IRON_MD, (cx - hw * 0.34, midg), (cx + hw * 0.34, midg),
                     max(2, int(2.4 * ss)))
    # Heavy pear pommel.
    pr = int(hw * 0.46)
    pygame.draw.polygon(surf, IRON_DK,
                        [(cx, py - pr * 1.1), (cx + pr, py), (cx, py + pr),
                         (cx - pr, py)])
    pygame.draw.polygon(surf, IRON_MD,
                        [(cx, py - pr * 1.1 + ss), (cx + pr - ss, py), (cx, py + pr - ss),
                         (cx - pr + ss, py)])
    pygame.draw.circle(surf, IRON_HI, (int(cx - pr * 0.3), int(py - pr * 0.3)),
                       max(1, int(pr * 0.24)))


# ════════════════════════════════════════════════════════════════════════════
#  FANTASY REGISTER — 4 dramatic hero/boss weapons
# ════════════════════════════════════════════════════════════════════════════

# ---- 9. Winged-Guard Relic --------------------------------------------------
# A gold hero relic: a gem-CORE blade, a swept golden WING crossguard (feathered
# wings sweeping up toward the blade), a CROWN pommel. Holy-loot.
GREL_LO = (70, 48, 16)
GREL_MD = (132, 100, 40)
GREL_HI = (224, 188, 96)
SAPPHIRE = (66, 120, 220)
SAPPHIRE_HI = (160, 200, 255)
SAPPHIRE_DK = (28, 56, 130)


def sword_09(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.03)
    _vgrad_poly(surf, body, GREL_HI, GREL_LO, outline=GOLD_SHADOW,
                ow=max(2, int(2.0 * ss)))
    span = base_y - tip_y
    # A sapphire GEM-CORE channel running up the blade to a hard apex.
    pygame.draw.polygon(surf, SAPPHIRE_DK,
                        [(cx - bwid * 0.18, base_y - int(6 * ss)),
                         (cx, tip_y + int(14 * ss)),
                         (cx + bwid * 0.18, base_y - int(6 * ss))])
    pygame.draw.polygon(surf, SAPPHIRE,
                        [(cx - bwid * 0.1, base_y - int(8 * ss)),
                         (cx, tip_y + int(20 * ss)),
                         (cx + bwid * 0.1, base_y - int(8 * ss))])
    pygame.draw.line(surf, GOLD_HI, (cx - bwid, base_y), (cx, tip_y + int(4 * ss)),
                     max(1, int(1.6 * ss)))
    pygame.draw.line(surf, GOLD_HI, (cx + bwid, base_y), (cx, tip_y + int(4 * ss)),
                     max(1, int(1.6 * ss)))
    # Swept golden WING crossguard: two feathered wings sweeping UP toward the
    # blade. A few BOLD feather lobes per wing (de-noised), gold with dark keylines.
    for sgn in (-1, 1):
        base = (cx + sgn * int(8 * ss), gy + int(2 * ss))
        wing = [base,
                (cx + sgn * ghw * 0.55, gy - int(6 * ss)),
                (cx + sgn * ghw, gy - int(14 * ss)),
                (cx + sgn * ghw * 0.92, gy + int(2 * ss)),
                (cx + sgn * ghw * 0.6, gy + int(8 * ss)),
                (cx + sgn * int(8 * ss), gy + int(10 * ss))]
        pygame.draw.polygon(surf, GREL_MD, wing)
        pygame.draw.polygon(surf, GOLD_DK, wing, max(2, int(2 * ss)))
        for k in (0.45, 0.7, 0.92):
            fx = cx + sgn * ghw * k
            pygame.draw.line(surf, GOLD_HI, (fx, gy - int(2 * ss)),
                             (fx, gy - int(10 * ss) * (k)), max(1, int(1.6 * ss)))
    # Gold wrapped grip.
    _wrap_grip(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.36), GREL_MD, ss)
    # CROWN pommel: a ring of gold points crowning the base, a gem set in front.
    pr = int(hw * 0.5)
    pygame.draw.circle(surf, GOLD_DK, (cx, py), pr)
    pygame.draw.circle(surf, GOLD, (cx, py), int(pr - ss))
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.5
        bx = cx + math.cos(a) * pr
        by2 = py + math.sin(a) * pr
        pygame.draw.polygon(surf, GOLD,
                            [(bx - int(3 * ss), by2), (bx + int(3 * ss), by2),
                             (bx + math.cos(a) * int(7 * ss),
                              by2 + math.sin(a) * int(7 * ss))])
        pygame.draw.polygon(surf, GOLD_DK,
                            [(bx - int(3 * ss), by2), (bx + int(3 * ss), by2),
                             (bx + math.cos(a) * int(7 * ss),
                              by2 + math.sin(a) * int(7 * ss))], max(1, int(ss)))
    _facet_gem(surf, cx, py + int(2 * ss), int(pr * 0.5), SAPPHIRE, SAPPHIRE_HI,
               SAPPHIRE_DK, ss)


# ---- 10. Rune Greatsword ----------------------------------------------------
# A dark forged greatsword with ONE bold glowing RUNE in the fuller, an angular
# anvil guard, a charcoal ribbed grip, a faceted gem pommel. Brooding boss steel.
RUNE_BODY_HI = (78, 84, 102)
RUNE_BODY_LO = (26, 28, 38)
RUNE_GLOW = (120, 220, 255)
RUNE_HOT = (220, 248, 255)


def sword_10(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss, hilt_px=148)
    hw = int(_blade_hw(ss) * 1.08)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.04)
    _vgrad_poly(surf, body, RUNE_BODY_HI, RUNE_BODY_LO, outline=(12, 14, 20),
                ow=max(2, int(2.2 * ss)))
    span = base_y - tip_y
    # ONE bold SOLID glowing rune locked to the lower-mid fuller — a single filled
    # diamond sigil, no inner detail, so it reads as one clean glyph at route scale.
    ry = base_y - int(span * 0.36)
    gr = int(11 * ss)
    glyph = [(cx, ry - gr), (cx + gr * 0.62, ry), (cx, ry + gr), (cx - gr * 0.62, ry)]
    _glow_disc(surf, cx, ry, int(gr * 1.5), RUNE_GLOW, ss, alpha=170)
    pygame.draw.polygon(surf, RUNE_GLOW, glyph)
    pygame.draw.polygon(surf, RUNE_HOT, glyph, max(2, int(2.2 * ss)))
    # A thin cool edge-light to a hard apex.
    pygame.draw.line(surf, (150, 170, 200), (cx - bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, (150, 170, 200), (cx + bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    # Angular ANVIL guard: a hard chevron block with down-swept tips.
    guard = [(cx - ghw, gy - int(2 * ss)), (cx + ghw, gy - int(2 * ss)),
             (cx + ghw * 0.6, gy + int(13 * ss)), (cx + int(5 * ss), gy + int(6 * ss)),
             (cx - int(5 * ss), gy + int(6 * ss)), (cx - ghw * 0.6, gy + int(13 * ss))]
    pygame.draw.polygon(surf, (54, 58, 70), guard)
    pygame.draw.polygon(surf, (16, 18, 26), guard, max(2, int(2.2 * ss)))
    pygame.draw.line(surf, (96, 102, 120), (cx - ghw + int(3 * ss), gy),
                     (cx + ghw - int(3 * ss), gy), max(1, int(1.8 * ss)))
    # Charcoal ribbed grip.
    _ribbed_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.32), (44, 46, 58), ss)
    # Faceted glowing gem pommel.
    pr = int(hw * 0.46)
    pygame.draw.polygon(surf, (20, 22, 30),
                        [(cx, py - pr), (cx + pr, py), (cx, py + pr), (cx - pr, py)])
    _facet_gem(surf, cx, py, int(pr * 0.6), RUNE_GLOW, RUNE_HOT, (30, 80, 110), ss)


# ---- 11. Crystal Saber ------------------------------------------------------
# An opaque dark-CRYSTAL curved saber: a faceted amethyst blade, a JAGGED raw
# natural-crystal guard, a candy-twist-free shard grip, a raw-gem cluster pommel.
XTAL_CORE = (34, 22, 56)
XTAL_A = (120, 70, 200)
XTAL_B = (78, 48, 150)
XTAL_HI = (210, 180, 255)
XTAL_DK = (18, 12, 32)


def sword_11(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.22, edge=0.22)
    _vgrad_poly(surf, body, XTAL_A, XTAL_CORE, outline=XTAL_DK,
                ow=max(2, int(2.0 * ss)))
    span = base_y - tip_y
    # Big angular crystal facets stacked up the blade (alternating two tones).
    cuts = [0.0, 0.34, 0.62, 1.0]
    tones = [XTAL_B, XTAL_A, XTAL_B]
    for i in range(len(cuts) - 1):
        y0 = base_y - span * cuts[i]
        y1 = base_y - span * cuts[i + 1]
        cx0 = cx + 0.22 * hw * (cuts[i] ** 1.3)
        cx1 = cx + 0.22 * hw * (cuts[i + 1] ** 1.3)
        w0 = hw * (1.0 - cuts[i] * 0.9)
        w1 = hw * (1.0 - cuts[i + 1] * 0.9)
        pygame.draw.polygon(surf, _shade_c(tones[i], -24),
                            [(cx0 - w0 * 0.4, y0), (cx0 + w0, y0),
                             (cx1 + w1, y1), (cx1 - w1 * 0.4, y1)])
        pygame.draw.line(surf, XTAL_HI, (cx0 - w0 * 0.4, y0), (cx1 - w1 * 0.4, y1),
                         max(1, int(1.6 * ss)))
    # A bright crystalline ridge to a hard apex.
    pygame.draw.line(surf, (255, 255, 255), (cx + 0.22 * hw, tip_y + int(3 * ss)),
                     (cx + hw * 0.1, base_y - int(8 * ss)), max(2, int(2.0 * ss)))
    # JAGGED raw-crystal guard: a cluster of angular shards instead of a bar.
    for sgn in (-1, 1):
        shard = [(cx + sgn * int(6 * ss), gy + int(8 * ss)),
                 (cx + sgn * ghw * 0.5, gy - int(6 * ss)),
                 (cx + sgn * ghw, gy + int(2 * ss)),
                 (cx + sgn * ghw * 0.7, gy + int(12 * ss))]
        pygame.draw.polygon(surf, XTAL_B, shard)
        pygame.draw.polygon(surf, XTAL_DK, shard, max(2, int(2 * ss)))
        pygame.draw.line(surf, XTAL_HI, (cx + sgn * ghw * 0.5, gy - int(6 * ss)),
                         (cx + sgn * ghw * 0.6, gy + int(10 * ss)), max(1, int(1.6 * ss)))
    # Dark shard grip.
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.32), (40, 28, 60), ss)
    # Raw-gem cluster pommel.
    pr = int(hw * 0.46)
    _glow_disc(surf, cx, py, int(pr * 1.1), XTAL_A, ss, alpha=110)
    for (dx, dy, rr) in ((0, 0, 0.9), (-0.5, 0.3, 0.5), (0.5, 0.35, 0.5),
                         (0, -0.5, 0.45)):
        gx, gy2 = cx + dx * pr, py + dy * pr
        pygame.draw.polygon(surf, XTAL_A,
                            [(gx, gy2 - pr * rr), (gx + pr * rr * 0.7, gy2),
                             (gx, gy2 + pr * rr), (gx - pr * rr * 0.7, gy2)])
        pygame.draw.polygon(surf, XTAL_DK,
                            [(gx, gy2 - pr * rr), (gx + pr * rr * 0.7, gy2),
                             (gx, gy2 + pr * rr), (gx - pr * rr * 0.7, gy2)],
                            max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, (255, 255, 255), (int(cx - pr * 0.2), int(py - pr * 0.2)),
                       max(1, int(pr * 0.18)))


# ─────────────────────────────────────────────────────────────────────────────
#  CRYSTAL-SABER VARIANTS (round-7 maturation of sword_11)
#  Five DISTINCT amethyst-family blades. They share the opaque dark-crystal
#  language (so the body luma stays well below the 140 gate — round-6 measured
#  44.6) but each varies curvature, facet stacking, guard form, pommel cluster
#  and palette TEMPERATURE along a cool-violet → warm-magenta → icy-blue ramp.
#  Per-variant XTAL ramps (CORE deep/opaque, A mid, B shade, HI bright glint,
#  DK keyline) so the gap-facing TIP stays a hard dark→bright break (GATE 1).
# ─────────────────────────────────────────────────────────────────────────────

def _xtal_facets(surf, cx, tip_y, base_y, hw, cuts, tones, hi, *, lean=0.22, ss=1,
                 body=None, outline=None, ow=2):
    """Stack angular crystal facets up a curved blade — the shared faceting core
    the variants tune (cut count, tones, lateral lean). A bright crystalline ridge
    runs to the apex so the tip reads as a hard lit edge against the gap.

    The facets are strictly INTERNAL shading: every outer (cutting-edge-side)
    vertex is pulled a couple of px INSIDE the body boundary so the faceting never
    touches or steps the silhouette — at route scale a facet landing on the edge
    rasterises into a notched/stepped outline, which reads as a broken (not sharp)
    blade. To guarantee one clean razor edge the caller passes the body polygon +
    its outline colour so the body's continuous outline is re-stroked LAST, on top
    of the facets, restoring a single smooth dark→bright break to the fine tip."""
    span = base_y - tip_y
    # Outer vertices are scaled in AND pulled a margin inside the edge so the
    # faceting stays internal regardless of how far the body belly swells. The
    # margin is keyed to BLADE WIDTH (not just SS px) so the gap survives the
    # downscale to ~30-40px route width — a few SS px of inset collapses to a
    # sub-pixel after smoothscale and re-steps the silhouette.
    edge_in = max(2.0 * ss, hw * 0.14)
    for i in range(len(cuts) - 1):
        y0 = base_y - span * cuts[i]
        y1 = base_y - span * cuts[i + 1]
        cx0 = cx + lean * hw * (cuts[i] ** 1.3)
        cx1 = cx + lean * hw * (cuts[i + 1] ** 1.3)
        w0 = hw * (1.0 - cuts[i] * 0.9)
        w1 = hw * (1.0 - cuts[i + 1] * 0.9)
        ow0 = max(0.0, w0 * 0.78 - edge_in)
        ow1 = max(0.0, w1 * 0.78 - edge_in)
        pygame.draw.polygon(surf, _shade_c(tones[i % len(tones)], -24),
                            [(cx0 - w0 * 0.4, y0), (cx0 + ow0, y0),
                             (cx1 + ow1, y1), (cx1 - w1 * 0.4, y1)])
        pygame.draw.line(surf, hi, (cx0 - w0 * 0.4, y0), (cx1 - w1 * 0.4, y1),
                         max(1, int(1.6 * ss)))
    pygame.draw.line(surf, (255, 255, 255), (cx + lean * hw, tip_y + int(3 * ss)),
                     (cx + hw * 0.1, base_y - int(8 * ss)), max(2, int(2.0 * ss)))
    # Re-stroke the body's clean outer outline LAST so the silhouette is a single
    # continuous edge converging to the fine sharp tip, not the facet steps.
    if body is not None and outline is not None:
        pygame.draw.polygon(surf, outline, body, max(1, ow))


def _gem_cluster(surf, cx, py, pr, core, dk, hi, ss, gems):
    """A raw-gem pommel cluster: a glow halo, then a set of diamond facets at the
    given (dx, dy, r-scale) offsets, capped with a hot glint. The opaque dark
    keyline keeps the cluster reading as a dark mass on day-blue."""
    _glow_disc(surf, cx, py, int(pr * 1.1), core, ss, alpha=110)
    for (dx, dy, rr) in gems:
        gx, gy2 = cx + dx * pr, py + dy * pr
        pygame.draw.polygon(surf, core,
                            [(gx, gy2 - pr * rr), (gx + pr * rr * 0.7, gy2),
                             (gx, gy2 + pr * rr), (gx - pr * rr * 0.7, gy2)])
        pygame.draw.polygon(surf, dk,
                            [(gx, gy2 - pr * rr), (gx + pr * rr * 0.7, gy2),
                             (gx, gy2 + pr * rr), (gx - pr * rr * 0.7, gy2)],
                            max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, hi, (int(cx - pr * 0.2), int(py - pr * 0.2)),
                       max(1, int(pr * 0.18)))


# ---- 11a. Amethyst Saber (cool violet, deep belly) --------------------------
# The base amethyst tuned WARMER-cool: a deeper-bellied sweep (edge 0.34) and a
# four-shard fanned guard so it reads richer than the round-6 base.
A_CORE, A_A, A_B, A_HI, A_DK = (38, 22, 64), (132, 74, 214), (86, 50, 162), (216, 188, 255), (18, 12, 34)


def sword_11a(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    # A gentler belly (edge 0.26) keeps the cutting edge a single smooth arc rather
    # than a bulging belly that reads wavy beside the internal facets at route scale.
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.20, edge=0.26)
    ow = max(2, int(2.0 * ss))
    _vgrad_poly(surf, body, A_A, A_CORE, outline=A_DK, ow=ow)
    _xtal_facets(surf, cx, tip_y, base_y, hw, [0.0, 0.28, 0.52, 0.78, 1.0],
                 [A_B, A_A, A_B, A_A], A_HI, lean=0.20, ss=ss,
                 body=body, outline=A_DK, ow=ow)
    # Four-shard FANNED guard (more angular spread than the round-6 two-shard).
    for sgn in (-1, 1):
        for k, sc in ((0.55, 0.7), (1.0, 1.0)):
            shard = [(cx + sgn * int(5 * ss), gy + int(9 * ss)),
                     (cx + sgn * ghw * 0.5 * sc, gy - int(7 * ss) * sc),
                     (cx + sgn * ghw * sc, gy + int(2 * ss)),
                     (cx + sgn * ghw * 0.7 * sc, gy + int(12 * ss))]
            pygame.draw.polygon(surf, A_B, shard)
            pygame.draw.polygon(surf, A_DK, shard, max(2, int(2 * ss)))
        pygame.draw.line(surf, A_HI, (cx + sgn * ghw * 0.5, gy - int(7 * ss)),
                         (cx + sgn * ghw * 0.6, gy + int(10 * ss)), max(1, int(1.6 * ss)))
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.32), (44, 30, 66), ss)
    pr = int(hw * 0.48)
    _gem_cluster(surf, cx, py, pr, A_A, A_DK, (255, 255, 255), ss,
                 ((0, 0, 0.95), (-0.55, 0.3, 0.5), (0.55, 0.35, 0.5), (0, -0.55, 0.45)))


# ---- 11b. Magenta Tanto (warm magenta, near-straight broad facets) ----------
# A short, broad, near-straight crystal blade (bow ~0, shallow belly) with FEW
# big bold facets — the chunkiest, warmest variant; a flat slab pommel gem.
B_CORE, B_A, B_B, B_HI, B_DK = (52, 16, 50), (196, 60, 168), (140, 40, 120), (255, 196, 240), (28, 8, 26)


def sword_11b(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.12)        # broader slab
    ghw = _guard_hw(ss)
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.04, edge=0.12)
    _vgrad_poly(surf, body, B_A, B_CORE, outline=B_DK, ow=max(2, int(2.2 * ss)))
    # Few BIG facets (3) so the slab stays bold, not fizzy, at route scale.
    _xtal_facets(surf, cx, tip_y, base_y, hw, [0.0, 0.40, 0.72, 1.0],
                 [B_B, B_A, B_B], B_HI, lean=0.06, ss=ss)
    # A solid crystalline CROSS-shard guard: one wide low bar of two fused shards.
    bar = [(cx - ghw, gy + int(3 * ss)), (cx - ghw * 0.4, gy - int(8 * ss)),
           (cx + ghw * 0.4, gy - int(8 * ss)), (cx + ghw, gy + int(3 * ss)),
           (cx + ghw * 0.5, gy + int(12 * ss)), (cx - ghw * 0.5, gy + int(12 * ss))]
    pygame.draw.polygon(surf, B_B, bar)
    pygame.draw.polygon(surf, B_DK, bar, max(2, int(2.2 * ss)))
    pygame.draw.line(surf, B_HI, (cx - ghw * 0.4, gy - int(8 * ss)),
                     (cx + ghw * 0.4, gy - int(8 * ss)), max(1, int(1.8 * ss)))
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.30), (54, 18, 50), ss)
    # Flat slab gem pommel (single big faceted lozenge, no cluster).
    pr = int(hw * 0.46)
    _glow_disc(surf, cx, py, int(pr * 1.1), B_A, ss, alpha=110)
    slab = [(cx, py - pr), (cx + pr * 0.8, py - pr * 0.2),
            (cx + pr * 0.55, py + pr), (cx - pr * 0.55, py + pr),
            (cx - pr * 0.8, py - pr * 0.2)]
    pygame.draw.polygon(surf, B_A, slab)
    pygame.draw.polygon(surf, B_DK, slab, max(2, int(2 * ss)))
    pygame.draw.line(surf, B_HI, (cx, py - pr), (cx - pr * 0.55, py + pr),
                     max(1, int(1.6 * ss)))


# ---- 11c. Glacier Saber (icy blue, deep recurve) ----------------------------
# An icy-blue crystal with a strong RECURVE (high bow), many thin stacked facets
# climbing the long sweep, a spiky three-shard guard, an iceberg shard pommel.
C_CORE, C_A, C_B, C_HI, C_DK = (16, 36, 64), (74, 150, 224), (44, 100, 180), (200, 236, 255), (10, 20, 40)


def sword_11c(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 0.98)
    ghw = _guard_hw(ss)
    # A calmer recurve (bow 0.26) so the long edge stays one smooth sweep; the high
    # bow plus a thin facet stack used to step the silhouette into a wavy edge.
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.26, edge=0.14)
    ow = max(2, int(2.0 * ss))
    # Body keyed off the MID tone so the icy-blue fill clears the 140 luma gate;
    # the bright C_A / white ridge stays on the facet edges only.
    _vgrad_poly(surf, body, C_B, C_CORE, outline=C_DK, ow=ow)
    # Many thin INTERNAL facets so the long recurve glints like a glacier shard
    # without breaking the clean edge; lean trimmed to keep them inside the body.
    _xtal_facets(surf, cx, tip_y, base_y, hw,
                 [0.0, 0.18, 0.34, 0.50, 0.66, 0.82, 1.0],
                 [C_B, C_A], C_HI, lean=0.24, ss=ss,
                 body=body, outline=C_DK, ow=ow)
    # Bias the BELLY-side internal shading one step deeper so the recurve registers
    # as a curve at route scale: a translucent dark strip hugging the cutting-edge
    # side, INSET well inside the silhouette (margin keyed to blade width) so it
    # never touches the clean outer edge the facets just re-stroked. Deepest at the
    # mid-belly where the recurve bows most, fading to the tip and base.
    span_c = base_y - tip_y
    margin = max(2.0 * ss, hw * 0.16)
    inner, outer_in = [], []
    n = 14
    for i in range(n + 1):
        t = i / n
        y = base_y - span_c * t
        arc = math.sin(t * math.pi)
        cxt = cx + 0.26 * hw * (t ** 1.3)
        bwt = hw * (1.0 - t * 0.92) + 0.14 * hw * 0.5 * arc * (1 - t * 0.4)
        belly_x = cxt + bwt - margin
        inner.append((belly_x - hw * 0.30, y))
        outer_in.append((belly_x, y))
    strip = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(strip, _shade_c(C_CORE, -16) + (150,),
                        inner + list(reversed(outer_in)))
    surf.blit(strip, (0, 0))
    # Three upright spike shards (a frosty crown guard).
    for sgn, sc in ((-1, 1.0), (0, 0.6), (1, 1.0)):
        bx = cx + sgn * ghw * 0.7
        shard = [(bx - int(5 * ss), gy + int(10 * ss)),
                 (bx, gy - int(12 * ss) * sc),
                 (bx + int(5 * ss), gy + int(10 * ss))]
        pygame.draw.polygon(surf, C_B, shard)
        pygame.draw.polygon(surf, C_DK, shard, max(2, int(2 * ss)))
        pygame.draw.line(surf, C_HI, (bx, gy - int(12 * ss) * sc),
                         (bx - int(4 * ss), gy + int(8 * ss)), max(1, int(1.4 * ss)))
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.32), (24, 40, 64), ss)
    # Iceberg pommel: one big jagged shard pointing down.
    pr = int(hw * 0.5)
    _glow_disc(surf, cx, py, int(pr * 1.15), C_A, ss, alpha=110)
    berg = [(cx - pr * 0.7, py - pr * 0.6), (cx + pr * 0.7, py - pr * 0.5),
            (cx + pr * 0.3, py + pr * 1.1), (cx - pr * 0.2, py + pr * 0.7),
            (cx - pr * 0.6, py + pr * 0.3)]
    pygame.draw.polygon(surf, C_A, berg)
    pygame.draw.polygon(surf, C_DK, berg, max(2, int(2 * ss)))
    pygame.draw.line(surf, C_HI, (cx - pr * 0.7, py - pr * 0.6),
                     (cx + pr * 0.3, py + pr * 1.1), max(1, int(1.6 * ss)))


# ---- 11d. Rose-Quartz Khopesh (warm pink, hooked sickle) --------------------
# A warm rose-quartz blade with an exaggerated HOOK/sickle bow and a SWELLED
# belly, a single fat triangular guard shard, a twin-gem pommel — the most
# silhouette-distinct of the saber set (a curved hook reads instantly at scale).
D_CORE, D_A, D_B, D_HI, D_DK = (60, 24, 44), (224, 118, 158), (170, 78, 116), (255, 214, 230), (32, 12, 24)


def sword_11d(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.06)
    ghw = _guard_hw(ss)
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.52, edge=0.40)
    # Body keyed off the MID tone (not the bright lit tone) so the warm-pink broad
    # fill stays well below the 140 luma gate; D_A lives on the facet glints only.
    _vgrad_poly(surf, body, D_B, D_CORE, outline=D_DK, ow=max(2, int(2.2 * ss)))
    _xtal_facets(surf, cx, tip_y, base_y, hw, [0.0, 0.30, 0.58, 0.82, 1.0],
                 [D_B, D_A, D_B, D_A], D_HI, lean=0.50, ss=ss)
    # One fat angular guard shard sweeping toward the hook side.
    shard = [(cx - ghw * 0.5, gy + int(10 * ss)),
             (cx - ghw * 0.2, gy - int(8 * ss)),
             (cx + ghw, gy - int(2 * ss)),
             (cx + ghw * 0.7, gy + int(13 * ss))]
    pygame.draw.polygon(surf, D_B, shard)
    pygame.draw.polygon(surf, D_DK, shard, max(2, int(2.2 * ss)))
    pygame.draw.line(surf, D_HI, (cx - ghw * 0.2, gy - int(8 * ss)),
                     (cx + ghw, gy - int(2 * ss)), max(1, int(1.8 * ss)))
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.32), (62, 26, 46), ss)
    pr = int(hw * 0.46)
    _gem_cluster(surf, cx, py, pr, D_A, D_DK, (255, 255, 255), ss,
                 ((-0.35, -0.1, 0.7), (0.35, 0.25, 0.7)))


# ---- 11e. Twilight Estoc (deep violet-indigo, narrow needle, gem-stack) -----
# A long NARROW thrusting needle in the deepest violet-indigo, with a tall stack
# of small chevron facets and a vertical TRIPLE-gem stacked pommel — the darkest,
# most regal variant; the slim profile contrasts the broad tanto.
E_CORE, E_A, E_B, E_HI, E_DK = (26, 18, 58), (96, 78, 196), (60, 48, 140), (190, 178, 252), (14, 10, 30)


def sword_11e(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 0.82)        # narrow needle
    ghw = _guard_hw(ss)
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.10, edge=0.06)
    ow = max(2, int(2.0 * ss))
    _vgrad_poly(surf, body, E_A, E_CORE, outline=E_DK, ow=ow)
    _xtal_facets(surf, cx, tip_y, base_y, hw,
                 [0.0, 0.16, 0.32, 0.48, 0.64, 0.80, 1.0],
                 [E_B, E_A], E_HI, lean=0.10, ss=ss,
                 body=body, outline=E_DK, ow=ow)
    # A low diamond guard (two flat shards meeting in a point each side).
    for sgn in (-1, 1):
        shard = [(cx + sgn * int(3 * ss), gy - int(2 * ss)),
                 (cx + sgn * ghw, gy + int(2 * ss)),
                 (cx + sgn * int(4 * ss), gy + int(11 * ss))]
        pygame.draw.polygon(surf, E_B, shard)
        pygame.draw.polygon(surf, E_DK, shard, max(2, int(2 * ss)))
    pygame.draw.line(surf, E_HI, (cx - ghw, gy + int(2 * ss)),
                     (cx + ghw, gy + int(2 * ss)), max(1, int(1.6 * ss)))
    _wrap_grip(surf, cx, gy + int(11 * ss), gbot - int(10 * ss), int(hw * 0.36), (32, 24, 64), ss)
    # Vertical TRIPLE-gem stacked pommel down from the grip.
    pr = int(hw * 0.5)
    _glow_disc(surf, cx, py, int(pr * 1.0), E_A, ss, alpha=110)
    for k, dy in enumerate((-0.7, 0.1, 0.9)):
        rr = (0.55, 0.85, 0.55)[k]
        gy2 = py + dy * pr
        pygame.draw.polygon(surf, E_A,
                            [(cx, gy2 - pr * rr), (cx + pr * rr * 0.7, gy2),
                             (cx, gy2 + pr * rr), (cx - pr * rr * 0.7, gy2)])
        pygame.draw.polygon(surf, E_DK,
                            [(cx, gy2 - pr * rr), (cx + pr * rr * 0.7, gy2),
                             (cx, gy2 + pr * rr), (cx - pr * rr * 0.7, gy2)],
                            max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - pr * 0.2), int(py - pr * 0.9)), max(1, int(pr * 0.16)))


# ---- 11f. Prism Greatcrystal (teal-cyan, double-edge SYMMETRIC longsword) ---
# A FRESH silhouette for the saber line: not a curved single-edge body like the
# other four, but a broad DOUBLE-EDGED symmetric crystal longsword — a straight
# faceted slab tapering on BOTH edges to one hard central apex, so the tip stays
# the single dark→bright break at the gap (GATE 1). The signature is a WINGED /
# BRANCHING cross-guard: the crossbar flares up into two swept crystal WINGS (a
# guard architecture not used by 11a-e, which are all shard-fans / spikes / fused
# slabs). A teal-cyan temperature sits between the icy Glacier and violet
# Amethyst. Body keyed dark (CORE/MID fill) so the broad slab clears the 140 gate.
F_CORE, F_A, F_B, F_HI, F_DK = (16, 50, 56), (64, 196, 196), (40, 124, 132), (196, 248, 248), (8, 26, 30)


def sword_11f(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss, hilt_px=150)
    hw = int(_blade_hw(ss) * 1.0)
    ghw = _guard_hw(ss)
    span = base_y - tip_y
    # SYMMETRIC double-edge crystal slab: both edges taper evenly to one apex, a
    # mid-blade shoulder so it reads as a broad faceted greatsword, not a saber.
    left, right = [], []
    n = 12
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        # A gentle double-bevel: full width low, a soft shoulder, hard taper to tip.
        w = hw * (1.0 - 0.12 * math.sin(t * math.pi) - t * 0.86)
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + [(cx, tip_y)] + list(reversed(right))
    _vgrad_poly(surf, body, F_B, F_CORE, outline=F_DK, ow=max(2, int(2.2 * ss)))
    # A bold symmetric chevron facet stack down the centreline (no lateral lean —
    # the double-edge read) climbing to a hot crystalline apex ridge.
    for t in (0.16, 0.40, 0.64, 0.86):
        y = base_y - span * t
        w = hw * (1.0 - 0.12 * math.sin(t * math.pi) - t * 0.86)
        pygame.draw.line(surf, F_HI, (cx - w, y), (cx, y - int(7 * ss)),
                         max(1, int(1.6 * ss)))
        pygame.draw.line(surf, F_HI, (cx + w, y), (cx, y - int(7 * ss)),
                         max(1, int(1.6 * ss)))
    pygame.draw.line(surf, (255, 255, 255), (cx, tip_y + int(3 * ss)),
                     (cx, base_y - int(10 * ss)), max(2, int(2.0 * ss)))
    # WINGED / BRANCHING guard: a low crossbar that BRANCHES into two crystal wings
    # sweeping UP toward the blade — two bold elements, dark-keyed + lit ridges.
    pygame.draw.line(surf, F_DK, (cx - ghw, gy + int(2 * ss)),
                     (cx + ghw, gy + int(2 * ss)), max(2, int(3 * ss)))
    for sgn in (-1, 1):
        wing = [(cx + sgn * int(4 * ss), gy + int(6 * ss)),
                (cx + sgn * ghw * 0.55, gy - int(16 * ss)),
                (cx + sgn * ghw, gy - int(6 * ss)),
                (cx + sgn * ghw * 0.78, gy + int(9 * ss))]
        pygame.draw.polygon(surf, F_B, wing)
        pygame.draw.polygon(surf, F_DK, wing, max(2, int(2.2 * ss)))
        pygame.draw.line(surf, F_HI, (cx + sgn * int(4 * ss), gy + int(6 * ss)),
                         (cx + sgn * ghw * 0.55, gy - int(16 * ss)), max(1, int(1.8 * ss)))
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.32), (20, 44, 50), ss)
    # A faceted octahedron pommel (single bold lit gem, distinct from the clusters).
    pr = int(hw * 0.48)
    _glow_disc(surf, cx, py, int(pr * 1.1), F_A, ss, alpha=110)
    oct_pts = [(cx, py - pr), (cx + pr * 0.72, py - pr * 0.18),
               (cx + pr * 0.5, py + pr * 0.9), (cx - pr * 0.5, py + pr * 0.9),
               (cx - pr * 0.72, py - pr * 0.18)]
    pygame.draw.polygon(surf, F_A, oct_pts)
    pygame.draw.polygon(surf, F_DK, oct_pts, max(2, int(2 * ss)))
    pygame.draw.line(surf, F_HI, (cx, py - pr), (cx - pr * 0.5, py + pr * 0.9),
                     max(1, int(1.6 * ss)))
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - pr * 0.24), int(py - pr * 0.32)), max(1, int(pr * 0.16)))


# ---- 11g. Geode Glaive (wine-violet, broad LEAF blade, pommel-heavy geode) --
# The SECOND fresh direction, maximising silhouette variety: a broad LEAF-shaped
# crystal glaive — a body that swells to a wide belly mid-blade then tapers to a
# single hard apex (distinct from every curved single-edge saber AND the narrow
# Estoc needle). The weight sits at the BASE: a pommel-heavy ceremonial GEODE — a
# big rounded crust cracked open to a pocket of small bright crystals (a cluster
# pommel form not used by 11a-e). A deep wine-violet keeps the broad leaf body
# dark on day-blue (GATE 2) while the geode pocket carries the brightest beat.
G_CORE, G_A, G_B, G_HI, G_DK = (44, 16, 56), (150, 64, 188), (100, 44, 132), (224, 184, 248), (22, 8, 30)


def sword_11g(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.14)        # broad leaf belly
    ghw = int(_guard_hw(ss) * 0.84)
    span = base_y - tip_y
    # LEAF silhouette: narrow base, a wide belly ~55% up, graceful taper to a hard
    # apex (the gap-facing dark→bright break, GATE 1). Symmetric, so it reads as a
    # leaf-glaive head rather than a curved saber.
    left, right = [], []
    n = 14
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        leaf = math.sin(min(1, t * 1.02) * math.pi) ** 0.72
        w = hw * (0.30 + 0.78 * leaf)
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + [(cx, tip_y)] + list(reversed(right))
    _vgrad_poly(surf, body, G_B, G_CORE, outline=G_DK, ow=max(2, int(2.2 * ss)))
    # A bold raised crystal midrib to the apex + a pair of lit veins (2-3 beats).
    pygame.draw.polygon(surf, G_B,
                        [(cx - hw * 0.14, base_y), (cx, tip_y + int(6 * ss)),
                         (cx + hw * 0.14, base_y)])
    pygame.draw.line(surf, (255, 255, 255), (cx, base_y - int(8 * ss)),
                     (cx, tip_y + int(8 * ss)), max(2, int(2.0 * ss)))
    for sgn in (-1, 1):
        pygame.draw.line(surf, G_HI,
                         (cx, base_y - span * 0.5),
                         (cx + sgn * hw * 0.62, base_y - span * 0.34),
                         max(1, int(1.6 * ss)))
    # A short flared crystal collar guard (low, so the eye reads the heavy pommel).
    collar = [(cx - ghw, gy + int(4 * ss)), (cx - ghw * 0.4, gy - int(6 * ss)),
              (cx + ghw * 0.4, gy - int(6 * ss)), (cx + ghw, gy + int(4 * ss)),
              (cx + ghw * 0.5, gy + int(11 * ss)), (cx - ghw * 0.5, gy + int(11 * ss))]
    pygame.draw.polygon(surf, G_B, collar)
    pygame.draw.polygon(surf, G_DK, collar, max(2, int(2.2 * ss)))
    pygame.draw.line(surf, G_HI, (cx - ghw * 0.4, gy - int(6 * ss)),
                     (cx + ghw * 0.4, gy - int(6 * ss)), max(1, int(1.8 * ss)))
    _wrap_grip(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.30), (40, 18, 52), ss)
    # POMMEL-HEAVY GEODE: a big rounded dark crust cracked open to a bright pocket
    # of small crystals — the ceremonial signature, the visual weight at the base.
    pr = int(hw * 0.66)
    _glow_disc(surf, cx, py, int(pr * 1.15), G_A, ss, alpha=120)
    pygame.draw.circle(surf, G_DK, (cx, int(py)), pr)
    pygame.draw.circle(surf, G_CORE, (cx, int(py)), pr - int(2 * ss))
    # The cracked-open pocket: a bright inner cup, then a fan of small crystals.
    pocket = [(cx - pr * 0.62, py - pr * 0.2), (cx, py - pr * 0.66),
              (cx + pr * 0.62, py - pr * 0.2), (cx + pr * 0.4, py + pr * 0.5),
              (cx - pr * 0.4, py + pr * 0.5)]
    pygame.draw.polygon(surf, G_B, pocket)
    pygame.draw.polygon(surf, G_DK, pocket, max(1, int(1.8 * ss)))
    for dx in (-0.34, 0.0, 0.34):
        gx = cx + dx * pr
        cluster = [(gx, py - pr * 0.5), (gx + pr * 0.18, py + pr * 0.18),
                   (gx - pr * 0.18, py + pr * 0.18)]
        pygame.draw.polygon(surf, G_A, cluster)
        pygame.draw.polygon(surf, G_HI, cluster, max(1, int(ss)))
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - pr * 0.18), int(py - pr * 0.34)), max(1, int(pr * 0.16)))


# ─────────────────────────────────────────────────────────────────────────────
#  CRYSTAL-SABER — TWO FRESH DIRECTIONS (round-8 saber-only browse)
#  Both stay in the faceted opaque-dark crystal language (body keyed off the
#  MID/CORE tones so the median luma clears the 140 day-sky gate) and keep a hard
#  dark→bright TIP terminus for route gap-readability. They explore silhouettes +
#  guard architectures NOT used by 11a-g: a SAWTOOTH cutting edge (11h) and a
#  closed RING / HALO guard (11i) — neither a shard-fan, spike-crown, fused slab,
#  wing, collar nor geode. 2-3 bold beats each, no fizz at route scale.
# ─────────────────────────────────────────────────────────────────────────────

# ---- 11h. Obsidian Cleaver (smoky charcoal-violet, clean broad cleaver edge) --
# A single-edge crystal CLEAVER with a clean broad swept cutting edge sweeping to
# one hard apex (de-serrated: the old sawtooth read as a broken edge at route
# scale; a sharp cleaver keeps the identity without the notches). The guard is a
# round knuckle-DISC plate (a flat pierced crystal disc — a guard form distinct
# from the shard-fans / spikes / wings / rings), the pommel a heavy faceted ANVIL
# wedge. Smoky charcoal-violet keeps it the darkest, moodiest of the set.
H_CORE, H_A, H_B, H_HI, H_DK = (28, 22, 40), (118, 96, 150), (74, 60, 104), (198, 184, 224), (14, 10, 22)


def sword_11h(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.06)
    ghw = _guard_hw(ss)
    span = base_y - tip_y
    # A broad single-edge cleaver: a calm belly (edge 0.22) sweeping to one hard
    # apex so the outer silhouette is a SINGLE smooth sharp edge, not a row of
    # teeth that rasterised into notches at route scale.
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.16, edge=0.22)
    ow = max(2, int(2.2 * ss))
    _vgrad_poly(surf, body, H_B, H_CORE, outline=H_DK, ow=ow)
    # Internal-only crystal facets (outer vertices inset inside the body boundary)
    # so the cleaver glints like cut glass without stepping the sharp edge; the
    # body outline is re-stroked LAST to keep one clean break to the fine tip.
    _xtal_facets(surf, cx, tip_y, base_y, hw, [0.0, 0.30, 0.56, 0.80, 1.0],
                 [H_B, H_A, H_B, H_A], H_HI, lean=0.16, ss=ss,
                 body=body, outline=H_DK, ow=ow)
    # A dark fuller groove + a bright lit ridge to the apex (the 2 internal beats);
    # the ridge keeps the tip a hard lit edge against the gap (GATE 1).
    pygame.draw.line(surf, H_CORE, (cx - hw * 0.06, base_y - int(8 * ss)),
                     (cx + hw * 0.02, tip_y + int(span * 0.22)), max(2, int(2.4 * ss)))
    # Round knuckle-DISC guard: a flat pierced crystal plate edge-on (a squat
    # faceted oval) — a guard architecture not used by the other variants.
    rect = pygame.Rect(int(cx - ghw), int(gy - 9 * ss), int(ghw * 2), int(18 * ss))
    pygame.draw.ellipse(surf, H_B, rect)
    pygame.draw.ellipse(surf, H_DK, rect, max(2, int(2.2 * ss)))
    pygame.draw.line(surf, H_HI, (cx - ghw + int(4 * ss), gy - int(3 * ss)),
                     (cx + ghw - int(4 * ss), gy - int(3 * ss)), max(1, int(1.8 * ss)))
    pygame.draw.circle(surf, H_CORE, (cx, int(gy)), max(2, int(4 * ss)))   # pierced eye
    _wrap_grip(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.32), (36, 28, 52), ss)
    # Heavy faceted ANVIL wedge pommel (a broad flat-bottomed crystal block, not a
    # cluster or single gem) — the dark weight at the base.
    pr = int(hw * 0.52)
    _glow_disc(surf, cx, py, int(pr * 1.05), H_A, ss, alpha=100)
    anvil = [(cx - pr * 0.5, py - pr), (cx + pr * 0.5, py - pr),
             (cx + pr, py + pr * 0.3), (cx + pr * 0.7, py + pr),
             (cx - pr * 0.7, py + pr), (cx - pr, py + pr * 0.3)]
    pygame.draw.polygon(surf, H_A, anvil)
    pygame.draw.polygon(surf, H_DK, anvil, max(2, int(2 * ss)))
    pygame.draw.line(surf, H_HI, (cx - pr * 0.5, py - pr), (cx - pr, py + pr * 0.3),
                     max(1, int(1.6 * ss)))
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - pr * 0.2), int(py - pr * 0.4)), max(1, int(pr * 0.16)))


# ---- 11i. Halo Reliquary (amber-gold violet, straight blade, RING/HALO guard) -
# A slim STRAIGHT ceremonial crystal blade (no curve, no belly — distinct from the
# curved sabers, the recurve and the broad bodies) rising to one hard apex. The
# signature is a CLOSED crystalline RING / HALO encircling the base of the blade —
# a guard architecture none of 11a-g use (all are open shards / spikes / wings /
# collars). The pommel echoes it as a smaller pierced RING. A warm amber-gold core
# warmed against the cool violet facets gives the set its one regal-warm member;
# the body stays keyed dark so the slim blade still clears the 140 gate.
# Body warmed ~25% in value and shifted toward gold so the BLADE ITSELF reads
# amber-gold at route scale (not the brown/charcoal of the prior round): the
# whole body gradient is warmed ~25% in value and pushed toward gold so even the
# lower core reads warm amber rather than brown — the gradient top (I_B) is a lit
# amber and the core (I_CORE) a lifted warm gold (no longer a near-black bronze).
# The deeper crystalline RING rim (I_DK + I_VIO) stays the cooler/darker accent so
# the ring still contrasts the gold body. Median body luma still clears the <140
# day-sky gate with headroom (the renderer prints the figure).
I_CORE, I_A, I_B, I_HI, I_DK = (108, 76, 34), (236, 184, 104), (214, 164, 82), (255, 236, 184), (28, 16, 10)
I_VIO = (120, 86, 168)


def sword_11i(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 0.9)         # slim straight ceremonial blade
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.02)
    _vgrad_poly(surf, body, I_B, I_CORE, outline=I_DK, ow=max(2, int(2.0 * ss)))
    # A bold symmetric chevron facet stack down the centreline to a hot apex ridge
    # (the straight-blade read, no lateral lean) — 2-3 bold beats.
    span = base_y - tip_y
    for t in (0.20, 0.48, 0.76):
        y = base_y - span * t
        w = hw * (1.0 - t * 0.92)
        pygame.draw.line(surf, I_HI, (cx - w, y), (cx, y - int(7 * ss)),
                         max(1, int(1.6 * ss)))
        pygame.draw.line(surf, I_HI, (cx + w, y), (cx, y - int(7 * ss)),
                         max(1, int(1.6 * ss)))
    pygame.draw.line(surf, (255, 255, 255), (cx, tip_y + int(3 * ss)),
                     (cx, base_y - int(10 * ss)), max(2, int(2.0 * ss)))
    # CLOSED crystalline RING / HALO guard SEATED at the blade base — drawn as an
    # outer + inner ring so the sky reads THROUGH its eye, the ring itself a hard
    # dark mass with a violet inner facet rim. The ring is sized as a base GUARD
    # (not a column-filling hoop) and its CENTRE is pushed below the blade base so
    # its top rim just meets the base while its bulk sits toward the grip: the
    # straight blade then rises CLEAN above the ring, so when the shared blade flip
    # plants the TIP on the ground the long blade reads as the body and the ring +
    # grip + pommel lift UP to the hand — matching the other four sabers' guards
    # (which seat at the base and never engulf the blade).
    halo_r = int(ghw * 0.66)
    halo_cy = int(gy + halo_r * 0.42)
    ring_w = int(6 * ss)
    pygame.draw.circle(surf, I_DK, (cx, halo_cy), halo_r)
    pygame.draw.circle(surf, I_A, (cx, halo_cy), halo_r - int(1.5 * ss))
    pygame.draw.circle(surf, I_VIO, (cx, halo_cy), halo_r - ring_w)
    pygame.draw.circle(surf, I_DK, (cx, halo_cy), halo_r - ring_w, max(2, int(2 * ss)))
    # A few bold facet keylines spoking the halo so it reads cut, not a flat hoop.
    for k in range(6):
        a = k * math.tau / 6 - math.pi / 2
        x0 = cx + math.cos(a) * (halo_r - ring_w)
        y0 = halo_cy + math.sin(a) * (halo_r - ring_w)
        x1 = cx + math.cos(a) * halo_r
        y1 = halo_cy + math.sin(a) * halo_r
        pygame.draw.line(surf, I_DK, (x0, y0), (x1, y1), max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, I_HI, (int(cx - halo_r * 0.4), int(halo_cy - halo_r * 0.4)),
                       max(2, int(halo_r * 0.18)))
    _wrap_grip(surf, cx, halo_cy + int(halo_r * 0.7), gbot, int(hw * 0.34), (46, 30, 24), ss)
    # Pierced RING pommel echoing the halo (a smaller open ring, not a gem/cluster).
    pr = int(hw * 0.5)
    _glow_disc(surf, cx, py, int(pr * 1.05), I_A, ss, alpha=100)
    pygame.draw.circle(surf, I_DK, (cx, int(py)), pr)
    pygame.draw.circle(surf, I_A, (cx, int(py)), pr - int(1.5 * ss))
    pygame.draw.circle(surf, I_CORE, (cx, int(py)), int(pr * 0.42))
    pygame.draw.circle(surf, I_DK, (cx, int(py)), int(pr * 0.42), max(1, int(1.6 * ss)))
    pygame.draw.circle(surf, (255, 255, 255),
                       (int(cx - pr * 0.4), int(py - pr * 0.4)), max(1, int(pr * 0.16)))


# ---- 12. Bone / Demon Blade -------------------------------------------------
# A carved BONE blade with a fanged DEMON-SKULL guard, a VERTEBRA grip, a HORNED
# skull pommel. The monstrous boss weapon — pure bone, no metal.
# Bone keyed so the blade BODY (the lower core of the gradient) sits dark on
# day-blue (GATE 2); the pale ivory lives on the spine highlight + the skull/grip
# furniture, not the broad blade fill.
# Body keyed ~12% deeper than round 6 (it measured 133.8, closest to the 140 gate)
# so it keeps clear margin below 140 against the bright day sky; the skull guard +
# ivory spine sliver still carry the pale read.
DEMON_BONE_HI = (150, 141, 117)
DEMON_BONE_LO = (64, 57, 42)
DEMON_BONE_KEY = (36, 30, 21)
DEMON_RED = (200, 40, 44)
DEMON_HOT = (255, 120, 80)


def sword_12(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.06)
    ghw = _guard_hw(ss)
    span = base_y - tip_y
    # Carved bone blade: a serrated/clawed single-edge silhouette to a hard hook
    # point — but kept BOLD (few big serrations) so it doesn't fizz at route scale.
    back, edge = [], []
    n = 6
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        back.append((cx - hw * (0.5 - t * 0.4), y))
    # a few big claw serrations on the cutting edge
    serr = [(cx + hw, base_y), (cx + hw * 0.9, base_y - span * 0.18),
            (cx + hw * 1.0, base_y - span * 0.30), (cx + hw * 0.7, base_y - span * 0.46),
            (cx + hw * 0.82, base_y - span * 0.58), (cx + hw * 0.5, base_y - span * 0.74),
            (cx + hw * 0.55, base_y - span * 0.84)]
    body = back + [(cx + hw * 0.1, tip_y)] + list(reversed(serr))
    # Tip-dark gradient: the gap-facing tip end is the DARK key so the dark-body→
    # bright-gap break stays hard (GATE 1) and the body luma clears day-blue.
    _vgrad_poly(surf, body, DEMON_BONE_LO, DEMON_BONE_HI, outline=DEMON_BONE_KEY,
                ow=max(2, int(2.2 * ss)))
    # A dark marrow groove down the bone (the single bold body accent).
    pygame.draw.line(surf, DEMON_BONE_KEY, (cx - hw * 0.05, base_y - int(8 * ss)),
                     (cx + hw * 0.06, tip_y + int(span * 0.2)), max(2, int(2.4 * ss)))
    # A THIN ivory back-spine sliver (kept slim so the body stays dark on blue).
    pygame.draw.line(surf, (224, 216, 192), (cx - hw * 0.5, base_y),
                     (cx + hw * 0.1, tip_y + int(4 * ss)), max(1, int(1.4 * ss)))
    # Fanged DEMON-SKULL guard: a wide bone skull the blade erupts from, two glowing
    # eyes, a row of big fangs, swept horns at the ends.
    sk_w = ghw
    sk_h = int(20 * ss)
    skull = [(cx - sk_w, gy - int(2 * ss)), (cx - sk_w * 0.5, gy - sk_h * 0.7),
             (cx + sk_w * 0.5, gy - sk_h * 0.7), (cx + sk_w, gy - int(2 * ss)),
             (cx + sk_w * 0.6, gy + sk_h * 0.7), (cx - sk_w * 0.6, gy + sk_h * 0.7)]
    pygame.draw.polygon(surf, DEMON_BONE_HI, skull)
    pygame.draw.polygon(surf, DEMON_BONE_KEY, skull, max(2, int(2.2 * ss)))
    # Swept horns at the guard ends.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, DEMON_BONE_LO,
                            [(cx + sgn * sk_w * 0.9, gy - int(2 * ss)),
                             (cx + sgn * sk_w * 1.05, gy - int(14 * ss)),
                             (cx + sgn * sk_w * 0.7, gy - int(4 * ss))])
        pygame.draw.polygon(surf, DEMON_BONE_KEY,
                            [(cx + sgn * sk_w * 0.9, gy - int(2 * ss)),
                             (cx + sgn * sk_w * 1.05, gy - int(14 * ss)),
                             (cx + sgn * sk_w * 0.7, gy - int(4 * ss))], max(1, int(ss)))
    # Glowing eyes.
    for sgn in (-1, 1):
        ex = cx + sgn * sk_w * 0.38
        _glow_disc(surf, ex, gy - int(2 * ss), int(5 * ss), DEMON_HOT, ss, alpha=150)
        pygame.draw.circle(surf, DEMON_RED, (int(ex), int(gy - 2 * ss)), int(4 * ss))
        pygame.draw.circle(surf, (20, 8, 8), (int(ex), int(gy - 2 * ss)), int(2 * ss))
    # A row of big fangs across the jaw.
    for i in range(4):
        t = (i + 0.5) / 4
        fx = cx - sk_w * 0.55 + sk_w * 1.1 * t
        pygame.draw.polygon(surf, (250, 244, 224),
                            [(fx - int(4 * ss), gy + sk_h * 0.4),
                             (fx + int(4 * ss), gy + sk_h * 0.4),
                             (fx, gy + sk_h * 0.4 + int(10 * ss))])
    # VERTEBRA grip (stacked bone segments).
    _bone_grip(surf, cx, gy + int(sk_h * 0.7), gbot, int(hw * 0.34), ss, vertebra=True)
    # HORNED skull pommel.
    pr = int(hw * 0.5)
    pygame.draw.circle(surf, DEMON_BONE_LO, (cx, py), pr)
    pygame.draw.circle(surf, DEMON_BONE_HI, (cx, int(py - ss)), int(pr - ss))
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, DEMON_BONE_LO,
                            [(cx + sgn * pr * 0.7, py - pr * 0.4),
                             (cx + sgn * pr * 1.3, py - pr * 1.0),
                             (cx + sgn * pr * 0.85, py - pr * 0.1)])
        pygame.draw.polygon(surf, DEMON_BONE_KEY,
                            [(cx + sgn * pr * 0.7, py - pr * 0.4),
                             (cx + sgn * pr * 1.3, py - pr * 1.0),
                             (cx + sgn * pr * 0.85, py - pr * 0.1)], max(1, int(ss)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, (20, 8, 8), (int(cx + sgn * pr * 0.4), int(py)),
                           max(2, int(pr * 0.22)))
    pygame.draw.polygon(surf, (20, 8, 8),
                        [(cx, py + pr * 0.3), (cx + int(3 * ss), py + pr * 0.7),
                         (cx - int(3 * ss), py + pr * 0.7)])


# ════════════════════════════════════════════════════════════════════════════
#  BROADENED ROUND-6 PROPS — STAFFS · CLOWN PROPS · MYSTIC
#  Every prop is authored TIP/FINIAL-UP in the box (gap-facing end at y=0, the
#  bottom resting end at the box bottom) so the existing route flip scaffolding
#  plants it point-UP from the ground and point-DOWN from the ceiling unchanged.
#  Bodies are keyed DARK (median luma < ~140 on the ~190 day sky): the shaft fill
#  is a dark core with only a SLIM lit rail, and finials carry the value break.
# ════════════════════════════════════════════════════════════════════════════

# Dark woods / staves that always hold value on day-blue.
WOOD_HI = (120, 92, 58)
WOOD_MD = (84, 62, 38)
WOOD_LO = (48, 34, 20)
WOOD_KEY = (30, 20, 12)
ROD_HI = (150, 158, 172)
ROD_MD = (78, 84, 96)
ROD_LO = (40, 44, 52)


def _shaft(surf, cx, top_y, bot_y, hw, ss, hi, md, lo, *, gnarl=0.0, key=None):
    """A vertical staff/cane SHAFT as a dark volume: a `lo`→`md` body gradient
    with a single SLIM lit rail down the lit side, so the body stays dark on the
    day sky while still reading round. `gnarl` waggles the silhouette into a
    knobbed wizard rod; 0 keeps it a clean straight cane."""
    key = key or _shade_c(lo, -40)
    span = max(1, bot_y - top_y)
    left, right = [], []
    n = 16
    for i in range(n + 1):
        t = i / n
        y = top_y + span * t
        wob = math.sin(t * math.pi * 3.0) * gnarl * hw
        left.append((cx - hw + wob, y))
        right.append((cx + hw + wob, y))
    body = left + list(reversed(right))
    _vgrad_poly(surf, body, md, lo, outline=key, ow=max(2, int(2.0 * ss)))
    # One slim lit rail down the lit (left) side — kept thin so the body luma
    # stays dark on day-blue.
    rail = [(p[0] + hw * 0.32, p[1]) for p in left]
    pygame.draw.lines(surf, hi, False, rail, max(1, int(1.6 * ss)))


def _bind_rings(surf, cx, ys, hw, ss, col):
    """A couple of bold binding rings around a shaft (a 2-3 bold-element accent)."""
    for y in ys:
        pygame.draw.line(surf, _shade_c(col, -40), (cx - hw - int(1.5 * ss), y),
                         (cx + hw + int(1.5 * ss), y), max(2, int(3 * ss)))
        pygame.draw.line(surf, _shade_c(col, 30), (cx - hw, y - int(ss)),
                         (cx + hw, y - int(ss)), max(1, int(1.4 * ss)))


# ════════════════════════════════════════════════════════════════════════════
#  FAMILY B — STAFFS & SCEPTERS (gap-facing FINIAL at box top)
# ════════════════════════════════════════════════════════════════════════════

# ---- 13. Wizard Orb Staff ---------------------------------------------------
# A gnarled dark rod with a glowing crystal ORB clutched in a claw finial. The
# orb's hard rim is the gap terminus: a dark claw frames a bright cyan core so
# the blunt round top still reads as a clean, contrast-y gap end.
ORB_CORE = (40, 120, 150)
ORB_GLOW = (120, 226, 245)
ORB_HOT = (224, 250, 255)


def prop_13(surf, bw, bh, ss):
    cx = bw // 2
    finial_r = int(15 * ss)
    fy = finial_r + int(8 * ss)            # orb centre sits just below the top
    shaft_top = fy + int(finial_r * 0.4)
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(7 * ss), ss,
           WOOD_HI, WOOD_MD, WOOD_LO, gnarl=0.10)
    _bind_rings(surf, cx, [bh * 0.55, bh * 0.8], int(7.5 * ss), ss, GOLD_DK)
    # Dark claw prongs cupping ONLY the orb's lower half — they stop at the orb
    # equator so the UPPER half of the sphere stays a smooth unbroken circle. That
    # clean round crown is the wizard staff's terminus cue (vs the marotte's two
    # ears and the skull's domed-jaw), the distinct SPHERE in the staff family.
    for sgn in (-1, 0, 1):
        bx = cx + sgn * finial_r * 0.7
        prong = [(cx + sgn * int(3 * ss), shaft_top + int(2 * ss)),
                 (bx, fy + finial_r * 0.55),
                 (bx + sgn * int(3 * ss), fy)]
        pygame.draw.lines(surf, WOOD_LO, False, prong, max(3, int(4 * ss)))
        pygame.draw.lines(surf, WOOD_KEY, False, prong, max(1, int(1.4 * ss)))
    # The glowing orb finial — a dark rim, a saturated core, a hot glint.
    _glow_disc(surf, cx, fy, int(finial_r * 1.3), ORB_GLOW, ss, alpha=150)
    pygame.draw.circle(surf, (18, 36, 46), (cx, int(fy)), finial_r)
    pygame.draw.circle(surf, ORB_CORE, (cx, int(fy)), int(finial_r - ss))
    pygame.draw.circle(surf, ORB_GLOW, (cx, int(fy)), int(finial_r * 0.55))
    pygame.draw.circle(surf, ORB_HOT, (int(cx - finial_r * 0.3), int(fy - finial_r * 0.3)),
                       max(2, int(finial_r * 0.26)))


# ---- 14. Jester Marotte -----------------------------------------------------
# A fool's-head bauble SCEPTER: a plum rod topped by a belled jester head whose
# TWO splayed donkey-ear hood lobes break the round outline into a distinctly
# LOBED/EARED silhouette (NOT a circle) — that non-circular eared head is the
# gap terminus that sets the marotte apart from the orb / skull staffs at 1x.
def prop_14(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(11 * ss)                      # the central head shrunk so the EARS
    hy = int(26 * ss)                      # dominate the terminus silhouette
    shaft_top = hy + hr
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6 * ss), ss,
           _shade_c(PLUM, 40), PLUM, PLUM_DK)
    _bind_rings(surf, cx, [bh * 0.6], int(6.5 * ss), ss, GOLD_DK)
    # TWO big splayed hood lobes (donkey-ear jester hood) flaring far up-and-OUT
    # past the head circle so the terminus silhouette reads as two distinct EARS
    # breaking the round outline, never a ball — the cue that separates the marotte
    # from the orb SPHERE and skull DOME at 1x. Each lobe is a long horn ending in a
    # fat bell-nub knob (one plum, one lime) that bulges clearly outward.
    for sgn, col in ((-1, PLUM_DK), (1, LIME_DK)):
        ex = cx + sgn * int(22 * ss)       # bell-nub centre, far outside the head
        ey = int(8 * ss)                   # raised high so the ears tower over the head
        lobe = [(cx + sgn * int(2 * ss), hy - hr * 0.1),
                (cx + sgn * int(5 * ss), hy - hr * 1.1),
                (ex - sgn * int(6 * ss), ey + int(4 * ss)),
                (ex + sgn * int(6 * ss), ey + int(3 * ss)),
                (ex + sgn * int(4 * ss), ey - int(7 * ss)),
                (cx + sgn * int(10 * ss), hy - hr * 0.4)]
        pygame.draw.polygon(surf, col, lobe)
        pygame.draw.polygon(surf, _shade_c(col, -50), lobe, max(1, int(1.4 * ss)))
        # Bell-nub knob bulge at the lobe tip so the bump clearly rounds OUTWARD.
        pygame.draw.circle(surf, col, (int(ex), int(ey)), int(7 * ss))
        pygame.draw.circle(surf, _shade_c(col, -50), (int(ex), int(ey)), int(7 * ss),
                           max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, GOLD, (int(ex), int(ey - 4 * ss)), max(2, int(3.4 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(ex), int(ey - 4 * ss)), max(2, int(3.4 * ss)),
                           max(1, int(ss)))
    # The tiny fool's head (cream face) nested between the two lobes — bold + simple
    # so it reads at route scale; the lobes carry the non-circular silhouette.
    pygame.draw.circle(surf, _shade_c(CREAM, -50), (cx, int(hy)), hr)
    pygame.draw.circle(surf, CREAM, (cx, int(hy)), int(hr - ss))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (int(cx + sgn * hr * 0.4), int(hy - hr * 0.1)),
                           max(2, int(2.2 * ss)))
    pygame.draw.circle(surf, CANDY_RED, (cx, int(hy + hr * 0.2)), max(2, int(2.6 * ss)))
    pygame.draw.arc(surf, INK, (int(cx - hr * 0.5), int(hy + hr * 0.1),
                                int(hr), int(hr * 0.7)),
                    math.pi * 0.15, math.pi * 0.85, max(2, int(2 * ss)))


# ─────────────────────────────────────────────────────────────────────────────
#  JESTER-MAROTTE VARIANTS (round-7 maturation of prop_14)
#  Five DISTINCT fool's-head baubles. They keep the plum shaft + cream fool's
#  head + non-circular lobed terminus (the gap-break cue that separates the
#  marotte from the orb/skull staffs at route scale — round-6 luma 62.1), but
#  vary lobe spread/COUNT (2 vs 3), bell-nub styling/size, face expression,
#  and shaft binds. ONE variant (prop_14e) crowns the bauble with a mini version
#  of the CLOWN's own four-point cap, so it reads as a tiny clown bauble.
# ─────────────────────────────────────────────────────────────────────────────

def _marotte_face(surf, cx, hy, hr, ss, *, mouth="smile"):
    """The tiny cream fool's-head face shared by the marotte variants. `mouth`
    swaps the expression: a smile arc, an open 'O', or a sly tongue-out grin."""
    pygame.draw.circle(surf, _shade_c(CREAM, -50), (cx, int(hy)), hr)
    pygame.draw.circle(surf, CREAM, (cx, int(hy)), int(hr - ss))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (int(cx + sgn * hr * 0.4), int(hy - hr * 0.1)),
                           max(2, int(2.2 * ss)))
    pygame.draw.circle(surf, CANDY_RED, (cx, int(hy + hr * 0.2)), max(2, int(2.6 * ss)))
    if mouth == "smile":
        pygame.draw.arc(surf, INK, (int(cx - hr * 0.5), int(hy + hr * 0.1),
                                    int(hr), int(hr * 0.7)),
                        math.pi * 0.15, math.pi * 0.85, max(2, int(2 * ss)))
    elif mouth == "open":
        pygame.draw.circle(surf, INK, (cx, int(hy + hr * 0.5)), max(2, int(hr * 0.3)))
    elif mouth == "tongue":
        pygame.draw.arc(surf, INK, (int(cx - hr * 0.5), int(hy + hr * 0.1),
                                    int(hr), int(hr * 0.7)),
                        math.pi * 0.05, math.pi * 0.95, max(2, int(2 * ss)))
        pygame.draw.circle(surf, CANDY_RED, (int(cx + hr * 0.2), int(hy + hr * 0.55)),
                           max(2, int(hr * 0.22)))


def _bell_lobe(surf, cx, hy, hr, sgn, ex, ey, col, ss, *, nub=7):
    """One splayed donkey-ear hood lobe ending in a fat bell-nub knob, shared by
    the marotte variants. `ex,ey` is the nub centre; `nub` scales the knob."""
    lobe = [(cx + sgn * int(2 * ss), hy - hr * 0.1),
            (cx + sgn * int(5 * ss), hy - hr * 1.1),
            (ex - sgn * int(6 * ss), ey + int(4 * ss)),
            (ex + sgn * int(6 * ss), ey + int(3 * ss)),
            (ex + sgn * int(4 * ss), ey - int(7 * ss)),
            (cx + sgn * int(10 * ss), hy - hr * 0.4)]
    pygame.draw.polygon(surf, col, lobe)
    pygame.draw.polygon(surf, _shade_c(col, -50), lobe, max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, col, (int(ex), int(ey)), int(nub * ss))
    pygame.draw.circle(surf, _shade_c(col, -50), (int(ex), int(ey)), int(nub * ss),
                       max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, GOLD, (int(ex), int(ey - 4 * ss)), max(2, int(3.4 * ss)))
    pygame.draw.circle(surf, GOLD_DK, (int(ex), int(ey - 4 * ss)), max(2, int(3.4 * ss)),
                       max(1, int(ss)))


# ---- 14a. Marotte — Wide-Ear (round-6 silhouette, refined binds) ------------
# The two-lobe round-6 read kept, but with a smiling face and an extra plum bind
# ring so the shaft reads richer at hero scale.
def prop_14a(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(11 * ss)
    hy = int(26 * ss)
    shaft_top = hy + hr
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6 * ss), ss,
           _shade_c(PLUM, 40), PLUM, PLUM_DK)
    _bind_rings(surf, cx, [bh * 0.45, bh * 0.7], int(6.5 * ss), ss, GOLD_DK)
    for sgn, col in ((-1, PLUM_DK), (1, LIME_DK)):
        _bell_lobe(surf, cx, hy, hr, sgn, cx + sgn * int(22 * ss), int(8 * ss), col, ss)
    _marotte_face(surf, cx, hy, hr, ss, mouth="smile")


# ---- 14b. Marotte — Three-Ear Crown (3 lobes, open-mouth glee) --------------
# THREE lobes (left, top, right) so the terminus reads as a triple-eared fool's
# crown — a clearly different non-circular break from the two-ear base. Bigger
# bell-nubs; an open-O surprised face.
def prop_14b(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(10 * ss)
    hy = int(28 * ss)
    shaft_top = hy + hr
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6 * ss), ss,
           _shade_c(PLUM, 40), PLUM, PLUM_DK)
    _bind_rings(surf, cx, [bh * 0.6], int(6.5 * ss), ss, GOLD_DK)
    # Two splayed side lobes plus one tall central lobe spiking straight up.
    for sgn, col in ((-1, PLUM_DK), (1, LIME_DK)):
        _bell_lobe(surf, cx, hy, hr, sgn, cx + sgn * int(24 * ss), int(12 * ss),
                   col, ss, nub=8)
    centre = [(cx - int(5 * ss), hy - hr * 0.4), (cx - int(3 * ss), int(2 * ss)),
              (cx + int(3 * ss), int(2 * ss)), (cx + int(5 * ss), hy - hr * 0.4)]
    pygame.draw.polygon(surf, GOLD_DK, centre)
    pygame.draw.polygon(surf, _shade_c(GOLD_DK, -50), centre, max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, GOLD_DK, (cx, int(3 * ss)), int(7 * ss))
    pygame.draw.circle(surf, _shade_c(GOLD_DK, -50), (cx, int(3 * ss)), int(7 * ss),
                       max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, GOLD, (cx, int(2 * ss)), max(2, int(3.4 * ss)))
    _marotte_face(surf, cx, hy, hr, ss, mouth="open")


# ---- 14c. Marotte — Coxcomb Crest (single tall scalloped lobe) --------------
# A single ROOSTER-COMB crest: a tall scalloped lobe leaning to one side, the
# coxcomb fool's head. A sly tongue-out grin; the comb's scallops carry the
# non-circular break.
def prop_14c(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(11 * ss)
    hy = int(28 * ss)
    shaft_top = hy + hr
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6 * ss), ss,
           _shade_c(PLUM, 40), PLUM, PLUM_DK)
    _bind_rings(surf, cx, [bh * 0.5, bh * 0.75], int(6.5 * ss), ss, LIME_DK)
    # A scalloped coxcomb sweeping up-and-over: a bold filled crest with three
    # rounded scallop humps + bell tips, leaning right.
    comb = [(cx - int(8 * ss), hy - hr * 0.2),
            (cx - int(4 * ss), int(14 * ss)),
            (cx + int(4 * ss), int(4 * ss)),
            (cx + int(14 * ss), int(2 * ss)),
            (cx + int(20 * ss), int(10 * ss)),
            (cx + int(14 * ss), int(16 * ss)),
            (cx + int(8 * ss), hy - hr * 0.3)]
    pygame.draw.polygon(surf, PLUM_DK, comb)
    pygame.draw.polygon(surf, _shade_c(PLUM_DK, -50), comb, max(1, int(1.4 * ss)))
    for (bx, by) in ((cx - int(4 * ss), int(14 * ss)), (cx + int(14 * ss), int(2 * ss)),
                     (cx + int(20 * ss), int(10 * ss))):
        pygame.draw.circle(surf, GOLD, (int(bx), int(by)), max(2, int(3 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(bx), int(by)), max(2, int(3 * ss)),
                           max(1, int(ss)))
    _marotte_face(surf, cx, hy, hr, ss, mouth="tongue")


# ---- 14d. Marotte — Belled Spray (many small bells, fanned spray) -----------
# A FAN of four short stubby nubs spraying outward, each tipped with a small
# bell — a busier, jollier terminus than the two long ears, but kept bold (four
# fat lobes, no fizz). A wide smile.
def prop_14d(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(11 * ss)
    hy = int(26 * ss)
    shaft_top = hy + hr
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6 * ss), ss,
           _shade_c(PLUM, 40), PLUM, PLUM_DK)
    _bind_rings(surf, cx, [bh * 0.6], int(6.5 * ss), ss, GOLD_DK)
    spray = [(-26, 14, PLUM_DK), (-12, 4, LIME_DK), (12, 4, PLUM_DK), (26, 14, LIME_DK)]
    for (ox, oy, col) in spray:
        ex, ey = cx + int(ox * ss), int(oy * ss)
        sgn = 1 if ox >= 0 else -1
        stub = [(cx + sgn * int(2 * ss), hy - hr * 0.2),
                (cx + sgn * int(6 * ss), hy - hr * 0.9),
                (ex, ey + int(3 * ss)),
                (ex + sgn * int(2 * ss), ey - int(4 * ss)),
                (cx + sgn * int(9 * ss), hy - hr * 0.4)]
        pygame.draw.polygon(surf, col, stub)
        pygame.draw.polygon(surf, _shade_c(col, -50), stub, max(1, int(1.3 * ss)))
        pygame.draw.circle(surf, col, (int(ex), int(ey)), int(5 * ss))
        pygame.draw.circle(surf, _shade_c(col, -50), (int(ex), int(ey)), int(5 * ss),
                           max(1, int(1.2 * ss)))
        pygame.draw.circle(surf, GOLD, (int(ex), int(ey - 2 * ss)), max(2, int(3 * ss)))
    _marotte_face(surf, cx, hy, hr, ss, mouth="smile")


# ---- 14e. Marotte — Mini-Clown (the bauble wears the CLOWN's own cap) -------
# The bauble head is crowned with a SCALED-DOWN version of the hero clown's own
# four-point splayed cap (the same cap_four_point geometry from build_jester:
# plum/lime/gold points flopping out past the head, each bell-tipped), so the
# marotte reads as a tiny twin of the clown holding it. The face stays the cream
# fool's head; the cap supplies the non-circular gap-break terminus.
def prop_14e(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(11 * ss)
    hy = int(30 * ss)                       # head dropped so the cap towers above
    shaft_top = hy + hr
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6 * ss), ss,
           _shade_c(PLUM, 40), PLUM, PLUM_DK)
    _bind_rings(surf, cx, [bh * 0.6], int(6.5 * ss), ss, GOLD_DK)
    # The clown's cap, scaled to the bauble. Mirror cap_four_point's splayed
    # four-point fan (two outer points flopping far out + low, two inner points
    # leaning apart), each a triangle to a bell knob, in the clown's plum/lime/
    # gold. base_y sits at the head crown; offsets scale with ss.
    base_y = hy - hr + int(1 * ss)
    # The two OUTER points flop far out past the head and lift high; the two INNER
    # points lean apart — mirroring cap_four_point so nothing stands upright and
    # the terminus breaks the round head into a clearly four-pointed fool's cap.
    pts = [(-26, -8, PLUM_DK), (26, -6, PLUM_DK), (-11, -24, LIME_DK), (11, -22, GOLD_DK)]
    for (dx, dy, col) in pts:
        bx, by = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(7 * ss)
        tri = [(cx - span, base_y + int(2 * ss)), (cx + span, base_y + int(2 * ss)),
               (bx, by)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)),
                             (cx, base_y + int(2 * ss)), (bx, by)])
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        # Bell knob at the point tip.
        pygame.draw.circle(surf, GOLD, (int(bx), int(by)), max(2, int(3.2 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(bx), int(by)), max(2, int(3.2 * ss)),
                           max(1, int(ss)))
    _marotte_face(surf, cx, hy, hr, ss, mouth="smile")


# ═════════════════════════════════════════════════════════════════════════════
#  ROUND 9 — MINI-CLOWN MAROTTE CRAFT PASS (prop_14f … prop_14j)
#  Five fresh single-staff designs that pour all the attention into the STAFF
#  ITSELF: the bauble becomes a TRUE mini-clown (the hero clown's own happy-but-
#  mean grin + ruff, not the plain cream fool's head), and the shaft graduates
#  from one flat plum gradient to a per-design FANCY ornament. The existing
#  prop_14 / prop_14a-e are left untouched as the baseline.
#
#  COORDINATE SPACE: these draw funcs live in `_box` SS space (every offset *ss),
#  unlike the 1x clown-kit primitives. So the hero clown's `naughty_face` recipe
#  (eyes / sly brows / open toothy grin + fang / cheeks) and the scalloped ruff
#  are PORTED here in ss-scaled space, keyed off the head radius `hr`, so they
#  read crisp at the marotte's own scale instead of the clown's.
# ─────────────────────────────────────────────────────────────────────────────

# Warm clown-face inks ported from the hero recipe (render_jester_variants).
FACE_SHADOW = (212, 198, 168)          # cream head keyline / under-shade
EYE_WHITE = (252, 250, 244)
EYE_PUPIL = (44, 38, 60)
EYE_PUPIL_DK = (14, 12, 22)
BROW_COL = (76, 56, 60)                # soft warm brow (never heavy black)
NOSE_RED = (232, 72, 72)
MOUTH_THROAT = (120, 30, 42)
TEETH = (250, 248, 240)
LIP = (188, 56, 66)
TONGUE = (228, 110, 124)
CHEEK = (255, 150, 150)
DEAD_EYE = (196, 30, 44)               # the blank-stare "mean" variant's pinprick


def _mini_clown_face(surf, cx, hy, hr, ss, *, expr="grin", look=None):
    """The hero clown's HAPPY-but-MEAN expression ported into ss-scaled marotte
    space: a cream head, bright open eyes glancing sidelong, lifted SLY brows,
    a warm ball nose, and a wide upturned OPEN grin with a tooth row + one fang.
    `expr` flavours the mouth — "grin" (base), "tongue" (tongue-tip licking the
    corner), or "stare" (the dead-eyed, blank-stare 'mean' read). All geometry
    keys off `hr` so it scales with the bauble, never the clown's fixed 1x grid."""
    # `u` is the DIMENSIONLESS head scale vs the round-6 head (hr already carries
    # the ss factor), so `u * ss` below yields proper supersampled pixels — the
    # face never double-scales by ss.
    u = hr / (11.0 * ss)
    look = (-2.0 * u * ss) if look is None else look
    # Cream head with a soft under-shade keyline (the clown's round face).
    pygame.draw.circle(surf, FACE_SHADOW, (cx, int(hy)), hr)
    pygame.draw.circle(surf, CREAM, (cx, int(hy)), int(hr - ss))
    # Warm cheek flush low + outward on the apple so it reads charming, not a tear.
    for s in (-1, 1):
        blush = pygame.Surface((int(7 * u * ss), int(5 * u * ss)), pygame.SRCALPHA)
        pygame.draw.ellipse(blush, (*CHEEK, 120), blush.get_rect())
        surf.blit(blush, (int(cx + s * hr * 0.46 - 3.5 * u * ss),
                          int(hy + hr * 0.28)))
    ex = hr * 0.42                         # eye spacing
    ew, eh = 2.0 * u, 2.5 * u              # tall round OPEN eye (alive, not hooded)
    # "smirk" shares the dead pinprick eyes with "stare" but carries a sly raised
    # brow + a one-corner-up closed mouth so it reads as a mischievous clown, not an
    # empty doll. `dead` drives the eye treatment; the mouth branch splits below.
    smirk = expr == "smirk"
    stare = expr == "stare" or smirk
    for s in (-1, 1):
        exx = cx + s * ex
        # White sclera — a tall bright open eye.
        rect = pygame.Rect(int(exx - ew * ss), int(hy - eh * ss + ss),
                           int(ew * 2 * ss), int(eh * 2 * ss))
        pygame.draw.ellipse(surf, EYE_WHITE, rect)
        if stare:
            # The 'mean' read: tiny dead pinprick pupils dead-centre — a vacant,
            # unsettling stare instead of the gleeful sidelong glance.
            pygame.draw.circle(surf, DEAD_EYE, (int(exx), int(hy + ss)),
                               max(1, int(1.4 * u * ss)))
            pygame.draw.circle(surf, EYE_PUPIL_DK, (int(exx), int(hy + ss)),
                               max(1, int(1.4 * u * ss)), max(1, int(ss)))
        else:
            px = exx + look
            py = hy + 0.6 * u * ss
            pr = max(2, int(2.0 * u * ss))
            pygame.draw.circle(surf, EYE_PUPIL, (int(px), int(py)), pr)
            pygame.draw.circle(surf, EYE_PUPIL_DK, (int(px), int(py)), pr, max(1, int(ss)))
            pygame.draw.circle(surf, (255, 255, 255),
                               (int(px - 0.7 * u * ss), int(py - 1.0 * u * ss)),
                               max(1, int(0.7 * u * ss)))
        # Thin LIGHT upper lid arched UP (a happy lifted lid), never a hooded bar.
        pygame.draw.arc(surf, INK, (int(exx - ew * ss - ss), int(hy - eh * ss),
                                    int(ew * 2 * ss + 2 * ss), int(eh * ss + 2 * ss)),
                        math.pi * 0.15, math.pi * 0.85, max(1, int(1.4 * ss)))
        # SLY raised brow — inner (nose-side) end HIGH, outer end lower, bowed up
        # at the mid: a lifted "oh-really" arch that can never knit into the angry
        # inner-down V. Drawn as a thin 3-point polyline so it reads arched, not a
        # heavy flat bar.
        inner = (exx - s * 1.0 * u * ss, hy - 5.4 * u * ss)
        mid = (exx + s * 1.8 * u * ss, hy - 5.6 * u * ss)
        outer = (exx + s * 4.6 * u * ss, hy - 3.6 * u * ss)
        if stare and not smirk:
            # A flatter, lower brow for the blank-stare so the calm reads colder.
            inner = (exx - s * 1.0 * u * ss, hy - 4.6 * u * ss)
            mid = (exx + s * 1.8 * u * ss, hy - 4.6 * u * ss)
            outer = (exx + s * 4.6 * u * ss, hy - 4.4 * u * ss)
        elif smirk:
            # ONE sly raised brow (the die-side / LEFT, s == -1) cocks up high; the
            # other stays flat + low — a single cocked brow over dead eyes is the
            # whole "knowing menace-glee" tell of the sinister smirk.
            if s < 0:
                inner = (exx - s * 1.0 * u * ss, hy - 6.4 * u * ss)
                mid = (exx + s * 1.8 * u * ss, hy - 6.8 * u * ss)
                outer = (exx + s * 4.6 * u * ss, hy - 5.0 * u * ss)
            else:
                inner = (exx - s * 1.0 * u * ss, hy - 4.4 * u * ss)
                mid = (exx + s * 1.8 * u * ss, hy - 4.4 * u * ss)
                outer = (exx + s * 4.6 * u * ss, hy - 4.4 * u * ss)
        pygame.draw.lines(surf, BROW_COL, False,
                          [(int(inner[0]), int(inner[1])), (int(mid[0]), int(mid[1])),
                           (int(outer[0]), int(outer[1]))], max(1, int(1.3 * ss)))
    # Red ball nose, lifted up between the eyes so the grin owns the lower face.
    # Bumped up again so the warm dot is the last face cue to survive at 30px, where
    # the eyes/brows dissolve and only "warm nose over dark smile" reads — the dot
    # has to win the silhouette fight against the cap clutter above it.
    nr = max(3, int(3.0 * u * ss))
    pygame.draw.circle(surf, _shade_c(NOSE_RED, -60), (cx, int(hy + 1.4 * u * ss)), nr + 1)
    pygame.draw.circle(surf, NOSE_RED, (cx, int(hy + 1.4 * u * ss)), nr)
    pygame.draw.circle(surf, _shade_c(NOSE_RED, 100),
                       (int(cx - nr * 0.4), int(hy + 1.4 * u * ss - nr * 0.4)),
                       max(1, int(nr * 0.4)))
    if smirk:
        # A closed-mouth SMIRK: a smooth lip curve with the die-side (LEFT) corner
        # cocked UP and the other corner held low — a sliver of menace-glee so the
        # dead eyes read as a sly clown, not a vacant doll. A short dimple tick seats
        # the raised corner so the asymmetry survives shrinking.
        my = hy + 5.0 * u * ss
        l_up = (cx - 4.2 * u * ss, my - 1.8 * u * ss)
        r_lo = (cx + 4.2 * u * ss, my + 1.2 * u * ss)
        smk = []
        for k in range(11):
            t = k / 10.0
            sx = l_up[0] + (r_lo[0] - l_up[0]) * t
            sy = l_up[1] + (r_lo[1] - l_up[1]) * t + (1.0 - (2.0 * t - 1.0) ** 2) * 1.2 * u * ss
            smk.append((int(sx), int(sy)))
        pygame.draw.lines(surf, LIP, False, smk, max(2, int(2.2 * ss)))
        pygame.draw.line(surf, _shade_c(LIP, -40),
                         (int(l_up[0]), int(l_up[1])),
                         (int(l_up[0] + 1.2 * u * ss), int(l_up[1] - 1.6 * u * ss)),
                         max(1, int(1.4 * ss)))
        return
    if stare:
        # A small flat closed line-mouth for the unsettling calm — no toothy grin.
        my = hy + 5.4 * u * ss
        pygame.draw.line(surf, LIP, (int(cx - 4.0 * u * ss), int(my)),
                         (int(cx + 4.0 * u * ss), int(my)), max(2, int(2.0 * ss)))
        pygame.draw.line(surf, _shade_c(LIP, -30),
                         (int(cx - 2.0 * u * ss), int(my + 1.6 * u * ss)),
                         (int(cx + 2.0 * u * ss), int(my + 1.6 * u * ss)), max(1, int(ss)))
        return
    # THE DOMINANT FEATURE: a WIDE OPEN happy grin, die-side (LEFT) corner highest
    # so it stays lopsided/sly, with a tooth row + one pointed fang for the edge.
    mw = 5.0 * u * ss
    my = hy + 4.6 * u * ss
    l_corner = (cx - mw - 0.6 * u * ss, my - 1.0 * u * ss)
    r_corner = (cx + mw, my)
    bottom = (cx, my + 3.6 * u * ss)
    mouth = [l_corner, (cx - 2.3 * u * ss, my + 0.5 * u * ss),
             (cx + 2.3 * u * ss, my + 0.5 * u * ss), r_corner,
             (cx + 2.7 * u * ss, my + 1.8 * u * ss), bottom,
             (cx - 2.7 * u * ss, my + 1.8 * u * ss)]
    # Throat darkened one step so the open grin reads as a solid dark smile-band
    # at route scale (the "dark smile under a warm dot" cue) once the teeth blur.
    pygame.draw.polygon(surf, _shade_c(MOUTH_THROAT, -34),
                        [(int(p[0]), int(p[1])) for p in mouth])
    # Bright tooth band across the top of the open grin + tooth separators.
    teeth = [l_corner, (cx - 2.3 * u * ss, my), (cx + 2.3 * u * ss, my), r_corner,
             (cx + 2.3 * u * ss, my + 1.4 * u * ss), (cx - 2.3 * u * ss, my + 1.4 * u * ss)]
    pygame.draw.polygon(surf, TEETH, [(int(p[0]), int(p[1])) for p in teeth])
    pygame.draw.polygon(surf, _shade_c(TEETH, -70),
                        [(int(p[0]), int(p[1])) for p in teeth], max(1, int(ss)))
    for k in range(-2, 3):
        gx = cx + k * 1.9 * u * ss
        pygame.draw.line(surf, _shade_c(TEETH, -70), (int(gx), int(my)),
                         (int(gx), int(my + 1.4 * u * ss)), max(1, int(ss)))
    # One pointed FANG dropping below the tooth row on the die-side (LEFT). It is the
    # MVP of the "mean" read and the FIRST thing to vanish when shrunk, so it is now
    # seated HIGH into the tooth band (base up at the tooth-band top) with a wider
    # base and a longer drop — a fat triangular spike that reads as a single dark-
    # rimmed tusk even after the tooth separators blur. Drawn against the dark throat
    # FIRST as a fat throat wedge so the fang silhouette persists, then the bright
    # tooth fang over it with a heavy keyline.
    fang = [(cx - 3.4 * u * ss, my), (cx + 0.2 * u * ss, my),
            (cx - 1.6 * u * ss, my + 4.8 * u * ss)]
    pygame.draw.polygon(surf, _shade_c(MOUTH_THROAT, -34),
                        [(int(p[0] - 0.5 * u * ss), int(p[1] + 0.6 * u * ss)) for p in fang])
    pygame.draw.polygon(surf, TEETH, [(int(p[0]), int(p[1])) for p in fang])
    pygame.draw.polygon(surf, _shade_c(TEETH, -70),
                        [(int(p[0]), int(p[1])) for p in fang], max(2, int(1.6 * ss)))
    # The lip line wrapping the grin — a single smooth up-curving crescent.
    lip = []
    for k in range(13):
        t = k / 12.0
        lx = (l_corner[0] - 1.0 * u * ss) + ((r_corner[0] + 1.0 * u * ss)
                                             - (l_corner[0] - 1.0 * u * ss)) * t
        ly = (l_corner[1] - 1.4 * u * ss) + ((r_corner[1] - 1.0 * u * ss)
                                             - (l_corner[1] - 1.4 * u * ss)) * t \
            + (1.0 - (2.0 * t - 1.0) ** 2) * 4.2 * u * ss
        lip.append((int(lx), int(ly)))
    pygame.draw.lines(surf, LIP, False, lip, max(2, int(1.6 * ss)))
    if expr == "tongue":
        # A small tongue-tip licking the raised (die-side) grin corner.
        tr = pygame.Rect(int(l_corner[0] - 1.0 * u * ss), int(my + 1.0 * u * ss),
                         int(3.0 * u * ss), int(2.6 * u * ss))
        pygame.draw.ellipse(surf, TONGUE, tr)
        pygame.draw.ellipse(surf, _shade_c(TONGUE, -60), tr, max(1, int(ss)))


def _marotte_ruff(surf, cx, ny, r, ss, col, *, lobes=9, bell_col=GOLD, fringe=None):
    """A scalloped ruff under the bauble (the clown's neck collar), ported into
    ss space: a row of overlapping lit lobes ringing the neck with a small bell
    dangling at each outer edge, so the mini-clown reads as a costumed head, not
    a bare ball. Drawn dark-cored so it holds value on the day sky. `fringe` (a
    gold) hangs a fat bell off the bottom of each lobe — the jingle density moved
    to the collar so it can't blur the head silhouette into a halo."""
    for i in range(lobes):
        t = i / (lobes - 1)
        lx = cx - r + 2 * r * t
        ly = ny + 2.0 * ss + math.sin(t * math.pi) * -2.0 * ss
        rad = max(3, int(r * 0.30))
        if fringe is not None:
            # A short thread + fat bell hanging off the lobe's lower edge — a tidy
            # belled fringe along the collar reads as "jingles" at any scale.
            by = ly + rad + int(4 * ss)
            pygame.draw.line(surf, _shade_c(fringe, -60), (int(lx), int(ly + rad)),
                             (int(lx), int(by)), max(2, int(2.0 * ss)))
            pygame.draw.circle(surf, _shade_c(fringe, -55), (int(lx), int(by)), max(3, int(3.6 * ss)))
            pygame.draw.circle(surf, fringe, (int(lx), int(by)), max(2, int(2.8 * ss)))
            pygame.draw.circle(surf, _shade_c(fringe, 80),
                               (int(lx - ss), int(by - ss)), max(1, int(1.2 * ss)))
        pygame.draw.circle(surf, _shade_c(col, -55), (int(lx), int(ly)), rad)
        pygame.draw.circle(surf, col, (int(lx), int(ly)), max(2, rad - int(ss)))
        pygame.draw.circle(surf, _shade_c(col, 55),
                           (int(lx - rad * 0.3), int(ly - rad * 0.3)),
                           max(1, int(rad * 0.34)))
    for s in (-1, 1):
        bx, by = int(cx + s * (r + 1.5 * ss)), int(ny + 4 * ss)
        pygame.draw.circle(surf, _shade_c(bell_col, -55), (bx, by), max(2, int(3 * ss)))
        pygame.draw.circle(surf, bell_col, (bx, by), max(2, int(2.4 * ss)))
        pygame.draw.circle(surf, _shade_c(bell_col, 80),
                           (int(bx - ss), int(by - ss)), max(1, int(ss)))


# ── FANCY SHAFT ORNAMENTS — each design owns one so the five bodies read as
#    distinct material stories, all dark-cored so the route luma stays < 140. ──

def _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo, *, taper=0.0):
    """The dark shaft mass + a hard keyline. `taper` pinches the foot so the
    scepter narrows toward the pommel for a finished, balanced read. Returns the
    left/right edge point lists so an ornament can ride the (possibly tapered)
    body without recomputing the silhouette."""
    span = max(1, bot_y - top_y)
    left, right = [], []
    n = 18
    for i in range(n + 1):
        t = i / n
        y = top_y + span * t
        w = hw * (1.0 - taper * t)
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + list(reversed(right))
    pygame.draw.polygon(surf, lo, [(int(p[0]), int(p[1])) for p in body])
    pygame.draw.polygon(surf, _shade_c(lo, -45),
                        [(int(p[0]), int(p[1])) for p in body], max(2, int(2.0 * ss)))
    return left, right


def _shaft_twist(surf, cx, top_y, bot_y, hw, ss, col_a, col_b, lo):
    """A BARBER-POLE twist: bold diagonal plum/gold ribbons spiralling up a dark
    pole, clipped to the column so the stripes stay inside the body. The carousel-
    barker shaft."""
    left, right = _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo)
    clip = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    stripe = max(4, int(7 * ss))
    n = int((bot_y - top_y) / stripe) + 4
    # A 4-band cycle (plum x3, gold x1) so the dark plum dominates ~3:1 and the gold
    # ribbon reads as a bold spiral accent — the old 2:1 strobed/flickered at
    # distance, and the wider plum keeps the route median dark.
    for i in range(-2, n):
        y0 = top_y + i * stripe
        c = col_b if i % 4 == 3 else col_a
        quad = [(cx - hw, y0), (cx + hw, y0 - hw * 1.5),
                (cx + hw, y0 - hw * 1.5 + stripe), (cx - hw, y0 + stripe)]
        pygame.draw.polygon(clip, c, [(int(p[0]), int(p[1])) for p in quad])
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    body = left + list(reversed(right))
    pygame.draw.polygon(mask, (255, 255, 255, 255), [(int(p[0]), int(p[1])) for p in body])
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(clip, (0, 0))
    # A slim lit rail down the lit side reads the pole as round, not flat.
    pygame.draw.line(surf, _shade_c(col_a, 50), (int(cx - hw * 0.45), int(top_y)),
                     (int(cx - hw * 0.45), int(bot_y)), max(1, int(1.4 * ss)))
    pygame.draw.polygon(surf, _shade_c(lo, -45),
                        [(int(p[0]), int(p[1])) for p in body], max(2, int(2.0 * ss)))


def _shaft_panels(surf, cx, top_y, bot_y, hw, ss, body_col, lo, *, gold=GOLD):
    """RELIEF CARTOUCHE panels: a stack of raised, gold-framed lozenge panels down
    a dark pole, each with a lit bevel + a small diamond boss — a heraldic,
    marionette-master scepter."""
    _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo)
    panel_h = max(int(16 * ss), int((bot_y - top_y) * 0.13))
    y = top_y + int(4 * ss)
    while y + panel_h < bot_y:
        pw = hw * 0.78
        cyp = y + panel_h * 0.5
        lozenge = [(cx, y), (cx + pw, cyp), (cx, y + panel_h), (cx - pw, cyp)]
        pygame.draw.polygon(surf, _shade_c(gold, -40),
                            [(int(p[0]), int(p[1])) for p in lozenge])
        inner = [(cx, y + int(2.4 * ss)), (cx + pw - int(2.4 * ss), cyp),
                 (cx, y + panel_h - int(2.4 * ss)), (cx - pw + int(2.4 * ss), cyp)]
        pygame.draw.polygon(surf, body_col, [(int(p[0]), int(p[1])) for p in inner])
        # Lit upper-left bevel facet so each panel reads raised.
        pygame.draw.polygon(surf, _shade_c(body_col, 40),
                            [(int(cx), int(y + 2.4 * ss)),
                             (int(cx - pw + 2.4 * ss), int(cyp)), (int(cx), int(cyp))])
        pygame.draw.polygon(surf, gold,
                            [(int(p[0]), int(p[1])) for p in lozenge], max(1, int(1.6 * ss)))
        # A small bright diamond boss centred in the panel.
        br = max(2, int(2.6 * ss))
        pygame.draw.polygon(surf, GOLD_HI,
                            [(cx, int(cyp - br)), (int(cx + br), int(cyp)),
                             (cx, int(cyp + br)), (int(cx - br), int(cyp))])
        y += panel_h + int(3 * ss)


def _shaft_guilloche(surf, cx, top_y, bot_y, hw, ss, body_col, lo, *, line=GOLD_DK):
    """A GUILLOCHÉ / engine-turned grid: a dark pole engraved with a cross-hatched
    lattice of fine gold diagonals + bright lozenge nodes — the jingles-&-filigree
    body. Kept to a clean diamond lattice so it never fizzes at route scale."""
    left, right = _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo)
    grid = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    step = max(6, int(10 * ss))
    span = bot_y - top_y
    # Two opposing diagonal families weave the engine-turn lattice.
    for off in range(-int(2 * hw), int(span + 2 * hw), step):
        pygame.draw.line(grid, (*line, 230), (int(cx - hw), int(top_y + off)),
                         (int(cx + hw), int(top_y + off - 2 * hw)), max(1, int(1.3 * ss)))
        pygame.draw.line(grid, (*line, 230), (int(cx - hw), int(top_y + off - 2 * hw)),
                         (int(cx + hw), int(top_y + off)), max(1, int(1.3 * ss)))
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    body = left + list(reversed(right))
    pygame.draw.polygon(mask, (255, 255, 255, 255), [(int(p[0]), int(p[1])) for p in body])
    grid.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grid, (0, 0))
    # Bright lozenge nodes marching down the centre seam where the diagonals meet.
    y = top_y + step
    while y < bot_y:
        br = max(2, int(2.2 * ss))
        pygame.draw.polygon(surf, GOLD_HI,
                            [(cx, int(y - br)), (int(cx + br), int(y)),
                             (cx, int(y + br)), (int(cx - br), int(y))])
        y += step * 2
    pygame.draw.polygon(surf, _shade_c(lo, -45),
                        [(int(p[0]), int(p[1])) for p in body], max(2, int(2.0 * ss)))


def _shaft_fluted(surf, cx, top_y, bot_y, hw, ss, body_col, lo):
    """A SKELETAL fluted shaft: sharp vertical flutes cut into a near-black pole,
    its silhouette pinched into spine-like notches — the sinister scepter's cold,
    bony body. Tapers to a fanged foot."""
    span = max(1, bot_y - top_y)
    left, right = [], []
    n = 20
    for i in range(n + 1):
        t = i / n
        y = top_y + span * t
        # Periodic sharp notches pinch the edges into a vertebral spine.
        notch = abs(math.sin(t * math.pi * 6.0)) ** 2 * hw * 0.34
        w = hw * (1.0 - t * 0.30) - notch
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + list(reversed(right))
    pygame.draw.polygon(surf, lo, [(int(p[0]), int(p[1])) for p in body])
    pygame.draw.polygon(surf, _shade_c(lo, -55),
                        [(int(p[0]), int(p[1])) for p in body], max(2, int(2.0 * ss)))
    # A few cold vertical flute grooves catching a thin steely highlight.
    for fx in (-0.5, 0.0, 0.5):
        pygame.draw.line(surf, _shade_c(body_col, 30),
                         (int(cx + fx * hw), int(top_y + 4 * ss)),
                         (int(cx + fx * hw), int(bot_y - 4 * ss)), max(1, int(1.4 * ss)))


def _shaft_spiral_flute(surf, cx, top_y, bot_y, hw, ss, body_col, lo, *,
                        gem_a=PLUM, gem_b=LIME):
    """SPIRAL FLUTING with alternating plum/lime gem inlays winding up a dark
    twisted pole — the twisted-jester body. The diagonal flute seams plus the
    studded gems give a candy-cane-meets-jewelled-scepter read."""
    left, right = _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo)
    body = left + list(reversed(right))
    clip = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    span = bot_y - top_y
    flute = max(5, int(9 * ss))
    n = int(span / flute) + 3
    # Diagonal flute shading bands spiral the pole (lit / shade alternating).
    for i in range(-1, n):
        y0 = top_y + i * flute
        shade = _shade_c(body_col, 24) if i % 2 == 0 else _shade_c(lo, 12)
        quad = [(cx - hw, y0), (cx + hw, y0 - hw * 1.3),
                (cx + hw, y0 - hw * 1.3 + flute * 0.5), (cx - hw, y0 + flute * 0.5)]
        pygame.draw.polygon(clip, shade, [(int(p[0]), int(p[1])) for p in quad])
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), [(int(p[0]), int(p[1])) for p in body])
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(clip, (0, 0))
    # Alternating plum/lime gem studs marching down the centre (the inlay band).
    y = top_y + int(8 * ss)
    i = 0
    while y < bot_y - int(6 * ss):
        gc = gem_a if i % 2 == 0 else gem_b
        gr = max(2, int(3.2 * ss))
        pygame.draw.circle(surf, _shade_c(gc, -55), (cx, int(y)), gr + 1)
        pygame.draw.circle(surf, gc, (cx, int(y)), gr)
        pygame.draw.circle(surf, _shade_c(gc, 80),
                           (int(cx - gr * 0.3), int(y - gr * 0.3)), max(1, int(gr * 0.36)))
        pygame.draw.circle(surf, GOLD_DK, (cx, int(y)), gr + 1, max(1, int(ss)))
        y += int(18 * ss)
        i += 1
    pygame.draw.polygon(surf, _shade_c(lo, -45),
                        [(int(p[0]), int(p[1])) for p in body], max(2, int(2.0 * ss)))


def _ferrule(surf, cx, y, hw, ss, col, *, h=8, jewel=None):
    """A rich banded ferrule ring round the shaft: a dark base bead, a lit gold
    rim, an engraved mid-line — far richer than the old two thin lines. Optional
    `jewel` colour sets a centred cabochon for a jewelled collar."""
    hh = int(h * ss)
    over = int(2.0 * ss)
    pygame.draw.rect(surf, _shade_c(col, -45),
                     (int(cx - hw - over), int(y - hh * 0.5), int((hw + over) * 2), hh))
    pygame.draw.rect(surf, col,
                     (int(cx - hw - over), int(y - hh * 0.5), int((hw + over) * 2), hh),
                     max(1, int(1.4 * ss)))
    pygame.draw.line(surf, _shade_c(col, 70), (int(cx - hw - over), int(y - hh * 0.28)),
                     (int(cx + hw + over), int(y - hh * 0.28)), max(1, int(1.4 * ss)))
    pygame.draw.line(surf, _shade_c(col, -70), (int(cx - hw - over), int(y + hh * 0.28)),
                     (int(cx + hw + over), int(y + hh * 0.28)), max(1, int(ss)))
    if jewel is not None:
        jr = max(2, int(hh * 0.36))
        pygame.draw.circle(surf, _shade_c(jewel, -50), (cx, int(y)), jr + 1)
        pygame.draw.circle(surf, jewel, (cx, int(y)), jr)
        pygame.draw.circle(surf, _shade_c(jewel, 90),
                           (int(cx - jr * 0.3), int(y - jr * 0.3)), max(1, int(jr * 0.4)))


def _pommel_finial(surf, cx, bot_y, hw, ss, col, *, kind="ball", gem=None, bead=True):
    """A finished finial/pommel at the foot so the staff reads as a real scepter
    butt, not a sawn-off pole. `kind` picks the silhouette: a knobbed "ball", a
    spike-tipped "spike", or a flared collared "bell". `bead` adds the small
    collar bead above a ball pommel; drop it for a cleaner single-knob foot."""
    if kind == "spike":
        pr = int(hw * 1.5)
        pygame.draw.polygon(surf, _shade_c(col, -50),
                            [(int(cx - hw), int(bot_y - pr)), (int(cx + hw), int(bot_y - pr)),
                             (cx, int(bot_y + pr * 0.5))])
        pygame.draw.polygon(surf, col,
                            [(int(cx - hw + ss), int(bot_y - pr)),
                             (int(cx + hw - ss), int(bot_y - pr)),
                             (cx, int(bot_y + pr * 0.4))])
        pygame.draw.line(surf, _shade_c(col, 60), (int(cx - hw * 0.3), int(bot_y - pr)),
                         (cx, int(bot_y + pr * 0.3)), max(1, int(1.4 * ss)))
        return
    if kind == "bell":
        bw2 = int(hw * 1.7)
        pygame.draw.polygon(surf, _shade_c(col, -50),
                            [(int(cx - hw), int(bot_y - hw * 1.6)),
                             (int(cx + hw), int(bot_y - hw * 1.6)),
                             (int(cx + bw2), int(bot_y)), (int(cx - bw2), int(bot_y))])
        pygame.draw.polygon(surf, col,
                            [(int(cx - hw + ss), int(bot_y - hw * 1.6)),
                             (int(cx + hw - ss), int(bot_y - hw * 1.6)),
                             (int(cx + bw2 - ss), int(bot_y - ss)),
                             (int(cx - bw2 + ss), int(bot_y - ss))])
        pygame.draw.ellipse(surf, _shade_c(col, -40),
                            (int(cx - bw2), int(bot_y - 2 * ss), int(bw2 * 2), int(4 * ss)))
        return
    # Default: a fat knobbed ball pommel with a small bead beneath it.
    pr = int(hw * 1.5)
    pcy = int(bot_y - pr * 0.55)
    pygame.draw.circle(surf, _shade_c(col, -55), (cx, pcy), pr)
    pygame.draw.circle(surf, col, (cx, pcy), int(pr - ss))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - pr * 0.3), int(pcy - pr * 0.3)), max(2, int(pr * 0.36)))
    if gem is not None:
        pygame.draw.circle(surf, _shade_c(gem, -40), (cx, pcy), max(2, int(pr * 0.4)))
        pygame.draw.circle(surf, gem, (cx, pcy), max(2, int(pr * 0.32)))
        pygame.draw.circle(surf, _shade_c(gem, 90),
                           (int(cx - pr * 0.16), int(pcy - pr * 0.16)), max(1, int(pr * 0.14)))
    if bead:
        pygame.draw.circle(surf, _shade_c(col, -45), (cx, int(bot_y - pr * 1.25)),
                           max(2, int(hw * 0.8)))


# ---- 14f. Carousel Barker ---------------------------------------------------
# A fairground-barker scepter: a plum/gold BARBER-TWIST shaft spiralling up to a
# grinning mini-clown under a four-point cap, a jewelled gold ferrule collar and
# a gem-set ball pommel. The loudest, jolliest of the five.
def prop_14f(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(34 * ss)
    shaft_top = hy + hr
    hwid = int(7 * ss)
    _shaft_twist(surf, cx, shaft_top, bh - int(7 * ss), hwid, ss, PLUM, GOLD, PLUM_DK)
    _ferrule(surf, cx, bh * 0.5, hwid, ss, GOLD, h=9, jewel=PLUM)
    _pommel_finial(surf, cx, bh - int(4 * ss), hwid, ss, GOLD, kind="ball", gem=PLUM,
                   bead=False)
    # The clown's own four-point splayed cap (mirrors cap_four_point): two outer
    # points flop far out + low, two inner points lean apart, each bell-tipped.
    # Inner points splayed further apart (±19) and lifted so the cap clears the
    # forehead and stops shadowing the eyes; the two outer points still flop far
    # out + low.
    base_y = hy - hr + int(1 * ss)
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(8 * ss)
        tri = [(cx - span, base_y + int(2 * ss)), (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)), (cx, base_y + int(2 * ss)),
                             (bxp, byp)])
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, GOLD, (int(bxp), int(byp)), max(2, int(3.4 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(bxp), int(byp)), max(2, int(3.4 * ss)), max(1, int(ss)))
    _marotte_ruff(surf, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, LIME, lobes=9)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="grin")


# ---- 14g. Marionette Master -------------------------------------------------
# A heraldic puppeteer's scepter: a dark plum pole stacked with gold-framed RELIEF
# CARTOUCHE panels, a segmented-jaw mini-clown (an extra jaw-line under the grin),
# a flat lime two-point cap, double gold ferrules and a bell-flared foot.
def prop_14g(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(34 * ss)
    shaft_top = hy + hr
    hwid = int(8 * ss)
    _shaft_panels(surf, cx, shaft_top, bh - int(8 * ss), hwid, ss, PLUM, PLUM_DK)
    _ferrule(surf, cx, shaft_top + int(4 * ss), hwid, ss, GOLD, h=8)
    _ferrule(surf, cx, bh - int(20 * ss), hwid, ss, GOLD, h=8)
    _pommel_finial(surf, cx, bh - int(4 * ss), hwid, ss, GOLD, kind="bell")
    # A close lime hood-cap with two forward-leaning bell points (heraldic, tidy).
    # Crown lifted one step to LIME so it reads as lime, not olive, where it meets
    # the dark plum point above it.
    base_y = hy - hr + int(1 * ss)
    pygame.draw.ellipse(surf, LIME_DK,
                        (int(cx - hr - ss), int(base_y - 6 * ss), int(hr * 2 + 2 * ss), int(11 * ss)))
    pygame.draw.ellipse(surf, LIME,
                        (int(cx - hr), int(base_y - 6 * ss), int(hr * 2), int(10 * ss)))
    # A brighter lit crown band across the cap top so it reads clearly as LIME (not
    # an olive smudge where LIME_DK met the dark plum point) once shrunk.
    pygame.draw.ellipse(surf, _shade_c(LIME, 45),
                        (int(cx - hr * 0.78), int(base_y - 6 * ss), int(hr * 1.56), int(6 * ss)))
    for (dx, dy, col) in [(-20, -16, PLUM_DK), (20, -14, GOLD_DK)]:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(7 * ss)
        tri = [(cx - span, base_y - int(2 * ss)), (cx + span, base_y - int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, GOLD, (int(bxp), int(byp)), max(2, int(3.2 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(bxp), int(byp)), max(2, int(3.2 * ss)), max(1, int(ss)))
    _marotte_ruff(surf, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, PLUM, lobes=9, bell_col=GOLD)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="grin")
    # The marionette signature: a REAL second jaw-line well below the grin so the
    # head reads as a segmented puppet jaw that could clack open. Drawn as a deep
    # INK-dark, fat crescent set a clear gap below the lip — a soft shadow band under
    # it gives the lower jaw volume so the split survives shrinking instead of
    # reading as one faint scratch.
    jy = hy + int(hr * 1.00)
    jaw, jaw_lo = [], []
    for k in range(11):
        t = k / 10.0
        jx = cx - hr * 0.66 + hr * 1.32 * t
        dip = (1.0 - (2.0 * t - 1.0) ** 2) * hr * 0.36
        jaw.append((int(jx), int(jy + dip)))
        jaw_lo.append((int(jx), int(jy + dip + 2.0 * ss)))
    pygame.draw.lines(surf, _shade_c(CREAM, -50), False, jaw_lo, max(2, int(2.4 * ss)))
    pygame.draw.lines(surf, INK, False, jaw, max(3, int(2.8 * ss)))
    # Two short hinge ticks at the jaw corners reinforce the clack-open puppet read.
    for s in (-1, 1):
        hx = cx + s * int(hr * 0.66)
        pygame.draw.line(surf, INK, (hx, int(jy + hr * 0.06)),
                         (int(hx - s * 2 * ss), int(hy + hr * 0.46)), max(2, int(2.0 * ss)))


# ---- 14h. Jingles & Filigree ------------------------------------------------
# An ornate filigree scepter: a GUILLOCHÉ engine-turned gold lattice over a dark
# pole, a DENSE spray of dangling bells round a layered double-ruff mini-clown
# (tongue out), gold ferrules and a beaded ball pommel.
def prop_14h(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(36 * ss)
    shaft_top = hy + hr
    hwid = int(7 * ss)
    _shaft_guilloche(surf, cx, shaft_top, bh - int(7 * ss), hwid, ss, PLUM, PLUM_DK)
    _ferrule(surf, cx, shaft_top + int(3 * ss), hwid, ss, GOLD, h=7)
    _ferrule(surf, cx, bh * 0.62, hwid, ss, GOLD, h=7, jewel=LIME)
    _pommel_finial(surf, cx, bh - int(4 * ss), hwid, ss, GOLD, kind="ball", gem=LIME,
                   bead=False)
    # A compact two-point cap, then a DENSE belled spray fanning round the head so
    # the terminus jingles. Bells alternate gold so the cluster reads rich, not noisy.
    base_y = hy - hr + int(1 * ss)
    for (dx, dy, col) in [(-15, -22, PLUM_DK), (15, -20, LIME_DK)]:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(7 * ss)
        tri = [(cx - span, base_y + int(2 * ss)), (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
    # The radiating crown spray (even 4 bells) collapsed into a fuzzy gold halo that
    # broke the head silhouette at 30px, so the jingle density is RELOCATED to the
    # ruff as a fat belled FRINGE (see `bell_fringe` below) — the head stays a clean
    # round dome and "jingles" now lives at the collar where it can't blur the face.
    # Just two tight bells sit ON the cap points as the only head-level jingle.
    for (ax, ay) in [(-15, -22), (15, -20)]:
        ex, ey = cx + int(ax * ss), base_y + int(ay * ss)
        pygame.draw.circle(surf, GOLD_DK, (int(ex), int(ey)), max(3, int(3.8 * ss)))
        pygame.draw.circle(surf, GOLD, (int(ex), int(ey)), max(2, int(3.0 * ss)))
        pygame.draw.circle(surf, GOLD_HI, (int(ex - ss), int(ey - ss)), max(1, int(1.4 * ss)))
    # Layered DOUBLE ruff (a wide outer scallop + a tighter inner one) for the
    # filigree-rich neck read; the outer ruff carries the dense belled fringe so the
    # "jingles" payoff reads at the collar without crowding the head.
    _marotte_ruff(surf, cx, hy + hr + int(1 * ss), int(hr * 1.25), ss, PLUM_DK,
                  lobes=11, fringe=GOLD)
    _marotte_ruff(surf, cx, hy + hr - int(3 * ss), int(hr * 0.95), ss, LIME, lobes=9, bell_col=GOLD)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="tongue")


# ---- 14i. Sinister Scepter --------------------------------------------------
# The "MEAN" pole: a SKELETAL fluted near-black shaft pinched into a spine, a
# blank-stare dead-eyed mini-clown under a drooping single horned hood, an iron
# ferrule and a downward SPIKE foot. Amusing-but-unsettling.
# The sinister body is now on-palette: a deep PLUM_DK shaft (still dark — clears the
# luma gate) lit on one edge, with GOLD_DK metalwork. "Mean" comes from VALUE +
# expression, not the old cool blue-grey iron that read cheap and off-palette.
SINISTER_LO = (44, 24, 58)             # deep plum shaft core (a touch warmer than PLUM_DK)
SINISTER_MD = (96, 52, 118)            # the lit plum edge / hood face


def prop_14i(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(34 * ss)
    shaft_top = hy + hr
    hwid = int(8 * ss)
    _shaft_fluted(surf, cx, shaft_top, bh - int(10 * ss), hwid, ss, SINISTER_MD, SINISTER_LO)
    # A visible lit plum rail down one side so the near-black shaft no longer reads
    # as an indistinct dark stick at route scale — it catches a clear edge of light.
    pygame.draw.line(surf, SINISTER_MD, (int(cx - hwid * 0.62), int(shaft_top + 4 * ss)),
                     (int(cx - hwid * 0.62), int(bh - 12 * ss)), max(2, int(2.0 * ss)))
    # Metalwork re-spec'd to GOLD_DK (on-palette) instead of cool iron. A warm gold
    # collar with a candy-red cabochon is the one focal POP that pulls the eye to the
    # face and keeps the dark prop reading as a clown staff at distance.
    _ferrule(surf, cx, shaft_top + int(3 * ss), int(hwid * 0.85), ss, GOLD_DK, h=8,
             jewel=CANDY_RED)
    _pommel_finial(surf, cx, bh - int(6 * ss), int(hwid * 0.7), ss, GOLD_DK, kind="spike")
    # A single drooping horned hood — one forward point ROUNDED (no longer a sharp
    # witch-hat spike) + a prominent back HORN-NUB so the "horned hood" cue reads,
    # in lit plum so the silhouette leans sinister, not jolly.
    base_y = hy - hr + int(1 * ss)
    pygame.draw.ellipse(surf, _shade_c(SINISTER_LO, 20),
                        (int(cx - hr), int(base_y - 5 * ss), int(hr * 2), int(10 * ss)))
    # The forward point is built with a blunt rounded crook (two near-apex points)
    # so it reads as a flopped horn, not a pointed hat.
    hood = [(cx - int(6 * ss), base_y - int(2 * ss)),
            (cx + int(4 * ss), base_y - int(7 * ss)),
            (cx + int(22 * ss), base_y - int(24 * ss)),
            (cx + int(27 * ss), base_y - int(20 * ss)),
            (cx + int(24 * ss), base_y - int(13 * ss)),
            (cx + int(22 * ss), base_y - int(7 * ss)),
            (cx + int(10 * ss), base_y + int(2 * ss))]
    pygame.draw.polygon(surf, SINISTER_MD, [(int(p[0]), int(p[1])) for p in hood])
    pygame.draw.polygon(surf, _shade_c(SINISTER_LO, -10),
                        [(int(p[0]), int(p[1])) for p in hood], max(1, int(1.4 * ss)))
    # A rounded gold bell knob caps the flopped forward horn.
    pygame.draw.circle(surf, GOLD_DK, (int(cx + 24 * ss), int(base_y - 22 * ss)), max(3, int(3.6 * ss)))
    pygame.draw.circle(surf, GOLD, (int(cx + 24 * ss), int(base_y - 22 * ss)), max(2, int(3.0 * ss)))
    # A MORE PROMINENT back horn-nub (fatter + longer) so the "horned" read is
    # legible and balances the forward horn instead of looking like one hat-tip.
    nub = [(cx - int(5 * ss), base_y - int(4 * ss)), (cx - int(20 * ss), base_y - int(20 * ss)),
           (cx - int(13 * ss), base_y - int(18 * ss)),
           (cx - int(12 * ss), base_y - int(2 * ss))]
    pygame.draw.polygon(surf, SINISTER_MD, [(int(p[0]), int(p[1])) for p in nub])
    pygame.draw.polygon(surf, _shade_c(SINISTER_LO, -10),
                        [(int(p[0]), int(p[1])) for p in nub], max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, GOLD_DK, (int(cx - 20 * ss), int(base_y - 20 * ss)), max(2, int(2.8 * ss)))
    pygame.draw.circle(surf, GOLD, (int(cx - 20 * ss), int(base_y - 20 * ss)), max(2, int(2.2 * ss)))
    _marotte_ruff(surf, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, SINISTER_MD, lobes=9, bell_col=GOLD_DK)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="smirk")


# ---- 14j. Twisted Jester ----------------------------------------------------
# A jewelled candy scepter: a SPIRAL-FLUTED dark pole studded with alternating
# plum/lime GEM inlays, an ornate crown-cap mini-clown (grinning), a jewelled
# ferrule and a gem-set ball pommel — the richest, most regal of the five.
def prop_14j(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(36 * ss)
    shaft_top = hy + hr
    hwid = int(7 * ss)
    _shaft_spiral_flute(surf, cx, shaft_top, bh - int(7 * ss), hwid, ss, PLUM, PLUM_DK)
    _ferrule(surf, cx, shaft_top + int(4 * ss), hwid, ss, GOLD, h=9, jewel=PLUM)
    _pommel_finial(surf, cx, bh - int(4 * ss), hwid, ss, GOLD, kind="ball", gem=PLUM)
    # An ornate crown-cap: a low gold band ringing the head with five short
    # alternating plum/lime points, each gem- or bell-tipped — a jester's coronet.
    base_y = hy - hr + int(1 * ss)
    pygame.draw.arc(surf, GOLD_DK, (int(cx - hr - ss), int(base_y - 4 * ss),
                                    int(hr * 2 + 2 * ss), int(12 * ss)),
                    math.pi, math.tau, max(2, int(3 * ss)))
    # Staggered heights read the points as a coronet ARC, not a picket fence: the
    # CENTRE point spikes tallest, the inner pair drop a clear step, the outer pair
    # drop another step lower — a smooth bell of heights so the eye reads a crowned
    # arc even after the gold tips blur at route scale.
    pts = [(-22, -12, PLUM_DK), (-11, -24, LIME_DK), (0, -34, PLUM_DK),
           (11, -24, LIME_DK), (22, -12, PLUM_DK)]
    for (dx, dy, col) in pts:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(5 * ss)
        tri = [(cx + int(dx * ss) - span, base_y), (cx + int(dx * ss) + span, base_y), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.2 * ss)))
        # A single fat gold tip — the old lime-on-plum / plum-on-lime centre dot
        # vanished by 30px, so one clean gold bead keeps every point reading.
        pygame.draw.circle(surf, GOLD_DK, (int(bxp), int(byp)), max(2, int(3.4 * ss)))
        pygame.draw.circle(surf, GOLD, (int(bxp), int(byp)), max(2, int(2.8 * ss)))
        pygame.draw.circle(surf, GOLD_HI, (int(bxp - ss), int(byp - ss)), max(1, int(ss)))
    _marotte_ruff(surf, cx, hy + hr - int(2 * ss), int(hr * 1.1), ss, LIME_DK, lobes=11, bell_col=GOLD)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="grin")


# ---- 14k. Golden Jester (Twisted-Jester recolor + four-point cap) -----------
# The Twisted-Jester lead re-dressed: the spiral-flute shaft keeps its winding
# flutes but swaps the plum/lime gem studs for LIME/GOLD inlays, the foot pommel
# drops its collar bead for a cleaner gold-ball-on-purple-gem butt, and the
# coronet is replaced by the Carousel-Barker four-point splayed cap so the bauble
# wears the same loud fool's cap as the jolliest sibling.
def prop_14k(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(34 * ss)                      # cap seats as on prop_14f (the borrowed cap)
    shaft_top = hy + hr
    hwid = int(7 * ss)
    _shaft_spiral_flute(surf, cx, shaft_top, bh - int(7 * ss), hwid, ss, PLUM, PLUM_DK,
                        gem_a=LIME, gem_b=GOLD)
    _ferrule(surf, cx, shaft_top + int(4 * ss), hwid, ss, GOLD, h=9, jewel=PLUM)
    _pommel_finial(surf, cx, bh - int(4 * ss), hwid, ss, GOLD, kind="ball", gem=PLUM,
                   bead=False)
    # The four-point splayed cap from prop_14f: two outer points flop far out + low,
    # two inner points lean apart, each bell-tipped.
    base_y = hy - hr + int(1 * ss)
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(8 * ss)
        tri = [(cx - span, base_y + int(2 * ss)), (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)), (cx, base_y + int(2 * ss)),
                             (bxp, byp)])
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, GOLD, (int(bxp), int(byp)), max(2, int(3.4 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(bxp), int(byp)), max(2, int(3.4 * ss)), max(1, int(ss)))
    _marotte_ruff(surf, cx, hy + hr - int(2 * ss), int(hr * 1.1), ss, LIME_DK, lobes=11, bell_col=GOLD)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="grin")


# ════════════════════════════════════════════════════════════════════════════
#  BELL-FOOT VARIANTS (prop_14l … prop_14n) — three siblings re-shod with the
#  Marionette-Master flared BELL foot (a gold trumpet collar above a foot-ferrule
#  band) in place of the gem-ball pommel. The bell terminus reads as the more
#  elegant, formal scepter butt; everything above the foot is unchanged.
# ════════════════════════════════════════════════════════════════════════════

# ---- 14l. Carousel Barker · bell foot ---------------------------------------
def prop_14l(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(50 * ss)                      # seat the head lower so the tall cap +
                                           # its bell tips clear the box top (no clip)
    shaft_top = hy + hr
    hwid = int(7 * ss)
    _shaft_twist(surf, cx, shaft_top, bh - int(7 * ss), hwid, ss, PLUM, GOLD, PLUM_DK)
    _ferrule(surf, cx, bh * 0.5, hwid, ss, GOLD, h=9, jewel=PLUM)
    _ferrule(surf, cx, bh - int(20 * ss), hwid, ss, GOLD, h=8)
    # Foot planted ON the ground line (bot_y == bh): the flared bell ends at the
    # box bottom rather than 4 px above it, so the staff rests on the ground.
    _pommel_finial(surf, cx, bh, hwid, ss, GOLD, kind="bell")
    base_y = hy - hr + int(1 * ss)
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(8 * ss)
        tri = [(cx - span, base_y + int(2 * ss)), (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)), (cx, base_y + int(2 * ss)),
                             (bxp, byp)])
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, GOLD, (int(bxp), int(byp)), max(2, int(3.4 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(bxp), int(byp)), max(2, int(3.4 * ss)), max(1, int(ss)))
    _marotte_ruff(surf, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, LIME, lobes=9)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="grin")


# ---- 14m. Jingles & Filigree · bell foot ------------------------------------
def prop_14m(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(48 * ss)                      # seat the head lower so the tall cap +
                                           # its bell tips clear the box top (no clip)
    shaft_top = hy + hr
    hwid = int(7 * ss)
    _shaft_guilloche(surf, cx, shaft_top, bh - int(7 * ss), hwid, ss, PLUM, PLUM_DK)
    _ferrule(surf, cx, shaft_top + int(3 * ss), hwid, ss, GOLD, h=7)
    _ferrule(surf, cx, bh * 0.62, hwid, ss, GOLD, h=7, jewel=LIME)
    _ferrule(surf, cx, bh - int(20 * ss), hwid, ss, GOLD, h=8)
    _pommel_finial(surf, cx, bh, hwid, ss, GOLD, kind="bell")
    base_y = hy - hr + int(1 * ss)
    for (dx, dy, col) in [(-15, -22, PLUM_DK), (15, -20, LIME_DK)]:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(7 * ss)
        tri = [(cx - span, base_y + int(2 * ss)), (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
    for (ax, ay) in [(-15, -22), (15, -20)]:
        ex, ey = cx + int(ax * ss), base_y + int(ay * ss)
        pygame.draw.circle(surf, GOLD_DK, (int(ex), int(ey)), max(3, int(3.8 * ss)))
        pygame.draw.circle(surf, GOLD, (int(ex), int(ey)), max(2, int(3.0 * ss)))
        pygame.draw.circle(surf, GOLD_HI, (int(ex - ss), int(ey - ss)), max(1, int(1.4 * ss)))
    _marotte_ruff(surf, cx, hy + hr + int(1 * ss), int(hr * 1.25), ss, PLUM_DK,
                  lobes=11, fringe=GOLD)
    _marotte_ruff(surf, cx, hy + hr - int(3 * ss), int(hr * 0.95), ss, LIME, lobes=9, bell_col=GOLD)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="tongue")


# ---- 14n. Golden Jester · bell foot -----------------------------------------
def prop_14n(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(50 * ss)                      # seat the head lower so the tall cap +
                                           # its bell tips clear the box top (no clip)
    shaft_top = hy + hr
    hwid = int(7 * ss)
    _shaft_spiral_flute(surf, cx, shaft_top, bh - int(7 * ss), hwid, ss, PLUM, PLUM_DK,
                        gem_a=LIME, gem_b=GOLD)
    _ferrule(surf, cx, shaft_top + int(4 * ss), hwid, ss, GOLD, h=9, jewel=PLUM)
    _ferrule(surf, cx, bh - int(20 * ss), hwid, ss, GOLD, h=8)
    _pommel_finial(surf, cx, bh, hwid, ss, GOLD, kind="bell")
    base_y = hy - hr + int(1 * ss)
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp, byp = cx + int(dx * ss), base_y + int(dy * ss)
        span = int(8 * ss)
        tri = [(cx - span, base_y + int(2 * ss)), (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(surf, col, tri)
        pygame.draw.polygon(surf, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)), (cx, base_y + int(2 * ss)),
                             (bxp, byp)])
        pygame.draw.polygon(surf, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        pygame.draw.circle(surf, GOLD, (int(bxp), int(byp)), max(2, int(3.4 * ss)))
        pygame.draw.circle(surf, GOLD_DK, (int(bxp), int(byp)), max(2, int(3.4 * ss)), max(1, int(ss)))
    _marotte_ruff(surf, cx, hy + hr - int(2 * ss), int(hr * 1.1), ss, LIME_DK, lobes=11, bell_col=GOLD)
    _mini_clown_face(surf, cx, hy, hr, ss, expr="grin")


# ---- 15. Shepherd's Crook ---------------------------------------------------
# A long pale-wood crook whose hooked top is the gap terminus — the hook curls
# IN so the inner mouth of the hook reads as a clean dark-on-bright end.
CROOK_HI = (176, 150, 110)
CROOK_MD = (120, 96, 62)
CROOK_LO = (70, 54, 32)


def prop_15(surf, bw, bh, ss):
    cx = bw // 2
    hook_h = int(48 * ss)
    # Thicker shaft so the whole crook reads as a SOLID pillar, not a wire.
    _shaft(surf, cx, hook_h, bh - int(4 * ss), int(10 * ss), ss,
           CROOK_HI, CROOK_MD, CROOK_LO)
    # The hook: a THICK SOLID C curling from the shaft top up and back round. The
    # round-6 read flagged the open hook as the weakest gap-break (its hollow inner
    # curl let bright sky through and pygame's thin arc rasterising left seams), so
    # the hook is built as a CLOSED filled band polygon (outer sweep + inner sweep)
    # — a guaranteed hard dark mass against the gap, no sky bleed, no arc seams.
    hw = int(11 * ss)                      # heavier hook band
    rad = int(19 * ss)
    cxh = cx + int(2 * ss)
    cyh = hook_h - int(6 * ss)
    a0, a1 = math.pi * 0.06, math.pi * 1.98
    n = 22
    outer, inner = [], []
    for i in range(n + 1):
        a = a0 + i / n * (a1 - a0)
        outer.append((cxh + math.cos(a) * (rad + hw * 0.5),
                      cyh + math.sin(a) * (rad + hw * 0.5)))
        inner.append((cxh + math.cos(a) * (rad - hw * 0.5),
                      cyh + math.sin(a) * (rad - hw * 0.5)))
    band = outer + list(reversed(inner))
    # Dark keyline mass first (the silhouette), then the mid body inset.
    pygame.draw.polygon(surf, CROOK_LO, band)
    inner_band = ([(cxh + math.cos(a0 + i / n * (a1 - a0)) * (rad + hw * 0.5 - ss),
                    cyh + math.sin(a0 + i / n * (a1 - a0)) * (rad + hw * 0.5 - ss))
                   for i in range(n + 1)] +
                  list(reversed(
                      [(cxh + math.cos(a0 + i / n * (a1 - a0)) * (rad - hw * 0.5 + ss),
                        cyh + math.sin(a0 + i / n * (a1 - a0)) * (rad - hw * 0.5 + ss))
                       for i in range(n + 1)])))
    pygame.draw.polygon(surf, CROOK_MD, inner_band)
    # Slim lit rail on the outer curl for form (kept thin so the mass stays dark).
    pygame.draw.lines(surf, CROOK_HI, False,
                      [outer[i] for i in range(int(n * 0.4), int(n * 0.85))],
                      max(1, int(1.6 * ss)))
    # A bold leather binding band where hook meets shaft.
    _bind_rings(surf, cx, [hook_h + int(6 * ss), bh * 0.62], int(8.5 * ss), ss,
                LEATHER_DK)


# ---- 16. Skull-Topped Gold Rod ----------------------------------------------
# An ornate dark-gold scepter rod with a bone SKULL finial crowned by a faceted
# gem. The skull's domed cranium + the gem catch are the gap terminus.
def prop_16(surf, bw, bh, ss):
    cx = bw // 2
    sk_r = int(14 * ss)
    sy = int(20 * ss)
    shaft_top = sy + sk_r
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6 * ss), ss,
           GOLD_DK, GOLD_SHADOW, _shade_c(GOLD_SHADOW, -30))
    _bind_rings(surf, cx, [bh * 0.5, bh * 0.78], int(6.5 * ss), ss, GOLD)
    # Collar of gold points beneath the skull.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, GOLD_DK,
                            [(cx + sgn * int(4 * ss), shaft_top + int(4 * ss)),
                             (cx + sgn * int(13 * ss), shaft_top + int(2 * ss)),
                             (cx + sgn * int(7 * ss), shaft_top - int(8 * ss))])
    # Bone SKULL finial built as a true skull SILHOUETTE (not a ball): a wide domed
    # cranium that pinches IN at the cheeks then steps OUT to a square jaw, so the
    # outline reads as a skull at 1x — that distinct shape sets it apart from the
    # orb / marotte staffs. Dark eye sockets + a jaw notch carry the value break.
    dome = []
    n = 12
    for i in range(n + 1):                 # the rounded cranium cap (top half-arc)
        a = math.pi + i / n * math.pi
        dome.append((cx + math.cos(a) * sk_r, sy - sk_r * 0.25 + math.sin(a) * sk_r * 0.95))
    skull = (dome +
             [(cx + sk_r * 0.96, sy + sk_r * 0.15),       # temple (wide cranium)
              (cx + sk_r * 0.34, sy + sk_r * 0.62),       # cheek pinch DEEP in
              (cx + sk_r * 0.52, sy + sk_r * 1.15),       # jaw steps OUT below
              (cx + sk_r * 0.34, sy + sk_r * 1.32),       # square jaw corner
              (cx - sk_r * 0.34, sy + sk_r * 1.32),
              (cx - sk_r * 0.52, sy + sk_r * 1.15),
              (cx - sk_r * 0.34, sy + sk_r * 0.62),
              (cx - sk_r * 0.96, sy + sk_r * 0.15)])
    pygame.draw.polygon(surf, BONE_DK, skull)
    pygame.draw.polygon(surf, _shade_c(BONE_DK, -40), skull, max(1, int(1.6 * ss)))
    # Lit cranium dome inset so the rounded top reads bright above the dark sockets.
    pygame.draw.polygon(surf, BONE, [(p[0], p[1] + ss) for p in dome] +
                        [(cx + sk_r * 0.7, sy + sk_r * 0.1),
                         (cx - sk_r * 0.7, sy + sk_r * 0.1)])
    # Deep BIG angular eye sockets (the unmistakable skull cue) + a triangular nose.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, (24, 18, 16),
                            [(int(cx + sgn * sk_r * 0.14), int(sy + sk_r * 0.16)),
                             (int(cx + sgn * sk_r * 0.74), int(sy + sk_r * 0.06)),
                             (int(cx + sgn * sk_r * 0.66), int(sy + sk_r * 0.54)),
                             (int(cx + sgn * sk_r * 0.24), int(sy + sk_r * 0.54))])
    pygame.draw.polygon(surf, (24, 18, 16),
                        [(cx, int(sy + sk_r * 0.52)),
                         (cx + int(3.5 * ss), int(sy + sk_r * 0.82)),
                         (cx - int(3.5 * ss), int(sy + sk_r * 0.82))])
    # Jaw NOTCH: dark teeth gaps cut DEEP into the square jaw so the bottom reads as
    # a row of teeth, not a rounded chin.
    for sgn in (-1, 0, 1):
        pygame.draw.line(surf, (24, 18, 16),
                         (int(cx + sgn * sk_r * 0.26), int(sy + sk_r * 0.92)),
                         (int(cx + sgn * sk_r * 0.26), int(sy + sk_r * 1.3)),
                         max(1, int(1.8 * ss)))
    _facet_gem(surf, cx, int(sy - sk_r * 0.85), int(5 * ss), CANDY_RED,
               (255, 150, 150), CANDY_RED_DK, ss)


# ════════════════════════════════════════════════════════════════════════════
#  FAMILY C — CLOWN PROPS (gap-facing end at box top)
# ════════════════════════════════════════════════════════════════════════════

# ---- 17. Candy Cane ---------------------------------------------------------
# A red/white spiral cane with the hooked top as the gap terminus. The stripes
# are kept BOLD (few fat diagonals) so they never fizz; the body reads dark via
# deep candy-red cores between the cream stripes + a dark keyline.
CANE_RED = (190, 40, 50)
CANE_RED_DK = (120, 22, 30)
CANE_CREAM = (244, 236, 220)


def _candy_band(surf, cx, top_y, bot_y, hw, ss, *, red=CANE_RED, cream=CANE_CREAM,
                vert=True):
    """A barber-pole striped column/segment kept DARK overall: deep-red cores
    with fewer, slimmer cream diagonals + a dark keyline, so the body luma stays
    under the day sky. Clipped to the column rect via a mask."""
    w = int(hw * 2)
    h = max(1, int(bot_y - top_y))
    seg = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    seg.fill(red + (255,))
    stripe = max(4, int(8 * ss))
    for i in range(-2, (w + h) // stripe + 3):
        x0 = i * stripe
        pygame.draw.polygon(seg, cream + (255,),
                            [(x0, 0), (x0 + stripe // 2, 0),
                             (x0 + stripe // 2 - h, h), (x0 - h, h)])
    # Re-darken the RGB only (NOT alpha — BLEND_RGB_SUB leaves the band fully
    # opaque) so the cream reads cooler/darker and the whole band median sits
    # below the day sky, while the column stays a solid dark obstacle.
    seg.fill((60, 60, 60), special_flags=pygame.BLEND_RGB_SUB)
    mask = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (1, 0, w, h),
                     border_radius=int(hw))
    seg.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(seg, (int(cx - hw), int(top_y)))
    pygame.draw.rect(surf, CANE_RED_DK, (int(cx - hw), int(top_y), w, h),
                     max(1, int(1.6 * ss)), border_radius=int(hw))


def prop_17(surf, bw, bh, ss):
    cx = bw // 2
    hw = int(7 * ss)
    hook_h = int(40 * ss)
    rad = int(15 * ss)
    cxh = cx + int(2 * ss)
    cyh = hook_h - int(2 * ss)
    # Straight striped shaft.
    _candy_band(surf, cx, hook_h, bh - int(4 * ss), hw, ss)
    # Hooked top — a thick striped arc. Draw a dark base arc then a few bold
    # cream stripe ticks across it so the hook reads candy without fizz.
    rect = pygame.Rect(int(cxh - rad), int(cyh - rad), int(rad * 2), int(rad * 2))
    pygame.draw.arc(surf, CANE_RED_DK, rect, math.pi * 0.1, math.pi * 1.95,
                    int(hw * 2 + 2 * ss))
    pygame.draw.arc(surf, CANE_RED, rect, math.pi * 0.1, math.pi * 1.95, int(hw * 2))
    for k in range(7):
        a = math.pi * 0.2 + k * (math.pi * 1.6 / 6)
        x0 = cxh + math.cos(a) * (rad)
        y0 = cyh + math.sin(a) * (rad)
        pygame.draw.line(surf, CANE_CREAM,
                         (x0 + math.cos(a) * hw, y0 + math.sin(a) * hw),
                         (x0 - math.cos(a) * hw, y0 - math.sin(a) * hw),
                         max(2, int(2.6 * ss)))
    pygame.draw.arc(surf, CANE_RED_DK, rect, math.pi * 0.1, math.pi * 1.95,
                    max(1, int(1.6 * ss)))


# ---- 18. Giant Lollipop -----------------------------------------------------
# A big swirl DISC on a striped stick. A fat round top is the worst case for gap
# readability, so the disc is given a hard dark rim + a tight bright swirl core
# and the disc is kept NARROW enough (and dark-rimmed) that the sky-gap above its
# crown still reads as the brightest band.
LOLLI_A = (224, 96, 120)
LOLLI_B = (255, 232, 210)
LOLLI_RIM = (96, 30, 50)


def prop_18(surf, bw, bh, ss):
    cx = bw // 2
    disc_r = int(17 * ss)
    dy = disc_r + int(6 * ss)
    stick_top = dy + int(disc_r * 0.4)
    # A DARK candy-red stick (not a pale white one — a cream stick would wash on
    # the day sky, failing GATE 2), bound with cream rings for the candy read.
    _shaft(surf, cx, stick_top, bh - int(4 * ss), int(5 * ss), ss,
           CANE_RED, CANE_RED_DK, _shade_c(CANE_RED_DK, -30))
    _bind_rings(surf, cx, [bh * 0.5, bh * 0.72], int(5.5 * ss), ss, CANE_CREAM)
    # The swirl disc: a hard DARK rim (the value break that keeps the gap above it
    # reading), then a bold two-tone spiral kept LOW-frequency (a few fat arms).
    pygame.draw.circle(surf, LOLLI_RIM, (cx, int(dy)), disc_r + int(ss))
    pygame.draw.circle(surf, LOLLI_A, (cx, int(dy)), disc_r)
    arms = 5
    for k in range(arms):
        a0 = k * math.tau / arms
        pts = []
        for j in range(7):
            t = j / 6
            ang = a0 + t * 2.0
            rr = disc_r * t
            pts.append((cx + math.cos(ang) * rr, dy + math.sin(ang) * rr))
        pygame.draw.lines(surf, LOLLI_B, False, pts, max(2, int(3 * ss)))
    pygame.draw.circle(surf, LOLLI_RIM, (cx, int(dy)), disc_r, max(2, int(2.4 * ss)))
    pygame.draw.circle(surf, (255, 250, 244), (int(cx - disc_r * 0.35),
                                               int(dy - disc_r * 0.35)),
                       max(2, int(disc_r * 0.18)))


# ---- 19. Ringmaster Cane ----------------------------------------------------
# A black/gold show cane with a round gold KNOB top. The blunt knob is shaped
# with a hard dark underside + a tight specular so the gap still reads; a gold
# collar bands it.
CANE_BLACK = (34, 32, 40)
CANE_BLACK_HI = (78, 76, 88)


def prop_19(surf, bw, bh, ss):
    cx = bw // 2
    knob_r = int(11 * ss)
    ky = knob_r + int(6 * ss)
    shaft_top = ky + int(knob_r * 0.6)
    # Widened ~22% so the show cane reads as a genuine pillar to thread, not a
    # wire; the round gold knob top still carries the gap-read.
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6.7 * ss), ss,
           CANE_BLACK_HI, CANE_BLACK, _shade_c(CANE_BLACK, -18))
    # Gold bands striping the black cane (the bold show accent).
    for yt in (0.34, 0.55, 0.76):
        _bind_rings(surf, cx, [shaft_top + (bh - shaft_top) * yt], int(7.2 * ss), ss, GOLD)
    # Gold collar + round knob. A dark crescent across the knob's lower half is
    # the value break that keeps the gap above the knob reading bright.
    pygame.draw.rect(surf, GOLD_DK, (int(cx - knob_r * 0.7), int(shaft_top - 3 * ss),
                                     int(knob_r * 1.4), int(6 * ss)))
    pygame.draw.circle(surf, GOLD_DK, (cx, int(ky)), knob_r)
    pygame.draw.circle(surf, GOLD, (cx, int(ky - ss)), int(knob_r - ss))
    pygame.draw.circle(surf, GOLD_SHADOW, (cx, int(ky + knob_r * 0.35)),
                       int(knob_r * 0.7))
    pygame.draw.circle(surf, GOLD, (cx, int(ky - ss)), int(knob_r - ss),
                       max(1, int(ss)))
    pygame.draw.circle(surf, GOLD_HI, (int(cx - knob_r * 0.32), int(ky - knob_r * 0.34)),
                       max(2, int(knob_r * 0.26)))


# ---- 20. Furled Parasol -----------------------------------------------------
# A closed plum/lime parasol: a tight furled bundle tapering to a POINTED ferrule
# at the top — a clean sharp terminus — with a curved cane handle at the bottom.
def prop_20(surf, bw, bh, ss):
    cx = bw // 2
    tip_y = int(4 * ss)
    bundle_bot = bh - int(40 * ss)
    hw = int(9 * ss)
    by = bundle_bot - int(6 * ss)
    # Furled bundle: ONE solid dark tapered triangle from a pointed ferrule down to
    # the handle, panelled into exactly THREE BOLD full-height furl facets (plum /
    # lime / plum). No thin hairline ribs — each facet is a fat wedge that holds at
    # 1x, the dark spine + keyline carry the silhouette.
    facets = [(-1.0, -0.33, PLUM_DK), (-0.33, 0.33, LIME_DK), (0.33, 1.0, PLUM_DK)]
    for fa, fb, col in facets:
        poly = [(cx + fa * hw * 0.04, tip_y), (cx + fb * hw * 0.04, tip_y),
                (cx + fb * hw, by), (cx + fa * hw, by)]
        pygame.draw.polygon(surf, col, poly)
    # A single bold dark spine keyline so the bundle reads as ONE furled volume.
    spine = [(cx - hw, by), (cx, tip_y), (cx + hw, by)]
    pygame.draw.polygon(surf, _shade_c(PLUM_DK, -30), spine, max(2, int(2.4 * ss)))
    # Pointed metal ferrule terminus.
    pygame.draw.polygon(surf, ROD_HI, [(cx, tip_y), (cx - int(3 * ss), tip_y + int(12 * ss)),
                                       (cx + int(3 * ss), tip_y + int(12 * ss))])
    pygame.draw.polygon(surf, ROD_LO, [(cx, tip_y), (cx - int(3 * ss), tip_y + int(12 * ss)),
                                       (cx + int(3 * ss), tip_y + int(12 * ss))],
                        max(1, int(ss)))
    # A gold tie-band cinching the furl.
    _bind_rings(surf, cx, [bundle_bot - int(20 * ss)], hw, ss, GOLD)
    # Dark cane shaft + a curved handle at the bottom (the resting end).
    _shaft(surf, cx, bundle_bot - int(6 * ss), bh - int(18 * ss), int(5 * ss), ss,
           WOOD_HI, WOOD_MD, WOOD_LO)
    rad = int(10 * ss)
    rect = pygame.Rect(int(cx - rad * 2), int(bh - int(20 * ss)), int(rad * 2), int(rad * 2))
    pygame.draw.arc(surf, WOOD_MD, rect, math.pi * 1.5, math.tau, max(3, int(4 * ss)))


# ════════════════════════════════════════════════════════════════════════════
#  FAMILY D — MYSTIC & MENACING (gap-facing end at box top)
# ════════════════════════════════════════════════════════════════════════════

# ---- 21. Trident ------------------------------------------------------------
# A dark iron trident: three sharp prongs (the gap terminus reads as a trio of
# clean points), a swept crossbar, a wrapped haft.
def prop_21(surf, bw, bh, ss):
    cx = bw // 2
    bar_y = int(40 * ss)
    hw = int(6 * ss)
    _shaft(surf, cx, bar_y, bh - int(4 * ss), hw, ss, ROD_HI, ROD_MD, ROD_LO)
    _wrap_grip(surf, cx, bh * 0.45, bh - int(8 * ss), int(hw * 0.9), LEATHER, ss,
               diag=True)
    # Three prongs rising to sharp points (the trident head). Centre tallest.
    for sgn, h_mul, x_mul in ((-1, 0.7, 1.0), (0, 1.0, 0.0), (1, 0.7, 1.0)):
        px = cx + sgn * int(13 * ss) * x_mul
        tipy = bar_y - int(34 * ss) * h_mul
        prong = [(px - int(4 * ss), bar_y), (px, tipy), (px + int(4 * ss), bar_y)]
        _vgrad_poly(surf, prong, ROD_MD, ROD_LO, outline=(18, 20, 26),
                    ow=max(1, int(1.6 * ss)))
        pygame.draw.line(surf, ROD_HI, (px, tipy + int(3 * ss)),
                         (px - int(2 * ss), bar_y), max(1, int(1.4 * ss)))
    # Swept crossbar the prongs root into.
    bar = [(cx - int(16 * ss), bar_y + int(2 * ss)), (cx + int(16 * ss), bar_y + int(2 * ss)),
           (cx + int(12 * ss), bar_y + int(10 * ss)), (cx - int(12 * ss), bar_y + int(10 * ss))]
    pygame.draw.polygon(surf, ROD_LO, bar)
    pygame.draw.polygon(surf, (18, 20, 26), bar, max(2, int(2 * ss)))
    pygame.draw.line(surf, ROD_HI, (cx - int(14 * ss), bar_y + int(4 * ss)),
                     (cx + int(14 * ss), bar_y + int(4 * ss)), max(1, int(1.4 * ss)))


# ---- 22. Star Wand ----------------------------------------------------------
# A slender dark wand tipped with a glowing five-point STAR — the star's sharp
# upper points are the gap terminus, framed by its own glow.
STAR_GLOW = (255, 232, 120)
STAR_HOT = (255, 250, 220)


def prop_22(surf, bw, bh, ss):
    cx = bw // 2
    star_r = int(15 * ss)
    sy = star_r + int(8 * ss)
    shaft_top = sy + int(star_r * 0.5)
    # Widened ~28% again so the wand reads as a genuine pillar to thread, not a
    # hairline; the glowing star finial still carries the gap-read.
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(7.4 * ss), ss,
           CANE_BLACK_HI, CANE_BLACK, _shade_c(CANE_BLACK, -18))
    # A couple of bold gold bands so the slim wand still carries 2-3 elements.
    _bind_rings(surf, cx, [bh * 0.5, bh * 0.74], int(7.9 * ss), ss, GOLD)
    # Glowing five-point star finial — built from its outer + inner radii points.
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = star_r if k % 2 == 0 else star_r * 0.42
        pts.append((cx + math.cos(a) * rr, sy + math.sin(a) * rr))
    _glow_disc(surf, cx, sy, int(star_r * 1.4), STAR_GLOW, ss, alpha=150)
    pygame.draw.polygon(surf, GOLD_DK, pts)
    pygame.draw.polygon(surf, STAR_GLOW, [(cx + (p[0] - cx) * 0.82, sy + (p[1] - sy) * 0.82)
                                          for p in pts])
    pygame.draw.polygon(surf, GOLD_SHADOW, pts, max(1, int(1.6 * ss)))
    pygame.draw.circle(surf, STAR_HOT, (cx, int(sy)), max(2, int(star_r * 0.22)))


# ---- 23. Flaming Torch ------------------------------------------------------
# A dark cloth-wrapped torch whose gap-facing terminus is the DARK torch HEAD —
# a heavy dark pitch-soaked cloth knot crowning the top so the route reads a hard
# dark-body→bright-gap break (GATE 1). The warm FLAME is an ACCENT that licks up
# AROUND the head's sides and only to the head's crown, never spiking past it into
# the bright sky-gap, so the brightest band stays the gap, not the flame.
FLAME_LO = (180, 60, 24)
FLAME_MD = (236, 130, 36)
FLAME_HI = (255, 214, 96)
TORCH_HEAD = (38, 30, 24)
TORCH_HEAD_HI = (78, 62, 48)


def prop_23(surf, bw, bh, ss):
    cx = bw // 2
    head_top = int(6 * ss)                 # the DARK head crown faces the gap
    head_bot = int(40 * ss)
    bowl_y = int(48 * ss)
    _shaft(surf, cx, bowl_y, bh - int(4 * ss), int(7 * ss), ss,
           WOOD_HI, WOOD_MD, WOOD_LO)
    # Cloth wrap bindings on the haft (bold criss-cross feel via a couple rings).
    _bind_rings(surf, cx, [bh * 0.55, bh * 0.72, bh * 0.88], int(7.5 * ss), ss,
                LEATHER_DK)
    # The warm flame ACCENT first, UNDER the dark head so the head overlaps it on
    # top: tongues fan up the head's SIDES, cresting only to the head crown — the
    # warm glow frames the dark terminus instead of pointing into the gap.
    for sgn in (-1, 1):
        tongue = [(cx + sgn * int(4 * ss), bowl_y - int(4 * ss)),
                  (cx + sgn * int(13 * ss), head_bot - int(2 * ss)),
                  (cx + sgn * int(10 * ss), head_top + int(10 * ss)),
                  (cx + sgn * int(3 * ss), head_top + int(4 * ss)),
                  (cx + sgn * int(2 * ss), head_bot)]
        _vgrad_poly(surf, tongue, FLAME_MD, FLAME_LO, outline=(120, 36, 14),
                    ow=max(1, int(1.6 * ss)))
    _glow_disc(surf, cx, head_top + int(12 * ss), int(15 * ss), FLAME_MD, ss, alpha=80)
    # The DARK torch HEAD — a heavy rounded dark mass (cloth knot) crowning the top,
    # drawn OVER the flame so the topmost gap-facing pixels are dark, with only a
    # slim warm rim where the flame catches its lower edge.
    head = [(cx - int(11 * ss), head_bot),
            (cx - int(10 * ss), head_top + int(12 * ss)),
            (cx - int(5 * ss), head_top),
            (cx + int(5 * ss), head_top),
            (cx + int(10 * ss), head_top + int(12 * ss)),
            (cx + int(11 * ss), head_bot)]
    _vgrad_poly(surf, head, TORCH_HEAD_HI, TORCH_HEAD, outline=(18, 14, 10),
                ow=max(2, int(2.2 * ss)))
    # A few dark cloth-wrap seams across the head + a hot flame-lick rim at its base.
    for t in (0.32, 0.6):
        hy = head_top + (head_bot - head_top) * t
        pygame.draw.line(surf, (16, 12, 8), (cx - int(9 * ss), hy),
                         (cx + int(9 * ss), hy), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, FLAME_HI, (cx - int(9 * ss), head_bot - int(2 * ss)),
                     (cx + int(9 * ss), head_bot - int(2 * ss)), max(1, int(1.8 * ss)))
    # Dark pitch collar where the head meets the haft.
    pygame.draw.polygon(surf, (40, 30, 22),
                        [(cx - int(12 * ss), bowl_y), (cx + int(12 * ss), bowl_y),
                         (cx + int(8 * ss), bowl_y - int(8 * ss)),
                         (cx - int(8 * ss), bowl_y - int(8 * ss))])


# ── version registry ──────────────────────────────────────────────────────────
# (name, family, one-line distinct note, draw_fn). ~15 rows across FOUR families
# (~4/4/4/3): A SWORDS & BLADES · B STAFFS & SCEPTERS · C CLOWN PROPS ·
# D MYSTIC & MENACING. Every prop is a COMPLETE, structurally distinct object,
# authored gap-facing-end UP so the route flip scaffolding plants it correctly.
# Round 7: the user picked TWO round-6 winners — the Crystal Saber (#3) and the
# Jester Marotte (#6) — and asked each matured into 5 distinct variants. Each row
# carries a `hold` flag so the clown's lean is FAMILY-AWARE: a BLADE leans tip-DOWN
# on the ground with the gloved hand on the HANDLE near the top, while a STAFF
# stands point-UP with the hand gripping the shaft below the head.
VERSIONS = [
    # A — CRYSTAL-SABER VARIANTS (blade tip planted on the ground, handle up)
    ("Amethyst Saber", "BLADES",
     "cool-violet crystal · deep belly (edge 0.34) · four-shard FANNED guard · 4-gem cluster pommel",
     sword_11a, "blade"),
    ("Magenta Tanto", "BLADES",
     "warm-magenta BROAD near-straight slab · few bold facets · fused cross-shard guard · slab gem",
     sword_11b, "blade"),
    ("Glacier Saber", "BLADES",
     "icy-blue deep RECURVE · many thin glinting facets · frosty three-spike guard · iceberg pommel",
     sword_11c, "blade"),
    ("Rose-Quartz Khopesh", "BLADES",
     "warm-pink HOOKED sickle · swelled belly · one fat sweeping guard shard · twin-gem pommel",
     sword_11d, "blade"),
    ("Twilight Estoc", "BLADES",
     "deep indigo NARROW needle · tall chevron facet stack · low diamond guard · triple-gem stack pommel",
     sword_11e, "blade"),
    # B — JESTER-MAROTTE VARIANTS (point-up, hand grips shaft below the head)
    ("Marotte — Wide-Ear", "STAFFS",
     "round-6 two-ear silhouette · smiling face · twin plum/lime bell-nub ears · extra bind ring",
     prop_14a, "staff"),
    ("Marotte — Three-Ear Crown", "STAFFS",
     "THREE lobes (L/top/R) · open-O surprised face · big bell-nubs · triple-eared fool's crown",
     prop_14b, "staff"),
    ("Marotte — Coxcomb Crest", "STAFFS",
     "single tall scalloped ROOSTER-comb crest · sly tongue-out grin · three bell-tipped scallops",
     prop_14c, "staff"),
    ("Marotte — Belled Spray", "STAFFS",
     "FAN of four short stubby bell-nubs spraying out · jollier busy terminus · wide smile",
     prop_14d, "staff"),
    ("Marotte — Mini-Clown", "STAFFS",
     "the bauble WEARS the clown's own four-point cap (plum/lime/gold, bell-tipped) · tiny twin",
     prop_14e, "staff"),
]


# ── BLADE-ROUTE saber browse (round 8) ────────────────────────────────────────
# A FOCUSED saber-only comparison for the BLADE-route decision: the three
# strongest crystal sabers from round 7 KEPT as-is, plus TWO fresh crystalline
# directions exploring silhouettes / guard architectures untried in 11a-g — a
# SAWTOOTH cutting edge (11h) and a closed RING / HALO guard (11i). The marotte is
# already settled (Mini-Clown), so this sheet is sabers ONLY. Every row holds
# "blade" so the clown leans on it TIP-DOWN with the gloved hand on the HANDLE.
SABER_VERSIONS = [
    ("Twilight Estoc", "BLADES",
     "deep indigo NARROW needle · tall chevron facet stack · low diamond guard · triple-gem stack pommel",
     sword_11e, "blade"),
    ("Glacier Saber", "BLADES",
     "icy-blue deep RECURVE · many thin glinting facets · frosty three-spike guard · iceberg pommel",
     sword_11c, "blade"),
    ("Amethyst Saber", "BLADES",
     "cool-violet crystal · deep belly (edge 0.34) · four-shard FANNED guard · 4-gem cluster pommel",
     sword_11a, "blade"),
    ("Obsidian Sawglass", "BLADES",
     "smoky charcoal-violet · clean broad CLEAVER edge · round knuckle-DISC guard · faceted anvil pommel",
     sword_11h, "blade"),
    ("Halo Reliquary", "BLADES",
     "regal amber-gold STRAIGHT ceremonial blade · closed crystalline RING/HALO guard · pierced ring pommel",
     sword_11i, "blade"),
]


# ── STAFF-ROUTE marotte browse ────────────────────────────────────────────────
# The mirror of SABER_VERSIONS for the STAFF-route decision: the five latest
# jester-marotte variants on their own sheet so the staff prop can be browsed in
# isolation. Every row holds "staff" so the clown leans on it point-UP with the
# gloved hand on the shaft just below the lobed head.
MAROTTE_VERSIONS = [
    ("Marotte — Wide-Ear", "STAFFS",
     "round-6 two-ear silhouette · smiling face · twin plum/lime bell-nub ears · extra bind ring",
     prop_14a, "staff"),
    ("Marotte — Three-Ear Crown", "STAFFS",
     "THREE lobes (L/top/R) · open-O surprised face · big bell-nubs · triple-eared fool's crown",
     prop_14b, "staff"),
    ("Marotte — Coxcomb Crest", "STAFFS",
     "single tall scalloped ROOSTER-comb crest · sly tongue-out grin · three bell-tipped scallops",
     prop_14c, "staff"),
    ("Marotte — Belled Spray", "STAFFS",
     "FAN of four short stubby bell-nubs spraying out · jollier busy terminus · wide smile",
     prop_14d, "staff"),
    ("Marotte — Mini-Clown", "STAFFS",
     "the bauble WEARS the clown's own four-point cap (plum/lime/gold, bell-tipped) · tiny twin",
     prop_14e, "staff"),
]


# ── ROUND-9 MINI-CLOWN CRAFT pass ──────────────────────────────────────────────
# Panel 1 is the settled Mini-Clown (prop_14e) UNCHANGED, the baseline for
# contrast; panels 2-6 are the five new high-craft directions, each a TRUE mini-
# clown bauble (hero clown grin + ruff) over a distinct FANCY shaft ornament.
MAROTTE_CRAFT_VERSIONS = [
    ("Mini-Clown (baseline)", "STAFFS",
     "the SETTLED prop_14e UNCHANGED · plain cream face + four-point cap + flat plum shaft",
     prop_14e, "staff"),
    ("Carousel Barker", "STAFFS",
     "plum/gold BARBER-TWIST shaft · jewelled gold ferrule + gem ball pommel · grinning four-point cap",
     prop_14f, "staff"),
    ("Marionette Master", "STAFFS",
     "heraldic RELIEF CARTOUCHE panels · segmented-jaw bauble · lime hood-cap · twin ferrules + bell foot",
     prop_14g, "staff"),
    ("Jingles & Filigree", "STAFFS",
     "GUILLOCHÉ engine-turn lattice · dense dangling bell spray · layered double ruff · tongue-out grin",
     prop_14h, "staff"),
    ("Sinister Scepter", "STAFFS",
     "skeletal FLUTED near-black spine shaft · blank dead-eyed STARE · horned hood · iron SPIKE foot",
     prop_14i, "staff"),
    ("Twisted Jester", "STAFFS",
     "SPIRAL-FLUTE shaft with plum/lime GEM inlays · ornate crown-cap · jewelled ferrule + gem pommel",
     prop_14j, "staff"),
    ("Golden Jester", "STAFFS",
     "Twisted-Jester body recolored to LIME/GOLD gem inlays · four-point splayed cap (design 2) · "
     "jewelled ferrule + gem ball pommel (no collar bead)",
     prop_14k, "staff"),
    ("Carousel Barker · Bell-Foot", "STAFFS",
     "design 2 re-shod with the design-3 flared BELL foot (gold trumpet collar + foot ferrule) "
     "in place of the gem ball pommel",
     prop_14l, "staff"),
    ("Jingles & Filigree · Bell-Foot", "STAFFS",
     "design 4 re-shod with the design-3 flared BELL foot (gold trumpet collar + foot ferrule) "
     "in place of the gem ball pommel",
     prop_14m, "staff"),
    ("Golden Jester · Bell-Foot", "STAFFS",
     "design 7 re-shod with the design-3 flared BELL foot (gold trumpet collar + foot ferrule) "
     "in place of the gem ball pommel",
     prop_14n, "staff"),
]


# ════════════════════════════════════════════════════════════════════════════
#  ROUTE PANORAMA — true px, carried from round 2/4 unchanged
# ════════════════════════════════════════════════════════════════════════════

def _render_obstacle(draw_fn, H_true, ss, *, flip):
    surf, bw, bh = _box(H_true, ss)
    draw_fn(surf, bw, bh, ss)
    out_w = PIPE_W + 2 * OVERHANG
    out_h = max(1, int(H_true))
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    if flip:
        small = pygame.transform.flip(small, False, True)
    return small


def _blit_pair(dest, draw_fn, col_cx, gap_y, ss, *, ground_y=GROUND_Y):
    top_h = max(1, gap_y - HALF_GAP)
    bot_h = max(1, ground_y - (gap_y + HALF_GAP))
    x_left = int(col_cx - (PIPE_W + 2 * OVERHANG) / 2)
    top = _render_obstacle(draw_fn, top_h, ss, flip=True)
    dest.blit(top, (x_left, 0))                       # tip points DOWN to the gap
    bot = _render_obstacle(draw_fn, bot_h, ss, flip=False)
    dest.blit(bot, (x_left, gap_y + HALF_GAP))        # tip points UP to the gap


def _sky(w, h, top, bot):
    s = pygame.Surface((w, h))
    for i in range(h):
        s.fill(lerp_color(top, bot, i / max(1, h - 1)), (0, i, w, 1))
    return s


def _ground(surf, w):
    pygame.draw.rect(surf, (84, 132, 58), (0, GROUND_Y, w, surf.get_height() - GROUND_Y))
    pygame.draw.line(surf, (60, 100, 40), (0, GROUND_Y), (w, GROUND_Y), 2)


def _crest_gap_y(step, n_steps):
    lo, hi = 150, 430
    t = step / max(1, n_steps - 1)
    arc = math.sin(t * math.pi)
    gy = hi - (hi - lo) * arc
    return int(max(HALF_GAP + 30, min(GROUND_Y - HALF_GAP - 30, gy)))


def _route_panel(draw_fn, w, h, ss):
    route = _sky(w, h, SKY_TOP, SKY_BOT)
    _ground(route, w)
    n_steps = 11
    for step in range(n_steps):
        cx = 20 + SP // 2 + step * SP
        gy = _crest_gap_y(step, n_steps)
        _blit_pair(route, draw_fn, cx, gy, ss)
    pygame.draw.rect(route, (10, 12, 18), route.get_rect(), 2)
    return route


# ════════════════════════════════════════════════════════════════════════════
#  THE CLOWN LEANING ON THE GROUNDED PROP — left panel
# ════════════════════════════════════════════════════════════════════════════

from tools.render_jester_variants import (  # noqa: E402
    build_jester, JESTERS, draw_cupped_die, _mitt_thumb,
)
from tools.render_clown_dice import (  # noqa: E402
    _shade, _arm, VIEW_W, VIEW_H, VIEW_FEET_Y, SS as CLOWN_SS,
)
from tools.render_warren_mockup import shaped_palette  # noqa: E402
from tools.render_clown_dice import DAY_PHASE  # noqa: E402

# The clown's down-arm geometry baked into build_jester (warren_demo hero spec):
# hip_y = feet_y - 84, the near/down shoulder r_sh = (hip_cx + 25, hip_y - 50),
# hip_cx = cx + hip_dx with hip_dx = -6. We re-derive these to RE-POSE the down
# arm onto the grounded prop after build_jester paints its default down arm.
_HIP_DX = -6
_HIP_OFF = 84


def _grounded_prop_surface(draw_fn, prop_px, ss, *, w_scale=1.0):
    """Render ONE complete prop (gap-facing end UP, resting end at the box
    bottom) into its own tight box at hero scale, for the clown to LEAN on with
    the prop's bottom tip planted on the ground. The held/leaned LEFT version can
    carry finer detail than the tiled route version (brief: held > tiled).

    `w_scale` narrows ONLY the hero output width (the held prop) so a shortened
    blade stays slender beside the figure; the ROUTE tiles render through
    `_render_obstacle` at the full column width and are untouched by this.
    Returns a 1x surface + its (w, h)."""
    H = prop_px
    surf, bw, bh = _box(H, ss)
    draw_fn(surf, bw, bh, ss)
    out_w = max(1, int((PIPE_W + 2 * OVERHANG) * w_scale))
    return pygame.transform.smoothscale(surf, (out_w, H)), out_w, H


def render_clown_panel(draw_fn, idx, hold="staff"):
    """The REAL hero Plum & Lime jester (exactly as warren_demo builds it) in a
    FAMILY-AWARE lean pose: the prop stands VERTICALLY beside the clown with one
    end planted ON the ground, the near/lower gloved hand wraps its GRIP, while
    the OTHER hand presents the floating power-up die up high.

    `hold` orients the prop by family so the clown never grips the business end:
      - "blade": the prop is FLIPPED so the blade TIP rests on the ground and the
        HANDLE/pommel point UP; the gloved hand wraps the handle (top region).
      - "staff": kept as round 6 — head/bauble UP, the hand grips the shaft just
        below the head, the shaft foot on the ground.
    Returns a VIEW_W x VIEW_H surface."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    # Day-clearing sky + a sliver of grass (the warren clearing read).
    ground_y = VIEW_FEET_Y + 4        # the ground line the prop rests ON
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    # The OTHER (raised) hand presents the floating die high in the upper sky. The
    # die itself is drawn AFTER, up-left of the head, with the raised arm pointing
    # at it (the approved presenter read).
    die_x = jester_cx - 40
    die_base_y = 34
    hand_up = (die_x + 10, 80)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # --- the GROUNDED prop the clown leans on -------------------------------
    # Stand the prop vertically to the clown's near (right) side, bottom tip ON
    # the ground line, slightly angled like a cane so the lean reads relaxed. The
    # prop is rendered gap-end-UP, so its bottom edge is the resting tip.
    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    # Per-family height + grip so the prop is PROPORTIONATE to the figure and the
    # gloved hand meets a real grip rather than the business end. Blades are taller
    # (the planted tip eats length the handle must clear the hip); the marotte is
    # shorter so the bauble sits near head height with the hand below it.
    if hold == "blade":
        prop_px = 128                  # ~48% of the clown's display height: tip on
                                       # the ground, hilt at the hand near the hip,
                                       # no longer towering over the head
    else:
        prop_px = 150                  # bauble near head height, foot on the ground
    p_ss = 6                           # finer hero source than the route tiles
    # Shortening the blade alone leaves it relatively stubby (output width is fixed
    # to the column), so the hero held blade is slimmed; the route width is set in
    # _render_obstacle and is NOT affected by this hero-only scale.
    w_scale = 0.74 if hold == "blade" else 1.0
    prop, p_w, p_h = _grounded_prop_surface(draw_fn, prop_px, p_ss, w_scale=w_scale)
    # Blades flip so the TIP (authored at the top) ends DOWN on the ground and the
    # handle/pommel (authored at the bottom) points UP into the gloved hand.
    if hold == "blade":
        prop = pygame.transform.flip(prop, False, True)
    rot = -7                           # slight cane lean (top tips toward the clown)
    rotated = pygame.transform.rotate(prop, rot)
    # Plant the bottom-centre of the prop on the ground, set out to the clown's
    # near side. We compute where the unrotated bottom-centre lands post-rotation.
    foot_local = (p_w / 2, p_h - 2)
    cxr, cyr = p_w / 2, p_h / 2
    rad = math.radians(rot)
    dx = foot_local[0] - cxr
    dy = foot_local[1] - cyr
    rfx = cxr + (dx * math.cos(rad) + dy * math.sin(rad))
    rfy = cyr + (-dx * math.sin(rad) + dy * math.cos(rad))
    rfx += (rotated.get_width() - p_w) / 2
    rfy += (rotated.get_height() - p_h) / 2
    plant_x = jester_cx + 30           # plant point on the ground beside the clown
    plant_y = ground_y - 1
    prop_ox = int(plant_x - rfx)
    prop_oy = int(plant_y - rfy)
    layer.blit(rotated, (prop_ox, prop_oy))

    # The GRIP point on the prop's UPPER region (where the gloved hand wraps). For
    # a flipped blade the handle now sits near the TOP, so the grip rides high
    # (on the handle between guard and pommel, never the blade); nudged DOWN onto
    # the grip band (~0.34) from the prior 0.28 so the gloved mitt clearly OVERLAPS
    # the hilt on all five sabers rather than floating just above it. The marotte
    # grips the shaft ~0.32 down, just below the lobed head. Mapped through the
    # rotation + blit offset so it lands ON the prop in panel space.
    grip_frac = 0.34 if hold == "blade" else 0.32
    grip_local = (p_w / 2, p_h * grip_frac)
    gdx = grip_local[0] - cxr
    gdy = grip_local[1] - cyr
    rgx = cxr + (gdx * math.cos(rad) + gdy * math.sin(rad))
    rgy = cyr + (-gdx * math.sin(rad) + gdy * math.cos(rad))
    rgx += (rotated.get_width() - p_w) / 2
    rgy += (rotated.get_height() - p_h) / 2
    grip_x = prop_ox + rgx
    grip_y = prop_oy + rgy

    # --- RE-POSE the near/lower arm onto the grip (a confident showman lean) ---
    # build_jester already painted a default down arm into the hip; redraw OVER it
    # so a gloved hand rests on the grounded prop, resting weight. Use the same
    # _arm + _mitt_thumb kit so the limb matches the figure exactly. The shoulder
    # is the hard-coded down shoulder r_sh = (hip_cx + 25, hip_y - 50).
    r_sh = (hip_cx + 25, hip_y - 50)
    grip_hand = (int(grip_x), int(grip_y))
    light = spec["light"]
    _arm(layer, r_sh, grip_hand, 8, light)
    _mitt_thumb(layer, grip_hand, 7, (250, 250, 252), side=1)

    # --- the floating power-up die, presented up high by the raised hand -------
    pulse = idx * 1.7 + 2.0
    draw_cupped_die(layer, die_x, die_base_y, pulse, show_inset=(idx % 5 == 0))

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# ════════════════════════════════════════════════════════════════════════════
#  GATE-2 METER — median BODY luma of a prop at route scale
# ════════════════════════════════════════════════════════════════════════════

def _median_body_luma(draw_fn, ss, *, body_px=240):
    """Render ONE prop into a route-scale tile and return the MEDIAN perceptual
    luma of its opaque body pixels (the gap-facing END + finial highlights are a
    minority of pixels, so the median tracks the BODY). GATE 2 aims < ~140 vs the
    ~190 day sky. Measured on the route-tile render (the tiled version the player
    actually threads), not the finer LEFT hero shot."""
    small = _render_obstacle(draw_fn, body_px, ss, flip=False)
    small.lock()
    vals = []
    w, h = small.get_size()
    # Sample on a stride so the meter is fast but representative.
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b, a = small.get_at((x, y))
            if a < 200:
                continue
            vals.append(0.299 * r + 0.587 * g + 0.114 * b)
    small.unlock()
    if not vals:
        return 0.0
    vals.sort()
    return vals[len(vals) // 2]


# ════════════════════════════════════════════════════════════════════════════
#  THE SHEET — ~15 rows, each = clown-leaning (left) + route panorama (right)
# ════════════════════════════════════════════════════════════════════════════

def _render_sheet(versions, out_name, headers):
    """Render ONE comparison sheet (LEFT clown-lean + RIGHT route panorama per row)
    from a versions list and write it to docs/warren_sword/<out_name>. The hi-res
    settings (SS=6 route, p_ss=6 hero, ROW_SCALE=1.4) are shared so the saber-only
    round-8 browse renders identically to the round-7 sheet, only with fewer rows.
    `headers` is a list of (text, rgb) banner lines drawn under the title."""
    SS = 6                             # route supersample bumped 4→6 for crisper tiles

    # The sheet is rendered LARGER (ROW_SCALE) so the crisper SS=6 / p_ss=6 sources
    # are shown at higher resolution, not shrunk back down.
    ROW_SCALE = 1.4
    clown_w, clown_h = VIEW_W, VIEW_H
    N_STEPS = 11
    ROUTE_W = SP * N_STEPS + 40
    ROUTE_H = PLAY_H
    DISP_ROUTE_W = int(ROUTE_W * ROW_SCALE)
    DISP_ROUTE_H = int(ROUTE_H * ROW_SCALE)

    pad = 18
    head = 104
    row_gap = 14
    name_strip = 30
    inner_gap = 22

    # The route panel is the tall one; scale the clown panel up to match its
    # displayed height so both panels in a row sit on the same baseline.
    clown_scale = DISP_ROUTE_H / clown_h
    clown_dw = int(clown_w * clown_scale)
    clown_dh = DISP_ROUTE_H

    row_w = clown_dw + inner_gap + DISP_ROUTE_W
    row_h = name_strip + DISP_ROUTE_H

    sheet_w = pad * 2 + row_w
    sheet_h = head + len(versions) * (row_h + row_gap) + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(headers[0][0], True, headers[0][1]), (pad, 14))
    sheet.blit(sub_f.render(headers[1][0], True, headers[1][1]), (pad, 48))
    sheet.blit(sub_f.render(headers[2][0], True, headers[2][1]), (pad, 70))

    name_f = hud._font(19, True)
    reg_f = hud._font(13, True)
    note_f = hud._font(13, False)

    for idx, (name, register, note, draw_fn, hold) in enumerate(versions):
        ry = head + idx * (row_h + row_gap)
        strip = pygame.Surface((row_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        reg_col = ((150, 200, 235) if register == "BLADES" else
                   (250, 200, 120) if register == "STAFFS" else
                   (250, 150, 90) if register == "CLOWN PROPS" else
                   (210, 150, 250))
        ntxt = name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255))
        strip.blit(ntxt, (8, 5))
        rtxt = reg_f.render(f"[{register}]", True, reg_col)
        strip.blit(rtxt, (12 + ntxt.get_width(), 9))
        strip.blit(note_f.render(note, True, (188, 194, 206)),
                   (20 + ntxt.get_width() + rtxt.get_width(), 9))
        sheet.blit(strip, (pad, ry))

        body_y = ry + name_strip

        # --- LEFT: the clown LEANING on this grounded prop + presenting the die ---
        clown = render_clown_panel(draw_fn, idx, hold)
        clown = pygame.transform.smoothscale(clown, (clown_dw, clown_dh))
        pygame.draw.rect(clown, (10, 12, 18), clown.get_rect(), 2)
        sheet.blit(clown, (pad, body_y))

        # --- RIGHT: the route filled with this prop ---
        # Rendered at native game px (fixed geometry) from SS=6 supersampled tiles,
        # then scaled up to the displayed size so the crisp tiles read large.
        route = _route_panel(draw_fn, ROUTE_W, ROUTE_H, SS)
        route = pygame.transform.smoothscale(route, (DISP_ROUTE_W, DISP_ROUTE_H))
        sheet.blit(route, (pad + clown_dw + inner_gap, body_y))

        # Measure + print the median BODY luma of this prop at route scale (GATE 2:
        # aim < 140 against the ~190 day sky).
        luma = _median_body_luma(draw_fn, SS)
        print(f"  {idx + 1:2d}. {name:<22s} [{register:<11s}] median body luma = {luma:5.1f}"
              + ("  OK<140" if luma < 140 else "  HOT>=140"))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_sword")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, out_name)
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


_ROUND7_HEADERS = [
    ("Warren Prop Route — Round 7 (TWO winners matured: 5 Crystal-Saber + 5 Jester-Marotte variants · hi-res)",
     (255, 255, 255)),
    ("POSE (family-aware): BLADES lean TIP-DOWN with the gloved hand on the HANDLE (handle/pommel UP); "
     "MAROTTES stand point-UP, hand on the shaft below the head; the OTHER hand presents the floating die.",
     (205, 210, 220)),
    ("BLADES = amethyst-crystal family (cool-violet → warm-magenta → icy-blue).  STAFFS = jester-marotte family "
     "(one bauble wears the clown's own cap).  LEFT = hero clown LEANING on it · RIGHT = the route FILLED with it.",
     (170, 178, 190)),
]

_ROUND8_HEADERS = [
    ("Warren BLADE Route — Round 8 (SABERS ONLY · pick one: 3 round-7 keepers + 2 fresh crystal directions · hi-res)",
     (255, 255, 255)),
    ("POSE: the clown leans on the blade TIP-DOWN, gloved hand on the HANDLE (handle/pommel UP); "
     "the OTHER hand presents the floating power-up die. Marotte is already settled (Mini-Clown) — sabers only here.",
     (205, 210, 220)),
    ("KEEPERS = Twilight Estoc · Glacier Saber · Amethyst Saber.  FRESH = Obsidian Sawglass (sawtooth edge) · "
     "Halo Reliquary (closed ring guard).  LEFT = hero clown LEANING on it · RIGHT = the route FILLED with it.",
     (170, 178, 190)),
]


_ROUND8M_HEADERS = [
    ("Warren STAFF Route — Marotte browse (STAFFS ONLY · the five latest jester-marotte variants · hi-res)",
     (255, 255, 255)),
    ("POSE: the clown leans on the marotte point-UP, gloved hand on the shaft just below the lobed head; "
     "the OTHER hand presents the floating power-up die. Sabers live on their own sheet — marottes only here.",
     (205, 210, 220)),
    ("VARIANTS = Wide-Ear · Three-Ear Crown · Coxcomb Crest · Belled Spray · Mini-Clown (wears the clown's own cap).  "
     "LEFT = hero clown LEANING on it · RIGHT = the route FILLED with it.",
     (170, 178, 190)),
]


_ROUND9_HEADERS = [
    ("Warren STAFF — Round 9 (MINI-CLOWN CRAFT pass · 1 baseline + 5 fresh designs · ONE big staff per panel)",
     (255, 255, 255)),
    ("Each panel = ONE marotte at MAX size, bauble UP, foot on the ground, on a day-sky strip. Panel 1 = the "
     "settled Mini-Clown (prop_14e) UNCHANGED; panels 2-6 pour all craft into the STAFF (true mini-clown grin + ruff + fancy shaft).",
     (205, 210, 220)),
    ("DESIGNS = Carousel Barker (barber-twist) · Marionette Master (relief panels) · Jingles & Filigree (guilloché) · "
     "Sinister Scepter (fluted spine, the 'mean' pole) · Twisted Jester (spiral-flute gem inlay). Amusing-and-a-little-mean.",
     (170, 178, 190)),
]


_ROUND10_HEADERS = [
    ("Warren STAFF — Round 10 (CRAFT roster + BELL-FOOT variants · ONE big staff per panel)",
     (255, 255, 255)),
    ("Panels 1-7 = the round-9 craft roster. Panels 8-10 re-shoe designs 2 / 4 / 7 with the design-3 "
     "flared BELL foot (gold trumpet collar + foot ferrule) in place of the gem ball pommel.",
     (205, 210, 220)),
    ("Everything above the foot is unchanged per design; only the staff terminus differs on 8-10 — "
     "the bell reads as the more elegant, formal scepter butt.",
     (170, 178, 190)),
]


_ROUND10_BELLFOOT_HEADERS = [
    ("Warren STAFF — BELL-FOOT designs only (8, 9, 10) · ONE big staff per panel",
     (255, 255, 255)),
    ("The three flared-BELL-foot scepters: Carousel Barker, Jingles & Filigree, and "
     "Golden Jester (the one currently on the hero), each with the gold trumpet collar + foot ferrule.",
     (205, 210, 220)),
    ("Same heads/shafts as their craft-roster originals; only shown together here for a close compare.",
     (170, 178, 190)),
]


def _render_craft_sheet(versions, out_name, headers, *, label_offset=0):
    """Round-9 single-staff sheet: ONE marotte per panel at MAXIMUM size, bauble
    UP, foot planted on a day-sky + ground strip — the staff 'from the route, as
    big as the panel allows'. A 3-column grid of tall panels lets each staff read
    big enough that the bauble's mini-clown face + the shaft ornament are legible.
    Renders each staff through `_render_obstacle` (head-UP, no flip) at a HIGH
    supersample so the ported face + shaft detail stays crisp. Prints each prop's
    median body luma with the same OK<140 / HOT>=140 tag as `_render_sheet`."""
    SS = 9                             # high supersample so bauble + shaft read crisp

    # Each panel shows the full play-column height so the staff towers as on the
    # route; the staff fills the column from a foot on the ground line up to the
    # bauble rising into the upper sky.
    PANEL_W = PIPE_W + 2 * OVERHANG + 60   # the column + a little sky to each side
    PANEL_H = PLAY_H
    SCALE = 1.6                         # show the crisp SS=9 source large
    DISP_W = int(PANEL_W * SCALE)
    DISP_H = int(PANEL_H * SCALE)

    cols = 3
    rows = -(-len(versions) // cols)   # ceil so a 7th panel adds a row, not overflows
    pad = 20
    head = 104
    name_strip = 30
    gap = 16

    cell_w = DISP_W
    cell_h = name_strip + DISP_H
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + rows * cell_h + (rows - 1) * gap + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(headers[0][0], True, headers[0][1]), (pad, 14))
    sheet.blit(sub_f.render(headers[1][0], True, headers[1][1]), (pad, 48))
    sheet.blit(sub_f.render(headers[2][0], True, headers[2][1]), (pad, 70))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    # Plant the staff's foot on the ground; the bauble rises from the top of the
    # column. The whole prop spans foot-to-bauble in one obstacle so it reads as a
    # single grounded scepter (head-UP, no flip).
    col_x = (PANEL_W - (PIPE_W + 2 * OVERHANG)) // 2
    prop_h = GROUND_Y                  # foot exactly on the ground line

    for idx, (name, register, note, draw_fn, _hold) in enumerate(versions):
        cxg = idx % cols
        ryg = idx // cols
        px = pad + cxg * (cell_w + gap)
        py = head + ryg * (cell_h + gap)

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        ntxt = name_f.render(f"{idx + 1 + label_offset}. {name}", True, (255, 255, 255))
        strip.blit(ntxt, (8, 5))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (12 + ntxt.get_width(), 9))
        sheet.blit(strip, (px, py))

        # The day-sky + ground strip, then ONE staff foot-on-ground, bauble UP.
        panel = _sky(PANEL_W, PANEL_H, SKY_TOP, SKY_BOT)
        _ground(panel, PANEL_W)
        staff = _render_obstacle(draw_fn, prop_h, SS, flip=False)
        panel.blit(staff, (col_x, 0))
        pygame.draw.rect(panel, (10, 12, 18), panel.get_rect(), 2)
        panel = pygame.transform.smoothscale(panel, (DISP_W, DISP_H))
        sheet.blit(panel, (px, py + name_strip))

        luma = _median_body_luma(draw_fn, SS)
        print(f"  {idx + 1:2d}. {name:<22s} median body luma = {luma:5.1f}"
              + ("  OK<140" if luma < 140 else "  HOT>=140"))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_sword")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, out_name)
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ════════════════════════════════════════════════════════════════════════════
#  WARREN CLOWN HERO LOOK-DEV — Round 2 (the FULL clown gripping prop_14n)
# ════════════════════════════════════════════════════════════════════════════
# Built on render_clown_panel (the approved hero composition): the REAL Plum &
# Lime jester from build_jester, the prop_14n marotte rendered VERBATIM and stood
# vertically with its foot on the ground, the near hand wrapping the shaft, the
# raised hand presenting the floating die. Round 2 changes nothing about the
# clown's drawing kit or the marotte's design; it only retunes four pose knobs:
#   - staff LENGTH  (a taller source box at the same ss lengthens the shaft span
#     only — the head px is fixed, so head size + shaft width are untouched),
#   - GRIP HEIGHT   (pushed DOWN onto the mid/lower shaft, clear of bauble+lobes),
#   - the GRIP HAND (a compact wrap built from the figure's own glove kit, sized
#     to _mitt_thumb's radius-7 glove — small realistic fingers, not fat digits),
#   - the RAISED ARM reach (a clearly LONG left arm presenting the die up high).


def _staff_grip_hand(surf, hand, shaft_w, glove, light, *, fingers, side=1):
    """A COMPACT gloved hand wrapping a vertical shaft, proportioned to the
    figure's own radius-7 mitt (`_mitt_thumb`). The read: the back of the hand
    sits BEHIND the shaft (small knuckle nubs peek above the wrap) while the
    thumb + front fingers cross IN FRONT of it, so weight rests on a real grip.

    `fingers` selects the front-finger styling so the five variants differ only
    in how the hand reads, never in scale:
      - "wrap"     : a smooth mitt band + thumb-over (round, minimal digits),
      - "split"    : two short front fingers separated by a single groove,
      - "knuckles" : three small rounded knuckle bumps over the shaft front.
    `side`=+1 means the thumb crosses on the figure's inner (left) side."""
    hx, hy = int(hand[0]), int(hand[1])
    gr = 7                                 # matches the figure's down-mitt glove
    dk = _shade_c(glove, -55)
    # Back-of-hand knuckles BEHIND the shaft: small dark-edged nubs cresting the
    # top of the wrap so the shaft visibly passes through the fist.
    for k in (-1, 0, 1):
        bx = hx + k * (gr // 2)
        by = hy - gr + 1
        pygame.draw.circle(surf, dk, (bx, by), 3)
        pygame.draw.circle(surf, _shade_c(glove, -25), (bx, by), 2)
    # The palm band: a short rounded mitt clamping the shaft front, the wrist cuff
    # tucking under it. Kept compact (a touch wider than tall) so it reads as a
    # closed fist on the pole, not a ball stuck to it.
    palm = pygame.Rect(0, 0, gr * 2 + 2, gr + 3)
    palm.center = (hx, hy + 1)
    pygame.draw.rect(surf, dk, palm, border_radius=gr // 2 + 1)
    palm2 = palm.inflate(-2, -2)
    pygame.draw.rect(surf, glove, palm2, border_radius=gr // 2)
    # Top-left sheen on the palm so the glove catches light like the other mitts.
    pygame.draw.circle(surf, _shade_c(glove, 35), (hx - 2, hy - 1), 2)
    # Thumb crossing OVER the shaft on the inner side — a small nub + nail groove.
    tx = hx - side * (gr - 1)
    pygame.draw.circle(surf, dk, (tx, hy + 1), gr // 2 + 1)
    pygame.draw.circle(surf, glove, (tx, hy + 1), gr // 2)
    # Front fingers crossing the shaft, styled per variant — all SMALL.
    if fingers == "wrap":
        pygame.draw.line(surf, dk, (hx - gr + 1, hy + 2), (hx + gr - 1, hy + 2), 1)
    elif fingers == "split":
        for fx in (hx - 2, hx + 3):
            pygame.draw.circle(surf, dk, (fx, hy + gr - 2), 3)
            pygame.draw.circle(surf, glove, (fx, hy + gr - 2), 2)
        pygame.draw.line(surf, dk, (hx, hy + 2), (hx, hy + gr - 1), 1)
    else:  # "knuckles"
        for fx in (hx - 3, hx + 1, hx + 5):
            pygame.draw.circle(surf, dk, (fx, hy + gr - 3), 2)
            pygame.draw.circle(surf, _shade_c(glove, 10), (fx, hy + gr - 3), 1)
    # Crisp keyline around the whole hand so it lifts off the shaft + sky.
    pygame.draw.rect(surf, dk, palm, border_radius=gr // 2 + 1, width=1)
    _ = (shaft_w, light)                   # kept for call-site symmetry/future use


def render_clown_staff_r2(idx, *, prop_px, grip_frac, reach, fingers):
    """Round-2 hero panel: the REAL build_jester clown gripping prop_14n VERBATIM.
    Only the four pose knobs vary across variants — see `_staff_grip_hand` and the
    module banner. Returns a VIEW_W x VIEW_H surface (same canvas as the approved
    render_clown_panel)."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    # The raised LEFT arm presents the floating die high in the sky. `reach` pulls
    # the open offering palm farther up + out so the left arm reads clearly LONG
    # (build_jester's true shoulder is fixed; a higher hand target lengthens the
    # visible reach). The die hovers just above that open palm.
    die_x = jester_cx - 40
    die_base_y = 34 - reach // 2
    hand_up = (die_x + 12, 80 - reach)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # --- prop_14n stood vertically beside the clown, foot on the ground ---------
    # Rendered VERBATIM through the grounded-prop path; `prop_px` is the ONLY lever
    # and it lengthens the SHAFT only (head px fixed in the source draw).
    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    p_ss = 6
    prop, p_w, p_h = _grounded_prop_surface(prop_14n, prop_px, p_ss, w_scale=1.0)
    rot = -7                               # the relaxed cane lean (top toward clown)
    rotated = pygame.transform.rotate(prop, rot)
    foot_local = (p_w / 2, p_h - 2)
    cxr, cyr = p_w / 2, p_h / 2
    rad = math.radians(rot)
    dx = foot_local[0] - cxr
    dy = foot_local[1] - cyr
    rfx = cxr + (dx * math.cos(rad) + dy * math.sin(rad))
    rfy = cyr + (-dx * math.sin(rad) + dy * math.cos(rad))
    rfx += (rotated.get_width() - p_w) / 2
    rfy += (rotated.get_height() - p_h) / 2
    plant_x = jester_cx + 30
    plant_y = ground_y - 1
    prop_ox = int(plant_x - rfx)
    prop_oy = int(plant_y - rfy)
    layer.blit(rotated, (prop_ox, prop_oy))

    # The grip point pushed DOWN the shaft (well below the lobed head + ear lobes)
    # so the compact hand wraps the mid/lower shaft body.
    grip_local = (p_w / 2, p_h * grip_frac)
    gdx = grip_local[0] - cxr
    gdy = grip_local[1] - cyr
    rgx = cxr + (gdx * math.cos(rad) + gdy * math.sin(rad))
    rgy = cyr + (-gdx * math.sin(rad) + gdy * math.cos(rad))
    rgx += (rotated.get_width() - p_w) / 2
    rgy += (rotated.get_height() - p_h) / 2
    grip_x = prop_ox + rgx
    grip_y = prop_oy + rgy

    # --- re-pose the near/lower arm onto the grip + lay the COMPACT wrap hand ----
    # build_jester already painted a default down arm into the hip; redraw the limb
    # OVER it with the figure's own _arm kit, then a compact grip hand replaces the
    # plain mitt so small realistic fingers read as wrapping the shaft.
    r_sh = (hip_cx + 25, hip_y - 50)
    grip_hand = (int(grip_x), int(grip_y))
    light = spec["light"]
    _arm(layer, r_sh, grip_hand, 8, light)
    shaft_w = int(7 * CLOWN_SS)
    _staff_grip_hand(layer, grip_hand, shaft_w, (250, 250, 252), light,
                     fingers=fingers, side=1)

    # --- the floating power-up die, presented up high by the raised hand --------
    pulse = idx * 1.7 + 2.0
    draw_cupped_die(layer, die_x, die_base_y, pulse, show_inset=(idx % 5 == 0))

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Five FULL clown-with-staff variants — same real clown + real prop_14n, varying
# ONLY: staff length, grip height, compact grip-hand finger styling, raised reach.
_CLOWN_R2_VARIANTS = [
    ("Tall Wrap",      dict(prop_px=176, grip_frac=0.50, reach=10, fingers="wrap"),
     "long shaft, mid-shaft wrap grip, smooth mitt, raised arm extended"),
    ("Low Knuckles",   dict(prop_px=186, grip_frac=0.58, reach=14, fingers="knuckles"),
     "longer shaft, lower grip, three small knuckles, longest reach"),
    ("Mid Split",      dict(prop_px=170, grip_frac=0.46, reach=8, fingers="split"),
     "long shaft, mid grip, two split front fingers, high reach"),
    ("Slim Low Wrap",  dict(prop_px=182, grip_frac=0.55, reach=12, fingers="wrap"),
     "tall shaft, low wrap grip, smooth mitt, extended reach"),
    ("High Knuckles",  dict(prop_px=172, grip_frac=0.44, reach=6, fingers="knuckles"),
     "long shaft, upper-mid grip, small knuckles, tallest die present"),
]


_CLOWN_R2_HEADERS = [
    ("Warren Clown HERO look-dev — Round 2 (FULL clown gripping prop_14n · 5 variants · hi-res p_ss=6)",
     (255, 255, 255)),
    ("REAL build_jester clown + prop_14n VERBATIM (only its LENGTH changes). Grip pushed DOWN the shaft body, "
     "below the lobed head; the grip hand is a COMPACT wrap sized to the figure's own radius-7 mitt.",
     (205, 210, 220)),
    ("Variants vary ONLY: staff length · grip height · compact grip-hand fingers · raised-arm reach. "
     "Long left arm presents the floating power-up die over an open offering palm.",
     (170, 178, 190)),
]


def _render_clown_r2_sheet():
    """Round-2 clown look-dev sheet: a 1-column stack of the five FULL
    clown-with-staff variants at hero scale, each labelled with what differs.
    Writes docs/warren_clown/round_2.png. A fresh, uniquely-named renderer so it
    never overwrites an existing sheet (the round-10 caching lesson)."""
    SCALE = 2.4                            # show the hero VIEW_W x VIEW_H source large
    clown_w, clown_h = VIEW_W, VIEW_H
    disp_w = int(clown_w * SCALE)
    disp_h = int(clown_h * SCALE)

    cols = 5
    pad = 20
    head = 110
    name_strip = 34
    gap = 14

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R2_HEADERS[0][0], True, _CLOWN_R2_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R2_HEADERS[1][0], True, _CLOWN_R2_HEADERS[1][1]), (pad, 50))
    sheet.blit(sub_f.render(_CLOWN_R2_HEADERS[2][0], True, _CLOWN_R2_HEADERS[2][1]), (pad, 74))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    for idx, (name, kw, note) in enumerate(_CLOWN_R2_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        ntxt = name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255))
        strip.blit(ntxt, (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 20))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r2(idx, **kw)
        clown = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(clown, (10, 12, 18), clown.get_rect(), 2)
        sheet.blit(clown, (px, py + name_strip))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ════════════════════════════════════════════════════════════════════════════
#  WARREN CLOWN HERO LOOK-DEV — Round 3 (RE-ROLL staged from R2 #4 Slim Low Wrap)
# ════════════════════════════════════════════════════════════════════════════
# Round 2 read as TWO clowns because the marotte rendered at near-hero scale (a
# hero-size mini-jester head + a leg-wide shaft). Round 3 keeps prop_14n VERBATIM
# (same colors / geometry / head / lobes / rings / bell foot) and fixes the read
# by SCALE alone: it is rendered at its NATIVE ASPECT and scaled down UNIFORMLY so
# the bauble is FIST-SIZED (~the grip fist) and the shaft is a slim stick, never a
# barber-pole as wide as a leg. Shaft LENGTH is extended by rendering prop_14n into
# a TALLER source box (more shaft units) before the uniform down-scale — so length
# grows without the width ever widening. The whole prop stays one slim marotte the
# hero holds: total height ~1.2-1.4x the hero, bauble rising just over his head.
#
# Round 3 also restores the things round 2 dropped:
#   - the raised LEFT arm is build_jester's own raised arm (shoulder→elbow→open
#     mitt), reaching UP to MEET the die — the die is seated ON the open palm with
#     a pinch over it, so contact is legible (the floating glow halo is kept),
#   - the grip hand is a COMPACT real-finger fist (palm + knuckle ridges + thumb),
#     not the round-2 white blob, placed on the shaft body well below the lobes,
#   - the face is SOFTENED toward friendly-casual (round eyes, lifted smile, no
#     fang, no red dimple-drip) via build_jester's soft_face path,
#   - the curl-toe bell slippers are build_jester's own — unchanged.


def _held_marotte_surface(total_px, bauble_px, draw_fn=prop_14n):
    """Render prop_14n VERBATIM at its NATIVE ASPECT, then scale the whole prop
    down UNIFORMLY so it reads as a slim HELD marotte beside the hero rather than a
    second full clown. `bauble_px` is the target display diameter of the lobed head
    (sized to the grip fist); `total_px` is the target display height foot-to-head.

    The prop's head is authored at radius 13 in a box 82 wide, so a uniform scale
    f = bauble_px / 26 maps the head to `bauble_px` and the shaft to its NATIVE
    fraction of that — proportions untouched. Shaft LENGTH is set by the SOURCE box
    height H = total_px / f (taller box = more shaft units), so length grows with
    NO change to the prop's width or head. Returns (surface, w, h) at display px."""
    f = bauble_px / 26.0                   # head 26 source-units → bauble_px display
    p_ss = 6
    H = max(1, int(round(total_px / f)))   # source box height in true px (pre-ss)
    surf, bw, bh = _box(H, p_ss)
    draw_fn(surf, bw, bh, p_ss)            # VERBATIM — no geometry/colour touched
    disp_w = max(1, int(round((PIPE_W + 2 * OVERHANG) * f)))
    disp_h = max(1, int(round(H * f)))
    return pygame.transform.smoothscale(surf, (disp_w, disp_h)), disp_w, disp_h


def _r3_grip_fist(surf, hand, glove, *, fingers, side=1):
    """A COMPACT real-finger fist wrapping the slim shaft: a palm block, ~3 stacked
    knuckle ridges cresting the back of the hand, and a thumb wrapping the FRONT, so
    it reads as fingers gripping a stick — not a featureless snowball (round-2) nor
    fat sausage digits (round-1). ~15-17px wide at hero scale.

    `fingers` only restyles the FRONT digits so the five variants differ in finger
    read alone, never in scale:
      - "curl"   : three soft rounded finger-tips curling over the shaft front,
      - "ridged" : three crisp knuckle ridges with shaded grooves between,
      - "wrapped": a smooth banded wrap with a single knuckle crease (minimal)."""
    hx, hy = int(hand[0]), int(hand[1])
    dk = _shade_c(glove, -55)
    mid = _shade_c(glove, -22)
    hi = _shade_c(glove, 38)
    # Palm block: a compact rounded fist body, a touch wider than tall so it reads
    # as a closed hand clamping the pole rather than a ball stuck to it.
    palm = pygame.Rect(0, 0, 16, 13)
    palm.center = (hx, hy + 1)
    pygame.draw.rect(surf, dk, palm, border_radius=5)
    pygame.draw.rect(surf, glove, palm.inflate(-2, -2), border_radius=4)
    # Back-of-hand KNUCKLE RIDGES cresting the top of the wrap (shaft passes behind
    # them) — three small stacked bumps so the top of the fist reads as knuckles.
    for k in (-1, 0, 1):
        bx = hx + k * 4
        by = hy - 6
        pygame.draw.circle(surf, dk, (bx, by), 3)
        pygame.draw.circle(surf, mid, (bx, by), 2)
    # FRONT fingers crossing the shaft, styled per variant — all small + compact.
    if fingers == "curl":
        for fx in (hx - 4, hx, hx + 4):
            pygame.draw.circle(surf, dk, (fx, hy + 5), 3)
            pygame.draw.circle(surf, glove, (fx, hy + 5), 2)
    elif fingers == "ridged":
        for fx in (hx - 5, hx - 1, hx + 3):
            pygame.draw.line(surf, dk, (fx, hy - 1), (fx, hy + 6), 2)
            pygame.draw.line(surf, hi, (fx + 1, hy), (fx + 1, hy + 5), 1)
    else:  # "wrapped"
        pygame.draw.line(surf, dk, (hx - 6, hy + 4), (hx + 6, hy + 4), 1)
        pygame.draw.line(surf, mid, (hx - 6, hy + 1), (hx + 6, hy + 1), 1)
    # THUMB wrapping the front on the inner side — a nub + nail crease, so a real
    # opposed thumb crosses the shaft in front of the fingers.
    tx = hx - side * 7
    pygame.draw.circle(surf, dk, (tx, hy + 2), 4)
    pygame.draw.circle(surf, glove, (tx, hy + 2), 3)
    pygame.draw.line(surf, dk, (tx, hy), (tx, hy + 4), 1)
    # Top-left palm sheen + a crisp keyline so the fist lifts off shaft + sky.
    pygame.draw.circle(surf, hi, (hx - 3, hy - 1), 2)
    pygame.draw.rect(surf, dk, palm, border_radius=5, width=1)


def render_clown_staff_r3(idx, *, total_px, bauble_px, grip_frac, reach, fingers):
    """Round-3 hero panel staged from R2 #4 (Slim Low Wrap): the REAL build_jester
    clown holding prop_14n VERBATIM at proper HELD-MAROTTE scale. The raised LEFT
    arm is build_jester's own raised arm, re-targeted so its open mitt MEETS the
    floating die. Variants differ ONLY in the four allowed axes — finger style,
    grip height on the shaft, shaft length, raised-arm extension. Returns a
    VIEW_W x VIEW_H surface (the approved hero canvas)."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    spec["soft_face"] = True               # friendly-casual read for the held hero
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 6
    feet_y = VIEW_FEET_Y

    # The die is presented UP and OUT on the die side; `reach` lifts it so the LEFT
    # arm extends to a clearly LONG reach (visibly longer than the grip arm). We aim
    # build_jester's raised hand AT the die so the open mitt MEETS it (round 2 left
    # the die floating with no arm). The die sits up-and-LEFT, clear of the head, so
    # the raised forearm reads in full silhouette against the sky before the die.
    die_x = jester_cx - 54
    die_cy = 56 - reach                    # die centre height (the glow halo bobs it)
    hand_up = (die_x + 6, die_cy + 12)     # open mitt just under the die, touching it
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # --- prop_14n at HELD-MAROTTE scale, stood foot-on-ground beside the clown ----
    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7                               # the relaxed cane lean (top toward clown)
    rotated = pygame.transform.rotate(prop, rot)
    foot_local = (p_w / 2, p_h - 2)
    cxr, cyr = p_w / 2, p_h / 2
    rad = math.radians(rot)
    dx = foot_local[0] - cxr
    dy = foot_local[1] - cyr
    rfx = cxr + (dx * math.cos(rad) + dy * math.sin(rad))
    rfy = cyr + (-dx * math.sin(rad) + dy * math.cos(rad))
    rfx += (rotated.get_width() - p_w) / 2
    rfy += (rotated.get_height() - p_h) / 2
    plant_x = jester_cx + 34
    plant_y = ground_y - 1
    prop_ox = int(plant_x - rfx)
    prop_oy = int(plant_y - rfy)
    layer.blit(rotated, (prop_ox, prop_oy))

    # The grip point on the slim shaft BODY, well below the lobed head (>= ~2 bauble
    # diameters of clearance), mapped through the rotation + blit offset.
    grip_local = (p_w / 2, p_h * grip_frac)
    gdx = grip_local[0] - cxr
    gdy = grip_local[1] - cyr
    rgx = cxr + (gdx * math.cos(rad) + gdy * math.sin(rad))
    rgy = cyr + (-gdx * math.sin(rad) + gdy * math.cos(rad))
    rgx += (rotated.get_width() - p_w) / 2
    rgy += (rotated.get_height() - p_h) / 2
    grip_x = prop_ox + rgx
    grip_y = prop_oy + rgy

    # --- re-pose the near/lower arm onto the grip + lay the COMPACT real-finger fist
    # build_jester already painted a default down arm into the hip; redraw the limb
    # OVER it with the figure's own _arm kit, then a compact fist wraps the shaft.
    r_sh = (hip_cx + 25, hip_y - 50)
    grip_hand = (int(grip_x), int(grip_y))
    light = spec["light"]
    _arm(layer, r_sh, grip_hand, 8, light)
    _r3_grip_fist(layer, grip_hand, (250, 250, 252), fingers=fingers, side=1)

    # --- the floating power-up die, seated ON the raised open palm (legible contact)
    # Drawn AFTER the arm so the open mitt reads tucked just under the die; the die's
    # own glow halo (the on-brand power-up tell) is kept by draw_cupped_die.
    pulse = idx * 1.7 + 2.0
    draw_cupped_die(layer, die_x, die_cy, pulse, show_inset=(idx % 5 == 0))
    # A small pinch over the die so the raised hand visibly HOLDS it, not just hovers
    # beneath — two fingertip nubs cresting the top-right edge of the cube (toward
    # the arm), reading as thumb + finger pinching the floating power-up.
    for fx in (die_x + 8, die_x + 16):
        pygame.draw.circle(layer, _shade_c((250, 250, 252), -55), (fx, die_cy - 12), 3)
        pygame.draw.circle(layer, (250, 250, 252), (fx, die_cy - 12), 2)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Five FULL clown-with-staff variants — SAME real hero clown + SAME prop_14n at
# held-marotte scale; they vary ONLY: grip-fist finger style, grip height on the
# shaft, shaft length, and raised-arm extension. All staged from R2 #4 Slim Low Wrap.
_CLOWN_R3_VARIANTS = [
    ("Slim Low Curl",   dict(total_px=224, bauble_px=16, grip_frac=0.56, reach=8,
                             fingers="curl"),
     "R2#4 base · slim long shaft, low fist, three curled fingers, mid reach"),
    ("Slim Low Ridged", dict(total_px=224, bauble_px=16, grip_frac=0.58, reach=12,
                             fingers="ridged"),
     "slim long shaft, lower fist, crisp knuckle ridges, longer reach"),
    ("Tall Mid Wrapped", dict(total_px=238, bauble_px=15, grip_frac=0.50, reach=14,
                              fingers="wrapped"),
     "tallest slim shaft, mid fist, smooth wrap, longest reach"),
    ("Short Low Curl",  dict(total_px=212, bauble_px=17, grip_frac=0.60, reach=6,
                             fingers="curl"),
     "shorter shaft + slightly bigger bauble, lowest fist, curled fingers"),
    ("Mid High Ridged", dict(total_px=228, bauble_px=16, grip_frac=0.46, reach=16,
                             fingers="ridged"),
     "slim shaft, upper-mid fist, knuckle ridges, tallest die present"),
]


_CLOWN_R3_HEADERS = [
    ("Warren Clown HERO look-dev — Round 3 (RE-ROLL from R2 #4 · FULL clown holding prop_14n at HELD-MAROTTE scale)",
     (255, 255, 255)),
    ("prop_14n VERBATIM but scaled to a SLIM HELD marotte (bauble FIST-sized, shaft a slim stick, never a 2nd clown). "
     "Raised LEFT arm RESTORED — build_jester's own arm reaches UP and MEETS the die (pinched over an open palm).",
     (205, 210, 220)),
    ("Variants vary ONLY: grip-fist fingers · grip height · shaft length · raised-arm reach. Compact real-finger grip "
     "fist; softened friendly face (round eyes, lifted smile, no fang/drip); curl-toe bell slippers kept.",
     (170, 178, 190)),
]


def _render_clown_r3_sheet():
    """Round-3 clown look-dev sheet: a 1-row strip of the five FULL clown-holding-
    marotte variants at hero scale, each labelled with what differs. Writes
    docs/warren_clown/round_3.png. Uniquely named so it never overwrites a sheet."""
    SCALE = 2.4                            # show the hero VIEW_W x VIEW_H source large
    clown_w, clown_h = VIEW_W, VIEW_H
    disp_w = int(clown_w * SCALE)
    disp_h = int(clown_h * SCALE)

    cols = 5
    pad = 20
    head = 110
    name_strip = 34
    gap = 14

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R3_HEADERS[0][0], True, _CLOWN_R3_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R3_HEADERS[1][0], True, _CLOWN_R3_HEADERS[1][1]), (pad, 50))
    sheet.blit(sub_f.render(_CLOWN_R3_HEADERS[2][0], True, _CLOWN_R3_HEADERS[2][1]), (pad, 74))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    for idx, (name, kw, note) in enumerate(_CLOWN_R3_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        ntxt = name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255))
        strip.blit(ntxt, (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 20))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r3(idx, **kw)
        clown = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(clown, (10, 12, 18), clown.get_rect(), 2)
        sheet.blit(clown, (px, py + name_strip))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ════════════════════════════════════════════════════════════════════════════
#  ROUND 4 — FINAL clown-with-marotte pass (builds on round 3; never overwrites
#  round_3.png). The gameplay-scale silhouette (one clown + one slim stick) is
#  CORRECT and HELD — round 3 nailed it; this round only folds in the art-
#  director's pixel-level punch list on top of the round-3 staging:
#    1. SELL THE DIE-CONTACT — the raised forearm ends in a readable OPEN GLOVE
#       BLOCK (not a thin nub), and the big held die OVERLAPS that hand by a few
#       px so it reads as held/balanced with ZERO sky gap above the hand.
#    2. REMOVE the staff-cap mini-die topper — the round-3 die's roll-result
#       inset ("27") read as a second die capping the prop behind the jester-head
#       finial; r4 never shows it (one big held die + one jester-head finial).
#    3/4. ROUNDER eyes + a TAMED grin via render_jester_variants' deeper _R4_SOFT
#       tier (flipped on only for the duration of this render so the ten power-up
#       presenters and the round-3 sheet render unchanged).
#    5. The raised forearm holds a consistent width into the wrist (no tentacle
#       neck-down) because r4 draws its OWN raised arm with a flat-width forearm.
#  HOLD verbatim from round 3: the grip fist (_r3_grip_fist), the held-marotte
#  scale + slim shaft (_held_marotte_surface / prop_14n), grip placement below the
#  lobes, curl-toe bell slippers, palette, the 5-variant axis structure.

import tools.render_jester_variants as _rjv  # noqa: E402  toggle the deep-soft face tier


def _r4_raised_arm_and_hand(surf, shoulder, hand, w, glove):
    """The raised presenting arm, drawn with a CONSISTENT forearm width into the
    wrist (round 3's `_arm` necked the forearm down to a thin nub before the hand,
    reading as a tentacle). The limb keeps ~full width through the elbow and only
    eases to ~2/3 width at the wrist, then ends in a small OPEN GLOVE BLOCK — the
    flat-topped open hand the die rests ON. Same white as the grip fist so the two
    hands read as one pair. Returns the open-hand top-centre (where the die seats).

    The open hand is a small rounded block (not a round ball + nub) so the die's
    bottom-back corner can OVERLAP it cleanly with no sky gap — the contact the
    art-director wanted sold."""
    dk = _shade_c(glove, -55)
    mid = _shade_c(glove, -22)
    sh = (int(shoulder[0]), int(shoulder[1]))
    hd = (int(hand[0]), int(hand[1]))
    # Elbow bend (slight) so the limb reads as a real arm reaching up.
    mx = (sh[0] + hd[0]) // 2
    my = (sh[1] + hd[1]) // 2 - 3
    # Upper arm at full width, forearm only eases to ~2/3 (never a point).
    pygame.draw.line(surf, dk, sh, (mx, my), w + 3)
    pygame.draw.line(surf, dk, (mx, my), hd, w + 1)
    pygame.draw.line(surf, glove, sh, (mx, my), w)
    pygame.draw.line(surf, glove, (mx, my), hd, max(3, int(w * 0.7)))
    pygame.draw.circle(surf, mid, (mx, my), w // 2 + 1)   # rounded elbow
    # OPEN GLOVE BLOCK at the wrist: a small flat-topped rounded hand, ~2-3px of
    # readable open palm, the die balanced on its top edge.
    hand_w, hand_h = 13, 10
    block = pygame.Rect(0, 0, hand_w, hand_h)
    block.center = (hd[0], hd[1])
    pygame.draw.rect(surf, dk, block, border_radius=4)
    pygame.draw.rect(surf, glove, block.inflate(-2, -2), border_radius=3)
    # Three short open fingertips cresting the flat top — the OPEN palm presenting
    # the die (reads as fingers cupping under it, not a closed fist).
    for k in (-1, 0, 1):
        fx = hd[0] + k * 4
        pygame.draw.circle(surf, dk, (fx, block.top - 1), 3)
        pygame.draw.circle(surf, glove, (fx, block.top - 1), 2)
    # A thumb nub on the inner side + a top-left sheen so the open hand reads lit.
    pygame.draw.circle(surf, dk, (hd[0] + hand_w // 2, hd[1]), 3)
    pygame.draw.circle(surf, glove, (hd[0] + hand_w // 2, hd[1]), 2)
    pygame.draw.circle(surf, _shade_c(glove, 38), (hd[0] - 3, hd[1] - 2), 2)
    return (hd[0], block.top - 3)             # top-centre of the open palm


def render_clown_staff_r4(idx, *, total_px, bauble_px, grip_frac, reach, fingers,
                          die_dx=0):
    """Round-4 hero panel — round 3's exact staging with the punch list folded in.
    The held-marotte prop, the grip fist, the lean, slippers + palette are KEPT
    verbatim; only the raised arm / die contact / face soft-tier / mini-die topper
    change. `die_dx` nudges the die inboard toward the fingertips (V5 needs this so
    the outward arm angle doesn't reopen a gap). Returns a VIEW_W x VIEW_H surface."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    spec["soft_face"] = True               # friendly-casual read for the held hero
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 6
    feet_y = VIEW_FEET_Y

    # Die seat. `die_dx` brings it inboard toward the open hand (V5). build_jester
    # paints its own default raised arm; r4 redraws the raised arm OVER it so the
    # forearm keeps a real width and ends in the open glove block under the die.
    die_x = jester_cx - 54 + die_dx
    die_cy = 56 - reach                    # die centre height (the glow halo bobs it)
    hand_up = (die_x + 6, die_cy + 12)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # --- prop_14n at HELD-MAROTTE scale, stood foot-on-ground beside the clown ----
    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7                               # the relaxed cane lean (top toward clown)
    rotated = pygame.transform.rotate(prop, rot)
    foot_local = (p_w / 2, p_h - 2)
    cxr, cyr = p_w / 2, p_h / 2
    rad = math.radians(rot)
    dx = foot_local[0] - cxr
    dy = foot_local[1] - cyr
    rfx = cxr + (dx * math.cos(rad) + dy * math.sin(rad))
    rfy = cyr + (-dx * math.sin(rad) + dy * math.cos(rad))
    rfx += (rotated.get_width() - p_w) / 2
    rfy += (rotated.get_height() - p_h) / 2
    plant_x = jester_cx + 34
    plant_y = ground_y - 1
    prop_ox = int(plant_x - rfx)
    prop_oy = int(plant_y - rfy)
    layer.blit(rotated, (prop_ox, prop_oy))

    # The grip point on the slim shaft BODY, well below the lobed head (KEPT from r3).
    grip_local = (p_w / 2, p_h * grip_frac)
    gdx = grip_local[0] - cxr
    gdy = grip_local[1] - cyr
    rgx = cxr + (gdx * math.cos(rad) + gdy * math.sin(rad))
    rgy = cyr + (-gdx * math.sin(rad) + gdy * math.cos(rad))
    rgx += (rotated.get_width() - p_w) / 2
    rgy += (rotated.get_height() - p_h) / 2
    grip_x = prop_ox + rgx
    grip_y = prop_oy + rgy

    # --- the near/lower arm onto the grip + the COMPACT real-finger fist (r3, KEPT)
    r_sh = (hip_cx + 25, hip_y - 50)
    grip_hand = (int(grip_x), int(grip_y))
    light = spec["light"]
    _arm(layer, r_sh, grip_hand, 8, light)
    _r3_grip_fist(layer, grip_hand, (250, 250, 252), fingers=fingers, side=1)

    # --- the RAISED arm + OPEN HAND under the die (punch list #1 + #5) ------------
    # The raised hand is aimed just below where the die's bottom-back corner will
    # land; the die is then drawn so that corner OVERLAPS the open palm — no sky gap.
    l_sh = (jester_cx - 18, hip_y - 54)
    palm_top = _r4_raised_arm_and_hand(layer, l_sh, hand_up, 8, (250, 250, 252))

    # --- the floating power-up die, its bottom-back corner OVERLAPPING the palm ---
    # NEVER show the roll-result inset ("27") — that read as a second mini-die cap
    # behind the jester-head finial (punch list #2). The die's own glow halo stays.
    # Seat the die so its lowest cube corner sits ~3-4px BELOW the open palm top,
    # i.e. the die overlaps the hand (held/balanced), eliminating the round-3 gap.
    die_seat_cy = palm_top[1] - 14         # cube bottom-front ≈ die_cy + 22; overlap ~4px
    draw_cupped_die(layer, die_x, die_seat_cy, idx * 1.7 + 2.0, show_inset=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Five FINAL clown-with-marotte variants — SAME real hero clown + SAME prop_14n at
# held-marotte scale + SAME grip fist; they vary ONLY: grip-fist finger style, grip
# height on the shaft, shaft length, and raised-arm reach. V3 (Tall Mid Wrapped) is
# the art-director's ship pick and is tuned as the strongest panel.
_CLOWN_R4_VARIANTS = [
    ("Slim Mid Curl",   dict(total_px=224, bauble_px=16, grip_frac=0.50, reach=8,
                             fingers="curl"),
     "slim long shaft, fist RAISED ~10px (grip arm reads full), three curled fingers"),
    ("Slim Mid Ridged", dict(total_px=224, bauble_px=16, grip_frac=0.50, reach=12,
                             fingers="ridged"),
     "twin of V1 but DEEPER knuckle ridges to distinguish it, longer reach"),
    ("Tall Mid Wrapped", dict(total_px=238, bauble_px=15, grip_frac=0.48, reach=15,
                              fingers="wrapped"),
     "LEAD · tallest slim shaft, high reach, smooth wrap, warm tamed smile"),
    ("Mid Low Curl",    dict(total_px=222, bauble_px=16, grip_frac=0.56, reach=7,
                             fingers="curl"),
     "shaft lengthened + bauble shrunk toward the others, low fist, curled fingers"),
    ("Mid High Ridged", dict(total_px=228, bauble_px=16, grip_frac=0.46, reach=16,
                             fingers="ridged", die_dx=10),
     "knuckle ridges, tallest die present, die brought INBOARD to close the gap"),
]


_CLOWN_R4_HEADERS = [
    ("Warren Clown HERO look-dev — Round 4 (FINAL · folds the art-director punch list onto round 3's held-marotte staging)",
     (255, 255, 255)),
    ("Die-CONTACT sold: the raised forearm ends in an OPEN GLOVE BLOCK and the big held die OVERLAPS it (zero sky gap). "
     "Staff-cap mini-die topper REMOVED — one big held die + one jester-head finial only.",
     (205, 210, 220)),
    ("Rounder friendly eyes (soft dark disc + 1px catch-light, ~30% less brow/lash) + a tamed warm grin. Grip fist, "
     "held-marotte scale, grip placement, curl-toe bell slippers KEPT verbatim from round 3. Lead = V3 Tall Mid Wrapped.",
     (170, 178, 190)),
]


def _render_clown_r4_sheet():
    """Round-4 clown look-dev sheet: a 1-row strip of the five FINAL clown-holding-
    marotte variants at hero scale. Writes docs/warren_clown/round_4.png. The deep
    _R4_SOFT face tier is flipped ON only for the duration of this render so other
    renders (the ten presenters, round 3) are unaffected."""
    SCALE = 2.4
    clown_w, clown_h = VIEW_W, VIEW_H
    disp_w = int(clown_w * SCALE)
    disp_h = int(clown_h * SCALE)

    cols = 5
    pad = 20
    head = 110
    name_strip = 34
    gap = 14

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R4_HEADERS[0][0], True, _CLOWN_R4_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R4_HEADERS[1][0], True, _CLOWN_R4_HEADERS[1][1]), (pad, 50))
    sheet.blit(sub_f.render(_CLOWN_R4_HEADERS[2][0], True, _CLOWN_R4_HEADERS[2][1]), (pad, 74))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    prev = _rjv._R4_SOFT
    _rjv._R4_SOFT = True                   # deep friendly-mascot face for this sheet only
    try:
        for idx, (name, kw, note) in enumerate(_CLOWN_R4_VARIANTS):
            px = pad + idx * (cell_w + gap)
            py = head

            strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
            strip.fill((18, 20, 28, 220))
            ntxt = name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255))
            strip.blit(ntxt, (8, 4))
            strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 20))
            sheet.blit(strip, (px, py))

            clown = render_clown_staff_r4(idx, **kw)
            clown = pygame.transform.smoothscale(clown, (disp_w, disp_h))
            pygame.draw.rect(clown, (10, 12, 18), clown.get_rect(), 2)
            sheet.blit(clown, (px, py + name_strip))
    finally:
        _rjv._R4_SOFT = prev

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_4.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


def render_clown_staff_final(idx, *, total_px, bauble_px, fingers):
    """The corrected held-marotte hero panel: the EXACT in-game clown
    (`build_jester` with warren_demo's own `hand_up` reach — its raised LEFT arm
    presenting the die and its single down RIGHT arm) with the staff placed INTO
    that existing right hand. No extra arm is ever drawn, so there is exactly one
    arm per side; the marotte's shaft simply passes through the down hand and the
    compact grip fist is drawn over the figure's own mitt. The only authored
    changes vs the in-game figure are the held staff and that grip fist."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    # EXACT in-game raised-arm reach (warren_demo: hand_up = cx-60, feet-154) so the
    # left arm matches the deployed clown rather than a shorter, stubbier reach.
    hand_up = (jester_cx - 60, feet_y - 154)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # build_jester's OWN down RIGHT hand (baked geometry) — the staff is seated into
    # it; we never add a second arm. The shaft passes through this point and the
    # grip fist is drawn over the figure's default mitt.
    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    # prop_14n at HELD-MAROTTE scale. grip_frac is DERIVED so the bell foot rests on
    # the ground while the grip sits in the existing hand — `total_px` (the length)
    # then governs only how far the bauble rises above the hand.
    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)
    layer.blit(rotated, (prop_ox, prop_oy))

    # The compact real-finger fist over the figure's own mitt (matches the down
    # hand's thumb side), so the existing hand reads as gripping the shaft.
    _r3_grip_fist(layer, (int(r_hand[0]), int(r_hand[1])), (250, 250, 252),
                  fingers=fingers, side=-1)

    # The floating power-up die presented just beyond the extended raised hand (no
    # roll-result inset). Its aura reads it as an airborne pickup, not a held prop.
    draw_cupped_die(layer, jester_cx - 56, 30, idx * 1.7 + 2.0, show_inset=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Five PICK options on the corrected staging — the SAME canonical hero clown (its
# own untouched face + its own raised presenting arm), differing only in the two
# requested axes: staff LENGTH (held-marotte scale) and the grip-fist finger style
# / grip height on the shaft.
_CLOWN_FINAL_VARIANTS = [
    ("Short · Curl",   dict(total_px=150, bauble_px=16, fingers="curl"),
     "short marotte, bauble just above the hand, three curled fingers"),
    ("Medium · Ridged", dict(total_px=176, bauble_px=16, fingers="ridged"),
     "medium shaft, crisp knuckle ridges"),
    ("Tall · Wrapped",  dict(total_px=200, bauble_px=15, fingers="wrapped"),
     "tall slim shaft, smooth banded wrap"),
    ("Tall · Curl",    dict(total_px=224, bauble_px=15, fingers="curl"),
     "tall slim shaft, curled fingers"),
    ("X-Tall · Ridged", dict(total_px=246, bauble_px=15, fingers="ridged"),
     "longest slim shaft, bauble well above the head, knuckle ridges"),
]


_CLOWN_FINAL_HEADERS = [
    ("Warren Clown HERO look-dev — CORRECTED (canonical clown, untouched face + its own single raised arm)",
     (255, 255, 255)),
    ("Reverted the unrequested face change and removed the duplicate raised arm that crossed the face. "
     "ONE raised presenting arm + ONE grip hand. Only the staff LENGTH and the grip-fist fingers vary below — PICK ONE.",
     (205, 210, 220)),
]


def _render_clown_final_sheet():
    """Corrected clown look-dev sheet: a 1-row strip of five clown-holding-marotte
    PICK options at hero scale. Writes docs/warren_clown/round_5.png. No soft-face
    tier is touched — the canonical hero face renders exactly as shipped."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = 5
    pad = 20
    head = 86
    name_strip = 34
    gap = 14

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_FINAL_HEADERS[0][0], True, _CLOWN_FINAL_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_FINAL_HEADERS[1][0], True, _CLOWN_FINAL_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    for idx, (name, kw, note) in enumerate(_CLOWN_FINAL_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 20))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_final(idx, **kw)
        clown = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(clown, (10, 12, 18), clown.get_rect(), 2)
        sheet.blit(clown, (px, py + name_strip))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_5.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ── Round-6 DETAILED HANDS look-dev ───────────────────────────────────────────
#  The round-5 held-marotte hero is approved; the ONLY open note was that the
#  clown's HANDS read under-detailed. These primitives reintroduce the proven
#  round-1 palm+finger kit, COMPACTED ~35% (finger w 3-4 / len 8-12, palm r 6-7)
#  so a real open offering hand and a real wrapping grip read at hero scale
#  without ever bulking past the ~16px mitt the art-director sized us to. The
#  detail is in CREASES + KEYLINES + OCCLUSION, never in size.

_R6_GLOVE = (250, 250, 252)
_R6_GLOVE_DK = _shade(_R6_GLOVE, -58)
_R6_GLOVE_MD = _shade(_R6_GLOVE, -26)
_R6_GLOVE_HI = (255, 255, 255)


def _r6_finger(surf, base, tip, w, *, crease=True):
    """One rounded finger capsule from knuckle `base` to `tip`, keylined with a
    top-left sheen and a soft mid crease so it reads as a digit, not a stripe.
    Digit definition is carried by the keyline + crease, so it survives the
    compact widths (3-4px) the hero scale demands."""
    pygame.draw.line(surf, _R6_GLOVE_DK, base, tip, w + 2)
    pygame.draw.line(surf, _R6_GLOVE, base, tip, w)
    pygame.draw.circle(surf, _R6_GLOVE, tip, max(1, w // 2))
    pygame.draw.circle(surf, _R6_GLOVE_DK, tip, max(1, w // 2), 1)
    pygame.draw.line(surf, _R6_GLOVE_HI,
                     (base[0] - 1, base[1] - 1), (tip[0] - 1, tip[1] - 1),
                     max(1, w // 3))
    if crease:
        mx = (base[0] + tip[0]) // 2
        my = (base[1] + tip[1]) // 2
        pygame.draw.line(surf, _R6_GLOVE_MD, (mx - w // 3, my), (mx + w // 3, my), 1)


def _r6_palm(surf, cx, cy, rx, ry):
    """The rounded palm mass: dark keyline ellipse + glove fill + a soft top-left
    alpha sheen so the palm reads round and lifts off the shaft / sky."""
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, _R6_GLOVE_DK, rect)
    pygame.draw.ellipse(surf, _R6_GLOVE, rect.inflate(-2, -2))
    sheen = pygame.Surface((rx, ry), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 90), sheen.get_rect())
    surf.blit(sheen, (cx - rx + 1, cy - ry + 1))


# OPEN presenting hands — palm tipped up under the floating die, fingers spread.
# Each treatment carries its own finger grammar; all stay inside a ~16px box.

def _r6_open_realistic(surf, hand):
    """Slim separated fingers + an opposed thumb fanned over a compact palm."""
    hx, hy = hand
    _r6_palm(surf, hx, hy, 7, 6)
    for i, ang in enumerate((-58, -30, -6, 18)):
        a = math.radians(ang - 90)
        ln = 10 - abs(i - 1)             # middle pair longest, outers shorter
        tip = (hx + int(math.cos(a) * ln), hy + int(math.sin(a) * ln))
        _r6_finger(surf, (hx, hy - 2), tip, 3)
    _r6_finger(surf, (hx - 3, hy + 3), (hx - 9, hy + 4), 4, crease=False)


def _r6_open_mascot(surf, hand):
    """Three plump gloved fingers + a fat thumb, with bold dark Mickey-glove
    seams splitting them — read-at-a-glance toon hand, still compact."""
    hx, hy = hand
    _r6_palm(surf, hx, hy, 7, 6)
    for ang in (-52, -18, 16):
        a = math.radians(ang - 90)
        tip = (hx + int(math.cos(a) * 9), hy + int(math.sin(a) * 9))
        _r6_finger(surf, (hx, hy - 1), tip, 4)
    _r6_finger(surf, (hx - 4, hy + 3), (hx - 10, hy + 5), 5, crease=False)
    for ang in (-35, 0):
        a = math.radians(ang - 90)
        ex = hx + int(math.cos(a) * 8)
        ey = hy + int(math.sin(a) * 8)
        pygame.draw.line(surf, _R6_GLOVE_DK, (hx, hy), (ex, ey), 2)


def _r6_open_elegant(surf, hand):
    """Long-ish slender tapered fingers off a refined oval palm, each carrying a
    base knuckle crease so the hand reads poised and articulated, not stiff."""
    hx, hy = hand
    _r6_palm(surf, hx, hy, 6, 7)
    for i, ang in enumerate((-64, -40, -16, 10)):
        a = math.radians(ang - 90)
        ln = 13 - abs(i - 1) * 2         # graceful long taper
        tip = (hx + int(math.cos(a) * ln), hy + int(math.sin(a) * ln))
        _r6_finger(surf, (hx, hy - 2), tip, 3)
        pygame.draw.circle(surf, _R6_GLOVE_MD,
                           (hx + int(math.cos(a) * 4), hy + int(math.sin(a) * 4)), 1)
    _r6_finger(surf, (hx - 3, hy + 2), (hx - 11, hy - 1), 4, crease=False)


# WRAP grips — drawn in TWO of the three z-passes here (the caller blits the
# shaft between them): `behind=True` paints the palm heel + back fingers BEFORE
# the shaft; `behind=False` paints the front fingertips + thumb crossing the
# shaft AFTER it. `shaft_w` is the shaft half-width so digits land ON the wood.

def _r6_wrap_realistic(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _r6_palm(surf, hx + 2, hy, 7, 6)
        for dy in (-5, -1, 3, 7):
            _r6_finger(surf, (hx + 5, hy + dy), (hx - shaft_w + 1, hy + dy), 3)
    else:
        for dy in (-3, 5):
            _r6_finger(surf, (hx + 5, hy + dy), (hx - shaft_w - 2, hy + dy), 3)
        _r6_finger(surf, (hx + 6, hy - 7), (hx - 2, hy - 8), 4, crease=False)


def _r6_wrap_mascot(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _r6_palm(surf, hx + 2, hy, 7, 6)
        for dy in (-4, 3, 9):
            _r6_finger(surf, (hx + 6, hy + dy), (hx - shaft_w + 1, hy + dy), 4)
    else:
        for dy in (-1, 7):
            _r6_finger(surf, (hx + 6, hy + dy), (hx - shaft_w - 2, hy + dy), 4)
        _r6_finger(surf, (hx + 7, hy - 7), (hx - 2, hy - 9), 5, crease=False)
        # A bold seam between the two front fingers for the toon glove read.
        pygame.draw.line(surf, _R6_GLOVE_DK, (hx - 1, hy - 3), (hx - shaft_w - 1, hy + 3), 2)


def _r6_wrap_elegant(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _r6_palm(surf, hx + 3, hy, 6, 7)
        for dy in (-6, -2, 2, 6):
            _r6_finger(surf, (hx + 4, hy + dy), (hx - shaft_w, hy + dy), 3)
    else:
        # A single long index + thumb cross in front — a light, poised rest.
        _r6_finger(surf, (hx + 5, hy + 1), (hx - shaft_w - 3, hy - 1), 3)
        _r6_finger(surf, (hx + 6, hy - 8), (hx - 2, hy - 10), 4, crease=False)


# The 3 matched-pair treatments: each maps a (open, wrap) drawing function pair.
_R6_HAND_KITS = {
    "realistic": (_r6_open_realistic, _r6_wrap_realistic),
    "mascot":    (_r6_open_mascot,    _r6_wrap_mascot),
    "elegant":   (_r6_open_elegant,   _r6_wrap_elegant),
}


def render_clown_staff_r6(idx, *, total_px, bauble_px, hands):
    """Round-6 hero panel: the approved round-5 held-marotte composition VERBATIM
    (exact in-game `build_jester`, marotte seated into the figure's own down hand,
    foot on ground, untouched hero face, one arm per side) with ONLY the two HANDS
    re-detailed. `hands` selects one of the three matched-pair treatments applied
    to BOTH the raised presenting hand (a local OVERDRAW over build_jester's plain
    mitt) and the staff-grip hand (a three-z-pass wrap around the shaft). The
    in-game clown is never touched — all detail lives in this look-dev overdraw."""
    open_fn, wrap_fn = _R6_HAND_KITS[hands]

    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    # EXACT in-game raised-arm reach (warren_demo: hand_up = cx-60, feet-154).
    hand_up = (jester_cx - 60, feet_y - 154)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # Detailed OPEN presenting hand drawn OVER build_jester's plain raised mitt —
    # palm + spread fingers + opposed thumb, tipped up so it cups under the die.
    open_fn(layer, hand_up)

    # build_jester's OWN down hand — the staff seats into it; we never add an arm.
    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    # THREE-Z-PASS grip so the wrap reads as a real grasp: palm heel + back
    # fingers BEHIND the shaft, then the shaft, then fingertips + thumb IN FRONT.
    # The slim held shaft is ~2px half-width at hero scale, so digits land on wood.
    shaft_w = 2
    wrap_fn(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    wrap_fn(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    # The floating power-up die presented just beyond the extended raised hand.
    draw_cupped_die(layer, jester_cx - 56, 30, idx * 1.7 + 2.0, show_inset=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# The staff is HELD CONSTANT (the Tall finalist) so the only variable across the
# three panels is the hand-detail treatment applied to BOTH hands as a pair.
_CLOWN_R6_VARIANTS = [
    ("Realistic", dict(total_px=200, bauble_px=15, hands="realistic"),
     "slim separated fingers + opposed thumb, compact anatomical"),
    ("Mascot", dict(total_px=200, bauble_px=15, hands="mascot"),
     "plump 3-finger gloved read with bold dark seams"),
    ("Elegant", dict(total_px=200, bauble_px=15, hands="elegant"),
     "long slender tapered fingers + refined oval palm + knuckle creases"),
]


_CLOWN_R6_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 6: DETAILED HANDS (staff held constant; hand detail is the only variable)",
     (255, 255, 255)),
    ("Round-5 hero approved. ONLY note: hands under-detailed. Both hands (raised presenting + staff grip) re-detailed, "
     "kept COMPACT (~16px). Three matched-pair treatments below — PICK ONE.",
     (205, 210, 220)),
]


def _render_clown_r6_sheet():
    """Round-6 clown look-dev: a 1-row strip of three hero panels that differ ONLY
    in the hand-detail treatment (the staff is the constant Tall finalist). Writes
    docs/warren_clown/round_6.png — never overwrites an existing round sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = 3
    pad = 20
    head = 86
    name_strip = 34
    gap = 14

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R6_HEADERS[0][0], True, _CLOWN_R6_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R6_HEADERS[1][0], True, _CLOWN_R6_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    for idx, (name, kw, note) in enumerate(_CLOWN_R6_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 20))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r6(idx, **kw)
        clown = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(clown, (10, 12, 18), clown.get_rect(), 2)
        sheet.blit(clown, (px, py + name_strip))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_6.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ── Round-7 DETAILED HANDS polish ─────────────────────────────────────────────
#  Round 6's three matched-pair hand treatments are right in spirit but got the
#  art-director note: at true 1x the digits merge into a mitt, the grip reads as
#  "beside" not "gripping", and the two gloves are uneven. Round 7 keeps the size
#  (~16px footprint is correct — never enlarge) and pushes legibility through
#  VALUE instead: a single TOP-LEFT rim on every digit, a macaw-matched 1px dark
#  keyline, a 1-shade-darker GROOVE in every inter-finger gap, and a darker
#  OCCLUSION band where the shaft passes behind the fingers so the wrap reads as
#  in-front/behind. The grips now show a real thumb crossing the FRONT of the
#  shaft plus fingertips peeking on the same side, so the grasp is shown.

_R7_GLOVE    = (250, 250, 252)
_R7_GROOVE   = _shade(_R7_GLOVE, -78)   # 1-shade-darker inter-finger groove
_R7_OCCLUDE  = _shade(_R7_GLOVE, -96)   # darkest: shaft-behind-fingers band
_R7_GLOVE_MD = _shade(_R7_GLOVE, -26)
_R7_GLOVE_HI = (255, 255, 255)

# Outline value matched to the shipped macaw/coin 1px hairline so the gloves sit
# naturally beside existing art; rim is ALWAYS top-left (-1,-1) for consistency.
_R7_OUTLINE  = (20, 12, 18)


def _r7_finger(surf, base, tip, w, *, crease=True, groove_above=False):
    """One rounded finger capsule, base→tip, with a macaw-weight dark keyline, a
    constant TOP-LEFT rim sheen, and an optional darker GROOVE skimming its upper
    edge so the negative space between adjacent fingers reads as a real gap even
    when the digits are only 3-4px wide at hero scale. `groove_above` paints that
    separating groove so neighbouring fingers never melt into one mitt."""
    # A darker separating groove laid just above this finger first, so the
    # finger's own keyline crisply overdraws its lower lip (value separation).
    if groove_above:
        pygame.draw.line(surf, _R7_GROOVE,
                         (base[0], base[1] - w // 2 - 1), (tip[0], tip[1] - w // 2 - 1),
                         max(1, w // 2))
    pygame.draw.line(surf, _R7_OUTLINE, base, tip, w + 2)   # macaw-weight keyline
    pygame.draw.line(surf, _R7_GLOVE, base, tip, w)
    pygame.draw.circle(surf, _R7_GLOVE, tip, max(1, w // 2))
    pygame.draw.circle(surf, _R7_OUTLINE, tip, max(1, w // 2), 1)
    pygame.draw.line(surf, _R7_GLOVE_HI,
                     (base[0] - 1, base[1] - 1), (tip[0] - 1, tip[1] - 1),
                     max(1, w // 3))                          # constant top-left rim
    if crease:
        mx = (base[0] + tip[0]) // 2
        my = (base[1] + tip[1]) // 2
        pygame.draw.line(surf, _R7_GLOVE_MD, (mx - w // 3, my), (mx + w // 3, my), 1)


def _r7_palm(surf, cx, cy, rx, ry):
    """Rounded palm mass: macaw-weight dark keyline ellipse + glove fill + a
    top-left alpha sheen so the palm reads round and lifts off the shaft / sky."""
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, _R7_OUTLINE, rect)
    pygame.draw.ellipse(surf, _R7_GLOVE, rect.inflate(-2, -2))
    sheen = pygame.Surface((rx, ry), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 90), sheen.get_rect())
    surf.blit(sheen, (cx - rx + 1, cy - ry + 1))


def _r7_occlusion(surf, hand, shaft_w):
    """The 1-shade-darker band painted on the shaft exactly where the front
    fingers will cross it, so the wood reads as passing BEHIND those digits
    rather than sitting beside the hand. Drawn after the shaft, before the
    front pass."""
    hx, hy = hand
    pygame.draw.line(surf, _R7_OCCLUDE,
                     (hx - shaft_w - 2, hy - 4), (hx - shaft_w - 2, hy + 8), shaft_w + 1)


# OPEN presenting hands — palm tipped up under the floating die, fingers spread.
# All stay inside the ~16px box; legibility comes from grooves + rim, not size.

def _r7_open_realistic(surf, hand):
    """Slim separated fingers + an opposed thumb over a compact palm. Each finger
    carries a darker groove above it so the inter-finger negative space stays a
    crisp ≥1px gap at 1x instead of fusing into a mitt."""
    hx, hy = hand
    _r7_palm(surf, hx, hy, 7, 6)
    # Wider angular spread than r6 (-64..28 vs -58..18) so gaps open up; the
    # groove rides above each digit to value-separate adjacent fingers.
    for i, ang in enumerate((-64, -34, -4, 28)):
        a = math.radians(ang - 90)
        ln = 10 - abs(i - 1)             # middle pair longest, outers shorter
        tip = (hx + int(math.cos(a) * ln), hy + int(math.sin(a) * ln))
        _r7_finger(surf, (hx, hy - 2), tip, 3, groove_above=(i > 0))
    # KEEP the convincing r6 thumb placement/angle on the raised hand.
    _r7_finger(surf, (hx - 3, hy + 3), (hx - 9, hy + 4), 4, crease=False)


def _r7_open_mascot(surf, hand):
    """Three plump gloved fingers + a fat thumb, with bold dark Mickey-glove
    seams. EQUALIZED to the grip hand: same finger width (4) and the same 4-seam
    grammar (3 inter-finger + 1 thumb split) so both gloves match in mass."""
    hx, hy = hand
    _r7_palm(surf, hx, hy, 7, 6)
    for ang in (-52, -18, 16):
        a = math.radians(ang - 90)
        tip = (hx + int(math.cos(a) * 9), hy + int(math.sin(a) * 9))
        _r7_finger(surf, (hx, hy - 1), tip, 4)
    _r7_finger(surf, (hx - 4, hy + 3), (hx - 10, hy + 5), 4, crease=False)
    # Four bold glove seams (one per finger) — the toon read, matched to the grip.
    for ang in (-52, -18, 16):
        a = math.radians(ang - 90)
        ex = hx + int(math.cos(a) * 8)
        ey = hy + int(math.sin(a) * 8)
        pygame.draw.line(surf, _R7_GROOVE, (hx, hy), (ex, ey), 2)
    pygame.draw.line(surf, _R7_GROOVE, (hx - 2, hy + 2), (hx - 8, hy + 4), 2)


def _r7_open_elegant(surf, hand):
    """Refined oval palm + slender tapered fingers, but SHORTENED ~28% from r6 so
    the hand returns to the ~16px mitt footprint, dropped to THREE fingers with
    wider gaps for clean 1x legibility, each with a base knuckle crease."""
    hx, hy = hand
    _r7_palm(surf, hx, hy, 6, 7)
    # Three fingers (r6 had four) at a wider spread, lengths cut ~28% (was 13/11).
    for i, ang in enumerate((-60, -26, 12)):
        a = math.radians(ang - 90)
        ln = 9 - (1 if i == 1 else 0)    # gentle taper, all short
        tip = (hx + int(math.cos(a) * ln), hy + int(math.sin(a) * ln))
        _r7_finger(surf, (hx, hy - 2), tip, 3, groove_above=(i > 0))
        pygame.draw.circle(surf, _R7_GLOVE_MD,
                           (hx + int(math.cos(a) * 3), hy + int(math.sin(a) * 3)), 1)
    _r7_finger(surf, (hx - 3, hy + 2), (hx - 9, hy), 3, crease=False)


# WRAP grips — three z-passes (caller blits shaft between behind / front). The
# `behind` pass paints the palm heel + back fingers; the `front` pass paints the
# fingertips + a THUMB crossing the FRONT face of the shaft so the grasp is shown.

def _r7_wrap_realistic(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _r7_palm(surf, hx + 2, hy, 7, 6)
        for k, dy in enumerate((-5, -1, 3, 7)):
            _r7_finger(surf, (hx + 5, hy + dy), (hx - shaft_w + 1, hy + dy), 3,
                       groove_above=(k > 0))
    else:
        # Two fingertips cross clearly IN FRONT of the shaft + a thumb over its
        # front face — the grasp reads, not "beside". The caller has already laid
        # the occlusion band so the wood darkens under these digits.
        for dy in (-3, 5):
            _r7_finger(surf, (hx + 4, hy + dy), (hx - shaft_w - 3, hy + dy), 3)
        _r7_finger(surf, (hx + 6, hy - 7), (hx - shaft_w - 1, hy - 2), 4, crease=False)


def _r7_wrap_mascot(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _r7_palm(surf, hx + 2, hy, 7, 6)
        for dy in (-4, 3, 9):
            _r7_finger(surf, (hx + 6, hy + dy), (hx - shaft_w + 1, hy + dy), 4)
    else:
        # Two fat fingertips peek on the FRONT side + a thumb wraps over the
        # shaft's front face — the grip is shown, not implied. Four-seam grammar
        # matches the open hand for equalized gloves.
        for dy in (-1, 7):
            _r7_finger(surf, (hx + 5, hy + dy), (hx - shaft_w - 3, hy + dy), 4)
        _r7_finger(surf, (hx + 7, hy - 6), (hx - shaft_w - 2, hy - 1), 4, crease=False)
        # Bold seams between the two front fingers + along the thumb (toon read).
        pygame.draw.line(surf, _R7_GROOVE, (hx - 1, hy - 2), (hx - shaft_w - 2, hy + 4), 2)
        pygame.draw.line(surf, _R7_GROOVE, (hx + 2, hy - 4), (hx - shaft_w, hy - 1), 2)


def _r7_wrap_elegant(surf, hand, shaft_w, *, behind):
    hx, hy = hand
    if behind:
        _r7_palm(surf, hx + 3, hy, 6, 7)
        for k, dy in enumerate((-5, -1, 4)):
            _r7_finger(surf, (hx + 4, hy + dy), (hx - shaft_w, hy + dy), 3,
                       groove_above=(k > 0))
    else:
        # A slender index fingertip crosses in front + a poised thumb over the
        # shaft's front face — light, but unambiguously a grasp.
        _r7_finger(surf, (hx + 4, hy + 1), (hx - shaft_w - 4, hy - 1), 3)
        _r7_finger(surf, (hx + 6, hy - 7), (hx - shaft_w - 1, hy - 3), 3, crease=False)


_R7_HAND_KITS = {
    "realistic": (_r7_open_realistic, _r7_wrap_realistic),
    "mascot":    (_r7_open_mascot,    _r7_wrap_mascot),
    "elegant":   (_r7_open_elegant,   _r7_wrap_elegant),
}


def render_clown_staff_r7(idx, *, total_px, bauble_px, hands):
    """Round-7 hero panel: the approved round-5 held-marotte composition VERBATIM
    with ONLY the two HANDS re-detailed at the round-7 polish (consistent top-left
    rim, macaw-weight keyline, inter-finger grooves, shaft occlusion band, and a
    thumb crossing the FRONT of the shaft on the grip). Size is held at the ~16px
    footprint — all the added legibility is value, never bulk. The in-game clown
    is never touched; all detail lives in this look-dev overdraw."""
    open_fn, wrap_fn = _R7_HAND_KITS[hands]

    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    hand_up = (jester_cx - 60, feet_y - 154)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    open_fn(layer, hand_up)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    # Three z-passes: back fingers + palm heel BEHIND the shaft, then the shaft,
    # then an occlusion band on the wood, then the fingertips + thumb IN FRONT.
    shaft_w = 2
    wrap_fn(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r7_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    wrap_fn(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    draw_cupped_die(layer, jester_cx - 56, 30, idx * 1.7 + 2.0, show_inset=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


_CLOWN_R7_VARIANTS = [
    ("Realistic", dict(total_px=200, bauble_px=15, hands="realistic"),
     "wider grooved gaps + 2 fingertips crossing the shaft front"),
    ("Mascot", dict(total_px=200, bauble_px=15, hands="mascot"),
     "equalized 4-seam gloves + thumb wrapping the shaft front"),
    ("Elegant", dict(total_px=200, bauble_px=15, hands="elegant"),
     "shortened 3-finger slender hand, wide gaps, poised grasp"),
]


_CLOWN_R7_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 7: DETAILED HANDS polish (staff held constant; hand detail is the only variable)",
     (255, 255, 255)),
    ("Round-6 fixes applied: top-left rim + macaw keyline, grooved finger gaps, shaft-occlusion band, real front-of-shaft grip. "
     "Size held at ~16px (legibility via VALUE, never bulk). Three treatments — PICK ONE.",
     (205, 210, 220)),
]


def _render_clown_r7_sheet():
    """Round-7 clown look-dev: a 1-row strip of three hero panels differing ONLY
    in the polished hand-detail treatment, plus a true-1x shrink-test strip of all
    three over day AND night sky beneath. Writes docs/warren_clown/round_7.png —
    never overwrites an existing round sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = 3
    pad = 20
    head = 86
    name_strip = 34
    gap = 14
    shrink_h = 40 + VIEW_H            # label band + one true-1x row pair

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R7_HEADERS[0][0], True, _CLOWN_R7_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R7_HEADERS[1][0], True, _CLOWN_R7_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R7_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 20))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r7(idx, **kw)        # true 1x VIEW_W×VIEW_H
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip))

    # SHRINK-TEST: each panel at TRUE 1x, composited over day AND night sky so the
    # gate "must stay legible at 1x against day and night" is verifiable on-sheet.
    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)      # mid-night phase for the contrast gate
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        # Day on the left half of the cell, night on the right half, panel on each.
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_7.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ── Round-8 REFERENCE-GROUNDED HANDS ──────────────────────────────────────────
#  Round 7's value polish was right, but two reads stayed wrong: the GRIP read as
#  a fist/blob beside the pole (no four-finger wrap), and the OPEN hand was a flat
#  splayed star floating disconnected below the die. Round 8 rebuilds both from
#  cartoon-hand construction rules:
#    GRIP  — four sausage finger SEGMENTS banded across the NEAR face of the shaft,
#            each separated by a dark groove and curling so the shaft passes BEHIND
#            them (one tall occlusion band), a thumb wrapping over from the near
#            side overlapping the index, a back-of-hand knuckle line, the top
#            finger a touch looser. The point is it reads as 4 fingers, not a mitt.
#    CUP   — a rounded cup/oblong palm with four sausage fingers fanning UP and
#            curling inward (a cradle, never a flat star), thumb to the side. The
#            cube sits IN the curled fingers — CRADLE poses nudge the floating die
#            DOWN locally to meet the cup; PRESENT poses leave the die afloat with
#            a clean upturned cup beneath. Size held at the ~16px footprint; the
#            round-7 globals (top-left rim, macaw keyline, glove white) carry over.

_R8_GLOVE   = _R7_GLOVE
_R8_GROOVE  = _R7_GROOVE
_R8_OCCLUDE = _R7_OCCLUDE
_R8_GLOVE_MD = _R7_GLOVE_MD
_R8_GLOVE_HI = _R7_GLOVE_HI
_R8_OUTLINE = _R7_OUTLINE


def _r8_segment(surf, base, tip, w, *, rim=True, cap=True):
    """One finger SEGMENT capsule (base→tip) with the macaw-weight keyline, glove
    fill, rounded tip cap and the constant TOP-LEFT rim sheen. Unlike r7's open
    finger it carries no mid-crease — grip segments read by their bounding GROOVES,
    not internal creases, so they don't muddy at 3-4px wide."""
    pygame.draw.line(surf, _R8_OUTLINE, base, tip, w + 2)
    pygame.draw.line(surf, _R8_GLOVE, base, tip, w)
    if cap:
        pygame.draw.circle(surf, _R8_GLOVE, tip, max(1, w // 2))
        pygame.draw.circle(surf, _R8_OUTLINE, tip, max(1, w // 2), 1)
    if rim:
        pygame.draw.line(surf, _R8_GLOVE_HI,
                         (base[0] - 1, base[1] - 1), (tip[0] - 1, tip[1] - 1),
                         max(1, w // 3))


def _r8_palm(surf, cx, cy, rx, ry):
    """Rounded palm/cup mass — keyline ellipse, glove fill, top-left alpha sheen."""
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, _R8_OUTLINE, rect)
    pygame.draw.ellipse(surf, _R8_GLOVE, rect.inflate(-2, -2))
    sheen = pygame.Surface((rx, ry), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 90), sheen.get_rect())
    surf.blit(sheen, (cx - rx + 1, cy - ry + 1))


def _r8_grip_occlusion(surf, hand, shaft_w):
    """The dark band on the shaft spanning the full height of the FOUR banded
    fingers, so the wood reads as passing behind the whole grip rather than beside
    one digit. Taller than r7's because all four fingers cross the wood here."""
    hx, hy = hand
    pygame.draw.line(surf, _R8_OCCLUDE,
                     (hx - shaft_w - 2, hy - 8), (hx - shaft_w - 2, hy + 11),
                     shaft_w + 2)


# GRIP builders — three z-passes (caller blits the shaft between behind / front).
#   behind  : palm heel + the back of the hand BEHIND the shaft.
#   front   : FOUR finger segments banded across the near face, separated by dark
#             grooves, plus a thumb wrapping over and overlapping the index.
# `fw`/`gap`/`dys` shape each variant's finger mass + banding rhythm.

def _r8_grip_core(surf, hand, shaft_w, *, behind, fw, dys, palm_rx, palm_ry,
                  thumb_w, loose_top=1, knuckle=True):
    hx, hy = hand
    reach = shaft_w + 5                         # how far past the shaft a band runs
    if behind:
        # The back of the hand / palm heel sits behind the shaft; the four bands
        # are painted in the FRONT pass so they crisply overdraw the wood.
        _r8_palm(surf, hx + 3, hy + 1, palm_rx, palm_ry)
        # Back-of-hand knuckle ridge line (a single dark crease down the heel) so
        # the mass reads as a hand back, not a ball.
        if knuckle:
            pygame.draw.line(surf, _R8_GROOVE,
                             (hx + 3, hy - palm_ry + 2), (hx + 3, hy + palm_ry - 2), 1)
        return
    # FRONT: four banded finger segments. Each band is a short horizontal capsule
    # crossing the near face of the shaft; the top one sits a touch looser (lifted
    # + reaching further) to break the stack and sell a real grip.
    for k, dy in enumerate(dys):
        loose = loose_top if k == 0 else 0
        # A dark groove laid just ABOVE each lower band first, then the band
        # overdraws it — guarantees a ≥1px value gap between adjacent fingers.
        if k > 0:
            pygame.draw.line(surf, _R8_GROOVE,
                             (hx + 4, hy + dy - fw // 2 - 1),
                             (hx - reach + 1, hy + dy - fw // 2 - 1 - loose),
                             max(1, fw // 2))
        base = (hx + 4, hy + dy)
        tip = (hx - reach - loose, hy + dy - loose)
        _r8_segment(surf, base, tip, fw)
    # THUMB wraps over from the near (lower) side, tip up + inward, overlapping
    # the index band — drawn last so it reads as crossing in front of the fingers.
    tb = (hx + thumb_w + 2, hy + dys[-1] + 3)
    tt = (hx - 2, hy + dys[0] - 1)
    _r8_segment(surf, tb, tt, thumb_w)


def _r8_grip_glove(surf, hand, shaft_w, *, behind):
    """Classic 4-finger glove grip: four plump even bands, fat thumb over."""
    _r8_grip_core(surf, hand, shaft_w, behind=behind, fw=4,
                  dys=(-6, -1, 4, 9), palm_rx=6, palm_ry=8, thumb_w=4)


def _r8_grip_mascot(surf, hand, shaft_w, *, behind):
    """Rounded mascot grip: chunky bands, bold grooves, very fat thumb."""
    hx, hy = hand
    _r8_grip_core(surf, hand, shaft_w, behind=behind, fw=5,
                  dys=(-6, 0, 6, 11), palm_rx=7, palm_ry=8, thumb_w=5, loose_top=2)
    if not behind:
        # An extra bold Mickey-glove seam splitting the thumb from the palm.
        pygame.draw.line(surf, _R8_GROOVE,
                         (hx + 4, hy + 9), (hx - shaft_w - 1, hy + 5), 2)


def _r8_grip_slim(surf, hand, shaft_w, *, behind):
    """Slimmer articulated grip: four narrow bands, tighter banding, slim thumb."""
    _r8_grip_core(surf, hand, shaft_w, behind=behind, fw=3,
                  dys=(-5, -1, 3, 7), palm_rx=5, palm_ry=7, thumb_w=3, loose_top=2)


# CUP builders — a rounded cup palm with four fingers fanning UP and curling
# inward toward the object. `present` leaves the floating die where it is and
# seats a clean upturned cup beneath; `cradle` raises the cup and the caller
# nudges the die down so the curled fingertips contact it.

def _r8_cup_core(surf, hand, *, fw, palm_rx, palm_ry, fan, ln, thumb_w, curl):
    """Paint a cradle/offer cup at `hand`. Fingers fan across `fan` (degrees, left
    to right, measured from straight-up) and curl inward by `curl` so their tips
    arc toward the held object instead of splaying flat."""
    hx, hy = hand
    _r8_palm(surf, hx, hy, palm_rx, palm_ry)
    angs = [fan[0] + (fan[1] - fan[0]) * i / 3 for i in range(4)]
    for i, ang in enumerate(angs):
        a = math.radians(ang - 90)
        l = ln - abs(i - 1.5) * 0.6              # middle fingers longest
        # Each finger roots at a DISTINCT knuckle spread across the cup's top rim
        # (not one shared point), so the four digits read individually rather than
        # fanning from a single knot.
        root = (hx + int(math.cos(a) * palm_rx * 0.55),
                hy - 2 + int(math.sin(a) * palm_ry * 0.45))
        # Curl: the tip bends inward (toward centre) + up, so the fan cups instead
        # of splaying — two short segments per finger sell the bend at hero scale.
        mid = (root[0] + int(math.cos(a) * l * 0.55),
               root[1] + int(math.sin(a) * l * 0.55))
        ca = a - math.radians(curl) * (1 if ang < 0 else -1)
        tip = (mid[0] + int(math.cos(ca) * l * 0.5),
               mid[1] + int(math.sin(ca) * l * 0.5))
        if i > 0:
            pygame.draw.line(surf, _R8_GROOVE,
                             root, (mid[0], mid[1] - fw // 2 - 1), max(1, fw // 2))
        _r8_segment(surf, root, mid, fw, cap=False)
        _r8_segment(surf, mid, tip, fw)
    # THUMB out to the side, also curling up, framing the cup's near rim.
    tb = (hx - palm_rx + 1, hy + 2)
    tt = (hx - palm_rx - thumb_w, hy - thumb_w)
    _r8_segment(surf, tb, tt, thumb_w)


def _r8_cup_glove(surf, hand):
    _r8_cup_core(surf, hand, fw=4, palm_rx=7, palm_ry=6,
                 fan=(-52, 38), ln=9, thumb_w=4, curl=18)


def _r8_cup_mascot(surf, hand):
    _r8_cup_core(surf, hand, fw=5, palm_rx=7, palm_ry=7,
                 fan=(-48, 34), ln=8, thumb_w=5, curl=20)


def _r8_cup_slim(surf, hand):
    _r8_cup_core(surf, hand, fw=3, palm_rx=6, palm_ry=6,
                 fan=(-56, 42), ln=10, thumb_w=3, curl=15)


# Each variant pairs a grip builder + a cup builder + a cube relationship.
#   relation = "cradle": raise the cup `cup_dy` px and pull the die DOWN `die_dy`
#              so the curled fingertips meet the cube (local hero overdraw only).
#   relation = "present": die stays afloat; a clean upturned cup sits beneath it.
_R8_HAND_KITS = {
    "glove":  (_r8_grip_glove,  _r8_cup_glove),
    "mascot": (_r8_grip_mascot, _r8_cup_mascot),
    "slim":   (_r8_grip_slim,   _r8_cup_slim),
}


def render_clown_staff_r8(idx, *, total_px, bauble_px, grip, cup, relation,
                          cup_dy=0, die_dy=0):
    """Round-8 hero panel: the approved round-5 held-marotte composition VERBATIM
    with ONLY the two HANDS swapped for the reference-grounded four-finger GRIP and
    cupped CRADLE/OFFER hands. `grip`/`cup` name the cartoon-hand style; `relation`
    is the cube read (cradle vs present). Size held at the ~16px footprint."""
    grip_fn = _R8_HAND_KITS[grip][0]
    cup_fn = _R8_HAND_KITS[cup][1]

    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    # The open hand lifts by `cup_dy` for cradle poses so the curled fingers reach
    # up to the cube; presents keep the round-5 hand height.
    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # The floating die — drawn FIRST so the cradle cup can overdraw its lower edge
    # (the fingers wrap in FRONT of the cube). `die_dy` pulls it down to the cup
    # on cradle poses; present poses leave it afloat (die_dy=0).
    draw_cupped_die(layer, jester_cx - 56, 30 + die_dy, idx * 1.7 + 2.0,
                    show_inset=False)

    cup_fn(layer, hand_up)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    # Grip z-order: back-of-hand + palm heel BEHIND the shaft, shaft, a tall
    # occlusion band on the wood, then the FOUR banded fingers + thumb IN FRONT.
    shaft_w = 2
    grip_fn(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r8_grip_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    grip_fn(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


_CLOWN_R8_VARIANTS = [
    ("Glove · Cradle", dict(total_px=200, bauble_px=15, grip="glove", cup="glove",
                            relation="cradle", cup_dy=2, die_dy=9),
     "classic 4-finger glove: 4 banded fingers grip the staff; cup raised to CRADLE the die"),
    ("Mascot · Cradle", dict(total_px=200, bauble_px=15, grip="mascot", cup="mascot",
                             relation="cradle", cup_dy=2, die_dy=8),
     "chunky rounded mascot: bold 4-band grip + thumb over; fat cup CRADLES the die"),
    ("Glove · Present", dict(total_px=200, bauble_px=15, grip="glove", cup="glove",
                             relation="present", cup_dy=6),
     "classic glove grip; die floats free above a clean upturned PRESENTING cup"),
    ("Slim · Present", dict(total_px=200, bauble_px=15, grip="slim", cup="slim",
                            relation="present", cup_dy=6),
     "slim articulated hand: 4 tight bands grip the staff; airy cup PRESENTS the floating die"),
    ("Best-of · Cradle", dict(total_px=200, bauble_px=15, grip="glove", cup="mascot",
                              relation="cradle", cup_dy=2, die_dy=9),
     "refined pick: glove 4-band grip + mascot cradle cup conforming to the die"),
]


_CLOWN_R8_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 8: REFERENCE-GROUNDED HANDS (staff held constant; only the two hands change)",
     (255, 255, 255)),
    ("Fixes: GRIP now reads as FOUR banded fingers wrapping the staff (shaft occluded behind, thumb over). "
     "OPEN hand is a cupped CRADLE/OFFER conforming to the die — never a flat star. Size held ~16px. PICK ONE.",
     (205, 210, 220)),
]


def _render_clown_r8_sheet():
    """Round-8 clown look-dev: five hero panels varying BOTH the cartoon-hand
    style AND the grip-wrap + cradle/present pose, plus the carried-over true-1x
    day/night shrink-test strip so the hands are confirmed legible at real size.
    Writes docs/warren_clown/round_8.png — never overwrites an existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = 5
    pad = 20
    head = 86
    name_strip = 38
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R8_HEADERS[0][0], True, _CLOWN_R8_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R8_HEADERS[1][0], True, _CLOWN_R8_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R8_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r8(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_8.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ── Round-9 DIE SEATED IN THE CRADLE ──────────────────────────────────────────
#  Round 8 LOCKED the four-finger staff grip (Panel-1 "glove" grip is canonical —
#  reused here verbatim) and picked Panel-5's chunky mascot cup as the best cradle
#  shape. The one remaining blocker was the OPEN hand never actually HOLDING the
#  die: every "present"/"cradle" pose left a clean sky gap between the upturned
#  hand and the floating cube, so it read as "loose hand + separately floating
#  die." Round 9 retires "present" entirely and fixes the read with a single
#  device the whole "holding" cue rests on: the near cup fingertips are redrawn
#  OVER the die's lower-front corner — a tooth of glove crossing IN FRONT of the
#  cube, so there is never clean sky between hand and object (the Subway-Surfers /
#  Crossy-Road held-prop rule). The cup is also tightened to a shallow C of three
#  curled ridges hugging the cube's bottom corner (no splayed 5-finger fan, which
#  muddies the 1x noise budget), and the die is dropped so its bottom corner
#  overlaps the fingertips. Only the cube-seating varies across the panels; the
#  grip is the locked Panel-1 glove grip on every one. Globals (top-left rim,
#  macaw keyline, glove white, shaft occlusion band) carry over from r7/r8.

_R9_GLOVE   = _R8_GLOVE
_R9_GROOVE  = _R8_GROOVE
_R9_OCCLUDE = _R8_OCCLUDE
_R9_GLOVE_HI = _R8_GLOVE_HI
_R9_OUTLINE = _R8_OUTLINE


# The LOCKED grip is Panel-1's glove grip, reused unchanged so the won read does
# not regress. Only an alias — the builder itself is _r8_grip_glove verbatim.
_r9_grip = _r8_grip_glove


def _r9_cradle_cup(surf, hand, *, behind):
    """Panel-5's chunky mascot CUP, re-cut as a shallow C that HUGS the die's
    lower corner instead of fanning at empty sky. The `behind` pass paints the
    palm mass + the LEFT-side ridges/thumb that sit beside the cube; the near
    (right) fingertips that overdraw the cube are painted later by
    _r9_cradle_occlude. Kept at the round-8 ~16px footprint — the contact
    OVERLAP, not size, is the read. We keep the silhouette to a shallow C of three
    readable ridges (left ridge + a short mid ridge + the two near teeth), never a
    splayed five-finger fan, to fit the 1x noise budget."""
    hx, hy = hand
    fw = 5
    palm_rx, palm_ry = 7, 7
    if behind:
        # Cup palm mass + the far (left) side of the C sit behind the die so the
        # near fingertips can later wrap over the cube's front face.
        _r8_palm(surf, hx, hy, palm_rx, palm_ry)
        # Far-LEFT ridge: roots at the palm's left rim, curls up + inward so the
        # cube's left underside rests in it. One groove sets it off the palm.
        root = (hx - palm_rx + 2, hy - 2)
        mid = (root[0] + 1, root[1] - 7)
        tip = (mid[0] + 4, mid[1] - 4)
        pygame.draw.line(surf, _R9_GROOVE, root, (root[0] + 2, root[1] - 5), 2)
        _r8_segment(surf, root, mid, fw, cap=False)
        _r8_segment(surf, mid, tip, fw)
        # Fat THUMB framing the near (right) base of the C, curling up.
        tb = (hx + palm_rx - 1, hy + 2)
        tt = (hx + palm_rx + 3, hy - 4)
        _r8_segment(surf, tb, tt, 5)
        return
    # FRONT (over the die not yet drawn here — only the SHORT mid ridge that sits
    # between the left ridge and the near teeth, completing the C's floor).
    root = (hx - 1, hy - 3)
    mid = (root[0] + 1, root[1] - 6)
    pygame.draw.line(surf, _R9_GROOVE, (root[0] - 3, root[1]), root, 2)
    _r8_segment(surf, root, mid, fw)


def _r9_cradle_occlude(surf, hand, die_corner):
    """The ENTIRE "holding" read: the two NEAR (right-side) cup fingertips drawn as
    short glove teeth crossing IN FRONT of the die's lower-front corner, so a
    fingertip visibly overlaps the cube and there is no clean sky between hand and
    object. `die_corner` is the cube's bottom-front point in layer space. A dark
    groove between the two teeth keeps them reading as separate digits, and a
    shadow notch where they meet the cube sells the wrap."""
    hx, hy = hand
    dx, dy = die_corner
    # Two distinct teeth rising from the cup's near rim onto the cube's lower-front
    # corner — the inner one buries into the corner, the outer one clasps the front
    # face a touch higher, so the glove unmistakably closes over the cube edge.
    inner = ((hx + 1, hy - 4), (dx - 2, dy - 1))
    outer = ((hx + 4, hy - 3), (dx + 3, dy - 4))
    # Dark groove between the two teeth so they don't merge into a blob.
    pygame.draw.line(surf, _R9_GROOVE, inner[0], (outer[1][0], outer[1][1] + 2), 2)
    _r8_segment(surf, *inner, 5)
    _r8_segment(surf, *outer, 5)
    # A short shadow notch where the teeth cross the cube — seats them ON the face
    # rather than merely touching the edge.
    pygame.draw.line(surf, _R9_GROOVE, (dx - 3, dy - 5), (dx + 4, dy - 7), 1)


def render_clown_staff_r9(idx, *, total_px, bauble_px, cup_dy, die_dy, die_dx=0,
                          die_pulse_off=2.0):
    """Round-9 hero panel: the approved round-5 held-marotte composition with the
    LOCKED Panel-1 glove staff grip on the down hand and the Panel-5-derived
    cradle cup on the open hand — now with the die SEATED INTO the cup. The die is
    dropped (`die_dy`) so its bottom corner overlaps the curled fingertips, then a
    near-fingertip occlusion pass draws glove teeth OVER that corner. Panels differ
    ONLY in how the cube is seated (`die_dy`/`die_dx`/`die_pulse_off`)."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    # The open arm lifts so the cradle reaches up to the seated die.
    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    die_cx = jester_cx - 56 + die_dx
    die_cy = 30 + die_dy
    bob = int(math.sin((idx * 1.7 + die_pulse_off) * 1.1) * 3)
    # The cube's bottom-front corner in layer space (cube geometry: bf = cy + 22 at
    # size 40). The cup is anchored DIRECTLY beneath this corner — not at the bare
    # arm endpoint — so the curled C wraps the corner instead of sitting off to one
    # side; a wrist stub bridges the gap back to the build_jester arm tip.
    die_bf = (die_cx, die_cy + bob + 22)
    cup = (die_bf[0], die_bf[1] + 4)
    # Wrist stub from the arm endpoint up into the cup so the cradle reads as a
    # continuation of the same arm, not a free-floating hand.
    pygame.draw.line(layer, _R9_OUTLINE, hand_up, (cup[0], cup[1] + 5), 9)
    pygame.draw.line(layer, _R9_GLOVE, hand_up, (cup[0], cup[1] + 5), 7)

    # z-order for the HOLDING read: cup palm mass BEHIND the die, then the die,
    # then the curled ridges, then the near fingertip TEETH overdrawing the cube's
    # lower-front corner so a glove tooth crosses in front of the cube (no sky gap).
    _r9_cradle_cup(layer, cup, behind=True)

    draw_cupped_die(layer, die_cx, die_cy, idx * 1.7 + die_pulse_off,
                    show_inset=False)

    _r9_cradle_cup(layer, cup, behind=False)
    _r9_cradle_occlude(layer, cup, die_bf)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    # Grip z-order (LOCKED Panel-1 glove grip): back-of-hand + palm heel BEHIND
    # the shaft, shaft, the tall occlusion band on the wood, then the FOUR banded
    # fingers + thumb IN FRONT.
    shaft_w = 2
    _r9_grip(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r8_grip_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    _r9_grip(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# All four panels share the LOCKED grip + the Panel-5 cradle cup; ONLY the die
# seating differs. die_dy seats the cube's bottom corner onto the fingertips;
# die_dx / die_pulse_off tune which corner contacts and the tilt of the bob.
_CLOWN_R9_VARIANTS = [
    ("Corner-rest", dict(total_px=200, bauble_px=15, cup_dy=2, die_dy=12,
                         die_dx=0, die_pulse_off=2.0),
     "die balanced CORNER-DOWN on the fingertips; near teeth clasp the lower-front corner"),
    ("Flat-seat", dict(total_px=200, bauble_px=15, cup_dy=2, die_dy=14,
                       die_dx=2, die_pulse_off=0.6),
     "die sits FLATTER across the fingertips; cube edge buried into the curled C"),
    ("Near-corner", dict(total_px=200, bauble_px=15, cup_dy=2, die_dy=13,
                         die_dx=4, die_pulse_off=3.4),
     "die shifted onto the NEAR corner; thumb-side rim + teeth close over that corner"),
    ("Deep-seat", dict(total_px=200, bauble_px=15, cup_dy=3, die_dy=16,
                       die_dx=1, die_pulse_off=1.5),
     "die sunk DEEPEST into the cup; most glove crosses the cube's lower face"),
]


_CLOWN_R9_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 9: DIE SEATED IN THE CRADLE (grip LOCKED to Panel-1; only the cube seating varies)",
     (255, 255, 255)),
    ("Fix: the open hand now HOLDS the die — near glove fingertips overdraw the cube's lower-front corner (no sky gap). "
     "Cradle is a shallow C of <=3 curled ridges hugging the cube. Glow kept behind the contact. PICK ONE SEATING.",
     (205, 210, 220)),
]


def _render_clown_r9_sheet():
    """Round-9 clown look-dev: 3-4 hero panels of the SAME best-of merge (locked
    Panel-1 grip + Panel-5 cradle cup) varying only how the die is seated into the
    cup, plus the carried-over true-1x day/night shrink-test strip. Writes
    docs/warren_clown/round_9.png — never overwrites an existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = len(_CLOWN_R9_VARIANTS)
    pad = 20
    head = 86
    name_strip = 38
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R9_HEADERS[0][0], True, _CLOWN_R9_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R9_HEADERS[1][0], True, _CLOWN_R9_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R9_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r9(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_9.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ── Round-10 GRIP DE-THUMBED + DIE FLOATS ABOVE A SIMPLE OPEN HAND ────────────
#  Two prescriptive fixes on the round-9 Panel-1 (Corner-rest) geometry:
#   1. The staff grip kept ONLY its four banded fingers — the diagonal thumb that
#      wrapped OVER them (round-8/9's _r8_grip_core thumb stroke) read as a stray
#      fifth digit crossing on top and is removed entirely. Nothing crosses the
#      four fingers now; the won four-band read is otherwise untouched.
#   2. The die-into-cup seating is retired: no fingertip-over-corner occlusion, no
#      curled C cradle. The cube floats free in the air ABOVE a SIMPLE OPEN HAND
#      with a clear sky gap (the die is NOT held). The open hand is a calm rounded
#      mitt — four relaxed, gently extended fingers — explicitly NOT the splayed
#      five-point star an earlier round shipped, and NOT a curled cup. Three open-
#      hand reads vary only the finger spread/angle so the cleanest can be picked.
#  Globals (top-left rim, macaw keyline, glove white, shaft occlusion band) and
#  the floating die's glow ring + sparkles all carry over unchanged.

_R10_GLOVE   = _R8_GLOVE
_R10_GROOVE  = _R8_GROOVE
_R10_OCCLUDE = _R8_OCCLUDE
_R10_GLOVE_HI = _R8_GLOVE_HI
_R10_OUTLINE = _R8_OUTLINE


def _r10_grip_glove(surf, hand, shaft_w, *, behind):
    """LOCKED Panel-1 four-finger staff grip with FIX 1 applied: the back-of-hand
    + palm heel sit behind the shaft, then the four banded finger segments wrap
    the near face — and NOTHING else. The diagonal thumb that round-8/9 drew over
    the top of the fingers is gone, so the grip reads as exactly four grooved
    digits with the shaft occluded behind them. Geometry (fw / dys / palm size /
    loose top finger) is verbatim from the won _r8_grip_glove minus the thumb."""
    hx, hy = hand
    fw = 4
    dys = (-6, -1, 4, 9)
    palm_rx, palm_ry = 6, 8
    loose_top = 1
    reach = shaft_w + 5
    if behind:
        # Back of hand / palm heel behind the shaft; the four bands overdraw the
        # wood in the front pass so the wrap reads cleanly.
        _r8_palm(surf, hx + 3, hy + 1, palm_rx, palm_ry)
        pygame.draw.line(surf, _R10_GROOVE,
                         (hx + 3, hy - palm_ry + 2), (hx + 3, hy + palm_ry - 2), 1)
        return
    # FRONT: four banded finger segments only. The top one sits a touch looser
    # (lifted + reaching further) to break the stack and sell a real grip.
    for k, dy in enumerate(dys):
        loose = loose_top if k == 0 else 0
        if k > 0:
            pygame.draw.line(surf, _R10_GROOVE,
                             (hx + 4, hy + dy - fw // 2 - 1),
                             (hx - reach + 1, hy + dy - fw // 2 - 1 - loose),
                             max(1, fw // 2))
        base = (hx + 4, hy + dy)
        tip = (hx - reach - loose, hy + dy - loose)
        _r8_segment(surf, base, tip, fw)


def _r10_open_hand(surf, hand, *, spread, lift, finger_w=4):
    """FIX 2 — a SIMPLE, relaxed OPEN hand presenting upward, with the die floating
    free above it (drawn separately, with a clear sky gap). A rounded palm with
    four softly-extended fingers reaching up; `spread` is the lateral fan between
    fingertips (small = together-ish, never the spiky 5-point star) and `lift`
    angles the whole splay up toward the die. There is NO thumb-over, NO curled
    cup, NO contact with the cube. Kept inside the ~16px round-8/9 footprint."""
    hx, hy = hand
    # Rounded palm mass — the calm open mitt the fingers root from.
    _r8_palm(surf, hx, hy, 6, 6)
    # Four fingers fanning gently UP off the palm rim. The middle pair are a hair
    # longer than the outer pair (natural hand silhouette), and each tip steps in
    # by `spread` so they read as relaxed-apart, not splayed into a star.
    rim_y = hy - 4
    cols = (-spread * 1.6, -spread * 0.55, spread * 0.55, spread * 1.6)
    lens = (8, 10, 10, 8)
    for k, (dx, ln) in enumerate(zip(cols, lens)):
        base = (hx + int(dx * 0.5), rim_y)
        tip = (hx + int(dx), rim_y - ln - lift)
        # A short groove just inboard of each finger so adjacent fingers stay
        # legibly separate at 1x without fanning into spikes.
        if k > 0:
            pygame.draw.line(surf, _R10_GROOVE,
                             (base[0] - 1, base[1]), (tip[0] - 1, tip[1] + 2), 1)
        _r8_segment(surf, base, tip, finger_w)


def render_clown_staff_r10(idx, *, total_px, bauble_px, cup_dy, open_spread,
                           open_lift, die_pulse_off=2.0):
    """Round-10 hero panel built on round-9 Panel-1 (Corner-rest) geometry with the
    two prescriptive fixes: a de-thumbed four-finger staff grip and a simple open
    hand under a FREELY FLOATING die. Panels differ ONLY in the open hand's finger
    spread/lift (`open_spread`/`open_lift`) so the cleanest open read can be
    picked; the staff grip and floating die are identical across all three."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    # The open arm reaches up under the floating die (same lift as round 9 so the
    # composition is unchanged); only the hand at its tip differs.
    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # Die FLOATS in the air, NOT seated — back to round-5 placement (no die_dy
    # drop), so there is clear sky between the cube and the open hand below it.
    die_cx = jester_cx - 56
    die_cy = 30
    # The open hand sits a touch above the bare arm tip, presenting up toward the
    # die. A short wrist stub bridges the arm tip to the palm so the hand reads as
    # a continuation of the same arm, not a free-floating mitt.
    open_hand = (die_cx + 2, die_cy + 60)
    pygame.draw.line(layer, _R10_OUTLINE, hand_up, (open_hand[0], open_hand[1] + 5), 9)
    pygame.draw.line(layer, _R10_GLOVE, hand_up, (open_hand[0], open_hand[1] + 5), 7)

    # Open hand UNDER the gap, then the floating die ABOVE it with its glow ring +
    # sparkles — drawn after the hand so the air gap is unmistakable.
    _r10_open_hand(layer, open_hand, spread=open_spread, lift=open_lift)
    draw_cupped_die(layer, die_cx, die_cy, idx * 1.7 + die_pulse_off,
                    show_inset=False)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    # Grip z-order (de-thumbed four-finger grip): back-of-hand + palm heel BEHIND
    # the shaft, shaft, the tall occlusion band on the wood, then the FOUR banded
    # fingers IN FRONT — and nothing crossing over them.
    shaft_w = 2
    _r10_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r8_grip_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    _r10_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Three open-hand reads on the SAME de-thumbed grip + floating die: only the open
# hand's finger spread/lift varies so the cleanest "simple open hand" can be
# picked. open_spread = lateral fingertip fan (small = together-ish, never a star);
# open_lift = how far the splay angles UP toward the die.
_CLOWN_R10_VARIANTS = [
    ("Flat-open", dict(total_px=200, bauble_px=15, cup_dy=2,
                       open_spread=4, open_lift=0, die_pulse_off=2.0),
     "palm-up flat-open: four fingers softly together, gently extended, die floats above"),
    ("Relaxed-gap", dict(total_px=200, bauble_px=15, cup_dy=2,
                         open_spread=6, open_lift=1, die_pulse_off=2.0),
     "relaxed open with a slight natural gap between fingers; clear air to the floating die"),
    ("Angled-up", dict(total_px=200, bauble_px=15, cup_dy=2,
                       open_spread=5, open_lift=4, die_pulse_off=2.0),
     "open mitt angled slightly UP toward the die; fingers together-ish, not fanned"),
]


_CLOWN_R10_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 10: GRIP DE-THUMBED + DIE FLOATS ABOVE A SIMPLE OPEN HAND (grip + die constant; only the open hand varies)",
     (255, 255, 255)),
    ("Fix 1: the staff grip shows ONLY four banded fingers — the diagonal thumb-over is GONE (nothing crosses on top). "
     "Fix 2: the die FLOATS free above a simple open hand (clear air, NOT held, NOT a star, NOT a cup). PICK ONE OPEN HAND.",
     (205, 210, 220)),
]


def _render_clown_r10_sheet():
    """Round-10 clown look-dev: 3 hero panels of the SAME de-thumbed four-finger
    grip + freely floating die, varying only the simple open hand beneath the die,
    plus the carried-over true-1x day/night shrink-test strip so both fixes are
    confirmed legible at real size. Writes docs/warren_clown/round_10.png — never
    overwrites an existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = len(_CLOWN_R10_VARIANTS)
    pad = 20
    head = 86
    name_strip = 38
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R10_HEADERS[0][0], True, _CLOWN_R10_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R10_HEADERS[1][0], True, _CLOWN_R10_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R10_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r10(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_10.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ── Round-11 GRIP FOURTH FINGER JOINED + DIE OVER A SIDE-VIEW OPEN HAND ────────
#  Two prescriptive fixes on the won round-10 geometry:
#   1. Grip: round-10 joined the TOP THREE fingers to the right-side palm/knuckle
#      mass but left the FOURTH (bottom) finger floating alone. The knuckle mass
#      is now extended down so all FOUR finger roots emerge from ONE continuous
#      gripping hand on the right — no orphan digit. Groove separation, shaft
#      occlusion behind, and the slightly looser top finger are all unchanged; the
#      removed thumb-over is NOT re-added.
#   2. Open hand: the front-on open palm is retired for a SIDE / PROFILE open hand.
#      From the side a hand is a thin slab — you see the palm edge, the thumb
#      projecting off the near/top edge, and the four fingers as a layered/stacked
#      set extending outward (only the near 1-2 fully read, the rest stepped just
#      behind). The die's float position + gap, its glow ring and sparkles are
#      unchanged; only the hand pose under it becomes a profile. Three profile
#      reads vary so the clearest can be picked.
#  Globals (top-left rim, macaw keyline, glove white, shaft occlusion band) carry
#  over unchanged; hero face/body, the marotte in the DOWN hand and the bell foot
#  are identical to round 10.

_R11_GLOVE   = _R10_GLOVE
_R11_GROOVE  = _R10_GROOVE
_R11_OCCLUDE = _R10_OCCLUDE
_R11_GLOVE_HI = _R10_GLOVE_HI
_R11_OUTLINE = _R10_OUTLINE


def _r11_grip_glove(surf, hand, shaft_w, *, behind):
    """LOCKED four-finger staff grip with FIX 1 applied: round-10's behind pass
    drew a single palm ellipse whose narrowing bottom edge left the FOURTH finger
    root (dy=9) uncovered, so that digit read as floating free of the hand mass.
    Here the back-of-hand mass is widened into a tall knuckle ridge that spans the
    full -6..+9 finger band on the right, so ALL FOUR finger bases emerge from one
    continuous palm. The four banded fingers, their grooves, the looser top finger
    and the shaft occlusion behind are verbatim from round 10; no thumb is added."""
    hx, hy = hand
    fw = 4
    dys = (-6, -1, 4, 9)
    palm_rx, palm_ry = 6, 8
    loose_top = 1
    reach = shaft_w + 5
    if behind:
        # Back of hand / palm heel behind the shaft. The ellipse is kept (heel +
        # rounded back), then a knuckle ridge is added down the RIGHT side spanning
        # every finger root so the bottom finger is no longer an orphan: it joins
        # the same mass as the top three.
        _r8_palm(surf, hx + 3, hy + 1, palm_rx, palm_ry)
        # Tall knuckle ridge on the grip side — a rounded slab from the top finger
        # band (dy=-6) down past the bottom one (dy=9) so all four roots fuse.
        ridge = pygame.Rect(0, 0, fw + 4, (dys[-1] - dys[0]) + fw + 4)
        ridge.center = (hx + 4, hy + (dys[0] + dys[-1]) // 2)
        pygame.draw.rect(surf, _R11_OUTLINE, ridge, border_radius=fw)
        pygame.draw.rect(surf, _R11_GLOVE, ridge.inflate(-2, -2), border_radius=fw)
        pygame.draw.line(surf, _R11_GROOVE,
                         (hx + 3, hy - palm_ry + 2), (hx + 3, hy + palm_ry - 2), 1)
        return
    # FRONT: four banded finger segments only, rooted in the knuckle ridge above.
    # The top one sits a touch looser (lifted + reaching further) to break the
    # stack and sell a real grip.
    for k, dy in enumerate(dys):
        loose = loose_top if k == 0 else 0
        if k > 0:
            pygame.draw.line(surf, _R11_GROOVE,
                             (hx + 4, hy + dy - fw // 2 - 1),
                             (hx - reach + 1, hy + dy - fw // 2 - 1 - loose),
                             max(1, fw // 2))
        base = (hx + 4, hy + dy)
        tip = (hx - reach - loose, hy + dy - loose)
        _r8_segment(surf, base, tip, fw)


def _r11_side_open_hand(surf, hand, *, tilt, thumb_up, finger_w=4):
    """FIX 2 — a SIMPLE open hand seen from the SIDE / in profile, the die floating
    free above it. From the side a hand is a THIN SLAB, not a broad palm face: a
    narrow palm edge, the THUMB projecting off the near/top edge, and the four
    fingers reading as a LAYERED set extending out to the side — the near finger
    fully visible, the rest stepped just behind it (not a flat face-on spread).
    `tilt` rotates the whole splay up toward the die (0 = level); `thumb_up` raises
    the thumb to a clear thumb-up read. NO front palm face, NO star, NO cup. Kept
    inside the ~16px round-8/9 footprint."""
    hx, hy = hand
    ang = math.radians(-tilt)          # negative = fingers angle UP toward the die
    ca, sa = math.cos(ang), math.sin(ang)

    def _proj(dx, dy):
        # Local hand frame (x = out along the slab, y = up) → screen, with tilt.
        return (hx + int(dx * ca - dy * sa), hy + int(dx * sa + dy * ca))

    # Palm seen edge-on: a thin vertical slab, taller than it is wide. Drawn as a
    # rounded capsule so the side silhouette stays slim, not a broad disc.
    top = _proj(0, -5)
    bot = _proj(0, 5)
    pygame.draw.line(surf, _R11_OUTLINE, top, bot, finger_w + 5)
    pygame.draw.line(surf, _R11_GLOVE, top, bot, finger_w + 3)
    sheen = _proj(-1, -3)
    pygame.draw.circle(surf, _R11_GLOVE_HI, sheen, 2)

    # Four fingers extend OUT to the side as a stacked layer: the near (lowest)
    # one reads full, the rest step back+up just behind it with a slight backward
    # curve (extended-finger silhouette). Stepping in screen-y keeps them legibly
    # layered at 1x instead of merging into one blob.
    finger_rows = ((5, 13), (3, 12), (1, 11), (-1, 10))
    for k, (oy, ln) in enumerate(finger_rows):
        base = _proj(4, oy)
        # Slight backward (downward-trailing) curve at the tip of extended fingers.
        tip = _proj(4 + ln, oy + 1)
        if k > 0:
            # Groove shadow where each layered finger tucks behind the one in front.
            sh = _proj(4, oy + 2)
            st = _proj(4 + ln - 1, oy + 3)
            pygame.draw.line(surf, _R11_GROOVE, sh, st, 1)
        _r8_segment(surf, base, tip, finger_w)

    # Thumb projects off the NEAR/TOP edge of the slab — the side-view signature.
    th_base = _proj(1, -4)
    th_tip = _proj(2 + thumb_up, -4 - 8 - thumb_up * 2)
    _r8_segment(surf, th_base, th_tip, finger_w)


def render_clown_staff_r11(idx, *, total_px, bauble_px, cup_dy, side_tilt,
                           thumb_up, die_pulse_off=2.0):
    """Round-11 hero panel built on round-10 geometry with the two prescriptive
    fixes: a four-finger staff grip whose bottom finger now joins the same palm
    mass as the other three, and a SIDE-VIEW open hand under the FREELY FLOATING
    die. Panels differ ONLY in the side-view hand's tilt / thumb (`side_tilt` /
    `thumb_up`); the staff grip and floating die are identical across all three."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    die_cx = jester_cx - 56
    die_cy = 30
    # Side-view open hand sits a touch above the bare arm tip; a short wrist stub
    # bridges the arm tip into the slab so the profile hand reads as the same arm.
    open_hand = (die_cx + 2, die_cy + 60)
    pygame.draw.line(layer, _R11_OUTLINE, hand_up, (open_hand[0], open_hand[1] + 5), 9)
    pygame.draw.line(layer, _R11_GLOVE, hand_up, (open_hand[0], open_hand[1] + 5), 7)

    # Profile open hand UNDER the gap, then the floating die ABOVE it with its glow
    # ring + sparkles — die position + gap unchanged from round 10.
    _r11_side_open_hand(layer, open_hand, tilt=side_tilt, thumb_up=thumb_up)
    draw_cupped_die(layer, die_cx, die_cy, idx * 1.7 + die_pulse_off,
                    show_inset=False)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    shaft_w = 2
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r8_grip_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Three SIDE-VIEW open-hand reads on the SAME (Fix-1) grip + floating die: only
# the profile hand's tilt / thumb varies so the clearest read can be picked.
# side_tilt = how far the fingers angle UP toward the die; thumb_up = how raised
# the near-edge thumb sits (0 = relaxed forward, higher = clear thumb-up).
_CLOWN_R11_VARIANTS = [
    ("Flat-profile", dict(total_px=200, bauble_px=15, cup_dy=2,
                          side_tilt=0, thumb_up=0, die_pulse_off=2.0),
     "flat side profile: thin palm edge, fingers extend horizontally, thumb off the near edge"),
    ("Tilt-present", dict(total_px=200, bauble_px=15, cup_dy=2,
                          side_tilt=18, thumb_up=0, die_pulse_off=2.0),
     "side view tilted UP, presenting the layered fingers toward the floating die"),
    ("Thumb-up", dict(total_px=200, bauble_px=15, cup_dy=2,
                      side_tilt=8, thumb_up=2, die_pulse_off=2.0),
     "side view with a raised thumb-up read; fingers stacked, extending to the side"),
]


_CLOWN_R11_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 11: GRIP 4TH FINGER JOINED + DIE FLOATS OVER A SIDE-VIEW OPEN HAND (grip + die constant; only the profile hand varies)",
     (255, 255, 255)),
    ("Fix 1: ALL FOUR grip fingers now emerge from one palm mass on the right (no orphan bottom finger; thumb-over still gone). "
     "Fix 2: the open hand is now a SIDE / PROFILE view (thin slab, thumb off the near edge, layered fingers) under the same floating die. PICK ONE.",
     (205, 210, 220)),
]


def _render_clown_r11_sheet():
    """Round-11 clown look-dev: 3 hero panels of the SAME Fix-1 four-finger grip +
    freely floating die, varying only the SIDE-VIEW open hand beneath the die, plus
    the carried-over true-1x day/night shrink-test strip so both fixes are confirmed
    legible at real size. Writes docs/warren_clown/round_11.png — never overwrites
    an existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = len(_CLOWN_R11_VARIANTS)
    pad = 20
    head = 86
    name_strip = 38
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R11_HEADERS[0][0], True, _CLOWN_R11_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R11_HEADERS[1][0], True, _CLOWN_R11_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R11_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r11(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_11.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ----------------------------------------------------------------------------
#  ROUND 12 — the open "die hand" is genuinely rebuilt against real palm-up
#  references. Round 11's profile SLAB read as unnatural and (per the user) was
#  mirrored the wrong way. Real palm-up / presenting hands are NOT seen edge-on:
#  you see a broad rounded palm mass with the four fingers spreading UP and the
#  thumb branching off to ONE side. For this LEFT (screen-left) arm — the side
#  away from the body/head which sits to the right — the thumb belongs on the
#  OUTSIDE, i.e. the screen-LEFT edge. So the round-11 hand is rebuilt front-on
#  AND mirrored so the thumb lands outside, palm open. ONLY this hand changes:
#  the four-finger staff grip is byte-for-byte round 11 (reused verbatim), and
#  the floating die's position, gap, glow ring and sparkles are untouched.

_R12_GLOVE   = _R11_GLOVE
_R12_GROOVE  = _R11_GROOVE
_R12_OCCLUDE = _R11_OCCLUDE
_R12_GLOVE_HI = _R11_GLOVE_HI
_R12_OUTLINE = _R11_OUTLINE


def _r12_open_palm_hand(surf, hand, *, spread, tilt, finger_w=4):
    """A natural FRONT-ON open palm-up hand offering upward toward the floating
    die. Built to real presenting-palm references (drawing-tutorial proportions:
    palm reads as a slanted pentagon, palm width ~= middle-finger length, middle
    longest then ring/index then pinky shortest, thumb a wedge off ONE side with
    a fleshy thenar web) — NOT round 11's edge-on slab. The THUMB branches off the
    OUTSIDE (screen-LEFT) edge because this is the figure's LEFT arm and the
    body/head sit to the right. `spread` fans the four fingers apart (0 = softly
    together, higher = relaxed splay); `tilt` rotates the whole hand a touch up
    toward the die. Stays inside the round-8..11 ~16px footprint; reads as an
    OPEN PALM offering up, never a comb of stripes, a star, or a cup."""
    hx, hy = hand
    ang = math.radians(-tilt)
    ca, sa = math.cos(ang), math.sin(ang)

    def _proj(dx, dy):
        # Local hand frame (x = across the palm, +x toward the OUTSIDE/left edge;
        # y = up the hand) → screen, with the slight upward tilt applied.
        return (hx - int(round(dx * ca - dy * sa)),
                hy + int(round(-dx * sa - dy * ca)))

    # The whole open hand is laid down as ONE filled palm-up silhouette FIRST —
    # a broad rounded heel that swells across the knuckle line with the four
    # finger stubs and the thumb wedge fused into it — so the read is a single
    # open palm, not separate digits. Round 11 failed because the fingers were
    # drawn as standalone capsules with heavy grooves between them, which photographs
    # as a striped comb; here they share one mass and the grooves are only hairline
    # hints near the knuckles.
    fingers = (
        (-3.6, 9.8, -1.3),    # index  (toward the OUTSIDE/thumb side), shorter
        (-1.2, 13.4, -0.4),   # middle (clearly longest — crowns the fan)
        (1.2, 12.0, 0.4),     # ring   (a touch shorter than middle)
        (3.5, 8.8, 1.3),      # pinky  (inner side, shortest)
    )

    def _finger_endpoints(rx, ln, fan):
        base = _proj(rx, 5)
        tip = _proj(rx + fan * spread, 5 + ln)
        return base, tip

    # --- filled silhouette mass (keyline + glove) so the palm + fingers + thumb
    # read as continuous flesh, with the macaw keyline only on the outer contour.
    palm_pts_local = [
        (5.0, 1.0),    # outer (thumb-side) heel
        (5.6, 4.5),    # thumb root / thenar swell on the OUTSIDE edge
        (-4.8, 5.0),   # inner knuckle corner (pinky side)
        (-4.8, -3.0),  # inner wrist corner
        (4.6, -3.0),   # outer wrist corner
    ]
    palm_pts = [_proj(x, y) for (x, y) in palm_pts_local]
    pygame.draw.polygon(surf, _R12_OUTLINE, palm_pts)
    pygame.draw.polygon(surf, _R12_GLOVE,
                        [_proj(x * 0.92, y) for (x, y) in palm_pts_local])

    # Each finger: a fat glove capsule sharing the palm mass — outline first for the
    # whole fan, then glove fill over it so neighbours blend into one open hand and
    # only a faint groove separates them near the base.
    for rx, ln, fan in fingers:
        base, tip = _finger_endpoints(rx, ln, fan)
        pygame.draw.line(surf, _R12_OUTLINE, base, tip, finger_w + 2)
        pygame.draw.circle(surf, _R12_OUTLINE, tip, (finger_w + 2) // 2)
    for rx, ln, fan in fingers:
        base, tip = _finger_endpoints(rx, ln, fan)
        pygame.draw.line(surf, _R12_GLOVE, base, tip, finger_w)
        pygame.draw.circle(surf, _R12_GLOVE, tip, finger_w // 2)

    # Thumb: a SHORT fat wedge off the OUTSIDE (screen-LEFT) edge, angled out+up
    # and clearly separated below the index — the palm-up signature that fixes
    # round 11's wrong-side mirror. Drawn outline-then-fill so it fuses to the
    # thenar swell already in the palm polygon, reading as the same open hand.
    th_base = _proj(5.2, 1.0)
    th_tip = _proj(10.4, 4.0)
    pygame.draw.line(surf, _R12_OUTLINE, th_base, th_tip, finger_w + 2)
    pygame.draw.circle(surf, _R12_OUTLINE, th_tip, (finger_w + 2) // 2)
    pygame.draw.line(surf, _R12_GLOVE, th_base, th_tip, finger_w)
    pygame.draw.circle(surf, _R12_GLOVE, th_tip, finger_w // 2)

    # Hairline groove HINTS only between the knuckles (short, low-contrast) so the
    # fingers separate just enough to count as four without becoming a striped comb.
    for k in range(1, len(fingers)):
        rprev = fingers[k - 1][0]
        rcur = fingers[k][0]
        gv_b = _proj((rprev + rcur) / 2, 6)
        gv_t = _proj((rprev + rcur) / 2, 6 + 4)
        pygame.draw.line(surf, _R12_GROOVE, gv_b, gv_t, 1)

    # Top-left rim sheen on the palm cup + a soft highlight up the middle finger,
    # the constant macaw rim light read.
    sh = _proj(-2, 0)
    pygame.draw.circle(surf, _R12_GLOVE_HI, sh, 2)
    mb, mt = _finger_endpoints(*fingers[1])
    pygame.draw.line(surf, _R12_GLOVE_HI, (mb[0] - 1, mb[1] - 1),
                     (mt[0] - 1, mt[1] - 1), max(1, finger_w // 3))


def render_clown_staff_r12(idx, *, total_px, bauble_px, cup_dy, spread, tilt,
                           die_pulse_off=2.0):
    """Round-12 hero panel: the LOCKED round-11 four-finger staff grip and the
    untouched floating die, but the open hand beneath the die is rebuilt as a
    natural FRONT-ON open palm with the thumb on the OUTSIDE edge. Panels differ
    ONLY in the open hand's finger `spread` / upward `tilt`."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    die_cx = jester_cx - 56
    die_cy = 30
    # Open palm sits a touch above the bare arm tip; a short wrist stub bridges the
    # arm tip into the palm heel so the open hand reads as the same arm.
    open_hand = (die_cx + 2, die_cy + 60)
    pygame.draw.line(layer, _R12_OUTLINE, hand_up, (open_hand[0], open_hand[1] + 5), 9)
    pygame.draw.line(layer, _R12_GLOVE, hand_up, (open_hand[0], open_hand[1] + 5), 7)

    # Open palm-up hand UNDER the gap, then the LOCKED floating die ABOVE it with
    # its glow ring + sparkles — die position + gap unchanged from round 11.
    _r12_open_palm_hand(layer, open_hand, spread=spread, tilt=tilt)
    draw_cupped_die(layer, die_cx, die_cy, idx * 1.7 + die_pulse_off,
                    show_inset=False)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    # LOCKED round-11 staff grip, verbatim (behind → shaft → occlusion → front).
    shaft_w = 2
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r8_grip_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Three OPEN-PALM reads on the SAME locked grip + floating die: only the rebuilt
# front-on open hand's finger spread / upward tilt varies, so the most natural
# can be picked. In all three the thumb is on the OUTSIDE edge and the palm open.
_CLOWN_R12_VARIANTS = [
    ("Flat-open", dict(total_px=200, bauble_px=15, cup_dy=2,
                       spread=0.0, tilt=0, die_pulse_off=2.0),
     "flat open palm-up, fingers softly together, thumb on the OUTSIDE edge"),
    ("Relaxed-spread", dict(total_px=200, bauble_px=15, cup_dy=2,
                            spread=1.0, tilt=4, die_pulse_off=2.0),
     "relaxed open palm with a slight natural finger spread, thumb OUTSIDE"),
    ("Angled-offer", dict(total_px=200, bauble_px=15, cup_dy=2,
                          spread=0.6, tilt=12, die_pulse_off=2.0),
     "open palm angled up toward the die, easy fan, thumb OUTSIDE"),
]


_CLOWN_R12_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 12: DIE HAND REBUILT as a NATURAL OPEN PALM-UP (thumb on the OUTSIDE, palm open); LOCKED grip + floating die constant",
     (255, 255, 255)),
    ("Round 11's edge-on slab is retired: this is a front-on open presenting palm — broad palm mass, four fingers fanning UP, THUMB on the OUTSIDE (screen-left) edge. "
     "Staff grip + die unchanged. Only finger spread / upward tilt varies. PICK ONE.",
     (205, 210, 220)),
]


def _render_clown_r12_sheet():
    """Round-12 clown look-dev: 3 hero panels of the LOCKED four-finger grip +
    untouched floating die, varying only the rebuilt OPEN PALM-UP hand beneath the
    die, plus the carried-over true-1x day/night shrink-test strip so the open
    palm + outside thumb stay legible at real size. Writes
    docs/warren_clown/round_12.png — never overwrites an existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = len(_CLOWN_R12_VARIANTS)
    pad = 20
    head = 86
    name_strip = 38
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R12_HEADERS[0][0], True, _CLOWN_R12_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R12_HEADERS[1][0], True, _CLOWN_R12_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R12_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r12(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_12.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# --- ROUND 13 ----------------------------------------------------------------
#  Round 12 shipped the open palm-up read (broad palm mass, four fingers, thumb
#  on the OUTSIDE edge) but ANCHORED it below-right of the bare forearm's wrist
#  tip and drew it FLAT, so the silhouette reversed and kinked at the wrist and
#  a detached "stub" line tried to hide the gap. Round 13 keeps that #1 open
#  palm verbatim in shape and only fixes how it MEETS THE ARM: the heel is
#  re-anchored ONTO the forearm's wrist tip and the whole hand is rotated so its
#  wrist->palm axis FOLLOWS the forearm vector (up-and-left, ~47deg off vertical)
#  with a natural wrist bend — one continuous limb, no slab, no reversed kink, no
#  orphaned stub. ONLY this hand moves: the four-finger staff grip and the
#  floating die (position / gap / glow / sparkles) are reused untouched.
_R13_GLOVE   = _R12_GLOVE
_R13_GROOVE  = _R12_GROOVE
_R13_GLOVE_HI = _R12_GLOVE_HI
_R13_OUTLINE = _R12_OUTLINE

# Forearm vector of the LOCKED raised arm (shoulder->elbow->wrist tip): up-LEFT,
# ~47deg off vertical. The open hand's up-the-fingers axis is rotated onto this
# so the palm is the natural END of the arm rather than a pasted-on flat slab.
_R13_FOREARM_DEG = 47.0


def _r13_open_palm_hand(surf, hand, *, spread, wrist, finger_w=4):
    """Round-12's #1 open palm-up hand REUSED in shape (broad palm pentagon, four
    fingers fanning out — middle longest — and the THUMB as a wedge off the
    OUTSIDE edge with its thenar swell) but rotated as a whole so the wrist->palm
    axis CONTINUES THE FOREARM instead of standing flat. `hand` is the forearm's
    wrist tip: the palm heel is laid right on it so the bare arm flows straight
    into the palm. `wrist` is the total rotation of the up-the-hand axis (degrees,
    CCW toward screen-left): set near the forearm angle for a colinear read, a
    touch more to cock the open palm toward the floating die above. `spread` fans
    the four fingers. Stays inside the round-8..12 ~16px footprint; reads as ONE
    continuous limb ending in an OPEN palm, thumb on the OUTSIDE edge."""
    hx, hy = hand
    # Reuse round 12's `tilt`/`_proj` rotation math verbatim — the only change is
    # that `wrist` carries the LARGE forearm-following angle (round 12 only ever
    # passed a small `tilt`), so the whole hand swings onto the forearm axis.
    ang = math.radians(-wrist)
    ca, sa = math.cos(ang), math.sin(ang)

    def _proj(dx, dy):
        # Local hand frame (x = across the palm, +x toward the OUTSIDE/left edge;
        # y = up the hand) -> screen, rotated onto the forearm axis. The heel sits
        # a hair UP the hand from `hand` so the wrist tip lands inside the palm
        # mass (no gap, no stub) rather than at its very bottom corner.
        return (hx - int(round(dx * ca - dy * sa)),
                hy + int(round(-dx * sa - dy * ca)) - int(round(2 * ca)))

    fingers = (
        (-3.6, 9.8, -1.3),    # index  (toward the OUTSIDE/thumb side), shorter
        (-1.2, 13.4, -0.4),   # middle (clearly longest — crowns the fan)
        (1.2, 12.0, 0.4),     # ring   (a touch shorter than middle)
        (3.5, 8.8, 1.3),      # pinky  (inner side, shortest)
    )

    def _finger_endpoints(rx, ln, fan):
        base = _proj(rx, 5)
        tip = _proj(rx + fan * spread, 5 + ln)
        return base, tip

    # Filled palm-up silhouette mass FIRST (keyline + glove) so palm + fingers +
    # thumb read as continuous flesh — identical pentagon to round 12.
    palm_pts_local = [
        (5.0, 1.0),    # outer (thumb-side) heel
        (5.6, 4.5),    # thumb root / thenar swell on the OUTSIDE edge
        (-4.8, 5.0),   # inner knuckle corner (pinky side)
        (-4.8, -3.0),  # inner wrist corner
        (4.6, -3.0),   # outer wrist corner
    ]
    palm_pts = [_proj(x, y) for (x, y) in palm_pts_local]
    pygame.draw.polygon(surf, _R13_OUTLINE, palm_pts)
    pygame.draw.polygon(surf, _R13_GLOVE,
                        [_proj(x * 0.92, y) for (x, y) in palm_pts_local])

    for rx, ln, fan in fingers:
        base, tip = _finger_endpoints(rx, ln, fan)
        pygame.draw.line(surf, _R13_OUTLINE, base, tip, finger_w + 2)
        pygame.draw.circle(surf, _R13_OUTLINE, tip, (finger_w + 2) // 2)
    for rx, ln, fan in fingers:
        base, tip = _finger_endpoints(rx, ln, fan)
        pygame.draw.line(surf, _R13_GLOVE, base, tip, finger_w)
        pygame.draw.circle(surf, _R13_GLOVE, tip, finger_w // 2)

    # Thumb: SHORT fat wedge off the OUTSIDE edge, angled out+up — the palm-up
    # signature, fused to the thenar swell already in the palm polygon.
    th_base = _proj(5.2, 1.0)
    th_tip = _proj(10.4, 4.0)
    pygame.draw.line(surf, _R13_OUTLINE, th_base, th_tip, finger_w + 2)
    pygame.draw.circle(surf, _R13_OUTLINE, th_tip, (finger_w + 2) // 2)
    pygame.draw.line(surf, _R13_GLOVE, th_base, th_tip, finger_w)
    pygame.draw.circle(surf, _R13_GLOVE, th_tip, finger_w // 2)

    # Hairline groove HINTS only between knuckles so the fingers count as four
    # without becoming a striped comb.
    for k in range(1, len(fingers)):
        rprev = fingers[k - 1][0]
        rcur = fingers[k][0]
        gv_b = _proj((rprev + rcur) / 2, 6)
        gv_t = _proj((rprev + rcur) / 2, 6 + 4)
        pygame.draw.line(surf, _R13_GROOVE, gv_b, gv_t, 1)

    # Top-left rim sheen on the palm + a soft highlight up the middle finger.
    sh = _proj(-2, 0)
    pygame.draw.circle(surf, _R13_GLOVE_HI, sh, 2)
    mb, mt = _finger_endpoints(*fingers[1])
    pygame.draw.line(surf, _R13_GLOVE_HI, (mb[0] - 1, mb[1] - 1),
                     (mt[0] - 1, mt[1] - 1), max(1, finger_w // 3))


def render_clown_staff_r13(idx, *, total_px, bauble_px, cup_dy, spread, wrist,
                           die_pulse_off=2.0):
    """Round-13 hero panel: LOCKED round-11 four-finger staff grip + untouched
    floating die, but the open hand is re-anchored onto the raised forearm's
    wrist tip and rotated so its axis FOLLOWS the forearm — one continuous limb.
    Panels differ ONLY in how much the wrist follows the forearm vs. cocks toward
    the die (`wrist`) and the finger `spread`."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    die_cx = jester_cx - 56
    die_cy = 30
    # The open hand is anchored ON the forearm's wrist tip (`hand_up`) — NOT below
    # and to the right of it as in round 12 — so the bare forearm flows straight
    # into the palm heel with no detached stub and no drop-below-wrist reversal.
    open_hand = (hand_up[0], hand_up[1])

    # Open palm-up hand AT the wrist tip, axis along the forearm, then the LOCKED
    # floating die ABOVE it with its glow ring + sparkles — die unchanged.
    _r13_open_palm_hand(layer, open_hand, spread=spread, wrist=wrist)
    draw_cupped_die(layer, die_cx, die_cy, idx * 1.7 + die_pulse_off,
                    show_inset=False)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    # LOCKED round-11 staff grip, verbatim (behind -> shaft -> occlusion -> front).
    shaft_w = 2
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r8_grip_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Three CONTINUATION reads on the SAME locked grip + floating die: only how much
# the open hand follows the forearm vs. cocks toward the die varies. The forearm
# is ~47deg up-left; (a) sits the palm axis right on it, (b) bends a touch off it,
# (c) cocks a little further so the open palm aims more at the floating die.
_CLOWN_R13_VARIANTS = [
    ("Inline", dict(total_px=200, bauble_px=15, cup_dy=2,
                    spread=0.7, wrist=_R13_FOREARM_DEG, die_pulse_off=2.0),
     "palm axis fully colinear with the forearm — the straightest continuation"),
    ("Soft-bend", dict(total_px=200, bauble_px=15, cup_dy=2,
                       spread=0.8, wrist=_R13_FOREARM_DEG - 12, die_pulse_off=2.0),
     "a gentle natural wrist bend off the forearm axis"),
    ("Cocked", dict(total_px=200, bauble_px=15, cup_dy=2,
                    spread=0.9, wrist=_R13_FOREARM_DEG - 24, die_pulse_off=2.0),
     "wrist cocked a touch further so the open palm aims more toward the die"),
]


_CLOWN_R13_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 13: open DIE HAND now CONTINUES THE RAISED ARM (heel on the wrist tip, axis along the forearm); LOCKED grip + floating die constant",
     (255, 255, 255)),
    ("Round 12's flat palm pasted below-right of the wrist is retired: the same open palm (thumb OUTSIDE) is re-anchored ONTO the forearm's wrist tip and rotated onto the forearm axis "
     "so arm->wrist->palm reads as ONE limb. Only wrist-follow vs. die-cock varies. PICK ONE.",
     (205, 210, 220)),
]


def _render_clown_r13_sheet():
    """Round-13 clown look-dev: 3 hero panels of the LOCKED four-finger grip +
    untouched floating die, varying only how much the re-anchored OPEN PALM
    follows the forearm vs. cocks toward the die, plus the carried-over true-1x
    day/night shrink-test strip so the continuation + outside thumb stay legible
    at real size. Writes docs/warren_clown/round_13.png — never overwrites an
    existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = len(_CLOWN_R13_VARIANTS)
    pad = 20
    head = 86
    name_strip = 38
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R13_HEADERS[0][0], True, _CLOWN_R13_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R13_HEADERS[1][0], True, _CLOWN_R13_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R13_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r13(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_13.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ---------------------------------------------------------------------------
# ROUND 14 — back-of-hand read: the thumb moves BEHIND the open palm.
#
#  Round 13 locked Variation 1 "Inline (47deg)" as the winner: the open hand
#  reads as a natural continuation of the raised arm. But its thumb sat on the
#  FRONT/near OUTSIDE edge, projecting toward the viewer (palm-facing-us read).
#  The user wants the BACK of the hand: the thumb belongs on the FAR/rear edge,
#  tucked behind the palm mass rather than projecting forward. Drawing the thumb
#  FIRST (so the filled palm polygon paints over it) and re-rooting it on the
#  rear/inner side flips the read from palm-toward-us to knuckles-toward-us.
#  Everything else from Inline (47deg) is kept verbatim: broad palm pentagon,
#  four fingers (middle longest) fanning up-left along the forearm vector, die
#  floating free with a gap, arm->wrist->palm as one continuous limb.
_R14_GLOVE    = _R13_GLOVE
_R14_GROOVE   = _R13_GROOVE
_R14_GLOVE_HI = _R13_GLOVE_HI
_R14_OUTLINE  = _R13_OUTLINE

# Inherit Inline's locked forearm-following angle so the continuation is identical.
_R14_FOREARM_DEG = _R13_FOREARM_DEG


def _r14_open_palm_hand(surf, hand, *, spread, wrist, finger_w=4,
                        thumb_base, thumb_tip, thumb_behind=True,
                        thenar_x=4.8):
    """Round-13 Inline open palm REUSED verbatim in shape and continuation, with
    the ONLY change being the THUMB moved to the BACK of the hand so we read the
    knuckle side facing us instead of the palm. Local hand frame is unchanged
    (x = across the palm, +x toward the OUTSIDE/left edge; y = up the hand) and
    the wrist->palm axis still FOLLOWS the forearm vector. `thumb_base`/`thumb_tip`
    are local (x, y) endpoints re-rooted toward the FAR/rear edge; when
    `thumb_behind` is set the thumb is painted FIRST so the filled palm polygon
    occludes most of it — only the rear hint survives, giving a clean back-of-hand
    silhouette. `thenar_x` pulls the palm's thumb-root corner IN off the outside
    edge (the thenar swell that fronted the palm-up read is flattened, since on the
    back of the hand the thumb root sits behind, not bulging toward us)."""
    hx, hy = hand
    ang = math.radians(-wrist)
    ca, sa = math.cos(ang), math.sin(ang)

    def _proj(dx, dy):
        # Identical projection to round 13 — heel laid a hair up the hand so the
        # wrist tip lands inside the palm mass (continuous limb, no stub/gap).
        return (hx - int(round(dx * ca - dy * sa)),
                hy + int(round(-dx * sa - dy * ca)) - int(round(2 * ca)))

    fingers = (
        (-3.6, 9.8, -1.3),    # index  (toward the OUTSIDE edge), shorter
        (-1.2, 13.4, -0.4),   # middle (clearly longest — crowns the fan)
        (1.2, 12.0, 0.4),     # ring   (a touch shorter than middle)
        (3.5, 8.8, 1.3),      # pinky  (inner side, shortest)
    )

    def _finger_endpoints(rx, ln, fan):
        base = _proj(rx, 5)
        tip = _proj(rx + fan * spread, 5 + ln)
        return base, tip

    def _draw_thumb():
        th_base = _proj(*thumb_base)
        th_tip = _proj(*thumb_tip)
        pygame.draw.line(surf, _R14_OUTLINE, th_base, th_tip, finger_w + 2)
        pygame.draw.circle(surf, _R14_OUTLINE, th_tip, (finger_w + 2) // 2)
        pygame.draw.line(surf, _R14_GLOVE, th_base, th_tip, finger_w)
        pygame.draw.circle(surf, _R14_GLOVE, th_tip, finger_w // 2)

    # Back-of-hand order: the thumb goes DOWN FIRST so the palm paints over it.
    if thumb_behind:
        _draw_thumb()

    # Filled silhouette mass (keyline + glove). The thenar swell that bulged off
    # the OUTSIDE edge in round 13 is pulled in (`thenar_x`) because on the back
    # of the hand the thumb root sits behind the knuckle line, not in front.
    palm_pts_local = [
        (5.0, 1.0),        # outer heel
        (thenar_x, 4.5),   # thumb-root corner pulled IN (no forward thenar bulge)
        (-4.8, 5.0),       # inner knuckle corner (pinky side)
        (-4.8, -3.0),      # inner wrist corner
        (4.6, -3.0),       # outer wrist corner
    ]
    palm_pts = [_proj(x, y) for (x, y) in palm_pts_local]
    pygame.draw.polygon(surf, _R14_OUTLINE, palm_pts)
    pygame.draw.polygon(surf, _R14_GLOVE,
                        [_proj(x * 0.92, y) for (x, y) in palm_pts_local])

    for rx, ln, fan in fingers:
        base, tip = _finger_endpoints(rx, ln, fan)
        pygame.draw.line(surf, _R14_OUTLINE, base, tip, finger_w + 2)
        pygame.draw.circle(surf, _R14_OUTLINE, tip, (finger_w + 2) // 2)
    for rx, ln, fan in fingers:
        base, tip = _finger_endpoints(rx, ln, fan)
        pygame.draw.line(surf, _R14_GLOVE, base, tip, finger_w)
        pygame.draw.circle(surf, _R14_GLOVE, tip, finger_w // 2)

    # A back-of-hand thumb on the rear edge (variations 2/3) is still drawn last
    # for the surviving sliver only if it is NOT meant to be occluded — but here
    # all three move it behind, so the post-palm pass is skipped. Knuckle dimples
    # along the finger roots sell the BACK of the hand facing us.
    for k in range(len(fingers)):
        rx = fingers[k][0]
        kn = _proj(rx, 4.6)
        pygame.draw.circle(surf, _R14_GROOVE, kn, 1)

    # Hairline grooves between fingers — four distinct digits, not a striped comb.
    for k in range(1, len(fingers)):
        rprev = fingers[k - 1][0]
        rcur = fingers[k][0]
        gv_b = _proj((rprev + rcur) / 2, 6)
        gv_t = _proj((rprev + rcur) / 2, 6 + 4)
        pygame.draw.line(surf, _R14_GROOVE, gv_b, gv_t, 1)

    # Top-left rim sheen on the palm + a soft highlight up the middle finger.
    sh = _proj(-2, 0)
    pygame.draw.circle(surf, _R14_GLOVE_HI, sh, 2)
    mb, mt = _finger_endpoints(*fingers[1])
    pygame.draw.line(surf, _R14_GLOVE_HI, (mb[0] - 1, mb[1] - 1),
                     (mt[0] - 1, mt[1] - 1), max(1, finger_w // 3))


def render_clown_staff_r14(idx, *, total_px, bauble_px, cup_dy, spread, wrist,
                           thumb_base, thumb_tip, thenar_x=4.8,
                           die_pulse_off=2.0):
    """Round-14 hero panel: identical to round-13 Inline (LOCKED grip + untouched
    floating die + continuous-limb open palm on the forearm wrist tip) except the
    open hand's THUMB is re-rooted BEHIND the palm so the BACK of the hand faces
    the viewer. Panels differ ONLY in how far the thumb tucks behind."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    die_cx = jester_cx - 56
    die_cy = 30
    # Open hand anchored ON the forearm's wrist tip (continuation), unchanged.
    open_hand = (hand_up[0], hand_up[1])

    _r14_open_palm_hand(layer, open_hand, spread=spread, wrist=wrist,
                        thumb_base=thumb_base, thumb_tip=thumb_tip,
                        thenar_x=thenar_x)
    draw_cupped_die(layer, die_cx, die_cy, idx * 1.7 + die_pulse_off,
                    show_inset=False)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    # LOCKED round-11 staff grip, verbatim (behind -> shaft -> occlusion -> front).
    shaft_w = 2
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r8_grip_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Three back-of-hand reads on the SAME locked grip + floating die + locked Inline
# continuation: ONLY how far the thumb tucks behind varies. The thumb was on the
# FRONT outside edge in round 13 (local ~base (5.2,1.0) -> tip (10.4,4.0), out+up
# toward the viewer); here every variant moves it to the FAR/rear side so the
# knuckles face us. The palm thenar corner is also pulled in so no forward bulge
# survives.
_CLOWN_R14_VARIANTS = [
    # 1. Thumb fully behind: rooted on the inner/rear wrist corner and short, so the
    #    palm polygon paints over nearly all of it — only a hint peeks at the rear
    #    edge. Cleanest back-of-hand read.
    ("Thumb fully behind",
     dict(total_px=200, bauble_px=15, cup_dy=2, spread=0.7,
          wrist=_R14_FOREARM_DEG,
          thumb_base=(-3.4, -1.0), thumb_tip=(-5.4, 2.2),
          thenar_x=4.4, die_pulse_off=2.0),
     "thumb almost fully occluded behind the palm — only a hint at the rear edge"),
    # 2. Thumb rear-edge: visible running DOWN the far/outside-rear edge but clearly
    #    on the back side (rooted high, angled back-and-down, NOT projecting forward).
    ("Thumb rear-edge",
     dict(total_px=200, bauble_px=15, cup_dy=2, spread=0.7,
          wrist=_R14_FOREARM_DEG,
          thumb_base=(4.8, 2.0), thumb_tip=(6.0, -2.4),
          thenar_x=4.6, die_pulse_off=2.0),
     "thumb visible along the far/rear edge, clearly behind, not projecting forward"),
    # 3. Thumb tucked-low: low and behind near the wrist HEEL on the rear side, the
    #    knuckle-side read with the thumb almost in the wrist shadow.
    ("Thumb tucked-low",
     dict(total_px=200, bauble_px=15, cup_dy=2, spread=0.7,
          wrist=_R14_FOREARM_DEG,
          thumb_base=(4.2, -1.6), thumb_tip=(5.6, -4.6),
          thenar_x=4.6, die_pulse_off=2.0),
     "thumb low and behind, near the wrist heel on the rear side"),
]


_CLOWN_R14_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 14: THUMB MOVED TO THE BACK of the open DIE HAND (back-of-hand / knuckle side faces us); LOCKED grip + floating die + Inline continuation constant",
     (255, 255, 255)),
    ("Round 13's winner (Inline 47deg) kept verbatim — broad open palm, four fingers fanning up-left along the forearm, die floating free with a gap, arm->wrist->palm as ONE limb — but the thumb that "
     "projected off the FRONT outside edge is re-rooted BEHIND the hand so the knuckle side reads. Only how far the thumb tucks behind varies. PICK ONE.",
     (205, 210, 220)),
]


def _render_clown_r14_sheet():
    """Round-14 clown look-dev: 3 hero panels of the LOCKED four-finger grip +
    untouched floating die + locked Inline continuation, varying only how far the
    open hand's THUMB tucks BEHIND the palm so the BACK of the hand faces us, plus
    the carried-over true-1x day/night shrink-test strip so the back-of-hand read
    + continuation + open-palm hold stay legible at real size. Writes
    docs/warren_clown/round_14.png — never overwrites an existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = len(_CLOWN_R14_VARIANTS)
    pad = 20
    head = 86
    name_strip = 38
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R14_HEADERS[0][0], True, _CLOWN_R14_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R14_HEADERS[1][0], True, _CLOWN_R14_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R14_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r14(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_14.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ---------------------------------------------------------------------------
# ROUND 15 — the open DIE HAND rebuilt FROM SCRATCH on real hand proportions.
#
#  Rounds 11-14 only ever TWEAKED one polygon: a near-rectangular palm pentagon
#  whose four fingers all rooted on ONE flat local line as uniform straight
#  sausages, with the thumb hung off a palm corner. The user rejected ~6 rounds
#  of that as not anatomically plausible and asked for a redesign from real
#  proportions. `_r15_open_hand` THROWS OUT the r14 shape and rebuilds the hand
#  from human ratios (measured against the ~16px footprint so it survives the
#  true-1x shrink): a TAPERED palm (narrow wrist -> wide knuckles), an ARCHED
#  knuckle line with the pinky knuckle set lower/more proximal, fingers that are
#  GENTLY CURVED 3-segment arcs (middle longest -> pinky shortest) tapering to
#  the tips, and a SHORT 2-segment thumb rooted at the WRIST via a triangular
#  thenar wedge at ~45deg. Anatomy lives entirely in shape/arc/taper, never in
#  bulk, so the compact route silhouette is preserved.
#
#  KEPT verbatim from the already-approved r13/r14 read: the heel-on-wrist anchor
#  and the `_proj` rotation that aligns the wrist->palm axis to the forearm's
#  ~47deg up-left vector, so arm->wrist->palm still reads as ONE continuous limb.
#  Also reused untouched: the LOCKED staff-grip hand `_r11_grip_glove` and the
#  floating die `draw_cupped_die` (same call, same gap/glow/sparkles). ONLY the
#  open-hand SHAPE downstream of the anchor is new.
_R15_GLOVE    = _R14_GLOVE
_R15_GROOVE   = _R14_GROOVE
_R15_GLOVE_HI = _R14_GLOVE_HI
_R15_OUTLINE  = _R14_OUTLINE
_R15_FOREARM_DEG = _R14_FOREARM_DEG


def _r15_open_hand(surf, hand, *, wrist, curl, spread, cup=0.0,
                   thumb_side=1, thumb_behind=False, base_w=4):
    """Open hand built FROM SCRATCH on human proportions inside the ~16px
    footprint. Local frame matches r13/r14 (x = across the palm, +x toward the
    OUTSIDE/left edge; y = up the hand); `_proj` roots the wrist heel on the
    forearm tip `hand` and rotates the up-the-hand axis onto the forearm vector
    (`wrist` deg), so the bare arm flows straight into the palm — the approved
    one-continuous-limb read, unchanged.

    Anatomy parameters drive the NEW shape:
      `curl`   how far the fingers flex toward the palm (0 = open splay, 1 =
               curled into a cup beneath the die); also deepens the fingertip arc.
      `spread` lateral fan of the fingers.
      `cup`    bows the whole hand into an offering cup (palm-toward-viewer reads).
      `thumb_side` +1 puts the thumb on the OUTSIDE/near edge (3-4 reads), -1 on
               the FAR/rear edge (back-of-hand read).
      `thumb_behind` paints the thumb FIRST so the palm occludes it (back of hand).
    """
    hx, hy = hand
    ang = math.radians(-wrist)
    ca, sa = math.cos(ang), math.sin(ang)

    def _proj(dx, dy):
        # Heel laid a hair up the hand so the forearm tip lands INSIDE the palm
        # mass (continuous limb, no stub/gap) — the locked r13/r14 anchor math.
        return (hx - int(round(dx * ca - dy * sa)),
                hy + int(round(-dx * sa - dy * ca)) - int(round(2 * ca)))

    # --- Knuckle ARCH: each finger roots at its OWN (x, y), not one flat line.
    # The hand WIDENS from a narrow wrist to the spread knuckles; the knuckle row
    # bows UP in the middle (arch) and the pinky knuckle sits LOWER / more
    # proximal. Roots are ordered outside(index) -> inside(pinky).
    KW = 5.6                       # half-width across the knuckle row (wide end)
    knuckles = (
        # rx (across)         ky (root height, the arch)   length   curve sign
        (-KW * 0.82,          7.4,                          9.6,    -1.0),  # index
        (-KW * 0.30,          8.1,                         11.4,    -0.4),  # middle (longest, crown)
        ( KW * 0.30,          7.8,                         10.7,     0.4),  # ring (~index, a hair longer)
        ( KW * 0.86,          6.4,                          7.7,     1.1),  # pinky (shortest, knuckle LOW)
    )

    def _finger_arc(rx, ky, ln, curve):
        # A relaxed open finger is a gentle ARC of three segments, never a rod:
        # lay 4 points (knuckle -> two joints -> tip) along a quadratic that bows
        # sideways with `curve`/`spread` and flexes toward the palm with `curl`.
        # The middle phalanx is the longest segment, the tip the shortest.
        segs = (0.0, 0.40, 0.74, 1.0)        # cumulative length: mid seg longest
        pts = []
        for t in segs:
            up = ky + ln * t
            # sideways bow grows toward the tip (fan); cup/curl pull the tip in
            # and DOWN so the fingers close into an offering arc.
            bow = (curve * spread) * (t * t)
            flex = curl * (t * t) * (3.4 + 1.6 * cup)
            pts.append((rx + bow, up - flex))
        return [_proj(x, y) for (x, y) in pts]

    def _taper_w(t):
        # Fingers taper tip-ward; never thinner than the keyline reads at 1x.
        return max(2, int(round(base_w - 1.4 * t)))

    # --- Thumb: SHORT, 2 segments, rooted at the WRIST via a thenar wedge, ~45deg
    # off the index. Reaches only ~to the base of the fingers (much shorter than
    # r14). Side + visibility follow the orientation.
    tx = thumb_side
    thenar = [
        _proj(tx * 4.2, -1.6),     # wrist root, outside
        _proj(tx * 6.4, 1.2),      # thenar swell apex
        _proj(tx * 3.0, 3.4),      # blends back into the palm near the index
    ]
    th_knuckle = _proj(tx * 6.0, 1.0)
    th_mid = _proj(tx * 7.6 + tx * spread * 0.6, 3.4)
    th_tip = _proj(tx * 7.4 + tx * spread * 0.8, 5.8)

    def _draw_thumb():
        pygame.draw.polygon(surf, _R15_OUTLINE, thenar)
        pygame.draw.polygon(surf, _R15_GLOVE, thenar)
        pygame.draw.line(surf, _R15_OUTLINE, th_knuckle, th_mid, base_w + 2)
        pygame.draw.line(surf, _R15_OUTLINE, th_mid, th_tip, base_w + 1)
        pygame.draw.circle(surf, _R15_OUTLINE, th_tip, (base_w + 1) // 2)
        pygame.draw.line(surf, _R15_GLOVE, th_knuckle, th_mid, base_w)
        pygame.draw.line(surf, _R15_GLOVE, th_mid, th_tip, base_w - 1)
        pygame.draw.circle(surf, _R15_GLOVE, th_tip, base_w // 2)

    if thumb_behind:
        _draw_thumb()

    # --- TAPERED palm mass: a narrow wrist that widens across the knuckle row,
    # the top edge following the knuckle ARCH (NOT a flat rectangle). Walk the
    # outline up the outside edge, across the arched knuckles, down the inside.
    WW = 3.4                       # half-width at the wrist (narrow end)
    palm_local = [
        (-WW, -3.4),               # inner wrist corner (narrow)
        (-KW * 0.92, 6.6),         # widen out to the pinky-side knuckle base
        (knuckles[3][0], knuckles[3][1] - 0.6),  # pinky knuckle (low)
        (knuckles[2][0], knuckles[2][1]),        # ring knuckle (arch)
        (knuckles[1][0], knuckles[1][1] + 0.2),  # middle knuckle (arch crown)
        (knuckles[0][0], knuckles[0][1]),        # index knuckle (arch)
        (KW * 0.96, 6.2),          # widen out to the index/thumb-side knuckle base
        (WW + 0.6, -3.4),          # outer wrist corner (narrow)
    ]
    palm_pts = [_proj(x, y) for (x, y) in palm_local]
    pygame.draw.polygon(surf, _R15_OUTLINE, palm_pts)
    pygame.draw.polygon(surf, _R15_GLOVE,
                        [_proj(x * 0.9, y) for (x, y) in palm_local])

    # Thumb on the NEAR side draws AFTER the palm so it overlaps the heel.
    if not thumb_behind:
        _draw_thumb()

    # --- Fingers: keyline pass then glove pass, each a curved tapered poly-line
    # of three segments so the joints + bow read; tips are rounded caps.
    arcs = [(_finger_arc(rx, ky, ln, cv), ln) for (rx, ky, ln, cv) in knuckles]
    for col, lw_off in ((_R15_OUTLINE, 2), (_R15_GLOVE, 0)):
        for pts, ln in arcs:
            for i in range(len(pts) - 1):
                t = i / (len(pts) - 1)
                w = _taper_w(t) + lw_off
                pygame.draw.line(surf, col, pts[i], pts[i + 1], w)
            tipw = (_taper_w(1.0) + lw_off) // 2
            pygame.draw.circle(surf, col, pts[-1], max(1, tipw))

    # --- Legible-but-light detail: knuckle dimples along the arch, a hairline
    # groove between each finger, a thumb-crease, and rim sheen. Kept sparse so
    # it doesn't turn to noise at 1x.
    for rx, ky, ln, cv in knuckles:
        pygame.draw.circle(surf, _R15_GROOVE, _proj(rx, ky - 0.4), 1)
    for k in range(1, len(knuckles)):
        midx = (knuckles[k - 1][0] + knuckles[k][0]) / 2
        midy = (knuckles[k - 1][1] + knuckles[k][1]) / 2
        gv_b = _proj(midx, midy - 1.2)
        gv_t = _proj(midx, midy + 2.4)
        pygame.draw.line(surf, _R15_GROOVE, gv_b, gv_t, 1)

    # Rim sheen on the wide knuckle ridge + a soft highlight up the middle finger.
    pygame.draw.circle(surf, _R15_GLOVE_HI, _proj(-KW * 0.30, 6.6), 2)
    mid_pts = arcs[1][0]
    pygame.draw.line(surf, _R15_GLOVE_HI,
                     (mid_pts[0][0] - 1, mid_pts[0][1] - 1),
                     (mid_pts[-1][0] - 1, mid_pts[-1][1] - 1),
                     max(1, base_w // 3))


def render_clown_staff_r15(idx, *, total_px, bauble_px, cup_dy, wrist, curl,
                           spread, cup=0.0, thumb_side=1, thumb_behind=False,
                           die_pulse_off=2.0):
    """Round-15 hero panel: the LOCKED staff grip + untouched floating die + the
    approved continuous-limb anchor, with the open die hand replaced by the new
    from-scratch `_r15_open_hand`. Panels differ ONLY in the hand's orientation /
    curl params (relaxed 3-4, cupped-up, or back-of-hand)."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    die_cx = jester_cx - 56
    die_cy = 30
    # Open hand anchored ON the forearm's wrist tip (the approved continuation).
    open_hand = (hand_up[0], hand_up[1])

    _r15_open_hand(layer, open_hand, wrist=wrist, curl=curl, spread=spread,
                   cup=cup, thumb_side=thumb_side, thumb_behind=thumb_behind)
    draw_cupped_die(layer, die_cx, die_cy, idx * 1.7 + die_pulse_off,
                    show_inset=False)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    # LOCKED round-11 staff grip, verbatim (behind -> shaft -> occlusion -> front).
    shaft_w = 2
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r8_grip_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# Five orientations of the SAME new from-scratch hand on the SAME locked grip +
# floating die + continuation anchor — only the hand's orientation/curl params
# differ. The user picks the orientation by SEEING it (a text question failed).
_CLOWN_R15_VARIANTS = [
    # 1-2 RELAXED 3/4 OPEN HAND — natural slightly-turned hand, gently curved
    #     fingers, thumb on the NEAR/outside edge. Two curl/spread degrees.
    ("Relaxed 3/4 - soft",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R15_FOREARM_DEG,
          curl=0.22, spread=0.9, cup=0.0, thumb_side=1, die_pulse_off=2.0),
     "natural 3/4 hand, gently curved fingers, thumb reading on the near side"),
    ("Relaxed 3/4 - open",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R15_FOREARM_DEG,
          curl=0.10, spread=1.15, cup=0.0, thumb_side=1, die_pulse_off=2.0),
     "same hand, fingers more open + spread, thumb splayed on the near side"),
    # 3-4 OPEN PALM CUPPED UPWARD — palm toward viewer, fingers curl into an
    #     offering cup beneath the die, thumb out to the side. Two cup depths.
    ("Cupped up - shallow",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R15_FOREARM_DEG - 6,
          curl=0.40, spread=0.8, cup=0.6, thumb_side=1, die_pulse_off=2.0),
     "palm up, fingers curl into a shallow offering cup beneath the die"),
    ("Cupped up - deep",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R15_FOREARM_DEG - 10,
          curl=0.62, spread=0.7, cup=1.0, thumb_side=1, die_pulse_off=2.0),
     "deeper cup, fingertips arc up to cradle the die, thumb out to the side"),
    # 5 BACK OF HAND — knuckles to viewer, thumb LOW on the far side, rebuilt on
    #   this arch/taper anatomy (the r14 direction, done right).
    ("Back of hand",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R15_FOREARM_DEG,
          curl=0.18, spread=0.95, cup=0.0, thumb_side=-1, thumb_behind=True,
          die_pulse_off=2.0),
     "knuckles to viewer, short thumb low on the far side, arched knuckle row"),
]


_CLOWN_R15_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 15: open DIE HAND REBUILT FROM SCRATCH on real proportions (tapered palm, arched knuckles, curved tapered fingers, wrist-rooted short thumb); LOCKED grip + floating die + continuation constant",
     (255, 255, 255)),
    ("Same NEW from-scratch hand in 5 orientations — pick one. 1-2 relaxed 3/4 (thumb near), 3-4 palm cupped up beneath the die, 5 back of hand. Narrow wrist widens to an ARCHED knuckle row (pinky lowest); fingers curve + taper "
     "(middle longest, pinky shortest); the SHORT thumb roots at the wrist ~45deg. Arm->wrist->palm stays ONE limb; die floats free with its gap.",
     (205, 210, 220)),
]


def _render_clown_r15_sheet():
    """Round-15 clown look-dev: 5 hero panels of the LOCKED four-finger grip +
    untouched floating die + approved continuation anchor, with the open die hand
    rebuilt FROM SCRATCH (`_r15_open_hand`) and shown in 5 orientations so the
    user can PICK the pose by seeing it, plus the carried-over true-1x day/night
    shrink-test strip so the new hand reads at real size. Writes
    docs/warren_clown/round_15.png — never overwrites an existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)

    cols = len(_CLOWN_R15_VARIANTS)
    pad = 20
    head = 86
    name_strip = 38
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R15_HEADERS[0][0], True, _CLOWN_R15_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R15_HEADERS[1][0], True, _CLOWN_R15_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R15_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        clown = render_clown_staff_r15(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_15.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# ---------------------------------------------------------------------------
# ROUND 16 — make the round-15 anatomy LEGIBLE + two small shape fixes.
#
#  Round 15 cleared the silhouette bar (no more slab/blob/star) but the sheet
#  showed only full clown figures (~12px hand) + a 1x strip, so the four
#  rejected-six-times landmarks (knuckle arch, pinky-lower, wrist-rooted short
#  thumb, finger taper) were never legible enough to verify. Round 16 keeps the
#  SAME 5 orientations and the SAME figure but ADDS a big isolated HERO-ZOOM
#  crop of just the open hand per panel (scaled ~7x off a neutral card, no busy
#  sky, no die glow on the flesh) so the anatomy can actually be judged.
#
#  Two shape fixes ride along, scoped to the open hand only:
#    - V2 "Relaxed 3/4 - open": the inter-finger fan is softened ~18% so the
#      open hand stops reading as a spiky star at gameplay scale, while still
#      splaying clearly at hero zoom (the fan now compresses as spread climbs).
#    - V5 "Back of hand": the knuckle top edge is given a touch more arch (and
#      the pinky a touch lower) so from the back it visibly CURVES, never a flat
#      paddle edge.
#  Everything else is locked: the same glove palette, the heel-on-wrist anchor +
#  `_proj` ~47deg continuation, the LOCKED `_r11_grip_glove`, and the floating
#  `draw_cupped_die` (same gap/glow/sparkles). The die's glow lives in
#  draw_cupped_die and is only ever painted around the FLOATING die — the crop
#  omits the die entirely, so flesh/glove never blooms.
_R16_GLOVE    = _R15_GLOVE
_R16_GROOVE   = _R15_GROOVE
_R16_GLOVE_HI = _R15_GLOVE_HI
_R16_OUTLINE  = _R15_OUTLINE
_R16_FOREARM_DEG = _R15_FOREARM_DEG


def _r16_open_hand(surf, hand, *, wrist, curl, spread, cup=0.0,
                   thumb_side=1, thumb_behind=False, base_w=4, back_arch=False):
    """Round-16 open hand: the approved from-scratch r15 anatomy with two scoped
    shape fixes. Identical local frame + `_proj` continuation as r15.

    Fixes vs r15:
      - The lateral finger fan now COMPRESSES as `spread` climbs (a relaxed open
        hand fans the fingers a little, not into a star): the per-finger bow is
        damped by `1/(1 + k*spread)`, so a high `spread` still separates the
        fingers at hero zoom but collapses gracefully — no spikes — at true 1x.
      - `back_arch` deepens the knuckle-row arch and drops the pinky knuckle a
        hair more, used for the back-of-hand read where the top edge IS the
        knuckle line and must visibly curve rather than read as a flat paddle.
    """
    hx, hy = hand
    ang = math.radians(-wrist)
    ca, sa = math.cos(ang), math.sin(ang)

    def _proj(dx, dy):
        # Heel laid a hair up the hand so the forearm tip lands INSIDE the palm
        # mass (continuous limb, no stub/gap) — the locked r13/r14/r15 anchor.
        return (hx - int(round(dx * ca - dy * sa)),
                hy + int(round(-dx * sa - dy * ca)) - int(round(2 * ca)))

    # --- Knuckle ARCH: each finger roots at its OWN (x, y), not one flat line.
    # `back_arch` lifts the middle/ring crown and drops the pinky so the row
    # curves harder when the knuckles face the viewer.
    arch_lift = 0.6 if back_arch else 0.0
    pinky_drop = 0.7 if back_arch else 0.0
    KW = 5.6                       # half-width across the knuckle row (wide end)
    knuckles = (
        # rx (across)    ky (root height, the arch)        length   curve sign
        (-KW * 0.82,     7.4,                                9.6,    -1.0),  # index
        (-KW * 0.30,     8.1 + arch_lift,                   11.4,    -0.4),  # middle (longest, crown)
        ( KW * 0.30,     7.8 + arch_lift,                   10.7,     0.4),  # ring (~index, a hair longer)
        ( KW * 0.86,     6.4 - pinky_drop,                   7.7,     1.1),  # pinky (shortest, knuckle LOW)
    )

    # A relaxed open hand fans the fingers a touch, not into a spiky star: damp
    # the lateral bow as spread climbs so the splay reads at hero zoom yet stops
    # the fingers separating into spikes at gameplay-scale 1x.
    fan = 1.0 / (1.0 + 0.55 * max(0.0, spread))

    def _finger_arc(rx, ky, ln, curve):
        # A relaxed open finger is a gentle ARC of three segments, never a rod:
        # lay 4 points (knuckle -> two joints -> tip) along a quadratic that bows
        # sideways with `curve`/`spread` and flexes toward the palm with `curl`.
        # The middle phalanx is the longest segment, the tip the shortest.
        segs = (0.0, 0.40, 0.74, 1.0)        # cumulative length: mid seg longest
        pts = []
        for t in segs:
            up = ky + ln * t
            bow = (curve * spread * fan) * (t * t)
            flex = curl * (t * t) * (3.4 + 1.6 * cup)
            pts.append((rx + bow, up - flex))
        return [_proj(x, y) for (x, y) in pts]

    def _taper_w(t):
        # Fingers taper tip-ward; never thinner than the keyline reads at 1x.
        return max(2, int(round(base_w - 1.4 * t)))

    # --- Thumb: SHORT, 2 segments, rooted at the WRIST via a thenar wedge,
    # ~45deg off the index, reaching only ~to the base of the fingers.
    tx = thumb_side
    thenar = [
        _proj(tx * 4.2, -1.6),     # wrist root, outside
        _proj(tx * 6.4, 1.2),      # thenar swell apex
        _proj(tx * 3.0, 3.4),      # blends back into the palm near the index
    ]
    th_knuckle = _proj(tx * 6.0, 1.0)
    th_mid = _proj(tx * 7.6 + tx * spread * 0.6, 3.4)
    th_tip = _proj(tx * 7.4 + tx * spread * 0.8, 5.8)

    def _draw_thumb():
        pygame.draw.polygon(surf, _R16_OUTLINE, thenar)
        pygame.draw.polygon(surf, _R16_GLOVE, thenar)
        pygame.draw.line(surf, _R16_OUTLINE, th_knuckle, th_mid, base_w + 2)
        pygame.draw.line(surf, _R16_OUTLINE, th_mid, th_tip, base_w + 1)
        pygame.draw.circle(surf, _R16_OUTLINE, th_tip, (base_w + 1) // 2)
        pygame.draw.line(surf, _R16_GLOVE, th_knuckle, th_mid, base_w)
        pygame.draw.line(surf, _R16_GLOVE, th_mid, th_tip, base_w - 1)
        pygame.draw.circle(surf, _R16_GLOVE, th_tip, base_w // 2)

    if thumb_behind:
        _draw_thumb()

    # --- TAPERED palm mass: a narrow wrist that widens across the knuckle row,
    # the top edge following the knuckle ARCH (NOT a flat rectangle).
    WW = 3.4                       # half-width at the wrist (narrow end)
    palm_local = [
        (-WW, -3.4),               # inner wrist corner (narrow)
        (-KW * 0.92, 6.6),         # widen out to the pinky-side knuckle base
        (knuckles[3][0], knuckles[3][1] - 0.6),  # pinky knuckle (low)
        (knuckles[2][0], knuckles[2][1]),        # ring knuckle (arch)
        (knuckles[1][0], knuckles[1][1] + 0.2),  # middle knuckle (arch crown)
        (knuckles[0][0], knuckles[0][1]),        # index knuckle (arch)
        (KW * 0.96, 6.2),          # widen out to the index/thumb-side knuckle base
        (WW + 0.6, -3.4),          # outer wrist corner (narrow)
    ]
    palm_pts = [_proj(x, y) for (x, y) in palm_local]
    pygame.draw.polygon(surf, _R16_OUTLINE, palm_pts)
    pygame.draw.polygon(surf, _R16_GLOVE,
                        [_proj(x * 0.9, y) for (x, y) in palm_local])

    if not thumb_behind:
        _draw_thumb()

    # --- Fingers: keyline pass then glove pass, each a curved tapered poly-line.
    arcs = [(_finger_arc(rx, ky, ln, cv), ln) for (rx, ky, ln, cv) in knuckles]
    for col, lw_off in ((_R16_OUTLINE, 2), (_R16_GLOVE, 0)):
        for pts, ln in arcs:
            for i in range(len(pts) - 1):
                t = i / (len(pts) - 1)
                w = _taper_w(t) + lw_off
                pygame.draw.line(surf, col, pts[i], pts[i + 1], w)
            tipw = (_taper_w(1.0) + lw_off) // 2
            pygame.draw.circle(surf, col, pts[-1], max(1, tipw))

    # --- Legible-but-light detail: knuckle dimples along the arch, a hairline
    # groove between each finger, and rim sheen. Sparse so it stays clean at 1x.
    for rx, ky, ln, cv in knuckles:
        pygame.draw.circle(surf, _R16_GROOVE, _proj(rx, ky - 0.4), 1)
    for k in range(1, len(knuckles)):
        midx = (knuckles[k - 1][0] + knuckles[k][0]) / 2
        midy = (knuckles[k - 1][1] + knuckles[k][1]) / 2
        gv_b = _proj(midx, midy - 1.2)
        gv_t = _proj(midx, midy + 2.4)
        pygame.draw.line(surf, _R16_GROOVE, gv_b, gv_t, 1)

    pygame.draw.circle(surf, _R16_GLOVE_HI, _proj(-KW * 0.30, 6.6), 2)
    mid_pts = arcs[1][0]
    pygame.draw.line(surf, _R16_GLOVE_HI,
                     (mid_pts[0][0] - 1, mid_pts[0][1] - 1),
                     (mid_pts[-1][0] - 1, mid_pts[-1][1] - 1),
                     max(1, base_w // 3))


def render_clown_staff_r16(idx, *, total_px, bauble_px, cup_dy, wrist, curl,
                           spread, cup=0.0, thumb_side=1, thumb_behind=False,
                           back_arch=False, die_pulse_off=2.0):
    """Round-16 hero panel — identical to r15 except the open die hand is drawn
    by `_r16_open_hand` (the tamed-fan + deeper back-arch fixes). Locked grip,
    floating die, and continuation anchor are unchanged."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    die_cx = jester_cx - 56
    die_cy = 30
    open_hand = (hand_up[0], hand_up[1])

    _r16_open_hand(layer, open_hand, wrist=wrist, curl=curl, spread=spread,
                   cup=cup, thumb_side=thumb_side, thumb_behind=thumb_behind,
                   back_arch=back_arch)
    draw_cupped_die(layer, die_cx, die_cy, idx * 1.7 + die_pulse_off,
                    show_inset=False)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px)
    rot = -7
    rad = math.radians(rot)
    grip_frac = max(0.30, 1.0 - (ground_y - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = int(r_hand[0] - grip_rx)
    prop_oy = int(r_hand[1] - grip_ry)

    shaft_w = 2
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=True)
    layer.blit(rotated, (prop_ox, prop_oy))
    _r8_grip_occlusion(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w)
    _r11_grip_glove(layer, (int(r_hand[0]), int(r_hand[1])), shaft_w, behind=False)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


def _render_open_hand_crop_r16(kw, *, crop_px=150, zoom=7):
    """Isolated HERO-ZOOM crop of JUST the open die hand for one variant, on a
    flat neutral card (no sky, no die, so no die-glow bloom on the flesh). The
    hand is drawn at a local origin into a small SRCALPHA tile, the painted
    bounding box is found, and that box is nearest-neighbour upscaled so the four
    landmarks (arch, pinky-low, wrist-rooted short thumb, finger taper) read
    large. Returns a `crop_px`-tall card surface with the zoomed hand centred."""
    # A roomy tile so the rotated/spread hand never clips at its native scale.
    tile = pygame.Surface((96, 96), pygame.SRCALPHA)
    origin = (60, 64)
    _r16_open_hand(tile, origin,
                   wrist=kw["wrist"], curl=kw["curl"], spread=kw["spread"],
                   cup=kw.get("cup", 0.0), thumb_side=kw.get("thumb_side", 1),
                   thumb_behind=kw.get("thumb_behind", False),
                   back_arch=kw.get("back_arch", False))

    bbox = tile.get_bounding_rect()
    if bbox.width == 0 or bbox.height == 0:
        bbox = pygame.Rect(0, 0, 96, 96)
    bbox.inflate_ip(6, 6)
    bbox = bbox.clip(tile.get_rect())
    hand_sub = tile.subsurface(bbox).copy()

    # Nearest-neighbour upscale (pixel-honest at the zoom the AD asked to judge).
    zw = int(bbox.width * zoom)
    zh = int(bbox.height * zoom)
    zoomed = pygame.transform.scale(hand_sub, (zw, zh))

    card_w = max(zw + 28, int(crop_px * 0.9))
    card = pygame.Surface((card_w, crop_px), pygame.SRCALPHA)
    # Flat neutral slate card with a thin frame — deliberately NOT the sky.
    card.fill((38, 41, 52, 255))
    pygame.draw.rect(card, (70, 76, 92), card.get_rect(), 2)
    cx = (card_w - zw) // 2
    cy = (crop_px - zh) // 2
    card.blit(zoomed, (cx, cy))
    return card


_CLOWN_R16_VARIANTS = [
    # 1-2 RELAXED 3/4 OPEN HAND — natural slightly-turned hand, gently curved
    #     fingers, thumb on the NEAR/outside edge. Two curl/spread degrees.
    ("Relaxed 3/4 - soft",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R16_FOREARM_DEG,
          curl=0.22, spread=0.9, cup=0.0, thumb_side=1, die_pulse_off=2.0),
     "natural 3/4 hand, gently curved fingers, thumb reading on the near side"),
    ("Relaxed 3/4 - open",
     # spread softened ~18% (1.15 -> 0.95) + the new fan damping so the open
     # hand no longer reads as a spiky star at 1x while still splaying at zoom.
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R16_FOREARM_DEG,
          curl=0.10, spread=0.95, cup=0.0, thumb_side=1, die_pulse_off=2.0),
     "fingers more open, fan softened ~18% so it stops being a star at 1x"),
    # 3-4 OPEN PALM CUPPED UPWARD — palm toward viewer, fingers curl into an
    #     offering cup beneath the die, thumb out to the side. Two cup depths.
    ("Cupped up - shallow",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R16_FOREARM_DEG - 6,
          curl=0.40, spread=0.8, cup=0.6, thumb_side=1, die_pulse_off=2.0),
     "palm up, fingers curl into a shallow offering cup beneath the die"),
    ("Cupped up - deep",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R16_FOREARM_DEG - 10,
          curl=0.62, spread=0.7, cup=1.0, thumb_side=1, die_pulse_off=2.0),
     "deeper cup, fingertips arc up to cradle the die, thumb out to the side"),
    # 5 BACK OF HAND — knuckles to viewer; `back_arch` deepens the top-edge
    #   curve so the knuckle line reads as an ARCH, never a flat paddle.
    ("Back of hand",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R16_FOREARM_DEG,
          curl=0.18, spread=0.95, cup=0.0, thumb_side=-1, thumb_behind=True,
          back_arch=True, die_pulse_off=2.0),
     "knuckles to viewer; top edge given more arch so it visibly curves"),
]


_CLOWN_R16_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 16: round-15 from-scratch die hand made LEGIBLE — a big HERO-ZOOM crop of just the open hand per panel (no sky, no die glow) so the arch / pinky-low / wrist-rooted short thumb / finger taper can be judged",
     (255, 255, 255)),
    ("Each panel: LARGE isolated hand crop (~7x, neutral card) above the full figure + the true-1x day/night strip below. Fixes this round: V2 fan softened ~18% (no spiky star at 1x); V5 back-of-hand knuckle top edge given more arch. "
     "Locked: heel-on-wrist + ~47deg continuation, the staff grip, and the floating die (glow stays on the die only — the crop omits the die so flesh never blooms).",
     (205, 210, 220)),
]


def _render_clown_r16_crops():
    """Emit each of the 5 open-hand HERO crops as its OWN full-res PNG so the four
    landmarks (arch / pinky-low / wrist-rooted short thumb / finger taper) can be
    read at native pixels, instead of collapsing inside the wide contact sheet.
    Higher zoom than the in-sheet card; never touches the round_16.png composite."""
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    for idx, (name, kw, note) in enumerate(_CLOWN_R16_VARIANTS, start=1):
        card = _render_open_hand_crop_r16(kw, crop_px=300, zoom=14)
        out_path = os.path.join(out_dir, f"round_16_crop_v{idx}.png")
        pygame.image.save(card, out_path)
        print("wrote", out_path, f"({card.get_width()}x{card.get_height()})", "-", name)


def _render_clown_r16_sheet():
    """Round-16 clown look-dev: the same 5 orientations as r15 but each panel now
    leads with a LARGE isolated hero-zoom crop of just the open hand (neutral
    card, ~7x, no die glow on the flesh) so the four landmarks are legible, with
    the full-figure panel + the true-1x day/night shrink strip kept beneath.
    Writes docs/warren_clown/round_16.png — never overwrites an existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)
    crop_h = 150

    cols = len(_CLOWN_R16_VARIANTS)
    pad = 20
    head = 96
    name_strip = 38
    crop_gap = 10
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + crop_h + crop_gap + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R16_HEADERS[0][0], True, _CLOWN_R16_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R16_HEADERS[1][0], True, _CLOWN_R16_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)
    crop_tag_f = hud._font(12, True)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R16_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        # HERO-ZOOM hand crop — the headline of round 16 — centred above the figure.
        crop = _render_open_hand_crop_r16(kw, crop_px=crop_h, zoom=7)
        cx = px + (cell_w - crop.get_width()) // 2
        sheet.blit(crop, (cx, py + name_strip))
        sheet.blit(crop_tag_f.render("hero-zoom: arch / pinky-low / short wrist thumb / taper",
                                     True, (255, 235, 120)),
                   (px + 6, py + name_strip + crop_h - 16))

        clown = render_clown_staff_r16(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip + crop_h + crop_gap))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_16.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


_R17_GLOVE    = _R16_GLOVE
_R17_GROOVE   = _R16_GROOVE
_R17_GLOVE_HI = _R16_GLOVE_HI
_R17_OUTLINE  = _R16_OUTLINE
_R17_FOREARM_DEG = _R16_FOREARM_DEG


def _r17_die_hand(surf, hand, *, wrist, gesture="mitt", knuckles_up=False,
                  point_len=0.0, point_bow=0.0, base_w=4):
    """Round-17 die-side hand: a DIRECTION CHANGE away from the open palm. At
    ~16px on screen there are too few pixels to carry knuckle-arch + four tapered
    fingers, so r11-r16 open hands read as malformed. r17 instead draws a SIMPLE
    closed-glove gesture whose read comes from one strong silhouette plus 1-2 dark
    grooves — never from fine finger anatomy.

    Same local frame + heel-on-wrist `_proj` ~47deg continuation as the r16 hand,
    so it still flows out of the raised forearm as one limb. `gesture` selects:
      - "mitt": a clean rounded 4-finger glove fist at the wrist (one blob,
        knuckle band hinted). `knuckles_up` rotates the band toward the die.
      - "point": the same fist with ONE clean tapered digit extended toward the
        floating die; `point_len`/`point_bow` set its reach and curve.
      - "reach": the fingers curl UP toward the die as a single cupped unit (a
        soft-grab silhouette, not individual splayed fingers).
    """
    hx, hy = hand
    ang = math.radians(-wrist)
    ca, sa = math.cos(ang), math.sin(ang)

    def _proj(dx, dy):
        # Heel laid a hair up the hand so the forearm tip lands INSIDE the mitt
        # mass — the locked r13-r16 continuation anchor (no stub/gap).
        return (hx - int(round(dx * ca - dy * sa)),
                hy + int(round(-dx * sa - dy * ca)) - int(round(2 * ca)))

    # --- The fist body: one rounded blob spanning wrist -> knuckle crown. A
    # closed mitt is read as a soft oval, so a polygon ring of points around the
    # local frame keeps the silhouette clean at any size (no spiky edges at 1x).
    # `crown` is the knuckle-row apex; `knuckles_up` lifts/rounds it toward the
    # die so the dark knuckle band sits at the top of the read.
    crown = 9.6 + (1.2 if knuckles_up else 0.0)
    HALF = 6.2                          # half-width of the fist across the band
    body_local = [
        (-3.6, -3.6),                   # inner wrist corner (narrow heel)
        (-HALF, 3.0),                   # widen out toward the knuckle band
        (-HALF * 0.86, crown - 1.0),
        (-HALF * 0.30, crown),          # knuckle crown, viewer-left lobe
        ( HALF * 0.30, crown),          # knuckle crown, viewer-right lobe
        ( HALF * 0.86, crown - 1.0),
        ( HALF + 0.4, 3.0),
        ( 4.0, -3.6),                   # outer wrist corner (narrow heel)
    ]
    body_pts = [_proj(x, y) for (x, y) in body_local]

    # --- A short, low thumb wedge folded against the index side of the fist:
    # present enough to break the pure-oval read, never an extended digit.
    thenar = [
        _proj(4.6, -1.4),               # wrist root, outside
        _proj(7.0, 1.6),                # thumb knuckle swell
        _proj(5.2, 4.4),                # tucks back into the fist
        _proj(3.2, 2.0),
    ]

    def _draw_blob():
        pygame.draw.polygon(surf, _R17_OUTLINE, thenar)
        pygame.draw.polygon(surf, _R17_GLOVE, [_proj(x * 0.9, y) for (x, y) in
                                               ((4.6, -1.4), (7.0, 1.6),
                                                (5.2, 4.4), (3.2, 2.0))])
        pygame.draw.polygon(surf, _R17_OUTLINE, body_pts)
        pygame.draw.polygon(surf, _R17_GLOVE,
                            [_proj(x * 0.9, y) for (x, y) in body_local])

    # --- ONE clean tapered digit. For "point" it extends straight toward the
    # die; for "reach" it curls back over the fist as a soft cupped grab. Either
    # way it is a SINGLE shape, never four fingers.
    def _digit(reach_back):
        # Root just above the knuckle crown, on the die-facing edge of the fist.
        root_x, root_y = -HALF * 0.30, crown - 0.6
        segs = (0.0, 0.42, 0.76, 1.0)
        pts = []
        for t in segs:
            up = root_y + point_len * t
            bow = point_bow * (t * t)
            if reach_back:
                # A soft grab: the unit arcs back over the fist instead of out,
                # so the silhouette cups upward toward the die as one mass.
                up = root_y + point_len * (t - 1.2 * t * t)
                bow = -point_bow * (t * t) - HALF * 0.30 * t
            pts.append((root_x + bow, up))
        return [_proj(x, y) for (x, y) in pts]

    def _taper_w(t):
        # The digit tapers tip-ward but never below what the keyline reads at 1x.
        return max(2, int(round(base_w - 1.2 * t)))

    def _draw_digit(reach_back=False):
        pts = _digit(reach_back)
        for col, lw_off in ((_R17_OUTLINE, 2), (_R17_GLOVE, 0)):
            for i in range(len(pts) - 1):
                t = i / (len(pts) - 1)
                pygame.draw.line(surf, col, pts[i], pts[i + 1], _taper_w(t) + lw_off)
            pygame.draw.circle(surf, col, pts[-1],
                               max(1, (_taper_w(1.0) + lw_off) // 2))

    # The extended digit roots ABOVE the fist, so paint it under the body for
    # "reach" (grab curls in front of the fist) and over the body for "point".
    if gesture == "reach":
        _draw_digit(reach_back=True)
        _draw_blob()
    elif gesture == "point":
        _draw_blob()
        _draw_digit(reach_back=False)
    else:
        _draw_blob()

    # --- Legible-but-light detail: ONE curved dark knuckle groove across the
    # band and a hairline crease at the wrist, plus a single rim-sheen lobe. This
    # is the whole "anatomy" budget — sparse so it never fizzes at true 1x.
    band_y = crown - 2.4
    groove = [_proj(x, band_y + (0.8 if knuckles_up else 0.0))
              for x in (-HALF * 0.7, -HALF * 0.2, HALF * 0.3, HALF * 0.72)]
    if len(groove) >= 2:
        pygame.draw.lines(surf, _R17_GROOVE, False, groove, 1)
    pygame.draw.line(surf, _R17_GROOVE, _proj(-HALF * 0.6, 0.2),
                     _proj(HALF * 0.6, 0.2), 1)
    pygame.draw.circle(surf, _R17_GLOVE_HI, _proj(-HALF * 0.25, crown - 3.4), 2)


def render_clown_staff_r17(idx, *, total_px, bauble_px, cup_dy, wrist,
                           gesture="mitt", knuckles_up=False, point_len=0.0,
                           point_bow=0.0, die_dx=0, die_dy=0,
                           ext_left=0, ext_top=0, ext_right=0, staff_fn=prop_14n,
                           die_pulse_off=2.0):
    """Round-17 hero panel — identical to r16 except the die-side hand is drawn by
    `_r17_die_hand` (a simple closed-glove gesture, not an open palm). Locked grip,
    floating die, and heel-on-wrist ~47deg continuation are unchanged.

    `ext_left`/`ext_top`/`ext_right` grow the CANVAS (in VIEW px) without resizing
    the clown or die — the figure simply shifts right/down by the margins — so the
    floating die has room to sit further up-left (where the pointing finger aims)
    without running off the frame. All zero reproduces the original panel exactly."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = 3                                 # higher supersample so the staff texture
                                           # + bauble face stay crisp when a sheet
                                           # scales the figure up (was CLOWN_SS=2)
    palette = shaped_palette(DAY_PHASE)
    cw, ch = VIEW_W + ext_left + ext_right, VIEW_H + ext_top
    bw, bh = cw * ss, ch * ss
    big = pygame.Surface((bw, bh))

    ground_y = VIEW_FEET_Y + 4 + ext_top
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((cw, ch), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10 + ext_left
    feet_y = VIEW_FEET_Y + ext_top

    hand_up = (jester_cx - 60, feet_y - 154 - cup_dy)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    die_cx = jester_cx - 56 + die_dx
    die_cy = 30 + ext_top + die_dy
    die_hand = (hand_up[0], hand_up[1])

    _r17_die_hand(layer, die_hand, wrist=wrist, gesture=gesture,
                  knuckles_up=knuckles_up, point_len=point_len,
                  point_bow=point_bow)
    draw_cupped_die(layer, die_cx, die_cy, idx * 1.7 + die_pulse_off,
                    show_inset=False)

    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    r_hand = (hip_cx + 34, hip_y - 4)

    prop, p_w, p_h = _held_marotte_surface(total_px, bauble_px, draw_fn=staff_fn)
    rot = -7
    rad = math.radians(rot)
    # Plant the marotte FOOT a few px INTO the ground line for every staff length,
    # so the lower shaft unmistakably touches the ground rather than hovering at
    # ankle height. The hand keeps gripping the shaft (grip rides higher up for
    # shorter staffs); the lower clamp just guards the bauble for extreme lengths.
    foot_target = ground_y + 7
    grip_frac = max(0.16, 1.0 - (foot_target - r_hand[1]) / (p_h * math.cos(rad)))
    rotated = pygame.transform.rotate(prop, rot)
    cxr, cyr = p_w / 2, p_h / 2

    def _mapped(lx, ly):
        ldx, ldy = lx - cxr, ly - cyr
        rx = cxr + (ldx * math.cos(rad) + ldy * math.sin(rad)) + (rotated.get_width() - p_w) / 2
        ry = cyr + (-ldx * math.sin(rad) + ldy * math.cos(rad)) + (rotated.get_height() - p_h) / 2
        return rx, ry

    grip_rx, grip_ry = _mapped(p_w / 2, p_h * grip_frac)
    prop_ox = r_hand[0] - grip_rx
    prop_oy = r_hand[1] - grip_ry
    rhi = (int(r_hand[0]), int(r_hand[1]))

    shaft_w = 2
    # The thin staff carries the fine shaft texture + the mini-clown bauble face,
    # so render it (and the front grip) at the FULL supersample resolution and
    # composite onto `big` rather than the 1x layer — on the 1x layer the staff is
    # only ~8px wide, and upscaling that in a sheet softens the texture + face to
    # mush. The body/open-hand stay on the 1x layer (flat fills upscale cleanly).
    _r11_grip_glove(layer, rhi, shaft_w, behind=True)
    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))

    prop_hi, _pw_hi, _ph_hi = _held_marotte_surface(total_px * ss, bauble_px * ss,
                                                    draw_fn=staff_fn)
    rotated_hi = pygame.transform.rotate(prop_hi, rot)
    big.blit(rotated_hi, (int(round(prop_ox * ss)), int(round(prop_oy * ss))))

    top = pygame.Surface((cw, ch), pygame.SRCALPHA)
    _r8_grip_occlusion(top, rhi, shaft_w)
    _r11_grip_glove(top, rhi, shaft_w, behind=False)
    big.blit(pygame.transform.smoothscale(top, (bw, bh)), (0, 0))
    return big


def _render_die_hand_crop_r17(kw, *, crop_px=150, zoom=7):
    """Isolated HERO-ZOOM crop of JUST the r17 die-side gesture on a flat neutral
    card (no sky, no die, so no die-glow bloom on the glove). Mirrors the r16 crop
    so the simple silhouette + grooves can be judged at native pixels."""
    tile = pygame.Surface((96, 96), pygame.SRCALPHA)
    origin = (52, 70)
    _r17_die_hand(tile, origin, wrist=kw["wrist"], gesture=kw.get("gesture", "mitt"),
                  knuckles_up=kw.get("knuckles_up", False),
                  point_len=kw.get("point_len", 0.0),
                  point_bow=kw.get("point_bow", 0.0))

    bbox = tile.get_bounding_rect()
    if bbox.width == 0 or bbox.height == 0:
        bbox = pygame.Rect(0, 0, 96, 96)
    bbox.inflate_ip(6, 6)
    bbox = bbox.clip(tile.get_rect())
    hand_sub = tile.subsurface(bbox).copy()

    zw = int(bbox.width * zoom)
    zh = int(bbox.height * zoom)
    zoomed = pygame.transform.scale(hand_sub, (zw, zh))

    card_w = max(zw + 28, int(crop_px * 0.9))
    card = pygame.Surface((card_w, crop_px), pygame.SRCALPHA)
    card.fill((38, 41, 52, 255))
    pygame.draw.rect(card, (70, 76, 92), card.get_rect(), 2)
    cx = (card_w - zw) // 2
    cy = (crop_px - zh) // 2
    card.blit(zoomed, (cx, cy))
    return card


_CLOWN_R17_VARIANTS = [
    # 1 RELAXED CLOSED MITT — the safest read: a clean rounded glove fist at the
    #   wrist, knuckle band hinted by one curved groove, no extended digit.
    ("Relaxed mitt",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R17_FOREARM_DEG,
          gesture="mitt", knuckles_up=False, die_pulse_off=2.0),
     "clean rounded 4-finger glove fist at the wrist, knuckle band hinted"),
    # 2 MITT, KNUCKLES-UP — same fist rotated so the dark knuckle row faces the
    #   die for a subtle 'ready' read.
    ("Mitt - knuckles up",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R17_FOREARM_DEG,
          gesture="mitt", knuckles_up=True, die_pulse_off=2.0),
     "same fist, knuckle row turned toward the die for a subtle 'ready' read"),
    # 3 POINTING UP AT THE DIE — index extended toward the floating die, rest of
    #   the hand a closed mitt; directs the eye to the power-up.
    ("Pointing at die",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R17_FOREARM_DEG,
          gesture="point", point_len=11.0, point_bow=-0.6, die_pulse_off=2.0),
     "one clean tapered digit points up at the die, rest a closed mitt"),
    # 4 POINTING, EXTENDED REACH — same point with more reach/energy toward the die.
    ("Pointing - extended",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R17_FOREARM_DEG,
          gesture="point", point_len=15.0, point_bow=-1.0, die_pulse_off=2.0),
     "same point reaching further up toward the die for more energy"),
    # 5 REACHING / SOFT GRAB — fingers curl UP toward the die as one cupped unit.
    ("Reaching soft-grab",
     dict(total_px=200, bauble_px=15, cup_dy=2, wrist=_R17_FOREARM_DEG,
          gesture="reach", point_len=12.0, point_bow=2.2, die_pulse_off=2.0),
     "fingers curl up toward the die as one soft cupped grab, not splayed"),
]


_CLOWN_R17_HEADERS = [
    ("Warren Clown HERO look-dev — ROUND 17: DIRECTION CHANGE on the die-side hand. The open palm is abandoned (too few pixels at ~16px for real finger anatomy) — replaced by a SIMPLE closed-glove gesture that reads from one strong silhouette + 1-2 dark grooves",
     (255, 255, 255)),
    ("Two families across 5 versions: CLOSED MITT (1-2) and POINTING / REACHING toward the die (3-5). Each panel: LARGE isolated gesture crop (~7x, neutral card) above the full figure + the true-1x day/night strip below. "
     "Locked: heel-on-wrist + ~47deg continuation, the staff grip, and the floating die (glow stays on the die only).",
     (205, 210, 220)),
]


def _render_clown_r17_crops():
    """Emit each of the 5 r17 gestures as its OWN full-res PNG so the simple
    silhouette + grooves can be read at native pixels instead of collapsing inside
    the wide contact sheet. Mirrors `_render_clown_r16_crops`; never touches
    round_16* or earlier outputs."""
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    for idx, (name, kw, note) in enumerate(_CLOWN_R17_VARIANTS, start=1):
        card = _render_die_hand_crop_r17(kw, crop_px=300, zoom=14)
        out_path = os.path.join(out_dir, f"round_17_crop_v{idx}.png")
        pygame.image.save(card, out_path)
        print("wrote", out_path, f"({card.get_width()}x{card.get_height()})", "-", name)


def _render_clown_r17_compare():
    """Round-17 SIDE-BY-SIDE: one 6-cell grid of WHOLE clown figures (staff + die)
    so the poses can be compared in context, not as zoomed hands — cell 1 is the
    current open-hand pose, cells 2-6 are the 5 simple gestures. Writes
    docs/warren_clown/round_17_compare.png; never overwrites an existing sheet."""
    SCALE = 3.0
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)
    cols, rows = 3, 2
    pad = 24
    head = 64
    label_h = 34
    gap = 18
    cell_w = disp_w
    cell_h = label_h + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + rows * cell_h + (rows - 1) * gap + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(26, True)
    label_f = hud._font(19, True)
    sheet.blit(title_f.render(
        "Warren Clown — die-side pose comparison: cell 1 = CURRENT (open hand), "
        "cells 2-6 = the 5 simple gestures, each on the WHOLE figure", True,
        (255, 255, 255)), (pad, 18))

    # Cell 1 is the current open-hand pose (round-16, relaxed 3/4) as the baseline;
    # the rest are the round-17 simple gestures in declaration order.
    cur_name, cur_kw, _ = _CLOWN_R16_VARIANTS[0]
    figs = [("1. CURRENT — open hand",
             render_clown_staff_r16(0, **cur_kw))]
    for i, (name, kw, _note) in enumerate(_CLOWN_R17_VARIANTS):
        figs.append((f"{i + 2}. {name}", render_clown_staff_r17(i, **kw)))

    for i, (label, fig) in enumerate(figs):
        r, c = divmod(i, cols)
        cx = pad + c * (cell_w + gap)
        cy = head + r * (cell_h + gap)
        # Label band over each cell so it's obvious which pose is which.
        pygame.draw.rect(sheet, (40, 43, 54), (cx, cy, cell_w, label_h))
        sheet.blit(label_f.render(label, True, (235, 238, 246)), (cx + 8, cy + 7))
        scaled = pygame.transform.smoothscale(fig, (disp_w, disp_h))
        sheet.blit(scaled, (cx, cy + label_h))
        pygame.draw.rect(sheet, (70, 76, 92),
                         (cx, cy, cell_w, cell_h), 2)

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_17_compare.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# The canvas is grown up-and-left so the die can sit where the pointing finger
# actually aims (a steep up-left line that ran off the old frame). The clown/die
# keep their size — only the image gets bigger and the figure shifts right/down.
_R17_EXT_LEFT = 120
_R17_EXT_TOP = 55
_R17_EXT_RIGHT = 12


def _render_clown_r17_die():
    """Round-17 DIE-POSITION sweep: the SAME pointing pose (gesture v4) on the whole
    figure across 5 cells, on an ENLARGED canvas; the ONLY thing that changes is
    where the floating die sits — walked up-left along the extended finger's line —
    so the player can pick the placement the clown actually points at. Writes
    docs/warren_clown/round_17_die.png."""
    extL, extT, extR = _R17_EXT_LEFT, _R17_EXT_TOP, _R17_EXT_RIGHT
    cw = VIEW_W + extL + extR
    ch = VIEW_H + extT
    SCALE = 2.2
    disp_w = int(cw * SCALE)
    disp_h = int(ch * SCALE)
    cols, rows = 3, 2
    pad = 24
    head = 64
    label_h = 34
    gap = 18
    cell_w = disp_w
    cell_h = label_h + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + rows * cell_h + (rows - 1) * gap + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(26, True)
    label_f = hud._font(18, True)
    sheet.blit(title_f.render(
        "Warren Clown — bigger canvas, SAME pointing pose + SAME clown/die size. "
        "Only the DIE POSITION moves (up the finger line). Pick the best.", True,
        (255, 255, 255)), (pad, 18))

    base_kw = dict(_CLOWN_R17_VARIANTS[3][1])      # the "Pointing - extended" pose
    jester_cx = VIEW_W // 2 - 10 + extL
    # Approx fingertip for this pose + the up-left direction it points along.
    tip_x = jester_cx - 60 - 15.6
    tip_y = (VIEW_FEET_Y + extT) - 156 - 19.8
    dir_x, dir_y = -0.687, -0.727
    s_values = (40, 60, 80, 100, 114)              # distance up the finger line

    for i, s in enumerate(s_values):
        tx = tip_x + dir_x * s
        ty = tip_y + dir_y * s
        die_dx = int(round(tx - (jester_cx - 56)))
        die_dy = int(round(ty - (30 + extT)))
        kw = dict(base_kw)
        kw.update(die_dx=die_dx, die_dy=die_dy,
                  ext_left=extL, ext_top=extT, ext_right=extR)
        fig = render_clown_staff_r17(i, **kw)
        label = f"{i + 1}. die at ({int(round(tx))},{int(round(ty))})"
        r, c = divmod(i, cols)
        cx = pad + c * (cell_w + gap)
        cy = head + r * (cell_h + gap)
        pygame.draw.rect(sheet, (40, 43, 54), (cx, cy, cell_w, label_h))
        sheet.blit(label_f.render(label, True, (235, 238, 246)), (cx + 8, cy + 8))
        sheet.blit(pygame.transform.smoothscale(fig, (disp_w, disp_h)),
                   (cx, cy + label_h))
        pygame.draw.rect(sheet, (70, 76, 92), (cx, cy, cell_w, cell_h), 2)

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_17_die.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


def _r17_die4_offsets():
    """The locked die placement (#4 from the die sweep) — s=100 up the pointing
    line on the enlarged canvas — as (die_dx, die_dy) for `render_clown_staff_r17`."""
    extL, extT = _R17_EXT_LEFT, _R17_EXT_TOP
    jester_cx = VIEW_W // 2 - 10 + extL
    tip_x = jester_cx - 60 - 15.6
    tip_y = (VIEW_FEET_Y + extT) - 156 - 19.8
    s = 100
    tx = tip_x - 0.687 * s
    ty = tip_y - 0.727 * s
    return int(round(tx - (jester_cx - 56))), int(round(ty - (30 + extT)))


_R17_STAFF_LENGTHS = [
    ("Short", 150),
    ("Medium", 175),
    ("Tall (current)", 200),
    ("Taller", 225),
    ("X-Tall", 250),
]


def _render_clown_r17_staff():
    """Round-17 STAFF-LENGTH chooser, rebuilt on the LOCKED design (pointing pose v4
    + die position #4 + enlarged canvas): 5 cells, same clown/pose/die, only the
    marotte staff length (`total_px`) changes. Writes
    docs/warren_clown/round_17_staff.png."""
    extL, extT, extR = _R17_EXT_LEFT, _R17_EXT_TOP, _R17_EXT_RIGHT
    cw = VIEW_W + extL + extR
    ch = VIEW_H + extT
    SCALE = 2.2
    disp_w = int(cw * SCALE)
    disp_h = int(ch * SCALE)
    cols, rows = 3, 2
    pad = 24
    head = 64
    label_h = 34
    gap = 18
    cell_w = disp_w
    cell_h = label_h + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + rows * cell_h + (rows - 1) * gap + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(26, True)
    label_f = hud._font(18, True)
    sheet.blit(title_f.render(
        "Warren Clown — STAFF LENGTH chooser on the locked design (pointing pose "
        "+ die #4). Only the staff length changes. Pick the best.", True,
        (255, 255, 255)), (pad, 18))

    base_kw = dict(_CLOWN_R17_VARIANTS[3][1])      # the locked "Pointing" pose
    die_dx, die_dy = _r17_die4_offsets()
    for i, (name, total_px) in enumerate(_R17_STAFF_LENGTHS):
        kw = dict(base_kw)
        kw.update(total_px=total_px, die_dx=die_dx, die_dy=die_dy,
                  ext_left=extL, ext_top=extT, ext_right=extR)
        fig = render_clown_staff_r17(i, **kw)
        label = f"{i + 1}. {name}  (total_px={total_px})"
        r, c = divmod(i, cols)
        cx = pad + c * (cell_w + gap)
        cy = head + r * (cell_h + gap)
        pygame.draw.rect(sheet, (40, 43, 54), (cx, cy, cell_w, label_h))
        sheet.blit(label_f.render(label, True, (235, 238, 246)), (cx + 8, cy + 8))
        sheet.blit(pygame.transform.smoothscale(fig, (disp_w, disp_h)),
                   (cx, cy + label_h))
        pygame.draw.rect(sheet, (70, 76, 92), (cx, cy, cell_w, cell_h), 2)

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_17_staff.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


_R17_STAFF_DESIGNS = [
    ("8 · Carousel Barker", prop_14l),
    ("9 · Jingles & Filigree", prop_14m),
    ("10 · Golden Jester", prop_14n),
]


def _render_clown_r17_staffgrid():
    """Round-17 STAFF DESIGN x LENGTH grid on the locked hero (pointing pose v4 +
    die #4 + grounded foot): ONE ROW per bell-foot staff design (8/9/10), columns
    across the staff lengths, so each design can be compared at every length.
    Writes docs/warren_clown/round_17_staff_grid.png."""
    extL, extT, extR = _R17_EXT_LEFT, _R17_EXT_TOP, _R17_EXT_RIGHT
    cw = VIEW_W + extL + extR
    ch = VIEW_H + extT
    SCALE = 1.5
    disp_w = int(cw * SCALE)
    disp_h = int(ch * SCALE)
    cols = len(_R17_STAFF_LENGTHS)
    rows = len(_R17_STAFF_DESIGNS)
    pad = 24
    head = 64
    label_h = 30
    gap = 14
    cell_w = disp_w
    cell_h = label_h + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + rows * cell_h + (rows - 1) * gap + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(26, True)
    label_f = hud._font(17, True)
    sheet.blit(title_f.render(
        "Warren Clown — staff DESIGN (rows: 8, 9, 10) x LENGTH (columns), locked "
        "pointing pose + die #4 + grounded foot", True, (255, 255, 255)), (pad, 18))

    base_kw = dict(_CLOWN_R17_VARIANTS[3][1])      # the locked "Pointing" pose
    die_dx, die_dy = _r17_die4_offsets()
    for r, (dname, staff_fn) in enumerate(_R17_STAFF_DESIGNS):
        for c, (lname, total_px) in enumerate(_R17_STAFF_LENGTHS):
            kw = dict(base_kw)
            kw.update(total_px=total_px, die_dx=die_dx, die_dy=die_dy,
                      ext_left=extL, ext_top=extT, ext_right=extR, staff_fn=staff_fn)
            fig = render_clown_staff_r17(r * cols + c, **kw)
            cx = pad + c * (cell_w + gap)
            cy = head + r * (cell_h + gap)
            pygame.draw.rect(sheet, (40, 43, 54), (cx, cy, cell_w, label_h))
            sheet.blit(label_f.render(f"{dname}  —  {lname} ({total_px})", True,
                                      (235, 238, 246)), (cx + 8, cy + 7))
            sheet.blit(pygame.transform.smoothscale(fig, (disp_w, disp_h)),
                       (cx, cy + label_h))
            pygame.draw.rect(sheet, (70, 76, 92), (cx, cy, cell_w, cell_h), 2)

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_17_staff_grid.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


def _render_staff_route():
    """The game ROUTE panorama filled with the STAFFS instead of swords — 3 rows,
    one per bell-foot staff design (8/9/10), each the route tiled with that marotte
    as the obstacle pairs. Writes docs/warren_sword/staff_route.png."""
    SS = 6                             # route supersample (matches the saber sheets)
    ROW_SCALE = 1.4
    N_STEPS = 11
    ROUTE_W = SP * N_STEPS + 40
    ROUTE_H = PLAY_H
    DISP_W = int(ROUTE_W * ROW_SCALE)
    DISP_H = int(ROUTE_H * ROW_SCALE)

    pad = 18
    head = 70
    row_gap = 14
    name_strip = 30
    row_h = name_strip + DISP_H
    sheet_w = pad * 2 + DISP_W
    sheet_h = head + len(_R17_STAFF_DESIGNS) * (row_h + row_gap) + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(26, True)
    name_f = hud._font(19, True)
    sheet.blit(title_f.render(
        "Warren ROUTE filled with the STAFFS (not swords) — one row per staff "
        "design (8, 9, 10)", True, (255, 255, 255)), (pad, 20))

    for idx, (name, draw_fn) in enumerate(_R17_STAFF_DESIGNS):
        ry = head + idx * (row_h + row_gap)
        strip = pygame.Surface((DISP_W, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(name, True, (255, 255, 255)), (8, 5))
        sheet.blit(strip, (pad, ry))

        route = _route_panel(draw_fn, ROUTE_W, ROUTE_H, SS)
        route = pygame.transform.smoothscale(route, (DISP_W, DISP_H))
        sheet.blit(route, (pad, ry + name_strip))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_sword")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "staff_route.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


# The LOCKED hero: pointing pose (v4) + die position #4 + grounded foot + the
# Carousel-Barker bell-foot staff (design 8) at the "Taller" length (225).
_R17_FINAL_KW = dict(_CLOWN_R17_VARIANTS[3][1])
_R17_FINAL_KW.update(total_px=225, ext_left=_R17_EXT_LEFT, ext_top=_R17_EXT_TOP,
                     ext_right=_R17_EXT_RIGHT, staff_fn=prop_14l)


def _render_clown_r17_final():
    """The settled hero clown: pointing pose, die #4, grounded foot, Carousel-Barker
    staff (design 8) at Taller (225). Writes docs/warren_clown/round_17_final.png."""
    kw = dict(_R17_FINAL_KW)
    dx, dy = _r17_die4_offsets()
    kw.update(die_dx=dx, die_dy=dy)
    fig = render_clown_staff_r17(0, **kw)
    cw = VIEW_W + _R17_EXT_LEFT + _R17_EXT_RIGHT
    ch = VIEW_H + _R17_EXT_TOP
    SCALE = 2.0
    out = pygame.transform.smoothscale(fig, (int(cw * SCALE), int(ch * SCALE)))
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_17_final.png")
    pygame.image.save(out, out_path)
    print("wrote", out_path, f"({out.get_width()}x{out.get_height()})")


def _render_clown_r17_sheet():
    """Round-17 clown look-dev: 5 SIMPLE die-side gestures (closed mitt + pointing
    /reaching families). Same panel layout as r16 — a name strip, a LARGE isolated
    hero-zoom gesture crop, the full-figure panel, and the true-1x day/night shrink
    strip. Writes docs/warren_clown/round_17.png — never overwrites an existing sheet."""
    SCALE = 2.4
    disp_w = int(VIEW_W * SCALE)
    disp_h = int(VIEW_H * SCALE)
    crop_h = 150

    cols = len(_CLOWN_R17_VARIANTS)
    pad = 20
    head = 96
    name_strip = 38
    crop_gap = 10
    gap = 14
    shrink_h = 40 + VIEW_H

    cell_w = disp_w
    cell_h = name_strip + crop_h + crop_gap + disp_h
    sheet_w = pad * 2 + cols * cell_w + (cols - 1) * gap
    sheet_h = head + cell_h + gap + shrink_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(_CLOWN_R17_HEADERS[0][0], True, _CLOWN_R17_HEADERS[0][1]), (pad, 14))
    sheet.blit(sub_f.render(_CLOWN_R17_HEADERS[1][0], True, _CLOWN_R17_HEADERS[1][1]), (pad, 50))

    name_f = hud._font(18, True)
    note_f = hud._font(12, False)
    crop_tag_f = hud._font(12, True)

    panels = []
    for idx, (name, kw, note) in enumerate(_CLOWN_R17_VARIANTS):
        px = pad + idx * (cell_w + gap)
        py = head

        strip = pygame.Surface((cell_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        strip.blit(note_f.render(note, True, (188, 194, 206)), (10, 22))
        sheet.blit(strip, (px, py))

        crop = _render_die_hand_crop_r17(kw, crop_px=crop_h, zoom=7)
        cx = px + (cell_w - crop.get_width()) // 2
        sheet.blit(crop, (cx, py + name_strip))
        sheet.blit(crop_tag_f.render("hero-zoom: simple silhouette + grooves (no open-palm anatomy)",
                                     True, (255, 235, 120)),
                   (px + 6, py + name_strip + crop_h - 16))

        clown = render_clown_staff_r17(idx, **kw)
        panels.append(clown)
        big = pygame.transform.smoothscale(clown, (disp_w, disp_h))
        pygame.draw.rect(big, (10, 12, 18), big.get_rect(), 2)
        sheet.blit(big, (px, py + name_strip + crop_h + crop_gap))

    sy = head + cell_h + gap
    sheet.blit(name_f.render("Shrink test — true 1x (left half: day sky / right half: night sky)",
                             True, (255, 235, 120)), (pad, sy))
    sy += 34
    day_pal = shaped_palette(DAY_PHASE)
    night_pal = shaped_palette(0.5)
    for idx, clown in enumerate(panels):
        px = pad + idx * (cell_w + gap)
        day_bg = pygame.Surface((VIEW_W, VIEW_H))
        day_bg.fill(day_pal['sky_mid'])
        night_bg = pygame.Surface((VIEW_W, VIEW_H))
        night_bg.fill(night_pal['sky_mid'])
        day_bg.blit(clown, (0, 0))
        night_bg.blit(clown, (0, 0))
        sheet.blit(day_bg, (px, sy))
        sheet.blit(night_bg, (px + VIEW_W + 6, sy))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_17.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


def main():
    # Default: emit the round-8 SABER-ONLY and MAROTTE-ONLY browse sheets alongside
    # the untouched round-7 sheet. `--sabers` / `--marottes` / `--round7` each render
    # only that one sheet (faster when iterating on a single sheet).
    args = sys.argv[1:]
    only = any(a in args for a in ("--sabers", "--marottes", "--round7", "--craft", "--round10", "--clown-r2", "--clown-r3", "--clown-r4", "--clown-final", "--clown-r6", "--clown-r7", "--clown-r8", "--clown-r9", "--clown-r10", "--clown-r11", "--clown-r12", "--clown-r13", "--clown-r14", "--clown-r15", "--clown-r16", "--clown-r16-crops", "--clown-r17", "--clown-r17-crops", "--clown-r17-compare", "--clown-r17-die", "--clown-r17-staff", "--clown-r17-staffgrid", "--marottes-8910", "--staff-route", "--clown-r17-final"))
    do_round7 = "--round7" in args or not only
    do_sabers = "--sabers" in args or not only
    do_marottes = "--marottes" in args or not only
    do_craft = "--craft" in args            # round-9 craft sheet is opt-in only
    do_round10 = "--round10" in args        # round-10 craft + bell-foot sheet, opt-in
    do_clown_r2 = "--clown-r2" in args      # round-2 clown hero look-dev, opt-in
    do_clown_r3 = "--clown-r3" in args      # round-3 clown hero look-dev, opt-in
    do_clown_r4 = "--clown-r4" in args      # round-4 clown hero look-dev (FINAL), opt-in
    do_clown_final = "--clown-final" in args  # corrected clown look-dev sheet, opt-in
    do_clown_r6 = "--clown-r6" in args      # round-6 detailed-hands look-dev, opt-in
    do_clown_r7 = "--clown-r7" in args      # round-7 detailed-hands polish, opt-in
    do_clown_r8 = "--clown-r8" in args      # round-8 reference-grounded hands, opt-in
    do_clown_r9 = "--clown-r9" in args      # round-9 die-seated-in-cradle, opt-in
    do_clown_r10 = "--clown-r10" in args    # round-10 de-thumbed grip + floating die, opt-in
    do_clown_r11 = "--clown-r11" in args    # round-11 4th-finger joined + side-view open hand, opt-in
    do_clown_r12 = "--clown-r12" in args    # round-12 die hand rebuilt as natural open palm-up, opt-in
    do_clown_r13 = "--clown-r13" in args    # round-13 open hand continues the raised arm, opt-in
    do_clown_r14 = "--clown-r14" in args    # round-14 thumb moved to the BACK of the open hand, opt-in
    do_clown_r15 = "--clown-r15" in args    # round-15 die hand rebuilt FROM SCRATCH on real proportions, opt-in
    do_clown_r16 = "--clown-r16" in args    # round-16 hero-zoom hand crop + tamed V2 fan + deeper V5 back-arch, opt-in
    do_clown_r17 = "--clown-r17" in args    # round-17 SIMPLE die-side gesture (closed mitt + pointing/reaching), opt-in
    if do_round7:
        _render_sheet(VERSIONS, "round_7.png", _ROUND7_HEADERS)
    if do_sabers:
        _render_sheet(SABER_VERSIONS, "round_8_sabers.png", _ROUND8_HEADERS)
    if do_marottes:
        _render_sheet(MAROTTE_VERSIONS, "round_8_marottes.png", _ROUND8M_HEADERS)
    if do_craft:
        _render_craft_sheet(MAROTTE_CRAFT_VERSIONS, "round_9_marottes.png", _ROUND9_HEADERS)
    if do_round10:
        _render_craft_sheet(MAROTTE_CRAFT_VERSIONS, "round_10_marottes.png", _ROUND10_HEADERS)
    if "--marottes-8910" in args:
        _render_craft_sheet(MAROTTE_CRAFT_VERSIONS[7:10], "round_10_marottes_8910.png",
                            _ROUND10_BELLFOOT_HEADERS, label_offset=7)
    if do_clown_r2:
        _render_clown_r2_sheet()
    if do_clown_r3:
        _render_clown_r3_sheet()
    if do_clown_r4:
        _render_clown_r4_sheet()
    if do_clown_final:
        _render_clown_final_sheet()
    if do_clown_r6:
        _render_clown_r6_sheet()
    if do_clown_r7:
        _render_clown_r7_sheet()
    if do_clown_r8:
        _render_clown_r8_sheet()
    if do_clown_r9:
        _render_clown_r9_sheet()
    if do_clown_r10:
        _render_clown_r10_sheet()
    if do_clown_r11:
        _render_clown_r11_sheet()
    if do_clown_r12:
        _render_clown_r12_sheet()
    if do_clown_r13:
        _render_clown_r13_sheet()
    if do_clown_r14:
        _render_clown_r14_sheet()
    if do_clown_r15:
        _render_clown_r15_sheet()
    if do_clown_r16:
        _render_clown_r16_sheet()
    if "--clown-r16-crops" in args:
        _render_clown_r16_crops()
    if do_clown_r17:
        _render_clown_r17_sheet()
    if "--clown-r17-crops" in args:
        _render_clown_r17_crops()
    if "--clown-r17-compare" in args:
        _render_clown_r17_compare()
    if "--clown-r17-die" in args:
        _render_clown_r17_die()
    if "--clown-r17-staff" in args:
        _render_clown_r17_staff()
    if "--clown-r17-staffgrid" in args:
        _render_clown_r17_staffgrid()
    if "--staff-route" in args:
        _render_staff_route()
    if "--clown-r17-final" in args:
        _render_clown_r17_final()


if __name__ == "__main__":
    main()
