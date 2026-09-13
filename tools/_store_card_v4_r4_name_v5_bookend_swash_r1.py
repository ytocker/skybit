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


def _name_bookend_swash(big, name, cx, cy, max_w):
    sz = 13.5
    f = font(sz)
    while sum(f.size(c)[0] for c in name) > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)

    master = _stamp_bold(_glyph_base(name, f, 0), m(0.7))
    bw, bh = master.get_size()
    gx = cx - bw // 2
    gy = cy - bh // 2

    # Champagne->ivory gradient body: a clean, legible logotype metal, not a
    # noisy emboss. The ornament (the two swashes) carries the bespoke feel, so
    # the letterforms themselves stay quiet and readable.
    body = vgrad_stops(bw, bh, 0,
        [(0.0, (218, 208, 182)),   # champagne crown
         (1.0, (250, 244, 225))],  # ivory base
        255)
    body.blit(master, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Pewter down-right cast shadow reads the name off the navy plinth and gives
    # the glyphs enough weight to hold their own beside the bright flourishes.
    shadow = _stamp_bold(_glyph_base(name, f, 0), m(0.7))
    sh_surf = pygame.Surface(shadow.get_size(), pygame.SRCALPHA)
    sh_surf.fill((100, 96, 80, 160))
    sh_surf.blit(shadow, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(sh_surf, (gx + max(1, m(1)), gy + max(1, m(1))))
    big.blit(body, (gx, gy))

    # Swash length scales with the flanking dead space so a wide name that eats
    # the band doesn't push the arcs off-card or into the letterforms.
    flank = (max_w - bw) // 2
    reach = max(m(5), min(m(13), flank - m(1)))

    left_x = gx
    left_y = gy + int(bh * 0.75)
    right_x = gx + bw
    right_y = gy + int(bh * 0.75)

    steps = 20
    swash_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)

    # Cubic-bezier flourish sweeping out from a letter's outer terminal into the
    # band's empty flank, then flicking up — a calligraphic bookend. Only the
    # outer terminals get one, so no arc ever crosses an inter-glyph gap.
    def _swash(ox, oy, sign):
        p0 = (ox, oy)
        p1 = (ox + sign * int(reach * 0.46), oy + m(3))
        p2 = (ox + sign * int(reach * 0.77), oy + m(1))
        p3 = (ox + sign * reach, oy - m(4))
        pts = []
        for i in range(steps + 1):
            t = i / steps
            px = ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0]
                  + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0])
            py = ((1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1]
                  + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1])
            pts.append((int(px), int(py)))
        for i in range(len(pts) - 1):
            # Alpha tapers toward the free tip so the flourish dissolves into the
            # band instead of ending on a hard dot.
            alpha = int(200 * (1 - i / len(pts)))
            pygame.draw.line(swash_surf, (*CARD_RING_BRIGHT, alpha),
                             pts[i], pts[i + 1], max(1, m(1)))

    _swash(left_x, left_y, -1)
    _swash(right_x, right_y, +1)
    big.blit(swash_surf, (0, 0))


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
    _name_bookend_swash(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
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
htxt = hfont.render("store_card_v4_r4_name_v5 — bookend-swash — round 1", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v5/bookend-swash/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
