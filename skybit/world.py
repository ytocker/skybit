import math
import random
import pyxel
from .config import (GROUND_Y, BIRD_X, PIPE_W, PIPE_SPACING,
                     GAP_START, GAP_MIN, SCROLL_BASE, SCROLL_MAX,
                     MUSHROOM_CHANCE, MUSHROOM_COOLDOWN, TRIPLE_DURATION,
                     COMBO_WINDOW)
from .entities import Bird, Pipe, Coin, Mushroom, Particle, FloatText
from .palette import DKRED, ORNG, GOLD, CREAM, SKY, RED, WHITE, WGRN


def _lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


class World:
    def __init__(self):
        self.bird = Bird()
        self._reset_state()
        self._mountain_scroll = 0.0
        self._ground_scroll   = 0.0
        self._clouds = [
            {'x': float(random.randint(0, 160)), 'y': float(random.randint(10, 100)),
             'spd': 0.12 + random.random() * 0.2}
            for _ in range(5)
        ]

    def _reset_state(self):
        self.pipes:      list[Pipe]      = []
        self.coins:      list[Coin]      = []
        self.mushrooms:  list[Mushroom]  = []
        self.particles:  list[Particle]  = []
        self.floats:     list[FloatText] = []
        self.score       = 0
        self.coin_count  = 0
        self.combo       = 0
        self.combo_t     = 0.0
        self.triple_t    = 0.0
        self.mush_cd     = 0.0
        self._spawn_x    = pyxel.width + 40.0
        self.elapsed     = 0.0
        self.started     = False
        self.game_over   = False
        # screen-shake
        self._shake      = 0.0
        self._shake_mag  = 0
        # flash
        self._flash_t    = 0.0
        self._flash_col  = WHITE

    def full_reset(self):
        self.bird.reset()
        self._reset_state()

    # ── helpers ───────────────────────────────────────────────────────────

    def _scroll_speed(self):
        t = min(1.0, self.score / 40.0)
        return _lerp(SCROLL_BASE, SCROLL_MAX, t)

    def _pipe_gap(self):
        t = min(1.0, self.score / 35.0)
        return round(_lerp(GAP_START, GAP_MIN, t))

    def shake(self, mag, dur):
        if mag > self._shake_mag:
            self._shake_mag = mag
            self._shake     = dur

    def flash(self, col, dur=0.08):
        self._flash_col = col
        self._flash_t   = dur

    # ── spawn ─────────────────────────────────────────────────────────────

    def _spawn_pipe(self):
        gap   = self._pipe_gap()
        min_t = 22
        max_t = GROUND_Y - gap - 22
        gap_y = random.randint(min_t, max_t)
        pipe  = Pipe(self._spawn_x, gap_y, gap)
        self.pipes.append(pipe)
        self._spawn_coins(pipe)
        if self.mush_cd <= 0 and random.random() < MUSHROOM_CHANCE:
            my = gap_y + gap // 2 + random.randint(-6, 6)
            self.mushrooms.append(Mushroom(self._spawn_x + PIPE_W // 2, my))
            self.mush_cd = MUSHROOM_COOLDOWN
        self._spawn_x += PIPE_SPACING

    def _spawn_coins(self, pipe):
        cx   = pipe.x + PIPE_W // 2
        cy   = pipe.gap_y + pipe.gap_h // 2
        kind = random.choice(['arc', 'line', 'cluster'])
        if kind == 'line':
            n = random.randint(4, 6)
            for i in range(n):
                self.coins.append(Coin(cx - (n-1)*5 + i*10, cy))
        elif kind == 'arc':
            n = 5
            for i in range(n):
                tl = i / (n - 1)
                self.coins.append(Coin(cx - 18 + tl*36,
                                       cy - math.sin(tl * math.pi) * 18))
        else:
            for dx, dy in [(0,0),(-7,-4),(7,-4),(-7,4),(7,4)]:
                self.coins.append(Coin(cx + dx, cy + dy))

    # ── update ────────────────────────────────────────────────────────────

    def update(self, dt):
        self.elapsed += dt
        speed = self._scroll_speed()

        if self.started and not self.game_over:
            if not self.pipes or self.pipes[-1].x < self._spawn_x - PIPE_SPACING:
                self._spawn_pipe()

            for p in self.pipes:    p.update(dt, speed)
            for c in self.coins:    c.update(dt, speed)
            for m in self.mushrooms: m.update(dt, speed)

            self._mountain_scroll += speed * dt
            self._ground_scroll   += speed * dt
            self.mush_cd = max(0.0, self.mush_cd - dt)
            if self.triple_t > 0:
                self.triple_t = max(0.0, self.triple_t - dt)
            if self.combo_t > 0:
                self.combo_t -= dt
                if self.combo_t <= 0:
                    self.combo = 0
            self._spawn_x -= speed * dt

        self.bird.update(dt)

        for p in self.particles:  p.update(dt)
        for f in self.floats:     f.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        self.floats    = [f for f in self.floats    if f.alive]

        # Ground/ceiling
        if self.bird.y + 7 >= GROUND_Y:
            self.bird.y = float(GROUND_Y - 7)
            if self.started and not self.game_over:
                self._kill()
            self.bird.vy = 0
        if self.bird.y < 6:
            self.bird.y = 6.0
            if self.bird.vy < 0:
                self.bird.vy = 0

        if self.started and not self.game_over:
            self._collisions()

        # Clouds
        for cl in self._clouds:
            cl['x'] -= speed * cl['spd'] * dt
            if cl['x'] < -20:
                cl['x'] = pyxel.width + random.randint(0, 30)
                cl['y'] = float(random.randint(10, 100))

        # Prune off-screen
        self.pipes     = [p for p in self.pipes     if p.x + PIPE_W > -4]
        self.coins     = [c for c in self.coins     if c.alive and c.x > -12]
        self.mushrooms = [m for m in self.mushrooms if m.alive and m.x > -12]

        # Shake
        if self._shake > 0:
            self._shake -= dt
            if self._shake <= 0:
                self._shake_mag = 0
        if self._flash_t > 0:
            self._flash_t -= dt

    # ── collisions ────────────────────────────────────────────────────────

    def _collisions(self):
        b = self.bird
        for p in self.pipes:
            if not p.passed and p.x + PIPE_W < b.x:
                p.passed = True
                self.score += 1
            r = p.top_rect
            if b.hits_rect(*r): self._kill(); return
            r = p.bot_rect
            if b.hits_rect(*r): self._kill(); return

        for c in self.coins:
            if c.alive and c.hits(b):
                c.alive = False
                self._collect_coin(c)

        for m in self.mushrooms:
            if m.alive and m.hits(b):
                m.alive = False
                self._collect_mushroom(m)

    def _collect_coin(self, c):
        mult  = 3 if self.triple_t > 0 else 1
        gain  = mult
        self.score      += gain
        self.coin_count += 1
        self.combo      += 1
        self.combo_t     = COMBO_WINDOW
        # Particles
        for _ in range(7):
            ang = random.random() * 2 * math.pi
            sp  = 25 + random.random() * 45
            col = GOLD if random.random() > 0.4 else CREAM
            self.particles.append(
                Particle(c.x, c.y, math.cos(ang)*sp, math.sin(ang)*sp,
                         0.5, col, 1, 60))
        self.floats.append(
            FloatText(c.x, c.y - 6,
                      f'+{gain}', ORNG if mult > 1 else GOLD))
        self.flash(CREAM, 0.045)

    def _collect_mushroom(self, m):
        self.triple_t = TRIPLE_DURATION
        self.shake(2, 0.14)
        self.flash(ORNG, 0.14)
        for i in range(22):
            ang = i / 22 * 2 * math.pi
            sp  = 35 + random.random() * 45
            col = WHITE if i%3==0 else (ORNG if i%2 else CREAM)
            self.particles.append(
                Particle(m.x, m.y, math.cos(ang)*sp, math.sin(ang)*sp,
                         0.75, col, 1, 25))
        self.floats.append(FloatText(m.x, m.y - 10, '3X POWER!', ORNG))

    def _kill(self):
        if self.game_over:
            return
        self.game_over = True
        self.bird.alive = False
        self.shake(6, 0.35)
        self.flash(DKRED, 0.20)
        for _ in range(18):
            ang = random.random() * 2 * math.pi
            sp  = 40 + random.random() * 70
            col = RED if random.random() > 0.5 else ORNG
            self.particles.append(
                Particle(self.bird.x, self.bird.y,
                         math.cos(ang)*sp, math.sin(ang)*sp,
                         1.0, col, 1, 220))

    def world_idle_tick(self, dt):
        """Lightweight tick used on the menu: scrolls clouds + parallax only."""
        speed = SCROLL_BASE * 0.4
        self._mountain_scroll += speed * dt
        self._ground_scroll   += speed * dt
        for cl in self._clouds:
            cl['x'] -= speed * cl['spd'] * dt
            if cl['x'] < -20:
                cl['x'] = pyxel.width + random.randint(0, 30)
                cl['y'] = float(random.randint(10, 100))

    # ── render ────────────────────────────────────────────────────────────

    def draw(self):
        from .sprites import draw_sky, draw_mountains, draw_ground, draw_cloud

        ox = random.randint(-self._shake_mag, self._shake_mag) if self._shake_mag else 0
        oy = random.randint(-self._shake_mag, self._shake_mag) if self._shake_mag else 0

        draw_sky(GROUND_Y)
        for cl in self._clouds:
            draw_cloud(cl['x'] + ox, cl['y'] + oy)
        draw_mountains(self._mountain_scroll, GROUND_Y)
        draw_ground(self._ground_scroll, GROUND_Y)

        for p in self.pipes:     p.draw()
        for c in self.coins:     c.draw()
        for m in self.mushrooms: m.draw()
        for p in self.particles: p.draw()

        self.bird.draw()

        # Mushroom-active aura around bird
        if self.triple_t > 0:
            t = self.elapsed
            r = 12 + int(math.sin(t * 10) * 2)
            pyxel.circb(int(self.bird.x), int(self.bird.y), r,     ORNG)
            pyxel.circb(int(self.bird.x), int(self.bird.y), r + 2, GOLD)

        # Flash overlay
        if self._flash_t > 0 and self._flash_t > 0:
            pyxel.dither(min(0.65, self._flash_t * 8))
            pyxel.rect(0, 0, pyxel.width, pyxel.height, self._flash_col)
            pyxel.dither(1.0)
