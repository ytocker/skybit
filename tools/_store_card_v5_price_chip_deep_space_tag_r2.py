"""v5 price-chip concept: DEEP-SPACE TAG — round 2.

Round-1 read as a good instrument face but sat too flush on the card and lost
its currency signifier when locked. Round 2 addresses the art-director notes:

  1. Seated object — the space body is pushed distinctly darker + cooler-neutral
     than the card floor, and a faded cool-steel catch-light rides the top lip so
     the pill reads as recessed hardware catching sky (still matte — no gloss).
  2. Locked coin — no more near-black void; the disc keeps its shape and reads as
     currency, cooled toward grey-gold by a translucent steel tint on the face.
  3. Tier-agnostic bezel — the rim is now neutral steel-grey, so it defines the
     pill edge on EPIC (purple gem) and LEGENDARY (gold gem) alike, instead of
     harmonising only with cyan RARE.
  4. Two tiers on the sheet — EPIC (skin_mummy) and LEGENDARY (skin_kitsune) shown
     side by side, plus a true-1x swatch row for gameplay-scale legibility.

Output: docs/store_card_v5_price_chip/deep-space-tag/round_2.png
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.hud import _font as hud_font

EPIC_SID = "skin_mummy"        # EPIC — purple gem
LEG_SID = "skin_kitsune"       # LEGENDARY — gold gem

CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
SS = sc.SS
_INSET = 6
PANEL_W = CARD_W * SS
PANEL_H = CARD_H * SS

# Deep space body: pushed distinctly darker + cooler-neutral than the card floor
# (CARD_B is 12,13,38) so the pill reads as a seated object, not a same-value patch.
DSPACE_STOPS = [(0.0, (6, 7, 14)), (1.0, (4, 5, 10))]
# Cold cyan->white numeral gradient (top cyan, foot near-white): a lit readout.
TXT_STOPS = [(0.0, (180, 230, 255)), (1.0, (240, 250, 255))]
# Tier-agnostic edge: a neutral steel-grey bezel defines the pill on ANY gem hue.
BEZEL = (100, 115, 130)


# ── the deep-space price chip ──────────────────────────────────────────────────
def _grad_numerals(surf, text, f, center):
    """Cyan->white gradient numerals: a white faux-bold glyph mask multiplied by
    a vertical cold ramp so the digits read like an instrument readout without any
    actual glow layer."""
    base = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(0.9))
    w_t, h_t = base.get_size()
    grad = sc.vgrad_stops(w_t, h_t, 0, TXT_STOPS, 255, 1.0)
    img = base.copy()
    img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, img.get_rect(center=center))


def _top_catchlight(surf, r, rad, w):
    """A cool-steel hairline riding ONLY the top lip, faded to nothing by mid-body.
    This is the single cue that turns a flat dark patch into recessed hardware
    catching sky — deliberately not a full outline, so the finish stays matte."""
    cl = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    pygame.draw.rect(cl, (176, 194, 214, 255), (1, 1, r.w - 2, r.h - 2),
                     width=w, border_radius=rad)
    fade = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    span = max(1.0, r.h * 0.5)
    for y in range(r.h):
        a = max(0, 60 - int(60 * y / span))
        fade.fill((255, 255, 255, a), (0, y, r.w, 1))
    cl.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(cl, r.topleft)


def deep_space_chip(surf, cx, cy, text, h, affordable=True):
    """Price chip as a hyperspace-coordinates readout. Same coin-cell + digit-cell
    footprint as the production price chip so the row metrics are unchanged, but
    the finish is a recessed instrument bezel: matte space body seated on the card,
    ONE neutral steel rim, cold numerals, warm coin. Can't-afford desaturates the
    digits and cools the coin toward grey-gold — keeping the disc legible as
    currency rather than deleting it."""
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)                                   # clear gap: coin cell -> digits
    f = sc.font(h * 0.50 / SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    rad = h // 2

    # A restrained drop shadow seats the matte body on the card as a physical
    # bezel; no gloss sweep / AO so it reads FLAT, not domed.
    sc.drop_shadow(surf, r, rad, blur=sc.m(4), alpha=110, dy=sc.m(2))
    surf.blit(sc.vgrad_stops(r.w, r.h, rad, DSPACE_STOPS, 255, gamma=1.0), r.topleft)

    # top-lip catch-light BEFORE the rim so the steel bezel stays the crisp edge.
    _top_catchlight(surf, r, rad, max(1, sc.m(1)))

    # single thin NEUTRAL steel bezel, even on all four sides (no bevel bias so it
    # reads as a bezel, not a raised rim). Tier-agnostic: same on purple/gold gems.
    rim_a = 100 if affordable else 70
    rim_surf = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    pygame.draw.rect(rim_surf, (*BEZEL, rim_a), (0, 0, r.w, r.h),
                     width=max(1, sc.m(1)), border_radius=rad)
    surf.blit(rim_surf, r.topleft)

    # warm gold coin anchor — the deliberate warm/cold contrast against the body.
    x = r.x + pad
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
    if not affordable:
        # cool the coin toward grey-gold rather than dimming to a void: the disc +
        # rim shape survives so the locked chip still reads as a PRICE, just muted.
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, (80, 90, 110, 150),
                           (coin_d // 2, coin_d // 2), coin_d // 2)
        surf.blit(tint, (x, cy - coin_d // 2))

    x += coin_d + gapc
    center = (x + nw // 2, cy)
    if affordable:
        _grad_numerals(surf, text, f, center)
    else:
        sc.plain_text(surf, text, f, center, (150, 156, 168), shadow_a=0,
                      weight=sc.m(0.9))
    return r


# ── full card with the deep-space chip swapped in for state_chip ───────────────
def draw_card_with_chip(surf, sid, rect, affordable=True):
    """A verbatim copy of sc.draw_card()'s body with the final state_chip() call
    replaced by the deep-space price chip. Everything else is identical."""
    pal = sc.RARITY[sc._rarity(sid)]
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
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray,
                     width=max(1, sc.m(1)), border_radius=trad)

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
    price = sc._cost(sid)
    deep_space_chip(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY, f"{price:,}",
                    sc.m(20), affordable=affordable)


def render_card_panel(sid, affordable):
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET), PANEL_H - 2 * sc.m(_INSET))
    draw_card_with_chip(big, sid, rect, affordable=affordable)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


# ── zoomed chip tile (chip on its real card-body ground) ────────────────────────
ZOOM = 2   # SS=2 author surface x2 upscale = 4x logical


def _chip_footprint(text, h):
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    return pad + coin_d + gapc + nw + pad


def render_chip_tile(text, affordable, zoom=ZOOM, marg=None):
    h = sc.m(20)
    w = _chip_footprint(text, h)
    marg = sc.m(11) if marg is None else marg
    tw, th = w + marg * 2, h + marg * 2
    tile = pygame.Surface((tw, th), pygame.SRCALPHA)
    # draw on the real card-body gradient so the matte chip is judged in context.
    tile.blit(sc.vgrad(tw, th, sc.m(8), sc.CARD_T, sc.CARD_B, 255, gamma=1.15), (0, 0))
    deep_space_chip(tile, tw // 2, th // 2, text, h, affordable=affordable)
    if zoom == 1:
        return tile
    return pygame.transform.smoothscale(tile, (tw * zoom, th * zoom))


# ── compose sheet ───────────────────────────────────────────────────────────────
BG = (8, 8, 20)
MARGIN = 22
HDR_H = 44
FOOTER_H = 30
GAP = 16
COL_GAP = 34
LBL_H = 20
SWATCH_LBL_H = 30

EPIC_PRICE = f"{sc._cost(EPIC_SID):,}"
LEG_PRICE = f"{sc._cost(LEG_SID):,}"

# Per-tier column: affordable + can't-afford full cards side by side, then a
# 4x-zoomed chip strip (affordable | locked) directly beneath.
tiers = [
    ("EPIC", EPIC_SID, EPIC_PRICE, sc.RARITY["epic"]["gem"]),
    ("LEGENDARY", LEG_SID, LEG_PRICE, sc.RARITY["legendary"]["gem"]),
]

zoom_tiles = {name: (render_chip_tile(price, True), render_chip_tile(price, False))
              for name, _sid, price, _c in tiers}

col_cards_w = PANEL_W * 2 + GAP
zt = zoom_tiles["EPIC"]
zoom_strip_w = zt[0].get_width() + GAP + zt[1].get_width()
zoom_strip_h = max(zt[0].get_height(), zt[1].get_height())
col_w = max(col_cards_w, zoom_strip_w)

content_w = col_w * 2 + COL_GAP
canvas_w = MARGIN * 2 + content_w

col_block_h = LBL_H + PANEL_H + GAP + zoom_strip_h + LBL_H + 20

# true-1x swatch row (no zoom) — gameplay-scale legibility check.
sw1x = {name: (render_chip_tile(price, True, zoom=1, marg=sc.m(6)),
               render_chip_tile(price, False, zoom=1, marg=sc.m(6)))
        for name, _sid, price, _c in tiers}
swatch_h = sw1x["EPIC"][0].get_height()

canvas_h = (MARGIN + HDR_H + col_block_h + GAP
            + SWATCH_LBL_H + swatch_h + LBL_H + FOOTER_H + MARGIN)

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf = hud_font(18, True)
htxt = hf.render("v5 deep-space-tag r2 — seated object + tier check",
                 True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

col_lbl_font = hud_font(15, True)
lbl_font = hud_font(12, True)
sub_font = hud_font(10, False)

top_y = MARGIN + HDR_H
for i, (name, sid, price, gem) in enumerate(tiers):
    col_x = MARGIN + i * (col_w + COL_GAP)

    # column tier heading
    ct = col_lbl_font.render(f"{name}  ({price})", True, gem)
    canvas.blit(ct, (col_x + (col_w - ct.get_width()) // 2, top_y))

    cards_x = col_x + (col_w - col_cards_w) // 2
    cards_y = top_y + LBL_H
    canvas.blit(render_card_panel(sid, True), (cards_x, cards_y))
    canvas.blit(render_card_panel(sid, False), (cards_x + PANEL_W + GAP, cards_y))

    # card-state labels
    st_y = cards_y + PANEL_H - 2
    for sx, title, col in [
        (cards_x, "AFFORDABLE", (150, 220, 255)),
        (cards_x + PANEL_W + GAP, "CAN'T AFFORD", (150, 158, 172)),
    ]:
        st = sub_font.render(title, True, col)
        canvas.blit(st, (sx + (PANEL_W - st.get_width()) // 2, st_y))

    # 4x-zoomed chip strip beneath the two cards
    aff, lock = zoom_tiles[name]
    strip_w = aff.get_width() + GAP + lock.get_width()
    strip_x = col_x + (col_w - strip_w) // 2
    strip_y = cards_y + PANEL_H + GAP + 8
    canvas.blit(aff, (strip_x, strip_y))
    canvas.blit(lock, (strip_x + aff.get_width() + GAP, strip_y))

# ── bottom: true-1x swatches for both tiers, no zoom ────────────────────────────
sw_hdr_y = top_y + col_block_h + GAP
sh = hud_font(13, True)
sht = sh.render("TRUE 1x — gameplay-scale legibility (no zoom)", True, (198, 194, 216))
canvas.blit(sht, ((canvas_w - sht.get_width()) // 2, sw_hdr_y))

sw_y = sw_hdr_y + SWATCH_LBL_H
sw_items = []
for name, _sid, _price, gem in tiers:
    a, l = sw1x[name]
    sw_items.append((f"{name} · buy", a, gem))
    sw_items.append((f"{name} · locked", l, (150, 158, 172)))

sw_total = sum(t[1].get_width() for t in sw_items) + GAP * (len(sw_items) - 1)
sw_x = (canvas_w - sw_total) // 2
for title, tile, col in sw_items:
    canvas.blit(tile, (sw_x, sw_y))
    lt = sub_font.render(title, True, col)
    canvas.blit(lt, (sw_x + (tile.get_width() - lt.get_width()) // 2,
                     sw_y + tile.get_height() + 4))
    sw_x += tile.get_width() + GAP

ft = sub_font.render(
    "matte space body seated on card · top-lip catch-light · neutral steel bezel (tier-agnostic) · locked coin cooled, not deleted",
    True, (120, 118, 140))
canvas.blit(ft, ((canvas_w - ft.get_width()) // 2, canvas_h - MARGIN - ft.get_height()))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_price_chip", "deep-space-tag", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}x{canvas_h})")
