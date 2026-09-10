"""
Round-1 concept renderer for CHANDRA-MATA — the lunar crescent-arc bone-mother
(Mukha-Devi brood, concept #3). Headless Pygame; ELEVATED pipeline (supersample
SS=6 -> smoothscale) so the slim arms + moon-phase bead-arc stay crisp at
downscale. Keeps the citipati house grammar: flat triad (dark-core -> flat-fill
-> top-left rim-sheen), hard 1-2px ink keyline (28,22,26), 1px alpha-grown
outline, scary-CUTE; procedural-only.

WHY this is the WIDE-LOW-CRESCENT + RISING-HORN KIND (a shape no sibling can
collide with): the six arms sweep ONLY the lower hemisphere, cupping the torso in
a wide shallow smile-arc, while a SINGLE large crescent-horn rises BEHIND the
crown. Blackout therefore reads as a low cupping SMILE under a rising HORN —
unlike Mukha's symmetric open sideways starburst (arms in BOTH hemispheres). The
arms are slim/elegant and the whole figure is MID-TALL, not chibi-squat: the
brood's slender silhouette.

WHY moon-silver + grey-lilac, DESATURATED and GREY-leaning: the cross-set pin
bans Necrarch's saturated violet-glow and Draugr/Yurei's blue-cyan. The accent
is the only NIGHT-tuned hue in the roster, so the moon-phase disc cores carry a
hair MORE value contrast (brighter lit limb + darker shadow limb) than they would
warm-toned — they have to pop dark-on-dark on the night biome at 32px.

WHY six MOON-PHASE discs + eclipse-charm skulls on the OUTER tips: each hand
cradles one disc (waning -> new -> waxing), so the lower arc reads as an even bead
string. At 32px the phases blur to identical beads, so identity rides the ARC and
the HORN, not legible phases (the brief's 32px rule). Tiny skulls hang only from
the TWO OUTER crescent-tips as eclipse-charms — the arm-end-skull DNA survives.

WHY a moon-gnomon staff IS the pillar: an upright bone gnomon casting a banded
shadow-scale, hung with phase-disc pendants, tiles as the shaft; the cap is a
single rising crescent-horn cradling a lit full-moon at the gap — the creature's
own lunar language, bottom-rooted.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Moon-silver bone is the dominant mass — cool/neutral pale, NOT warm rose (that's
# Mukha) and NOT ash-white. Grey-lilac is the single accent, DESATURATED and
# GREY-leaning so it never tips into Necrarch's saturated violet.
BONE      = (196, 194, 206)   # moon-silver bone (the dominant fill) — pulled ~20%
                              # darker/greyer than r2's (214,212,222) so the hero
                              # holds VALUE on the pale-blue DAY sky, not just night
BONE_D    = (138, 136, 150)   # cool grey-bone dark-core / shade
BONE_DD   = (104, 102, 118)   # deepest bone hollow (sockets, grooves)
BONE_SH   = (244, 244, 250)   # bone top-left rim-sheen (moonlit)
LILAC     = (176, 168, 196)   # grey-lilac accent — DESATURATED, grey-leaning
LILAC_BR  = (216, 210, 232)   # lit limb / sheen of the lilac accent
LILAC_D   = (108,  98, 132)   # shadow limb / deep grey-lilac (the value-contrast end)
LILAC_DD  = ( 70,  62,  92)   # deepest grey-lilac (disc shadow core, night pop)
SILVER    = (198, 200, 214)   # cold moon-silver trim (gnomon rings, horn rim)
SILVER_BR = (238, 240, 248)
INK       = ( 28,  22,  26)   # hard ink keyline (shared with the lineage)
EYE_GLOW  = (188, 180, 208)   # cool lilac eye-glow (her power-focus, NOT magenta)
EYE_BR    = (230, 226, 244)   # hot inner of the eye-glow

BG        = ( 96,  92, 100)   # neutral grey review backdrop
PANEL     = ( 74,  72,  84)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top) — the hostile dark-on-dark test
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 236, 240)
LABEL_DIM = (196, 190, 202)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob — dark core bottom-right, sheen top-left."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def crescent(surf, cx, cy, r, color, dark, sheen, ow, bite=0.62, ang=-90.0):
    """A clean crescent: a full disc with a second disc punched out to leave a
    horn. `ang` aims the horn's OPENING; `bite` is how deep the cut goes (smaller
    = fatter crescent). Built as a mask so the inner edge is a true arc, then
    re-keyed with ink. Returns nothing; draws in place.

    WHY mask-punched rather than two arcs: a polygon crescent gets chunky inner
    facets at SS downscale; a boolean disc-minus-disc keeps the lunar inner curve
    smooth, which is the whole identity tell."""
    size = r * 3
    tmp = pygame.Surface((size, size), pygame.SRCALPHA)
    c0 = (size // 2, size // 2)
    pygame.draw.circle(tmp, color, c0, r)
    # offset the subtractor toward the opening so a horn remains on the far side
    a = math.radians(ang)
    ox = int(math.cos(a) * r * bite)
    oy = int(math.sin(a) * r * bite)
    cut = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(cut, (0, 0, 0, 255), (c0[0] + ox, c0[1] + oy), int(r * 0.96))
    tmp.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    # value-contrast: a brighter lit limb on the OUTER rim, darker toward the cut
    lit = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(lit, sheen, (c0[0] - int(r * 0.28), c0[1] - int(r * 0.30)), int(r * 0.92))
    lit.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    # punch the lit cap back to where the crescent actually exists
    cap = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(cap, (0, 0, 0, 255), c0, r)
    cap_cut = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(cap_cut, (0, 0, 0, 255), (c0[0] + ox, c0[1] + oy), int(r * 0.96))
    cap.blit(cap_cut, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    lit2 = pygame.Surface((size, size), pygame.SRCALPHA)
    lit2.blit(lit, (0, 0))
    lit2.blit(cap, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(tmp, (cx - c0[0], cy - c0[1]))
    surf.blit(lit2, (cx - c0[0], cy - c0[1]))


def moon_disc(surf, cx, cy, r, s, phase=0):
    """One IDENTICAL flat-lilac bead held in a hand — a moon-disc charm, NOT a
    rendered phase. WHY identical beads (the `phase` arg is ignored): phase
    terminators die to mush at 32px, so every bead is the same to read as a clean
    deliberate bead-STRING along the crescent. WHY a darker-lilac CORE under a
    brighter cold-silver RIM: this is the only NIGHT-tuned accent, so a hard
    core↔rim value jump (deep LILAC_DD core -> bright SILVER_BR rim) lets the bead
    pop both dark-on-light (DAY) and dark-on-dark (NIGHT) at 32px."""
    # bright cold-silver rim ring (the value HIGH, top-left lit)
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(s)))
    pygame.draw.circle(surf, SILVER_BR, (cx, cy), r)
    pygame.draw.circle(surf, SILVER, (cx + int(r * 0.2), cy + int(r * 0.22)), int(r * 0.92))
    # the darker grey-lilac core (the value LOW) — a clear step darker than the rim
    inner = max(1, int(r * 0.66))
    pygame.draw.circle(surf, LILAC_D, (cx, cy), inner)
    pygame.draw.circle(surf, LILAC_DD, (cx + int(inner * 0.22), cy + int(inner * 0.24)),
                       int(inner * 0.82))
    # a single bright catch-light on the rim's top-left (seals the core↔rim contrast)
    pygame.draw.circle(surf, SILVER_BR, (cx - int(r * 0.44), cy - int(r * 0.46)),
                       max(1, int(r * 0.24)))
    pygame.draw.circle(surf, INK, (cx, cy), r, max(1, int(1.2 * s)))


def eclipse_skull(surf, cx, cy, r, s, lit=False):
    """Tiny moon-silver skull hung as an eclipse-charm off an outer crescent-tip.
    WHY a domed cranium + two dark sockets: it must punch a clean bone shape at
    32px so the arm-end-skull DNA survives even when the discs blur to beads."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.3 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.30), cy + int(r * 0.92)),
           (cx - int(r * 0.30), cy + int(r * 0.92))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.0 * s)))
    eye_c = EYE_BR if lit else INK
    for ex in (cx - int(r * 0.36), cx + int(r * 0.36)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.40)), max(1, int(r * 0.13)))


# ── the WIDE-LOW crescent CUP arm-arc (the KIND tell) ─────────────────────────
def _cup_point(sh_cx, tip_y, span_r, depth, t):
    """One point on the crescent-CUP path, t in [-1,+1] (left tip -> midline -> right
    tip). WHY this profile: x grows linearly with |t| while y follows a raised
    cosine so the path sits LOW at the midline (t=0) and curves back UP to `tip_y`
    at the tips (|t|=1). `tip_y` is set ABOVE the midline so the outer tips rise to
    shoulder height — a true U/bowl whose lateral SPAN is ~1.7x its DEPTH, a low
    cupping crescent, NOT a downward spray."""
    x = sh_cx + t * span_r
    # raised cosine: 1 at the midline (low) -> 0 at the tips (high)
    dip = 0.5 * (1.0 + math.cos(t * math.pi))
    y = tip_y + depth * dip
    return (x, y)


def draw_low_crescent_arms(surf, sh_cx, sh_cy, s, span_r):
    """Six slim bone arms spread WIDE + LATERAL, each bowing DOWN at the midline and
    curving back UP at the tip, so the six hands sit on a single U/BOWL whose width
    is ~1.7x its depth and whose OUTER tips rise to ~shoulder height or above.

    WHY a cupping crescent and NOT a downward spray: this is the cross-pin vs
    Mukha. Her six arms fan out in a symmetric sideways starburst; Chandra's sweep
    ONLY the lower hemisphere AND close back upward at the ends, so the blackout
    reads as a low cupping CRESCENT-smile that echoes the small rising horn above
    (small horn up, wide crescent down). There are NO vertical-down centre limbs —
    the two innermost arms reach laterally-inward to the LOW midline of the bowl,
    never straight down. Returns the six hand centres + the two OUTER tips flagged
    for the eclipse-charm skulls that cap the crescent's horns."""
    arm_th = int(9 * s)              # +~28% over r1's slim limb so it holds at 32px
    # six hands along the cup, evenly spaced from left tip to right tip.
    # WHY depth ~0.80x span_r: lateral span is 2*span_r, so width/depth ~= 2.5 — a
    # WIDE shallow smile, but with a real downward DIP at the midline so the blackout
    # reads as a curved CUP/smile rather than the flat horizontal bar that too-shallow
    # produced. The midline beads sit clearly LOW; the outer tips ride well UP into
    # two distinct cusps above shoulder height (a true U, not a line).
    depth = int(span_r * 0.80)
    tip_y = sh_cy - int(span_r * 0.86)     # outer tips RISE clearly above shoulder
    # WHY the inner pair is pulled WIDE (|t|=0.46, was 0.34): the two midline beads
    # must sit far enough apart that BACKGROUND shows through the centre of the U
    # beneath the torso — an OPEN cup with air inside, not a filled skirt. The inner
    # arms reach laterally-outward to a HIGH, wide midline so the bottom of the cup is
    # a shallow open smile that clears the body entirely.
    ts = [-1.0, -0.70, -0.46, 0.46, 0.70, 1.0]
    hands_t = [(t, _cup_point(sh_cx, tip_y, span_r, depth, t)) for t in ts]

    # the two shoulders the arms spring from (just inboard of the torso). WHY high +
    # narrow: the arms must spring UP-and-OUT toward the high cusps so the cup's inner
    # edge clears the torso and leaves open air below it, not wrap under the body.
    def shoulder(sgn):
        return (sh_cx + sgn * int(span_r * 0.16), sh_cy - int(span_r * 0.62))

    # draw the MIDLINE (low, behind) arms first; the OUTER (high, front) arms last
    # so the up-curved tips overlap on top and the bowl reads as one continuous cup.
    order = sorted(hands_t, key=lambda ht: abs(ht[0]))        # midline first, tips last
    for t, hand in order:
        sgn = -1 if t < 0 else 1
        sh = shoulder(sgn)
        # elbow biased DOWN of the chord so EVERY limb sags below its shoulder->hand
        # line — including the outer arms, whose tips ride high. WHY a deep sag on
        # the outer arms too: it stops them reading as a horizontal T-bar and makes
        # the whole arm contribute to the cup's downward curve before sweeping UP to
        # the high tip — the crescent-member smile, never a radial spoke.
        mx, my = (sh[0] + hand[0]) / 2.0, (sh[1] + hand[1]) / 2.0
        # WHY a SHALLOW sag (was span*0.30 + extra): a deep elbow-drop pushed every
        # arm down into the centre of the U and filled it solid. A light sag lets the
        # arm follow the shallow smile-arc, keeping the inner negative space OPEN so
        # the eye reads a wide crescent cup with air inside, not a bulbous skirt.
        bow = (1.0 - abs(t)) * span_r * 0.06 + span_r * 0.11
        elbow = (mx + sgn * span_r * 0.10, my + bow)
        for (p, q) in ((sh, elbow), (elbow, hand)):
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = max(1.0, math.hypot(dx, dy))
            nx, ny = -dy / L * arm_th / 2, dx / L * arm_th / 2
            quad = [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                    (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]
            triad_blob(surf, BONE, quad,
                       sheen_pts=[(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                                  (q[0] + nx * 0.3, q[1] + ny * 0.3),
                                  (p[0] + nx * 0.3, p[1] + ny * 0.3)],
                       ow=max(1, int(arm_th * 0.22)))
        triad_circle(surf, BONE, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.0 * s)), core=False)
    is_outer = {ts[0], ts[-1]}
    return [(int(h[0]), int(h[1]), (t in is_outer))
            for t, h in sorted(hands_t, key=lambda ht: ht[1][0])]


# ── the rising crescent-horn behind the crown (the second tell) ───────────────
def draw_rising_horn(surf, cx, cy, hr, s):
    """A SINGLE large crescent-horn rising BEHIND the crown — the upper-hemisphere
    half of the silhouette. WHY one big horn, not a fan: paired with the low arc it
    makes the blackout read 'low cupping smile UNDER a rising horn,' the two-part
    tell that no sibling shares. Drawn first so it sits behind the head."""
    horn_r = int(hr * 1.7)
    hcx, hcy = cx, cy - int(hr * 1.15)
    # the dark keyline horn (slightly larger), then the silver crescent on top
    crescent(surf, hcx, hcy, horn_r + max(1, int(2 * s)), INK, INK, INK,
             ow=0, bite=0.52, ang=90.0)
    crescent(surf, hcx, hcy, horn_r, SILVER, LILAC_D, SILVER_BR,
             ow=0, bite=0.52, ang=90.0)
    # a thin lilac inner-rim line tracing the lit inner edge of the horn
    for k in range(7):
        t = k / 6.0
        aa = math.radians(150 + t * 60)
        rx = hcx + int(math.cos(aa) * horn_r * 0.74)
        ry = hcy + int(math.sin(aa) * horn_r * 0.74)
        pygame.draw.circle(surf, LILAC_BR, (rx, ry), max(1, int(1.4 * s)))


# ── the lunar bone-mother ─────────────────────────────────────────────────────
def draw_chandra_mata(surf, cx, cy, s):
    """Slim, MID-TALL lunar death-mother: an elegant skull-head under a single
    rising crescent-horn, six slim arms cupping a wide LOW smile-arc of moon-phase
    discs, eclipse-charm skulls swinging from the two outer crescent-tips.
    `s` = unit scale around a ~150-unit-tall figure."""

    head_c = (cx, cy - int(34 * s))
    hr = int(26 * s)                 # smaller head than Mukha (slim, not chibi)
    disc_r = int(12 * s)             # enlarged bead so the arc reads at 32px DAY

    # === RISING CRESCENT-HORN (behind everything) =============================
    draw_rising_horn(surf, head_c[0], head_c[1], hr, s)

    # === WIDE LOW CRESCENT CUP (drawn behind torso) ===========================
    # WHY a wide span anchored BELOW the chest: the arms spread wide, dip only
    # SHALLOWLY at the midline and sweep back UP at the tips, so the bowl is a wide
    # shallow smile (span >> depth) whose outer cusps rise above the shoulder and
    # whose centre leaves OPEN air beneath the torso — the low cupping crescent that
    # echoes the small rising horn above (small horn up / wide cup down).
    span_r = int(hr * 2.70)
    hands = draw_low_crescent_arms(surf, head_c[0], cy + int(40 * s), s, span_r)

    # === SLIM TALL TORSO — a narrow elegant rib-column ========================
    # WHY narrow + tall: this brood member is the slim/elegant one; a slender
    # column under a modest head reads MID-TALL, the antithesis of Mukha's squat
    # chibi barrel.
    rc_cx = cx
    rc_top = head_c[1] + int(hr * 0.86)
    # WHY a shorter column: the torso must sit ABOVE the cup's open bottom so the
    # bead-string reads as one continuous crescent around the body, not as a body
    # with the lowest beads fused on as legs.
    rc_bot = cy + int(26 * s)
    rc_w = int(20 * s)
    cage = [(rc_cx - rc_w // 2, rc_top),
            (rc_cx + rc_w // 2, rc_top),
            (rc_cx + int(rc_w * 0.40), rc_bot),
            (rc_cx - int(rc_w * 0.40), rc_bot)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_top + int(2 * s)),
                         (rc_cx + rc_w // 2, rc_top),
                         (rc_cx + int(rc_w * 0.40), rc_bot),
                         (rc_cx + int(2 * s), rc_bot)],
               sheen_pts=[(rc_cx - rc_w // 2, rc_top + int(2 * s)),
                          (rc_cx - int(3 * s), rc_top),
                          (rc_cx - int(5 * s), rc_bot - int(6 * s)),
                          (rc_cx - rc_w // 2, rc_bot - int(8 * s))],
               ow=max(1, int(1.6 * s)))
    # hard rib bands down the slim column
    for i in range(4):
        ry = rc_top + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.42 - i * 0.03))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(5 * s), bw * 2, int(12 * s)),
                        math.radians(205), math.radians(335), max(2, int(1.8 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_top + int(4 * s)),
                     (rc_cx, rc_bot - int(4 * s)), max(1, int(1.6 * s)))
    # a thin grey-lilac prayer-cord sash (linear accent, never a mass)
    pygame.draw.line(surf, LILAC, (rc_cx - int(rc_w * 0.42), rc_top + int(14 * s)),
                     (rc_cx + int(rc_w * 0.42), rc_top + int(10 * s)), max(1, int(1.6 * s)))

    # === a small lunar pelvis-cap so the figure roots (slim, not a wide base) ==
    base_y = rc_bot
    base = [(rc_cx - int(14 * s), base_y - int(4 * s)),
            (rc_cx - int(9 * s), base_y - int(9 * s)),
            (rc_cx + int(9 * s), base_y - int(9 * s)),
            (rc_cx + int(14 * s), base_y - int(4 * s)),
            (rc_cx + int(10 * s), base_y + int(7 * s)),
            (rc_cx - int(10 * s), base_y + int(7 * s))]
    triad_blob(surf, BONE, base, ow=max(1, int(1.4 * s)))
    # a small deep grey-lilac seed-glow at the pelvis (SECONDARY focal, kept dim)
    pygame.draw.circle(surf, LILAC_D, (rc_cx, base_y - int(1 * s)), int(3 * s))

    # === SIX IDENTICAL MOON-BEADS — one per hand (the even bead-string) ========
    # WHY drawn after torso, before head: the beads ride the crescent-cup so the
    # lower edge is an even bead-string smile; the head overdraws none of them.
    for i, (hx, hy, is_outer) in enumerate(hands):
        moon_disc(surf, hx, hy, disc_r, s)
        if is_outer:
            # eclipse-charm skull CAPPING the up-curved OUTER crescent-tip (above
            # the bead), so it crowns the smile's horn rather than dangling below.
            sgn = -1 if hx < rc_cx else 1
            ekx = hx + sgn * int(disc_r * 0.5)
            eky = hy - int(disc_r * 1.6)
            pygame.draw.line(surf, SILVER, (hx, hy - disc_r),
                             (ekx, eky + int(disc_r * 0.6)), max(1, int(1.4 * s)))
            eclipse_skull(surf, ekx, eky, int(disc_r * 0.78), s, lit=False)

    # === SKULL HEAD — slim, elegant, scary-cute, two-eyed + a lunar brow-mark ==
    # WHY a narrower head with high cheek-hollows: the slim brood member should
    # read graceful, not the big-domed chibi of Mukha. A vertical crescent brow-
    # mark (her lunar tilak) replaces Mukha's hot third eye with a COOL focal.
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    # tall narrow skull: pull the lower face into a slight taper for elegance
    chin = [(head_c[0] - int(hr * 0.52), head_c[1] + int(hr * 0.30)),
            (head_c[0] + int(hr * 0.52), head_c[1] + int(hr * 0.30)),
            (head_c[0] + int(hr * 0.30), head_c[1] + int(hr * 0.96)),
            (head_c[0] - int(hr * 0.30), head_c[1] + int(hr * 0.96))]
    triad_blob(surf, BONE, chin, ow=max(1, int(1.4 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.62), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.22))
    # two big eye sockets — cool lilac pin, scary-CUTE, kept dimmer than the brow
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.40)
        ey = head_c[1] + int(hr * 0.18)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, LILAC_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
        pygame.draw.circle(surf, EYE_GLOW, (ex, ey - int(hr * 0.04)), int(hr * 0.07))
    # LUNAR BROW-MARK — a small UP-opening crescent tilak, the brightest cool focal.
    # WHY a horizontal up-cupping crescent (not the vertical sliver that read as a
    # forehead crack): it echoes the wide low cup below + the rising horn above in
    # miniature, and is unmistakably COOL (anti-Mukha hot magenta) at 32px on both
    # biomes. A small ink seat under it keeps it from fusing with the cranium fill.
    bmx, bmy = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.circle(surf, INK, (bmx, bmy + int(hr * 0.04)), int(hr * 0.22))
    crescent(surf, bmx, bmy, int(hr * 0.26), EYE_GLOW, LILAC_D, EYE_BR,
             ow=0, bite=0.5, ang=-90.0)
    pygame.draw.circle(surf, EYE_BR, (bmx - int(hr * 0.05), bmy + int(hr * 0.04)),
                       max(1, int(hr * 0.06)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.12), head_c[1] + int(hr * 0.32)),
                         (head_c[0] + int(hr * 0.12), head_c[1] + int(hr * 0.32)),
                         (head_c[0], head_c[1] + int(hr * 0.58))])
    # a small calm tooth row (slim + serene, less wrathful than Mukha's bared grin)
    my = head_c[1] + int(hr * 0.74)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.40), my),
                     (head_c[0] + int(hr * 0.40), my), max(1, int(1.8 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.08)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.11)), max(1, int(1 * s)))

    # === SKULL-CROWN / TIARA with TINY SKULLS (preserved DNA) =================
    # WHY a low crescent-tiara band of skulls seated on the brow, UNDER the rising
    # horn: keeps the skull-crown DNA while the horn owns the upper silhouette. A
    # shallow ~64° arc of THREE skulls, centre one lit lilac.
    tiara_r = int(hr * 0.96)
    tiara_skull_r = int(hr * 0.28)
    band_pts = []
    for i in range(9):
        a = math.radians(238 + i * (64 / 8))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(5 * s))
    pygame.draw.lines(surf, SILVER, False, band_pts, int(2.4 * s))
    pygame.draw.lines(surf, SILVER_BR, False, band_pts[:5], max(1, int(1.1 * s)))
    for i in range(3):
        a = math.radians(244 + i * (52 / 2))
        sx = head_c[0] + math.cos(a) * tiara_r
        sy = head_c[1] + math.sin(a) * tiara_r
        eclipse_skull(surf, int(sx), int(sy), tiara_skull_r, s, lit=(i == 1))

    # WHY a TRUE negative-space groove (erased, not inked) carved AFTER the crown:
    # an ink stroke is dark-on-dark on the night sky and can't separate crown from
    # horn. Punching the alpha to ZERO in an arc that rides ABOVE the skull-tops lets
    # the actual background show THROUGH the slot, so the crown reads as a distinct
    # BAND under the horn at 32px on both biomes. The horn (drawn first, behind) keeps
    # its mass above the slot; the skulls keep theirs below it.
    groove_w = max(int(3.2 * s), 4)
    groove_r = tiara_r + tiara_skull_r * 1.02
    erase = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    gpts = []
    for i in range(33):
        a = math.radians(234 + i * (72 / 32))
        gpts.append((head_c[0] + math.cos(a) * groove_r,
                     head_c[1] + math.sin(a) * groove_r))
    pygame.draw.lines(erase, (0, 0, 0, 255), False, gpts, groove_w)
    surf.blit(erase, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


# ── the moon-gnomon staff → pillar mirror ──────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The moon-gnomon staff IS the pillar: an upright bone gnomon casting a banded
    shadow-scale, hung with moon-phase disc pendants = the tileable shaft; the cap
    is a SINGLE rising crescent-horn cradling a lit full-moon at the gap — the
    creature's own lunar language, bottom-rooted and on-axis.

    `cap` names the END that faces the GAP."""
    shaft_w = int(11 * s)
    disc_r = int(6 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(22 * s)
    cap_room = int(36 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    idx = 0
    while y <= b1:
        # a bone gnomon-band segment with a hard shadow-scale groove (the tile)
        bw = shaft_w
        band = [(cx - bw, y - int(8 * s)),
                (cx + bw, y - int(8 * s)),
                (cx + bw, y + int(8 * s)),
                (cx - bw, y + int(8 * s))]
        triad_blob(surf, BONE, band,
                   core_pts=[(cx, y - int(7 * s)), (cx + bw, y - int(7 * s)),
                             (cx + bw, y + int(7 * s)), (cx, y + int(7 * s))],
                   sheen_pts=[(cx - bw, y - int(7 * s)), (cx - int(bw * 0.3), y - int(7 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        # the shadow-scale tick marks (the gnomon casts hour-lines)
        pygame.draw.line(surf, BONE_DD, (cx - bw, y), (cx + bw, y), max(1, int(1.6 * s)))
        pygame.draw.line(surf, LILAC_D, (cx - int(bw * 0.5), y), (cx + int(bw * 0.5), y),
                         max(1, int(1.0 * s)))
        # a moon-phase disc pendant hung off alternating sides
        side = -1 if (idx % 2 == 0) else 1
        rx = cx + side * (bw + int(8 * s))
        ry = y + int(2 * s)
        pygame.draw.line(surf, SILVER, (cx + side * bw, y), (rx, ry), max(1, int(1.4 * s)))
        moon_disc(surf, rx, ry, disc_r, s, idx % 6)
        idx += 1
        y += band_pitch

    # === gap-edge cap: rising crescent-horn cradling a lit full-moon ==========
    # WHY a single horn + full-moon at the gap: it mirrors the creature's own
    # rising-horn tell in miniature and glows toward the gap, on-axis and never
    # wider than the shaft's pendant span.
    cap_y = (bot - int(22 * s)) if cap == "bottom" else (top + int(22 * s))
    grow = +1 if cap == "bottom" else -1
    horn_r = int(15 * s)
    horn_ang = 90.0 if grow > 0 else -90.0   # horn opens toward the gap
    crescent(surf, cx, cap_y, horn_r + max(1, int(2 * s)), INK, INK, INK,
             ow=0, bite=0.5, ang=horn_ang)
    crescent(surf, cx, cap_y, horn_r, SILVER, LILAC_D, SILVER_BR,
             ow=0, bite=0.5, ang=horn_ang)
    # a thin silver collar where the horn meets the shaft
    collar_y = cap_y - grow * int(horn_r + int(3 * s))
    pygame.draw.rect(surf, INK, (cx - int(9 * s), collar_y - int(3 * s), int(18 * s), int(7 * s)))
    pygame.draw.rect(surf, SILVER, (cx - int(8 * s), collar_y - int(2 * s), int(16 * s), int(5 * s)))
    pygame.draw.rect(surf, SILVER_BR, (cx - int(8 * s), collar_y - int(2 * s), int(16 * s), int(2 * s)))
    # the lit FULL-MOON cradled in the horn (the gap glow)
    full_y = cap_y + grow * int(horn_r * 0.30)
    triad_circle(surf, LILAC_BR, (cx, full_y), int(6 * s), ow=max(1, int(1.2 * s)), core=False)
    pygame.draw.circle(surf, LILAC, (cx + int(1 * s), full_y + int(1 * s)), int(4 * s))
    pygame.draw.circle(surf, SILVER_BR, (cx - int(2 * s), full_y - int(2 * s)), max(1, int(1.6 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    # WHY a 2px grown keyline (was 1px): on the pale-blue DAY sky the silver bone is
    # close in value to the sky, so a thicker outer ink ring carries the silhouette —
    # the figure now holds on day the way it already held on night.
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_chandra_mata(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 2)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def silhouette_chip(boxw, boxh, draw_cx, draw_cy, scale):
    """A blacked-out proof: render at SS, recolour every opaque pixel to flat ink.
    WHY: the brief's silhouette tell (low cupping smile under a rising horn) must
    survive as pure blackout — this is the read that distinguishes the KIND."""
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_chandra_mata(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    mask = pygame.mask.from_surface(small, 40)
    sil = mask.to_surface(setcolor=(18, 16, 22, 255), unsetcolor=(0, 0, 0, 0))
    return sil


def main():
    W, H = 1010, 860
    font_big = pygame.font.Font(FONT_PATH, 30)
    font = pygame.font.Font(FONT_PATH, 17)
    font_sm = pygame.font.Font(FONT_PATH, 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("CHANDRA-MATA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "lunar crescent-arc bone-mother  ·  KIND: wide-low-crescent CUP + rising-horn · moon-silver + grey-lilac · slim mid-tall · round 3",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(330, 470, 165, 244, 1.45)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (96, 566))
    sheet.blit(font_sm.render("SLIM mid-tall figure: single rising crescent-HORN behind the crown,", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("six arms spread WIDE into a low cupping CRESCENT (U/bowl, span ~1.7x depth),", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("tips curve UP to shoulder height + are CAPPED by eclipse-charm skulls.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, bottom-rooted gnomon ================
    pcx = 440
    top_big = pygame.Surface((140 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 70 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (140, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((140 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 70 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (140, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 86 + 250, 124, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 50, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — moon-gnomon", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("upright gnomon + shadow-scale ticks, hung with", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("phase-disc pendants = shaft; a rising crescent-", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("horn cradling a full-moon caps the gap (mirrored)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips (day + night) + silhouette proof + palette =======
    panel_x = 620
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 700))
    sheet.blit(font.render("True 32px gameplay chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((110 * SS, 116 * SS), pygame.SRCALPHA)
        draw_chandra_mata(big, 55 * SS, 62 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 116))
        return grow_outline(small, INK + (255,), 2)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 130, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 130, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 10, day_y + 18))
    sheet.blit(font_sm.render("32px on DAY sky", True, LABEL), (panel_x + 20, day_y + 154))

    night_y = day_y + 178
    vgrad(sheet, (panel_x + 20, night_y, 130, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 130, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 10, night_y + 18))
    sheet.blit(font_sm.render("32px on NIGHT sky (dark-on-dark pop)", True, LABEL_DIM), (panel_x + 20, night_y + 154))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.30 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 162
    vgrad(sheet, (px2, day_y, 52, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 52, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 52, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 52, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # === (d) BLACKED-OUT SILHOUETTE PROOF =====================================
    sil_x = px2 + 70
    sil_w = W - sil_x - 30
    pygame.draw.rect(sheet, (170, 170, 178), (sil_x, day_y, sil_w, 150))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, sil_w, 150), 1)
    sil_big = silhouette_chip(150, 150, 75, 78, 0.92)
    sheet.blit(sil_big, (sil_x + (sil_w - 150) // 2, day_y))
    sheet.blit(font_sm.render("BLACKOUT proof:", True, LABEL), (sil_x, day_y + 154))
    sheet.blit(font_sm.render("low cupping smile UNDER a rising horn", True, LABEL_DIM), (sil_x, day_y + 168))

    # small 32px silhouette too, to prove the tell at true scale
    sil_sm = silhouette_chip(56, 56, 28, 30, (32 / 150.0))
    pygame.draw.rect(sheet, (170, 170, 178), (sil_x + sil_w - 64, night_y, 64, 64))
    pygame.draw.rect(sheet, INK, (sil_x + sil_w - 64, night_y, 64, 64), 1)
    sheet.blit(sil_sm, (sil_x + sil_w - 64 + 4, night_y + 4))
    sheet.blit(font_sm.render("32px blackout", True, LABEL_DIM), (sil_x + sil_w - 92, night_y + 70))

    # === (e) PALETTE STRIP (below the night chip, full width of the panel) =====
    pal_y = night_y + 178
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, pal_y))
    swatches = [
        (BONE, "moon-silver bone"), (BONE_D, "cool-grey shade"),
        (LILAC, "grey-lilac accent"), (LILAC_D, "shadow-limb (value lo)"),
        (LILAC_BR, "lit-limb (value hi)"), (SILVER, "cold silver trim"),
        (EYE_GLOW, "lunar brow-mark"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, pal_y + 26
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 178
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 18, 18))
        pygame.draw.rect(sheet, c, (rx, ry, 16, 16))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 24, ry + 2))

    pygame.draw.rect(sheet, PANEL, (14, 810, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat triad fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen · 1px grown outline · scary-cute · procedural-only.  Accent grey-lilac, desaturated.",
        True, LABEL_DIM), (26, 823))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
