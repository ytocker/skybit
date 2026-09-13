"""Round-1 render sheet for the `star-gem` crest-badge concept.

A monkey-patched replacement for game.store_cards.facet_gem that draws a
6-point star cut whose read hinges on hard-dark valleys that stay locked
across every tier — only the glow and the lit arm facets modulate per tier.
Renders two full v5 cards plus a 4-tier gem strip so the small-scale read is
judged the way the card actually shows it.
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
SID_PRIMARY = "skin_mummy"      # EPIC
SID_SECONDARY = "skin_kitsune"  # LEGENDARY
CARD_W = sc.CARD_W * sc.SS   # 324
GEM_R = sc.m(sc.GEM_R + 3)   # 22 device px

L = (-0.7071, -0.7071)          # top-left key light unit vector


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """A 6-point star cut. Six lit arm facets radiate to a central hex table;
    between them sit six notch valleys whose fill is FIXED dark regardless of
    tier — the invariant valleys are what let the star silhouette read at 22px.
    Mystery claims red so it visibly owns no tier."""
    if mystery:
        base, deep = (228, 72, 72), (120, 22, 22)

    hi = lerp_color(base, WHITE, 0.5)
    lo = lerp_color(base, deep, 0.6)
    # The notch + stroke recipe is tier-invariant: this is the whole read.
    dark = lerp_color(deep, NEAR_BLACK, 0.4)

    # Brighter tiers throw more light; gf modulates ONLY glow + arm lift so the
    # dark valleys stay identical across the ladder.
    gf = max(0.75, min(1.15, _luma(base) / 190.0))

    def pt(radius, deg):
        a = math.radians(deg)
        return (cx + radius * math.cos(a), cy + radius * math.sin(a))

    # Table verts + valleys share angle 60k so each table VERT points at a
    # valley; peaks sit at 60k+30 over each table EDGE midpoint (point-up star).
    peaks = [pt(r, 60 * k + 30) for k in range(6)]
    valleys = [pt(0.5 * r, 60 * k) for k in range(6)]
    table = [pt(0.3 * r, 60 * k) for k in range(6)]

    # --- Layer 0: additive tier glow, brightest at centre ---------------------
    gr = int(r * 1.1)
    pad = 2
    glow = pygame.Surface((gr * 2 + pad * 2, gr * 2 + pad * 2), pygame.SRCALPHA)
    gc = gr + pad
    for i in range(gr, 0, -1):
        a = int(60 * gf * (1.0 - i / gr))
        if a > 0:
            pygame.draw.circle(glow, (*base, a), (gc, gc), i)
    surf.blit(glow, (cx - gc, cy - gc), special_flags=pygame.BLEND_RGBA_ADD)

    # --- Layer 1: 12-vertex star body (valley, peak, valley, peak ...) --------
    body = []
    for k in range(6):
        body.append(valleys[k])       # 60k
        body.append(peaks[k])         # 60k+30
    pygame.draw.polygon(surf, lo, body)

    # --- Layer 2: six lit arm (peak) facets -----------------------------------
    # Triangle from table edge (verts 60k, 60k+60) up to the peak at 60k+30.
    for k in range(6):
        a = table[k]
        b = table[(k + 1) % 6]
        apex = peaks[k]
        dvec = math.cos(math.radians(60 * k + 30)) * L[0] + \
            math.sin(math.radians(60 * k + 30)) * L[1]
        f = (dvec + 1) / 2                       # 0 (away) .. 1 (into light)
        col = lerp_color(lo, hi, min(1.0, f * gf))
        pygame.draw.polygon(surf, col, [a, b, apex])

    # --- Layer 3: six valley (notch) facets — FIXED dark, tier-invariant ------
    # Kite around each valley, bounded by the two flanking arm-facet edges that
    # both meet at table vert k.
    for k in range(6):
        quad = [table[k], peaks[(k - 1) % 6], valleys[k], peaks[k]]
        pygame.draw.polygon(surf, dark, quad)

    # --- Layer 4: central hex table -------------------------------------------
    pygame.draw.polygon(surf, hi, table)

    # --- Layer 5: 12-point star silhouette stroke (locked dark) ---------------
    pygame.draw.polygon(surf, dark, body, max(1, sc.m(1)))


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
    size = GEM_R * 2 + margin * 2
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    my_facet_gem(g, size // 2, size // 2, GEM_R, base, deep, False)
    return g


def main():
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge/star-gem"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    pad = 24
    gap = 24
    card_p = render_card(SID_PRIMARY)
    card_s = render_card(SID_SECONDARY)
    cw, chh = card_p.get_size()

    scale = 8
    gem_px = (GEM_R * 2 + 8) * scale
    strip_w = gem_px * 4 + gap * 3

    header_h = 40
    row1_w = cw * 2 + gap
    row1_h = chh
    label_h = 26
    row2_h = gem_px + label_h

    content_w = max(row1_w, strip_w)
    W = content_w + pad * 2
    H = header_h + row1_h + gap + row2_h + pad * 2

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    # header
    hf = hud_font(26)
    htxt = hf.render("gem badge — star-gem r1", True, (236, 232, 248))
    canvas.blit(htxt, (pad, pad // 2))

    y0 = pad + header_h
    # row 1: two full cards centred
    row1_x = (W - row1_w) // 2
    canvas.blit(card_p, (row1_x, y0))
    canvas.blit(card_s, (row1_x + cw + gap, y0))

    lf = hud_font(18)
    for lbl, sid_x in (("EPIC · skin_mummy", row1_x),
                       ("LEGENDARY · skin_kitsune", row1_x + cw + gap)):
        t = lf.render(lbl, True, (150, 150, 176))
        canvas.blit(t, (sid_x + (cw - t.get_width()) // 2, y0 + chh - 20))

    # row 2: 4-tier gem strip scaled 8x
    y1 = y0 + row1_h + gap
    strip_x = (W - strip_w) // 2
    for i, (name, base, deep) in enumerate(RARITY_TIERS):
        gem = render_gem(base, deep)
        big = pygame.transform.scale(gem, (gem_px, gem_px))
        gx = strip_x + i * (gem_px + gap)
        canvas.blit(big, (gx, y1))
        t = lf.render(name, True, (210, 206, 228))
        canvas.blit(t, (gx + (gem_px - t.get_width()) // 2, y1 + gem_px + 4))

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
