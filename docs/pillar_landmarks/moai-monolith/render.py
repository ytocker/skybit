"""moai-monolith — a stacked megalithic idol tower (standalone candidate).

An ancestor stack: knobbly volcanic-tuff heads piled flush head-on-head into a
lumpy organic column, crowned by a red scoria pukao topknot at the gap end. This
is the ONLY organic/bulbous silhouette in the landmark set — the scalloped
side-outline (one clean cheek lobe bulging out, necks pinching in) plus a
jutting brow shelf are the read at small size, so it survives without relying on
interior face relief.

Distinctness pins: a full STACK of many faces forming the whole tower (not one
`stone_face` dressing on a plain pillar), a lumpy carved profile (not the smooth
pebbles of the shipped cairn), and a fixed-red pukao crown.

Column-fill: a hidden full-height core column (just under the neck width)
guarantees the central PIPE_W band is solid top-to-bottom at every section
height; the heads bulge past it for the wavy outline and the neck notches are
kept short so no empty vertical band exceeds the ceiling.

Mirror read (pinned): a symmetric two-ended ancestor totem. Both sections cap
their gap end with the red pukao and root their plinth at the world edge; the
top section is a true vertical flip. The head lobe is near-vertically-symmetric
so the flip stays ambiguous rather than reading as an upside-down face.

Standalone: imports biome/config only for the palette + canvas constants; it
does NOT import or modify any game drawing module.

Run:  python docs/pillar_landmarks/moai-monolith/render.py
Out:  docs/pillar_landmarks/moai-monolith/round_2.png
"""
from __future__ import annotations

import math
import os
import pathlib
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, PIPE_W
from game import biome

MARGIN = 64                       # matches entities.Pipe eave/ornament gutter
CACHE_W = PIPE_W + MARGIN * 2
CACHE_H = GROUND_Y
PHASE_DAY = 0.30                  # basalt body reads warm against the tan sky
PHASE_NIGHT = 0.64               # NIGHT keyframe — checks pukao-red + lit rim

# The ONE deliberately non-palette color: a fixed saturated volcanic-scoria red.
# Anchoring the pukao here (instead of the horizon role) keeps the crown a red
# focal in EVERY biome; by day the horizon is yellow and melts a horizon-mixed
# crown into the sandstone body, which is the round-1 bug this fixes.
_SCORIA = (150, 25, 20)

# Head silhouette dial. Cheek lobe bulges past the PIPE_W (58) collision band;
# the neck pinches back toward the hidden core. The pinch is kept SHORT (fuller
# ovoid, brief neck notch) so the outermost band columns never starve.
_CHEEK_HALF = 34                  # widest half-width (cheek lobe, ~68 wide)
_NECK_HALF = 27                   # narrowest half-width — pinches inside the band
_PEAK = 0.55                      # lobe crest near cell-center → flip-ambiguous
_LOBE_FULL = 0.6                  # <1 fattens the ovoid + shortens the notch
_CORE_HALF = 27                   # hidden core column (54 wide) fill guarantee


# ── local shading helpers (kept standalone; mirror pillar_pagodas idiom) ──
def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _gradient_rect(surf, rect, lit, mid, shadow):
    """Horizontal 3-stop body gradient so a flat mass reads as a lit volume."""
    if rect.width < 2 or rect.height < 2:
        return
    n = rect.width
    for i in range(n):
        t = i / max(1, n - 1)
        col = _mix(lit, mid, t * 2) if t < 0.5 else _mix(mid, shadow, (t - 0.5) * 2)
        pygame.draw.line(surf, col, (rect.x + i, rect.y),
                         (rect.x + i, rect.bottom - 1), 1)


def _gradient_span(surf, y, x_left, x_right, lit, mid, shadow):
    """One scanline of the same 3-stop body gradient across [x_left, x_right].
    Building the whole stack this way gives one clean, controllable outline per
    row instead of the serrated overlap of stacked ellipses."""
    n = x_right - x_left
    if n < 1:
        surf.set_at((x_left, y), mid)
        return
    for i in range(n + 1):
        t = i / n
        col = _mix(lit, mid, t * 2) if t < 0.5 else _mix(mid, shadow, (t - 0.5) * 2)
        surf.set_at((x_left + i, y), col)


def _pukao_color(palette):
    # Fixed scoria red, only lightly biome-retinted so it survives day AND night
    # as a saturated red focal (hue break R-G>=110 and a >=25% value break vs the
    # body mid it sits on) instead of mixing into the sandstone.
    return _mix(_SCORIA, palette['horizon'], 0.08)


def _grass_seam(surf, cx, cy, palette, rng, blades=3):
    """A small clump of blades sprouting from a stacked-shoulder seam."""
    mid, top = palette['foliage_mid'], palette['foliage_top']
    for _ in range(blades):
        dx = rng.randint(-4, 4)
        h = rng.randint(3, 6)
        lean = rng.randint(-2, 2)
        pygame.draw.line(surf, mid, (cx + dx, cy), (cx + dx + lean, cy - h), 1)
        pygame.draw.line(surf, top, (cx + dx, cy), (cx + dx + lean, cy - h + 1), 1)


# ── silhouette profile ──────────────────────────────────────────────────────
def _half_width(u):
    """Half-width of one head cell at fractional height u in [0,1] (0 = lower
    neck seam, 1 = upper neck seam). A single confident lobe: rises to the cheek
    crest at _PEAK, pinches to the neck at both ends. The <1 exponent fattens the
    ovoid so the neck notch stays short — one peak-and-valley, feeds the band."""
    if u <= _PEAK:
        s = math.sin(0.5 * math.pi * (u / _PEAK)) if _PEAK > 0 else 1.0
    else:
        s = math.sin(0.5 * math.pi * ((1.0 - u) / (1.0 - _PEAK))) if _PEAK < 1 else 1.0
    s = max(0.0, s) ** _LOBE_FULL
    return _NECK_HALF + (_CHEEK_HALF - _NECK_HALF) * s


# ── one carved head's interior relief (close-up reward, stays INSIDE outline) ─
def _draw_head_relief(surf, cx, cy, hh, palette):
    """Sockets / nose / lip carved WITHIN the lobe so they never chew the
    outline. Lit from the upper-left, matching the roster."""
    tuff_d = palette['stone_dark']
    tuff_m = palette['stone_mid']
    tuff_l = palette['stone_light']
    accent = palette['stone_accent']

    # Brow shelf — a lit ridge with a deep under-shadow, kept inside the cheek so
    # it reads as an overhang at the SAME height as the lobe crest (one peak).
    bw = int(_CHEEK_HALF * 1.4)
    by = cy - int(hh * 0.08)
    pygame.draw.line(surf, _mix(tuff_m, accent, 0.5),
                     (cx - bw // 2, by - 1), (cx + bw // 2, by - 1), 1)
    pygame.draw.line(surf, tuff_d, (cx - bw // 2, by + 1), (cx + bw // 2, by + 1), 2)

    # Eye sockets tucked under the brow.
    ew = max(3, int(_CHEEK_HALF * 0.34))
    eh = max(2, int(hh * 0.10))
    ey = by + 3
    for sgn in (-1, 1):
        ex = cx + sgn * int(_CHEEK_HALF * 0.42) - ew // 2
        pygame.draw.ellipse(surf, tuff_d, (ex, ey, ew, eh))
        if ew >= 5:
            pygame.draw.circle(surf, _shade(accent, 15),
                               (ex + ew // 2, ey + eh // 2), 1)

    # Long nose wedge — lit ridge with a shadowed right flank.
    nose_top = ey + eh
    nose_bot = cy + int(hh * 0.24)
    nw = max(4, int(_CHEEK_HALF * 0.36))
    if nose_bot > nose_top + 3:
        pygame.draw.polygon(surf, _mix(tuff_m, tuff_l, 0.55),
                            [(cx - 2, nose_top), (cx + 2, nose_top),
                             (cx + nw // 2, nose_bot), (cx - nw // 2, nose_bot)])
        pygame.draw.polygon(surf, _shade(tuff_d, 12),
                            [(cx + 1, nose_top), (cx + 2, nose_top),
                             (cx + nw // 2, nose_bot), (cx + nw // 2 - 2, nose_bot)])

    # Pouty lip + lit chin ledge.
    lw = int(_CHEEK_HALF * 0.8)
    ly = cy + int(hh * 0.34)
    pygame.draw.line(surf, tuff_d, (cx - lw // 2, ly), (cx + lw // 2, ly), 2)
    pygame.draw.line(surf, _mix(tuff_m, accent, 0.5),
                     (cx - lw // 3, ly + 2), (cx + lw // 3, ly + 2), 1)


def _draw_pukao(surf, cx, y_top, pw, ph, palette):
    """Red scoria topknot cylinder capping the gap end — presents a solid wide
    edge at the rim so the collision column stays filled to the tip."""
    puk = _pukao_color(palette)
    lit, mid, shadow = _shade(puk, 34), puk, _shade(puk, -46)
    x = cx - pw // 2
    # Rounded crown.
    pygame.draw.ellipse(surf, shadow, (x - 1, y_top - 1, pw + 2, int(ph * 0.9) + 2))
    pygame.draw.ellipse(surf, mid, (x, y_top, pw, int(ph * 0.9)))
    pygame.draw.ellipse(surf, lit,
                        (x + 3, y_top + 2, int(pw * 0.5), int(ph * 0.5)))
    # Cylinder wall below the crown, shaded for volume.
    body = pygame.Rect(x, y_top + int(ph * 0.42), pw, int(ph * 0.58) + 2)
    _gradient_rect(surf, body, lit, mid, shadow)
    # Dark seat line where the topknot rests on the head.
    pygame.draw.line(surf, shadow, (x + 2, body.bottom - 1),
                     (x + pw - 2, body.bottom - 1), 1)


def _draw_tower_upright(surf, cx, y_top, y_bottom, palette, seed):
    """Draw the idol stack upright with the plinth at y_bottom and the pukao at
    y_top. Callers flip the whole surface for the ceiling-hung top section."""
    rng = random.Random(seed)
    sect_h = y_bottom - y_top
    if sect_h < 8:
        return

    tuff_d = palette['stone_dark']
    tuff_m = palette['stone_mid']
    tuff_l = palette['stone_light']
    accent = palette['stone_accent']

    plinth_h = max(4, min(10, int(sect_h * 0.06)))
    pukao_h = max(12, min(26, int(sect_h * 0.17)))
    # Very short sections can't afford both caps and a head — shed the pukao
    # budget first so a lone head still fills the stub.
    if sect_h < 64:
        pukao_h = max(10, min(pukao_h, sect_h // 4))

    heads_bottom = y_bottom - plinth_h
    heads_top = y_top + pukao_h
    heads_h = heads_bottom - heads_top
    if heads_h < 8:
        heads_top = y_top
        heads_h = heads_bottom - heads_top

    # Height-adaptive head COUNT keyed off a natural head height (~46 px): one
    # big head at ~70 px, a tall stack toward ~355 px.
    head_target = 46
    n = max(1, int(round(heads_h / head_target)))
    pitch = heads_h / n

    # Hidden core column — just under the neck width so it is invisible behind
    # the cheeks yet guarantees the central band is fed even at the neck notches.
    core = pygame.Rect(cx - _CORE_HALF, heads_top - 2, _CORE_HALF * 2, heads_h + 4)
    _gradient_rect(surf, core, tuff_l, tuff_m, tuff_d)

    # Scanline the whole stack as one clean lobed silhouette. Lit rim on the
    # upper-left edge, dark rim on the lower-right — the rim keeps the outline
    # off a dark night sky where the body-to-sky value gap is thin.
    rim_lit = _shade(tuff_l, 18)
    for y in range(heads_top, heads_bottom):
        rel = heads_bottom - y
        cell = min(n - 1, int(rel / pitch))
        cell_bottom = heads_bottom - pitch * cell
        u = (cell_bottom - y) / pitch
        u = min(1.0, max(0.0, u))
        hw = _half_width(u)
        left = cx - int(round(hw))
        right = cx + int(round(hw))
        _gradient_span(surf, y, left, right, tuff_l, tuff_m, tuff_d)
        surf.set_at((left, y), rim_lit)
        surf.set_at((right, y), tuff_d)

    # Per-head interior relief, brow at each lobe crest.
    for i in range(n):
        cy = int(heads_bottom - pitch * (i + _PEAK))
        _draw_head_relief(surf, cx, cy, int(pitch), palette)

    # Grass tufts: sparse + height-adaptive, only at the LOWEST seams so it reads
    # as growth creeping up from the ground rather than fuzz on the whole tower.
    if n >= 2:
        low_seams = min(2, n - 1)
        for i in range(low_seams):
            jy = int(heads_bottom - pitch * (i + 1))
            _grass_seam(surf, cx - 24, jy + 2, palette, rng, blades=3)
            if i == 0:
                _grass_seam(surf, cx + 24, jy + 2, palette, rng, blades=3)

    # Pukao topknot caps the top head at the gap end — wide enough to present a
    # solid edge across the full band at the rim.
    pw = 60
    _draw_pukao(surf, cx, y_top, pw, pukao_h, palette)

    # Base plinth slab — a wide, short footing rooted at the world edge.
    pl_w = 74
    ply = y_bottom - plinth_h
    pygame.draw.rect(surf, tuff_d, (cx - pl_w // 2, ply, pl_w, plinth_h))
    pygame.draw.rect(surf, tuff_m, (cx - pl_w // 2 + 1, ply + 1, pl_w - 2, plinth_h - 2))
    pygame.draw.line(surf, _mix(tuff_m, accent, 0.4),
                     (cx - pl_w // 2 + 3, ply), (cx + pl_w // 2 - 3, ply), 1)


def candidate_moai_monolith(surf, top_rect, bot_rect, palette, seed):
    """Bottom is an ancestor stack rising from the ground, pukao at the gap.
    Top is the same builder flipped — a symmetric two-ended totem hung from the
    ceiling, its pukao pointing into the gap."""
    if bot_rect.height > 0:
        _draw_tower_upright(surf, bot_rect.centerx, bot_rect.y, bot_rect.bottom,
                            palette, seed)

    if top_rect.height > 0:
        tmp = pygame.Surface((surf.get_width(), top_rect.height), pygame.SRCALPHA)
        _draw_tower_upright(tmp, top_rect.centerx, 0, top_rect.height,
                            palette, seed + 1)
        surf.blit(pygame.transform.flip(tmp, False, True), (0, top_rect.y))


# ── review harness ─────────────────────────────────────────────────────────
def _bg(w, h, pal, ground_line):
    """Sky gradient + ground band, matching the comparison sheet."""
    cell = pygame.Surface((w, h))
    for y in range(min(ground_line, h)):
        t = y / max(1, ground_line - 1)
        pygame.draw.line(cell, _mix(pal["sky_top"], pal["horizon"], t), (0, y), (w, y))
    for y in range(ground_line, h):
        t = (y - ground_line) / max(1, h - ground_line)
        pygame.draw.line(cell, _mix(pal["ground_top"], pal["ground_mid"], t),
                         (0, y), (w, y))
    return cell


def _max_empty_run(surf, x0, x1, y0, y1):
    """Longest contiguous vertical run of transparent pixels within the band —
    a numeric feasibility check (never viewed as an image)."""
    worst = 0
    for x in range(x0, x1):
        run = 0
        for y in range(y0, y1):
            if surf.get_at((x, y))[3] == 0:
                run += 1
                worst = max(worst, run)
            else:
                run = 0
    return worst


def _hero(pal, seed, label_bottom):
    """One upright + ceiling-mirror tower over a sky, cropped to a hero strip."""
    gap_y, gap_h = 150, 150
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    full = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_moai_monolith(full, top_rect, bot_rect, pal, seed=seed)

    tip_y = bot_top - 12
    base_y = GROUND_Y + 8
    hero_h = base_y - tip_y
    hero = _bg(CACHE_W, hero_h, pal, hero_h - (base_y - GROUND_Y))
    hero.blit(full, (0, -tip_y))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(hero, (230, 60, 60), (ex, 0), (ex, hero_h), 1)
    return hero, hero_h


def _closeup(pal, seed, scale=3):
    """Zoom on the ceiling-mirrored TOP section so the flip is checkable."""
    top_h = 150
    surf = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, 0, PIPE_W, 0)
    candidate_moai_monolith(surf, top_rect, bot_rect, pal, seed=seed)
    crop = pygame.Surface((CACHE_W, top_h + 6))
    crop.blit(_bg(CACHE_W, top_h + 6, pal, top_h + 6), (0, 0))
    crop.blit(surf, (0, 0))
    for ex in (MARGIN, MARGIN + PIPE_W):
        pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, top_h + 6), 1)
    return pygame.transform.scale(
        crop, (crop.get_width() * scale, crop.get_height() * scale))


def main():
    pal = biome.palette_for_phase(PHASE_DAY)
    pal_n = biome.palette_for_phase(PHASE_NIGHT)

    # ── FIX 1 proof: pukao vs stone_mid in DAY (must be a hue + value break) ──
    puk_day = _pukao_color(pal)
    sm_day = pal['stone_mid']
    puk_night = _pukao_color(pal_n)
    sm_night = pal_n['stone_mid']
    print("PUKAO vs STONE_MID")
    print(f"  DAY   pukao={puk_day} lum={_lum(puk_day):.1f}  "
          f"stone_mid={sm_day} lum={_lum(sm_day):.1f}  "
          f"R-G={puk_day[0]-puk_day[1]}  "
          f"valDelta={abs(_lum(sm_day)-_lum(puk_day))/_lum(sm_day)*100:.1f}%")
    print(f"  NIGHT pukao={puk_night} lum={_lum(puk_night):.1f}  "
          f"stone_mid={sm_night} lum={_lum(sm_night):.1f}  "
          f"R-G={puk_night[0]-puk_night[1]}  "
          f"valDelta={abs(_lum(sm_night)-_lum(puk_night))/_lum(sm_night)*100:.1f}%")

    hero_day, hd_h = _hero(pal, 7, "day")
    hero_night, hn_h = _hero(pal_n, 7, "night")
    close = _closeup(pal, 7)

    # ── FEASIBILITY STRIP: bottom section at three heights, column edges ──
    strip_heights = [70, 210, 355]
    strips = []
    print("FILL GATE (max empty vertical run inside the 58px PIPE_W band)")
    for h in strip_heights:
        s = pygame.Surface((CACHE_W, CACHE_H), pygame.SRCALPHA)
        br = pygame.Rect(MARGIN, GROUND_Y - h, PIPE_W, h)
        tr = pygame.Rect(MARGIN, 0, PIPE_W, 0)
        candidate_moai_monolith(s, tr, br, pal, seed=7)
        run = _max_empty_run(s, MARGIN, MARGIN + PIPE_W, GROUND_Y - h, GROUND_Y)
        crop = pygame.Surface((CACHE_W, h + 8))
        crop.blit(_bg(CACHE_W, h + 8, pal, h), (0, 0))
        crop.blit(s, (0, -(GROUND_Y - h)))
        for ex in (MARGIN, MARGIN + PIPE_W):
            pygame.draw.line(crop, (230, 60, 60), (ex, 0), (ex, h + 8), 1)
        strips.append((h, crop, run))
        print(f"  h={h:3d}  max empty run = {run}px  [{'OK' if run <= 12 else 'FAIL'}]")

    # ── compose the sheet ──
    pad = 12
    label_h = 24
    head_h = 62
    title = pygame.font.SysFont(None, 32)
    sub = pygame.font.SysFont(None, 19)
    lab = pygame.font.SysFont(None, 20)

    col1_w = CACHE_W
    col2_w = CACHE_W
    col3_w = close.get_width()
    strips_total_h = sum(c.get_height() + label_h + pad for _, c, _ in strips)
    col_h = max(hd_h + label_h, hn_h + label_h, strips_total_h,
                close.get_height() + label_h)
    sheet_w = pad + col1_w + pad + col1_w + pad + col2_w + pad + col3_w + pad
    sheet_h = head_h + col_h + pad * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render("moai-monolith — stacked ancestor idol tower  ·  round_2",
                            True, (245, 240, 230)), (pad, 12))
    sheet.blit(sub.render("red column edges = PIPE_W (58px) collision band  ·  "
                          "fixed-scoria pukao  ·  clean single-lobe heads  ·  "
                          "deeper neck pinch  ·  lit night rim", True,
                          (170, 172, 182)), (pad, 40))

    # col 1: hero day
    x = pad
    y = head_h
    sheet.blit(hero_day, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, col1_w, hd_h), 1)
    sheet.blit(lab.render("HERO — DAY totem", True, (255, 224, 150)),
               (x, y + hd_h + 4))

    # col 2: hero night
    x += col1_w + pad
    sheet.blit(hero_night, (x, y))
    pygame.draw.rect(sheet, (60, 62, 72), (x, y, col1_w, hn_h), 1)
    sheet.blit(lab.render("HERO — NIGHT (pukao-red + rim)", True, (255, 224, 150)),
               (x, y + hn_h + 4))

    # col 3: feasibility strips
    x += col1_w + pad
    sy = head_h
    sheet.blit(lab.render("FILL — bottom section", True, (255, 224, 150)),
               (x, sy - 20))
    for h, crop, run in strips:
        sheet.blit(crop, (x, sy))
        pygame.draw.rect(sheet, (60, 62, 72), (x, sy, col2_w, crop.get_height()), 1)
        ok = "OK" if run <= 12 else "FAIL"
        sheet.blit(lab.render(f"h={h}px  ·  run {run}px  [{ok}]", True,
                              (200, 235, 170) if run <= 12 else (255, 140, 140)),
                   (x, sy + crop.get_height() + 4))
        sy += crop.get_height() + label_h + pad

    # col 4: mirror close-up
    x += col2_w + pad
    sheet.blit(close, (x, head_h))
    pygame.draw.rect(sheet, (60, 62, 72),
                     (x, head_h, close.get_width(), close.get_height()), 1)
    sheet.blit(lab.render("CLOSE-UP — mirrored TOP (flip check)", True,
                          (255, 224, 150)), (x, head_h + close.get_height() + 4))

    out = pathlib.Path(__file__).resolve().parent / "round_2.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
