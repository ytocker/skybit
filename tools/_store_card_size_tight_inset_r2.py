"""tight-inset store-card size concept — round 2.

Commits to the HERO-growth thesis: reclaimed margin is spent on the dome, not
the frame. Reclaim the inset, grow the hero dome, and keep the bevel_rim at its
original width so none of the recovered space feeds the frame:
  _INSET 6 -> 3 logical (12 -> 6 SS px headroom)
  _DOME_R 56 -> 70 dev  (bigger hero payoff than r1's 64)
  _BOX_PX 84 -> 98 dev
  bevel_rim card width HELD at original m(2.0)  (no jeweled-edge thickening)
  card drop-shadow blur m(8) -> m(5)  (only 6 SS headroom outside the body)

The shadow patch is keyed on the card-only signature so chip shadows (blur=m(4))
are left untouched. No bevel patch this round — the frame stays baseline width.

This branch's production draw_card has NO equipped gold halo / 2-step gold frame
(equipped differs only by the green EQUIPPED chip), so no equipped panels are
rendered here. The 1x final-size row is the primary judging panel.

Output: docs/store_card_size/tight_inset/round_2.png
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
SS = sc.SS
CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
PANEL_W = CARD_W * SS          # 324 at SS=2
PANEL_H = CARD_H * SS          # 200 at SS=2

# ── captured originals ──────────────────────────────────────────────────────────
_ORIG_INSET = sc._INSET
_ORIG_DOME = sc._DOME_R
_ORIG_BOX = sc._BOX_PX
_orig_drop_shadow = sc.drop_shadow


def patched_drop_shadow(surf, rect, radius, blur, alpha, dy):
    # Only 6 SS px of headroom outside the body now, so the card shadow (blur=m(8))
    # must pull in; chip shadows at m(4) already fit and are left as-is.
    return _orig_drop_shadow(surf, rect, radius, min(blur, sc.m(5)), alpha, dy)


def render_panel(equipped):
    """Draw one 324x200 supersampled card panel using the ACTIVE sc._INSET."""
    big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    inset = sc.m(sc._INSET)
    rect = pygame.Rect(inset, inset, PANEL_W - 2 * inset, PANEL_H - 2 * inset)
    sc.draw_card(big, SID, rect, equipped, False)
    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


# ── concept render (patched) ────────────────────────────────────────────────────
sc._INSET = 3
sc._DOME_R = 70
sc._BOX_PX = 98
sc.drop_shadow = patched_drop_shadow
sc._card_cache.clear()

concept_unequipped = render_panel(False)

# ── restore originals, baseline render ──────────────────────────────────────────
sc._INSET = _ORIG_INSET
sc._DOME_R = _ORIG_DOME
sc._BOX_PX = _ORIG_BOX
sc.drop_shadow = _orig_drop_shadow
sc._card_cache.clear()

baseline_unequipped = render_panel(False)

# ── comparison sheet ────────────────────────────────────────────────────────────
BG = (8, 8, 20)
GAP = 16
MARGIN = 22
HDR_H = 46
LBL_H = 34
ROW_GAP = 26

# The 1x row is the primary judging panel — display it at 2x screen size so the
# real final pixels are visible without re-supersampling (nearest to preserve
# exactly what ships at 1x, scaled up for the reviewer's eye).
one_x_baseline = pygame.transform.smoothscale(baseline_unequipped, (CARD_W, CARD_H))
one_x_concept = pygame.transform.smoothscale(concept_unequipped, (CARD_W, CARD_H))
disp_baseline = pygame.transform.scale(one_x_baseline, (CARD_W * 2, CARD_H * 2))
disp_concept = pygame.transform.scale(one_x_concept, (CARD_W * 2, CARD_H * 2))
DISP_W, DISP_H = CARD_W * 2, CARD_H * 2

grid_w = PANEL_W * 2 + GAP
canvas_w = MARGIN * 2 + grid_w
canvas_h = (MARGIN + HDR_H
            + PANEL_H + LBL_H + ROW_GAP           # row 1 (2x detail)
            + DISP_H + LBL_H                       # row 2 (1x final size, judging)
            + MARGIN)

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf = hud_font(18, True)
htxt = hf.render(
    f"tight-inset r2  —  {SID}  —  HERO growth: inset 6->3, dome 56->70, "
    f"box 84->98, frame HELD m2.0, shadow m8->m5",
    True, (214, 210, 228))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_font = hud_font(13, True)
sub_font = hud_font(10, False)

BASE_COL = (170, 166, 190)
CONC_COL = (255, 226, 120)


def place_labels(x, y, w, title, subtitle, col):
    t1 = lbl_font.render(title, True, col)
    t2 = sub_font.render(subtitle, True, (128, 124, 148))
    canvas.blit(t1, (x + (w - t1.get_width()) // 2, y))
    canvas.blit(t2, (x + (w - t2.get_width()) // 2, y + t1.get_height() + 2))


col_x0 = MARGIN
col_x1 = MARGIN + PANEL_W + GAP

# Row 1 — 2x detail (baseline | concept)
y = MARGIN + HDR_H
canvas.blit(baseline_unequipped, (col_x0, y))
canvas.blit(concept_unequipped, (col_x1, y))
ly = y + PANEL_H + 5
place_labels(col_x0, ly, PANEL_W, "BASELINE  (2x detail)", "inset 6  /  frame m2.0  /  dome 56", BASE_COL)
place_labels(col_x1, ly, PANEL_W, "CONCEPT tight-inset  (2x detail)", "inset 3  /  frame m2.0  /  dome 70", CONC_COL)

# Row 2 — PRIMARY: 1x final size, shown at 2x display so real pixels read big
y = ly + LBL_H + ROW_GAP
row2_gap = 48
row2_w = DISP_W * 2 + row2_gap
x0 = (canvas_w - row2_w) // 2
x1 = x0 + DISP_W + row2_gap
canvas.blit(disp_baseline, (x0, y))
canvas.blit(disp_concept, (x1, y))
ly = y + DISP_H + 5
place_labels(x0, ly, DISP_W, "BASELINE — final size 162x100", "shipped 1x pixels", BASE_COL)
place_labels(x1, ly, DISP_W, "CONCEPT — final size 162x100", "shipped 1x pixels  <-- judge here", CONC_COL)

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_size", "tight_inset", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {os.path.abspath(out)}  ({canvas_w}x{canvas_h})")
