import math
import random
import pyxel
from .config import (GRAVITY, FLAP_V, MAX_FALL, BIRD_X, BIRD_R,
                     GROUND_Y, PIPE_W, GAP_START, GAP_MIN,
                     COIN_R, MUSHROOM_R)
from .palette import INK, CREAM, SKY, DKRED, ORNG, GOLD, RED, WHITE
from .sprites import (draw_parrot_tilt, draw_trail, draw_pipe,
                      draw_coin, draw_mushroom)


class Bird:
    TRAIL_LEN = 10

    def __init__(self):
        self.reset()

    def reset(self):
        self.x   = float(BIRD_X)
        self.y   = 120.0
        self.vy  = 0.0
        self.alive = True
        self.t   = 0.0
        self.trail: list[tuple[float, float]] = []
        self._flap_t = 0.0   # time since last flap (drives wing cycle)

    def flap(self):
        if not self.alive:
            return
        self.vy = FLAP_V
        self._flap_t = 0.0   # restart wing cycle from top

    def update(self, dt):
        self.vy = min(self.vy + GRAVITY * dt, MAX_FALL)
        self.y += self.vy * dt
        self.t += dt
        self._flap_t += dt
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.TRAIL_LEN:
            self.trail.pop(0)

    @property
    def frame(self):
        # Wing sweeps down over ~0.35 s then resets
        cycle = 0.35
        phase = (self._flap_t % cycle) / cycle       # 0→1
        if self.vy > 180:
            return 3                                  # diving: wings down
        return int(phase * 4) % 4

    def hits_rect(self, rx, ry, rw, rh):
        """Circle-vs-AABB test."""
        cx = max(rx, min(self.x, rx + rw))
        cy = max(ry, min(self.y, ry + rh))
        dx, dy = self.x - cx, self.y - cy
        return dx*dx + dy*dy <= BIRD_R * BIRD_R

    def draw(self):
        draw_trail(self.trail)
        draw_parrot_tilt(self.x, self.y, self.frame, self.vy)


# ─────────────────────────────────────────────────────────────────────────────

class Pipe:
    def __init__(self, x, gap_y, gap_h):
        self.x = float(x)
        self.gap_y = gap_y
        self.gap_h = gap_h
        self.passed = False

    def update(self, dt, speed):
        self.x -= speed * dt

    def draw(self):
        draw_pipe(int(self.x), self.gap_y, self.gap_h, GROUND_Y)

    @property
    def top_rect(self):
        return (self.x, 0, PIPE_W, self.gap_y)

    @property
    def bot_rect(self):
        by = self.gap_y + self.gap_h
        return (self.x, by, PIPE_W, max(0, GROUND_Y - by))


# ─────────────────────────────────────────────────────────────────────────────

class Coin:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.alive = True
        self.t = random.random() * 10

    def update(self, dt, speed):
        self.x -= speed * dt
        self.t += dt

    def draw(self):
        draw_coin(self.x, self.y, self.t)

    def hits(self, bird):
        dx = self.x - bird.x
        dy = (self.y + math.sin(self.t * 4.5) * 1.5) - bird.y
        r  = COIN_R + BIRD_R
        return dx*dx + dy*dy <= r*r


# ─────────────────────────────────────────────────────────────────────────────

class Mushroom:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.alive = True
        self.t = 0.0

    def update(self, dt, speed):
        self.x -= speed * dt
        self.t += dt

    def draw(self):
        draw_mushroom(self.x, self.y, self.t)

    def hits(self, bird):
        dx = self.x - bird.x
        dy = self.y - bird.y
        r  = MUSHROOM_R + BIRD_R
        return dx*dx + dy*dy <= r*r


# ─────────────────────────────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, vx, vy, life, col, size=1, grav=0.0):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.life = self.max_life = float(life)
        self.col  = col
        self.size = size
        self.grav = grav
        self.alive = True

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.vy += self.grav * dt
        self.x  += self.vx * dt
        self.y  += self.vy * dt

    def draw(self):
        if self.size <= 1:
            _px = pyxel.pset
            _px(int(self.x), int(self.y), self.col)
        else:
            s = self.size
            pyxel.rect(int(self.x) - s//2, int(self.y) - s//2, s, s, self.col)


class FloatText:
    def __init__(self, x, y, text, col):
        self.x, self.y = float(x), float(y)
        self.text = text
        self.col  = col
        self.life = 0.75
        self.alive = True

    def update(self, dt):
        self.life -= dt
        self.y    -= 25 * dt
        if self.life <= 0:
            self.alive = False
