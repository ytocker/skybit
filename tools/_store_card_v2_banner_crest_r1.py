"""Headless review render for the `banner-crest` store card v2 concept.

A trophy-case card: a full-width tier banner across the body top, a medallion
cabochon centred below, the item name on a frosted-glass strip, and the
canonical gold price chip centred beneath. Renders RARE / EPIC / LEGENDARY
side by side so the tier read + the locked gold chip can be judged together.
Not wired into the game — this only writes a docs/ review sheet.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.store_cards import (
    vgrad, vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, price_chip, facet_gem, cabochon, cabochon_glass, blit_thumb,
    soft_glow, font, m, SS, CABO_LO, CABO_HI, CARD_T, CARD_B,
    CARD_RING_DEEP, CARD_RING_BRIGHT, CREAM, CARD_RAD, GEM_R,
)
from game.hud import _font

# Locked card geometry — SS=2 author canvas, 6px body inset (see store_cards).
CARD_W, CARD_H = 162, 100
INSET = 6
BODY_W, BODY_H = 150, 88          # visible body rect at (INSET, INSET)
R = 30                             # medallion disc radius (logical)


def draw_banner_crest(big, sid, rect, pal, price_str, tier_word):
    """One banner-crest card onto `big` at device-px `rect`, in the locked
    draw order (banner under the crest gem, chip centred, edge last)."""
    rad = m(CARD_RAD)
    body_x, body_y = rect.x, rect.y
    cx_ss = rect.centerx
    cy_ss = rect.y + m(48)          # medallion centre: body-relative cy=48

    # 1 — depth: soft multi-layer drop shadow (top-left light => offset down).
    drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    # 2 — body gradient.
    big.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15),
             rect.topleft)
    # 3 — glossy top sheen.
    top_sheen(big, rect, rad, m(30), peak=62)
    # 4 — bottom-right contact AO.
    contact_shadow(big, rect, rad, m(9), alpha=120)
    # 5 — inner tray: dark contact border under a faint gold lane.
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)

    # 6 — HEADER TIER BANNER: a full-width tier-gradient band across the body
    # top (body-rel y=2..17). Top corners are clipped to the body radius so the
    # band blends into the card edge rather than floating as a loose bar.
    bw, bh = m(BODY_W), m(15)
    banner = vgrad_stops(bw, bh, 0,
                         [(0.0, pal["gem"]), (0.5, pal["glow"]), (1.0, pal["deep"])],
                         255)
    bmask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(bmask, (255, 255, 255, 255), (0, 0, bw, bh),
                     border_top_left_radius=rad, border_top_right_radius=rad)
    banner.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(banner, (body_x, body_y + m(2)))
    # tier word centred on the banner, heavy + dark-keyed so it reads on the
    # bright tier gradient.
    plain_text(big, tier_word, font(9), (cx_ss, body_y + m(9)), (250, 248, 230),
               shadow_a=0, tracking=m(1.2), weight=m(0.8), keyline=(6, 6, 16),
               kw=m(0.8))

    # 7 — soft tier aura under the medallion.
    soft_glow(big, cx_ss, cy_ss, m(R + 3), pal["glow"], 30, layers=8)
    # 8 — cabochon well + rim-lit hero skin + glass dome overlay.
    cabochon(big, cx_ss, cy_ss, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx_ss, cy_ss, m(R) * 1.5)
    cabochon_glass(big, cx_ss, cy_ss, m(R), tint=pal["gem"])

    # 9 — frosted name band at the disc lower arc (body-rel cy=72) + name.
    strip = pygame.Surface((m(BODY_W - 16), m(14)), pygame.SRCALPHA)
    strip.fill((10, 10, 24, 170))
    big.blit(strip, (body_x + m(8), body_y + m(65)))
    plain_text(big, name_of(sid), font(13.5), (cx_ss, body_y + m(72)), CREAM,
               shadow_a=160, weight=m(0.8), keyline=(6, 6, 16), kw=m(0.8))

    # 10 — price chip: canonical GOLD RAMP A, centred on the x-axis (never a
    # corner, never recoloured). Bottom lands at body-rel y=88 exactly.
    price_chip(big, cx_ss, body_y + m(78), price_str, m(20), affordable=True)

    # 11 — CREST GEM: a larger faceted tier gem top-right, drawn on top of the
    # banner's top-right edge so it reads as a rank seal pinned to the header.
    facet_gem(big, rect.right - m(19), rect.y + m(19), m(GEM_R + 3),
              pal["gem"], pal["deep"])

    # 12 — defined edge LAST: dark keyline under the bright gold bevel.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))


# Names shown on the frosted band — kept literal so the review sheet reads
# without pulling live catalog state.
_NAMES = {"skin_lorikeet": "LORIKEET", "skin_prism": "PRISM",
          "skin_kitsune": "KITSUNE"}


def name_of(sid):
    return _NAMES.get(sid, sid.replace("skin_", "").upper())


def render_panel(sid, pal, price):
    """Draw one card at full SS canvas (324x200) so the review sheet shows the
    author-resolution art (no downscale)."""
    big = pygame.Surface((CARD_W * SS, CARD_H * SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(INSET), m(INSET),
                       CARD_W * SS - 2 * m(INSET), CARD_H * SS - 2 * m(INSET))
    draw_banner_crest(big, sid, rect, pal, f"{price:,}", tier_of(price))
    return big


def tier_of(price):
    return {600: "RARE", 1400: "EPIC", 3500: "LEGENDARY"}[price]


def main():
    variants = [
        ("RARE", "skin_lorikeet",
         {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}, 600),
        ("EPIC", "skin_prism",
         {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}, 1400),
        ("LEGENDARY", "skin_kitsune",
         {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}, 3500),
    ]

    panel_w, panel_h = CARD_W * SS, CARD_H * SS
    margin, gutter, header_h, footer_h = 20, 16, 40, 30
    n = len(variants)
    sheet_w = margin * 2 + panel_w * n + gutter * (n - 1)
    sheet_h = margin * 2 + header_h + panel_h + footer_h

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 46))

    hf = _font(26, True)
    htxt = hf.render("store_card_v2 - banner-crest - round 1", True, (238, 232, 214))
    sheet.blit(htxt, (margin, margin + (header_h - htxt.get_height()) // 2))

    ff = _font(22, True)
    panel_top = margin + header_h
    for i, (label, sid, pal, price) in enumerate(variants):
        px = margin + i * (panel_w + gutter)
        sheet.blit(render_panel(sid, pal, price), (px, panel_top))
        lt = ff.render(label, True, (232, 226, 208))
        sheet.blit(lt, (px + (panel_w - lt.get_width()) // 2,
                        panel_top + panel_h + (footer_h - lt.get_height()) // 2))

    out = "/home/user/skybit/docs/store_card_v2/banner-crest/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
