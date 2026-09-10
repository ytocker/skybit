"""tidal-shelf — store_card_v4_r3 concept, round 1 headless render.

A "buried-behind" card: the item disc sinks behind a tide shelf built at the
card foot from a stack of horizontal strata. The shelf's top edge is a shallow
periodic sine wave (a calm waterline, not a torn tear) with a thin warm rim
riding the crests. The strata are composited OVER a fully-drawn disc via a
rounded-rect mask, so they occlude only the disc's lower ~third — the item's
centroid stays well above the horizon.

The strata descend cool indigo (CARD_T -> CARD_B) EXCEPT the topmost NAME
stratum, which is lifted toward a warm tier tone so the cream item name clears
~7:1. The price is a bodiless tide-mark etch upper-right, above the waterline:
engraved numerals (dark pressed body + warm lower-right highlight, no chip / no
pill) beside a faint coin ring.

Headless (SDL dummy) -> a 3-up RARE / EPIC / LEGENDARY strip at SS (324x200 per
panel, no downscale) on a near-black ground with tier labels below. Not wired
into the live store; writes docs/store_card_v4_r3/tidal-shelf/round_1.png.
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

from game.draw import lerp_color
from game.hud import _font
from game import store_catalog
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, coin_glyph, _glyph_base, _stamp_bold,
    _cost,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
)

# LOCKED card shell constants (mirrors store_cards.render_card).
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36                         # hero disc radius; its lower ~third is buried
CREAM = (248, 246, 236)

# Waterline: a shallow calm wave with 2.5 gentle crests across the card and a
# low amplitude so it reads as a tide line rather than a torn silhouette.
WAVE_AMP = 3.5                 # logical px
WAVE_CRESTS = 2.5


def _name_on_shelf(surf, name, cx, cy, max_w):
    """Cream item name on the warm name stratum, with a tight dark keyline and
    drop shadow so it clears the lifted band; auto-shrunk to fit the lane."""
    sz = 13.5
    f = font(sz)
    while _glyph_base(name, f, 0).get_width() > max_w and sz > 9:
        sz -= 0.5
        f = font(sz)
    plain_text(surf, name, f, (cx, cy), CREAM, shadow_a=170,
               weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def _etch_number(surf, text, right_x, cy, size):
    """A bodiless tide-mark engrave (no chip / no pill): the numerals appear
    PRESSED into the card face. Card light is top-left, so an intaglio groove
    is shadowed on its upper-left wall and catches a warm glint on its
    lower-right wall — a dark up-left offset under a warm down-right offset,
    with a deep carved core between them."""
    f = font(size)
    base = _stamp_bold(_glyph_base(text, f, 0), m(0.6))
    w, h = base.get_size()
    x = right_x - w
    y = cy - h // 2
    e = max(1, m(0.8))

    def tint(col, alpha=255):
        img = base.copy()
        img.fill((*col, 255), special_flags=pygame.BLEND_RGBA_MULT)
        if alpha < 255:
            img.set_alpha(alpha)
        return img

    # faint warm halo sells the etch as catching stray light, not a sticker
    soft_glow(surf, x + w // 2, cy, int(m(size * 0.42)), (255, 214, 150), 9,
              layers=6)
    surf.blit(tint((2, 3, 10)), (x - e, y - e))               # up-left shadow
    surf.blit(tint((255, 226, 158)), (x + e, y + e))          # down-right glint
    surf.blit(tint((9, 10, 26)), (x, y))                      # carved core
    return pygame.Rect(x, y, w, h)


def _coin_ring(surf, cx, cy, r):
    """A small denomination coin rendered faint, capped by a bare gold rim ring
    so it reads as a low-opacity outline mark beside the etched numerals."""
    pad = m(2)
    tmp = pygame.Surface((r * 2 + pad * 2, r * 2 + pad * 2), pygame.SRCALPHA)
    coin_glyph(tmp, r + pad, r + pad, r)
    tmp.fill((255, 255, 255, 96), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(tmp, (cx - r - pad, cy - r - pad))
    pygame.draw.circle(surf, (*CARD_RING_BRIGHT, 130), (cx, cy), r, max(1, m(1)))


def _wave_y(x, x0, span, base):
    """Waterline height at column x: a shallow sine of WAVE_CRESTS periods."""
    return base + m(WAVE_AMP) * math.sin(
        2 * math.pi * WAVE_CRESTS * (x - x0) / span)


def _shelf(surf, rect, rad, base, pal):
    """Build the tide shelf on its own SRCALPHA layer and composite it OVER the
    already-drawn disc so the strata bury the disc's lower arc.

    The topmost strip is the warm NAME stratum (lifted toward the tier tone so
    the cream name clears ~7:1); below it, three cool strata deepen CARD_T ->
    CARD_B, parted by thin sediment keylines. The shelf's top edge is the wavy
    waterline, and a warm rim rides its crests. The whole layer is finally
    masked to the card's rounded rect so it honours the bottom corners."""
    x0 = rect.left
    span = rect.w
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)

    # Warm, tier-tinted-but-DARK name band: pulled off CARD_T toward the tier
    # deep + a touch of amber warmth. Stays dark enough for cream to clear ~7:1
    # while reading as a distinct lifted lane over the near-black strata.
    name_band = lerp_color(lerp_color(CARD_T, pal["deep"], 0.45),
                           (96, 74, 42), 0.16)
    s1 = base + m(23)                     # foot of the name stratum
    bottom = rect.bottom
    seg = (bottom - s1) / 3.0
    strata = [
        (base - m(WAVE_AMP) - m(2), s1, name_band),
        (s1, s1 + seg, (24, 26, 60)),
        (s1 + seg, s1 + 2 * seg, (18, 19, 48)),
        (s1 + 2 * seg, bottom, CARD_B),
    ]
    for top, bot, col in strata:
        pygame.draw.rect(layer, col,
                         (0, int(round(top)), surf.get_width(),
                          int(round(bot - top)) + 1))
    # thin sediment keylines between the cool strata
    for yb in (s1, s1 + seg, s1 + 2 * seg):
        pygame.draw.line(layer, (6, 7, 20), (0, int(round(yb))),
                         (surf.get_width(), int(round(yb))), max(1, m(0.7)))

    # carve the wavy top edge: keep only what sits BELOW the waterline
    pts = [(x, _wave_y(x, x0, span, base))
           for x in range(0, surf.get_width() + 1, m(1))]
    below = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    poly = pts + [(surf.get_width(), bottom + m(4)), (0, bottom + m(4))]
    pygame.draw.polygon(below, (255, 255, 255, 255), poly)
    layer.blit(below, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # warm rim rides the crest line so the waterline catches the light
    pygame.draw.lines(layer, (255, 228, 172, 200), False, pts, max(1, m(1.2)))

    # honour the card's rounded bottom corners
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=rad)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (0, 0))


def render_card(sid):
    """Draw ONE tidal-shelf card onto a fresh SS panel (324x200) and return it
    (authored directly at SS, no smoothscale)."""
    pal = RARITY.get(_rarity(sid), MYSTERY)
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)

    # ── card shell (locked order) ──
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))

    # ── hero disc (drawn FIRST so the shelf can bury it) ──
    cx = rect.left + m(40)
    cy = rect.centery - m(6)               # shifted up: the lower arc is buried
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])

    # ── tide shelf composited over the disc ──
    wl_base = cy + m(13)                    # mean waterline ~ disc lower third
    _shelf(big, rect, rad, wl_base, pal)

    # ── name on the warm name stratum ──
    _name_on_shelf(big, store_catalog.name(sid), rect.centerx, wl_base + m(11),
                   rect.w - m(26))

    # ── bodiless tide-mark price, upper-right above the waterline ──
    right_x = rect.right - m(12)
    py = rect.y + m(40)
    num = _etch_number(big, f"{_cost(sid):,}", right_x, py, 12.5)
    _coin_ring(big, num.left - m(9), py, m(6))

    # ── corner tier gem ──
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])
    return big


# ── review strip ───────────────────────────────────────────────────────────────
PANELS = [
    ("skin_tophat", "RARE"),
    ("skin_prism", "EPIC"),
    ("skin_kitsune", "LEGENDARY"),
]

PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS       # 324 × 200
MARGIN = 10
GAP = 8
HEADER_H = 26
LABEL_H = 22

sheet_w = MARGIN * 2 + PANEL_W * 3 + GAP * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + LABEL_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = _font(20, True)
lfont = _font(18, True)
htxt = hfont.render("store_card_v4_r3  —  tidal-shelf  —  round 1",
                    True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

panel_y = MARGIN + HEADER_H
for i, (sid, tier) in enumerate(PANELS):
    px = MARGIN + i * (PANEL_W + GAP)
    sheet.blit(render_card(sid), (px, panel_y))
    ltxt = lfont.render(tier, True, (214, 210, 196))
    sheet.blit(ltxt, (px + (PANEL_W - ltxt.get_width()) // 2,
                      panel_y + PANEL_H + (LABEL_H - ltxt.get_height()) // 2))

out = "/home/user/skybit/docs/store_card_v4_r3/tidal-shelf/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
