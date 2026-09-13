"""Round-1 exploration render for the `dog-ear` store-card price tag.

A large rounded-rect label face pinned to the card's top-left, its top-left
corner physically folded back like a dog-ear on a book page: a triangular flap
reveals a slightly darker interior face beneath, capped by one crisp
single-value-step crease line. The price sits on the flat part of the face and
stays fully readable in both states — warm gold when affordable, pewter when
locked (the lock glyph then rides inside the fold flap).

Review sheet only — nothing here is wired into the live store draw path.
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
    """Prices climb into the thousands; the flat price band on the face is
    finite, so collapse long numbers to a compact `1.2k` style that still reads
    at 1x."""
    digits = ''.join(c for c in text if c.isdigit())
    if not digits:
        return text
    v = int(digits)
    if v >= 1000:
        frac = (v % 1000) // 100
        return f"{v//1000}.{frac}k" if frac else f"{v//1000}k"
    return str(v)


def _price_mask(text):
    """Faux-bold numeral master that steps its point size down until it clears
    the flat price band, so the fold never crowds the digits."""
    for fs in (13, 11, 10):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(0.9))
        if mask.get_width() <= 62:
            return mask
    return mask


def my_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
    """Draw the dog-ear tag at a fixed anchor in the 2x card buffer.
    Affordability is read from the variant (the store passes "locked" for
    gated / too-expensive cards); the wallet-derived `affordable` kwarg is
    absorbed and ignored so the exploration sheet can force both states."""
    affordable = (variant != "locked")
    text = _abbr(text)

    # Face panel geometry, all in the 2x author buffer.
    fx, fy, fw, fh = 12, 18, 80, 76
    rad = sc.m(5)                              # 10px on all corners; the fold clips TL

    if affordable:
        face_stops = [(0.0, (252, 220, 120)), (0.5, (232, 192, 80)),
                      (1.0, (200, 156, 40))]
        face_gamma = 1.04
        bevel_deep, bevel_bright = (80, 52, 12, 200), (255, 240, 190, 200)
        flap_stops = [(0.0, (180, 118, 28)), (1.0, (140, 86, 16))]
        crease_dark, crease_bright = (60, 36, 8), (255, 240, 200)
        lock_col = None
    else:
        face_stops = [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))]
        face_gamma = 1.02
        bevel_deep, bevel_bright = (54, 58, 74, 200), (214, 218, 232, 200)
        flap_stops = [(0.0, (110, 114, 132)), (1.0, (72, 76, 96))]
        crease_dark, crease_bright = (40, 44, 60), (210, 214, 228)
        lock_col = (188, 194, 214)             # pale slate

    # 1. Main face panel (rounded rect). Copy the cached gradient before beveling
    #    so the shared vgrad cache is never mutated.
    face = sc.vgrad_stops(fw, fh, rad, face_stops, 255, gamma=face_gamma).copy()
    sc.bevel_rim(face, pygame.Rect(0, 0, fw, fh), rad, bevel_deep, bevel_bright,
                 w=max(1, sc.m(1.5)))
    surf.blit(face, (fx, fy))

    # Absolute crease endpoints (shared by flap, shadow and the crease line).
    c0 = (42, 18)                              # crease meets the top edge
    c1 = (12, 48)                              # crease meets the left edge

    # 2. Fold flap — the folded-back TL corner, a darker interior face. Build the
    #    gradient in a 30x30 tile, then keep only the top-left triangle.
    flap = sc.vgrad_stops(30, 30, 0, flap_stops, 255).copy()
    fmask = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.polygon(fmask, (255, 255, 255, 255), [(0, 0), (30, 0), (0, 30)])
    flap.blit(fmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(flap, (fx, fy))

    # 3. Drop shadow cast by the raised flap onto the face side of the crease —
    #    the crease swept 3px toward bottom-right, filled as a thin quad. Alpha
    #    is blitted (draw.polygon would overwrite alpha, not blend).
    sh = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 80),
                        [c0, c1, (c1[0] + 3, c1[1] + 3), (c0[0] + 3, c0[1] + 3)])
    surf.blit(sh, (0, 0))

    # 4. Crease — one crisp value step: a dark line on the fold edge plus a bright
    #    line nudged 2px toward the flap interior (up-left along the crease
    #    normal), so the fold reads as a single hard edge, not a blur.
    n = (-2, -2)
    pygame.draw.line(surf, crease_dark, c0, c1, 1)
    pygame.draw.line(surf, crease_bright,
                     (c0[0] + n[0], c0[1] + n[1]),
                     (c1[0] + n[0], c1[1] + n[1]), 1)

    # 5. Lock glyph (locked only) — nested in the fold flap so the fold itself
    #    carries the "sealed" read while the price stays clean below.
    if lock_col is not None:
        lcx, lcy = 22, 32
        body = pygame.Rect(lcx - sc.m(2.5), lcy - sc.m(1), sc.m(5), sc.m(4))
        pygame.draw.rect(surf, lock_col, body, border_radius=max(1, sc.m(1)))
        srect = pygame.Rect(lcx - sc.m(4), lcy - sc.m(1) - sc.m(4),
                            sc.m(8), sc.m(8))
        pygame.draw.arc(surf, lock_col, srect,
                        math.radians(20), math.radians(160), max(1, sc.m(1)))

    # 6. Price numerals on the flat face, clear of the fold. A soft dark drop
    #    keeps gold-on-gold / pale-on-pewter legible.
    mask = _price_mask(text)
    pcx, pcy = 56, 62
    shadow = mask.copy()
    shadow.fill((0, 0, 0, 140), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(shadow, shadow.get_rect(center=(pcx + 1, pcy + 1)))

    img = mask.copy()
    if affordable:
        grad = sc.vgrad_stops(mask.get_width(), mask.get_height(), 0,
                              sc._SOVEREIGN_NUM_STOPS, 255, 1.0)
        img.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    else:
        fill = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        fill.fill((178, 184, 206, 255))
        img.blit(fill, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(img, img.get_rect(center=(pcx, pcy)))


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
# probe the flat face below the fold, where the price sits (2x (56,62) -> 1x (28,31))
px, py = 28, 31
pa, pl = _va.get_at((px, py))[:3], _vl.get_at((px, py))[:3]
assert any(abs(pa[i] - bg[i]) > 40 for i in range(3)), f"no dog-ear face aff at ({px},{py}): {pa}"
assert any(abs(pl[i] - bg[i]) > 40 for i in range(3)), f"no dog-ear face locked at ({px},{py}): {pl}"
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
sheet.blit(fh.render("DOG-EAR price tag — round 1", True, (240, 224, 180)),
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
out = "docs/store_price_tl2/dog-ear/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
