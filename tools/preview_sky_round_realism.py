"""Headless exploration sheet for the REALISM sky round — HONEST TIME AXIS.

Renders the `tools.sky_round_realism.CONCEPTS` (rows) across the full day/night
cycle (columns), sky-only via the smoother Catmull-Rom `paint_sky` (stars kept
on), into `docs/biome_redesign/round_realism_1.png`.

The columns are sampled at EQUAL TIME STEPS across one full cycle, not at hand-
picked stage phases. The biome cycle is `phase = t / CYCLE_SECONDS` (real
gameplay seconds), so equal phase steps = equal wall-clock time, and the screen
width given to day / sunset / night reflects how long each ACTUALLY lasts — the
whole point of the realism brief's lopsided clock (30% day, 22% held night). A
stage-name ribbon marks where each named stage truly falls; each column is
labelled with elapsed time (m:ss) and an approximate pillar count.

Dev aid only — the game never imports this; `ACTIVE_SKY_DESIGN` is untouched.

    python tools/preview_sky_round_realism.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y          # noqa: E402
from game import biome_sky_field as sf          # noqa: E402
from game.biome_sky import _sky_stops, _scatter_stars  # noqa: E402
from tools.sky_round_realism import CONCEPTS     # noqa: E402


# ── smoother sky bake (figure-only) ──────────────────────────────────────────
# The shared engine eases each stop segment with smoothstep, which flattens the
# gradient to a near-zero slope at every interior stop. Those plateaus span tall
# bands of rows that quantize to the same 8-bit colour, so the eye reads a hard
# horizontal contour at each stop. A Catmull-Rom pass through the OKLab stops has
# a continuous non-zero slope everywhere — no plateaus, no contour lines — and a
# touch more dither dissolves the residual 8-bit steps. Kept here (not in
# game/biome_sky_field) so the live sky path stays byte-for-byte unchanged.
def _catmull_rows(stops, n):
    st = sorted(stops, key=lambda s: s[0])
    P = [sf.srgb_to_oklab(c) for _, c in st]
    pos = [p for p, _ in st]
    out = []
    for i in range(n):
        u = i / max(1, n - 1)
        seg = 0
        while seg < len(pos) - 2 and u > pos[seg + 1]:
            seg += 1
        p0, p1 = pos[seg], pos[seg + 1]
        span = p1 - p0 if p1 > p0 else 1e-6
        t = min(1.0, max(0.0, (u - p0) / span))
        P1, P2 = P[seg], P[seg + 1]
        P0 = P[seg - 1] if seg - 1 >= 0 else P[seg]
        P3 = P[seg + 2] if seg + 2 < len(P) else P[seg + 1]
        c = tuple(
            0.5 * ((2 * P1[k])
                   + (-P0[k] + P2[k]) * t
                   + (2 * P0[k] - 5 * P1[k] + 4 * P2[k] - P3[k]) * t * t
                   + (-P0[k] + 3 * P1[k] - 3 * P2[k] + P3[k]) * t * t * t)
            for k in range(3)
        )
        out.append(sf.oklab_to_srgb(c))
    return out


def paint_sky(tile, spec, w, h, phase, stars=True, ground_y=None):
    """Sky-only bake with the smoother Catmull-Rom ramp + a little extra dither."""
    pal = spec.palette_for_phase(phase)
    stops = _sky_stops(spec, pal)
    for y, col in enumerate(_catmull_rows(stops, h)):
        pygame.draw.line(tile, col, (0, y), (w - 1, y))
    amp = max(spec.sky.dither_amp, 3.0)
    pos, neg = sf._dither_overlays(w, h, amp)
    tile.blit(pos, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    tile.blit(neg, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    if stars:
        sa = int(pal.get('star_alpha', 0))
        if sa > 0:
            _scatter_stars(tile, w, ground_y or h, sa)


# ── honest time axis ─────────────────────────────────────────────────────────
# game/biome.py: phase = t / CYCLE_SECONDS, so phase IS linear in gameplay time.
CYCLE_SECONDS = 320.0
# Approx seconds per pillar at base scroll: PIPE_SPACING 280 px / SCROLL_BASE
# 160 px/s = 1.75 s. Pillars/cycle and the per-column counts are APPROXIMATE —
# the scroll speed ramps over a run, so later pillars arrive faster. Time is the
# exact invariant; pillars are a rough gameplay-feel reference only.
SEC_PER_PILLAR = 280.0 / 160.0
N_COLS = 25                      # one column every 320/25 = 12.8 s
STEP = 1.0 / N_COLS
PHASES = [i * STEP for i in range(N_COLS)]

# Named stages at their TRUE phase on the SHARED REALISTIC CLOCK, drawn as a
# ribbon so the layout shows where each falls in real time (and how wide a slice
# of the cycle it occupies). These match the realism brief's lopsided clock:
# 30% held day, a short golden/sunset, the Belt-of-Venus blue hour, then a long
# 22% held night before a slightly quicker dawn.
STAGES_REF = [
    ("morning", 0.05), ("midday", 0.16), ("afternoon", 0.27), ("golden", 0.33),
    ("sunset", 0.39), ("blue-hour", 0.47), ("twilight", 0.55), ("night", 0.70),
    ("predawn", 0.86), ("dawn", 0.91), ("sunrise", 0.97),
]


def _mmss(phase):
    s = int(round(phase * CYCLE_SECONDS))
    return f"{s // 60}:{s % 60:02d}"


def _pillars(phase):
    return int(round(phase * CYCLE_SECONDS / SEC_PER_PILLAR))


CW, CH = 150, 266            # narrower cells so the full 25-column cycle fits
GUT = 210                    # left gutter for concept name
HEAD = 96                    # top strip: title + legend + stage ribbon + axis
PAD = 4

f_title = pygame.font.SysFont("dejavusans", 19, bold=True)
f_sub = pygame.font.SysFont("dejavusans", 12)
f_stage = pygame.font.SysFont("dejavusans", 12, bold=True)
f_axis = pygame.font.SysFont("dejavusans", 11, bold=True)
f_axis2 = pygame.font.SysFont("dejavusans", 10)
f_name = pygame.font.SysFont("dejavusans", 18, bold=True)
f_note = pygame.font.SysFont("dejavusans", 12)


def _wrap(text, font, max_w):
    words = text.split()
    lines, cur = [], ""
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
    """Pixel centre of where `phase` lands on the evenly-time-spaced axis."""
    return GUT + (phase / STEP) * (CW + PAD) + CW / 2


def main():
    cols = len(PHASES)
    rows = len(CONCEPTS)
    sheet_w = GUT + cols * (CW + PAD) + PAD
    sheet_h = HEAD + rows * (CH + PAD) + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    sheet.blit(f_title.render(
        "Skybit Realism Round — full day/night on the HONEST TIME axis (warm low / cool high)",
        True, (245, 246, 250)), (10, 6))
    sheet.blit(f_sub.render(
        "Columns are equally spaced in real gameplay time (phase = t/320 s). "
        "One full cycle = 320 s (5:20); each column = 12.8 s. "
        "Width per stage = how long it truly lasts (30% day, 22% held night). "
        "~p = approx pillars at base speed (1.75 s/pillar; faster as the run speeds up).",
        True, (185, 188, 198)), (10, 28))

    # Stage-name ribbon at the true phase positions, staggered to avoid overlap,
    # with a tick down toward the grid.
    for i, (nm, ph) in enumerate(STAGES_REF):
        x = _col_x(ph)
        yy = 48 if i % 2 == 0 else 62
        lbl = f_stage.render(nm, True, (250, 232, 184))
        sheet.blit(lbl, (int(x - lbl.get_width() / 2), yy))
        pygame.draw.line(sheet, (120, 116, 96),
                         (int(x), yy + 14), (int(x), HEAD - 26), 1)

    # Per-column axis: elapsed time (m:ss) + approx pillar count.
    for c, phase in enumerate(PHASES):
        x = GUT + c * (CW + PAD)
        t = f_axis.render(_mmss(phase), True, (236, 238, 244))
        sheet.blit(t, (x + (CW - t.get_width()) // 2, HEAD - 25))
        p = f_axis2.render(f"~{_pillars(phase)}p", True, (150, 160, 175))
        sheet.blit(p, (x + (CW - p.get_width()) // 2, HEAD - 13))

    for r, (cid, spec) in enumerate(CONCEPTS):
        y = HEAD + r * (CH + PAD)
        nm = f_name.render(spec.name, True, (248, 248, 252))
        sheet.blit(nm, (10, y + 8))
        ny = y + 8 + nm.get_height() + 6
        for line in _wrap(spec.note, f_note, GUT - 18):
            sheet.blit(f_note.render(line, True, (176, 180, 190)), (10, ny))
            ny += f_note.get_height() + 2
        for c, phase in enumerate(PHASES):
            x = GUT + c * (CW + PAD)
            tile = pygame.Surface((W, H))
            paint_sky(tile, spec, W, H, phase, stars=True, ground_y=GROUND_Y)
            sheet.blit(pygame.transform.smoothscale(tile, (CW, CH)), (x, y))

    out = os.environ.get("SKY_SHEET_OUT") or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "biome_redesign", "round_realism_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()}, "
          f"{rows} rows x {cols} cols, cell {CW}x{CH})")


if __name__ == "__main__":
    main()
