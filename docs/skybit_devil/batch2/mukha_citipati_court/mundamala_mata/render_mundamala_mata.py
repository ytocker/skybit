"""
Round-1 concept renderer for MUNDAMALA-MATA — the severed-head-garland mother
(mukha_citipati_court brood, sister #4). Headless Pygame; ELEVATED pipeline
(supersample SS=8 → smoothscale) so the double-loop skull garland, the six
palm-cradled skulls, and the fused crown stay crisp at downscale. Keeps the
house grammar: flat triad fills, hard 1-2px ink keyline (28,22,26),
dark-core → flat-fill → top-left rim-sheen, 1px alpha-grown outline, chibi
scary-cute proportions; procedural-only.

WHY this sister is the GARLAND one: among the five court sisters the locked
"non-naked device" here is a MUNDAMALA — a double-loop severed-head/skull
garland that frames the face, fills the chest, and swings up beside the crown
into the open sky. That swag is the single bold shape that survives true 32px;
everything else (apron carving, lotus grooves, gold spacer pips) is hero-only
brocade that collapses into the garland mass.

WHY oxblood + gold dominate, rose only sparingly: the brood pins this sister to
the Mukha family but MOODIER, and explicitly guards against drifting back to
the rejected Mukha-round magenta. So the cord is OXBLOOD with GOLD bead-spacers
as the dominant rhythm; dusky rose is reserved for the single brightest pixel —
the third-eye slit — plus a thin crown-centre glow, nothing else.

WHY the value ladder is policed hard: third-eye = single brightest pixel → the
six palm-skulls = mid bone → the garland heads = DIMMEST (dusky, sunk a notch
below body bone) so the swag reads as one ornate dark wreath, never competing
with the focal triangle of the face.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers cloned from
the two reference renderers, not runtime sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

# FONT path from this sister dir is five "..": .../mundamala_mata → game/assets/
_HERE = os.path.dirname(os.path.abspath(__file__))
_FONT_TTF = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "..", "..",
                                          "game", "assets",
                                          "LiberationSans-Bold.ttf"))


def _font(size):
    if os.path.exists(_FONT_TTF):
        return pygame.font.Font(_FONT_TTF, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=True)


# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Dusky-rose bone is the body mass; OXBLOOD cord + GOLD spacers DOMINATE the
# ornament; rose is the single focal accent. Guarded AWAY from magenta.
# --- THE VALUE LADDER (the gate) ----------------------------------------------
# Four skull-types must NOT share one value. Three SEPARATED bands, each ~30-40L
# below the last: third-eye = single brightest (~255) → six palm-skulls MID
# (~L150-160, warmed) → garland heads + crown skulls DIMMEST (~L110-120). Body
# bone sits between palms and the eye so the face mass still reads as the brightest
# field after the focal triangle.
BONE      = (210, 184, 184)   # dusky-rose body bone (the dominant fill, L≈190)
BONE_D    = (150, 116, 124)   # mauve-bone dark-core / shade
BONE_DD   = (104,  76,  86)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (236, 220, 220)   # bone top-left rim-sheen
# Garland heads + crown skulls = DIMMEST band, dropped to ~L115 — a clear 35-40L
# gap below the palm-skulls so the strung swag reads as ONE dark ornate wreath,
# never a second field of bright skulls.
GHEAD     = (132, 102, 110)   # garland severed-head bone — DIMMEST tier (L≈115)
GHEAD_D   = ( 90,  66,  76)
GHEAD_SH  = (158, 130, 138)
# Palm-skulls = MID band, pulled DOWN to ~L155 and WARMED (a touch more red) so
# they sit a clean ~40L below the body and a clean ~40L above the garland.
PSKULL    = (180, 148, 142)   # palm-cradled tiny skull — MID tier (L≈155, warm)
PSKULL_D  = (134, 102, 104)
PSKULL_SH = (208, 180, 174)
OXBLOOD   = (104,  24,  30)   # oxblood garland cord — DOMINANT ornament colour
OXBLOOD_D = ( 66,  14,  20)
OXBLOOD_BR= (150,  46,  48)
GOLD      = (210, 164,  76)   # gold bead-spacers / apron trim — SPACER accent
GOLD_BR   = (242, 206, 122)
GOLD_D    = (154, 116,  48)
ROSE      = (214,  74, 110)   # dusky rose — focal ONLY (third-eye + crown core)
ROSE_BR   = (250, 150, 176)   # hot rose inner sheen (third-eye core)
ROSE_D    = (146,  40,  70)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (214,  74, 110)   # third-eye glow (rose — her single brightest pixel)
THIRD_BR  = (252, 168, 192)

BG        = ( 92,  86,  92)   # neutral grey review backdrop
PANEL     = ( 72,  68,  78)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 234, 238)
LABEL_DIM = (198, 190, 200)


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


# ── a tiny palm-cradled skull (the brood-wide six-palm motif) ─────────────────
def palm_skull(surf, cx, cy, r, s, lit=False):
    """A MID-tier bone skull cradled in an open palm. WHY brighter than the
    garland heads but dimmer than the third-eye: the locked value ladder makes
    these six the only ring of clean light skulls — the garland heads must sink
    below them.

    WHY the skull is drawn HEAVY (no surrounding bone pad, fat dome + jaw): all
    six palm-skulls must land on ONE readable MID value-band (~L155) when sampled
    at hero scale, between body (~L192) and garland (~L112). The earlier bone
    cradle-pad (BONE, ~L192) ringed the skull and let a sample hit body-value on
    some palms; here PSKULL is the dominant footprint so every palm samples MID."""
    triad_circle(surf, PSKULL, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, PSKULL, jaw, ow=max(1, int(1.1 * s)))
    eye_c = ROSE_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


def draw_palm(surf, hx, hy, r, s, oa):
    """An OPEN palm cradling a skull at the WRIST, fingers curling UP around it.
    WHY one construction for all six (no special-case for the lowest pair): the
    AD found the two horizontal palms read as skull-tipped FISTS — skull sitting
    AT the arm terminus, bead-knuckles wrapped over it. So every palm now seats
    its skull at a wrist set BACK from the arm-end, with an explicit wrist-gap
    below the skull and a fan of bead-fingers arcing UP and around it. `oa` is
    the arm's outward angle; the cradle opens along it so the cup always faces
    away from the body and the fingers always rise toward the sky-side."""
    # WHY the cradle is offset back toward the body along the arm axis: it pulls
    # the skull off the very tip so the bone wrist + finger-arc read on the
    # outboard side as "hand holding skull," not a knob capping the limb.
    ux, uy = math.cos(oa), math.sin(oa)            # outward (arm) direction
    px, py = -uy, ux                               # perpendicular (finger spread)
    # wrist pad: a small bone cup set just OUTBOARD of the skull, the heel of the
    # palm the skull rests in (kept small + below so it never out-masses PSKULL)
    wx = hx + ux * r * 0.46
    wy = hy + uy * r * 0.46
    triad_circle(surf, BONE, (int(wx), int(wy)), int(r * 0.44),
                 ow=max(1, int(1.0 * s)), core=False, sheen=False)
    # the wrist-gap: a sliver of ink between wrist heel and skull so the eye reads
    # an OPEN palm (skull held above the heel), never a fused skull-on-a-stick
    pygame.draw.line(surf, INK, (int(wx - px * r * 0.4), int(wy - py * r * 0.4)),
                     (int(wx + px * r * 0.4), int(wy + py * r * 0.4)),
                     max(1, int(1.4 * s)))
    # gold offering-pip nested in the heel of the palm (her gold-spacer cadence)
    pygame.draw.circle(surf, GOLD_D, (int(wx), int(wy)), max(1, int(r * 0.30)))
    pygame.draw.circle(surf, GOLD, (int(wx - ux * r * 0.06), int(wy - uy * r * 0.06)),
                       max(1, int(r * 0.20)))
    # five bead-fingers fanning UP and AROUND the skull on the inboard (sky) side,
    # curling toward the cradle so the hand visibly closes around what it holds
    for k in range(-2, 3):
        a = oa + math.pi + k * 0.52        # point back INWARD, then spread
        bx = hx + math.cos(a) * r * 1.18
        by = hy + math.sin(a) * r * 1.18
        pygame.draw.line(surf, INK, (int(wx), int(wy)), (int(bx), int(by)),
                         max(2, int(2.6 * s)))
        pygame.draw.line(surf, BONE, (int(wx), int(wy)), (int(bx), int(by)),
                         max(1, int(1.5 * s)))
        triad_circle(surf, BONE, (int(bx), int(by)), max(1, int(1.7 * s)),
                     ow=max(1, int(0.9 * s)), core=False, sheen=False)


# ── the six-arm radial starburst (Mukha KIND tell, cloned + palm ends) ────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the Mukha radial silhouette. Low SHOULDER origin, arc spans ≈ ±100° off
    vertical (top arms near-horizontal, mid-diagonal, low-down), NONE straight
    up so a clean wedge of open sky stays over the crown for the fused tiara to
    read. Returns the six hand centres (with their outward angle) for palms +
    palm-skulls."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.98)
    arm_th = int(12 * s)
    spread = [100, 64, 28]   # degrees off vertical for the 3 arms per side
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])   # lowest arms first → upper splay overlaps
    hands = []
    for sgn, d, a in order:
        sh = (shoulder[0] + sgn * int(hr * 0.55), shoulder[1])
        # WHY nudge the lowest (widest-spread, d≈100) pair outward: they otherwise
        # overlap the apron-edge chest-garland heads and muddle. ~5px of extra
        # outward reach gives each low palm-skull clean negative space and lets the
        # apron chest-loop read as a distinct lower band.
        #
        # WHY pull the UPPER (d≈28) pair IN: at full reach their palm-skulls landed
        # right on the sky-garland heads (same radius from the head) and got read at
        # the DIM garland value instead of the MID palm value. Shortening their reach
        # seats them inboard of the sky-loop arc, in clean sky, so all six palm-skulls
        # hold ONE mid band and the upper pair no longer collapses into the garland.
        if d >= 100:
            extra = int(hr * 0.16)
        elif d <= 28:
            extra = -int(hr * 0.22)
        else:
            extra = 0
        reach = arm_len + extra
        elbow = (sh[0] + math.cos(a) * reach * 0.52,
                 sh[1] + math.sin(a) * reach * 0.52)
        hand = (sh[0] + math.cos(a) * reach + sgn * extra * 0.5,
                sh[1] + math.sin(a) * reach)
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
                       ow=max(1, int(arm_th * 0.16)))
        triad_circle(surf, BONE, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        hands.append((sgn, d, hand, a))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1]), h[3]) for h in hands]


# ── a single severed garland head (the DIMMEST tier — the mundamala unit) ─────
def garland_head(surf, cx, cy, r, s):
    """One severed head on the cord — a dusky bone skull threaded through the
    crown. WHY the DIMMEST tier: the value ladder pins garland heads below both
    the third-eye and the palm-skulls, so each is drawn in bruised GHEAD bone
    with sunk sockets and NO lit core — the swag reads as one dark ornate wreath
    at a glance, the individual heads only on close inspection."""
    triad_circle(surf, GHEAD, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False, sheen=False)
    # faint top-left sheen so it still reads as rounded bone, not a flat dot
    pygame.draw.circle(surf, GHEAD_SH, (cx - int(r * 0.34), cy - int(r * 0.36)),
                       max(1, int(r * 0.22)))
    jaw = [(cx - int(r * 0.48), cy + int(r * 0.5)),
           (cx + int(r * 0.48), cy + int(r * 0.5)),
           (cx + int(r * 0.3), cy + int(r * 0.96)),
           (cx - int(r * 0.3), cy + int(r * 0.96))]
    triad_blob(surf, GHEAD, jaw, ow=max(1, int(1.0 * s)))
    for ex in (cx - int(r * 0.36), cx + int(r * 0.36)):
        pygame.draw.circle(surf, GHEAD_D, (ex, cy + int(r * 0.02)), max(1, int(r * 0.30)))
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.22)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.40)), max(1, int(r * 0.13)))


def gold_spacer(surf, cx, cy, r, s):
    """A gold bead-spacer between two garland heads — the DOMINANT rhythm dot
    that carries the cord's value/hue at hero AND keeps the swag legible as a
    string of beads, not a smear, near 32px."""
    triad_circle(surf, GOLD, (cx, cy), r, ow=max(1, int(1.0 * s)), core=False)
    pygame.draw.circle(surf, GOLD_BR, (cx - int(r * 0.3), cy - int(r * 0.3)),
                       max(1, int(r * 0.4)))


def draw_garland_loop(surf, cx, cy, rx, ry, a0, a1, s, n_heads, head_r,
                      cord_w, draw_heads=True):
    """One sweeping OXBLOOD cord loop hung with severed garland heads, gold beads
    cadenced as TRUE spacers. WHY cord-first and THICK: oxblood is the DOMINANT
    colour and must read as one continuous dark line at hero — so the cord is
    drawn heavy and the bright OXBLOOD_BR top-sheen is dropped (a bright cord
    competed with the gold). The dim heads sit ON the cord; gold appears only
    ~every 3rd-4th bead as a spacer accent, never a near-continuous gold string.
    The loop is an elliptical arc so it can frame the face, swag across the chest,
    or rise into the sky beside the crown depending on the caller."""
    # the oxblood cord — drawn THICK so it reads as one continuous dark swag and
    # out-masses the gold (the cord is the dominant ornament colour, not the gold)
    cord_pts = []
    steps = 46
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * (i / steps)
        cord_pts.append((cx + math.cos(a) * rx, cy + math.sin(a) * ry))
    pygame.draw.lines(surf, INK, False, cord_pts, int(cord_w + 4 * s))
    pygame.draw.lines(surf, OXBLOOD_D, False, cord_pts, int(cord_w + 2 * s))
    pygame.draw.lines(surf, OXBLOOD, False, cord_pts, int(cord_w))
    if not draw_heads:
        return
    # heads on EVERY non-end slot; gold drops in only ~every 3rd as a spacer accent
    slots = n_heads + 1
    for k in range(1, slots):
        a = a0 + (a1 - a0) * (k / slots)
        px = cx + math.cos(a) * rx
        py = cy + math.sin(a) * ry
        garland_head(surf, int(px), int(py), head_r, s)
    # gold spacer beads — sparse cadence: between heads, only every 3rd gap
    for k in range(0, slots):
        if k % 3 != 0:
            continue
        a = a0 + (a1 - a0) * ((k + 0.5) / slots)
        px = cx + math.cos(a) * rx
        py = cy + math.sin(a) * ry
        gold_spacer(surf, int(px), int(py), max(1, int(head_r * 0.40)), s)


# ── a single fused crown-skull (Citipati dome reused for the arc) ─────────────
def crown_skull(surf, cx, cy, r, s, lit=False):
    """Tiny bone skull for the fused crown arc — domed cranium, small sockets,
    stub jaw. WHY the SAME dim tier as the garland heads (GHEAD) and NO glow
    unless `lit`: the locked ladder pins crown skulls + garland heads to ONE
    dimmest band (~L115), a clear 40L below the palm-skulls; only the crown-CENTRE
    skull glows rose (the single permitted crown bloom)."""
    triad_circle(surf, GHEAD, (cx, cy), r, ow=max(1, int(1.4 * s)),
                 core=False, sheen=False)
    pygame.draw.circle(surf, GHEAD_SH, (cx - int(r * 0.34), cy - int(r * 0.36)),
                       max(1, int(r * 0.22)))
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, GHEAD, jaw, ow=max(1, int(1.1 * s)))
    eye_c = ROSE_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))


def tiara_skull(surf, cx, cy, r, s, lit=False):
    """The Mukha tiara-band skull seated across the brow (the band the crown
    fuses with the Citipati arc-sweep). Slightly squatter than the arc skulls so
    the two crown languages read as distinct registers stacked together."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.46)),
           (cx + int(r * 0.5), cy + int(r * 0.46)),
           (cx + int(r * 0.3), cy + int(r * 0.84)),
           (cx - int(r * 0.3), cy + int(r * 0.84))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.0 * s)))
    eye_c = ROSE_BR if lit else INK
    for ex in (cx - int(r * 0.36), cx + int(r * 0.36)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.0)), max(1, int(r * 0.22)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.0)), max(1, int(r * 0.12)))


# ── the severed-head-garland mother ───────────────────────────────────────────
def draw_mundamala_mata(surf, cx, cy, s):
    """Squat chibi bone-mother on a wide lotus throne, framed by a double-loop
    severed-head garland, under a six-arm radial fan whose palms each cradle a
    tiny skull, crowned by a FUSED Citipati arc + Mukha tiara band.
    `s` = unit scale around a ~136-unit figure."""

    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)

    # === SIX-ARM RADIAL FAN (drawn first → arms sit BEHIND torso & head) ======
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.84), s, hr)

    # === SKY GARLAND LOOP — the swag rises beside the crown into open sky ======
    # WHY drawn before the body: this upper loop arcs over the shoulders and up
    # past the temples so the mundamala fills the sky beside the fused crown —
    # the locked "fills the sky beside the crown" read — sitting behind the head.
    draw_garland_loop(surf, head_c[0], head_c[1] + int(hr * 0.10),
                      int(hr * 2.05), int(hr * 1.55),
                      math.radians(-202), math.radians(22), s,
                      n_heads=6, head_r=int(hr * 0.30), cord_w=int(5 * s))

    # === LOWER BODY — a wide squat lotus-base (Mukha throne; keeps mass low) ===
    base_y = cy + int(44 * s)
    base = [(cx - int(36 * s), base_y - int(7 * s)),
            (cx - int(25 * s), base_y - int(16 * s)),
            (cx + int(25 * s), base_y - int(16 * s)),
            (cx + int(36 * s), base_y - int(7 * s)),
            (cx + int(28 * s), base_y + int(12 * s)),
            (cx - int(28 * s), base_y + int(12 * s))]
    triad_blob(surf, BONE, base,
               core_pts=[(cx, base_y - int(15 * s)), (cx + int(30 * s), base_y - int(7 * s)),
                         (cx + int(23 * s), base_y + int(10 * s)), (cx, base_y + int(8 * s))],
               ow=max(1, int(1.6 * s)))
    # lotus petal grooves + gold petal-tips (hero brocade, collapses at 32px)
    for k in range(-2, 3):
        px = cx + int(k * 12 * s)
        pygame.draw.line(surf, BONE_DD, (px, base_y - int(16 * s)),
                         (px, base_y + int(9 * s)), max(1, int(1.4 * s)))
    for k in (-2, 0, 2):   # sparse gold petal-tips — matches the spacer cadence
        px = cx + int((k + 0.5) * 12 * s)
        pygame.draw.circle(surf, GOLD, (px, base_y - int(13 * s)), max(1, int(1.6 * s)))
    # an oxblood seed-knot at the lotus heart — secondary, kept deep (not focal)
    pygame.draw.circle(surf, OXBLOOD_D, (cx, base_y - int(3 * s)), int(5 * s))
    pygame.draw.circle(surf, OXBLOOD, (cx - int(1 * s), base_y - int(4 * s)), max(1, int(2 * s)))

    # === CARVED BONE APRON — backs the chest garland (the dense non-naked field)
    # WHY an apron behind the chest swag: the brief backs the mundamala with a
    # carved bone apron so the torso is never naked; it is a fan of bone slats
    # with gold-rivet trim, kept a value below the body so the bright cord + dim
    # heads stay legible against it.
    apron_top = cy + int(2 * s)
    apron = [(cx - int(26 * s), apron_top),
             (cx + int(26 * s), apron_top),
             (cx + int(31 * s), base_y - int(6 * s)),
             (cx - int(31 * s), base_y - int(6 * s))]
    triad_blob(surf, BONE_D, apron,
               core_pts=[(cx + int(2 * s), apron_top + int(2 * s)),
                         (cx + int(26 * s), apron_top),
                         (cx + int(31 * s), base_y - int(6 * s)),
                         (cx + int(2 * s), base_y - int(6 * s))],
               ow=max(1, int(1.6 * s)))
    for k in range(-4, 5):   # carved bone slats — VERTICAL ribbing (the decisive
        px = cx + int(k * 7 * s)   # non-naked tell; kept dense + straight-vertical)
        pygame.draw.line(surf, BONE_DD, (px, apron_top + int(3 * s)),
                         (px, base_y - int(8 * s)), max(1, int(1.6 * s)))
    # gold rivet trim across the apron lip — sparse cadence (every other slat) so
    # the apron isn't more gold-heavy than the re-cadenced garland
    for k in range(-4, 5, 2):
        px = cx + int(k * 7 * s)
        pygame.draw.circle(surf, GOLD, (px, apron_top + int(3 * s)), max(1, int(1.6 * s)))

    # === TORSO — a SHORT rib barrel (squat Mukha proportion) ==================
    rc_cx, rc_cy = cx, cy + int(10 * s)
    rc_w, rc_h = int(32 * s), int(24 * s)
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
    for i in range(2):
        ry = rc_cy - rc_h // 2 + int(7 * s) + i * int(8 * s)
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx, rc_cy + int(3 * s)), max(1, int(2 * s)))

    # === CHEST GARLAND LOOP — the lower swag of the double-loop mundamala ======
    # WHY a deep U across the chest: the inner loop dips low over the rib barrel
    # and apron so the garland clearly FILLS the chest (the brief), completing
    # the "double-loop" with the sky loop above.
    draw_garland_loop(surf, rc_cx, rc_cy - int(2 * s),
                      int(hr * 1.18), int(hr * 0.92),
                      math.radians(28), math.radians(152), s,
                      n_heads=5, head_r=int(hr * 0.26), cord_w=int(5 * s))

    # === SIX OPEN PALMS, each cradling a TINY SKULL (the brood motif) =========
    # WHY palms drawn here, then palm-skulls last so they sit ON the cradle: the
    # six fan-tips read as a ring of open hands each offering a mid-bone skull —
    # the value tier between the focal eye and the dim garland.
    for (hx, hy, oa) in hands:
        draw_palm(surf, hx, hy, int(hr * 0.32), s, oa)
    # The cradled tiny skull sits ON each palm at the SAME hand centre for all six
    # — MID tier (the brood motif). WHY drawn dead-last and footprint-dominant: it
    # must sample ~L155 on every palm; sitting on top of both garland loops AND the
    # body keeps the upper pair off the garland band and the left pair off body bone.
    for (hx, hy, oa) in hands:
        palm_skull(surf, hx, hy, int(hr * 0.28), s)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (the framed FACE) =========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two big lower sockets — empty, wrathful, NEUTRAL DARK (ink/oxblood-shadow,
    # ~L35). WHY no rose fill: rose is reserved for the brow third-eye ALONE; a
    # rose socket-fill makes two competing focals flanking the brow. The sockets
    # read as hollow shadow, the eye as the single bloom.
    SOCKET = (44, 30, 34)   # oxblood-shadow ink, ~L35 — empty wrathful socket
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, SOCKET, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.16))
    # THIRD EYE — the single BRIGHTEST pixel on the whole sprite (locked rule).
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, ROSE, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, ROSE_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, THIRD_BR, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.48), my),
                     (head_c[0] + int(hr * 0.48), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.15), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.15), my + int(hr * 0.13)), max(1, int(1 * s)))
    for sgn in (-1, 1):   # corner fangs (wrathful tell)
        fx = head_c[0] + sgn * int(hr * 0.40)
        pygame.draw.polygon(surf, BONE_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.22))])

    # === FUSED CROWN — Citipati arc-sweep AND Mukha tiara-band TOGETHER ========
    # WHY both registers, stacked: a plain arc alone reads as the Citipati
    # reference, so the crown shows BOTH — a low wide 6-skull ARC fanned in the
    # open sky over the head (the sweep) AND a tiara BAND of squat skulls seated
    # across the brow just above the third-eye (the band). Centre arc-skull is
    # the one permitted rose glow; everything else stays dim per the ladder.
    # -- Mukha tiara BAND across the brow --
    band_r = int(hr * 1.04)
    band_pts = []
    for i in range(11):
        a = math.radians(232 + i * (76 / 10))   # shallow band seated on the brow
        band_pts.append((head_c[0] + math.cos(a) * band_r,
                         head_c[1] + math.sin(a) * band_r))
    # WHY a DARK band, not a gold one: at true 32px the crown skulls collapse to a
    # lumpy cap and the tiara-band is the fusion tell. A single darker horizontal
    # line across the brow survives the downscale; a thin gold rim sits on top for
    # hero richness only.
    # WHY the dark underlay is widened (9s): the band must persist at true 32px as
    # ONE slightly-darker horizontal row across the brow — the fusion tell. The
    # extra dark width sits INSIDE the dark cap silhouette (it never widens the
    # blackout outline), so it strengthens the 32px band read without touching the
    # clean dark-cap shape the AD flagged as KEEP.
    pygame.draw.lines(surf, INK, False, band_pts, int(9 * s))
    pygame.draw.lines(surf, OXBLOOD, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, max(1, int(1.6 * s)))
    for i in range(4):   # squat tiara-band skulls on the brow
        a = math.radians(240 + i * (60 / 3))
        sx = head_c[0] + math.cos(a) * band_r
        sy = head_c[1] + math.sin(a) * band_r
        tiara_skull(surf, int(sx), int(sy), int(hr * 0.20), s)
    # -- Citipati 6-skull ARC sweeping ABOVE the band, in the open sky --
    arc_r = int(hr * 1.62)
    for i in range(6):
        a = math.radians(212 + i * (116 / 5))
        sx = head_c[0] + math.cos(a) * arc_r
        sy = head_c[1] + math.sin(a) * arc_r
        crown_skull(surf, int(sx), int(sy), int(hr * 0.34), s, lit=(i in (2, 3)))
    # the single permitted crown-centre rose glow at the arc apex
    apex = (head_c[0], head_c[1] - arc_r + int(hr * 0.10))
    pygame.draw.circle(surf, ROSE_D, apex, max(2, int(hr * 0.16)))
    pygame.draw.circle(surf, ROSE, apex, max(1, int(hr * 0.10)))
    pygame.draw.circle(surf, ROSE_BR, (apex[0] - int(1 * s), apex[1] - int(1 * s)),
                       max(1, int(hr * 0.05)))


# ── the garland-cord pillar mirror (built from her OWN forms) ─────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The mundamala IS the pillar: a vertical OXBLOOD cord strung with the
    sister's own alternating gold spacers + severed garland heads = the tileable
    shaft; the gap-edge cap is a lotus-cup hung with a glowing rose-cored skull
    (her lotus throne + focal language) — symmetric, on-axis, never top-heavy.

    `cap` names the END that faces the GAP."""
    head_r = int(8 * s)
    # the oxblood cord rod the beads thread onto
    pygame.draw.rect(surf, INK, (cx - int(4 * s), top, int(8 * s), bot - top))
    pygame.draw.rect(surf, OXBLOOD_D, (cx - int(3 * s), top, int(6 * s), bot - top))
    pygame.draw.rect(surf, OXBLOOD, (cx - int(2 * s), top, int(3 * s), bot - top))

    pitch = int(22 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    # WHY heads-dominant, gold every 3rd: the hero garland cut gold to a sparse
    # spacer cadence, so the shaft matches — mostly dim severed heads strung on
    # the dark oxblood cord, a gold bead only every third unit. The shaft must NOT
    # be more gold-heavy than the hero garland.
    y = b0
    idx = 0
    while y <= b1:
        if idx % 3 == 1:   # a gold spacer bead — sparse rhythm accent
            gold_spacer(surf, cx, y, int(head_r * 0.66), s)
        else:              # a severed garland head (dim) threaded on the cord
            garland_head(surf, cx, y, head_r, s)
            for sgn in (-1, 1):   # tiny oxblood side-knots so the shaft is dense
                pygame.draw.circle(surf, OXBLOOD,
                                   (cx + sgn * int(head_r * 1.05), y), max(1, int(2 * s)))
        idx += 1
        y += pitch

    # === gap-edge cap: a lotus-cup + glowing rose-cored skull =================
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    grow = +1 if cap == "bottom" else -1
    # lotus cup opening toward the gap (her throne language, in miniature)
    petals = []
    for k in range(7):
        a = (math.radians(-90 + (k - 3) * 22) if grow > 0
             else math.radians(90 + (k - 3) * 22))
        tip = (cx + math.cos(a) * int(16 * s), cap_y + math.sin(a) * int(16 * s))
        mid = (cx + math.cos(a - 0.18) * int(8 * s), cap_y + math.sin(a - 0.18) * int(8 * s))
        mid2 = (cx + math.cos(a + 0.18) * int(8 * s), cap_y + math.sin(a + 0.18) * int(8 * s))
        triad_blob(surf, BONE, [(cx, cap_y), mid, tip, mid2], ow=max(1, int(1.2 * s)))
    # gold collar where the cup meets the cord
    collar_y = cap_y - grow * int(20 * s)
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # the glowing rose-cored skull at the cup hub (the single gap glow)
    crown_skull(surf, cx, cap_y, int(8 * s), s, lit=True)
    pygame.draw.circle(surf, ROSE, (cx, cap_y - int(2 * s)), max(1, int(2.4 * s)))
    pygame.draw.circle(surf, ROSE_BR, (cx - int(1 * s), cap_y - int(3 * s)), max(1, int(1.4 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def render_hero_surface(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_mundamala_mata(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def export_hero_png():
    """Standalone hi-res hero (~1024px tall) on a dusk panel — the close-read
    proof of the garland + fused crown + palm-skulls + value ladder."""
    HW, HH = 820, 1024
    surf = pygame.Surface((HW, HH))
    vgrad(surf, (0, 0, HW, HH), (52, 40, 52), (30, 24, 36))
    hero = render_hero_surface(720, 940, 360, 470, 3.05)
    surf.blit(hero, ((HW - 720) // 2, (HH - 940) // 2))
    f = _font(26)
    surf.blit(f.render("MUNDAMALA-MATA  ·  severed-head garland mother", True, LABEL),
              (28, 22))
    out = os.path.join(_HERE, "round_3_hero.png")
    pygame.image.save(surf, out)
    return out


def main():
    W, H = 1040, 920
    font_big = _font(30)
    font = _font(17)
    font_sm = _font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("MUNDAMALA-MATA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "severed-head garland mother  ·  MUKHA body + lotus throne · double-loop skull garland "
        "· OXBLOOD-dominant cord, gold true-spacer · rose third-eye focal ONLY · round 3",
        True, LABEL_DIM), (300, 27))

    # === (a) BIG HERO =========================================================
    hero = render_hero_surface(380, 500, 190, 250, 1.55)
    sheet.blit(hero, (14, 86))
    sheet.blit(font.render("Creature — hero", True, LABEL), (120, 596))
    sheet.blit(font_sm.render("Double-loop MUNDAMALA frames face, fills chest + sky beside the crown (the 32px shape).", True, LABEL_DIM), (14, 620))
    sheet.blit(font_sm.render("Six open palms each cradle a tiny skull. Fused crown = 6-skull arc-sweep + Mukha tiara band.", True, LABEL_DIM), (14, 636))
    sheet.blit(font_sm.render("Ladder: rose third-eye brightest > palm-skulls mid > garland heads dimmest. Oxblood+gold dominate.", True, LABEL_DIM), (14, 652))

    # === (b) PILLAR assembled — mirrored, built from her own forms ============
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (58, 52, 64), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — mundamala cord", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("oxblood cord strung with alternating gold", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("spacers + severed heads = tileable shaft;", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("lotus-cup + glowing skull caps the gap (mirrored).", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 540))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((112 * SS, 112 * SS), pygame.SRCALPHA)
        draw_mundamala_mata(big, 56 * SS, 60 * SS, (32 / 156.0) * SS)
        small = pygame.transform.smoothscale(big, (112, 112))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 19, day_y + 19))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 19, night_y + 19))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # === (d) BLACKOUT / SILHOUETTE proof ======================================
    sil_y = night_y + 184
    sheet.blit(font.render("Silhouette proof", True, LABEL), (panel_x + 16, sil_y - 18))
    sil_big = pygame.Surface((150 * SS, 150 * SS), pygame.SRCALPHA)
    draw_mundamala_mata(sil_big, 75 * SS, 80 * SS, (40 / 156.0) * SS)
    sil_small = pygame.transform.smoothscale(sil_big, (150, 150))
    mask = pygame.mask.from_surface(sil_small)
    blk = mask.to_surface(setcolor=(18, 14, 18, 255), unsetcolor=(0, 0, 0, 0))
    pygame.draw.rect(sheet, (210, 206, 214), (panel_x + 20, sil_y, 150, 150))
    pygame.draw.rect(sheet, INK, (panel_x + 20, sil_y, 150, 150), 1)
    sheet.blit(blk, (panel_x + 20, sil_y))
    sheet.blit(font_sm.render("garland swag + fan + crown read as one shape", True, LABEL_DIM),
               (panel_x + 20, sil_y + 156))

    # === palette strip ========================================================
    sheet.blit(font.render("Pinned palette", True, LABEL), (14, 776))
    swatches = [
        (BONE, "dusky-rose body bone"), (BONE_D, "mauve-bone shade"),
        (OXBLOOD, "OXBLOOD cord (dom.)"), (GOLD, "GOLD spacers (dom.)"),
        (PSKULL, "palm-skull (mid)"), (GHEAD, "garland head (DIM)"),
        (ROSE, "rose third-eye (focal)"), (INK, "ink keyline"),
    ]
    sxp, syp = 14, 800
    for i, (c, name) in enumerate(swatches):
        col, row = i % 4, i // 4
        rx = sxp + col * 154
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 24, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 872, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale.  STAY: flat triad fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen · 1px grown outline · chibi scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 885))

    out = os.path.join(_HERE, "round_3.png")
    pygame.image.save(sheet, out)
    return out


if __name__ == "__main__":
    hero_path = export_hero_png()
    sheet_path = main()
    print("wrote", sheet_path)
    print("wrote", hero_path)
