"""Headless review render for the `banner-crest` store card v2 concept — round 2.

A trophy-case card: a notched tier ribbon across the body top, a medallion
cabochon centred below, the item name on a frosted-glass plate, and the
canonical gold price chip centred beneath. Round 2 rebudgets the vertical
stack so all four bands (ribbon | disc | name plate | price chip) read with
clear separation and the name plate finally has real height. Renders
RARE / EPIC / LEGENDARY side by side. Not wired into the game.
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
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font

# Locked card geometry — SS=2 author canvas, 6px body inset (see store_cards).
CARD_W, CARD_H = 162, 100
INSET = 6
BODY_W, BODY_H = 150, 88          # visible body rect at (INSET, INSET)

# Rebudgeted vertical stack (body-relative logical px). Round 1 crushed the
# name plate to ~2 scanlines; here every band is allotted room and a gap:
#   ribbon  y=2..17 (h=15)
#   disc    cy=39, R=21 -> spans y=18..60   (1px below ribbon)
#   name    plate top y=62, h=13 -> y=62..75 (2px below disc)
#   chip    cy=82, h=12 -> y=76..88          (1px below plate, bottom = body foot)
R = 21                             # medallion disc radius (logical)
CY_DISC = 39
NAME_TOP = 62
NAME_H = 13
CHIP_CY = 82
CHIP_H = 12


def _goldish(col):
    """A tier gem so warm the ribbon under the crest gem is itself gold — cream
    type and gold facets vanish against it, so these need a dark treatment."""
    r, g, b = col[0], col[1], col[2]
    return r > 200 and g > 150 and b < 160


def _notched_ribbon(big, body_x, body_y, cx_ss, pal, tier_word):
    """A tier-gradient award ribbon with triangular-notched ends — inset from
    the body edges so the notches read as a ribbon rather than a full-bleed
    colour bar. Dark defined edge; tier word darkened when the gem is gold."""
    w, h = m(BODY_W - 14), m(15)
    notch = m(5)
    x0 = cx_ss - w // 2
    y0 = body_y + m(2)
    top = lerp_color(pal["gem"], WHITE, 0.10)
    bot = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0,
                       [(0.0, top), (0.5, pal["glow"]), (1.0, bot)], 255,
                       gamma=1.08)
    poly = [(notch, 0), (w - notch, 0), (w, h // 2), (w - notch, h),
            (notch, h), (0, h // 2)]
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # cast shadow so the ribbon lifts off the body
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(big, (4, 5, 16), abspoly, width=max(1, m(1.4)))

    # tier word: dark brown on a gold ribbon (cream fails), cream + dark keyline
    # otherwise. Either way a keyline keeps the strokes crisp on the gradient.
    gold = _goldish(pal["gem"])
    fill = (60, 38, 10) if gold else (250, 248, 230)
    key = (150, 110, 40) if gold else (6, 6, 16)
    plain_text(big, tier_word, font(8.5), (cx_ss, y0 + h // 2), fill,
               shadow_a=0, tracking=m(1.4), weight=m(0.7), keyline=key,
               kw=m(0.8))


def _frosted_plate(big, body_x, body_y, cx_ss, sid):
    """The frosted name plate: a translucent dark rounded slab with a faint gold
    top edge so it reads as a glass label seated between the disc and the chip
    (Round 1's plate was too short to see)."""
    pw, ph = m(BODY_W - 16), m(NAME_H)
    px = cx_ss - pw // 2
    py = body_y + m(NAME_TOP)
    plate = pygame.Surface((pw, ph), pygame.SRCALPHA)
    prad = m(4)
    pygame.draw.rect(plate, (14, 16, 34, 185), (0, 0, pw, ph),
                     border_radius=prad)
    # faint gold keyline + a lit top edge => a "frosted plate", not a hole
    pygame.draw.rect(plate, (*CARD_RING_BRIGHT, 70), (0, 0, pw, ph),
                     width=max(1, m(0.8)), border_radius=prad)
    pygame.draw.line(plate, (255, 255, 255, 55), (prad, m(1)),
                     (pw - prad, m(1)), max(1, m(0.8)))
    big.blit(plate, (px, py))
    plain_text(big, name_of(sid), font(11.5),
               (cx_ss, py + ph // 2), (250, 248, 240), shadow_a=150,
               weight=m(0.8), keyline=(6, 6, 16), kw=m(0.9))


def draw_banner_crest(big, sid, rect, pal, price_str, tier_word):
    """One banner-crest card onto `big` at device-px `rect`, in the locked
    draw order (ribbon under the crest gem, chip centred, edge last)."""
    rad = m(CARD_RAD)
    body_x, body_y = rect.x, rect.y
    cx_ss = rect.centerx
    cy_ss = rect.y + m(CY_DISC)

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

    # 6 — HEADER TIER RIBBON: a notched award ribbon carrying the tier word.
    _notched_ribbon(big, body_x, body_y, cx_ss, pal, tier_word)

    # 7 — soft tier aura under the medallion.
    soft_glow(big, cx_ss, cy_ss, m(R + 3), pal["glow"], 30, layers=8)
    # 8 — cabochon well + rim-lit hero skin + glass dome overlay.
    cabochon(big, cx_ss, cy_ss, m(R), CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    blit_thumb(big, sid, cx_ss, cy_ss, m(R) * 1.5)
    cabochon_glass(big, cx_ss, cy_ss, m(R), tint=pal["gem"])

    # 9 — frosted name plate (real height now) + name.
    _frosted_plate(big, body_x, body_y, cx_ss, sid)

    # 10 — price chip: canonical GOLD RAMP A, centred, bottom at body foot.
    price_chip(big, cx_ss, body_y + m(CHIP_CY), price_str, m(CHIP_H),
               affordable=True)

    # 11 — CREST GEM: a faceted tier gem pinned to the ribbon's top-right end.
    # A dark collar bezel first so a GOLD gem's facets never vanish into a gold
    # ribbon (LEGENDARY was gold-on-gold in R1).
    gem_cx, gem_cy = rect.right - m(19), rect.y + m(19)
    pygame.draw.circle(big, (20, 16, 8), (gem_cx, gem_cy), m(GEM_R + 5),
                       width=max(1, m(3)))
    facet_gem(big, gem_cx, gem_cy, m(GEM_R + 3), pal["gem"], pal["deep"])

    # 12 — defined edge LAST: dark keyline under the bright gold bevel.
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235),
              w=max(1, m(2.0)))


# Names shown on the frosted plate — kept literal so the review sheet reads
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

    # 1x strip beneath the SS panels so the shipped-resolution read is visible.
    strip_h = CARD_H
    sheet_w = margin * 2 + panel_w * n + gutter * (n - 1)
    sheet_h = (margin * 2 + header_h + panel_h + footer_h + strip_h + 20)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 46))

    hf = _font(26, True)
    htxt = hf.render("store_card_v2 - banner-crest - round 2", True, (238, 232, 214))
    sheet.blit(htxt, (margin, margin + (header_h - htxt.get_height()) // 2))

    ff = _font(22, True)
    panel_top = margin + header_h
    for i, (label, sid, pal, price) in enumerate(variants):
        px = margin + i * (panel_w + gutter)
        panel = render_panel(sid, pal, price)
        sheet.blit(panel, (px, panel_top))
        lt = ff.render(label, True, (232, 226, 208))
        sheet.blit(lt, (px + (panel_w - lt.get_width()) // 2,
                        panel_top + panel_h + (footer_h - lt.get_height()) // 2))
        # 1x downscale of the same panel, centred under each column.
        one = pygame.transform.smoothscale(panel, (CARD_W, CARD_H))
        sheet.blit(one, (px + (panel_w - CARD_W) // 2,
                         panel_top + panel_h + footer_h + 10))

    out = "/home/user/skybit/docs/store_card_v2/banner-crest/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
