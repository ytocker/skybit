"""woven-carbon — store_card_v4_r4 concept, round 2 headless render.

AD notes applied:
  * Weave pitch widened m(3)→m(4) and light-cell base lifted (26,25,32)→(40,39,50)
    so the 2/2 twill diagonal rib is the readable feature, not the glints.
  * Pure-255 specular glints replaced with tier-tinted, capped glints (≤200/channel).
  * Directional sheen alpha scales with tier richness so LEGENDARY reads visibly hotter.
  * Price plaque: a carbon-shard rounded-rect with a 1px specular lip anchors the
    debossed numeral into a defined surface rather than floating above the card body.
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
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base, _stamp_bold,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36

# Lifted graphite pair — +4/+14 luma so the diagonal rib reads at 1×
WEAVE_DARK  = (18, 18, 24)
WEAVE_LIGHT = (40, 39, 50)


def _weave_band(big, rect, plinth_top, rad, pal):
    """2/2 twill carbon weave with wider pitch and tier-scaled iridescent sheen.

    Fix vs r1:
      * cell = m(4) (was m(3)) — diagonal rib is the readable feature now
      * WEAVE_LIGHT lifted +14 luma — contrast between dark/light cells visible at 1×
      * Glints tier-tinted and capped at 200/channel — no blown-white specular
      * Sheen alpha scales with tier luma so LEGENDARY is noticeably hotter"""
    ph = rect.bottom - plinth_top
    band = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    band.fill((*WEAVE_DARK, 255))

    cell = m(4)    # wider pitch: diagonal rib legible, no moiré at 1×
    ncols = rect.w // cell + 2
    nrows = ph    // cell + 2

    # Tier-tinted glints, capped so no channel exceeds 200 (no pure white)
    raw_glint = lerp_color(pal["glow"], (180, 185, 200), 0.35)
    glint = tuple(min(200, c) for c in raw_glint)
    gcell = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.line(gcell, (*glint, 90), (0, 0), (cell - 1, cell // 2), 1)

    for row in range(nrows):
        y = row * cell
        for col in range(ncols):
            x = col * cell
            light = ((col - row) % 4) < 2
            pygame.draw.rect(band, WEAVE_LIGHT if light else WEAVE_DARK,
                             (x, y, cell, cell))
            if light:
                band.blit(gcell, (x, y))

    # Broad directional sheen — amplitude scales with tier richness
    tier_lum   = sum(pal["glow"]) // 3
    sheen_a    = max(18, min(42, tier_lum // 7))
    soft_glow(band, rect.w, ph // 2, m(40), pal["glow"], sheen_a, layers=8)

    # Clip to card's rounded bottom corners
    body_mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=rad)
    band.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))


def _clear_coat(big, cx, cy, r):
    soft_glow(big, cx, cy, r, (6, 6, 10), 100, layers=8)


def _deboss(big, txt, f, center, core, weight):
    cx, cy = center
    base = _stamp_bold(_glyph_base(txt, f, 0), weight)

    def stamp(col, dx, dy, a):
        img = base.copy()
        img.fill((*col, 255), special_flags=pygame.BLEND_RGBA_MULT)
        if a < 255:
            img.set_alpha(a)
        big.blit(img, img.get_rect(center=(cx + dx, cy + dy)))

    stamp(lerp_color(core, WHITE, 0.5), -m(1), -m(1), 150)
    stamp((12, 12, 16), m(1), m(1), 180)
    stamp(core, 0, 0, 255)


def _deboss_price(big, cx, cy, price, pal):
    """Frameless deboss anchored on a carbon-shard plaque with a specular lip."""
    f = font(11.0)
    txt = f"{price}"
    glyph_h = _glyph_base(txt, f, 0).get_height()
    nw      = _glyph_base(txt, f, 0).get_width()
    coin_d  = m(11)
    gap     = m(3)
    total   = coin_d + gap + nw

    # Carbon-shard plaque: anchors the numeral into a defined material surface
    plaque_w = total + m(10)
    plaque_h = glyph_h + m(10)
    px0 = cx - plaque_w // 2
    py0 = cy - plaque_h // 2
    plaque_surf = pygame.Surface((plaque_w, plaque_h), pygame.SRCALPHA)
    pygame.draw.rect(plaque_surf, (10, 10, 16, 175),
                     (0, 0, plaque_w, plaque_h), border_radius=m(2))
    big.blit(plaque_surf, (px0, py0))
    # 1px specular lip — reads as a carbon shard's bevelled edge
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 100),
                     (px0, py0, plaque_w, plaque_h), 1, border_radius=m(2))

    # Clear-coat mute over the plaque for a clean deboss bed
    _clear_coat(big, cx, cy, m(11))

    x0 = cx - total // 2
    coin_glyph(big, x0 + coin_d // 2, cy, coin_d // 2)
    platinum = lerp_color((180, 185, 200), WHITE, 0.4)
    _deboss(big, txt, f, (x0 + coin_d + gap + nw // 2, cy), platinum, m(0.9))


def _deboss_name(big, name, cx, cy, max_w):
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    nw = _glyph_base(name, f, 0).get_width()

    half = nw // 2 + m(4)
    step = m(10)
    xx = cx - half
    while xx <= cx + half:
        _clear_coat(big, xx, cy, m(9))
        xx += step

    _deboss(big, name, f, (cx, cy), (190, 188, 200), m(0.95))


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

    _weave_band(big, rect, plinth_top, rad, pal)

    bevel_y = plinth_top - max(1, m(1))
    bevel_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(bevel_surf, (*CARD_RING_BRIGHT, 180),
                     (rect.left, bevel_y), (rect.right - 1, bevel_y),
                     max(1, m(1)))
    big.blit(bevel_surf, (0, 0))
    pygame.draw.line(big, (3, 4, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))

    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    _deboss_price(big, rect.right - m(23), rect.y + m(48), price, pal)
    _deboss_name(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(22))

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
htxt = hfont.render("store_card_v4_r4 — woven-carbon — round 2", True,
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

out = "/home/user/skybit/docs/store_card_v4_r4/woven-carbon/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
