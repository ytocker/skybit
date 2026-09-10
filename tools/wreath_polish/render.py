"""
Headless render harness for the wreath-polish round. For each of the 5
variations, lays out a figure showing:
  Fame hero (~170px) + Fame ROW-STRIP (real 44px badge in a 56px row) +
  Shame hero + Shame ROW-STRIP.
The row-strip is the proof the leaves fit on screen at the live row size.

Run:  PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/wreath_polish/render.py
"""
from __future__ import annotations

import os
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()
pygame.font.init()

import game.achievement_icons as ai  # noqa: E402
from game.draw import lerp_color  # noqa: E402
from tools.wreath_polish.concepts import VARIATIONS, compose  # noqa: E402

# Live row dims from achievements_screen.py
_ROW_H = 56
_BADGE = 44
_PAD_X = 12

_NIGHT = (10, 6, 24)
_PANEL_LIGHTER = (40, 32, 70)
_PANEL_DARK = (20, 14, 44)
_GOLD_PALE = (255, 226, 150)
_WHITE = (240, 242, 255)
_BRONZE_PALE = (228, 182, 130)
_SHAME_DIM = (180, 150, 120)

HERO = 170
ICONS = {  # Fame uses pillar_100, Shame uses goose_egg per the brief
    "fame": "pillar_100",
    "shame": "goose_egg",
}


def _font(px, bold=True):
    return pygame.font.SysFont(None, px, bold=bold)


def _row_strip(width, title, shame, wreath_fn):
    """A real achievements row: rounded card, 44px badge, title + sample desc.
    Proves the wreath fits with no clipping at the badge edge."""
    surf = pygame.Surface((width, _ROW_H), pygame.SRCALPHA)
    rad = 12
    body_top, body_bot = _PANEL_LIGHTER, _PANEL_DARK
    panel = pygame.Surface((width, _ROW_H), pygame.SRCALPHA)
    for yy in range(_ROW_H):
        t = yy / (_ROW_H - 1)
        pygame.draw.line(panel, lerp_color(body_top, body_bot, t), (0, yy), (width, yy))
    mask = pygame.Surface((width, _ROW_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, width, _ROW_H), border_radius=rad)
    panel.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    acc = (198, 132, 66) if shame else _GOLD_PALE
    pygame.draw.rect(panel, (*acc, 210), (0, 0, width, _ROW_H), width=1, border_radius=rad)
    surf.blit(panel, (0, 0))

    # 44px badge composed by our concept (NOT ai.get_badge — that's the old sprig)
    icon = ICONS["shame" if shame else "fame"]
    badge = compose(_BADGE, wreath_fn, shame, icon)
    bx = 8
    by = (_ROW_H - _BADGE) // 2
    surf.blit(badge, (bx, by))
    # red hairline framing the exact badge square — visual clip check
    pygame.draw.rect(surf, (255, 60, 60, 120), (bx, by, _BADGE, _BADGE), 1)

    tx = bx + _BADGE + 10
    tcol = _SHAME_DIM if shame else _GOLD_PALE
    dcol = _BRONZE_PALE if shame else _WHITE
    ts = _font(20).render(title, True, tcol)
    surf.blit(ts, (tx, 8))
    desc = "Same wreath, shedding." if shame else "Pristine gold laurel."
    ds = _font(15).render(desc, True, dcol)
    surf.blit(ds, (tx, 32))
    return surf


def render_candidate(idx, name, wreath_fn):
    pad = 26
    col_w = HERO + 40
    fig_w = col_w * 2 + pad
    fig_h = HERO + _ROW_H + 130
    fig = pygame.Surface((fig_w, fig_h), pygame.SRCALPHA)
    fig.fill(_NIGHT)

    title = _font(30).render(f"#{idx}  {name.replace('_', ' ').upper()}", True, _GOLD_PALE)
    fig.blit(title, (pad, 14))

    for ci, (label, shame, accent) in enumerate(
            (("FAME", False, _GOLD_PALE), ("SHAME", True, _BRONZE_PALE))):
        ox = pad + ci * col_w
        lab = _font(24).render(label, True, accent)
        fig.blit(lab, (ox, 56))
        hero = compose(HERO, wreath_fn, shame, ICONS["shame" if shame else "fame"])
        hy = 84
        fig.blit(hero, (ox, hy))

    # full-width row strips below the heroes (real on-screen size)
    strip_w = fig_w - pad * 2
    ry = 84 + HERO + 18
    fig.blit(_row_strip(strip_w, "Pristine gold laurel", False, wreath_fn), (pad, ry))
    fig.blit(_row_strip(strip_w, "The same wreath, shedding", True, wreath_fn),
             (pad, ry + _ROW_H + 10))

    cap = _font(17).render("red box = exact 44px badge square (clip check)",
                           True, (150, 150, 170))
    fig.blit(cap, (pad, ry + (_ROW_H + 10) * 2 + 4))

    out = f"/home/user/skybit/docs/wreath_polish/candidate_{idx}_{name}.png"
    pygame.image.save(fig, out)
    return out


def main():
    paths = []
    for i, (name, fn) in enumerate(VARIATIONS, 1):
        paths.append(render_candidate(i, name, fn))
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
