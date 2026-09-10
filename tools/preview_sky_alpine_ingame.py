"""Headless IN-GAME sheet for the Alpine sunset study — HONEST TIME AXIS.

Same rows + same evenly-time-spaced columns as `tools/preview_sky_alpine_sunsets.py`,
but every cell is a real engine frame: the candidate sky baked through the live
`game.biome_sky` gradient, then the actual in-game **mountains + pagodas**
(phase-driven), the empty sandstone **ground/sidewalk**, and the **parrot**
composited over it exactly as `App._draw_background` does.

The columns are sampled at EQUAL TIME STEPS across one full cycle (phase =
t / CYCLE_SECONDS, real gameplay seconds), so the width given to day / sunset /
night honestly reflects how long each lasts — not how many stage phases were
hand-picked. A stage-name ribbon marks where each named stage truly falls; each
column is labelled with elapsed time (m:ss) and an approximate pillar count.

Omitted so the figure stays about the sky+terrain palette: pillars, coins,
power-ups, weather, HUD, and the promenade people/props (the sidewalk is drawn
but empty). Pagodas DO retint across the day (they key off `world.biome_phase`).

Dev aid only; the game never imports this and `ACTIVE_SKY_DESIGN` stays untouched.
Output: docs/biome_redesign/alpine_sunsets_v3_ingame_timeaxis_balanced.png

    python tools/preview_sky_alpine_ingame.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()

import game.scenes as scenes                       # noqa: E402
from game import foreground                         # noqa: E402
from game import sky_designs as _sky_designs        # noqa: E402
from game.config import W, H, GROUND_Y             # noqa: E402
from game.scenes import App, STATE_PLAY            # noqa: E402
from game.world import World                       # noqa: E402
from game.biome_sky import paint_sky               # noqa: E402
from tools.sky_alpine_sunsets import CONCEPTS      # noqa: E402

# Force the live-bake path so our per-cell sky shim is the only sky source.
_sky_designs.ACTIVE_SKY_DESIGN = None

# game/biome.py: phase = t / CYCLE_SECONDS, so phase IS linear in gameplay time.
CYCLE_SECONDS = 320.0
# Approx seconds per pillar at base scroll: PIPE_SPACING 280 / SCROLL_BASE 160 =
# 1.75 s. Pillar counts are APPROXIMATE (scroll speed ramps over a run); time is
# the exact invariant.
SEC_PER_PILLAR = 280.0 / 160.0
N_COLS = 25                      # one column every 320/25 = 12.8 s
STEP = 1.0 / N_COLS
PHASES = [i * STEP for i in range(N_COLS)]

# Positioned at the NIGHT-BALANCED phases (see _RETIME in sky_alpine_sunsets):
# day compressed, evening descent + dark night hold each ~the same length.
STAGES_REF = [
    ("morning", 0.04), ("midday", 0.12), ("afternoon", 0.20), ("golden", 0.27),
    ("sunset", 0.37), ("dusk", 0.47), ("twilight", 0.52), ("night", 0.66),
    ("predawn", 0.86), ("dawn", 0.92), ("sunrise", 0.97),
]


def _mmss(phase):
    s = int(round(phase * CYCLE_SECONDS))
    return f"{s // 60}:{s % 60:02d}"


def _pillars(phase):
    return int(round(phase * CYCLE_SECONDS / SEC_PER_PILLAR))


# Native frame downscaled so the full 25-column cycle fits.
TILE_H = 250
TILE_SCALE = TILE_H / H
TW, TH = int(W * TILE_SCALE), int(H * TILE_SCALE)
GUT = 210
HEAD = 96
PAD = 4


# ── per-cell sky swap ─────────────────────────────────────────────────────────
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


f_title = pygame.font.SysFont("dejavusans", 19, bold=True)
f_sub = pygame.font.SysFont("dejavusans", 12)
f_stage = pygame.font.SysFont("dejavusans", 12, bold=True)
f_axis = pygame.font.SysFont("dejavusans", 11, bold=True)
f_axis2 = pygame.font.SysFont("dejavusans", 10)
f_name = pygame.font.SysFont("dejavusans", 18, bold=True)
f_note = pygame.font.SysFont("dejavusans", 12)


def _wrap(text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.size(trial)[0] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _col_x(phase):
    return GUT + (phase / STEP) * (TW + PAD) + TW / 2


def main():
    # Empty sidewalk: keep the sandstone floor, drop the promenade people/props.
    foreground.draw_promenade = lambda *a, **k: None
    foreground.draw_near_lane = lambda *a, **k: None
    scenes.get_sky_surface_biome = _design_sky_shim

    app = App()
    if hasattr(app, "_splash_covering"):
        app._splash_covering = False
    app._cloud_phase = 0.0
    if hasattr(app, "_cloud_variant"):
        app._cloud_variant = 0

    world = World()
    world.ready_t = 0.0
    world.bird.y = H * 0.42
    app.world = world
    app.state = STATE_PLAY

    cols, rows = PHASES, CONCEPTS
    sheet_w = GUT + len(cols) * (TW + PAD) + PAD
    sheet_h = HEAD + len(rows) * (TH + PAD) + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    sheet.blit(f_title.render(
        "Skybit Alpine — in-game over a full day/night, HONEST TIME + night-balanced timing (v3)",
        True, (245, 246, 250)), (10, 6))
    sheet.blit(f_sub.render(
        "Columns equally spaced in real gameplay time (phase = t/320 s). "
        "One cycle = 320 s (5:20); each column = 12.8 s. Width per stage = how "
        "long it truly lasts. ~p = approx pillars at base speed (1.75 s/pillar; "
        "faster as the run speeds up). Mountains + pagodas + parrot; empty walk.",
        True, (185, 188, 198)), (10, 28))

    for i, (nm, ph) in enumerate(STAGES_REF):
        x = _col_x(ph)
        yy = 48 if i % 2 == 0 else 62
        lbl = f_stage.render(nm, True, (250, 232, 184))
        sheet.blit(lbl, (int(x - lbl.get_width() / 2), yy))
        pygame.draw.line(sheet, (120, 116, 96),
                         (int(x), yy + 14), (int(x), HEAD - 26), 1)

    for c, phase in enumerate(PHASES):
        x = GUT + c * (TW + PAD)
        t = f_axis.render(_mmss(phase), True, (236, 238, 244))
        sheet.blit(t, (x + (TW - t.get_width()) // 2, HEAD - 25))
        p = f_axis2.render(f"~{_pillars(phase)}p", True, (150, 160, 175))
        sheet.blit(p, (x + (TW - p.get_width()) // 2, HEAD - 13))

    for r, (cid, spec) in enumerate(rows):
        y = HEAD + r * (TH + PAD)
        _CUR["spec"] = spec
        nm = f_name.render(spec.name, True, (248, 248, 252))
        sheet.blit(nm, (10, y + 8))
        ny = y + 8 + nm.get_height() + 6
        for line in _wrap(spec.note, f_note, GUT - 18):
            sheet.blit(f_note.render(line, True, (176, 180, 190)), (10, ny))
            ny += f_note.get_height() + 2
        for c, phase in enumerate(PHASES):
            x = GUT + c * (TW + PAD)
            _CUR["phase"] = phase
            world.biome_time = phase * CYCLE_SECONDS
            app._draw_background(app.screen)
            world.bird.draw(app.screen, 0, 0)
            sheet.blit(pygame.transform.smoothscale(app.screen, (TW, TH)), (x, y))

    out = os.environ.get("SKY_SHEET_OUT") or os.path.join(
        _ROOT, "docs", "biome_redesign",
        "alpine_sunsets_v3_ingame_timeaxis_balanced.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()}, "
          f"{len(rows)} rows x {len(cols)} cols, cell {TW}x{TH})")


if __name__ == "__main__":
    main()
