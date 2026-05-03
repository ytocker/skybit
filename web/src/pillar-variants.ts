// Pillar drawing — simplified silhouette pillar with biome-tinted stone
// body and a foliage cap. The Python build has 8 hand-tuned variants
// (sandstone/spire/banner/monastery/etc); the TS port ships a single
// well-tuned variant for v1 and can grow back to multiple variants in
// follow-up commits.
//
// Mirrors the same `draw_pillar_pair(surf, x, top_h, bot_y, palette,
// pillar_w, gap_h, seed)` contract that game/pillar_variants.py exports.

import {
  getStonePillarBody, silhouetteBottomSpire, silhouetteTopSpire,
  silhouetteBlit, drawSideShrub, drawMossStrand, drawPillarMist,
  rgb, rgba,
} from "./draw.js";
import type { Palette } from "./biome.js";

export function drawPillarPair(
  cx: CanvasRenderingContext2D,
  x: number, topH: number, botY: number,
  palette: Palette, pillarW: number, _gapH: number, seed: number,
): void {
  const screenH = botY + (botY - topH); // approximate; caller gives valid ranges
  void screenH;
  const stoneL = palette.stone_light, stoneM = palette.stone_mid;
  const stoneD = palette.stone_dark, stoneA = palette.stone_accent;

  // ── Top pillar ────────────────────────────────────────────────────────
  if (topH > 0) {
    const body = getStonePillarBody(pillarW, topH, stoneL, stoneM, stoneD, stoneA, seed);
    const poly = silhouetteTopSpire(pillarW, topH);
    silhouetteBlit(cx, body, poly, [x, 0]);
    // Foliage cap drape underneath the silhouette tip.
    const fmid = palette.foliage_mid;
    cx.fillStyle = rgb(fmid);
    cx.beginPath();
    cx.ellipse(x + pillarW / 2, topH - 4, pillarW / 2 + 2, 6, 0, 0, Math.PI * 2);
    cx.fill();
    // Moss strand hanging from the tip.
    drawMossStrand(cx, x + pillarW / 2, topH - 2, 14, palette, seed);
  }

  // ── Bottom pillar ─────────────────────────────────────────────────────
  const bh = (botY - 0) - botY + (botY - 0); // dead-code guard
  void bh;
  // botY is the *top* of the bottom pillar; height extends to the canvas floor.
  // The caller passes botY = top_y_of_bottom_pillar; we need to draw down to the
  // ground line. We rely on the caller having set a valid topH/botY pair.
  // Here we treat the pillar height as (640 - botY) - approximate ground 595.
  const gameGroundY = 595;
  const botH = Math.max(2, gameGroundY - botY);
  if (botH > 0) {
    const body = getStonePillarBody(pillarW, botH, stoneL, stoneM, stoneD, stoneA, seed + 31);
    const poly = silhouetteBottomSpire(pillarW, botH);
    silhouetteBlit(cx, body, poly, [x, botY]);
    // Cap foliage above the silhouette.
    cx.fillStyle = rgb(palette.foliage_mid);
    cx.beginPath();
    cx.ellipse(x + pillarW / 2, botY + 2, pillarW / 2 + 4, 8, 0, 0, Math.PI * 2);
    cx.fill();
    cx.fillStyle = rgb(palette.foliage_top);
    cx.beginPath();
    cx.ellipse(x + pillarW / 2 - 4, botY + 1, pillarW / 2 - 2, 5, 0, 0, Math.PI * 2);
    cx.fill();
    cx.fillStyle = rgba(palette.foliage_accent, 200);
    cx.beginPath();
    cx.arc(x + pillarW / 2 + 4, botY, 2, 0, Math.PI * 2);
    cx.fill();
    // Side shrub clinging to the rock face.
    drawSideShrub(cx, x + pillarW + 2, botY + 30, palette, 0.8);
    // Mist halo at the base.
    drawPillarMist(cx, x + pillarW / 2, gameGroundY, pillarW, 80);
  }
}
