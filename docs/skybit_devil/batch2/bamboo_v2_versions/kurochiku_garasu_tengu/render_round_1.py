"""
Round-1 concept renderer for KUROCHIKU-GARASU-TENGU — the black-bamboo
crow-tengu of the mountain grove (bamboo v2 REALISTIC set, concept #5). Headless
Pygame; ELEVATED pipeline (supersample SS=6 -> smoothscale) so the split-culm
quill geometry and node-rings stay crisp at downscale.

WHY this departs from the chibi house grammar: bamboo v2 is a DELIBERATE
departure toward REALISM and botanical accuracy — true tall-thin proportions,
NO chibi big-head. Shading is hard-edged FLAT but pushed to 4-6 HARD STEPPED
value bands per form for a sculpted near-volumetric read; NEVER smooth gradients
(they boil at true-32px). Radial glow is for accents ONLY. Hard ink keyline
(28,22,30) + a 1px alpha-mask outline for silhouette POP.

WHY this is the WINGED BEAKED TENGU — the ONLY winged form in the set: a hunched
crow-headed mountain-guardian yokai feathered in glossy black kurochiku, sharp
beak, a tall single feather-tuft, two angular SPLIT-CULM quill-wings spread,
gripping a black-bamboo staff. Black-on-black NIGHT legibility is the real risk,
so the steely blue-grey quill-sheen (132,140,162) is carried as a FIRM value
band — wing edges hold against a night biome — and the vermilion beak-wattle
(206,68,52) + thin gold staff-band (214,176,90) carry the warm focal. FEWER,
BIGGER quills (~4 per wing) so the split-culm node-rings survive at 32px.

WHY the black-bamboo STAFF is the pillar: a black node-segment shaft is the
tileable repeat band; a feather-tuft crook (hung with a small shide) caps the
gap edge; the gold ferrule + a curled fresh shoot mirror it at the lower edge.
Slim, on-axis, bottom-rooted.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it imports nothing from game.* — only colour math + the triad/outline
helpers cloned from the lineage template, plus the necrarch radial_glow.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (locked brief #5) ─────────────────────────────────────────
# Blackened kurochiku re-keyed COOLER/steelier than the old Nushi. The black is
# the dominant feathered mass; the steely blue-grey quill-sheen is the legibility
# anchor (a FIRM band, not a whisper) so the wing edges read on a night sky. The
# two WARM accents (vermilion beak-wattle + thin gold staff-band) carry the focal.
BLACK      = ( 46,  40,  50)   # black-culm base (the dominant feathered mass)
INKVIO     = ( 28,  24,  36)   # ink-violet shade / deepest feather hollow
SHEEN      = (132, 140, 162)   # steely blue-grey quill-sheen (FIRM value band)
SHEEN_HI   = (176, 184, 204)   # hottest quill-sheen edge (rim only)
BLOOM      = ( 84,  78,  98)   # faint violet waxy-bloom mid-band on the culm
VERM       = (206,  68,  52)   # vermilion tengu beak-wattle (THE warm focal)
VERM_HI    = (236, 132,  96)   # hot vermilion highlight
VERM_D     = (150,  44,  36)   # vermilion shade
GOLD       = (214, 176,  90)   # thin gold staff-band / ferrule
GOLD_HI    = (244, 216, 150)   # hot gold edge
GOLD_D     = (150, 116,  52)   # gold shade
SHOOT      = (134, 176,  96)   # fresh green node-shoot collar (tiny, the only green)
SHOOT_D    = ( 84, 124,  66)   # shoot shade
SHIDE      = (224, 224, 232)   # paper shide (white zigzag streamer) on the staff
INK        = ( 28,  22,  30)   # hard ink keyline

BG         = ( 60,  58,  72)   # neutral cool-grey review backdrop
PANEL      = ( 46,  44,  58)
DAY_SKY_T  = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B  = (196, 232, 244)
NIGHT_T    = ( 18,  20,  44)   # night biome sky (top) — the real legibility test
NIGHT_B    = ( 40,  38,  72)
LABEL      = (238, 240, 244)
LABEL_DIM  = (186, 192, 206)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── outline grown from the alpha mask (the house keyline / silhouette POP) ────
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


# ── radial accent glow (necrarch precedent) — accents ONLY, never a fill ──────
def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


def hard_blob(surf, base, pts, shade=None, shade_pts=None,
              band=None, band_pts=None, hi=None, hi_pts=None, ow=2):
    """HARD STEPPED flat shading: ink keyline -> flat base fill -> a discrete
    SHADE band -> an optional mid-tone band -> a discrete rim HIGHLIGHT band.
    Each band is its OWN closed polygon (a hard step), NEVER an interpolated
    gradient — this is the bamboo-v2 sculpted-but-flat read that protects
    true-32px legibility."""
    if ow:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, base, pts)
    if shade and shade_pts:
        pygame.draw.polygon(surf, shade, shade_pts)
    if band and band_pts:
        pygame.draw.polygon(surf, band, band_pts)
    if hi and hi_pts:
        pygame.draw.polygon(surf, hi, hi_pts)
    if ow:
        pygame.draw.polygon(surf, INK, pts, ow)


# ── a single SPLIT-CULM QUILL — a fat blackened bamboo-slat feather ───────────
def split_culm_quill(surf, root, ang, length, width, s, nodes=2):
    """ONE quill = a split blackened culm-slat: a fat near-parallel-sided plank
    swept along `ang` to a chisel tip, banded with `nodes` NODE-RINGS (the
    bamboo tell). WHY fat + few: at 32px thin needle-quills collapse to fuzz, so
    the brief calls for FEWER, BIGGER quills (~4/wing) whose split-culm node-
    rings actually survive. Each quill is hard-stepped as its OWN form: black
    base, an ink-violet trailing shade, a FIRM steely-sheen leading rail (the
    night-legibility band), then the white sheath-scar node-rings — so sky reads
    cleanly BETWEEN quills and the winged silhouette stays a winged silhouette."""
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca                       # perpendicular = quill width axis
    hw = width * 0.5
    tip = (root[0] + ca * length, root[1] + sa * length)
    tw = hw * 0.32                         # blunt chisel tip half-width
    belly = 0.74 * length
    bx = (root[0] + ca * belly, root[1] + sa * belly)
    quill = [
        (root[0] + px * hw * 0.84, root[1] + py * hw * 0.84),
        (bx[0]   + px * hw,        bx[1]   + py * hw),
        (tip[0]  + px * tw,        tip[1]  + py * tw),
        (tip[0]  - px * tw,        tip[1]  - py * tw),
        (bx[0]   - px * hw,        bx[1]   - py * hw),
        (root[0] - px * hw * 0.84, root[1] - py * hw * 0.84),
    ]
    pygame.draw.polygon(surf, INK, quill)
    pygame.draw.polygon(surf, BLACK, quill)
    # ink-violet trailing-edge shade (the body-side half) — hard step 2
    shade = [
        (root[0] - px * hw * 0.58, root[1] - py * hw * 0.58),
        (bx[0]   - px * hw * 0.84, bx[1]   - py * hw * 0.84),
        (tip[0]  - px * tw,        tip[1]  - py * tw),
        (tip[0]  + px * tw * 0.2,  tip[1]  + py * tw * 0.2),
        (bx[0]   - px * hw * 0.10, bx[1]   - py * hw * 0.10),
    ]
    pygame.draw.polygon(surf, INKVIO, shade)
    # FIRM steely-sheen leading rail — the night-legibility band (NOT a whisper)
    lead = [
        (root[0] + px * hw * 0.66, root[1] + py * hw * 0.66),
        (bx[0]   + px * hw * 0.92, bx[1]   + py * hw * 0.92),
        (tip[0]  + px * tw * 0.8,  tip[1]  + py * tw * 0.8),
        (tip[0]  + px * tw * 0.1,  tip[1]  + py * tw * 0.1),
        (bx[0]   + px * hw * 0.30, bx[1]   + py * hw * 0.30),
    ]
    pygame.draw.polygon(surf, SHEEN, lead)
    # a thin hot edge on the very leading rail (rim only) — hard step 4
    pygame.draw.line(surf, SHEEN_HI,
                     (root[0] + px * hw * 0.78, root[1] + py * hw * 0.78),
                     (tip[0] + px * tw * 0.6, tip[1] + py * tw * 0.6),
                     max(1, int(width * 0.10)))
    # NODE-RINGS — white sheath-scar bands crossing the slat (the bamboo tell)
    for k in range(1, nodes + 1):
        f = k / (nodes + 1)
        nx = root[0] + ca * length * f
        ny = root[1] + sa * length * f
        w_at = hw + (tw - hw) * f
        a0 = (nx + px * w_at, ny + py * w_at)
        a1 = (nx - px * w_at, ny - py * w_at)
        # the swollen node ridge (ink-violet) then the pale sheath-scar ring
        pygame.draw.line(surf, INKVIO, a0, a1, max(2, int(width * 0.22)))
        pygame.draw.line(surf, SHEEN_HI, a0, a1, max(1, int(width * 0.10)))
    pygame.draw.polygon(surf, INK, quill, max(2, int(width * 0.14)))


def quill_wing(surf, root, base_ang, s, sign, n=4, big=True):
    """ONE crow-tengu wing per side = a fan of ~4 BIG split-culm quills. WHY four,
    not many: the brief's hard constraint — fewer/bigger quills so node-rings
    survive at 32px. Longest leading primary rises up-and-out; successive quills
    rake DOWN toward the lower-outer quadrant and shorten, so each side reads as
    ONE spread crow-wing (a drooping fan), never a radial spoke-cross. `sign`
    (+1 right / -1 left) sweeps the fan outward from the shoulder."""
    L = (62.0 if big else 30.0) * s
    bw = (15.0 if big else 8.5) * s
    # (downward-sweep°, length-fac, width-fac, node-count) — graded long->short
    ranks = (
        (0,   1.00, 1.00, 2),   # P1 — longest leading primary (the wing tip)
        (26,  0.86, 0.94, 2),   # P2
        (54,  0.68, 0.86, 1),   # secondary
        (84,  0.50, 0.78, 1),   # covert — short, folded under, trailing edge
    )[:n]
    for off, fac, wfac, nodes in ranks:
        a = base_ang + sign * math.radians(off)
        split_culm_quill(surf, root, a, L * fac, bw * wfac, s, nodes=nodes)


# ── the black-bamboo STAFF (a real culm — reused for hero grip + pillar shaft) ─
def bamboo_segment(surf, cx, y0, y1, half_w, s, branch=True):
    """One black-bamboo node-segment: a glossy purple-black barrel between two
    swollen NODE rings, banded hard (ink-violet hollow -> black base -> violet
    waxy-bloom mid -> steely vertical sheen rail), with a white sheath-scar ring
    under the node and PAIRED branch-whorl stubs (Phyllostachys = paired). The
    pillar repeat band is built from a stack of these."""
    seg = [(cx - half_w, y0), (cx + half_w, y0),
           (cx + half_w, y1), (cx - half_w, y1)]
    pygame.draw.polygon(surf, INK, seg)
    pygame.draw.polygon(surf, BLACK, seg)
    # violet waxy-bloom mid-band (a hard vertical step, not a gradient)
    pygame.draw.rect(surf, BLOOM,
                     (cx - int(half_w * 0.18), y0, int(half_w * 0.5), y1 - y0))
    # ink-violet shade rail on the right (rounded-culm dark step)
    pygame.draw.rect(surf, INKVIO,
                     (cx + int(half_w * 0.42), y0, int(half_w * 0.58), y1 - y0))
    # steely vertical sheen rail on the left (the legibility band on the culm)
    pygame.draw.rect(surf, SHEEN,
                     (cx - int(half_w * 0.72), y0, int(half_w * 0.26), y1 - y0))
    pygame.draw.rect(surf, SHEEN_HI,
                     (cx - int(half_w * 0.72), y0, max(1, int(half_w * 0.08)), y1 - y0))
    pygame.draw.polygon(surf, INK, seg, max(2, int(2.0 * s)))
    # NODE ring at the TOP of the segment: swollen ridge + pale sheath-scar
    nodes_h = max(3, int(5 * s))
    node = [(cx - int(half_w * 1.12), y0 + nodes_h), (cx - half_w, y0 - nodes_h),
            (cx + half_w, y0 - nodes_h), (cx + int(half_w * 1.12), y0 + nodes_h)]
    pygame.draw.polygon(surf, INK, node)
    pygame.draw.polygon(surf, INKVIO, node)
    # white sheath-scar ring just under the node ridge (the kurochiku tell)
    pygame.draw.line(surf, SHIDE,
                     (cx - half_w, y0 + nodes_h), (cx + half_w, y0 + nodes_h),
                     max(1, int(1.6 * s)))
    pygame.draw.line(surf, SHEEN_HI,
                     (cx - int(half_w * 0.9), y0 - int(nodes_h * 0.4)),
                     (cx + int(half_w * 0.4), y0 - int(nodes_h * 0.4)),
                     max(1, int(1.2 * s)))
    if branch:
        # PAIRED branch-whorl stubs at the node (Phyllostachys signature)
        for sgn in (-1, 1):
            bx = cx + sgn * half_w
            for dy in (-int(3 * s), int(2 * s)):
                tip = (bx + sgn * int(7 * s), y0 + dy - int(4 * s))
                pygame.draw.line(surf, INK, (bx, y0 + dy), tip, max(2, int(2.6 * s)))
                pygame.draw.line(surf, BLACK, (bx, y0 + dy), tip, max(1, int(1.6 * s)))
                pygame.draw.line(surf, SHEEN, (bx, y0 + dy),
                                 (bx + sgn * int(4 * s), y0 + dy - int(2 * s)),
                                 max(1, int(1.0 * s)))


def gold_band(surf, cx, y, half_w, s, h=None):
    """A thin gold staff-band/ferrule ring — one of the two warm focal accents."""
    h = h or max(3, int(5 * s))
    pygame.draw.rect(surf, INK, (cx - half_w - 1, y - 1, half_w * 2 + 2, h + 2))
    pygame.draw.rect(surf, GOLD_D, (cx - half_w, y, half_w * 2, h))
    pygame.draw.rect(surf, GOLD, (cx - half_w, y, half_w * 2, int(h * 0.66)))
    pygame.draw.rect(surf, GOLD_HI, (cx - half_w, y, half_w * 2, max(1, int(h * 0.24))))


# ── the crow-tengu HEAD (sharp beak + vermilion wattle + tall feather-tuft) ───
def tengu_head(surf, cx, cy, r, s, lit=True):
    """A hunched crow-tengu skull: a glossy black feathered cranium hard-stepped
    for volume, a tall single FEATHER-TUFT spiking up off the crown (the karasu
    tell + the silhouette breaker), a sharp downward crow BEAK, a hooked vermilion
    NOSE/beak-WATTLE that is the warm focal, and a steely-glinting eye. Realistic
    crow proportions — NOT a chibi big-head."""
    # --- tall single FEATHER-TUFT off the crown (drawn first, behind the dome) -
    # three raked black blades, longest centre, so the crown notches the outline
    # as a clear spike at 32px (the karasu-tengu read).
    for off, fac, wf in ((-22, 0.78, 0.7), (0, 1.0, 1.0), (20, 0.82, 0.74)):
        a = math.radians(-90 + off)
        split_culm_quill(surf, (cx - int(r * 0.1), cy - int(r * 0.7)),
                         a, r * 1.7 * fac, r * 0.42 * wf, s, nodes=1)

    # --- cranium dome: a hunched crow head, hard-stepped black ---------------
    head = [(cx - int(r * 0.92), cy - int(r * 0.10)),
            (cx - int(r * 0.78), cy - int(r * 0.74)),
            (cx - int(r * 0.10), cy - int(r * 0.96)),
            (cx + int(r * 0.62), cy - int(r * 0.78)),
            (cx + int(r * 0.96), cy - int(r * 0.16)),   # back of skull
            (cx + int(r * 0.86), cy + int(r * 0.46)),
            (cx + int(r * 0.30), cy + int(r * 0.66)),   # cheek toward beak
            (cx - int(r * 0.40), cy + int(r * 0.58)),
            (cx - int(r * 0.86), cy + int(r * 0.30))]
    hard_blob(surf, BLACK, head,
              shade=INKVIO,
              shade_pts=[(cx + int(r * 0.30), cy - int(r * 0.30)),
                         (cx + int(r * 0.96), cy - int(r * 0.16)),
                         (cx + int(r * 0.86), cy + int(r * 0.46)),
                         (cx + int(r * 0.30), cy + int(r * 0.50))],
              band=BLOOM,
              band_pts=[(cx - int(r * 0.10), cy - int(r * 0.40)),
                        (cx + int(r * 0.40), cy - int(r * 0.20)),
                        (cx + int(r * 0.30), cy + int(r * 0.30)),
                        (cx - int(r * 0.10), cy + int(r * 0.20))],
              hi=SHEEN,
              hi_pts=[(cx - int(r * 0.90), cy - int(r * 0.06)),
                      (cx - int(r * 0.74), cy - int(r * 0.66)),
                      (cx - int(r * 0.30), cy - int(r * 0.50)),
                      (cx - int(r * 0.52), cy + int(r * 0.10)),
                      (cx - int(r * 0.82), cy + int(r * 0.22))],
              ow=max(1, int(1.8 * s)))

    # --- sharp downward crow BEAK (black upper) -------------------------------
    beak_root_y = cy + int(r * 0.30)
    beak = [(cx - int(r * 0.34), beak_root_y),
            (cx + int(r * 0.40), beak_root_y),
            (cx + int(r * 0.16), cy + int(r * 1.18)),   # sharp tip, slight down-hook
            (cx - int(r * 0.06), cy + int(r * 1.30)),
            (cx - int(r * 0.22), cy + int(r * 1.02))]
    hard_blob(surf, BLACK, beak,
              shade=INKVIO,
              shade_pts=[(cx + int(r * 0.06), beak_root_y),
                         (cx + int(r * 0.40), beak_root_y),
                         (cx + int(r * 0.16), cy + int(r * 1.14)),
                         (cx + int(r * 0.0), cy + int(r * 0.94))],
              hi=SHEEN,
              hi_pts=[(cx - int(r * 0.32), beak_root_y + int(r * 0.04)),
                      (cx - int(r * 0.08), beak_root_y + int(r * 0.02)),
                      (cx - int(r * 0.10), cy + int(r * 0.86)),
                      (cx - int(r * 0.22), cy + int(r * 0.96))],
              ow=max(1, int(1.6 * s)))
    # the beak's cutting edge — a hard steely glint line
    pygame.draw.line(surf, SHEEN_HI,
                     (cx - int(r * 0.30), beak_root_y + int(r * 0.06)),
                     (cx - int(r * 0.04), cy + int(r * 1.22)), max(1, int(1.4 * s)))

    # --- vermilion NOSE / beak-WATTLE: a hooked fleshy ridge over the beak base
    # THE warm focal. Sits at the cere, the highest-chroma mark on the head.
    wat = [(cx - int(r * 0.30), cy + int(r * 0.16)),
           (cx + int(r * 0.34), cy + int(r * 0.18)),
           (cx + int(r * 0.20), cy + int(r * 0.48)),
           (cx - int(r * 0.16), cy + int(r * 0.46))]
    hard_blob(surf, VERM, wat,
              shade=VERM_D,
              shade_pts=[(cx + int(r * 0.04), cy + int(r * 0.18)),
                         (cx + int(r * 0.34), cy + int(r * 0.18)),
                         (cx + int(r * 0.20), cy + int(r * 0.48)),
                         (cx + int(r * 0.04), cy + int(r * 0.44))],
              hi=VERM_HI,
              hi_pts=[(cx - int(r * 0.28), cy + int(r * 0.18)),
                      (cx - int(r * 0.02), cy + int(r * 0.20)),
                      (cx - int(r * 0.08), cy + int(r * 0.34)),
                      (cx - int(r * 0.24), cy + int(r * 0.32))],
              ow=max(1, int(1.4 * s)))
    if lit:
        # a small vermilion accent glow so the focal reads at distance (accent only)
        g = radial_glow(max(3, int(r * 0.5)), VERM, alpha_center=120, falloff=2.4)
        surf.blit(g, (cx - g.get_width() // 2, cy + int(r * 0.30) - g.get_height() // 2),
                  special_flags=pygame.BLEND_ADD)

    # --- eye: a steely glint set in the black brow (the bird stare) -----------
    ex, ey = cx + int(r * 0.30), cy - int(r * 0.06)
    pygame.draw.circle(surf, INK, (ex, ey), max(2, int(r * 0.20)))
    pygame.draw.circle(surf, SHEEN, (ex, ey), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, SHEEN_HI, (ex - int(r * 0.04), ey - int(r * 0.04)),
                       max(1, int(r * 0.06)))
    pygame.draw.circle(surf, INK, (ex, ey), max(1, int(r * 0.05)))   # hard pupil


# ── the spread-wing hero ──────────────────────────────────────────────────────
def draw_tengu(surf, cx, cy, s):
    """Hunched black-bamboo crow-tengu: REALISTIC (non-chibi) proportions — a tall
    hunched torso, two angular split-culm quill-wings spread, a crow head with a
    tall feather-tuft on top, gripping a black-bamboo staff held on-axis. `s` =
    unit scale around a ~150-unit-tall figure. Drawn back-to-front: wings ->
    staff -> torso -> arms/claws -> head last so the beak owns the read."""
    shoulder_y = cy - int(26 * s)
    shoulder_dx = int(16 * s)
    head_c = (cx, cy - int(54 * s))
    hr = int(20 * s)

    # === WINGS — two spread crow-wings of ~4 big split-culm quills (behind) ===
    wL = (cx - shoulder_dx, shoulder_y)
    wR = (cx + shoulder_dx, shoulder_y)
    # leading primary up-and-out; fan rakes DOWN to the lower-outer quadrant.
    quill_wing(surf, wL, math.radians(208), s, sign=-1, n=4, big=True)
    quill_wing(surf, wR, math.radians(-28), s, sign=+1, n=4, big=True)

    # === STAFF — a black-bamboo culm held vertically, slightly off the centre =
    stx = cx - int(20 * s)
    s_top = cy - int(64 * s)
    s_bot = cy + int(64 * s)
    hw = max(3, int(4.2 * s))
    seg_h = int(26 * s)
    y = s_top
    while y < s_bot:
        bamboo_segment(surf, stx, y, min(y + seg_h, s_bot), hw, s, branch=True)
        y += seg_h
    # gold ferrule near the grip + a fresh green node-shoot collar at the top
    gold_band(surf, stx, cy + int(2 * s), hw + int(2 * s), s)
    for sgn in (-1, 1):
        leaf = [(stx, s_top + int(2 * s)),
                (stx + sgn * int(10 * s), s_top - int(8 * s)),
                (stx + sgn * int(4 * s), s_top - int(1 * s))]
        pygame.draw.polygon(surf, INK, leaf)
        pygame.draw.polygon(surf, SHOOT_D, leaf)
        pygame.draw.polygon(surf, SHOOT,
                            [(stx, s_top + int(1 * s)),
                             (stx + sgn * int(7 * s), s_top - int(5 * s)),
                             (stx + sgn * int(3 * s), s_top)])

    # === TORSO — a tall hunched feathered body (REALISTIC, not chibi) =========
    torso = [(cx - int(15 * s), shoulder_y - int(2 * s)),
             (cx + int(17 * s), shoulder_y - int(4 * s)),   # hunched higher shoulder
             (cx + int(15 * s), cy + int(26 * s)),
             (cx + int(6 * s), cy + int(46 * s)),
             (cx - int(8 * s), cy + int(44 * s)),
             (cx - int(16 * s), cy + int(22 * s))]
    hard_blob(surf, BLACK, torso,
              shade=INKVIO,
              shade_pts=[(cx + int(2 * s), shoulder_y),
                         (cx + int(16 * s), shoulder_y - int(3 * s)),
                         (cx + int(14 * s), cy + int(26 * s)),
                         (cx + int(4 * s), cy + int(40 * s))],
              band=BLOOM,
              band_pts=[(cx - int(6 * s), cy - int(6 * s)),
                        (cx + int(6 * s), cy - int(4 * s)),
                        (cx + int(4 * s), cy + int(28 * s)),
                        (cx - int(6 * s), cy + int(26 * s))],
              hi=SHEEN,
              hi_pts=[(cx - int(15 * s), shoulder_y),
                      (cx - int(6 * s), shoulder_y - int(1 * s)),
                      (cx - int(8 * s), cy + int(14 * s)),
                      (cx - int(15 * s), cy + int(16 * s))],
              ow=max(1, int(1.8 * s)))
    # breast-feather chevrons (hard stepped feather rows, not gradient)
    for i in range(3):
        fy = shoulder_y + int(10 * s) + i * int(11 * s)
        fw = int(12 * s) - i * int(2 * s)
        pygame.draw.lines(surf, INKVIO, False,
                          [(cx - fw, fy), (cx, fy + int(5 * s)), (cx + fw, fy)],
                          max(1, int(1.6 * s)))
        pygame.draw.lines(surf, SHEEN, False,
                          [(cx - fw, fy - int(2 * s)), (cx, fy + int(3 * s)),
                           (cx + fw, fy - int(2 * s))], max(1, int(1.0 * s)))

    # === ARM/HAND gripping the staff (a clawed black hand on the culm) ========
    hand_y = cy + int(4 * s)
    arm = [(cx - int(8 * s), shoulder_y + int(6 * s)),
           (cx - int(20 * s), cy - int(6 * s)),
           (cx - int(22 * s), hand_y),
           (cx - int(14 * s), hand_y + int(4 * s)),
           (cx - int(6 * s), cy)]
    hard_blob(surf, BLACK, arm,
              shade=INKVIO,
              shade_pts=[(cx - int(8 * s), shoulder_y + int(8 * s)),
                         (cx - int(14 * s), cy - int(4 * s)),
                         (cx - int(14 * s), hand_y + int(2 * s)),
                         (cx - int(7 * s), cy)],
              hi=SHEEN,
              hi_pts=[(cx - int(18 * s), cy - int(4 * s)),
                      (cx - int(20 * s), cy - int(6 * s)),
                      (cx - int(22 * s), hand_y),
                      (cx - int(20 * s), hand_y)],
              ow=max(1, int(1.6 * s)))
    # three small claw-toes curling onto the staff
    for k in range(3):
        ty = hand_y - int(4 * s) + k * int(5 * s)
        tip = (stx - hw - int(1 * s), ty + int(2 * s))
        pygame.draw.line(surf, INK, (cx - int(20 * s), ty), tip, max(2, int(2.6 * s)))
        pygame.draw.line(surf, SHEEN, (cx - int(20 * s), ty), tip, max(1, int(1.2 * s)))

    # === scapula feather-mantle where the wings root (covers the join) ========
    for sgn in (-1, 1):
        kx = cx + sgn * shoulder_dx
        mant = [(kx - sgn * int(8 * s), shoulder_y + int(6 * s)),
                (kx - sgn * int(6 * s), shoulder_y - int(8 * s)),
                (kx + sgn * int(6 * s), shoulder_y - int(10 * s)),
                (kx + sgn * int(11 * s), shoulder_y - int(1 * s)),
                (kx + sgn * int(6 * s), shoulder_y + int(8 * s))]
        hard_blob(surf, BLACK, mant,
                  shade=INKVIO,
                  shade_pts=[(kx, shoulder_y + int(6 * s)),
                             (kx + sgn * int(10 * s), shoulder_y),
                             (kx + sgn * int(5 * s), shoulder_y + int(7 * s))],
                  hi=SHEEN,
                  hi_pts=[(kx - sgn * int(6 * s), shoulder_y - int(7 * s)),
                          (kx + sgn * int(2 * s), shoulder_y - int(9 * s)),
                          (kx - sgn * int(1 * s), shoulder_y - int(1 * s))],
                  ow=max(1, int(1.2 * s)))

    # === HEAD last — beak + vermilion wattle own the focal ====================
    pygame.draw.line(surf, INK, (cx, head_c[1] + int(hr * 0.9)),
                     (cx, shoulder_y - int(2 * s)), max(2, int(7 * s)))
    pygame.draw.line(surf, BLACK, (cx, head_c[1] + int(hr * 0.9)),
                     (cx, shoulder_y - int(2 * s)), max(1, int(4 * s)))
    pygame.draw.line(surf, SHEEN, (cx - int(2 * s), head_c[1] + int(hr * 0.9)),
                     (cx - int(2 * s), shoulder_y - int(2 * s)), max(1, int(1.2 * s)))
    tengu_head(surf, head_c[0], head_c[1], hr, s, lit=True)


# ── the black-bamboo STAFF → pillar mirror ────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The black-bamboo STAFF IS the pillar: a black node-segment shaft = the
    tileable repeat band; the gap-edge cap = a feather-tuft CROOK hung with a
    small white shide (paper streamer); the lower mirror = the gold ferrule + a
    curled fresh shoot. Slim, on-axis, bottom-rooted. `cap` names the END facing
    the GAP."""
    half_w = int(11 * s)
    seg_h = int(30 * s)
    cap_room = int(48 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    # === tileable black node-segment shaft ===================================
    y = b0
    while y < b1:
        bamboo_segment(surf, cx, y, min(y + seg_h, b1), half_w, s, branch=True)
        y += seg_h

    if cap == "bottom":
        # === gap-edge cap: feather-tuft CROOK hung with a shide ==============
        crook_y = bot - int(30 * s)
        gold_band(surf, cx, crook_y - int(8 * s), half_w + int(3 * s), s,
                  h=int(7 * s))
        # the crook = a tight raked tuft of 3 black quills curling toward the gap
        for off, fac, wf in ((-30, 0.8, 0.78), (-6, 1.0, 1.0), (24, 0.78, 0.74)):
            a = math.radians(90 + off)   # point DOWN toward the gap
            split_culm_quill(surf, (cx, crook_y), a, 34 * s * fac,
                             10 * s * wf, s, nodes=2)
        # a small white shide (zigzag paper streamer) hanging off the crook
        sx0 = cx + int(10 * s)
        zig = [(sx0, crook_y), (sx0 + int(5 * s), crook_y + int(8 * s)),
               (sx0, crook_y + int(14 * s)), (sx0 + int(5 * s), crook_y + int(22 * s)),
               (sx0, crook_y + int(28 * s))]
        pygame.draw.lines(surf, INK, False, zig, max(2, int(3 * s)))
        pygame.draw.lines(surf, SHIDE, False, zig, max(1, int(1.8 * s)))
    else:
        # === lower mirror: gold ferrule + a curled fresh shoot ===============
        ferrule_y = top + int(18 * s)
        gold_band(surf, cx, ferrule_y, half_w + int(3 * s), s, h=int(9 * s))
        # a curled fresh-green shoot springing up from the ferrule (the only green)
        cxs = cx
        cys = top + int(6 * s)
        shoot = [(cxs - int(4 * s), ferrule_y),
                 (cxs - int(8 * s), cys + int(6 * s)),
                 (cxs - int(2 * s), cys),
                 (cxs + int(5 * s), cys + int(3 * s)),
                 (cxs + int(2 * s), ferrule_y)]
        pygame.draw.polygon(surf, INK, shoot)
        pygame.draw.polygon(surf, SHOOT_D, shoot)
        pygame.draw.polygon(surf, SHOOT,
                            [(cxs - int(3 * s), ferrule_y),
                             (cxs - int(6 * s), cys + int(6 * s)),
                             (cxs - int(1 * s), cys + int(2 * s))])


# ── compose the review sheet (asthi_garuda multi-panel convention) ────────────
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
    sheet.blit(font_big.render("KUROCHIKU-GARASU-TENGU", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "black-bamboo crow-tengu  ·  WINGED BEAKED TENGU · split-culm quill-wings · vermilion wattle + gold staff · bamboo v2 REALISTIC · round 1",
        True, LABEL_DIM), (24, 42))

    # === (a) BIG HERO =========================================================
    def render_hero():
        big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
        draw_tengu(big, 184 * SS, 250 * SS, 1.78 * SS)
        small = pygame.transform.smoothscale(big, (360, 470))
        return grow_outline(small, INK + (255,), 1)

    sheet.blit(render_hero(), (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Hunched crow-tengu (realistic, non-chibi): sharp beak + vermilion wattle focal,", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("tall feather-tuft, TWO spread split-culm quill-wings (~4 big quills/side, node-rings).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Grips a black-bamboo staff (paired branch-whorls, gold ferrule, fresh-shoot collar).", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (40, 38, 52), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — bamboo staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("black node-segment shaft = repeat band;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("feather-tuft crook + shide = gap-edge cap;", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("gold ferrule + curled shoot = lower mirror.", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_tengu(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
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
    sheet.blit(font_sm.render("32px on night sky (black-on-black test)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blacked-out 32px silhouette — must read ONLY as a winged beaked tengu
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_tengu(big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        small = grow_outline(small, INK + (255,), 1)
        mask = pygame.mask.from_surface(small, 24)
        return mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))

    sil_y = night_y + 188
    sx = panel_x + 20
    pygame.draw.rect(sheet, (212, 214, 220), (sx, sil_y, 96, 96))
    pygame.draw.rect(sheet, INK, (sx, sil_y, 96, 96), 1)
    sheet.blit(silhouette32(), (sx, sil_y))
    sheet.blit(font_sm.render("32px BLACKED-OUT silhouette —", True, LABEL), (sx + 104, sil_y + 30))
    sheet.blit(font_sm.render("must read WINGED BEAKED TENGU", True, LABEL_DIM), (sx + 104, sil_y + 48))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.30 * SS, cap="bottom")
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
        (BLACK, "black-culm"), (INKVIO, "ink-violet sh"),
        (SHEEN, "steely sheen"), (BLOOM, "violet bloom"),
        (VERM, "vermilion wattle"), (GOLD, "gold band"),
        (SHOOT, "fresh shoot"), (INK, "ink keyline"),
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
        "bamboo v2 REALISTIC: SS=6 supersample -> smoothscale.  4-6 HARD STEPPED value bands per form (NO gradients) · hard ink keyline (28,22,30) · "
        "1px grown outline · radial glow for accents only · steely sheen = night-legibility band · procedural-only.",
        True, LABEL_DIM), (26, 863))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
