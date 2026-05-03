// World simulation — physics, spawner, collision, power-up timers.
// Ported from game/world.py with a lighter codebase in v1 (the more
// elaborate proof-bundle and per-event ledger machinery is replaced by
// the much simpler `runId + score` submission model in leaderboard.ts).

import {
  W, GROUND_Y, PIPE_W, PIPE_SPACING, GAP_START, GAP_MIN,
  SCROLL_BASE, SCROLL_MAX, BIRD_X, COIN_R, POWERUP_R,
  POWERUP_CHANCE, POWERUP_COOLDOWN,
  TRIPLE_DURATION, MAGNET_DURATION, MAGNET_RADIUS,
  SLOWMO_DURATION, SLOWMO_SCALE,
  KFC_DURATION, GHOST_DURATION, GROW_DURATION,
  POWERUP_WEIGHTS,
  COIN_RUSH_INTERVAL, COIN_RUSH_GAP_BOOST, COIN_RUSH_COINS,
  type PowerUpKind,
} from "./config.js";
import {
  Bird, Pipe, Coin, PowerUp, Particle, FloatText, CloudPuff, PARTICLE_COLORS,
} from "./entities.js";
import { Weather } from "./weather.js";
import * as audio from "./audio.js";
import { paletteForTime, type Palette } from "./biome.js";

function randInt(lo: number, hi: number): number {
  return lo + Math.floor(Math.random() * (hi - lo + 1));
}

function pickWeighted(weights: ReadonlyArray<readonly [PowerUpKind, number]>): PowerUpKind {
  const total = weights.reduce((s, [, w]) => s + w, 0);
  let r = Math.random() * total;
  for (const [k, w] of weights) {
    r -= w;
    if (r <= 0) return k;
  }
  return weights[0][0];
}

export class World {
  static readonly SPAWN_GRACE = 1.5;

  bird = new Bird();
  pipes: Pipe[] = [];
  coins: Coin[] = [];
  powerups: PowerUp[] = [];
  particles: Particle[] = [];
  cloudPuffs: CloudPuff[] = [];
  floatTexts: FloatText[] = [];

  scrollSpeed = SCROLL_BASE;
  bgScroll = 0;

  score = 0;
  coinCount = 0;

  tripleTimer = 0;
  magnetTimer = 0;
  slowmoTimer = 0;
  kfcTimer = 0;
  ghostTimer = 0;
  growTimer = 0;
  reverseTimer = 0;
  powerupCooldown = 0;

  pipesSpawned = 0;
  pillarsPassed = 0;
  timeAlive = 0;
  nearMisses = 0;
  powerupsPicked: Record<string, number> = {
    triple: 0, magnet: 0, slowmo: 0, kfc: 0, ghost: 0, grow: 0, reverse: 0, surprise: 0,
  };

  hitFlash = 0;
  shakeMag = 0;
  shakeT = 0;

  biomeTime = 0;
  private idleT = 0;

  readyT = 1.0;
  gameOver = false;
  hitPipe: Pipe | null = null;

  weather = new Weather();

  // ── Mutators ──────────────────────────────────────────────────────────────

  flap(): void {
    if (this.gameOver) return;
    if (this.readyT > 0) this.readyT = 0;
    if (this.reverseTimer > 0) {
      this.bird.vy = -this.bird.vy;
      this.bird.flap();
      this.bird.vy = -this.bird.vy;  // flap then re-invert
    } else {
      this.bird.flap();
    }
    audio.playFlap();
  }

  worldIdleTick(dt: number): void {
    this.idleT += dt;
    this.bird.frameT += dt * 6;
    // Idle bob.
    this.bird.y = 320 + Math.sin(this.idleT * 1.6) * 6;
  }

  // ── Spawner ───────────────────────────────────────────────────────────────

  private spawnPipe(): void {
    const isRush = (this.pipesSpawned + 1) % COIN_RUSH_INTERVAL === 0;
    const baseGap = Math.max(GAP_MIN, GAP_START - this.pillarsPassed * 1.2);
    const gap = isRush ? baseGap * COIN_RUSH_GAP_BOOST : baseGap;
    const margin = 60;
    const topH = randInt(margin, GROUND_Y - margin - gap | 0);
    const botY = topH + gap;
    const seed = (Math.random() * 1000) | 0;
    const x = this.pipes.length === 0 ? W + 40 : this.pipes[this.pipes.length - 1].x + PIPE_SPACING;
    const pipe = new Pipe(x, topH, botY, seed, isRush);
    this.pipes.push(pipe);
    this.pipesSpawned++;
    if (isRush) {
      // Coin formation across the gap.
      const cy = (topH + botY) / 2;
      const formations = ["sine", "s_curve", "chevron", "oval"] as const;
      const form = formations[(Math.random() * formations.length) | 0];
      for (let i = 0; i < COIN_RUSH_COINS; i++) {
        const t = i / (COIN_RUSH_COINS - 1);
        let cx = x + PIPE_W / 2;
        let cyy = cy;
        if (form === "sine") {
          cx += (t - 0.5) * PIPE_W * 1.6;
          cyy += Math.sin(t * Math.PI * 2) * gap * 0.32;
        } else if (form === "s_curve") {
          cx += (t - 0.5) * PIPE_W * 1.6;
          cyy += Math.sin(t * Math.PI) * gap * 0.34 - gap * 0.08;
        } else if (form === "chevron") {
          cx += (t - 0.5) * PIPE_W * 1.6;
          cyy += Math.abs(t - 0.5) * gap * 0.5 - gap * 0.12;
        } else {
          const ang = t * Math.PI * 2;
          cx += Math.cos(ang) * PIPE_W * 0.6;
          cyy += Math.sin(ang) * gap * 0.30;
        }
        this.coins.push(new Coin(cx, cyy));
      }
      this.floatTexts.push(new FloatText(W - 40, 80, "COIN RUSH!", [240, 192, 64], [168, 32, 16], 22));
    } else {
      // Maybe spawn a powerup in the gap.
      if (this.powerupCooldown <= 0 && Math.random() < POWERUP_CHANCE) {
        const kind = pickWeighted(POWERUP_WEIGHTS);
        const cy = (topH + botY) / 2 + (Math.random() - 0.5) * gap * 0.4;
        this.powerups.push(new PowerUp(x + PIPE_W / 2, cy, kind));
        this.powerupCooldown = POWERUP_COOLDOWN;
      }
      // Sprinkle one or two coins in non-rush pillars too.
      if (Math.random() < 0.55) {
        const cn = randInt(1, 3);
        for (let i = 0; i < cn; i++) {
          const cy = topH + 30 + (gap - 60) * (i + 1) / (cn + 1);
          this.coins.push(new Coin(x + PIPE_W / 2 + (i - 1) * 18, cy));
        }
      }
    }
  }

  // ── Frame update ──────────────────────────────────────────────────────────

  update(dt: number): void {
    if (this.gameOver) {
      this.bird.update(dt);
      // Bird falls; particles still settle.
      this.updateParticles(dt);
      return;
    }
    if (this.readyT > 0) {
      this.readyT -= dt;
      this.worldIdleTick(dt);
      return;
    }
    this.timeAlive += dt;
    this.biomeTime += dt;
    this.scrollSpeed = Math.min(SCROLL_MAX, SCROLL_BASE + this.pillarsPassed * 0.5);
    const slowmoScale = this.slowmoTimer > 0 ? SLOWMO_SCALE : 1.0;
    const effSpeed = this.scrollSpeed * slowmoScale;
    this.bgScroll += effSpeed * dt;

    // Bird physics — input physics NOT slowed by slowmo.
    this.bird.update(dt);

    // Pipes.
    if (this.pipes.length === 0 || this.pipes[this.pipes.length - 1].x < W - PIPE_SPACING) {
      if (this.timeAlive >= World.SPAWN_GRACE) this.spawnPipe();
    }
    for (const p of this.pipes) p.update(dt, effSpeed);
    this.pipes = this.pipes.filter((p) => !p.offscreen());

    // Coins.
    const magnetActive = this.magnetTimer > 0;
    for (const c of this.coins) {
      if (magnetActive && !c.collected) {
        const dx = this.bird.x - c.x, dy = this.bird.y - c.y;
        const dist = Math.hypot(dx, dy);
        if (dist < MAGNET_RADIUS) {
          const pull = (1 - dist / MAGNET_RADIUS) * 320;
          const inv = pull / Math.max(0.001, dist);
          c.vx = dx * inv;
          c.vy = dy * inv;
          c.magnetPulled = true;
        }
      }
      c.update(dt, effSpeed);
    }
    this.coins = this.coins.filter((c) => !c.collected && !c.offscreen());

    // PowerUps.
    for (const p of this.powerups) p.update(dt, effSpeed);
    this.powerups = this.powerups.filter((p) => !p.collected && !p.offscreen());

    // Score for passing pipes.
    for (const p of this.pipes) {
      if (!p.passed && p.x + PIPE_W < BIRD_X) {
        p.passed = true;
        this.score++;
        this.pillarsPassed++;
      }
    }

    // Collisions.
    if (!this.bird.ghostActive) {
      for (const p of this.pipes) {
        if (this.collidePipe(p)) {
          this.die(p);
          return;
        }
      }
    } else {
      // Ghost: only ground/ceiling kills.
    }
    if (this.bird.y - this.bird.rect().r <= 0 || this.bird.y + this.bird.rect().r >= GROUND_Y) {
      this.die(null);
      return;
    }

    // Coin pickup.
    for (const c of this.coins) {
      if (c.collected) continue;
      const dx = c.x - this.bird.x, dy = c.y - this.bird.y;
      if (Math.hypot(dx, dy) < COIN_R + this.bird.rect().r) {
        c.collected = true;
        this.coinCount++;
        if (this.tripleTimer > 0) {
          this.score += 3;
          audio.playCoinTriple();
          this.floatTexts.push(new FloatText(c.x, c.y, "+3", [240, 192, 64], [168, 32, 16]));
        } else {
          this.score++;
          audio.playCoin();
          this.floatTexts.push(new FloatText(c.x, c.y, "+1", [240, 192, 64], [168, 32, 16]));
        }
        this.spawnCoinSparkles(c.x, c.y);
      }
    }

    // PowerUp pickup.
    for (const p of this.powerups) {
      if (p.collected) continue;
      const dx = p.x - this.bird.x, dy = p.y - this.bird.y;
      if (Math.hypot(dx, dy) < POWERUP_R + this.bird.rect().r) {
        p.collected = true;
        this.onPowerup(p.kind);
      }
    }

    // Power-up timers.
    this.tripleTimer = Math.max(0, this.tripleTimer - dt);
    this.magnetTimer = Math.max(0, this.magnetTimer - dt);
    this.slowmoTimer = Math.max(0, this.slowmoTimer - dt);
    this.kfcTimer = Math.max(0, this.kfcTimer - dt);
    this.ghostTimer = Math.max(0, this.ghostTimer - dt);
    this.growTimer = Math.max(0, this.growTimer - dt);
    this.reverseTimer = Math.max(0, this.reverseTimer - dt);
    this.powerupCooldown = Math.max(0, this.powerupCooldown - dt);
    this.bird.kfcActive = this.kfcTimer > 0;
    this.bird.ghostActive = this.ghostTimer > 0;
    this.bird.growActive = this.growTimer > 0;
    this.bird.tripleActive = this.tripleTimer > 0;

    // Particles + float texts + cloud puffs.
    this.updateParticles(dt);
    for (const f of this.floatTexts) f.update(dt);
    this.floatTexts = this.floatTexts.filter((f) => f.alive());
    for (const c of this.cloudPuffs) c.update(dt);
    this.cloudPuffs = this.cloudPuffs.filter((c) => c.alive());

    // Hit flash + shake decay.
    this.hitFlash = Math.max(0, this.hitFlash - dt);
    this.shakeT = Math.max(0, this.shakeT - dt);

    // Weather.
    this.weather.update(dt, this.biomePalette, effSpeed);
  }

  private updateParticles(dt: number): void {
    for (const p of this.particles) p.update(dt);
    this.particles = this.particles.filter((p) => p.alive());
  }

  private collidePipe(p: Pipe): boolean {
    const r = this.bird.rect();
    const px1 = p.x, px2 = p.x + PIPE_W;
    if (r.x + r.r < px1 || r.x - r.r > px2) return false;
    if (r.y - r.r < p.topH || r.y + r.r > p.botY) return true;
    if (r.parcelY + r.parcelR > p.botY && r.x + r.parcelR > px1 && r.x - r.parcelR < px2) return true;
    if (r.parcelY - r.parcelR < p.topH && r.x + r.parcelR > px1 && r.x - r.parcelR < px2) return true;
    return false;
  }

  private die(pipe: Pipe | null): void {
    this.gameOver = true;
    this.hitPipe = pipe;
    this.hitFlash = 0.35;
    this.shakeMag = 8;
    this.shakeT = 0.3;
    audio.playDeath();
    this.bird.vy = -200;
  }

  private spawnCoinSparkles(x: number, y: number): void {
    for (let i = 0; i < 8; i++) {
      const ang = (i / 8) * Math.PI * 2;
      const sp = 60 + Math.random() * 40;
      const c = i % 2 === 0 ? PARTICLE_COLORS.GOLD : PARTICLE_COLORS.WHT;
      this.particles.push(new Particle(x, y,
        Math.cos(ang) * sp, Math.sin(ang) * sp,
        0.45 + Math.random() * 0.2, c, 2));
    }
  }

  private onPowerup(kind: string): void {
    let realKind = kind;
    if (kind === "surprise") {
      const choices: PowerUpKind[] = ["triple", "magnet", "slowmo", "kfc", "ghost", "grow"];
      realKind = choices[(Math.random() * choices.length) | 0];
      this.powerupsPicked["surprise"]++;
    }
    this.powerupsPicked[realKind] = (this.powerupsPicked[realKind] ?? 0) + 1;
    switch (realKind) {
      case "triple":
        this.tripleTimer = TRIPLE_DURATION;
        audio.playTripleCoin();
        this.floatTexts.push(new FloatText(this.bird.x, this.bird.y - 30, "3× POWER!", [240, 192, 64], [168, 32, 16], 20));
        break;
      case "magnet":
        this.magnetTimer = MAGNET_DURATION;
        audio.playMagnet();
        this.floatTexts.push(new FloatText(this.bird.x, this.bird.y - 30, "MAGNET!", [255, 100, 100], [80, 20, 20], 20));
        break;
      case "slowmo":
        this.slowmoTimer = SLOWMO_DURATION;
        audio.playSlowmo();
        this.floatTexts.push(new FloatText(this.bird.x, this.bird.y - 30, "SLOW-MO!", [180, 110, 240], [60, 20, 90], 20));
        break;
      case "kfc":
        this.kfcTimer = KFC_DURATION;
        audio.playPoof();
        this.cloudPuffs.push(new CloudPuff(this.bird.x, this.bird.y));
        this.floatTexts.push(new FloatText(this.bird.x, this.bird.y - 30, "DEEP FRIED!", [220, 60, 60], [80, 20, 20], 20));
        break;
      case "ghost":
        this.ghostTimer = GHOST_DURATION;
        audio.playGhost();
        this.floatTexts.push(new FloatText(this.bird.x, this.bird.y - 30, "GHOST!", [200, 220, 240], [60, 80, 120], 20));
        break;
      case "grow":
        this.growTimer = GROW_DURATION;
        audio.playGrow();
        this.floatTexts.push(new FloatText(this.bird.x, this.bird.y - 30, "GROW!", [220, 100, 130], [80, 20, 40], 20));
        break;
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  get biomePhase(): number {
    return ((this.biomeTime / 300.0) + 0.04) % 1.0;
  }

  get biomePalette(): Palette {
    return paletteForTime(this.biomeTime);
  }

  shakeOffset(): [number, number] {
    if (this.shakeT <= 0) return [0, 0];
    const k = this.shakeT / 0.3;
    return [
      (Math.random() - 0.5) * 2 * this.shakeMag * k,
      (Math.random() - 0.5) * 2 * this.shakeMag * k,
    ];
  }
}
