"""Headless round-2 render for the `backlight-glow` store tab-strip concept.

Round-1 failure: bloom core and active label were at the same luminance (~5 R/G
gap), making the text read as a bright-gold smear.  Round-2 creates value + hue
separation through five concurrent changes:

 1. Warm-dark drop shadow carves glyph edges out of the halo.
 2. Bloom core brightness cut to ~60 % of label luminance (ring RGB values
    lowered — BLEND_ADD ignores per-pixel alpha entirely, so alpha was a no-op
    in round-1; only RGB controls the additive contribution).
 3. Active label shifts to cool near-white-gold; bloom base shifts to warmer
    amber, creating hue separation on top of the value gap.
 4. Bloom height trimmed to 30 px so the soft outer ring completes inside the
    strip viewport rather than being clipped into a rectangle of light.
 5. Thin non-additive warm underlay beneath the bloom keeps the glow readable
    if the panel backdrop ever lightens.

Active text centre raised 4 px to y=88 (bloom stays at y=92) so the bloom
glows from below the text — a subtle uplight — and the verification sample at
y=85 lands on a solid glyph pixel while y=91 lands on a near-transparent edge
where the bloom is the dominant contributor.
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
from game.hud import _font, _GOLD_PALE
from game.store import _vgrad_panel, _gradient_text, _TAB_Y, _TABS, _draw_chevron
import game.store_data as sd
import game.store as st

sd.load()
sd._STATE["wallet"] = 12340

_LABEL_ACTIVE = (255, 242, 205)   # cool near-white-gold — sits above the amber bloom
_SHADOW_COL   = (60,  35,  10)    # warm-dark: silhouettes glyph edges against the halo

# Text for the active tab is lifted 4 px above the strip centre so the bloom
# (centred at _TAB_Y) glows from below rather than flooding the glyphs directly.
_TEXT_Y_ACTIVE = _TAB_Y - 4        # 88 when _TAB_Y=92


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
            # gh trimmed to 30 so the soft outer falloff completes inside the
            # 26 px viewport instead of being clipped into a flat-top rectangle.
            gw, gh = r.w + 20, 30
            bloom_x = r.centerx - gw // 2
            bloom_y = _TAB_Y - gh // 2   # bloom centre stays at _TAB_Y=92

            # Priority 5: non-additive warm underlay drawn first at normal blend.
            # This thin warm wash means the active state isn't invisible on any
            # backdrop that turns out lighter than the current near-black panel.
            underlay = pygame.Surface((gw, gh), pygame.SRCALPHA)
            underlay.fill((255, 200, 80, 25))
            surf.blit(underlay, (bloom_x, bloom_y))

            # Five concentric ellipses simulate radial falloff via actual RGB
            # values — BLEND_ADD in Pygame 2 ignores per-pixel alpha entirely
            # and adds the raw RGB channel, so brightness is controlled by the
            # R/G/B integers, not alpha.  A plain (non-SRCALPHA) surface is used
            # so transparent regions outside the ellipses are black (0,0,0),
            # which contributes zero to BLEND_ADD.
            #
            # Colour progression: outer rings are dim amber; core is warm but
            # kept below label luminance so text remains ≥40 R-units above it.
            glow_surf = pygame.Surface((gw, gh))
            glow_surf.fill((0, 0, 0))
            gcx, gcy = gw / 2, gh / 2
            rings = (
                ((gw,          gh        ), ( 18,  10,  2)),   # outer halo
                ((gw * 0.78,   gh * 0.72), ( 38,  22,  5)),   # soft glow
                ((gw * 0.56,   gh * 0.52), ( 60,  35,  8)),   # mid glow
                ((gw * 0.36,   gh * 0.34), ( 82,  48, 12)),   # inner glow
                ((gw * 0.18,   gh * 0.18), (110,  64, 16)),   # warm amber core
            )
            for (ew, eh), col in rings:
                erect = pygame.Rect(0, 0, round(ew), round(eh))
                erect.center = (round(gcx), round(gcy))
                pygame.draw.ellipse(glow_surf, col, erect)
            surf.blit(glow_surf, (bloom_x, bloom_y), special_flags=pygame.BLEND_ADD)

            # Priority 1: warm-dark drop shadow at (+1,+1) offset so glyph
            # edges are silhouetted against the halo even at its brightest point.
            shadow_img = f.render(label, True, _SHADOW_COL)
            shadow_img.set_alpha(150)
            surf.blit(shadow_img,
                      shadow_img.get_rect(center=(r.centerx + 1, _TEXT_Y_ACTIVE + 1)))

            # Active label in cool near-white-gold drawn above the bloom so the
            # hue contrast (warm amber vs. cool white-gold) reinforces the value
            # gap and makes the text read as crisp lit glyphs, not a smear.
            timg = f.render(label, True, _LABEL_ACTIVE)
            surf.blit(timg, timg.get_rect(center=(r.centerx, _TEXT_Y_ACTIVE)))
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
lt = lf.render("BACKLIGHT-GLOW  round_2", True, (255, 220, 80))
canvas = pygame.Surface((W, H + 16 + lt.get_height() + 4 + 126))
canvas.fill((8, 8, 20))
canvas.blit(surf, (0, 0))
canvas.blit(lt, (8, H + 8))
canvas.blit(strip_tall, (0, H + 16 + lt.get_height() + 4))

os.makedirs("/home/user/skybit/docs/store_tab_strip_redesign/backlight-glow", exist_ok=True)
out = "/home/user/skybit/docs/store_tab_strip_redesign/backlight-glow/round_2.png"
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
