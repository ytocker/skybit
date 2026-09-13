"""Round-2 render sheet for the DOG-EAR store-card price treatment.

Round 1's peel read as a tilted ribbon, not a lifting sticker, so round 2 OWNS
THE CORNER BANNER instead of faking the lift: an AXIS-ALIGNED right-triangle
seated flat in the card's bottom-left corner, carrying an upright price. No
rotation anywhere. The whole tag re-tints — warm gold when the player can buy,
cool pewter (with a padlock) when locked — so affordability reads at a glance.
The tag's compact bottom-left mass is the diagonal counterweight to the crest
gem in the top-right, and a faint warm line along the card's bottom edge closes
the composition.

Review-only tooling — never imported by the game.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game import store_catalog as cat
from game import store_data
from game.hud import _font as hud_font


# ── tag palette ───────────────────────────────────────────────────────────────
# Affordable rides the canonical Ramp-A gold the card already speaks; locked is a
# MANDATORY flip to cool pewter so the state reads as colour, not just geometry.
GOLD_STOPS   = sc.GOLD_A_STOPS
GOLD_RIM_HI  = sc.GOLD_A_RIM_BRIGHT          # (255,240,190)
GOLD_RIM_LO  = sc.GOLD_A_RIM_DARK            # (86,50,8)
GOLD_NUM_DROP = (40, 24, 4)                  # dark relief under gold numerals

PEWTER_STOPS  = [(0.0, (156, 160, 176)), (0.5, (120, 124, 142)), (1.0, (78, 82, 100))]
PEWTER_RIM_HI = (214, 218, 230)
PEWTER_RIM_LO = (54, 58, 74)
PEWTER_NUM    = (176, 182, 202)              # cool slate numerals
PEWTER_NUM_DROP = (30, 34, 46)
PEWTER_LOCK   = (188, 194, 214)              # padlock glyph — a shade brighter

# Triangle vertices in the 2x card buffer (right angle bottom-left, left leg up,
# bottom leg right, hypotenuse = the crease). All axis-aligned — no rotation.
TX0, TY0 = sc.m(6),  sc.m(66)                # (12,132) crease top on the left edge
TX1, TY1 = sc.m(40), sc.m(94)               # (80,188) crease foot on the bottom
TXC, TYC = sc.m(6),  sc.m(94)               # (12,188) right-angle corner
TRI = [(TX0, TY0), (TX1, TY1), (TXC, TYC)]

COIN_CX, COIN_CY = sc.m(11), sc.m(89)        # (22,178) coin/lock centre
COIN_R = sc.m(3.5)                           # r=7 device — a small functional glyph
TEXT_X = sc.m(18)                            # (36) price numerals start here


def _hyp_x(y):
    """Where the crease diagonal sits at row y — the triangle's right boundary,
    so the price can be sized to stay inside the fold."""
    return TX0 + (TX1 - TX0) * (y - TY0) / (TY1 - TY0)


def _fit_font(text):
    """The fixed corner tag is small; a 6-digit price won't fit at font(9). Pick
    the largest size whose numerals sit fully inside the fold to the right of the
    coin, so the whole number stays legible upright (never clipped to mush)."""
    limit = _hyp_x(COIN_CY)                   # right boundary at the numeral baseline
    for s in (8, 7.5, 7, 6.5, 6, 5.5, 5):
        f = sc.font(s)
        if TEXT_X + sc._glyph_base(text, f, 0).get_width() <= limit:
            return f
    return sc.font(5)


def _numerals(layer, text, f, affordable):
    """Upright price glyphs seated along the fold's bottom band: gold coin-metal
    fill (affordable) or cool slate (locked), each over a faint dark drop so the
    metal-on-metal / slate-on-pewter still separates from the tag fill."""
    mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(0.6))
    w, h = mask.get_size()
    x, y = TEXT_X, COIN_CY - h // 2
    drop = mask.copy()
    drop.fill((*(GOLD_NUM_DROP if affordable else PEWTER_NUM_DROP), 255),
              special_flags=pygame.BLEND_RGBA_MULT)
    drop.set_alpha(160)
    layer.blit(drop, (x + sc.m(0.6), y + sc.m(0.7)))
    if affordable:
        grad = sc.vgrad_stops(w, h, 0, sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img = mask.copy()
        img.fill((*PEWTER_NUM, 255), special_flags=pygame.BLEND_RGBA_MULT)
    layer.blit(img, (x, y))


def _padlock(layer):
    """A minimal lock in the coin's slot when locked — a wordless 'can't buy
    yet'. Rounded body + a top D-arc shackle, in slightly brighter pewter."""
    bw, bh = sc.m(6), sc.m(5)
    bx, by = COIN_CX - bw // 2, COIN_CY - sc.m(1)
    pygame.draw.rect(layer, PEWTER_LOCK, (bx, by, bw, bh),
                     border_radius=max(1, sc.m(1)))
    pygame.draw.arc(layer, PEWTER_LOCK,
                    (COIN_CX - sc.m(2), by - sc.m(3), sc.m(4), sc.m(6)),
                    math.radians(20), math.radians(160), max(1, sc.m(1.2)))


def my_price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    """DOG-EAR corner tag: an axis-aligned gold/pewter right-triangle in the
    card's bottom-left corner carrying the upright price + coin (or padlock)."""
    if affordable:
        stops, rim_hi, rim_lo = GOLD_STOPS, GOLD_RIM_HI, GOLD_RIM_LO
        anchor = (255, 228, 168, 40)
    else:
        stops, rim_hi, rim_lo = PEWTER_STOPS, PEWTER_RIM_HI, PEWTER_RIM_LO
        anchor = (150, 156, 176, 30)

    # ── card anchor: a faint warm line along the lit bottom bevel gives the
    # composition closure and counterweights the top-right crest gem. Drawn on
    # the real body edge (m(93)); the literal 194 would fall below the body.
    ay = sc.m(93)
    pygame.draw.line(surf, anchor, (sc.m(23), ay), (sc.CARD_W * sc.SS - sc.m(23), ay),
                     max(1, sc.m(0.6)))

    # ── content layer: gradient fill + coin/lock + numerals, then hard-clipped
    # to the triangle so the upright price is trimmed cleanly by the fold ──
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    bw, bh = TX1 - TXC, TYC - TY0
    layer.blit(sc.vgrad_stops(bw, bh, 0, stops, 255, gamma=sc.GOLD_A_GAMMA),
               (TXC, TY0))
    if affordable:
        sc.coin_glyph(layer, COIN_CX, COIN_CY, COIN_R, rim=sc.GOLD_A_COIN_RIM)
    else:
        _padlock(layer)
    _numerals(layer, text, _fit_font(text), affordable)
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), TRI)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # ── soft cast shadow (offset +2,+2) BEHIND the tag, then the tag on top ──
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    off = [(x + sc.m(1), y + sc.m(1)) for x, y in TRI]
    pygame.draw.polygon(shadow, (0, 0, 0, 90), off)
    surf.blit(shadow, (0, 0))
    surf.blit(layer, (0, 0))

    # crease: a bright rim along the fold diagonal (the lifted free edge catches
    # light); the two cut outer edges get a thin dark contact keyline.
    pygame.draw.line(surf, (*rim_hi, 220), (TX0, TY0), (TX1, TY1), max(1, sc.m(1)))
    pygame.draw.line(surf, (6, 6, 14, 210), (TXC, TY0), (TXC, TYC), max(1, sc.m(0.6)))
    pygame.draw.line(surf, (6, 6, 14, 210), (TXC, TYC), (TX1, TYC), max(1, sc.m(0.6)))
    return pygame.Rect(cx, cy, 1, 1)


sc.price_chip = my_price_chip                # patch BEFORE any draw_card call


# ── render helpers ────────────────────────────────────────────────────────────
def render_card_1x(sid, affordable):
    """Full v5 card at native 162x100: 2x author render then one smoothscale.
    Wallet is stubbed so state_chip resolves the affordability we want."""
    store_data.balance = (lambda: 10 ** 9) if affordable else (lambda: 0)
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                       sc.CARD_H * sc.SS - 2 * sc.m(sc._INSET))
    sc.draw_card(big, sid, rect, equipped=False, secret=False)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def main():
    out_dir = "/home/user/skybit/docs/store_price_redesign/dog-ear"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

    pad, gap = 20, 12
    header_h = 40
    label_h = 20

    specs = [
        ("skin_mummy",   True,  "MUMMY · EPIC · affordable"),
        ("skin_mummy",   False, "MUMMY · EPIC · locked"),
        ("skin_kitsune", True,  "KITSUNE · LEG · affordable"),
        ("skin_kitsune", False, "KITSUNE · LEG · locked"),
    ]
    cards = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in specs]
    cw, ch = cards[0][0].get_size()

    # 4x zoom of the corner (x 0-60, y 72-100 of the 1x card -> 240x112).
    def corner_zoom(sid, aff):
        src = render_card_1x(sid, aff)
        crop = src.subsurface(pygame.Rect(0, 72, 60, 28)).copy()
        return pygame.transform.scale(crop, (240, 112))

    zoom_aff = corner_zoom("skin_kitsune", True)
    zoom_lck = corner_zoom("skin_kitsune", False)

    row1_w = cw * 4 + gap * 3
    row2_w = 240 + gap + 240
    canvas_w = pad * 2 + max(row1_w, row2_w)
    row1_y = header_h
    row2_y = row1_y + ch + label_h + gap
    canvas_h = row2_y + 112 + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))
    hf = hud_font(26, True)
    lf = hud_font(15)
    canvas.blit(hf.render("store price — dog-ear r2 (corner banner)", True,
                          (236, 232, 250)), (pad, 8))

    x = pad
    for card, lbl in cards:
        canvas.blit(card, (x, row1_y))
        canvas.blit(lf.render(lbl, True, (206, 202, 224)), (x, row1_y + ch + 3))
        x += cw + gap

    x = pad
    canvas.blit(zoom_aff, (x, row2_y))
    canvas.blit(lf.render("4x corner · affordable", True, (206, 202, 224)),
                (x, row2_y + 112 + 3))
    x += 240 + gap
    canvas.blit(zoom_lck, (x, row2_y))
    canvas.blit(lf.render("4x corner · locked", True, (206, 202, 224)),
                (x, row2_y + 112 + 3))

    pygame.image.save(canvas, out)

    # ── pixel verification ────────────────────────────────────────────────────
    aff = render_card_1x("skin_kitsune", True)
    lck = render_card_1x("skin_kitsune", False)

    r, g, b, _ = aff.get_at((20, 88))
    assert r > 140 and r > b + 20, f"affordable tag not warm gold at (20,88): {(r,g,b)}"
    lr, lg, lb, _ = lck.get_at((20, 88))
    assert lb > lr, f"locked tag not cool pewter at (20,88): {(lr,lg,lb)}"

    # upright gold numerals must appear inside the fold (bright coin-metal vs the
    # darker amber tag fill).
    num_hits = 0
    for yy in range(80, 96):
        for xx in range(14, 40):
            pr, pg, pb, pa = aff.get_at((xx, yy))
            if pa > 60 and pr > 205 and pg > 180 and pb < 165:
                num_hits += 1
    assert num_hits > 8, f"upright gold numerals missing in fold: {num_hits}"

    print("verify OK — gold@(20,88)=%s pewter@(20,88)=%s numeral_px=%d"
          % ((r, g, b), (lr, lg, lb), num_hits))
    print("saved %dx%d -> %s" % (canvas.get_width(), canvas.get_height(), out))


if __name__ == "__main__":
    main()
