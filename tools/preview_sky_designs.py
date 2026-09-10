"""Headless QA sheet for the dormant biome sky-design registry.

Renders the 10 `game.sky_designs.CATALOG` designs (rows) across the
`game.biome_sky_keyframes.STAGES` day→night phases (columns) into
`docs/biome_redesign/sky_designs_port_check.png`, for visual comparison against
`docs/biome_redesign/round_7_all_skystars_daynight.png` (same biome order, same
arc). Dev aid only — the game never imports this.

    python tools/preview_sky_designs.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y          # noqa: E402
from game.sky_designs import CATALOG            # noqa: E402
from game.biome_sky_keyframes import STAGES     # noqa: E402

TILE_SCALE = 0.42
TW, TH = int(W * TILE_SCALE), int(H * TILE_SCALE)
GUT = 150          # left gutter for biome name
HEAD = 24          # top strip for stage labels
PAD = 3

f_head = pygame.font.SysFont("dejavusans", 13, bold=True)
f_name = pygame.font.SysFont("dejavusans", 14, bold=True)
f_tag = pygame.font.SysFont("dejavusans", 11)


def main():
    cols = len(STAGES)
    rows = len(CATALOG)
    sheet_w = GUT + cols * (TW + PAD) + PAD
    sheet_h = HEAD + rows * (TH + PAD) + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 24, 28))

    # Column labels (stage names) along the top strip.
    for c, (label, _phase) in enumerate(STAGES):
        x = GUT + c * (TW + PAD)
        lbl = f_tag.render(label, True, (250, 230, 180))
        sheet.blit(lbl, (x + (TW - lbl.get_width()) // 2, HEAD - 16))

    for r, (design_id, name, _note, render_fn) in enumerate(CATALOG):
        y = HEAD + r * (TH + PAD)
        nm = f_name.render(name, True, (245, 245, 250))
        sheet.blit(nm, (6, y + TH // 2 - 8))
        for c, (_label, phase) in enumerate(STAGES):
            x = GUT + c * (TW + PAD)
            tile = pygame.Surface((W, H))
            render_fn(tile, W, H, GROUND_Y, None, phase)
            sheet.blit(pygame.transform.smoothscale(tile, (TW, TH)), (x, y))

    title = f_head.render(
        "Sky designs port check — 10 designs x day/night stages "
        "(compare vs round_7_all_skystars_daynight.png)",
        True, (240, 240, 245))
    # Title rides in the gutter's top-left corner.
    sheet.blit(title, (6, 4))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "biome_redesign", "sky_designs_port_check.png")
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()}, "
          f"{rows} rows x {cols} cols)")


if __name__ == "__main__":
    main()
