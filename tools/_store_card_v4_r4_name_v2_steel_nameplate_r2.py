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


def _name_steel_nameplate(big, name, cx, cy, max_w):
    # Brushed pewter/champagne hardware: a raised machined plate that sits BESIDE
    # the gold frame instead of competing with it. Fixed non-tier silver tones so
    # the treatment reads identically across rarities — the gem is the tier cue.
    sz = 13.0
    f = font(sz)

    def _mask(fnt):
        return _stamp_bold(_glyph_base(name.upper(), fnt, 0), m(0.9))

    mask = _mask(f)
    while mask.get_width() > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)
        mask = _mask(f)
    mw, mh = mask.get_size()

    # Champagne-pewter vertical ramp — cool silver crown, warm pewter mid, and a
    # warm bronze-pewter foot. The foot is kept warm (raised chroma) rather than a
    # desaturated olive so the plate reads as living metal, yet stays deliberately
    # OFF amber/gold so it never becomes a second gold surface next to the frame.
    plate = vgrad_stops(mw, mh, 0,
                        [(0.0, (216, 208, 192)),
                         (0.45, (182, 172, 150)),
                         (1.0, (134, 122, 96))], 255, gamma=1.05)
    plate.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    dst = mask.get_rect(center=(cx, cy))

    # Tight dark keyline seats the plate on the neutral band and gives the emboss
    # a crisp shoulder to catch light against.
    key = mask.copy()
    key.fill((18, 16, 12, 255), special_flags=pygame.BLEND_RGBA_MULT)
    kw = m(0.8)
    for ang in range(0, 360, 45):
        dx = int(round(kw * math.cos(math.radians(ang))))
        dy = int(round(kw * math.sin(math.radians(ang))))
        big.blit(key, (dst.x + dx, dst.y + dy))

    # Raised emboss — cooled specular key TOP-LEFT, warm undercut BOTTOM-RIGHT, to
    # match the card's bevel_rim light source. The highlight is pulled off chalky
    # white so the value gap between it and the metal body widens: the emboss then
    # reads as depth (caught light) rather than a bright painted outline. Highlight
    # laid first, shadow next, ramp-filled face last so the metal owns the centre.
    hi = mask.copy()
    hi.fill((238, 232, 218, 255), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(hi, mask.get_rect(center=(cx - m(1), cy - m(1))))

    sh = mask.copy()
    sh.fill((40, 36, 28, 255), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sh, mask.get_rect(center=(cx + m(1), cy + m(1))))

    big.blit(plate, dst)


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
    _name_steel_nameplate(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
    return big


VARIANTS = [("RARE", "skin_tophat"), ("EPIC", "skin_prism"), ("LEGENDARY", "skin_kitsune")]
PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN, GUTTER, HEADER_H, FOOTER_H = 10, 8, 26, 22
sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))
hfont = _font(20, True); ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r4_name_v2 — steel-nameplate — round 2", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2, panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v2/steel-nameplate/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
