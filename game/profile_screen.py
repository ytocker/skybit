"""PROFILE — the shared parent screen for WARDROBE and ACHIEVEMENTS.

The two are siblings behind one entry point (the main menu's PROFILE
card): a shared header ("PROFILE" wordmark, 0-40px) and a WARDROBE /
ACHIEVEMENTS segmented pill (40-72px) are always drawn here; content below
belongs to whichever tab is active. WARDROBE's own content starts right
at y=72 (it has no per-tab sub-control). ACHIEVEMENTS keeps its own real
FAME/SHAME toggle — rather than lose it under the shared pill, this
scene tells AchievementsScene to draw that toggle at y=72-104 instead of
its standalone y=40-72, so nothing about the real achievements screen's
own navigation is dropped (see AchievementsScene.embedded_top).

A single MENU footer button is drawn once here, shared by both tabs.
"""
from __future__ import annotations

import pygame

from game.config import W, H
from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text, _outline_pill_btn,
    _GOLD_BRIGHT, _GOLD_DEEP, _PANEL_DARK, _NIGHT_DEEP,
)
from game.wardrobe_screen import WardrobeScene
from game.achievements_screen import AchievementsScene
from game import achievements as ach

_HEADER_H = 40
_TAB_H = 32
# The FAME/SHAME toggle, when the ACHIEVEMENTS tab is active, is hosted at
# this y (see AchievementsScene.embedded_top) — right after our own pill.
_ACHV_EMBED_TOP = _HEADER_H + _TAB_H


class ProfileScene:
    def __init__(self):
        self.tab = "wardrobe"  # "wardrobe" | "achievements"
        self.wardrobe = WardrobeScene()
        self.achievements = AchievementsScene()
        self.achievements.embedded_top = _ACHV_EMBED_TOP

        self.tab_wardrobe_rect: "pygame.Rect | None" = None
        self.tab_achievements_rect: "pygame.Rect | None" = None
        self.menu_btn_rect: "pygame.Rect | None" = None

    def set_tab(self, name: str) -> None:
        if name not in ("wardrobe", "achievements") or name == self.tab:
            return
        self.tab = name

    # ── per-frame lifecycle ──────────────────────────────────────────────
    def update(self, dt: float) -> None:
        if self.tab == "wardrobe":
            self.wardrobe.update(dt)
        else:
            self.achievements.update(dt)

    def render(self, surf: pygame.Surface) -> None:
        if self.tab == "wardrobe":
            self.wardrobe.render(surf)
        else:
            self.achievements.render(surf, 1 / 60, ach.load())

        # Shared header + view-pill, drawn on top of whichever content just
        # rendered (both scenes leave y<72 either blank/transparent or, in
        # achievements' case, painted with its own now-embedded-elsewhere
        # background — this always wins the top band).
        hdr = pygame.Surface((W, _HEADER_H), pygame.SRCALPHA)
        hdr.fill((*_NIGHT_DEEP, 235))
        surf.blit(hdr, (0, 0))
        _outlined_text(surf, "PROFILE", (W // 2, 16), size=22, px=2, shadow_offset=(2, 3))
        uw = 152
        pygame.draw.line(surf, _GOLD_BRIGHT, (W // 2 - uw // 2, 30),
                         (W // 2 + uw // 2, 30), 2)

        band = pygame.Surface((W, _TAB_H), pygame.SRCALPHA)
        band.fill((*_NIGHT_DEEP, 235))
        surf.blit(band, (0, _HEADER_H))
        pad, gap = 10, 6
        seg_w = (W - pad * 2 - gap) // 2
        self.tab_wardrobe_rect = pygame.Rect(pad, _HEADER_H + 4, seg_w, _TAB_H - 8)
        self.tab_achievements_rect = pygame.Rect(pad + seg_w + gap, _HEADER_H + 4, seg_w, _TAB_H - 8)
        self._draw_tab(surf, self.tab_wardrobe_rect, "WARDROBE", self.tab == "wardrobe")
        self._draw_tab(surf, self.tab_achievements_rect, "ACHIEVEMENTS", self.tab == "achievements")
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 110), (0, _HEADER_H + _TAB_H - 1),
                         (W, _HEADER_H + _TAB_H - 1), 1)

        # One shared footer/MENU button, regardless of tab.
        fy = H - 54
        ftr = pygame.Surface((W, 54), pygame.SRCALPHA)
        ftr.fill((*_NIGHT_DEEP, 236))
        surf.blit(ftr, (0, fy))
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 120), (0, fy), (W, fy), 1)
        self.menu_btn_rect = _outline_pill_btn(
            surf, (W // 2, fy + 27), "MENU", size=15, min_width=150)

    def _draw_tab(self, surf, rect, label, active) -> None:
        rad = rect.h // 2
        if active:
            grad = pygame.Surface(rect.size, pygame.SRCALPHA)
            for yy in range(rect.h):
                t = yy / max(1, rect.h - 1)
                grad.fill((*lerp_color(_GOLD_BRIGHT, _GOLD_DEEP, t), 255), (0, yy, rect.w, 1))
            m = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(m, (255, 255, 255, 255), (0, 0, rect.w, rect.h), border_radius=rad)
            grad.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(grad, rect.topleft)
            pygame.draw.rect(surf, _GOLD_BRIGHT, rect, width=2, border_radius=rad)
            txt = _font(13, True).render(label, True, _NIGHT_DEEP)
        else:
            pygame.draw.rect(surf, (*_PANEL_DARK, 235), rect, border_radius=rad)
            pygame.draw.rect(surf, (*_GOLD_BRIGHT, 140), rect, width=1, border_radius=rad)
            txt = _font(13, True).render(label, True, _GOLD_BRIGHT)
            txt.set_alpha(150)
        surf.blit(txt, txt.get_rect(center=rect.center))

    # ── pointer routing (delegates to the active tab's own scene) ────────
    def pointer_down(self, pos) -> None:
        if self.tab == "wardrobe":
            self.wardrobe.pointer_down(pos[1])
        else:
            self.achievements.pointer_down(pos[1])

    def pointer_move(self, pos) -> None:
        if self.tab == "wardrobe":
            self.wardrobe.pointer_move(pos[1])
        else:
            self.achievements.pointer_move(pos[1])

    def pointer_up(self) -> bool:
        if self.tab == "wardrobe":
            return self.wardrobe.pointer_up()
        return self.achievements.pointer_up()

    def scroll_by(self, dpx: float) -> None:
        if self.tab == "wardrobe":
            self.wardrobe.scroll_by(dpx)
        else:
            self.achievements.scroll_by(dpx)

    def tap_or_close(self, pos) -> "str | None":
        """Resolve a stationary tap: our own view-pill first, then delegate
        into the active tab's own controls (FAME/SHAME toggle, rail
        buttons, item tiles), then the shared MENU button. Returns "close"
        if the caller should dismiss the whole PROFILE screen."""
        if self.tab_wardrobe_rect and self.tab_wardrobe_rect.collidepoint(pos):
            self.set_tab("wardrobe")
            return None
        if self.tab_achievements_rect and self.tab_achievements_rect.collidepoint(pos):
            self.set_tab("achievements")
            return None
        if self.tab == "wardrobe":
            self.wardrobe.handle_tap(pos)
        else:
            tf = self.achievements.tab_fame_rect
            ts = self.achievements.tab_shame_rect
            if tf and tf.collidepoint(pos):
                self.achievements.set_tab("fame")
                return None
            if ts and ts.collidepoint(pos):
                self.achievements.set_tab("shame")
                return None
        if self.menu_btn_rect and self.menu_btn_rect.collidepoint(pos):
            return "close"
        return None
