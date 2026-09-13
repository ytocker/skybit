"""Contact-sheet harness for Pip's power-up combination skins.

Sets the relevant Bird flags for each combination, calls Bird.draw onto a
tile, and lays the tiles into a labelled grid so every combo can be eyeballed
for clipping / double-stacked head-pieces / dropped buffs. Procedural-art
verification only; not shipped in the WASM bundle.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((360, 640))

from game.entities import Bird  # noqa: E402

K = {"knight_active": True}
# Each combo: label -> dict of Bird-flag overrides.
COMBOS = [
    ("base", {}),
    ("3x (hat)", {"triple_active": True}),
    ("kfc", {"kfc_active": True}),
    ("ghost", {"ghost_active": True}),
    ("knight", {**K}),
    ("knight+3x", {**K, "triple_active": True}),
    ("knight+kfc", {**K, "kfc_active": True}),
    ("knight+ghost", {**K, "ghost_active": True}),
    ("kn+kfc+ghost", {**K, "kfc_active": True, "ghost_active": True}),
    ("kn+kfc+3x", {**K, "kfc_active": True, "triple_active": True}),
    ("kn+ghost+3x", {**K, "ghost_active": True, "triple_active": True}),
    ("kn+kfc+gh+3x", {**K, "kfc_active": True, "ghost_active": True, "triple_active": True}),
    ("skate", {"skateboard_active": True}),
    ("skate+3x", {"skateboard_active": True, "triple_active": True}),
    ("skate+knight", {"skateboard_active": True, **K}),
    ("skate+grow", {"skateboard_active": True, "grow_active": True}),
    ("poison base", {"poison_active": True, "poison_t": 0.85}),
    ("poison kfc", {"poison_active": True, "poison_t": 0.85, "kfc_active": True}),
    ("poison ghost", {"poison_active": True, "poison_t": 0.85, "ghost_active": True}),
    ("poison knight", {"poison_active": True, "poison_t": 0.85, **K}),
]

TW, TH = 150, 168
COLS = 4
PAD_TOP = 26


def tile(flags):
    s = pygame.Surface((TW, TH))
    for y in range(TH):
        t = y / TH
        s.fill((int(120 - 40 * t), int(150 - 30 * t), int(200 - 20 * t)),
               (0, y, TW, 1))
    b = Bird()
    b.x, b.y = TW / 2, TH / 2 - 6
    for k, v in flags.items():
        setattr(b, k, v)
    b.draw(s, 0, 0)
    return s


# The NEW interactions added in the combo-skin effort — each saved as its own
# zoomed PNG under docs/pip_combos/tiles/ so it can be linked individually.
NEW_TILES = [
    ("knight_3x", "KNIGHT + 3x  (royal crown)", {**K, "triple_active": True}),
    ("knight_kfc", "KNIGHT + KFC  (the fried knight)", {**K, "kfc_active": True}),
    ("knight_ghost", "KNIGHT + GHOST  (spectral)", {**K, "ghost_active": True}),
    ("knight_kfc_ghost", "KNIGHT + KFC + GHOST", {**K, "kfc_active": True, "ghost_active": True}),
    ("knight_kfc_3x", "KNIGHT + KFC + 3x", {**K, "kfc_active": True, "triple_active": True}),
    ("knight_ghost_3x", "KNIGHT + GHOST + 3x", {**K, "ghost_active": True, "triple_active": True}),
    ("knight_kfc_ghost_3x", "KNIGHT + KFC + GHOST + 3x", {**K, "kfc_active": True, "ghost_active": True, "triple_active": True}),
    ("skate_3x", "SKATEBOARD + 3x  (gold bunny top-hat)", {"skateboard_active": True, "triple_active": True}),
    ("skate_knight", "SKATEBOARD + KNIGHT  (armet, no 2nd helm)", {"skateboard_active": True, **K}),
    ("skate_grow", "SKATEBOARD + GROW  (board scaled up)", {"skateboard_active": True, "grow_active": True}),
    ("skate_shrink", "SKATEBOARD + SHRINK  (board scaled down)", {"skateboard_active": True, "shrink_scale": 0.6}),
    ("poison_base", "POISON  (tints base)", {"poison_active": True, "poison_t": 0.85}),
    ("poison_kfc", "POISON + KFC", {"poison_active": True, "poison_t": 0.85, "kfc_active": True}),
    ("poison_ghost", "POISON + GHOST", {"poison_active": True, "poison_t": 0.85, "ghost_active": True}),
    ("poison_knight", "POISON + KNIGHT", {"poison_active": True, "poison_t": 0.85, **K}),
]


def save_tiles():
    """Each new interaction as its own 3x-zoomed PNG with a caption."""
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "pip_combos", "tiles")
    os.makedirs(out, exist_ok=True)
    font = pygame.font.SysFont("monospace", 13, bold=True)
    for slug, label, flags in NEW_TILES:
        raw = tile(flags)                       # 150x168 sky tile, bird centred
        big = pygame.transform.scale(raw, (raw.get_width() * 3, raw.get_height() * 3))
        canvas = pygame.Surface((big.get_width(), big.get_height() + 30))
        canvas.fill((22, 26, 36))
        canvas.blit(font.render(label, True, (255, 235, 140)), (8, 8))
        canvas.blit(big, (0, 30))
        pygame.image.save(canvas, os.path.join(out, slug + ".png"))
    print("saved", len(NEW_TILES), "tiles to", out)


def main():
    rows = (len(COMBOS) + COLS - 1) // COLS
    sheet = pygame.Surface((TW * COLS, (TH + PAD_TOP) * rows))
    sheet.fill((22, 26, 36))
    font = pygame.font.SysFont("monospace", 14, bold=True)
    for i, (label, flags) in enumerate(COMBOS):
        c, r = i % COLS, i // COLS
        x, y = c * TW, r * (TH + PAD_TOP)
        sheet.blit(font.render(label, True, (255, 235, 140)), (x + 6, y + 5))
        sheet.blit(tile(flags), (x, y + PAD_TOP))
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "pip_combos")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "phase1.png")
    pygame.image.save(sheet, path)
    print("saved", path, sheet.get_size())


if __name__ == "__main__":
    main()
    save_tiles()
