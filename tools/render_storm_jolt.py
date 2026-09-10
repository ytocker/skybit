"""Render a storm-jolt sequence: Pip flying in heavy storm, then a
sudden gust strips ~50 coins off his belly in a 360° spread.

Produces 6 PNGs under docs/screenshots/storm_jolt/:
  00_contact_sheet.png — all five frames side-by-side
  01_pre_jolt.png      — Pip flying in storm (shiver visible)
  02_fire.png          — instant jolt fired, coins just spawned
  03_spread.png        — coins mid-flight, radial spread peaks
  04_settle.png        — coins arc out, "-50!" text visible
  05_after.png         — coins faded, Pip down 50 coins

Run from repo root:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_storm_jolt
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import random
import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y, BIRD_X
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.world import World
from game.entities import Coin
import math


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "storm_jolt")
os.makedirs(OUT_DIR, exist_ok=True)


def render_world(world, target):
    """Paint background + entities so each frame reads as a real
    gameplay snapshot."""
    phase = world.biome_phase
    pal = _biome.palette_for_phase(phase)
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    target.blit(sky, (0, 0))
    # A few drifting clouds for atmosphere.
    for i, (bx, by, sc, variant) in enumerate(
            ((20, 90, 0.9, 0), (220, 130, 1.0, 2),
             (90, 200, 0.8, 3))):
        draw_cloud(target, bx, by, sc, variant=variant)
    draw_mountains(target, world.bg_scroll, GROUND_Y, W,
                   pal["mtn_far"], pal["mtn_near"])
    draw_ground(target, GROUND_Y, W, H, world.bg_scroll,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    # Pipes, coins, particles, bird.
    for p in world.pipes:
        p.draw(target)
    for c in world.coins:
        c.draw(target)
    for p in world.particles:
        p.draw(target)
    world.bird.draw(target, flipped=False)
    # Float texts on top.
    for t in world.float_texts:
        t.draw(target)
    # Weather render on top of everything so rain streaks read.
    world.weather.draw(target)
    # Lightning bolt — drawn last so the bright core sits over weather.
    from game.scenes import _draw_lightning_bolt
    _draw_lightning_bolt(target, world.lightning_strike)


def setup_storm_world():
    """Build a world in mid-dusk-storm so weather hooks fire."""
    random.seed(7)
    w = World()
    w.ready_t = 0
    # Drive biome to peak storm (~phase 0.50). cycle is 300 s, so 150 s.
    w.biome_time = _biome.CYCLE_SECONDS * 0.50
    # Spin the weather a few frames so streaks populate.
    for _ in range(60):
        w.weather.update(1 / 60, w.biome_phase)
    # Give Pip plenty of coins to lose so the -50 lands cleanly.
    w.coin_count = 120
    w.score = 120
    # A few stable coins in flight so the scene reads as gameplay.
    for k in range(4):
        w.coins.append(Coin(220 + k * 35, 280 + (k % 2) * 20))
    # One pipe in the background so the frame isn't empty.
    w._spawn_pipe(W + 60)
    return w


def save_frame(surf, name, label=None):
    """Persist a frame. If label is given, overlay a small caption at
    the top so the contact sheet reads as a sequence."""
    out = surf.copy()
    if label:
        font = pygame.font.SysFont("Arial", 14, bold=True)
        img = font.render(label, True, (255, 255, 255))
        bg = pygame.Surface((img.get_width() + 12, img.get_height() + 6),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        out.blit(bg, (6, 6))
        out.blit(img, (12, 9))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(out, path)
    print(f"  saved {path}")
    return out


def make_contact_sheet(frames, name):
    """5-up horizontal contact sheet — frames are tiles."""
    margin = 8
    sw = W // 2
    sh = H // 2
    total_w = sw * len(frames) + margin * (len(frames) + 1)
    total_h = sh + margin * 2
    sheet = pygame.Surface((total_w, total_h))
    sheet.fill((20, 20, 28))
    for i, fr in enumerate(frames):
        small = pygame.transform.smoothscale(fr, (sw, sh))
        sheet.blit(small, (margin + i * (sw + margin), margin))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(sheet, path)
    print(f"  saved {path}")


def main():
    surf = pygame.Surface((W, H))
    frames = []

    # Frame 1: Pre-jolt — Pip flying in heavy storm. Run _apply_weather_effects
    # a few frames so the shiver fields are non-zero on the rendered frame.
    # Force the lockout HIGH so the random roll inside _apply_weather_effects
    # can't fire the jolt prematurely (we want to control when it fires).
    w = setup_storm_world()
    w._storm_jolt_lockout = 999.0
    for _ in range(8):
        w._apply_weather_effects(1 / 60)
    render_world(w, surf)
    frames.append(save_frame(surf, "01_pre_jolt.png",
                             "1: storm — Pip shivering"))

    # Frame 2: LIGHTNING strikes. Advance ~6 frames so the full-screen
    # flash has dropped to ~30% (Pip stays readable) but the bolt is
    # still mid-life (0.18 - 6*1/60 = 0.08s) and the coin scatter has
    # had a beat to spread.
    w._fire_storm_jolt()
    for _ in range(6):
        for p in w.particles:
            p.update(1 / 60)
        for t in w.float_texts:
            t.update(1 / 60)
        # Decay flash and bolt in lockstep — same path World.update uses.
        w.weather.flash_remaining = max(0.0, w.weather.flash_remaining - 1 / 60)
        if w.lightning_strike is not None:
            w.lightning_strike["life"] -= 1 / 60
            if w.lightning_strike["life"] <= 0:
                w.lightning_strike = None
    render_world(w, surf)
    frames.append(save_frame(surf, "02_fire.png",
                             "2: LIGHTNING strikes Pip — ZAP!"))

    # Frame 3: ~0.25 s in — radial spread peaks.
    def tick_world(steps):
        """Advance just enough state for the screenshot — particles,
        float texts, flash + bolt decay, and scorch wisp spawns from
        Pip. We don't run World.update() because that would also tick
        physics and clear our staged conditions."""
        for _ in range(steps):
            for p in w.particles:
                p.update(1 / 60)
            for t in w.float_texts:
                t.update(1 / 60)
            w.particles = [p for p in w.particles if p.alive()]
            w.weather.flash_remaining = max(0.0,
                w.weather.flash_remaining - 1 / 60)
            if w.lightning_strike is not None:
                w.lightning_strike["life"] -= 1 / 60
                if w.lightning_strike["life"] <= 0:
                    w.lightning_strike = None
            # Scorch wisps off Pip while the scorch state is live.
            if w._lightning_scorch_t > 0:
                w._lightning_scorch_t = max(0.0,
                    w._lightning_scorch_t - 1 / 60)
                w._scorch_smoke_accum += 1 / 60
                while w._scorch_smoke_accum >= 0.025:
                    w._scorch_smoke_accum -= 0.025
                    w._spawn_scorch_wisp()

    tick_world(12)
    render_world(w, surf)
    frames.append(save_frame(surf, "03_spread.png",
                             "3: spread — coins fly, sparks crackle"))

    # Frame 4: ~0.55 s in — coins arcing; scorch smoke wisps off Pip.
    tick_world(18)
    render_world(w, surf)
    frames.append(save_frame(surf, "04_settle.png",
                             "4: settle — scorch smoke off Pip"))

    # Frame 5: ~1.1 s in — coins faded, lingering smoke.
    tick_world(30)
    w.float_texts = [t for t in w.float_texts if t.alive()]
    render_world(w, surf)
    frames.append(save_frame(surf, "05_after.png",
                             "5: after — score down by 50"))

    # Contact sheet
    make_contact_sheet(frames, "00_contact_sheet.png")
    print("\nDone. Output in:", OUT_DIR)


if __name__ == "__main__":
    main()
