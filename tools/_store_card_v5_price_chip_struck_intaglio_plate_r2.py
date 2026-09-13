"""struck-intaglio-plate — store_card_v5 price-chip concept, round 2 render.

Round-2 fixes over r1, driven by the art-director's relief/value notes:

  * Affordability value logic was INVERTED — the cool locked numerals measured
    BRIGHTER than the warm affordable ones. The locked fill now drops to a cool
    dim grey (lum ~100), clearly below the amber fill's lum ~131, so enabled
    reads warm+bright and disabled reads cool+dim (value AND hue redundancy —
    colourblind-safe).
  * Relief read ambiguous — the down-right catch-light out-massed the up-left
    shadow, so the groove could flip to reading embossed-OUT. The catch-light is
    now a THIN glint (no faux-bold growth) while the shadow keeps its heavier
    footprint, so the shadow footprint is >= the catch and the ink unmistakably
    reads SUNK.
  * Locked state kept its intaglio identity — instead of dropping the catch
    entirely (which flattened to plain drop-shadow text), it now keeps a dim
    COOL catch sliver, so the numerals read cold and pressed but unlit.
  * The plate itself is recessed — a faint plate-dark inner shadow rides the top
    inner edge of the pill so the chip reads as a table cut INTO the card, not a
    sticker laid on top.

Headless (SDL dummy). Renders the skin_mummy EPIC card at SS with the intaglio
chip swapped for the stock price chip (affordable | can't-afford), a 4x-zoomed
chip strip, and a true-1x swatch row (including 1,250 / 14,500 counter guards)
so gameplay-scale legibility is visible. Not wired into the live store. Writes
docs/store_card_v5_price_chip/struck-intaglio-plate/round_2.png.
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


# ── the intaglio-plate price chip ─────────────────────────────────────────────
def intaglio_chip(surf, cx, cy, text, h, affordable=True):
    """A debossed denomination plate. Flat dark table (vgrad_stops, no gloss), a
    thin dark keyline rim, a recessed top inner edge, the standard coin in its
    left cell, and the price struck THREE times to simulate engraving under a
    top-left light: a heavy dark shadow up-left, a THIN catch-light glint
    down-right, and a mid fill centred. Can't-afford keeps a dim COOL catch (so
    it stays intaglio, not flat drop-shadow) and cools + dims the fill below the
    amber's luminance."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)                                 # clear gap: coin cell -> digits
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    radius = h // 2

    # flat dark table — a desaturated plate, cooled further when unaffordable so
    # the whole chip greys out, not just the numerals.
    if affordable:
        stops = [(0.0, (24, 26, 44)), (1.0, (20, 22, 38))]
        plate_dark = (8, 9, 20)
    else:
        stops = [(0.0, (20, 22, 40)), (1.0, (14, 15, 32))]
        plate_dark = (6, 7, 18)
    surf.blit(sc.vgrad_stops(w, h, radius, stops, 255, gamma=1.0), r.topleft)

    # recess the plate: a faint plate-dark inner shadow hugging the TOP inner
    # edge, so with the top-left light the chip reads as a table cut into the
    # card rather than a sticker sitting on it.
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(ov, (*plate_dark, 80), ov.get_rect().inflate(-sc.m(1) * 2,
                     -sc.m(1) * 2), width=max(1, sc.m(1)), border_radius=radius)
    surf.blit(ov, r.topleft, area=pygame.Rect(0, 0, w, int(h * 0.45)))

    # minimal rim: one thin dark keyline, no bright bevel (the plate is meant to
    # sit FLAT in the card, letting the engraving carry all the relief).
    pygame.draw.rect(surf, plate_dark, r, width=max(1, sc.m(1)), border_radius=radius)

    # standard coin in its own left cell
    x = r.x + pad
    coin_rim = sc.GOLD_A_COIN_RIM if affordable else (78, 84, 104)
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2, rim=coin_rim)
    x += coin_d + gapc

    # DEBOSSED numerals — light is top-left, so a HEAVY shadow above/left plus a
    # THIN catch-light below/right reads as ink pressed INTO the plate. Keeping
    # the shadow footprint >= the catch stops the groove flipping to embossed.
    tcx = x + nw // 2
    # shadow copy (up-left) — heavier stamp, always present so the numerals
    # always read pressed.
    sc.plain_text(surf, text, f, (tcx - sc.m(1), cy - sc.m(1)), (8, 9, 16),
                  shadow_a=0, weight=sc.m(0.9))
    if affordable:
        # warm lit lower edge of the groove — a THIN glint, no faux-bold growth,
        # so it can't out-mass the shadow.
        sc.plain_text(surf, text, f, (tcx + sc.m(1), cy + sc.m(1)), (200, 170, 110),
                      shadow_a=0, weight=sc.m(0.5))
        fill_col = (160, 128, 72)                   # warm amber, lum ~131
    else:
        # a DIM COOL catch sliver keeps the groove reading pressed-but-unlit,
        # preserving the intaglio identity instead of collapsing to flat text.
        sc.plain_text(surf, text, f, (tcx + sc.m(1), cy + sc.m(1)), (88, 98, 116),
                      shadow_a=0, weight=sc.m(0.4))
        fill_col = (96, 104, 120)                   # cool grey, lum ~100 (< amber)
    # fill copy (centred) on top
    sc.plain_text(surf, text, f, (tcx, cy), fill_col, shadow_a=0, weight=sc.m(0.9))
    return r


# ── full card with the intaglio chip swapped for state_chip ───────────────────
def draw_card_with_chip(surf, sid, rect, equipped, secret, affordable):
    """A verbatim copy of sc.draw_card's body with the trailing state_chip(...)
    replaced by the intaglio plate, so the concept is judged in situ."""
    pal = sc.MYSTERY if secret else sc.RARITY[sc._rarity(sid)]
    rad = sc.m(sc.CARD_RAD)
    sc.drop_shadow(surf, rect, rad, blur=sc.m(8), alpha=160, dy=sc.m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, sc.m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, sc.m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, sc.m(2)), border_radius=rad)
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

    sc.facet_gem(surf, rect.right - sc.m(19), rect.y + sc.m(19), sc.m(sc.GEM_R + 3),
                 pal["gem"], pal["deep"], mystery=secret)

    tier_word = "MYSTERY" if secret else sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + sc.m(55) - sc._RIBN_DY,
                       rect.w - sc.m(34), pal)
    sc._name_on(surf, name, cx, rect.y + sc.m(70), rect.w - sc.m(26))

    price = sc._cost(sid)
    intaglio_chip(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY, f"{price:,}",
                  sc.m(20), affordable=affordable)


# ── review sheet ──────────────────────────────────────────────────────────────
SID = "skin_mummy"
PRICE_TEXT = f"{sc._cost(SID):,}"

PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324 x 200, no downscale
MARGIN = 20
HEADER_H = 44
FOOTER_H = 36
GAP = 22
CHIP_ZOOM = 2                                    # SS chip x2 => 4x logical
LABEL_H = 22
PANEL_GAP = 26


def render_full_card(affordable):
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       PANEL_W - 2 * sc.m(sc._INSET), PANEL_H - 2 * sc.m(sc._INSET))
    draw_card_with_chip(big, SID, rect, equipped=False, secret=False,
                        affordable=affordable)
    return big


def _chip_on_body(text, affordable):
    """Draw ONE chip over a slice of the real card body gradient and crop tight,
    so the chip is judged on its real indigo ground, not a flat swatch."""
    pad = sc.m(10)
    cw, ch = sc.m(160), sc.m(20) + pad * 2
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    cell.blit(sc.vgrad(cw, ch, 0, (20, 22, 52), (12, 13, 38), 255, gamma=1.15),
              (0, 0))
    r = intaglio_chip(cell, cw // 2, ch // 2, text, sc.m(20), affordable=affordable)
    crop = r.inflate(pad, pad).clip(cell.get_rect())
    return cell.subsurface(crop).copy()


def render_chip_zoom(affordable):
    chip = _chip_on_body(PRICE_TEXT, affordable)
    return pygame.transform.smoothscale(
        chip, (chip.get_width() * CHIP_ZOOM, chip.get_height() * CHIP_ZOOM))


def render_chip_1x(text, affordable):
    """The chip downscaled by 1/SS to true gameplay pixels — this is what the
    player actually sees, so counters and relief must survive here."""
    chip = _chip_on_body(text, affordable)
    return pygame.transform.smoothscale(
        chip, (chip.get_width() // sc.SS, chip.get_height() // sc.SS))


card_aff = render_full_card(True)
card_no = render_full_card(False)
chip_aff = render_chip_zoom(True)
chip_no = render_chip_zoom(False)

# true-1x swatches: both states at the mummy price, plus counter guards.
sw_specs = [(PRICE_TEXT, True, "AFFORDABLE"),
            (PRICE_TEXT, False, "CAN'T AFFORD"),
            ("1,250", True, "1,250"),
            ("14,500", True, "14,500")]
swatches = [(render_chip_1x(t, a), lab) for (t, a, lab) in sw_specs]

# ── layout ────────────────────────────────────────────────────────────────────
cards_w = PANEL_W * 2 + PANEL_GAP
strip_h = max(chip_aff.get_height(), chip_no.get_height())
strip_w = chip_aff.get_width() + GAP + chip_no.get_width()
sw_h = max(s.get_height() for s, _ in swatches)
sw_gap = 26
sw_w = sum(s.get_width() for s, _ in swatches) + sw_gap * (len(swatches) - 1)

content_w = max(cards_w, strip_w, sw_w)
sheet_w = MARGIN * 2 + content_w
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H
           + LABEL_H + strip_h + LABEL_H            # zoom strip + captions
           + LABEL_H + sw_h + LABEL_H               # 1x swatch row + captions
           + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = hud_font(23, True)
sfont = hud_font(17, True)
lfont = hud_font(15, True)

htxt = hfont.render(
    f"v5 struck-intaglio-plate r2 — {SID} — value fix + relief balance",
    True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

# two full cards side by side
cards_x = MARGIN + (content_w - cards_w) // 2
cards_y = MARGIN + HEADER_H
sheet.blit(card_aff, (cards_x, cards_y))
sheet.blit(card_no, (cards_x + PANEL_W + PANEL_GAP, cards_y))
cap_full_y = cards_y + PANEL_H
for label, ox in (("skin_mummy EPIC — AFFORDABLE", cards_x),
                  ("skin_mummy EPIC — CAN'T AFFORD", cards_x + PANEL_W + PANEL_GAP)):
    ft = sfont.render(label, True, (210, 206, 192))
    sheet.blit(ft, (ox + (PANEL_W - ft.get_width()) // 2,
                    cap_full_y + (FOOTER_H - ft.get_height()) // 2))

# zoomed chip strip
strip_label_y = cards_y + PANEL_H + FOOTER_H
lt = lfont.render("chip 4x zoom  —  affordable (left)   vs   can't-afford (right)",
                  True, (196, 200, 218))
sheet.blit(lt, (MARGIN + (content_w - lt.get_width()) // 2,
                strip_label_y + (LABEL_H - lt.get_height()) // 2))
strip_y = strip_label_y + LABEL_H
strip_x0 = MARGIN + (content_w - strip_w) // 2
sheet.blit(chip_aff, (strip_x0, strip_y))
sheet.blit(chip_no, (strip_x0 + chip_aff.get_width() + GAP, strip_y))
zc_y = strip_y + strip_h
c1 = lfont.render("AFFORDABLE", True, (200, 170, 110))
c2 = lfont.render("CAN'T AFFORD", True, (150, 158, 178))
sheet.blit(c1, (strip_x0 + (chip_aff.get_width() - c1.get_width()) // 2,
                zc_y + (LABEL_H - c1.get_height()) // 2))
sheet.blit(c2, (strip_x0 + chip_aff.get_width() + GAP
                + (chip_no.get_width() - c2.get_width()) // 2,
                zc_y + (LABEL_H - c2.get_height()) // 2))

# true-1x swatch row
sw_label_y = zc_y + LABEL_H
slt = lfont.render("true 1x — gameplay scale (no zoom)  +  counter guards",
                   True, (196, 200, 218))
sheet.blit(slt, (MARGIN + (content_w - slt.get_width()) // 2,
                 sw_label_y + (LABEL_H - slt.get_height()) // 2))
sw_y = sw_label_y + LABEL_H
sw_x = MARGIN + (content_w - sw_w) // 2
for surf_s, lab in swatches:
    sheet.blit(surf_s, (sw_x, sw_y + (sw_h - surf_s.get_height()) // 2))
    ct = lfont.render(lab, True, (188, 194, 210))
    sheet.blit(ct, (sw_x + (surf_s.get_width() - ct.get_width()) // 2,
                    sw_y + sw_h + (LABEL_H - ct.get_height()) // 2))
    sw_x += surf_s.get_width() + sw_gap

out = ("/home/user/skybit/docs/store_card_v5_price_chip/"
       "struck-intaglio-plate/round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
