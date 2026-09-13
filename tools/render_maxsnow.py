"""DESIGN PICK: 5 distinctive MAXIMUM-snow designs. Much more snow
at the storm peak — draping the whole body, the head crown, and a
cap on the PARCEL. Buildup uses the picked PATCHY order. The flake
body/head set is a WIDER pool (swapped into _SNOW_POOL); parcel
snow is drawn as a separate pass on top (replicating the in-game
pass we'll add after the parcel blit).

Renders a 5-row (designs) x 3-col (load 0.45 / 0.75 / 1.00) grid.

Output: docs/screenshots/wind_themes/snow_back/maxsnow_sheet.png

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
      python -m tools.render_maxsnow
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import game.entities as E
from game.entities import Bird, _snow_disc

pygame.init()
pygame.display.set_mode((360, 640))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes", "snow_back")
os.makedirs(OUT_DIR, exist_ok=True)

LOADS = [0.45, 0.75, 1.00]
A1, A2 = 0.7548776662, 0.5698402910

# Continuous top line tail tip -> back -> nape -> crown (head-forward).
LINE = [
    (-31.0, -2.0), (-25.0, -4.0), (-19.0, -6.0), (-12.0, -8.0),
    (-5.0,  -8.5), (2.0,  -8.0),  (8.0,  -9.0),
    (11.0, -15.0), (16.5, -19.5), (19.0, -21.0),
]


def _line_y(x):
    k = LINE
    if x <= k[0][0]:
        return k[0][1]
    if x >= k[-1][0]:
        return k[-1][1]
    for j in range(len(k) - 1):
        x0, y0 = k[j]
        x1, y1 = k[j + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return k[-1][1]


def _patchy(pool):
    # chosen buildup order: perimeter-first, windward high-spots seed
    return sorted(pool, key=lambda p: abs(p[2]) * 1.3 - p[3] * 3.0)


def body_pool(dy_end, wmul, M, prof, dy_full=5.0, y_hi=18.0):
    """Wider body+head flake pool. The band drapes from the top
    line down by up to dy_end (big dy_end = snow wraps the whole
    body). `prof(x, dy)` shapes the volume. Patchy-sorted."""
    pool = []
    x_lo, x_hi, y_lo = -29.5, 20.5, -26.0
    for i in range(M):
        u = (0.5 + A1 * (i + 1)) % 1.0
        v = (0.5 + A2 * (i + 1)) % 1.0
        x = x_lo + u * (x_hi - x_lo)
        y = y_lo + v * (y_hi - y_lo)
        if x > 13.0 and y > -17.0:           # face guard (keep off lenses)
            continue
        dy = y - _line_y(x)
        if dy < -1.5:
            continue
        if dy < 0.0:
            wy = max(0.0, 1.0 + dy / 1.5) * 0.6
        elif dy <= dy_full:
            wy = 1.0
        else:
            wy = max(0.0, 1.0 - (dy - dy_full) / (dy_end - dy_full))
        wind = 1.0 + max(0.0, -x) / 55.0
        noise = 0.78 + 0.22 * ((math.sin(i * 12.9898) * 43758.5453) % 1.0)
        w = wy * wind * noise * wmul * prof(x, dy)
        if w <= 0.001:
            continue
        pool.append((x, y, dy, w))
    return _patchy(pool)


# ── volume profiles ──────────────────────────────────────────────────────────

def p_even(x, dy):
    return 1.0


def p_lumpy(x, dy):
    return 0.7 + 0.45 * (math.cos(x * 0.7) * math.cos(x * 0.31) + 1.0) / 2.0 + 0.3


def p_rear(x, dy):
    if x < -5.0:
        return 1.35
    if x > 6.0:
        return max(0.45, 1.0 - (x - 6.0) / 14.0)
    return 1.0


# ── 5 designs ────────────────────────────────────────────────────────────────
# (pool builder, parcel-snow amount)
DESIGNS = [
    ("1  FULL BLANKET",   lambda: body_pool(16.0, 1.4, 1500, p_even), 1.0),
    ("2  SNOWMAN encased", lambda: body_pool(24.0, 1.5, 2000, p_even, y_hi=22.0), 1.4),
    ("3  LAYERED drifts", lambda: body_pool(16.0, 1.5, 1600, p_lumpy), 1.1),
    ("4  WIND-sculpted",  lambda: body_pool(18.0, 1.5, 1600, p_rear), 0.6),
    ("5  TOTAL FROST",    lambda: body_pool(14.0, 1.1, 1500, p_even), 0.9),
]


def draw_parcel_snow(surf, pcx, pcy, load, amount):
    """Low white mound on the parcel's top face. Parcel is 22x22
    centred at (pcx, pcy); its top face sits ~y-7..-2 from centre."""
    a_amt = max(0.0, min(1.0, load * amount))
    if a_amt < 0.05:
        return
    top_y = pcy - 7
    half = 9
    n = 9
    base_a = int(min(240, 120 + a_amt * 120))
    rmax = 1
    items = []
    for i in range(n):
        t = i / (n - 1)
        x = pcx - half + t * 2 * half
        # mound profile: thicker in the middle
        hump = math.sin(t * math.pi)
        r = max(1, int((1.5 + a_amt * 4.0) * (0.5 + 0.6 * hump)))
        y = top_y - r * 0.3
        items.append((x, y, r))
        rmax = max(rmax, r)
    for x, y, r in items:
        disc = _snow_disc(r, (245, 248, 255), base_a)
        surf.blit(disc, (int(x - disc.get_width() / 2),
                         int(y - disc.get_height() / 2)))


def render_pip(pool, load, zoom, parcel_amt):
    E._SNOW_POOL = pool
    b = Bird()
    b.x = 34
    b.y = 32
    b.vy = 0
    b.snow_load = load
    cell = pygame.Surface((68, 64), pygame.SRCALPHA)
    b.draw(cell, 0, 0)
    # Parcel snow on top (parcel centre = bird centre + (0, +12))
    draw_parcel_snow(cell, 34, 32 + 12, load, parcel_amt)
    return pygame.transform.scale(cell, (68 * zoom, 64 * zoom))


def main():
    Z = 4
    pw, ph = 68 * Z, 64 * Z
    left, top, pad = 150, 30, 6
    sheet_w = left + len(LOADS) * (pw + pad) + pad
    sheet_h = top + len(DESIGNS) * (ph + pad) + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 40, 56))
    font = pygame.font.SysFont("Arial", 14, bold=True)
    small = pygame.font.SysFont("Arial", 13, bold=True)

    for c, ld in enumerate(LOADS):
        x = left + c * (pw + pad) + pad
        sheet.blit(small.render(f"load {ld:.2f}", True, (210, 225, 245)), (x + 4, 8))

    for r, (label, poolfn, pamt) in enumerate(DESIGNS):
        pool = poolfn()
        y = top + r * (ph + pad) + pad
        for li, line in enumerate(label.split("  ", 1)):
            sheet.blit(font.render(line, True, (240, 246, 255)), (8, y + 6 + li * 18))
        for c, ld in enumerate(LOADS):
            x = left + c * (pw + pad) + pad
            sheet.blit(render_pip(pool, ld, Z, pamt), (x, y))
            pygame.draw.rect(sheet, (70, 90, 120), (x - 1, y - 1, pw + 2, ph + 2), 1)

    out = os.path.join(OUT_DIR, "maxsnow_sheet.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
