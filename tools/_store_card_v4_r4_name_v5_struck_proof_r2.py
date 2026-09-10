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

# Die-struck coin-proof palette. The name is one metal — champagne — read
# through relief alone: a cast pewter shadow below-right, a single narrow warm
# crest where one raking light grazes the struck face, and a gold crown-catch
# on the milled top rim. Warm-white/ivory only ever appear as the crest cap so
# the body never reads as a white wash.
PEWTER    = (160, 155, 140)
CHAMPAGNE = (218, 208, 182)
IVORY     = (250, 244, 225)   # specular crest cap; nothing brighter in body


def _name_struck_proof(big, name, cx, cy, max_w):
    sz = 13.5
    f = font(sz)
    while sum(f.size(c)[0] for c in name) > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)

    advances = [f.size(c)[0] for c in name]
    total_w = sum(advances)

    body_mask = _stamp_bold(_glyph_base(name, f, 0), m(0.7))
    sw, sh = body_mask.get_size()
    gx = cx - sw // 2
    gy = cy - sh // 2

    # Cast shadow first: an offset pewter copy down-right of the strike. It only
    # ever peeks out past the champagne body along the lower-right contour, which
    # is exactly what sells the letters as raised off the navy plinth.
    shadow_fill = pygame.Surface((sw, sh), pygame.SRCALPHA)
    shadow_fill.fill(PEWTER)
    shadow_fill.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(shadow_fill, (gx + max(1, m(1)), gy + max(1, m(1))))

    # Champagne is the whole body — one flat metal tone. All relief comes from
    # the shadow beneath and the crest above, never from a second fill colour.
    body_fill = pygame.Surface((sw, sh), pygame.SRCALPHA)
    body_fill.fill(CHAMPAGNE)
    body_fill.blit(body_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(body_fill, (gx, gy))

    # One diagonal specular crest, phase-locked per glyph: every letter catches
    # the light at the SAME relative column (40% from its left edge) so the word
    # reads as struck by one die under one raking light. Built as a warm-white
    # stamp whose alpha is a tight gaussian (peak 75, sigma ch*0.18) and blitted
    # NORMALLY over the champagne — a lerp toward ivory, never an additive wash,
    # so no body pixel can exceed the ivory cap and the crest stays a narrow
    # band well under a quarter of each glyph's area.
    sweep_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    x = cx - total_w // 2
    for char, adv in zip(name, advances):
        char_mask = _stamp_bold(_glyph_base(char, f, 0), m(0.7))
        cw, ch = char_mask.get_size()
        char_gx = x + adv // 2 - cw // 2
        char_gy = cy - ch // 2

        crest_x = cw * 0.40
        sigma = max(1.0, ch * 0.18)
        sweep_tile = pygame.Surface((cw, ch), pygame.SRCALPHA)
        for py in range(ch):
            shear = (py - ch // 2) * 0.3
            row = pygame.Surface((cw, 1), pygame.SRCALPHA)
            for px in range(cw):
                d = (px - crest_x) + shear
                a = 75.0 * math.exp(-0.5 * (d / sigma) ** 2)
                ai = int(a)
                if ai > 2:
                    row.set_at((px, 0), (*IVORY, min(255, ai)))
            sweep_tile.blit(row, (0, py))

        sweep_tile.blit(char_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        sweep_surf.blit(sweep_tile, (char_gx, char_gy))
        x += adv

    big.blit(sweep_surf, (0, 0))

    # Gold crown-catch on the milled top rim: the upper contour isolated by
    # subtracting a down-shifted copy of the mask, filled with CARD_RING_BRIGHT
    # at alpha 240 so it separates cleanly from the champagne body as a warm
    # hairline. Drawn last, above the crest, so nothing dilutes it.
    full_mask = body_mask
    shifted_down = pygame.Surface((sw, sh), pygame.SRCALPHA)
    shifted_down.blit(full_mask, (0, max(1, m(1))))
    top_band = full_mask.copy()
    top_band.blit(shifted_down, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    ring_fill = pygame.Surface((sw, sh), pygame.SRCALPHA)
    ring_fill.fill((*CARD_RING_BRIGHT, 240))
    ring_fill.blit(top_band, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(ring_fill, (gx, gy))


def _neutral_band(big, rect, plinth_top, rad):
    ph = rect.bottom - plinth_top
    band = vgrad_stops(rect.w, ph, 0, [(0.0, (28, 24, 44)), (1.0, (14, 12, 26))], 255)
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h), border_radius=rad)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))
    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.line(seam, (*CARD_RING_BRIGHT, 80),
                     (rect.left, plinth_top - max(1, m(1))),
                     (rect.right - 1, plinth_top - max(1, m(1))), max(1, m(1)))
    big.blit(seam, (0, 0))
    pygame.draw.line(big, (6, 5, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))


def _simple_price(big, cx, cy, price, pal):
    f   = font(9.0)
    txt = f"{price}"
    nw  = _glyph_base(txt, f, 0).get_width()
    ar  = nw // 2 + m(6)
    rimbox = pygame.Rect(cx - ar, cy - ar, ar * 2, ar * 2)
    arc = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(arc, (*CARD_RING_BRIGHT, 140), rimbox,
                    math.radians(60), math.radians(210), max(1, m(1)))
    big.blit(arc, (0, 0))
    plain_text(big, txt, f, (cx, cy), lerp_color(pal["gem"], WHITE, 0.25),
               shadow_a=0, weight=m(0.9))


def render_card(sid):
    pal   = RARITY.get(_rarity(sid), MYSTERY)
    name  = store_catalog.name(sid)
    price = store_catalog.cost(sid)
    big   = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect  = pygame.Rect(m(_INSET), m(_INSET), CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
    rad   = m(CARD_RAD)
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
    _name_struck_proof(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
    return big


VARIANTS = [("RARE", "skin_tophat"), ("EPIC", "skin_prism"), ("LEGENDARY", "skin_kitsune")]
PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN, GUTTER, HEADER_H, FOOTER_H = 10, 8, 26, 22
sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))
hfont = _font(20, True)
ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r4_name_v5 — struck-proof — round 2", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v5/struck-proof/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
