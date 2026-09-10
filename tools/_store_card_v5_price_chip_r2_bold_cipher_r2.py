"""v5 price-chip concept: BOLD-CIPHER — round 2 (Lever: T — typography).

The premise is unchanged from r1: strip the chip back to a matte near-black
obsidian slab and let the numerals BE the identity. r2 acts on the art-director
critique:

  - Cool numeral gradient, verified. r1 read warm-cream; r2 pins a PURE-WHITE
    crown fading to a COOL blue-white foot (b must exceed r by ~35) and samples
    the actually-rendered glyph foot pixels at the bottom of this file to prove
    b>r — the gradient can't drift warm undetected.
  - True near-black body. Affordable slab is (12,12,18)->(6,6,12): obsidian with
    ZERO purple/hue cast (r1 had a purple tint). gloss dropped to 10.
  - Unmissable state split. Locked slab lifts to a clearly lighter, cooler slate
    (58,62,80)->(36,40,56) — a large, obvious luma gap over the affordable
    obsidian so afford/locked can never be confused. gloss 10.
  - Locked numerals cool + clearly dimmer than the affordable near-white, yet
    still readable and cooler than their slate body so they pop.

Round-2 sheet: skin_mummy EPIC affordable + can't-afford heroes, a 4x detail
strip, and a true-1x swatch row that includes the "100,000" worst-case so the
oversized glyph width holds against the widest price the store can show.

Output: docs/store_card_v5_price_chip_r2/bold-cipher/round_2.png
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

SID = "skin_mummy"        # EPIC — purple gem

# ── state palette (r2) ────────────────────────────────────────────────────────
# Affordable: obsidian, no hue tint. Locked: distinctly lighter + cooler slate —
# the luma gap is the primary "can't afford" read (colourblind-safe on value).
AFF_BODY = [(0.0, (12, 12, 18)), (1.0, (6, 6, 12))]
LOCK_BODY = [(0.0, (58, 62, 80)), (1.0, (36, 40, 56))]
AFF_RIM_BRIGHT = (140, 155, 175)          # cool steel
LOCK_RIM_BRIGHT = (155, 168, 188)         # cool steel, a touch brighter on slate
RIM_DARK = (8, 8, 14)
# Numerals: pure-white crown -> cool blue-white foot (b>r). Locked cools + dims.
AFF_TOP, AFF_FOOT = (255, 255, 255), (200, 215, 235)
LOCK_TOP, LOCK_FOOT = (210, 216, 230), (190, 196, 212)


# ── numerals: the entire identity ─────────────────────────────────────────────
def _draw_numerals(surf, text, f, nw, center, top_col, foot_col):
    """Cool-lit glyph block over a 1px dark keyline.

    A black keyline is stamped one step out (kw) so a hairline of dark survives
    around the glyph on the matte slab, killing the soft halo a bright glyph
    would otherwise bleed on a near-black ground. The face is a WHITE glyph
    master multiplied (BLEND_RGBA_MULT) by a top->foot cool ramp, so white*cool
    = cool: the digits read as one lit block of type, crown to foot, and can
    never resolve warm as long as foot_col keeps b>r."""
    sc.plain_text(surf, text, f, center, (0, 0, 0), shadow_a=0,
                  weight=sc.m(0.8), keyline=(12, 14, 26), kw=sc.m(0.8),
                  tracking=sc.m(2))
    glyph_mask = sc._stamp_bold(sc._glyph_base(text, f, sc.m(2)), sc.m(1.2))
    grad = sc.vgrad_stops(glyph_mask.get_width(), glyph_mask.get_height(), 0,
                          [(0.0, top_col), (1.0, foot_col)], 255, 1.0)
    img = glyph_mask.copy()
    img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, img.get_rect(center=center))


def _stamped_width(text, f):
    """Chip width is driven by the ACTUAL stamped glyph (oversized + tracked +
    faux-bolded), not the raw glyph — so the pill hugs the real ink extent."""
    stamped = sc._stamp_bold(sc._glyph_base(text, f, sc.m(2)), sc.m(1.2))
    return stamped.get_width()


def bold_cipher_chip(surf, cx, cy, text, h, affordable=True):
    """Matte-slab price chip whose whole identity is oversized numerals. The
    body is a true near-black obsidian slab (affordable) or a clearly lighter,
    cooler slate (locked) with ONE thin cool-steel bevel and minimal gloss/AO,
    so nothing competes with the type. Digits are 1.2x the stock height,
    m(2)-tracked, cool near-white with a blue-white foot, keylined against the
    slab. Locked lifts the whole slab in value (unmissable affordability read)
    and cools the coin toward slate so it reads locked on value, not hue."""
    coin_d = int(h * 0.66)                 # 26 dev px at h=40
    pad = sc.m(13)                         # 26
    gapc = sc.m(8)                         # 16 — clear gap: coin cell -> digits
    f = sc.font(h * 0.60 / sc.SS)          # 1.2x the stock 0.50 height
    nw = _stamped_width(text, f)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    rad = h // 2                           # full pill silhouette

    if affordable:
        # true obsidian — no purple/hue cast, deliberately abandoning the gold pill
        sc.chip_body_stops(surf, r, rad, stops=AFF_BODY,
                           rim_dark=RIM_DARK, rim_bright=AFF_RIM_BRIGHT,
                           gloss=10, gamma=1.03)
        top_col, foot_col = AFF_TOP, AFF_FOOT
        cool_coin = None
    else:
        # locked: whole slab lifts to a clearly lighter, cooler slate — the luma
        # gap over obsidian IS the affordability signal.
        sc.chip_body_stops(surf, r, rad, stops=LOCK_BODY,
                           rim_dark=RIM_DARK, rim_bright=LOCK_RIM_BRIGHT,
                           gloss=10, gamma=1.03)
        top_col, foot_col = LOCK_TOP, LOCK_FOOT
        cool_coin = (60, 70, 90, 160)

    x = r.x + pad
    ccx = x + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2)
    if cool_coin is not None:
        # coin_glyph() ignores its rim arg; overlay a slate tint so the locked
        # coin cools toward grey rather than staying warm gold.
        cr = coin_d // 2
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, cool_coin, (cr, cr), cr)
        surf.blit(tint, (ccx - cr, cy - cr))
    x += coin_d + gapc
    _draw_numerals(surf, text, f, nw, (x + nw // 2, cy), top_col, foot_col)
    return r


# ── full card with the bold-cipher chip swapped in for state_chip ─────────────
def draw_card_with_chip(surf, sid, rect, affordable=True):
    """sc.draw_card()'s body verbatim, with the final state_chip() call replaced
    by the bold-cipher price chip. Everything else is identical."""
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
    price = f"{sc._cost(sid):,}"
    bold_cipher_chip(surf, cx, rect.y + sc.m(88) - sc._CHIP_DY, price,
                     sc.m(20), affordable=affordable)


# ── panels + chip tiles ───────────────────────────────────────────────────────
_INSET = 6
PANEL_W = sc.CARD_W * sc.SS       # 324
PANEL_H = sc.CARD_H * sc.SS       # 200


def render_card_panel(sid, affordable):
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                       PANEL_W - 2 * sc.m(_INSET), PANEL_H - 2 * sc.m(_INSET))
    draw_card_with_chip(big, sid, rect, affordable=affordable)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


def _chip_footprint(text, h):
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.60 / sc.SS)
    nw = _stamped_width(text, f)
    return pad + coin_d + gapc + nw + pad


def render_chip_tile(text, affordable, zoom=4, marg=None):
    """A chip drawn on the real card-body gradient so the matte slab is judged in
    context, then scaled by `zoom` (1 = true gameplay logical scale)."""
    h = sc.m(20)
    w = _chip_footprint(text, h)
    marg = sc.m(11) if marg is None else marg
    tw, th = w + marg * 2, h + marg * 2
    tile = pygame.Surface((tw, th), pygame.SRCALPHA)
    tile.blit(sc.vgrad(tw, th, sc.m(8), sc.CARD_T, sc.CARD_B, 255, gamma=1.15), (0, 0))
    bold_cipher_chip(tile, tw // 2, th // 2, text, h, affordable=affordable)
    if zoom == 1:
        # downscale SS author surface to true 1x logical gameplay size
        return pygame.transform.smoothscale(
            tile, (max(1, round(tw / sc.SS)), max(1, round(th / sc.SS))))
    return pygame.transform.smoothscale(tile, (tw * zoom, th * zoom))


# ── verification: prove the numeral gradient is cool (b>r at the foot) ─────────
def _verify_cool_gradient():
    """Render an affordable numeral block in isolation, then sample its LOWEST
    opaque glyph pixels: the foot must satisfy b>r by a healthy margin. Guards
    against any silent drift back to the r1 warm-cream failure."""
    h = sc.m(20)
    f = sc.font(h * 0.60 / sc.SS)
    text = "1,234"
    glyph_mask = sc._stamp_bold(sc._glyph_base(text, f, sc.m(2)), sc.m(1.2))
    gw, gh = glyph_mask.get_size()
    grad = sc.vgrad_stops(gw, gh, 0, [(0.0, AFF_TOP), (1.0, AFF_FOOT)], 255, 1.0)
    img = glyph_mask.copy()
    img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    # sample opaque pixels in the bottom 12% of the glyph body (the "foot")
    foot_r = foot_b = n = 0
    y0 = int(gh * 0.88)
    for y in range(y0, gh):
        for x in range(gw):
            rr, gg, bb, aa = img.get_at((x, y))
            if aa > 200:
                foot_r += rr
                foot_b += bb
                n += 1
    if n:
        ar, ab = foot_r / n, foot_b / n
        print("FOOT SAMPLE  r=%.1f b=%.1f  (b-r=%.1f, must be >0 / target ~+35)"
              % (ar, ab, ab - ar))
        assert ab - ar > 20, "numeral foot drifted WARM — b must exceed r"
    else:
        print("FOOT SAMPLE  no opaque pixels found")


# ── compose sheet ─────────────────────────────────────────────────────────────
BG = (8, 8, 20)
MARGIN = 20
HDR_H = 44
FOOTER_H = 30
GAP = 16
LBL_H = 20

MUMMY_PRICE = f"{sc._cost(SID):,}"
WIDE_PRICE = "100,000"            # worst-case width verification

# width + colour reports
_h = sc.m(20)
_f = sc.font(_h * 0.60 / sc.SS)
print("stamped nw (100,000):", _stamped_width(WIDE_PRICE, _f),
      " chip w:", _chip_footprint(WIDE_PRICE, _h))
print("stamped nw (mummy %s):" % MUMMY_PRICE, _stamped_width(MUMMY_PRICE, _f),
      " chip w:", _chip_footprint(MUMMY_PRICE, _h))
print("AFF_FOOT b-r =", AFF_FOOT[2] - AFF_FOOT[0],
      " LOCK_FOOT b-r =", LOCK_FOOT[2] - LOCK_FOOT[0])
_verify_cool_gradient()


def main():
    card_yes = render_card_panel(SID, True)
    card_no = render_card_panel(SID, False)

    chip_yes = render_chip_tile(MUMMY_PRICE, True, zoom=4)
    chip_no = render_chip_tile(MUMMY_PRICE, False, zoom=4)

    # true-1x swatches: mummy price, can't-afford, and the widest "100,000"
    sw = [
        (f"{MUMMY_PRICE} · buy", render_chip_tile(MUMMY_PRICE, True, zoom=1,
                                                  marg=sc.m(6)), (170, 216, 255)),
        (f"{MUMMY_PRICE} · locked", render_chip_tile(MUMMY_PRICE, False, zoom=1,
                                                     marg=sc.m(6)), (150, 158, 172)),
        ("100,000 · widest", render_chip_tile(WIDE_PRICE, True, zoom=1,
                                              marg=sc.m(6)), (232, 224, 246)),
    ]

    lbl_lg = hud_font(18, True)
    lbl_md = hud_font(14, True)
    lbl_sm = hud_font(11, True)
    lbl_xs = hud_font(10, False)

    col_gap = 30
    card_row_w = PANEL_W * 2 + col_gap
    content_w = card_row_w
    canvas_w = MARGIN * 2 + content_w

    y_cards = MARGIN + HDR_H
    y_cardlbl = y_cards + PANEL_H - 2
    y_striplbl = y_cards + PANEL_H + 22
    y_strip = y_striplbl + LBL_H
    strip_h = max(chip_yes.get_height(), chip_no.get_height())
    y_1xlbl = y_strip + strip_h + 24
    y_1x = y_1xlbl + LBL_H
    sw_h = max(t.get_height() for _n, t, _c in sw)
    canvas_h = y_1x + sw_h + 22 + FOOTER_H + MARGIN

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(BG)

    def text(s, font_obj, center, col=(226, 230, 244)):
        img = font_obj.render(s, True, col)
        canvas.blit(img, img.get_rect(center=center))

    text("v5 bold-cipher r2 — obsidian slab, cool numerals ARE the identity (Lever: T)",
         lbl_lg, (canvas_w // 2, MARGIN + HDR_H // 2))

    # hero cards
    cx_yes = MARGIN
    cx_no = MARGIN + PANEL_W + col_gap
    canvas.blit(card_yes, (cx_yes, y_cards))
    canvas.blit(card_no, (cx_no, y_cards))
    text("AFFORDABLE — obsidian", lbl_sm, (cx_yes + PANEL_W // 2, y_cardlbl + 12),
         (150, 220, 255))
    text("CAN'T AFFORD — lifted slate", lbl_sm, (cx_no + PANEL_W // 2, y_cardlbl + 12),
         (150, 158, 172))

    # 4x detail strip
    text("4x DETAIL", lbl_md, (canvas_w // 2, y_striplbl), (150, 156, 178))
    strip_w = chip_yes.get_width() + col_gap + chip_no.get_width()
    sx = (canvas_w - strip_w) // 2
    canvas.blit(chip_yes, (sx, y_strip))
    canvas.blit(chip_no, (sx + chip_yes.get_width() + col_gap, y_strip))

    # true-1x swatch row (gameplay scale) with the widest-case check
    text("TRUE 1x — gameplay scale  ·  width verified vs 100,000", lbl_md,
         (canvas_w // 2, y_1xlbl), (150, 156, 178))
    sw_gap = 34
    sw_total = sum(t.get_width() for _n, t, _c in sw) + sw_gap * (len(sw) - 1)
    tx = (canvas_w - sw_total) // 2
    for title, tile, col in sw:
        canvas.blit(tile, (tx, y_1x + (sw_h - tile.get_height()) // 2))
        lt = lbl_xs.render(title, True, col)
        canvas.blit(lt, (tx + (tile.get_width() - lt.get_width()) // 2,
                         y_1x + sw_h + 4))
        tx += tile.get_width() + sw_gap

    text("obsidian slab, zero hue cast  ·  1.2x oversized numerals, m(2) tracking  ·  "
         "pure-white crown -> cool blue-white foot  ·  locked lifts to cool slate (luma delta)",
         lbl_xs, (canvas_w // 2, canvas_h - MARGIN - FOOTER_H // 2),
         (120, 118, 140))

    out = os.path.join(os.path.dirname(__file__), "..", "docs",
                       "store_card_v5_price_chip_r2", "bold-cipher", "round_2.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
