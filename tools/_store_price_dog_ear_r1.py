"""Round-1 render sheet for the DOG-EAR store-card price treatment.

Monkey-patches store_cards.price_chip with a bottom-left PEELED CORNER fold:
the price rides a lifted paper flap — a right-triangle whose crease diagonal
runs upper-right — casting a soft shadow onto the card, as if a physical price
sticker were peeling off the corner. The colour FLIPS with affordability: a
warm gold peel when the player can buy it, a cool pewter peel when locked (the
whole flap re-tints, not just the geometry). Renders it in-context on the two
hero cards in both wallet states plus a 4x zoom of the price corner.

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
from game.draw import lerp_color, WHITE
from game.hud import _font as hud_font


# ── peel palette ──────────────────────────────────────────────────────────────
# Affordable = warm gold peel (the canonical Ramp-A gold family the card already
# speaks); locked = cool pewter peel — a MANDATORY colour flip so the state reads
# at a glance, not just a geometry change.
GOLD_STOPS   = sc.GOLD_A_STOPS
GOLD_RIM_HI  = sc.GOLD_A_RIM_BRIGHT      # (255,240,190)
GOLD_RIM_LO  = sc.GOLD_A_RIM_DARK        # (86,50,8)
GOLD_NUM     = (52, 28, 4)               # dark relief numerals bitten into gold
GOLD_NUM_HI  = (255, 236, 182)

PEWTER_STOPS = [(0.0, (156, 160, 176)), (0.5, (120, 124, 142)), (1.0, (78, 82, 100))]
PEWTER_RIM_HI = (214, 218, 230)
PEWTER_RIM_LO = (54, 58, 74)
PEWTER_NUM    = (34, 38, 52)             # cool slate numerals
PEWTER_NUM_HI = (198, 204, 220)

# The peel lifts up-right at a SHALLOW angle: a wide flap rotated a full 22deg
# inflates its bounding box straight up into the item name — this gentler tilt
# keeps the whole fold in the clear bottom strip beneath the name.
THETA = 15
CORNER = (sc.m(7), sc.m(93))             # near the card body bottom-left corner


def _emboss(surf, text, f, center, dark, hi):
    """Numerals bitten into the fold: a faint top highlight lip under a solid
    dark glyph, so the price reads as pressed INTO the paper, not printed on."""
    base = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(0.7))
    hl = base.copy()
    hl.fill((*hi, 130), special_flags=pygame.BLEND_RGBA_MULT)
    ink = base.copy()
    ink.fill((*dark, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = ink.get_rect(center=center)
    surf.blit(hl, (r.x, r.y - sc.m(0.8)))
    surf.blit(ink, r.topleft)


def _widest_price():
    """The fold must fit the LONGEST price in the catalog, not this card's — so
    every card's peel is the same size and the grid stays even."""
    f = sc.font(10)
    best, bw = "0", 0
    for v in cat.CATALOG.values():
        t = f"{v['cost']:,}"
        w = sc._glyph_base(t, f, 0).get_width()
        if w > bw:
            bw, best = w, t
    return best, bw


_WIDEST_TXT, _WIDEST_W = _widest_price()


def _label_strip(text, affordable):
    """The coin + price as a compact horizontal strip (transparent ground). It
    is later laid ALONG the flap's crease so a wide price fits a small corner
    triangle — a horizontal band never would (it pinches under the diagonal)."""
    f = sc.font(10)
    coin_r = sc.m(5.5)
    coin_d = coin_r * 2
    gap = sc.m(4)
    nw = sc._glyph_base(text, f, 0).get_width()
    lw = coin_d + gap + nw
    lh = max(coin_d, f.get_height())
    if affordable:
        num, num_hi, coin_rim, coin_tint = GOLD_NUM, GOLD_NUM_HI, sc.GOLD_A_COIN_RIM, None
    else:
        num, num_hi, coin_rim, coin_tint = PEWTER_NUM, PEWTER_NUM_HI, (110, 116, 134), (86, 92, 112, 150)
    lab = pygame.Surface((lw, lh), pygame.SRCALPHA)
    cy = lh // 2
    sc.coin_glyph(lab, coin_r, cy, coin_r, rim=coin_rim)
    if coin_tint:
        tw = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tw, coin_tint, (coin_r, coin_r), coin_r)
        lab.blit(tw, (0, cy - coin_r))
    _emboss(lab, text, f, (coin_d + gap + nw // 2, cy), num, num_hi)
    return lab


def _widest_label_w(affordable):
    return _label_strip(_WIDEST_TXT, affordable).get_width()


def my_price_chip(surf, cx, cy, text, h, variant=1, affordable=True):
    """DOG-EAR peel: a physical price sticker lifting off the card's bottom-left.
    The sticker carries the price horizontally (the clear strip beneath the item
    name is only wide, not tall — a steep tilt would collide with the name), and
    its bottom-left corner CURLS UP as a dog-ear so it reads as peeling paper.
    The whole sticker re-tints gold (affordable) vs pewter (locked)."""
    lab = _label_strip(text, affordable)
    lw, lh = lab.get_size()
    pad_x = sc.m(9)
    ear = sc.m(9)                              # size of the peeled corner
    plate_w = pad_x + _widest_label_w(affordable) + pad_x
    plate_h = lh + sc.m(4)
    rad = sc.m(3)

    # anchor the plate into the bottom-left corner, snug to the card's bottom
    # edge and left inset, sitting entirely below the item name.
    x0 = sc.m(9)
    y1 = sc.m(93)
    y0 = y1 - plate_h
    plate = pygame.Rect(x0, y0, plate_w, plate_h)

    if affordable:
        stops, rim_hi, rim_lo = GOLD_STOPS, GOLD_RIM_HI, GOLD_RIM_LO
        under = (150, 92, 18)                  # dark gold sticker underside
    else:
        stops, rim_hi, rim_lo = PEWTER_STOPS, PEWTER_RIM_HI, PEWTER_RIM_LO
        under = (78, 82, 100)

    # ── cast shadow first: the sticker floats, so it drops a soft offset shadow;
    # the peeled corner throws a deeper wedge of shade beneath the curl ──
    sh = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 95), plate.move(sc.m(2), sc.m(3)),
                     border_radius=rad)
    pygame.draw.polygon(sh, (0, 0, 0, 150),
                        [(x0, y1 - ear), (x0 + ear + sc.m(3), y1 + sc.m(2)),
                         (x0 - sc.m(2), y1 + sc.m(3))])
    surf.blit(sh, (0, 0))

    # ── plate body: one gold gradient, gloss on the crown, AO on the foot, a
    # dark keyline under a bright top-left bevel — the card's chip finish, but
    # gold/pewter instead of dark enamel ──
    body = sc.vgrad_stops(plate_w, plate_h, rad, stops, 255, gamma=sc.GOLD_A_GAMMA)
    surf.blit(body, plate.topleft)
    sc.top_sheen(surf, plate, rad, plate_h // 2, peak=70)
    sc.contact_shadow(surf, plate, rad, sc.m(3), alpha=70)
    # notch out the peeled corner so the plate reads as missing that triangle
    notch = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(notch, (255, 255, 255, 255),
                        [(x0 - 1, y1 - ear), (x0 + ear, y1 + 1), (x0 - 1, y1 + 1)])
    surf.blit(notch, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    pygame.draw.rect(surf, (*rim_lo, 220), plate, width=max(1, sc.m(1.2)),
                     border_radius=rad)
    sc.bevel_rim(surf, plate, rad, (*rim_lo, 220), (*rim_hi, 225), w=max(1, sc.m(1.2)))

    # ── the peeled dog-ear: a triangle folded UP-LEFT off the bottom-left corner,
    # showing the sticker's darker underside, with a bright catch of light on the
    # curl and a dark crease along the diagonal ──
    P0 = (x0, y1 - ear)                        # crease top on the left edge
    P1 = (x0 + ear, y1)                        # crease foot on the bottom edge
    P2 = (x0 - ear + sc.m(2), y1 - ear + sc.m(3))   # lifted free tip, curled out
    curl = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    ug = sc.vgrad_stops(ear * 2, ear * 2, 0,
                        [(0.0, sc.lerp_color(under, WHITE, 0.30)),
                         (1.0, sc.lerp_color(under, (0, 0, 0), 0.25))], 255)
    umask = pygame.Surface((ear * 2, ear * 2), pygame.SRCALPHA)
    off = (P0[0] - ear, P0[1] - ear)
    pygame.draw.polygon(umask, (255, 255, 255, 255),
                        [(p[0] - off[0], p[1] - off[1]) for p in (P0, P1, P2)])
    ug.blit(umask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    curl.blit(ug, off)
    surf.blit(curl, (0, 0))
    pygame.draw.line(surf, (*rim_lo, 235), P0, P1, max(1, sc.m(1.3)))   # crease
    pygame.draw.line(surf, (*rim_hi, 210), P2, P0, max(1, sc.m(1.0)))   # lit curl
    pygame.draw.line(surf, (*rim_hi, 170), P2, P1, max(1, sc.m(0.8)))

    # ── the price, seated on the plate face, nudged right to clear the ear ──
    surf.blit(lab, lab.get_rect(center=(plate.centerx + ear // 2,
                                        plate.centery)))

    # locked plates carry a tiny padlock at the right end
    if not affordable:
        lx = plate.right - sc.m(11)
        ly = plate.centery - sc.m(2)
        pygame.draw.rect(surf, PEWTER_RIM_LO, (lx, ly, sc.m(6), sc.m(4)),
                         border_radius=max(1, sc.m(1)))
        pygame.draw.arc(surf, PEWTER_RIM_LO,
                        (lx + sc.m(1), ly - sc.m(3), sc.m(4), sc.m(6)),
                        math.radians(20), math.radians(160), max(1, sc.m(1)))
    return plate


sc.price_chip = my_price_chip            # patch BEFORE any draw_card call


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
    out = os.path.join(out_dir, "round_1.png")

    pad, gap = 20, 16
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

    # 4x zoom of the price corner framing the whole peeled sticker.
    cr = pygame.Rect(0, 70, 78, 28)
    zdim = (cr.w * 4, cr.h * 4)
    zoom = pygame.transform.scale(
        render_card_1x("skin_kitsune", True).subsurface(cr).copy(), zdim)
    zoom2 = pygame.transform.scale(
        render_card_1x("skin_kitsune", False).subsurface(cr).copy(), zdim)

    row1_w = cw * 3 + gap * 2
    zw, zh = zoom.get_size()
    row2_w = cw + gap + zw + gap + zw
    canvas_w = pad * 2 + max(row1_w, row2_w)
    row1_y = header_h
    row2_y = row1_y + ch + label_h + gap
    canvas_h = row2_y + max(ch, zh) + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))
    hf = hud_font(26, True)
    lf = hud_font(15)
    canvas.blit(hf.render("store price — dog-ear r1", True, (236, 232, 250)),
                (pad, 8))

    # row 1: three cards
    x = pad
    for card, lbl in cards[:3]:
        canvas.blit(card, (x, row1_y))
        canvas.blit(lf.render(lbl, True, (206, 202, 224)), (x, row1_y + ch + 3))
        x += cw + gap

    # row 2: fourth card + two zoom crops (affordable / locked)
    x = pad
    canvas.blit(cards[3][0], (x, row2_y))
    canvas.blit(lf.render(cards[3][1], True, (206, 202, 224)),
                (x, row2_y + ch + 3))
    x += cw + gap
    canvas.blit(zoom, (x, row2_y))
    canvas.blit(lf.render("4x zoom · affordable", True, (206, 202, 224)),
                (x, row2_y + zh + 3))
    x += zw + gap
    canvas.blit(zoom2, (x, row2_y))
    canvas.blit(lf.render("4x zoom · locked", True, (206, 202, 224)),
                (x, row2_y + zh + 3))

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())

    # ── sanity: warm gold must land in the affordable card's price corner ──
    probe = render_card_1x("skin_kitsune", True)
    hits = 0
    for yy in range(78, 98):
        for xx in range(6, 46):
            r, g, b, a = probe.get_at((xx, yy))
            if a > 40 and r > 150 and g > 110 and b < 130 and r > b:
                hits += 1
    print("gold peel pixels in affordable corner:", hits)
    assert hits > 60, "gold peel missing from bottom-left corner"
    print("sanity OK — gold dog-ear present in the price corner")


if __name__ == "__main__":
    main()
