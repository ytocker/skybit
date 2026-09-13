"""IN-GAME threshold-height sweep of the live Coral Ember sky — HONEST TIME AXIS.

Six rows (Original live + V1..V5) of `tools.sky_alpine_haze_threshold.VARIANTS`,
each across one full day on the honest time axis, rendered through the REAL game
path — `App._draw_background → game.sky_designs.render_active` (the two-bucket
OKLab bake + live stars). Each variant is swapped into the live registry slot
per row (`sky_designs.BIOMES['alpine_haze']`, cache cleared) so every row shows
exactly what that threshold height would look like in-game.

Only the sunset "warm threshold" height differs between rows; the Coral Ember
colours are identical. Scene-only to match the prior sheets: mountains + pagodas
+ parrot over the empty sidewalk; no pillars/coins/HUD/people.

Output: docs/biome_redesign/alpine_haze_threshold_lower_ingame.png

    python tools/preview_alpine_haze_threshold.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()

from game import foreground                         # noqa: E402
from game import sky_designs as _sky_designs        # noqa: E402
from game.config import W, H, GROUND_Y             # noqa: E402
from game.scenes import App, STATE_PLAY            # noqa: E402
from game.world import World                       # noqa: E402
from game.biome_sky_keyframes import ALPINE_HAZE   # noqa: E402
from tools.sky_alpine_haze_threshold import VARIANTS  # noqa: E402

# The sweep is rendered through the live design slot, so the design must be live.
assert _sky_designs.ACTIVE_SKY_DESIGN == "alpine_haze", (
    f"expected live ACTIVE_SKY_DESIGN='alpine_haze', got "
    f"{_sky_designs.ACTIVE_SKY_DESIGN!r}")

CYCLE_SECONDS = 320.0
SEC_PER_PILLAR = 280.0 / 160.0
N_COLS = 25
STEP = 1.0 / N_COLS
PHASES = [i * STEP for i in range(N_COLS)]

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


TILE_H = 250
TILE_SCALE = TILE_H / H
TW, TH = int(W * TILE_SCALE), int(H * TILE_SCALE)
GUT = 230
HEAD = 96
PAD = 4

f_title = pygame.font.SysFont("dejavusans", 19, bold=True)
f_sub = pygame.font.SysFont("dejavusans", 12)
f_stage = pygame.font.SysFont("dejavusans", 12, bold=True)
f_axis = pygame.font.SysFont("dejavusans", 11, bold=True)
f_axis2 = pygame.font.SysFont("dejavusans", 10)
f_name = pygame.font.SysFont("dejavusans", 17, bold=True)
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
    foreground.draw_promenade = lambda *a, **k: None
    foreground.draw_near_lane = lambda *a, **k: None

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

    rows = VARIANTS
    sheet_w = GUT + len(PHASES) * (TW + PAD) + PAD
    sheet_h = HEAD + len(rows) * (TH + PAD) + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    sheet.blit(f_title.render(
        "Skybit LIVE sky — sunset 'warm threshold' lowered: Original + 5 amounts "
        "(in-game, HONEST TIME axis, real render path)",
        True, (245, 246, 250)), (10, 6))
    sheet.blit(f_sub.render(
        "Same Coral Ember colours every row; only the height of the cool->warm "
        "line differs (SkyParams positions). Painted via render_active (real "
        "game path). Columns = gameplay time; one cycle = 320 s (5:20). Watch "
        "the golden/sunset/dusk columns: the warm band's top edge sinks each row.",
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

    try:
        for r, (label, spec) in enumerate(rows):
            # Swap this variant into the live design slot and clear the per-bucket
            # sky cache (keyed by design-id, which stays 'alpine_haze') so the next
            # render_active bake uses this row's positions.
            _sky_designs.BIOMES["alpine_haze"] = spec
            _sky_designs._sky_cache.clear()

            y = HEAD + r * (TH + PAD)
            nm = f_name.render(label, True, (248, 248, 252))
            sheet.blit(nm, (10, y + 8))
            ny = y + 8 + nm.get_height() + 6
            for line in _wrap(f"positions={spec.sky.positions}", f_note, GUT - 18):
                sheet.blit(f_note.render(line, True, (176, 180, 190)), (10, ny))
                ny += f_note.get_height() + 2
            for c, phase in enumerate(PHASES):
                x = GUT + c * (TW + PAD)
                world.biome_time = phase * CYCLE_SECONDS
                app._draw_background(app.screen)
                world.bird.draw(app.screen, 0, 0)
                sheet.blit(pygame.transform.smoothscale(app.screen, (TW, TH)), (x, y))
    finally:
        # Restore the real live spec + drop the swapped bakes.
        _sky_designs.BIOMES["alpine_haze"] = ALPINE_HAZE
        _sky_designs._sky_cache.clear()

    out = os.environ.get("SKY_SHEET_OUT") or os.path.join(
        _ROOT, "docs", "biome_redesign",
        "alpine_haze_threshold_lower_ingame.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()}, "
          f"{len(rows)} rows x {len(PHASES)} cols, cell {TW}x{TH})")


if __name__ == "__main__":
    main()
