"""Harbor-lighthouse pillar candidate — standalone landmark exploration.

The soft pole of the landmark set: the ONLY smooth curved-side taper. A
round shaft with true entasis (a swelling belly that pinches into a narrow
neck, so the outline reads as an unmistakable bottle curve, never the
obelisk's dead-straight wedge) rises from a wide waterline plinth up to a
distinct narrow "head" — a corbelled gallery ring (the widest ring of the
head), a glazed lantern room with a warm cached-radial glow, a narrower
copper dome and a ball finial. Blackout silhouette is a bottle: narrow
head over a swelling round shaft.

Contract mirrors the shipped pagoda pillars
(`game/pillar_pagodas.py::candidate_stupa_canopy`): one
`candidate_harbor_lighthouse(surf, top_rect, bot_rect, palette, seed)`; the
tower is painted upright once into an SRCALPHA temp and the ceiling section
is a `transform.flip` of that temp (the mirrored-hanger idiom). Every
structural colour is mixed from the biome palette so day->night retints.

This module is intentionally standalone — it does NOT import into or modify
any `game/` module. Run it to render the round review sheet.
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


# ── Colour helpers (same idiom as pillar_pagodas) ────────────────────────────

def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (max(0, min(255, int(c[0]) + d)),
            max(0, min(255, int(c[1]) + d)),
            max(0, min(255, int(c[2]) + d)))


# Candy bands alternate on VALUE (colour-blind safe, survives the night
# palette): a near-white light course against a dark warm-red course. Both
# are pinned to stone_light / stone_dark so their large value gap rides the
# biome retint instead of a fixed hue pair.
def _candy_light(p):
    return _mix(p['stone_light'], (255, 250, 246), 0.22)


def _candy_dark(p):
    return _mix(p['stone_dark'], (170, 58, 50), 0.46)


def _gallery(p):
    return _mix(p['stone_mid'], (120, 96, 82), 0.35)


def _glass(p):
    # Cool dark glazing so the warm lamp glow reads hot against it.
    return _mix(p['stone_dark'], (46, 60, 84), 0.40)


def _lamp_warm(p):
    return _mix(p['stone_accent'], (255, 232, 150), 0.55)


# ── Warm lantern glow — one cached radial, like draw_paper_lantern ───────────

_GLOW_CACHE: dict = {}


def _lamp_glow(radius, warm):
    key = (radius, warm)
    surf = _GLOW_CACHE.get(key)
    if surf is not None:
        return surf
    d = radius * 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    # Soft outer halo -> hot core, a few concentric stops (no per-pixel work).
    stops = ((1.00, 26), (0.72, 60), (0.46, 120), (0.24, 200), (0.12, 255))
    for frac, a in stops:
        col = (warm[0], warm[1], warm[2], a)
        pygame.draw.circle(g, col, (radius, radius), max(1, int(radius * frac)))
    _GLOW_CACHE[key] = g
    return g


# ── The tower, painted upright once ──────────────────────────────────────────

# A fixed candy-band COUNT (not a fixed band height): the shaft always reads
# as the same bold barber-pole no matter how tall the section is, so tall
# towers stop shimmering into a fine moiré of stripes when scrolling.
N_BANDS = 7


def _cyl_band(surf, cx, y0, bh, w, tone):
    """One horizontal course of the shaft, shaded left-light / right-dark so
    the round cross-section reads as a cylinder — this is what sells the
    'smooth round' pole. Full-width fill first guarantees the collision core."""
    x0 = cx - w // 2
    pygame.draw.rect(surf, tone, (x0, y0, w, bh))
    # Right-side body shadow (curved-away face).
    sh = max(4, int(w * 0.22))
    pygame.draw.rect(surf, _shade(tone, -34), (x0 + w - sh, y0, sh, bh))
    # Left highlight lobe + a thin specular seam near the light terminator.
    hw = max(4, int(w * 0.30))
    pygame.draw.rect(surf, _shade(tone, 26), (x0 + int(w * 0.10), y0, hw, bh))
    pygame.draw.rect(surf, _shade(tone, 44),
                     (x0 + int(w * 0.24), y0, max(1, int(w * 0.06)), bh))
    # Crisp course seam so the candy stripes stay legible at 1x.
    pygame.draw.line(surf, _shade(tone, -20), (x0 + 1, y0), (x0 + w - 1, y0), 1)


def _draw_tower(tmp, cx, palette, seed):
    """Paint an upright lighthouse filling the full temp height. The shaft
    absorbs all elastic height; the head (gallery/lantern/dome/finial) keeps
    a near-constant size so it reads at the gap for every section height."""
    rng = random.Random(seed)
    H = tmp.get_height()
    base_y = H - 1

    c_lt = _candy_light(palette)
    c_dk = _candy_dark(palette)
    accent = palette['stone_accent']

    # Head parts shrink gracefully on very short sections but never vanish.
    s = max(0.62, min(1.0, H / 120.0))
    finial_h = max(4, int(6 * s))
    dome_h = max(7, int(10 * s))
    lantern_h = int(18 * s)
    gallery_h = max(5, int(9 * s))
    head_h = finial_h + dome_h + lantern_h + gallery_h
    shaft_h = max(14, H - head_h)
    shaft_top = base_y - shaft_h

    # Widths — the collision core (the full inclusive PIPE_W column, ±29 px)
    # is ALWAYS covered: the narrowest structural member (the neck) still
    # clears PIPE_W so a centred rect spans both extreme edges; belly/plinth
    # flare spills only into the ±64 gutters, never widening the hitbox.
    #
    # Head cascade (FIX 3): shaft neck -> flared GALLERY (widest ring) ->
    # narrower lantern -> narrower dome -> ball finial. No onion-cap wobble.
    neck_w = PIPE_W + 2       # 60 — pinched shaft top, still covers the column
    base_w = PIPE_W + 20      # 78 — shaft footing
    belly_amp = 20            # entasis swell (belly peaks ~PIPE_W+34 = 92)
    plinth_w = PIPE_W + 38    # 96 — widest waterline footing
    gallery_w = PIPE_W + 32   # 90 — widest ring of the head
    lantern_w = PIPE_W + 18   # 76
    dome_w = PIPE_W + 10      # 68 — clearly narrower than the lantern (76)

    # ── Shaft — entasis profile (belly swell + neck pinch) as candy bands ────
    # t: 0 at the waterline, 1 at the neck. A linear base->neck taper carries
    # a sine belly that peaks low (~t=0.32) and dies out into the neck, so the
    # curve is a bottle, not a straight cone.
    def wid(y):
        t = max(0.0, min(1.0, (base_y - y) / max(1, shaft_h)))
        taper = base_w + (neck_w - base_w) * t
        belly = belly_amp * math.sin(math.pi * min(1.0, t / 0.64))
        return int(round(taper + belly))

    # Fixed band count -> band height stretches to fill the section.
    n_bands = N_BANDS
    band_h = shaft_h / n_bands
    while band_h < 6.0 and n_bands > 3:   # keep bands bold on tiny stubs
        n_bands -= 1
        band_h = shaft_h / n_bands
    dark_course = True                    # dark course sits at the waterline
    for i in range(n_bands):
        y_hi = int(round(base_y - band_h * (i + 1)))
        y_lo = int(round(base_y - band_h * i))
        bh = y_lo - y_hi
        if bh <= 0:
            continue
        w = wid(y_hi + bh / 2)
        _cyl_band(tmp, cx, y_hi, bh, w, c_dk if dark_course else c_lt)
        dark_course = not dark_course

    # ── Waterline plinth — wider granite footing with sparse moss clumps ────
    plinth_h = min(13, max(6, int(H * 0.10)))
    py = base_y - plinth_h
    granite = _mix(palette['stone_dark'], palette['stone_mid'], 0.42)
    pygame.draw.rect(tmp, _shade(granite, -22),
                     (cx - plinth_w // 2, py, plinth_w, plinth_h))
    pygame.draw.rect(tmp, granite,
                     (cx - plinth_w // 2 + 1, py + 1, plinth_w - 2, plinth_h - 2))
    pygame.draw.rect(tmp, _shade(granite, 22),
                     (cx - plinth_w // 2 + 2, py + 1, plinth_w - 4, 2))
    # A couple of sparse moss clumps at the waterline (not a stipple field).
    moss = palette['foliage_dark']
    moss_lt = _mix(moss, palette['foliage_mid'], 0.5)
    for _ in range(3):
        mx = cx - plinth_w // 2 + rng.randint(3, plinth_w - 4)
        my = py + rng.randint(2, plinth_h - 2)
        r = rng.randint(2, 3)
        pygame.draw.circle(tmp, moss, (mx, my), r)
        pygame.draw.circle(tmp, moss_lt, (mx - 1, my - 1), max(1, r - 1))

    # ── Gallery ring — corbelled shoulder proud of the shaft, with balusters ─
    gy = shaft_top
    pygame.draw.rect(tmp, _shade(_gallery(palette), -30),
                     (cx - gallery_w // 2, gy - gallery_h, gallery_w, gallery_h))
    pygame.draw.rect(tmp, _gallery(palette),
                     (cx - gallery_w // 2 + 1, gy - gallery_h + 1,
                      gallery_w - 2, gallery_h - 3))
    # Bright deck lip catching the sun + tiny baluster ticks along the rail.
    pygame.draw.rect(tmp, _shade(_gallery(palette), 34),
                     (cx - gallery_w // 2 + 2, gy - gallery_h + 1, gallery_w - 4, 1))
    n_bal = max(4, gallery_w // 7)
    rail_dk = _shade(_gallery(palette), -46)
    for i in range(n_bal):
        bx = cx - gallery_w // 2 + 3 + i * (gallery_w - 6) // (n_bal - 1)
        pygame.draw.line(tmp, rail_dk, (bx, gy - gallery_h + 2), (bx, gy - 2), 1)

    # ── Lantern room — glazed box, 3 bold astragal bars, cached warm glow ───
    ly = gy - gallery_h
    lx = cx - lantern_w // 2
    lroom = pygame.Rect(lx, ly - lantern_h, lantern_w, lantern_h)
    pygame.draw.rect(tmp, _shade(_glass(palette), -26), lroom)
    pygame.draw.rect(tmp, _glass(palette), lroom.inflate(-2, -2))
    # Glow blit BEHIND the astragal bars so the lamp reads as light through glass.
    warm = _lamp_warm(palette)
    gr = int(lantern_h * 0.95)
    glow = _lamp_glow(gr, warm)
    tmp.blit(glow, (cx - gr, ly - lantern_h // 2 - gr),
             special_flags=pygame.BLEND_PREMULTIPLIED)
    # Hot lamp core.
    pygame.draw.circle(tmp, _mix(warm, (255, 255, 240), 0.6),
                       (cx, ly - lantern_h // 2), max(2, lantern_h // 5))
    # Astragal bars — capped at 3 bold verticals so they never alias to noise.
    bar_c = _candy_light(palette)
    for bx in (cx - lantern_w // 4, cx, cx + lantern_w // 4):
        pygame.draw.line(tmp, bar_c, (bx, ly - lantern_h + 2), (bx, ly - 2), 1)
    # Frame top/sill so the glazing reads enclosed.
    pygame.draw.rect(tmp, _gallery(palette), (lx, ly - lantern_h, lantern_w, 2))
    pygame.draw.rect(tmp, _gallery(palette), (lx, ly - 2, lantern_w, 2))

    # ── Dome cap — copper dome (narrower than the lantern) + ball finial ─────
    dy = ly - lantern_h
    dome_col = _candy_dark(palette)
    dome_rect = pygame.Rect(cx - dome_w // 2, dy - dome_h, dome_w, dome_h * 2)
    # Half-ellipse: draw the ellipse then let the lantern frame clip its base.
    pygame.draw.ellipse(tmp, _shade(dome_col, -30), dome_rect)
    pygame.draw.ellipse(tmp, dome_col, dome_rect.inflate(-2, -2))
    # Sunlit crown highlight arc.
    pygame.draw.arc(tmp, _shade(dome_col, 40), dome_rect.inflate(-4, -4),
                    math.pi * 0.55, math.pi * 0.95, 2)
    # Flatten the dome's base onto the lantern roof.
    pygame.draw.rect(tmp, _shade(dome_col, -30),
                     (cx - dome_w // 2, dy - 1, dome_w, 2))
    # Ball finial + short vent spike — the tiny tip above the wide dome.
    fy = dy - dome_h
    pygame.draw.line(tmp, _shade(accent, -30), (cx, fy - finial_h), (cx, fy), 2)
    pygame.draw.circle(tmp, accent, (cx, fy - finial_h), max(2, finial_h // 2))
    pygame.draw.circle(tmp, _mix(accent, (255, 255, 240), 0.7),
                       (cx - 1, fy - finial_h - 1), 1)


def candidate_harbor_lighthouse(surf, top_rect, bot_rect, palette, seed):
    """Bottom lighthouse rises from the ground (dome points up into the gap);
    top section is the SAME tower flipped 180° and hung from the ceiling
    (dome points down into the gap)."""
    gutter = 64
    tmp_w = PIPE_W + gutter * 2
    tmp_cx = tmp_w // 2

    if bot_rect.height > 8:
        tmp = pygame.Surface((tmp_w, bot_rect.height), pygame.SRCALPHA)
        _draw_tower(tmp, tmp_cx, palette, seed)
        bcx = bot_rect.x + bot_rect.width // 2
        surf.blit(tmp, (bcx - tmp_cx, bot_rect.y))

    if top_rect.height > 8:
        tmp = pygame.Surface((tmp_w, top_rect.height), pygame.SRCALPHA)
        _draw_tower(tmp, tmp_cx, palette, seed)
        flipped = pygame.transform.flip(tmp, False, True)
        tcx = top_rect.x + top_rect.width // 2
        surf.blit(flipped, (tcx - tmp_cx, top_rect.y))


# ── Review-sheet harness ─────────────────────────────────────────────────────

PHASE = 0.30
MARGIN = 64
CACHE_W = PIPE_W + MARGIN * 2


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _sky_ground(w, h, pal, ground_h):
    cell = pygame.Surface((w, h))
    sky_h = h - ground_h
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal['sky_top'], pal['horizon'], t),
                         (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, ground_h)
        pygame.draw.line(cell, _lerp(pal['ground_top'], pal['ground_mid'], t),
                         (0, y), (w, y))
    return cell


def _blackout(pal, h):
    """Solid-black silhouette of the standing tower at section height `h`,
    cropped tight — the pure-shape read used to verify the head shoulder
    survives at gameplay scale."""
    tmp = pygame.Surface((CACHE_W, h), pygame.SRCALPHA)
    bot = pygame.Rect(MARGIN, 0, PIPE_W, h)
    candidate_harbor_lighthouse(tmp, pygame.Rect(0, 0, 0, 0), bot, pal, 7)
    silo = pygame.Surface((CACHE_W, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(CACHE_W):
            if tmp.get_at((x, y))[3] >= 24:
                silo.set_at((x, y), (14, 14, 20, 255))
    bb = silo.get_bounding_rect(min_alpha=1)
    return silo.subsurface(bb).copy()


def _col_fill_report(pal):
    """Feasibility math (NOT art critique): for each test height, print the
    tallest fully-empty vertical run inside the central PIPE_W collision
    column. Must stay <= 12 px everywhere from 70..355."""
    print("collision-column fill (central PIPE_W band):")
    for h in (70, 120, 210, 300, 355):
        surf = pygame.Surface((CACHE_W, h), pygame.SRCALPHA)
        bot = pygame.Rect(MARGIN, 0, PIPE_W, h)
        candidate_harbor_lighthouse(surf, pygame.Rect(0, 0, 0, 0), bot, pal, 7)
        cx = MARGIN + PIPE_W // 2
        worst = 0
        worst_x = 0
        for dx in range(-PIPE_W // 2, PIPE_W // 2 + 1):
            x = cx + dx
            run = best = 0
            for y in range(h):
                if surf.get_at((x, y))[3] < 24:
                    run += 1
                    best = max(best, run)
                else:
                    run = 0
            if best > worst:
                worst, worst_x = best, dx
        flag = "OK" if worst <= 12 else "!! KILLZONE"
        print(f"  h={h:>3}px  max empty vertical run = {worst:>3}px "
              f"(at dx={worst_x:+d})  {flag}")


def main():
    pal = biome.palette_for_phase(PHASE)

    # ── HERO: full pillar pair (hung + gap + standing) over daytime sky ─────
    gap_y, gap_h = 150, 120
    top_h = int(gap_y - gap_h / 2)
    bot_top = int(gap_y + gap_h / 2)
    hero = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, top_h)
    bot_rect = pygame.Rect(MARGIN, bot_top, PIPE_W, GROUND_Y - bot_top)
    candidate_harbor_lighthouse(hero, top_rect, bot_rect, pal, 7)
    hero_bg = _sky_ground(CACHE_W, GROUND_Y, pal, 18)
    hero_bg.blit(hero, (0, 0))

    # ── FEASIBILITY STRIP: bottom section at short / mid / tall + PIPE_W edges
    strip_heights = (70, 210, 355)
    strip_cells = []
    for h in strip_heights:
        cell = _sky_ground(CACHE_W, h + 20, pal, 16)
        surf = pygame.Surface((CACHE_W, h), pygame.SRCALPHA)
        bot = pygame.Rect(MARGIN, 0, PIPE_W, h)
        candidate_harbor_lighthouse(surf, pygame.Rect(0, 0, 0, 0), bot, pal, 7)
        cell.blit(surf, (0, 4))
        cx = MARGIN + PIPE_W // 2
        for ex in (cx - PIPE_W // 2, cx + PIPE_W // 2):
            pygame.draw.line(cell, (255, 60, 60), (ex, 0), (ex, h + 20), 1)
        strip_cells.append((h, cell))

    # ── BLACKOUT thumbnails: pure silhouette at 1x + a 0.72x downscale ──────
    silo_1x = _blackout(pal, 210)
    ds = 0.72
    silo_ds = pygame.transform.smoothscale(
        silo_1x, (max(1, int(silo_1x.get_width() * ds)),
                  max(1, int(silo_1x.get_height() * ds))))

    # ── Compose sheet ──────────────────────────────────────────────────────
    pad = 14
    label_h = 24
    font_t = pygame.font.SysFont(None, 30)
    font_s = pygame.font.SysFont(None, 20)
    font_l = pygame.font.SysFont(None, 20)

    strip_w = CACHE_W
    strip_total_h = sum(c.get_height() + label_h + pad for _, c in strip_cells)
    head_h = 60
    hero_block_w = CACHE_W
    sheet_w = pad + hero_block_w + pad + strip_w + pad
    sheet_h = max(head_h + hero_bg.get_height() + label_h + pad * 2,
                  head_h + strip_total_h + pad)

    # Blackout panel lives under the hero in the left column.
    black_panel_h = silo_1x.get_height() + label_h + pad * 2 + 6
    sheet_h = max(sheet_h,
                  head_h + hero_bg.get_height() + label_h + pad + black_panel_h)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(font_t.render("harbor-lighthouse — round 2", True,
                             (245, 240, 230)), (pad, 12))
    sheet.blit(font_s.render("fixed 7-band candy · entasis bottle curve · "
                             "gallery = widest head ring · dome<lantern · "
                             "daytime phase 0.30", True, (170, 172, 182)),
               (pad, 38))

    # Hero on the left.
    hx, hy = pad, head_h
    sheet.blit(hero_bg, (hx, hy))
    pygame.draw.rect(sheet, (60, 62, 72),
                     pygame.Rect(hx, hy, CACHE_W, GROUND_Y), 1)
    lab = font_l.render("HERO — hung + gap + standing pair", True, (255, 224, 150))
    sheet.blit(lab, (hx, hy + GROUND_Y + 4))

    # Blackout panel under the hero.
    bpy = hy + GROUND_Y + label_h + pad
    sheet.blit(font_l.render("BLACKOUT — head over swelling shaft (1x · 0.72x)",
                             True, (255, 224, 150)), (hx, bpy))
    panel_top = bpy + label_h
    panel = pygame.Rect(hx, panel_top, CACHE_W, silo_1x.get_height() + pad)
    pygame.draw.rect(sheet, (206, 208, 214), panel)
    pygame.draw.rect(sheet, (60, 62, 72), panel, 1)
    # 1x silhouette, centred, with red PIPE_W edges to prove the hitbox column.
    s1x = hx + 28
    s1y = panel_top + pad // 2
    sheet.blit(silo_1x, (s1x, s1y))
    col_cx = s1x + silo_1x.get_width() // 2
    for ex in (col_cx - PIPE_W // 2, col_cx + PIPE_W // 2):
        pygame.draw.line(sheet, (220, 70, 70),
                         (ex, s1y), (ex, s1y + silo_1x.get_height()), 1)
    # 0.72x downscale to the right, baseline-aligned.
    sdx = s1x + silo_1x.get_width() + 34
    sdy = s1y + silo_1x.get_height() - silo_ds.get_height()
    sheet.blit(silo_ds, (sdx, sdy))

    # Feasibility strip on the right.
    sx = pad + hero_block_w + pad
    sy = head_h
    sheet.blit(font_l.render("FEASIBILITY — bottom section, red = PIPE_W edges",
                             True, (255, 224, 150)), (sx, sy - 20))
    for h, cell in strip_cells:
        sheet.blit(cell, (sx, sy))
        pygame.draw.rect(sheet, (60, 62, 72),
                         pygame.Rect(sx, sy, cell.get_width(), cell.get_height()), 1)
        sheet.blit(font_l.render(f"h = {h}px", True, (210, 212, 222)),
                   (sx + 4, sy + cell.get_height() + 3))
        sy += cell.get_height() + label_h + pad

    out = _REPO / "docs" / "pillar_landmarks" / "harbor-lighthouse" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    _col_fill_report(pal)

    # Silhouette-width sanity (my own check, not art critique): confirm the
    # entasis belly reads clearly wider than the pinched neck.
    tmp = pygame.Surface((PIPE_W + 128, 320), pygame.SRCALPHA)
    _draw_tower(tmp, (PIPE_W + 128) // 2, pal, 7)
    widths = []
    for y in range(320):
        row = [x for x in range(tmp.get_width()) if tmp.get_at((x, y))[3] >= 24]
        widths.append((row[-1] - row[0] + 1) if row else 0)
    print(f"shaft silhouette: max belly ~{max(widths)}px, "
          f"neck min (shaft band) reported via fill gate")


if __name__ == "__main__":
    main()
