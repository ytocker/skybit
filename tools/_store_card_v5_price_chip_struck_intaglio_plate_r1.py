"""struck-intaglio-plate — store_card_v5 price-chip concept, round 1 render.

A denomination PLATE, not a coin button: a flat dark table (no gold ramp, no
bright bevel) whose price reads as DEBOSSED numerals. The engraving is faked
cheaply — the same text struck three times: a dark shadow copy nudged up-left,
a warm catch-light copy nudged down-right, and a mid-amber fill centred on top.
Because the light comes from top-left (lx,ly = -0.7071, matching the tier gem's
lighting family), a shadow above/left + a catch-light below/right reads as ink
sunk INTO the plate. The plate echoes the gem through light DIRECTION, not
faceting.

Can't-afford drops the catch-light (only the shadow remains, so the numerals
read pressed but unlit), cools the fill to grey, and cools the plate body.

Headless (SDL dummy). Renders the full skin_mummy EPIC card at SS (324x200) with
the intaglio chip swapped in for the stock price chip, then a 4x-zoomed chip
strip comparing affordable (left) vs can't-afford (right). Not wired into the
live store. Writes docs/store_card_v5_price_chip/struck-intaglio-plate/round_1.png.
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
    """A debossed denomination plate. Flat dark table (vgrad_stops, no gloss),
    a single thin dark keyline for a rim, the standard coin in its left cell,
    and the price struck THREE times to simulate engraving under a top-left
    light: dark shadow up-left, warm catch-light down-right, mid-amber fill
    centred. Can't-afford omits the catch-light and cools fill + body."""
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
    else:
        stops = [(0.0, (20, 22, 40)), (1.0, (14, 15, 32))]
    surf.blit(sc.vgrad_stops(w, h, radius, stops, 255, gamma=1.0), r.topleft)

    # minimal rim: one thin dark keyline, no bright bevel (the plate is meant to
    # sit FLAT in the card, letting the engraving carry all the relief).
    pygame.draw.rect(surf, (8, 9, 20), r, width=max(1, sc.m(1)), border_radius=radius)

    # standard coin in its own left cell
    x = r.x + pad
    coin_rim = sc.GOLD_A_COIN_RIM if affordable else (78, 84, 104)
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2, rim=coin_rim)
    x += coin_d + gapc

    # DEBOSSED numerals — light is top-left, so a shadow above/left and a
    # catch-light below/right reads as ink pressed INTO the plate.
    tcx = x + nw // 2
    # shadow copy (up-left) — always present so the numerals always read pressed
    sc.plain_text(surf, text, f, (tcx - sc.m(1), cy - sc.m(1)), (8, 9, 16),
                  shadow_a=0, weight=sc.m(0.9))
    if affordable:
        # catch-light copy (down-right) — warm lit lower edge of the groove
        sc.plain_text(surf, text, f, (tcx + sc.m(1), cy + sc.m(1)), (200, 170, 110),
                      shadow_a=0, weight=sc.m(0.9))
        fill_col = (160, 128, 72)
    else:
        # no catch-light when unlit; fill cools to neutral grey
        fill_col = (140, 148, 168)
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


def render_full_card():
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       PANEL_W - 2 * sc.m(sc._INSET), PANEL_H - 2 * sc.m(sc._INSET))
    draw_card_with_chip(big, SID, rect, equipped=False, secret=False,
                        affordable=True)
    return big


def render_chip_zoom(affordable):
    """Draw ONE chip over a slice of the real card body gradient, crop tight,
    then upscale so the engraving relief is inspectable."""
    pad = sc.m(10)
    cw, ch = sc.m(150), sc.m(20) + pad * 2
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    # a slice of the card's own indigo body so the chip is judged on its real
    # ground, not a flat swatch.
    cell.blit(sc.vgrad(cw, ch, 0, (20, 22, 52), (12, 13, 38), 255, gamma=1.15),
              (0, 0))
    r = intaglio_chip(cell, cw // 2, ch // 2, PRICE_TEXT, sc.m(20),
                      affordable=affordable)
    crop = r.inflate(pad, pad).clip(cell.get_rect())
    chip = cell.subsurface(crop).copy()
    return pygame.transform.smoothscale(
        chip, (chip.get_width() * CHIP_ZOOM, chip.get_height() * CHIP_ZOOM))


card = render_full_card()
chip_aff = render_chip_zoom(True)
chip_no = render_chip_zoom(False)

strip_h = max(chip_aff.get_height(), chip_no.get_height())
strip_w = chip_aff.get_width() + GAP + chip_no.get_width()
content_w = max(PANEL_W, strip_w)

sheet_w = MARGIN * 2 + content_w
sheet_h = (MARGIN + HEADER_H + PANEL_H + FOOTER_H + LABEL_H + strip_h
           + LABEL_H + MARGIN)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

hfont = hud_font(24, True)
sfont = hud_font(17, True)
lfont = hud_font(15, True)

htxt = hfont.render("store_card_v5 price chip — struck-intaglio-plate — round 1",
                    True, (236, 232, 214))
sheet.blit(htxt, (MARGIN, MARGIN + (HEADER_H - htxt.get_height()) // 2))

# full card, centred
card_x = MARGIN + (content_w - PANEL_W) // 2
card_y = MARGIN + HEADER_H
sheet.blit(card, (card_x, card_y))
ftxt = sfont.render("skin_mummy — EPIC — full card (SS 324x200)", True,
                    (210, 206, 192))
sheet.blit(ftxt, (MARGIN + (content_w - ftxt.get_width()) // 2,
                  card_y + PANEL_H + (FOOTER_H - ftxt.get_height()) // 2))

# zoomed chip strip
strip_label_y = card_y + PANEL_H + FOOTER_H
lt = lfont.render("chip 4x zoom  —  affordable (left)   vs   can't-afford (right)",
                  True, (196, 200, 218))
sheet.blit(lt, (MARGIN + (content_w - lt.get_width()) // 2,
                strip_label_y + (LABEL_H - lt.get_height()) // 2))
strip_y = strip_label_y + LABEL_H
strip_x0 = MARGIN + (content_w - strip_w) // 2
sheet.blit(chip_aff, (strip_x0, strip_y))
sheet.blit(chip_no, (strip_x0 + chip_aff.get_width() + GAP, strip_y))

# per-chip captions
cap_y = strip_y + strip_h
c1 = lfont.render("AFFORDABLE", True, (200, 170, 110))
c2 = lfont.render("CAN'T AFFORD", True, (140, 148, 168))
sheet.blit(c1, (strip_x0 + (chip_aff.get_width() - c1.get_width()) // 2,
                cap_y + (LABEL_H - c1.get_height()) // 2))
sheet.blit(c2, (strip_x0 + chip_aff.get_width() + GAP
                + (chip_no.get_width() - c2.get_width()) // 2,
                cap_y + (LABEL_H - c2.get_height()) // 2))

out = ("/home/user/skybit/docs/store_card_v5_price_chip/"
       "struck-intaglio-plate/round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
