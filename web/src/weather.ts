// Weather — biome-driven rain and night-fog. Simplified from
// game/weather.py; lightning thunderclaps deferred for v1.

import { W, H, GROUND_Y } from "./config.js";
import { rgba } from "./draw.js";
import type { Palette } from "./biome.js";

interface Drop { x: number; y: number; vx: number; vy: number; len: number; }

export class Weather {
  private drops: Drop[] = [];
  private fogPhase = 0;

  // Decide how heavy the rain should be based on the biome. Dusk + sunset
  // get a moderate sprinkle, the rest is dry.
  private intensity(palette: Palette): number {
    const s = palette.star_alpha;
    if (s > 100 && s < 200) return 0.6;     // dusk
    if (s >= 20 && s <= 100) return 0.25;   // sunset / predawn
    return 0;
  }

  update(dt: number, palette: Palette, scrollSpeed: number): void {
    const inten = this.intensity(palette);
    this.fogPhase += dt;
    // Spawn new drops proportional to intensity.
    const target = (inten * 80) | 0;
    while (this.drops.length < target) {
      this.drops.push({
        x: Math.random() * W,
        y: -10 - Math.random() * 200,
        vx: -scrollSpeed * 0.4,
        vy: 320 + Math.random() * 80,
        len: 6 + Math.random() * 6,
      });
    }
    // Update & cull.
    for (const d of this.drops) {
      d.x += d.vx * dt;
      d.y += d.vy * dt;
    }
    this.drops = this.drops.filter((d) => d.y < GROUND_Y && d.x > -10);
  }

  draw(cx: CanvasRenderingContext2D): void {
    if (this.drops.length > 0) {
      cx.strokeStyle = rgba([170, 200, 230], 110);
      cx.lineWidth = 1;
      cx.beginPath();
      for (const d of this.drops) {
        cx.moveTo(d.x, d.y);
        cx.lineTo(d.x - 1, d.y + d.len);
      }
      cx.stroke();
    }
    // No global fog overlay in v1 — keeps the biome palette readable.
    void this.fogPhase;
    void H;
  }
}
