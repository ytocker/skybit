#!/usr/bin/env python3
"""
arch-keystone  ·  confirm_purchase_v6  ·  round 1

Concept: the confirm card is a KEYSTONE ARCH. The plate's top edge is cut into
an upward-pointing arch that rises from two flat shoulders to a central apex
(like the wedge keystone that locks an arch). The lower rim is a wave/scalloped
edge. The hero cabochon disc is seated ON the apex — its lower ~60% nested in
the arch cavity, its top ~40% overhanging the plate, with the tier bloom
streaming straight UP out of the open apex as a directional comet-tail plume
(a soft_glow masked to a 120° upward cone). BELOW the disc the tier banner (a
2.6x notched-hex ribbon) dominates the arch face, then the item name in cream
and the gold price chip.

Sheet: three tiers side by side — RARE (sky-blue) / EPIC (purple) /
LEGENDARY (gold). Only the tier tint + the plume colour change per panel; the
keystone-arch structure is identical across all three.
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
    vgrad_stops, soft_glow, plain_text, price_chip,
    cabochon, cabochon_glass, blit_thumb, _glyph_base, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE


# ── mandatory gloss_sweep patch ───────────────────────────────────────────────
# BLEND_ADD reads RGB magnitude directly (source alpha is ignored), so the sheen
# has to live in the RGB channels — an alpha-driven sweep silently blows the gold
# chips to white.
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
     {"gem": (108, 188, 252), "glow": (74, 158, 248), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",     "1,400",
     {"gem": (194, 122, 248), "glow": (172, 94, 244), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,600",
     {"gem": (255, 202, 104), "glow": (255, 168, 58), "deep": (90, 50, 0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}


# ── popup metrics (logical px; flow through m()) ──────────────────────────────
POP_W, POP_H = 224, 312
CX = POP_W // 2

PLATE_X = 12
PLATE_W = POP_W - PLATE_X * 2      # 200
CORNER = 15

APEX_Y = 90                        # topmost plate point (the keystone apex)
SHOULDER_Y = 126                   # where the flat shoulders / vertical sides begin
BOTTOM_Y = 270                     # scallop baseline (cusps sit here)
SCALLOP_AMP = 9
N_SCALLOP = 6
APEX_PT = 8                        # apex peakiness — control offset past centre

R_DISC = 40
CY_DISC = APEX_Y + int(R_DISC * 0.2)   # 60% nested below apex, 40% overhanging

BANNER_CY = 178
BANNER_H = 38                      # ~2.6x the store card's m(15) ribbon
Y_NAME = 216
Y_PRICE = 246


# ── geometry samplers ─────────────────────────────────────────────────────────
def _quad(p0, p1, p2, steps):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return pts


def _arc(cx, cy, r, a0, a1, steps):
    pts = []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def arch_path():
    """The keystone-arch silhouette as one closed point path (device px):
    rounded shoulders, a pointed apex built from two quarter-ellipse beziers
    that overshoot the centre so the crown reads as a locking keystone tip, and
    a scalloped bottom rim."""
    L = m(PLATE_X)
    Rr = m(PLATE_X + PLATE_W)
    cor = m(CORNER)
    apexY = m(APEX_Y)
    shY = m(SHOULDER_Y)
    botY = m(BOTTOM_Y)
    cxd = m(CX)
    dx = m(APEX_PT)
    amp = m(SCALLOP_AMP)

    pts = []
    # top-left rounded shoulder
    pts += _arc(L + cor, shY + cor, cor, 180, 270, 6)
    # arch: left half rising to the pointed apex, then right half descending.
    # Controls overshoot past centre (cxd ∓ dx) so the two halves cross into a
    # crisp keystone point instead of a soft dome.
    pts += _quad((L + cor, shY), (cxd - dx, shY), (cxd, apexY), 18)[1:]
    pts += _quad((cxd, apexY), (cxd + dx, shY), (Rr - cor, shY), 18)[1:]
    # top-right rounded shoulder
    pts += _arc(Rr - cor, shY + cor, cor, 270, 360, 6)
    # bottom-right corner
    pts += _arc(Rr - cor, botY - cor, cor, 0, 90, 6)
    # scalloped bottom rim, right -> left (each segment a downward semicircle,
    # cusps pointing up on BOTTOM_Y between scallops)
    x_start = Rr - cor
    x_end = L + cor
    steps = N_SCALLOP * 8
    for k in range(1, steps):
        g = k / steps
        x = x_start - (x_start - x_end) * g
        frac = (g * N_SCALLOP) % 1.0
        pts.append((x, botY + amp * math.sin(math.pi * frac)))
    # bottom-left corner
    pts += _arc(L + cor, botY - cor, cor, 90, 180, 6)
    return pts


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _inset(pts, d):
    """Shrink the path toward its centroid by ~d px for the bright inner bevel
    stroke. Approximate (radial), which is all a thin lit rim needs."""
    cxg = sum(p[0] for p in pts) / len(pts)
    cyg = sum(p[1] for p in pts) / len(pts)
    out = []
    for px, py in pts:
        vx, vy = cxg - px, cyg - py
        l = math.hypot(vx, vy) or 1
        out.append((px + vx / l * d, py + vy / l * d))
    return out


# ── plate finish (polygon analogues of drop_shadow + bevel_rim) ───────────────
def poly_drop_shadow(base, pts, blur, alpha, dy):
    """Soft multi-offset outer shadow for the arch silhouette (top-left light =>
    offset down). Same read as store_cards.drop_shadow, but for a free path."""
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
    """Fine emboss on the arch edge: a dark outer keyline UNDER a bright inner
    stroke biased to the top (a top-left lit rim), mirroring bevel_rim."""
    minx, miny, maxx, maxy = _bbox(pts)
    pad = m(3)
    w = int(maxx - minx + pad * 2)
    h = int(maxy - miny + pad * 2)
    off = (int(minx - pad), int(miny - pad))
    inner = _inset(pts, m(2.2))
    lp_in = [(p[0] - off[0], p[1] - off[1]) for p in inner]
    hl = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(hl, (*CARD_RING_BRIGHT, 235), lp_in, width=max(1, m(1.4)))
    # bias the bright rim to the top: a top->bottom alpha ramp min'd in
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        a = int(255 * (1 - y / h) ** 1.5)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (w, y))
    hl.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(hl, off)
    # dark outer contact keyline so the edge is defined against the scrim
    pygame.draw.polygon(base, (4, 5, 16), pts, width=max(1, m(2)))


def masked_top_sheen(base, pts, mask, peak=58):
    """Glossy crown highlight over the upper arch face, clipped to the plate
    silhouette so the gloss never spills past the scalloped/arched edge."""
    minx, miny, maxx, maxy = _bbox(pts)
    w = int(maxx - minx)
    h = int(maxy - miny)
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    span = int(h * 0.42)
    for y in range(span):
        a = int(peak * (1 - y / span) ** 1.4)
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (w, y))
    sheen.blit(mask, (-int(minx), -int(miny)),
               special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(sheen, (int(minx), int(miny)))


# ── directional comet-tail plume ──────────────────────────────────────────────
def _norm(color, target_max=235):
    """Scale a glow colour so its brightest channel hits target_max — the plume
    reads equally intense across tiers while keeping each tier's hue unmistakable
    (colour-swap only)."""
    mx = max(color) or 1
    s = target_max / mx
    return tuple(min(255, int(c * s)) for c in color)


def comet_plume(base, gx, gy, radius, glow):
    """A rising bloom that escapes straight up through the open apex.

    Build a soft radial glow in the tier colour, then multiply it by a 120°
    upward wedge (±60° from straight up, feathered at the cone edges) so only the
    upward stream survives, and composite additively.

    Two constraints drive the construction. (1) A plain additive stack of full
    tier-colour circles saturates every channel to white, killing the hue — so
    the radial falloff is built with BLEND_RGBA_MAX (constant tier RGB, alpha
    stepping up toward the core) which keeps the tint pure. (2) BLEND_ADD only
    touches RGB, so a plume over the TRANSPARENT canopy above the plate would end
    up with alpha 0 and vanish — so the cone is applied as an ALPHA multiply and
    the plume is laid down with BLEND_RGBA_ADD, carrying both its glow RGB and
    the alpha that makes it visible over the scrim."""
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
        g.blit(circ, (gx - ri - 1, gy - ri - 1),
               special_flags=pygame.BLEND_RGBA_MAX)

    # feathered upward cone mask via thin angular slices. Straight up = -90°;
    # full inside ±45°, ramping to zero out to ±60°. RGB stays white so the
    # multiply preserves the tier tint; alpha carries the wedge feather.
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


# ── disc (store-card cabochon DNA, tier-tinted) ───────────────────────────────
def hero_disc(base, sid, gx, gy, r, pal):
    cabochon(base, gx, gy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(base, sid, gx, gy, int(r * 1.5))
    cabochon_glass(base, gx, gy, r, tint=pal["gem"])
    ring_w = max(3, m(3.0))
    pygame.draw.circle(base, pal["gem"], (gx, gy), r + ring_w // 2 + m(1), ring_w)
    pygame.draw.circle(base, lerp_color(pal["deep"], NEAR_BLACK, 0.35),
                       (gx, gy), r - m(1), max(1, m(1)))


# ── dominant tier banner (2.6x notched-hex ribbon) ────────────────────────────
def big_ribbon(base, tier_word, cx, cy, max_w, pal):
    """The store _ribbon scaled ~2.6x into the dominant rarity read: a notched
    tier-gradient hex holding the tier word, sitting on the arch face below the
    disc."""
    h = m(BANNER_H)
    notch = m(13)
    sz = 22
    trk = m(1.8)
    f = font(sz)
    while _glyph_base(tier_word, f, trk).get_width() > max_w - m(30) and sz > 14:
        sz -= 1
        f = font(sz)
    tw = _glyph_base(tier_word, f, trk).get_width()
    w = min(max_w, tw + m(34))
    x0, y0 = cx - w // 2, cy - h // 2

    top = lerp_color(pal["gem"], WHITE, 0.12)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0, [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                       255, gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # own drop shadow so the banner sits proud on the arch face
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 135), poly)
    base.blit(sh, (x0, y0 + m(3)))
    base.blit(body, (x0, y0))
    # top gloss + defined edges
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

    # 1) plate: shadow -> silhouette-masked body gradient -> crown gloss -> bevel
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
    # full-size silhouette mask for the clipped crown sheen
    fmask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(fmask, (255, 255, 255, 255), pts)
    masked_top_sheen(big, pts, fmask, peak=60)
    poly_bevel(big, pts)

    # 2) comet-tail plume rising up through the open apex — laid over the plate so
    #    it blooms the crown, then occluded at its hot origin by the disc, leaving
    #    only the upward stream showing above the apex.
    comet_plume(big, gx, m(APEX_Y), m(int(R_DISC * 3.4)), pal["glow"])

    # 3) hero disc seated on the apex (lower 60% nested, top 40% overhanging)
    hero_disc(big, sid, gx, gy, m(R_DISC), pal)

    # 4) banner (dominant) -> item name (cream) -> gold price chip
    big_ribbon(big, tier_word, m(CX), m(BANNER_CY), m(PLATE_W) - m(10), pal)
    nf = font(15)
    plain_text(big, NAMES[tier_word], nf, (m(CX), m(Y_NAME)), (250, 248, 240),
               shadow_a=150, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    price_chip(big, m(CX), m(Y_PRICE), price, m(22), affordable=True)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── three-tier review sheet over a modal scrim ────────────────────────────────
GAP = 22
MARGIN = 24
HEAD = 60
CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 44

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    pygame.draw.line(canvas, lerp_color((11, 12, 27), (5, 5, 14), y / CANVAS_H),
                     (0, y), (CANVAS_W, y))

title = _font(19, True).render(
    "confirm_purchase_v6  ·  arch-keystone  ·  round 1", True, (232, 226, 208))
canvas.blit(title, (MARGIN, 16))
sub = _font(11, True).render(
    "keystone-arch plate · disc seated on apex · comet-tail plume up through the apex",
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

OUT = "/home/user/skybit/docs/confirm_purchase_v6/arch-keystone/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print("saved", OUT, canvas.get_size())
