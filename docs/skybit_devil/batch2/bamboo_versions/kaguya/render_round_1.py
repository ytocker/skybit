"""
Round-1 concept renderer for KAGUYA — moon-child in the split culm
(bamboo-versions set, concept #5). Headless Pygame; ELEVATED pipeline
(supersample SS=6 -> smoothscale) so the vesica aperture + stepped moon-rings
stay crisp at downscale. Keeps the shipped house grammar: flat fills, hard
1-2px ink keyline, dark-core -> flat-fill -> top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE pushed EPIC; procedural-only
(NO gradients, NO PNGs, NO soft raster halos).

WHY this is the SPLIT-STALK-WITH-INNER-FIGURE of the brood: the roster spreads
five distinct silhouette KINDs; Kaguya is the ONLY straight split-stalk with an
inner figure. The AD pins are binding and baked in here:

  * The vesica/almond SPLIT + its glow is the DOMINANT 32px read — a luminous
    aperture bleeding light into the gap, NOT a creature in a tube. The split is
    cut wide and centred; the moon-glow rings are the brightest, largest single
    mark, so the blacked-out chip reads "split stalk pouring light," never "bug
    in a pipe."
  * The outer culm is held dead STRAIGHT and SYMMETRIC — NO coil. This is the
    explicit anti-Take-Ryu pin: Take-Ryu is a live S-coil with a cranial head;
    Kaguya is a rigid vertical pillar that has cracked open. The two never
    collide at 32px.
  * The pearl base is pushed COOLER/PALER than spec so its value reads clearly
    LIGHTER than Take-Ryu's saturated jade — pearl-culm against pale-jade shade,
    never the deep node-green of the dragon.
  * The moon-glow is FLAT STEPPED concentric rings (no gradient, no soft raster
    halo) — discrete poured polygons, hard-edged, the house procedural law.
  * The gold is a SOFT STEPPED HALO — the deliberate foil to Madake's hard
    metallic gold-leaf cracks — so the two gold accents never collide.

WHY the luminous culm IS the pillar: glowing pale node-segments tile as the
repeatable shaft; the split-open glowing aperture (the moon-child tucked at the
gap, light radiating into the gap) is the creature-derived gap-edge cap.
Symmetric stalk, bottom-rooted — the cleanest mirror in the set.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief, section 5) ---------------------------------
# Pearl culm pushed COOLER/PALER than spec so its value sits clearly LIGHTER
# than Take-Ryu's saturated jade. The glow accent is a NEW pale gold-white hue,
# held clear of Kitsune mint and Yurei cyan.
CULM      = (214, 228, 210)   # pearl-culm base (the dominant pale fill)
CULM_D    = (150, 188, 158)   # pale-jade shade / dark-core groove
CULM_DD   = (110, 150, 124)   # deepest culm hollow (split inner edge, node rings)
RIM       = (192, 206, 232)   # cool moon-blue rim
SHEEN     = (252, 250, 236)   # hottest culm sheen
GLOW      = (244, 238, 196)   # pale gold-white MOON-glow (the SOLE glow accent)
GLOW_BR   = (250, 246, 222)   # hotter inner moon-ring
GLOW_HOT  = (255, 254, 246)   # hottest moon core (near-white)
GOLD      = (224, 196, 120)   # gold hair-tie / soft stepped gold halo ring
GOLD_D    = (182, 150,  82)   # gold shade
SKIN      = (238, 232, 224)   # child-pale skin
SKIN_D    = (200, 188, 184)   # skin shade
INK       = ( 30,  32,  34)   # hard ink keyline

BG        = ( 70,  78,  92)   # neutral cool review backdrop
PANEL     = ( 54,  62,  76)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (190, 196, 208)


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


# -- the vesica / almond aperture (THE dominant read) -------------------------
def vesica_pts(cx, cy, half_w, half_h, n=14, t=1.0):
    """A symmetric pointed-oval (vesica/almond) outline as a polygon, scalable
    inward by `t` so concentric stepped copies can be poured for the moon-rings.
    WHY a vesica and not a plain ellipse: the split in a cut culm is a pointed
    almond — sharp at top and bottom where the two culm halves still meet, fat
    in the middle. That pointed-oval read is the silhouette tell that says
    'a stalk has cracked OPEN', not 'a porthole'."""
    pts = []
    hw, hh = half_w * t, half_h * t
    for i in range(n + 1):
        # parametric pointed oval: cos for the vertical axis, sin shaped so the
        # ends pinch to a point (|sin|^0.7 fattens the belly, keeps tips sharp)
        a = math.pi * i / n - math.pi / 2.0
        y = math.sin(a) * hh
        x = math.cos(a) * hw
        pts.append((cx + x, cy + y))
    # mirror back down the other side
    for i in range(n - 1, 0, -1):
        a = math.pi * i / n - math.pi / 2.0
        y = math.sin(a) * hh
        x = -math.cos(a) * hw
        pts.append((cx + x, cy + y))
    return pts


def moon_aperture(surf, cx, cy, half_w, half_h, s, child=True):
    """The split-open glowing APERTURE — the DOMINANT mark. A pointed vesica
    cut through the culm, filled with FLAT STEPPED concentric moon-rings (NO
    gradient, NO soft halo) bleeding pale gold-white light, with a small curled
    glowing moon-child tucked inside. WHY stepped rings: house procedural law
    forbids raster halos — the radiance is built from discrete hard-edged
    poured polygons, each a step paler toward the core, so the glow reads as
    deliberate stylised light, not a blurred bloom."""
    # ink the aperture rim hard so the split edge is a confident keyline
    rim = vesica_pts(cx, cy, half_w, half_h, t=1.0)
    pygame.draw.polygon(surf, INK, rim)
    # CULM_DD inner lip — the cut bamboo wall, darkest, frames the light
    lip = vesica_pts(cx, cy, half_w, half_h, t=0.92)
    pygame.draw.polygon(surf, CULM_DD, lip)

    # --- FLAT STEPPED concentric moon-rings (the radiance) -------------------
    # each step is a smaller vesica poured a notch paler; hard edges only.
    ring_steps = (
        (0.84, lerp(GLOW, INK, 0.18)),   # outer dim ring (light just born)
        (0.70, GLOW),                    # the pale gold-white body of the glow
        (0.54, GLOW_BR),                 # hotter inner ring
        (0.38, GLOW_HOT),                # hottest near-white core field
    )
    for t, col in ring_steps:
        pygame.draw.polygon(surf, col, vesica_pts(cx, cy, half_w, half_h, t=t))

    # --- SOFT STEPPED GOLD HALO arcs (foil to Madake's hard metallic gold) ---
    # a few concentric gold ARC ticks hugging the aperture rim — stepped, soft
    # in feel (graded value, rounded caps) but still hard-edged polygons, never
    # a raster glow. This is the calm moon-gold, deliberately NOT metallic.
    for k, gt in enumerate((0.96, 1.06, 1.16)):
        col = lerp(GOLD, GLOW, 0.25 + k * 0.18)
        ga = vesica_pts(cx, cy, half_w * gt, half_h * gt, t=1.0)
        pygame.draw.polygon(surf, col, ga, max(1, int(2.0 * s)))

    if child:
        # --- the curled glowing moon-child, tucked low in the aperture -------
        # WHY small & curled: she is a NEWBORN found in the culm (chibi: big
        # head, tiny tucked body). Kept small so the GLOW dominates the read at
        # 32px — she is the sweet secret inside the light, the scary-CUTE core,
        # not a creature filling a tube.
        chr_ = half_w * 0.46
        chcx = cx
        chcy = cy + half_h * 0.20
        # tucked body — a small curled pale crescent under the head
        body = [(chcx - chr_ * 1.05, chcy + chr_ * 0.30),
                (chcx - chr_ * 0.55, chcy + chr_ * 1.30),
                (chcx + chr_ * 0.55, chcy + chr_ * 1.30),
                (chcx + chr_ * 1.05, chcy + chr_ * 0.30),
                (chcx + chr_ * 0.50, chcy + chr_ * 0.10),
                (chcx - chr_ * 0.50, chcy + chr_ * 0.10)]
        triad_blob(surf, SKIN, body,
                   core_pts=[(chcx + chr_ * 0.10, chcy + chr_ * 0.40),
                             (chcx + chr_ * 0.95, chcy + chr_ * 0.34),
                             (chcx + chr_ * 0.45, chcy + chr_ * 1.20),
                             (chcx, chcy + chr_ * 0.90)],
                   sheen_pts=[(chcx - chr_ * 0.90, chcy + chr_ * 0.34),
                              (chcx - chr_ * 0.30, chcy + chr_ * 0.30),
                              (chcx - chr_ * 0.40, chcy + chr_ * 0.90),
                              (chcx - chr_ * 0.80, chcy + chr_ * 0.80)],
                   ow=max(1, int(1.2 * s)))
        # big chibi head
        triad_circle(surf, SKIN, (chcx, int(chcy - chr_ * 0.40)), int(chr_ * 0.92),
                     ow=max(1, int(1.4 * s)), sheen=True, core=True)
        # gold hair-tie topknot (the one gold focal on the child)
        triad_circle(surf, GOLD, (chcx, int(chcy - chr_ * 1.16)), max(2, int(chr_ * 0.30)),
                     ow=max(1, int(1.0 * s)), sheen=True, core=False)
        # two calm closed-eye arcs + a tiny serene mouth (scary-CUTE: serene,
        # otherworldly-still, eyes shut as if just woken from the moon)
        eh = int(chr_ * 0.40)
        ey = int(chcy - chr_ * 0.42)
        for sg in (-1, 1):
            ex = int(chcx + sg * chr_ * 0.34)
            pygame.draw.arc(surf, INK,
                            (ex - eh // 2, ey - eh // 2, eh, eh),
                            math.radians(200), math.radians(340), max(1, int(1.6 * s)))
        pygame.draw.line(surf, lerp(SKIN_D, INK, 0.4),
                         (int(chcx - chr_ * 0.12), int(chcy + chr_ * 0.02)),
                         (int(chcx + chr_ * 0.12), int(chcy + chr_ * 0.02)),
                         max(1, int(1.4 * s)))
        # faint rosy cheek ticks (cold pale cheeks — a moon child)
        for sg in (-1, 1):
            cxp = int(chcx + sg * chr_ * 0.62)
            pygame.draw.circle(surf, lerp(SKIN, GOLD, 0.3),
                               (cxp, int(chcy - chr_ * 0.18)), max(1, int(chr_ * 0.12)))


# -- a single STRAIGHT pale culm node-segment (the repeat band) ---------------
def culm_segment(surf, cx, top_y, h, half_w, s, glow_seam=True):
    """One STRAIGHT symmetric pale node-segment: a flat vertical bamboo barrel
    with a raised node RING at its top, a dark-core groove on the body-right, a
    top-left rim-sheen rail, and a cool moon-blue edge accent. WHY dead straight
    & symmetric: the anti-Take-Ryu pin — the outer culm must read as a rigid
    vertical pillar that has cracked open, never a coil. Each segment is its own
    closed shape so the shaft tiles cleanly top<->bottom."""
    # the barrel body — straight parallel sides, faint node bulge at the ring
    bulge = half_w * 0.10
    body = [(cx - half_w, top_y + int(4 * s)),
            (cx - half_w - bulge, top_y),                 # node-ring lip (left)
            (cx + half_w + bulge, top_y),                 # node-ring lip (right)
            (cx + half_w, top_y + int(4 * s)),
            (cx + half_w, top_y + h),
            (cx - half_w, top_y + h)]
    triad_blob(surf, CULM, body,
               core_pts=[(cx + int(half_w * 0.20), top_y + int(4 * s)),
                         (cx + half_w, top_y + int(4 * s)),
                         (cx + half_w, top_y + h),
                         (cx + int(half_w * 0.20), top_y + h)],
               sheen_pts=[(cx - half_w, top_y + int(5 * s)),
                          (cx - int(half_w * 0.55), top_y + int(5 * s)),
                          (cx - int(half_w * 0.55), top_y + h),
                          (cx - half_w, top_y + h)],
               ow=max(1, int(1.6 * s)))
    # cool moon-blue rim rail down the left edge (the cold celestial accent)
    pygame.draw.line(surf, RIM,
                     (cx - half_w + int(2 * s), top_y + int(6 * s)),
                     (cx - half_w + int(2 * s), top_y + h - int(2 * s)),
                     max(1, int(1.6 * s)))
    # node-ring groove (the dark seam where segments meet)
    pygame.draw.line(surf, CULM_DD,
                     (cx - half_w - bulge, top_y + int(2 * s)),
                     (cx + half_w + bulge, top_y + int(2 * s)),
                     max(2, int(3 * s)))
    # raised node ring highlight just under the groove
    pygame.draw.line(surf, SHEEN,
                     (cx - half_w, top_y + int(6 * s)),
                     (cx + half_w, top_y + int(6 * s)),
                     max(1, int(1.4 * s)))
    if glow_seam:
        # a faint pale gold-white glow seam leaking from the node joint — hints
        # the whole culm is luminous, not just the split (FLAT, hard-edged).
        pygame.draw.line(surf, lerp(GLOW, CULM, 0.45),
                         (cx - int(half_w * 0.5), top_y + int(3 * s)),
                         (cx + int(half_w * 0.5), top_y + int(3 * s)),
                         max(1, int(1.2 * s)))


# -- the split-stalk hero ------------------------------------------------------
def draw_kaguya(surf, cx, cy, s):
    """The straight luminous culm cracked open: a rigid symmetric pale bamboo
    stalk of stacked node-segments, split down the middle by a big glowing
    vesica aperture (the dominant read) with the curled moon-child inside, light
    bleeding out into the world. `s` = unit scale around a ~132-unit figure.
    Drawn back-to-front: outer culm segments -> the cut split walls -> the
    glowing aperture + child last so the LIGHT owns the centre."""

    half_w = int(22 * s)
    seg_h = int(26 * s)
    # the stalk spans from above to below the aperture; segments above + below.
    top_y = cy - int(64 * s)
    bot_y = cy + int(64 * s)

    # === UPPER culm segments (above the split) ===============================
    y = top_y
    while y < cy - int(34 * s):
        culm_segment(surf, cx, y, seg_h, half_w, s)
        y += seg_h

    # === LOWER culm segments (below the split) ===============================
    y = cy + int(34 * s)
    while y < bot_y:
        culm_segment(surf, cx, y, seg_h, half_w, s)
        y += seg_h

    # === the SPLIT — two culm halves peeling apart around the aperture =======
    # WHY peeling halves: the silhouette must say 'cracked OPEN'. The two culm
    # walls bow slightly outward at the split mid-line and meet at sharp points
    # top and bottom (the vesica). Each wall is triad-lit as its own form so the
    # split reads as thick bamboo wall framing the light, never a flat hole.
    ap_hw = int(15 * s)         # aperture half-width (fat belly of the vesica)
    ap_hh = int(34 * s)         # aperture half-height (tall almond)
    for sgn in (-1, 1):
        wall = [(cx + sgn * half_w, cy - int(34 * s)),          # top outer
                (cx + sgn * half_w, cy + int(34 * s)),          # bottom outer
                (cx + sgn * ap_hw * 0.34, cy + int(34 * s)),    # bottom inner
                (cx + sgn * ap_hw, cy),                         # belly inner (bowed out)
                (cx + sgn * ap_hw * 0.34, cy - int(34 * s))]    # top inner
        triad_blob(surf, CULM, wall,
                   core_pts=[(cx + sgn * int(half_w * 0.30), cy - int(30 * s)),
                             (cx + sgn * half_w, cy - int(30 * s)),
                             (cx + sgn * half_w, cy + int(30 * s)),
                             (cx + sgn * int(half_w * 0.30), cy + int(30 * s))]
                             if sgn > 0 else None,
                   sheen_pts=[(cx + sgn * half_w, cy - int(28 * s)),
                              (cx + sgn * int(half_w * 0.62), cy - int(28 * s)),
                              (cx + sgn * int(half_w * 0.62), cy + int(28 * s)),
                              (cx + sgn * half_w, cy + int(28 * s))]
                              if sgn < 0 else None,
                   ow=max(1, int(1.6 * s)))
        # cool moon-blue rim on the outer edge of each wall (held straight)
        pygame.draw.line(surf, RIM,
                         (cx + sgn * (half_w - int(2 * s)), cy - int(32 * s)),
                         (cx + sgn * (half_w - int(2 * s)), cy + int(32 * s)),
                         max(1, int(1.6 * s)))

    # === the glowing APERTURE + child — drawn LAST, owns the centre ==========
    moon_aperture(surf, cx, cy, ap_hw, ap_hh, s, child=True)


# -- the luminous culm -> pillar mirror ---------------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The luminous culm IS the pillar: glowing straight pale node-segments tile
    as the shaft; the split-open glowing aperture (moon-child tucked at the gap,
    light radiating INTO the gap) is the gap-edge cap. Symmetric stalk,
    bottom-rooted. `cap` names the END that faces the GAP."""
    half_w = int(20 * s)
    seg_h = int(26 * s)
    cap_room = int(58 * s)

    if cap == "bottom":
        seg_top, seg_bot = top + int(2 * s), bot - cap_room
        ap_cy = bot - int(32 * s)
    else:
        seg_top, seg_bot = top + cap_room, bot - int(2 * s)
        ap_cy = top + int(32 * s)

    # === straight tiling node-segments (the shaft) ===========================
    y = seg_top
    while y < seg_bot:
        culm_segment(surf, cx, y, min(seg_h, seg_bot - y), half_w, s)
        y += seg_h

    # === gap-edge cap: the split-open glowing aperture =======================
    # WHY the aperture is the cap: the AD pin says the split + glow is the
    # dominant read and the brief names the aperture itself as the gap-edge cap
    # — so the brightest thing in the pillar sits right at the gap, bleeding
    # light into it. The split is cut into the final segment facing the gap.
    ap_hw = int(13 * s)
    ap_hh = int(28 * s)
    # two short split walls peeling around the aperture at the cap end
    for sgn in (-1, 1):
        wall = [(cx + sgn * half_w, ap_cy - int(28 * s)),
                (cx + sgn * half_w, ap_cy + int(28 * s)),
                (cx + sgn * ap_hw * 0.34, ap_cy + int(28 * s)),
                (cx + sgn * ap_hw, ap_cy),
                (cx + sgn * ap_hw * 0.34, ap_cy - int(28 * s))]
        triad_blob(surf, CULM, wall,
                   core_pts=[(cx + sgn * int(half_w * 0.30), ap_cy - int(24 * s)),
                             (cx + sgn * half_w, ap_cy - int(24 * s)),
                             (cx + sgn * half_w, ap_cy + int(24 * s)),
                             (cx + sgn * int(half_w * 0.30), ap_cy + int(24 * s))]
                             if sgn > 0 else None,
                   ow=max(1, int(1.4 * s)))
        pygame.draw.line(surf, RIM,
                         (cx + sgn * (half_w - int(2 * s)), ap_cy - int(26 * s)),
                         (cx + sgn * (half_w - int(2 * s)), ap_cy + int(26 * s)),
                         max(1, int(1.4 * s)))

    if cap == "bottom":
        moon_aperture(surf, cx, ap_cy, ap_hw, ap_hh, s, child=True)
    else:
        # mirror vertically so the aperture + child point the right way at the
        # gap, proving the clean top<->bottom mirror of the symmetric stalk.
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        moon_aperture(tmp, cx, surf.get_height() - ap_cy, ap_hw, ap_hh, s, child=True)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, 0))


# -- compose the review sheet -------------------------------------------------
SS = 6


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 900
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("KAGUYA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "moon-child in the split culm  ·  STRAIGHT symmetric culm · vesica SPLIT + stepped moon-rings (dominant) · curled moon-child · round 1",
        True, LABEL_DIM), (190, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_kaguya(big, 178 * SS, 235 * SS, 1.95 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("STRAIGHT symmetric pale culm cracked open by a glowing VESICA aperture —", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("flat stepped concentric moon-rings (no gradient/halo), soft stepped gold halo arcs.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Curled chibi moon-child tucked inside; cooler/paler pearl culm (lighter than jade).", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable shaft ================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (58, 56, 68), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — luminous culm", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("straight glowing node-segments = shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("the split-open glowing aperture (child at", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("the gap, light into the gap) caps each edge — mirror visible", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_kaguya(big, 48 * SS, 50 * SS, (32 / 132.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blacked-out 32px silhouette — the SPLIT-read TEST: must read as a STRAIGHT
    # stalk with a pinched vesica notch (the split), never a coil / a creature.
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_kaguya(big, 48 * SS, 50 * SS, (32 / 132.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
        return sil

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 220), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("STRAIGHT stalk, pinched vesica split", True, LABEL_DIM), (sx + 104, sil_y + 48))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
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

    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 636))
    swatches = [
        (CULM, "pearl-culm"), (CULM_D, "pale-jade sh"),
        (GLOW, "moon-glow"), (GLOW_HOT, "moon core"),
        (RIM, "moon-blue rim"), (GOLD, "gold hair-tie"),
        (SKIN, "child skin"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 664
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 850, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (30,32,34) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-CUTE · procedural-only · stepped moon-rings (NO halo).",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
