"""Diagnostic: compare the original biome's day/night schedule against the new
Karst sky schedule on a shared "pillars passed" axis.

Both systems are driven by the SAME global phase clock (phase = biome_time /
CYCLE_SECONDS), so the only thing that differs is WHERE each places its
time-of-day keyframes. Rendering both as stacked sky strips over one full cycle
makes the order/length divergence read at a glance — which is the whole point of
this artifact. Off the live render path (a `tools/` script), so it is fine to
draw with plain Pygame and write a PNG under docs/.
"""
import os
import sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame

from game.draw import lerp_color
from game import biome
from game.biome_sky_keyframes import BIOMES
from game.config import SCROLL_BASE, PIPE_SPACING

# ── timing model ──────────────────────────────────────────────────────────────
# Steady-state normal scroll: one pillar every PIPE_SPACING/SCROLL_BASE seconds.
# The onboarding "newbie" ramp briefly slows early pillars; deliberately ignored
# here so the axis is a clean linear proxy for elapsed cycle time (noted on the
# chart).
SEC_PER_PILLAR = PIPE_SPACING / SCROLL_BASE          # 280 / 160 = 1.75 s
CYCLE = biome.CYCLE_SECONDS                          # 320 s
PILLARS_PER_CYCLE = CYCLE / SEC_PER_PILLAR           # ~182.9

# Keyframe anchors (phase, label). Names live only in source comments, so they
# are restated here alongside their phase markers.
ORIG_ANCHORS = [
    (0.00000, "DAY"), (0.23125, "GOLDEN HR"), (0.36250, "SUNSET"),
    (0.51250, "DUSK"), (0.64375, "NIGHT"), (0.79375, "PREDAWN"),
    (0.90625, "SUNRISE"),
]
KARST_ANCHORS = [
    (0.06, "MORNING"), (0.18, "MIDDAY"), (0.40, "GOLDEN"), (0.50, "SUNSET"),
    (0.62, "DUSK"), (0.70, "NIGHT"), (0.80, "PREDAWN"), (0.94, "SUNRISE"),
]

# ── geometry ──────────────────────────────────────────────────────────────────
LEFT, RIGHT = 196, 36
TOP = 58
PLOT_W = 1120
LABEL_GAP = 104          # rotated phase names hang here, above each band
BAND_H = 150
W = LEFT + PLOT_W + RIGHT

INK = (40, 44, 52)
GRID = (120, 126, 138)

# vertical sky-gradient stops (fraction down the band -> palette key)
STOPS = [(0.0, "sky_top"), (0.40, "sky_mid"), (0.72, "sky_bot"), (1.0, "horizon")]


def col_color(pal, f):
    """Color at fraction f (0=top,1=bottom) down a sky column for palette `pal`."""
    for i in range(len(STOPS) - 1):
        p0, k0 = STOPS[i]
        p1, k1 = STOPS[i + 1]
        if p0 <= f <= p1:
            t = (f - p0) / (p1 - p0) if p1 > p0 else 0.0
            return lerp_color(pal[k0], pal[k1], t)
    return pal["horizon"]


def name_at(anchors, phase):
    """Current keyframe name for a wrapped phase (segment's left anchor)."""
    last = anchors[-1][1]
    for ph, nm in anchors:
        if phase < ph:
            return last
        last = nm
    return last


def draw_band(surf, top_y, palette_fn):
    for col in range(PLOT_W):
        phase = col / PLOT_W
        pal = palette_fn(phase)
        x = LEFT + col
        for row in range(BAND_H):
            surf.set_at((x, top_y + row), col_color(pal, row / (BAND_H - 1)))


def x_for_phase(phase):
    return LEFT + int(round(phase * PLOT_W))


def draw_anchor_labels(surf, band_top, anchors, font):
    for phase, nm in anchors:
        x = x_for_phase(phase)
        # tick line down through the band + up into the label gap
        pygame.draw.line(surf, (20, 22, 28), (x, band_top - 6), (x, band_top + BAND_H), 1)
        pygame.draw.line(surf, (245, 245, 245), (x, band_top), (x, band_top + 10), 1)
        txt = pygame.transform.rotate(font.render(nm, True, INK), 90)
        r = txt.get_rect()
        r.midbottom = (x, band_top - 7)
        surf.blit(txt, r)


def main():
    pygame.init()
    pygame.font.init()
    f_title = pygame.font.SysFont("dejavusans", 26, bold=True)
    f_axis = pygame.font.SysFont("dejavusans", 17)
    f_small = pygame.font.SysFont("dejavusans", 15)
    f_phase = pygame.font.SysFont("dejavusans", 15, bold=True)
    f_strip = pygame.font.SysFont("dejavusans", 19, bold=True)

    band1_top = TOP + 30 + LABEL_GAP
    band2_top = band1_top + BAND_H + LABEL_GAP + 26
    H = band2_top + BAND_H + 84

    surf = pygame.Surface((W, H))
    surf.fill((250, 250, 250))

    # title
    surf.blit(f_title.render("Skybit day/night schedule — original biome vs new Karst sky",
                             True, INK), (LEFT, 14))

    # secondary top axis: elapsed seconds (0..320)
    sec_y = TOP + 18
    pygame.draw.line(surf, GRID, (LEFT, sec_y), (LEFT + PLOT_W, sec_y), 1)
    for s in range(0, int(CYCLE) + 1, 40):
        x = LEFT + int(round(s / CYCLE * PLOT_W))
        pygame.draw.line(surf, GRID, (x, sec_y - 4), (x, sec_y), 1)
        lab = f_small.render(f"{s}s", True, GRID)
        surf.blit(lab, lab.get_rect(midbottom=(x, sec_y - 5)))
    surf.blit(f_small.render("elapsed seconds", True, GRID), (LEFT, sec_y - 22))

    # strips
    draw_band(surf, band1_top, biome.palette_for_phase)
    draw_band(surf, band2_top, BIOMES["karst_watertown"].palette_for_phase)
    pygame.draw.rect(surf, INK, (LEFT, band1_top, PLOT_W, BAND_H), 1)
    pygame.draw.rect(surf, INK, (LEFT, band2_top, PLOT_W, BAND_H), 1)
    draw_anchor_labels(surf, band1_top, ORIG_ANCHORS, f_phase)
    draw_anchor_labels(surf, band2_top, KARST_ANCHORS, f_phase)

    # left-margin strip labels
    def strip_label(l1, l2, l3, band_top):
        cy = band_top + BAND_H // 2
        t1 = f_strip.render(l1, True, INK)
        t2 = f_small.render(l2, True, (90, 94, 102))
        t3 = f_small.render(l3, True, (90, 94, 102))
        surf.blit(t1, t1.get_rect(midright=(LEFT - 14, cy - 16)))
        surf.blit(t2, t2.get_rect(midright=(LEFT - 14, cy + 4)))
        surf.blit(t3, t3.get_rect(midright=(LEFT - 14, cy + 22)))

    strip_label("Original biome", "game/biome.py", "7 phases", band1_top)
    strip_label("Karst sky (new)", "biome_sky_keyframes", "8 phases", band2_top)

    # primary bottom axis: pillars passed
    ax_y = band2_top + BAND_H + 12
    pygame.draw.line(surf, INK, (LEFT, ax_y), (LEFT + PLOT_W, ax_y), 1)
    for pillars in range(0, int(PILLARS_PER_CYCLE) + 1, 20):
        x = LEFT + int(round(pillars / PILLARS_PER_CYCLE * PLOT_W))
        pygame.draw.line(surf, INK, (x, ax_y), (x, ax_y + 5), 1)
        # skip the last 20-step label when it would collide with the wrap label
        if PILLARS_PER_CYCLE - pillars >= 12:
            lab = f_axis.render(str(pillars), True, INK)
            surf.blit(lab, lab.get_rect(midtop=(x, ax_y + 7)))
    # final tick + label at the wrap (one full cycle)
    xend = LEFT + PLOT_W
    pygame.draw.line(surf, INK, (xend, ax_y), (xend, ax_y + 5), 1)
    end_lab = f_axis.render(f"{PILLARS_PER_CYCLE:.0f}", True, INK)
    surf.blit(end_lab, end_lab.get_rect(midtop=(xend, ax_y + 7)))

    surf.blit(f_axis.render("pillars passed  (one full day/night cycle)", True, INK),
              (LEFT, ax_y + 30))
    cap = (f"1.75 s/pillar (280px spacing / 160px·s scroll), {CYCLE:.0f} s cycle "
           f"= {PILLARS_PER_CYCLE:.0f} pillars. Steady-state scroll; onboarding ramp ignored. "
           f"Both strips share one phase clock — only the keyframe placement differs.")
    surf.blit(f_small.render(cap, True, (110, 114, 122)), (LEFT, ax_y + 52))

    out = os.path.join(os.path.dirname(__file__), "..", "docs", "biome_redesign",
                       "phase_schedule_compare.png")
    out = os.path.abspath(out)
    pygame.image.save(surf, out)
    print(f"wrote {out}  ({W}x{H})")

    # stdout sanity rows: pillar -> phase -> current keyframe on each schedule
    print("\npillar |  phase | original      | karst")
    for pillars in (0, 30, 60, 90, 118, 128, 150, 180):
        phase = (pillars * SEC_PER_PILLAR / CYCLE) % 1.0
        print(f"{pillars:6d} | {phase:.3f}  | {name_at(ORIG_ANCHORS, phase):<12s} | "
              f"{name_at(KARST_ANCHORS, phase)}")


if __name__ == "__main__":
    main()
