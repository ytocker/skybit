"""Round-1 render for the `split-cream` price-chip concept (r3, Lever C).

The identity is the NUMERALS, not the body: the chip body stays a genuinely
dark near-black obsidian pill (no halo, no bloom, no additive light — that would
wash the body), and all the drama is a two-tone cream->amber gradient poured
into the digit glyphs. A tight 0.48->0.52 stop band forges a crisp horizontal
seam so the top of each numeral reads cream-lit and the foot deep gold, as if a
single hard light grazes the lettering. A thin warm keyline defines the pill
edge. Can't-afford drops the two-tone entirely for flat muted gold, and dims the
keyline + tints the coin cool — so wealth reads as struck-light lettering and
poverty as the same digits gone dull.
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


# ── the concept: dark obsidian pill + struck-light two-tone numerals ──────────
def price_chip_split_cream(surf, cx, cy, text, h, affordable=True):
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)                                   # clear gap: coin cell -> digits
    f = sc.font(h * 0.50 / sc.SS)                     # DEFAULT size — the seam works
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    rad = h // 2                                     # full pill silhouette
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    if affordable:
        # near-black body: gradient stays dark, gloss kept very low so nothing
        # near the pill can read as glow — the light lives ONLY in the digits
        stops = [(0.0, (12, 13, 22)), (1.0, (34, 37, 56))]
        sc.chip_body_stops(surf, r, rad, stops, (8, 10, 20), (60, 65, 100),
                           gloss=12, gamma=1.04)
        # warm keyline: a thin struck edge, defined by alpha not additive light
        sc.bevel_rim(surf, r, rad, (120, 90, 30, 180), (255, 230, 150, 150), w=1)
        coin_rim = (180, 150, 60)
        cool_coin = None
    else:
        stops = [(0.0, (10, 11, 20)), (1.0, (26, 28, 44))]
        sc.chip_body_stops(surf, r, rad, stops, (8, 10, 20), (60, 65, 100),
                           gloss=12, gamma=1.04)
        sc.bevel_rim(surf, r, rad, (120, 90, 30, 180), (255, 230, 150, 80), w=1)
        coin_rim = (120, 110, 80)
        cool_coin = (60, 70, 90, 140)                # slate tint over the coin
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
    nx = x + nw // 2
    if affordable:
        # gradient poured into the glyph MASK only — multiplied into the alpha
        # stamp so the ramp never bleeds onto the body. The tight 0.48->0.52
        # band is the horizontal seam: cream crown, deep-gold foot.
        mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(1.0))
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              [(0.0, (255, 246, 205)), (0.48, (250, 230, 150)),
                               (0.52, (226, 168, 66)), (1.0, (178, 124, 34))],
                              255, 1.0)
        img = mask.copy()
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, img.get_rect(center=(nx, cy)))
    else:
        sc.plain_text(surf, text, f, (nx, cy), color=(150, 140, 110),
                      shadow_a=0, weight=sc.m(1.0))
    return r


def draw_card_with_chip(surf, sid, rect, equipped=False, secret=False,
                        affordable=True):
    """draw_card() verbatim, with state_chip() swapped for the split-cream chip."""
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
        price_chip_split_cream(surf, cx, rect.y + m(88) - sc._CHIP_DY, price,
                               m(20), affordable=affordable)


def chip_native(text, affordable):
    """Draw one chip at native SS onto a tight cropped surface."""
    h = sc.m(20)
    pad = sc.m(6)
    tmp = pygame.Surface((sc.m(400), h + pad * 2), pygame.SRCALPHA)
    r = price_chip_split_cream(tmp, sc.m(200), h // 2 + pad, text, h,
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
    t1_h = max(t1_yes.get_height(), t1_no.get_height())
    H = y_1x + t1_h + footer

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    text(canvas, f"v5 price-chip r3 — split-cream r1 — {SID} EPIC — C(gradient)",
         label_lg, (W // 2, HDR_H // 2))

    cx_yes = MARGIN
    cx_no = MARGIN + cw + col_gap
    canvas.blit(card_yes, (cx_yes, y_cards))
    canvas.blit(card_no, (cx_no, y_cards))
    text(canvas, "AFFORDABLE", label_sm, (cx_yes + cw // 2, y_cards + ch + 12),
         (150, 214, 150))
    text(canvas, "CAN'T AFFORD", label_sm, (cx_no + cw // 2, y_cards + ch + 12),
         (214, 158, 158))

    # 4x detail strip on a card-body gradient patch — judge the chip on the
    # same ground it ships on (not a flat swatch)
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

    text(canvas, "TRUE 1× (gameplay scale)", label_md, (W // 2, y_1xlbl),
         (150, 156, 178))
    t1_gap = 40
    t1_w = t1_yes.get_width() + t1_gap + t1_no.get_width()
    tx = (W - t1_w) // 2
    canvas.blit(t1_yes, (tx, y_1x + (t1_h - t1_yes.get_height()) // 2))
    canvas.blit(t1_no, (tx + t1_yes.get_width() + t1_gap,
                        y_1x + (t1_h - t1_no.get_height()) // 2))

    text(canvas,
         "dark obsidian body  ·  cream-top/amber-foot digit gradient  ·  "
         "warm gold keyline  ·  locked = muted gold flat",
         label_sm, (W // 2, H - footer // 2), (150, 156, 178))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "store_card_v5_price_chip_r3",
                       "split-cream", "round_1.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
