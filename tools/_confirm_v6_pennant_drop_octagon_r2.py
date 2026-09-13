#!/usr/bin/env python3
"""
pennant-drop-octagon  ·  confirm_purchase_v6  ·  round 2

Octagonal card plate — round 2 addresses all art-director notes:
- Octagon silhouette asserted: 30px equal chamfers on all 4 corners gives
  ~134px flat left/right vertical edges that read unambiguously as 8-sided.
- Disc centre at plate_top + 0.20×R_DISC for a clean 40% overhang above the
  top face; dropped ~10px vs r1.
- Asymmetric 6-ray BLEND_ADD starburst via the opaque-accumulator technique:
  rays accumulate on a black surface, alpha = max(R,G,B) extracts a
  luminance-shaped mask, then a normal blit composites onto the scene.
  Two top arms (−90°, −30°) are 1.6× longer than the four side/bottom arms.
- Pennant body doubled to 74 logical px tall, 204px wide (≈29% overhang past
  each plate edge). Slight overlap with plate bottom anchors the bottom.
- LEGENDARY starburst and pennant nudged +12% to equalise visual punch.
"""
import os
import math
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import numpy as np

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, plain_text, price_chip,
    _glyph_base, font, m, SS,
    CARD_T, CARD_B, CARD_RING_BRIGHT,
)
from game.hud import _font
from game.draw import lerp_color, WHITE, NEAR_BLACK


# ── mandatory gloss_sweep patch (BLEND_ADD reads RGB, not alpha) ──────────────
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


# ── layout (logical px; pass through m() for device px at SS=2) ──────────────
PANEL_W, PANEL_H = 220, 448
CX = PANEL_W // 2            # 110

# Octagon — equal chamfer on all 4 corners so all 8 faces read clearly.
# Vertical flat edge height = PLATE_H - 2×CHAMFER = 134px → assertive octagon.
PLATE_W  = 158
PLATE_H  = 194
CHAMFER  = 30
PLATE_X0 = CX - PLATE_W // 2   # 31

# Generous top headroom so the disc bloom and long starburst arms breathe.
PLATE_Y0 = 96

# Disc: centre at plate_top + 0.20×R_DISC → 40% of diameter overhangs above.
R_DISC  = 46
CY_DISC = PLATE_Y0 + int(R_DISC * 0.20)    # 96 + 9 = 105

# Starburst ray lengths (logical px from disc centre).
# Short arms reach 9px beyond disc edge; long arms reach 42px beyond.
R_SHORT = 55
R_LONG  = int(R_SHORT * 1.6)   # 88  (ratio = 1.6 ✓)

# Long-arm angles: straight-up and upper-right create assertive asymmetric bias.
_LONG_ANG_SET = {-90.0, -30.0}
ALL_ANG       = [-90.0, -30.0, 30.0, 90.0, 150.0, -150.0]   # screen-math °

# Pennant: 74px tall body, 204px wide → (204-158)/2 = 23px past each plate
# edge = 29% overhang per brief target of 25-30%.
PEN_W  = 204
PEN_H  = 74
PEN_Y0 = PLATE_Y0 + PLATE_H - 8   # slight overlap with plate bottom

Y_NAME = PEN_Y0 + PEN_H + 20      # 282 + 74 + 20 = 376
Y_CHIP = Y_NAME + 32               # 408

BG_TOP = (14, 15, 30)
BG_BOT = (6,  6,  16)
GAP    = 18
MARGIN = 20
HEAD   = 50
CANVAS_W = MARGIN * 2 + PANEL_W * 3 + GAP * 2
CANVAS_H = HEAD + PANEL_H + 44


# =============================================================================
# Octagon helpers
# =============================================================================
def octa_pts(x0, y0, W, H, C):
    """8 vertices of the card octagon in device px, CW from top-left chamfer."""
    return [
        (x0 + C,     y0),
        (x0 + W - C, y0),
        (x0 + W,     y0 + C),
        (x0 + W,     y0 + H - C),
        (x0 + W - C, y0 + H),
        (x0 + C,     y0 + H),
        (x0,         y0 + H - C),
        (x0,         y0 + C),
    ]


def _centroid(pts):
    return (sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts))


def _inset(pts, d):
    """Shrink each vertex toward the centroid by d for bevel strokes."""
    cx, cy = _centroid(pts)
    out = []
    for px, py in pts:
        vx, vy = px - cx, py - cy
        ln = math.hypot(vx, vy) or 1
        out.append((px - vx / ln * d, py - vy / ln * d))
    return out


def _poly_shadow(surf, pts, blur, alpha, dy):
    """Soft multi-layer drop shadow for an arbitrary polygon."""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = min(xs), min(ys)
    pad = blur + abs(dy) + m(4)
    w = int(max(xs) - x0 + pad * 2)
    h = int(max(ys) - y0 + pad * 2)
    lp    = [(p[0] - x0 + pad, p[1] - y0 + pad) for p in pts]
    shape = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(shape, (0, 0, 0, 255), lp)
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 1.7 / blur * 2.6)
        if a <= 0:
            continue
        tmp = shape.copy()
        tmp.fill((255, 255, 255, a), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(tmp, (int(x0 - pad), int(y0 - pad + dy)),
                  special_flags=pygame.BLEND_RGBA_MAX)


# =============================================================================
# Asymmetric starburst — correct BLEND_ADD approach
# =============================================================================
def _ray_onto_acc(acc, cx, cy, angle_deg, length, color, half_w=10):
    """Feathered tapered triangle accumulated on opaque black surface via
    BLEND_ADD so layers stack without clamping colour to white individually."""
    rad  = math.radians(angle_deg)
    perp = rad + math.pi / 2
    tip  = (cx + length * math.cos(rad), cy + length * math.sin(rad))
    layers = 10
    for i in range(layers, 0, -1):
        w     = half_w * i / layers
        inten = (1.0 - (i - 1) / layers) ** 1.6
        c     = tuple(min(255, int(ch * inten)) for ch in color)
        if max(c) <= 0:
            continue
        bl  = (cx + w * math.cos(perp), cy + w * math.sin(perp))
        br  = (cx - w * math.cos(perp), cy - w * math.sin(perp))
        tmp = pygame.Surface(acc.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(tmp, (*c, 255), [bl, br, tip])
        acc.blit(tmp, (0, 0), special_flags=pygame.BLEND_ADD)


def starburst(surf, cx, cy, pal, boost=1.0):
    """6-ray asymmetric starburst.

    Correct BLEND_ADD path:
    1. Opaque black accumulation surface — rays build up without alpha issues.
    2. BLEND_ADD all 6 rays; top-2 at 1.6× length.
    3. alpha = max(R,G,B) per pixel  → luminance-shaped mask.
    4. Normal blit onto scene — tier hue stays chromatic.

    `boost` nudges LEGENDARY +12% so all three tiers land with equal punch.
    """
    pw, ph = surf.get_size()
    acc = pygame.Surface((pw, ph))   # opaque black, no SRCALPHA
    acc.fill((0, 0, 0))

    # Moderate per-ray RGB so multi-ray centre accumulation stays chromatic.
    g    = pal["glow"]
    base = tuple(max(1, int(c * 0.44 * boost)) for c in g)

    for ang in ALL_ANG:
        length = m(R_LONG) if ang in _LONG_ANG_SET else m(R_SHORT)
        _ray_onto_acc(acc, cx, cy, ang, length, base, half_w=m(10))

    # Luminance-shaped alpha: each pixel's alpha = brightest channel of its
    # accumulated RGB.  Keeps the tier hue; makes black (no ray) fully
    # transparent so the card body shows through cleanly.
    rgb   = pygame.surfarray.pixels3d(acc)           # (w, h, 3)
    alpha = np.max(rgb, axis=2).astype(np.uint8)     # (w, h)
    del rgb

    out = pygame.Surface((pw, ph), pygame.SRCALPHA)
    out.blit(acc, (0, 0))                            # copies RGB; sets alpha=255
    pa = pygame.surfarray.pixels_alpha(out)
    pa[:] = alpha
    del pa

    surf.blit(out, (0, 0))                           # normal composite


# =============================================================================
# Pennant (dominant, large notched-hex ribbon)
# =============================================================================
def pennant(surf, tier_word, cx, top_y, pal):
    """Notched-hex pennant anchoring the card bottom.

    74px tall body at 204px wide sits below the octagon with 29% chevron
    overhang past each plate edge, making the flare unmistakable at a glance.
    """
    w     = m(PEN_W)
    h     = m(PEN_H)
    notch = m(22)
    x0    = cx - w // 2
    y0    = top_y

    top_c = lerp_color(pal["gem"], WHITE, 0.12)
    bot_c = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body  = vgrad_stops(w, h, 0,
                        [(0.0, top_c), (0.5, pal["glow"]), (1.0, bot_c)],
                        255, gamma=1.08)
    # Notched-hex silhouette: pointed ends on left and right.
    poly = [
        (notch,     0),
        (w - notch, 0),
        (w,         h // 2),
        (w - notch, h),
        (notch,     h),
        (0,         h // 2),
    ]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # drop shadow before the body
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 145), poly)
    surf.blit(sh, (x0, y0 + m(3)))
    surf.blit(body, (x0, y0))

    # Dark outer keyline + top-lit bright inner bevel
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(surf, (4, 5, 16), abspoly, width=max(1, m(1.6)))
    brite   = lerp_color(pal["gem"], WHITE, 0.55)
    inpoly  = _inset(abspoly, m(2.2))
    # Fade bevel toward bottom so it reads as top-lit.
    bevel   = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(bevel, (*brite, 185), inpoly, width=max(1, m(1.2)))
    # Vertical alpha ramp — bright top, fading to 30% at the bottom of the bevel
    fade = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    py0, py1 = y0, y0 + h
    for gy in range(surf.get_height()):
        if py0 <= gy <= py1:
            f = 1.0 - (gy - py0) / max(1, py1 - py0)
            a = int(255 * max(0.30, f ** 0.8))
        else:
            a = 0
        pygame.draw.line(fade, (255, 255, 255, a), (0, gy), (surf.get_width(), gy))
    bevel.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bevel, (0, 0))

    # Top gloss sweep on the pennant body
    gloss = pygame.Surface((w, h), pygame.SRCALPHA)
    for gy in range(h // 2):
        a = int(48 * (1 - gy / (h // 2)) ** 1.4)
        pygame.draw.line(gloss, (255, 255, 255, a), (0, gy), (w, gy))
    gloss.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(gloss, (x0, y0), special_flags=pygame.BLEND_ADD)

    # Tier word centred in pennant
    sz = 11.0
    f  = font(sz)
    trk = m(1.6)
    tw  = _glyph_base(tier_word, f, trk).get_width()
    while tw > w - notch * 2 - m(8) and sz > 7.5:
        sz -= 0.5
        f   = font(sz)
        tw  = _glyph_base(tier_word, f, trk).get_width()
    plain_text(surf, tier_word, f, (cx, y0 + h // 2),
               (14, 12, 26), shadow_a=0, tracking=trk, weight=m(0.8))


# =============================================================================
# One tier panel
# =============================================================================
def render_panel(tier_word, sid, price, pal, is_legendary=False):
    pw   = PANEL_W * SS
    ph   = PANEL_H * SS
    big  = pygame.Surface((pw, ph), pygame.SRCALPHA)

    # Opaque backdrop — BLEND_ADD starburst needs a scene to accumulate on.
    for y in range(ph):
        big.fill(lerp_color(BG_TOP, BG_BOT, y / ph), (0, y, pw, 1))

    # Octagon geometry (device px)
    x0  = m(PLATE_X0)
    y0  = m(PLATE_Y0)
    W   = m(PLATE_W)
    H   = m(PLATE_H)
    C   = m(CHAMFER)
    pts = octa_pts(x0, y0, W, H, C)

    # ── drop shadow ───────────────────────────────────────────────────────────
    _poly_shadow(big, pts, blur=m(8), alpha=165, dy=m(4))

    # ── plate body: vgrad tinted toward tier deep, masked to octagon ──────────
    xs  = [p[0] for p in pts]; ys = [p[1] for p in pts]
    bx  = int(min(xs)); by = int(min(ys))
    bw  = int(max(xs) - bx); bh = int(max(ys) - by)
    plate_t = lerp_color(CARD_T, pal["deep"], 0.28)
    plate_b = lerp_color(CARD_B, pal["deep"], 0.16)
    body    = vgrad_stops(bw, bh, 0,
                          [(0.0, plate_t), (1.0, plate_b)], 255, gamma=1.15)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - bx, p[1] - by) for p in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Top sheen clipped to silhouette
    sheen_h = min(m(44), bh)
    sheen   = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for sy in range(sheen_h):
        a = int(60 * (1 - sy / sheen_h) ** 1.3)
        pygame.draw.line(sheen, (255, 255, 255, a), (0, sy), (bw, sy))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(sheen, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    big.blit(body, (bx, by))

    # ── plate edge: dark keyline + top-lit gold bevel ─────────────────────────
    pygame.draw.polygon(big, (4, 5, 16), pts, width=max(1, m(2)))
    in2 = _inset(pts, m(2.2))
    for j in range(len(in2)):
        lx1, ly1 = in2[j]
        lx2, ly2 = in2[(j + 1) % len(in2)]
        ny = ((ly1 + ly2) / 2 - by) / max(1, bh)
        a  = max(70, int(235 * (1 - ny) ** 1.1))
        pygame.draw.line(big, (*CARD_RING_BRIGHT, a),
                         (int(lx1), int(ly1)), (int(lx2), int(ly2)),
                         max(1, m(1.8)))
    # Faint tier-tint inner tray
    tray = _inset(pts, m(5))
    pygame.draw.polygon(big, (*pal["gem"], 48), tray, width=max(1, m(1)))

    cxd = m(CX)
    cyd = m(CY_DISC)
    boost = 1.12 if is_legendary else 1.0

    # ── asymmetric starburst halo ─────────────────────────────────────────────
    starburst(big, cxd, cyd, pal, boost)

    # ── soft tier aura under disc ─────────────────────────────────────────────
    aura_r   = int(m(R_DISC) * 1.45)
    aura_col = tuple(min(255, int(c * boost)) for c in pal["glow"])
    sc.soft_glow(big, cxd, cyd, aura_r, aura_col, int(28 * boost), layers=8)

    # ── hero disc ─────────────────────────────────────────────────────────────
    sc.cabochon(big, cxd, cyd, m(R_DISC), sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cxd, cyd, int(m(R_DISC) * 1.5))
    except Exception:
        pygame.draw.circle(big, (*pal["gem"], 255), (cxd, cyd),
                           int(m(R_DISC) * 0.7))
    sc.cabochon_glass(big, cxd, cyd, m(R_DISC), tint=pal["gem"])
    # Tier ring: a warm gem-coloured band + dark inner contact
    pygame.draw.circle(big, pal["gem"], (cxd, cyd),
                       m(R_DISC) + m(3), max(2, m(2.4)))
    pygame.draw.circle(big, lerp_color(pal["deep"], NEAR_BLACK, 0.30),
                       (cxd, cyd), m(R_DISC) - m(1), max(1, m(1)))

    # ── pennant below plate ───────────────────────────────────────────────────
    # LEGENDARY pennant receives a slight colour lift so all three tiers
    # present equal warmth and saturation in the banner.
    if is_legendary:
        pal_p = {
            "gem":  tuple(min(255, int(c * 1.06)) for c in pal["gem"]),
            "glow": tuple(min(255, int(c * 1.10)) for c in pal["glow"]),
            "deep": pal["deep"],
        }
    else:
        pal_p = pal
    pennant(big, tier_word, m(CX), m(PEN_Y0), pal_p)

    # ── item name ─────────────────────────────────────────────────────────────
    try:
        name = sc._name(sid)
    except Exception:
        name = tier_word
    nf = font(14)
    plain_text(big, name, nf, (m(CX), m(Y_NAME)), (250, 248, 240),
               shadow_a=150, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # ── price chip ────────────────────────────────────────────────────────────
    price_chip(big, m(CX), m(Y_CHIP), price, m(23), affordable=True)

    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


# =============================================================================
# Review canvas
# =============================================================================
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    canvas.fill(lerp_color(BG_TOP, BG_BOT, y / CANVAS_H), (0, y, CANVAS_W, 1))

tt = _font(18, True).render(
    "confirm_purchase_v6  ·  pennant-drop-octagon  ·  round 2",
    True, (224, 226, 240))
canvas.blit(tt, tt.get_rect(midtop=(CANVAS_W // 2, 14)))

lab = _font(12, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    is_leg = (word == "LEGENDARY")
    panel  = render_panel(word, sid, price, pal, is_legendary=is_leg)
    px     = MARGIN + i * (PANEL_W + GAP)
    canvas.blit(panel, (px, HEAD))
    t = lab.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(midtop=(px + PANEL_W // 2, HEAD + PANEL_H + 8)))

OUT = "/home/user/skybit/docs/confirm_purchase_v6/pennant-drop-octagon/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print("saved", OUT, canvas.get_size())
