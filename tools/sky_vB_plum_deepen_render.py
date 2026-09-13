"""ALPINE_HAZE fine-tune vB_plum_deepen — base settles into a cooler rose-plum.

Only sky_bot and horizon differ from live ALPINE_HAZE, and only across the
three sunset-arc phases where the live base reads orange against the rose
mid above it. The golden-hour stops (0.27–0.37) are deliberately left alone:
their warmth is on-brand, so widening the override there would trade a real
hue clash for a taste change.

    python tools/sky_vB_plum_deepen_render.py

Output: docs/sky_transition/vB_plum_deepen/round_2.png
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


# Every sky_bot sits well below its own sky_mid in luminance and carries Blue
# a clear 38–49 points above Green. That B-over-G margin is the whole point of
# this variant: a narrower one collapses back into the live rose base, and a
# straight darkening of sky_mid would read flat rather than plum. The arc also
# rotates as it falls — Red still leads Blue at 0.42, they meet at 0.47, and
# Blue overtakes Red by 0.52, so dusk lands on violet-plum instead of oxblood.
# Horizon trails each base a step brighter and warmer so the last band keeps a
# sunset accent, and the 0.42 base holds ~1.75:1 against BIRD_RED so the parrot
# never sinks into it.
_OVERRIDES = {
    0.42: dict(sky_bot=(155, 52, 92), horizon=(172, 59, 78)),
    0.47: dict(sky_bot=( 92, 46, 84), horizon=(110, 54, 70)),
    0.52: dict(sky_bot=( 50, 31, 80), horizon=( 66, 40, 66)),
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
    name='alpine_haze_vB_plum_deepen',
    note='vB plum deepen - base settles into a cooler rose-plum, jewel-toned rather than orange',
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
PANEL_H = 440       # tall enough to show the full sky gradient
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
        "vB_plum_deepen (round 2) — warm rose zenith sinking into a deep violet-plum base "
        "(sky_bot + horizon, phases 0.42 / 0.47 / 0.52 only)", True, TEXT_HI)
    canvas.blit(title, (canvas_w // 2 - title.get_width() // 2, 12))

    ground_frac = GROUND_Y / H

    for i, (phase, label) in enumerate(SAMPLES):
        x = MARGIN + i * (PANEL_W + GAP)
        y = HEADER

        tile = pygame.Surface((W, H))
        paint_sky(tile, SPEC, W, H, phase, stars=True, ground_y=GROUND_Y)
        panel = pygame.transform.smoothscale(tile, (PANEL_W, PANEL_H))

        canvas.blit(panel, (x, y))

        # the three retuned stops get an accent rule above the panel — the
        # footer has no room left, and a tag over the art would tint the very
        # gradient under review
        if phase in _OVERRIDES:
            pygame.draw.rect(canvas, (255, 214, 150), (x, y - 4, PANEL_W, 3))

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

    out = os.path.join(_ROOT, "docs", "sky_transition", "vB_plum_deepen", "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print(f"wrote {out}  ({canvas.get_width()}×{canvas.get_height()})")


if __name__ == "__main__":
    main()
