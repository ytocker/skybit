"""Round-1 render sheet for the `radiant-brilliant` gem badge concept.

Monkey-patches store_cards.facet_gem with a top-down round-brilliant cut
(octagonal table ringed by alternating kite/star facets) and renders two
production cards plus a magnified 4-tier gem strip. Review-only; never wired
into the live card path.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font as hud_font

RARITY_TIERS = [
    ("common",    (214, 206, 230), (78,  74, 112)),
    ("rare",      (108, 188, 252), (24,  78, 142)),
    ("epic",      (194, 122, 248), (80,  34, 126)),
    ("legendary", (255, 202, 104), (150, 92,  22)),
]
SID_PRIMARY   = "skin_mummy"    # EPIC
SID_SECONDARY = "skin_kitsune"  # LEGENDARY
CARD_W = sc.CARD_W * sc.SS   # 324
GEM_R  = sc.m(sc.GEM_R + 3)  # 22 device px

_GF = {
    (214, 206, 230): 0.55,   # common
    (108, 188, 252): 0.70,   # rare
    (194, 122, 248): 0.85,   # epic
    (255, 202, 104): 1.00,   # legendary
}


def _pt(cx, cy, r, f, deg):
    """Polar → screen: radius f*r at `deg` degrees (screen y grows downward, so
    the (-,-) light vector still reads as the upper-left flash)."""
    a = math.radians(deg)
    return (cx + f * r * math.cos(a), cy + f * r * math.sin(a))


def _add_pip(surf, cx, cy, rx, ry, alpha):
    """Additive white catch-light ellipse — lifts the stone toward a glow rather
    than painting an opaque slab that would flatten the table."""
    pw, ph = int(rx * 2) + 2, int(ry * 2) + 2
    pip = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.ellipse(pip, (255, 255, 255, alpha), (1, 1, int(rx * 2), int(ry * 2)))
    surf.blit(pip, (int(cx - rx), int(cy - ry)), special_flags=pygame.BLEND_ADD)


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    body = base if not mystery else (244, 96, 96)
    dp = deep if not mystery else (120, 22, 26)
    # Tier factor drives every additive intensity so higher tiers flash hotter;
    # unknown hues (mystery) fall back to a mid luminance read.
    gf = _GF.get(tuple(body), sum(body) / (255 * 3))

    hi = lerp_color(body, WHITE, 0.5)
    mid = body
    lo = lerp_color(body, dp, 0.6)
    dark = lerp_color(dp, NEAR_BLACK, 0.4)

    L = (-0.7071, -0.7071)   # top-left key light

    # Layer 0 — additive inner glow: a radial base-hue lift, hottest at centre.
    R = int(r * 1.1)
    if R > 0:
        c = R + 1
        glow = pygame.Surface((c * 2, c * 2), pygame.SRCALPHA)
        for i in range(R, 0, -1):
            a = int(60 * gf * (1 - i / R))
            pygame.draw.circle(glow, (body[0], body[1], body[2], a), (c, c), i)
        surf.blit(glow, (cx - c, cy - c), special_flags=pygame.BLEND_ADD)

    # Layer 1 — girdle disc: the deep seat the crown facets sit on.
    pygame.draw.circle(surf, lo, (cx, cy), r)

    # Layer 2 — eight crown KITE facets, value-stepped by facing vs the key light.
    for k in range(8):
        bis = 45 * k + 22.5
        tcorner = _pt(cx, cy, r, 0.34, bis)
        ga = _pt(cx, cy, r, 1.0, 45 * k)
        seam = _pt(cx, cy, r, 0.62, bis)
        gb = _pt(cx, cy, r, 1.0, 45 * k + 45)
        d = math.cos(math.radians(bis)) * L[0] + math.sin(math.radians(bis)) * L[1]
        t = (1 - d) / 2                       # 0 fully lit .. 1 fully shaded
        if d >= 0:
            col = lerp_color(mid, hi, 1 - t)
        else:
            col = lerp_color(mid, dark, t)
        pygame.draw.polygon(surf, col, [tcorner, ga, seam, gb])

    # Layer 3 — eight STAR facets between the kites. They vanish at the badge's
    # production radius, so skip them cleanly rather than draw sub-pixel slivers.
    if r >= 24:
        for k in range(8):
            p0 = _pt(cx, cy, r, 0.34, 45 * k + 22.5)
            apex = _pt(cx, cy, r, 1.0, 45 * k + 22.5)
            p1 = _pt(cx, cy, r, 0.34, 45 * (k + 1) + 22.5)
            pygame.draw.polygon(surf, lerp_color(mid, hi, 0.3), [p0, apex, p1])

    # Layer 4 — octagonal TABLE: the flat top, brightest plane.
    table = [_pt(cx, cy, r, 0.34, 45 * k + 22.5) for k in range(8)]
    pygame.draw.polygon(surf, hi, table)

    # Layer 5 — facet seam strokes + a bright hue-tinted RIM ring. The ring
    # REPLACES a dark keyline so the stone glows at its edge instead of looking
    # inked on.
    for k in range(8):
        tcorner = _pt(cx, cy, r, 0.34, 45 * k + 22.5)
        ga = _pt(cx, cy, r, 1.0, 45 * k)
        gb = _pt(cx, cy, r, 1.0, 45 * k + 45)
        pygame.draw.line(surf, dark, tcorner, ga, max(1, sc.m(1)))
        pygame.draw.line(surf, dark, tcorner, gb, max(1, sc.m(1)))
    pygame.draw.circle(surf, lerp_color(base, WHITE, 0.4), (cx, cy), r, max(1, sc.m(1)))

    # Layer 6 — specular catch-light on the upper-left table (+ a legendary pip).
    pr = max(3, int(r * 0.22))
    _add_pip(surf, cx - r * 0.16, cy - r * 0.16, pr * 1.35, pr, int(170 * gf))
    if tuple(body) == (255, 202, 104):
        _add_pip(surf, cx + r * 0.18, cy - r * 0.08, pr * 0.7, pr * 0.55, 120)


sc.facet_gem = my_facet_gem   # monkey-patch before any draw_card call


def render_card(sid):
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((CARD_W, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       CARD_W - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, False, False, sc.PRICE_VARIANT)
    return surf


def render_gem(base, deep):
    margin = 4
    size = (GEM_R + margin) * 2
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    my_facet_gem(g, size // 2, size // 2, GEM_R, base, deep)
    return g


def main():
    bg = (8, 8, 20)
    pad = 28
    gap = 24

    card_a = render_card(SID_PRIMARY)
    card_b = render_card(SID_SECONDARY)
    cw, chh = card_a.get_size()

    strip_scale = 8
    gems = [(name, pygame.transform.scale(render_gem(base, deep),
                                          ((GEM_R + 4) * 2 * strip_scale,) * 2))
            for name, base, deep in RARITY_TIERS]
    gw = gems[0][1].get_width()
    gem_gap = 40

    header_f = hud_font(30, True)
    label_f = hud_font(22, True)
    header = header_f.render("gem badge — radiant-brilliant r1", True, (232, 228, 246))

    row1_w = cw * 2 + gap
    row2_w = gw * len(gems) + gem_gap * (len(gems) - 1)
    content_w = max(header.get_width(), row1_w, row2_w)
    canvas_w = content_w + pad * 2

    header_h = header.get_height()
    label_h = label_f.get_height()
    canvas_h = pad + header_h + gap + chh + gap + gw + 8 + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(bg)

    y = pad
    canvas.blit(header, ((canvas_w - header.get_width()) // 2, y))
    y += header_h + gap

    x0 = (canvas_w - row1_w) // 2
    canvas.blit(card_a, (x0, y))
    canvas.blit(card_b, (x0 + cw + gap, y))
    y += chh + gap

    x0 = (canvas_w - row2_w) // 2
    for name, gimg in gems:
        canvas.blit(gimg, (x0, y))
        lbl = label_f.render(name, True, (208, 204, 224))
        canvas.blit(lbl, (x0 + (gw - lbl.get_width()) // 2, y + gw + 8))
        x0 += gw + gem_gap

    out = "/home/user/skybit/docs/store_card_v5_gem_badge/radiant-brilliant/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
