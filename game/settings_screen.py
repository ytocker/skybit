"""
Settings screen — a full-screen list of launchers, in the achievements-screen
family (night-sky bg + gilded header + grounded MENU pill). Today it holds two
items, How to Play and Power-Ups, each a tappable row that opens the matching
scene; it is laid out to take more rows later (audio, reduced-motion, …) without
a redesign. Pure procedural render; no target-divergent code.
"""
from __future__ import annotations

import math
import random

import pygame

from game import prefs
from game.config import W, H
from game.draw import lerp_color
from game.hud import (
    _font, _outlined_text, _outline_pill_btn, _volume_panel, _draw_gear,
    _draw_overlay_stars, _draw_mountain_silhouette,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _NIGHT_DEEP,
)

_WHITE    = (245, 246, 255)
_DIM      = (150, 150, 172)
_NAVY_INK = (10, 6, 30)          # near-black ink for glyphs on the gold discs

_HEADER_H = 56
_FOOTER_H = 54


# Seeded twinkle field so Settings lives in the same night world as the menu +
# achievements wall (same seed-42 discipline).
_STARS: list = []
def _star_field():
    if not _STARS:
        rng = random.Random(42)
        for _ in range(46):
            _STARS.append((rng.randint(6, W - 6), rng.randint(8, H - 150),
                           rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28)))
    return _STARS


def _section_header(surf, text, y):
    """Gold diamond pip + tracked caps + a fading engraved rule — the
    achievements category band, so the group reads as one system."""
    py = y + 9
    d = 4
    px0 = 14
    pip = [(px0, py), (px0 + d, py - d), (px0 + 2 * d, py), (px0 + d, py + d)]
    pygame.draw.polygon(surf, _GOLD_BRIGHT, pip)
    pygame.draw.polygon(surf, _GOLD_DEEP, pip, 1)
    lab = _font(14, True).render(text, True, _GOLD_BRIGHT)
    lx = px0 + 3 * d
    surf.blit(lab, (lx, y + 1))
    rail_l = lx + lab.get_width() + 8
    rail_r = W - 12
    if rail_r > rail_l:
        rail = pygame.Surface((rail_r - rail_l, 2), pygame.SRCALPHA)
        for xx in range(rail.get_width()):
            fade = 1.0 - xx / max(1, rail.get_width())
            rail.fill((*_GOLD_BRIGHT, int(150 * fade)), (xx, 0, 1, 2))
        surf.blit(rail, (rail_l, py))


def _chevron(surf, cx, cy, s, color, w=3):
    pygame.draw.line(surf, color, (cx - s * 0.35, cy - s), (cx + s * 0.4, cy), w)
    pygame.draw.line(surf, color, (cx + s * 0.4, cy), (cx - s * 0.35, cy + s), w)


def _icon_disc(surf, cx, cy, r):
    """Gold coin-like backer the row glyph sits on — a struck disc, top-lit body
    gradient + a dark rim (no highlight dot, so the disc reads clean)."""
    disc = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    cc = r + 2
    for yy in range(r * 2):
        f = yy / max(1, r * 2 - 1)
        col = lerp_color(_GOLD_PALE, _GOLD_DEEP, f)
        half = int(math.sqrt(max(0, r * r - (yy - r) ** 2)))
        pygame.draw.line(disc, col, (cc - half, yy + 2), (cc + half, yy + 2))
    pygame.draw.circle(disc, _GOLD_DEEP, (cc, cc), r, 2)
    surf.blit(disc, (cx - cc, cy - cc))


def _g_book(surf, cx, cy, s, ink=_NAVY_INK):
    left = [(cx, cy - s * 0.8), (cx - s, cy - s * 0.5),
            (cx - s, cy + s * 0.8), (cx, cy + s * 0.5)]
    right = [(cx, cy - s * 0.8), (cx + s, cy - s * 0.5),
             (cx + s, cy + s * 0.8), (cx, cy + s * 0.5)]
    pygame.draw.polygon(surf, ink, left, 2)
    pygame.draw.polygon(surf, ink, right, 2)
    pygame.draw.line(surf, ink, (cx, cy - s * 0.8), (cx, cy + s * 0.5), 2)
    for k in range(1, 3):
        yy = cy - s * 0.35 + k * s * 0.4
        pygame.draw.line(surf, ink, (cx - s * 0.75, yy), (cx - s * 0.2, yy + 0.15 * s), 1)
        pygame.draw.line(surf, ink, (cx + s * 0.2, yy + 0.15 * s), (cx + s * 0.75, yy), 1)


def _g_bolt(surf, cx, cy, s, ink=_NAVY_INK):
    pts = [
        (cx + s * 0.18, cy - s),
        (cx - s * 0.55, cy + s * 0.12),
        (cx - s * 0.05, cy + s * 0.12),
        (cx - s * 0.22, cy + s),
        (cx + s * 0.55, cy - s * 0.18),
        (cx + s * 0.05, cy - s * 0.18),
    ]
    pygame.draw.polygon(surf, ink, pts)
    pygame.draw.polygon(surf, _NAVY_INK, pts, 1)


def _g_sound(surf, cx, cy, s, ink=_NAVY_INK):
    # Speaker box + cone + two sound-wave arcs.
    box = [(cx - s * 0.75, cy - s * 0.3), (cx - s * 0.3, cy - s * 0.3),
           (cx + s * 0.1, cy - s * 0.7), (cx + s * 0.1, cy + s * 0.7),
           (cx - s * 0.3, cy + s * 0.3), (cx - s * 0.75, cy + s * 0.3)]
    pygame.draw.polygon(surf, ink, box)
    for k in (0.45, 0.8):
        pygame.draw.arc(surf, ink,
                        (int(cx + s * 0.1 - s * k), int(cy - s * k),
                         int(s * k * 2), int(s * k * 2)),
                        -0.7, 0.7, 2)


def _g_info(surf, cx, cy, s, ink=_NAVY_INK):
    # A classic "i" mark — a dot over a rounded stem.
    pygame.draw.circle(surf, ink, (int(cx), int(cy - s * 0.55)), max(2, int(s * 0.2)))
    bar = pygame.Rect(int(cx - s * 0.18), int(cy - s * 0.15),
                      max(3, int(s * 0.36)), int(s * 0.9))
    pygame.draw.rect(surf, ink, bar, border_radius=max(1, int(s * 0.14)))


_GLYPHS = {"book": _g_book, "bolt": _g_bolt, "sound": _g_sound, "info": _g_info}


def _toggle(surf, cx, cy, on):
    """A rounded on/off switch. ON = gold track + knob at right (sound plays);
    OFF = pewter track + knob at left (muted). Returns its rect."""
    tw, th = 46, 24
    rect = pygame.Rect(cx - tw // 2, cy - th // 2, tw, th)
    pygame.draw.rect(surf, _GOLD_BRIGHT if on else (66, 62, 92), rect,
                     border_radius=th // 2)
    pygame.draw.rect(surf, (10, 6, 30), rect, 2, border_radius=th // 2)
    kr = th // 2 - 3
    kx = rect.right - kr - 4 if on else rect.left + kr + 4
    pygame.draw.circle(surf, (245, 246, 255) if on else (150, 150, 172), (kx, cy), kr)
    pygame.draw.circle(surf, (10, 6, 30), (kx, cy), kr, 1)
    return rect


class SettingsScene:
    """Grouped settings list. Taps route through App._flap_input, which
    hit-tests the row rects + MENU button this scene publishes each frame.
    Row types: 'nav' (opens a scene, drawn with a chevron) and 'toggle' (an
    on/off switch — the Sound row reflects prefs.get_muted())."""

    # (section title, rows), each row: (icon, label, subtitle, action, type).
    SECTIONS = (
        ("HELP", (
            ("book",  "How to Play",   "Controls & the basics",  "howto",        "nav"),
            ("bolt",  "Power-Ups",     "What every pickup does",  "powerups",     "nav"),
        )),
        ("GENERAL", (
            ("sound", "Sound Effects", "Mute all game audio",     "toggle_sound", "toggle"),
            ("info",  "About",         "Credits & version",       "about",        "nav"),
        )),
    )

    def __init__(self):
        self._t = 0.0
        # Published each frame for the tap router: [(rect, action), …] + MENU.
        self.row_rects: list = []
        self.menu_btn_rect: "pygame.Rect | None" = None

    def update(self, dt: float) -> None:
        self._t += dt

    def render(self, surf, dt: float) -> None:
        # Background — the menu/achievements night world.
        for yy in range(H):
            f = yy / (H - 1)
            pygame.draw.line(surf, lerp_color(_NIGHT_DEEP, (14, 8, 36), f),
                             (0, yy), (W, yy))
        _draw_overlay_stars(surf, _star_field(), self._t)
        _draw_mountain_silhouette(surf, alpha=130)

        # Header — a struck cog + outlined SETTINGS + gold underline rule.
        hdr = pygame.Surface((W, _HEADER_H), pygame.SRCALPHA)
        hdr.fill((*_NIGHT_DEEP, 235))
        surf.blit(hdr, (0, 0))
        _draw_gear(surf, 26, 22, 11)
        _outlined_text(surf, "SETTINGS", (W // 2, 16), size=22, px=2,
                       shadow_offset=(2, 3))
        uw = 152
        ux = W // 2 - uw // 2
        pygame.draw.line(surf, _GOLD_BRIGHT, (ux, 30), (ux + uw, 30), 2)
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 90),
                         (0, _HEADER_H - 1), (W, _HEADER_H - 1), 1)

        # Sectioned list, vertically centred in the open body.
        row_h, row_gap, sec_hdr, sec_gap = 58, 9, 28, 12
        content_h = 0
        for i, (_title, rows) in enumerate(self.SECTIONS):
            if i:
                content_h += sec_gap
            content_h += sec_hdr + len(rows) * row_h + (len(rows) - 1) * row_gap
        body_top, body_bot = _HEADER_H, H - _FOOTER_H
        y = body_top + max(14, (body_bot - body_top - content_h) // 2)

        muted = prefs.get_muted()
        self.row_rects = []
        for i, (title, rows) in enumerate(self.SECTIONS):
            if i:
                y += sec_gap
            _section_header(surf, title, y)
            y += sec_hdr
            for j, (kind, label, sub, action, rtype) in enumerate(rows):
                rect = pygame.Rect(6, y, W - 12, row_h)
                _volume_panel(surf, rect, radius=13)
                cy = rect.centery
                _icon_disc(surf, 42, cy, 20)
                _GLYPHS[kind](surf, 42, cy, 12)
                surf.blit(_font(17, True).render(label, True, _GOLD_PALE), (76, rect.y + 11))
                surf.blit(_font(11, True).render(sub, True, _DIM), (76, rect.y + 33))
                if rtype == "toggle":
                    _toggle(surf, W - 36, cy, not muted)   # ON = sound plays
                else:
                    _chevron(surf, W - 28, cy, 8, _GOLD_BRIGHT)
                self.row_rects.append((rect, action))
                y += row_h + (row_gap if j < len(rows) - 1 else 0)

        # Footer — the grounded MENU pill, the only way back.
        fy = H - _FOOTER_H
        ftr = pygame.Surface((W, _FOOTER_H), pygame.SRCALPHA)
        ftr.fill((*_NIGHT_DEEP, 236))
        surf.blit(ftr, (0, fy))
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 120), (0, fy), (W, fy), 1)
        self.menu_btn_rect = _outline_pill_btn(
            surf, (W // 2, fy + _FOOTER_H // 2), "MENU", size=15, min_width=150)
