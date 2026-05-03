// Game entities — Bird, Pipe, Coin, PowerUp, Particle, FloatText.
// Consolidated from game/entities.py with simplified procedural sprites
// for power-up icons (gameplay-faithful; visual polish iterates).

import {
  W, GRAVITY, FLAP_V, MAX_FALL,
  BIRD_X, BIRD_R, PIPE_W, COIN_R, POWERUP_R, GROUND_Y,
  PARCEL_R, PARCEL_Y_OFFSET, GROW_SCALE,
} from "./config.js";
import {
  rgb, rgba, blitGlow, makeCanvas, ctx2d,
  COIN_GOLD, COIN_DARK,
  PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
} from "./draw.js";
import * as parrot from "./parrot.js";
import { drawPillarPair } from "./pillar-variants.js";
import type { Palette } from "./biome.js";

// ── Bird ────────────────────────────────────────────────────────────────────

export class Bird {
  x = BIRD_X;
  y = 320;
  vy = 0;
  tiltDeg = 0;
  frameT = 0;
  flapBoost = 0;
  ghostPulse = 0;
  kfcActive = false;
  ghostActive = false;
  growActive = false;
  tripleActive = false;

  flap(): void {
    this.vy = FLAP_V;
    this.flapBoost = 1;
  }

  update(dt: number, scrollScale = 1): void {
    this.vy += GRAVITY * dt;
    if (this.vy > MAX_FALL) this.vy = MAX_FALL;
    this.y += this.vy * dt;
    // Tilt: nose up while flapping, nose down on falls.
    const target = this.vy < 0 ? -28 : Math.min(41, this.vy / 14);
    this.tiltDeg += (target - this.tiltDeg) * Math.min(1, dt * 8);
    let baseHz = 9 + this.flapBoost * 20;
    if (this.vy < -100) baseHz += 3;
    else if (this.vy > 200) baseHz = Math.max(3, baseHz - 4);
    this.frameT += dt * baseHz * scrollScale;
    this.flapBoost = Math.max(0, this.flapBoost - dt * 1.8);
    if (this.ghostActive) this.ghostPulse += dt * 2.4;
  }

  draw(cx: CanvasRenderingContext2D, shakeX = 0, shakeY = 0, flipped = false): void {
    const frameIdx = (this.frameT | 0) % parrot.FRAMES.length;
    const tilt = flipped ? -this.tiltDeg : this.tiltDeg;
    let img: HTMLCanvasElement;
    if (this.kfcActive && this.ghostActive && this.tripleActive)
      img = parrot.getKfcGhostHatParrot(frameIdx, tilt);
    else if (this.kfcActive && this.ghostActive)
      img = parrot.getKfcGhostParrot(frameIdx, tilt);
    else if (this.kfcActive && this.tripleActive)
      img = parrot.getKfcHatParrot(frameIdx, tilt);
    else if (this.ghostActive && this.tripleActive)
      img = parrot.getGhostHatParrot(frameIdx, tilt);
    else if (this.kfcActive)
      img = parrot.getFriedParrot(frameIdx, tilt);
    else if (this.ghostActive)
      img = parrot.getGhostParrot(frameIdx, tilt);
    else if (this.tripleActive)
      img = parrot.getHatParrot(frameIdx, tilt);
    else if (this.growActive)
      img = parrot.getGrowParrot(frameIdx, tilt);
    else
      img = parrot.getParrot(frameIdx, tilt);

    if (this.growActive && (this.kfcActive || this.ghostActive || this.tripleActive)) {
      const sw = (img.width * GROW_SCALE) | 0, sh = (img.height * GROW_SCALE) | 0;
      const c = makeCanvas(sw, sh);
      const c2 = ctx2d(c);
      c2.imageSmoothingEnabled = true;
      c2.drawImage(img, 0, 0, sw, sh);
      img = c;
    }
    if (flipped) {
      const c = makeCanvas(img.width, img.height);
      const c2 = ctx2d(c);
      c2.translate(0, img.height);
      c2.scale(1, -1);
      c2.drawImage(img, 0, 0);
      img = c;
    }
    cx.save();
    if (this.ghostActive) {
      const pulse = 0.5 + 0.5 * Math.sin(this.ghostPulse);
      cx.globalAlpha = (90 + pulse * 80) / 255;
    }
    cx.drawImage(img, (this.x + shakeX - img.width / 2) | 0,
                       (this.y + shakeY - img.height / 2) | 0);
    cx.restore();

    // Parcel companion.
    const mode: parrot.ParcelMode =
      this.kfcActive ? "kfc" :
      this.ghostActive ? "ghost" :
      this.tripleActive ? "triple" : "normal";
    let parcel = parrot.getParcel(mode);
    const scale = this.growActive ? GROW_SCALE : 1.0;
    if (scale !== 1.0) {
      const pw = (parcel.width * scale) | 0, ph = (parcel.height * scale) | 0;
      const c = makeCanvas(pw, ph);
      const c2 = ctx2d(c);
      c2.imageSmoothingEnabled = true;
      c2.drawImage(parcel, 0, 0, pw, ph);
      parcel = c;
    }
    if (flipped) {
      const c = makeCanvas(parcel.width, parcel.height);
      const c2 = ctx2d(c);
      c2.translate(0, parcel.height);
      c2.scale(1, -1);
      c2.drawImage(parcel, 0, 0);
      parcel = c;
    }
    const yOff = flipped ? -PARCEL_Y_OFFSET * scale : PARCEL_Y_OFFSET * scale;
    cx.save();
    if (this.ghostActive) {
      const pulse = 0.5 + 0.5 * Math.sin(this.ghostPulse);
      cx.globalAlpha = (110 + pulse * 70) / 255;
    }
    cx.drawImage(parcel,
      (this.x + shakeX - parcel.width / 2) | 0,
      (this.y + shakeY + yOff - parcel.height / 2) | 0);
    cx.restore();
  }

  rect(): { x: number; y: number; r: number; parcelY: number; parcelR: number } {
    return {
      x: this.x, y: this.y, r: BIRD_R * (this.growActive ? GROW_SCALE : 1),
      parcelY: this.y + PARCEL_Y_OFFSET * (this.growActive ? GROW_SCALE : 1),
      parcelR: PARCEL_R * (this.growActive ? GROW_SCALE : 1),
    };
  }
}

// ── Pipe ────────────────────────────────────────────────────────────────────

export class Pipe {
  x: number;
  topH: number;
  botY: number;
  passed = false;
  isCoinRush: boolean;
  seed: number;

  constructor(x: number, topH: number, botY: number, seed: number, isCoinRush = false) {
    this.x = x;
    this.topH = topH;
    this.botY = botY;
    this.seed = seed;
    this.isCoinRush = isCoinRush;
  }

  update(dt: number, scrollSpeed: number): void {
    this.x -= scrollSpeed * dt;
  }

  offscreen(): boolean { return this.x + PIPE_W < -10; }

  draw(cx: CanvasRenderingContext2D, palette: Palette): void {
    drawPillarPair(cx, this.x, this.topH, this.botY, palette, PIPE_W, this.botY - this.topH, this.seed);
  }
}

// ── Coin ────────────────────────────────────────────────────────────────────

let _coinFace: HTMLCanvasElement | null = null;

function getCoinFace(): HTMLCanvasElement {
  if (_coinFace) return _coinFace;
  const D = COIN_R * 2 + 2;
  const c = makeCanvas(D, D);
  const cx = ctx2d(c);
  // Body gradient.
  const grad = cx.createLinearGradient(0, 0, 0, D);
  grad.addColorStop(0, rgb([255, 245, 130]));
  grad.addColorStop(0.5, rgb(COIN_GOLD));
  grad.addColorStop(1, rgb(COIN_DARK));
  cx.fillStyle = grad;
  cx.beginPath(); cx.arc(D / 2, D / 2, COIN_R, 0, Math.PI * 2); cx.fill();
  // Outer band.
  cx.strokeStyle = rgb([180, 120, 0]); cx.lineWidth = 2;
  cx.beginPath(); cx.arc(D / 2, D / 2, COIN_R - 1, 0, Math.PI * 2); cx.stroke();
  // Embossed parrot silhouette (simplified — solid ellipse + dot).
  cx.fillStyle = rgb([200, 140, 0]);
  cx.beginPath(); cx.ellipse(D / 2, D / 2 + 1, COIN_R - 5, COIN_R - 6, 0, 0, Math.PI * 2); cx.fill();
  cx.fillStyle = rgb([255, 230, 120]);
  cx.beginPath(); cx.arc(D / 2 - 2, D / 2 - 1, COIN_R - 8, 0, Math.PI * 2); cx.fill();
  // Specular highlight.
  cx.fillStyle = rgba([255, 255, 255], 200);
  cx.beginPath();
  cx.ellipse(D / 2 - 4, D / 2 - 5, 3, 2, 0, 0, Math.PI * 2);
  cx.fill();
  _coinFace = c;
  return c;
}

export class Coin {
  x: number; y: number;
  collected = false;
  spinT = Math.random() * Math.PI * 2;
  vx = 0; vy = 0;
  magnetPulled = false;

  constructor(x: number, y: number) { this.x = x; this.y = y; }

  update(dt: number, scrollSpeed: number): void {
    if (this.magnetPulled) {
      this.x += this.vx * dt;
      this.y += this.vy * dt;
    } else {
      this.x -= scrollSpeed * dt;
    }
    this.spinT += dt * 4;
  }

  offscreen(): boolean { return this.x + COIN_R < -10; }

  draw(cx: CanvasRenderingContext2D): void {
    // Spin squeeze: scale x by |cos(spinT)|.
    const sq = Math.max(0.15, Math.abs(Math.cos(this.spinT)));
    const face = getCoinFace();
    const sw = Math.max(2, (face.width * sq) | 0);
    cx.save();
    cx.translate(this.x | 0, this.y | 0);
    cx.drawImage(face, -sw / 2, -face.height / 2, sw, face.height);
    cx.restore();
    // Sparkle.
    if (Math.sin(this.spinT * 3) > 0.85) {
      blitGlow(cx, this.x, this.y - 2, 4, [255, 240, 160], 80);
    }
  }
}

// ── PowerUp ─────────────────────────────────────────────────────────────────

const POWERUP_COLORS: Record<string, readonly [number, number, number]> = {
  triple: [240, 192, 64],
  magnet: [200, 50, 60],
  slowmo: [140, 70, 210],
  kfc: [220, 60, 60],
  ghost: [200, 220, 240],
  grow: [180, 90, 110],
  reverse: [120, 100, 200],
  surprise: [240, 192, 64],
};

export class PowerUp {
  x: number; y: number;
  kind: string;
  collected = false;
  spinT = 0;

  constructor(x: number, y: number, kind: string) {
    this.x = x; this.y = y; this.kind = kind;
  }

  update(dt: number, scrollSpeed: number): void {
    this.x -= scrollSpeed * dt;
    this.spinT += dt * 2;
  }

  offscreen(): boolean { return this.x + POWERUP_R < -10; }

  draw(cx: CanvasRenderingContext2D): void {
    const col = POWERUP_COLORS[this.kind] ?? [240, 192, 64];
    // Glow halo.
    blitGlow(cx, this.x, this.y, POWERUP_R + 8, col, 90);
    // Outer ring.
    cx.fillStyle = rgb([20, 12, 18]);
    cx.beginPath(); cx.arc(this.x, this.y, POWERUP_R + 2, 0, Math.PI * 2); cx.fill();
    // Body — radial gradient.
    const grad = cx.createRadialGradient(this.x - 3, this.y - 3, 1, this.x, this.y, POWERUP_R);
    grad.addColorStop(0, rgb([
      Math.min(255, col[0] + 40),
      Math.min(255, col[1] + 40),
      Math.min(255, col[2] + 40),
    ]));
    grad.addColorStop(1, rgb(col));
    cx.fillStyle = grad;
    cx.beginPath(); cx.arc(this.x, this.y, POWERUP_R, 0, Math.PI * 2); cx.fill();
    // Glyph by kind.
    cx.fillStyle = rgb([255, 255, 255]);
    cx.font = `bold ${POWERUP_R + 4}px LiberationSans, Arial`;
    cx.textAlign = "center";
    cx.textBaseline = "middle";
    const glyph: Record<string, string> = {
      triple: "$", magnet: "M", slowmo: "⌛", kfc: "K",
      ghost: "👻", grow: "🍄", reverse: "⇅", surprise: "?",
    };
    cx.fillText(glyph[this.kind] ?? "?", this.x, this.y + 1);
  }
}

// ── Particle ────────────────────────────────────────────────────────────────

export class Particle {
  x: number; y: number; vx: number; vy: number;
  life: number; max: number;
  color: readonly [number, number, number];
  size: number;
  glow: boolean;

  constructor(x: number, y: number, vx: number, vy: number, life: number,
              color: readonly [number, number, number], size = 3, glow = true) {
    this.x = x; this.y = y; this.vx = vx; this.vy = vy;
    this.life = life; this.max = life;
    this.color = color; this.size = size; this.glow = glow;
  }

  update(dt: number): void {
    this.x += this.vx * dt;
    this.y += this.vy * dt;
    this.vy += 200 * dt;
    this.life -= dt;
  }

  alive(): boolean { return this.life > 0; }

  draw(cx: CanvasRenderingContext2D): void {
    const t = this.life / this.max;
    const a = Math.max(0, Math.min(255, (255 * t) | 0));
    if (this.glow) blitGlow(cx, this.x, this.y, this.size + 2, this.color, a);
    cx.fillStyle = rgba(this.color, a);
    cx.beginPath();
    cx.arc(this.x | 0, this.y | 0, this.size, 0, Math.PI * 2);
    cx.fill();
  }
}

export const PARTICLE_COLORS = {
  GOLD: PARTICLE_GOLD, ORNG: PARTICLE_ORNG, WHT: PARTICLE_WHT, CRIM: PARTICLE_CRIM,
};

// ── CloudPuff ───────────────────────────────────────────────────────────────

export class CloudPuff {
  x: number; y: number; t = 0; max: number;
  constructor(x: number, y: number, life = 0.55) {
    this.x = x; this.y = y; this.max = life;
  }
  update(dt: number): void { this.t += dt; }
  alive(): boolean { return this.t < this.max; }
  draw(cx: CanvasRenderingContext2D): void {
    const k = this.t / this.max;
    const r = 8 + k * 14;
    const a = (180 * (1 - k)) | 0;
    cx.fillStyle = rgba([255, 255, 255], a);
    cx.beginPath(); cx.arc(this.x, this.y, r, 0, Math.PI * 2); cx.fill();
  }
}

// ── FloatText ───────────────────────────────────────────────────────────────

export class FloatText {
  x: number; y: number;
  text: string;
  color: readonly [number, number, number];
  outline: readonly [number, number, number];
  t = 0;
  max = 1.0;
  size: number;

  constructor(x: number, y: number, text: string,
              color: readonly [number, number, number] = [240, 192, 64],
              outline: readonly [number, number, number] = [168, 32, 16],
              size = 22) {
    this.x = x; this.y = y; this.text = text;
    this.color = color; this.outline = outline; this.size = size;
  }

  update(dt: number): void { this.t += dt; this.y -= 30 * dt; }
  alive(): boolean { return this.t < this.max; }

  draw(cx: CanvasRenderingContext2D): void {
    const k = this.t / this.max;
    const a = Math.max(0, Math.min(1, 1 - k * 0.7));
    cx.save();
    cx.globalAlpha = a;
    cx.font = `900 ${this.size}px LiberationSans, Arial`;
    cx.textAlign = "center";
    cx.textBaseline = "middle";
    cx.lineWidth = 4;
    cx.strokeStyle = rgb(this.outline);
    cx.strokeText(this.text, this.x, this.y);
    cx.fillStyle = rgb(this.color);
    cx.fillText(this.text, this.x, this.y);
    cx.restore();
  }
}

// Helper for callers that need to know the playfield width.
export const FIELD_W = W;
export const FIELD_GROUND_Y = GROUND_Y;
