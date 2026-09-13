"""
About screen — reached from Settings → About. Same night-sky family as the
Settings and achievements screens (bg + gilded header + grounded MENU pill),
with a short block of credits + version. Pure procedural render.
"""
from __future__ import annotations

import random

import pygame

from game.config import W, H, VERSION
from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text, _outline_pill_btn,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_MUTED, _NIGHT_DEEP,
)

_WHITE = (238, 240, 252)
_DIM   = (168, 168, 190)

_HEADER_H = 56
_FOOTER_H = 54

_STARS: list = []
def _star_field():
    if not _STARS:
        rng = random.Random(42)
        for _ in range(46):
            _STARS.append((rng.randint(6, W - 6), rng.randint(8, H - 150),
                           rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28)))
    return _STARS


class AboutScene:
    """Static About page (credits + version). Publishes menu_btn_rect for the
    tap router."""

    # (text, font size, colour, extra gap above) — laid out top-down, then the
    # whole block is vertically centred in the body.
    LINES = (
        ("SKYBIT",                        26, _GOLD_BRIGHT, 0),
        ("Pocket Sky Flyer",              15, _GOLD_PALE,   2),
        (f"Version {VERSION}",            14, _GOLD_PALE,   8),
        ("The game was built using code",  12, _GOLD_MUTED,  6),
    )

    def __init__(self):
        self._t = 0.0
        self.menu_btn_rect: "pygame.Rect | None" = None

    def update(self, dt: float) -> None:
        self._t += dt

    def render(self, surf, dt: float) -> None:
        # Background — the shared night world.
        for yy in range(H):
            f = yy / (H - 1)
            pygame.draw.line(surf, lerp_color(_NIGHT_DEEP, (14, 8, 36), f),
                             (0, yy), (W, yy))
        _draw_overlay_stars(surf, _star_field(), self._t)
        _draw_mountain_silhouette(surf, alpha=130)

        # Header.
        hdr = pygame.Surface((W, _HEADER_H), pygame.SRCALPHA)
        hdr.fill((*_NIGHT_DEEP, 235))
        surf.blit(hdr, (0, 0))
        _outlined_text(surf, "ABOUT", (W // 2, 16), size=22, px=2,
                       shadow_offset=(2, 3))
        uw = 152
        ux = W // 2 - uw // 2
        pygame.draw.line(surf, _GOLD_BRIGHT, (ux, 30), (ux + uw, 30), 2)
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 90),
                         (0, _HEADER_H - 1), (W, _HEADER_H - 1), 1)

        # Attribution block, vertically centred in the body.
        rendered = [(_font(sz, True).render(txt, True, col), gap)
                    for (txt, sz, col, gap) in self.LINES]
        block_h = sum(img.get_height() + gap for img, gap in rendered)
        body_top, body_bot = _HEADER_H, H - _FOOTER_H
        y = body_top + (body_bot - body_top - block_h) // 2
        for img, gap in rendered:
            y += gap
            surf.blit(img, img.get_rect(center=(W // 2, y + img.get_height() // 2)))
            y += img.get_height()

        # Footer MENU pill (back to Settings).
        fy = H - _FOOTER_H
        ftr = pygame.Surface((W, _FOOTER_H), pygame.SRCALPHA)
        ftr.fill((*_NIGHT_DEEP, 236))
        surf.blit(ftr, (0, fy))
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 120), (0, fy), (W, fy), 1)
        self.menu_btn_rect = _outline_pill_btn(
            surf, (W // 2, fy + _FOOTER_H // 2), "MENU", size=15, min_width=150)
