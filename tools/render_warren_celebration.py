"""Look-dev renderer for the warren-demo ROLL-RESULT celebration popup.

The clown's floating die settles on a roll N (the number of STAFFS the route
will carry) and a festive popup announces it. The current ship look is a
low-res 12-wedge two-colour prize wheel (orange/pink) behind a system-font
number + "PILLARS" — a fun "prize-reveal" read the user wants KEPT but elevated
to high-res and themed to the jester clown + his Carousel-Barker staff.

This sheet anchors that comparison: cell 1 ports the CURRENT wheel faithfully
as the baseline, and cells 2-6 are five distinct high-res, on-theme variants in
the staff's Plum & Lime palette. Every cell keeps the foundation read — a
radiating festive burst/wheel behind a DOMINANT rolled number + a theme label
("STAFFS") — and each is drawn at the true ~264 design-px popup size on the
in-game day sky, with a true-1x inset per cell so real on-screen legibility is
judged honestly (no flattering zoom-only cells).

Run (headless):
    python tools/render_warren_celebration.py --warren-cele
Writes docs/dice_results/warren_roll/round_1.png.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import hud  # vendored bold TTF + cache
from game.draw import _shade_c
from game.pillar_staff import (
    PLUM, PLUM_DK, LIME, LIME_DK, GOLD, GOLD_HI, GOLD_DK, CREAM,
    _mini_clown_face, _marotte_ruff, _shaft_twist, _ferrule, _pommel_finial,
)
from tools.render_dice_celebration import (
    sky_tile, _num_block, _label_plate, _star,
    SKY_TOP, SKY_BOT, W,
)

ROLL = 17  # representative roll, held constant across every cell

# A richer two-colour jester wheel lineage: plum + lime alternating wedges keep
# the baseline's "two-colour prize wheel" read but in the staff's world palette.
WHEEL_A = PLUM
WHEEL_B = LIME


def _jingle_bell(canvas, cx, cy, r, ss, col=GOLD):
    """A small gold jingle bell: a lit dome with a dark band + slit, a hanging
    clapper dot, and a top-left specular pip — the staff's signature jingle, used
    to ring the festive frames so the popup ties to the Carousel-Barker bells."""
    pygame.draw.circle(canvas, _shade_c(col, -55), (int(cx), int(cy)), int(r))
    pygame.draw.circle(canvas, col, (int(cx), int(cy)), int(r - ss))
    # Lower band + vertical slit so it reads as a bell, not a coin.
    pygame.draw.arc(canvas, _shade_c(col, -70),
                    (int(cx - r), int(cy - r), int(r * 2), int(r * 2)),
                    math.pi * 1.08, math.pi * 1.92, max(1, int(1.6 * ss)))
    pygame.draw.line(canvas, _shade_c(col, -70), (int(cx), int(cy + r * 0.2)),
                     (int(cx), int(cy + r * 0.78)), max(1, int(1.4 * ss)))
    pygame.draw.circle(canvas, _shade_c(col, -45), (int(cx), int(cy + r * 0.92)),
                       max(2, int(r * 0.32)))
    pygame.draw.circle(canvas, GOLD_HI, (int(cx - r * 0.34), int(cy - r * 0.34)),
                       max(1, int(r * 0.26)))


def _wheel(canvas, c, R, ss, wedges, col_a, col_b, *, spin=0.55, rim=None,
           rim_w=6, hub=None, cy=None):
    """A radiating prize-wheel rosette: alternating two-colour wedges with hard
    keylines, an optional crisp gold rim ring, and an optional hub disc. Normal-
    blended so it stays a festive colour over the pale sky (additive blows white).
    Keeps the baseline's spinning-wheel lineage, elevated and recoloured.
    `cy` overrides the vertical centre (default = `c`) so the wheel can sit low
    while a tall bauble crowns the top."""
    cy = c if cy is None else cy
    step = math.tau / wedges
    for i in range(wedges):
        a0 = spin + i * step
        a1 = a0 + step
        col = col_a if i % 2 == 0 else col_b
        pygame.draw.polygon(canvas, col, [
            (c, cy),
            (c + math.cos(a0) * R, cy + math.sin(a0) * R),
            (c + math.cos(a1) * R, cy + math.sin(a1) * R)])
    # Hairline wedge keylines so the high-res wheel reads crisp, not muddy.
    for i in range(wedges):
        a = spin + i * step
        pygame.draw.line(canvas, _shade_c(PLUM_DK, -10), (c, cy),
                         (c + math.cos(a) * R, cy + math.sin(a) * R), max(1, ss))
    if rim is not None:
        pygame.draw.circle(canvas, _shade_c(rim, -45), (c, cy), R, max(2, int((rim_w + 2) * ss)))
        pygame.draw.circle(canvas, rim, (c, cy), R, max(2, int(rim_w * ss)))
        pygame.draw.circle(canvas, GOLD_HI, (c, cy), R - int(rim_w * 0.5 * ss),
                           max(1, ss))
    if hub is not None:
        pygame.draw.circle(canvas, _shade_c(hub, -45), (c, cy), int(R * 0.30))
        pygame.draw.circle(canvas, hub, (c, cy), int(R * 0.30 - ss))


# ── Cell 1: the CURRENT ship wheel, ported faithfully (the foundation) ────────
def var_baseline(roll, ss):
    """The current `_draw_celebration` look, ported 1:1 as the anchor: a 12-wedge
    orange/pink prize wheel (normal-blended, slightly spun), 14 confetti dots
    spraying outward, a system-font big number with a 4-way warm outline, and a
    "PILLARS" label. Deliberately low-fidelity — it is the baseline the five
    elevated variants are measured against."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    R = int(64 * ss)
    rays = 12
    rose_cols = [(255, 184, 72), (255, 138, 150)]
    spin = 0.55
    step = math.tau / rays
    for i in range(rays):
        a0 = spin + i * step
        a1 = a0 + step
        col = rose_cols[i % 2] + (82,)
        pygame.draw.polygon(canvas, col, [
            (c, c),
            (c + math.cos(a0) * R, c + math.sin(a0) * R),
            (c + math.cos(a1) * R, c + math.sin(a1) * R)])

    conf = [(255, 210, 90), (255, 120, 150), (120, 200, 255), (170, 255, 150)]
    for i in range(14):
        a = (i / 14) * math.tau
        dist = R * 0.7 + 40 * ss + (i % 3) * 6 * ss
        px = int(c + math.cos(a) * dist)
        py = int(c + math.sin(a) * dist * 0.82)
        col = conf[i % 4] + (220,)
        dot = pygame.Surface((8 * ss, 8 * ss), pygame.SRCALPHA)
        pygame.draw.circle(dot, col, (4 * ss, 4 * ss), 3 * ss)
        canvas.blit(dot, (px - 4 * ss, py - 4 * ss))

    # System bold font + 4-way warm outline, matching the ship code exactly.
    nf = pygame.font.SysFont(None, int(92 * ss), bold=True)
    num = nf.render(str(roll), True, (255, 232, 158))
    out = nf.render(str(roll), True, (120, 70, 20))
    for ox, oy in ((-2 * ss, 0), (2 * ss, 0), (0, -2 * ss), (0, 2 * ss)):
        canvas.blit(out, out.get_rect(center=(c + ox, c + oy)))
    nb = num.get_rect(center=(c, c))
    canvas.blit(num, nb)

    lf = pygame.font.SysFont(None, int(30 * ss), bold=True)
    label = lf.render("PILLARS", True, (255, 244, 210))
    canvas.blit(label, label.get_rect(center=(c, nb.bottom + 12 * ss)))
    return canvas, D


# ── Cell 2: polished jester prize-wheel + crisp gold rim + jingle bells ───────
def var_jester_wheel(roll, ss):
    """The baseline wheel, elevated: a high-res plum/lime two-colour prize wheel
    with a crisp double-stroke gold rim, a ring of gold jingle bells riding the
    rim (the Carousel-Barker jingle), a cream number disc hub so the hero number
    sits on cream not a wedge seam, and the number + "STAFFS" plate on top. The
    direct, faithful upgrade of the foundation."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    R = int(HD * 0.40)
    _wheel(canvas, c, R, ss, 12, WHEEL_A, WHEEL_B, spin=0.42,
           rim=GOLD, rim_w=7)
    # A ring of jingle bells seated just OUTSIDE the gold rim.
    nb_bells = 8
    for i in range(nb_bells):
        a = i * math.tau / nb_bells - math.pi / 2
        bx = c + math.cos(a) * (R + int(9 * ss))
        by = c + math.sin(a) * (R + int(9 * ss))
        _jingle_bell(canvas, bx, by, int(7 * ss), ss)
    # Cream hub disc so the number reads on cream, ringed in plum + gold.
    hub_r = int(R * 0.56)
    pygame.draw.circle(canvas, PLUM, (c, c), hub_r + int(4 * ss))
    pygame.draw.circle(canvas, GOLD, (c, c), hub_r + int(4 * ss), max(2, int(2 * ss)))
    pygame.draw.circle(canvas, CREAM, (c, c), hub_r)
    pygame.draw.circle(canvas, PLUM, (c, c), hub_r, max(2, int(2 * ss)))

    _num_block(canvas, c, c - int(8 * ss), roll, ss, size=86,
               num_col=PLUM, edge_col=CREAM, edge_w=4)
    _label_plate(canvas, c, c + int(hub_r * 0.70), "STAFFS", ss, PLUM, CREAM,
                 PLUM_DK, size=22)
    return canvas, D


# ── Cell 3: carousel-barker barber-twist framed sign ──────────────────────────
def var_barber_sign(roll, ss):
    """The staff's barber-twist spiral becomes the FRAME: two vertical barber-pole
    shafts down the sides and two short horizontal ones top/bottom box a cream
    sign, with gold-jewel ferrule corners and a clown-bell finial topper. The
    spinning-wheel energy is re-read as the carousel barker's spiralling pole."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    half = int(HD * 0.34)
    hw = int(8 * ss)
    # Cream sign field behind the twist frame.
    pad = int(hw * 1.3)
    field = pygame.Rect(c - half + pad, c - half + pad,
                        (half - pad) * 2, (half - pad) * 2)
    pygame.draw.rect(canvas, _shade_c(CREAM, -16), field, border_radius=int(10 * ss))
    pygame.draw.rect(canvas, CREAM, field.inflate(-2 * ss, -2 * ss),
                     border_radius=int(10 * ss))

    # Four barber-twist rails framing the sign (the staff's _shaft_twist).
    _shaft_twist(canvas, c - half, c - half, c + half, hw, ss, PLUM, GOLD, PLUM_DK)
    _shaft_twist(canvas, c + half, c - half, c + half, hw, ss, PLUM, GOLD, PLUM_DK)
    # Horizontal rails: rotate a twist strip so the spiral wraps all four sides.
    for yy in (c - half, c + half):
        strip = pygame.Surface((HD, HD), pygame.SRCALPHA)
        _shaft_twist(strip, c, c - half, c + half, hw, ss, PLUM, GOLD, PLUM_DK)
        strip = pygame.transform.rotate(strip, 90)
        off = (strip.get_width() - HD) // 2
        canvas.blit(strip, (-off, yy - c - off))

    # Gold jewelled ferrule beads clamp each corner so the frame reads finished.
    for sx in (-1, 1):
        for sy in (-1, 1):
            jx, jy = c + sx * half, c + sy * half
            pygame.draw.circle(canvas, _shade_c(GOLD, -45), (jx, jy), int(11 * ss))
            pygame.draw.circle(canvas, GOLD, (jx, jy), int(9 * ss))
            pygame.draw.circle(canvas, PLUM, (jx, jy), int(4 * ss))
            pygame.draw.circle(canvas, GOLD_HI, (jx - int(3 * ss), jy - int(3 * ss)),
                               int(2.4 * ss))
    # Clown-bell finial topper crowning the sign.
    _pommel_finial(canvas, c, c - half - int(8 * ss), hw, ss, GOLD, kind="bell")
    _jingle_bell(canvas, c, c - half - int(20 * ss), int(8 * ss), ss)

    _num_block(canvas, c, c - int(8 * ss), roll, ss, size=88,
               num_col=PLUM, edge_col=GOLD, edge_w=4)
    _label_plate(canvas, c, c + int(half * 0.62), "STAFFS", ss, PLUM, CREAM,
                 PLUM_DK, size=21)
    return canvas, D


# ── Cell 4: marotte-flanked plaque — two mini staffs frame the number ─────────
def var_marotte_plaque(roll, ss):
    """A rounded plum plaque flanked by two mini Carousel-Barker marottes (the
    grinning clown head + belled ruff atop a short barber-twist shaft), so the
    rolled number is literally announced by the clown's own scepters. A burst of
    plum/lime/gold flecks fans out behind the plaque to keep the prize-reveal
    pop, and "STAFFS" rides a cream plate below."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Festive fleck fan behind everything (the reveal burst, held off-centre).
    pal = [GOLD, LIME, CREAM, PLUM]
    for i in range(20):
        a = i * math.tau / 20 + 0.3
        dist = HD * 0.30 + (i % 4) * 8 * ss
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist * 0.92
        col = pal[i % len(pal)]
        if i % 2 == 0:
            sz = (5 + i % 3 * 2) * ss
            d = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.polygon(d, col + (235,),
                                [(sz // 2, 0), (sz, sz // 2), (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 47) % 360)
            canvas.blit(d, d.get_rect(center=(int(px), int(py))))
        else:
            pygame.draw.circle(canvas, col, (int(px), int(py)), 3 * ss)

    # Two mini Carousel-Barker marottes flank the plaque, heads turned inward.
    def marotte(mx, lean):
        hr = int(20 * ss)
        hy = c - int(HD * 0.18)
        shaft_top = hy + hr
        shaft_bot = c + int(HD * 0.30)
        hwid = int(6 * ss)
        _shaft_twist(canvas, mx, shaft_top, shaft_bot, hwid, ss, PLUM, GOLD, PLUM_DK)
        _ferrule(canvas, mx, (shaft_top + shaft_bot) // 2, hwid, ss, GOLD, h=7,
                 jewel=PLUM)
        _pommel_finial(canvas, mx, shaft_bot, hwid, ss, GOLD, kind="ball", gem=PLUM)
        _marotte_ruff(canvas, mx, hy + hr - int(2 * ss), int(hr * 1.05), ss, LIME,
                      lobes=9, fringe=GOLD)
        _mini_clown_face(canvas, mx, hy, hr, ss, expr="grin", look=lean * 2.4 * ss)
    marotte(c - int(HD * 0.36), 1)
    marotte(c + int(HD * 0.36), -1)

    # The central plaque the marottes present.
    pw, ph = int(HD * 0.42), int(HD * 0.40)
    plaque = pygame.Rect(c - pw // 2, c - ph // 2, pw, ph)
    pygame.draw.rect(canvas, GOLD, plaque.inflate(8 * ss, 8 * ss),
                     border_radius=int(16 * ss))
    pygame.draw.rect(canvas, PLUM_DK, plaque.inflate(2 * ss, 2 * ss),
                     border_radius=int(14 * ss))
    pygame.draw.rect(canvas, PLUM, plaque, border_radius=int(13 * ss))
    pygame.draw.rect(canvas, GOLD, plaque.inflate(-8 * ss, -8 * ss),
                     width=max(1, 2 * ss), border_radius=int(10 * ss))

    _num_block(canvas, c, c - int(6 * ss), roll, ss, size=84,
               num_col=CREAM, edge_col=PLUM_DK, edge_w=4)
    _label_plate(canvas, c, plaque.bottom + int(8 * ss), "STAFFS", ss, PLUM,
                 CREAM, PLUM_DK, size=21)
    return canvas, D


# ── Cell 5: jester-cap / bell banderole ribbon banner ─────────────────────────
def var_cap_banderole(roll, ss):
    """A ribbon banner in the staff palette crowned by a three-point jester cap,
    each point tipped with a gold jingle bell and the band split into alternating
    plum/lime triangle pennants (the cap's harlequin read). Lime banner body, big
    cream number, "STAFFS" on a plum plate, flared plum ribbon tails — the
    festive ribbon lineage re-themed to the clown's cap + bells."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    bw, bh = int(HD * 0.70), int(HD * 0.42)
    bx, by = c - bw // 2, c - bh // 2 + int(HD * 0.06)

    # Flared plum ribbon tails behind the body.
    tail_w = int(HD * 0.17)
    for sgn in (-1, 1):
        x0 = c + sgn * (bw // 2 - 4 * ss)
        pts = [
            (x0, by + int(bh * 0.20)),
            (x0 + sgn * tail_w, by + int(bh * 0.05)),
            (x0 + sgn * tail_w * 0.7, by + bh // 2),
            (x0 + sgn * tail_w, by + int(bh * 0.95)),
            (x0, by + int(bh * 0.80)),
        ]
        pygame.draw.polygon(canvas, PLUM_DK, [(int(p[0]), int(p[1])) for p in pts])

    # Three-point jester cap crowning the banner, points tipped with bells.
    cap_base_y = by - int(2 * ss)
    n_pts = 3
    seg = bw / n_pts
    for k in range(n_pts):
        bx0 = bx + k * seg
        bx1 = bx + (k + 1) * seg
        apex_x = (bx0 + bx1) / 2
        apex_y = cap_base_y - int(bh * (0.62 if k == 1 else 0.50))
        col = PLUM if k % 2 == 0 else LIME
        pygame.draw.polygon(canvas, _shade_c(col, -40),
                            [(bx0, cap_base_y), (bx1, cap_base_y), (apex_x, apex_y)])
        pygame.draw.polygon(canvas, col,
                            [(bx0 + ss, cap_base_y), (bx1 - ss, cap_base_y),
                             (apex_x, apex_y + ss)])
        _jingle_bell(canvas, apex_x, apex_y - int(2 * ss), int(6 * ss), ss)

    # Lime banner body with rolled plum frame + soft gold keyline + top gloss.
    rad = int(18 * ss)
    halo = int(7 * ss)
    pygame.draw.rect(canvas, PLUM, (bx - halo, by - halo, bw + 2 * halo, bh + 2 * halo),
                     border_radius=rad + halo)
    pygame.draw.rect(canvas, LIME, (bx, by, bw, bh), border_radius=rad)
    pygame.draw.rect(canvas, GOLD, (bx + 6 * ss, by + 6 * ss, bw - 12 * ss, bh - 12 * ss),
                     width=2 * ss, border_radius=rad - 4 * ss)
    gloss = pygame.Surface((bw - 12 * ss, bh // 3), pygame.SRCALPHA)
    gloss.fill((255, 255, 255, 42))
    canvas.blit(gloss, (bx + 6 * ss, by + 6 * ss))

    _num_block(canvas, c, by + bh // 2 - int(6 * ss), roll, ss, size=88,
               num_col=CREAM, edge_col=PLUM, edge_w=5)
    _label_plate(canvas, c, by + bh + int(2 * ss), "STAFFS", ss, PLUM, CREAM,
                 PLUM_DK, size=22)
    return canvas, D


# ── Cell 6: radiant bell-burst sunburst — gold rays + ring of jingle bells ─────
def var_bell_sunburst(roll, ss):
    """A radiant gold sunburst — long/short alternating gold rays fanning out from
    the centre — ringed by jingle bells, with a plum cream-cored medallion holding
    the hero number. The most explosive 'reveal' read: the wheel re-imagined as a
    bell-fringed sunburst so the prize-pop energy peaks while staying on-theme."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Two-tone radiating sunburst (long gold + short lime spokes between).
    n = 16
    for i in range(n):
        a0 = i * math.tau / n - math.pi / 2
        long_ray = i % 2 == 0
        rr = HD * (0.46 if long_ray else 0.37)
        col = GOLD if long_ray else LIME
        half_w = (0.10 if long_ray else 0.07)
        p_in = (c + math.cos(a0) * HD * 0.16, c + math.sin(a0) * HD * 0.16)
        p_l = (c + math.cos(a0 - half_w) * rr, c + math.sin(a0 - half_w) * rr)
        p_r = (c + math.cos(a0 + half_w) * rr, c + math.sin(a0 + half_w) * rr)
        pygame.draw.polygon(canvas, _shade_c(col, -35),
                            [(int(p_in[0]), int(p_in[1])),
                             (int(p_l[0]), int(p_l[1])), (int(p_r[0]), int(p_r[1]))])
        pygame.draw.polygon(canvas, col,
                            [(int(c), int(c)),
                             (int(p_l[0]), int(p_l[1])), (int(p_r[0]), int(p_r[1]))], 0)

    # Ring of jingle bells at the long-ray tips.
    for i in range(0, n, 2):
        a0 = i * math.tau / n - math.pi / 2
        bx = c + math.cos(a0) * HD * 0.44
        by = c + math.sin(a0) * HD * 0.44
        _jingle_bell(canvas, bx, by, int(8 * ss), ss)

    # Plum medallion with a cream core so the number sits clear of the rays.
    med_r = int(HD * 0.24)
    pygame.draw.circle(canvas, GOLD, (c, c), med_r + int(5 * ss))
    pygame.draw.circle(canvas, _shade_c(GOLD, -45), (c, c), med_r + int(5 * ss),
                       max(2, int(2 * ss)))
    pygame.draw.circle(canvas, PLUM, (c, c), med_r)
    pygame.draw.circle(canvas, CREAM, (c, c), int(med_r * 0.78))
    pygame.draw.circle(canvas, PLUM, (c, c), int(med_r * 0.78), max(2, int(2 * ss)))

    _num_block(canvas, c, c - int(8 * ss), roll, ss, size=84,
               num_col=PLUM, edge_col=CREAM, edge_w=4)
    _label_plate(canvas, c, c + int(med_r * 0.70), "STAFFS", ss, PLUM, CREAM,
                 PLUM_DK, size=21)
    return canvas, D


VARIANTS = [
    ("1  Original (baseline)", "current 12-wedge orange/pink wheel + PILLARS",
     var_baseline),
    ("2  Jester prize-wheel", "plum/lime wheel, gold rim + jingle-bell ring",
     var_jester_wheel),
    ("3  Barber-twist sign", "staff barber-spiral as the framed sign",
     var_barber_sign),
    ("4  Marotte plaque", "two mini Carousel-Barker staffs flank the number",
     var_marotte_plaque),
    ("5  Cap-bell banderole", "ribbon banner under a belled jester cap",
     var_cap_banderole),
    ("6  Bell-burst sunburst", "gold rays + ring of jingle bells",
     var_bell_sunburst),
]


# ── Round 2: art-director polish pass ─────────────────────────────────────────
# Cell 3 (Barber-twist sign) is the chosen WINNER, cell 5 (Cap-bell banderole)
# the alternate; the rest are tuned so the rolled NUMBER stays the dominant hero
# and reads on value at the true-1x inset, never leaning on the "STAFFS" label.

def _gold_stud(canvas, cx, cy, r, ss, col=GOLD):
    """A solid domed gold rivet/stud: a dark seat, a lit dome, a top-left pip.
    Replaces the tiny jingle bells that turned to mud at 1x — a stud is a single
    bold disc that survives the downscale where a belled silhouette dissolves."""
    pygame.draw.circle(canvas, _shade_c(col, -55), (int(cx), int(cy)), int(r))
    pygame.draw.circle(canvas, col, (int(cx), int(cy)), int(r - ss))
    pygame.draw.circle(canvas, GOLD_HI, (int(cx - r * 0.34), int(cy - r * 0.34)),
                       max(1, int(r * 0.3)))


def _shaft_twist_wide(surf, cx, top_y, bot_y, hw, ss, col_a, col_b, lo, *,
                      pitch=8.0):
    """A widened-pitch barber-pole twist for the winning frame: the spiral pitch
    is opened up ~15% over the staff's stock `_shaft_twist` so the candy stripe
    stays a clean read at the 1x inset instead of strobing. Same dark-cored body,
    lit rail and keyline so it still matches the Carousel-Barker pole."""
    from game.pillar_staff import _shaft_outline
    left, right = _shaft_outline(surf, cx, top_y, bot_y, hw, ss, lo)
    clip = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    stripe = max(4, int(pitch * ss))
    n = int((bot_y - top_y) / stripe) + 4
    # Same 4-band cycle (plum x3, gold x1) as the stock pole so plum dominates
    # ~3:1; only the band height grows, opening the spiral.
    for i in range(-2, n):
        y0 = top_y + i * stripe
        c = col_b if i % 4 == 3 else col_a
        quad = [(cx - hw, y0), (cx + hw, y0 - hw * 1.5),
                (cx + hw, y0 - hw * 1.5 + stripe), (cx - hw, y0 + stripe)]
        pygame.draw.polygon(clip, c, [(int(p[0]), int(p[1])) for p in quad])
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    body = left + list(reversed(right))
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(int(p[0]), int(p[1])) for p in body])
    clip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(clip, (0, 0))
    pygame.draw.line(surf, _shade_c(col_a, 50), (int(cx - hw * 0.45), int(top_y)),
                     (int(cx - hw * 0.45), int(bot_y)), max(1, int(1.4 * ss)))
    pygame.draw.polygon(surf, _shade_c(lo, -45),
                        [(int(p[0]), int(p[1])) for p in body], max(2, int(2.0 * ss)))


# ── Cell 2 (R2): 8-wedge wheel, big number hub, gold studs (no mud bells) ─────
def var_jester_wheel_r2(roll, ss):
    """8 wedges instead of 12 so the wheel can't shimmer at 1x; the rim's belled
    ring is swapped for four bold gold studs at the cardinal points (small bells
    turned to mud); the cream hub + hero number is pushed larger so the number
    owns the centre."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    R = int(HD * 0.40)
    _wheel(canvas, c, R, ss, 8, WHEEL_A, WHEEL_B, spin=0.42, rim=GOLD, rim_w=7)
    # Four larger gold studs at the cardinals read where a bell ring muddied.
    for i in range(4):
        a = i * math.tau / 4 - math.pi / 2
        sx = c + math.cos(a) * (R + int(2 * ss))
        sy = c + math.sin(a) * (R + int(2 * ss))
        _gold_stud(canvas, sx, sy, int(11 * ss), ss)
    # Cream hub disc grown so the bigger number sits on cream, ringed plum + gold.
    hub_r = int(R * 0.62)
    pygame.draw.circle(canvas, PLUM, (c, c), hub_r + int(4 * ss))
    pygame.draw.circle(canvas, GOLD, (c, c), hub_r + int(4 * ss), max(2, int(2 * ss)))
    pygame.draw.circle(canvas, CREAM, (c, c), hub_r)
    pygame.draw.circle(canvas, PLUM, (c, c), hub_r, max(2, int(2 * ss)))

    _num_block(canvas, c, c - int(8 * ss), roll, ss, size=96,
               num_col=PLUM, edge_col=CREAM, edge_w=4)
    _label_plate(canvas, c, c + int(hub_r * 0.74), "STAFFS", ss, PLUM, CREAM,
                 PLUM_DK, size=22)
    return canvas, D


# ── Cell 3 (R2, WINNER): widened barber twist, lighter shadow, nudged number ──
def var_barber_sign_r2(roll, ss):
    """The winning framed sign, polished: the barber spiral pitch is widened ~15%
    so it stays a clean candy-twist (no strobe) at 1x; the number's drop shadow is
    lightened ~20% so the digits stay crisp; the number is nudged DOWN ~4px so its
    optical centre accounts for the "STAFFS" lozenge below. Frame, ferrules, bell
    topper, cream field and dominant number are otherwise untouched."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    half = int(HD * 0.34)
    hw = int(8 * ss)
    pad = int(hw * 1.3)
    field = pygame.Rect(c - half + pad, c - half + pad,
                        (half - pad) * 2, (half - pad) * 2)
    pygame.draw.rect(canvas, _shade_c(CREAM, -16), field, border_radius=int(10 * ss))
    pygame.draw.rect(canvas, CREAM, field.inflate(-2 * ss, -2 * ss),
                     border_radius=int(10 * ss))

    # Four widened-pitch barber-twist rails framing the sign.
    _shaft_twist_wide(canvas, c - half, c - half, c + half, hw, ss, PLUM, GOLD, PLUM_DK)
    _shaft_twist_wide(canvas, c + half, c - half, c + half, hw, ss, PLUM, GOLD, PLUM_DK)
    for yy in (c - half, c + half):
        strip = pygame.Surface((HD, HD), pygame.SRCALPHA)
        _shaft_twist_wide(strip, c, c - half, c + half, hw, ss, PLUM, GOLD, PLUM_DK)
        strip = pygame.transform.rotate(strip, 90)
        off = (strip.get_width() - HD) // 2
        canvas.blit(strip, (-off, yy - c - off))

    for sx in (-1, 1):
        for sy in (-1, 1):
            jx, jy = c + sx * half, c + sy * half
            pygame.draw.circle(canvas, _shade_c(GOLD, -45), (jx, jy), int(11 * ss))
            pygame.draw.circle(canvas, GOLD, (jx, jy), int(9 * ss))
            pygame.draw.circle(canvas, PLUM, (jx, jy), int(4 * ss))
            pygame.draw.circle(canvas, GOLD_HI, (jx - int(3 * ss), jy - int(3 * ss)),
                               int(2.4 * ss))
    _pommel_finial(canvas, c, c - half - int(8 * ss), hw, ss, GOLD, kind="bell")
    _jingle_bell(canvas, c, c - half - int(20 * ss), int(8 * ss), ss)

    # Number nudged down ~4px + shadow lightened (~88 vs the stock 110 alpha).
    _num_block(canvas, c, c - int(4 * ss), roll, ss, size=88,
               num_col=PLUM, edge_col=GOLD, shadow_a=88, edge_w=4)
    _label_plate(canvas, c, c + int(half * 0.62), "STAFFS", ss, PLUM, CREAM,
                 PLUM_DK, size=21)
    return canvas, D


# ── Cell 4 (R2): squarer plaque, bigger number, smaller marottes low-flanking ──
def var_marotte_plaque_r2(roll, ss):
    """The plaque is squared up (less tall/narrow) so the hero number can grow
    ~20%; the two marottes are shrunk ~30% and dropped to flank only the LOWER
    third, so they stop crowding the number while keeping their charming faces."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    pal = [GOLD, LIME, CREAM, PLUM]
    for i in range(20):
        a = i * math.tau / 20 + 0.3
        dist = HD * 0.30 + (i % 4) * 8 * ss
        px = c + math.cos(a) * dist
        py = c + math.sin(a) * dist * 0.92
        col = pal[i % len(pal)]
        if i % 2 == 0:
            sz = (5 + i % 3 * 2) * ss
            d = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.polygon(d, col + (235,),
                                [(sz // 2, 0), (sz, sz // 2), (sz // 2, sz), (0, sz // 2)])
            d = pygame.transform.rotate(d, (i * 47) % 360)
            canvas.blit(d, d.get_rect(center=(int(px), int(py))))
        else:
            pygame.draw.circle(canvas, col, (int(px), int(py)), 3 * ss)

    # Smaller marottes dropped to the LOWER third so they flank, never crowd.
    def marotte(mx, lean):
        hr = int(14 * ss)
        hy = c + int(HD * 0.16)
        shaft_top = hy + hr
        shaft_bot = c + int(HD * 0.36)
        hwid = int(5 * ss)
        _shaft_twist(canvas, mx, shaft_top, shaft_bot, hwid, ss, PLUM, GOLD, PLUM_DK)
        _pommel_finial(canvas, mx, shaft_bot, hwid, ss, GOLD, kind="ball", gem=PLUM)
        _marotte_ruff(canvas, mx, hy + hr - int(2 * ss), int(hr * 1.05), ss, LIME,
                      lobes=9, fringe=GOLD)
        _mini_clown_face(canvas, mx, hy, hr, ss, expr="grin", look=lean * 2.0 * ss)
    marotte(c - int(HD * 0.34), 1)
    marotte(c + int(HD * 0.34), -1)

    # Squared-up plaque (near 1:1) so the number has room to grow.
    pw, ph = int(HD * 0.50), int(HD * 0.44)
    plaque = pygame.Rect(c - pw // 2, c - ph // 2, pw, ph)
    pygame.draw.rect(canvas, GOLD, plaque.inflate(8 * ss, 8 * ss),
                     border_radius=int(16 * ss))
    pygame.draw.rect(canvas, PLUM_DK, plaque.inflate(2 * ss, 2 * ss),
                     border_radius=int(14 * ss))
    pygame.draw.rect(canvas, PLUM, plaque, border_radius=int(13 * ss))
    pygame.draw.rect(canvas, GOLD, plaque.inflate(-8 * ss, -8 * ss),
                     width=max(1, 2 * ss), border_radius=int(10 * ss))

    _num_block(canvas, c, c - int(8 * ss), roll, ss, size=100,
               num_col=CREAM, edge_col=PLUM_DK, edge_w=4)
    _label_plate(canvas, c, plaque.bottom - int(2 * ss), "STAFFS", ss, PLUM,
                 CREAM, PLUM_DK, size=21)
    return canvas, D


# ── Cell 5 (R2, ALTERNATE): keylined cap points + enlarged side bells ─────────
def var_cap_banderole_r2(roll, ss):
    """The alternate banner, hardened for dark/night sky: a thin cream/gold
    keyline rings each dark-plum cap point so the crown silhouette survives on a
    near-black sky, and the two side bells are enlarged ~25% so they're not the
    only mud detail. Cap, lime banner and number scale are otherwise kept."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    bw, bh = int(HD * 0.70), int(HD * 0.42)
    bx, by = c - bw // 2, c - bh // 2 + int(HD * 0.06)

    tail_w = int(HD * 0.17)
    for sgn in (-1, 1):
        x0 = c + sgn * (bw // 2 - 4 * ss)
        pts = [
            (x0, by + int(bh * 0.20)),
            (x0 + sgn * tail_w, by + int(bh * 0.05)),
            (x0 + sgn * tail_w * 0.7, by + bh // 2),
            (x0 + sgn * tail_w, by + int(bh * 0.95)),
            (x0, by + int(bh * 0.80)),
        ]
        pygame.draw.polygon(canvas, PLUM_DK, [(int(p[0]), int(p[1])) for p in pts])

    cap_base_y = by - int(2 * ss)
    n_pts = 3
    seg = bw / n_pts
    for k in range(n_pts):
        bx0 = bx + k * seg
        bx1 = bx + (k + 1) * seg
        apex_x = (bx0 + bx1) / 2
        apex_y = cap_base_y - int(bh * (0.62 if k == 1 else 0.50))
        col = PLUM if k % 2 == 0 else LIME
        pygame.draw.polygon(canvas, _shade_c(col, -40),
                            [(bx0, cap_base_y), (bx1, cap_base_y), (apex_x, apex_y)])
        pygame.draw.polygon(canvas, col,
                            [(bx0 + ss, cap_base_y), (bx1 - ss, cap_base_y),
                             (apex_x, apex_y + ss)])
        # Thin cream/gold keyline so the dark plum points hold their crown
        # silhouette against a near-black night sky (the plum vanished before).
        key = CREAM if k % 2 == 0 else GOLD
        pygame.draw.lines(canvas, key, False,
                          [(int(bx0), int(cap_base_y)), (int(apex_x), int(apex_y)),
                           (int(bx1), int(cap_base_y))], max(1, int(1.6 * ss)))
        # Larger bells (~25% up) so the cap-tip jingle is a real detail at 1x.
        _jingle_bell(canvas, apex_x, apex_y - int(2 * ss), int(7.5 * ss), ss)

    rad = int(18 * ss)
    halo = int(7 * ss)
    pygame.draw.rect(canvas, PLUM, (bx - halo, by - halo, bw + 2 * halo, bh + 2 * halo),
                     border_radius=rad + halo)
    pygame.draw.rect(canvas, LIME, (bx, by, bw, bh), border_radius=rad)
    pygame.draw.rect(canvas, GOLD, (bx + 6 * ss, by + 6 * ss, bw - 12 * ss, bh - 12 * ss),
                     width=2 * ss, border_radius=rad - 4 * ss)
    gloss = pygame.Surface((bw - 12 * ss, bh // 3), pygame.SRCALPHA)
    gloss.fill((255, 255, 255, 42))
    canvas.blit(gloss, (bx + 6 * ss, by + 6 * ss))

    _num_block(canvas, c, by + bh // 2 - int(6 * ss), roll, ss, size=88,
               num_col=CREAM, edge_col=PLUM, edge_w=5)
    _label_plate(canvas, c, by + bh + int(2 * ss), "STAFFS", ss, PLUM, CREAM,
                 PLUM_DK, size=22)
    return canvas, D


# ── Cell 6 (R2): bigger medallion, shorter rays, 4 cardinal studs (no bells) ──
def var_bell_sunburst_r2(roll, ss):
    """The sunburst, tightened: the central medallion grows ~20% and the rays are
    shortened ~15% so the burst frames the hero number instead of fighting it;
    the ring of ray-tip bells is dropped for four larger gold studs at the
    cardinal points (the bells turned to mud). Number gets the extra room."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    # Two-tone rays, shortened ~15% from the round-1 reach.
    n = 16
    for i in range(n):
        a0 = i * math.tau / n - math.pi / 2
        long_ray = i % 2 == 0
        rr = HD * (0.39 if long_ray else 0.32)
        col = GOLD if long_ray else LIME
        half_w = (0.10 if long_ray else 0.07)
        p_in = (c + math.cos(a0) * HD * 0.18, c + math.sin(a0) * HD * 0.18)
        p_l = (c + math.cos(a0 - half_w) * rr, c + math.sin(a0 - half_w) * rr)
        p_r = (c + math.cos(a0 + half_w) * rr, c + math.sin(a0 + half_w) * rr)
        pygame.draw.polygon(canvas, _shade_c(col, -35),
                            [(int(p_in[0]), int(p_in[1])),
                             (int(p_l[0]), int(p_l[1])), (int(p_r[0]), int(p_r[1]))])
        pygame.draw.polygon(canvas, col,
                            [(int(c), int(c)),
                             (int(p_l[0]), int(p_l[1])), (int(p_r[0]), int(p_r[1]))], 0)

    # Four larger gold studs at the cardinals replace the muddy bell ring.
    for i in range(4):
        a0 = i * math.tau / 4 - math.pi / 2
        sx = c + math.cos(a0) * HD * 0.37
        sy = c + math.sin(a0) * HD * 0.37
        _gold_stud(canvas, sx, sy, int(11 * ss), ss)

    # Medallion grown ~20% so the number sits clearly framed within it.
    med_r = int(HD * 0.29)
    pygame.draw.circle(canvas, GOLD, (c, c), med_r + int(5 * ss))
    pygame.draw.circle(canvas, _shade_c(GOLD, -45), (c, c), med_r + int(5 * ss),
                       max(2, int(2 * ss)))
    pygame.draw.circle(canvas, PLUM, (c, c), med_r)
    pygame.draw.circle(canvas, CREAM, (c, c), int(med_r * 0.78))
    pygame.draw.circle(canvas, PLUM, (c, c), int(med_r * 0.78), max(2, int(2 * ss)))

    _num_block(canvas, c, c - int(8 * ss), roll, ss, size=88,
               num_col=PLUM, edge_col=CREAM, edge_w=4)
    _label_plate(canvas, c, c + int(med_r * 0.66), "STAFFS", ss, PLUM, CREAM,
                 PLUM_DK, size=21)
    return canvas, D


def _jester_bauble(canvas, cx, hy, hr, ss):
    """The staff's mini-clown BAUBLE head — the same assembly that crowns the
    Carousel-Barker staff: a 4-point bell-tipped jester CAP (his hat), the lime
    belled RUFF collar (the "scarf"), and the grinning mini-clown FACE. The cap
    offsets are authored for hr = 13*ss, so they scale by u = hr / (13*ss)."""
    u = hr / (13.0 * ss)
    base_y = hy - hr + int(1 * ss)
    span = max(2, int(8 * ss * u))
    for (dx, dy, col) in [(-30, -8, PLUM_DK), (30, -6, PLUM_DK),
                          (-19, -29, LIME_DK), (19, -27, GOLD_DK)]:
        bxp = cx + int(dx * ss * u)
        byp = base_y + int(dy * ss * u)
        tri = [(cx - span, base_y + int(2 * ss)),
               (cx + span, base_y + int(2 * ss)), (bxp, byp)]
        pygame.draw.polygon(canvas, col, tri)
        pygame.draw.polygon(canvas, _shade_c(col, 50),
                            [(cx - span, base_y + int(2 * ss)),
                             (cx, base_y + int(2 * ss)), (bxp, byp)])
        pygame.draw.polygon(canvas, _shade_c(col, -60), tri, max(1, int(1.4 * ss)))
        br = max(2, int(3.4 * ss * u))
        pygame.draw.circle(canvas, GOLD, (int(bxp), int(byp)), br)
        pygame.draw.circle(canvas, GOLD_DK, (int(bxp), int(byp)), br, max(1, int(ss)))
    _marotte_ruff(canvas, cx, hy + hr - int(2 * ss), int(hr * 1.05), ss, LIME, lobes=9)
    _mini_clown_face(canvas, cx, hy, hr, ss, expr="grin")


# ── Cell 2 (R3): the chosen wheel, label dropped + mini-clown BAUBLE topper ───
def var_jester_wheel_r3(roll, ss):
    """The chosen jester prize-wheel, refined per the user's pick: the "STAFFS"
    label is dropped so the number stands alone, and the TOP cardinal stud is
    replaced by the staff's own mini-clown bauble (cap + ruff + face) crowning
    the wheel."""
    D = 264
    HD = D * ss
    c = HD // 2
    canvas = pygame.Surface((HD, HD), pygame.SRCALPHA)

    R = int(HD * 0.40)
    _wheel(canvas, c, R, ss, 8, WHEEL_A, WHEEL_B, spin=0.42, rim=GOLD, rim_w=7)
    # Keep the three side/bottom cardinal studs; the TOP one becomes the face.
    for i in range(1, 4):
        a = i * math.tau / 4 - math.pi / 2
        sx = c + math.cos(a) * (R + int(2 * ss))
        sy = c + math.sin(a) * (R + int(2 * ss))
        _gold_stud(canvas, sx, sy, int(11 * ss), ss)
    # Cream hub disc + hero number, now CENTRED (no label plate below it).
    hub_r = int(R * 0.62)
    pygame.draw.circle(canvas, PLUM, (c, c), hub_r + int(4 * ss))
    pygame.draw.circle(canvas, GOLD, (c, c), hub_r + int(4 * ss), max(2, int(2 * ss)))
    pygame.draw.circle(canvas, CREAM, (c, c), hub_r)
    pygame.draw.circle(canvas, PLUM, (c, c), hub_r, max(2, int(2 * ss)))
    _num_block(canvas, c, c, roll, ss, size=96, num_col=PLUM, edge_col=CREAM, edge_w=4)

    # The staff's whole mini-clown bauble (cap + ruff + face) crowns the top,
    # where the stud was — sized + seated so the cap clears the canvas top and the
    # ruff rests on the wheel without dipping onto the number in the hub.
    _jester_bauble(canvas, c, c - int(R * 0.87), int(11 * ss), ss)
    return canvas, D


VARIANTS_R3 = [
    ("2  Jester wheel  (before)", "with STAFFS label + top gold stud",
     var_jester_wheel_r2),
    ("2  Bauble topper  (NEW)", "no label, full clown bauble (cap + ruff + face) "
     "replaces the top stud", var_jester_wheel_r3),
]


# ── Round 4: bauble-TOPPER size/placement study (taller canvas) ───────────────
# The bauble sits ON TOP of a low-seated wheel; the popup canvas is taller than
# wide so the tall jester cap clears the top. Five sizes from "modest on top" to
# "huge, crowning the whole wheel" for the user to pick from.
TOPPER_DW, TOPPER_DH = 264, 360


def var_wheel_topper(roll, ss, *, R_frac, wcy_frac, b_hr_ss, seat_factor=1.6):
    """A jester prize-wheel seated low with the full clown bauble (cap+ruff+face)
    crowning the TOP. `R_frac` = wheel radius vs width; `wcy_frac` = wheel centre
    y vs height; `b_hr_ss` = bauble head radius (ss-px). `seat_factor` sets how far
    the bauble is lifted above the rim — smaller seats it LOWER so the face itself
    touches the round frame (1.6 floats it on the ruff; ~0.95 drops the face to the
    rim). Returns a TALL canvas."""
    hdw, hdh = TOPPER_DW * ss, TOPPER_DH * ss
    cx = hdw // 2
    canvas = pygame.Surface((hdw, hdh), pygame.SRCALPHA)
    R = int(hdw * R_frac)
    wcy = int(hdh * wcy_frac)
    _wheel(canvas, cx, R, ss, 8, WHEEL_A, WHEEL_B, spin=0.42, rim=GOLD, rim_w=7, cy=wcy)
    # three side/bottom cardinal studs; the TOP one is replaced by the bauble.
    for i in range(1, 4):
        a = i * math.tau / 4 - math.pi / 2
        sx = cx + math.cos(a) * (R + int(2 * ss))
        sy = wcy + math.sin(a) * (R + int(2 * ss))
        _gold_stud(canvas, sx, sy, int(11 * ss), ss)
    # cream hub + hero number, scaled to the wheel so it stays the centre hero.
    hub_r = int(R * 0.62)
    pygame.draw.circle(canvas, PLUM, (cx, wcy), hub_r + int(4 * ss))
    pygame.draw.circle(canvas, GOLD, (cx, wcy), hub_r + int(4 * ss), max(2, int(2 * ss)))
    pygame.draw.circle(canvas, CREAM, (cx, wcy), hub_r)
    pygame.draw.circle(canvas, PLUM, (cx, wcy), hub_r, max(2, int(2 * ss)))
    num_size = max(46, int(96 * R / int(hdw * 0.40)))
    _num_block(canvas, cx, wcy, roll, ss, size=num_size,
               num_col=PLUM, edge_col=CREAM, edge_w=4)
    # the full bauble crowns the top; `seat_factor` lowers it so the face meets
    # the round frame instead of floating above on the ruff.
    b_hr = int(b_hr_ss * ss)
    b_hy = (wcy - R) - int(seat_factor * b_hr)
    _jester_bauble(canvas, cx, b_hy, b_hr, ss)
    return canvas


TOPPER_VARIANTS = [
    ("A  On-top small",  "modest bauble crowning a big wheel", 0.40, 0.50, 12),
    ("B  On-top medium", "bigger bauble, slightly smaller wheel", 0.36, 0.515, 16),
    ("C  On-top large",  "large bauble on a mid wheel", 0.33, 0.54, 20),
    ("D  On-top XL",     "big bauble crowning the whole wheel", 0.30, 0.57, 24),
    ("E  On-top huge",   "huge bauble dominating the top", 0.27, 0.60, 28),
]


def render_topper_sheet():
    """Round-4 study: the 5 bauble-topper sizes on the taller popup canvas, each on
    the day sky with a true-1x 'actual size' inset. Writes round_4.png."""
    SS = 4
    DW, DH = TOPPER_DW, TOPPER_DH
    disp_w = 220
    disp_h = int(disp_w * DH / DW)
    ins_w = 90
    ins_h = int(ins_w * DH / DW)
    cols, rows = 3, 2
    pad = 20
    head = 64
    tile_w = disp_w + ins_w + 36
    tile_h = disp_h + 60
    sheet_w = cols * tile_w + (cols + 1) * pad
    sheet_h = head + rows * tile_h + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 42))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(
        "Warren Roll Celebration — bauble TOPPER size study (pick one)",
        True, (255, 255, 255)), (pad, 12))
    sheet.blit(sub_f.render(
        "Full clown bauble (cap + ruff + face) crowning the wheel, on a taller "
        "popup. A (small) -> E (huge). Number stays the hero; 1x inset = true size.",
        True, (200, 205, 215)), (pad, 40))

    label_f = hud._font(18, True)
    samp_f = hud._font(13, True)

    for idx, (name, desc, rf, wf, bh) in enumerate(TOPPER_VARIANTS):
        col = idx % cols
        row = idx // cols
        tx = pad + col * (tile_w + pad)
        ty = head + pad + row * (tile_h + pad)
        tile = sky_tile(tile_w, tile_h)

        canvas = var_wheel_topper(ROLL, SS, R_frac=rf, wcy_frac=wf, b_hr_ss=bh)
        out = pygame.transform.smoothscale(canvas, (disp_w, disp_h))
        tile.blit(out, (14, 34))

        chip = sky_tile(ins_w + 12, ins_h + 12)
        ins = pygame.transform.smoothscale(canvas, (ins_w, ins_h))
        chip.blit(ins, (6, 6))
        pygame.draw.rect(chip, (255, 255, 255), chip.get_rect(), 2)
        tile.blit(chip, (disp_w + 22, tile_h - ins_h - 40))
        tile.blit(samp_f.render("actual size", True, (255, 255, 255)),
                  (disp_w + 22, tile_h - ins_h - 58))

        strip = pygame.Surface((tile_w, 28), pygame.SRCALPHA)
        strip.fill((20, 22, 28, 210))
        tile.blit(strip, (0, 0))
        tile.blit(label_f.render(name, True, LIME), (8, 5))
        cap = pygame.Surface((tile_w, 22), pygame.SRCALPHA)
        cap.fill((20, 22, 28, 210))
        tile.blit(cap, (0, tile_h - 22))
        tile.blit(samp_f.render(f"{desc}  (roll {ROLL})", True, (220, 225, 235)),
                  (8, tile_h - 19))
        sheet.blit(tile, (tx, ty))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "dice_results", "warren_roll")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_4.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


# Round 5: keep D + E only, with the bauble dropped so the FACE touches the rim.
TOPPER_VARIANTS_R5 = [
    ("D  face on the frame", "big bauble, face dropped to touch the round frame",
     0.30, 0.57, 24, 0.95),
    ("E  face on the frame", "huge bauble, face dropped to touch the round frame",
     0.27, 0.60, 28, 0.95),
]


def render_facesize_ingame():
    """Show the shipped roll celebration at several clown-FACE (bauble) sizes, each
    composited on a game screen (day sky + the top-centre score counter, banner
    drawn OVER it + a bit low, exactly as in game). One labelled row. round_6.png."""
    from game import warren_celebration as wc
    GW, GH = 360, 640
    SS = 4
    sizes = [20, 24, 28, 32, 34]          # bauble head radius (ss-px); 28 = current ship
    disp_scale = 0.62
    dw, dh = int(GW * disp_scale), int(GH * disp_scale)
    pad = 18
    head = 60
    label_h = 26
    gap = 14
    cell_w, cell_h = dw, label_h + dh
    sheet_w = pad * 2 + len(sizes) * cell_w + (len(sizes) - 1) * gap
    sheet_h = head + cell_h + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 42))
    title_f = hud._font(26, True)
    lab_f = hud._font(17, True)
    samp = hud._font(13, True)
    sheet.blit(title_f.render(
        "Warren roll celebration — clown-FACE size sweep (shown in game)",
        True, (255, 255, 255)), (pad, 12))
    sheet.blit(samp.render(
        "Each = the popup as it appears in game (day sky + score counter, banner "
        "drawn over it + a bit low). 28 = current ship.",
        True, (200, 205, 215)), (pad, 40))

    for idx, fs in enumerate(sizes):
        scr = pygame.Surface((GW, GH))
        for y in range(GH):
            t = y / GH
            scr.fill((int(120 + 55 * t), int(180 + 35 * t), int(225 + 20 * t)),
                     (0, y, GW, 1))
        # mock top-centre score plate (like draw_play) to show the overlay.
        sw = 102
        sp = pygame.Rect((GW - sw) // 2, 42, sw, 56)
        pygame.draw.rect(scr, (54, 46, 38), sp, border_radius=9)
        pygame.draw.rect(scr, GOLD, sp, 2, border_radius=9)
        nf = hud._font(40, True)
        scr.blit(nf.render("5", True, CREAM),
                 nf.render("5", True, CREAM).get_rect(center=sp.center))
        # the celebration at this face size, drawn OVER the score, a bit low.
        canvas, cdw, cdh = wc.render(17, False, ss=SS, b_hr_ss=fs)
        pop = pygame.transform.smoothscale(canvas, (cdw, cdh))
        scr.blit(pop, pop.get_rect(center=(GW // 2, 210)))

        tx = pad + idx * (cell_w + gap)
        ty = head + pad
        strip = pygame.Surface((cell_w, label_h))
        strip.fill((20, 22, 28))
        tag = "face %d%s" % (fs, "  (current)" if fs == 28 else "")
        strip.blit(lab_f.render(tag, True, LIME), (6, 4))
        sheet.blit(strip, (tx, ty))
        sheet.blit(pygame.transform.smoothscale(scr, (dw, dh)), (tx, ty + label_h))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "dice_results", "warren_roll")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_6.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


def render_topper_sheet_r5():
    """Round-5 study: D + E only, with the bauble seated LOWER so the clown's face
    touches the round wheel frame (not floating above on the ruff). round_5.png."""
    SS = 4
    DW, DH = TOPPER_DW, TOPPER_DH
    disp_w = 240
    disp_h = int(disp_w * DH / DW)
    ins_w = 100
    ins_h = int(ins_w * DH / DW)
    pad = 20
    head = 64
    tile_w = disp_w + ins_w + 36
    tile_h = disp_h + 60
    cols = 2
    sheet_w = cols * tile_w + (cols + 1) * pad
    sheet_h = head + tile_h + 2 * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 42))

    title_f = hud._font(28, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(
        "Warren Roll Celebration — D & E with the face DROPPED onto the frame",
        True, (255, 255, 255)), (pad, 12))
    sheet.blit(sub_f.render(
        "Bauble seated lower so the clown face touches the round wheel rim. "
        "1x inset = true on-screen size.", True, (200, 205, 215)), (pad, 40))

    label_f = hud._font(18, True)
    samp_f = hud._font(13, True)

    for idx, (name, desc, rf, wf, bh, seat) in enumerate(TOPPER_VARIANTS_R5):
        tx = pad + idx * (tile_w + pad)
        ty = head + pad
        tile = sky_tile(tile_w, tile_h)
        canvas = var_wheel_topper(ROLL, SS, R_frac=rf, wcy_frac=wf,
                                  b_hr_ss=bh, seat_factor=seat)
        tile.blit(pygame.transform.smoothscale(canvas, (disp_w, disp_h)), (14, 34))
        chip = sky_tile(ins_w + 12, ins_h + 12)
        chip.blit(pygame.transform.smoothscale(canvas, (ins_w, ins_h)), (6, 6))
        pygame.draw.rect(chip, (255, 255, 255), chip.get_rect(), 2)
        tile.blit(chip, (disp_w + 22, tile_h - ins_h - 40))
        tile.blit(samp_f.render("actual size", True, (255, 255, 255)),
                  (disp_w + 22, tile_h - ins_h - 58))
        strip = pygame.Surface((tile_w, 28), pygame.SRCALPHA)
        strip.fill((20, 22, 28, 210))
        tile.blit(strip, (0, 0))
        tile.blit(label_f.render(name, True, LIME), (8, 5))
        cap = pygame.Surface((tile_w, 22), pygame.SRCALPHA)
        cap.fill((20, 22, 28, 210))
        tile.blit(cap, (0, tile_h - 22))
        tile.blit(samp_f.render(f"{desc}  (roll {ROLL})", True, (220, 225, 235)),
                  (8, tile_h - 19))
        sheet.blit(tile, (tx, ty))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "dice_results", "warren_roll")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_5.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


VARIANTS_R2 = [
    ("1  Original (baseline)", "current 12-wedge orange/pink wheel + PILLARS",
     var_baseline),
    ("2  Jester prize-wheel", "8 wedges, big-number hub, 4 gold studs",
     var_jester_wheel_r2),
    ("3  Barber-twist sign  (WINNER)", "wider spiral pitch, lighter shadow, "
     "number nudged down", var_barber_sign_r2),
    ("4  Marotte plaque", "squarer plaque, +20% number, smaller low marottes",
     var_marotte_plaque_r2),
    ("5  Cap-bell banderole  (ALT)", "keylined cap points + larger side bells",
     var_cap_banderole_r2),
    ("6  Bell-burst sunburst", "bigger medallion, shorter rays, 4 cardinal studs",
     var_bell_sunburst_r2),
]


def render_sheet(variants=VARIANTS, out_name="round_1.png", *,
                 title="Warren Roll-Result Celebration — Round 1 "
                 "(baseline + 5 jester variants)"):
    SS = 4  # supersample for crisp downscale to true size
    TRUE = 264   # popup is 264 design px on the 360 canvas
    INSET = 116  # actual-size inset shows the popup at real small-screen size
    cols = 3
    rows = max(1, -(-len(variants) // cols))   # ceil, so a short list isn't padded
    pad = 20
    head = 64
    tile_w = TRUE + INSET + 40
    tile_h = TRUE + 96
    sheet_w = cols * tile_w + (cols + 1) * pad
    sheet_h = head + rows * tile_h + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 42))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(title, True, (255, 255, 255)), (pad, 12))
    sheet.blit(sub_f.render(
        "Cell 1 = current ship wheel. Cells 2-6 = high-res Plum & Lime clown+staff "
        "takes. True 264px on day sky + actual-size inset.",
        True, (200, 205, 215)), (pad, 40))

    label_f = hud._font(19, True)
    samp_f = hud._font(13, True)

    for idx, (name, desc, fn) in enumerate(variants):
        col = idx % cols
        row = idx // cols
        tx = pad + col * (tile_w + pad)
        ty = head + pad + row * (tile_h + pad)

        tile = sky_tile(tile_w, tile_h)
        canvas, D = fn(ROLL, SS)

        out = pygame.transform.smoothscale(canvas, (TRUE, TRUE))
        tile.blit(out, out.get_rect(center=(16 + TRUE // 2, 36 + TRUE // 2)))

        chip = sky_tile(INSET + 16, INSET + 16)
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
        tag = (190, 196, 206) if idx == 0 else LIME
        tile.blit(label_f.render(name, True, tag), (8, 6))
        cap = pygame.Surface((tile_w, 24), pygame.SRCALPHA)
        cap.fill((20, 22, 28, 205))
        tile.blit(cap, (0, tile_h - 24))
        tile.blit(samp_f.render(f"{desc}  (roll {ROLL})", True, (220, 225, 235)),
                  (8, tile_h - 21))
        sheet.blit(tile, (tx, ty))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "dice_results", "warren_roll")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, out_name)
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


def main():
    # Opt-in flags so these look-dev sheets aren't rendered by accident.
    if "--warren-cele-r6" in sys.argv:
        render_facesize_ingame()
    elif "--warren-cele-r5" in sys.argv:
        render_topper_sheet_r5()
    elif "--warren-cele-r4" in sys.argv:
        render_topper_sheet()
    elif "--warren-cele-r3" in sys.argv:
        render_sheet(
            VARIANTS_R3, "round_3.png",
            title="Warren Roll Celebration — Jester wheel refined "
            "(drop STAFFS label + clown bauble topper: cap + ruff + face)")
    elif "--warren-cele-r2" in sys.argv:
        render_sheet(
            VARIANTS_R2, "round_2.png",
            title="Warren Roll-Result Celebration — Round 2 "
            "(art-director polish: cell 3 WINNER, cell 5 ALT)")
    elif "--warren-cele" in sys.argv:
        render_sheet()
    else:
        print("pass --warren-cele (round_1.png) or --warren-cele-r2 (round_2.png)")


if __name__ == "__main__":
    main()
