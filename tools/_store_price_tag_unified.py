"""Price tag unified scale — tag face + digits + rule all grow together.

5 options from the 76×88 baseline at ~13% steps each.
Single row only — no 1× zoom strip.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

SID = "skin_mummy"
CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
PANEL_W, PANEL_H = CARD_W * sc.SS, CARD_H * sc.SS   # 324×200

# ── steps: (label, tw, th, gx, gy, max_fs, max_glyph_w, peak_h, min_h) ──────
# Fine-grain range between 76×88 (original) and 86×100 (next step)
STEPS = [
    ("A — ORIGINAL\n76×88",  76,  88, 28, 12, 15, 66, 6, 2),
    ("B\n79×92",              79,  92, 29, 13, 15, 69, 6, 2),
    ("C\n81×94",              81,  94, 30, 13, 16, 71, 6, 2),
    ("D\n84×97",              84,  97, 31, 13, 16, 73, 6, 2),
    ("E\n86×100",             86, 100, 32, 14, 17, 75, 7, 2),
]

_ORIG_TAG_W     = sc._TAG_W
_ORIG_TAG_H     = sc._TAG_H
_orig_glyph     = sc._tag_price_glyph
_orig_draw      = sc._tag_draw_price
_orig_price     = sc.price_chip


def make_glyph(max_fs, max_w):
    def _fn(text):
        for fs in range(max_fs, 7, -1):
            raw = sc._stamp_bold(sc._glyph_base(text, sc.font(fs), 0), sc.m(1.0))
            crushed = pygame.transform.smoothscale(
                raw, (max(1, int(raw.get_width() * 0.86)), raw.get_height()))
            if crushed.get_width() <= max_w:
                return crushed
        return crushed
    return _fn


def make_draw_price(peak_h, min_h):
    def _fn(face, text, affordable):
        cx = sc._TAG_W // 2
        ink      = (40, 30, 26) if affordable else (40, 40, 52)
        rule_col = (56, 42, 30) if affordable else (40, 40, 52)
        amt_mask = sc._tag_price_glyph(text)
        cy_amount = int(sc._TAG_H * 0.52)
        amt_r = amt_mask.get_rect(center=(cx, cy_amount))
        amt_fill = amt_mask.copy()
        amt_fill.fill((*ink, 255), special_flags=pygame.BLEND_RGBA_MULT)
        face.blit(amt_fill, amt_r)
        amt_h = amt_mask.get_height()
        rule_y = cy_amount + amt_h // 2 + sc.m(2)
        rule_w = min(amt_mask.get_width() + sc.m(4), sc._TAG_W - sc.m(8))
        rule_x = sc._TAG_W // 2 - rule_w // 2
        pts = [
            (rule_x,          rule_y),
            (rule_x + rule_w, rule_y + (peak_h - min_h) // 2),
            (rule_x + rule_w, rule_y + (peak_h + min_h) // 2),
            (rule_x,          rule_y + peak_h),
        ]
        pygame.draw.polygon(face, rule_col, pts)
    return _fn


def make_price_chip(tw, th, gx, gy):
    def _chip(surf, cx, cy, text, h, variant=1, affordable=True):
        affordable = True   # always show cream affordable state for comparison
        text = sc._tag_full(text)
        rad = sc.m(3)
        grommet = (gx, gy)
        face = pygame.Surface((tw, th), pygame.SRCALPHA)
        brect = pygame.Rect(0, 0, tw, th)
        if affordable:
            body = sc.vgrad_stops(tw, th, rad,
                                  [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                                  255, gamma=1.04)
            face.blit(body, (0, 0))
            sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                         (255, 240, 190, 200), w=max(1, sc.m(1.2)))
            ring_col = (110, 80, 30)
        else:
            body = sc.vgrad_stops(tw, th, rad,
                                  [(0.0, (156, 160, 176)), (1.0, (88, 92, 112))],
                                  255, gamma=1.02)
            face.blit(body, (0, 0))
            sc.bevel_rim(face, brect, rad, (54, 58, 74, 200),
                         (214, 218, 232, 200), w=max(1, sc.m(1.2)))
            ring_col = (60, 64, 80)
        sc._tag_draw_price(face, text, affordable)
        pygame.draw.circle(face, (0, 0, 0, 0), grommet, sc.m(5))
        pygame.draw.circle(face, ring_col, grommet, sc.m(5) + 1,
                           width=max(1, sc.m(1)))
        rot = pygame.transform.rotate(face, sc._TAG_TILT)
        cord = (190, 165, 115) if affordable else (155, 160, 175)
        tag_center = (44, 60)
        knot = (22, 13)
        gx_r, gy_r = sc._tag_rot_point(*grommet, tag_center)
        lw = sc.m(1.5)
        pygame.draw.line(surf, cord, (gx_r, gy_r), (knot[0] - 1, knot[1] - 1), lw)
        pygame.draw.line(surf, cord, (gx_r, gy_r), (knot[0] + 2, knot[1] + 2), lw)
        surf.blit(rot, rot.get_rect(center=tag_center))
        pygame.draw.circle(surf, cord, knot, sc.m(1.5))
        pygame.draw.circle(surf,
                           (min(cord[0]+30, 255), min(cord[1]+30, 255),
                            min(cord[2]+30, 255)),
                           knot, max(1, sc.m(0.6)))
    return _chip


def render_panel(tw, th, gx, gy, max_fs, max_w, peak_h, min_h):
    sc._TAG_W           = tw
    sc._TAG_H           = th
    sc._tag_price_glyph = make_glyph(max_fs, max_w)
    sc._tag_draw_price  = make_draw_price(peak_h, min_h)
    sc.price_chip       = make_price_chip(tw, th, gx, gy)
    sc._card_cache.clear()

    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    ri = sc.m(sc._INSET)
    rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
    sc.draw_card(big, SID, rect, equipped=False, secret=False)

    sc._TAG_W           = _ORIG_TAG_W
    sc._TAG_H           = _ORIG_TAG_H
    sc._tag_price_glyph = _orig_glyph
    sc._tag_draw_price  = _orig_draw
    sc.price_chip       = _orig_price
    sc._card_cache.clear()
    return big


panels = [(lbl, render_panel(tw, th, gx, gy, mfs, mw, ph, mh))
          for lbl, tw, th, gx, gy, mfs, mw, ph, mh in STEPS]

# ── layout: single row ────────────────────────────────────────────────────────
BG    = (8, 8, 20)
PAD   = 20
GAP   = 10
HDR_H = 48
LBL_H = 46

N = len(panels)
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(17, True)
fl = hud_font(12, True)

title = fh.render(
    "price tag unified scale — face + digits + rule · skin_mummy",
    True, (240, 224, 180))
sheet.blit(title, ((sheet_w - title.get_width()) // 2,
                   PAD + (HDR_H - title.get_height()) // 2))

y_panels = PAD + HDR_H + LBL_H
for i, (lbl, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    col = (170, 166, 190) if i == 0 else (255, 226, 120)
    lines = lbl.split("\n")
    lh = fl.get_height()
    for li, line in enumerate(lines):
        t = fl.render(line, True, col)
        ly = PAD + HDR_H + (LBL_H - lh * len(lines)) // 2 + li * lh
        sheet.blit(t, (x + (PANEL_W - t.get_width()) // 2, ly))
    sheet.blit(surf, (x, y_panels))

out = "docs/store_card_size/price_chip_options_3.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
