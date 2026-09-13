"""Headless render harness for the SLIM/ELEGANT ring concepts.

Renders at the REAL badge geometry (``R = 0.46 * px``, matching
``achievement_icons._build``). Per concept it emits a figure with:
  * a Fame hero + red badge-bounds square (to spot any spill past the square),
  * a Fame 44px row strip (the real achievements-row size, on the row bg),
  * a Shame hero + a Shame 44px row strip.
Plus a showcase tiling all five pairs.

Run: PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/ring_elegant/render.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from tools.ring_elegant.concepts import CONCEPTS

SS = ai._SS
BG = (16, 14, 28)              # page background
ROW_BG = (26, 22, 44)         # achievements-row background (navy)
INK = (236, 232, 244)
SUB = (176, 172, 196)
FAME_GK = "pillar_100"
SHAME_GK = "goose_egg"

os.makedirs("docs/ring_elegant", exist_ok=True)


def font(p, bold=True):
    return pygame.font.SysFont(None, p, bold=bold)


def render(fn, glyph, size):
    """Render a composer at the REAL geometry onto a size x size surface."""
    px = size * SS
    s = pygame.Surface((px, px), pygame.SRCALPHA)
    c = px // 2
    fn(s, c, c, int(px * 0.46), glyph)
    return pygame.transform.smoothscale(s, (size, size))


def hero(fn, glyph, badge=200, margin=0.16):
    """A large hero with the red badge-bounds square marked, so any ornament
    spilling past the badge square is visible."""
    canvas = int(badge * (1 + 2 * margin))
    img = pygame.Surface((canvas, canvas), pygame.SRCALPHA)
    b = render(fn, glyph, badge)
    off = int(badge * margin)
    img.blit(b, (off, off))
    pygame.draw.rect(img, (232, 72, 72), (off, off, badge, badge), 2)
    return img, canvas


def row_strip(fn, glyph):
    """The badge at the real 44px row size on the achievements-row background,
    shown a few times + at 32px, to verify it READS at scan size."""
    row_h = 56
    W = 300
    strip = pygame.Surface((W, row_h * 2 + 8), pygame.SRCALPHA)
    for r in range(2):
        y = r * (row_h + 8)
        pygame.draw.rect(strip, ROW_BG, (0, y, W, row_h), border_radius=6)
    # top row: three 44px badges (the real row size)
    b44 = render(fn, glyph, 44)
    for i in range(3):
        strip.blit(b44, (10 + i * 60, 6))
    strip.blit(font(14).render("44px (real row)", True, SUB), (200, 20))
    # bottom row: 32 / 44 / 56 scale check
    y2 = row_h + 8
    for i, sz in enumerate((32, 44, 56)):
        b = render(fn, glyph, sz)
        strip.blit(b, (14 + i * 64, y2 + (row_h - sz) // 2))
    strip.blit(font(14).render("32 / 44 / 56", True, SUB), (210, y2 + 20))
    return strip


def concept_figure(idx, name, fame_fn, shame_fn):
    h_fame, cv = hero(fame_fn, FAME_GK)
    h_shame, _ = hero(shame_fn, SHAME_GK)
    strip_f = row_strip(fame_fn, FAME_GK)
    strip_s = row_strip(shame_fn, SHAME_GK)

    pad = 24
    col_w = cv + 40 + strip_f.get_width()
    W = pad * 2 + col_w
    H = 70 + (cv + 40) * 2
    out = pygame.Surface((W, H))
    out.fill(BG)
    out.blit(font(30).render(f"RING · {name.upper()}  (slim / elegant)", True, INK),
             (pad, 18))

    def block(y, label, herosurf, strip):
        col = (255, 214, 120) if label == "FAME" else (176, 150, 120)
        out.blit(font(22).render(label, True, col), (pad, y))
        out.blit(herosurf, (pad, y + 26))
        out.blit(font(13).render("red = badge square", True, SUB),
                 (pad, y + 26 + cv + 2))
        out.blit(strip, (pad + cv + 30, y + 26 + (cv - strip.get_height()) // 2))

    block(58, "FAME", h_fame, strip_f)
    block(58 + cv + 40, "SHAME", h_shame, strip_s)

    path = f"docs/ring_elegant/concept_{idx}_{name}.png"
    pygame.image.save(out, path)
    return path, out


def showcase(pairs):
    """Tile all five Fame/Shame pairs at a mid preview size in a labelled grid."""
    sz = 128
    cell_w = sz * 2 + 40
    cols = 2
    rows = (len(pairs) + cols - 1) // cols
    pad = 26
    head = 64
    lab = 26
    cell_h = sz + lab + 24
    W = pad * 2 + cols * cell_w + (cols - 1) * pad
    H = head + rows * (cell_h + pad)
    out = pygame.Surface((W, H))
    out.fill(BG)
    out.blit(font(32).render("SLIM ELEGANT RINGS — Fame vs Shame (5 concepts)",
                             True, INK), (pad, 18))
    for idx, (name, fame_fn, shame_fn) in enumerate(pairs):
        r, c = divmod(idx, cols)
        x = pad + c * (cell_w + pad)
        y = head + r * (cell_h + pad)
        out.blit(font(22).render(f"{idx+1}. {name.upper()}", True, (255, 214, 120)),
                 (x, y))
        out.blit(render(fame_fn, FAME_GK, sz), (x, y + lab))
        out.blit(render(shame_fn, SHAME_GK, sz), (x + sz + 40, y + lab))
        out.blit(font(15).render("FAME", True, SUB), (x + sz // 2 - 20, y + lab + sz + 2))
        out.blit(font(15).render("SHAME", True, SUB),
                 (x + sz + 40 + sz // 2 - 24, y + lab + sz + 2))
    path = "docs/ring_elegant/showcase.png"
    pygame.image.save(out, path)
    return path


def main():
    paths = []
    for i, (name, fame_fn, shame_fn) in enumerate(CONCEPTS, start=1):
        p, _ = concept_figure(i, name, fame_fn, shame_fn)
        paths.append(p)
        print("saved", p)
    sc = showcase(CONCEPTS)
    print("saved", sc)


if __name__ == "__main__":
    main()
