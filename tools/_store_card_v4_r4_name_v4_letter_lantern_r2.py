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


def _warm_puck(surf, cx, cy, rx, ry, color, peak_a, layers):
    # Premultiplied additive glow.  BLEND_ADD ignores source alpha, so the shared
    # soft_glow's flat-colour circles saturate every channel to 255 on overlap —
    # the r1 white-clip.  Scaling each layer's RGB by its own alpha keeps peak_a
    # governing brightness AND preserves the warm 255:236:190 ratio through
    # accumulation, so cores read ivory and never blow to pure white.  The pool
    # is an ellipse: this glyph's ink fills its whole advance box, so a circular
    # halo wide enough to sit past the letter would flood the butting neighbour
    # and erase the dark gaps.  A tall/narrow lozenge spills vertically past the
    # cap (the visible pool) while staying inside the advance so gaps stay dark.
    for i in range(layers, 0, -1):
        ax = int(rx * i / layers)
        ay = int(ry * i / layers)
        a = int(peak_a * (1 - (i - 1) / layers) ** 1.8)
        if ax <= 0 or ay <= 0 or a <= 0:
            continue
        fr = a / 255.0
        col = (int(color[0] * fr), int(color[1] * fr), int(color[2] * fr))
        g = pygame.Surface((ax * 2 + 2, ay * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(g, (*col, 255), (1, 1, ax * 2, ay * 2))
        surf.blit(g, (cx - ax - 1, cy - ay - 1), special_flags=pygame.BLEND_ADD)


def _name_letter_lantern(big, name, cx, cy, max_w):
    # Auto-fit font size
    sz = 13.5
    f = font(sz)
    while sum(f.size(c)[0] for c in name) > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)

    # Total advance width for centering
    advances = [f.size(c)[0] for c in name]
    total_w = sum(advances)
    n_chars = len(name)

    # peak_alpha base ~90; longer names (>=8) pack more pucks so each is dimmed
    # toward ~70 to keep neighbour overlap from washing gaps or clipping cores.
    peak_a = 90 if n_chars < 8 else int(round(max(70, 90 - (n_chars - 7) * (90 - 70) / 3)))

    # Glow pass, per glyph: a tall core puck plus two soft under-lobes offset
    # above/below.  The lobes push warm light out past the cap top/bottom so each
    # letter visibly sits in its own pool WITHOUT over-brightening (and clipping)
    # the centre the way one big centred disc would.  Additive accumulation reads
    # as individual lanterns; the dark inter-glyph gaps stay dark because every
    # pool is a narrow vertical lozenge sized to its own advance, not the band.
    glow_surf = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    puck_y = cy - m(1)                              # centre on the cap body, not descender space
    x = cx - total_w // 2
    for char, adv in zip(name, advances):
        glyph_cx = x + adv // 2
        # rx stays inside the advance so gaps stay dark; ry adds m(7) of height so
        # the pool clears the glyph vertically (the "extend past the glyph" note).
        rx = max(m(2.5), min(m(6), int(adv * 0.32)))
        ry = rx + m(7)
        pa = peak_a
        # Narrow glyphs (e.g. "I") sit close to neighbours; dim their core so the
        # two pools don't fuse into one bar.
        if adv < m(4):
            pa = max(peak_a - 20, 48)
        lobe_rx = int(rx * 0.85)
        _warm_puck(glow_surf, glyph_cx, puck_y - m(4), lobe_rx, m(8), (255, 236, 190), 44, layers=2)
        _warm_puck(glow_surf, glyph_cx, puck_y + m(4), lobe_rx, m(8), (255, 236, 190), 44, layers=2)
        _warm_puck(glow_surf, glyph_cx, puck_y, rx, ry, (255, 236, 190), pa, layers=4)
        x += adv
    big.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)

    # Glyph pass: full ivory with a THIN lifted keyline — a 2px near-black moat
    # ate the warm fringe at the edges, so 1px at (20,16,30) lets the pool glow
    # read right up to the letter while the filament stays crisp on the ground.
    plain_text(big, name, f, (cx, cy), (246, 240, 216), shadow_a=0,
               weight=m(0.5), keyline=(20, 16, 30), kw=m(0.5))


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
    _name_letter_lantern(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
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
htxt = hfont.render("store_card_v4_r4_name_v4 — letter-lantern — round 2", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
panel_y = MARGIN + HEADER_H
for i, (tier, sid) in enumerate(VARIANTS):
    px = MARGIN + i * (PANEL_W + GUTTER)
    sheet.blit(render_card(sid), (px, panel_y))
    ftxt = ffont.render(tier, True, (218, 214, 200))
    sheet.blit(ftxt, (px + (PANEL_W - ftxt.get_width()) // 2,
                      panel_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))
out = "/home/user/skybit/docs/store_card_v4_r4_name_v4/letter-lantern/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
