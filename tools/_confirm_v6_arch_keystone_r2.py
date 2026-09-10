#!/usr/bin/env python3
"""
arch-keystone  ·  confirm_purchase_v6  ·  round 2

AD notes implemented:
1. Real arch: SHOULDER_Y=152, APEX_Y=78 (74 logical px rise vs r1's 36 px).
   APEX_PT=18 so the two Bezier halves pinch the tip into a pointed wedge.
2. Dominant ribbon: BANNER_H=45, minimum width forced to 1.5x disc diameter
   so RARE aligns with the other tiers; notch deepened to m(18); cast shadow
   enhanced.
3. Tier-coloured ribbon: blue-metal for RARE, purple-metal for EPIC, gold only
   for LEGENDARY.
4. Normalised + tiered plume: RARE (3.0x) < EPIC (3.4x) < LEGENDARY (3.8x)
   radius so LEGENDARY reads boldest; cone geometry identical across tiers.
5. Disc nudged up ~12 px by lowering APEX_Y from 90 to 78 (40 % overhang
   unchanged by formula); RARE ribbon width stabilised via forced minimum.
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
    vgrad_stops, plain_text, price_chip,
    cabochon, cabochon_glass, blit_thumb, _glyph_base, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE


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

# Ribbon gradient stops per tier: each owns its metal language.
# Gold is reserved for LEGENDARY only.
RIBBON_STOPS = {
    "RARE": [
        (0.00, (185, 220, 255)),   # bright blue-white crown
        (0.45, (60, 140, 230)),    # mid gem-blue
        (1.00, (8, 22, 60)),       # deep navy foot
    ],
    "EPIC": [
        (0.00, (215, 155, 255)),   # bright purple-white crown
        (0.45, (150, 60, 220)),    # mid gem-purple
        (1.00, (22, 4, 50)),       # deep violet foot
    ],
    "LEGENDARY": [
        (0.00, (255, 228, 140)),   # bright gold crown
        (0.45, (220, 160, 40)),    # mid amber
        (1.00, (90, 50, 0)),       # deep amber-brown foot
    ],
}

# Per-tier plume radius factor — LEGENDARY reads boldest/widest.
PLUME_SCALE = {"RARE": 3.0, "EPIC": 3.4, "LEGENDARY": 3.8}


# ── popup metrics (logical px; flow through m()) ──────────────────────────────
POP_W, POP_H = 224, 312
CX = POP_W // 2      # 112

PLATE_X = 12
PLATE_W = POP_W - PLATE_X * 2    # 200
CORNER = 13

# Arch geometry — 74 px logical rise from shoulders to apex so the silhouette
# is unmistakable even with the disc hidden.
APEX_Y = 78           # keystone apex — topmost plate point
SHOULDER_Y = 152      # where card sides become vertical (was 126 in r1)
BOTTOM_Y = 275        # scallop baseline
SCALLOP_AMP = 9
N_SCALLOP = 6
# Bezier overshoot: cxd±APEX_PT controls land at shoulder height, causing the
# two arcs to pinch past each other at the apex → pointed wedge, not a dome.
APEX_PT = 18

R_DISC = 40
# 40 % overhang means disc top = APEX_Y - 0.4*diameter = APEX_Y - 32.
# Solving: CY_DISC = APEX_Y + 0.2*R_DISC = 78+8 = 86 (12 px above r1's 98).
CY_DISC = APEX_Y + int(R_DISC * 0.2)

# Ribbon minimum = 1.5 × disc diameter so all tiers align and read dominant.
MIN_RIBBON_W = int(R_DISC * 2 * 1.5)    # 120 logical px
BANNER_H = 45
BANNER_CY = 188

Y_NAME = 233
Y_PRICE = 260


# ── geometry helpers ──────────────────────────────────────────────────────────
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
    """Closed keystone-arch silhouette (device px).

    The top edge rises 74 logical px from the rounded shoulders to a pointed
    central apex.  APEX_PT=18 means each Bezier control sits 18 px past the
    arch centreline at shoulder height, so the two ascending arcs converge at a
    narrow wedge angle rather than joining tangentially — the keystone read is
    clear even without the disc."""
    L   = m(PLATE_X)
    Rr  = m(PLATE_X + PLATE_W)
    cor = m(CORNER)
    aY  = m(APEX_Y)
    shY = m(SHOULDER_Y)
    bY  = m(BOTTOM_Y)
    cxd = m(CX)
    dx  = m(APEX_PT)
    amp = m(SCALLOP_AMP)

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
    # scalloped bottom rim (right → left)
    x0s, x1s = Rr - cor, L + cor
    steps = N_SCALLOP * 8
    for k in range(1, steps):
        g = k / steps
        x = x0s - (x0s - x1s) * g
        frac = (g * N_SCALLOP) % 1.0
        pts.append((x, bY + amp * math.sin(math.pi * frac)))
    # bottom-left corner
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


# ── plate finish ──────────────────────────────────────────────────────────────
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
    """Emboss: dark outer keyline under a top-lit bright inner stroke."""
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


# ── directional comet-tail plume ──────────────────────────────────────────────
def _norm(color, target_max=235):
    """Normalise glow to a fixed peak luminance so tier colours read equally
    vivid before tier-specific radius scaling takes over."""
    mx = max(color) or 1
    s = target_max / mx
    return tuple(min(255, int(c * s)) for c in color)


def comet_plume(base, gx, gy, radius, glow):
    """Rising bloom streaming straight up through the open arch apex.

    Radial layers accumulated with BLEND_RGBA_MAX keep the tier hue pure
    (constant RGB, alpha stepping toward the core).  A feathered ±60° upward
    cone mask is applied via BLEND_RGBA_MULT, then the result composites with
    BLEND_RGBA_ADD so the plume carries alpha over the transparent canopy above
    the arch plate."""
    ng = _norm(glow)
    g = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    layers = 16
    for i in range(layers, 0, -1):
        ri = int(radius * i / layers)
        ai = int(200 * (1 - (i - 1) / layers) ** 1.8)
        if ri <= 0 or ai <= 0:
            continue
        circ = pygame.Surface((ri * 2 + 2, ri * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(circ, (*ng, ai), (ri + 1, ri + 1), ri)
        g.blit(circ, (gx - ri - 1, gy - ri - 1), special_flags=pygame.BLEND_RGBA_MAX)

    # ±60° upward wedge (straight up = −90°); full brightness within ±45°,
    # feathered to zero at ±60°.
    mask = pygame.Surface(base.get_size(), pygame.SRCALPHA)
    rr = radius * 1.2
    for a in range(-150, -29):
        off = abs(a + 90)
        v = 255 if off <= 45 else int(255 * (1 - (off - 45) / 15))
        if v <= 0:
            continue
        a0 = math.radians(a)
        a1 = math.radians(a + 1.5)
        tri = [(gx, gy),
               (gx + rr * math.cos(a0), gy + rr * math.sin(a0)),
               (gx + rr * math.cos(a1), gy + rr * math.sin(a1))]
        pygame.draw.polygon(mask, (255, 255, 255, v), tri)
    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    base.blit(g, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


# ── disc ──────────────────────────────────────────────────────────────────────
def hero_disc(base, sid, gx, gy, r, pal):
    cabochon(base, gx, gy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(base, sid, gx, gy, int(r * 1.5))
    cabochon_glass(base, gx, gy, r, tint=pal["gem"])
    ring_w = max(3, m(3.0))
    pygame.draw.circle(base, pal["gem"], (gx, gy), r + ring_w // 2 + m(1), ring_w)
    pygame.draw.circle(base, lerp_color(pal["deep"], NEAR_BLACK, 0.35),
                       (gx, gy), r - m(1), max(1, m(1)))


# ── dominant tier ribbon ──────────────────────────────────────────────────────
def big_ribbon(base, tier_word, cx, cy, max_w_dev, pal):
    """Tier-coloured notched-hex ribbon — the primary label element on the arch
    face.  Width is forced to at least MIN_RIBBON_W so all three tiers are
    equally wide and RARE doesn't drift narrower than EPIC/LEGENDARY.  The
    notch is deepened and the cast shadow offset enlarged so the banner sits
    visually proud of the arch body."""
    h = m(BANNER_H)
    notch = m(18)       # deep chevron ends (was m(13))
    sz = 22
    trk = m(1.8)
    f = font(sz)
    while _glyph_base(tier_word, f, trk).get_width() > max_w_dev - m(30) and sz > 14:
        sz -= 1
        f = font(sz)
    tw = _glyph_base(tier_word, f, trk).get_width()
    # enforce minimum so RARE aligns with the wider tiers
    w = max(m(MIN_RIBBON_W), min(max_w_dev, tw + m(34)))
    x0, y0 = cx - w // 2, cy - h // 2

    stops = RIBBON_STOPS[tier_word]
    body = vgrad_stops(w, h, 0, stops, 255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # enhanced cast shadow — deeper offset + more opaque so the ribbon reads as
    # the primary label element lifting off the arch face
    sh = pygame.Surface((w + m(8), h + m(6)), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 170), poly)
    base.blit(sh, (x0 - m(1), y0 + m(5)))

    base.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    edge_br = lerp_color(pal["gem"], WHITE, 0.5)
    pygame.draw.polygon(base, (4, 5, 16), abspoly, width=max(1, m(2)))
    inpoly = [(x0 + px + (1 if px < w / 2 else -1) * m(2),
               y0 + py + (1 if py < h / 2 else -1) * m(1.4)) for px, py in poly]
    pygame.draw.polygon(base, (*edge_br, 150), inpoly, width=max(1, m(1)))
    plain_text(base, tier_word, f, (cx, cy), (250, 248, 240), shadow_a=110,
               tracking=trk, weight=m(1.3),
               keyline=lerp_color(pal["deep"], NEAR_BLACK, 0.3), kw=m(1.1))


# ── popup ─────────────────────────────────────────────────────────────────────
def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    pts = arch_path()
    gx, gy = m(CX), m(CY_DISC)

    # 1) plate: shadow → gradient body masked to arch silhouette → crown sheen → bevel
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

    # 2) comet-tail plume — tier-scaled so LEGENDARY reads boldest
    plume_r = m(int(R_DISC * PLUME_SCALE[tier_word]))
    comet_plume(big, gx, m(APEX_Y), plume_r, pal["glow"])

    # 3) hero disc seated on the apex (40 % overhang above, 60 % inside)
    hero_disc(big, sid, gx, gy, m(R_DISC), pal)

    # 4) ribbon (dominant) → item name → price chip
    big_ribbon(big, tier_word, m(CX), m(BANNER_CY), m(PLATE_W - 10), pal)
    nf = font(15)
    plain_text(big, NAMES[tier_word], nf, (m(CX), m(Y_NAME)), (250, 248, 240),
               shadow_a=150, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    price_chip(big, m(CX), m(Y_PRICE), price, m(22), affordable=True)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── three-tier review sheet ───────────────────────────────────────────────────
GAP    = 22
MARGIN = 24
HEAD   = 60
CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 44

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    pygame.draw.line(canvas, lerp_color((11, 12, 27), (5, 5, 14), y / CANVAS_H),
                     (0, y), (CANVAS_W, y))

title = _font(19, True).render(
    "confirm_purchase_v6  ·  arch-keystone  ·  round 2", True, (232, 226, 208))
canvas.blit(title, (MARGIN, 16))
sub = _font(11, True).render(
    "real keystone arch (74 px rise) · tier-coloured ribbon · LEGENDARY-boldest plume",
    True, (150, 156, 178))
canvas.blit(sub, (MARGIN, 38))

lab = _font(13, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(word, sid, price, pal)
    px = MARGIN + i * (POP_W + GAP)
    py = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(midtop=(px + POP_W // 2, py + POP_H + 8)))

OUT = "/home/user/skybit/docs/confirm_purchase_v6/arch-keystone/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print("saved", OUT, canvas.get_size())
