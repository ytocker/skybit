"""Marquise-cut gem badge exploration (iteration 2) for the v5 store card.

Swaps the locked 8-facet brilliant for a vertical navette (pointed oval): a
pointed-oval girdle with a table lens and seven crown facets value-stepped off
ONE top-left light. The pointed silhouette is the whole read — so both tips are
blunted to a 2-3 device-px flat to keep them from aliasing to a 1px thread. This
is a standalone review-sheet renderer; it never wires into the live card path.
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


def _tier_gf(base):
    # Gold radiates hardest, pale-common softest — glow weight tracks tier heat.
    if base == (214, 206, 230):
        return 0.55
    if base == (108, 188, 252):
        return 0.70
    if base == (194, 122, 248):
        return 0.85
    if base == (255, 202, 104):
        return 1.00
    return 0.85


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """A vertical marquise (navette): pointed top+bottom, widest at the sides,
    with a central table lens and seven crown facets shaded off ONE top-left
    light. Tips are blunted to a short flat so the pointed silhouette reads
    clean instead of fraying to a single aliased pixel."""
    gf = _tier_gf(base)
    t_dk = lerp_color(deep, base, 0.18)
    t_mid = base
    t_hi = lerp_color(base, WHITE, 0.55)
    t_table = lerp_color(base, WHITE, 0.50)
    warm = lerp_color(base, (255, 238, 206), 0.5)      # warm bounce toward light
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)

    def shade(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)
        f = (d + 1) / 2
        col = lerp_color(t_dk, t_mid, f * 2) if f < 0.5 else lerp_color(t_mid, t_hi, (f - 0.5) * 2)
        d2 = nx * 0.5 + ny * 0.5
        col = lerp_color(col, warm, 0.12 * max(0.0, (d2 + 1) / 2) * gf)
        return col

    # dark seat well FIRST so the gem reads on any ground
    seat_sz = r * 2 + sc.m(10)
    seat = pygame.Surface((seat_sz, seat_sz), pygame.SRCALPHA)
    off = r + sc.m(5)
    pygame.draw.circle(seat, (0, 0, 0, 175), (off, off), r + sc.m(4))
    pygame.draw.circle(seat, (*base, 100), (off, off), r + sc.m(4), max(1, sc.m(0.8)))
    surf.blit(seat, (cx - off, cy - off))

    # inner tier glow seated beneath the crown
    sc.soft_glow(surf, cx, cy, int(r * 0.5), base, int(80 * gf))

    # blunted pointed-oval outline vertices
    TFL = (cx - 2, cy - r + 1)
    TFR = (cx + 2, cy - r + 1)
    BFL = (cx - 2, cy + r - 1)
    BFR = (cx + 2, cy + r - 1)
    L = (cx - int(r * 0.50), cy)
    R = (cx + int(r * 0.50), cy)

    # table lens (inner diamond)
    tT = (cx, cy - int(r * 0.42))
    tR = (cx + int(r * 0.22), cy)
    tB = (cx, cy + int(r * 0.42))
    tL = (cx - int(r * 0.22), cy)

    def norm(a, b):
        # outer-edge midpoint direction from centre = that facet's face normal
        mx = (a[0] + b[0]) / 2 - cx
        my = (a[1] + b[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        return mx / ml, my / ml

    # seven facets, each shaded by its outer-edge normal
    facets = [
        ([TFL, tT, tL, L], norm(TFL, L)),        # upper-left — most lit
        ([TFR, R, tR, tT], norm(TFR, R)),        # upper-right
        ([BFR, tB, tR, R], norm(R, BFR)),        # lower-right — darkest
        ([BFL, L, tL, tB], norm(L, BFL)),        # lower-left
        ([TFL, TFR, tT], norm(TFL, TFR)),        # top tip — faces up, lit
        ([BFL, BFR, tB], norm(BFL, BFR)),        # bottom tip — faces down, dark
    ]
    for poly, (nx, ny) in facets:
        pygame.draw.polygon(surf, shade(nx, ny), poly)
    pygame.draw.polygon(surf, t_table, [tT, tR, tB, tL])

    # crown seams from tips + sides into the table
    for a, b in ((TFL, tT), (TFR, tT), (BFL, tB), (BFR, tB), (L, tL), (R, tR)):
        pygame.draw.line(surf, (*t_key, 190), a, b, max(1, sc.m(0.4)))

    # bright outer rim carries the pointed silhouette; straight segments between
    # the blunted tips read clean at this size
    rim_col = lerp_color(base, WHITE, 0.4)
    rim = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(rim, (*rim_col, 235), [TFL, TFR, R, BFR, BFL, L],
                        max(1, sc.m(0.5)))
    surf.blit(rim, (0, 0))

    # dual top-left specular (last, additive): a lens glint + a hot pip
    spec = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    lrx, lry = int(r * 0.14), int(r * 0.10)
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(200 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    spec.blit(lens, (cx - int(r * 0.24) - lrx, cy - int(r * 0.24) - lry))
    pr = int(r * 0.08)
    pygame.draw.circle(spec, (255, 255, 255, 255),
                       (cx - int(r * 0.32), cy - int(r * 0.30)), max(1, pr))
    surf.blit(spec, (0, 0), special_flags=pygame.BLEND_ADD)


# ── render sheet ──────────────────────────────────────────────────────────────
RARITY_TIERS = [
    ("common",    (214, 206, 230), (78,  74, 112)),
    ("rare",      (108, 188, 252), (24,  78, 142)),
    ("epic",      (194, 122, 248), (80,  34, 126)),
    ("legendary", (255, 202, 104), (150, 92,  22)),
]
SID_PRIMARY = "skin_mummy"
SID_SECONDARY = "skin_kitsune"
CARD_W = sc.CARD_W * sc.SS
GEM_R = sc.m(sc.GEM_R + 3)

sc.facet_gem = my_facet_gem   # BEFORE draw_card so the card uses the marquise cut


def render_card(sid):
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((CARD_W, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       CARD_W - 2 * sc.m(sc._INSET),
                       ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, equipped=False, secret=False,
                 variant=sc.PRICE_VARIANT)
    return surf


def render_gem(base, deep):
    sz = (GEM_R + 4) * 2
    g = pygame.Surface((sz, sz), pygame.SRCALPHA)
    my_facet_gem(g, sz // 2, sz // 2, GEM_R, base, deep)
    return g


def main():
    pad, gap = 28, 24
    bg = (8, 8, 20)

    header_font = hud_font(30, True)
    label_font = hud_font(20, True)
    header = header_font.render("gem badge — marquise-cut r1", True, (236, 232, 246))

    cards = [render_card(SID_PRIMARY), render_card(SID_SECONDARY)]
    cw, chh = cards[0].get_size()

    zoom = 8
    gems = [(name, render_gem(b, d)) for name, b, d in RARITY_TIERS]
    gsz = gems[0][1].get_size()[0]
    zsz = gsz * zoom

    row1_w = cw * 2 + gap
    row2_w = zsz * len(gems) + gap * (len(gems) - 1)
    content_w = max(row1_w, row2_w, header.get_width())
    canvas_w = content_w + pad * 2

    header_h = header.get_height()
    label_h = label_font.get_height()
    canvas_h = pad + header_h + gap + chh + gap + zsz + 8 + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    canvas.fill(bg)

    y = pad
    canvas.blit(header, (pad, y))
    y += header_h + gap

    # Row 1 — two full cards using the marquise crest gem
    x = pad + (content_w - row1_w) // 2
    for card in cards:
        canvas.blit(card, (x, y))
        x += cw + gap
    y += chh + gap

    # Row 2 — 8x zoomed 4-tier gem strip with labels
    x = pad + (content_w - row2_w) // 2
    for name, g in gems:
        z = pygame.transform.scale(g, (zsz, zsz))
        canvas.blit(z, (x, y))
        lab = label_font.render(name, True, (222, 218, 234))
        canvas.blit(lab, (x + (zsz - lab.get_width()) // 2, y + zsz + 8))
        x += zsz + gap

    out = "/home/user/skybit/docs/store_card_v5_gem_badge_r2/marquise-cut/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
