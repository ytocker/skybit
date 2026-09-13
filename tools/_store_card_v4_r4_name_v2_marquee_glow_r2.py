import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import math, sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game import store_catalog
from game.hud import _font
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, _glyph_base, _stamp_bold,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36


def _warm_halo(scratch, cx, cy, radius, color, peak, layers=8):
    # Source-over (not additive) feathered disc: overlapping lamps deepen the
    # alpha toward opaque but the RGB never leaves `color`, so a hot marquee
    # cluster stays warm ivory instead of clipping to dead white the way
    # stacked BLEND_ADD passes do — which is what kills R-B on the halo.
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak * (1 - (i - 1) / layers) ** 1.8)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        scratch.blit(g, (cx - r - 1, cy - r - 1))


def _name_marquee_glow(big, name, cx, cy, max_w, rect, plinth_top):
    # Backlit theatre marquee: lamp-white halo behind cream letters so the word
    # reads as lit from behind. Ivory is deliberately warm but rarity-neutral so
    # the "lit lamp" reads identically on every tier — the light is the fixture,
    # not a gem. Heated to 255,248,210 so R-B stays positive after the halo
    # blends over the dark navy band.
    IVORY = (255, 248, 210)
    CREAM = (250, 248, 240)
    sz = 13.0
    while sz > 9.0:
        f = font(sz)
        if _glyph_base(name, f, 0).get_width() <= max_w:
            break
        sz -= 0.5
    f = font(sz)
    gw = _glyph_base(name, f, 0).get_width()
    # Endpoints pulled to 0.7 of the half-width so the hot lamps stay inside the
    # word and the bloom never crosses the card edge.
    spread = int(gw // 2 * 0.7)
    xs = (cx - spread, cx - spread // 3, cx + spread // 3, cx + spread)
    # Build the whole halo on a scratch layer so it can be clipped to the band
    # before it touches the card — otherwise the above-cap bleed spills over the
    # plinth seam into the gem/thumb region.
    halo = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    # Centreline lamps: strong + wide so the halo actually reads against the
    # near-black band (r1 at alpha 80 / r=11 was invisible).
    for fx in xs:
        _warm_halo(halo, fx, cy, m(15), IVORY, 160, layers=8)
    # Bleed the bloom above and below cap-height so warm light escapes AROUND
    # the letters — a marquee reads by the halo in the clear band, not by a hot
    # spot the type body sits on and occludes.
    for fx in xs:
        _warm_halo(halo, fx, cy - m(5), m(9), IVORY, 80, layers=8)
        _warm_halo(halo, fx, cy + m(5), m(9), IVORY, 80, layers=8)
    # Clip the halo to the band interior: a straight cut at the plinth seam kills
    # any spill above it, and the horizontal bound keeps the ends off the card
    # edge. The band's rounded bottom sits well clear of the centred word.
    clip = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(clip, (255, 255, 255, 255),
                     (rect.left, plinth_top, rect.w, rect.bottom - plinth_top))
    halo.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(halo, (0, 0))
    # No shadow — the halo is the atmosphere; tight dark keyline keeps the cream
    # type crisp against its own glow.
    plain_text(big, name, f, (cx, cy), CREAM, shadow_a=0,
               weight=m(0.9), keyline=(10, 10, 22), kw=m(0.9))


def _neutral_band(big, rect, plinth_top, rad):
    ph = rect.bottom - plinth_top
    band = vgrad_stops(rect.w, ph, 0, [(0.0, (28, 24, 44)), (1.0, (14, 12, 26))], 255)
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, plinth_top - rect.bottom, rect.w, rect.h), border_radius=rad)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))
    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(seam, (*CARD_RING_BRIGHT, 80), (rect.left, plinth_top - max(1, m(1))), (rect.right - 1, plinth_top - max(1, m(1))), max(1, m(1)))
    big.blit(seam, (0, 0))
    pygame.draw.line(big, (6, 5, 12), (rect.left, plinth_top), (rect.right - 1, plinth_top), max(1, m(1)))


def _simple_price(big, cx, cy, price, pal):
    f = font(9.0)
    txt = f"{price}"
    nw = _glyph_base(txt, f, 0).get_width()
    ar = nw // 2 + m(6)
    rimbox = pygame.Rect(cx - ar, cy - ar, ar * 2, ar * 2)
    arc = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(arc, (*CARD_RING_BRIGHT, 140), rimbox, math.radians(60), math.radians(210), max(1, m(1)))
    big.blit(arc, (0, 0))
    plain_text(big, txt, f, (cx, cy), lerp_color(pal["gem"], WHITE, 0.25), shadow_a=0, weight=m(0.9))


def render_card(sid):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET), CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad = m(CARD_RAD)
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15), rect.topleft)
    top_sheen(big, rect, rad, m(30), peak=62)
    contact_shadow(big, rect, rad, m(9), alpha=120)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235), w=max(1, m(2.0)))
    cx = rect.left + m(40)
    cy = rect.y + m(38)
    plinth_top = rect.y + m(72)
    _neutral_band(big, rect, plinth_top, rad)
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3), pal["gem"], pal["deep"])
    _simple_price(big, rect.right - m(23), rect.y + m(48), price, pal)
    _name_marquee_glow(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26), rect, plinth_top)
    return big


VARIANTS = [("RARE", "skin_tophat"), ("EPIC", "skin_prism"), ("LEGENDARY", "skin_kitsune")]
PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN, GUTTER, HEADER_H, FOOTER_H = 10, 8, 26, 22
sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))
hfont = _font(20, True); ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r4_name_v2 — marquee-glow — round 2", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2, panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v2/marquee-glow/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
