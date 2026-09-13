"""
Round-1 concept renderer for LEKHA-DAKINI — the gilt-scripture mantra adept
(brood II `mukha_citipati_court_ii`, sister #4). Headless Pygame; ELEVATED
pipeline (SS=8 supersample -> smoothscale) so the gold lantsa-script bands,
prayer-wheel pendants and the round stupa finial stay crisp at downscale. Keeps
the shipped house grammar: flat saturated fills, hard 1-2px ink keyline
(28,22,26), dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown
outline, chibi proportions, scary-CUTE; procedural-only.

WHY this sister is collision-free vs the bone/skull kings: she is the ONLY
indigo+vermillion+gold figure. The indigo ground is pushed materially BLUER and
a touch lighter than ink so it NEVER collapses to the taken near-black+gold
("Obsidian" king) at 32px on the night sky — a real blue separates her. The
deliberate VERMILLION seal-cartouche is a visible second note (a clear red stamp
on the torso, not a hidden 2px mark). Her crown is the ANTI-gable: a smooth
ROUND-domed stupa/chorten finial (bumpa dome + harmika + stacked umbrella rings
+ sun-moon tip) — roundness is what separates her from the angular GABLED
reliquary-shrine king. The finial springs from BEHIND the centre skull so the
fused arc+band still reads UNBROKEN in front of it (never replaced).

WHY CITIPATI body + MUKHA fan: she is one of the 3 Citipati-bodied sisters —
the tall rib-barrel dancing torso, cocked hip, bone limbs — but wears the locked
Mukha SIX-ARM radial fan, six open PALMS each cradling a TINY SKULL, and the
fused crown (Citipati 5-skull arc-SWEEP + Mukha tiara-BAND). The fresh ornament
class is gold lantsa-SCRIPT inlay bands wrapping bone + prayer-wheel cylinder
pendants (hero-only). Glow ONLY on third-eye + crown-centre skull.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers cloned from the
sister renderers, not runtime sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

# FONT — five `..` up from this sister dir to game/assets/.
FONT_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "..", "game", "assets", "LiberationSans-Bold.ttf"))

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Bone stays the dominant figure mass; indigo is the ornament/inlay GROUND, gold
# the script, vermillion the seal. WHY indigo pushed materially BLUER + a touch
# lighter than ink: it must read BLUE (not black) at 32px on the night sky so she
# never collapses into the taken near-black+gold king — the whole separator.
BONE      = (240, 230, 208)   # warm-ivory bone (the dominant figure fill)
BONE_D    = (188, 174, 142)   # bone dark-core / shade
BONE_DD   = (138, 124,  96)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (255, 248, 230)   # bone top-left rim-sheen
INDIGO    = ( 58,  72, 158)   # indigo-ink ornament GROUND — emphatically BLUE
INDIGO_D  = ( 38,  48, 112)   # indigo shade (still clearly blue, never black)
INDIGO_BR = ( 96, 116, 200)   # indigo top sheen
GOLD      = (226, 184,  78)   # gold lantsa-script + ring inlay
GOLD_BR   = (250, 218, 122)   # hot gold sheen / finial dome highlight
GOLD_D    = (168, 130,  50)   # gold shade
# WHY the finial dome is now a MID/DIM gold (not the old pale 248,232,170): the
# value ladder is locked third-eye(brightest)->palm-skulls(mid)->crown(dimmest).
# The dome must sit clearly BELOW the ivory palm-skulls so the white-cored gold
# third-eye stays the single brightest pixel by a wide margin. Roundness — not
# brightness — is what makes the dome read as the 32px carrier silhouette.
GOLD_DOME = (176, 142,  64)   # mid/dim gold bumpa dome (crown = dimmest mass)
GOLD_DOME_BR = (208, 170,  88)  # dome convex sheen — still below palm-skull bone
VERM      = (208,  52,  40)   # VERMILLION seal — a visible red cartouche, not a sliver
VERM_BR   = (236,  96,  72)   # vermillion sheen
VERM_D    = (150,  32,  28)   # vermillion shade
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (248, 214, 120)   # GOLD third-eye glow (her focal — warm pin)
THIRD_BR  = (255, 244, 200)   # hottest third-eye core (single brightest pixel)

BG        = ( 92,  94, 104)   # neutral grey review backdrop
PANEL     = ( 72,  74,  86)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  88)   # +6 blue vs r1 — banks margin off Obsidian near-black
LABEL     = (240, 238, 242)
LABEL_DIM = (194, 196, 206)


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


# ── gold lantsa-script inlay band (the fresh ornament class) ──────────────────
def script_band(surf, p0, p1, s, w, glyphs=4):
    """An indigo inlay strip carrying a row of gold lantsa glyph-marks. WHY
    indigo ground + gold marks: the script must read as gilt scripture INLAID on
    the bone, not a plain ring — the indigo channel separates the gold from the
    ivory so both stay legible. At 32px the glyph-marks mush to a dense gold band
    (intended). Each glyph is a stylised lantsa stroke: a vertical stem, a curled
    head-tick and a foot-serif — abstract but reverently script-like."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / L, dy / L            # along the band
    nx, ny = -uy, ux                   # across the band
    hw = w / 2
    quad = [(p0[0] + nx * hw, p0[1] + ny * hw),
            (p1[0] + nx * hw, p1[1] + ny * hw),
            (p1[0] - nx * hw, p1[1] - ny * hw),
            (p0[0] - nx * hw, p0[1] - ny * hw)]
    # indigo inlay channel with the house triad
    triad_blob(surf, INDIGO, quad,
               sheen_pts=[(p0[0] + nx * hw, p0[1] + ny * hw),
                          (p1[0] + nx * hw, p1[1] + ny * hw),
                          (p1[0] + nx * hw * 0.4, p1[1] + ny * hw * 0.4),
                          (p0[0] + nx * hw * 0.4, p0[1] + ny * hw * 0.4)],
               ow=max(1, int(w * 0.16)))
    # gold script glyph-marks marching along the channel
    gw = max(2, int(2.2 * s))
    for i in range(glyphs):
        t = (i + 0.5) / glyphs
        cxg = p0[0] + ux * L * t
        cyg = p0[1] + uy * L * t
        stem = hw * 0.62
        # vertical stem of the glyph
        a = (cxg + nx * stem, cyg + ny * stem)
        b = (cxg - nx * stem, cyg - ny * stem)
        pygame.draw.line(surf, GOLD, a, b, gw)
        # curled head-tick (a short cross-stroke at the top of the stem)
        ht = (a[0] - ux * stem * 0.7, a[1] - uy * stem * 0.7)
        pygame.draw.line(surf, GOLD_BR, a, ht, max(1, gw - 1))
        # foot serif
        ft = (b[0] + ux * stem * 0.6, b[1] + uy * stem * 0.6)
        pygame.draw.line(surf, GOLD, b, ft, max(1, gw - 1))


# ── prayer-wheel cylinder pendant (hero-only detail) ──────────────────────────
def prayer_wheel(surf, cx, cy, s, rot=0.0):
    """A small gold cylinder pendant embossed with a vertical lantsa-band — the
    Tibetan prayer-wheel (mani-khor). WHY hero-only: the cylinder + emboss is too
    fussy to survive 32px, so it appears only at hero scale to enrich the figure;
    the script-bands + finial carry the small-scale read."""
    wpx = int(8 * s)
    hpx = int(13 * s)
    body = [(cx - wpx, cy - hpx), (cx + wpx, cy - hpx),
            (cx + wpx, cy + hpx), (cx - wpx, cy + hpx)]
    triad_blob(surf, GOLD, body,
               core_pts=[(cx + int(2 * s), cy - hpx), (cx + wpx, cy - hpx),
                         (cx + wpx, cy + hpx), (cx + int(2 * s), cy + hpx)],
               sheen_pts=[(cx - wpx, cy - hpx), (cx - int(wpx * 0.4), cy - hpx),
                          (cx - int(wpx * 0.4), cy + hpx), (cx - wpx, cy + hpx)],
               ow=max(1, int(1.4 * s)))
    # the indigo band around the drum carrying a gold lantsa stroke
    pygame.draw.rect(surf, INDIGO, (cx - wpx, cy - int(3 * s), wpx * 2, int(6 * s)))
    pygame.draw.line(surf, GOLD_BR, (cx - int(wpx * 0.5), cy - int(2 * s)),
                     (cx - int(wpx * 0.5), cy + int(2 * s)), max(1, int(1.4 * s)))
    pygame.draw.line(surf, GOLD_BR, (cx + int(wpx * 0.4), cy - int(2 * s)),
                     (cx + int(wpx * 0.4), cy + int(2 * s)), max(1, int(1.4 * s)))
    # rim caps top + bottom (the spindle ferrules)
    for ry in (cy - hpx, cy + hpx):
        pygame.draw.ellipse(surf, GOLD_BR, (cx - wpx, ry - int(2 * s), wpx * 2, int(4 * s)))
        pygame.draw.ellipse(surf, INK, (cx - wpx, ry - int(2 * s), wpx * 2, int(4 * s)),
                            max(1, int(1 * s)))
    # the swinging weight-bead on a chain (the mani spinner)
    pygame.draw.line(surf, GOLD_D, (cx + wpx, cy),
                     (cx + wpx + int(7 * s), cy + int(6 * s)), max(1, int(1.4 * s)))
    triad_circle(surf, VERM, (cx + wpx + int(7 * s), cy + int(6 * s)), int(3 * s),
                 ow=max(1, int(1 * s)), core=False)


# ── a tiny SKULL cradled in an open palm (the core locked motif) ──────────────
def palm_skull(surf, cx, cy, r, s, lit=False):
    """An open bone PALM cradling a TINY ivory skull. WHY palm + skull, not a
    relic: brood II's locked core motif is six open palms each holding a small
    skull. The palm is a shallow bone cup; the skull is a domed cranium with two
    dark sockets so it punches a clean bone shape with two dots at 32px."""
    # open palm cup beneath the skull
    cup = [(cx - int(r * 1.15), cy + int(r * 0.30)),
           (cx + int(r * 1.15), cy + int(r * 0.30)),
           (cx + int(r * 0.75), cy + int(r * 1.05)),
           (cx - int(r * 0.75), cy + int(r * 1.05))]
    triad_blob(surf, BONE, cup, ow=max(1, int(1.2 * s)))
    # three short finger-ticks curling up around the skull
    for k in (-1, 0, 1):
        fx = cx + int(k * r * 0.8)
        pygame.draw.line(surf, INK, (fx, cy + int(r * 0.30)),
                         (fx + int(k * r * 0.25), cy - int(r * 0.30)), max(1, int(1.6 * s)))
        pygame.draw.line(surf, BONE, (fx, cy + int(r * 0.30)),
                         (fx + int(k * r * 0.25), cy - int(r * 0.30)), max(1, int(1 * s)))
    # the tiny skull dome
    triad_circle(surf, BONE, (cx, cy - int(r * 0.10)), int(r * 0.85),
                 ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.42), cy + int(r * 0.55)),
           (cx + int(r * 0.42), cy + int(r * 0.55)),
           (cx + int(r * 0.26), cy + int(r * 0.92)),
           (cx - int(r * 0.26), cy + int(r * 0.92))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1 * s)))
    eye_c = THIRD_BR if lit else INK
    for ex in (cx - int(r * 0.34), cx + int(r * 0.34)):
        pygame.draw.circle(surf, INK, (ex, cy - int(r * 0.04)), max(1, int(r * 0.22)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy - int(r * 0.04)), max(1, int(r * 0.11)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.26)), max(1, int(r * 0.12)))


# ── a single crown-skull (Citipati arc + Mukha tiara reuse) ───────────────────
def crown_skull(surf, cx, cy, r, s, lit=False):
    """Tiny ivory crown-skull — domed cranium, two dark sockets, stub jaw. Used
    for both the Citipati 5-skull arc-SWEEP and seated into the tiara band. `lit`
    swaps the eye-pins to warm gold for the glowing crown-centre skull."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.5 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.96)),
           (cx - int(r * 0.32), cy + int(r * 0.96))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    eye_c = THIRD_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── the ROUND stupa/chorten finial (the ANTI-gable crown carrier) ─────────────
def stupa_finial(surf, cx, base_y, h, s):
    """A smooth ROUND-domed stupa/chorten finial built so its SILHOUETTE is a fat
    round dome topped by a CONE OF ROUND RINGS — every contour convex/curved, no
    straight edge, no pinched chevron, no triangular gable anywhere.

    WHY rebuilt for round 2: roundness is the ONLY separator from the angular
    GABLED reliquary-shrine king, and at 32px the old pinched-ring spire collapsed
    to a pointed angular spike = that collision. The fix makes the spire a smooth
    tapering CONE assembled from heavily OVERLAPPING round discs (the umbrella
    rings barely step in radius and sit close together, so their outer edges trace
    a gently curved cone wall — a stack of beads, never a sawtooth). The top ~6px
    of the blackout finial is a rounded sun-disc + crescent cap, NOT a point.

    The dome is a MID/DIM gold (GOLD_DOME) — the dimmest crown mass per the value
    ladder; only the third-eye + crown-centre skull get drawn glow, never the dome
    face. `base_y` is where the dome foot sits; the finial rises UPWARD."""
    # WHY the dome is LARGE relative to a SHORT spire: at the carrier scale any
    # tall-narrow spire blacks out to a triangular spike (the gable collision). A
    # big round dome that DOMINATES, topped by a stubby fat-bead stack + a round
    # ball, keeps the blackout silhouette a wide ROUND mound — never a needle.
    dome_r = int(h * 0.40)
    dome_cy = base_y - int(h * 0.22)
    # round bumpa DOME — dim-gold, the dominant ROUND mass (the 32px carrier shape)
    triad_circle(surf, GOLD_DOME, (cx, dome_cy), dome_r, ow=max(1, int(1.8 * s)),
                 core=False, sheen=False)
    # a soft convex sheen so the dome reads round (kept BELOW palm-skull bone value)
    pygame.draw.circle(surf, GOLD_DOME_BR,
                       (cx - int(dome_r * 0.30), dome_cy - int(dome_r * 0.34)),
                       max(1, int(dome_r * 0.42)))
    # a thin curved throne-band hugging the dome foot (anti-gable: an arc, not an edge)
    pygame.draw.arc(surf, INDIGO,
                    (cx - dome_r, dome_cy - int(dome_r * 0.2), dome_r * 2, int(dome_r * 1.0)),
                    math.radians(196), math.radians(344), max(2, int(2.6 * s)))

    # SHORT FAT STACK OF ROUND RINGS — the spire is deliberately squat with only a
    # few BOLDLY-STEPPED discs (each clearly smaller, with a wide pitch) so the
    # blackout outline is a ROUND STAIRCASE of bumps, NOT a smooth tapering needle.
    # WHY this matters at the carrier scale: a tall smooth cone blacks out to a
    # triangular SPIKE = the Garnet gable collision. A short stepped stack stays
    # legibly tiered/round even after downscale. The radius does not run to a
    # point — the smallest ring is still a fat disc, then a BALL caps it.
    # TWO fat round beads only — a stubby stack, each bead WIDE so the outline is a
    # round staircase, kept short so the dome stays the dominant mass.
    ring_radii = [0.62, 0.48]
    ring_gap = h * 0.085
    ring_top_y = dome_cy - dome_r + int(h * 0.05)
    top_ring_cy = ring_top_y
    for i, frac in enumerate(ring_radii):
        rr = max(3, int(dome_r * frac))
        ry = ring_top_y - int(i * ring_gap)
        triad_circle(surf, GOLD, (cx, ry), rr, ow=max(1, int(1.2 * s)),
                     core=False, sheen=False)
        pygame.draw.circle(surf, GOLD_BR, (cx - int(rr * 0.28), ry - int(rr * 0.30)),
                           max(1, int(rr * 0.40)))
        top_ring_cy = ry

    # ROUND BALL TIP — a fat sun-DISC ball wider than the top bead, sitting close on
    # the stack so the very top reads as a CIRCLE (a ball cap), never a point.
    ball_r = int(dome_r * 0.50)
    ball_cy = top_ring_cy - int(dome_r * 0.18) - ball_r
    # crescent moon behind/beside the sun-ball (gold disc with an indigo bite)
    triad_circle(surf, GOLD_BR, (cx + int(ball_r * 0.10), ball_cy), int(ball_r * 1.02),
                 ow=max(1, int(1.2 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, INDIGO, (cx + int(ball_r * 0.78), ball_cy - int(ball_r * 0.18)),
                       int(ball_r * 0.92))
    # the round sun-ball itself — the literal rounded tip, a fat circle
    triad_circle(surf, GOLD, (cx, ball_cy), ball_r, ow=max(1, int(1.2 * s)),
                 core=False, sheen=False)
    pygame.draw.circle(surf, GOLD_BR, (cx - int(ball_r * 0.28), ball_cy - int(ball_r * 0.30)),
                       max(1, int(ball_r * 0.46)))


# ── the six-arm radial fan (cloned from Mukha; ends in palm-skulls) ───────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the locked Mukha six-arm radial fan. Low origin (below the head), arc spans
    ~[100,64,28] deg off vertical, three per side, NONE straight up so the crown
    sky stays open. Routes BEHIND the torso/head. Returns the six hand centres
    so each can cradle a tiny palm-skull on the outer arc."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(11 * s)
    spread = [100, 64, 28]
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])
    hands = []
    for sgn, d, a in order:
        sh = (shoulder[0] + sgn * int(hr * 0.55), shoulder[1])
        elbow = (sh[0] + math.cos(a) * arm_len * 0.52,
                 sh[1] + math.sin(a) * arm_len * 0.52)
        hand = (sh[0] + math.cos(a) * arm_len,
                sh[1] + math.sin(a) * arm_len)
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
        # a thin gold lantsa-script wrist cuff at each hand (ornament, not naked)
        wx, wy = hand
        ex, ey = elbow
        cuff0 = (ex + (wx - ex) * 0.66, ey + (wy - ey) * 0.66)
        script_band(surf, cuff0, (wx, wy), s, int(arm_th * 1.1), glyphs=2)
        hands.append((sgn, d, hand))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1])) for h in hands]


# ── the gilt-scripture mantra adept ───────────────────────────────────────────
def draw_lekha_dakini(surf, cx, cy, s, hero=False):
    """CITIPATI-bodied dancing bone-adept under the locked Mukha six-arm fan; six
    open palms cradle tiny skulls; the fused crown (5-skull arc-SWEEP + tiara
    BAND) reads unbroken IN FRONT of a round stupa finial springing from behind
    the centre skull. Ornament: gold lantsa-script inlay bands + (hero-only)
    prayer-wheel pendants; indigo+vermillion+gold palette. `s` = unit scale
    around a ~140-unit figure. `hero` enables the prayer-wheel pendants."""

    head_c = (cx, cy - int(34 * s))
    hr = int(26 * s)
    hip_y = cy + int(24 * s)
    hip_cx = cx + int(7 * s)            # Citipati cocked hip

    # === SIX-ARM RADIAL FAN (drawn first → behind torso & head) ===============
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.86), s, hr)

    # === LEGS — Citipati cocked-hip dance: one knee kicked OUT =================
    def bone_limb(p0, p1, p2, thick, joint=True):
        for (a, b) in ((p0, p1), (p1, p2)):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = max(1.0, math.hypot(dx, dy))
            nx, ny = -dy / L * thick / 2, dx / L * thick / 2
            quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                    (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
            triad_blob(surf, BONE, quad,
                       sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                                  (b[0] + nx * 0.3, b[1] + ny * 0.3),
                                  (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                       ow=max(1, int(thick * 0.18)))
        if joint:
            triad_circle(surf, BONE, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                         core=False)

    leg_th = int(13 * s)
    hipL = (hip_cx - int(13 * s), hip_y)
    kneeL = (hip_cx - int(20 * s), hip_y + int(26 * s))
    footL = (hip_cx - int(22 * s), hip_y + int(52 * s))
    bone_limb(hipL, kneeL, footL, leg_th)
    hipR = (hip_cx + int(11 * s), hip_y)
    kneeR = (hip_cx + int(30 * s), hip_y + int(8 * s))
    footR = (hip_cx + int(20 * s), hip_y + int(34 * s))
    bone_limb(hipR, kneeR, footR, leg_th)
    for (fx, fy), sgn in ((footL, -1), (footR, +1)):
        foot = [(fx - int(4 * s), fy - int(2 * s)), (fx + sgn * int(15 * s), fy + int(2 * s)),
                (fx + sgn * int(14 * s), fy + int(10 * s)), (fx - int(5 * s), fy + int(8 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.4 * s)))
    # gold lantsa anklet-script on the standing shin (ornament, never naked)
    script_band(surf, (kneeL[0], kneeL[1] + int(8 * s)),
                (footL[0], footL[1] - int(6 * s)), s, int(leg_th * 1.05), glyphs=2)

    # === PELVIS + RIBCAGE torso ===============================================
    pelvis = [(hip_cx - int(17 * s), hip_y - int(4 * s)),
              (hip_cx + int(17 * s), hip_y - int(6 * s)),
              (hip_cx + int(14 * s), hip_y + int(10 * s)),
              (hip_cx, hip_y + int(13 * s)),
              (hip_cx - int(15 * s), hip_y + int(9 * s))]
    triad_blob(surf, BONE, pelvis,
               core_pts=[(hip_cx - int(6 * s), hip_y + int(2 * s)),
                         (hip_cx + int(14 * s), hip_y - int(2 * s)),
                         (hip_cx + int(13 * s), hip_y + int(9 * s)),
                         (hip_cx, hip_y + int(12 * s))],
               ow=max(1, int(1.6 * s)))
    pygame.draw.circle(surf, BONE_DD, (hip_cx, hip_y + int(2 * s)), int(4 * s))

    spine_top_y = cy - int(16 * s)
    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx + int(2 * s), cy + int(4 * s)),
             (cx - int(1 * s), spine_top_y)]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    rc_cx, rc_cy = cx, cy - int(4 * s)
    rc_w, rc_h = int(34 * s), int(40 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.40), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(6 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.8 * s)))
    # rib bands
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.4 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(6 * s)), max(1, int(2 * s)))

    # === GOLD LANTSA-SCRIPT BANDS wrapping the torso (the fresh ornament) =====
    # WHY two horizontal script bands across the rib-barrel: gilt scripture
    # INLAID on bone is her ornament class — rows of gold glyph-marks on an
    # indigo channel. They route across the front of the cage so the figure
    # never reads naked, and mush to a dense gold band at 32px (intended).
    script_band(surf, (rc_cx - int(rc_w * 0.46), rc_cy - int(6 * s)),
                (rc_cx + int(rc_w * 0.46), rc_cy - int(8 * s)), s, int(7 * s), glyphs=4)
    script_band(surf, (rc_cx - int(rc_w * 0.42), rc_cy + int(12 * s)),
                (rc_cx + int(rc_w * 0.42), rc_cy + int(10 * s)), s, int(7 * s), glyphs=4)

    # === VERMILLION SEAL CARTOUCHE on the chest (visible red second note) =====
    # WHY a clear stamp, not a sliver: the brood-read needs a deliberate visible
    # vermillion — a red consecration seal block centred on the sternum with a
    # gold glyph, the loud second colour that (with the blue indigo) keeps her
    # off the near-black+gold king.
    seal_w, seal_h = int(13 * s), int(15 * s)
    seal_x, seal_y = rc_cx, rc_cy + int(rc_h * 0.10)
    seal = [(seal_x - seal_w, seal_y - seal_h), (seal_x + seal_w, seal_y - seal_h),
            (seal_x + seal_w, seal_y + seal_h), (seal_x - seal_w, seal_y + seal_h)]
    triad_blob(surf, VERM, seal,
               core_pts=[(seal_x + int(2 * s), seal_y - seal_h), (seal_x + seal_w, seal_y - seal_h),
                         (seal_x + seal_w, seal_y + seal_h), (seal_x + int(2 * s), seal_y + seal_h)],
               sheen_pts=[(seal_x - seal_w, seal_y - seal_h), (seal_x - int(seal_w * 0.4), seal_y - seal_h),
                          (seal_x - int(seal_w * 0.4), seal_y), (seal_x - seal_w, seal_y)],
               ow=max(1, int(1.8 * s)))
    # gold lantsa glyph stamped in the seal
    pygame.draw.line(surf, GOLD_BR, (seal_x, seal_y - int(seal_h * 0.6)),
                     (seal_x, seal_y + int(seal_h * 0.55)), max(1, int(2.2 * s)))
    pygame.draw.line(surf, GOLD_BR, (seal_x - int(seal_w * 0.5), seal_y - int(seal_h * 0.4)),
                     (seal_x + int(seal_w * 0.5), seal_y - int(seal_h * 0.4)), max(1, int(2 * s)))
    pygame.draw.arc(surf, GOLD, (seal_x - int(seal_w * 0.6), seal_y, int(seal_w * 1.2), int(seal_h * 0.9)),
                    math.radians(200), math.radians(340), max(1, int(1.8 * s)))
    pygame.draw.rect(surf, GOLD_D, (seal_x - seal_w, seal_y - seal_h, seal_w * 2, seal_h * 2),
                     max(1, int(1.4 * s)))

    # === ARMS — Citipati flamenco flourish (the dancing pair, over the fan) ===
    arm_th = int(8 * s)
    shoulderL = (rc_cx - int(16 * s), rc_cy - rc_h // 2 + int(6 * s))
    shoulderR = (rc_cx + int(16 * s), rc_cy - rc_h // 2 + int(5 * s))
    elbowL = (rc_cx - int(33 * s), rc_cy - int(20 * s))
    handL = (rc_cx - int(29 * s), rc_cy - int(43 * s))
    bone_limb(shoulderL, elbowL, handL, arm_th)
    elbowR = (rc_cx + int(33 * s), rc_cy - int(2 * s))
    handR = (rc_cx + int(43 * s), rc_cy + int(16 * s))
    bone_limb(shoulderR, elbowR, handR, arm_th)
    for (hx, hy), up in ((handL, True), (handR, False)):
        triad_circle(surf, BONE, (hx, hy), int(5 * s), ow=max(1, int(1.2 * s)), core=False)
        for k in range(-1, 3):
            ang = math.radians(-90 + k * 26) if up else math.radians(40 + k * 26)
            ex = hx + math.cos(ang) * int(8 * s)
            ey = hy + math.sin(ang) * int(8 * s)
            pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(1, int(1.6 * s)))
            pygame.draw.line(surf, BONE, (hx, hy), (ex, ey), max(1, int(1 * s)))

    # === PRAYER-WHEEL CYLINDER PENDANTS (hero-only) ===========================
    # WHY they hang off the two dancing hands: the spinning mani-wheels are the
    # signature hero detail — too fine for 32px, so gated to hero scale.
    if hero:
        prayer_wheel(surf, handL[0] - int(4 * s), handL[1] + int(14 * s), s)
        prayer_wheel(surf, handR[0] + int(2 * s), handR[1] + int(16 * s), s)

    # === SIX PALM-SKULLS — one cradled at each fan hand (the locked core) =====
    palm_r = int(9 * s)
    for (hx, hy) in hands:
        palm_skull(surf, hx, hy, palm_r, s)

    # === SKULL HEAD — chibi, scary-cute, GOLD third eye =======================
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # big round sockets — scary-cute, a NOTCH dimmer than the third eye
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.10)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.27))
        pygame.draw.circle(surf, GOLD_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.11))
    # THIRD EYE — GOLD, the single brightest pixel (her warm focal).
    tex, tey = head_c[0], head_c[1] - int(hr * 0.40)
    pygame.draw.ellipse(surf, INK, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, GOLD, (tex - int(5 * s), tey - int(7 * s), int(10 * s), int(14 * s)))
    pygame.draw.ellipse(surf, THIRD_EYE, (tex - int(3 * s), tey - int(5 * s), int(6 * s), int(10 * s)))
    pygame.draw.circle(surf, THIRD_BR, (tex, tey - int(1 * s)), max(2, int(3.0 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex, tey - int(1 * s)), max(1, int(1.4 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.26)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.26)),
                         (head_c[0], head_c[1] + int(hr * 0.52))])
    # grinning tooth row
    my = head_c[1] + int(hr * 0.68)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))

    # === ROUND STUPA FINIAL — springs from BEHIND the centre skull ============
    # WHY drawn BEFORE the crown arc+band, and WHY the dome foot sits ABOVE the
    # crown arc: the finial must clear the head so its round dome + spire reads as
    # the crown silhouette (the 32px carrier). Its FOOT tucks behind the centre
    # crown-skull so the fused 5-skull arc + tiara-band overdraw it and read
    # UNBROKEN IN FRONT — the dome rises above, never replacing the arc.
    finial_h = int(hr * 1.15)
    # dome foot tucked just behind the centre crown-skull (no floating gap) while
    # the arc+band still overdraw it; a big dome + short stack keeps it compact.
    stupa_finial(surf, head_c[0], head_c[1] - int(hr * 1.28), finial_h, s)

    # === FUSED CROWN: Citipati 5-skull arc-SWEEP + Mukha tiara-BAND ===========
    # WHY both, frontmost: brood-locked. The wide 5-skull arc-sweep crowns the head
    # AND a gold lantsa tiara-band runs across the brow under it. The centre skull
    # is the lit crown glow. The finial peeks UP between/behind the arc — never over.
    # -- the Mukha tiara-BAND across the brow (gold script, seated low) --
    tiara_r = int(hr * 1.04)
    tiara_cy = head_c[1] - int(hr * 0.04)
    band_pts = []
    for i in range(11):
        a = math.radians(214 + i * (112 / 10))   # brow arc
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         tiara_cy + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(7 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, GOLD_BR, False, band_pts[:6], max(1, int(1.4 * s)))
    # gold lantsa glyph-ticks marching along the tiara band
    for i in range(1, 10, 2):
        bx, by = band_pts[i]
        pygame.draw.circle(surf, GOLD_BR, (int(bx), int(by)), max(1, int(1.6 * s)))

    # -- the Citipati 5-skull arc-SWEEP riding OUTSIDE the band (frontmost) --
    # WHY the arc hugs the brow with the centre skull pulled DOWN off the apex: the
    # finial dome owns the apex, so the 5-skull sweep wraps the upper head and the
    # centre crown-skull sits just below the dome foot — arc+band frontmost, the
    # round dome rising clearly above as the silhouette tell.
    arc_cy = head_c[1] - int(hr * 0.04)
    skull_cr = hr * 1.20
    skull_r = int(hr * 0.36)
    # the centre skull rides a touch lower so the dome clears it
    for i in range(5):
        a = math.radians(208 + i * (124 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = arc_cy + math.sin(a) * skull_cr
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2))


# ── the mantra-pillar mirror (built from the sister's OWN forms) ──────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The mantra-pillar IS her own forms: a banded bone shaft INLAID with gold
    lantsa-script channels (the torso ornament continued) hung with prayer-wheel
    cylinder pendants = the tileable shaft; a round stupa-finial dome + crown-skull
    caps each gap edge — her crown's own round language, symmetric and on-axis.

    `cap` names the END that faces the GAP."""
    shaft_w = int(14 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(24 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    idx = 0
    while y <= b1:
        # a fat bone band carrying a gold lantsa-script channel (the shaft tile)
        bw = shaft_w
        band = [(cx - bw, y - int(9 * s)), (cx + bw, y - int(9 * s)),
                (cx + bw, y + int(9 * s)), (cx - bw, y + int(9 * s))]
        triad_blob(surf, BONE, band,
                   core_pts=[(cx, y - int(8 * s)), (cx + bw, y - int(8 * s)),
                             (cx + bw, y + int(8 * s)), (cx, y + int(8 * s))],
                   sheen_pts=[(cx - bw, y - int(8 * s)), (cx - int(bw * 0.3), y - int(8 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        # the inlaid script channel across the band
        script_band(surf, (cx - bw + int(2 * s), y), (cx + bw - int(2 * s), y), s,
                    int(9 * s), glyphs=3)
        # a prayer-wheel pendant hung off alternating sides (the hero detail)
        side = -1 if (idx % 2 == 0) else 1
        rx = cx + side * (bw + int(9 * s))
        pygame.draw.line(surf, GOLD, (cx + side * bw, y), (rx, y + int(2 * s)),
                         max(1, int(1.6 * s)))
        prayer_wheel(surf, rx, y + int(6 * s), s * 0.62)
        idx += 1
        y += band_pitch

    # === gap-edge cap: a round stupa-finial dome + crown-skull ================
    cap_y = (bot - int(26 * s)) if cap == "bottom" else (top + int(26 * s))
    # the round finial dome rises away from the gap; the crown-skull faces the gap
    if cap == "bottom":
        crown_skull(surf, cx, cap_y, int(13 * s), s, lit=True)
        stupa_finial(surf, cx, cap_y - int(16 * s), int(34 * s), s)
    else:
        crown_skull(surf, cx, cap_y, int(13 * s), s, lit=True)
        stupa_finial(surf, cx, cap_y + int(50 * s), int(34 * s), s)
    # a gold lantsa collar where the cap meets the shaft
    collar_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    script_band(surf, (cx - int(13 * s), collar_y), (cx + int(13 * s), collar_y), s,
                int(8 * s), glyphs=3)


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def measure_extent(scale, hero=True):
    """Draw the figure once at the given unit-scale on a generous transparent
    canvas and return its tight alpha bounding box, so the hero + chips can be
    AUTO-FIT inside their frames with real margin (round-1 clipped the finial and
    the dancing shin/foot). WHY measure per render-mode: hero=True hangs the
    prayer-wheels out wider than the 32px figure, so the bbox must be taken in the
    SAME mode it will be drawn or the fit mis-scales and re-clips the finial."""
    pad = 360
    probe = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    draw_lekha_dakini(probe, pad, pad, scale, hero=hero)
    r = probe.get_bounding_rect()
    # offsets of the figure's bbox relative to the draw centre (pad, pad)
    return r.width, r.height, (r.centerx - pad), (r.centery - pad)


def render_hero_surface(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_lekha_dakini(big, draw_cx * SS, draw_cy * SS, scale * SS, hero=True)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def fit_hero(boxw, boxh, hero=True, margin=0.92):
    """Render the figure auto-fit + auto-centred inside a box with `margin`
    headroom on the tighter axis, so nothing clips. Returns the outlined surface."""
    probe_scale = 4.0
    w0, h0, ox0, oy0 = measure_extent(probe_scale, hero=hero)
    scale = probe_scale * min((boxw * margin) / w0, (boxh * margin) / h0)
    # re-measure at the chosen scale (bbox is linear in scale, so offsets scale too)
    k = scale / probe_scale
    cx = boxw / 2 - ox0 * k
    cy = boxh / 2 - oy0 * k
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_lekha_dakini(big, cx * SS, cy * SS, scale * SS, hero=hero)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def export_hero(path):
    """Standalone hi-res hero ~1024px tall on a soft indigo-grey vignette."""
    HW, HH = 760, 1024
    surf = pygame.Surface((HW, HH))
    vgrad(surf, (0, 0, HW, HH), (44, 46, 64), (28, 30, 44))
    # auto-fit so the rebuilt round-ring spire AND the dancing shin/foot both sit
    # inside the frame with margin (round-1 clipped top + bottom).
    hero = fit_hero(640, 940, hero=True, margin=0.94)
    surf.blit(hero, (HW // 2 - 320, 84))
    font = pygame.font.Font(FONT_PATH, 30)
    font_sm = pygame.font.Font(FONT_PATH, 18)
    surf.blit(font.render("LEKHA-DAKINI", True, LABEL), (28, 24))
    surf.blit(font_sm.render("gilt-scripture mantra adept  ·  brood II #4  ·  hero  ·  SS=8  ·  round 2",
                             True, LABEL_DIM), (28, 62))
    pygame.image.save(surf, path)
    print("wrote", path)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    export_hero(os.path.join(out_dir, "round_2_hero.png"))

    W, H = 1040, 860
    font_big = pygame.font.Font(FONT_PATH, 30)
    font = pygame.font.Font(FONT_PATH, 17)
    font_sm = pygame.font.Font(FONT_PATH, 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("LEKHA-DAKINI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "gilt-scripture mantra adept  ·  brood II #4  ·  CITIPATI body + Mukha 6-arm fan  ·  "
        "indigo+vermillion+gold  ·  round stupa finial  ·  round 2",
        True, LABEL_DIM), (250, 24))

    # === (a) BIG HERO — auto-fit so finial + dancing shin sit inside =========
    hero = fit_hero(372, 510, hero=True, margin=0.93)
    sheet.blit(hero, (14, 88))
    sheet.blit(font.render("Creature — hero", True, LABEL), (120, 596))
    sheet.blit(font_sm.render("Six-arm fan; six open palms cradle tiny skulls. Fused crown: 5-skull arc-SWEEP", True, LABEL_DIM), (14, 620))
    sheet.blit(font_sm.render("+ gold tiara-BAND, UNBROKEN in front of a ROUND stupa finial behind centre skull.", True, LABEL_DIM), (14, 636))
    sheet.blit(font_sm.render("Gold lantsa-script inlay + prayer-wheels + vermillion chest seal. Gold third-eye.", True, LABEL_DIM), (14, 652))

    # === (b) PILLAR — mirrored, from her own forms ============================
    pcx = 408
    top_big = pygame.Surface((140 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 70 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (140, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 84))
    bot_big = pygame.Surface((140 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 70 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (140, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 84 + 250 + 92))
    pygame.draw.rect(sheet, (58, 60, 74), (pcx + 8, 84 + 250, 124, 92))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 50, 84 + 250 + 38))
    sheet.blit(font.render("Pillar — mantra-staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("script-inlay bone bands + prayer-wheel", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("pendants = shaft; round stupa-dome +", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("crown-skull caps each gap (mirrored)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) panels: chips, blackout proof, palette ===========================
    panel_x = 590
    pygame.draw.rect(sheet, PANEL, (panel_x, 84, W - panel_x - 14, 690))
    sheet.blit(font.render("True 32px gameplay chip", True, LABEL), (panel_x + 16, 94))

    def chip32():
        # TRUE 32px: render the figure at a 32px footprint, auto-centred, then show
        # it on a 104px swatch (3.25x preview) so the full shape — including the
        # rebuilt round dome+spire and the dancing leg — sits inside, never cropped.
        TARGET = 32
        prev = 104
        w0, h0, ox0, oy0 = measure_extent(4.0, hero=False)
        scale = 4.0 * (TARGET * 0.92) / max(w0, h0)
        k = scale / 4.0
        ccx = TARGET / 2 - ox0 * k
        ccy = TARGET / 2 - oy0 * k
        big = pygame.Surface((TARGET * SS, TARGET * SS), pygame.SRCALPHA)
        draw_lekha_dakini(big, ccx * SS, ccy * SS, scale * SS, hero=False)
        small = pygame.transform.smoothscale(big, (TARGET, TARGET))
        small = grow_outline(small, INK + (255,), 1)
        return pygame.transform.scale(small, (prev, prev))

    chip = chip32()
    day_y = 122
    vgrad(sheet, (panel_x + 18, day_y, 140, 140), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 18, day_y, 140, 140), 1)
    sheet.blit(chip, (panel_x + 18 + 18, day_y + 18))
    sheet.blit(font_sm.render("32px DAY", True, LABEL), (panel_x + 18, day_y + 144))

    night_y = day_y + 172
    vgrad(sheet, (panel_x + 18, night_y, 140, 140), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 18, night_y, 140, 140), 1)
    sheet.blit(chip, (panel_x + 18 + 18, night_y + 18))
    sheet.blit(font_sm.render("32px NIGHT", True, LABEL_DIM), (panel_x + 18, night_y + 144))

    # 32px pillar gap-cap chips beside, on both skies
    def pillar_chip32():
        big = pygame.Surface((42 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 21 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (42, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 172
    vgrad(sheet, (px2, day_y, 54, 140), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 54, 140), 1)
    sheet.blit(pc, (px2 + 6, day_y + 6))
    vgrad(sheet, (px2, night_y, 54, 140), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 54, 140), 1)
    sheet.blit(pc, (px2 + 6, night_y + 6))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # blackout / silhouette proof — the read MUST survive as a pure shape
    sheet.blit(font.render("Blackout / silhouette proof", True, LABEL), (panel_x + 16, night_y + 174))
    bo_w, bo_h = 104, 130
    bw0, bh0, box0, boy0 = measure_extent(4.0, hero=False)
    bo_scale = 4.0 * min((bo_w * 0.88) / bw0, (bo_h * 0.88) / bh0)
    bk = bo_scale / 4.0
    bo_cx = bo_w / 2 - box0 * bk
    bo_cy = bo_h / 2 - boy0 * bk
    bo_big = pygame.Surface((bo_w * SS, bo_h * SS), pygame.SRCALPHA)
    draw_lekha_dakini(bo_big, bo_cx * SS, bo_cy * SS, bo_scale * SS, hero=False)
    bo_small = pygame.transform.smoothscale(bo_big, (bo_w, bo_h))
    mask = pygame.mask.from_surface(bo_small)
    sil = mask.to_surface(setcolor=(18, 18, 22, 255), unsetcolor=(0, 0, 0, 0))
    boy = night_y + 198
    vgrad(sheet, (panel_x + 18, boy, 104, 130), (208, 210, 216), (170, 172, 180))
    pygame.draw.rect(sheet, INK, (panel_x + 18, boy, 104, 130), 1)
    sheet.blit(sil, (panel_x + 18, boy))
    sheet.blit(font_sm.render("six-arm star + stupa", True, LABEL_DIM), (panel_x + 130, boy + 50))
    sheet.blit(font_sm.render("dome reads as a shape", True, LABEL_DIM), (panel_x + 130, boy + 66))

    # palette strip
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 612))
    swatches = [
        (BONE, "ivory bone"), (INDIGO, "indigo ground (BLUE)"),
        (GOLD, "gold lantsa-script"), (GOLD_DOME, "dim-gold dome (crown=dimmest)"),
        (VERM, "vermillion seal"), (THIRD_EYE, "gold third-eye"),
        (INDIGO_D, "indigo shade"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 638
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 200
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 786, W - 28, 60))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 798))
    sheet.blit(font_sm.render(
        "32px CARRIER: the ROUND stupa dome + CONE-OF-ROUND-RINGS silhouette — never an angular spike (the anti-Garnet read).  "
        "Value ladder: gold third-eye = sole brightest; palm-skulls mid; dim-gold crown dome dimmest. Indigo reads BLUE on night.",
        True, LABEL_DIM), (26, 818))

    out = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
