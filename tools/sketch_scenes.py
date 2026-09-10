"""Render representative still PNGs for candidate dynamic background scenes.

Each PNG is one frame, drawn on top of the real Skybit backdrop (sky, biome,
parallax clouds, mountains, ground) at the appropriate biome phase. Animations
are represented as a single evocative frame.

Run:
    python tools/sketch_scenes.py
"""
import os, sys, pathlib, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))   # needed for fonts / image.save

from game.config import W, H, GROUND_Y
from game.world import World
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)

CYCLE = _biome.CYCLE_SECONDS

OUT_DIR = pathlib.Path(__file__).parent.parent / "docs" / "scene_sketches"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _phase_to_time(phase: float) -> float:
    return ((phase - 0.04) % 1.0) * CYCLE


def _make_world(phase: float, sim_ticks: int = 60) -> World:
    """Build a World, advance it briefly so parallax scroll is non-zero,
    then pin biome_time to the requested phase for the final frame."""
    world = World()
    world.biome_time = _phase_to_time(phase)
    world.ready_t = 0.0
    dt = 1 / 60
    for tick in range(sim_ticks):
        if tick % 24 == 0:
            world.bird.flap()
        world.update(dt)
    world.biome_time = _phase_to_time(phase)
    return world


def _draw_backdrop(surf: pygame.Surface, world: World) -> None:
    """Sky + clouds + mountains + ground — mirrors scenes._draw_background.
    Lifted from tools/biome_snapshots.py:117-146."""
    palette = world.biome_palette
    buckets = _biome.PHASE_BUCKETS
    bf = (world.biome_phase % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    t = bf - int(bf)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)

    scroll = world.bg_scroll
    cloud_phase = 1.5
    for i, (bx, by, sc, variant) in enumerate((
            (20, 90, 0.9, 0), (180, 140, 1.1, 2),
            (60, 220, 0.8, 3), (230, 60, 0.7, 1),
            (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W, palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))


# ──────────────── Scene primitives ────────────────

def draw_shooting_stars(surf: pygame.Surface, palette: dict) -> None:
    """Faint starfield + one bright shooting streak across the upper sky."""
    rnd = random.Random(101)
    star_alpha = int(palette.get('star_alpha', 200))
    star_layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(36):
        sx = rnd.randint(0, W - 1)
        sy = rnd.randint(8, GROUND_Y - 220)
        a = rnd.randint(int(star_alpha * 0.4), star_alpha)
        star_layer.set_at((sx, sy), (255, 255, 255, a))
    surf.blit(star_layer, (0, 0))

    # Streak: diagonal upper-right → lower-left, 24 fading segments.
    streak = pygame.Surface((W, H), pygame.SRCALPHA)
    x0, y0 = 290, 60
    x1, y1 = 200, 130
    segs = 24
    for i in range(segs):
        u0 = i / segs
        u1 = (i + 1) / segs
        a = int(255 * (1.0 - u0) ** 1.6)
        if a <= 4:
            continue
        sx = int(x0 + (x1 - x0) * u0)
        sy = int(y0 + (y1 - y0) * u0)
        ex = int(x0 + (x1 - x0) * u1)
        ey = int(y0 + (y1 - y0) * u1)
        pygame.draw.line(streak, (255, 250, 230, a), (sx, sy), (ex, ey), 2)
    # Bright head
    pygame.draw.circle(streak, (255, 255, 240, 255), (x0, y0), 3)
    pygame.draw.circle(streak, (255, 240, 200, 90),  (x0, y0), 7)
    surf.blit(streak, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_v_flock(surf: pygame.Surface, palette: dict) -> None:
    """Distant V-formation of birds at mid-far parallax depth."""
    base_color = palette.get('mtn_far', (90, 90, 110))
    silhouette = (max(0, base_color[0] - 60),
                  max(0, base_color[1] - 60),
                  max(0, base_color[2] - 60))

    cx, cy = int(W * 0.55), int(H * 0.40)
    sx, sy = 14, 11  # horizontal/vertical spacing
    # 7 birds: leader at (cx,cy), trailing in two rearward-spreading lines.
    offsets = [
        (0, 0),
        (-sx,    sy),   ( sx,   sy),
        (-2*sx,  2*sy), ( 2*sx, 2*sy),
        (-3*sx,  3*sy), ( 3*sx, 3*sy),
    ]
    for ox, oy in offsets:
        bx, by = cx + ox, cy + oy
        # Tiny chevron: two 2-px diagonal strokes meeting at a point.
        pygame.draw.line(surf, silhouette, (bx - 6, by + 2), (bx, by - 2), 2)
        pygame.draw.line(surf, silhouette, (bx + 6, by + 2), (bx, by - 2), 2)


def draw_lighthouse(surf: pygame.Surface, palette: dict) -> None:
    """Tiny lighthouse silhouette on far hill with a sweeping beam cone."""
    # Tower silhouette
    tower_x = int(W * 0.78)
    tower_top_y = GROUND_Y - 28
    tower_w = 5
    tower_h = 18
    pygame.draw.rect(surf, (15, 15, 25),
                     (tower_x - tower_w // 2, tower_top_y, tower_w, tower_h))
    # Cap (slightly wider)
    pygame.draw.rect(surf, (15, 15, 25),
                     (tower_x - tower_w // 2 - 2, tower_top_y - 3,
                      tower_w + 4, 3))
    # Lamp
    lamp_y = tower_top_y - 1
    pygame.draw.circle(surf, (255, 200, 120), (tower_x, lamp_y), 1)

    # Beam — additive cone reaching up-and-left.
    # Single thin polygon with very low alpha so it reads as atmospheric
    # light catching mist, not a solid spotlight.
    beam = pygame.Surface((W, H), pygame.SRCALPHA)
    beam_len = 220
    spread = math.radians(7)
    angle = math.radians(215)  # pointing up and to the left
    tip_a_x = tower_x + math.cos(angle - spread) * beam_len
    tip_a_y = lamp_y + math.sin(angle - spread) * beam_len
    tip_b_x = tower_x + math.cos(angle + spread) * beam_len
    tip_b_y = lamp_y + math.sin(angle + spread) * beam_len

    # Hand-paint the cone in slim slices, each slice darker toward the
    # tip. Use standard alpha blending (NOT additive) so it reads as a
    # soft atmospheric haze rather than a saturated spotlight.
    slices = 18
    for k in range(slices):
        u0 = k / slices
        u1 = (k + 1) / slices
        a = max(0, int(60 * (1.0 - u0) ** 1.8))
        if a <= 2:
            continue
        a0x = tower_x + (tip_a_x - tower_x) * u0
        a0y = lamp_y  + (tip_a_y - lamp_y)  * u0
        a1x = tower_x + (tip_a_x - tower_x) * u1
        a1y = lamp_y  + (tip_a_y - lamp_y)  * u1
        b0x = tower_x + (tip_b_x - tower_x) * u0
        b0y = lamp_y  + (tip_b_y - lamp_y)  * u0
        b1x = tower_x + (tip_b_x - tower_x) * u1
        b1y = lamp_y  + (tip_b_y - lamp_y)  * u1
        pygame.draw.polygon(beam, (255, 235, 190, a),
                            [(a0x, a0y), (a1x, a1y),
                             (b1x, b1y), (b0x, b0y)])
    surf.blit(beam, (0, 0))  # standard alpha blend, no BLEND_RGB_ADD
    # Lamp bloom — small additive pop at the lamp itself
    glow = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 220, 160, 70), (tower_x, lamp_y), 3)
    pygame.draw.circle(glow, (255, 180, 120, 35), (tower_x, lamp_y), 6)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_fireflies(surf: pygame.Surface, palette: dict) -> None:
    """Cluster of glowing yellow-green dots in the foliage band at dusk."""
    rnd = random.Random(202)
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(22):
        x = rnd.randint(20, W - 20)
        y = rnd.randint(GROUND_Y - 70, GROUND_Y - 12)
        # Outer bloom
        pygame.draw.circle(layer, (180, 240, 140, 50), (x, y), 6)
        pygame.draw.circle(layer, (210, 255, 160, 90), (x, y), 3)
        # Bright core
        pygame.draw.circle(layer, (240, 255, 200, 220), (x, y), 1)
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_fireworks(surf: pygame.Surface, palette: dict) -> None:
    """Three small bursts low on the horizon — distant, not full-screen."""
    bursts = [
        (80,  GROUND_Y - 95,  (255, 180,  90)),
        (180, GROUND_Y - 115, (255, 120, 180)),
        (280, GROUND_Y - 80,  (180, 220, 255)),
    ]
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for cx, cy, col in bursts:
        rays = 14
        radius = 18
        for i in range(rays):
            ang = (i / rays) * math.tau
            ex = cx + math.cos(ang) * radius
            ey = cy + math.sin(ang) * radius
            # Per-ray fade: brighter near center, dim at tip
            for step, a in ((0.0, 235), (0.45, 160), (0.85, 60)):
                px = cx + (ex - cx) * step
                py = cy + (ey - cy) * step
                pygame.draw.circle(layer, (*col, a), (int(px), int(py)), 1)
        # White-hot core
        pygame.draw.circle(layer, (255, 255, 240, 240), (cx, cy), 2)
        pygame.draw.circle(layer, (*col, 90),           (cx, cy), 5)
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_aurora(surf: pygame.Surface, palette: dict) -> None:
    """Soft sinusoidal green→violet ribbon across the upper sky."""
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    band_h = 90
    for x in range(0, W, 2):
        baseline = 110 + 30 * math.sin(x * 0.025)
        # Color blend across x
        u = x / W
        r = int(120 * (1 - u) + 180 * u)
        g = int(255 * (1 - u) + 140 * u)
        b = int(180 * (1 - u) + 255 * u)
        for k in range(band_h):
            v = k / band_h
            # Bell curve alpha: 0 → ~110 mid → 0
            a = int(110 * math.sin(v * math.pi))
            if a <= 0:
                continue
            y = int(baseline + k - band_h // 2)
            if 0 <= y < H:
                layer.set_at((x, y),     (r, g, b, a))
                if x + 1 < W:
                    layer.set_at((x + 1, y), (r, g, b, a))
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


# ──────────── Hot-air balloon helpers (shared by 07a–07e) ────────────

def _teardrop_polygon(cx: float, cy: float, w: float, h: float, n: int = 36):
    """Closed polygon approximating a hot-air-balloon envelope:
    rounded top, gently pinched bottom mouth."""
    pts = []
    rx, ry = w / 2, h / 2
    for i in range(n):
        ang = -math.pi / 2 + (i / n) * math.tau
        x = math.cos(ang) * rx
        y = math.sin(ang) * ry
        if y > 0:
            pinch = 1.0 - 0.62 * (y / ry) ** 2
            x *= pinch
        pts.append((cx + x, cy + y))
    return pts


def _envelope_extent_at_y(cx: float, cy: float, w: float, h: float, y: float):
    """Return (left_x, right_x) of the teardrop envelope at world-y `y`."""
    rx, ry = w / 2, h / 2
    dy = y - cy
    if abs(dy) >= ry:
        return None
    x_ell = rx * math.sqrt(max(0.0, 1 - (dy / ry) ** 2))
    if dy > 0:
        x_ell *= 1.0 - 0.62 * (dy / ry) ** 2
    return cx - x_ell, cx + x_ell


def _draw_basket(surf, cx: int, top_y: int, w: int, h: int,
                 weave: bool = True, passenger: bool = False):
    pygame.draw.rect(surf, (130, 85, 40), (cx - w // 2, top_y, w, h))
    pygame.draw.rect(surf, (60, 40, 20), (cx - w // 2, top_y, w, h), 1)
    if weave:
        for k in range(1, 3):
            ly = top_y + h * k // 3
            pygame.draw.line(surf, (90, 60, 30),
                             (cx - w // 2 + 1, ly),
                             (cx + w // 2 - 1, ly), 1)
        for vx in (cx - w // 4, cx, cx + w // 4):
            pygame.draw.line(surf, (95, 65, 32),
                             (vx, top_y + 1), (vx, top_y + h - 1), 1)
    if passenger:
        pygame.draw.circle(surf, (35, 25, 20), (cx, top_y - 2), 2)


def _draw_paneled_envelope(surf, cx: int, cy: int, w: int, h: int,
                           panel_a: tuple, panel_b: tuple,
                           seam: tuple, n_panels: int = 8):
    """Reusable paneled (multi-gore) hot-air-balloon envelope.

    Renders teardrop outline, alternating vertical panels masked to the
    envelope, gore-separator hairlines, equator seam, outline, and a
    small upper-left highlight."""
    outline = _teardrop_polygon(cx, cy, w, h)
    pygame.draw.polygon(surf, panel_a, outline)
    # Alternating panel stripes
    for i in range(n_panels):
        if i % 2 == 0:
            continue
        x0 = cx - w / 2 + i * (w / n_panels)
        x1 = cx - w / 2 + (i + 1) * (w / n_panels)
        for y_int in range(int(cy - h / 2), int(cy + h / 2) + 1):
            ext = _envelope_extent_at_y(cx, cy, w, h, y_int)
            if ext is None:
                continue
            lx, rx = ext
            dx0 = max(x0, lx)
            dx1 = min(x1, rx)
            if dx1 > dx0:
                pygame.draw.line(surf, panel_b,
                                 (int(dx0), y_int), (int(dx1), y_int), 1)
    # Gore separator hairlines
    for i in range(1, n_panels):
        sx = cx - w / 2 + i * (w / n_panels)
        for y_int in range(int(cy - h / 2 + 2), int(cy + h / 2 - 1)):
            ext = _envelope_extent_at_y(cx, cy, w, h, y_int)
            if ext is None:
                continue
            lx, rx = ext
            if lx + 1 <= sx <= rx - 1:
                surf.set_at((int(sx), y_int), seam)
    # Equator seam
    ext = _envelope_extent_at_y(cx, cy, w, h, cy + 1)
    if ext is not None:
        lx, rx = ext
        pygame.draw.line(surf, seam, (int(lx + 1), int(cy + 1)),
                         (int(rx - 1), int(cy + 1)), 1)
    # Outer outline
    pygame.draw.polygon(surf, seam, outline, 1)
    # Upper-left highlight
    hi = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(hi, (255, 255, 255, 60),
                        (3, 3, max(5, w // 3), max(5, h // 3)))
    surf.blit(hi, (cx - w // 2, cy - h // 2))


# Smaller, tighter set of 3 paneled balloons used by all 07a*-variants.
_BALLOONS_SMALL = [
    # cx, cy, w, h, panels[0], panels[1], seam
    (W * 0.22, H * 0.34, 36, 46,
     (220,  60,  60), (250, 230, 200), (90, 50, 30)),
    (W * 0.58, H * 0.46, 28, 36,
     (40, 140, 200), (240, 240, 240), (30, 70, 110)),
    (W * 0.84, H * 0.26, 22, 28,
     (245, 175,  80), (90,  60, 130), (90, 60, 25)),
]


def _draw_ropes(surf, env_cx: int, env_bottom_y: int,
                basket_cx: int, basket_top_y: int,
                basket_w: int, env_w: int):
    rope = (45, 30, 20)
    bx0 = basket_cx - basket_w // 2 + 1
    bx1 = basket_cx + basket_w // 2 - 1
    ex0 = env_cx - env_w // 4
    ex1 = env_cx + env_w // 4
    ex_mid_l = env_cx - env_w // 8
    ex_mid_r = env_cx + env_w // 8
    pygame.draw.line(surf, rope, (ex0, env_bottom_y), (bx0, basket_top_y), 1)
    pygame.draw.line(surf, rope, (ex1, env_bottom_y), (bx1, basket_top_y), 1)
    pygame.draw.line(surf, rope, (ex_mid_l, env_bottom_y - 2),
                     (basket_cx - basket_w // 6, basket_top_y), 1)
    pygame.draw.line(surf, rope, (ex_mid_r, env_bottom_y - 2),
                     (basket_cx + basket_w // 6, basket_top_y), 1)


# ──────────── 07a Paneled (multi-gore) ────────────

def draw_balloons_paneled(surf: pygame.Surface, palette: dict) -> None:
    """Real hot-air balloon multi-gore construction with alternating
    vertical panels and a visible equator seam."""
    balloons = [
        # cx, cy, w, h, panel_colors (alternating), seam color
        (W * 0.22, H * 0.32, 56, 70,
         [(220,  60,  60), (250, 230, 200)], (90, 50, 30)),
        (W * 0.58, H * 0.46, 44, 56,
         [(40, 140, 200), (240, 240, 240)], (30, 70, 110)),
        (W * 0.84, H * 0.24, 36, 46,
         [(245, 175,  80), (90,  60, 130)], (90, 60, 25)),
    ]
    for cx, cy, w, h, panels, seam in balloons:
        cx, cy = int(cx), int(cy)
        # 1) Fill envelope with base panel color
        outline = _teardrop_polygon(cx, cy, w, h)
        pygame.draw.polygon(surf, panels[0], outline)
        # 2) Overlay alternating vertical panel stripes, masked to envelope
        n_panels = 8
        for i in range(n_panels):
            if i % 2 == 0:
                continue  # base color already covers these
            x0 = cx - w / 2 + i * (w / n_panels)
            x1 = cx - w / 2 + (i + 1) * (w / n_panels)
            # Walk row-by-row, clipping to envelope extent
            for y_int in range(int(cy - h / 2), int(cy + h / 2) + 1):
                ext = _envelope_extent_at_y(cx, cy, w, h, y_int)
                if ext is None:
                    continue
                lx, rx = ext
                draw_x0 = max(x0, lx)
                draw_x1 = min(x1, rx)
                if draw_x1 > draw_x0:
                    pygame.draw.line(surf, panels[1],
                                     (int(draw_x0), y_int),
                                     (int(draw_x1), y_int), 1)
        # 3) Vertical gore-separator hairlines
        for i in range(1, n_panels):
            sx = cx - w / 2 + i * (w / n_panels)
            # Only draw where the envelope exists
            for y_int in range(int(cy - h / 2 + 2), int(cy + h / 2 - 1)):
                ext = _envelope_extent_at_y(cx, cy, w, h, y_int)
                if ext is None:
                    continue
                lx, rx = ext
                if lx + 1 <= sx <= rx - 1:
                    surf.set_at((int(sx), y_int), seam)
        # 4) Equator seam (horizontal hairline at envelope mid)
        ext = _envelope_extent_at_y(cx, cy, w, h, cy + 2)
        if ext is not None:
            lx, rx = ext
            pygame.draw.line(surf, seam, (int(lx + 1), int(cy + 2)),
                             (int(rx - 1), int(cy + 2)), 1)
        # 5) Outline
        pygame.draw.polygon(surf, seam, outline, 1)
        # 6) Subtle highlight on upper-left
        hi = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(hi, (255, 255, 255, 55),
                            (4, 4, max(6, w // 3), max(6, h // 3)))
        surf.blit(hi, (cx - w // 2, cy - h // 2))
        # 7) Ropes + basket
        env_bottom_y = int(cy + h / 2)
        basket_top_y = env_bottom_y + 9
        basket_w = max(12, int(w * 0.32))
        _draw_ropes(surf, cx, env_bottom_y, cx, basket_top_y, basket_w, w)
        _draw_basket(surf, cx, basket_top_y, basket_w, 9,
                     weave=True, passenger=True)


# ──────────── 07a1 Skirt band + fanning ropes ────────────

def draw_balloons_paneled_skirt(surf: pygame.Surface, palette: dict) -> None:
    """Smaller paneled balloons with an explicit darker skirt band at the
    envelope's bottom and 6 ropes fanning from the skirt to the basket."""
    rope = (40, 28, 18)
    for cx, cy, w, h, pa, pb, seam in _BALLOONS_SMALL:
        cx, cy = int(cx), int(cy)
        _draw_paneled_envelope(surf, cx, cy, w, h, pa, pb, seam)
        # Skirt band — a darker horizontal band at the bottom of the envelope
        skirt_y = int(cy + h * 0.40)
        ext = _envelope_extent_at_y(cx, cy, w, h, skirt_y)
        if ext is not None:
            lx, rx = ext
            for off in range(-1, 3):
                pygame.draw.line(surf, (max(0, seam[0] - 10),
                                        max(0, seam[1] - 10),
                                        max(0, seam[2] - 10)),
                                 (int(lx) + 1, skirt_y + off),
                                 (int(rx) - 1, skirt_y + off), 1)
        env_bottom_y = int(cy + h / 2)
        # Basket — closer to envelope (smaller air gap)
        basket_top_y = env_bottom_y + 5
        basket_w = max(10, int(w * 0.36))
        basket_h = max(6, int(h * 0.20))
        bx0 = cx - basket_w // 2
        bx1 = cx + basket_w // 2
        # 6 ropes: 3 anchor points on each side of the envelope skirt,
        # fanning down to evenly-spaced points along the basket's top edge.
        for k in range(3):
            u = (k + 0.5) / 3        # 1/6, 1/2, 5/6
            anchor_y = cy + h * (0.05 + u * 0.35)
            ae = _envelope_extent_at_y(cx, cy, w, h, anchor_y)
            if ae is None:
                continue
            ae_l, ae_r = ae
            target_l = bx0 + (k * (basket_w - 1)) // 3
            target_r = bx1 - (k * (basket_w - 1)) // 3
            pygame.draw.line(surf, rope,
                             (int(ae_l), int(anchor_y)),
                             (target_l, basket_top_y), 1)
            pygame.draw.line(surf, rope,
                             (int(ae_r), int(anchor_y)),
                             (target_r, basket_top_y), 1)
        _draw_basket(surf, cx, basket_top_y, basket_w, basket_h,
                     weave=True, passenger=True)


# ──────────── 07a2 Load ring ────────────

def draw_balloons_paneled_loadring(surf: pygame.Surface, palette: dict) -> None:
    """Paneled balloons with a small darker load-ring directly below the
    envelope. Top ropes converge into the ring; a short set of taut ropes
    drops from the ring straight down to the basket."""
    rope = (40, 28, 18)
    for cx, cy, w, h, pa, pb, seam in _BALLOONS_SMALL:
        cx, cy = int(cx), int(cy)
        _draw_paneled_envelope(surf, cx, cy, w, h, pa, pb, seam)
        env_bottom_y = int(cy + h / 2)
        # Load ring — a small dark ellipse just below envelope mouth
        ring_cy = env_bottom_y + 4
        ring_w = max(6, int(w * 0.28))
        ring_h = max(2, int(w * 0.10))
        pygame.draw.ellipse(surf, (35, 25, 18),
                            (cx - ring_w // 2, ring_cy - ring_h // 2,
                             ring_w, ring_h))
        pygame.draw.ellipse(surf, (90, 65, 35),
                            (cx - ring_w // 2 + 1, ring_cy - ring_h // 2 + 1,
                             max(2, ring_w - 2), max(1, ring_h - 2)), 1)
        # 8 thin ropes from envelope underside converging into the ring
        for k in range(4):
            u = (k + 0.5) / 4   # spread evenly
            anchor_y = cy + h * (0.10 + u * 0.35)
            ae = _envelope_extent_at_y(cx, cy, w, h, anchor_y)
            if ae is None:
                continue
            ae_l, ae_r = ae
            ring_left  = cx - ring_w // 2 + 1
            ring_right = cx + ring_w // 2 - 1
            pygame.draw.line(surf, rope,
                             (int(ae_l), int(anchor_y)),
                             (ring_left, ring_cy), 1)
            pygame.draw.line(surf, rope,
                             (int(ae_r), int(anchor_y)),
                             (ring_right, ring_cy), 1)
        # Basket — a small gap below the ring
        basket_top_y = ring_cy + 4
        basket_w = max(10, int(w * 0.40))
        basket_h = max(6, int(h * 0.20))
        # 4 short taut ropes from ring down to basket corners
        for x_off in (-ring_w // 2 + 1, -1, 1, ring_w // 2 - 1):
            target_x = cx + int(x_off * (basket_w / max(1, ring_w)))
            pygame.draw.line(surf, rope,
                             (cx + x_off, ring_cy),
                             (target_x, basket_top_y), 1)
        _draw_basket(surf, cx, basket_top_y, basket_w, basket_h,
                     weave=True, passenger=True)


# ──────────── 07a3 Suspension lattice ────────────

def draw_balloons_paneled_lattice(surf: pygame.Surface, palette: dict) -> None:
    """Paneled balloons with 8 mostly-parallel suspension cables running
    from the envelope's underside straight down to a wider basket. Looks
    like real suspension rigging."""
    rope = (45, 30, 20)
    for cx, cy, w, h, pa, pb, seam in _BALLOONS_SMALL:
        cx, cy = int(cx), int(cy)
        _draw_paneled_envelope(surf, cx, cy, w, h, pa, pb, seam)
        env_bottom_y = int(cy + h / 2)
        # Basket — wider so the lattice reads as parallel
        basket_top_y = env_bottom_y + 6
        basket_w = max(12, int(w * 0.55))
        basket_h = max(6, int(h * 0.20))
        bx0 = cx - basket_w // 2
        # 8 suspension cables anchored along the envelope's lower curve,
        # each running near-vertical to a corresponding point on the
        # basket's top edge.
        n_cables = 8
        anchor_y = cy + h * 0.42
        ae = _envelope_extent_at_y(cx, cy, w, h, anchor_y)
        if ae is None:
            continue
        ae_l, ae_r = ae
        for k in range(n_cables):
            u = k / (n_cables - 1)
            ax = ae_l + (ae_r - ae_l) * u
            tx = bx0 + (basket_w - 1) * u
            pygame.draw.line(surf, rope,
                             (int(ax), int(anchor_y)),
                             (int(tx), basket_top_y), 1)
        _draw_basket(surf, cx, basket_top_y, basket_w, basket_h,
                     weave=True, passenger=True)


# ──────────── 07a4 Throat connector ────────────

def draw_balloons_paneled_throat(surf: pygame.Surface, palette: dict) -> None:
    """Paneled balloons with a short trapezoidal 'throat' piece directly
    connecting envelope to basket — minimal air gap, no exposed ropes."""
    for cx, cy, w, h, pa, pb, seam in _BALLOONS_SMALL:
        cx, cy = int(cx), int(cy)
        _draw_paneled_envelope(surf, cx, cy, w, h, pa, pb, seam)
        env_bottom_y = int(cy + h / 2)
        # Throat trapezoid
        throat_top_w = max(6, int(w * 0.30))
        throat_h = max(4, int(h * 0.14))
        basket_top_y = env_bottom_y + throat_h
        basket_w = max(10, int(w * 0.45))
        basket_h = max(6, int(h * 0.20))
        # Trapezoid corners: top is throat_top_w wide at envelope mouth,
        # bottom is basket_w wide at basket top.
        throat_pts = [
            (cx - throat_top_w // 2, env_bottom_y),
            (cx + throat_top_w // 2, env_bottom_y),
            (cx + basket_w // 2,     basket_top_y),
            (cx - basket_w // 2,     basket_top_y),
        ]
        pygame.draw.polygon(surf, (95, 65, 35), throat_pts)
        pygame.draw.polygon(surf, (50, 32, 18), throat_pts, 1)
        # Two visible vertical seams on the throat
        for x_off in (-throat_top_w // 4, throat_top_w // 4):
            tx_top = cx + x_off
            tx_bot = cx + int(x_off * (basket_w / max(1, throat_top_w)))
            pygame.draw.line(surf, (60, 42, 22),
                             (tx_top, env_bottom_y),
                             (tx_bot, basket_top_y), 1)
        _draw_basket(surf, cx, basket_top_y, basket_w, basket_h,
                     weave=True, passenger=True)


# ──────────── 07a5 Crown net ────────────

def draw_balloons_paneled_crown(surf: pygame.Surface, palette: dict) -> None:
    """Paneled balloons with crown ropes that start from HIGH on the
    envelope sides (around the equator) and converge tightly down to a
    small basket — feels like the basket is netted to the whole envelope."""
    rope = (40, 28, 18)
    for cx, cy, w, h, pa, pb, seam in _BALLOONS_SMALL:
        cx, cy = int(cx), int(cy)
        _draw_paneled_envelope(surf, cx, cy, w, h, pa, pb, seam)
        env_bottom_y = int(cy + h / 2)
        basket_top_y = env_bottom_y + 5
        basket_w = max(10, int(w * 0.34))
        basket_h = max(6, int(h * 0.20))
        bx0 = cx - basket_w // 2
        bx1 = cx + basket_w // 2
        # 4 crown anchors per side, starting at envelope equator (cy)
        # down to envelope mouth (cy + h*0.45). Each anchor sends one
        # rope to a corresponding point along the basket top.
        n_per_side = 4
        for k in range(n_per_side):
            u = k / (n_per_side - 1) if n_per_side > 1 else 0
            anchor_y = cy + h * (-0.05 + u * 0.50)  # equator → mouth
            ae = _envelope_extent_at_y(cx, cy, w, h, anchor_y)
            if ae is None:
                continue
            ae_l, ae_r = ae
            target_l = bx0 + int(u * (basket_w - 1))
            target_r = bx1 - int(u * (basket_w - 1))
            pygame.draw.line(surf, rope,
                             (int(ae_l), int(anchor_y)),
                             (target_l, basket_top_y), 1)
            pygame.draw.line(surf, rope,
                             (int(ae_r), int(anchor_y)),
                             (target_r, basket_top_y), 1)
        _draw_basket(surf, cx, basket_top_y, basket_w, basket_h,
                     weave=True, passenger=True)


# ──────────── 07b Burner glow (lit from within) ────────────

def draw_balloons_glow(surf: pygame.Surface, palette: dict) -> None:
    """Hot-air balloons with a visible burner flame and warm internal
    glow — atmospheric, evening-fire vibe."""
    balloons = [
        (W * 0.22, H * 0.32, 54, 68, (220,  85,  85), (255, 200, 130)),
        (W * 0.58, H * 0.46, 44, 56, (95,  150, 215), (255, 200, 130)),
        (W * 0.84, H * 0.26, 38, 48, (235, 165,  85), (255, 220, 150)),
    ]
    for cx, cy, w, h, body, accent in balloons:
        cx, cy = int(cx), int(cy)
        # Envelope outline
        outline = _teardrop_polygon(cx, cy, w, h)
        pygame.draw.polygon(surf, body, outline)
        # Vertical accent stripe (thin)
        pygame.draw.line(surf, accent,
                         (cx, int(cy - h / 2 + 4)),
                         (cx, int(cy + h / 2 - 4)), 2)
        # Warm wash: gradient band ramping from transparent at envelope
        # mid down to warm at the bottom mouth. Body color dominates the
        # upper portion; only the lower third gets the burner-lit feel.
        warm = pygame.Surface((W, H), pygame.SRCALPHA)
        band_top_y = int(cy)
        band_bot_y = int(cy + h * 0.50)
        for y_int in range(band_top_y, band_bot_y + 1):
            u = (y_int - band_top_y) / max(1, band_bot_y - band_top_y)
            a = int(110 * (u ** 1.6))
            if a <= 2:
                continue
            ext = _envelope_extent_at_y(cx, cy, w, h, y_int)
            if ext is None:
                continue
            lx, rx = ext
            pygame.draw.line(warm, (255, 205, 140, a),
                             (int(lx) + 1, y_int),
                             (int(rx) - 1, y_int), 1)
        surf.blit(warm, (0, 0))
        # Outline on top
        pygame.draw.polygon(surf, (60, 30, 25), outline, 1)
        # Burner flame at the bottom mouth — small and bright
        bx = cx
        by = int(cy + h / 2 - 1)
        flame = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.ellipse(flame, (255, 235, 150, 230), (bx - 2, by - 3, 4, 6))
        pygame.draw.ellipse(flame, (255, 180,  90, 180), (bx - 3, by - 1, 6, 7))
        surf.blit(flame, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        # Ropes + basket
        env_bottom_y = int(cy + h / 2)
        basket_top_y = env_bottom_y + 10
        basket_w = max(12, int(w * 0.32))
        _draw_ropes(surf, cx, env_bottom_y, cx, basket_top_y, basket_w, w)
        _draw_basket(surf, cx, basket_top_y, basket_w, 9,
                     weave=True, passenger=True)


# ──────────── 07c Painterly (radial-gradient shading) ────────────

def draw_balloons_painterly(surf: pygame.Surface, palette: dict) -> None:
    """Soft radial gradient shading for a 3-D painted look. Light comes
    from the upper-left so the right/lower side falls into shadow."""
    balloons = [
        (W * 0.22, H * 0.32, 56, 72, (235, 95, 95)),
        (W * 0.58, H * 0.46, 46, 58, (95, 175, 230)),
        (W * 0.83, H * 0.24, 38, 50, (245, 180, 80)),
    ]
    for cx, cy, w, h, base in balloons:
        cx, cy = int(cx), int(cy)
        # Build an offscreen surface for the envelope so we can paint
        # gradient shading and then blit.
        pad = 10
        env_surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
        local_cx = w // 2 + pad
        local_cy = h // 2 + pad
        # Light direction: upper-left at ~ (-0.7, -0.7)
        light = (-0.7, -0.7)
        for y_int in range(0, h + pad * 2):
            for x_int in range(0, w + pad * 2):
                lx = x_int - local_cx
                ly = y_int - local_cy
                # Inside teardrop?
                rx, ry = w / 2, h / 2
                # World coords for the helper
                ext = _envelope_extent_at_y(local_cx, local_cy, w, h, y_int)
                if ext is None:
                    continue
                lxx, rxx = ext
                if x_int < lxx or x_int > rxx:
                    continue
                # Surface normal approx: vector from center, normalized
                d = math.hypot(lx, ly)
                if d < 1e-3:
                    nx, ny = 0, -1
                else:
                    nx, ny = lx / d, ly / d
                # Lambert shading factor
                lambert = max(0.15, nx * light[0] + ny * light[1])
                # Specular highlight bump near the upper-left
                hl_dx = lx - light[0] * rx * 0.55
                hl_dy = ly - light[1] * ry * 0.55
                hl = max(0.0, 1 - math.hypot(hl_dx, hl_dy) / (rx * 0.45))
                # Blend
                shade = 0.55 + 0.55 * lambert
                r = min(255, int(base[0] * shade + 255 * 0.35 * hl))
                g = min(255, int(base[1] * shade + 255 * 0.35 * hl))
                b = min(255, int(base[2] * shade + 255 * 0.35 * hl))
                env_surf.set_at((x_int, y_int), (r, g, b, 255))
        # Outline (slightly darker than base)
        outline = _teardrop_polygon(local_cx, local_cy, w, h)
        pygame.draw.polygon(env_surf,
                            (max(0, base[0] - 100),
                             max(0, base[1] - 100),
                             max(0, base[2] - 100)),
                            outline, 1)
        # Composite envelope
        rect = env_surf.get_rect(center=(cx, cy))
        surf.blit(env_surf, rect.topleft)
        # Soft cast shadow under the basket
        env_bottom_y = int(cy + h / 2)
        basket_top_y = env_bottom_y + 10
        basket_w = max(12, int(w * 0.32))
        shadow = pygame.Surface((basket_w + 14, 5), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70),
                            (0, 0, basket_w + 14, 5))
        surf.blit(shadow, (cx - (basket_w + 14) // 2,
                           basket_top_y + 11))
        # Ropes + basket
        _draw_ropes(surf, cx, env_bottom_y, cx, basket_top_y, basket_w, w)
        _draw_basket(surf, cx, basket_top_y, basket_w, 9,
                     weave=True, passenger=True)


# ──────────── 07d Festival patterns ────────────

def draw_balloons_festival(surf: pygame.Surface, palette: dict) -> None:
    """Three balloons each with a different decorative motif: polka dots,
    harlequin diamonds, and chevron stripes."""
    balloons = [
        # cx, cy, w, h, motif, base, motif_color
        (W * 0.22, H * 0.32, 56, 70, "dots",     (215,  55,  55), (250, 240, 220)),
        (W * 0.58, H * 0.46, 46, 58, "harlequin",(255, 205,  85), (210,  60, 110)),
        (W * 0.84, H * 0.24, 38, 48, "chevron",  (90, 165, 220), (240, 240, 240)),
    ]
    for cx, cy, w, h, motif, base, accent in balloons:
        cx, cy = int(cx), int(cy)
        outline = _teardrop_polygon(cx, cy, w, h)
        pygame.draw.polygon(surf, base, outline)

        # Each motif is rendered to a w×h SRCALPHA layer, then masked
        # by the envelope outline.
        layer = pygame.Surface((W, H), pygame.SRCALPHA)
        if motif == "dots":
            rnd = random.Random(11)
            for _ in range(28):
                px = rnd.randint(int(cx - w / 2), int(cx + w / 2))
                py = rnd.randint(int(cy - h / 2), int(cy + h / 2))
                ext = _envelope_extent_at_y(cx, cy, w, h, py)
                if ext is None or not (ext[0] + 2 <= px <= ext[1] - 2):
                    continue
                pygame.draw.circle(layer, (*accent, 255), (px, py),
                                   rnd.choice((2, 2, 3)))
        elif motif == "harlequin":
            # Diamond grid — alternate cells get the accent color
            cell = 8
            for iy in range(int(cy - h / 2), int(cy + h / 2) + 1, cell):
                for ix in range(int(cx - w / 2 - cell), int(cx + w / 2 + cell), cell):
                    row = (iy // cell)
                    col = (ix // cell)
                    if (row + col) % 2 != 0:
                        continue
                    # Diamond polygon centered at (ix, iy)
                    diamond = [
                        (ix, iy - cell // 2),
                        (ix + cell // 2, iy),
                        (ix, iy + cell // 2),
                        (ix - cell // 2, iy),
                    ]
                    # Clip each vertex to envelope vertically
                    pygame.draw.polygon(layer, (*accent, 255), diamond)
        elif motif == "chevron":
            # Three horizontal chevron bands
            for k, by in enumerate((cy - h * 0.30, cy - h * 0.05, cy + h * 0.20)):
                ext = _envelope_extent_at_y(cx, cy, w, h, by)
                if ext is None:
                    continue
                lx, rx = ext
                pts = [
                    (lx + 1, by - 3),
                    (cx,     by + 4),
                    (rx - 1, by - 3),
                    (rx - 1, by + 1),
                    (cx,     by + 8),
                    (lx + 1, by + 1),
                ]
                pygame.draw.polygon(layer, (*accent, 255), pts)

        # Mask: only keep motif pixels that lie inside the envelope.
        mask = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), outline)
        # Use BLEND_RGBA_MIN to intersect alpha channels (motif AND mask).
        layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(layer, (0, 0))

        # Outline on top
        pygame.draw.polygon(surf,
                            (max(0, base[0] - 80),
                             max(0, base[1] - 80),
                             max(0, base[2] - 80)),
                            outline, 1)
        # Highlight pop
        hi = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(hi, (255, 255, 255, 60),
                            (4, 4, max(6, w // 3), max(6, h // 3)))
        surf.blit(hi, (cx - w // 2, cy - h // 2))
        # Ropes + basket
        env_bottom_y = int(cy + h / 2)
        basket_top_y = env_bottom_y + 9
        basket_w = max(12, int(w * 0.32))
        _draw_ropes(surf, cx, env_bottom_y, cx, basket_top_y, basket_w, w)
        _draw_basket(surf, cx, basket_top_y, basket_w, 9,
                     weave=True, passenger=True)


# ──────────── 07e Alto-style minimal cinematic ────────────

def draw_balloons_alto(surf: pygame.Surface, palette: dict) -> None:
    """Two larger balloons in flat single colors with restrained detail —
    Alto's-Adventure-style cinematic minimalism. Negative space lets the
    sky breathe."""
    balloons = [
        # Larger hero balloon, lower-left
        (W * 0.28, H * 0.42, 78, 100, (210,  70,  70)),
        # Smaller companion, upper-right
        (W * 0.78, H * 0.18, 50, 64,  (60, 130, 200)),
    ]
    for cx, cy, w, h, color in balloons:
        cx, cy = int(cx), int(cy)
        outline = _teardrop_polygon(cx, cy, w, h, n=48)
        # Flat fill
        pygame.draw.polygon(surf, color, outline)
        # Single subtle shadow band on the lower-right (one elliptical
        # darken region, low alpha)
        shade_layer = pygame.Surface((W, H), pygame.SRCALPHA)
        shade_color = (max(0, color[0] - 60), max(0, color[1] - 60),
                       max(0, color[2] - 60), 110)
        pygame.draw.ellipse(shade_layer, shade_color,
                            (cx - 3, cy - h // 4,
                             w // 2 + 4, h - h // 4))
        # Mask shade to envelope
        mask = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), outline)
        shade_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(shade_layer, (0, 0))
        # Tiny single-color band at the equator (no outline, no panels)
        ext = _envelope_extent_at_y(cx, cy, w, h, cy + 2)
        if ext is not None:
            lx, rx = ext
            pygame.draw.line(surf,
                             (max(0, color[0] - 40), max(0, color[1] - 40),
                              max(0, color[2] - 40)),
                             (int(lx + 2), int(cy + 2)),
                             (int(rx - 2), int(cy + 2)), 2)
        # Ropes + basket — minimal, no weave
        env_bottom_y = int(cy + h / 2)
        basket_top_y = env_bottom_y + 14
        basket_w = max(14, int(w * 0.30))
        _draw_ropes(surf, cx, env_bottom_y, cx, basket_top_y, basket_w, w)
        _draw_basket(surf, cx, basket_top_y, basket_w, int(h * 0.13),
                     weave=False, passenger=False)


def draw_hot_air_balloons(surf: pygame.Surface, palette: dict) -> None:
    """Three colorful hot-air balloons drifting at mid-distance."""
    rnd = random.Random(303)
    # (cx, cy, scale, body_color, accent_color)
    balloons = [
        (W * 0.20, H * 0.30, 1.10, (235,  90,  90), (250, 220, 100)),
        (W * 0.55, H * 0.42, 0.90, (110, 170, 230), (240, 240, 240)),
        (W * 0.83, H * 0.22, 0.80, (245, 175,  80), (180,  90, 150)),
    ]
    for cx, cy, sc, body, accent in balloons:
        cx, cy = int(cx), int(cy)
        bw = int(28 * sc)
        bh = int(34 * sc)
        # Envelope (teardrop-ish)
        env = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)
        pygame.draw.ellipse(surf, body, env)
        # Vertical accent stripe
        stripe = pygame.Rect(cx - 2, env.top, 4, bh)
        pygame.draw.rect(surf, accent, stripe)
        # Horizontal accent band near bottom of envelope
        band = pygame.Rect(env.left + 2, env.bottom - int(6 * sc), bw - 4, max(2, int(3 * sc)))
        pygame.draw.rect(surf, accent, band)
        # Highlight on the upper-left of the envelope
        hi = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.ellipse(hi, (255, 255, 255, 60),
                            (3, 3, max(4, bw // 2 - 4), max(4, bh // 2 - 4)))
        surf.blit(hi, env.topleft)
        # Ropes
        rope_color = (40, 30, 20)
        bx = env.left + 4
        by = env.bottom
        bx2 = env.right - 4
        basket_top = env.bottom + int(7 * sc)
        basket_w = int(11 * sc)
        basket_h = int(7 * sc)
        basket_x = cx - basket_w // 2
        pygame.draw.line(surf, rope_color, (bx, by), (basket_x + 1, basket_top), 1)
        pygame.draw.line(surf, rope_color, (bx2, by), (basket_x + basket_w - 1, basket_top), 1)
        # Basket
        pygame.draw.rect(surf, (110, 70, 35),
                         (basket_x, basket_top, basket_w, basket_h))
        pygame.draw.rect(surf, (70, 45, 22),
                         (basket_x, basket_top, basket_w, basket_h), 1)


def draw_windmill(surf: pygame.Surface, palette: dict) -> None:
    """Silhouetted windmill on a far hill with 4-blade sails."""
    # Sit on the silhouette of the near mountain — match its color slightly darker.
    near = palette.get('mtn_near', (90, 90, 110))
    silhouette = (max(0, near[0] - 35),
                  max(0, near[1] - 35),
                  max(0, near[2] - 35))

    base_x = int(W * 0.32)
    base_y = GROUND_Y - 22
    # Trapezoidal tower (wider at base)
    tower = [
        (base_x - 10, base_y),
        (base_x + 10, base_y),
        (base_x + 6,  base_y - 28),
        (base_x - 6,  base_y - 28),
    ]
    pygame.draw.polygon(surf, silhouette, tower)
    # Roof cap (small triangle / dome)
    pygame.draw.polygon(surf, silhouette, [
        (base_x - 7, base_y - 28),
        (base_x + 7, base_y - 28),
        (base_x,     base_y - 35),
    ])
    # Hub
    hub_x, hub_y = base_x, base_y - 30
    pygame.draw.circle(surf, silhouette, (hub_x, hub_y), 2)
    # Four sails — 45° X cross. Each sail = a thin rectangle rotated.
    sail_len = 18
    sail_w = 4
    for k in range(4):
        ang = math.pi / 4 + k * math.pi / 2  # 45, 135, 225, 315
        # Rectangle from hub outward; built as polygon
        cos, sin = math.cos(ang), math.sin(ang)
        # Two perpendicular vectors
        px, py = -sin, cos
        # Sail corners
        corners = [
            (hub_x + px * sail_w * 0.5,                      hub_y + py * sail_w * 0.5),
            (hub_x - px * sail_w * 0.5,                      hub_y - py * sail_w * 0.5),
            (hub_x + cos * sail_len - px * sail_w * 0.5,     hub_y + sin * sail_len - py * sail_w * 0.5),
            (hub_x + cos * sail_len + px * sail_w * 0.5,     hub_y + sin * sail_len + py * sail_w * 0.5),
        ]
        pygame.draw.polygon(surf, silhouette, corners)


def draw_paper_lanterns(surf: pygame.Surface, palette: dict) -> None:
    """Cluster of glowing paper lanterns rising from a small pagoda silhouette."""
    # Tiny pagoda silhouette on a far hill
    pag_x = int(W * 0.50)
    pag_y = GROUND_Y - 18
    silh = (15, 15, 25)
    # Body
    pygame.draw.rect(surf, silh, (pag_x - 6, pag_y - 14, 12, 14))
    # Lower roof (wide trapezoid)
    pygame.draw.polygon(surf, silh, [
        (pag_x - 11, pag_y - 14),
        (pag_x + 11, pag_y - 14),
        (pag_x + 8,  pag_y - 17),
        (pag_x - 8,  pag_y - 17),
    ])
    # Upper roof
    pygame.draw.polygon(surf, silh, [
        (pag_x - 8, pag_y - 17),
        (pag_x + 8, pag_y - 17),
        (pag_x + 5, pag_y - 21),
        (pag_x - 5, pag_y - 21),
    ])
    # Spire
    pygame.draw.line(surf, silh, (pag_x, pag_y - 21), (pag_x, pag_y - 26), 1)

    # Lanterns rising — a vertical column of glowing dots, denser near the base
    rnd = random.Random(404)
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    n_lanterns = 14
    for i in range(n_lanterns):
        u = i / max(1, n_lanterns - 1)  # 0 at base → 1 at sky
        # Lateral drift increases as they rise
        drift = (rnd.uniform(-1, 1)) * (10 + u * 60)
        lx = pag_x + drift + rnd.uniform(-4, 4)
        ly = (pag_y - 28) - u * 220 + rnd.uniform(-6, 6)
        # Lantern intensity fades slightly as they rise (further away)
        warm = (255, 190, 110)
        glow_a = int(180 - u * 60)
        bloom_a = int(70 - u * 20)
        # Rectangle "lantern" body — tiny
        body_w, body_h = 3, 4
        rect = pygame.Rect(int(lx) - body_w // 2, int(ly) - body_h // 2, body_w, body_h)
        pygame.draw.rect(layer, (*warm, max(140, glow_a)), rect)
        # Bloom
        pygame.draw.circle(layer, (255, 200, 130, max(20, bloom_a)),
                           (int(lx), int(ly)), 5)
        pygame.draw.circle(layer, (255, 220, 160, max(40, bloom_a + 30)),
                           (int(lx), int(ly)), 2)
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_cherry_blossoms(surf: pygame.Surface, palette: dict) -> None:
    """Drifting pink cherry blossom petals across the screen."""
    rnd = random.Random(505)
    # 30 petals scattered, with size & opacity varying for depth
    for _ in range(34):
        x = rnd.randint(-6, W + 6)
        y = rnd.randint(20, GROUND_Y - 20)
        scale = rnd.uniform(0.6, 1.3)
        r = max(2, int(3 * scale))
        # Pink palette — vary lightness
        pink = rnd.choice((
            (255, 195, 215),
            (250, 175, 200),
            (245, 210, 225),
            (255, 220, 230),
        ))
        # Tilt the petal — render as a rotated ellipse approximation:
        # two overlapping ellipses at 45°.
        ang = rnd.uniform(0, math.tau)
        # Build a small rotated petal shape on a tiny surface
        petal = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.ellipse(petal, (*pink, 220),
                            (0, r, r * 4, r * 2))
        # Notch in the center to suggest the cleft
        pygame.draw.circle(petal, (0, 0, 0, 0),
                           (r * 2, r * 2), max(1, r // 2))
        rotated = pygame.transform.rotate(petal, math.degrees(ang))
        rect = rotated.get_rect(center=(x, y))
        surf.blit(rotated, rect.topleft)


def draw_parrot_family(surf: pygame.Surface, palette: dict) -> None:
    """Distant flyby of small colorful parrots in a loose diagonal line.

    Unlike the V-flock (silhouettes), Pip's family is recognizable as
    parrots — colorful body + visible beak — but still small enough to
    sit at mid-far parallax depth."""
    rnd = random.Random(606)
    # 5 parrots in a loose diagonal line, drifting up-and-right
    leaders = [
        (W * 0.12, H * 0.55),
        (W * 0.30, H * 0.46),
        (W * 0.48, H * 0.40),
        (W * 0.66, H * 0.34),
        (W * 0.84, H * 0.28),
    ]
    body_palette = [
        (235,  60,  55),  # scarlet (Pip-like)
        (240, 180,  60),  # gold
        (90,  170, 235),  # blue
        (90,  200,  90),  # green
        (235, 110, 200),  # pink
    ]
    rnd.shuffle(body_palette)
    for (px, py), color in zip(leaders, body_palette):
        px, py = int(px), int(py)
        # Body — small ellipse
        pygame.draw.ellipse(surf, color, (px - 5, py - 3, 10, 6))
        # Wing flaps — small dark stroke on top
        wing_dark = (max(0, color[0] - 90),
                     max(0, color[1] - 90),
                     max(0, color[2] - 90))
        # Two upstroke wing lines (mid-flap)
        pygame.draw.line(surf, wing_dark, (px - 4, py - 3), (px - 6, py - 6), 2)
        pygame.draw.line(surf, wing_dark, (px + 4, py - 3), (px + 6, py - 6), 2)
        # Beak — tiny yellow triangle pointing right
        pygame.draw.polygon(surf, (240, 200, 80), [
            (px + 5, py - 1),
            (px + 8, py),
            (px + 5, py + 1),
        ])
        # Eye dot
        pygame.draw.circle(surf, (20, 15, 20), (px + 2, py - 1), 1)


# ──────────────── 15 Campfire camp ────────────────

def draw_campfire(surf: pygame.Surface, palette: dict) -> None:
    """Small campsite at night: tent silhouette + flickering fire +
    rising sparks + warm firelight halo."""
    cx = int(W * 0.40)
    base_y = GROUND_Y - 24
    tent_silh = (165, 90, 65)   # lighter brown so the tent reads at night
    tent_dark = ( 90, 50, 35)

    # Tent (triangular silhouette) to the right of the fire — bigger
    tent_cx = cx + 28
    tent_h = 22
    tent_half_w = 14
    pygame.draw.polygon(surf, tent_silh, [
        (tent_cx - tent_half_w, base_y),
        (tent_cx + tent_half_w, base_y),
        (tent_cx,               base_y - tent_h),
    ])
    # Tent door — darker triangle in the center
    pygame.draw.polygon(surf, tent_dark, [
        (tent_cx - 4, base_y),
        (tent_cx + 4, base_y),
        (tent_cx,     base_y - 12),
    ])
    # Tent center seam — front-edge ridge
    pygame.draw.line(surf, tent_dark,
                     (tent_cx, base_y - tent_h),
                     (tent_cx, base_y - 12), 1)
    # Side seams
    pygame.draw.line(surf, tent_dark,
                     (tent_cx - tent_half_w + 1, base_y - 1),
                     (tent_cx, base_y - tent_h + 1), 1)
    pygame.draw.line(surf, tent_dark,
                     (tent_cx + tent_half_w - 1, base_y - 1),
                     (tent_cx, base_y - tent_h + 1), 1)

    # Logs around fire — two small dark crossed sticks
    pygame.draw.line(surf, (40, 25, 15),
                     (cx - 5, base_y - 1), (cx + 5, base_y - 1), 2)
    pygame.draw.line(surf, (45, 28, 16),
                     (cx - 4, base_y - 2), (cx + 4, base_y - 2), 1)

    # Flame — layered ellipses, hottest in the centre
    flame = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.ellipse(flame, (255,  90,  50, 200), (cx - 5, base_y - 7,  10, 8))
    pygame.draw.ellipse(flame, (255, 150,  60, 230), (cx - 4, base_y - 8,   8, 8))
    pygame.draw.ellipse(flame, (255, 210, 110, 240), (cx - 2, base_y - 8,   5, 7))
    pygame.draw.ellipse(flame, (255, 240, 180, 250), (cx - 1, base_y - 6,   3, 4))
    # Top tongue (taller)
    pygame.draw.ellipse(flame, (255, 200, 100, 200), (cx - 1, base_y - 11,  3, 5))
    surf.blit(flame, (0, 0))
    # Bright core highlight
    pygame.draw.circle(surf, (255, 250, 220), (cx, base_y - 5), 1)

    # Rising sparks
    spark_layer = pygame.Surface((W, H), pygame.SRCALPHA)
    rnd = random.Random(710)
    for _ in range(14):
        sx = cx + rnd.randint(-7, 7)
        sy = base_y - rnd.randint(8, 38)
        a = rnd.randint(120, 230)
        col = rnd.choice(((255, 220, 130, a), (255, 180,  90, a),
                          (255, 240, 200, a)))
        pygame.draw.circle(spark_layer, col, (sx, sy), 1)
    surf.blit(spark_layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Warm firelight halo — smooth radial gradient (not concentric
    # circles). Built per-pixel: distance from the fire centre is
    # mapped through a quadratic falloff to RGB intensity, then blitted
    # additively so the small per-pixel RGB values just tint the
    # surrounding ground/tent without saturating to white.
    halo_radius = 30
    halo_size = halo_radius * 2 + 2
    halo = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
    hcx = hcy = halo_size // 2
    peak = (160, 80, 32)   # max additive contribution at the fire centre
    for y in range(halo_size):
        for x in range(halo_size):
            d = math.hypot(x - hcx, y - hcy)
            if d > halo_radius:
                continue
            u = d / halo_radius                    # 0 centre → 1 edge
            intensity = (1.0 - u) ** 2.4           # smooth quadratic
            r = int(peak[0] * intensity)
            g = int(peak[1] * intensity)
            b = int(peak[2] * intensity)
            if r + g + b > 0:
                halo.set_at((x, y), (r, g, b, 255))
    halo_rect = halo.get_rect(center=(cx, base_y - 4))
    surf.blit(halo, halo_rect.topleft, special_flags=pygame.BLEND_RGB_ADD)



# ──────────────── Driver ────────────────

SCENES = [
    ("01_shooting_stars",  0.62, draw_shooting_stars),
    ("02_v_flock",         0.18, draw_v_flock),
    ("03_lighthouse",      0.62, draw_lighthouse),
    ("04_fireflies",       0.48, draw_fireflies),
    ("05_fireworks",       0.62, draw_fireworks),
    ("06_aurora",          0.78, draw_aurora),
    ("07_hot_air_balloons", 0.16, draw_hot_air_balloons),
    ("07a_balloons_paneled",   0.16, draw_balloons_paneled),
    ("07a1_paneled_skirt",     0.16, draw_balloons_paneled_skirt),
    ("07a2_paneled_loadring",  0.16, draw_balloons_paneled_loadring),
    ("07a3_paneled_lattice",   0.16, draw_balloons_paneled_lattice),
    ("07a4_paneled_throat",    0.16, draw_balloons_paneled_throat),
    ("07a5_paneled_crown",     0.16, draw_balloons_paneled_crown),
    ("07b_balloons_glow",      0.16, draw_balloons_glow),
    ("07c_balloons_painterly", 0.16, draw_balloons_painterly),
    ("07d_balloons_festival",  0.16, draw_balloons_festival),
    ("07e_balloons_alto",      0.16, draw_balloons_alto),
    ("08_windmill",        0.04, draw_windmill),
    ("09_paper_lanterns",  0.60, draw_paper_lanterns),
    ("10_cherry_blossoms", 0.92, draw_cherry_blossoms),
    ("11_parrot_family",   0.08, draw_parrot_family),
    ("15_campfire_camp",          0.62, draw_campfire),
]


def main() -> None:
    for slug, phase, fn in SCENES:
        random.seed(42)  # deterministic backdrop variation
        world = _make_world(phase)
        surf = pygame.Surface((W, H))
        _draw_backdrop(surf, world)
        fn(surf, world.biome_palette)
        out = OUT_DIR / f"{slug}.png"
        pygame.image.save(surf, out)
        print(f"wrote {out}  phase={phase:.2f}")


if __name__ == "__main__":
    main()
