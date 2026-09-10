"""Genie chamber mock — 3 wishes stacked in an OVER-wide pillar gap.

Larger gap + more spacing between the offers, and the 3 kinds appear
in a RANDOM order each cast. Two size options side by side; each cell
uses a different shuffle so the random-order behaviour is visible.

Output: docs/screenshots/icon_sizes/genie_chamber_mock.png
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


# (label, gap_boost, column_half_span, shuffle_seed)
VARIANTS = (
    ("1.8x gap  +  spacing +/-95   (random order)", 1.8, 95, 7),
    ("2.0x gap  +  spacing +/-105  (random order)", 2.0, 105, 3),
)

CHAMBER_X = 235
GAP_CENTER = 300

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _grab_frame(gap_boost, half_span, seed) -> pygame.Surface:
    app = App()
    app.state = STATE_PLAY
    app.world.ready_t = 0
    app.world.bird.x = 90
    app.world.bird.y = GAP_CENTER
    app.world.bird.vy = 0
    app.world.pipes.clear()
    app.world.coins.clear()
    app.world.powerups.clear()

    gap_h = int(GAP_START * gap_boost)
    chamber = Pipe(CHAMBER_X, GAP_CENTER, gap_h)
    app.world.pipes.append(chamber)

    # Random order across the three vertical slots.
    kinds = ["skateboard", "poison", "knight"]
    random.Random(seed).shuffle(kinds)
    slots = (-half_span, 0, half_span)
    for kind, dy in zip(kinds, slots):
        p = PowerUp(CHAMBER_X + 29, GAP_CENTER + dy, kind=kind)
        p.is_genie_offer = True
        p.pulse = 0.0
        app.world.powerups.append(p)

    app._render()
    return app.screen.copy(), kinds


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "genie_chamber_mock.png")

    PAD = 18
    COL_GAP = 24
    HEADER = 64
    CAP_H = 48

    rendered = []
    for lbl, boost, hs, seed in VARIANTS:
        frame, order = _grab_frame(boost, hs, seed)
        rendered.append((lbl, frame, order))

    sheet_w = PAD * 2 + len(rendered) * (W + COL_GAP) - COL_GAP
    sheet_h = HEADER + H + CAP_H + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(22, bold=True).render(
        "GENIE chamber — bigger gap, more spacing, random order",
        True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "Real PlayScene frames. Pip flies through the over-wide gap and "
        "picks one wish by altitude. The 3 kinds shuffle every cast.",
        True, SUB)
    sheet.blit(sub, (PAD, 38))

    for i, (lbl, frame, order) in enumerate(rendered):
        x = PAD + i * (W + COL_GAP)
        y = HEADER
        sheet.blit(frame, (x, y))
        pygame.draw.rect(sheet, (60, 66, 80), (x, y, W, H), 1)
        cap = _font(15, bold=True).render(lbl, True, LABEL)
        sheet.blit(cap, (x, y + H + 6))
        order_txt = "top -> bottom:  " + "  /  ".join(
            k.upper() for k in order)
        os_ = _font(12).render(order_txt, True, SUB)
        sheet.blit(os_, (x, y + H + 28))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})  GAP_START={GAP_START}")


if __name__ == "__main__":
    main()
