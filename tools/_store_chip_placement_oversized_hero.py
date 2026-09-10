"""Concept: oversized-hero — larger chip (h=36) centered below STORE (y≈62)."""
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
from game.hud import _font, _GOLD_BRIGHT
from game.store import _vgrad_panel, _drop_shadow, _gradient_text

sd.load()
sd._STATE["wallet"] = 12340


def _draw_balance_oversized_hero(self, surf, y):
    """Bigger pill (h=36, font=20) centered below STORE — reads as 'YOUR BALANCE'."""
    cy = 62
    val = f"{sd.balance():,}"
    vf = _font(20, True)
    vimg_w = vf.size(val)[0]
    coin_d, gap_coin, pad = 24, 8, 10
    h_cap = 36
    w = coin_d + gap_coin + vimg_w + pad * 2
    cap = pygame.Rect(0, cy - h_cap // 2, w, h_cap)
    cap.centerx = W // 2
    _drop_shadow(surf, cap, h_cap // 2, blur=6, alpha=100)
    surf.blit(_vgrad_panel(cap.w, cap.h, h_cap // 2,
                           (52, 38, 20), (24, 16, 8), 252), cap.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 120), cap.inflate(-2, -2), width=1,
                     border_radius=h_cap // 2 - 1)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), cap, width=1,
                     border_radius=h_cap // 2)
    x = cap.x + pad
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
    x += coin_d + gap_coin
    _gradient_text(surf, val, vf, (x + vimg_w // 2, cy),
                   (255, 248, 200), (240, 178, 60), shadow=True)


st.StoreScene._draw_balance = _draw_balance_oversized_hero

scene = st.StoreScene()
scene.view = "category"
scene.tab = 0
scene.page = 0

surf = pygame.Surface((W, H))
scene.render(surf)

out = "/home/user/skybit/docs/store_coin_chip_placement/oversized-hero.png"
pygame.image.save(surf, out)
print(f"saved {W}×{H} → {out}")
