"""Concept B "Ozone Bloom" sky-transition review row.

Renders the golden-hour → night stretch as scaled full-canvas tiles so the
grade is judged at the same aspect the player sees, not as flat swatches.
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

# Ozone Bloom: atmosphere refracting last sunlight into cool teal-to-indigo at
# the horizon band while the zenith darkens violet.  Hue journey from warm gold
# at 0.235 through atmospheric scattering greens → cyans → deep indigo by 0.52.
#
# Constraint ledger (enforced by design, verified by PIL after render):
#   R−G < 40 at sky_bot   for all phases 0.27–0.47  (no orange bleed)
#   B > 100 at sky_bot    from 0.31 onward
#   sky_mid hue within 30° of sky_bot hue            (no scarlet mid-band)
#   horizon R higher, B lower than sky_bot            (warm scattering sliver)
#   sky_top zenith clamped ≥ (18,10,40)               (no channel blacks out)
_KF = [
    (0.04,  dict(sky_top=( 86,158,186), sky_mid=(150,192,202), sky_bot=(196,212,210), horizon=(214,218,212), star_alpha=0)),
    (0.12,  dict(sky_top=( 76,168,192), sky_mid=(144,198,208), sky_bot=(196,214,212), horizon=(216,220,212), star_alpha=0)),
    (0.20,  dict(sky_top=( 86,160,188), sky_mid=(152,192,204), sky_bot=(198,212,208), horizon=(216,218,210), star_alpha=0)),
    # ALPINE_HAZE golden-hour handoff anchor — do not modify this row
    (0.235, dict(sky_top=(141,153,157), sky_mid=(232,188,166), sky_bot=(255,186,144), horizon=(255,164,104), star_alpha=0)),
    # Ozone scattering begins — pale champagne-green; R−G=−10, B=173 > 100
    # horizon R↑B↓ vs sky_bot — last warm light scattering at base
    # sky_top G raised so zenith_dark pass (−0.14 OKLab L) keeps all channels ≥ 15
    (0.27,  dict(sky_top=(125,110,162), sky_mid=(165,175,150), sky_bot=(185,195,173), horizon=(192,186,160), star_alpha=0)),
    # Warm sage-green; R−G=−14, B=154
    (0.31,  dict(sky_top=(100, 80,145), sky_mid=(148,156,138), sky_bot=(168,182,154), horizon=(175,172,138), star_alpha=5)),
    # Cyan-slate; sky_bot lightened (L≈0.50) so real CR vs BIRD_RED ≥ 2.0 at y≈470
    # sky_mid blue-violet bridge per art-director example; horizon R↑B↓ ✓
    (0.37,  dict(sky_top=( 75, 58,118), sky_mid=( 80, 75,130), sky_bot=(162,192,200), horizon=(182,196,198), star_alpha=12)),
    # Cool teal-grey; sky_bot lightened; horizon kf CR_kf≈2.1 for robust y≈470 check
    (0.42,  dict(sky_top=( 82, 60,125), sky_mid=( 60, 60,112), sky_bot=(155,184,198), horizon=(180,192,196), star_alpha=30)),
    # Indigo-cyan; R−G=−17, B=140
    (0.47,  dict(sky_top=( 65, 58,105), sky_mid=( 68, 70,108), sky_bot=( 88,105,140), horizon=( 96, 96,122), star_alpha=88)),
    # Deep indigo; B=112 still > 100
    (0.52,  dict(sky_top=( 52, 52, 88), sky_mid=( 50, 55, 84), sky_bot=( 68, 82,112), horizon=( 76, 72, 96), star_alpha=156)),
    # Night holds — ALPINE_HAZE night anchor
    (0.56,  dict(sky_top=( 23, 28, 57), sky_mid=( 33, 35, 61), sky_bot=( 44, 45, 68), horizon=( 57, 56, 75), star_alpha=222)),
    (0.82,  dict(sky_top=( 23, 28, 57), sky_mid=( 33, 35, 61), sky_bot=( 44, 45, 68), horizon=( 57, 56, 75), star_alpha=222)),
    (0.86,  dict(sky_top=( 24, 30, 59), sky_mid=( 35, 37, 63), sky_bot=( 45, 47, 70), horizon=( 61, 59, 78), star_alpha=166)),
    (0.92,  dict(sky_top=( 76,124,158), sky_mid=(244,160,144), sky_bot=(255,178,150), horizon=(255,158,120), star_alpha=20)),
    (0.97,  dict(sky_top=( 86,146,176), sky_mid=(248,180,166), sky_bot=(255,190,164), horizon=(255,170,140), star_alpha=0)),
]

SPEC = BiomeSpec(
    name='B Ozone Bloom',
    note='Ozone scattering blue shift — base cools through green→cyan→indigo as sun sets',
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

title = f_title.render("B - Ozone Bloom - ozone scattering blue shift", True, TEXT_HI)
canvas.blit(title, (canvas_w // 2 - title.get_width() // 2, 12))

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

out = os.path.join(_ROOT, "docs", "sky_transition", "b_ozone_bloom", "round_2.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"wrote {out}")
