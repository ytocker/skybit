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

# Keycap cross-section palette. The near-black seat is drawn first as a full
# fill so the 1px inset gradient leaves it as a keyline ring; lip + undercut
# then land INSIDE that ring so neither the gold top nor the pewter bottom get
# eaten by the outline (the r1 bug was the outline drawn last).
CAP_SEAT   = (8, 8, 20)        # near-black seat / glyph ink (palette near-black)
CAP_TOP    = (244, 236, 210)   # champagne face, dished-key highlight
CAP_BOT    = (198, 184, 150)   # champagne face, shadowed lower lip
CAP_PEWTER = (88, 82, 66)      # undercut shadow just above the seat


def _draw_cap(big, char, f, cap_left, cap_w, cap_cy, glyph_cy):
    """One mechanical keycap: near-black seat, inset champagne face, gold top
    lip, pewter undercut, debossed glyph. Everything works in device px because
    the panel is authored at device resolution (no downscale on the sheet)."""
    CAP_H = m(14)   # 28 device px cap inside the 32px navy band
    CRAD  = m(2)    # corner radius shared with r1
    cap_top    = cap_cy - CAP_H // 2
    cap_bottom = cap_top + CAP_H
    cxk = cap_left + cap_w // 2

    # 1) near-black seat under the whole cap (shows as a 1px ring after inset)
    pygame.draw.rect(big, CAP_SEAT, (cap_left, cap_top, cap_w, CAP_H),
                     border_radius=CRAD)
    # 2) champagne->ivory face, inset 1px on all sides so the seat rings it
    face = vgrad_stops(cap_w - 2, CAP_H - 2, max(1, CRAD - 1),
                       [(0.0, CAP_TOP), (1.0, CAP_BOT)], 255)
    big.blit(face, (cap_left + 1, cap_top + 1))
    # 3) CARD_RING_BRIGHT top lip, 2px inside the seat ring
    pygame.draw.rect(big, CARD_RING_BRIGHT,
                     (cap_left + 1, cap_top + 1, cap_w - 2, 2))
    # 4) pewter undercut, 2px above the bottom seat ring
    pygame.draw.rect(big, CAP_PEWTER,
                     (cap_left + 1, cap_bottom - 3, cap_w - 2, 2))
    # 5) debossed glyph last, full near-black weight so single verticals read
    plain_text(big, char, f, (cxk, glyph_cy), CAP_SEAT, shadow_a=0,
               weight=m(1), keyline=None, kw=0)


def _name_capsule_key(big, name, cx, glyph_cy, max_w, cap_cy):
    GAP = m(2)   # inter-capsule gap (shrinks last)

    # Uniform-width caps: every key is as wide as the widest glyph + padding, so
    # the row reads as a keyboard, not width-fit Scrabble tiles. Degrade by
    # trimming PAD, then font, then only fall back to variable width.
    PAD = m(2)
    sz  = 13.5
    f   = font(sz)

    def uniform(f_, pad):
        cw = max(max(f_.size(c)[0] for c in name) + 2 * pad, m(9))
        return cw, len(name) * cw + (len(name) - 1) * GAP

    cap_w, total = uniform(f, PAD)
    if total > max_w and PAD > m(1):
        PAD = m(1)
        cap_w, total = uniform(f, PAD)
    while total > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)
        cap_w, total = uniform(f, PAD)

    if total <= max_w:
        x = cx - total // 2
        for char in name:
            _draw_cap(big, char, f, x, cap_w, cap_cy, glyph_cy)
            x += cap_w + GAP
        return

    # Fallback: variable-width caps sized to each glyph advance (only when even
    # the smallest uniform row overflows the band).
    advances = [f.size(c)[0] for c in name]
    total = sum(a + 2 * PAD for a in advances) + GAP * (len(name) - 1)
    x = cx - total // 2
    for char, adv in zip(name, advances):
        cw = adv + 2 * PAD
        _draw_cap(big, char, f, x, cw, cap_cy, glyph_cy)
        x += cw + GAP


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
    band_cy = (plinth_top + rect.bottom) // 2   # centre caps in the navy band
    _name_capsule_key(big, name.upper(), rect.centerx, rect.y + m(81),
                      rect.w - m(26), band_cy)
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
htxt = hfont.render("store_card_v4_r4_name_v4 — capsule-key — round 2", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v4/capsule-key/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
