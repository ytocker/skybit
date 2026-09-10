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
    chip_body_stops, coin_glyph,
    CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    CABO_LO, CABO_HI, GEM_R, RARITY, MYSTERY, _rarity,
    lerp_color, WHITE, NEAR_BLACK,
    PRICE_STOPS, PRICE_RIM_DARK, PRICE_RIM_BRIGHT, GOLD_A_NUM, GOLD_A_COIN_RIM,
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


# Rarity reads through the price tag WITHOUT restaining the gold: a soft under-
# glow whose intensity climbs by tier, and a bevel that warms its bright edge
# toward the gem hue. The body ramp itself is the ONE constant gold so the price
# still reads as currency, not as a second gem.
_GLOW_PEAK = {"common": 16, "rare": 24, "epic": 32, "legendary": 48}
_BEVEL_WARM = {"common": 0.0, "rare": 0.11, "epic": 0.22, "legendary": 0.34}


def _price_coin_pill(big, cx, cy, price, pal, tier):
    """Industry-standard horizontal price pill: coin glyph in a left cell, bold
    amber numeral in a right cell, on the ONE gold ramp with a double rim. Tighter
    padding + a smaller coin than the live chip so it sits compact in the card's
    upper-right without crowding the disc or clipping the frame."""
    text = f"{price:,}"
    h = m(21)
    coin_d = int(h * 0.60)                          # a touch smaller than the live chip
    pad = m(7)                                        # compact vs the live m(13)
    gapc = m(5)                                       # compact vs the live m(8)
    f = font(h * 0.50 / SS)
    nw = _glyph_base(text, f, 0).get_width() + m(2)   # account for faux-bold
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    soft_glow(big, cx, cy, w // 2 + m(4), pal["glow"], _GLOW_PEAK.get(tier, 16),
              layers=8)
    rim_bright = lerp_color(PRICE_RIM_BRIGHT, pal["gem"], _BEVEL_WARM.get(tier, 0.0))
    chip_body_stops(big, r, h // 2, PRICE_STOPS, PRICE_RIM_DARK, rim_bright,
                    gloss=40, gamma=1.04)

    x = r.x + pad
    coin_glyph(big, x + coin_d // 2, cy, coin_d // 2, rim=GOLD_A_COIN_RIM)
    x += coin_d + gapc
    plain_text(big, text, f, (x + nw // 2, cy), GOLD_A_NUM, shadow_a=0,
               weight=m(1.0), kw=m(0.7))
    return r


def render_card(sid, name, price, tier):
    pal   = RARITY.get(tier, MYSTERY)
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
    _price_coin_pill(big, rect.left + m(112), rect.y + m(50), price, pal, tier)
    _name_filament_core(big, name.upper(), rect.centerx, rect.y + m(81), rect.w - m(26))
    return big


if __name__ == "__main__":
    # Positioning guard — the pill must clear the disc's right edge and never
    # clip the card frame across the range of price widths the store shows.
    disc_right = m(_INSET) + m(40) + m(R)            # cabochon right edge, device px
    frame_right = (CARD_W * SS - m(_INSET)) - m(6)
    pal = RARITY["epic"]
    probe = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    for p in (1800, 9500, 1250):
        r = _price_coin_pill(probe, m(_INSET) + m(112), m(_INSET) + m(50), p, pal, "epic")
        clr_disc = r.left - disc_right
        clr_frame = frame_right - r.right
        print(f"price {p:>5}: pill=({r.left},{r.right}) disc_gap={clr_disc} frame_gap={clr_frame}")

    card = render_card("sword", "SWORD", 1800, "epic")
    out = "/home/user/skybit/docs/store_card_v4_r4_price/coin-pill/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(card, out)
    print("saved", out, card.get_size())
