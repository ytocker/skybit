# Assembles the 15 matured batch-2 boss finals into one legible showcase grid.
# WHY a left-region proportional crop: every concept sheet places the hero
# creature in the upper-left below the title bar; side panels (pillar/scale/
# palette) and the bottom 32px strip are reference, not the hero, so we trim
# them away rather than uniformly shrinking the whole sheet (which would bury
# the creature among its annotations).
import os
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()

BASE = os.path.dirname(os.path.abspath(__file__))

# Grouped by family, in the requested row order.
# (slug/round, caption, hero-crop window as L,T,R,B fractions of that sheet).
# WHY per-sheet windows: every concept sheet is a bespoke layout, so a single
# fixed fraction either clips a creature or grabs the neighbouring pillar /
# scale panel. These windows were measured off each final to frame the hero.
ROWS = [
    ("DEVILISH", [
        ("ifra/round_3", "Ifra", (0.05, 0.13, 0.32, 0.80)),
        ("leyak/round_2", "Leyak", (0.02, 0.15, 0.22, 0.66)),
        ("cernun/round_2", "Cernun", (0.045, 0.175, 0.275, 0.60)),
        ("tlaloc_tiki/round_2", "Tlaloc-Tiki", (0.03, 0.13, 0.38, 0.62)),
        ("pazul/round_2", "Pazul", (0.02, 0.13, 0.26, 0.72)),
    ]),
    ("SKELETONS", [
        ("draugr/round_3", "Draugr", (0.02, 0.14, 0.27, 0.55)),
        ("necrarch/round_3", "Necrarch", (0.04, 0.13, 0.30, 0.70)),
        ("catrina/round_3", "Catrina", (0.02, 0.10, 0.165, 0.67)),
        ("jiangshi/round_3", "Jiangshi", (0.06, 0.20, 0.30, 0.58)),
        ("mariachi/round_3", "Mariachi", (0.02, 0.13, 0.33, 0.585)),
    ]),
    ("JAPANESE", [
        ("kitsune/round_2", "Kitsune", (0.04, 0.12, 0.49, 0.62)),
        ("yurei/round_3", "Yurei", (0.05, 0.12, 0.30, 0.72)),
        ("kappa/round_2", "Kappa", (0.0, 0.10, 0.40, 0.68)),
        ("raijin/round_2", "Raijin", (0.0, 0.08, 0.36, 0.62)),
        ("karakasa/round_2", "Karakasa", (0.05, 0.12, 0.30, 0.80)),
    ]),
]

TILE_W = 300
TILE_H = 300
TILE_PAD = 18
CAP_H = 30           # name caption band under each tile
ROW_LABEL_H = 46     # family label band above each row
MARGIN = 36
BG = (96, 98, 104)             # neutral mid-grey
TILE_BG = (60, 62, 68)
CAP_BG = (44, 46, 50)
INK = (236, 238, 242)
FAMILY_INK = (255, 226, 150)

pygame.font.init()
title_font = pygame.font.SysFont("dejavusans,arial", 30, bold=True)
family_font = pygame.font.SysFont("dejavusans,arial", 26, bold=True)
cap_font = pygame.font.SysFont("dejavusans,arial", 22, bold=True)


def hero_tile(path, window):
    left, top, right, bottom = window
    sheet = pygame.image.load(path)
    sw, sh = sheet.get_size()
    box = pygame.Rect(
        int(sw * left),
        int(sh * top),
        int(sw * (right - left)),
        int(sh * (bottom - top)),
    )
    crop = sheet.subsurface(box).copy()
    cw, ch = crop.get_size()
    # Fit-inside scale so the whole hero stays visible and undistorted.
    scale = min((TILE_W - 12) / cw, (TILE_H - 12) / ch)
    scaled = pygame.transform.smoothscale(
        crop, (max(1, int(cw * scale)), max(1, int(ch * scale)))
    )
    tile = pygame.Surface((TILE_W, TILE_H))
    tile.fill(TILE_BG)
    sx = (TILE_W - scaled.get_width()) // 2
    sy = (TILE_H - scaled.get_height()) // 2
    tile.blit(scaled, (sx, sy))
    pygame.draw.rect(tile, (28, 29, 33), tile.get_rect(), 2)
    return tile


cols = 5
grid_w = cols * TILE_W + (cols - 1) * TILE_PAD
sheet_w = grid_w + 2 * MARGIN
row_block_h = ROW_LABEL_H + TILE_H + CAP_H
sheet_h = MARGIN + 70 + len(ROWS) * (row_block_h + TILE_PAD) + MARGIN

out = pygame.Surface((sheet_w, sheet_h))
out.fill(BG)

# Top title.
t = title_font.render("Skybit — Batch-2 Boss Concepts — 15 matured finals", True, INK)
out.blit(t, (MARGIN, MARGIN - 6))

y = MARGIN + 64
for fam, items in ROWS:
    lbl = family_font.render(fam, True, FAMILY_INK)
    pygame.draw.rect(out, (40, 42, 47), (MARGIN, y, grid_w, ROW_LABEL_H - 8))
    out.blit(lbl, (MARGIN + 12, y + 4))
    ty = y + ROW_LABEL_H
    for i, (rel, name, window) in enumerate(items):
        tx = MARGIN + i * (TILE_W + TILE_PAD)
        tile = hero_tile(os.path.join(BASE, rel + ".png"), window)
        out.blit(tile, (tx, ty))
        # caption band
        pygame.draw.rect(out, CAP_BG, (tx, ty + TILE_H, TILE_W, CAP_H))
        cap = cap_font.render(name, True, INK)
        out.blit(cap, (tx + (TILE_W - cap.get_width()) // 2, ty + TILE_H + 4))
    y += row_block_h + TILE_PAD

out_path = os.path.join(BASE, "showcase.png")
pygame.image.save(out, out_path)
print("WROTE", out_path, out.get_size())
