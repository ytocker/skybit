"""Ember-crown price chip — round 1 review render (Levers C + P).

The concept inverts the price chip's usual bright-gold BEFORE state: the body
goes near-black so warmth is a scarce, precious signal rather than the whole
surface. Warmth lives ONLY in a restrained halo ring behind the body and never
in the numerals, which stay cream so the "value in cold metal" read holds.

  - Body: near-black two-stop fill on the canonical chip finish (double rim,
    one gloss sweep). The rim's bright top-left bevel is the only warm gold on
    the pill itself — an amber-lit crown edge on a dark coin.
  - Halo: a soft additive glow drawn BEHIND the body so the body occludes the
    centre and only the corona reads. Kept to peak_alpha 64 so it glows without
    washing the dark body out.
  - Numerals: cream / near-white with a dark keyline for legibility on the
    near-black ground — no amber in the type.
  - Can't-afford: the halo is killed entirely (warmth gone = locked) and the
    rim bevel + numerals cool to dim slate, so state separates by warmth AND
    value, not hue alone.
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

SID = "skin_mummy"

# Near-black body stops shared by both states so the pill silhouette is stable;
# only the halo + rim + numeral warmth change with affordability.
EMBER_STOPS = [(0.0, (18, 18, 30)), (1.0, (10, 10, 20))]
EMBER_RIM_DARK = (8, 8, 16)
# rim_bright is the RGB of the lit bevel; chip_body_stops appends the 235 alpha
# before handing it to bevel_rim, so the composed edge is (255,196,110,235).
EMBER_RIM_WARM = (255, 196, 110)
EMBER_RIM_COOL = (168, 176, 198)         # can't-afford: cool-dim milled edge
EMBER_NUM_WARM = (246, 244, 232)         # cream numerals — no amber in the type
EMBER_NUM_COOL = (150, 158, 178)         # locked: dim cool grey (value delta)
EMBER_NUM_KEY = (12, 12, 22)             # dark keyline keeps cream legible
HALO_COL = (255, 168, 58)                # scarce warmth: a legendary-amber corona


def ember_chip(surf, cx, cy, text, h, affordable=True):
    """The ember-crown price chip: a near-black pill whose only warmth is a
    restrained amber halo behind it and its lit crown-edge bevel, with cream
    numerals. Locked kills the halo and cools the edge + type so warmth reads as
    the affordance."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)                                   # clear gap: coin cell -> digits
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    radius = h // 2                                  # pill silhouette

    # WARMTH FIRST: the halo is drawn BEFORE the body so the near-black pill
    # occludes the corona's centre and only the ring bleeds past the edge. Killed
    # entirely when locked so absence-of-warmth is the can't-afford signal.
    if affordable:
        sc.soft_glow(surf, cx, cy, int(h * 0.95), HALO_COL, peak_alpha=64,
                     layers=10)

    rim_bright = EMBER_RIM_WARM if affordable else EMBER_RIM_COOL
    sc.chip_body_stops(surf, r, radius, EMBER_STOPS, EMBER_RIM_DARK, rim_bright,
                       gloss=20, gamma=1.05)

    x = r.x + pad
    ccx = x + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2, rim=sc.GOLD_A_COIN_RIM)
    if not affordable:
        # coin_glyph blits the real game coin face and ignores its rim arg, so
        # cool the LOCKED coin with an explicit slate overlay to match the cold
        # body — the warm coin would otherwise contradict the locked read.
        cool = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(cool, (60, 70, 90, 160), (coin_d // 2, coin_d // 2),
                           coin_d // 2)
        surf.blit(cool, (ccx - coin_d // 2, cy - coin_d // 2))

    x += coin_d + gapc
    num_col = EMBER_NUM_WARM if affordable else EMBER_NUM_COOL
    sc.plain_text(surf, text, f, (x + nw // 2, cy), num_col, shadow_a=0,
                  weight=sc.m(1.0), keyline=EMBER_NUM_KEY, kw=sc.m(0.7))
    return r


# ── card body copied from sc.draw_card, chip call swapped ──────────────────────
def draw_card_with_chip(surf, sid, rect, affordable=True):
    """sc.draw_card verbatim (non-secret, not equipped) with the state_chip call
    replaced by the ember-crown chip, so the chip is judged in its real frame."""
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

    sc.facet_gem(surf, rect.right - sc.m(19), rect.y + sc.m(19),
                 sc.m(sc.GEM_R + 3), pal["gem"], pal["deep"], mystery=False)
    tier_word = sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + sc.m(55) - sc._RIBN_DY,
                       rect.w - sc.m(34), pal)
    sc._name_on(surf, name, cx, rect.y + sc.m(70), rect.w - sc.m(26))
    # SWAP: ember-crown price chip in place of state_chip.
    price = sc._cost(sid)
    ember_chip(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY, f"{price:,}",
               sc.m(20), affordable=affordable)


# ── chip on a patch of card plane so the halo has a body to bleed over ─────────
def render_chip_tile(text, affordable):
    """One chip centred on a patch of the card-body gradient. The tile is opaque
    (alpha 255) so the additive halo composites correctly and reads exactly as it
    will on the live dark card body."""
    h = sc.m(20)
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    margin = sc.m(18)
    tw, th = w + margin * 2, h + margin * 2
    tile = pygame.Surface((tw, th))
    tile.blit(sc.vgrad(tw, th, sc.m(6), sc.CARD_T, sc.CARD_B, 255, gamma=1.15),
              (0, 0))
    ember_chip(tile, tw // 2, th // 2, text, h, affordable=affordable)
    return tile


def one_x_tile(text, affordable):
    """The chip tile at the live (1x) pixel density — the exact size the player
    sees in the store — so legibility at gameplay scale is visible with no zoom."""
    ss_tile = render_chip_tile(text, affordable)
    return pygame.transform.smoothscale(
        ss_tile, (ss_tile.get_width() // sc.SS, ss_tile.get_height() // sc.SS))


# ── compose the review sheet ───────────────────────────────────────────────────
def main():
    price_text = f"{sc._cost(SID):,}"

    # two hero cards at SS scale (324x200): affordable + can't-afford.
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

    # 4x zoom of the in-game (1x) chip so the halo bleed + crown edge + cream
    # keyline can be inspected pixel-for-pixel.
    ZOOM = 4
    tiles = []
    for aff in (True, False):
        one_x = one_x_tile(price_text, aff)
        big = pygame.transform.scale(
            one_x, (one_x.get_width() * ZOOM, one_x.get_height() * ZOOM))
        tiles.append(big)

    # TRUE 1x swatches (no zoom) — exact gameplay size, plus a wide "14,500" case
    # to confirm the comma survives inside the pill width.
    swatches = [one_x_tile(price_text, True), one_x_tile(price_text, False),
                one_x_tile("14,500", True)]

    GAP = 26
    strip_w = tiles[0].get_width() + GAP + tiles[1].get_width()
    strip_h = tiles[0].get_height()

    sw_gap = 30
    sw_w = sum(s.get_width() for s in swatches) + sw_gap * (len(swatches) - 1)
    sw_h = max(s.get_height() for s in swatches)

    MARGIN = 20
    HDR_H = 44
    FOOTER = 16
    LABEL_H = 22
    cards_w = card_w * 2 + GAP
    inner_w = max(cards_w, strip_w, sw_w)
    W = inner_w + MARGIN * 2
    H = (HDR_H + card_h + LABEL_H + 24 + strip_h + LABEL_H + 26
         + sw_h + LABEL_H + FOOTER + MARGIN * 2)

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    title_f = hud_font(23, True)
    sub_f = hud_font(15, False)
    lbl_f = hud_font(16, True)

    t = title_f.render(f"v5 ember-crown r1 — {SID} EPIC — warmth = scarcity "
                       "(Levers C + P)", True, (246, 244, 232))
    canvas.blit(t, (MARGIN, MARGIN + 4))
    s = sub_f.render("near-black body  ·  warm only in the halo + crown edge  ·  "
                     "cream numerals  ·  locked kills the halo",
                     True, (150, 150, 176))
    canvas.blit(s, (MARGIN, MARGIN + 4 + t.get_height() + 2))

    # ── two full cards ────────────────────────────────────────────────────────
    y = MARGIN + HDR_H
    x_cards = (W - cards_w) // 2
    canvas.blit(card_aff, (x_cards, y))
    canvas.blit(card_lock, (x_cards + card_w + GAP, y))
    y += card_h + 2
    ca = lbl_f.render("AFFORDABLE", True, (255, 196, 110))
    cl = lbl_f.render("CAN'T AFFORD", True, (150, 158, 178))
    canvas.blit(ca, (x_cards + (card_w - ca.get_width()) // 2, y))
    canvas.blit(cl, (x_cards + card_w + GAP + (card_w - cl.get_width()) // 2, y))
    y += LABEL_H + 24

    # ── 4x zoom strip ─────────────────────────────────────────────────────────
    x0 = (W - strip_w) // 2
    canvas.blit(tiles[0], (x0, y))
    canvas.blit(tiles[1], (x0 + tiles[0].get_width() + GAP, y))
    y += strip_h + 4
    z = lbl_f.render("4x ZOOM — halo bleed + crown edge + cream keyline", True,
                     (176, 176, 200))
    canvas.blit(z, ((W - z.get_width()) // 2, y))
    y += LABEL_H + 26

    # ── true 1x swatches ──────────────────────────────────────────────────────
    x1 = (W - sw_w) // 2
    xs = x1
    sw_labels = ["1x  1,100 ok", "1x  1,100 locked", "1x  14,500 ok"]
    sw_cols = [(255, 196, 110), (150, 158, 178), (255, 196, 110)]
    for sw, lab, col in zip(swatches, sw_labels, sw_cols):
        sy = y + (sw_h - sw.get_height()) // 2
        canvas.blit(sw, (xs, sy))
        lt = lbl_f.render(lab, True, col)
        canvas.blit(lt, (xs + (sw.get_width() - lt.get_width()) // 2,
                         y + sw_h + 2))
        xs += sw.get_width() + sw_gap
    ttl = lbl_f.render("TRUE 1x — gameplay-scale legibility", True,
                       (176, 176, 200))
    canvas.blit(ttl, ((W - ttl.get_width()) // 2, y + sw_h + LABEL_H))

    out = os.path.join(os.path.dirname(__file__), "..", "docs",
                       "store_card_v5_price_chip_r2", "ember-crown",
                       "round_1.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
