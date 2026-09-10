"""Five polished crown redesigns — iteration on the amateur first pass.

The previous _draw_crown was three flat triangles + a flat band + dot
gems, all rendered at the target resolution. Edges were jaggy and the
silhouette read as cartoon-y. This pass redraws each crown:

  * 3x oversampling + smoothscale  → anti-aliased edges
  * 3-stop gold gradients          → readable depth
  * Distinct silhouettes           → not just "same crown, different gem"

Renders five PNG previews to tools/screenshots/:

  crown_r1.png — Royal Velvet     (5-peak medieval + velvet cap + pearls)
  crown_r2.png — Imperial Cross   (arched dome + orb + cross on apex)
  crown_r3.png — Sharp Spires     (5 thin spires + hex sapphire centre)
  crown_r4.png — Diamond Tiara    (3 peaks + kite-cut jewels + filigree)
  crown_r5.png — Onion Dome       (Russian style + ermine trim + cabochon)

Run from repo root:
  python3 tools/preview_crown_redesigns.py
"""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import sys
import pygame

pygame.init()
pygame.font.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H
from tools.preview_crown_variants import (
    draw_leaderboard_variant, draw_bg, SCORES,
)


# ── Shared palette ──────────────────────────────────────────────────────────

GOLD_HI    = (255, 232, 132)
GOLD       = (240, 192,  64)
GOLD_LO    = (188, 138,  28)
GOLD_DEEP  = (110,  72,   8)
VELVET     = (140,  18,  22)
VELVET_DK  = ( 80,   8,  10)
PEARL      = (252, 248, 232)
PEARL_SH   = (200, 195, 175)
RUBY       = (220,  40,  50)
RUBY_HI    = (255, 180, 190)
SAPPHIRE   = ( 64, 102, 220)
SAPPHIRE_HI= (172, 200, 255)
EMERALD    = ( 64, 200, 100)
EMERALD_HI = (172, 240, 192)
FUR        = (245, 240, 230)
FUR_SH     = (170, 160, 145)
ERMINE     = ( 40,  30,  25)
DARK_GOLD  = (115,  85,  20)
WHITE_HI   = (255, 255, 255)


def _oversampled(draw_fn, w, h, s=3):
    """Render draw_fn onto an s×-oversampled surface, then smoothscale
    down to (w, h) for anti-aliased edges."""
    big = pygame.Surface((w * s, h * s), pygame.SRCALPHA)
    draw_fn(big, s)
    return pygame.transform.smoothscale(big, (w, h))


def _with_shadow(img, offset=(2, 2), alpha=110):
    """Return a composite surface: drop shadow under + crown on top.
    The shadow is the crown's silhouette tinted black at `alpha`."""
    shadow = img.copy()
    shadow.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
    shadow.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    composite = pygame.Surface(
        (img.get_width() + offset[0], img.get_height() + offset[1]),
        pygame.SRCALPHA)
    composite.blit(shadow, offset)
    composite.blit(img, (0, 0))
    return composite


def _band_gradient(surf, rect, s):
    """Vertical 3-stop gold gradient: hi (top) → gold → lo (bottom)."""
    x, y, w, h = rect
    for yy in range(h):
        u = yy / max(1, h - 1)
        if u < 0.4:
            t = u / 0.4
            col = tuple(int(GOLD_HI[i] * (1 - t) + GOLD[i] * t) for i in range(3))
        else:
            t = (u - 0.4) / 0.6
            col = tuple(int(GOLD[i] * (1 - t) + GOLD_LO[i] * t) for i in range(3))
        pygame.draw.line(surf, col + (255,),
                         (x, y + yy), (x + w - 1, y + yy))


def _quad_bezier(p0, p1, p2, n=14):
    """Quadratic-bezier polyline."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


# ── Design 1: Royal Velvet ──────────────────────────────────────────────────

def _draw_royal(big, s):
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2
    band_top = 14 * s
    band_bot = 21 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    # Drop shadow under the band
    pygame.draw.rect(big, GOLD_DEEP,
                     (band_l - 1, band_top + s,
                      band_r - band_l + 2, band_bot - band_top),
                     border_radius=s)
    _band_gradient(big,
                   (band_l, band_top, band_r - band_l, band_bot - band_top), s)
    pygame.draw.rect(big, DARK_GOLD,
                     (band_l, band_top, band_r - band_l, band_bot - band_top),
                     border_radius=s, width=max(1, s // 2))
    # Velvet cap behind peaks (rounded top, hidden behind gold)
    velvet_top = 5 * s
    pygame.draw.rect(big, VELVET,
                     (band_l + 2 * s, velvet_top,
                      band_r - band_l - 4 * s, band_top - velvet_top),
                     border_top_left_radius=3 * s,
                     border_top_right_radius=3 * s)
    pygame.draw.rect(big, VELVET_DK,
                     (band_l + 2 * s + (band_r - band_l - 4 * s) * 2 // 3,
                      velvet_top + s,
                      (band_r - band_l - 4 * s) // 3, band_top - velvet_top - s),
                     border_top_right_radius=3 * s)
    # 5 peaks (gold, multi-tone)
    centers = [cx - 10 * s, cx - 4 * s, cx, cx + 4 * s, cx + 10 * s]
    heights = [4 * s,  7 * s, 11 * s,  7 * s,  4 * s]
    pw = 3 * s
    for px, ph in zip(centers, heights):
        tip = (px, band_top - ph)
        l   = (px - pw, band_top + 1)
        r   = (px + pw, band_top + 1)
        pygame.draw.polygon(big, GOLD_DEEP,
                            [(tip[0], tip[1] + s),
                             (l[0] - 1, l[1]),
                             (r[0] + 1, r[1])])
        pygame.draw.polygon(big, GOLD_LO, [tip, l, r])
        pygame.draw.polygon(big, GOLD,
                            [tip, l, (px, band_top + 1)])
        pygame.draw.line(big, GOLD_HI,
                         tip, (px - s, band_top), max(1, s // 2))
    # Pearl on each peak tip
    for px, ph in zip(centers, heights):
        tip = (px, band_top - ph)
        pygame.draw.circle(big, PEARL_SH, (tip[0], tip[1] - s), s + 1)
        pygame.draw.circle(big, PEARL, (tip[0], tip[1] - s), s)
        pygame.draw.circle(big, WHITE_HI, (tip[0] - 1, tip[1] - s - 1), 1)
    # Pearl trim along the band's upper edge
    bx = band_l + 2 * s
    while bx <= band_r - 2 * s:
        pygame.draw.circle(big, PEARL, (bx, band_top + s),
                           max(1, s - 1))
        bx += 2 * s
    # Centre ruby gem
    band_cx = (band_l + band_r) // 2
    band_cy = (band_top + band_bot) // 2 + 1
    pygame.draw.circle(big, GOLD_DEEP, (band_cx, band_cy + 1), 2 * s)
    pygame.draw.circle(big, RUBY, (band_cx, band_cy), 2 * s - 1)
    pygame.draw.circle(big, RUBY_HI, (band_cx - 1, band_cy - 1), s)


def draw_crown_royal(surf, cx, cy):
    bw, bh = 38, 28
    img = _with_shadow(_oversampled(_draw_royal, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2))


# ── Design 2: Imperial Cross ────────────────────────────────────────────────

def _draw_imperial(big, s):
    bw, bh = big.get_width(), big.get_height()
    band_top = 18 * s
    band_bot = 24 * s
    band_l = 3 * s
    band_r = bw - 3 * s
    pygame.draw.rect(big, GOLD_DEEP,
                     (band_l - 1, band_top + s,
                      band_r - band_l + 2, band_bot - band_top),
                     border_radius=s)
    _band_gradient(big,
                   (band_l, band_top, band_r - band_l, band_bot - band_top), s)
    pygame.draw.rect(big, DARK_GOLD,
                     (band_l, band_top, band_r - band_l, band_bot - band_top),
                     border_radius=s, width=max(1, s // 2))
    # Three gems on the band: sapphire / ruby / emerald
    band_cy = (band_top + band_bot) // 2
    for fx, col, hi in (
            (band_l + 5 * s, SAPPHIRE, SAPPHIRE_HI),
            ((band_l + band_r) // 2, RUBY, RUBY_HI),
            (band_r - 5 * s, EMERALD, EMERALD_HI)):
        pygame.draw.circle(big, GOLD_DEEP, (fx, band_cy + 1), int(1.7 * s))
        pygame.draw.circle(big, col, (fx, band_cy), int(1.5 * s))
        pygame.draw.circle(big, hi, (fx - 1, band_cy - 1), max(1, s // 2))
    # Velvet dome inside the arches
    dome_rect = pygame.Rect(band_l + 3 * s, 6 * s,
                            band_r - band_l - 6 * s, band_top - 6 * s + 2)
    pygame.draw.ellipse(big, VELVET, dome_rect)
    pygame.draw.ellipse(big, VELVET_DK,
                        (dome_rect.x + dome_rect.w * 3 // 5,
                         dome_rect.y + s,
                         dome_rect.w * 2 // 5, dome_rect.h - 2 * s))
    # Two crossing arches via quadratic bezier
    cx_mid = (band_l + band_r) // 2
    arch_top = 5 * s
    arch_thick = max(s, 2)
    left = _quad_bezier(
        (band_l + 3 * s, band_top),
        (band_l + 4 * s, arch_top),
        (cx_mid, arch_top))
    right = _quad_bezier(
        (band_r - 3 * s, band_top),
        (band_r - 4 * s, arch_top),
        (cx_mid, arch_top))
    pygame.draw.lines(big, GOLD_DEEP, False,
                      [(x, y + s) for x, y in left], arch_thick + s)
    pygame.draw.lines(big, GOLD_DEEP, False,
                      [(x, y + s) for x, y in right], arch_thick + s)
    pygame.draw.lines(big, GOLD_LO, False, left, arch_thick + 1)
    pygame.draw.lines(big, GOLD_LO, False, right, arch_thick + 1)
    pygame.draw.lines(big, GOLD, False, left, arch_thick)
    pygame.draw.lines(big, GOLD, False, right, arch_thick)
    # Highlight along the inside of each arch
    pygame.draw.lines(big, GOLD_HI, False,
                      [(x, y - 1) for x, y in left[: len(left) // 2 + 1]],
                      max(1, s // 2))
    # Orb at the apex
    orb_cx, orb_cy = cx_mid, arch_top - s
    pygame.draw.circle(big, GOLD_DEEP, (orb_cx, orb_cy + 1), int(1.6 * s))
    pygame.draw.circle(big, GOLD, (orb_cx, orb_cy), int(1.4 * s))
    pygame.draw.circle(big, GOLD_HI, (orb_cx - 1, orb_cy - 1), max(1, s // 2))
    # Cross on top of the orb
    cross_top = orb_cy - int(3.0 * s)
    cross_bot = orb_cy - int(1.0 * s)
    cross_thick = max(2, s)
    pygame.draw.rect(big, GOLD_DEEP,
                     (orb_cx - cross_thick // 2 + 1, cross_top + 1,
                      cross_thick, cross_bot - cross_top))
    pygame.draw.rect(big, GOLD,
                     (orb_cx - cross_thick // 2, cross_top,
                      cross_thick, cross_bot - cross_top))
    cross_h_y = cross_top + int(1.2 * s)
    pygame.draw.rect(big, GOLD,
                     (orb_cx - int(1.4 * s), cross_h_y,
                      int(2.8 * s), max(1, s)))


def draw_crown_imperial(surf, cx, cy):
    bw, bh = 36, 32
    img = _with_shadow(_oversampled(_draw_imperial, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── Design 3: Sharp Spires ──────────────────────────────────────────────────

def _draw_spires(big, s):
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2
    band_top = 14 * s
    band_bot = 20 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    pygame.draw.rect(big, GOLD_DEEP,
                     (band_l - 1, band_top + s,
                      band_r - band_l + 2, band_bot - band_top),
                     border_radius=s)
    _band_gradient(big,
                   (band_l, band_top, band_r - band_l, band_bot - band_top), s)
    # Two horizontal ridges across the band for thickness
    for ry_off in (1, 2):
        ridge_y = band_top + ry_off * (band_bot - band_top) // 3
        pygame.draw.line(big, DARK_GOLD,
                         (band_l + s, ridge_y), (band_r - s, ridge_y),
                         max(1, s // 2))
        pygame.draw.line(big, GOLD_HI,
                         (band_l + s, ridge_y - 1), (band_r - s, ridge_y - 1),
                         1)
    pygame.draw.rect(big, DARK_GOLD,
                     (band_l, band_top, band_r - band_l, band_bot - band_top),
                     border_radius=s, width=max(1, s // 2))
    # 5 thin tall spires
    xs = [cx - 10 * s, cx - 5 * s, cx, cx + 5 * s, cx + 10 * s]
    hs = [6 * s, 9 * s, 13 * s, 9 * s, 6 * s]
    pw = max(1, int(1.2 * s))
    for sx, sh in zip(xs, hs):
        tip = (sx, band_top - sh)
        l   = (sx - pw, band_top + 1)
        r   = (sx + pw, band_top + 1)
        pygame.draw.polygon(big, GOLD_DEEP,
                            [(tip[0], tip[1] + s),
                             (l[0] - 1, l[1]),
                             (r[0] + 1, r[1])])
        pygame.draw.polygon(big, GOLD_LO, [tip, l, r])
        pygame.draw.polygon(big, GOLD, [tip, l, (sx, band_top + 1)])
        pygame.draw.line(big, GOLD_HI, tip, (sx - 1, band_top),
                         max(1, s // 2))
    # Pearl on each spire tip
    for sx, sh in zip(xs, hs):
        tip = (sx, band_top - sh)
        pygame.draw.circle(big, PEARL_SH, (tip[0], tip[1] - s + 1), s)
        pygame.draw.circle(big, PEARL, (tip[0], tip[1] - s + 1),
                           max(1, s - 1))
        pygame.draw.circle(big, WHITE_HI, (tip[0] - 1, tip[1] - s),
                           max(1, s // 2))
    # Hex sapphire gem in centre of band
    band_cx = (band_l + band_r) // 2
    band_cy = (band_top + band_bot) // 2
    hr = int(2.2 * s)
    pts = [
        (band_cx + math.cos(math.pi / 2 + i * math.pi / 3) * hr,
         band_cy + math.sin(math.pi / 2 + i * math.pi / 3) * hr)
        for i in range(6)
    ]
    pygame.draw.polygon(big, GOLD_DEEP, [(p[0], p[1] + 1) for p in pts])
    pygame.draw.polygon(big, SAPPHIRE, pts)
    pygame.draw.polygon(big, SAPPHIRE_HI,
                        [pts[5], pts[0], pts[1], (band_cx, band_cy)])


def draw_crown_spires(surf, cx, cy):
    bw, bh = 36, 28
    img = _with_shadow(_oversampled(_draw_spires, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2))


# ── Design 4: Diamond Tiara ─────────────────────────────────────────────────

def _draw_tiara(big, s):
    bw, bh = big.get_width(), big.get_height()
    band_top = 10 * s
    band_bot = 15 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    pygame.draw.rect(big, GOLD_DEEP,
                     (band_l - 1, band_top + 1,
                      band_r - band_l + 2, band_bot - band_top),
                     border_radius=s)
    _band_gradient(big,
                   (band_l, band_top, band_r - band_l, band_bot - band_top), s)
    # Filigree V-zigzag along band middle
    band_cy = (band_top + band_bot) // 2
    zig = max(1, s // 2)
    px = band_l + s
    while px < band_r - s:
        pygame.draw.line(big, DARK_GOLD,
                         (px, band_cy + zig), (px + s, band_cy - zig),
                         max(1, s // 2))
        pygame.draw.line(big, DARK_GOLD,
                         (px + s, band_cy - zig), (px + 2 * s, band_cy + zig),
                         max(1, s // 2))
        px += 2 * s
    pygame.draw.rect(big, DARK_GOLD,
                     (band_l, band_top, band_r - band_l, band_bot - band_top),
                     border_radius=s, width=max(1, s // 2))
    # 3 peaks with kite-cut gems
    centers = [bw // 4, bw // 2, 3 * bw // 4]
    heights = [4 * s, 8 * s, 4 * s]
    bases   = [3 * s, 4 * s, 3 * s]
    gem_cs  = [SAPPHIRE, RUBY, EMERALD]
    gem_hs  = [SAPPHIRE_HI, RUBY_HI, EMERALD_HI]
    for px, ph, bw_, gc, gh in zip(centers, heights, bases, gem_cs, gem_hs):
        tip = (px, band_top - ph)
        l   = (px - bw_, band_top + 1)
        r   = (px + bw_, band_top + 1)
        pygame.draw.polygon(big, GOLD_DEEP,
                            [(tip[0], tip[1] + 1),
                             (l[0] - 1, l[1] + 1),
                             (r[0] + 1, r[1] + 1)])
        pygame.draw.polygon(big, GOLD_LO, [tip, l, r])
        pygame.draw.polygon(big, GOLD, [tip, l, (px, band_top)])
        # Kite-cut gem
        gem_top   = (px, tip[1] - int(1.6 * s))
        gem_bot   = (px, tip[1] + int(1.3 * s))
        gem_left  = (px - int(1.3 * s), tip[1])
        gem_right = (px + int(1.3 * s), tip[1])
        pygame.draw.polygon(big, GOLD_DEEP,
                            [(gem_top[0], gem_top[1] + 1),
                             (gem_right[0] + 1, gem_right[1] + 1),
                             (gem_bot[0], gem_bot[1] + 1),
                             (gem_left[0] - 1, gem_left[1] + 1)])
        pygame.draw.polygon(big, gc, [gem_top, gem_right, gem_bot, gem_left])
        # Highlight along the left facet
        pygame.draw.polygon(big, gh, [gem_top, gem_left, (px, tip[1])])
        # Bright glint at the top
        pygame.draw.line(big, WHITE_HI,
                         (gem_top[0] - 1, gem_top[1] + 1),
                         (gem_top[0] - 1, gem_top[1] + max(1, s)), 1)


def draw_crown_tiara(surf, cx, cy):
    bw, bh = 36, 22
    img = _with_shadow(_oversampled(_draw_tiara, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2))


# ── Design 5: Onion Dome ────────────────────────────────────────────────────

def _draw_dome(big, s):
    bw, bh = big.get_width(), big.get_height()
    # Ermine fur trim at base
    fur_top = 20 * s
    fur_bot = 26 * s
    fur_l   = s
    fur_r   = bw - s
    pygame.draw.rect(big, FUR_SH,
                     (fur_l - 1, fur_top + 1,
                      fur_r - fur_l + 2, fur_bot - fur_top),
                     border_radius=s)
    pygame.draw.rect(big, FUR,
                     (fur_l, fur_top, fur_r - fur_l, fur_bot - fur_top),
                     border_radius=s)
    for spot_x in (fur_l + 3 * s, fur_l + 9 * s, fur_l + 15 * s):
        pygame.draw.circle(big, ERMINE, (spot_x, fur_top + 3 * s),
                           max(1, s // 2))
    # Bulb dome
    dome = pygame.Rect(s, 6 * s, bw - 2 * s, fur_top - 5 * s)
    pygame.draw.ellipse(big, GOLD_DEEP,
                        (dome.x + 1, dome.y + 1, dome.w, dome.h))
    pygame.draw.ellipse(big, GOLD_LO, dome)
    pygame.draw.ellipse(big, GOLD,
                        (dome.x + s, dome.y + s, dome.w - 2 * s, dome.h - 2 * s))
    pygame.draw.ellipse(big, GOLD_HI,
                        (dome.x + int(1.6 * s), dome.y + int(1.6 * s),
                         dome.w // 2, dome.h // 3))
    # Neck above the bulb
    dome_cx = bw // 2
    neck_top = 4 * s
    neck_bot = 7 * s
    neck_w = 3 * s
    pygame.draw.rect(big, GOLD_LO,
                     (dome_cx - neck_w // 2, neck_top, neck_w, neck_bot - neck_top))
    pygame.draw.line(big, GOLD_HI,
                     (dome_cx - neck_w // 2, neck_top),
                     (dome_cx - neck_w // 2, neck_bot), max(1, s // 2))
    # Mini-orb between neck and cross
    ball_cy = neck_top - s
    pygame.draw.circle(big, GOLD_DEEP, (dome_cx, ball_cy + 1), int(1.4 * s))
    pygame.draw.circle(big, GOLD, (dome_cx, ball_cy), int(1.2 * s))
    pygame.draw.circle(big, GOLD_HI, (dome_cx - 1, ball_cy - 1), max(1, s // 2))
    # Cross on top
    cross_top = max(0, ball_cy - int(3.5 * s))
    cross_h_y = cross_top + int(1.2 * s)
    cross_thick = max(1, s)
    pygame.draw.rect(big, GOLD_DEEP,
                     (dome_cx - cross_thick // 2 + 1, cross_top + 1,
                      cross_thick, int(2.5 * s)))
    pygame.draw.rect(big, GOLD,
                     (dome_cx - cross_thick // 2, cross_top,
                      cross_thick, int(2.5 * s)))
    pygame.draw.rect(big, GOLD,
                     (dome_cx - int(1.4 * s), cross_h_y,
                      int(2.8 * s), max(1, s)))
    # Cabochon ruby on the dome face
    cab_cx = dome_cx
    cab_cy = dome.y + dome.h * 2 // 3
    pygame.draw.ellipse(big, GOLD_DEEP,
                        (cab_cx - int(2.5 * s), cab_cy - int(1.7 * s) + 1,
                         int(5 * s), int(3.4 * s)))
    pygame.draw.ellipse(big, RUBY,
                        (cab_cx - int(2.5 * s), cab_cy - int(1.7 * s),
                         int(5 * s), int(3.4 * s)))
    pygame.draw.ellipse(big, RUBY_HI,
                        (cab_cx - int(1.7 * s), cab_cy - int(1.2 * s),
                         int(2 * s), int(1.2 * s)))


def draw_crown_dome(surf, cx, cy):
    bw, bh = 28, 34
    img = _with_shadow(_oversampled(_draw_dome, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── Render the five previews ────────────────────────────────────────────────

OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

CROWNS = [
    ("crown_r1.png", draw_crown_royal,    "Royal Velvet"),
    ("crown_r2.png", draw_crown_imperial, "Imperial Cross"),
    ("crown_r3.png", draw_crown_spires,   "Sharp Spires"),
    ("crown_r4.png", draw_crown_tiara,    "Diamond Tiara"),
    ("crown_r5.png", draw_crown_dome,     "Onion Dome"),
]


def main():
    screen = pygame.Surface((W, H))
    for fname, drawer, label in CROWNS:
        draw_bg(screen)
        draw_leaderboard_variant(
            screen, title_t=1.4, scores=SCORES,
            player_rank=6, variant=6, crown_drawer=drawer)
        out = os.path.join(OUT_DIR, fname)
        pygame.image.save(screen, out)
        print(f"saved {out}  ({label})")


if __name__ == "__main__":
    main()
