"""Round-2 render sheet for the shield-cut gem badge concept.

Monkey-patches store_cards.facet_gem with a revised D-shaped 7-facet
"shield-cut" stone. All art-director notes from round-1 are applied:
explicit per-tier glow factor, deeper D silhouette for a bolder shape,
separated trapezoid and triangle facets, crisp post-outline highlight
edge, correctly gated legendary table glint, thinned internal seams, and
glow alpha scaled by tier. Review-only tooling — never imported by the game.
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


def _tier_gf(base):
    # Explicit lookup avoids the luma misfiring on common (pale lavender sits
    # near legendary on Rec.601 luma, so the old formula gave them similar glow).
    if base == (214, 206, 230): return 0.55   # common
    if base == (108, 188, 252): return 0.70   # rare
    if base == (194, 122, 248): return 0.85   # epic
    if base == (255, 202, 104): return 1.00   # legendary
    return 0.85                               # mystery fallback


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Shield-cut: a D-shaped stone — flat top edge, domed bottom — cut into
    7 facets. The flat top (three trapezoids under a bright table nub) is the
    distinctive read; four alternating triangles fan down into the dome. The
    flat top anchors cleanly into the card corner with no fragile apex."""
    if mystery:
        base = (206, 60, 60)          # mystery owns red so it claims NO tier
        deep = (96, 18, 24)

    hi   = lerp_color(base, WHITE, 0.5)
    mid  = base
    lo   = lerp_color(base, deep, 0.6)
    dark = lerp_color(deep, NEAR_BLACK, 0.4)
    gf   = _tier_gf(base)

    # Flat top moved to 0.55r (was 0.7r) and dome deepened to 0.45r (was 0.3r)
    # so the D silhouette reads with a bolder ~3:2 height impression.
    top_y    = cy - int(0.55 * r)
    mid_y    = cy - int(0.20 * r)
    hub      = (cx, cy + int(0.15 * r))
    bottom_y = cy + int(0.45 * r)
    left_x   = cx - r
    right_x  = cx + r

    # --- Layer 0: additive glow bloom scaled by tier ---
    gr = int(r * 1.1)
    glow = pygame.Surface((gr * 2 + 2, gr * 2 + 2), pygame.SRCALPHA)
    gc = gr + 1
    for i in range(gr, 0, -1):
        # Peak alpha 80*gf — legendary visibly hotter than common (44 vs 80).
        a = int(80 * gf * (1 - i / gr))
        if a > 0:
            pygame.draw.circle(glow, (*base, a), (gc, gc), i)
    surf.blit(glow, (cx - gc, cy - gc), special_flags=pygame.BLEND_ADD)

    # --- Layer 1: D-silhouette body (flat top, elliptical dome) ---
    body = [(left_x, top_y), (right_x, top_y)]
    steps = 16
    # Elliptical dome sweeps right→bottom→left; arc_ry is the full dome depth
    # so the polygon traces the complete D perimeter.
    arc_cy = top_y
    arc_ry = bottom_y - top_y
    for k in range(steps + 1):
        ang = math.pi * (k / steps)
        bx = cx + r * math.cos(ang)
        by = arc_cy + arc_ry * math.sin(ang)
        body.append((bx, by))
    pygame.draw.polygon(surf, lo, body)

    # --- Layer 2: three upper trapezoids — centre reads forward by ~35% ---
    third = (right_x - left_x) / 3.0
    tl = lerp_color(mid, hi, 0.25)   # flanks — dim
    tc = lerp_color(mid, hi, 0.60)   # centre — noticeably brighter than flanks
    tr = lerp_color(mid, hi, 0.25)
    for i, col in enumerate((tl, tc, tr)):
        x0 = left_x + third * i
        x1 = left_x + third * (i + 1)
        pygame.draw.polygon(surf, col, [
            (x0, top_y), (x1, top_y), (x1, mid_y), (x0, mid_y)])

    # --- Layer 3: four lower fan triangles — alternation now clearly visible ---
    seam_pts = [(left_x + (right_x - left_x) * (j / 4.0), mid_y) for j in range(5)]
    # Wider contrast gap (0.25 vs 0.70) so the two tones don't collapse at
    # production size; t_lite moved from 0.40→0.25 to pull it away from dark.
    t_lite = lerp_color(mid, dark, 0.25)
    t_dark = lerp_color(mid, dark, 0.70)
    for j in range(4):
        col = t_lite if j % 2 == 0 else t_dark
        pygame.draw.polygon(surf, col, [seam_pts[j], seam_pts[j + 1], hub])

    # --- Layer 4: bright table nub at top-centre (kept — strongest facet read) ---
    tw = max(int(0.4 * r), 6)
    th = max(int(0.3 * r), 4)
    trect = pygame.Rect(0, 0, tw, th)
    # Centre the nub within the flat-top band (top_y → mid_y); 0.35r sits
    # comfortably inside the narrower band that results from moving top_y to 0.55r.
    trect.center = (cx, cy - int(0.35 * r))
    pygame.draw.rect(surf, hi, trect, border_radius=max(1, sc.m(1)))

    # --- Layer 5: seam strokes + silhouette outline ---
    # Internal seams thinned to 1px so they don't eat the narrow lower triangles;
    # outer silhouette stays at 2px for a clean badge silhouette.
    sw = max(1, sc.m(0.5))
    for j in range(1, 4):
        x = left_x + third * j
        pygame.draw.line(surf, dark, (x, top_y), (x, mid_y), sw)
    pygame.draw.line(surf, dark, (left_x, mid_y), (right_x, mid_y), sw)
    for j in range(1, 4):
        pygame.draw.line(surf, dark, seam_pts[j], hub, sw)
    pygame.draw.polygon(surf, dark, body, max(1, sc.m(1)))

    # --- Layer 6: crisp flat-top white highlight — drawn after outline so it wins ---
    # 2px line rather than 1px rect; alpha scaled with gf so common is subtler
    # than legendary; 2px inset from left/right so the outline corners don't bleed.
    hlt = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    pygame.draw.line(hlt, (*WHITE, int(140 * gf)),
                     (cx - r + 2, top_y), (cx + r - 2, top_y), 2)
    surf.blit(hlt, (0, 0))

    # Legendary only — explicit tier gate avoids the luma false-positive on common
    if gf == 1.0:
        gsz = max(2, int(0.16 * r))
        glint = pygame.Surface((gsz * 2, gsz * 2), pygame.SRCALPHA)
        pygame.draw.circle(glint, (255, 255, 255, 230), (gsz, gsz), gsz)
        surf.blit(glint,
                  (cx - gsz - int(0.12 * r), cy - int(0.35 * r) - gsz),
                  special_flags=pygame.BLEND_ADD)


sc.facet_gem = my_facet_gem   # monkey-patch before any draw_card call


def render_card(sid):
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((CARD_W, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       CARD_W - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, False, False, sc.PRICE_VARIANT)
    return surf


def render_gem(base, deep):
    m = GEM_R + 4
    surf = pygame.Surface((m * 2, m * 2), pygame.SRCALPHA)
    my_facet_gem(surf, m, m, GEM_R, base, deep)
    return surf


def main():
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge/shield-cut"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

    pad = 24
    gap = 24
    header_h = 40

    cards = [render_card(SID_PRIMARY), render_card(SID_SECONDARY)]
    cw, chh = cards[0].get_size()
    row1_w = cw * 2 + gap
    row1_y = header_h + pad

    zoom = 8
    gem_src = render_gem((0, 0, 0), (0, 0, 0)).get_size()[0]  # size probe
    gz = gem_src * zoom
    label_h = 24
    row2_y = row1_y + chh + gap * 2
    row2_w = gz * 4 + gap * 3

    canvas_w = pad * 2 + max(row1_w, row2_w)
    canvas_h = row2_y + gz + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(26)
    lf = hud_font(18)

    header = hf.render("gem badge — shield-cut r2", True, (236, 232, 250))
    canvas.blit(header, (pad, pad // 2 + 4))

    # Row 1 — full cards, centred
    x = pad + (max(row1_w, row2_w) - row1_w) // 2
    for card in cards:
        canvas.blit(card, (x, row1_y))
        x += cw + gap

    # Row 2 — 8x gem strip with tier labels
    x = pad + (max(row1_w, row2_w) - row2_w) // 2
    for name, base, deep in RARITY_TIERS:
        gem = render_gem(base, deep)
        big = pygame.transform.scale(gem, (gz, gz))
        canvas.blit(big, (x, row2_y))
        lbl = lf.render(name, True, (210, 206, 226))
        canvas.blit(lbl, (x + (gz - lbl.get_width()) // 2, row2_y + gz + 4))
        x += gz + gap

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
