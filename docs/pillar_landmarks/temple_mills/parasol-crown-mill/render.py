"""Standalone candidate: `parasol-crown-mill` — a squat Song-brick shrine
PEDESTAL crowned by ONE big rotating temple PARASOL: a smooth ribbed convex
DOME in lacquer-red with gold rib-spokes and a deep scalloped hanging fringe,
capped by a bronze crown-knob finial that carries the centreline to the gap rim.

Seeded on the `waterwheel-mill` river-shrine tower: we KEEP its Song-brick
material kit + scan-line masonry + corbel cap + 3-layer plinth + plinth-mist +
foliage harness, and REMOVE the water-wheel and all water (no `_water_wheel`,
`_launder_and_splash`, `_pond_aqua`). The battered cone is re-shaped into a
squat wide brick DRUM-and-necking pedestal so the broad parasol dominates the
silhouette (the inverse proportion of the tall-spire sibling).

Colocated EXPLORATION module for the pillar-landmark design loop. It follows the
shipped pagoda idiom (`candidate_*(surf, top_rect, bot_rect, palette, seed)`, an
upright `_draw_one` reused for both rects, the ceiling twin a vertical flip of a
temp surface) but does NOT import into or modify any game/ module — it only
borrows read-only colour + AA + ornament helpers so the exploration reads like
the real game at the pagoda fidelity bar.

Silhouette identity (set-level pin): the ONLY concept whose crown is ONE smooth
convex DOME with a hanging SCALLOPED SKIRT. That domed skirt is the edge
signature that splits it from the vane-star's pointed gold rosette and the
sail-fan's flat-based canvas sweep — a big smooth umbrella, not a flat spread.
The 'it turns' read lives INSIDE that fixed dome+skirt silhouette (so the
mirror flip stays clean): alternating lit/shadow meridian GORES (fluting),
spiral-swept gilt ribs, a hard foreshortening skew and a wind-leaned hem —
value + sweep, never a change of silhouette KIND. Blackout reads as a squat
brick block under one wide domed cap.

Column-fill contract: the ~58 px collision column is carried top-to-bottom by
the BRICK PEDESTAL. Its slight batter is capped so shoulder and base half-widths
both stay >= PIPE_W/2, and the pedestal is kept from over-widening the plinth
past the column (the opposite fill risk of a squat body). The parasol is pure
crown/gutter overhang; the bronze crown-knob holds the centreline to the gap rim.

Mirror: the ceiling twin is a true vertical FLIP of an upright draw into a temp
surface. The dome + fringe are bilaterally symmetric about `cx`, so the flip
leaves a clean centred parasol on the hung copy (the family's easiest flip); the
knob carries the centreline to the gap rim on both halves.

Run:  python docs/pillar_landmarks/temple_mills/parasol-crown-mill/render.py
Out:  docs/pillar_landmarks/temple_mills/parasol-crown-mill/round_1.png
"""
from __future__ import annotations

import math
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO))

import pygame

from game.config import GROUND_Y, PIPE_W
from game import biome
from game.pillar_pagodas import (
    _mix,
    _shade,
    _gradient_rect,
    _aa_polyline,
    _lit_niche,                  # noqa: F401 — retained from the borrowed kit
    _tile_hatch,
    _glazed_tile_checker,        # noqa: F401 — imported per brief material kit
    _draw_plinth_mist,
    _is_dark_sky,
    _is_warming_sky,             # noqa: F401 — imported per brief material kit
    _cap_lit_for_dark_sky,
    _cap_dark_for_dark_sky,
    _terracotta,
    _song_brick,                 # noqa: F401 — imported per brief material kit
    _bronze,
    _gold_bright,
    _vermilion,
    _lacquer_red,
    _brick_mortar,
    _songyue_dwarf_eave,
)
from game.pillar_variants import draw_grass_bed
# draw_side_shrub lives in game.draw (the shipped foliage kit), not
# pillar_variants — the seed harness borrows it from there too.
from game.draw import draw_side_shrub


# ── Material roles (all biome-derived via _mix/_shade so day→night retints) ───
#
# BRICK PEDESTAL → stone_dark / stone_mid  (_terracotta + _brick_mortar): the
#   squat warm-clay shrine drum, distinct from the cool cream Song-brick pagoda.
# PARASOL DOME   → stone_dark lacquer  (_vermilion lit → _lacquer_red shadow):
#   a saturated cinnabar canopy, radially shaded so it reads as a round turning
#   umbrella rather than a flat painted arc.
# RIBS + KNOB    → stone_accent  (_gold_bright / _bronze): the gilt rib-spokes,
#   rim-tip nubs and crown-knob finial. Only the metal carries a night halo.
# FRINGE         → lacquer + cream: alternating _vermilion / stone_light scallops
#   for the deep rhythmic hanging skirt that is this concept's edge signature.

def _brick_lit(p):
    # Sun-side clay — capped at dusk/night so the shaded flank + niche glow
    # carry the silhouette instead of a value-spiking wall.
    return _cap_lit_for_dark_sky(_shade(_terracotta(p), 28), p)


def _brick_mid(p):
    return _terracotta(p)


def _brick_shadow(p):
    # Floored at night so the shaded pedestal edge keeps value over a deep sky
    # and the mass doesn't collapse into one black blob.
    return _cap_dark_for_dark_sky(_shade(_terracotta(p), -42), p, floor=60)


def _mortar(p):
    return _shade(_brick_mortar(p), 16)


def _edge_rim(p):
    # Faint cool-lit rim run down the shadow-side outline at night so the
    # pedestal holds its edge against a dark sky (day palettes never trigger).
    return _mix(p['stone_mid'], p['stone_light'], 0.55)


def _dome_lit(p):
    # Cinnabar highlight — capped at night so the convex hotspot never spikes
    # toward hot white; the rotation-read comes from value, not glare.
    return _cap_lit_for_dark_sky(_shade(_vermilion(p), 44), p, cap=228)


def _dome_mid(p):
    return _vermilion(p)


def _dome_shadow(p):
    # Deep lacquer on the shaded rim of the canopy, floored at night so the
    # dome edge holds value instead of swallowing into the sky.
    return _cap_dark_for_dark_sky(_lacquer_red(p), p, floor=52)


def _cream(p):
    return _mix(p['stone_light'], (244, 232, 210), 0.58)


def _matte_niche(surf, cx, cy, w, h, palette):
    """A recessed shrine doorway drawn MATTE — dark frame + darker inside + a
    thin warm rim on a plain alpha blit. The pedestal is deliberately NEVER a
    glow source (unlike the shipped additive `_lit_niche`, which blows to white
    over dark brick at night); the only night glow on this concept is the
    finial metal halo, so the rim here is clamped and never accumulates."""
    if w < 3 or h < 4:
        return
    frame = _shade(palette['stone_dark'], -25)
    inside = _shade(palette['stone_dark'], -50)
    pygame.draw.rect(surf, frame, (cx - w // 2, cy, w, h))
    pygame.draw.rect(surf, inside, (cx - w // 2 + 1, cy + 1, w - 2, h - 2))
    rim = _mix(palette['stone_accent'], (210, 180, 110), 0.7)
    alpha = 150 if _is_dark_sky(palette) else 90
    rim_layer = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(rim_layer, (*rim, alpha), (0, 0, w, h), 1)
    surf.blit(rim_layer, (cx - w // 2, cy))


# ── Brick pedestal body ──────────────────────────────────────────────────────

def _brick_pedestal(surf, cx, top_y, base_y, hw_top, hw_base, palette):
    """Squat brick drum painted as horizontal scan-lines, each a short
    left-lit → mid → right-shadow ramp so the flat body reads as rounded
    masonry volume at PIPE_W=58 (the `_gradient_rect` per-row volume trick).
    Mortar coursing overlays every 3 px with a broken half-cell offset so the
    eye reads brick-bond, not stripes. WASM-safe: only pygame.draw 1-px lines."""
    lit, mid, shadow = _brick_lit(palette), _brick_mid(palette), _brick_shadow(palette)
    mortar = _mortar(palette)
    rim = _edge_rim(palette)
    dark_sky = _is_dark_sky(palette)
    h = base_y - top_y
    if h < 2:
        return
    for i in range(h):
        y = top_y + i
        t = i / (h - 1)                       # 0 at neck, 1 at base
        hw = int(round(hw_top + (hw_base - hw_top) * t))
        if hw < 1:
            continue
        for j in range(hw):
            u = j / max(1, hw)
            pygame.draw.line(surf, _mix(lit, mid, u),
                             (cx - hw + j, y), (cx - hw + j, y), 1)
            pygame.draw.line(surf, _mix(mid, shadow, u),
                             (cx + j, y), (cx + j, y), 1)
        if i % 3 == 2:
            if (i // 3) % 2 == 0:
                pygame.draw.line(surf, mortar,
                                 (cx - hw + 1, y), (cx + hw - 1, y), 1)
            else:
                pygame.draw.line(surf, mortar,
                                 (cx - hw + 1, y), (cx - 1, y), 1)
                pygame.draw.line(surf, mortar,
                                 (cx + 1, y), (cx + hw - 1, y), 1)
        if dark_sky:
            pygame.draw.line(surf, rim, (cx + hw - 1, y), (cx + hw - 1, y), 1)
    edge = _shade(_brick_shadow(palette), -18)
    _aa_polyline(surf, edge, [(cx - hw_top, top_y), (cx - hw_base, base_y)])
    _aa_polyline(surf, edge, [(cx + hw_top, top_y), (cx + hw_base, base_y)])


def _corbel_neck(surf, cx, neck_y, hw_neck, palette):
    """A short corbelled necking that seats the dome on the pedestal — two
    stepped brick ledges with a `_songyue_dwarf_eave` lip so the canopy springs
    from a proper string-course rather than floating over bare brick."""
    for k in range(2):
        hw = int(hw_neck * (1.0 + 0.10 * k))
        y = neck_y - 3 + k * 3
        band = pygame.Rect(cx - hw, y, hw * 2, 3)
        _gradient_rect(surf, band, _brick_lit(palette), _brick_mid(palette),
                       _brick_shadow(palette))
    _songyue_dwarf_eave(surf, cx, neck_y - 3, int(hw_neck * 1.14), palette, depth=2)
    _tile_hatch(surf, cx - hw_neck + 2, neck_y - 4, cx + hw_neck - 2, neck_y - 4,
                _mortar(palette), step=5)


# ── The domed parasol crown ──────────────────────────────────────────────────

# Toggled only by the review harness so the realized per-gore value step can be
# measured as the difference between an alternated and a flat canopy render.
_GORE_ALT = True


def _cap228(c):
    # Hard ceiling so no lacquer/gold pixel spikes toward hot white — the pop
    # is carried by saturation + value, never by glare.
    return (min(228, c[0]), min(228, c[1]), min(228, c[2]))


def _rib_lats(n_rib, compress):
    # Meridian rib lateral positions across the rim, in [-1, 1]. `compress`
    # bunches ribs toward the near/left edge so that side foreshortens — the
    # >1 exponent is the perspective cue that the canopy is caught mid-turn.
    return [-1.0 + 2.0 * ((i / (n_rib - 1)) ** compress) for i in range(n_rib)]


def _gore_of(lat, rib_lats):
    # Which inter-rib gore a lateral coord falls in (clamped at the edges).
    for j in range(len(rib_lats) - 1):
        if lat < rib_lats[j + 1]:
            return j
    return len(rib_lats) - 2


def _parasol_dome(surf, cx, peak_y, rim_y, hw, palette, *, skew):
    """One convex parasol canopy filling the ellipse whose bottom edge is the
    rim at `rim_y` (half-width `hw`) and whose apex is at `peak_y`.

    The 'it TURNS' read (this family's one live gate) lives entirely INSIDE a
    silhouette that stays a symmetric dome+skirt (so the mirror flip is clean):
      · gore VALUE-ALTERNATION — every other meridian gore is stepped darker,
        so the canopy reads as a fluted spinning wind-catcher, not a smooth
        mushroom (the highest-leverage cue, and mirror-safe since it is a
        left↔right-symmetric rhythm about `cx`);
      · a tangential SPIRAL sweep on the thin gilt ribs (a uniform bow whose
        direction follows `skew`) so the fan reads as a pinwheel curl;
      · a hard foreshortening `skew` — off-centre hotspot + near-edge rib
        compression — pushed until the tilt reads at 58 px.
    Matte-saturated lacquer — capped, never a glow source (metal-only halo)."""
    dome_h = rim_y - peak_y
    if dome_h < 6 or hw < 8:
        return
    lit = _dome_lit(palette)
    mid = _dome_mid(palette)
    shadow = _dome_shadow(palette)
    gold = _gold_bright(palette)
    bronze = _bronze(palette)
    dark_sky = _is_dark_sky(palette)

    sgn = 1.0 if skew >= 0 else -1.0             # canopy lean → curl direction
    n_rib = 9
    rib_lats = _rib_lats(n_rib, 1.5)             # stronger near-edge compression

    # Off-centre hotspot, biased hard along the lean so the convex read also
    # says 'tilted, mid-rotation' rather than a static front-on mushroom.
    hlx = cx + skew * 1.35 - hw * 0.22
    hly = peak_y + dome_h * 0.36

    def _curl(ss):
        # Uniform tangential bow (0 at apex + rim, max mid-span) shared by the
        # gore fill AND the ribs so both spiral together as one turning fan.
        return sgn * hw * 0.16 * math.sin(math.pi * ss)

    # Filled dome by ellipse scan-rows (apex → rim). Each pixel gets a radial
    # 3-stop convex shade, THEN an alternating per-gore value step so adjacent
    # gores differ by ~a value of 46 at 1× — the fluting that sells rotation.
    for y in range(peak_y, rim_y + 1):
        dy = rim_y - y
        frac = dy / dome_h                       # 0 rim → 1 apex
        ss = 1.0 - frac
        w = hw * math.sqrt(max(0.0, 1.0 - frac ** 2))
        wi = int(w)
        if wi < 1:
            continue
        row_cx = cx + skew * (1.0 - ss) + _curl(ss)
        for x in range(cx - wi, cx + wi + 1):
            nx = (x - hlx) / hw
            ny = (y - hly) / dome_h
            d = math.sqrt(nx * nx + ny * ny)
            t = min(1.0, d / 1.12)
            if t < 0.5:
                col = _mix(lit, mid, t * 2.0)
            else:
                col = _mix(mid, shadow, (t - 0.5) * 2.0)
            lat = max(-1.0, min(1.0, (x - row_cx) / max(1.0, w)))
            if _GORE_ALT and _gore_of(lat, rib_lats) % 2 == 1:
                col = (max(22, col[0] - 54), max(18, col[1] - 54),
                       max(18, col[2] - 54))
            surf.set_at((x, y), _cap228(col))

    # Gilt meridian ribs — the thin seams between gores. They ride the ellipse
    # AND the shared `_curl` bow so the whole fan reads as a spiralling
    # pinwheel; kept 1 px gilt lines (never fattened into a gold rosette).
    rim_pts = []
    for lat in rib_lats:
        pts = []
        steps = 8
        for s in range(steps + 1):
            ss = s / steps
            yy = peak_y + ss * dome_h
            rowfrac = (rim_y - yy) / dome_h
            roww = hw * math.sqrt(max(0.0, 1.0 - rowfrac ** 2))
            xx = cx + skew * (1.0 - ss) + _curl(ss) + lat * roww
            pts.append((xx, yy))
        # Fold-shadow just inboard of the rib so each gore reads rounded.
        fold = [(px + (1 if lat >= 0 else -1), py) for px, py in pts]
        _aa_polyline(surf, _shade(shadow, -14), fold)
        rib_col = _cap228(_mix(gold, lit, 0.15))
        _aa_polyline(surf, rib_col, pts)
        rim_pts.append(pts[-1])

    # AA the dome silhouette so the canopy edge reads smooth at scale. At night
    # the shadow-side (left) edge is carried in a cool lit rim so the shaded
    # canopy holds its outline against a deep sky instead of dissolving.
    outline = []
    for s in range(25):
        ang = math.pi * (s / 24)                 # left → right over the top
        outline.append((cx - hw * math.cos(ang), rim_y - dome_h * math.sin(ang)))
    _aa_polyline(surf, _shade(shadow, -22), outline)
    if dark_sky:
        cool = _mix(shadow, palette['stone_light'], 0.42)
        _aa_polyline(surf, cool, outline[:13])

    # Scalloped hanging fringe — DEEP + rhythmic, the concept's edge signature.
    # A few px of uniform wind-lean (following the lean) sells the caught-air.
    _parasol_fringe(surf, cx, rim_y, hw, dome_h, palette, sway=sgn * 3)

    # Gilt rim-tip nubs at each rib landing (metal that catches the night halo).
    for (tx, ty) in (rim_pts[0], rim_pts[-1], rim_pts[len(rim_pts) // 2]):
        pygame.draw.circle(surf, gold, (int(tx), int(ty)), 2)
        pygame.draw.circle(surf, _cap228(_shade(gold, 22)), (int(tx), int(ty) - 1), 1)

    # Bronze crown-knob finial carrying the centreline toward the gap rim. At
    # night the tip is pulled back a couple px so the hung-twin centreline gap
    # opens to breathing air (~3 px) instead of welding shut at the rim.
    knob_x = cx                                  # held ON the centreline so the
    tip_y = peak_y - (2 if dark_sky else 5)      # hung twin still meets the rim
    pygame.draw.line(surf, _shade(bronze, -28), (knob_x, peak_y + 1),
                     (knob_x, tip_y + 2), 2)
    pygame.draw.circle(surf, bronze, (knob_x, tip_y + 2), 3)
    pygame.draw.circle(surf, gold, (knob_x, tip_y + 2), 2)
    pygame.draw.circle(surf, _cap228(_shade(gold, 26)), (knob_x - 1, tip_y + 1), 1)

    # Night halo on the metal only (knob + rib tips), gated on a dark sky.
    # Warm amber with a low blue channel + modest alphas so the additive glow
    # reads as a gilt shrine-lamp aura, never accumulating to a blown white.
    if dark_sky:
        halo = (236, 196, 108)
        glow = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*halo, 40), (12, 12), 11)
        pygame.draw.circle(glow, (*halo, 70), (12, 12), 6)
        pygame.draw.circle(glow, (*halo, 105), (12, 12), 3)
        surf.blit(glow, (knob_x - 12, tip_y + 2 - 12),
                  special_flags=pygame.BLEND_RGBA_ADD)
        for (tx, ty) in (rim_pts[0], rim_pts[-1]):
            tnub = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(tnub, (*halo, 55), (5, 5), 4)
            pygame.draw.circle(tnub, (*halo, 95), (5, 5), 2)
            surf.blit(tnub, (int(tx) - 5, int(ty) - 5),
                      special_flags=pygame.BLEND_RGBA_ADD)


def _parasol_fringe(surf, cx, rim_y, hw, dome_h, palette, *, sway=0.0):
    """A row of deep hanging scallop-lobes off the canopy rim — alternating
    lacquer-red and cream with a gilt cusp between, drawn as filled downward
    semicircles. This is the concept's edge signature (a skirt, not a flat
    fan-base) AND the 'it catches wind' cue: `sway` leans the lobe bottoms a
    few px off pendant (uniform, so a vertical flip just mirrors the lean)."""
    depth = int(min(11, max(6, dome_h * 0.30)))
    span = hw * 2
    n = max(6, min(11, int(span / 11)))
    lobe_w = span / n
    verm = _vermilion(palette)
    verm_lo = _shade(_lacquer_red(palette), -8)
    cream = _cream(palette)
    cream_lo = _shade(cream, -26)
    gold = _gold_bright(palette)
    left = cx - hw
    for k in range(n):
        lx = left + lobe_w * k
        mx = lx + lobe_w * 0.5
        r = lobe_w * 0.5
        top = _cream(palette) if k % 2 else verm
        bot = cream_lo if k % 2 else verm_lo
        # Filled downward semicircle via a fan of vertical spans (cheap + AA-free
        # so it survives WASM identically to native). The wind-lean grows with
        # drop so the free hem swings while the attached rim stays put.
        pts = [(lx, rim_y)]
        segs = 8
        for s in range(segs + 1):
            a = math.pi * (s / segs)             # 0..pi sweeps the lobe bottom
            px = mx - r * math.cos(a) + sway * math.sin(a)
            py = rim_y + depth * math.sin(a)
            pts.append((px, py))
        pts.append((lx + lobe_w, rim_y))
        pygame.draw.polygon(surf, _mix(top, bot, 0.5),
                            [(int(px), int(py)) for px, py in pts])
        # Shaded lower half + a bright underside tick so the scallop reads 3-D.
        pygame.draw.line(surf, bot, (int(lx + 1), rim_y + depth - 3),
                         (int(mx), int(rim_y + depth)), 1)
        pygame.draw.line(surf, _shade(top, 18),
                         (int(mx), int(rim_y + depth)),
                         (int(lx + lobe_w - 1), rim_y + depth - 3), 1)
        # Gilt cusp seam between lobes catches a point of light.
        pygame.draw.line(surf, _cap228(gold), (int(lx), rim_y),
                         (int(lx), rim_y + 2), 1)
    _aa_polyline(surf, _shade(verm_lo, -18),
                 [(cx - hw, rim_y), (cx + hw, rim_y)])


# ── One upright silhouette ───────────────────────────────────────────────────

def _draw_one(surf, cx, base_y, top_y, body_w, palette, seed, *, decor=True):
    """One upright parasol-crown-mill filling [top_y, base_y]. Height-adaptive:
    the parasol crown takes a capped share of the height (smaller dome on short
    sections) while the squat brick pedestal always fills the collision column
    down to the plinth. Very short sections drop to a knob-only crown."""
    total_h = base_y - top_y
    if total_h < 20:
        return
    skew = 1 if (seed % 2 == 0) else -1          # rotational lean of the canopy

    # Pedestal batter capped so both neck + base half-widths stay >= PIPE_W/2
    # (the collision column is always filled) but the base is kept from
    # over-widening the plinth much past the 58 px column (the squat-body risk).
    hw_base = max(PIPE_W // 2 + 4, int(body_w * 0.57))
    hw_neck = max(PIPE_W // 2 + 1, int(body_w * 0.52))

    # Crown budget: a generous but capped share so the dome dominates at nominal
    # proportions yet a tall section keeps a squat pedestal under it.
    crown_v = min(int(total_h * 0.42), 82)
    crown_v = min(crown_v, total_h - 24)          # always leave pedestal height
    crown_v = max(0, crown_v)

    # 3-layer plinth under the pedestal.
    plinth_h = 6 if total_h > 60 else 3
    pw0 = hw_base * 2 + 8
    if decor:
        _draw_plinth_mist(surf, cx, base_y, pw0 + 8, palette)
    pygame.draw.rect(surf, _shade(palette['stone_dark'], -16),
                     (cx - pw0 // 2, base_y - plinth_h, pw0, plinth_h))
    pygame.draw.rect(surf, _shade(palette['stone_mid'], -6),
                     (cx - pw0 // 2 + 2, base_y - plinth_h + 1, pw0 - 4, 2))
    pygame.draw.line(surf, palette['stone_light'],
                     (cx - pw0 // 2, base_y - plinth_h),
                     (cx + pw0 // 2, base_y - plinth_h), 1)

    body_base_y = base_y - plinth_h

    if crown_v >= 16 and hw_neck >= 12:
        rim_y = top_y + crown_v
        finial_h = min(9, int(crown_v * 0.16))
        peak_y = top_y + finial_h
        hw_dome = min(52, int(hw_neck + crown_v * 0.36) + 6)

        # Pedestal under the canopy (its neck seats the dome rim).
        _brick_pedestal(surf, cx, rim_y, body_base_y, hw_neck, hw_base, palette)

        # Corbel string-courses band the shaft (0–2 depending on height).
        body_h = body_base_y - rim_y
        n_band = max(0, min(2, body_h // 40))
        for k in range(n_band):
            ht = (k + 1) / (n_band + 1)
            y = int(rim_y + body_h * (1 - ht))
            hw = int(round(hw_neck + (hw_base - hw_neck) * (1 - ht)))
            _songyue_dwarf_eave(surf, cx, y, hw, palette, depth=2)
            _tile_hatch(surf, cx - hw + 3, y - 1, cx + hw - 3, y - 1,
                        _mortar(palette), step=5)

        # A matte shrine doorway niche low on the pedestal face (never a glow
        # source — the finial metal is this concept's only night halo).
        if body_h > 24 and hw_base > 14:
            door_w = min(9, hw_base // 2)
            door_h = min(16, body_h // 3)
            _matte_niche(surf, cx, body_base_y - door_h - 2, door_w, door_h, palette)

        # The corbelled necking + the domed parasol crown.
        _corbel_neck(surf, cx, rim_y, hw_neck, palette)
        # Pushed hard (~hw/4) so the foreshortening tilt reads at 58 px, where
        # R1's gentle ~7% skew was invisible.
        _parasol_dome(surf, cx, peak_y, rim_y, hw_dome, palette,
                      skew=skew * max(6, hw_dome // 4))
    else:
        # Very short section — pedestal fills the column, tiny knob crown only.
        _brick_pedestal(surf, cx, top_y + 4, body_base_y, hw_neck, hw_base, palette)
        pygame.draw.circle(surf, _bronze(palette), (cx, top_y + 3), 2)
        pygame.draw.circle(surf, _gold_bright(palette), (cx, top_y + 3), 1)

    if decor:
        draw_grass_bed(surf, cx, base_y - 1, pw0 + 6, 14, palette, seed=seed)
        draw_side_shrub(surf, cx - (hw_base - 2), base_y - 1, palette, scale=0.82)
        draw_side_shrub(surf, cx + (hw_base - 2), base_y - 1, palette, scale=0.72)


def candidate_parasol_crown_mill(surf, top_rect, bot_rect, palette, seed):
    bcx = bot_rect.x + bot_rect.width // 2
    tcx = top_rect.x + top_rect.width // 2

    if bot_rect.height > 22:
        _draw_one(surf, bcx, bot_rect.bottom, bot_rect.y,
                  bot_rect.width, palette, seed, decor=True)

    if top_rect.height > 22:
        # Structural mirror: draw upright into a temp sized to top_rect.height,
        # flip vertically, hang from the ceiling. The dome + fringe are
        # bilaterally symmetric about cx so the flip yields a clean parasol and
        # the crown-knob still reaches the gap rim on the hung twin.
        w = surf.get_width()
        tmp = pygame.Surface((w, top_rect.height), pygame.SRCALPHA)
        _draw_one(tmp, tcx, top_rect.height, 0,
                  top_rect.width, palette, seed, decor=False)
        flipped = pygame.transform.flip(tmp, False, True)
        surf.blit(flipped, (0, top_rect.y))


# ── Review harness ───────────────────────────────────────────────────────────

MARGIN = 70
CACHE_W = PIPE_W + MARGIN * 2
PHASE_DAY = 0.30
PHASE_NIGHT = 0.85
SEED = 12                                       # even → canopy leans right

GAP_Y, GAP_H = 205, 150
TOP_H = int(GAP_Y - GAP_H / 2)
BOT_TOP = int(GAP_Y + GAP_H / 2)
CROP_TOP, CROP_BOT = 14, 496


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
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    top_rect = pygame.Rect(MARGIN, 0, PIPE_W, TOP_H)
    bot_rect = pygame.Rect(MARGIN, BOT_TOP, PIPE_W, GROUND_Y - BOT_TOP)
    candidate_parasol_crown_mill(surf, top_rect, bot_rect, pal, SEED)
    return surf


def _render_pair(pal):
    surf = _pair_surf(pal)
    cell = _sky_ground(CACHE_W, GROUND_Y, pal, 60)
    cell.blit(surf, (0, 0))
    guide = (255, 90, 90)
    for rim in (TOP_H, BOT_TOP):
        for x in range(0, CACHE_W, 8):
            pygame.draw.line(cell, guide, (x, rim), (x + 4, rim), 1)
    return cell.subsurface(pygame.Rect(0, CROP_TOP, CACHE_W,
                                       CROP_BOT - CROP_TOP)).copy()


def _measure_centreline(pal):
    """Mirrored-centreline coverage: on the top (hung) section, how close does
    the crown centreline reach the gap rim (TOP_H)? Returns px gap between the
    lowest filled pixel at x=cx in the top section and the rim (0 = touches)."""
    surf = _pair_surf(pal)
    cx = MARGIN + PIPE_W // 2
    low = -1
    for y in range(0, TOP_H + 2):
        if surf.get_at((cx, y))[3] > 50:
            low = y
    return TOP_H - low if low >= 0 else TOP_H


def _measure_gore_step(pal):
    """Adjacent-gore value step: scan a mid-dome horizontal row, collect the
    per-pixel brightness of the lacquer canopy pixels (reddish, non-gilt), and
    report the amplitude between the lit-gore band and the shadow-gore band —
    the fluting contrast that carries the rotation read."""
    # The realized per-gore value step is exactly the darkening applied to odd
    # gores (radial-ramp independent): render the canopy alternated vs flat and
    # average |Δ| over the shadow-gore pixels that actually changed.
    global _GORE_ALT
    _GORE_ALT = True
    on = _pair_surf(pal)
    _GORE_ALT = False
    off = _pair_surf(pal)
    _GORE_ALT = True
    diffs = []
    for y in range(BOT_TOP, BOT_TOP + 60):
        for x in range(MARGIN, MARGIN + PIPE_W + 40):
            a, b = on.get_at((x, y)), off.get_at((x, y))
            if a[3] > 50 and b[3] > 50:
                d = (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) / 3.0
                if d > 4:
                    diffs.append(d)
    return round(sum(diffs) / len(diffs), 1) if diffs else 0.0


def _measure_fill(pal, section_h):
    """Max vertical run (px) of ZERO-fill rows inside the PIPE_W collision
    column for a bottom-only section of the given height."""
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_parasol_crown_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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
    candidate_parasol_crown_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
                                 bot_rect, pal, SEED)
    cell = _sky_ground(CACHE_W, cell_h, pal, 10)
    crop_top = GROUND_Y - section_h - head
    cell.blit(surf, (0, 0), pygame.Rect(0, crop_top, CACHE_W, cell_h))
    cx = MARGIN + PIPE_W // 2
    for ex in (cx - PIPE_W // 2, cx + PIPE_W // 2):
        pygame.draw.line(cell, (255, 60, 60), (ex, 0), (ex, cell_h), 1)
    return cell, cell_h


def _render_blackout(pal, section_h=235):
    surf = pygame.Surface((CACHE_W, GROUND_Y), pygame.SRCALPHA)
    bot_rect = pygame.Rect(MARGIN, GROUND_Y - section_h, PIPE_W, section_h)
    candidate_parasol_crown_mill(surf, pygame.Rect(MARGIN, 0, PIPE_W, 0),
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

    pair_day = _render_pair(day)
    pair_night = _render_pair(night)
    cl_day = _measure_centreline(day)
    cl_night = _measure_centreline(night)

    heights = [70, 210, 355]
    feas = [_render_feas(day, h) for h in heights]
    fills = {h: _measure_fill(day, h) for h in heights}
    blackout = _render_blackout(day)

    pad = 14
    label_h = 22
    title_h = 62
    pw, ph = pair_day.get_width(), pair_day.get_height()

    title = pygame.font.SysFont(None, 30)
    sub = pygame.font.SysFont(None, 18)
    label = pygame.font.SysFont(None, 19)

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

    sheet.blit(title.render("parasol-crown-mill — round 2", True, (245, 240, 230)),
               (pad, 12))
    sheet.blit(sub.render("squat brick pedestal + ONE domed lacquer PARASOL: gilt "
                          "ribs, deep scalloped fringe, bronze crown-knob",
                          True, (170, 172, 182)), (pad, 40))

    for i, (pair, name, cl) in enumerate((
            (pair_day, f"DAY  PHASE={PHASE_DAY}", cl_day),
            (pair_night, f"NIGHT  PHASE={PHASE_NIGHT}", cl_night))):
        hx = pad + i * (pw + pad)
        hy = title_h
        sheet.blit(pair, (hx, hy))
        pygame.draw.rect(sheet, (60, 62, 72), (hx, hy, pw, ph), 1)
        lab = label.render(name, True, (255, 224, 150))
        sheet.blit(lab, (hx + (pw - lab.get_width()) // 2, hy + ph + 3))
        cl2 = sub.render(f"mirror centreline gap to rim: {cl}px", True,
                         (200, 202, 212))
        sheet.blit(cl2, (hx + (pw - cl2.get_width()) // 2, hy + ph + 3 + 18))

    bx = pad
    by = title_h + ph + label_h + pad + 14
    sheet.blit(blackout, (bx, by))
    pygame.draw.rect(sheet, (60, 62, 72), (bx, by, bo_w, bo_h), 1)
    lab = label.render("BLACKOUT — 58px silhouette read", True, (255, 224, 150))
    sheet.blit(lab, (bx, by + bo_h + 3))

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

    out = _REPO / "docs" / "pillar_landmarks" / "temple_mills" / \
        "parasol-crown-mill" / "round_2.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")
    print(f"mirror centreline->rim gap: day={cl_day}px night={cl_night}px")
    print("max empty run: " + "  ".join(f"{h}px->{fills[h]}px" for h in heights))
    print(f"adjacent-gore value step: day={_measure_gore_step(day)}  "
          f"night={_measure_gore_step(night)}")

    # PIL-sanity contract (no display): day and night pairs must DIFFER (the
    # biome retint is live) and neither may spike to hot white (>=250 all-ch).
    ds = pygame.image.tostring(_pair_surf(day), "RGBA")
    ns = pygame.image.tostring(_pair_surf(night), "RGBA")
    print(f"day==night pair bytes: {ds == ns}  (must be False)")
    for pname, pal in (("day", day), ("night", night)):
        psurf = _pair_surf(pal)
        hot = 0
        for yy in range(psurf.get_height()):
            for xx in range(psurf.get_width()):
                c = psurf.get_at((xx, yy))
                if c[3] > 50 and c[0] >= 250 and c[1] >= 250 and c[2] >= 250:
                    hot += 1
        print(f"{pname}: pure-white(>=250) alpha>50 pixels = {hot}")


if __name__ == "__main__":
    main()
