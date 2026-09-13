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
    plain_text, coin_glyph, font, m, SS, soft_glow, _glyph_base, _stamp_bold,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP, PRICE_STOPS,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
)
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36


# Warm-bleed halo: composited BEFORE the crisp glyph so bleed survives the navy
# band; hugging each stroke (not a centre blob) keeps counters dark.
_FILAMENT_RINGS = ((3, 90, (255, 236, 190)),
                   (2, 160, (255, 236, 190)),
                   (1, 210, (255, 255, 252)))

# Tier aura peak escalates so a scarcer item reads hotter at a glance — the ONLY
# tier-reactive element of the price unit.
_BUBBLE_GLOW_PEAK = {"common": 16, "rare": 22, "epic": 30, "legendary": 40}


def _name_filament_core(big, name, cx, cy, max_w):
    sz = 13.5
    f = font(sz)
    while sum(f.size(c)[0] for c in name) > max_w and sz > 9.0:
        sz -= 0.5
        f = font(sz)

    advances = [f.size(c)[0] for c in name]
    total_w = sum(advances)

    # Inverted layering vs r1: warm halo is a dilated per-glyph silhouette blit
    # BEFORE the crisp glyph so bleed survives into the navy band.
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

    # Crisp ivory glyph on top; thin keyline so the warm light survives outside
    # each stroke instead of being sealed off by a heavy outline.
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


def _grad_numeral(big, txt, f, cx, cy, stops, keyline):
    """Gold-gradient price digits clipped to glyph alpha via BLEND_RGBA_MIN so
    the amber reads only inside the strokes; dark keyline ring keeps legibility
    on the indigo body."""
    base = _stamp_bold(_glyph_base(txt, f, 0), m(0.9))
    w, h = base.get_size()
    grad = vgrad_stops(w, h, 0, stops, 255)
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    r = base.get_rect(center=(cx, cy))
    if keyline:
        kl = base.copy()
        kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        p = m(0.7)
        for ang in range(0, 360, 45):
            dx = int(round(p * math.cos(math.radians(ang))))
            dy = int(round(p * math.sin(math.radians(ang))))
            big.blit(kl, (r.x + dx, r.y + dy))
    big.blit(grad, r.topleft)
    return r


def _rarity_of(pal):
    for k, v in RARITY.items():
        if v is pal:
            return k
    return "epic"


def _price_gem_bubble(big, rect, price, pal, gem_cx, gem_cy, gem_r):
    """Speech-bubble tooltip hung under the gem badge; the gem 'quotes its price'.
    A triangular tail off the bubble TOP points at the gem centre.

    r2 fixes:
    - Body is a lighter indigo vgrad so the bubble reads as a solid shape at 1x
      without depending on its rim; tinted slightly toward the tier gem for a
      subtle tier hint that doesn't shift legibility.
    - Tail+bubble are treated as ONE continuous gradient across their combined
      height, eliminating the colour seam at the junction.
    - Tail apex overlaps the gem's lower rim by 1 device px to close the dark gap.
    - bevel_rim uses CARD_RING_BRIGHT (gold) not a gem-tinted warm, and the same
      gold pair extends continuously along both tail edges — consistent top-left
      light direction across the entire price unit.
    - Coin cell and gold numerals are unchanged (strongest element from r1).
    """
    txt = f"{price:,}"
    h = m(23)
    rad = m(8)
    pad = m(8)
    gap = m(6)
    coin_d = int(h * 0.55)
    f = font(10.5)
    nw = _glyph_base(txt, f, 0).get_width()
    w = pad + coin_d + gap + nw + pad
    right = rect.right - m(6)
    x0 = right - w
    cy_b = rect.y + m(48)
    y0 = cy_b - h // 2
    body = pygame.Rect(x0, y0, w, h)

    # Tier aura under the whole unit; the escalating peak is the only tier-reactive
    # element so the body stays a constant indigo pair at every tier.
    peak = _BUBBLE_GLOW_PEAK.get(_rarity_of(pal), 30)
    soft_glow(big, x0 + w // 2, cy_b, m(20), pal["gem"], peak, layers=9)

    # Lighter indigo base, tinted ~12% toward the tier gem at the top and ~8% at
    # the bottom so the bubble body sits clearly above the card background
    # (~4% delta at r1) and carries a warm tier hint without fighting the price.
    body_top_col = lerp_color((48, 50, 98), pal["gem"], 0.12)
    body_bot_col = lerp_color((34, 36, 80), pal["gem"], 0.08)

    # Tail: apex overlaps the gem's lower rim by 1 device px to close the seam
    # that produced a dark gap at r1.
    tail_x = gem_cx
    tail_half = m(5)
    apex_y = gem_cy + gem_r - m(1)
    tail_base_y = y0 + m(1)

    # Treat the full tail+bubble stack as ONE gradient so the colour is
    # continuous at the junction; sample by absolute y position in the stack.
    total_top_y = float(apex_y)
    total_h_px = float(max(1, (y0 + h) - apex_y))

    def _sample(y_main):
        t = (y_main - total_top_y) / total_h_px
        return lerp_color(body_top_col, body_bot_col, max(0.0, min(1.0, t)))

    # Gradient-filled tail: scanline approach so each row's colour is the exact
    # value the body gradient would produce at that y — no separate surface blit
    # needed and no rounding mismatch at the junction.
    tail_h_px = max(1, tail_base_y - int(apex_y))
    for y in range(int(apex_y), tail_base_y + 1):
        frac = (y - int(apex_y)) / tail_h_px
        half_w = int(round(tail_half * frac))
        col = _sample(y)
        pygame.draw.line(big, col,
                         (int(tail_x) - half_w, y),
                         (int(tail_x) + half_w, y))

    # Bubble body — gradient starts where the tail left off so they read as one
    # contiguous shape; the bubble body vgrad is therefore NOT anchored to
    # body_top/body_bot directly but to the assembly-relative sample values.
    col_at_y0 = _sample(y0)
    col_at_ybot = _sample(y0 + h)
    body_surf = vgrad(w, h, rad, col_at_y0, col_at_ybot, 252, gamma=1.0)
    big.blit(body_surf, body.topleft)
    top_sheen(big, body, rad, m(9), peak=40)
    contact_shadow(big, body, rad, m(4), alpha=90)

    # Rim — unified top-left light direction. CARD_RING_BRIGHT (gold) as the
    # bright, not a gem-tinted warm, so the rim reads gold at every tier and the
    # direction is consistent with the card's own bevel frame.
    pygame.draw.rect(big, (6, 6, 18), body, width=max(1, m(1.4)), border_radius=rad)
    bevel_rim(big, body, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(1.4)))

    # Tail rim: extend the same gold bevel pair continuously along both tail edges
    # all the way to the apex. Left edge (faces top-left light) gets the bright
    # inner gold line; right edge (shadow side) gets only the dark outer keyline.
    rim_w = max(1, m(1.4))
    br_w = max(1, rim_w - 1)
    # Dark outer keyline on both edges (matches bevel_rim's CARD_RING_DEEP stroke)
    pygame.draw.line(big, CARD_RING_DEEP,
                     (int(tail_x - tail_half), tail_base_y),
                     (int(tail_x), int(apex_y)), rim_w)
    pygame.draw.line(big, CARD_RING_DEEP,
                     (int(tail_x + tail_half), tail_base_y),
                     (int(tail_x), int(apex_y)), rim_w)
    # Bright gold lit rim on the lit left tail edge, inset one step
    pygame.draw.line(big, (*CARD_RING_BRIGHT, 200),
                     (int(tail_x - tail_half) + br_w, tail_base_y - br_w),
                     (int(tail_x), int(apex_y) + br_w), br_w)

    # Coin cell and gold numerals — unchanged from r1 (the strongest element).
    coin_r = coin_d // 2
    coin_glyph(big, x0 + pad + coin_r, cy_b, coin_r)
    num_x = x0 + pad + coin_d + gap
    _grad_numeral(big, txt, f, num_x + nw // 2, cy_b, PRICE_STOPS, (30, 18, 6))


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
    gem_cx, gem_cy, gem_r = rect.right - m(19), rect.y + m(19), m(GEM_R + 3)
    facet_gem(big, gem_cx, gem_cy, gem_r, pal["gem"], pal["deep"])
    _price_gem_bubble(big, rect, price, pal, gem_cx, gem_cy, gem_r)
    _name_filament_core(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
    return big


card = render_card("skin_prism")
out = "/home/user/skybit/docs/store_card_v4_r4_price/gem-bubble/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(card, out)
print("saved", out, card.get_size())
