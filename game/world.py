"""
World simulation: physics, spawner, collision, difficulty ramp.
Handles coin/mushroom pickup FX. IMPORTANT: coin pickup must NOT do a
full-screen flash (that was the 'glitch' the user saw) — only localized
sparkle particles around the coin.
"""
import math
import random
import pygame

from game.config import (
    W, H, GROUND_Y, PIPE_W, PIPE_SPACING,
    GAP_START, GAP_MIN, SCROLL_BASE, SCROLL_MAX,
    BIRD_X, BIRD_R, COIN_R, MUSHROOM_R,
    MUSHROOM_CHANCE, MUSHROOM_COOLDOWN,
    TRIPLE_DURATION, MAGNET_DURATION, MAGNET_RADIUS,
    SLOWMO_DURATION, SLOWMO_SCALE,
    POWERUP_WEIGHTS, COMBO_WINDOW,
    COIN_RUSH_INTERVAL, COIN_RUSH_GAP_BOOST, COIN_RUSH_COINS,
)
from game.entities import (
    Bird, Pipe, Coin, PowerUp, Particle, FloatText,
)
from game.draw import (
    COIN_GOLD, COIN_LIGHT,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    UI_GOLD, UI_ORANGE, UI_CREAM, WHITE, BIRD_RED,
)
from game import biome
from game import audio
from game.weather import Weather


def _lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


class World:
    def __init__(self):
        self.bird = Bird()
        self.pipes: list[Pipe] = []
        self.coins: list[Coin] = []
        self.powerups: list[PowerUp] = []
        self.particles: list[Particle] = []
        self.float_texts: list[FloatText] = []

        self.scroll_speed = SCROLL_BASE
        self.bg_scroll = 0.0

        self.score = 0
        self.coin_count = 0
        self.combo = 1
        self.combo_timer = 0.0

        self.triple_timer = 0.0
        self.magnet_timer = 0.0
        self.slowmo_timer = 0.0
        self.shield_armed = False
        self.mushroom_cooldown = 0.0

        # Coin-rush counter: increments each spawn; every Nth pipe is a rush.
        self.pipes_spawned = 0

        # Per-run stats surfaced on the post-game summary.
        self.max_combo = 1
        self.pillars_passed = 0
        self.time_alive = 0.0
        self.near_misses = 0
        self.powerups_picked = {"triple": 0, "shield": 0, "magnet": 0, "slowmo": 0}
        # Transient flag so near-miss detection fires once per pillar.
        self._near_miss_flags: dict[int, bool] = {}

        self.hit_flash = 0.0    # death-only red tint, NOT coin
        self.shake_mag = 0.0
        self.shake_t = 0.0

        # Real elapsed gameplay seconds — drives the day/night biome cycle.
        self.biome_time = 0.0

        self.weather = Weather()

        # "Get ready" freeze at the start of a round: physics paused until
        # the player flaps or the timer expires. Gives new players a moment
        # to orient before the first pillar scrolls in (REVIEW.md finding).
        self.ready_t = 1.0

        self.game_over = False

        self._seed_first_pipes()

    # Back-compat: older snapshot/playtest scripts poke `world.mushrooms`.
    @property
    def mushrooms(self):
        return self.powerups

    @mushrooms.setter
    def mushrooms(self, value):
        self.powerups = value

    # ── difficulty ───────────────────────────────────────────────────────────

    def _diff_t(self):
        # Constant difficulty — coins do not speed up the scroll or shrink
        # the pipe gap. The game stays at SCROLL_BASE / GAP_START always.
        return 0.0

    # ── biome ────────────────────────────────────────────────────────────────

    @property
    def biome_phase(self):
        return biome.phase_for_time(self.biome_time)

    @property
    def biome_palette(self):
        return biome.palette_for_phase(self.biome_phase)

    def _current_gap(self):
        return int(_lerp(GAP_START, GAP_MIN, self._diff_t()))

    def _current_scroll(self):
        return _lerp(SCROLL_BASE, SCROLL_MAX, self._diff_t())

    # ── spawning ─────────────────────────────────────────────────────────────

    def _seed_first_pipes(self):
        x = W + 60
        for _ in range(3):
            self._spawn_pipe(x)
            x += PIPE_SPACING

    def _spawn_pipe(self, x):
        gap_h = self._current_gap()
        # Every Nth pipe is a "coin rush": wider gap + dense coin arc, no
        # power-up. The visual announcement fires below.
        self.pipes_spawned += 1
        is_rush = (self.pipes_spawned % COIN_RUSH_INTERVAL == 0)
        if is_rush:
            gap_h = int(gap_h * COIN_RUSH_GAP_BOOST)
        margin = 70
        gy = random.randint(margin + gap_h // 2, GROUND_Y - margin - gap_h // 2)
        p = Pipe(x, gy, gap_h)
        p.is_rush = is_rush
        self.pipes.append(p)
        if is_rush:
            self._spawn_rush_coins(p)
            self._announce_rush(p)
        else:
            self._spawn_coins_in_gap(p)
            self._maybe_spawn_powerup(p)

    def _spawn_coins_in_gap(self, pipe: Pipe):
        pattern = random.choice(("arc", "line", "cluster"))
        cx = pipe.x + PIPE_W + PIPE_SPACING * 0.5
        gy = pipe.gap_y
        if pattern == "arc":
            n = 5
            radius = min(70, pipe.gap_h * 0.35)
            for i in range(n):
                t = i / (n - 1)
                ang = -math.pi * 0.35 + math.pi * 0.7 * t
                x = cx + math.sin(ang) * 50
                y = gy + math.cos(ang) * radius - radius * 0.2
                self.coins.append(Coin(x, y))
        elif pattern == "line":
            n = 4
            for i in range(n):
                x = cx - 40 + i * 22
                self.coins.append(Coin(x, gy))
        else:  # cluster
            for dx, dy in ((0, 0), (-20, -14), (20, -14), (-20, 14), (20, 14)):
                self.coins.append(Coin(cx + dx, gy + dy))

    def _spawn_rush_coins(self, pipe: Pipe):
        """Dense sinusoidal arc of ~COIN_RUSH_COINS coins across the gap."""
        cx = pipe.x + PIPE_W + PIPE_SPACING * 0.45
        gy = pipe.gap_y
        span = PIPE_SPACING * 0.85
        amp = min(pipe.gap_h * 0.35, 70)
        n = COIN_RUSH_COINS
        # Random sine phase + wavelength so consecutive rushes don't all feel
        # the same.
        phase = random.uniform(0, math.tau)
        waves = random.uniform(1.0, 1.6)
        for i in range(n):
            t = i / (n - 1)
            x = cx - span / 2 + span * t
            y = gy + math.sin(phase + waves * math.pi * 2 * t) * amp
            self.coins.append(Coin(x, y))

    def _announce_rush(self, pipe: Pipe):
        """'COIN RUSH!' float text + a burst of gold sparkles when a rush
        pipe enters from the right edge."""
        x = pipe.x - 20
        y = pipe.gap_y
        self.float_texts.append(FloatText(
            "COIN RUSH!", x, y - 40, UI_GOLD, size=26, life=1.6, vy=-28,
        ))
        for _ in range(22):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(60, 220)
            col = random.choice((PARTICLE_GOLD, COIN_LIGHT, UI_ORANGE))
            self.particles.append(Particle(
                x, y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.0),
                random.randint(2, 4),
                col, gravity=120,
            ))

    def _maybe_spawn_powerup(self, pipe: Pipe):
        if self.mushroom_cooldown > 0:
            return
        if random.random() >= MUSHROOM_CHANCE:
            return
        kinds = [k for k, _ in POWERUP_WEIGHTS]
        weights = [w for _, w in POWERUP_WEIGHTS]
        kind = random.choices(kinds, weights=weights, k=1)[0]
        x = pipe.x + PIPE_W + PIPE_SPACING * 0.5 + random.uniform(-20, 20)
        y = pipe.gap_y + random.uniform(-10, 10)
        self.powerups.append(PowerUp(x, y, kind=kind))
        self.mushroom_cooldown = MUSHROOM_COOLDOWN

    # ── public control ──────────────────────────────────────────────────────

    def flap(self):
        if not self.game_over:
            # A tap during the "get ready" freeze both lifts the bird and
            # kicks the world into motion immediately.
            if self.ready_t > 0:
                self.ready_t = 0.0
            self.bird.flap()
            audio.play_flap()

    # ── update ──────────────────────────────────────────────────────────────

    def update(self, dt):
        self.biome_time += dt
        # Slowmo scales the *world* (scroll, entity velocity, entity spin,
        # pickup physics) — not the bird's input physics. Lets players
        # still flap responsively while everything else crawls.
        world_scale = SLOWMO_SCALE if self.slowmo_timer > 0 else 1.0
        sdt = dt * world_scale
        # Weather tracks biome phase, scales with sdt so slowmo softens rain too.
        self.weather.update(sdt, self.biome_phase)

        # While the "get ready" prompt is up, hold everything still except
        # a tiny idle animation on the bird.
        if self.ready_t > 0 and not self.game_over:
            self.ready_t = max(0.0, self.ready_t - dt)
            # Gentle bob without physics integration.
            self.bird.vy = 0
            self.bird.y = H * 0.42 + math.sin(self.biome_time * 4.0) * 6
            self.bird.frame_t += dt * 6.0
            # Keep particles / float-texts ticking so nothing freezes visually.
            for p in self.particles:
                p.update(dt)
            self.particles = [p for p in self.particles if p.alive()]
            for t in self.float_texts:
                t.update(dt)
            self.float_texts = [t for t in self.float_texts if t.alive()]
            return

        if not self.game_over:
            self.bird.update(dt)  # bird physics at real time

            speed = self._current_scroll() if not self.game_over else 0
            self.bg_scroll += speed * sdt
            for p in self.pipes:
                p.x -= speed * sdt
            for c in self.coins:
                c.x -= speed * sdt
                c.update(sdt)
            for m in self.powerups:
                m.x -= speed * sdt
                m.update(sdt)

            # Magnet pull — tug uncollected coins toward the bird.
            if self.magnet_timer > 0:
                self._apply_magnet(dt)

            # cull off-screen
            self.pipes = [p for p in self.pipes if not p.off_screen()]
            self.coins = [c for c in self.coins if c.x + 20 > 0 and not c.collected]
            self.powerups = [m for m in self.powerups if m.x + 20 > 0 and not m.collected]

            # spawn more pipes
            if self.pipes and self.pipes[-1].x < W - PIPE_SPACING:
                self._spawn_pipe(self.pipes[-1].x + PIPE_SPACING)

            # scoring: pass a pipe
            bx = self.bird.x
            by = self.bird.y
            for p in self.pipes:
                if not p.scored and p.x + PIPE_W < bx:
                    p.scored = True
                    self.score += 1
                    self.pillars_passed += 1

            # Near-miss detection: once per pipe, flag if the bird was within
            # a narrow band of either edge without hitting. Fires as the pipe
            # passes behind the bird so it doesn't double-count mid-flight.
            for p in self.pipes:
                pid = id(p)
                if self._near_miss_flags.get(pid):
                    continue
                # Only check pipes currently overlapping the bird's x-range
                if p.x < bx + BIRD_R and p.x + PIPE_W > bx - BIRD_R:
                    gap_top = p.gap_y - p.gap_h / 2
                    gap_bot = p.gap_y + p.gap_h / 2
                    # Distance from bird to nearest pipe edge vertically
                    d_top = by - gap_top  # positive if below the top edge
                    d_bot = gap_bot - by  # positive if above the bot edge
                    margin = 10
                    if 0 < d_top < margin or 0 < d_bot < margin:
                        self.near_misses += 1
                        self._near_miss_flags[pid] = True

            # Time alive
            self.time_alive += dt

            # collisions
            self._check_collisions()

            # pickups
            self._check_pickups()

            # timers (real time, not scaled — the buffs shouldn't self-extend).
            if self.triple_timer > 0:
                self.triple_timer = max(0.0, self.triple_timer - dt)
            if self.magnet_timer > 0:
                self.magnet_timer = max(0.0, self.magnet_timer - dt)
            if self.slowmo_timer > 0:
                self.slowmo_timer = max(0.0, self.slowmo_timer - dt)
            if self.mushroom_cooldown > 0:
                self.mushroom_cooldown -= dt
            if self.combo_timer > 0:
                self.combo_timer -= dt
                if self.combo_timer <= 0:
                    self.combo = 1
            if self.hit_flash > 0:
                self.hit_flash = max(0.0, self.hit_flash - dt)
        else:
            # freeze world but let particles + float texts drift
            pass

        # shake decay
        if self.shake_t > 0:
            self.shake_t -= dt
            if self.shake_t <= 0:
                self.shake_mag = 0.0

        # particles and float texts
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]
        for t in self.float_texts:
            t.update(dt)
        self.float_texts = [t for t in self.float_texts if t.alive()]

    def world_idle_tick(self, dt):
        """Run the background without handling bird death/pipe spawning
        logic — used by the Menu scene to keep visuals alive."""
        self.biome_time += dt
        self.weather.update(dt, self.biome_phase)
        self.bg_scroll += SCROLL_BASE * 0.5 * dt
        for p in self.pipes:
            p.x -= SCROLL_BASE * 0.25 * dt
        for c in self.coins:
            c.x -= SCROLL_BASE * 0.25 * dt
            c.update(dt)
        for m in self.powerups:
            m.x -= SCROLL_BASE * 0.25 * dt
            m.update(dt)
        self.pipes = [p for p in self.pipes if not p.off_screen()]
        self.coins = [c for c in self.coins if c.x + 20 > 0]
        self.powerups = [m for m in self.powerups if m.x + 20 > 0]
        if self.pipes and self.pipes[-1].x < W - PIPE_SPACING:
            self._spawn_pipe(self.pipes[-1].x + PIPE_SPACING)

        # animate bird gently (bobbing)
        self.bird.frame_t += dt * 8.0
        self.bird.y = H * 0.42 + math.sin(self.bg_scroll * 0.05) * 12
        self.bird.vy = -math.cos(self.bg_scroll * 0.05) * 40

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive()]

    # ── collisions ───────────────────────────────────────────────────────────

    def _check_collisions(self):
        bx, by = self.bird.x, self.bird.y
        if by + BIRD_R > GROUND_Y or by - BIRD_R < 0:
            self._die()
            return
        for p in self.pipes:
            if p.collides_circle(bx, by, BIRD_R - 2):
                if self.shield_armed:
                    self._break_shield(p)
                    return
                self._die()
                return

    def _break_shield(self, pipe):
        """Consume the shield: spawn a blue shimmer + a safety nudge."""
        self.shield_armed = False
        self.shake_mag = max(self.shake_mag, 4.0)
        self.shake_t = max(self.shake_t, 0.25)
        # Nudge the bird upward out of the pillar so it isn't still overlapping.
        self.bird.vy = -240
        audio.play_shield_break()
        bx, by = self.bird.x, self.bird.y
        for _ in range(24):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(140, 320)
            col = random.choice(((120, 200, 255), (80, 160, 255), WHITE))
            self.particles.append(Particle(
                bx, by,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.4, 0.9),
                random.randint(2, 4),
                col, gravity=80,
            ))
        self.float_texts.append(FloatText(
            "SHIELD!", bx, by - 24, (120, 200, 255),
            size=22, life=1.1, vy=-40,
        ))

    def _die(self):
        if self.game_over:
            return
        self.game_over = True
        self.bird.alive = False
        self.hit_flash = 0.35
        self.shake_mag = 8
        self.shake_t = 0.45
        self.combo = 1
        audio.play_death()
        for _ in range(26):
            self.particles.append(Particle(
                self.bird.x, self.bird.y,
                random.uniform(-260, 260), random.uniform(-360, -40),
                random.uniform(0.5, 1.2), random.randint(3, 6),
                random.choice((PARTICLE_CRIM, PARTICLE_ORNG, PARTICLE_WHT)),
                gravity=900,
            ))

    # ── pickups ──────────────────────────────────────────────────────────────

    def _check_pickups(self):
        bx, by = self.bird.x, self.bird.y
        br = BIRD_R + 4
        for c in self.coins:
            if c.collected:
                continue
            dx = c.x - bx
            dy = c.y - by
            if dx * dx + dy * dy < (br + COIN_R) ** 2:
                c.collected = True
                self._on_coin(c)
        for m in self.powerups:
            if m.collected:
                continue
            dx = m.x - bx
            dy = m.y - by
            if dx * dx + dy * dy < (br + MUSHROOM_R) ** 2:
                m.collected = True
                self._on_powerup(m)

    def _apply_magnet(self, dt):
        """Tug uncollected coins within MAGNET_RADIUS toward the bird."""
        bx, by = self.bird.x, self.bird.y
        r2 = MAGNET_RADIUS * MAGNET_RADIUS
        # Strength falls off linearly with distance, capped so close coins
        # don't teleport.
        for c in self.coins:
            if c.collected:
                continue
            dx = bx - c.x
            dy = by - c.y
            d2 = dx * dx + dy * dy
            if d2 > r2 or d2 < 1.0:
                continue
            d = math.sqrt(d2)
            pull = 520 * (1.0 - d / MAGNET_RADIUS)
            c.x += (dx / d) * pull * dt
            c.y += (dy / d) * pull * dt

    def _on_coin(self, coin: Coin):
        value = 3 if self.triple_timer > 0 else 1
        self.score += value
        self.coin_count += 1
        # combo
        if self.combo_timer > 0:
            self.combo += 1
        else:
            self.combo = 2
        self.combo_timer = COMBO_WINDOW
        if self.combo > self.max_combo:
            self.max_combo = self.combo

        # *** GLITCH FIX ***
        # NO screen-wide flash. Only localized sparkle particles.
        for _ in range(10):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(80, 220)
            col = random.choice((PARTICLE_GOLD, COIN_LIGHT, PARTICLE_WHT))
            self.particles.append(Particle(
                coin.x, coin.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.4, 0.8),
                random.randint(2, 4),
                col, gravity=300,
            ))
        if value == 3:
            label = "+3"
            color = UI_ORANGE
            size = 30
            text_y_offset = 18
        else:
            label = "+1"
            color = UI_GOLD
            size = 22
            text_y_offset = 8
        self.float_texts.append(
            FloatText(label, coin.x, coin.y - text_y_offset, color,
                      size=size, life=0.9))

        # Pick the richest available audio cue for this pickup.
        if value == 3:
            audio.play_coin_triple()
        elif self.combo >= 3:
            audio.play_coin_combo()
        else:
            audio.play_coin()

        # Combo is communicated by the persistent bouncing HUD badge — no
        # per-pickup FloatText spawn, which would stack mid-air on fast streaks.

    def _on_powerup(self, m: PowerUp):
        self.powerups_picked[m.kind] = self.powerups_picked.get(m.kind, 0) + 1
        if m.kind == "triple":
            self._activate_triple(m)
        elif m.kind == "shield":
            self._activate_shield(m)
        elif m.kind == "magnet":
            self._activate_magnet(m)
        elif m.kind == "slowmo":
            self._activate_slowmo(m)

    def _pickup_burst(self, m, colors, n=30, speed_hi=320, grav=150):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(100, speed_hi)
            col = random.choice(colors)
            self.particles.append(Particle(
                m.x, m.y,
                math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.5, 1.0),
                random.randint(3, 6),
                col, gravity=grav,
            ))

    def _activate_triple(self, m):
        self.triple_timer = TRIPLE_DURATION
        self.shake_mag = max(self.shake_mag, 3.0)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_mushroom()
        self._pickup_burst(m, (UI_ORANGE, UI_GOLD, BIRD_RED, UI_CREAM))
        self.float_texts.append(FloatText(
            "3X POWER!", m.x, m.y - 22, UI_ORANGE, size=26, life=1.4, vy=-30,
        ))

    def _activate_shield(self, m):
        self.shield_armed = True
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_shield()
        self._pickup_burst(m, ((120, 200, 255), (80, 160, 255), WHITE, (180, 225, 255)))
        self.float_texts.append(FloatText(
            "SHIELD UP!", m.x, m.y - 22, (120, 200, 255), size=24, life=1.3, vy=-30,
        ))

    def _activate_magnet(self, m):
        self.magnet_timer = MAGNET_DURATION
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_magnet()
        self._pickup_burst(m, (BIRD_RED, (220, 30, 40), UI_CREAM, WHITE))
        self.float_texts.append(FloatText(
            "MAGNET!", m.x, m.y - 22, BIRD_RED, size=24, life=1.3, vy=-30,
        ))

    def _activate_slowmo(self, m):
        self.slowmo_timer = SLOWMO_DURATION
        self.shake_mag = max(self.shake_mag, 2.5)
        self.shake_t = max(self.shake_t, 0.25)
        audio.play_slowmo()
        self._pickup_burst(m, ((180, 100, 255), (120, 60, 200), WHITE, UI_CREAM))
        self.float_texts.append(FloatText(
            "SLOW-MO!", m.x, m.y - 22, (200, 140, 255), size=24, life=1.3, vy=-30,
        ))

    # ── utility ──────────────────────────────────────────────────────────────

    def shake_offset(self):
        if self.shake_t <= 0 or self.shake_mag <= 0:
            return 0, 0
        amp = self.shake_mag * (self.shake_t / 0.45)
        return (random.uniform(-amp, amp), random.uniform(-amp, amp))
