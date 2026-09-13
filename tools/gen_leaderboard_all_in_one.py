"""Throwaway: stack the original leaderboard + every suggestion sheet into ONE
combined image for easy sharing.
Run: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/gen_leaderboard_all_in_one.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game.hud import _font

BG = (16, 14, 30)
GOLD = (243, 200, 90)
WHITE = (235, 235, 245)

CANVAS_W = 1560
PAD = 20

# (file, target content width, label)
SECTIONS = [
    ("docs/leaderboard/original_leaderboard.png", 560,
     "ORIGINAL  -  current single-board leaderboard"),
    ("docs/leaderboard/round_1.png", 1520,
     "ROUND 1  -  5 initial directions"),
    ("docs/leaderboard/round_2.png", 1520,
     "ROUND 2  -  fused lead + variants (each shown V5 LIVE + V4 LEGENDS)"),
    ("docs/leaderboard/round_3.png", 1520,
     "ROUND 3 (FINAL)  -  5 polished candidates (each V5 LIVE + V4 LEGENDS)"),
    ("docs/leaderboard/round_3_lead_360.png", 1100,
     "ROUND 3 LEAD at true 360px scale  -  recommended winner"),
]

TITLE_H = 90
LABEL_H = 64
GAP = 28

# Load + scale, measure total height.
tiles = []
total_h = TITLE_H
for path, w, label in SECTIONS:
    img = pygame.image.load(path).convert_alpha()
    ow, oh = img.get_size()
    h = round(oh * (w / ow))
    img = pygame.transform.smoothscale(img, (w, h))
    tiles.append((img, w, h, label))
    total_h += LABEL_H + h + GAP

canvas = pygame.Surface((CANVAS_W, total_h))
canvas.fill(BG)

# Title
tf = _font(40, True)
t = tf.render("Skybit  -  Leaderboard redesign: original + all suggestions", True, GOLD)
canvas.blit(t, t.get_rect(center=(CANVAS_W // 2, TITLE_H // 2)))

lf = _font(26, True)
y = TITLE_H
for img, w, h, label in tiles:
    lbl = lf.render(label, True, WHITE)
    canvas.blit(lbl, (PAD, y + (LABEL_H - lbl.get_height()) // 2))
    pygame.draw.line(canvas, (70, 64, 96),
                     (PAD, y + LABEL_H - 6),
                     (CANVAS_W - PAD, y + LABEL_H - 6), 2)
    y += LABEL_H
    canvas.blit(img, ((CANVAS_W - w) // 2, y))
    y += h + GAP

path = "docs/leaderboard/all_in_one.png"
pygame.image.save(canvas, path)
print("wrote", os.path.abspath(path), canvas.get_size())
