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


# Deliberately the inverse thermal read of molten-cast: light champagne crown
# falling to a near-black root, so the letters look lit from above and COOL in
# the body. The single warm accent is reserved for the sparks — heat that has
# already left the metal and is drifting up out of frame.
COOL_RAMP = [
    (0.0, (218, 208, 182)),   # champagne crown, catching the top light
    (0.40, (120, 114, 88)),   # warm-mid
    (0.75, (30, 28, 38)),     # near-dark
    (1.0, (6, 6, 14)),        # near-black root
]


def _name_rising_heat(big, name, cx, cy, max_w, top_limit):
    sz = 13.5
    f = font(sz)
    while sum(f.size(c)[0] for c in name) > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)

    master = _stamp_bold(_glyph_base(name, f, 0), m(0.7))
    bw, bh = master.get_size()
    gx = cx - bw // 2
    gy = cy - bh // 2

    body = vgrad_stops(bw, bh, 0, COOL_RAMP, 255)
    body.blit(master, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Pewter drop offset down-right gives the cool body footing against the band
    # before the crisp body lands back on top.
    shadow_mask = _stamp_bold(_glyph_base(name, f, 0), m(0.7))
    sh = pygame.Surface(shadow_mask.get_size(), pygame.SRCALPHA)
    sh.fill((80, 76, 60, 120))
    sh.blit(shadow_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(sh, (gx + max(1, m(1)), gy + max(1, m(1))))
    big.blit(body, (gx, gy))

    # Heat leaving the metal: a few bright specks lift off the crown line and
    # fade with height into the band's upper headroom. Only above the word, never
    # between letters, so the escaping-heat read stays clean.
    crown_y = gy
    spark_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    spark_xs = [cx - bw // 4, cx, cx + bw // 4]
    spark_alphas = [160, 200, 140]   # centre speck reads brightest

    for sx, sa in zip(spark_xs, spark_alphas):
        base_y = max(top_limit + m(2), crown_y - m(2))
        soft_glow(spark_surf, sx, base_y, m(2), CARD_RING_BRIGHT, sa, layers=2)
        for step in range(1, 4):
            wisp_y = base_y - step * m(2)
            wisp_a = max(0, sa - step * 50)
            if wisp_y < top_limit or wisp_a <= 10:
                break
            soft_glow(spark_surf, sx, wisp_y, m(1), (255, 255, 252), wisp_a, layers=1)

    big.blit(spark_surf, (0, 0), special_flags=pygame.BLEND_ADD)


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
    _name_rising_heat(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26), plinth_top)
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
htxt = hfont.render("store_card_v4_r4_name_v5 — rising-heat — round 1", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v5/rising-heat/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
