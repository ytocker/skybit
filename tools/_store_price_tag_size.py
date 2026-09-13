"""Price tag size comparison — 5 size options.

Current tag: _TAG_W=76, _TAG_H=88.  Steps scale both dimensions ~8% each.
Shows skin_mummy (4-digit price) at SS and 1× zoom so glyph quality is clear.
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

# ── size steps: (label, tag_w, tag_h) ────────────────────────────────────────
STEPS = [
    ("CURRENT\n76×88",   76,  88),
    ("SIZE +1\n82×95",   82,  95),
    ("SIZE +2\n88×102",  88, 102),
    ("SIZE +3\n94×109",  94, 109),
    ("SIZE +4\n100×116", 100, 116),
]

_ORIG_TAG_W  = sc._TAG_W
_ORIG_TAG_H  = sc._TAG_H
_orig_price  = sc.price_chip


def make_price_chip(tag_w, tag_h):
    """Return a price_chip replacement that draws the tag at (tag_w × tag_h)."""
    gx = round(tag_w * 28 / 76)   # grommet x scaled proportionally
    gy = round(tag_h * 12 / 88)   # grommet y scaled proportionally

    def _chip(surf, cx, cy, text, h, variant=1, affordable=True):
        sc._TAG_W = tag_w
        sc._TAG_H = tag_h
        text = sc._tag_full(text)
        rad = sc.m(3)
        grommet = (gx, gy)
        face = pygame.Surface((tag_w, tag_h), pygame.SRCALPHA)
        brect = pygame.Rect(0, 0, tag_w, tag_h)
        if affordable:
            body = sc.vgrad_stops(tag_w, tag_h, rad,
                                  [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                                  255, gamma=1.04)
            face.blit(body, (0, 0))
            sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                         (255, 240, 190, 200), w=max(1, sc.m(1.2)))
            ring_col = (110, 80, 30)
        else:
            body = sc.vgrad_stops(tag_w, tag_h, rad,
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
        sc._TAG_W = _ORIG_TAG_W
        sc._TAG_H = _ORIG_TAG_H
    return _chip


def render_panel(tag_w, tag_h):
    sc.price_chip = make_price_chip(tag_w, tag_h)
    sc._card_cache.clear()
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    ri = sc.m(sc._INSET)
    rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
    sc.draw_card(big, SID, rect, equipped=False, secret=False)
    sc.price_chip = _orig_price
    sc._TAG_W = _ORIG_TAG_W
    sc._TAG_H = _ORIG_TAG_H
    sc._card_cache.clear()
    return big


panels = [(lbl, render_panel(tw, th)) for lbl, tw, th in STEPS]

# ── layout ────────────────────────────────────────────────────────────────────
BG      = (8, 8, 20)
PAD     = 20
GAP     = 10
HDR_H   = 48
LBL_H   = 38
ROW_GAP = 18
DISP_W, DISP_H = CARD_W * 2, CARD_H * 2

N = len(panels)
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + ROW_GAP + LBL_H + DISP_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

fh = hud_font(17, True)
fl = hud_font(12, True)
fs = hud_font(10, False)

title = fh.render("price tag size — 5 options · skin_mummy", True, (240, 224, 180))
sheet.blit(title, ((sheet_w - title.get_width()) // 2,
                   PAD + (HDR_H - title.get_height()) // 2))

y_ss = PAD + HDR_H + LBL_H
for i, (lbl, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    col = (170, 166, 190) if i == 0 else (255, 226, 120)
    lines = lbl.split("\n")
    lh = fl.get_height()
    for li, line in enumerate(lines):
        t = fl.render(line, True, col)
        ly = PAD + HDR_H + (LBL_H - lh * len(lines)) // 2 + li * lh
        sheet.blit(t, (x + (PANEL_W - t.get_width()) // 2, ly))
    sheet.blit(surf, (x, y_ss))

y_1x_lbl = y_ss + PANEL_H + ROW_GAP
y_1x = y_1x_lbl + LBL_H
sub = fs.render("1× final pixels at 2× display zoom — judge here", True, (160, 160, 190))
sheet.blit(sub, ((sheet_w - sub.get_width()) // 2,
                  y_1x_lbl + (LBL_H - sub.get_height()) // 2))

for i, (_, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    one_x = pygame.transform.smoothscale(surf, (CARD_W, CARD_H))
    disp  = pygame.transform.scale(one_x, (DISP_W, DISP_H))
    sheet.blit(disp, (x + (PANEL_W - DISP_W) // 2, y_1x))

out = "docs/store_card_size/price_tag_size.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
