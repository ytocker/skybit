"""Round-2 render for the rose-cut gem badge concept.

Applies art-director critique from round 1:
- Exact per-tier gf lookup replaces saturation heuristic (accessibility).
- Table uses a brighter fill (table_hi) distinct from lit crown facets, plus a
  1-px dark seam ring so the flat plane reads as its own surface.
- Table radius is tier-scaled (gf ladder) with a floor of 0.28r for readability.
- Crown triangles swapped to petal orientation: two base vertices on the girdle,
  one apex at the table rim (wide-at-girdle, narrow-at-table).
- Seam strokes widened to max(SS, m(0.9)) so they survive downscale to card size.
- UL highlight replaced by a crescent (outer ellipse minus inner offset ellipse via
  BLEND_RGBA_SUB) so it reads as a curved rim reflection, not a flat blob.
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

# Common base colour constant used in multiple places.
_COMMON_BASE = (214, 206, 230)


def _tier_gf(base):
    """Exact per-tier glow/size factor — defined by design spec, not derived
    from colour properties, so it stays stable if palette shifts later."""
    if base == (214, 206, 230): return 0.55   # common
    if base == (108, 188, 252): return 0.70   # rare
    if base == (194, 122, 248): return 0.85   # epic
    if base == (255, 202, 104): return 1.00   # legendary
    return 0.85                                # mystery fallback


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Rose-cut: circular girdle, six crown triangles in petal orientation
    (wide base at girdle, narrow apex at table) fanning from a brighter central
    hex table. Tier legibility comes from glow brightness AND table size without
    relying on hue shift alone."""
    if mystery:
        base, deep = (232, 96, 96), (120, 24, 24)

    hi       = lerp_color(base, WHITE, 0.50)
    # Separate, brighter fill for the table so the flat plane reads above the
    # lit upper crown facets rather than blending into them.
    table_hi = lerp_color(base, WHITE, 0.65)
    lo       = lerp_color(base, deep, 0.60)
    dark     = lerp_color(deep, NEAR_BLACK, 0.40)
    gf       = _tier_gf(base)

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

    # Table radius: tier-scaled so legendary has a perceptibly larger flat face
    # than common, giving a non-hue geometric rarity signal. Floor at 0.28r keeps
    # it readable at the smallest card-display size.
    tr_formula = max(4, int(r * (0.22 + 0.08 * gf)))
    tr         = max(tr_formula, max(4, int(0.28 * r)))

    def pt(rad, deg):
        a = math.radians(deg)
        return (cx + rad * math.cos(a), cy + rad * math.sin(a))

    lx, ly = -0.7071, -0.7071   # top-left light unit vector (screen coords)

    # ── Layer 2: six crown triangles, petal orientation ───────────────────────
    # Each triangle: two base vertices on the girdle ring, one apex pointing
    # inward to the table rim. This is the authentic rose-cut silhouette —
    # "petals" open outward, points collect at the central table.
    for k in range(6):
        v1   = pt(r,  60 * k + 30)   # girdle base-left
        v2   = pt(r,  60 * k + 90)   # girdle base-right
        apex = pt(tr, 60 * k + 60)   # apex at table rim, pointing inward
        # Face normal approximated by the outward direction of the apex angle.
        ax   = math.cos(math.radians(60 * k + 60))
        ay   = math.sin(math.radians(60 * k + 60))
        d    = ax * lx + ay * ly      # -1 away .. +1 toward light
        f    = (d + 1) / 2            # 0 dark .. 1 lit
        col  = lerp_color(lerp_color(dark, lo, min(1.0, f * 2)),
                          hi, max(0.0, (f - 0.5) * 2))
        pygame.draw.polygon(surf, col, [v1, v2, apex])

    # ── Layer 3: central hex table ────────────────────────────────────────────
    # Vertices are the triangle apexes, so the table naturally caps all facets.
    # table_hi is brighter than hi so the flat plane reads above lit crown facets.
    table = [pt(tr, 60 * k + 60) for k in range(6)]
    pygame.draw.polygon(surf, table_hi, table)
    # 1-px dark seam ring separates the flat table from surrounding tilted facets.
    pygame.draw.polygon(surf, dark, table, 1)

    # ── Layer 4: crown seam strokes ──────────────────────────────────────────
    # Wide enough to survive downscale to card size — hairlines vanish.
    seam_w = max(sc.SS, int(sc.m(0.9)))
    for k in range(6):
        # One seam per triangle from its inward apex to its left girdle base;
        # adjacent triangles share girdle boundary points so all boundaries are covered.
        pygame.draw.line(surf, dark, pt(tr, 60 * k + 60), pt(r, 60 * k + 30), seam_w)

    # ── Layer 5: girdle rim keyline ──────────────────────────────────────────
    pygame.draw.circle(surf, lerp_color(lo, dark, 0.4), (cx, cy), r, max(1, sc.m(1)))

    # ── Layer 6: upper-left crescent highlight (skip common — its pale value
    # contrast is low and a bright specular would wash the facets out) ────────
    if base != _COMMON_BASE:
        hw = max(2, int(r * 0.4))
        hh = max(1, int(r * 0.25))
        # Build crescent on a temporary SRCALPHA surface: draw the outer ellipse
        # then subtract an offset inner ellipse (BLEND_RGBA_SUB zeroes alpha where
        # the mask is opaque) to leave only the curved outer rim visible.
        pad_c = max(3, int(r * 0.12))
        tw = hw * 2 + pad_c * 2
        th = hh * 2 + pad_c * 2
        crescent = pygame.Surface((tw, th), pygame.SRCALPHA)
        crescent.fill((0, 0, 0, 0))
        pygame.draw.ellipse(crescent, (*WHITE, int(130 * gf)),
                            (pad_c, pad_c, hw * 2, hh * 2))
        # Offset shifts the punch-out ellipse toward lower-right so the remaining
        # crescent faces upper-left, matching the gem's primary light source.
        ox = max(2, int(r * 0.08))
        oy = max(2, int(r * 0.06))
        sub = pygame.Surface((tw, th), pygame.SRCALPHA)
        sub.fill((0, 0, 0, 0))
        iw = max(2, hw * 2 - ox * 2)
        ih = max(2, hh * 2 - oy * 2)
        pygame.draw.ellipse(sub, (0, 0, 0, 255),
                            (pad_c + ox, pad_c + oy, iw, ih))
        crescent.blit(sub, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        # Place the crescent near the upper-left girdle rim, inside the circle.
        hx = cx - int(0.35 * r)
        hy = cy - int(0.35 * r)
        surf.blit(crescent, (hx - tw // 2, hy - th // 2))


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
    head_f  = hud_font(30)

    cards   = [render_card(SID_PRIMARY), render_card(SID_SECONDARY)]
    row1_w  = sum(c.get_width() for c in cards) + gap
    row1_h  = max(c.get_height() for c in cards)

    scale   = 8
    gems    = [(name, pygame.transform.scale(render_gem(b, d),
                                             (render_gem(b, d).get_width() * scale,
                                              render_gem(b, d).get_height() * scale)))
               for (name, b, d) in RARITY_TIERS]
    strip_gap = 28
    row2_w  = sum(g.get_width() for _, g in gems) + strip_gap * (len(gems) - 1)
    row2_h  = max(g.get_height() for _, g in gems)
    label_h = 30

    head_h    = 46
    content_w = max(row1_w, row2_w)
    W = content_w + pad * 2
    H = pad + head_h + row1_h + gap * 2 + row2_h + label_h + pad
    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    head = head_f.render("gem badge — rose-cut r2", True, (235, 235, 245))
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
        canvas.blit(lab, (x + (g.get_width() - lab.get_width()) // 2,
                          y + g.get_height() + 6))
        x += g.get_width() + strip_gap

    out = "/home/user/skybit/docs/store_card_v5_gem_badge/rose-cut/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
