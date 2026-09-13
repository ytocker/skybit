"""
Round-1 concept renderer for XINNIANG — the vermilion ghost-marriage corpse
bride (Batch 2 / Jiangshi-epic set, concept #3). Headless Pygame; supersample
at SS=6 → smoothscale to keep the elevated "epic" pipeline crisp at downscale.
House grammar held: chibi + scary-CUTE, flat saturated fills, hard 1-2px ink
keyline (28,22,30), dark-core → flat-fill → top-left rim-sheen triad, 1px
alpha-grown outline; procedural-only (no gradients/PNGs).

WHY this concept owns the ONE saturated-red mass in the set: per the cross-set
red-arc fix, Citipati is ivory-dominant and Vetala dark ox-blood — only Xinniang
is allowed a full SATURATED VERMILION mass. So the bell-robe is rendered as the
warmest, most chromatic block in the whole roster; the gold fengguan crown-arc,
the two glowing dead-eye dots under a SQUARE veil, and the gold hem motif are
pinned high in value so they carry the read and the red bell never collapses to
a plain cone at 32px.

WHY a standalone script: review art must never enter the shipped bundle, so it
lives under docs/ and reuses only colour math, not runtime sprite modules.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ────────────────────────────────────────────
# Xinniang owns the saturated-red mass: the robe is the warmest, most chromatic
# block in the set. Gold is the hero metal; jade is a literal hairpin sliver.
ROBE      = (206,  34,  40)   # SATURATED VERMILION robe — the dominant warm mass
ROBE_D    = (138,  22,  30)   # deep vermilion shade (dark core)
ROBE_T    = (236,  84,  72)   # vermilion rim-sheen helper (top-left)
SILK_D    = (118,  18,  26)   # silk-band shade — separates bands on the shaft
VEIL      = (182,  26,  34)   # square hanging veil — a touch deeper than robe
VEIL_D    = (120,  18,  26)
VEIL_T    = (224,  72,  66)
VEIL_GLOW = (255, 150, 120)   # faint warm veil-glow behind the dead-eyes
GOLD      = (228, 178,  72)   # gold fengguan / hem / medallions (hero metal)
GOLD_D    = (168, 124,  44)
GOLD_BR   = (250, 214, 116)   # brighter gold — night-biome anchor lift
GOLD_HI   = (255, 240, 196)   # gold specular pip
JADE      = ( 96, 186, 150)   # jade-hairpin sliver (lineage tell)
JADE_HI   = (176, 230, 204)
EYE_GLOW  = (252, 226, 168)   # faint glowing dead-eye dots
EYE_CORE  = (255, 248, 222)
INK       = ( 28,  22,  30)   # hard ink keyline (set-wide)
TASSEL    = (228, 178,  72)   # gold lantern tassel

BG        = ( 96,  98, 104)   # neutral grey review backdrop
PANEL     = ( 78,  80,  88)
DAY_SKY   = (132, 196, 232)   # day biome chip backdrop
NIGHT_SKY = ( 26,  32,  58)   # dark-blue night biome chip backdrop
LABEL     = (238, 240, 242)
LABEL_DIM = (190, 196, 204)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in outline_pts:
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
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.32), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def radial_glow(surf, center, radius, color, peak=80):
    """Additive procedural glow disc (no gradient surfaces — drawn ring by ring)."""
    g = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
    for r in range(radius*2, 0, -1):
        a = int(peak * (1 - r/(radius*2)) ** 1.4)
        pygame.draw.circle(g, (*color, a), (radius*2, radius*2), r)
    surf.blit(g, (center[0]-radius*2, center[1]-radius*2),
              special_flags=pygame.BLEND_ADD)


# ── gold fengguan phoenix-crown scalloped arc ────────────────────────────────
def fengguan(surf, cx, base_y, w, s):
    """A gold scalloped arc crowning the head — a row of filigree lobes rising
    in a dome, two phoenix-drop strings at the temples, a center jewel.

    WHY a scalloped ARC and not a solid block: the brief's tell is
    'square-veil-under-crown', and the crown must read as ornate METAL at 1x.
    A run of distinct gold lobes (each with its own ink notch + specular pip)
    keeps a filigree read where a solid dome would flatten to a hat."""
    n = 7
    half = w // 2
    pts_top = []
    pts_bot = []
    for i in range(n + 1):
        t = i / n
        x = cx - half + int(w * t)
        # dome profile — tallest at center, lobes scalloped along the rim
        dome = math.sin(t * math.pi)
        ytop = base_y - int((10 + 26 * dome) * s)
        pts_top.append((x, ytop))
        pts_bot.append((x, base_y))
    # ink backing arc
    band = pts_top + list(reversed(pts_bot))
    pygame.draw.polygon(surf, INK, band)
    pygame.draw.polygon(surf, GOLD, band)
    # dark core along the lower band
    core = [(p[0], p[1]) for p in pts_top[1:-1]] + \
           [(cx + half - int(2*s), base_y - int(2*s)),
            (cx - half + int(2*s), base_y - int(2*s))]
    pygame.draw.polygon(surf, GOLD_D, core)
    # scalloped lobes — distinct filigree bumps along the crown rim
    for i in range(n):
        t = (i + 0.5) / n
        x = cx - half + int(w * t)
        dome = math.sin(t * math.pi)
        ly = base_y - int((10 + 26 * dome) * s)
        lr = int((3.0 + 1.2 * dome) * s)
        pygame.draw.circle(surf, GOLD_BR, (x, ly), lr)
        pygame.draw.circle(surf, INK, (x, ly), lr, max(1, int(1*s)))
        pygame.draw.circle(surf, GOLD_HI, (x - int(1*s), ly - int(1*s)), max(1, int(1.2*s)))
        # filigree notches between lobes
        nx = cx - half + int(w * (i / n))
        pygame.draw.line(surf, GOLD_D, (nx, base_y - int(4*s)),
                         (nx, base_y - int(12*s)), max(1, int(1.4*s)))
    # center phoenix jewel
    jy = base_y - int(34*s)
    pygame.draw.circle(surf, INK, (cx, jy), int(6*s) + 1)
    pygame.draw.circle(surf, GOLD_BR, (cx, jy), int(6*s))
    pygame.draw.circle(surf, ROBE, (cx, jy), int(3.2*s))
    pygame.draw.circle(surf, EYE_CORE, (cx - int(1.5*s), jy - int(1.5*s)), max(1, int(1.6*s)))
    # phoenix-tail dangle strings — pulled IN toward the temple axis (and shorter)
    # so the head silhouette stays a clean dome, not a widening fan that crowns a
    # top-heavy read at 32px.
    for sgn in (-1, 1):
        bx = cx + sgn * int(half * 0.66)
        for k in range(2):
            by = base_y + int((4 + k*6) * s)
            pygame.draw.line(surf, GOLD_D, (bx, base_y), (bx, by), max(1, int(1.4*s)))
            pygame.draw.circle(surf, GOLD, (bx, by), max(1, int(2.0*s)))
            pygame.draw.circle(surf, INK, (bx, by), max(1, int(2.0*s)), 1)
        # red tassel drop at the end — kept short, hugging the temple axis
        ey = base_y + int(18*s)
        pygame.draw.line(surf, ROBE, (bx, base_y + int(12*s)), (bx, ey), max(1, int(2*s)))
    # jade hairpin sliver — the lineage tell, tucked above the right temple
    px0 = cx + int((half - 6) * s)
    pygame.draw.line(surf, INK, (px0, jy + int(2*s)),
                     (px0 + int(13*s), jy - int(7*s)), max(2, int(3*s)))
    pygame.draw.line(surf, JADE, (px0, jy + int(2*s)),
                     (px0 + int(13*s), jy - int(7*s)), max(1, int(2*s)))
    pygame.draw.circle(surf, JADE, (px0 + int(13*s), jy - int(7*s)), int(3*s))
    pygame.draw.circle(surf, INK, (px0 + int(13*s), jy - int(7*s)), int(3*s), 1)
    pygame.draw.circle(surf, JADE_HI, (px0 + int(12*s), jy - int(8*s)), max(1, int(1.2*s)))


# ── the creature ─────────────────────────────────────────────────────────────
def draw_xinniang(surf, cx, cy, s):
    """Tall narrow BELL-robe to the floor; a SQUARE hanging veil over a hidden
    face showing two faint glowing dead-eye dots; gold fengguan phoenix-crown
    scalloped arc on top; two bound silk hands clasped at the waist. `s` is a
    unit scale around a ~140-unit figure."""

    # bell-robe geometry — narrow at the shoulders, flaring to a wide floor hem
    top_w = int(46*s)
    bot_w = int(96*s)
    bh    = int(118*s)
    top_y = cy - int(46*s)
    bot_y = top_y + bh

    # ground shadow disc (keeps the floor-length bell rooted, never floating)
    sh = pygame.Surface((bot_w*2, int(20*s)*2), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 70), (0, 0, bot_w*2, int(20*s)*2))
    surf.blit(sh, (cx - bot_w, bot_y - int(10*s)))

    # bell skirt — concave flare so it reads as a hanging silk bell, not a cone
    bell = [
        (cx - top_w//2, top_y),
        (cx + top_w//2, top_y),
        (cx + int(top_w*0.62), top_y + int(bh*0.40)),
        (cx + bot_w//2,        bot_y - int(8*s)),
        (cx + bot_w//2 - int(4*s), bot_y),
        (cx - bot_w//2 + int(4*s), bot_y),
        (cx - bot_w//2,        bot_y - int(8*s)),
        (cx - int(top_w*0.62), top_y + int(bh*0.40)),
    ]
    triad_blob(
        surf, ROBE, bell,
        core_pts=[(cx + int(4*s), top_y + int(8*s)),
                  (cx + int(top_w*0.62), top_y + int(bh*0.40)),
                  (cx + bot_w//2 - int(6*s), bot_y - int(4*s)),
                  (cx + int(6*s), bot_y - int(4*s))],
        sheen_pts=[(cx - top_w//2 + int(3*s), top_y + int(3*s)),
                   (cx - int(3*s), top_y + int(3*s)),
                   (cx - int(int(top_w*0.55)), top_y + int(bh*0.42)),
                   (cx - bot_w//2 + int(10*s), bot_y - int(12*s)),
                   (cx - bot_w//2 + int(6*s), bot_y - int(6*s))],
        ow=max(2, int(2*s)),
    )

    # vertical silk fold lines down the bell — quiet shade grooves for body
    for fx in (-0.26, 0.10, 0.30):
        x0 = cx + int(top_w * fx)
        x1 = cx + int(bot_w * fx)
        pygame.draw.line(surf, SILK_D, (x0, top_y + int(20*s)),
                         (x1, bot_y - int(6*s)), max(1, int(1.6*s)))

    # gold hem motif — the floor band that anchors the bell at small scale.
    # A run of gold double-happiness ticks on a brighter gold band (night-lift).
    hem_y = bot_y - int(14*s)
    hem_h = int(11*s)
    pygame.draw.rect(surf, GOLD_BR, (cx - bot_w//2 + int(4*s), hem_y, bot_w - int(8*s), hem_h))
    pygame.draw.rect(surf, GOLD_D, (cx - bot_w//2 + int(4*s), hem_y + hem_h - int(2*s),
                                    bot_w - int(8*s), int(2*s)))
    pygame.draw.rect(surf, INK, (cx - bot_w//2 + int(4*s), hem_y, bot_w - int(8*s), hem_h),
                     max(1, int(1*s)))
    for k in range(-3, 4):
        gx = cx + int(k * 11 * s)
        pygame.draw.rect(surf, GOLD_D, (gx - int(2*s), hem_y + int(2*s), int(4*s), hem_h - int(4*s)), 1)
        pygame.draw.line(surf, GOLD_D, (gx, hem_y + int(2*s)), (gx, hem_y + hem_h - int(2*s)), 1)

    # --- two bound silk hands clasped at the waist (white wrap over the red) ---
    wy = top_y + int(58*s)
    hand_w = int(22*s)
    hand_h = int(18*s)
    hx0 = cx - hand_w//2
    hands = [(hx0, wy), (hx0 + hand_w, wy),
             (hx0 + hand_w - int(2*s), wy + hand_h), (hx0 + int(2*s), wy + hand_h)]
    # cream knocked down (236→212) so the clasp doesn't read as a second bright
    # spot competing with the hem; the eye still travels crown → eyes → hem first.
    triad_blob(surf, (212, 200, 186), hands,
               core_pts=[(cx, wy + int(4*s)), (hx0 + hand_w - int(2*s), wy + int(6*s)),
                         (hx0 + hand_w - int(3*s), wy + hand_h), (cx, wy + hand_h)],
               sheen_pts=[(hx0 + int(2*s), wy + int(2*s)), (cx - int(2*s), wy + int(2*s)),
                          (cx - int(2*s), wy + int(8*s)), (hx0 + int(2*s), wy + int(8*s))],
               ow=max(1, int(1.4*s)))
    # silk binding wrap — gold cord lashing the clasped hands
    for k in range(3):
        cyy = wy + int((5 + k*5) * s)
        pygame.draw.line(surf, GOLD, (hx0 + int(2*s), cyy), (hx0 + hand_w - int(2*s), cyy),
                         max(1, int(1.6*s)))
    pygame.draw.line(surf, INK, (cx, wy + int(2*s)), (cx, wy + hand_h - int(2*s)), max(1, int(1.2*s)))

    # --- head + SQUARE hanging veil over a hidden face ---
    head_r = int(24*s)
    hc = (cx, top_y - int(16*s))
    # faint warm glow behind the veil where the dead-eyes sit
    radial_glow(surf, (hc[0], hc[1] + int(2*s)), int(22*s), VEIL_GLOW, peak=58)

    # the SQUARE veil — a flat hanging panel that hides the face; corners squared
    vw = int(46*s)
    vtop = hc[1] - int(20*s)
    vbot = hc[1] + int(26*s)
    veil = [(hc[0] - vw//2, vtop), (hc[0] + vw//2, vtop),
            (hc[0] + vw//2, vbot), (hc[0] - vw//2, vbot)]
    triad_blob(
        surf, VEIL, veil,
        core_pts=[(hc[0] + int(2*s), vtop + int(4*s)), (hc[0] + vw//2, vtop + int(6*s)),
                  (hc[0] + vw//2, vbot), (hc[0] + int(2*s), vbot)],
        sheen_pts=[(hc[0] - vw//2 + int(2*s), vtop + int(2*s)),
                   (hc[0] - int(2*s), vtop + int(2*s)),
                   (hc[0] - int(2*s), vtop + int(16*s)),
                   (hc[0] - vw//2 + int(2*s), vtop + int(16*s))],
        ow=max(2, int(2*s)),
    )
    # veil weave — coarsened to FEW fat threads so it stays a clean panel, never
    # a stipple, at true 32px. Below a scale threshold the weave drops out entirely
    # so the square reads as a flat hanging panel and never competes with the eyes.
    if s >= 2.2:
        for vx in (-int(vw*0.24), int(vw*0.06), int(vw*0.24)):
            pygame.draw.line(surf, VEIL_D, (hc[0] + vx, vtop + int(4*s)),
                             (hc[0] + vx, vbot - int(3*s)), max(1, int(1.4*s)))
    # hard INK seam along the veil's BOTTOM edge so the SQUARE tell keeps a crisp
    # bottom line against the shoulders even when the red mass barely separates.
    pygame.draw.line(surf, INK, (hc[0] - vw//2, vbot), (hc[0] + vw//2, vbot), max(2, int(2*s)))
    # gold fringe — reduced to a crisp run of 4 beads on a bright lower edge, not
    # a muddy stipple band at 32px.
    fringe = [-int(vw*0.30), -int(vw*0.10), int(vw*0.10), int(vw*0.30)]
    pygame.draw.line(surf, GOLD_D, (hc[0] - vw//2 + int(3*s), vbot + int(2*s)),
                     (hc[0] + vw//2 - int(3*s), vbot + int(2*s)), max(1, int(1.4*s)))
    for fx in fringe:
        bx = hc[0] + fx
        pygame.draw.circle(surf, GOLD, (bx, vbot + int(4*s)), max(1, int(2.0*s)))
        pygame.draw.circle(surf, INK, (bx, vbot + int(4*s)), max(1, int(2.0*s)), 1)

    # two faint glowing dead-eye dots showing THROUGH the veil (scary-CUTE)
    # WHY small + close-set + flat-bottomed: wide-set round discs read owl/baby;
    # two close hot pinpricks slightly squashed read as a cold corpse-stare. The
    # glow peak is lowered so at 32px the two dots stay TWO dots, never bloom into
    # one fuzzy mass.
    for sgn in (-1, 1):
        ex = hc[0] + sgn * int(6.5*s)
        ey = hc[1] + int(2*s)
        radial_glow(surf, (ex, ey), int(4*s), EYE_GLOW, peak=82)
        # very-slightly wider-than-tall + flat bottom kills the button/owl read
        er = max(1, int(2.3*s))
        eh = max(1, int(2.0*s))
        pygame.draw.ellipse(surf, EYE_GLOW, (ex-er, ey-eh, er*2, eh*2))
        pygame.draw.circle(surf, EYE_CORE, (ex, ey - int(0.2*s)), max(1, int(1.3*s)))

    # --- gold fengguan phoenix-crown scalloped arc on top ---
    # WHY narrowed from 58→52: at 58 the arc was the widest mass on the figure and
    # flirted with a pagoda-wide / top-heavy head; 52 keeps the dome read clean.
    fengguan(surf, hc[0], vtop + int(2*s), int(52*s), s)


# ── the prop → pillar mirror (wedding-lantern dowry pole) ────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """Wedding-lantern dowry pole = red silk bands + hanging gold
    double-happiness medallions (echo the hem) = repeatable shaft band; cap =
    round wedding-LANTERN with a gold tassel at the gap edge. Round, on-axis."""
    shaft_w = int(18*s)
    pygame.draw.rect(surf, INK, (cx-shaft_w//2-1, top, shaft_w+2, bot-top))
    pygame.draw.rect(surf, ROBE, (cx-shaft_w//2, top, shaft_w, bot-top))
    pygame.draw.rect(surf, ROBE_D, (cx+shaft_w//2-int(5*s), top, int(5*s), bot-top))
    pygame.draw.rect(surf, ROBE_T, (cx-shaft_w//2, top, int(4*s), bot-top))

    # tileable band unit: a deep silk band + a hanging gold double-happiness
    # medallion, repeating on a fixed pitch so top↔bottom mirror cleanly
    pitch = int(40*s)
    band = top + int(20*s)
    while band < bot - int(20*s):
        # red silk band — a darker cinch ring around the shaft
        pygame.draw.rect(surf, INK, (cx-shaft_w//2-int(3*s)-1, band-1,
                                     shaft_w+int(6*s)+2, int(9*s)+2))
        pygame.draw.rect(surf, SILK_D, (cx-shaft_w//2-int(3*s), band,
                                        shaft_w+int(6*s), int(9*s)))
        pygame.draw.rect(surf, ROBE_T, (cx-shaft_w//2-int(3*s), band,
                                        shaft_w+int(6*s), int(2*s)))
        # gold double-happiness medallion hanging just below the band
        my = band + int(20*s)
        mr = int(11*s)
        pygame.draw.circle(surf, INK, (cx, my), mr+1)
        pygame.draw.circle(surf, GOLD_BR, (cx, my), mr)
        pygame.draw.circle(surf, GOLD_D, (cx, my), mr, max(1, int(1.4*s)))
        pygame.draw.circle(surf, ROBE, (cx, my), int(mr*0.62))
        # SHAFT medallion glyph — a bold low-detail mark so the tileable band stays
        # crisp at the 32px cap: a single fat gold cross-stroke (+ verticals only
        # when there's pixel room). The full 囍 is reserved for the lantern cap.
        pygame.draw.line(surf, GOLD_BR, (cx-int(5*s), my), (cx+int(5*s), my), max(2, int(2.4*s)))
        if s >= 0.6:
            for gx in (-int(4*s), int(4*s)):
                pygame.draw.line(surf, GOLD_BR, (cx+gx, my-int(4*s)), (cx+gx, my+int(4*s)), max(1, int(1.8*s)))
        pygame.draw.circle(surf, GOLD_HI, (cx-int(mr*0.4), my-int(mr*0.4)), max(1, int(1.4*s)))
        band += pitch

    # --- round wedding-lantern cap at the gap edge (creature-derived) ---
    ly = bot - int(6*s) if cap == "bottom" else top + int(6*s)
    lr = int(22*s)
    radial_glow(surf, (cx, ly), int(lr*1.4), VEIL_GLOW, peak=70)
    # top & bottom gold caps of the lantern
    for off in (-int(lr*1.05) - int(3*s), int(lr*1.05) - int(2*s)):
        pygame.draw.rect(surf, INK, (cx-int(8*s)-1, ly+off-1, int(16*s)+2, int(6*s)+2))
        pygame.draw.rect(surf, GOLD_BR, (cx-int(8*s), ly+off, int(16*s), int(6*s)))
        pygame.draw.rect(surf, GOLD_D, (cx-int(8*s), ly+off+int(4*s), int(16*s), int(2*s)))
    # the round red lantern body
    rect = pygame.Rect(cx-lr, ly-int(lr*1.0), lr*2, int(lr*2.0))
    pygame.draw.ellipse(surf, INK, rect.inflate(int(3*s), int(3*s)))
    pygame.draw.ellipse(surf, ROBE, rect)
    dark = rect.copy(); dark.left = cx + int(2*s)
    pygame.draw.ellipse(surf, ROBE_D, dark)
    pygame.draw.ellipse(surf, ROBE_T,
                        pygame.Rect(cx-lr+int(3*s), ly-int(lr*0.8), int(lr*0.7), int(lr*0.9)))
    pygame.draw.ellipse(surf, INK, rect, max(2, int(2*s)))
    # vertical lantern ribs
    for rx in (-int(8*s), 0, int(8*s)):
        pygame.draw.line(surf, ROBE_D, (cx+rx, ly-int(lr*0.95)), (cx+rx, ly+int(lr*0.95)), max(1, int(1.2*s)))
    # gold double-happiness on the lantern face (echoes the medallions)
    for gx in (-int(3.5*s), int(3.5*s)):
        pygame.draw.line(surf, GOLD_BR, (cx+gx, ly-int(6*s)), (cx+gx, ly+int(6*s)), max(1, int(2*s)))
    pygame.draw.line(surf, GOLD_BR, (cx-int(7*s), ly-int(2*s)), (cx+int(7*s), ly-int(2*s)), max(1, int(1.6*s)))
    pygame.draw.line(surf, GOLD_BR, (cx-int(7*s), ly+int(2*s)), (cx+int(7*s), ly+int(2*s)), max(1, int(1.6*s)))
    # gold tassel hanging off the gap-facing end
    tip = ly + int(lr*1.05) + int(6*s) if cap == "bottom" else ly - int(lr*1.05) - int(6*s)
    tdir = 1 if cap == "bottom" else -1
    pygame.draw.circle(surf, GOLD_BR, (cx, tip), int(3*s))
    pygame.draw.circle(surf, INK, (cx, tip), int(3*s), 1)
    for tx in (-int(3*s), 0, int(3*s)):
        pygame.draw.line(surf, TASSEL, (cx+tx, tip),
                         (cx+tx, tip + tdir*int(12*s)), max(1, int(1.6*s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def render_creature_box(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw*SS, boxh*SS), pygame.SRCALPHA)
    draw_xinniang(big, draw_cx*SS, draw_cy*SS, scale*SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def main():
    W, H = 1010, 820
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 13)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 54))
    sheet.blit(font_big.render("XINNIANG", True, LABEL), (24, 12))
    sheet.blit(font_sm.render(
        "vermilion ghost-marriage corpse bride  ·  saturated-vermilion bell (the warmest mass in the set) + gold fengguan + jade sliver  ·  round 2",
        True, LABEL_DIM), (220, 24))

    # --- HERO sprite (large, epic scale) ---
    hero = render_creature_box(340, 470, 170, 250, 1.7)
    sheet.blit(hero, (10, 92))
    sheet.blit(font.render("Hero sprite", True, LABEL), (90, 568))
    sheet.blit(font_sm.render("square veil over hidden face + two glowing dead-eye dots;", True, LABEL_DIM), (14, 592))
    sheet.blit(font_sm.render("gold fengguan scalloped arc on top; bound silk hands; floor-length red bell", True, LABEL_DIM), (14, 610))

    # --- prop → pillar mirror (assembled: top seg + gap + bottom seg, mirrored) ---
    pcx = 470
    # bottom segment (cap faces UP toward the gap)
    bot_big = pygame.Surface((150*SS, 300*SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75*SS, 4*SS, 296*SS, 1.0*SS, cap="top")
    botseg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 300)), INK + (255,), 1)
    # top segment (cap faces DOWN toward the gap) — the mirror
    top_big = pygame.Surface((150*SS, 230*SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75*SS, 4*SS, 226*SS, 1.0*SS, cap="bottom")
    topseg = grow_outline(pygame.transform.smoothscale(top_big, (150, 230)), INK + (255,), 1)

    sheet.blit(topseg, (pcx - 75, 78))
    gap_y = 78 + 230
    gap_h = 70
    sheet.blit(botseg, (pcx - 75, gap_y + gap_h))
    # gap markers
    pygame.draw.line(sheet, (220, 220, 100), (pcx - 86, gap_y), (pcx + 86, gap_y), 1)
    pygame.draw.line(sheet, (220, 220, 100), (pcx - 86, gap_y + gap_h), (pcx + 86, gap_y + gap_h), 1)
    sheet.blit(font_sm.render("GAP", True, (230, 230, 140)), (pcx - 14, gap_y + gap_h//2 - 8))
    sheet.blit(font.render("Pillar (mirrored)", True, LABEL), (pcx - 70, 678))
    sheet.blit(font_sm.render("red silk bands + hanging gold 囍 medallions =", True, LABEL_DIM), (pcx - 80, 702))
    sheet.blit(font_sm.render("tileable shaft; round wedding-lantern cap + gold tassel", True, LABEL_DIM), (pcx - 80, 720))

    # --- TRUE 32px gameplay-scale chips: day sky + night sky ---
    panel_x = 620
    pygame.draw.rect(sheet, PANEL, (panel_x, 78, W - panel_x - 12, 400))
    sheet.blit(font.render("True 32px gameplay chip", True, LABEL), (panel_x + 16, 88))
    sheet.blit(font_sm.render("does the read carry: gold crown-arc +", True, LABEL_DIM), (panel_x + 16, 114))
    sheet.blit(font_sm.render("two eye-dots + gold hem (not a plain cone)?", True, LABEL_DIM), (panel_x + 16, 132))

    def chip(px, sky):
        boxbig = pygame.Surface((px*SS*3, px*SS*3, ), pygame.SRCALPHA)
        # figure ~140 units tall → fit roughly into the chip height
        draw_xinniang(boxbig, int(px*SS*1.5), int(px*SS*1.7), (px/130.0)*SS)
        c = pygame.transform.smoothscale(boxbig, (px*3, px*3))
        c = grow_outline(c, INK + (255,), 1)
        base = pygame.Surface((px*3, px*3))
        base.fill(sky)
        base.blit(c, (0, 0))
        return base

    # 32px day
    d32 = chip(32, DAY_SKY)
    sheet.blit(d32, (panel_x + 20, 158))
    sheet.blit(font_sm.render("32px · DAY", True, LABEL), (panel_x + 20, 158 + 32*3 + 4))
    # 32px night
    n32 = chip(32, NIGHT_SKY)
    sheet.blit(n32, (panel_x + 20 + 32*3 + 24, 158))
    sheet.blit(font_sm.render("32px · NIGHT", True, LABEL_DIM), (panel_x + 20 + 32*3 + 24, 158 + 32*3 + 4))

    # 48px day + night for a step-up read
    d48 = chip(48, DAY_SKY)
    sheet.blit(d48, (panel_x + 20, 300))
    sheet.blit(font_sm.render("48px · day", True, LABEL), (panel_x + 20, 300 + 48*2 + 2)) if False else None
    n48 = chip(48, NIGHT_SKY)
    sheet.blit(n48, (panel_x + 20 + 48*3 + 14, 300)) if False else None
    sheet.blit(font_sm.render("48px day (step-up read)", True, LABEL_DIM), (panel_x + 20, 300 + 48*3 + 4))

    # pillar gap-cap chip at 32px
    pchipbig = pygame.Surface((44*SS, 130*SS), pygame.SRCALPHA)
    draw_pillar(pchipbig, 22*SS, 2*SS, 128*SS, 0.30*SS, cap="bottom")
    pchip = grow_outline(pygame.transform.smoothscale(pchipbig, (44, 130)), INK + (255,), 1)
    pbase = pygame.Surface((44, 130)); pbase.fill(DAY_SKY); pbase.blit(pchip, (0, 0))
    sheet.blit(pbase, (panel_x + 20 + 48*3 + 24, 300))
    sheet.blit(font_sm.render("pillar @ 32px cap", True, LABEL_DIM), (panel_x + 20 + 48*3 + 18, 300 + 130 + 4))

    # --- palette swatch row ---
    py = 496
    pygame.draw.rect(sheet, PANEL, (panel_x, py, W - panel_x - 12, 312))
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, py + 10))
    sheet.blit(font_sm.render("Xinniang owns the ONE saturated-red mass", True, LABEL_DIM), (panel_x + 16, py + 34))
    swatches = [
        (ROBE, "vermilion robe"), (ROBE_D, "deep vermilion"),
        (VEIL, "veil red"), (SILK_D, "silk-band shade"),
        (GOLD, "gold (hero metal)"), (GOLD_BR, "gold (night-lift)"),
        (JADE, "jade hairpin sliver"), (EYE_GLOW, "dead-eye glow"),
        (VEIL_GLOW, "veil glow"), (INK, "ink keyline"),
    ]
    sx, sy = panel_x + 16, py + 58
    for i, (c, name) in enumerate(swatches):
        col = i % 2
        row = i // 2
        rx = sx + col*185
        ry = sy + row*30
        pygame.draw.rect(sheet, INK, (rx-1, ry-1, 24, 24))
        pygame.draw.rect(sheet, c, (rx, ry, 22, 22))
        sheet.blit(font_sm.render("%s" % name, True, LABEL), (rx+30, ry+1))
        sheet.blit(font_sm.render("%d,%d,%d" % c, True, LABEL_DIM), (rx+30, ry+13))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
