"""Round-2 render for the `night-enamel-tablet` price-chip concept.

Round-1 held the identity (flat matte enamel, gold confined to coin + numerals,
m(6) tablet corners, no gloss). Round 2 lands the state-legibility fixes the art
director flagged: the locked chip must READ locked without leaning on hue alone.

  1. The locked coin is cooled with an explicit slate overlay — coin_glyph()
     ignores its rim arg, so a cool tint is composited over the coin face.
  2. The whole locked plate recedes via clearly cooler/darker body stops.
  3. Locked numerals dim to a cool grey (value delta, colourblind-safe).
  4. The affordable keyline commits to a brighter true gold as the tap CTA.
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


# ── the concept: flat matte enamel tablet price chip ──────────────────────────
def price_chip_enamel(surf, cx, cy, text, h, affordable=True):
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)                                   # clear gap: coin cell -> digits
    f = sc.font(h * 0.50 / sc.SS)
    nw = sc._glyph_base(text, f, 0).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    rad = sc.m(6)                                    # soft tablet corner, NOT h//2
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    if affordable:
        stops = [(0.0, (20, 22, 40)), (1.0, (14, 15, 30))]   # flat matte enamel
        # option (a): a brighter true-gold keyline as the tap affordance
        key_col = (228, 196, 110, 235)
        num_col = (224, 188, 96)                      # warm matte gold numerals
        coin_rim = sc.GOLD_A_COIN_RIM
        cool_coin = None
    else:
        # locked plate recedes as a whole: clearly cooler + darker enamel
        stops = [(0.0, (14, 15, 28)), (1.0, (10, 11, 22))]
        key_col = (90, 98, 120, 100)                 # keyline drops to quiet slate
        num_col = (150, 156, 170)                     # dimmer cool grey (value delta)
        coin_rim = (78, 84, 104)
        cool_coin = (60, 70, 90, 160)                 # slate tint over the gold coin
    # flat fill (gloss=0, alpha=255) then a single 1px keyline — no bevel/sheen
    surf.blit(sc.vgrad_stops(r.w, r.h, rad, stops, 255, 1.0), r.topleft)
    pygame.draw.rect(surf, key_col, r, width=max(1, sc.m(1)), border_radius=rad)
    x = r.x + pad
    ccx = x + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2, rim=coin_rim)
    if cool_coin is not None:
        # coin_glyph() ignores `rim`; overlay a cool desaturating tint so the
        # locked coin reads slate-grey rather than warm gold
        cr = coin_d // 2
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, cool_coin, (cr, cr), cr)
        surf.blit(tint, (ccx - cr, cy - cr))
    x += coin_d + gapc
    sc.plain_text(surf, text, f, (x + nw // 2, cy), num_col, shadow_a=0,
                  weight=sc.m(1.0), keyline=None)
    return r


def draw_card_with_chip(surf, sid, rect, equipped=False, secret=False,
                        affordable=True):
    """draw_card() verbatim, with state_chip() swapped for the enamel chip."""
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
    # SWAP: the enamel-tablet price chip in place of state_chip()
    if equipped:
        sc.status_chip(surf, cx, rect.y + m(88) - sc._CHIP_DY, "EQUIPPED", m(20),
                       kind="equipped")
    else:
        price = f"{sc._cost(sid):,}"
        price_chip_enamel(surf, cx, rect.y + m(88) - sc._CHIP_DY, price, m(20),
                          affordable=affordable)


def chip_native(text, affordable):
    """Draw one chip at native SS onto a tight cropped surface."""
    h = sc.m(20)
    pad = sc.m(6)
    tmp = pygame.Surface((sc.m(400), h + pad * 2), pygame.SRCALPHA)
    r = price_chip_enamel(tmp, sc.m(200), h // 2 + pad, text, h,
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

    # two hero cards at SS scale (324x200): affordable + can't-afford
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

    # zoomed detail chips
    chip_yes = zoom_chip("1,100", True, zoom=4)
    chip_no = zoom_chip("1,100", False, zoom=4)

    # true-1x swatches
    t1_yes = true1x_chip("1,100", True)
    t1_no = true1x_chip("1,100", False)

    margin = 22
    header = 44
    footer = 34
    col_gap = 30
    card_row_w = cw + col_gap + cw
    W = card_row_w + margin * 2

    def text(surf, s, font_obj, center, col=(232, 236, 248)):
        img = font_obj.render(s, True, col)
        surf.blit(img, img.get_rect(center=center))

    # layout math for total height
    y_cards = header
    y_striplbl = y_cards + ch + 26
    y_strip = y_striplbl + 20
    strip_h = max(chip_yes.get_height(), chip_no.get_height())
    y_1xlbl = y_strip + strip_h + 24
    y_1x = y_1xlbl + 20
    t1_h = max(t1_yes.get_height(), t1_no.get_height())
    H = y_1x + t1_h + footer

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    text(canvas, f"v5 night-enamel-tablet r2 — {SID} — state fix + keyline",
         label_lg, (W // 2, header // 2))

    # hero cards side by side
    cx_yes = margin
    cx_no = margin + cw + col_gap
    canvas.blit(card_yes, (cx_yes, y_cards))
    canvas.blit(card_no, (cx_no, y_cards))
    text(canvas, "AFFORDABLE", label_sm, (cx_yes + cw // 2, y_cards + ch + 12),
         (150, 214, 150))
    text(canvas, "CAN'T AFFORD", label_sm, (cx_no + cw // 2, y_cards + ch + 12),
         (214, 158, 158))

    # 4x zoom detail strip
    text(canvas, "4× DETAIL", label_md, (W // 2, y_striplbl), (150, 156, 178))
    strip_w = chip_yes.get_width() + col_gap + chip_no.get_width()
    sx = (W - strip_w) // 2
    canvas.blit(chip_yes, (sx, y_strip))
    canvas.blit(chip_no, (sx + chip_yes.get_width() + col_gap, y_strip))

    # true-1x legibility row
    text(canvas, "TRUE 1× (gameplay scale)", label_md, (W // 2, y_1xlbl),
         (150, 156, 178))
    t1_gap = 40
    t1_w = t1_yes.get_width() + t1_gap + t1_no.get_width()
    tx = (W - t1_w) // 2
    canvas.blit(t1_yes, (tx, y_1x + (t1_h - t1_yes.get_height()) // 2))
    canvas.blit(t1_no, (tx + t1_yes.get_width() + t1_gap,
                        y_1x + (t1_h - t1_no.get_height()) // 2))

    text(canvas,
         "cool-slate locked coin  ·  recessed dark enamel  ·  dim grey numerals"
         "  ·  true-gold CTA keyline",
         label_sm, (W // 2, H - footer // 2), (150, 156, 178))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "store_card_v5_price_chip",
                       "night-enamel-tablet", "round_2.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
