"""Look-dev sheet for the Skybit BOSS mokoi-versions take — "MIMI".

A flat-graphic painted-spirit spin-off off the shipped Mokoi: where Mokoi is a
blocky floating plank-MASK, Mimi is the opposite KIND — a thin, gangly mid-stride
STICK-FIGURE drawn as frantic crosshatch linework. It is the only thin/linework
silhouette in the brood, for maximal contrast against the blocky masks. Modelled
on the Arnhem Land mimih rock-art figures: extremely thin, elongated, dynamic
hunters caught mid-stride with a thrown spear + woomera (spear-thrower).

House style this obeys (mokoi-versions flat-graphic dialect):
  - CHIBI + scary-CUTE — a doodle come alive, all speed and limbs. Pushed EPIC
    via richer pattern + scale, not via 3D rendering.
  - FLAT saturated fills. NO within-shape gradients, NO bevels, NO soft edges.
    Detail is carried by PATTERN DENSITY (hatch-bands on the limbs), not shading.
  - Hard charcoal ink keyline + a 1px grown outline on the silhouette so the
    thin figure POPS on any sky (the parrot `_add_outline` recipe).
  - YELLOW-DOMINANT body on an overall LIGHT value — the deliberate opposite of
    sibling Baiame's dark charcoal-authority block, so the two never twin. Body
    is warm yellow-ochre; charcoal is reserved for the hatch-keyline + ink. The
    pipeclay-white dot-JOINTS are the protected hue-blind tell.
  - Ember is the lone warm glow, confined to the spear-tip CAP.

The chibi anchor (PINNED): at true 32px a thin hatch-only figure dissolves into
noise — so the figure carries an OVERSIZED, high-contrast pipeclay/charcoal
dot-HEAD that anchors the silhouette. The head carries the read; the hatch body
is texture. The compact gameplay variant grows the head further and bakes a
low-res dot-eye tell so the icon reads "big-headed scribble-spirit," not a speck.

Prop -> pillar mirror: the thrown SPEAR + woomera IS the pillar. One hatch-banded
spear-shaft + one pipeclay dot-knot binding per repeat = the tiling shaft; a
barbed spear-TIP plaque (~strip+30%) = the gap-edge cap, ember confined to the
barb tip. Naturally vertical + symmetric — clean on-axis mirror.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/mokoi_versions/mimi/render_mimi.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (mokoi-versions — MIMI) — hex-exact from the locked brief ──
# Yellow-ochre is the DOMINANT body mass on an overall LIGHT value — the opposite
# value structure from sibling Baiame (dark charcoal block, yellow accent). Keep
# it light so it never twins Baiame. Charcoal is reserved for the hatch-keyline +
# ink. Pipeclay-white dot-joints are the protected hue-blind tell. Red-ochre is a
# faint spear accent only. Ember is the lone warm glow, confined to the cap.
OCHRE       = (204, 158, 86)    # warm yellow-ochre body (DOMINANT, light)
OCHRE_HI    = (224, 184, 116)   # a flat lighter ochre for graphic separation
OCHRE_DK    = (170, 122, 58)    # a quiet deeper ochre for limb shadow-fill

CHAR        = (42, 38, 44)      # charcoal hatch-keyline (linework, NOT a mass)
CHAR_HI     = (62, 56, 64)      # a flat lighter charcoal for hatch variation

PIPECLAY    = (232, 226, 212)   # pipeclay-white dot-joints — the protected tell
PIPECLAY_DK = (190, 184, 170)   # a quiet shade for dot keylines (still light)

REDOCHRE    = (168, 86, 58)     # faint red-ochre spear accent
REDOCHRE_HI = (196, 112, 78)    # lighter red-ochre for the binding twine

EMBER       = (236, 138, 58)    # cap-only ember glow core
EMBER_HOT   = (255, 206, 132)   # ember twinkle centre

INK         = (28, 22, 30)      # the house keyline


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot `_add_outline` recipe). Returns a padded surface."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── flat-graphic primitives (NO triad — fills + ink keylines only) ────────────

def _dot_joint(surf, x, y, r, ss, *, ember=False):
    """A pipeclay dot-JOINT — the protected tell motif, marking each limb pivot.
    A flat filled circle with a thin lighter keyline so it reads as crisp clean
    geometry at high res and survives the downscale. The big dot-HEAD reuses this
    so the joints + head are one coherent dotted system."""
    core = EMBER_HOT if ember else PIPECLAY
    pygame.draw.circle(surf, core, (int(x), int(y)), int(r))
    key = EMBER if ember else PIPECLAY_DK
    pygame.draw.circle(surf, key, (int(x), int(y)), int(r), max(1, int(ss * 0.7)))


def _joint_dot_square(surf, x, y, r, ss):
    """A LOAD-BEARING joint marker built to SURVIVE the downscale to true 32px:
    a fat pipeclay SQUARE wrapped in a hard ink ring. Squares hold their corners
    through smoothscale far better than small discs hold their edge, so the
    hue-blind pipeclay tell stays countable at gameplay scale instead of mushing
    into the ochre limb. Sized so it lands at ~2px pipeclay + 1px ink ring at 1x."""
    s = int(r)
    rect = pygame.Rect(int(x - s), int(y - s), int(2 * s), int(2 * s))
    # Ink ground first (so the ring reads as a hard border on every side).
    pygame.draw.rect(surf, INK, rect.inflate(int(ss * 1.6), int(ss * 1.6)))
    pygame.draw.rect(surf, PIPECLAY, rect)


def _hatch_limb(surf, p0, p1, half_w, ss, col, *, n=5):
    """A thin, gangly LIMB drawn as a hatch-banded bar: a flat yellow-ochre quad
    between two joints, ribbed with short charcoal cross-hatch ticks, then FULLY
    wrapped in a continuous charcoal keyline (both long edges + both end caps) so
    the ochre always sits inside an ink edge — the limb keeps a hard, dark border
    against the bright day sky and never goes soft at 32px. Pure flat fill +
    linework; volume is faked only by the keyline + rib density, never shading."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length          # unit normal across the limb
    ux, uy = dx / length, dy / length            # unit along the limb
    quad = [
        (x0 + nx * half_w, y0 + ny * half_w),
        (x1 + nx * half_w, y1 + ny * half_w),
        (x1 - nx * half_w, y1 - ny * half_w),
        (x0 - nx * half_w, y0 - ny * half_w),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in quad])
    # Charcoal hatch ribs across the limb — the pattern-density detail.
    lw = max(1, int(1.5 * ss))
    for i in range(1, n + 1):
        t = i / (n + 1)
        cxp = x0 + ux * length * t
        cyp = y0 + uy * length * t
        hc = CHAR if i % 2 else CHAR_HI
        pygame.draw.line(surf, hc,
                         (int(cxp + nx * half_w), int(cyp + ny * half_w)),
                         (int(cxp - nx * half_w), int(cyp - ny * half_w)), lw)
    # A continuous charcoal keyline that FULLY rings the limb quad — both long
    # edges AND both end caps — so the ochre is always boxed in ink. Heavier than
    # round 1 so it survives the downscale onto the bright day sky.
    kw = max(2, int(2.2 * ss))
    pygame.draw.polygon(surf, CHAR, [(int(x), int(y)) for x, y in quad], kw)


def _dot_head(surf, cx, cy, r, ss):
    """The OVERSIZED high-contrast dot-HEAD — the chibi anchor (PINNED). A flat
    pipeclay disk ringed by a fat charcoal keyline, carrying two big charcoal
    dot-eyes and a tiny ochre headband stroke. Sized to dominate the thin body so
    the silhouette never dissolves at 32px: the head carries the read, the hatch
    is texture. Flat fills, hard edges — no shading."""
    # Charcoal keyline-mass ring behind the disk (high contrast vs the light body).
    pygame.draw.circle(surf, CHAR, (int(cx), int(cy)), int(r * 1.10))
    # The pipeclay disk (the bright, hue-blind-readable anchor).
    pygame.draw.circle(surf, PIPECLAY, (int(cx), int(cy)), int(r))
    # A fat INK ring fully wrapping the disk so the head pops off BOTH day and
    # night skies and stays the silhouette anchor after the downscale.
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r), max(2, int(2.4 * ss)))
    # A thin red-ochre headband arc across the brow (faint warm accent, the
    # painted-spirit tell on the head).
    band_r = int(r * 0.80)
    pygame.draw.arc(surf, REDOCHRE,
                    pygame.Rect(int(cx - band_r), int(cy - band_r),
                                int(2 * band_r), int(2 * band_r)),
                    math.radians(202), math.radians(338), max(2, int(2.6 * ss)))
    # Two clean high-contrast INK dot-eyes — wide-set with clear pipeclay between
    # them so the face stays scary-CUTE (not a single grey smudge) at 32px. No
    # catch-dot glint: at icon scale it only muddied the read, so the eyes are
    # solid stamped ink discs.
    eye_dx = r * 0.42
    eye_y = cy - r * 0.04
    eye_r = r * 0.24
    for s in (-1, 1):
        ex = cx + s * eye_dx
        pygame.draw.circle(surf, INK, (int(ex), int(eye_y)), int(eye_r))
    # A small bared grin: an INK arc-mouth (open, mid-shout — all speed).
    pygame.draw.arc(surf, INK,
                    pygame.Rect(int(cx - r * 0.32), int(cy + r * 0.18),
                                int(r * 0.64), int(r * 0.50)),
                    math.radians(202), math.radians(338), max(2, int(2.8 * ss)))


# ── the gangly stick-figure ───────────────────────────────────────────────────

def _mimi_figure(surf, cx, cy, scale_px, ss, *, big_head=False):
    """The frantic mid-stride mimih: a tiny torso-bar slung between an OVERSIZED
    dot-head and four splayed hatch-limbs, one arm cocked back hurling a spear
    through a woomera. Everything is flat yellow-ochre fill + charcoal hatch +
    pipeclay dot-joints. `big_head` grows the head for the compact icon so the
    chibi anchor owns the silhouette at true 32px."""
    u = scale_px                                   # one body-unit (already *ss)
    head_r = u * (0.62 if big_head else 0.50)

    # Skeleton, in body-units — caught mid-stride, limbs splayed for max speed.
    # All limbs spring from a short central torso-bar; the read is a scribble.
    head_c   = (cx, cy - u * 1.18)
    neck     = (cx, cy - u * 0.62)
    hip      = (cx + u * 0.06, cy + u * 0.46)
    sh_back  = (cx - u * 0.30, cy - u * 0.42)      # rear shoulder (throwing arm)
    sh_front = (cx + u * 0.30, cy - u * 0.40)      # lead shoulder (balance arm)
    # Throwing arm cocked WAY back-and-up — the spear launches from here.
    elbow_b  = (cx - u * 0.95, cy - u * 0.78)
    hand_b   = (cx - u * 1.46, cy - u * 1.10)
    # Lead arm flung forward for balance.
    elbow_f  = (cx + u * 0.92, cy - u * 0.18)
    hand_f   = (cx + u * 1.40, cy + u * 0.10)
    # Wide mid-stride legs — a deep lunge, all forward momentum.
    knee_b   = (cx - u * 0.62, cy + u * 1.12)      # trailing leg pushing off
    foot_b   = (cx - u * 1.18, cy + u * 1.62)
    knee_f   = (cx + u * 0.74, cy + u * 1.10)      # leading leg reaching out
    foot_f   = (cx + u * 1.30, cy + u * 1.58)

    limb_w   = u * 0.205                            # thin+gangly, widened so the
                                                    # full ink keyline survives 32px
    torso_w  = u * 0.275                            # torso just a touch fatter

    # Draw far-side (back) limbs first, then torso, then near limbs + head, so
    # the dot-joints and head stack cleanly on top.
    _hatch_limb(surf, neck, elbow_b, limb_w, ss, OCHRE_DK, n=3)
    _hatch_limb(surf, elbow_b, hand_b, limb_w, ss, OCHRE_DK, n=3)
    _hatch_limb(surf, hip, knee_b, limb_w, ss, OCHRE_DK, n=4)
    _hatch_limb(surf, knee_b, foot_b, limb_w, ss, OCHRE_DK, n=3)

    # The torso-bar (a touch lighter ochre so it separates from the back limbs).
    _hatch_limb(surf, neck, hip, torso_w, ss, OCHRE, n=4)

    # Near-side limbs (lead arm + lead leg) in the bright body ochre.
    _hatch_limb(surf, neck, elbow_f, limb_w, ss, OCHRE, n=3)
    _hatch_limb(surf, elbow_f, hand_f, limb_w, ss, OCHRE, n=3)
    _hatch_limb(surf, hip, knee_f, limb_w, ss, OCHRE, n=4)
    _hatch_limb(surf, knee_f, foot_f, limb_w, ss, OCHRE, n=3)

    # The thrown SPEAR — a red-ochre shaft launching up-forward from the back
    # hand, through the woomera (spear-thrower hook at the hand). It points up
    # out of frame, foreshadowing the pillar.
    spear_tail = (cx - u * 1.72, cy - u * 1.34)
    spear_tip  = (cx + u * 0.55, cy - u * 2.55)
    pygame.draw.line(surf, REDOCHRE, (int(spear_tail[0]), int(spear_tail[1])),
                     (int(spear_tip[0]), int(spear_tip[1])), max(2, int(3.4 * ss)))
    pygame.draw.line(surf, REDOCHRE_HI, (int(spear_tail[0]), int(spear_tail[1])),
                     (int(spear_tip[0]), int(spear_tip[1])), max(1, int(1.4 * ss)))
    # Woomera hook at the throwing hand (a short red-ochre lever stub).
    pygame.draw.line(surf, REDOCHRE, (int(hand_b[0]), int(hand_b[1])),
                     (int(hand_b[0] - u * 0.34), int(hand_b[1] + u * 0.20)),
                     max(2, int(3.0 * ss)))
    # Barbed spear-tip: a small charcoal arrowhead with an ember spark cap.
    bx, by = spear_tip
    barb = [(bx, by), (bx - u * 0.22, by + u * 0.30), (bx + u * 0.16, by + u * 0.26)]
    pygame.draw.polygon(surf, CHAR, [(int(x), int(y)) for x, y in barb])
    _dot_joint(surf, bx, by - u * 0.02, u * 0.10, ss, ember=True)

    # The protected pipeclay dot-tell, re-spec'd for true-32 legibility: instead
    # of eight small discs that mush at gameplay scale, FOUR load-bearing joint
    # SQUARES — one per limb at its mid pivot (elbow / knee) — each fat + ink-ringed
    # so they stay COUNTABLE after the downscale. The hue-blind articulation tell
    # now survives at 32px instead of being head-only.
    jr = limb_w * 1.05
    for jx, jy in (elbow_b, elbow_f, knee_b, knee_f):
        _joint_dot_square(surf, jx, jy, jr, ss)
    # A small pipeclay hub at the shoulder/hip core so the four limbs still read
    # as sprung from one body — a quiet connector, not a counted tell.
    _dot_joint(surf, hip[0], hip[1], limb_w * 0.6, ss)
    _dot_joint(surf, (sh_back[0] + sh_front[0]) * 0.5,
               (sh_back[1] + sh_front[1]) * 0.5, limb_w * 0.55, ss)

    # The OVERSIZED dot-HEAD last so it owns the silhouette (the chibi anchor).
    _dot_head(surf, head_c[0], head_c[1], head_r * u / u, ss)


def _baked_head_tell(surf, cx, cy, r, ss):
    """A baked LOW-RES head tell for the compact icon: the big pipeclay dot-head
    with two fat charcoal dot-eyes, sized so smoothscale to true 32px PRESERVES a
    recognizable big-headed dotted spirit instead of mushing to noise. The thin
    hatch limbs survive only as a faint scribble; this head is what carries the
    'big-headed scribble-spirit' read at icon scale."""
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r * 1.12))
    pygame.draw.circle(surf, PIPECLAY, (int(cx), int(cy)), int(r))
    eye_dx = r * 0.42
    eye_r = r * 0.28
    for s in (-1, 1):
        pygame.draw.circle(surf, INK, (int(cx + s * eye_dx), int(cy - r * 0.04)),
                           int(eye_r))


def build_mimi(scale=1.0, ss=5, *, compact=False):
    """The full creature on its own transparent surface: the frantic mid-stride
    mimih, big dot-head up top, spear launching out the top-right. Returns an
    outlined surface. Renders LARGE at SS=5-6 then smoothscales down so the dense
    hatch + dot geometry stays crisp.

    `compact` is the GAMEPLAY / 32px-icon variant: the dot-HEAD is grown to
    dominate the vertical budget and a low-res head tell is baked, so the icon
    reads 'big-headed scribble-spirit' — not a thin tangle of lines with a speck.
    """
    u = int(22 * scale) * ss                       # one body-unit
    # The figure spans roughly: spear-tip (top) to feet (bottom), hand-b (left)
    # to hand-f (right). Pad generously so nothing clips after the outline grow.
    pad = int(8 * scale) * ss
    W = int(u * 3.7 + 2 * pad)
    H = int(u * 4.5 + 2 * pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    # Centre the figure's torso roughly in the lower-middle so the spear has room.
    cx = W // 2 - int(u * 0.1)
    cy = int(H * 0.52)

    _mimi_figure(surf, cx, cy, u, ss, big_head=compact)
    if compact:
        head_r = u * 0.62
        _baked_head_tell(surf, cx, cy - u * 1.18, head_r, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallv)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _spear_band_repeat(surf, cx, y0, band_h, half_w, ss):
    """ONE repeat of the thrown-spear shaft: a hatch-banded red-ochre spear-shaft
    segment + one pipeclay dot-knot binding. This is the unit that TILES
    top<->bottom — exactly one hatch-banded shaft + one dot-knot per repeat.
    Pure flat motifs; the alternation + the dot cadence are the read."""
    # The yellow-ochre shaft ground for this repeat (the dominant light mass).
    pygame.draw.rect(surf, OCHRE,
                     (int(cx - half_w), int(y0), int(2 * half_w), int(band_h)))
    pygame.draw.rect(surf, OCHRE_HI,
                     (int(cx - half_w * 0.5), int(y0), int(half_w), int(band_h)))

    # Charcoal cross-hatch ribs banding the shaft — the pattern-density detail.
    lw = max(1, int(1.6 * ss))
    n = 4
    for i in range(n):
        ry = y0 + band_h * ((i + 0.5) / n)
        hc = CHAR if i % 2 else CHAR_HI
        # Short diagonal ticks crossing the shaft (the frantic scribble texture).
        pygame.draw.line(surf, hc, (int(cx - half_w * 0.8), int(ry - half_w * 0.5)),
                         (int(cx + half_w * 0.8), int(ry + half_w * 0.5)), lw)
        pygame.draw.line(surf, hc, (int(cx - half_w * 0.8), int(ry + half_w * 0.5)),
                         (int(cx + half_w * 0.8), int(ry - half_w * 0.5)), lw)

    # A pipeclay dot-KNOT binding at the band midpoint — the protected tell,
    # reading as the sinew lashing that binds the spear-thrower to the shaft.
    knot_y = y0 + band_h * 0.5
    _dot_joint(surf, cx, knot_y, half_w * 0.46, ss)
    # A faint red-ochre twine wrap flanking the knot.
    for s in (-1, 1):
        pygame.draw.line(surf, REDOCHRE,
                         (int(cx + s * half_w * 0.66), int(knot_y - half_w * 0.34)),
                         (int(cx + s * half_w * 0.66), int(knot_y + half_w * 0.34)),
                         max(1, int(1.8 * ss)))

    # Charcoal keyline up both long edges so the shaft reads as one spear.
    for s in (-1, 1):
        pygame.draw.line(surf, CHAR, (int(cx + s * half_w), int(y0)),
                         (int(cx + s * half_w), int(y0 + band_h)),
                         max(1, int(1.6 * ss)))


def _spear_column(surf, cx, top_y, bot_y, half_w, ss):
    """The repeatable PILLAR BODY: the thrown-spear shaft as a straight tiling
    post — exactly one hatch-banded shaft + one pipeclay dot-knot per repeat (the
    band that mirrors top<->bottom). NO ember here — ember is cap-only."""
    length = bot_y - top_y
    band = half_w * 3.2
    n = max(1, int(round(length / band)))
    band = length / n
    for i in range(n):
        _spear_band_repeat(surf, cx, top_y + i * band, band, half_w, ss)


def _barb_cap(surf, cx, cap_base_y, half_w, ss, *, point_up, night=False):
    """The creature-derived GAP-EDGE CAP: a barbed spear-TIP plaque sized
    ~shaft+30%, facing the gap, with the EMBER glow CONFINED to the barb tip (the
    only warm light anywhere). `point_up` faces the barb toward the gap."""
    d = -1 if point_up else 1
    plaque_hw = half_w * 1.30          # cap ~ shaft + 30%
    tip_len = plaque_hw * 2.4
    tip_y = cap_base_y + d * tip_len   # the barb point, into the gap

    # Ember glow CONFINED to the barb tip — radiates INTO the gap. Night alpha +
    # radius pulled DOWN so the halo stays a contained cap glow and does not
    # bloom into the shaft.
    gr = int(plaque_hw * (1.5 if night else 1.3))
    gl = make_glow_surface(gr, EMBER, alpha_center=160 if night else 125, falloff=2.4)
    surf.blit(gl, (int(cx - gr), int(tip_y - gr)), special_flags=pygame.BLEND_ADD)

    # The barbed arrowhead: a flat yellow-ochre diamond-blade with charcoal
    # barb-hooks, on-axis. Built from the base ring out to the point.
    base_y = cap_base_y + d * half_w * 0.5
    blade = [
        (cx, tip_y),
        (cx - plaque_hw, base_y + d * tip_len * 0.32),
        (cx, base_y),
        (cx + plaque_hw, base_y + d * tip_len * 0.32),
    ]
    pygame.draw.polygon(surf, OCHRE, [(int(x), int(y)) for x, y in blade])
    pygame.draw.polygon(surf, CHAR, [(int(x), int(y)) for x, y in blade],
                        max(1, int(1.8 * ss)))
    # Barb hooks flaring back from the blade base (the "barbed" read).
    for s in (-1, 1):
        hook = [
            (cx + s * plaque_hw * 0.9, base_y + d * tip_len * 0.28),
            (cx + s * plaque_hw * 1.45, base_y - d * tip_len * 0.10),
            (cx + s * plaque_hw * 0.7, base_y + d * tip_len * 0.02),
        ]
        pygame.draw.polygon(surf, CHAR, [(int(x), int(y)) for x, y in hook])
    # The WOOMERA read: an ASYMMETRIC hooked lug jutting off ONE side of the
    # blade base — the spear-thrower's catch-peg. This is the silhouette tell that
    # separates the cap from a generic barb and from the roster's other staff/pole
    # caps: a clean spear-thrower, not just a point. Built as a red-ochre cranked
    # hook (the prop accent) outlined in ink so it reads at the cap.
    lug = [
        (cx + plaque_hw * 0.55, base_y + d * half_w * 0.10),
        (cx + plaque_hw * 1.85, base_y + d * half_w * 0.10),
        (cx + plaque_hw * 1.95, base_y - d * tip_len * 0.34),
        (cx + plaque_hw * 1.50, base_y - d * tip_len * 0.30),
        (cx + plaque_hw * 1.42, base_y - d * half_w * 0.30),
        (cx + plaque_hw * 0.55, base_y - d * half_w * 0.30),
    ]
    pygame.draw.polygon(surf, REDOCHRE, [(int(x), int(y)) for x, y in lug])
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in lug],
                        max(2, int(1.8 * ss)))
    # A pipeclay dot-knot at the blade base — the tell, binding tip to shaft.
    _dot_joint(surf, cx, base_y, plaque_hw * 0.34, ss)
    # Charcoal hatch ribs up the blade centreline (pattern density on the cap).
    for i in range(1, 4):
        t = i / 4.0
        ry = base_y + d * (tip_y - base_y) * t * 0.9
        hw = plaque_hw * (1 - t) * 0.7
        pygame.draw.line(surf, CHAR, (int(cx - hw), int(ry)), (int(cx + hw), int(ry)),
                         max(1, int(1.5 * ss)))
    # Ember twinkle core at the very point — the lone warm spark.
    pygame.draw.circle(surf, EMBER, (int(cx), int(tip_y)), max(1, int(plaque_hw * 0.22)))
    pygame.draw.circle(surf, EMBER_HOT, (int(cx), int(tip_y)), max(1, int(plaque_hw * 0.11)))


def _spear_pillar_obstacle(height, ss, *, flip, night=False):
    """One thrown-spear pillar obstacle: the hatch/dot-knot shaft fills the post
    and a barbed spear-tip CAP sits at the GAP-facing edge, its ember glow
    radiating INTO the gap. `flip=True` is the TOP pillar — cap at the bottom
    (gap) edge; `flip=False` is the BOTTOM pillar — cap at the top (gap) edge.
    Both mirror the same hatch+knot body into a clean vertical spear-pillar."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    half_w = int((PIPE_W * 0.34)) * ss
    cap_band = int(58 * ss)
    if flip:
        _spear_column(surf, cx, 0, bh - cap_band, half_w, ss)
        _barb_cap(surf, cx, bh - cap_band, half_w, ss, point_up=False, night=night)
    else:
        _spear_column(surf, cx, cap_band, bh, half_w, ss)
        _barb_cap(surf, cx, cap_band, half_w, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    return _add_outline(out)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(245, 240, 230)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot, *, stars=False):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    if stars:
        import random as _r
        rng = _r.Random(99)
        for _ in range(26):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, int(h * 0.7))
            pygame.draw.circle(s, (220, 230, 255), (sx, sy), rng.choice((1, 1, 2)))
    return s


def _to_gray(src):
    g = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    g.blit(src, (0, 0))
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    return g


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1080, 770
    sheet = pygame.Surface((SW, SH))
    sheet.fill((120, 120, 124))            # neutral grey bg
    _label(sheet, font,
           "MIMI  —  mokoi-versions  —  thin crosshatch stick-spirit + thrown-spear pillar  —  round 2",
           18, 12, (24, 24, 28))
    _label(sheet, small,
           "R2 fixes: 4 FAT ink-ringed joint-SQUARES survive 32px; limbs FULLY ink-wrapped + widened; clean ink dot-eyes; woomera lug on the cap. Yellow-DOMINANT LIGHT, ember cap-only.",
           18, 32, (40, 40, 46))

    # — Cell A: the BIG hero stick-figure on a neutral panel (elevated SS=6).
    panel = pygame.Rect(18, 56, 320, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panel, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panel, 2, border_radius=8)
    _label(sheet, font, "(a) HERO  big scale  SS=6", panel.x + 8, panel.y + 8, (245, 240, 230))
    _label(sheet, small, "ink-wrapped limbs; 4 fat joint-squares; woomera-lug spear",
           panel.x + 8, panel.y + 28, (235, 230, 220))
    hero = build_mimi(scale=1.7, ss=6)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2,
                      panel.centery - hero.get_height() // 2 + 16))

    # — Cell B: spear as a tileable PILLAR pair at TRUE obstacle scale, on NIGHT,
    #   plus a 2x zoom of the CAP band proving the contained ember + the mirror.
    panelB = pygame.Rect(348, 56, 320, 600)
    bg = _sky(panelB.w, panelB.h, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (60, 60, 64), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE  (NIGHT)", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 500
    slice_x = panelB.x + 22
    slice_y = panelB.y + 44
    gap_top = 158
    gap_h = 124
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _spear_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _spear_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (210, 200, 180), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native: hatch-banded shaft +", slice_x - 2, slice_y + slice_h + 6,
           (235, 225, 210))
    _label(sheet, small, "dot-knot per repeat tiles; barbed-tip cap, ember only",
           slice_x - 2, slice_y + slice_h + 22, (255, 210, 150))

    cap_band = 58
    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 14
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 170
    zy = panelB.y + 110
    zbg = _sky(zw * 2, zh * 2, (8, 8, 30), (16, 14, 44), (28, 20, 58))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (210, 200, 180), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom CAP band:", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "barbed spear-tip cap;", zx - 2, zy + zh * 2 + 6, (255, 210, 150))
    _label(sheet, small, "mirror visible; ember -> gap", zx - 2, zy + zh * 2 + 22, (255, 210, 150))

    # — Cell C: TRUE 32px gameplay chip on a DAY sky AND a NIGHT sky, plus a 4x
    #   audit + grayscale tell-check.
    panelC = pygame.Rect(678, 56, 384, 600)
    pygame.draw.rect(sheet, (96, 96, 100), panelC, border_radius=8)
    pygame.draw.rect(sheet, (60, 60, 64), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8, (245, 240, 230))
    _label(sheet, small, "head-dominant compact; day + night skies", panelC.x + 8, panelC.y + 28,
           (235, 230, 220))

    # The compact gameplay creature blown up for a clear day/night read.
    boss = build_mimi(scale=0.66, ss=5, compact=True)
    day = _sky(140, 280, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(140, 280, (8, 8, 30), (20, 18, 52), (40, 30, 70), stars=True)
    dy = panelC.y + 48
    sheet.blit(day, (panelC.x + 16, dy))
    sheet.blit(night, (panelC.x + 168, dy))
    sheet.blit(boss, (panelC.x + 16 + 70 - boss.get_width() // 2,
                      dy + 140 - boss.get_height() // 2))
    sheet.blit(boss, (panelC.x + 168 + 70 - boss.get_width() // 2,
                      dy + 140 - boss.get_height() // 2))
    _label(sheet, small, "DAY", panelC.x + 16 + 6, dy + 6, (18, 28, 24))
    _label(sheet, small, "NIGHT", panelC.x + 168 + 6, dy + 6, (255, 220, 200))

    # The TRUE-32 icon: shown at 1x on day/night/neutral chips, then 3x audit + gray.
    icon_src = build_mimi(scale=1.0, ss=5, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))
    sc64 = 64 / icon_src.get_height()
    icon64 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc64)), 64))

    gy = dy + 296
    _label(sheet, small, "TRUE 32px-tall at 1x (no blow-up):", panelC.x + 16, gy - 2,
           (235, 225, 215))
    swatches = [
        ((40, 110, 200), "day"),
        ((40, 30, 70), "night"),
        ((96, 96, 100), "neutral"),
    ]
    sx = panelC.x + 16
    sw = 92
    for col, lab in swatches:
        chip = pygame.Rect(sx, gy + 16, sw, 76)
        pygame.draw.rect(sheet, col, chip, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 240))
        sx += sw + 8

    # 3x nearest-neighbour blow-up of the true-32 icon so the tell is auditable,
    # plus the grayscale value check (the protected dot tell must survive).
    chip = pygame.Rect(panelC.x + 16, gy + 104, 86, 100)
    pygame.draw.rect(sheet, (78, 78, 82), chip, border_radius=4)
    blow = pygame.transform.scale(icon32, (icon32.get_width() * 3, icon32.get_height() * 3))
    sheet.blit(blow, (chip.x + 6, chip.centery - blow.get_height() // 2))
    sheet.blit(icon64, (chip.right + 10, chip.centery - icon64.get_height() // 2))
    _label(sheet, small, "3x / 64px audit", chip.x + 4, chip.y + 2, (240, 240, 240))

    gray = _to_gray(icon64)
    gchip = pygame.Rect(panelC.x + 250, gy + 104, 100, 100)
    pygame.draw.rect(sheet, (124, 128, 124), gchip, border_radius=4)
    sheet.blit(gray, (gchip.centerx - gray.get_width() // 2,
                      gchip.centery - gray.get_height() // 2))
    _label(sheet, small, "grayscale tell", gchip.x + 4, gchip.y + 2, (24, 24, 24))

    # — Footer: style notes.
    _label(sheet, small,
           "FLAT only: detail via PATTERN DENSITY (hatch-banded limbs + dot-joints), never 3D shading; yellow-ochre LIGHT body dominant; charcoal = hatch-keyline; pipeclay dots are the protected tell.",
           18, SH - 64, (40, 40, 46))
    _label(sheet, small,
           "prop->pillar: thrown spear = 1 hatch-banded shaft + 1 pipeclay dot-knot per repeat (tiles); gap-edge cap = barbed spear-tip plaque w/ ember CONFINED to the tip. Clean on-axis mirror.",
           18, SH - 44, (40, 40, 46))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
