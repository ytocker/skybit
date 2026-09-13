#!/usr/bin/env python3
"""
coin-keystone-arch  ·  confirm_purchase_v7  ·  round 1

The card becomes a pointed Gothic-arch portal rendered entirely in the
indigo+gold card vocabulary (NO sandstone / desert palette). The hero disc
seats in the arch's crown; below it a large octagonal keystone medallion —
the coin itself — is wedged into the apex, locking the arch. Two tall,
slightly tapered pier columns with capital tops form the action buttons.

Geometry reuses the v6 arch scaffold (arch_path / poly_bevel /
poly_drop_shadow) re-metricked for the taller 260x442 popup.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, plain_text, m, SS, font,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image


# ── mandatory gloss_sweep patch ───────────────────────────────────────────────
# BLEND_ADD reads RGB directly (source alpha is ignored), so sheen lives in the
# RGB channels of the sweep surface, not alpha.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


sc.gloss_sweep = _gloss_sweep_fixed


# ── tier palette (brief-exact) ────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_wizard",    "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",     "1,400",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,600",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}


# ── popup metrics (logical px; flow through m()) ──────────────────────────────
POP_W, POP_H = 260, 442
CX = 130

PLATE_X = 10
PLATE_W = 240
CORNER = 13

# Pointed-arch top edge: 65 px logical rise from the vertical shoulders to a
# pinched central apex; flat bottom (the piers, not scallops, sit under it).
APEX_Y = 95
SHOULDER_Y = 160
BOTTOM_Y = 438
# cxd±APEX_PT lands at shoulder height, so the two ascending Bezier halves
# converge to a narrow wedge (keystone read) rather than a soft dome.
APEX_PT = 22

# Hero disc — crown of the arch, overhanging above the shoulders.
R_DISC = 53
CY_DISC = 135

# Octagonal keystone medallion wedged into the apex, directly below the disc.
KEY_CX, KEY_CY, KEY_R = 130, 225, 34


# ── geometry helpers (from v6 scaffold) ───────────────────────────────────────
def _quad(p0, p1, p2, steps):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        pts.append((u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0],
                    u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1]))
    return pts


def _arc(cx, cy, r, a0, a1, steps):
    pts = []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def arch_path():
    """Closed pointed-arch silhouette (device px), flat bottom.

    The top edge rises from rounded shoulders to a pointed apex; APEX_PT keeps
    the two ascending arcs converging at a narrow wedge so the keystone read is
    clear even before the medallion is drawn. The bottom is a straight rim
    (the piers stand under the arch) instead of v6's scalloped baseline."""
    L   = m(PLATE_X)
    Rr  = m(PLATE_X + PLATE_W)
    cor = m(CORNER)
    aY  = m(APEX_Y)
    shY = m(SHOULDER_Y)
    bY  = m(BOTTOM_Y)
    cxd = m(CX)
    dx  = m(APEX_PT)

    pts = []
    # rounded top-left shoulder
    pts += _arc(L + cor, shY + cor, cor, 180, 270, 6)
    # arch — left shoulder rising to the pointed apex, then right descending
    pts += _quad((L + cor, shY), (cxd - dx, shY), (cxd, aY), 20)[1:]
    pts += _quad((cxd, aY), (cxd + dx, shY), (Rr - cor, shY), 20)[1:]
    # rounded top-right shoulder
    pts += _arc(Rr - cor, shY + cor, cor, 270, 360, 6)
    # right side + bottom-right corner
    pts += _arc(Rr - cor, bY - cor, cor, 0, 90, 6)
    # flat bottom rim closes straight across to the bottom-left corner
    pts += _arc(L + cor, bY - cor, cor, 90, 180, 6)
    return pts


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _inset(pts, d):
    """Radial shrink toward centroid — approximation sufficient for a thin bevel."""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    out = []
    for px, py in pts:
        vx, vy = cx - px, cy - py
        ln = math.hypot(vx, vy) or 1
        out.append((px + vx / ln * d, py + vy / ln * d))
    return out


# ── plate finish (from v6 scaffold) ───────────────────────────────────────────
def poly_drop_shadow(base, pts, blur, alpha, dy):
    """Soft multi-ring outer shadow for the free arch polygon (top-left light)."""
    minx, miny, maxx, maxy = _bbox(pts)
    pad = blur + dy + m(4)
    w = int(maxx - minx + pad * 2)
    h = int(maxy - miny + pad * 2)
    lp = [(p[0] - minx + pad, p[1] - miny + pad) for p in pts]
    shape = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(shape, (0, 0, 0, 255), lp)
    acc = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 1.7 / blur * 2.6)
        if a <= 0:
            continue
        tmp = shape.copy()
        tmp.fill((255, 255, 255, a), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 45):
            ox = int(round(i * math.cos(math.radians(ang))))
            oy = int(round(i * math.sin(math.radians(ang))))
            acc.blit(tmp, (ox, oy), special_flags=pygame.BLEND_RGBA_MAX)
    base.blit(acc, (int(minx - pad), int(miny - pad + dy)))


def poly_bevel(base, pts):
    """Emboss: dark outer keyline under a top-lit bright inner stroke. Works on
    any closed polygon (arch outline or the octagon keystone)."""
    minx, miny, maxx, maxy = _bbox(pts)
    pad = m(3)
    w = int(maxx - minx + pad * 2)
    h = int(maxy - miny + pad * 2)
    off = (int(minx - pad), int(miny - pad))
    inner = _inset(pts, m(2.2))
    lp_in = [(p[0] - off[0], p[1] - off[1]) for p in inner]
    hl = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(hl, (*CARD_RING_BRIGHT, 235), lp_in, width=max(1, m(1.4)))
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        a = int(255 * (1 - y / h) ** 1.5)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (w, y))
    hl.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(hl, off)
    pygame.draw.polygon(base, (4, 5, 16), pts, width=max(1, m(2)))


def masked_top_sheen(base, pts, mask, peak=58):
    """Glossy crown highlight clipped to the arch silhouette."""
    minx, miny, maxx, maxy = _bbox(pts)
    w = int(maxx - minx)
    h = int(maxy - miny)
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    span = int(h * 0.42)
    for y in range(span):
        a = int(peak * (1 - y / span) ** 1.4)
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (w, y))
    sheen.blit(mask, (-int(minx), -int(miny)), special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(sheen, (int(minx), int(miny)))


# ── hero disc (crown of the arch) ─────────────────────────────────────────────
def hero_disc(base, sid, gx, gy, r, pal):
    sc.cabochon(base, gx, gy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    sc.blit_thumb(base, sid, gx, gy, int(r * 1.5))
    sc.cabochon_glass(base, gx, gy, r, tint=pal["gem"])
    ring_w = max(3, m(3.0))
    pygame.draw.circle(base, pal["gem"], (gx, gy), r + ring_w // 2 + m(1), ring_w)
    pygame.draw.circle(base, lerp_color(pal["deep"], NEAR_BLACK, 0.35),
                       (gx, gy), r - m(1), max(1, m(1)))


# ── octagonal keystone medallion ──────────────────────────────────────────────
def octagon_pts(cx, cy, r):
    """8 vertices at radius r, first vertex at the top (point-up octagon)."""
    return [(cx + r * math.cos(math.radians(-90 + 45 * i)),
             cy + r * math.sin(math.radians(-90 + 45 * i))) for i in range(8)]


def keystone(base, pal, price_str):
    kcx, kcy, kr = m(KEY_CX), m(KEY_CY), m(KEY_R)

    # 1) feathered aura reading through the transparent headroom
    sc._alpha_aura(base, kcx, kcy, m(KEY_R + 16), pal["glow"], peak=55, layers=15)

    # 2) octagonal metallic face — distinct silhouette from the round disc
    pts = octagon_pts(kcx, kcy, kr)
    minx, miny, maxx, maxy = _bbox(pts)
    w = int(maxx - minx) + 2
    h = int(maxy - miny) + 2
    stops = [(0.0, pal["deep"]),
             (0.5, pal["gem"]),
             (1.0, lerp_color(pal["gem"], WHITE, 0.30))]
    body = vgrad_stops(w, h, 0, stops, 255, gamma=1.08)
    fmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(fmask, (255, 255, 255, 255),
                        [(px - minx, py - miny) for px, py in pts])
    body.blit(fmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(body, (int(minx), int(miny)))

    # gold emboss + dark contact keyline lock the medallion into the arch
    poly_bevel(base, pts)
    pygame.draw.polygon(base, (4, 5, 16), pts, m(2))

    # 3) gem shoulders flanking the keystone
    sc.facet_gem(base, m(103), kcy, m(6), pal["gem"], pal["deep"])
    sc.facet_gem(base, m(157), kcy, m(6), pal["gem"], pal["deep"])

    # 4) coin face seated in the medallion, price stamped on it
    sc.coin_glyph(base, kcx, kcy, m(26))
    plain_text(base, price_str, font(12), (kcx, m(229)), pal["gem"],
               shadow_a=150, weight=m(1.2), keyline=(6, 6, 16), kw=m(1.0))


# ── pier button (flanking arch column) ────────────────────────────────────────
def pier(base, x, y, w, h, label, label_size):
    """Tall, slightly tapered indigo column with a gold capital block on top and
    a bright bevel rim — the pillar SILHOUETTE in card colours, not sandstone."""
    rad = m(8)
    rect = pygame.Rect(x, y, w, h)

    # column body: indigo card gradient, top corners rounded (capital seats over)
    body = vgrad_stops(w, h, 0, [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15)
    bmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(bmask, (255, 255, 255, 255), (0, 0, w, h),
                     border_top_left_radius=rad, border_top_right_radius=rad,
                     border_bottom_left_radius=m(3), border_bottom_right_radius=m(3))
    body.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(body, (x, y))
    sc.bevel_rim(base, rect, rad, CARD_RING_DEEP, CARD_RING_BRIGHT, max(1, m(2)))

    # capital block — a slightly wider cap crowning the column
    cap_w = w + m(4)
    cap_h = m(10)
    cap = pygame.Rect(x + (w - cap_w) // 2, y, cap_w, cap_h)
    cbody = vgrad_stops(cap_w, cap_h, m(3),
                        [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15)
    base.blit(cbody, cap.topleft)
    sc.bevel_rim(base, cap, m(3), CARD_RING_DEEP, CARD_RING_BRIGHT, max(1, m(1.6)))

    # label centred low on the shaft
    plain_text(base, label, font(label_size), (x + w // 2, y + m(43)),
               (250, 248, 240), shadow_a=150, weight=m(1.0),
               keyline=(6, 6, 16), kw=m(1.0))


# ── popup ─────────────────────────────────────────────────────────────────────
def _cancel_label():
    """Prefer the full word; fall back to a compact glyph if it can't fit the
    84 px pier at the small pier font size."""
    f = font(11)
    if sc._glyph_base("CANCEL", f, 0).get_width() <= m(84) - m(14):
        return "CANCEL", 11
    return "NO", 12


def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    pts = arch_path()

    # 1) plate: shadow → indigo gradient body masked to arch → crown sheen → gold bevel
    poly_drop_shadow(big, pts, blur=m(8), alpha=165, dy=m(4))
    minx, miny, maxx, maxy = _bbox(pts)
    bw = int(maxx - minx) + m(2)
    bh = int(maxy - miny) + m(2)
    body = vgrad_stops(bw, bh, 0, [(0.0, CARD_T), (1.0, CARD_B)], 252, gamma=1.15)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - minx, p[1] - miny) for p in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(body, (int(minx), int(miny)))
    fmask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(fmask, (255, 255, 255, 255), pts)
    masked_top_sheen(big, pts, fmask, peak=60)
    poly_bevel(big, pts)

    # 2) hero disc seated on the arch crown (overhangs above the shoulders)
    hero_disc(big, sid, m(CX), m(CY_DISC), m(R_DISC), pal)

    # 3) octagonal keystone medallion wedged into the apex
    keystone(big, pal, price)

    # 4) rarity lozenge in the spandrel below the keystone
    sc._ribbon_lozenge(big, tier_word, m(CX), m(292), m(PLATE_W - 60), pal)

    # 5) item name
    plain_text(big, NAMES[tier_word], font(14), (m(CX), m(320)), (250, 248, 240),
               shadow_a=150, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # 6) two vertical pier buttons form the arch's flanking columns
    pier(big, m(17), m(345), m(84), m(428 - 345), "BUY", 14)
    clab, csize = _cancel_label()
    pier(big, m(159), m(345), m(84), m(428 - 345), clab, csize)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── three-tier review sheet ───────────────────────────────────────────────────
GAP    = 12
MARGIN = 22
HEAD   = 58

CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 42

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((8, 8, 20))

title = _font(19, True).render(
    "confirm_purchase_v7  ·  coin-keystone-arch  ·  round 1", True, (232, 226, 208))
canvas.blit(title, (MARGIN, 14))
sub = _font(11, True).render(
    "pointed indigo+gold arch · octagon coin-keystone wedged at apex · pier-column buttons",
    True, (150, 156, 178))
canvas.blit(sub, (MARGIN, 37))

lab = _font(13, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(word, sid, price, pal)
    px = MARGIN + i * (POP_W + GAP)
    py = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(midtop=(px + POP_W // 2, py + POP_H + 8)))

OUT = "/home/user/skybit/docs/confirm_purchase_v7/coin-keystone-arch/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)

img = Image.open(OUT)
print("saved", OUT, img.size)
