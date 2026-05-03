// Low-level Canvas2D drawing utilities — ported from game/draw.py.
// All offscreen surfaces are pre-computed once and cached.

import type { Color, Palette } from "./biome.js";
import { lerpColor } from "./biome.js";

// ── Colour constants ────────────────────────────────────────────────────────
export const SKY_TOP: Color = [12, 18, 55];
export const SKY_MID: Color = [25, 60, 130];
export const SKY_BOT: Color = [40, 140, 210];
export const HORIZON_GLOW: Color = [255, 200, 100];
export const MTN_FAR: Color = [35, 45, 100];
export const MTN_NEAR: Color = [22, 30, 72];
export const GROUND_TOP: Color = [60, 190, 60];
export const GROUND_MID: Color = [30, 140, 30];
export const GROUND_BOT: Color = [80, 50, 20];
export const PIPE_HILIGHT: Color = [110, 240, 110];
export const PIPE_MID: Color = [45, 185, 45];
export const PIPE_DARK: Color = [20, 100, 20];
export const PIPE_SHADOW: Color = [12, 60, 12];
export const COIN_GOLD: Color = [255, 210, 20];
export const COIN_LIGHT: Color = [255, 245, 120];
export const COIN_DARK: Color = [200, 140, 0];
export const MUSH_CAP: Color = [125, 30, 45];
export const MUSH_CAP2: Color = [180, 60, 75];
export const MUSH_SPOT: Color = [255, 235, 175];
export const MUSH_STEM: Color = [245, 230, 200];
export const BIRD_RED: Color = [240, 55, 55];
export const BIRD_RED_D: Color = [170, 25, 25];
export const BIRD_WING: Color = [40, 100, 255];
export const BIRD_WING_D: Color = [20, 55, 180];
export const BIRD_TIP: Color = [50, 220, 100];
export const BIRD_BELLY: Color = [255, 170, 50];
export const BIRD_BEAK: Color = [255, 185, 0];
export const BIRD_BEAK_D: Color = [200, 130, 0];
export const WHITE: Color = [255, 255, 255];
export const BLACK: Color = [0, 0, 0];
export const NEAR_BLACK: Color = [15, 15, 30];
export const UI_SCORE: Color = [255, 255, 255];
export const UI_GOLD: Color = [255, 215, 0];
export const UI_ORANGE: Color = [255, 155, 30];
export const UI_SHADOW: Color = [0, 0, 0];
export const UI_CREAM: Color = [245, 230, 200];
export const UI_RED: Color = [230, 40, 40];
export const PARTICLE_GOLD: Color = [255, 215, 0];
export const PARTICLE_ORNG: Color = [255, 140, 0];
export const PARTICLE_WHT: Color = [255, 255, 220];
export const PARTICLE_CRIM: Color = [220, 30, 30];

// ── Helpers ────────────────────────────────────────────────────────────────

export function rgb(c: Color, a = 1): string {
  return a >= 1 ? `rgb(${c[0]},${c[1]},${c[2]})` : `rgba(${c[0]},${c[1]},${c[2]},${a})`;
}

export function rgba(c: Color, alpha255: number): string {
  return `rgba(${c[0]},${c[1]},${c[2]},${Math.max(0, Math.min(255, alpha255)) / 255})`;
}

export function lerpColorMulti(stops: ReadonlyArray<readonly [number, Color]>, t: number): Color {
  t = Math.max(0, Math.min(1, t));
  for (let i = 0; i < stops.length - 1; i++) {
    const [t0, c0] = stops[i];
    const [t1, c1] = stops[i + 1];
    if (t <= t1) {
      const seg = t1 > t0 ? (t - t0) / (t1 - t0) : 0;
      return lerpColor(c0, c1, seg);
    }
  }
  return stops[stops.length - 1][1];
}

export function makeCanvas(w: number, h: number): HTMLCanvasElement {
  const c = document.createElement("canvas");
  c.width = Math.max(1, Math.round(w));
  c.height = Math.max(1, Math.round(h));
  return c;
}

export function ctx2d(c: HTMLCanvasElement): CanvasRenderingContext2D {
  const x = c.getContext("2d");
  if (!x) throw new Error("2D context unavailable");
  return x;
}

// ── Gradient surfaces ──────────────────────────────────────────────────────

export function makeGradientSurface(
  w: number, h: number,
  stops: ReadonlyArray<readonly [number, Color]>,
  horizontal = false,
): HTMLCanvasElement {
  const c = makeCanvas(w, h);
  const cx = ctx2d(c);
  const span = horizontal ? w : h;
  for (let i = 0; i < span; i++) {
    const col = lerpColorMulti(stops, i / Math.max(1, span - 1));
    cx.fillStyle = rgb(col);
    if (horizontal) cx.fillRect(i, 0, 1, h);
    else cx.fillRect(0, i, w, 1);
  }
  return c;
}

// ── Radial glow ────────────────────────────────────────────────────────────

export function makeGlowSurface(
  radius: number, color: Color,
  alphaCenter = 180, falloff = 1.8,
): HTMLCanvasElement {
  const size = radius * 2 + 2;
  const c = makeCanvas(size, size);
  const cx = ctx2d(c);
  const cxn = radius + 1, cyn = radius + 1;
  for (let r = radius; r > 0; r--) {
    const t = Math.pow(r / radius, falloff);
    const a = Math.round(alphaCenter * (1 - t));
    cx.fillStyle = rgba(color, a);
    cx.beginPath();
    cx.arc(cxn, cyn, r, 0, Math.PI * 2);
    cx.fill();
  }
  return c;
}

const _glowCache = new Map<string, HTMLCanvasElement>();

export function getGlow(radius: number, color: Color, alpha = 160): HTMLCanvasElement {
  const key = `${radius | 0}|${color[0]},${color[1]},${color[2]}|${alpha | 0}`;
  let g = _glowCache.get(key);
  if (!g) {
    g = makeGlowSurface(radius, color, alpha);
    _glowCache.set(key, g);
  }
  return g;
}

export function blitGlow(
  cx: CanvasRenderingContext2D,
  x: number, y: number, radius: number,
  color: Color, alpha = 160,
): void {
  const g = getGlow(radius, color, alpha);
  const prev = cx.globalCompositeOperation;
  cx.globalCompositeOperation = "lighter"; // pygame.BLEND_ADD
  cx.drawImage(g, (x - radius - 1) | 0, (y - radius - 1) | 0);
  cx.globalCompositeOperation = prev;
}

// ── Rounded rect helpers ──────────────────────────────────────────────────

function roundRectPath(
  cx: CanvasRenderingContext2D,
  x: number, y: number, w: number, h: number, r: number,
): void {
  r = Math.min(r, w / 2, h / 2);
  cx.beginPath();
  cx.moveTo(x + r, y);
  cx.lineTo(x + w - r, y);
  cx.quadraticCurveTo(x + w, y, x + w, y + r);
  cx.lineTo(x + w, y + h - r);
  cx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  cx.lineTo(x + r, y + h);
  cx.quadraticCurveTo(x, y + h, x, y + h - r);
  cx.lineTo(x, y + r);
  cx.quadraticCurveTo(x, y, x + r, y);
  cx.closePath();
}

export function roundedRect(
  cx: CanvasRenderingContext2D,
  x: number, y: number, w: number, h: number,
  radius: number, color: Color, alpha255 = 255,
): void {
  cx.save();
  roundRectPath(cx, x, y, w, h, radius);
  cx.fillStyle = rgba(color, alpha255);
  cx.fill();
  cx.restore();
}

export function roundedRectGrad(
  cx: CanvasRenderingContext2D,
  x: number, y: number, w: number, h: number,
  radius: number, top: Color, bot: Color,
): void {
  cx.save();
  roundRectPath(cx, x, y, w, h, radius);
  const g = cx.createLinearGradient(0, y, 0, y + h);
  g.addColorStop(0, rgb(top));
  g.addColorStop(1, rgb(bot));
  cx.fillStyle = g;
  cx.fill();
  cx.restore();
}

// ── Sky cache ──────────────────────────────────────────────────────────────

const _bgCache = new Map<string, HTMLCanvasElement>();

export function getSkySurface(w: number, h: number, groundY: number): HTMLCanvasElement {
  const key = `sky|${w}|${h}|${groundY}`;
  let c = _bgCache.get(key);
  if (!c) {
    c = makeGradientSurface(w, groundY, [
      [0.0, SKY_TOP],
      [0.35, SKY_MID],
      [0.75, SKY_BOT],
      [1.0, [120, 195, 235]],
    ]);
    _bgCache.set(key, c);
  }
  return c;
}

// Mulberry32 PRNG, seeded — deterministic star sprinkle per cache key.
function mulberry32(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return (((t ^ (t >>> 14)) >>> 0)) / 4294967296;
  };
}

export function getSkySurfaceBiome(
  w: number, h: number, groundY: number, palette: Palette, phaseBucket: number,
): HTMLCanvasElement {
  const key = `sky_b|${w}|${h}|${groundY}|${phaseBucket}|${palette.star_alpha | 0}`;
  let c = _bgCache.get(key);
  if (c) return c;
  c = makeGradientSurface(w, groundY, [
    [0.0, palette.sky_top],
    [0.45, palette.sky_mid],
    [0.85, palette.sky_bot],
    [1.0, palette.horizon],
  ]);
  const sa = Math.round(palette.star_alpha);
  if (sa > 0) {
    const cx = ctx2d(c);
    const rng = mulberry32(w * 7919);
    const starBand = Math.round(groundY * 0.72);
    const n = sa > 180 ? 60 : 30;
    for (let i = 0; i < n; i++) {
      const sx = (rng() * w) | 0;
      const sy = (rng() * starBand) | 0;
      const sz = [1, 1, 1, 2][(rng() * 4) | 0];
      cx.fillStyle = rgba([255, 255, 255], sa);
      cx.beginPath();
      cx.arc(sx, sy, sz, 0, Math.PI * 2);
      cx.fill();
    }
    for (let i = 0; i < 6; i++) {
      const sx = (rng() * w) | 0;
      const sy = (rng() * starBand) | 0;
      cx.fillStyle = rgba([255, 240, 200], Math.min(255, sa + 20));
      cx.beginPath();
      cx.arc(sx, sy, 2, 0, Math.PI * 2);
      cx.fill();
    }
  }
  _bgCache.set(key, c);
  return c;
}

export function getPipeBodyGradient(w: number, h: number): HTMLCanvasElement {
  const key = `pipebody|${w}|${h}`;
  let c = _bgCache.get(key);
  if (!c) {
    c = makeGradientSurface(w, h, [
      [0.0, PIPE_HILIGHT], [0.18, PIPE_MID],
      [0.55, PIPE_DARK], [0.82, PIPE_DARK],
      [1.0, PIPE_SHADOW],
    ], true);
    _bgCache.set(key, c);
  }
  return c;
}

export function getPipeCapGradient(w: number, h: number): HTMLCanvasElement {
  const key = `pipecap|${w}|${h}`;
  let c = _bgCache.get(key);
  if (!c) {
    c = makeGradientSurface(w, h, [
      [0.0, PIPE_HILIGHT], [0.12, PIPE_MID],
      [0.50, PIPE_DARK], [0.88, PIPE_DARK],
      [1.0, PIPE_SHADOW],
    ], true);
    _bgCache.set(key, c);
  }
  return c;
}

// ── Mountain layers ────────────────────────────────────────────────────────

function clampedMid(a: number, b: number): number {
  return Math.max(0, Math.min(255, ((a + b) / 2) | 0));
}

export function drawMountains(
  cx: CanvasRenderingContext2D,
  scroll: number, groundY: number, w: number,
  farColor?: Color, nearColor?: Color,
): void {
  const far = farColor ?? MTN_FAR;
  const near = nearColor ?? MTN_NEAR;
  const back: Color = [
    clampedMid(far[0], 200),
    clampedMid(far[1], 210),
    clampedMid(far[2], 230),
  ];
  const ptsBack: Array<[number, number]> = [[0, groundY]];
  const ptsFar: Array<[number, number]> = [[0, groundY]];
  const ptsNear: Array<[number, number]> = [[0, groundY]];
  for (let x = 0; x <= w; x += 2) {
    const bx = x + scroll * 0.06;
    const hb = (105 + Math.sin(bx * 0.008) * 32 + Math.sin(bx * 0.023 + 2.1) * 14) | 0;
    ptsBack.push([x, groundY - hb]);
    const fx = x + scroll * 0.15;
    const hf = (80 + Math.sin(fx * 0.012) * 42 + Math.sin(fx * 0.031) * 22) | 0;
    ptsFar.push([x, groundY - hf]);
    const nx = x + scroll * 0.28;
    const hn = (55 + Math.sin(nx * 0.019 + 1.4) * 34 + Math.sin(nx * 0.047 + 0.7) * 16) | 0;
    ptsNear.push([x, groundY - hn]);
  }
  for (const pts of [ptsBack, ptsFar, ptsNear]) pts.push([w, groundY]);
  const drawPoly = (pts: Array<[number, number]>, color: Color) => {
    cx.fillStyle = rgb(color);
    cx.beginPath();
    cx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) cx.lineTo(pts[i][0], pts[i][1]);
    cx.closePath();
    cx.fill();
  };
  drawPoly(ptsBack, back);
  drawPoly(ptsFar, far);
  drawPoly(ptsNear, near);
}

// ── Cloud variants ─────────────────────────────────────────────────────────

const CLOUD_VARIANTS: ReadonlyArray<ReadonlyArray<readonly [number, number, number, number]>> = [
  [[0, 0, 22, 230], [28, -6, 28, 235], [56, 0, 20, 225],
   [14, 10, 18, 220], [42, 10, 18, 220]],
  [[0, 2, 18, 220], [22, -8, 24, 235], [40, 0, 20, 225],
   [16, 12, 16, 215]],
  [[0, 4, 16, 205], [18, -2, 22, 230], [38, -6, 22, 235],
   [58, -2, 20, 225], [78, 4, 14, 205], [28, 12, 16, 215]],
  [[0, 2, 22, 230], [20, -8, 26, 235], [42, 4, 18, 220]],
  [[0, -4, 26, 235], [26, 2, 22, 228], [48, -2, 18, 222],
   [12, 14, 18, 215], [36, 14, 14, 205]],
];

export function drawCloud(
  cx: CanvasRenderingContext2D,
  x: number, y: number, scale = 1.0, variant = 0,
): void {
  const puffs = CLOUD_VARIANTS[variant % CLOUD_VARIANTS.length];
  for (const [ox, oy, r, a] of puffs) {
    const rr = Math.max(2, (r * scale) | 0);
    cx.fillStyle = rgba([255, 255, 255], a);
    cx.beginPath();
    cx.arc((x + ox * scale) | 0, (y + oy * scale) | 0, rr, 0, Math.PI * 2);
    cx.fill();
  }
}

// ── Ground ─────────────────────────────────────────────────────────────────

export function drawGround(
  cx: CanvasRenderingContext2D,
  groundY: number, w: number, h: number, scroll: number,
  topColor?: Color, midColor?: Color, botColor?: Color,
): void {
  const top = topColor ?? GROUND_TOP;
  const mid = midColor ?? GROUND_MID;
  const bot = botColor ?? GROUND_BOT;
  const grassH = 22;
  for (let i = 0; i < grassH; i++) {
    const t = i / (grassH - 1);
    const c = lerpColor(top, mid, t);
    cx.fillStyle = rgb(c);
    cx.fillRect(0, groundY + i, w, 1);
  }
  for (let i = 0; i < h - groundY - grassH; i++) {
    const t = i / Math.max(1, h - groundY - grassH - 1);
    const c = lerpColor(mid, bot, t);
    cx.fillStyle = rgb(c);
    cx.fillRect(0, groundY + grassH + i, w, 1);
  }
  const blade: Color = [
    Math.min(255, top[0] + 40),
    Math.min(255, top[1] + 40),
    Math.min(255, top[2] + 40),
  ];
  const edge: Color = [
    Math.min(255, top[0] + 60),
    Math.min(255, top[1] + 60),
    Math.min(255, top[2] + 60),
  ];
  const off = ((scroll * 0.7) | 0) % 30;
  cx.strokeStyle = rgb(blade);
  cx.lineWidth = 2;
  for (let gx = -off; gx < w; gx += 30) {
    cx.beginPath();
    cx.moveTo(gx, groundY); cx.lineTo(gx - 4, groundY - 8);
    cx.moveTo(gx + 12, groundY); cx.lineTo(gx + 8, groundY - 6);
    cx.stroke();
  }
  cx.strokeStyle = rgb(edge);
  cx.lineWidth = 2;
  cx.beginPath();
  cx.moveTo(0, groundY); cx.lineTo(w - 1, groundY);
  cx.stroke();
}

// ── Stone pillar bodies (used by pillar-variants) ─────────────────────────

function shade(c: Color, d: number): Color {
  return [
    Math.max(0, Math.min(255, c[0] + d)),
    Math.max(0, Math.min(255, c[1] + d)),
    Math.max(0, Math.min(255, c[2] + d)),
  ];
}

function makeStonePillarBody(
  w: number, h: number,
  light: Color, mid: Color, dark: Color, accent: Color,
  bodySeed = 0,
): HTMLCanvasElement {
  const c = makeCanvas(w, h);
  const cx = ctx2d(c);
  for (let x = 0; x < w; x++) {
    const t = x / Math.max(1, w - 1);
    let col: Color;
    if (t < 0.18) col = lerpColor(mid, light, (0.18 - t) / 0.18);
    else if (t < 0.55) {
      const seg = (t - 0.18) / 0.37;
      col = lerpColor(light, mid, seg * seg * (3 - 2 * seg));
    } else {
      const seg = (t - 0.55) / 0.45;
      col = lerpColor(mid, dark, seg * seg * (3 - 2 * seg));
    }
    cx.fillStyle = rgb(col);
    cx.fillRect(x, 0, 1, h);
  }
  cx.fillStyle = rgba(accent, 90);
  cx.fillRect((w * 0.14) | 0, 0, 3, h);
  const rng = mulberry32(w * 7919 + h + bodySeed * 6151);
  for (let i = 0; i < 4; i++) {
    const gx = 3 + ((rng() * (w - 7)) | 0);
    cx.strokeStyle = rgb(shade(dark, -10));
    cx.lineWidth = 1;
    cx.beginPath(); cx.moveTo(gx + 0.5, 0); cx.lineTo(gx + 0.5, h - 1); cx.stroke();
  }
  const crackStep = 80;
  const ystart = 10 + ((rng() * (crackStep - 10)) | 0);
  for (let cy = ystart; cy < h - 10; cy += crackStep) {
    const jitter = ((rng() * 7) | 0) - 3;
    cx.strokeStyle = rgb(shade(dark, -20));
    cx.lineWidth = 1;
    cx.beginPath();
    cx.moveTo(2, cy + jitter + 0.5);
    cx.lineTo(w - 3, cy + jitter + ((rng() * 3) | 0) - 1 + 0.5);
    cx.stroke();
    cx.strokeStyle = rgb(light);
    cx.beginPath();
    const sx = 4 + ((rng() * (w - 9)) | 0);
    const sx2 = 4 + ((rng() * (w - 9)) | 0);
    cx.moveTo(sx, cy + jitter + 1.5);
    cx.lineTo(sx2, cy + jitter + 2.5);
    cx.stroke();
  }
  return c;
}

const _pillarBodyCache = new Map<string, HTMLCanvasElement>();

function colorKey(c: Color): string { return `${c[0]},${c[1]},${c[2]}`; }

export function getStonePillarBody(
  w: number, h: number,
  light: Color, mid: Color, dark: Color, accent: Color,
  bodySeed = 0,
): HTMLCanvasElement {
  const qh = (((h + 7) / 8) | 0) * 8;
  const bucket = bodySeed % 8;
  const key = `${w}|${qh}|${colorKey(light)}|${colorKey(mid)}|${colorKey(dark)}|${colorKey(accent)}|${bucket}`;
  let s = _pillarBodyCache.get(key);
  if (!s || s.height < h) {
    s = makeStonePillarBody(w, Math.max(qh, h), light, mid, dark, accent, bucket);
    _pillarBodyCache.set(key, s);
  }
  // Subsurface(0,0,w,h) — return source canvas; callers respect bounds via drawImage(src,sx,sy,sw,sh,...).
  return s;
}

// ── Silhouette pillar polygons ─────────────────────────────────────────────

export type Point = readonly [number, number];

export function silhouetteBottomSpire(w: number, h: number): Point[] {
  const s = w / 90.0;
  const pkR: Point = [(w / 2) | 0 + Math.max(2, (s * 12) | 0), 0];
  const pkL: Point = [(w / 2) | 0 - Math.max(2, (s * 8) | 0), 0];
  const rt: Point[] = [
    [w - Math.max(1, (s * 18) | 0), (s * 18) | 0],
    [w - Math.max(1, (s * 6) | 0), (s * 40) | 0],
    [w - Math.max(1, (s * 4) | 0), (s * 80) | 0],
    [w, (s * 130) | 0],
  ];
  const lt: Point[] = [
    [0, (s * 130) | 0],
    [Math.max(1, (s * 8) | 0), (s * 80) | 0],
    [Math.max(1, (s * 14) | 0), (s * 40) | 0],
    [Math.max(1, (s * 24) | 0), (s * 18) | 0],
  ];
  const rs = rt.filter((p) => p[1] < h);
  const ls = lt.filter((p) => p[1] < h);
  return [pkR, ...rs, [w, h] as Point, [0, h] as Point, ...ls, pkL];
}

export function silhouetteTopSpire(w: number, h: number): Point[] {
  const s = w / 90.0;
  const pkR: Point = [(w / 2) | 0 + Math.max(2, (s * 10) | 0), h];
  const pkL: Point = [(w / 2) | 0 - Math.max(2, (s * 6) | 0), h];
  const rt: Point[] = [
    [w, h - ((s * 50) | 0)],
    [w - Math.max(1, (s * 4) | 0), h - ((s * 22) | 0)],
    [w - Math.max(1, (s * 14) | 0), h - ((s * 8) | 0)],
  ];
  const lt: Point[] = [
    [Math.max(1, (s * 16) | 0), h - ((s * 8) | 0)],
    [Math.max(1, (s * 4) | 0), h - ((s * 22) | 0)],
    [0, h - ((s * 50) | 0)],
  ];
  const rs = rt.filter((p) => p[1] > 0);
  const ls = lt.filter((p) => p[1] > 0);
  return [[0, 0] as Point, [w, 0] as Point, ...rs, pkR, pkL, ...ls];
}

// silhouetteBlit: mask a stone-body surface to a polygon and blit.
// Mirrors silhouette_blit() in draw.py: shadow + masked fill + outline.
export function silhouetteBlit(
  cx: CanvasRenderingContext2D,
  body: HTMLCanvasElement, polygon: Point[], topLeft: Point,
  shadowAlpha = 110,
): void {
  const w = body.width, h = body.height;
  if (shadowAlpha > 0) {
    const sh = makeCanvas(w + 8, h + 6);
    const shx = ctx2d(sh);
    shx.fillStyle = rgba([0, 0, 0], shadowAlpha);
    shx.beginPath();
    shx.moveTo(polygon[0][0] + 4, polygon[0][1] + 3);
    for (let i = 1; i < polygon.length; i++) {
      shx.lineTo(polygon[i][0] + 4, polygon[i][1] + 3);
    }
    shx.closePath(); shx.fill();
    cx.drawImage(sh, topLeft[0] - 2, topLeft[1] + 1);
  }
  // Mask the body to the polygon via an offscreen canvas with destination-in.
  const masked = makeCanvas(w, h);
  const mx = ctx2d(masked);
  mx.drawImage(body, 0, 0, w, h, 0, 0, w, h);
  mx.globalCompositeOperation = "destination-in";
  mx.fillStyle = "rgba(255,255,255,1)";
  mx.beginPath();
  mx.moveTo(polygon[0][0], polygon[0][1]);
  for (let i = 1; i < polygon.length; i++) mx.lineTo(polygon[i][0], polygon[i][1]);
  mx.closePath(); mx.fill();
  cx.drawImage(masked, topLeft[0], topLeft[1]);
  // Dark outline.
  cx.strokeStyle = rgb([40, 28, 22]);
  cx.lineWidth = 1;
  cx.beginPath();
  cx.moveTo(polygon[0][0] + topLeft[0] + 0.5, polygon[0][1] + topLeft[1] + 0.5);
  for (let i = 1; i < polygon.length; i++) {
    cx.lineTo(polygon[i][0] + topLeft[0] + 0.5, polygon[i][1] + topLeft[1] + 0.5);
  }
  cx.closePath(); cx.stroke();
}

// ── Foliage helpers ────────────────────────────────────────────────────────

const TRUNK: Color = [60, 42, 28];

export function drawWulingPine(
  cx: CanvasRenderingContext2D,
  rootX: number, rootY: number, height: number,
  palette: Palette, lean = 0, direction: "up" | "down" = "up", layers = 5,
): void {
  const pineDk = palette.foliage_dark;
  const pineMid = palette.foliage_mid;
  const pineLt = palette.foliage_top;
  const sign = direction === "up" ? -1 : 1;
  const tipX = rootX + lean;
  const tipY = rootY + sign * height;
  cx.strokeStyle = rgb(TRUNK); cx.lineWidth = 2;
  cx.beginPath(); cx.moveTo(rootX, rootY); cx.lineTo(tipX, tipY); cx.stroke();
  for (let i = 0; i < layers; i++) {
    const t = i / Math.max(1, layers - 1);
    const layerW = Math.max(3, (height * (0.55 - t * 0.40)) | 0);
    const posT = 0.30 + t * 0.70;
    const cxn = (rootX + (tipX - rootX) * posT) | 0;
    const cyn = (rootY + (tipY - rootY) * posT) | 0;
    const offset = ((height * 0.10 * (i % 2 === 0 ? 1 : -1)) | 0);
    const drawEll = (col: Color, dx: number, dy: number, dw: number, dh: number) => {
      cx.fillStyle = rgb(col);
      cx.beginPath();
      cx.ellipse(cxn + offset + dx, cyn - 4 + dy, layerW + dw, 4 + dh, 0, 0, Math.PI * 2);
      cx.fill();
    };
    drawEll(pineDk, 0, 0, 1, 1);
    drawEll(pineMid, 0, 0, 0, 0);
    drawEll(pineLt, 0, 0, -3, -2);
  }
}

export function drawMossStrand(
  cx: CanvasRenderingContext2D,
  x: number, y: number, length: number, palette: Palette, jitterSeed = 0,
): void {
  const dark = palette.foliage_dark;
  const mid = palette.foliage_mid;
  const top = palette.foliage_top;
  const accent = palette.foliage_accent;
  for (let i = 0; i < length; i++) {
    const yy = y + i;
    const jitter = (Math.sin((i + jitterSeed) * 0.45) * 1.2) | 0;
    const col = lerpColor(dark, mid, i / Math.max(1, length));
    cx.fillStyle = rgb(col);
    cx.fillRect(x + jitter, yy, 1, 2);
  }
  const tipY = y + length;
  const bulb = Math.max(5, (length / 3) | 0);
  const half = (bulb / 2) | 0;
  const drawEll = (col: Color, dx: number, dy: number, dw: number, dh: number) => {
    cx.fillStyle = rgb(col);
    cx.beginPath();
    cx.ellipse(x - half + dx + (bulb + dw) / 2,
               tipY - half + dy + (bulb + dh) / 2,
               (bulb + dw) / 2, (bulb + dh) / 2, 0, 0, Math.PI * 2);
    cx.fill();
  };
  drawEll(dark, 0, 0, 0, 0);
  drawEll(mid, 1, 0, -2, -1);
  drawEll(top, 2, 0, Math.max(2, bulb - 5) - bulb, Math.max(2, bulb - 5) - bulb);
  cx.fillStyle = rgb(accent);
  cx.beginPath();
  cx.arc(x + 2, tipY - (bulb / 3) | 0, 2, 0, Math.PI * 2);
  cx.fill();
}

export function drawSideShrub(
  cx: CanvasRenderingContext2D,
  x: number, y: number, palette: Palette, scale = 1.0,
): void {
  const dark = palette.foliage_dark;
  const mid = palette.foliage_mid;
  const top = palette.foliage_top;
  const rw = Math.max(6, (10 * scale) | 0);
  const rh = Math.max(4, (6 * scale) | 0);
  const drawEll = (col: Color, dx: number, dy: number, dwn: number, dh: number) => {
    cx.fillStyle = rgb(col);
    cx.beginPath();
    cx.ellipse(x + dx, y + dy, rw + dwn, rh + dh, 0, 0, Math.PI * 2);
    cx.fill();
  };
  drawEll(dark, 0, 0, 0, 0);
  drawEll(mid, 1, 1, -2, -1);
  drawEll(top, 2, 0, -4, Math.max(2, rh) - rh);
}

export function drawPillarMist(
  cx: CanvasRenderingContext2D,
  centerX: number, baseY: number, width: number, alpha = 110,
): void {
  const layers: Array<[number, number, number]> = [
    [width * 4, 32, (alpha / 3) | 0],
    [width * 3, 22, (alpha / 2) | 0],
    [width * 2, 14, alpha],
  ];
  for (const [w, h, a] of layers) {
    cx.fillStyle = rgba([255, 255, 255], a);
    cx.beginPath();
    cx.ellipse(centerX, baseY + 4, w / 2, h / 2, 0, 0, Math.PI * 2);
    cx.fill();
  }
}
