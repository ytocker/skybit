"""v2_haze round 2 — diffuse milky haze, CR and hue corrections.

Every untouched key (sky_top, sky_mid, star_alpha) and every untouched phase
inherits the live ALPINE_HAZE spec byte-for-byte.  Only sky_bot and horizon
differ at phases 0.27–0.52, per the art-director's signed-off table.

Output: docs/sky_transition/v2_haze/round_2.png
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
from game.biome_sky import BiomeSpec, paint_sky                     # noqa: E402
from game.config import W, H, GROUND_Y                              # noqa: E402


# Surgical fine-tune: horizon at 0.37 lifted to clear borderline CR; 0.42/0.47
# pushed to milkier/higher-CR values to anchor the haze concept; 0.52 hue-
# corrected so the blue channel no longer strays 36.7° from sky_mid.
_OVERRIDES = {
    0.27: dict(sky_bot=(246, 188, 172), horizon=(242, 170, 162)),
    0.31: dict(sky_bot=(248, 178, 162), horizon=(238, 152, 142)),
    0.37: dict(sky_bot=(248, 155, 148), horizon=(240, 143, 135)),
    0.42: dict(sky_bot=(250, 148, 168), horizon=(250, 130, 152)),
    0.47: dict(sky_bot=(240, 150, 178), horizon=(236, 140, 166)),
    0.52: dict(sky_bot=(132, 72, 104),  horizon=(118, 62, 94)),
}

_KF = []
for phase, d in _ALPINE_HAZE_KF:
    if phase in _OVERRIDES:
        new_d = dict(d)
        new_d.update(_OVERRIDES[phase])
        _KF.append((phase, new_d))
    else:
        _KF.append((phase, d))

# SkyParams shared with live spec — stop placement, dither and warm-band
# descent are not part of this fine-tune.
SPEC = BiomeSpec(
    name='alpine_haze_v2_r2',
    note='v2 haze round 2 — milky haze fix: CR-safe 0.42/0.47, hue-corrected 0.52',
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
        "v2_haze r2 — CR fix 0.42/0.47, milky haze stronger, hue correction 0.52",
        True, TEXT_HI,
    )
    canvas.blit(title, (canvas_w // 2 - title.get_width() // 2, 12))

    ground_frac = GROUND_Y / H

    for i, (phase, label) in enumerate(SAMPLES):
        x = MARGIN + i * (PANEL_W + GAP)
        y = HEADER

        tile = pygame.Surface((W, H))
        paint_sky(tile, SPEC, W, H, phase, stars=True, ground_y=GROUND_Y)
        panel = pygame.transform.smoothscale(tile, (PANEL_W, PANEL_H))

        canvas.blit(panel, (x, y))

        # ground-level dashed line so the sky/terrain boundary is visible
        gy = y + int(ground_frac * PANEL_H)
        for dx in range(0, PANEL_W, 8):
            pygame.draw.line(canvas, GROUND_LINE,
                             (x + dx, gy), (x + min(dx + 4, PANEL_W - 1), gy), 1)

        # footer: label + phase
        fy = y + PANEL_H + 6
        for j, line in enumerate(_wrap_lines(label)):
            lbl = f_label.render(line, True, TEXT_HI)
            canvas.blit(lbl, (x + PANEL_W // 2 - lbl.get_width() // 2, fy + j * 16))

        ph_lbl = f_phase.render(f"phase {phase:.2f}", True, TEXT_LO)
        canvas.blit(ph_lbl, (x + PANEL_W // 2 - ph_lbl.get_width() // 2, fy + 36))

    out = os.path.join(_ROOT, "docs", "sky_transition", "v2_haze", "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print(f"wrote {out}  ({canvas.get_width()}x{canvas.get_height()})")


if __name__ == "__main__":
    main()
