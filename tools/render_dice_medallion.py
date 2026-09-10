"""Look-dev renderer (Round 3): the DEVILISH dice-results medallion, refined.

Round 1 ranged across cheeky → devilish → menacing; the art director locked the
DEVILISH face as the standard "you rolled N!" celebration look. Round 2 held the
geometry the AD signed off on (keep-out ring, constant cream disc R*0.74, horn
top-clearance, N drawn LAST and dominant) but flagged three reads to fix.

Round 3 holds ALL the round-2 geometry unchanged and lands the final fixes:

  * BELLS read as BELLS — not pins/antennae. Each crest/dangler bell is now a
    proper bell SILHOUETTE: a rounded-trapezoid dome body with a visibly FLARED
    MOUTH at the bottom, the plum bell-mouth shadow, a clapper bead, and a
    single specular dot. Reads as a chunky reward bell at true 264px.
  * NO clock-dial rim. The dense ring of even-length even-angle radial gold
    ticks is gone; the bezel is a smooth gold band carrying IRREGULAR gold
    sparkle flecks off the angular grid, so the rim never reads watch/gear.
  * The grin is sharpened to DEVILISH: narrower, with the locked single
    ASYMMETRIC fang, ONE corner curled up under the cocked brow — smug imp, not
    happy emoji.

The CHEEKY fallback is CUT — one face system everywhere. Any low-roll softening
is carried by the banderole LABEL only. The only ramp levers across tiers are
(a) crest-bell DENSITY (3 / 7 / 11) and (b) the LABEL ("PAGODAS" vs "JACKPOT").

Judged at TRUE 264px on the day sky WITH an actual-size inset.

Run (headless):
    PYTHONPATH=. python tools/render_dice_medallion.py
Writes docs/dice_results/medallion/round_3.png.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import hud  # noqa: E402  vendored bold TTF + cache

# Reuse the base renderer's machinery so these explorations are pixel-faithful
# to the real popup pipeline (number treatment, label plate, confetti keepout,
# sky swatch, SS-supersample compositing, the sheet builder's actual-size inset).
from tools.render_dice_celebration import (  # noqa: E402
    SKY_TOP, SKY_BOT, NIGHT_TOP, NIGHT_BOT,
    PLUM, PLUM_DK, LIME, GOLD, CREAM,
    sky_tile, _num_block, _label_plate, _star,
)

# Local copy of the jester _shade so this module needn't pull the whole clown
# body kit (and its game.config / parrot imports) into a UI-only renderer.
def _shade(c, d):
    return (max(0, min(255, int(c[0] + d))),
            max(0, min(255, int(c[1] + d))),
            max(0, min(255, int(c[2] + d))))


# Gold tones for the bezel metal (matching the base medallion's metal ramp).
GOLD_DK = (180, 132, 28)
GOLD_MD = (200, 150, 30)
# A muted gold for the JACKPOT crest bells: ~18% value/saturation knocked off
# the hero GOLD so the dense bell-ring RECEDES behind the hero digits instead of
# competing — still warm treasure-gold, never the cold tin the menacing take read.
GOLD_RECEDE = (206, 168, 78)
INK = (28, 22, 30)
MOUTH_DK = (120, 30, 42)


# ── ported jester ornaments, re-implemented at MEDALLION (bezel) scale ───────
# The jester kit was authored at ~22px head scale; here every primitive is
# rebuilt to ride the ~166px-radius bezel of a 264px medallion (supersampled),
# so it reads as the SAME mischief vocabulary scaled UP to a hero frame.

def _bell(canvas, x, y, r, *, col=GOLD):
    """A chunky warm-GOLD jingle bell drawn as a true bell SILHOUETTE so it never
    reads as a pin/antenna/stud (the round-2 break: a gold dot on a stalk topped
    by a ring). The round-3 shape is a SOLID single-piece bell read at a glance:
    a domed SHOULDER that swells out and FLARES into a wide bell-MOUTH at the
    bottom (the body is one continuous teardrop-trapezoid, not a ball-on-stalk),
    a TINY suspension loop barely peeking over the dome (so the top reads "hung
    bell", never "antenna"), the plum bell-mouth shadow + clapper, and ONE hot
    specular dot. `r` is the body half-width; the body half-width at the mouth
    is ~1.3r so the flared silhouette holds at true 264px. Always the bezel
    GOLD — never a green/cool tint."""
    x, y = int(x), int(y)
    r = max(3, int(r))
    # The bell occupies a generous box so the loop + flared mouth never clip;
    # everything is composited from a local SRCALPHA surface for clean edges.
    bw = r * 3
    bh = int(r * 3.2)
    s = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cxp = bw // 2
    body_dk = _shade(col, -65)
    # Geometry of the one continuous bell body, top to bottom.
    loop_y = max(2, int(r * 0.35))          # tiny suspension loop, barely peeking
    shoulder_cy = int(r * 1.25)             # centre of the domed shoulder circle
    shoulder_r = int(r * 0.92)              # dome radius (the rounded top mass)
    mouth_y = bh - max(2, int(r * 0.45))    # the flared lip line
    top_hw = int(r * 0.82)                  # body half-width where it leaves dome
    bot_hw = int(r * 1.30)                  # body half-width at the flared mouth
    waist_y = int(shoulder_cy + shoulder_r * 0.55)  # where dome meets the flare
    # TINY suspension loop — a short stub + small ring, only just clearing the
    # dome so it never reads as a long stalk/antenna.
    pygame.draw.line(s, body_dk, (cxp, loop_y + int(r * 0.2)),
                     (cxp, shoulder_cy - int(shoulder_r * 0.4)), max(2, int(r * 0.22)))
    pygame.draw.circle(s, body_dk, (cxp, loop_y), max(2, int(r * 0.26)),
                       max(1, int(r * 0.14)))
    # The body is ONE filled silhouette: a flared trapezoid skirt from the waist
    # down to the mouth, capped by the domed shoulder circle above it, so the
    # whole thing reads as a single continuous bell mass. Dark base for a clean
    # outline, then the lighter face inset on top.
    skirt = [(cxp - top_hw, waist_y), (cxp + top_hw, waist_y),
             (cxp + bot_hw, mouth_y), (cxp - bot_hw, mouth_y)]
    pygame.draw.polygon(s, body_dk, skirt)
    pygame.draw.circle(s, body_dk, (cxp, shoulder_cy), shoulder_r)
    inset = max(1, int(r * 0.2))
    skirt_in = [(cxp - top_hw + inset, waist_y + inset),
                (cxp + top_hw - inset, waist_y + inset),
                (cxp + bot_hw - inset, mouth_y - 1), (cxp - bot_hw + inset, mouth_y - 1)]
    pygame.draw.polygon(s, col, skirt_in)
    pygame.draw.circle(s, col, (cxp, shoulder_cy), shoulder_r - inset)
    # Flared MOUTH: a wide shallow lip closing the bottom of the skirt. The plum
    # bell-mouth shadow ellipse reads as the hollow opening; a gold rim around it
    # and a small clapper bead in the centre complete the open-bell read.
    lip_h = max(3, int(r * 0.72))
    pygame.draw.ellipse(s, PLUM_DK,
                        (cxp - bot_hw, mouth_y - lip_h // 2, bot_hw * 2, lip_h))
    pygame.draw.ellipse(s, col,
                        (cxp - bot_hw, mouth_y - lip_h // 2, bot_hw * 2, lip_h),
                        max(1, int(r * 0.22)))
    pygame.draw.circle(s, _shade(col, 55), (cxp, mouth_y - max(1, int(r * 0.04))),
                       max(2, int(r * 0.28)))  # clapper bead in the mouth
    # ONE hot specular catch on the upper-left of the dome — the only highlight.
    pygame.draw.circle(s, _shade(col, 95),
                       (cxp - int(shoulder_r * 0.4), shoulder_cy - int(shoulder_r * 0.35)),
                       max(1, int(r * 0.3)))
    # Seat the bell so (x, y) is roughly its visual centre on the cord.
    canvas.blit(s, s.get_rect(center=(x, y + int(r * 0.3))))


def _dangler(canvas, cx, cy, ang, R, ss, *, length, bell_r, col=GOLD,
             cord=PLUM_DK):
    """A jester BELL hanging off the bezel rim on a short cord at angle `ang`.
    The cord roots just inside the rim and the bell swings out past it so the
    medallion reads fringed with jingle bells."""
    rx = cx + math.cos(ang) * (R - 2 * ss)
    ry = cy + math.sin(ang) * (R - 2 * ss)
    bx = cx + math.cos(ang) * (R + length)
    by = cy + math.sin(ang) * (R + length)
    pygame.draw.line(canvas, cord, (int(rx), int(ry)), (int(bx), int(by)),
                     max(2, int(2 * ss)))
    _bell(canvas, bx, by, bell_r, col=col)


def _imp_horn(canvas, cx, cy, R, ss, *, sgn, col, length=1.0):
    """A soft IMP HORN cresting the medallion — a stubby rounded nub curling
    gently outward+up, finished with a small bell-lit tip. Devilish but impish,
    never a sharp menace spike (the jester kit's cap_imp_hood read)."""
    base_a = -math.pi / 2 + sgn * 0.42
    bx = cx + math.cos(base_a) * (R + 2 * ss)
    by = cy + math.sin(base_a) * (R + 2 * ss)
    tipx = bx + sgn * 18 * ss * length
    tipy = by - 30 * ss * length
    midx = bx + sgn * 6 * ss
    midy = by - 18 * ss * length
    pts = [(bx - sgn * 9 * ss, by + 2 * ss), (bx + sgn * 9 * ss, by),
           (midx + sgn * 7 * ss, midy), (tipx, tipy), (midx - sgn * 5 * ss, midy)]
    pygame.draw.polygon(canvas, col, pts)
    pygame.draw.polygon(canvas, _shade(col, 40),
                        [(bx - sgn * 9 * ss, by + 2 * ss),
                         (bx + sgn * 2 * ss, by - 6 * ss), (midx - sgn * 5 * ss, midy)])
    pygame.draw.polygon(canvas, _shade(col, -60), pts, max(2, int(2 * ss)))
    pygame.draw.circle(canvas, _shade(col, 30), (int(tipx), int(tipy)), int(4 * ss))


def _crest_bells(canvas, cx, cy, R, ss, *, count, bell_r, arc=1.5, col=GOLD):
    """The reward ramp's PRIMARY lever: a fan of warm-GOLD jingle bells cresting
    the TOP of the bezel on short cords, spanning a symmetric arc centred on the
    top. `count` is the only thing that changes between the plain (sparse) and
    jackpot (dense) tiers — same gold bell, same cord, just MORE of them. Each
    bell hangs on its own short cord so the crest reads as a row of bells, never
    a beaded rim.

    The arc (~1.5 rad) stays inside the two imp horns (which crest at ±0.42 from
    the top): the fan nestles BETWEEN and just below the horn bases, so bells
    never land on a horn. All of it lives well outside the disc keep-out ring."""
    if count < 1:
        return
    top = -math.pi / 2  # straight up
    # Even angular spacing across the arc, symmetric about the top.
    for i in range(count):
        t = 0.5 if count == 1 else i / (count - 1)
        a = top - arc / 2 + arc * t
        rx = cx + math.cos(a) * (R + 1 * ss)
        ry = cy + math.sin(a) * (R + 1 * ss)
        # Cord length alternates slightly so the bell heads sit on a gentle
        # scallop rather than one flat line — rhythmic, still even.
        clen = (10 + (i % 2) * 4) * ss
        bx = cx + math.cos(a) * (R + clen)
        by = cy + math.sin(a) * (R + clen)
        pygame.draw.line(canvas, PLUM_DK, (int(rx), int(ry)), (int(bx), int(by)),
                         max(2, int(2 * ss)))
        _bell(canvas, bx, by, bell_r, col=col)


# ── the medallion's JESTER FACE motif (embossed around / framing the disc) ───
# The naughty-face grammar from the jester kit (wide fanged grin, cocked brow,
# sidelong sly eyes) rebuilt to FRAME the cream disc: eyes ride the upper bezel
# arc and the grin rides the lower bezel arc, so the rolled NUMBER sits in the
# "mouth" of a sly clown face without any feature out-shouting it.

def _sly_eye(canvas, x, y, ss, *, look, r=7, cocked=False, glint=False,
            sclera=CREAM, pupil=(44, 38, 60)):
    """A bright sly eye glancing sidelong (toward `look`<0 = inward/left). Used
    on the bezel arc above the disc. `cocked` lifts the inner brow higher;
    `glint` swaps in a gold sidelong catch-glint for the devilish read."""
    ew, eh = int(r * 0.85), int(r)
    pygame.draw.ellipse(canvas, sclera, (x - ew, y - eh, ew * 2, eh * 2))
    pygame.draw.ellipse(canvas, _shade(sclera, -70), (x - ew, y - eh, ew * 2, eh * 2),
                        max(1, int(ss)))
    px = int(x + look)
    py = int(y + 1 * ss)
    pygame.draw.circle(canvas, pupil, (px, py), int(r * 0.55))
    pygame.draw.circle(canvas, INK, (px, py), int(r * 0.55), max(1, int(ss)))
    cl = GOLD if glint else (255, 255, 255)
    pygame.draw.circle(canvas, cl, (px - int(r * 0.3), py - int(r * 0.4)), max(1, int(r * 0.22)))
    # Happy-squint lower lid arc.
    pygame.draw.arc(canvas, _shade(sclera, -90),
                    (x - ew, y - int(ss), ew * 2, eh + int(2 * ss)),
                    math.pi * 1.1, math.tau * 0.95, max(1, int(ss)))


def _sly_brow(canvas, x, y, ss, *, sgn, cocked=False, col=(76, 56, 60), thick=1.0):
    """A raised cheeky 'oh-really' brow: inner end HIGH, outer end low — never the
    angry inner-down V. `cocked` rides the whole brow higher (one-up asymmetry)."""
    inner = (x - sgn * 3 * ss, y - 6 * ss - (4 * ss if cocked else 0))
    outer = (x + sgn * 13 * ss, y + 2 * ss)
    pygame.draw.line(canvas, col, inner, outer, max(2, int(3 * ss * thick)))


def _fanged_grin(canvas, cx, gy, ss, *, w, fang_sgn=-1, tongue=False,
                 lip_col=(188, 56, 66)):
    """The locked DEVILISH grin: a NARROW, asymmetric smirk — not a wide even
    happy smile. ONE corner (the fang side) curls UP higher than the other under
    the cocked brow, the mouth carries only a few teeth (not a full even band)
    plus the single prominent ASYMMETRIC FANG, so it reads "smug imp", not
    "happy emoji". `fang_sgn` picks the fang/curl side; `tongue` adds a tip lick.

    Geometry is unchanged from round 2 (same seat radius / `w` lever); only the
    SHAPE of the mouth is re-cut."""
    # The curled corner rides HIGH; the opposite corner sits low — that tilt is
    # the whole devilish read. fang_sgn<0 -> left corner curls up. The mouth is
    # NARROWED (~0.78*w of round 2's seat) so it reads a tight smirk, not a wide
    # even happy arc; geometry seat / `w` lever itself is unchanged.
    up = fang_sgn  # which side curls up
    nw = w * 0.78  # the effective NARROW half-width of the smirk
    curl_c = (cx + up * nw, gy - 8 * ss)        # high, sharply curled corner
    flat_c = (cx - up * nw * 0.85, gy + 3 * ss)  # low corner, lower than round 2
    bottom = (cx - up * nw * 0.12, gy + 10 * ss)
    # The dark mouth gap — a tight asymmetric lens slanted hard toward the curl.
    mouth = [curl_c, (cx + up * nw * 0.32, gy - 2 * ss), flat_c,
             (cx - up * nw * 0.28, gy + 6 * ss), bottom, (cx + up * nw * 0.16, gy + 5 * ss)]
    pygame.draw.polygon(canvas, MOUTH_DK, mouth)
    # Only a SLIVER of upper teeth on the curled side — just enough to catch the
    # light, never a full even tooth band (which read happy-emoji in round 2).
    teeth = [curl_c, (cx + up * nw * 0.32, gy - 2 * ss),
             (cx + up * nw * 0.06, gy + 1 * ss), (cx + up * nw * 0.14, gy + 3 * ss),
             (cx + up * nw * 0.34, gy + 2 * ss)]
    pygame.draw.polygon(canvas, (250, 248, 240), teeth)
    pygame.draw.polygon(canvas, _shade((250, 248, 240), -80), teeth, max(1, int(ss)))
    # A single dividing line in the tooth sliver — one notch, not a grid.
    gx = cx + up * nw * 0.2
    pygame.draw.line(canvas, _shade((250, 248, 240), -80),
                     (gx, gy - 1 * ss), (gx, gy + 3 * ss), max(1, int(ss)))
    # The single mean FANG dropping from the upper lip into the dark mouth, on
    # the curl side — the locked round-1 asymmetric fang, made the dominant
    # tooth: longer + wider than the sliver so it is unmistakably one big fang.
    fx = cx + fang_sgn * nw * 0.46
    fang = [(fx - 5 * ss, gy + 1 * ss), (fx + 5 * ss, gy + 1 * ss), (fx, gy + 12 * ss)]
    pygame.draw.polygon(canvas, (252, 250, 244), fang)
    pygame.draw.polygon(canvas, _shade((252, 250, 244), -80), fang, max(1, int(ss)))
    # The lip line: a hard SMIRK curve — sweeps UP into the curled corner, sags
    # under the low corner. Strongly asymmetric (never a symmetric parabola).
    lip = []
    for k in range(13):
        t = k / 12.0
        lx = flat_c[0] + (curl_c[0] - flat_c[0]) * t
        # Quadratic that lifts the curl end hard and sags the flat end.
        ly = flat_c[1] + (curl_c[1] - flat_c[1]) * t + (1.0 - t) * t * 18 * ss \
            - (t ** 2) * 6 * ss
        lip.append((lx, ly))
    pygame.draw.lines(canvas, lip_col, False, lip, max(2, int(3 * ss)))
    if tongue:
        tx0 = curl_c[0] - up * 5 * ss
        ty0 = gy + 3 * ss
        pygame.draw.ellipse(canvas, (228, 110, 124),
                            (tx0 - 4 * ss, ty0, 9 * ss, 7 * ss))
        pygame.draw.ellipse(canvas, _shade((228, 110, 124), -60),
                            (tx0 - 4 * ss, ty0, 9 * ss, 7 * ss), max(1, int(ss)))


# ── shared medallion shell (field, bezel, disc, specular) ────────────────────
# All five variants build on ONE shell so the family reads consistent. The disc
# diameter is CONSTANT in every cell (disc_inner is fixed) so the hero number N
# never shrinks; the only differences are the jester treatment + bell density.
#
# KEEP-OUT RING: callers must hold a ~10px (true-px) ornament-free margin just
# OUTSIDE the cream disc. The face features that ride the disc edge (eyes, grin)
# are seated against the disc-edge keep-out radius the shell returns; horns,
# bells, poms and danglers all live out at the bezel rim (R) and beyond, well
# clear of the disc, so nothing crowds N.

# Disc radius held constant across all cells; the bezel rim R = HD*0.315.
DISC_INNER = 0.74
KEEPOUT_PX = 10  # true-px ornament-free margin just outside the cream disc


def _medallion_shell(canvas, c, R, ss, *, field_plum=PLUM, field_dk=PLUM_DK,
                     bezel_segs=44, fleck_n=16, gold_face=GOLD):
    """Plum field ring → fluted gold bezel → gold disc → cream inner field →
    clipped top-left specular crescent. Returns (cream_radius, keepout_radius):
    the number seats on the cream optical centre and face features stay outside
    the keepout radius. `bezel_segs`/`fleck_n` scale the "loaded" read."""
    HD = canvas.get_width()
    # Plum field ring (not a flat bruise) with a gold keyline.
    field = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(field, field_plum + (235,), (c, c), int(HD * 0.42))
    pygame.draw.circle(field, GOLD + (210,), (c, c), int(HD * 0.42), max(2, int(3 * ss)))
    pygame.draw.circle(field, field_dk + (235,), (c, c), int(HD * 0.365))
    canvas.blit(field, (0, 0))
    # Festive flecks (reads "roll", not "award").
    for i in range(fleck_n):
        a = i * math.tau / fleck_n + 0.4
        dist = HD * 0.365 + (i % 3) * 6 * ss
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist
        col = [GOLD, LIME, CREAM][i % 3]
        if i % 2 == 0:
            sz = (5 + i % 2 * 2) * ss
            d = pygame.Surface((int(sz), int(sz)), pygame.SRCALPHA)
            pygame.draw.polygon(d, col + (235,),
                                [(sz // 2, 0), (sz, sz // 2), (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 51) % 360)
            canvas.blit(d, d.get_rect(center=(int(px), int(py))))
        else:
            pygame.draw.circle(canvas, col, (int(px), int(py)), int(3 * ss))
    # Smooth gold bezel BAND — no radial fluting. The round-2 even-length,
    # even-angle radial ticks turned the rim into a clock/gear face; a clean
    # band with a soft inner shadow + outer keyline keeps it reading as a metal
    # frame, leaving the bells + flecks to carry the festive rim.
    pygame.draw.circle(canvas, GOLD_DK, (c, c), R + int(4 * ss))
    pygame.draw.circle(canvas, gold_face, (c, c), R)
    pygame.draw.circle(canvas, _shade(gold_face, 55), (c, c), R, max(2, int(2 * ss)))
    pygame.draw.circle(canvas, GOLD_DK, (c, c), R - int(6 * ss), max(2, int(3 * ss)))
    pygame.draw.circle(canvas, gold_face, (c, c), R - int(8 * ss))
    # IRREGULAR gold sparkle on the band — jittered angle, distance and size
    # (and a few skipped) so it never falls on the even angular grid that read
    # as tick marks. A scattering of treasure-glints, not a dial.
    for i in range(bezel_segs):
        a = i * math.tau / bezel_segs + (i * i % 7) * 0.11
        if i % 5 == 3:
            continue  # break the rhythm so no even cadence survives
        rr = R - (3 + (i * 3 % 5)) * ss
        sx = c + math.cos(a) * rr
        sy = c + math.sin(a) * rr
        sz = (2 + (i % 3)) * ss
        col = [_shade(gold_face, 70), CREAM, _shade(gold_face, 30)][i % 3]
        pygame.draw.circle(canvas, col, (int(sx), int(sy)), max(1, int(sz * 0.5)))
    # Cream inner field — the number's home, a CONSTANT diameter every cell.
    cr = int(R * DISC_INNER)
    pygame.draw.circle(canvas, (255, 244, 212), (c, c), cr)
    pygame.draw.circle(canvas, PLUM, (c, c), cr, max(2, int(2 * ss)))
    # Clipped top-left specular crescent.
    hl = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, 90), (c - int(R * 0.32), c - int(R * 0.32)),
                       int(R * 0.55))
    mask = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), R - 8 * ss)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(hl, (0, 0))
    return cr, cr + int(KEEPOUT_PX * ss)


def _ribbon_banderole(canvas, c, cy, txt, ss, *, plate_col=PLUM, text_col=CREAM,
                      edge_col=PLUM_DK, size=20, curve=True):
    """The label relocated OFF the disc onto a curved banderole hugging the bezel
    bottom, so the rolled NUMBER can own the disc centre. A shallow plum ribbon
    with notched ends + a gold keyline + lightly-tracked cream lettering.

    Tracking is TIGHT (the font's natural spacing, not letter-by-letter spaces)
    and the body carries wide end padding so the notched tips never bite into
    "PAGODAS"/"JACKPOT" at true size (round 1 read cramped)."""
    lf = hud._font(int(size * ss), True)
    lab = lf.render(txt, True, text_col)
    # Generous end padding so the V-notch on each tip clears the glyphs.
    pw = lab.get_width() + int(48 * ss)
    ph = lab.get_height() + int(12 * ss)
    rib = pygame.Surface((pw, ph), pygame.SRCALPHA)
    notch = int(ph * 0.42)
    body = [(notch, 0), (pw - notch, 0), (pw, ph // 2), (pw - notch, ph),
            (notch, ph), (0, ph // 2)]
    pygame.draw.polygon(rib, plate_col, body)
    pygame.draw.polygon(rib, GOLD, body, max(1, int(2 * ss)))
    edge = lf.render(txt, True, edge_col)
    cxp, cyp = pw // 2, ph // 2
    for ox, oy in ((-ss, 0), (ss, 0), (0, -ss), (0, ss)):
        rib.blit(edge, edge.get_rect(center=(cxp + ox, cyp + oy)))
    rib.blit(lab, lab.get_rect(center=(cxp, cyp)))
    # Folded ribbon tails behind the notched ends for the banderole read.
    for sgn in (-1, 1):
        tx = c + sgn * (pw // 2 - int(4 * ss))
        tail = [(tx, cy - int(ph * 0.3)), (tx + sgn * int(16 * ss), cy - int(ph * 0.5)),
                (tx + sgn * int(13 * ss), cy), (tx + sgn * int(16 * ss), cy + int(ph * 0.5)),
                (tx, cy + int(ph * 0.3))]
        pygame.draw.polygon(canvas, _shade(plate_col, -30), tail)
    canvas.blit(rib, rib.get_rect(center=(c, cy)))


# ── the five DEVILISH medallion cells ────────────────────────────────────────
# The whole sheet is now ONE locked face — the cell-2 DEVILISH look: soft plum
# imp horns cresting the top, sidelong GOLD eye-glints, ONE cocked brow, a
# fanged grin. The menacing variant (dark bruise field + dagged crest + cold
# gold) is dropped: at true size its crest read as a gear/sunburst and its cold
# gold read as tin, not treasure.
#
# N stays the hero in EVERY cell: the cream disc is a CONSTANT diameter (shell's
# DISC_INNER) and a ~10px ornament-free KEEP-OUT ring sits just outside it. Face
# features seat AGAINST the keep-out radius the shell returns (on the gold bezel
# ring, never over the cream); horns, crest bells, and danglers all live at the
# bezel rim R and beyond. The reward ramp reads on just TWO levers: crest-bell
# DENSITY (sparse low → dense high) and the banderole LABEL.
#
# NUMBER CENTRING (all five): the base anchored N at c-12*ss to clear the plate
# below; here it drops to ~c-3*ss (the cream field's optical centre, allowing
# for the bold font's low baseline) with the label moved onto a banderole, so N
# reads dead-centre on the disc and stays dominant.

NCTR = lambda ss: -int(3 * ss)  # optical-centre anchor for the bold number  # noqa: E731


def _even_danglers(canvas, c, R, ss, *, bell_r=5):
    """Symmetric jingle-bell danglers around the bezel BOTTOM — mirrored pairs at
    fixed angles, deliberately rhythmic (round 1's asymmetry read unfinished).
    They flank the banderole's seat without crowding it, and all hang OUTSIDE the
    disc keep-out at the bezel rim. Always the same warm-gold bell."""
    for sgn in (-1, 1):
        for a in (0.58, 1.05):
            _dangler(canvas, c, c, math.pi / 2 + sgn * a, R + 4 * ss, ss,
                     length=12 * ss, bell_r=int(bell_r * ss))


def _devil_face(canvas, c, R, cr, ko, ss, *, glint=True, cocked=True,
                wink_right=False, tongue=False, grin_w=0.36):
    """The locked DEVILISH face, framing the cream disc: sidelong eyes on the
    gold bezel ring ABOVE the disc (seated against the keep-out radius `ko` so
    they never touch the cream), ONE cocked brow for the up-to-no-good
    asymmetry, and a fanged grin on the bezel ring BELOW the disc. `glint` swaps
    the eye catch to gold; `wink_right` closes the right eye into a directional
    downturned wink (the cheeky read)."""
    # Eyes ride a radius just outside the keep-out ring, on the gold bezel, so
    # the cream disc stays N's clean home. Angle keeps them clear of the horns.
    eang = 0.52
    er = ko + int(7 * ss)
    ey = c - int(math.cos(eang) * er)
    for sgn in (-1, 1):
        ex = c + sgn * int(math.sin(eang) * er)
        if wink_right and sgn > 0:
            _winking_lash(canvas, ex, ey, ss, sgn=sgn)
        else:
            _sly_eye(canvas, ex, ey, ss, look=-int(2 * ss), r=int(6 * ss),
                     glint=glint)
            _sly_brow(canvas, ex, ey - int(9 * ss), ss, sgn=sgn,
                      cocked=(cocked and sgn < 0))
    # Grin seated against the keep-out below the disc, on the gold bezel ring.
    gr = ko + int(6 * ss)
    _fanged_grin(canvas, c, gr, ss, w=int(cr * grin_w), tongue=tongue)


def _winking_lash(canvas, x, y, ss, *, sgn, col=INK):
    """A CLOSED happy wink — a lash curve that DOWNTURNS (smiles closed) with two
    short lashes flicking off the outer corner, so at ~8px it reads directionally
    DIFFERENT from the round open eye (which is a filled disc with a pupil)."""
    w, h = int(8 * ss), int(6 * ss)
    # A downturned closed-eye crescent: the lid bows DOWN at the centre.
    pygame.draw.arc(canvas, col, (x - w, y - h, w * 2, h * 2),
                    math.pi * 1.12, math.tau * 0.98, max(2, int(3 * ss)))
    # Lashes flicking off the OUTER corner so the wink has a clear direction.
    ox = x + sgn * w
    for dy in (-2, 1, 4):
        pygame.draw.line(canvas, col, (ox, y + int(dy * ss * 0.4)),
                         (ox + sgn * int(5 * ss), y + int((dy - 1) * ss)),
                         max(1, int(2 * ss)))


def _devil_medallion(roll, ss, *, bell_count, label, glint=True, cocked=True,
                     wink_right=False, tongue=False, grin_w=0.36,
                     bezel_segs=48, fleck_n=16, ramp_recede=False, horn_len=1.0):
    """The ONE locked DEVILISH medallion every cell shares. Plum field → gold
    bezel → constant-diameter cream disc with its keep-out ring → soft plum imp
    horns cresting the top → a crest of warm-GOLD bells (count is the ramp lever)
    → the devil face (eyes/brow/grin) seated on the bezel ring outside the
    keep-out → even gold danglers flanking the bottom → the banderole label.

    `ramp_recede` knocks the crest bells DOWN in value/size so the gold ring
    recedes behind N on the jackpot (the digits must out-shout the ornament)."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    R = int(HD * 0.315)
    cr, ko = _medallion_shell(canvas, c, R, ss, bezel_segs=bezel_segs,
                              fleck_n=fleck_n)

    # Soft plum imp horns crest the top — drawn BEFORE the crest bells so the
    # bells (which fan around the top arc) sit in front of the horn bases.
    _imp_horn(canvas, c, c, R, ss, sgn=-1, col=PLUM, length=horn_len)
    _imp_horn(canvas, c, c, R, ss, sgn=1, col=PLUM, length=horn_len)

    # The reward-ramp lever: a fan of warm-gold crest bells, sparse → dense. On
    # the jackpot the bells are smaller + a muted gold (value knocked ~18%) so
    # the dense ring RECEDES behind the hero digits instead of competing.
    bell_r = 5 if ramp_recede else 6
    bell_col = GOLD_RECEDE if ramp_recede else GOLD
    _crest_bells(canvas, c, c, R, ss, count=bell_count, bell_r=bell_r, col=bell_col)

    # Even gold danglers flanking the bezel bottom — symmetric, rhythmic.
    _even_danglers(canvas, c, R, ss)

    _devil_face(canvas, c, R, cr, ko, ss, glint=glint, cocked=cocked,
                wink_right=wink_right, tongue=tongue, grin_w=grin_w)

    # N: hero, dead-centre on the constant cream disc, the sheet's highest-
    # contrast pair (plum on cream). Drawn LAST so nothing crosses it.
    _num_block(canvas, c, c + NCTR(ss), roll, ss, size=92,
               num_col=PLUM, edge_col=CREAM, edge_w=4)

    _ribbon_banderole(canvas, c, c + R + int(15 * ss), label, ss, size=16)
    return canvas, D


def var_hero(roll, ss):
    """DEVILISH HERO — the refined locked template: plum imp horns, gold-glint
    eyes, ONE cocked brow, a fanged grin, even danglers. The standard "you
    rolled N" celebration look; N dead-centre and dominant."""
    return _devil_medallion(roll, ss, bell_count=7, label="PAGODAS")


def var_hero_2digit(roll, ss):
    """DEVILISH HERO (2-digit) — the same template, confirming a 2-digit N stays
    centred and dominant inside the disc keep-out ring."""
    return _devil_medallion(roll, ss, bell_count=7, label="PAGODAS")


def var_ramp_low(roll, ss):
    """RAMP LOW (PAGODAS) — the plain tier: the devilish face with a SPARSE
    3-bell crest (now reading as proper bells, the round-2 fix that mattered
    most here), a thinner bezel and fewer flecks. The everyday low roll."""
    return _devil_medallion(roll, ss, bell_count=3, label="PAGODAS",
                            bezel_segs=40, fleck_n=12, grin_w=0.34)


def var_ramp_jackpot(roll, ss):
    """RAMP JACKPOT (JACKPOT) — the SAME language LOADED on just two legible
    levers: a DENSE gold crest-bell fan and the JACKPOT label. De-cluttered (no
    poms / star toppers), with the bell-ring value knocked down so the 25 stays
    the hero. A wider tongue-out grin is the only extra payoff reaction."""
    return _devil_medallion(roll, ss, bell_count=11, label="JACKPOT",
                            bezel_segs=56, fleck_n=24, tongue=True, grin_w=0.40,
                            ramp_recede=True, horn_len=1.05)


def var_detail(roll, ss):
    """DETAIL INSET — a zoomed verification panel (NOT a medallion) showing the
    two round-3 fixes up close so they can be eyeballed at large scale: the NEW
    bell silhouette (dome + flared mouth, no antenna) and the sharpened DEVILISH
    grin (narrow, single asymmetric fang, one curled corner). On a plum panel
    with gold keyline; `roll` is ignored. Same draw helpers as the live cells so
    what is verified here is exactly what ships."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    # Plum verification panel with a gold keyline, matching the family metal.
    pygame.draw.rect(canvas, PLUM_DK, canvas.get_rect(), border_radius=int(18 * ss))
    pygame.draw.rect(canvas, GOLD, canvas.get_rect(), max(2, int(3 * ss)),
                     border_radius=int(18 * ss))
    # LEFT: one big bell at ~3x the live crest size so the dome + flared mouth +
    # tiny suspension loop read unambiguously. A short cord roots it like a crest
    # bell so the hung-bell silhouette is shown in context.
    big_r = int(18 * ss)
    bx = c - int(58 * ss)
    by = c - int(6 * ss)
    pygame.draw.line(canvas, PLUM_DK, (bx, by - int(big_r * 2.4)),
                     (bx, by - int(big_r * 1.4)), max(2, int(3 * ss)))
    _bell(canvas, bx, by, big_r)
    # RIGHT: the sharpened grin alone, large, on a cream chip so the asymmetry +
    # single fang + curled corner read without the eyes/horns around it.
    chip_r = int(46 * ss)
    gx = c + int(48 * ss)
    gy = c - int(2 * ss)
    pygame.draw.circle(canvas, (255, 244, 212), (gx, gy), chip_r)
    pygame.draw.circle(canvas, PLUM, (gx, gy), chip_r, max(2, int(2 * ss)))
    _fanged_grin(canvas, gx, gy + int(2 * ss), ss, w=int(34 * ss))
    return canvas, D


VARIANTS = [
    ("1  STANDARD CELEBRATION", "7 bell crest, no clock rim, sharpened fang grin", "day",
     var_hero, 19),
    ("2  STANDARD CELEBRATION", "same template, different digits, confirms read", "day",
     var_hero_2digit, 22),
    ("3  RAMP LOW — PAGODAS", "SPARSE 3-bell crest (now true bells), thinner bezel", "day",
     var_ramp_low, 11),
    ("4  RAMP JACKPOT — JACKPOT", "DENSE 11-bell crest, ring receded, the payoff", "day",
     var_ramp_jackpot, 25),
    ("5  DETAIL INSET", "NEW bell silhouette + sharpened devilish grin, up close", "day",
     var_detail, 0),
]


def main():
    SS = 4
    TRUE = 264
    INSET = 116
    cols = 3
    rows = 2
    pad = 20
    head = 78
    tile_w = TRUE + INSET + 40
    tile_h = TRUE + 96
    sheet_w = cols * tile_w + (cols + 1) * pad
    sheet_h = head + rows * tile_h + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 42))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(
        "Dice Medallion — Round 3: bells read as BELLS, no clock-dial rim, sharpened devilish grin",
        True, (255, 255, 255)), (pad, 12))
    sheet.blit(sub_f.render(
        "Geometry HELD from round 2 (keep-out ring, constant cream disc R*0.74, horn clearance, "
        "N drawn LAST + dominant). Crest bells now a dome + flared-mouth silhouette, not a dot on a stalk.",
        True, (200, 205, 215)), (pad, 40))
    sheet.blit(sub_f.render(
        "Rim is a smooth gold band with IRREGULAR sparkle (no radial ticks). Grin narrowed to a smug "
        "smirk: ONE curled corner + single asymmetric fang. Cheeky face CUT — one face everywhere.",
        True, (170, 178, 190)), (pad, 58))

    label_f = hud._font(18, True)
    samp_f = hud._font(13, True)

    for idx, (name, desc, sky, fn, roll) in enumerate(VARIANTS):
        col = idx % cols
        row = idx // cols
        tx = pad + col * (tile_w + pad)
        ty = head + pad + row * (tile_h + pad)

        if sky == "night":
            tile = sky_tile(tile_w, tile_h, NIGHT_TOP, NIGHT_BOT, lo=0.10, hi=0.55)
            chip_top, chip_bot, chip_lo, chip_hi = NIGHT_TOP, NIGHT_BOT, 0.10, 0.55
        else:
            tile = sky_tile(tile_w, tile_h)
            chip_top, chip_bot, chip_lo, chip_hi = SKY_TOP, SKY_BOT, 0.35, 0.80
        canvas, D = fn(roll, SS)

        out = pygame.transform.smoothscale(canvas, (TRUE, TRUE))
        tile.blit(out, out.get_rect(center=(16 + TRUE // 2, 36 + TRUE // 2)))

        chip = sky_tile(INSET + 16, INSET + 16, chip_top, chip_bot, chip_lo, chip_hi)
        ins = pygame.transform.smoothscale(canvas, (INSET, INSET))
        chip.blit(ins, ins.get_rect(center=((INSET + 16) // 2, (INSET + 16) // 2)))
        pygame.draw.rect(chip, (255, 255, 255), chip.get_rect(), 2)
        cr = chip.get_rect()
        cr.bottomright = (tile_w - 8, tile_h - 34)
        tile.blit(chip, cr)
        ilab = samp_f.render("actual size", True, (255, 255, 255))
        ib = pygame.Surface((ilab.get_width() + 6, ilab.get_height() + 2),
                            pygame.SRCALPHA)
        ib.fill((20, 22, 28, 200))
        ib.blit(ilab, (3, 1))
        tile.blit(ib, (cr.left, cr.top - ib.get_height() - 1))

        strip = pygame.Surface((tile_w, 30), pygame.SRCALPHA)
        strip.fill((20, 22, 28, 205))
        tile.blit(strip, (0, 0))
        tile.blit(label_f.render(name, True, LIME), (8, 6))
        cap = pygame.Surface((tile_w, 24), pygame.SRCALPHA)
        cap.fill((20, 22, 28, 205))
        tile.blit(cap, (0, tile_h - 24))
        # The detail-inset cell has no roll; everything else always rolls 10..25.
        cap_txt = desc if roll == 0 else f"{desc}  (roll {roll})"
        tile.blit(samp_f.render(cap_txt, True, (220, 225, 235)),
                  (8, tile_h - 21))
        sheet.blit(tile, (tx, ty))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "dice_results", "medallion")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
