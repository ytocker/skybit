"""
Round-1 concept renderer for VAJRA-RAKTA — the wrathful blood-scarf adept,
sister #2 of the mukha_citipati_court brood. Headless Pygame; ELEVATED pipeline
(SS=8 supersample -> smoothscale) so the brocade silk + six-arm fan + six
palm-skulls stay crisp at downscale. Keeps the shipped house grammar: flat
saturated fills, hard 1-2px ink keyline (28,22,26), dark-core -> flat-fill ->
top-left rim-sheen triad, 1px alpha-grown outline, chibi proportions,
scary-CUTE; procedural-only (no gradients/PNGs).

WHY this sister is the FABRIC-AS-MASS answer to the "naked" rejection: where
asthi wraps bone in bead-lattice, Vajra-Rakta drapes the CITIPATI dancing
rib-barrel in billowing brocade vajra-silk — crossed sashes printed with a gold
visvavajra (double-dorje crossed-vajra) lattice, a waist wrap, and tassels that
flare PAST the six-arm fan. Gestural silk, never fiddle: the cloth IS the
non-naked device, so the dense detail is the woven mass and a regular gold print
rather than a hundred little hung trinkets. An OPEN flame-halo + a tall 5-skull
crown fused with the Mukha tiara-band say, unmistakably, the FIERCE sister.

WHY the two-scale ornament: at HERO the sash carries the full visvavajra gold
brocade; at true 32px that print would mush, so it COLLAPSES to a sparse regular
gold-dot lattice on the cinnabar silk. The silk MASS is the element that carries
the gameplay silhouette at 32px (a fierce wedge of cinnabar drapery flaring past
the fan), the gold dots merely keeping the woven read alive.

WHY the flame-ring stays OPEN: the six-arm fan needs a clean wedge of open sky
above the crown, so the ember ring is drawn as separated tongues across the TOP
arc only, never closing behind the head into a fire-field that would erase the
crown (the cross-set / AD ruling baked into the brief).

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers cloned from
the Citipati + Mukha-Devi references, not runtime sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

# FONT — five `..` up from this sister dir reaches the repo root, then game/assets.
FONT_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "..", "game", "assets", "LiberationSans-Bold.ttf"))

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Cinnabar SILK is the dominant ornament mass (the fabric carries the figure);
# warm-ivory bone is the body under it; saffron-gold is the brocade print +
# trim; turquoise is a literal sliver. Violet third-eye = the single focal.
BONE      = (244, 234, 208)   # warm-ivory bone (the body the silk drapes)
BONE_D    = (188, 170, 136)   # bone dark-core
BONE_DD   = (138, 120,  92)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (255, 249, 232)   # bone top-left rim-sheen
CINNABAR  = (196,  44,  38)   # cinnabar silk — the dominant ornament MASS
CINNA_D   = (138,  28,  26)   # silk shade / fold-shadow
CINNA_DD  = ( 96,  20,  20)   # deepest fold core
CINNA_BR  = (226,  92,  66)   # silk top-light fold
CINNA_32  = (220,  62,  52)   # silk base brightened ~12% for the true-32px read
CINNA_RIM = (236, 110,  82)   # 1px warm rim on the 32px silk outer edge
SAFFRON   = (236, 176,  64)   # saffron-gold brocade print + tassel + trim
SAFFRON_BR= (250, 214, 120)
SAFFRON_D = (176, 124,  44)
EMBER     = (250, 138,  46)   # ember-orange — the OPEN flame-halo only
EMBER_BR  = (255, 212, 118)
EMBER_HOT = (255, 240, 178)   # hottest flame core (lightest)
TURQ      = ( 64, 178, 170)   # turquoise sliver — sash core-thread + brow bead
TURQ_BR   = (140, 222, 214)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (150,  92, 214)   # violet third-eye slit (the single focal)
THIRD_BR  = (206, 168, 255)

BG        = ( 92,  90,  98)   # neutral grey review backdrop
PANEL     = ( 72,  70,  82)
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


# ── two-segment bone limb (cloned from Citipati) ──────────────────────────────
def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
    """Two-segment ivory bone limb with ink keyline + bulbous joint."""
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


# ── a single ornamental crown-skull (cloned from Citipati) ────────────────────
def crown_skull(surf, cx, cy, r, s, lit=False, glow=False, cracked=False, idx=0):
    """Tiny ivory skull — domed cranium, two dark sockets, a stub jaw. `lit`
    swaps the eye-pins to hot ember for the crown-centre; `glow` adds the single
    permitted crown bloom behind the centre skull. `idx` selects a DISTINCT
    war-trophy specimen so the 5-skull arc reads as five battle-skulls gathered
    off a field, not one dome stamped five times.

    WHY silhouette-altering damage (not interior lines): the crown skulls live
    at ~32px in-game, where any hairline crack mushes away — so the per-`idx`
    war-marks CUT THE OUTLINE itself (a sheared jaw corner, a caved-temple dent,
    a missing-tooth gap, a chopped tooth bar) and VARY THE CRANIUM PROPORTION
    (tall-narrow / squat-wide), giving each lump of the halo-arc its own
    distinct profile. Interior gash/suture detail is hero-only flavour layered
    on top. The crown stays the DIMMEST tier — flat BONE-cream, no brightness
    bump, no per-skull gem — so the focal violet third-eye keeps the single
    brightest pixel and only the centre skull carries the one permitted glow.

    PER-`idx` SPEC (silhouette-altering marks flagged ◆):
      0  tall-narrow,  CLEAN — but lit eyes + the sole crown glow (centre)
      1  squat-wide,   ◆ sheared-off LEFT jaw corner (asymmetric mandible)
      2  base dome,    ◆ caved RIGHT temple (concave dome dent + shadow wedge)
      3  tall-narrow,  ◆ chipped/missing teeth (gap in the tooth bar)
      4  squat-wide,   ◆ scored gash + ◆ missing front tooth (gash is hero flavour)
    """
    # cranium proportion per specimen — ≥2 depart from the base round dome so the
    # arc isn't one stamp (tall-narrow domes rise, squat-wide domes hunker).
    PROP = {0: (0.86, 1.10), 1: (1.12, 0.82), 2: (1.0, 1.0),
            3: (0.84, 1.12), 4: (1.14, 0.80)}
    wf, hf = PROP.get(idx, (1.0, 1.0))
    crw, crh = int(r * wf), int(r * hf)
    if glow:
        for gr, ga in ((int(r * 2.0), 26), (int(r * 1.5), 46), (int(r * 1.1), 74)):
            g = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
            pygame.draw.circle(g, EMBER_BR + (ga,), (gr, gr), gr)
            surf.blit(g, (cx - gr, cy - gr))

    # the cranium dome — an ELLIPSE per proportion so tall/squat read in silhouette.
    dome_box = (cx - crw, cy - crh, crw * 2, crh * 2)
    pygame.draw.ellipse(surf, INK, (dome_box[0] - max(1, int(1.6 * s)),
                                    dome_box[1] - max(1, int(1.6 * s)),
                                    dome_box[2] + max(2, int(3.2 * s)),
                                    dome_box[3] + max(2, int(3.2 * s))))
    pygame.draw.ellipse(surf, BONE, dome_box)
    pygame.draw.ellipse(surf, INK, dome_box, max(1, int(1.6 * s)))
    # idx 2 — CAVED RIGHT TEMPLE: bite a concave dent out of the dome outline so
    # the silhouette is visibly dished on one side, plus an interior shadow wedge.
    if idx == 2:
        dx = cx + int(crw * 0.74)
        dent = [(dx, cy - int(crh * 0.34)), (cx + int(crw * 0.30), cy - int(crh * 0.06)),
                (dx, cy + int(crh * 0.18))]
        pygame.draw.polygon(surf, INK, dent)               # the bitten-out dent (silhouette)
        pygame.draw.polygon(surf, BONE_DD,                 # shadow wedge inside the cave
                            [(cx + int(crw * 0.28), cy - int(crh * 0.10)),
                             (cx + int(crw * 0.58), cy - int(crh * 0.02)),
                             (cx + int(crw * 0.30), cy + int(crh * 0.20))])

    # JAW — per-idx mandible. idx 1 SHEARS the left foot off (asymmetric outline).
    if idx == 1:
        jaw = [(cx - int(crw * 0.52), cy + int(crh * 0.52)),
               (cx + int(crw * 0.52), cy + int(crh * 0.52)),
               (cx + int(crw * 0.34), cy + int(crh * 1.0)),
               (cx - int(crw * 0.10), cy + int(crh * 0.86))]   # left corner sheared away
    else:
        jaw = [(cx - int(crw * 0.52), cy + int(crh * 0.52)),
               (cx + int(crw * 0.52), cy + int(crh * 0.52)),
               (cx + int(crw * 0.34), cy + int(crh * 1.0)),
               (cx - int(crw * 0.34), cy + int(crh * 1.0))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.2 * s)))

    eye_c = EMBER_HOT if lit else INK
    for ex in (cx - int(crw * 0.38), cx + int(crw * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(crh * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(crh * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(crh * 0.42)), max(1, int(r * 0.13)))

    # TOOTH BAR — a clean line, except idx 3/4 cut GAPS into it (missing teeth)
    # so the bite reads broken even at 32px. idx 3 loses two; idx 4 loses the front.
    tb_l, tb_r = cx - int(crw * 0.34), cx + int(crw * 0.34)
    tb_y = cy + int(crh * 0.70)
    gaps = {3: (-1, 1), 4: (0,)}.get(idx, ())
    seg = (tb_r - tb_l) / 5.0
    for t in range(5):
        if (t - 2) in gaps:
            continue                                       # a knocked-out tooth gap
        x0 = int(tb_l + t * seg + seg * 0.12)
        x1 = int(tb_l + (t + 1) * seg - seg * 0.12)
        pygame.draw.line(surf, INK, (x0, tb_y), (x1, tb_y), max(1, int(1.2 * s)))

    # idx 4 — SCORED GASH crown-to-cheek (hero-only interior flavour over the
    # already-broken bite); a thin bone-dark score that mushes harmlessly at 32px.
    if idx == 4:
        pygame.draw.lines(surf, BONE_D, False,
                          [(cx - int(crw * 0.30), cy - int(crh * 0.50)),
                           (cx - int(crw * 0.02), cy - int(crh * 0.18)),
                           (cx - int(crw * 0.14), cy + int(crh * 0.12))],
                          max(1, int(1.0 * s)))
    if cracked:
        # legacy faint war echo — kept for the cap-skull caller's default path
        pygame.draw.lines(surf, BONE_D, False,
                          [(cx - int(crw * 0.30), cy - int(crh * 0.52)),
                           (cx - int(crw * 0.04), cy - int(crh * 0.28)),
                           (cx - int(crw * 0.14), cy - int(crh * 0.04))],
                          max(1, int(1.0 * s)))


# ── a tiny palm-skull cradled in an open hand (the brood motif) ───────────────
def palm_skull(surf, hx, hy, r, s, variant=0):
    """An OPEN palm cradling a TINY ivory skull — the locked brood motif that
    replaces Mukha's relic-discs. WHY a thin five-tick palm fan UNDER a slightly
    brighter skull: the value ladder wants the palm-skulls MID — dimmer than the
    third-eye, brighter than the crown — so the skull cradle reads as the second
    tier of bone at 32px without competing with the focal violet eye.

    WHY the war-trophy spec table: this is the wrathful thunderbolt sister, so her
    six skulls are BATTLE-SCARRED trophies, not a stamped print of one relic. Each
    `variant` selects a DISTINCT specimen — different cranium shape, jaw set, and a
    unique war-mark (missing tooth / diagonal fracture / sheared jaw corner / caved
    temple / scored gash / one clean intact) — so the brood reads as six skulls
    gathered off a battlefield. WHY a DIM violet gem on three of them (a third-eye
    dot on idx 1+4, a violet-lit socket on idx 5): the thunderbolt sister marks her
    war-trophies with a vajra spark, but they are kept DIM (no white core, low
    THIRD_EYE→bone blend) so the head's focal violet third-eye stays the single
    brightest pixel and the value ladder is unchanged."""
    # open palm — a small bone cup with five spread finger-ticks beneath the skull
    cup = [(hx - int(r * 1.05), hy + int(r * 0.30)),
           (hx + int(r * 1.05), hy + int(r * 0.30)),
           (hx + int(r * 0.70), hy + int(r * 1.05)),
           (hx - int(r * 0.70), hy + int(r * 1.05))]
    triad_blob(surf, BONE, cup, ow=max(1, int(1.1 * s)))
    for k in range(-2, 3):
        a = math.radians(-90 + k * 22)
        ex = hx + math.cos(a) * r * 1.5
        ey = (hy - int(r * 0.10)) + math.sin(a) * r * 1.5
        pygame.draw.line(surf, INK, (hx, hy + int(r * 0.2)), (ex, ey), max(2, int(2.4 * s)))
        pygame.draw.line(surf, BONE, (hx, hy + int(r * 0.2)), (ex, ey), max(1, int(1.4 * s)))

    # PER-SKULL WAR-TROPHY SPEC — six DISTINCT specimens keyed off `variant`. Each
    # row sets cranium WIDTH/HEIGHT factor, lean, jaw set + style, and which unique
    # war-mark + (dim) violet gem this skull carries. The dim violet stays well
    # below the focal so the head keeps the single brightest pixel.
    #   wf/hf : cranium width/height factor   lean : crown tilt   jw : jaw shift
    #   jaw_style : "full"|"chipped"|"gap"|"sheared"   mark : the war-scar
    #   gem : None|"brow"|"socket" (dim violet vajra-spark)
    spec = [
        # idx 0 — CLEAN INTACT war-veteran: broad steady cranium, full bite
        dict(wf=0.84, hf=0.78, lean=-0.04, jw=0.0,  jaw_style="full",
             mark=None, gem=None),
        # idx 1 — CHIPPED TEETH + dim violet BROW dot: narrow tall skull, slight tilt
        dict(wf=0.72, hf=0.86, lean=0.05,  jw=0.03, jaw_style="chipped",
             mark="gash_brow", gem="brow"),
        # idx 2 — DEEP DIAGONAL FRACTURE across the parietal: wide low dome
        dict(wf=0.90, hf=0.70, lean=-0.06, jw=-0.04, jaw_style="full",
             mark="fracture", gem=None),
        # idx 3 — SHEARED-OFF JAW CORNER (broke right in battle): squarer cranium
        dict(wf=0.80, hf=0.80, lean=0.02,  jw=0.02, jaw_style="sheared",
             mark=None, gem=None),
        # idx 4 — CAVED TEMPLE (a war-hammer dent) + dim violet BROW dot
        dict(wf=0.86, hf=0.76, lean=-0.03, jw=-0.02, jaw_style="full",
             mark="caved_temple", gem="brow"),
        # idx 5 — SCORED GASH crown-to-cheek + a dim violet-LIT socket: tall narrow
        dict(wf=0.70, hf=0.88, lean=0.06,  jw=0.04, jaw_style="gap",
             mark="scored", gem="socket"),
    ]
    sp = spec[variant % len(spec)]
    wf, hf, lean = sp["wf"], sp["hf"], sp["lean"]
    tilt = int(r * lean)                                 # crown lean per specimen
    jaw_set = int(r * sp["jw"])
    # DIM violet vajra-spark: a low THIRD_EYE→bone blend, no white core, so it sits
    # clearly under the head's focal violet (which gets a full glow + white pixel).
    GEM_DIM = lerp(THIRD_EYE, BONE_D, 0.30)
    GEM_CORE = lerp(THIRD_BR, BONE, 0.40)
    cx, cy = hx, hy - int(r * 0.05)                       # SAME centre & size as round 2

    # the cradled tiny skull — a notch brighter so it reads as the MID tier. The
    # cranium is an ELLIPSE per spec (distinct dome shapes), not one re-tilted dome.
    crw, crh = int(r * wf), int(r * hf)
    sx = cx + tilt
    crown_box = (sx - crw, cy - crh, crw * 2, int(crh * 1.7))
    pygame.draw.ellipse(surf, INK, (crown_box[0] - 1, crown_box[1] - 1,
                                    crown_box[2] + 2, crown_box[3] + 2))
    pygame.draw.ellipse(surf, BONE_SH, crown_box)
    pygame.draw.ellipse(surf, INK, crown_box, max(1, int(1.2 * s)))
    # cranial SUTURE — a dim zig seam from crown apex down between the sockets
    suture = [(sx, cy - int(r * 0.70)),
              (sx + int(r * 0.10), cy - int(r * 0.46)),
              (sx - int(r * 0.08), cy - int(r * 0.24)),
              (sx + int(r * 0.04), cy - int(r * 0.05))]
    pygame.draw.lines(surf, BONE_D, False, suture, max(1, int(1.0 * s)))
    # BROW RIDGE — a dim shaded arc over the sockets to define the orbital bone
    brow_r = int(crw * 0.96)
    brow_box = (sx - brow_r, cy - int(r * 0.30) - brow_r // 2, brow_r * 2, brow_r)
    pygame.draw.arc(surf, BONE_D, brow_box, math.radians(20), math.radians(160),
                    max(1, int(1.6 * s)))
    # TEMPLE / CHEEK hollows — dim recesses just outboard of each socket
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (cx + sgn * int(r * 0.52) + tilt, cy + int(r * 0.16)),
                           max(1, int(r * 0.14)))
    # the two sockets — sunk hollow ring then ink pupil so they read as orbits
    sock = [cx - int(r * 0.32) + tilt, cx + int(r * 0.32) + tilt]
    for si, ex in enumerate(sock):
        pygame.draw.circle(surf, BONE_DD, (ex, cy), max(1, int(r * 0.24)))
        pygame.draw.circle(surf, INK, (ex, cy), max(1, int(r * 0.20)))
    # nasal aperture — a small ink triangle (an inverted-heart cavity, not a dot)
    nay = cy + int(r * 0.22)
    pygame.draw.polygon(surf, INK,
                        [(cx + tilt, cy + int(r * 0.06)),
                         (cx - int(r * 0.10) + tilt, nay),
                         (cx + int(r * 0.10) + tilt, nay)])

    # JAW — per-spec mandible. `sheared` lops the right corner (broke in battle);
    # the bite line carries the per-style tooth damage.
    jl, jr = cx - int(r * 0.40) + jaw_set, cx + int(r * 0.40) + jaw_set
    jt, jb = cy + int(r * 0.40), cy + int(r * 0.74)
    if sp["jaw_style"] == "sheared":
        # the right corner is missing — an angular broken stub instead of a foot
        jaw = [(jl, jt), (jr, jt), (jr, jt + int(r * 0.14)),
               (jr - int(r * 0.30), jb), (jl + int(r * 0.14), jb)]
    else:
        jaw = [(jl, jt), (jr, jt), (jr - int(r * 0.14), jb), (jl + int(r * 0.14), jb)]
    triad_blob(surf, BONE_SH, jaw, ow=max(1, int(1.0 * s)))
    # teeth along the bite line — full set, or with damage per spec
    style = sp["jaw_style"]
    for tx in range(-2, 3):
        if style == "gap" and tx == 0:
            continue                                     # a missing front tooth gap
        if style == "chipped" and tx in (-2, 2):
            th = int(r * 0.09)                           # outer teeth chipped short
        else:
            th = int(r * 0.16)
        ttx = cx + tx * int(r * 0.16) + jaw_set
        pygame.draw.line(surf, BONE_D, (ttx, jt + int(r * 0.02)),
                         (ttx, jt + int(r * 0.02) + th), max(1, int(1.0 * s)))

    # the unique WAR-MARK per specimen
    mark = sp["mark"]
    if mark == "fracture":
        # a DEEP diagonal fracture — a double ink+shade line crossing the parietal
        frac = [(sx - int(r * 0.30), cy - int(r * 0.62)),
                (sx + int(r * 0.06), cy - int(r * 0.30)),
                (sx + int(r * 0.40), cy - int(r * 0.02))]
        pygame.draw.lines(surf, INK, False, frac, max(1, int(1.4 * s)))
        pygame.draw.lines(surf, BONE_DD, False,
                          [(p[0] + int(r * 0.05), p[1]) for p in frac],
                          max(1, int(1.0 * s)))
    elif mark == "caved_temple":
        # a war-hammer dent — a sunk dark lens on the left temple/parietal
        dent_box = (sx - int(r * 0.74), cy - int(r * 0.44),
                    int(r * 0.42), int(r * 0.40))
        pygame.draw.ellipse(surf, BONE_DD, dent_box)
        pygame.draw.arc(surf, INK, dent_box, math.radians(40), math.radians(250),
                        max(1, int(1.2 * s)))
    elif mark == "scored":
        # a long scored gash raking crown-to-cheek (a sword score)
        pygame.draw.line(surf, INK,
                         (sx - int(r * 0.10), cy - int(r * 0.64)),
                         (cx + int(r * 0.34) + tilt, cy + int(r * 0.30)),
                         max(1, int(1.4 * s)))
        pygame.draw.line(surf, BONE_DD,
                         (sx - int(r * 0.04), cy - int(r * 0.60)),
                         (cx + int(r * 0.38) + tilt, cy + int(r * 0.26)),
                         max(1, int(1.0 * s)))
    elif mark == "gash_brow":
        # a short hairline split over the right brow ridge
        pygame.draw.line(surf, BONE_DD,
                         (sx + int(r * 0.16), cy - int(r * 0.40)),
                         (sx + int(r * 0.40), cy - int(r * 0.18)),
                         max(1, int(1.0 * s)))

    # DIM violet vajra-spark gem (only idx 1, 4 = brow dot; idx 5 = lit socket)
    gem = sp["gem"]
    if gem == "brow":
        gy = cy - int(r * 0.40)
        pygame.draw.circle(surf, INK, (sx, gy), max(2, int(r * 0.18)))
        pygame.draw.circle(surf, GEM_DIM, (sx, gy), max(1, int(r * 0.13)))
        pygame.draw.circle(surf, GEM_CORE, (sx, gy), max(1, int(r * 0.06)))
    elif gem == "socket":
        # the right socket glows a DIM violet (no white core) — a vajra-lit relic
        ex = sock[1]
        pygame.draw.circle(surf, GEM_DIM, (ex, cy), max(1, int(r * 0.13)))
        pygame.draw.circle(surf, GEM_CORE, (ex, cy), max(1, int(r * 0.06)))


# ── the OPEN lobed flame-halo RING (cloned from Citipati, top-arc only) ───────
def flame_halo(surf, cx, cy, rad, s, lobes=11, gap_bottom=0.50, angles=None, reach=1.0):
    """A THIN, OPEN lobed ember ring behind the head. Negative-space-first: sky
    shows THROUGH the gap between head and the flame band and BETWEEN the
    separated tongues. WHY top-arc-only here (the brief's hard rule): the ring
    must NOT close behind the crown and kill the open-sky wedge the six-arm fan
    needs, so `gap_bottom` keeps the whole lower arc clear."""
    base_r = rad * 0.84
    tip_r  = rad * (1.06 + 0.30 * reach)
    half_w = (math.pi / lobes) * 0.80
    if angles is None:
        angles = [-math.pi / 2 + (i / lobes) * 2 * math.pi for i in range(lobes)]
    for ang in angles:
        if math.sin(ang) > gap_bottom:
            continue
        a0 = ang - half_w
        a1 = ang + half_w
        base0 = (cx + math.cos(a0) * base_r, cy + math.sin(a0) * base_r)
        base1 = (cx + math.cos(a1) * base_r, cy + math.sin(a1) * base_r)
        tipp  = (cx + math.cos(ang) * tip_r, cy + math.sin(ang) * tip_r)
        kink  = (cx + math.cos(ang + half_w * 0.5) * (base_r + (tip_r - base_r) * 0.55),
                 cy + math.sin(ang + half_w * 0.5) * (base_r + (tip_r - base_r) * 0.55))
        tongue = [base0, kink, tipp, base1]
        pygame.draw.polygon(surf, INK, tongue)
        pygame.draw.polygon(surf, EMBER, tongue)
        mid0 = (base0[0] + (tipp[0] - base0[0]) * 0.50, base0[1] + (tipp[1] - base0[1]) * 0.50)
        mid1 = (base1[0] + (tipp[0] - base1[0]) * 0.50, base1[1] + (tipp[1] - base1[1]) * 0.50)
        pygame.draw.polygon(surf, EMBER_BR, [base0, mid0, tipp, mid1])
        pygame.draw.polygon(surf, EMBER_HOT, [mid0, tipp, mid1])
        pygame.draw.polygon(surf, INK, tongue, max(1, int(1.1 * s)))


# ── the six-arm radial fan (cloned from Mukha-Devi) ───────────────────────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr, arm_len_mul=1.95):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    low-origin, none aimed straight up, so a clean wedge of sky stays open above
    the crown. Returns the six hand centres (sorted) for palm-skull placement."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * arm_len_mul)
    arm_th = int(12 * s)
    spread = [100, 64, 28]   # degrees off the vertical, 3 per side; no vertical arm
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])   # lowest arms first so the upper splay overlaps cleanly
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
        hands.append((sgn, d, hand))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1])) for h in hands]


# ── the tiara-band skull (cloned from Mukha-Devi) ─────────────────────────────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny ivory skull for the Mukha tiara-BAND seated across the brow. The
    fused crown shows BOTH this low brow-band AND the tall Citipati arc-sweep."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    eye_c = SAFFRON_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── the gold visvavajra (crossed-vajra) brocade motif ─────────────────────────
def visvavajra(surf, cx, cy, r, s, dot_only=False):
    """ONE crossed-vajra (double-dorje) print unit: four lotus-mounted vajra-prongs
    radiating to the cardinal directions from a central hub. WHY two-scale: at HERO
    this draws the full gold cross with prong-flares; at true 32px (`dot_only`) it
    collapses to a single saffron dot, so the brocade reads as a SPARSE REGULAR
    GOLD-DOT LATTICE on the silk rather than mushing into noise."""
    if dot_only or r < int(3.0 * s):
        # a fat bright saffron pip so the regular lattice survives the downscale.
        dr = max(2, int(2.6 * s))
        pygame.draw.circle(surf, SAFFRON, (cx, cy), dr)
        pygame.draw.circle(surf, SAFFRON_BR, (cx, cy), max(1, int(dr * 0.5)))
        return
    for k in range(4):
        a = math.radians(45 + k * 90)
        # the shaft of one vajra arm
        tip = (cx + math.cos(a) * r, cy + math.sin(a) * r)
        pygame.draw.line(surf, INK, (cx, cy), tip, max(2, int(2.6 * s)))
        pygame.draw.line(surf, SAFFRON, (cx, cy), tip, max(1, int(1.6 * s)))
        # the splayed three-prong vajra head at the tip
        for j in (-1, 0, 1):
            pa = a + j * 0.34
            pt = (cx + math.cos(pa) * r * 1.18, cy + math.sin(pa) * r * 1.18)
            mid = (cx + math.cos(a) * r * 0.78, cy + math.sin(a) * r * 0.78)
            pygame.draw.line(surf, SAFFRON, mid, pt, max(1, int(1.3 * s)))
    # central hub bead
    triad_circle(surf, SAFFRON_BR, (cx, cy), max(1, int(r * 0.30)),
                 ow=max(1, int(1.0 * s)), core=False, sheen=False)


# ── the wrathful blood-scarf adept ────────────────────────────────────────────
def draw_vajra_rakta(surf, cx, cy, s, scale32=False):
    """CITIPATI dancing rib-barrel torso (tall, cocked hip) draped in billowing
    cinnabar brocade vajra-silk + six-arm radial fan + six palm-skulls + a fused
    tall-5-skull / tiara-band crown under an OPEN flame-ring. The violet third-eye
    is the single brightest pixel. `scale32` swaps the full visvavajra brocade for
    the sparse gold-dot lattice (the two-scale ornament rule).
    `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(30 * s))
    hr = int(26 * s)
    hip_y = cy + int(34 * s)
    hip_cx = cx + int(7 * s)          # hips cocked to the figure's right (the dance)
    rc_cx, rc_cy = cx, cy - int(2 * s)
    rc_w, rc_h = int(34 * s), int(40 * s)

    # === OPEN FLAME-HALO RING (drawn first → behind everything) ================
    # An OPEN ring of distinct ember tongues arcing the crown's outer edge on
    # BOTH sides, explicitly NOT closing across the top (the open-sky wedge the
    # six-arm fan needs is preserved). WHY two angle-bands per side instead of a
    # continuous arc: 2-3 separated licks carried DOWN each flank give the ring a
    # clear "ring of fire" read — pointed tongues with the ink keyline — and the
    # ember orange is hotter than the saffron brocade so it separates by hue+value.
    # The crown skulls sit at ~216..324°; tongues live OUTSIDE that arc to the
    # left (≈150..205°) and right (≈335..390°), leaving the very top (~270°) open.
    # WHY a larger base radius than the crown arc (hr*1.74 + skull_r): the
    # tongues must sit OUTSIDE the outer crown skulls so they read as a halo of
    # fire, not licks tucked behind the bone. Angles hug the upper flanks
    # (~146..210° L, ~330..394° R) and the open top (~270°) stays clear.
    left_degs  = [146, 164, 184, 204, 210]
    right_degs = [394, 376, 356, 336, 330]
    flame_angles = [math.radians(d) for d in left_degs + right_degs]
    flame_halo(surf, head_c[0], head_c[1] - int(hr * 0.06), int(hr * 2.12), s,
               lobes=22, gap_bottom=1.10, angles=flame_angles, reach=1.10)

    # === SIX-ARM RADIAL FAN (behind the torso, low origin) =====================
    hand_pts = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 1.05), s, hr,
                            arm_len_mul=2.05)

    # === BILLOWING VAJRA-SILK SKIRT — a wide BELL of overlapping fold-lobes =====
    # WHY drawn before the body: the cinnabar drapery is the OUTERMOST silhouette
    # mass (the non-naked device), so it bells OUT past the six-arm fan tips and
    # below the hips into a skirt. WHY 3 curved overlapping lobes per side with
    # scalloped trailing edges (not two stiff triangles): real cloth reads as a
    # bell, never a tapering wedge — each lobe is a quadratic-bezier hem that
    # flares wider than the fan, the overlaps + inner fold-shade planes giving it
    # volume rather than a flat flap.
    waist_cx = hip_cx
    waist_y  = hip_y - int(2 * s)
    fan_tip_x = int(56 * s)   # the widest fan reach the skirt must clear

    def qbez(p0, p1, p2, n=10):
        return [(p0[0] + (p1[0] - p0[0]) * 2 * t * (1 - t) + (p2[0] - p0[0]) * t * t,
                 p0[1] + (p1[1] - p0[1]) * 2 * t * (1 - t) + (p2[1] - p0[1]) * t * t)
                for t in (i / n for i in range(n + 1))]

    def skirt_lobe(sgn, spread, drop, fill, fold=False):
        """One curved fabric lobe hanging from the waist: a smooth bezier outer
        hem swinging OUT to `spread` (past the fan) and DOWN to `drop`, returning
        to a scalloped inner hem. `fold` tints it the deeper fold-shade so the
        overlapped inner lobes read as receding volume."""
        outx = waist_cx + sgn * spread
        hemy = waist_y + drop
        # outer hem: waist -> bulge out -> hem tip
        outer = qbez((waist_cx + sgn * int(8 * s), waist_y - int(2 * s)),
                     (waist_cx + sgn * int(spread + 18 * s), waist_y + int(drop * 0.34)),
                     (outx, hemy), n=12)
        # scalloped trailing hem back toward centre (3 little wave dips)
        hem = []
        steps = 6
        for k in range(steps + 1):
            t = k / steps
            hx = outx + (waist_cx - outx) * t
            hy = hemy - int(drop * 0.10 * t) + int(7 * s) * math.sin(t * math.pi * 3)
            hem.append((hx, hy))
        poly = outer + hem + [(waist_cx + sgn * int(4 * s), waist_y)]
        if scale32:
            # brighter base so the bell holds on both day + night chips, with a
            # 1px warm rim on the outer hem so it doesn't bleed into the sky.
            col = CINNA_D if fold else CINNA_32
        else:
            col = CINNA_D if fold else CINNABAR
        triad_blob(surf, col, poly, ow=max(1, int(1.4 * s)))
        if scale32 and not fold:
            pygame.draw.lines(surf, CINNA_RIM, False, outer, max(1, int(1.2 * s)))
        if not fold:
            # an inner fold-shade plane down the lobe centre (volume, not flat)
            fs = qbez((waist_cx + sgn * int(6 * s), waist_y + int(2 * s)),
                      (waist_cx + sgn * int(spread * 0.5 + 8 * s), waist_y + int(drop * 0.4)),
                      (outx - sgn * int(spread * 0.30), hemy - int(2 * s)), n=10)
            fold_poly = fs + [(waist_cx + sgn * int(4 * s), waist_y + int(drop * 0.5))]
            pygame.draw.polygon(surf, CINNA_DD, fold_poly)
            # a top-light fold groove riding the outer bulge (silk sheen)
            pygame.draw.lines(surf, CINNA_BR, False, outer[:8], max(1, int(1.8 * s)))
            # a deep fold groove just inboard of the bulge
            pygame.draw.lines(surf, CINNA_DD, False,
                              qbez((waist_cx + sgn * int(10 * s), waist_y + int(4 * s)),
                                   (waist_cx + sgn * int(spread * 0.6), waist_y + int(drop * 0.42)),
                                   (outx - sgn * int(spread * 0.18), hemy - int(4 * s)), n=8),
                              max(1, int(2.0 * s)))
        return poly

    # back lobes first (deeper fold-shade), then the front bell on top — the
    # overlap is what gives the skirt its rounded mass.
    skirt_polys = []
    for sgn in (-1, 1):
        skirt_lobe(sgn, fan_tip_x - int(6 * s), int(56 * s), CINNA_D, fold=True)   # rear lobe
    for sgn in (-1, 1):
        skirt_polys.append(
            skirt_lobe(sgn, fan_tip_x + int(14 * s), int(68 * s), CINNABAR))       # front bell

    # === GOLD VISVAVAJRA BROCADE on the skirt silk (two-scale) =================
    # full crossed-vajra print at hero; sparse regular gold-dot lattice at 32px.
    def brocade_on(poly_bbox, pitch_mul=1.0):
        x0 = min(p[0] for p in poly_bbox); x1 = max(p[0] for p in poly_bbox)
        y0 = min(p[1] for p in poly_bbox); y1 = max(p[1] for p in poly_bbox)
        if scale32:
            # a DELIBERATE regular grid of a few fat gold dots, NOT a fine
            # staggered print — so the lattice reads as ornament, not noise.
            pitch = max(int(9 * s * pitch_mul), int((x1 - x0) / 3.2))
            stagger = False
        else:
            pitch = int(20 * s * pitch_mul)
            stagger = True
        unit_r = int(6.5 * s)
        row = 0
        y = y0 + pitch // 2
        while y < y1:
            off = (pitch // 2) if (stagger and row % 2) else 0
            x = x0 + pitch // 2 + off
            while x < x1:
                if _point_in_poly((x, y), poly_bbox):
                    visvavajra(surf, x, y, unit_r, s, dot_only=scale32)
                x += pitch
            y += pitch
            row += 1

    for poly in skirt_polys:
        brocade_on(poly)

    # === CROSSED VAJRA-SILK SASHES — two brocade bands X-ing OVER the shoulders =
    # WHY this is DEFERRED to draw AFTER the rib-cage (see the call below the
    # ribcage block): the round-1 failure was a bare rib-barrel + bare shoulders.
    # Two diagonal brocade bands must lie ON TOP of the bone, crossing the chest,
    # passing over the arm-fan origins, and meeting at the waist knot — so the
    # body shows ≤1 bare rib-band between collar and belt and the sternum X reads
    # at 32px as a bright chest mark.
    shoulderL = (rc_cx - int(20 * s), rc_cy - rc_h // 2 - int(1 * s))
    shoulderR = (rc_cx + int(20 * s), rc_cy - rc_h // 2 - int(2 * s))
    sash_w = int(11 * s)
    knot = (waist_cx, waist_y - int(2 * s))

    def chest_band(top, waist):
        dx, dy = waist[0] - top[0], waist[1] - top[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * sash_w / 2, dx / L * sash_w / 2
        return ([(top[0] + nx, top[1] + ny), (waist[0] + nx, waist[1] + ny),
                 (waist[0] - nx, waist[1] - ny), (top[0] - nx, top[1] - ny)],
                (nx, ny))

    def draw_chest_sashes():
        botA = (knot[0] + int(7 * s), knot[1])
        botB = (knot[0] - int(7 * s), knot[1])
        bandA, nA = chest_band(shoulderL, botA)   # \ band
        bandB, nB = chest_band(shoulderR, botB)   # / band

        def one(poly, nrm, top, waist):
            triad_blob(surf, CINNABAR, poly,
                       core_pts=[(poly[0][0] - nrm[0] * 0.4, poly[0][1] - nrm[1] * 0.4),
                                 (poly[1][0] - nrm[0] * 0.4, poly[1][1] - nrm[1] * 0.4),
                                 poly[2], poly[3]],
                       ow=max(1, int(1.4 * s)))
            pygame.draw.line(surf, SAFFRON, top, waist, max(1, int(1.8 * s)))

        # both bands, then their brocade ON TOP — the crossing X reads bright
        one(bandA, nA, shoulderL, botA)
        one(bandB, nB, shoulderR, botB)
        # a small shoulder-pad lump where each sash crests the shoulder
        for (sx, sy) in (shoulderL, shoulderR):
            triad_circle(surf, CINNABAR, (sx, sy), int(7 * s), ow=max(1, int(1.2 * s)),
                         core=False)
        brocade_on(bandA, pitch_mul=0.9)
        brocade_on(bandB, pitch_mul=0.9)
        # a turquoise core-thread sliver runs each sash (the literal sliver, hero)
        if not scale32:
            pygame.draw.line(surf, TURQ, shoulderL, botA, max(1, int(1.4 * s)))
            pygame.draw.line(surf, TURQ, shoulderR, botB, max(1, int(1.4 * s)))

    # === LEGS — wide cocked-hip dance (cloned from Citipati) ===================
    leg_th = int(14 * s)
    hipL = (hip_cx - int(13 * s), hip_y)
    kneeL = (hip_cx - int(20 * s), hip_y + int(26 * s))
    footL = (hip_cx - int(22 * s), hip_y + int(52 * s))
    bone_limb(surf, hipL, kneeL, footL, leg_th, s)
    hipR = (hip_cx + int(11 * s), hip_y)
    kneeR = (hip_cx + int(30 * s), hip_y + int(8 * s))
    footR = (hip_cx + int(20 * s), hip_y + int(34 * s))
    bone_limb(surf, hipR, kneeR, footR, leg_th, s)
    for (fx, fy), sgn in ((footL, -1), (footR, +1)):
        foot = [(fx - int(4 * s), fy - int(2 * s)), (fx + sgn * int(16 * s), fy + int(2 * s)),
                (fx + sgn * int(15 * s), fy + int(10 * s)), (fx - int(5 * s), fy + int(8 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.4 * s)))

    # === PELVIS + RIBCAGE (the Citipati tall rib-barrel) =======================
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

    spine_top_y = cy - int(14 * s)
    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx + int(2 * s), cy + int(6 * s)),
             (cx - int(1 * s), spine_top_y)]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

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
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.4 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(6 * s)), max(1, int(2 * s)))

    # the crossed sashes lie ON the rib-cage (kills the bare-torso zone); the
    # waist wrap below then ties the X at the knot.
    draw_chest_sashes()

    # === WAIST WRAP — a fat cinnabar silk band across the hips =================
    # the brief's waist-wrap: a bold horizontal silk mass that ties the crossed
    # sashes together and carries a gold trim + turquoise core-thread sliver.
    wrap = [(hip_cx - int(24 * s), hip_y - int(8 * s)),
            (hip_cx + int(24 * s), hip_y - int(10 * s)),
            (hip_cx + int(26 * s), hip_y + int(8 * s)),
            (hip_cx - int(26 * s), hip_y + int(10 * s))]
    triad_blob(surf, CINNABAR, wrap,
               core_pts=[(hip_cx - int(4 * s), hip_y - int(7 * s)),
                         (hip_cx + int(24 * s), hip_y - int(8 * s)),
                         (hip_cx + int(24 * s), hip_y + int(7 * s)),
                         (hip_cx - int(4 * s), hip_y + int(8 * s))],
               ow=max(1, int(1.6 * s)))
    # gold trim top + bottom edges (the brocade tie)
    pygame.draw.line(surf, SAFFRON, (hip_cx - int(24 * s), hip_y - int(7 * s)),
                     (hip_cx + int(24 * s), hip_y - int(9 * s)), max(1, int(2 * s)))
    pygame.draw.line(surf, SAFFRON_D, (hip_cx - int(26 * s), hip_y + int(8 * s)),
                     (hip_cx + int(26 * s), hip_y + int(7 * s)), max(1, int(2 * s)))
    # turquoise core-thread sliver running through the wrap (the literal sliver)
    pygame.draw.line(surf, TURQ, (hip_cx - int(23 * s), hip_y + int(1 * s)),
                     (hip_cx + int(24 * s), hip_y - int(1 * s)), max(1, int(2 * s)))
    pygame.draw.line(surf, TURQ_BR, (hip_cx - int(18 * s), hip_y),
                     (hip_cx + int(4 * s), hip_y - int(1 * s)), max(1, int(1 * s)))
    # a couple of gold brocade units on the wrap (collapses with the silk at 32px)
    if not scale32:
        visvavajra(surf, hip_cx - int(12 * s), hip_y, int(5 * s), s)
        visvavajra(surf, hip_cx + int(12 * s), hip_y - int(1 * s), int(5 * s), s)
    else:
        pygame.draw.circle(surf, SAFFRON, (hip_cx - int(12 * s), hip_y), max(1, int(2 * s)))
        pygame.draw.circle(surf, SAFFRON, (hip_cx + int(12 * s), hip_y), max(1, int(2 * s)))

    # === TASSELS — saffron-gold knots dangling from the wrap (the flutter) =====
    for tx, ph in ((hip_cx - int(20 * s), 0), (hip_cx, 1), (hip_cx + int(20 * s), 0)):
        ty = hip_y + int(11 * s)
        triad_circle(surf, SAFFRON, (tx, ty), int(4 * s), ow=max(1, int(1.0 * s)),
                     core=False, sheen=False)
        # a short fringe of saffron threads
        for k in (-1, 0, 1):
            ex = tx + k * int(3 * s)
            pygame.draw.line(surf, SAFFRON_D, (tx, ty + int(3 * s)),
                             (ex, ty + int(13 * s)), max(1, int(1.6 * s)))
            pygame.draw.line(surf, SAFFRON_BR, (tx, ty + int(3 * s)),
                             (ex, ty + int(11 * s)), max(1, int(1.0 * s)))

    # === SIX PALM-SKULLS — one in each open hand (the brood motif) =============
    palm_r = int(9 * s)
    for i, (hx, hy) in enumerate(hand_pts):
        palm_skull(surf, hx, hy, palm_r, s, variant=i)

    # === SKULL HEAD — chibi scary-cute, violet third-eye (the single focal) ====
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two big lower sockets — scary-cute, kept DIMMER than the third-eye
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.06)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.27))
        pygame.draw.circle(surf, CINNA_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.11))
    # THIRD EYE — the single BRIGHTEST pixel: a fat violet slit + hot core + glow.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.38)
    if not scale32:
        for gr, ga in ((int(hr * 0.62), 60), (int(hr * 0.40), 110)):
            g = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
            pygame.draw.circle(g, THIRD_BR + (ga,), (gr, gr), gr)
            surf.blit(g, (tex - gr, tey - gr))
    pygame.draw.ellipse(surf, INK, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, THIRD_EYE, (tex - int(5 * s), tey - int(7 * s), int(10 * s), int(14 * s)))
    pygame.draw.ellipse(surf, THIRD_BR, (tex - int(3 * s), tey - int(4 * s), int(6 * s), int(8 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(1 * s)),
                       max(1, int(2.0 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.24)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.24)),
                         (head_c[0], head_c[1] + int(hr * 0.5))])
    # bared wrathful grin
    my = head_c[1] + int(hr * 0.66)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))
    for sgn in (-1, 1):   # corner fangs (wrathful tell)
        fx = head_c[0] + sgn * int(hr * 0.42)
        pygame.draw.polygon(surf, BONE_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.22))])
    # cinnabar silk brow-scarf wrapped over the temples (the blood-scarf tell)
    for sgn in (-1, 1):
        bx = head_c[0] + sgn * int(hr * 0.96)
        scarf = [(bx - sgn * int(2 * s), head_c[1] - int(hr * 0.2)),
                 (bx + sgn * int(11 * s), head_c[1] - int(hr * 0.4)),
                 (bx + sgn * int(14 * s), head_c[1] + int(hr * 0.1)),
                 (bx + sgn * int(8 * s), head_c[1] + int(hr * 0.4))]
        triad_blob(surf, CINNABAR, scarf, ow=max(1, int(1.2 * s)))
        pygame.draw.line(surf, SAFFRON_BR,
                         (bx + sgn * int(2 * s), head_c[1] - int(hr * 0.12)),
                         (bx + sgn * int(11 * s), head_c[1] - int(hr * 0.34)),
                         max(1, int(1.2 * s)))

    # === FUSED CROWN — tall 5-skull arc-sweep + Mukha tiara-BAND ===============
    # BOTH crown languages present (the locked true-fusion rule):
    #   (1) the LOW Mukha tiara-band seated across the brow, and
    #   (2) the TALL Citipati 5-skull arc sweeping high above it.
    # (1) tiara-band across the brow
    tiara_r = int(hr * 1.04)
    tiara_skull_r = int(hr * 0.26)
    band_pts = []
    for i in range(11):
        a = math.radians(232 + i * (76 / 10))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, SAFFRON, False, band_pts, int(3 * s))
    pygame.draw.lines(surf, SAFFRON_BR, False, band_pts[:6], max(1, int(1.2 * s)))
    # turquoise brow-bead at the band centre (the sliver, mirrored on the crown)
    pygame.draw.circle(surf, TURQ, (head_c[0], head_c[1] - int(tiara_r) + int(2 * s)),
                       max(1, int(2.4 * s)))
    for i in range(3):
        a = math.radians(244 + i * (52 / 2))
        sx = head_c[0] + math.cos(a) * tiara_r
        sy = head_c[1] + math.sin(a) * tiara_r
        tiara_skull(surf, int(sx), int(sy), tiara_skull_r, s, lit=False)
    # (2) the TALL 5-skull arc sweeping high — the fierce-sister crown
    arc_r = int(hr * 1.74)
    skull_r = int(hr * 0.42)
    band2 = []
    for i in range(13):
        a = math.radians(212 + i * (116 / 12))
        band2.append((head_c[0] + math.cos(a) * int(hr * 1.34),
                      head_c[1] + math.sin(a) * int(hr * 1.34)))
    pygame.draw.lines(surf, INK, False, band2, int(6 * s))
    pygame.draw.lines(surf, CINNABAR, False, band2, int(4 * s))   # cinnabar crown band (silk family)
    pygame.draw.lines(surf, CINNA_BR, False, band2[:7], max(1, int(1.4 * s)))
    for i in range(5):
        a = math.radians(216 + i * (108 / 4))
        sx = head_c[0] + math.cos(a) * arc_r
        sy = head_c[1] + math.sin(a) * arc_r
        # each skull is a DISTINCT war-trophy specimen (idx=i): the centre keeps
        # the single permitted crown glow + lit eyes (kept DIMMER than the focal
        # third-eye — the value ladder), the flanks carry silhouette-altering
        # damage (sheared jaw / caved temple / missing teeth) + varied cranium
        # proportions so the halo-arc is five profiles, not one stamp.
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2),
                    glow=(i == 2 and not scale32), idx=i)


# ── point-in-polygon (ray cast) for clipping the brocade to the silk ──────────
def _point_in_poly(p, poly):
    x, y = p
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
            inside = not inside
        j = i
    return inside


# ── the vajra-silk staff → pillar mirror (built from her OWN forms) ───────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The vajra-silk banner-staff IS the pillar, built ONLY from Vajra-Rakta's
    own forms: a cinnabar silk shaft wrapped on a bone rod, printed with the gold
    visvavajra lattice and hung with saffron tassels (the shaft tile); the
    gap-edge cap is a single crown-skull under a small OPEN flame-ring with a
    turquoise brow-bead — her crown in miniature. On-axis, symmetric, not
    top-heavy. `cap` names the END that faces the GAP."""
    shaft_w = int(15 * s)
    pygame.draw.rect(surf, INK, (cx - int(4 * s), top, int(8 * s), bot - top))   # bone rod

    band_pitch = int(22 * s)
    cap_room = int(32 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    idx = 0
    while y <= b1:
        bw = shaft_w
        # a fat cinnabar silk band segment with a SAGGING curved lower hem so the
        # tab reads as draped cloth, not a flat flag (echoes the hero skirt curve).
        sag = int(4 * s)
        band = [(cx - bw, y - int(9 * s)),
                (cx + bw, y - int(9 * s)),
                (cx + bw, y + int(7 * s)),
                (cx + int(bw * 0.5), y + int(9 * s) + sag),
                (cx, y + int(8 * s) + sag),
                (cx - int(bw * 0.5), y + int(9 * s) + sag),
                (cx - bw, y + int(7 * s))]
        triad_blob(surf, CINNABAR, band,
                   core_pts=[(cx, y - int(8 * s)), (cx + bw, y - int(8 * s)),
                             (cx + bw, y + int(6 * s)), (cx, y + int(8 * s) + sag)],
                   sheen_pts=[(cx - bw, y - int(8 * s)), (cx - int(bw * 0.3), y - int(8 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        # the curved lower hem in deep fold-shade (the drape)
        pygame.draw.lines(surf, CINNA_DD, False,
                          [(cx - bw, y + int(7 * s)),
                           (cx - int(bw * 0.5), y + int(9 * s) + sag),
                           (cx, y + int(8 * s) + sag),
                           (cx + int(bw * 0.5), y + int(9 * s) + sag),
                           (cx + bw, y + int(7 * s))], max(1, int(1.8 * s)))
        # gold trim edge + a visvavajra brocade unit centred on the band
        pygame.draw.line(surf, SAFFRON, (cx - bw, y - int(8 * s)),
                         (cx + bw, y - int(8 * s)), max(1, int(1.6 * s)))
        small_pillar = s < 0.5
        visvavajra(surf, cx, y, int(5 * s), s, dot_only=small_pillar)
        # a saffron tassel hung off alternating sides (the silk flutter)
        side = -1 if (idx % 2 == 0) else 1
        tx = cx + side * (bw + int(7 * s))
        triad_circle(surf, SAFFRON, (tx, y + int(2 * s)), int(4 * s),
                     ow=max(1, int(1.0 * s)), core=False, sheen=False)
        pygame.draw.line(surf, SAFFRON_D, (tx, y + int(5 * s)),
                         (tx, y + int(13 * s)), max(1, int(1.6 * s)))
        idx += 1
        y += band_pitch

    # === gap-edge cap: a crown-skull under an OPEN flame-ring + turquoise bead ==
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    cap_skull_r = int(14 * s)
    flame_halo(surf, cx, cap_y - int(cap_skull_r * 0.18), int(cap_skull_r * 1.05), s, lobes=9,
               gap_bottom=0.40)
    # the saffron tiara-band arc behind the cap skull (her fused crown, in mini)
    band_pts = []
    for i in range(9):
        a = math.radians(216 + i * (108 / 8))
        band_pts.append((cx + math.cos(a) * int(cap_skull_r * 1.2),
                         cap_y + math.sin(a) * int(cap_skull_r * 1.2)))
    pygame.draw.lines(surf, INK, False, band_pts, int(5 * s))
    pygame.draw.lines(surf, SAFFRON, False, band_pts, int(2 * s))
    crown_skull(surf, cx, cap_y, cap_skull_r, s, lit=True)
    pygame.draw.circle(surf, TURQ, (cx, cap_y - int(cap_skull_r * 1.2)), max(1, int(2.4 * s)))
    # a gold ferrule collar where the cap meets the shaft
    collar_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(11 * s), collar_y - int(3 * s), int(22 * s), int(7 * s)))
    pygame.draw.rect(surf, SAFFRON, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(5 * s)))
    pygame.draw.rect(surf, SAFFRON_BR, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(2 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale, scale32=False):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_vajra_rakta(big, draw_cx * SS, draw_cy * SS, scale * SS, scale32=scale32)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def font_at(size):
    return pygame.font.Font(FONT_PATH, size)


def export_hero():
    """Standalone hi-res hero PNG, ~1024px tall, SS=8 supersample."""
    HW, HH = 760, 1024
    big = pygame.Surface((HW * SS, HH * SS), pygame.SRCALPHA)
    draw_vajra_rakta(big, (HW // 2) * SS, int(HH * 0.52) * SS, 3.0 * SS)
    hero = pygame.transform.smoothscale(big, (HW, HH))
    hero = grow_outline(hero, INK + (255,), 2)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_7_hero.png")
    pygame.image.save(hero, out)
    return out


def main():
    hero_path = export_hero()

    W, H = 1010, 860
    font_big = font_at(30)
    font = font_at(17)
    font_sm = font_at(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("#2 — VAJRA-RAKTA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "wrathful blood-scarf adept  ·  CITIPATI body · billowing vajra-silk MASS · 6-arm fan + 6 WAR-MARKED palm-skulls · "
        "fused 5-WAR-TROPHY skull arc + tiara-band · OPEN flame-ring · round 7",
        True, LABEL_DIM), (270, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 500, 180, 268, 1.95)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 596))
    sheet.blit(font_sm.render("Cocked-hip DANCE draped in cinnabar brocade vajra-silk that flares PAST the", True, LABEL_DIM), (14, 620))
    sheet.blit(font_sm.render("six-arm fan. Six open palms each cradle a DISTINCT WAR-MARKED trophy skull (3 dim-violet", True, LABEL_DIM), (14, 636))
    sheet.blit(font_sm.render("gems). Fused crown: TALL 5-WAR-TROPHY arc (sheared jaw/caved temple/missing teeth) + tiara-BAND, OPEN flame-ring.", True, LABEL_DIM), (14, 652))
    sheet.blit(font_sm.render("Gold VISVAVAJRA brocade on the silk at hero. Focal VIOLET third-eye = brightest pixel.", True, LABEL_DIM), (14, 668))

    # === (b) PILLAR — mirrored, built from her OWN forms ======================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (58, 56, 66), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — vajra-silk staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("cinnabar silk shaft + gold visvavajra brocade +", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("saffron tassels = tile; crown-skull + OPEN flame-", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("ring + turquoise bead caps the gap (mirrored).", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) RIGHT COLUMN: 32px chips, blackout proof, palette ================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 690))
    sheet.blit(font.render("True 32px gameplay chip", True, LABEL), (panel_x + 16, 96))

    def chip32(outline_col):
        big = pygame.Surface((118 * SS, 118 * SS), pygame.SRCALPHA)
        draw_vajra_rakta(big, 59 * SS, 64 * SS, (32 / 150.0) * SS, scale32=True)
        small = pygame.transform.smoothscale(big, (118, 118))
        return grow_outline(small, outline_col, 1)

    # DAY keeps the ink keyline; NIGHT uses a bone-ivory contour so the dark
    # silk bell + tassels separate from the navy sky (the FIX-5 night read).
    chip_day = chip32(INK + (255,))
    chip_night = chip32(lerp(BONE, INK, 0.18) + (255,))

    day_y = 124
    vgrad(sheet, (panel_x + 18, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 18, day_y, 150, 150), 1)
    sheet.blit(chip_day, (panel_x + 18 + 16, day_y + 16))
    sheet.blit(font_sm.render("32px DAY", True, LABEL), (panel_x + 18, day_y + 154))

    night_y = day_y + 180
    vgrad(sheet, (panel_x + 18, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 18, night_y, 150, 150), 1)
    sheet.blit(chip_night, (panel_x + 18 + 16, night_y + 16))
    sheet.blit(font_sm.render("32px NIGHT", True, LABEL_DIM), (panel_x + 18, night_y + 154))

    # 32px pillar gap-cap chips beside, both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 150 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 148 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 150))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 190
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 0))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 0))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 6, day_y - 16))

    # === BLACKOUT / SILHOUETTE PROOF ==========================================
    blk_y = night_y + 180
    sheet.blit(font.render("Silhouette proof", True, LABEL), (panel_x + 16, blk_y - 22))
    # render the hero into an alpha surface, then stamp its mask solid black on grey
    sil_big = pygame.Surface((118 * SS, 130 * SS), pygame.SRCALPHA)
    draw_vajra_rakta(sil_big, 59 * SS, 70 * SS, (40 / 150.0) * SS)
    sil_small = pygame.transform.smoothscale(sil_big, (118, 130))
    mask = pygame.mask.from_surface(sil_small)
    sil = mask.to_surface(setcolor=(18, 16, 20, 255), unsetcolor=(0, 0, 0, 0))
    pygame.draw.rect(sheet, (170, 168, 176), (panel_x + 18, blk_y, 150, 130))
    pygame.draw.rect(sheet, INK, (panel_x + 18, blk_y, 150, 130), 1)
    sheet.blit(sil, (panel_x + 18 + 16, blk_y))
    sheet.blit(font_sm.render("silk MASS flares past the fan", True, LABEL_DIM),
               (panel_x + 18, blk_y + 132))

    # === PALETTE STRIP ========================================================
    pal_y = blk_y + 158
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, pal_y))
    swatches = [
        (CINNABAR, "cinnabar silk"), (CINNA_D, "silk fold-shade"),
        (SAFFRON, "saffron-gold brocade"), (BONE, "warm-ivory bone"),
        (EMBER, "ember flame-ring"), (TURQ, "turquoise sliver"),
        (THIRD_EYE, "violet third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, pal_y + 24
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 160
        ry = syp + row * 22
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 18, 18))
        pygame.draw.rect(sheet, c, (rx, ry, 16, 16))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 22, ry + 2))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 786, W - 28, 60))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale; standalone hi-res hero exported to round_7_hero.png.",
        True, LABEL_DIM), (26, 794))
    sheet.blit(font_sm.render(
        "Two-scale ornament: full gold VISVAVAJRA brocade at HERO -> SPARSE REGULAR GOLD-DOT lattice at 32px; "
        "the SILK MASS carries the 32px silhouette.", True, LABEL_DIM), (26, 810))
    sheet.blit(font_sm.render(
        "STAY: flat fills · ink keyline (28,22,26) · dark-core->fill->sheen triad · 1px grown outline · chibi scary-cute · "
        "glow only on third-eye + crown-centre skull · procedural-only.", True, LABEL_DIM), (26, 826))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_7.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    print("wrote", hero_path)


if __name__ == "__main__":
    main()
