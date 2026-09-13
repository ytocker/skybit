"""halo-orb gem badge exploration — round 1 render.

A smooth spherical cabochon that reads as a glowing pearl/orb: offset
specular, tight halo ring, 4-arm sparkle cross. No angular facets. Legibility
at 22px is the whole point, so the sparkle arms and specular carry HARD minimum
sizes. Rendered off a monkey-patched facet_gem so the production card geometry
stays untouched — the badge is the only thing under test.
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


def _gf(base):
    # Tier factor by luminance so brighter/warmer tiers glow harder — the
    # legendary gold pushes to a full 1.0, common dusk-lilac sits near 0.55.
    return 0.55 + min(1.0, sum(base) / (255 * 3)) * 0.45


def _is_legendary(base, deep):
    # Only the top tier earns the second sparkle. Detect by the warm-gold hue
    # rather than threading tier metadata through the locked signature.
    return base[0] > 230 and base[1] > 170 and base[2] < 150


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """halo-orb: a glowing pearl/orb badge. Offset radial body, rim darkening,
    a tight halo ring, an offset specular, and a 4-arm sparkle cross whose arms
    hold a hard minimum width so they survive at 22px. Legendary gets a second
    smaller sparkle lower-right."""
    if mystery:
        # Mystery owns red so it visibly claims NO tier.
        base, deep = (232, 74, 74), (120, 20, 20)
    gf = _gf(base)

    hi   = lerp_color(base, WHITE, 0.5)
    lo   = lerp_color(base, deep, 0.6)
    dark = lerp_color(deep, NEAR_BLACK, 0.4)

    # --- Layer 0: outer glow (HARD CAPS keep the footprint tight) ------------
    gr = int(r * 1.1)
    peak = min(60, int(60 * gf))
    glow = pygame.Surface((gr * 2, gr * 2), pygame.SRCALPHA)
    layers = 10
    for i in range(layers, 0, -1):
        rr = int(gr * i / layers)
        a = int(peak * (1 - i / layers))
        if rr > 0 and a > 0:
            pygame.draw.circle(glow, (*hi, a), (gr, gr), rr)
    surf.blit(glow, (cx - gr, cy - gr), special_flags=pygame.BLEND_ADD)

    # --- Layer 1: orb body — smooth concentric rings around an offset light --
    # Highlight centre sits upper-left so the sphere reads as lit from there.
    hcx, hcy = cx - int(0.3 * r), cy - int(0.3 * r)
    for rr in range(r, 0, -1):
        # Sample colour by this ring's farthest-from-light point so the terminator
        # falls on the lower-right, then deepen sharply in the outer 15%.
        d = min(1.0, (rr + math.hypot(cx - hcx, cy - hcy)) / r)
        col = lerp_color(hi, lo, d)
        if rr > r * 0.85:
            k = (rr - r * 0.85) / (r * 0.15)
            col = lerp_color(col, dark, min(1.0, k))
        pygame.draw.circle(surf, col, (hcx, hcy), rr)

    # --- Layer 2: rim darkening — a crisp seat against any ground ------------
    pygame.draw.circle(surf, lerp_color(lo, dark, 0.5), (cx, cy), r, max(1, sc.m(1.5)))

    # --- Layer 3: halo ring — a thin bright band just inside the rim ---------
    halo = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(halo, (*hi, int(90 * gf)), (r + 2, r + 2),
                       int(r * 0.9), max(1, sc.m(1)))
    surf.blit(halo, (cx - r - 2, cy - r - 2))

    # --- Layer 4: specular — a hot offset pearl glint ------------------------
    sax, say = max(3, int(r * 0.25)), max(2, int(r * 0.18))
    spec = pygame.Surface((sax * 2 + 2, say * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(spec, (255, 255, 255, int(200 * gf)),
                        (1, 1, sax * 2, say * 2))
    scx, scy = cx - int(0.35 * r), cy - int(0.35 * r)
    surf.blit(spec, (scx - sax - 1, scy - say - 1), special_flags=pygame.BLEND_ADD)

    # --- Layer 5: sparkle cross — arms hold a hard min width at any size ------
    def _sparkle(ox, oy, length):
        aw = max(2, sc.m(1))
        pygame.draw.line(surf, WHITE, (ox - length, oy), (ox + length, oy), aw)
        pygame.draw.line(surf, WHITE, (ox, oy - length), (ox, oy + length), aw)

    arm = int(r * 0.5)
    spark = pygame.Surface(surf.get_size(), pygame.SRCALPHA)

    def _sparkle_on(dst, ox, oy, length):
        aw = max(2, sc.m(1))
        pygame.draw.line(dst, (255, 255, 255, int(255 * gf)),
                         (ox - length, oy), (ox + length, oy), aw)
        pygame.draw.line(dst, (255, 255, 255, int(255 * gf)),
                         (ox, oy - length), (ox, oy + length), aw)

    _sparkle_on(spark, scx, scy, arm)
    if _is_legendary(base, deep):
        _sparkle_on(spark, cx + int(0.35 * r), cy + int(0.32 * r), int(arm * 0.6))
    surf.blit(spark, (0, 0), special_flags=pygame.BLEND_ADD)


sc.facet_gem = my_facet_gem   # monkey-patch before any draw_card call


def render_card(sid):
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((CARD_W, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       CARD_W - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, False, False, sc.PRICE_VARIANT)
    return surf


def render_gem(base, deep):
    pad = GEM_R + 4
    g = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    my_facet_gem(g, pad, pad, GEM_R, base, deep, mystery=False)
    return g


def main():
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge/halo-orb"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    margin = 24
    gap = 20
    header_h = 40

    card_a = render_card(SID_PRIMARY)      # epic
    card_b = render_card(SID_SECONDARY)    # legendary
    cw, chh = card_a.get_size()

    row1_y = header_h + margin
    row1_h = chh

    # Row 2 — 8x gem strip
    gems = [render_gem(b, d) for _, b, d in RARITY_TIERS]
    gw = gems[0].get_width() * 8
    label_h = 22
    strip_gap = 28
    row2_y = row1_y + row1_h + margin + 20
    row2_h = gw + label_h

    total_gw = gw * 4 + strip_gap * 3
    canvas_w = max(margin * 2 + cw * 2 + gap, margin * 2 + total_gw)
    canvas_h = row2_y + row2_h + margin

    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    canvas.fill((8, 8, 20, 255))

    # Header
    hf = hud_font(26)
    htx = hf.render("gem badge — halo-orb r1", True, (236, 236, 248))
    canvas.blit(htx, (margin, margin // 2 + 4))

    # Row 1 — full cards
    row1_x = (canvas_w - (cw * 2 + gap)) // 2
    canvas.blit(card_a, (row1_x, row1_y))
    canvas.blit(card_b, (row1_x + cw + gap, row1_y))

    lf = hud_font(18)
    for i, (label, x) in enumerate((("EPIC — skin_mummy", row1_x),
                                    ("LEGENDARY — skin_kitsune", row1_x + cw + gap))):
        tx = lf.render(label, True, (200, 200, 220))
        canvas.blit(tx, (x + (cw - tx.get_width()) // 2, row1_y - 20))

    # Row 2 — gem strip 8x
    row2_x = (canvas_w - total_gw) // 2
    sf = hud_font(18)
    for i, ((name, _, _), gem) in enumerate(zip(RARITY_TIERS, gems)):
        big = pygame.transform.scale(gem, (gem.get_width() * 8, gem.get_height() * 8))
        gx = row2_x + i * (gw + strip_gap)
        canvas.blit(big, (gx, row2_y))
        tx = sf.render(name, True, (206, 206, 226))
        canvas.blit(tx, (gx + (gw - tx.get_width()) // 2, row2_y + gw + 4))

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
