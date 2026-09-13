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
    plain_text, font, m, SS, soft_glow, _glyph_base, _stamp_bold, coin_glyph,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    PRICE_STOPS, PRICE_RIM_DARK, PRICE_RIM_BRIGHT, GOLD_A_NUM,
    lerp_color, WHITE, NEAR_BLACK,
)
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36


# Warm-bleed halo painted outer-ring first, inner-ring last, with a warm-white
# hot core immediately at the stroke fading to the (255,236,190) glow tint by
# 3px out. Normal-alpha (not additive): compositing displaces the navy's blue
# toward the warm hue, which is the only way the fixed palette can read warm
# (R-B) AND bright at once — additive over navy keeps blue too high to be warm.
_FILAMENT_RINGS = ((3, 90, (255, 236, 190)),
                   (2, 160, (255, 236, 190)),
                   (1, 210, (255, 255, 252)))


def _name_filament_core(big, name, cx, cy, max_w):
    sz = 13.5
    f = font(sz)
    while sum(f.size(c)[0] for c in name) > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)

    advances = [f.size(c)[0] for c in name]
    total_w = sum(advances)

    # Inverted layering vs r1: the warm halo is a dilated per-glyph SILHOUETTE
    # composited BEFORE the crisp glyph, so its bleed survives in the navy band
    # instead of hiding under an opaque fill. Hugging each stroke (not a centre
    # blob) keeps letter counters and inter-glyph gaps dark — no shared bar —
    # so every letter reads as its own heated filament element.
    x = cx - total_w // 2
    for char, adv in zip(name, advances):
        glyph_cx = x + adv // 2
        tile = _stamp_bold(_glyph_base(char, f, 0), m(0.8))
        tw, th = tile.get_size()
        bx, by = glyph_cx - tw // 2, cy - th // 2
        for rad, alpha, col in _FILAMENT_RINGS:
            tinted = tile.copy()
            tinted.fill((*col, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            steps = max(8, rad * 10)
            for s in range(steps):
                ang = 2 * math.pi * s / steps
                dx = int(round(rad * math.cos(ang)))
                dy = int(round(rad * math.sin(ang)))
                big.blit(tinted, (bx + dx, by + dy))
        x += adv

    # Crisp ivory glyph on top with a hairline keyline — thinner than r1 so the
    # warm light survives immediately outside each stroke rather than being
    # sealed off by a heavy near-black outline.
    plain_text(big, name, f, (cx, cy), (250, 244, 225), shadow_a=0,
               weight=m(0.8), keyline=(8, 8, 20), kw=m(0.5))


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
    """scroll-ribbon price: a double-swallowtail banner whose HERO is the
    embossed numeral, with a small coin wax-seal medallion pinned into the left
    notch. Distinct from coin-pill: the numeral dominates, the coin decorates."""
    txt = f"{price}"
    h = m(24)
    nd = m(7)                                   # inward notch depth (scroll cut)

    # Hero numeral — sized to dominate the banner and out-weigh the item name;
    # the coin is a decorative seal, so the digits are the read.
    f = font(12.5)
    nw = _glyph_base(txt, f, 0).get_width() + m(2)   # account for faux-bold grow
    left_pad = m(13)                            # clearance for the coin seal
    right_pad = m(9)
    W = left_pad + nw + right_pad
    x0 = cx - W // 2
    y0 = cy - h // 2

    poly = [(0, 0), (W, 0), (W - nd, h // 2), (W, h), (0, h), (nd, h // 2)]
    abspoly = [(x0 + px, y0 + py) for px, py in poly]

    # Rarity read is a soft warm halo beneath — no body-colour change, so the
    # banner stays ONE gold across every tier.
    soft_glow(big, cx, cy, int(W * 0.62), CARD_RING_BRIGHT, 40, layers=8)

    # cast shadow so the banner lifts off the navy body
    sh = pygame.Surface((W, h + m(3)), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), [(px, py + m(2)) for px, py in poly])
    big.blit(sh, (x0, y0))

    # ONE-gold fill: the PRICE ramp painted as a rect, then hard-clipped to the
    # swallowtail polygon via BLEND_RGBA_MIN so the gradient stays continuous.
    body = vgrad_stops(W, h, 0, PRICE_STOPS, 255, gamma=1.05)
    pmask = pygame.Surface((W, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(body, (x0, y0))

    # emboss edge: a bright bevel inset 1px from the silhouette sitting inside a
    # dark outer keyline (the defined edge against the navy ground).
    cxp = sum(p[0] for p in abspoly) / len(abspoly)
    cyp = sum(p[1] for p in abspoly) / len(abspoly)
    ins = m(1.6)
    inpoly = []
    for px, py in abspoly:
        vx, vy = cxp - px, cyp - py
        d = math.hypot(vx, vy) or 1
        inpoly.append((px + vx / d * ins, py + vy / d * ins))
    pygame.draw.polygon(big, (*PRICE_RIM_BRIGHT, 235), inpoly, width=max(1, m(1)))
    pygame.draw.polygon(big, PRICE_RIM_DARK, abspoly, width=max(1, m(1.4)))

    # numeral engraved INTO the gold: a dark fill with a bright catch on the
    # lower edge reads as a stamped/embossed digit rather than printed ink.
    num_cx = x0 + left_pad + nw // 2
    base = _stamp_bold(_glyph_base(txt, f, 0), m(0.9))
    rct = base.get_rect(center=(num_cx, cy))
    hi = base.copy()
    hi.fill((*PRICE_RIM_BRIGHT, 255), special_flags=pygame.BLEND_RGBA_MULT)
    hi.set_alpha(120)
    big.blit(hi, (rct.x, rct.y + m(1)))
    dk = base.copy()
    dk.fill((*GOLD_A_NUM, 255), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(dk, rct.topleft)

    # coin wax-seal seated in the left notch: a dark round well the exact in-game
    # coin sits inside, pinning the ribbon like a stamped seal.
    coin_cx, coin_cy = x0 + m(1), cy
    well = pygame.Surface((m(7) * 2 + 2, m(7) * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(well, (*PRICE_RIM_DARK, 180), (m(7) + 1, m(7) + 1), m(7))
    big.blit(well, (coin_cx - m(7) - 1, coin_cy - m(7) - 1))
    coin_glyph(big, coin_cx, coin_cy, m(6))


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
    _simple_price(big, rect.left + m(112), rect.y + m(50), price, pal)
    _name_filament_core(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
    return big


# ── review sheet: the EPIC card at full SS res + an in-game 1x scale view + a
# 2x banner-detail crop so the art-director can judge the hero read at scale.
CARD_PX_W, CARD_PX_H = CARD_W * SS, CARD_H * SS
big = render_card("skin_prism")
one_x = pygame.transform.smoothscale(big, (CARD_W, CARD_H))
zoom_src = big.subsurface(pygame.Rect(176, 78, 130, 68)).copy()
zoom = pygame.transform.smoothscale(zoom_src, (130 * 2, 68 * 2))

MARGIN, GUTTER, HEADER_H = 16, 20, 30
col_r_w = max(CARD_W, zoom.get_width())
sheet_w = MARGIN * 2 + CARD_PX_W + GUTTER + col_r_w
sheet_h = MARGIN * 2 + HEADER_H + max(CARD_PX_H, CARD_H + 20 + zoom.get_height() + 20)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))
hfont = _font(20, True)
lfont = _font(15, True)
htxt = hfont.render("store_card_v4_r4_price — scroll-ribbon — round 1  (EPIC / PRISM)", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

top = MARGIN + HEADER_H
sheet.blit(big, (MARGIN, top))
lt = lfont.render("EPIC  324x200 (SS=2)", True, (200, 196, 182))
sheet.blit(lt, (MARGIN, top + CARD_PX_H + 4))

rx = MARGIN + CARD_PX_W + GUTTER
sheet.blit(one_x, (rx, top))
lt2 = lfont.render("in-game 1x  162x100", True, (200, 196, 182))
sheet.blit(lt2, (rx, top + CARD_H + 4))
zy = top + CARD_H + 20
sheet.blit(zoom, (rx, zy))
lt3 = lfont.render("banner detail 2x", True, (200, 196, 182))
sheet.blit(lt3, (rx, zy + zoom.get_height() + 4))

out = "/home/user/skybit/docs/store_card_v4_r4_price/scroll-ribbon/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
