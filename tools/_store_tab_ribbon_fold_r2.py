import os; os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame; pygame.init(); pygame.display.set_mode((360, 640), pygame.NOFRAME)
import sys; sys.path.insert(0, "/home/user/skybit")
from game.config import W, H
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP
from game.draw import lerp_color, NEAR_BLACK
from game.store import _drop_shadow, _TAB_Y, _TABS, _draw_chevron
import game.store_data as sd
import game.store as st
sd.load(); sd._STATE["wallet"] = 12340

# Three-tier value ladder so ribbons read at a glance:
#   near-black background   luma ~11
#   warm-brown inactive     luma ~58  (was ~30 — invisible in r1)
#   lit-gold active         luma ~200 top gradient apex
_GOLD_ACT_TOP  = (255, 224, 120)  # active gradient apex — top of banner, lit
_GOLD_ACT_BOT  = (238, 176,  44)  # active gradient base — deep amber
_INACTIVE_FILL = ( 82,  60,  32)  # luma ~58; clearly readable over bg luma ~11
_INACTIVE_RIM  = (180, 130,  20)  # _GOLD_DEEP-equivalent at full opacity (r1 was alpha 130)

# Own the full 24 px slot — 2 px dead space top+bottom in r1 removed.
_TAB_TOP = 80
_TAB_BOT = 104

# Swallowtail geometry: top narrower (_TI), bites inward at mid (_ND > _TI),
# expands to full width at bottom. Three-point V on each side reads "ribbon"
# far more strongly than a shallow trapezoid at this 24 px height.
_TI = 6   # top inset from outer edge (taper)
_ND = 9   # notch depth from outer edge at mid-height (bite deeper than taper)


def _sw_offset(dy, h):
    """Left-edge offset from rect.x at scanline dy inside the swallowtail.
    Upper half: taper corner → notch tip.  Lower half: notch tip → full width."""
    half = h // 2
    if dy <= half:
        return _TI + (_ND - _TI) * dy / max(1, half)
    return _ND * (1.0 - (dy - half) / max(1, h - half))


def _ribbon_scanlines(surf, r, top_color, bot_color):
    """Gradient fill for the swallowtail polygon, one scanline at a time.
    Tracking the polygon edge per row means no SRCALPHA surface or mask blit
    is needed — the fill never leaks outside the shape."""
    h = _TAB_BOT - _TAB_TOP
    for dy in range(h + 1):
        y   = _TAB_TOP + dy
        t   = dy / max(1, h)
        col = lerp_color(top_color, bot_color, t)
        ox  = _sw_offset(dy, h)
        lx  = round(r.x + ox)
        rx  = round(r.x + r.w - ox)
        if rx > lx:
            pygame.draw.line(surf, col, (lx, y), (rx, y))


def _ribbon_outline(surf, r, color):
    """1 px outline of the swallowtail polygon — same six-point geometry as
    the scanline fill so the outline hugs the fill exactly."""
    h     = _TAB_BOT - _TAB_TOP
    mid_y = _TAB_TOP + h // 2
    pts   = [
        (r.x + _TI,        _TAB_TOP),
        (r.x + r.w - _TI,  _TAB_TOP),
        (r.x + r.w - _ND,  mid_y),
        (r.x + r.w,        _TAB_BOT),
        (r.x,              _TAB_BOT),
        (r.x + _ND,        mid_y),
    ]
    pygame.draw.polygon(surf, color, pts, width=1)


def _fold_seam(surf, r):
    """Highlight/shadow pair at the ribbon centre reads as a physical fold.
    Drawn directly on surf (no SRCALPHA needed) — pale left, deep right."""
    mx = r.x + r.w // 2
    pygame.draw.line(surf, _GOLD_PALE, (mx - 1, _TAB_TOP), (mx - 1, _TAB_BOT))
    pygame.draw.line(surf, _GOLD_DEEP, (mx,     _TAB_TOP), (mx,     _TAB_BOT))


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

    # Two-pass: inactive ribbons first, active ribbon on top with drop shadow
    # so the lit gold never sits under a neighbour body.
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

        # Solid fill + warm gold rim, both at full alpha — luma ~58 over bg ~11.
        _ribbon_scanlines(surf, r, _INACTIVE_FILL, _INACTIVE_FILL)
        _ribbon_outline(surf, r, _INACTIVE_RIM)
        timg = f.render(label, True, _GOLD_PALE)
        timg.set_alpha(175)
        surf.blit(timg, timg.get_rect(center=r.center))

    if active_slot is not None:
        r, label = active_slot
        # Drop shadow behind the active ribbon so it floats above its neighbours.
        _drop_shadow(surf, pygame.Rect(r.x, _TAB_TOP - 2, r.w, _TAB_BOT - _TAB_TOP + 4),
                     4, blur=3, alpha=100)
        # Vertical gradient turns a flat chip into a lit banner.
        _ribbon_scanlines(surf, r, _GOLD_ACT_TOP, _GOLD_ACT_BOT)
        _ribbon_outline(surf, r, _GOLD_PALE)
        _fold_seam(surf, r)
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
lt = lf.render("RIBBON-FOLD  round_2", True, (255, 220, 80))
canvas = pygame.Surface((W, H + 16 + lt.get_height() + 4 + 126))
canvas.fill((8, 8, 20))
canvas.blit(surf, (0, 0))
canvas.blit(lt, (8, H + 8))
canvas.blit(strip_tall, (0, H + 16 + lt.get_height() + 4))

import os as _os; _os.makedirs("/home/user/skybit/docs/store_tab_strip_redesign/ribbon-fold", exist_ok=True)
out = "/home/user/skybit/docs/store_tab_strip_redesign/ribbon-fold/round_2.png"
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
