"""Dice-results medallion — the celebration frame for a settled warren roll.

A struck jester medallion announces the rolled N (the warren route length): a
plum field ring + smooth gold bezel + constant-diameter cream disc that hosts
the hero number, framed by the hero clown's mischievous identity — soft plum
imp horns cresting the top, a fan of warm-gold jingle bells, sidelong sly eyes
with one cocked brow, and a single-fanged smug grin.

The number is the hero in every tier: the cream disc is a CONSTANT diameter and
a small ornament-free keep-out ring sits just outside it, so horns, bells and
the face all live out at the bezel rim and never crowd N (which is drawn last).

The reward ramp reads on two glance-legible levers only — crest-bell DENSITY and
the banderole LABEL:
  * low roll  → sparse 3-bell crest, "PAGODAS"
  * mid roll  → 7-bell crest, "PAGODAS"
  * high roll → dense 11-bell crest, value receded so N stays hero, "JACKPOT"
A GHOST roll re-skins the same medallion to a navy field + cyan-tinted eyes +
"GHOST!", reading as a spooky sibling of the normal frame.

Drawn from code (no sprite assets) and self-contained under game/ so it ships in
both the native and pygbag/WASM builds — it touches only pygame and the vendored
font cache, never the mixer or any tools/ helper.
"""
import math

import pygame

from game import hud  # vendored bold TTF + size cache

# Hero clown "Plum & Lime" palette.
PLUM = (96, 44, 150)
PLUM_DK = (66, 28, 110)
LIME = (132, 218, 116)
GOLD = (250, 205, 72)
CREAM = (255, 248, 224)
CREAM_DISC = (255, 244, 212)
GOLD_DK = (180, 132, 28)
# A muted gold for the JACKPOT crest bells: ~18% value/saturation off the hero
# GOLD so the dense bell-ring RECEDES behind the hero digits instead of competing
# — still warm treasure-gold, never a cold tin.
GOLD_RECEDE = (206, 168, 78)
INK = (28, 22, 30)
MOUTH_DK = (120, 30, 42)
# GHOST re-skin: a lifted navy body holds its own value against a near-black
# night sky while the gold bezel keyline carries the silhouette; cyan eye-catches
# read spooky without a second popup shape.
NAVY = (50, 34, 96)
NAVY_DK = (30, 20, 64)
GHOST_GLINT = (150, 240, 230)
GHOST_SCLERA = (224, 250, 248)

DISC_INNER = 0.74     # cream-disc radius as a fraction of the bezel rim R
KEEPOUT_PX = 10       # ornament-free margin (true px) just outside the cream disc
NCTR = lambda ss: -int(3 * ss)  # optical-centre anchor for the bold number  # noqa: E731


def _shade(c, d):
    return (max(0, min(255, int(c[0] + d))),
            max(0, min(255, int(c[1] + d))),
            max(0, min(255, int(c[2] + d))))


def _num_block(canvas, c, ncy, roll, ss, size=88, num_col=CREAM, edge_col=PLUM,
               shadow_a=110, edge_w=5):
    """The hero number — vendored bold font with a drop shadow + thick outline
    ring. The outline is stroked as a fine-step ring at one radius and the fill
    is re-stamped LAST, so the digit counters (holes in 2/8/0) stay open instead
    of clogging with edge ink at true size."""
    nf = hud._font(int(size * ss), True)
    num = nf.render(str(roll), True, num_col)
    edge = nf.render(str(roll), True, edge_col)
    shadow = nf.render(str(roll), True, (0, 0, 0))
    shadow.set_alpha(shadow_a)
    canvas.blit(shadow, shadow.get_rect(center=(c + 3 * ss, ncy + 5 * ss)))
    o = edge_w * ss
    for ang in range(0, 360, 15):
        ox = math.cos(math.radians(ang)) * o
        oy = math.sin(math.radians(ang)) * o
        canvas.blit(edge, edge.get_rect(center=(c + ox, ncy + oy)))
    nb = num.get_rect(center=(c, ncy))
    canvas.blit(num, nb)
    return nb


def _bell(canvas, x, y, r, *, col=GOLD):
    """A chunky warm-gold jingle bell drawn as a true bell SILHOUETTE so it reads
    as a bell at a glance, never a pin/antenna/stud: a domed shoulder that swells
    out and flares into a wide bell-mouth (one continuous mass, not a ball on a
    stalk), a tiny suspension loop barely peeking over the dome, the plum
    bell-mouth shadow + clapper, and one hot specular dot. `r` is the body
    half-width; the mouth half-width is ~1.3r so the flare holds when shrunk."""
    x, y = int(x), int(y)
    r = max(3, int(r))
    bw = r * 3
    bh = int(r * 3.2)
    s = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cxp = bw // 2
    body_dk = _shade(col, -65)
    loop_y = max(2, int(r * 0.35))
    shoulder_cy = int(r * 1.25)
    shoulder_r = int(r * 0.92)
    mouth_y = bh - max(2, int(r * 0.45))
    top_hw = int(r * 0.82)
    bot_hw = int(r * 1.30)
    waist_y = int(shoulder_cy + shoulder_r * 0.55)
    pygame.draw.line(s, body_dk, (cxp, loop_y + int(r * 0.2)),
                     (cxp, shoulder_cy - int(shoulder_r * 0.4)), max(2, int(r * 0.22)))
    pygame.draw.circle(s, body_dk, (cxp, loop_y), max(2, int(r * 0.26)),
                       max(1, int(r * 0.14)))
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
    lip_h = max(3, int(r * 0.72))
    pygame.draw.ellipse(s, PLUM_DK,
                        (cxp - bot_hw, mouth_y - lip_h // 2, bot_hw * 2, lip_h))
    pygame.draw.ellipse(s, col,
                        (cxp - bot_hw, mouth_y - lip_h // 2, bot_hw * 2, lip_h),
                        max(1, int(r * 0.22)))
    pygame.draw.circle(s, _shade(col, 55), (cxp, mouth_y - max(1, int(r * 0.04))),
                       max(2, int(r * 0.28)))
    pygame.draw.circle(s, _shade(col, 95),
                       (cxp - int(shoulder_r * 0.4), shoulder_cy - int(shoulder_r * 0.35)),
                       max(1, int(r * 0.3)))
    canvas.blit(s, s.get_rect(center=(x, y + int(r * 0.3))))


def _dangler(canvas, cx, cy, ang, R, ss, *, length, bell_r, col=GOLD, cord=PLUM_DK):
    """A jester bell hanging off the bezel rim on a short cord at angle `ang`, the
    cord rooting just inside the rim so the medallion reads fringed with bells."""
    rx = cx + math.cos(ang) * (R - 2 * ss)
    ry = cy + math.sin(ang) * (R - 2 * ss)
    bx = cx + math.cos(ang) * (R + length)
    by = cy + math.sin(ang) * (R + length)
    pygame.draw.line(canvas, cord, (int(rx), int(ry)), (int(bx), int(by)),
                     max(2, int(2 * ss)))
    _bell(canvas, bx, by, bell_r, col=col)


def _imp_horn(canvas, cx, cy, R, ss, *, sgn, col, length=1.0):
    """A soft imp horn cresting the medallion — a stubby rounded nub curling
    outward+up with a bell-lit tip: devilish but impish, never a menace spike."""
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
    """A fan of warm-gold bells cresting the TOP of the bezel on short cords — the
    reward ramp's primary lever. `count` is the only thing that changes between
    the sparse and dense tiers; each bell hangs on its own cord so the crest reads
    as a row of bells, never a beaded rim. The arc nestles between the two imp
    horns (±0.42 from the top), and all of it sits outside the disc keep-out."""
    if count < 1:
        return
    top = -math.pi / 2
    for i in range(count):
        t = 0.5 if count == 1 else i / (count - 1)
        a = top - arc / 2 + arc * t
        rx = cx + math.cos(a) * (R + 1 * ss)
        ry = cy + math.sin(a) * (R + 1 * ss)
        clen = (10 + (i % 2) * 4) * ss   # gentle scallop, still even
        bx = cx + math.cos(a) * (R + clen)
        by = cy + math.sin(a) * (R + clen)
        pygame.draw.line(canvas, PLUM_DK, (int(rx), int(ry)), (int(bx), int(by)),
                         max(2, int(2 * ss)))
        _bell(canvas, bx, by, bell_r, col=col)


def _sly_eye(canvas, x, y, ss, *, look, r=7, glint=False,
             sclera=CREAM, pupil=(44, 38, 60), glint_col=None):
    """A bright sly eye glancing sidelong (`look`<0 = inward). `glint` swaps the
    white catch for a sidelong gold (or `glint_col`) catch for the devilish read."""
    ew, eh = int(r * 0.85), int(r)
    pygame.draw.ellipse(canvas, sclera, (x - ew, y - eh, ew * 2, eh * 2))
    pygame.draw.ellipse(canvas, _shade(sclera, -70), (x - ew, y - eh, ew * 2, eh * 2),
                        max(1, int(ss)))
    px = int(x + look)
    py = int(y + 1 * ss)
    pygame.draw.circle(canvas, pupil, (px, py), int(r * 0.55))
    pygame.draw.circle(canvas, INK, (px, py), int(r * 0.55), max(1, int(ss)))
    cl = glint_col if glint_col else (GOLD if glint else (255, 255, 255))
    pygame.draw.circle(canvas, cl, (px - int(r * 0.3), py - int(r * 0.4)),
                       max(1, int(r * 0.22)))
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
    """A narrow asymmetric smug smirk — not a wide even happy smile. ONE corner
    (the fang side) curls UP higher than the other, the mouth carries only a
    sliver of teeth plus a single prominent ASYMMETRIC FANG, so it reads "smug
    imp", not "happy emoji". `fang_sgn` picks the fang/curl side; `tongue` adds a
    tip lick."""
    up = fang_sgn
    nw = w * 0.78
    curl_c = (cx + up * nw, gy - 8 * ss)
    flat_c = (cx - up * nw * 0.85, gy + 3 * ss)
    bottom = (cx - up * nw * 0.12, gy + 10 * ss)
    mouth = [curl_c, (cx + up * nw * 0.32, gy - 2 * ss), flat_c,
             (cx - up * nw * 0.28, gy + 6 * ss), bottom, (cx + up * nw * 0.16, gy + 5 * ss)]
    pygame.draw.polygon(canvas, MOUTH_DK, mouth)
    teeth = [curl_c, (cx + up * nw * 0.32, gy - 2 * ss),
             (cx + up * nw * 0.06, gy + 1 * ss), (cx + up * nw * 0.14, gy + 3 * ss),
             (cx + up * nw * 0.34, gy + 2 * ss)]
    pygame.draw.polygon(canvas, (250, 248, 240), teeth)
    pygame.draw.polygon(canvas, _shade((250, 248, 240), -80), teeth, max(1, int(ss)))
    gx = cx + up * nw * 0.2
    pygame.draw.line(canvas, _shade((250, 248, 240), -80),
                     (gx, gy - 1 * ss), (gx, gy + 3 * ss), max(1, int(ss)))
    fx = cx + fang_sgn * nw * 0.46
    fang = [(fx - 5 * ss, gy + 1 * ss), (fx + 5 * ss, gy + 1 * ss), (fx, gy + 12 * ss)]
    pygame.draw.polygon(canvas, (252, 250, 244), fang)
    pygame.draw.polygon(canvas, _shade((252, 250, 244), -80), fang, max(1, int(ss)))
    lip = []
    for k in range(13):
        t = k / 12.0
        lx = flat_c[0] + (curl_c[0] - flat_c[0]) * t
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


def _medallion_shell(canvas, c, R, ss, *, field_plum=PLUM, field_dk=PLUM_DK,
                     bezel_segs=44, fleck_n=16, gold_face=GOLD):
    """Plum field ring → smooth gold bezel → gold disc → cream inner field →
    clipped top-left specular crescent. Returns (cream_radius, keepout_radius):
    the number seats on the cream optical centre, face features stay outside the
    keepout radius. The outer gold field-keyline carries the silhouette even when
    the field is the dark GHOST navy on a night sky."""
    HD = canvas.get_width()
    field = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(field, field_plum + (235,), (c, c), int(HD * 0.42))
    pygame.draw.circle(field, GOLD + (210,), (c, c), int(HD * 0.42), max(2, int(3 * ss)))
    pygame.draw.circle(field, field_dk + (235,), (c, c), int(HD * 0.365))
    canvas.blit(field, (0, 0))
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
    # A clean gold band with a soft inner shadow + outer keyline — no radial
    # fluting (even ticks read as a clock/gear face); the bells + flecks carry
    # the festive rim instead.
    pygame.draw.circle(canvas, GOLD_DK, (c, c), R + int(4 * ss))
    pygame.draw.circle(canvas, gold_face, (c, c), R)
    pygame.draw.circle(canvas, _shade(gold_face, 55), (c, c), R, max(2, int(2 * ss)))
    pygame.draw.circle(canvas, GOLD_DK, (c, c), R - int(6 * ss), max(2, int(3 * ss)))
    pygame.draw.circle(canvas, gold_face, (c, c), R - int(8 * ss))
    # Irregular jittered sparkle on the band (a few skipped) so it never falls on
    # an even angular grid that reads as tick marks — treasure-glints, not a dial.
    for i in range(bezel_segs):
        a = i * math.tau / bezel_segs + (i * i % 7) * 0.11
        if i % 5 == 3:
            continue
        rr = R - (3 + (i * 3 % 5)) * ss
        sx = c + math.cos(a) * rr
        sy = c + math.sin(a) * rr
        sz = (2 + (i % 3)) * ss
        col = [_shade(gold_face, 70), CREAM, _shade(gold_face, 30)][i % 3]
        pygame.draw.circle(canvas, col, (int(sx), int(sy)), max(1, int(sz * 0.5)))
    cr = int(R * DISC_INNER)
    pygame.draw.circle(canvas, CREAM_DISC, (c, c), cr)
    pygame.draw.circle(canvas, PLUM, (c, c), cr, max(2, int(2 * ss)))
    hl = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, 90), (c - int(R * 0.32), c - int(R * 0.32)),
                       int(R * 0.55))
    mask = pygame.Surface((HD, HD), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (c, c), R - 8 * ss)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    canvas.blit(hl, (0, 0))
    return cr, cr + int(KEEPOUT_PX * ss)


def _ribbon_banderole(canvas, c, cy, txt, ss, *, plate_col=PLUM, text_col=CREAM,
                      edge_col=PLUM_DK, size=20):
    """The label relocated OFF the disc onto a curved banderole hugging the bezel
    bottom, so the rolled number can own the disc centre. A shallow plum ribbon
    with notched ends + a gold keyline + tracked cream lettering; the body carries
    wide end padding so the notched tips never bite into the word."""
    lf = hud._font(int(size * ss), True)
    lab = lf.render(txt, True, text_col)
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
    for sgn in (-1, 1):
        tx = c + sgn * (pw // 2 - int(4 * ss))
        tail = [(tx, cy - int(ph * 0.3)), (tx + sgn * int(16 * ss), cy - int(ph * 0.5)),
                (tx + sgn * int(13 * ss), cy), (tx + sgn * int(16 * ss), cy + int(ph * 0.5)),
                (tx, cy + int(ph * 0.3))]
        pygame.draw.polygon(canvas, _shade(plate_col, -30), tail)
    canvas.blit(rib, rib.get_rect(center=(c, cy)))


def _even_danglers(canvas, c, R, ss, *, bell_r=5):
    """Symmetric mirrored jingle-bell danglers around the bezel BOTTOM, flanking
    the banderole without crowding it, all hung outside the disc keep-out."""
    for sgn in (-1, 1):
        for a in (0.58, 1.05):
            _dangler(canvas, c, c, math.pi / 2 + sgn * a, R + 4 * ss, ss,
                     length=12 * ss, bell_r=int(bell_r * ss))


def _devil_face(canvas, c, R, cr, ko, ss, *, glint=True, cocked=True,
                tongue=False, grin_w=0.36, glint_col=None, sclera=CREAM):
    """The devilish face framing the cream disc: sidelong eyes on the gold bezel
    ring ABOVE the disc (seated against the keep-out radius `ko` so they never
    touch the cream), ONE cocked brow for the up-to-no-good asymmetry, and a
    fanged grin on the bezel ring BELOW the disc."""
    eang = 0.52
    er = ko + int(7 * ss)
    ey = c - int(math.cos(eang) * er)
    for sgn in (-1, 1):
        ex = c + sgn * int(math.sin(eang) * er)
        _sly_eye(canvas, ex, ey, ss, look=-int(2 * ss), r=int(6 * ss),
                 glint=glint, glint_col=glint_col, sclera=sclera)
        _sly_brow(canvas, ex, ey - int(9 * ss), ss, sgn=sgn,
                  cocked=(cocked and sgn < 0))
    gr = ko + int(6 * ss)
    _fanged_grin(canvas, c, gr, ss, w=int(cr * grin_w), tongue=tongue)


def _devil_medallion(roll, ss, *, bell_count, label, tongue=False, grin_w=0.36,
                     bezel_segs=48, fleck_n=16, ramp_recede=False, horn_len=1.0,
                     ghost=False):
    """The one locked devilish medallion every tier shares. Plum (or GHOST navy)
    field → gold bezel → constant-diameter cream disc with its keep-out ring →
    soft plum imp horns → a crest of warm-gold bells (count is the ramp lever) →
    the devil face seated on the bezel ring outside the keep-out → even gold
    danglers → the banderole label. `ramp_recede` knocks the crest bells down in
    value/size so the gold ring recedes behind N on the jackpot."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)
    R = int(HD * 0.315)
    field_plum = NAVY if ghost else PLUM
    field_dk = NAVY_DK if ghost else PLUM_DK
    cr, ko = _medallion_shell(canvas, c, R, ss, field_plum=field_plum,
                              field_dk=field_dk, bezel_segs=bezel_segs,
                              fleck_n=fleck_n)
    horn_col = NAVY_DK if ghost else PLUM
    _imp_horn(canvas, c, c, R, ss, sgn=-1, col=horn_col, length=horn_len)
    _imp_horn(canvas, c, c, R, ss, sgn=1, col=horn_col, length=horn_len)
    bell_r = 5 if ramp_recede else 6
    bell_col = GOLD_RECEDE if ramp_recede else GOLD
    _crest_bells(canvas, c, c, R, ss, count=bell_count, bell_r=bell_r, col=bell_col)
    _even_danglers(canvas, c, R, ss)
    _devil_face(canvas, c, R, cr, ko, ss, tongue=tongue, grin_w=grin_w,
                glint_col=GHOST_GLINT if ghost else None,
                sclera=GHOST_SCLERA if ghost else CREAM)
    # N: hero, dead-centre on the constant cream disc (plum on cream, the
    # highest-contrast pair). Drawn LAST so nothing crosses it.
    _num_block(canvas, c, c + NCTR(ss), roll, ss, size=92,
               num_col=PLUM, edge_col=CREAM, edge_w=4)
    band = PLUM if not ghost else NAVY
    _ribbon_banderole(canvas, c, c + R + int(15 * ss), label, ss, size=16,
                      plate_col=band)
    return canvas, D


# Reward-ramp thresholds: a high roll pays off with a denser crest + "JACKPOT".
JACKPOT_FROM = 23
LOW_TO = 14


def render(roll, ghost, ss):
    """The dice-results medallion for a settled roll, at supersample `ss`.

    Returns (canvas, D): an SRCALPHA medallion `D` design-px wide rendered at
    `ss`× — the caller pops it in and smooth-scales it down. The tier is chosen
    by the roll value (sparse/mid/dense crest + label); a GHOST roll re-skins the
    same medallion navy with "GHOST!"."""
    if ghost:
        return _devil_medallion(roll, ss, bell_count=7, label="GHOST!",
                                grin_w=0.36, ghost=True)
    if roll <= LOW_TO:
        return _devil_medallion(roll, ss, bell_count=3, label="PAGODAS",
                                bezel_segs=40, fleck_n=12, grin_w=0.34)
    if roll >= JACKPOT_FROM:
        return _devil_medallion(roll, ss, bell_count=11, label="JACKPOT",
                                bezel_segs=56, fleck_n=24, tongue=True,
                                grin_w=0.40, ramp_recede=True, horn_len=1.05)
    return _devil_medallion(roll, ss, bell_count=7, label="PAGODAS")
