"""Stitch the 5 matured award-interstitial LOOKS into one labeled comparison
figure: docs/achievements/unlock_notice/award_interstitial_v2/showcase.png.

Scratch tooling only; nothing here is imported by the game.

    python tools/build_award_v2_showcase.py
"""
import os
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _NIGHT_DEEP

BASE = os.path.join(_ROOT, "docs", "achievements", "unlock_notice",
                    "award_interstitial_v2")

# (slug, final-round file, one-line thesis) in figure order.
CONCEPTS = [
    ("pedestal-spotlight", "round_1.png",
     "Badge rises onto a gold plinth under a hard spotlight; confetti in the beam."),
    ("pip-parcel-handover", "round_2.png",
     "Pip the courier opens the parcel; the badge erupts on a diagonal."),
    ("constellation-coalesce", "round_2.png",
     "The night starfield streams inward and resolves into the badge."),
    ("delivered-postmark-stamp", "round_2.png",
     "A 'DELIVERED' postmark strikes around the badge; kinetic impact."),
    ("banner-unfurl", "round_1.png",
     "A heraldic banner drops with the medal pinned at its head."),
]

PANEL_W, PANEL_H = 360, 640
MARGIN = 30
GAP = 26
TITLE_H = 58
CAP_H = 84
DIM = (170, 172, 196)


def _wrap(text, font, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.size(trial)[0] <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    n = len(CONCEPTS)
    fig_w = MARGIN * 2 + n * PANEL_W + (n - 1) * GAP
    fig_h = MARGIN + TITLE_H + CAP_H + PANEL_H + MARGIN
    fig = pygame.Surface((fig_w, fig_h))

    for yy in range(fig_h):
        t = yy / (fig_h - 1)
        c = (int(_NIGHT_DEEP[0] + (10 - _NIGHT_DEEP[0]) * t),
             int(_NIGHT_DEEP[1] + (6 - _NIGHT_DEEP[1]) * t),
             int(_NIGHT_DEEP[2] + (28 - _NIGHT_DEEP[2]) * t))
        pygame.draw.line(fig, c, (0, yy), (fig_w, yy))

    title = _font(38, True).render(
        "ACHIEVEMENT-UNLOCK CEREMONY  ·  5 LOOKS", True, _GOLD_BRIGHT)
    fig.blit(title, title.get_rect(center=(fig_w // 2, MARGIN + TITLE_H // 2)))

    num_f = _font(22, True)
    slug_f = _font(24, True)
    thesis_f = _font(19, True)

    for i, (slug, fname, thesis) in enumerate(CONCEPTS):
        px = MARGIN + i * (PANEL_W + GAP)
        cap_y = MARGIN + TITLE_H

        chip = num_f.render(f"{i + 1}", True, _NIGHT_DEEP)
        cr = chip.get_rect()
        cr.topleft = (px, cap_y + 6)
        pygame.draw.rect(fig, _GOLD_BRIGHT, cr.inflate(16, 8), border_radius=11)
        fig.blit(chip, (cr.x, cr.y))
        slug_img = slug_f.render(slug, True, _GOLD_PALE)
        fig.blit(slug_img, (px + 30, cap_y + 6))

        for li, line in enumerate(_wrap(thesis, thesis_f, PANEL_W - 6)):
            img = thesis_f.render(line, True, DIM)
            fig.blit(img, (px, cap_y + 40 + li * 22))

        panel = pygame.image.load(os.path.join(BASE, slug, fname))
        if panel.get_size() != (PANEL_W, PANEL_H):
            panel = pygame.transform.smoothscale(panel, (PANEL_W, PANEL_H))
        py = cap_y + CAP_H
        fig.blit(panel, (px, py))
        pygame.draw.rect(fig, (*_GOLD_BRIGHT, 160),
                         (px, py, PANEL_W, PANEL_H), width=2, border_radius=4)

    out = os.path.join(BASE, "showcase.png")
    pygame.image.save(fig, out)
    print("saved", out, fig.get_size())


if __name__ == "__main__":
    main()
