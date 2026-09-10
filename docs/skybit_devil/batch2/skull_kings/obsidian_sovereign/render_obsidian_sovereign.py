"""
Round-1 concept renderer for OBSIDIAN SOVEREIGN — the dark imperial monarch and
the VALUE POLE of the KING SKULL royal brood (Batch 2 / skull_kings, concept #4).
Headless Pygame; ELEVATED pipeline (supersample SS=6 -> smoothscale) so the extra
geometry stays crisp at downscale. Keeps the shipped house grammar: flat fills,
hard 1-2px ink keyline, dark-core -> flat-fill -> top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE; procedural-only (no PNGs).

WHY this concept is the value pole / anti-everyone: every other king is a
mid-to-light bone mass. The Sovereign is the ONLY near-black king and the ONLY
TALL-NARROW one — a slender monarch wrapped in a SMOOTH columnar robe that falls
unbroken to the floor. No ribs, no rib-bands, no splayed limbs: the smooth column
is what keeps him from reading as "yet another skeleton-man." His tell is shape
+ light, not bone detail.

WHY the cool blue-grey RIM-SHEEN is the make-or-break (and is engineered wide):
onyx near-black bone vanishes into the night sky (top (22,26,54)). Reusing
Koschei's iron-on-indigo night lesson, EVERY outer edge of the robe column, the
shoulders, the hood and the crown carries a wide cool blue-grey rim band so the
WHOLE silhouette stays legible at 32px night. The rim is the brightest cool
element; GOLD is the only saturated accent (crown dome, a single vertical hem
line, the sceptre) and stays the warm focal.

WHY the crown is a closed IMPERIAL DOME: every sibling has its own crown (5-skull
arc, iron spikes, amethyst cone, war-crown, coral antlers, trefoil coronet). The
Sovereign owns the only SMOOTH/ROUND crown — two crossed gold arches over a
circlet, capped by a tiny orb-and-cross finial. At 32px it reads as a single gold
domed cap, unmistakably imperial.

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
# Onyx near-black bone is the dominant MASS. It is carried on the night sky NOT
# by its own value (it has almost none) but by a wide cool blue-grey rim-sheen.
ONYX      = ( 44,  42,  52)   # onyx near-black bone (the dominant fill)
ONYX_D    = ( 28,  26,  34)   # onyx dark-core
ONYX_DD   = ( 18,  17,  24)   # deepest hollow (hood shadow, robe seam)
# the cool blue-grey RIM-SHEEN — the silhouette carrier on the night sky.
# WHY engineered cool + bright: it must out-value the night sky top (22,26,54)
# along every edge so the black mass keeps a clean outline at 32px night. Pushed
# brighter+cooler than r1 (150,165,200) so the whole tall column clears the
# night-sky value at 32px, not just the body — a dimmer rim left the lower column
# dissolving into the sky.
RIM       = (164, 178, 212)   # cool blue-grey rim-sheen (the carrier)
RIM_BR    = (212, 224, 248)   # brightest rim highlight (shoulder/crown crest)
RIM_D     = (110, 124, 162)   # rim shade (where it folds back into onyx)
# GOLD — the ONLY bright/saturated accent (crown dome, hem line, sceptre).
# WHY the body gold is pulled DOWN a notch from r1: the orb-and-cross finial must
# be the single brightest pixel, so crest-dome + hem/base gold read as structure,
# not a competing 2nd bright mass.
GOLD      = (210, 172,  78)
GOLD_BR   = (234, 200, 112)   # warm gold crest (structure — NOT the brightest)
GOLD_D    = (158, 122,  50)
GOLD_HOT  = (255, 232, 150)   # the finial ONLY — the single brightest pixel
# the eye-pins: a cold imperial pale-gold glow, kept tiny so gold stays focal.
EYE       = (236, 214, 150)
EYE_HOT   = (255, 244, 206)
INK       = ( 20,  18,  24)   # hard ink keyline (near-black, fits the onyx)
# WHY a COOL grown-outline keyline (not pure black): at 32px the 1px grown outline
# is the literal silhouette EDGE; a near-black edge vanishes on the night sky, so
# the outermost ring carries a cool blue-grey value instead — the rim and the edge
# now read as one continuous cool contour top-to-bottom on night.
INK_RIM   = ( 92, 106, 144)

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


# -- the WIDE cool rim-sheen along a directed edge (the silhouette carrier) ----
def rim_edge(surf, pts, s, width=4.6, bright=False):
    """Stroke a polyline with a WIDE cool blue-grey rim band, plus a thinner hot
    crest on the lit side. WHY a fat band, not a 1px line: onyx near-black has no
    value on the night sky, so the rim must be wide + bright enough that the band
    ITSELF carries the silhouette edge — a thin line vanishes. WHY ~4.6 units wide
    now (was 3.0): at the 32px chip scale ((32/134)*SS) a 3-unit native band
    smoothscaled down to a sub-pixel ghost and the lower column dissolved; ~4.6
    survives smoothscale to ~2px native / ~1px at the chip. The brighter inner
    crest reads as a polished obsidian sheen. Drawn AFTER the onyx fill so it sits
    on the outer contour."""
    if len(pts) < 2:
        return
    pygame.draw.lines(surf, RIM_D, False, pts, max(2, int((width + 1.6) * s)))
    pygame.draw.lines(surf, RIM, False, pts, max(2, int(width * s)))
    if bright:
        pygame.draw.lines(surf, RIM_BR, False, pts, max(1, int((width * 0.5) * s)))


# -- the closed IMPERIAL DOME crown (the only smooth/round crown — the tell) ---
def imperial_crown(surf, cx, cy, r, s):
    """A closed gold imperial dome: a circlet band, two crossed arches springing
    over it, and a tiny orb-and-cross finial. WHY closed + smooth + round: every
    sibling king has a jagged/spiky/spired crown, so the Sovereign owns the only
    domed silhouette. At 32px the crossed gold arches collapse into one solid gold
    cap, which is exactly the 32px tell. GOLD is the single bright accent and the
    finial is the single brightest pixel.

    `r` ~ head radius; the dome rides just above the crown of the skull."""
    # the circlet band (sits on the brow, the dome springs from it)
    band = [(cx - int(r * 1.04), cy + int(2 * s)),
            (cx + int(r * 1.04), cy + int(2 * s)),
            (cx + int(r * 0.96), cy + int(11 * s)),
            (cx - int(r * 0.96), cy + int(11 * s))]
    triad_blob(surf, GOLD, band,
               core_pts=[(cx - int(r * 0.6), cy + int(7 * s)),
                         (cx + int(r * 0.96), cy + int(6 * s)),
                         (cx + int(r * 0.92), cy + int(11 * s)),
                         (cx - int(r * 0.6), cy + int(11 * s))],
               sheen_pts=[(cx - int(r * 1.02), cy + int(2 * s)),
                          (cx + int(r * 0.2), cy + int(2 * s)),
                          (cx + int(r * 0.2), cy + int(5 * s)),
                          (cx - int(r * 1.02), cy + int(5 * s))],
               ow=max(1, int(1.5 * s)))
    # circlet gem ticks (tiny, kept as a thin accent)
    for fx in (-0.5, 0.0, 0.5):
        pygame.draw.circle(surf, GOLD_BR,
                           (cx + int(fx * r * 1.4), cy + int(6 * s)), max(1, int(1.6 * s)))

    # the closed DOME — a filled gold ogee dome rising from the band.
    apex_y = cy - int(r * 1.32)
    dome = []
    for k in range(25):
        t = k / 24.0
        a = math.pi * (1.0 - t)                 # left band-foot -> right band-foot
        # ogee profile: a swelling shoulder that necks toward the apex
        prof = math.sin(math.pi * t)
        bx = cx + math.cos(a) * r * 1.0
        # height blends a half-ellipse with an ogee shoulder for the imperial swell
        by = cy + int(2 * s) - prof * (cy + int(2 * s) - apex_y) * (0.86 + 0.14 * math.sin(math.pi * t))
        dome.append((bx, by))
    dome.append((cx + int(r * 1.0), cy + int(2 * s)))
    dome.append((cx - int(r * 1.0), cy + int(2 * s)))
    triad_blob(surf, GOLD, dome,
               core_pts=[(cx, cy + int(2 * s)), (cx + int(r * 0.9), cy - int(r * 0.3)),
                         (cx + int(r * 0.3), apex_y + int(6 * s)),
                         (cx, apex_y + int(4 * s))],
               sheen_pts=[(cx - int(r * 0.9), cy - int(r * 0.1)),
                          (cx - int(r * 0.2), apex_y + int(8 * s)),
                          (cx - int(r * 0.05), apex_y + int(10 * s)),
                          (cx - int(r * 0.7), cy - int(r * 0.05))],
               ow=max(1, int(1.6 * s)))

    # two crossed arch RIBS over the dome (the imperial-arch read)
    for sgn in (-1, 1):
        arch = []
        for k in range(13):
            t = k / 12.0
            x = cx + sgn * (1 - t) * r * 0.98
            y = (cy + int(2 * s)) + (apex_y - (cy + int(2 * s))) * (math.sin(math.pi * 0.5 * t))
            arch.append((x, y))
        pygame.draw.lines(surf, GOLD_D, False, arch, max(2, int(3.0 * s)))
        pygame.draw.lines(surf, GOLD_BR, False, arch, max(1, int(1.4 * s)))

    # orb-and-cross finial at the apex — the SINGLE BRIGHTEST PIXEL.
    # WHY GOLD_HOT here and nowhere else: the finial must read ~15-20% brighter
    # than the rest of the gold so the eye lands on the crown apex; every other
    # gold element (dome, hem, sceptre) sits a notch darker as structure.
    fy = apex_y - int(3 * s)
    triad_circle(surf, GOLD, (cx, fy), int(4.2 * s), ow=max(1, int(1.2 * s)), core=False)
    pygame.draw.circle(surf, GOLD_HOT, (cx - int(1 * s), fy - int(1 * s)), max(1, int(2.2 * s)))
    pygame.draw.line(surf, GOLD_HOT, (cx, fy - int(4 * s)), (cx, fy - int(11 * s)), max(2, int(2.4 * s)))
    pygame.draw.line(surf, GOLD_HOT, (cx - int(3 * s), fy - int(8 * s)),
                     (cx + int(3 * s), fy - int(8 * s)), max(1, int(2.2 * s)))


# -- the tiny skull sceptre knob (the lineage TOOLKIT tell) -------------------
def skull_knob(surf, cx, cy, r, s):
    """A tiny onyx skull knob atop the sceptre — the brood's tiny-skull toolkit,
    kept small + rim-lit so it reads as a knob, not a second head. Onyx dome with
    a cool rim crescent + two pale-gold eye dots."""
    triad_circle(surf, ONYX, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    # cool rim crescent on the top-left so the black knob survives night
    rim = [(cx + math.cos(math.radians(a)) * r,
            cy + math.sin(math.radians(a)) * r) for a in range(150, 271, 12)]
    pygame.draw.lines(surf, RIM, False, rim, max(1, int(1.4 * s)))
    # stub jaw
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)), (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 1.0)), (cx - int(r * 0.32), cy + int(r * 1.0))]
    triad_blob(surf, ONYX, jaw, ow=max(1, int(1.0 * s)))
    for ex in (cx - int(r * 0.36), cx + int(r * 0.36)):
        pygame.draw.circle(surf, INK, (ex, cy), max(1, int(r * 0.24)))
        pygame.draw.circle(surf, EYE, (ex, cy), max(1, int(r * 0.13)))


# -- the dark imperial monarch ------------------------------------------------
def draw_obsidian(surf, cx, cy, s):
    """A TALL slender dark monarch: a smooth columnar robe falling unbroken to the
    floor (the only tall-narrow + only near-black king). Two arms — one across the
    chest, one holding an upright sceptre with a tiny skull knob. A closed gold
    imperial-dome crown over a hooded onyx skull. A single vertical GOLD hem line
    runs the centre of the robe. The cool blue-grey rim-sheen wraps the whole
    silhouette so the near-black mass survives the night sky.
    `s` = unit scale around a ~134-unit-tall figure."""

    head_c = (cx, cy - int(40 * s))
    hr = int(19 * s)
    shoulder_y = cy - int(20 * s)
    hem_y = cy + int(60 * s)            # the floor — robe falls to here

    # === THE COLUMNAR ROBE (drawn first -> the dominant mass) ================
    # WHY one smooth unbroken trapezoid column: no ribs, no segmentation. A
    # tall-narrow silhouette that flares slightly at the floor like a fixed
    # imperial mantle. This single onyx mass is what makes him read as a robed
    # monarch and NOT a skeleton-man.
    top_w = int(26 * s)
    hem_w = int(40 * s)
    robe = [(cx - top_w, shoulder_y + int(4 * s)),
            (cx + top_w, shoulder_y + int(4 * s)),
            (cx + int(top_w * 0.94), cy),
            (cx + hem_w, hem_y - int(6 * s)),
            (cx + int(hem_w * 0.72), hem_y),
            (cx - int(hem_w * 0.72), hem_y),
            (cx - hem_w, hem_y - int(6 * s)),
            (cx - int(top_w * 0.94), cy)]
    triad_blob(surf, ONYX, robe,
               core_pts=[(cx, shoulder_y + int(6 * s)),
                         (cx + int(top_w * 0.9), cy),
                         (cx + hem_w, hem_y - int(6 * s)),
                         (cx + int(hem_w * 0.4), hem_y),
                         (cx, hem_y)],
               ow=max(1, int(1.8 * s)))
    # WHY no interior fold lines: a horizontal-reading fold seam mid-column got
    # mistaken for a rib band and pulled the king toward "another skeleton-man".
    # One smooth onyx column floor-to-collar — the top-left sheen from triad_blob
    # is the ONLY light on the body, no banding.

    # WIDE cool rim-sheen as ONE CONTINUOUS unbroken wrap around the whole robe
    # outline: down the left edge, across the full hem floor, up the right edge —
    # a single polyline so there are NO gaps along the lower column. WHY uniform
    # width on both sides: a thinner right edge in r1 let the lower-right column
    # dissolve into night; a balanced wide wrap keeps the tall shape legible
    # top-to-bottom. The lit (left) side then gets a brighter crest overlaid.
    column_wrap = [(cx - top_w, shoulder_y + int(4 * s)),
                   (cx - int(top_w * 0.94), cy),
                   (cx - hem_w, hem_y - int(6 * s)),
                   (cx - int(hem_w * 0.72), hem_y),
                   (cx + int(hem_w * 0.72), hem_y),
                   (cx + hem_w, hem_y - int(6 * s)),
                   (cx + int(top_w * 0.94), cy),
                   (cx + top_w, shoulder_y + int(4 * s))]
    rim_edge(surf, column_wrap, s, width=5.2, bright=True)
    # WHY a doubled-up hem floor band: the very bottom rows lost the rim to
    # smoothscale dilution and dropped out of the night row-carry gate, so the
    # full hem hem-flare gets an extra-wide cool band to hold the base edge.
    rim_edge(surf, [(cx - hem_w, hem_y - int(6 * s)),
                    (cx - int(hem_w * 0.72), hem_y),
                    (cx + int(hem_w * 0.72), hem_y),
                    (cx + hem_w, hem_y - int(6 * s))], s, width=5.4, bright=True)
    # brighter crest on the lit LEFT edge only (polished-obsidian sheen)
    left_edge = [(cx - top_w, shoulder_y + int(4 * s)),
                 (cx - int(top_w * 0.94), cy),
                 (cx - hem_w, hem_y - int(6 * s)),
                 (cx - int(hem_w * 0.72), hem_y)]
    pygame.draw.lines(surf, RIM_BR, False, left_edge, max(1, int(2.2 * s)))

    # === the single vertical GOLD HEM LINE (the 32px hem tell) ===============
    # one crisp gold seam down the centre of the robe. WHY no filled cuff at the
    # base: a bright gold block at the feet anchored the eye DOWN and competed
    # with the finial; it's now a thin hem line so the eye travels UP to the
    # orb-and-cross finial (the single brightest pixel).
    pygame.draw.line(surf, GOLD_D, (cx, shoulder_y + int(10 * s)), (cx, hem_y - int(2 * s)),
                     max(2, int(3.0 * s)))
    pygame.draw.line(surf, GOLD, (cx, shoulder_y + int(10 * s)), (cx, hem_y - int(2 * s)),
                     max(1, int(1.8 * s)))
    pygame.draw.line(surf, GOLD_BR, (cx, shoulder_y + int(12 * s)), (cx, cy + int(14 * s)),
                     max(1, int(0.9 * s)))
    # a thin gold hem LINE at the floor where the seam terminates (not a cuff block)
    pygame.draw.line(surf, GOLD_D, (cx - int(9 * s), hem_y - int(3 * s)),
                     (cx + int(9 * s), hem_y - int(3 * s)), max(2, int(2.4 * s)))
    pygame.draw.line(surf, GOLD, (cx - int(8 * s), hem_y - int(3 * s)),
                     (cx + int(8 * s), hem_y - int(3 * s)), max(1, int(1.4 * s)))

    # === SHOULDER MANTLE — a smooth onyx yoke capping the column =============
    mantle = [(cx - int(30 * s), shoulder_y + int(6 * s)),
              (cx - int(20 * s), shoulder_y - int(8 * s)),
              (cx + int(20 * s), shoulder_y - int(8 * s)),
              (cx + int(30 * s), shoulder_y + int(6 * s)),
              (cx + int(22 * s), shoulder_y + int(12 * s)),
              (cx - int(22 * s), shoulder_y + int(12 * s))]
    triad_blob(surf, ONYX, mantle,
               core_pts=[(cx - int(8 * s), shoulder_y - int(4 * s)),
                         (cx + int(20 * s), shoulder_y - int(6 * s)),
                         (cx + int(28 * s), shoulder_y + int(6 * s)),
                         (cx, shoulder_y + int(10 * s))],
               ow=max(1, int(1.6 * s)))
    # bright cool rim along the top crest of the mantle (catches the most light)
    rim_edge(surf, [(cx - int(29 * s), shoulder_y + int(5 * s)),
                    (cx - int(20 * s), shoulder_y - int(7 * s)),
                    (cx + int(20 * s), shoulder_y - int(7 * s)),
                    (cx + int(29 * s), shoulder_y + int(5 * s))], s, width=3.0, bright=True)
    # a single thin gold collar trim under the chin
    pygame.draw.line(surf, GOLD, (cx - int(16 * s), shoulder_y - int(2 * s)),
                     (cx + int(16 * s), shoulder_y - int(2 * s)), max(1, int(2.0 * s)))
    pygame.draw.line(surf, GOLD_BR, (cx - int(14 * s), shoulder_y - int(3 * s)),
                     (cx + int(2 * s), shoulder_y - int(3 * s)), max(1, int(1.0 * s)))

    # === ARMS — two, drawn as smooth onyx robe-sleeves (no exposed bone) ======
    # WHY sleeves, not bone limbs: bone arms would re-introduce the skeleton-man
    # read the brief forbids. The left sleeve folds across the chest; the right
    # sleeve drops to grip the upright sceptre.
    # left sleeve across the chest
    lsleeve = [(cx - int(22 * s), shoulder_y + int(8 * s)),
               (cx - int(6 * s), shoulder_y + int(20 * s)),
               (cx + int(8 * s), cy + int(2 * s)),
               (cx + int(2 * s), cy + int(8 * s)),
               (cx - int(16 * s), cy - int(2 * s)),
               (cx - int(24 * s), shoulder_y + int(20 * s))]
    triad_blob(surf, ONYX, lsleeve,
               core_pts=[(cx - int(6 * s), shoulder_y + int(20 * s)),
                         (cx + int(8 * s), cy + int(2 * s)),
                         (cx + int(2 * s), cy + int(8 * s)),
                         (cx - int(8 * s), cy)],
               ow=max(1, int(1.5 * s)))
    rim_edge(surf, [(cx - int(22 * s), shoulder_y + int(8 * s)),
                    (cx - int(6 * s), shoulder_y + int(20 * s)),
                    (cx + int(8 * s), cy + int(2 * s))], s, width=4.0, bright=True)
    # right sleeve dropping to the sceptre grip
    rsleeve = [(cx + int(22 * s), shoulder_y + int(8 * s)),
               (cx + int(28 * s), cy - int(6 * s)),
               (cx + int(26 * s), cy + int(14 * s)),
               (cx + int(16 * s), cy + int(14 * s)),
               (cx + int(16 * s), shoulder_y + int(16 * s))]
    triad_blob(surf, ONYX, rsleeve,
               core_pts=[(cx + int(26 * s), cy - int(6 * s)),
                         (cx + int(26 * s), cy + int(14 * s)),
                         (cx + int(18 * s), cy + int(14 * s)),
                         (cx + int(20 * s), cy)],
               ow=max(1, int(1.5 * s)))
    rim_edge(surf, [(cx + int(22 * s), shoulder_y + int(8 * s)),
                    (cx + int(28 * s), cy - int(6 * s)),
                    (cx + int(26 * s), cy + int(14 * s))], s, width=4.4, bright=True)

    # === SCEPTRE — slim gold rod with the tiny skull knob (toolkit tell) ======
    sc_x = cx + int(33 * s)
    sc_top = head_c[1] - int(2 * s)
    sc_bot = cy + int(40 * s)
    pygame.draw.line(surf, GOLD_D, (sc_x, sc_top), (sc_x, sc_bot), max(2, int(3.2 * s)))
    pygame.draw.line(surf, GOLD, (sc_x, sc_top + int(6 * s)), (sc_x, sc_bot), max(1, int(1.8 * s)))
    pygame.draw.line(surf, GOLD_BR, (sc_x - int(1 * s), sc_top + int(8 * s)),
                     (sc_x - int(1 * s), cy), max(1, int(0.8 * s)))
    # a small gold ferrule collar under the knob
    pygame.draw.rect(surf, GOLD, (sc_x - int(4 * s), sc_top + int(3 * s), int(8 * s), int(4 * s)))
    skull_knob(surf, sc_x, sc_top - int(5 * s), int(7 * s), s)

    # === HOOD + SKULL HEAD — hooded onyx skull, cool rim, pale-gold eyes ======
    # a smooth onyx hood framing the skull (keeps the head reading as cowled
    # royalty, and gives a big cool rim arc that anchors the night silhouette)
    hood = [(head_c[0] - int(hr * 1.5), head_c[1] + int(hr * 0.5)),
            (head_c[0] - int(hr * 1.2), head_c[1] - int(hr * 1.1)),
            (head_c[0], head_c[1] - int(hr * 1.5)),
            (head_c[0] + int(hr * 1.2), head_c[1] - int(hr * 1.1)),
            (head_c[0] + int(hr * 1.5), head_c[1] + int(hr * 0.5)),
            (head_c[0] + int(hr * 1.1), head_c[1] + int(hr * 1.2)),
            (head_c[0] - int(hr * 1.1), head_c[1] + int(hr * 1.2))]
    triad_blob(surf, ONYX, hood,
               core_pts=[(head_c[0], head_c[1] - int(hr * 1.2)),
                         (head_c[0] + int(hr * 1.3), head_c[1] - int(hr * 0.8)),
                         (head_c[0] + int(hr * 1.2), head_c[1] + int(hr * 0.9)),
                         (head_c[0], head_c[1] + int(hr * 1.0))],
               ow=max(1, int(1.6 * s)))
    rim_edge(surf, [(head_c[0] - int(hr * 1.48), head_c[1] + int(hr * 0.45)),
                    (head_c[0] - int(hr * 1.2), head_c[1] - int(hr * 1.1)),
                    (head_c[0], head_c[1] - int(hr * 1.5)),
                    (head_c[0] + int(hr * 1.2), head_c[1] - int(hr * 1.1)),
                    (head_c[0] + int(hr * 1.48), head_c[1] + int(hr * 0.45))],
             s, width=3.0, bright=True)

    # the skull itself — onyx, recessed in the hood shadow, lit only by rim+eyes
    triad_circle(surf, ONYX, head_c, hr, ow=max(2, int(2 * s)), core=False)
    # cool rim crescent on the skull's top-left so it lifts off the hood shadow
    skull_rim = [(head_c[0] + math.cos(math.radians(a)) * hr,
                  head_c[1] + math.sin(math.radians(a)) * hr) for a in range(160, 281, 10)]
    pygame.draw.lines(surf, RIM, False, skull_rim, max(1, int(1.8 * s)))
    pygame.draw.lines(surf, RIM_BR, False, skull_rim[:5], max(1, int(0.9 * s)))
    # eye sockets with cold pale-gold imperial pin-lights (small -> gold stays focal)
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] - int(hr * 0.04)
        pygame.draw.circle(surf, ONYX_DD, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.28))
        pygame.draw.circle(surf, EYE, (ex + sgn * int(1 * s), ey + int(1 * s)), int(hr * 0.14))
        pygame.draw.circle(surf, EYE_HOT, (ex, ey - int(1 * s)), max(1, int(hr * 0.07)))
    # nose triangle + a small calm grin (scary-CUTE, regal-serene not gory)
    pygame.draw.polygon(surf, ONYX_DD,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.4), my),
                     (head_c[0] + int(hr * 0.4), my), max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.18), my - int(hr * 0.06)),
                         (head_c[0] + int(k * hr * 0.18), my + int(hr * 0.10)), max(1, int(1 * s)))

    # === the closed IMPERIAL DOME crown (the top tell) =======================
    imperial_crown(surf, head_c[0], head_c[1] - int(hr * 0.96), int(hr * 0.92), s)


# -- the robe-column -> pillar mirror -----------------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The Sovereign's smooth columnar ROBE IS the pillar: a tall unbroken onyx
    column with the single vertical gold hem line = the tileable shaft; a closed
    gold imperial-dome cap (a miniature of the crown) over a smooth onyx collar at
    the gap = the creature-derived gap-edge cap. On-axis, symmetric, smooth (no
    ribs), the cool rim down both edges carries it on the night sky.

    `cap` names the END that faces the GAP."""
    shaft_w = int(15 * s)
    cap_room = int(30 * s)
    if cap == "bottom":
        shaft_top, shaft_bot = top, bot - cap_room
        cap_y = bot - int(16 * s)
        col_y = cap_y - int(14 * s)
    else:
        shaft_top, shaft_bot = top + cap_room, bot
        cap_y = top + int(16 * s)
        col_y = cap_y + int(14 * s)

    # smooth onyx column shaft (a hair waisted, like a draped mantle)
    column = [(cx - shaft_w, shaft_top), (cx + shaft_w, shaft_top),
              (cx + int(shaft_w * 0.86), (shaft_top + shaft_bot) // 2),
              (cx + shaft_w, shaft_bot), (cx - shaft_w, shaft_bot),
              (cx - int(shaft_w * 0.86), (shaft_top + shaft_bot) // 2)]
    triad_blob(surf, ONYX, column,
               core_pts=[(cx, shaft_top), (cx + shaft_w, shaft_top),
                         (cx + shaft_w, shaft_bot), (cx, shaft_bot)],
               ow=max(1, int(1.6 * s)))
    # WIDE cool rim as a CONTINUOUS wrap down both edges + across the shaft ends
    # (the night carrier) — uniform width so neither edge dissolves; brighter
    # crest on the lit left only.
    mid_y = (shaft_top + shaft_bot) // 2
    rim_edge(surf, [(cx - shaft_w, shaft_top),
                    (cx + shaft_w, shaft_top),
                    (cx + int(shaft_w * 0.86), mid_y),
                    (cx + shaft_w, shaft_bot),
                    (cx - shaft_w, shaft_bot),
                    (cx - int(shaft_w * 0.86), mid_y),
                    (cx - shaft_w, shaft_top)], s, width=4.2, bright=False)
    pygame.draw.lines(surf, RIM_BR, False,
                      [(cx - shaft_w, shaft_top),
                       (cx - int(shaft_w * 0.86), mid_y),
                       (cx - shaft_w, shaft_bot)], max(1, int(1.8 * s)))
    # the single vertical gold hem line down the centre (the shaft tell)
    pygame.draw.line(surf, GOLD_D, (cx, shaft_top), (cx, shaft_bot), max(2, int(3.0 * s)))
    pygame.draw.line(surf, GOLD, (cx, shaft_top), (cx, shaft_bot), max(1, int(1.6 * s)))
    pygame.draw.line(surf, GOLD_BR, (cx - int(1 * s), shaft_top), (cx - int(1 * s), shaft_bot),
                     max(1, int(0.7 * s)))

    # smooth onyx collar where the cap meets the shaft
    collar = [(cx - int(17 * s), col_y - int(8 * s)), (cx + int(17 * s), col_y - int(8 * s)),
              (cx + int(14 * s), col_y + int(8 * s)), (cx - int(14 * s), col_y + int(8 * s))]
    triad_blob(surf, ONYX, collar, ow=max(1, int(1.4 * s)))
    rim_edge(surf, [(cx - int(17 * s), col_y - int(8 * s)),
                    (cx + int(17 * s), col_y - int(8 * s))], s, width=2.6, bright=True)
    pygame.draw.line(surf, GOLD, (cx - int(15 * s), col_y - int(2 * s)),
                     (cx + int(15 * s), col_y - int(2 * s)), max(1, int(2 * s)))

    # the gap-edge IMPERIAL DOME cap (miniature crown — the creature tell)
    imperial_crown(surf, cx, cap_y, int(13 * s), s)


# -- compose the review sheet -------------------------------------------------
SS = 6


def load_font(size, bold=True):
    """Font path is FIVE levels up from this script (game/assets), SysFont fallback."""
    ttf = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "..", "..", "..", "..",
                                        "game", "assets", "LiberationSans-Bold.ttf"))
    if os.path.exists(ttf):
        return pygame.font.Font(ttf, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_obsidian(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK_RIM + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def silhouette_check(chip):
    """Measure how much of the chip's silhouette the rim+gold carries (not just
    the near-black mass that vanishes on night). Returns the fraction of opaque
    pixels whose colour is clearly LIGHTER than the night sky top — those are the
    pixels that actually read on the night chip.

    WHY no convert_alpha(): under SDL_VIDEODRIVER=dummy no display mode is set, so
    convert_alpha() raised 'No video mode has been set' and the self-check never
    ran. The chip is already an SRCALPHA surface, so we sample get_at() directly."""
    w, h = chip.get_size()
    opaque = 0
    carried = 0
    night_lum = sum(NIGHT_T) / 3.0
    for y in range(h):
        for x in range(w):
            r, g, b, a = chip.get_at((x, y))
            if a < 80:
                continue
            opaque += 1
            # a pixel "carries" if it is meaningfully brighter than night sky OR
            # is the warm gold accent (both stay visible on (22,26,54))
            lum = (r + g + b) / 3.0
            warm = r > g > b and r > 120
            if lum > night_lum + 26 or warm:
                carried += 1
    frac = carried / max(1, opaque)
    return opaque, carried, frac


def night_rowcarry_check(chip):
    """Stronger night gate: composite the chip onto the NIGHT sky gradient, then
    for every row that contains figure pixels confirm the rim/gold lifts at least
    one pixel clearly above the local night-sky value. Returns (figure_rows,
    carried_rows) so the print proves the tall column survives TOP-TO-BOTTOM, not
    just in aggregate."""
    w, h = chip.get_size()
    fig_rows = 0
    carried_rows = 0
    for y in range(h):
        sky = lerp(NIGHT_T, NIGHT_B, y / max(1, h - 1))
        sky_lum = sum(sky) / 3.0
        row_has_fig = False
        row_carries = False
        for x in range(w):
            r, g, b, a = chip.get_at((x, y))
            if a < 80:
                continue
            row_has_fig = True
            # alpha-composite onto the local night sky, then test contrast
            cr = (r * a + sky[0] * (255 - a)) // 255
            cg = (g * a + sky[1] * (255 - a)) // 255
            cb = (b * a + sky[2] * (255 - a)) // 255
            lum = (cr + cg + cb) / 3.0
            if lum > sky_lum + 22:
                row_carries = True
                break
        if row_has_fig:
            fig_rows += 1
            if row_carries:
                carried_rows += 1
    return fig_rows, carried_rows


def main():
    W, H = 1010, 820
    font_big = load_font(30)
    font = load_font(17)
    font_sm = load_font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("OBSIDIAN SOVEREIGN", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "dark imperial monarch (value pole)  ·  tall smooth onyx robe-column · gold imperial-dome crown · "
        "single gold hem line · cool rim-sheen carries night · round 2",
        True, LABEL_DIM), (24, 40))

    # === (a) BIG HERO ========================================================
    hero = render_creature_chip(330, 470, 165, 226, 1.95)
    sheet.blit(hero, (14, 70))
    sheet.blit(font.render("Creature — hero", True, LABEL), (100, 548))
    sheet.blit(font_sm.render("TALL slender monarch: one SMOOTH onyx robe-column to the floor (no ribs)", True, LABEL_DIM), (14, 574))
    sheet.blit(font_sm.render("= the only tall-narrow + only near-black king. Closed gold imperial-DOME", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("crown + single vertical gold hem line. Tiny-skull sceptre knob = toolkit tell.", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Wide cool blue-grey RIM-SHEEN wraps the silhouette so the black mass survives.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, smooth tileable robe-column ========
    pcx = 400
    top_big = pygame.Surface((130 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 65 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (130, 250)), INK_RIM + (255,), 1)
    sheet.blit(top_seg, (pcx, 70))
    bot_big = pygame.Surface((130 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 65 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (130, 250)), INK_RIM + (255,), 1)
    sheet.blit(bot_seg, (pcx, 70 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 70 + 250, 114, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 46, 70 + 250 + 40))
    sheet.blit(font.render("Pillar — robe-column", True, LABEL), (pcx - 4, 674))
    sheet.blit(font_sm.render("smooth onyx column + gold hem line = shaft;", True, LABEL_DIM), (pcx - 4, 698))
    sheet.blit(font_sm.render("imperial-dome cap over a collar caps each gap", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, rim-lit edges)", True, LABEL_DIM), (pcx - 4, 730))

    # === (c) TRUE 32px gameplay chips on day + night sky =====================
    panel_x = 590
    pygame.draw.rect(sheet, PANEL, (panel_x, 70, W - panel_x - 14, 576))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 80))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_obsidian(big, 48 * SS, 52 * SS, (32 / 134.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK_RIM + (255,), 1)

    chip = chip32()

    day_y = 112
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on DAY sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on NIGHT sky (make-or-break)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # 32px pillar gap-cap chip on both skies
    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK_RIM + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # === (d) BLACKOUT silhouette proof =======================================
    # the alpha mask filled flat — proves the SHAPE reads as a tall-narrow robed
    # monarch (crown + column + hem flare) before any colour.
    blk_big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
    draw_obsidian(blk_big, 48 * SS, 52 * SS, (32 / 134.0) * SS)
    blk = pygame.transform.smoothscale(blk_big, (96, 96))
    mask = pygame.mask.from_surface(blk)
    sil = mask.to_surface(setcolor=(18, 18, 22, 255), unsetcolor=(0, 0, 0, 0))
    # WHY no stray tile over px2: the night gap-cap chip already lives there;
    # the blackout proof is placed below the palette only.

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 470))
    swatches = [
        (ONYX, "onyx near-black bone"), (ONYX_D, "onyx shade"),
        (RIM, "cool rim-sheen"), (RIM_BR, "rim crest"),
        (GOLD, "gold (structure)"), (GOLD_HOT, "gold finial (brightest)"),
        (EYE, "pale-gold eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 498
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # blackout proof tile under the palette
    sheet.blit(font_sm.render("Blackout silhouette", True, LABEL), (panel_x + 16, 608))
    pygame.draw.rect(sheet, (214, 216, 222), (panel_x + 16, 626, 96, 96))
    pygame.draw.rect(sheet, INK, (panel_x + 16, 626, 96, 96), 1)
    sheet.blit(sil, (panel_x + 16, 626))
    sheet.blit(font_sm.render("tall robed-king shape", True, LABEL_DIM), (panel_x + 120, 660))
    sheet.blit(font_sm.render("(crown + column + hem)", True, LABEL_DIM), (panel_x + 120, 676))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 760, W - 28, 48))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (20,18,24) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 770))
    sheet.blit(font_sm.render(
        "VALUE-POLE LOCK: smooth onyx robe (no ribs) · gold = only bright accent · WIDE cool rim-sheen carries the night silhouette.",
        True, LABEL_DIM), (26, 788))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    # -- self-check: does the rim-sheen carry the silhouette on the night chip? --
    opaque, carried, frac = silhouette_check(chip)
    print("NIGHT-CHIP mass self-check: opaque=%d carried(rim/gold)=%d fraction=%.2f"
          % (opaque, carried, frac))
    mass_ok = frac >= 0.30

    # the real GATE: every figure row must keep at least one edge legible on night
    # so the TALL column survives top-to-bottom, not just on average.
    fig_rows, carried_rows = night_rowcarry_check(chip)
    row_frac = carried_rows / max(1, fig_rows)
    print("NIGHT-CHIP row-carry self-check: figure_rows=%d carried_rows=%d row_fraction=%.2f"
          % (fig_rows, carried_rows, row_frac))
    rows_ok = row_frac >= 0.92    # near-every row must carry (top-to-bottom legible)

    verdict = "PASS" if (mass_ok and rows_ok) else "WEAK — widen/brighten the rim"
    print("RIM CARRIES NIGHT SILHOUETTE: %s "
          "(gate: mass-fraction>=0.30 AND row-fraction>=0.92)" % verdict)


if __name__ == "__main__":
    main()
