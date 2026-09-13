import os; os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame; pygame.init(); pygame.display.set_mode((360, 640), pygame.NOFRAME)
import sys; sys.path.insert(0, "/home/user/skybit")
from game.config import W, H
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP
from game.draw import lerp_color, rounded_rect, NEAR_BLACK, WHITE
from game.store import _vgrad_panel, _drop_shadow, _gradient_text, _TAB_Y, _TABS
import game.store_data as sd
import game.store as st
sd.load(); sd._STATE["wallet"] = 12340


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

    # Two passes: inactive capsules first, active capsule + label on top so the
    # bright pill and its dark label are never clipped by a neighbour's wash.
    active_r = None
    cx = 0
    for i, (label, _g) in enumerate(_TABS):
        w = widths[i]
        r = pygame.Rect(round(vp.x + cx - self.tab_scroll), _TAB_Y - 13, w, 26)
        self.tab_rects.append(r)
        if i == self.tab:
            active_r = r
        else:
            wash = r.inflate(-2, -4)
            pygame.draw.rect(surf, (*_GOLD_PALE, 38), wash, width=0, border_radius=11)
            pygame.draw.rect(surf, (*_GOLD_DEEP, 70), wash, width=1, border_radius=11)
            timg = f.render(label, True, _GOLD_PALE)
            timg.set_alpha(190)
            surf.blit(timg, timg.get_rect(center=r.center))
        cx += w + gap

    if active_r is not None:
        label = _TABS[self.tab][0]
        cap = active_r.inflate(-2, -4)
        _drop_shadow(surf, cap, 11, blur=3, alpha=80)
        surf.blit(_vgrad_panel(cap.w, cap.h, 11, (80, 58, 22), (48, 32, 12), 242),
                  cap.topleft)
        pygame.draw.rect(surf, (*_GOLD_BRIGHT, 200), cap, width=1, border_radius=11)
        # Inner highlight kissing the top edge reads as a lit bevel on the pill.
        pygame.draw.line(surf, (*_GOLD_PALE, 60),
                         (cap.x + 6, cap.y + 1), (cap.right - 6, cap.y + 1))
        timg = f.render(label, True, NEAR_BLACK)
        surf.blit(timg, timg.get_rect(center=active_r.center))

    surf.set_clip(prev_clip)

    self.tab_chev_l = self.tab_chev_r = None
    if overflow and self.tab_scroll > 1:
        self.tab_chev_l = pygame.Rect(full_vp.x, full_vp.y, chev, 26)
        st._draw_chevron(surf, self.tab_chev_l, -1)
    if overflow and self.tab_scroll < max_scroll - 1:
        self.tab_chev_r = pygame.Rect(full_vp.right - chev, full_vp.y, chev, 26)
        st._draw_chevron(surf, self.tab_chev_r, 1)


st.StoreScene._draw_tabs = my_draw_tabs
scene = st.StoreScene(); scene.view = "category"; scene.tab = 0; scene.page = 0
surf = pygame.Surface((W, H)); scene.render(surf)

# Compose: full screen + 3× vertical strip crop
strip = surf.subsurface(pygame.Rect(0, 70, W, 42))
strip_tall = pygame.transform.smoothscale(strip, (W, 126))
lf = _font(11, True)
lt = lf.render("PILL-CAPSULE — tab strip close-up (3× vertical)", True, (180, 200, 255))
canvas = pygame.Surface((W, H + 16 + lt.get_height() + 4 + 126))
canvas.fill((8, 8, 20))
canvas.blit(surf, (0, 0))
canvas.blit(lt, (8, H + 8))
canvas.blit(strip_tall, (0, H + 16 + lt.get_height() + 4))

import os as _os; _os.makedirs("/home/user/skybit/docs/store_tab_strip_redesign/pill-capsule", exist_ok=True)
out = "/home/user/skybit/docs/store_tab_strip_redesign/pill-capsule/round_1.png"
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
