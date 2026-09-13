"""ALPINE_HAZE fine-tune v7_ember_on_dark — round 2: narrowed concept.

The concept identity lives at 0.37–0.52 where ember-on-dark is genuinely strong.
Phases 0.27/0.31 now stay bright (near sky_mid level) so the CR dead zone is
avoided; the hard brightness step from 0.31 → 0.37 is the signature moment when
the ember arrives suddenly.

    python tools/sky_v7_r2_render.py

Output: docs/sky_transition/v7_ember_on_dark/round_2.png
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


# 0.27/0.31 stay bright — sky_bot near sky_mid level so we remain above the
# CR dead zone vs BIRD_RED (luma 0.36–0.43 vs dead zone 0.127–0.348).
# 0.37+ drops hard into ember-on-dark: the sudden brightness cliff is the
# concept signature — the ember moment arrives, not gradual.
# horizon keeps G-B ≈ 50–70 at 0.37+ as a deliberate amber-sliver design mark.
_OVERRIDES = {
    # bright, near sky_mid — ember hasn't arrived yet
    0.27: dict(sky_bot=(232, 158, 116), horizon=(222, 159,  89)),
    0.31: dict(sky_bot=(228, 140, 100), horizon=(217, 145,  82)),
    # ember-on-dark starts here — dark base, thin warm amber sliver at horizon
    0.37: dict(sky_bot=(140,  67,  56), horizon=(160,  88,  62)),
    0.42: dict(sky_bot=(116,  53,  50), horizon=(130,  70,  52)),
    0.47: dict(sky_bot=( 86,  40,  42), horizon=(100,  52,  40)),
    0.52: dict(sky_bot=( 58,  28,  36), horizon=( 68,  38,  32)),
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
    name='alpine_haze_v7_ember_r2',
    note='v7 ember_on_dark r2 — bright at 0.27/0.31, hard cliff into ember-on-dark at 0.37',
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

    title = f_title.render(
        "v7_ember_on_dark r2 — bright 0.27/0.31, ember arrives hard at 0.37",
        True, TEXT_HI)
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

    out = os.path.join(_ROOT, "docs", "sky_transition", "v7_ember_on_dark",
                       "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print(f"wrote {out}  ({canvas.get_width()}x{canvas.get_height()})")


if __name__ == "__main__":
    main()
