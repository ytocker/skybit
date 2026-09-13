"""v5_card_item_size — item thumbnail size ladder on the locked CONSTELLATION card.

Only the box_px passed to blit_thumb varies.  Every other element (dome, glass,
gem badge, ribbon, name, price chip) is drawn by the exact production draw_card()
from game/store_cards.  Uses monkeypatching so the card draw function itself stays
untouched — we only swap in a fixed box_px for the thumb call.

Panels (all use skin_mummy — EPIC):
  #0  60 px  baseline  (current production)
  #1  72 px  +20 %
  #2  84 px  +40 %
  #3  96 px  +60 %
  #4 108 px  +80 %
  #5 120 px  +100 %

Output: docs/store_card_v5_card_item/size_r1.png
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

# The item used across all panels (EPIC tier)
SID = "skin_mummy"

CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
SS = sc.SS
_INSET = 6
PANEL_W = CARD_W * SS   # 324
PANEL_H = CARD_H * SS   # 200

# Size ladder: (label, box_px)
SIZES = [
    ("baseline  60 px", 60),
    ("+20 %   72 px",  72),
    ("+40 %   84 px",  84),
    ("+60 %   96 px",  96),
    ("+80 %  108 px", 108),
    ("+100 % 120 px", 120),
]


def render_panel(box_px: int) -> pygame.Surface:
    """Draw a 324×200 CONSTELLATION card with the thumb box fixed to box_px."""
    # Monkeypatch blit_thumb so only the box size differs
    original_blit_thumb = sc.blit_thumb

    def _patched_blit_thumb(surf, sid, cx, cy, _ignored):
        original_blit_thumb(surf, sid, cx, cy, box_px)

    sc.blit_thumb = _patched_blit_thumb
    try:
        big = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
        rect = pygame.Rect(sc.m(_INSET), sc.m(_INSET),
                           PANEL_W - 2 * sc.m(_INSET),
                           PANEL_H - 2 * sc.m(_INSET))
        sc.draw_card(big, SID, rect, equipped=False, secret=False)
    finally:
        sc.blit_thumb = original_blit_thumb  # always restore

    pygame.draw.rect(big, (40, 38, 58), (0, 0, PANEL_W, PANEL_H), 1)
    return big


# ── canvas ────────────────────────────────────────────────────────────────────
BG       = (8, 8, 20)
GAP      = 10
MARGIN   = 20
HDR_H    = 44
LBL_H    = 26
FOOTER_H = LBL_H + 8

n         = len(SIZES)
canvas_w  = MARGIN * 2 + PANEL_W * n + GAP * (n - 1)
canvas_h  = MARGIN + HDR_H + PANEL_H + FOOTER_H + MARGIN

canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

# Header
hf   = hud_font(18, True)
htxt = hf.render(
    f"v5 card item size  —  {SID}  (EPIC)  — item thumbnail size options",
    True, (210, 206, 224))
canvas.blit(htxt, ((canvas_w - htxt.get_width()) // 2,
                   MARGIN + (HDR_H - htxt.get_height()) // 2))

lbl_font = hud_font(12, False)
panel_y  = MARGIN + HDR_H

for col, (label, box_px) in enumerate(SIZES):
    x = MARGIN + col * (PANEL_W + GAP)
    panel = render_panel(box_px)
    canvas.blit(panel, (x, panel_y))

    lbl = f"{'BASELINE' if col == 0 else f'#{col}'}  {label}"
    col_colour = (255, 230, 120) if col == 0 else (178, 174, 198)
    lbl_surf = lbl_font.render(lbl, True, col_colour)
    if lbl_surf.get_width() > PANEL_W - 4:
        lbl_surf = hud_font(10, False).render(lbl, True, col_colour)
    canvas.blit(lbl_surf,
                (x + (PANEL_W - lbl_surf.get_width()) // 2,
                 panel_y + PANEL_H + 6))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_card_v5_card_item", "size_r1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved: {out}  ({canvas_w}×{canvas_h})")
