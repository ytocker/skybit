"""Round-1 render for the `night-enamel-tablet` price-chip concept.

A flat matte dark-enamel nameplate: gold is confined to the coin + numerals,
the body stays quiet and recessive (no gloss, no bevel), and a single crisp
1px gold keyline invites the tap. Corners are a soft m(6) tablet radius rather
than the family's h//2 pill. This script only draws the price chip; it inlines
draw_card() with the state chip swapped so the concept reads in context.
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
        key_col = (220, 190, 100, 200)               # crisp gold keyline
        num_col = (224, 188, 96)                      # warm matte gold numerals
        coin_rim = sc.GOLD_A_COIN_RIM
        key_txt = None
    else:
        stops = [(0.0, (18, 20, 38)), (1.0, (12, 13, 28))]   # body cools slightly
        key_col = (90, 98, 120, 100)                 # keyline drops to quiet slate
        num_col = (190, 196, 210)                     # legible cool grey
        coin_rim = (78, 84, 104)
        key_txt = None
    # flat fill (gloss=0, alpha=255) then a single 1px keyline — no bevel/sheen
    surf.blit(sc.vgrad_stops(r.w, r.h, rad, stops, 255, 1.0), r.topleft)
    pygame.draw.rect(surf, key_col, r, width=max(1, sc.m(1)), border_radius=rad)
    x = r.x + pad
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2, rim=coin_rim)
    x += coin_d + gapc
    sc.plain_text(surf, text, f, (x + nw // 2, cy), num_col, shadow_a=0,
                  weight=sc.m(1.0), keyline=key_txt)
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


def zoom_chip(text, affordable, zoom=4):
    """Draw one chip at native SS then smoothscale up for the detail strip."""
    h = sc.m(20)
    pad = sc.m(6)
    tmp = pygame.Surface((sc.m(400), h + pad * 2), pygame.SRCALPHA)
    r = price_chip_enamel(tmp, sc.m(200), h // 2 + pad, text, h,
                          affordable=affordable)
    crop = pygame.Rect(r.x - pad, 0, r.w + pad * 2, h + pad * 2)
    sub = tmp.subsurface(crop).copy()
    return pygame.transform.smoothscale(sub, (crop.w * zoom, crop.h * zoom))


def main():
    label_lg = hud_font(22, True)
    label_md = hud_font(16, True)
    label_sm = hud_font(13, True)

    # hero card at SS scale (324x200)
    cw, ch = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS
    card = pygame.Surface((cw, ch), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       cw - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
    draw_card_with_chip(card, "skin_mummy", rect, equipped=False, secret=False,
                        affordable=True)

    # zoomed detail chips
    chip_yes = zoom_chip("1,100", True, zoom=4)
    chip_no = zoom_chip("1,100", False, zoom=4)

    margin = 20
    header = 44
    footer = 36
    gap = 34
    strip_w = chip_yes.get_width() + gap + chip_no.get_width()
    content_w = max(cw, strip_w)
    W = content_w + margin * 2
    strip_h = max(chip_yes.get_height(), chip_no.get_height())
    H = (header + ch + gap + 26 + strip_h + footer)

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    def text(surf, s, font_obj, center, col=(232, 236, 248)):
        img = font_obj.render(s, True, col)
        surf.blit(img, img.get_rect(center=center))

    text(canvas, "night-enamel-tablet  ·  price chip  ·  round 1", label_lg,
         (W // 2, header // 2))

    # hero card
    cx0 = (W - cw) // 2
    y = header
    canvas.blit(card, (cx0, y))

    # chip strip
    y = header + ch + gap
    text(canvas, "AFFORDABLE", label_sm, (margin + chip_yes.get_width() // 2, y),
         (150, 214, 150))
    text(canvas, "CAN'T AFFORD", label_sm,
         (W - margin - chip_no.get_width() // 2, y), (214, 158, 158))
    y += 22
    sx = (W - strip_w) // 2
    canvas.blit(chip_yes, (sx, y))
    canvas.blit(chip_no, (sx + chip_yes.get_width() + gap, y))

    text(canvas, "flat matte enamel body  ·  1px gold keyline  ·  m(6) tablet corners",
         label_md, (W // 2, H - footer // 2), (150, 156, 178))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "store_card_v5_price_chip",
                       "night-enamel-tablet", "round_1.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
