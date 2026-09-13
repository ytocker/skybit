"""SKULL-KING event ROUTE figure: 5 hard routes (difficulty 6-10, one each) drawn
as stacked-skull / skewer PILLARS — every pillar slot a (deterministic-)random one
of the twenty skull pillar designs P1-P20. The skull analogue of the clown event's
warren route, but the skull event draws from the HARD band (6-10) instead of the
clown's easy archetypes (2-4).

Design-only: mirrors docs/pagoda_warren/routes_all.png but skull-themed; the event
is NOT wired into the game. Reuses the route catalog + difficulty from
render_warren_all, the sky/overlays from render_warren_mockup, and the skull
pillar_engine.

    PYTHONPATH=. python tools/render_skull_routes.py
"""
import os, sys, importlib.util, random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import PIPE_W, GROUND_Y, H
from game.parrot import get_parrot
from tools.render_warren_mockup import (
    shaped_palette, draw_sky_ground, draw_flight_path, _path_y_at,
)
from tools.render_warren_all import TIERS, get_pagodas, diff_color

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILLARS_DIR = os.path.join(ROOT, "docs/skull_king_stack/pillars")
sys.path.insert(0, PILLARS_DIR)
import pillar_engine as PE

PHASE = 0.62          # dusk/night-leaning sky for the skull-king mood (bone reads on it)
ROUTE_MARGIN_R = 1.05  # seat the focal skull at the gap edge so pillars frame the channel
MAX_PILLARS = 30       # cap very long routes (legibility + render time)
# skull columns only fill ~46px of the 58px slot (vs pagodas, which fill it + eaves),
# so the routes' native 72px pitch leaves a big gap. Re-space the columns tighter so
# the skull totems sit shoulder-to-shoulder — vertical gap path is untouched. At 48px
# pitch the ~46px columns nearly touch, packing the skewers into a near-continuous wall.
SP_SKULL = 48
START_X_SKULL = 46


def _compress(pagodas):
    """Re-space a route's pillars to a tighter horizontal pitch (SP_SKULL) so the
    narrow skull columns sit close together. Only x changes; gap centre/height stay."""
    if not pagodas:
        return pagodas
    base = pagodas[0][0]
    orig_pitch = (pagodas[1][0] - pagodas[0][0]) if len(pagodas) >= 2 else 72.0
    f = SP_SKULL / orig_pitch
    return [(START_X_SKULL + (x - base) * f, cy, gap_h, seed)
            for (x, cy, gap_h, seed) in pagodas]

# the twenty skull pillar designs in P1..P20 order (P11-P20 are no-skewer totems
# that widen the pool so the routes stop visibly repeating)
DESIGN_FILES = [
    ("relic-reliquary-totem",        "render_relic_reliquary_totem.py"),
    ("horned-warband",               "render_horned_warband.py"),
    ("keystone-cairn",               "render_keystone_cairn.py"),
    ("gaunt-hollow-spire",           "render_gaunt_hollow_spire.py"),
    ("broken-bone-pile",             "render_broken_bone_pile.py"),
    ("plain-bone-spit",              "render_plain_bone_spit.py"),
    ("gold-cored-scepter",           "render_gold_cored_scepter.py"),
    ("ring-eye-washer-axle",         "render_ring_eye_washer_axle.py"),
    ("barbed-fang-harpoon",          "render_barbed_fang_harpoon.py"),
    ("bead-threaded-strand-spindle", "render_bead_threaded_strand_spindle.py"),
    ("runt-cairn-taper",             "render_runt_cairn_taper.py"),
    ("thirdeye-watchtower",          "render_thirdeye_watchtower.py"),
    ("lopsided-fang-lean",           "render_lopsided_fang_lean.py"),
    ("child-relic-shrine",           "render_child_relic_shrine.py"),
    ("darkblue-bone-rosary",         "render_darkblue_bone_rosary.py"),
    ("broad-block-bastion",          "render_broad_block_bastion.py"),
    ("cracked-ruin-lean",            "render_cracked_ruin_lean.py"),
    ("palm-jewel-pagoda",            "render_palm_jewel_pagoda.py"),
    ("necklace-draped-warlord",      "render_necklace_draped_warlord.py"),
    ("mongrel-generations-totem",    "render_mongrel_generations_totem.py"),
]


def _load_design(slug, fname):
    spec = importlib.util.spec_from_file_location("dsn_" + slug.replace("-", "_"),
                                                  os.path.join(PILLARS_DIR, slug, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return dict(recipe=m.RECIPE, with_skewer=m.WITH_SKEWER,
                skewer_style=m.SKEWER_STYLE, lean=getattr(m, "LEAN", 0.0))


DESIGNS = [_load_design(s, f) for s, f in DESIGN_FILES]


def _fill(recipe, hpx):
    """Tile a design's recipe to fill a pillar of height hpx: focal at the gap, then
    cycle the body up the column. Extra tiers past the surface clip harmlessly."""
    n = max(len(recipe), int(hpx / 34) + 2)
    body = recipe[1:] if len(recipe) > 1 else recipe
    return [recipe[0]] + [body[i % len(body)] for i in range(n - 1)]


def _skull_half(hpx, cap, design):
    return PE.render_pillar_half(int(hpx), cap=cap, recipe=_fill(design["recipe"], hpx),
                                 with_skewer=design["with_skewer"],
                                 skewer_style=design["skewer_style"],
                                 lean=design["lean"], margin_r=ROUTE_MARGIN_R)


def render_skull_strip(pagodas, rng):
    """Mirror render_warren_all.render_strip but paint each gap slot with a random
    skull pillar (top + bottom halves) instead of a pagoda pair."""
    pagodas = _compress(pagodas)                     # tighten the column spacing
    native_w = int(pagodas[-1][0] + SP_SKULL + 30)
    palette = shaped_palette(PHASE, dense=False)
    surf = pygame.Surface((native_w, H))
    draw_sky_ground(surf, native_w, H, palette)
    for (x, cy, gap_h, _seed) in pagodas:
        top_h = cy - gap_h / 2
        bot_y = cy + gap_h / 2
        bot_h = GROUND_Y - bot_y
        design = DESIGNS[rng.randrange(len(DESIGNS))]   # random pillar per slot
        if top_h > 6:
            surf.blit(_skull_half(top_h, "bottom", design), (int(x - PIPE_W / 2), 0))
        if bot_h > 6:
            surf.blit(_skull_half(bot_h, "top", design), (int(x - PIPE_W / 2), int(bot_y)))
    draw_flight_path(surf, pagodas)
    # the player (Pip) flying the route, near the start
    bx = pagodas[min(3, len(pagodas) - 1)][0]
    by = _path_y_at(pagodas, bx)
    nxt = _path_y_at(pagodas, bx + 24)
    bird = get_parrot(1, -12 if nxt > by else 12)
    surf.blit(bird, (int(bx - bird.get_width() / 2), int(by - bird.get_height() / 2)))
    return surf, native_w


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    # every route in the hard band, then pick the SHORTEST at each of d6..d10
    band = []
    for tier, build, ratings in TIERS:
        routes = build()
        assert len(routes) == len(ratings), f"{tier}: rating count mismatch"
        for route, d in zip(routes, ratings):
            if 6 <= d <= 10:
                band.append((d, route.name, tier, route.n, route.duration, get_pagodas(route)))
    chosen = []
    # prefer the most VARIED tier at each difficulty (so the 5 aren't all plunges),
    # then the shortest route within it for legibility.
    tier_pref = {
        "Advanced — creative": 0,
        "Base — teaching routes": 1,
        "Serious drop": 2,
        "Smaller drop (fair)": 3,
        "Aggressive drop": 4,
    }
    for d in (6, 7, 8, 9, 10):
        cands = [r for r in band if r[0] == d]
        if cands:
            chosen.append(min(cands, key=lambda r: (tier_pref.get(r[2], 9), r[3])))
    chosen.sort(key=lambda r: r[0])

    # render each chosen route's skull strip (cap length for legibility/time)
    strips = []
    for (d, name, tier, n, dur, pg) in chosen:
        shown = pg[:MAX_PILLARS]
        rng = random.Random("skull-route::" + name)      # deterministic per route
        strip, native_w = render_skull_strip(shown, rng)
        strips.append((d, name, tier, n, dur, len(shown), strip, native_w))

    max_native = max(nw for *_, nw in strips)
    CONTENT_W = 1680
    factor = min(0.46, CONTENT_W / max_native)
    row_h = int(H * factor)

    PAD, LEFT, ROW_GAP, TITLE_H = 24, 360, 12, 100
    canvas_w = PAD + LEFT + int(max_native * factor) + PAD
    canvas_h = TITLE_H + len(strips) * (row_h + ROW_GAP) + PAD
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((16, 14, 20))

    f_title = pygame.font.SysFont(None, 44, bold=True)
    f_sub = pygame.font.SysFont(None, 24, bold=True)
    f_rate = pygame.font.SysFont(None, 40, bold=True)
    f_name = pygame.font.SysFont(None, 30, bold=True)
    f_tier = pygame.font.SysFont(None, 20, bold=True)
    f_meta = pygame.font.SysFont(None, 20, bold=True)

    canvas.blit(f_title.render("SKULL-KING event — 5 routes (difficulty 6-10)", True,
                               (245, 240, 235)), (PAD, PAD - 2))
    canvas.blit(f_sub.render(
        "the event rolls a random hard route (6-10) · each pillar = a random skull "
        "design P1-P20 · one route per difficulty", True, (210, 180, 175)), (PAD, PAD + 40))

    y = TITLE_H
    for (d, name, tier, n, dur, shown, strip, native_w) in strips:
        disp_w = int(native_w * factor)
        scaled = pygame.transform.smoothscale(strip, (disp_w, row_h))
        rx = PAD + LEFT
        canvas.blit(scaled, (rx, y))
        pygame.draw.rect(canvas, (60, 58, 70),
                         pygame.Rect(rx - 1, y - 1, disp_w + 2, row_h + 2), 1)

        col = diff_color(d)
        chip = f_rate.render(f"{d}", True, (15, 17, 22))
        cw = 56
        pygame.draw.rect(canvas, col, pygame.Rect(PAD, y + 6, cw, 40), border_radius=8)
        canvas.blit(chip, (PAD + (cw - chip.get_width()) // 2, y + 11))
        canvas.blit(f_meta.render("/10", True, col), (PAD + cw + 4, y + 24))
        canvas.blit(f_name.render(name, True, (240, 230, 200)), (PAD + cw + 40, y + 4))
        canvas.blit(f_tier.render(tier, True, (150, 150, 165)), (PAD + cw + 40, y + 30))
        bar_x, bar_w = PAD + cw + 40, LEFT - cw - 64
        pygame.draw.rect(canvas, (40, 38, 50), pygame.Rect(bar_x, y + 50, bar_w, 7), border_radius=3)
        pygame.draw.rect(canvas, col, pygame.Rect(bar_x, y + 50, int(bar_w * d / 10), 7), border_radius=3)
        meta = f"{n}p · ~{dur:.0f}s" + (f"  · first {shown}" if shown < n else "")
        canvas.blit(f_meta.render(meta, True, (175, 170, 165)), (bar_x + bar_w + 8, y + 48))
        y += row_h + ROW_GAP

    out_dir = os.path.join(ROOT, "docs", "skull_king_stack", "routes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "skull_routes.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})  scale={factor:.3f}  {len(strips)} routes")


if __name__ == "__main__":
    main()
