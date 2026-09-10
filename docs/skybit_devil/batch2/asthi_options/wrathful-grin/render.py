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
def crown_skull(surf, cx, cy, r, s, lit=False, idx=0, nudge=False):
    """Tiny crown skull — WRATHFUL charnel relic seated in her tiara arc. WHY a
    notch darker/cooler than the warm-light body (CROWN_BONE): against the warm ivory
    body, an equally-warm crown would melt in, so the crown sits a value step down
    (the dimmest tier) and slightly cooler to keep its shape against both body and
    sky. WHY `idx`: the six crown relics share the palm-skulls' ONE bared-fangs
    language at varying intensity — 2 rictus (jaw CLOSED, clenched fang row), 2 snarl
    (partly dropped), 2 roar (jaw torn WELL below the cranium, agape void, fangs top +
    bottom) — and `idx` also drives cranium PROPORTION (narrow-tall / squat / leaning),
    brow angle, fang count, crack side and SILHOUETTE-altering damage (caved temple /
    broken crest / sheared jaw / knocked fang), so the arc reads as six individual
    screamers in pure black at 32px, not one stamp swept six times, and the fury lives
    in the OUTLINE — caved temples, a sheared crest, a lost jaw corner are CARVED out
    of the cranium edge (bone ABSENT, sky through), not inked on the fill. `lit` is the
    crown-CENTRE relic: it carries MOST cyan wrath-fire (a CYAN ember core + CYAN_BR
    upper glint). `nudge` is the two OUTERMOST fan-tip relics: one value notch up (a
    mid-cyan core, no glint) so the 3-up beat reads at hero scale. All stay the DIMMEST
    tier — NO white core, NO glow, below the brow third-eye; the rest get DIM CYAN_D."""
    ow1 = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── per-relic WRATH table — six distinct fierce crown skulls ──
    # cw/ch = cranium width/height stretch · lean = sideways skew · brow = angry
    # ridge steepness (out/up) · jaw roar mode · fangs · suture · damage · rage 0..1
    # Same single BARED-FANGS grammar as the palm skulls (rictus / snarl / roar),
    # so the 12-strong chorus reads as ONE language at varying intensity. Crown
    # spread: 2 rictus · 2 snarl · 2 roar.
    # WHY the cw/ch spread is now AGGRESSIVE (one genuinely tall-narrow, one squat-
    # broad, real asymmetric leans): the crown arc is the rank that sits against open
    # sky and DRIVES the silhouette proof + 32px read. Subtle proportion deltas wash
    # out at downscale, so each dome must contribute a DISTINCT bump to the arc's
    # top edge — a saw-tooth of countable skulls, not one smooth hump. The `dmg`
    # field now names a CONTOUR wound that is CARVED OUT of the cranium edge (bone
    # ABSENT, sky shows through) rather than inked on the fill — see the dome loop.
    CROWN_PROFILE = [
        # 0: GENUINELY TALL-NARROW snarl, forked crack, sheared jaw corner —
        #    a real missing-bone notch in the lower edge. CONTOUR damage.
        dict(cw=0.70, ch=1.34, lean=0.00, brow=0.30, jaw="snarl", fangs=3, sut="crack",
             dmg="jaw_shear", rage=0.66),
        # 1: BROAD full-roar, zig suture, LEFT temple CAVED — a concave bite eaten
        #    into the upper-left dome edge. CONTOUR damage.
        dict(cw=1.22, ch=0.92, lean=0.00, brow=0.32, jaw="roar", fangs=4, sut="zig",
             dmg="temple_cave", rage=0.92),
        # 2: GENUINELY SQUAT-BROAD low dome (CENTRE, lit) — full-roar, crest SHEARED
        #    off in a jagged notch cut from the top, brightest cyan. CONTOUR damage.
        dict(cw=1.30, ch=0.74, lean=0.00, brow=0.34, jaw="roar", fangs=4, sut="zig",
             dmg="crest_break", rage=0.98),
        # 3: STRONG asymmetric RIGHT-lean rictus, forked crack, knocked lower fang —
        #    a real gap bitten into the lower edge. CONTOUR damage.
        dict(cw=1.00, ch=1.06, lean=0.34, brow=0.24, jaw="rictus", fangs=5, sut="crack",
             dmg="fang_knock", rage=0.44),
        # 4: clenched RICTUS, broad squat, faint median, cheek hairline — the ONE
        #    relic kept deliberately SMOOTH / WHOLE in the contour: the intact relic
        #    that makes the broken neighbours count. INTERIOR-only hairline, no
        #    contour wound. low rage.
        dict(cw=1.08, ch=1.00, lean=-0.04, brow=0.20, jaw="rictus", fangs=6, sut="line",
             dmg="cheek_crack", rage=0.36),
        # 5: STRONG asymmetric LEFT-lean snarl, zig suture, RIGHT temple CAVED —
        #    concave bite eaten into the upper-right dome edge. CONTOUR damage.
        dict(cw=1.02, ch=1.00, lean=-0.34, brow=0.28, jaw="snarl", fangs=4, sut="zig",
             dmg="temple_cave_r", rage=0.78),
    ]
    p = CROWN_PROFILE[idx % len(CROWN_PROFILE)]
    cw, ch, lean = p["cw"], p["ch"], p["lean"]
    rage = p["rage"]
    dmg = p["dmg"]

    # cranium as an ink-keyed POLYGON whose CONTOUR carries the damage. WHY 6° steps
    # (was 12°): a sheared crest or a caved temple has to be a CRISP concave bite in
    # the silhouette, and coarse steps round it back into a smooth lump. The damage
    # now MOVES POINTS INWARD (toward the skull centre) and/or DROPS the crown line
    # so bone is genuinely ABSENT there — in the pure-black proof the dome edge caves
    # in / loses its crest / loses a jaw corner, instead of the whole crown reading as
    # one cauliflower lump. Test: if a wound does not change the black edge, it is not
    # a wound. Five of six crown skulls are notched here; idx 4 stays whole.
    dome = []
    for ang_deg in range(-180, 1, 6):      # top half-ring: brow → temples → crown
        a = math.radians(ang_deg)
        rad_w, rad_h = r * cw, r * ch
        dx = math.cos(a) * rad_w
        dy = math.sin(a) * rad_h
        dx += lean * r * (-dy / max(1.0, r))      # shear the dome toward the lean
        # caved LEFT temple — eat a concave bite INTO the upper-left edge: pull the
        # edge points back TOWARD centre (dx less negative) + sink them, so the dome
        # outline dents inward and sky shows through the bite.
        if dmg == "temple_cave" and -2.85 < a < -1.95:
            bite = max(0.0, 1.0 - abs((a + 2.40) / 0.45))
            dx += rad_w * 0.48 * bite; dy += rad_h * 0.20 * bite
        # caved RIGHT temple — mirror bite into the upper-right edge (dx less positive)
        if dmg == "temple_cave_r" and -1.15 < a < -0.25:
            bite = max(0.0, 1.0 - abs((a + 0.70) / 0.45))
            dx -= rad_w * 0.48 * bite; dy += rad_h * 0.20 * bite
        # broken cranium CREST — a jagged chunk SHEARED off the very top: the crown
        # line drops well inward and saw-teeth across the gap (real missing bone)
        if dmg == "crest_break" and -2.05 < a < -1.05:
            notch = 1.0 - abs((a + 1.55) / 0.50)
            saw = 0.55 + 0.45 * math.sin(a * 7.0)
            dy += rad_h * 0.52 * max(0.0, notch) * saw
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

    # cranial SUTURE — zig seam / forked battle-crack / faint median hairline
    seam_y = cy - r * ch * 0.56
    if p["sut"] == "zig":
        zp = [(cx - r * 0.34 + j * (r * 0.68 / 4),
               seam_y + (r * 0.12 if j % 2 else -r * 0.08)) for j in range(5)]
        pygame.draw.lines(surf, CROWN_BONE_D, False,
                          [(int(x), int(y)) for x, y in zp], ow_thin)
    elif p["sut"] == "crack":
        ck = [(cx + r * 0.06, cy - r * ch * 0.74), (cx - r * 0.08, cy - r * ch * 0.36),
              (cx + r * 0.04, cy - r * 0.04)]
        pygame.draw.lines(surf, CROWN_BONE_D, False, [(int(x), int(y)) for x, y in ck], ow_thin)
    else:   # "line" — a single faint median suture (the near-clenched grimace)
        pygame.draw.line(surf, CROWN_BONE_D, (int(cx), int(cy - r * ch * 0.78)),
                         (int(cx), int(cy - r * 0.06)), ow_thin)

    # ── HEAVY angry brow ridges — outward/up wedges over the sockets ──
    # p["brow"] scales the scowl; even a low-rage grimace keeps a slight frown.
    bwf = p["brow"]
    for sgn in (-1, 1):
        bi = (cx + sgn * r * 0.08, cy - r * (0.02 - bwf * 0.36))   # inner low (near nose)
        bo = (cx + sgn * r * 0.52, cy - r * (0.16 + bwf * 0.50))   # outer high (raised)
        bb = (cx + sgn * r * 0.50, cy + r * 0.04)
        bn = (cx + sgn * r * 0.10, cy + r * 0.10)
        triad_blob(surf, CROWN_BONE_D, [(int(bi[0]), int(bi[1])), (int(bo[0]), int(bo[1])),
                                        (int(bb[0]), int(bb[1])), (int(bn[0]), int(bn[1]))],
                   ow=ow_thin)

    # ── BARED-FANGS mouth — same three intensities as the palm skulls ──
    # rictus = jaw CLOSED with a clenched fang row · snarl = partly dropped · roar =
    # torn WELL below the cranium (agape void editing the silhouette).
    mode = p["jaw"]
    nf = p["fangs"]
    jl, jr = -r * 0.44, r * 0.44
    uy = cy + r * 0.44
    ow_f = max(1, int(0.8 * s))

    def c_upfang(fx, length, skip=False):
        if skip:
            return
        tp = (fx, uy + length)
        pygame.draw.polygon(surf, CROWN_BONE, [(int(fx - r * 0.06), int(uy)),
                                               (int(fx + r * 0.06), int(uy)),
                                               (int(tp[0]), int(tp[1]))])
        pygame.draw.polygon(surf, INK, [(int(fx - r * 0.06), int(uy)),
                                        (int(fx + r * 0.06), int(uy)),
                                        (int(tp[0]), int(tp[1]))], ow_f)

    def c_lowfang(fx, baseline, length, skip=False):
        if skip:
            return
        tp = (fx, baseline - length)
        pygame.draw.polygon(surf, CROWN_BONE, [(int(fx - r * 0.06), int(baseline)),
                                               (int(fx + r * 0.06), int(baseline)),
                                               (int(tp[0]), int(tp[1]))])
        pygame.draw.polygon(surf, INK, [(int(fx - r * 0.06), int(baseline)),
                                        (int(fx + r * 0.06), int(baseline)),
                                        (int(tp[0]), int(tp[1]))], ow_f)

    if mode == "rictus":
        # CLOSED clenched grin — a thin dark seam, fangs meeting it edge-to-edge,
        # the jaw tucked right beneath (NOT dropped).
        seam = [(int(cx + jl * 0.90), int(uy + r * 0.10)), (int(cx + jr * 0.90), int(uy + r * 0.10)),
                (int(cx + jr * 0.84), int(uy + r * 0.22)), (int(cx + jl * 0.84), int(uy + r * 0.22))]
        pygame.draw.polygon(surf, INK, seam)
        jy0 = uy + r * 0.22
        if dmg == "fang_knock":
            # knocked-out fang = a real V-notch bitten DEEP into the lower jaw edge,
            # so the silhouette's bottom contour gains a gap (bone absent), not just
            # a missing interior tooth.
            jaw = [(cx + jl * 0.86, jy0), (cx - r * 0.10, jy0 + r * 0.04),
                   (cx, jy0 + r * 0.34), (cx + r * 0.12, jy0 + r * 0.04),
                   (cx + jr * 0.86, jy0),
                   (cx + jr * 0.62, jy0 + r * 0.30), (cx + jl * 0.62, jy0 + r * 0.30)]
        else:
            jaw = [(cx + jl * 0.86, jy0), (cx + jr * 0.86, jy0),
                   (cx + jr * 0.62, jy0 + r * 0.30), (cx + jl * 0.62, jy0 + r * 0.30)]
        triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in jaw], ow=max(1, int(1.0 * s)))
        knock = idx % nf
        for j in range(nf):
            fx = cx - r * 0.36 + j * (r * 0.72 / max(1, nf - 1))
            c_upfang(fx, r * 0.16)
            c_lowfang(fx, jy0 + r * 0.02, r * 0.14,
                      skip=(dmg == "fang_knock" and j == knock))
    else:
        open_amt = (0.30 if mode == "snarl" else 0.70) + rage * 0.16
        drop = r * (0.12 + open_amt)
        void = [(cx + jl * 0.92, uy), (cx + jr * 0.92, uy),
                (cx + jr * 0.80, uy + drop), (cx + jl * 0.80, uy + drop)]
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in void])
        jy0 = uy + drop
        if dmg == "jaw_shear":
            # one whole jaw CORNER sheared clean away — the jaw polygon loses a side,
            # so the silhouette's lower edge is hard-asymmetric (missing bone), not a
            # symmetric chin. The tall-narrow idx-0 relic carries this.
            if idx % 2 == 0:
                jaw = [(cx + jl * 0.86, jy0), (cx + jr * 0.18, jy0),
                       (cx + jl * 0.10, jy0 + r * 0.20), (cx + jl * 0.78, jy0 + r * 0.30)]
            else:
                jaw = [(cx + jl * 0.18, jy0), (cx + jr * 0.86, jy0),
                       (cx + jr * 0.78, jy0 + r * 0.30), (cx + jr * 0.10, jy0 + r * 0.20)]
        else:
            jaw = [(cx + jl * 0.80, jy0), (cx + jr * 0.80, jy0),
                   (cx + jr * 0.56, jy0 + r * 0.34), (cx + jl * 0.56, jy0 + r * 0.34)]
        triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in jaw], ow=max(1, int(1.0 * s)))
        ulen = r * (0.14 + (0.0 if mode == "snarl" else 0.10) + rage * 0.08)
        ugap = idx % 3
        for j in range(nf):
            fx = cx - r * 0.32 + j * (r * 0.64 / max(1, nf - 1))
            c_upfang(fx, ulen, skip=(j == ugap and rage > 0.6))
        ly = jy0 + r * 0.02
        n_tusk = 2 + int(rage * 2)
        for j in range(n_tusk):
            fx = cx - r * 0.22 + j * (r * 0.44 / max(1, n_tusk - 1))
            c_lowfang(fx, ly, r * (0.16 + rage * 0.10))

    # ── WIDE OVAL sockets canted OUTWARD/UP + DIM cyan wrath-fire ember ──
    # Three-step crown ember ladder, all still DIM (below the brow third-eye, far
    # below the necklace hero gem; NO white core, NO glow): the lit CENTRE relic
    # carries MOST cyan (CYAN core + CYAN_BR glint); the two OUTERMOST fan-tip relics
    # are NUDGED one value notch (a mid CYAN_MID core, no glint) so the 3-up beat —
    # two arc ends + the centre — reads at hero scale; the inner rest stay CYAN_D.
    CYAN_MID = lerp(CYAN_D, CYAN, 0.5)
    for sgn in (-1, 1):
        ex = cx + int(sgn * r * 0.38)
        ey = cy + int(r * 0.04)
        ax, ay = int(r * 0.30), int(r * 0.22)
        ov = []
        for od in range(0, 360, 60):
            oa = math.radians(od)
            ox = math.cos(oa) * ax + sgn * 0.26 * (-math.sin(oa) * ay)
            oy = math.sin(oa) * ay + sgn * 0.10 * (math.cos(oa) * ax)
            ov.append((ex + int(ox), ey + int(oy)))
        pygame.draw.polygon(surf, INK, ov)
        em_x, em_y = ex, ey + int(r * 0.03)
        if lit:
            pygame.draw.circle(surf, CYAN, (em_x, em_y), max(1, int(r * 0.13)))
            pygame.draw.circle(surf, CYAN_BR, (em_x - int(r * 0.04), em_y - int(r * 0.05)),
                               max(1, int(r * 0.05)))
        elif nudge:
            pygame.draw.circle(surf, CYAN_MID, (em_x, em_y), max(1, int(r * 0.12)))
        else:
            pygame.draw.circle(surf, CYAN_D, (em_x, em_y), max(1, int(r * 0.10)))

    # nasal pit — flared with rage (a snarling snout)
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.40)), max(1, int(r * (0.12 + rage * 0.05))))

    # cheek-crack damage on the near-clenched grimace — INTERIOR hairline ONLY.
    # WHY no contour wound here: idx 4 is the deliberate INTACT-dome relic, the
    # smooth/whole contrast skull that makes its broken neighbours read as broken.
    if dmg == "cheek_crack":
        cc = [(cx + r * 0.28, cy + r * 0.16), (cx + r * 0.42, cy + r * 0.34),
              (cx + r * 0.34, cy + r * 0.50)]
        pygame.draw.lines(surf, CROWN_BONE_D, False, [(int(x), int(y)) for x, y in cc], ow_thin)


# ── a small CYAN cabochon inlay — the palm-gem (DIM tier, gold bezel) ─────────
def palm_cabochon(surf, c, r, s):
    """A gold-bezel cyan CABOCHON inlay set into a palm-skull's brow. WHY a clear
    value step BELOW the focal third-eye: the brow gem must stay the single
    brightest pixel, so this inlay caps at CYAN_BR for a tiny rim glint only — NO
    white-hot core — and rides a warm GOLD bezel so it reads as jewel-set bone,
    matching her bead identity rather than competing with the third-eye."""
    cx, cy = int(c[0]), int(c[1])
    # warm gold bezel ring first (the setting), then the domed cyan stone inside
    triad_circle(surf, GOLD, (cx, cy), r + max(1, int(0.9 * s)),
                 ow=max(1, int(1.0 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, INK, (cx, cy), r)
    pygame.draw.circle(surf, CYAN_D, (cx, cy), max(1, r - max(1, int(0.6 * s))))
    pygame.draw.circle(surf, CYAN, (cx, cy), max(1, int(r * 0.66)))
    # a single small rim glint (capped at CYAN_BR — never the focal white core)
    pygame.draw.circle(surf, CYAN_BR, (cx - int(r * 0.30), cy - int(r * 0.32)),
                       max(1, int(r * 0.26)))


# ── a tiny skull cradled in an open palm (the brood MOTIF) ────────────────────
def palm_skull(surf, cx, cy, r, s, idx=0):
    """An open BONE palm cradling a WRATHFUL charnel-ground reliquary skull. WHY
    both pieces: the brood motif is six open palms EACH holding a skull at the fan
    tips. WHY this sister is the WRATHFUL pole: she is the fierce protector-destroyer,
    so every cradled skull bares FANGS — ONE fury language at varying intensity so
    the chorus never splits into bland closed glares: rictus (jaw CLOSED, lips pulled
    back over a clenched fang row), snarl (jaw partly dropped, bared fangs over a thin
    void), full ROAR (jaw torn WELL below the cranium, a black agape void with fang
    triangles top + bottom). The fury also lives in the OUTLINE: SILHOUETTE-ALTERING
    damage — sheared jaw corner, caved temple, broken cranium crest, knocked-out fang
    (a gap in the lower edge), a displaced crack-wedge — so the wrath reads in pure
    black at 32px, not only in interior ink that vaporizes. WHY `idx`: the six are a
    CHORUS — 2 rictus, 2 snarl, 2 roar, with cranium PROPORTION (narrow-tall / squat-
    broad / leaning), crack side, brow angle and fang count all varying, never one
    screamer stamped six times. The two OUTERMOST fan-tip skulls (idx 0 + idx 3) carry
    MORE cyan wrath-fire (a CYAN ember core + a CYAN_BR upper glint); the rest keep
    DIM CYAN_D embers. LADDER: all embers stay DIM — a perceptible step below the brow
    third-eye and far below the necklace hero gem; NO palm skull gets a white-hot core.
    MID value tier: pale BEAD bone."""
    ow1 = max(1, int(1.4 * s))
    ow_thin = max(1, int(1.0 * s))

    # ── per-skull WRATH table — a chorus of six distinct fierce skulls ──
    # tilt(rad)·cranium x/y stretch·jaw roar mode·fang count·suture·brow angle(out/up)
    # ·socket cant·damage (which silhouette-altering wound)·rage 0..1·cyan tier
    # rage drives jaw-open amount + brow heaviness; damage edits the OUTLINE so the
    # fury survives downscale; cyan="bright" gets the ember-core + glint.
    # ONE fury LANGUAGE = BARED FANGS, intensity varying along a single axis:
    #   rictus  = lips pulled back, jaw CLOSED, full fang row clenched edge-to-edge
    #   snarl   = jaw partly dropped, bared fangs over a thin void
    #   roar    = jaw torn WELL below the cranium, big black void, fang triangles
    #             top + bottom — the agape silhouette wound
    # Spread of the six PALM satellites: 2 rictus · 2 snarl · 2 roar. Combined with
    # the six CROWN relics this gives the 12-strong chorus ~4 / ~4 / ~4.
    PROFILE = [
        # 0: FULL-ROAR (outermost LEFT fan tip), jaw torn wide + sheared corner —
        #    SILHOUETTE damage · BRIGHT cyan ember
        dict(tilt=-0.10, cw=1.02, ch=1.06, jaw="roar", fangs=4, sut="zig",
             brow=0.34, cant=0.30, dmg="jaw_shear", rage=1.00, cyan="bright"),
        # 1: mid-SNARL, NARROW TALL skull, caved LEFT temple — SILHOUETTE damage
        dict(tilt= 0.12, cw=0.84, ch=1.18, jaw="snarl", fangs=4, sut="crack",
             brow=0.30, cant=0.22, dmg="temple_cave", rage=0.60, cyan="dim"),
        # 2: clenched RICTUS (innermost LEFT), SQUAT BROAD dome, full clenched fang
        #    row, knocked-out lower fang — SILHOUETTE damage (gap in lower edge)
        dict(tilt=-0.04, cw=1.18, ch=0.88, jaw="rictus", fangs=6, sut="line",
             brow=0.22, cant=0.16, dmg="fang_knock", rage=0.40, cyan="dim"),
        # 3: FULL-ROAR (outermost RIGHT fan tip), broken cranium crest (chunk gone)
        #    — SILHOUETTE damage · BRIGHT cyan ember (mirror of #0)
        dict(tilt= 0.18, cw=1.00, ch=1.04, jaw="roar", fangs=4, sut="zig",
             brow=0.30, cant=0.26, dmg="crest_break", rage=0.94, cyan="bright"),
        # 4: hard SNARL, TALL leaning skull, displaced offset crack-wedge —
        #    SILHOUETTE damage (a shifted plate off the dome edge)
        dict(tilt=-0.22, cw=0.90, ch=1.14, jaw="snarl", fangs=4, sut="crack",
             brow=0.28, cant=0.24, dmg="crack_shift", rage=0.72, cyan="dim"),
        # 5: clenched RICTUS (innermost RIGHT), WIDEST SQUAT dome, full clenched
        #    fang grin, caved RIGHT temple — SILHOUETTE damage
        dict(tilt= 0.08, cw=1.16, ch=0.94, jaw="rictus", fangs=6, sut="zig",
             brow=0.24, cant=0.18, dmg="temple_cave_r", rage=0.46, cyan="dim"),
    ]
    p = PROFILE[idx % len(PROFILE)]
    t = p["tilt"]
    ct, st = math.cos(t), math.sin(t)

    def rot(dx, dy):
        # rotate an offset about the skull centre, then translate to (cx,cy)
        return (cx + dx * ct - dy * st, cy + dx * st + dy * ct)

    cw, ch = p["cw"], p["ch"]
    rage = p["rage"]
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
    dmg = p["dmg"]

    # cranium dome — an ink-keyed bone polygon shaped per-profile (NOT a plain
    # circle): wide brow tapering to a narrower jaw, stretched by cw/ch + tilted.
    # WHY damage edits the dome point-by-point: a caved temple or a broken crest is a
    # SILHOUETTE wound, not an inked line, so the fury survives the downscale to 32px.
    dome = []
    for ang_deg in range(-180, 1, 12):    # top half-ring (brow + temples + crown)
        a = math.radians(ang_deg)
        dx = math.cos(a) * cr * cw
        dy = math.sin(a) * cr * ch
        # caved temple — punch a flat in the upper-left (or -right) of the dome
        if dmg == "temple_cave" and -2.7 < a < -1.9:
            dx += cr * 0.30; dy += cr * 0.16
        if dmg == "temple_cave_r" and -1.25 < a < -0.45:
            dx -= cr * 0.30; dy += cr * 0.16
        # broken cranium crest — a jagged chunk sheared off the crown top
        if dmg == "crest_break" and -1.95 < a < -1.15:
            dy += cr * 0.34 * (0.4 + 0.6 * abs(math.cos(a * 3.0)))
        # displaced crack-wedge — a plate of the upper-right dome shoved OUTWARD,
        # leaving a stepped notch in the silhouette (a battle-shifted skull plate)
        if dmg == "crack_shift" and -0.95 < a < -0.25:
            dx += cr * 0.30; dy -= cr * 0.18
        dome.append(rot(dx, dy))
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

    # cranial SUTURE — per-profile zig / jagged battle-crack / hairline median.
    # WHY a crack-style suture on the wrathful skulls: a forked temple crack reads as
    # damage rather than decorative seam, reinforcing the charnel-ground fury.
    if p["sut"] == "zig":
        zp = []
        for j in range(5):
            zx = -cr * 0.34 + j * (cr * 0.68 / 4)
            zy = -cr * ch * 0.62 + (cr * 0.12 if j % 2 else -cr * 0.08)
            zp.append(rot(zx, zy))
        pygame.draw.lines(surf, BONE_DD, False, [(int(x), int(y)) for x, y in zp], ow_thin)
    elif p["sut"] == "crack":
        # a forked battle-crack splitting down from the crown into the brow
        ck = [rot(cr * 0.06, -cr * ch * 0.78), rot(-cr * 0.10, -cr * ch * 0.40),
              rot(cr * 0.04, -cr * ch * 0.12), rot(-cr * 0.06, cr * 0.06)]
        pygame.draw.lines(surf, BONE_DD, False, [(int(x), int(y)) for x, y in ck], ow_thin)
        fork = [rot(-cr * 0.10, -cr * ch * 0.40), rot(-cr * 0.30, -cr * ch * 0.20)]
        pygame.draw.lines(surf, BONE_DD, False, [(int(x), int(y)) for x, y in fork], ow_thin)
    else:   # "line" — a single faint median hairline (the near-clenched grimace)
        pygame.draw.line(surf, BONE_DD,
                         (int(rot(0, -cr * ch * 0.80)[0]), int(rot(0, -cr * ch * 0.80)[1])),
                         (int(rot(0, -cr * 0.10)[0]), int(rot(0, -cr * 0.10)[1])), ow_thin)

    # extra scar lines scaled with rage — a chipped temple crack on the angriest
    if rage > 0.5:
        sc = [rot(cr * cw * 0.70, -cr * ch * 0.20), rot(cr * cw * 0.42, cr * 0.02)]
        pygame.draw.lines(surf, BONE_DD, False, [(int(x), int(y)) for x, y in sc], ow_thin)

    # ── HEAVY angry brow ridges — two wedges canted OUTWARD/UP over the sockets ──
    # WHY wedges, not a flat bar: a down-and-in inner edge with a raised outer end
    # is the universal ANGRY-eyebrow geometry; the per-skull brow weight scales how
    # heavy/steep, so the chorus ranges from a slight frown to a thunderous scowl.
    bw = p["brow"]
    for sgn in (-1, 1):
        bi_x, bi_y = rot(sgn * cr * 0.08, -cr * (0.02 - bw * 0.30))   # inner (low, near nose)
        bo_x, bo_y = rot(sgn * cr * 0.58, -cr * (0.20 + bw * 0.55))   # outer (high, raised)
        bb_x, bb_y = rot(sgn * cr * 0.56, -cr * 0.02)                 # outer base
        bn_x, bn_y = rot(sgn * cr * 0.10, cr * 0.10)                  # inner base (frown crease)
        triad_blob(surf, BONE_D, [(int(bi_x), int(bi_y)), (int(bo_x), int(bo_y)),
                                  (int(bb_x), int(bb_y)), (int(bn_x), int(bn_y))], ow=ow_thin)

    # ── WIDE OVAL sockets canted OUTWARD/UP, deep ink with carved rim + cyan EMBER ──
    # WHY ovals tilted toward the temples (not round pits): the outward upward tilt
    # plus the heavy brow reads as a glare. The cyan EMBER is drawn-flat and DIM
    # (CYAN_D core for most; CYAN core + CYAN_BR upper glint on the bright-tier pair)
    # — wrath-fire, never a focal: it stays below the brow third-eye in value.
    cant = p["cant"]
    bright = (p["cyan"] == "bright")
    for sgn in (-1, 1):
        ecx, ecy = rot(sgn * cr * 0.42, cr * 0.16)
        ecx, ecy = int(ecx), int(ecy)
        ax = int(cr * 0.34)               # socket horizontal radius (wide)
        ay = int(cr * 0.26)               # vertical radius (oval)
        # canted oval socket as a small rotated polygon (outward/up tilt)
        ov = []
        for od in range(0, 360, 45):
            oa = math.radians(od)
            ox = math.cos(oa) * ax
            oy = math.sin(oa) * ay
            # shear the oval so its long axis cants up toward the outer temple
            ox += sgn * cant * (-oy)
            oy += sgn * cant * 0.4 * ox
            ov.append((ecx + int(ox), ecy + int(oy)))
        pygame.draw.polygon(surf, BONE_D, ov)
        pygame.draw.polygon(surf, INK, ov)
        pygame.draw.polygon(surf, BONE_DD, [(ecx + int((x - ecx) * 0.62),
                                             ecy + int((y - ecy) * 0.62)) for x, y in ov])
        # the wrath-fire ember — drawn flat, DIM, sitting low in the socket
        em_x, em_y = ecx, ecy + int(cr * 0.04)
        if bright:
            pygame.draw.circle(surf, CYAN, (em_x, em_y), max(1, int(cr * 0.15)))
            pygame.draw.circle(surf, CYAN_BR, (em_x - int(cr * 0.05), em_y - int(cr * 0.06)),
                               max(1, int(cr * 0.06)))
        else:
            pygame.draw.circle(surf, CYAN_D, (em_x, em_y), max(1, int(cr * 0.12)))

    # nasal aperture — an inverted ink teardrop between/below the sockets, flared
    # wider with rage (a snarling, flared snout)
    nflare = 0.16 + rage * 0.08
    n_top = rot(0, cr * 0.30)
    n_l = rot(-cr * nflare, cr * 0.60)
    n_r = rot(cr * nflare, cr * 0.60)
    pygame.draw.polygon(surf, INK, [(int(n_top[0]), int(n_top[1])),
                                    (int(n_l[0]), int(n_l[1])),
                                    (int(n_r[0]), int(n_r[1]))])

    # ── BARED-FANGS mouth — one grammar, three intensities ──
    # rictus  = jaw CLOSED, lips pulled back, a full clenched fang row on a thin seam
    # snarl   = jaw partly dropped over a thin dark void, bared fangs top + bottom
    # roar    = jaw torn WELL below the cranium, big black void, fang triangles both
    #           rows — agape so it EDITS the silhouette.
    mode = p["jaw"]
    nf = p["fangs"]
    jl, jr = -cr * 0.42, cr * 0.42       # jaw corners under the cheeks
    uy = cr * 0.66                       # upper tooth baseline

    def upfang(fx, length, skip=False):
        if skip:
            return
        t0 = rot(fx - cr * 0.06, uy)
        t1 = rot(fx + cr * 0.06, uy)
        tp = rot(fx, uy + length)
        pygame.draw.polygon(surf, BEAD, [(int(t0[0]), int(t0[1])), (int(t1[0]), int(t1[1])),
                                         (int(tp[0]), int(tp[1]))])
        pygame.draw.polygon(surf, INK, [(int(t0[0]), int(t0[1])), (int(t1[0]), int(t1[1])),
                                        (int(tp[0]), int(tp[1]))], max(1, int(0.8 * s)))

    def lowfang(fx, baseline, length, skip=False):
        if skip:
            return
        t0 = rot(fx - cr * 0.07, baseline)
        t1 = rot(fx + cr * 0.07, baseline)
        tp = rot(fx, baseline - length)
        pygame.draw.polygon(surf, BEAD, [(int(t0[0]), int(t0[1])), (int(t1[0]), int(t1[1])),
                                         (int(tp[0]), int(tp[1]))])
        pygame.draw.polygon(surf, INK, [(int(t0[0]), int(t0[1])), (int(t1[0]), int(t1[1])),
                                        (int(tp[0]), int(tp[1]))], max(1, int(0.8 * s)))

    if mode == "rictus":
        # CLOSED clenched grin: no agape void — a tight dark mouth-seam with the
        # fangs meeting it edge-to-edge (lips pulled back over bared teeth).
        seam = [rot(jl * 0.90, uy + cr * 0.10), rot(jr * 0.90, uy + cr * 0.10),
                rot(jr * 0.84, uy + cr * 0.22), rot(jl * 0.84, uy + cr * 0.22)]
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in seam])
        # the closed lower jaw bone, tucked right under the seam (NOT dropped)
        jy0 = uy + cr * 0.22
        if dmg == "fang_knock":
            # a knocked-out lower fang shows as a notch bitten into the jaw EDGE
            jaw = [rot(jl * 0.86, jy0), rot(-cr * 0.06, jy0), rot(0.0, jy0 + cr * 0.16),
                   rot(cr * 0.08, jy0), rot(jr * 0.86, jy0),
                   rot(jr * 0.62, jy0 + cr * 0.30), rot(jl * 0.62, jy0 + cr * 0.30)]
        else:
            jaw = [rot(jl * 0.86, jy0), rot(jr * 0.86, jy0),
                   rot(jr * 0.62, jy0 + cr * 0.30), rot(jl * 0.62, jy0 + cr * 0.30)]
        triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        # full clenched fang row — short, edge-to-edge, the lower-edge gap on knock
        knock = idx % nf
        for j in range(nf):
            fx = -cr * 0.36 + j * (cr * 0.72 / max(1, nf - 1))
            upfang(fx, cr * 0.18)
            lowfang(fx, jy0 + cr * 0.02, cr * 0.16,
                    skip=(dmg == "fang_knock" and j == knock))
    else:
        # SNARL / ROAR — agape void, jaw dropped (roar drops WELL below the cranium).
        open_amt = (0.30 if mode == "snarl" else 0.72) + rage * 0.18
        drop = cr * (0.16 + open_amt)
        void = [rot(jl * 0.92, uy), rot(jr * 0.92, uy),
                rot(jr * 0.80, uy + drop), rot(jl * 0.80, uy + drop)]
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in void])
        jy0 = uy + drop
        if dmg == "jaw_shear":
            # one jaw corner sheared clean off — a hard asymmetric silhouette wound
            if idx % 2 == 0:
                jaw = [rot(jl * 0.86, jy0), rot(jr * 0.30, jy0),
                       rot(jr * 0.05, jy0 + cr * 0.30), rot(jl * 0.70, jy0 + cr * 0.34)]
            else:
                jaw = [rot(jl * 0.30, jy0), rot(jr * 0.86, jy0),
                       rot(jr * 0.70, jy0 + cr * 0.34), rot(jl * 0.05, jy0 + cr * 0.30)]
        else:
            jaw = [rot(jl * 0.80, jy0), rot(jr * 0.80, jy0),
                   rot(jr * 0.58, jy0 + cr * 0.34), rot(jl * 0.58, jy0 + cr * 0.34)]
        triad_blob(surf, BEAD, [(int(x), int(y)) for x, y in jaw], ow=ow_thin)
        # upper fang row ringing the void; the roar/snarl shows 2-3 big fangs top
        ulen = cr * (0.20 + (0.0 if mode == "snarl" else 0.12) + rage * 0.10)
        ugap = idx % 3
        for j in range(nf):
            fx = -cr * 0.34 + j * (cr * 0.68 / max(1, nf - 1))
            upfang(fx, ulen, skip=(j == ugap and rage > 0.6))
        # lower tusk row biting UP from the dropped jaw (more + bigger with rage)
        ly = jy0 + cr * 0.02
        n_tusk = 2 + int(rage * 2)
        for j in range(n_tusk):
            fx = -cr * 0.24 + j * (cr * 0.48 / max(1, n_tusk - 1))
            lowfang(fx, ly, cr * (0.18 + rage * 0.12))


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
    # WHY ONE lit skull (centre, idx 2) + a NUDGE on the two fan-tip ends (idx 0, 5):
    # the locked rule keeps the crown the dimmest tier, but a 3-up ember beat (two arc
    # ends + the centre) reads at hero scale. WHY `idx=i`: each relic gets a DISTINCT
    # cranium silhouette + carved damage, so the arc reads as six jewels.
    # WHY the WIDER 110° spread + RADIAL STAGGER (RADJ): a tighter ring let the domes
    # overlap edge-to-edge into one mound, so the silhouette proof collapsed to a
    # smooth hump. Spacing the perches wider opens SKY between adjacent dome TOPS, and
    # pushing each skull OUT by its own amount gives each its own crest height — a
    # saw-tooth of six countable bumps in the pure-black proof. WHY a gentle undulation
    # (not a hard zigzag): a pure alternating in/out sinks the pulled-in domes under
    # their neighbours and merges pairs, so all six pushes stay >=0 and every crest
    # pokes the top edge; the tall-narrow idx 0 and squat-broad idx 2 add their own
    # height delta on top of the push.
    RADJ = [0.26, 0.02, 0.30, 0.00, 0.10, 0.24]     # per-skull perch push (× skull_r)
    centres = []
    for i in range(6):
        a = math.radians(215 + i * (110 / 5))
        rr = arc_r + RADJ[i] * skull_r
        sx = head_c[0] + math.cos(a) * rr
        sy = head_c[1] + math.sin(a) * rr
        centres.append((sx, sy, a))
        crown_skull(surf, int(sx), int(sy), skull_r, s,
                    lit=(i == 2), idx=i, nudge=(i in (0, 5)))
    # carve a thin dark seam between neighbouring domes — a tapered INK sliver along
    # the radial join. WHY this is for the RENDERED chip, not the proof: in the
    # blackout the mask flattens ink to solid too, so the COUNTABILITY in the proof
    # comes from the stagger + carved contours above; the ink seam is what keeps the
    # skulls visually separable in the literal 32px DAY/NIGHT chip where the domes
    # would otherwise read as one bone ridge.
    seam_w = max(2, int(2.2 * s))
    for i in range(5):
        ax_, ay_, _ = centres[i]
        bx_, by_, _ = centres[i + 1]
        mx, my = (ax_ + bx_) * 0.5, (ay_ + by_) * 0.5
        rad = math.atan2(my - head_c[1], mx - head_c[0])
        gx0 = mx + math.cos(rad) * skull_r * 0.34
        gy0 = my + math.sin(rad) * skull_r * 0.34
        gx1 = mx - math.cos(rad) * skull_r * 0.80
        gy1 = my - math.sin(rad) * skull_r * 0.80
        pygame.draw.line(surf, INK, (int(gx0), int(gy0)), (int(gx1), int(gy1)), seam_w)


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
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3_hero.png")
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
    sheet.blit(font_big.render("ASTHI v2 — WRATHFUL-GRIN", True, LABEL), (24, 13))
    sheet.blit(f_sm.render(
        "bone-jewel sky-dancer · CITIPATI body + MUKHA 6-arm fan · 12 BARED-FANGS satellites (rictus->snarl->roar) · crown skulls CARVED at the contour (caved temples / sheared crest / lost jaw corner) + staggered domes -> countable in the proof · round 3",
        True, LABEL_DIM), (270, 28))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(380, 540, 188, 296, 2.05)
    sheet.blit(hero, (14, 92))
    sheet.blit(f.render("Creature — hero", True, LABEL), (120, 636))
    sheet.blit(f_sm.render("Cocked-hip DANCE under a six-arm radial fan; each of the 6 open palms cradles", True, LABEL_DIM), (14, 660))
    sheet.blit(f_sm.render("a tiny skull. Fused crown = Mukha tiara-band on the brow + wide airy 6-skull arc.", True, LABEL_DIM), (14, 676))
    sheet.blit(f_sm.render("Bead-lattice over every surface; gold spacer-pips carry the texture (not cyan-on-blue).", True, LABEL_DIM), (14, 692))
    sheet.blit(f_sm.render("Value ladder: cyan third-eye brightest > palm-skulls + dim palm-gems mid > crown skulls dimmest.", True, LABEL_DIM), (14, 708))

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
        "ELEVATED pipeline: SS=8 supersample -> smoothscale; standalone hi-res hero export (round_3_hero.png).",
        True, LABEL_DIM), (26, 846))
    sheet.blit(f_sm.render(
        "STAY: flat fills · hard ink keyline (28,22,26) · dark-core->fill->top-left sheen triad · 1px grown outline · chibi scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 864))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    hero_out = export_hero()
    print("wrote", out)
    print("wrote", hero_out)


if __name__ == "__main__":
    main()
