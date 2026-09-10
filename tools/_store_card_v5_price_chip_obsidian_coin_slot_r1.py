"""Obsidian coin-slot price chip — round 1 review render.

Explores a DEBOSSED price chip: instead of the shipped chip's raised, gold,
glossy pill, this one recedes BELOW the card plane like a milled coin slot.
The read is inverted — a dark well, a top-edge contact shadow, and a single
whisper-thin gold catch-lip on the far (bottom-right) rim where a pressed
recess would catch the top-left key light.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.hud import _font as hud_font


# ── obsidian coin-slot chip ────────────────────────────────────────────────────
# Debossed-well palette: fill is INVERTED (darker at the top) so the pill reads
# as a recess catching sky, not a lit dome. Gold is de-saturated to a matte
# leaf so nothing glows out of the well.
OBS_STOPS = [(0.0, (14, 15, 26)), (1.0, (26, 28, 44))]
CATCH_LIP = (150, 120, 60)         # de-saturated gold rim glint, whisper-level
NUM_GOLD = (228, 196, 120)         # matte gold-leaf numerals (affordable)
NUM_GREY = (150, 158, 178)         # cool grey numerals (can't-afford)


def _inner_top_shadow(surf, rect, radius, depth, alpha):
    """Ambient-occlusion INTO the well along the TOP-LEFT inner edge — the wall
    the top-left key light can't reach, which sells the pill as pressed below
    the card plane rather than floating on it."""
    ao = pygame.Surface(rect.size, pygame.SRCALPHA)
    for i in range(depth):
        a = int(alpha * (1 - i / depth) ** 1.4)
        pygame.draw.rect(ao, (0, 0, 0, a),
                         (i, i, rect.w - 2 * i, rect.h - 2 * i),
                         width=max(1, sc.m(0.9)), border_radius=max(1, radius - i))
    # keep only the top-left inner edge (the shaded lip of the recess)
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(0, 0), (rect.w, 0), (0, rect.h)])
    ao.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(ao, rect.topleft)


def _catch_lip(surf, rect, radius, alpha):
    """A single hair-thin gold catch-lip on the BOTTOM-RIGHT inner rim — the far
    wall of the recess that the key light grazes. Kept to ~1 device px so it
    stays a whisper, never a full bevel."""
    if alpha <= 0:
        return
    lip = pygame.Surface(rect.size, pygame.SRCALPHA)
    inner = pygame.Rect(sc.m(1), sc.m(1), rect.w - sc.m(2), rect.h - sc.m(2))
    pygame.draw.rect(lip, (*CATCH_LIP, alpha), inner, width=1,
                     border_radius=max(1, radius - sc.m(1)))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(rect.w, 0), (rect.w, rect.h), (0, rect.h)])
    lip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lip, rect.topleft)


def obsidian_chip(surf, cx, cy, text, h, affordable=True):
    """Debossed dark-well price chip. Shares the price chip's pill silhouette +
    coin cell + numerals layout so the product line still reads, but the body
    recedes: inverted dark fill, no gloss, top-edge contact shadow, and one
    whisper gold catch-lip on the far rim (dropped to invisible when locked)."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    radius = h // 2

    # INVERTED fill — darker at the crown, no gloss sweep — so it reads as a
    # recess, not a dome.
    surf.blit(sc.vgrad_stops(r.w, r.h, radius, OBS_STOPS, 255, gamma=1.0),
              r.topleft)
    _inner_top_shadow(surf, r, radius, depth=sc.m(4), alpha=150)
    _catch_lip(surf, r, radius, alpha=60 if affordable else 0)

    # coin nestled in the well: a soft dark seat ring hugs it so it settles into
    # the recess instead of sitting on top.
    x = r.x + pad
    ccx = x + coin_d // 2
    seat = pygame.Surface((coin_d + sc.m(6), coin_d + sc.m(6)), pygame.SRCALPHA)
    scc = (coin_d + sc.m(6)) // 2
    pygame.draw.circle(seat, (0, 0, 0, 120), (scc, scc), coin_d // 2 + sc.m(2))
    surf.blit(seat, (ccx - scc, cy - scc))
    sc.coin_glyph(surf, ccx, cy, coin_d // 2,
                  rim=sc.GOLD_A_COIN_RIM if affordable else (78, 84, 104))
    if not affordable:
        # dim the coin into the cool locked state via a dark well-tint.
        dim = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(dim, (12, 14, 24, 130), (coin_d // 2, coin_d // 2),
                           coin_d // 2)
        surf.blit(dim, (ccx - coin_d // 2, cy - coin_d // 2))

    x += coin_d + gapc
    sc.plain_text(surf, text, f, (x + nw // 2, cy),
                  NUM_GOLD if affordable else NUM_GREY, shadow_a=0,
                  weight=sc.m(1.0),
                  keyline=None if affordable else (20, 24, 38),
                  kw=sc.m(0.7))
    return r


# ── card body copied from sc.draw_card, chip call swapped ──────────────────────
def draw_card_with_chip(surf, sid, rect):
    """The full CONSTELLATION card body (identical to sc.draw_card) with the
    state_chip call replaced by the obsidian coin-slot chip."""
    equipped, secret = False, False
    pal = sc.RARITY[sc._rarity(sid)]
    rad = sc.m(sc.CARD_RAD)
    sc.drop_shadow(surf, rect, rad, blur=sc.m(8), alpha=160, dy=sc.m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, sc.m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, sc.m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, sc.m(2)),
                     border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235),
                 w=max(1, sc.m(2.0)))
    tray = rect.inflate(-sc.m(7), -sc.m(7))
    trad = rad - sc.m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(sc.m(2), sc.m(2)),
                     width=max(1, sc.m(1)), border_radius=trad + sc.m(1))
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray, width=max(1, sc.m(1)),
                     border_radius=trad)

    cx, cy = rect.centerx, rect.y + sc.m(sc.CY_DISC) + sc._DOME_DY
    sc.soft_glow(surf, cx, cy, sc._DOME_R + sc.m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, sc._DOME_R, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    name = sc._name(sid)
    sc.cabochon_glass(surf, cx, cy, sc._DOME_R, tint=pal["gem"])
    sc.blit_thumb(surf, sid, cx, cy - sc._ITEM_DY, sc._BOX_PX)

    sc.facet_gem(surf, rect.right - sc.m(19), rect.y + sc.m(19), sc.m(sc.GEM_R + 3),
                 pal["gem"], pal["deep"], mystery=False)
    tier_word = sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + sc.m(55) - sc._RIBN_DY,
                       rect.w - sc.m(34), pal)
    sc._name_on(surf, name, cx, rect.y + sc.m(70), rect.w - sc.m(26))
    # SWAP: obsidian coin-slot chip in place of state_chip. Force affordable so
    # the card presents the hero state; the strip below shows both states.
    price = sc._cost(sid)
    obsidian_chip(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY, f"{price:,}",
                  sc.m(20), affordable=True)


# ── chip strip tile (chip on a patch of card plane so the deboss reads) ─────────
def render_chip_tile(text, affordable):
    """Render one chip centred on a patch of the card body gradient, so the
    'recede below the plane' read has a plane to recede below."""
    h = sc.m(20)
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    margin = sc.m(16)
    tw, th = w + margin * 2, h + margin * 2
    tile = pygame.Surface((tw, th), pygame.SRCALPHA)
    tile.blit(sc.vgrad(tw, th, sc.m(6), sc.CARD_T, sc.CARD_B, 255, gamma=1.15),
              (0, 0))
    obsidian_chip(tile, tw // 2, th // 2, text, h, affordable=affordable)
    return tile


# ── compose the review sheet ───────────────────────────────────────────────────
def main():
    price_text = f"{sc._cost('skin_mummy'):,}"

    # top: full card at SS scale (no downscale) so the chip's fine rim survives.
    card_w, card_h = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS
    card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    crect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                        card_w - 2 * sc.m(sc._INSET), card_h - 2 * sc.m(sc._INSET))
    draw_card_with_chip(card, "skin_mummy", crect)

    # bottom: 4x zoom of the in-game (1x) chip — render the SS tile, downscale to
    # the live pixel density, then blow up 4x to inspect the whisper rim.
    ZOOM = 4
    tiles = []
    for aff in (True, False):
        ss_tile = render_chip_tile(price_text, aff)
        one_x = pygame.transform.smoothscale(
            ss_tile, (ss_tile.get_width() // sc.SS, ss_tile.get_height() // sc.SS))
        big = pygame.transform.scale(
            one_x, (one_x.get_width() * ZOOM, one_x.get_height() * ZOOM))
        tiles.append(big)

    gap = 26
    strip_w = tiles[0].get_width() + gap + tiles[1].get_width()
    strip_h = tiles[0].get_height()

    MARGIN = 20
    HEADER = 44
    FOOTER = 36
    LABEL_H = 22
    inner_w = max(card_w, strip_w)
    W = inner_w + MARGIN * 2
    H = HEADER + card_h + 28 + strip_h + LABEL_H + FOOTER + MARGIN * 2

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    title_f = hud_font(24, True)
    sub_f = hud_font(15, False)
    lbl_f = hud_font(16, True)

    t = title_f.render("OBSIDIAN COIN-SLOT price chip", True, (232, 224, 208))
    canvas.blit(t, (MARGIN, MARGIN + 4))
    s = sub_f.render("round 1  ·  debossed dark-well pill  ·  skin_mummy EPIC",
                     True, (150, 150, 176))
    canvas.blit(s, (MARGIN, MARGIN + 4 + t.get_height() + 2))

    y = MARGIN + HEADER
    canvas.blit(card, ((W - card_w) // 2, y))
    y += card_h + 28

    x0 = (W - strip_w) // 2
    canvas.blit(tiles[0], (x0, y))
    canvas.blit(tiles[1], (x0 + tiles[0].get_width() + gap, y))
    y += strip_h + 4

    la = lbl_f.render("AFFORDABLE", True, (228, 196, 120))
    lb = lbl_f.render("CAN'T AFFORD", True, (150, 158, 178))
    canvas.blit(la, (x0 + (tiles[0].get_width() - la.get_width()) // 2, y))
    canvas.blit(lb, (x0 + tiles[0].get_width() + gap
                     + (tiles[1].get_width() - lb.get_width()) // 2, y))

    out = os.path.join(os.path.dirname(__file__), "..", "docs",
                       "store_card_v5_price_chip", "obsidian-coin-slot",
                       "round_1.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
