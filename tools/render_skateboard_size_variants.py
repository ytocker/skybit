"""Skateboard pickup — size variant sheet (in-game gameplay frames).

Five candidate display sizes for the skateboard icon, all rendered as
actual PlayScene frames so the user can judge each option at gameplay
scale. The recipe internally bakes at AUTHORED_N=96 then smoothscales
to a DISPLAY_N output; this tool overrides that final dimension per
cell by capturing the 40-px production output and smoothscaling to
the candidate native footprint at draw time.

Includes the current 40 px at the left as the size reference.

Output: docs/screenshots/icon_sizes/skateboard_size_variants.png
"""
from __future__ import annotations

import math
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


SIZES = (40, 48, 56, 64, 72)

CROP_X = 0
CROP_Y = 230
CROP_W = 360
CROP_H = 180

CELL_W = 230
CELL_H = int(CELL_W * CROP_H / CROP_W)
PAD       = 14
ROW_GAP   = 14
HEADER_H  = 78

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _load_module_with_display_n(target_size: int):
    """Load a temp copy of game.entities with the skateboard recipe's
    DISPLAY_N rewritten so the production smoothscale lands at the
    candidate size natively (no upscale blur).

    Uses a unique module name per call so sys.modules doesn't return a
    cached earlier-loaded version."""
    import importlib.util
    from game import entities as E_mod
    src = open(E_mod.__file__).read()
    needle = "        DISPLAY_N  = 40"
    replacement = f"        DISPLAY_N  = {target_size}"
    if needle not in src:
        raise SystemExit(f"could not find {needle!r} in entities.py")
    patched = src.replace(needle, replacement, 1)
    mod_name = f"_entities_skate_n{target_size}"
    tmp_path = os.path.join(os.path.dirname(THIS_DIR),
                            "tools", f"{mod_name}.py")
    with open(tmp_path, "w") as f:
        f.write(patched)
    try:
        spec = importlib.util.spec_from_file_location(mod_name, tmp_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def _grab_frame(target_size: int) -> pygame.Surface:
    """One PlayScene frame with the skateboard pickup rendered at
    `target_size` native px. We hot-load a copy of game.entities with
    DISPLAY_N patched to the target and bind the new method onto the
    pickup so the recipe runs at the candidate output natively."""
    app = App()
    app.state = STATE_PLAY
    app.world.ready_t = 0
    app.world.bird.x = 90
    app.world.bird.y = 320
    app.world.bird.vy = 0
    app.world.pipes.clear()
    app.world.coins.clear()
    app.world.powerups.clear()

    pickup = PowerUp(220, 320, kind="skateboard")
    pickup.pulse = 0.0

    patched_mod = _load_module_with_display_n(target_size)
    patched_draw_icon = patched_mod.PowerUp._draw_skateboard_icon

    def _draw(self, surf):
        # Invoke the patched recipe so the final smoothscale lands at
        # the candidate native footprint with no upscale blur.
        patched_draw_icon(self, surf)

    pickup.draw = _draw.__get__(pickup, PowerUp)
    app.world.powerups.append(pickup)

    app._render()
    return app.screen.copy()


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "skateboard_size_variants.png")

    sheet_w = (PAD * 2 + len(SIZES) * (CELL_W + ROW_GAP) - ROW_GAP)
    sheet_h = HEADER_H + CELL_H + PAD * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(20, bold=True).render(
        "SKATEBOARD pickup — size variants (real PlayScene frames)",
        True, LABEL)
    sheet.blit(title, (PAD, PAD))
    sub = _font(13).render(
        "Pip + the pickup at the candidate size. Leftmost cell (40) is "
        "the current shipped size; the others are larger.",
        True, SUB)
    sheet.blit(sub, (PAD, PAD + 24))

    for col, sz in enumerate(SIZES):
        x = PAD + col * (CELL_W + ROW_GAP) + CELL_W // 2
        lbl = f"{sz} px" + ("  (current)" if sz == 40 else "")
        h = _font(14, bold=True).render(lbl, True, LABEL)
        sheet.blit(h, (x - h.get_width() // 2, HEADER_H - 22))

    y = HEADER_H
    for col, sz in enumerate(SIZES):
        x = PAD + col * (CELL_W + ROW_GAP)
        print(f"  rendering skateboard @ {sz} px ...")
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
