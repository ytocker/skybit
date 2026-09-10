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


# Keyline spectrum: common uses a muted warm tone, legendary reaches near
# warm-white. Chosen to be LIGHTER than both the dark card body and the gold
# glyph top-stop so the ring genuinely lifts the glyph edge off the indigo.
_PRICE_KEYLINE_LO = (210, 188, 138)
_PRICE_KEYLINE_HI = (255, 252, 225)
_TIER_T = {"common": 0.0, "rare": 0.34, "epic": 0.67, "legendary": 1.0}


def _silhouette_shadow(big, sil, x, y, blur, alpha, dy):
    """Faint blurred lift of the WHOLE price group's silhouette, dropped below
    it — with no container the type would otherwise sit flat on the indigo body,
    so this soft dark plate gives the glyphs a little cast separation."""
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 1.7 / blur * 2.4)
        if a <= 0:
            continue
        layer = sil.copy()
        layer.fill((255, 255, 255, a), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 45):
            dx = int(round(i * math.cos(math.radians(ang))))
            ddy = int(round(i * math.sin(math.radians(ang))))
            big.blit(layer, (x + dx, y + dy + ddy))


def _price_bloom(surf, cx, cy, radius, peak_rgb=(20, 16, 8), rings=14):
    """Warm additive bloom sized to one glyph-height. All rings composite into
    ONE SRCALPHA surface; a single BLEND_ADD blit means the peak additive RGB
    contribution at the centre equals peak_rgb exactly — no per-ring stacking
    that would drive channels to white. The gradient falls to (0,0,0) at the
    rim so the dark card body reads through unobstructed."""
    d = radius * 2 + 4
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    g.fill((0, 0, 0, 0))
    pr, pg, pb = peak_rgb
    # Draw OUTER → INNER: each inner circle has alpha=255, so Porter-Duff
    # compositing means the last-drawn (innermost) ring wins at every pixel.
    # t rises from near-zero at the rim to 1.0 at the innermost ring.
    for i in range(rings, 0, -1):
        t = (rings + 1 - i) / rings
        r = int(radius * i / rings)
        col = (max(0, int(pr * t)), max(0, int(pg * t)), max(0, int(pb * t)), 255)
        if r <= 0:
            continue
        pygame.draw.circle(g, col, (radius + 2, radius + 2), r)
    surf.blit(g, (cx - radius - 2, cy - radius - 2), special_flags=pygame.BLEND_ADD)


def _price_bare_numeral(big, cx, cy, price, rarity, *, _sample_lum=False):
    """Container-free price: a coin icon + a gold gradient-filled numeral, the
    letterforms themselves acting as the tag. Separation from the dark body
    comes from a LIGHT warm per-glyph keyline, a faint single-blit underglow
    (no per-layer accumulation), and a cast silhouette shadow — no bounding box
    at all. The bloom and keyline are each luminance-bounded so the dark indigo
    card reads through both effects."""
    text = str(price)
    f = font(11.0)
    tracking = m(1)                          # inter-glyph air so digits stay legible
    mask = _glyph_base(text, f, tracking)
    nw, nh = mask.get_size()

    coin_d = m(14)
    coin_r = coin_d // 2
    gap = m(5)
    total_w = coin_d + gap + nw
    group_h = max(coin_d, nh)
    gx = cx - total_w // 2
    gy = cy - group_h // 2

    t_tier = _TIER_T.get(rarity, 0.5)
    # Light warm keyline: must be brighter than both the dark card body and the
    # glyph's own amber to create an outward lift. The tier ramp lets LEGENDARY
    # get a near-white edge while COMMON stays muted.
    keyline = lerp_color(_PRICE_KEYLINE_LO, _PRICE_KEYLINE_HI, t_tier)

    # Warm bloom centred on the numeral string (not the coin), radius = 1 glyph-
    # height. Single BLEND_ADD blit: peak (20,16,8) RGB additive at centre keeps
    # background luminance under the numeral well below 40.
    num_x = gx + coin_d + gap
    num_y = cy - nh // 2
    numeral_cx = num_x + nw // 2
    bloom_r = nh
    _price_bloom(big, numeral_cx, cy, bloom_r)

    if _sample_lum:
        # Verify background luminance under the centre of the numeral string
        # (after bloom, before glyphs are drawn) — must stay below 40.
        p = big.get_at((numeral_cx, cy))
        lum = 0.2126 * p.r + 0.7152 * p.g + 0.0722 * p.b
        print(f"bg under numeral  px={p[:3]}  luminance={lum:.2f}  (<40: {'PASS' if lum < 40 else 'FAIL'})")

    sil = pygame.Surface((total_w, group_h), pygame.SRCALPHA)
    pygame.draw.circle(sil, (255, 255, 255, 255), (coin_r, group_h // 2), coin_r)
    sil.blit(mask, (coin_d + gap, (group_h - nh) // 2))
    sil.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    _silhouette_shadow(big, sil, gx, gy, blur=m(3), alpha=60, dy=m(1))

    coin_glyph(big, gx + coin_r, cy, coin_r)

    # Light keyline: blit the glyph silhouette in bright warm cream at kw
    # outward on 8 compass points so the ring lifts cleanly from the indigo.
    # Gold gradient goes on top, so only the projecting halo is visible.
    kl = mask.copy()
    kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
    kw = m(2.0)
    for ang in range(0, 360, 45):
        dx = int(round(kw * math.cos(math.radians(ang))))
        dy = int(round(kw * math.sin(math.radians(ang))))
        big.blit(kl, (num_x + dx, num_y + dy))
    # PRICE_STOPS top-stop (236,176,72) is saturated amber — well within the
    # (255,230,150) cap, so glyph tops stay richly chromatic, not near-white.
    grad = vgrad_stops(nw, nh, 0, PRICE_STOPS, 255)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(grad, (num_x, num_y))


def render_card(sid, *, check_lum=False):
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
    _price_bare_numeral(big, rect.right - m(24), rect.y + m(50), price,
                        _rarity(sid), _sample_lum=check_lum)
    _name_filament_core(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
    return big


# EPIC-tier card at native 324×200 (SS=2) — the scale at which the bare-numeral
# concept must hold: gold digits separating from dark indigo with no container.
EPIC_SID = "skin_prism"
card = render_card(EPIC_SID, check_lum=True)
out = "/home/user/skybit/docs/store_card_v4_r4_price/bare-numeral/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(card, out)
print("saved", out, card.get_size(), "rarity", _rarity(EPIC_SID))
