"""
Headless autoplayer that drives the live App through several rounds with a
simple "aim above the gap center" heuristic, then captures frames at notable
moments for a design-critique pass.

Saves PNGs into docs/critique/ — run-and-review tool, not a test.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from game.config import H, GRAVITY, PIPE_W, FLAP_V
from game.scenes import App, STATE_MENU, STATE_PLAY, STATE_NAMEENTRY, STATE_GAMEOVER

OUT = os.path.join(ROOT, "docs", "critique")
os.makedirs(OUT, exist_ok=True)


def ai_should_flap(world):
    """Flap whenever the bird is at or below the gap centre. Tiny ceiling
    safety net prevents the AI from over-flapping into the top of the screen
    on the opening frames."""
    bird = world.bird
    if not bird.alive:
        return False
    if bird.y < 40:           # ceiling safety
        return False
    ahead = [p for p in world.pipes if p.x + PIPE_W > bird.x - 6]
    target_y = (min(ahead, key=lambda p: p.x).gap_y if ahead else H * 0.5)
    return bird.y > target_y and bird.vy > -150


def label_frame(name):
    return os.path.join(OUT, f"{name}.png")


def run():
    pygame.init()
    pygame.display.set_mode((360, 640))
    app = App()
    app._cooldown_t = 0.0
    if app.state == STATE_MENU:
        app._start_play()

    captured: dict[str, bool] = {}
    log: list[str] = []

    def snap(name, force=False):
        if name in captured and not force:
            return
        captured[name] = True
        pygame.image.save(app.screen, label_frame(name))
        log.append(f"snap {name}: state={app.state} score={app.world.score} "
                   f"coins={app.world.coin_count} 3x={app.world.triple_timer:.1f}")

    deaths = 0
    death_scores: list[int] = []
    last_coin_count = 0
    saw_first_coin = False
    saw_first_mushroom = False

    for frame in range(60 * 90):     # up to 90s of simulated play
        dt = 1 / 60.0

        if app.state == STATE_PLAY:
            if ai_should_flap(app.world):
                app.world.flap()
            # Capture a coin grab the moment count ticks up.
            if app.world.coin_count > last_coin_count and not saw_first_coin:
                saw_first_coin = True
                snap("01_coin_grab")
            last_coin_count = app.world.coin_count
            # Capture mushroom 3X activation.
            if app.world.triple_timer > 0 and not saw_first_mushroom:
                saw_first_mushroom = True
                snap("02_mushroom_3x")
            # Generic mid-play sample around 8s into the first life.
            if app.world.score >= 5 and app.world.score <= 9:
                snap("03_play_early")
            # High-difficulty sample.
            if app.world.score >= 25:
                snap("04_play_high_diff")
        elif app.state == STATE_NAMEENTRY:
            # Skip the name-entry overlay so the next round can start.
            app.name_entry.submit()
        elif app.state == STATE_GAMEOVER:
            # Snap once during the cooldown so the overlay is fully drawn.
            if app._cooldown_t > 0.05:
                snap("05_game_over")
            if app._cooldown_t <= 0:
                death_scores.append(app.world.score)
                deaths += 1
                app._restart()

        app._update(dt)
        app._render()

    log.append(f"--- ended after {frame+1} frames")
    log.append(f"deaths={deaths} death_scores={death_scores}")
    for line in log:
        print(line)


if __name__ == "__main__":
    run()
