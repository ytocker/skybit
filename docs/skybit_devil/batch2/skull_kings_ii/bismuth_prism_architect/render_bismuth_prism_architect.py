"""
Round-1 concept renderer for the BISMUTH PRISM ARCHITECT — a royal skull-KING
of the Skull-Kings-II brood, rendered as a STEPPED CRYSTAL ZIGGURAT rather than
a figure. Headless Pygame; ELEVATED pipeline (SS=6 supersample -> smoothscale)
so the thin rainbow facet-edges survive the downscale. Keeps the shipped house
grammar: flat saturated triad fills, a hard 1-2px ink keyline (28,22,30),
dark-core -> flat-fill -> top-left sheen, 1px alpha-grown outline, chibi
scary-CUTE proportions; procedural-only (no gradients/PNGs).

WHY this king is LIMBLESS architecture, not a body: the brood's de-collision
rule is that the sibling Oxblood Automaton already owns the humanoid-machine
read. The Architect must NOT resolve into arms/legs/torso, so it has NO cradle
and NO limbs — it is a right-angle terraced mass (a Mesoamerican-pyramid-of-
crystal) that steps OUT toward the base. The kingship is carried entirely by a
FACETED BISMUTH SKULL CAPSTONE sitting as the topmost step, plus the rainbow
edges. Read order: pyramid mass first, skull-crown capstone second.

WHY the rainbow lives in the EDGES, not a glow-core: bismuth's identity is its
iridescent oxide step-edges. The dominant MASS is a single cool steel-grey
crystal; the rainbow is a set of DISCRETE per-edge colored line STROKES walked
along each facet boundary (magenta/teal/gold cycling), never a gradient fill.
The focal = the single brightest facet-edge pip, not a warm interior. This keeps
one dominant mass + thin accents and dodges the "glowing gem" cliche.

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
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE ------------------------------------------------------------
# Steel-grey bismuth crystal is the dominant MASS; rainbow lives only in edges.
CRY       = (132, 138, 150)   # steel-grey crystal body (dominant fill)
CRY_D     = ( 88,  94, 108)   # crystal dark-core / recessed terrace face
CRY_DD    = ( 58,  62,  76)   # deepest crystal hollow (under-step shadow)
CRY_SH    = (196, 202, 214)   # crystal top-left rim-sheen (lit terrace top)
CRY_LIT   = (170, 176, 188)   # mid-lit facet face
# rainbow FACET-EDGE accents — drawn as discrete per-edge colored line strokes,
# cycling around the spectrum so adjacent edges never repeat a hue.
EDGE_MAG  = (206,  96, 168)   # iridescent magenta oxide edge
EDGE_TEA  = ( 96, 196, 196)   # iridescent teal oxide edge
EDGE_GLD  = (214, 184,  96)   # iridescent gold oxide edge
EDGE_MAG_H = (244, 168, 222)  # magenta edge highlight pip
EDGE_TEA_H = (176, 244, 244)  # teal edge highlight pip
EDGE_GLD_H = (250, 232, 168)  # gold edge highlight pip (brightest -> the focal)
INK       = ( 28,  22,  30)   # hard ink keyline

BG        = ( 96, 100, 108)
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)

EDGE_CYCLE   = (EDGE_MAG, EDGE_TEA, EDGE_GLD)
EDGE_CYCLE_H = (EDGE_MAG_H, EDGE_TEA_H, EDGE_GLD_H)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


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
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


# -- the rainbow facet-edge stroke (the king's identity + focal) ---------------
def facet_edge(surf, p0, p1, hue_i, s, hot=False):
    """Walk ONE facet boundary as a discrete colored line stroke. WHY a stroke,
    not a gradient fill: bismuth's iridescence is literally the oxide film at the
    terrace EDGES; coloring the boundaries (and leaving the faces flat grey)
    reads unmistakably as bismuth while keeping the rainbow a thin accent that
    can't swell into a second warm mass. hue_i cycles magenta/teal/gold so no two
    touching edges share a hue. `hot` lays the bright highlight pip — used only
    on the capstone so the single brightest pixel lives in the skull-crown."""
    col = EDGE_CYCLE[hue_i % 3]
    pygame.draw.line(surf, INK, p0, p1, max(2, int(2.4 * s)))
    pygame.draw.line(surf, col, p0, p1, max(1, int(1.6 * s)))
    if hot:
        hc = EDGE_CYCLE_H[hue_i % 3]
        # a short bright pip on the lit (upper) third of the edge
        mx = (p0[0] + p1[0]) / 2
        my = (p0[1] + p1[1]) / 2
        pygame.draw.line(surf, hc, p0, (mx, my), max(1, int(1.1 * s)))


def crystal_block(surf, cx, top_y, half_w, h, s, hue_base, sheen=True):
    """One right-angle terrace block: a flat grey rectangular crystal face with
    a thin top-cap (the lit step surface). Returns the block's top-left/right
    corners so the caller can chain the rainbow continuously up the ziggurat.
    WHY rectangular + right-angle: the silhouette must read as STEPPED
    ARCHITECTURE (a built pyramid), never an organic crystal cluster or a figure.

    WHY only ONE rainbow stroke (the terrace front-lip): round-1 walked every
    boundary, which slid into chroma-confetti at 32px. Restricting iridescence to
    the single lit front-lip per terrace keeps the edges reading as discrete
    facets and lets the grey mass stay dominant."""
    x0, x1 = cx - half_w, cx + half_w
    y0, y1 = top_y, top_y + h
    # cap thickness gives each step a lit top surface (the terrace tread)
    cap_h = max(2, int(h * 0.26))

    # front face (flat grey mass, dark-core lower-right for volume)
    face = [(x0, y0 + cap_h), (x1, y0 + cap_h), (x1, y1), (x0, y1)]
    triad_blob(surf, CRY, face,
               core_pts=[(cx, y0 + cap_h), (x1, y0 + cap_h), (x1, y1), (cx, y1)],
               sheen_pts=([(x0, y0 + cap_h), (x0 + half_w * 0.5, y0 + cap_h),
                           (x0 + half_w * 0.5, y1), (x0, y1)] if sheen else None),
               ow=max(1, int(1.4 * s)))
    # lit top tread (a brighter slab) — sells the right-angle step
    tread = [(x0, y0), (x1, y0), (x1 - max(2, int(3 * s)), y0 + cap_h),
             (x0 + max(2, int(3 * s)), y0 + cap_h)]
    triad_blob(surf, CRY_SH, tread, ow=max(1, int(1.2 * s)))
    # internal facet split — a single diagonal crease so the face reads faceted
    crease0 = (x0 + half_w * 0.62, y0 + cap_h)
    crease1 = (x0 + half_w * 0.30, y1)
    pygame.draw.line(surf, CRY_DD, crease0, crease1, max(1, int(1.2 * s)))

    # RAINBOW FACET EDGE: the single lit front-lip of the terrace, nothing else.
    facet_edge(surf, (x0, y0), (x1, y0), hue_base, s)               # tread front-lip
    return (x0, y0), (x1, y0)


# -- the FACETED BISMUTH SKULL CAPSTONE (the above-head crown) -----------------
def _erase_void(surf, pts):
    """Punch a hole through surf's ALPHA along a polygon — the cut survives the
    smoothscale into the silhouette mask. WHY alpha-punch rather than a dark
    fill: the blackout proof is built from the alpha mask, so a merely-dark
    socket still reads as solid mass. Carving the alpha is the ONLY way the
    silhouette breaks into a skull at 32px."""
    pygame.draw.polygon(surf, (0, 0, 0, 0), [(int(p[0]), int(p[1])) for p in pts])


def skull_capstone(surf, cx, base_y, w, s):
    """A faceted bismuth SKULL crowning the ziggurat — the royal tell. WHY a TALL
    NARROW cranial dome on a pinched neck-step: round-1's wide low dome collapsed
    into "the top step of a pyramid." A taller-than-wide cranium that sits on a
    visibly narrower neck separates the crown from the terraced body, and TWO
    eye-socket voids + a jaw notch are carved straight through the alpha so the
    silhouette breaks as a skull at 32px. The brightest gold pip is a brow-glint
    so the focal lives in the crown."""
    half = w * 0.5
    # cranial dome is TALLER than wide (a cranium, not a step); pinch the base in.
    top_y = base_y - int(w * 1.18)
    jaw_y = base_y                      # bottom of the (narrower) jaw
    brow_y = base_y - int(w * 0.62)     # where the skull widens at the brow
    chin_half = half * 0.50             # pinched jaw -> distinct from the dome

    # cranium silhouette: dome up top, brow shoulders, pinched-in jaw at the base
    cran = [(cx - chin_half, jaw_y),
            (cx - half * 0.92, brow_y + int(w * 0.06)),
            (cx - half * 0.96, brow_y - int(w * 0.10)),
            (cx - half * 0.58, top_y + int(w * 0.12)),
            (cx - half * 0.18, top_y),
            (cx + half * 0.18, top_y),
            (cx + half * 0.58, top_y + int(w * 0.12)),
            (cx + half * 0.96, brow_y - int(w * 0.10)),
            (cx + half * 0.92, brow_y + int(w * 0.06)),
            (cx + chin_half, jaw_y)]
    triad_blob(surf, CRY_LIT, cran,
               core_pts=[(cx, top_y), (cx + half * 0.58, top_y + int(w * 0.12)),
                         (cx + half * 0.96, brow_y - int(w * 0.10)),
                         (cx + half * 0.92, brow_y + int(w * 0.06)),
                         (cx + chin_half, jaw_y), (cx, jaw_y)],
               sheen_pts=[(cx - half * 0.18, top_y), (cx, top_y),
                          (cx - half * 0.10, brow_y),
                          (cx - half * 0.50, brow_y - int(w * 0.04))],
               ow=max(1, int(1.6 * s)))

    # neck-step pinch: a short dark waist between jaw and the capstone step below,
    # so the crown reads as a separate mass perched on the terrace.
    nw = chin_half * 0.92
    neck = [(cx - nw, jaw_y), (cx + nw, jaw_y),
            (cx + nw * 0.84, jaw_y + int(w * 0.16)),
            (cx - nw * 0.84, jaw_y + int(w * 0.16))]
    pygame.draw.polygon(surf, CRY_D, [(int(p[0]), int(p[1])) for p in neck])
    pygame.draw.polygon(surf, INK, [(int(p[0]), int(p[1])) for p in neck],
                        max(1, int(1.4 * s)))

    # eye-socket VOIDS — carved through the alpha so the silhouette breaks. WHY
    # enlarged to ~0.52*half and set wide: at the now-bigger capstone these holes
    # downscale to a clear 1-2px void each, the single break that stops the dome
    # reading as a solid bright nub. A fat grey nasal bridge is left between them.
    eye_r = half * 0.52
    ey = brow_y + int(w * 0.06)
    for sgn in (-1, 1):
        ex = cx + sgn * half * 0.48
        socket = [(ex - eye_r, ey - eye_r * 0.55),
                  (ex + eye_r * 0.10, ey - eye_r * 0.90),
                  (ex + eye_r, ey - eye_r * 0.18),
                  (ex + eye_r * 0.70, ey + eye_r * 0.85),
                  (ex - eye_r * 0.60, ey + eye_r * 0.78)]
        _erase_void(surf, socket)
        # thin ink rim so the void edge stays crisp on the day chip
        pygame.draw.polygon(surf, INK, [(int(p[0]), int(p[1])) for p in socket],
                            max(1, int(1.4 * s)))
        # a tiny iridescent pin deep in the socket (cool spark, not a warm core)
        pygame.draw.circle(surf, EDGE_TEA, (int(ex), int(ey)),
                           max(1, int(eye_r * 0.22)))

    # JAW NOTCH — a wide DEEP void biting up into the base so the bottom contour
    # of the dome breaks into two cheek tabs (the third skull break alongside the
    # sockets). WHY deeper (0.42*w) + wider: a shallow notch vanished at 32px; the
    # cut must clearly nick the silhouette's lower edge to register as a jaw.
    jn_w = chin_half * 0.72
    jaw_notch = [(cx - jn_w, jaw_y + int(w * 0.05)),
                 (cx + jn_w, jaw_y + int(w * 0.05)),
                 (cx + jn_w * 0.45, jaw_y - int(w * 0.42)),
                 (cx - jn_w * 0.45, jaw_y - int(w * 0.42))]
    _erase_void(surf, jaw_notch)

    # nasal — a small down-pointing ink triangle between the sockets
    pygame.draw.polygon(surf, INK,
                        [(cx - int(half * 0.12), brow_y + int(w * 0.16)),
                         (cx + int(half * 0.12), brow_y + int(w * 0.16)),
                         (cx, brow_y + int(w * 0.34))])
    # cheek-tab teeth flanking the jaw notch — short ink slots on the tabs
    ty = jaw_y - int(w * 0.06)
    for sgn in (-1, 1):
        tx = cx + sgn * int(chin_half * 0.80)
        pygame.draw.line(surf, INK, (tx, ty - int(w * 0.10)), (tx, ty),
                         max(1, int(1.1 * s)))

    # RAINBOW EDGE on the crown: ONE bright gold stroke across the brow ridge,
    # carrying the single HOT pip -> the named focal sits on the skull.
    bl = (cx - half * 0.58, brow_y - int(w * 0.04))
    br = (cx + half * 0.58, brow_y - int(w * 0.04))
    facet_edge(surf, bl, br, 2, s, hot=True)
    px = int((bl[0] + br[0]) / 2)
    py = int((bl[1] + br[1]) / 2)
    pygame.draw.circle(surf, EDGE_GLD_H, (px, py), max(1, int(1.6 * s)))


# -- the limbless stepped-crystal ziggurat KING --------------------------------
def draw_king(surf, cx, cy, s):
    """Compose the ziggurat from wide base step up to the narrow capstone step,
    then crown it with the bismuth skull. WHY drawn bottom-up: each higher step
    must overlap the one below at its back edge so the terraces read as receding
    treads (a built pyramid), and the rainbow edges chain continuously upward.

    WHY the body is now SQUATTER (3 steps, shorter pitch) and the skull bigger:
    at true 32px the round-2 4-step tower ate the height budget and the crown
    collapsed to a nub. The royal read lives ENTIRELY in the skull, so the body
    is compressed to a low broad plinth and the skull is enlarged to ~28% of the
    total tower height — enough that the two socket voids + jaw notch land as
    1-2px holes that survive the downscale."""
    n_steps = 3
    base_half = int(50 * s)
    step_h = int(15 * s)
    base_bottom = cy + int(46 * s)
    inset = int(12 * s)   # each step pulls IN by this much (steps OUT to base)

    # the steps, widest (bottom) -> narrowest (top)
    for k in range(n_steps):
        half_w = base_half - k * inset
        # higher steps sit further back/up; bottom of this step = top of prev
        block_bottom = base_bottom - k * step_h
        top_y = block_bottom - step_h - (0 if k == 0 else int(2 * s))
        crystal_block(surf, cx, top_y, half_w, step_h + int(4 * s), s,
                      hue_base=k, sheen=True)

    # the capstone step (a small grey block) the skull's neck pinches onto —
    # kept SHORT so the skull's neck-pinch is the dominant transition, not a tread.
    cap_step_half = int(15 * s)
    cap_step_top = base_bottom - n_steps * step_h - int(9 * s)
    crystal_block(surf, cx, cap_step_top, cap_step_half, int(8 * s), s,
                  hue_base=n_steps, sheen=True)

    # the FACETED BISMUTH SKULL CAPSTONE — the above-head crown tell, ENLARGED so
    # it wins the size war at 32px. Width ~40 (vs body base ~100) and its dome
    # rises ~47px, making the crown ~28% of the ~165px total tower height. Sized
    # narrower than the cap step so the cranial dome reads as a perched crown, and
    # raised so its neck-pinch lands ON the step top (crown separates from body).
    skull_capstone(surf, cx, cap_step_top + int(1 * s), int(40 * s), s)


# -- the pillar: a single mirrored ziggurat-terrace tower ----------------------
def pillar_step(surf, cx, top_y, half_w, h, s, hue_base, flip=False, accent=True):
    """One terrace block for the pillar, drawn so it can mirror top<->bottom.
    `flip` inverts the lit tread to the underside for the ceiling-rooted half.
    `accent` gates the rainbow stroke: round-1 walked all three edges of every
    terrace, which read as a magenta/teal barber-pole. We now color ONLY the
    front-lip and only on alternating terraces, letting grey dominate the shaft."""
    x0, x1 = cx - half_w, cx + half_w
    cap_h = max(2, int(h * 0.30))
    if not flip:
        y0, y1 = top_y, top_y + h
        face = [(x0, y0 + cap_h), (x1, y0 + cap_h), (x1, y1), (x0, y1)]
        tread = [(x0, y0), (x1, y0), (x1 - max(2, int(3 * s)), y0 + cap_h),
                 (x0 + max(2, int(3 * s)), y0 + cap_h)]
        e_a, e_b = (x0, y0), (x1, y0)
    else:
        y0, y1 = top_y, top_y + h
        face = [(x0, y0), (x1, y0), (x1, y1 - cap_h), (x0, y1 - cap_h)]
        tread = [(x0 + max(2, int(3 * s)), y1 - cap_h),
                 (x1 - max(2, int(3 * s)), y1 - cap_h), (x1, y1), (x0, y1)]
        e_a, e_b = (x0, y1), (x1, y1)
    triad_blob(surf, CRY, face,
               core_pts=[(cx, face[0][1]), (x1, face[1][1]),
                         (x1, face[2][1]), (cx, face[3][1])],
               sheen_pts=[(x0, face[0][1]), (x0 + half_w * 0.5, face[0][1]),
                          (x0 + half_w * 0.5, face[3][1]), (x0, face[3][1])],
               ow=max(1, int(1.4 * s)))
    triad_blob(surf, CRY_SH, tread, ow=max(1, int(1.2 * s)))
    if accent:
        facet_edge(surf, e_a, e_b, hue_base, s)


def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """A vertical bismuth-terrace tower: a stack of stepped crystal blocks that
    flare OUT toward the gap-edge cap (the creature-derived tell), mirrored so
    the top half hangs from the ceiling and the bottom half rises from the floor.
    A small skull capstone marks the gap edge."""
    shaft_w = int(13 * s)
    # central ink shaft for body so the tower never breaks apart at the gap
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    pitch = int(22 * s)
    cap_room = int(46 * s)
    flip = (cap == "top")
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
        order = range(b0, b1, pitch)
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
        order = range(b1 - pitch, b0, -pitch)

    # one rainbow accent per ~2 shaft terraces (alternating) so grey dominates;
    # hue advances only on accented terraces, killing the barber-pole.
    hue = 0
    for i, y in enumerate(order):
        acc = (i % 2 == 0)
        pillar_step(surf, cx, y, shaft_w, pitch - int(3 * s), s, hue, flip=flip,
                    accent=acc)
        if acc:
            hue += 1

    # the flared gap-edge cap: 3 widening terraces ending in a skull capstone.
    # only the OUTERMOST cap lip carries a rainbow accent (the cap is the focal
    # flare, not a stripe stack).
    cap_y = (bot - int(40 * s)) if cap == "bottom" else (top + int(40 * s))
    fan_dir = -1 if cap == "bottom" else 1
    for j in range(3):
        half_w = int((11 + j * 6) * s)
        step_h = int(11 * s)
        acc = (j == 2)
        if fan_dir < 0:
            ty = cap_y + j * step_h
            pillar_step(surf, cx, ty, half_w, step_h + int(3 * s), s, 2,
                        flip=False, accent=acc)
        else:
            ty = cap_y - (j + 1) * step_h
            pillar_step(surf, cx, ty, half_w, step_h + int(3 * s), s, 2,
                        flip=True, accent=acc)

    # skull capstone marks the gap edge (mirrored to face into the gap). WHY
    # enlarged to 28: same size-war fix as the king — a 22px capstone collapsed
    # to a nub at the pillar chip scale, so the gap-edge skull cue was lost.
    if fan_dir < 0:
        sk_base = cap_y + 3 * int(11 * s) + int(2 * s)
        skull_capstone(surf, cx, sk_base, int(28 * s), s)
    else:
        # for the top half, build the skull pointing DOWN via a flipped sub-surf
        sub = pygame.Surface((int(76 * s), int(52 * s)), pygame.SRCALPHA)
        skull_capstone(sub, int(38 * s), int(48 * s), int(28 * s), s)
        sub = pygame.transform.flip(sub, False, True)
        sk_base = cap_y - 3 * int(11 * s) - int(2 * s)
        surf.blit(sub, (cx - int(38 * s), int(sk_base)))


# -- compose the review sheet --------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_king(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_fonts():
    """FONT is five levels up from this script; SysFont fallback if missing."""
    base = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(base, "..", "..", "..", "..", "..",
                      "game", "assets", "LiberationSans-Bold.ttf")
    try:
        return (pygame.font.Font(fp, 30), pygame.font.Font(fp, 17),
                pygame.font.Font(fp, 12))
    except Exception:
        return (pygame.font.SysFont("DejaVu Sans", 30, bold=True),
                pygame.font.SysFont("DejaVu Sans", 17, bold=True),
                pygame.font.SysFont("DejaVu Sans", 12))


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("BISMUTH PRISM ARCHITECT", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "Skull-Kings-II  ·  LIMBLESS stepped-crystal ziggurat (no figure, no cradle) · TALL cranial SKULL capstone on a neck-pinch (carved socket+jaw voids) · "
        "steel-grey mass + ONE rainbow front-lip per terrace · round 3 (skull wins the 32px size war)",
        True, LABEL_DIM), (440, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 224, 1.55)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("King — hero", True, LABEL), (120, 566))
    sheet.blit(font_sm.render("LIMBLESS terraced crystal mass that steps OUT to the base; one steel-grey", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("dominant mass, rainbow = ONE front-lip stroke per terrace (no confetti);", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("TALL cranial SKULL capstone (carved socket+jaw voids); brow gold-pip = focal.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored ======================================
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
    sheet.blit(font.render("Pillar — bismuth terrace tower", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked stepped-crystal terraces; flared gap-edge cap", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("with skull capstone + rainbow edges", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_king(big, 48 * SS, 50 * SS, (32 / 116.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        # WHY a teal rim on the night chip: the cool steel mass dissolves into a
        # dark night sky; a thin iridescent teal halo carries the silhouette
        # while keeping the gold capstone pip the unambiguous brightest point.
        if night:
            base = grow_outline(small, lerp(EDGE_TEA, INK, 0.3) + (255,), 2)
            return grow_outline(base, INK + (200,), 1)
        return grow_outline(small, INK + (255,), 1)

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(day_chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(night_chip, (panel_x + 20 + 27 - 1, night_y + 27 - 1))
    sheet.blit(font_sm.render("32px on night sky (teal rim)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof — blacked-out at the EXACT true-32px gameplay scale, then
    # nearest-neighbor magnified for inspection. WHY identical to chip32(): a proof
    # rendered larger is not a valid gate — the round-2 proof passed only because
    # it was drawn bigger than the in-game chip. The skull must break the
    # silhouette (2 socket voids + jaw notch) at the size the player actually sees.
    def silhouette():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_king(big, 48 * SS, 50 * SS, (32 / 116.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))   # the true 32px chip
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((96, 96), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        # nearest-neighbor 2x so the genuine 32px-scale voids are visible, not
        # re-smoothed (no detail is added — this is the same pixels, magnified).
        return pygame.transform.scale(sil, (192, 192))

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 192, 192))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 192, 192), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("blackout proof @ TRUE 32px", True, LABEL_DIM), (sil_x, day_y + 196))
    sheet.blit(font_sm.render("(2x nearest-neighbor; same pixels)", True, LABEL_DIM), (sil_x, day_y + 212))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.30 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 200   # right gutter, clear of the now-wider 192px blackout proof
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (CRY, "steel-grey crystal"), (CRY_D, "crystal dark-core"),
        (CRY_SH, "crystal sheen"), (CRY_DD, "deep hollow"),
        (EDGE_MAG, "edge magenta"), (EDGE_TEA, "edge teal"),
        (EDGE_GLD, "edge gold"), (EDGE_GLD_H, "edge focal pip"),
        (EDGE_TEA_H, "teal highlight"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 188
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "LIMBLESS stepped-crystal ZIGGURAT: a built pyramid of bismuth, NOT a figure (de-collides from the humanoid Oxblood Automaton).  "
        "ONE grey mass + DISCRETE per-edge rainbow STROKES (never a gradient fill); faceted SKULL CAPSTONE = crown; brightest gold-edge pip = focal.  "
        "SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    self_check()


def self_check():
    """Render the hero alone and verify (1) the brightest pixel sits inside the
    skull-capstone crown (the focal owns the peak), and (2) the rainbow reads as
    thin edges — strongly-saturated edge pixels stay a small fraction of grey
    crystal mass (one dominant mass + thin accents)."""
    surf = pygame.Surface((400, 520), pygame.SRCALPHA)
    draw_king(surf, 200, 250, 1.7)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    edge_n, mass_n = 0, 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
            mx, mn = max(r, g, b), min(r, g, b)
            sat = (mx - mn)
            if sat > 55:        # saturated -> a rainbow edge pixel
                edge_n += 1
            elif mx > 70 and sat <= 40:   # near-neutral grey -> crystal mass
                mass_n += 1
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    # crown band: the capstone sits in the upper ~35% of the rendered mass
    in_crown = by < int(h * 0.42)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> in crown band?", in_crown)
    print("self-check: edge px ~%d  vs grey-mass px ~%d  -> edge fraction %.2f"
          % (edge_n, mass_n, edge_n / max(1, edge_n + mass_n)))


if __name__ == "__main__":
    main()
