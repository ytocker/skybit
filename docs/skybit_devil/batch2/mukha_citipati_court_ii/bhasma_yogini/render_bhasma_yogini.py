"""
Round-1 concept renderer for BHASMA-YOGINI — the ash-ascetic seed-bead mother
(mukha_citipati_court_ii, sister #2; MUKHA body). Headless Pygame; ELEVATED
pipeline (supersample SS=8 → smoothscale) so the six-arm fan + six palm-skulls +
the knobbly rudraksha swag stay crisp at downscale. Keeps the house grammar:
flat triad fills, hard 1-2px ink keyline (28,22,26), dark-core → flat-fill →
top-left rim-sheen, 1px alpha-grown outline, chibi scary-CUTE; procedural-only.

WHY this sister reads as the ASH-ASCETIC of brood II (charnel-cave register, not
brood I's temple-treasury): the dominant MASS is ash-grey bone smeared with cool
funeral ash, the single saturated accent is saffron (the renunciate's robe), and
the one ornament class is a RUDRAKSHA seed-bead mala. The collision rule vs
asthi_dakini's bone-bead lattice is honoured by SILHOUETTE + TEXTURE, not hue:
each seed is a KNOBBLY, irregular, matte warm-brown nut (puckered/pitted like a
walnut, no two alike, NO smooth pale pip, NO socket-dots), and they string as a
SINGLE FAT U-SWAG across the chest — never a multi-strand net.

WHY the JATA topknot is the gameplay carrier: a lumpy dark matted-dreadlock mass
piled above the crown is a silhouette nothing else in either brood owns. It sits
BEHIND/ABOVE the fused crown so the Citipati 5-skull arc-sweep AND the Mukha
tiara-band still read IN FRONT (never masked). The jata is sculpted/ordered
(reverent ascetic gravitas, the jatamukuta of a yogi), never a messy comic mop.

WHY the alms-staff (khatvanga of seed-bead + ash) IS the pillar: a banded ash
shaft strung with the rudraksha U-swag motif tiles as the repeatable shaft; a
single saffron-lit skull capped by the jata-knot is the gap-edge cap — the
creature's own forms, mirrored on-axis, never top-heavy.

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

# Font lives in the shipped assets dir, five levels up from this sister folder.
FONT_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "..", "game", "assets"))
FONT_PATH = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")


# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Ash-grey bone is the dominant MASS — a cool funeral-ash desaturated bone, NOT
# the rose-bone of Mukha-Devi nor the warm ivory of Citipati. Saffron is the one
# saturated accent (renunciate's robe + third-eye). Seed-brown is the rudraksha
# mala — warm, matte, knobbly, the texture tell vs smooth bone pips.
ASH       = (206, 204, 200)   # ash-grey bone (the dominant fill)
ASH_D     = (150, 148, 146)   # ash dark-core / shade
ASH_DD    = (102, 100, 100)   # deepest ash hollow (sockets, rib gaps)
ASH_SH    = (238, 238, 234)   # ash top-left rim-sheen
SMEAR     = (176, 176, 172)   # cool ash-smear band over the bone (the vibhuti)
CROWN_ASH = (186, 182, 176)   # dim tier — warm ash crown & tiara skulls, a step under body ASH
CROWN_ASH_SH = (212, 208, 202)
SAFF      = (236, 150,  46)   # saffron robe + accent (the one saturated note)
SAFF_BR   = (252, 200, 110)   # hot saffron sheen / inner
SAFF_D    = (176,  98,  26)   # deep saffron shade
# WHY a dedicated dim-ember tone (~173 lum) sits between SAFF and SAFF_D: the
# upper-left palm-skull's lit socket sat alone high on its arm at ~194 lum, only
# a notch under the focal third-eye, so it competed. This banks it at/just below
# the arm-cuff pips, keeping the third-eye the single brightest pixel.
SAFF_EMBER = (226, 162,  90)  # dim saffron ember (~173 lum) for the lone hi relic
# WHY pushed a touch warmer/redder-brown than round 1: at 32px the saffron robe
# and the seed-brown were drifting toward the same orange note; a redder mahogany
# keeps the mala a separate brown read from the saffron even when downscaled.
SEED      = (138,  78,  44)   # rudraksha seed-brown (knobbly matte mala)
SEED_BR   = (180, 116,  66)   # seed top-light (still MATTE — low spread)
SEED_D    = ( 88,  48,  28)   # seed deep pit / cord-shadow
SEED_DD   = ( 58,  32,  20)   # the pitted walnut grooves (no specular)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (250, 176,  64)   # saffron-amber third-eye (the brightest focal)
THIRD_BR  = (255, 226, 150)

BG        = ( 92,  90,  92)   # neutral grey review backdrop
PANEL     = ( 72,  70,  74)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 238, 238)
LABEL_DIM = (198, 194, 198)


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


# ── a single KNOBBLY rudraksha seed bead (the texture tell vs bone pips) ──────
def seed_bead(surf, cx, cy, r, s, seed=0):
    """ONE rudraksha seed — a matte warm-brown NUT, deliberately NOT a smooth bone
    pip. WHY irregular + pitted: asthi_dakini's bone-bead lattice is smooth pale
    round pips with socket-dots; the collision is broken by SILHOUETTE+TEXTURE.
    Each bead is a slightly lobed blob (a few bulges so the outline is knobbly,
    never a clean circle) with DEEP pit-grooves and NO bright specular — the warm
    light is kept low-spread so the bead reads MATTE like a walnut. `seed` jitters
    the lobes so no two beads look identical (the natural-seed read)."""
    rng = (seed * 2654435761) & 0xFFFFFFFF
    def jit(span):
        nonlocal rng
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        return (rng / 0x7FFFFFFF - 0.5) * span
    # a lobed/knobbly outline — 7 bumps with jittered radius so it reads irregular
    lobes = 7
    pts = []
    for i in range(lobes):
        a = (i / lobes) * 2 * math.pi
        rr = r * (1.0 + 0.18 * math.cos(a * 2 + seed) + jit(0.16))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, SEED, pts)
    # deep dark core bottom-right — keeps it round-bodied but MATTE
    pygame.draw.circle(surf, SEED_D,
                       (cx + int(r * 0.22), cy + int(r * 0.24)), int(r * 0.66))
    pygame.draw.circle(surf, SEED, (cx, cy), int(r * 0.74))
    # the pitted walnut grooves — meridian + cross furrows (no two seeds alike)
    for k in range(3):
        a = math.radians(28 + k * 58 + (seed * 23) % 40)
        pygame.draw.line(surf, SEED_DD,
                         (cx - math.cos(a) * r * 0.82, cy - math.sin(a) * r * 0.82),
                         (cx + math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82),
                         max(1, int(1.4 * s)))
    # a SMALL, low-spread top-light dot — matte, not a glossy bone glint
    pygame.draw.circle(surf, SEED_BR,
                       (cx - int(r * 0.30), cy - int(r * 0.32)), max(1, int(r * 0.24)))
    pygame.draw.polygon(surf, INK, pts, max(1, int(1.3 * s)))


# ── the rudraksha mala as a single fat U-SWAG (NOT a multi-strand lattice) ────
def seed_swag(surf, cx, cy, span, dip, r, s, n=11):
    """A single hanging U-loop of rudraksha seeds across the chest. WHY one fat
    swag, not a net: asthi_dakini owns the multi-strand smooth-pip LATTICE; this
    is ONE catenary string of knobbly seeds, the silhouette difference doing the
    distinctness work. The cord dips low at centre (gravity) and the centre bead
    is the largest (a guru-bead), so it reads as one mala draped on the body."""
    # the catenary cord the beads thread onto (a real U, low at the middle)
    cord = []
    for i in range(41):
        t = i / 40.0
        x = cx - span + t * span * 2
        y = cy + dip * (1 - (2 * t - 1) ** 2)   # parabolic dip
        cord.append((x, y))
    pygame.draw.lines(surf, SEED_D, False, cord, max(2, int(3.0 * s)))
    pygame.draw.lines(surf, INK, False, cord, max(1, int(1.2 * s)))
    # beads strung evenly along the U; centre bead larger (guru bead)
    for i in range(n):
        t = i / (n - 1)
        x = cx - span + t * span * 2
        y = cy + dip * (1 - (2 * t - 1) ** 2)
        edge = abs(2 * t - 1)
        br = r * (1.0 - 0.18 * edge)
        if i == n // 2:
            br = r * 1.5   # the guru bead at the bottom of the loop
        seed_bead(surf, int(x), int(y), int(br), s, seed=i + 3)


# ── a single ornamental tiara-skull (reused for tiara + pillar) ───────────────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny ash-bone skull for the Mukha tiara-BAND across the brow. A domed
    cranium + two dark sockets + a stub jaw, kept LOW on the brow so the face
    still reads under the arm-fan and below the jata mass. `lit` glows the
    centre-skull eyes saffron (the one crown glow allowed). DIMMEST tier — drawn
    in cool greyer CROWN_ASH so the value ladder reads below the mid palm-skulls."""
    triad_circle(surf, CROWN_ASH, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, CROWN_ASH, jaw, ow=max(1, int(1.1 * s)))
    eye_c = SAFF_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))
    # faint ascetic echo — a single dim tilaka stripe across the brow so the
    # crown shares the renunciate language, kept DIMMEST (CROWN_ASH_SH, no glow).
    pygame.draw.line(surf, CROWN_ASH_SH, (cx - int(r * 0.30), cy - int(r * 0.42)),
                     (cx + int(r * 0.30), cy - int(r * 0.42)), max(1, int(1.2 * s)))


# ── a single Citipati crown-skull (the OUTER 5-skull arc-sweep) ───────────────
def crown_skull(surf, cx, cy, r, s, lit=False, variant=0):
    """Tiny ash skull for the Citipati 5-skull arc that owns the OUTER silhouette
    arc. Bigger sockets than the tiara skull so the arc reads countable at 32px.
    The crown is the DIMMEST tier of the value ladder — drawn in cool greyer
    CROWN_ASH (~17% below mid). Only the centre skull is `lit` (a small saffron
    pin kept clearly below the third-eye), the one crown glow the brief allows.
    `variant` individuates the otherwise-mirror inner pair so the arc has no
    near-repeat: 1 = eroded/asymmetric jaw with a missing front tooth (one value
    step of crown<->brow separation so it doesn't read muddy); 2 = a fuller
    three-stripe tripundra brow band. Stays the DIMMEST tier + clean at 32px."""
    triad_circle(surf, CROWN_ASH, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    # variant 1 leans the jaw off-axis (eroded relic); the others stay square.
    jskew = int(r * 0.16) if variant == 1 else 0
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34) + jskew, cy + int(r * 1.0)),
           (cx - int(r * 0.34) + jskew, cy + int(r * 1.0))]
    triad_blob(surf, CROWN_ASH, jaw, ow=max(1, int(1.2 * s)))
    eye_c = SAFF_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    # bite line — variant 1 carries a missing front tooth (a gap punched into the
    # bite line) so its grin reads asymmetric vs its mirror twin.
    pygame.draw.line(surf, INK, (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)), max(1, int(1.2 * s)))
    if variant == 1:
        gap = int(r * 0.10)
        pygame.draw.line(surf, CROWN_ASH, (cx - gap, cy + int(r * 0.70)),
                         (cx + gap, cy + int(r * 0.70)), max(2, int(2.4 * s)))
    # faint ascetic echo — a dim tilaka stripe across the brow. variant 2 wears a
    # FULLER three-stripe tripundra band (more brow language); variant 1 (eroded)
    # gets one value step of moss-dark crown<->brow separation so the dark cap and
    # the band don't read muddy together.
    if variant == 2:
        for bi in range(3):
            by = cy - int(r * 0.46) + bi * int(r * 0.13)
            bw = r * (0.34 - bi * 0.05)
            pygame.draw.line(surf, CROWN_ASH_SH, (cx - bw, by), (cx + bw, by),
                             max(1, int(1.3 * s)))
    else:
        if variant == 1:
            # a darker moss cap above the brow lifts the band off the crown by a
            # value step (separation so the eroded skull doesn't read flat/muddy).
            pygame.draw.line(surf, lerp(CROWN_ASH, INK, 0.30),
                             (cx - int(r * 0.30), cy - int(r * 0.52)),
                             (cx + int(r * 0.30), cy - int(r * 0.52)), max(1, int(1.6 * s)))
        pygame.draw.line(surf, CROWN_ASH_SH, (cx - int(r * 0.32), cy - int(r * 0.40)),
                         (cx + int(r * 0.32), cy - int(r * 0.40)), max(1, int(1.3 * s)))
    if lit:
        pygame.draw.circle(surf, SAFF_D, (cx, cy - int(r * 0.18)), max(1, int(r * 0.10)))


# ── a tiny palm-skull each open hand cradles (the core motif) ─────────────────
def palm_skull(surf, cx, cy, r, s, idx=0):
    """A TINY ash skull cradled in one open palm — the MID tier of the value
    ladder (brighter than the crown, dimmer than the third-eye). Now each of the
    six is a GENUINELY DISTINCT charnel-ground relic, individuated by `idx`: a
    different CRANIUM SHAPE (round / tall / broad / asymmetric-eroded), different
    JAW + TOOTH LOSS, and its own ascetic MARKING set — a horizontal tripundra
    band across the brow, diagonal ash-smear streaks, a knobbly rudraksha seed
    pressed at brow or temple, surface pitting/erosion, and a moss/ash-darkened
    crown. Two-to-three of the six (idx in SAFF_SKULLS) carry a DIM saffron
    accent (a brow bindu or a saffron-tinted socket) kept clearly below the
    head's focal third-eye — never a hot near-white core. SIZE unchanged (`r`).
    WHY an explicit idx (with the position hash kept as a secondary jitter seed):
    the six can be cleanly individuated + gem-assigned, deterministic per slot."""
    lw = max(1, int(1.0 * s))
    # idx drives the structural identity; the position hash is a secondary jitter
    # so two relics sharing an idx-archetype still wobble apart microscopically.
    v = (cx * 13 + cy * 7)
    n = idx % 6
    # which slots carry the DIM saffron element — kept to 3 of 6, none near the
    # head, all sub-focal (deep/mid saffron, no hot core).
    SAFF_SKULLS = (1, 3, 5)

    # per-idx cranium archetype: (x-radius mul, y-radius mul, tilt, lean-skew)
    # so the dome is a DIFFERENT SHAPE per slot, not one ball re-tilted.
    archs = [
        (1.00, 1.02,  0.00,  0.00),   # 0: balanced round relic
        (0.90, 1.16, -0.05,  0.00),   # 1: tall narrow ascetic cranium
        (1.16, 0.92,  0.04,  0.00),   # 2: broad low brachycephalic skull
        (1.02, 1.04,  0.10,  0.08),   # 3: asymmetric, eroded-leaning
        (0.96, 1.08, -0.10, -0.06),   # 4: slim tilted relic
        (1.08, 0.98,  0.02,  0.05),   # 5: wide weathered guru-skull
    ]
    rx_m, ry_m, tilt, skew = archs[n]
    tilt += ((v % 5) - 2) * 0.012     # tiny secondary wobble off position hash
    jaw_open = 0.40 + (n % 3) * 0.08
    ct, stt = math.cos(tilt), math.sin(tilt)

    def rot(dx, dy):
        # skew leans the upper cranium so the eroded relics are visibly lopsided
        dx2 = dx + skew * (-dy) if dy < 0 else dx
        return (int(cx + dx2 * ct - dy * stt), int(cy + dx2 * stt + dy * ct))

    # cranial dome — an ELLIPTICAL ball per archetype so the shape varies; ink
    # keyline first, then the ash-sheen fill, so it reads rounded.
    drx, dry = int(r * rx_m), int(r * ry_m)
    dome = []
    for i in range(20):
        a = (i / 20) * 2 * math.pi
        dome.append(rot(math.cos(a) * drx, math.sin(a) * dry))
    pygame.draw.polygon(surf, INK, dome)
    pygame.draw.polygon(surf, ASH_SH, dome)
    pygame.draw.polygon(surf, INK, dome, max(1, int(1.2 * s)))
    shade = lerp(ASH_SH, ASH_D, 0.55)
    bright = lerp(ASH_SH, (255, 255, 255), 0.4)
    moss = lerp(ASH_D, (96, 104, 86), 0.5)   # ash/moss-darkened crown weathering

    # a moss/ash-darkened crown cap on the weathered relics (idx 2,4) — a
    # desaturated cool patch over the dome top so it reads charnel-aged.
    if n in (2, 4):
        cap = [rot(-drx * 0.74, -dry * 0.30), rot(-drx * 0.34, -dry * 0.78),
               rot(drx * 0.10, -dry * 0.86), rot(drx * 0.52, -dry * 0.60),
               rot(drx * 0.70, -dry * 0.24)]
        pygame.draw.polygon(surf, moss, cap)

    # surface PITTING / erosion — a scatter of tiny dark pocks, denser on the
    # eroded relics; deterministic off (idx, position) so each relic is its own.
    pit_n = (3, 2, 5, 6, 5, 3)[n]
    pr = (v ^ (idx * 2654435761)) & 0x7FFFFFFF
    for _ in range(pit_n):
        pr = (pr * 1103515245 + 12345) & 0x7FFFFFFF
        pa = (pr / 0x7FFFFFFF) * 2 * math.pi
        pr = (pr * 1103515245 + 12345) & 0x7FFFFFFF
        pd = (0.30 + (pr / 0x7FFFFFFF) * 0.55)
        pp = rot(math.cos(pa) * drx * pd, math.sin(pa) * dry * pd)
        pygame.draw.circle(surf, shade, pp, max(1, int(r * 0.06)))

    # sagittal suture — a faint wavy seam down the crown (cranial detail)
    sut = [rot(int(r * 0.04 * math.sin(k)), int(-dry * (0.88 - k * 0.20)))
           for k in (0.0, 1.0, 2.0, 3.0)]
    pygame.draw.lines(surf, shade, False, sut, lw)

    # brow ridge — a shaded arc shelf above the sockets gives the skull a face
    brow = [rot(-r * 0.58, -r * 0.10), rot(-r * 0.30, -r * 0.30),
            rot(0, -r * 0.34), rot(r * 0.30, -r * 0.30), rot(r * 0.58, -r * 0.10)]
    pygame.draw.lines(surf, shade, False, brow, lw)

    # temple / cheek hollows — short shade ticks pinch the face below the dome
    for sgn in (-1, 1):
        pygame.draw.line(surf, shade, rot(sgn * r * 0.62, -r * 0.02),
                         rot(sgn * r * 0.50, r * 0.34), lw)

    # deep eye sockets — ink pit with a faint inner highlight so they read
    # carved. idx 3 (asymmetric) loses one socket-rim to erosion; the saffron
    # relics get a DIM deep-saffron socket-tint (sub-focal, no hot core).
    # WHY idx 1 (the upper-left relic, isolated on its own arm) uses the deeper
    # SAFF_EMBER and DROPS the near-white socket glint: high + alone it was the
    # only mid-tier carrier close enough to rival the focal third-eye, so it is
    # pulled one step toward SAFF_D into the ~172-lum band (at/just below the
    # arm cuff pips) and stripped of the white falloff that read hot on it. The
    # lower-row saffron carriers keep the brighter socket — they read fine.
    saff_socket = (SAFF_EMBER if n == 1 else SAFF_D) if n in SAFF_SKULLS else None
    for si, ex in enumerate((-0.40, 0.40)):
        sc = rot(ex * r, -r * 0.02)
        pygame.draw.circle(surf, INK, sc, max(1, int(r * 0.28)))
        if saff_socket and si == 0:
            # one socket lit by a DIM ember of saffron — deep tone, kept tiny
            pygame.draw.circle(surf, saff_socket, sc, max(1, int(r * 0.16)))
        rim = (shade if not (n == 3 and si == 1) else moss)
        pygame.draw.circle(surf, rim, sc, max(1, int(r * 0.30)), lw)
        # skip the near-white socket glint on idx 1's lit ember so no falloff
        # pixel spikes its value back up toward the focal third-eye.
        if n == 1 and si == 0:
            continue
        pygame.draw.circle(surf, bright,
                           (sc[0] - max(1, int(r * 0.10)), sc[1] - max(1, int(r * 0.10))),
                           max(1, int(r * 0.07)))

    # triangular nasal aperture
    nasal = [rot(0, r * 0.10), rot(-r * 0.16, r * 0.40), rot(r * 0.16, r * 0.40)]
    pygame.draw.polygon(surf, INK, nasal)

    # proper jaw — per-idx mandible: idx 4 has NO jaw (jawless relic), idx 0/5
    # a full grin, idx 1/2/3 a slack hinge; tooth loss varies the bite line.
    if n != 4:
        jy = r * (0.30 + jaw_open * 0.30)
        jw = (0.44, 0.40, 0.46, 0.42, 0.0, 0.48)[n]
        jaw = [rot(-r * jw, r * 0.40), rot(-r * (jw * 0.77), jy),
               rot(0, jy + r * 0.06), rot(r * (jw * 0.77), jy), rot(r * jw, r * 0.40)]
        pygame.draw.polygon(surf, ASH_SH, jaw)
        pygame.draw.lines(surf, INK, False, jaw, lw)
        # tooth row — each relic has missing teeth at different slots (tooth loss)
        teeth_y = r * 0.44
        missing = ((), (1,), (0, 3), (2,), (), (1, 2))[n]
        for ti, tx in enumerate((-0.24, -0.08, 0.08, 0.24)):
            if ti in missing:
                continue
            pygame.draw.line(surf, shade, rot(tx * r, teeth_y),
                             rot(tx * r, teeth_y + r * 0.16), lw)
    else:
        # jawless relic — a raw ink bite-stub where the mandible broke away
        pygame.draw.line(surf, ASH_DD, rot(-r * 0.30, r * 0.42),
                         rot(r * 0.30, r * 0.42), max(1, int(2.0 * s)))

    # ── ASCETIC MARKINGS — each relic wears the marks of the renunciate ────────
    # a horizontal TRIPUNDRA tilaka band across the brow (idx 0,2,5) — the same
    # forehead language as the head, scaled to the relic.
    if n in (0, 2, 5):
        for bi in range(2):
            by = -r * 0.50 + bi * r * 0.14
            bw = r * (0.36 - bi * 0.06)
            mk = ASH_SH if n != 5 else lerp(ASH_SH, SMEAR, 0.3)
            pygame.draw.line(surf, INK, rot(-bw, by), rot(bw, by), max(2, int(2.0 * s)))
            pygame.draw.line(surf, mk, rot(-bw, by), rot(bw, by), max(1, int(1.2 * s)))

    # diagonal ASH-SMEAR streaks down a cheek (idx 1,3,4) — the vibhuti swipe,
    # cool smear over the bone so the relic reads hand-marked, not clean.
    if n in (1, 3, 4):
        for k in range(2):
            sxk = (-0.34 + k * 0.62)
            pygame.draw.line(surf, SMEAR, rot(sxk * r, -r * 0.12),
                             rot(sxk * r - r * 0.10, r * 0.30), max(1, int(2.2 * s)))

    # a pressed RUDRAKSHA seed bead at brow or temple (every relic gets one, the
    # mala-mark of the order); placed per idx so it doesn't always sit centre.
    seed_pos = [(0.0, -0.40), (0.0, -0.46), (-0.52, -0.16),
                (0.46, -0.20), (0.0, -0.42), (0.50, -0.14)][n]
    sb = rot(seed_pos[0] * r, seed_pos[1] * r)
    seed_bead(surf, sb[0], sb[1], max(2, int(r * 0.20)), s, seed=idx + 17)

    # a DIM saffron brow BINDU on the saffron relics that did NOT get the socket
    # ember — kept deep/mid saffron, no hot core, so the head's third-eye stays
    # the single brightest pixel.
    if n in SAFF_SKULLS:
        bn = rot(0, -r * 0.18)
        pygame.draw.circle(surf, SAFF_D, bn, max(1, int(r * 0.13)))
        pygame.draw.circle(surf, SAFF, bn, max(1, int(r * 0.07)))


# ── the six-arm radial fan with OPEN palms cradling tiny skulls ───────────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat ash-bone arms splay in a wide symmetric STARBURST around the torso
    (the MUKHA KIND tell). Low origin, ~[100,64,28]° off vertical, NONE straight
    up → the crown sky stays open for the jata + fused crown. Each arm ends in an
    OPEN PALM that cradles a tiny skull. Ash-smear bands ring the forearms so the
    arms never read naked. Returns the six hand centres + their open-palm angles."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    spread = [100, 64, 28]   # degrees off vertical, 3 per side; none vertical
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])   # lowest arms first, upper splay overlaps clean
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
            triad_blob(surf, ASH, quad,
                       sheen_pts=[(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                                  (q[0] + nx * 0.3, q[1] + ny * 0.3),
                                  (p[0] + nx * 0.3, p[1] + ny * 0.3)],
                       ow=max(1, int(arm_th * 0.16)))
        triad_circle(surf, ASH, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        # a saffron + ash-smear forearm cuff so the arm reads dressed, not naked
        cuf = (sh[0] + math.cos(a) * arm_len * 0.78,
               sh[1] + math.sin(a) * arm_len * 0.78)
        pygame.draw.circle(surf, SMEAR, (int(cuf[0]), int(cuf[1])), max(1, int(arm_th * 0.5)))
        pygame.draw.circle(surf, SAFF, (int(cuf[0]), int(cuf[1])), max(1, int(arm_th * 0.28)))
        hands.append((sgn, d, hand, a))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1]), h[3]) for h in hands]


def draw_open_palm(surf, hx, hy, ang, s, r):
    """An OPEN cupped palm at a fan tip — a small ash blob with three short finger
    ticks curling toward the cradled skull, so the hand reads as holding, not a
    fist. Drawn before the palm-skull so the skull sits IN the cup."""
    triad_circle(surf, ASH, (hx, hy), int(r * 0.9), ow=max(1, int(1.2 * s)), core=False)
    for k in range(-1, 2):
        fa = ang - math.pi / 2 + k * 0.5   # fingers fan toward the sky-side of the tip
        ex = hx + math.cos(fa) * r * 1.5
        ey = hy + math.sin(fa) * r * 1.5
        pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(2, int(3.2 * s)))
        pygame.draw.line(surf, ASH, (hx, hy), (ex, ey), max(1, int(1.8 * s)))


# ── the ash-ascetic seed-bead mother ──────────────────────────────────────────
def draw_bhasma_yogini(surf, cx, cy, s):
    """Pint-sized six-armed ash-mother on a wide lotus base: a chibi ash skull
    framed by a low-origin six-arm fan, each open palm cradling a tiny skull, a
    single fat rudraksha U-swag across the chest, the fused Citipati 5-skull
    arc + Mukha tiara-band on the brow, and a lumpy matted-hair JATA topknot
    piled BEHIND/ABOVE the crown. `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)
    palm_r = int(9 * s)

    # === SIX-ARM RADIAL FAN (drawn first → behind torso & head) ===============
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr)

    # === LOWER BODY — a WIDE 6-PETAL LOTUS base (the MUKHA body-base separator) =
    # WHY a true lotus profile, not a banded plinth: the brief's MUKHA references
    # seat the figure on an unambiguous open lotus. Five upturned front petals
    # (overlapping pointed leaves) fan out wide and shallow; the body rises from
    # their hollow. Petals alternate ash / saffron-tipped so the bloom reads.
    base_y = cy + int(40 * s)
    pet_w = int(13 * s)
    pet_h = int(20 * s)
    # the front rank of 5 open petals, centre tallest, fanning outward + down
    pet_specs = [(-2, -0.42), (-1, -0.20), (0, 0.0), (1, 0.20), (2, 0.42)]
    for k, tilt in pet_specs:
        bx = cx + int(k * pet_w * 0.92)
        tipx = bx + int(tilt * pet_w * 2.0)
        tip = (tipx, base_y - pet_h)
        lft = (bx - pet_w // 2, base_y + int(4 * s))
        rgt = (bx + pet_w // 2, base_y + int(4 * s))
        mid_l = ((lft[0] + tip[0]) // 2 - int(pet_w * 0.18), (lft[1] + tip[1]) // 2)
        mid_r = ((rgt[0] + tip[0]) // 2 + int(pet_w * 0.18), (rgt[1] + tip[1]) // 2)
        petal = [lft, mid_l, tip, mid_r, rgt]
        col = SAFF if (k % 2 == 0) else ASH
        triad_blob(surf, col, petal,
                   sheen_pts=[lft, mid_l, ((mid_l[0]+tip[0])//2, (mid_l[1]+tip[1])//2)],
                   ow=max(1, int(1.6 * s)))
        # a centre vein down each petal (the lotus-leaf tell)
        vcol = SAFF_D if (k % 2 == 0) else ASH_DD
        pygame.draw.line(surf, vcol, (bx, base_y + int(2 * s)), tip, max(1, int(1.6 * s)))
    # the lotus calyx hollow the body sits in — a small dark seedpod heart
    pygame.draw.circle(surf, SEED_D, (cx, base_y - int(6 * s)), int(6 * s))
    pygame.draw.circle(surf, SEED, (cx - int(1 * s), base_y - int(7 * s)), max(1, int(2.4 * s)))
    pygame.draw.circle(surf, SEED_BR, (cx - int(2 * s), base_y - int(8 * s)), max(1, int(1.2 * s)))

    # === TORSO — a SHORT ash rib barrel, smeared with funeral ash =============
    rc_cx, rc_cy = cx, cy + int(12 * s)
    rc_w, rc_h = int(32 * s), int(24 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42), rc_cy + rc_h // 2)]
    triad_blob(surf, ASH, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(4 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(2 * s))],
               ow=max(1, int(1.8 * s)))
    # horizontal ash-smear (vibhuti) bands across the ribs — the ascetic tell.
    # WHY paired ink-shadowed bands the full torso width: the bare slab must carry
    # the same tripundra ash language as the brow so the body never reads naked,
    # even on the lower ribs the swag leaves exposed.
    for i in range(4):
        sy = rc_cy - rc_h // 2 + int(5 * s) + i * int(6 * s)
        bw = int(rc_w * 0.42) - int(i * 1.0 * s)
        pygame.draw.line(surf, INK, (rc_cx - bw, sy + int(1 * s)),
                         (rc_cx + bw, sy + int(1 * s)), max(2, int(3.0 * s)))
        pygame.draw.line(surf, SMEAR, (rc_cx - bw, sy),
                         (rc_cx + bw, sy), max(2, int(2.6 * s)))
    pygame.draw.line(surf, ASH_DD, (rc_cx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx, rc_cy + int(8 * s)), max(1, int(2 * s)))
    # a saffron renunciate's waist-wrap knotting the torso into the lotus — closes
    # the gap between the bare ribs and the bloom so the body reads dressed.
    wy = rc_cy + rc_h // 2 - int(2 * s)
    wrap = [(rc_cx - int(rc_w * 0.46), wy),
            (rc_cx + int(rc_w * 0.46), wy),
            (rc_cx + int(rc_w * 0.40), wy + int(7 * s)),
            (rc_cx - int(rc_w * 0.40), wy + int(7 * s))]
    triad_blob(surf, SAFF, wrap,
               sheen_pts=[(rc_cx - int(rc_w * 0.46), wy), (rc_cx, wy),
                          (rc_cx, wy + int(3 * s)), (rc_cx - int(rc_w * 0.46), wy + int(3 * s))],
               ow=max(1, int(1.4 * s)))
    pygame.draw.line(surf, SAFF_D, (rc_cx - int(rc_w * 0.42), wy + int(4 * s)),
                     (rc_cx + int(rc_w * 0.42), wy + int(4 * s)), max(1, int(1.6 * s)))

    # === SIX PALM-SKULLS — one cradled in each open hand (the core motif) ======
    # Drawn after torso, before head: they ride at the fan tips so the outer arc
    # is six even bone-pips; each is an OPEN palm cupping a tiny skull.
    for i, (hx, hy, ang) in enumerate(hands):
        draw_open_palm(surf, hx, hy, ang, s, palm_r)
        palm_skull(surf, hx, hy - int(palm_r * 0.25), int(palm_r * 0.78), s, idx=i)

    # === RUDRAKSHA SEED-SWAG — a single fat U across the chest (the ornament) ==
    # WHY routed in FRONT of the torso but BETWEEN the arm origins: it must read
    # as the dressed mala without occluding any palm-skull. One catenary loop of
    # knobbly matte brown seeds — NOT asthi's smooth multi-strand pip lattice.
    # WHY slung WIDE and high off the shoulders with a fat guru-bead: the seed
    # distinctness is the locked CRITICAL tell, so the swag must be unmistakably
    # the secondary read — a generous U that brackets the upper ribs clear of the
    # chin, not a thin necklace buried under the jaw.
    seed_swag(surf, rc_cx, rc_cy - int(rc_h * 0.50), int(rc_w * 0.82),
              int(rc_h * 0.92), int(6.2 * s), s, n=11)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (the framed FACE) =========
    triad_circle(surf, ASH, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, ASH_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two lower sockets — a NOTCH dimmer than the third eye (dark hollow + small
    # deep-saffron pin, no hot core) so the 3-eye triangle points UP to the brow.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, ASH_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, SAFF_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # THIRD EYE — the single BRIGHTEST pixel (AD hard rule). A saffron-amber
    # teardrop with a hot core, central on the brow. Kept compact so the forehead
    # above it stays open for the tripundra ash-marks.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.20)
    pygame.draw.ellipse(surf, INK, (tex - int(6 * s), tey - int(7 * s), int(12 * s), int(15 * s)))
    pygame.draw.ellipse(surf, SAFF, (tex - int(5 * s), tey - int(6 * s), int(10 * s), int(13 * s)))
    pygame.draw.ellipse(surf, SAFF_BR, (tex - int(3 * s), tey - int(4 * s), int(7 * s), int(9 * s)))
    pygame.draw.circle(surf, THIRD_BR, (tex - int(1 * s), tey - int(1 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    # TRIPUNDRA — three clean horizontal ash tilaka marks across the brow, framing
    # the third-eye from ABOVE (the ascetic forehead tell). Drawn AFTER the eye so
    # the ash-marks sit on top; seated in the open forehead strip above the eye.
    for i in range(3):
        ly = head_c[1] - int(hr * 0.50) + i * int(hr * 0.034)
        ww = hr * (0.27 - i * 0.045)
        pygame.draw.line(surf, INK, (head_c[0] - ww, ly), (head_c[0] + ww, ly),
                         max(2, int(2.6 * s)))
        pygame.draw.line(surf, ASH_SH, (head_c[0] - ww, ly), (head_c[0] + ww, ly),
                         max(1, int(1.5 * s)))
    # nose triangle
    pygame.draw.polygon(surf, ASH_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # grinning tooth row + corner fangs (wrathful, not gory)
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.48), my),
                     (head_c[0] + int(hr * 0.48), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.15), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.15), my + int(hr * 0.13)), max(1, int(1 * s)))
    for sgn in (-1, 1):
        fx = head_c[0] + sgn * int(hr * 0.40)
        pygame.draw.polygon(surf, ASH_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.22))])

    # === JATA TOPKNOT — the DOMINANT dark dome, BEHIND/ABOVE the whole crown ===
    # WHY drawn HERE (after the head, before the crown): the lumpy dark jata mass
    # crests ABOVE the 5-skull arc as a single tall dome — the tallest, darkest
    # 32px blackout shape. Raised so its dome+bun clear the arc; the arc + tiara-
    # band still read IN FRONT (drawn after). This dark mass is the SILHOUETTE
    # CARRIER (nothing else in either brood owns it).
    draw_jata(surf, head_c[0], head_c[1] - int(hr * 0.42), hr, s)

    # === Citipati 5-skull arc-SWEEP — a tight upper ring hugging the dome ======
    # Drawn AFTER the jata so the countable arc reads in front of the dome. Seated
    # HIGH + tight (a crowning ring around the dome base) so it stays clearly
    # ABOVE and separate from the brow tiara-band added below.
    arc_band_r = int(hr * 1.30)
    skull_cr = hr * 1.46
    skull_r = int(hr * 0.32)
    arc_pts = []
    for i in range(13):
        a = math.radians(220 + i * (100 / 12))
        arc_pts.append((head_c[0] + math.cos(a) * arc_band_r,
                        head_c[1] + math.sin(a) * arc_band_r))
    pygame.draw.lines(surf, INK, False, arc_pts, int(5 * s))
    pygame.draw.lines(surf, SEED, False, arc_pts, int(3 * s))   # seed-brown crown cord
    # the inner-lower mirror pair (i=1,3) were the last near-repeat in the arc;
    # variant 1 = eroded/asymmetric jaw + missing front tooth, variant 2 = fuller
    # tripundra brow band, so no two crown skulls read identical.
    crown_variants = (0, 1, 0, 2, 0)
    for i in range(5):
        a = math.radians(224 + i * (92 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = head_c[1] + math.sin(a) * skull_cr
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2),
                    variant=crown_variants[i])

    # === Mukha TIARA-BAND across the BROW — explicit HORIZONTAL fillet, FRONTMOST
    # WHY drawn LAST + seated LOW on the forehead: the brief demands the tiara-band
    # read in FRONT of and visually SEPARATE from the arc-sweep above. A straight
    # saffron ash fillet laid flat across the brow (a real headband, not a buried
    # radial arc), riding just above the third-eye + tripundra, with 3 dim crown-
    # value skulls on it. Sits on the FACE, clear below the arc ring.
    band_y = head_c[1] - int(hr * 0.74)
    band_hw = int(hr * 0.84)
    band_h = int(hr * 0.24)
    band_box = [(head_c[0] - band_hw, band_y - band_h // 2),
                (head_c[0] + band_hw, band_y - band_h // 2),
                (head_c[0] + int(band_hw * 0.94), band_y + band_h // 2),
                (head_c[0] - int(band_hw * 0.94), band_y + band_h // 2)]
    triad_blob(surf, SAFF, band_box,
               core_pts=[(head_c[0], band_y), (head_c[0] + band_hw, band_y - band_h // 2 + int(1 * s)),
                         (head_c[0] + int(band_hw * 0.94), band_y + band_h // 2), (head_c[0], band_y + band_h // 2)],
               sheen_pts=[(head_c[0] - band_hw, band_y - band_h // 2),
                          (head_c[0], band_y - band_h // 2),
                          (head_c[0], band_y - int(band_h * 0.18)),
                          (head_c[0] - band_hw, band_y - int(band_h * 0.18))],
               ow=max(1, int(1.6 * s)))
    # a thin seed-brown bead-rail along the band's lower lip (ties to the mala)
    pygame.draw.line(surf, SEED_D, (head_c[0] - int(band_hw * 0.92), band_y + int(band_h * 0.42)),
                     (head_c[0] + int(band_hw * 0.92), band_y + int(band_h * 0.42)), max(1, int(1.8 * s)))
    # 3 low tiara skulls riding ON the band (dim crown tier), evenly spaced
    tiara_skull_r = int(hr * 0.20)
    for k in (-1, 0, 1):
        sx = head_c[0] + int(k * band_hw * 0.62)
        tiara_skull(surf, sx, band_y - int(hr * 0.02), tiara_skull_r, s, lit=False)


# ── the matted-hair JATA topknot (the DOMINANT 32px silhouette carrier) ───────
HAIR   = ( 50,  38,  36)   # near-ink matted-hair brown (the dark mass body)
HAIR_C = ( 34,  26,  26)   # deepest matted-coil shadow (groove cores)
HAIR_H = ( 92,  68,  58)   # the dressed-lock highlight (still dark)


def _coil_lobe(surf, cx, cy, rx, ry, rot, fill, edge_ink=True, ow=2):
    """One ordered dreadlock COIL drawn as a tilted egg lobe — a clean curved
    bulge, the unit of the sculpted ascetic bun (NOT a scribbled line)."""
    pts = []
    for i in range(16):
        a = (i / 16) * 2 * math.pi
        x = math.cos(a) * rx
        y = math.sin(a) * ry
        px = cx + x * math.cos(rot) - y * math.sin(rot)
        py = cy + x * math.sin(rot) + y * math.cos(rot)
        pts.append((px, py))
    if edge_ink:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, fill, pts)
    if edge_ink:
        pygame.draw.polygon(surf, INK, pts, ow)


def draw_jata(surf, cx, cy, hr, s):
    """A BIG lumpy dark matted-hair JATA piled above the head — the DOMINANT top
    silhouette. WHY doubled + raised into a single coiled dome: it must be the
    tallest, darkest shape in the 32px blackout (the gameplay carrier nothing
    else owns). Built from 5 ORDERED grouped dreadlock coils swirling up into a
    piled ascetic bun (consistent clockwise direction — a coiled jatamukuta, not
    a mop), bound by a saffron tie. Near-ink value so it never out-values the
    crown skulls drawn in front of it."""
    # one big rounded under-mass first — the dome body the coils ride on, so the
    # blackout reads as ONE lumpy cap, not separate strands.
    dome_c = (cx, cy - int(hr * 0.78))
    dome = []
    dn = 22
    rng = 9173
    for i in range(dn):
        a = math.pi + (i / (dn - 1)) * math.pi   # upper hemisphere arc, wide
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        bump = 0.10 * math.cos(a * 4) + (rng / 0x7FFFFFFF - 0.5) * 0.10
        rx = hr * (1.34 + bump)
        ry = hr * (1.18 + bump)
        dome.append((dome_c[0] + math.cos(a) * rx, dome_c[1] + math.sin(a) * ry))
    # close the dome across a flat-ish base just above the crown line
    dome.append((dome_c[0] + int(hr * 0.96), cy + int(hr * 0.10)))
    dome.append((dome_c[0] - int(hr * 0.96), cy + int(hr * 0.10)))
    pygame.draw.polygon(surf, INK, dome)
    pygame.draw.polygon(surf, HAIR, dome)

    # the 5 ordered coils that sculpt the dome into a swirled bun. Each is a
    # tilted lobe ink-edged against its neighbour so the grouped dreadlocks read
    # as separate wound coils (not a smooth blob); tilts step consistently up
    # into the apex so the whole reads as one coiled ascetic bun.
    coils = [
        (-0.66, hr * 0.20, hr * 0.46, hr * 0.62, -0.62),
        (-0.34, hr * 0.46, hr * 0.50, hr * 0.66, -0.30),
        ( 0.00, hr * 0.56, hr * 0.54, hr * 0.70,  0.0),
        ( 0.34, hr * 0.46, hr * 0.50, hr * 0.66,  0.30),
        ( 0.66, hr * 0.20, hr * 0.46, hr * 0.62,  0.62),
    ]
    for fx, rise, rx, ry, rot in coils:
        lx = cx + fx * hr * 1.02
        ly = dome_c[1] + hr * 0.30 - rise
        # ink-edge each coil first (heavier than the fill outline) so adjacent
        # coils stay visually separated even at HERO scale
        _coil_lobe(surf, lx, ly, rx, ry, rot, HAIR, ow=max(2, int(2.6 * s)))
        # a curved inner groove + a dark crescent giving each coil its rope read
        gx0 = lx - math.sin(rot) * ry * 0.55
        gy0 = ly + math.cos(rot) * ry * 0.55
        gx1 = lx + math.sin(rot) * ry * 0.55
        gy1 = ly - math.cos(rot) * ry * 0.55
        pygame.draw.line(surf, HAIR_C, (gx0, gy0), (gx1, gy1), max(1, int(2.4 * s)))
        pygame.draw.line(surf, HAIR_H, (gx0 + int(2 * s), gy0), (gx1 + int(2 * s), gy1),
                         max(1, int(1.4 * s)))

    # the piled top-KNOT crowning the dome — a tight lumpy coil at the apex
    knot_c = (cx, cy - int(hr * 1.34))
    knot = []
    kpts = 15
    rng = 7777
    for i in range(kpts):
        a = (i / kpts) * 2 * math.pi
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        rr = hr * (0.62 + 0.12 * math.cos(a * 3) + (rng / 0x7FFFFFFF - 0.5) * 0.12)
        knot.append((knot_c[0] + math.cos(a) * rr, knot_c[1] + math.sin(a) * rr * 0.94))
    pygame.draw.polygon(surf, INK, knot)
    pygame.draw.polygon(surf, HAIR, knot)
    # a spiral groove on the knot (ordered swirl, the wound-coil tell)
    for k in range(3):
        rr = hr * (0.50 - k * 0.16)
        pygame.draw.arc(surf, HAIR_C,
                        (knot_c[0] - rr, knot_c[1] - rr * 0.94, rr * 2, rr * 1.88),
                        0.4 + k, 3.2 + k, max(1, int(1.6 * s)))
    pygame.draw.polygon(surf, INK, knot, max(1, int(1.4 * s)))

    # the saffron tie binding the bun to the dome (the one ascetic colour up top)
    tie_y = cy - int(hr * 1.06)
    pygame.draw.line(surf, INK, (cx - int(hr * 0.46), tie_y),
                     (cx + int(hr * 0.46), tie_y), max(3, int(4.6 * s)))
    pygame.draw.line(surf, SAFF, (cx - int(hr * 0.42), tie_y),
                     (cx + int(hr * 0.42), tie_y), max(2, int(3.0 * s)))
    pygame.draw.line(surf, SAFF_BR, (cx - int(hr * 0.34), tie_y - int(1 * s)),
                     (cx + int(hr * 0.06), tie_y - int(1 * s)), max(1, int(1.4 * s)))


# ── the alms-staff (ash + seed-bead khatvanga) → pillar mirror ────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The ash-and-seed alms-staff IS the pillar: a banded ash shaft strung with
    the rudraksha U-swag motif = the tileable shaft; a single saffron-lit skull
    capped by the enlarged JATA-DOME (echoing the new hero silhouette) = the gap-
    edge cap — the sister's own forms, mirrored on-axis, never top-heavy. `cap`
    names the END that faces the GAP."""
    shaft_w = int(13 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(30 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    while y <= b1:
        bw = shaft_w
        band = [(cx - bw, y - int(10 * s)),
                (cx + bw, y - int(10 * s)),
                (cx + bw, y + int(10 * s)),
                (cx - bw, y + int(10 * s))]
        triad_blob(surf, ASH, band,
                   core_pts=[(cx, y - int(9 * s)), (cx + bw, y - int(9 * s)),
                             (cx + bw, y + int(9 * s)), (cx, y + int(9 * s))],
                   sheen_pts=[(cx - bw, y - int(9 * s)), (cx - int(bw * 0.3), y - int(9 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        # an ash-smear groove across the band (the vibhuti tell on the shaft)
        pygame.draw.line(surf, SMEAR, (cx - bw, y - int(4 * s)),
                         (cx + bw, y - int(4 * s)), max(1, int(2.0 * s)))
        # a single fat seed-swag slung across the band (the mala motif tiled)
        seed_swag(surf, cx, y - int(2 * s), int(bw * 0.92), int(11 * s),
                  int(3.6 * s), s, n=7)
        y += band_pitch

    # === gap-edge cap: a saffron-lit ash skull capped by the enlarged JATA-DOME =
    # WHY the dome (not a knot): the cap must echo the new hero's dominant top
    # silhouette — a lumpy dark mound + bun — so the staff reads as HER staff.
    cap_y = (bot - int(24 * s)) if cap == "bottom" else (top + int(24 * s))
    cap_skull_r = int(13 * s)
    sky_dir = 1 if cap == "top" else -1   # the jata piles toward the figure body
    dome_c = (cx, cap_y + sky_dir * int(cap_skull_r * 1.5))
    # the lumpy dome under-mass
    dm = []
    rng = 4242
    dn = 16
    for i in range(dn):
        a = math.pi + (i / (dn - 1)) * math.pi
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        bump = 0.12 * math.cos(a * 4) + (rng / 0x7FFFFFFF - 0.5) * 0.10
        rx = cap_skull_r * (1.18 + bump)
        ry = cap_skull_r * (1.0 + bump)
        dm.append((dome_c[0] + math.cos(a) * rx, dome_c[1] + sky_dir * math.sin(a) * ry))
    dm.append((dome_c[0] + int(cap_skull_r * 0.9), cap_y))
    dm.append((dome_c[0] - int(cap_skull_r * 0.9), cap_y))
    pygame.draw.polygon(surf, INK, dm)
    pygame.draw.polygon(surf, HAIR, dm)
    # 3 ordered coil lobes + the apex bun (the same sculpted-bun grammar as hero)
    for fx, rot in ((-0.5, -0.4), (0.0, 0.0), (0.5, 0.4)):
        lx = dome_c[0] + int(fx * cap_skull_r * 1.3)
        ly = dome_c[1] + sky_dir * int(cap_skull_r * 0.35)
        _coil_lobe(surf, lx, ly, cap_skull_r * 0.55, cap_skull_r * 0.46, rot,
                   HAIR, ow=max(1, int(1.2 * s)))
    bun_y = dome_c[1] + sky_dir * int(cap_skull_r * 1.05)
    pygame.draw.circle(surf, INK, (cx, bun_y), int(cap_skull_r * 0.5))
    pygame.draw.circle(surf, HAIR, (cx, bun_y), int(cap_skull_r * 0.44))
    # saffron tie binding the bun (the ascetic colour note, mirrored from hero)
    tie_y = dome_c[1] + sky_dir * int(cap_skull_r * 0.7)
    pygame.draw.line(surf, SAFF, (cx - int(cap_skull_r * 0.6), tie_y),
                     (cx + int(cap_skull_r * 0.6), tie_y), max(2, int(2.6 * s)))
    crown_skull(surf, cx, cap_y, cap_skull_r, s, lit=True)
    # a saffron collar where the cap meets the shaft
    collar_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, SAFF, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, SAFF_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))


# ── render pipeline ───────────────────────────────────────────────────────────
SS = 8


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_bhasma_yogini(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def font(size):
    return pygame.font.Font(FONT_PATH, size)


def render_hero():
    """Standalone hi-res hero (~1024px tall) — the brood-II hero pipeline."""
    HW, HH = 760, 1024
    surf = pygame.Surface((HW, HH))
    vgrad(surf, (0, 0, HW, HH), (70, 66, 72), (44, 42, 48))
    hero = render_creature_chip(620, 880, 310, 470, 3.0)
    surf.blit(hero, ((HW - 620) // 2, 70))
    f = font(26)
    surf.blit(f.render("#4 — BHASMA-YOGINI", True, LABEL), (30, 24))
    fs = font(16)
    surf.blit(fs.render("ash-ascetic seed-bead mother  ·  MUKHA body  ·  SS=8 hero", True, LABEL_DIM),
              (30, 60))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_7_hero.png")
    pygame.image.save(surf, out)
    return out


def main():
    W, H = 1010, 860
    font_big = font(30)
    f = font(17)
    f_sm = font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("#4 — BHASMA-YOGINI", True, LABEL), (24, 13))
    sheet.blit(f_sm.render(
        "ash-ascetic seed-bead mother  ·  MUKHA body · six-arm fan · 6 distinct ascetic palm-skulls · rudraksha U-swag · jata topknot · round 7",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 500, 178, 256, 1.62)
    sheet.blit(hero, (14, 84))
    sheet.blit(f.render("Creature — hero", True, LABEL), (110, 588))
    sheet.blit(f_sm.render("DOMINANT jata dome crests above the arc (the dark 32px carrier). Six palm-skulls = mid tier, each a distinct ascetic relic.", True, LABEL_DIM), (14, 612))
    sheet.blit(f_sm.render("Fused crown: 5-skull arc-sweep + explicit horizontal tiara-BAND frontmost; jata behind/above both.", True, LABEL_DIM), (14, 628))
    sheet.blit(f_sm.render("Tripundra brow + ash-band torso + saffron waist-wrap = never naked. 6-petal lotus base.", True, LABEL_DIM), (14, 644))
    sheet.blit(f_sm.render("Rudraksha mala = ONE fat knobbly warmer-brown U-swag. Saffron-amber third-eye = brightest.", True, LABEL_DIM), (14, 660))

    # === (b) PILLAR assembled — mirrored ======================================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 84))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 84 + 250 + 96))
    pygame.draw.rect(sheet, (58, 56, 62), (pcx + 8, 84 + 250, 134, 96))
    sheet.blit(f_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 84 + 250 + 40))
    sheet.blit(f.render("Pillar — alms-staff", True, LABEL), (pcx - 4, 688))
    sheet.blit(f_sm.render("banded ash shaft strung with the rudraksha", True, LABEL_DIM), (pcx - 4, 712))
    sheet.blit(f_sm.render("U-swag = shaft; saffron-lit skull + small", True, LABEL_DIM), (pcx - 4, 728))
    sheet.blit(f_sm.render("jata-knot caps the gap (mirrored top<->bottom)", True, LABEL_DIM), (pcx - 4, 744))

    # === (c) TRUE 32px DAY + NIGHT chips + blackout proof ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 84, W - panel_x - 14, 580))
    sheet.blit(f.render("True 32px gameplay chip", True, LABEL), (panel_x + 16, 94))

    def chip32():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_bhasma_yogini(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 124
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, day_y + 20))
    sheet.blit(f_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, night_y + 20))
    sheet.blit(f_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout / silhouette proof — the read at pure-mask scale (jata carrier)
    def blackout():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_bhasma_yogini(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        mask = pygame.mask.from_surface(small)
        sil = mask.to_surface(setcolor=(20, 18, 22, 255), unsetcolor=(0, 0, 0, 0))
        return sil

    px2 = panel_x + 192
    pygame.draw.rect(sheet, (224, 224, 226), (px2, day_y, 130, 150))
    pygame.draw.rect(sheet, INK, (px2, day_y, 130, 150), 1)
    sheet.blit(blackout(), (px2 + 10, day_y + 20))
    sheet.blit(f_sm.render("blackout", True, LABEL_DIM), (px2 + 2, day_y - 16))
    sheet.blit(f_sm.render("(jata + fan", True, LABEL_DIM), (px2, day_y + 156))
    sheet.blit(f_sm.render(" silhouette)", True, LABEL_DIM), (px2, day_y + 170))

    # 32px pillar gap-cap on both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    vgrad(sheet, (px2 + 36, night_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2 + 36, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 42, night_y + 10))
    sheet.blit(f_sm.render("pillar 32px", True, LABEL_DIM), (px2 + 32, night_y - 16))

    # palette strip
    sheet.blit(f.render("Pinned palette", True, LABEL), (panel_x + 16, 524))
    swatches = [
        (ASH, "ash-grey bone"), (CROWN_ASH, "crown ash (dim)"),
        (SMEAR, "ash-smear"), (SAFF, "saffron robe"),
        (SEED, "seed-brown (warm)"), (HAIR, "jata hair"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 552
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(f_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 810, W - 28, 42))
    sheet.blit(f_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 824))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_7.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    hero_path = render_hero()
    print("wrote", hero_path)
    main()
