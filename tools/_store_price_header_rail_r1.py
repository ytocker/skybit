"""Round-1 render sheet for the header-rail store-card price redesign.

Monkey-patches store_cards.state_chip with a dark-enamel RAIL that spans the
card top: the item name rides the left, the price rides the right, unified in
one app-store editorial bar. The rail deliberately stops at x=248, clearing the
crest gem's bbox (starts x=252) so the two never collide. Renders four cards
(EPIC + LEGENDARY, affordable + locked) plus a 4x zoom of each top rail so the
type, coin and hairline detail can be judged. Review-only tooling — never
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
from game.hud import _font as hud_font


# ── rail geometry (device px on the 324x200 author buffer) ────────────────────
RAIL = pygame.Rect(24, 14, 224, 26)   # right edge 248 clears the crest gem @252
RAIL_RAD = 13
RAIL_CY = 27                          # vertical centre of the rail interior
NAME_LEFT = 34                        # name left margin
NAME_MAX_RIGHT = 150                  # name must stop here so price has room
COIN_CX = 196
COIN_R = 9
NUM_LEFT = 208

CREAM = (246, 244, 232)

# Affordability is read from store_data.balance(); this lets the sheet force an
# affordable vs. locked rail per card without touching the real wallet.
_FORCE_BALANCE = [10 ** 9]


def _draw_name(surf, name):
    """Item name, cream, left-aligned at NAME_LEFT, auto-shrunk so its right
    edge never crosses into the price zone."""
    sz = 11.0
    f = sc.font(sz)
    avail = NAME_MAX_RIGHT - NAME_LEFT
    while sc._glyph_base(name, f, 0).get_width() > avail and sz > 7.5:
        sz -= 0.5
        f = sc.font(sz)
    w = sc._glyph_base(name, f, 0).get_width()
    sc.plain_text(surf, name, f, (NAME_LEFT + w // 2, RAIL_CY), CREAM,
                  shadow_a=140, weight=sc.m(0.8), keyline=(6, 6, 16),
                  kw=sc.m(0.9))


def _hairline(surf, x0, x1, y, color, alpha):
    """A fine warm/steel underline seating the price numerals in the bar."""
    line = pygame.Surface((x1 - x0, sc.m(2)), pygame.SRCALPHA)
    pygame.draw.line(line, (*color, alpha), (0, 0), (x1 - x0 - 1, 0),
                     max(1, sc.m(0.7)))
    surf.blit(line, (x0, y))


def _draw_price(surf, sid, equipped):
    """Right side of the rail: EQUIPPED mint check+label, else the coin +
    affordability-tinted numerals over a matching hairline."""
    if equipped:
        f = sc.font(9)
        label = "EQUIPPED"
        lw = sc._glyph_base(label, f, 0).get_width()
        ckw = sc.m(11)
        gap = sc.m(5)
        # right-align the group to the rail's inner right edge
        x1 = 244
        lx = x1 - lw
        ckx = lx - gap - ckw
        ink = (110, 232, 158)
        pygame.draw.lines(surf, ink, False,
                          [(ckx, RAIL_CY + sc.m(0.5)),
                           (ckx + sc.m(4), RAIL_CY + sc.m(4)),
                           (ckx + ckw, RAIL_CY - sc.m(5))], max(1, sc.m(2.2)))
        sc.plain_text(surf, label, f, (lx + lw // 2, RAIL_CY), ink,
                      shadow_a=0, weight=sc.m(0.8), tracking=sc.m(0.4))
        return

    price = sc._cost(sid)
    text = f"{price:,}"
    affordable = sc.store_data.balance() >= price
    f = sc.font(10)

    coin_rim = (180, 150, 60) if affordable else (120, 108, 78)
    sc.coin_glyph(surf, COIN_CX, RAIL_CY, COIN_R, rim=coin_rim)
    if not affordable:
        tint = pygame.Surface((COIN_R * 2, COIN_R * 2), pygame.SRCALPHA)
        pygame.draw.circle(tint, (70, 74, 84, 170), (COIN_R, COIN_R), COIN_R)
        surf.blit(tint, (COIN_CX - COIN_R, RAIL_CY - COIN_R))

    mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(0.8))
    img = mask.copy()
    if affordable:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((150, 150, 168, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = img.get_rect()
    r.left = NUM_LEFT
    r.centery = RAIL_CY
    # a soft dark shadow so numerals read off the enamel
    sh = mask.copy()
    sh.fill((6, 6, 16, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(130)
    surf.blit(sh, (r.x, r.y + sc.m(1)))
    surf.blit(img, r.topleft)

    hy = RAIL.bottom - sc.m(5)
    if affordable:
        _hairline(surf, COIN_CX - COIN_R + sc.m(1), r.right, hy,
                  (230, 200, 130), 200)
    else:
        _hairline(surf, COIN_CX - COIN_R + sc.m(1), r.right, hy,
                  (120, 126, 142), 200)


def my_state_chip(surf, sid, cx, cy, equipped, secret, h, variant=sc.PRICE_VARIANT):
    """Dark-enamel header rail across the card top: name (left) + price/state
    (right) in one editorial bar. Coordinates are the fixed rail rect, not the
    incoming cx/cy — the bar always banners the top of the card."""
    sc._dark_chip_body(surf, RAIL, RAIL_RAD,
                       [(0.0, (26, 20, 32)), (1.0, (18, 14, 24))],
                       (10, 11, 22), (56, 52, 76), gloss=14, gamma=1.04)
    sc.bevel_rim(surf, RAIL, RAIL_RAD, (120, 88, 28, 235),
                 (230, 200, 130, 220), w=2)
    _draw_name(surf, "???" if secret else sc._name(sid))
    if secret:
        return RAIL
    _draw_price(surf, sid, equipped)
    return RAIL


sc.state_chip = my_state_chip   # monkey-patch BEFORE any draw_card call


def render_card(sid, equipped, affordable):
    """Full 324x200 author-res card with the header rail wired in."""
    _FORCE_BALANCE[0] = 10 ** 9 if affordable else 0
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((sc.CARD_W * sc.SS, ch), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                       ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, equipped=equipped, secret=False,
                 variant=sc.PRICE_VARIANT)
    return surf


def main():
    # force the wallet so affordability is deterministic per card
    sc.store_data.balance = lambda: _FORCE_BALANCE[0]

    out_dir = "/home/user/skybit/docs/store_price_redesign/header-rail"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    specs = [
        ("skin_mummy",   "EPIC affordable",    True),
        ("skin_mummy",   "EPIC locked",        False),
        ("skin_kitsune", "LEGENDARY afford.",  True),
        ("skin_kitsune", "LEGENDARY locked",   False),
    ]

    pad = 26
    gap = 20
    header_h = 44
    card_w, card_h = sc.CARD_W, sc.CARD_H          # displayed at 1x (162x100)

    # Row 1: the four cards at 1x
    row1_w = card_w * 4 + gap * 3
    row1_y = header_h + pad
    lbl_h = 22

    # Row 2: 4x zoom of each top rail (cropped from the author-res render)
    crop = pygame.Rect(18, 6, 240, 40)             # rail neighbourhood
    zoom = 4
    zw, zh = crop.w * zoom // 2, crop.h * zoom // 2  # 480x80 (crop is @2x already)
    # crop is on the SS=2 author buffer, so it is effectively 4x of the 1x card;
    # scaling by 2 more yields an 8x-of-1x inspection view without re-authoring.
    row2_cols = 2
    row2_rows = 2
    row2_y = row1_y + card_h + lbl_h + gap * 2
    row2_w = zw * row2_cols + gap * (row2_cols - 1)

    canvas_w = pad * 2 + max(row1_w, row2_w)
    canvas_h = row2_y + (zh + lbl_h + gap) * row2_rows + pad
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(30, True)
    lf = hud_font(16)

    canvas.blit(hf.render("store price — header-rail  r1", True, (236, 232, 250)),
                (pad, pad // 2 + 2))

    big_cards = []
    x = pad + (max(row1_w, row2_w) - row1_w) // 2
    for sid, label, afford in specs:
        big = render_card(sid, equipped=False, affordable=afford)
        big_cards.append(big)
        card = pygame.transform.smoothscale(big, (card_w, card_h))
        canvas.blit(card, (x, row1_y))
        lbl = lf.render(label, True, (208, 204, 224))
        canvas.blit(lbl, (x + (card_w - lbl.get_width()) // 2, row1_y + card_h + 4))
        x += card_w + gap

    # Row 2 — zoomed rails
    zx0 = pad + (max(row1_w, row2_w) - row2_w) // 2
    for i, (big, (sid, label, afford)) in enumerate(zip(big_cards, specs)):
        col = i % row2_cols
        rrow = i // row2_cols
        zx = zx0 + col * (zw + gap)
        zy = row2_y + rrow * (zh + lbl_h + gap)
        sub = big.subsurface(crop).copy()
        big2 = pygame.transform.scale(sub, (zw, zh))
        # a hairline frame around each crop so the rail edge is readable
        canvas.blit(big2, (zx, zy))
        pygame.draw.rect(canvas, (60, 58, 82), (zx, zy, zw, zh), 1)
        lbl = lf.render(f"4x rail — {label}", True, (196, 192, 214))
        canvas.blit(lbl, (zx + (zw - lbl.get_width()) // 2, zy + zh + 3))

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())

    # ── sanity: the rail body must actually paint (not blank) on the card ──
    probe = render_card("skin_mummy", equipped=False, affordable=True)
    px = probe.get_at((RAIL.centerx, RAIL.centery))
    print("rail centre pixel:", tuple(px))
    assert px[3] > 0, "rail did not render"
    print("sanity OK — rail paints on the card top")


if __name__ == "__main__":
    main()
