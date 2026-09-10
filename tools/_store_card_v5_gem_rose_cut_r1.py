"""Round-1 render for the rose-cut gem badge concept.

Standalone author sheet: monkey-patches store_cards.facet_gem with the rose-cut
cut (six crown triangles fanning from a tiny hex table) and lays two live cards
above an 8x tier strip. Kept out of the shipped bundle (docs/ + tools/ are not
staged by the pygbag workflow) so it can't bloat the .apk.
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


def _sat(base):
    """HSV-style saturation: common skins are pale (low sat), rare hues pop."""
    mx, mn = max(base), min(base)
    return 0.0 if mx == 0 else (mx - mn) / mx


def _is_common(base):
    # The pale common palette (or any near-grey hue) skips the extra sheen so
    # its low-contrast facets don't get washed out by a bright white arc.
    return base == (214, 206, 230) or _sat(base) < 0.15


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Rose-cut: a plain circular girdle, but the interior reads as a CUT stone
    — six crown triangles fan from a tiny central hex table to the girdle edge,
    value-stepped off one top-left light. Not a dome; unmistakably faceted."""
    # Mystery owns a red hue so it never reads as a real tier colour.
    if mystery:
        base, deep = (232, 96, 96), (120, 24, 24)

    hi = lerp_color(base, WHITE, 0.5)
    lo = lerp_color(base, deep, 0.6)
    dark = lerp_color(deep, NEAR_BLACK, 0.4)
    # Rarer, more saturated hues glow harder; pale common stays subtle.
    gf = max(0.55, min(1.0, 0.45 + _sat(base)))

    # ── Layer 0: additive glow bloom, brightest at centre ────────────────────
    gr = int(r * 1.1)
    glow = pygame.Surface((gr * 2 + 2, gr * 2 + 2), pygame.SRCALPHA)
    gc = gr + 1
    for rr in range(gr, 0, -1):
        a = int(58 * gf * (1 - rr / gr))
        if a > 0:
            pygame.draw.circle(glow, (*base, a), (gc, gc), rr)
    surf.blit(glow, (cx - gc, cy - gc), special_flags=pygame.BLEND_ADD)

    # ── Layer 1: girdle disc — the plain circular profile ────────────────────
    pygame.draw.circle(surf, lo, (cx, cy), r)

    # Hex table radius, floored so tiny gems never collapse to a dot.
    tr = max(0.22 * r, 3.0, float(int(0.22 * r)))

    def pt(rad, deg):
        a = math.radians(deg)
        return (cx + rad * math.cos(a), cy + rad * math.sin(a))

    lx, ly = -0.7071, -0.7071                       # top-left light unit vector

    # ── Layer 2: six crown triangles, dot-product value-stepped ──────────────
    for k in range(6):
        v1 = pt(tr, 60 * k + 30)
        v2 = pt(tr, 60 * k + 90)
        apex = pt(r, 60 * k + 60)
        ax, ay = math.cos(math.radians(60 * k + 60)), math.sin(math.radians(60 * k + 60))
        d = ax * lx + ay * ly                        # -1 away .. 1 toward light
        f = (d + 1) / 2                              # 0 dark .. 1 lit
        col = lerp_color(lerp_color(dark, lo, min(1.0, f * 2)),
                         hi, max(0.0, (f - 0.5) * 2))
        pygame.draw.polygon(surf, col, [v1, v2, apex])

    # ── Layer 3: central hex table, the brightest flat ───────────────────────
    table = [pt(tr, 60 * k + 30) for k in range(6)]
    pygame.draw.polygon(surf, hi, table)

    # ── Layer 4: crown seam strokes ──────────────────────────────────────────
    for k in range(6):
        pygame.draw.line(surf, dark, pt(tr, 60 * k + 30), pt(r, 60 * k + 60),
                         max(1, sc.m(0.8)))

    # ── Layer 5: girdle rim keyline ──────────────────────────────────────────
    pygame.draw.circle(surf, lerp_color(lo, dark, 0.4), (cx, cy), r, max(1, sc.m(1)))

    # ── Layer 6: short upper-left specular sheen (skip pale common) ───────────
    if not _is_common(base):
        hw, hh = max(2, int(r * 0.5)), max(1, int(r * 0.28))
        sheen = pygame.Surface((hw * 2 + 2, hh * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(sheen, (*WHITE, int(130 * gf)),
                            (1, 1, hw * 2, hh * 2))
        hx, hy = cx - 0.3 * r, cy - 0.3 * r
        surf.blit(sheen, (hx - hw - 1, hy - hh - 1))


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
    d = (GEM_R + margin) * 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    my_facet_gem(g, d // 2, d // 2, GEM_R, base, deep, False)
    return g


def main():
    pad = 24
    gap = 20
    label_f = hud_font(20)
    head_f = hud_font(30)

    cards = [render_card(SID_PRIMARY), render_card(SID_SECONDARY)]
    row1_w = sum(c.get_width() for c in cards) + gap
    row1_h = max(c.get_height() for c in cards)

    scale = 8
    gems = [(name, pygame.transform.scale(render_gem(b, d),
                                          (render_gem(b, d).get_width() * scale,
                                           render_gem(b, d).get_height() * scale)))
            for (name, b, d) in RARITY_TIERS]
    strip_gap = 28
    row2_w = sum(g.get_width() for _, g in gems) + strip_gap * (len(gems) - 1)
    row2_h = max(g.get_height() for _, g in gems)
    label_h = 30

    head_h = 46
    content_w = max(row1_w, row2_w)
    W = content_w + pad * 2
    H = pad + head_h + row1_h + gap * 2 + row2_h + label_h + pad
    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    head = head_f.render("gem badge — rose-cut r1", True, (235, 235, 245))
    canvas.blit(head, (pad, pad))

    y = pad + head_h
    x = (W - row1_w) // 2
    for c in cards:
        canvas.blit(c, (x, y))
        x += c.get_width() + gap

    y += row1_h + gap * 2
    x = (W - row2_w) // 2
    for name, g in gems:
        canvas.blit(g, (x, y))
        lab = label_f.render(name, True, (210, 210, 225))
        canvas.blit(lab, (x + (g.get_width() - lab.get_width()) // 2, y + g.get_height() + 6))
        x += g.get_width() + strip_gap

    out = "/home/user/skybit/docs/store_card_v5_gem_badge/rose-cut/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
