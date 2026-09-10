"""
Round-1 concept renderer for the CARNELIAN WARLORD — the armoured colossus of
the KING SKULL royal brood (Batch 2 / skull_kings, concept #3). Headless Pygame;
ELEVATED pipeline (supersample SS=6 -> smoothscale) so the extra plate/spike
geometry stays crisp at the downscale. Clones the shipped house grammar from
jiangshi_epic/citipati/render_citipati.py: flat saturated fills, hard 1-2px ink
keyline (28,22,30), dark-core -> flat-fill -> top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE; procedural-only.

WHY this king is the colossus pole: every other king in the court is slender,
seated, radial, organic or tiny. The Warlord is the ONLY heavy/broad-shouldered
mass -- a top-heavy WEDGE (wide pauldron shoulders tapering to a narrow planted
base) with a single VERTICAL planted greatsword down the dead centre. That broad
wedge + centre-line sword is the 32px tell, readable day and night.

WHY the bronze bone is pushed clearly WARMER/grubbier than Citipati's ivory: the
brief's failure mode is "ivory king with red trim." So the bone fill is a dirty
bronze (~206,176,128) -- a full step warmer + darker than the (246,236,210)
ivory -- and it stays the DOMINANT mass. Iron is CONFINED to the crown + the two
pauldrons + the narrow skull-belt (never a torso plate), so the warm bone barrel
is always the biggest field. Carnelian is a THIN accent only: the brow gem (the
single brightest focal), a sword-fuller line, a pauldron rivet glow.

WHY the lineage tells: two-armed (gripping the planted sword), an iron skull-belt
and pauldron skull-faces tie it to the Citipati skull grammar without the
5-skull corona (that crown is Citipati's alone). The crown here is a heavy
FORWARD-spiked iron war-crown -- its own iconic royal headpiece.

WHY a standalone script under docs/: review art never enters the shipped bundle,
so this reuses only colour math + the triad/outline helpers, not runtime modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Bronze-dirty bone is the dominant mass; iron + carnelian are accents only.
# WHY pushed warm/grubby vs ivory: the brief's drift risk is "ivory king w/ red
# trim." A full warm-down step (R up, B down) keeps it reading as a battle-grimed
# bronze colossus, distinct from Citipati's high-key (246,236,210) ivory.
# WHY pushed warmer+dirtier than the brief's ~(206,176,128) target: at a bright
# day sky the prior bronze still flirted with ivory. Dropping value ~12 and
# loading red keeps the triad dimensional while reading unmistakably as a
# battle-grimed bronze, never "ivory king with red trim."
BONE      = (198, 162, 112)   # bronze-dirty bone (the dominant fill)
BONE_D    = (150, 118,  76)   # bone dark-core
BONE_DD   = (102,  78,  46)   # deepest bone hollow (sockets, plate gaps)
BONE_SH   = (230, 202, 152)   # bone top-left rim-sheen
IVORY_REF = (246, 236, 210)   # Citipati ivory, swatched ONLY to prove bone reads warmer

# dark-iron: pauldrons + crown + skull-belt ONLY (never a torso plate)
IRON      = ( 74,  78,  88)   # dark blued iron (cool, low value)
IRON_D    = ( 46,  48,  58)   # iron deep shade
IRON_BR   = (126, 132, 146)   # iron top edge / bevel highlight
IRON_RIM  = (150, 162, 184)   # cool blue-grey rim that carries iron on night sky

# blood-carnelian: THIN accent only; the brow gem is the single brightest focal
CARN      = (176,  30,  34)   # blood-carnelian accent
CARN_D    = (120,  22,  26)
CARN_BR   = (224,  72,  62)   # lit carnelian facet
CARN_HOT  = (255, 168, 150)   # gem hot core (single brightest pixel)

STEEL     = (150, 156, 168)   # the planted sword blade (cool neutral steel)
STEEL_D   = ( 96, 102, 116)
STEEL_BR  = (212, 218, 228)   # blade light edge / fuller highlight
GOLD      = (210, 168,  84)   # a sliver of gilt on the crown band / pommel
GOLD_BR   = (242, 206, 120)

INK       = ( 28,  22,  30)   # hard ink keyline

BG        = ( 96, 100, 108)   # neutral grey review backdrop
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


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


def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
    """Two-segment bronze-bone limb with ink keyline + bulbous joint (cloned)."""
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


# -- a tiny iron skull-face (the lineage tell on belt + pauldrons) ------------
def iron_skull(surf, cx, cy, r, s):
    """A small DARK-IRON skull medallion: domed cranium, two DARK INK sockets,
    a notch grin. WHY iron + ink sockets (not carnelian pins): the skull tell on
    this king is forged into his armour -- it reads as a riveted war medallion,
    keeping bone the only big pale field and iron confined to crown/pauldron/belt.
    The sockets are dark ink, NOT red, so the brow gem stays the SOLE red focal."""
    triad_circle(surf, IRON, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    pygame.draw.circle(surf, IRON_RIM, (cx - int(r * 0.4), cy - int(r * 0.42)),
                       max(1, int(r * 0.22)))
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.96)),
           (cx - int(r * 0.32), cy + int(r * 0.96))]
    triad_blob(surf, IRON, jaw, ow=max(1, int(1.0 * s)))
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        pygame.draw.circle(surf, IRON_D, (ex, cy + int(r * 0.02)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.12)))
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.68)),
                     (cx + int(r * 0.34), cy + int(r * 0.68)),
                     max(1, int(1.0 * s)))


# -- the heavy forward-spiked iron WAR-CROWN (this king's iconic headpiece) ---
def war_crown(surf, cx, cy, w, s):
    """A heavy iron circlet with FORWARD-RAKED spikes (tilted toward the viewer,
    not straight up) so the crown reads as aggressive/martial and is unmistakably
    NOT Citipati's 5-skull arc. A blood-carnelian brow gem sits dead-centre on the
    band -- the single brightest focal. WHY forward-spiked: it gives the top
    silhouette a jagged battlemented read that survives 32px and pairs with the
    broad-shoulder wedge as 'warlord,' not 'priest.'"""
    band_h = int(11 * s)
    band = [(cx - w // 2, cy),
            (cx + w // 2, cy),
            (cx + int(w * 0.42), cy + band_h),
            (cx - int(w * 0.42), cy + band_h)]
    triad_blob(surf, IRON, band,
               core_pts=[(cx - int(w * 0.3), cy + int(band_h * 0.4)),
                         (cx + w // 2, cy + int(band_h * 0.2)),
                         (cx + int(w * 0.42), cy + band_h),
                         (cx - int(w * 0.3), cy + band_h)],
               ow=max(1, int(1.6 * s)))
    # cool rim along the top band edge so iron survives the night sky
    pygame.draw.line(surf, IRON_RIM, (cx - w // 2 + int(2 * s), cy + int(1.5 * s)),
                     (cx + w // 2 - int(2 * s), cy + int(1.5 * s)), max(1, int(2 * s)))
    # gilt under-rail (a sliver of royal gold)
    pygame.draw.line(surf, GOLD, (cx - int(w * 0.42), cy + band_h - int(1.5 * s)),
                     (cx + int(w * 0.42), cy + band_h - int(1.5 * s)), max(1, int(1.6 * s)))

    # FORWARD-RAKED spikes -- 5 across, the centre tallest, all tipped toward us
    n = 5
    for i in range(n):
        t = i / (n - 1)
        base_x = cx + int((t - 0.5) * w * 0.86)
        # tallest at centre, raked forward (tip pulled toward the viewer/down-front)
        height = (26 - abs(i - 2) * 5) * s
        rake = int((8 - abs(i - 2) * 2) * s)          # forward lean of the tip
        half = int((5.5 - abs(i - 2) * 0.7) * s)
        tip = (base_x + rake, cy - int(height))
        spike = [(base_x - half, cy + int(2 * s)),
                 (base_x + half, cy + int(2 * s)),
                 (tip[0] + int(2 * s), tip[1] + int(3 * s)),
                 tip]
        triad_blob(surf, IRON, spike,
                   sheen_pts=[(base_x - half, cy), (tip[0], tip[1] + int(4 * s)),
                              (tip[0] + int(1 * s), tip[1] + int(2 * s)),
                              (base_x - int(half * 0.4), cy)],
                   ow=max(1, int(1.2 * s)))
        # cool rim on the front (lit) edge of each spike for night legibility
        pygame.draw.line(surf, IRON_RIM, (base_x - half + int(1 * s), cy),
                         tip, max(1, int(1.2 * s)))

    # blood-carnelian brow GEM dead-centre on the band -- the single focal
    gx, gy = cx, cy + int(band_h * 0.5)
    gr = int(6.5 * s)
    pygame.draw.circle(surf, INK, (gx, gy), gr + max(1, int(1 * s)))
    pygame.draw.circle(surf, CARN_D, (gx, gy), gr)
    pygame.draw.circle(surf, CARN, (gx, gy), int(gr * 0.82))
    pygame.draw.circle(surf, CARN_BR, (gx - int(gr * 0.22), gy - int(gr * 0.24)), int(gr * 0.46))
    pygame.draw.circle(surf, CARN_HOT, (gx - int(gr * 0.3), gy - int(gr * 0.32)), max(1, int(gr * 0.22)))


# -- the armoured colossus ----------------------------------------------------
def draw_warlord(surf, cx, cy, s):
    """Top-heavy broad-shouldered WEDGE: wide iron pauldrons up top tapering down
    to a narrow planted stance, with a single VERTICAL greatsword planted point-
    down the dead centre, both bony hands stacked on the grip. `s` = unit scale
    around a ~130-unit-tall figure."""

    # vertical anchors (chibi: big head, broad short torso, planted stubby legs)
    head_c = (cx, cy - int(34 * s))
    hr = int(22 * s)
    shoulder_y = cy - int(10 * s)
    hip_y = cy + int(26 * s)

    # === PLANTED GREATSWORD (drawn FIRST so torso/hands stack over the grip) ==
    # WHY dead-centre + vertical + point-down: this is the unique 32px tell. The
    # blade runs from below the chin down past the feet, planted into the ground;
    # the crossguard sits at the belt, the pommel just under the chin.
    blade_w = int(11 * s)
    blade_top = cy - int(6 * s)
    blade_bot = cy + int(70 * s)
    blade_tip = cy + int(82 * s)
    blade = [(cx - blade_w, blade_top),
             (cx + blade_w, blade_top),
             (cx + blade_w, blade_bot),
             (cx, blade_tip),
             (cx - blade_w, blade_bot)]
    triad_blob(surf, STEEL, blade,
               core_pts=[(cx, blade_top), (cx + blade_w, blade_top),
                         (cx + blade_w, blade_bot), (cx, blade_tip)],
               sheen_pts=[(cx - blade_w, blade_top), (cx - int(blade_w * 0.3), blade_top),
                          (cx - int(blade_w * 0.3), blade_bot), (cx - blade_w, blade_bot)],
               ow=max(1, int(1.6 * s)))
    # dark STEEL fuller groove down the blade centre -- NOT red, so the brow gem
    # stays the single red focal; the groove just adds blade dimension.
    pygame.draw.line(surf, STEEL_D, (cx, blade_top + int(4 * s)),
                     (cx, blade_bot - int(2 * s)), max(1, int(2.2 * s)))
    pygame.draw.line(surf, STEEL_BR, (cx - int(blade_w * 0.55), blade_top + int(3 * s)),
                     (cx - int(blade_w * 0.55), blade_bot - int(4 * s)), max(1, int(1.4 * s)))

    # === LEGS -- ONE chunky planted bronze segment per side + a big foot ======
    # WHY consolidated to a single thick column (no knee bead): scattered joint
    # knobs muddy at 32px. A clean wide bone pillar per leg plants the figure
    # astride the sword and reads as a solid base, not loose beads.
    leg_th = int(16 * s)
    for sgn in (-1, 1):
        hipx = cx + sgn * int(13 * s)
        footx = cx + sgn * int(16 * s)
        fy = hip_y + int(44 * s)
        # a single straight bone column from hip to ankle (no mid joint)
        dx, dy = footx - hipx, fy - hip_y
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * leg_th / 2, dx / L * leg_th / 2
        quad = [(hipx + nx, hip_y + ny), (footx + nx, fy + ny),
                (footx - nx, fy - ny), (hipx - nx, hip_y - ny)]
        triad_blob(surf, BONE, quad,
                   sheen_pts=[(hipx + nx, hip_y + ny), (footx + nx, fy + ny),
                              (footx + nx * 0.3, fy + ny * 0.3),
                              (hipx + nx * 0.3, hip_y + ny * 0.3)],
                   ow=max(1, int(leg_th * 0.16)))
        # one large bronze knee-cap segment (single big knob, not a bead string)
        triad_circle(surf, BONE, (cx + sgn * int(15 * s), hip_y + int(22 * s)),
                     int(9 * s), ow=max(1, int(1.4 * s)), core=False)
        # chunky planted foot block
        fx = footx
        foot = [(fx - int(6 * s), fy - int(2 * s)), (fx + sgn * int(17 * s), fy + int(1 * s)),
                (fx + sgn * int(16 * s), fy + int(11 * s)), (fx - int(7 * s), fy + int(9 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.4 * s)))

    # === PELVIS + broad RIBCAGE torso (the dominant bronze mass) =============
    pelvis = [(cx - int(17 * s), hip_y - int(4 * s)),
              (cx + int(17 * s), hip_y - int(4 * s)),
              (cx + int(13 * s), hip_y + int(10 * s)),
              (cx - int(13 * s), hip_y + int(10 * s))]
    triad_blob(surf, BONE, pelvis,
               core_pts=[(cx - int(6 * s), hip_y), (cx + int(13 * s), hip_y - int(2 * s)),
                         (cx + int(12 * s), hip_y + int(9 * s)), (cx, hip_y + int(9 * s))],
               ow=max(1, int(1.6 * s)))

    # ribcage -- a WIDE+DEEP bronze barrel (broad-chested = the colossus read).
    # WHY enlarged: the top-heavy wedge must come from BRONZE shoulders, so the
    # barrel itself is the broadest, deepest central mass -- not the iron caps.
    rc_cx, rc_cy = cx, cy + int(3 * s)
    rc_w, rc_h = int(58 * s), int(50 * s)
    # broad bronze SHOULDERS at the top, tapering to a narrower waist -- the wedge
    # is built into the bone barrel itself, so bronze carries the top-heavy read.
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx - int(rc_w * 0.40), rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.40), rc_cy - rc_h // 2),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + int(rc_w * 0.30), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.30), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(5 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(4 * s)),
                         (rc_cx + int(rc_w * 0.34), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(3 * s), rc_cy - rc_h // 2 + int(5 * s)),
                          (rc_cx - int(6 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(8 * s), rc_cy + int(6 * s)),
                          (rc_cx - rc_w // 2 + int(3 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.8 * s)))
    # rib bands (curved dark grooves) -- the bone texture, kept subordinate
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(9 * s) + i * int(7 * s)
        bw = int(rc_w * (0.40 - i * 0.04))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(7 * s)),
                     (rc_cx, rc_cy + int(8 * s)), max(1, int(2 * s)))   # sternum

    # === iron SKULL-BELT across the hips -- a single THIN band (accent line) ==
    # WHY a thin band, not a plate: keeps iron mass off the torso so bronze
    # dominates; the belt reads as a furniture accent, with one tiny skull buckle.
    belt_y = hip_y - int(2 * s)
    belt = [(cx - int(18 * s), belt_y - int(3 * s)),
            (cx + int(18 * s), belt_y - int(3 * s)),
            (cx + int(18 * s), belt_y + int(3 * s)),
            (cx - int(18 * s), belt_y + int(3 * s))]
    triad_blob(surf, IRON, belt, ow=max(1, int(1.2 * s)))
    pygame.draw.line(surf, IRON_RIM, (cx - int(17 * s), belt_y - int(2 * s)),
                     (cx + int(17 * s), belt_y - int(2 * s)), max(1, int(1.2 * s)))

    # === ARMS -- both gripping the planted sword (two-armed, symmetric power) =
    arm_th = int(9 * s)
    for sgn in (-1, 1):
        shoulderx = rc_cx + sgn * int(20 * s)
        elbowx = rc_cx + sgn * int(20 * s)
        bone_limb(surf, (shoulderx, shoulder_y),
                  (elbowx, rc_cy + int(8 * s)),
                  (cx + sgn * int(7 * s), belt_y + int(2 * s)), arm_th, s)

    # === IRON CROSSGUARD + grip + pommel (over the stacked hands) ============
    # crossguard at the belt line -- a slim bar (kept narrow so iron stays minimal)
    cg = [(cx - int(15 * s), belt_y - int(3 * s)),
          (cx + int(15 * s), belt_y - int(3 * s)),
          (cx + int(13 * s), belt_y + int(3 * s)),
          (cx - int(13 * s), belt_y + int(3 * s))]
    triad_blob(surf, IRON, cg, ow=max(1, int(1.4 * s)))
    pygame.draw.line(surf, IRON_RIM, (cx - int(14 * s), belt_y - int(2 * s)),
                     (cx + int(14 * s), belt_y - int(2 * s)), max(1, int(1.4 * s)))
    # grip rising to the pommel just under the chin
    grip_top = cy - int(16 * s)
    pygame.draw.line(surf, INK, (cx, belt_y - int(3 * s)), (cx, grip_top), int(7 * s))
    pygame.draw.line(surf, IRON, (cx, belt_y - int(3 * s)), (cx, grip_top), int(4 * s))
    # bony hands stacked on the grip
    for hy in (belt_y - int(6 * s), cy - int(2 * s)):
        triad_circle(surf, BONE, (cx, hy), int(6 * s), ow=max(1, int(1.2 * s)), core=False)
        pygame.draw.line(surf, BONE_DD, (cx - int(5 * s), hy), (cx + int(5 * s), hy), max(1, int(1.2 * s)))
    # gilt pommel knob
    triad_circle(surf, GOLD, (cx, grip_top - int(2 * s)), int(5 * s), ow=max(1, int(1.2 * s)), core=False)
    pygame.draw.circle(surf, GOLD_BR, (cx - int(2 * s), grip_top - int(4 * s)), max(1, int(2 * s)))

    # === IRON PAULDRONS -- small SHOULDER CAPS, not outboard wings ============
    # WHY shrunk ~38% + pulled inboard: the broad-shoulder wedge now comes from the
    # bronze barrel; iron is reduced to two small caps that sit ON TOP of the bone
    # shoulder (overlapping it inboard, not flaring past it) so the bronze stays
    # the dominant pale field at 32px. Each still carries a skull-face + a short
    # forward spike (the lineage tell + crown-rake echo), but no torso plate.
    for sgn in (-1, 1):
        px = rc_cx + sgn * int(22 * s)
        py = shoulder_y - int(1 * s)
        pw, ph = int(15 * s), int(14 * s)
        # cap arcs over the bone shoulder; outer edge tucks just inside the barrel rim
        pauld = [(px - sgn * int(pw * 0.6), py - ph // 2),
                 (px + sgn * int(pw * 0.6), py - int(ph * 0.3)),
                 (px + sgn * int(pw * 0.6), py + int(ph * 0.55)),
                 (px - sgn * int(pw * 0.55), py + ph // 2)]
        triad_blob(surf, IRON, pauld,
                   core_pts=[(px, py),
                             (px + sgn * int(pw * 0.6), py - int(ph * 0.3)),
                             (px + sgn * int(pw * 0.6), py + int(ph * 0.55)),
                             (px, py + int(ph * 0.4))],
                   ow=max(1, int(1.6 * s)))
        # cool rim along the OUTER lit edge -- carries the cap on night sky
        pygame.draw.line(surf, IRON_RIM,
                         (px - sgn * int(pw * 0.6), py - ph // 2),
                         (px + sgn * int(pw * 0.6), py - int(ph * 0.3)), max(1, int(1.6 * s)))
        # a short forward shoulder spike (echoes the crown rake)
        sp_base = (px + sgn * int(pw * 0.2), py - ph // 2)
        sp_tip = (sp_base[0] + sgn * int(4 * s), py - int(ph * 0.5) - int(9 * s))
        spike = [(sp_base[0] - sgn * int(3 * s), sp_base[1] + int(2 * s)),
                 (sp_base[0] + sgn * int(3 * s), sp_base[1] + int(2 * s)),
                 sp_tip]
        triad_blob(surf, IRON, spike, ow=max(1, int(1.0 * s)))
        pygame.draw.line(surf, IRON_RIM, sp_base, sp_tip, max(1, int(1.2 * s)))
        # the pauldron skull-face medallion (lineage tell, ink sockets only)
        iron_skull(surf, px, py + int(1 * s), int(5 * s), s)

    # === SKULL HEAD -- chibi, scary-cute, bronze bone ========================
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    # cheek hollows
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.24))
    # big round sockets -- scary-cute, a DIM deep ember pin only (never the bright
    # CARN/CARN_BR): the brow gem must stay the single brightest red, so the eyes
    # read as dark embers far below it in value.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.02)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.28))
        pygame.draw.circle(surf, CARN_D, (ex + sgn * int(1 * s), ey + int(1 * s)), int(hr * 0.12))
    # heavy brow ridge (martial frown over the sockets)
    pygame.draw.line(surf, BONE_DD,
                     (head_c[0] - int(hr * 0.62), head_c[1] - int(hr * 0.18)),
                     (head_c[0] - int(hr * 0.1), head_c[1] - int(hr * 0.04)), max(1, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD,
                     (head_c[0] + int(hr * 0.62), head_c[1] - int(hr * 0.18)),
                     (head_c[0] + int(hr * 0.1), head_c[1] - int(hr * 0.04)), max(1, int(2.2 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.26)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.26)),
                         (head_c[0], head_c[1] + int(hr * 0.52))])
    # grinning tooth row
    my = head_c[1] + int(hr * 0.68)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))

    # === WAR-CROWN last (the top tell, owns the head's top silhouette) =======
    war_crown(surf, head_c[0], head_c[1] - int(hr * 0.78), int(hr * 1.9), s)


# -- the pillar mirror: a stacked-pauldron iron-and-bone column ---------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The pillar is built from the king's OWN forms: a tileable shaft of stacked
    bronze vertebra blocks banded with thin iron rings (the skull-belt motif),
    capped at the gap edge by a broad iron PAULDRON wedge + a forward spike + a
    carnelian rivet -- a fragment of the colossus's own shoulder armour. On-axis,
    symmetric, never top-heavy: the cap is shoulder-width, the shaft narrower.

    `cap` names the END that faces the GAP."""
    shaft_w = int(15 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    bead_pitch = int(22 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    flip = 0
    while y <= b1:
        bw = shaft_w
        # a bronze vertebra block
        bead = [(cx - bw, y + int(2 * s)),
                (cx - int(bw * 0.6), y - int(8 * s)),
                (cx + int(bw * 0.6), y - int(8 * s)),
                (cx + bw, y + int(2 * s)),
                (cx + int(bw * 0.6), y + int(12 * s)),
                (cx - int(bw * 0.6), y + int(12 * s))]
        triad_blob(surf, BONE, bead,
                   core_pts=[(cx, y - int(1 * s)), (cx + bw, y + int(2 * s)),
                             (cx + int(bw * 0.6), y + int(12 * s)), (cx, y + int(10 * s))],
                   sheen_pts=[(cx - bw, y + int(2 * s)), (cx - int(bw * 0.6), y - int(7 * s)),
                              (cx - int(bw * 0.2), y - int(4 * s)), (cx - int(bw * 0.7), y + int(5 * s))],
                   ow=max(1, int(1.4 * s)))
        # thin IRON band ring (the skull-belt motif) between every block
        pygame.draw.rect(surf, INK, (cx - bw - int(1 * s), y + int(9 * s), bw * 2 + int(2 * s), int(6 * s)))
        pygame.draw.rect(surf, IRON, (cx - bw, y + int(10 * s), bw * 2, int(4 * s)))
        pygame.draw.line(surf, IRON_RIM, (cx - bw + int(1 * s), y + int(10 * s)),
                         (cx + bw - int(1 * s), y + int(10 * s)), max(1, int(1.2 * s)))
        # alternating tiny iron skull on the ring (lineage tell, sparse)
        if flip % 2 == 0:
            iron_skull(surf, cx, y + int(12 * s), int(4 * s), s)
        flip += 1
        y += bead_pitch

    # === gap-edge cap: a broad iron PAULDRON wedge + forward spike + gem ======
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    sdir = 1 if cap == "bottom" else -1   # spike points toward the gap
    pw = int(20 * s)
    pauld = [(cx - pw, cap_y),
             (cx + pw, cap_y),
             (cx + int(pw * 0.7), cap_y + sdir * int(14 * s)),
             (cx - int(pw * 0.7), cap_y + sdir * int(14 * s))]
    triad_blob(surf, IRON, pauld,
               core_pts=[(cx, cap_y), (cx + pw, cap_y),
                         (cx + int(pw * 0.7), cap_y + sdir * int(14 * s)), (cx, cap_y + sdir * int(12 * s))],
               ow=max(1, int(1.8 * s)))
    pygame.draw.line(surf, IRON_RIM, (cx - pw + int(2 * s), cap_y + sdir * int(1 * s)),
                     (cx + pw - int(2 * s), cap_y + sdir * int(1 * s)), max(1, int(2 * s)))
    # forward spike at the dead centre, pointing into the gap
    tip = (cx, cap_y + sdir * int(30 * s))
    spike = [(cx - int(6 * s), cap_y + sdir * int(10 * s)),
             (cx + int(6 * s), cap_y + sdir * int(10 * s)), tip]
    triad_blob(surf, IRON, spike, ow=max(1, int(1.2 * s)))
    pygame.draw.line(surf, IRON_RIM, (cx - int(4 * s), cap_y + sdir * int(11 * s)), tip, max(1, int(1.4 * s)))
    # carnelian rivet gem on the cap (the thin accent, echoing the brow gem)
    gx, gy = cx, cap_y + sdir * int(4 * s)
    pygame.draw.circle(surf, INK, (gx, gy), int(5 * s))
    pygame.draw.circle(surf, CARN, (gx, gy), int(4 * s))
    pygame.draw.circle(surf, CARN_HOT, (gx - int(1 * s), gy - int(1 * s)), max(1, int(1.6 * s)))


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_warlord(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_font(size, bold=True):
    # FONT path FIVE levels up from this script; SysFont fallback if missing.
    here = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.normpath(os.path.join(here, "..", "..", "..", "..", "..",
                                       "game", "assets", "LiberationSans-Bold.ttf"))
    if os.path.exists(fp):
        return pygame.font.Font(fp, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def main():
    W, H = 1010, 820
    font_big = load_font(30)
    font = load_font(17)
    font_sm = load_font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("CARNELIAN WARLORD", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "armoured colossus  ·  bronze-bone-dominant · forward-spiked iron war-crown · planted greatsword · round 2",
        True, LABEL_DIM), (330, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 180, 232, 1.95)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature -- hero", True, LABEL), (108, 566))
    sheet.blit(font_sm.render("top-heavy WEDGE built from a WIDE+DEEP bronze barrel (broad bone shoulders),", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("tapering to a planted base. VERTICAL greatsword down the centre, hands on grip.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Iron shrunk to two SMALL shoulder caps + war-crown + a thin belt line. ONE red:", True, LABEL_DIM), (14, 622))
    sheet.blit(font_sm.render("the carnelian brow gem (single brightest pixel). Bronze out-masses iron at 32px.", True, LABEL_DIM), (14, 638))

    # === (b) PILLAR assembled -- mirrored, clean tileable shaft ===============
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar -- shoulder-column", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("bronze vertebra blocks + iron skull-belt rings", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("= shaft; an iron pauldron wedge + forward spike", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("+ carnelian rivet caps each gap edge (mirrored).", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips + blackout + palette =============================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 414))
    sheet.blit(font.render("True 32px gameplay chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_warlord(big, 48 * SS, 50 * SS, (32 / 130.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 130, 130), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 130, 130), 1)
    sheet.blit(chip, (panel_x + 20 + 17, day_y + 17))
    sheet.blit(font_sm.render("32px day", True, LABEL), (panel_x + 20, day_y + 134))

    night_y = day_y
    nx = panel_x + 168
    vgrad(sheet, (nx, night_y, 130, 130), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (nx, night_y, 130, 130), 1)
    sheet.blit(chip, (nx + 17, night_y + 17))
    sheet.blit(font_sm.render("32px night", True, LABEL_DIM), (nx, night_y + 134))

    # blackout silhouette proof (does the broad wedge + centre sword read solid?)
    blk_y = 300
    bx = panel_x + 20
    pygame.draw.rect(sheet, (150, 154, 162), (bx, blk_y, 90, 130))
    pygame.draw.rect(sheet, INK, (bx, blk_y, 90, 130), 1)
    # blacken the hero alpha onto the grey
    sil_big = pygame.Surface((96 * SS, 130 * SS), pygame.SRCALPHA)
    draw_warlord(sil_big, 48 * SS, 60 * SS, (40 / 130.0) * SS)
    sil = pygame.transform.smoothscale(sil_big, (96, 130))
    mask = pygame.mask.from_surface(sil)
    sil_flat = mask.to_surface(setcolor=(18, 18, 22, 255), unsetcolor=(0, 0, 0, 0))
    sheet.blit(sil_flat, (bx - 3, blk_y))
    sheet.blit(font_sm.render("blackout", True, LABEL), (bx, blk_y + 134))

    # palette strip (incl. ivory ref to PROVE bronze reads warmer than ivory)
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 130, 300))
    swatches = [
        (BONE, "bronze bone"), (BONE_D, "bone shade"),
        (IVORY_REF, "(ivory ref)"), (IRON, "dark iron"),
        (IRON_RIM, "iron rim"), (CARN, "carnelian"),
        (CARN_HOT, "gem focal"), (STEEL, "blade steel"),
        (GOLD, "gilt"), (INK, "ink"),
    ]
    sxp, syp = panel_x + 130, 328
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 96
        ry = syp + row * 22
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 16, 16))
        pygame.draw.rect(sheet, c, (rx, ry, 14, 14))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 20, ry + 1))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat saturated fills · hard ink keyline (28,22,30) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    # ---- self-check (NON-fatal: PNG is already written above; print PASS/FAIL
    #      so a failed gate never crashes the render) -------------------------
    results = []

    def check(name, ok, detail=""):
        results.append((name, ok, detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {detail}")

    # bronze bone must read warmer (R-B larger) and lower-value than the ivory ref
    bone_warm = BONE[0] - BONE[2]
    ivory_warm = IVORY_REF[0] - IVORY_REF[2]
    bone_val = sum(BONE) / 3
    ivory_val = sum(IVORY_REF) / 3
    check("bronze warmer than ivory", bone_warm > ivory_warm + 30,
          f"R-B bronze={bone_warm} ivory={ivory_warm}")
    check("bronze grubbier (lower value)", bone_val < ivory_val - 20,
          f"value bronze={bone_val:.0f} ivory={ivory_val:.0f}")

    # GATE: bronze must OUT-MASS iron on the true 32px chip
    chip_big = pygame.Surface((96, 96), pygame.SRCALPHA)
    chip_big.blit(chip, (0, 0))
    bone_px = iron_px = red_px = 0
    red_peak = (0, None)   # brightest red pixel (value, xy) -> must be near the brow gem
    for yy in range(96):
        for xx in range(96):
            r, g, b, a = chip_big.get_at((xx, yy))
            if a < 40:
                continue
            val = (r + g + b) / 3
            warm = r - b
            # Ink keyline + deep cores + the cool STEEL blade belong to NEITHER
            # coloured armour mass -- excluding them isolates the real bone-vs-iron
            # contest. Dark (<78) = ink/core/socket; bright cool blue = steel blade
            # / cool rim. What remains is genuine bone fill vs iron plate, split by
            # warmth: warm -> bronze bone, cool mid -> dark iron.
            if val < 78:
                pass
            elif warm >= 22:
                bone_px += 1
            elif b > 130 and val > 120:
                pass
            else:
                iron_px += 1
            # a clearly RED pixel: red dominant over both green and blue
            if r > 130 and r - g > 50 and r - b > 40:
                red_px += 1
                if r > red_peak[0]:
                    red_peak = (r, (xx, yy))
    check("GATE bronze out-masses iron @32px", bone_px > iron_px,
          f"bone~{bone_px}px iron~{iron_px}px")

    # ONE red focal: the red is a small, single cluster, and its brightest pixel
    # sits in the upper head band (the brow gem), not scattered across the body
    one_focal = red_px <= 40 and red_peak[1] is not None and red_peak[1][1] < 48
    check("ONE red focal (brow gem)", one_focal,
          f"red_px~{red_px} brightest_red_y={red_peak[1][1] if red_peak[1] else 'none'}")

    # broad-wedge read: measure against the figure's ACTUAL bounding box (the
    # 32px chip does not fill the 96px frame), comparing the shoulder third vs
    # the planted-base third.
    smask = pygame.mask.from_surface(chip)
    filled_rows = [y for y in range(96) if any(smask.get_at((x, y)) for x in range(96))]
    y0, y1 = (filled_rows[0], filled_rows[-1]) if filled_rows else (0, 95)
    span = max(1, y1 - y0)
    cols_with = [x for x in range(96) if any(smask.get_at((x, y)) for y in range(96))]
    cx_mask = (cols_with[0] + cols_with[-1]) // 2 if cols_with else 48

    def row_width(y):
        xs = [x for x in range(96) if smask.get_at((x, y))]
        return (max(xs) - min(xs)) if len(xs) > 1 else 0
    top_w = max(row_width(y) for y in range(y0 + int(span * 0.18), y0 + int(span * 0.45)))
    bot_w = max(row_width(y) for y in range(y0 + int(span * 0.60), y0 + int(span * 0.92)))
    check("top-heavy wedge (broad shoulders)", top_w > bot_w,
          f"top~{top_w}px bot~{bot_w}px")

    # vertical centre-line sword: a tall connected run of fill on the centre column
    col_fill = [y for y in range(96)
                if any(smask.get_at((x, y)) for x in range(cx_mask - 2, cx_mask + 3))]
    check("vertical planted-sword spine", len(col_fill) > int(span * 0.72),
          f"centre rows {len(col_fill)} of span {span}")

    passed = sum(1 for _, ok, _ in results if ok)
    print(f"SELF-CHECK: {passed}/{len(results)} PASSED",
          "-- ALL PASS" if passed == len(results) else "-- SOME FAILED")


if __name__ == "__main__":
    main()
