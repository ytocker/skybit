"""Look-dev mockup: the dice-clown presenter's EVOLVED "BOSS" form (ROUND 2).

The approved FRIENDLY presenter — tile #13 of `render_jester_variants.py`
("Plum & Lime — FINAL (no shadow)") — fronts an EASY route. This sheet explores
his EVOLVED BOSS form: the bigger, MEANER jester the player meets later, who
offers a MUCH HARDER route. The brief is a PLAYFUL-MENACING mini-boss (casual-
arcade, NOT horror-gore) who still reads as the SAME clown, evolved.

ROUND 2 reaction to the art-director critique. The single fatal blocker in
round 1 was the body aura: it was a bright near-WHITE additive DISC, so the
boss read HOLY/spotlit and at 1x collapsed into "a glowing ball with legs."
This round INVERTS it — the boss now LOOMS OUT OF SHADOW:
  - The aura is built FROM the boss's own SILHOUETTE (not a circular disc): the
    figure is rendered first, its alpha mask taken, then the aura is grown OUT
    of that shape so it edge-lights the body instead of haloing a circle.
  - DARK CORE: the area right behind the body is pushed DARKER than the sky (a
    deep crimson-black / bruise-violet), so the figure reads as shadow.
  - SATURATED EDGE RIM: a danger-colour ring (crimson / violet / fiery / cold)
    hugs the silhouette edge and falls off OUTWARD into smoke — this rim is the
    legibility carrier that keeps the dark boss crisp against the day sky.
  - SMOKE + EMBERS, not a clean radial: low-alpha smoke wisps licking up off the
    shoulders/cap plus a few drifting additive embers. Clean glow = holy; smoke
    + embers = danger.

Panel 0 is the UNCHANGED original #13 (the friendly easy-route presenter) for
side-by-side comparison. Panels 1-5 are five distinct evolved bosses. Every
boss is:
  - PHYSICALLY LARGER — the whole jester FIGURE layer is rendered then scaled up
    ~1.3-1.5x inside a taller panel, while the real parrot stays the SAME size
    in every panel, so the boss visibly dwarfs both the parrot and #13.
  - MEANER — a `menace` face path: steeper low-angled brows, GLOWING eyes (a hot
    pupil + a coloured `blit_glow`), a wider jagged snarl with bigger FANGS.
  - CORRUPTED in palette — #13's plum/lime/gold deepened + desaturated + pushed
    toward each version's aura hue, still recognisably the same clown.
  - STILL PRESENTING the route DIE (the 3D cube + its yellow aura, upper-LEFT,
    LEFT arm raised to it) — the offer is unchanged, only the offerer is.

Nothing under `game/` is touched; we import the real kit and mutate no state.
Headless + deterministic. Output: docs/jester/boss_round_2.png.

    PYTHONPATH=. python tools/render_jester_boss.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from game.draw import lerp_color, blit_glow
from game.parrot import get_parrot
from tools.render_warren_mockup import shaped_palette

from tools.render_clown_dice import (
    _shade, DAY_PHASE, SS, VIEW_W, VIEW_H, VIEW_FEET_Y,
    _round_head, _nose,
)

# The whole approved jester kit — body, pose, caps, collar, costume, the die +
# its yellow aura — is reused verbatim so the boss stays in the SAME family.
from tools.render_jester_variants import (
    build_jester, cap_four_point, _bell, _cap_point,
    draw_cupped_die, _cheek,
)


# ── palette corruption ────────────────────────────────────────────────────────
# #13's plum/lime/gold pushed toward each version's danger hue: deepen (drag
# toward black), desaturate (drag toward the channel mean), then tint toward the
# aura colour. Still the same three-role costume — just corrupted — so the boss
# reads as the SAME clown gone bad, never a brand-new character.

BASE = dict(dark=(96, 44, 150), light=(132, 218, 116), gold=(250, 205, 72))


def _desat(c, amt):
    g = sum(c) / 3.0
    return tuple(int(ch + (g - ch) * amt) for ch in c)


def _deepen(c, amt):
    return tuple(int(ch * (1.0 - amt)) for ch in c)


def corrupt(c, hue, *, deep=0.32, desat=0.34, tint=0.30):
    """Deepen + desaturate + tint a base costume colour toward the danger `hue`."""
    c = _deepen(c, deep)
    c = _desat(c, desat)
    return lerp_color(c, hue, tint)


def corrupt_palette(hue, **kw):
    return {k: corrupt(v, hue, **kw) for k, v in BASE.items()}


# ── ominous body aura (the danger telegraph) ─────────────────────────────────
# Round 2 rebuild. The aura is grown FROM the boss's own SILHOUETTE so the boss
# LOOMS OUT OF SHADOW instead of being haloed by a bright disc:
#   1. DARK CORE — the silhouette is dilated and stamped DARK (deeper than the
#      sky) behind the figure, so the body reads as shadow against the day sky.
#   2. EDGE RIM — a saturated danger-colour ring hugs the silhouette edge and
#      falls off OUTWARD into smoke; this rim is the legibility carrier that
#      keeps the dark figure crisp. Brightest at the edge, never at the centre.
#   3. SMOKE + EMBERS — low-alpha smoke wisps lick up off the shoulders/cap and
#      a few additive embers drift, so it telegraphs DANGER (smoke), not HOLY
#      (a clean radial glow). `breathe` pulses everything so the aura is alive.

def _silhouette_mask(fig):
    """Binary-ish silhouette: the figure's own alpha, hard-thresholded, used as
    the seed shape the dark core + rim grow out of (so the aura hugs the BODY,
    not a circle)."""
    mask = pygame.mask.from_surface(fig, 40)
    sil = mask.to_surface(setcolor=(255, 255, 255, 255),
                          unsetcolor=(0, 0, 0, 0))
    return sil


def _grow(sil, px):
    """Cheap silhouette dilation: stamp the shape offset in a ring of directions
    so a fattened copy comes back. Used to push the dark core + rim OUTSIDE the
    body edge without a per-pixel morphology pass."""
    w, h = sil.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    for ang in range(0, 360, 30):
        dx = int(round(math.cos(math.radians(ang)) * px))
        dy = int(round(math.sin(math.radians(ang)) * px))
        out.blit(sil, (dx, dy))
    out.blit(sil, (0, 0))
    return out


def silhouette_aura(big, fig_big, cx, cy, hue, breathe, *, dark=(8, 4, 12),
                    rim=None, embers=True, smoke=True, seed=0, scl=1.0,
                    bulk=1.0):
    """Paint the ominous aura BEHIND the already-scaled figure `fig_big`, derived
    from its silhouette. `big` is the supersampled scene; `fig_big` is the boss
    layer at panel size; (cx, cy) is the torso centre on `big` in supersample px.
    `scl` carries the supersample factor (so the rim stays crisp); `bulk` is a
    mild figure-scale nudge (bigger boss → slightly bigger shadow). `rim` is the
    saturated edge colour (defaults to a lifted `hue`)."""
    # 1. A BIG AMORPHOUS DARK POOL the boss EMERGES FROM — NOT a body-hugging
    # halo. The art-director's gate (3 rounds): a silhouette-shaped dark core
    # hides behind the figure and a continuous bright rim reads HOLY. So instead
    # we lay a soft RADIAL shadow ellipse ~1.9x the figure's width, centred on the
    # boss and DARKER than the day sky, that the figure then sits INSIDE — it
    # emerges from darkness rather than wearing a dark coat. No bright rim at all;
    # the menace light leaks from WITHIN (the glowing eyes/snarl/seams).
    mask = pygame.mask.from_surface(fig_big, 40)
    rects = mask.get_bounding_rects()
    if rects:
        br = rects[0]
        for r in rects[1:]:
            br = br.union(r)
    else:
        br = fig_big.get_rect()
    pcx = cx
    pcy = cy + int(br.height * 0.12)              # bias down onto the body mass
    rx = int(br.width * 0.98)
    ry = int(br.height * 0.70)
    pool = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    steps = 24
    for i in range(steps):
        t = i / (steps - 1)                        # 0 = faint outer → 1 = dark core
        a = int((8 + 170 * t) * (0.9 + 0.1 * breathe))
        ex = max(2, int(rx * (1.0 - 0.9 * t)))
        ey = max(2, int(ry * (1.0 - 0.9 * t)))
        pygame.draw.ellipse(pool, (*dark, a),
                            (pcx - ex, pcy - ey, ex * 2, ey * 2))
    big.blit(_softscale(pool), (0, 0))

    # 3. SMOKE wisps licking UP off the shoulders/cap — low-alpha violet/black
    # tongues so the silhouette frays into danger, not a clean halo.
    rng = __import__('random').Random(seed * 6151 + 11)
    if smoke:
        smoke_col = lerp_color(dark, hue, 0.5)
        sw = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        for i in range(5):
            ox = cx + int(rng.uniform(-30, 30) * scl)
            oy = cy - int(rng.uniform(20, 54) * scl)
            puff_r = int(rng.uniform(12, 22) * scl)
            climb = int(((breathe * 18 + i * 7) % 26) * scl)
            for k in range(4):
                rr = puff_r - k * (puff_r // 5)
                if rr < 2:
                    break
                a = int((34 + 16 * breathe) * (1 - k / 4))
                pygame.draw.circle(sw, (*smoke_col, a),
                                   (ox + rng.randint(-4, 4),
                                    oy - climb - k * int(6 * scl)), rr)
        big.blit(sw, (0, 0))

    if not embers:
        return
    # A few floating embers rising out of the aura — the boss is smouldering.
    ember_col = _shade(hue, 40)
    for i in range(6):
        a0 = rng.uniform(0, math.tau)
        rad = rng.uniform(22, 58) * scl
        drift = breathe * 8 + i * 3
        ex = int(cx + math.cos(a0) * rad)
        ey = int(cy + math.sin(a0) * rad * 0.86) - int((drift % 16) * scl)
        tw = 0.5 + 0.5 * math.sin(breathe * 6.0 + i * 1.7)
        sz = max(2, int((2 + 1.5 * tw) * scl))
        spark = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
        al = int(70 + 80 * tw)
        pygame.draw.circle(spark, (*ember_col, al), (sz * 2, sz * 2), sz)
        pygame.draw.circle(spark, (*_shade(ember_col, 60), al), (sz * 2, sz * 2),
                           max(1, sz // 2))
        big.blit(spark, (ex - sz * 2, ey - sz * 2),
                 special_flags=pygame.BLEND_ADD)


def _softscale(surf):
    """Soften a mask-derived layer by down/up bouncing it, cheaply blurring the
    hard dilation edges so the dark core + rim feather instead of stairstepping."""
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, w // 6), max(1, h // 6)))
    return pygame.transform.smoothscale(small, (w, h))


# ── the MEAN boss face (overrides the friendly #13 face) ─────────────────────
# A `menace` path: keep the SAME face anatomy as #13 (so it's the same clown) but
# swing every cue to MEAN — steep low brows knitting toward the nose, GLOWING
# eyes (a coloured glow under a hot slit pupil), and a WIDE JAGGED grin with two
# big fangs. The friendly #13 face stays untouched (panel 0 uses `naughty_face`).

def _glow_eye(surf, x, y, glow_col, *, look, narrow=False):
    """A menacing GLOWING eye: a coloured glow halo, a dark socket, then a hot
    bright slit pupil shoved toward the die (sidelong). `narrow` gives the hollow,
    quieter wraith read (a thin glowing slit, no full sclera)."""
    blit_glow(surf, x, y, 7, glow_col, alpha=150)
    if narrow:
        # Hollow glowing slit — no white sclera. Reads cold + empty.
        pygame.draw.ellipse(surf, (10, 8, 14), (x - 5, y - 3, 10, 7))
        pygame.draw.ellipse(surf, glow_col, (x - 4 + look, y - 2, 6, 4))
        pygame.draw.circle(surf, (255, 255, 255),
                           (x + look, y), 1)
        return
    # Dark recessed socket so the glow reads as light coming FROM the eye.
    pygame.draw.ellipse(surf, (16, 10, 18), (x - 6, y - 5, 12, 11))
    # Hot bright pupil (the glow's source) jammed to the die-side corner.
    px = x + look
    pygame.draw.circle(surf, glow_col, (px, y + 1), 4)
    pygame.draw.circle(surf, _shade(glow_col, 130), (px, y + 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), (px - 1, y - 1), 1)


def menace_face(surf, cx, hy, hr, *, nose_col, glow_col, fang_xtra=0,
                narrow_eyes=False):
    """Paint the MEAN boss expression. SAME geometry as #13's naughty_face — the
    nose, the cheeks, the lopsided sly mouth seat — so it's clearly the same
    clown, but every cue swung MEAN: steep low brows knitting toward the nose,
    glowing eyes, a wider JAGGED grin with two big fangs. `fang_xtra` lengthens
    the fangs (demon read); `narrow_eyes` gives the hollow wraith slit."""
    ex = max(6, hr // 2)
    look = -3
    # NO cheek blush on the boss — the pink apples are #13's "cute" cue and kept
    # dragging the menace back toward friendly. The mean read is carried by the
    # glowing eyes + anger-V brows + fang snarl alone.

    for s in (-1, 1):
        exx = cx + s * ex
        _glow_eye(surf, exx, hy, glow_col, look=look, narrow=narrow_eyes)
        # MEAN brow — the universal anger shape #13 was carefully kept OUT of:
        # the INNER (nose-side) end drops LOW and the outer rides high, knitting
        # into a hard down-and-in "V" over the nose. Heavy dark ink for weight.
        inner = (exx - s * 1, hy - 8)        # inner end LOW (anger)
        outer = (exx + s * 11, hy - 17)      # outer end HIGH
        pygame.draw.line(surf, (24, 14, 22), inner, outer, 3)
        # A second short stroke thickening the inner knit so the scowl reads bold.
        pygame.draw.line(surf, (24, 14, 22), inner,
                         (exx - s * 4, hy - 10), 3)

    _nose(surf, cx, hy + 3, 4, nose_col)

    # A WIDER, more JAGGED open grin than #13 — a snarl. The die-side corner still
    # rides highest (lopsided sly), but the lip is a sawtooth and TWO big fangs
    # drop from the tooth row for the mean edge.
    mw = 13
    my = hy + 12
    l_corner = (cx - mw - 1, my - 3)
    r_corner = (cx + mw, my - 1)
    bottom = (cx, my + 10)
    mouth_poly = [l_corner, (cx - 6, my + 1), (cx + 6, my + 1), r_corner,
                  (cx + 7, my + 5), bottom, (cx - 7, my + 5)]
    pygame.draw.polygon(surf, (84, 16, 28), mouth_poly)
    # Jagged tooth band along the top of the grin (a row of points, not a smooth
    # band) so the grin reads as a snarl.
    top_teeth = [l_corner]
    for k in range(7):
        t = k / 6.0
        tx = l_corner[0] + (r_corner[0] - l_corner[0]) * t
        ty = my + (0 if k % 2 == 0 else 3)
        top_teeth.append((tx, ty))
    top_teeth.append((r_corner[0], r_corner[1] + 3))
    top_teeth.append((l_corner[0], l_corner[1] + 3))
    pygame.draw.polygon(surf, (250, 246, 236), top_teeth)
    pygame.draw.polygon(surf, _shade((250, 246, 236), -80), top_teeth, 1)
    # TWO big fangs hanging into the dark mouth (one each side), longer than #13's
    # single fang. `fang_xtra` drops them further for the demon read.
    for fs in (-1, 1):
        fx = cx + fs * 6
        fang = [(fx - 2, my + 3), (fx + 2, my + 3),
                (fx, my + 9 + fang_xtra)]
        pygame.draw.polygon(surf, (252, 250, 244), fang)
        pygame.draw.polygon(surf, _shade((252, 250, 244), -80), fang, 1)
    # The lip as a tight MEAN crescent — corners flicked up, centre dipped, but
    # drawn in a darker bloodier line than #13's friendly MOUTH.
    lip = []
    for k in range(13):
        t = k / 12.0
        lx = l_corner[0] - 2 + (r_corner[0] + 2 - (l_corner[0] - 2)) * t
        ly = (l_corner[1] - 2) + ((r_corner[1] - 1) - (l_corner[1] - 2)) * t \
            + (1.0 - (2.0 * t - 1.0) ** 2) * 10.0
        lip.append((lx, ly))
    pygame.draw.lines(surf, (150, 30, 44), False, lip, 3)


# ── boss cap add-ons (horns / taller crown) ──────────────────────────────────
# Drawn as wrappers that first lay the approved four-point cap, then add the
# version-specific menace silhouette (small horns through the cap, or a taller
# crown-spike) so each boss owns a distinct head shape while staying a jester.

def _horn(surf, base, tip, col):
    """A small curved menace horn — a tapered dark cone with a lit front edge."""
    bx, by = base
    tx, ty = tip
    midx = (bx + tx) // 2 + (4 if tx > bx else -4)
    midy = (by + ty) // 2
    pts = [(bx - 4, by), (bx + 4, by), (midx + 2, midy), (tx, ty)]
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, _shade(col, 40),
                        [(bx - 4, by), (bx, by), (midx, midy), (tx, ty)])
    pygame.draw.polygon(surf, _shade(col, -70), pts, 2)


def cap_demon(surf, cx, base_y, hr, cols):
    """The approved four-point fool's cap with two small horns pushed THROUGH it —
    the demon-jester read."""
    cap_four_point(surf, cx, base_y, hr, cols)
    horn = (28, 18, 30)
    _horn(surf, (cx - 13, base_y - 4), (cx - 24, base_y - 26), horn)
    _horn(surf, (cx + 13, base_y - 4), (cx + 24, base_y - 26), horn)


def cap_crown(surf, cx, base_y, hr, cols):
    """A taller, more COMMANDING cap for the Genie-King boss: the four-point cap
    plus a central upright crown-spike rising between the points (regal menace),
    each tipped with a dark-gold bell. Reads as a king's fool, not a floppy one."""
    a, b, c, d = cols
    # Central tall spike FIRST so the splayed points overlap its base.
    spike = [(cx - 9, base_y - 2), (cx + 9, base_y - 2),
             (cx + 4, base_y - 40), (cx - 4, base_y - 40)]
    pygame.draw.polygon(surf, a, spike)
    pygame.draw.polygon(surf, _shade(a, 45),
                        [(cx - 9, base_y - 2), (cx - 1, base_y - 2),
                         (cx - 2, base_y - 40)])
    pygame.draw.polygon(surf, _shade(a, -65), spike, 2)
    _bell(surf, cx, base_y - 42, r=4, col=_shade(c, -10))
    # Two tall side prongs flanking the spike — a three-pronged crown silhouette.
    for s in (-1, 1):
        _cap_point(surf, cx, base_y, hr, s * 26, -22, b, span=12)


# ── the boss head (menace face + version cap) ────────────────────────────────
# Mirrors render_jester_variants._draw_tilted_head but routes through menace_face
# instead of the friendly naughty_face, and lets each version override the cap.

def _shadow_eyes(surf, cx, hy, hr, glow_col):
    """Wraith face: NO lit features — only two cold glowing pinpoint eyes burning
    out of a head already sunk in shadow. Silhouette + eyes carry the read."""
    ex = max(6, hr // 2)
    for s in (-1, 1):
        x = cx + s * ex
        blit_glow(surf, x, hy, 9, glow_col, alpha=190)
        pygame.draw.circle(surf, glow_col, (x - 2, hy), 2)
        pygame.draw.circle(surf, (255, 255, 255), (x - 2, hy), 1)


def _draw_boss_head(surf, cx, cy, hr, skin, cap_fn, cap_cols, tilt_deg,
                    *, nose_col, glow_col, fang_xtra=0, narrow_eyes=False,
                    shadow_face=False):
    pad = 80
    scratch = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    sx, sy = pad, pad
    _round_head(scratch, sx, sy, hr, skin, blush=False)
    cap_fn(scratch, sx, sy - hr + 7, hr, cap_cols)
    if shadow_face:
        # Sink the whole head into shadow (a dark wash clipped to the head disc)
        # so it reads as a near-silhouette, THEN burn the cold eyes on top — the
        # wraith is a shape with two glowing eyes, not a lit grey clown.
        veil = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
        pygame.draw.circle(veil, (6, 6, 12, 215), (sx, sy), hr + 1)
        scratch.blit(veil, (0, 0))
        _shadow_eyes(scratch, sx, sy, hr, glow_col)
    else:
        menace_face(scratch, sx, sy, hr, nose_col=nose_col, glow_col=glow_col,
                    fang_xtra=fang_xtra, narrow_eyes=narrow_eyes)
    rot = pygame.transform.rotate(scratch, tilt_deg)
    surf.blit(rot, (cx - rot.get_width() // 2, cy - rot.get_height() // 2))


def _broad_shoulders(surf, cx, hip_y, dark, light, gold, *, span, hunch):
    """Slabs of extra deltoid mass for the BRUTE: two heavy quartered shoulder
    plates bulging out past the collar, with a hunched neck-hump between them, so
    the silhouette reads as a wide brawler — not just a taller #13."""
    sh_y = hip_y - 56
    for s in (-1, 1):
        ox = cx + s * span
        plate = [(cx + s * 6, sh_y - 6), (ox, sh_y - hunch),
                 (ox + s * 3, sh_y + 16), (cx + s * 8, sh_y + 20)]
        pygame.draw.polygon(surf, _shade(dark, -18), plate)
        pygame.draw.polygon(surf, _shade(dark, -55), plate, 2)
        # Quartered lime wedge so the plate stays harlequin, not a blank slab.
        wedge = [(ox, sh_y - hunch), (ox + s * 3, sh_y + 16),
                 (cx + s * 9, sh_y + 6)]
        pygame.draw.polygon(surf, _shade(light, -28), wedge)
        _bell(surf, ox + s * 1, sh_y - hunch + 2, r=3, col=_shade(gold, -10))
    # Hunched trapezius hump rising between the shoulders behind the neck.
    hump = [(cx - span + 6, sh_y - 4), (cx, sh_y - hunch - 8),
            (cx + span - 6, sh_y - 4)]
    pygame.draw.polygon(surf, _shade(dark, -30), hump)


def build_boss(surf, cx, feet_y, hand_up, *, dark, light, gold, cap_fn,
               glow_col, nose_col=(150, 30, 30), fang_xtra=0,
               narrow_eyes=False, skin=(214, 168, 150), shadow_face=False,
               mass=1.0, lean=0.0, head_extra_tilt=0):
    """Draw the EVOLVED boss jester: the approved chunky body/pose from
    build_jester, but with the costume's HEAD swapped for the menace head. We
    reuse build_jester for everything from the neck down (so the body, pose,
    collar, costume, harlequin legs and presenting arms are pixel-family with
    #13), then OVER-draw the boss head on top with the mean glowing face + the
    version cap. `skin` is dulled toward a corpse-grey so the face reads corrupted.
    `mass` widens the torso (Brute brawler); `lean` shears the upper body off
    vertical (Corrupted's broken/unstable posture); `head_extra_tilt` cocks the
    head further. Everything is drawn to a scratch so mass/lean can transform the
    whole figure before it lands on `surf`, keeping the feet planted."""
    scratch = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    # Body, pose, collar, costume, legs, arms — straight from the approved kit so
    # the boss is unmistakably the same jester. Its friendly head is then painted
    # OVER by the menace head below (same head seat math as build_jester).
    build_jester(scratch, cx, feet_y, hand_up, dark=dark, light=light, gold=gold,
                 cap_fn=cap_four_point, motif="panels", collar="scalloped",
                 variant="browcock", collar_in_gold=True, skin=skin,
                 nose_col=nose_col)
    # Re-derive the head seat exactly as build_jester does, then over-draw the
    # mean glowing boss head + the version cap on top of the friendly one.
    hip_dx = -6
    hip_y = feet_y - 84
    hip_cx = cx + hip_dx
    neck_y = hip_y - 50
    hr = 22
    head_cx = hip_cx - 4
    hy_center = neck_y - hr
    cap_cols = (dark, light, gold, dark)
    if mass > 1.02:
        _broad_shoulders(scratch, hip_cx, hip_y, dark, light, gold,
                         span=int(26 * mass), hunch=int(22 * mass))
    _draw_boss_head(scratch, head_cx, hy_center, hr, skin, cap_fn, cap_cols,
                    -8 + head_extra_tilt, nose_col=nose_col, glow_col=glow_col,
                    fang_xtra=fang_xtra, narrow_eyes=narrow_eyes,
                    shadow_face=shadow_face)

    # Widen the torso about the centreline for the Brute's brawler mass, and shear
    # the upper body off vertical for the Corrupted's broken stance — both pivot
    # about the FEET so the boss stays planted while the bulk/lean grows upward.
    if mass > 1.02 or abs(lean) > 0.001:
        if mass > 1.02:
            w = int(PANEL_W * mass)
            wide = pygame.transform.smoothscale(scratch, (w, PANEL_H))
            scratch = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
            scratch.blit(wide, (int(cx - cx * mass), 0))
        if abs(lean) > 0.001:
            sheared = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
            for y in range(0, feet_y, 2):
                # Top of the body shifts most; nothing below the feet shifts.
                t = max(0.0, (feet_y - y) / float(feet_y))
                dx = int(lean * 48 * (t ** 1.6))
                sheared.blit(scratch, (dx, y), (0, y, PANEL_W, 2))
            sheared.blit(scratch, (0, feet_y), (0, feet_y, PANEL_W,
                                                PANEL_H - feet_y))
            scratch = sheared
    surf.blit(scratch, (0, 0))


# ── the five evolved bosses ──────────────────────────────────────────────────
# Each entry: a corrupted palette tinted toward its danger hue, an aura hue +
# dark, a version cap, the eye-glow colour and face flavour, and a FIGURE SCALE
# (how much bigger than #13 the boss looms). Panel 0 is the untouched #13.

CRIMSON = (150, 24, 24)
VIOLET = (118, 30, 158)
FIRE = (224, 96, 20)
SMOKE = (40, 36, 52)
PURPLE = (96, 36, 168)

BOSSES = [
    # 1 — THE BRUTE (round 2: was weakest — now the BIGGEST + MEANEST mass): real
    # brawler bulk via `mass` (broad quartered shoulder plates + a hunched neck-
    # hump), the tallest `scale`, a hard down-V scowl with long fangs. Dark-RED
    # ominous aura: deep crimson-black core, crimson edge rim, red embers.
    dict(name="The Brute",
         vibe="brawler mass · hunched · DARK-RED rim aura · snarl",
         pal=corrupt_palette(CRIMSON, deep=0.40, desat=0.28, tint=0.36),
         aura_hue=(200, 30, 36), aura_dark=(26, 6, 10), rim=(200, 30, 46),
         glow=(255, 70, 50), cap=cap_four_point, scale=1.52, fang_xtra=3,
         mass=1.22, head_tilt=-3),
    # 2 — THE CORRUPTED (round 2: now UNSTABLE + BROKEN, differentiated from the
    # upright King): an off-vertical `lean` so the posture reads wrong/glitched,
    # bright glowing seam-tears, magenta eye-glow. Magenta/violet-black rim aura.
    dict(name="The Corrupted",
         vibe="ASYMMETRIC broken stance · glitch seams · magenta rim",
         pal=corrupt_palette(VIOLET, deep=0.34, desat=0.46, tint=0.42),
         aura_hue=(150, 24, 168), aura_dark=(18, 4, 24), rim=(214, 40, 220),
         glow=(244, 80, 240), cap=cap_four_point, scale=1.36, fang_xtra=1,
         seams=True, lean=0.40, head_tilt=-6),
    # 3 — THE DEMON JESTER (round 2: best face kept — fangs + yellow eye-glow —
    # but PLUM/LIME pulled back so it stops drifting olive/khaki): lighter deepen
    # + a plum/lime re-tint pass on top of the fire corruption. Fiery orange-red
    # rim aura, glowing yellow eyes, the longest fangs.
    dict(name="The Demon Jester",
         vibe="horns · PLUM/LIME + fiery rim · yellow eyes · long fangs",
         pal={"dark": lerp_color(corrupt(BASE["dark"], FIRE, deep=0.22,
                                         desat=0.16, tint=0.22), VIOLET, 0.30),
              "light": lerp_color(corrupt(BASE["light"], FIRE, deep=0.16,
                                          desat=0.14, tint=0.18),
                                  (132, 218, 116), 0.34),
              "gold": corrupt(BASE["gold"], FIRE, deep=0.18, desat=0.10,
                              tint=0.20)},
         aura_hue=(232, 92, 18), aura_dark=(30, 8, 4), rim=(248, 120, 30),
         glow=(255, 206, 40), cap=cap_demon, scale=1.40, fang_xtra=5),
    # 4 — THE SHADOW WRAITH (round 2: face DROPPED INTO SHADOW — only the eyes
    # glow): `shadow_face` sinks the head to a near-silhouette and burns two cold
    # violet/cyan pinpoints; no lit clown face. Cold smoky-black rim aura with
    # cool embers (it smoulders cold, not warm).
    dict(name="The Shadow Wraith",
         vibe="face IN SHADOW · only eyes glow · cold smoke rim",
         pal=corrupt_palette(SMOKE, deep=0.66, desat=0.60, tint=0.50),
         aura_hue=(60, 56, 92), aura_dark=(4, 4, 10), rim=(96, 150, 200),
         glow=(150, 220, 255), cap=cap_four_point, scale=1.42,
         shadow_face=True, embers=True, skin=(120, 116, 132), head_tilt=2),
    # 5 — THE GENIE KING (round 2: UPRIGHT + GOLD-HEAVY + CROWNED, differentiated
    # from the Corrupted): no lean, the crown cap, a gold-lifted regal palette and
    # a commanding royal-VIOLET rim aura. The climactic hard-route boss — regal,
    # not broken.
    dict(name="The Genie King",
         vibe="UPRIGHT · gold-heavy · CROWNED · royal-violet rim",
         pal={**corrupt_palette(PURPLE, deep=0.26, desat=0.22, tint=0.28),
              "gold": (236, 184, 56)},
         aura_hue=(120, 44, 206), aura_dark=(16, 6, 30), rim=(176, 96, 244),
         glow=(214, 130, 255), cap=cap_crown, scale=1.44, fang_xtra=1,
         head_tilt=-2),
]


# ── per-cell scene ────────────────────────────────────────────────────────────
# A taller-than-source panel (so the bigger bosses fit), the same day clearing,
# the boss figure rendered onto its own layer then SCALED UP and composited over
# its body aura, the route die floating upper-left, and the real parrot un-scaled
# for the size comparison.

PANEL_W = VIEW_W
PANEL_H = VIEW_H + 56          # taller so the looming bosses are not clipped
FEET_Y = PANEL_H - 26


def _scene_bg(big, bw, bh, idx):
    palette = shaped_palette(DAY_PHASE)
    g_y = int(FEET_Y * SS) + 6 * SS
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'],
                                         palette['sky_bot'], t), (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'],
                                         palette['ground_mid'], t), (0, y),
                         (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))
    hill = pygame.Surface((bw, 30 * SS), pygame.SRCALPHA)
    hc = _shade(palette['ground_mid'], 22)
    for hx, hw, hh in ((40, 90, 18), (130, 110, 22), (185, 80, 16)):
        pygame.draw.ellipse(hill, (*hc, 160),
                            ((hx - hw) * SS, 0, hw * 2 * SS, hh * 2 * SS))
    big.blit(hill, (0, g_y - 14 * SS))
    tuft = _shade(palette['ground_top'], 22)
    rng = __import__('random').Random(idx * 131 + 7)
    for _ in range(10):
        tx = rng.randint(8, PANEL_W - 8) * SS
        ty = g_y + rng.randint(3, max(4, bh // SS - FEET_Y - 4)) * SS
        for k in (-3, 0, 3):
            pygame.draw.line(big, tuft, (tx + k * SS, ty),
                             (tx + k * SS, ty - rng.randint(4, 7) * SS),
                             max(1, SS))


def render_original(idx):
    """Panel 0: the UNCHANGED #13 friendly presenter, drawn in this taller panel
    at the SAME figure size as the source sheet (no scale-up), for comparison."""
    bw, bh = PANEL_W * SS, PANEL_H * SS
    big = pygame.Surface((bw, bh))
    _scene_bg(big, bw, bh, idx)

    layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    jester_cx = PANEL_W // 2 + 12
    die_x = jester_cx - 66
    die_base_y = 36
    hand_up = (die_x + 6, 76 + (PANEL_H - VIEW_H))
    # The #13 spec verbatim (friendly face), seated so its FEET land on FEET_Y.
    build_jester(layer, jester_cx, FEET_Y, hand_up,
                 dark=BASE['dark'], light=BASE['light'], gold=BASE['gold'],
                 cap_fn=cap_four_point, motif="quartered", collar="scalloped",
                 variant="browcock", collar_in_gold=True)
    draw_cupped_die(layer, die_x, die_base_y, idx * 1.7 + 2.0)
    _blit_parrot(layer)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


def _blit_parrot(layer):
    """The real parrot, ALWAYS the same size, low on the RIGHT — the scale ruler
    that proves the bosses dwarf both it and #13."""
    bird = get_parrot(1, -10)
    bird = pygame.transform.smoothscale(
        bird, (int(bird.get_width() * 0.92), int(bird.get_height() * 0.92)))
    layer.blit(bird, (PANEL_W - 22 - bird.get_width() // 2,
                      (FEET_Y - 64) - bird.get_height() // 2))


def render_boss(spec, idx):
    bw, bh = PANEL_W * SS, PANEL_H * SS
    big = pygame.Surface((bw, bh))
    _scene_bg(big, bw, bh, idx)

    layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    jester_cx = PANEL_W // 2 + 12
    die_x = jester_cx - 66
    die_base_y = 36

    breathe = 0.5 + 0.5 * math.sin((idx * 1.7 + 2.0) * 1.3)
    scale = spec["scale"]

    # The boss FIGURE on its own transparent layer so we can scale it UP (bigger
    # = more menacing) while the parrot + die stay at base size. Feet are seated
    # at a virtual baseline that, after scaling about the feet, lands on FEET_Y.
    fig = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    base_feet = FEET_Y
    hand_up = (die_x + 6, 76 + (PANEL_H - VIEW_H))
    pal = spec["pal"]
    build_boss(fig, jester_cx, base_feet, hand_up,
               dark=pal["dark"], light=pal["light"], gold=pal["gold"],
               cap_fn=spec["cap"], glow_col=spec["glow"],
               fang_xtra=spec.get("fang_xtra", 0),
               narrow_eyes=spec.get("narrow_eyes", False),
               skin=spec.get("skin", (214, 168, 150)),
               shadow_face=spec.get("shadow_face", False),
               mass=spec.get("mass", 1.0), lean=spec.get("lean", 0.0),
               head_extra_tilt=spec.get("head_tilt", 0))
    if spec.get("seams"):
        _add_seams(fig, jester_cx, base_feet, spec["glow"])

    # Place the boss onto a PANEL-sized layer at its final scaled size + position
    # (scaled ABOUT THE FEET so it looms taller/broader yet stays planted on the
    # ground line). We need this composited layer FIRST because the ominous aura
    # is grown out of the boss's own SILHOUETTE — so it edge-lights the BODY, not
    # a circle. Round-1's bright circular disc read holy; this reads as shadow.
    sw, sh = int(PANEL_W * scale), int(PANEL_H * scale)
    fig_big = pygame.transform.smoothscale(fig, (sw, sh))
    off_x = int(jester_cx - jester_cx * scale)
    off_y = int(base_feet - base_feet * scale)
    boss_layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    boss_layer.blit(fig_big, (off_x, off_y))

    # Supersample-resolution silhouette of just-the-boss drives the aura on the
    # smooth `big` surface. Torso centre (in supersample px) seeds smoke/embers.
    boss_ss = pygame.transform.smoothscale(boss_layer, (bw, bh))
    torso_x = int(jester_cx * SS)
    torso_y = int((FEET_Y - 70) * SS)
    silhouette_aura(big, boss_ss, torso_x, torso_y, spec["aura_hue"], breathe,
                    dark=spec["aura_dark"], rim=spec.get("rim"),
                    embers=spec.get("embers", True),
                    smoke=spec.get("smoke", True), seed=idx, scl=SS,
                    bulk=0.85 + 0.35 * scale)

    # Boss over its own aura, then the route DIE + its yellow aura (unchanged, at
    # BASE scale — the offer is identical to #13's) and the un-scaled parrot.
    big.blit(boss_ss, (0, 0))
    overlay = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    draw_cupped_die(overlay, die_x, die_base_y, idx * 1.7 + 2.0)
    _blit_parrot(overlay)
    big.blit(pygame.transform.smoothscale(overlay, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


def _add_seams(surf, cx, feet_y, glow):
    """Glowing corruption CRACKS across the Corrupted boss's torso — a few
    branching bright seams so the body reads as fracturing with corruption."""
    hip_y = feet_y - 84
    top = hip_y - 50
    rng = __import__('random').Random(424)
    for _ in range(4):
        x0 = cx + rng.randint(-22, 22)
        y0 = top + rng.randint(2, 8)
        pts = [(x0, y0)]
        for _ in range(3):
            x0 += rng.randint(-6, 6)
            y0 += rng.randint(8, 16)
            pts.append((x0, y0))
        pygame.draw.lines(surf, _shade(glow, 60), False, pts, 2)
        pygame.draw.lines(surf, (255, 240, 255), False, pts, 1)


# ── sheet layout ──────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    cells = []
    captions = []
    cells.append(render_original(0))
    captions.append(("current — EASY route", "#13 plum/lime · friendly grin "
                     "· the un-evolved presenter"))
    for i, spec in enumerate(BOSSES, start=1):
        cells.append(render_boss(spec, i))
        captions.append((spec["name"], spec["vibe"]))

    cols, rows = 3, 2
    sw, sh = int(PANEL_W * 3.1), int(PANEL_H * 3.1)

    PAD = 48
    GAP = 26
    TITLE_H = 100
    CAP_H = 70
    FOOT_H = PANEL_H + 40

    canvas_w = PAD * 2 + cols * sw + (cols - 1) * GAP
    canvas_h = (PAD * 2 + TITLE_H + rows * (sh + CAP_H) + (rows - 1) * GAP
                + FOOT_H)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((20, 16, 24))

    f_title = pygame.font.SysFont(None, 74, bold=True)
    f_sub = pygame.font.SysFont(None, 32, bold=True)
    f_cap = pygame.font.SysFont(None, 40, bold=True)
    f_caps = pygame.font.SysFont(None, 28, bold=True)

    title = f_title.render(
        "DICE JESTER — EVOLVED BOSS form (round 4 — amorphous shadow pool, no rim)", True, (252, 226, 226))
    canvas.blit(title, (PAD, PAD - 2))
    sub = f_sub.render(
        "Round 2 — INVERTED the aura: the boss now LOOMS OUT OF SHADOW. The aura "
        "is grown from the boss's own SILHOUETTE — a DARK crimson/bruise core "
        "(deeper than the sky) + a saturated danger-colour EDGE RIM + smoke "
        "wisps + embers — never a bright disc. Brute = brawler mass + snarl; "
        "Corrupted = broken/asymmetric + glitch-seams; Demon = plum/lime + fiery "
        "fangs; Wraith = face in shadow, only eyes glow; King = upright, gold, "
        "crowned. Parrot kept the SAME size for scale. Still presents the die.",
        True, (196, 190, 200))
    canvas.blit(sub, (PAD, PAD + 54))

    y0 = PAD + TITLE_H
    strong_cells = {}
    STRONG = {2, 3, 5}            # the three to push: Corrupted, Demon, King
    for i, cell in enumerate(cells):
        r, c = divmod(i, cols)
        cx = PAD + c * (sw + GAP)
        cy = y0 + r * (sh + CAP_H + GAP)
        scaled = pygame.transform.smoothscale(cell, (sw, sh))
        border = (210, 60, 60) if i in STRONG else (70, 60, 80)
        pygame.draw.rect(canvas, border,
                         pygame.Rect(cx - 2, cy - 2, sw + 4, sh + 4), 2)
        canvas.blit(scaled, (cx, cy))
        name, vibe = captions[i]
        tag = "0. " + name if i == 0 else f"{i}. {name}"
        cap = f_cap.render(tag, True, (245, 220, 200))
        canvas.blit(cap, (cx + (sw - cap.get_width()) // 2, cy + sh + 8))
        sub2 = f_caps.render(vibe, True, (190, 184, 196))
        canvas.blit(sub2, (cx + (sw - sub2.get_width()) // 2, cy + sh + 42))
        if i in (3, 5):
            strong_cells[i] = cell    # Demon + King — the 1x validation gate

    # TWO 1x insets — the aura-inversion validation GATE. At in-game scale each
    # strong boss must read as a DARK looming silhouette rimmed in danger-colour
    # (NOT a light disc). Demon (fiery) + King (royal-violet) shown side by side.
    foot_y = y0 + rows * (sh + CAP_H) + (rows - 1) * GAP + 16
    cap_intro = f_cap.render(
        "1x in-game scale — does it read DARK + ominous (not holy)?",
        True, (236, 196, 196))
    canvas.blit(cap_intro, (PAD, foot_y - 4))
    iy = foot_y + 40
    for n, (idx_s, label) in enumerate((
            (3, "The Demon Jester — fiery rim, plum/lime, fangs"),
            (5, "The Genie King — royal-violet rim, crowned"))):
        cell = strong_cells.get(idx_s)
        if cell is None:
            continue
        ix = PAD + n * (PANEL_W + 200)
        pygame.draw.rect(canvas, (210, 60, 60),
                         pygame.Rect(ix - 2, iy - 2, PANEL_W + 4,
                                     PANEL_H + 4), 2)
        canvas.blit(cell, (ix, iy))
        lab = f_caps.render(label, True, (206, 200, 210))
        canvas.blit(lab, (ix + PANEL_W + 16, iy + PANEL_H // 2 - 30))
        lab2 = f_caps.render("dark core · edge rim · smoke + embers",
                             True, (170, 164, 178))
        canvas.blit(lab2, (ix + PANEL_W + 16, iy + PANEL_H // 2 + 2))

    out_dir = os.path.join("docs", "jester")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "boss_round_4.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
