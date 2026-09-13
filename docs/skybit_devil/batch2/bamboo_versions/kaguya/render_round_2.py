"""
Round-2 concept renderer for KAGUYA — moon-child in the split culm
(bamboo-versions set, concept #5). Headless Pygame; ELEVATED pipeline
(supersample SS=6 -> smoothscale) so the vesica aperture + stepped moon-rings
stay crisp at downscale. Keeps the shipped house grammar: flat fills, hard
1-2px ink keyline, dark-core -> flat-fill -> top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE pushed EPIC; procedural-only
(NO gradients, NO PNGs, NO soft raster halos).

WHY round 2 (the AD ITERATE punch list, all baked in):

  1. THE GLOW IS REBUILT AS TRUE FLAT STEPPED RINGS. Round 1's halo was a near-
     continuous soft falloff (closely-spaced vesica steps + concentric gold arc
     ticks that AA-feathered into a bloom). Here the radiance is 5 HARD concentric
     vesica BANDS, each a single FLAT poured polygon with a hard 1px boundary to
     the next — outer pale-jade ring -> moon-glow (244,238,196) -> paler step ->
     hot ring -> near-white core. The step COUNT is deliberately small and the
     value jumps are large so you can COUNT the plateaus by eye. The gold-arc
     ticks (the raster-feeling part of round 1) are GONE; the gold now lives only
     as the child's hair-tie + one stepped gold band, never as feathered arcs.

  2. THE APERTURE WINS AT 32px. The vesica now occupies ~60% of the culm height
     and pushes to ~88% of culm width (round 1 sat at a thin mid-shaft sliver).
     The core is brightened one more step (pure near-white moon core enlarged) so
     squinting at the day chip the GLOW — not the shaft — is the first read.

  3. THE GLOW BLEEDS INTO THE GAP. The outermost 1-2 stepped rings now extend a
     few px BEYOND the culm silhouette (still flat, still hard-edged) so the
     gap-edge cap reads as a luminous aperture RADIATING outward, not a capped
     porthole. Round 1 contained the whole glow inside the culm width.

  4. THE MOON-CHILD IS DEMOTED AT SMALL SCALE. She stays crisp in the HERO, but
     at 32px she collapses to a tiny dark seed inside the bright aperture — pixels
     are spent on glow contrast, not face legibility. The figure is the close-
     inspection reward; the glow carries the read.

  5. EVERY GLOW EDGE IS HARDENED with the 1px ink/keyed boundary. The gold stays a
     SOFT STEPPED HALO in HUE/ROLE (warm, diffuse-FEELING via stepping, foil to
     Madake's hard metallic gold) but is never raster-blurred.

KEEP (AD said these work): the straight symmetric culm (blackout = pinched vesica
in a STRAIGHT stalk — the headline anti-Take-Ryu win, protected); the pearl-culm
value (clearly paler/cooler than Take-Ryu jade); the chibi moon-child in the hero
(big-head/tiny-shoulders + gold hair-tie); the gap-cap mirror + node-ring cadence
(clean, tileable, bottom-rooted).

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
# --- the 5 FLAT stepped moon-ring plateaus (outer -> core). Large value jumps,
# so the steps are COUNTABLE by eye and never read as a smooth falloff. The
# outer band is a pale-jade-tinted glow (light just born in the culm wall); the
# core is pushed near-white and HOT so it wins the 32px read.
GLOW_RING0 = (196, 222, 188)  # outer pale-jade glow ring (bleeds into the gap)
GLOW       = (244, 238, 196)  # moon-glow body — pale gold-white (the SOLE glow hue)
GLOW_BR    = (250, 244, 214)  # paler step
GLOW_HOT   = (254, 252, 238)  # hot ring
GLOW_CORE  = (255, 255, 252)  # near-white moon core (the brightest single mark)
GOLD      = (224, 196, 120)   # gold hair-tie / one soft stepped gold halo band
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
def vesica_pts(cx, cy, half_w, half_h, n=18):
    """A symmetric pointed-oval (vesica/almond) outline as a polygon.
    WHY a vesica and not a plain ellipse: the split in a cut culm is a pointed
    almond — sharp at top and bottom where the two culm halves still meet, fat
    in the middle. That pointed-oval read is the silhouette tell that says
    'a stalk has cracked OPEN', not 'a porthole'."""
    pts = []
    for i in range(n + 1):
        a = math.pi * i / n - math.pi / 2.0
        y = math.sin(a) * half_h
        x = math.cos(a) * half_w
        pts.append((cx + x, cy + y))
    for i in range(n - 1, 0, -1):
        a = math.pi * i / n - math.pi / 2.0
        y = math.sin(a) * half_h
        x = -math.cos(a) * half_w
        pts.append((cx + x, cy + y))
    return pts


def moon_aperture(surf, cx, cy, half_w, half_h, s, child=True):
    """The split-open glowing APERTURE — the DOMINANT mark. A big pointed vesica
    cut through the culm, filled with FIVE FLAT STEPPED concentric moon-ring
    BANDS (NO gradient, NO soft halo, NO feathered arcs). Each band is a single
    poured polygon a notch paler toward a near-white core; the value jumps are
    LARGE so the plateaus are countable by eye. The outermost 1-2 bands are
    drawn one size UP from the cut so the glow bleeds a few px past the culm
    silhouette into the gap — a luminous aperture radiating outward.

    `half_w`/`half_h` are the CUT vesica's half-extents (the bamboo-wall hole).
    The glow bands are scaled in absolute px (not by `t`) so the step widths are
    even and readable rather than crowding toward the tips."""

    # --- bleed rings: drawn FIRST and LARGER than the cut so they spill past
    # the culm wall into the gap. Still flat, still hard-edged. ----------------
    bleed1 = int(8 * s)   # outermost spill (pale-jade glow, dimmest)
    bleed0 = int(4 * s)   # second spill (moon-glow body)
    pygame.draw.polygon(surf, INK,
                        vesica_pts(cx, cy, half_w + bleed1 + int(1.4 * s),
                                   half_h + bleed1 + int(1.4 * s)))
    pygame.draw.polygon(surf, GLOW_RING0,
                        vesica_pts(cx, cy, half_w + bleed1, half_h + bleed1))
    pygame.draw.polygon(surf, GLOW,
                        vesica_pts(cx, cy, half_w + bleed0, half_h + bleed0))

    # ink the aperture rim hard so the cut split edge is a confident keyline,
    # then the CULM_DD inner lip — the cut bamboo wall, darkest, frames the light
    pygame.draw.polygon(surf, INK, vesica_pts(cx, cy, half_w, half_h))
    lip_in = max(2, int(2.2 * s))
    pygame.draw.polygon(surf, CULM_DD,
                        vesica_pts(cx, cy, half_w - max(1, int(1.0 * s)),
                                   half_h - max(1, int(1.0 * s))))

    # --- the FIVE FLAT STEPPED moon-ring BANDS inside the cut -----------------
    # absolute inward steps in px keep band widths even (countable plateaus).
    # Each entry: (inset_w_px, inset_h_px, flat_colour).
    inner_w = half_w - lip_in
    inner_h = half_h - lip_in
    bw = inner_w / 4.0     # roughly four even bands + the core
    bh = inner_h / 4.0
    bands = (
        (0.00, GLOW_RING0),   # outer dim ring (light just born) — already wide
        (0.90, GLOW),         # the pale gold-white body of the glow
        (1.80, GLOW_BR),      # paler step
        (2.60, GLOW_HOT),     # hot ring
    )
    for k, col in bands:
        hw = inner_w - bw * k
        hh = inner_h - bh * k
        if hw <= 1 or hh <= 1:
            continue
        pygame.draw.polygon(surf, col, vesica_pts(cx, cy, hw, hh))
    # the near-white HOT core field — enlarged one step vs round 1 so it owns the
    # 32px read. A fat core ellipse, not a sliver.
    core_w = max(2, int(inner_w * 0.40))
    core_h = max(2, int(inner_h * 0.46))
    pygame.draw.polygon(surf, GLOW_CORE, vesica_pts(cx, cy, core_w, core_h))

    # --- ONE soft-stepped GOLD halo band, hugging just outside the moon body --
    # the moon-gold accent kept as a single hard-edged stepped ring (NOT the
    # feathered arc ticks of round 1). Soft in HUE/role; hard in edge.
    gband_w = inner_w - bw * 0.45
    gband_h = inner_h - bh * 0.45
    pygame.draw.polygon(surf, lerp(GOLD, GLOW, 0.35),
                        vesica_pts(cx, cy, gband_w, gband_h),
                        max(1, int(1.6 * s)))

    if child:
        # --- the curled glowing moon-child, tucked low in the aperture -------
        # WHY small & curled: she is a NEWBORN found in the culm (chibi: big
        # head, tiny tucked body). Sized so she is the close-inspection reward;
        # at 32px she collapses to a dark seed and the GLOW carries the read.
        chr_ = half_w * 0.40
        chcx = cx
        chcy = cy + half_h * 0.26
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
    stalk of stacked node-segments, split down the middle by a BIG glowing
    vesica aperture (the dominant read) with the curled moon-child inside, light
    bleeding out into the world. `s` = unit scale around a ~132-unit figure.
    Drawn back-to-front: outer culm segments -> the cut split walls -> the
    glowing aperture + child last so the LIGHT owns the centre."""

    half_w = int(22 * s)
    seg_h = int(26 * s)
    top_y = cy - int(64 * s)
    bot_y = cy + int(64 * s)

    # the split spans a TALLER window than round 1 so the aperture can dominate.
    split_half = int(40 * s)   # half-height of the cut window

    # === UPPER culm segments (above the split) ===============================
    y = top_y
    while y < cy - split_half:
        culm_segment(surf, cx, y, seg_h, half_w, s)
        y += seg_h

    # === LOWER culm segments (below the split) ===============================
    y = cy + split_half
    while y < bot_y:
        culm_segment(surf, cx, y, seg_h, half_w, s)
        y += seg_h

    # === the SPLIT — two culm halves peeling apart around the aperture =======
    # WHY peeling halves: the silhouette must say 'cracked OPEN'. The aperture is
    # now FAT — it pushes to ~88% of the culm width so the bamboo walls are thin
    # luminous lips, not a thick frame around a small hole. Vesica points still
    # meet sharply top + bottom (the split tell).
    ap_hw = int(19 * s)         # aperture half-width (~88% of half_w)
    ap_hh = int(38 * s)         # aperture half-height (~60% of culm-segment span)
    for sgn in (-1, 1):
        wall = [(cx + sgn * half_w, cy - split_half),          # top outer
                (cx + sgn * half_w, cy + split_half),          # bottom outer
                (cx + sgn * ap_hw * 0.30, cy + split_half),    # bottom inner
                (cx + sgn * ap_hw, cy),                        # belly inner (bowed out)
                (cx + sgn * ap_hw * 0.30, cy - split_half)]    # top inner
        triad_blob(surf, CULM, wall,
                   core_pts=[(cx + sgn * int(half_w * 0.40), cy - int(36 * s)),
                             (cx + sgn * half_w, cy - int(36 * s)),
                             (cx + sgn * half_w, cy + int(36 * s)),
                             (cx + sgn * int(half_w * 0.40), cy + int(36 * s))]
                             if sgn > 0 else None,
                   sheen_pts=[(cx + sgn * half_w, cy - int(34 * s)),
                              (cx + sgn * int(half_w * 0.70), cy - int(34 * s)),
                              (cx + sgn * int(half_w * 0.70), cy + int(34 * s)),
                              (cx + sgn * half_w, cy + int(34 * s))]
                              if sgn < 0 else None,
                   ow=max(1, int(1.6 * s)))
        # cool moon-blue rim on the outer edge of each wall (held straight)
        pygame.draw.line(surf, RIM,
                         (cx + sgn * (half_w - int(2 * s)), cy - int(38 * s)),
                         (cx + sgn * (half_w - int(2 * s)), cy + int(38 * s)),
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
    cap_room = int(62 * s)

    if cap == "bottom":
        seg_top, seg_bot = top + int(2 * s), bot - cap_room
        ap_cy = bot - int(34 * s)
    else:
        seg_top, seg_bot = top + cap_room, bot - int(2 * s)
        ap_cy = top + int(34 * s)

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
    ap_hw = int(17 * s)         # fat — pushes to ~85% of culm width
    ap_hh = int(32 * s)
    cap_half = int(34 * s)
    for sgn in (-1, 1):
        wall = [(cx + sgn * half_w, ap_cy - cap_half),
                (cx + sgn * half_w, ap_cy + cap_half),
                (cx + sgn * ap_hw * 0.30, ap_cy + cap_half),
                (cx + sgn * ap_hw, ap_cy),
                (cx + sgn * ap_hw * 0.30, ap_cy - cap_half)]
        triad_blob(surf, CULM, wall,
                   core_pts=[(cx + sgn * int(half_w * 0.40), ap_cy - int(28 * s)),
                             (cx + sgn * half_w, ap_cy - int(28 * s)),
                             (cx + sgn * half_w, ap_cy + int(28 * s)),
                             (cx + sgn * int(half_w * 0.40), ap_cy + int(28 * s))]
                             if sgn > 0 else None,
                   ow=max(1, int(1.4 * s)))
        pygame.draw.line(surf, RIM,
                         (cx + sgn * (half_w - int(2 * s)), ap_cy - cap_half + int(2 * s)),
                         (cx + sgn * (half_w - int(2 * s)), ap_cy + cap_half - int(2 * s)),
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
        "moon-child in the split culm  ·  STRAIGHT symmetric culm · FAT vesica SPLIT + 5 FLAT stepped moon-bands (dominant, bleeds into gap) · round 2",
        True, LABEL_DIM), (190, 26))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_kaguya(big, 178 * SS, 235 * SS, 1.95 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("STRAIGHT symmetric pale culm cracked open by a FAT glowing VESICA aperture —", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("5 FLAT stepped moon-bands (countable plateaus, near-white core); outer bands BLEED past the culm.", True, LABEL_DIM), (14, 606))
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
    sheet.blit(font_sm.render("the gap, light bleeding into the gap) caps each edge — mirror visible", True, LABEL_DIM), (pcx - 4, 746))

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
        (GLOW, "moon-glow"), (GLOW_CORE, "moon core"),
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
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-CUTE · procedural-only · 5 FLAT stepped moon-bands (NO halo, NO gradient).",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
