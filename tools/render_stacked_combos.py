"""Render gameplay screenshots of every reachable bird state — including
the 4 stacked-powerup combos that currently fall back to a single sprite
and silently lose the rest of the active modes.

Per the audit (game/Bird.draw lines 295–322), the cascade is:
    if kfc: KFC; elif ghost: Ghost; elif triple: Hat; else: default.
That means **kfc+hat**, **ghost+hat**, **kfc+ghost** and **kfc+ghost+hat**
all reach the bird's flag-True state but render only the highest-
precedence sprite. This tool builds the missing combo sprites and
renders them in real gameplay context for the user to review BEFORE we
land them in game/parrot.py + Bird.draw.

Output:

    docs/stacked_combos/v0_default.png
    docs/stacked_combos/v1_kfc.png            (already-correct reference)
    docs/stacked_combos/v2_ghost.png          (already-correct reference)
    docs/stacked_combos/v3_hat.png            (already-correct reference)
    docs/stacked_combos/v4_kfc_hat.png        (NEW — fried + stovepipe)
    docs/stacked_combos/v5_ghost_hat.png      (NEW — spectral + stovepipe)
    docs/stacked_combos/v6_kfc_ghost.png      (NEW — fried tinted cyan)
    docs/stacked_combos/v7_kfc_ghost_hat.png  (NEW — all three)
    docs/stacked_combos/compare.png           (labelled 1.5× zoom strip)

Run from the repo root:

    PYTHONPATH=. python tools/render_stacked_combos.py
"""
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


# ── Combo sprite builders (preview only — not in game/) ─────────────────────
def _hatted_composite(parrot_sprite, hat_fn, parrot_dy, hat_hx, hat_hy,
                       composite_w, composite_h):
    """Generic version of game.dollar_parrot_hat._build_hatted_frame — accepts
    any pre-built parrot surface so we can plug in fried, spectral, or a
    cyan-tinted hybrid."""
    composite = pygame.Surface((composite_w, composite_h), pygame.SRCALPHA)
    composite.blit(parrot_sprite, (0, parrot_dy))
    hat_fn(composite, hat_hx, hat_hy)
    return composite


def _cyan_tint_in_place(sprite, tint=(170, 230, 255), strength=0.55):
    """Shift a sprite's RGB toward a cool cyan while preserving its alpha
    silhouette. Used to derive a 'spectral fried' look from the standard
    KFC frame without rebuilding a new palette pixel-by-pixel.

    strength = 0 → original colour, 1 → fully cyan-replaced.
    Implementation: blend a solid cyan layer over the sprite using the
    sprite's alpha channel as the mask, at `strength` opacity."""
    sw, sh = sprite.get_size()
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((*tint, int(255 * strength)))
    # Mask the overlay to the sprite's silhouette so we don't leak cyan
    # into transparent regions.
    overlay.blit(sprite, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(overlay, (0, 0))


def build_kfc_hat_frames():
    """KFC fried parrot wearing the gold stovepipe hat."""
    from game import parrot
    from game.dollar_parrot_hat import (
        COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY, draw_stovepipe,
    )
    return [
        parrot._add_outline(_hatted_composite(
            parrot._build_fried_frame(a), draw_stovepipe,
            PARROT_DY, HAT_HX, HAT_HY, COMPOSITE_W, COMPOSITE_H,
        ))
        for a in parrot._WING_ANGLES
    ]


def build_ghost_hat_frames():
    """Ghost (spectral cyan) parrot wearing the gold stovepipe hat."""
    from game import parrot
    from game.dollar_parrot_ghost import build_spectral_frame
    from game.dollar_parrot_hat import (
        COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY, draw_stovepipe,
    )
    return [
        parrot._add_outline(_hatted_composite(
            build_spectral_frame(a), draw_stovepipe,
            PARROT_DY, HAT_HX, HAT_HY, COMPOSITE_W, COMPOSITE_H,
        ))
        for a in parrot._WING_ANGLES
    ]


def build_kfc_ghost_frames():
    """Fried parrot tinted toward ghost cyan. Cheap derivation: take the
    KFC frame and shift its RGB toward (170, 230, 255). Reads as 'spectral
    fried chicken'."""
    from game import parrot
    frames = []
    for a in parrot._WING_ANGLES:
        f = parrot._build_fried_frame(a).copy()
        _cyan_tint_in_place(f)
        frames.append(parrot._add_outline(f))
    return frames


def build_kfc_ghost_hat_frames():
    """Spectral fried parrot wearing the stovepipe hat."""
    from game import parrot
    from game.dollar_parrot_hat import (
        COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY, draw_stovepipe,
    )
    frames = []
    for a in parrot._WING_ANGLES:
        f = parrot._build_fried_frame(a).copy()
        _cyan_tint_in_place(f)
        composite = _hatted_composite(
            f, draw_stovepipe,
            PARROT_DY, HAT_HX, HAT_HY, COMPOSITE_W, COMPOSITE_H,
        )
        frames.append(parrot._add_outline(composite))
    return frames


# ── Gameplay scene helpers (mirror tools/take_screenshots.py) ───────────────
def draw_bg(surf, scroll=0.0, phase=0.62):
    from game.config import W, H, GROUND_Y
    from game import biome as _biome
    from game.draw import (
        get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
    )
    buckets = _biome.PHASE_BUCKETS
    bf = (phase % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    t = bf - int(bf)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None); surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255)); surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)
    for i, (bx, by, sc, var) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2), (60, 220, 0.8, 3),
             (230, 60, 0.7, 1), (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=var)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W, pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                pal['ground_top'], pal['ground_mid'], (60, 40, 25))


def render_bird_at(surf, sprite, cx, cy, tilt_deg=0.0, ghost_alpha=None):
    """Apply tilt (and optional ghost-mode alpha) to a sprite then blit
    centred on (cx, cy). Mirrors the scaling/rotation Bird.draw does."""
    img = pygame.transform.rotate(sprite, tilt_deg)
    if ghost_alpha is not None:
        img = img.copy()
        img.set_alpha(ghost_alpha)
    rect = img.get_rect(center=(cx, cy))
    surf.blit(img, rect.topleft)


def main():
    random.seed(42)
    pygame.init()
    pygame.font.init()

    from game.config import (
        W, H, KFC_DURATION, GHOST_DURATION, TRIPLE_DURATION, GROW_DURATION,
    )
    screen = pygame.display.set_mode((W, H))

    from game.world import World
    from game.hud import HUD
    from game import parrot
    from game.dollar_parrot_ghost import build_spectral_frame
    from game.dollar_parrot_hat import (
        COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY, draw_stovepipe,
    )

    world = World()
    world.score = 12
    world.coin_count = 7
    world.world_idle_tick(0.016)

    hud = HUD()
    hud.title_t = 0.8

    # Pre-build every sprite needed. Use frame index 1 (mid-flap) and
    # tilt 0° so each preview cell is the same pose.
    FRAME_IDX = 1
    TILT = 0.0
    GHOST_ALPHA = 130   # mid-breath alpha — what Bird.draw actually applies

    angle = parrot._WING_ANGLES[FRAME_IDX]

    # Cells: (label, sprite, ghost_alpha_or_none, hud_active_dict)
    # `hud_active_dict` controls the world's *_timer values so the buff
    # bar shows the correct icons for each combo.
    sprites = {
        "default":      parrot._add_outline(parrot._build_frame(angle)),
        "kfc":          parrot._add_outline(parrot._build_fried_frame(angle)),
        "ghost":        parrot._add_outline(build_spectral_frame(angle)),
        "hat":          parrot._add_outline(_hatted_composite(
                            parrot._build_frame(angle), draw_stovepipe,
                            PARROT_DY, HAT_HX, HAT_HY, COMPOSITE_W, COMPOSITE_H,
                        )),
        "kfc_hat":      build_kfc_hat_frames()[FRAME_IDX],
        "ghost_hat":    build_ghost_hat_frames()[FRAME_IDX],
        "kfc_ghost":    build_kfc_ghost_frames()[FRAME_IDX],
        "kfc_ghost_hat": build_kfc_ghost_hat_frames()[FRAME_IDX],
    }

    cells = [
        ("0 — default",            "default",       None,        {}),
        ("1 — kfc only",           "kfc",           None,        {"kfc": KFC_DURATION}),
        ("2 — ghost only",         "ghost",         GHOST_ALPHA, {"ghost": GHOST_DURATION}),
        ("3 — triple only",        "hat",           None,        {"triple": TRIPLE_DURATION}),
        ("4 — kfc + triple (NEW)", "kfc_hat",       None,        {"kfc": KFC_DURATION, "triple": TRIPLE_DURATION}),
        ("5 — ghost + triple (NEW)","ghost_hat",    GHOST_ALPHA, {"ghost": GHOST_DURATION, "triple": TRIPLE_DURATION}),
        ("6 — kfc + ghost (NEW)",  "kfc_ghost",     GHOST_ALPHA, {"kfc": KFC_DURATION, "ghost": GHOST_DURATION}),
        ("7 — kfc + ghost + triple (NEW)",
                                   "kfc_ghost_hat", GHOST_ALPHA, {"kfc": KFC_DURATION, "ghost": GHOST_DURATION, "triple": TRIPLE_DURATION}),
    ]

    out_dir = os.path.join("docs", "stacked_combos")
    os.makedirs(out_dir, exist_ok=True)
    full_frames: "list[pygame.Surface]" = []

    bird_x, bird_y = W * 0.40, H * 0.42

    for idx, (label, sprite_key, ghost_alpha, timers) in enumerate(cells):
        # Reset all relevant timers first, then set the ones for this combo.
        world.kfc_timer = 0.0
        world.ghost_timer = 0.0
        world.triple_timer = 0.0
        world.grow_timer = 0.0
        world.bird.kfc_active = False
        world.bird.ghost_active = False
        world.bird.grow_active = False
        for kind, dur in timers.items():
            setattr(world, f"{kind}_timer", dur)
            if hasattr(world.bird, f"{kind}_active"):
                setattr(world.bird, f"{kind}_active", True)
        # World loop normally derives triple_active from the timer.
        world.bird.triple_active = world.triple_timer > 0

        # Render the gameplay frame: bg, pipes, weather, bird, HUD.
        # We bypass Bird.draw (would render the buggy fallback) and
        # directly blit the combo sprite so the user sees what the
        # FIXED behaviour will look like.
        draw_bg(screen)
        for p in world.pipes:
            p.draw(screen, world.biome_palette)
        world.weather.draw(screen)
        for c in world.coins:
            c.draw(screen, kfc_active=world.bird.kfc_active,
                   triple_active=world.triple_timer > 0)
        render_bird_at(screen, sprites[sprite_key],
                       int(bird_x), int(bird_y),
                       tilt_deg=TILT, ghost_alpha=ghost_alpha)
        hud.draw_play(screen, world, best=18)

        frame = screen.copy()
        full_frames.append(frame)

        out_path = os.path.join(out_dir, f"v{idx}_{sprite_key}.png")
        pygame.image.save(frame, out_path)
        print(f"saved {out_path}  ({label})")

    # Comparison strip — tight crop around bird (incl. hat clearance), 1.5×.
    crop_w = 130
    crop_h = 150
    crop_x = max(0, min(W - crop_w, int(bird_x - crop_w / 2)))
    crop_y = max(0, min(H - crop_h, int(bird_y - crop_h / 2 - 10)))
    SCALE = 2
    cell_w = crop_w * SCALE
    cell_h = crop_h * SCALE

    n = len(cells)
    GAP = 22
    LABEL_H = 32
    PAD = 24
    canvas_w = cell_w * n + GAP * (n - 1) + PAD * 2
    canvas_h = cell_h + LABEL_H + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((230, 232, 235))
    font = pygame.font.SysFont(None, 22, bold=True)

    for i, (label, _k, _a, _t) in enumerate(cells):
        x = PAD + i * (cell_w + GAP)
        y = PAD
        crop = full_frames[i].subsurface(
            pygame.Rect(crop_x, crop_y, crop_w, crop_h)
        ).copy()
        scaled = pygame.transform.scale(crop, (cell_w, cell_h))
        pygame.draw.rect(canvas, (60, 70, 100),
                         pygame.Rect(x - 1, y - 1, cell_w + 2, cell_h + 2),
                         width=1)
        canvas.blit(scaled, (x, y))
        lbl = font.render(label, True, (30, 35, 55))
        canvas.blit(lbl, (x + (cell_w - lbl.get_width()) // 2, y + cell_h + 8))

    compare_path = os.path.join(out_dir, "compare.png")
    pygame.image.save(canvas, compare_path)
    print(f"saved {compare_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    sys.exit(main() or 0)
