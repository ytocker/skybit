"""v5 price-chip concept: GEM-RING (Lever P) — round 1.

The rarity signal lives entirely in the PERIMETER, not the body: a quiet dark
neutral pill wears a gem-coloured bevel ring whose brightness is value-stepped
per tier toward white (so it reads on value, not hue alone), separated from the
card by a thin dark channel and lifted by a soft tier aura. Near-white numerals
stay rarity-agnostic and always legible. Can't-afford drops the aura and cools
the ring + digits to a dim neutral.

Two tiers on the sheet — EPIC (skin_mummy, purple gem) and LEGENDARY
(skin_kitsune, gold gem) — side by side to prove the rarity-matched perimeter,
plus a 4x chip strip and a true-1x swatch row for gameplay-scale legibility.

Output: docs/store_card_v5_price_chip_r2/gem-ring/round_1.png
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

# Quiet dark-neutral body: the perimeter carries ALL the rarity signal, so the
# fill is a near-flat cool slate that never competes with the gem ring.
BODY_STOPS = [(0.0, (26, 28, 46)), (1.0, (16, 18, 32))]
# The chip-body's own inner edge is kept a mute dark neutral (mostly ridden over
# by the gem ring) so it reads as a quiet self-edge, not a second colour band.
INNER_DARK = (12, 14, 24)
INNER_BRIGHT = (40, 44, 64)
# Near-white numerals: rarity-agnostic, always legible on the dark body.
NUM_COL = (246, 244, 232)
NUM_KEYLINE = (12, 14, 26)


def lerp_c(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


# ── per-tier gem-ring brightness step ───────────────────────────────────────────
# The bevel is value-stepped toward white so a saturated gem hue reads as a lit
# metal ring rather than a muddy coloured line: EPIC purple needs the biggest lift
# (deepest hue), LEGENDARY gold a touch less, quieter tiers barely any.
_BEVEL_LIFT = {"epic": 0.35, "legendary": 0.28, "rare": 0.14,
               "common": 0.14, "mystery": 0.14}


def _bevel_bright(rarity, gem):
    return (*lerp_c(gem, (255, 255, 255), _BEVEL_LIFT.get(rarity, 0.14)), 235)


# ── the gem-ring price chip ─────────────────────────────────────────────────────
def gem_ring_chip(surf, cx, cy, text, h, sid, affordable=True):
    """Price chip whose rarity read is a gem-coloured bevel ring on a quiet dark
    body. Draw order: tier aura -> dark channel -> body (+ mute inner bevel) ->
    gem outer ring -> coin -> near-white numerals. Can't-afford drops the aura and
    cools the ring + digits to a dim neutral, keeping the coin legible as currency
    under a cool tint."""
    rarity = sc._rarity(sid)
    pal = sc.RARITY[rarity]

    # same coin-cell + digit-cell footprint as the production price chip so the
    # card's row metrics are unchanged.
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    rad = h // 2

    if affordable:
        bright = _bevel_bright(rarity, pal["gem"])
        deep = pal["deep"]
        # soft tier aura lifts the whole chip off the card BEFORE the body lands.
        sc._alpha_aura(surf, cx, cy, radius=int(h * 0.7), color=pal["glow"],
                       peak=24, layers=15)
    else:
        # cool-dim neutral ring: the pill still reads as a defined object, the
        # rarity signal simply goes quiet when unaffordable.
        bright = (168, 176, 198, 235)
        deep = (14, 16, 26)

    # dark channel just OUTSIDE the body edge, drawn before the ring so a thin
    # gap separates the gem ring from the card — the jewellery "floating" cue.
    pygame.draw.rect(surf, (14, 16, 26, 180), r.inflate(sc.m(1), sc.m(1)),
                     width=max(1, sc.m(1)), border_radius=rad)

    # quiet dark body with only a mute inner emboss (INNER_*); the gem ring below
    # is the sole coloured perimeter band.
    sc.chip_body_stops(surf, r, rad, BODY_STOPS, INNER_DARK, INNER_BRIGHT,
                       gloss=24, gamma=1.05)

    # the single rarity band: a value-stepped gem-colour bevel ring.
    sc.bevel_rim(surf, r, rad, deep, bright, w=max(1, sc.m(1.5)))

    # coin anchor (rim is a no-op in coin_glyph; locked state gets a cool overlay).
    x = r.x + pad
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2, rim=(120, 74, 14))
    if not affordable:
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, (60, 70, 90, 160),
                           (coin_d // 2, coin_d // 2), coin_d // 2)
        surf.blit(tint, (x, cy - coin_d // 2))

    x += coin_d + gapc
    center = (x + nw // 2, cy)
    col = NUM_COL if affordable else (150, 158, 178)
    sc.plain_text(surf, text, f, center, col, shadow_a=0, weight=sc.m(1.0),
                  keyline=NUM_KEYLINE, kw=sc.m(0.7))
    return r


# ── full card with the gem-ring chip swapped in for state_chip ──────────────────
def draw_card_with_chip(surf, sid, rect, affordable=True):
    """A copy of sc.draw_card()'s body with the final state_chip() call replaced
    by the gem-ring price chip. Everything else is identical."""
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
    gem_ring_chip(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY, f"{price:,}",
                  sc.m(20), sid, affordable=affordable)


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


def render_chip_tile(text, sid, affordable, zoom=ZOOM, marg=None):
    h = sc.m(20)
    w = _chip_footprint(text, h)
    marg = sc.m(11) if marg is None else marg
    tw, th = w + marg * 2, h + marg * 2
    tile = pygame.Surface((tw, th), pygame.SRCALPHA)
    tile.blit(sc.vgrad(tw, th, sc.m(8), sc.CARD_T, sc.CARD_B, 255, gamma=1.15), (0, 0))
    gem_ring_chip(tile, tw // 2, th // 2, text, h, sid, affordable=affordable)
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

tiers = [
    ("EPIC", EPIC_SID, EPIC_PRICE, sc.RARITY["epic"]["gem"]),
    ("LEGENDARY", LEG_SID, LEG_PRICE, sc.RARITY["legendary"]["gem"]),
]

zoom_tiles = {name: (render_chip_tile(price, sid, True),
                     render_chip_tile(price, sid, False))
              for name, sid, price, _c in tiers}

col_cards_w = PANEL_W * 2 + GAP
zt = zoom_tiles["EPIC"]
zoom_strip_w = zt[0].get_width() + GAP + zt[1].get_width()
zoom_strip_h = max(zt[0].get_height(), zt[1].get_height())
col_w = max(col_cards_w, zoom_strip_w)

content_w = col_w * 2 + COL_GAP
canvas_w = MARGIN * 2 + content_w

col_block_h = LBL_H + PANEL_H + GAP + zoom_strip_h + LBL_H + 20

sw1x = {name: (render_chip_tile(price, sid, True, zoom=1, marg=sc.m(6)),
               render_chip_tile(price, sid, False, zoom=1, marg=sc.m(6)))
        for name, sid, price, _c in tiers}
swatch_h = sw1x["EPIC"][0].get_height()

canvas_h = (MARGIN + HDR_H + col_block_h + GAP
            + SWATCH_LBL_H + swatch_h + LBL_H + FOOTER_H + MARGIN)

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf = hud_font(18, True)
htxt = hf.render("v5 gem-ring r1 — rarity in the perimeter, quiet body",
                 True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

col_lbl_font = hud_font(15, True)
lbl_font = hud_font(12, True)
sub_font = hud_font(10, False)

top_y = MARGIN + HDR_H
for i, (name, sid, price, gem) in enumerate(tiers):
    col_x = MARGIN + i * (col_w + COL_GAP)

    ct = col_lbl_font.render(f"{name}  ({price})", True, gem)
    canvas.blit(ct, (col_x + (col_w - ct.get_width()) // 2, top_y))

    cards_x = col_x + (col_w - col_cards_w) // 2
    cards_y = top_y + LBL_H
    canvas.blit(render_card_panel(sid, True), (cards_x, cards_y))
    canvas.blit(render_card_panel(sid, False), (cards_x + PANEL_W + GAP, cards_y))

    st_y = cards_y + PANEL_H - 2
    for sx, title, col in [
        (cards_x, "AFFORDABLE", (150, 220, 255)),
        (cards_x + PANEL_W + GAP, "CAN'T AFFORD", (150, 158, 172)),
    ]:
        st = sub_font.render(title, True, col)
        canvas.blit(st, (sx + (PANEL_W - st.get_width()) // 2, st_y))

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
    "quiet dark body · value-stepped gem bevel ring (EPIC +35% / LEG +28% toward white) · dark channel gap · tier aura · near-white rarity-agnostic numerals",
    True, (120, 118, 140))
canvas.blit(ft, ((canvas_w - ft.get_width()) // 2, canvas_h - MARGIN - ft.get_height()))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_price_chip_r2", "gem-ring", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}x{canvas_h})")
