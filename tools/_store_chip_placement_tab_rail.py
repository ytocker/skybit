"""Concept: tab-rail — chip floats right of the tab strip (y=92), drawn after tabs."""
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

_TAB_Y = 92


def _draw_chip_at_tab_y(surf):
    """Draw balance chip right-aligned at the tab rail Y, tight right margin."""
    cy = _TAB_Y
    val = f"{sd.balance():,}"
    vf = _font(14, True)
    vimg_w = vf.size(val)[0]
    coin_d, gap_coin, pad = 16, 5, 5
    w = coin_d + gap_coin + vimg_w + pad * 2
    cap = pygame.Rect(0, cy - 13, w, 26)
    cap.right = W - 4
    _drop_shadow(surf, cap, 13, blur=3, alpha=90)
    surf.blit(_vgrad_panel(cap.w, cap.h, 13, (44, 32, 18), (20, 14, 8), 252), cap.topleft)
    pygame.draw.rect(surf, (0, 0, 0, 120), cap.inflate(-2, -2), width=1, border_radius=12)
    pygame.draw.rect(surf, (*_GOLD_BRIGHT, 190), cap, width=1, border_radius=13)
    x = cap.x + pad
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2)
    x += coin_d + gap_coin
    _gradient_text(surf, val, vf, (x + vimg_w // 2, cy),
                   (255, 246, 196), (236, 170, 60), shadow=True)


# Make the normal _draw_balance call (at y=16) a no-op
def _draw_balance_noop(self, surf, y):
    pass


# After tabs are drawn, inject the chip into the tab rail area
_orig_tabs = st.StoreScene._draw_tabs


def _draw_tabs_with_rail_chip(self, surf):
    _orig_tabs(self, surf)
    _draw_chip_at_tab_y(surf)


st.StoreScene._draw_balance = _draw_balance_noop
st.StoreScene._draw_tabs = _draw_tabs_with_rail_chip

scene = st.StoreScene()
scene.view = "category"
scene.tab = 0
scene.page = 0

surf = pygame.Surface((W, H))
scene.render(surf)

out = "/home/user/skybit/docs/store_coin_chip_placement/tab-rail.png"
pygame.image.save(surf, out)
print(f"saved {W}×{H} → {out}")
