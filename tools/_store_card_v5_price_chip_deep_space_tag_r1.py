"""v5 price-chip concept: DEEP-SPACE TAG — round 1.

Hyperspace-coordinates readout: a warm gold coin anchor against a near-black
matte "space" body, cold cyan->white instrument numerals, and a single thin
cyan bezel — no glass, no gloss, no glow. The warm coin is the deliberate
temperature contrast that keeps the price legible on the dark card body.

Sheet:
  Top   — full CONSTELLATION card (skin_mummy, EPIC) with the deep-space chip.
  Below — 4x-zoomed chip strip: affordable LEFT, can't-afford RIGHT.

Output: docs/store_card_v5_price_chip/deep-space-tag/round_1.png
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

SID = "skin_mummy"

CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
SS = sc.SS
_INSET = 6
PANEL_W = CARD_W * SS
PANEL_H = CARD_H * SS

# Near-black matte space body — flat instrument face, no gloss/glow.
DSPACE_STOPS = [(0.0, (10, 12, 22)), (1.0, (4, 5, 12))]
# Cold cyan->white numeral gradient (top cyan, foot near-white): a lit readout.
TXT_STOPS = [(0.0, (180, 230, 255)), (1.0, (240, 250, 255))]


# ── the deep-space price chip ──────────────────────────────────────────────────
def _grad_numerals(surf, text, f, center):
    """Cyan->white gradient numerals: a white faux-bold glyph mask multiplied by
    a vertical cold ramp so the digits glow like an instrument readout without any
    actual glow layer."""
    base = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(0.9))
    w_t, h_t = base.get_size()
    grad = sc.vgrad_stops(w_t, h_t, 0, TXT_STOPS, 255, 1.0)
    img = base.copy()
    img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, img.get_rect(center=center))


def deep_space_chip(surf, cx, cy, text, h, affordable=True):
    """Price chip as a hyperspace-coordinates readout. Same coin-cell + digit-cell
    footprint as the production price chip so the row metrics are unchanged, but
    the finish is an instrument bezel: matte space body, ONE even thin cyan rim,
    cold numerals, warm coin. Can't-afford desaturates the rim + digits and dims
    the coin rather than recolouring the whole body."""
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
    sc.drop_shadow(surf, r, rad, blur=sc.m(4), alpha=100, dy=sc.m(2))
    surf.blit(sc.vgrad_stops(r.w, r.h, rad, DSPACE_STOPS, 255, gamma=1.0), r.topleft)

    # single thin cyan instrument bezel, even on all four sides (no bevel bias so
    # it reads as a bezel, not a raised rim). Alpha-carried so it stays a hairline.
    rim_col = (120, 190, 230, 80) if affordable else (150, 158, 172, 70)
    rim_surf = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    pygame.draw.rect(rim_surf, rim_col, (0, 0, r.w, r.h),
                     width=max(1, sc.m(1)), border_radius=rad)
    surf.blit(rim_surf, r.topleft)

    # warm gold coin anchor — the deliberate warm/cold contrast against the body.
    x = r.x + pad
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
    if not affordable:
        # dim the coin so the locked chip reads locked without the price-colour cue.
        dim = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(dim, (8, 10, 18, 120),
                           (coin_d // 2, coin_d // 2), coin_d // 2)
        surf.blit(dim, (x, cy - coin_d // 2))

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


def render_card_panel():
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET), PANEL_H - 2 * sc.m(_INSET))
    draw_card_with_chip(big, SID, rect, affordable=True)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


# ── 4x-zoomed chip tile (chip on its real card-body ground) ─────────────────────
ZOOM = 2   # SS=2 author surface x2 upscale = 4x logical


def render_chip_tile(text, affordable):
    h = sc.m(20)
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    marg = sc.m(11)
    tw, th = w + marg * 2, h + marg * 2
    tile = pygame.Surface((tw, th), pygame.SRCALPHA)
    # draw on the real card-body gradient so the matte chip is judged in context.
    tile.blit(sc.vgrad(tw, th, sc.m(8), sc.CARD_T, sc.CARD_B, 255, gamma=1.15), (0, 0))
    deep_space_chip(tile, tw // 2, th // 2, text, h, affordable=affordable)
    return pygame.transform.smoothscale(tile, (tw * ZOOM, th * ZOOM))


# ── compose sheet ───────────────────────────────────────────────────────────────
BG = (8, 8, 20)
MARGIN = 20
HDR_H = 44
FOOTER_H = 36
GAP = 16
LBL_H = 22

price_txt = f"{sc._cost(SID):,}"
tile_aff = render_chip_tile(price_txt, True)
tile_lock = render_chip_tile(price_txt, False)

strip_w = tile_aff.get_width() + GAP + tile_lock.get_width()
strip_h = max(tile_aff.get_height(), tile_lock.get_height())

content_w = max(PANEL_W, strip_w)
canvas_w = MARGIN * 2 + content_w
canvas_h = (MARGIN + HDR_H + PANEL_H + GAP + strip_h + LBL_H + FOOTER_H + MARGIN)

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf = hud_font(18, True)
htxt = hf.render("v5 price chip  —  DEEP-SPACE TAG  —  round 1  —  skin_mummy (EPIC)",
                 True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

# full card, centered
card = render_card_panel()
card_x = (canvas_w - PANEL_W) // 2
card_y = MARGIN + HDR_H
canvas.blit(card, (card_x, card_y))

# chip strip: affordable LEFT, can't-afford RIGHT
strip_x = (canvas_w - strip_w) // 2
strip_y = card_y + PANEL_H + GAP
canvas.blit(tile_aff, (strip_x, strip_y))
canvas.blit(tile_lock, (strip_x + tile_aff.get_width() + GAP, strip_y))

lbl_font = hud_font(13, True)
sub_font = hud_font(10, False)
lbl_y = strip_y + strip_h + 4
for x0, tw_i, title, sub, col in [
    (strip_x, tile_aff.get_width(), "AFFORDABLE", "cyan->white readout, warm coin", (150, 220, 255)),
    (strip_x + tile_aff.get_width() + GAP, tile_lock.get_width(), "CAN'T AFFORD",
     "rim + digits desaturate, coin dims", (150, 158, 172)),
]:
    t1 = lbl_font.render(title, True, col)
    canvas.blit(t1, (x0 + (tw_i - t1.get_width()) // 2, lbl_y))
    t2 = sub_font.render(sub, True, (130, 126, 150))
    canvas.blit(t2, (x0 + (tw_i - t2.get_width()) // 2, lbl_y + t1.get_height() + 2))

ft = sub_font.render("4x-zoomed chips shown on the real card-body ground  ·  no glass, no gloss, no glow",
                     True, (120, 118, 140))
canvas.blit(ft, ((canvas_w - ft.get_width()) // 2, canvas_h - MARGIN - ft.get_height()))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_price_chip", "deep-space-tag", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}x{canvas_h})")
