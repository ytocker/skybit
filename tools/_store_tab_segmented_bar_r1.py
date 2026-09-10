import os; os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame; pygame.init(); pygame.display.set_mode((360, 640), pygame.NOFRAME)
import sys; sys.path.insert(0, "/home/user/skybit")
from game.config import W, H
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.draw import lerp_color, rounded_rect, NEAR_BLACK, WHITE
from game.store import _vgrad_panel, _drop_shadow, _gradient_text, _TAB_Y, _TABS, _draw_chevron
import game.store_data as sd
import game.store as st
sd.load(); sd._STATE["wallet"] = 12340


def my_draw_tabs(self, surf):
    """Segmented-bar tab strip: one fixed dark trough spanning the viewport, with
    the active tab raised as a lighter carved segment and inactive tabs as flat
    labels sitting on the trough."""
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

    # Fixed trough — anchored to the viewport, never scrolled with the tabs.
    trough = pygame.Rect(vp.x, _TAB_Y - 6, vp.width, 12)
    _drop_shadow(surf, trough, 6, blur=2, alpha=60)
    surf.blit(_vgrad_panel(trough.w, trough.h, 6, (42, 30, 12), (22, 15, 7), 200),
              trough.topleft)
    pygame.draw.rect(surf, (*_GOLD_DEEP, 140), trough, width=1, border_radius=6)

    # Chevrons live as filled rail end-caps at each trough end when tabs overflow.
    self.tab_chev_l = self.tab_chev_r = None
    if overflow:
        cap_l = pygame.Rect(full_vp.x, _TAB_Y - 6, 18, 12)
        cap_r = pygame.Rect(full_vp.right - 18, _TAB_Y - 6, 18, 12)
        rounded_rect(surf, cap_l, 6, _GOLD_DEEP, alpha=160)
        rounded_rect(surf, cap_r, 6, _GOLD_DEEP, alpha=160)
        self.tab_chev_l = cap_l
        self.tab_chev_r = cap_r
        _draw_chevron(surf, cap_l, -1)
        _draw_chevron(surf, cap_r, 1)

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
            # Raised carved segment: shadow first so the body sits proud of it.
            seg = pygame.Rect(r.x + 2, _TAB_Y - 10, r.w - 4, 20)
            _drop_shadow(surf, seg, 8, blur=3, alpha=70)
            surf.blit(_vgrad_panel(seg.w, seg.h, 8, (100, 72, 28), (64, 44, 16), 245),
                      seg.topleft)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 210), seg, width=1, border_radius=8)
            pygame.draw.line(surf, (*_GOLD_PALE, 50),
                             (seg.x + 3, seg.y + 1), (seg.right - 4, seg.y + 1))
            timg = f.render(label, True, NEAR_BLACK)
            surf.blit(timg, timg.get_rect(center=r.center))
        else:
            timg = f.render(label, True, _GOLD_PALE)
            timg.set_alpha(180)
            surf.blit(timg, timg.get_rect(center=r.center))
        cx += w + gap
    surf.set_clip(prev_clip)


st.StoreScene._draw_tabs = my_draw_tabs
scene = st.StoreScene(); scene.view = "category"; scene.tab = 0; scene.page = 0
surf = pygame.Surface((W, H)); scene.render(surf)

strip = surf.subsurface(pygame.Rect(0, 70, W, 42))
strip_tall = pygame.transform.smoothscale(strip, (W, 126))
lf = _font(11, True)
lt = lf.render("SEGMENTED-BAR — tab strip close-up (3x vertical)", True, (180, 200, 255))
canvas = pygame.Surface((W, H + 16 + lt.get_height() + 4 + 126))
canvas.fill((8, 8, 20))
canvas.blit(surf, (0, 0)); canvas.blit(lt, (8, H + 8))
canvas.blit(strip_tall, (0, H + 16 + lt.get_height() + 4))

import os as _os; _os.makedirs("/home/user/skybit/docs/store_tab_strip_redesign/segmented-bar", exist_ok=True)
out = "/home/user/skybit/docs/store_tab_strip_redesign/segmented-bar/round_1.png"
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
