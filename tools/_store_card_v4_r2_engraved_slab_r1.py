"""engraved-slab — store_card_v4_r2 concept, round 1 headless render.

The whole card reads as ONE carved block. Instead of raised plates for the
name and price, both are CUT INTO the surface as incised troughs that share a
single carved grammar:

  * NAME BAND is a recessed trough at the foot of the card — not a plate. It is
    drawn with INVERTED bevel logic: a dark inner shadow on the top/left edges
    (the wall the light can't reach as it presses IN) and a warm lit lip on the
    bottom/right (the far interior wall catching the top-left key). A faint cream
    fill is laid across the floor so the incised letters keep a LIT FACE and
    survive the 1x smoothscale — an un-filled incision crushes to black at scale.
  * The NAME sits in that trough in warm highlight cream with a dark shadow
    stamp, so each letterform reads carved: dark on the pressed face, warm light
    catching the rim.
  * The PRICE is debossed into a SECOND small trough in the right collar at disc
    mid-height — the identical dark-inner / light-lip recess, holding the coin
    glyph + cream digits. It is deliberately NOT a struck coin / facet gem (that
    is intaglio-seal grammar); it is the same cut material as the name.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200, no downscale) plus a real-scale 1x strip so the carved-type-at-1x
risk is visible. Not wired into the live store; writes
docs/store_card_v4_r2/engraved-slab/round_1.png.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import math
import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import store_catalog
from game.hud import _font
from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    cabochon, cabochon_glass, blit_thumb, facet_gem, plain_text, soft_glow,
    coin_glyph, _glyph_base, _rarity, font, m, SS,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_DEEP, CARD_RING_BRIGHT,
    GEM_R, RARITY, MYSTERY,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero disc radius (logical). Fills most of the block; the carved name band
# reads in front of its lower rim like a ledge cut into the same stone.
R = 34

# Cream shared by the name AND the price numerals — one type value so gold never
# has to carry legibility on the carved face (only the coin glyph is gold).
CREAM_LABEL = (236, 230, 208)


def _hero_specular(surf, cx, cy, r):
    """A guaranteed high-value glass specular on the upper-left rim, drawn OVER
    the cabochon glass so EVERY skin keeps a lit crescent — dark heroes (e.g.
    skin_tophat) no longer read as a flat low-value blob under the dome."""
    ec = r + m(3)
    edge = pygame.Surface((ec * 2 + m(2), ec * 2 + m(2)), pygame.SRCALPHA)
    steps = max(2, m(4))
    for k in range(steps):
        a = int(210 * (1 - k / steps))
        rk = r - m(1) - k
        if rk <= 0:
            break
        pygame.draw.arc(edge, (255, 250, 234, a),
                        (ec - rk, ec - rk, rk * 2, rk * 2),
                        math.radians(110), math.radians(198), max(1, m(1)))
    surf.blit(edge, (cx - ec, cy - ec), special_flags=pygame.BLEND_ADD)
    # a single hot pip upper-left so there is always a crisp catch-light.
    pr = max(1, int(r * 0.17))
    pip = pygame.Surface((pr * 2 + m(2), pr * 2 + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 235), (pr + m(1), pr + m(1)), pr)
    off = int(r * 0.66)
    surf.blit(pip, (cx - pr - off, cy - pr - off),
              special_flags=pygame.BLEND_ADD)


def _carved_trough(surf, rect, radius):
    """Cut a recess INTO the carved surface with INVERTED bevel logic, so the
    hollow reads as pressed-in stone rather than a raised plate:

      * a deep floor darker than the card body (the material removed),
      * a faint CREAM fill across it so anything set inside keeps a lit face and
        survives the 1x smoothscale (a black-floored incision crushes at scale),
      * a DARK inner shadow banked on the TOP+LEFT walls (the light can't reach
        the near lip it presses past),
      * a WARM LIT lip on the BOTTOM+RIGHT (the far interior wall catches the
        top-left key),
      * a crisp dark keyline round the mouth so the cut edge is defined.
    """
    w, h = rect.w, rect.h
    # MANDATORY faint cream fill laid straight over the body — a lit floor face
    # (cream at the top where the key reaches, dropping to a warm shadow at the
    # foot) so incised type keeps a lit face and clears the body L* at 1x. The
    # RECESS read is carried by the inverted bevel below, not by darkening the
    # floor (a dark-floored incision crushes to black at scale).
    cream = vgrad_stops(w, h, radius,
                        [(0.0, (238, 228, 202)), (1.0, (44, 38, 50))], alpha=50)
    surf.blit(cream, rect.topleft)

    depth = max(2, m(3))
    # dark inner shadow -> keep only TOP+LEFT via an upper-left triangular mask.
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(depth):
        a = int(190 * (1 - i / depth))
        pygame.draw.rect(sh, (5, 5, 15, a), (i, i, w - 2 * i, h - 2 * i),
                         width=max(1, m(0.9)), border_radius=max(1, radius - i))
    mtl = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mtl, (255, 255, 255, 255), [(0, 0), (w, 0), (0, h)])
    sh.blit(mtl, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(sh, rect.topleft)

    # warm lit lip -> keep only BOTTOM+RIGHT via a lower-right triangular mask.
    lip = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(depth):
        a = int(120 * (1 - i / depth))
        pygame.draw.rect(lip, (96, 78, 46, a), (i, i, w - 2 * i, h - 2 * i),
                         width=max(1, m(0.9)), border_radius=max(1, radius - i))
    mbr = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mbr, (255, 255, 255, 255), [(w, 0), (w, h), (0, h)])
    lip.blit(mbr, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lip, rect.topleft)

    # crisp dark mouth keyline defining the cut edge in the surface.
    pygame.draw.rect(surf, (4, 4, 12), rect, width=max(1, m(1)),
                     border_radius=radius)


def _name_in_trough(surf, name, cx, cy, max_w):
    """Carved item name: warm highlight cream with a dark shadow stamp + dark
    keyline, auto-shrunk from 9.5pt until it fits `max_w`. The warm fill is the
    lit letter face; the dark keyline is the pressed edge — together they read
    as incised, and (unlike unfilled incised type) they survive the 1x."""
    warm = (230, 215, 175)
    sz = 9.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 6.0:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), warm, shadow_a=170,
               weight=m(0.9), keyline=(8, 8, 18), kw=m(0.8))


def render_card(sid):
    """Draw ONE engraved-slab card onto a fresh SS panel (324x200) and return it
    (drawn directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(36)          # disc high; band cuts the foot

    # ── SHELL (locked order) — the carved block itself ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── HERO DISC ──
    soft_glow(big, cx, cy, m(R + 3), pal["glow"], 34, layers=9)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(big, sid, cx, cy, m(R) * 0.66)
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    _hero_specular(big, cx, cy, m(R))              # luminance-independent catch-light

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE (debossed into a small trough in the right collar) ──
    # Same carved recess as the name, holding the coin glyph + cream digits — the
    # price is CUT into the block, not a floating pill or struck medallion.
    price_str = "480"
    pf = font(7.0)
    num_w = _glyph_base(price_str, pf, 0).get_width()
    coin_r = m(4.5)
    pad = m(6)
    gapc = m(4)
    pt_w = pad + coin_r * 2 + gapc + num_w + pad
    pt_h = m(15)
    pt = pygame.Rect(rect.right - m(7) - pt_w, cy - pt_h // 2, pt_w, pt_h)
    _carved_trough(big, pt, m(6))
    coin_cx = pt.x + pad + coin_r
    coin_glyph(big, coin_cx, pt.centery, coin_r)
    plain_text(big, price_str, pf, (coin_cx + coin_r + gapc + num_w // 2,
                                    pt.centery), CREAM_LABEL, shadow_a=0,
               weight=m(0.8), keyline=(8, 8, 18), kw=m(0.7))

    # ── NAME BAND (carved recess at the foot) ──
    band_h = m(19)
    band = pygame.Rect(rect.x + m(5), rect.bottom - m(4) - band_h,
                       rect.w - m(10), band_h)
    _carved_trough(big, band, m(7))
    _name_in_trough(big, name.upper(), band.centerx, band.centery,
                    band.w - m(16))

    return big


# ── review sheet ──────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 x 200 (SS panels, no downscale)
MARGIN = 10
GUTTER = 8
HEADER_H = 30
FOOTER_H = 22
STRIP_LABEL_H = 20
STRIP_H = CARD_H                              # real-scale 1x cards (162x100)

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + STRIP_LABEL_H + STRIP_H
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(22, True)
ffont = _font(18, True)
sfont = _font(15, True)
htxt = hfont.render("store_card_v4_r2 — engraved-slab — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
panels = []
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel = render_card(sid)
    panels.append(panel)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# 1x real-scale strip: smoothscale each SS panel down to the live 162x100 card so
# the carved-type-at-1x survival is visible in the same sheet.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1x, 162x100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v4_r2/engraved-slab/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# ── L* probes (no image display): confirm both carved recesses read ABOVE the
#    card body floor at 1x — i.e. the cream fill keeps the incised type lit. ──
def _lstar(rgb):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb[:3])
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 903.3 * y if y <= 0.008856 else 116 * y ** (1 / 3) - 16


def _region_peak(surf, x0, y0, x1, y1):
    """Brightest L* over a box — the recess's LIT FACE (cream floor / incised
    letter face). The carved read must keep this above the body floor so the
    type never crushes black at 1x."""
    best = -1.0
    for yy in range(y0, y1):
        for xx in range(x0, x1):
            best = max(best, _lstar(surf.get_at((xx, yy))))
    return best


epic = pygame.transform.smoothscale(render_card("skin_prism"), (CARD_W, CARD_H))
# 1x check: the card body floor, vs the LIT FACE peak inside each carved recess.
body = epic.get_at((int(CARD_W * 0.16), int(CARD_H * 0.30)))
name_peak = _region_peak(epic, 12, 72, 150, 90)     # name band region
price_peak = _region_peak(epic, 116, 30, 150, 45)   # right-collar price trough
print(f"  body            rgb={tuple(body)[:3]}  L*={_lstar(body):5.1f}")
print(f"  name_trough lit L*={name_peak:5.1f}  (must exceed body)")
print(f"  price_trough lit L*={price_peak:5.1f}  (must exceed body)")
