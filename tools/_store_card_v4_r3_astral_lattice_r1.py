"""astral-lattice — store_card_v4_r3 concept, round 1 headless render.

A celestial star-chart card. The standard indigo body carries a near-black
CELESTIAL BAND at the foot (CARD_B darkened, kept slightly narrower than the
plinth concepts). Across that band — and wiring UP out of it toward the hero
disc — runs a constellation of straight DIAGONAL gold hairline star-lines
linking a handful of glint nodes; at least one line lands on the disc's gold
bezel, so the band and the hero read as one wired lattice rather than two
stacked slabs. The item name sits in warm gilt across the band over a subtle
darkening vgrad that keeps it legible where the hairlines cross. The price is a
digit-only phosphor stencil (glowing numerals in the rarity tint) right-biased
above the band — no chip body.

Headless (SDL dummy) -> a 3-up RARE/EPIC/LEGENDARY review strip authored at SS
(324x200 panels, no downscale). Not wired into the live store; writes
docs/store_card_v4_r3/astral-lattice/round_1.png.
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

from game.draw import lerp_color, WHITE
from game.hud import _font
from game import store_catalog
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, _glyph_base, _rarity,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, NEAR_BLACK,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36                       # hero disc radius (logical), left-leaning

# The band's near-black ground: CARD_B pulled halfway to black so the gold
# hairlines and gilt name read as light-on-void, the star-chart contrast.
BAND_TOP = lerp_color(CARD_B, NEAR_BLACK, 0.42)
BAND_BOT = lerp_color(CARD_B, NEAR_BLACK, 0.78)
GILT = (238, 206, 132)       # warm gilt for the name


def _draw_lattice(surf, rect, band, cx, cy, rd, pal):
    """The constellation: diagonal gold hairlines linking gem-pip nodes, with a
    line rising from the band to a node landing on the disc's gold bezel. Lines
    are laid on ONE alpha layer (so the hairline alpha blends instead of
    overwriting the card body), then the pips + their twinkle are added on top."""
    # Node on the disc's gold bezel, lower-right where the band can reach it.
    ba = math.radians(24)
    bez = (cx + rd * math.cos(ba), cy + rd * math.sin(ba))
    # A rising diagonal chain across the band and up into the right field, so the
    # eye is carried band -> disc and band -> price.
    p_low = (rect.x + m(78), band.top + m(10))          # band, just right of disc
    p_mid = (rect.right - m(58), band.top + m(3))        # band, far right
    p_up = (rect.right - m(46), rect.centery - m(4))     # up toward the price
    p_top = (rect.right - m(30), rect.y + m(42))         # up toward the gem crest
    nodes = [bez, p_low, p_mid, p_up, p_top]
    # Diagonal-only links (no axis-aligned Manhattan runs); p_low->bez wires the
    # band up onto the bezel; p_up->bez closes a triangle for a charted feel.
    links = [(p_low, bez), (p_low, p_mid), (p_mid, p_up),
             (p_up, p_top), (p_up, bez)]

    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    ox, oy = rect.topleft
    for a, b in links:
        pygame.draw.line(layer, (*CARD_RING_BRIGHT, 72),
                         (a[0] - ox, a[1] - oy), (b[0] - ox, b[1] - oy),
                         max(1, m(0.7)))
    surf.blit(layer, rect.topleft)

    # Glint nodes: a soft tier twinkle, a gem pip, a hot white core.
    rp = max(2, m(2.4))
    for nx, ny in nodes:
        soft_glow(surf, int(nx), int(ny), m(4), pal["glow"], 34, layers=6)
        pip = pygame.Surface((rp * 2 + m(2), rp * 2 + m(2)), pygame.SRCALPHA)
        c = rp + m(1)
        pygame.draw.circle(pip, (*pal["gem"], 255), (c, c), rp)
        pygame.draw.circle(pip, (*lerp_color(pal["gem"], WHITE, 0.85), 255),
                           (c, c), max(1, int(rp * 0.42)))
        surf.blit(pip, (int(nx) - c, int(ny) - c))


def _name_gilt(surf, name, band, disc_right):
    """Warm gilt name across the band's clear right zone (right of the disc),
    over a subtle darkening vgrad so the hairlines never fight the glyphs. Kept
    high-contrast by a crisp near-black keyline under the warm fill."""
    zone_l = int(disc_right + m(4))
    zone_r = band.right - m(8)
    cxn = (zone_l + zone_r) // 2
    max_w = zone_r - zone_l
    # subtle darkening pad beneath the glyphs (legibility floor on the band)
    pad_h = m(19)
    pad = vgrad_stops(max_w + m(12), pad_h, m(6),
                      [(0.0, (*NEAR_BLACK, 0)), (0.5, (*NEAR_BLACK, 150)),
                       (1.0, (*NEAR_BLACK, 0))], alpha=255)
    surf.blit(pad, (cxn - (max_w + m(12)) // 2, band.centery - pad_h // 2))

    sz = 12.0
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 7.0:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cxn, band.centery), GILT, shadow_a=0,
               weight=m(0.9), keyline=(4, 4, 12), kw=m(0.9))


def _price_phosphor(surf, text, cx, cy, pal):
    """Digit-only phosphor stencil: a soft tier glow bloom, a hairline bare coin
    token, then glowing stencil-cut numerals in the rarity tint. No chip body."""
    f = font(11.5)
    nw = _glyph_base(text, f, 0).get_width()
    coin_r = m(5)
    gap = m(6)
    total = coin_r * 2 + gap + nw
    x0 = cx - total // 2
    coin_cx = x0 + coin_r
    num_cx = x0 + coin_r * 2 + gap + nw // 2

    # phosphor bloom behind the whole readout
    soft_glow(surf, num_cx, cy, m(15), pal["glow"], 30, layers=8)
    # hairline bare coin outline (a struck token, not a filled coin)
    pygame.draw.circle(surf, (*CARD_RING_BRIGHT, 200), (coin_cx, cy), coin_r,
                       max(1, m(0.8)))
    pygame.draw.circle(surf, (*CARD_RING_BRIGHT, 90), (coin_cx, cy),
                       coin_r - m(1.4), max(1, m(0.7)))
    # stencil-cut numerals: hot phosphor core in the rarity glow tint
    phosphor = lerp_color(pal["glow"], WHITE, 0.30)
    plain_text(surf, text, f, (num_cx, cy), phosphor, shadow_a=0,
               weight=m(1.0), keyline=(*lerp_color(pal["deep"], NEAR_BLACK, 0.4),),
               kw=m(0.7))


def render_card(sid):
    """Draw ONE astral-lattice card onto a fresh SS panel (324x200) and return
    it (authored directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid).upper()
    price = f"{store_catalog.cost(sid):,}"

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

    # ── CELESTIAL BAND — near-black strip at the foot, slightly narrower than a
    #    plinth so it reads as a horizon strip, not a full base. Drawn BEFORE the
    #    lattice so the hairlines + nodes sit on top of it. ──
    band = pygame.Rect(rect.x + m(9), rect.bottom - m(28),
                       rect.w - m(18), m(20))
    band_body = vgrad_stops(band.w, band.h, m(6),
                            [(0.0, BAND_TOP), (1.0, BAND_BOT)], alpha=236)
    big.blit(band_body, band.topleft)
    pygame.draw.rect(big, (2, 3, 10), band, width=max(1, m(1)),
                     border_radius=m(6))
    # a faint gold kiss along the band's top edge — the horizon line
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 90),
                     (band.x + m(8), band.top), (band.right - m(8), band.top),
                     max(1, m(0.8)))

    # ── HERO DISC (left-leaning) ──
    cx = rect.left + m(40)
    cy = rect.centery
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── LATTICE — diagonal gold hairlines + gem-pip nodes, wired band -> bezel ──
    _draw_lattice(big, rect, band, cx, cy, m(R), pal)

    # ── GEM CREST (locked call) ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # ── PRICE — phosphor stencil digits, right-biased above the band ──
    _price_phosphor(big, price, rect.right - m(52), band.top - m(20), pal)

    # ── NAME — warm gilt across the band's clear right zone ──
    _name_gilt(big, name, band, cx + m(R))

    return big


# ── review strip ───────────────────────────────────────────────────────────────
VARIANTS = [
    ("RARE",      "skin_tophat"),
    ("EPIC",      "skin_prism"),
    ("LEGENDARY", "skin_kitsune"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS   # 324 x 200 (author scale)
MARGIN = 10
GAP = 8
HEADER_H = 26
FOOTER_H = 22

sheet_w = MARGIN * 2 + PANEL_W * 3 + GAP * 2
sheet_h = MARGIN * 2 + HEADER_H + PANEL_H + FOOTER_H
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(20, True)
ffont = _font(17, True)
htxt = hfont.render("store_card_v4_r3 — astral-lattice — round 1", True,
                    (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GAP)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4_r3/astral-lattice/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
