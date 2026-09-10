"""Knight shield — size variant sheet (in-game gameplay frames).

Five candidate `size=` values for `knight_skin.draw_shield_icon`.
Each cell is an actual PlayScene frame at playtest start (score 450)
with a knight pickup force-spawned beside Pip, rendered at the
candidate size. Includes 48 px (current) as the right anchor so the
user can see how much smaller each option reads in context.

Output: docs/screenshots/icon_sizes/knight_size_variants.png
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game.scenes import App, STATE_PLAY
from game.entities import PowerUp
from game import knight_skin


# Sizes sweep small → current. Current ships at 48 (Pip-and-pickup
# variant pick from the earlier round).
SIZES = (24, 30, 36, 42, 48)

CROP_X = 0
CROP_Y = 230
CROP_W = 360
CROP_H = 180

CELL_W = 230
CELL_H = int(CELL_W * CROP_H / CROP_W)
PAD       = 14
LABEL_COL = 0
ROW_GAP   = 14
HEADER_H  = 78

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _grab_frame(target_size: int) -> pygame.Surface:
    """One PlayScene frame with the knight pickup rendered at
    `target_size` px (monkey-patched via the PowerUp instance)."""
    app = App()
    app.state = STATE_PLAY
    app.world.ready_t = 0
    app.world.bird.x = 90
    app.world.bird.y = 320
    app.world.bird.vy = 0
    app.world.pipes.clear()
    app.world.coins.clear()
    app.world.powerups.clear()

    pickup = PowerUp(220, 320, kind="knight")
    pickup.pulse = 0.0
    import math as _math

    def _draw(self, surf):
        cx = int(self.x)
        cy = int(self.y + _math.sin(self.pulse * 0.9) * 2)
        knight_skin.draw_shield_icon(surf, cx, cy, size=target_size)

    pickup.draw = _draw.__get__(pickup, PowerUp)
    app.world.powerups.append(pickup)

    app._render()
    return app.screen.copy()


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "knight_size_variants.png")

    sheet_w = (PAD * 2 + len(SIZES) * (CELL_W + ROW_GAP) - ROW_GAP)
    sheet_h = HEADER_H + CELL_H + 36 + PAD * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(20, bold=True).render(
        "KNIGHT shield — size variants (real PlayScene frames)",
        True, LABEL)
    sheet.blit(title, (PAD, PAD))
    sub = _font(13).render(
        "Pip + the pickup at the candidate size. Rightmost cell (48) "
        "is the current shipped size; the others are smaller.",
        True, SUB)
    sheet.blit(sub, (PAD, PAD + 24))

    for col, sz in enumerate(SIZES):
        x = PAD + col * (CELL_W + ROW_GAP) + CELL_W // 2
        h = _font(14, bold=True).render(
            f"{sz} px" + ("  (current)" if sz == 48 else ""), True, LABEL)
        sheet.blit(h, (x - h.get_width() // 2, HEADER_H - 22))

    y = HEADER_H
    for col, sz in enumerate(SIZES):
        x = PAD + col * (CELL_W + ROW_GAP)
        print(f"  rendering knight @ {sz} px ...")
        frame = _grab_frame(sz)
        crop = frame.subsurface(
            pygame.Rect(CROP_X, CROP_Y, CROP_W, CROP_H)).copy()
        frame_sm = pygame.transform.smoothscale(crop, (CELL_W, CELL_H))
        sheet.blit(frame_sm, (x, y))
        pygame.draw.rect(sheet, (44, 50, 60),
                         (x, y, CELL_W, CELL_H), 1)

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
