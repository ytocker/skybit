"""Headless candidate-sheet renderer for the Achievements visual loop.

Composes (A) the full Achievements screen in a representative state and (B) a
truthful state grid: the 12 normal glyphs only ever appear unlocked + dormant
(they have no hidden look), and the 6 Mysteries appear unlocked (amethyst well)
+ hidden-locked (amethyst "?"). Not shipped — lives under tools/, out of the
bundle.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

from game import achievements as ach
from game.achievements_screen import AchievementsScene
from game.achievement_icons import draw_badge
from game.hud import _font, _outlined_text, _GOLD_PALE, _GOLD_BRIGHT, _GOLD_DEEP, _NIGHT_DEEP

# ── representative store: a spread of unlocked + progress ────────────────────
store = ach._blank()
for i, a in enumerate(ach.ACHIEVEMENTS):
    if i % 3 == 0:
        store["unlocked"][a.id] = 1
# unlock one hidden so a secret medallion appears in the grid + list
store["unlocked"]["made_a_wish"] = 1
store["life"]["total_coins"] = 240
store["life"]["total_flaps"] = 2600
store["life"]["powerups_seen"] = {"magnet": 9}

# (A) screen
scr = pygame.Surface((360, 640), pygame.SRCALPHA)
sc = AchievementsScene()
sc.scroll_offset = 0.0
for _ in range(2):
    sc.render(scr, 1 / 60, store)

# (B) badge grid — two truthful panels:
#   • the 12 NORMAL glyphs, shown unlocked + dormant only (no hidden state).
#   • the 6 MYSTERIES, shown unlocked (amethyst well) + hidden-locked ("?").
normal_keys = ["pillar", "coin", "day", "score", "powerup", "magnet",
               "kfc", "nerve", "clock", "storm", "wing", "skate"]
mystery_keys = ["genie", "knight", "treasure", "lottery", "rail", "poison"]

cell = 92
label_h = 16
BADGE = 56


def _bg(surf):
    w, h = surf.get_size()
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = (int(8 + 8 * t), int(6 + 6 * t), int(26 + 14 * t))
        pygame.draw.line(surf, c, (0, yy), (w, yy))


def make_section(title, keys, cols, draw_states):
    """draw_states: list of (state_title, fn(grid, key, rect)). Renders one row
    band per state, stacked, with a section caption."""
    rows = (len(keys) + cols - 1) // cols
    gw = cols * cell
    band_h = rows * (cell + label_h) + 30
    gh = 26 + band_h * len(draw_states)
    sec = pygame.Surface((gw, gh), pygame.SRCALPHA)
    _bg(sec)
    cap = _font(16, True).render(title, True, _GOLD_BRIGHT)
    sec.blit(cap, (10, 4))
    for bi, (state_title, fn) in enumerate(draw_states):
        top = 26 + bi * band_h
        lab = _font(14, True).render(state_title, True, _GOLD_PALE)
        sec.blit(lab, (10, top))
        y0 = top + 22
        for idx, k in enumerate(keys):
            r, c = divmod(idx, cols)
            cx = c * cell + cell // 2
            cy = y0 + r * (cell + label_h) + cell // 2 - 6
            rect = pygame.Rect(cx - BADGE // 2, cy - BADGE // 2, BADGE, BADGE)
            fn(sec, k, rect)
            tl = _font(11, True).render(k, True, (210, 210, 230))
            sec.blit(tl, tl.get_rect(center=(cx, cy + BADGE // 2 + 8)))
    return sec


normal_sec = make_section(
    "12 NORMAL GLYPHS", normal_keys, 6,
    [("UNLOCKED", lambda g, k, rr: draw_badge(g, k, rr, True, False)),
     ("DORMANT (locked)", lambda g, k, rr: draw_badge(g, k, rr, False, False))])

mystery_sec = make_section(
    "6 MYSTERIES (hidden tier)", mystery_keys, 6,
    [("UNLOCKED (amethyst)", lambda g, k, rr: draw_badge(g, k, rr, True, True)),
     ("HIDDEN + LOCKED (?)", lambda g, k, rr: draw_badge(g, k, rr, False, True))])

# Stack the two sections into the grid surface.
GW = max(normal_sec.get_width(), mystery_sec.get_width())
GH = normal_sec.get_height() + 20 + mystery_sec.get_height()
grid = pygame.Surface((GW, GH), pygame.SRCALPHA)
_bg(grid)
grid.blit(normal_sec, (0, 0))
grid.blit(mystery_sec, (0, normal_sec.get_height() + 20))

# ── compose A + B side by side with a caption banner ────────────────────────
pad = 16
cap_h = 38
sheet_w = 360 + pad * 3 + GW
sheet_h = max(640, GH) + cap_h + pad
sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill((5, 4, 16))

# Drop the leading "ACHIEVEMENTS" word — it stutters directly above the
# screen's own ACHIEVEMENTS wordmark in panel (A).
cap = _font(18, True).render(
    "Courier's Commendation  ·  round 3", True, _GOLD_BRIGHT)
sheet.blit(cap, (pad, pad - 2))

sheet.blit(scr, (pad, cap_h + pad // 2))
# label A
la = _font(12, True).render("(A) screen", True, _GOLD_DEEP)
sheet.blit(la, (pad, cap_h + pad // 2 + 640 + 2))

gx = pad * 2 + 360
sheet.blit(grid, (gx, cap_h + pad // 2))
lb = _font(12, True).render(
    "(B) 12 normal (unlocked+dormant) · 6 Mysteries (unlocked+hidden)",
    True, _GOLD_DEEP)
sheet.blit(lb, (gx, cap_h + pad // 2 + GH + 2))

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "docs", "achievements", "round_3.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
