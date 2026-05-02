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
    overlay.blit(sprite, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(overlay, (0, 0))


# ── Themed hat palettes ────────────────────────────────────────────────────
# Hats need to match the bird underneath. The default palette in
# game.dollar_parrot_hat is gold-on-dark-band; we override per combo so
# the hat reads as part of the fried/spectral/etc. theme instead of a
# floating gold artefact.
HAT_PALETTE_DEFAULT = {
    "bright":  (255, 240, 130),  # GOLD_LT
    "main":    (255, 200,  50),  # GOLD
    "mid":     (220, 165,  35),  # GOLD_MID
    "dark":    (160, 100,  20),  # GOLD_DK
    "band_dk": ( 35,  20,   8),
    "band_hi": ( 85,  55,  20),
    "dollar":     ( 75, 165, 105),  # BILL_GREEN
    "dollar_dk":  ( 40, 110,  70),
    "dollar_hi":  (140, 220, 170),  # subtle inner highlight
    "spot":       None,
    "spot_hi":    None,
}
HAT_PALETTE_KFC = {
    # Crispy fried-chicken tones — warm oranges/browns that match the
    # KFC bird's batter colours.
    "bright":  (245, 195, 110),
    "main":    (215, 145,  55),
    "mid":     (180, 110,  35),
    "dark":    (120,  70,  20),
    "band_dk": ( 65,  35,  10),
    "band_hi": (130,  80,  25),
    # `$` glyph in the KFC bird's DARKEST batter tone — reads as branded
    # / burnt into the warm hat body, same colour as the spots/crackles
    # the bird carries.
    "dollar":     ( 45,  22,   2),
    "dollar_dk":  ( 20,  10,   0),
    "dollar_hi":  (115,  70,  20),
    # Spot/bump tones for the fried-batter texture — high contrast vs.
    # the cylinder so they actually read at the 32-px native scale.
    "spot":       ( 75,  40,   5),
    "spot_hi":    (245, 200, 130),
}
HAT_PALETTE_GHOST = {
    # Spectral cyans that match the ghost bird's body palette.
    "bright":  (220, 245, 255),
    "main":    (140, 200, 230),
    "mid":     (100, 170, 210),
    "dark":    ( 55, 105, 155),
    "band_dk": ( 25,  55,  95),
    "band_hi": ( 90, 140, 180),
    # Strong pure-blue `$` — green channel pulled down so the glyph
    # doesn't read as cyan/teal-with-yellow against the cyan hat body.
    "dollar":    ( 25,  60, 230),
    "dollar_dk": (  5,  15,  95),
    "dollar_hi": (110, 150, 245),
    "spot":      None,   # ghost hat has no fried texture
    "spot_hi":   None,
}


def _draw_brim_themed(surf, hx, hy, half_w, P):
    """Themed version of game.dollar_parrot_hat._draw_brim — same geometry,
    palette swapped per combo."""
    sh = pygame.Surface((half_w * 2 + 8, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
    surf.blit(sh, (hx - half_w - 4, hy + 1))
    pygame.draw.ellipse(surf, P["band_dk"],
                        (hx - half_w - 1, hy, (half_w + 1) * 2, 7))
    pygame.draw.ellipse(surf, P["dark"],
                        (hx - half_w, hy - 1, half_w * 2, 6))
    pygame.draw.ellipse(surf, P["main"],
                        (hx - half_w + 1, hy, half_w * 2 - 2, 4))
    pygame.draw.line(surf, P["bright"],
                     (hx - half_w + 3, hy + 1), (hx + half_w - 3, hy + 1), 1)


def _draw_crown_cylinder_themed(surf, hx, hy, half_w, height, P):
    """Themed version of _draw_crown_cylinder."""
    top_y = hy - height
    left_x = hx - half_w
    w = half_w * 2

    pygame.draw.rect(surf, P["dark"], (left_x - 1, top_y + 1, w + 2, height - 2))
    pygame.draw.rect(surf, P["main"], (left_x, top_y + 2, w, height - 4))
    pygame.draw.rect(surf, P["bright"], (left_x + 2, top_y + 3, 2, height - 8))
    pygame.draw.rect(surf, P["mid"], (left_x + w - 3, top_y + 3, 2, height - 8))

    pygame.draw.ellipse(surf, P["dark"], (left_x - 1, hy - 4, w + 2, 7))
    pygame.draw.ellipse(surf, P["main"], (left_x, hy - 3, w, 5))

    pygame.draw.ellipse(surf, P["dark"], (left_x - 1, top_y - 1, w + 2, 6))
    pygame.draw.ellipse(surf, P["main"], (left_x + 1, top_y, w - 2, 4))
    pygame.draw.ellipse(surf, P["bright"], (left_x + 3, top_y + 1, w - 6, 1))

    band_h = max(3, height // 7)
    pygame.draw.rect(surf, P["band_dk"], (left_x, hy - band_h - 1, w, band_h))
    pygame.draw.line(surf, P["band_hi"],
                     (left_x + 1, hy - band_h - 1),
                     (left_x + w - 2, hy - band_h - 1), 1)


def _draw_fried_bumps(surf, hx, hy, crown_half, crown_h, P):
    """Two darker batter spots on the cylinder face — matches the KFC
    bird's spotty fried-chicken texture. Sized 5×4 with a 2×2 highlight
    so they actually read at the 32-px hat scale."""
    if P.get("spot") is None:
        return
    # Bump 1 — top-left of the cylinder, clear of the `$` zone.
    b1_cx = hx - crown_half + 4
    b1_cy = hy - crown_h + 9
    pygame.draw.ellipse(surf, P["spot"],
                        (b1_cx - 2, b1_cy - 2, 5, 4))
    pygame.draw.rect(surf, P["spot_hi"],
                     (b1_cx - 1, b1_cy - 2, 2, 2))
    # Bump 2 — bottom-right, just above the band.
    b2_cx = hx + crown_half - 5
    b2_cy = hy - 8
    pygame.draw.ellipse(surf, P["spot"],
                        (b2_cx - 2, b2_cy - 2, 5, 4))
    pygame.draw.rect(surf, P["spot_hi"],
                     (b2_cx - 1, b2_cy - 2, 2, 2))


def _draw_stovepipe_themed(surf, hx, hy, P):
    """Themed stovepipe — same geometry as game.dollar_parrot_hat.draw_stovepipe."""
    crown_half = 9
    crown_h = 28
    _draw_crown_cylinder_themed(surf, hx, hy, crown_half, crown_h, P)
    _draw_fried_bumps(surf, hx, hy, crown_half, crown_h, P)
    _draw_brim_themed(surf, hx, hy, half_w=17, P=P)

    # `$` glyph on the crown — themed colour per palette. Order:
    # (1) outline 8-direction stamps,
    # (2) body fill,
    # (3) tiny highlight stamp offset up-left so the glyph doesn't
    #     blend into a similar-tone hat body at native scale.
    import pathlib as _pl
    fpath = str(_pl.Path(__file__).resolve().parent.parent
                / "game" / "assets" / "LiberationSans-Bold.ttf")
    f = pygame.font.Font(fpath, 18)
    body = f.render("$", True, P["dollar"])
    edge = f.render("$", True, P["dollar_dk"])
    hi   = f.render("$", True, P["dollar_hi"])
    hi.set_alpha(160)
    cy = hy - crown_h // 2 - 1
    rect = body.get_rect(center=(hx, cy))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        surf.blit(edge, (rect.x + dx, rect.y + dy))
    surf.blit(body, rect.topleft)
    surf.blit(hi, (rect.x - 1, rect.y - 1))


def _stovepipe_kfc(surf, hx, hy):
    _draw_stovepipe_themed(surf, hx, hy, HAT_PALETTE_KFC)


def _stovepipe_ghost(surf, hx, hy):
    _draw_stovepipe_themed(surf, hx, hy, HAT_PALETTE_GHOST)


def build_kfc_hat_frames():
    """KFC fried parrot wearing a CRISPY hat (golden-brown palette)."""
    from game import parrot
    from game.dollar_parrot_hat import (
        COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY,
    )
    return [
        parrot._add_outline(_hatted_composite(
            parrot._build_fried_frame(a), _stovepipe_kfc,
            PARROT_DY, HAT_HX, HAT_HY, COMPOSITE_W, COMPOSITE_H,
        ))
        for a in parrot._WING_ANGLES
    ]


def build_ghost_hat_frames():
    """Ghost (spectral cyan) parrot wearing a SPECTRAL hat (cyan palette)."""
    from game import parrot
    from game.dollar_parrot_ghost import build_spectral_frame
    from game.dollar_parrot_hat import (
        COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY,
    )
    return [
        parrot._add_outline(_hatted_composite(
            build_spectral_frame(a), _stovepipe_ghost,
            PARROT_DY, HAT_HX, HAT_HY, COMPOSITE_W, COMPOSITE_H,
        ))
        for a in parrot._WING_ANGLES
    ]


def build_kfc_ghost_frames():
    """Fried parrot tinted toward ghost cyan. Cheap derivation."""
    from game import parrot
    frames = []
    for a in parrot._WING_ANGLES:
        f = parrot._build_fried_frame(a).copy()
        _cyan_tint_in_place(f)
        frames.append(parrot._add_outline(f))
    return frames


def build_kfc_ghost_hat_frames():
    """Spectral fried parrot wearing the KFC hat — but the cyan tint is
    applied to the whole composite (bird + hat) so the hat reads as
    spectral fried too, matching the bird underneath."""
    from game import parrot
    from game.dollar_parrot_hat import (
        COMPOSITE_W, COMPOSITE_H, PARROT_DY, HAT_HX, HAT_HY,
    )
    frames = []
    for a in parrot._WING_ANGLES:
        # Build kfc-themed bird+hat first (warm, fully fried look).
        composite = _hatted_composite(
            parrot._build_fried_frame(a), _stovepipe_kfc,
            PARROT_DY, HAT_HX, HAT_HY, COMPOSITE_W, COMPOSITE_H,
        ).copy()
        # Then cool the entire silhouette to spectral.
        _cyan_tint_in_place(composite)
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
