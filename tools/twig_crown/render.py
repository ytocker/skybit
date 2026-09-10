"""Headless render harness for the five twig-crown PAIRED concepts.

Renders at the REAL badge geometry: a composer is handed R = int(px*0.46) on a
px = size*_SS supersampled square, exactly like ``ai._build``, then smoothscaled
down — so what we see is the true fit at 44px, NOT an old shrunk-preview scale
that hid clipping.

Per concept → docs/twig_crown/concept_<n>_<name>.png:
  Fame hero (with the red badge-bounds square drawn at the true 0.46 bound) +
  a real 44px Fame badge sitting in a 56px row strip + Shame hero (bounds
  square) + a 44px Shame row strip.
Plus docs/twig_crown/showcase.png tiling all five.

Run:  PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/twig_crown/render.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()
pygame.display.set_mode((1, 1))  # dummy surface so convert_alpha works headless

import game.achievement_icons as ai
from tools.twig_crown.concepts import CONCEPTS

SS = ai._SS
BG = (18, 16, 30)
PANEL = (26, 23, 40)
INK = (236, 232, 244)
SUB = (176, 172, 196)
BOUND = (232, 72, 72)

# the real geometry of a 44px row badge
BADGE = 44
ROW_H = 56

FAME_GLYPH = "pillar_100"
SHAME_GLYPH = "goose_egg"


def font(p, bold=True):
    return pygame.font.SysFont(None, p, bold=bold)


def render_medal(composer, glyph_key, size):
    """Draw a composer at the TRUE _build geometry (R = int(px*0.46)) and
    smoothscale to ``size`` — the exact path a live badge takes."""
    px = size * SS
    surf = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    R = int(px * 0.46)
    composer(surf, c, c, R, glyph_key)
    return pygame.transform.smoothscale(surf, (size, size))


def hero(composer, glyph_key, size=200):
    """A large hero with the red badge-bounds square at the true 0.46 bound so
    clipping is impossible to hide. The square marks the 44px-equivalent edge."""
    img = render_medal(composer, glyph_key, size).convert_alpha()
    # the badge square is the full ``size`` (R=0.46*size lives inside it) — any
    # twig crossing this red edge would clip at 44px.
    pygame.draw.rect(img, BOUND, (0, 0, size, size), 2)
    return img


def row_strip(composer, glyph_key):
    """A real 44px badge centered in a 56px-tall navy row — the actual
    achievements-screen scale, the only honest small-size test."""
    w = 168
    strip = pygame.Surface((w, ROW_H), pygame.SRCALPHA)
    strip.fill((30, 27, 46))
    badge = render_medal(composer, glyph_key, BADGE)
    strip.blit(badge, badge.get_rect(center=(28, ROW_H // 2)))
    # a couple of repeats so a stranger reads it at true density
    strip.blit(badge, badge.get_rect(center=(28 + 52, ROW_H // 2)))
    strip.blit(badge, badge.get_rect(center=(28 + 104, ROW_H // 2)))
    strip.blit(font(15).render("44px badge", True, SUB), (28 + 130, 4))
    strip.blit(font(13).render("row scale", True, (130, 126, 150)),
               (28 + 130, ROW_H - 18))
    return strip


def concept_sheet(idx, name, fame, shame):
    pad = 22
    hero_sz = 200
    col_w = hero_sz + pad
    W = col_w * 2 + pad * 2
    H = 56 + hero_sz + 16 + ROW_H + 28 + 22
    out = pygame.Surface((W, H))
    out.fill(BG)
    out.blit(font(30).render(f"{idx}. {name.upper()} — golden twig crown / degraded",
                             True, INK), (pad, 14))

    for col, (label, composer, glyph) in enumerate(
            (("FAME  (gilded, whole)", fame, FAME_GLYPH),
             ("SHAME  (snapped, shed, gaps)", shame, SHAME_GLYPH))):
        x = pad + col * col_w
        y = 56
        out.blit(font(20).render(label, True,
                                 (255, 224, 150) if col == 0 else (180, 184, 200)),
                 (x, y - 26 + 4))
        out.blit(hero(composer, glyph, hero_sz), (x, y))
        out.blit(row_strip(composer, glyph), (x, y + hero_sz + 16))

    note = ("red square = true badge bound (R=0.46*size) — every twig/leaf "
            "stays inside it; 44px strip = real row scale")
    out.blit(font(15).render(note, True, SUB), (pad, H - 22))
    path = f"docs/twig_crown/concept_{idx}_{name}.png"
    pygame.image.save(out, path)
    print("saved", path, out.get_size())
    return path


def showcase():
    """Tile all five pairs in a labeled grid — Fame hero + Shame hero per row."""
    pad = 18
    cell = 132
    label_w = 132
    rows = len(CONCEPTS)
    W = label_w + (cell + pad) * 2 + pad
    H = 70 + rows * (cell + pad)
    out = pygame.Surface((W, H))
    out.fill(BG)
    out.blit(font(32).render("TWIG CROWN — 5 paired concepts", True, INK), (pad, 16))
    out.blit(font(18).render("Fame", True, (255, 224, 150)),
             (label_w + cell // 2 - 18, 48))
    out.blit(font(18).render("Shame", True, (180, 184, 200)),
             (label_w + cell + pad + cell // 2 - 24, 48))
    for r, (name, fame, shame) in enumerate(CONCEPTS):
        y = 70 + r * (cell + pad)
        out.blit(font(22).render(f"{r + 1}. {name}", True, INK), (pad, y + cell // 2 - 10))
        fimg = render_medal(fame, FAME_GLYPH, cell - 8)
        simg = render_medal(shame, SHAME_GLYPH, cell - 8)
        out.blit(fimg, (label_w + 4, y + 4))
        out.blit(simg, (label_w + cell + pad + 4, y + 4))
    pygame.image.save(out, "docs/twig_crown/showcase.png")
    print("saved docs/twig_crown/showcase.png", out.get_size())


def main():
    os.makedirs("docs/twig_crown", exist_ok=True)
    for i, (name, fame, shame) in enumerate(CONCEPTS, start=1):
        concept_sheet(i, name, fame, shame)
    showcase()


if __name__ == "__main__":
    main()
