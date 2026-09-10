"""Concept: header-bar — full-width top strip with chip right-aligned inside it."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((360, 640), pygame.NOFRAME)

import sys
sys.path.insert(0, "/home/user/skybit")

from game.config import W, H
import game.store_data as sd
import game.store as st
import game.store_cards as sc
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE
from game.store import _vgrad_panel, _drop_shadow, _gradient_text

sd.load()
sd._STATE["wallet"] = 12340

_STRIP_H = 32  # full-width bar height at top


def _draw_balance_header_bar(self, surf, y):
    """Full-width dark strip at y=0..32; chip right-aligned within it."""
    # Draw full-width bar strip
    bar = pygame.Surface((W, _STRIP_H), pygame.SRCALPHA)
    bar.fill((8, 5, 22, 210))
    surf.blit(bar, (0, 0))
    pygame.draw.line(surf, (*_GOLD_BRIGHT, 80), (0, _STRIP_H - 1), (W, _STRIP_H - 1))

    # Chip inside the strip, right-aligned
    cy = _STRIP_H // 2  # vertical center of the strip = 16
    val = f"{sd.balance():,}"
    vf = _font(18, True)
    vimg_w = vf.size(val)[0]
    coin_d, gap_coin, pad = 20, 7, 6
    w = coin_d + gap_coin + vimg_w + pad * 2
    cap = pygame.Rect(0, cy - 14, w, 28)
    cap.right = W - 6
    _drop_shadow(surf, cap, 14, blur=4, alpha=90)
    surf.blit(_vgrad_panel(cap.w, cap.h, 14, (44, 32, 18), (20, 14, 8), 252), cap.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 120), cap.inflate(-2, -2), width=1, border_radius=13)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190), cap, width=1, border_radius=14)
    x = cap.x + pad
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
    x += coin_d + gap_coin
    _gradient_text(surf, val, vf, (x + vimg_w // 2, cy),
                   (255, 246, 196), (236, 170, 60), shadow=True)


st.StoreScene._draw_balance = _draw_balance_header_bar

scene = st.StoreScene()
scene.view = "category"
scene.tab = 0
scene.page = 0

surf = pygame.Surface((W, H))
scene.render(surf)

out = "/home/user/skybit/docs/store_coin_chip_placement/header-bar.png"
pygame.image.save(surf, out)
print(f"saved {W}×{H} → {out}")
