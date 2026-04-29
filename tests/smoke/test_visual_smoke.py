"""Render every entity / HUD / power-up variant once to a dummy surface.

These tests don't assert pixel content — they only assert that ``draw``
methods don't raise. Their value is coverage: the visual variants
(``dollar_variants``, ``surprise_box_variants``, ``kfc_fries``,
``dollar_parrot_hat``, ``dollar_parrot_ghost``, ``pillar_variants``,
``hud``, ``weather``) are otherwise unreachable from headless tests.
"""
import pygame
import pytest


@pytest.fixture
def surface():
    """SRCALPHA surface usable for any HUD / sprite ``draw`` call.

    Initialises the pygame display + font subsystems — the variant
    modules build font objects lazily and require ``pygame.font.init()``
    to have run."""
    pygame.display.init()
    pygame.font.init()
    surf = pygame.Surface((360, 640), pygame.SRCALPHA)
    yield surf


# ── Bird rendering across active flags ──────────────────────────────────────

@pytest.mark.parametrize("flag",
                         ["normal", "kfc", "ghost", "triple", "grow"])
def test_bird_draws_each_mode(surface, flag):
    from game.entities import Bird
    b = Bird()
    if flag == "kfc":
        b.kfc_active = True
    elif flag == "ghost":
        b.ghost_active = True
    elif flag == "triple":
        b.triple_active = True
    elif flag == "grow":
        b.grow_active = True
    # Drive frame_t through every wing index
    for i in range(8):
        b.frame_t = float(i)
        b.draw(surface)


# ── Pipe variants ───────────────────────────────────────────────────────────

def test_pipe_draws_with_default_palette(surface):
    from game.entities import Pipe
    Pipe(100, 320, 170).draw(surface)


def test_pipe_draws_with_biome_palette(surface):
    from game.entities import Pipe
    from game import biome
    pal = biome.palette_for_phase(0.0)
    Pipe(100, 320, 170).draw(surface, palette=pal)


def test_pipe_draws_many_seeds(surface):
    """Different ``seed`` values pick different visual variants — render
    a handful so all variant branches fire."""
    from game.entities import Pipe
    for seed in range(0, 20_000, 1000):
        p = Pipe(100, 320, 170)
        p.seed = seed
        p.draw(surface)


# ── Coin rendering ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("kfc", [False, True])
def test_coin_draws_each_spin_phase(surface, kfc):
    from game.entities import Coin
    c = Coin(100, 200)
    import math
    for spin in (0.0, math.pi / 8, math.pi / 4, math.pi / 2, math.pi, math.tau):
        c.spin = spin
        c.draw(surface, kfc_active=kfc)


# ── PowerUp every kind ──────────────────────────────────────────────────────

@pytest.mark.parametrize("kind",
                         ["triple", "magnet", "slowmo", "kfc",
                          "ghost", "grow", "surprise"])
def test_powerup_draws_each_kind(surface, kind):
    from game.entities import PowerUp
    p = PowerUp(180, 300, kind=kind)
    p.update(0.1)
    p.draw(surface)


# ── HUD scenes ──────────────────────────────────────────────────────────────

def test_hud_draws_play_overlay(surface, world):
    from game.hud import HUD
    hud = HUD()
    world.score = 5
    world.coin_count = 3
    world.triple_timer = 1.0
    world.magnet_timer = 1.0
    world.slowmo_timer = 1.0
    hud.draw_play(surface, world, best=10, paused=False)


def test_hud_draws_menu(surface):
    from game.hud import HUD
    hud = HUD()
    hud.draw_menu(surface, 1 / 60, best=42)


def test_hud_draws_pause_overlay(surface):
    from game.hud import HUD
    hud = HUD()
    hud.draw_pause_overlay(surface)


def test_hud_draws_gameover(surface, world):
    from game.hud import HUD
    hud = HUD()
    hud.draw_gameover(surface, 1 / 60, score=42, new_best=False)


def test_hud_draws_stats(surface, world):
    from game.hud import HUD
    hud = HUD()
    world.score = 42
    world.coin_count = 12
    world.pillars_passed = 18
    world.near_misses = 3
    world.time_alive = 30.0
    hud.draw_stats(surface, world, dt=1 / 60, elapsed=0.5)


def test_hud_draws_name_entry(surface):
    from game.hud import HUD
    hud = HUD()
    hud.draw_name_entry(surface, 1 / 60, buf="ALICE")


def test_hud_draws_leaderboard(surface):
    from game.hud import HUD
    hud = HUD()
    scores = [{"name": f"P{i}", "score": (10 - i) * 100} for i in range(10)]
    hud.draw_leaderboard(surface, 1 / 60, scores, player_rank=2,
                         loading=False, cooldown=0.0)


def test_hud_draws_leaderboard_loading(surface):
    from game.hud import HUD
    hud = HUD()
    hud.draw_leaderboard(surface, 1 / 60, [], player_rank=-1,
                         loading=True, cooldown=0.0)


def test_hud_draws_leaderboard_empty(surface):
    from game.hud import HUD
    hud = HUD()
    hud.draw_leaderboard(surface, 1 / 60, [], player_rank=-1,
                         loading=False, cooldown=0.0)


# ── Weather ─────────────────────────────────────────────────────────────────

def test_weather_updates_and_draws(surface):
    from game.weather import Weather
    w = Weather()
    # Walk through the day/night cycle so each phase's weather can fire.
    for phase in (0.0, 0.2, 0.5, 0.8):
        for _ in range(20):
            w.update(1 / 30, phase)
        w.draw(surface)


# ── Variant draw functions: everything in registries ────────────────────────

def test_surprise_box_variants_all_render(surface):
    from game import surprise_box_variants as sbv
    for name, fn in sbv.VARIANTS:
        fn(surface, 32, 32, t=0.0)


def test_kfc_fries_variants_all_render(surface):
    from game import kfc_fries
    for name, fn in kfc_fries.VARIANTS:
        fn(surface, 32, 32, t=0.0)


def test_dollar_variants_all_render(surface):
    from game import dollar_variants
    for name, fn in dollar_variants.VARIANTS:
        fn(surface, 180, 200, pulse=0.0)


# ── Parrot frame builders ───────────────────────────────────────────────────

def test_parrot_get_frames(surface):
    from game import parrot
    for i in range(len(parrot.FRAMES)):
        parrot.get_parrot(i, 0.0)
        parrot.get_fried_parrot(i, 0.0)
        parrot.get_ghost_parrot(i, 0.0)
        parrot.get_hat_parrot(i, 0.0)


# ── Scenes render path ──────────────────────────────────────────────────────

def test_scenes_render_each_state(monkeypatch, mute_audio):
    from game import play_log
    async def _noop(*a, **k): return False
    monkeypatch.setattr(play_log, "log_run", _noop)

    from game.scenes import (
        App, STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_STATS,
        STATE_NAMEENTRY, STATE_LEADERBOARD, STATE_GAMEOVER,
    )
    app = App()
    app._cooldown_t = 0.0
    states = [STATE_MENU, STATE_PLAY, STATE_PAUSE, STATE_STATS,
              STATE_NAMEENTRY, STATE_LEADERBOARD, STATE_GAMEOVER]
    for st in states:
        app.state = st
        app._render()
