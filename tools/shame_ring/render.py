"""Headless render harness for the 5 cheerful Hall-of-Shame ring concepts.

For EACH concept it composes the two sample center emblems (goose_egg from the
Blooper Reel, kfc_incident from the same module) at hero (~200px) AND at the
live 44px row size, into ``docs/shame_ring/concept_<n>_<name>.png``; then a
combined ``docs/shame_ring/showcase.png`` tiles all five across with both
emblems + a 44px chip per concept, labeled by name.

The concept composers draw at SS supersample (matching the live builder) then
this harness smoothscales each medallion down for razor-sharp edges. The sample
glyphs are merged into the live ``achievement_icons._GLYPHS`` table so
``_stamp_glyph`` finds them — read-only preview, nothing under game/ is changed
on disk.

Run:  PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/shame_ring/render.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from game.emblems.blooper_reel import GLYPHS as BLOOP
from tools.shame_ring.concepts import CONCEPTS

# Make the two sample center emblems available to the live _stamp_glyph.
ai._GLYPHS.update(BLOOP)

SS = ai._SS
SAMPLES = [("goose_egg", "goose egg"), ("kfc_incident", "kfc incident")]

# Showcase / hero background — a soft warm-neutral so cheerful pastels read
# (the live shame screen is dark navy, but for an OPTIONS sheet a light card
# makes the palettes legible).
_BG_TOP = (40, 38, 56)
_BG_BOT = (22, 20, 34)
_FG = (236, 232, 244)
_SUB = (176, 172, 196)


def _font(px, bold=True):
    return pygame.font.SysFont(None, px, bold=bold)


def _vgrad(surf, top, bot):
    w, h = surf.get_size()
    for yy in range(h):
        t = yy / max(1, h - 1)
        pygame.draw.line(surf, (int(top[0] + (bot[0] - top[0]) * t),
                                int(top[1] + (bot[1] - top[1]) * t),
                                int(top[2] + (bot[2] - top[2]) * t)),
                         (0, yy), (w, yy))


def render_medal(fn, glyph_key, size):
    """Compose one medallion at SS supersample, smoothscale to ``size``."""
    px = size * SS
    surf = pygame.Surface((px, px), pygame.SRCALPHA)
    cx = cy = px // 2
    R = int(px * 0.36)   # well under 0.46 to leave room for trim that spills
    fn(surf, cx, cy, R, glyph_key)   # past the rim (ribbons / bursts / drips)
    return pygame.transform.smoothscale(surf, (size, size))


def make_concept_sheet(name, fn, idx):
    hero = 200
    chip = 44
    pad = 28
    gap = 26
    col_w = hero + 40
    # layout: title row, then a row of [hero goose] [hero kfc], then a 44px chip row
    w = pad * 2 + col_w * 2
    h = pad + 40 + hero + 34 + chip + 60 + pad
    sheet = pygame.Surface((w, h), pygame.SRCALPHA)
    _vgrad(sheet, _BG_TOP, _BG_BOT)

    title = _font(30).render(f"#{idx}  {name.upper()}", True, _FG)
    sheet.blit(title, (pad, pad))

    y_hero = pad + 48
    for ci, (gk, glab) in enumerate(SAMPLES):
        med = render_medal(fn, gk, hero)
        x = pad + ci * col_w + (col_w - hero) // 2
        sheet.blit(med, (x, y_hero))
        lab = _font(20).render(glab, True, _SUB)
        sheet.blit(lab, lab.get_rect(centerx=x + hero // 2, top=y_hero + hero + 4))

    # 44px legibility chips — the real row size — for both emblems, side by side.
    y_chip = y_hero + hero + 40
    cap = _font(18).render("at 44px (live row size):", True, _SUB)
    sheet.blit(cap, (pad, y_chip + chip // 2 - 8))
    cx0 = pad + 240
    for ci, (gk, glab) in enumerate(SAMPLES):
        med = render_medal(fn, gk, chip)
        sheet.blit(med, (cx0 + ci * (chip + 24), y_chip))
    return sheet


def main():
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "docs", "shame_ring")
    os.makedirs(out_dir, exist_ok=True)

    sheets = []
    for i, (name, fn) in enumerate(CONCEPTS, 1):
        sh = make_concept_sheet(name, fn, i)
        p = os.path.join(out_dir, f"concept_{i}_{name}.png")
        pygame.image.save(sh, p)
        print("saved", p, sh.get_size())
        sheets.append((name, fn))

    # ── combined showcase: 5 columns, each with goose hero, kfc hero, two 44px
    #    chips, labeled by concept name ──────────────────────────────────────
    hero = 168
    chip = 44
    pad = 32
    col_w = hero + 28
    head_h = 64
    w = pad * 2 + col_w * len(sheets)
    h = pad + head_h + hero + 14 + hero + 36 + chip + 30 + pad
    show = pygame.Surface((w, h), pygame.SRCALPHA)
    _vgrad(show, _BG_TOP, _BG_BOT)

    head = _font(34).render(
        "HALL OF SHAME  ·  cheerful booby-prize rings  ·  5 concepts",
        True, _FG)
    show.blit(head, (pad, pad))
    sub = _font(20).render(
        "ring/frame redesign only — center emblem unchanged · no diagonal crack",
        True, _SUB)
    show.blit(sub, (pad, pad + 34))

    for i, (name, fn) in enumerate(sheets):
        x = pad + i * col_w + (col_w - hero) // 2
        # concept name
        nm = _font(26).render(f"{i + 1}. {name}", True, _FG)
        show.blit(nm, nm.get_rect(centerx=x + hero // 2, top=pad + head_h - 4))
        y0 = pad + head_h + 26
        # goose hero
        show.blit(render_medal(fn, "goose_egg", hero), (x, y0))
        # kfc hero
        y1 = y0 + hero + 14
        show.blit(render_medal(fn, "kfc_incident", hero), (x, y1))
        # two 44px chips centered under the column
        y2 = y1 + hero + 24
        cw = chip * 2 + 18
        cx0 = x + (hero - cw) // 2
        show.blit(render_medal(fn, "goose_egg", chip), (cx0, y2))
        show.blit(render_medal(fn, "kfc_incident", chip), (cx0 + chip + 18, y2))
        cl = _font(16).render("44px", True, _SUB)
        show.blit(cl, cl.get_rect(centerx=x + hero // 2, top=y2 + chip + 4))

    p = os.path.join(out_dir, "showcase.png")
    pygame.image.save(show, p)
    print("saved", p, show.get_size())


if __name__ == "__main__":
    main()
