"""oriental_pearl — Oriental Pearl Tower, Shanghai (standalone hi-fi candidate).

The row's most sci-fi silhouette: rose-glass pearls skewered on a thin steel
mast that splays into three slanting tripod legs at the base. Circles on a
stick — a blackout tell nothing else in the roster shares. Only TWO large
spheres carry the read (fat lower entertainment sphere + a slightly smaller
upper sphere), with a tiny Space Capsule bead near the crown; the bare mast
GAP between the two big spheres is the tell, so it is protected rather than
filled with a third lump.

Standalone review module — imports the pagoda fidelity helpers so material,
palette and day/night retint match `game/pillar_pagodas.py` exactly. Not wired
into the live game; the design loop selects a winner first.
"""
from __future__ import annotations

import math
import random

import pygame

from game.pillar_pagodas import (
    _mix, _shade, _gradient_rect, _aa_polyline, _lit_niche,
    _draw_plinth_mist, _is_dark_sky, _is_warming_sky,
    _cap_lit_for_dark_sky, _cap_dark_for_dark_sky,
    _bronze, _gold_bright, _lotus_pink, _column_grey, _plaster,
)
from game.pillar_variants import draw_grass_bed
from game.draw import draw_side_shrub


# ── Material triads ─────────────────────────────────────────────────────────
#
# Every colour is mixed against the live palette so the biome's day→night
# retint sweeps through; no raw RGB leaks into the body. Highlights use
# `_shade` (a value nudge on a palette-anchored hue) rather than a hard white
# so the specular retints with the sky rather than punching a fixed colour.

def _steel_triad(palette):
    """Cool steel-grey concrete mast/legs, biased off `_column_grey` so it
    reads as bare structural concrete — deliberately far from the rose glass
    so the Shanghai spike never trades against a cool-steel tower at a glance."""
    mid = _column_grey(palette)
    lit = _cap_lit_for_dark_sky(_shade(_mix(mid, palette['stone_light'], 0.55), 26),
                                palette)
    shadow = _cap_dark_for_dark_sky(_shade(mid, -48), palette)
    return lit, mid, shadow


def _pearl_triad(palette):
    """The tower's famous laminated-red glass — a saturated rose anchored in
    `stone_accent` (so the biome's warm-highlight band sweeps it day→night)
    and grounded partly in `_lotus_pink`, held well clear of the steel so the
    two China spikes never trade. Day reads hot magenta-rose, night a lit cool
    magenta. This hue is the concept's signature.

    The day anchor is pushed hotter and more saturated than the night one: the
    warm daylight band drifts the glass toward sandstone-peach, so day needs a
    deeper magenta target to stay unmistakably rose glass; night already reads
    as lit cool magenta and is left on the softer anchor."""
    if _is_dark_sky(palette):
        rose = _mix(palette['stone_accent'], (216, 98, 120), 0.58)
    else:
        rose = _mix(palette['stone_accent'], (226, 58, 104), 0.70)
    mid = _mix(rose, _lotus_pink(palette), 0.28)
    lit = _shade(mid, 54)
    shadow = _cap_dark_for_dark_sky(_shade(_mix(mid, palette['stone_dark'], 0.40), -14),
                                    palette)
    return lit, mid, shadow


# ── Pearl (convex radial-gradient glass sphere) ─────────────────────────────

def _draw_pearl(surf, cx, cy, r, palette):
    """A convex glass sphere: concentric shells whose centre drifts up-left so
    the lit peak sits toward the light and a shadow crescent falls bottom-right,
    then an additive specular hotspot + an AA rim. This is the pearl's whole
    volume read at PIPE_W scale."""
    if r < 3:
        pygame.draw.circle(surf, _pearl_triad(palette)[1], (cx, cy), max(1, r))
        return
    lit, mid, shadow = _pearl_triad(palette)
    # Terminator is baked by shifting inner (brighter) shells toward the light
    # so the outermost shadow shell stays exposed on the bottom-right rim.
    for i in range(r, 0, -1):
        t = i / r
        col = _mix(lit, shadow, t ** 0.82)
        off = int((r - i) * 0.34)
        pygame.draw.circle(surf, col, (cx - off, cy - off), i)
    # AA rim so the sphere edge doesn't stair-step against the sky.
    rim = _shade(shadow, -12)
    pts = [(cx + r * math.cos(a), cy + r * math.sin(a))
           for a in (k / 22 * 2 * math.pi for k in range(22))]
    _aa_polyline(surf, rim, pts, closed=True)
    # Additive glass hotspot toward the light corner.
    hs = max(2, int(r * 0.32))
    hx, hy = cx - int(r * 0.40), cy - int(r * 0.42)
    hot = _shade(lit, 55)
    glow = pygame.Surface((hs * 2, hs * 2), pygame.SRCALPHA)
    for j in range(hs, 0, -1):
        a = int(210 * (1 - j / hs))
        pygame.draw.circle(glow, (*hot, a), (hs, hs), j)
    surf.blit(glow, (hx - hs, hy - hs), special_flags=pygame.BLEND_RGBA_ADD)


def _pearl_halo(surf, cx, cy, r, palette):
    """Additive magenta bloom behind a pearl — gated on dark sky so the tower
    reads as a lit glass beacon at night and a quiet solid by day. Drawn BEFORE
    the pearl fill so only the outer falloff peeks past the rim."""
    if not (_is_dark_sky(palette) or _is_warming_sky(palette)):
        return
    strength = 1.0 if _is_dark_sky(palette) else 0.5
    glow_col = _mix(_lotus_pink(palette), palette['horizon'], 0.45)
    hr = int(r * 1.85)
    g = pygame.Surface((hr * 2, hr * 2), pygame.SRCALPHA)
    for ring, a in ((1.0, 22), (0.72, 44), (0.46, 78)):
        pygame.draw.circle(g, (*glow_col, int(a * strength)),
                           (hr, hr), int(hr * ring))
    surf.blit(g, (cx - hr, cy - hr), special_flags=pygame.BLEND_RGBA_ADD)


def _collar(surf, cx, cy, w, palette):
    """Bronze structural collar where the mast threads through a pearl pole —
    a short lit/shadow gradient band with a gold glint on its top lip."""
    if w < 6:
        return
    br = _bronze(palette)
    rect = pygame.Rect(cx - w // 2, cy - 2, w, 4)
    _gradient_rect(surf, rect, _shade(br, 28), br, _shade(br, -32))
    pygame.draw.line(surf, _gold_bright(palette),
                     (cx - w // 2, cy - 2), (cx + w // 2 - 1, cy - 2), 1)


# ── Whole tower (drawn UPRIGHT; the top pillar flips this) ──────────────────

def _draw_tower(surf, cx, base_y, top_y, body_w, palette):
    """One upright Oriental Pearl silhouette filling [top_y, base_y]. Layout is
    height-adaptive: a tall rect gets both big pearls + capsule bead + needle;
    a short rect sheds the capsule, then the upper pearl, so the mast never
    squashes into a lumpy sausage. The mast is one continuous steel column so
    no horizontal band between the beads is ever empty."""
    total_h = base_y - top_y
    if total_h < 30:
        return
    s_lit, s_mid, s_shadow = _steel_triad(palette)

    # Base-anchored substructure (tripod + plinth grow off the bottom).
    plinth_h = int(min(12, max(4, total_h * 0.045)))
    leg_h = int(min(58, max(14, total_h * 0.17)))
    plinth_top = base_y - plinth_h
    leg_top = plinth_top - leg_h                              # mast foot / apex

    # A DELIBERATELY THIN steel mast — emphatically narrower than the pearls, so
    # the spheres read as discrete beads threaded on a stick rather than bulges
    # on a fat vase. The bare thinness IS the tell; a thin centred column still
    # paints a pixel in every row, so the fill gate is unaffected.
    mast_w = max(8, min(10, int(body_w * 0.16)))

    # Bead sizes. Radii scale with height for short sections (so two pearls fit)
    # but cap on width, so at PIPE_W the lower pearl is near a full-width sphere.
    lower_r = max(9, int(min(body_w * 0.46, total_h * 0.145)))
    upper_r = max(7, int(lower_r * 0.72))
    capsule_r = max(4, int(upper_r * 0.5))
    gap_h = int(min(28, max(10, total_h * 0.09)))            # bare-mast pearl tell
    umast_h = int(min(18, max(6, total_h * 0.05)))           # air isolating capsule

    # Antenna needle, CAPPED to ~18–20% of the tower so the crown is pearls, not
    # a broadcast spike. Recessed 3px from the rect edge to buy mirror air.
    ant_tip = top_y + 3
    needle_h = int(min(total_h * 0.19, capsule_r * 6))
    needle_h = min(needle_h, max(4, (leg_top - ant_tip) // 2))

    # Beads cluster near the crown under the short needle; the long thin shaft
    # below fills the collision column down to the tripod (faithful + fills).
    # Pick the richest bead config whose lowest pearl still clears the apex.
    min_stick = 2

    def _stack_h(with_upper, with_capsule):
        h = needle_h + 2 * lower_r
        if with_capsule:
            h += 2 * capsule_r + umast_h
        if with_upper:
            h += 2 * upper_r + gap_h
        return h

    def _fits(with_upper, with_capsule):
        return ant_tip + _stack_h(with_upper, with_capsule) <= leg_top - min_stick

    show_upper = _fits(True, False)
    show_capsule = show_upper and _fits(True, True)
    if not _fits(False, False):
        # Extremely short section: shrink the sole pearl to sit above the apex.
        avail = (leg_top - min_stick) - (ant_tip + needle_h)
        lower_r = max(6, min(lower_r, avail // 2))

    # Lay the crown out top-down from the recessed tip.
    y = ant_tip + needle_h                                    # top of highest bead
    capsule_cy = upper_cy = None
    if show_capsule:
        capsule_top = y
        capsule_cy = capsule_top + capsule_r
        y = capsule_cy + capsule_r + umast_h
    if show_upper:
        upper_top = y
        upper_cy = upper_top + upper_r
        y = upper_cy + upper_r + gap_h
    lower_top = y
    lower_cy = lower_top + lower_r

    # The mast climbs behind the crown up to the highest bead centre; the pearl
    # above covers the last stretch to the needle, so no row is left open.
    if show_capsule:
        mast_top = capsule_cy
    elif show_upper:
        mast_top = upper_cy
    else:
        mast_top = lower_cy

    # 1 — night backlight wedge lifting the silhouette off the mountains.
    _draw_plinth_mist(surf, cx, base_y, int(body_w * 1.5), palette)

    # 2 — dim recessed tripod core so the leg triangle is NEVER an open hole.
    back = _cap_dark_for_dark_sky(_shade(palette['stone_dark'], -8), palette)
    pygame.draw.rect(surf, back,
                     (cx - int(body_w * 0.44), leg_top,
                      int(body_w * 0.88), plinth_top - leg_top))

    # 3 — the continuous steel mast (horizontal gradient = a round column).
    mast_rect = pygame.Rect(cx - mast_w // 2, mast_top,
                            mast_w, leg_top - mast_top)
    _gradient_rect(surf, mast_rect, s_lit, s_mid, s_shadow)
    # Hard specular streak on the sun side.
    pygame.draw.line(surf, _shade(s_lit, 34),
                     (cx - mast_w // 4, mast_top),
                     (cx - mast_w // 4, leg_top), 1)
    _aa_polyline(surf, s_shadow,
                 [(cx + mast_w // 2 - 1, mast_top),
                  (cx + mast_w // 2 - 1, leg_top)])

    # 4 — three slanting tripod legs as LIT relief struts over the dim core.
    foot_span = int(body_w * 0.42)
    for sgn in (-1, 0, 1):
        foot_x = cx + sgn * foot_span
        top_half = mast_w // 2
        leg = [(cx - top_half, leg_top - leg_h // 3),
               (cx + top_half, leg_top - leg_h // 3),
               (foot_x + 5, plinth_top),
               (foot_x - 5, plinth_top)]
        pygame.draw.polygon(surf, s_mid, leg)
        # Lit inboard edge + shadow outboard edge give the strut round volume.
        _aa_polyline(surf, _shade(s_lit, 22),
                     [(cx - top_half, leg_top - leg_h // 3), (foot_x - 5, plinth_top)])
        _aa_polyline(surf, s_shadow,
                     [(cx + top_half, leg_top - leg_h // 3), (foot_x + 5, plinth_top)])

    # 5 — three-layer plinth (widening down) grounding the tripod feet.
    for i, (dw, dv) in enumerate(((0.98, 18), (1.14, -2), (1.30, -26))):
        pw = int(body_w * dw)
        ph = max(2, plinth_h - i * 2)
        py = plinth_top + i * 2
        col = _cap_lit_for_dark_sky(_shade(palette['stone_mid'], dv), palette)
        pygame.draw.rect(surf, col, (cx - pw // 2, py, pw, ph))
    pygame.draw.line(surf, s_lit,
                     (cx - int(body_w * 0.49), plinth_top),
                     (cx + int(body_w * 0.49), plinth_top), 1)

    # 6 — lower entertainment sphere (the fat pearl) with pole collars.
    _collar(surf, cx, lower_cy + lower_r - 1, mast_w + 6, palette)
    _pearl_halo(surf, cx, lower_cy, lower_r, palette)
    _draw_pearl(surf, cx, lower_cy, lower_r, palette)
    _collar(surf, cx, lower_cy - lower_r + 1, mast_w + 2, palette)
    # A ring of lit observation-deck windows belts the fat pearl at night.
    if _is_dark_sky(palette) and lower_r >= 14:
        for k in range(-2, 3):
            _lit_niche(surf, cx + k * (lower_r // 3), lower_cy + lower_r // 2,
                       2, 2, palette)

    # 7 — upper sphere (slightly smaller) + capsule bead, height permitting.
    if show_upper:
        _collar(surf, cx, upper_cy + upper_r - 1, mast_w + 2, palette)
        _pearl_halo(surf, cx, upper_cy, upper_r, palette)
        _draw_pearl(surf, cx, upper_cy, upper_r, palette)
        _collar(surf, cx, upper_cy - upper_r + 1, mast_w - 2, palette)
    if show_capsule:
        _pearl_halo(surf, cx, capsule_cy, capsule_r, palette)
        _draw_pearl(surf, cx, capsule_cy, capsule_r, palette)

    # 8 — short antenna needle (capped) + a tight night beacon.
    ant_base = capsule_top if show_capsule else (
        upper_top if show_upper else lower_top)
    if ant_base - ant_tip > 4:
        pygame.draw.polygon(surf, s_mid,
                            [(cx - 2, ant_base), (cx + 2, ant_base),
                             (cx + 1, ant_tip), (cx - 1, ant_tip)])
        pygame.draw.line(surf, s_lit, (cx - 1, ant_base), (cx, ant_tip), 1)
        if _is_dark_sky(palette):
            # A tight beacon: its additive falloff is clamped small so the
            # mirrored top-pillar tip can't re-close the gap across the recess.
            beac = _mix(palette['stone_accent'], _gold_bright(palette), 0.5)
            halo = pygame.Surface((10, 10), pygame.SRCALPHA)
            for ring, a in ((1.0, 34), (0.55, 84), (0.28, 150)):
                pygame.draw.circle(halo, (*beac, a), (5, 5), max(1, int(5 * ring)))
            surf.blit(halo, (cx - 5, ant_tip - 5),
                      special_flags=pygame.BLEND_RGBA_ADD)


def _draw_oriental_pearl(surf, top_rect, bot_rect, palette, seed):
    rng = random.Random(seed)
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 30:
        _draw_tower(surf, bcx, bot_rect.bottom, bot_rect.y,
                    bot_rect.width, palette)
        draw_grass_bed(surf, bcx, bot_rect.bottom - 1,
                       bot_rect.width + 6, 14, palette, seed=seed)
        draw_side_shrub(surf, bot_rect.x - 4, bot_rect.bottom - 1, palette, scale=1.0)
        draw_side_shrub(surf, bot_rect.right + 4, bot_rect.bottom - 1, palette, scale=0.9)

    if top_rect.height > 30:
        # STRUCTURAL MIRROR: draw the tower UPRIGHT into a temp sized to exactly
        # top_rect.height, then vertical-flip. The bead-string is near-symmetric
        # so it flips clean — the antenna hangs into the gap, the podium meets
        # the ceiling — with no killzone band against the gap edge.
        w = top_rect.width + 20
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_tower(tmp, w // 2, top_rect.height, 0, top_rect.width, palette)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (tcx - w // 2, top_rect.y))


def candidate_oriental_pearl(surf, top_rect, bot_rect, palette, seed):
    """Public pillar-pair entry matching the live contract."""
    _draw_oriental_pearl(surf, top_rect, bot_rect, palette, seed)


# ── Headless review harness ─────────────────────────────────────────────────

def _sky_bg(w, h, palette):
    bg = pygame.Surface((w, h))
    top, mid, bot = palette['sky_top'], palette['sky_mid'], palette['sky_bot']
    for y in range(h):
        t = y / max(1, h - 1)
        col = _mix(top, mid, t * 2) if t < 0.5 else _mix(mid, bot, (t - 0.5) * 2)
        pygame.draw.line(bg, col, (0, y), (w, y))
    return bg


def _max_empty_band(surf, rect):
    """Longest run of fully-empty rows inside the collision rect (px)."""
    worst = run = 0
    for y in range(rect.y, rect.bottom):
        filled = any(surf.get_at((x, y))[3] > 0
                     for x in range(rect.x, rect.right))
        run = 0 if filled else run + 1
        worst = max(worst, run)
    return worst


def _render_sheet():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))
    from game.biome import palette_for_phase

    PIPE_W = 58
    day = palette_for_phase(0.30)
    night = palette_for_phase(0.85)

    pad = 16
    hero_w, hero_h = 210, 470
    strip_w, strip_h = 470, 330
    black_w = 150
    label_h = 30
    sheet_w = hero_w * 2 + pad * 3
    sheet_w = max(sheet_w, strip_w + black_w + pad * 3)
    sheet_h = label_h + hero_h + pad + label_h + strip_h + pad * 2

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 34))
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    def label(text, x, y, col=(235, 235, 240)):
        sheet.blit(font.render(text, True, col), (x, y))

    sheet.blit(font.render(
        "oriental_pearl — Oriental Pearl Tower, Shanghai  ·  round_2",
        True, (255, 210, 150)), (pad, 6))

    # Hero pillar pairs (top pillar hangs from ceiling; bottom from floor).
    def hero(pal, title, x0):
        panel = _sky_bg(hero_w, hero_h, pal)
        cx = hero_w // 2
        gap_top, gap_bot = 150, 300
        top_rect = pygame.Rect(cx - PIPE_W // 2, 0, PIPE_W, gap_top)
        bot_rect = pygame.Rect(cx - PIPE_W // 2, gap_bot, PIPE_W, hero_h - gap_bot)
        candidate_oriental_pearl(panel, top_rect, bot_rect, pal, seed=7)
        y0 = label_h
        sheet.blit(panel, (x0, y0))
        pygame.draw.rect(sheet, (70, 74, 84), (x0, y0, hero_w, hero_h), 1)
        label(title, x0, y0 - 22)

    hero(day, "DAY  (phase 0.30)", pad)
    hero(night, "NIGHT (phase 0.85) — pearl + beacon glow", pad * 2 + hero_w)

    # Feasibility strip: three pillars at x = 70 / 210 / 355 + fill readout.
    sy = label_h + hero_h + pad + label_h
    strip = _sky_bg(strip_w, strip_h, day)
    fills = []
    for i, cx in enumerate((70, 210, 355)):
        bot_rect = pygame.Rect(cx - PIPE_W // 2, 40, PIPE_W, strip_h - 40)
        top_rect = pygame.Rect(cx - PIPE_W // 2, 0, PIPE_W, 0)
        candidate_oriental_pearl(strip, top_rect, bot_rect, day, seed=3 + i)
        band = _max_empty_band(strip, bot_rect)
        fills.append((cx, band))
        pygame.draw.rect(strip, (90, 200, 120), bot_rect, 1)
    sheet.blit(strip, (pad, sy))
    pygame.draw.rect(sheet, (70, 74, 84), (pad, sy, strip_w, strip_h), 1)
    label("feasibility 70/210/355 (green = collision col)", pad, sy - 22)
    for cx, band in fills:
        sheet.blit(small.render(f"x{cx}: max empty band {band}px",
                                True, (200, 255, 200)),
                   (pad + 4, sy + strip_h - 46 + fills.index((cx, band)) * 14))

    # 58-px blackout — the bead-string tell as a pure silhouette.
    bx = pad * 2 + strip_w
    blk = pygame.Surface((black_w, strip_h))
    blk.fill((240, 240, 240))
    mask = pygame.Surface((PIPE_W, strip_h), pygame.SRCALPHA)
    bot_rect = pygame.Rect(0, 34, PIPE_W, strip_h - 34)
    top_rect = pygame.Rect(0, 0, PIPE_W, 0)
    candidate_oriental_pearl(mask, top_rect, bot_rect, day, seed=7)
    sil = pygame.Surface((PIPE_W, strip_h), pygame.SRCALPHA)
    for y in range(strip_h):
        for x in range(PIPE_W):
            if mask.get_at((x, y))[3] > 0:
                sil.set_at((x, y), (18, 18, 22, 255))
    blk.blit(sil, ((black_w - PIPE_W) // 2, 0))
    sheet.blit(blk, (bx, sy))
    pygame.draw.rect(sheet, (70, 74, 84), (bx, sy, black_w, strip_h), 1)
    label("58px blackout", bx, sy - 22, (30, 30, 30))
    sheet.blit(small.render("bead-string tell", True, (60, 60, 60)),
               (bx + 6, sy + strip_h - 20))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    return out, sheet.get_size(), fills, day, night


if __name__ == "__main__":
    path, size, fills, _d, _n = _render_sheet()
    print(f"saved: {path}")
    print(f"dims:  {size[0]}x{size[1]}")
    for cx, band in fills:
        print(f"fill x{cx}: max empty band = {band}px  (gate <=12)")
