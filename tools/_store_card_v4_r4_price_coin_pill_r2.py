import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import math, sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game import store_catalog
from game.store_cards import (
    cabochon, cabochon_glass, blit_thumb, facet_gem,
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, font, m, SS, soft_glow, _glyph_base, _stamp_bold,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
    PRICE_STOPS, PRICE_RIM_DARK, PRICE_RIM_BRIGHT,
)
CARD_W, CARD_H = 162, 100
CARD_RAD = 17
_INSET = 6
R = 36


# Warm-bleed halo: outer ring first, hot-core last. Normal-alpha so the warm
# hue displaces the navy's blue channel rather than adding on top of it.
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

    # Warm halo is a dilated per-glyph silhouette composited BEFORE the crisp
    # glyph so the bleed survives in the navy band instead of hiding under an
    # opaque fill. Hugging each stroke keeps letter counters dark so every
    # letter reads as its own heated filament element.
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

    # Crisp ivory glyph on top with a hairline keyline so the warm light
    # survives immediately outside each stroke rather than being sealed off.
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


# Glow intensity per tier: drives the pill's warm amber under-glow.
_GLOW_PEAK = {"common": 14, "rare": 20, "epic": 28, "legendary": 40}

# Warm amber pill under-glow: rarity colour lives in the gem badge + cabochon
# aura only; the pill under-glow stays amber so it always reads as currency.
_PILL_GLOW = (200, 140, 50)

# Numeral: deep warm-brown so it reads as "struck amber" not navy/black.
# The gold catch-light ring gives 1px contrast against the amber body.
_NUM_COL = (88, 44, 10)
_NUM_CATCH = (204, 144, 32)


def _pill_gloss(surf, rect, radius):
    """Narrow warm crown band — BLEND_ADD with LOW-value warm RGB (not white=255)
    so the crown lifts to cream-gold rather than blowing to chrome.
    Root cause of r1 blowout: gloss_sweep draws (255,255,255,a) + BLEND_ADD adds
    the raw 255 per channel regardless of the alpha value, clipping every pixel
    to white. Fix: draw (28, 18, 6, 255) so BLEND_ADD adds only +28/+18/+6,
    keeping the top gold at (236+28, 176+18, 72+6) = (255, 194, 78) — amber."""
    band_h = max(1, int(rect.h * 0.28))
    gloss = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(band_h):
        a = int(255 * (1 - y / band_h) ** 1.5)
        pygame.draw.line(gloss, (28, 18, 6, a), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    gloss.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(gloss, rect.topleft, special_flags=pygame.BLEND_ADD)


def _simple_coin(surf, cx, cy, r):
    """Clean 2-value gold disc: dark-amber rim + lighter amber face body.
    Fully opaque — no transparent pixels that let rarity glow bleed through.
    Tiny seat shadow and a bright top-left rim arc for a 3-D read at 1×."""
    # Tiny seat shadow beneath the disc
    seat = pygame.Surface((r * 2 + m(4), r * 2 + m(4)), pygame.SRCALPHA)
    sc = r + m(2)
    pygame.draw.circle(seat, (0, 0, 0, 65), (sc + m(1), sc + m(1)), r)
    surf.blit(seat, (cx - sc, cy - sc))
    # Face: mid-amber body fills the disc solidly
    pygame.draw.circle(surf, (208, 154, 50), (cx, cy), r)
    # Crown highlight: lighter offset disc biased top-left (value 2)
    fi = max(1, int(r * 0.56))
    pygame.draw.circle(surf, (236, 186, 76), (cx - r // 4, cy - r // 4), fi)
    # Dark outer rim to define the disc edge
    pygame.draw.circle(surf, (90, 50, 10), (cx, cy), r, max(1, m(0.7)))
    # Bright top-left arc specular on the rim itself
    pygame.draw.arc(surf, (248, 218, 108),
                    (cx - r, cy - r, r * 2, r * 2),
                    math.radians(90), math.radians(180), max(1, m(0.9)))


def _price_coin_pill(big, cx, cy, price, pal, tier):
    """Compact horizontal price pill: clean 2-value coin glyph left cell,
    deep warm-amber numeral with gold catch-light right cell, on the ONE gold
    ramp.  Pill under-glow is warm amber — rarity colour lives in the gem
    badge + cabochon aura, not here, so the pill always reads as currency."""
    text = f"{price:,}"
    h = m(21)
    coin_d = int(h * 0.60)
    pad = m(5)                   # tighter than r1's m(7): more air on right edge
    gapc = m(5)
    f = font(h * 0.50 / SS)
    nw = _glyph_base(text, f, 0).get_width() + m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    # Warm amber under-glow (not the tier's rarity purple)
    soft_glow(big, cx, cy, w // 2 + m(4), _PILL_GLOW,
              _GLOW_PEAK.get(tier, 14), layers=8)

    # Body: gradient fill + constrained warm gloss + AO shadow + double rim.
    # PRICE_RIM_BRIGHT used directly — no lerp toward rarity gem so the bevel
    # stays warm gold without purple contamination.
    drop_shadow(big, r, h // 2, blur=m(4), alpha=110, dy=m(2))
    big.blit(vgrad_stops(r.w, r.h, h // 2, PRICE_STOPS, 255, gamma=1.04),
             r.topleft)
    _pill_gloss(big, r, h // 2)
    contact_shadow(big, r, h // 2, m(3), alpha=80)
    pygame.draw.rect(big, PRICE_RIM_DARK, r, width=max(1, m(1.6)),
                     border_radius=h // 2)
    bevel_rim(big, r, h // 2, PRICE_RIM_DARK, (*PRICE_RIM_BRIGHT, 235),
              w=max(1, m(1.5)))

    x = r.x + pad
    _simple_coin(big, x + coin_d // 2, cy, coin_d // 2)
    x += coin_d + gapc
    # Deep warm-brown numeral + 1px gold catch-light ring for legibility on gold
    plain_text(big, text, f, (x + nw // 2, cy), _NUM_COL, shadow_a=0,
               weight=m(1.0), keyline=_NUM_CATCH, kw=m(0.5))
    return r


def render_card(sid, name, price, tier):
    pal   = RARITY.get(tier, MYSTERY)
    big   = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect  = pygame.Rect(m(_INSET), m(_INSET),
                        CARD_W * SS - 2 * m(_INSET), CARD_H * SS - 2 * m(_INSET))
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
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])
    # cx pulled 4 logical px left vs r1 for added right-edge clearance
    _price_coin_pill(big, rect.left + m(108), rect.y + m(50), price, pal, tier)
    _name_filament_core(big, name.upper(), rect.centerx, rect.y + m(81),
                        rect.w - m(26))
    return big


if __name__ == "__main__":
    # Positioning guard — pill must clear disc right edge and card frame right
    # across the full price range the store uses.
    disc_right = m(_INSET) + m(40) + m(R)
    frame_right = (CARD_W * SS - m(_INSET)) - m(6)
    pal = RARITY["epic"]
    probe = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    for p in (1800, 9500, 1250):
        r = _price_coin_pill(probe, m(_INSET) + m(108),
                             m(_INSET) + m(50), p, pal, "epic")
        clr_disc  = r.left - disc_right
        clr_frame = frame_right - r.right
        print(f"price {p:>5}: pill=({r.left},{r.right})"
              f"  disc_gap={clr_disc}  frame_gap={clr_frame}")

    card = render_card("sword", "SWORD", 1800, "epic")
    out = "/home/user/skybit/docs/store_card_v4_r4_price/coin-pill/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(card, out)
    print("saved", out, card.get_size())
