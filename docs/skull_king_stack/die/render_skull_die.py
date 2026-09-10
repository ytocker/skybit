"""Skull-King DIE — the king-skull that tumbles like a dice and, when it settles,
shows a difficulty face 6..10 (plus a neutral pre-roll face). The skull IS the die;
the difficulty is its expression + a forehead numeral.

WHY this builds on the lit focal `crown:2` skull: the chosen Skull-King design's
heart-domed, cyan-lit-eye crown relic is the brood's hero face — the die has to
read as the SAME king, just escalating in menace, so the base silhouette/suture/
jaw/pip are lifted verbatim from `render_switchbig.crown_skull` (idx 2) and only
the menace levers move.

Self-contained for the GAME: draw_skull_die() depends ONLY on the chosen design's
engine module (palette + triad/outline helpers), stdlib + pygame. The game's
game/pillar_skull.py can replicate this exact logic.

Run headless:
  SDL_VIDEODRIVER=dummy python3 docs/skull_king_stack/die/render_skull_die.py
"""
import os, sys, math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# WHY this import dance mirrors build_showcase.py / render_skull_king_stack.py:
# the chosen design lives under asthi_ringeye and owns the palette + house helpers;
# review art reuses colour math + triad/outline only, never a shipped sprite module.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
ASTHI = os.path.join(ROOT, "docs/skybit_devil/batch2/asthi_ringeye")
sys.path.insert(0, ASTHI)

import pygame
pygame.init()
import render_switchbig as sk

OUT = HERE
os.makedirs(OUT, exist_ok=True)


# ── the difficulty ramp ───────────────────────────────────────────────────────
# WHY a single consistent treatment escalated on a fixed lever stack: each face must
# be instantly told apart AND read as the same king getting angrier. The read runs on
# TWO independent, value-driven (colorblind-safe) channels:
#   1. the NUMBER — the hero — on a RAISED bone PLATE on the brow, a CONSTANT near-white
#      digit with a hard dark keyline on every face (heat NEVER touches the digit), so
#      it stays legible when the eye-sockets tumble off-axis;
#   2. the EYES — the only thing that carries the amber→searing-red heat ramp.
# A third, SILHOUETTE channel (accreting horns) is the tumble safety net: difficulty
# reads from the outline even when the digit can't be parsed.
#
# Lever stack 6→10 (escalation): EYE glow amber→searing-red · accreting menace cues
# (crack → chip → breaching horn stubs → short horns → full swept horns) · jaw clench
# tightens. glow = (bezel/dark, mid fill, hot core) per difficulty — eyes only.
_AMBER  = ((150, 96, 24),  (236, 168, 52),  (255, 224, 140))
_ORANGE = ((150, 70, 18),  (240, 132, 36),  (255, 196, 110))
_REDORG = ((140, 46, 18),  (236, 92, 28),   (255, 168, 92))
_RED    = ((128, 28, 22),  (224, 56, 40),   (255, 132, 96))
_SEAR   = ((120, 16, 18),  (242, 40, 30),   (255, 196, 150))

# difficulty -> (glow triad, menace tier, jaw-clench frac, label)
# menace tier: 0 crack · 1 crack+chip · 2 +horn nubs · 3 +short horns · 4 +full horns
_FACES = {
    6:  dict(glow=_AMBER,  menace=0, clench=0.00),
    7:  dict(glow=_ORANGE, menace=1, clench=0.18),
    8:  dict(glow=_REDORG, menace=2, clench=0.38),
    9:  dict(glow=_RED,    menace=3, clench=0.62),
    10: dict(glow=_SEAR,   menace=4, clench=0.86),
}
# neutral pre-roll: cool cyan eyes (the king's resting identity), no numeral, no menace.
_NEUTRAL_GLOW = (sk.CYAN_D, sk.CYAN, sk.CYAN_BR)


def _glow_dot(surf, cx, cy, r, triad):
    """A lit cabochon in the difficulty heat: ink bezel · dark rim · mid fill · hot
    core · white pin-sheen — the value ladder that keeps it punching on any sky."""
    dark, mid, hot = triad
    pygame.draw.circle(surf, sk.INK, (cx, cy), r + max(1, r // 6))
    pygame.draw.circle(surf, dark, (cx, cy), r)
    pygame.draw.circle(surf, mid, (cx, cy), max(1, int(r * 0.74)))
    pygame.draw.circle(surf, hot, (cx, cy), max(1, int(r * 0.40)))
    pygame.draw.circle(surf, (255, 255, 255),
                       (cx - max(1, r // 4), cy - max(1, r // 4)), max(1, int(r * 0.18)))


# the digit is its OWN channel: a CONSTANT high-value bone-white on every face, so
# only the eyes carry the amber>red heat (two independent, value-driven, colorblind-
# safe signals). Near-white face + dark ink keyline = max value contrast on any sky.
_DIGIT_FACE = sk.BONE_SH               # warm near-white glyph body
_DIGIT_CORE = (255, 255, 255)          # hot pin-centre so the stroke reads lit, not flat


def _numeral_plate(surf, cx, cy, r, s, num, night=False):
    """A RAISED, flat-faced brow PLATE carrying the difficulty digit as the hero of
    the face. WHY raised + hard keyline (was a recessed inlay): the number is the
    primary read, so it sits PROUD of the dome on its own bone slab with a 1px dark
    keyline all the way around — it never merges into bone or eye. The digit is a
    CONSTANT bone-white (heat lives only in the eyes); strokes are fat with FLAT
    6/9 terminals so the figure survives the 24deg tumble; a cool top rim-light lifts
    the white digit on the dusk/night sky. '10' gets a wider plate."""
    wide = (num >= 10)
    # plate sized so the DIGIT becomes the HERO — ~55-60% of skull width (cw=1.10 ->
    # ~2.2r wide), a big jump from the old ~35% inlay. The slab is correspondingly
    # tall and seated high on the brow/lower dome so a big digit clears the eyes.
    half_w = int(r * (1.16 if wide else 0.72))
    half_h = int(r * 0.46)
    plate = [(cx - half_w, cy - half_h), (cx + half_w, cy - half_h),
             (cx + int(half_w * 0.92), cy + half_h), (cx - int(half_w * 0.92), cy + half_h)]
    plate = [(int(x), int(y)) for x, y in plate]
    kl = max(1, int(1.0 * s))          # the hard 1px-at-true-size dark keyline
    # raised slab: ink keyline ring · flat bone face · top rim-light (cool at night,
    # warm-bright by day) so the plate sits proud and the white digit always pops.
    pygame.draw.polygon(surf, sk.INK, plate)
    face = [(int(x), int(y)) for x, y in
            [(cx - half_w + kl, cy - half_h + kl), (cx + half_w - kl, cy - half_h + kl),
             (cx + int(half_w * 0.92) - kl, cy + half_h - kl),
             (cx - int(half_w * 0.92) + kl, cy + half_h - kl)]]
    pygame.draw.polygon(surf, sk.BONE, face)
    # bottom-right core shade + top rim-light → the plate reads RAISED, not painted on
    pygame.draw.polygon(surf, sk.BONE_D,
                        [(cx - half_w + kl, cy + int(half_h * 0.30)),
                         (cx + half_w - kl, cy + int(half_h * 0.30)),
                         (cx + int(half_w * 0.92) - kl, cy + half_h - kl),
                         (cx - int(half_w * 0.92) + kl, cy + half_h - kl)])
    rim = sk.CYAN_BR if night else sk.BONE_SH
    pygame.draw.line(surf, rim, (cx - half_w + kl, cy - half_h + kl),
                     (cx + half_w - kl, cy - half_h + kl), max(1, int(1.0 * s)))

    # the hand-stroked digit: constant bone-white, FAT strokes (~20% over a typeface),
    # FLAT 6/9 terminals, drawn ink-keyed-then-bone so it carves cleanly off the plate.
    # A jumbo cap height (~half the skull) makes the numeral the unmistakable hero —
    # the eyes/nose were slid down (efy) to clear it.
    gh = r * 0.86                      # cap height — the hero numeral
    sw = max(1, r * 0.13)              # fat stroke half-width (~20% over a typeface)

    col_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    if wide:
        # '10' — pack a '1' and '0' side by side inside the wider plate
        _digit_at(col_surf, cx - int(r * 0.46), cy, gh, sw * 0.9, which=1)
        _digit_at(col_surf, cx + int(r * 0.44), cy, gh, sw * 0.9, which=0)
    else:
        _digit_at(col_surf, cx, cy, gh, sw, which=num)
    # ink keyline around the whole figure (grow from its own alpha), then the bone fill
    keyed = sk.grow_outline(col_surf, sk.INK + (255,), max(1, int(1.4 * s)))
    surf.blit(keyed, (0, 0))


def _digit_at(col_surf, gx, cy, gh, sw, which):
    """Stroke one figure `which` in (0,1,6,7,8,9) at constant bone-white, centred at
    (gx, cy). FLAT 6/9 terminals + an annulus bowl keep bowl-up vs bowl-down legible
    under the 24deg tumble. `sw` is the fat stroke half-width."""
    col = _DIGIT_FACE
    sw = max(1.0, sw)
    hw = gh * 0.34
    top = cy - gh * 0.5
    bot = cy + gh * 0.5

    def cap(p0, p1):
        x0, y0 = p0; x1, y1 = p1
        pygame.draw.line(col_surf, col, (int(x0), int(y0)), (int(x1), int(y1)), int(sw * 2))
        pygame.draw.circle(col_surf, col, (int(x0), int(y0)), int(sw))
        pygame.draw.circle(col_surf, col, (int(x1), int(y1)), int(sw))

    def ring(rcy):
        br = gh * 0.30
        pygame.draw.circle(col_surf, col, (int(gx), int(rcy)), int(br + sw))
        punch = pygame.Surface(col_surf.get_size(), pygame.SRCALPHA)
        punch.fill((255, 255, 255, 255))
        pygame.draw.circle(punch, (0, 0, 0, 0), (int(gx), int(rcy)), int(max(1, br - sw)))
        col_surf.blit(punch, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        # hot pin-sheen sat ON the upper-left of the stroke band (radius ~br) so the
        # ring reads as a lit bone tube, not a flat outline.
        d = br * 0.70
        pygame.draw.circle(col_surf, _DIGIT_CORE,
                           (int(gx - d), int(rcy - d)), max(1, int(sw * 0.55)))

    if which == 6:
        bcy = bot - gh * 0.30
        cap((gx + hw, top), (gx - hw * 0.9, cy + gh * 0.04))
        ring(bcy)
    elif which == 9:
        bcy = top + gh * 0.30
        cap((gx - hw, bot), (gx + hw * 0.9, cy - gh * 0.04))
        ring(bcy)
    elif which == 7:
        cap((gx - hw, top), (gx + hw, top))
        cap((gx + hw, top), (gx - hw * 0.5, bot))
    elif which == 8:
        ring(top + gh * 0.27)
        ring(bot - gh * 0.27)
    elif which == 1:
        cap((gx, top), (gx, bot))
        cap((gx - hw * 0.7, top + gh * 0.20), (gx, top))
        cap((gx - hw, bot), (gx + hw, bot))
    elif which == 0:
        # a TALL oval matching the '1' height with a cleanly OPEN centre (the squat
        # ring read as a dumpy blob beside the slim '1'): solid oval, then punch an
        # inner oval so an even bone tube remains, plus the upper-left pin-sheen.
        ow, oh = gh * 0.40, gh * 0.50
        pygame.draw.ellipse(col_surf, col,
                            (int(gx - ow), int(cy - oh), int(2 * ow), int(2 * oh)))
        punch = pygame.Surface(col_surf.get_size(), pygame.SRCALPHA)
        punch.fill((255, 255, 255, 255))
        iw, ih = max(1.0, ow - sw * 1.5), max(1.0, oh - sw * 1.5)
        pygame.draw.ellipse(punch, (0, 0, 0, 0),
                            (int(gx - iw), int(cy - ih), int(2 * iw), int(2 * ih)))
        col_surf.blit(punch, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        d = oh * 0.42
        pygame.draw.circle(col_surf, _DIGIT_CORE,
                           (int(gx - ow * 0.5), int(cy - d)), max(1, int(sw * 0.55)))


def _menace(surf, cx, cy, r, s, tier, triad):
    """Accreting menace cues drawn ON TOP of the cranium. WHY accretion (each tier
    keeps the prior cues): the player should feel the same king visibly hardening —
    a hairline crack at 6, a chip taken out at 7, then horn growth 8→10. Horns are
    bone-coloured triad blobs with a hot tip so they tie to the rising heat."""
    dark, mid, hot = triad
    ow = max(1, int(1.2 * s))

    def crack(x0f, y0f, segs):
        """A jagged hairline fracture across the dome, ink-dark."""
        pts = []
        x, y = cx + x0f * r, cy + y0f * r
        for (dx, dy) in segs:
            pts.append((int(x), int(y)))
            x += dx * r; y += dy * r
        pts.append((int(x), int(y)))
        pygame.draw.lines(surf, sk.INK, False, pts, ow)
        pygame.draw.lines(surf, sk.CROWN_BONE_D, False,
                          [(px - 1, py) for px, py in pts], max(1, ow - 1))

    def horn(side, length, sweep, rootw_f):
        """A swept horn rooted at the upper temple. WHY a fat root + explicit dark
        outline: the silhouette change nubs>stubs>full-sweep is the tumble SAFETY NET
        (difficulty must read from the OUTLINE even when the digit is unreadable), so
        the horn enforces a minimum ~2px-at-true-size body + a 1px dark keyline so the
        delta survives the 56px downscale instead of dissolving into a bone smear."""
        bx = cx + side * r * 0.74
        by = cy - r * 0.62
        # min root half-width so the horn body is >=~2px wide after the SS downscale.
        # s = (r/12)*SS, so one TRUE px == 12*s/r supersampled px; floor at ~1.5 true px
        # half-width (=>~3px body) so the silhouette delta survives 56px.
        rootw = max(r * rootw_f, 1.5 * (12.0 * s / max(1.0, r)))
        tipx = bx + side * r * sweep
        tipy = by - r * length
        midx = bx + side * r * sweep * 0.35
        midy = by - r * length * 0.62
        pts = [(bx - side * rootw, by + r * 0.10),
               (bx + side * rootw, by - r * 0.04),
               (int(midx + side * rootw * 0.5), int(midy)),
               (int(tipx), int(tipy)),
               (int(midx - side * rootw * 0.3), int(midy + r * 0.06))]
        pts = [(int(x), int(y)) for x, y in pts]
        # heavy dark keyline FIRST (a fat ink underlay) so the horn silhouette stays a
        # hard-edged delta against the sky at size, then the bone body on top.
        sk.triad_blob(surf, sk.CROWN_BONE, pts, ow=max(2, int(1.6 * s)))
        # hot-lit tip so the horns share the face's rising heat
        _glow_dot(surf, int(tipx), int(tipy), max(2, int(r * 0.10)), triad)

    if tier >= 0:
        crack(-0.10, -0.86, [(0.06, 0.12), (-0.05, 0.14), (0.07, 0.16), (-0.03, 0.14)])
    if tier >= 1:
        # a chip bitten out of the right temple — a notch of dark sky into the dome
        chip = [(cx + r * 0.66, cy - r * 0.50), (cx + r * 0.92, cy - r * 0.42),
                (cx + r * 0.70, cy - r * 0.24)]
        pygame.draw.polygon(surf, sk.INK, [(int(x), int(y)) for x, y in chip])
        crack(0.30, -0.78, [(0.05, 0.18), (-0.06, 0.16), (0.06, 0.20)])
    # tier 2 (the '8' face) must clearly BREACH the crown silhouette so 7 (chip only)
    # and 8 (chip + stubs) are an EVEN rung apart — the nubs are now real horn stubs
    # that punch above the dome, not the near-invisible bumps they were.
    if tier == 2:
        for side in (-1, 1):
            horn(side, 0.46, 0.22, 0.24)      # breaching stubs
    elif tier == 3:
        for side in (-1, 1):
            horn(side, 0.70, 0.32, 0.24)      # short horns
    elif tier >= 4:
        for side in (-1, 1):
            horn(side, 1.02, 0.48, 0.26)      # full swept horns


# WHY a render hint, not a signature change: the GAME-facing draw_skull_die() signature
# is frozen, but the plate's top rim-light wants to flip cool on a dusk/night sky so the
# white digit keeps its lift. The review sheet sets this per-row; day is the safe default
# (and what the game gets), so the public contract is unchanged.
_NIGHT_HINT = False


def _crown_die_face(surf, cx, cy, r, s, *, glow, num=None, menace=0, clench=0.0):
    """The king-skull die face: render_switchbig.crown_skull idx 2 (heart dome, dots
    suture, brow, set jaw, brow pip) drawn straight, with the eye glow swapped to the
    difficulty heat, the jaw clenched, the forehead numeral, and accreting menace.

    WHY idx 2 verbatim as the base: it is the lit focal 'crown:2' the brief pins —
    keeping its cw/ch/heart/suture identity makes every difficulty unmistakably the
    SAME king. Only `glow`, `clench`, `menace`, and the cartouche move."""
    CROWN_BONE, CROWN_BONE_D, CROWN_SH = sk.CROWN_BONE, sk.CROWN_BONE_D, sk.CROWN_SH
    INK = sk.INK
    ow1 = max(1, int(1.6 * s))
    ow_thin = max(1, int(1.0 * s))
    # crown:2 profile (heart dome / dots suture / brow / set jaw / pip)
    cw, ch = 1.10, 0.86
    dark, mid, hot = glow

    # ── domed heart cranium (verbatim crown_skull geometry, lean=0) ──
    dome = []
    for ang_deg in range(-180, 1, 18):
        a = math.radians(ang_deg)
        dx = math.cos(a) * r * cw
        dy = math.sin(a) * r * ch
        if abs(math.cos(a)) < 0.34 and math.sin(a) < -0.4:    # heart notch
            dy += r * 0.22
        dome.append((cx + dx, cy + dy))
    dome.append((cx + r * cw * 0.74, cy + r * ch * 0.34))
    dome.append((cx - r * cw * 0.74, cy + r * ch * 0.34))
    sk.triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in dome], ow=ow1)
    sheen = [(cx - r * cw * 0.58, cy - r * ch * 0.10),
             (cx - r * cw * 0.10, cy - r * ch * 0.66),
             (cx - r * cw * 0.02, cy - r * ch * 0.34),
             (cx - r * cw * 0.46, cy + r * ch * 0.02)]
    pygame.draw.polygon(surf, CROWN_SH, [(int(x), int(y)) for x, y in sheen])

    # ── dotted suture seam ──
    seam_y = cy - r * ch * 0.56
    for j in range(5):
        zx = cx - r * 0.34 + j * (r * 0.68 / 4)
        pygame.draw.circle(surf, CROWN_BONE_D, (int(zx), int(seam_y)), max(1, int(0.9 * s)))
        if j % 2 == 0:
            pygame.draw.circle(surf, sk.GOLD_D, (int(zx), int(seam_y)), max(1, int(0.8 * s)))

    # ── brow ridge ──
    pygame.draw.line(surf, CROWN_BONE_D,
                     (int(cx - r * 0.46), int(cy - r * 0.02)),
                     (int(cx + r * 0.46), int(cy - r * 0.02)), max(1, int(1.3 * s)))

    # ── set jaw, tightened by `clench`: corners pull in + up as menace rises ──
    cl = clench
    jw = 0.44 - 0.10 * cl
    jh0 = 0.52 - 0.04 * cl
    jh1 = 0.98 - 0.10 * cl
    jaw = [(cx - r * jw, cy + r * jh0), (cx + r * jw, cy + r * jh0),
           (cx + r * (0.26 - 0.06 * cl), cy + r * jh1),
           (cx - r * (0.26 - 0.06 * cl), cy + r * jh1)]
    sk.triad_blob(surf, CROWN_BONE, [(int(x), int(y)) for x, y in jaw], ow=max(1, int(1.2 * s)))

    # ── eyes: lit in the difficulty heat (neutral = cyan). A furrow over each socket
    #    deepens with clench so the face reads angrier without losing the eye read.
    #    WHY a downward feature shift on NUMBERED faces: the digit is now the hero and
    #    needs the whole forehead/lower-dome — the eyes/nose/teeth slide down so the big
    #    plate owns the top of the face without burying the eye heat-channel. ──
    efy = int(r * 0.24) if num is not None else 0
    eye_y = cy + int(r * 0.04) + efy
    for sgn, ex in ((-1, cx - int(r * 0.38)), (1, cx + int(r * 0.38))):
        pygame.draw.circle(surf, INK, (ex, eye_y), max(1, int(r * 0.26)))
        _glow_dot(surf, ex, eye_y, max(1, int(r * 0.15)), glow)
        if cl > 0.0:
            # angled brow furrow — inner end dips toward the nose as clench rises
            ix = cx - sgn * int(r * 0.10)
            ox = ex - sgn * int(r * 0.26)
            iy = eye_y - int(r * (0.30 + 0.16 * cl))
            oy = eye_y - int(r * 0.34)
            pygame.draw.line(surf, INK, (ox, oy), (ix, iy), max(1, int(1.6 * s)))

    # ── nose + teeth row (slid down with the eyes on numbered faces) ──
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42) + efy), max(1, int(r * 0.13)))
    ty = cy + int(r * 0.70) + efy
    pygame.draw.line(surf, INK, (cx - int(r * 0.32), ty), (cx + int(r * 0.32), ty),
                     max(1, int(1.2 * s)))
    for j in range(3):
        tx = cx - int(r * 0.24) + j * int(r * 0.24)
        pygame.draw.line(surf, INK, (tx, ty - int(r * 0.08)), (tx, ty + int(r * 0.10)),
                         max(1, int(1.0 * s)))

    # ── menace cues (under the cartouche so horns root behind the plate cleanly) ──
    _menace(surf, cx, cy, r, s, menace, glow)

    # ── the difficulty numeral PLATE on the brow (the hero), OR the resting brow pip ──
    if num is None:
        # neutral: the king's resting gold-bezel cyan brow pip (crown:2 'pip')
        bg_y = cy - int(r * 0.28)
        pygame.draw.circle(surf, sk.GOLD_D, (cx, bg_y), max(1, int(r * 0.18)))
        pygame.draw.circle(surf, sk.CYAN_D, (cx, bg_y), max(1, int(r * 0.11)))
    else:
        _numeral_plate(surf, cx, cy - int(r * 0.40), r, s, num, night=_NIGHT_HINT)


# ── public API (the GAME calls this same logic) ───────────────────────────────
def draw_skull_die(surf, cx, cy, px, difficulty=None, neutral=False):
    """Draw the king-skull die face centred at (cx, cy), fitting roughly `px` pixels
    tall, supersampled + smoothscaled + house-outlined so it survives downscale.

    difficulty: 6..10 picks the escalating menace face; neutral=True (or difficulty
    None) draws the cool resting pre-roll face. The skull is the die; this one call
    produces every face — the GAME replicates it in game/pillar_skull.py."""
    SS = 8
    r = int(px * 0.40)                       # radius from target box
    big = pygame.Surface((px * SS, int(px * 1.5 * SS)), pygame.SRCALPHA)
    bx = px * SS // 2
    by = int(px * 1.5 * SS * 0.46)           # headroom above for horns
    rb = r * SS
    s = (r / 12.0) * SS

    if neutral or difficulty is None:
        _crown_die_face(big, bx, by, rb, s, glow=_NEUTRAL_GLOW, num=None, menace=-1, clench=0.0)
    else:
        f = _FACES[difficulty]
        _crown_die_face(big, bx, by, rb, s, glow=f["glow"], num=difficulty,
                        menace=f["menace"], clench=f["clench"])

    small = pygame.transform.smoothscale(big, (px, int(px * 1.5)))
    chip = sk.grow_outline(small, sk.INK + (255,), 1)
    surf.blit(chip, (int(cx - px / 2), int(cy - px * 1.5 * 0.46)))


# ── review sheet ──────────────────────────────────────────────────────────────
def _sky(w, h, night=False):
    top = sk.NIGHT_T if night else sk.DAY_SKY_T
    if night:
        bot = sk.lerp(top, (60, 70, 110), 0.7)
    else:
        bot = sk.lerp(top, (255, 255, 255), 0.45)
    surf = pygame.Surface((w, h))
    for yy in range(h):
        surf.fill(sk.lerp(top, bot, yy / max(1, h - 1)), (0, yy, w, 1))
    return surf


def _label(surf, text, x, y, sz=15, col=(235, 230, 222)):
    f = sk.font(sz)
    surf.blit(f.render(text, True, (20, 16, 22)), (x + 1, y + 1))
    surf.blit(f.render(text, True, col), (x, y))


_ORDER = [("neutral", None, True), ("6", 6, False), ("7", 7, False),
          ("8", 8, False), ("9", 9, False), ("10", 10, False)]


def _row(px, night, rot=0.0):
    """One row of all six faces on a sky strip, each at box `px`, optionally rotated
    to test the tumbling read."""
    global _NIGHT_HINT
    _NIGHT_HINT = night                       # flip the plate rim-light cool on night sky
    cell = int(px * 1.9)
    h = int(px * 2.1)
    strip = _sky(cell * len(_ORDER), h, night=night)
    for i, (lab, diff, neu) in enumerate(_ORDER):
        cx = i * cell + cell // 2
        cy = int(h * 0.50)
        if rot:
            tmp = pygame.Surface((cell, h), pygame.SRCALPHA)
            draw_skull_die(tmp, cell // 2, int(h * 0.50), px, difficulty=diff, neutral=neu)
            tmp = pygame.transform.rotate(tmp, rot)
            strip.blit(tmp, (cx - tmp.get_width() // 2, cy - tmp.get_height() // 2))
        else:
            draw_skull_die(strip, cx, cy, px, difficulty=diff, neutral=neu)
        if not rot:
            _label(strip, lab, i * cell + 8, h - 22,
                   col=(220, 224, 240) if night else (40, 30, 26))
    return strip


def build_sheet():
    px_big = 96
    px_true = 56                              # ~in-game pillar-skull scale
    big_day = _row(px_big, night=False)
    big_night = _row(px_big, night=True)
    true_day = _row(px_true, night=False)
    rot_day = _row(px_big, night=False, rot=24)   # tumbling read at angle

    pad, head = 24, 64
    rows = [("2x — DAY", big_day), ("2x — NIGHT", big_night),
            ("tumbling read (rotated 24deg) — DAY", rot_day),
            (f"true ~{px_true}px crop — DAY (in-game scale)", true_day)]
    W = max(r.get_width() for _, r in rows) + pad * 2
    Ht = head + sum(r.get_height() + 30 for _, r in rows) + pad
    sheet = pygame.Surface((W, Ht))
    sheet.fill((26, 24, 30))
    _label(sheet, "SKULL-KING DIE — settled difficulty faces 6..10 + neutral pre-roll", pad, 14, sz=22)
    _label(sheet, "base crown:2 (lit heart-relic) · RAISED bone numeral PLATE (hero, ~56% width, ink keyline, "
                  "cool night rim) · WHITE digit + heat ONLY in eyes · breaching horns = silhouette safety net",
                  pad, 40, sz=13, col=(190, 198, 212))
    y = head
    for lab, r in rows:
        _label(sheet, lab, pad, y, sz=14, col=(190, 198, 212))
        y += 24
        sheet.blit(r, (pad, y))
        y += r.get_height() + 6
    out = os.path.join(OUT, "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    build_sheet()
