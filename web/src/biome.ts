// Biome / time-of-day palettes — ported 1:1 from game/biome.py.
//
// A single `phase` float in [0, 1) cycles through day → golden hour →
// sunset → dusk → night → predawn → sunrise → day, driven by real
// elapsed gameplay seconds.

export type Color = readonly [number, number, number];

export interface Palette {
  sky_top: Color;
  sky_mid: Color;
  sky_bot: Color;
  horizon: Color;
  mtn_far: Color;
  mtn_near: Color;
  ground_top: Color;
  ground_mid: Color;
  stone_light: Color;
  stone_mid: Color;
  stone_dark: Color;
  stone_accent: Color;
  foliage_top: Color;
  foliage_mid: Color;
  foliage_dark: Color;
  foliage_accent: Color;
  star_alpha: number;
}

export function lerpColor(a: Color, b: Color, t: number): Color {
  t = Math.max(0, Math.min(1, t));
  return [
    (a[0] + (b[0] - a[0]) * t) | 0,
    (a[1] + (b[1] - a[1]) * t) | 0,
    (a[2] + (b[2] - a[2]) * t) | 0,
  ];
}

const KEYFRAMES: ReadonlyArray<readonly [number, Palette]> = [
  [0.00, {
    sky_top: [40, 110, 200], sky_mid: [90, 170, 230], sky_bot: [170, 220, 245],
    horizon: [255, 240, 200], mtn_far: [80, 120, 170], mtn_near: [55, 95, 145],
    ground_top: [80, 200, 80], ground_mid: [40, 150, 40],
    stone_light: [225, 195, 155], stone_mid: [175, 140, 105],
    stone_dark: [95, 70, 55], stone_accent: [255, 220, 170],
    foliage_top: [140, 220, 110], foliage_mid: [70, 170, 75],
    foliage_dark: [30, 100, 50], foliage_accent: [255, 240, 120],
    star_alpha: 0,
  }],
  [0.18, {
    sky_top: [80, 120, 200], sky_mid: [220, 175, 140], sky_bot: [255, 210, 160],
    horizon: [255, 220, 140], mtn_far: [130, 110, 150], mtn_near: [85, 75, 115],
    ground_top: [120, 190, 80], ground_mid: [80, 135, 50],
    stone_light: [240, 200, 145], stone_mid: [200, 150, 90],
    stone_dark: [110, 70, 40], stone_accent: [255, 225, 155],
    foliage_top: [180, 210, 90], foliage_mid: [130, 170, 60],
    foliage_dark: [70, 100, 40], foliage_accent: [255, 200, 80],
    star_alpha: 0,
  }],
  [0.32, {
    sky_top: [90, 50, 130], sky_mid: [230, 95, 120], sky_bot: [255, 160, 90],
    horizon: [255, 200, 120], mtn_far: [90, 60, 120], mtn_near: [55, 35, 85],
    ground_top: [150, 105, 110], ground_mid: [95, 60, 80],
    stone_light: [240, 170, 155], stone_mid: [190, 105, 110],
    stone_dark: [100, 45, 60], stone_accent: [255, 210, 170],
    foliage_top: [210, 150, 90], foliage_mid: [150, 95, 65],
    foliage_dark: [85, 45, 40], foliage_accent: [255, 160, 80],
    star_alpha: 20,
  }],
  [0.48, {
    sky_top: [25, 20, 70], sky_mid: [70, 45, 130], sky_bot: [170, 95, 140],
    horizon: [255, 150, 140], mtn_far: [45, 30, 85], mtn_near: [25, 15, 55],
    ground_top: [80, 70, 110], ground_mid: [45, 35, 75],
    stone_light: [180, 160, 200], stone_mid: [110, 95, 150],
    stone_dark: [55, 40, 80], stone_accent: [220, 200, 240],
    foliage_top: [120, 160, 150], foliage_mid: [60, 100, 110],
    foliage_dark: [25, 50, 70], foliage_accent: [180, 220, 200],
    star_alpha: 130,
  }],
  [0.62, {
    sky_top: [5, 8, 30], sky_mid: [15, 25, 70], sky_bot: [35, 55, 115],
    horizon: [170, 190, 255], mtn_far: [25, 35, 75], mtn_near: [15, 20, 50],
    ground_top: [35, 60, 75], ground_mid: [20, 40, 55],
    stone_light: [150, 170, 210], stone_mid: [80, 100, 150],
    stone_dark: [30, 45, 85], stone_accent: [200, 225, 255],
    foliage_top: [80, 130, 130], foliage_mid: [35, 80, 90],
    foliage_dark: [10, 35, 55], foliage_accent: [160, 220, 230],
    star_alpha: 235,
  }],
  [0.78, {
    sky_top: [30, 30, 80], sky_mid: [70, 60, 140], sky_bot: [200, 130, 180],
    horizon: [255, 200, 210], mtn_far: [55, 50, 110], mtn_near: [30, 25, 70],
    ground_top: [80, 95, 130], ground_mid: [45, 60, 95],
    stone_light: [220, 175, 200], stone_mid: [155, 110, 150],
    stone_dark: [75, 50, 90], stone_accent: [255, 210, 225],
    foliage_top: [130, 155, 130], foliage_mid: [70, 105, 95],
    foliage_dark: [35, 60, 60], foliage_accent: [200, 220, 180],
    star_alpha: 90,
  }],
  [0.90, {
    sky_top: [50, 100, 180], sky_mid: [255, 150, 150], sky_bot: [255, 220, 170],
    horizon: [255, 235, 180], mtn_far: [135, 105, 150], mtn_near: [85, 70, 110],
    ground_top: [130, 190, 120], ground_mid: [85, 140, 75],
    stone_light: [255, 205, 175], stone_mid: [215, 150, 125],
    stone_dark: [130, 75, 70], stone_accent: [255, 230, 195],
    foliage_top: [170, 220, 130], foliage_mid: [95, 170, 90],
    foliage_dark: [45, 110, 60], foliage_accent: [255, 210, 130],
    star_alpha: 0,
  }],
  [1.00, {
    sky_top: [40, 110, 200], sky_mid: [90, 170, 230], sky_bot: [170, 220, 245],
    horizon: [255, 240, 200], mtn_far: [80, 120, 170], mtn_near: [55, 95, 145],
    ground_top: [80, 200, 80], ground_mid: [40, 150, 40],
    stone_light: [225, 195, 155], stone_mid: [175, 140, 105],
    stone_dark: [95, 70, 55], stone_accent: [255, 220, 170],
    foliage_top: [140, 220, 110], foliage_mid: [70, 170, 75],
    foliage_dark: [30, 100, 50], foliage_accent: [255, 240, 120],
    star_alpha: 0,
  }],
];

export const CYCLE_SECONDS = 300.0;
export const PHASE_BUCKETS = 32;

export function phaseForTime(elapsed: number): number {
  return ((elapsed / CYCLE_SECONDS) + 0.04) % 1.0;
}

function blend(a: Palette, b: Palette, t: number): Palette {
  return {
    sky_top: lerpColor(a.sky_top, b.sky_top, t),
    sky_mid: lerpColor(a.sky_mid, b.sky_mid, t),
    sky_bot: lerpColor(a.sky_bot, b.sky_bot, t),
    horizon: lerpColor(a.horizon, b.horizon, t),
    mtn_far: lerpColor(a.mtn_far, b.mtn_far, t),
    mtn_near: lerpColor(a.mtn_near, b.mtn_near, t),
    ground_top: lerpColor(a.ground_top, b.ground_top, t),
    ground_mid: lerpColor(a.ground_mid, b.ground_mid, t),
    stone_light: lerpColor(a.stone_light, b.stone_light, t),
    stone_mid: lerpColor(a.stone_mid, b.stone_mid, t),
    stone_dark: lerpColor(a.stone_dark, b.stone_dark, t),
    stone_accent: lerpColor(a.stone_accent, b.stone_accent, t),
    foliage_top: lerpColor(a.foliage_top, b.foliage_top, t),
    foliage_mid: lerpColor(a.foliage_mid, b.foliage_mid, t),
    foliage_dark: lerpColor(a.foliage_dark, b.foliage_dark, t),
    foliage_accent: lerpColor(a.foliage_accent, b.foliage_accent, t),
    star_alpha: a.star_alpha + (b.star_alpha - a.star_alpha) * t,
  };
}

export function paletteForPhase(phase: number): Palette {
  const p = ((phase % 1.0) + 1.0) % 1.0;
  for (let i = 0; i < KEYFRAMES.length - 1; i++) {
    const [t0, p0] = KEYFRAMES[i];
    const [t1, p1] = KEYFRAMES[i + 1];
    if (t0 <= p && p <= t1) {
      const span = t1 - t0;
      let t = span > 0 ? (p - t0) / span : 0;
      t = t * t * (3 - 2 * t);
      return blend(p0, p1, t);
    }
  }
  return KEYFRAMES[0][1];
}

export function paletteForTime(elapsed: number): Palette {
  return paletteForPhase(phaseForTime(elapsed));
}

export function phaseBucket(phase: number): number {
  return ((((phase % 1.0) + 1.0) % 1.0) * PHASE_BUCKETS) | 0;
}
