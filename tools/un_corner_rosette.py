"""Scratch mockup: the `corner-rosette` unlock-notice concept.

A single bold "commendation seal" stamped into the top-right dead corner —
the way a certificate carries a gold-foil seal. A scalloped/notched foil disc
(NO sunburst rays) reads as STRUCK INTO the paper (flat, no ribbon, no hung
medal), so it stays clearly distinct from the medal-rail badge-on-ribbon
language AND from the full-screen award beat, which owns the only radiating
rays in the option set. One always-present object + a "2 EARNED" count-badge.

The seal is tucked FULLY into the corner wedge above the 'RUN SUMMARY' title
baseline (title lettering occupies y48-64, right edge ~x310), so it occludes
nothing: title, hero plaque, stat tiles, power-up strip, and buttons stay clear.

Scratch tooling only; `game/` is untouched.
"""
import os
import math
import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game.achievement_icons import draw_badge
from game.hud import (_font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _NIGHT_DEEP)

# Local foil palette tuned to the gold-on-navy "Courier's Commendation" family.
_FOIL_HI   = (255, 240, 188)   # foil crest catching the upper-left light
_FOIL_MID  = (236, 190,  78)   # body gold of the foil
_FOIL_LO   = (168, 116,  28)   # shadowed lower-right of the foil
_FOIL_EDGE = ( 96,  62,  14)   # thin keyline round the seal
_INK_NAVY  = (14, 9, 40)


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _draw_notched_rim(surf, cx, cy, R, n, col):
    """A scalloped foil-disc rim: a continuous gold ring whose outer edge is
    notched with shallow bumps and grooves, like the milled border pressed into
    a wax/foil certificate seal. Deliberately NON-radiating — no rays leave the
    disc — so the corner seal never competes with the award-beat's sunburst."""
    rim = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    bump = R * 0.16          # how far each scallop bulges past the base radius
    r_out = R + bump
    # Outer scalloped contour: a polygon whose radius oscillates with a cosine,
    # so the silhouette gains soft rounded notches rather than sharp teeth.
    steps = n * 6
    outer = []
    for i in range(steps):
        a = i * math.tau / steps
        rr = R + bump * (math.cos(a * n) * 0.5 + 0.5)
        outer.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    # Light the rim from the upper-left so it ties to the foil's single source.
    pygame.draw.polygon(rim, _lerp(_FOIL_LO, col, 0.55), outer)
    surf.blit(rim, (0, 0))
    # A thin keyline traces the scalloped edge to crisp the pressed border.
    pygame.draw.polygon(surf, _FOIL_EDGE, outer, 2)
    # Small recessed dots in each notch valley read as the milled punch marks.
    for i in range(n):
        a = (i + 0.5) * math.tau / n
        dx = cx + math.cos(a) * (R + bump * 0.5)
        dy = cy + math.sin(a) * (R + bump * 0.5)
        d = (math.cos(a - math.radians(135)) + 1) * 0.5
        dc = _lerp(_FOIL_LO, _FOIL_HI, 0.25 + 0.55 * d)
        pygame.draw.circle(surf, dc, (int(dx), int(dy)), max(1, int(R * 0.07)))
    return r_out


def _draw_seal(surf, cx, cy, R, badge_id):
    """A struck gold-foil seal: scalloped/notched rim, a domed foil disc lit
    upper-left, a recessed navy well, and the unlocked badge pressed into it."""
    # Notched foil rim sits just behind the domed disc.
    _draw_notched_rim(surf, cx, cy, int(R * 1.0), 18, _FOIL_MID)

    # Domed foil disc — radial-ish shading via stacked circles, light upper-left.
    for i in range(R, 0, -1):
        t = (R - i) / R
        base = _lerp(_FOIL_HI, _FOIL_LO, t)
        pygame.draw.circle(surf, base, (cx, cy), i)
    # Offset specular bloom toward the upper-left to dome the foil.
    bloom = pygame.Surface((R * 2, R * 2), pygame.SRCALPHA)
    for i in range(int(R * 0.62), 0, -1):
        t = i / (R * 0.62)
        pygame.draw.circle(bloom, (*_FOIL_HI, int(120 * (1 - t))),
                           (int(R * 0.78), int(R * 0.74)), i)
    surf.blit(bloom, (cx - R, cy - R))
    pygame.draw.circle(surf, _FOIL_EDGE, (cx, cy), R, max(1, R // 16))

    # Recessed navy well that carries the emblem — a stamped inner field.
    wr = int(R * 0.62)
    pygame.draw.circle(surf, _INK_NAVY, (cx, cy), wr)
    pygame.draw.circle(surf, _FOIL_LO, (cx, cy), wr, max(1, R // 18))
    # The earned emblem, pressed into the well.
    em = int(wr * 1.86)
    draw_badge(surf, badge_id, pygame.Rect(cx - em // 2, cy - em // 2, em, em),
               unlocked=True)


def _draw_count_badge(surf, right_x, ccy, n):
    """A compact dark '2 EARNED' count-pill — the tally that turns one
    always-present seal into a counter without a second seal. A gold numeral
    chip + small caption, right-anchored so it never drifts over the title
    lettering or off the screen edge."""
    f_num = _font(16, bold=True)
    f_lbl = _font(11, bold=True)
    num = f_num.render(str(n), True, _NIGHT_DEEP)
    lbl = f_lbl.render("EARNED", True, _GOLD_PALE)
    chip_r = num.get_height() // 2 + 2
    gap = 4
    inner = chip_r * 2 + gap + lbl.get_width()
    pad = 5
    w = inner + pad * 2
    h = chip_r * 2 + 6
    x = right_x - w
    y = ccy - h // 2
    pill = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(pill, (*_PANEL_DARK, 250), pill.get_rect(),
                     border_radius=h // 2)
    pygame.draw.rect(pill, _GOLD_BRIGHT, pill.get_rect(), 2, border_radius=h // 2)
    surf.blit(pill, (x, y))
    # gold numeral chip on the left of the pill
    ccx = x + pad + chip_r
    for i in range(chip_r, 0, -1):
        t = (chip_r - i) / chip_r
        pygame.draw.circle(surf, _lerp(_GOLD_PALE, _GOLD_BRIGHT, t), (ccx, y + h // 2), i)
    pygame.draw.circle(surf, _GOLD_DEEP, (ccx, y + h // 2), chip_r, 1)
    surf.blit(num, num.get_rect(center=(ccx, y + h // 2)))
    surf.blit(lbl, (ccx + chip_r + gap, y + (h - lbl.get_height()) // 2))


def main():
    surf = render_backdrop()
    ids = demo_ids(2)

    # Tuck the seal FULLY into the top-right corner wedge ABOVE the title. The
    # 'RUN SUMMARY' lettering occupies y48-64 with its right edge near x310, so
    # the seal — shrunk ~25% to R=20 and including its notched rim (~R*1.16) —
    # is centred high and tight enough that its entire body and rim sit clear of
    # the title (bottom of rim ~y42 < y48) and right of x312, in true dead space.
    R = 20
    cx = 360 - int(R * 1.16) - 2
    cy = int(R * 1.16) - 1

    _draw_seal(surf, cx, cy, R, ids[0])
    # '2 EARNED' pill in the clear band between the title bottom (~y66) and the
    # plaque top (y104), right-anchored to the edge — a genuine dead strip so it
    # occludes neither the title lettering nor the hero plaque.
    _draw_count_badge(surf, 360 - 6, 90, 2)

    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice", "corner-rosette")
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "round_2.png")
    pygame.image.save(surf, out)
    print(out)


if __name__ == "__main__":
    main()
