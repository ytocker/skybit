"""Headless round-1 render for the `backlight-glow` store tab-strip concept.

The active tab is lit from behind by a soft additive gold bloom on the night
sky — no fill, pill, rail, or underline. Kept as a throwaway tool render so the
art-director reviews it on git rather than inline.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
pygame.init()
pygame.display.set_mode((360, 640), pygame.NOFRAME)

import sys
sys.path.insert(0, "/home/user/skybit")

from game.config import W, H
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.draw import lerp_color, rounded_rect, NEAR_BLACK, WHITE
from game.store import _vgrad_panel, _drop_shadow, _gradient_text, _TAB_Y, _TABS, \
    _draw_chevron
import game.store_data as sd
import game.store as st

sd.load()
sd._STATE["wallet"] = 12340


def my_draw_tabs(self, surf):
    f = _font(12, True)
    pad, gap = 11, 6
    widths = [f.size(label)[0] + 2 * pad for label, _g in _TABS]
    content_w = sum(widths) + gap * (len(_TABS) - 1)
    full_vp = pygame.Rect(12, _TAB_Y - 13, W - 24, 26)
    overflow = content_w > full_vp.width
    chev = 18 if overflow else 0
    vp = pygame.Rect(full_vp.x + chev, full_vp.y, full_vp.width - 2 * chev, 26)
    max_scroll = max(0, content_w - vp.width)
    self.tab_scroll = max(0.0, min(self.tab_scroll, float(max_scroll)))
    self._tab_vp, self._tab_widths, self._tab_gap = vp, widths, gap

    prev_clip = surf.get_clip()
    surf.set_clip(vp)
    self.tab_rects = []
    cx = 0
    for i, (label, _g) in enumerate(_TABS):
        w = widths[i]
        r = pygame.Rect(round(vp.x + cx - self.tab_scroll), _TAB_Y - 13, w, 26)
        self.tab_rects.append(r)
        active = (i == self.tab)

        if active:
            # Elliptical bloom BEHIND the text — five stacked ellipses fake a
            # radial falloff so the additive halo hugs the label rather than
            # flooding the strip; brightest core reads as the light source.
            gw, gh = r.w + 20, 40
            glow_surf = pygame.Surface((gw, gh), pygame.SRCALPHA)
            gcx, gcy = gw / 2, gh / 2
            rings = (
                ((gw, gh), (255, 195, 60, 12)),
                ((gw * 0.78, gh * 0.72), (255, 200, 70, 28)),
                ((gw * 0.56, gh * 0.52), (255, 208, 80, 55)),
                ((gw * 0.36, gh * 0.34), (255, 218, 95, 90)),
                ((gw * 0.18, gh * 0.18), (255, 235, 130, 140)),
            )
            for (ew, eh), col in rings:
                erect = pygame.Rect(0, 0, round(ew), round(eh))
                erect.center = (round(gcx), round(gcy))
                pygame.draw.ellipse(glow_surf, col, erect)
            surf.blit(glow_surf, (r.centerx - gw // 2, _TAB_Y - gh // 2),
                      special_flags=pygame.BLEND_ADD)

            timg = f.render(label, True, _GOLD_PALE)
            surf.blit(timg, timg.get_rect(center=r.center))
        else:
            timg = f.render(label, True, _GOLD_PALE)
            timg.set_alpha(185)
            surf.blit(timg, timg.get_rect(center=r.center))
        cx += w + gap
    surf.set_clip(prev_clip)

    self.tab_chev_l = self.tab_chev_r = None
    if overflow and self.tab_scroll > 1:
        self.tab_chev_l = pygame.Rect(full_vp.x, full_vp.y, chev, 26)
        _draw_chevron(surf, self.tab_chev_l, -1)
    if overflow and self.tab_scroll < max_scroll - 1:
        self.tab_chev_r = pygame.Rect(full_vp.right - chev, full_vp.y, chev, 26)
        _draw_chevron(surf, self.tab_chev_r, 1)


st.StoreScene._draw_tabs = my_draw_tabs
scene = st.StoreScene()
scene.view = "category"
scene.tab = 0
scene.page = 0
surf = pygame.Surface((W, H))
scene.render(surf)

strip = surf.subsurface(pygame.Rect(0, 70, W, 42))
strip_tall = pygame.transform.smoothscale(strip, (W, 126))
lf = _font(11, True)
lt = lf.render("BACKLIGHT-GLOW — tab strip close-up (3x vertical)", True, (180, 200, 255))
canvas = pygame.Surface((W, H + 16 + lt.get_height() + 4 + 126))
canvas.fill((8, 8, 20))
canvas.blit(surf, (0, 0))
canvas.blit(lt, (8, H + 8))
canvas.blit(strip_tall, (0, H + 16 + lt.get_height() + 4))

os.makedirs("/home/user/skybit/docs/store_tab_strip_redesign/backlight-glow", exist_ok=True)
out = "/home/user/skybit/docs/store_tab_strip_redesign/backlight-glow/round_1.png"
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
