"""Review render: pear-cut gem badge (round 2) for the v5 store card.

An asymmetric teardrop tier gem in place of the locked 8-facet octagon: a
rounded 5-point head arc up top narrowing to a single sharp apex below, cut
into six crown facets tiling as a convex ring-strip around a small hex table.
r2 answers the art-director notes: the table is a readable mid-dark hue (not
the near-black it was collapsing to), the bottom apex carries a bright rim
keyline plus a dark tip so it separates from the seat, the warm reflected pass
is anchored to the gem's own hue family (no olive drift on epic purple), and
visual mass is graded head-left bright -> head-right mid -> lower kites dark
-> apex darkest. All geometry hangs off a LIFTED centre so the round head gets
card-corner breathing room above the point. Review-only tooling — never
imported by the game.
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
    # Brighter tiers carry a hotter aura/specular than muddy low tiers; keyed
    # off the tier's own hue so the four badges read as one graded family.
    if base == (214, 206, 230): return 0.55
    if base == (108, 188, 252): return 0.70
    if base == (194, 122, 248): return 0.85
    if base == (255, 202, 104): return 1.00
    return 0.85


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Pear-cut: a teardrop stone — round head up top, single sharp apex
    below — cut into six crown facets tiling a small hex table. Each facet
    takes ONE flat value off a top-left key light via its outer-edge normal;
    the lower kites and apex are pushed darker so mass falls toward the point,
    which is then held by a bright rim keyline against the near-black seat."""
    if mystery:
        # Mystery owns red so it claims none of the four tier hues.
        base = (244, 96, 96)
        deep = (120, 22, 26)

    gf = _tier_gf(base)

    # Value ramp. The table is deliberately a mid-dark window (between deep and
    # base) so it recesses UNDER the lit crown instead of flashing white — and,
    # critically, never collapses toward the card's near-black ground.
    t_dk      = lerp_color(deep, base, 0.18)
    t_mid     = base
    t_hi      = lerp_color(base, WHITE, 0.48 + 0.18 * gf)
    table_col = lerp_color(deep, base, 0.35 + 0.20 * gf)
    t_tip     = lerp_color(deep, NEAR_BLACK, 0.45)
    # Warm bounce anchored to the gem's own hue so it stays in-family (a pure
    # cream warm drifts olive on epic purple); strength stays low.
    warm      = lerp_color(base, (255, 220, 180), 0.30)
    rim_col   = lerp_color(base, WHITE, 0.42)
    t_key     = lerp_color(deep, NEAR_BLACK, 0.5)

    def shade(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)
        f = (d + 1) / 2
        col = (lerp_color(t_dk, t_mid, f * 2) if f < 0.5
               else lerp_color(t_mid, t_hi, (f - 0.5) * 2))
        f2 = max(0.0, (nx * 0.5 + ny * 0.5 + 1) / 2)
        return lerp_color(col, warm, 0.12 * f2 * gf)

    # LIFTED centre — head geometry hangs off cg; the apex reaches to cy+r so
    # the stone falls as a teardrop with its mass in the round head.
    cgx, cgy = cx, cy - int(r * 0.10)

    # dark seat well (tall ellipse to contain both head and the low apex) so
    # the stone reads on any card ground
    ew, eh = int(r * 2.3), int(r * 2.7)
    seat = pygame.Surface((ew + 4, eh + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(seat, (0, 0, 0, 175), (2, 2, ew, eh))
    pygame.draw.ellipse(seat, (*base, 90), (2, 2, ew, eh), max(1, sc.m(0.8)))
    surf.blit(seat, (cx - ew // 2 - 2, cy - eh // 2 - 2))

    # inner tier bloom settling the head into the seat
    sc.soft_glow(surf, cgx, cgy, int(r * 0.5), base, int(80 * gf))

    # teardrop girdle — 5-point head arc (left shoulder -> top -> right
    # shoulder) closing to a single bottom apex
    A    = (cgx,                    cgy - r)
    gTL  = (cgx - int(r * 0.62),    cgy - int(r * 0.80))
    gTR  = (cgx + int(r * 0.62),    cgy - int(r * 0.80))
    gL   = (cgx - int(r * 0.95),    cgy - int(r * 0.12))
    gR   = (cgx + int(r * 0.95),    cgy - int(r * 0.12))
    apex = (cx,                     cy + r)
    girdle = [gL, gTL, A, gTR, gR, apex]

    # small hex table seated in the head zone, clearly inside the rim
    tc = (cgx, cgy - int(r * 0.20))
    tr = int(r * 0.33)
    table = [(tc[0] + int(tr * math.cos(math.radians(a))),
              tc[1] + int(tr * math.sin(math.radians(a))))
             for a in (-150, -90, -30, 30, 90, 150)]

    def edge_normal(p, q):
        mx = (p[0] + q[0]) / 2 - cgx
        my = (p[1] + q[1]) / 2 - cgy
        ml = math.hypot(mx, my) or 1.0
        return mx / ml, my / ml

    # Crown ring-strip: each girdle edge to the matching table edge. The two
    # facets that touch the apex are the lower kites — pushed darker so the
    # stone's mass converges into the point (fix: head bright, tip dark).
    n = len(girdle)
    for i in range(n):
        a, b = girdle[i], girdle[(i + 1) % n]
        ta, tb = table[i], table[(i + 1) % n]
        col = shade(*edge_normal(a, b))
        if apex in (a, b):
            col = lerp_color(col, t_tip, 0.42)
        pygame.draw.polygon(surf, col, [a, b, tb, ta])

    # flat hex table — mid-dark window, the recessed focal plane
    pygame.draw.polygon(surf, table_col, table)

    # darkest point: a small tip triangle at the apex so L bottoms out there
    tipL = (apex[0] + int((gL[0] - apex[0]) * 0.26),
            apex[1] + int((gL[1] - apex[1]) * 0.26))
    tipR = (apex[0] + int((gR[0] - apex[0]) * 0.26),
            apex[1] + int((gR[1] - apex[1]) * 0.26))
    pygame.draw.polygon(surf, t_tip, [apex, tipR, tipL])

    # facet seams from each table corner to its girdle corner
    sw = max(1, sc.m(0.4))
    for tv, gv in zip(table, girdle):
        pygame.draw.line(surf, (*t_key, 190), tv, gv, sw)

    # crisp rim outline
    pygame.draw.polygon(surf, rim_col, girdle, max(1, sc.m(0.6)))
    # bright apex keyline — the two lower girdle edges redrawn hot so the sharp
    # tip separates from the near-black seat instead of dissolving into it
    kw = max(1, sc.m(1))
    pygame.draw.line(surf, rim_col, gR, apex, kw)
    pygame.draw.line(surf, rim_col, gL, apex, kw)

    # dual specular in the round-head zone, offset up-left onto the plane the
    # top-left key light actually strikes (never on the apex)
    def _add_pip(spx, spy, rx, ry, al):
        pw, ph = int(rx * 2) + 2, int(ry * 2) + 2
        pip = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.ellipse(pip, (255, 255, 255, al), (1, 1, int(rx * 2), int(ry * 2)))
        surf.blit(pip, (int(spx - rx), int(spy - ry)), special_flags=pygame.BLEND_ADD)

    pr = max(2, int(r * (0.11 + 0.09 * gf)))
    _add_pip(cgx - r * 0.20, cgy - r * 0.28, pr * 1.3, pr, int(175 * gf))
    pr2 = max(1, int(r * 0.06))
    _add_pip(cgx - r * 0.26, cgy - r * 0.34, pr2, pr2 * 0.8, 210)


# ── render sheet ──────────────────────────────────────────────────────────────
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

sc.facet_gem = my_facet_gem   # rebind BEFORE draw_card so cards use the new cut


def render_card(sid):
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((sc.CARD_W * sc.SS, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
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
    BG = (8, 8, 20)
    PAD, GAP = 28, 24

    cards = [render_card(SID_PRIMARY), render_card(SID_SECONDARY)]
    ZOOM = 8
    gems = []
    for name, base, deep in RARITY_TIERS:
        g = render_gem(base, deep)
        gz = pygame.transform.smoothscale(
            g, (g.get_width() * ZOOM // 2, g.get_height() * ZOOM // 2))
        gems.append((name, gz))

    hf = hud_font(30, True)
    lf = hud_font(16, True)

    card_row_w = len(cards) * cards[0].get_width() + (len(cards) - 1) * GAP
    gem_w = gems[0][1].get_width()
    strip_w = len(gems) * gem_w + (len(gems) - 1) * GAP
    content_w = max(card_row_w, strip_w)
    W = content_w + 2 * PAD

    header = hf.render("gem badge — pear-cut r2", True, (238, 236, 250))
    card_h = cards[0].get_height()
    gem_h = gems[0][1].get_height()
    label_h = lf.get_height() + 8

    y = PAD
    header_h = header.get_height()
    cards_y = y + header_h + GAP
    strip_y = cards_y + card_h + GAP + 30
    H = strip_y + gem_h + label_h + PAD

    canvas = pygame.Surface((W, H))
    canvas.fill(BG)

    canvas.blit(header, (PAD, y))

    # row 1 — two full cards, centred
    x = (W - card_row_w) // 2
    for c in cards:
        canvas.blit(c, (x, cards_y))
        x += c.get_width() + GAP

    # row 2 — zoomed gem strip, one per tier, labelled below
    sub = lf.render("zoomed gem badge — all four tiers", True, (170, 170, 200))
    canvas.blit(sub, (PAD, strip_y - 26))
    x = (W - strip_w) // 2
    for name, gz in gems:
        canvas.blit(gz, (x, strip_y))
        lbl = lf.render(name, True, (222, 220, 238))
        canvas.blit(lbl, (x + (gem_w - lbl.get_width()) // 2,
                          strip_y + gem_h + 4))
        x += gem_w + GAP

    out = "/home/user/skybit/docs/store_card_v5_gem_badge_r2/pear-cut/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
