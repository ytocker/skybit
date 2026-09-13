"""Carved-plate price chip — round 2 review render (levers T + P).

The identity is a RECESSED PLATE WINDOW: the numerals sit struck into a
slightly-darker cool-steel inset milled into the gunmetal pill. r2 fixes the
r1 read failures:

- The plate is now VISIBLY smaller than the pill interior (a real gunmetal
  frame survives on every side), so it reads as a plate INSIDE a body rather
  than a body-wide bar.
- Intaglio lighting is corrected: a debossed floor catches a low uplight, so
  the DARK edge sits at the plate's TOP inner lip and the BRIGHT catch-light
  at its BOTTOM inner lip — the opposite of the r1 top-keyline.
- The macro cast shadow lands OUTSIDE the plate, on the gunmetal body just
  below it, where it has a plane to fall on and stays visible at 1x.
- The rim is cooled + de-glossed so it stops blowing to near-white.

Body stays cool gunmetal (no amber, zero amber-regression risk). Locked dims
the rim, unlights the plate (no catch-light — the recess shadow stays), cools
the coin, and greys the numerals so 'can't afford' reads by VALUE, not hue.
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


# ── carved-plate chip ──────────────────────────────────────────────────────────
def carved_plate_chip(surf, cx, cy, text, h, affordable=True):
    """Cool-gunmetal price pill whose numerals are struck into a recessed
    cool-steel plate window. Depth reads from macro cues that survive the
    downscale: ONE cast shadow beneath the whole plate (landing on the body)
    plus intaglio lighting on the plate lips — dark top, bright bottom. Locked
    dims the rim, unlights the plate, cools the coin, and greys the digits."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)                                  # clear gap: coin cell -> plate
    f = sc.font(h * 0.50 / sc.SS)
    # measure the FAUX-BOLD stamp so the plate hugs the real inked glyph width
    nw = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0)).get_width()
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    radius = h // 2

    # cool-gunmetal body + ONE cool-steel rim, cooled + de-glossed from r1 so the
    # bright bevel stops reading near-white. Locked dims the rim further.
    if affordable:
        sc.chip_body_stops(surf, r, radius,
                           [(0.0, (58, 64, 84)), (1.0, (34, 38, 54))],
                           rim_dark=(14, 16, 26), rim_bright=(120, 135, 160),
                           gloss=16, gamma=1.04)
    else:
        sc.chip_body_stops(surf, r, radius,
                           [(0.0, (48, 52, 68)), (1.0, (30, 33, 46))],
                           rim_dark=(14, 16, 26), rim_bright=(100, 115, 140),
                           gloss=16, gamma=1.04)

    # coin cell — cool-steel rim; coin_glyph blits the real game face and ignores
    # its rim arg, so the LOCKED coin is cooled with an explicit overlay tint.
    x = r.x + pad
    ccx = x + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2, rim=(78, 84, 104))
    if not affordable:
        cool = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(cool, (60, 70, 90, 160), (coin_d // 2, coin_d // 2),
                           coin_d // 2)
        surf.blit(cool, (ccx - coin_d // 2, cy - coin_d // 2))

    # ── recessed plate window: tight around the numeral cell, and now noticeably
    # SHORTER than the pill so a gunmetal frame survives above + below it ────────
    plate_margin = sc.m(3)
    plate_x = r.x + pad + coin_d + gapc - plate_margin
    plate_w = nw + plate_margin * 2
    plate_h = h - sc.m(12)                           # smaller than r1's h - m(6)
    plate_rect = pygame.Rect(plate_x, r.centery - plate_h // 2, plate_w, plate_h)
    plate_rad = sc.m(3)

    # 1. ONE macro cast shadow OUTSIDE (below) the plate, on the gunmetal body —
    # r1 drew it on the plate itself, where it was invisible. Here it has a plane
    # to fall on and survives the downscale.
    sh_surf = pygame.Surface((plate_rect.w, sc.m(3)), pygame.SRCALPHA)
    pygame.draw.rect(sh_surf, (4, 5, 14, 90), (0, 0, plate_rect.w, sc.m(3)),
                     border_radius=2)
    surf.blit(sh_surf, (plate_rect.x, plate_rect.bottom))

    # 2. plate fill — slightly darker/cooler than the body so it reads as inset.
    plate_fill = sc.vgrad_stops(plate_rect.w, plate_rect.h, plate_rad,
                                [(0.0, (40, 44, 60)), (1.0, (28, 31, 44))],
                                255, 1.0)
    surf.blit(plate_fill, plate_rect.topleft)

    # 3. intaglio lighting — a debossed floor lit from below, so the DARK edge is
    # the TOP inner lip and the BRIGHT catch-light the BOTTOM inner lip (the
    # reverse of r1). The recess shadow persists in both states; only the
    # catch-light is state-gated so locked reads as an UNLIT plate.
    shadow_surf = pygame.Surface(plate_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (4, 5, 14, 110),
                     (0, 0, plate_rect.w, sc.m(2)), border_radius=plate_rad)
    surf.blit(shadow_surf, plate_rect.topleft)

    if affordable:
        keyline = pygame.Surface(plate_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(keyline, (190, 200, 220, 220),
                         (0, plate_rect.h - sc.m(1), plate_rect.w, sc.m(1)))
        surf.blit(keyline, plate_rect.topleft)

    # numerals struck into the plate — depth reads from the plate, not the type,
    # so no extra keyline on the glyphs themselves.
    num_col = (236, 240, 250) if affordable else (150, 158, 178)
    sc.plain_text(surf, text, f, (plate_rect.centerx, r.centery), num_col,
                  shadow_a=0, weight=sc.m(1.0))
    return r


# ── card body copied from sc.draw_card, chip call swapped ──────────────────────
def draw_card_with_chip(surf, sid, rect, affordable=True):
    """The full CONSTELLATION card body (identical to sc.draw_card) with the
    state_chip call replaced by the carved-plate chip."""
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
    # SWAP: carved-plate chip in place of state_chip.
    price = sc._cost(sid)
    carved_plate_chip(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY, f"{price:,}",
                      sc.m(20), affordable=affordable)


# ── chip strip tile (chip on a patch of card plane so the deboss reads) ─────────
def render_chip_tile(text, affordable):
    """Render one chip centred on a patch of the card body gradient, so the
    'recess below the plane' read has a plane to recede below."""
    h = sc.m(20)
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0)).get_width()
    w = pad + coin_d + gapc + nw + pad
    margin = sc.m(16)
    tw, th = w + margin * 2, h + margin * 2
    tile = pygame.Surface((tw, th), pygame.SRCALPHA)
    tile.blit(sc.vgrad(tw, th, sc.m(6), sc.CARD_T, sc.CARD_B, 255, gamma=1.15),
              (0, 0))
    carved_plate_chip(tile, tw // 2, th // 2, text, h, affordable=affordable)
    return tile


def one_x_tile(text, affordable):
    """The chip tile downscaled to the live (1x) pixel density — the exact size
    the player sees in the store — so plate legibility at gameplay scale is
    visible without any zoom."""
    ss_tile = render_chip_tile(text, affordable)
    return pygame.transform.smoothscale(
        ss_tile, (ss_tile.get_width() // sc.SS, ss_tile.get_height() // sc.SS))


# ── compose the review sheet ───────────────────────────────────────────────────
def main():
    SID = "skin_mummy"
    price_text = f"{sc._cost(SID):,}"

    # top row: two full cards at SS scale (no downscale) so the chip's fine rim +
    # plate intaglio survive — affordable left, can't-afford right.
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

    # middle: 4x zoom of the in-game (1x) chip so the plate deboss — cast shadow
    # band + top-shadow / bottom catch-light lips — can be inspected pixel-for-pixel.
    ZOOM = 4
    tiles = []
    for aff in (True, False):
        one_x = one_x_tile(price_text, aff)
        big = pygame.transform.scale(
            one_x, (one_x.get_width() * ZOOM, one_x.get_height() * ZOOM))
        tiles.append(big)

    # bottom: TRUE 1x swatches (no zoom) — the exact gameplay size — plus a wide
    # "14,500" case to confirm the plate still hugs the comma'd numerals.
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

    t = title_f.render(f"v5 carved-plate r2 — {SID} — recessed plate window",
                       True, (226, 232, 246))
    canvas.blit(t, (MARGIN, MARGIN + 4))
    s = sub_f.render("smaller plate (gunmetal frame survives)  ·  intaglio: dark "
                     "top lip + bottom catch-light  ·  cast shadow on the body",
                     True, (150, 154, 178))
    canvas.blit(s, (MARGIN, MARGIN + 4 + t.get_height() + 2))

    # ── two full cards ────────────────────────────────────────────────────────
    y = MARGIN + HEADER
    x_cards = (W - cards_w) // 2
    canvas.blit(card_aff, (x_cards, y))
    canvas.blit(card_lock, (x_cards + card_w + gap, y))
    y += card_h + 2
    ca = lbl_f.render("AFFORDABLE", True, (210, 218, 236))
    cl = lbl_f.render("CAN'T AFFORD", True, (150, 158, 178))
    canvas.blit(ca, (x_cards + (card_w - ca.get_width()) // 2, y))
    canvas.blit(cl, (x_cards + card_w + gap + (card_w - cl.get_width()) // 2, y))
    y += LABEL_H + 24

    # ── 4x zoom strip ─────────────────────────────────────────────────────────
    x0 = (W - strip_w) // 2
    canvas.blit(tiles[0], (x0, y))
    canvas.blit(tiles[1], (x0 + tiles[0].get_width() + gap, y))
    y += strip_h + 4
    z = lbl_f.render("4x ZOOM — cast shadow + intaglio lips (dark top / bright "
                     "bottom)", True, (176, 180, 204))
    canvas.blit(z, ((W - z.get_width()) // 2, y))
    y += LABEL_H + 26

    # ── true 1x swatches ──────────────────────────────────────────────────────
    x1 = (W - sw_w) // 2
    xs = x1
    sw_labels = ["1x  1,100 ok", "1x  1,100 locked", "1x  14,500 ok"]
    sw_cols = [(210, 218, 236), (150, 158, 178), (210, 218, 236)]
    for sw, lab, col in zip(swatches, sw_labels, sw_cols):
        sy = y + (sw_h - sw.get_height()) // 2
        canvas.blit(sw, (xs, sy))
        lt = lbl_f.render(lab, True, col)
        canvas.blit(lt, (xs + (sw.get_width() - lt.get_width()) // 2,
                         y + sw_h + 2))
        xs += sw.get_width() + sw_gap
    ttl = lbl_f.render("TRUE 1x — gameplay-scale legibility", True, (176, 180, 204))
    canvas.blit(ttl, ((W - ttl.get_width()) // 2, y + sw_h + LABEL_H))

    out = os.path.join(os.path.dirname(__file__), "..", "docs",
                       "store_card_v5_price_chip_r2", "carved-plate",
                       "round_2.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
