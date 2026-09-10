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

# Prefer the shared multi-stop lerp so foil ramps read identically to the card
# system; fall back to a local copy only if the export ever moves.
try:
    from game.store_cards import lerp_stops as _lerp_stops
except ImportError:
    def _lerp_stops(stops, t):
        t = max(0.0, min(1.0, t))
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]; t1, c1 = stops[i + 1]
            if t <= t1:
                s = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
                return tuple(int(a + (b - a) * s) for a, b in zip(c0, c1))
        return tuple(stops[-1][1])

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36


def _neutral_band(big, rect, plinth_top, rad):
    # Calm indigo plinth keeps focus on the foil nameplate — no forge texture.
    ph = rect.bottom - plinth_top
    band = vgrad_stops(rect.w, ph, 0,
                       [(0.0, (28, 24, 44)), (1.0, (14, 12, 26))], 255)
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h),
                     border_radius=rad)
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
    # Struck numeral with a thin bright arc — reads as a minted denomination.
    f = font(9.0)
    txt = f"{price}"
    nw = _glyph_base(txt, f, 0).get_width()
    ar = nw // 2 + m(6)
    rimbox = pygame.Rect(cx - ar, cy - ar, ar * 2, ar * 2)
    arc = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(arc, (*CARD_RING_BRIGHT, 140), rimbox,
                    math.radians(60), math.radians(210), max(1, m(1)))
    big.blit(arc, (0, 0))
    plain_text(big, txt, f, (cx, cy),
               lerp_color(pal["gem"], WHITE, 0.25), shadow_a=0, weight=m(0.9))


def _name_foil_gradient(big, name, cx, cy, max_w, pal):
    # Letters read as cut from tier-reactive metallic foil: a diagonal gem ramp
    # gives the metal its body, and one baked sheen stripe fakes a fixed
    # highlight so the "foil" catches light without any runtime animation.
    sz = 13.5
    f = font(sz)
    tracking = m(0.3)
    while _glyph_base(name, f, tracking).get_width() > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)
    base = _stamp_bold(_glyph_base(name, f, tracking), m(0.7))
    bw, bh = base.get_size()
    total = bw + bh

    # 4-stop diagonal foil ramp: deep → gem → white sheen → gem → deep
    FOIL = [
        (0.00, pal["deep"]),
        (0.38, pal["gem"]),
        (0.60, lerp_color(pal["gem"], WHITE, 0.60)),
        (0.78, pal["gem"]),
        (1.00, pal["deep"]),
    ]
    grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for d in range(total):
        col = _lerp_stops(FOIL, d / total)
        pygame.draw.line(grad, col, (d, 0), (0, d), 2)
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Baked fixed specular sheen stripe at 60% along diagonal
    sheen = pygame.Surface((bw, bh), pygame.SRCALPHA)
    d0 = int(total * 0.60)
    sigma = bh * 0.50
    for d in range(total):
        a = int(170 * math.exp(-0.5 * ((d - d0) / sigma) ** 2))
        if a >= 2:
            pygame.draw.line(sheen, (255, 255, 255, min(200, a)), (d, 0), (0, d), 2)
    sheen.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    dst = base.get_rect(center=(cx, cy))

    # Dark keyline (8-direction compass at m(1))
    kl = base.copy()
    kl.fill((6, 6, 16, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for ang in range(0, 360, 45):
        dx = int(round(m(1) * math.cos(math.radians(ang))))
        dy = int(round(m(1) * math.sin(math.radians(ang))))
        big.blit(kl, base.get_rect(center=(cx + dx, cy + dy)))

    # Drop shadow
    sh = base.copy()
    sh.fill((4, 4, 12, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(160)
    big.blit(sh, base.get_rect(center=(cx, cy + m(1.5))))

    # Gradient fill then specular
    big.blit(grad, dst)
    big.blit(sheen, dst, special_flags=pygame.BLEND_ADD)


def render_card(sid):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = store_catalog.cost(sid)
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET),
                       CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
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
    _name_foil_gradient(big, name.upper(), rect.centerx, rect.y + m(81),
                        rect.w - m(22), pal)
    return big


VARIANTS = [("RARE", "skin_tophat"), ("EPIC", "skin_prism"), ("LEGENDARY", "skin_kitsune")]
PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN, GUTTER, HEADER_H, FOOTER_H = 10, 8, 26, 22
sheet_w = MARGIN * 2 + PANEL_W * 3 + GUTTER * 2
sheet_h = MARGIN + HEADER_H + PANEL_H + FOOTER_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))
hfont = _font(20, True); ffont = _font(18, True)
htxt = hfont.render("store_card_v4_r4_name — foil-gradient — round 1", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name/foil-gradient/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
