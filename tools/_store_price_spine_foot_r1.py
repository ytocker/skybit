"""Round-1 render sheet for the `spine-foot` store-card price redesign.

Monkey-patches store_cards.price_chip with a two-part read: a decorative gold
enamel SPINE down the left gutter (punched hole up top, identical in both
affordability states) plus a compact upright horizontal micro-CHIP at the
spine's foot that carries the actual price — no rotated text. Affordability
lives only in the foot chip (coin-metal numerals + warm gold rim when
affordable, pewter numerals + steel rim when locked); the spine stays gold
either way. Renders four v5 cards (EPIC + LEGENDARY x afford/locked) plus a
4x zoomed crop of the left gutter + price area. Review-only tooling — never
imported by the game.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as store_data
from game.hud import _font as hud_font


# ── spine-foot price chip ─────────────────────────────────────────────────────
# Device-px coords in the 324x200 (2x) card buffer, authored directly (NOT via
# m()) because the brief specifies them at the buffer scale already. cx/cy are
# ignored: this chip anchors to the card's left gutter, not the old
# bottom-centre lane, so it reads at a fixed spot regardless of the caller's
# centre hint.
def my_price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    # (a) DECORATIVE SPINE — gold enamel bar, identical in both states so the
    # card's left edge always carries the same jewellery cue; only the foot
    # chip flips with affordability.
    spine = pygame.Rect(19, 50, 8, 100)
    surf.blit(sc.vgrad_stops(spine.w, spine.h, 4, sc.GOLD_A_STOPS,
                             255, gamma=sc.GOLD_A_GAMMA), spine.topleft)
    pygame.draw.rect(surf, sc.GOLD_A_RIM_DARK, spine, width=1, border_radius=4)
    # bright top-left kiss so the enamel bar reads domed, not flat
    pygame.draw.line(surf, (*sc.GOLD_A_RIM_BRIGHT, 150),
                     (spine.x + 2, spine.y + 6), (spine.x + 2, spine.bottom - 6), 1)

    # punched hole up top: a dark well ringed in gold, with a bottom-right
    # bright arc so the bore reads sunken rather than painted.
    hx, hy, hr = 23, 58, 4
    pygame.draw.circle(surf, (15, 15, 30), (hx, hy), hr)
    pygame.draw.circle(surf, (208, 158, 78), (hx, hy), hr, 1)
    pygame.draw.arc(surf, (255, 236, 180),
                    (hx - hr, hy - hr, hr * 2, hr * 2),
                    0.6, 2.2, 1)

    # (b) UPRIGHT FOOT CHIP — the price read, standard left-to-right. Dark
    # enamel pill seated at the spine's base.
    r = pygame.Rect(30, 158, 88, 22)
    rad = 11
    sc._dark_chip_body(surf, r, rad,
                       [(0.0, (26, 20, 32)), (1.0, (18, 14, 24))],
                       (10, 11, 22), (56, 52, 76), gloss=14, gamma=1.04)

    if affordable:
        sc.bevel_rim(surf, r, rad, (120, 88, 28, 235), (230, 200, 130), w=2)
        num_col = None                    # coin-metal gradient poured below
    else:
        sc.bevel_rim(surf, r, rad, (60, 64, 80), (150, 156, 172), w=2)
        num_col = (150, 150, 168)         # pewter

    # coin glyph — the exact in-game coin
    sc.coin_glyph(surf, 46, 169, 8)

    # price numerals, left-aligned from x=60, vertically centred on the coin.
    f = sc.font(9)
    base = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
    if num_col is None:
        grad = sc.vgrad_stops(base.get_width(), base.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img = base.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img = base.copy()
        img.fill((*num_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    rct = img.get_rect()
    rct.midleft = (60, 169)
    surf.blit(img, rct)
    return r


sc.price_chip = my_price_chip   # monkey-patch BEFORE any draw_card call


CARD_W_SS = sc.CARD_W * sc.SS   # 324
CARD_H_SS = sc.CARD_H * sc.SS   # 200

# (sid, tier-label, affordable) — the four requested review states.
STATES = [
    ("skin_mummy",   "MUMMY  EPIC  ·  AFFORD",  True),
    ("skin_mummy",   "MUMMY  EPIC  ·  LOCKED",  False),
    ("skin_kitsune", "KITSUNE  LEGEND  ·  AFFORD", True),
    ("skin_kitsune", "KITSUNE  LEGEND  ·  LOCKED", False),
]


def _draw_big(sid, affordable):
    """Author one card at SS, controlling affordability via the wallet the
    price chip reads. Returns the 324x200 SS surface (kept for the crop)."""
    store_data.balance = (lambda: 10 ** 9) if affordable else (lambda: 0)
    big = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, CARD_W_SS - 2 * inset, CARD_H_SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False)
    return big


def main():
    out_dir = "/home/user/skybit/docs/store_price_redesign/spine-foot"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    pad = 28
    gap = 22
    header_h = 42
    label_h = 22

    bigs = [_draw_big(sid, aff) for sid, _, aff in STATES]
    cards = [pygame.transform.smoothscale(b, (sc.CARD_W, sc.CARD_H)) for b in bigs]
    cw, chh = sc.CARD_W, sc.CARD_H

    row1_y = header_h + pad
    row1_w = cw * 4 + gap * 3

    # 4x zoom crops of the left gutter + price area (affordable + locked) from
    # the SS buffers so the enamel edges stay crisp under magnification.
    crop = pygame.Rect(14, 44, 112, 142)
    zoom = 4
    zsz = (crop.w * zoom, crop.h * zoom)
    crops = [(bigs[0], "AFFORD zoom 4x"), (bigs[1], "LOCKED zoom 4x")]
    row2_y = row1_y + chh + label_h + gap * 2
    row2_w = zsz[0] * 2 + gap

    canvas_w = pad * 2 + max(row1_w, row2_w)
    canvas_h = row2_y + zsz[1] + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(28, True)
    lf = hud_font(15)

    canvas.blit(hf.render("store price — spine-foot r1", True, (236, 232, 250)),
                (pad, pad // 2 + 2))

    # Row 1 — the four cards, labelled.
    x = pad + (max(row1_w, row2_w) - row1_w) // 2
    for card, (_, label, _aff) in zip(cards, STATES):
        canvas.blit(card, (x, row1_y))
        lbl = lf.render(label, True, (206, 202, 224))
        canvas.blit(lbl, (x + (cw - lbl.get_width()) // 2, row1_y + chh + 5))
        x += cw + gap

    # Row 2 — 4x zoomed crops.
    x = pad + (max(row1_w, row2_w) - row2_w) // 2
    for big, label in crops:
        piece = big.subsurface(crop).copy()
        z = pygame.transform.scale(piece, zsz)
        canvas.blit(z, (x, row2_y))
        pygame.draw.rect(canvas, (40, 42, 66),
                         (x, row2_y, zsz[0], zsz[1]), width=1)
        lbl = lf.render(label, True, (206, 202, 224))
        canvas.blit(lbl, (x + (zsz[0] - lbl.get_width()) // 2, row2_y + zsz[1] + 4))
        x += zsz[0] + gap

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
