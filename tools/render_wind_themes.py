"""Design-round renderer: FIVE distinct windstorm visual themes
for the predawn wind event, each a full reskin of the scene at
PEAK intensity, plus a "current (reference)" panel using the
live Weather.draw. Tooling-only — does NOT touch game/weather.py.

Every theme paints its atmosphere + particles onto a 2x
supersampled SRCALPHA surface and smoothscales down, so edges
are smooth (fixing the "too pixelized" complaint).

Output (docs/screenshots/wind_themes/):
  themes_sheet_<ver>.png            3x2 contact sheet
  theme_<n>_<name>_<ver>.png        individual full-size panels
  theme_0_current_<ver>.png         live-engine reference

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
      python -m tools.render_wind_themes v1
"""
import os
import sys
import math
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pygame.gfxdraw
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y
from game.world import World
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes")
os.makedirs(OUT_DIR, exist_ok=True)

# Peak wind happens at biome phase 0.85 (predawn). All themes
# render at that moment so the sky palette is consistent.
PEAK_PHASE = 0.85
SS = 2  # supersample factor


# ── shared helpers ──────────────────────────────────────────────────────────

def base_scene():
    """Sky + mountains + ground + Pip at peak phase, hover pose.
    Returns (surface, world)."""
    w = World()
    w.ready_t = 0
    w.biome_time = _biome.CYCLE_SECONDS * PEAK_PHASE
    w.weather.phase = w.biome_phase
    w.bird.y = H * 0.42
    w.bird.vy = 0
    w.bird.wind_lean = 0.0
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(w.biome_phase)
    buckets = _biome.PHASE_BUCKETS
    a = int((w.biome_phase % 1.0) * buckets) % buckets
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, a), (0, 0))
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    return surf, w, pal


def new_ss():
    """Fresh transparent supersampled layer."""
    return pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)


def blit_ss(target, ss_layer):
    """Smoothscale a supersampled layer down onto the target."""
    small = pygame.transform.smoothscale(ss_layer, (W, H))
    target.blit(small, (0, 0))


def soft_disc(radius, color, alpha):
    """Smooth radial particle: opaque centre fading to a soft
    transparent edge. Concentric circles drawn LARGEST-first with
    an explicit alpha ramp (transparent at the rim → `alpha` at
    the centre). pygame.draw.circle SETS pixel RGBA on an SRCALPHA
    surface (no blend), so each smaller/higher-alpha ring cleanly
    overwrites the centre → a true radial gradient, no hollow-ring
    artifact. Edges smooth out under the 2× supersample. Coords in
    supersampled space."""
    radius = max(1, int(radius))
    d = radius * 2 + 2
    surf = pygame.Surface((d, d), pygame.SRCALPHA)
    cx = cy = radius + 1
    steps = max(4, radius)
    for i in range(steps, 0, -1):
        rr = max(1, int(radius * i / steps))
        frac = i / steps                       # 1 rim → ~0 centre
        a = int(alpha * (1.0 - frac) ** 1.4)   # 0 rim → alpha centre
        pygame.draw.circle(surf, (*color, a), (cx, cy), rr)
    return surf


def aa_tapered_line(ss_layer, x1, y1, x2, y2, width, color, alpha):
    """Anti-aliased thick line drawn as a filled quad (so width >
    1 still gets smooth edges). Coords in supersampled space."""
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 0.5:
        return
    nx, ny = -dy / ln, dx / ln
    hw = width / 2.0
    pts = [
        (x1 + nx * hw, y1 + ny * hw),
        (x2 + nx * hw, y2 + ny * hw),
        (x2 - nx * hw, y2 - ny * hw),
        (x1 - nx * hw, y1 - ny * hw),
    ]
    ipts = [(int(px), int(py)) for px, py in pts]
    pygame.gfxdraw.filled_polygon(ss_layer, ipts, (*color, alpha))
    pygame.gfxdraw.aapolygon(ss_layer, ipts, (*color, alpha))


def tint_overlay(target, color, alpha):
    """Flat colour wash over the whole frame."""
    o = pygame.Surface((W, H), pygame.SRCALPHA)
    o.fill((*color, alpha))
    target.blit(o, (0, 0))


def vertical_gradient_band(width_px, col_top, col_bot, a_top, a_bot):
    """A soft vertical gradient column (supersampled units)."""
    band = pygame.Surface((width_px, H * SS), pygame.SRCALPHA)
    for yy in range(0, H * SS, 2):
        t = yy / (H * SS)
        r = int(col_top[0] + (col_bot[0] - col_top[0]) * t)
        g = int(col_top[1] + (col_bot[1] - col_top[1]) * t)
        b = int(col_top[2] + (col_bot[2] - col_top[2]) * t)
        a = int(a_top + (a_bot - a_top) * t)
        pygame.draw.rect(band, (r, g, b, a), (0, yy, width_px, 2))
    return band


# ── THEME 1: HABOOB — desert sandstorm ──────────────────────────────────────
# RESERVED FOR A FUTURE WEATHER EVENT. The snow direction (theme 4)
# was chosen for the current predawn wind event; this dark dust-wall
# haboob is parked here intact for a separate desert/sandstorm event
# to be designed later. Keep it + theme_1_haboob.png — do not delete.

def theme_haboob(rng):
    surf, w, pal = base_scene()

    # 1) Base warm haze across the whole sky — strong enough to
    #    bury the night stars and establish the orange haboob
    #    cast. Left lighter, right (leading edge) near-opaque.
    haze = pygame.Surface((W, H), pygame.SRCALPHA)
    for xx in range(0, W, 2):
        t = xx / W
        a = int(120 + t * 120)
        pygame.draw.rect(haze, (198, 148, 82, a), (xx, 0, 2, H))
    surf.blit(haze, (0, 0))

    # 2) Pip — drawn now so the dense leading wall can roll over
    #    him (visibility drop, the signature haboob effect).
    w.bird.draw(surf, flipped=False)

    # 3) The DUST WALL — a real haboob is a dark, ominous wall of
    #    sand rising from the GROUND, looming taller as it
    #    advances. Built as a dense band of dark saturated-brown
    #    puffs filling the lower screen, with a lumpy billowing
    #    TOP edge (taller on the right = advancing front). The
    #    dark wall against the lit dawn sky gives the value
    #    contrast that scattered same-hue puffs lacked.
    ss = new_ss()
    hi  = ((250, 210, 150), (255, 225, 170))         # sunlit rim
    body = ((150, 100, 58), (130, 86, 48), (168, 116, 70))  # dark dust
    deep = ((96, 62, 36), (80, 52, 30))              # deepest core

    gy0 = GROUND_Y * SS
    # Top-edge profile: base height of the wall across x, higher
    # on the right. Sample anchor points then fill puffs up to it.
    def wall_top(x_frac):
        # taller (smaller y) on the right; lumpy via two sines
        base = gy0 * (0.62 - x_frac * 0.30)
        lump = (math.sin(x_frac * 9) * 0.05
                + math.sin(x_frac * 23 + 1.7) * 0.03) * gy0
        return base + lump

    # Fill the wall with densely overlapping stacked puffs from
    # its top edge to ground. High density + big radii + soft
    # discs blend into a cohesive rolling mass (not isolated
    # spots). Colour eases gradually from body near the rim to
    # deep core at the base.
    cols_x = 100
    for ci in range(cols_x):
        x_frac = ci / (cols_x - 1)
        gx = x_frac * W * SS
        top = wall_top(x_frac)
        col_count = rng.randint(9, 13)
        for _ in range(col_count):
            yy = rng.uniform(top - 8 * SS, gy0)
            depth_into = (yy - top) / max(1.0, gy0 - top)  # 0 top →1 base
            r = int(rng.uniform(22, 38) * SS)
            # Smoothly bias colour by depth (probabilistic, no hard
            # threshold) so there are no isolated dark blobs.
            if rng.random() < depth_into * 0.85:
                col = rng.choice(deep)
            else:
                col = rng.choice(body)
            a = rng.randint(95, 150)
            ss.blit(soft_disc(r, col, a),
                    (gx - r + rng.uniform(-14, 14) * SS, yy - r))
        # sunlit highlight rim riding the very top edge
        if rng.random() < 0.55:
            rr = int(rng.uniform(10, 20) * SS)
            ss.blit(soft_disc(rr, rng.choice(hi), rng.randint(60, 110)),
                    (gx - rr, top - rr * 0.5))

    # Airborne grit lofted above the wall (lighter, sparser, rising
    # toward the upper-right where the storm is strongest)
    for _ in range(150):
        x_frac = rng.random() ** 0.5
        gx = x_frac * W * SS
        gy = rng.uniform(wall_top(x_frac) - 120 * SS, wall_top(x_frac))
        if gy < 0:
            continue
        r = rng.randint(3, 8) * SS
        ss.blit(soft_disc(r, rng.choice(body), rng.randint(50, 110)),
                (gx - r, gy - r))
    blit_ss(surf, ss)
    return surf


# ── THEME 2: SPEED GALE — manga/anime motion lines ──────────────────────────

def theme_speed_gale(rng):
    surf, w, pal = base_scene()
    w.bird.draw(surf, flipped=False)

    # Cool the sky for a crisp graphic feel + bury the stars
    tint_overlay(surf, (150, 180, 222), 70)

    ss = new_ss()
    # Vanishing point ahead-right of Pip — lines converge slightly
    # toward it for that energetic anime "rushing forward" read.
    vp_x = W * SS * 1.15
    vp_y = H * SS * 0.42

    def speed_line(ly, length, lx, weight, col, a):
        x_head = lx + length
        x_tail = lx
        # Pull the head toward the vanishing point for convergence
        head_y = ly + (vp_y - ly) * 0.10
        pts = [
            (int(x_head), int(head_y - weight * 0.4)),
            (int(x_head), int(head_y + weight * 0.4)),
            (int(x_tail), int(ly)),
        ]
        pygame.gfxdraw.filled_polygon(ss, pts, (*col, a))
        pygame.gfxdraw.aapolygon(ss, pts, (*col, a))

    # A few THICK hero lines, many medium, some thin — bold and
    # confident with generous negative space between them.
    bands = [(weight, count) for weight, count in
             ((11 * SS, 4), (6 * SS, 7), (3 * SS, 9))]
    for weight, count in bands:
        for _ in range(count):
            ly = rng.uniform(16 * SS, (GROUND_Y - 16) * SS)
            length = rng.uniform(W * SS * 0.45, W * SS * 1.0)
            lx = rng.uniform(-20 * SS, W * SS - length * 0.6)
            col = rng.choice(((255, 255, 255), (225, 245, 255),
                              (190, 225, 250)))
            a = rng.randint(150, 235)
            speed_line(ly, length, lx, weight, col, a)

    # Faint radial speed-burst converging behind Pip for punch
    bird_cx = (90 + 32) * SS
    bird_cy = H * SS * 0.42 + 24 * SS
    for _ in range(26):
        ang = rng.uniform(-0.5, 0.5)
        r0 = rng.uniform(30 * SS, 60 * SS)
        r1 = r0 + rng.uniform(60 * SS, 160 * SS)
        x0 = bird_cx - math.cos(ang) * r0
        y0 = bird_cy - math.sin(ang) * r0
        x1 = bird_cx - math.cos(ang) * r1
        y1 = bird_cy - math.sin(ang) * r1
        aa_tapered_line(ss, x1, y1, x0, y0, 2 * SS,
                        (255, 255, 255), rng.randint(40, 90))
    blit_ss(surf, ss)
    return surf


# ── THEME 3: GHIBLI RIBBONS — painterly streamers ───────────────────────────

def _ribbon_poly(x0, y0, length, amp, wavelength, max_w, phase):
    """Build ONE closed polygon for a smooth silk ribbon: walk the
    centreline forward building the top edge, then walk back
    building the bottom edge. Width swells thick in the middle,
    tapering to points at both ends. No segmentation/ladder
    artifact because it's a single filled polygon."""
    steps = 70
    top, bot = [], []
    for i in range(steps + 1):
        t = i / steps
        x = x0 + t * length
        y = y0 + math.sin(phase + t * math.tau * (length / wavelength)) * amp
        # tangent for perpendicular offset
        dt = 1.0 / steps
        y2 = y0 + math.sin(phase + (t + dt) * math.tau * (length / wavelength)) * amp
        dx = length * dt
        dy = y2 - y
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        wt = math.sin(t * math.pi) ** 0.7        # swell profile
        hw = max(0.5, max_w * wt) / 2.0
        top.append((x + nx * hw, y + ny * hw))
        bot.append((x - nx * hw, y - ny * hw))
    return [(int(px), int(py)) for px, py in (top + bot[::-1])]


def theme_ghibli(rng):
    surf, w, pal = base_scene()
    w.bird.draw(surf, flipped=False)

    # Soft pearlescent bloom wash — covers stars, dreamy haze
    tint_overlay(surf, (205, 210, 240), 45)

    palette = [
        (245, 245, 255), (215, 228, 252), (230, 235, 250),
        (205, 230, 250), (245, 235, 255),
    ]
    ribbons = []
    for _ in range(6):
        ribbons.append(dict(
            x0=-30 * SS, y0=rng.uniform(40 * SS, (GROUND_Y - 40) * SS),
            length=rng.uniform(W * SS * 0.95, W * SS * 1.25),
            amp=rng.uniform(20 * SS, 44 * SS),
            wavelength=rng.uniform(W * SS * 0.7, W * SS * 1.1),
            max_w=rng.uniform(9 * SS, 16 * SS),
            color=rng.choice(palette),
            alpha=rng.randint(110, 165),
            phase=rng.uniform(0, math.tau)))
    for _ in range(5):
        ribbons.append(dict(
            x0=rng.uniform(-30 * SS, W * SS * 0.4),
            y0=rng.uniform(30 * SS, (GROUND_Y - 30) * SS),
            length=rng.uniform(W * SS * 0.5, W * SS * 0.85),
            amp=rng.uniform(12 * SS, 24 * SS),
            wavelength=rng.uniform(W * SS * 0.5, W * SS * 0.8),
            max_w=rng.uniform(4 * SS, 7 * SS),
            color=rng.choice(palette),
            alpha=rng.randint(80, 130),
            phase=rng.uniform(0, math.tau)))

    # Glow pass: fat, faint, blurred ribbons underneath
    glow = new_ss()
    for r in ribbons:
        poly = _ribbon_poly(r["x0"], r["y0"], r["length"], r["amp"],
                            r["wavelength"], r["max_w"] * 2.4, r["phase"])
        pygame.gfxdraw.filled_polygon(glow, poly, (*r["color"], 45))
    glow_small = pygame.transform.smoothscale(glow, (W, H))
    glow_small = pygame.transform.smoothscale(
        pygame.transform.smoothscale(glow_small, (W // 3, H // 3)), (W, H))
    surf.blit(glow_small, (0, 0))

    # Crisp ribbon pass + a bright thin highlight core down the
    # middle of each ribbon so they read as luminous silk catching
    # the dawn light rather than flat grey bands.
    ss = new_ss()
    for r in ribbons:
        poly = _ribbon_poly(r["x0"], r["y0"], r["length"], r["amp"],
                            r["wavelength"], r["max_w"], r["phase"])
        pygame.gfxdraw.filled_polygon(ss, poly, (*r["color"], r["alpha"]))
        pygame.gfxdraw.aapolygon(ss, poly, (*r["color"], r["alpha"]))
        core = _ribbon_poly(r["x0"], r["y0"], r["length"], r["amp"],
                            r["wavelength"], r["max_w"] * 0.4, r["phase"])
        pygame.gfxdraw.filled_polygon(
            ss, core, (255, 255, 255, min(235, r["alpha"] + 70)))
    blit_ss(surf, ss)
    return surf


# ── THEME 4: SNOW SQUALL — blizzard ──────────────────────────────────────────

def theme_snow(rng):
    surf, w, pal = base_scene()
    w.bird.draw(surf, flipped=False)

    # Deep cold storm wash — darker blue-grey so bright white snow
    # POPS against it (a whiteout reads as low-contrast in real
    # life but needs contrast to look good in-game) and the night
    # stars are fully buried.
    tint_overlay(surf, (74, 96, 130), 135)

    ss = new_ss()
    # Driven-snow streaks (fast, near-horizontal) — pure white
    for _ in range(85):
        sx = rng.uniform(0, W * SS)
        sy = rng.uniform(0, GROUND_Y * SS)
        ln = rng.uniform(12 * SS, 30 * SS)
        aa_tapered_line(ss, sx, sy, sx + ln, sy + rng.uniform(-3, 6) * SS,
                        rng.choice((2, 3, 4)) * SS // 2,
                        (255, 255, 255), rng.randint(150, 220))
    # Soft round flakes — near (big, blurred) to far (tiny), bright
    for _ in range(190):
        fx = rng.uniform(0, W * SS)
        fy = rng.uniform(0, GROUND_Y * SS)
        depth = rng.random()
        r = int(2 * SS + depth * 7 * SS)
        a = int(170 + depth * 85)
        ss.blit(soft_disc(r, (255, 255, 255), a), (fx - r, fy - r))
    # Turbulence curls (small swirls)
    for _ in range(10):
        cx = rng.uniform(0, W * SS)
        cy = rng.uniform(30 * SS, (GROUND_Y - 40) * SS)
        rad = rng.uniform(8 * SS, 16 * SS)
        pts = []
        for k in range(10):
            t = k / 9.0
            ang = t * math.pi * 1.4
            rr = rad * (0.3 + 0.7 * t)
            pts.append((cx + math.cos(ang) * rr,
                        cy + math.sin(ang) * rr * 0.7))
        for i in range(len(pts) - 1):
            aa_tapered_line(ss, *pts[i], *pts[i + 1], 2 * SS // 2,
                            (255, 255, 255), 130)
    blit_ss(surf, ss)
    return surf


# ── THEME 5: PETAL STORM — organic spring debris ─────────────────────────────

def _petal(ss, cx, cy, size, rot, color, alpha):
    """A small rotated leaf/petal ellipse with a soft edge."""
    pad = size * 2
    layer = pygame.Surface((pad, pad), pygame.SRCALPHA)
    # Petal = pointed ellipse
    pts = []
    for k in range(14):
        t = k / 14.0 * math.tau
        # Teardrop-ish radius
        rr = size * (0.55 + 0.45 * math.cos(t))
        px = pad / 2 + math.cos(t) * rr
        py = pad / 2 + math.sin(t) * rr * 0.6
        pts.append((px, py))
    ipts = [(int(p[0]), int(p[1])) for p in pts]
    pygame.gfxdraw.filled_polygon(layer, ipts, (*color, alpha))
    pygame.gfxdraw.aapolygon(layer, ipts, (*color, alpha))
    layer = pygame.transform.rotate(layer, math.degrees(rot))
    ss.blit(layer, (cx - layer.get_width() // 2,
                    cy - layer.get_height() // 2))


def theme_petal(rng):
    surf, w, pal = base_scene()
    # Golden spring warmth applied to the SKY first (also buries
    # stars) so the vivid petals read on top
    tint_overlay(surf, (255, 216, 162), 52)
    w.bird.draw(surf, flipped=False)

    ss = new_ss()
    # Vivid spring pastels (drawn at high alpha so they pop)
    spring = [
        (255, 175, 200), (255, 150, 185), (255, 205, 220),
        (255, 230, 175), (185, 230, 175), (255, 240, 215),
    ]
    # Curved motion trails + bigger tumbling petals
    for _ in range(55):
        px = rng.uniform(0, W * SS)
        py = rng.uniform(0, GROUND_Y * SS)
        col = rng.choice(spring)
        size = rng.uniform(8 * SS, 17 * SS)
        # curved trail (a short arc behind the petal)
        trail = rng.uniform(20 * SS, 46 * SS)
        arc = rng.uniform(-10, 10) * SS
        midx, midy = px - trail * 0.5, py + arc
        for seg in range(6):
            t0 = seg / 6.0
            t1 = (seg + 1) / 6.0
            ax = px - trail * t0
            ay = py + arc * math.sin(t0 * math.pi)
            bx = px - trail * t1
            by = py + arc * math.sin(t1 * math.pi)
            aa_tapered_line(ss, bx, by, ax, ay, 2.5 * SS, col,
                            int(70 * (1 - t0)))
        _petal(ss, int(px), int(py), int(size),
               rng.uniform(0, math.tau), col, rng.randint(190, 245))
    # Drifting bright seeds
    for _ in range(28):
        sx = rng.uniform(0, W * SS)
        sy = rng.uniform(0, GROUND_Y * SS)
        ss.blit(soft_disc(3 * SS, (255, 250, 230), 210),
                (sx - 3 * SS, sy - 3 * SS))
    blit_ss(surf, ss)
    return surf


# ── reference panel: live engine ─────────────────────────────────────────────

def theme_current(rng):
    """The current live wind, via the real Weather.draw, for
    side-by-side comparison."""
    w = World()
    w.ready_t = 0
    w.biome_time = _biome.CYCLE_SECONDS * PEAK_PHASE
    w.weather.phase = w.biome_phase
    w.bird.y = H * 0.42
    w.bird.vy = 0
    for _ in range(120):
        w.weather.update(1 / 60.0, w.biome_phase)
    w._apply_weather_effects(1 / 60.0)
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(w.biome_phase)
    buckets = _biome.PHASE_BUCKETS
    a = int((w.biome_phase % 1.0) * buckets) % buckets
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, a), (0, 0))
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    w.bird.draw(surf, flipped=False)
    w.weather.draw(surf)
    return surf


THEMES = [
    ("1", "haboob",      "1  HABOOB — sandstorm",   theme_haboob),
    ("2", "speed_gale",  "2  SPEED GALE — manga",   theme_speed_gale),
    ("3", "ghibli",      "3  GHIBLI — ribbons",     theme_ghibli),
    ("4", "snow",        "4  SNOW SQUALL — blizzard", theme_snow),
    ("5", "petal",       "5  PETAL STORM — spring", theme_petal),
    ("0", "current",     "0  CURRENT (reference)",  theme_current),
]


def main():
    # Optional version suffix arg (e.g. "v2") for side-by-side
    # iteration; default writes the clean committed filenames.
    ver = sys.argv[1] if len(sys.argv) > 1 else ""
    suffix = f"_{ver}" if ver else ""
    panels = []
    for num, slug, label, fn in THEMES:
        rng = random.Random(40 + int(num))   # per-theme stable seed
        panel = fn(rng)
        panels.append((label, panel))
        out = os.path.join(OUT_DIR, f"theme_{num}_{slug}{suffix}.png")
        pygame.image.save(panel, out)
        print(f"saved {out}")

    # 3x2 contact sheet
    cols, rows = 3, 2
    margin = 12
    label_h = 28
    sheet_w = W * cols + margin * (cols + 1)
    sheet_h = (H + label_h) * rows + margin * (rows + 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    font = pygame.font.SysFont("Arial", 14, bold=True)
    for i, (label, panel) in enumerate(panels):
        c = i % cols
        r = i // cols
        x = margin + c * (W + margin)
        y = margin + r * (H + label_h + margin)
        pygame.draw.rect(sheet, (60, 65, 80), (x - 2, y - 2, W + 4, H + 4), 2)
        sheet.blit(panel, (x, y))
        txt = font.render(label, True, (240, 240, 245))
        sheet.blit(txt, (x + (W - txt.get_width()) // 2, y + H + 5))
    out = os.path.join(OUT_DIR, f"themes_sheet{suffix}.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
