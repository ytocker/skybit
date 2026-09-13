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


# Warm-bleed halo painted outer-ring first, inner-ring last, with a warm-white
# hot core immediately at the stroke fading to the (255,236,190) glow tint by
# 3px out. Normal-alpha (not additive): compositing displaces the navy's blue
# toward the warm hue, which is the only way the fixed palette can read warm
# (R-B) AND bright at once — additive over navy keeps blue too high to be warm.
_FILAMENT_RINGS = ((3, 90, (255, 236, 190)),
                   (2, 160, (255, 236, 190)),
                   (1, 210, (255, 255, 252)))

# Rarity aura peak beneath the bubble escalates by tier so a scarcer item
# reads hotter at a glance — the ONLY tier-reactive element of the price unit
# (body + tail stay a constant indigo so price legibility never shifts).
_BUBBLE_GLOW_PEAK = {"common": 16, "rare": 22, "epic": 30, "legendary": 40}


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


def _grad_numeral(big, txt, f, cx, cy, stops, keyline):
    """Gold-gradient price digits: the PRICE_STOPS ramp CLIPPED to the glyph
    alpha via BLEND_RGBA_MIN (so the amber reads only inside the strokes), laid
    over a dark keyline ring so the numerals stay legible on the indigo body."""
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


def _price_gem_bubble(big, rect, price, pal, gem_cx, gem_cy, gem_r):
    """A compact speech-bubble tooltip hung under the gem badge: the gem is
    'quoting its price'. A short wide triangular tail off the bubble TOP points
    up at the gem centre so the two read as one unit. Body is a CONSTANT indigo
    vgrad at every tier (price legibility must not shift with rarity); only the
    soft aura beneath it is tier-coloured."""
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
    cy = rect.y + m(48)
    y0 = cy - h // 2
    body = pygame.Rect(x0, y0, w, h)

    # tier aura sits UNDER the whole unit so the escalating peak reads as a halo
    # around the price rather than tinting the legible body.
    peak = _BUBBLE_GLOW_PEAK.get(_rarity_of(pal), 30)
    soft_glow(big, x0 + w // 2, cy, m(20), pal["gem"], peak, layers=9)

    # warm rim colour lerped toward the tier gem — used for BOTH the body bevel
    # and the solid tail so the tail reads as the rim pinching up into a pointer.
    warm = lerp_color(CARD_RING_BRIGHT, pal["gem"], 0.6)

    # short + wide tail off the bubble top, apex at the gem's lower rim. Solid
    # fill (no bevel) so it survives the SS=2 downscale as a crisp point instead
    # of smearing; drawn AFTER the rim so it merges seamlessly into the body top.
    tail_x = gem_cx
    tail_half = m(5)
    apex_y = gem_cy + gem_r

    body_surf = vgrad(w, h, rad, CARD_T, CARD_B, 252, gamma=1.12)
    big.blit(body_surf, body.topleft)
    top_sheen(big, body, rad, m(9), peak=40)
    contact_shadow(big, body, rad, m(4), alpha=90)
    pygame.draw.rect(big, (6, 6, 18), body, width=max(1, m(1.4)), border_radius=rad)
    bevel_rim(big, body, rad, CARD_RING_DEEP, (*warm, 235), w=max(1, m(1.4)))

    pygame.draw.polygon(big, warm,
                        [(tail_x - tail_half, y0 + m(1)),
                         (tail_x + tail_half, y0 + m(1)),
                         (tail_x, apex_y)])

    # coin in its own left cell, then the gold-gradient numerals with a clear gap.
    coin_r = coin_d // 2
    coin_glyph(big, x0 + pad + coin_r, cy, coin_r)
    num_x = x0 + pad + coin_d + gap
    _grad_numeral(big, txt, f, num_x + nw // 2, cy, PRICE_STOPS, (30, 18, 6))


def _rarity_of(pal):
    for k, v in RARITY.items():
        if v is pal:
            return k
    return "epic"


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
out = "/home/user/skybit/docs/store_card_v4_r4_price/gem-bubble/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(card, out)
print("saved", out, card.get_size())
