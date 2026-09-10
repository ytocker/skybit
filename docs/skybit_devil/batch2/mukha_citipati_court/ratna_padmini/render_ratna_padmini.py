"""
Round-1 concept renderer for RATNA-PADMINI — the jewel-lotus throne mother
(mukha_citipati_court brood, sister #5; the gentlest, the brood's PREMIUM /
high-end anchor). Headless Pygame; HIGH-RES pipeline (supersample SS=8 →
smoothscale) so the highest small-element count in the brood stays crisp at
downscale. Keeps the shipped house grammar: flat saturated fills, hard 1-2px
ink keyline (28,22,26), dark-core → flat-fill → top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE; procedural-only (no
gradients/PNGs).

WHY this sister is the premium CONTRAST piece: turquoise + lavish gold + coral
read as jewel-and-treasure against the wrathful sisters' bone-and-fire. The
look must be RICH by drawn jewel-edge value (gold rims, cabochon highlights,
inlay facets), NOT by bloom — glow is confined to the turquoise third-eye + the
crown-centre skull only, per the value ladder.

WHY she is the ONLY sister with a FULL enclosing flame-halo (prabhamandala): the
locked 32px element. With the highest small-element count in the brood (jewel
inlay + tassels + beadwork + per-petal gems + a tiered throne), the two-scale
rule is policed hardest here — the closed halo RING is the one element that
carries the gameplay silhouette; every fiddly inlay/tassel/per-petal gem is
HERO-ONLY and is dropped at true 32px. The body is MUKHA's squat chibi
rib-barrel over a wide 6-petal lotus base; she fuses the Citipati 5-skull
arc-sweep AND the Mukha tiara-band across the brow into one gem-studded crown.

WHY the jewel-lotus throne IS the pillar: a stacked column of tiered lotus
thrones (her own base, repeated) threaded on a gold rod = the tileable shaft;
the gap-edge cap is a single gem-tipped lotus blossom inside a small closed
flame-ring with a glowing turquoise cabochon at the hub — her own forms,
symmetric and on-axis.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Bone is the structural mass but pushed warm-pale so the GOLD + TURQUOISE read
# as the dominant treasure hues (this is the premium / high-end anchor). Coral
# is the tassel accent. Everything reads rich by drawn value, never by bloom.
BONE      = (236, 224, 206)   # warm pale bone (structural mass)
BONE_D    = (186, 168, 144)   # bone dark-core / shade
BONE_DD   = (132, 116,  96)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (250, 244, 230)   # bone top-left rim-sheen
TURQ      = ( 56, 178, 178)   # turquoise — third-eye + cabochons + halo cores
TURQ_BR   = (138, 226, 222)   # hot turquoise inner / sheen
TURQ_HOT  = (208, 248, 244)   # hottest turquoise core (third-eye brightest)
TURQ_D    = ( 30, 112, 116)   # deep turquoise shade
GOLD      = (226, 182,  72)   # lavish gold — the dominant treasure metal
GOLD_BR   = (250, 220, 128)   # hot gold sheen / facet
GOLD_HOT  = (255, 244, 196)   # hottest gold spark
GOLD_SPEC = (230, 215, 160)   # warm pale-gold bead/facet specular (NOT white —
                              # keeps every gold glint below the third-eye core)
GOLD_D    = (166, 124,  44)   # deep gold shade (rim, recessed inlay)
CORAL     = (236, 110,  88)   # coral tassel accent
CORAL_BR  = (252, 170, 144)
CORAL_D   = (172,  62,  52)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = ( 56, 178, 178)   # turquoise third-eye (the single brightest focal)

BG        = ( 88,  92,  98)   # neutral grey review backdrop
PANEL     = ( 70,  74,  82)
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


# ── a faceted jewel cabochon (the premium tell — HERO-only detail) ────────────
def cabochon(surf, c, r, s, col, br, glow=False):
    """A round gem in a gold bezel with a hard facet highlight. WHY a gold rim +
    a single bright facet pip: this is what makes the sprite read RICH by drawn
    jewel-edge value, not by bloom — the bezel separates the gem from bone and
    the pip gives it the cut-stone glint. `glow` reserves the brightest core for
    the focal cabochons only (third-eye + crown-centre)."""
    cx, cy = int(c[0]), int(c[1])
    # gold bezel
    triad_circle(surf, GOLD, (cx, cy), r + max(1, int(2 * s)),
                 ow=max(1, int(1.4 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, GOLD_D, (cx, cy), r + max(1, int(2 * s)), max(1, int(1.2 * s)))
    # the stone
    triad_circle(surf, col, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    pygame.draw.circle(surf, lerp(col, INK, 0.4),
                       (cx + int(r * 0.30), cy + int(r * 0.32)), int(r * 0.62))
    pygame.draw.circle(surf, col, (cx, cy), int(r * 0.78))
    # the hard facet glint — capped to warm pale-gold for non-focal stones so no
    # cabochon out-shines the third-eye (the value-ladder fix).
    glint = br if glow else lerp(br, GOLD_SPEC, 0.5)
    pygame.draw.circle(surf, glint, (cx - int(r * 0.32), cy - int(r * 0.34)),
                       max(1, int(r * 0.34)))
    if glow:
        pygame.draw.circle(surf, TURQ_HOT, (cx - int(r * 0.16), cy - int(r * 0.18)),
                           max(1, int(r * 0.20)))


# ── a FACETED CUT gem (the focal brow jewel — a cut stone, not a dot) ──────────
def faceted_gem(surf, c, r, s, col, br, hot, white=True):
    """A cut, FACETED gem in a gold bezel — the brow third-eye focal. WHY this is
    distinct from cabochon(): a cabochon reads as a smooth domed dot; the focal
    must read as a CUT jewel. So this lays a polygonal crown of facet triangles
    (a girdle of trapezoid facets around a central table), shades alternating
    facets dark/bright so the cut catches light, then sets a tight hard white
    HOTSPOT on the table — the single brightest pixel in the whole figure. The
    gold bezel + facet glints make it rich by drawn jewel-edge value, not bloom."""
    cx, cy = int(c[0]), int(c[1])
    # gold bezel ring around the stone (the setting)
    triad_circle(surf, GOLD, (cx, cy), r + max(1, int(2.2 * s)),
                 ow=max(1, int(1.6 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, GOLD_D, (cx, cy), r + max(1, int(2.2 * s)), max(1, int(1.3 * s)))
    # the stone body (deep-shade base so the bright facets pop off it)
    pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1 * s)))
    pygame.draw.circle(surf, lerp(col, INK, 0.35), (cx, cy), r)
    # girdle of trapezoid facets — alternate light/dark around a central table so
    # the cut reads as ground planes catching light from the top-left.
    facets = 8
    tabr = r * 0.46
    for k in range(facets):
        a0 = -math.pi / 2 + (k / facets) * 2 * math.pi
        a1 = -math.pi / 2 + ((k + 1) / facets) * 2 * math.pi
        am = (a0 + a1) * 0.5
        outer0 = (cx + math.cos(a0) * r, cy + math.sin(a0) * r)
        outer1 = (cx + math.cos(a1) * r, cy + math.sin(a1) * r)
        tab0 = (cx + math.cos(a0) * tabr, cy + math.sin(a0) * tabr)
        tab1 = (cx + math.cos(a1) * tabr, cy + math.sin(a1) * tabr)
        # light bias toward the top-left where the sheen falls (cos of angle to NW)
        lit = math.cos(am - math.radians(-135))
        fc = lerp(col, br, 0.55) if lit > 0 else lerp(col, INK, 0.5)
        pygame.draw.polygon(surf, fc, [outer0, outer1, tab1, tab0])
        pygame.draw.line(surf, lerp(col, INK, 0.6), outer0, tab0, max(1, int(0.9 * s)))
    # the central TABLE — the flat top face, brightest plane of the cut
    tab_poly = [(cx + math.cos(-math.pi / 2 + (k / facets) * 2 * math.pi) * tabr,
                 cy + math.sin(-math.pi / 2 + (k / facets) * 2 * math.pi) * tabr)
                for k in range(facets)]
    pygame.draw.polygon(surf, br, tab_poly)
    pygame.draw.polygon(surf, lerp(br, hot, 0.5),
                        [(cx + (p[0] - cx) * 0.6, cy + (p[1] - cy) * 0.6) for p in tab_poly])
    # two hard facet GLINTS — the cut-stone sparkle, top-left + a lower-right kicker
    pygame.draw.circle(surf, hot, (cx - int(r * 0.30), cy - int(r * 0.32)), max(1, int(r * 0.22)))
    pygame.draw.circle(surf, lerp(br, hot, 0.5),
                       (cx + int(r * 0.34), cy + int(r * 0.30)), max(1, int(r * 0.12)))
    # the single brightest pixel: a tight pure-white hotspot on the table
    if white:
        pygame.draw.circle(surf, (255, 255, 255),
                           (cx - int(r * 0.12), cy - int(r * 0.16)), max(1, int(r * 0.16)))


# ── a coral tassel — bell-cap + cord + fringe (HERO-only beadwork) ────────────
def tassel(surf, x, y, length, s, sgn=1):
    """A hanging coral tassel: a gold bell-cap, a beaded cord, a coral fringe of
    threads. WHY HERO-only: at 32px the threads are sub-pixel and would mush into
    the halo ring — these only survive on the big hero, dropped at gameplay scale
    per the two-scale rule."""
    # gold bell-cap
    triad_circle(surf, GOLD, (int(x), int(y)), max(1, int(3.2 * s)),
                 ow=max(1, int(1 * s)), core=False, sheen=False)
    # a couple of gold beads on the cord
    for k in (1, 2):
        by = y + k * int(4.5 * s)
        pygame.draw.circle(surf, GOLD_D, (int(x), int(by)), max(1, int(2.0 * s)))
        pygame.draw.circle(surf, GOLD_SPEC, (int(x - 1 * s), int(by - 1 * s)), max(1, int(0.9 * s)))
    # coral fringe threads spreading slightly
    base_y = y + int(11 * s)
    for k in range(-2, 3):
        tx = x + k * int(2.2 * s)
        ty = base_y + length + abs(k) * int(2 * s)
        pygame.draw.line(surf, CORAL_D, (int(x), int(base_y)), (int(tx), int(ty)), max(1, int(2.0 * s)))
        pygame.draw.line(surf, CORAL, (int(x), int(base_y)), (int(tx), int(ty)), max(1, int(1.2 * s)))
        pygame.draw.circle(surf, CORAL_BR, (int(tx), int(ty)), max(1, int(1.6 * s)))


# ── a single ornamental tiara/crown skull (cloned from Mukha tiara_skull) ─────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny pale-bone skull for the fused crown arc + tiara-band. WHY a domed
    cranium with two dark dots: it must punch a clean bone shape with two sockets
    at 32px. For ratna it is gem-studded — a turquoise brow-cabochon set on the
    forehead — but that gem is HERO-only; at small scale the bone dome carries it.
    `lit` reserves the hot turquoise eyes for the crown-CENTRE skull (the only
    crown glow). WHY darkened + no sheen: the crown is the dimmest value rung."""
    cbone = lerp(BONE, BONE_D, 0.70)
    triad_circle(surf, cbone, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False,
                 sheen=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, cbone, jaw, ow=max(1, int(1.1 * s)))
    # the one crown glow uses TURQ_BR (not TURQ_HOT) so even the lit crown-centre
    # stays the dimmest tier — only the third-eye carries the hottest core.
    eye_c = TURQ_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── crown-skull — five DISTINCT gilded-reliquary skulls along the arc-sweep ───
def crown_skull(surf, cx, cy, r, s, lit=False, idx=0):
    """One skull of the Citipati 5-skull arc-SWEEP riding the OUTER crown
    silhouette. WHY a per-`idx` cabinet, not one dome stamped five times: the
    crown row was one rounded skull cloned across the arc and read as a repeat
    stamp. Each `idx` (0-4) now picks a DISTINCT CRANIUM SILHOUETTE — built as a
    per-idx polygon dome, NOT a shared circle — so the difference survives at
    32px in the SHAPE, not only in the etching: tall ogival / broad squat /
    heart-domed centre / narrow oval / angular lantern. Each also carries its own
    GILT treatment (gold beaded suture / filigree-zigzag suture / lotus-petal
    brow etch / gold brow-fillet / crown rosette) so the row reads as a band of
    individuated reliquaries — the palm-skulls' build-richness ported UP.

    WHY this stays the DIMMEST rung: the crown bone is darkened, there is NO white
    specular, NO sheen, and the gilt is GOLD_D/GOLD only (never GOLD_BR/HOT, never
    a brightness bump). The one crown glow is the centre's small TURQ tick — capped
    at TURQ (never TURQ_BR/TURQ_HOT) — so the brow turquoise cabochon stays the
    single brightest pixel."""
    # per-idx character cabinet — the five crown reliquary identities. (wx, top,
    # bot) reshape the cranium SILHOUETTE; the strings/booleans pick the gilt.
    SPEC = [
        # idx 0 — TALL OGIVAL reliquary, gold beaded suture, round jaw
        dict(wx=0.80, top=1.30, bot=0.96, jaw="round", suture="beaded",
             fillet=False, petals=False, rosette=False),
        # idx 1 — BROAD SQUAT reliquary, fine filigree-zigzag suture, square jaw
        dict(wx=1.22, top=0.84, bot=1.04, jaw="square", suture="filigree",
             fillet=False, petals=False, rosette=True),
        # idx 2 — HEART-DOMED CENTRE reliquary (the lit centre), gold brow-fillet
        dict(wx=1.04, top=1.16, bot=0.92, jaw="round", suture="plain",
             fillet=True, petals=False, rosette=False),
        # idx 3 — NARROW OVAL reliquary, lotus-petal brow etch, round jaw
        dict(wx=0.78, top=1.06, bot=1.12, jaw="round", suture="plain",
             fillet=False, petals=True, rosette=False),
        # idx 4 — ANGULAR LANTERN reliquary, crown rosette, square jaw
        dict(wx=0.94, top=0.96, bot=1.18, jaw="square", suture="beaded",
             fillet=False, petals=False, rosette=True),
    ][idx % 5]
    wx, top, bot = SPEC["wx"], SPEC["top"], SPEC["bot"]
    cbone = lerp(BONE, BONE_D, 0.70)   # darkened: crown sits below the palm-skulls

    # cranium SILHOUETTE — a per-idx polygon dome (lantern variants square the
    # shoulders; ogival pinches the apex) so the five read as different skull
    # shapes in the bare outline, the variety that survives 32px downscale.
    lantern = SPEC["jaw"] == "square" and SPEC["rosette"]
    dome = []
    for k in range(13):
        a = math.pi + math.pi * (k / 12)
        rise = top if math.sin(a) < 0 else 1.0
        # ogival: pinch the apex narrower as it rises; lantern: hold width square.
        wfac = wx
        if not lantern and top > 1.1:
            wfac = wx * (1.0 - 0.30 * max(0.0, -math.sin(a)))
        elif lantern:
            wfac = wx * (1.0 if abs(math.cos(a)) < 0.55 else 0.92)
        dome.append((cx + math.cos(a) * r * wfac, cy + math.sin(a) * r * rise))
    dome.append((cx + r * wx * 0.80, cy + r * 0.48 * bot))
    dome.append((cx - r * wx * 0.80, cy + r * 0.48 * bot))
    triad_blob(surf, cbone, dome, ow=max(1, int(1.5 * s)))

    # JAW — round chin or square lantern, per idx, so the lower face individuates.
    if SPEC["jaw"] == "square":
        jaw = [(cx - int(r * 0.52), cy + int(r * 0.46 * bot)),
               (cx + int(r * 0.52), cy + int(r * 0.46 * bot)),
               (cx + int(r * 0.50), cy + int(r * 1.04 * bot)),
               (cx - int(r * 0.50), cy + int(r * 1.04 * bot))]
    else:
        jaw = [(cx - int(r * 0.50), cy + int(r * 0.46 * bot)),
               (cx + int(r * 0.50), cy + int(r * 0.46 * bot)),
               (cx + int(r * 0.32), cy + int(r * 0.98 * bot)),
               (cx - int(r * 0.32), cy + int(r * 0.98 * bot))]
    triad_blob(surf, cbone, jaw, ow=max(1, int(1.2 * s)))

    # central SUTURE — three distinct dim-gilt treatments (gold beaded studs /
    # fine filigree-zigzag / plain bone seam) so the gilt read changes along the
    # row. All GOLD_D/GOLD only — no bright gold, the crown stays the dim rung.
    su_top, su_bot = -r * top * 0.92, -r * 0.06
    if SPEC["suture"] == "beaded":
        for k in range(4):
            yk = cy + su_top + (su_bot - su_top) * (k / 3)
            pygame.draw.circle(surf, GOLD_D, (cx, int(yk)), max(1, int(1.0 * s)))
    elif SPEC["suture"] == "filigree":
        prev = (cx, cy + su_top)
        for k in range(1, 6):
            off = (r * 0.18) * (1 if k % 2 else -1)
            p = (cx + off, cy + su_top + (su_bot - su_top) * (k / 5))
            pygame.draw.line(surf, GOLD_D, prev, p, max(1, int(0.9 * s)))
            prev = p
    else:
        pygame.draw.line(surf, BONE_DD, (cx, cy + int(su_top)), (cx, cy + int(su_bot)),
                         max(1, int(1.0 * s)))

    # fine LOTUS-PETAL brow etch fanning over the dome (idx 3) — hairline gold so
    # it reads as engraving, never jewellery; capped at GOLD_D for the dim rung.
    if SPEC["petals"]:
        for k in range(-2, 3):
            a = -math.pi / 2 + k * 0.40
            p0 = (cx + math.cos(a) * r * 0.26, cy - r * 0.28 + math.sin(a) * r * 0.18)
            p1 = (cx + math.cos(a) * r * 0.64 * wx, cy - r * 0.70 + math.sin(a) * r * 0.08)
            pygame.draw.line(surf, GOLD_D, p0, p1, max(1, int(0.8 * s)))

    # a thin gold BROW-FILLET diadem (idx 2) — GOLD_D/GOLD only, no bright rail.
    if SPEC["fillet"]:
        f0 = (cx - r * 0.50 * wx, cy - r * 0.34)
        f1 = (cx + r * 0.50 * wx, cy - r * 0.34)
        pygame.draw.line(surf, GOLD_D, f0, f1, max(2, int(1.8 * s)))
        pygame.draw.line(surf, GOLD, f0, f1, max(1, int(1.0 * s)))

    # a small gold-rimmed crown ROSETTE at the apex (idx 1, 4) — GOLD_D/GOLD only.
    if SPEC["rosette"]:
        rc = (cx, cy - int(r * top * 0.80))
        rr = max(1, int(r * 0.20))
        pygame.draw.circle(surf, GOLD_D, rc, rr + max(1, int(0.7 * s)))
        pygame.draw.circle(surf, GOLD, rc, rr)

    # SOCKETS — deep flat-dark ink eyes; the lit CENTRE gets a TURQ fill (capped at
    # TURQ, never TURQ_BR/HOT) so even the one crown glow stays the dimmest tier.
    for ex in (cx - int(r * 0.38 * wx), cx + int(r * 0.38 * wx)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, TURQ, (ex, cy + int(r * 0.04)), max(1, int(r * 0.12)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42 * bot)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70 * bot)),
                     (cx + int(r * 0.34), cy + int(r * 0.70 * bot)),
                     max(1, int(1.2 * s)))
    # the one crown glow: a tiny TURQ brow tick on the lit centre only (kept small
    # + capped at TURQ so the focal brow cabochon stays the single brightest pixel).
    if lit:
        pygame.draw.circle(surf, TURQ, (cx, cy - int(r * 0.40)), max(1, int(r * 0.12)))


# ── the FULL enclosing flame-halo RING — prabhamandala (THE 32px element) ─────
def flame_halo(surf, cx, cy, rad, s, lobes=22, reach=1.0, full=True, hero=True):
    """A complete enclosing lobed flame ring — the prabhamandala. Cloned from
    Citipati's flame_halo but rebuilt CLOSED: ratna is the ONLY sister with a
    full enclosing halo, and it is the locked element that carries the gameplay
    silhouette at true 32px. WHY value-graded gold→turquoise tongues, not orange
    fire: this halo is jewel-edged treasure, not a wrathful pyre — gold tongues
    with cool turquoise tips read as her premium prabhamandala and stay distinct
    from the wrathful sisters' ember halos.

    `full=True` draws the entire ring (no bottom gap); each tongue is a slim,
    separated flame so the ring reads as a clean lobed band with sky between the
    tongues — dense but never a solid disc. At 32px the lobed band collapses to
    the one bold ring that defines the silhouette.

    `hero=False` is the 32px gameplay treatment: spikes are SOLID GOLD (the cool
    turquoise tip is dead weight on navy at small scale — it dropped out and left
    orphaned gold flecks at night), and a CONTINUOUS gold ring CIRCLE at the spike
    bases keeps the closed-ring read even when the spike-tips vanish in downscale."""
    base_r = rad * 0.94
    tip_r = rad * (1.10 + 0.26 * reach)
    half_w = (math.pi / lobes) * 0.46
    # CLOSED gold ring connecting the spike bases — drawn FIRST so it underlies
    # the tongues. This is what carries the ring read at night-32px when tips drop.
    ring_w = max(2, int(2.4 * s)) if hero else max(3, int(3.4 * s))
    pygame.draw.circle(surf, GOLD_D, (int(cx), int(cy)), int(base_r) + ring_w // 2, ring_w)
    pygame.draw.circle(surf, GOLD, (int(cx), int(cy)), int(base_r),
                       max(1, int(1.6 * s)) if hero else max(2, int(2.2 * s)))
    angles = [-math.pi / 2 + (i / lobes) * 2 * math.pi for i in range(lobes)]
    for ang in angles:
        if not full and math.sin(ang) > 0.5:
            continue
        a0 = ang - half_w
        a1 = ang + half_w
        base0 = (cx + math.cos(a0) * base_r, cy + math.sin(a0) * base_r)
        base1 = (cx + math.cos(a1) * base_r, cy + math.sin(a1) * base_r)
        tipp = (cx + math.cos(ang) * tip_r, cy + math.sin(ang) * tip_r)
        kink = (cx + math.cos(ang + half_w * 0.5) * (base_r + (tip_r - base_r) * 0.55),
                cy + math.sin(ang + half_w * 0.5) * (base_r + (tip_r - base_r) * 0.55))
        tongue = [base0, kink, tipp, base1]
        pygame.draw.polygon(surf, INK, tongue)
        pygame.draw.polygon(surf, GOLD, tongue)
        mid0 = (base0[0] + (tipp[0] - base0[0]) * 0.50, base0[1] + (tipp[1] - base0[1]) * 0.50)
        mid1 = (base1[0] + (tipp[0] - base1[0]) * 0.50, base1[1] + (tipp[1] - base1[1]) * 0.50)
        pygame.draw.polygon(surf, GOLD_BR, [base0, mid0, tipp, mid1])
        # cool turquoise tip = the jewel-treasure read — HERO ONLY (vanishes on
        # navy at 32px and orphaned the gold flecks; solid-gold tongues at 32px).
        if hero:
            pygame.draw.polygon(surf, TURQ_BR, [mid0, tipp, mid1])
        pygame.draw.polygon(surf, INK, tongue, max(1, int(1.0 * s)))


# ── the six-arm radial fan (cloned from Mukha draw_arm_fan) ───────────────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the brood KIND tell. Cloned from Mukha: low-origin shoulders, spread
    ~[100,64,28]° off vertical, NO arm aimed straight up so a clean wedge of open
    sky stays above the crown. For ratna each arm carries a thin gold armlet band
    (HERO-only beadwork). Returns the six hand centres for the palm-skulls."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
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
        # a thin gold ARMLET BAND wrapping across the arm at the elbow. WHY a band
        # across the limb, NOT a bone disc + gold ring: round 1/2's filled disc
        # read as the very "gold-rimmed medallion" the palm-skull motif must NOT
        # be confused with. A perpendicular cuff stripe is unmistakably jewellery,
        # never a cradled relic.
        adx, ady = hand[0] - sh[0], hand[1] - sh[1]
        aL = max(1.0, math.hypot(adx, ady))
        pnx, pny = -ady / aL, adx / aL            # across-arm normal
        e0 = (elbow[0] + pnx * arm_th * 0.5, elbow[1] + pny * arm_th * 0.5)
        e1 = (elbow[0] - pnx * arm_th * 0.5, elbow[1] - pny * arm_th * 0.5)
        pygame.draw.line(surf, GOLD_D, e0, e1, max(2, int(3.4 * s)))
        pygame.draw.line(surf, GOLD, e0, e1, max(1, int(2.0 * s)))
        pygame.draw.line(surf, GOLD_SPEC,
                         (e0[0], e0[1]), ((e0[0] + e1[0]) / 2, (e0[1] + e1[1]) / 2),
                         max(1, int(1.0 * s)))
        hands.append((sgn, d, hand))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1])) for h in hands]


# ── a DIM gold-bezelled turquoise inlay (the palm-skull's reliquary tell) ─────
def reliquary_inlay(surf, c, r, s, col=TURQ, br=TURQ_BR):
    """A tiny gem set in a gold bezel for the palm-skulls — the gilt-reliquary
    signature, but kept DIM on the value ladder. WHY a hand-rolled mini-bezel and
    NOT cabochon(): cabochon()'s warm pale-gold facet glint would push these
    secondary stones up toward the focal brow cabochon. This stops at TURQ_BR — no
    white core, no TURQ_HOT — so the six palm gems stay a dim, even sister-tier
    while the head's third-eye keeps the single brightest pixel."""
    cx, cy = int(c[0]), int(c[1])
    # gold bezel ring (the setting that says reliquary, not bare bone)
    pygame.draw.circle(surf, GOLD_D, (cx, cy), r + max(1, int(1.3 * s)))
    pygame.draw.circle(surf, GOLD, (cx, cy), r + max(1, int(1.3 * s)), max(1, int(1.0 * s)))
    # the stone, dim domed shading only
    pygame.draw.circle(surf, INK, (cx, cy), r)
    pygame.draw.circle(surf, col, (cx, cy), max(1, r - max(1, int(0.8 * s))))
    pygame.draw.circle(surf, br, (cx - int(r * 0.3), cy - int(r * 0.3)), max(1, int(r * 0.42)))


# ── a crafted TINY SKULL — six DISTINCT gilt-and-turquoise reliquary skulls ───
def craft_skull(surf, skx, sky_, sr, s, idx=0):
    """One small CRAFTED gilt-and-turquoise RELIQUARY skull — RATNA's signature.
    WHY a per-`idx` cabinet of traits rather than a base + flags: round 4's six
    were one craft_skull re-dressed and read as a set of near-clones. Here each
    `idx` (0-5) picks a DISTINCT cranium silhouette and proportion (tall ogival,
    broad squat, narrow oval, heart-domed, etc.), its own gilt ornament (a gold
    brow-fillet, lotus-petal etchings, a beaded/filigree suture, a gold-rimmed
    crown rosette, varied jaw treatment), and a DIM turquoise inlay only on three
    of the six. The MID value rung holds (flat bone, no white sheen, gems capped
    at TURQ_BR — never TURQ_HOT / white) so the palm-skulls stay under the focal
    brow cabochon and above the dim crown."""
    # per-idx character cabinet — the six reliquary identities. tilt is the head
    # cant; (wx, hy_top, hy_bot) reshape the cranium; the booleans select ornament.
    SPEC = [
        # idx 0 — TALL OGIVAL reliquary, gold brow-fillet + brow inlay, closed jaw
        dict(tilt=-0.30, wx=0.82, top=1.18, bot=0.96, jaw="round", suture="beaded",
             fillet=True, petals=False, rosette=False, gem=True, lit=False),
        # idx 1 — BROAD SQUAT reliquary, lotus-petal etched dome, lit socket, agape
        dict(tilt=0.14, wx=1.16, top=0.86, bot=1.02, jaw="open", suture="plain",
             fillet=False, petals=True, rosette=False, gem=False, lit=True),
        # idx 2 — NARROW OVAL reliquary, crown rosette + brow inlay, gentle agape
        dict(tilt=-0.08, wx=0.80, top=1.04, bot=1.10, jaw="open", suture="filigree",
             fillet=False, petals=False, rosette=True, gem=True, lit=False),
        # idx 3 — HEART-DOMED reliquary, gold fillet + petal etch + brow inlay
        dict(tilt=0.26, wx=1.02, top=1.10, bot=0.90, jaw="round", suture="beaded",
             fillet=True, petals=True, rosette=False, gem=True, lit=False),
        # idx 4 — ROUND CHERUB reliquary, filigree suture, lit socket, fanged jaw
        dict(tilt=-0.20, wx=1.04, top=1.00, bot=1.04, jaw="fanged", suture="filigree",
             fillet=False, petals=False, rosette=True, gem=False, lit=True),
        # idx 5 — ANGULAR LANTERN reliquary, petal etch, square agape jaw, no gem
        dict(tilt=0.10, wx=0.92, top=0.94, bot=1.16, jaw="square", suture="plain",
             fillet=False, petals=True, rosette=False, gem=False, lit=False),
    ][idx % 6]
    tilt = SPEC["tilt"]
    ca, sa = math.cos(tilt), math.sin(tilt)

    def R(px, py):   # rotate a local offset by `tilt` about the skull centre
        return (skx + px * ca - py * sa, sky_ + px * sa + py * ca)

    skbone = lerp(BONE, BONE_D, 0.45)
    wx = SPEC["wx"]          # cranium width factor
    top = SPEC["top"]        # how far the dome rises (silhouette tell)
    bot = SPEC["bot"]        # how far the face/jaw drops

    # cranium SILHOUETTE — a per-idx polygon, NOT a shared circle, so the six read
    # as different skull shapes at a glance (the core of the individuation push).
    dome = []
    for k in range(13):
        a = math.pi + math.pi * (k / 12)            # sweep the upper dome
        rr = sr * (top if math.sin(a) < 0 else 1.0)
        dome.append(R(math.cos(a) * sr * wx, math.sin(a) * rr))
    # lower cheeks taper in toward the jaw — gives each skull its facial wedge
    dome.append(R(sr * wx * 0.78, sr * 0.46))
    dome.append(R(-sr * wx * 0.78, sr * 0.46))
    triad_blob(surf, skbone, dome, ow=max(1, int(1.2 * s)))

    # brow RIDGE — a short ink arc across the upper face (the carved tell)
    pygame.draw.arc(surf, BONE_DD,
                    (skx - int(sr * 0.7 * wx), sky_ - int(sr * 0.5),
                     int(sr * 1.4 * wx), int(sr * 0.9)),
                    math.radians(205), math.radians(335), max(1, int(1.3 * s)))

    # central SUTURE down the crown — three distinct treatments per idx so the
    # gilt-reliquary read changes hand to hand (beaded / filigree / plain).
    su_top, su_bot = -sr * top * 0.96, -sr * 0.10
    if SPEC["suture"] == "beaded":
        steps = 4
        for k in range(steps + 1):
            t = k / steps
            p = R(0, su_top + (su_bot - su_top) * t)
            pygame.draw.circle(surf, GOLD_D, (int(p[0]), int(p[1])), max(1, int(1.1 * s)))
            pygame.draw.circle(surf, GOLD, (int(p[0]), int(p[1])), max(1, int(0.7 * s)))
    elif SPEC["suture"] == "filigree":
        prev = R(0, su_top)
        for k in range(1, 7):
            t = k / 6
            off = (sr * 0.16) * (1 if k % 2 else -1)
            p = R(off, su_top + (su_bot - su_top) * t)
            pygame.draw.line(surf, BONE_DD, prev, p, max(1, int(0.9 * s)))
            prev = p
    else:
        pygame.draw.line(surf, BONE_DD, R(0, su_top), R(0, su_bot), max(1, int(1.0 * s)))
        for sgn in (-1, 1):   # a couple of short suture branches
            pygame.draw.line(surf, BONE_DD, R(0, -sr * 0.62),
                             R(sgn * sr * 0.32, -sr * 0.78), max(1, int(0.8 * s)))

    # fine LOTUS-PETAL etchings fanning over the cranium — the gilt-engraving tell
    # (her sister signature). Hairline gold strokes, kept thin so they read as
    # engraving, not jewellery, and never out-shine a set stone.
    if SPEC["petals"]:
        for k in range(-2, 3):
            a = -math.pi / 2 + k * 0.42
            p0 = R(math.cos(a) * sr * 0.30, -sr * 0.30 + math.sin(a) * sr * 0.20)
            p1 = R(math.cos(a) * sr * 0.72 * wx, -sr * 0.74 + math.sin(a) * sr * 0.10)
            pygame.draw.line(surf, GOLD_D, p0, p1, max(1, int(0.8 * s)))

    # a thin gold BROW-FILLET band hugging the brow — a reliquary diadem (HERO etch)
    if SPEC["fillet"]:
        f0 = R(-sr * 0.66 * wx, -sr * 0.32)
        f1 = R(sr * 0.66 * wx, -sr * 0.32)
        pygame.draw.line(surf, GOLD_D, f0, f1, max(2, int(2.2 * s)))
        pygame.draw.line(surf, GOLD, f0, f1, max(1, int(1.2 * s)))

    # a small gold-rimmed crown ROSETTE set at the apex of the dome (relief boss)
    if SPEC["rosette"]:
        rc = R(0, -sr * top * 0.78)
        rr = max(1, int(sr * 0.18))
        pygame.draw.circle(surf, GOLD_D, (int(rc[0]), int(rc[1])), rr + max(1, int(0.8 * s)))
        pygame.draw.circle(surf, GOLD, (int(rc[0]), int(rc[1])), rr)
        pygame.draw.circle(surf, GOLD_BR, (int(rc[0] - rr * 0.3), int(rc[1] - rr * 0.3)),
                           max(1, int(rr * 0.4)))

    # temple / cheek HOLLOWS — a darker bone pocket on each side
    for sgn in (-1, 1):
        hc = R(sgn * sr * 0.62 * wx, sr * 0.18)
        pygame.draw.circle(surf, BONE_D, (int(hc[0]), int(hc[1])), max(1, int(sr * 0.22)))

    # JAW — four distinct treatments per idx (round chin / dropped agape / square
    # lantern / fanged) so the lower face individuates as much as the cranium.
    jaw_kind = SPEC["jaw"]
    jdrop = (jaw_kind in ("open", "square", "fanged"))
    jh = (1.15 if jdrop else 0.95) * bot
    jw = 0.60 if jdrop else 0.55
    if jaw_kind == "square":
        jaw = [R(-sr * jw, sr * 0.42 * bot), R(sr * jw, sr * 0.42 * bot),
               R(sr * jw * 0.92, sr * jh), R(-sr * jw * 0.92, sr * jh)]
    else:
        jaw = [R(-sr * jw, sr * 0.42 * bot), R(sr * jw, sr * 0.42 * bot),
               R(sr * 0.30, sr * jh), R(-sr * 0.30, sr * jh)]
    triad_blob(surf, skbone, jaw, ow=max(1, int(1.0 * s)))
    # TEETH along the jaw line; the fanged variant grows two corner canines.
    ty = sr * (0.50 if jdrop else 0.42) * bot
    for k in (-1, 0, 1):
        t0 = R(k * sr * 0.26, ty)
        t1 = R(k * sr * 0.26, ty + sr * 0.26)
        pygame.draw.line(surf, INK, t0, t1, max(1, int(0.9 * s)))
    if jaw_kind == "fanged":
        for sgn in (-1, 1):
            f0 = R(sgn * sr * 0.40, ty)
            f1 = R(sgn * sr * 0.40, ty + sr * 0.40)
            pygame.draw.line(surf, INK, f0, f1, max(1, int(1.4 * s)))

    # SOCKETS — deep ink eyes; one may be turquoise-lit (a DIM accent, capped at
    # TURQ_BR so it never rivals the head's hot focal).
    for i, sgn in enumerate((-1, 1)):
        ec = R(sgn * sr * 0.40 * wx, -sr * 0.02)
        pygame.draw.circle(surf, INK, (int(ec[0]), int(ec[1])), max(1, int(sr * 0.30)))
        if SPEC["lit"] and i == 0:
            # same desaturation + value drop as the brow inlay (applied to BOTH lit
            # palm skulls) so the palm turquoise gem elements stay one even dim rung
            # below the head's focal brow cabochon, symmetric across the arc.
            pygame.draw.circle(surf, lerp(TURQ, TURQ_D, 0.12),
                               (int(ec[0]), int(ec[1])), max(1, int(sr * 0.18)))
            pygame.draw.circle(surf, lerp(TURQ_BR, TURQ, 0.18),
                               (int(ec[0]), int(ec[1])), max(1, int(sr * 0.09)))
    # nasal notch
    nc = R(0, sr * 0.40 * bot)
    pygame.draw.circle(surf, INK, (int(nc[0]), int(nc[1])), max(1, int(sr * 0.13)))

    # the DIM turquoise brow INLAY in a gold bezel — three of six carry it (the
    # reliquary signature). No white hotspot, capped at TURQ_BR, so it stays well
    # under the focal head cabochon on the value ladder.
    if SPEC["gem"]:
        gc = R(0, -sr * 0.46)
        # ALL gem palm-skulls take the SAME desaturation + value drop (lerp the
        # inlay fill + sheen toward the deep turquoise shade) so the mirrored
        # six-arm arc stays symmetric and no single palm inlay (the upper-left one
        # in particular) reads as a second focal beside the head's brow cabochon.
        # Passed into reliquary_inlay's own draw colours so it renders at EVERY gem
        # skull, not one — the previous idx-gated dim never moved pixels.
        reliquary_inlay(surf, gc, max(1, int(sr * 0.26)), s,
                        col=lerp(TURQ, TURQ_D, 0.12), br=lerp(TURQ_BR, TURQ, 0.18))


# ── an open palm cradling a TINY SKULL (the brood motif) ──────────────────────
def palm_skull(surf, hx, hy, s, ang, idx=0):
    """An actual OPEN bone PALM cradling ONE crafted tiny skull — the locked brood
    motif. WHY the hand now LEADS: with the skull shrunk (~30% smaller) the cradle
    must carry the read, so this draws a wrist-cuff + bone half-cup PLUS individual
    finger SEGMENTS — each finger a two-bone digit with a knuckle tick — fanning up
    around the skull, the dome seated just above the fingertips. `idx` (0-5) drives
    light variety: skull tilt, jaw, and which 2-3 carry a DIM turquoise gem element
    so all six read as the same set with character, never clones."""
    # Local frame: u = OUTWARD (the way the palm faces / opens, away from torso);
    # v = across the wrist. The hand is a palm-up cup: bowl + fingers are nearer
    # the torso (-u side); the skull sits in the bowl, dome rising OUT along +u.
    ux, uy = math.cos(ang), math.sin(ang)
    vx, vy = -uy, ux
    # cup grown to match the LARGER skull (sr 6.5*s) so the bigger dome still
    # nests cleanly inside the fingertips without overflowing the hand.
    cupr = 9.5 * s

    def L(p):   # project local (out, side) into screen space about the bowl
        return (bx + ux * p[0] + vx * p[1], by + uy * p[0] + vy * p[1])

    # bowl centre sits a touch back toward the wrist so the skull dome leads.
    bx = hx - ux * cupr * 0.30
    by = hy - uy * cupr * 0.30

    # (1) thin gold WRIST-CUFF across the wrist on the near-torso side — a BAND,
    # not an enclosing bezel (the bezel is what made round 1 a medallion). A second
    # hairline rail makes the cuff read as a crafted band, not a smear.
    w0 = L((-cupr * 1.0, -cupr * 0.98))
    w1 = L((-cupr * 1.0, cupr * 0.98))
    pygame.draw.line(surf, GOLD_D, w0, w1, max(2, int(3.4 * s)))
    pygame.draw.line(surf, GOLD, w0, w1, max(1, int(1.9 * s)))
    pygame.draw.line(surf, GOLD_SPEC,
                     (w0[0], w0[1]), ((w0[0] + w1[0]) / 2, (w0[1] + w1[1]) / 2),
                     max(1, int(0.9 * s)))

    # (2) the bone half-CUP / palm — a shallow bowl open toward +u (outward), with
    # a darker palm-hollow core so the cup reads as a cupped hand, not a flat fan.
    cup = [L((-cupr * 0.85, -cupr * 1.0))]
    for k in range(9):
        a = math.pi - math.pi * (k / 8)        # sweep the bowl underside
        cup.append(L((-math.cos(a) * cupr * 0.55 - cupr * 0.15,
                      math.sin(a) * cupr * 1.0)))
    cup.append(L((-cupr * 0.85, cupr * 1.0)))
    triad_blob(surf, BONE, cup,
               core_pts=[L((-cupr * 0.6, -cupr * 0.55)), L((cupr * 0.05, -cupr * 0.6)),
                         L((cupr * 0.05, cupr * 0.6)), L((-cupr * 0.6, cupr * 0.55))],
               ow=max(1, int(1.3 * s)))

    # (3) FINGERS — four segmented digits (proximal + distal bone with a knuckle
    # tick) + a thumb, fanning UP/OUT from the front rim around the skull. Drawing
    # real segments is what makes the detailed HAND lead now the skull is small.
    finger_specs = [(-0.98, 0.50, 0.92),   # thumb (near side, shorter)
                    (-0.42, 0.92, 1.04),
                    (0.30, 0.92, 1.06),
                    (0.98, 0.78, 0.96)]
    for side, mid_reach, tip_reach in finger_specs:
        root = L((cupr * 0.12, side * cupr))
        knuck = L((cupr * mid_reach, side * cupr * 0.85))
        tip = L((cupr * tip_reach + cupr * 0.32, side * cupr * 0.70))
        # proximal bone
        pygame.draw.line(surf, INK, root, knuck, max(2, int(3.0 * s)))
        pygame.draw.line(surf, BONE, root, knuck, max(1, int(1.9 * s)))
        # knuckle tick
        pygame.draw.circle(surf, BONE_D, (int(knuck[0]), int(knuck[1])), max(1, int(1.5 * s)))
        pygame.draw.circle(surf, INK, (int(knuck[0]), int(knuck[1])), max(1, int(1.5 * s)),
                           max(1, int(0.7 * s)))
        # distal bone
        pygame.draw.line(surf, INK, knuck, tip, max(2, int(2.6 * s)))
        pygame.draw.line(surf, BONE, knuck, tip, max(1, int(1.6 * s)))
        # fingertip nub
        pygame.draw.circle(surf, BONE, (int(tip[0]), int(tip[1])), max(1, int(1.5 * s)))
        pygame.draw.circle(surf, INK, (int(tip[0]), int(tip[1])), max(1, int(1.5 * s)),
                           max(1, int(0.7 * s)))

    # (4) the cradled SKULL — re-seated in the grown cup just above the fingertips
    # so the dome leads while still nesting cleanly. `idx` now drives a full per-
    # skull identity (distinct cranium silhouette + gilt ornament + jaw + DIM
    # turquoise inlay on three of six) so the six read as six DISTINCT elegant
    # reliquaries, not one craft_skull re-dressed.
    sc = L((cupr * 0.58, 0.0))
    skx, sky_ = int(sc[0]), int(sc[1])
    sr = int(6.5 * s)
    craft_skull(surf, skx, sky_, sr, s, idx=idx)


# ── the jewel-lotus throne mother ─────────────────────────────────────────────
def draw_ratna_padmini(surf, cx, cy, s, hero=True):
    """Pint-sized jewel-lotus throne mother: a squat MUKHA chibi torso on a wide
    tiered gem-tipped lotus throne, framed by a FULL enclosing gold-turquoise
    flame-halo, under a six-arm radial fan whose palms each cradle a tiny skull.
    A gem-studded fused crown (Citipati 5-skull arc + Mukha tiara-band + turquoise
    brow-cabochons) tops the head; a turquoise third-eye slit is the single
    brightest pixel. `s` = unit scale around a ~150-unit figure."""

    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)

    # === FULL ENCLOSING FLAME-HALO (drawn FIRST → behind everything) ==========
    # WHY it wraps the whole figure, not just the head: a prabhamandala encloses
    # the deity. Centred low between head and torso so head, throne, and fan all
    # sit inside the ring. This is the locked 32px silhouette element.
    halo_c = (cx, cy - int(2 * s))
    flame_halo(surf, halo_c[0], halo_c[1], int(82 * s), s, lobes=24, reach=1.0,
               full=True, hero=hero)

    # === SIX-ARM RADIAL FAN (behind torso & head, frames the face) ============
    # WHY origin lifted (was hr*0.82): round 1's lower wrists sank behind the
    # throne rim + necklace, hiding ~half the palm-skulls. A higher shoulder pulls
    # all six hand-tips up so every wrist clears the throne and reads in full.
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.55), s, hr)

    # === TIERED GEM-TIPPED LOTUS THRONE (the wide MUKHA base, enriched) =======
    # WHY a tiered throne, not a flat base: three stacked petal tiers read as a
    # high-end throne. Per-petal gold-tipped gems are HERO-only; at 32px the
    # stacked tiers collapse to one wide pedestal mass under the body.
    base_y = cy + int(44 * s)
    for tier, (half, lift, pet) in enumerate(((40, 0, 6), (32, 14, 5), (24, 26, 4))):
        ty = base_y - int(lift * s)
        hw = int(half * s)
        petal = [(cx - hw, ty - int(6 * s)),
                 (cx - int(hw * 0.7), ty - int(13 * s)),
                 (cx + int(hw * 0.7), ty - int(13 * s)),
                 (cx + hw, ty - int(6 * s)),
                 (cx + int(hw * 0.8), ty + int(10 * s)),
                 (cx - int(hw * 0.8), ty + int(10 * s))]
        triad_blob(surf, BONE, petal,
                   core_pts=[(cx, ty - int(12 * s)), (cx + hw, ty - int(6 * s)),
                             (cx + int(hw * 0.8), ty + int(8 * s)), (cx, ty + int(6 * s))],
                   ow=max(1, int(1.6 * s)))
        # per-petal grooves + a gold-tipped gem in each petal (HERO inlay)
        for k in range(-(pet // 2), pet // 2 + 1):
            px = cx + int(k * (2 * half / max(1, pet)) * s)
            pygame.draw.line(surf, BONE_DD, (px, ty - int(12 * s)),
                             (px, ty + int(8 * s)), max(1, int(1.3 * s)))
            cabochon(surf, (px, ty - int(8 * s)), max(1, int(2.6 * s)), s,
                     CORAL if (k % 2) else TURQ, CORAL_BR if (k % 2) else TURQ_BR)
    # a turquoise seed-cabochon at the lotus heart — kept BELOW the third-eye so
    # it stays a secondary focal, never the brightest pixel.
    cabochon(surf, (cx, base_y - int(20 * s)), int(5 * s), s, TURQ, TURQ_BR)

    # ONE dark value-break where the torso meets the throne — a deep bone-hollow
    # shadow line. WHY: at night-32px the pale body mass + throne fused into one
    # blob; this seam (plus the dark eye-sockets) splits it into face-vs-throne.
    seam_y = cy + int(24 * s)
    pygame.draw.line(surf, BONE_DD,
                     (cx - int(26 * s), seam_y), (cx + int(26 * s), seam_y),
                     max(2, int(3.4 * s)))
    pygame.draw.line(surf, INK,
                     (cx - int(20 * s), seam_y + int(2 * s)),
                     (cx + int(20 * s), seam_y + int(2 * s)), max(1, int(1.6 * s)))

    # === TORSO — a SHORT MUKHA rib barrel (squat, mass held low) ==============
    rc_cx, rc_cy = cx, cy + int(12 * s)
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

    # === JEWELLED BEADWORK NECKLACE + a GOLD INLAY GIRDLE (HERO ornament) =====
    # WHY a 3-bead choker + a swag of cabochons across the chest: she must never
    # read naked — beadwork wraps the torso. All HERO-only; at 32px it collapses
    # into the torso mass under the halo. Gold girdle band at the waist.
    neck_y = rc_cy - rc_h // 2 + int(3 * s)
    swag = []
    for k in range(-3, 4):
        sxp = rc_cx + int(k * 5 * s)
        syp = neck_y + int(7 * s) + int(abs(k) * 1.4 * s)
        swag.append((sxp, syp))
    pygame.draw.lines(surf, GOLD_D, False, swag, max(1, int(2.0 * s)))
    for (sxp, syp) in swag:
        cabochon(surf, (sxp, syp), max(1, int(2.2 * s)), s, TURQ, TURQ_BR)
    # the gold girdle band at the waist with a coral centre cabochon
    gy = rc_cy + int(rc_h * 0.36)
    pygame.draw.line(surf, INK, (rc_cx - int(rc_w * 0.42), gy),
                     (rc_cx + int(rc_w * 0.42), gy), max(2, int(4.0 * s)))
    pygame.draw.line(surf, GOLD, (rc_cx - int(rc_w * 0.42), gy),
                     (rc_cx + int(rc_w * 0.42), gy), max(1, int(2.4 * s)))
    cabochon(surf, (rc_cx, gy), max(1, int(2.8 * s)), s, CORAL, CORAL_BR)

    # === SIX PALM-SKULLS — one cradled in each open palm (the motif) ==========
    for i, (hx, hy) in enumerate(hands):
        oa = math.atan2(hy - rc_cy, hx - rc_cx)
        palm_skull(surf, hx, hy, s, oa, idx=i)

    # === CORAL TASSELS — one off EACH lower palm-cuff (both sides) ============
    # WHY one per side, not two on one side: round 1 hung both bottom-left and the
    # warm accent framed the throne lopsidedly. Splitting the hands by side and
    # taking the lowest of each gives a symmetric coral frame. Sub-pixel at 32px
    # → hero-only.
    mid_x = cx
    left = [h for h in hands if h[0] < mid_x]
    right = [h for h in hands if h[0] >= mid_x]
    low = []
    if left:
        low.append(max(left, key=lambda h: h[1]))
    if right:
        low.append(max(right, key=lambda h: h[1]))
    for (hx, hy) in low:
        tassel(surf, hx, hy + int(9 * s), int(16 * s), s)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (the framed FACE) =========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two lower sockets — scary-CUTE, kept dimmer than the third eye (the ladder)
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, TURQ_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # THIRD EYE — a SOFT ROUNDED turquoise CABOCHON in a gold bezel, the single
    # BRIGHTEST pixel (AD hard rule). WHY a smooth domed cabochon, NOT a faceted
    # cut stone: the focal reads as a polished gem — a stacked dome of concentric
    # ellipses (deep-ink base → turquoise body → bright mid-sheen → hot core →
    # a tiny pure-white hotspot pip). The white pip wins the value ladder by 40+
    # over every warm pale-gold bead glint, the flat-dark crown sockets, and the
    # DIM turquoise palm-skull accents.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    gr = int(8.5 * s)
    # gold bezel around the cabochon (the setting)
    triad_circle(surf, GOLD, (tex, tey), gr + max(1, int(2.2 * s)),
                 ow=max(1, int(1.6 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, GOLD_D, (tex, tey), gr + max(1, int(2.2 * s)), max(1, int(1.3 * s)))
    # the domed stone: concentric ellipses from deep-ink base up to a hot core
    pygame.draw.ellipse(surf, INK, (tex - gr - int(1 * s), tey - gr - int(1 * s),
                                    (gr + int(1 * s)) * 2, (gr + int(1 * s)) * 2))
    pygame.draw.ellipse(surf, TURQ, (tex - gr, tey - gr, gr * 2, gr * 2))
    mr = int(gr * 0.66)
    pygame.draw.ellipse(surf, TURQ_BR,
                        (tex - mr - int(gr * 0.18), tey - mr - int(gr * 0.22),
                         mr * 2, mr * 2))
    cr = int(gr * 0.34)
    pygame.draw.ellipse(surf, TURQ_HOT,
                        (tex - cr - int(gr * 0.22), tey - cr - int(gr * 0.26),
                         cr * 2, cr * 2))
    # the single brightest pixel: a tiny pure-white hotspot pip, top-left
    pygame.draw.circle(surf, (255, 255, 255),
                       (tex - int(gr * 0.24), tey - int(gr * 0.28)), max(1, int(gr * 0.16)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # gentle grinning tooth row (the gentlest sister — softer grin, no fangs)
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.44), my),
                     (head_c[0] + int(hr * 0.44), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.14), my - int(hr * 0.08)),
                         (head_c[0] + int(k * hr * 0.14), my + int(hr * 0.11)), max(1, int(1 * s)))

    # === FUSED GEM-STUDDED CROWN — Citipati arc-SWEEP + Mukha tiara-BAND =======
    # WHY both crown languages, fused: the locked rule. A WIDE 5-skull arc rides
    # the OUTER silhouette (the Citipati sweep) AND a gold tiara-band seats across
    # the brow with turquoise brow-cabochons (the Mukha band) — both visibly
    # present. Crown skulls are the DIMMEST rung of the value ladder; only the
    # centre skull is lit turquoise (the one crown glow).

    # (1) the Mukha tiara-BAND seated on the brow — a CONTINUOUS gold band
    # brow-to-temple with cabochons set INTO it. WHY a denser continuous rail
    # (was reading as three loose gems): a wide ink-backed gold band sweeps the
    # whole brow arc, then a thin bright 2px gold rail runs its full length so the
    # eye reads an unbroken BAND; the three cabochons are studs ON that band.
    tiara_r = int(hr * 0.98)
    band_pts = []
    for i in range(21):
        a = math.radians(228 + i * (84 / 20))   # seated low across the brow→temple
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(8 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, int(5 * s))
    # the continuous bright rail that makes it read as ONE band, not loose gems
    pygame.draw.lines(surf, GOLD_BR, False, band_pts, max(2, int(2.0 * s)))
    # three turquoise brow-cabochons studding the band (HERO inlay)
    for i in (3, 10, 17):
        bx, by = band_pts[i]
        cabochon(surf, (bx, by), max(1, int(2.8 * s)), s, TURQ, TURQ_BR)

    # (2) the Citipati 5-skull arc-SWEEP riding the OUTER crown silhouette
    skull_cr = hr * 1.46
    skull_r = int(hr * 0.34)
    for i in range(5):
        a = math.radians(218 + i * (104 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = head_c[1] + math.sin(a) * skull_cr
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2), idx=i)


# ── the jewel-lotus throne → pillar mirror ────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom", hero=True):
    """The jewel-lotus throne IS the pillar: a stacked column of tiered lotus
    thrones (her own base, repeated) threaded on a gold rod = the tileable shaft;
    the gap-edge cap is a single gem-tipped lotus blossom inside a small CLOSED
    flame-ring with a glowing turquoise cabochon at the hub — her own forms,
    symmetric and on-axis, never top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(14 * s)
    # central gold rod the lotus tiers thread onto (her treasure metal)
    pygame.draw.rect(surf, INK, (cx - int(4 * s), top, int(8 * s), bot - top))
    pygame.draw.rect(surf, GOLD_D, (cx - int(3 * s), top, int(6 * s), bot - top))

    tier_pitch = int(26 * s)
    cap_room = int(38 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    idx = 0
    while y <= b1:
        # one lotus-throne tier: a wide petal block with per-petal grooves and a
        # cabochon at the centre (the hero inlay; at 32px the petal mass tiles).
        bw = shaft_w
        petal = [(cx - bw, y - int(9 * s)),
                 (cx - int(bw * 0.6), y - int(13 * s)),
                 (cx + int(bw * 0.6), y - int(13 * s)),
                 (cx + bw, y - int(9 * s)),
                 (cx + int(bw * 0.78), y + int(9 * s)),
                 (cx - int(bw * 0.78), y + int(9 * s))]
        triad_blob(surf, BONE, petal,
                   core_pts=[(cx, y - int(12 * s)), (cx + bw, y - int(9 * s)),
                             (cx + int(bw * 0.78), y + int(8 * s)), (cx, y + int(6 * s))],
                   sheen_pts=[(cx - bw, y - int(9 * s)), (cx - int(bw * 0.6), y - int(12 * s)),
                              (cx - int(bw * 0.3), y - int(9 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        for k in (-2, -1, 0, 1, 2):
            px = cx + int(k * bw * 0.38)
            pygame.draw.line(surf, BONE_DD, (px, y - int(12 * s)),
                             (px, y + int(7 * s)), max(1, int(1.2 * s)))
        cabochon(surf, (cx, y - int(3 * s)), max(1, int(3.4 * s)), s,
                 TURQ if (idx % 2 == 0) else CORAL,
                 TURQ_BR if (idx % 2 == 0) else CORAL_BR)
        # a coral tassel hung off alternating sides (hero beadwork)
        side = -1 if (idx % 2 == 0) else 1
        tassel(surf, cx + side * (bw + int(3 * s)), y + int(2 * s), int(10 * s), s)
        idx += 1
        y += tier_pitch

    # === gap-edge cap: gem-tipped lotus blossom in a small CLOSED flame-ring ===
    cap_y = (bot - int(22 * s)) if cap == "bottom" else (top + int(22 * s))
    # the small closed flame-ring (her prabhamandala in miniature)
    flame_halo(surf, cx, cap_y, int(18 * s), s, lobes=14, reach=0.9, full=True, hero=hero)
    grow = +1 if cap == "bottom" else -1
    # a lotus blossom opening toward the gap
    for k in range(7):
        a = (math.radians(-90 + (k - 3) * 24) if grow > 0
             else math.radians(90 + (k - 3) * 24))
        tip = (cx + math.cos(a) * int(15 * s), cap_y + math.sin(a) * int(15 * s))
        pygame.draw.line(surf, INK, (cx, cap_y), tip, max(2, int(4 * s)))
        pygame.draw.line(surf, BONE, (cx, cap_y), tip, max(1, int(2.4 * s)))
        triad_circle(surf, BONE, (int(tip[0]), int(tip[1])), max(1, int(2.4 * s)),
                     ow=max(1, int(1 * s)), core=False, sheen=False)
    # gold collar where the blossom meets the shaft
    collar_y = cap_y - grow * int(22 * s)
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # the glowing turquoise cabochon at the blossom hub (the gap glow)
    cabochon(surf, (cx, cap_y), int(6 * s), s, TURQ, TURQ_BR, glow=True)


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def render_hero(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_ratna_padmini(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def export_hero():
    """Standalone hi-res hero PNG (~1024px tall) per the higher-res brief."""
    HW, HH = 820, 1024
    big = pygame.Surface((HW * 2, HH * 2), pygame.SRCALPHA)
    draw_ratna_padmini(big, HW, int(HH * 1.04), 5.6)
    hero = pygame.transform.smoothscale(big, (HW, HH))
    hero = grow_outline(hero, INK + (255,), 2)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_7_hero.png")
    pygame.image.save(hero, out)
    print("wrote", out)
    return out


def main():
    W, H = 1040, 860
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("#3 — RATNA-PADMINI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "jewel-lotus throne mother  ·  mukha_citipati_court #5 · MUKHA body · turquoise+gold+coral · "
        "FULL enclosing flame-halo (the only sister) · round 7",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    hero = render_hero(380, 500, 188, 256, 1.95)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero (SS=8)", True, LABEL), (110, 596))
    sheet.blit(font_sm.render("FULL halo · 6 HANDS each cradle a DISTINCT gilt-turquoise RELIQUARY skull (own cranium/jaw/etch/suture; 3 w/ DIM turquoise inlay).", True, LABEL_DIM), (14, 620))
    sheet.blit(font_sm.render("Fused crown: 5 DISTINCT gilded-reliquary skulls (ogival/squat/heart-centre/oval/lantern silhouettes; beaded/filigree/petal/fillet/rosette gilt) + Mukha gold tiara-BAND.", True, LABEL_DIM), (14, 636))
    sheet.blit(font_sm.render("Brow third-eye = SOFT ROUNDED turquoise cabochon (gold bezel + domed sheen + white hotspot pip) = single brightest pixel.", True, LABEL_DIM), (14, 652))

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
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — jewel-lotus throne", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked lotus-throne tiers on a gold rod =", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("shaft; gem-lotus blossom + closed flame-ring", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("+ glowing turquoise cabochon caps the gap", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips (day+night), blackout proof, palette =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 588))
    sheet.blit(font.render("True 32px gameplay-scale", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((120 * SS, 120 * SS), pygame.SRCALPHA)
        draw_ratna_padmini(big, 60 * SS, 62 * SS, (32 / 150.0) * SS, hero=False)
        small = pygame.transform.smoothscale(big, (120, 120))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 15, day_y + 15))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 15, night_y + 15))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout / silhouette proof — fill the chip's alpha solid to read the shape
    def blackout32():
        big = pygame.Surface((120 * SS, 120 * SS), pygame.SRCALPHA)
        draw_ratna_padmini(big, 60 * SS, 62 * SS, (32 / 150.0) * SS, hero=False)
        small = pygame.transform.smoothscale(big, (120, 120))
        mask = pygame.mask.from_surface(small)
        sil = mask.to_surface(setcolor=(20, 18, 24, 255), unsetcolor=(0, 0, 0, 0))
        return sil

    bo = blackout32()
    px2 = panel_x + 192
    pygame.draw.rect(sheet, (214, 214, 220), (px2, day_y, 150, 150))
    pygame.draw.rect(sheet, INK, (px2, day_y, 150, 150), 1)
    sheet.blit(bo, (px2 + 15, day_y + 15))
    sheet.blit(font_sm.render("blackout proof", True, LABEL), (px2, day_y + 156))
    sheet.blit(font_sm.render("(halo RING carries", True, LABEL_DIM), (px2, day_y + 172))
    sheet.blit(font_sm.render(" the 32px silhouette)", True, LABEL_DIM), (px2, day_y + 186))

    # a 32px pillar chip on both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom", hero=False)
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px3 = panel_x + 192
    vgrad(sheet, (px3, night_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px3, night_y, 56, 150), 1)
    sheet.blit(pc, (px3 + 6, night_y + 10))
    vgrad(sheet, (px3 + 64, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px3 + 64, night_y, 56, 150), 1)
    sheet.blit(pc, (px3 + 70, night_y + 10))
    sheet.blit(font_sm.render("pillar 32px (day / night)", True, LABEL_DIM), (px3, night_y + 156))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 524))
    swatches = [
        (BONE, "warm pale bone"), (GOLD, "lavish gold"),
        (TURQ, "turquoise focal"), (TURQ_HOT, "third-eye core"),
        (CORAL, "coral tassel"), (GOLD_D, "deep-gold inlay"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 552
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 168
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 808, W - 28, 44))
    sheet.blit(font_sm.render(
        "HIGH-RES pipeline: SS=8 supersample -> smoothscale; standalone round_7_hero.png ~1024px tall.  "
        "STAY: flat fills · ink keyline (28,22,26) · dark-core->fill->top-left sheen triad · 1px grown outline · "
        "chibi scary-cute · procedural-only.  Round 7: palm-skull turquoise inlays + lit-sockets dimmed ~12% (symmetric).",
        True, LABEL_DIM), (26, 821))
    sheet.blit(font_sm.render(
        "Two-scale rule: the FULL flame-halo RING carries the 32px silhouette; inlay + tassels + per-petal gems are HERO-ONLY.",
        True, LABEL_DIM), (26, 837))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_7.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    return out


if __name__ == "__main__":
    export_hero()
    main()
