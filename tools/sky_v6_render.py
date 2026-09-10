"""ALPINE_HAZE fine-tune v6_chroma_drop — sunset seen through high-altitude dust.

Only sky_bot and horizon differ from live ALPINE_HAZE at phases 0.27–0.52.
Note: at phases 0.37 and 0.42, sky_bot luminance is in the bird's dead zone
(CR ~1.0–1.3); the hero reads via saturation contrast, not luminance.

    python tools/sky_v6_render.py

Output: docs/sky_transition/v6_chroma_drop/round_1.png
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


# Surgical fine-tune: every untouched key (sky_top, sky_mid, star_alpha) and
# every untouched phase inherits the live spec, so the diff stays readable and
# the day/night ends of the cycle are byte-identical to what already ships.
_OVERRIDES = {
    0.27: dict(sky_bot=(224, 179, 157), horizon=(238, 210, 191)),
    0.31: dict(sky_bot=(204, 158, 143), horizon=(217, 187, 173)),
    0.37: dict(sky_bot=(183, 136, 132), horizon=(189, 161, 155)),
    0.42: dict(sky_bot=(161, 119, 126), horizon=(169, 142, 144)),
    0.47: dict(sky_bot=(93, 70, 78), horizon=(108, 93, 97)),
    0.52: dict(sky_bot=(59, 46, 59), horizon=(78, 69, 77)),
}

_KF = []
for phase, d in _ALPINE_HAZE_KF:
    if phase in _OVERRIDES:
        new_d = dict(d)
        new_d.update(_OVERRIDES[phase])
        _KF.append((phase, new_d))
    else:
        _KF.append((phase, d))

# SkyParams is shared with the live spec on purpose — stop placement, dither and
# the warm-band descent are NOT part of this fine-tune.
SPEC = BiomeSpec(
    name='alpine_haze_v6_chroma_drop',
    note='v6 chroma_drop - same value as sky_mid, saturation drained, aerial haze',
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
        "v6_chroma_drop — high-altitude dust (hero pops by saturation)",
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

        ph_lbl = f_phase.render(f"phase {phase:.2f}", True, TEXT_LO)
        canvas.blit(ph_lbl, (x + PANEL_W // 2 - ph_lbl.get_width() // 2, fy + 36))

    out = os.path.join(_ROOT, "docs", "sky_transition", "v6_chroma_drop",
                       "round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print(f"wrote {out}  ({canvas.get_width()}×{canvas.get_height()})")


if __name__ == "__main__":
    main()
