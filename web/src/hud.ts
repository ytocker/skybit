// HUD: score, hi-score, coin count, power-up timers, pause button,
// menu / pause / stats / leaderboard / game-over overlays.
//
// Functional parity with game/hud.py — visual polish (pulse rings on
// low-time bars, magic-card backgrounds for stats, etc.) iterates later.

import { W, H } from "./config.js";
import {
  rgb, rgba, roundedRectGrad,
  WHITE, NEAR_BLACK,
} from "./draw.js";
import type { World } from "./world.js";
import type { ScoreRow } from "./leaderboard.js";

const GOLD_BRIGHT: readonly [number, number, number] = [240, 192, 64];
const GOLD_MUTED: readonly [number, number, number] = [216, 184, 85];
const RED_OUTLINE: readonly [number, number, number] = [168, 32, 16];
const ORANGE_BORDER: readonly [number, number, number] = [232, 104, 40];
const BTN_TOP: readonly [number, number, number] = [200, 64, 24];
const BTN_BOT: readonly [number, number, number] = [126, 28, 2];
const PANEL_DARK: readonly [number, number, number] = [12, 8, 38];

function fontStr(size: number, bold = true): string {
  return `${bold ? "900" : "400"} ${size}px LiberationSans, Arial`;
}

function outlinedText(
  cx: CanvasRenderingContext2D, txt: string, x: number, y: number, size: number,
  fill: readonly [number, number, number] = GOLD_BRIGHT,
  outline: readonly [number, number, number] = RED_OUTLINE,
  px = 3,
): void {
  cx.font = fontStr(size, true);
  cx.textAlign = "center";
  cx.textBaseline = "middle";
  cx.fillStyle = rgb(outline);
  for (const [ox, oy] of [[-px, 0], [px, 0], [0, -px], [0, px],
                          [-px, -px], [px, -px], [-px, px], [px, px]] as const) {
    cx.fillText(txt, x + ox, y + oy);
  }
  cx.fillStyle = rgba(NEAR_BLACK, 170);
  cx.fillText(txt, x + 3, y + 5);
  cx.fillStyle = rgb(fill);
  cx.fillText(txt, x, y);
}

function pillBtn(
  cx: CanvasRenderingContext2D, x: number, y: number, label: string, size = 20,
  alpha = 1, minWidth?: number,
): { x: number; y: number; w: number; h: number } {
  cx.font = fontStr(size, true);
  const tw = cx.measureText(label).width;
  const padX = 44;
  const w = Math.max(tw + padX, minWidth ?? 0);
  const h = size + 22;
  cx.save();
  cx.globalAlpha = alpha;
  roundedRectGrad(cx, x - w / 2, y - h / 2, w, h, h / 2, BTN_TOP, BTN_BOT);
  cx.lineWidth = 2;
  cx.strokeStyle = rgb(ORANGE_BORDER);
  cx.beginPath();
  cx.moveTo(x - w / 2 + h / 2, y - h / 2);
  cx.arc(x + w / 2 - h / 2, y, h / 2, -Math.PI / 2, Math.PI / 2);
  cx.lineTo(x - w / 2 + h / 2, y + h / 2);
  cx.arc(x - w / 2 + h / 2, y, h / 2, Math.PI / 2, -Math.PI / 2);
  cx.closePath();
  cx.stroke();
  cx.fillStyle = rgb(WHITE);
  cx.font = fontStr(size, true);
  cx.textAlign = "center";
  cx.textBaseline = "middle";
  cx.fillText(label, x, y + 1);
  cx.restore();
  return { x: x - w / 2, y: y - h / 2, w, h };
}

export class HUD {
  titleT = 0;
  pauseBtn = { x: W - 30, y: 30, r: 22 };

  drawMenu(cx: CanvasRenderingContext2D, dt: number, best: number): void {
    this.titleT += dt;
    cx.save();
    const dim = makeRgba(0, 0, 0, 80);
    cx.fillStyle = dim; cx.fillRect(0, 0, W, H);
    const cy = H * 0.32;
    outlinedText(cx, "SKYBIT", W / 2, cy, 64);
    cx.font = fontStr(11, true);
    cx.fillStyle = rgba(GOLD_MUTED, 220);
    cx.textAlign = "center";
    cx.fillText("POCKET SKY FLYER", W / 2, cy + 38);
    pillBtn(cx, W / 2, H * 0.62, "TAP TO PLAY", 18, 1);
    if (best > 0) {
      cx.font = fontStr(12, true);
      cx.fillStyle = rgba(GOLD_MUTED, 200);
      cx.fillText(`BEST  ${best}`, W / 2, H * 0.74);
    }
    cx.restore();
  }

  drawPlay(cx: CanvasRenderingContext2D, world: World, best: number, paused = false): void {
    void paused;
    // Score pill in centre top.
    const score = String(world.score);
    cx.save();
    cx.fillStyle = rgba([0, 0, 0], 110);
    cx.beginPath();
    cx.ellipse(W / 2, 36, 50, 22, 0, 0, Math.PI * 2);
    cx.fill();
    outlinedText(cx, score, W / 2, 36, 30);
    // Best.
    if (best > 0) {
      cx.font = fontStr(11, true);
      cx.fillStyle = rgba([255, 230, 150], 220);
      cx.textAlign = "left"; cx.textBaseline = "middle";
      cx.fillText(`BEST ${best}`, 12, 24);
    }
    // Coins.
    cx.font = fontStr(11, true);
    cx.fillStyle = rgba([255, 230, 150], 220);
    cx.textAlign = "right"; cx.textBaseline = "middle";
    cx.fillText(`◯ ${world.coinCount}`, W - 12, 24);
    // Pause button.
    cx.fillStyle = rgba([0, 0, 0], 110);
    cx.beginPath(); cx.arc(this.pauseBtn.x, this.pauseBtn.y, this.pauseBtn.r, 0, Math.PI * 2); cx.fill();
    cx.fillStyle = rgb([240, 192, 64]);
    cx.fillRect(this.pauseBtn.x - 6, this.pauseBtn.y - 7, 4, 14);
    cx.fillRect(this.pauseBtn.x + 2, this.pauseBtn.y - 7, 4, 14);
    cx.restore();

    // Active power-up timer bars.
    const bars: Array<[string, number, number, readonly [number, number, number]]> = [];
    if (world.tripleTimer > 0) bars.push(["3X", world.tripleTimer, 8, [240, 192, 64]]);
    if (world.magnetTimer > 0) bars.push(["MAG", world.magnetTimer, 8, [255, 90, 90]]);
    if (world.slowmoTimer > 0) bars.push(["SLOW", world.slowmoTimer, 8, [180, 110, 240]]);
    if (world.kfcTimer > 0) bars.push(["KFC", world.kfcTimer, 8, [220, 80, 60]]);
    if (world.ghostTimer > 0) bars.push(["GHO", world.ghostTimer, 8, [200, 220, 240]]);
    if (world.growTimer > 0) bars.push(["GRO", world.growTimer, 8, [220, 100, 130]]);
    let yy = 60;
    for (const [label, t, max, col] of bars) {
      const k = Math.max(0, Math.min(1, t / max));
      const bw = 132;
      cx.fillStyle = rgba([0, 0, 0], 110);
      cx.fillRect(W / 2 - bw / 2 - 3, yy - 8, bw + 6, 16);
      cx.fillStyle = rgb([40, 40, 50]);
      cx.fillRect(W / 2 - bw / 2, yy - 5, bw, 10);
      cx.fillStyle = rgb(col);
      cx.fillRect(W / 2 - bw / 2, yy - 5, bw * k, 10);
      cx.font = fontStr(9, true);
      cx.fillStyle = rgb([255, 255, 255]);
      cx.textAlign = "left"; cx.textBaseline = "middle";
      cx.fillText(label, W / 2 - bw / 2 - 30, yy);
      yy += 22;
    }

    // Float texts.
    for (const f of world.floatTexts) f.draw(cx);
  }

  drawPauseOverlay(cx: CanvasRenderingContext2D): void {
    cx.fillStyle = rgba([6, 2, 28], 165);
    cx.fillRect(0, 0, W, H);
    outlinedText(cx, "PAUSED", W / 2, H / 2 - 20, 36);
    cx.font = fontStr(12, true);
    cx.fillStyle = rgba([216, 184, 85], 200);
    cx.textAlign = "center"; cx.textBaseline = "middle";
    cx.fillText("Tap to resume", W / 2, H / 2 + 24);
  }

  drawStats(cx: CanvasRenderingContext2D, world: World, _dt: number, statsT: number, showPrompt: boolean): void {
    cx.fillStyle = rgba([6, 2, 28], 200);
    cx.fillRect(0, 0, W, H);
    outlinedText(cx, "RUN END", W / 2, 80, 30);
    cx.font = fontStr(14, true);
    cx.fillStyle = rgb([240, 192, 64]);
    cx.textAlign = "left";
    cx.textBaseline = "middle";
    const x = 70;
    let y = 150;
    const rows: Array<[string, string]> = [
      ["Score", String(world.score)],
      ["Coins", String(world.coinCount)],
      ["Pillars", String(world.pillarsPassed)],
      ["Time", `${world.timeAlive.toFixed(1)}s`],
      ["Near misses", String(world.nearMisses)],
    ];
    for (const [k, v] of rows) {
      cx.fillStyle = rgba([216, 184, 85], 220);
      cx.fillText(k, x, y);
      cx.fillStyle = rgb([255, 255, 255]);
      cx.textAlign = "right";
      cx.fillText(v, W - x, y);
      cx.textAlign = "left";
      y += 30;
    }
    if (showPrompt && statsT >= 0.6) {
      pillBtn(cx, W / 2, H - 90, "TAP TO CONTINUE", 14, 0.5 + 0.5 * Math.sin(statsT * 4));
    }
  }

  drawLeaderboard(
    cx: CanvasRenderingContext2D, _dt: number,
    scores: ScoreRow[], playerRank: number, cooldown: number, fetchError: string,
  ): void {
    cx.fillStyle = rgba([6, 2, 28], 220);
    cx.fillRect(0, 0, W, H);
    outlinedText(cx, "TOP 10", W / 2, 60, 28);
    cx.font = fontStr(14, true);
    if (scores.length === 0) {
      cx.fillStyle = rgb([216, 184, 85]);
      cx.textAlign = "center"; cx.textBaseline = "middle";
      cx.fillText(fetchError ? `Top-10 unavailable (${fetchError})` : "No scores yet — be the first!",
                   W / 2, H / 2);
    } else {
      let y = 110;
      scores.forEach((row, i) => {
        const isYou = i === playerRank;
        cx.fillStyle = rgb(isYou ? [240, 192, 64] : [255, 255, 255]);
        cx.textAlign = "left"; cx.textBaseline = "middle";
        cx.fillText(`${i + 1}. ${row.name.padEnd(10).slice(0, 10)}`, 60, y);
        cx.textAlign = "right";
        cx.fillText(String(row.score), W - 60, y);
        y += 32;
      });
    }
    if (cooldown <= 0) {
      pillBtn(cx, W / 2, H - 60, "TAP", 14, 0.85);
    }
  }

  drawGameover(cx: CanvasRenderingContext2D, _dt: number, score: number, newBest: boolean): void {
    cx.fillStyle = rgba([6, 2, 28], 200);
    cx.fillRect(0, 0, W, H);
    outlinedText(cx, "GAME OVER", W / 2, H * 0.32, 30);
    cx.font = fontStr(16, true);
    cx.fillStyle = rgb([240, 192, 64]);
    cx.textAlign = "center"; cx.textBaseline = "middle";
    cx.fillText(`SCORE  ${score}`, W / 2, H * 0.32 + 50);
    if (newBest) {
      outlinedText(cx, "NEW BEST!", W / 2, H * 0.32 + 90, 18, [255, 230, 130], RED_OUTLINE, 2);
    }
    pillBtn(cx, W / 2, H * 0.7, "TAP TO RETRY", 16);
    void PANEL_DARK;
  }
}

function makeRgba(r: number, g: number, b: number, a: number): string {
  return `rgba(${r},${g},${b},${a / 255})`;
}
