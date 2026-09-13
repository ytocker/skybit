"""Headless review-sheet renderer for the five paired trade-off ring concepts.

For EACH concept it renders, at the REAL badge geometry (a size x size badge,
core R = core*size like ``_build``'s R = 0.46*size):

  * a Fame hero on a margined canvas with the badge-bounds square drawn in red
    (anything spilling past it would clip at 44px),
  * a Fame 44px ROW STRIP — the true 44px badge in a 56px row, plus a 3x zoom,
  * the Shame hero + bounds square,
  * the Shame 44px ROW STRIP.

Plus a ``showcase.png`` tiling all five pairs. Run:
    PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/ring_tradeoff/render.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from tools.ring_tradeoff.concepts import CONCEPTS

SS = ai._SS
BG = (16, 14, 28)
ROW_BG = (22, 19, 40)          # the achievements-screen navy row feel
BOUND = (232, 72, 72)
INK = (236, 232, 244)
DIM = (176, 172, 196)
FAME_GLYPH = "pillar_100"
SHAME_GLYPH = "goose_egg"

os.makedirs("docs/ring_tradeoff", exist_ok=True)


def font(p, bold=True):
    return pygame.font.SysFont(None, p, bold=bold)


def hero(fn, glyph, core, badge=176, margin=0.40):
    cv = int(badge * (1 + 2 * margin))
    px = cv * SS
    c = px // 2
    s = pygame.Surface((px, px), pygame.SRCALPHA)
    fn(s, c, c, int(badge * SS * core), glyph)
    img = pygame.transform.smoothscale(s, (cv, cv))
    b0 = int(badge * margin)
    pygame.draw.rect(img, BOUND, (b0, b0, badge, badge), 2)
    return img


def chip(fn, glyph, core, size=44):
    """The true 44px badge — surface is exactly size x size so any ornament past
    the badge square really clips, proving the fit."""
    px = size * SS
    c = px // 2
    s = pygame.Surface((px, px), pygame.SRCALPHA)
    fn(s, c, c, int(px * core), glyph)
    return pygame.transform.smoothscale(s, (size, size))


def row_strip(fn, glyph, core, label, width=360):
    """A 56px achievements-style row: real 44px badge left, a 3x zoom right."""
    h = 56
    strip = pygame.Surface((width, h))
    strip.fill(ROW_BG)
    pygame.draw.line(strip, (40, 36, 62), (0, h - 1), (width, h - 1), 1)
    badge = chip(fn, glyph, core, 44)
    strip.blit(badge, (10, (h - 44) // 2))
    big = pygame.transform.scale(badge, (132, 132))     # nearest-neighbour zoom
    zx = width - 132 - 8
    strip.blit(big, (zx, (h - 132) // 2)) if False else None
    strip.blit(font(13).render(label, True, DIM), (66, 6))
    strip.blit(font(11, False).render("actual 44px  |  3x ->", True, DIM), (66, 34))
    # place the 3x zoom in its own tall lane so it doesn't overflow the 56px row
    return strip, big


def concept_sheet(name, fame, shame, core):
    hf = hero(fame, FAME_GLYPH, core)
    hs = hero(shame, SHAME_GLYPH, core)
    cvv = hf.get_width()
    zoomF = pygame.transform.scale(chip(fame, FAME_GLYPH, core, 44), (140, 140))
    zoomS = pygame.transform.scale(chip(shame, SHAME_GLYPH, core, 44), (140, 140))
    stripF, _ = row_strip(fame, FAME_GLYPH, core, "FAME  ·  earned honour")
    stripS, _ = row_strip(shame, SHAME_GLYPH, core, "SHAME  ·  the same, gone bad")

    pad = 24
    col_w = cvv + 24 + 140 + pad
    W = pad + col_w * 2
    H = 60 + cvv + 20 + 56 + 30
    out = pygame.Surface((W, H))
    out.fill(BG)
    out.blit(font(30).render("%d)  %s" % (
        [c[0] for c in CONCEPTS].index(name) + 1, name.upper()), True, INK), (pad, 16))

    def col(x, hero_img, zoom, strip, tag, tagcol):
        out.blit(font(20).render(tag, True, tagcol), (x, 52))
        out.blit(hero_img, (x, 76))
        out.blit(zoom, (x + cvv + 20, 76 + (cvv - 140) // 2))
        out.blit(font(12).render("44px zoom", True, DIM),
                 (x + cvv + 20 + 32, 76 + (cvv - 140) // 2 + 142))
        out.blit(strip, (x, 76 + cvv + 14))

    col(pad, hf, zoomF, stripF, "FAME", (250, 214, 120))
    col(pad + col_w, hs, zoomS, stripS, "SHAME", (170, 170, 182))
    path = "docs/ring_tradeoff/concept_%d_%s.png" % (
        [c[0] for c in CONCEPTS].index(name) + 1, name)
    pygame.image.save(out, path)
    return path, hf, hs


def main():
    heroes = []
    for name, fame, shame, core in CONCEPTS:
        p, hf, hs = concept_sheet(name, fame, shame, core)
        heroes.append((name, hf, hs))
        print("saved", p)

    # showcase: all five pairs tiled, Fame | Shame per row
    cvv = heroes[0][1].get_width()
    pad = 22
    label_w = 150
    row_h = cvv + 20
    W = pad * 2 + label_w + cvv * 2 + 30
    H = 70 + row_h * len(heroes)
    out = pygame.Surface((W, H))
    out.fill(BG)
    out.blit(font(32).render("RING TRADE-OFF  ·  Fame  vs  the same GONE BAD",
                             True, INK), (pad, 20))
    out.blit(font(18).render("FAME", True, (250, 214, 120)),
             (pad + label_w + cvv // 2 - 26, 52))
    out.blit(font(18).render("SHAME", True, (170, 170, 182)),
             (pad + label_w + cvv + 30 + cvv // 2 - 32, 52))
    for i, (name, hf, hs) in enumerate(heroes):
        y = 70 + i * row_h
        out.blit(font(24).render(name.upper(), True, INK), (pad, y + cvv // 2 - 12))
        out.blit(hf, (pad + label_w, y))
        out.blit(hs, (pad + label_w + cvv + 30, y))
    pygame.image.save(out, "docs/ring_tradeoff/showcase.png")
    print("saved docs/ring_tradeoff/showcase.png", out.get_size())


if __name__ == "__main__":
    main()
