"""Headless QA sheet: the 10 dormant biome sky designs behind REAL gameplay.

Same shape as docs/biome_redesign/round_7_all_skystars_daynight.png — rows =
the 10 sky designs, columns = the 12 day/night stages — but every cell is an
actual gameplay frame (bird, pipes, coins, mountains, foreground, HUD) rendered
through the real `App._render`, with ONLY the sky swapped to that design at the
column's phase.

How the swap works: `get_sky_surface_biome` is the function `_draw_background`
calls to bake the live sky; it's monkeypatched here to hand back a pre-baked
design sky (`game.biome_sky.paint_sky`). Everything drawn after the sky
(mountains/foreground/HUD) keys off `world.biome_phase`, so setting the cell's
phase makes the whole scene read at that time of day and harmonize with the
swapped sky. The registry is sky-only by scope, so mountains/foreground keep the
live biome lighting — this is an honest "what activating this design looks like"
preview, not a full-scene re-theme.

Dev aid only; the game never imports this. Output:
docs/biome_redesign/sky_designs_gameplay_grid.png

    python tools/preview_sky_designs_gameplay.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import random

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()

import game.scenes as scenes                       # noqa: E402
import game.sky_designs as _sky_designs            # noqa: E402
from game.config import W, H, GROUND_Y             # noqa: E402
from game.scenes import App, STATE_PLAY            # noqa: E402
from game.world import World                       # noqa: E402
from game.biome_sky import paint_sky               # noqa: E402
from game.biome_sky_keyframes import STAGES, BIOMES  # noqa: E402
from game.sky_designs import CATALOG               # noqa: E402

# This sheet drives the sky per cell via its own monkeypatch of the live bake;
# force the live-bake path (else an active design would short-circuit it and
# paint the same design in every row).
_sky_designs.ACTIVE_SKY_DESIGN = None

OUT = os.path.join(_ROOT, "docs", "biome_redesign", "sky_designs_gameplay_grid.png")
CYCLE_SECONDS = 320.0  # game/biome.py: phase = (t / 320) % 1

# Sheet geometry — native frame, downscaled tiles so 10x12 stays viewable.
TILE_SCALE = 0.42
TW, TH = int(W * TILE_SCALE), int(H * TILE_SCALE)
GUT = 150          # left gutter for biome name
PAD = 6
HEAD = 30          # top strip for stage labels


def day_night_columns():
    """The round_7 `daynight` arc: the 10 STAGES + a DAY anchor after midday and
    a deep NIGHT anchor at the end. Built locally — the shared STAGES is left
    untouched."""
    cols = list(STAGES)
    mi = next(i for i, (lbl, _ph) in enumerate(cols) if lbl == "midday")
    cols.insert(mi + 1, ("day", 0.15))
    cols.append(("night", 0.74))
    return cols


# ── sky swap shim ─────────────────────────────────────────────────────────────
# `_draw_background` calls get_sky_surface_biome(w,h,ground_y,palette,bucket)
# twice and blends; we ignore the live palette/bucket and return the current
# cell's pre-baked design sky. A fresh copy each call because _draw_background
# mutates set_alpha on the returned surface.
_CUR = {"spec": None, "phase": 0.0}
_sky_cache = {}


def _design_sky_shim(w, h, ground_y, palette, phase_bucket):
    spec = _CUR["spec"]
    key = (id(spec), _CUR["phase"])
    surf = _sky_cache.get(key)
    if surf is None:
        surf = pygame.Surface((W, H))
        paint_sky(surf, spec, W, H, _CUR["phase"], stars=True, ground_y=GROUND_Y)
        _sky_cache[key] = surf
    return surf.copy()


def build_gameplay_frame(seconds=7.0):
    """Seeded sim that flaps through gaps until it has a believable score + an
    on-screen coin, so the frozen frame shows real gameplay. Returns (app, world)
    advanced to that frame; not updated further, so every cell shares one layout."""
    def run(seed):
        random.seed(seed)
        app = App()
        if hasattr(app, "_splash_covering"):
            app._splash_covering = False
        w = World()
        w.ready_t = 0.0
        w.flap()
        app.world = w
        app.state = STATE_PLAY
        dt = 1 / 60
        for _ in range(int(seconds / dt)):
            target = H * 0.45
            ahead = [p for p in w.pipes if p.x > w.bird.x - 18]
            if ahead:
                target = min(ahead, key=lambda p: p.x).gap_y - 12
            if w.bird.y > target:
                w.flap()
            w.update(dt)
            if w.game_over:
                break
        return app, w

    best = None
    for seed in range(40):
        app, w = run(seed)
        on_screen_coin = any(0 < c.x < W for c in w.coins)
        if not w.game_over and w.score >= 3 and on_screen_coin:
            best = (app, w)
            break
        if best is None and not w.game_over and w.score >= 2:
            best = (app, w)
    if best is None:
        best = (app, w)
    return best


def main():
    cols = day_night_columns()
    rows = CATALOG
    app, world = build_gameplay_frame()
    # Freeze animation so only sky + time-of-day vary across the grid.
    app._cloud_phase = 0.0
    if hasattr(app, "_cloud_variant"):
        app._cloud_variant = 0

    scenes.get_sky_surface_biome = _design_sky_shim  # the swap

    n, c = len(rows), len(cols)
    sheet_w = GUT + PAD + c * (TW + PAD)
    sheet_h = HEAD + PAD + n * (TH + PAD)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))

    f_head = pygame.font.SysFont("dejavusans", 15, bold=True)
    f_name = pygame.font.SysFont("dejavusans", 13, bold=True)
    f_tag = pygame.font.SysFont("dejavusans", 10)

    sheet.blit(f_head.render(
        "SKY DESIGNS x GAMEPLAY — 10 designs x day/night stages "
        "(sky swapped; live foreground per phase)", True, (240, 240, 245)),
        (GUT + PAD, 7))

    for ci, (label, _ph) in enumerate(cols):
        x = GUT + PAD + ci * (TW + PAD)
        lbl = f_name.render(label, True, (250, 230, 180))
        sheet.blit(lbl, (x + (TW - lbl.get_width()) // 2, HEAD - 15))

    for ri, (design_id, name, _note, _fn) in enumerate(rows):
        y = HEAD + PAD + ri * (TH + PAD)
        _CUR["spec"] = BIOMES[design_id]
        nm = f_name.render(name, True, (245, 245, 250))
        sheet.blit(nm, (8, y + TH // 2 - 8))
        for ci, (label, phase) in enumerate(cols):
            x = GUT + PAD + ci * (TW + PAD)
            _CUR["phase"] = phase
            world.biome_time = phase * CYCLE_SECONDS
            app._render()
            tile = pygame.transform.smoothscale(app.screen, (TW, TH))
            sheet.blit(tile, (x, y))
            tag = f_tag.render(label, True, (245, 245, 245))
            bg = pygame.Surface((tag.get_width() + 6, tag.get_height() + 2), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 140))
            sheet.blit(bg, (x + 3, y + 3))
            sheet.blit(tag, (x + 6, y + 4))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print(f"wrote {OUT}  ({sheet.get_width()}x{sheet.get_height()}, "
          f"{n} rows x {c} cols)")


if __name__ == "__main__":
    main()
