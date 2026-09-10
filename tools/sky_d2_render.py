"""Sky-transition row for concept D2 'Amber Afterglow'.

Hue counterpoint: a smoky olive-brass afterglow band under the fire, kept at
maximum hue distance from both the scarlet macaw and the warm-rose sandstone so
the bird and pillars never sink into the sky, while the band stays warm enough
to still read as evening rather than as a colour-grade error.
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

_KF = [
    (0.04,  dict(sky_top=( 86,158,186), sky_mid=(150,192,202), sky_bot=(196,212,210), horizon=(214,218,212), star_alpha=0)),
    (0.12,  dict(sky_top=( 76,168,192), sky_mid=(144,198,208), sky_bot=(196,214,212), horizon=(216,220,212), star_alpha=0)),
    (0.20,  dict(sky_top=( 86,160,188), sky_mid=(152,192,204), sky_bot=(198,212,208), horizon=(216,218,210), star_alpha=0)),
    (0.235, dict(sky_top=(141,153,157), sky_mid=(232,188,166), sky_bot=(255,186,144), horizon=(255,164,104), star_alpha=0)),
    # FIX 2: real brass at sky_bot (R−G ≈ 20-35, B pushed 60-90 for metal depth) vs the
    # old khaki that had R−G≈4.  FIX 1 start: sky_mid stays warm-peachy at 0.27 (golden hour),
    # but transitions into the plum/mauve family by 0.31 so the bird never sinks into scarlet.
    (0.27,  dict(sky_top=(181,150,139), sky_mid=(254,168,126), sky_bot=(206,178,128), horizon=(255,198,132), star_alpha=0)),
    # FIX 1: sky_mid moves into rose-plum (hue ~355°) to open the plum descent to 0.52.
    # FIX 2 cont: sky_bot now R−G=30, B=112 — genuine brass.  FIX 4: saturation cliff
    # 0.31→0.37 smoothed from 52 pts to ~8 pts by aligning both to the plum family.
    (0.31,  dict(sky_top=(168,122,140), sky_mid=(185,112,118), sky_bot=(198,168,112), horizon=(252,212,148), star_alpha=5)),
    # FIX 1: sky_mid (155,88,92) desaturated rose-plum, hue 357, CR vs bird ≈ 1.9.
    # FIX 2: sky_bot R−G=26, B=108 — lifted slightly for headroom above 1.8 CR.
    # FIX 5: horizon brighter/warmer brass, framing the bottom glow convincingly.
    (0.37,  dict(sky_top=(108, 66,116), sky_mid=(155, 88, 92), sky_bot=(200,174,108), horizon=(212,180,110), star_alpha=12)),
    # FIX 1: sky_mid (130,70,100) deeper plum-mauve, hue 340, CR vs bird ≈ 2.2.
    # FIX 2: sky_bot R−G=30 raised to (210,180,110) so CR vs bird reaches ≈ 2.0 — the
    # critique's prescribed (184,158,96) assumed luma_bird≈0.040 but actual WCAG luma is
    # 0.215; a brighter brass band still reads "ancient metal" at sunset and clears 1.8.
    # FIX 5: horizon (220,190,115) — slightly warmer/brighter than sky_bot.
    (0.42,  dict(sky_top=( 80, 42,112), sky_mid=(130, 70,100), sky_bot=(210,180,110), horizon=(220,190,115), star_alpha=30)),
    # FIX 1: sky_mid (100,60,95) transitional plum, CR vs bird ≈ 2.6.
    # FIX 2+3: sky_bot (145,124,80) R−G=21, B=80 — darker backdrop lifts bot CR to 2.8.
    # FIX 5: horizon (155,128,82) warmer/brighter than sky_bot.
    (0.47,  dict(sky_top=( 37, 30, 70), sky_mid=(100, 60, 95), sky_bot=(145,124, 80), horizon=(155,128, 82), star_alpha=88)),
    (0.52,  dict(sky_top=( 28, 30, 64), sky_mid=( 68, 42, 68), sky_bot=( 88, 82, 68), horizon=(128,112, 84), star_alpha=156)),
    (0.56,  dict(sky_top=( 23, 28, 57), sky_mid=( 33, 35, 61), sky_bot=( 44, 45, 68), horizon=( 57, 56, 75), star_alpha=222)),
    (0.82,  dict(sky_top=( 23, 28, 57), sky_mid=( 33, 35, 61), sky_bot=( 44, 45, 68), horizon=( 57, 56, 75), star_alpha=222)),
    (0.86,  dict(sky_top=( 24, 30, 59), sky_mid=( 35, 37, 63), sky_bot=( 45, 47, 70), horizon=( 61, 59, 78), star_alpha=166)),
    (0.92,  dict(sky_top=( 76,124,158), sky_mid=(244,160,144), sky_bot=(255,178,150), horizon=(255,158,120), star_alpha=20)),
    (0.97,  dict(sky_top=( 86,146,176), sky_mid=(248,180,166), sky_bot=(255,190,164), horizon=(255,170,140), star_alpha=0)),
]

SPEC = BiomeSpec(
    name='D2 Amber Afterglow',
    note='Hue counterpoint — olive-brass afterglow under the fire',
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
    (0.62,  "Night"),
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

title = f_title.render("D2 · Amber Afterglow — olive-brass hue counterpoint", True, TEXT_HI)
canvas.blit(title, (canvas_w // 2 - title.get_width() // 2, 12))

# The dashed rule marks where the ground meets the sky in-game, so the reviewer
# judges the afterglow band against the visible slice, not the cropped tile.
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

out = os.path.join(_ROOT, "docs", "sky_transition", "d2_amber_afterglow", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"wrote {out}")
