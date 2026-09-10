"""rarity-rim price-chip concept (r3 iteration, round 1) — review render only.

Thesis: gold currency numerals stay readable everywhere; a single thin
hue-coded bevel keyline carries the rarity signal (purple=EPIC, gold=LEGENDARY).
Price and rarity are decoupled onto separate channels. The chip body is a
genuinely dark obsidian — NO glow/halo/additive light touches it.

Headless review sheet: not wired into the live store. Shows both skin_mummy
(EPIC) and skin_kitsune (LEGENDARY), affordable + locked, so the rarity keyline
difference is visible across states.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.hud import _font as hud_font


BG = (8, 8, 20)
MARGIN = 20
GAP = 16

EPIC_SID = "skin_mummy"       # cost 1100
LEGEND_SID = "skin_kitsune"   # cost 3500


# ── the concept: dark-body chip with a rarity-tinted keyline ──────────────────
def price_chip_rarity_rim(surf, cx, cy, text, h, rarity="epic", affordable=True):
    """Dark obsidian price chip. Gold currency numerals read on EVERY state; the
    ONLY rarity cue is one thin hue-tinted bevel keyline (purple=EPIC,
    gold=LEGENDARY). No additive light ever touches the near-black body."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    rar = sc.RARITY[rarity]
    gem = rar["gem"]
    deep = rar["deep"]

    # dark obsidian body — low gloss keeps it near-black; neutral rim, no hue
    rim_dark = (8, 10, 20)
    rim_bright = (60, 65, 100)
    if affordable:
        stops = [(0.0, (12, 13, 22)), (1.0, (34, 37, 56))]
    else:
        stops = [(0.0, (10, 11, 20)), (1.0, (26, 28, 44))]
    sc.chip_body_stops(surf, r, h // 2, stops, rim_dark, rim_bright,
                       gloss=12, gamma=1.04)

    # the ONE rarity-tinted bevel keyline — the sole rarity channel
    if affordable:
        if rarity == "legendary":
            sc.bevel_rim(surf, r, h // 2, (90, 66, 20, 200), (240, 200, 90, 225), w=1)
        else:
            sc.bevel_rim(surf, r, h // 2, (48, 26, 90, 200), (150, 100, 230, 220), w=1)
    else:
        # same rarity hue, dimmed, so a locked chip still whispers its tier
        sc.bevel_rim(surf, r, h // 2, (*deep, 200), (*gem, 110), w=1)

    # coin cell
    x = r.x + pad
    ccx = x + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2, rim=(180, 150, 60))
    if not affordable:
        # cool desaturating veil so the locked coin recedes without a glow
        ov = pygame.Surface((coin_d + 2, coin_d + 2), pygame.SRCALPHA)
        pygame.draw.circle(ov, (60, 70, 90, 140),
                           (coin_d // 2 + 1, coin_d // 2 + 1), coin_d // 2)
        surf.blit(ov, (ccx - coin_d // 2 - 1, cy - coin_d // 2 - 1))
    x += coin_d + gapc
    nx = x + nw // 2

    if affordable:
        # split-cream gold gradient — currency numerals stay gold on ALL rarities
        mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              [(0.0, (255, 246, 205)), (0.48, (250, 230, 150)),
                               (0.52, (226, 168, 66)), (1.0, (178, 124, 34))],
                              255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, img.get_rect(center=(nx, cy)))
    else:
        sc.plain_text(surf, text, f, (nx, cy), (150, 140, 110), shadow_a=0,
                      weight=sc.m(1.0))
    return r


# ── full card carrying the concept chip (mirrors draw_card, chip swapped) ─────
def draw_card_with_chip(surf, sid, rect, equipped=False, secret=False,
                        affordable=True):
    pal = sc.MYSTERY if secret else sc.RARITY[sc._rarity(sid)]
    rad = sc.m(sc.CARD_RAD)
    sc.drop_shadow(surf, rect, rad, blur=sc.m(8), alpha=160, dy=sc.m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252,
                       gamma=1.15), rect.topleft)
    sc.top_sheen(surf, rect, rad, sc.m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, sc.m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, sc.m(2)),
                     border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 235), w=max(1, sc.m(2.0)))
    tray = rect.inflate(-sc.m(7), -sc.m(7))
    trad = rad - sc.m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(sc.m(2), sc.m(2)),
                     width=max(1, sc.m(1)), border_radius=trad + sc.m(1))
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray,
                     width=max(1, sc.m(1)), border_radius=trad)
    cx, cy = rect.centerx, rect.y + sc.m(sc.CY_DISC) + sc._DOME_DY
    sc.soft_glow(surf, cx, cy, sc._DOME_R + sc.m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, sc._DOME_R, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    if secret:
        from game.surprise_box_variants import _draw_qmark
        _draw_qmark(surf, cx, cy, sc._DOME_R + sc.m(6), sc.CREAM,
                    sc.NEAR_BLACK, thick=sc.m(2))
        name = "???"
    else:
        name = sc._name(sid)
    sc.cabochon_glass(surf, cx, cy, sc._DOME_R, tint=pal["gem"])
    if not secret:
        sc.blit_thumb(surf, sid, cx, cy - sc._ITEM_DY, sc._BOX_PX)
    sc.facet_gem(surf, rect.right - sc.m(19), rect.y + sc.m(19),
                 sc.m(sc.GEM_R + 3), pal["gem"], pal["deep"], mystery=secret)
    tier_word = "MYSTERY" if secret else sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + sc.m(55) - sc._RIBN_DY,
                       rect.w - sc.m(34), pal)
    sc._name_on(surf, name, cx, rect.y + sc.m(70), rect.w - sc.m(26))
    price = f"{sc._cost(sid):,}"
    price_chip_rarity_rim(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY, price,
                          sc.m(20), rarity=sc._rarity(sid), affordable=affordable)


# ── review-sheet helpers ──────────────────────────────────────────────────────
def _chip_w(text, h):
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    return pad + coin_d + gapc + nw + pad


def _label(surf, text, cx, cy, size=10, color=(214, 216, 232)):
    f = hud_font(size, True)
    img = f.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))
    return img.get_height()


_CHIP_SPECS = [
    ("1,100", "epic", True),
    ("1,100", "epic", False),
    ("3,500", "legendary", True),
    ("3,500", "legendary", False),
]


def chip_strip_patch(h, scale_down=1):
    """The four chips on ONE card-body gradient patch, so the concept is judged
    against the real card ground it sits on."""
    widths = [_chip_w(t, h) for t, _, _ in _CHIP_SPECS]
    inner_pad = sc.m(20)
    gap = sc.m(24)
    total_w = sum(widths) + gap * 3 + inner_pad * 2
    ph = h + sc.m(22) * 2
    patch = sc.vgrad_stops(total_w, ph, sc.m(14),
                           [(0.0, sc.CARD_T), (1.0, sc.CARD_B)], 255, 1.15)
    x = inner_pad
    cy = ph // 2
    for (t, rar, aff), wch in zip(_CHIP_SPECS, widths):
        price_chip_rarity_rim(patch, x + wch // 2, cy, t, h,
                              rarity=rar, affordable=aff)
        x += wch + gap
    if scale_down != 1:
        patch = pygame.transform.smoothscale(
            patch, (total_w // scale_down, ph // scale_down))
    return patch


def render_sheet():
    ccw = sc.CARD_W * sc.SS   # 324
    cch = sc.CARD_H * sc.SS   # 200

    # cards
    card_specs = [
        (EPIC_SID, True, "EPIC / AFFORDABLE"),
        (EPIC_SID, False, "EPIC / LOCKED"),
        (LEGEND_SID, True, "LEGEND / AFFORDABLE"),
        (LEGEND_SID, False, "LEGEND / LOCKED"),
    ]
    cards = []
    for sid, aff, _lab in card_specs:
        cs = pygame.Surface((ccw, cch), pygame.SRCALPHA)
        rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                           ccw - 2 * sc.m(sc._INSET), cch - 2 * sc.m(sc._INSET))
        draw_card_with_chip(cs, sid, rect, affordable=aff)
        cards.append(cs)

    detail = chip_strip_patch(sc.m(30), scale_down=1)
    true1x = chip_strip_patch(sc.m(20), scale_down=sc.SS)

    row_w = 4 * ccw + 3 * GAP
    sheet_w = MARGIN * 2 + row_w

    f_head = hud_font(18, True)
    f_sub = hud_font(12, True)

    # precompute stacked height
    y = MARGIN
    y += f_head.get_height() + GAP           # header
    y += cch + 8                             # card row
    y += hud_font(10, True).get_height() + GAP   # card labels
    y += f_sub.get_height() + 8              # detail label
    y += detail.get_height() + GAP          # detail strip
    y += f_sub.get_height() + 8             # true1x label
    y += true1x.get_height() + GAP         # true1x strip
    y += f_sub.get_height()                # footer
    sheet_h = y + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill(BG)

    y = MARGIN
    _label(sheet, "v5 price-chip r3 — rarity-rim r1 — EPIC vs LEGENDARY — C(rim-hue)",
           sheet_w // 2, y + f_head.get_height() // 2, size=18, color=(238, 240, 252))
    y += f_head.get_height() + GAP

    # card row
    for i, cs in enumerate(cards):
        x = MARGIN + i * (ccw + GAP)
        sheet.blit(cs, (x, y))
    card_y = y
    y += cch + 8

    # card labels
    lh = hud_font(10, True).get_height()
    for i, (_sid, _aff, lab) in enumerate(card_specs):
        cx = MARGIN + i * (ccw + GAP) + ccw // 2
        _label(sheet, lab, cx, y + lh // 2, size=10)
    y += lh + GAP

    # detail strip
    _label(sheet, "4x DETAIL (on card-body gradient)", sheet_w // 2,
           y + f_sub.get_height() // 2, size=12)
    y += f_sub.get_height() + 8
    sheet.blit(detail, ((sheet_w - detail.get_width()) // 2, y))
    y += detail.get_height() + GAP

    # true 1x strip
    _label(sheet, "TRUE 1x (gameplay scale)", sheet_w // 2,
           y + f_sub.get_height() // 2, size=12)
    y += f_sub.get_height() + 8
    sheet.blit(true1x, ((sheet_w - true1x.get_width()) // 2, y))
    y += true1x.get_height() + GAP

    _label(sheet,
           "dark body  ·  gold numerals everywhere  ·  rarity signal ONLY in thin "
           "bevel keyline (purple=EPIC, gold=LEGENDARY)",
           sheet_w // 2, y + f_sub.get_height() // 2, size=12, color=(196, 198, 216))

    return sheet


def main():
    out = "/home/user/skybit/docs/store_card_v5_price_chip_r3/rarity-rim/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sheet = render_sheet()
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
