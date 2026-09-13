"""
Bespoke engraved center glyphs for the SHAME — Blooper Reel + Wasted Opportunity
(Wall of Shame) medallions, rendered TARNISHED (cracked-pewter anti-trophy).

Same single-colour engrave idiom as ``game.achievement_icons``: each
``_glyph_<id>(surf, cx, cy, r, col)`` lays BOLD filled shapes in the passed
``col`` only (the builder strokes a down-right inset shadow + up-left sheen for
the struck-relief look), with recessed sockets/notches drawn in the shared
engraved-shadow tone ``_SH``. Authored to the ~44px legibility floor: nothing
thinner than ~3px or smaller than ~5px, ONE decisive silhouette per glyph with
the JOKE living in the shape, never a figure-plus-props tangle.

The read per id:
  * bullet_bystander — an hourglass split by a collision-burst: time crawled and
                       you SPLATTED anyway.
  * cursed           — a skull breathing out a genie-wisp: the wish that killed
                       you (SKULL-led, so never the plain poison skull or a lamp).
  * board_to_death   — a skateboard flipped WHEELS-UP with a wipeout star: ate it
                       mid-trick (the skate glyph, inverted).
  * lightning_rod    — one bold bolt striking a scorched feather: zapped off your
                       perch, single strike.
  * party_foul       — a tipped party-popper spraying confetti + a sad down-tick:
                       the Day-Complete party is what got you.
  * rich_reckless    — a horseshoe magnet with a coin escaping, slashed out: the
                       vacuum that caught nothing.
  * coin_blind       — a coin wearing a blindfold band: flew a whole Coin Rush
                       blind to the loot.
  * wish_unspent     — an upright, whole lamp with NO wisp (a slash of absence):
                       grabbed the lamp, died before a wish. Lamp is the WHOLE
                       silhouette, dormant — distinct from cursed's skull and the
                       pillar-led the_49er.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai

# Reuse the live module's engraved-shadow tone so recessed sockets/notches match
# the cast-shadow pass the builder stamps around every glyph.
_SH = ai._GLYPH_SH

_glyph_fonts: dict = {}


def _glyph_font(px: int):
    # Mirror ``achievement_icons._glyph_font`` so a `$` coin face matches the
    # Riches family exactly.
    f = _glyph_fonts.get(px)
    if f is None:
        f = pygame.font.SysFont(None, px, bold=True)
        _glyph_fonts[px] = f
    return f


def _ring_dollar(surf, cx, cy, r, col, rr):
    # The in-game `$` coin read, matching ``_glyph_coin``: a bold ring with a
    # struck `$` centred in it, so a coin here is unmistakably the wealth coin.
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 8))
    f = _glyph_font(int(rr * 1.7))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy)))


def _glyph_bullet_bystander(surf, cx, cy, r, col):
    # An hourglass (Slow-Mo) shattered by a collision-burst at its waist — time
    # crawled and you SPLATTED anyway. The bold bowtie glass reads as "slow"; the
    # jagged crack driven through the pinch plus the radiating impact spikes are
    # the crash the slowdown never saved you from.
    w = int(r * 0.60)                     # half-width at the caps
    h = int(r * 0.74)                     # half-height to a cap plate
    capw = max(4, int(r * 0.16))
    # top + bottom cap plates so the glass reads as a framed hourglass
    for sy in (cy - h, cy + h - capw):
        pygame.draw.rect(surf, col, (cx - w, sy, w * 2, capw),
                         border_radius=max(1, r // 16))
    # the two glass bulbs as a filled bowtie meeting at the waist — bold so it
    # survives at 44px, unlike a thin outline.
    inset = capw
    pygame.draw.polygon(surf, col, [
        (cx - w + inset, cy - h + capw), (cx + w - inset, cy - h + capw), (cx, cy)])
    pygame.draw.polygon(surf, col, [
        (cx - w + inset, cy + h - capw), (cx + w - inset, cy + h - capw), (cx, cy)])
    # a jagged crack driven down through the waist, engraved in the shadow tone.
    pygame.draw.lines(surf, _SH, False, [
        (cx - int(r * 0.20), cy - int(r * 0.42)),
        (cx + int(r * 0.06), cy - int(r * 0.10)),
        (cx - int(r * 0.08), cy + int(r * 0.06)),
        (cx + int(r * 0.16), cy + int(r * 0.44)),
    ], max(3, r // 11))
    # impact spikes bursting out of the waist beyond the glass — the "splat".
    # Shorter + splayed steeper (up/down) so they clear the cap plates.
    for a in (math.radians(140), math.radians(220), math.radians(-40),
              math.radians(40)):
        ex = cx + int(math.cos(a) * r * 0.72)
        ey = cy + int(math.sin(a) * r * 0.44)
        pygame.draw.line(surf, col, (cx, cy), (ex, ey), max(2, r // 13))


def _glyph_cursed(surf, cx, cy, r, col):
    # A skull breathing out a genie-wisp of poison vapour — the wish that KILLED
    # you. The skull LEADS (round cranium + jaw + dark sockets) so it never reads
    # as the plain poison skull or a lamp; the curling wisp rising off its crown
    # is the cursed genie-breath that seals the joke.
    sk = cy + int(r * 0.30)               # skull pushed low so the wisp has sky
    cr = int(r * 0.50)
    pygame.draw.circle(surf, col, (cx, sk), cr)
    jaw = pygame.Rect(cx - int(cr * 0.58), sk + int(cr * 0.46),
                      int(cr * 1.16), int(cr * 0.66))
    pygame.draw.rect(surf, col, jaw, border_radius=max(2, r // 10))
    # two dark eye sockets + a nasal notch, all in the engraved shadow tone
    for dx in (-0.44, 0.44):
        pygame.draw.circle(surf, _SH, (cx + int(dx * cr), sk - int(cr * 0.12)),
                           max(3, r // 8))
    pygame.draw.polygon(surf, _SH, [
        (cx, sk + int(cr * 0.14)),
        (cx - int(cr * 0.20), sk + int(cr * 0.48)),
        (cx + int(cr * 0.20), sk + int(cr * 0.48)),
    ])
    # the genie-wisp: an S of thick curling strokes rising off the crown into a
    # small vapour puff — the breath of the fatal wish.
    top = sk - cr
    pygame.draw.lines(surf, col, False, [
        (cx + int(r * 0.02), top),
        (cx - int(r * 0.22), top - int(r * 0.26)),
        (cx + int(r * 0.18), top - int(r * 0.52)),
        (cx - int(r * 0.10), top - int(r * 0.78)),
    ], max(3, r // 11))
    # puffs offset to one side so the wisp curls asymmetrically, not straight up.
    for px, py, pr in ((-0.14, -0.84, 0.11), (-0.26, -0.98, 0.15)):
        pygame.draw.circle(surf, col, (cx + int(r * px), top + int(r * py)),
                           max(3, int(r * pr)))


def _glyph_board_to_death(surf, cx, cy, r, col):
    # A skateboard flung belly-up mid-wipeout — you ate it doing a trick. A fat
    # rounded plank TILTED ~20° (launched, not level, so it never reads as a level
    # frown) with its two wheels clustered close on ONE end pointing up on visible
    # truck stubs, a grip-tape seam down the deck top, and a tumble-star only after
    # the board reads. The tilt + one-sided belly-up wheels break the night-owl
    # face collision the symmetric version had.
    ang = math.radians(-20)               # whole board rotated (launched off-axis)
    ca, sa = math.cos(ang), math.sin(ang)

    def rot(px, py):
        return (cx + int(px * ca - py * sa), cy + int(px * sa + py * ca))

    th = int(r * 0.34)                     # FAT plank, a dominant mass
    hl = int(r * 0.82)                     # half-length of the deck
    # fat rounded plank via a thick capsule: a bar plus round end-caps.
    top = rot(-hl, -th // 2)
    bl = rot(-hl, th // 2)
    tr = rot(hl, -th // 2)
    br = rot(hl, th // 2)
    pygame.draw.polygon(surf, col, [top, tr, br, bl])
    for ex, ey in (rot(-hl, 0), rot(hl, 0)):
        pygame.draw.circle(surf, col, (ex, ey), th // 2)
    # grip-tape seam along the deck top so the belly-up plank reads as a deck.
    s0 = rot(-hl * 0.7, -th * 0.24)
    s1 = rot(hl * 0.7, -th * 0.24)
    pygame.draw.line(surf, _SH, s0, s1, max(2, r // 14))
    # two wheels clustered close on the RIGHT end, up on short truck stubs — a
    # belly-up asymmetry, not two symmetric eyes.
    wr = max(5, int(r * 0.19))
    for pxl in (0.34, 0.66):
        stub = rot(hl * pxl, -th * 0.5)
        wheel = rot(hl * pxl, -th * 0.5 - r * 0.24)
        pygame.draw.line(surf, col, stub, wheel, max(3, r // 9))   # truck stub
        pygame.draw.circle(surf, _SH, wheel, wr)
        pygame.draw.circle(surf, col, wheel, max(1, wr // 3))
    # a wipeout tumble-star at the lower-left where the rider hit the ground.
    sx, sy = cx - int(r * 0.58), cy + int(r * 0.52)
    for a in range(8):
        aa = a * math.pi / 4
        ln = r * (0.24 if a % 2 == 0 else 0.12)
        pygame.draw.line(surf, col, (sx, sy),
                         (sx + int(math.cos(aa) * ln), sy + int(math.sin(aa) * ln)),
                         max(2, r // 14))


def _glyph_lightning_rod(surf, cx, cy, r, col):
    # One bold lightning bolt striking down onto a scorched feather — zapped clean
    # off your perch. A single jagged bolt plunging into a singed feather, with
    # scorch-marks radiating from the contact, reads as a direct hit at 44px.
    # the bolt: a filled zigzag falling from the top toward the feather.
    bolt = [
        (cx + int(r * 0.10), cy - int(r * 0.92)),
        (cx - int(r * 0.30), cy - int(r * 0.14)),
        (cx - int(r * 0.02), cy - int(r * 0.14)),
        (cx - int(r * 0.24), cy + int(r * 0.30)),
        (cx + int(r * 0.34), cy - int(r * 0.34)),
        (cx + int(r * 0.06), cy - int(r * 0.34)),
        (cx + int(r * 0.34), cy - int(r * 0.92)),
    ]
    # nudge the bolt's lower tip DOWN so it touches the feather — contact sells
    # "struck". The point at index 3 is the bolt's low tip.
    bolt[3] = (cx - int(r * 0.20), cy + int(r * 0.40))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in bolt])
    # the struck feather lying low: a TAPERED lens (pointed left tip, rounded
    # blunt right) tilted slightly, with an engraved rachis and short barb ticks
    # so it reads as a feather, not a bean.
    fcx, fcy = cx + int(r * 0.02), cy + int(r * 0.54)
    fa = math.radians(-14)
    ux, uy = math.cos(fa), math.sin(fa)
    nx, ny = -uy, ux
    L = r * 0.50
    prof = ((-1.0, 0.0), (-0.55, 0.20), (0.0, 0.24), (0.6, 0.18), (1.0, 0.09))
    topln, botln = [], []
    for t, w in prof:
        axx = fcx + ux * L * t
        axy = fcy + uy * L * t
        topln.append((axx + nx * r * w, axy + ny * r * w))
        botln.append((axx - nx * r * w, axy - ny * r * w))
    pygame.draw.polygon(surf, col, [(int(x), int(y))
                                    for x, y in topln + botln[::-1]])
    # rachis + barbs in the engraved shadow tone.
    tip = (fcx - ux * L, fcy - uy * L)
    end = (fcx + ux * L, fcy + uy * L)
    pygame.draw.line(surf, _SH, (int(tip[0]), int(tip[1])),
                     (int(end[0]), int(end[1])), max(2, r // 14))
    for t in (-0.2, 0.2, 0.55):
        bxx = fcx + ux * L * t
        bxy = fcy + uy * L * t
        for sgn in (-1, 1):
            pygame.draw.line(surf, _SH, (int(bxx), int(bxy)),
                             (int(bxx + (ux * 0.4 + nx * sgn) * r * 0.14),
                              int(bxy + (uy * 0.4 + ny * sgn) * r * 0.14)),
                             max(1, r // 20))
    # scorch-burst radiating from the strike point where bolt meets feather.
    ix, iy = cx - int(r * 0.16), cy + int(r * 0.40)
    for a in (math.radians(210), math.radians(250), math.radians(290),
              math.radians(330)):
        pygame.draw.line(surf, col, (ix, iy),
                         (ix + int(math.cos(a) * r * 0.26),
                          iy + int(math.sin(a) * r * 0.26)), max(2, r // 13))


def _glyph_party_foul(surf, cx, cy, r, col):
    # A party-popper tube erupting a WIDE burst of confetti — the Day-Complete
    # celebration is exactly what killed you. The tube points up-right with a clear
    # RIM RING at its mouth (so it reads as an open tube, not a solid triangle),
    # and the confetti scatters as a broad multi-directional spray of chunky
    # dots + bars across the upper-right — the opposite of kfc_incident's tight
    # down-left spill, so the two never converge.
    ang = math.radians(-40)
    ca, sa = math.cos(ang), math.sin(ang)
    acx, acy = cx - int(r * 0.44), cy + int(r * 0.40)   # apex, lower-left

    def rot(px, py):
        return (acx + int(px * ca - py * sa), acy + int(px * sa + py * ca))

    mouth_l = rot(r * 0.72, -r * 0.34)
    mouth_r = rot(r * 0.72, r * 0.34)
    pygame.draw.polygon(surf, col, [(acx, acy), mouth_l, mouth_r])
    # rim RING at the mouth — an ellipse lip so the cone reads as a hollow tube.
    mouth_c = rot(r * 0.72, 0)
    rim = pygame.Rect(0, 0, int(r * 0.24), int(r * 0.66))
    rim.center = mouth_c
    pygame.draw.ellipse(surf, col, rim, max(3, r // 12))
    # a WIDE fan of confetti bursting up-and-right — chunky dots mixed with short
    # bars scattered across the quadrant, the celebration spray.
    bursts = (
        (-0.85, 0.62, "dot"), (-0.50, 0.96, "bar"), (-0.20, 0.72, "dot"),
        (0.12, 1.00, "bar"), (0.42, 0.66, "dot"), (0.70, 0.88, "dot"),
    )
    for da, ln, kind in bursts:
        fa = ang + da
        ex = mouth_c[0] + int(math.cos(fa) * r * ln)
        ey = mouth_c[1] + int(math.sin(fa) * r * ln)
        if kind == "dot":
            pygame.draw.circle(surf, col, (ex, ey), max(3, int(r * 0.11)))
        else:
            bx = int(math.cos(fa) * r * 0.18)
            by = int(math.sin(fa) * r * 0.18)
            pygame.draw.line(surf, col, (ex - bx, ey - by), (ex + bx, ey + by),
                             max(3, r // 11))


def _glyph_rich_reckless(surf, cx, cy, r, col):
    # A horseshoe magnet that grabbed NOTHING — a fat U dominating the field, its
    # banded poles gaping open while a tiny `$` darts AWAY off their mouth on a
    # motion streak. The chunky magnet is the whole silhouette (no bare "C"); the
    # escaping coin is a small disc, not a slashed ring, so it reads "the vacuum
    # caught nothing", not "null". Pure single-colour; pole-bands in `_SH`.
    # A fat horseshoe drawn as a thick near-closed ring with its GAP opening
    # up-right — the classic magnet silhouette, dominating the field. The two tips
    # flanking the gap wear thick `_SH` pole-bands.
    mcx, mcy = cx - int(r * 0.14), cy + int(r * 0.10)
    rr = int(r * 0.56)
    bar = max(8, int(r * 0.32))
    arc_rect = pygame.Rect(mcx - rr, mcy - rr, rr * 2, rr * 2)
    # pygame arc angles are CCW from east in a y-UP frame; the gap spans 5°..85°
    # (screen upper-right), so the solid horseshoe runs 85° all the way to 365°.
    pygame.draw.arc(surf, col, arc_rect, math.radians(85), math.radians(365), bar)
    # banded pole-tips: short thick `_SH` arcs riding the ring just inside each
    # tip so both poles read as banded magnet ends.
    for tip in (5, 85):
        pygame.draw.arc(surf, _SH, arc_rect, math.radians(tip),
                        math.radians(tip + 15), bar)
    # a small `$` coin darting away past the open mouth on a short motion streak —
    # the loot the magnet never pulled in.
    coin_cx = cx + int(r * 0.50)
    coin_cy = cy - int(r * 0.48)
    crr = int(r * 0.24)
    pygame.draw.circle(surf, col, (coin_cx, coin_cy), crr)
    f = _glyph_font(int(crr * 2.0))
    g = f.render("$", True, _SH)
    surf.blit(g, g.get_rect(center=(coin_cx, coin_cy)))
    for off in (0.0, 0.18):
        s0 = (coin_cx - int(r * (0.30 + off)), coin_cy + int(r * (0.28 + off)))
        s1 = (coin_cx - int(r * (0.14 + off)), coin_cy + int(r * (0.12 + off)))
        pygame.draw.line(surf, col, s0, s1, max(2, r // 14))


def _glyph_coin_blind(surf, cx, cy, r, col):
    # A `$` coin wearing a blindfold band — flew a whole Coin Rush half-blind and
    # grabbed nothing. The bold coin ring with a thick band strapped across its
    # face (knot + trailing tie-tails to one side) is the read: blind to the loot.
    rr = int(r * 0.60)
    pygame.draw.circle(surf, col, (cx, cy), rr, max(3, r // 8))
    # `$` peeking above the band so the coin reads as the wealth coin.
    f = _glyph_font(int(rr * 1.2))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(cx, cy - int(rr * 0.46))))
    # the blindfold band strapped across the coin's lower-middle (eye level).
    band_h = max(6, int(r * 0.30))
    band_y = cy + int(r * 0.02)
    pygame.draw.rect(surf, col, (cx - rr - int(r * 0.10), band_y - band_h // 2,
                                 (rr + int(r * 0.10)) * 2, band_h),
                     border_radius=max(1, r // 14))
    # a small dark seam so the band reads as fabric, not a bar.
    pygame.draw.line(surf, _SH, (cx - rr, band_y), (cx + rr, band_y), max(2, r // 16))
    # a fat knot + two long, thick trailing tie-tails streaming off the right edge
    # — the tails ARE the whole "blindfold-strap" signal, so they stay bold at 44px.
    kx = cx + rr + int(r * 0.10)
    pygame.draw.circle(surf, col, (kx, band_y), max(4, int(r * 0.17)))
    tw = max(4, int(r * 0.16))
    for sgn in (-1, 1):
        pygame.draw.lines(surf, col, False, [
            (kx, band_y),
            (kx + int(r * 0.28), band_y + sgn * int(r * 0.18)),
            (kx + int(r * 0.50), band_y + sgn * int(r * 0.40)),
        ], tw)


def _glyph_wish_unspent(surf, cx, cy, r, col):
    # An upright, whole genie lamp with NO wisp — a slash marking the ABSENCE
    # where the smoke should rise: you grabbed the lamp and died before a wish.
    # The lamp is the WHOLE silhouette here (body + spout + handle + lid knob),
    # dormant — distinct from cursed's skull and the pillar-led the_49er.
    lcy = cy + int(r * 0.20)
    # fat lamp body low-centre.
    bw, bh = int(r * 1.10), int(r * 0.62)
    pygame.draw.ellipse(surf, col, (cx - bw // 2, lcy - bh // 2, bw, bh))
    # spout flicking up to the LEFT — the classic Aladdin lamp read.
    pygame.draw.polygon(surf, col, [
        (cx - int(r * 0.36), lcy - int(r * 0.08)),
        (cx - int(r * 0.92), lcy - int(r * 0.44)),
        (cx - int(r * 0.34), lcy + int(r * 0.14)),
    ])
    # C-handle looping off the right.
    hr = pygame.Rect(cx + int(r * 0.30), lcy - int(r * 0.30),
                     int(r * 0.46), int(r * 0.58))
    pygame.draw.arc(surf, col, hr, math.radians(-70), math.radians(120),
                    max(3, r // 10))
    # lid knob on top so the dome reads as a lidded vessel.
    pygame.draw.circle(surf, col, (cx + int(r * 0.04), lcy - int(bh * 0.52)),
                       max(3, int(r * 0.11)))
    # the ABSENCE: a faint wisp-curl starting to rise off the spout mouth, then one
    # BOLD slash overstruck across it — the slash visibly cancels the wish before
    # it forms, so "never rubbed" reads instead of a stray sparkle.
    spx, spy = cx - int(r * 0.62), lcy - int(r * 0.30)   # spout mouth
    pygame.draw.lines(surf, _SH, False, [
        (spx, spy),
        (spx - int(r * 0.06), spy - int(r * 0.26)),
        (spx + int(r * 0.14), spy - int(r * 0.44)),
    ], max(2, r // 13))
    d = int(r * 0.30)
    wx, wy = spx + int(r * 0.02), spy - int(r * 0.24)
    pygame.draw.line(surf, col, (wx - d, wy + d), (wx + d, wy - d), max(3, r // 10))


GLYPHS = {
    "bullet_bystander": _glyph_bullet_bystander,
    "cursed": _glyph_cursed,
    "board_to_death": _glyph_board_to_death,
    "lightning_rod": _glyph_lightning_rod,
    "party_foul": _glyph_party_foul,
    "rich_reckless": _glyph_rich_reckless,
    "coin_blind": _glyph_coin_blind,
    "wish_unspent": _glyph_wish_unspent,
}
