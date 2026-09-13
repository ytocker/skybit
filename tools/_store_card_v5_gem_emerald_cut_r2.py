"""Round-2 render sheet for the emerald-cut gem badge concept.

Monkey-patches store_cards.facet_gem with a rectangular step cut — a stretched
octagon (taller than wide) drawn NOT as radiating facets but as concentric
step bands whose value falls INTO the stone: a dark seat rim, one bright flash
ring, a medium ring, then a dark table well at centre. That inverted "looking
down into a box" value curve — plus a thin horizontal step flash and a tight
left/right edge bias standing in for a 3/4-view key — is what makes a step cut
read differently from a brilliant. Renders it on two full v5 cards plus an 8x
zoomed 4-tier strip. Review-only tooling — never imported by the game.
"""
import os
import sys

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
CARD_W = sc.CARD_W * sc.SS
GEM_R  = sc.m(sc.GEM_R + 3)


def _tier_gf(base):
    # Brighter tiers earn a hotter flash ring + flash so legendary reads as the
    # richest stone; muted low tiers stay restrained.
    if base == (214, 206, 230): return 0.55
    if base == (108, 188, 252): return 0.70
    if base == (194, 122, 248): return 0.85
    if base == (255, 202, 104): return 1.00
    return 0.85


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def make_oct(cx, cy, hw, hh, cc, scale=1.0):
    """Stretched octagon (taller than wide). Vertices ordered so index 1->2 is
    the RIGHT vertical edge and 5->6 is the LEFT vertical edge — the two faces a
    3/4 key rakes. Scale shrinks the ring about (cx,cy)."""
    hw, hh, cc = hw * scale, hh * scale, cc * scale
    return [
        (cx + hw - cc, cy - hh),   # 0 top-right
        (cx + hw,      cy - hh + cc),  # 1 right-upper
        (cx + hw,      cy + hh - cc),  # 2 right-lower   (1->2 = RIGHT edge)
        (cx + hw - cc, cy + hh),   # 3 bottom-right
        (cx - hw + cc, cy + hh),   # 4 bottom-left
        (cx - hw,      cy + hh - cc),  # 5 left-lower
        (cx - hw,      cy - hh + cc),  # 6 left-upper    (5->6 = LEFT edge)
        (cx - hw + cc, cy - hh),   # 7 top-left
    ]


# The 3/4-view key rakes the step edges; ±12 is a raked highlight, not a flood —
# r1's ±60 inverted band values so the lit edge out-shone the bright ring.
EDGE_BIAS = 12


def bias_col(col, is_left_edge):
    delta = EDGE_BIAS if is_left_edge else -EDGE_BIAS
    return tuple(max(0, min(255, c + delta)) for c in col)


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Emerald cut: a stretched step-cut octagon. Value falls INTO the stone —
    dark seat rim, one bright flash ring, a medium ring, then a dark table well
    at centre — so the eye reads a box you look down into rather than a sparkle
    that throws light out. Painted as concentric rings (no triangular facets),
    each ring's left face raked bright and right face raked dark by a tight key,
    finished with a thin horizontal step flash. Mystery owns red — claims NO
    tier."""
    if mystery:
        base = (244, 96, 96)          # mystery owns red so it claims NO tier
        deep = (120, 22, 26)

    gf = _tier_gf(base)

    # ── band value curve — the inverted "into the stone" read ────────────────
    # band1 is the peak (the flash step); the table is a DARK well; band0 is the
    # dark seat rim. Falling value toward centre is what sells a step cut.
    band0_col = lerp_color(deep, NEAR_BLACK, 0.20)          # dark seat rim
    band1_col = lerp_color(base, WHITE, 0.25 + 0.15 * gf)   # bright flash ring
    band2_col = lerp_color(deep, base, 0.55)                # medium ring
    table_col = lerp_color(deep, base, 0.22 + 0.10 * gf)    # dark table well

    # ── seat: a dark well + faint tier ring so it reads on any ground ─────────
    seat_r = int(r + sc.m(3))
    seat_sz = seat_r * 2 + sc.m(6)
    seat = pygame.Surface((seat_sz, seat_sz), pygame.SRCALPHA)
    so = seat_sz // 2
    pygame.draw.circle(seat, (0, 0, 0, 160), (so, so), seat_r)
    pygame.draw.circle(seat, (*base, 90), (so, so), seat_r, max(1, sc.m(0.8)))
    surf.blit(seat, (cx - so, cy - so))

    # restrained bloom — never enough to blow out the falling step values
    sc.soft_glow(surf, cx, cy, int(r * 0.5), base, int(48 * gf))

    # ── concentric step rings, painted outer→inner (painter's algorithm) ─────
    hw = r * 0.70
    hh = r
    cc = hw * 0.40
    rings = [
        (make_oct(cx, cy, hw, hh, cc, 1.00), band0_col),
        (make_oct(cx, cy, hw, hh, cc, 0.72), band1_col),
        (make_oct(cx, cy, hw, hh, cc, 0.50), band2_col),
        (make_oct(cx, cy, hw, hh, cc, 0.34), table_col),
    ]
    lw = max(1, sc.m(1))
    for poly, col in rings:
        pygame.draw.polygon(surf, col, poly)
        # left step face raked bright, right step face raked dark (tight key)
        pygame.draw.line(surf, bias_col(col, True),  poly[5], poly[6], lw)
        pygame.draw.line(surf, bias_col(col, False), poly[1], poly[2], lw)

    # ── girdle rim: hue-tinted outline last so the silhouette stays crisp ─────
    rim_col = lerp_color(base, WHITE, 0.42)
    pygame.draw.polygon(surf, rim_col, rings[0][0], lw)

    # ── thin horizontal step flash — the iconic long streak across the top ───
    frx = max(1, int(r * 0.28 * gf))
    fry = max(1, int(r * 0.06))
    fx, fy = cx, cy - int(r * 0.35)
    flash = pygame.Surface((frx * 2 + 2, fry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(flash, (255, 255, 255, 220), (1, 1, frx * 2, fry * 2))
    surf.blit(flash, (fx - frx - 1, fy - fry - 1), special_flags=pygame.BLEND_ADD)

    return band0_col, band1_col, band2_col, table_col


sc.facet_gem = my_facet_gem   # monkey-patch BEFORE any draw_card call


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
    cols = my_facet_gem(g, sz // 2, sz // 2, GEM_R, base, deep)
    return g, cols


def _validate():
    # Fix 4: band1 must be the peak, band0 the dark rim, and the table a well
    # DARKER than the medium ring — the whole point of the inverted step read.
    for name, base, deep in RARITY_TIERS:
        _, (b0, b1, b2, tbl) = render_gem(base, deep)
        l0, l1, l2, lt = _lum(b0), _lum(b1), _lum(b2), _lum(tbl)
        print(f"{name:9s} band0={l0:6.1f} band1={l1:6.1f} "
              f"band2={l2:6.1f} table={lt:6.1f}")
        assert l1 == max(l0, l1, l2, lt), f"{name}: band1 not the peak"
        assert l0 == min(l0, l1, l2, lt), f"{name}: band0 not the dark rim"
        assert lt < l2, f"{name}: table not a well below the medium ring"
    print("monotonic step-value ordering holds for all tiers")


def main():
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r2/emerald-cut"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

    pad = 28
    gap = 24
    header_h = 44

    cards = [render_card(SID_PRIMARY), render_card(SID_SECONDARY)]
    cw, chh = cards[0].get_size()
    row1_w = cw * 2 + gap
    row1_y = header_h + pad

    zoom = 8
    gsz = render_gem((0, 0, 0), (0, 0, 0))[0].get_size()[0]
    gz = gsz * zoom
    label_h = 24
    row2_y = row1_y + chh + gap * 2
    row2_w = gz * 4 + gap * 3

    canvas_w = pad * 2 + max(row1_w, row2_w)
    canvas_h = row2_y + gz + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(30, True)
    lf = hud_font(18)

    header = hf.render("gem badge — emerald-cut r2", True, (236, 232, 250))
    canvas.blit(header, (pad, pad // 2 + 4))

    # Row 1 — full cards, centred
    x = pad + (max(row1_w, row2_w) - row1_w) // 2
    for card in cards:
        canvas.blit(card, (x, row1_y))
        x += cw + gap

    # Row 2 — 8x gem strip with tier labels
    x = pad + (max(row1_w, row2_w) - row2_w) // 2
    for name, base, deep in RARITY_TIERS:
        gem, _ = render_gem(base, deep)
        big = pygame.transform.scale(gem, (gz, gz))
        canvas.blit(big, (x, row2_y))
        lbl = lf.render(name, True, (210, 206, 226))
        canvas.blit(lbl, (x + (gz - lbl.get_width()) // 2, row2_y + gz + 4))
        x += gz + gap

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())

    _validate()


if __name__ == "__main__":
    main()
