"""Round-2 render sheet for the header-rail store-card price redesign.

Round 1 (a single name-left + price-right rail) was re-rolled: ~13% of catalog
names (TEMPEST CONDOR, MANTIS SHRIMP, FLYING TOASTER, ...) shrank the shared
row to an unreadable 3.75px at 1x. R2 answers with a STACKED-HEADER badge: a
compact dark-enamel plaque in the card's upper-LEFT corner (clear of the crest
gem top-right) that stacks the price on its OWN row above a smaller, ellipsis-
capped name row. Because the badge width is fixed, the name is always bounded
and the price is always fully readable — the overflow class is designed out.

Monkey-patches store_cards.state_chip so it can see `sid` (needed for the name
line). Renders four cards (EPIC + LEGENDARY, affordable + locked), two stress
cards (the longest catalog names) to prove the ellipsis, and a 4x zoom of two
badges so the coin, gold-vs-pewter numerals and rim detail can be judged.
Review-only tooling — never imported by the game.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.hud import _font as hud_font


# ── badge geometry (device px on the 324x200 author buffer) ───────────────────
# Upper-LEFT plaque, fixed width so it ALWAYS ends well clear of the crest gem
# (gem bbox starts ~x252). A fixed width is the whole idea: the name row can
# never overflow because it is measured against a constant budget.
BADGE = pygame.Rect(12, 14, 140, 40)
BADGE_RAD = 10
INNER_X = 22                     # left content margin inside the plaque
COIN_R = 7
ROW1_CY = 27                     # price row centre
ROW2_CY = 44                     # name row centre
NAME_MAX = 120                   # name budget — truncated with an ellipsis past it

PEWTER = (150, 150, 168)         # locked numerals + name (desaturated, readable)
NUM_SHADOW = (6, 6, 16)

# Affordability is read from store_data.balance(); forcing it here lets one card
# render affordable and its twin locked without touching the real wallet.
_FORCE_BALANCE = [10 ** 9]


def _ellipsis(font_obj):
    """Prefer a real ellipsis glyph, but the shipped bold ttf may lack it — fall
    back to three periods so the truncation mark always paints."""
    return "…" if font_obj.size("…")[0] > sc.m(2) else "..."


def _fit_name(name, font_obj, maxw):
    """Single line, truncated with an ellipsis so its rendered width never
    exceeds the badge's fixed name budget."""
    if sc._glyph_base(name, font_obj, 0).get_width() <= maxw:
        return name
    ell = _ellipsis(font_obj)
    s = name
    while s and sc._glyph_base(s + ell, font_obj, 0).get_width() > maxw:
        s = s[:-1]
    return (s.rstrip() + ell) if s else ell


def _price_row(surf, text, affordable):
    """Row 1: the in-game coin + affordability-tinted price numerals, on their
    OWN full-width row so the price is always legible regardless of the name."""
    coin_rim = (180, 150, 60) if affordable else (120, 108, 78)
    coin_cx = INNER_X + COIN_R
    sc.coin_glyph(surf, coin_cx, ROW1_CY, COIN_R, rim=coin_rim)
    if not affordable:
        tint = pygame.Surface((COIN_R * 2, COIN_R * 2), pygame.SRCALPHA)
        pygame.draw.circle(tint, (70, 74, 84, 170), (COIN_R, COIN_R), COIN_R)
        surf.blit(tint, (coin_cx - COIN_R, ROW1_CY - COIN_R))

    f = sc.font(9)
    mask = sc._stamp_bold(sc._glyph_base(text, f, 0), sc.m(0.8))
    img = mask.copy()
    if affordable:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        img.fill((*PEWTER, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = img.get_rect()
    r.left = coin_cx + COIN_R + sc.m(3)
    r.centery = ROW1_CY
    sh = mask.copy()
    sh.fill((*NUM_SHADOW, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(130)
    surf.blit(sh, (r.x, r.y + sc.m(1)))
    surf.blit(img, r.topleft)


def _name_row(surf, name, affordable):
    """Row 2: the item name at a smaller size, ellipsis-capped to NAME_MAX so it
    can never bleed toward the crest gem — the exact failure that sank R1."""
    f = sc.font(7)
    txt = _fit_name(name, f, NAME_MAX)
    col = sc.GOLD_PALE if affordable else PEWTER
    w = sc._glyph_base(txt, f, 0).get_width()
    sc.plain_text(surf, txt, f, (INNER_X + w // 2, ROW2_CY), col,
                  shadow_a=150, weight=sc.m(0.7))


def _equipped_badge(surf):
    """Owned + active state: a mint check + EQUIPPED on row 1, keeping the same
    plaque so the three states read as one family."""
    ink = (100, 224, 150)
    ck = INNER_X
    pygame.draw.lines(surf, ink, False,
                      [(ck, ROW1_CY + sc.m(1)),
                       (ck + sc.m(4), ROW1_CY + sc.m(5)),
                       (ck + sc.m(11), ROW1_CY - sc.m(6))], max(1, sc.m(2.4)))
    f = sc.font(8)
    lw = sc._glyph_base("EQUIPPED", f, 0).get_width()
    sc.plain_text(surf, "EQUIPPED", f,
                  (ck + sc.m(15) + lw // 2, ROW1_CY), ink,
                  shadow_a=0, weight=sc.m(0.8))


def my_state_chip(surf, sid, cx, cy, equipped, secret, h, variant=sc.PRICE_VARIANT):
    """STACKED-HEADER badge in the card's upper-left. Ignores the incoming
    cx/cy (which target the old bottom chip lane) — the plaque always banners
    the top-left corner, clear of the top-right crest gem."""
    affordable = sc.store_data.balance() >= sc._cost(sid)
    sc._dark_chip_body(surf, BADGE, BADGE_RAD,
                       [(0.0, (28, 22, 36)), (1.0, (18, 14, 26))],
                       (10, 11, 22), (48, 44, 62), gloss=14, gamma=1.04)
    # Rim carries the affordability read too: warm gold when buyable, cool steel
    # when locked — a second, colour-independent cue alongside the numeral tint.
    if affordable:
        sc.bevel_rim(surf, BADGE, BADGE_RAD, (120, 88, 28, 235),
                     (230, 200, 130, 220), w=2)
    else:
        sc.bevel_rim(surf, BADGE, BADGE_RAD, (58, 62, 78, 220),
                     (150, 158, 178, 200), w=2)

    if equipped:
        _equipped_badge(surf)
        _name_row(surf, "???" if secret else sc._name(sid), True)
        return BADGE

    _price_row(surf, f"{sc._cost(sid):,}", affordable)
    _name_row(surf, "???" if secret else sc._name(sid), affordable)
    return BADGE


sc.state_chip = my_state_chip   # monkey-patch BEFORE any draw_card call


def render_card(sid, equipped, affordable):
    """Full 324x200 author-res card with the stacked header badge wired in."""
    _FORCE_BALANCE[0] = 10 ** 9 if affordable else 0
    surf = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                       sc.CARD_H * sc.SS - 2 * sc.m(sc._INSET))
    # secret=False on every card so the stress names actually render (jet_fighter
    # is a masked catalog entry) — we are reviewing the price treatment, not the
    # reveal state.
    sc.draw_card(surf, sid, rect, equipped=equipped, secret=False,
                 variant=sc.PRICE_VARIANT)
    return surf


def main():
    sc.store_data.balance = lambda: _FORCE_BALANCE[0]

    out_dir = "/home/user/skybit/docs/store_price_redesign/header-rail"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

    row1 = [
        ("skin_mummy",   "EPIC affordable",   True),
        ("skin_mummy",   "EPIC locked",       False),
        ("skin_kitsune", "LEG. affordable",   True),
        ("skin_kitsune", "LEG. locked",       False),
    ]
    row2 = [
        ("skin_tempest",     "TEMPEST CONDOR  locked", False),
        ("skin_jet_fighter", "JET FIGHTER  affordable", True),
    ]

    pad, gap = 20, 12
    lbl_h = 20
    cw, ch = sc.CARD_W, sc.CARD_H     # displayed at 1x (162x100)

    header_h = 40
    row1_y = header_h + pad
    row1_w = cw * 4 + gap * 3

    row2_y = row1_y + ch + lbl_h + gap * 2
    row2_w = cw * 2 + gap

    # Row 3 — 4x zoom of the top-left badge (80x44 crop -> 320x176).
    crop = pygame.Rect(8, 10, 80, 44)
    zw, zh = crop.w * 4, crop.h * 4
    zooms = [("skin_kitsune", "4x badge — LEGENDARY affordable", True),
             ("skin_tempest", "4x badge — TEMPEST locked",       False)]
    row3_y = row2_y + ch + lbl_h + gap * 2
    row3_w = zw * 2 + gap

    content_w = max(row1_w, row2_w, row3_w)
    canvas_w = pad * 2 + content_w
    canvas_h = row3_y + zh + lbl_h + pad
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(30, True)
    lf = hud_font(15)
    canvas.blit(hf.render("store price — header-rail  r2  (stacked-header)",
                          True, (236, 232, 250)), (pad, pad // 2 + 2))

    def place_cards(specs, y, block_w):
        x = pad + (content_w - block_w) // 2
        for sid, label, afford in specs:
            big = render_card(sid, equipped=False, affordable=afford)
            card = pygame.transform.smoothscale(big, (cw, ch))
            canvas.blit(card, (x, y))
            lbl = lf.render(label, True, (208, 204, 224))
            canvas.blit(lbl, (x + (cw - lbl.get_width()) // 2, y + ch + 3))
            x += cw + gap

    place_cards(row1, row1_y, row1_w)
    place_cards(row2, row2_y, row2_w)

    zx = pad + (content_w - row3_w) // 2
    for sid, label, afford in zooms:
        big = render_card(sid, equipped=False, affordable=afford)
        sub = big.subsurface(crop).copy()
        big4 = pygame.transform.scale(sub, (zw, zh))
        canvas.blit(big4, (zx, row3_y))
        pygame.draw.rect(canvas, (60, 58, 82), (zx, row3_y, zw, zh), 1)
        lbl = lf.render(label, True, (196, 192, 214))
        canvas.blit(lbl, (zx + (zw - lbl.get_width()) // 2, row3_y + zh + 3))
        zx += zw + gap

    pygame.image.save(canvas, out)
    print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")

    # ── pixel verification ────────────────────────────────────────────────────
    # (1) plaque paints; (2) numerals gold (affordable) vs pewter (locked);
    # (3) the longest name is truncated so NO ink crosses x=155.
    afford = render_card("skin_kitsune", equipped=False, affordable=True)
    locked = render_card("skin_tempest", equipped=False, affordable=False)
    assert afford.get_at((BADGE.centerx, BADGE.centery))[3] > 0, "badge blank"

    def num_pixel(buf):
        # sample the price-numeral band on row 1, just right of the coin
        xs = range(INNER_X + COIN_R * 2 + sc.m(4), 110)
        best = (0, 0, 0)
        for x in xs:
            for y in range(ROW1_CY - sc.m(6), ROW1_CY + sc.m(6)):
                p = buf.get_at((x, y))
                if p[3] > 200 and p[0] + p[1] + p[2] > sum(best):
                    best = (p[0], p[1], p[2])
        return best

    ga = num_pixel(afford)
    gl = num_pixel(locked)
    print("affordable numeral (brightest):", ga, "-> warm gold: R>G>B",
          ga[0] > ga[1] > ga[2])
    print("locked numeral (brightest):", gl, "-> cool pewter: B>=R",
          gl[2] >= gl[0] - 6)
    assert ga[0] > ga[1] > ga[2], "affordable numerals are not warm gold"
    assert gl[2] >= gl[0] - 6, "locked numerals are not desaturated/pewter"

    # The plaque and its rim are a hard rounded rect ending at x=152; the only
    # variable-width badge ink is the name row, which is measured against a fixed
    # budget. Prove the WORST catalog name's truncated width keeps its right edge
    # clear of x=155 (a straight pixel scan can't be used here — the hero dome +
    # its gold bezel legitimately paint bright pixels in the same x band).
    worst = max((sc._name(i) for i in sc.store_catalog.CATALOG), key=len)
    nf = sc.font(7)
    fitted = _fit_name(worst, nf, NAME_MAX)
    right = INNER_X + sc._glyph_base(fitted, nf, 0).get_width()
    print(f"worst name {worst!r} -> {fitted!r}  right edge x={right} (<155)")
    assert BADGE.right <= 152, "plaque right edge crossed x=152"
    assert right < 155, "truncated name ink crossed x=155"
    print("no badge ink past x=155 — longest catalog name truncated OK")


if __name__ == "__main__":
    main()
