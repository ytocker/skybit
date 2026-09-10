"""IMPLET — chibi Skybit DEVIL boss, take B8 (the pocket gremlin imp).

A teeny acid-GREEN pear-shaped gremlin — the set's scale-FLOOR (smallest,
lightest figure of the ten) — hauling a fire-SPEAR comically too big for it.
Menace through pure gremlin GLEE plus the comedy of scale: a wee winged
trouble-maker that can barely lift its own weapon.

Drawn in the Skybit chibi house style — FLAT saturated fills, 1-2px hard ink
keylines, the dark-core -> fill -> top-left sheen triad (the `_marotte_ruff` /
Grim Sprout recipe), supersampled then smoothscaled for crisp AA, with a grown
1px silhouette outline so the imp pops on any sky.

DISTINCTNESS FROM GRIM SPROUT (the shipped reaper) is load-bearing here: that
one is a hooded orchid-violet imp dragging a great SCYTHE. This is a DEVIL, not
a reaper — a PEAR-shaped acid-green gremlin (no hood, no skull), with DEVIL
BAT-WINGS — a bold two-lobe membrane that anchors the 1x silhouette while the
acid-green torso stays the dominant value — a tiny pointy horn-nub + big pointed
ears (NOT a curved ram pair), a curl tail, and a slim FIRE-SPEAR (warm
flame-fork tip) it visibly STRAINS to lift, never a scythe. The palette is acid-green —
distinct from Pyrecrown's green soul-FLAME by being a body-green gremlin, not a
green-flame skull, and from any reaper-grey/violet.

Headless review renderer — not shipped. Imports the real game helpers so the
finish matches house style.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame

from game.draw import _shade_c, lerp_color, blit_glow  # noqa: F401
from game.config import PIPE_W

# ── IMPLET palette ("acid gremlin": acid-green body + plum-black wings) ───────
GREEN      = (120, 196,  72)   # #78C448 acid-green body
GREEN_DK   = ( 78, 142,  46)   # #4E8E2E olive shade
GREEN_HI   = (182, 232,  96)   # #B6E860 chartreuse sheen
CREAM      = (220, 232, 176)   # #DCE8B0 belly-cream
# Wing membrane warmed OUT of the near-black hole that vanished on night: a
# desaturated plum-grey reads as a lit HUE on both skies while still ranking
# darker than the acid-green body so green stays the dominant 1x value.
WING       = ( 86,  62,  96)   # #563E60 plum-grey membrane (was near-black)
WING_HI    = (150, 104, 168)   # #9668A8 brighter plum top-light (devil accent)
WING_DK    = ( 58,  40,  68)   # #3A2844 plum wing-shade core
HORN       = ( 28,  22,  30)   # ink-black horn-nub + ear-tips
EYE_ORANGE = (248, 168,  52)   # #F8A834 huge glowing gremlin eyes
EYE_HOT    = (255, 226, 150)   # eye hotspot
TONGUE     = (214,  72, 110)   # cheeky little tongue
SHAFT      = (122,  92,  58)   # warm-wood spear shaft
SHAFT_DK   = _shade_c(SHAFT, -55)
SHAFT_HI   = _shade_c(SHAFT, 55)
IRON       = (108, 112, 124)   # the spear's iron collar / socket
FLAME_OUT  = (255, 120,  36)   # warm fire-fork flame (NOT green — own the warm)
FLAME_MID  = (255, 176,  64)
FLAME_CORE = (255, 232, 168)
INK        = ( 28,  22,  30)   # #1C1620 hard keyline


def _triad_circle(surf, cx, cy, r, col, ss):
    """The house FORM recipe: a dark-core ring, the flat fill, and a ~1/3-radius
    top-left sheen — flat shapes that read sculpted without any gradient (the
    shared `_marotte_ruff`/Grim Sprout primitive)."""
    pygame.draw.circle(surf, _shade_c(col, -55), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), max(2, int(r - ss)))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - r * 0.32), int(cy - r * 0.32)),
                       max(1, int(r * 0.34)))


def _add_outline(src, outline_color=(28, 22, 30, 235)):
    """Grow a 1px dark outline from the alpha mask so the imp keeps a black-shape
    silhouette on any sky (the parrot `_add_outline` recipe)."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _flame_fork(surf, cx, ty, w, h, ss):
    """The fire-SPEAR tip: a slim THREE-pronged flame-fork (a fire trident), warm
    not green so it never echoes Pyrecrown's green soul-flame or Glitchfiend's
    neon. Each prong is a tapered teardrop flame with a glow halo; the centre
    prong rides tallest so the silhouette reads 'fork', not 'torch'."""
    blit_glow(surf, int(cx), int(ty - h * 0.45), int(h * 0.6), FLAME_OUT, 130)
    prongs = ((-1, 0.74), (0, 1.0), (1, 0.74))   # (x-dir, height-frac)
    for xd, hf in prongs:
        px = cx + xd * w * 0.62
        ph = h * hf
        # A leaf/teardrop flame: a fat bulb low that pinches up to a curled licking
        # point with a strong outward lean — never a straight spike (so it can't be
        # mistaken for an iron tine or a bone fork). Extra waist vertices give the
        # tongue its taper at 1x.
        tip   = (px + xd * w * 0.34, ty - ph)               # tip licks outward
        base_l = (px - w * 0.32, ty)
        base_r = (px + w * 0.32, ty)
        bulb_l = (px - w * 0.38, ty - ph * 0.30)            # widest point low
        bulb_r = (px + w * 0.30 + xd * w * 0.06, ty - ph * 0.34)
        waist_l = (px - w * 0.10 + xd * w * 0.14, ty - ph * 0.70)
        waist_r = (px + w * 0.06 + xd * w * 0.22, ty - ph * 0.66)
        flame = [base_l, bulb_l, waist_l, tip, waist_r, bulb_r, base_r]
        pygame.draw.polygon(surf, FLAME_OUT, flame)
        pygame.draw.polygon(surf, INK, flame, max(1, int(1.6 * ss)))
        # Inner warm core — a tall mid-orange tongue + a pale-yellow heart, both
        # tapering with the outer flame so it reads HOT and licking, not a chip.
        inner = [(px - w * 0.18, ty - ph * 0.06),
                 (px - w * 0.04 + xd * w * 0.16, ty - ph * 0.62),
                 (px + xd * w * 0.22, ty - ph * 0.86),
                 (px + w * 0.06 + xd * w * 0.18, ty - ph * 0.58),
                 (px + w * 0.18, ty - ph * 0.06)]
        pygame.draw.polygon(surf, FLAME_MID, inner)
        pygame.draw.polygon(surf, FLAME_CORE,
                            [(px - w * 0.08, ty - ph * 0.10),
                             (px + xd * w * 0.14, ty - ph * 0.60),
                             (px + w * 0.09, ty - ph * 0.10)])


def _bat_wing(surf, hinge, scale, ss, *, side):
    """One oversized DEVIL bat-wing as a BOLD TWO-LOBE membrane — the imp's 1x
    silhouette ANCHOR. The R1 wing was a finely-ribbed black FAN that turned to
    mush + swallowed the body at gameplay scale; here the anchor is the SHAPE: a
    fat upper lobe + lower lobe with ONE scallop notch between them, reach pulled
    in ~18%, swept up-and-back so clear sky cuts between the wing and the green
    torso (the torso must stay the dominant value). Only TWO bold finger spars,
    no rib noise. `side` (-1 left, +1 right) mirrors it. Wings, not a hood — the
    core devil/Grim-Sprout separator."""
    hx, hy = hinge
    sgn = side
    L = 70 * scale * ss            # wing reach (pulled in ~18% from R1's 86)
    # Two bold spars define a fat upper lobe and a shorter lower lobe. The single
    # notch between their tips is the only scallop — a clean bat read, not a fan.
    top_tip = (hx + sgn * L * 0.96, hy - L * 0.62)        # swept up + out + back
    notch   = (hx + sgn * L * 0.74, hy - L * 0.12)        # the one scallop cusp
    low_tip = (hx + sgn * L * 0.78, hy + L * 0.30)
    # Outer edge bows OUTWARD (control points) so each lobe reads convex + plump
    # rather than a straight wedge; we approximate the curve with extra vertices.
    up_bow  = (hx + sgn * L * 0.62, hy - L * 0.52)
    lo_bow  = (hx + sgn * L * 0.40, hy + L * 0.12)
    # Membrane: hinge -> arc out to the top tip -> in to the notch -> out to the
    # low tip -> bow back to a body-hugging anchor. The anchor sits TUCKED so a
    # sky gap opens between membrane and torso.
    anchor = (hx + sgn * L * 0.06, hy + L * 0.20)
    membrane = [(hx, hy), up_bow, top_tip, notch, low_tip, lo_bow, anchor]
    pygame.draw.polygon(surf, WING_DK, membrane)
    pygame.draw.polygon(surf, WING, [(x - sgn * ss, y + ss) for x, y in membrane])
    pygame.draw.polygon(surf, INK, membrane, max(2, int(2.6 * ss)))
    # Plum top-light skim along the leading spar so the wing reads as a LIT form.
    pygame.draw.line(surf, WING_HI, (hx, hy), top_tip, max(2, int(3.0 * ss)))
    # The TWO bold finger spars (only) so the bat structure reads without noise.
    for tx, ty in (top_tip, low_tip):
        pygame.draw.line(surf, INK, (hx, hy), (int(tx), int(ty)), max(2, int(2.4 * ss)))
        # A claw hook at each spar tip (gremlin tell) — bold, only two of them.
        ca = math.atan2(ty - hy, tx - hx)
        claw = (tx + math.cos(ca - sgn * 0.6) * 8 * scale * ss,
                ty + math.sin(ca - sgn * 0.6) * 8 * scale * ss)
        pygame.draw.line(surf, INK, (int(tx), int(ty)),
                         (int(claw[0]), int(claw[1])), max(2, int(2.6 * ss)))


# ── the imp + his oversized fire-spear ───────────────────────────────────────

def build_implet(scale=1.0, ss=3):
    """Render the gremlin + oversized fire-spear onto a tight transparent surface,
    then add a grown outline. The body is sized SMALL and the spear DELIBERATELY
    tall so the prop-to-body ratio reads as the comedy-of-scale gag, while the big
    bat-wings spread wide to anchor the 1x silhouette."""
    BW = int(250 * scale * ss)
    BH = int(420 * scale * ss)
    s = pygame.Surface((BW, BH), pygame.SRCALPHA)

    # Tiny pear body anchored low; the spear towers above it. The body LEANS into
    # the prop (a left tilt) so the comedy-of-scale strain reads as a pose, not a
    # caption — the imp is buckling under a weapon too big for it.
    body_cx = int(BW * 0.40)
    feet_y = int(BH * 0.94)
    head_r = int(34 * scale * ss)          # big head (chibi cute lever)
    belly_w = int(30 * scale * ss)         # pear: wide bottom
    belly_h = int(40 * scale * ss)
    lean = math.radians(13)                # whole-body tilt toward the load

    # ── 1. THE OVERSIZED FIRE-SPEAR (drawn first; the imp's mitts close over it) ─
    # A slim pole far taller than the imp, topped by a small warm flame-fork. It is
    # tilted HARD (top swung out, butt swung back under the imp) so its weight
    # visibly DRAGS the wee body — the spear leads the eye into the strain gag.
    spear_top = (int(BW * 0.78), int(BH * 0.08))
    spear_bot = (int(BW * 0.50), feet_y - int(2 * scale * ss))
    sw = int(6 * scale * ss)
    pygame.draw.line(s, SHAFT_DK, spear_top, spear_bot, sw + max(2, int(3 * ss)))
    pygame.draw.line(s, SHAFT, spear_top, spear_bot, sw)
    dx, dy = spear_bot[0] - spear_top[0], spear_bot[1] - spear_top[1]
    plen = math.hypot(dx, dy) or 1
    nx, ny = -dy / plen, dx / plen
    off = int(2 * scale * ss)
    pygame.draw.line(s, SHAFT_HI,
                     (spear_top[0] - nx * off, spear_top[1] - ny * off),
                     (spear_bot[0] - nx * off, spear_bot[1] - ny * off),
                     max(1, int(1.8 * ss)))
    # Iron banding collars (also the pillar-banding cue) at three points.
    for t in (0.30, 0.55, 0.80):
        bxp = int(spear_top[0] + dx * t)
        byp = int(spear_top[1] + dy * t)
        pygame.draw.circle(s, INK, (bxp, byp), max(3, int(5 * scale * ss)))
        pygame.draw.circle(s, IRON, (bxp, byp), max(2, int(4 * scale * ss)))
        pygame.draw.circle(s, _shade_c(IRON, 50),
                           (bxp - int(ss), byp - int(ss)), max(1, int(2 * scale * ss)))
    # Iron socket where the flame-fork seats on the shaft.
    sock = (spear_top[0], spear_top[1] + int(6 * scale * ss))
    pygame.draw.circle(s, IRON, sock, max(3, int(6 * scale * ss)))
    pygame.draw.circle(s, INK, sock, max(3, int(6 * scale * ss)), max(1, int(ss)))
    # The warm flame-fork tip (the gap-edge cap, here at the top of the prop).
    _flame_fork(s, spear_top[0], spear_top[1] + int(2 * scale * ss),
                int(26 * scale * ss), int(58 * scale * ss), ss)

    # ── 2. BAT-WINGS as a bold two-lobe pair behind the body (1x silhouette anchor)
    # Hinged high on the shoulders and swept up+back so a clear strip of sky cuts
    # between each wing and the green torso — the torso stays the dominant value.
    wing_hy = feet_y - belly_h - int(20 * scale * ss)
    _bat_wing(s, (body_cx + int(14 * scale * ss), wing_hy), scale, ss, side=1)
    _bat_wing(s, (body_cx - int(14 * scale * ss), wing_hy), scale, ss, side=-1)

    # ── 3. CURL TAIL — ONE bold S-stroke + spade tip ─────────────────────────────
    # R1's bead-chain became a row of 1x dots that fuzzed out; this is a single
    # tapered S polyline (the stroke, drawn as a thick line) ending in the devil
    # spade arrowhead — the spade is the only tell that has to read, the body of
    # the tail is just one confident curve.
    tseg = 14
    t0x, t0y = body_cx - belly_w + int(2 * scale * ss), feet_y - int(10 * scale * ss)
    tail = []
    for i in range(tseg):
        t = i / (tseg - 1)
        tx = t0x - math.sin(t * math.pi * 1.15) * 24 * scale * ss
        ty = t0y - t * 34 * scale * ss + math.sin(t * math.pi) * 7 * scale * ss
        tail.append((int(tx), int(ty)))
    pygame.draw.lines(s, GREEN_DK, False, tail, max(3, int(7 * scale * ss)))
    pygame.draw.lines(s, GREEN, False, tail, max(2, int(4 * scale * ss)))
    # Spade tip — a tiny devil arrowhead (the load-bearing devil tell), points up.
    spx, spy = tail[-1]
    spade = [(spx - 9 * scale * ss, spy + 2 * scale * ss),
             (spx + 5 * scale * ss, spy + 4 * scale * ss),
             (spx - 3 * scale * ss, spy - 12 * scale * ss)]
    pygame.draw.polygon(s, GREEN_DK, spade)
    pygame.draw.polygon(s, INK, spade, max(1, int(1.8 * ss)))

    # ── 4. CLAWED FEET — a braced, knee-buckled stance under the load ────────────
    # The back foot (left) is splayed out wide + planted low to brace; the front
    # foot (right) is tucked in + raised a touch, reading as a buckling knee. The
    # asymmetry sells "barely holding it up", not a relaxed stand.
    for fx_off, fy_off in ((-20, 0), (8, -7)):
        fx = body_cx + int(fx_off * scale * ss)
        fy = feet_y + int(fy_off * scale * ss)
        fr = int(8 * scale * ss)
        _triad_circle(s, fx, fy, fr, GREEN, ss)
        for k in (-1, 0, 1):
            ca = math.radians(90 + k * 26)
            cx2 = fx + math.cos(ca) * fr * 0.4
            cy2 = fy + fr * 0.5
            tip = (cx2 + math.cos(ca) * fr * 0.6, cy2 + fr * 0.7)
            pygame.draw.line(s, INK, (int(cx2), int(cy2)),
                             (int(tip[0]), int(tip[1])), max(2, int(2.0 * ss)))

    # ── 5. PEAR BODY — wide-bottomed acid-green torso w/ a cream belly patch ─────
    belly_cy = feet_y - belly_h - int(2 * scale * ss)
    # Pear silhouette via an ellipse: narrow up top (toward the head), fat at base.
    pygame.draw.ellipse(s, GREEN_DK,
                        (body_cx - belly_w, belly_cy - belly_h,
                         belly_w * 2, belly_h * 2))
    pygame.draw.ellipse(s, GREEN,
                        (body_cx - belly_w + int(ss), belly_cy - belly_h + int(ss),
                         belly_w * 2 - int(2 * ss), belly_h * 2 - int(2 * ss)))
    # Top-left sheen wedge.
    pygame.draw.ellipse(s, GREEN_HI,
                        (body_cx - belly_w + int(3 * ss), belly_cy - belly_h + int(2 * ss),
                         belly_w, belly_h))
    # Cream belly patch (lower-front).
    pygame.draw.ellipse(s, CREAM,
                        (body_cx - int(belly_w * 0.55), belly_cy - int(belly_h * 0.1),
                         int(belly_w * 1.1), int(belly_h * 1.0)))
    pygame.draw.ellipse(s, _shade_c(CREAM, -34),
                        (body_cx - int(belly_w * 0.55), belly_cy - int(belly_h * 0.1),
                         int(belly_w * 1.1), int(belly_h * 1.0)), max(1, int(ss)))

    # ── 6. STUB MITT ARMS — BOTH thrown overhead in a two-handed strain ──────────
    # The R1 imp held the spear casually at belly height with one arm — it read
    # relaxed. Now BOTH stub arms reach up OVERHEAD to grip the shaft high, elbows
    # flung wide, so the silhouette is plainly "heaving a too-big weapon aloft".
    # The two grips sit close together up the dragging shaft.
    dx_s, dy_s = spear_bot[0] - spear_top[0], spear_bot[1] - spear_top[1]
    up_grip = (int(spear_top[0] + dx_s * 0.40), int(spear_top[1] + dy_s * 0.40))
    lo_grip = (int(spear_top[0] + dx_s * 0.52), int(spear_top[1] + dy_s * 0.52))
    # Shoulders high on the torso; both arms angle UP and OUT to the high grips.
    sh_hi = (body_cx + int(16 * scale * ss), belly_cy - int(20 * scale * ss))
    sh_lo = (body_cx - int(2 * scale * ss), belly_cy - int(14 * scale * ss))
    # A wide elbow on each arm so the limbs read as straining bends, not stretches.
    elb_hi = (sh_hi[0] + int(20 * scale * ss), sh_hi[1] - int(18 * scale * ss))
    elb_lo = (sh_lo[0] + int(8 * scale * ss),  sh_lo[1] - int(24 * scale * ss))
    for sh, elb, grip in ((sh_hi, elb_hi, up_grip), (sh_lo, elb_lo, lo_grip)):
        pygame.draw.lines(s, GREEN_DK, False, [sh, elb, grip], int(9 * scale * ss))
        pygame.draw.lines(s, GREEN, False, [sh, elb, grip], int(6 * scale * ss))
    for grip, gr in ((up_grip, 7), (lo_grip, 7)):
        _triad_circle(s, grip[0], grip[1], int(gr * scale * ss), GREEN, ss)
        pygame.draw.circle(s, INK, grip, int(gr * scale * ss), max(1, int(ss)))

    # ── 7. THE HEAD — round, with big POINTED EARS, a single horn-NUB + huge eyes ─
    # Tipped LEFT off the body centre (the lean) so the head + heavy spear pull the
    # silhouette into a buckle. The whole head cluster shifts by head_lean.
    head_cy = belly_cy - belly_h - int(2 * scale * ss)
    head_lean = int(math.sin(lean) * belly_h * 1.6)
    body_cx = body_cx - head_lean    # shadow the torso var for all head features
    # Big pointed ears (gremlin signature) BEFORE the head so they tuck behind it.
    for esgn in (-1, 1):
        eb = (body_cx + esgn * head_r * 0.78, head_cy + head_r * 0.06)
        etip = (body_cx + esgn * head_r * 1.7, head_cy - head_r * 0.7)
        ebk = (body_cx + esgn * head_r * 0.7, head_cy + head_r * 0.5)
        ear = [eb, etip, ebk]
        pygame.draw.polygon(s, GREEN_DK, ear)
        # Inner ear-shell so it reads as an ear, not a fin.
        inner = [(body_cx + esgn * head_r * 0.85, head_cy + head_r * 0.04),
                 (body_cx + esgn * head_r * 1.45, head_cy - head_r * 0.5),
                 (body_cx + esgn * head_r * 0.78, head_cy + head_r * 0.36)]
        pygame.draw.polygon(s, GREEN, inner)
        pygame.draw.polygon(s, INK, ear, max(1, int(1.6 * ss)))
    _triad_circle(s, body_cx, head_cy, head_r, GREEN, ss)
    # Single off-centre pointy horn-NUB (tiny imp horn — explicitly NOT a ram
    # pair; the set-wide no-second-ram-horn guardrail).
    hnx = body_cx + int(head_r * 0.30)
    hny = head_cy - head_r + int(2 * scale * ss)
    horn = [(hnx - 5 * scale * ss, hny + 2 * scale * ss),
            (hnx + 5 * scale * ss, hny + 2 * scale * ss),
            (hnx + 1 * scale * ss, hny - 16 * scale * ss)]
    pygame.draw.polygon(s, HORN, horn)
    pygame.draw.polygon(s, _shade_c(HORN, 40), horn, max(1, int(ss)))

    # Huge glowing gremlin eyes (the cute lever) — big, round, asymmetric, with a
    # warm glow. Orange so they pop against acid-green without going green-on-green.
    eyes = ((-0.40, -0.05, 0.36), (0.42, -0.10, 0.30))
    for exf, eyf, erf in eyes:
        ex = int(body_cx + exf * head_r)
        ey = int(head_cy + eyf * head_r)
        blit_glow(s, ex, ey, int(8 * scale * ss), EYE_ORANGE, 120)
    for exf, eyf, erf in eyes:
        ex = int(body_cx + exf * head_r)
        ey = int(head_cy + eyf * head_r)
        er = max(3, int(erf * head_r))
        pygame.draw.circle(s, INK, (ex, ey), er + max(1, int(ss)))
        pygame.draw.circle(s, EYE_ORANGE, (ex, ey), er)
        pygame.draw.circle(s, EYE_HOT, (ex - int(er * 0.3), ey - int(er * 0.3)),
                           max(1, int(er * 0.42)))
        # Tiny dark pupil so the big eye still reads as an eye, not a lamp.
        pygame.draw.circle(s, INK, (ex + int(er * 0.1), ey + int(er * 0.1)),
                           max(1, int(er * 0.32)))

    # Snaggle grin + a cheeky tongue tip (gremlin glee — pure mischief, not grim).
    gy = head_cy + int(head_r * 0.48)
    gx = body_cx - int(head_r * 0.05)
    grin = [(gx - head_r * 0.34, gy),
            (gx - head_r * 0.10, gy + head_r * 0.18),
            (gx + head_r * 0.30, gy + head_r * 0.06)]
    pygame.draw.lines(s, INK, False, [(int(a), int(b)) for a, b in grin],
                      max(2, int(2.2 * ss)))
    # One up-poking snaggle fang.
    fx = gx + int(head_r * 0.14)
    fang = [(fx - 4 * scale * ss, gy + 4 * scale * ss),
            (fx + 4 * scale * ss, gy + 4 * scale * ss),
            (fx, gy - 7 * scale * ss)]
    pygame.draw.polygon(s, CREAM, fang)
    pygame.draw.polygon(s, INK, fang, max(1, int(1.4 * ss)))
    # Cheeky tongue tip at the grin's low corner.
    pygame.draw.circle(s, TONGUE,
                       (int(gx - head_r * 0.06), int(gy + head_r * 0.22)),
                       max(2, int(3 * scale * ss)))

    s = _add_outline(s)
    fw = max(1, s.get_width() // ss)
    fh = max(1, s.get_height() // ss)
    return pygame.transform.smoothscale(s, (fw, fh))


# ── prop -> pillar mirror: the fire-spear is a tileable vertical post ─────────

def _spear_post(surf, cx, top, bot, w, ss):
    """The shared shaft body: a slim warm-wood post, dark-cored + top-left lit
    edge + iron banding collars — the repeatable pillar SHAFT."""
    pygame.draw.line(surf, SHAFT_DK, (cx, top), (cx, bot), w + max(2, int(3 * ss)))
    pygame.draw.line(surf, SHAFT, (cx, top), (cx, bot), w)
    pygame.draw.line(surf, SHAFT_HI, (cx - int(2 * ss), top), (cx - int(2 * ss), bot),
                     max(1, int(2 * ss)))
    span = bot - top
    n = max(2, int(span / (max(1, w) * 6)))
    for i in range(n):
        cy = int(top + span * (i + 0.5) / n)
        pygame.draw.circle(surf, INK, (cx, cy), max(4, int(7 * ss)))
        pygame.draw.circle(surf, IRON, (cx, cy), max(3, int(5 * ss)))
        pygame.draw.circle(surf, _shade_c(IRON, 50),
                           (cx - int(ss), cy - int(ss)), max(2, int(3 * ss)))


def draw_spear_pillar_cap(surf, cx, top, bot, w, ss, *, flip):
    """The TOP CAP pier: the spear shaft runs the full height, the warm flame-fork
    rides the GAP-EDGE (inner end) ONLY, flaring INTO the gap. `flip=True` draws
    the bottom pier as a vertical mirror so a top/bottom pair reads as one matched
    obstacle. The flame is detachable to the gap-edge so the repeatable mid-shaft
    tiles cleanly with no flame in it."""
    if flip:
        h = surf.get_height()
        tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        draw_spear_pillar_cap(tmp, cx, h - bot, h - top, w, ss, flip=False)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, 0))
        return

    _spear_post(surf, cx, top, bot, w, ss)
    # GAP-EDGE flame-fork at the inner (here BOTTOM) end ONLY, flaring up into the
    # gap. Iron socket where it seats on the shaft.
    gap_y = bot
    pygame.draw.circle(surf, IRON, (cx, gap_y), max(4, int(7 * ss)))
    pygame.draw.circle(surf, INK, (cx, gap_y), max(4, int(7 * ss)), max(1, int(ss)))
    _flame_fork(surf, cx, gap_y - int(2 * ss), int(34 * ss), int(76 * ss), ss)


def draw_spear_pillar_mid(surf, cx, top, bot, w, ss):
    """The REPEATABLE MID segment: pure banded shaft, NO flame — proves the body
    tiles cleanly because the flame is a detachable gap-flourish."""
    _spear_post(surf, cx, top, bot, w, ss)


# ── sheet composition ────────────────────────────────────────────────────────

def _sky_panel(w, h, night):
    """The game's real biome day/night keyframes, so legibility is judged on the
    actual backdrop the boss must read on."""
    surf = pygame.Surface((w, h))
    if night:
        top, bot = (5, 8, 30), (35, 55, 115)
    else:
        top, bot = (40, 110, 200), (170, 220, 245)
    for y in range(h):
        pygame.draw.line(surf, lerp_color(top, bot, y / h), (0, y), (w, y))
    return surf


def _grayscale(src):
    """A B/W silhouette-legibility check: luminance copy so the wings + face must
    read on value alone, not hue."""
    g = src.copy()
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114)
    arr[:, :, 0] = arr[:, :, 1] = arr[:, :, 2] = lum.astype(arr.dtype)
    del arr
    return g


def _label(surf, font, text, x, y):
    sh = font.render(text, True, (0, 0, 0))
    surf.blit(sh, (x + 1, y + 1))
    surf.blit(font.render(text, True, (255, 255, 255)), (x, y))


def main():
    pygame.init()
    ss = 3
    SHEET_W, SHEET_H = 980, 760
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((40, 48, 36))                       # neutral olive-grey board
    font = pygame.font.SysFont("dejavusans", 16, bold=True)
    fbig = pygame.font.SysFont("dejavusans", 22, bold=True)

    _label(sheet, fbig, "IMPLET  -  pocket gremlin imp (take B8)  R2", 20, 14)

    # (a) Showcase boss on a neutral panel — emphasize tiny-imp + oversized
    # fire-spear comedy of scale (but it must read DEVIL, not reaper).
    panel_w, panel_h = 330, 650
    panel = pygame.Surface((panel_w, panel_h))
    panel.fill((56, 64, 48))
    pygame.draw.rect(panel, (84, 96, 70), panel.get_rect(), 3)
    boss = build_implet(scale=1.45, ss=ss)
    panel.blit(boss, (panel_w // 2 - boss.get_width() // 2,
                      panel_h // 2 - boss.get_height() // 2 + 6))
    sheet.blit(panel, (20, 52))
    _label(sheet, font, "(a) showcase  -  STRAINING under the spear", 24, 60)

    # (b) prop -> pillar mirror: a tall vertical PILLAR pair (flame-tip cap +
    # repeatable shaft mid) proving the spear tiles and the flame stays gap-edge.
    pil_w, pil_h = 170, 600
    pil = pygame.Surface((pil_w * ss, pil_h * ss), pygame.SRCALPHA)
    pil.fill((38, 44, 34))
    pcx = pil_w * ss // 2
    post_w = int(PIPE_W * 0.34 * ss)
    gap_top = int(pil_h * 0.46 * ss)
    gap_bot = int(pil_h * 0.58 * ss)
    draw_spear_pillar_cap(pil, pcx, int(0.04 * pil_h * ss), gap_top, post_w, ss,
                          flip=False)
    draw_spear_pillar_cap(pil, pcx, gap_bot, int(0.96 * pil_h * ss), post_w, ss,
                          flip=True)
    pil = pygame.transform.smoothscale(pil, (pil_w, pil_h))
    sheet.blit(pil, (372, 78))
    _label(sheet, font, "(b) spear -> PILLAR pair", 376, 58)
    _label(sheet, font, "flame = gap-edge only", 376, 686)

    # A standalone repeatable-MID strip beside it, proving the body tiles cleanly.
    mid_w, mid_h = 80, 600
    mid = pygame.Surface((mid_w * ss, mid_h * ss), pygame.SRCALPHA)
    mid.fill((38, 44, 34))
    draw_spear_pillar_mid(mid, mid_w * ss // 2, 0, mid_h * ss, post_w, ss)
    mid = pygame.transform.smoothscale(mid, (mid_w, mid_h))
    sheet.blit(mid, (560, 78))
    _label(sheet, font, "(b') repeat MID", 562, 686)

    # (c) 1x in-game-scale insets on day + night sky + a grayscale check.
    inset_w, inset_h = 132, 230
    small_boss = build_implet(scale=0.62, ss=ss)
    cells = ((False, "DAY"), (True, "NIGHT"))
    for i, (night, name) in enumerate(cells):
        sky = _sky_panel(inset_w, inset_h, night)
        sky.blit(small_boss, (inset_w // 2 - small_boss.get_width() // 2,
                              inset_h // 2 - small_boss.get_height() // 2 + 6))
        pygame.draw.rect(sky, (20, 24, 18), sky.get_rect(), 2)
        x = 672
        y = 80 + i * 250
        sheet.blit(sky, (x, y))
        _label(sheet, font, "(c) 1x  " + name, x + 2, y - 20)

    bw = _grayscale(small_boss)
    bwpanel = pygame.Surface((inset_w, inset_h))
    bwpanel.fill((128, 128, 128))
    bwpanel.blit(bw, (inset_w // 2 - bw.get_width() // 2,
                      inset_h // 2 - bw.get_height() // 2 + 6))
    pygame.draw.rect(bwpanel, (20, 24, 18), bwpanel.get_rect(), 2)
    sheet.blit(bwpanel, (820, 80))
    _label(sheet, font, "(c) 1x  B/W", 822, 60)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "devil", "implet")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
