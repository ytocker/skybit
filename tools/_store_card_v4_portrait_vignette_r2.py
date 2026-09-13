"""portrait-vignette — store_card_v4 concept, round 2 headless render.

A theatrical, disc-led card. The standard indigo body is overlaid with a
SPOTLIGHT VIGNETTE, but round 2 fixes the light so it reads as a real stage
lamp rather than only subtracted black:

  * The dark veil now falls off SHALLOW (exp 1.1) over a WIDE reach, so a lit
    indigo COLLAR survives in the annulus from the disc rim out to ~R60 while
    the four corners still sink to shadow. The eye catches a lit halo hugging
    the disc, then fade-out corners.
  * A warm ADDITIVE glow core is blit at the spotlight centre after the veil,
    so the lamp ADDS light (not just removes it) and the collar reads warm.
  * The disc is nudged down (cy = m(43)) for top headroom so its aura clears
    the bevel.
  * Every hero disc carries a guaranteed high-value glass specular crescent so
    dark-skin heroes (e.g. skin_tophat) still show a lit rim regardless of
    thumbnail luminance.
  * The frosted bar's price numerals share the name's cream so gold-on-plate
    never fights for contrast; only the coin glyph keeps the gold tone.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200, no downscale) + a real-scale 1x strip (162x100). Not wired into the
live store; writes docs/store_card_v4/portrait-vignette/round_2.png.
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
    GEM_R, RARITY, MYSTERY, NEAR_BLACK,
)

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero disc: R=38 fills nearly the full width, centred high (with headroom) so
# the frosted name/price bar clears its lower rim and the corners can shadow.
R = 38

# Cream shared by the name AND the price numerals — one type value so gold never
# has to carry legibility on the frosted plate (only the coin glyph is gold).
CREAM_LABEL = (236, 230, 208)


def _spotlight_vignette(surf, rect, spot, peak=104, reach=None, falloff=1.1):
    """Lay a radial stage-lamp veil over the indigo body: a uniform NEAR_BLACK
    sheet with a SHALLOW, WIDE light disc subtracted at `spot`, so a lit indigo
    COLLAR survives out to ~R60 and only the far corners keep the full veil.

    The light mask is built with BLEND_RGBA_MAX rings so the removed-veil alpha
    at distance d is exactly peak*(1-d/reach)**falloff — a clean radial falloff
    with no additive double-counting, hence no banding. Clipped to the body."""
    w, h = rect.w, rect.h
    sx, sy = spot
    if reach is None:
        # Reach well past the disc so the collar stays lit; corners (~0.9*reach)
        # still fall deep into the veil.
        reach = int(math.hypot(w, h) * 0.66)
    vig = pygame.Surface((w, h), pygame.SRCALPHA)
    vig.fill((*NEAR_BLACK, peak))
    light = pygame.Surface((w, h), pygame.SRCALPHA)
    layers = 84                                    # dense rings => sub-2 alpha steps
    for i in range(layers, 0, -1):
        r = int(reach * i / layers)
        if r <= 0:
            continue
        frac = i / layers                          # == r / reach
        a = int(round(peak * (1 - frac) ** falloff))
        if a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (255, 255, 255, a), (r + 1, r + 1), r)
        light.blit(g, (sx - r - 1, sy - r - 1),
                   special_flags=pygame.BLEND_RGBA_MAX)
    vig.blit(light, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=m(CARD_RAD))
    vig.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(vig, rect.topleft)


def _warm_core(surf, cx, cy, radius, color=(30, 20, 8), peak=38, layers=24,
               exp=1.3):
    """A soft warm ADDITIVE glow at the lamp centre — the light the spotlight
    ADDS. Reaches out over the collar so the indigo annulus round the disc reads
    as genuinely lit (not merely un-shadowed black)."""
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak * (1 - (i - 1) / layers) ** exp)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


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


def _name_on_bar(surf, name, cx, cy, max_w):
    """Cream item name with a tight dark keyline, auto-shrunk from 9.5pt in 0.5
    steps until it fits `max_w` (the bar minus the reserved price cell)."""
    sz = 9.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 6.0:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), CREAM_LABEL, shadow_a=150,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(0.8))


def render_card(sid):
    """Draw ONE portrait-vignette card onto a fresh SS panel (324x200) and
    return it (drawn directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    cx, cy = rect.centerx, rect.y + m(43)          # top headroom for the aura

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    # spotlight over the bright indigo, tracking the disc centre: shallow+wide
    # veil first, then the warm additive lamp core so the collar reads lit.
    _spotlight_vignette(big, rect, (cx - rect.x, cy - rect.y), peak=96)
    _warm_core(big, cx, cy, m(60))
    # softened, shallower AO so the bottom corners settle to shadow (L~8-12)
    # rather than crushing to pure black under the veil.
    contact_shadow(big, rect, rad, m(7), alpha=70)
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

    # ── FROSTED NAME/PRICE BAR — one full-width plate flush at the bottom, in
    #    front of the disc's lower rim like a lit stage ledge. ──
    bar_h = m(16)
    bar_bottom = rect.bottom - m(2)
    bar = pygame.Rect(rect.x + m(2), bar_bottom - bar_h, rect.w - m(4), bar_h)
    frosted = vgrad_stops(bar.w, bar.h, m(6), [(0.0, CABO_LO), (1.0, CABO_HI)],
                          alpha=200)
    big.blit(frosted, bar.topleft)
    # thin gold kiss along the bar's top edge so it reads as frosted glass.
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 140),
                     (bar.x + m(6), bar.top), (bar.right - m(6), bar.top),
                     max(1, m(1)))
    bar_cy = bar.centery

    # price — coin glyph (the ONE gold accent) + CREAM numerals so the number
    # never fights the frosted plate for contrast.
    price_str = "480"
    pf = font(9.0)
    num_w = _glyph_base(price_str, pf, 0).get_width()
    coin_r = m(5)
    price_x = bar.right - m(8) - num_w - m(16) + coin_r  # coin cell centre
    coin_glyph(big, price_x, bar_cy, coin_r)
    plain_text(big, price_str, pf, (price_x + m(16), bar_cy), CREAM_LABEL,
               shadow_a=0, weight=m(0.9), keyline=(6, 6, 16), kw=m(0.7))

    # name — cream, auto-fit into the bar minus the reserved price cell.
    max_w = rect.w - m(50)
    name_cx = bar.x + m(8) + max_w // 2
    _name_on_bar(big, name.upper(), name_cx, bar_cy, max_w)

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
htxt = hfont.render("store_card_v4 — portrait-vignette — round 2", True,
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

# 1x real-scale strip: smoothscale each SS panel down to the live 162x100 card.
strip_label_y = panel_y + PANEL_H + FOOTER_H
ltxt = sfont.render("real scale (1x, 162x100)", True, (200, 204, 220))
sheet.blit(ltxt, (MARGIN, strip_label_y + (STRIP_LABEL_H - ltxt.get_height()) // 2))
strip_y = strip_label_y + STRIP_LABEL_H
for i, panel in enumerate(panels):
    px = MARGIN + i * (PANEL_W + GUTTER)
    left = px + (PANEL_W - CARD_W) // 2
    small = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
    sheet.blit(small, (left, strip_y))

out = "/home/user/skybit/docs/store_card_v4/portrait-vignette/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())

# ── L* probes (no image display) so the collar/corner/disc targets are checked
#    numerically, per the AD notes, without ever viewing the PNG. ──
if "--probe" in sys.argv:
    def _lstar(rgb):
        def lin(c):
            c /= 255.0
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (lin(v) for v in rgb[:3])
        y = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return 903.3 * y if y <= 0.008856 else 116 * y ** (1 / 3) - 16

    epic = render_card("skin_prism")
    tophat = render_card("skin_tophat")           # RARE, dark jacket/top-hat
    # local disc centre in the SS panel
    r = pygame.Rect(m(_INSET), m(_INSET),
                    CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    dcx, dcy = r.centerx, r.y + m(43)
    d = m(50)
    probes = {
        "disc_center": (dcx, dcy),
        "collar_left": (dcx - d, dcy),
        "collar_right": (dcx + d, dcy),
        "collar_dnleft": (dcx - int(d * 0.7), dcy + int(d * 0.7)),
        "corner_TL": (r.x + m(16), r.y + m(16)),
        "corner_BL": (r.x + m(16), r.bottom - m(26)),
        "corner_BR": (r.right - m(16), r.bottom - m(26)),
    }
    for label, (x, y) in probes.items():
        c = epic.get_at((x, y))
        print(f"  {label:16s} rgb={tuple(c)[:3]} L*={_lstar(c):5.1f}")
    # dark-skin rescue check: scan the upper-left rim band of skin_tophat for its
    # brightest specular pixel — it must be a genuine high-value catch-light.
    best = 0.0
    for ang in range(120, 205, 5):
        rr = m(R) - m(4)
        px = dcx + int(rr * math.cos(math.radians(ang)))
        py = dcy + int(rr * math.sin(math.radians(ang)))
        best = max(best, _lstar(tophat.get_at((px, py))))
    print(f"  tophat_specular_peak L*={best:5.1f}")
