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

    # Lit champagne face reads near-ivory so it stays a light seat for the
    # near-black glyph; pewter is the smaller shadow facet, kept bright enough
    # to separate from the navy band rather than melting into it.
    CHAMP  = (234, 222, 202)
    PEWT   = (108, 102, 84)

    seam = pygame.Surface(big.get_size(), pygame.SRCALPHA)

    x = cx - total_w // 2
    for char, adv in zip(name, advances):
        sw = adv + 2 * PAD_X      # socket width
        sx = x
        sy = cy - H // 2

        mx = min(MITER, sw // 3)   # clamp miter to 1/3 width

        # Full hexagon silhouette: flat top/bottom, mitred angled ends.
        A = (sx + mx,      sy)          # top-left miter
        B = (sx + sw - mx, sy)          # top-right miter
        C = (sx + sw,      sy + H // 2) # right middle
        D = (sx + sw - mx, sy + H)      # bottom-right miter
        E = (sx + mx,      sy + H)      # bottom-left miter
        Fp = (sx,          sy + H // 2) # left middle
        pts = [A, B, C, D, E, Fp]

        # Hard diagonal facet split. The seam drops from the top-right miter to
        # a bottom point biased right so the lit champagne face owns ~2/3 of the
        # socket (and the glyph centre), leaving pewter as the narrow shadow.
        gx = sx + (sw + 2 * mx) // 3
        G = (gx, sy + H)

        champ_pts = [A, B, G, E, Fp]        # lit zone: top-left + centre + left
        pewt_pts  = [B, C, D, G]            # shadow zone: bottom-right edge
        pygame.draw.polygon(big, CHAMP, champ_pts)
        pygame.draw.polygon(big, PEWT, pewt_pts)

        # Two-tone crease along the facet boundary: a bright accent nudged onto
        # the pewter side (where it pops) and a near-black crease nudged onto the
        # champagne side (where a bright line would vanish).
        pygame.draw.line(seam, (*CARD_RING_BRIGHT, 200),
                         (B[0] + 1, B[1]), (G[0] + 1, G[1]), max(1, m(1)))
        pygame.draw.line(seam, (8, 8, 20, 180),
                         (B[0] - 1, B[1]), (G[0] - 1, G[1]), max(1, m(1)))

        # Strong dark seat: full outline plus thicker bottom/right edges and a
        # 1px contact shadow so each socket sits proud of the navy band.
        pygame.draw.polygon(big, (4, 4, 12), pts, max(1, m(1)))
        pygame.draw.line(big, (4, 4, 12), C, D, max(1, m(1.5)))
        pygame.draw.line(big, (4, 4, 12), D, E, max(1, m(1.5)))
        pygame.draw.line(big, (6, 5, 12),
                         (sx + mx, sy + H + max(1, m(1))),
                         (sx + sw - mx, sy + H + max(1, m(1))), max(1, m(1)))

        # Near-black glyph centred on the light champagne face.
        plain_text(big, char, f, (sx + sw // 2, cy), (18, 16, 30), shadow_a=0,
                   weight=m(0.5))

        x += sw + GAP

    big.blit(seam, (0, 0))


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
htxt = hfont.render("store_card_v4_r4_name_v4 — facet-seat — round 2", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v4/facet-seat/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
