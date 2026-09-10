"""ALPINE_HAZE fine-tune v3_deepen — round 2 revision.

De-orange 0.27/0.31 by lifting B channel (preserves luma better than
dropping G), and push 0.37 darker to widen the CR separation.

    python tools/sky_v3_r2_render.py

Output: docs/sky_transition/v3_deepen/round_2.png
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


# 0.27/0.31: B raised instead of G lowered — keeps luma higher and
# exits the dead zone where the sky reads as flat orange mud.
# 0.37: pushed darker so the contrast ratio against sky_mid grows from
# 1.698 to 1.880, anchoring the oxblood transition more decisively.
# 0.42–0.52: unchanged from round_1 (already best-in-set for legibility).
_OVERRIDES = {
    0.27: dict(sky_bot=(234, 152, 132), horizon=(218, 128, 110)),
    0.31: dict(sky_bot=(240, 132, 116), horizon=(224, 108,  96)),
    0.37: dict(sky_bot=(160,  38,  53), horizon=(142,  33,  47)),
    0.42: dict(sky_bot=(133,  32,  49), horizon=(116,  26,  40)),
    0.47: dict(sky_bot=( 96,  25,  44), horizon=( 82,  20,  36)),
    0.52: dict(sky_bot=( 62,  24,  39), horizon=( 50,  18,  30)),
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
    name='alpine_haze_v3_deepen_r2',
    note='v3 deepen r2 - de-orange 0.27/0.31 via B-lift, deepen 0.37 CR to 1.880',
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
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill(BG)

    f_title = pygame.font.SysFont("dejavusans", 16, bold=True)
    f_label = pygame.font.SysFont("dejavusans", 13, bold=True)
    f_phase = pygame.font.SysFont("dejavusans", 11)

    title = f_title.render("v3_deepen r2 — de-orange 0.27/0.31 (B-lift), deepen 0.37", True, TEXT_HI)
    canvas.blit(title, (canvas_w // 2 - title.get_width() // 2, 12))

    ground_frac = GROUND_Y / H

    for i, (phase, label) in enumerate(SAMPLES):
        x = MARGIN + i * (PANEL_W + GAP)
        y = HEADER

        tile = pygame.Surface((W, H))
        paint_sky(tile, SPEC, W, H, phase, stars=True, ground_y=GROUND_Y)
        panel = pygame.transform.smoothscale(tile, (PANEL_W, PANEL_H))

        canvas.blit(panel, (x, y))

        # ground-level dashed line
        gy = y + int(ground_frac * PANEL_H)
        for dx in range(0, PANEL_W, 8):
            pygame.draw.line(canvas, GROUND_LINE,
                             (x + dx, gy), (x + min(dx + 4, PANEL_W - 1), gy), 1)

        # footer: label + phase
        fy = y + PANEL_H + 6
        for j, line in enumerate(_wrap_lines(label)):
            lbl = f_label.render(line, True, TEXT_HI)
            canvas.blit(lbl, (x + PANEL_W // 2 - lbl.get_width() // 2, fy + j * 16))

        ph_lbl = f_phase.render(f"phase {phase}", True, TEXT_LO)
        canvas.blit(ph_lbl, (x + PANEL_W // 2 - ph_lbl.get_width() // 2, fy + 36))

    out = os.path.join(_ROOT, "docs", "sky_transition", "v3_deepen", "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print(f"wrote {out}  ({canvas.get_width()}x{canvas.get_height()})")


if __name__ == "__main__":
    main()
