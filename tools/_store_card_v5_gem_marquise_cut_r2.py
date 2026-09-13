"""Marquise-cut gem badge exploration (iteration 2) for the v5 store card.

A vertical navette (pointed oval): a pointed-oval girdle with a table lens and
six crown facets value-stepped off ONE top-left light. The pointed silhouette
is the whole read, so both tips stay blunted to a 2px flat to keep them from
aliasing to a 1px thread.

r2 rework, driven by art-direction notes: the specular now runs along the gem's
LONG axis (a vertical hall-of-light streak, not a horizontal blob); the crown
facets sit on a clean 4-step NW->SE value ramp with LR as the single deepest
shadow corner; tier brightness is anchored to gf so legendary reads brightest;
and the seat is an oval halo hugging the navette's tall aspect. Standalone
review-sheet renderer — it never wires into the live card path.
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


def shade(nx, ny, base, deep, gf):
    # Common's shadow stop is deepened so its dark facets keep structure instead
    # of flattening into the near-white base; every other tier keeps the 0.18 lift.
    dk_stop = 0.12 if base == (214, 206, 230) else 0.18
    t_dk = lerp_color(deep, base, dk_stop)
    t_mid = base
    # gf lifts legendary's highlight past common's near-white base so tier heat,
    # not base lightness, decides which gem reads brightest.
    t_hi = lerp_color(base, WHITE, 0.40 + 0.22 * gf)
    warm = lerp_color(base, (255, 200, 120), 0.4)
    d = nx * (-0.7071) + ny * (-0.7071)
    f = (d + 1) / 2
    if f < 0.5:
        col = lerp_color(t_dk, t_mid, f * 2)
    else:
        col = lerp_color(t_mid, t_hi, (f - 0.5) * 2)
    # reflected warm pass toward the light
    d2 = nx * 0.5 + ny * 0.5
    f2 = max(0.0, (d2 + 1) / 2)
    col = lerp_color(col, warm, 0.14 * f2 * gf)
    return col


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """A vertical marquise (navette): pointed top+bottom, widest at the sides,
    with a central table lens and six crown facets shaded off ONE top-left
    light. Tips are blunted to a short flat so the pointed silhouette reads clean
    instead of fraying to a single aliased pixel."""
    gf = _tier_gf(base)
    t_table = lerp_color(base, WHITE, 0.34 + 0.18 * gf)
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)

    # Oval seat FIRST so the gem seats on any ground — half-axes chosen to hug
    # the navette's 2:1 aspect and leave a soft shadow halo past the girdle.
    ehw = int(r * 1.15)
    ehh = int(r * 1.30)
    seat = pygame.Surface((ehw * 2 + sc.m(6), ehh * 2 + sc.m(6)), pygame.SRCALPHA)
    ox, oy = seat.get_width() // 2, seat.get_height() // 2
    pygame.draw.ellipse(seat, (0, 0, 0, 175), (ox - ehw, oy - ehh, ehw * 2, ehh * 2))
    pygame.draw.ellipse(seat, (*base, 100),
                        (ox - ehw - 1, oy - ehh - 1, (ehw + 1) * 2, (ehh + 1) * 2),
                        max(1, sc.m(0.8)))
    surf.blit(seat, (cx - ox, cy - oy))

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

    UL = ([TFL, tT, tL, L], norm(TFL, L))          # faces the light — brightest
    UR = ([TFR, R, tR, tT], norm(TFR, R))          # a step down from UL
    LR = ([BFR, tB, tR, R], norm(R, BFR))          # shadow corner — darkest
    LL = ([BFL, L, tL, tB], norm(L, BFL))          # mid-dark, pulled below UL
    TOP = ([TFL, TFR, tT], norm(TFL, TFR))         # top tip — faces up, lit
    BOT = ([BFL, BFR, tB], norm(BFL, BFR))         # bottom tip — pushed to LR's dark

    # `extra` pulls a facet toward `deep` AFTER the dot-product so the ramp reads
    # as four distinct value steps (UL > UR > LL > LR) instead of two bright pairs.
    for poly, (nx, ny), extra in (
        (*UL, 0.0), (*UR, 0.0), (*LR, 0.0),
        (*LL, 0.15), (*TOP, 0.0), (*BOT, 0.15),
    ):
        col = shade(nx, ny, base, deep, gf)
        if extra:
            col = lerp_color(col, deep, extra)
        pygame.draw.polygon(surf, col, poly)
    pygame.draw.polygon(surf, t_table, [tT, tR, tB, tL])

    # crown seams from tips + sides into the table
    for a, b in ((TFL, tT), (TFR, tT), (BFL, tB), (BFR, tB), (L, tL), (R, tR)):
        pygame.draw.line(surf, (*t_key, 190), a, b, max(1, sc.m(0.4)))

    # hue-tinted bright rim LAST — carries the pointed silhouette clean at 1x
    rim_col = lerp_color(base, WHITE, 0.42)
    rim = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(rim, (*rim_col, 235), [TFL, TFR, R, BFR, BFL, L],
                        max(1, sc.m(0.5)))
    surf.blit(rim, (0, 0))

    # top-left specular (last, additive) runs along the LONG axis: a tall lens
    # streak + a hot pip so it reads as a vertical hall-of-light, never a blob.
    spec = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    lrx = int(r * (0.08 + 0.04 * gf))
    lry = int(r * (0.18 + 0.06 * gf))
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(185 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    lcx = cx - int(r * 0.12)
    lcy = cy - int(r * 0.22)
    spec.blit(lens, (lcx - lrx, lcy - lry))
    prx = max(1, int(r * 0.05))
    pry = max(1, int(r * 0.04))
    pygame.draw.ellipse(spec, (255, 255, 255, 220),
                        (cx - int(r * 0.14) - prx, cy - int(r * 0.28) - pry,
                         prx * 2, pry * 2))
    surf.blit(spec, (0, 0), special_flags=pygame.BLEND_ADD)


# ── render sheet ──────────────────────────────────────────────────────────────
RARITY_TIERS = [
    ("common",    (214, 206, 230), (78,  74, 112)),
    ("rare",      (108, 188, 252), (24,  78, 142)),
    ("epic",      (194, 122, 248), (80,  34, 126)),
    ("legendary", (255, 202, 104), (150, 92,  22)),
]
SID_PRIMARY = "skin_mummy"        # EPIC
SID_SECONDARY = "skin_kitsune"    # LEGENDARY
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
    header = header_font.render("gem badge — marquise-cut r2", True, (236, 232, 246))

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

    out = "/home/user/skybit/docs/store_card_v5_gem_badge_r2/marquise-cut/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
