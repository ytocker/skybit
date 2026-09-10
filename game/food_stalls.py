"""Food-market stall structures for the daytime FOOD-MARKET beat.

Five far-lane booth structures the cast works at — bamboo STEAMER, soup CAULDRON,
skewer GRILL, stir-fry WOK, tea/drinks URN — each the shared draw_kiosk-style
temple booth (posts + striped awning + counter + back wall) carrying a distinct
cooking apparatus with its own ANIMATED steam/smoke. Art-director SHIP-READY
(docs/sidewalk_overhaul/food_stalls/round_2.png).

The user asked for a real food market: a steaming stall, a soup cauldron, a
barbecue grill. The day_cast vendor pool's fanning + ladling poses are stationed
at the grill + cauldron so the cast reads as working the stalls.

Steam/smoke are translucent puffs that visibly CLIMB and fade with t (rising
motion, not a static smudge). Coals/flame/embers are warm but _cap150-clamped so
nothing out-pops the gold coin or breaks the night-glow ceiling. Pure-Pygame /
pygbag-safe (draw.* + Surface, BLEND_RGB_ADD for soft glow). Night cooling via
ped_cast._retint_person.
"""
from __future__ import annotations

import math

import pygame

from game.foreground_props import _mix, _shade, _clamp
from game.ped_cast import _retint_person as _retint

NIGHT_GLOW_CAP = 150
HALF_W = 22


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _cap150(col):
    """Hold a lit ember/flame/glow under the 150 luma ceiling without flattening
    hue — the contract that keeps the gold coin the brightest object."""
    y = _luma(col)
    if y <= NIGHT_GLOW_CAP:
        return col
    k = NIGHT_GLOW_CAP / y
    return (_clamp(col[0] * k), _clamp(col[1] * k), _clamp(col[2] * k))


def _wisp(surf, x, y0, t, *, n=3, rise=20, spread=3.0, speed=0.55, phase=0.0,
          color=(232, 232, 236), peak_a=70, r0=2, sway=2.4):
    """A rising column of `n` translucent puffs reading as RISING MOTION: each
    puff eases up the full `rise` while fattening + drifting, and fades over its
    top third so it visibly dissipates at the crest. Cool/pale = steam; warm + low
    alpha = thin smoke."""
    for i in range(n):
        ph = ((t * speed) + phase + i / n) % 1.0
        climb = 1.0 - (1.0 - ph) * (1.0 - ph)
        yy = y0 - climb * rise
        xx = x + math.sin(ph * math.pi * 1.6 + i * 1.3 + t * 0.7) * sway
        if ph < 0.18:
            a = peak_a * (ph / 0.18)
        else:
            a = peak_a * (1.0 - (ph - 0.18) / 0.82) ** 1.4
        if a < 4:
            continue
        rr = int(r0 + ph * spread)
        d = rr * 2 + 2
        layer = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(layer, (*color, int(a)), (rr + 1, rr + 1), rr)
        pygame.draw.circle(layer, (*color, int(a * 0.5)), (rr + 1, rr + 1), max(1, rr - 1))
        surf.blit(layer, (int(xx) - rr - 1, int(yy) - rr - 1))


def _warm_glow(surf, cx, cy, *, radius, peak, color):
    """A small capped additive halo for coals/flame — held low + capped so even
    over the lit ember it stays under 150 luma and below the coin."""
    col = _cap150(color)
    d = radius * 2 + 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    for rr in range(radius, 0, -1):
        a = int(peak * (rr / radius) * (1.0 - rr / radius) * 4.0)
        if a <= 0:
            continue
        k = rr / radius
        c = (int(col[0] * (0.5 + 0.5 * (1 - k))),
             int(col[1] * (0.5 + 0.5 * (1 - k))),
             int(col[2] * (0.5 + 0.5 * (1 - k))))
        pygame.draw.circle(g, (*c, min(255, a)), (radius + 1, radius + 1), rr)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


def _steam_col(night):
    return _mix((236, 238, 240), (150, 170, 200), 0.35 + 0.4 * night)


def _smoke_col(night):
    return _mix((200, 190, 180), (120, 120, 130), 0.4 + 0.3 * night)


# ── shared booth shell (matched to draw_kiosk) ────────────────────────────────

def _flat_awning(surf, sx, post_top, half_w, night, awning):
    aw = half_w + 1
    ay = post_top - 4
    palette = {
        "terra": (198, 86, 66), "cream": (236, 224, 204),
        "bamboo": (170, 150, 96), "indigo": (86, 104, 150),
        "jade": (108, 150, 120), "rust": (176, 96, 58),
    }
    a_name, b_name = awning
    dimk = min(0.72, 1.3 * night)
    col_a = _mix(palette[a_name], (70, 70, 96), min(0.6, 0.9 * night))
    col_b = _mix(palette[b_name], (74, 80, 104), dimk)
    pygame.draw.rect(surf, _mix((110, 80, 50), (60, 66, 92), 0.3 * night),
                     (sx - aw - 1, ay - 2, aw * 2 + 2, 2))
    for i, ax in enumerate(range(sx - aw, sx + aw, 6)):
        col = col_a if i % 2 == 0 else col_b
        pygame.draw.polygon(surf, col, [
            (ax, ay), (ax + 6, ay), (ax + 6, ay + 4), (ax + 3, ay + 6), (ax, ay + 4)])


def _stall_shell(surf, sx, base_y, night, *, awning=("terra", "cream"),
                 counter_h=15, post_top_off=34, roof=True, sign=None):
    half_w = HALF_W
    post_top = base_y - post_top_off
    post = _mix((92, 64, 40), (60, 66, 92), 0.30 * night)
    post_dk = _shade(post, -20)
    for px in (sx - half_w + 3, sx + half_w - 3):
        pygame.draw.rect(surf, post, (px - 1, post_top, 3, base_y - post_top))
        pygame.draw.line(surf, post_dk, (px + 1, post_top), (px + 1, base_y), 1)
    wall = _mix((150, 132, 110), (150, 124, 96), 0.5)
    wall = _mix(wall, (56, 62, 88), 0.32 * night)
    pygame.draw.rect(surf, _shade(wall, -10),
                     (sx - half_w + 4, post_top + 2, (half_w - 4) * 2, 13))
    if roof:
        _flat_awning(surf, sx, post_top, half_w, night, awning)
    counter = _mix((120, 84, 52), (60, 66, 92), 0.30 * night)
    counter_lt = _shade(counter, 16)
    cy = base_y - counter_h
    pygame.draw.rect(surf, counter, (sx - half_w + 1, cy, (half_w - 1) * 2, counter_h))
    pygame.draw.rect(surf, counter_lt, (sx - half_w + 1, cy, (half_w - 1) * 2, 2))
    pygame.draw.rect(surf, _shade(counter, -22),
                     (sx - half_w + 1, base_y - 4, (half_w - 1) * 2, 4))
    if sign:
        col = _cap150(_retint(sign, night))
        bx = sx - half_w + 6
        by = post_top + 1
        pygame.draw.rect(surf, col, (bx - 2, by, 5, 12))
        pygame.draw.rect(surf, _shade(col, -30), (bx - 2, by, 5, 12), 1)
        pygame.draw.line(surf, _shade(col, 24), (bx, by + 3), (bx, by + 9), 1)
    return cy


# ── the five stalls — (surf, sx, base_y, night, t) ────────────────────────────

def stall_steamer(surf, sx, base_y, night, t):
    cy = _stall_shell(surf, sx, base_y, night, awning=("terra", "cream"), sign=(190, 150, 90))
    stove = _retint((86, 70, 60), night)
    pygame.draw.rect(surf, stove, (sx - 10, cy - 6, 20, 6))
    pygame.draw.rect(surf, _shade(stove, -20), (sx - 10, cy - 6, 20, 6), 1)
    pygame.draw.line(surf, _shade(stove, 18), (sx - 9, cy - 5), (sx + 9, cy - 5), 1)
    if night > 0.05:
        _warm_glow(surf, sx, cy - 3, radius=7, peak=46, color=(150, 96, 50))
    bamboo = _retint((188, 156, 96), night)
    bamboo_d = _shade(bamboo, -34)
    bamboo_hi = _shade(bamboo, 18)
    bx = sx - 11
    bw = 22
    by = cy - 6
    for i in range(4):
        band_y = by - 5 - i * 5
        rim = pygame.Rect(bx + 1, band_y, bw - 2, 6)
        pygame.draw.ellipse(surf, bamboo, rim)
        pygame.draw.ellipse(surf, bamboo_d, rim, 1)
        pygame.draw.line(surf, bamboo_hi, (rim.left + 1, band_y + 1), (rim.right - 1, band_y + 1), 1)
        pygame.draw.line(surf, bamboo_d, (rim.left + 1, band_y + 4), (rim.right - 1, band_y + 4), 1)
        _wisp(surf, sx - 5 + i * 3, band_y, t, n=2, rise=10, spread=2.0,
              speed=0.6, phase=i * 0.3, peak_a=46, r0=1, sway=2.0, color=_steam_col(night))
    lid_y = by - 5 - 4 * 5
    pygame.draw.ellipse(surf, bamboo, (bx + 1, lid_y - 2, bw - 2, 7))
    pygame.draw.arc(surf, bamboo_hi, (bx + 3, lid_y - 5, bw - 6, 9), math.radians(20), math.radians(160), 2)
    pygame.draw.circle(surf, bamboo_d, (sx, lid_y - 2), 1)
    _wisp(surf, sx, lid_y - 2, t, n=4, rise=26, spread=3.4, speed=0.5,
          phase=0.1, peak_a=78, r0=2, sway=3.0, color=_steam_col(night))
    _wisp(surf, sx + 4, lid_y - 1, t, n=3, rise=20, spread=2.6, speed=0.55,
          phase=0.5, peak_a=58, r0=2, sway=2.6, color=_steam_col(night))


def stall_cauldron(surf, sx, base_y, night, t):
    cy = _stall_shell(surf, sx, base_y, night, awning=("indigo", "cream"), sign=(168, 96, 80))
    brick = _retint((150, 96, 70), night)
    pygame.draw.rect(surf, brick, (sx - 13, cy - 8, 26, 8))
    pygame.draw.rect(surf, _shade(brick, -22), (sx - 13, cy - 8, 26, 8), 1)
    for bxx in range(sx - 11, sx + 12, 7):
        pygame.draw.line(surf, _shade(brick, -16), (bxx, cy - 8), (bxx, cy), 1)
    pygame.draw.line(surf, _shade(brick, -16), (sx - 12, cy - 4), (sx + 12, cy - 4), 1)
    if night > 0.05:
        _warm_glow(surf, sx, cy - 2, radius=8, peak=52, color=(150, 92, 46))
    pygame.draw.ellipse(surf, _cap150((128, 70, 36) if night > 0.05 else (70, 44, 30)),
                        (sx - 5, cy - 4, 10, 3))
    pot = _retint((64, 60, 62), night)
    pot_d = _shade(pot, -22)
    pot_hi = _shade(pot, 22)
    py = cy - 8
    belly = pygame.Rect(sx - 16, py - 11, 32, 14)
    pygame.draw.ellipse(surf, pot, belly)
    pygame.draw.ellipse(surf, pot_d, belly, 1)
    pygame.draw.arc(surf, pot_hi, belly, math.radians(20), math.radians(80), 1)
    broth = _retint((150, 96, 58), night)
    rim = pygame.Rect(sx - 14, py - 12, 28, 7)
    pygame.draw.ellipse(surf, _shade(pot, -10), rim)
    pygame.draw.ellipse(surf, broth, rim.inflate(-3, -2))
    for k, ph in ((-4, 0.0), (5, 0.5), (1, 0.8)):
        fy = py - 9 + int(math.sin(t * 2.0 + ph * 6) * 0.6)
        pygame.draw.circle(surf, _retint((196, 150, 92), night), (sx + k, fy), 1)
    ladle = _retint((150, 120, 70), night)
    pygame.draw.line(surf, ladle, (sx + 9, py - 11), (sx + 16, py - 19), 1)
    pygame.draw.circle(surf, _shade(ladle, 14), (sx + 16, py - 19), 1)
    _wisp(surf, sx - 4, py - 11, t, n=4, rise=30, spread=3.6, speed=0.5,
          phase=0.0, peak_a=80, r0=2, sway=3.4, color=_steam_col(night))
    _wisp(surf, sx + 5, py - 11, t, n=3, rise=25, spread=3.0, speed=0.58,
          phase=0.5, peak_a=62, r0=2, sway=3.0, color=_steam_col(night))


def stall_grill(surf, sx, base_y, night, t):
    cy = _stall_shell(surf, sx, base_y, night, awning=("rust", "cream"), sign=(176, 110, 70))
    metal = _retint((52, 50, 56), night)
    metal_d = _shade(metal, -16)
    trough = pygame.Rect(sx - 17, cy - 10, 34, 8)
    pygame.draw.rect(surf, metal, trough)
    pygame.draw.rect(surf, metal_d, trough, 1)
    pygame.draw.line(surf, _shade(metal, 14), (trough.left + 1, trough.top + 1),
                     (trough.right - 1, trough.top + 1), 1)
    for lx in (sx - 15, sx + 14):
        pygame.draw.line(surf, metal_d, (lx, cy - 2), (lx, cy + 3), 1)
    ash = _retint((34, 30, 34), night)
    pygame.draw.rect(surf, ash, (sx - 15, cy - 8, 30, 4))
    if night > 0.05:
        _warm_glow(surf, sx, cy - 6, radius=12, peak=54, color=(150, 84, 40))
    coal_hot = (148, 80, 34) if night > 0.05 else (150, 88, 38)
    coal_dk = _shade(coal_hot, -34)
    for j, kx in enumerate((-9, 0, 9)):
        pulse = 0.55 + 0.45 * math.sin(t * 3.0 + j * 1.9)
        col = _cap150(_mix(coal_dk, coal_hot, pulse))
        pygame.draw.rect(surf, col, (sx + kx - 1, cy - 7, 3, 2))
        pygame.draw.circle(surf, _cap150(_mix(coal_hot, (150, 110, 60), pulse)), (sx + kx, cy - 7), 1)
    char = _retint((40, 32, 30), night)
    meat = _retint((128, 80, 58), night)
    meat_hi = _shade(meat, 18)
    for kx, lift in ((-9, 0), (0, -1), (9, 0)):
        sxp = sx + kx
        sky = cy - 10 + lift
        pygame.draw.line(surf, char, (sxp - 7, sky + 1), (sxp + 7, sky + 1), 2)
        for mi, mx in enumerate((sxp - 4, sxp, sxp + 4)):
            mc = meat if (mi + kx) % 2 == 0 else _shade(meat, -16)
            pygame.draw.rect(surf, mc, (mx - 1, sky - 2, 3, 3))
            pygame.draw.line(surf, meat_hi, (mx - 1, sky - 2), (mx + 1, sky - 2), 1)
    smoke = _smoke_col(night)
    _wisp(surf, sx - 6, cy - 11, t, n=3, rise=28, spread=2.6, speed=0.62,
          phase=0.0, peak_a=46, r0=1, sway=3.2, color=smoke)
    _wisp(surf, sx + 5, cy - 11, t, n=3, rise=24, spread=2.4, speed=0.7,
          phase=0.4, peak_a=40, r0=1, sway=3.0, color=smoke)
    for i in range(3):
        ph = (t * 0.8 + i * 0.4) % 1.0
        ex = sx - 4 + i * 5 + int(math.sin(ph * 6 + i) * 3)
        ey = cy - 11 - int(ph * 16)
        a = int(120 * (1.0 - ph))
        if a > 8:
            lay = pygame.Surface((2, 2), pygame.SRCALPHA)
            lay.fill((*_cap150((150, 90, 40)), a))
            surf.blit(lay, (ex, ey), special_flags=pygame.BLEND_RGB_ADD)


def stall_wok(surf, sx, base_y, night, t):
    cy = _stall_shell(surf, sx, base_y, night, awning=("jade", "cream"), sign=(150, 120, 70))
    stove = _retint((70, 64, 64), night)
    stove_d = _shade(stove, -20)
    pygame.draw.polygon(surf, stove, [(sx - 8, cy - 9), (sx + 8, cy - 9), (sx + 11, cy), (sx - 11, cy)])
    pygame.draw.polygon(surf, stove_d, [(sx - 8, cy - 9), (sx + 8, cy - 9), (sx + 11, cy), (sx - 11, cy)], 1)
    flick = math.sin(t * 11.0) * 0.5 + math.sin(t * 7.3) * 0.5
    fh = int(4 + flick * 2)
    if night > 0.05:
        _warm_glow(surf, sx, cy - 9, radius=11, peak=56, color=(150, 88, 40))
    for fx, fhh, col in ((sx - 4, fh, (148, 78, 30)), (sx + 3, fh + 1, (150, 92, 38)), (sx, fh + 2, (146, 100, 44))):
        col = _cap150(col if night > 0.05 else _shade(col, -30))
        pygame.draw.polygon(surf, col, [(fx - 2, cy - 9), (fx + 2, cy - 9), (fx, cy - 9 - fhh)])
    wok = _retint((48, 46, 52), night)
    wok_hi = _shade(wok, 24)
    belly = pygame.Rect(sx - 13, cy - 16, 26, 11)
    pygame.draw.ellipse(surf, wok, belly)
    pygame.draw.ellipse(surf, _shade(wok, -22), belly, 1)
    pygame.draw.arc(surf, wok_hi, belly, math.radians(20), math.radians(90), 1)
    rim_pts = [(sx - 12, cy - 14), (sx - 4, cy - 17), (sx + 6, cy - 18),
               (sx + 12, cy - 16), (sx + 5, cy - 14), (sx - 5, cy - 13)]
    pygame.draw.polygon(surf, _shade(wok, -8), rim_pts)
    food = _retint((176, 138, 84), night)
    pygame.draw.ellipse(surf, food, (sx - 6, cy - 16, 14, 4))
    for k, ph in ((-4, 0.0), (3, 0.4), (6, 0.7)):
        pygame.draw.circle(surf, _retint((196, 100, 80), night),
                           (sx + k, cy - 16 + int(math.sin(t * 2 + ph * 6))), 1)
    hcol = _retint((118, 90, 60), night)
    hx0, hy0 = sx - 12, cy - 14
    hx1, hy1 = sx - 26, cy - 22
    pygame.draw.line(surf, _shade(hcol, -24), (hx0, hy0 + 1), (hx1, hy1 + 1), 3)
    pygame.draw.line(surf, hcol, (hx0, hy0), (hx1, hy1), 2)
    pygame.draw.line(surf, _shade(hcol, 20), (hx0, hy0 - 1), (hx1 + 2, hy1), 1)
    pygame.draw.circle(surf, _shade(hcol, -16), (hx1, hy1), 2)
    _wisp(surf, sx, cy - 18, t, n=4, rise=28, spread=3.2, speed=0.52,
          phase=0.0, peak_a=74, r0=2, sway=3.4, color=_steam_col(night))
    _wisp(surf, sx - 4, cy - 17, t, n=3, rise=22, spread=2.4, speed=0.62,
          phase=0.5, peak_a=54, r0=1, sway=2.8, color=_steam_col(night))


def stall_tea(surf, sx, base_y, night, t):
    cy = _stall_shell(surf, sx, base_y, night, awning=("bamboo", "indigo"), sign=(176, 96, 80))
    if night > 0.05:
        _warm_glow(surf, sx - 6, cy - 3, radius=6, peak=40, color=(150, 92, 46))
    warmer = _retint((92, 76, 64), night)
    pygame.draw.rect(surf, warmer, (sx - 11, cy - 4, 12, 4))
    pygame.draw.rect(surf, _shade(warmer, -20), (sx - 11, cy - 4, 12, 4), 1)
    brass = _retint((176, 142, 78), night)
    brass_d = _shade(brass, -34)
    brass_hi = _shade(brass, 26)
    ux = sx - 5
    body = pygame.Rect(ux - 6, cy - 22, 12, 18)
    pygame.draw.ellipse(surf, brass, body)
    pygame.draw.ellipse(surf, brass_d, body, 1)
    pygame.draw.line(surf, brass_hi, (ux - 2, cy - 20), (ux - 2, cy - 8), 1)
    pygame.draw.ellipse(surf, _shade(brass, -10), (ux - 6, cy - 24, 12, 5))
    pygame.draw.circle(surf, brass_hi, (ux, cy - 24), 1)
    pygame.draw.lines(surf, _shade(brass, -18), False,
                      [(ux + 5, cy - 13), (ux + 11, cy - 18), (ux + 14, cy - 24), (ux + 13, cy - 28)], 3)
    pygame.draw.lines(surf, brass, False,
                      [(ux + 5, cy - 14), (ux + 11, cy - 18), (ux + 14, cy - 24), (ux + 13, cy - 27)], 2)
    pygame.draw.circle(surf, brass_hi, (ux + 13, cy - 27), 1)
    pygame.draw.arc(surf, brass_d, (ux - 9, cy - 18, 5, 9), math.radians(60), math.radians(300), 1)
    cup = _retint((210, 200, 180), night)
    pygame.draw.ellipse(surf, cup, (sx + 8, cy - 5, 8, 4))
    pygame.draw.ellipse(surf, _shade(cup, -30), (sx + 8, cy - 5, 8, 4), 1)
    pygame.draw.line(surf, _shade(cup, 16), (sx + 10, cy - 4), (sx + 14, cy - 4), 1)
    _wisp(surf, ux + 13, cy - 28, t, n=3, rise=24, spread=2.2, speed=0.55,
          phase=0.0, peak_a=58, r0=1, sway=2.6, color=_steam_col(night))


# Stall kinds → drawer, and the day_cast vendor pose (pool index) that works it.
STALLS = {
    "steamer":  (stall_steamer, 0),    # V1 calling
    "cauldron": (stall_cauldron, 3),   # V4 ladling
    "grill":    (stall_grill, 2),      # V3 fanning
    "wok":      (stall_wok, 2),        # V3 fanning
    "tea":      (stall_tea, 0),        # V1 calling
}
