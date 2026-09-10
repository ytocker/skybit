"""
Round-1 concept renderer for ASTHI-DAKINI — the bone-jewel sky-dancer
(mukha_citipati_court brood, sister #1). Headless Pygame; ELEVATED pipeline
(SS=8 supersample → smoothscale) so the dense multi-strand bead-lattice survives
the downscale. Keeps the shipped house grammar: flat saturated fills, hard 1-2px
ink keyline (28,22,26), dark-core → flat-fill → top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE; procedural-only.

WHY this sister is the bead-jewel dancer: she fuses the CITIPATI body (tall
rib-barrel dancing torso, cocked hip, flamenco-flourish) with the MUKHA six-arm
radial fan — every one of the six open palms cradles a tiny skull. Her non-naked
density is multi-strand bone-BEAD jewelry: a 3-row choker, a long swag necklace,
beaded armlets/bracelets/anklets, wheel earrings, and a bold beaded girdle. A
bead-lattice wraps every surface.

WHY DAWN-LOTUS-COURT reads WARM where her kin read cool: she is the auspicious
sunrise blessing-bringer, so the whole field is pushed warm — a dawn-ivory bone
(~222,204,184) plus a ROSE-GOLD ornament metal (~216,156,118) that covers the
crown band, pips, bezels, earrings and ferrules. That rose-gold is the single
biggest 32px signal that separates her from the cool-gold sisters. A SPARING
LOTUS-PINK (~232,166,182) blush — a third hue no other version uses — ticks the
ornament-marks as a low-third accent only. The #1 tonal-collapse risk is still
low-chroma beads on low-chroma bone reading as a grey smear; the fix is the same
value-step bead chain held by INK keylines + sheen, with the rose-gold pips now
carrying the warm hue separation — value AND hue, colourblind-safe.

WHY the fused crown shows BOTH languages: a plain skull-arc alone reads as the
Citipati reference, so the crown seats the Mukha tiara-BAND across the brow AND
sweeps the wide airy 6-skull arc above it. Crown skulls are a touch darker/cooler
than the warm body so they don't melt into it and still hold against open sky.

Value ladder (AD hard rule): the necklace HERO gem = the single white-hot core →
the brow third-eye gem one step under → the cyan blessing-drops + the lotus-pink
blush stay DIM, below the third-eye → no skull ever gets a white-hot core. The
lotus-pink is a LOW-THIRD accent — never competing with the gems or the rose-gold.

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

# WHY the vendored font over SysFont: review sheets must read identically on the
# headless CI box where no system fonts are guaranteed; the shipped Liberation
# face is always present, five dirs up from the sister folder in game/assets/.
_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "..", "..", "..", "..",
                          "game", "assets", "LiberationSans-Bold.ttf")
_FONT_PATH = os.path.abspath(_FONT_PATH)


def font(sz):
    if os.path.exists(_FONT_PATH):
        return pygame.font.Font(_FONT_PATH, sz)
    return pygame.font.SysFont("DejaVu Sans", sz, bold=True)


# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# WARM, light AGED-BONE field (Citipati-family ivory/chalk), R>=G>=B — reads as
# real bone, not steel. The field is now LIGHT, so the bead lattice can no longer
# rely on light-on-dark; instead the beads sit a value step ABOVE the bone with
# INK keylines + sheen holding the rounded lattice, and the WARM gold spacer-pips
# stay the hue separator (gold-on-ivory reads cleanly). Deep hollows stay dark so
# sockets / rib-gaps still punch.
# DAWN-LOTUS-COURT — this version pushes the whole field WARM so it reads at 32px
# as the sunrise/festive sister versus everyone else's cool ivory. The bone is
# nudged a few points pinker/warmer (R lifted, B dropped) so even the dominant
# field carries the dawn cast; the ornament metal is RE-TUNED from cool gold to
# ROSE-GOLD, which is the single biggest 32px warm signal (the metal covers the
# crown band, pips, bezels, earrings, ferrules).
BONE      = (222, 204, 184)   # warm DAWN-ivory bone (R lifted, B dropped vs cool kin)
BONE_D    = (168, 148, 128)   # bone shade / mid-core (warmed)
BONE_DD   = (100,  86,  74)   # deepest bone hollow (sockets, rib gaps) — stays dark
BONE_SH   = (246, 234, 220)   # bone top-left rim-sheen (warm near-white)
# Beads stay the bright value step above the warm field, but tinted faintly warm
# so they don't read cool against the dawn bone.
BEAD      = (240, 230, 218)   # pale warm bone bead — a value step above the field
BEAD_BR   = (254, 248, 240)   # bead top sheen / hottest bone bead
CYAN      = ( 86, 214, 226)   # icy-cyan — the COOL counterpoint (blessing jewels)
CYAN_BR   = (188, 248, 252)   # hot cyan inner (capped — never a skull's core)
CYAN_D    = ( 40, 132, 150)
# ROSE-GOLD family — warm pink-bronze metal, the dominant 32px warm carrier. This
# is the hue that separates DAWN-LOTUS-COURT from the cool-gold kin: the cyan
# blessing stones sit in WARM rose-gold bezels (warm setting, cool stone).
GOLD      = (216, 156, 118)   # rose-gold metal (the warm hue separator on ivory)
GOLD_BR   = (244, 196, 162)
GOLD_D    = (158, 104,  74)
# LOTUS-PINK — a SPARING low-third blush accent unique to this version (no cool
# kin uses a third hue). Used ONLY for petal-ticks / lotus-bud incisions / a faint
# brow blush; kept DIM (below the gems and the rose-gold) so it never competes.
LOTUS     = (232, 166, 182)   # auspicious lotus blush (low-third accent ONLY)
LOTUS_D   = (176, 110, 130)   # incised/shaded lotus-mark line
INK       = ( 28,  22,  26)   # hard ink keyline
# crown skulls go a touch DARKER than the warm-light body so they don't melt into
# it OR wash out on the day sky (dimmest tier) — but they keep the DAWN warm cast
# (not cooled) so the 32px read stays uniformly warm versus the cool kin.
CROWN_BONE   = (178, 160, 146)
CROWN_BONE_D = (116, 104,  94)
CROWN_SH     = (214, 198, 184)
THIRD_EYE = CYAN              # cyan third-eye slit = the single brightest focal

BG        = ( 92,  96, 108)   # neutral grey review backdrop
PANEL     = ( 70,  74,  86)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 246)
LABEL_DIM = (190, 198, 212)


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


# ── bone-bead strand — the brood's non-naked density device ───────────────────
def bead_strand(surf, pts, bead_r, s, gold_every=3, pip_r_frac=0.42, light=True):
    """A strand of pale bone beads threaded along a polyline, with WARM gold
    spacer-pips every `gold_every` beads. WHY: the whole tonal-collapse fix lives
    here — on the LIGHT warm-bone field the pale beads read as a sheen-lit highlight
    chain (INK keyline + near-white sheen dot give each a rounded edge), and the
    periodic gold pip injects a warm hue so the strand never collapses to a grey
    smear. Beads are spaced evenly by arc length so the lattice stays regular at
    downscale."""
    if len(pts) < 2:
        return
    # accumulate arc length and walk it, dropping a bead every 2*bead_r
    segs = []
    total = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, d))
        total += d
    pitch = max(1.0, bead_r * 1.85)
    n = max(1, int(total / pitch))
    idx = 0
    for k in range(n + 1):
        target = k * pitch
        # find the segment containing this arc position
        acc = 0.0
        bx, by = pts[0]
        for (a, b, d) in segs:
            if acc + d >= target or (a, b, d) is segs[-1]:
                t = (target - acc) / max(1e-6, d)
                t = max(0.0, min(1.0, t))
                bx = a[0] + (b[0] - a[0]) * t
                by = a[1] + (b[1] - a[1]) * t
                break
            acc += d
        if idx % gold_every == 0:
            # warm gold spacer-pip (smaller, the hue separator)
            triad_circle(surf, GOLD, (int(bx), int(by)), max(1, int(bead_r * (0.6 + pip_r_frac))),
                         ow=max(1, int(1.0 * s)), core=False)
            pygame.draw.circle(surf, GOLD_BR, (int(bx - bead_r * 0.2), int(by - bead_r * 0.2)),
                               max(1, int(bead_r * 0.22)))
        else:
            col = BEAD if light else BONE
            triad_circle(surf, col, (int(bx), int(by)), max(1, int(bead_r)),
                         ow=max(1, int(1.0 * s)), core=False)
            pygame.draw.circle(surf, BEAD_BR, (int(bx - bead_r * 0.28), int(by - bead_r * 0.30)),
                               max(1, int(bead_r * 0.30)))
        idx += 1


def bead_arc(surf, cx, cy, r, a0, a1, bead_r, s, gold_every=3, light=True):
    """Convenience wrapper — a bead strand laid along a circular arc."""
    steps = max(2, int(abs(a1 - a0) / 0.18))
    pts = [(cx + math.cos(a0 + (a1 - a0) * i / steps) * r,
            cy + math.sin(a0 + (a1 - a0) * i / steps) * r) for i in range(steps + 1)]
    bead_strand(surf, pts, bead_r, s, gold_every=gold_every, light=light)


# ── a single ornamental crown-skull (cloned from Citipati; crown-warm tint) ────
def crown_skull(surf, cx, cy, r, s, lit=False, idx=0):
    """Tiny crown skull — bone-JEWEL relic seated in her tiara arc. WHY a notch
    darker than the warm-light body (CROWN_BONE) but kept WARM (not cooled): against
    the dawn-ivory body the crown sits a value step down (the dimmest tier) to hold
    its shape, but stays warm so the 32px read is uniformly the warm/festive sister.
    WHY `idx`: the six crown relics must read as six DISTINCT skulls — so `idx`
    drives the CRANIUM SILHOUETTE (tall / round / squat / lopsided / heart-domed)
    plus a gentle lean AND a DIFFERENT auspicious brow-mark each, so the scalloped
    arc reads as six individually-blessed lumps. These are GENTLE relics — even
    teeth, NO chips, a calm low socket glint. `lit` is the crown-CENTRE relic: it
    carries the slightly larger rose-gold-bezelled cyan BLESSING-DROP (still DIM —
    no white core, no glow), the only crown drop; the rest get the calm glint."""
    ow1 = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── per-relic table — variety in the SHAPE + a distinct auspicious mark ──
    # cw/ch = cranium width/height · lean = dome skew · heart = dimpled crown top ·
    # suture style · brow ridge? · jaw set (set/plain — both gentle) · mark = the
    # forehead ornament-mark (each crown relic a DIFFERENT one). NO chip — calm.
    CROWN_PROFILE = [
        # 0: TALL narrow dome, beaded suture, set jaw — TILAKA stroke
        dict(cw=0.88, ch=1.18, lean=0.00, heart=False, sut="dots", brow=True,  jaw="set",   mark="tilaka"),
        # 1: broad ROUND dome, zigzag suture, plain jaw — PETAL-tick
        dict(cw=1.16, ch=0.96, lean=0.06, heart=False, sut="zig",  brow=False, jaw="plain", mark="petal"),
        # 2: SQUAT low dome (centre, lit) — heart-domed, beaded suture — LOTUS-bud
        dict(cw=1.10, ch=0.86, lean=0.00, heart=True,  sut="dots", brow=True,  jaw="set",   mark="lotus"),
        # 3: LOPSIDED dome leaning right, zigzag suture — rose-gold BAND
        dict(cw=1.00, ch=1.02, lean=0.18, heart=False, sut="zig",  brow=True,  jaw="plain", mark="band"),
        # 4: HEART-domed (notched crown), plain suture, set jaw — BINDI dot
        dict(cw=1.02, ch=1.06, lean=-0.08, heart=True, sut="line", brow=False, jaw="set",   mark="bindi"),
        # 5: lopsided SQUAT dome leaning left, zigzag suture — PETAL-tick
        dict(cw=1.08, ch=0.92, lean=-0.16, heart=False, sut="zig", brow=True,  jaw="plain", mark="petal"),
    ]
    p = CROWN_PROFILE[idx % len(CROWN_PROFILE)]
    cw, ch, lean = p["cw"], p["ch"], p["lean"]

    # cranium as an ink-keyed POLYGON (not a plain circle) so width/height/lean and
    # the heart-notch all live in the silhouette. The lean skews the upper dome
    # sideways; the heart profiles dimple the crown top into two soft lumps.
    dome = []
    for ang_deg in range(-180, 1, 18):     # top half-ring: brow → temples → crown
        a = math.radians(ang_deg)
        dx = math.cos(a) * r * cw
        dy = math.sin(a) * r * ch
        dx += lean * r * (-dy / max(1.0, r))      # shear the dome toward the lean
        if p["heart"] and abs(math.cos(a)) < 0.34 and math.sin(a) < -0.4:
            dy += r * 0.22                         # dimple the crown into a heart
        dome.append((cx + dx, cy + dy))
    # cheeks taper down to the jaw line
    dome.append((cx + r * cw * 0.74 + lean * r * 0.2, cy + r * ch * 0.34))
    dome.append((cx - r * cw * 0.74 + lean * r * 0.2, cy + r * ch * 0.34))
    triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in dome], ow=ow1)
    # a single dim top-left sheen wedge (CROWN_SH — never brighter than the body)
    sheen = [(cx - r * cw * 0.58, cy - r * ch * 0.10),
             (cx - r * cw * 0.10 + lean * r * 0.2, cy - r * ch * 0.66),
             (cx - r * cw * 0.02, cy - r * ch * 0.34),
             (cx - r * cw * 0.46, cy + r * ch * 0.02)]
    pygame.draw.polygon(surf, CROWN_SH, [(int(x), int(y)) for x, y in sheen])

    # cranial SUTURE — per-profile crown seam (the carved-bone read at hero scale)
    seam_y = cy - r * ch * 0.56
    if p["sut"] == "zig":
        zp = [(cx - r * 0.34 + j * (r * 0.68 / 4),
               seam_y + (r * 0.10 if j % 2 else -r * 0.06)) for j in range(5)]
        pygame.draw.lines(surf, CROWN_BONE_D, False,
                          [(int(x), int(y)) for x, y in zp], ow_thin)
    elif p["sut"] == "dots":
        for j in range(5):
            zx = cx - r * 0.34 + j * (r * 0.68 / 4)
            pygame.draw.circle(surf, CROWN_BONE_D, (int(zx), int(seam_y)), max(1, int(0.9 * s)))
            if j % 2 == 0:    # dim gold pip on alternate suture nodes (jewel-set bone)
                pygame.draw.circle(surf, GOLD_D, (int(zx), int(seam_y)), max(1, int(0.8 * s)))
    else:   # "line" — a single straight median suture
        pygame.draw.line(surf, CROWN_BONE_D, (int(cx), int(cy - r * ch * 0.78)),
                         (int(cx), int(cy - r * 0.06)), ow_thin)

    # optional brow ridge — a short dark bar above the sockets (carved relief)
    if p["brow"]:
        pygame.draw.line(surf, CROWN_BONE_D,
                         (int(cx - r * 0.46), int(cy - r * 0.02)),
                         (int(cx + r * 0.46), int(cy - r * 0.02)), max(1, int(1.3 * s)))

    # jaw — per-profile: a SET stub (narrow, tucked) or a PLAIN wider bar
    if p["jaw"] == "set":
        jaw = [(cx - r * 0.44, cy + r * 0.52), (cx + r * 0.44, cy + r * 0.52),
               (cx + r * 0.26, cy + r * 0.98), (cx - r * 0.26, cy + r * 0.98)]
    else:
        jaw = [(cx - r * 0.54, cy + r * 0.50), (cx + r * 0.54, cy + r * 0.50),
               (cx + r * 0.38, cy + r * 1.02), (cx - r * 0.38, cy + r * 1.02)]
    triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in jaw], ow=max(1, int(1.2 * s)))

    # two dark sockets, each with a CALM low cyan glint (every gentle relic) — the
    # lit centre relic's glint sits a hair brighter but still dim (no white, no glow)
    glint_c = CYAN if lit else CYAN_D
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        pygame.draw.circle(surf, glint_c, (ex, cy + int(r * 0.06)), max(1, int(r * 0.10)))

    # nasal pit
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))

    # tooth line — a short bar with EVEN slits (no chips; these relics are gentle)
    ty = cy + int(r * 0.70)
    pygame.draw.line(surf, INK, (cx - int(r * 0.32), ty), (cx + int(r * 0.32), ty),
                     max(1, int(1.2 * s)))
    for j in range(3):
        tx = cx - int(r * 0.24) + j * int(r * 0.24)
        pygame.draw.line(surf, INK, (tx, ty - int(r * 0.08)), (tx, ty + int(r * 0.10)),
                         max(1, int(1.0 * s)))

    # AUSPICIOUS brow-mark — each crown relic carries a DIFFERENT ornament-mark
    # (lotus-bud / tilaka / petal / bindi / rose-gold band), dim low-third flavour.
    brow_mark(surf, cx, cy - int(r * 0.30), max(2, int(r * 0.30)), s, p["mark"])
    # the lit crown-CENTRE relic carries the slightly larger rose-gold-bezelled cyan
    # BLESSING-DROP — still DIM (no white core, no glow) so the gems stay above it.
    if lit:
        blessing_drop(surf, (cx, cy - int(r * 0.06)), max(2, int(r * 0.26)), s)


# ── the cyan "blessing-drop" — a rose-gold-bezelled brow drop (DIM, cool) ─────
def blessing_drop(surf, c, r, s):
    """A slightly LARGER rose-gold-bezelled cyan brow drop — the cool blessing the
    auspicious skulls carry. WHY a clear value step BELOW the brow third-eye and
    well below the hero gem: no skull may own a white-hot core, so this drop caps
    at a small CYAN_BR rim glint only and rides a WARM rose-gold bezel (warm
    setting, cool stone) so it reads as a blessed jewel, not a focal."""
    cx, cy = int(c[0]), int(c[1])
    triad_circle(surf, GOLD, (cx, cy), r + max(1, int(1.1 * s)),
                 ow=max(1, int(1.0 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, INK, (cx, cy), r)
    pygame.draw.circle(surf, CYAN_D, (cx, cy), max(1, r - max(1, int(0.6 * s))))
    pygame.draw.circle(surf, CYAN, (cx, cy), max(1, int(r * 0.62)))
    pygame.draw.circle(surf, CYAN_BR, (cx - int(r * 0.30), cy - int(r * 0.32)),
                       max(1, int(r * 0.24)))


# ── per-skull auspicious BROW-MARK — the lotus-court blessing on every skull ──
def brow_mark(surf, cx, cy, r, s, kind):
    """Incise/ink a DIFFERENT auspicious ornament-mark on each skull's forehead so
    all 12 read as individually BLESSED, not one stamp. WHY low-third dim: these
    are close-up flavour — the WARM rose-gold palette carries the 32px read, so
    the lotus-pink marks stay below the gems and the metal. `kind` selects the
    mark: lotus-bud incision, tilaka dot, petal-tick, bindi, or a rose-gold band."""
    ow = max(1, int(1.0 * s))
    if kind == "lotus":
        # an incised lotus-bud: a small upright teardrop with two side petals
        pygame.draw.polygon(surf, LOTUS_D,
                            [(cx, cy - int(r * 0.7)), (cx + int(r * 0.34), cy),
                             (cx, cy + int(r * 0.18)), (cx - int(r * 0.34), cy)])
        pygame.draw.line(surf, LOTUS, (cx, cy - int(r * 0.6)), (cx, cy), ow)
        for sgn in (-1, 1):
            pygame.draw.line(surf, LOTUS_D, (cx, cy),
                             (cx + sgn * int(r * 0.5), cy - int(r * 0.18)), ow)
    elif kind == "tilaka":
        # a vertical tilaka stroke (third-eye line)
        pygame.draw.line(surf, LOTUS_D, (cx, cy - int(r * 0.7)), (cx, cy + int(r * 0.5)),
                         max(1, int(1.6 * s)))
        pygame.draw.line(surf, LOTUS, (cx, cy - int(r * 0.6)), (cx, cy + int(r * 0.3)), ow)
    elif kind == "petal":
        # a three-petal tick fanning up (lotus shorthand)
        for k in (-1, 0, 1):
            a = math.radians(-90 + k * 32)
            pygame.draw.line(surf, LOTUS_D, (cx, cy + int(r * 0.2)),
                             (cx + math.cos(a) * r * 0.7, cy + math.sin(a) * r * 0.7), ow)
        pygame.draw.circle(surf, LOTUS, (cx, cy + int(r * 0.2)), max(1, int(0.9 * s)))
    elif kind == "bindi":
        # a round lotus-pink bindi dot ringed by a dim rose-gold tick
        pygame.draw.circle(surf, GOLD_D, (cx, cy), max(1, int(r * 0.5)))
        pygame.draw.circle(surf, LOTUS, (cx, cy), max(1, int(r * 0.34)))
    else:   # "band" — a small rose-gold brow band arc
        rect = (cx - int(r * 0.7), cy - int(r * 0.5), int(r * 1.4), int(r * 1.0))
        pygame.draw.arc(surf, GOLD_D, rect, math.radians(200), math.radians(340),
                        max(1, int(1.8 * s)))
        pygame.draw.arc(surf, GOLD, rect, math.radians(205), math.radians(335), ow)


# ── a tiny skull cradled in an open palm (the brood MOTIF) ────────────────────
def palm_skull(surf, cx, cy, r, s, idx=0):
    """An open BONE palm cradling a CRAFTED reliquary skull. WHY both pieces: the
    brood motif is six open palms EACH holding a skull at the fan tips. WHY the
    `idx`: DAWN-LOTUS-COURT's six palm-skulls are GENTLE-AUSPICIOUS (mild/closed
    jaws, even teeth, NO cracks, a calm low cyan socket glint) but each BLESSED by
    a DIFFERENT brow ornament-mark + a gentle per-skull tilt, so the six read as
    six individually-blessed relics, not one stamp. The two FLANKING palms
    (idx 1 + idx 4 — the outer hands either side of the body) carry a slightly
    LARGER rose-gold-bezelled cyan BLESSING-DROP on the brow; the rest get a calm
    socket glint. MID value tier: pale warm BEAD bone, brighter than the crown
    skulls, dimmer than the third-eye — and no skull ever owns a white-hot core."""
    ow1 = max(1, int(1.4 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── per-skull auspicious table (six gentle, individually-blessed relics) ──
    # tilt(rad), cranium x/y stretch, jaw mode (closed/mild — NO cracks), n_teeth
    # (even), suture style, mark = distinct brow ornament, drop = bigger cyan
    # blessing-drop? (only the two flanking palms). NO `chip` — these are calm.
    PROFILE = [
        # 0: tall egg-dome, mildly-parted jaw, zigzag suture, incised LOTUS-bud
        dict(tilt=-0.12, cw=0.96, ch=1.12, jaw="mild",   teeth=6, sut="zig",  mark="lotus",  drop=False),
        # 1: FLANK — broad round, closed jaw, dotted suture, BINDI + BLESSING-DROP
        dict(tilt= 0.08, cw=1.14, ch=0.96, jaw="closed", teeth=6, sut="dots", mark="bindi",  drop=True),
        # 2: narrow upright, closed jaw, zigzag suture, TILAKA stroke
        dict(tilt=-0.18, cw=0.90, ch=1.06, jaw="closed", teeth=6, sut="zig",  mark="tilaka", drop=False),
        # 3: squat low dome, mildly-parted jaw, straight suture, PETAL-tick
        dict(tilt= 0.06, cw=1.06, ch=0.90, jaw="mild",   teeth=6, sut="line", mark="petal",  drop=False),
        # 4: FLANK — tall narrow, closed jaw, dotted suture, rose-gold BAND + DROP
        dict(tilt= 0.16, cw=0.90, ch=1.10, jaw="closed", teeth=6, sut="dots", mark="band",   drop=True),
        # 5: gently lopsided, closed jaw, zigzag suture, incised LOTUS-bud
        dict(tilt=-0.06, cw=1.04, ch=1.00, jaw="closed", teeth=6, sut="zig",  mark="lotus",  drop=False),
    ]
    p = PROFILE[idx % len(PROFILE)]
    t = p["tilt"]
    ct, st = math.cos(t), math.sin(t)

    def rot(dx, dy):
        # rotate an offset about the skull centre, then translate to (cx,cy)
        return (cx + dx * ct - dy * st, cy + dx * st + dy * ct)

    cw, ch = p["cw"], p["ch"]
    # ── open palm cup — a shallow bone bowl with finger-ticks fanning up ──
    cup = [(cx - int(r * 1.05), cy + int(r * 0.30)),
           (cx - int(r * 0.70), cy + int(r * 0.78)),
           (cx + int(r * 0.70), cy + int(r * 0.78)),
           (cx + int(r * 1.05), cy + int(r * 0.30)),
           (cx + int(r * 0.75), cy + int(r * 0.10)),
           (cx - int(r * 0.75), cy + int(r * 0.10))]
    triad_blob(surf, BONE, cup, ow=max(1, int(1.2 * s)))
    for k in range(-2, 3):
        fx = cx + int(k * r * 0.40)
        pygame.draw.line(surf, INK, (fx, cy + int(r * 0.20)),
                         (fx + int(k * r * 0.10), cy - int(r * 0.20)), max(1, int(2.0 * s)))
        pygame.draw.line(surf, BONE_SH, (fx, cy + int(r * 0.18)),
                         (fx + int(k * r * 0.10), cy - int(r * 0.16)), max(1, int(1.0 * s)))

    # ── the cradled skull centre (seated a touch higher so the dome nests) ──
    scx, scy = cx, cy - int(r * 0.36)
    cr = r * 0.66                     # cranium radius unit (modest enlarge for detail)

    # cranium dome — an ink-keyed bone polygon shaped per-profile (NOT a plain
    # circle): wide brow tapering to a narrower jaw, stretched by cw/ch + tilted.
    dome = []
    for ang_deg in range(-180, 1, 20):    # top half-ring (brow + temples + crown)
        a = math.radians(ang_deg)
        dome.append(rot(math.cos(a) * cr * cw, math.sin(a) * cr * ch))
    # cheek taper down to the jaw line (the lower face narrows)
    dome.append(rot(cr * cw * 0.78, cr * ch * 0.30))
    dome.append(rot(cr * cw * 0.52, cr * ch * 0.72))
    dome.append(rot(-cr * cw * 0.52, cr * ch * 0.72))
    dome.append(rot(-cr * cw * 0.78, cr * ch * 0.30))
    triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in dome], ow=ow1)
    # top-left bone sheen wedge on the cranium (the triad highlight)
    sheen = [rot(-cr * cw * 0.62, -cr * ch * 0.30),
             rot(-cr * cw * 0.12, -cr * ch * 0.74),
             rot(-cr * cw * 0.04, -cr * ch * 0.40),
             rot(-cr * cw * 0.50, -cr * ch * 0.04)]
    pygame.draw.polygon(surf, BEAD_BR, [(int(x), int(y)) for x, y in sheen])

    # cranial SUTURE — per-profile, riding the crown seam (the carved-bone read)
    if p["sut"] == "zig":
        zp = []
        for j in range(5):
            zx = -cr * 0.34 + j * (cr * 0.68 / 4)
            zy = -cr * ch * 0.62 + (cr * 0.10 if j % 2 else -cr * 0.06)
            zp.append(rot(zx, zy))
        pygame.draw.lines(surf, BONE_DD, False, [(int(x), int(y)) for x, y in zp], ow_thin)
    elif p["sut"] == "dots":
        for j in range(5):
            zx = -cr * 0.34 + j * (cr * 0.68 / 4)
            dx, dy = rot(zx, -cr * ch * 0.60)
            pygame.draw.circle(surf, BONE_DD, (int(dx), int(dy)), max(1, int(0.9 * s)))
            if j % 2 == 0:    # tiny gold pip on alternate suture nodes (jewel-set bone)
                gx, gy = rot(zx, -cr * ch * 0.60)
                pygame.draw.circle(surf, GOLD, (int(gx), int(gy)), max(1, int(0.8 * s)))
    else:   # "line" — a single straight median suture
        pygame.draw.line(surf, BONE_DD,
                         (int(rot(0, -cr * ch * 0.80)[0]), int(rot(0, -cr * ch * 0.80)[1])),
                         (int(rot(0, -cr * 0.10)[0]), int(rot(0, -cr * 0.10)[1])), ow_thin)

    # brow ridge — a short dark bar above the sockets (carved relief)
    br0 = rot(-cr * 0.46, -cr * 0.02)
    br1 = rot(cr * 0.46, -cr * 0.02)
    pygame.draw.line(surf, BONE_D, (int(br0[0]), int(br0[1])), (int(br1[0]), int(br1[1])),
                     max(1, int(1.4 * s)))

    # temple / cheek hollow — a faint shade pocket on the lower-right cheek
    hollow = [rot(cr * 0.20, cr * 0.18), rot(cr * 0.60, cr * 0.20),
              rot(cr * 0.52, cr * 0.56), rot(cr * 0.18, cr * 0.50)]
    pygame.draw.polygon(surf, BONE_D, [(int(x), int(y)) for x, y in hollow])

    # ── deep ink sockets with a CARVED rim (a bone ring around each pit) ──
    socket_r = cr * 0.30
    for sgn in (-1, 1):
        ecx, ecy = rot(sgn * cr * 0.40, cr * 0.14)
        ecx, ecy = int(ecx), int(ecy)
        # carved bone rim (a ring) then the deep ink pit
        pygame.draw.circle(surf, BONE_D, (ecx, ecy), int(socket_r + max(1, 1.2 * s)))
        pygame.draw.circle(surf, INK, (ecx, ecy), int(socket_r))
        pygame.draw.circle(surf, BONE_DD, (ecx, ecy), int(socket_r * 0.62))
        pygame.draw.circle(surf, INK, (ecx, ecy), int(socket_r * 0.34))
        # a CALM low cyan socket glint on every gentle skull (auspicious, not lit):
        # a small dim CYAN_D dot deep in the pit — never bright enough to compete
        # with the brow blessing-drop or the gems.
        pygame.draw.circle(surf, CYAN_D, (ecx, ecy + int(socket_r * 0.10)),
                           max(1, int(socket_r * 0.22)))

    # nasal aperture — an inverted ink teardrop between/below the sockets
    n_top = rot(0, cr * 0.30)
    n_l = rot(-cr * 0.16, cr * 0.58)
    n_r = rot(cr * 0.16, cr * 0.58)
    pygame.draw.polygon(surf, INK, [(int(n_top[0]), int(n_top[1])),
                                    (int(n_l[0]), int(n_l[1])),
                                    (int(n_r[0]), int(n_r[1]))])

    # ── jaw — per-profile, BOTH gentle: a closed bar or a mildly-parted jaw ──
    # WHY no agape/cracked here: this version is auspicious, so the jaws stay calm.
    jl, jr = -cr * 0.40, cr * 0.40       # jaw corners under the cheeks
    if p["jaw"] == "closed":
        jaw = [rot(jl, cr * 0.74), rot(jr, cr * 0.74),
               rot(jr * 0.70, cr * 1.04), rot(jl * 0.70, cr * 1.04)]
        triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        teeth_y0, teeth_y1 = cr * 0.74, cr * 1.00
    else:   # "mild" — a softly-parted jaw: a shallow dark line, then a tucked jaw
        gap = [rot(jl * 0.72, cr * 0.78), rot(jr * 0.72, cr * 0.78),
               rot(jr * 0.62, cr * 0.94), rot(jl * 0.62, cr * 0.94)]
        pygame.draw.polygon(surf, BONE_DD, [(int(x), int(y)) for x, y in gap])
        jaw = [rot(jl * 0.74, cr * 0.94), rot(jr * 0.74, cr * 0.94),
               rot(jr * 0.58, cr * 1.18), rot(jl * 0.58, cr * 1.18)]
        triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        teeth_y0, teeth_y1 = cr * 0.74, cr * 0.92

    # tooth row — n_teeth EVEN ink slits, no gaps (gentle, intact smile)
    nt = p["teeth"]
    for j in range(nt):
        fx = -cr * 0.34 + j * (cr * 0.68 / max(1, nt - 1))
        tp0 = rot(fx, teeth_y0)
        tp1 = rot(fx, teeth_y1)
        pygame.draw.line(surf, INK, (int(tp0[0]), int(tp0[1])),
                         (int(tp1[0]), int(tp1[1])), max(1, int(1.0 * s)))

    # ── auspicious BROW: a distinct ornament-mark on every skull, and on the two
    # flanking palms a slightly larger rose-gold-bezelled cyan BLESSING-DROP ──
    mx, my = rot(0, -cr * 0.26)
    brow_mark(surf, int(mx), int(my), max(2, int(cr * 0.30)), s, p["mark"])
    if p["drop"]:
        gx, gy = rot(0, -cr * 0.04)
        blessing_drop(surf, (gx, gy), max(2, int(cr * 0.30)), s)


# ── the Mukha-Devi six-arm radial fan (cloned; bead-armlet wrapped) ───────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr, arm_th_frac=0.16):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the ONLY radial silhouette in the brood. Low-origin, ~[100,64,28]° off the
    vertical, NONE straight up → the crown sky stays open. WHY beaded armlets:
    this sister wraps every surface, so each arm carries a bone-bead bracelet at
    the wrist + an armlet near the shoulder. Returns the six hand centres + their
    outward angles for palm-skull placement."""
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
                       ow=max(1, int(arm_th * arm_th_frac)))
        triad_circle(surf, BONE, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        # beaded armlet (near the elbow) + bracelet (at the wrist) wrapping the arm
        for frac, br in ((0.62, 0.55), (0.92, 0.62)):
            wx = sh[0] + (hand[0] - sh[0]) * frac
            wy = sh[1] + (hand[1] - sh[1]) * frac
            perp = a + math.pi / 2
            band_r = arm_th * 0.80
            p0 = (wx + math.cos(perp) * band_r, wy + math.sin(perp) * band_r)
            p1 = (wx - math.cos(perp) * band_r, wy - math.sin(perp) * band_r)
            bead_strand(surf, [p0, p1], arm_th * br * 0.42, s, gold_every=2)
        hands.append((sgn, d, hand, a))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1]), h[3]) for h in hands]


# ── a FACETED cyan cut-stone GEM — asthi's contained jewel (current-design focal) ──
def cyan_gem(surf, c, r, s, focal=False, bg=None, hot=None):
    """A CUT cyan jewel built from FLAT FACET PLANES, not a glossy sphere — a facet
    ROSETTE: a flat angular TABLE polygon at the crown, ringed by angled crown facets
    that radiate from the table edge out to the bezel, each a FILLED polygon in a
    stepped cyan value so adjacent planes meet at SHARP corners. Hard glints are tiny
    white TRIANGLES pinned at facet corners. `focal` is the brow third-eye: it alone
    gets the white hot core + 3 glints and shows ONLY its octagonal faceted stone (no
    circular background)."""
    cx, cy = int(c[0]), int(c[1])
    # `bg`/`hot` decouple the two focal traits so a gem can drop one without the
    # other: the necklace HERO gem keeps the white-hot core (hot) with no ink seat
    # (bg off); the brow third-eye reuses no-seat but drops the hot core a step.
    show_bg = (not focal) if bg is None else bg
    show_hot = focal if hot is None else hot
    # the focal brow gem shows only its faceted stone (no circular background); a
    # non-focal palm gem keeps an ink seat to read against bone.
    if show_bg:
        pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.4 * s)))

    # the crown girdle outline — a faceted POLYGON (octagonal), NOT a circle: the
    # straight-edged girdle kills the round-lens read at the silhouette.
    def gpt(ang_deg, rad):
        a = math.radians(ang_deg)
        return (cx + math.cos(a) * rad, cy + math.sin(a) * rad)
    n_crown = 8
    girdle = [gpt(-90 + i * (360 / n_crown), r) for i in range(n_crown)]
    pygame.draw.polygon(surf, CYAN_D, girdle)

    # the flat TABLE face — a smaller angular polygon offset UP toward the crown.
    table_r = r * 0.46
    tcx, tcy = cx, cy - int(r * 0.10)
    table = [(tcx + math.cos(math.radians(-90 + i * (360 / n_crown))) * table_r,
              tcy + math.sin(math.radians(-90 + i * (360 / n_crown))) * table_r)
             for i in range(n_crown)]

    # the CROWN FACETS — one filled trapezoid bridging each girdle edge to the table
    # edge, light-direction value steps so neighbours never share a tone.
    for i in range(n_crown):
        g0, g1 = girdle[i], girdle[(i + 1) % n_crown]
        t0, t1 = table[i], table[(i + 1) % n_crown]
        mx = (g0[0] + g1[0]) * 0.5 - cx
        my = (g0[1] + g1[1]) * 0.5 - cy
        facing = -(mx * 0.7 + my * 0.7) / max(1.0, r)
        if facing > 0.35:
            fc = CYAN_BR
        elif facing > -0.15:
            fc = CYAN
        else:
            fc = lerp(CYAN, CYAN_D, 0.6)
        pygame.draw.polygon(surf, fc, [g0, g1, t1, t0])
        pygame.draw.polygon(surf, INK, [g0, g1, t1, t0], max(1, int(0.9 * s)))

    # the flat table plane on top — lighter than every crown facet so the eye lands
    # on the table, like a real cut stone.
    pygame.draw.polygon(surf, lerp(CYAN, CYAN_BR, 0.55), table)
    pygame.draw.polygon(surf, INK, table, max(1, int(0.9 * s)))
    pygame.draw.line(surf, CYAN_BR, table[0], table[n_crown // 2], max(1, int(0.8 * s)))

    # HARD specular glints — tiny TRIANGLES pinned at facet corners. Pure white is
    # reserved for the HERO necklace gem (show_hot); the dimmer non-hot third-eye
    # glints a soft cyan-white so the hero gem stays the single brightest pixel.
    gcol = (255, 255, 255) if show_hot else (210, 238, 245)
    def glint(px, py, sz):
        pygame.draw.polygon(surf, gcol,
                            [(px, py - sz), (px + sz, py + sz * 0.5),
                             (px - sz, py + sz * 0.5)])

    g = max(1, int(r * 0.16))
    glint(table[6][0], table[6][1], g)
    if show_hot:
        # the white HOT CORE — the single brightest pixel of the whole sprite.
        pygame.draw.polygon(surf, CYAN_BR,
                            [(tcx, tcy - int(r * 0.22)), (tcx + int(r * 0.20), tcy),
                             (tcx, tcy + int(r * 0.20)), (tcx - int(r * 0.20), tcy)])
        pygame.draw.circle(surf, (240, 255, 255), (tcx, tcy), max(2, int(r * 0.15)))
        pygame.draw.circle(surf, (255, 255, 255), (tcx - int(r * 0.04), tcy - int(r * 0.04)),
                           max(1, int(r * 0.08)))
        glint(girdle[1][0], girdle[1][1], max(1, int(r * 0.12)))
        glint(table[3][0], table[3][1], max(1, int(r * 0.11)))


# ── the bone-jewel sky-dancer ─────────────────────────────────────────────────
def draw_asthi_dakini(surf, cx, cy, s):
    """Cocked-hip dancing chibi skeleton (CITIPATI body) under a six-arm radial
    fan (MUKHA). Each of the six open palms cradles a tiny skull. A fused crown
    (Mukha tiara-band across the brow + wide airy 6-skull arc) tops the head, and
    a multi-strand bone-bead jewelry SET (3-row choker, swag necklace, armlets/
    bracelets/anklets, wheel earrings, beaded girdle) wraps every surface.
    `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(34 * s))
    hr = int(26 * s)
    hip_y = cy + int(24 * s)
    hip_cx = cx + int(7 * s)

    # === SIX-ARM RADIAL FAN (drawn first → behind torso & head) ===============
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.92), s, hr)

    # === LEGS — cocked-hip dance, one knee kicked OUT (Citipati body) =========
    def bone_limb(p0, p1, p2, thick, joint=True):
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

    leg_th = int(14 * s)
    hipL = (hip_cx - int(13 * s), hip_y)
    kneeL = (hip_cx - int(20 * s), hip_y + int(26 * s))
    footL = (hip_cx - int(22 * s), hip_y + int(52 * s))
    bone_limb(hipL, kneeL, footL, leg_th)
    hipR = (hip_cx + int(11 * s), hip_y)
    kneeR = (hip_cx + int(30 * s), hip_y + int(8 * s))
    footR = (hip_cx + int(20 * s), hip_y + int(34 * s))
    bone_limb(hipR, kneeR, footR, leg_th)
    for (fx, fy), sgn in ((footL, -1), (footR, +1)):
        foot = [(fx - int(4 * s), fy - int(2 * s)), (fx + sgn * int(16 * s), fy + int(2 * s)),
                (fx + sgn * int(15 * s), fy + int(10 * s)), (fx - int(5 * s), fy + int(8 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.4 * s)))
    # beaded ANKLETS — a bead band just above each foot (jewelry set, ankle tier)
    for (kx, ky), (fx, fy) in ((kneeL, footL), (kneeR, footR)):
        ax = fx + (kx - fx) * 0.32
        ay = fy + (ky - fy) * 0.32
        ang = math.atan2(ky - fy, kx - fx) + math.pi / 2
        ar = leg_th * 0.85
        bead_strand(surf, [(ax + math.cos(ang) * ar, ay + math.sin(ang) * ar),
                           (ax - math.cos(ang) * ar, ay - math.sin(ang) * ar)],
                    leg_th * 0.30, s, gold_every=2)

    # === PELVIS + RIBCAGE (Citipati torso) ====================================
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

    spine_top_y = cy - int(16 * s)
    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx + int(2 * s), cy + int(6 * s)),
             (cx - int(1 * s), spine_top_y)]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    rc_cx, rc_cy = cx, cy - int(4 * s)
    rc_w, rc_h = int(34 * s), int(40 * s)
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
    # 4 rib-band arcs (the Citipati torso motif)
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.4 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(6 * s)), max(1, int(2 * s)))

    # === ARMS of the DANCE (flamenco flourish) wrapped in bead bracelets ======
    # WHY a flourish PAIR on top of the six-arm fan: the Citipati dance read needs
    # an asymmetric raised pair; the radial fan frames behind, this pair gestures.
    arm_th = int(8 * s)
    shoulderL = (rc_cx - int(16 * s), rc_cy - rc_h // 2 + int(6 * s))
    shoulderR = (rc_cx + int(16 * s), rc_cy - rc_h // 2 + int(5 * s))
    elbowL = (rc_cx - int(30 * s), rc_cy - int(18 * s))
    handL = (rc_cx - int(26 * s), rc_cy - int(40 * s))
    bone_limb(shoulderL, elbowL, handL, arm_th)
    elbowR = (rc_cx + int(30 * s), rc_cy - int(2 * s))
    handR = (rc_cx + int(40 * s), rc_cy + int(14 * s))
    bone_limb(shoulderR, elbowR, handR, arm_th)
    for (hx, hy), sgn, up in ((handL, -1, True), (handR, +1, False)):
        triad_circle(surf, BONE, (hx, hy), int(5 * s), ow=max(1, int(1.2 * s)), core=False)
        for k in range(-1, 3):
            ang = math.radians(-90 + k * 26) if up else math.radians(40 + k * 26)
            ex = hx + math.cos(ang) * int(9 * s)
            ey = hy + math.sin(ang) * int(9 * s)
            pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(1, int(1.6 * s)))
            pygame.draw.line(surf, BONE, (hx, hy), (ex, ey), max(1, int(1 * s)))

    # === SIX PALM-SKULLS — one cradled in every fan hand (the brood MOTIF) ====
    # WHY enumerate: each hand gets a DISTINCT `idx` so the six read as six
    # individual reliquary skulls (cranium/jaw/teeth/suture/gem vary per idx),
    # making this sister's brood the most ornamented of the set.
    for i, (hx, hy, a) in enumerate(hands):
        palm_skull(surf, hx, hy, int(hr * 0.36), s, idx=i)

    # === BEADED GIRDLE — the 32px-CARRYING element (bold rows across the hips) =
    # WHY this is the silhouette element: a wide bold double-row bead-girdle slung
    # across the pelvis collapses to two clean light bands at 32px, the single
    # heaviest ornament read that holds when the fine lattice mushes.
    g_y0 = hip_y - int(2 * s)
    for row, (yy, br) in enumerate(((g_y0, 0.0), (g_y0 + int(7 * s), 0.0))):
        bead_arc(surf, hip_cx, hip_y - int(20 * s), int(40 * s) + row * int(4 * s),
                 math.radians(58), math.radians(122), int(4.6 * s), s, gold_every=3)
    # girdle pendant tassel — a short bead drop at the centre front
    bead_strand(surf, [(hip_cx, g_y0 + int(8 * s)), (hip_cx, g_y0 + int(22 * s))],
                int(3.4 * s), s, gold_every=2)

    # === 3-ROW CHOKER + long SWAG NECKLACE (bold rows, the second 32px read) ==
    neck_y = rc_cy - rc_h // 2 - int(1 * s)
    for r_i in range(3):
        cy_row = neck_y + r_i * int(5 * s)
        bead_arc(surf, rc_cx, cy_row - int(4 * s), int(18 * s) + r_i * int(2 * s),
                 math.radians(35), math.radians(145), int(3.2 * s), s, gold_every=3)
    # long swag necklace dipping onto the ribcage (a deep U)
    swag = [(rc_cx - int(15 * s), neck_y + int(10 * s)),
            (rc_cx - int(8 * s), rc_cy + int(8 * s)),
            (rc_cx, rc_cy + int(13 * s)),
            (rc_cx + int(8 * s), rc_cy + int(8 * s)),
            (rc_cx + int(15 * s), neck_y + int(10 * s))]
    bead_strand(surf, swag, int(3.6 * s), s, gold_every=3)
    # the HERO gem — a faceted cyan cut-stone at the necklace centre (the LARGER
    # gem + the single brightest pixel: hot core on, no ink seat).
    cyan_gem(surf, (rc_cx, rc_cy + int(14 * s)), int(10 * s), s, focal=True)

    # === SKULL HEAD — chibi, scary-cute, cyan third-eye (single brightest) ====
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # big round sockets — scary-cute, kept dim (no hot core) so the third-eye wins
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.10)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.26))
        pygame.draw.circle(surf, CYAN_D, (ex + sgn * int(1 * s), ey + int(1 * s)), int(hr * 0.10))
    # THIRD EYE — the same faceted cyan cut-gem, SMALLER than the necklace hero gem
    # and a step dimmer (no white-hot core), so the necklace gem reads as brightest.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.36)
    cyan_gem(surf, (tex, tey), int(hr * 0.28), s, focal=True, hot=False)
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.70)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))

    # === WHEEL EARRINGS — beaded ring discs hung at each temple (jewelry set) ==
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 1.04)
        ey = head_c[1] + int(hr * 0.10)
        triad_circle(surf, GOLD, (ex, ey), int(hr * 0.30), ow=max(1, int(1.4 * s)), core=False)
        triad_circle(surf, BONE_DD, (ex, ey), int(hr * 0.16), ow=max(1, int(1.0 * s)),
                     core=False, sheen=False)
        # bead rim ticks around the wheel
        for t in range(8):
            a = math.radians(t * 45)
            bx = ex + math.cos(a) * int(hr * 0.30)
            by = ey + math.sin(a) * int(hr * 0.30)
            pygame.draw.circle(surf, BEAD_BR, (int(bx), int(by)), max(1, int(1.4 * s)))

    # === FUSED CROWN — Mukha tiara-BAND on the brow + wide airy 6-skull ARC ====
    # WHY both languages: a plain arc reads as the Citipati reference, so the
    # tiara-band (a beaded gold band seated ACROSS the brow) is drawn first, then
    # the wide 6-skull arc sweeps above it in open sky. Crown skulls = warm-bone,
    # the dimmest value tier; only the centre skull glows.

    # -- tiara-band across the brow (Mukha language) --
    tiara_r = int(hr * 0.98)
    band_pts = []
    for i in range(11):
        a = math.radians(212 + i * (116 / 10))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, GOLD_BR, False, band_pts[:6], max(1, int(1.4 * s)))
    # a bead-row riding on the band (carry the brood's bead texture into the crown)
    bead_arc(surf, head_c[0], head_c[1], int(hr * 0.98), math.radians(214),
             math.radians(326), int(2.6 * s), s, gold_every=3)
    # three cyan brow-cabochons set into the band (sparse jewel — not focal-bright)
    for i in range(3):
        a = math.radians(232 + i * 38)
        bx = head_c[0] + math.cos(a) * int(hr * 0.98)
        by = head_c[1] + math.sin(a) * int(hr * 0.98)
        triad_circle(surf, CYAN_D, (int(bx), int(by)), max(1, int(2.4 * s)),
                     ow=max(1, int(1.0 * s)), core=False, sheen=False)

    # -- wide airy 6-skull arc sweeping ABOVE the band (Citipati language) --
    arc_r = int(hr * 1.66)
    skull_r = int(hr * 0.36)
    # thin gold arc-wire the skulls perch on (kept linear)
    wire_pts = []
    for i in range(13):
        a = math.radians(216 + i * (108 / 12))
        wire_pts.append((head_c[0] + math.cos(a) * arc_r,
                         head_c[1] + math.sin(a) * arc_r))
    pygame.draw.lines(surf, INK, False, wire_pts, int(4 * s))
    pygame.draw.lines(surf, GOLD_D, False, wire_pts, int(2 * s))
    # WHY exactly ONE lit skull (centre of the 6): the locked rule restricts the
    # crown accent to the crown-CENTRE relic only; the rest stay the dimmest value
    # tier. WHY `idx=i`: the six relics each get a DISTINCT cranium silhouette + set,
    # so the arc reads as six individual jewels, not one stamp swept six times.
    for i in range(6):
        a = math.radians(220 + i * (100 / 5))
        sx = head_c[0] + math.cos(a) * arc_r
        sy = head_c[1] + math.sin(a) * arc_r
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2), idx=i)


# ── the bone-bead reliquary-staff → pillar mirror (sister's own forms) ────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The pillar is built from this sister's OWN forms: a stacked column of
    vertebra beads strung on a central rod (the Citipati torso rib-band motif),
    EVERY tier wrapped in a bone-bead collar (her jewelry set), and a gap-edge cap
    of one warm crown-skull seated on a beaded tiara-band ring (her fused-crown
    language in miniature). On-axis, symmetric, never top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(15 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    bead_pitch = int(20 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    while y <= b1:
        bw = shaft_w
        bead = [(cx - bw, y + int(2 * s)),
                (cx - int(bw * 0.5), y - int(7 * s)),
                (cx + int(bw * 0.5), y - int(7 * s)),
                (cx + bw, y + int(2 * s)),
                (cx + int(bw * 0.5), y + int(11 * s)),
                (cx - int(bw * 0.5), y + int(11 * s))]
        triad_blob(surf, BONE, bead,
                   core_pts=[(cx, y - int(1 * s)), (cx + bw, y + int(2 * s)),
                             (cx + int(bw * 0.5), y + int(11 * s)), (cx, y + int(9 * s))],
                   sheen_pts=[(cx - bw, y + int(2 * s)), (cx - int(bw * 0.5), y - int(6 * s)),
                              (cx - int(bw * 0.2), y - int(4 * s)), (cx - int(bw * 0.7), y + int(5 * s))],
                   ow=max(1, int(1.4 * s)))
        pygame.draw.circle(surf, BONE_DD, (cx, y + int(2 * s)), int(4 * s))
        pygame.draw.circle(surf, INK, (cx, y + int(2 * s)), int(4 * s), max(1, int(1 * s)))
        # bone-bead collar wrapping each vertebra tier (her jewelry set on the shaft)
        bead_strand(surf, [(cx - bw - int(3 * s), y + int(2 * s)),
                           (cx + bw + int(3 * s), y + int(2 * s))],
                    int(3.0 * s), s, gold_every=3)
        y += bead_pitch

    # === gap-edge cap: warm crown-skull on a beaded tiara-band ring ===========
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    cap_skull_r = int(14 * s)
    # beaded tiara-band ring behind the cap skull (fused-crown language, miniature)
    bead_arc(surf, cx, cap_y, int(cap_skull_r * 1.35), math.radians(180), math.radians(360),
             int(3.0 * s), s, gold_every=3)
    crown_skull(surf, cx, cap_y, cap_skull_r, s, lit=True)
    # gold ferrule collar where the cap meets the shaft
    collar_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(11 * s), collar_y - int(3 * s), int(22 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(2 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale, ss=SS):
    big = pygame.Surface((boxw * ss, boxh * ss), pygame.SRCALPHA)
    draw_asthi_dakini(big, draw_cx * ss, draw_cy * ss, scale * ss)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def export_hero():
    """Standalone hi-res hero PNG (~1024px tall) so the dense bead-work survives.
    Rendered at SS=8 on a large canvas then smoothscaled into the export box."""
    boxw, boxh = 760, 1024
    hero = render_creature_chip(boxw, boxh, 380, 540, 3.7, ss=SS)
    canvas = pygame.Surface((boxw, boxh))
    vgrad(canvas, (0, 0, boxw, boxh), (74, 84, 104), (40, 46, 64))
    canvas.blit(hero, (0, 0))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2_hero.png")
    pygame.image.save(canvas, out)
    return out


def blackout(surf):
    """Flatten any non-transparent pixel to solid ink — the silhouette proof."""
    out = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(surf)
    sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
    out.blit(sil, (0, 0))
    return out


def main():
    W, H = 1180, 900
    font_big = font(30)
    f = font(16)
    f_sm = font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("ASTHI v5 — DAWN-LOTUS-COURT", True, LABEL), (24, 13))
    sheet.blit(f_sm.render(
        "auspicious sunrise blessing-bringer  ·  ROSE-GOLD + sparing LOTUS-PINK + cool cyan blessing-jewels · 12 gentle skulls each a DIFFERENT auspicious brow-mark · round 1",
        True, LABEL_DIM), (270, 28))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(380, 540, 188, 296, 2.05)
    sheet.blit(hero, (14, 92))
    sheet.blit(f.render("Creature — hero", True, LABEL), (120, 636))
    sheet.blit(f_sm.render("Cocked-hip DANCE under a six-arm radial fan; each of the 6 open palms cradles", True, LABEL_DIM), (14, 660))
    sheet.blit(f_sm.render("a tiny skull. Fused crown = Mukha tiara-band on the brow + wide airy 6-skull arc.", True, LABEL_DIM), (14, 676))
    sheet.blit(f_sm.render("ROSE-GOLD lattice carries the WARM 32px read; sparing lotus-pink ticks the brow-marks (low-third).", True, LABEL_DIM), (14, 692))
    sheet.blit(f_sm.render("Ladder: hero gem white core > brow third-eye > dim cyan blessing-drops + lotus-pink; NO skull core.", True, LABEL_DIM), (14, 708))

    # === (b) PILLAR assembled — mirrored, tileable shaft ======================
    pcx = 444
    top_big = pygame.Surface((150 * SS, 280 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 276 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 280)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 280 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 276 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 280)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 280 + 96))
    pygame.draw.rect(sheet, (58, 62, 74), (pcx + 8, 86 + 280, 134, 96))
    sheet.blit(f_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 280 + 40))
    sheet.blit(f.render("Pillar — bead-reliquary staff", True, LABEL), (pcx - 4, 766))
    sheet.blit(f_sm.render("vertebra beads + bone-bead collars = shaft;", True, LABEL_DIM), (pcx - 4, 790))
    sheet.blit(f_sm.render("crown-skull on a beaded tiara-ring caps the gap", True, LABEL_DIM), (pcx - 4, 806))

    # === (c) TRUE 32px DAY + NIGHT chips + blackout proof ======================
    panel_x = 632
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 700))
    sheet.blit(f.render("True 32px gameplay chip + silhouette", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((120 * SS, 120 * SS), pygame.SRCALPHA)
        draw_asthi_dakini(big, 60 * SS, 64 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (120, 120))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 15, day_y + 15))
    sheet.blit(f_sm.render("32px DAY sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 15, night_y + 15))
    sheet.blit(f_sm.render("32px NIGHT sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout / silhouette proof beside the 32px chips
    bo = blackout(chip)
    bx = panel_x + 192
    pygame.draw.rect(sheet, (208, 214, 224), (bx, day_y, 150, 150))
    pygame.draw.rect(sheet, INK, (bx, day_y, 150, 150), 1)
    sheet.blit(bo, (bx + 15, day_y + 15))
    sheet.blit(f_sm.render("silhouette proof", True, LABEL), (bx, day_y + 156))
    # a larger blackout of the hero so the fan + crown read as one shape
    bo_big = blackout(render_creature_chip(150, 200, 75, 110, 0.82))
    pygame.draw.rect(sheet, (208, 214, 224), (bx, night_y, 150, 200))
    pygame.draw.rect(sheet, INK, (bx, night_y, 150, 200), 1)
    sheet.blit(bo_big, (bx, night_y))
    sheet.blit(f_sm.render("hero silhouette", True, LABEL_DIM), (bx, night_y + 204))

    # a 32px pillar gap-cap chip on both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 140 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 138 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 140))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 364
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 6))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 6))
    sheet.blit(f_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(f_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette strip
    sheet.blit(f.render("Pinned palette", True, LABEL), (panel_x + 16, day_y + 380))
    swatches = [
        (BONE, "DAWN-ivory bone"), (BONE_D, "bone shade"),
        (GOLD, "ROSE-GOLD metal"), (GOLD_BR, "rose-gold sheen"),
        (LOTUS, "LOTUS-PINK (low-third)"), (LOTUS_D, "lotus-mark line"),
        (CYAN, "cool cyan blessing"), (CROWN_BONE, "crown bone"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, day_y + 408
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 184
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(f_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 836, W - 28, 48))
    sheet.blit(f_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale; standalone hi-res hero export (round_2_hero.png).",
        True, LABEL_DIM), (26, 846))
    sheet.blit(f_sm.render(
        "STAY: flat fills · hard ink keyline (28,22,26) · dark-core->fill->top-left sheen triad · 1px grown outline · chibi scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 864))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    hero_out = export_hero()
    print("wrote", out)
    print("wrote", hero_out)


if __name__ == "__main__":
    main()
