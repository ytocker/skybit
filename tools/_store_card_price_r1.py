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
    PRICE_STOPS, PRICE_RIM_BRIGHT, PRICE_RIM_DARK, GOLD_A_NUM, GOLD_A_COIN_RIM,
    lerp_color, WHITE, NEAR_BLACK,
)

CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36

# Rarity is carried ONLY by feathered under-glow peak + rim/keyline warmth so the
# price element's own body stays semantically constant (a price is a price at any
# tier). Gold-bodied concepts keep a gold rim that merely warms toward the tier
# hue on higher tiers; the indigo bubble keeps a constant body and lets the rim
# do all the tier work.
_TIER_PEAK = {"common": 16, "rare": 26, "epic": 36, "legendary": 48}
_TIER_WARM = {"common": 0.0, "rare": 0.18, "epic": 0.34, "legendary": 0.52}


def _tier(sid):
    return _rarity(sid) if _rarity(sid) in _TIER_PEAK else "legendary"


def _rim_warm(sid, base=CARD_RING_BRIGHT):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    return lerp_color(base, pal["gem"], _TIER_WARM[_tier(sid)])


def _gold_numeral(big, text, f, center, col_stops=PRICE_STOPS,
                  keyline=None, kw=None, shadow_a=110, weight=None):
    """Numeral filled by a single vertical gold ramp (clipped to the glyph mask),
    with an optional crisp keyline and a soft lift shadow."""
    base = _glyph_base(text, f, 0)
    if weight is None:
        weight = m(0.9)
    base = _stamp_bold(base, weight)
    bw, bh = base.get_size()
    fill = vgrad_stops(bw, bh, 0, col_stops, 255)
    fill.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    r = fill.get_rect(center=center)
    if shadow_a:
        sh = base.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow_a)
        big.blit(sh, (r.x, r.y + m(1.4)))
    if keyline:
        p = kw if kw is not None else m(1)
        kl = base.copy()
        kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 45):
            dx = int(round(p * math.cos(math.radians(ang))))
            dy = int(round(p * math.sin(math.radians(ang))))
            big.blit(kl, (r.x + dx, r.y + dy))
    big.blit(fill, r)
    return r


# ── concept 1: coin-pill (compact padding variant of the baseline price chip) ──
def price_coin_pill(big, rect, sid, text):
    h = m(21)
    coin_d = int(h * 0.66)
    pad = m(7)                     # compact vs baseline m(13)
    gapc = m(5)
    f = font(h * 0.50 / SS)
    nw = _glyph_base(text, f, 0).get_width() + m(2)
    w = pad + coin_d + gapc + nw + pad
    cx = rect.left + m(112)
    cy = rect.y + m(50)
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    soft_glow(big, r.centerx, r.centery, int(w * 0.62), RARITY.get(_rarity(sid), MYSTERY)["glow"],
              _TIER_PEAK[_tier(sid)], layers=8)
    drop_shadow(big, r, h // 2, blur=m(4), alpha=110, dy=m(2))
    big.blit(vgrad_stops(r.w, r.h, h // 2, PRICE_STOPS, 255, gamma=1.04), r.topleft)
    contact_shadow(big, r, h // 2, m(3), alpha=80)
    pygame.draw.rect(big, PRICE_RIM_DARK, r, width=max(1, m(1.4)), border_radius=h // 2)
    bevel_rim(big, r, h // 2, PRICE_RIM_DARK, (*_rim_warm(sid), 235), w=max(1, m(1.3)))
    x = r.x + pad
    coin_glyph(big, x + coin_d // 2, cy, coin_d // 2, rim=GOLD_A_COIN_RIM)
    x += coin_d + gapc
    plain_text(big, text, f, (x + nw // 2, cy), GOLD_A_NUM, shadow_a=0, weight=m(1.0))
    return r


# ── concept 2: gem-bubble (hero speech-bubble; indigo body, rim/glow=tier) ─────
def price_gem_bubble(big, rect, sid, text):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    h = m(23)
    rad = m(8)
    coin_d = int(h * 0.60)
    pad = m(8)
    gapc = m(5)
    f = font(h * 0.46 / SS)
    nw = _glyph_base(text, f, 0).get_width() + m(2)
    w = pad + coin_d + gapc + nw + pad
    cx = rect.right - m(6) - w // 2
    cy = rect.y + m(48)
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    # tail points down-left toward the disc; drawn as part of the body so the
    # rim can trace it as one silhouette.
    tail = [(r.left + m(9), r.bottom - m(2)),
            (r.left - m(6), r.bottom + m(8)),
            (r.left + m(20), r.bottom - m(2))]
    soft_glow(big, r.centerx, r.centery, int(w * 0.60), pal["glow"],
              _TIER_PEAK[_tier(sid)], layers=8)
    drop_shadow(big, r, rad, blur=m(4), alpha=120, dy=m(2))
    # indigo body (CONSTANT across tiers) + matching tail
    body = vgrad(r.w, r.h, rad, CARD_T, CARD_B, 255, gamma=1.1)
    big.blit(body, r.topleft)
    pygame.draw.polygon(big, CARD_B, tail)
    top_sheen(big, r, rad, m(9), peak=42)
    # rim carries the tier: a bright tier-hued bevel over a dark keyline, traced
    # around body AND tail so the tail reads as one clean pointer.
    rimcol = lerp_color(CARD_RING_BRIGHT, pal["gem"], 0.6)
    pygame.draw.rect(big, (4, 5, 16), r, width=max(1, m(1.6)), border_radius=rad)
    bevel_rim(big, r, rad, (10, 10, 24), (*rimcol, 235), w=max(1, m(1.4)))
    pygame.draw.polygon(big, (4, 5, 16), tail, width=max(1, m(1.6)))
    pygame.draw.line(big, rimcol, tail[0], tail[1], max(1, m(1.2)))
    x = r.x + pad
    coin_glyph(big, x + coin_d // 2, cy, coin_d // 2, rim=GOLD_A_COIN_RIM)
    x += coin_d + gapc
    _gold_numeral(big, text, f, (x + nw // 2, cy),
                  keyline=(6, 7, 18), kw=m(0.7), shadow_a=0, weight=m(1.0))
    return r


# ── concept 3: scroll-ribbon (reworked: struck numeral hero + wax-seal coin) ───
def price_scroll_ribbon(big, rect, sid, text):
    h = m(24)
    nd = m(7)                      # swallowtail notch depth
    seal_d = m(12)
    f = font(h * 0.48 / SS)
    nw = _glyph_base(text, f, 0).get_width()
    # body must host the seal pressed into the left notch + the centred numeral;
    # kept narrow enough that even the 6-glyph catalog max clears disc + card rim.
    w = nd + seal_d + m(6) + nw + m(6) + nd
    cx = rect.left + m(112)
    cy = rect.y + m(50)
    x0, y0 = cx - w // 2, cy - h // 2
    pts = [(x0, y0), (x0 + w, y0), (x0 + w - nd, y0 + h // 2),
           (x0 + w, y0 + h), (x0, y0 + h), (x0 + nd, y0 + h // 2)]
    soft_glow(big, cx, cy, int(w * 0.52), CARD_RING_BRIGHT, min(40, _TIER_PEAK[_tier(sid)]), layers=8)
    # gold vgrad clipped to the banner polygon
    bb = pygame.Rect(x0, y0, w, h)
    fill = vgrad_stops(w, h, 0, PRICE_STOPS, 255, gamma=1.04)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), [(px - x0, py - y0) for px, py in pts])
    fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = mask.copy(); sh.fill((0, 0, 0, 120), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(fill, bb.topleft)
    # dark outer keyline + inner bright bevel stroke
    pygame.draw.polygon(big, PRICE_RIM_DARK, pts, width=max(1, m(1.6)))
    inset = [(cx + (px - cx) * 0.9, cy + (py - cy) * 0.82) for px, py in pts]
    pygame.draw.polygon(big, (*_rim_warm(sid, PRICE_RIM_BRIGHT), 220), inset, width=max(1, m(1.0)))
    # numeral is the hero, centred in the banner body (offset right of the seal)
    num_cx = x0 + nd + seal_d + m(6) + nw // 2 + m(3)
    _gold_numeral(big, text, f, (num_cx, cy), keyline=(58, 34, 8), kw=m(0.5),
                  shadow_a=0, weight=m(1.1))
    # wax-seal medallion pressed into the left notch
    seal_cx = x0 + nd + seal_d // 2
    seat = pygame.Surface((seal_d + m(4), seal_d + m(4)), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 150), (seal_d // 2 + m(2), seal_d // 2 + m(2)), seal_d // 2 + m(1))
    big.blit(seat, (seal_cx - seal_d // 2 - m(2), cy - seal_d // 2 - m(2)))
    coin_glyph(big, seal_cx, cy, seal_d // 2, rim=GOLD_A_COIN_RIM)
    return bb


# ── concept 4: denom-stamp (reworked corner-tag: vertical coin-over-numeral) ───
def price_denom_stamp(big, rect, sid, text):
    w, h = m(22), m(28)
    rad = m(3)
    coin_d = m(14)
    cx = rect.left + m(87)
    cy = rect.y + m(50)
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    # auto-shrink numeral to the stamp's inner width (widest strings run small)
    sz = 7.0
    f = font(sz)
    while _glyph_base(text, f, 0).get_width() > w - m(4) and sz > 4.5:
        sz -= 0.25
        f = font(sz)
    nw = _glyph_base(text, f, 0).get_width()
    soft_glow(big, r.centerx, r.centery, int(h * 0.62), RARITY.get(_rarity(sid), MYSTERY)["glow"],
              _TIER_PEAK[_tier(sid)], layers=8)
    drop_shadow(big, r, rad, blur=m(4), alpha=130, dy=m(2))
    big.blit(vgrad(r.w, r.h, rad, (34, 36, 78), (14, 15, 40), 255, gamma=1.12), r.topleft)
    top_sheen(big, r, rad, m(8), peak=40)
    pygame.draw.rect(big, (4, 5, 16), r, width=max(1, m(1.4)), border_radius=rad)
    bevel_rim(big, r, rad, (10, 10, 24), (*_rim_warm(sid), 230), w=max(1, m(1.2)))
    coin_cy = r.y + m(3) + coin_d // 2
    coin_glyph(big, r.centerx, coin_cy, coin_d // 2, rim=GOLD_A_COIN_RIM)
    plain_text(big, text, f, (r.centerx, r.bottom - m(7)), (240, 240, 230),
               shadow_a=0, weight=m(0.8), keyline=(6, 7, 18), kw=m(0.4))
    return r


# ── concept 5: bare-numeral (reworked rarity-strip: container-less typography) ─
def price_bare_numeral(big, rect, sid, text):
    coin_d = m(14)
    gapc = m(5)
    f = font(11.0 / SS)
    nw = _glyph_base(text, f, 0).get_width()
    total = coin_d + gapc + nw
    cx = rect.right - m(24)
    cy = rect.y + m(50)
    left = cx - total // 2
    soft_glow(big, cx, cy, int(total * 0.52), RARITY.get(_rarity(sid), MYSTERY)["glow"],
              int(_TIER_PEAK[_tier(sid)] * 0.7), layers=8)
    coin_glyph(big, left + coin_d // 2, cy, coin_d // 2, rim=GOLD_A_COIN_RIM)
    # rarity lives in the keyline warmth (the only "rim" a container-less price
    # has) + the under-glow above; the gold fill itself stays constant.
    key = _rim_warm(sid, base=(150, 108, 40))
    _gold_numeral(big, text, f, (left + coin_d + gapc + nw // 2, cy),
                  keyline=(int(key[0]), int(key[1]), int(key[2])), kw=m(0.8),
                  shadow_a=120, weight=m(1.1))
    return pygame.Rect(left, cy - m(11), total, m(22))


CONCEPTS = [
    ("coin-pill", price_coin_pill),
    ("gem-bubble", price_gem_bubble),
    ("scroll-ribbon", price_scroll_ribbon),
    ("denom-stamp", price_denom_stamp),
    ("bare-numeral", price_bare_numeral),
]


def _name_band(big, rect, plinth_top, rad, name):
    ph = rect.bottom - plinth_top
    band = vgrad_stops(rect.w, ph, 0, [(0.0, (28, 24, 44)), (1.0, (14, 12, 26))], 255)
    mask = pygame.Surface((rect.w, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, plinth_top - rect.bottom, rect.w, rect.h), border_radius=rad)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(band, (rect.left, plinth_top))
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 80),
                     (rect.left, plinth_top - max(1, m(1))),
                     (rect.right - 1, plinth_top - max(1, m(1))), max(1, m(1)))
    pygame.draw.line(big, (6, 5, 12), (rect.left, plinth_top),
                     (rect.right - 1, plinth_top), max(1, m(1)))
    f = font(11.0)
    plain_text(big, name.upper(), f, (rect.centerx, plinth_top + ph // 2),
               (246, 240, 216), shadow_a=140, weight=m(0.8),
               keyline=(8, 8, 20), kw=m(0.5))


def render_card(sid, price_fn):
    pal = RARITY.get(_rarity(sid), MYSTERY)
    name = store_catalog.name(sid)
    price = f"{store_catalog.cost(sid):,}"
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(_INSET), m(_INSET), CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
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
    _name_band(big, rect, plinth_top, rad, name)
    soft_glow(big, cx, cy, m(R + 4), pal["glow"], 30, layers=8)
    cabochon(big, cx, cy, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx, cy, int(m(R) * 1.5))
    cabochon_glass(big, cx, cy, m(R), tint=pal["gem"])
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3), pal["gem"], pal["deep"])
    price_fn(big, rect, sid, price)
    return big


TIERS = [("COMMON", "skin_bat"), ("EPIC", "skin_mantis_shrimp"), ("LEGENDARY", "skin_chrome")]
PANEL_W, PANEL_H = CARD_W * SS, CARD_H * SS
MARGIN, GUTTER = 12, 8
COL_HEAD, ROW_HEAD, HEADER_H = 26, 74, 34
sheet_w = MARGIN * 2 + ROW_HEAD + PANEL_W * len(CONCEPTS) + GUTTER * (len(CONCEPTS) - 1)
sheet_h = MARGIN * 2 + HEADER_H + COL_HEAD + PANEL_H * len(TIERS) + GUTTER * (len(TIERS) - 1)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))
hfont = _font(22, True)
cfont = _font(17, True)
rfont = _font(16, True)
htxt = hfont.render("store card PRICE sprint — 5 locked concepts — round 1", True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))
grid_x = MARGIN + ROW_HEAD
grid_y = MARGIN + HEADER_H
for ci, (slug, fn) in enumerate(CONCEPTS):
    px = grid_x + ci * (PANEL_W + GUTTER)
    ct = cfont.render(slug, True, (250, 214, 130))
    sheet.blit(ct, (px + (PANEL_W - ct.get_width()) // 2, grid_y + (COL_HEAD - ct.get_height()) // 2))
for ri, (tier, sid) in enumerate(TIERS):
    py = grid_y + COL_HEAD + ri * (PANEL_H + GUTTER)
    rt = rfont.render(tier, True, (218, 214, 200))
    sheet.blit(rt, (MARGIN + (ROW_HEAD - rt.get_width()) // 2, py + PANEL_H // 2 - rt.get_height() // 2))
    for ci, (slug, fn) in enumerate(CONCEPTS):
        px = grid_x + ci * (PANEL_W + GUTTER)
        sheet.blit(render_card(sid, fn), (px, py))
out = "/home/user/skybit/docs/store_card_price/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
