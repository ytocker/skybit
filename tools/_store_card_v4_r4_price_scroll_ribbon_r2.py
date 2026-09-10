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


# r2 numeral fill: deep espresso-brown-amber, simple-avg lum ≈ 57 (vs r1's
# near-black lum 28).  Achieves WCAG ≥ 4.5:1 against peak gold top-stop.
# Reads as warm mahogany stamp rather than black ink on gold.
_NUM_FILL = (108, 50, 8)

# r2 bevel colours: both ends capped at max channel 182 / avg lum ≈ 141.
# Top lit edge keeps warm gold warmth; bottom shadowed edge reads the fold.
# Symmetric draw of the inset polygon naturally matches left / right ends —
# kills the r1 right-notch hotspot that blew to near-beige (lum 190+).
_BEV_TOP = (182, 152, 90)
_BEV_BOT = (62, 42, 10)


def _simple_price(big, cx, cy, price, pal):
    """scroll-ribbon price: a double-swallowtail banner whose HERO is the
    embossed numeral, with a small coin wax-seal medallion pinned into the left
    notch.  Distinct from coin-pill: the numeral dominates, the coin decorates."""
    txt = f"{price}"
    h = m(24)

    # 40% notch depth gives each end two clearly separated prongs with a deep
    # triangular V-cut — unambiguously swallowtail, not the r1 hex silhouette.
    nd = int(h * 0.40)

    f = font(12.5)

    # Pull raw numeral width in 10% so a thin gold lane frames the glyph inside
    # the bevel on both sides — the digits breathe without crowding the banner edge.
    raw_nw = _glyph_base(txt, f, 0).get_width() + m(2)
    nw = int(raw_nw * 0.90)
    left_pad = m(13)
    right_pad = m(9)
    W = left_pad + nw + right_pad
    x0 = cx - W // 2
    y0 = cy - h // 2

    poly = [(0, 0), (W, 0), (W - nd, h // 2), (W, h), (0, h), (nd, h // 2)]
    abspoly = [(x0 + px, y0 + py) for px, py in poly]

    # Rarity halo sits beneath — banner body stays ONE gold across all tiers.
    soft_glow(big, cx, cy, int(W * 0.62), CARD_RING_BRIGHT, 40, layers=8)

    # Cast shadow so the banner lifts off the navy body.
    sh = pygame.Surface((W, h + m(3)), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), [(px, py + m(2)) for px, py in poly])
    big.blit(sh, (x0, y0))

    # One-gold fill clipped to the swallowtail silhouette.
    body = vgrad_stops(W, h, 0, PRICE_STOPS, 255, gamma=1.05)
    pmask = pygame.Surface((W, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(body, (x0, y0))

    # Directional bevel: draw the inset stroke on an isolated SRCALPHA surface,
    # then multiply by a per-row gradient so the top edge stays lit (_BEV_TOP)
    # and the bottom edge fades to shadow (_BEV_BOT).  Both ends receive
    # identical treatment — no hotspot asymmetry, no blown-out channel.
    cxp = sum(p[0] for p in abspoly) / len(abspoly)
    cyp = sum(p[1] for p in abspoly) / len(abspoly)
    ins = m(1.6)
    inpoly = []
    for px, py in abspoly:
        vx, vy = cxp - px, cyp - py
        d = math.hypot(vx, vy) or 1
        inpoly.append((px + vx / d * ins, py + vy / d * ins))

    pad = m(4)
    bw, bh = W + pad * 2, h + pad * 2
    bev = pygame.Surface((bw, bh), pygame.SRCALPHA)
    local_in = [(p[0] - x0 + pad, p[1] - y0 + pad) for p in inpoly]
    pygame.draw.polygon(bev, (*_BEV_TOP, 215), local_in, width=max(1, m(1)))

    # Per-row multiplier: row 0 → (255,255,255) keeps lit values; row bh-1 →
    # scale factors that map _BEV_TOP channels down to _BEV_BOT channels.
    scale_r = _BEV_BOT[0] / max(1, _BEV_TOP[0])
    scale_g = _BEV_BOT[1] / max(1, _BEV_TOP[1])
    scale_b = _BEV_BOT[2] / max(1, _BEV_TOP[2])
    fade = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for row in range(bh):
        t = row / max(1, bh - 1)
        mr = int(255 * (1.0 - t * (1.0 - scale_r)))
        mg = int(255 * (1.0 - t * (1.0 - scale_g)))
        mb = int(255 * (1.0 - t * (1.0 - scale_b)))
        pygame.draw.line(fade, (max(0, mr), max(0, mg), max(0, mb), 255),
                         (0, row), (bw - 1, row))
    bev.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(bev, (x0 - pad, y0 - pad))

    # Dark outer keyline — defines the swallowtail edge cleanly against navy.
    pygame.draw.polygon(big, PRICE_RIM_DARK, abspoly, width=max(1, m(1.4)))

    # r2 numeral: deep brown-amber core with a 1px procedural emboss.
    # Dark shadow shifted 1 device-px bottom-right anchors the glyph downward;
    # warm catch shifted 1 device-px top-left simulates a raised lit edge.
    # The two layers separate the glyph from the gold body by VALUE and SHAPE
    # rather than hue alone, giving a stamped-die / engraved feel.
    num_cx = x0 + left_pad + nw // 2
    base = _stamp_bold(_glyph_base(txt, f, 0), m(0.9))
    rct = base.get_rect(center=(num_cx, cy))

    off = max(1, int(round(m(0.5))))   # 1 device px at SS=2

    # Shadow layer — near-black shifted bottom-right (dark keyline of the emboss)
    sh_g = base.copy()
    sh_g.fill((8, 4, 1, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh_g.set_alpha(180)
    big.blit(sh_g, (rct.x + off, rct.y + off))

    # Catch layer — warm ivory shifted top-left (light catch of the emboss)
    hi_g = base.copy()
    hi_g.fill((255, 234, 172, 255), special_flags=pygame.BLEND_RGBA_MULT)
    hi_g.set_alpha(125)
    big.blit(hi_g, (rct.x - off, rct.y - off))

    # Core glyph — deep espresso-brown-amber
    core = base.copy()
    core.fill((*_NUM_FILL, 255), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(core, rct.topleft)

    # Coin wax-seal: near-black seat well + distinct dark rim ring + single
    # specular pip so it reads as a stamped medallion, not a gold-family smudge.
    # The seal stays smaller than the numeral cap height — it decorates, not leads.
    coin_cx, coin_cy = x0 + m(1), cy
    seal_r = m(6)

    sc = seal_r + m(3)
    seat = pygame.Surface((sc * 2, sc * 2), pygame.SRCALPHA)
    # near-black outer well — lifts the coin away from the gold body
    pygame.draw.circle(seat, (4, 2, 6, 210), (sc, sc), seal_r + m(2))
    # 2px dark rim ring, clearly not gold — reads as a material border
    pygame.draw.circle(seat, (38, 16, 4, 255), (sc, sc), seal_r + m(1),
                       max(2, m(1.5)))
    big.blit(seat, (coin_cx - sc, coin_cy - sc))

    coin_glyph(big, coin_cx, coin_cy, seal_r)

    # Single specular pip top-left: the one catch-light that makes the surface
    # read as polished metal or wax rather than a flat printed disc.
    pip_r = max(1, int(round(m(1.2))))
    pip_x = coin_cx - int(seal_r * 0.44)
    pip_y = coin_cy - int(seal_r * 0.44)
    pip = pygame.Surface((pip_r * 2 + 2, pip_r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 252, 238, 215), (pip_r + 1, pip_r + 1), pip_r)
    big.blit(pip, (pip_x - pip_r - 1, pip_y - pip_r - 1),
             special_flags=pygame.BLEND_ADD)


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


# ── review sheet: EPIC card at full SS res + 1x in-game scale + 2x banner crop
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
htxt = hfont.render("store_card_v4_r4_price — scroll-ribbon — round 2  (EPIC / PRISM)", True, (236, 232, 214))
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

out = "/home/user/skybit/docs/store_card_v4_r4_price/scroll-ribbon/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
