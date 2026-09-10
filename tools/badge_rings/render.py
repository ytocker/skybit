"""Headless render harness for the 5 PAIRED Fame/Shame ring concepts.

For EACH concept it composes the Fame ring (stamping the real ``pillar_100``
fame emblem) beside its degraded Shame twin (stamping the real ``goose_egg``
shame emblem) at hero (~170px) AND at the live 44px row size, labeled with the
concept name + "FAME"/"SHAME", into ``docs/badge_rings/concept_<n>_<name>.png``;
then a combined ``docs/badge_rings/showcase.png`` tiles all five pairs.

The composers draw at SS supersample (matching the live builder); this harness
smoothscales each medallion down for razor-sharp edges. The sample glyphs are
already in ``achievement_icons._GLYPHS`` (merged at import of game.emblems) so
``_stamp_glyph`` finds them — read-only preview, nothing under game/ is changed.

Run:  PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/badge_rings/render.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

import game.achievement_icons as ai  # noqa: E402 — triggers emblem-glyph merge
from tools.badge_rings.concepts import CONCEPTS  # noqa: E402

SS = ai._SS
FAME_GLYPH = "pillar_100"      # a real fame center emblem
SHAME_GLYPH = "goose_egg"      # a real shame center emblem

_BG_TOP = (40, 38, 56)
_BG_BOT = (22, 20, 34)
_FG = (236, 232, 244)
_SUB = (176, 172, 196)
_GOLD = (244, 200, 96)
_GREY = (170, 168, 176)


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
    """Compose one medallion at SS supersample, smoothscale to ``size``. R is
    held well under 0.46 so motif trim (rays / arches / sash) can spill past the
    rim without clipping the canvas."""
    px = size * SS
    surf = pygame.Surface((px, px), pygame.SRCALPHA)
    cx = cy = px // 2
    R = int(px * 0.32)
    fn(surf, cx, cy, R, glyph_key)
    return pygame.transform.smoothscale(surf, (size, size))


def make_concept_sheet(name, fame_fn, shame_fn, idx):
    hero = 170
    chip = 44
    pad = 28
    col_w = hero + 56
    w = pad * 2 + col_w * 2
    h = pad + 44 + hero + 30 + 46 + chip + 30 + pad
    sheet = pygame.Surface((w, h), pygame.SRCALPHA)
    _vgrad(sheet, _BG_TOP, _BG_BOT)

    title = _font(30).render(f"#{idx}  {name.upper()}", True, _FG)
    sheet.blit(title, (pad, pad))

    y_hero = pad + 52
    cols = ((fame_fn, FAME_GLYPH, "FAME", _GOLD),
            (shame_fn, SHAME_GLYPH, "SHAME", _GREY))
    for ci, (fn, gk, lab, lc) in enumerate(cols):
        x = pad + ci * col_w + (col_w - hero) // 2
        sheet.blit(render_medal(fn, gk, hero), (x, y_hero))
        t = _font(24).render(lab, True, lc)
        sheet.blit(t, t.get_rect(centerx=x + hero // 2, top=y_hero + hero + 6))

    # 44px legibility chips — the real row size — Fame then Shame.
    y_chip = y_hero + hero + 46
    cap = _font(17).render("at 44px (live row size):", True, _SUB)
    sheet.blit(cap, (pad, y_chip + chip // 2 - 8))
    cx0 = pad + 230
    for ci, (fn, gk, lab, lc) in enumerate(cols):
        sheet.blit(render_medal(fn, gk, chip), (cx0 + ci * (chip + 50), y_chip))
        t = _font(15).render(lab, True, lc)
        sheet.blit(t, t.get_rect(centerx=cx0 + ci * (chip + 50) + chip // 2,
                                 top=y_chip + chip + 2))
    return sheet


def main():
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "docs", "badge_rings")
    os.makedirs(out_dir, exist_ok=True)

    for i, (name, fame_fn, shame_fn) in enumerate(CONCEPTS, 1):
        sh = make_concept_sheet(name, fame_fn, shame_fn, i)
        p = os.path.join(out_dir, f"concept_{i}_{name}.png")
        pygame.image.save(sh, p)
        print("saved", p, sh.get_size())

    # ── combined showcase: 5 columns, each Fame hero over Shame hero + chips ──
    hero = 150
    chip = 44
    pad = 32
    col_w = hero + 26
    head_h = 64
    w = pad * 2 + col_w * len(CONCEPTS)
    h = pad + head_h + 24 + hero + 18 + hero + 40 + chip + 28 + pad
    show = pygame.Surface((w, h), pygame.SRCALPHA)
    _vgrad(show, _BG_TOP, _BG_BOT)

    head = _font(34).render(
        "ACHIEVEMENT RINGS  ·  paired FAME / SHAME motifs  ·  5 concepts",
        True, _FG)
    show.blit(head, (pad, pad))
    sub = _font(20).render(
        "Shame = the SAME motif degraded (ring/frame only) · center emblem unchanged · no diagonal crack",
        True, _SUB)
    show.blit(sub, (pad, pad + 34))

    for i, (name, fame_fn, shame_fn) in enumerate(CONCEPTS):
        x = pad + i * col_w + (col_w - hero) // 2
        nm = _font(25).render(f"{i + 1}. {name}", True, _FG)
        show.blit(nm, nm.get_rect(centerx=x + hero // 2, top=pad + head_h - 2))
        y0 = pad + head_h + 30
        show.blit(render_medal(fame_fn, FAME_GLYPH, hero), (x, y0))
        fl = _font(16).render("FAME", True, _GOLD)
        show.blit(fl, fl.get_rect(centerx=x + hero // 2, top=y0 + 2))
        y1 = y0 + hero + 18
        show.blit(render_medal(shame_fn, SHAME_GLYPH, hero), (x, y1))
        sl = _font(16).render("SHAME", True, _GREY)
        show.blit(sl, sl.get_rect(centerx=x + hero // 2, top=y1 + 2))
        # two 44px chips centered under the column
        y2 = y1 + hero + 34
        cw = chip * 2 + 18
        cx0 = x + (hero - cw) // 2
        show.blit(render_medal(fame_fn, FAME_GLYPH, chip), (cx0, y2))
        show.blit(render_medal(shame_fn, SHAME_GLYPH, chip), (cx0 + chip + 18, y2))
        cl = _font(15).render("44px", True, _SUB)
        show.blit(cl, cl.get_rect(centerx=x + hero // 2, top=y2 + chip + 4))

    p = os.path.join(out_dir, "showcase.png")
    pygame.image.save(show, p)
    print("saved", p, show.get_size())


if __name__ == "__main__":
    main()
