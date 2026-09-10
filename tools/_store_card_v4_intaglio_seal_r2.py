#!/usr/bin/env python3
"""store_card_v4 intaglio-seal — round 2 (final).

Round-1 read as a Skybit COIN (gold ring + domed face + gem + price = coin
grammar) and had an invisible engraved name, a border that dissolved lower-left,
blown top-right speculars, and a price chip the same value as the card body.

Round 2 implements every art-director note:
  P0  Hero is a heraldic ESCUTCHEON (arched top, pointed bottom), not a round
      ring — instantly separating the crest from a coin. The domed gem now reads
      as a stone SET INTO the crest.
  P1  A warm stone-gold NAME PLAQUE below the shield carries the engraved name
      (incised down-right shadow + up-left bevel highlight) so it is legible.
  P2  A (8,8,20) contact-shadow ring outside the shield + a dark keyline under a
      gold bevel keep the silhouette CLOSED all the way round, incl. lower-left.
  P3  The shield bevel is lit by ONE consistent top-left source — golden bright
      top-left easing to a still-legible shadow-gold bottom-right; no highlight
      exceeds alpha 220 (no blown chrome).
  P4  The price chip steps clearly above the card: a lighter indigo body ramp +
      a CARD_RING_BRIGHT rim + a coin glyph + cream numerals.

The card sizes preserve the AD layout order (shield high, plaque below, chip at
the foot, tier gem top-right); the shield is scaled to compose cleanly inside
the 176px body rather than overrunning the plaque + chip.
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
    m, SS, vgrad, vgrad_stops, top_sheen, contact_shadow, bevel_rim,
    drop_shadow, cabochon, cabochon_glass, blit_thumb, facet_gem, coin_glyph,
    chip_body_stops, soft_glow, plain_text, _glyph_base, _stamp_bold, font,
    CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT, CARD_RAD, GEM_R, RARITY,
)
from game.hud import _font
from game.draw import lerp_color, WHITE, NEAR_BLACK


# BLEND_ADD reads only RGB, so the stock gloss_sweep (which encodes the sweep in
# ALPHA) writes alpha=0 into the destination on any transparent headroom. Encode
# the ramp as RGB magnitude clipped to the pill mask so the gloss survives.
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


# ── tiers under test ──────────────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_tophat",  "520"),
    ("EPIC",      "skin_prism",   "1,400"),
    ("LEGENDARY", "skin_kitsune", "3,500"),
]

BG = (8, 8, 20)
PANEL_W, PANEL_H = 162 * SS, 100 * SS       # authored device panel = 324x200
GAP = 8
MARGIN = 10
TITLE_H = 34
LABEL_H = 34
CANVAS_W = MARGIN * 2 + PANEL_W * 3 + GAP * 2
CANVAS_H = TITLE_H + PANEL_H + LABEL_H

# Single top-left light — the ONE direction for every bevel on the card.
LX, LY = -0.7071, -0.7071
# Bevel range: golden crest highlight -> a shadow-gold that still holds L>=80 so
# the border never dissolves into the body (P2 + P3 reconciled).
BEVEL_BRIGHT = CARD_RING_BRIGHT              # (236,202,116) luma ~203
BEVEL_SHADOW = (150, 120, 58)                # luma ~122 — dimmer, still an edge


def _quad(p0, p1, p2, steps):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / steps for i in range(steps + 1))]


def escutcheon(sx, sy, sw, sh):
    """Heraldic heater shield: flat rounded top, straight shoulders, twin lower
    arcs meeting at a point. Returned as a dense polygon so ONE smoothscale
    resolves the curves crisp."""
    left, right = sx, sx + sw
    cx = sx + sw / 2.0
    top, bot = sy, sy + sh
    corner = sw * 0.13
    shoulder = sy + sh * 0.34
    pts = []
    pts.append((left + corner, top))
    pts.append((right - corner, top))
    pts += _quad((right - corner, top), (right, top), (right, top + corner), 6)
    pts.append((right, shoulder))
    pts += _quad((right, shoulder), (right, bot), (cx, bot), 18)     # r lower arc
    pts += _quad((cx, bot), (left, bot), (left, shoulder), 18)       # l lower arc
    pts.append((left, top + corner))
    pts += _quad((left, top + corner), (left, top), (left + corner, top), 6)
    return pts


def _centroid(pts):
    return (sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts))


def _name_plaque(surf, name, cx, cy, w, h):
    """Warm stone-gold plaque carrying the incised name. On this warm ground the
    engraving reads: an up-left bevel highlight + a down-right incised shadow
    around a dark carved fill."""
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    rad = m(4)
    drop_shadow(surf, r, rad, blur=m(3), alpha=90, dy=m(1.5))
    surf.blit(vgrad_stops(w, h, rad, [(0.0, (180, 160, 110)), (1.0, (140, 115, 75))],
                          alpha=230), r.topleft)
    top_sheen(surf, r, rad, m(6), peak=52)
    # dark contact keyline under a soft top-left stone bevel
    pygame.draw.rect(surf, (66, 50, 24), r, width=max(1, m(1)), border_radius=rad)
    bevel_rim(surf, r, rad, (78, 60, 30), (250, 236, 200, 180), w=max(1, m(1)))

    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > w - m(16) and sz > 7.5:
        sz -= 0.5
        f = font(sz)
    base = _stamp_bold(_glyph_base(name, f, 0), m(0.7))
    rr = base.get_rect(center=(cx, cy))
    hi = base.copy(); hi.fill((255, 240, 200, 255), special_flags=pygame.BLEND_RGBA_MULT)
    shd = base.copy(); shd.fill((40, 30, 10, 255), special_flags=pygame.BLEND_RGBA_MULT)
    mid = base.copy(); mid.fill((66, 48, 20, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hi, (rr.x - m(1), rr.y - m(1)))       # up-left bevel highlight
    surf.blit(shd, (rr.x + m(1), rr.y + m(1)))      # down-right incised shadow
    surf.blit(mid, rr.topleft)                      # carved-dark letter core


def _seal_price_chip(surf, cx, cy, text, h):
    """Price chip stepped clearly above the card body: a lighter indigo ramp
    (never the card's own dark), a bright card-ring rim, a coin glyph + cream
    numerals."""
    coin_d = int(h * 0.62)
    pad = m(11)
    gapc = m(6)
    f = font(h * 0.46 / SS)
    nw = _glyph_base(text, f, 0).get_width() + m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    chip_body_stops(surf, r, h // 2, [(0.0, (48, 44, 80)), (1.0, (28, 24, 52))],
                    (8, 8, 20), CARD_RING_BRIGHT, gloss=34, gamma=1.05)
    rim = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(rim, (*CARD_RING_BRIGHT, 180), rim.get_rect(),
                     width=max(1, m(1)), border_radius=h // 2)
    surf.blit(rim, r.topleft)
    x = r.x + pad
    coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
    x += coin_d + gapc
    plain_text(surf, text, f, (x + nw // 2, cy), (236, 230, 208), shadow_a=0,
               weight=m(1.0))
    return r


def _draw_shield(big, sid, rect, pal):
    cx = rect.centerx
    sw, sh = m(44), m(50)
    sx = cx - sw // 2
    sy = rect.y + m(5)
    outline = escutcheon(sx, sy, sw, sh)
    ctr = _centroid(outline)

    # P2a — contact-shadow ring OUTSIDE the border (offset down-right) so even the
    # shadowed lower arch is backed by a dark edge on the body.
    shadow_pts = [(x + m(2), y + m(2)) for (x, y) in outline]
    shsurf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shsurf, (8, 8, 20, 220), shadow_pts)
    big.blit(shsurf, (0, 0))

    # Shield field — a dark, faintly tier-tinted stone so the set gem pops. Built
    # on its own surface + masked to the silhouette, then one top sheen.
    bx0 = min(p[0] for p in outline); by0 = min(p[1] for p in outline)
    bx1 = max(p[0] for p in outline); by1 = max(p[1] for p in outline)
    bw, bh = int(bx1 - bx0) + 1, int(by1 - by0) + 1
    field_t = lerp_color((26, 28, 62), pal["deep"], 0.28)
    field_b = lerp_color((10, 11, 30), pal["deep"], 0.16)
    grad = vgrad_stops(bw, bh, 0, [(0.0, field_t), (1.0, field_b)], 255, gamma=1.18)
    local = [(x - bx0, y - by0) for (x, y) in outline]
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sheen = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(int(sh * 0.5)):
        pygame.draw.line(sheen, (255, 255, 255, int(46 * (1 - y / (sh * 0.5)) ** 1.4)),
                         (0, y), (bw, y))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    grad.blit(sheen, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    big.blit(grad, (int(bx0), int(by0)))

    # P2b + P3 — the BORDER is an OPAQUE gold bevel drawn ON the outline, so the
    # silhouette holds a bright edge all the way round (incl. lower-left). Per-edge
    # shade eases from a bright top-left to a still-legible shadow-gold bottom-right
    # off the ONE top-left light; the dimmest edge is luma ~122, never dissolving
    # into the body. A thin dark keyline is then dropped just INSIDE the bevel as
    # the pressed/incised groove that reads as a struck seal, not a coin ring.
    obg = [(int(round(x)), int(round(y))) for x, y in outline]
    n = len(obg)
    for i in range(n):
        x1, y1 = obg[i]
        x2, y2 = obg[(i + 1) % n]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ux, uy = sc_unit(mx, my, ctr)
        f = max(0.0, min(1.0, (ux * LX + uy * LY + 1) / 2))   # 0 shadow .. 1 lit
        col = lerp_color(BEVEL_SHADOW, BEVEL_BRIGHT, f)
        pygame.draw.line(big, col, (x1, y1), (x2, y2), max(1, m(2.4)))
    groove = [(int(round(x + sc_unit(x, y, ctr)[0] * m(2.6))),
               int(round(y + sc_unit(x, y, ctr)[1] * m(2.6)))) for (x, y) in outline]
    pygame.draw.polygon(big, (10, 9, 22, 210), groove, width=max(1, m(1)))

    return cx, sy, sw, sh


def sc_unit(x, y, ctr):
    dx, dy = x - ctr[0], y - ctr[1]
    l = math.hypot(dx, dy) or 1.0
    return dx / l, dy / l


def render_panel(word, sid, price):
    pal = RARITY[sc._rarity(sid)]
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(m(6), m(6), PANEL_W - 2 * m(6), PANEL_H - 2 * m(6))
    rad = m(CARD_RAD)

    # ── card shell (the locked CONSTELLATION body finish) ─────────────────────
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235), w=max(1, m(2.0)))
    # neutral inner tray keyline, matching the family
    tray = rect.inflate(-m(7), -m(7))
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=rad - m(3))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 80), tray, width=max(1, m(1)),
                     border_radius=rad - m(4))

    # ── P0 hero: the escutcheon crest with a gem set into it ───────────────────
    cx, sy, sw, sh = _draw_shield(big, sid, rect, pal)
    cyd = sy + m(21)
    r_dome = m(15)
    soft_glow(big, cx, cyd, r_dome + m(3), pal["glow"], 26, layers=8)
    cabochon(big, cx, cyd, r_dome, sc.CABO_LO, sc.CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        blit_thumb(big, sid, cx, cyd, int(r_dome * 1.5))
    except Exception:
        pygame.draw.circle(big, (*pal["gem"], 255), (cx, cyd), int(r_dome * 0.7))
    cabochon_glass(big, cx, cyd, r_dome, tint=pal["gem"])

    # ── tier rank gem, top-right corner ───────────────────────────────────────
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── P1 name plaque, then P4 price chip ────────────────────────────────────
    _name_plaque(big, sc._name(sid), cx, sy + sh + m(7), rect.w - m(16), m(13))
    _seal_price_chip(big, cx, rect.bottom - m(10), price, m(16))
    return big


# =============================================================================
# Stitch the 3-panel strip.
# =============================================================================
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG)

title = _font(22, True)
tt = title.render("store_card_v4  –  intaglio-seal  –  round 2 (final)",
                  True, (226, 224, 240))
canvas.blit(tt, tt.get_rect(midtop=(CANVAS_W // 2, 7)))

label_font = _font(20, True)
for i, (word, sid, price) in enumerate(TIERS):
    panel = render_panel(word, sid, price)
    px = MARGIN + i * (PANEL_W + GAP)
    canvas.blit(panel, (px, TITLE_H))
    lab = label_font.render(word, True, (206, 210, 228))
    canvas.blit(lab, lab.get_rect(midtop=(px + PANEL_W // 2, TITLE_H + PANEL_H + 6)))

out = "/home/user/skybit/docs/store_card_v4/intaglio-seal/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
