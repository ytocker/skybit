"""Fusion of concepts A + B: dark obsidian body, B's cream→amber gradient and
chip keyline, B's default numeral size, plus a dark-amber outline ring around
each digit glyph so each character reads as a struck letterform.

Body:    A's obsidian (12,13,22)→(34,37,56) — same dark ground as both A & B
Size:    B's h*0.50 default — smaller, fits neatly in the pill
Colors:  B's 4-stop cream→amber with tight 0.48/0.52 seam
Chip rim: B's thin warm keyline (bevel_rim w=1) on top of the standard bevel
Digits:  new — dark warm-amber outline blit at 8 neighbour offsets before the
         gradient fill, so each numeral has a visible perimeter that lifts it
         off the dark body without adding any light to the chip surface.
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


# ── corrected chip body (BLEND_ADD-safe gloss) ────────────────────────────────
def _gloss_corrected(surf, rect, radius, peak):
    """Premultiplied gloss: draws (a,a,a,255) so BLEND_ADD adds correct amount."""
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        a = int(peak * (1 - y / h) ** 2.4)
        pygame.draw.line(sweep, (a, a, a, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


def dark_chip_body(surf, r, radius, stops, rim_dark, rim_bright_3tup,
                   gloss=12, gamma=1.04):
    """chip_body_stops replacement with corrected gloss. rim_bright_3tup = 3-tuple."""
    sc.drop_shadow(surf, r, radius, blur=sc.m(4), alpha=110, dy=sc.m(2))
    surf.blit(sc.vgrad_stops(r.w, r.h, radius, stops, 255, gamma=gamma), r.topleft)
    _gloss_corrected(surf, r, radius, peak=gloss)
    sc.contact_shadow(surf, r, radius, sc.m(3), alpha=80)
    pygame.draw.rect(surf, rim_dark, r, width=max(1, sc.m(1.6)), border_radius=radius)
    sc.bevel_rim(surf, r, radius, rim_dark, (*rim_bright_3tup, 235),
                 w=max(1, sc.m(1.5)))


# ── numeral constants ─────────────────────────────────────────────────────────
# Gradient identical to B: tight cream→amber seam mapped to glyph bounding rect
NUM_STOPS = [(0.0, (255, 244, 196)), (0.48, (250, 228, 148)),
             (0.52, (224, 164, 62)),  (1.0, (210, 150, 60))]
# Outline: dark warm amber — darker than numerals, slightly warmer than body
OUTLINE_COLOR = (85, 58, 14)
# Tracking: extra device-px gap inserted between each character pair
TRACKING = sc.m(2)


def _draw_numerals(surf, nx, cy, text, f):
    """Render gradient numerals with a 2-ring dark-amber outline at each glyph."""
    mask = sc._stamp_bold(sc._glyph_base(text, f, TRACKING), sc.m(1.0))
    bb = mask.get_bounding_rect()

    # 2-ring outline: outer ±2px pass first, then inner ±1px pass on top so the
    # combined ring is ~2 device px wide on every digit edge — no additive light.
    outline = mask.copy()
    tint_s = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
    tint_s.fill((*OUTLINE_COLOR, 255))
    outline.blit(tint_s, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)]:
        surf.blit(outline, outline.get_rect(center=(nx + ox, cy + oy)))
    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        surf.blit(outline, outline.get_rect(center=(nx + ox, cy + oy)))

    # gradient fill: mapped to the glyph bounding rect so the cream crown lands
    # on the actual top stroke, not on the transparent padding above.
    grad = sc.vgrad_stops(mask.get_width(), max(1, bb.height), 0,
                          NUM_STOPS, 255, 1.0)
    img = mask.copy()
    img.blit(grad, (0, bb.top), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, img.get_rect(center=(nx, cy)))


def price_chip_fusion(surf, cx, cy, text, h, affordable=True):
    coin_d = int(h * 0.66)
    pad = sc.m(13)
    gapc = sc.m(8)
    f = sc.font(h * 0.50 / sc.SS)                       # B's default size
    nw = sc._glyph_base(text, f, TRACKING).get_width() + sc.m(2)
    w = pad + coin_d + gapc + nw + pad
    rad = h // 2
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    if affordable:
        stops = [(0.0, (12, 13, 22)), (1.0, (34, 37, 56))]
    else:
        stops = [(0.0, (9, 10, 17)), (1.0, (24, 26, 40))]

    dark_chip_body(surf, r, rad, stops, (8, 10, 20), (60, 65, 100),
                   gloss=12, gamma=1.04)
    # Uniform warm gold ring drawn via SRCALPHA so it wraps the bottom arc equally
    # — sc.bevel_rim fades to zero at the bottom arc, leaving it invisible.
    rim_a = 160 if affordable else 80
    rim_surf = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    pygame.draw.rect(rim_surf, (220, 170, 60, rim_a), rim_surf.get_rect(),
                     width=max(1, sc.m(1)), border_radius=rad)
    surf.blit(rim_surf, r.topleft)

    ccx = r.x + pad + coin_d // 2
    sc.coin_glyph(surf, ccx, cy, coin_d // 2)
    if not affordable:
        cr = coin_d // 2
        tint = pygame.Surface((coin_d, coin_d), pygame.SRCALPHA)
        pygame.draw.circle(tint, (70, 74, 84, 180), (cr, cr), cr)
        surf.blit(tint, (ccx - cr, cy - cr))

    nx = r.x + pad + coin_d + gapc + nw // 2
    if affordable:
        _draw_numerals(surf, nx, cy, text, f)
    else:
        sc.plain_text(surf, text, f, (nx, cy), color=(150, 140, 110),
                      shadow_a=0, weight=sc.m(1.0))
    return r


def draw_card_with_chip(surf, sid, rect, equipped=False, secret=False,
                        affordable=True):
    """draw_card() verbatim, with state_chip() swapped for the fusion chip."""
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
        return None
    price = f"{sc._cost(sid):,}"
    return price_chip_fusion(surf, cx, rect.y + m(88) - sc._CHIP_DY, price,
                             m(20), affordable=affordable)


def chip_native(text, affordable):
    h = sc.m(20)
    pad = sc.m(6)
    tmp = pygame.Surface((sc.m(400), h + pad * 2), pygame.SRCALPHA)
    r = price_chip_fusion(tmp, sc.m(200), h // 2 + pad, text, h,
                          affordable=affordable)
    crop = pygame.Rect(r.x - pad, 0, r.w + pad * 2, h + pad * 2)
    return tmp.subsurface(crop).copy()


def zoom_chip(text, affordable, zoom=4):
    sub = chip_native(text, affordable)
    return pygame.transform.smoothscale(
        sub, (sub.get_width() * zoom, sub.get_height() * zoom))


def true1x_chip(text, affordable):
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
        card = pygame.Surface((cw, ch + 16), pygame.SRCALPHA)
        rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                           cw - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
        r = draw_card_with_chip(card, SID, rect, equipped=False, secret=False,
                                affordable=affordable)
        # body-dark assertion: sample in the gap between coin and numerals
        coin_d = int(sc.m(20) * 0.66)
        bx = r.x + sc.m(13) + coin_d + sc.m(8) // 2
        by = rect.y + sc.m(88) - sc._CHIP_DY
        px = card.get_at((bx, by))
        assert px[0] < 60 and px[1] < 60 and px[2] < 90, \
            f"Body blown! {tuple(px[:3])}"
        print(f"body ({'aff' if affordable else 'lock'}): {tuple(px[:3])}")
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
    y_striplbl = y_cards + ch + 42
    y_strip = y_striplbl + 20
    strip_h = max(chip_yes.get_height(), chip_no.get_height())
    y_1xlbl = y_strip + strip_h + 24
    y_1x = y_1xlbl + 20
    t1_h = max(t1_yes.get_height(), t1_no.get_height())
    H = y_1x + t1_h + footer

    canvas = pygame.Surface((W, H))
    canvas.fill((8, 8, 20))

    text(canvas,
         f"v5 price-chip r3 — fusion (A+B) r1 — {SID} EPIC — dark body / cream-amber / outlined digits",
         label_lg, (W // 2, HDR_H // 2))

    cx_yes = MARGIN
    cx_no = MARGIN + cw + col_gap
    canvas.blit(card_yes, (cx_yes, y_cards))
    canvas.blit(card_no, (cx_no, y_cards))
    text(canvas, "AFFORDABLE", label_sm, (cx_yes + cw // 2, y_cards + ch + 12),
         (150, 214, 150))
    text(canvas, "CAN'T AFFORD", label_sm, (cx_no + cw // 2, y_cards + ch + 12),
         (214, 158, 158))

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
         "A body + B size/gradient/keyline + outlined digits (dark-amber ring per stroke)",
         label_sm, (W // 2, H - footer // 2), (150, 156, 178))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "store_card_v5_price_chip_r3",
                       "fusion", "round_1.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("wrote", out, canvas.get_size())


if __name__ == "__main__":
    main()
