"""
Round-1 concept renderer for RAKTA-AMBU — coral-tree dendritic bone-canopy
(Mukha-Devi brood spin-off, concept #4). Headless Pygame; ELEVATED pipeline
(supersample SS=6 -> smoothscale) so the forked canopy + tip relics + tiny
encrusted skulls stay crisp at downscale. Keeps the shipped house grammar:
flat saturated fills, hard 1-2px ink keyline (28,22,26), dark-core -> flat-fill
-> top-left rim-sheen triad, 1px alpha-grown outline, chibi, scary-CUTE;
procedural-only.

WHY this is the forked-tree-canopy KIND (the ONLY ORGANIC silhouette in the
brood): Rakta-Ambu goes MID-TALL -> MONUMENTAL by spreading WIDE, not tall.
EIGHT bone arms leave a low shoulder line and immediately FORK — each splits
into two, and those two split again — into a knobbly spreading coral
tree-crown. So her blackout is NOT discrete radiating limbs (that is Mukha's
open starburst) but one organic branching CANOPY: a dendritic blob whose
outer edge is lumpy with coral-polyp cups. Recursion is hard-capped at TWO
fork levels so at 32px the OUTER canopy silhouette carries the read, never
interior tracery turning to noise.

WHY briny-indigo bone with a small coral-pink HEART, not white: the cross-set
pin bans Yurei cyan and Mukha hot magenta. The bone mass is pushed clearly
toward briny INDIGO-blue (dominant), and the single warm focal is a DULL
SALMON-CORAL heart-glow — a small warm core in a cold body, so it reads
unmistakably as a deep-reef thing, never a bright magenta deity.

WHY the coral-reef bone-trunk IS the pillar: a knobbly branching bone-trunk
rooted at the bottom (the root system roots it -> no taper risk) hung with
coral-polyp cups and conch relics as the tileable shaft; the gap-cap is a
small forked coral-frond crown with a glowing coral heart at the fork — the
creature's own dendritic language, on-axis.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Briny INDIGO-blue is the dominant bone mass (anti-Yurei: darker, never cyan).
# The single warm focal is a DULL SALMON-CORAL heart (anti-Mukha: never hot
# magenta) -- a small warm core, indigo dominant.
BONE      = ( 54,  86, 140)   # briny indigo-blue bone (the dominant fill)
BONE_D    = ( 36,  58,  98)   # deep-indigo dark-core / shade
BONE_DD   = ( 22,  38,  70)   # deepest indigo hollow (sockets, fork grooves)
BONE_SH   = (118, 152, 202)   # cool indigo top-left rim-sheen
CORAL     = (214, 118, 110)   # dull salmon-coral HEART glow (small warm focal -- RESERVED for the face eyes + mouth + chest heart)
CORAL_BR  = (244, 168, 156)   # lit coral inner / sheen (face/heart only)
CORAL_D   = (150,  72,  72)   # deep coral shade
# WHY a separate, DEMOTED canopy-polyp coral: the ~8 outer polyp dots were
# reading at the same value/sat as the face eye-cores, so the face lost the
# focal fight. The polyp coral is pulled one value step DOWN and desaturated
# toward indigo-shade so the canopy edge stays a quiet warm TEXTURE while peak
# coral chroma is reserved for the two face eyes + mouth + chest heart.
POLYP     = (150,  98, 104)   # demoted polyp coral (toward indigo-shade; quiet)
POLYP_BR  = (176, 122, 124)   # polyp inner (still well below CORAL_BR)
CONCH     = (220, 196, 170)   # pale conch-relic bone (a warm-neutral relic note)
CONCH_BR  = (244, 230, 210)
CONCH_D   = (158, 132, 108)
SKULL     = (168, 170, 162)   # encrusted skull -- bone-GREY, not pure white (crusted texture, not a necklace)
SKULL_D   = (108, 112, 110)   # skull shade (sunk into the dark fork crotches)
SKULL_BR  = (216, 218, 210)   # only the crown-center skull is lifted near-white
INK       = ( 28,  22,  26)   # hard ink keyline
HEART     = (214, 118, 110)   # heart-glow (same coral so it reads as her warm core)
HEART_BR  = (250, 196, 178)

BG        = ( 96,  92, 100)   # neutral grey review backdrop
PANEL     = ( 74,  72,  84)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 236, 240)
LABEL_DIM = (196, 190, 202)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# -- outline grown from the alpha mask (the house keyline) --------------------
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


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2,
               sheen_amt=0.4):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline.
    `sheen_amt` lets the canopy boughs carry a dimmer rim than the face/relics so
    the coral eye-face stays the single brightest focal point."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), sheen_amt), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob -- dark core bottom-right, sheen top-left."""
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


def tapered_limb(surf, p, q, w0, w1, color, ow, sheen_amt=0.28):
    """A knobbly bone branch segment that TAPERS from w0 (base) to w1 (tip).
    WHY tapered, not parallel-sided: a coral branch thins as it forks, so the
    canopy edge reads organic/dendritic instead of a bundle of even sticks.
    `sheen_amt` defaults a value-step DOWN from the face/relic sheen so the boughs
    never out-shine the coral eye-face (the single focal)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy / L, dx / L
    quad = [(p[0] + nx * w0 / 2, p[1] + ny * w0 / 2),
            (q[0] + nx * w1 / 2, q[1] + ny * w1 / 2),
            (q[0] - nx * w1 / 2, q[1] - ny * w1 / 2),
            (p[0] - nx * w0 / 2, p[1] - ny * w0 / 2)]
    # top-left edge catches the sheen
    sheen = [(p[0] + nx * w0 / 2, p[1] + ny * w0 / 2),
             (q[0] + nx * w1 / 2, q[1] + ny * w1 / 2),
             (q[0] + nx * w1 * 0.18, q[1] + ny * w1 * 0.18),
             (p[0] + nx * w0 * 0.18, p[1] + ny * w0 * 0.18)]
    triad_blob(surf, color, quad, sheen_pts=sheen, ow=ow, sheen_amt=sheen_amt)


# -- a tiny encrusted skull (the surviving arm-end-skull DNA) ------------------
def tiny_skull(surf, cx, cy, r, s, lit=False, crown=False, sunk=False):
    """A skull ENCRUSTED into a fork crotch -- death-as-growth. WHY bone-GREY,
    not pure white: it must read as crusted dead bone fused INTO the dark indigo
    branches (a texture), never a clean white bead on a necklace. Only the
    crown-center skull (`crown`) is lifted near-white as the single bright relic;
    the rest sit dull-grey and sunk so they don't pile into a horizontal belt.
    `sunk` pushes the body ONE value step further toward indigo-shade so the
    crotch-skulls crust into shadow and never out-value the face.
    A ring of indigo hollow under the skull seats it deeper into the dark fork."""
    if crown:
        body = SKULL_BR
    elif sunk:
        body = lerp(SKULL_D, BONE_DD, 0.30)   # one step deeper into the indigo crotch-shadow
    else:
        body = SKULL
    # seat it: a darker indigo crotch-shadow behind/below so the skull sinks in
    pygame.draw.circle(surf, BONE_DD, (cx, cy + max(1, int(r * 0.28))), int(r * 1.15))
    triad_circle(surf, body, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.45)),
           (cx + int(r * 0.5), cy + int(r * 0.45)),
           (cx + int(r * 0.30), cy + int(r * 0.92)),
           (cx - int(r * 0.30), cy + int(r * 0.92))]
    triad_blob(surf, body, jaw, ow=max(1, int(1.0 * s)))
    for ex in (cx - int(r * 0.36), cx + int(r * 0.36)):
        pygame.draw.circle(surf, INK, (ex, cy), max(1, int(r * 0.26)))
        if lit or crown:
            pygame.draw.circle(surf, CORAL_BR, (ex, cy), max(1, int(r * 0.12)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.40)), max(1, int(r * 0.12)))


# -- the tip ornaments: coral-polyp cups + conch relics ------------------------
def polyp_cup(surf, cx, cy, r, s, ang):
    """A coral-POLYP cup at a canopy tip -- a knobbly indigo cup cradling a small
    DEMOTED-coral dot. WHY the coral here is dull POLYP coral (not CORAL) and the
    core is shrunk ~20%: the canopy edge must twinkle as a quiet warm TEXTURE so
    the FACE (eyes + mouth + chest heart, the only peak-chroma coral) stays the
    single warm focal at 32px -- never a competing fringe of equal-bright dots."""
    triad_circle(surf, BONE, (cx, cy), int(r * 1.0), ow=max(1, int(1.3 * s)), core=False)
    # the open cup mouth (a dark crescent so it reads as a polyp cup, not a knob)
    pygame.draw.arc(surf, BONE_DD,
                    (cx - int(r * 0.78), cy - int(r * 0.86), int(r * 1.56), int(r * 1.5)),
                    math.radians(200), math.radians(340), max(2, int(2.0 * s)))
    # three tiny demoted-coral tentacle-nubs around the rim
    for k in (-1, 0, 1):
        a = math.radians(-90 + k * 34)
        tx = cx + math.cos(a) * r * 0.7
        ty = cy + math.sin(a) * r * 0.7 - int(r * 0.1)
        pygame.draw.circle(surf, INK, (int(tx), int(ty)), max(1, int(r * 0.20)))
        pygame.draw.circle(surf, POLYP, (int(tx), int(ty)), max(1, int(r * 0.13)))
    # the demoted-coral dot in the cup -- shrunk ~20% vs r2 and a value step down
    pygame.draw.circle(surf, POLYP, (cx, cy - int(r * 0.06)), max(1, int(r * 0.29)))
    pygame.draw.circle(surf, POLYP_BR, (cx - int(r * 0.10), cy - int(r * 0.18)),
                       max(1, int(r * 0.13)))


def conch_relic(surf, cx, cy, r, s):
    """A spiralled conch relic at a canopy tip (a held relic, the surviving
    arm-end-ornament DNA). WHY pale conch-bone + a coral aperture: a warm-neutral
    relic mass that reads as a distinct ornament chunk vs the polyp cups, with a
    small coral mouth tying it to the heart palette."""
    body = [(cx - int(r * 0.9), cy + int(r * 0.2)),
            (cx - int(r * 0.3), cy - int(r * 0.95)),
            (cx + int(r * 0.5), cy - int(r * 0.6)),
            (cx + int(r * 0.95), cy + int(r * 0.35)),
            (cx + int(r * 0.3), cy + int(r * 0.95)),
            (cx - int(r * 0.55), cy + int(r * 0.75))]
    triad_blob(surf, CONCH, body,
               core_pts=[(cx, cy - int(r * 0.2)), (cx + int(r * 0.7), cy + int(r * 0.1)),
                         (cx + int(r * 0.2), cy + int(r * 0.7)), (cx - int(r * 0.1), cy + int(r * 0.2))],
               sheen_pts=[(cx - int(r * 0.3), cy - int(r * 0.85)),
                          (cx + int(r * 0.2), cy - int(r * 0.5)),
                          (cx - int(r * 0.1), cy - int(r * 0.1)),
                          (cx - int(r * 0.6), cy - int(r * 0.1))],
               ow=max(1, int(1.3 * s)))
    # spiral whorl grooves
    pygame.draw.arc(surf, CONCH_D, (cx - int(r * 0.55), cy - int(r * 0.5),
                    int(r * 1.0), int(r * 1.0)), math.radians(20), math.radians(300), max(1, int(1.6 * s)))
    # demoted-coral aperture mouth at the lip (a canopy ornament -> quiet, like the polyp cups)
    pygame.draw.circle(surf, POLYP, (cx + int(r * 0.45), cy + int(r * 0.45)), max(1, int(r * 0.22)))
    pygame.draw.circle(surf, POLYP_BR, (cx + int(r * 0.4), cy + int(r * 0.38)), max(1, int(r * 0.10)))


# -- the FORKED dendritic canopy (the KIND tell) -------------------------------
def draw_canopy(surf, ox, oy, s, span, levels=2):
    """A low trunk-shoulder throws up a few thick boughs that each FORK twice into
    a knobbly, spreading coral tree-crown. WHY this is a TREE and not a fan:
      - each bough TAPERS thick-base -> thin-tip and carries mid-knuckle knobs, so
        no segment reads as a clean straight rod (Mukha's spokes);
      - the first-segment lengths are STAGGERED per bough, so the level-1 forks sit
        at DIFFERENT radii (uniform spoke length is exactly what makes a fan);
      - recursion is hard-capped at TWO fork levels (the 32px rule) so the OUTER
        canopy edge carries the read, never interior tracery;
      - the outermost boughs are SHORTENED and the outer tips fattened+clustered so
        the crown DOMES and CLOSES at the top -> WIDTH is mass (monumental-by-
        width), not ray length.
    Returns canopy tip centres and the lower fork-crotch centres for skull-crust."""
    tips = []        # (x, y, ang, tip_w) -- canopy edge ornaments
    lower_forks = [] # (x, y) -- dark Y-junctions to sink tiny skulls into

    base_w = int(23 * s)
    # FEWER, THICKER boughs than r1's eight even spokes; aimed across the upper
    # hemisphere, leaning outward. Symmetric pairs but each pair at its OWN radius.
    # (angle, length_factor, base_width_factor) -- lengths/widths deliberately
    # uneven so the level-1 junctions stagger across the crown.
    boughs = [
        (-134, 0.66, 1.06),   # low outer L -- longest, reaches widest (lifted off horizontal)
        ( -44, 0.66, 1.06),   # low outer R
        (-116, 0.56, 1.00),   # mid L -- a notch shorter, fork sits lower-in
        ( -64, 0.62, 1.00),   # mid R -- staggered vs its mirror on purpose
        ( -98, 0.48, 0.92),   # near-top L -- short, helps dome/close the crown
        ( -80, 0.44, 0.92),   # near-top R -- shortest, fills the apex
    ]

    def grow(px, py, ang, length, width, depth, is_outer=False):
        # split this bough into a base half + a knobbly knuckle + a tip half, so
        # the limb is never one clean rod -- the dendritic, organic read.
        mx = px + math.cos(math.radians(ang)) * length * 0.5
        my = py + math.sin(math.radians(ang)) * length * 0.5
        knob_w = width * (0.86 + 0.10 * math.sin(ang + depth))   # along-branch width wobble
        ex = px + math.cos(math.radians(ang)) * length
        ey = py + math.sin(math.radians(ang)) * length
        tip_w = width * 0.60
        tapered_limb(surf, (px, py), (mx, my), width, knob_w, BONE,
                     ow=max(1, int(width * 0.13)))
        triad_circle(surf, BONE, (int(mx), int(my)), int(knob_w * 0.56),
                     ow=max(1, int(1.0 * s)), core=False)   # the mid-branch knuckle
        tapered_limb(surf, (mx, my), (ex, ey), knob_w, tip_w, BONE,
                     ow=max(1, int(knob_w * 0.13)))
        triad_circle(surf, BONE, (int(ex), int(ey)), int(tip_w * 0.62),
                     ow=max(1, int(1.0 * s)), core=False)    # the fork joint
        # WHY the LOW knuckle of the OUTER boughs is a skull-crotch candidate: it
        # is the lowest + most lateral dark Y-junction available, so a skull seated
        # there frames the head from the side/below instead of stacking above it.
        if depth == 1 and is_outer:
            lower_forks.append((int(mx), int(my)))
        if depth >= levels:
            tips.append((int(ex), int(ey), ang, tip_w))
            return
        if depth == 1:
            lower_forks.append((int(ex), int(ey)))
        # FORK INTO TWO -- the level-1 split is WIDE so the Y is unmistakable.
        split = 38 - depth * 8
        outward = 1 if ang <= -90 else -1
        for d in (-split, split):
            child_ang = ang + d + outward * 7
            # outer child grows more, inner child stays short -> clusters tips
            child_len = length * (0.66 if d * outward > 0 else 0.58)
            grow(ex, ey, child_ang, child_len, tip_w, depth + 1)

    arm_len = span * 0.5
    # draw outermost/lowest first so the upper, clustering boughs overlap on top
    for ang, lf, wf in sorted(boughs, key=lambda b: -abs(b[0] - (-90))):
        sx = ox + (1 if ang > -90 else -1) * int(7 * s)
        is_outer = abs(ang - (-90)) >= 40   # the two long low-outer boughs
        grow(sx, oy, ang, arm_len * lf, int(base_w * wf), 1, is_outer=is_outer)

    return tips, lower_forks


# -- the coral-tree bone-canopy creature ---------------------------------------
def draw_rakta_ambu(surf, cx, cy, s):
    """Coral-reef death-mother: a chibi indigo-bone skull-trunk crowned by a
    WIDE forked dendritic canopy that spreads sideways (monumental-by-width).
    Tips bear polyp cups + conch relics; tiny pale skulls are encrusted into
    the lower forks; a low skull-crown + a dull-coral heart keep the FACE and
    warm focal reading inside the cold canopy. `s` = unit scale (~150-unit fig)."""

    head_c = (cx, cy - int(14 * s))
    hr = int(28 * s)

    # === FORKED CANOPY (drawn first -> branches sit BEHIND the head) ==========
    # WHY origin at a LOW shoulder line + a WIDE span: the canopy must SPREAD,
    # bracketing the head sideways, leaving open sky directly above the crown so
    # the skull-tiara reads -- and so the blackout is wider than tall.
    canopy_span = int(150 * s)
    tips, lower_forks = draw_canopy(surf, head_c[0], head_c[1] + int(hr * 0.55),
                                    s, canopy_span, levels=2)

    # === DOMED CROWN MASS -- fatten + fuse the UPPER tips so the top CLOSES ====
    # WHY a band of overlapping lumpy bone blobs across the upper tips: it welds
    # the cluster of short upper boughs into one domed crown so the blackout reads
    # as a knobbly canopy whose WIDTH is mass, not a ring of separate ray-ends.
    upper = sorted([t for t in tips if t[1] <= head_c[1] - int(hr * 0.4)],
                   key=lambda t: t[0])
    for (tx, ty, ang, tw) in upper:
        triad_circle(surf, BONE, (tx, ty), int(tw * 1.15),
                     ow=max(1, int(1.2 * s)), core=False)
    # a few extra fused lumps bridging adjacent upper tips -> a continuous dome
    for i in range(len(upper) - 1):
        ax, ay = upper[i][0], upper[i][1]
        bx, by = upper[i + 1][0], upper[i + 1][1]
        mx, my = (ax + bx) // 2, (ay + by) // 2 - int(2 * s)
        triad_circle(surf, BONE, (mx, my), int(7 * s),
                     ow=max(1, int(1.1 * s)), core=False)

    # === TIP ORNAMENTS -- polyp cups + conch relics around the canopy edge ====
    # WHY alternating by horizontal position (not draw order): a regular cup /
    # conch rhythm reads along the lumpy edge so it is clearly "ornamented
    # canopy," and the warm coral dots twinkle along the rim without a fringe.
    # WHY jittered radius + a small lateral nudge off the strict bilateral mirror:
    # a crown of identically-stamped cups reads MANUFACTURED. Jitter diameter
    # +/-15% and shove 2-3 cups a few px off their mirror twin so the canopy edge
    # feels GROWN, not stamped. (deterministic per-index so the sheet is stable.)
    tips_sorted = sorted(tips, key=lambda t: t[0])
    orn_r = int(7 * s)
    for i, (tx, ty, ang, tw) in enumerate(tips_sorted):
        jr = orn_r * (1.0 + 0.15 * math.sin(i * 2.3 + 0.7))   # +/-15% diameter jitter
        # nudge a couple off the strict mirror (every 3rd tip drifts laterally)
        nudge_x = int(2.4 * s * math.sin(i * 1.7)) if (i % 3 == 0) else 0
        nudge_y = int(1.8 * s * math.cos(i * 1.9))
        if i % 3 == 1:
            conch_relic(surf, tx + nudge_x, ty - int(jr * 0.2) + nudge_y, int(jr), s)
        else:
            polyp_cup(surf, tx + nudge_x, ty + nudge_y, int(jr), s, ang)

    # === LOWER BODY -- a wide squat reef-foot (mass low, spreading) ===========
    # WHY ~8% wider base than r2: a heavier foot anchors the monumental-by-width
    # read so the wide canopy sits on a wide root, not a stalk.
    base_y = cy + int(40 * s)
    base = [(cx - int(41 * s), base_y - int(6 * s)),
            (cx - int(28 * s), base_y - int(17 * s)),
            (cx + int(28 * s), base_y - int(17 * s)),
            (cx + int(41 * s), base_y - int(6 * s)),
            (cx + int(33 * s), base_y + int(13 * s)),
            (cx - int(33 * s), base_y + int(13 * s))]
    triad_blob(surf, BONE, base,
               core_pts=[(cx, base_y - int(15 * s)), (cx + int(35 * s), base_y - int(6 * s)),
                         (cx + int(26 * s), base_y + int(11 * s)), (cx, base_y + int(8 * s))],
               ow=max(1, int(1.6 * s)))
    # knobbly reef-foot bumps (organic, not petals)
    for k in range(-3, 4):
        px = cx + int(k * 11 * s)
        pygame.draw.circle(surf, BONE_DD, (px, base_y + int(11 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surf, BONE, (px - int(1 * s), base_y + int(10 * s)), max(1, int(2 * s)))
    # a hair of COOL rim-light along the trunk-base bottom edge -- WHY: at night
    # the dark-indigo foot dissolves into the dark ground; a thin cool catch-light
    # keeps the silhouette's base reading without warming the cold palette.
    rim = lerp(BONE_SH, (236, 244, 255), 0.25)
    pygame.draw.lines(surf, rim, False,
                      [(cx - int(37 * s), base_y - int(2 * s)),
                       (cx - int(30 * s), base_y + int(9 * s)),
                       (cx + int(30 * s), base_y + int(9 * s)),
                       (cx + int(37 * s), base_y - int(2 * s))],
                      max(1, int(1.4 * s)))

    # === TORSO -- a short coral-rib trunk (squat; head + canopy hold mass) ====
    rc_cx, rc_cy = cx, cy + int(14 * s)
    rc_w, rc_h = int(30 * s), int(26 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(4 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(2 * s))],
               ow=max(1, int(1.8 * s)))
    # coral-rib bands (knobbly, reef-textured)
    for i in range(2):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(9 * s)
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(4 * s)), max(1, int(2 * s)))

    # === CORAL HEART -- the single warm focal, set in the chest =============
    # WHY a dull-coral heart-glow on the sternum, kept WARMER+SMALLER than any
    # canopy dot: indigo dominant, this is the small warm core that says "living
    # reef" -- a dull salmon-coral, demonstrably NOT Mukha hot magenta.
    hxy = (rc_cx, rc_cy - int(1 * s))
    pygame.draw.circle(surf, INK, hxy, int(7 * s))
    pygame.draw.circle(surf, CORAL_D, hxy, int(6 * s))
    pygame.draw.circle(surf, CORAL, hxy, int(4 * s))
    pygame.draw.circle(surf, CORAL_BR, (hxy[0] - int(1 * s), hxy[1] - int(1 * s)), max(1, int(2 * s)))

    # === ENCRUSTED SKULLS sunk DEEP into the LOWER / OUTER fork crotches ======
    # WHY scored to the LOWEST + most LATERAL Y-junctions, ONE per crotch, sunk
    # one value step further into shadow than r2: in r2 they migrated into a
    # centered row ABOVE the face and competed with it. They must instead read as
    # crusted death-as-growth nodes wedged into the dark outer/lower crotches that
    # FRAME the head from the sides + below -- never a horizontal belt. The single
    # bright relic stays reserved for the crown-center skull alone; everything here
    # is dull-grey, sunk, and below/lateral to the face so the airspace directly
    # above the crown stays clear.
    # rank by LOW (largest y -> nearest/under the head) + LATERAL (far from the
    # centre column); hard-penalise crotches in the narrow column above the face
    # so none stack into a centred row, and penalise high crotches so the skulls
    # frame the head from the sides + below, never as a belt over the crown.
    cand = list(lower_forks)
    def crotch_score(f):
        lateral = abs(f[0] - head_c[0])
        dy = f[1] - head_c[1]                       # less negative == lower == better
        central_penalty = -200 if lateral < hr * 0.45 else 0
        return lateral * 1.0 + dy * 1.3 + central_penalty
    cand.sort(key=crotch_score, reverse=True)
    # one per crotch: drop any pick too close to one already chosen (no clustering)
    fl = []
    for f in cand:
        if all((abs(f[0] - g[0]) + abs(f[1] - g[1])) > hr * 0.7 for g in fl):
            fl.append(f)
        if len(fl) >= 4:
            break
    skull_r = int(4.8 * s)
    for (fx, fy) in fl:
        # sink it deeper INTO the crotch: pushed below the joint + a stronger
        # indigo crotch-shadow ring so it crusts into shadow, never a bright bead.
        pygame.draw.circle(surf, BONE_DD, (fx, fy + int(5 * s)), int(skull_r * 1.5))
        tiny_skull(surf, fx, fy + int(5 * s), skull_r, s, lit=False, sunk=True)

    # === SKULL HEAD -- chibi, scary-cute, coral-eyed (the framed FACE) ========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.24))
    # two big sockets -- dark hollows with small deep-coral pins (scary-CUTE),
    # kept a notch dimmer than the chest heart so the heart stays warm focal.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.40)
        ey = head_c[1] + int(hr * 0.06)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.26))
        pygame.draw.circle(surf, CORAL, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.13))
        pygame.draw.circle(surf, CORAL_BR, (ex, ey - int(1 * s)), max(1, int(hr * 0.06)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.34)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.34)),
                         (head_c[0], head_c[1] + int(hr * 0.58))])
    # grinning tooth row (cute, not gory) -- a thin coral inner-mouth behind the
    # teeth so the MOUTH joins the eyes as reserved peak-coral; with the canopy
    # polyps demoted, the face now owns all three warm beats (two eyes + mouth).
    my = head_c[1] + int(hr * 0.74)
    pygame.draw.ellipse(surf, CORAL_D,
                        (head_c[0] - int(hr * 0.46), my - int(hr * 0.12),
                         int(hr * 0.92), int(hr * 0.26)))
    pygame.draw.ellipse(surf, CORAL,
                        (head_c[0] - int(hr * 0.40), my - int(hr * 0.07),
                         int(hr * 0.80), int(hr * 0.16)))
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.46), my),
                     (head_c[0] + int(hr * 0.46), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.14), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.14), my + int(hr * 0.12)), max(1, int(1 * s)))

    # === LOW SKULL-CROWN -- a SINGLE bright center skull (the crown focal) =====
    # WHY only ONE skull now, dead-centre on the crown: in r2 a band of three sat
    # as a row above the face. The side relics moved DOWN into the lower/outer
    # crotches (above), so the crown keeps just the single brightest skull -- the
    # one bright relic in the figure, echoing the chest heart -- with a short,
    # dim bone tiara-band that frames it WITHOUT throwing a horizontal belt.
    tiara_r = int(hr * 0.98)
    band_pts = []
    for i in range(7):
        a = math.radians(250 + i * (40 / 6))   # a SHORTER, shallower band (no wide belt)
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    # a dim bone-shade band (no coral chroma here -> peak coral stays on the face)
    pygame.draw.lines(surf, INK, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, BONE_SH, False, band_pts, int(1 * s))
    # the single CENTER crown skull -- the lone bright relic
    a = math.radians(270)
    sx = head_c[0] + math.cos(a) * tiara_r
    sy = head_c[1] + math.sin(a) * tiara_r
    tiny_skull(surf, int(sx), int(sy), int(hr * 0.28), s, crown=True)


# -- the coral-reef bone-trunk -> pillar mirror --------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The coral-reef bone-TRUNK is the pillar: a knobbly branching bone-trunk
    hung with coral-polyp cups + conch relics = the tileable shaft; the gap-cap
    is a small FORKED coral-frond crown with a glowing coral heart at the fork --
    the creature's own dendritic language, on-axis. Bottom-rooted (the root
    system roots it, so there is no taper risk).

    `cap` names the END that faces the GAP."""
    trunk_w = int(15 * s)
    relic_r = int(6 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(24 * s)
    cap_room = int(38 * s)
    root_room = int(20 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
        root_y = bot
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
        root_y = top

    # === knobbly branching bone-trunk + relic side-branches ===================
    y = b0
    idx = 0
    while y <= b1:
        bw = trunk_w + int(math.sin(idx * 1.3) * 2 * s)  # knobbly width wobble
        band = [(cx - bw, y - int(9 * s)),
                (cx + bw, y - int(9 * s)),
                (cx + bw, y + int(9 * s)),
                (cx - bw, y + int(9 * s))]
        triad_blob(surf, BONE, band,
                   core_pts=[(cx, y - int(8 * s)), (cx + bw, y - int(8 * s)),
                             (cx + bw, y + int(8 * s)), (cx, y + int(8 * s))],
                   sheen_pts=[(cx - bw, y - int(8 * s)), (cx - int(bw * 0.3), y - int(8 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        # a forked node groove (so the shaft reads coral-knobbly, not a column)
        pygame.draw.arc(surf, BONE_DD, (cx - bw, y - int(8 * s), bw * 2, int(16 * s)),
                        math.radians(200), math.radians(340), max(1, int(1.6 * s)))
        # a relic side-branch off alternating sides (cup / conch alternation)
        side = -1 if (idx % 2 == 0) else 1
        bx = cx + side * (bw + int(2 * s))
        # the side-branch itself FORKS into a small Y before its relic -- WHY: it
        # echoes the canopy's dendritic split so the shaft reads as branching
        # bone-trunk, not a plain post with pendants.
        jx = cx + side * (bw + int(7 * s))
        jy = y - int(3 * s)
        # WHY fatter fork-knobs than r2: at the 0.32x pillar strip the 2-2.4px
        # dendritic knobs smeared into the post and the shaft read as a plain
        # column. Fattening the fork-joint + stub knobs keeps the branching
        # bone-trunk legible at gameplay scale.
        tapered_limb(surf, (bx, y), (jx, jy), int(6 * s), int(4 * s), BONE, ow=max(1, int(1.0 * s)))
        triad_circle(surf, BONE, (jx, jy), int(3.4 * s), ow=max(1, int(0.9 * s)), core=False)
        rx = cx + side * (bw + int(13 * s))
        ry = y - int(8 * s)
        # the relic-bearing fork-arm + a short barren stub-fork (the staggered knob)
        tapered_limb(surf, (jx, jy), (rx, ry), int(4 * s), int(3 * s), BONE, ow=max(1, int(0.9 * s)))
        sbx = cx + side * (bw + int(11 * s))
        sby = y + int(5 * s)
        tapered_limb(surf, (jx, jy), (sbx, sby), int(4 * s), int(3 * s), BONE, ow=max(1, int(0.9 * s)))
        triad_circle(surf, BONE, (sbx, sby), int(3 * s), ow=max(1, int(0.8 * s)), core=False)
        if idx % 2 == 0:
            polyp_cup(surf, rx, ry, relic_r, s, math.radians(-90))
        else:
            conch_relic(surf, rx, ry, relic_r, s)
        # tiny encrusted skull on a lower-third joint
        if (idx % 3 == 2):
            tiny_skull(surf, cx, y + int(7 * s), int(4 * s), s, lit=False)
        idx += 1
        y += band_pitch

    # === bottom root flare (the trunk roots it) ==============================
    rgrow = +1 if cap == "bottom" else -1
    ry0 = root_y - rgrow * int(2 * s)
    for d in (-1, 0, 1):
        rxt = cx + d * int(16 * s)
        ryt = ry0 + rgrow * int(16 * s)
        tapered_limb(surf, (cx, ry0), (rxt, ryt), int(8 * s), int(3 * s), BONE,
                     ow=max(1, int(1.2 * s)))

    # === gap-edge cap: forked coral-frond crown + glowing coral heart ========
    cap_y = (bot - int(22 * s)) if cap == "bottom" else (top + int(22 * s))
    grow = +1 if cap == "bottom" else -1   # the fronds fork toward the gap
    # a small two-level fork-burst mirroring the canopy in miniature
    fr = int(15 * s)
    for k in (-1, 1):
        base_a = math.radians(-90 + k * 18) if grow > 0 else math.radians(90 + k * 18)
        jx = cx + math.cos(base_a) * fr * 0.6
        jy = cap_y + math.sin(base_a) * fr * 0.6
        tapered_limb(surf, (cx, cap_y), (jx, jy), int(7 * s), int(4 * s), BONE,
                     ow=max(1, int(1.2 * s)))
        for d in (-22, 22):
            ca = base_a + math.radians(d)
            tx = jx + math.cos(ca) * fr * 0.6
            ty = jy + math.sin(ca) * fr * 0.6
            tapered_limb(surf, (jx, jy), (tx, ty), int(4 * s), int(2 * s), BONE,
                         ow=max(1, int(1.0 * s)))
            polyp_cup(surf, int(tx), int(ty), int(4 * s), s, ca)
    # a thin coral collar where the fronds meet the trunk
    collar_y = cap_y - grow * int(fr + int(3 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, CORAL_D, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, CORAL, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # the glowing coral HEART at the fork hub (the gap glow)
    triad_circle(surf, BONE, (cx, cap_y), int(7 * s), ow=max(1, int(1.4 * s)), core=False)
    pygame.draw.circle(surf, CORAL_D, (cx, cap_y), int(5 * s))
    pygame.draw.circle(surf, CORAL, (cx, cap_y), int(3 * s))
    pygame.draw.circle(surf, CORAL_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(1.6 * s)))


# -- compose the review sheet --------------------------------------------------
SS = 6


def font_at(size):
    path = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
    return pygame.font.Font(path, size)


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_rakta_ambu(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def silhouette_of(boxw, boxh, draw_cx, draw_cy, scale):
    """A blacked-out silhouette proof: render, then recolour every opaque pixel
    to ink so we can judge the canopy READ as a solid organic branching blob."""
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_rakta_ambu(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    sil = pygame.Surface((boxw, boxh), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(small, 40)
    for yy in range(boxh):
        for xx in range(boxw):
            if mask.get_at((xx, yy)):
                sil.set_at((xx, yy), (18, 14, 18, 255))
    return sil


def main():
    W, H = 1040, 840
    font_big = font_at(30)
    font = font_at(17)
    font_sm = font_at(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("RAKTA-AMBU", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "coral-tree dendritic bone-canopy  ·  KIND: forked tree-canopy · mid-tall -> MONUMENTAL via WIDTH · briny-indigo + coral HEART · round 3",
        True, LABEL_DIM), (250, 26))

    # === (1) EPIC HERO ========================================================
    hero = render_creature_chip(380, 470, 190, 230, 1.55)
    sheet.blit(hero, (14, 84))
    sheet.blit(font.render("Creature — EPIC hero", True, LABEL), (120, 558))
    sheet.blit(font_sm.render("TAPERED boughs (thick base->thin tip) FORK twice at STAGGERED radii; upper tips fused into a domed crown.", True, LABEL_DIM), (14, 584))
    sheet.blit(font_sm.render("4 skulls sunk DEEP into the LOWER/OUTER fork crotches (one per crotch, framing the head) -- airspace above clears.", True, LABEL_DIM), (14, 600))
    sheet.blit(font_sm.render("Peak coral RESERVED for the face (2 eyes + mouth) + chest heart; canopy polyps DEMOTED to quiet texture.", True, LABEL_DIM), (14, 616))
    sheet.blit(font_sm.render("ONLY the single crown-CENTER skull is the bright relic; polyp cups jittered +/-15% so the crown reads GROWN.", True, LABEL_DIM), (14, 632))

    # === (2) PILLAR -- bottom-rooted, mirrored top<->bottom ===================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 80))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 80 + 250 + 92))
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 80 + 250, 134, 92))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 80 + 250 + 38))
    sheet.blit(font.render("Pillar — coral-reef trunk", True, LABEL), (pcx - 4, 680))
    sheet.blit(font_sm.render("knobbly branching bone-trunk hung with", True, LABEL_DIM), (pcx - 4, 704))
    sheet.blit(font_sm.render("cup/conch relics = shaft; root-flare bottom-", True, LABEL_DIM), (pcx - 4, 720))
    sheet.blit(font_sm.render("roots it; forked coral-frond + heart caps gap", True, LABEL_DIM), (pcx - 4, 736))

    # === (3) TRUE 32px chips on day + night sky ===============================
    panel_x = 662
    pygame.draw.rect(sheet, PANEL, (panel_x, 80, W - panel_x - 14, 300))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 14, 88))

    def chip32():
        big = pygame.Surface((118 * SS, 118 * SS), pygame.SRCALPHA)
        draw_rakta_ambu(big, 59 * SS, 64 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (118, 118))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()
    day_y = 116
    vgrad(sheet, (panel_x + 16, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 16, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 16 + 16, day_y + 16))
    sheet.blit(font_sm.render("32px DAY", True, LABEL), (panel_x + 16, day_y + 154))

    px2 = panel_x + 180
    vgrad(sheet, (px2, day_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 150, 150), 1)
    sheet.blit(chip, (px2 + 16, day_y + 16))
    sheet.blit(font_sm.render("32px NIGHT", True, LABEL_DIM), (px2, day_y + 154))

    # 32px pillar chips on both skies
    def pillar_chip32():
        big = pygame.Surface((52 * SS, 150 * SS), pygame.SRCALPHA)
        draw_pillar(big, 26 * SS, 2 * SS, 148 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (52, 150))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    pcy = day_y + 178
    vgrad(sheet, (panel_x + 16, pcy, 60, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 16, pcy, 60, 150), 1)
    sheet.blit(pc, (panel_x + 16 + 4, pcy))
    vgrad(sheet, (panel_x + 86, pcy, 60, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 86, pcy, 60, 150), 1)
    sheet.blit(pc, (panel_x + 86 + 4, pcy))
    sheet.blit(font_sm.render("32px pillar (day / night)", True, LABEL_DIM), (panel_x + 16, pcy + 152))

    # === (4) BLACKED-OUT SILHOUETTE PROOF =====================================
    sil_panel_y = 392
    pygame.draw.rect(sheet, (150, 150, 158), (panel_x, sil_panel_y, W - panel_x - 14, 196))
    sheet.blit(font.render("Blackout silhouette proof", True, (40, 38, 44)), (panel_x + 14, sil_panel_y + 6))
    sil_big = silhouette_of(150, 160, 75, 90, 0.86)
    sheet.blit(sil_big, (panel_x + 16, sil_panel_y + 28))
    sil_sm = silhouette_of(64, 64, 32, 34, (32 / 150.0))
    sheet.blit(pygame.transform.scale(sil_sm, (96, 96)), (panel_x + 196, sil_panel_y + 30))
    sheet.blit(font_sm.render("hero", True, (40, 38, 44)), (panel_x + 60, sil_panel_y + 172))
    sheet.blit(font_sm.render("32px (x3)", True, (40, 38, 44)), (panel_x + 210, sil_panel_y + 128))

    # === (5) PALETTE STRIP ====================================================
    pal_y = 600
    pygame.draw.rect(sheet, PANEL, (14, pal_y, W - 28, 60))
    sheet.blit(font.render("Pinned palette", True, LABEL), (24, pal_y + 6))
    swatches = [
        (BONE, "briny-indigo bone"), (BONE_D, "indigo shade"),
        (BONE_DD, "indigo hollow"), (CORAL, "coral HEART"),
        (CORAL_D, "deep coral"), (CONCH, "conch relic"),
        (SKULL, "encrusted skull"), (INK, "ink keyline"),
    ]
    sxp, syp = 24, pal_y + 30
    for i, (c, name) in enumerate(swatches):
        rx = sxp + i * 126
        pygame.draw.rect(sheet, INK, (rx - 1, syp - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, syp, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx, syp + 22))

    # footer
    pygame.draw.rect(sheet, PANEL, (14, H - 56, W - 28, 42))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat triad fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, H - 44))
    sheet.blit(font_sm.render(
        "Silhouette tell: an ORGANIC knobbly BRANCHING canopy (forked, spreading) — not discrete radiating limbs (anti-Mukha starburst).",
        True, LABEL_DIM), (26, H - 28))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
