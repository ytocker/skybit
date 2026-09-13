"""enamel-inlay — store_card_v4_r4 concept, round 2 headless render.

AD notes applied:
  * Enamel fill saturation raised: less aggressive dark-shift so tier hue fills ~55%
    of band height (not just a 6px sliver).  Shadows carry tier hue (RARE = blue-black).
  * LEGENDARY enamel changed to deep emerald to break the gold-on-gold (93,74,41)
    vs wall (236,202,116) same-hue clash.
  * Price cell: square corners (border_radius=0 = minted-channel edge), drop shadow
    removed, gloss ramp replaced with a thin diagonal streak + dark top-edge recess
    so the numeral reads pressed-in rather than raised on a floating chip.
  * Band gloss changed from full horizontal ramp to a compact soft hotspot so the
    enamel reads vitreous rather than matte-washed.
  * Dark wall shadow tier-tinted so shadows carry rarity hue to the bottom corners.
"""
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys

sys.path.insert(0, "/home/user/skybit")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import store_catalog
from game.hud import _font
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36


def _is_legendary(pal):
    g = pal["gem"]
    return g[0] > 200 and g[1] > 140 and g[2] < 130


def _enamel_stops(pal):
    """Tier-reactive vitreous enamel ramp.

    Changes from r1: less aggressive dark-shift so jewel hue fills the field
    rather than only a 6px sliver.  LEGENDARY gets deep emerald instead of
    gold to break the gold-on-gold cloisonné wall conflict."""
    gem = pal["gem"]
    if _is_legendary(pal):
        # Deep emerald: distinct from the gold CARD_RING_BRIGHT wall
        return [(0.0, (36, 100, 54)), (0.55, (26, 72, 38)), (1.0, (15, 44, 24))]
    return [
        (0.0,  lerp_color(gem, (4,  4, 16), 0.26)),
        (0.55, lerp_color(gem, (4,  4, 16), 0.46)),
        (1.0,  lerp_color(gem, (8,  8, 28), 0.56)),
    ]


def _enamel_band(big, rect, plinth_top, rad, pal):
    """Cloisonné enamel channel.

    Changes from r1:
      * Full horizontal gloss ramp replaced with a compact soft hotspot so the
        surface reads "vitreous glass" not "washed-out paint".
      * Wall inner shadow tier-tinted so rarity hue bleeds into the bottom corners.
      * Specular oval hotspot kept; squash unchanged."""
    bx, by = rect.left, plinth_top
    bw = rect.w
    bh = rect.bottom - plinth_top

    moff = rect.y - plinth_top
    body_mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255),
                     (0, moff, bw, rect.h), border_radius=rad)

    # Deep vitreous jewel fill — richer saturation, wider chromatic zone
    fill = vgrad_stops(bw, bh, 0, _enamel_stops(pal), 255, gamma=1.05)
    fill.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(fill, (bx, by))

    # Compact soft gloss hotspot replaces the full horizontal ramp:
    # reads as a glass catching a point light rather than a diffuse wash.
    gs = pygame.Surface((bw, bh), pygame.SRCALPHA)
    soft_glow(gs, int(bw * 0.28), int(bh * 0.22), m(18),
              (255, 255, 255), 32, layers=5)
    gs = pygame.transform.smoothscale(gs, (bw, int(bh * 0.60)))
    gmask = pygame.Surface(gs.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(gmask, (255, 255, 255, 255),
                     (0, moff, bw, rect.h), border_radius=rad)
    gs.blit(gmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(gs, (bx, by), special_flags=pygame.BLEND_ADD)

    # Specular oval hotspot for the wet-glass point highlight
    spec = pygame.Surface((bw, bh), pygame.SRCALPHA)
    soft_glow(spec, int(bw * 0.30), int(bh * 0.30), m(15),
              (250, 250, 255), 36, layers=6)
    spec = pygame.transform.smoothscale(spec, (bw, int(bh * 0.72)))
    smask = pygame.Surface(spec.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255),
                     (0, moff, bw, rect.h), border_radius=rad)
    spec.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(spec, (bx, by), special_flags=pygame.BLEND_ADD)

    # Raised cloisonné metal wall (square edges = minted-channel look)
    wall = pygame.Surface((bw, bh), pygame.SRCALPHA)
    ww = max(1, m(1.5))
    pygame.draw.rect(wall, (*CARD_RING_BRIGHT, 200), (0, 0, bw, bh),
                     width=ww, border_radius=0)
    # Dark inner shadow — tier-tinted so rarity hue reaches the bottom corners
    shadow_col = lerp_color(pal["deep"], (4, 5, 14), 0.78)
    pygame.draw.rect(wall, (*shadow_col, 170), (ww, ww, bw - 2*ww, bh - 2*ww),
                     width=max(1, m(1)), border_radius=0)
    wall.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(wall, (bx, by))


def _price_cell(big, cx, cy, price, pal):
    """Minted cloisonné numeral cell — square corners, recessed, no floating chip.

    Changes from r1:
      * border_radius=0 everywhere — square minted-channel corners match the band wall
      * Drop shadow removed; dark top-edge recess reads as pressed-in not raised
      * Gloss ramp replaced with a single thin diagonal streak only
      * Same tier-reactive fill as the band (including emerald for LEGENDARY)"""
    f = font(7.5)
    txt = f"{price}"
    nw   = _glyph_base(txt, f, 0).get_width()
    nh   = _glyph_base(txt, f, 0).get_height()
    padx = m(6)
    pady = m(4)
    w = nw + padx * 2
    h = nh + pady * 2
    x0, y0 = cx - w // 2, cy - h // 2

    # Deep enamel fill — square corners to match the band's minted edge
    fill = vgrad_stops(w, h, 0, _enamel_stops(pal), 255, gamma=1.05)
    big.blit(fill, (x0, y0))

    # Dark top-edge recess: numeral sits pressed into the enamel, not on top
    pygame.draw.line(big, (4, 5, 12),
                     (x0 + 1, y0 + 1), (x0 + w - 2, y0 + 1), max(1, m(1)))
    pygame.draw.line(big, (6, 7, 18),
                     (x0 + 1, y0 + 2), (x0 + w - 2, y0 + 2), max(1, m(1)))

    # Single thin diagonal gloss streak (vitreous, not a full white ramp)
    gl = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.line(gl, (255, 255, 255, 55),
                     (int(w * 0.15), int(h * 0.20)),
                     (int(w * 0.70), int(h * 0.60)), max(1, m(1)))
    big.blit(gl, (x0, y0), special_flags=pygame.BLEND_ADD)

    # Raised metal wall — square corners, same construction as the band wall
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 220), (x0, y0, w, h),
                     width=max(1, m(1)), border_radius=0)

    # Engraved near-white numeral
    plain_text(big, txt, f, (cx, cy),
               lerp_color(WHITE, (240, 240, 255), 0.2), shadow_a=0,
               weight=m(0.8), keyline=(6, 6, 16), kw=m(0.8))


def _name_on_band(big, name, cx, cy, max_w):
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    plain_text(big, name, f, (cx, cy), (230, 225, 240), shadow_a=150,
               weight=m(0.95), keyline=(4, 4, 12), kw=m(1.0))


def render_card(sid):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)

    _enamel_band(big, rect, plinth_top, rad, pal)

    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    _price_cell(big, rect.right - m(23), rect.y + m(48), price, pal)
    _name_on_band(big, name.upper(), rect.centerx, rect.y + m(81),
                  rect.w - m(22))

    return big


VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN = 10
GUTTER = 8
HEADER_H = 26
FOOTER_H = 22

sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(20, True)
ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r4 — enamel-inlay — round 2", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    panel = render_card(sid)
    sheet.blit(panel, (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4_r4/enamel-inlay/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
