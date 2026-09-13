"""ALPINE_HAZE fine-tune vD_ember_fade — night creeps up from the horizon.

Only sky_bot and horizon differ from live ALPINE_HAZE at phases 0.42–0.52.

    python tools/sky_vD_ember_fade_render.py

Output: docs/sky_transition/vD_ember_fade/round_2.png
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


# Surgical fine-tune: every other channel of the live spec (sky_top, sky_mid,
# star_alpha, SkyParams, all non-sunset-arc phases) is inherited untouched, so
# any visual delta on the sheet is attributable to these three stops alone.
#
# The base progressively abandons sky_mid for sky_top: at 0.42 it is still the
# rose of the mid band (a touch darker, blue lifted), by 0.47 it sits halfway to
# the indigo above it, and by 0.52 it has all but joined it. Reading the strip
# bottom-up, night therefore arrives at the horizon before it arrives overhead,
# which is both the dramatic read we want and how dusk actually behaves once the
# sun is below the horizon line.
#
# Round 2 retunes the two outer stops. 0.42 was bright enough to flatten the
# gradient against sky_mid and to crowd the bird's red silhouette, so it drops
# to a ~39% falloff that both restores the vertical read and clears the
# contrast gate. 0.52 rises slightly so the late-dusk base never sinks below
# the 0.56 night floor — night should be the darkest thing on the strip. 0.47
# is the anchor of the whole ramp and is deliberately untouched.
_OVERRIDES = {
    0.42: dict(sky_bot=(174, 52, 106), horizon=(185, 58, 112)),
    0.47: dict(sky_bot=( 74, 44,  78), horizon=( 90, 50,  76)),
    0.52: dict(sky_bot=( 44, 42,  70), horizon=( 50, 45,  72)),
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
    name='alpine_haze_vD_ember_fade',
    note='vD ember fade - base pulls from rose to indigo, night bleeds up from the horizon',
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

    title = f_title.render("vD_ember_fade v2 (round 2) — night bleeds up from the horizon", True, TEXT_HI)
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

    out = os.path.join(_ROOT, "docs", "sky_transition", "vD_ember_fade", "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print(f"wrote {out}  ({canvas.get_width()}×{canvas.get_height()})")


if __name__ == "__main__":
    main()
