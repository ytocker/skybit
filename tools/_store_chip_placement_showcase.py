"""Compile 5 coin-chip placement concepts into a single showcase PNG."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((360, 640), pygame.NOFRAME)

import sys
sys.path.insert(0, "/home/user/skybit")

from game.hud import _font

SLUGS = [
    ("header-bar",           "HEADER BAR"),
    ("inline-right",         "INLINE RIGHT"),
    ("below-title-centered", "BELOW TITLE"),
    ("tab-rail",             "TAB RAIL"),
    ("oversized-hero",       "HERO CAPSULE"),
]

COLORS = [
    (255, 220, 80),
    (120, 210, 255),
    (180, 255, 150),
    (255, 160, 100),
    (210, 150, 255),
]

THUMB_W = 270
THUMB_H = int(640 * THUMB_W / 360)  # = 480
GAP = 12
PAD = 16
HDR = 32

canvas_w = PAD * 2 + THUMB_W * len(SLUGS) + GAP * (len(SLUGS) - 1)
canvas_h = PAD + HDR + THUMB_H + PAD
canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill((8, 8, 20))

hf = _font(13, True)

base = "/home/user/skybit/docs/store_coin_chip_placement"

for i, ((slug, label), col) in enumerate(zip(SLUGS, COLORS)):
    path = os.path.join(base, f"{slug}.png")
    img = pygame.image.load(path)
    thumb = pygame.transform.smoothscale(img, (THUMB_W, THUMB_H))
    x = PAD + i * (THUMB_W + GAP)
    y_thumb = PAD + HDR

    # Label
    t = hf.render(label, True, col)
    canvas.blit(t, (x + (THUMB_W - t.get_width()) // 2, PAD + (HDR - t.get_height()) // 2))

    # Thumbnail
    canvas.blit(thumb, (x, y_thumb))

    # Border
    pygame.draw.rect(canvas, (*col, 140), (x - 1, y_thumb - 1, THUMB_W + 2, THUMB_H + 2), 1)

out = os.path.join(base, "showcase.png")
pygame.image.save(canvas, out)
print(f"saved {canvas_w}×{canvas_h} → {out}")
