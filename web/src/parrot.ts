// Procedural scarlet macaw — base frames + parcel + KFC variant + stubbed
// cosmetic variants (ghost / hat / grow / combos) that recolour the base
// frames. Faithful gameplay, with cosmetic variant polish deferred.
//
// Ported from game/parrot.py.

import {
  BIRD_RED, BIRD_RED_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
  BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D, WHITE,
  rgb, rgba, makeCanvas, ctx2d, lerpColorMulti,
} from "./draw.js";
import { lerpColor, type Color } from "./biome.js";

export const SPRITE_W = 64;
export const SPRITE_H = 60;

const SHADE_BLACK: Color = [15, 15, 25];
const SHADE_FRAME: Color = [255, 200, 50];
const SHADE_GLINT: Color = [255, 255, 255];
const SHADE_TINT: Color  = [35, 55, 90];

function aaEllipse(cx: CanvasRenderingContext2D, color: Color, x: number, y: number, rx: number, ry: number, alpha = 1): void {
  cx.fillStyle = alpha >= 1 ? rgb(color) : rgba(color, Math.round(alpha * 255));
  cx.beginPath();
  cx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
  cx.fill();
}

function ellipseRgba(cx: CanvasRenderingContext2D, c: Color, a: number, x: number, y: number, rx: number, ry: number): void {
  cx.fillStyle = rgba(c, a);
  cx.beginPath();
  cx.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2);
  cx.fill();
}

function polyFill(cx: CanvasRenderingContext2D, pts: Array<readonly [number, number]>, color: Color, alpha = 1): void {
  cx.fillStyle = alpha >= 1 ? rgb(color) : rgba(color, Math.round(alpha * 255));
  cx.beginPath();
  cx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) cx.lineTo(pts[i][0], pts[i][1]);
  cx.closePath();
  cx.fill();
}

function polyStroke(cx: CanvasRenderingContext2D, pts: Array<readonly [number, number]>, color: Color, w = 1): void {
  cx.strokeStyle = rgb(color); cx.lineWidth = w;
  cx.beginPath();
  cx.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) cx.lineTo(pts[i][0], pts[i][1]);
  cx.closePath();
  cx.stroke();
}

function lineRgb(cx: CanvasRenderingContext2D, c: Color, x1: number, y1: number, x2: number, y2: number, w = 1): void {
  cx.strokeStyle = rgb(c); cx.lineWidth = w;
  cx.beginPath(); cx.moveTo(x1 + 0.5, y1 + 0.5); cx.lineTo(x2 + 0.5, y2 + 0.5); cx.stroke();
}

// ── Wing builder ──────────────────────────────────────────────────────────

function buildWing(angleDeg: number): HTMLCanvasElement {
  const w = makeCanvas(50, 50);
  const cx = ctx2d(w);
  polyFill(cx, [[24, 26], [46, 14], [50, 30], [34, 44], [18, 40]], [0, 0, 0], 110 / 255);
  polyFill(cx, [[24, 24], [44, 13], [48, 28], [32, 42], [18, 36]], BIRD_WING);
  polyFill(cx, [[24, 24], [32, 42], [18, 36]], BIRD_WING_D);
  polyFill(cx, [[44, 13], [50, 18], [48, 28]], BIRD_TIP);
  polyFill(cx, [[42, 18], [48, 22], [46, 28], [40, 24]], [255, 200, 60]);
  lineRgb(cx, BIRD_WING_D, 26, 25, 42, 18, 2);
  lineRgb(cx, BIRD_WING_D, 28, 30, 44, 25, 2);
  lineRgb(cx, BIRD_WING_D, 30, 34, 46, 32, 2);
  lineRgb(cx, [170, 210, 255], 25, 25, 41, 15, 1);
  return rotate(w, angleDeg);
}

// ── Sunglasses ────────────────────────────────────────────────────────────

function drawSunglasses(cx: CanvasRenderingContext2D, cxn: number, cyn: number): void {
  const rOuter = 6;
  const left:  readonly [number, number] = [cxn - 4, cyn];
  const right: readonly [number, number] = [cxn + 6, cyn - 1];
  cx.fillStyle = rgb(SHADE_FRAME);
  cx.beginPath(); cx.arc(left[0], left[1], rOuter + 1, 0, Math.PI * 2); cx.fill();
  cx.beginPath(); cx.arc(right[0], right[1], rOuter + 1, 0, Math.PI * 2); cx.fill();
  cx.fillStyle = rgb(SHADE_BLACK);
  cx.beginPath(); cx.arc(left[0], left[1], rOuter, 0, Math.PI * 2); cx.fill();
  cx.beginPath(); cx.arc(right[0], right[1], rOuter, 0, Math.PI * 2); cx.fill();
  // Sky-blue lens tint.
  ellipseRgba(cx, SHADE_TINT, 130, left[0],  left[1] + 0.5, rOuter, rOuter / 2);
  ellipseRgba(cx, SHADE_TINT, 130, right[0], right[1] + 0.5, rOuter, rOuter / 2);
  cx.fillStyle = rgb(SHADE_GLINT);
  cx.beginPath(); cx.arc(left[0]  - 2, left[1]  - 2, 2, 0, Math.PI * 2); cx.fill();
  cx.beginPath(); cx.arc(right[0] - 2, right[1] - 3, 2, 0, Math.PI * 2); cx.fill();
  cx.fillStyle = rgba([255, 255, 255], 200);
  cx.beginPath(); cx.arc(left[0]  + 2, left[1]  + 2, 1, 0, Math.PI * 2); cx.fill();
  cx.beginPath(); cx.arc(right[0] + 2, right[1] + 1, 1, 0, Math.PI * 2); cx.fill();
  // Nose bridge + brow line.
  lineRgb(cx, SHADE_FRAME, left[0]  + rOuter, left[1],  right[0] - rOuter, right[1], 2);
  lineRgb(cx, SHADE_FRAME, left[0]  - rOuter + 1, left[1]  - rOuter + 2,
                            right[0] + rOuter - 1, right[1] - rOuter + 2, 1);
}

// ── Frame builder ─────────────────────────────────────────────────────────

function buildFrame(wingAngleDeg: number): HTMLCanvasElement {
  const c = makeCanvas(SPRITE_W, SPRITE_H);
  const cx = ctx2d(c);
  // Tail.
  const tailColors: Color[] = [[200, 30, 40], [240, 95, 40], [255, 160, 55], [255, 220, 80]];
  tailColors.forEach((col, i) => {
    polyFill(cx, [
      [2 + i * 3, 26 + i * 2], [14 + i, 24 + i],
      [20 + i, 30 + i * 2], [6 + i * 3, 36 + i * 2],
    ], col);
  });
  lineRgb(cx, BIRD_RED_D, 4, 27, 18, 31, 1);
  lineRgb(cx, BIRD_RED_D, 6, 33, 20, 35, 1);
  // Body.
  aaEllipse(cx, [120, 20, 25], 34, 35, 19, 14);
  aaEllipse(cx, BIRD_RED, 32, 32, 19, 14);
  aaEllipse(cx, [255, 100, 100], 30, 29, 13, 8);
  aaEllipse(cx, BIRD_BELLY, 28, 38, 12, 6);
  ellipseRgba(cx, [255, 230, 230], 160, 22 + 14, 21 + 3, 14, 3);
  // Wing.
  const wing = buildWing(wingAngleDeg);
  cx.drawImage(wing, 34 - wing.width / 2, 28 - wing.height / 2);
  // Head.
  aaEllipse(cx, [150, 15, 20], 48, 23, 12, 11);
  aaEllipse(cx, BIRD_RED, 47, 21, 12, 11);
  aaEllipse(cx, [255, 130, 130], 44, 24, 4, 3);
  aaEllipse(cx, [255, 170, 170], 46, 16, 7, 3);
  drawSunglasses(cx, 50, 20);
  // Beak.
  const beak: Array<[number, number]> = [[55, 21], [61, 24], [58, 28], [52, 26]];
  polyFill(cx, beak, BIRD_BEAK);
  polyStroke(cx, beak, BIRD_BEAK_D, 1);
  lineRgb(cx, [255, 230, 150], 55, 22, 59, 24, 1);
  lineRgb(cx, BIRD_BEAK_D, 52, 24, 58, 25, 1);
  // Feet.
  lineRgb(cx, BIRD_BEAK_D, 28, 45, 26, 49, 2);
  lineRgb(cx, BIRD_BEAK_D, 34, 45, 36, 49, 2);
  return c;
}

// ── Outline ───────────────────────────────────────────────────────────────
// Mirrors `_add_outline` in parrot.py: render an alpha-only silhouette
// in `outline_color`, blit at 8 neighbour offsets to grow it 1 px, then
// stamp the original sprite on top.

function addOutline(src: HTMLCanvasElement, outline: Color = [20, 12, 18], alpha255 = 220): HTMLCanvasElement {
  const pad = 2;
  const w = src.width, h = src.height;
  const out = makeCanvas(w + pad * 2, h + pad * 2);
  const ox = ctx2d(out);

  // Build the silhouette: source canvas filled with outline colour, masked by source alpha.
  const sil = makeCanvas(w, h);
  const sx = ctx2d(sil);
  sx.drawImage(src, 0, 0);
  sx.globalCompositeOperation = "source-in";
  sx.fillStyle = rgba(outline, alpha255);
  sx.fillRect(0, 0, w, h);

  for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1],
                           [-1, -1], [1, -1], [-1, 1], [1, 1]] as const) {
    ox.drawImage(sil, pad + dx, pad + dy);
  }
  ox.drawImage(src, pad, pad);
  return out;
}

// ── Rotation ──────────────────────────────────────────────────────────────

function rotate(src: HTMLCanvasElement, angleDeg: number): HTMLCanvasElement {
  if (angleDeg === 0) return src;
  const rad = (angleDeg * Math.PI) / 180;
  const sw = src.width, sh = src.height;
  const cos = Math.abs(Math.cos(rad)), sin = Math.abs(Math.sin(rad));
  const nw = Math.ceil(sw * cos + sh * sin);
  const nh = Math.ceil(sw * sin + sh * cos);
  const out = makeCanvas(nw, nh);
  const ox = ctx2d(out);
  ox.translate(nw / 2, nh / 2);
  ox.rotate(-rad);  // pygame rotates counter-clockwise
  ox.drawImage(src, -sw / 2, -sh / 2);
  return out;
}

// ── Public sprite caches ──────────────────────────────────────────────────

const WING_ANGLES = [50, 20, -10, -40] as const;

// Eager, cheap (~4 ms native): the menu/intro/gameplay all need these.
export const FRAMES: HTMLCanvasElement[] = WING_ANGLES.map((a) => addOutline(buildFrame(a)));

const _rotCache = new Map<number, HTMLCanvasElement>();

function rotKey(frame: number, tilt: number): number {
  const bucket = Math.round(tilt / 3.0) * 3;
  // Encode (frame, bucket) into a single integer (bucket can be negative).
  return frame * 100000 + (bucket + 50000);
}

export function getParrot(frameIdx: number, tiltDeg: number): HTMLCanvasElement {
  const idx = ((frameIdx % FRAMES.length) + FRAMES.length) % FRAMES.length;
  const bucket = Math.round(tiltDeg / 3.0) * 3;
  const key = rotKey(idx, bucket);
  let s = _rotCache.get(key);
  if (!s) {
    s = rotate(FRAMES[idx], bucket);
    _rotCache.set(key, s);
  }
  return s;
}

// ── KFC variant (built lazily on first use) ───────────────────────────────

const CRISPY_GOLD: Color = [210, 138, 42];
const CRISPY_DARK: Color = [148, 82, 18];
const CRISPY_LIGHT: Color = [238, 178, 72];
const CRISPY_SPOT: Color = [125, 68, 12];

function buildFriedWing(angleDeg: number): HTMLCanvasElement {
  const w = makeCanvas(62, 62);
  const cx = ctx2d(w);
  polyFill(cx, [[22, 28], [52, 10], [58, 32], [40, 50], [16, 44]], [0, 0, 0], 120 / 255);
  polyFill(cx, [[22, 26], [50, 9], [56, 30], [38, 48], [16, 42]], CRISPY_DARK);
  polyFill(cx, [[22, 24], [48, 8], [54, 28], [36, 46], [16, 40]], CRISPY_GOLD);
  polyFill(cx, [[22, 24], [36, 46], [16, 40]], CRISPY_DARK);
  aaEllipse(cx, CRISPY_LIGHT, 38, 22, 12, 6);
  for (const [px, py, pr] of [[40, 14, 3], [50, 20, 3], [44, 28, 3],
                              [30, 18, 2], [54, 28, 2], [34, 36, 2], [46, 34, 2]] as const) {
    cx.fillStyle = rgb(CRISPY_SPOT);
    cx.beginPath(); cx.arc(px, py, pr, 0, Math.PI * 2); cx.fill();
  }
  lineRgb(cx, CRISPY_DARK,  25, 27, 47, 15, 2);
  lineRgb(cx, CRISPY_DARK,  28, 34, 50, 24, 2);
  lineRgb(cx, CRISPY_DARK,  30, 40, 52, 32, 1);
  lineRgb(cx, CRISPY_LIGHT, 24, 25, 46, 13, 1);
  lineRgb(cx, CRISPY_LIGHT, 27, 32, 49, 22, 1);
  return rotate(w, angleDeg);
}

function buildFriedFrame(wingAngleDeg: number): HTMLCanvasElement {
  const c = makeCanvas(SPRITE_W, SPRITE_H);
  const cx = ctx2d(c);
  const tail: Color[] = [[148, 82, 18], [178, 108, 28], [208, 138, 42], [228, 162, 58]];
  tail.forEach((col, i) => {
    polyFill(cx, [
      [2 + i * 3, 26 + i * 2], [14 + i, 24 + i],
      [20 + i, 30 + i * 2], [6 + i * 3, 36 + i * 2],
    ], col);
  });
  lineRgb(cx, CRISPY_DARK, 4, 27, 18, 31, 1);
  lineRgb(cx, CRISPY_DARK, 6, 33, 20, 35, 1);
  aaEllipse(cx, [85, 44, 5], 34, 36, 23, 17);
  aaEllipse(cx, CRISPY_DARK, 33, 35, 22, 16);
  aaEllipse(cx, CRISPY_GOLD, 32, 33, 21, 15);
  aaEllipse(cx, CRISPY_LIGHT, 29, 28, 15, 10);
  aaEllipse(cx, [242, 190, 80], 27, 39, 14, 8);
  aaEllipse(cx, CRISPY_DARK, 32, 45, 18, 5);
  for (const [px, py, pr] of [[20, 30, 3], [37, 27, 3], [43, 35, 3],
                              [24, 39, 2], [38, 39, 2], [28, 34, 2],
                              [32, 26, 2], [44, 30, 2], [16, 37, 2],
                              [34, 42, 2], [40, 24, 1], [22, 43, 1]] as const) {
    cx.fillStyle = rgb(CRISPY_SPOT);
    cx.beginPath(); cx.arc(px, py, pr, 0, Math.PI * 2); cx.fill();
  }
  for (const [x1, y1, x2, y2] of [[14, 30, 23, 25], [37, 25, 47, 30],
                                  [15, 39, 25, 44], [40, 38, 50, 33],
                                  [22, 34, 31, 29], [34, 39, 43, 36]] as const) {
    lineRgb(cx, CRISPY_DARK, x1, y1, x2, y2, 1);
    lineRgb(cx, CRISPY_LIGHT, x1 - 1, y1 - 1, x2 - 1, y2 - 1, 1);
  }
  ellipseRgba(cx, [255, 225, 145], 130, 17 + 15, 20 + 3.5, 15, 3.5);
  const wing = buildFriedWing(wingAngleDeg);
  cx.drawImage(wing, 32 - wing.width / 2, 24 - wing.height / 2);
  aaEllipse(cx, [95, 50, 6], 49, 23, 13, 12);
  aaEllipse(cx, CRISPY_GOLD, 48, 21, 13, 12);
  aaEllipse(cx, CRISPY_LIGHT, 45, 24, 5, 4);
  aaEllipse(cx, [232, 172, 68], 47, 15, 8, 4);
  for (const [px, py, pr] of [[52, 18, 2], [45, 22, 2], [51, 25, 1]] as const) {
    cx.fillStyle = rgb(CRISPY_SPOT);
    cx.beginPath(); cx.arc(px, py, pr, 0, Math.PI * 2); cx.fill();
  }
  cx.fillStyle = rgb(WHITE);
  cx.beginPath(); cx.arc(51, 20, 4, 0, Math.PI * 2); cx.fill();
  cx.fillStyle = rgb([15, 15, 25]);
  cx.beginPath(); cx.arc(52, 20, 2, 0, Math.PI * 2); cx.fill();
  cx.fillStyle = rgb(WHITE);
  cx.beginPath(); cx.arc(53, 18, 1, 0, Math.PI * 2); cx.fill();
  const beak: Array<[number, number]> = [[55, 21], [61, 24], [58, 28], [52, 26]];
  polyFill(cx, beak, BIRD_BEAK);
  polyStroke(cx, beak, BIRD_BEAK_D, 1);
  lineRgb(cx, [255, 230, 150], 55, 22, 59, 24, 1);
  lineRgb(cx, BIRD_BEAK_D, 52, 24, 58, 25, 1);
  for (const [lx, ly, ex, ey] of [[28, 44, 24, 51], [34, 44, 38, 51]] as const) {
    lineRgb(cx, CRISPY_DARK, lx, ly, ex, ey, 3);
    cx.fillStyle = rgb(CRISPY_GOLD);
    cx.beginPath(); cx.arc(ex, ey, 3, 0, Math.PI * 2); cx.fill();
    cx.strokeStyle = rgb(CRISPY_DARK); cx.lineWidth = 1;
    cx.beginPath(); cx.arc(ex, ey, 3, 0, Math.PI * 2); cx.stroke();
  }
  return c;
}

let _kfcFrames: HTMLCanvasElement[] | null = null;
const _kfcRotCache = new Map<number, HTMLCanvasElement>();

function ensureKfc(): HTMLCanvasElement[] {
  if (!_kfcFrames) _kfcFrames = WING_ANGLES.map((a) => addOutline(buildFriedFrame(a)));
  return _kfcFrames;
}

export function getFriedParrot(frameIdx: number, tiltDeg: number): HTMLCanvasElement {
  const frames = ensureKfc();
  const idx = ((frameIdx % frames.length) + frames.length) % frames.length;
  const bucket = Math.round(tiltDeg / 3.0) * 3;
  const key = rotKey(idx, bucket);
  let s = _kfcRotCache.get(key);
  if (!s) {
    s = rotate(frames[idx], bucket);
    _kfcRotCache.set(key, s);
  }
  return s;
}

// ── Cosmetic variants (recolour fallback) ─────────────────────────────────
// Ghost / hat / grow / combos in the Python build are full hand-drawn
// procedural sprites built by the dollar_parrot_* modules. For the TS port,
// we ship simpler recoloured fallbacks now and refine in follow-ups —
// gameplay is identical, only cosmetic polish shifts.

function tintedClone(src: HTMLCanvasElement, tint: Color, strength = 0.5): HTMLCanvasElement {
  const c = makeCanvas(src.width, src.height);
  const cx = ctx2d(c);
  cx.drawImage(src, 0, 0);
  cx.globalCompositeOperation = "source-atop";
  cx.fillStyle = rgba(tint, Math.round(255 * strength));
  cx.fillRect(0, 0, c.width, c.height);
  return c;
}

function scaledClone(src: HTMLCanvasElement, factor: number): HTMLCanvasElement {
  const w = Math.max(2, Math.round(src.width * factor));
  const h = Math.max(2, Math.round(src.height * factor));
  const c = makeCanvas(w, h);
  const cx = ctx2d(c);
  cx.imageSmoothingEnabled = true;
  cx.imageSmoothingQuality = "high";
  cx.drawImage(src, 0, 0, w, h);
  return c;
}

const _ghostCache = new Map<number, HTMLCanvasElement>();
const _hatCache = new Map<number, HTMLCanvasElement>();
const _growCache = new Map<number, HTMLCanvasElement>();
const _kfcHatCache = new Map<number, HTMLCanvasElement>();
const _ghostHatCache = new Map<number, HTMLCanvasElement>();
const _kfcGhostCache = new Map<number, HTMLCanvasElement>();
const _kfcGhostHatCache = new Map<number, HTMLCanvasElement>();

function makeVariant(
  base: HTMLCanvasElement, tint: Color, strength: number, addHat: boolean,
): HTMLCanvasElement {
  let s = tintedClone(base, tint, strength);
  if (addHat) {
    // Tiny stovepipe hat above the head.
    const hw = s.width;
    const c = makeCanvas(hw, s.height + 8);
    const cx = ctx2d(c);
    cx.drawImage(s, 0, 8);
    // Hat geometry approx — black rectangle + brim.
    cx.fillStyle = rgb([20, 18, 30]);
    cx.fillRect((hw / 2) - 6, 2, 12, 8);
    cx.fillRect((hw / 2) - 9, 9, 18, 2);
    cx.strokeStyle = rgb([240, 192, 64]); cx.lineWidth = 1;
    cx.beginPath(); cx.moveTo((hw / 2) - 6, 9); cx.lineTo((hw / 2) + 6, 9); cx.stroke();
    s = c;
  }
  return s;
}

function variantGet(
  cache: Map<number, HTMLCanvasElement>, base: (frame: number) => HTMLCanvasElement,
  tint: Color, strength: number, addHat: boolean,
  frameIdx: number, tiltDeg: number,
): HTMLCanvasElement {
  const idx = ((frameIdx % FRAMES.length) + FRAMES.length) % FRAMES.length;
  const bucket = Math.round(tiltDeg / 3.0) * 3;
  const key = rotKey(idx, bucket);
  let s = cache.get(key);
  if (!s) {
    s = rotate(makeVariant(base(idx), tint, strength, addHat), bucket);
    cache.set(key, s);
  }
  return s;
}

export function getGhostParrot(frame: number, tilt: number): HTMLCanvasElement {
  return variantGet(_ghostCache, (i) => FRAMES[i], [170, 230, 255], 0.55, false, frame, tilt);
}

export function getHatParrot(frame: number, tilt: number): HTMLCanvasElement {
  return variantGet(_hatCache, (i) => FRAMES[i], [240, 192, 64], 0.0, true, frame, tilt);
}

export function getGrowParrot(frame: number, tilt: number): HTMLCanvasElement {
  // Larger version of the base bird; rotation cache keys on tilt.
  const idx = ((frame % FRAMES.length) + FRAMES.length) % FRAMES.length;
  const bucket = Math.round(tilt / 3.0) * 3;
  const key = rotKey(idx, bucket);
  let s = _growCache.get(key);
  if (!s) {
    s = rotate(scaledClone(FRAMES[idx], 1.5), bucket);
    _growCache.set(key, s);
  }
  return s;
}

export function getKfcHatParrot(frame: number, tilt: number): HTMLCanvasElement {
  const frames = ensureKfc();
  return variantGet(_kfcHatCache, (i) => frames[i], [240, 192, 64], 0.0, true, frame, tilt);
}

export function getGhostHatParrot(frame: number, tilt: number): HTMLCanvasElement {
  return variantGet(_ghostHatCache, (i) => FRAMES[i], [170, 230, 255], 0.55, true, frame, tilt);
}

export function getKfcGhostParrot(frame: number, tilt: number): HTMLCanvasElement {
  const frames = ensureKfc();
  return variantGet(_kfcGhostCache, (i) => frames[i], [170, 230, 255], 0.55, false, frame, tilt);
}

export function getKfcGhostHatParrot(frame: number, tilt: number): HTMLCanvasElement {
  const frames = ensureKfc();
  return variantGet(_kfcGhostHatCache, (i) => frames[i], [170, 230, 255], 0.55, true, frame, tilt);
}

// ── Parcel sprite (4 visual modes) ────────────────────────────────────────

export const PARCEL_SIZE = 22;

export type ParcelMode = "normal" | "kfc" | "ghost" | "triple";

interface ParcelPalette {
  BOX_BASE: Color; BOX_SHADE: Color; BOX_HI: Color;
  RIBBON: Color; RIBBON_HI: Color;
  BOW_FILL: Color; BOW_HI: Color;
  OUTLINE: Color;
}

const PARCEL_PALETTES: Record<ParcelMode, ParcelPalette> = {
  normal: {
    BOX_BASE: [180, 130, 80], BOX_SHADE: [110, 75, 40], BOX_HI: [220, 175, 120],
    RIBBON: [200, 50, 60], RIBBON_HI: [255, 110, 100],
    BOW_FILL: [200, 50, 60], BOW_HI: [255, 130, 120],
    OUTLINE: [26, 10, 12],
  },
  kfc: {
    BOX_BASE: [210, 138, 42], BOX_SHADE: [148, 82, 18], BOX_HI: [238, 178, 72],
    RIBBON: [110, 46, 22], RIBBON_HI: [180, 100, 52],
    BOW_FILL: [110, 46, 22], BOW_HI: [180, 100, 52],
    OUTLINE: [60, 32, 16],
  },
  ghost: {
    BOX_BASE: [140, 200, 230], BOX_SHADE: [88, 150, 190], BOX_HI: [200, 235, 250],
    RIBBON: [110, 170, 210], RIBBON_HI: [180, 225, 250],
    BOW_FILL: [110, 170, 210], BOW_HI: [180, 225, 250],
    OUTLINE: [40, 90, 140],
  },
  triple: {
    BOX_BASE: [180, 130, 80], BOX_SHADE: [110, 75, 40], BOX_HI: [220, 175, 120],
    RIBBON: [210, 170, 60], RIBBON_HI: [255, 225, 140],
    BOW_FILL: [210, 170, 60], BOW_HI: [255, 225, 140],
    OUTLINE: [50, 32, 12],
  },
};

function buildParcelVariant(p: ParcelPalette): HTMLCanvasElement {
  const SIZE = 56;
  const c = makeCanvas(SIZE, SIZE);
  const cx = ctx2d(c);
  const BOX_W = 40, BOX_H = 34;
  const cxn = SIZE / 2, cyn = SIZE / 2 + 2;
  const rect = { x: cxn - BOX_W / 2, y: cyn - BOX_H / 2 + 2, w: BOX_W, h: BOX_H };
  // Drop shadow.
  ellipseRgba(cx, [8, 4, 22], 130, cxn, rect.y + rect.h - 4 + 5, (BOX_W + 8) / 2, 5);
  // Outline frame.
  cx.fillStyle = rgb(p.OUTLINE);
  cx.beginPath();
  const ow = rect.w + 4, oh = rect.h + 4;
  const ox = rect.x - 2, oy = rect.y - 2;
  const r1 = 8;
  cx.moveTo(ox + r1, oy);
  cx.arcTo(ox + ow, oy, ox + ow, oy + oh, r1);
  cx.arcTo(ox + ow, oy + oh, ox, oy + oh, r1);
  cx.arcTo(ox, oy + oh, ox, oy, r1);
  cx.arcTo(ox, oy, ox + ow, oy, r1);
  cx.closePath(); cx.fill();
  // Body — vertical gradient inside the rounded rect.
  const body = makeCanvas(rect.w, rect.h);
  const bx = ctx2d(body);
  const grad = bx.createLinearGradient(0, 0, 0, rect.h);
  grad.addColorStop(0, rgb(p.BOX_BASE));
  grad.addColorStop(1, rgb(p.BOX_SHADE));
  bx.fillStyle = grad; bx.fillRect(0, 0, rect.w, rect.h);
  // Round-corner clip via destination-in.
  bx.globalCompositeOperation = "destination-in";
  bx.fillStyle = "#fff";
  bx.beginPath();
  const r2 = 6;
  bx.moveTo(r2, 0);
  bx.arcTo(rect.w, 0, rect.w, rect.h, r2);
  bx.arcTo(rect.w, rect.h, 0, rect.h, r2);
  bx.arcTo(0, rect.h, 0, 0, r2);
  bx.arcTo(0, 0, rect.w, 0, r2);
  bx.closePath(); bx.fill();
  cx.drawImage(body, rect.x, rect.y);
  // Top sheen.
  lineRgb(cx, p.BOX_HI, rect.x + 4, rect.y + 3, rect.x + rect.w - 5, rect.y + 3, 2);
  // Vertical ribbon.
  const rvW = 6;
  const rvx = rect.x + rect.w / 2 - rvW / 2;
  cx.fillStyle = rgb(p.RIBBON);
  cx.fillRect(rvx, rect.y, rvW, rect.h);
  lineRgb(cx, p.RIBBON_HI, rvx + 1, rect.y, rvx + 1, rect.y + rect.h - 1, 1);
  // Horizontal ribbon.
  const rhW = 6;
  const rhy = rect.y + rect.h / 2 - rhW / 2;
  cx.fillStyle = rgb(p.RIBBON);
  cx.fillRect(rect.x, rhy, rect.w, rhW);
  lineRgb(cx, p.RIBBON_HI, rect.x, rhy + 1, rect.x + rect.w - 1, rhy + 1, 1);
  // Bow.
  const bxn = cxn, byn = rect.y - 6;
  const drawEll = (col: Color, x: number, y: number, w: number, h: number) => {
    cx.fillStyle = rgb(col);
    cx.beginPath(); cx.ellipse(x + w / 2, y + h / 2, w / 2, h / 2, 0, 0, Math.PI * 2); cx.fill();
  };
  drawEll(p.OUTLINE, bxn - 13, byn - 6, 13, 12);
  drawEll(p.BOW_FILL, bxn - 12, byn - 5, 11, 10);
  drawEll(p.OUTLINE, bxn, byn - 6, 13, 12);
  drawEll(p.BOW_FILL, bxn + 1, byn - 5, 11, 10);
  drawEll(p.BOW_HI, bxn - 10, byn - 4, 4, 3);
  drawEll(p.BOW_HI, bxn + 6, byn - 4, 4, 3);
  cx.fillStyle = rgb(p.OUTLINE); cx.fillRect(bxn - 4, byn - 6, 9, 12);
  cx.fillStyle = rgb(p.BOW_FILL); cx.fillRect(bxn - 3, byn - 5, 7, 10);
  lineRgb(cx, p.BOW_HI, bxn - 1, byn - 4, bxn - 1, byn + 3, 1);
  lineRgb(cx, p.OUTLINE, bxn - 2, byn + 4, bxn - 7, byn + 11, 4);
  lineRgb(cx, p.OUTLINE, bxn + 2, byn + 4, bxn + 7, byn + 11, 4);
  lineRgb(cx, p.BOW_FILL, bxn - 2, byn + 4, bxn - 6, byn + 10, 2);
  lineRgb(cx, p.BOW_FILL, bxn + 2, byn + 4, bxn + 6, byn + 10, 2);
  // Smoothscale-down to PARCEL_SIZE.
  const out = makeCanvas(PARCEL_SIZE, PARCEL_SIZE);
  const ox2 = ctx2d(out);
  ox2.imageSmoothingEnabled = true;
  ox2.imageSmoothingQuality = "high";
  ox2.drawImage(c, 0, 0, PARCEL_SIZE, PARCEL_SIZE);
  return out;
}

const _PARCELS: Record<ParcelMode, HTMLCanvasElement> = {
  normal: buildParcelVariant(PARCEL_PALETTES.normal),
  kfc: buildParcelVariant(PARCEL_PALETTES.kfc),
  ghost: buildParcelVariant(PARCEL_PALETTES.ghost),
  triple: buildParcelVariant(PARCEL_PALETTES.triple),
};

export function getParcel(mode: ParcelMode = "normal"): HTMLCanvasElement {
  return _PARCELS[mode] ?? _PARCELS.normal;
}

// Suppress unused-import warning for lerpColor / lerpColorMulti when this
// file is built in strict mode but those helpers aren't yet referenced.
// (They're imported for parity with the Python module and may be used by
// future variant work.)
void lerpColor; void lerpColorMulti;
