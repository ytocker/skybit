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

# Review the full 7-tab strip (incl. overflow chevrons) even though some stalls
# are closed on this branch, so the concept is judged on the real spec.
st._TABS = tuple((lbl, g) for lbl, g in (
    ("COSTUMES", "costume"), ("PARROTS", "parrot"), ("ANIMALS", "animal"),
    ("SHOES", "shoes"), ("HATS", "hats"), ("SHADES", "shades"),
    ("PARCELS", "parcels"),
))


def my_draw_tabs(self, surf):
    """underline-indicator: no fill on any tab. Active state is signalled ONLY
    by a 2px left→right gold-gradient underline (deep→bright→pale) with a soft
    additive glow and a subtle diamond gem end-cap. Inactive labels are pale
    gold at low alpha — the moving underline carries the whole affordance."""
    _TABS = st._TABS
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

        # Label first — no pill, no border on either state.
        if active:
            timg = f.render(label, True, _GOLD_BRIGHT)
        else:
            timg = f.render(label, True, _GOLD_PALE)
            timg.set_alpha(160)
        tr = timg.get_rect(center=r.center)
        surf.blit(timg, tr)

        if active:
            bar_w = timg.get_width() + 4
            bar_y = _TAB_Y + 9

            # Faint additive halo under the bar so the gold reads as lit, not painted.
            glow = pygame.Surface((bar_w + 8, 8), pygame.SRCALPHA)
            gcx = (bar_w + 8) / 2
            for gx in range(bar_w + 8):
                a = int(60 * (1 - abs(gx - gcx) / gcx))
                if a > 0:
                    pygame.draw.line(glow, (255, 200, 60, a), (gx, 0), (gx, 7))
            surf.blit(glow, (tr.x - 6, bar_y - 3), special_flags=pygame.BLEND_ADD)

            # The one active signal: 2px underline, colour + alpha shifting L→R.
            bar = pygame.Surface((bar_w, 2), pygame.SRCALPHA)
            third = bar_w / 3.0
            half = bar_w / 2.0
            for bx in range(bar_w):
                if bx < third:
                    col = lerp_color(_GOLD_DEEP, _GOLD_BRIGHT, bx / third)
                else:
                    col = lerp_color(_GOLD_BRIGHT, _GOLD_PALE, (bx - third) / (bar_w - third))
                if bx < half:
                    a = int(160 + (255 - 160) * (bx / half))
                else:
                    a = int(255 + (180 - 255) * ((bx - half) / half))
                bar.set_at((bx, 0), (*col, a))
                bar.set_at((bx, 1), (*col, a))
            surf.blit(bar, (tr.x - 2, bar_y))

            # Tiny diamond gem end-cap — a lit terminal, kept subtle.
            gem_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.rect(gem_surf, (*_GOLD_PALE, 200), (1, 1, 4, 4))
            gem = pygame.transform.rotate(gem_surf, 45)
            surf.blit(gem, gem.get_rect(center=(tr.x - 2 + bar_w, bar_y + 1)))

        cx += w + gap
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

strip = surf.subsurface(pygame.Rect(0, 70, W, 42))
strip_tall = pygame.transform.smoothscale(strip, (W, 126))
lf = _font(11, True)
lt = lf.render("UNDERLINE-INDICATOR — tab strip close-up (3× vertical)", True, (180, 200, 255))
canvas = pygame.Surface((W, H + 16 + lt.get_height() + 4 + 126))
canvas.fill((8, 8, 20))
canvas.blit(surf, (0, 0)); canvas.blit(lt, (8, H + 8))
canvas.blit(strip_tall, (0, H + 16 + lt.get_height() + 4))

import os as _os; _os.makedirs("/home/user/skybit/docs/store_tab_strip_redesign/underline-indicator", exist_ok=True)
out = "/home/user/skybit/docs/store_tab_strip_redesign/underline-indicator/round_1.png"
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
