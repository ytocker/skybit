"""Focused E1-vs-E2 comparison for the final HUD pick.

Renders the two co-shippable Neon-Arcade leads from round 8 as a clean A/B:
DAY frames side-by-side on top, NIGHT frames side-by-side below, at 1.3x so the
HUD reads crisply. Reuses the round-8 candidate draw routines and the round-7
backdrop harness verbatim — no new design, just a clearer presentation.
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game.config import W, H
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE
from game.draw import UI_CREAM
from tools.gen_gameplay_hud_round7 import build_backdrop, NIGHT_TIME
from tools.gen_gameplay_hud_round8 import cand_e1, cand_e2

OUT = os.path.join(_ROOT, "docs", "gameplay_hud", "round_8_E1_vs_E2.png")

SCALE = 1.3
FW, FH = int(W * SCALE), int(H * SCALE)


def _frame(bg, fn):
    s = bg.copy()
    fn(s)
    return pygame.transform.smoothscale(s, (FW, FH))


def main():
    day = build_backdrop(0.0)
    night = build_backdrop(NIGHT_TIME)

    cols = [
        ("E1 — Neon Arcade", "cooler / sharper teal rim, tighter cut-corners", cand_e1),
        ("E2 — Warmer / Rounder", "sandstone-warm slate, amber-teal rim, rounded (art-director pick)", cand_e2),
    ]

    pad = 26
    gap = 30
    label_h = 24
    head_h = 50
    title_h = 46
    sheet_w = pad + FW + gap + FW + pad
    sheet_h = pad + title_h + head_h + label_h + FH + 22 + label_h + FH + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((14, 16, 24))

    tf = _font(24, True)
    sf = _font(14, True)
    hf = _font(20, True)
    cf = _font(12, True)
    lf = _font(15, True)

    sheet.blit(tf.render("Skybit — Gameplay HUD  ·  final pick: E1 vs E2",
                         True, _GOLD_PALE), (pad, 12))

    xs = [pad, pad + FW + gap]
    # Column headers.
    hy = pad + title_h
    for (name, sub, _fn), x in zip(cols, xs):
        sheet.blit(hf.render(name, True, _GOLD_BRIGHT), (x, hy))
        sheet.blit(cf.render(sub, True, UI_CREAM), (x, hy + 26))

    # Row 1 — DAY.
    ry = hy + head_h
    sheet.blit(lf.render("DAY", True, (245, 240, 210)), (pad, ry))
    fy = ry + label_h
    for (_n, _s, fn), x in zip(cols, xs):
        sheet.blit(_frame(day, fn), (x, fy))
        pygame.draw.rect(sheet, _GOLD_BRIGHT, (x, fy, FW, FH), 1)

    # Row 2 — NIGHT.
    ry2 = fy + FH + 22
    sheet.blit(lf.render("NIGHT", True, (200, 210, 255)), (pad, ry2))
    fy2 = ry2 + label_h
    for (_n, _s, fn), x in zip(cols, xs):
        sheet.blit(_frame(night, fn), (x, fy2))
        pygame.draw.rect(sheet, _GOLD_BRIGHT, (x, fy2, FW, FH), 1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print(f"saved {OUT}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
