"""Standalone candidate: `smock-windmill` — a squat, steeply-battered drainage
mill throwing a 4-blade sail cross into the side gutters.

This is a colocated EXPLORATION module for the pillar-landmark design loop. It
follows the shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect,
palette, seed)`, upright `draw_one` reused for both rects, the top section a
vertical flip of a temp surface) but does NOT import into or modify any game/
module — it only borrows read-only colour + AA helpers so the exploration reads
like the real game.

Silhouette identity: the ONLY radial/diagonal tower in the set. A fat, ground-
heavy weatherboarded cone whose four bold sails fan OUTWARD into the ±64 px
gutters as a St-Andrew's X, sprung from the cap by a short centred windshaft
and capped by a small boat-cap + finial at the gap.

Column-fill contract: the collision column (central PIPE_W band) is filled by
the BODY, never the sails. The battered cone is full-column-wide from the base
up to ~three-quarters height, then the boat-cap + finial keep the centreline
continuously occupied all the way to the gap rim — so no empty vertical run
opens across the column at any section height 70–355 px. The sail-X is pure
gutter ornament laid over that solid core.

Run:  python docs/pillar_landmarks/smock-windmill/render.py
Out:  docs/pillar_landmarks/smock-windmill/round_1.png
"""
from __future__ import annotations

import math
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pygame

from game.config import GROUND_Y, PIPE_W
from game import biome
from game.pillar_pagodas import (
    _mix,
    _shade,
    _is_dark_sky,
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _aa_polyline,
)
from game.pillar_variants import draw_grass_bed, draw_flower_bed


# ── Windmill colour roles (all biome-derived so day→night retints) ───────────
#
# The body is the tarred, matte weatherboard of a drainage mill — grounded in
# stone_dark so it reads near-black-brown by day and doesn't collapse into the
# sky at night (floored via _cap_dark_for_dark_sky where it shades deepest).
# The sail canvas is the bright stone_light so the X punches against the dark
# cone. The boat-cap + finial + hub carry the warm stone_accent focal.


def _tar(c, amt):
    # Pull a warm sandstone hue toward its own neutral grey so the body reads
    # as matte TARRED weatherboard, not milk-chocolate clay. Desaturating
    # (not just darkening) widens the value gap to the bright sand sails and
    # keeps the blackout silhouette honest.
    g = (c[0] + c[1] + c[2]) / 3.0
    return (int(c[0] + (g - c[0]) * amt),
            int(c[1] + (g - c[1]) * amt),
            int(c[2] + (g - c[2]) * amt))


def _body_lit(pal):
    # One notch darker + desaturated vs a plain stone_mid lift so the sunlit
    # tar face still reads dim, not creamy.
    return _cap_lit_for_dark_sky(
        _tar(_shade(_mix(pal['stone_dark'], pal['stone_mid'], 0.60), -6), 0.28),
        pal)


def _body_mid(pal):
    return _tar(_shade(pal['stone_dark'], -14), 0.28)


def _body_shadow(pal):
    # Floor raised to 66 (from 52) so the night shadow face keeps ~14 value
    # over a deep sky and the cone's shaded edge no longer muddies into it.
    return _cap_dark_for_dark_sky(_shade(pal['stone_dark'], -42), pal, floor=66)


def _shadow_rim(pal):
    # A faint cool-lit rim laid down the shadow-side outline at night so the
    # silhouette holds its edge against a dark sky (day palettes never hit it).
    return _mix(pal['stone_mid'], pal['stone_light'], 0.55)


def _canvas(pal):
    return pal['stone_light']


def _spar(pal):
    return _shade(pal['stone_dark'], -30)


def _cap_col(pal):
    # Painted boat-cap — lighter than the tarred body so the crown reads as a
    # separate roof at the gap rim.
    return _mix(pal['stone_light'], pal['stone_accent'], 0.45)


def _cap_shadow(pal):
    return _shade(pal['stone_mid'], -18)


def _accent(pal):
    return _mix(pal['stone_accent'], (240, 196, 90), 0.55)


# ── Body: scan-lined battered trapezoid ──────────────────────────────────────

def _battered_body(surf, cx, top_y, base_y, hw_top, hw_base, palette):
    """Paint the steeply-battered cone as horizontal scan-lines, each a short
    left-lit → mid → right-shadow ramp, so the flat trapezoid reads as a
    rounded 3-D tarred cylinder at PIPE_W=58 (same volume trick as the pagoda
    `_gradient_rect`, adapted to a per-row sloping width). WASM-safe: uses only
    pygame.draw 1-px vertical lines, no set_at / surfarray."""
    lit, mid, shadow = _body_lit(palette), _body_mid(palette), _body_shadow(palette)
    dark_sky = _is_dark_sky(palette)
    rim = _shadow_rim(palette)
    h = base_y - top_y
    if h < 2:
        return
    for i in range(h):
        y = top_y + i
        t = i / (h - 1)                       # 0 at cap shoulder, 1 at base
        hw = int(round(hw_top + (hw_base - hw_top) * t))
        if hw < 1:
            continue
        # Lit half: cx-hw → cx, ramp lit→mid.  Shadow half: cx → cx+hw, mid→shadow.
        for j in range(hw):
            u = j / max(1, hw)
            pygame.draw.line(surf, _mix(lit, mid, u),
                             (cx - hw + j, y), (cx - hw + j, y), 1)
            pygame.draw.line(surf, _mix(mid, shadow, u),
                             (cx + j, y), (cx + j, y), 1)
        # Night edge-keep: a 1-px cool rim on the shadow-side outline so the
        # cone doesn't dissolve into the dark sky where its value nears sky_top.
        if dark_sky:
            pygame.draw.line(surf, rim, (cx + hw - 1, y), (cx + hw - 1, y), 1)


def _hoop(surf, cx, y, hw, palette):
    """A single string-course hoop banding the cone — sparse by design (2–3
    total) so the tarred body never stipples into noise against a busy sky."""
    if hw < 4:
        return
    pygame.draw.line(surf, _shade(palette['stone_dark'], -30),
                     (cx - hw, y + 1), (cx + hw, y + 1), 1)
    pygame.draw.line(surf, _mix(palette['stone_mid'], palette['stone_light'], 0.4),
                     (cx - hw, y), (cx + hw, y), 1)


# ── Cap + finial + fantail ───────────────────────────────────────────────────

def _boat_cap(surf, cx, shoulder_y, top_y, hw_cap, palette):
    """Ogee boat-cap from the body shoulder up to the gap tip. Presents a solid
    roofed edge (curb ring + rounded cap) and keeps the centreline continuously
    filled from shoulder to finial so the collision column never breaks."""
    cap_h = shoulder_y - top_y
    if cap_h < 4:
        pygame.draw.line(surf, _cap_col(palette),
                         (cx - hw_cap, shoulder_y), (cx + hw_cap, shoulder_y), 2)
        return
    # Curb ring the cap rotates on — a touch wider than the shoulder.
    pygame.draw.rect(surf, _cap_shadow(palette),
                     (cx - hw_cap - 1, shoulder_y - 2, (hw_cap + 1) * 2, 3))
    pygame.draw.line(surf, _mix(palette['stone_light'], palette['stone_accent'], 0.5),
                     (cx - hw_cap - 1, shoulder_y - 2), (cx + hw_cap, shoulder_y - 2), 1)
    # Ogee profile: bulge out low, sweep in to a rounded tip.
    steps = 10
    left = []
    for k in range(steps + 1):
        tt = k / steps                        # 0 shoulder, 1 tip
        y = shoulder_y - 2 - tt * (cap_h - 2)
        hw = hw_cap * (1.0 - tt ** 1.5) + (1.0 - tt) * tt * hw_cap * 0.35
        left.append((cx - hw, y))
    right = [(cx + (cx - x), y) for (x, y) in reversed(left)]
    poly = left + right
    pygame.draw.polygon(surf, _cap_shadow(palette), poly)
    inner = [(x + 1 if x < cx else x - 1, y) for (x, y) in poly]
    pygame.draw.polygon(surf, _cap_col(palette), inner)
    _aa_polyline(surf, _shade(_cap_shadow(palette), -20), poly, closed=True)
    # Sun-catching highlight down the lit flank of the cap.
    hl = _mix(palette['stone_light'], palette['stone_accent'], 0.7)
    pygame.draw.line(surf, hl, left[1], left[len(left) // 2], 1)


def _windshaft(surf, cx, shoulder_y, hub_y, palette):
    """A short, CENTRED windshaft spar dropping from the cap curb down to the
    sail hub. This is what springs the sail-X off the cap (not mid-body) and
    reads unmistakably as a mill — and being on the centreline it survives the
    vertical mirror symmetrically (the round-1 side-fantail did not). Replaces
    the sub-pixel fantail filigree the round-1 sheet aliased into a smudge."""
    if hub_y <= shoulder_y:
        return
    pygame.draw.line(surf, _spar(palette), (cx, shoulder_y - 1), (cx, hub_y), 3)
    # A single lit tick down the shaft's sunlit cheek so it reads as round wood.
    pygame.draw.line(surf, _mix(palette['stone_mid'], palette['stone_light'], 0.4),
                     (cx - 1, shoulder_y), (cx - 1, hub_y - 1), 1)


# ── The sail cross ───────────────────────────────────────────────────────────

def _sail_arm(surf, hx, hy, dirx, diry, length, palette):
    """One bold sail arm: a tapered canvas quad with a dark leading spar and
    2–3 rung ticks. Deliberately chunky (not filigree) so the X reads as four
    confident bars at PIPE_W=58 rather than aliasing into noise."""
    tx, ty = hx + dirx * length, hy + diry * length
    px, py = -diry, dirx                       # unit perpendicular
    w0, w1 = 4.2, 1.6                          # wide at hub, taper to tip
    quad = [(hx + px * w0, hy + py * w0),
            (tx + px * w1, ty + py * w1),
            (tx - px * w1, ty - py * w1),
            (hx - px * w0, hy - py * w0)]
    quad = [(int(x), int(y)) for (x, y) in quad]
    pygame.draw.polygon(surf, _canvas(palette), quad)
    _aa_polyline(surf, _spar(palette), quad, closed=True)
    # Rung ticks across the arm (the sail bars).
    rung = _shade(palette['stone_dark'], -18)
    for f in (0.32, 0.58, 0.82):
        mx, my = hx + dirx * length * f, hy + diry * length * f
        wf = w0 + (w1 - w0) * f
        pygame.draw.line(surf, rung,
                         (int(mx + px * wf), int(my + py * wf)),
                         (int(mx - px * wf), int(my - py * wf)), 1)
    # Leading-edge spar down the arm centre.
    pygame.draw.line(surf, _spar(palette), (int(hx), int(hy)), (int(tx), int(ty)), 1)


def _sail_cross(surf, cx, hub_y, arm_len, palette):
    """Four arms fanned as a St-Andrew's X. The angle is shallow (leaning
    toward horizontal) so the arms spill sideways into the ±64 px gutters while
    their VERTICAL reach stays short — the upper tips stop below the gap rim so
    a mirrored pair never bridges or clutters the flyable channel."""
    a = math.radians(34.0)                     # 34° above horizontal — flat-ish X
    ca, sa = math.cos(a), math.sin(a)
    for dirx, diry in ((ca, -sa), (-ca, -sa), (ca, sa), (-ca, sa)):
        _sail_arm(surf, cx, hub_y, dirx, diry, arm_len, palette)
    # Central hub canister + poll-end.
    pygame.draw.circle(surf, _spar(palette), (cx, hub_y), 5)
    pygame.draw.circle(surf, _accent(palette), (cx, hub_y), 3)
    pygame.draw.circle(surf, _mix(palette['stone_light'], palette['stone_accent'], 0.8),
                       (cx - 1, hub_y - 1), 1)


# ── The candidate ────────────────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, apron=True):
    """One upright smock-mill silhouette filling [top_y, base_y]. Height-
    adaptive: short sections get a stubbier cap, fewer hoops and a smaller
    sail-X, but the battered body always fills the collision column."""
    total_h = base_y - top_y
    if total_h < 20:
        return

    hw_base = int(body_w * 0.74)               # base spills into the gutters
    hw_cap = max(6, int(body_w * 0.42))        # shoulder stays ≥ ~48 px wide
    cap_h = min(int(total_h * 0.16), 24)
    shoulder_y = top_y + cap_h

    # Plinth / stone apron ring under the cone.
    plinth_h = 5 if total_h > 60 else 3
    plinth_w = hw_base * 2 + 8
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -12),
                     (cx - plinth_w // 2, base_y - plinth_h, plinth_w, plinth_h))
    pygame.draw.line(surf, palette['stone_light'],
                     (cx - plinth_w // 2, base_y - plinth_h),
                     (cx + plinth_w // 2, base_y - plinth_h), 1)

    body_base_y = base_y - plinth_h
    _battered_body(surf, cx, shoulder_y, body_base_y, hw_cap, hw_base, palette)

    # Sparse hoop string-courses, count keyed off body height so tall cones get
    # a couple and short ones stay clean.
    body_h = body_base_y - shoulder_y
    n_hoops = max(0, min(3, body_h // 40))
    for k in range(n_hoops):
        ht = (k + 1) / (n_hoops + 1)
        y = int(shoulder_y + body_h * (1 - ht))
        hw = int(round(hw_cap + (hw_base - hw_cap) * (1 - ht)))
        _hoop(surf, cx, y, hw, palette)

    # A single tarred plank door low on the sunlit face — one bold shape, not a
    # field of seams.
    if body_h > 26 and hw_base > 12:
        dw = max(5, hw_base // 4)
        dh = min(14, body_h // 3)
        dx = cx - hw_base // 2
        dy = body_base_y - dh
        pygame.draw.rect(surf, _shade(palette['stone_dark'], -40), (dx, dy, dw, dh))
        pygame.draw.line(surf, _mix(palette['stone_mid'], palette['stone_light'], 0.5),
                         (dx, dy), (dx, dy + dh - 1), 1)

    # Cap crowns the shoulder and holds the centreline to the gap rim.
    _boat_cap(surf, cx, shoulder_y, top_y, hw_cap, palette)
    # Finial ball at the very tip.
    pygame.draw.circle(surf, _accent(palette), (cx, top_y + 1), 2)

    # Sail cross — hub mounted just under the cap, arms fanning into the gutters.
    # TIP_CLEAR is the vertical clearance from the section tip to the upper arm
    # tips; raised from 3→6 px so that, once the arm spar's anti-aliasing and
    # the tip quad's perpendicular overshoot are added, the MIRRORED upper tips
    # still sit clear of the gap rim instead of visually kissing it.
    TIP_CLEAR = 8
    arm_len = int(min(total_h * 0.44, body_w * 1.28))
    arm_len = max(14, arm_len)
    hub_y = int(top_y + math.sin(math.radians(34.0)) * arm_len + TIP_CLEAR)
    # Keep the hub on the upper body / cap shoulder so the X reads mounted, not
    # floating; clamp so the upper arm tips never cross above the gap rim.
    hub_y = max(hub_y, shoulder_y - 1)
    # Windshaft springs the X off the cap so it reads as a mill, not a turnstile.
    _windshaft(surf, cx, shoulder_y, hub_y, palette)
    _sail_cross(surf, cx, hub_y, arm_len, palette)

    if apron:
        draw_grass_bed(surf, cx, base_y - 1, plinth_w + 4, 12, palette, seed=seed)
        draw_flower_bed(surf, cx, base_y - 2, plinth_w - 6, 5, seed=seed)


def candidate_smock_windmill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 24:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, apron=True)

    if top_rect.height > 24:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, blit hanging from the ceiling — the sail-hub end then
        # points at the gap exactly like the bottom section (an X either way up).
        w = surf.get_width()
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_one(tmp, tcx, top_rect.height, 0,
                  top_rect.width, palette, seed, apron=False)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, top_rect.y))


# ── Review harness ───────────────────────────────────────────────────────────

MARGIN = 64
CACHE_W = PIPE_W + MARGIN * 2
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85
SEED = 13

# The mirrored-pair geometry the round-2 hero must prove: a real flyable gap
# with a top-hung section AND a bottom-rising section, so the two sail-Xs
# flanking the channel are auditable in the same frame.
GAP_Y, GAP_H = 205, 150
TOP_H = int(GAP_Y - GAP_H / 2)          # top section runs 0..TOP_H
BOT_TOP = int(GAP_Y + GAP_H / 2)        # bottom section runs BOT_TOP..GROUND_Y
CROP_TOP, CROP_BOT = 18, 486            # hero window framing both Xs + the gap


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _sky_ground(w, h, pal, ground_h):
    cell = pygame.Surface((w, h))
    sky_h = h - ground_h
    for y in range(sky_h):
        t = y / max(1, sky_h - 1)
        pygame.draw.line(cell, _lerp(pal['sky_top'], pal['horizon'], t), (0, y), (w, y))
    for y in range(sky_h, h):
        t = (y - sky_h) / max(1, h - sky_h)
        pygame.draw.line(cell, _lerp(pal['ground_top'], pal['ground_mid'], t),
                         (0, y), (w, y))
    return cell


def _pair_surf(pal):
    """The mirrored pair on its own transparent surface (for compositing AND
    for measuring the true mirrored-tip clearance)."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, TOP_H)
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    candidate_smock_windmill(surf, top_rect, bot_rect, pal, SEED)
    return surf


def _render_pair(pal, label_str):
    surf = _pair_surf(pal)
    cell = _sky_ground(CACHE_W, GROUND_Y, pal, GROUND_Y - GROUND_Y + 60)
    cell.blit(surf, (0, 0))
    # Faint channel guides at the two gap rims so the reviewer can read exactly
    # how far each mirrored sail-tip clears the flyable lane.
    guide = (255, 90, 90)
    for rim in (TOP_H, BOT_TOP):
        for x in range(0, CACHE_W, 8):
            pygame.draw.line(cell, guide, (x, rim), (x + 4, rim), 1)
    win = cell.subsurface(pygame.Rect(0, CROP_TOP, CACHE_W, CROP_BOT - CROP_TOP)).copy()
    return win


def _measure_clearance(pal):
    """Highest sail pixel of each mirrored section vs its gap rim, measured only
    in the gutter columns (where the sails live), in px."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    gutter = lambda x: abs(x - cx) > PIPE_W // 2 + 2
    # Top (hung) section: sails point DOWN toward the gap → lowest gutter pixel.
    top_low = -1
    for y in range(0, TOP_H + 8):
        for x in range(CACHE_W):
            if gutter(x) and surf.get_at((x, y))[3] > 50:
                top_low = y
                break
    # Bottom (rising) section: sails point UP → highest gutter pixel.
    bot_high = GROUND_Y
    for y in range(BOT_TOP - 8, GROUND_Y):
        hit = False
        for x in range(CACHE_W):
            if gutter(x) and surf.get_at((x, y))[3] > 50:
                hit = True
                break
        if hit:
            bot_high = y
            break
    return TOP_H - top_low, bot_high - BOT_TOP


def _measure_fill(pal, section_h):
    """Max vertical run (px) of rows with ZERO fill inside the PIPE_W collision
    column, for a bottom-only section of the given height."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_smock_windmill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                             bot_rect, pal, SEED)
    cx = MARGIN + PIPE_W // 2
    x0, x1 = cx - PIPE_W // 2, cx + PIPE_W // 2
    run = worst = 0
    for y in range(GROUND_Y - section_h, GROUND_Y):
        filled = any(surf.get_at((x, y))[3] > 50 for x in range(x0, x1 + 1))
        run = 0 if filled else run + 1
        worst = max(worst, run)
    return worst


def _render_feas(pal, section_h):
    head = 16
    cell_h = section_h + head + 10
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_smock_windmill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                             bot_rect, pal, SEED)
    cell = _sky_ground(CACHE_W, cell_h, pal, 10)
    crop_top = GROUND_Y - section_h - head
    cell.blit(surf, (0, 0), pygame.Rect(0, crop_top, CACHE_W, cell_h))
    cx = MARGIN + PIPE_W // 2
    for ex in (cx - PIPE_W // 2, cx + PIPE_W // 2):
        pygame.draw.line(cell, (255, 60, 60), (ex, 0), (ex, cell_h), 1)
    return cell, cell_h


def _render_blackout(pal, section_h=230):
    """Pure-silhouette read at the true PIPE_W scale — does the radiating shape
    still say 'mill' with all interior detail stripped?"""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_smock_windmill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                             bot_rect, pal, SEED)
    crop_top = GROUND_Y - section_h - 12
    crop = surf.subsurface(pygame.Rect(0, crop_top, CACHE_W, section_h + 12)).copy()
    mask = pygame.mask.from_surface(crop, 60)
    return mask.to_surface(setcolor=(18, 18, 22, 255),
                           unsetcolor=(232, 232, 236, 255))


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    day = biome.palette_for_phase(PHASE_DAY)
    night = biome.palette_for_phase(PHASE_NIGHT)

    pair_day = _render_pair(day, "DAY")
    pair_night = _render_pair(night, "NIGHT")
    cl_day = _measure_clearance(day)
    cl_night = _measure_clearance(night)

    heights = [70, 210, 355]
    feas = [_render_feas(day, h) for h in heights]
    fills = {h: _measure_fill(day, h) for h in heights}
    blackout = _render_blackout(day)

    pad = 14
    label_h = 22
    title_h = 60
    pw, ph = pair_day.get_width(), pair_day.get_height()

    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    label = pygame.font.SysFont(None, 19)

    # Left block: the two mirrored pairs side by side + blackout beneath.
    left_w = pad + pw + pad + pw + pad
    feas_w = max(c.get_width() for c, _ in feas)
    right_w = feas_w + pad * 2
    sheet_w = left_w + right_w

    bo_w, bo_h = blackout.get_width(), blackout.get_height()
    left_h = title_h + ph + label_h + pad + bo_h + label_h + pad
    feas_col_h = title_h + sum(ch + label_h + pad for _, ch in feas) + 24
    sheet_h = max(left_h, feas_col_h) + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 25, 30))

    sheet.blit(title.render("smock-windmill — round 2", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("tarred battered cone + cap-sprung sail-X  ·  mirrored "
                          "pair with true gap, day + night", True,
                          (170, 172, 182)), (pad, 40))

    # Two hero pairs.
    for i, (pair, name, cl) in enumerate((
            (pair_day, f"DAY  PHASE={PHASE_DAY}", cl_day),
            (pair_night, f"NIGHT  PHASE={PHASE_NIGHT}", cl_night))):
        hx = pad + i * (pw + pad)
        hy = title_h
        sheet.blit(pair, (hx, hy))
        pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, pw, ph), 1)
        lab = label.render(name, True, (255, 224, 150))
        sheet.blit(lab, (hx + (pw - lab.get_width()) // 2, hy + ph + 3))
        cl2 = sub.render(f"tip clear: top {cl[0]}px  bot {cl[1]}px", True,
                         (200, 202, 212))
        sheet.blit(cl2, (hx + (pw - cl2.get_width()) // 2, hy + ph + 3 + 18))

    # Blackout silhouette under the pairs.
    bx = pad
    by = title_h + ph + label_h + pad + 14
    sheet.blit(blackout, (bx, by))
    pygame.draw.rect(sheet, (60, 62, 72), (bx, by, bo_w, bo_h), 1)
    lab = label.render("BLACKOUT — 58px silhouette read", True, (255, 224, 150))
    sheet.blit(lab, (bx, by + bo_h + 3))

    # Feasibility column (right).
    fx = left_w + pad
    fy = title_h
    sheet.blit(sub.render("FEASIBILITY — collision-column fill (red = PIPE_W)",
                          True, (255, 224, 150)), (fx, fy - 22))
    for (cell, ch), h in zip(feas, heights):
        sheet.blit(cell, (fx, fy))
        pygame.draw.rect(sheet, (60, 62, 72), (fx, fy, cell.get_width(), ch), 1)
        lab = label.render(f"{h}px  ·  max empty run {fills[h]}px", True,
                           (210, 212, 222))
        sheet.blit(lab, (fx, fy + ch + 3))
        fy += ch + label_h + pad

    out = _REPO / "docs" / "pillar_landmarks" / "smock-windmill" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"clearance day  top={cl_day[0]}px bot={cl_day[1]}px")
    print(f"clearance night top={cl_night[0]}px bot={cl_night[1]}px")
    print(f"max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))


if __name__ == "__main__":
    main()
