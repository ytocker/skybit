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

WHY the palette is a WARM, light AGED-BONE (~212,202,186) ivory: she reads as
real bone, not steel — matching the Citipati family's chalk/rose bone. The #1
tonal-collapse risk is low-chroma beads on low-chroma bone reading as a grey
smear ("naked in disguise"). The fix on a LIGHT field: the bead lattice sits a
value step ABOVE the bone as a pale highlight chain held by INK keylines + sheen,
and the WARM gold spacer-pips carry the hue separation (gold-on-ivory) — value
AND hue separation, colourblind-safe — so the contrast is never only cyan-on-blue.

WHY the fused crown shows BOTH languages: a plain skull-arc alone reads as the
Citipati reference, so the crown seats the Mukha tiara-BAND across the brow AND
sweeps the wide airy 6-skull arc above it. Crown skulls are a touch darker/cooler
than the warm body so they don't melt into it and still hold against open sky.

VERDIGRIS-RELIQUARY variant: a dug-up centuries-old Asthi in aged temple BRONZE
gone GREEN-PATINA. The metal ornament is oxidised olive-bronze; skull-cyan reads
as MATTE verdigris bloom. The two ICY/CRISP cyan gems — the larger necklace hero
(white-hot core) + the smaller brow third-eye — stay un-oxidised, and that clean
ice against the oxidised court is the whole point.

Value ladder (AD hard rule): ICY necklace hero gem (white core) = brightest →
ICY third-eye = next → bone → matte verdigris bloom = DIM (no skull gets a white
core; the bloom always sits below the brow third-eye).

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
# VERDIGRIS-RELIQUARY: a dug-up centuries-old Asthi. The bone carries a subtle
# COOLER / GREENER cast (B nudged up, R pulled down so R≈G>B instead of R>G>B) so
# the "ancient / unearthed" read lands even at 32px — but it stays clearly BONE,
# not green: a grey-green ivory, never sage. Hollows still go near-neutral dark.
# lit plane brightened ~10% toward the rim-sheen so the lower-half bone limbs hold
# their value against the BRIGHT day sky and don't muddy/soften into it; the dark
# INK keyline that holds the silhouette on the NIGHT chip is untouched, so night
# stays read-clean while the day chip's body gains separation.
BONE      = (212, 214, 198)   # ancient grey-green ivory (the dominant LIGHT field)
BONE_D    = (144, 148, 132)   # bone shade / mid-core (cooler)
BONE_DD   = ( 84,  88,  78)   # deepest bone hollow (sockets, rib gaps) — stays dark
BONE_SH   = (228, 230, 218)   # bone top-left rim-sheen (cool near-white)
# Beads pushed BRIGHTER + cooler-neutral than the warm bone field so the lattice
# reads as its own value step on the now-light bone (a pale highlight chain), with
# the gold pips carrying the hue contrast.
# beads follow the bone's cool-grey-green cast (a value step above the field).
BEAD      = (224, 226, 214)   # pale ancient bead — a value step above the field
BEAD_BR   = (244, 246, 238)   # bead top sheen / hottest bead (cool near-white)
# the TWO hero gems stay ICY / CRISP cyan — deliberately NOT green-shifted, so the
# clean ice reads against the oxidised bronze court. This contrast is the version.
CYAN      = ( 86, 214, 226)   # icy-cyan — necklace HERO gem + brow third-eye ONLY
CYAN_BR   = (188, 248, 252)   # hot cyan inner (hero white core sits on this)
CYAN_D    = ( 40, 132, 150)
# AGED-BRONZE metal family — the gold ornament has gone centuries-old bronze: a
# muted olive-bronze base, a dim tarnished low, a brighter burnished catch-light
# where edges were rubbed clean. Bezels/pips/ornament now read as dug-up metalwork.
GOLD      = (158, 140,  70)   # aged bronze base (the metal of every bezel/pip/band)
GOLD_BR   = (204, 184, 116)   # burnished bronze catch-light (rubbed-clean edge)
GOLD_D    = (104,  92,  46)   # tarnished bronze low (recessed metal)
# VERDIGRIS patina — the green copper-bloom that has crept over the bronze and
# stands in for the oxidised metalwork: a matte blue-green, used on bezels/pips/
# ornament edges and as the MATTE skull-cyan bloom (NOT the icy faceted gem look).
PATINA    = (120, 150, 110)   # verdigris patina (bronze oxidation green)
PATINA_BR = (162, 188, 150)   # lighter bloom / powdery seafoam crest
PATINA_D  = ( 70,  98,  78)   # deep verdigris crust in recesses (eaten edges)
INK       = ( 28,  22,  26)   # hard ink keyline
# crown skulls go a touch DARKER + cooler than the now-warm-light body so they
# don't melt into the body OR wash out on the day sky; they stay the dimmest tier.
CROWN_BONE   = (158, 162, 150)
CROWN_BONE_D = (100, 104,  94)
CROWN_SH     = (192, 196, 184)
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
    darker/cooler than the warm-light body (CROWN_BONE): against the new warm ivory
    body, an equally-warm crown would melt in, so the crown sits a value step down
    (the dimmest tier) and slightly cooler to keep its shape against both body and
    sky. WHY `idx`: the six crown relics must read as six DISTINCT skulls, not one
    stamp repeated — so `idx` drives the CRANIUM SILHOUETTE (tall / round / squat /
    lopsided / heart-domed), suture style, brow + jaw set and a tooth-chip on one.
    The variety lives in the OUTLINE (width/height/lean), so the scalloped arc reads
    as distinct lumps at 32px, not only as interior lines. `lit` keeps the centre
    relic's eyes cyan-tinted — the ONLY crown accent — but stays the DIMMEST tier
    (no white core, no glow, no brightness bump); the gold-bezel cyan pip on the
    pip-bearing relics is a DIM hue echo, not a focal."""
    ow1 = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── per-relic silhouette + EROSION table — variety in SHAPE and weathering ──
    # cw/ch = cranium width/height stretch · lean = sideways skew of the dome ·
    # heart = a notched/dimpled crown top · suture style · brow ridge? · jaw set ·
    # pip = bezel pip? · chip = a broken tooth? · eros = the verdigris decay over
    # THIS relic (crust from a socket edge / temple-streak / verdigris suture-studs /
    # a patina-EATEN socket altering the silhouette / pitting / heavy bloom). The 6
    # crown relics weather DIFFERENTLY from each other AND from the 6 palm skulls.
    # `bite` carves a chunk OUT of the cranium silhouette (a centuries-collapsed
    # skull) so the crown bead-row TOP EDGE reads broken/non-repeating at 32px, not
    # a uniform scallop. side = which temple/crown is gone (-1 L / 1 R / 0 crown-cap),
    # depth = how deep the collapse eats toward the dome centre. The fine-crust
    # weathering (eros) stays, but THIS is the silhouette-level damage.
    CROWN_PROFILE = [
        # 0: TALL narrow dome — CROWN-CAP knocked off (flat-topped, missing vault)
        dict(cw=0.88, ch=1.18, lean=0.00, heart=False, sut="dots", brow=True,  jaw="set",   pip=True,  chip=False,
             bite=dict(side=0, depth=0.46),
             eros=dict(crust=-1, streak=0,  studs=True,  eaten=0,  pit=False, bloom=False)),
        # 1: broad ROUND dome, plain jaw; R temple-STREAK + pitting; L socket BITTEN
        dict(cw=1.16, ch=0.96, lean=0.00, heart=False, sut="zig",  brow=False, jaw="plain", pip=False, chip=False,
             bite=None,
             eros=dict(crust=0,  streak=1,  studs=False, eaten=-1, pit=True,  bloom=False)),
        # 2: SQUAT heart-dome (CENTRE, lit) — MOST bloomed: both sockets + crust patch
        dict(cw=1.10, ch=0.86, lean=0.00, heart=True,  sut="dots", brow=True,  jaw="set",   pip=True,  chip=False,
             bite=None,
             eros=dict(crust=0,  streak=0,  studs=True,  eaten=0,  pit=True,  bloom=True)),
        # 3: LOPSIDED dome leaning right — R TEMPLE COLLAPSED (chunk out of silhouette)
        dict(cw=1.00, ch=1.02, lean=0.20, heart=False, sut="zig",  brow=True,  jaw="plain", pip=False, chip=True,
             bite=dict(side=1, depth=0.58),
             eros=dict(crust=0,  streak=-1, studs=False, eaten=1,  pit=False, bloom=False)),
        # 4: HEART-domed, set jaw; L socket crust + verdigris studs; R socket BITTEN
        dict(cw=1.02, ch=1.06, lean=-0.06, heart=True, sut="line", brow=False, jaw="set",   pip=False, chip=False,
             bite=None,
             eros=dict(crust=-1, streak=0,  studs=True,  eaten=1,  pit=True,  bloom=False)),
        # 5: lopsided SQUAT dome — L TEMPLE COLLAPSED (chunk out of silhouette)
        dict(cw=1.08, ch=0.92, lean=-0.18, heart=False, sut="zig", brow=True,  jaw="plain", pip=False, chip=True,
             bite=dict(side=-1, depth=0.52),
             eros=dict(crust=0,  streak=1,  studs=False, eaten=-1, pit=False, bloom=False)),
    ]
    p = CROWN_PROFILE[idx % len(CROWN_PROFILE)]
    cw, ch, lean = p["cw"], p["ch"], p["lean"]
    e = p["eros"]
    bite = p["bite"]

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
        # BITE — collapse part of the dome INWARD so the silhouette loses a chunk.
        # side 0 caves the whole crown-cap (flat top); ±1 caves one temple/upper
        # quadrant. Pulling the ring radius toward 0 over the bitten span removes
        # that lump from the OUTLINE — the broken top edge survives the downscale.
        if bite is not None:
            ca, sa = math.cos(a), math.sin(a)
            if bite["side"] == 0:               # crown-cap gone: flatten the very top
                if sa < -0.55:
                    dy += r * ch * bite["depth"]
            else:                               # one temple collapsed inward
                if bite["side"] * ca > 0.30 and sa < -0.10:
                    dx -= bite["side"] * r * cw * bite["depth"]
                    dy += r * ch * bite["depth"] * 0.30
        dome.append((cx + dx, cy + dy))
    # cheeks taper down to the jaw line
    dome.append((cx + r * cw * 0.74 + lean * r * 0.2, cy + r * ch * 0.34))
    dome.append((cx - r * cw * 0.74 + lean * r * 0.2, cy + r * ch * 0.34))
    triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in dome], ow=ow1)
    # a near-black crust packed into the COLLAPSED region so the broken edge also
    # reads by VALUE (a dark void where the vault/temple sheared away), not only by
    # the missing outline — this is what makes the gap legible at 32px.
    if bite is not None:
        bd = lerp(INK, CROWN_BONE_D, 0.30)
        if bite["side"] == 0:                   # dark scar under the lost crown-cap
            cap_scar = [(cx - r * cw * 0.40, cy - r * ch * (1.18 - bite["depth"])),
                        (cx + r * cw * 0.40, cy - r * ch * (1.18 - bite["depth"])),
                        (cx + r * cw * 0.30, cy - r * ch * (0.84 - bite["depth"])),
                        (cx - r * cw * 0.30, cy - r * ch * (0.84 - bite["depth"]))]
            pygame.draw.polygon(surf, bd, [(int(x), int(y)) for x, y in cap_scar])
        else:                                   # dark void in the caved temple
            sgnb = bite["side"]
            vcx = cx + sgnb * int(r * cw * (0.62 - bite["depth"] * 0.5))
            vcy = cy - int(r * ch * 0.42)
            pygame.draw.circle(surf, bd, (vcx, vcy), max(2, int(r * 0.30)))
            pygame.draw.circle(surf, INK, (vcx, vcy), max(1, int(r * 0.16)))
    # a single dim top-left sheen wedge (CROWN_SH — never brighter than the body)
    sheen = [(cx - r * cw * 0.58, cy - r * ch * 0.10),
             (cx - r * cw * 0.10 + lean * r * 0.2, cy - r * ch * 0.66),
             (cx - r * cw * 0.02, cy - r * ch * 0.34),
             (cx - r * cw * 0.46, cy + r * ch * 0.02)]
    pygame.draw.polygon(surf, CROWN_SH, [(int(x), int(y)) for x, y in sheen])

    # ── EROSION over THIS crown relic (pushed into value/silhouette for 32px) ──
    if e["streak"]:    # a matte verdigris temple-run down one cheek
        sg = e["streak"]
        st_poly = [(cx + sg * r * 0.40, cy - r * 0.18), (cx + sg * r * 0.58, cy - r * 0.10),
                   (cx + sg * r * 0.44, cy + r * 0.44), (cx + sg * r * 0.26, cy + r * 0.38)]
        pygame.draw.polygon(surf, PATINA, [(int(x), int(y)) for x, y in st_poly])
    if e["bloom"]:     # a heavy crust patch on the cranium (most-bloomed relic)
        verdigris_bloom(surf, int(cx - r * 0.06), int(cy - r * ch * 0.36), int(r * 0.34), s)
    if e["pit"]:       # scattered matte pitting flecks
        for (px, py) in ((-0.34, -0.28), (0.30, -0.18), (-0.10, -0.40)):
            pygame.draw.circle(surf, PATINA_D, (int(cx + px * r), int(cy + py * r)), max(1, int(0.8 * s)))

    # cranial SUTURE — per-profile crown seam (the carved-bone read at hero scale).
    # WHY studs go PATINA: an `eros.studs` relic carries green verdigris suture-studs
    # (oxidised pins) instead of the tarnished-bronze pip.
    seam_y = cy - r * ch * 0.56
    if p["sut"] == "zig":
        zp = [(cx - r * 0.34 + j * (r * 0.68 / 4),
               seam_y + (r * 0.10 if j % 2 else -r * 0.06)) for j in range(5)]
        pygame.draw.lines(surf, CROWN_BONE_D, False,
                          [(int(x), int(y)) for x, y in zp], ow_thin)
        if e["studs"]:
            for (zx, zy) in (zp[0], zp[2], zp[4]):
                pygame.draw.circle(surf, PATINA, (int(zx), int(zy)), max(1, int(0.8 * s)))
    elif p["sut"] == "dots":
        for j in range(5):
            zx = cx - r * 0.34 + j * (r * 0.68 / 4)
            pygame.draw.circle(surf, CROWN_BONE_D, (int(zx), int(seam_y)), max(1, int(0.9 * s)))
            if j % 2 == 0:    # alt nodes: verdigris stud (oxidised) or tarnished pip
                node = PATINA if e["studs"] else GOLD_D
                pygame.draw.circle(surf, node, (int(zx), int(seam_y)), max(1, int(0.8 * s)))
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

    # two dark sockets — patina EATS/CRUSTS one rim, the bloomed relic rings both.
    # WHY the lit centre's eyes go PATINA (not CYAN_D): skull-cyan is oxidised bloom,
    # so even the lit crown relic stays a matte verdigris glow — DIM, below the two
    # icy hero gems — never the crisp cyan that the necklace + brow gems own.
    eye_c = PATINA if lit else INK
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.38)
        ey = cy + int(r * 0.04)
        if e["eaten"] == sgn:    # an ASYMMETRIC near-black bite — a socket eaten open
            # WHY enlarged + INK-cored: a small verdigris speck vanished at 32px; this
            # merges the socket into a big irregular dark hole that reads as decay on
            # the crown row even when downscaled (a value bite, off-centre per side).
            bxe = ex + int(sgn * r * 0.24)
            pygame.draw.circle(surf, PATINA_D, (bxe, ey - int(r * 0.06)), int(r * 0.40))
            pygame.draw.circle(surf, INK, (ex + int(sgn * r * 0.10), ey), int(r * 0.30))
            pygame.draw.circle(surf, PATINA, (bxe + int(sgn * r * 0.12), ey - int(r * 0.18)),
                               int(r * 0.13))
        pygame.draw.circle(surf, INK, (ex, ey), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, ey), max(1, int(r * 0.12)))
        if e["crust"] == sgn:    # a softer patina lip creeping in from one edge
            pygame.draw.circle(surf, PATINA, (ex + int(sgn * r * 0.22), ey + int(r * 0.16)),
                               max(1, int(r * 0.14)))
        if e["bloom"]:           # heavy bloom ringing both sockets (most-bloomed relic)
            pygame.draw.circle(surf, PATINA, (ex, ey), int(r * 0.30), max(1, int(1.2 * s)))

    # nasal pit
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))

    # tooth line — a short bar with a couple of slits; the chip profiles drop one
    ty = cy + int(r * 0.70)
    pygame.draw.line(surf, INK, (cx - int(r * 0.32), ty), (cx + int(r * 0.32), ty),
                     max(1, int(1.2 * s)))
    for j in range(3):
        tx = cx - int(r * 0.24) + j * int(r * 0.24)
        if p["chip"] and j == 1:
            continue   # a knocked-out tooth — the chip read on a lopsided relic
        pygame.draw.line(surf, INK, (tx, ty - int(r * 0.08)), (tx, ty + int(r * 0.10)),
                         max(1, int(1.0 * s)))

    # DIM tarnished-bronze-bezel verdigris brow pip on the pip-bearing relics — an
    # oxidised echo of her metalwork, kept the dimmest tier (GOLD_D + PATINA, no
    # white core, no glow) so the two icy hero gems stay the brightest cyan.
    if p["pip"]:
        bg_y = cy - int(r * 0.28)
        pygame.draw.circle(surf, GOLD_D, (cx, bg_y), max(1, int(r * 0.18)))
        pygame.draw.circle(surf, PATINA, (cx, bg_y), max(1, int(r * 0.11)))


# ── a MATTE verdigris-bloom inlay — the skull-cyan, oxidised not icy ──────────
def palm_cabochon(surf, c, r, s):
    """Skull-cyan as a MATTE VERDIGRIS BLOOM, NOT the icy faceted gem. WHY the bloom
    look: the two hero gems (necklace + brow) are the only ICY/CRISP cyan on the
    figure; everything the skulls carry is oxidised-copper bloom — a dim, flat,
    green-shifted patina crust ringed by a tarnished-bronze bezel. WHY no glint /
    no white core: the LADDER GUARDRAIL keeps every skull below the brow third-eye,
    so this caps at a dull PATINA_BR speck (never CYAN_BR, never a hot core)."""
    cx, cy = int(c[0]), int(c[1])
    # tarnished bronze bezel (the eaten setting), then the matte verdigris crust
    triad_circle(surf, GOLD_D, (cx, cy), r + max(1, int(0.9 * s)),
                 ow=max(1, int(1.0 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, INK, (cx, cy), r)
    pygame.draw.circle(surf, PATINA_D, (cx, cy), max(1, r - max(1, int(0.6 * s))))
    pygame.draw.circle(surf, PATINA, (cx, cy), max(1, int(r * 0.62)))
    # an off-centre powdery bloom flake — matte, dim, irregular (NOT a rim glint)
    pygame.draw.circle(surf, PATINA_BR, (cx - int(r * 0.18), cy - int(r * 0.16)),
                       max(1, int(r * 0.30)))


# ── a creeping verdigris BLOOM patch — eats edges + rings sockets (silhouette) ─
def verdigris_bloom(surf, cx, cy, r, s, spread=1.0, ink_edge=True):
    """A matte patina BLOOM patch — the oxidised-copper crust creeping over bone.
    WHY it pushes into VALUE/SILHOUETTE (a cooler dark crust + a powdery crest),
    not fine glints: fine crust is hero-only, so the weathering must read at 32px
    as a cooler, darker bite out of the bone. `spread` scales the patch; the more-
    bloomed skulls stack several of these. Stays DIM — below the brow third-eye."""
    rr = max(2, int(r * spread))
    if ink_edge:
        pygame.draw.circle(surf, PATINA_D, (cx, cy), rr + max(1, int(0.6 * s)))
    pygame.draw.circle(surf, PATINA, (cx, cy), rr)
    # a small lighter seafoam crest, offset, so the bloom has a matte bi-tone read
    pygame.draw.circle(surf, PATINA_BR, (cx - int(rr * 0.22), cy - int(rr * 0.24)),
                       max(1, int(rr * 0.42)))


# ── a tiny skull cradled in an open palm (the brood MOTIF) ────────────────────
def palm_skull(surf, cx, cy, r, s, idx=0):
    """An open BONE palm cradling a CRAFTED reliquary skull. WHY both pieces: the
    brood motif is six open palms EACH holding a skull at the fan tips. WHY the
    `idx`: this sister's skulls are the most ORNAMENTED of the brood and must read
    as six DISTINCT individuals, not one dome re-tilted — so `idx` drives cranium
    shape, jaw set, tilt, tooth count/chips, suture pattern and ornament. 2-3 of
    the six carry a DIM gold-bezel cyan cabochon (a value step below the focal
    brow gem) to lean into the jewel-set-bone look. MID value tier: pale BEAD bone,
    brighter than the crown skulls, dimmer than the third-eye."""
    ow1 = max(1, int(1.4 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── per-skull EROSION register (six skulls, each weathered DIFFERENTLY) ──
    # Beyond shape/jaw/teeth/suture, each carries an `eros` recipe — the kind of
    # centuries-old decay creeping over THIS skull, pushed into VALUE/SILHOUETTE so
    # it reads at 32px (no two alike). `eros` fields:
    #   crust  — which socket EDGE a verdigris crust creeps in from (-1 L / 1 R / 0)
    #   streak — a patina temple-streak running down one cheek (-1 / 0 / 1)
    #   studs  — green verdigris suture-studs replacing the bone seam-dots
    #   eaten  — a socket whose silhouette is BITTEN by a patina-eaten edge (-1/1/0)
    #   pit    — scattered patina pitting flecks on the cranium
    #   bloom  — heavy bloom: rings BOTH sockets + a cranium crust patch (the 3 most)
    # WHY idx 0 + 3 carry bloom=True: after the fan sort, idx 0 and idx 3 are the
    # two LOWEST palms (the d=100° hands), the pair the brief blooms most heavily.
    # `tone` differentiates the six palms by VALUE (not just detail) so the fan reads
    # as differently-AGED relics, not six clones: <0 = darker/deeper patina (older,
    # more shadowed), >0 = lighter/cleaner (a near-intact relic). Two go dark, two
    # light, two stay mid — and the darkest (idx 0) is the most-eaten, the lightest
    # (idx 1) the most near-intact, so the pair anchors the aged-range read.
    PROFILE = [
        # 0: tall egg-dome, agape jaw, GEM-bloom brow — MOST bloomed + DARKEST (eaten)
        dict(tilt=-0.16, cw=0.96, ch=1.12, jaw="agape", teeth=5, sut="zig", gem=True,  chip=False, tone=-0.40,
             eros=dict(crust=-1, streak=1,  studs=True,  eaten=-1, pit=True,  bloom=True)),
        # 1: broad round skull, closed jaw — LIGHTEST / cleanest near-intact relic
        dict(tilt= 0.10, cw=1.14, ch=0.96, jaw="closed", teeth=6, sut="dots", gem=False, chip=False, tone=0.36,
             eros=dict(crust=0,  streak=0,  studs=False, eaten=0,  pit=False, bloom=False)),
        # 2: narrow tilted skull, cracked jaw, bloom-lit socket; R socket EATEN — MID
        dict(tilt=-0.30, cw=0.88, ch=1.04, jaw="cracked", teeth=3, sut="zig", gem="socket", chip=True, tone=0.0,
             eros=dict(crust=0,  streak=-1, studs=False, eaten=1,  pit=True,  bloom=False)),
        # 3: squat low dome, wide agape jaw — MOST bloomed + DARKER (older)
        dict(tilt= 0.06, cw=1.06, ch=0.90, jaw="agape", teeth=7, sut="line", gem=False, chip=False, tone=-0.30,
             eros=dict(crust=1,  streak=-1, studs=True,  eaten=1,  pit=True,  bloom=True)),
        # 4: tall narrow, closed jaw, GEM-bloom brow — LIGHTER / cleaner relic
        dict(tilt= 0.22, cw=0.90, ch=1.10, jaw="closed", teeth=5, sut="dots", gem=True,  chip=False, tone=0.26,
             eros=dict(crust=-1, streak=0,  studs=True,  eaten=0,  pit=False, bloom=False)),
        # 5: lopsided cranium, cracked jaw, chipped; L socket EATEN (silhouette) — MID
        dict(tilt=-0.08, cw=1.02, ch=1.00, jaw="cracked", teeth=4, sut="zig", gem=False, chip=True, tone=0.0,
             eros=dict(crust=0,  streak=0,  studs=False, eaten=-1, pit=True,  bloom=False)),
    ]
    p = PROFILE[idx % len(PROFILE)]
    t = p["tilt"]
    # per-skull bone tones — dark relics steer toward the cool bone shade, light ones
    # toward the cool near-white sheen, so adjacent palms separate by VALUE at 32px.
    tone = p["tone"]
    if tone < 0:
        skull_bone = lerp(BEAD, BONE_D, -tone)
        skull_sheen = lerp(BEAD_BR, BEAD, -tone * 0.9)
    else:
        skull_bone = lerp(BEAD, BEAD_BR, tone)
        skull_sheen = BEAD_BR
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
    triad_blob(surf, skull_bone, [(int(x), int(y)) for x, y in dome], ow=ow1)
    # top-left bone sheen wedge on the cranium (the triad highlight)
    sheen = [rot(-cr * cw * 0.62, -cr * ch * 0.30),
             rot(-cr * cw * 0.12, -cr * ch * 0.74),
             rot(-cr * cw * 0.04, -cr * ch * 0.40),
             rot(-cr * cw * 0.50, -cr * ch * 0.04)]
    pygame.draw.polygon(surf, skull_sheen, [(int(x), int(y)) for x, y in sheen])

    # ── EROSION register — the centuries-old verdigris decay over THIS skull ──
    # WHY here (under the carved detail): the crust/streak/pit sit ON the dome so
    # they read as patina eating into the bone, but below the sockets so the eaten-
    # edge silhouette work (further down) still bites the socket outline cleanly.
    e = p["eros"]
    # patina temple-STREAK — a matte verdigris run down one cheek (value, not line)
    if e["streak"]:
        sg = e["streak"]
        streak = [rot(sg * cr * 0.46, -cr * 0.10), rot(sg * cr * 0.66, -cr * 0.04),
                  rot(sg * cr * 0.50, cr * 0.70), rot(sg * cr * 0.30, cr * 0.64)]
        pygame.draw.polygon(surf, PATINA, [(int(x), int(y)) for x, y in streak])
        pygame.draw.polygon(surf, PATINA_D, [(int(x), int(y)) for x, y in streak], ow_thin)
    # heavy BLOOM — a cranium crust patch (the most-bloomed skulls only)
    if e["bloom"]:
        bx, by = rot(-cr * 0.10, -cr * ch * 0.34)
        verdigris_bloom(surf, int(bx), int(by), int(cr * 0.40), s, spread=1.0)
    # patina PITTING — scattered matte flecks bitten into the cranium
    if e["pit"]:
        for (px, py) in ((-0.30, -0.30), (0.32, -0.20), (0.10, 0.04), (-0.46, 0.20)):
            fx, fy = rot(px * cr, py * cr)
            pygame.draw.circle(surf, PATINA_D, (int(fx), int(fy)), max(1, int(0.9 * s)))
            pygame.draw.circle(surf, PATINA, (int(fx), int(fy)), max(1, int(0.6 * s)))

    # cranial SUTURE — per-profile, riding the crown seam (the carved-bone read).
    # WHY studs go PATINA: when `eros.studs` is set the seam-nodes are green
    # verdigris suture-studs (oxidised metal pins) instead of the bone/bronze dots.
    seam_dot = PATINA if e["studs"] else BONE_DD
    stud_col = PATINA_D if e["studs"] else GOLD
    if p["sut"] == "zig":
        zp = []
        for j in range(5):
            zx = -cr * 0.34 + j * (cr * 0.68 / 4)
            zy = -cr * ch * 0.62 + (cr * 0.10 if j % 2 else -cr * 0.06)
            zp.append(rot(zx, zy))
        pygame.draw.lines(surf, BONE_DD, False, [(int(x), int(y)) for x, y in zp], ow_thin)
        if e["studs"]:    # verdigris studs punctuating the zigzag seam
            for (zx, zy) in (zp[0], zp[2], zp[4]):
                pygame.draw.circle(surf, PATINA, (int(zx), int(zy)), max(1, int(0.9 * s)))
    elif p["sut"] == "dots":
        for j in range(5):
            zx = -cr * 0.34 + j * (cr * 0.68 / 4)
            dx, dy = rot(zx, -cr * ch * 0.60)
            pygame.draw.circle(surf, seam_dot, (int(dx), int(dy)), max(1, int(0.9 * s)))
            if j % 2 == 0:    # alt nodes: verdigris stud (oxidised) or bronze pip
                gx, gy = rot(zx, -cr * ch * 0.60)
                pygame.draw.circle(surf, stud_col, (int(gx), int(gy)), max(1, int(0.8 * s)))
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

    # ── deep ink sockets with a CARVED rim — patina EATS one rim's silhouette ──
    # WHY the eaten socket alters the OUTLINE: fine crust is hero-only, so the
    # weathering must read at 32px — a patina-eaten socket pushes a dark verdigris
    # bite OUTSIDE the round rim, breaking the clean circle (a silhouette change),
    # not just a tint. `crust` instead creeps a softer patina lip in from one edge.
    socket_r = cr * 0.30
    for sgn in (-1, 1):
        ecx, ecy = rot(sgn * cr * 0.40, cr * 0.14)
        ecx, ecy = int(ecx), int(ecy)
        # a patina-EATEN socket: a verdigris crust bite that overruns the rim edge,
        # breaking the clean round socket — a SILHOUETTE change that reads at 32px.
        if e["eaten"] == sgn:
            bxe = ecx + int(sgn * socket_r * 0.55)
            bye = ecy - int(socket_r * 0.30)
            pygame.draw.circle(surf, PATINA_D, (bxe, bye), int(socket_r * 1.18))
            pygame.draw.circle(surf, PATINA, (bxe, bye), int(socket_r * 0.72))
        # carved bone rim (a ring) then the deep ink pit. WHY the rim follows `tone`:
        # the darker/older relics carry MORE-shadowed sockets (a near-INK rim + a
        # slightly wider pit) so their value reads deeper than the clean light relics.
        rim_col = lerp(BONE_D, BONE_DD, 0.7) if tone < 0 else BONE_D
        socket_grow = 1.18 if tone < 0 else 1.0
        pygame.draw.circle(surf, rim_col, (ecx, ecy), int(socket_r + max(1, 1.2 * s)))
        pygame.draw.circle(surf, INK, (ecx, ecy), int(socket_r * socket_grow))
        pygame.draw.circle(surf, BONE_DD, (ecx, ecy), int(socket_r * 0.62))
        pygame.draw.circle(surf, INK, (ecx, ecy), int(socket_r * 0.34))
        # a softer crust LIP creeping in from one socket edge (value, stays inside)
        if e["crust"] == sgn:
            lip = ecx + int(sgn * socket_r * 0.66)
            pygame.draw.circle(surf, PATINA, (lip, ecy + int(socket_r * 0.22)),
                               max(1, int(socket_r * 0.46)))
            pygame.draw.circle(surf, PATINA_D, (lip, ecy + int(socket_r * 0.22)),
                               max(1, int(socket_r * 0.46)), max(1, int(0.8 * s)))
        # heavy BLOOM rings BOTH sockets (the most-bloomed skulls)
        if e["bloom"]:
            pygame.draw.circle(surf, PATINA, (ecx, ecy),
                               int(socket_r + max(2, 2.0 * s)), max(1, int(1.6 * s)))
            pygame.draw.circle(surf, PATINA_BR,
                               (ecx - int(socket_r * 0.5), ecy - int(socket_r * 0.5)),
                               max(1, int(0.9 * s)))
    # a profile may bloom ONE socket with the matte verdigris inlay (oxidised eye)
    if p["gem"] == "socket":
        scx2, scy2 = rot(-cr * 0.40, cr * 0.14)
        palm_cabochon(surf, (scx2, scy2), max(2, int(socket_r * 0.66)), s)

    # nasal aperture — an inverted ink teardrop between/below the sockets
    n_top = rot(0, cr * 0.30)
    n_l = rot(-cr * 0.16, cr * 0.58)
    n_r = rot(cr * 0.16, cr * 0.58)
    pygame.draw.polygon(surf, INK, [(int(n_top[0]), int(n_top[1])),
                                    (int(n_l[0]), int(n_l[1])),
                                    (int(n_r[0]), int(n_r[1]))])

    # ── jaw — per-profile: closed bar / agape gap / cracked-off stub ──
    jl, jr = -cr * 0.40, cr * 0.40       # jaw corners under the cheeks
    if p["jaw"] == "closed":
        jaw = [rot(jl, cr * 0.74), rot(jr, cr * 0.74),
               rot(jr * 0.70, cr * 1.04), rot(jl * 0.70, cr * 1.04)]
        triad_blob(surf, skull_bone, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        teeth_y0, teeth_y1 = cr * 0.74, cr * 1.00
    elif p["jaw"] == "agape":
        # an open mouth: a dark gap, then a dropped jaw bone below it
        gap = [rot(jl * 0.86, cr * 0.70), rot(jr * 0.86, cr * 0.70),
               rot(jr * 0.70, cr * 1.06), rot(jl * 0.70, cr * 1.06)]
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in gap])
        jaw = [rot(jl * 0.74, cr * 1.06), rot(jr * 0.74, cr * 1.06),
               rot(jr * 0.54, cr * 1.34), rot(jl * 0.54, cr * 1.34)]
        triad_blob(surf, skull_bone, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        teeth_y0, teeth_y1 = cr * 0.70, cr * 0.94   # upper teeth ring the gap
    else:   # "cracked" — one jaw corner snapped off, leaving an asymmetric stub
        jaw = [rot(jl, cr * 0.74), rot(jr * 0.55, cr * 0.74),
               rot(jr * 0.20, cr * 1.02), rot(jl * 0.78, cr * 1.06)]
        triad_blob(surf, skull_bone, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        # a jagged break notch on the snapped (right) corner
        pygame.draw.line(surf, BONE_DD,
                         (int(rot(jr * 0.55, cr * 0.76)[0]), int(rot(jr * 0.55, cr * 0.76)[1])),
                         (int(rot(jr * 0.30, cr * 0.98)[0]), int(rot(jr * 0.30, cr * 0.98)[1])),
                         ow_thin)
        teeth_y0, teeth_y1 = cr * 0.74, cr * 1.00

    # tooth row — n_teeth ink slits; the chipped profiles drop one for a gap
    nt = p["teeth"]
    for j in range(nt):
        fx = -cr * 0.34 + j * (cr * 0.68 / max(1, nt - 1))
        if p["chip"] and j == nt // 2:
            continue   # a missing/knocked-out tooth (the chip)
        tp0 = rot(fx, teeth_y0)
        tp1 = rot(fx, teeth_y1)
        pygame.draw.line(surf, INK, (int(tp0[0]), int(tp0[1])),
                         (int(tp1[0]), int(tp1[1])), max(1, int(1.0 * s)))

    # ── brow BLOOM — matte verdigris inlay for the bloom-bearing profiles ──
    # WHY not icy: skull-cyan is oxidised bloom, never the crisp faceted gem; this
    # caps dim (PATINA), keeping the two hero gems the brightest/crispest cyan.
    if p["gem"] is True:
        gx, gy = rot(0, -cr * 0.20)
        palm_cabochon(surf, (gx, gy), max(2, int(cr * 0.26)), s)


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
    # DARK CONTOUR RING around the WHOLE stone — drawn even when `show_bg` is off
    # (both icy gems sit seat-less). WHY: on the BRIGHT cyan DAY sky both cyan gems
    # share the sky's hue AND value and dissolve into it; a thick near-INK girdle
    # outline separates the stone from the sky by VALUE so the hero reads as the
    # unambiguous focal at 32px, not a faint same-hue smear on the field.
    ink_ring = max(2, int(2.2 * s))
    pygame.draw.polygon(surf, INK, girdle, ink_ring)
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

    # HARD specular glints — tiny TRIANGLES pinned at facet corners. WHY the colour
    # is gated on `show_hot`: only the necklace HERO gem (hot core on) may emit a
    # PURE-WHITE pixel; the brow third-eye (`show_hot` off) gets a soft cyan-white
    # glint instead, so the hero gem stays the SOLE pure-white pixel of the sprite
    # and the value ladder reads cleanly (hero > third-eye > bone > bloom).
    glint_col = (255, 255, 255) if show_hot else (210, 238, 245)

    def glint(px, py, sz):
        pygame.draw.polygon(surf, glint_col,
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
    # big round sockets — scary-cute, kept dim. The socket-glow is MATTE verdigris
    # bloom (oxidised, not icy): the unearthed figure's own sockets are part of the
    # oxidised court, so the ONLY crisp icy cyan on the head is the third-eye gem.
    # One socket carries a creeping crust lip (a faint silhouette bite) so the hero
    # head itself reads as centuries-dug. The two icy gems stay the brightest cyan.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.10)
        if sgn == 1:    # patina crust creeping over the right socket's outer rim
            pygame.draw.circle(surf, PATINA_D, (ex + int(hr * 0.18), ey - int(hr * 0.10)),
                               int(hr * 0.16))
            pygame.draw.circle(surf, PATINA, (ex + int(hr * 0.18), ey - int(hr * 0.10)),
                               int(hr * 0.09))
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.26))
        pygame.draw.circle(surf, PATINA, (ex + sgn * int(1 * s), ey + int(1 * s)), int(hr * 0.10))
        pygame.draw.circle(surf, PATINA_BR, (ex - int(hr * 0.04), ey - int(hr * 0.04)),
                           max(1, int(hr * 0.04)))
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
    # the wide 6-skull arc sweeps above it in open sky. Crown skulls = cool ancient
    # bone, the dimmest value tier; only the centre skull carries a matte verdigris glow.

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
    # three verdigris brow-studs set into the band (oxidised ornament — NOT icy):
    # the bezel-set court is all patina, so only the third-eye + necklace gem stay cyan.
    for i in range(3):
        a = math.radians(232 + i * 38)
        bx = head_c[0] + math.cos(a) * int(hr * 0.98)
        by = head_c[1] + math.sin(a) * int(hr * 0.98)
        triad_circle(surf, PATINA, (int(bx), int(by)), max(1, int(2.4 * s)),
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
    sheet.blit(font_big.render("ASTHI v4 — VERDIGRIS-RELIQUARY", True, LABEL), (24, 13))
    sheet.blit(f_sm.render(
        "dug-up centuries-old Asthi in AGED TEMPLE BRONZE gone VERDIGRIS · 12 differently-ERODED skulls · matte oxidised skull-bloom · ICY hero gem + third-eye vs oxidised court · round 2",
        True, LABEL_DIM), (270, 28))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(380, 540, 188, 296, 2.05)
    sheet.blit(hero, (14, 92))
    sheet.blit(f.render("Creature — hero", True, LABEL), (120, 636))
    sheet.blit(f_sm.render("Cocked-hip DANCE under a six-arm radial fan; each of the 6 open palms cradles", True, LABEL_DIM), (14, 660))
    sheet.blit(f_sm.render("a tiny skull. Fused crown = Mukha tiara-band on the brow + wide airy 6-skull arc.", True, LABEL_DIM), (14, 676))
    sheet.blit(f_sm.render("Bead-lattice over every surface; gold spacer-pips carry the texture (not cyan-on-blue).", True, LABEL_DIM), (14, 692))
    sheet.blit(f_sm.render("Ladder: ICY necklace hero gem (white core) > ICY third-eye > bone > matte verdigris bloom (DIM, no white core).", True, LABEL_DIM), (14, 708))

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
        (BONE, "ancient bone (LIGHT)"), (BONE_D, "bone shade (cool)"),
        (GOLD, "aged bronze"), (GOLD_BR, "burnished bronze"),
        (PATINA, "verdigris patina"), (PATINA_D, "verdigris crust"),
        (CYAN, "ICY hero gem"), (CYAN_BR, "hero white-core"),
        (CROWN_BONE, "crown ancient-bone"), (INK, "ink keyline"),
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
