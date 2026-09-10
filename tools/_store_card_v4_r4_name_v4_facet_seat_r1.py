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


def _name_facet_seat(big, name, cx, cy, max_w):
    PAD_X = m(3)   # horizontal end padding per socket (shrinks first)
    GAP   = m(2)   # inter-socket gap (shrinks last)
    H     = m(13)  # socket height
    MITER = m(4)   # horizontal miter cut at each corner (angled end)

    sz = 13.5
    f = font(sz)
    while True:
        advances = [f.size(c)[0] for c in name]
        total_w = sum(adv + 2*PAD_X for adv in advances) + GAP * (len(name) - 1)
        if total_w <= max_w or (sz <= 9.0 and PAD_X <= m(1)):
            break
        if PAD_X > m(1):
            PAD_X = m(1)
        elif sz > 9.0:
            sz -= 0.5
            f = font(sz)
        else:
            break
    advances = [f.size(c)[0] for c in name]
    total_w = sum(adv + 2*PAD_X for adv in advances) + GAP * (len(name) - 1)

    CHAMP  = (232, 216, 182)
    PEWTER = (74, 70, 58)

    x = cx - total_w // 2
    for char, adv in zip(name, advances):
        sw = adv + 2 * PAD_X      # socket width
        sx = x
        sy = cy - H // 2

        # Hexagon polygon: flat top/bottom with mitred angled ends
        # Points going clockwise: top-left-miter, top-right-miter, right-miter,
        #   bottom-right-miter, bottom-left-miter, left-miter
        mx = min(MITER, sw // 3)   # clamp miter to 1/3 width
        pts = [
            (sx + mx,      sy),          # top-left miter
            (sx + sw - mx, sy),          # top-right miter
            (sx + sw,      sy + H // 2), # right middle
            (sx + sw - mx, sy + H),      # bottom-right miter
            (sx + mx,      sy + H),      # bottom-left miter
            (sx,           sy + H // 2), # left middle
        ]

        # Draw full polygon in champagne first, then cover bottom-right triangle in pewter
        pygame.draw.polygon(big, CHAMP, pts)

        # Bottom-right half: the diagonal seam runs from top-right to bottom-left corner
        # Clip bottom-right region: polygon = (top-right-miter, right-mid, bottom-right-miter,
        #   bottom-left-miter, bottom of seam diagonal)
        br_pts = [
            (sx + sw - mx, sy),          # top-right (same as hexagon)
            (sx + sw,      sy + H // 2),
            (sx + sw - mx, sy + H),
            (sx + mx,      sy + H),
            (sx,           sy + H // 2), # left middle (bottom of diagonal)
        ]
        pygame.draw.polygon(big, PEWTER, br_pts)

        # CARD_RING_BRIGHT hairline seam: diagonal from top-right to bottom-left
        pygame.draw.line(big, CARD_RING_BRIGHT,
                         (sx + sw - mx, sy),
                         (sx + mx, sy + H),
                         max(1, m(1)))

        # Dark outline seats the socket on the band
        pygame.draw.polygon(big, (14, 12, 26), pts, max(1, m(1)))

        # Near-black glyph centred in socket
        plain_text(big, char, f, (sx + sw // 2, cy), (18, 16, 30), shadow_a=0,
                   weight=m(0.5))

        x += sw + GAP


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
    _name_facet_seat(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
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
htxt = hfont.render("store_card_v4_r4_name_v4 — facet-seat — round 1", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v4/facet-seat/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
