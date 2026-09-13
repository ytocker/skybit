import os; os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame; pygame.init(); pygame.display.set_mode((360, 640), pygame.NOFRAME)
import sys; sys.path.insert(0, "/home/user/skybit")
from game.config import W, H
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _GOLD_MUTED
from game.draw import lerp_color, rounded_rect, NEAR_BLACK, WHITE
from game.store import _vgrad_panel, _drop_shadow, _gradient_text, _TAB_Y, _TABS
import game.store_data as sd
import game.store as st

sd.load(); sd._STATE["wallet"] = 12340

# Force full 7-tab overflow so the concept is judged against the real spec.
st._TABS = tuple((lbl, g) for lbl, g in (
    ("COSTUMES", "costume"), ("PARROTS", "parrot"), ("ANIMALS", "animal"),
    ("SHOES", "shoes"), ("HATS", "hats"), ("SHADES", "shades"),
    ("PARCELS", "parcels"),
))

# Deeper than _GOLD_DEEP so the bar has a rich amber anchor on the left
# before the sweep brightens toward the right terminal.
_BAR_DEEP = (170, 120, 30)


def _draw_gem_faceted(surf, cx, cy, size=11):
    """Faceted diamond gem at each bar terminal.

    Top half is bright gold / near-white so the eye reads a lit crown; bottom
    half is deep gold so the form reads as a solid jewel rather than a flat
    diamond stamp.  A single-pixel white spec at the apex gives the glint that
    makes it feel hand-crafted.
    """
    h = size // 2
    # Extra 2-pixel padding so the 1px outline is never clipped.
    gs = pygame.Surface((size + 4, size + 4), pygame.SRCALPHA)
    gcx, gcy = h + 2, h + 2

    # Bottom half — deep amber grounds the gem.
    pygame.draw.polygon(gs, (*_GOLD_DEEP, 255),
                        [(gcx - h, gcy), (gcx + h, gcy), (gcx, gcy + h)])

    # Top half — bright gold base.
    pygame.draw.polygon(gs, (*_GOLD_BRIGHT, 255),
                        [(gcx, gcy - h), (gcx + h, gcy), (gcx - h, gcy)])

    # Near-white highlight on the upper-left face mimics a directional light
    # source consistent with the rest of the game's gold bevel vocabulary.
    pygame.draw.polygon(gs, (255, 248, 200, 145),
                        [(gcx, gcy - h), (gcx, gcy), (gcx - h, gcy)])

    # 1 px dark outline unifies the four facets as a single jewel.
    pygame.draw.polygon(gs, (120, 80, 10, 210),
                        [(gcx, gcy - h), (gcx + h, gcy),
                         (gcx, gcy + h), (gcx - h, gcy)], 1)

    # White apex spec — the single pixel that makes it read "lit."
    gs.set_at((gcx, gcy - h), (255, 255, 255, 255))

    surf.blit(gs, (cx - gcx, cy - gcy))


def my_draw_tabs(self, surf):
    """Underline-indicator r2.

    Changes from r1:
    - Gems at BOTH bar ends (not just right), with top-bright / bottom-deep
      facets and a white apex spec.
    - Bar is 3 px tall (was 2 px) with end-cap feathering so it butts cleanly
      into the gems.
    - Bar gradient anchors deeper on the left (_BAR_DEEP) for a dramatic sweep.
    - Additive halo is 2 px wider each side; centre alpha raised to 75.
    - Bloom ellipse added behind the active label glyphs via BLEND_ADD.
    - Inactive labels use _GOLD_MUTED at alpha 200 — warm gold, not gray.
    """
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

        if active:
            # Measure the label so the bloom ellipse fits the glyph footprint.
            timg = f.render(label, True, _GOLD_BRIGHT)
            tr = timg.get_rect(center=r.center)

            # Additive warm bloom behind the label glyphs — makes the active
            # text feel like it is emitting light, not just painted brighter.
            bloom_w = timg.get_width() + 24
            bloom_h = timg.get_height() + 12
            bloom = pygame.Surface((bloom_w, bloom_h), pygame.SRCALPHA)
            # Layer concentric ellipses from the outside in for a gaussian falloff.
            steps = 8
            for step in range(1, steps + 1):
                t = step / steps
                ew = max(1, int(bloom_w * t))
                eh = max(1, int(bloom_h * t))
                # Outer rings very faint; inner core slightly brighter.
                ea = int(48 * (1.0 - t))
                if ea > 0:
                    pygame.draw.ellipse(
                        bloom, (255, 200, 80, ea),
                        ((bloom_w - ew) // 2, (bloom_h - eh) // 2, ew, eh))
            surf.blit(bloom, bloom.get_rect(center=tr.center),
                      special_flags=pygame.BLEND_ADD)

            surf.blit(timg, tr)

        else:
            # _GOLD_MUTED reads as "soft gold" at alpha 200 over the dark panel
            # rather than the muddy-gray tan that _GOLD_PALE at alpha 160 gives.
            timg = f.render(label, True, _GOLD_MUTED)
            timg.set_alpha(200)
            tr = timg.get_rect(center=r.center)
            surf.blit(timg, tr)

        if active:
            bar_w = timg.get_width() + 4
            bar_x = tr.x - 2
            bar_y = _TAB_Y + 9   # = 101 for _TAB_Y=92

            # Additive halo 2 px wider each side than r1; centre alpha 75
            # so the glow halo reads at 1× scale, not only in the close-up strip.
            halo_w = bar_w + 14
            halo_h = 12
            glow = pygame.Surface((halo_w, halo_h), pygame.SRCALPHA)
            hcx = halo_w / 2
            for gx in range(halo_w):
                a = int(75 * (1.0 - abs(gx - hcx) / hcx))
                if a > 0:
                    pygame.draw.line(glow, (255, 200, 60, a), (gx, 0), (gx, halo_h - 1))
            surf.blit(glow, (bar_x - 7, bar_y - 4), special_flags=pygame.BLEND_ADD)

            # 3 px underline — deeper left anchor (_BAR_DEEP) ramps dramatically
            # to bright at 40 %, then fades toward pale at the right terminal.
            # End-cap rows (top/bottom) are feathered near each edge so they
            # butt cleanly against the gem silhouettes.
            bar = pygame.Surface((bar_w, 3), pygame.SRCALPHA)
            cap = 2
            for bx in range(bar_w):
                t = bx / (bar_w - 1) if bar_w > 1 else 0.0
                if t < 0.40:
                    col = lerp_color(_BAR_DEEP, _GOLD_BRIGHT, t / 0.40)
                else:
                    col = lerp_color(_GOLD_BRIGHT, _GOLD_PALE, (t - 0.40) / 0.60)
                # Alpha envelope peaks at the 40 % crossover.
                if t < 0.40:
                    a_full = int(195 + (255 - 195) * (t / 0.40))
                else:
                    a_full = int(255 + (175 - 255) * ((t - 0.40) / 0.60))
                # Cap feather: scale top/bottom rows near each end.
                if bx < cap:
                    cf = bx / cap
                elif bx >= bar_w - cap:
                    cf = (bar_w - 1 - bx) / cap
                else:
                    cf = 1.0
                a_edge = int(a_full * cf)
                bar.set_at((bx, 0), (*col, a_edge))
                bar.set_at((bx, 1), (*col, a_full))
                bar.set_at((bx, 2), (*col, a_edge))
            surf.blit(bar, (bar_x, bar_y))

            # Faceted diamond gems at both terminals — vertically centred on
            # the 3 px bar (bar_y + 1 = midpoint of rows 0..2).
            gem_y = bar_y + 1
            _draw_gem_faceted(surf, bar_x, gem_y)
            _draw_gem_faceted(surf, bar_x + bar_w, gem_y)

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
lt = lf.render("UNDERLINE-INDICATOR  round_2", True, (255, 220, 80))
canvas = pygame.Surface((W, H + 16 + lt.get_height() + 4 + 126))
canvas.fill((8, 8, 20))
canvas.blit(surf, (0, 0))
canvas.blit(lt, (8, H + 8))
canvas.blit(strip_tall, (0, H + 16 + lt.get_height() + 4))

import os as _os
_os.makedirs(
    "/home/user/skybit/docs/store_tab_strip_redesign/underline-indicator",
    exist_ok=True)
out = "/home/user/skybit/docs/store_tab_strip_redesign/underline-indicator/round_2.png"
pygame.image.save(canvas, out)
print(f"saved {canvas.get_width()}x{canvas.get_height()} -> {out}")
