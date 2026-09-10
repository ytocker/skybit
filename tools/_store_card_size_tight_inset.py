"""tight-inset store-card size concept — round 1.

Reclaims card real estate by shrinking the dead margin so the hero can grow:
  _INSET 6 -> 3 logical (12 -> 6 SS px headroom)
  bevel_rim card width m(2.0) -> m(2.6)   (enlarged card reads as a jeweled edge)
  _DOME_R 56 -> 64 dev,  _BOX_PX 84 -> 98 dev  (grown into the reclaimed space)
  card drop-shadow blur m(8) -> m(5)      (only 6 SS headroom outside the body)

The shadow + card-frame bevel are patched via helper wrappers keyed on their
card-only signatures so chip shadows (blur=m(4)) and chip bevels (non-card `deep`)
are left untouched.

NOTE: this branch's production draw_card has NO equipped gold halo / 2-step gold
frame — equipped differs only by the green EQUIPPED chip. The docstring's halo and
`_alpha_aura` are unused/legacy, so there is no halo to tighten. The EQUIPPED
panels are still rendered to confirm the tighter inset reads cleanly.

Output: docs/store_card_size/tight_inset/round_1.png
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
_orig_bevel_rim = sc.bevel_rim


def patched_drop_shadow(surf, rect, radius, blur, alpha, dy):
    # Only 6 SS px of headroom outside the body now, so the card shadow (blur=m(8))
    # must pull in; chip shadows at m(4) already fit and are left as-is.
    return _orig_drop_shadow(surf, rect, radius, min(blur, sc.m(5)), alpha, dy)


def patched_bevel_rim(surf, rect, radius, deep, bright, w):
    # Thicken ONLY the card frame (identified by CARD_RING_DEEP) into a jeweled
    # edge; chip/status bevels use other `deep` colours and stay their own width.
    if deep == sc.CARD_RING_DEEP:
        w = max(1, sc.m(2.6))
    return _orig_bevel_rim(surf, rect, radius, deep, bright, w)


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
sc._DOME_R = 64
sc._BOX_PX = 98
sc.drop_shadow = patched_drop_shadow
sc.bevel_rim = patched_bevel_rim
sc._card_cache.clear()

concept_unequipped = render_panel(False)
concept_equipped = render_panel(True)

# ── restore originals, baseline render ──────────────────────────────────────────
sc._INSET = _ORIG_INSET
sc._DOME_R = _ORIG_DOME
sc._BOX_PX = _ORIG_BOX
sc.drop_shadow = _orig_drop_shadow
sc.bevel_rim = _orig_bevel_rim
sc._card_cache.clear()

baseline_unequipped = render_panel(False)
baseline_equipped = render_panel(True)

# ── comparison sheet ────────────────────────────────────────────────────────────
BG = (8, 8, 20)
GAP = 16
MARGIN = 22
HDR_H = 46
LBL_H = 34
ROW_GAP = 14

# 1x actual-size panels
one_x_baseline = pygame.transform.smoothscale(baseline_unequipped, (CARD_W, CARD_H))
one_x_concept = pygame.transform.smoothscale(concept_unequipped, (CARD_W, CARD_H))

grid_w = PANEL_W * 2 + GAP
canvas_w = MARGIN * 2 + grid_w
canvas_h = (MARGIN + HDR_H
            + PANEL_H + LBL_H + ROW_GAP           # row 1 (unequipped)
            + PANEL_H + LBL_H + ROW_GAP           # row 2 (equipped)
            + CARD_H + LBL_H                       # row 3 (1x)
            + MARGIN)

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

hf = hud_font(18, True)
htxt = hf.render(
    f"tight-inset r1  —  {SID}  —  inset 6->3, frame m2.0->m2.6, "
    f"dome 56->64, box 84->98, shadow m8->m5",
    True, (214, 210, 228))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_font = hud_font(13, True)
sub_font = hud_font(10, False)

BASE_COL = (170, 166, 190)
CONC_COL = (255, 226, 120)


def place_labels(x, y, title, subtitle, col):
    t1 = lbl_font.render(title, True, col)
    t2 = sub_font.render(subtitle, True, (128, 124, 148))
    canvas.blit(t1, (x + (PANEL_W - t1.get_width()) // 2, y))
    canvas.blit(t2, (x + (PANEL_W - t2.get_width()) // 2, y + t1.get_height() + 2))


col_x0 = MARGIN
col_x1 = MARGIN + PANEL_W + GAP

# Row 1 — unequipped (2x)
y = MARGIN + HDR_H
canvas.blit(baseline_unequipped, (col_x0, y))
canvas.blit(concept_unequipped, (col_x1, y))
ly = y + PANEL_H + 5
place_labels(col_x0, ly, "BASELINE", "inset 6  /  frame m2.0  /  dome 56", BASE_COL)
place_labels(col_x1, ly, "CONCEPT  tight-inset", "inset 3  /  frame m2.6  /  dome 64", CONC_COL)

# Row 2 — equipped (2x): halo / clip check
y = ly + LBL_H + ROW_GAP
canvas.blit(baseline_equipped, (col_x0, y))
canvas.blit(concept_equipped, (col_x1, y))
ly = y + PANEL_H + 5
place_labels(col_x0, ly, "BASELINE  equipped", "green EQUIPPED chip", BASE_COL)
place_labels(col_x1, ly, "CONCEPT  equipped", "reduced-inset clip check", CONC_COL)

# Row 3 — 1x actual final size
y = ly + LBL_H + ROW_GAP
one_x_gap = 40
row3_w = CARD_W * 2 + one_x_gap
x0 = (canvas_w - row3_w) // 2
x1 = x0 + CARD_W + one_x_gap
canvas.blit(one_x_baseline, (x0, y))
canvas.blit(one_x_concept, (x1, y))
ly = y + CARD_H + 5
b1 = lbl_font.render("BASELINE 1x", True, BASE_COL)
c1 = lbl_font.render("CONCEPT 1x", True, CONC_COL)
canvas.blit(b1, (x0 + (CARD_W - b1.get_width()) // 2, ly))
canvas.blit(c1, (x1 + (CARD_W - c1.get_width()) // 2, ly))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_size", "tight_inset", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {os.path.abspath(out)}  ({canvas_w}x{canvas_h})")
