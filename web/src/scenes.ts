// Scene state machine + top-level App. Drives the main RAF loop, routes
// input, runs the world, and orchestrates HUD overlays.
//
// Mirrors the public surface of game/scenes.py (App / state constants /
// handlers) without the once-per-launch intro cinematic — that 1106-LOC
// module is deferred for v2.

import { W, H, FPS, GROUND_Y } from "./config.js";
import {
  getSkySurfaceBiome, drawMountains, drawCloud, drawGround, rgba,
} from "./draw.js";
import { paletteForPhase, PHASE_BUCKETS } from "./biome.js";
import { World } from "./world.js";
import { HUD } from "./hud.js";
import * as audio from "./audio.js";
import {
  fetchTop10, submit, lastFetchError, openNameEntry, newRunId, logRun,
  type ScoreRow,
} from "./leaderboard.js";

export const STATE_MENU = 0;
export const STATE_PLAY = 1;
export const STATE_NAMEENTRY = 2;
export const STATE_GAMEOVER = 3;
export const STATE_PAUSE = 4;
export const STATE_STATS = 5;
export const STATE_LEADERBOARD = 6;

export class App {
  private screen: HTMLCanvasElement;
  private cx: CanvasRenderingContext2D;
  world = new World();
  hud = new HUD();
  sessionBest = 0;
  newBest = false;
  state: number = STATE_MENU;
  cooldownT = 0;
  cloudPhase = 0;
  statsT = 0;
  fetchPending = false;
  finalScore = 0;
  lbScores: ScoreRow[] = [];
  lbPlayerRank = -1;
  lbFetchError = "";
  private lastTs = 0;
  private running = true;

  constructor(canvas: HTMLCanvasElement) {
    this.screen = canvas;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Canvas 2D context unavailable");
    this.cx = ctx;
    audio.init();
    this.attachInput();
    this.fitCanvas();
    window.addEventListener("resize", () => this.fitCanvas());
  }

  // ── Canvas sizing — preserve 360x640 aspect, fit to viewport ──────────────

  private fitCanvas(): void {
    const aspect = W / H;
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    let cw = vw, ch = vw / aspect;
    if (ch > vh) { ch = vh; cw = vh * aspect; }
    this.screen.style.width = `${cw}px`;
    this.screen.style.height = `${ch}px`;
  }

  // ── Input ─────────────────────────────────────────────────────────────────

  private attachInput(): void {
    const onTap = (clientX: number, clientY: number, e: Event) => {
      e.preventDefault();
      // Translate viewport coords to game coords for hit-tests.
      const r = this.screen.getBoundingClientRect();
      const x = ((clientX - r.left) / r.width) * W;
      const y = ((clientY - r.top) / r.height) * H;
      this.flapInput(x, y);
    };
    window.addEventListener("pointerdown", (e) => onTap(e.clientX, e.clientY, e));
    window.addEventListener("keydown", (e) => {
      if (e.key === " " || e.key === "ArrowUp" || e.key === "w") {
        e.preventDefault();
        this.flapInput(undefined, undefined);
      } else if (e.key === "p" || e.key === "P") {
        this.togglePause();
      } else if (e.key === "Escape") {
        if (this.state === STATE_PLAY || this.state === STATE_PAUSE) this.togglePause();
      }
    });
  }

  private flapInput(x?: number, y?: number): void {
    audio.unlockAudio(); // first user gesture unlocks Web Audio.
    if (this.state === STATE_MENU) {
      if (this.cooldownT <= 0) this.startPlay();
    } else if (this.state === STATE_PLAY) {
      if (x !== undefined && y !== undefined) {
        const pb = this.hud.pauseBtn;
        if (Math.hypot(x - pb.x, y - pb.y) <= pb.r) {
          this.state = STATE_PAUSE;
          return;
        }
      }
      this.world.flap();
    } else if (this.state === STATE_PAUSE) {
      this.state = STATE_PLAY;
    } else if (this.state === STATE_STATS) {
      if (this.statsT >= 0.6 && !this.fetchPending) this.advancePastStats();
    } else if (this.state === STATE_LEADERBOARD) {
      if (this.cooldownT <= 0) {
        this.state = STATE_MENU;
        this.cooldownT = 0.4;
      }
    } else if (this.state === STATE_GAMEOVER) {
      if (this.cooldownT <= 0) this.restart();
    }
  }

  private togglePause(): void {
    if (this.state === STATE_PLAY) this.state = STATE_PAUSE;
    else if (this.state === STATE_PAUSE) this.state = STATE_PLAY;
  }

  private startPlay(): void {
    this.world = new World();
    this.world.readyT = 0;
    this.world.flap();
    this.state = STATE_PLAY;
  }

  private restart(): void {
    this.world = new World();
    this.world.readyT = 0;
    this.world.flap();
    this.state = STATE_PLAY;
  }

  private onDeath(): void {
    audio.playGameover();
    const score = this.world.score;
    this.newBest = score > this.sessionBest;
    if (this.newBest) this.sessionBest = score;
    // Best-effort telemetry.
    void logRun({
      score, duration_s: this.world.timeAlive, coins: this.world.coinCount,
      pillars: this.world.pillarsPassed, near_misses: this.world.nearMisses,
      powerups: this.world.powerupsPicked,
    });
    this.state = STATE_STATS;
    this.statsT = 0;
  }

  private advancePastStats(): void {
    this.finalScore = this.world.score;
    this.fetchPending = true;
    void this.handleNameAndLeaderboard();
  }

  private async handleNameAndLeaderboard(): Promise<void> {
    try {
      let scores = await fetchTop10();
      this.lbFetchError = lastFetchError();
      const qualifies = this.qualifiesForTop10(scores, this.finalScore);
      if (qualifies) {
        this.state = STATE_NAMEENTRY;
        const name = await openNameEntry();
        if (name) {
          await submit(name, this.finalScore, newRunId());
          scores = await fetchTop10();
          this.lbFetchError = lastFetchError();
          this.lbPlayerRank = scores.findIndex((r) => r.score === this.finalScore);
        } else {
          this.lbPlayerRank = -1;
        }
      } else {
        this.lbPlayerRank = -1;
      }
      this.lbScores = scores;
    } catch (e) {
      console.warn("[skybit] leaderboard flow failed", e);
    }
    this.fetchPending = false;
    this.hud.titleT = 0;
    this.state = STATE_LEADERBOARD;
    this.cooldownT = 1.0;
  }

  private qualifiesForTop10(scores: ScoreRow[], score: number): boolean {
    if (score <= 0) return false;
    if (scores.length < 10) return true;
    return score > scores[scores.length - 1].score;
  }

  // ── Update / render ───────────────────────────────────────────────────────

  private update(dt: number): void {
    this.cloudPhase += dt;
    this.cooldownT = Math.max(0, this.cooldownT - dt);
    if (this.state === STATE_MENU) {
      this.world.worldIdleTick(dt);
    } else if (this.state === STATE_PLAY) {
      this.world.update(dt);
      if (this.world.gameOver) this.onDeath();
    } else if (this.state === STATE_PAUSE) {
      this.hud.titleT += dt;
    } else if (this.state === STATE_STATS) {
      this.world.update(dt);
      this.statsT += dt;
    } else if (this.state === STATE_NAMEENTRY) {
      this.world.update(dt);
    }
  }

  private drawBackground(): void {
    const palette = this.world.biomePalette;
    const phase = this.world.biomePhase;
    const buckets = PHASE_BUCKETS;
    const bucketF = (phase % 1.0) * buckets;
    const a = (bucketF | 0) % buckets;
    const b = (a + 1) % buckets;
    const t = bucketF - (bucketF | 0);
    const palA = paletteForPhase(a / buckets);
    const palB = paletteForPhase(b / buckets);
    const skyA = getSkySurfaceBiome(W, H, GROUND_Y, palA, a);
    const skyB = getSkySurfaceBiome(W, H, GROUND_Y, palB, b);
    this.cx.drawImage(skyA, 0, 0);
    if (t > 0) {
      this.cx.save();
      this.cx.globalAlpha = t;
      this.cx.drawImage(skyB, 0, 0);
      this.cx.restore();
    }
    const scroll = this.world.bgScroll;
    const variants = [[20, 90, 0.9, 0], [180, 140, 1.1, 2],
                      [60, 220, 0.8, 3], [230, 60, 0.7, 1],
                      [320, 180, 0.9, 4]] as const;
    variants.forEach(([bx, by, sc, variant], i) => {
      const ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160) + W + 160) % (W + 160) - 80;
      drawCloud(this.cx, ox, by + Math.sin(this.cloudPhase * 0.3 + i) * 3, sc, variant);
    });
    drawMountains(this.cx, scroll, GROUND_Y, W, palette.mtn_far, palette.mtn_near);
    drawGround(this.cx, GROUND_Y, W, H, scroll,
               palette.ground_top, palette.ground_mid, [60, 40, 25]);
  }

  private render(): void {
    const [sx, sy] = this.state === STATE_PLAY ? this.world.shakeOffset() : [0, 0];
    this.drawBackground();
    if (this.state === STATE_MENU) {
      this.world.bird.draw(this.cx, sx, sy);
      this.hud.drawMenu(this.cx, 1 / 60, this.sessionBest);
      return;
    }
    // World entities.
    const palette = this.world.biomePalette;
    for (const p of this.world.pipes) p.draw(this.cx, palette);
    this.world.weather.draw(this.cx);
    for (const c of this.world.coins) c.draw(this.cx);
    for (const m of this.world.powerups) m.draw(this.cx);
    this.world.bird.draw(this.cx, sx, sy, this.world.reverseTimer > 0);
    for (const p of this.world.particles) p.draw(this.cx);
    for (const c of this.world.cloudPuffs) c.draw(this.cx);

    // Tints.
    if (this.world.slowmoTimer > 0) {
      this.cx.fillStyle = rgba([140, 70, 210], 28); this.cx.fillRect(0, 0, W, H);
    }
    if (this.world.kfcTimer > 0) {
      this.cx.fillStyle = rgba([210, 120, 10], 20); this.cx.fillRect(0, 0, W, H);
    }
    if (this.world.ghostTimer > 0) {
      this.cx.fillStyle = rgba([140, 180, 255], 18); this.cx.fillRect(0, 0, W, H);
    }
    if (this.world.hitFlash > 0) {
      const t = this.world.hitFlash / 0.35;
      this.cx.fillStyle = rgba([230, 40, 40], (120 * t) | 0);
      this.cx.fillRect(0, 0, W, H);
    }

    if (this.state === STATE_PLAY) this.hud.drawPlay(this.cx, this.world, this.sessionBest);
    else if (this.state === STATE_PAUSE) {
      this.hud.drawPlay(this.cx, this.world, this.sessionBest, true);
      this.hud.drawPauseOverlay(this.cx);
    } else if (this.state === STATE_STATS) {
      this.hud.drawStats(this.cx, this.world, 1 / 60, this.statsT, !this.fetchPending);
    } else if (this.state === STATE_LEADERBOARD) {
      this.hud.drawLeaderboard(this.cx, 1 / 60, this.lbScores, this.lbPlayerRank,
                               this.cooldownT, this.lbFetchError);
    } else if (this.state === STATE_GAMEOVER) {
      this.hud.drawGameover(this.cx, 1 / 60, this.world.score, this.newBest);
    }
  }

  // ── Main loop ────────────────────────────────────────────────────────────

  start(): void {
    let firstFrame = true;
    const loop = (ts: number) => {
      if (!this.running) return;
      const dt = this.lastTs === 0 ? 1 / FPS : Math.min(1 / 20, (ts - this.lastTs) / 1000);
      this.lastTs = ts;
      this.update(dt);
      this.render();
      if (firstFrame) {
        firstFrame = false;
        // Hide the loading splash now that the canvas has a real frame.
        const ov = document.getElementById("skybit-loading");
        if (ov) ov.classList.add("skybit-hidden");
        // Mark dispatchable readiness for any external observer.
        (window as any).skybitGameReady = true;
      }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }
}
