"""Design sub-round: 5 wind-EMPHASIZING variants of the chosen
Snow Squall theme (#4). All share the approved cold storm wash;
they differ in HOW the wind reads — stretch / sheets / vortices /
streamlines / surge. Tooling-only; does NOT touch game/weather.py.

Output (docs/screenshots/wind_themes/snow_variants/):
  snow_variants_sheet.png         3x2 contact sheet
  snow_<n>_<name>.png             individual full-size panels

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
      python -m tools.render_snow_variants
"""
import os
import sys
import math
import random

import pygame

# Reuse the shared scaffold (pygame is initialised on import).
from tools.render_wind_themes import (
    base_scene, new_ss, blit_ss, soft_disc, aa_tapered_line,
    tint_overlay, theme_snow, SS, W, H, GROUND_Y,
)

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes",
                       "snow_variants")
os.makedirs(OUT_DIR, exist_ok=True)

# Approved cold storm wash — every variant starts here.
COLD = (74, 96, 130)
COLD_A = 135


def cold_base():
    surf, w, pal = base_scene()
    w.bird.draw(surf, flipped=False)
    tint_overlay(surf, COLD, COLD_A)
    return surf, w


def sprinkle_flakes(ss, rng, n, rmax=7, amin=120, amax=220):
    """Light grain of soft round flakes for texture."""
    for _ in range(n):
        fx = rng.uniform(0, W * SS)
        fy = rng.uniform(0, GROUND_Y * SS)
        depth = rng.random()
        r = int(2 * SS + depth * rmax * SS)
        a = int(amin + depth * (amax - amin))
        ss.blit(soft_disc(r, (255, 255, 255), a), (fx - r, fy - r))


# ── 1: HORIZONTAL DRIVE ──────────────────────────────────────────────────────

def snow_horizontal(rng):
    surf, w = cold_base()
    ss = new_ss()
    # Dense long near-horizontal speed streaks (wind so strong the
    # snow is pure motion blur). Slight downward drift L→R.
    for _ in range(190):
        sx = rng.uniform(-40 * SS, W * SS)
        sy = rng.uniform(0, GROUND_Y * SS)
        ln = rng.uniform(28 * SS, 75 * SS)
        droop = rng.uniform(2, 10) * SS * (ln / (W * SS))
        wgt = rng.choice((1, 2, 2, 3)) * SS / 2.0
        a = rng.randint(120, 225)
        aa_tapered_line(ss, sx, sy, sx + ln, sy + droop, wgt,
                        (255, 255, 255), a)
    # Light flake grain so it still reads as snow
    sprinkle_flakes(ss, rng, 45, rmax=4, amin=110, amax=180)
    blit_ss(surf, ss)
    return surf


# ── 2: GUST SHEETS ───────────────────────────────────────────────────────────

def _sheet(rng, angle_deg, cy, thickness, length, alpha):
    """One soft translucent diagonal snow-sheet as a smoothscaled
    gradient band, returned as its own SRCALPHA layer in screen
    space (already small)."""
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    ang = math.radians(angle_deg)
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    cx = W * 0.5
    steps = int(thickness)
    for i in range(-steps, steps + 1):
        t = abs(i) / steps
        a = int(alpha * (1.0 - t) ** 1.5)
        if a <= 0:
            continue
        ox, oy = nx * i, ny * i
        x1 = cx + ox - dx * length
        y1 = cy + oy - dy * length
        x2 = cx + ox + dx * length
        y2 = cy + oy + dy * length
        pygame.draw.line(layer, (235, 245, 255, a),
                         (x1, y1), (x2, y2), 2)
    return layer


def snow_sheets(rng):
    surf, w = cold_base()
    # 5 big sweeping sheets at a shared shallow downward angle
    for _ in range(5):
        ang = rng.uniform(6, 16)
        cy = rng.uniform(40, GROUND_Y - 40)
        thick = rng.uniform(14, 30)
        sheet = _sheet(rng, ang, cy, thick, W * 0.9,
                       rng.randint(35, 70))
        surf.blit(sheet, (0, 0))
    # Embedded flakes + streaks riding the gusts
    ss = new_ss()
    for _ in range(90):
        sx = rng.uniform(0, W * SS)
        sy = rng.uniform(0, GROUND_Y * SS)
        ln = rng.uniform(16 * SS, 40 * SS)
        aa_tapered_line(ss, sx, sy, sx + ln, sy + rng.uniform(2, 8) * SS,
                        rng.choice((1, 2)) * SS / 2.0,
                        (255, 255, 255), rng.randint(120, 200))
    sprinkle_flakes(ss, rng, 110, rmax=6, amin=130, amax=230)
    blit_ss(surf, ss)
    return surf


# ── 3: VORTEX TURBULENCE ─────────────────────────────────────────────────────

def snow_vortex(rng):
    surf, w = cold_base()
    ss = new_ss()
    # Many spiral wind eddies spread across the scene; snow streaks
    # follow the curves. Between the eddies, lots of swept snow
    # streaks fill the gaps so the whole frame reads as chaotic
    # turbulent gusting (not a few isolated coils).
    vortices = []
    for _ in range(8):
        vortices.append((
            rng.uniform(W * SS * 0.05, W * SS * 1.0),
            rng.uniform(GROUND_Y * SS * 0.1, GROUND_Y * SS * 0.95),
            rng.uniform(22 * SS, 64 * SS),
            rng.choice((-1, 1)),
        ))
    for vx, vy, vr, vdir in vortices:
        arms = rng.randint(6, 10)
        for a_i in range(arms):
            a0 = (a_i / arms) * math.tau
            pts = []
            turns = rng.uniform(1.0, 1.8)
            squash = rng.uniform(0.62, 0.85)      # organic ellipticity
            n = 24
            for k in range(n):
                t = k / (n - 1)
                ang = a0 + vdir * t * math.tau * turns
                rr = vr * (0.10 + 0.90 * t)
                pts.append((vx + math.cos(ang) * rr,
                            vy + math.sin(ang) * rr * squash))
            for i in range(len(pts) - 1):
                fade = i / len(pts)
                aa_tapered_line(ss, *pts[i], *pts[i + 1],
                                rng.choice((1, 2)) * SS / 2.0,
                                (255, 255, 255),
                                int(60 + 160 * fade))
    # Swept snow filling the gaps — short curved streaks with a
    # slight shared L→R drift so it reads as turbulent flow
    for _ in range(150):
        sx = rng.uniform(0, W * SS)
        sy = rng.uniform(0, GROUND_Y * SS)
        ln = rng.uniform(12 * SS, 30 * SS)
        curl = rng.uniform(-8, 8) * SS
        aa_tapered_line(ss, sx, sy, sx + ln, sy + curl,
                        rng.choice((1, 2)) * SS / 2.0,
                        (255, 255, 255), rng.randint(90, 175))
    sprinkle_flakes(ss, rng, 70, rmax=5, amin=110, amax=200)
    blit_ss(surf, ss)
    return surf


# ── 4: STREAMLINE FLOW ───────────────────────────────────────────────────────

def snow_streamlines(rng):
    surf, w = cold_base()
    ss = new_ss()
    # Bold parallel curving streamlines sweeping L→R (a shared
    # gentle sine field). Each line is a bright continuous flow
    # path with snow "packets" (soft flakes) riding along it, so
    # the airflow is unmistakable and the snow clearly FOLLOWS the
    # wind rather than drifting randomly.
    field_phase = rng.uniform(0, math.tau)
    n_lines = 22

    def flow_y(base_y, t, idx, amp, wl):
        return base_y + math.sin(field_phase + t * math.tau * (W * SS / wl)
                                 + idx * 0.30) * amp

    for li in range(n_lines):
        base_y = (li / n_lines) * GROUND_Y * SS + rng.uniform(-6, 6) * SS
        amp = rng.uniform(16 * SS, 32 * SS)
        wl = W * SS * rng.uniform(0.85, 1.15)
        a = rng.randint(110, 200)
        wgt = rng.choice((2, 2, 3, 4)) * SS / 2.0
        prev = None
        n = 64
        for k in range(n + 1):
            t = k / n
            x = -20 * SS + t * (W * SS + 40 * SS)
            y = flow_y(base_y, t, li, amp, wl)
            if prev is not None:
                # brighter in the middle, tapering at both ends
                seg_a = int(a * (0.30 + 0.70 * math.sin(t * math.pi)))
                aa_tapered_line(ss, prev[0], prev[1], x, y, wgt,
                                (255, 255, 255), seg_a)
            prev = (x, y)
        # Snow packets riding this streamline
        for _ in range(rng.randint(2, 4)):
            t = rng.uniform(0.1, 0.95)
            x = -20 * SS + t * (W * SS + 40 * SS)
            y = flow_y(base_y, t, li, amp, wl)
            r = rng.randint(2, 5) * SS
            ss.blit(soft_disc(r, (255, 255, 255), rng.randint(160, 240)),
                    (x - r, y - r))
    # Light free grain
    sprinkle_flakes(ss, rng, 40, rmax=4, amin=100, amax=170)
    blit_ss(surf, ss)
    return surf


# ── 5: WHITEOUT SURGE ────────────────────────────────────────────────────────

def snow_surge(rng):
    surf, w = cold_base()
    ss = new_ss()
    # Density rises hard toward the right (leading gust) — a
    # surging mass of snow being pushed across, plus driving
    # streaks throughout.
    # Big soft blizzard mass on the right via clustered flakes
    for _ in range(420):
        edge = rng.random() ** 0.55          # bias right
        fx = edge * W * SS
        fy = rng.uniform(0, GROUND_Y * SS)
        depth = rng.random()
        r = int(2 * SS + depth * 8 * SS)
        a = int((120 + depth * 110) * (0.35 + edge * 0.65))
        ss.blit(soft_disc(r, (255, 255, 255), a), (fx - r, fy - r))
    # Driving streaks everywhere, denser right
    for _ in range(150):
        edge = rng.random() ** 0.5
        sx = edge * W * SS
        sy = rng.uniform(0, GROUND_Y * SS)
        ln = rng.uniform(22 * SS, 60 * SS)
        aa_tapered_line(ss, sx, sy, sx + ln, sy + rng.uniform(2, 9) * SS,
                        rng.choice((1, 2, 3)) * SS / 2.0,
                        (255, 255, 255),
                        int(rng.randint(120, 210) * (0.5 + edge * 0.5)))
    blit_ss(surf, ss)
    # Extra near-white haze on the far right (whiteout core)
    haze = pygame.Surface((W, H), pygame.SRCALPHA)
    for xx in range(0, W, 2):
        t = xx / W
        a = int(max(0, (t - 0.45)) * 150)
        if a > 0:
            pygame.draw.rect(haze, (240, 248, 255, a), (xx, 0, 2, H))
    surf.blit(haze, (0, 0))
    return surf


VARIANTS = [
    ("1", "horizontal",  "1  HORIZONTAL DRIVE",  snow_horizontal),
    ("2", "sheets",      "2  GUST SHEETS",       snow_sheets),
    ("3", "vortex",      "3  VORTEX TURBULENCE", snow_vortex),
    ("4", "streamlines", "4  STREAMLINE FLOW",   snow_streamlines),
    ("5", "surge",       "5  WHITEOUT SURGE",    snow_surge),
    ("0", "reference",   "0  CURRENT SNOW (ref)", theme_snow),
]


def main():
    ver = sys.argv[1] if len(sys.argv) > 1 else ""
    suffix = f"_{ver}" if ver else ""
    panels = []
    for num, slug, label, fn in VARIANTS:
        rng = random.Random(70 + int(num))
        panel = fn(rng)
        panels.append((label, panel))
        out = os.path.join(OUT_DIR, f"snow_{num}_{slug}{suffix}.png")
        pygame.image.save(panel, out)
        print(f"saved {out}")

    cols, rows = 3, 2
    margin = 12
    label_h = 28
    sheet_w = W * cols + margin * (cols + 1)
    sheet_h = (H + label_h) * rows + margin * (rows + 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 22, 30))
    font = pygame.font.SysFont("Arial", 14, bold=True)
    for i, (label, panel) in enumerate(panels):
        c = i % cols
        r = i // cols
        x = margin + c * (W + margin)
        y = margin + r * (H + label_h + margin)
        pygame.draw.rect(sheet, (60, 70, 95), (x - 2, y - 2, W + 4, H + 4), 2)
        sheet.blit(panel, (x, y))
        txt = font.render(label, True, (235, 242, 250))
        sheet.blit(txt, (x + (W - txt.get_width()) // 2, y + H + 5))
    out = os.path.join(OUT_DIR, f"snow_variants_sheet{suffix}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
