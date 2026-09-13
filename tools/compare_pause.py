"""Before/after for the pause-screen cleanup.

Two modes:
  capture <out.png>            render the CURRENT pause frame deterministically
  compose <before> <after> <o> labelled side-by-side

The pause overlay dims a gameplay frame; we use a fresh deterministic World
as that backdrop so before/after differ only by the overlay UI. Run capture
once before the edits and once after, then compose.
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()


def capture(out):
    import random
    random.seed(0)
    from game.scenes import App, STATE_PAUSE
    from game.world import World
    app = App()
    app.world = World()
    if hasattr(app, "_splash_covering"):
        app._splash_covering = False
    app.state = STATE_PAUSE
    app.world.score = 47
    app.hud.title_t = 0.6  # fixed phase so any animation lands identically
    app._render()
    pygame.image.save(app.screen, out)
    print("captured", out)


def compose(before_p, after_p, out):
    from game.config import W, H
    before = pygame.image.load(before_p)
    after = pygame.image.load(after_p)
    MARGIN, GAP, HEADER = 24, 28, 56
    canvas = pygame.Surface((MARGIN * 2 + W * 2 + GAP, HEADER + H + MARGIN))
    canvas.fill((18, 16, 30))
    title_f = pygame.font.Font(None, 38)
    sub_f = pygame.font.Font(None, 24)

    def header(label, sublabel, cx):
        t = title_f.render(label, True, (245, 235, 210))
        canvas.blit(t, t.get_rect(center=(cx, 22)))
        s = sub_f.render(sublabel, True, (170, 160, 185))
        canvas.blit(s, s.get_rect(center=(cx, 44)))

    lx, rx = MARGIN, MARGIN + W + GAP
    canvas.blit(before, (lx, HEADER))
    canvas.blit(after, (rx, HEADER))
    pygame.draw.rect(canvas, (90, 80, 110), (lx, HEADER, W, H), 1)
    pygame.draw.rect(canvas, (90, 80, 110), (rx, HEADER, W, H), 1)
    header("BEFORE", "dedicated pause score panel", lx + W // 2)
    header("AFTER", "in-game score kept in background (dimmed)", rx + W // 2)
    pygame.image.save(canvas, out)
    print("composed", out)


if __name__ == "__main__":
    if sys.argv[1] == "capture":
        capture(sys.argv[2])
    elif sys.argv[1] == "compose":
        compose(sys.argv[2], sys.argv[3], sys.argv[4])
