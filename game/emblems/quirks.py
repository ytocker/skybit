"""Bespoke engraved center glyphs for the BATCH 2 Hall-of-Fame achievements.

Same struck-metal engrave idiom as ``game.achievement_icons`` and its sibling
``game.emblems`` modules: each ``_glyph_<id>(surf, cx, cy, r, col)`` draws BOLD
filled polygons / thick lines / discs in the passed ``col`` only, so the
builder's down-right inset + up-left sheen passes give every silhouette the same
relief. Recessed interior cues (eye sockets, phased pillar edge, magnified line)
use ``ai._GLYPH_SH``; nothing carries a saturated accent here (these read pure
gold), so ``_accent`` is unused. Glyph footprint is ~22px (builder calls at
``gr = R*0.52``); nothing thinner than ~2px or smaller than ~4px, since detail
muds at 44px row size inside the wreath.

Render-harness asset under ``tools/`` — it patches the live glyph table at
runtime (see ``render2.py``) and ships nothing into the game.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai


# ── shared primitives ────────────────────────────────────────────────────────

def _sparkle(surf, cx, cy, r, col, reach=0.92, waist=0.28):
    # The franchise four-point sparkle body, reused so the energy motifs read as
    # siblings of the powerup category anchor.
    pts = [
        (cx, cy - r * reach), (cx + r * waist, cy - r * waist),
        (cx + r * reach, cy), (cx + r * waist, cy + r * waist),
        (cx, cy + r * reach), (cx - r * waist, cy + r * waist),
        (cx - r * reach, cy), (cx - r * waist, cy - r * waist),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


def _bolt(surf, x0, y0, x1, y1, col, w, kink=0.24):
    # A short two-segment lightning tick between two points — the "crackle".
    dx, dy = x1 - x0, y1 - y0
    L = max(1.0, math.hypot(dx, dy))
    px, py = -dy / L, dx / L
    mx, my = (x0 + x1) / 2 + px * L * kink, (y0 + y1) / 2 + py * L * kink
    pygame.draw.lines(surf, col, False,
                      [(int(x0), int(y0)), (int(mx), int(my)), (int(x1), int(y1))], w)


# ── 1. overloaded — three overlapping four-point sparkles crackling ──────────
def _glyph_overloaded(surf, cx, cy, r, col):
    # THREE chunky sparkles in a kissing trefoil (the read: three effects at
    # once), with a short lightning tick crackling in each gap BETWEEN them —
    # contained inside the star cluster so the count-of-3 stays the silhouette,
    # not a messy spike-ball. Distinct from the single powerup sparkle by number.
    sr = r * 0.48
    rt = r * 0.50
    cen = [(cx + math.cos(a) * rt, cy + math.sin(a) * rt)
           for a in (math.radians(-90), math.radians(150), math.radians(30))]
    # Crackle first (under the stars) — a short bolt in each of the three inner
    # gaps (down, upper-left, upper-right), kept between centre and the star kiss
    # so it reads as energy arcing across the cluster, not extra points.
    bw = max(2, int(r * 0.08))
    for a in (math.radians(90), math.radians(210), math.radians(330)):
        x0, y0 = cx + math.cos(a) * r * 0.18, cy + math.sin(a) * r * 0.20
        x1, y1 = cx + math.cos(a) * r * 0.56, cy + math.sin(a) * r * 0.58
        _bolt(surf, x0, y0, x1, y1, col, bw, kink=0.34)
    # Three POINTY four-point sparkles, only just kissing, so the count-of-3 is
    # the silhouette (not a fused rhombus).
    for sx, sy in cen:
        _sparkle(surf, sx, sy, sr, col, reach=0.98, waist=0.24)


# ── 2. bullet_time — stopwatch with a frozen sweep-wedge ─────────────────────
def _glyph_bullet_time(surf, cx, cy, r, col):
    # A stopwatch (Slow-Mo's in-game clock) with ONE bold FILLED pie-wedge swept
    # from 12 o'clock to ~4 o'clock — the second-hand caught mid-sweep, "time
    # freezing". The solid wedge survives 44px where thin echo-hands vanish, and
    # it's what separates this from the plain two-hand clock emblem.
    rr = int(r * 0.64)
    ring_w = max(3, int(r * 0.13))
    # crown nub + two shoulder buttons so it reads stopwatch, not wall clock.
    pygame.draw.rect(surf, col, (cx - max(2, int(r * 0.10)), cy - rr - int(r * 0.24),
                                 max(4, int(r * 0.20)), max(3, int(r * 0.20))),
                     border_radius=max(1, int(r * 0.06)))
    for sgn in (-1, 1):
        a = math.radians(-90 + sgn * 42)
        bx, by = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        pygame.draw.line(surf, col, (int(bx), int(by)),
                         (int(bx + math.cos(a) * r * 0.16),
                          int(by + math.sin(a) * r * 0.16)), max(2, int(r * 0.10)))
    pygame.draw.circle(surf, col, (cx, cy), rr, ring_w)
    # The frozen sweep — a solid pie slice from 12 o'clock (top) clockwise to
    # ~4 o'clock, filled bold so the "part of the dial already swept" reads at
    # row size.
    wr = int(rr * 0.82)
    a0, a1 = math.radians(90), math.radians(-30)     # 12 o'clock → 4 o'clock
    wedge = [(cx, cy)]
    N = 16
    for i in range(N + 1):
        a = a0 + (a1 - a0) * i / N
        wedge.append((cx + math.cos(a) * wr, cy - math.sin(a) * wr))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in wedge])
    # The sweep's START edge (straight up) cut in as a recessed groove so the
    # wedge reads as a slice, not a filled half-disc.
    pygame.draw.line(surf, ai._GLYPH_SH, (cx, cy),
                     (cx, int(cy - wr)), max(2, int(r * 0.09)))
    # The live second-hand riding the wedge's leading edge, bold for definition.
    pygame.draw.line(surf, col, (cx, cy),
                     (int(cx + math.cos(a1) * wr), int(cy - math.sin(a1) * wr)),
                     max(3, int(r * 0.13)))
    pygame.draw.circle(surf, col, (cx, cy), max(2, int(r * 0.11)))


# ── 3. ghost_rider — sheet-ghost phasing through a pillar edge ───────────────
def _glyph_ghost_rider(surf, cx, cy, r, col):
    # A heroic sheet-ghost overlapping a pillar's edge, the pillar showing THROUGH
    # its body (recessed) as it phases past — Ghost's signature. Shimmer ticks
    # trail the leading edge.
    # Pillar edge standing on the right, capped, so the ghost has something to
    # phase THROUGH (drawn first; the ghost overpaints it).
    pcx = cx + int(r * 0.56)
    pw = int(r * 0.40)
    ptop, pbot = cy - int(r * 0.98), cy + int(r * 0.98)
    pygame.draw.rect(surf, col, (pcx - pw // 2, ptop + int(r * 0.14),
                                 pw, pbot - ptop - int(r * 0.28)))
    for yy in (ptop, pbot - int(r * 0.16)):   # capital + base
        pygame.draw.rect(surf, col, (pcx - int(pw * 0.82), yy,
                                     int(pw * 1.64), int(r * 0.16)),
                         border_radius=max(1, int(r * 0.05)))
    # Ghost body — ONE clean outline: a straight-sided sheet, a half-round dome
    # over the top, and a scalloped hem at the bottom. Built as a single ordered
    # ring (left side up, dome across, right side down, hem back) so it can't
    # self-intersect into a skull.
    gcx = cx - int(r * 0.18)
    gw = int(r * 0.98)
    hw = gw / 2
    gshoulder = cy - int(r * 0.26)     # where the straight sides meet the dome
    hem = cy + int(r * 0.60)
    pts = [(gcx - hw, hem), (gcx - hw, gshoulder)]
    for k in range(13):                # dome: left(180) → right(0), bulging up
        a = math.pi - math.pi * k / 12
        pts.append((gcx + math.cos(a) * hw, gshoulder - math.sin(a) * hw))
    pts.append((gcx + hw, hem))
    n = 8                              # scalloped hem, right → left
    for i in range(1, n):
        bx = gcx + hw - gw * i / n
        by = hem - (int(r * 0.20) if i % 2 else 0)
        pts.append((bx, by))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])
    # Where the ghost overlaps the pillar's left edge, show that edge THROUGH the
    # body (recessed) — the phase read.
    exx = pcx - pw // 2
    pygame.draw.line(surf, ai._GLYPH_SH, (exx, gshoulder + int(r * 0.06)),
                     (exx, hem - int(r * 0.06)), max(2, int(r * 0.12)))
    # Two round eyes + a small oval mouth, recessed — the friendly sheet-ghost.
    er = max(3, int(r * 0.15))
    for dx in (-0.28, 0.16):
        pygame.draw.circle(surf, ai._GLYPH_SH,
                           (gcx + int(dx * r), cy - int(r * 0.14)), er)
    pygame.draw.ellipse(surf, ai._GLYPH_SH,
                        (gcx - int(r * 0.10), cy + int(r * 0.10),
                         int(r * 0.20), int(r * 0.26)))
    # Phase shimmer — three short ticks trailing the leading (left) edge.
    for dy in (-0.28, 0.04, 0.36):
        sx = gcx - hw - int(r * 0.14)
        pygame.draw.line(surf, col, (int(sx - r * 0.22), int(cy + dy * r)),
                         (int(sx), int(cy + dy * r)), max(2, int(r * 0.08)))


# ── 4. regifted — gift box wrapped by a repeat/recycle arrow ─────────────────
def _glyph_regifted(surf, cx, cy, r, col):
    # A ribboned gift box hugged by a bold ¾ loop-arrow (the repeat/again cue) —
    # "the box handed you the same thing twice." The bow + ribbon-cross separate
    # it from the plain treasure chest.
    # Loop arrow behind the box: a ¾ ring with an arrowhead, so it appears to
    # circle the gift.
    lr = int(r * 0.92)
    aw = max(3, int(r * 0.12))
    pygame.draw.arc(surf, col, (cx - lr, cy - lr, lr * 2, lr * 2),
                    math.radians(-58), math.radians(210), aw)
    # arrowhead at the loop's open (lower-right) end, pointing clockwise-down.
    ae = math.radians(-58)
    hx, hy = cx + math.cos(ae) * lr, cy - math.sin(ae) * lr
    pygame.draw.polygon(surf, col, [
        (int(hx + r * 0.02), int(hy + r * 0.26)),
        (int(hx + r * 0.26), int(hy - r * 0.06)),
        (int(hx - r * 0.14), int(hy - r * 0.10)),
    ])
    # Gift box on top of the loop — a body + a lid + a vertical ribbon and a
    # two-loop bow.
    bw, bh = int(r * 0.98), int(r * 0.74)
    bx0, by0 = cx - bw // 2, cy - int(r * 0.16)
    pygame.draw.rect(surf, col, (bx0, by0, bw, bh), border_radius=max(1, int(r * 0.06)))
    lid_h = int(r * 0.22)
    pygame.draw.rect(surf, col, (bx0 - int(r * 0.06), by0 - lid_h,
                                 bw + int(r * 0.12), lid_h + int(r * 0.04)),
                     border_radius=max(1, int(r * 0.06)))
    # ribbon down the box face (recessed so it reads as a groove).
    pygame.draw.line(surf, ai._GLYPH_SH, (cx, by0), (cx, by0 + bh), max(2, int(r * 0.11)))
    # Bow atop the lid — two SIDE loops (apex at the centre knot, bases splayed
    # OUT to the sides, like a bow-tie) so it reads as a ribbon bow, not horns.
    ky = by0 - lid_h - int(r * 0.02)
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, col, [
            (cx, ky),
            (cx + sgn * int(r * 0.38), ky - int(r * 0.22)),
            (cx + sgn * int(r * 0.38), ky + int(r * 0.22)),
        ])
    pygame.draw.circle(surf, col, (cx, ky), max(3, int(r * 0.11)))


# ── 5. read_fine_print — scroll of tiny lines under a magnifier ──────────────
def _glyph_read_fine_print(surf, cx, cy, r, col):
    # A single PAGE dense with tiny "text" lines (one corner dog-eared so it
    # reads as paper), a magnifier lens hovering over its lower-right — "you
    # actually scrolled to the very bottom and read it." A flat page + rows of
    # print, deliberately NOT stacked cylinders (which read as a database).
    dw, dh = int(r * 1.04), int(r * 1.34)
    dx0, dy0 = cx - int(r * 0.50), cy - dh // 2
    fold = int(r * 0.28)                # dog-eared upper-right corner
    page = [
        (dx0, dy0), (dx0 + dw - fold, dy0), (dx0 + dw, dy0 + fold),
        (dx0 + dw, dy0 + dh), (dx0, dy0 + dh),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in page])
    # the turned-down corner, recessed, so the fold reads.
    pygame.draw.polygon(surf, ai._GLYPH_SH, [
        (dx0 + dw - fold, dy0), (dx0 + dw, dy0 + fold),
        (dx0 + dw - fold, dy0 + fold)])
    # rows of tiny "print" recessed across the page; the last row short.
    lw = max(2, int(r * 0.075))
    for i in range(5):
        ly = dy0 + int(r * 0.28) + i * int(r * 0.22)
        x_l = dx0 + int(r * 0.16)
        x_r = dx0 + dw - int(r * 0.16) - (fold if i == 0 else 0) - \
            (int(r * 0.34) if i == 4 else 0)
        pygame.draw.line(surf, ai._GLYPH_SH, (x_l, ly), (x_r, ly), lw)
    # Magnifier over the lower-right, breaking the page edge: bold lens ring +
    # thick handle, with one ENLARGED line inside the lens (the "fine print"
    # blown up).
    mx, my = cx + int(r * 0.54), cy + int(r * 0.50)
    mr = int(r * 0.40)
    pygame.draw.circle(surf, ai._GLYPH_SH, (mx, my), mr + max(2, int(r * 0.06)))
    pygame.draw.circle(surf, col, (mx, my), mr, max(3, int(r * 0.14)))
    pygame.draw.line(surf, col, (mx - int(mr * 0.42), my),
                     (mx + int(mr * 0.42), my), max(2, int(r * 0.10)))
    pygame.draw.line(surf, col, (mx + int(mr * 0.64), my + int(mr * 0.64)),
                     (mx + int(r * 0.42), my + int(r * 0.42)), max(4, int(r * 0.16)))


# ── 6. morbid_curiosity — a single eye peeking / glancing down ───────────────
def _glyph_morbid_curiosity(surf, cx, cy, r, col):
    # One wide eye glancing DOWN over an edge — curiosity peeking toward the
    # Shame wall. A bold almond with a heavy upper lid, a low-set dark iris, and a
    # brow + lashes so it can't be mistaken for a skull's socket.
    w = r * 0.94
    uh, lh = r * 0.60, r * 0.44
    upper = [(cx - w + 2 * w * (k / 16), cy - uh * math.sin(math.pi * k / 16))
             for k in range(17)]
    lower = [(cx + w - 2 * w * (k / 16), cy + lh * math.sin(math.pi * k / 16))
             for k in range(17)]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in upper + lower])
    # Iris set LOW against the lower lid = glancing down; a recessed disc with a
    # small lit catch-light.
    ir = int(r * 0.36)
    iy = cy + int(lh * 0.34)
    pygame.draw.circle(surf, ai._GLYPH_SH, (cx, iy), ir)
    pygame.draw.circle(surf, col, (cx - int(ir * 0.34), iy - int(ir * 0.30)),
                       max(2, int(r * 0.09)))
    # Heavier upper lid line (the hood of a peek).
    pygame.draw.lines(surf, col, False, [(int(x), int(y)) for x, y in upper],
                      max(3, int(r * 0.12)))
    # Brow arch above + three short lashes so the read is unmistakably an eye.
    pygame.draw.arc(surf, col, (int(cx - w * 0.9), int(cy - r * 1.14),
                                int(w * 1.8), int(r * 0.9)),
                    math.radians(30), math.radians(150), max(2, int(r * 0.10)))
    for dx in (-0.5, 0.0, 0.5):
        lx = cx + dx * w * 0.7
        ly = cy - uh * math.sin(math.pi * (0.5 + dx * 0.42))
        pygame.draw.line(surf, col, (int(lx), int(ly)),
                         (int(lx + dx * r * 0.14), int(ly - r * 0.22)),
                         max(2, int(r * 0.07)))


# ── 7. are_you_still_there — head-tucked sleeper under a Zzz stack ───────────
def _glyph_are_you_still_there(surf, cx, cy, r, col):
    # A bird fast asleep — a round, head-tucked silhouette (no perch, no beak
    # jutting out) — under a clean stack of THREE separate Z's shrinking as they
    # rise. Each Z is a distinct three-stroke letter with rounded joints so the
    # trio reads as "Zzz" (sleep), never one jagged lightning bolt.
    # Round body, low-left, with a folded-wing groove.
    bcx, bcy = cx - int(r * 0.36), cy + int(r * 0.40)
    br = int(r * 0.52)
    pygame.draw.circle(surf, col, (bcx, bcy), br)
    # Head tucked into the shoulder — a smaller bump merged onto the upper-left,
    # so the silhouette reads as a sleeping bird with its head nestled down.
    hcx, hcy = bcx - int(br * 0.46), bcy - int(br * 0.60)
    hr = int(r * 0.34)
    pygame.draw.circle(surf, col, (hcx, hcy), hr)
    # Closed, curved sleeping eye on the tucked head (recessed).
    pygame.draw.arc(surf, ai._GLYPH_SH,
                    (hcx - int(hr * 0.7), hcy - int(hr * 0.2),
                     int(hr * 1.4), int(hr * 1.0)),
                    math.radians(200), math.radians(340), max(2, int(r * 0.07)))
    # Folded wing — one shallow groove arcing across the body.
    pygame.draw.arc(surf, ai._GLYPH_SH,
                    (bcx - int(br * 0.5), bcy - int(br * 0.55),
                     int(br * 1.4), int(br * 1.2)),
                    math.radians(-40), math.radians(70), max(2, int(r * 0.09)))
    # Three separate Z's rising up-right, large → small. Each is drawn WIDER than
    # tall so its horizontal top/bottom bars dominate (reads as a letter Z), and
    # they're spaced with clear vertical gaps so the trio never fuses into one
    # diagonal lightning streak. The big anchor Z alone already says "sleep".
    zs = [(cx + r * 0.20, cy - r * 0.06, r * 0.40, r * 0.28),
          (cx + r * 0.46, cy - r * 0.58, r * 0.30, r * 0.21),
          (cx + r * 0.66, cy - r * 1.02, r * 0.22, r * 0.16)]
    for zx, zy, zhw, zvh in zs:
        zw = max(3, int(zvh * 0.72))
        tl = (int(zx - zhw), int(zy - zvh))
        tr = (int(zx + zhw), int(zy - zvh))
        bl = (int(zx - zhw), int(zy + zvh))
        br = (int(zx + zhw), int(zy + zvh))
        pygame.draw.lines(surf, col, False, [tl, tr, bl, br], zw)
        for pt in (tl, tr, bl, br):     # round the joints so it reads soft/sleepy
            pygame.draw.circle(surf, col, pt, max(1, zw // 2))


# ── 8. lucky_sevens — horseshoe over a triple of matched luck-pips ──────────
def _glyph_lucky_sevens(surf, cx, cy, r, col):
    # A lucky horseshoe crowning THREE matched pips in a row — the triple-reel
    # jackpot told in shapes not numerals. Drawn OPENING UP (the iconic luck-
    # catching orientation): a thick filled U with its bend at the BOTTOM and the
    # two calk-tipped ends at the TOP — the inversion that reads horseshoe, never
    # the top-band + bottom-cups of a headset.
    rw, rh = r * 0.62, r * 0.74
    hcy = cy - int(r * 0.08)
    band = r * 0.24
    a0, a1 = math.radians(58), math.radians(-238)   # top-right tip → top-left tip
    N = 26
    outer, inner = [], []
    for i in range(N + 1):
        a = a0 + (a1 - a0) * i / N
        outer.append((cx + math.cos(a) * rw, hcy - math.sin(a) * rh))
        inner.append((cx + math.cos(a) * (rw - band), hcy - math.sin(a) * (rh - band)))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in outer + inner[::-1]])
    # Flared calk nubs at the two top ends so the ends read as a shoe's heels.
    for a in (a0, a1):
        mx = cx + math.cos(a) * (rw - band / 2)
        my = hcy - math.sin(a) * (rh - band / 2)
        pygame.draw.circle(surf, col, (int(mx), int(my)), max(3, int(band * 0.62)))
    # Nail holes punched round the shoe (recessed).
    for deg in (35, -20, -90, 200, 145):
        a = math.radians(deg)
        nx = cx + math.cos(a) * (rw - band * 0.5)
        ny = hcy - math.sin(a) * (rh - band * 0.5)
        pygame.draw.circle(surf, ai._GLYPH_SH, (int(nx), int(ny)), max(2, int(r * 0.06)))
    # Triple matched pips in a row beneath the shoe — the reel win. Small solid
    # diamonds so they never read as loose coins.
    py = cy + int(r * 0.82)
    pr = int(r * 0.18)
    for dx in (-0.46, 0.0, 0.46):
        px = cx + dx * r
        pygame.draw.polygon(surf, col, [
            (int(px), int(py - pr)), (int(px + pr * 0.8), int(py)),
            (int(px), int(py + pr)), (int(px - pr * 0.8), int(py)),
        ])


# ── 9. palindrome — a mirror-symmetric twin-arrow motif ─────────────────────
def _glyph_palindrome(surf, cx, cy, r, col):
    # The emblem IS the metaphor: perfectly left-right symmetric. Two bold
    # arrowheads face inward to a central mirror axis, each with a tail bar and an
    # outer echo-chevron — a shape that reads the same reflected, like a
    # palindromic score.
    # Central mirror axis — a dashed vertical line.
    dash = int(r * 0.18)
    yy = int(cy - r * 0.82)
    while yy < cy + r * 0.82:
        pygame.draw.line(surf, col, (cx, yy), (cx, min(int(cy + r * 0.82), yy + dash)),
                         max(2, int(r * 0.09)))
        yy += dash * 2
    for sgn in (-1, 1):
        # Inner arrowhead pointing toward the axis.
        tipx = cx + sgn * int(r * 0.14)
        basex = cx + sgn * int(r * 0.52)
        pygame.draw.polygon(surf, col, [
            (tipx, cy),
            (basex, cy - int(r * 0.40)),
            (basex, cy + int(r * 0.40)),
        ])
        # Tail bar behind the head.
        pygame.draw.rect(surf, col, (min(basex, basex + sgn * int(r * 0.36)),
                                     cy - int(r * 0.14),
                                     int(r * 0.36), int(r * 0.28)),
                         border_radius=max(1, int(r * 0.05)))
        # Outer echo-chevron, mirrored, so the symmetry reads at a glance.
        ox = cx + sgn * int(r * 0.96)
        cw = max(3, int(r * 0.12))
        pygame.draw.lines(surf, col, False, [
            (ox - sgn * int(r * 0.20), cy - int(r * 0.34)),
            (ox, cy),
            (ox - sgn * int(r * 0.20), cy + int(r * 0.34)),
        ], cw)


GLYPHS = {
    "overloaded": _glyph_overloaded,
    "bullet_time": _glyph_bullet_time,
    "ghost_rider": _glyph_ghost_rider,
    "regifted": _glyph_regifted,
    "read_fine_print": _glyph_read_fine_print,
    "morbid_curiosity": _glyph_morbid_curiosity,
    "are_you_still_there": _glyph_are_you_still_there,
    "lucky_sevens": _glyph_lucky_sevens,
    "palindrome": _glyph_palindrome,
}
