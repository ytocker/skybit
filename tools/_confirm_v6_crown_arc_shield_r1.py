#!/usr/bin/env python3
"""crown-arc-shield confirm_purchase_v6 round 1 render.

Three tier panels side-by-side (RARE / EPIC / LEGENDARY). Each is a HERALDIC
SHIELD: a standard vgrad body whose bottom edge is cut to a rounded heraldic
point (two straight lower edges converging to a filleted tip), finished with a
dark keyline + a top-lit gold bevel rim + a cast drop shadow. The glass
cabochon disc is the HERO — drawn ~2.4x the store R_DISC and overhanging the
shield's top edge by ~40%, its tier-coloured soft-glow aura firing UPWARD past
the plate unclipped so the rarity reads before any text. A curved arc-text band
crowns the disc (each glyph individually rotated to its tangent). Below: the
notched-hex rarity ribbon at ~2.4x store scale, the item name in cream, and the
gold price chip.
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
    vgrad_stops, plain_text, price_chip, _stamp_bold, _glyph_base, font, m, SS,
)
from game.hud import _font
from game.draw import lerp_color, WHITE, NEAR_BLACK


# BLEND_ADD ignores source alpha, so keep the gloss sweep's intensity in RGB
# magnitude — otherwise a full-white sweep blows the chip body out.
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


# ── tier tracks (brief palette) ──────────────────────────────────────────────
TIERS = [
    ("RARE", "rare", "skin_wizard", "720",
     {"gem": (108, 188, 252), "glow": (74, 158, 248), "deep": (18, 44, 90)}),
    ("EPIC", "epic", "skin_prism", "1,400",
     {"gem": (194, 122, 248), "glow": (172, 94, 244), "deep": (44, 10, 80)}),
    ("LEGENDARY", "legendary", "skin_aurora", "2,800",
     {"gem": (255, 202, 104), "glow": (255, 168, 58), "deep": (90, 50, 0)}),
]

PANEL_W, PANEL_H = 200, 340
CX = PANEL_W // 2

# Review backdrop. Each panel tile is filled with this SAME vertical gradient so
# the additive tier bloom lands on an OPAQUE scene (exactly as it does in-game) —
# BLEND_ADD leaves destination alpha untouched, so a transparent headroom would
# swallow the upward glow. Tiles then blend seamlessly into the canvas gradient.
BG_TOP, BG_BOT = (14, 15, 30), (6, 6, 16)
GAP = 16
MARGIN = 20
CANVAS_W = MARGIN * 2 + PANEL_W * 3 + GAP * 2
CANVAS_H = PANEL_H + 74
PANEL_Y = 48

# Shield geometry (logical px). The body top sits well below the panel top so
# the overhanging disc + its upward glow have transparent headroom to bloom into.
CARD_L, CARD_R = 14, 186
CARD_TOP = 88
SHOULDER_Y = 268
TIP_X, TIP_Y = 100, 322

R_DISC = 48          # ~2.4x the store R_DISC (=20): the hero disc
CY_DISC = 98         # 40% of the disc overhangs above CARD_TOP


# =============================================================================
# Shield outline — filleted corners + a rounded heraldic tip
# =============================================================================
def _unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    l = math.hypot(dx, dy) or 1.0
    return dx / l, dy / l


def _fillet(P0, P1, P2, r, steps=12):
    """Circular-arc fillet rounding corner P1 between edges P0->P1 and P1->P2."""
    v1 = _unit(P1, P0)
    v2 = _unit(P1, P2)
    dot = max(-1.0, min(1.0, v1[0] * v2[0] + v1[1] * v2[1]))
    ang = math.acos(dot)
    if ang < 1e-3 or abs(ang - math.pi) < 1e-3:
        return [P1]
    tan = r / math.tan(ang / 2)
    t1 = (P1[0] + v1[0] * tan, P1[1] + v1[1] * tan)
    bis = (v1[0] + v2[0], v1[1] + v2[1])
    bl = math.hypot(*bis) or 1.0
    bis = (bis[0] / bl, bis[1] / bl)
    center = (P1[0] + bis[0] * r / math.sin(ang / 2),
              P1[1] + bis[1] * r / math.sin(ang / 2))
    t2 = (P1[0] + v2[0] * tan, P1[1] + v2[1] * tan)
    a1 = math.atan2(t1[1] - center[1], t1[0] - center[0])
    a2 = math.atan2(t2[1] - center[1], t2[0] - center[0])
    da = a2 - a1
    while da > math.pi:
        da -= 2 * math.pi
    while da < -math.pi:
        da += 2 * math.pi
    return [(center[0] + r * math.cos(a1 + da * i / steps),
             center[1] + r * math.sin(a1 + da * i / steps)) for i in range(steps + 1)]


def shield_outline():
    A = (m(CARD_L), m(CARD_TOP))
    B = (m(CARD_R), m(CARD_TOP))
    C = (m(CARD_R), m(SHOULDER_Y))
    T = (m(TIP_X), m(TIP_Y))
    D = (m(CARD_L), m(SHOULDER_Y))
    rc, rs, rt = m(15), m(9), m(12)
    out = []
    out += _fillet(D, A, B, rc)
    out += _fillet(A, B, C, rc)
    out += _fillet(B, C, T, rs)
    out += _fillet(C, T, D, rt)
    out += _fillet(T, D, A, rs)
    return out


def _centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


# =============================================================================
# Upward tier aura — a single-hue radial bloom (no ADD stacking -> stays chromatic)
# =============================================================================
def crown_glow(surf, cx, cy, r, color):
    """The tier aura firing up past the plate. Built as ONE opaque radial ramp
    (brightest core -> dark rim) then blitted once with BLEND_ADD, so the hue
    survives — ADD ignores source alpha, and stacking many layers would clip the
    core to white. Vertically stretched + nudged up so the bloom pools UPWARD."""
    reach = int(r * 1.55)
    aura = pygame.Surface((reach * 2 + 4, reach * 2 + 4), pygame.SRCALPHA)
    c = reach + 2
    steps = 30
    for i in range(steps, 0, -1):
        rad = int(reach * i / steps)
        if rad <= 0:
            continue
        inten = (1 - i / steps) ** 1.5
        col = tuple(max(0, min(255, int(ch * inten))) for ch in color)
        pygame.draw.circle(aura, (*col, 255), (c, c), rad)
    aura = pygame.transform.smoothscale(aura, (reach * 2, int(reach * 2 * 1.28)))
    ar = aura.get_rect(center=(cx, cy - int(r * 0.22)))
    surf.blit(aura, ar.topleft, special_flags=pygame.BLEND_ADD)


# =============================================================================
# Arc text — each glyph rotated to its tangent along the disc crown
# =============================================================================
def _arc_glyph(ch, f, fill, key):
    """One arc character: a dark keyline (8 compass stamps) under a tier-tinted
    fill, packed onto its own small surface so rotation carries the outline."""
    base = _stamp_bold(f.render(ch, True, WHITE), m(1.0))
    w, h = base.get_size()
    pad = m(2)
    g = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    kl = base.copy()
    kl.fill((*key, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for ang in range(0, 360, 45):
        g.blit(kl, (pad + int(round(m(1) * math.cos(math.radians(ang)))),
                    pad + int(round(m(1) * math.sin(math.radians(ang))))))
    img = base.copy()
    img.fill((*fill, 255), special_flags=pygame.BLEND_RGBA_MULT)
    g.blit(img, (pad, pad))
    return g


def arc_text(surf, word, cx, cy, radius, pal):
    """Lay the tier word around the top of the disc: characters advance by
    arc-length, each rotated so its baseline is tangent (rot = -deg(s/radius)),
    and blitted centred on the arc radius. NOT one rotated word-surface."""
    f = font(13)
    fill = lerp_color(pal["gem"], WHITE, 0.30)
    key = lerp_color(pal["deep"], NEAR_BLACK, 0.35)
    glyphs = [_arc_glyph(ch, f, fill, key) for ch in word]
    widths = [g.get_width() for g in glyphs]
    track = m(3)
    total = sum(widths) + track * (len(glyphs) - 1)

    # faint dark crescent behind the band so the tier word reads over the bloom.
    span = math.degrees(total / radius)
    back = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(back, (*lerp_color(pal["deep"], NEAR_BLACK, 0.2), 150),
                    (cx - radius, cy - radius, radius * 2, radius * 2),
                    math.radians(270 - span * 0.62), math.radians(270 + span * 0.62),
                    max(2, m(11)))
    surf.blit(back, (0, 0))

    s = -total / 2
    for g, w in zip(glyphs, widths):
        sc_ = s + w / 2
        beta = math.radians(270 + math.degrees(sc_ / radius))
        x = cx + radius * math.cos(beta)
        y = cy + radius * math.sin(beta)
        rot = pygame.transform.rotate(g, -math.degrees(sc_ / radius))
        surf.blit(rot, rot.get_rect(center=(x, y)))
        s += w + track


# =============================================================================
# Rarity ribbon at ~2.4x store scale
# =============================================================================
def scaled_ribbon(surf, word, cx, cy, pal, scale=2.4):
    """The store's notched-hex _ribbon rendered small, then smoothscaled up so
    the rarity banner dominates the shield face at the confirm scale."""
    sw, sh = m(150), m(30)
    scratch = pygame.Surface((sw, sh), pygame.SRCALPHA)
    sc._ribbon(scratch, word, sw // 2, sh // 2, m(130), pal)
    bb = scratch.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        scratch = scratch.subsurface(bb).copy()
    big = pygame.transform.smoothscale(
        scratch, (int(scratch.get_width() * scale), int(scratch.get_height() * scale)))
    surf.blit(big, big.get_rect(center=(cx, cy)))


# =============================================================================
# One tier panel
# =============================================================================
def render_panel(word, rarity, sid, price, pal):
    big = pygame.Surface((PANEL_W * SS, PANEL_H * SS), pygame.SRCALPHA)
    # opaque backdrop matching the canvas gradient (so the upward BLEND_ADD bloom
    # has a scene to add onto and reads unclipped in the headroom).
    for ry in range(PANEL_H * SS):
        f = (PANEL_Y + ry / SS) / CANVAS_H
        big.fill(lerp_color(BG_TOP, BG_BOT, min(1.0, f)), (0, ry, PANEL_W * SS, 1))
    outline = shield_outline()
    ctr = _centroid(outline)

    # ── cast drop shadow: expand the silhouette radially, offset down ──────────
    dy = m(4)
    for i in range(m(8), 0, -1):
        a = int(160 * (i / m(8)) ** 1.7 / m(8) * 2.4)
        if a <= 0:
            continue
        pts = []
        for (x, y) in outline:
            ux, uy = _unit((x, y), ctr)
            pts.append((x - ux * i, y - uy * i + dy))
        pygame.draw.polygon(big, (0, 0, 0, a), pts)

    # ── shield body: standard vgrad tinted toward the tier deep, masked to the
    #    heraldic silhouette, with a top sheen ─────────────────────────────────
    bx, by = m(CARD_L), m(CARD_TOP)
    bw, bh = m(CARD_R) - m(CARD_L), m(TIP_Y) - m(CARD_TOP)
    plate_t = lerp_color((28, 30, 70), pal["deep"], 0.30)
    plate_b = lerp_color((12, 13, 38), pal["deep"], 0.18)
    grad = vgrad_stops(bw, bh, 0, [(0.0, plate_t), (1.0, plate_b)], 255, gamma=1.15)
    local = [(x - bx, y - by) for (x, y) in outline]
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # glossy top sheen, clipped to the shield silhouette
    sheen = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(m(40)):
        pygame.draw.line(sheen, (255, 255, 255, int(58 * (1 - y / m(40)) ** 1.3)),
                         (0, y), (bw, y))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    grad.blit(sheen, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    big.blit(grad, (bx, by))

    # ── shield edge: dark keyline UNDER a top-lit gold bevel + faint tier tray ─
    pygame.draw.polygon(big, (4, 5, 16), outline, width=max(1, m(2)))
    inset = [(x + _unit((x, y), ctr)[0] * m(2), y + _unit((x, y), ctr)[1] * m(2))
             for (x, y) in outline]
    for j in range(len(inset)):
        (x1, y1) = inset[j]
        (x2, y2) = inset[(j + 1) % len(inset)]
        ny = ((y1 + y2) / 2 - by) / max(1, bh)          # 0 top .. 1 tip
        a = max(70, int(235 * (1 - ny) ** 1.1))
        pygame.draw.line(big, (236, 202, 116, a), (x1, y1), (x2, y2), max(1, m(2)))
    tray = [(x + _unit((x, y), ctr)[0] * m(5), y + _unit((x, y), ctr)[1] * m(5))
            for (x, y) in outline]
    pygame.draw.polygon(big, (*pal["gem"], 55), tray, width=max(1, m(1)))

    cxd, cyd = m(TIP_X), m(CY_DISC)

    # ── the tier aura firing UPWARD past the plate, then the hero disc ─────────
    crown_glow(big, cxd, cyd, m(R_DISC), pal["glow"])
    sc.cabochon(big, cxd, cyd, m(R_DISC))
    try:
        sc.blit_thumb(big, sid, cxd, cyd, int(m(R_DISC) * 1.4))
    except Exception:
        pygame.draw.circle(big, (*pal["gem"], 255), (cxd, cyd), int(m(R_DISC) * 0.7))
    sc.cabochon_glass(big, cxd, cyd, m(R_DISC), tint=pal["gem"])

    # ── the arc-text crown over the disc ───────────────────────────────────────
    arc_text(big, word, cxd, cyd, m(R_DISC) + m(15), pal)

    # ── rarity ribbon -> name -> price, each in its own lane on the shield face ─
    scaled_ribbon(big, word, cxd, m(172), pal)
    plain_text(big, sc._name(sid), font(15), (cxd, m(202)), (246, 244, 232),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    price_chip(big, cxd, m(244), price, m(46), affordable=True)

    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


# =============================================================================
# Compose the three-panel review canvas
# =============================================================================
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    canvas.fill(lerp_color(BG_TOP, BG_BOT, y / CANVAS_H), (0, y, CANVAS_W, 1))

title = _font(20, True)
tt = title.render("confirm_purchase_v6 - crown-arc-shield - round 1", True,
                  (224, 226, 240))
canvas.blit(tt, tt.get_rect(midtop=(CANVAS_W // 2, 12)))

lab = _font(13, True)
for i, (word, rarity, sid, price, pal) in enumerate(TIERS):
    panel = render_panel(word, rarity, sid, price, pal)
    px = MARGIN + i * (PANEL_W + GAP)
    canvas.blit(panel, (px, PANEL_Y))

out = "/home/user/skybit/docs/confirm_purchase_v6/crown-arc-shield/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
