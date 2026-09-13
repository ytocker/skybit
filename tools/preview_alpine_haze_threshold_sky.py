"""SKY-ONLY threshold-height sweep of the live Coral Ember sky — HONEST TIME AXIS.

Companion to `tools/preview_alpine_haze_threshold.py`: the same six rows
(Original + V1..V5) across the day, but full-tile sky only (no terrain), baked
with the live engine `game.biome_sky.paint_sky` (smoothstep OKLab + stars) — NOT
the figure-only Catmull-Rom. With no mountains occluding the lower dome, the
cool->warm threshold and its descent across the five variants is fully legible,
including the band that sits behind the terrain in-game. A faint dashed line
marks the in-game terrain level (GROUND_Y) so the threshold's height can be read
against where the mountains would cover it.

Output: docs/biome_redesign/alpine_haze_threshold_lower_sky.png

    python tools/preview_alpine_haze_threshold_sky.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y             # noqa: E402
from game.biome_sky import paint_sky               # noqa: E402
from tools.sky_alpine_haze_threshold import VARIANTS  # noqa: E402

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


CH = 320
CW = int(W * CH / H)
GUT = 230
HEAD = 96
PAD = 4
GROUND_FRAC = GROUND_Y / H            # in-game terrain level, as a cell fraction

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
    return GUT + (phase / STEP) * (CW + PAD) + CW / 2


def main():
    rows = VARIANTS
    sheet_w = GUT + len(PHASES) * (CW + PAD) + PAD
    sheet_h = HEAD + len(rows) * (CH + PAD) + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    sheet.blit(f_title.render(
        "Skybit LIVE sky — sunset 'warm threshold' lowered: Original + 5 amounts "
        "(SKY ONLY, HONEST TIME axis)",
        True, (245, 246, 250)), (10, 6))
    sheet.blit(f_sub.render(
        "Same Coral Ember colours every row; only the cool->warm line height "
        "differs (SkyParams positions). Full dome, no terrain. Dashed line = "
        "in-game terrain level (mountains cover below it). Columns = gameplay "
        "time. Watch golden/sunset/dusk: the warm band's top edge sinks each row.",
        True, (185, 188, 198)), (10, 28))

    for i, (nm, ph) in enumerate(STAGES_REF):
        x = _col_x(ph)
        yy = 48 if i % 2 == 0 else 62
        lbl = f_stage.render(nm, True, (250, 232, 184))
        sheet.blit(lbl, (int(x - lbl.get_width() / 2), yy))
        pygame.draw.line(sheet, (120, 116, 96),
                         (int(x), yy + 14), (int(x), HEAD - 26), 1)

    for c, phase in enumerate(PHASES):
        x = GUT + c * (CW + PAD)
        t = f_axis.render(_mmss(phase), True, (236, 238, 244))
        sheet.blit(t, (x + (CW - t.get_width()) // 2, HEAD - 25))
        p = f_axis2.render(f"~{_pillars(phase)}p", True, (150, 160, 175))
        sheet.blit(p, (x + (CW - p.get_width()) // 2, HEAD - 13))

    gy = int(GROUND_FRAC * CH)
    for r, (label, spec) in enumerate(rows):
        y = HEAD + r * (CH + PAD)
        nm = f_name.render(label, True, (248, 248, 252))
        sheet.blit(nm, (10, y + 8))
        ny = y + 8 + nm.get_height() + 6
        for line in _wrap(f"positions={spec.sky.positions}", f_note, GUT - 18):
            sheet.blit(f_note.render(line, True, (176, 180, 190)), (10, ny))
            ny += f_note.get_height() + 2
        for c, phase in enumerate(PHASES):
            x = GUT + c * (CW + PAD)
            tile = pygame.Surface((W, H))
            paint_sky(tile, spec, W, H, phase, stars=True, ground_y=GROUND_Y)
            cell = pygame.transform.smoothscale(tile, (CW, CH))
            # Dashed terrain-level marker so the threshold height reads against
            # where the mountains would occlude it in-game.
            for dx in range(0, CW, 8):
                pygame.draw.line(cell, (235, 235, 245), (dx, gy), (dx + 4, gy), 1)
            sheet.blit(cell, (x, y))

    out = os.environ.get("SKY_SHEET_OUT") or os.path.join(
        _ROOT, "docs", "biome_redesign",
        "alpine_haze_threshold_lower_sky.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()}, "
          f"{len(rows)} rows x {len(PHASES)} cols, cell {CW}x{CH})")


if __name__ == "__main__":
    main()
