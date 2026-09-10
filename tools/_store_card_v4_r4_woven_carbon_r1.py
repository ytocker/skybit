"""woven-carbon — store_card_v4_r4 concept, round 1 headless render.

Visual thesis: the card's bottom band is a real 2x2 twill carbon-fibre weave,
drawn cell-by-cell with an iridescent directional sheen, and the price is a
frameless debossed numeral pressed straight into the card body — no cartouche,
no shield, no plate. The material itself is the frame.

Construction:
  * Weave band fills plinth_top -> card floor. A grid of m(3) cells is tiled in
    a 2/2 twill draft (light run of 2 shifting one cell per row) alternating a
    dark graphite and a lighter graphite; each light cell gets a 1px diagonal
    specular glint, and a single broad soft_glow from the band's right edge lays
    the carbon shimmer across the whole field. Cell pitch is held at m(3) so the
    weave never beats into moiré at the /SS downscale.
  * Price is frameless: a soft near-black clear-coat patch mutes the ground
    locally for a clean bed, then the numeral is stamped as a deboss — a bright
    upper-left bevel highlight + a dark lower-right shadow around a cool platinum
    core — so it reads as pressed IN rather than sitting ON.
  * Name uses the same deboss bevel over a narrow clear-coat strip spanning its
    width, so it stays crisp against the busy weave.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review sheet at SS
(324x200 panels, no downscale). Not wired into the live store; writes
docs/store_card_v4_r4/woven-carbon/round_1.png.
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

# LOCKED card constants (from store_cards).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6

# Hero disc: R=36, left-leaning.
R = 36

# 2/2 twill tones — a graphite pair with just enough separation to read as
# woven tows without turning into a high-contrast checker.
WEAVE_DARK = (14, 14, 18)
WEAVE_LIGHT = (26, 25, 32)


def _weave_band(big, rect, plinth_top, rad, pal):
    """Tile a 2/2 twill carbon weave into the bottom band and lay an iridescent
    sheen over it. Drawn on a band-local surface so the sheen composites
    additively before the field is masked to the card's rounded floor."""
    ph = rect.bottom - plinth_top
    band = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    band.fill((*WEAVE_DARK, 255))

    cell = m(3)                                  # pitch >= m(2.5): moiré-safe
    ncols = rect.w // cell + 2
    nrows = ph // cell + 2

    # Specular glint colour: tier glow nudged toward cool white so the lit tows
    # pick up the rarity's hue as a faint iridescence.
    glint = lerp_color(pal["glow"], (180, 180, 200), 0.3)
    gcell = pygame.Surface((cell, cell), pygame.SRCALPHA)
    pygame.draw.line(gcell, (*glint, 74), (0, 0), (cell - 1, cell // 2), 1)

    for row in range(nrows):
        y = row * cell
        for col in range(ncols):
            x = col * cell
            # 2/2 twill: a 2-wide warp float that steps one cell per row, which
            # is what gives carbon its diagonal rib.
            light = ((col - row) % 4) < 2
            pygame.draw.rect(band, WEAVE_LIGHT if light else WEAVE_DARK,
                             (x, y, cell, cell))
            if light:
                band.blit(gcell, (x, y))

    # Broad directional sheen from the band's right edge — the whole-field
    # carbon shimmer, kept low so it reads as material, not a hotspot.
    soft_glow(band, rect.w, ph // 2, m(40), pal["glow"], 20, layers=8)

    # Clip to the card's rounded bottom corners so the weave seats flush.
    body_mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(body_mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=rad)
    band.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))


def _clear_coat(big, cx, cy, r):
    """A soft near-black patch that mutes the busy ground locally so debossed
    type gets a clean bed to press into."""
    soft_glow(big, cx, cy, r, (6, 6, 10), 100, layers=8)


def _deboss(big, txt, f, center, core, weight):
    """Stamp type as a deboss: a bright upper-left bevel highlight and a dark
    lower-right shadow bracketing a solid core, so the numeral/name reads as
    pressed into the card rather than laid on top of it."""
    cx, cy = center
    base = _stamp_bold(_glyph_base(txt, f, 0), weight)

    def stamp(col, dx, dy, a):
        img = base.copy()
        img.fill((*col, 255), special_flags=pygame.BLEND_RGBA_MULT)
        if a < 255:
            img.set_alpha(a)
        big.blit(img, img.get_rect(center=(cx + dx, cy + dy)))

    stamp(lerp_color(core, WHITE, 0.5), -m(1), -m(1), 150)   # upper-left bevel
    stamp((12, 12, 16), m(1), m(1), 180)                     # lower-right shadow
    stamp(core, 0, 0, 255)                                   # core


def _deboss_price(big, cx, cy, price, pal):
    """Frameless price — clear-coat bed + platinum deboss numeral, no cartouche."""
    f = font(11.0)
    txt = f"{price}"
    nw = _glyph_base(txt, f, 0).get_width()
    coin_d = m(11)
    gap = m(3)
    total = coin_d + gap + nw

    _clear_coat(big, cx, cy, m(12))

    x0 = cx - total // 2
    coin_glyph(big, x0 + coin_d // 2, cy, coin_d // 2)
    platinum = lerp_color((180, 185, 200), WHITE, 0.4)
    _deboss(big, txt, f, (x0 + coin_d + gap + nw // 2, cy), platinum, m(0.9))


def _deboss_name(big, name, cx, cy, max_w):
    """Debossed cool-grey name over a narrow clear-coat strip spanning its
    width, auto-shrunk to fit the band."""
    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    nw = _glyph_base(name, f, 0).get_width()

    # Clear-coat strip: overlapping dabs across the name width mute the weave to
    # a clean bed without a hard-edged shape.
    half = nw // 2 + m(4)
    step = m(10)
    xx = cx - half
    while xx <= cx + half:
        _clear_coat(big, xx, cy, m(9))
        xx += step

    _deboss(big, name, f, (cx, cy), (190, 188, 200), m(0.95))


def render_card(sid):
    """Draw ONE woven-carbon card onto a fresh SS panel (324x200) and return it."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)

    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    # ── SHELL (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── LOCKED positional skeleton ──
    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)

    # ── WOVEN-CARBON BAND ──
    _weave_band(big, rect, plinth_top, rad, pal)

    # ── BAND TOP SEAM — a 1px lit micro-bevel over the dark keyline so the
    #    weave reads as a discrete plate seated into the shell. ──
    bevel_y = plinth_top - max(1, m(1))
    bevel_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(bevel_surf, (*CARD_RING_BRIGHT, 180),
                     (rect.left, bevel_y), (rect.right - 1, bevel_y),
                     max(1, m(1)))
    big.blit(bevel_surf, (0, 0))
    pygame.draw.line(big, (3, 4, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))

    # ── HERO DISC (R=36, left-leaning) ──
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── FRAMELESS PRICE — debossed numeral pressed into the card body. ──
    _deboss_price(big, rect.right - m(23), rect.y + m(48), price, pal)

    # ── NAME — debossed, centred across the weave band. ──
    _deboss_name(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(22))

    return big


# ── review sheet ──────────────────────────────────────────────────────────────
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
htxt = hfont.render("store_card_v4_r4 — woven-carbon — round 1", True,
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

out = "/home/user/skybit/docs/store_card_v4_r4/woven-carbon/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
