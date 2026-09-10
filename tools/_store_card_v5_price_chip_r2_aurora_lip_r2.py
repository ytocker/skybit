"""Round-2 render for the `aurora-lip` price-chip concept (Levers P + C).

The identity is the chip BODY: a full pill (border_radius = h//2) filled with a
vivid two-stop spectral ramp — violet at the crown, cyan at the foot — with the
cream NOT baked into the gradient but seeping in as a separate light element.

r2 fixes the r1 art-director notes:
- the affordable body is now a MANUAL vgrad_stops fill + thin bevel_rim, NOT
  chip_body_stops. chip_body_stops layers a BLEND_ADD gloss sweep that washed
  the ramp toward mono-white and ate the cyan foot entirely; the manual path
  keeps the full spectral violet->cyan visible.
- the cream aurora-lip bloom sits AT the pill top edge (r.top) so it kisses the
  crown instead of floating with a dark gap above it.
- padding is widened so a band of raw spectral colour shows above and below the
  numerals — the ramp is the star, not the glyphs.
- can't-afford keeps chip_body_stops (flat slate, no bloom) where a gloss sweep
  is harmless because there is no ramp to protect.
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


# ── the concept: spectral pill + cream "aurora lip" bloom ─────────────────────
def price_chip_aurora_lip(surf, cx, cy, text, h, affordable=True):
    coin_d = int(h * 0.66)
    pad = sc.m(15)                                   # wider: expose spectral band
    gapc = sc.m(8)                                   # clear gap: coin cell -> digits
    f = sc.font(h * 0.50 / sc.SS)                    # glyphs stay small; ramp is star
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    rad = h // 2                                     # full pill silhouette
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    if affordable:
        # MANUAL body: pure vgrad_stops so the violet->cyan ramp survives intact.
        # chip_body_stops would BLEND_ADD a gloss over this and blow the ramp to
        # white, swallowing the cyan foot — the whole point of the concept.
        fill = sc.vgrad_stops(r.w, r.h, rad,
                              [(0.0, (150, 70, 230)), (1.0, (60, 190, 235))],
                              255, 1.0)
        surf.blit(fill, r.topleft)
        # thin clean rim only — no interior gloss
        sc.bevel_rim(surf, r, rad, (16, 22, 44), (200, 225, 255, 235),
                     w=max(1, sc.m(1)))
        # cream light cresting the crown from above — anchored ON the top edge so
        # it reads as spill-over onto the pill, no dark gap between it and the rim
        sc._alpha_aura(surf, cx, r.top, sc.m(16), (250, 246, 232),
                       peak=60, layers=14)
        num_col = (245, 247, 255)                     # near-white, front-lit
        key_col = (14, 20, 40)                         # violet-tinted keyline
        coin_rim = (78, 84, 104)                       # cool steel
        cool_coin = None
    else:
        # flat desaturated slate, no bloom — colour + light simply gone. Here the
        # gloss sweep is harmless (no ramp to protect), so chip_body_stops stays.
        stops = [(0.0, (70, 78, 100)), (1.0, (44, 50, 70))]
        sc.chip_body_stops(surf, r, rad, stops, (16, 22, 44),
                           (150, 162, 188), gloss=20, gamma=1.02)
        num_col = (145, 152, 172)                       # clearly dimmer than lit
        key_col = (20, 24, 44)
        coin_rim = (78, 84, 104)
        cool_coin = (60, 70, 90, 160)                   # slate tint over the coin
    x = r.x + pad
    ccx = x + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2, rim=coin_rim)
    if cool_coin is not None:
        # coin_glyph() ignores `rim`; overlay a cool tint so the locked coin
        # reads slate-grey rather than warm gold
        cr = coin_d // 2
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, cool_coin, (cr, cr), cr)
        surf.blit(tint, (ccx - cr, cy - cr))
    x += coin_d + gapc
    sc.plain_text(surf, text, f, (x + nw // 2, cy), color=num_col, shadow_a=0,
                  weight=sc.m(1.0), keyline=key_col, kw=sc.m(0.7))
    return r


def draw_card_with_chip(surf, sid, rect, equipped=False, secret=False,
                        affordable=True):
    """draw_card() verbatim, with state_chip() swapped for the aurora-lip chip."""
    m = sc.m
    pal = sc.MYSTERY if secret else sc.RARITY[sc._rarity(sid)]
    rad = m(sc.CARD_RAD)
    sc.drop_shadow(surf, rect, rad, blur=m(8), alpha=160, dy=m(4))
    surf.blit(sc.vgrad(rect.w, rect.h, rad, sc.CARD_T, sc.CARD_B, 252, gamma=1.15),
              rect.topleft)
    sc.top_sheen(surf, rect, rad, m(30), peak=62)
    sc.contact_shadow(surf, rect, rad, m(9), alpha=120)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(surf, rect, rad, sc.CARD_RING_DEEP, (*sc.CARD_RING_BRIGHT, 235),
                 w=max(1, m(2.0)))
    tray = rect.inflate(-m(7), -m(7))
    trad = rad - m(4)
    pygame.draw.rect(surf, (10, 10, 24, 200), tray.inflate(m(2), m(2)),
                     width=max(1, m(1)), border_radius=trad + m(1))
    pygame.draw.rect(surf, (*sc.CARD_RING_BRIGHT, 90), tray, width=max(1, m(1)),
                     border_radius=trad)
    cx, cy = rect.centerx, rect.y + m(sc.CY_DISC) + sc._DOME_DY
    sc.soft_glow(surf, cx, cy, sc._DOME_R + m(3), pal["glow"], 30, layers=8)
    sc.cabochon(surf, cx, cy, sc._DOME_R, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    if secret:
        sc._draw_qmark(surf, cx, cy, sc._DOME_R + m(6), sc.CREAM, sc.NEAR_BLACK,
                       thick=m(2))
        name = "???"
    else:
        name = sc._name(sid)
    sc.cabochon_glass(surf, cx, cy, sc._DOME_R, tint=pal["gem"])
    if not secret:
        sc.blit_thumb(surf, sid, cx, cy - sc._ITEM_DY, sc._BOX_PX)
    sc.facet_gem(surf, rect.right - m(19), rect.y + m(19), m(sc.GEM_R + 3),
                 pal["gem"], pal["deep"], mystery=secret)
    tier_word = "MYSTERY" if secret else sc._rarity(sid).upper()
    sc._ribbon_lozenge(surf, tier_word, cx, rect.y + m(55) - sc._RIBN_DY,
                       rect.w - m(34), pal)
    sc._name_on(surf, name, cx, rect.y + m(70), rect.w - m(26))
    if equipped:
        sc.status_chip(surf, cx, rect.y + m(88) - sc._CHIP_DY, "EQUIPPED", m(20),
                       kind="equipped")
    else:
        price = f"{sc._cost(sid):,}"
        price_chip_aurora_lip(surf, cx, rect.y + m(88) - sc._CHIP_DY, price, m(20),
                              affordable=affordable)


def chip_native(text, affordable):
    """Draw one chip at native SS onto a tight cropped surface."""
    h = sc.m(20)
    pad = sc.m(6)
    tmp = pygame.Surface((sc.m(400), h + pad * 2), pygame.SRCALPHA)
    r = price_chip_aurora_lip(tmp, sc.m(200), h // 2 + pad, text, h,
                              affordable=affordable)
    crop = pygame.Rect(r.x - pad, 0, r.w + pad * 2, h + pad * 2)
    return tmp.subsurface(crop).copy()


def zoom_chip(text, affordable, zoom=4):
    sub = chip_native(text, affordable)
    return pygame.transform.smoothscale(
        sub, (sub.get_width() * zoom, sub.get_height() * zoom))


def true1x_chip(text, affordable):
    """The chip at actual gameplay logical size (SS downscaled to 1x)."""
    sub = chip_native(text, affordable)
    w = max(1, round(sub.get_width() / sc.SS))
    h = max(1, round(sub.get_height() / sc.SS))
    return pygame.transform.smoothscale(sub, (w, h))


def main():
    label_lg = hud_font(22, True)
    label_md = hud_font(16, True)
    label_sm = hud_font(13, True)

    cw, ch = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS

    def hero(affordable):
        card = pygame.Surface((cw, ch), pygame.SRCALPHA)
        rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                           cw - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
        draw_card_with_chip(card, SID, rect, equipped=False, secret=False,
                            affordable=affordable)
        return card

    card_yes = hero(True)
    card_no = hero(False)

    chip_yes = zoom_chip("1,100", True, zoom=4)
    chip_no = zoom_chip("1,100", False, zoom=4)

    t1_yes = true1x_chip("1,100", True)
    t1_no = true1x_chip("1,100", False)
    t1_wide = true1x_chip("14,500", True)

    MARGIN = 20
    HDR_H = 44
    footer = 34
    col_gap = 30
    card_row_w = cw + col_gap + cw
    W = card_row_w + MARGIN * 2

    def text(surf, s, font_obj, center, col=(232, 236, 248)):
        img = font_obj.render(s, True, col)
        surf.blit(img, img.get_rect(center=center))

    y_cards = HDR_H
    y_striplbl = y_cards + ch + 26
    y_strip = y_striplbl + 20
    strip_h = max(chip_yes.get_height(), chip_no.get_height())
    y_1xlbl = y_strip + strip_h + 24
    y_1x = y_1xlbl + 20
    t1_h = max(t1_yes.get_height(), t1_no.get_height(), t1_wide.get_height())
    H = y_1x + t1_h + footer

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    text(canvas, f"v5 price-chip r2 — aurora-lip r2 — {SID} EPIC — P+C",
         label_lg, (W // 2, HDR_H // 2))

    cx_yes = MARGIN
    cx_no = MARGIN + cw + col_gap
    canvas.blit(card_yes, (cx_yes, y_cards))
    canvas.blit(card_no, (cx_no, y_cards))
    text(canvas, "AFFORDABLE", label_sm, (cx_yes + cw // 2, y_cards + ch + 12),
         (150, 214, 150))
    text(canvas, "CAN'T AFFORD", label_sm, (cx_no + cw // 2, y_cards + ch + 12),
         (214, 158, 158))

    # 4x detail strip on a card-body gradient patch — judged on shipping ground
    text(canvas, "4× DETAIL (on card-body gradient)", label_md,
         (W // 2, y_striplbl), (150, 156, 178))
    strip_w = chip_yes.get_width() + col_gap + chip_no.get_width()
    sx = (W - strip_w) // 2
    patch_pad = 18
    patch = pygame.Rect(sx - patch_pad, y_strip - patch_pad // 2,
                        strip_w + patch_pad * 2, strip_h + patch_pad)
    canvas.blit(sc.vgrad(patch.w, patch.h, sc.m(sc.CARD_RAD), sc.CARD_T,
                         sc.CARD_B, 255, gamma=1.15), patch.topleft)
    pygame.draw.rect(canvas, (*sc.CARD_RING_BRIGHT, 90), patch,
                     width=1, border_radius=sc.m(sc.CARD_RAD))
    canvas.blit(chip_yes, (sx, y_strip))
    canvas.blit(chip_no, (sx + chip_yes.get_width() + col_gap, y_strip))

    text(canvas, "TRUE 1× (gameplay scale) — affordable · locked · wide case",
         label_md, (W // 2, y_1xlbl), (150, 156, 178))
    t1_gap = 36
    t1_w = (t1_yes.get_width() + t1_gap + t1_no.get_width() + t1_gap
            + t1_wide.get_width())
    tx = (W - t1_w) // 2
    canvas.blit(t1_yes, (tx, y_1x + (t1_h - t1_yes.get_height()) // 2))
    tx += t1_yes.get_width() + t1_gap
    canvas.blit(t1_no, (tx, y_1x + (t1_h - t1_no.get_height()) // 2))
    tx += t1_no.get_width() + t1_gap
    canvas.blit(t1_wide, (tx, y_1x + (t1_h - t1_wide.get_height()) // 2))

    text(canvas,
         "manual vgrad spectral body (no gloss blowout)  ·  cream bloom kisses "
         "the crown  ·  wider pad exposes the ramp  ·  locked = flat slate, no bloom",
         label_sm, (W // 2, H - footer // 2), (150, 156, 178))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "store_card_v5_price_chip_r2",
                       "aurora-lip", "round_2.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
