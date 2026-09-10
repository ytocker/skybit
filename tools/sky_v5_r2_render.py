"""ALPINE_HAZE fine-tune v5_early_night round_2 — night rises from the ground up.

Fixes from round_1:
- Corrected horizon values (round_1 script had wrong values vs. intent)
- sky_mid dimmed at 0.37/0.42/0.47 to collapse the vivid salmon/red band
  that was sandwiched between the violet dome above and violet ground below
- 0.27/0.31 sky_bot pushed more violet so the concept begins before 0.37
- 0.52 sky_bot corrected to (38,28,60) (round_1 had (41,31,63))

    python tools/sky_v5_r2_render.py

Output: docs/sky_transition/v5_early_night/round_2.png
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

from game.biome_sky_keyframes import _ALPINE_HAZE_KF, ALPINE_HAZE  # noqa: E402
from game.biome_sky import BiomeSpec, paint_sky                    # noqa: E402
from game.config import W, H, GROUND_Y                             # noqa: E402


# Surgical override: sky_top, star_alpha, SkyParams, day anchors, and night hold
# remain unchanged. sky_mid is now also overridden at 0.37–0.47 to suppress the
# bright salmon stripe that floated between the already-violet top and bottom.
# sky_bot at 0.27/0.31 starts trending violet early (G-B goes negative) so the
# "night from below" mood begins a full two keyframes before the dome darkens.
_OVERRIDES = {
    0.27: dict(sky_bot=(240, 150, 158), horizon=(234, 140, 138)),
    0.31: dict(sky_bot=(236, 132, 162), horizon=(228, 116, 138)),
    0.37: dict(sky_mid=(198, 102, 112), sky_bot=(112, 76, 136), horizon=(108, 72, 136)),
    0.42: dict(sky_mid=(178, 80, 110),  sky_bot=(86, 58, 112),  horizon=(76, 50, 106)),
    0.47: dict(sky_mid=(104, 58, 86),   sky_bot=(59, 42, 86),   horizon=(50, 36, 80)),
    0.52: dict(sky_bot=(38, 28, 60),    horizon=(32, 22, 52)),
}

_KF = []
for phase, d in _ALPINE_HAZE_KF:
    if phase in _OVERRIDES:
        new_d = dict(d)
        new_d.update(_OVERRIDES[phase])
        _KF.append((phase, new_d))
    else:
        _KF.append((phase, d))

SPEC = BiomeSpec(
    name='alpine_haze_v5_early_night_r2',
    note='v5 early_night r2 - sky_mid dimmed at 0.37-0.47, violet ground begins at 0.27',
    keyframes=_KF,
    sky=ALPINE_HAZE.sky,
)


SAMPLES = [
    (0.235, "Golden Hour\n(start)"),
    (0.27,  "Golden Hour"),
    (0.31,  "Golden Hour\n(late)"),
    (0.37,  "Sunset"),
    (0.42,  "Sunset\n(deep)"),
    (0.47,  "Dusk"),
    (0.52,  "Dusk (late)"),
    (0.56,  "Twilight"),
    (0.62,  "Night"),
]

PANEL_W = 160
PANEL_H = 440
GAP = 8
MARGIN = 14
HEADER = 44
FOOTER = 56
ROW_W = 1532
ROW_H = 540

BG = (8, 8, 20)
TEXT_HI = (245, 246, 250)
TEXT_LO = (170, 175, 190)
GROUND_LINE = (60, 65, 80)


def _wrap_lines(text):
    return text.split("\n")


def main():
    n = len(SAMPLES)
    canvas_w = MARGIN * 2 + n * PANEL_W + (n - 1) * GAP
    canvas_h = HEADER + PANEL_H + FOOTER
    # Verify expected dimensions match the ROW constants.
    assert canvas_w == ROW_W, f"width mismatch: {canvas_w} != {ROW_W}"
    assert canvas_h == ROW_H, f"height mismatch: {canvas_h} != {ROW_H}"

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(BG)

    f_title = pygame.font.SysFont("dejavusans", 16, bold=True)
    f_label = pygame.font.SysFont("dejavusans", 13, bold=True)
    f_phase = pygame.font.SysFont("dejavusans", 11)

    title = f_title.render(
        "v5_early_night r2 — dim sky_mid 0.37-0.47, violet ground from 0.27", True, TEXT_HI)
    canvas.blit(title, (canvas_w // 2 - title.get_width() // 2, 12))

    ground_frac = GROUND_Y / H

    for i, (phase, label) in enumerate(SAMPLES):
        x = MARGIN + i * (PANEL_W + GAP)
        y = HEADER

        tile = pygame.Surface((W, H))
        paint_sky(tile, SPEC, W, H, phase, stars=True, ground_y=GROUND_Y)
        panel = pygame.transform.smoothscale(tile, (PANEL_W, PANEL_H))

        canvas.blit(panel, (x, y))

        # ground-level dashed line shows where sky meets terrain
        gy = y + int(ground_frac * PANEL_H)
        for dx in range(0, PANEL_W, 8):
            pygame.draw.line(canvas, GROUND_LINE,
                             (x + dx, gy), (x + min(dx + 4, PANEL_W - 1), gy), 1)

        # footer: label + phase value
        fy = y + PANEL_H + 6
        for j, line in enumerate(_wrap_lines(label)):
            lbl = f_label.render(line, True, TEXT_HI)
            canvas.blit(lbl, (x + PANEL_W // 2 - lbl.get_width() // 2, fy + j * 16))

        ph_lbl = f_phase.render(f"phase {phase}", True, TEXT_LO)
        canvas.blit(ph_lbl, (x + PANEL_W // 2 - ph_lbl.get_width() // 2,
                             fy + 36))

    out = os.path.join(_ROOT, "docs", "sky_transition", "v5_early_night", "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print(f"wrote {out}  ({canvas.get_width()}x{canvas.get_height()})")


if __name__ == "__main__":
    main()
