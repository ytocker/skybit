"""Before/after store category page — price chip comparison.

BEFORE: old brushwork (coin token 'G', comma format, heavy stamp, numeral at 0.62).
AFTER:  axis_crush (no coin, no comma, 0.86 crush, numeral centered at 0.52).
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

SIDS = [
    "skin_pirate", "skin_cowboy", "skin_pharaoh", "skin_crown",
    "skin_tophat", "skin_ninja", "skin_viking", "skin_wizard",
]

CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
GAP = 8
COLS, ROWS = 2, 4
grid_w = COLS * CARD_W + (COLS - 1) * GAP   # 332
grid_h = ROWS * CARD_H + (ROWS - 1) * GAP   # 424

PAD, HEADER_H, LABEL_H, BETWEEN = 20, 50, 30, 30
sheet_w = PAD + grid_w + BETWEEN + grid_w + PAD
sheet_h = PAD + HEADER_H + LABEL_H + grid_h + PAD

bg = sc.vgrad_stops(sheet_w, sheet_h, 0,
                    [(0.0, (8, 8, 24)), (0.33, (12, 12, 36)),
                     (0.66, (18, 16, 48)), (1.0, (24, 20, 58))], 255)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.blit(bg, (0, 0))

fh = hud_font(18)
fl = hud_font(15)

title = fh.render("price tag  ·  BEFORE vs AFTER  (costumes, 1×)", True, (240, 224, 180))
sheet.blit(title, (sheet_w // 2 - title.get_width() // 2, (HEADER_H - title.get_height()) // 2))

# ── BEFORE price chip (old brushwork — reconstructed inline) ─────────────────

_TW, _TH = sc._TAG_W, sc._TAG_H


def _tag_full_before(text):
    digits = ''.join(c for c in text if c.isdigit())
    return f"{int(digits):,}" if digits else text


def _tag_price_glyph_before(text):
    for fs in (13, 12, 11, 10, 9, 8):
        mask = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.8))
        if mask.get_width() <= 66:
            return mask
    return mask


def _tag_draw_price_before(face, text, affordable):
    cx = _TW // 2
    ink = (40, 30, 26) if affordable else (40, 40, 52)
    coin_col = (150, 100, 28) if affordable else (88, 92, 110)
    rule_col = (56, 42, 30) if affordable else (40, 40, 52)

    cy_token = int(_TH * 0.40)
    coin_mask = sc._stamp_bold(sc._glyph_base("G", sc.font(8), 0), sc.m(1.2))
    coin_r = coin_mask.get_rect(center=(cx, cy_token))
    coin_fill = coin_mask.copy()
    coin_fill.fill((*coin_col, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(coin_fill, coin_r)

    amt_mask = _tag_price_glyph_before(text)
    cy_amount = int(_TH * 0.62)
    amt_r = amt_mask.get_rect(center=(cx, cy_amount))
    amt_fill = amt_mask.copy()
    amt_fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
    face.blit(amt_fill, amt_r)

    rule_y = cy_amount + amt_mask.get_height() // 2 + sc.m(2)
    rule_w = min(amt_mask.get_width() + sc.m(4), _TW - sc.m(8))
    rule_x = cx - rule_w // 2
    ph, mh = max(3, sc.m(3)), max(1, sc.m(1))
    pygame.draw.polygon(face, rule_col, [
        (rule_x,          rule_y),
        (rule_x + rule_w, rule_y + (ph - mh) // 2),
        (rule_x + rule_w, rule_y + (ph + mh) // 2),
        (rule_x,          rule_y + ph),
    ])


def _before_price_chip(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, affordable=True):
    text = _tag_full_before(text)
    rad = sc.m(3)
    grommet = (28, 12)
    face = pygame.Surface((_TW, _TH), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, _TW, _TH)
    if affordable:
        face.blit(sc.vgrad_stops(_TW, _TH, rad,
                                 [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                                 255, gamma=1.04), (0, 0))
        sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                     (255, 240, 190, 200), w=max(1, sc.m(1.2)))
        ring_col = (110, 80, 30)
    else:
        face.blit(sc.vgrad_stops(_TW, _TH, rad,
                                 [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))],
                                 255, gamma=1.02), (0, 0))
        sc.bevel_rim(face, brect, rad, (54, 58, 74, 200),
                     (214, 218, 232, 200), w=max(1, sc.m(1.2)))
        ring_col = (60, 64, 80)
    _tag_draw_price_before(face, text, affordable)
    pygame.draw.circle(face, (0, 0, 0, 0), grommet, sc.m(5))
    pygame.draw.circle(face, ring_col, grommet, sc.m(5) + 1, width=max(1, sc.m(1)))
    rot = pygame.transform.rotate(face, sc._TAG_TILT)
    cord = (190, 165, 115) if affordable else (155, 160, 175)
    tag_center, knot = (44, 60), (22, 13)
    gx, gy = sc._tag_rot_point(*grommet, tag_center)
    lw = sc.m(1.5)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] - 1, knot[1] - 1), lw)
    pygame.draw.line(surf, cord, (gx, gy), (knot[0] + 2, knot[1] + 2), lw)
    surf.blit(rot, rot.get_rect(center=tag_center))
    pygame.draw.circle(surf, cord, knot, sc.m(1.5))
    pygame.draw.circle(surf,
                       tuple(min(c + 30, 255) for c in cord),
                       knot, max(1, sc.m(0.6)))


# ── render helper ─────────────────────────────────────────────────────────────

orig_price_chip = sc.price_chip


def render_card_direct(sid, chip_fn):
    """Render one card forcing affordable=True using the given chip function."""
    def _forced(surf, cx, cy, text, h, variant=sc.PRICE_VARIANT, **kw):
        return chip_fn(surf, cx, cy, text, h, variant=variant, affordable=True)
    sc.price_chip = _forced
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset,
                       sc.CARD_W * sc.SS - 2 * inset,
                       sc.CARD_H * sc.SS - 2 * inset)
    sc.draw_card(big, sid, rect, equipped=False, secret=False)
    sc.price_chip = orig_price_chip
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def render_grid(panel_x, panel_y, chip_fn):
    for idx, sid in enumerate(SIDS):
        col, row = idx % COLS, idx // COLS
        x = panel_x + col * (CARD_W + GAP)
        y = panel_y + row * (CARD_H + GAP)
        sheet.blit(render_card_direct(sid, chip_fn), (x, y))


# ── draw labels + grids ───────────────────────────────────────────────────────

grid_y = PAD + HEADER_H + LABEL_H

for i, (label, chip_fn, col) in enumerate([
    ("BEFORE  (coin token · comma · heavy stamp)", _before_price_chip, (220, 190, 130)),
    ("AFTER  (no coin · no comma · 0.86 crush)",  orig_price_chip,     (160, 220, 160)),
]):
    gx = PAD + i * (grid_w + BETWEEN)
    lbl = fl.render(label, True, col)
    sheet.blit(lbl, (gx + (grid_w - lbl.get_width()) // 2,
                     PAD + HEADER_H + (LABEL_H - lbl.get_height()) // 2))
    render_grid(gx, grid_y, chip_fn)

out = "docs/store_price_tl9/before_after_store.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
