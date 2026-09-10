import os; os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame; pygame.init(); pygame.display.set_mode((360, 640), pygame.NOFRAME)
import sys; sys.path.insert(0, "/home/user/skybit")
from game.config import W, H
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP
from game.draw import lerp_color, rounded_rect, NEAR_BLACK, WHITE
from game.store import _vgrad_panel, _drop_shadow, _gradient_text, _TAB_Y, _TABS, _draw_chevron
import game.store_data as sd
import game.store as st
sd.load(); sd._STATE["wallet"] = 12340

# Ribbon-fold: parchment banners — bright gold active, warm dark brown inactive.
_GOLD_BRIGHT = (255, 200, 60)
_BROWN = lerp_color((80, 56, 12), (8, 8, 20), 0.55)


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

    # Two-pass: inactive ribbons first, then the active ribbon on top so its
    # solid gold and drop shadow never sit under a neighbour's body.
    active_slot = None
    cx = 0
    for i, (label, _g) in enumerate(_TABS):
        w = widths[i]
        r = pygame.Rect(round(vp.x + cx - self.tab_scroll), _TAB_Y - 13, w, 26)
        self.tab_rects.append(r)
        cx += w + gap
        if i == self.tab:
            active_slot = (r, label)
            continue

        top_inset = 3
        points = [
            (r.x + 1 + top_inset, 82),
            (r.x + r.w - 2 - top_inset, 82),
            (r.x + r.w - 2, 102),
            (r.x + 1, 102),
        ]
        ribbon_surf = pygame.Surface((r.w, 22), pygame.SRCALPHA)
        ox, oy = r.x + 1, 82
        local_points = [(px - ox, py - oy) for px, py in points]
        pygame.draw.polygon(ribbon_surf, _BROWN, local_points)
        pygame.draw.polygon(ribbon_surf, (*_GOLD_DEEP, 130), local_points, width=1)
        ribbon_surf.set_alpha(210)
        surf.blit(ribbon_surf, (ox, oy))

        timg = f.render(label, True, _GOLD_PALE)
        timg.set_alpha(175)
        surf.blit(timg, timg.get_rect(center=r.center))

    if active_slot is not None:
        r, label = active_slot
        top_inset = 3
        points = [
            (r.x + 1 + top_inset, 82),
            (r.x + r.w - 2 - top_inset, 82),
            (r.x + r.w - 2, 102),
            (r.x + 1, 102),
        ]
        _drop_shadow(surf, pygame.Rect(r.x, 80, r.w, 24), 4, blur=3, alpha=100)
        pygame.draw.polygon(surf, _GOLD_BRIGHT, points)
        pygame.draw.polygon(surf, (*_GOLD_PALE, 220), points, width=1)
        mx = r.x + r.w // 2
        pygame.draw.line(surf, (*_GOLD_DEEP, 80), (mx, 82), (mx, 102))
        timg = f.render(label, True, NEAR_BLACK)
        surf.blit(timg, timg.get_rect(center=r.center))

    surf.set_clip(prev_clip)

    self.tab_chev_l = self.tab_chev_r = None
    if overflow and self.tab_scroll > 1:
        self.tab_chev_l = pygame.Rect(full_vp.x, full_vp.y, chev, 26)
        _draw_chevron(surf, self.tab_chev_l, -1)
    if overflow and self.tab_scroll < max_scroll - 1:
        self.tab_chev_r = pygame.Rect(full_vp.right - chev, full_vp.y, chev, 26)
        _draw_chevron(surf, self.tab_chev_r, 1)


st.StoreScene._draw_tabs = my_draw_tabs
scene = st.StoreScene(); scene.view = "category"; scene.tab = 0; scene.page = 0
surf = pygame.Surface((W, H)); scene.render(surf)

strip = surf.subsurface(pygame.Rect(0, 70, W, 42))
strip_tall = pygame.transform.smoothscale(strip, (W, 126))
lf = _font(11, True)
lt = lf.render("RIBBON-FOLD — tab strip close-up (3× vertical)", True, (180, 200, 255))
canvas = pygame.Surface((W, H + 16 + lt.get_height() + 4 + 126))
canvas.fill((8, 8, 20))
canvas.blit(surf, (0, 0)); canvas.blit(lt, (8, H + 8))
canvas.blit(strip_tall, (0, H + 16 + lt.get_height() + 4))

import os as _os; _os.makedirs("/home/user/skybit/docs/store_tab_strip_redesign/ribbon-fold", exist_ok=True)
out = "/home/user/skybit/docs/store_tab_strip_redesign/ribbon-fold/round_1.png"
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
