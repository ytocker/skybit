"""Obsidian coin-slot price chip — round 2 review render.

Round-2 fixes over r1 so the deboss reads at true 1x, not just at zoom:

- Dark-top / light-floor sandwich (top lum ~13, floor lum ~33) so the well
  floor visibly catches sky and the recess reads at gameplay scale.
- The far (bottom-right) inner rim becomes a VISIBLE warm floor-glow line, not
  a whisper hairline — that pressed-below-the-plane glint is what sells depth.
- States separate by VALUE: affordable numerals are gold-leaf (lum ~180),
  locked drop to a dim cool grey (lum ~124) so "can't afford" reads dimmer.
- The locked coin is cooled with a real overlay tint (coin_glyph ignores its
  rim), plus the rim swap + dim well-tint kept as belt-and-suspenders.
- A single cool warm-white highlight on the OUTER top lip frames the slot as
  intentionally milled card-plane metal.
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
# Dark-top / light-floor sandwich: crown lum ~13, floor lum ~33. The lit floor
# is what a real recess does — its base catches the sky the walls occlude — so
# the well reads as pressed even at 1x, not as a flat black pill.
OBS_STOPS = [(0.0, (12, 13, 22)), (1.0, (34, 37, 56))]
FLOOR_GLOW = (180, 150, 90)        # warm floor-glow on the far inner rim
TOP_LIP = (232, 224, 208)          # warm-white card-plane lip catching key light
NUM_GOLD = (228, 196, 120)         # gold-leaf numerals (affordable) — lum ~180
NUM_GREY = (118, 124, 140)         # dim cool numerals (can't-afford) — lum ~124


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


def _floor_glow(surf, rect, radius, alpha):
    """A VISIBLE warm floor-glow on the BOTTOM-RIGHT inner rim — the far wall of
    the recess where the key light grazes the lit floor. Kept to ~1 device px
    but raised to a readable alpha so it registers as depth at 1x, not just at
    zoom."""
    if alpha <= 0:
        return
    lip = pygame.Surface(rect.size, pygame.SRCALPHA)
    inner = pygame.Rect(sc.m(1), sc.m(1), rect.w - sc.m(2), rect.h - sc.m(2))
    pygame.draw.rect(lip, (*FLOOR_GLOW, alpha), inner, width=max(1, sc.m(1)),
                     border_radius=max(1, radius - sc.m(1)))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(rect.w, 0), (rect.w, rect.h), (0, rect.h)])
    lip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lip, rect.topleft)


def _outer_top_lip(surf, rect, radius, alpha):
    """A single cool warm-white highlight on the OUTER top-left rim — the card
    plane edge catching the key light — so the slot reads as an intentional
    milled cut rather than a hole punched in the card."""
    lip = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(lip, (*TOP_LIP, alpha),
                     (0, 0, rect.w, rect.h), width=max(1, sc.m(1)),
                     border_radius=radius)
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(0, 0), (rect.w, 0), (0, rect.h)])
    lip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lip, rect.topleft)


def obsidian_chip(surf, cx, cy, text, h, affordable=True):
    """Debossed dark-well price chip. Shares the price chip's pill silhouette +
    coin cell + numerals layout so the product line still reads, but the body
    recedes: dark-crown/lit-floor fill, top-edge contact shadow, a warm
    floor-glow on the far rim, and an outer milled top lip. Locked state cools
    the coin and dims the numerals so states separate by value, not just hue."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.56 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    radius = h // 2

    # dark-crown / lit-floor fill so the pill reads as a recess catching sky.
    surf.blit(sc.vgrad_stops(r.w, r.h, radius, OBS_STOPS, 255, gamma=1.0),
              r.topleft)
    _inner_top_shadow(surf, r, radius, depth=sc.m(4), alpha=150)
    _floor_glow(surf, r, radius, alpha=110 if affordable else 60)
    _outer_top_lip(surf, r, radius, alpha=46)

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
        # coin_glyph blits the real game coin face and ignores its rim arg, so
        # cool the LOCKED coin with an explicit overlay: a cool tint desaturates
        # the warm face, and a dark well-tint dims it into the recess.
        cool = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(cool, (60, 70, 90, 160), (coin_d // 2, coin_d // 2),
                           coin_d // 2)
        surf.blit(cool, (ccx - coin_d // 2, cy - coin_d // 2))
        dim = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(dim, (12, 14, 24, 110), (coin_d // 2, coin_d // 2),
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
def draw_card_with_chip(surf, sid, rect, affordable=True):
    """The full CONSTELLATION card body (identical to sc.draw_card) with the
    state_chip call replaced by the obsidian coin-slot chip."""
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
    # SWAP: obsidian coin-slot chip in place of state_chip.
    price = sc._cost(sid)
    obsidian_chip(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY, f"{price:,}",
                  sc.m(20), affordable=affordable)


# ── chip strip tile (chip on a patch of card plane so the deboss reads) ─────────
def render_chip_tile(text, affordable):
    """Render one chip centred on a patch of the card body gradient, so the
    'recede below the plane' read has a plane to recede below."""
    h = sc.m(20)
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.56 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    margin = sc.m(16)
    tw, th = w + margin * 2, h + margin * 2
    tile = pygame.Surface((tw, th), pygame.SRCALPHA)
    tile.blit(sc.vgrad(tw, th, sc.m(6), sc.CARD_T, sc.CARD_B, 255, gamma=1.15),
              (0, 0))
    obsidian_chip(tile, tw // 2, th // 2, text, h, affordable=affordable)
    return tile


def one_x_tile(text, affordable):
    """The chip tile downscaled to the live (1x) pixel density — the exact size
    the player sees in the store — so legibility at gameplay scale is visible
    without any zoom."""
    ss_tile = render_chip_tile(text, affordable)
    return pygame.transform.smoothscale(
        ss_tile, (ss_tile.get_width() // sc.SS, ss_tile.get_height() // sc.SS))


# ── compose the review sheet ───────────────────────────────────────────────────
def main():
    SID = "skin_mummy"
    price_text = f"{sc._cost(SID):,}"

    # top row: two full cards at SS scale (no downscale) so the chip's fine rim
    # survives — affordable on the left, can't-afford on the right.
    card_w, card_h = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS

    def full_card(affordable):
        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        crect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                            card_w - 2 * sc.m(sc._INSET),
                            card_h - 2 * sc.m(sc._INSET))
        draw_card_with_chip(card, SID, crect, affordable=affordable)
        return card

    card_aff = full_card(True)
    card_lock = full_card(False)

    # middle: 4x zoom of the in-game (1x) chip so the whisper rim + floor-glow
    # can be inspected pixel-for-pixel.
    ZOOM = 4
    tiles = []
    for aff in (True, False):
        one_x = one_x_tile(price_text, aff)
        big = pygame.transform.scale(
            one_x, (one_x.get_width() * ZOOM, one_x.get_height() * ZOOM))
        tiles.append(big)

    # bottom: TRUE 1x swatches (no zoom) — the exact gameplay size — including a
    # wide "14,500" case to confirm the comma survives inside the pill width.
    swatches = [one_x_tile(price_text, True), one_x_tile(price_text, False),
                one_x_tile("14,500", True)]

    gap = 26
    strip_w = tiles[0].get_width() + gap + tiles[1].get_width()
    strip_h = tiles[0].get_height()

    sw_gap = 30
    sw_w = sum(s.get_width() for s in swatches) + sw_gap * (len(swatches) - 1)
    sw_h = max(s.get_height() for s in swatches)

    MARGIN = 20
    HEADER = 44
    FOOTER = 16
    LABEL_H = 22
    cards_w = card_w * 2 + gap
    inner_w = max(cards_w, strip_w, sw_w)
    W = inner_w + MARGIN * 2
    H = (HEADER + card_h + LABEL_H + 24 + strip_h + LABEL_H + 26
         + sw_h + LABEL_H + FOOTER + MARGIN * 2)

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    title_f = hud_font(23, True)
    sub_f = hud_font(15, False)
    lbl_f = hud_font(16, True)

    t = title_f.render(f"v5 obsidian-coin-slot r2 — {SID} — recess + state fix",
                       True, (232, 224, 208))
    canvas.blit(t, (MARGIN, MARGIN + 4))
    s = sub_f.render("debossed dark-well pill  ·  dark-crown/lit-floor  ·  "
                     "warm floor-glow  ·  value-separated states",
                     True, (150, 150, 176))
    canvas.blit(s, (MARGIN, MARGIN + 4 + t.get_height() + 2))

    # ── two full cards ────────────────────────────────────────────────────────
    y = MARGIN + HEADER
    x_cards = (W - cards_w) // 2
    canvas.blit(card_aff, (x_cards, y))
    canvas.blit(card_lock, (x_cards + card_w + gap, y))
    y += card_h + 2
    ca = lbl_f.render("AFFORDABLE", True, (228, 196, 120))
    cl = lbl_f.render("CAN'T AFFORD", True, (150, 158, 178))
    canvas.blit(ca, (x_cards + (card_w - ca.get_width()) // 2, y))
    canvas.blit(cl, (x_cards + card_w + gap + (card_w - cl.get_width()) // 2, y))
    y += LABEL_H + 24

    # ── 4x zoom strip ─────────────────────────────────────────────────────────
    x0 = (W - strip_w) // 2
    canvas.blit(tiles[0], (x0, y))
    canvas.blit(tiles[1], (x0 + tiles[0].get_width() + gap, y))
    y += strip_h + 4
    z = lbl_f.render("4x ZOOM — rim + floor-glow detail", True, (176, 176, 200))
    canvas.blit(z, ((W - z.get_width()) // 2, y))
    y += LABEL_H + 26

    # ── true 1x swatches ──────────────────────────────────────────────────────
    x1 = (W - sw_w) // 2
    xs = x1
    sw_labels = ["1x  1,100 ok", "1x  1,100 locked", "1x  14,500 ok"]
    sw_cols = [(228, 196, 120), (150, 158, 178), (228, 196, 120)]
    for sw, lab, col in zip(swatches, sw_labels, sw_cols):
        sy = y + (sw_h - sw.get_height()) // 2
        canvas.blit(sw, (xs, sy))
        lt = lbl_f.render(lab, True, col)
        canvas.blit(lt, (xs + (sw.get_width() - lt.get_width()) // 2,
                         y + sw_h + 2))
        xs += sw.get_width() + sw_gap
    ttl = lbl_f.render("TRUE 1x — gameplay-scale legibility", True, (176, 176, 200))
    canvas.blit(ttl, ((W - ttl.get_width()) // 2, y + sw_h + LABEL_H))

    out = os.path.join(os.path.dirname(__file__), "..", "docs",
                       "store_card_v5_price_chip", "obsidian-coin-slot",
                       "round_2.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
