import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import math, sys, random
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

IVORY     = (250, 244, 225)
CHAMPAGNE = (218, 208, 182)
CREAM     = (242, 236, 212)   # fleck ceiling capped so grain reads paper not static
PEWTER    = (170, 164, 148)
INK       = (20, 14, 8)       # warmed to sepia so it belongs to the parchment


def _name_vellum_plaque(big, txt, cx, cy, maxw, rect):
    prad = m(6)
    pw   = maxw
    ph   = m(15)
    # Float the plaque off the band floor: shift up 2 device px so navy shows
    # below → the plaque reads as an object laid ON the band, not clipped by it.
    prect = pygame.Rect(0, 0, pw, ph)
    prect.center = (cx, cy - max(1, m(1)))

    plq = vgrad_stops(pw, ph, prad, [(0.0, IVORY), (1.0, CHAMPAGNE)], 255)

    # Mottled fibre: capped fleck ceiling (~CREAM max) so grain stays "paper" not "static".
    rnd = random.Random(0x5EED)
    for _ in range(46):
        bx  = rnd.randint(0, pw - 1)
        by  = rnd.randint(0, ph - 1)
        br  = rnd.randint(m(2), m(6))
        col = CREAM if rnd.random() < 0.5 else (195, 185, 158)
        a   = rnd.randint(12, 20)
        blob = pygame.Surface((br * 2 + 2, br * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(blob, (*col, a), (br + 1, br + 1), br)
        plq.blit(blob, (bx - br, by - br))

    soft_glow(plq, pw // 2, ph // 2, m(11), (255, 250, 232), 24, layers=8)

    # Clip to rounded silhouette.
    mask = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, pw, ph), border_radius=prad)
    plq.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(plq, prect.topleft)

    # Full-perimeter deckle: top, bottom, left, right all torn so the plaque
    # never reads as a clean machined rectangle on any edge.
    deck = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    ernd = random.Random(0xDEC1)
    step = max(2, m(3))

    # top and bottom horizontal deckle (wider jitter range than r1)
    for ex in range(prect.left + prad, prect.right - prad, step):
        jt = ernd.randint(-m(2), m(1))
        pygame.draw.line(deck, (*IVORY, 150),
                         (ex, prect.top + jt), (ex + step - 1, prect.top + jt),
                         max(1, m(0.8)))
        jb = ernd.randint(0, m(2))
        pygame.draw.line(deck, (*PEWTER, 130),
                         (ex, prect.bottom - 1 + jb), (ex + step - 1, prect.bottom - 1 + jb),
                         max(1, m(0.8)))

    # left and right vertical deckle
    for ey in range(prect.top + prad, prect.bottom - prad, step):
        jl = ernd.randint(-m(2), m(1))
        pygame.draw.line(deck, (*IVORY, 120),
                         (prect.left + jl, ey), (prect.left + jl, ey + step - 1),
                         max(1, m(0.8)))
        jr = ernd.randint(0, m(2))
        pygame.draw.line(deck, (*PEWTER, 110),
                         (prect.right - 1 + jr, ey), (prect.right - 1 + jr, ey + step - 1),
                         max(1, m(0.8)))

    big.blit(deck, (0, 0))

    bevel_rim(big, prect, prad, PEWTER, (*IVORY, 235), w=max(1, m(1.0)))

    size = 10.5
    while size > 6:
        f = font(size)
        if _glyph_base(txt, f, 0).get_width() <= pw - m(14):
            break
        size -= 0.5
    f = font(size)

    # Debossed sepia ink: warm lower-right highlight, then sepia fill on top.
    off = max(1, m(0.7))
    plain_text(big, txt, f, (cx + off, cy - max(1, m(1)) + off), (140, 130, 105),
               shadow_a=0, weight=m(0.7))
    plain_text(big, txt, f, (cx, cy - max(1, m(1))), INK, shadow_a=0, weight=m(0.7))


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
    _name_vellum_plaque(big, name.upper(), rect.centerx, rect.y + m(81),
                        rect.w - m(26), rect)
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
htxt = hfont.render("store_card_v4_r4_name_v3 — vellum-plaque — round 2", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v3/vellum-plaque/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
