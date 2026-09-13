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

Value ladder (AD hard rule): cyan third-eye slit = single brightest pixel → the
six palm-skulls = mid → crown skulls = dimmest. Glow ONLY on the third-eye + the
crown-centre skull.

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
BONE      = (212, 202, 186)   # warm aged ivory-bone (the dominant LIGHT field)
BONE_D    = (158, 148, 130)   # bone shade / mid-core
BONE_DD   = ( 96,  88,  76)   # deepest bone hollow (sockets, rib gaps) — stays dark
BONE_SH   = (240, 234, 222)   # bone top-left rim-sheen (warm near-white)
# Beads pushed BRIGHTER + cooler-neutral than the warm bone field so the lattice
# reads as its own value step on the now-light bone (a pale highlight chain), with
# the gold pips carrying the hue contrast.
BEAD      = (236, 232, 224)   # pale bone bead — a value step above the warm field
BEAD_BR   = (252, 250, 246)   # bead top sheen / hottest bone bead
CYAN      = ( 86, 214, 226)   # icy-cyan — third-eye + sparse jewel cabochons
CYAN_BR   = (188, 248, 252)   # hot cyan inner
CYAN_D    = ( 40, 132, 150)
GOLD      = (212, 162,  60)   # WARM gold spacer-pips (the hue separator on ivory)
GOLD_BR   = (246, 208, 110)
GOLD_D    = (158, 112,  40)
INK       = ( 28,  22,  26)   # hard ink keyline
# crown skulls go a touch DARKER + cooler than the now-warm-light body so they
# don't melt into the body OR wash out on the day sky; they stay the dimmest tier.
CROWN_BONE   = (170, 162, 152)
CROWN_BONE_D = (110, 104,  96)
CROWN_SH     = (206, 200, 190)
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
    """Tiny crown skull — a singing relic in the ANCESTOR-CHOIR, seated in her tiara
    arc. WHY a notch darker/cooler than the warm-light body (CROWN_BONE): against the
    warm ivory body an equally-warm crown would melt in, so the crown sits a value
    step down (the dimmest tier) and slightly cooler to keep its shape against both
    body and sky. WHY `idx`: the six crown relics complete the 12-voice choir, each a
    DISTINCT singer — so `idx` drives the CRANIUM SILHOUETTE (tall / round / squat /
    lopsided / heart-domed), head BOW, LID droop, and the open singing-mouth openness
    (parted / open / wide). They share the version's chant grammar with the palm
    skulls: LIDDED half-closed downcast sockets (NO round staring pits) and a soft
    rounded AGAPE 'O' mouth with NO fangs and NO cracks. Cyan pools FLAT + DIM inside
    the lidded sockets; the crown-CENTRE relic (`lit`) carries the fuller
    CYAN->CYAN_BR-rim socket pool — the only crown cyan accent — but stays the DIMMEST
    tier (no white core, no glow, no brightness bump), clearly below the gems."""
    ow1 = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── per-relic choir table — the variety must read in the SHAPE + the chant ──
    # cw/ch = dome width/height · lean = sideways skew of the dome · heart = a
    # notched/dimpled crown top · bow = head tilt (rad) · lid = crescent-lid droop ·
    # mouth = singing-jaw openness (parted / open / wide) · sut = crown-seam style.
    # WHY no adjacent repeats + a per-relic ornament: the AD flagged the crown band
    # repeating two molds and a copy-pasted orange bead in the same spot on two
    # heads. Every relic now varies across mouth + lid + bow + dome silhouette, no
    # two ADJACENT relics share the same mouth+lid pair, and `gem` places ONE small
    # warm bead-ornament at a per-singer spot (or none) so the detail never twins.
    CROWN_PROFILE = [
        # 0: TALL narrow dome bowed left, lips softly PARTED, full lid, dotted seam
        dict(cw=0.86, ch=1.20, lean=0.00, heart=False, bow=-0.14, lid=0.86, mouth="parted", sut="dots", gem="brow-l"),
        # 1: broad ROUND dome upright, OVAL open mid-note, half-crescent lid, zigzag
        dict(cw=1.18, ch=0.94, lean=0.04, heart=False, bow= 0.06, lid=0.50, mouth="open",   sut="zig",  gem="temple-r"),
        # 2: SQUAT heart-domed CENTRE (lit, the loudest), WIDE held-'O', heavy lid
        dict(cw=1.12, ch=0.86, lean=0.00, heart=True,  bow= 0.00, lid=0.92, mouth="wide",   sut="dots", gem="crown"),
        # 3: LOPSIDED dome leaning right chin-down, nearly-closed HUM, barely-open lid
        dict(cw=1.02, ch=1.00, lean=0.20, heart=False, bow= 0.18, lid=0.28, mouth="hum",    sut="zig",  gem=None),
        # 4: HEART-domed bowed left, OVAL open, full lid, line seam
        dict(cw=1.00, ch=1.08, lean=-0.08, heart=True, bow=-0.08, lid=0.82, mouth="open",   sut="line", gem="brow-r"),
        # 5: lopsided SQUAT dome leaning left, lips softly PARTED, half-crescent lid
        dict(cw=1.10, ch=0.90, lean=-0.20, heart=False, bow=-0.18, lid=0.58, mouth="parted", sut="zig", gem="temple-l"),
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

    # head BOW — the face features rotate about the relic centre so the singer can
    # bow / cock its head; the dome keeps its lean-based silhouette above.
    bow = p["bow"]
    cbw, sbw = math.cos(bow), math.sin(bow)

    def rotc(dx, dy):
        return (cx + dx * cbw - dy * sbw, cy + dx * sbw + dy * cbw)

    # ── LIDDED crescent sockets — same downcast devotional gaze as the palm choir ──
    # A heavy bone lid hoods each socket from above; a faint flat cyan pool sits at
    # the downcast (lower-inner) edge. The lit centre relic gets the fuller
    # CYAN->CYAN_BR-rim pool (the only crown cyan accent), still the dimmest tier.
    sr = max(2, int(r * 0.26))
    lid = p["lid"]
    for sgn in (-1, 1):
        ex, ey = rotc(sgn * r * 0.38, r * 0.06)
        ex, ey = int(ex), int(ey)
        pygame.draw.circle(surf, CROWN_BONE_D, (ex, ey), int(sr + max(1, 1.0 * s)))
        pygame.draw.circle(surf, INK, (ex, ey), sr)
        gaze_dx = -sgn * sr * 0.30
        gaze_dy = sr * 0.34
        # the lit crown-CENTRE relic carries the third of the 3-up cyan beat —
        # landed (bigger CYAN core + clear CYAN_BR rim) so it reads against its dim
        # band siblings, yet still the DIMMEST tier (no white core, no glow).
        if lit:
            pygame.draw.circle(surf, CYAN_D, (int(ex + gaze_dx), int(ey + gaze_dy)), max(1, int(sr * 0.66)))
            pygame.draw.circle(surf, CYAN, (int(ex + gaze_dx), int(ey + gaze_dy)), max(1, int(sr * 0.48)))
            pygame.draw.circle(surf, CYAN_BR, (int(ex + gaze_dx), int(ey + gaze_dy)), max(1, int(sr * 0.24)))
        else:
            pygame.draw.circle(surf, CYAN_D, (int(ex + gaze_dx), int(ey + gaze_dy)), max(1, int(sr * 0.38)))
            pygame.draw.circle(surf, CYAN, (int(ex + gaze_dx), int(ey + gaze_dy)), max(1, int(sr * 0.18)))
        lid_drop = sr * (0.20 + 0.62 * lid)
        lc = rotc(sgn * r * 0.38, r * 0.06 - sr + lid_drop)
        pygame.draw.circle(surf, CROWN_BONE, (int(lc[0]), int(lc[1])), int(sr + max(1, 1.0 * s)))

    # nasal pit (between + below the sockets, bowed with the head)
    np_c = rotc(0, r * 0.40)
    pygame.draw.circle(surf, INK, (int(np_c[0]), int(np_c[1])), max(1, int(r * 0.12)))

    # ── singing AGAPE mouth — the open 'O', NO fangs and NO cracks (chant grammar) ──
    if p["mouth"] == "hum":
        mw, mh = r * 0.22, r * 0.09
    elif p["mouth"] == "parted":
        mw, mh = r * 0.26, r * 0.16
    elif p["mouth"] == "open":
        mw, mh = r * 0.32, r * 0.26
    else:   # "wide" — the held note
        mw, mh = r * 0.38, r * 0.38
    my0 = r * 0.76
    cavity = [rotc(math.cos(math.radians(ad)) * mw, my0 + math.sin(math.radians(ad)) * mh)
              for ad in range(0, 360, 36)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in cavity])
    pygame.draw.polygon(surf, CROWN_BONE_D, [(int(x), int(y)) for x, y in cavity], ow_thin)
    # 1px warm-ivory inner LIP on the TOP edge so the open void reads as a lit open
    # mouth (upper lip) not a punched hole — vital on the top-centre crown heads.
    top_lip = [rotc(math.cos(math.radians(ad)) * mw * 0.92, my0 + math.sin(math.radians(ad)) * mh * 0.92)
               for ad in range(200, 341, 28)]
    if len(top_lip) >= 2:
        pygame.draw.lines(surf, CROWN_SH, False,
                          [(int(x), int(y)) for x, y in top_lip], max(1, int(1.0 * s)))
    # thin bone chin arc cupping the lower lip so the open mouth still reads as bone
    chin = [rotc(math.cos(math.radians(ad)) * (mw + r * 0.12),
                 my0 + math.sin(math.radians(ad)) * (mh + r * 0.16))
            for ad in range(20, 161, 35)]
    chin.append(rotc(mw + r * 0.06, my0 + mh * 0.20))
    chin.append(rotc(-mw - r * 0.06, my0 + mh * 0.20))
    triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in chin], ow=max(1, int(1.0 * s)))

    # ── per-singer warm bead-ornament — de-dupes the old copy-pasted orange bead ──
    # WHY one placement per relic (or none): the AD flagged the same orange bead in
    # the same spot on two crown heads as a copy-paste tell. Each relic now seats ONE
    # tiny warm-gold pip at its OWN landmark (a brow corner / temple / crown apex), so
    # the detail reads as individual jewel-set bone, never twins. The dim/centre
    # relics carry it on the crown apex; others tuck it at an off-centre brow/temple.
    gem = p["gem"]
    gem_xy = None
    if gem == "brow-l":
        gem_xy = rotc(-r * 0.30, -r * 0.04)
    elif gem == "brow-r":
        gem_xy = rotc(r * 0.30, -r * 0.04)
    elif gem == "temple-l":
        gem_xy = rotc(-r * 0.46, -r * 0.30)
    elif gem == "temple-r":
        gem_xy = rotc(r * 0.46, -r * 0.30)
    elif gem == "crown":
        gem_xy = rotc(0, -r * ch * 0.84)
    if gem_xy is not None:
        gx, gy = int(gem_xy[0]), int(gem_xy[1])
        pygame.draw.circle(surf, GOLD_D, (gx, gy), max(1, int(1.1 * s)))
        pygame.draw.circle(surf, GOLD, (gx, gy), max(1, int(0.8 * s)))
        pygame.draw.circle(surf, GOLD_BR, (gx, gy), max(1, int(0.4 * s)))


# ── a tiny singing skull cradled in an open palm (the choir MOTIF) ────────────
def palm_skull(surf, cx, cy, r, s, idx=0, lit=False):
    """An open BONE palm cradling a singing reliquary skull — one voice in the
    ANCESTOR-CHOIR. WHY this grammar: the defining move of this version is the
    CHANT, not a grin or a snarl. So every palm-skull holds a soft ROUNDED-AGAPE
    'singing' jaw (an open mouth, NO fangs and NO cracks) paired with LIDDED,
    half-closed crescent sockets whose gaze falls inward + downward — devotional,
    mid-hymn. The open jaw is a SILHOUETTE move: a rounded 'O' notched out of the
    lower face survives the 32px downscale and is what separates this brood from a
    gentle/auspicious read. WHY `idx`: the six must read as six DISTINCT singers,
    not one dome re-tilted — so `idx` drives the head BOW (tilt), dome width/height,
    LID droop, MOUTH openness (softly parted → wide rounded 'O'), suture pattern,
    and how much cyan pools in the sockets. The cyan is drawn FLAT and DIM, pooled
    INSIDE the lidded sockets as a gentle inner gaze-light — never a hot core, never
    out-glowing the gems. ~2 of the six (the brief lights the two LOWEST palm skulls)
    carry a fuller CYAN->CYAN_BR-rim socket pool, 'lit from within'. MID value tier:
    pale BEAD bone, brighter than the crown skulls, dimmer than the third-eye."""
    ow1 = max(1, int(1.4 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── per-singer choir table (six genuinely distinct chanting skulls) ──
    # tilt = head BOW (rad) · cw/ch = dome width/height · lid = crescent-lid droop
    # (0 a thin slit, 1 a deep downcast hood) · mouth = singing-jaw openness mode
    # (hum / parted / open / wide) · sut = crown-seam style. The inner cyan socket-
    # pool strength is NOT in the table — `lit` (the two LOWEST palm skulls) drives
    # the fuller pool, so it stays position-weighted regardless of which idx lands
    # low. WHY four mouth modes + four lid bands: the AD flagged "one face per row,
    # mirrored" — so every entry now varies across mouth + lid + bow + dome, and NO
    # two adjacent palm singers share the same mouth+lid pair (the choir is twelve
    # individuals mid-hymn, not one mold re-tilted).
    PROFILE = [
        # 0: tall dome bowed left, lips softly PARTED (first breath), full lid, zig
        dict(tilt=-0.18, cw=0.94, ch=1.18, lid=0.88, mouth="parted", sut="zig"),
        # 1: broad upright dome, OVAL open mid-note, half-crescent lid, bead-dots
        dict(tilt= 0.05, cw=1.18, ch=0.94, lid=0.52, mouth="open",   sut="dots"),
        # 2: narrow head bowed deep, WIDE held-'O', heavy lid (the loud one), zig
        dict(tilt=-0.30, cw=0.86, ch=1.08, lid=0.94, mouth="wide",   sut="zig"),
        # 3: squat lopsided dome, nearly-closed HUM, barely-open lid, line seam
        dict(tilt= 0.12, cw=1.10, ch=0.88, lid=0.30, mouth="hum",    sut="line"),
        # 4: tall head bowed right, OVAL open, full lid, dotted seam
        dict(tilt= 0.26, cw=0.90, ch=1.14, lid=0.82, mouth="open",   sut="dots"),
        # 5: rounder dome chin-down, lips softly PARTED, half-crescent lid, zig
        dict(tilt=-0.06, cw=1.06, ch=1.02, lid=0.60, mouth="parted", sut="zig"),
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

    # ── LIDDED crescent sockets — the devotional half-closed downcast gaze ──
    # WHY a half-moon, not a round pit: the chant reads as much in the EYES as the
    # mouth. A heavy bone lid hoods each socket from above, leaving a downcast
    # crescent of dark below it; the gaze falls inward + downward. A faint flat cyan
    # pool sits at the bottom of the crescent as a gentle inner gaze-light (DIM, no
    # rim glint); the two LIT singers get a fuller CYAN->CYAN_BR-rim pool, lit from
    # within but still clearly below the gems.
    socket_r = cr * 0.32
    lid = p["lid"]
    for sgn in (-1, 1):
        ecx, ecy = rot(sgn * cr * 0.40, cr * 0.16)
        ecx, ecy = int(ecx), int(ecy)
        sr = int(socket_r)
        # carved bone rim, then the full ink pit (the open part of the socket)
        pygame.draw.circle(surf, BONE_D, (ecx, ecy), int(sr + max(1, 1.2 * s)))
        pygame.draw.circle(surf, INK, (ecx, ecy), sr)
        # the inner cyan gaze-pool — pooled flat at the DOWNCAST (lower-inner) edge
        gaze_dx = -sgn * sr * 0.30                      # cast inward, toward midline
        gaze_dy = sr * 0.34                             # and downward (devotional)
        # WHY the lit pool is now visibly hotter: the AD called the 3-up cyan beat
        # (crown-centre + the two LOWEST palms) a phantom claim — invisible at hero
        # scale. The lit pool is LANDED: a bigger CYAN core plus a clear CYAN_BR rim
        # so the two lowest palms read distinctly brighter than their four siblings,
        # while staying capped below the gems (no white-hot core lives here).
        if lit:
            pygame.draw.circle(surf, CYAN_D, (int(ecx + gaze_dx), int(ecy + gaze_dy)),
                               max(1, int(sr * 0.68)))
            pygame.draw.circle(surf, CYAN, (int(ecx + gaze_dx), int(ecy + gaze_dy)),
                               max(1, int(sr * 0.50)))
            pygame.draw.circle(surf, CYAN_BR, (int(ecx + gaze_dx), int(ecy + gaze_dy)),
                               max(1, int(sr * 0.26)))
        else:
            pygame.draw.circle(surf, CYAN_D, (int(ecx + gaze_dx), int(ecy + gaze_dy)),
                               max(1, int(sr * 0.42)))
            pygame.draw.circle(surf, CYAN, (int(ecx + gaze_dx), int(ecy + gaze_dy)),
                               max(1, int(sr * 0.20)))
        # the heavy bone LID hooding the socket from above — a filled crescent that
        # eats the top of the pit, leaving only a downcast sliver of gaze below it.
        lid_drop = sr * (0.20 + 0.62 * lid)             # deeper lid = more covered
        lid_c = (ecx, int(ecy - sr + lid_drop))
        pygame.draw.circle(surf, BEAD, lid_c, int(sr + max(1, 1.0 * s)))
        # a thin dark lash-line under the lid edge so the lid reads as a closing lid
        lash_y = int(ecy - sr + lid_drop + sr * 0.02)
        pygame.draw.line(surf, BONE_DD, (int(ecx - sr * 0.78), lash_y),
                         (int(ecx + sr * 0.78), lash_y), max(1, int(0.9 * s)))

    # nasal aperture — an inverted ink teardrop between/below the sockets
    n_top = rot(0, cr * 0.30)
    n_l = rot(-cr * 0.16, cr * 0.58)
    n_r = rot(cr * 0.16, cr * 0.58)
    pygame.draw.polygon(surf, INK, [(int(n_top[0]), int(n_top[1])),
                                    (int(n_l[0]), int(n_l[1])),
                                    (int(n_r[0]), int(n_r[1]))])

    # ── singing AGAPE jaw — the open 'O' mouth that carries the chant ──
    # WHY a smooth rounded opening, NO fangs and NO cracks: the chant must read as
    # devotional song, not a snarl, and the soft 'O' is the SILHOUETTE move that
    # survives 32px. Four openings: a nearly-closed HUM slit, a small softly-PARTED
    # oval, a mid OPEN oval, a WIDE held-note 'O'. The dark oval is the cavity; a
    # thin dropped jaw-bone arc rings its lower edge so the open mouth still reads as
    # bone, not a hole. NO tooth slits anywhere — the chant grammar is fangless.
    if p["mouth"] == "hum":
        mw, mh, my0 = cr * 0.26, cr * 0.10, cr * 0.78
    elif p["mouth"] == "parted":
        mw, mh, my0 = cr * 0.30, cr * 0.18, cr * 0.78
    elif p["mouth"] == "open":
        mw, mh, my0 = cr * 0.36, cr * 0.30, cr * 0.80
    else:   # "wide" — the held note, the widest agape 'O'
        mw, mh, my0 = cr * 0.42, cr * 0.44, cr * 0.82
    # the dark singing cavity as a rounded polygon-oval (rotated with the head bow)
    cavity = []
    for ad in range(0, 360, 30):
        a = math.radians(ad)
        cavity.append(rot(math.cos(a) * mw, my0 + math.sin(a) * mh))
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in cavity])
    pygame.draw.polygon(surf, BONE_DD, [(int(x), int(y)) for x, y in cavity], ow_thin)
    # WHY a 1px warm-ivory inner LIP on the TOP edge: the AD flagged some open mouths
    # reading as punched-out holes. A bright bone rim hugging the upper arc of the
    # cavity reads as the lit inside of an OPEN mouth (the upper lip catching light),
    # not a void. Drawn before the chin arc so the lower jaw still cups it.
    top_lip = []
    for ad in range(200, 341, 28):
        a = math.radians(ad)
        top_lip.append(rot(math.cos(a) * mw * 0.92, my0 + math.sin(a) * mh * 0.92))
    if len(top_lip) >= 2:
        pygame.draw.lines(surf, BEAD_BR, False,
                          [(int(x), int(y)) for x, y in top_lip], max(1, int(1.0 * s)))
    # a thin bone jaw-bone arc cupping the LOWER half of the open mouth (the chin)
    jaw = []
    for ad in range(20, 161, 28):
        a = math.radians(ad)
        jaw.append(rot(math.cos(a) * (mw + cr * 0.16), my0 + math.sin(a) * (mh + cr * 0.18)))
    jaw.append(rot(mw + cr * 0.10, my0 + mh * 0.30))
    jaw.append(rot(-mw - cr * 0.10, my0 + mh * 0.30))
    triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
    # a soft sheen catch on the upper-inner lip so the 'O' rim reads rounded, lit
    lip_l = rot(-mw * 0.6, my0 - mh * 0.55)
    pygame.draw.circle(surf, BEAD_BR, (int(lip_l[0]), int(lip_l[1])), max(1, int(0.9 * s)))


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

    # === SIX SINGING PALM-SKULLS — one cradled in every fan hand (the choir) ====
    # WHY enumerate: each hand gets a DISTINCT `idx` so the six read as six
    # individual singers (dome/bow/lid/mouth vary per idx). WHY the two LOWEST get
    # `lit`: the brief lights the two lowest palm skulls with the fuller
    # CYAN->CYAN_BR-rim socket pool, so the cyan gaze-light reads bottom-weighted —
    # found by the two largest screen-Y hands, not a fixed idx, so it holds whatever
    # scale the fan is drawn at. Still the MID tier — well below the gems.
    lowest = sorted(range(len(hands)), key=lambda i: -hands[i][1])[:2]
    for i, (hx, hy, a) in enumerate(hands):
        palm_skull(surf, hx, hy, int(hr * 0.36), s, idx=i, lit=(i in lowest))

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
    # big round sockets — scary-cute, kept dim (no hot core) so the third-eye wins.
    # WHY the socket pupils are TAMED: the AD flagged the central cyan tying the brow
    # third-eye and muddying the vertical cyan ladder (gem > third-eye > eyes >
    # sockets). The pupils are pulled ~15% toward the dim bone-grey (lower chroma)
    # AND ~15% smaller so the eyes sit cleanly BELOW the third-eye, never level.
    socket_pupil = lerp(CYAN_D, BONE_DD, 0.15)
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.10)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.26))
        pygame.draw.circle(surf, socket_pupil, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           max(1, int(hr * 0.085)))
    # THIRD EYE — the same faceted cyan cut-gem, SMALLER than the necklace hero gem
    # and a step dimmer (no white-hot core), so the necklace gem reads as brightest.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.36)
    cyan_gem(surf, (tex, tey), int(hr * 0.28), s, focal=True, hot=False)
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # === HERO SINGING JAW — the matriarch is the LOUDEST voice in the choir =====
    # WHY no grin, no smile-line, no teeth: the AD noted the lead was SMILING (a
    # railed-teeth grin + an upturned smile-line beneath) while the twelve sang. The
    # matriarch must sing too — and be the widest agape 'O' of all. So the closed
    # grin is replaced with the same fangless chant grammar as the choir, scaled up:
    # a dark rounded singing cavity, a 1px warm-ivory inner LIP on its TOP edge so it
    # reads as an open mouth (not a punched hole), and a bone chin arc cupping the
    # lower lip. NO tooth slits, NO smile-line anywhere.
    mcy = head_c[1] + int(hr * 0.66)
    mw_h, mh_h = hr * 0.40, hr * 0.42
    cavity_h = [(head_c[0] + math.cos(math.radians(ad)) * mw_h,
                 mcy + math.sin(math.radians(ad)) * mh_h) for ad in range(0, 360, 30)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in cavity_h])
    pygame.draw.polygon(surf, BONE_DD, [(int(x), int(y)) for x, y in cavity_h], max(1, int(1.2 * s)))
    top_lip_h = [(head_c[0] + math.cos(math.radians(ad)) * mw_h * 0.9,
                  mcy + math.sin(math.radians(ad)) * mh_h * 0.9) for ad in range(200, 341, 24)]
    pygame.draw.lines(surf, BONE_SH, False,
                      [(int(x), int(y)) for x, y in top_lip_h], max(1, int(1.4 * s)))
    chin_h = [(head_c[0] + math.cos(math.radians(ad)) * (mw_h + hr * 0.10),
               mcy + math.sin(math.radians(ad)) * (mh_h + hr * 0.14)) for ad in range(20, 161, 28)]
    chin_h.append((head_c[0] + mw_h + hr * 0.06, mcy + mh_h * 0.24))
    chin_h.append((head_c[0] - mw_h - hr * 0.06, mcy + mh_h * 0.24))
    triad_blob(surf, BONE, [(int(x), int(y)) for x, y in chin_h], ow=max(1, int(1.2 * s)))

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
    # WHY no brow-cabochons in this version: the cyan accent belongs in the singing
    # skulls' inner gaze-pools, not strewn across the tiara band — the brow band
    # stays a clean gold-bead arc so the cyan ladder reads top-down without clutter.
    bead_arc(surf, head_c[0], head_c[1], int(hr * 0.98), math.radians(214),
             math.radians(326), int(2.6 * s), s, gold_every=3)

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
    Rendered at SS=8 on a large canvas then smoothscaled into the export box
    (round_2_hero.png)."""
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
    sheet.blit(font_big.render("ASTHI v1 — ANCESTOR-CHOIR", True, LABEL), (24, 13))
    sheet.blit(f_sm.render(
        "bone-jewel sky-dancer caught MID-CHANT  ·  12-voice choir: 6 palm + 6 crown singing skulls · lidded downcast eyes + soft rounded AGAPE 'O' jaws (NO fangs/cracks) · WARM aged-bone + gold pips",
        True, LABEL_DIM), (270, 28))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(380, 540, 188, 296, 2.05)
    sheet.blit(hero, (14, 92))
    sheet.blit(f.render("Creature — hero", True, LABEL), (120, 636))
    sheet.blit(f_sm.render("Cocked-hip DANCE under a six-arm radial fan; 6 palm + 6 crown skulls form a 12-voice", True, LABEL_DIM), (14, 660))
    sheet.blit(f_sm.render("CHOIR caught mid-chant: lidded half-closed downcast eyes + soft rounded AGAPE 'O' jaws.", True, LABEL_DIM), (14, 676))
    sheet.blit(f_sm.render("NO fangs, NO cracks. Cyan pools FLAT + DIM inside the sockets as inner gaze-light;", True, LABEL_DIM), (14, 692))
    sheet.blit(f_sm.render("ladder: HERO necklace gem (white core) > dim brow third-eye > skull socket-cyan dimmest.", True, LABEL_DIM), (14, 708))

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
        (BONE, "warm bone (LIGHT)"), (BONE_D, "bone shade"),
        (BEAD, "bone bead (light)"), (BEAD_BR, "bead sheen"),
        (GOLD, "gold spacer-pip"), (GOLD_BR, "gold sheen"),
        (CYAN, "icy-cyan focal"), (CROWN_BONE, "crown-warm bone"),
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
