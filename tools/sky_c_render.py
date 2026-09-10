"""Sky-transition row for concept C 'Ember Core'.

Renders the raw sky gradient only (no ridges/ground/game elements) so the
evening arc can be judged on colour alone. Upper sky (sky_top/sky_mid/
star_alpha) is taken verbatim from the live `_ALPINE_HAZE_KF` — this concept
only re-designs sky_bot/horizon, so holding the rest fixed keeps the diff
legible against the shipped sky.

The inversion this concept tests: horizon stays lighter and warmer than the
sky_bot above it, so the base of the dome reads as coals seen through ash
rather than the usual darker-toward-the-ground falloff.
"""

import os, sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
import pygame

pygame.init()
pygame.display.set_mode((1, 1))
from game.biome_sky import BiomeSpec, SkyParams, paint_sky
from game.config import W, H, GROUND_Y

# Day anchors (0.04/0.12/0.20) and the whole night/dawn tail are the live
# palette byte-for-byte; only the sunset arc's sky_bot/horizon are redesigned,
# so the concept re-joins the shipped cycle exactly at 0.56.
#
# 0.545 is an extra waypoint this concept alone needs: the ember horizon is
# still well above the night values at 0.52, and interpolating that straight
# into 0.56 snaps the warm base out in one step. The half-way stop bleeds the
# glow down so the landing on night reads continuous. Its upper-sky values are
# pass-through — sampled off the live 0.52→0.56 ramp so the extra stop changes
# nothing above the horizon band.
_KF = [
    (0.04,  dict(sky_top=( 86,158,186), sky_mid=(150,192,202), sky_bot=(196,212,210), horizon=(214,218,212), star_alpha=0)),
    (0.12,  dict(sky_top=( 76,168,192), sky_mid=(144,198,208), sky_bot=(196,214,212), horizon=(216,220,212), star_alpha=0)),
    (0.20,  dict(sky_top=( 86,160,188), sky_mid=(152,192,204), sky_bot=(198,212,208), horizon=(216,218,210), star_alpha=0)),
    (0.235, dict(sky_top=(141,153,157), sky_mid=(232,188,166), sky_bot=(255,186,144), horizon=(255,164,104), star_alpha=0)),
    # FIX 1/2: sky_bot shifted to hue 355–5 dark ember-coal (value 38–65%); no
    # orange. FIX 4: sky_mid pulled down at 0.37–0.47 so mid→bot value delta stays
    # continuous (< 20 HSV-% points per panel). Horizon set slightly brighter/
    # warmer than sky_bot so the ash-coal glow reads through.
    (0.27,  dict(sky_top=(181,150,139), sky_mid=(254,168,126), sky_bot=(155, 66, 63), horizon=(175, 74, 68), star_alpha=0)),
    (0.31,  dict(sky_top=(168,122,140), sky_mid=(250,138,100), sky_bot=(155, 66, 70), horizon=(171, 70, 70), star_alpha=5)),
    (0.37,  dict(sky_top=(108, 66,116), sky_mid=(120, 55,100), sky_bot=(151, 59, 71), horizon=(165, 65, 74), star_alpha=12)),
    (0.42,  dict(sky_top=( 80, 42,112), sky_mid=(100, 48, 90), sky_bot=(131, 63, 80), horizon=(143, 68, 82), star_alpha=30)),
    (0.47,  dict(sky_top=( 37, 30, 70), sky_mid=( 80, 42, 78), sky_bot=(108, 61, 83), horizon=(120, 66, 87), star_alpha=88)),
    (0.52,  dict(sky_top=( 28, 30, 64), sky_mid=( 68, 42, 68), sky_bot=( 81, 52, 71), horizon=(110, 70, 88), star_alpha=156)),
    (0.545, dict(sky_top=( 24, 28, 59), sky_mid=( 44, 37, 63), sky_bot=( 78, 62, 80), horizon=(104, 80, 96), star_alpha=201)),
    (0.56,  dict(sky_top=( 23, 28, 57), sky_mid=( 33, 35, 61), sky_bot=( 44, 45, 68), horizon=( 57, 56, 75), star_alpha=222)),
    (0.82,  dict(sky_top=( 23, 28, 57), sky_mid=( 33, 35, 61), sky_bot=( 44, 45, 68), horizon=( 57, 56, 75), star_alpha=222)),
    (0.86,  dict(sky_top=( 24, 30, 59), sky_mid=( 35, 37, 63), sky_bot=( 45, 47, 70), horizon=( 61, 59, 78), star_alpha=166)),
    (0.92,  dict(sky_top=( 76,124,158), sky_mid=(244,160,144), sky_bot=(255,178,150), horizon=(255,158,120), star_alpha=20)),
    (0.97,  dict(sky_top=( 86,146,176), sky_mid=(248,180,166), sky_bot=(255,190,164), horizon=(255,170,140), star_alpha=0)),
]

SPEC = BiomeSpec(
    name='C Ember Core',
    note='Value inversion - horizon lighter than sky_bot, glowing ember from below',
    keyframes=_KF,
    sky=SkyParams(positions=(0.0, 0.30, 0.58, 0.82, 1.0), dither_amp=1.8, zenith_dark=0.14, descent_drop=0.20),
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
    (0.545, "Dusk settle"),
]

PANEL_W, PANEL_H = 160, 440
GAP, MARGIN, HEADER, FOOTER = 8, 14, 44, 56
BG = (8, 8, 20)
TEXT_HI, TEXT_LO = (245, 246, 250), (170, 175, 190)
GROUND_LINE = (60, 65, 80)

n = len(SAMPLES)
canvas_w = MARGIN * 2 + n * PANEL_W + (n - 1) * GAP
canvas_h = HEADER + PANEL_H + FOOTER
canvas = pygame.Surface((canvas_w, canvas_h))
canvas.fill(BG)

f_title = pygame.font.SysFont("dejavusans", 15, bold=True)
f_label = pygame.font.SysFont("dejavusans", 13, bold=True)
f_phase = pygame.font.SysFont("dejavusans", 11)

title = f_title.render("C - Ember Core - horizon glows from below", True, TEXT_HI)
canvas.blit(title, (canvas_w // 2 - title.get_width() // 2, 12))

# Dashed marker where the ground would sit, so the low band is read at the
# height the player actually sees it.
ground_frac = GROUND_Y / H
for i, (phase, label) in enumerate(SAMPLES):
    x = MARGIN + i * (PANEL_W + GAP)
    y = HEADER
    tile = pygame.Surface((W, H))
    paint_sky(tile, SPEC, W, H, phase, stars=True, ground_y=GROUND_Y)
    panel = pygame.transform.smoothscale(tile, (PANEL_W, PANEL_H))
    canvas.blit(panel, (x, y))
    gy = y + int(ground_frac * PANEL_H)
    for dx in range(0, PANEL_W, 8):
        pygame.draw.line(canvas, GROUND_LINE, (x + dx, gy), (x + min(dx + 4, PANEL_W - 1), gy), 1)
    fy = y + PANEL_H + 6
    for j, line in enumerate(label.split("\n")):
        lbl = f_label.render(line, True, TEXT_HI)
        canvas.blit(lbl, (x + PANEL_W // 2 - lbl.get_width() // 2, fy + j * 16))
    ph_lbl = f_phase.render(f"phase {phase}", True, TEXT_LO)
    canvas.blit(ph_lbl, (x + PANEL_W // 2 - ph_lbl.get_width() // 2, fy + 36))

out = os.path.join(_ROOT, "docs", "sky_transition", "c_ember_core", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"wrote {out}")
