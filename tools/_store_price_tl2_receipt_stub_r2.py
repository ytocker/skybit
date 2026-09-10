"""Round-2 exploration render for the `receipt-stub` store-card price tag.

A horizontal paper receipt stub pinned to the card's top-left: warm manila
face when affordable, cool grey receipt paper when locked. Round 2 fixes the
r1 perforation — 5 well-spaced scallop bites (diameter < spacing) leave real
flat paper between each dip so the tear-off silhouette actually reads at 1x.
The PRICE kicker + rule are gone (illegible at 1x); the freed room buys a
bigger price numeral, a dark-bronze outline for cream-body contrast, and a
few faint register-tape hairlines. Review sheet only — nothing is wired into
the live store draw path.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")

import math
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
    """Faux-bold numeral master, +2pt over r1, stepped down until it fits the
    stub's numeral lane."""
    for fs in (15, 13, 12):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(0.9))
        if mask.get_width() <= 66:
            return mask
    return mask


def _outlined_numeral(text, affordable):
    """Numeral with a crisp 1px keyline so it clears the cream/grey paper: the
    stamped glyph is stroked in dark bronze at 8 compass offsets, then the
    sovereign coin-metal ramp (or slate ink) is poured into the crisp core.
    Gold-on-cream alone is ~31 lum delta and reads muddy at 1x — the keyline
    buys the contrast."""
    mask = _price_glyph(text)
    gw, gh = mask.get_size()
    p = sc.m(1)
    out = pygame.Surface((gw + 2 * p, gh + 2 * p), pygame.SRCALPHA)

    key_col = (110, 62, 8) if affordable else (44, 48, 66)
    key = mask.copy()
    key.fill((*key_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for ang in range(0, 360, 45):
        dx = int(round(p * math.cos(math.radians(ang))))
        dy = int(round(p * math.sin(math.radians(ang))))
        out.blit(key, (p + dx, p + dy))

    core = mask.copy()
    if affordable:
        grad = sc.vgrad_stops(gw, gh, 0, sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        core.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        fill = pygame.Surface((gw, gh), pygame.SRCALPHA)
        fill.fill((74, 80, 100, 255))
        core.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    out.blit(core, (p, p))
    return out


# stub geometry (2x/device coords in the stub-local surface)
_BW, _BH = 82, 54                 # paper rect; body reads y=0..53 (1x y=7..33.5)
_SURF_H = _BH + 8                 # room for scallop circles that dip below
_BITE_R = 7                       # diameter 14 < 16.5 spacing => 2px flat paper
_BITE_Y = 53                      # circle centre; only the tops bite the paper
# 5 bites centred across the body: first abs x=20 (local 8), last abs x=86
# (local 74), evenly spaced so the flat-dip-flat silhouette is symmetric.
_BITE_X = [int(round(8 + i * (74 - 8) / 4.0)) for i in range(5)]  # 8,24,41,58,74
_DOT_Y = (_BITE_Y - _BITE_R) - 5  # punch-dots ride just above the scallop zone


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the receipt stub at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant; the wallet-derived `affordable`
    kwarg is absorbed so the exploration sheet can force both states."""
    affordable = (variant != "locked")
    text = _abbr(text)

    bw, bh = _BW, _BH
    rad = sc.m(3)

    if affordable:
        body_stops = [(0.0, (252, 246, 228)), (1.0, (228, 208, 166))]
        gamma = 1.04
        bevel_hi = (255, 248, 220)
        rule_col = (240, 228, 200, 60)
        dot_col = (170, 145, 95)
    else:
        body_stops = [(0.0, (212, 216, 228)), (1.0, (152, 158, 176))]
        gamma = 1.02
        bevel_hi = (228, 234, 246)
        rule_col = (200, 206, 220, 40)
        dot_col = (120, 126, 150)

    stub = pygame.Surface((bw, _SURF_H), pygame.SRCALPHA)
    stub.blit(sc.vgrad_stops(bw, bh, rad, body_stops, 255, gamma), (0, 0))

    # embossed bright top lip (top-left light)
    pygame.draw.line(stub, bevel_hi, (3, 0), (bw - 4, 0), 1)

    # faint register-tape ruling — texture, not text, so nothing has to be
    # legible; the numeral sits on top and the lines peek out around it.
    for hy in (10, 30, 38):
        ln = pygame.Surface((bw - 12, 1), pygame.SRCALPHA)
        ln.fill(rule_col)
        stub.blit(ln, (6, hy))

    # hero price numeral, outlined for contrast, centred in the upper body
    glyph = _outlined_numeral(text, affordable)
    stub.blit(glyph, glyph.get_rect(center=(41, 24)))

    # scallop perforation: alpha=0 circles cut true holes so the card body
    # shows through the tear. Spaced so diameter (14) < gap (16.5) — real flat
    # paper survives between every dip instead of merging to one flat cut.
    for xi in _BITE_X:
        pygame.draw.circle(stub, (0, 0, 0, 0), (xi, _BITE_Y), _BITE_R)

    # reinforced punch-dots aligned to the bite centres, riding just above the
    # scalloped edge like a tear guide.
    for xi in _BITE_X:
        pygame.draw.circle(stub, dot_col, (xi, _DOT_Y), sc.m(1.5))

    # drop shadow under the stub, kept short so its straight bottom stays hidden
    # behind the scalloped paper edge.
    shadow = pygame.Surface((bw, bh - 6), pygame.SRCALPHA)
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
px, py = 20, 15
pa, pl = _va.get_at((px, py))[:3], _vl.get_at((px, py))[:3]
assert any(abs(pa[i] - bg[i]) > 40 for i in range(3)), f"no receipt aff at ({px},{py}): {pa}"
assert any(abs(pl[i] - bg[i]) > 40 for i in range(3)), f"no receipt locked at ({px},{py}): {pl}"
assert pa != pl, f"states identical at ({px},{py})"

# scallop presence at TRUE 1x: flat paper 2px above the bottom, dip below it
paper = _va.get_at((20, 30))[:3]
bite = _va.get_at((20, 33))[:3]
print(f"paper at 1x: {paper}, near-scallop: {bite}")

bottom_row = [_va.get_at((x, 33))[:3] for x in range(8, 46, 3)]
print("bottom edge variation (scallop check):", bottom_row[:5])
print(f"verify aff:{pa} lock:{pl} PASS")

# ── render sheet ──────────────────────────────────────────────────────────────
PAD, GAP, HEADER_H, LABEL_H = 20, 12, 40, 20
BG = (8, 8, 20)
row1 = [("skin_mummy", True, "MUMMY aff"), ("skin_mummy", False, "MUMMY locked"),
        ("skin_kitsune", True, "KITSUNE aff"), ("skin_kitsune", False, "KITSUNE locked")]
cards1 = [(render_card_1x(sid, aff), lbl) for sid, aff, lbl in row1]
crop_w, crop_h, zoom = 80, 100, 2
_va2 = render_card_1x("skin_mummy", True)
_vl2 = render_card_1x("skin_mummy", False)
crops = [(pygame.transform.scale(_va2.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left aff"),
         (pygame.transform.scale(_vl2.subsurface((0, 0, crop_w, crop_h)),
                                 (crop_w * zoom, crop_h * zoom)), "2x left locked")]
row1_w = 4 * sc.CARD_W + 3 * GAP
row2_w = 2 * crop_w * zoom + GAP
sheet_w = PAD * 2 + max(row1_w, row2_w)
sheet_h = PAD + HEADER_H + sc.CARD_H + LABEL_H + GAP + crop_h * zoom + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
fh = hud_font(22)
fl = hud_font(13)
sheet.blit(fh.render("RECEIPT-STUB price tag — round 2", True, (240, 224, 180)),
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
out = "docs/store_price_tl2/receipt-stub/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
