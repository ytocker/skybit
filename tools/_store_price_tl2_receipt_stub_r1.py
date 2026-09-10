"""Round-1 exploration render for the `receipt-stub` store-card price tag.

A horizontal paper receipt stub pinned to the card's top-left: warm manila
face when affordable, cool grey receipt paper when locked. Its bottom edge is
bitten into a scalloped perforation with a row of round punch-dots just above,
a small PRICE kicker over a hairline rule, then large bold price numerals.
Review sheet only — nothing here is wired into the live store draw path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()


def _abbr(text):
    """Prices run into the thousands; the stub's numeral lane is short, so
    collapse long numbers to a compact `1.1k` style that stays legible at 1x."""
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _price_glyph(text):
    """Faux-bold numeral master that steps down a font size until it fits the
    stub's ~62px numeral lane."""
    for fs in (13, 11, 10):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(0.9))
        if mask.get_width() <= 62:
            return mask
    return mask


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the receipt stub at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant (the store passes "locked" for
    gated/too-expensive cards); the wallet-derived `affordable` kwarg is
    absorbed and ignored so the exploration sheet can force both states."""
    affordable = (variant != "locked")
    text = _abbr(text)

    # Stub body is authored in local coords (origin = card-buffer (12,14)); the
    # bottom two rows of the surface hold the scallop overhang that gets erased.
    bw, bh = 82, 50
    rad = sc.m(3)
    scallop_x = [6, 16, 26, 36, 46, 56, 66, 76]   # local; abs 18,28,...,88

    if affordable:
        body_stops = [(0.0, (252, 246, 228)), (1.0, (228, 208, 166))]
        gamma = 1.04
        bevel_hi = (255, 248, 220)
        bevel_lo = (180, 156, 110)
        rule_col = (200, 176, 122)
        kick_col = (140, 88, 16)
        dot_col = (188, 164, 110)
    else:
        body_stops = [(0.0, (212, 216, 228)), (1.0, (152, 158, 176))]
        gamma = 1.02
        bevel_hi = (228, 234, 246)
        bevel_lo = (110, 116, 134)
        rule_col = (140, 146, 164)
        kick_col = (96, 102, 122)
        dot_col = (120, 126, 144)

    stub = pygame.Surface((bw, bh + 2), pygame.SRCALPHA)
    stub.blit(sc.vgrad_stops(bw, bh, rad, body_stops, 255, gamma), (0, 0))

    # embossed lips: a bright top edge + a darker lower lip above the tear line
    pygame.draw.line(stub, bevel_hi, (3, 0), (bw - 4, 0), 1)
    pygame.draw.line(stub, bevel_lo, (4, 39), (bw - 5, 39), 1)

    # hairline rule separating the PRICE kicker from the numerals
    pygame.draw.line(stub, rule_col, (6, 18), (76, 18), 1)

    # PRICE kicker, small caps, left-aligned above the rule
    kf = sc.font(7)
    kbase = sc._glyph_base("PRICE", kf, sc.m(0.6))
    kimg = kbase.copy()
    kimg.fill((*kick_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    stub.blit(kimg, (8, 2))

    # large bold price numerals, poured with the coin-metal ramp when affordable
    # and flat dark slate ink when locked (both via a MULT into the glyph mask)
    mask = _price_glyph(text)
    img = mask.copy()
    if affordable:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        fill = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        fill.fill((74, 80, 100, 255))
        img.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    stub.blit(img, img.get_rect(center=(40, 32)))

    # bite the scalloped perforation out of the bottom edge; alpha=0 circles cut
    # true holes so, once composited, the card body shows through the tear.
    for xi in scallop_x:
        pygame.draw.circle(stub, (0, 0, 0, 0), (xi, bh), sc.m(4))

    # round punch-dots riding the tear line, drawn last so they stay visible on
    # the scalloped edge like reinforced perforations.
    for xi in scallop_x:
        pygame.draw.circle(stub, dot_col, (xi, 42), max(1, sc.m(1.2)))

    # drop shadow under the whole stub, offset down-right (top-left light)
    shadow = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 60), shadow.get_rect(), border_radius=rad)
    surf.blit(shadow, (12 + 2, 14 + 2))

    surf.blit(stub, (12, 14))


sc.price_chip = my_price_chip


def render_card_1x(sid, affordable=True):
    variant = sc.PRICE_VARIANT if affordable else "locked"
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False, variant=variant)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


# ── pixel verification (run BEFORE saving the sheet) ──────────────────────────
_va = render_card_1x("skin_mummy", True)
_vl = render_card_1x("skin_mummy", False)
bg = (8, 8, 20)
# probe at 1x inside the stub body (stub at x=6..47, y=7..32 in 1x; avoid
# the scallop zone near y=32)
px, py = 20, 15
pa, pl = _va.get_at((px, py))[:3], _vl.get_at((px, py))[:3]
assert any(abs(pa[i] - bg[i]) > 40 for i in range(3)), f"no stub aff at ({px},{py}): {pa}"
assert any(abs(pl[i] - bg[i]) > 40 for i in range(3)), f"no stub locked at ({px},{py}): {pl}"
assert pa != pl, f"states identical at ({px},{py})"
print(f"verify aff:{pa} lock:{pl} PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)
row1 = [("skin_mummy", True, "MUMMY aff"), ("skin_mummy", False, "MUMMY locked"),
        ("skin_kitsune", True, "KITSUNE aff"), ("skin_kitsune", False, "KITSUNE locked")]
cards1 = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in row1]
crop_w, crop_h, zoom = 80, 100, 2
crops = [(pygame.transform.scale(_va.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left aff"),
         (pygame.transform.scale(_vl.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left locked")]
row1_w = 4 * sc.CARD_W + 3 * GAP
row2_w = 2 * crop_w * zoom + GAP
sheet_w = PAD * 2 + max(row1_w, row2_w)
sheet_h = PAD + HEADER_H + sc.CARD_H + LABEL_H + GAP + crop_h * zoom + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
fh = hud_font(22)
fl = hud_font(13)
sheet.blit(fh.render("RECEIPT-STUB price tag — round 1", True, (240, 224, 180)),
           (PAD, PAD // 2))


def _lbl(t, x, y, w):
    img = fl.render(t, True, (190, 196, 210))
    sheet.blit(img, (x + (w - img.get_width()) // 2, y))


y0 = PAD + HEADER_H
x = PAD
for card, lbl in cards1:
    sheet.blit(card, (x, y0))
    _lbl(lbl, x, y0 + sc.CARD_H + 3, sc.CARD_W)
    x += sc.CARD_W + GAP
y1 = y0 + sc.CARD_H + LABEL_H + GAP
x = PAD
for crop, lbl in crops:
    sheet.blit(crop, (x, y1))
    _lbl(lbl, x, y1 + crop_h * zoom + 3, crop_w * zoom)
    x += crop_w * zoom + GAP
out = "docs/store_price_tl2/receipt-stub/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
