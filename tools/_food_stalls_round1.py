"""Food-market STALL props — round 1 candidate-sheet generator.

Third family in the sidewalk variety overhaul (after the 50-strong adult
pedestrian pool and the kids/elders/vendors day-cast). These are STALL
STRUCTURES — far-lane background fixtures the cast stands AT, not characters —
for the daytime food-market event on the scrolling sidewalk. The promenade today
ships ONE pagoda kiosk (foreground_promenade.draw_kiosk) for the whole market
beat, so a real "food market" needs several distinct cooking stalls so the row
reads as a market, not one booth cloned.

Five explorations over a shared stall idiom (two timber corner posts, a striped/
cloth awning, a counter, a back wall) — matching draw_kiosk's footprint
(half_w~22, posts to base_y-34, pagoda-family palette) — each carrying a
different COOKING APPARATUS with its own animated steam/smoke, and each tuned so
a day_cast working vendor (the grill-FANNER pose:fan, the soup-LADLER pose:ladle)
reads as working at it:

  1. BAMBOO-STEAMER stack — round dim-sum baskets on a small stove, domed lid,
     steam escaping the basket seams.
  2. SOUP CAULDRON / big wok — a wide dark cauldron of broth on a brick stove, a
     ladle resting in it, broth steam curling up. (the LADLER's stall)
  3. SKEWER GRILL — a long sheet-metal coal trough on legs, bamboo skewers laid
     across glowing coals, thin smoke + a few embers. (the FANNER's stall)
  4. STIR-FRY WOK — a round wok on a flared stove with a brief flame-lick under
     it (the wok-hei toss) and steam off the food.
  5. TEA / DRINKS stall — a tall brass tea-urn (long-spout kettle) steaming over
     a warmer, stacked cups, a hanging cloth sign — the non-fire stall, distinct
     in silhouette so the row isn't all stoves.

CONSTRAINTS mirrored from the shipped families:
- pure pygame.draw.* + Surface (SRCALPHA, BLEND_RGB_ADD ok), pygbag-safe.
  No numpy/gfxdraw/PIL.
- STEAM/SMOKE drift + rise over time (driven by `t`): each wisp is a few small
  translucent puffs whose y/alpha cycle with t — never a static blob.
- Day->night: STEAM pale/cool/translucent. Glowing COALS/embers/flame are warm
  but held under the promenade's NIGHT_GLOW_CAP=150 luma and must NOT out-pop the
  gold coin (the brightness yardstick on the composite).
- Muted shan-shui temple-market palette (terracotta / bamboo / charcoal / cloth
  awning), consistent with the shipped families and draw_kiosk.

Nothing here touches production game files; review-sheet generator only.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))


# ── shared colour helpers (lifted from game/foreground_props + promenade) ──────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _retint(col, night):
    """Cool toward the night ground band — matches promenade._retint_person and
    the kiosk's `_mix(col, (60,66,92), 0.3*night)` cooling idiom."""
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


NIGHT_GLOW_CAP = 150


def _cap150(col):
    """Hold a lit ember/flame/glow under the promenade's 150 luma ceiling without
    flattening hue — the contract that keeps the gold coin the brightest object."""
    y = _luma(col)
    if y <= NIGHT_GLOW_CAP:
        return col
    k = NIGHT_GLOW_CAP / y
    return (_clamp(col[0] * k), _clamp(col[1] * k), _clamp(col[2] * k))


# ── animated steam/smoke + warm-glow primitives ───────────────────────────────

def _wisp(surf, x, y0, t, *, n=3, rise=20, spread=3.0, speed=0.55, phase=0.0,
          color=(232, 232, 236), peak_a=70, r0=2, sway=2.4):
    """A rising column of `n` translucent puffs. Each puff cycles 0..1 in t: it
    starts small + faint at the source, fattens + rises + drifts sideways, then
    fades out near the top — so the column reads as DRIFTING steam, never a static
    blob. Cool/pale by default (steam); pass a warm colour + low alpha for thin
    smoke. Each puff is its own tiny SRCALPHA blit so alpha composites cleanly."""
    for i in range(n):
        ph = ((t * speed) + phase + i / n) % 1.0
        yy = y0 - ph * rise
        # drift sideways on a slow sine so the column curls rather than going
        # straight up — the read that says "rising heat", not a pipe.
        xx = x + math.sin(ph * math.pi * 1.6 + i * 1.3 + t * 0.7) * sway
        # fade in off the source, hold, fade out at the top.
        a = peak_a * math.sin(ph * math.pi)
        if a < 4:
            continue
        rr = int(r0 + ph * spread)
        d = rr * 2 + 2
        layer = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(layer, (*color, int(a)), (rr + 1, rr + 1), rr)
        pygame.draw.circle(layer, (*color, int(a * 0.5)), (rr + 1, rr + 1), max(1, rr - 1))
        surf.blit(layer, (int(xx) - rr - 1, int(yy) - rr - 1))


def _warm_glow(surf, cx, cy, *, radius, peak, color):
    """A small capped additive halo for coals/flame, summed onto the deck — held
    LOW + capped so even over the lit ember it stays under 150 luma and below the
    coin. Mirrors promenade._glow / sp._warm_glow."""
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


# ── shared stall SHELL — posts + awning + counter + back wall ──────────────────
#
# The common temple-market booth all five cooking apparatuses sit in, matched to
# draw_kiosk: two timber corner posts, a back-wall panel, a striped cloth awning
# (the "open" cue) and a timber counter. Returns the counter-top y so each stall
# can place its stove/cauldron/grill ON the counter line.

HALF_W = 22


def _stall_shell(surf, sx, base_y, night, *, awning=("terra", "cream"),
                 counter_h=15, post_top_off=34, roof=True, sign=None):
    half_w = HALF_W
    post_top = base_y - post_top_off

    post = _mix((92, 64, 40), (60, 66, 92), 0.30 * night)
    post_dk = _shade(post, -20)
    for px in (sx - half_w + 3, sx + half_w - 3):
        pygame.draw.rect(surf, post, (px - 1, post_top, 3, base_y - post_top))
        pygame.draw.line(surf, post_dk, (px + 1, post_top), (px + 1, base_y), 1)

    # back wall panel (so the stall reads enclosed, not a bare frame)
    wall = _mix((150, 132, 110), (150, 124, 96), 0.5)
    wall = _mix(wall, (56, 62, 88), 0.32 * night)
    pygame.draw.rect(surf, _shade(wall, -10),
                     (sx - half_w + 4, post_top + 2, (half_w - 4) * 2, 13))

    if roof:
        _flat_awning(surf, sx, post_top, half_w, night, awning)

    # counter / shop front
    counter = _mix((120, 84, 52), (60, 66, 92), 0.30 * night)
    counter_lt = _shade(counter, 16)
    cy = base_y - counter_h
    pygame.draw.rect(surf, counter, (sx - half_w + 1, cy, (half_w - 1) * 2, counter_h))
    pygame.draw.rect(surf, counter_lt, (sx - half_w + 1, cy, (half_w - 1) * 2, 2))
    pygame.draw.rect(surf, _shade(counter, -22),
                     (sx - half_w + 1, base_y - 4, (half_w - 1) * 2, 4))

    if sign:
        # a small hanging cloth sign-banner under the awning eave (a vertical
        # market banner — the temple-fair shop-cloth cue). Muted + capped.
        col = _cap150(_retint(sign, night))
        bx = sx - half_w + 6
        by = post_top + 1
        pygame.draw.rect(surf, col, (bx - 2, by, 5, 12))
        pygame.draw.rect(surf, _shade(col, -30), (bx - 2, by, 5, 12), 1)
        pygame.draw.line(surf, _shade(col, 24), (bx, by + 3), (bx, by + 9), 1)

    return cy


def _flat_awning(surf, sx, post_top, half_w, night, awning):
    """A striped cloth awning rolled out over the counter — a flat valance with a
    scalloped hem, two-tone. The cream stripe is pulled hard toward night so the
    unlit cloth never out-pops the festival lights / coin (draw_kiosk idiom)."""
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
    # a thin eave board the cloth hangs from
    pygame.draw.rect(surf, _mix((110, 80, 50), (60, 66, 92), 0.3 * night),
                     (sx - aw - 1, ay - 2, aw * 2 + 2, 2))
    for i, ax in enumerate(range(sx - aw, sx + aw, 6)):
        col = col_a if i % 2 == 0 else col_b
        pygame.draw.polygon(surf, col, [
            (ax, ay), (ax + 6, ay), (ax + 6, ay + 4), (ax + 3, ay + 6), (ax, ay + 4)])


# ════════════════════════════════════════════════════════════════════════════
# THE FIVE STALLS — each draws its apparatus ON the shell's counter line.
# Signature: (surf, sx, base_y, night, t). Authored feet/base on base_y.
# ════════════════════════════════════════════════════════════════════════════

def stall_steamer(surf, sx, base_y, night, t):
    """BAMBOO-STEAMER STACK — a little brazier stove with a tall stack of round
    woven dim-sum baskets and a domed lid; steam escapes the seams between every
    basket and puffs from the lid. The stack's stepped round silhouette is the
    read."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("terra", "cream"),
                      sign=(190, 150, 90))
    # small charcoal brazier the stack sits on
    stove = _retint((86, 70, 60), night)
    pygame.draw.rect(surf, stove, (sx - 10, cy - 6, 20, 6))
    pygame.draw.rect(surf, _shade(stove, -20), (sx - 10, cy - 6, 20, 6), 1)
    pygame.draw.line(surf, _shade(stove, 18), (sx - 9, cy - 5), (sx + 9, cy - 5), 1)
    # a faint warm vent slot so the stove reads as hot (capped, never a beacon)
    if night > 0.05:
        _warm_glow(surf, sx, cy - 3, radius=7, peak=46, color=(150, 96, 50))
    bamboo = _retint((188, 156, 96), night)
    bamboo_d = _shade(bamboo, -34)
    bamboo_hi = _shade(bamboo, 18)
    bx = sx - 11
    bw = 22
    by = cy - 6
    # four stacked baskets, each a shallow ellipse band; steam from each seam
    for i in range(4):
        band_y = by - 5 - i * 5
        rim = pygame.Rect(bx + 1, band_y, bw - 2, 6)
        pygame.draw.ellipse(surf, bamboo, rim)
        pygame.draw.ellipse(surf, bamboo_d, rim, 1)
        # woven hoop bands
        pygame.draw.line(surf, bamboo_hi, (rim.left + 1, band_y + 1),
                         (rim.right - 1, band_y + 1), 1)
        pygame.draw.line(surf, bamboo_d, (rim.left + 1, band_y + 4),
                         (rim.right - 1, band_y + 4), 1)
        # steam leaking from this seam — thin sideways-curling wisps
        _wisp(surf, sx - 5 + i * 3, band_y, t, n=2, rise=10, spread=2.0,
              speed=0.6, phase=i * 0.3, peak_a=46, r0=1, sway=2.0,
              color=_steam_col(night))
    # domed woven lid on top
    lid_y = by - 5 - 4 * 5
    pygame.draw.ellipse(surf, bamboo, (bx + 1, lid_y - 2, bw - 2, 7))
    pygame.draw.arc(surf, bamboo_hi, (bx + 3, lid_y - 5, bw - 6, 9),
                    math.radians(20), math.radians(160), 2)
    pygame.draw.circle(surf, bamboo_d, (sx, lid_y - 2), 1)
    # the big steam plume off the lid
    _wisp(surf, sx, lid_y - 2, t, n=4, rise=26, spread=3.4, speed=0.5,
          phase=0.1, peak_a=78, r0=2, sway=3.0, color=_steam_col(night))
    _wisp(surf, sx + 4, lid_y - 1, t, n=3, rise=20, spread=2.6, speed=0.55,
          phase=0.5, peak_a=58, r0=2, sway=2.6, color=_steam_col(night))


def stall_cauldron(surf, sx, base_y, night, t):
    """SOUP CAULDRON / big WOK — a wide dark cast-iron cauldron of broth on a
    rough brick stove, a ladle resting against the rim, broth steam curling up.
    The LADLER vendor (day_cast pose:ladle) reads as working this stall."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("indigo", "cream"),
                      sign=(168, 96, 80))
    # brick/clay stove block under the pot
    brick = _retint((150, 96, 70), night)
    pygame.draw.rect(surf, brick, (sx - 13, cy - 8, 26, 8))
    pygame.draw.rect(surf, _shade(brick, -22), (sx - 13, cy - 8, 26, 8), 1)
    for bxx in range(sx - 11, sx + 12, 7):     # brick courses
        pygame.draw.line(surf, _shade(brick, -16), (bxx, cy - 8), (bxx, cy), 1)
    pygame.draw.line(surf, _shade(brick, -16), (sx - 12, cy - 4), (sx + 12, cy - 4), 1)
    # firebox mouth — a low capped warm slot at the stove front
    if night > 0.05:
        _warm_glow(surf, sx, cy - 2, radius=8, peak=52, color=(150, 92, 46))
    pygame.draw.ellipse(surf, _cap150((128, 70, 36) if night > 0.05 else (70, 44, 30)),
                        (sx - 5, cy - 4, 10, 3))
    # the cauldron: a wide dark cast-iron belly with a thick rim
    pot = _retint((64, 60, 62), night)
    pot_d = _shade(pot, -22)
    pot_hi = _shade(pot, 22)
    py = cy - 8
    belly = pygame.Rect(sx - 16, py - 11, 32, 14)
    pygame.draw.ellipse(surf, pot, belly)
    pygame.draw.ellipse(surf, pot_d, belly, 1)
    pygame.draw.arc(surf, pot_hi, belly, math.radians(20), math.radians(80), 1)
    # broth surface inside the rim — a warm muted disc (not lit; just food colour)
    broth = _retint((150, 96, 58), night)
    rim = pygame.Rect(sx - 14, py - 12, 28, 7)
    pygame.draw.ellipse(surf, _shade(pot, -10), rim)
    pygame.draw.ellipse(surf, broth, rim.inflate(-3, -2))
    # a couple of bobbing ingredient flecks
    for k, ph in ((-4, 0.0), (5, 0.5), (1, 0.8)):
        fy = py - 9 + int(math.sin(t * 2.0 + ph * 6) * 0.6)
        pygame.draw.circle(surf, _retint((196, 150, 92), night), (sx + k, fy), 1)
    # a ladle resting against the rim (so the LADLER reads working it)
    ladle = _retint((150, 120, 70), night)
    pygame.draw.line(surf, ladle, (sx + 9, py - 11), (sx + 16, py - 19), 1)
    pygame.draw.circle(surf, _shade(ladle, 14), (sx + 16, py - 19), 1)
    # broth steam — broad, lazy curls off the surface
    _wisp(surf, sx - 4, py - 11, t, n=4, rise=26, spread=3.6, speed=0.42,
          phase=0.0, peak_a=74, r0=2, sway=3.4, color=_steam_col(night))
    _wisp(surf, sx + 5, py - 11, t, n=3, rise=22, spread=3.0, speed=0.5,
          phase=0.5, peak_a=58, r0=2, sway=3.0, color=_steam_col(night))


def stall_grill(surf, sx, base_y, night, t):
    """SKEWER GRILL — a long sheet-metal coal trough on slim legs over the
    counter, a row of bamboo skewers laid across the glowing coals, thin rising
    smoke, and a few drifting embers. The FANNER vendor (day_cast pose:fan) reads
    as working this stall. Coals/embers warm but capped under the coin."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("rust", "cream"),
                      sign=(176, 110, 70))
    # the long charcoal trough — a low sheet-metal box wider than the cauldron
    metal = _retint((78, 74, 78), night)
    metal_d = _shade(metal, -22)
    trough = pygame.Rect(sx - 17, cy - 9, 34, 7)
    pygame.draw.rect(surf, metal, trough)
    pygame.draw.rect(surf, metal_d, trough, 1)
    pygame.draw.line(surf, _shade(metal, 16), (trough.left + 1, trough.top + 1),
                     (trough.right - 1, trough.top + 1), 1)
    # short legs
    for lx in (sx - 15, sx + 14):
        pygame.draw.line(surf, metal_d, (lx, cy - 2), (lx, cy + 3), 1)
    # the bed of glowing coals — a strip of warm capped embers with a soft glow.
    # Started warm but held under 150 luma; coals pulse gently with t.
    glow_base = (146, 78, 34) if night > 0.05 else (120, 68, 34)
    if night > 0.05:
        _warm_glow(surf, sx, cy - 6, radius=13, peak=58, color=(150, 84, 40))
    for k in range(-15, 16, 3):
        pulse = 0.5 + 0.5 * math.sin(t * 3.0 + k * 0.7)
        col = _cap150(_mix(_shade(glow_base, -26), _shade(glow_base, 18), pulse))
        pygame.draw.circle(surf, col, (sx + k, cy - 6 + (k % 2)), 1)
    # bamboo skewers laid across the trough, slightly fanned — meat nubs on each
    skew = _retint((176, 150, 100), night)
    meat = _retint((150, 92, 70), night)
    for k in range(-13, 14, 4):
        sxp = sx + k
        pygame.draw.line(surf, skew, (sxp - 6, cy - 8), (sxp + 8, cy - 8), 1)
        for mx in (sxp - 3, sxp + 1, sxp + 5):
            pygame.draw.circle(surf, meat, (mx, cy - 9), 1)
    # thin smoke ribbons rising off the bed — fainter + warmer than steam, since
    # it's smoke from dripping fat, not steam.
    smoke = _smoke_col(night)
    _wisp(surf, sx - 6, cy - 9, t, n=3, rise=24, spread=2.6, speed=0.6,
          phase=0.0, peak_a=44, r0=1, sway=3.2, color=smoke)
    _wisp(surf, sx + 5, cy - 9, t, n=3, rise=20, spread=2.4, speed=0.7,
          phase=0.4, peak_a=38, r0=1, sway=3.0, color=smoke)
    # a couple of capped embers drifting up on the smoke
    for i in range(3):
        ph = (t * 0.8 + i * 0.4) % 1.0
        ex = sx - 4 + i * 5 + int(math.sin(ph * 6 + i) * 3)
        ey = cy - 10 - int(ph * 16)
        a = int(120 * (1.0 - ph))
        if a > 8:
            lay = pygame.Surface((2, 2), pygame.SRCALPHA)
            lay.fill((*_cap150((150, 90, 40)), a))
            surf.blit(lay, (ex, ey), special_flags=pygame.BLEND_RGB_ADD)


def stall_wok(surf, sx, base_y, night, t):
    """STIR-FRY WOK — a round black wok on a flared cast stove with a brief
    flame-lick under it (the wok-hei toss) and steam rolling off the food. The
    flame is warm but capped; the round wok + flared stove silhouette sets it
    apart from the cauldron's wide belly."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("jade", "cream"),
                      sign=(150, 120, 70))
    # flared cast-iron stove cylinder (narrower top, wide foot)
    stove = _retint((70, 64, 64), night)
    stove_d = _shade(stove, -20)
    pygame.draw.polygon(surf, stove, [
        (sx - 8, cy - 9), (sx + 8, cy - 9), (sx + 11, cy), (sx - 11, cy)])
    pygame.draw.polygon(surf, stove_d, [
        (sx - 8, cy - 9), (sx + 8, cy - 9), (sx + 11, cy), (sx - 11, cy)], 1)
    # the flame-lick licking up the side of the wok — capped warm, flickers with t
    flick = math.sin(t * 11.0) * 0.5 + math.sin(t * 7.3) * 0.5
    fh = int(4 + flick * 2)
    if night > 0.05:
        _warm_glow(surf, sx, cy - 9, radius=11, peak=56, color=(150, 88, 40))
    for fx, fhh, col in ((sx - 4, fh, (148, 78, 30)),
                         (sx + 3, fh + 1, (150, 92, 38)),
                         (sx, fh + 2, (150, 104, 46))):
        col = _cap150(col if night > 0.05 else _shade(col, -30))
        pygame.draw.polygon(surf, col, [
            (fx - 2, cy - 9), (fx + 2, cy - 9), (fx, cy - 9 - fhh)])
    # the round wok belly resting in the stove mouth
    wok = _retint((52, 50, 54), night)
    wok_hi = _shade(wok, 24)
    belly = pygame.Rect(sx - 14, cy - 16, 28, 12)
    pygame.draw.ellipse(surf, wok, belly)
    pygame.draw.ellipse(surf, _shade(wok, -22), belly, 1)
    pygame.draw.arc(surf, wok_hi, belly, math.radians(20), math.radians(90), 1)
    # rim + food mound (warm muted, not lit)
    rim = pygame.Rect(sx - 13, cy - 17, 26, 6)
    pygame.draw.ellipse(surf, _shade(wok, -8), rim)
    food = _retint((176, 138, 84), night)
    pygame.draw.ellipse(surf, food, (sx - 8, cy - 16, 16, 4))
    for k, ph in ((-5, 0.0), (3, 0.4), (6, 0.7)):
        pygame.draw.circle(surf, _retint((196, 100, 80), night),
                           (sx + k, cy - 15 + int(math.sin(t * 2 + ph * 6))), 1)
    # a long wok handle out the back-left
    pygame.draw.line(surf, _retint((110, 84, 56), night),
                     (sx - 13, cy - 13), (sx - 20, cy - 16), 2)
    # steam rolling off the toss
    _wisp(surf, sx, cy - 17, t, n=4, rise=24, spread=3.2, speed=0.5,
          phase=0.0, peak_a=70, r0=2, sway=3.4, color=_steam_col(night))
    _wisp(surf, sx - 5, cy - 16, t, n=3, rise=18, spread=2.4, speed=0.6,
          phase=0.5, peak_a=52, r0=1, sway=2.8, color=_steam_col(night))


def stall_tea(surf, sx, base_y, night, t):
    """TEA / DRINKS stall — the non-fire stall: a tall brass long-spout tea-urn
    (the iconic Chinese teahouse kettle) steaming over a small warmer, a stack of
    bowls/cups, and a hanging cloth sign. Its tall slim urn + arcing spout reads
    nothing like the squat stoves, so the market row isn't all fire."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("bamboo", "indigo"),
                      sign=(176, 96, 80))
    # a low warmer under the urn (small capped glow, not a stove blaze)
    if night > 0.05:
        _warm_glow(surf, sx - 6, cy - 3, radius=6, peak=40, color=(150, 92, 46))
    warmer = _retint((92, 76, 64), night)
    pygame.draw.rect(surf, warmer, (sx - 11, cy - 4, 12, 4))
    pygame.draw.rect(surf, _shade(warmer, -20), (sx - 11, cy - 4, 12, 4), 1)
    # the tall brass urn — a slim ovoid body, lid knob, and a long arcing spout
    brass = _retint((176, 142, 78), night)
    brass_d = _shade(brass, -34)
    brass_hi = _shade(brass, 26)
    ux = sx - 5
    body = pygame.Rect(ux - 6, cy - 22, 12, 18)
    pygame.draw.ellipse(surf, brass, body)
    pygame.draw.ellipse(surf, brass_d, body, 1)
    pygame.draw.line(surf, brass_hi, (ux - 2, cy - 20), (ux - 2, cy - 8), 1)
    # lid + knob
    pygame.draw.ellipse(surf, _shade(brass, -10), (ux - 6, cy - 24, 12, 5))
    pygame.draw.circle(surf, brass_hi, (ux, cy - 24), 1)
    # the long curved spout arcing up and out (the teahouse-kettle signature)
    pygame.draw.lines(surf, brass, False,
                      [(ux + 5, cy - 14), (ux + 11, cy - 18), (ux + 14, cy - 24),
                       (ux + 13, cy - 27)], 2)
    pygame.draw.circle(surf, brass_hi, (ux + 13, cy - 27), 1)
    # a side handle loop
    pygame.draw.arc(surf, brass_d, (ux - 9, cy - 18, 5, 9),
                    math.radians(60), math.radians(300), 1)
    # a small stack of upturned bowls/cups on the counter beside the urn
    cup = _retint((210, 200, 180), night)
    for k in range(3):
        pygame.draw.ellipse(surf, cup, (sx + 7, cy - 3 - k * 2, 8, 3))
        pygame.draw.ellipse(surf, _shade(cup, -28), (sx + 7, cy - 3 - k * 2, 8, 3), 1)
    # a thin teacup steaming on the counter too
    pygame.draw.ellipse(surf, _shade(cup, -14), (sx + 9, cy - 8, 5, 3))
    # steam: a fine plume off the SPOUT TIP + a wisp off the cup
    _wisp(surf, ux + 13, cy - 27, t, n=3, rise=20, spread=2.2, speed=0.55,
          phase=0.0, peak_a=56, r0=1, sway=2.6, color=_steam_col(night))
    _wisp(surf, sx + 11, cy - 9, t, n=2, rise=12, spread=1.6, speed=0.7,
          phase=0.4, peak_a=40, r0=1, sway=1.6, color=_steam_col(night))


def _steam_col(night):
    """Steam is pale + cool + translucent — by day a near-white blue-grey, cooled
    further toward the night sky at night so it never glows warmer than the deck."""
    return _mix((236, 238, 240), (150, 170, 200), 0.35 + 0.4 * night)


def _smoke_col(night):
    """Grill smoke is greyer + a touch warmer/darker than steam (it's not water
    vapour) — but still muted so it never reads as a hot beacon."""
    return _mix((200, 190, 180), (120, 120, 130), 0.4 + 0.3 * night)


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (matches the day-cast round_2 house style)
# ════════════════════════════════════════════════════════════════════════════

STALLS = [
    ("S1 bamboo steamer", stall_steamer,
     "shell: posts+back-wall+terra/cream awning+banner | stove: charcoal brazier (capped vent) | "
     "stack: 4 woven bamboo baskets + domed lid | STEAM: seam wisps + big lid plume (cool/pale)"),
    ("S2 soup cauldron", stall_cauldron,
     "shell: indigo/cream awning | stove: brick block + capped firebox mouth | "
     "pot: wide cast-iron belly, broth disc + flecks, resting LADLE | STEAM: broad lazy curls | (LADLER's stall)"),
    ("S3 skewer grill", stall_grill,
     "shell: rust/cream awning | grill: long sheet-metal coal trough on legs | coals: capped warm pulsing bed | "
     "skewers: bamboo + meat nubs fanned across | SMOKE: thin warm-grey ribbons + capped embers | (FANNER's stall)"),
    ("S4 stir-fry wok", stall_wok,
     "shell: jade/cream awning | stove: flared cast cylinder + capped flame-lick | "
     "wok: round black belly + food mound + long handle | STEAM: rolling toss plume"),
    ("S5 tea / drinks urn", stall_tea,
     "shell: bamboo/indigo awning | warmer: small capped glow | urn: tall brass body + lid knob + long arcing SPOUT + handle | "
     "cups: bowl stack | STEAM: fine spout + cup plume | (non-fire stall, tall silhouette)"),
]

W = 1100
PAD = 12
BG_DAY = (150, 140, 118)
BG_NIGHT = (40, 46, 70)


def _font(sz, bold=False):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _text(surf, s, x, y, sz=11, col=(228, 224, 214), bold=False):
    surf.blit(_font(sz, bold).render(s, True, col), (x, y))


def _gold_coin(surf, cx, cy, r=8):
    """The in-game gold-coin brightness yardstick — nothing on a stall (least of
    all a coal/flame) may out-pop this."""
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, (255, 232, 150))):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(9, True).render("$", True, (150, 100, 20)), (cx - 3, cy - 6))


def _stall_cell(parent, name, fn, note, x, y, w, h, night):
    """One annotated cell: a TRUE far-lane stall + a zoom inset, on a day or night
    deck, across 3 animation frames so the steam/smoke MOTION reads, with the
    part/palette note."""
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 18
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    # 3 animation frames at TRUE far-lane size so the wisp drift reads as motion
    frames_t = (0.0, 0.9, 1.8)
    fx0 = 16
    for i, ft in enumerate(frames_t):
        cx = fx0 + 22 + i * 50
        fn(cell, cx, base, night, ft)
        _text(cell, f"t{i}", cx - 6, base + 2, 8, _shade(bg, 60))
    _text(cell, "TRUE far-lane  (3 anim frames -> steam drift)", fx0, base + 9, 8, _shade(bg, 50))

    # zoom inset (~2.4x) framed at right, single still
    SCRATCH = 64
    nat = pygame.Surface((SCRATCH, SCRATCH), pygame.SRCALPHA)
    fn(nat, SCRATCH // 2, SCRATCH - 6, night, 0.6)
    z = 2.4
    zoom = pygame.transform.scale(nat, (int(SCRATCH * z), int(SCRATCH * z)))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 24
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)
    _text(cell, "2.4x zoom", zx, zy - 12, 8, _shade(bg, 60))

    # a coin yardstick in this cell so each stall's coals can be judged in place
    _gold_coin(cell, w - 16, h - 14, r=7)
    _text(cell, "coin", w - 30, h - 12, 7, _shade(bg, 55))

    _text(cell, name, 6, 4, 13, (240, 236, 226), bold=True)
    fnt = _font(9, False)
    words = note.split(" ")
    line = ""; yy = 22
    wrap_w = zx - 12
    for wd in words:
        test = (line + " " + wd).strip()
        if fnt.size(test)[0] > wrap_w:
            cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy)); yy += 11; line = wd
        else:
            line = test
    if line:
        cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy))

    parent.blit(cell, (x, y))
    pygame.draw.rect(parent, (70, 74, 90), (x, y, w, h), 1)


def render():
    title_h = 56
    # A. true-size band (day) — all five stalls in a row at far-lane size
    bandA_h = 30 + 132
    # B. per-stall detail cells — day then night, 2 cols
    cell_w = (W - PAD * 3) // 2
    cell_h = 150
    n_rows = (len(STALLS) + 1) // 2
    detailB_h = 30 + 2 * (24 + n_rows * (cell_h + 6))
    # C. on-street market-row composite (day + night) with coin yardstick
    strip_h = 110
    compC_h = 30 + 2 * (strip_h + 6)

    total_h = title_h + bandA_h + detailB_h + compC_h + PAD * 5
    sheet = pygame.Surface((W, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT PROMENADE — FOOD-MARKET STALL PROPS (round 1): 5 stalls", PAD, y, 17, (250, 246, 236), bold=True)
    y += 22
    _text(sheet, "Far-lane STALL STRUCTURES the cast stands AT (kiosk scale, draw_kiosk footprint). Animated steam/smoke (drift+rise w/ t); steam pale/cool; coals/flame WARM but capped <=150 luma, never out-popping the gold coin. Muted shan-shui palette.", PAD, y, 10, (188, 186, 200))
    y += title_h - 22

    # ── A. true-size band (day) ──
    _text(sheet, "A.  TRUE FAR-LANE SIZE — all five stalls on the day deck, with the gold-coin brightness reference", PAD, y, 13, (240, 220, 150), bold=True)
    y += 24
    band_h = 126
    row = pygame.Surface((W - PAD * 2, band_h))
    row.fill(BG_DAY)
    deck = _mix(BG_DAY, (0, 0, 0), 0.18)
    base = band_h - 22
    pygame.draw.rect(row, deck, (0, base, W - PAD * 2, 22))
    pygame.draw.line(row, _shade(BG_DAY, 26), (0, base), (W - PAD * 2, base), 1)
    _gold_coin(row, W - PAD * 2 - 22, base - 36)
    _text(row, "coin ref", W - PAD * 2 - 46, base + 2, 8, _shade(BG_DAY, 50))
    spacing = (W - PAD * 2 - 120) // len(STALLS)
    for i, (name, fn, _note) in enumerate(STALLS):
        cx = 70 + i * spacing
        fn(row, cx, base, 0.0, 0.6 + i * 0.3)
        _text(row, name.split(" ")[0], cx - 8, base + 2, 8, (70, 58, 46))
    sheet.blit(row, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, W - PAD * 2, band_h), 1)
    y += band_h + 8

    # ── B. per-stall detail (day rows then night rows) ──
    _text(sheet, "B.  PER-STALL — TRUE far-lane across 3 anim frames (steam drift) · 2.4x zoom · in-cell coin · part/palette note  (DAY then NIGHT)", PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT  (steam stays cool/pale; coals/flame capped <=150)" if is_night else "DAY",
              PAD, y, 11, (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 16
        for r in range(n_rows):
            for c in range(2):
                idx = r * 2 + c
                if idx >= len(STALLS):
                    break
                name, fn, note = STALLS[idx]
                cx = PAD + c * (cell_w + PAD)
                _stall_cell(sheet, name, fn, note, cx, y, cell_w, cell_h, night)
            y += cell_h + 6
        y += 8

    # ── C. on-street market-row composite ──
    _text(sheet, "C.  MARKET-ROW COMPOSITE — the five stalls in a market row with working cast (FANNER@grill, LADLER@cauldron) + gold-coin yardstick", PAD, y, 13, (240, 220, 150), bold=True)
    y += 22
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        bg = BG_NIGHT if is_night else BG_DAY
        strip = pygame.Surface((W - PAD * 2, strip_h))
        strip.fill(bg)
        deck = _mix(bg, (0, 0, 0), 0.2)
        base = strip_h - 16
        pygame.draw.rect(strip, deck, (0, base, W - PAD * 2, strip_h - base))
        pygame.draw.line(strip, _shade(bg, 24), (0, base), (W - PAD * 2, base), 1)
        spacing = (W - PAD * 2 - 90) // len(STALLS)
        for i, (name, fn, _note) in enumerate(STALLS):
            cx = 64 + i * spacing
            fn(strip, cx, base, night, 0.5 + i * 0.7)
            # a tiny cast figure standing at the counter of grill (FANNER) +
            # cauldron (LADLER) so those stalls read as worked-at.
            _mini_vendor(strip, cx + 26, base, night,
                         pose=("fan" if i == 2 else ("ladle" if i == 1 else "call")))
        _gold_coin(strip, W - PAD * 2 - 18, 20)
        _text(strip, "coin ref", W - PAD * 2 - 44, 32, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, W - PAD * 2, strip_h), 1)
        y += strip_h + 6

    out = "/home/user/skybit/docs/sidewalk_overhaul/food_stalls/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


def _mini_vendor(surf, sx, base_y, night, *, pose="call"):
    """A tiny stand-in vendor so the composite shows a worker AT the stall — a
    coarse echo of day_cast.draw_vendor's fan/ladle poses (not the production
    drawer; just enough to prove the stall affords the working pose)."""
    skin = _retint((222, 178, 132), night)
    shirt = _retint((150, 110, 78), night)
    shirt_d = _shade(shirt, -34)
    apron = _retint((204, 192, 172), night)
    hair = _retint((50, 40, 32), night)
    g = base_y
    body_y = g - 11
    pygame.draw.line(surf, shirt_d, (sx - 1, body_y + 7), (sx - 1, g), 2)
    pygame.draw.line(surf, shirt_d, (sx + 2, body_y + 7), (sx + 2, g), 2)
    pygame.draw.rect(surf, shirt, (sx - 3, body_y, 7, 8))
    pygame.draw.rect(surf, apron, (sx - 2, body_y + 3, 5, 5))
    if pose == "fan":
        fy = body_y + 2 + int(math.sin(0.6 * 6) * 1)
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 2), (sx - 7, fy), 2)
        pygame.draw.rect(surf, _retint((200, 180, 140), night), (sx - 9, fy - 1, 3, 4))
    elif pose == "ladle":
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 2), (sx - 6, body_y + 6), 2)
        pygame.draw.line(surf, shirt, (sx + 3, body_y + 2), (sx - 5, body_y + 6), 2)
    else:
        pygame.draw.line(surf, skin, (sx - 2, body_y + 2), (sx - 5, body_y), 2)
    pygame.draw.circle(surf, skin, (sx, body_y - 2), 3)
    pygame.draw.circle(surf, hair, (sx, body_y - 4), 3)


if __name__ == "__main__":
    render()
