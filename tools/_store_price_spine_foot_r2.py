"""Round-2 render sheet for the `spine-foot` store-card price redesign.

Round-1 established the read: a gold enamel SPINE down the left gutter feeding a
compact upright FOOT CHIP that carries the price left-to-right, with a top-right
crest gem for diagonal balance. This pass folds in the art-director notes:

  * the punched hole is gone — at 1x it collapsed to a damage-like speck; a clean
    enamel rule reads better;
  * the spine is wider (11 px @2x) for more presence at 1x;
  * the spine's foot FLARES into the chip's top-left so the two read as ONE
    anchored price tag rather than two stacked parts (the r1 8 px dead gutter);
  * the LOCKED state stops leaning on hue alone — a much darker body, a low-value
    steel rim, a hand-drawn PADLOCK glyph in place of the coin (a coin means "you
    can afford this"; a lock is the honest not-yet signal), and dimmer slate
    numerals;
  * affordable numerals ride the coin-metal sovereign ramp for contrast.

Renders four v5 cards (EPIC + LEGENDARY x afford/locked) plus 4x zoomed crops of
the bottom-left price corner. Review-only tooling — never imported by the game.
"""
import math
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
from game.draw import NEAR_BLACK
from game.hud import _font as hud_font


# ── locked-state padlock glyph ────────────────────────────────────────────────
# A coin says "affordable"; when the price is out of reach that same coin lies.
# Drawn by hand so it matches the enamel scale: a rounded steel body carrying a
# dark keyhole, capped by an inverted-U shackle (top arc + two legs seated into
# the body). Steel-toned so it belongs to the locked chip's cool palette.
def _padlock(surf, cx, cy, body_col, rim_col, shadow_col):
    bw, bh = sc.m(6.5), sc.m(5.0)
    body = pygame.Rect(cx - bw // 2, cy - sc.m(0.5), bw, bh)

    sr = sc.m(2.1)                                  # shackle radius
    leg = sc.m(2.0)                                 # straight legs under the arc
    lx = cx - sr
    rx = cx + sr
    arc_top = body.top - leg - sr

    # shackle: top arc over two vertical legs seating into the body
    pygame.draw.arc(surf, rim_col,
                    (cx - sr, arc_top, sr * 2, sr * 2),
                    0.0, math.pi, max(2, sc.m(1.6)))
    for x in (lx, rx):
        pygame.draw.line(surf, rim_col, (x, arc_top + sr - sc.m(0.4)),
                         (x, body.top + sc.m(0.6)), max(2, sc.m(1.4)))

    # body: rounded steel block with a lit top-left rim + dark seat keyline
    pygame.draw.rect(surf, shadow_col, body.move(0, sc.m(0.8)),
                     border_radius=sc.m(1.6))
    pygame.draw.rect(surf, body_col, body, border_radius=sc.m(1.6))
    pygame.draw.line(surf, rim_col, (body.left + sc.m(1), body.top + sc.m(0.8)),
                     (body.right - sc.m(1), body.top + sc.m(0.8)), max(1, sc.m(0.8)))
    pygame.draw.rect(surf, shadow_col, body, width=max(1, sc.m(0.8)),
                     border_radius=sc.m(1.6))
    # keyhole
    pygame.draw.circle(surf, shadow_col, (cx, body.centery), max(1, sc.m(0.9)))


# ── spine-foot price chip ─────────────────────────────────────────────────────
# Device-px coords in the 324x200 (2x) card buffer, authored directly (NOT via
# m()) because the brief fixes them at the buffer scale. cx/cy are ignored: this
# chip anchors to the card's left gutter, not the caller's centre hint.
_SPINE = pygame.Rect(19, 50, 11, 109)     # x:19-30, bottom y=159 (into the chip)
_FOOT = pygame.Rect(30, 158, 88, 22)      # top y=158 => overlaps the spine foot
_FOOT_RAD = 11


def my_price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    # (a) DECORATIVE SPINE — gold enamel bar, identical in both states so the
    # card's left edge always carries the same jewellery cue; only the foot chip
    # flips with affordability. No punched hole: at 1x it read as damage, and the
    # enamel bar carries the read cleanly as a plain rule.
    spine = _SPINE
    surf.blit(sc.vgrad_stops(spine.w, spine.h, 4, sc.GOLD_A_STOPS,
                             255, gamma=sc.GOLD_A_GAMMA), spine.topleft)

    # (b) FOOT FLARE — the spine's base widens down-right into the chip's
    # top-left corner so the vertical rule and the horizontal price plate read as
    # ONE anchored tag (r1 left an 8 px dead gutter between them). Drawn as a gold
    # gusset UNDER the chip; the chip's rounded corner seats onto its base.
    flare = [(spine.x, 144), (spine.right, 144),
             (spine.right + 18, _FOOT.top), (spine.right, _FOOT.top + 1),
             (spine.x, _FOOT.top + 1)]
    gcol = sc.lerp_stops(sc.GOLD_A_STOPS, 0.62)
    pygame.draw.polygon(surf, gcol, flare)
    pygame.draw.polygon(surf, sc.GOLD_A_RIM_DARK, flare, width=1)

    # spine rim + a bright top-left kiss so the enamel bar reads domed, not flat
    pygame.draw.rect(surf, sc.GOLD_A_RIM_DARK, spine, width=1, border_radius=4)
    pygame.draw.line(surf, (*sc.GOLD_A_RIM_BRIGHT, 160),
                     (spine.x + 2, spine.y + 6), (spine.x + 2, spine.bottom - 8), 1)

    # (c) UPRIGHT FOOT CHIP — the price read, standard left-to-right.
    r = _FOOT
    rad = _FOOT_RAD
    if affordable:
        # dark warm enamel + gold struck rim + the real coin + coin-metal numerals
        sc._dark_chip_body(surf, r, rad,
                           [(0.0, (26, 20, 32)), (1.0, (18, 14, 24))],
                           (10, 11, 22), (56, 52, 76), gloss=14, gamma=1.04)
        sc.bevel_rim(surf, r, rad, (120, 88, 28, 235), (230, 200, 130), w=2)
        sc.coin_glyph(surf, 46, 169, 8)
    else:
        # much DARKER body (bottoms out near the card ground), a low-value steel
        # rim, and a padlock where the coin would be — luminance carries the
        # locked read, not hue alone.
        sc._dark_chip_body(surf, r, rad,
                           [(0.0, (16, 16, 26)), (1.0, (10, 11, 22))],
                           (8, 9, 18), (40, 44, 58), gloss=10, gamma=1.04)
        sc.bevel_rim(surf, r, rad, (40, 44, 56), (100, 106, 124), w=2)
        _padlock(surf, 46, 168, (118, 124, 142), (176, 182, 200), (26, 28, 40))

    # price numerals, left-aligned from x=60, vertically centred on the glyph.
    f = sc.font(9)
    base = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
    if affordable:
        grad = sc.vgrad_stops(base.get_width(), base.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img = base.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img = base.copy()
        img.fill((104, 108, 128, 255), special_flags=pygame.BLEND_RGBA_MULT)
    # a crisp dark backing stamp lifts the numerals off the near-black body
    sh = base.copy()
    sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(150)
    rct = img.get_rect()
    rct.midleft = (60, 169)
    surf.blit(sh, (rct.x, rct.y + 1))
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
    """Author one card at SS, controlling affordability via the wallet the price
    chip reads. Returns the 324x200 SS surface (kept for the crop)."""
    store_data.balance = (lambda: 10 ** 9) if affordable else (lambda: 0)
    big = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, CARD_W_SS - 2 * inset, CARD_H_SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False)
    return big


def _probe(bigs):
    """Pixel sanity per the round-2 brief: the affordable foot chip carries warm
    gold, the locked chip a cool dark slate, and the spine foot connects to the
    chip with no meaningful gap."""
    afford, locked = bigs[0], bigs[1]

    # affordable: the warmest pixel (max r-b) across the foot-chip band should be
    # gold — probing max-r alone catches a white specular, not the gold rim.
    best = (0, 0, 0)
    best_warm = -999
    for x in range(30, 118):
        for y in range(156, 182):
            r, g, b, _ = afford.get_at((x, y))
            if r > 150 and (r - b) > best_warm:
                best_warm = r - b
                best = (r, g, b)
    ar, ag, ab = best
    print(f"  afford chip warm-max rgb=({ar},{ag},{ab}) "
          f"r>150={ar > 150} r>b+20={ar > ab + 20}")

    # locked: body centre should be a cool dark slate (b>r, low luminance)
    lr, lg, lb, _ = locked.get_at((74, 169))
    lum = 0.299 * lr + 0.587 * lg + 0.114 * lb
    print(f"  locked chip body rgb=({lr},{lg},{lb}) b>r={lb > lr} "
          f"lum={lum:.1f}<100={lum < 100}")

    # gap: lowest gold pixel in the spine/flare column vs the chip top (158).
    low = 0
    for y in range(140, 165):
        for x in range(19, 40):
            r, g, b, a = afford.get_at((x, y))
            if a > 40 and r > 130 and r > b + 15:
                low = max(low, y)
    gap = _FOOT.top - low
    print(f"  spine-foot lowest gold y={low} chip top={_FOOT.top} "
          f"gap={gap}px (<=2={gap <= 2})")


def main():
    out_dir = "/home/user/skybit/docs/store_price_redesign/spine-foot"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

    pad = 28
    gap = 22
    header_h = 42
    label_h = 22

    bigs = [_draw_big(sid, aff) for sid, _, aff in STATES]
    _probe(bigs)

    cards = [pygame.transform.smoothscale(b, (sc.CARD_W, sc.CARD_H)) for b in bigs]
    cw, chh = sc.CARD_W, sc.CARD_H

    row1_y = header_h + pad
    row1_w = cw * 4 + gap * 3

    # 4x zoom crops of the bottom-left price corner (60x40 source -> 240x160) so
    # the flared spine->chip joint + the padlock resolve under magnification.
    crop = pygame.Rect(12, 140, 60, 40)
    zoom = 4
    zsz = (crop.w * zoom, crop.h * zoom)
    crops = [(bigs[0], "AFFORD  corner zoom 4x"), (bigs[1], "LOCKED  corner zoom 4x")]
    row2_y = row1_y + chh + label_h + gap * 2
    row2_w = zsz[0] * 2 + gap

    canvas_w = pad * 2 + max(row1_w, row2_w)
    canvas_h = row2_y + zsz[1] + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(28, True)
    lf = hud_font(15)

    canvas.blit(hf.render("store price — spine-foot r2", True, (236, 232, 250)),
                (pad, pad // 2 + 2))

    # Row 1 — the four cards, labelled.
    x = pad + (max(row1_w, row2_w) - row1_w) // 2
    for card, (_, label, _aff) in zip(cards, STATES):
        canvas.blit(card, (x, row1_y))
        lbl = lf.render(label, True, (206, 202, 224))
        canvas.blit(lbl, (x + (cw - lbl.get_width()) // 2, row1_y + chh + 5))
        x += cw + gap

    # Row 2 — 4x zoomed corner crops.
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
    print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")


if __name__ == "__main__":
    main()
