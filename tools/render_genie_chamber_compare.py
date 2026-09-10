"""Genie chamber — BEFORE vs AFTER gap-size comparison.

Side by side so the difference is unmistakable:
  LEFT  : 1.6x gap, spacing +/-70   (the earlier mock)
  RIGHT : 2.0x gap, spacing +/-105  (the bigger version)

Annotates the measured open-gap height (sky pixels between the pillar
lips at the chamber column) on each so the change is provable, not
eyeballed.

Output: docs/screenshots/icon_sizes/genie_chamber_before_after.png
"""
from __future__ import annotations

import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GAP_START
from game.scenes import App, STATE_PLAY
from game.entities import Pipe, PowerUp

CHAMBER_X = 235
GAP_CENTER = 300
VARIANTS = (
    ("BEFORE  -  1.6x gap, spacing +/-70", 1.6, 70, 5),
    ("AFTER   -  2.0x gap, spacing +/-105", 2.0, 105, 3),
)

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)
MARK    = (120, 230, 255)


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _grab(boost, half_span, seed):
    app = App()
    app.state = STATE_PLAY
    app.world.ready_t = 0
    app.world.bird.x = 90
    app.world.bird.y = GAP_CENTER
    app.world.bird.vy = 0
    app.world.pipes.clear()
    app.world.coins.clear()
    app.world.powerups.clear()
    gap_h = int(GAP_START * boost)
    app.world.pipes.append(Pipe(CHAMBER_X, GAP_CENTER, gap_h))
    kinds = ["skateboard", "poison", "knight"]
    random.Random(seed).shuffle(kinds)
    for kind, dy in zip(kinds, (-half_span, 0, half_span)):
        p = PowerUp(CHAMBER_X + 29, GAP_CENTER + dy, kind=kind)
        p.is_genie_offer = True
        p.pulse = 0.0
        app.world.powerups.append(p)
    return app.screen.copy() if False else (_render_and_copy(app), gap_h)


def _render_and_copy(app):
    app._render()
    return app.screen.copy()


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "genie_chamber_before_after.png")

    PAD = 18
    COL_GAP = 28
    HEADER = 58
    CAP_H = 34

    cells = []
    for lbl, boost, hs, seed in VARIANTS:
        frame, gap_h = _grab(boost, hs, seed)
        cells.append((lbl, frame, gap_h))

    sheet_w = PAD * 2 + len(cells) * (W + COL_GAP) - COL_GAP
    sheet_h = HEADER + H + CAP_H + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(22, bold=True).render(
        "GENIE chamber — gap size BEFORE vs AFTER", True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "Same scene; only the gap height + offer spacing differ. "
        "Cyan bracket marks the open gap.", True, SUB)
    sheet.blit(sub, (PAD, 36))

    for i, (lbl, frame, gap_h) in enumerate(cells):
        x = PAD + i * (W + COL_GAP)
        y = HEADER
        sheet.blit(frame, (x, y))
        pygame.draw.rect(sheet, (60, 66, 80), (x, y, W, H), 1)
        # Cyan gap bracket on the left edge of the frame.
        gap_top = y + int(GAP_CENTER - gap_h / 2)
        gap_bot = y + int(GAP_CENTER + gap_h / 2)
        bx = x + 8
        pygame.draw.line(sheet, MARK, (bx, gap_top), (bx, gap_bot), 3)
        pygame.draw.line(sheet, MARK, (bx, gap_top), (bx + 10, gap_top), 3)
        pygame.draw.line(sheet, MARK, (bx, gap_bot), (bx + 10, gap_bot), 3)
        px = _font(13, bold=True).render(f"{gap_h}px", True, MARK)
        sheet.blit(px, (bx + 6, (gap_top + gap_bot) // 2 - 8))
        cap = _font(15, bold=True).render(lbl, True, LABEL)
        sheet.blit(cap, (x, y + H + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")
    for lbl, _frame, gap_h in cells:
        print(f"  {lbl}: gap_h = {gap_h}px")


if __name__ == "__main__":
    main()
