// Skybit gameplay constants — ported 1:1 from game/config.py.
// Keep the layout in sync; if you tune a value here, mirror it in any
// asset-side tooling so visual references stay valid.

export const W = 360;
export const H = 640;
export const FPS = 60;
export const TITLE = "Skybit";

export const GROUND_Y = 595;
export const CEILING_Y = 0;

export const GRAVITY = 1600.0;
export const FLAP_V = -520.0;
export const MAX_FALL = 700.0;

export const SCROLL_BASE = 160.0;
export const SCROLL_MAX = 290.0;

export const PIPE_W = 58;
export const PIPE_SPACING = 280;
export const GAP_START = 170;
export const GAP_MIN = 115;

export const BIRD_X = 90;
export const BIRD_R = 14;

// Pip carries the parcel for the entire run. The parcel collision footprint
// is a second circle below the bird; pillars touching it are also lethal.
export const PARCEL_R = 9;
export const PARCEL_Y_OFFSET = 12;

export const COIN_R = 13;

export const COIN_RUSH_INTERVAL = 15;
export const COIN_RUSH_GAP_BOOST = 1.30;
export const COIN_RUSH_COINS = 14;

export const POWERUP_R = 14;
export const POWERUP_CHANCE = 0.24;
export const POWERUP_COOLDOWN = 5.5;
export const TRIPLE_DURATION = 8.0;
export const MAGNET_DURATION = 8.0;
export const MAGNET_RADIUS = 82.0;
export const SLOWMO_DURATION = 8.0;
export const SLOWMO_SCALE = 0.7;
export const KFC_DURATION = 8.0;
export const GHOST_DURATION = 8.0;
export const GROW_DURATION = 8.0;
export const GROW_SCALE = 1.5;
export const REVERSE_DURATION = 8.0;

export type PowerUpKind =
  | "triple" | "magnet" | "slowmo" | "kfc" | "ghost" | "grow"
  | "reverse" | "surprise";

// Spawn weights for power-up kinds. Normalised at pick time. `surprise`
// resolves at pickup time to one of the six "real" kinds chosen at
// random. `reverse` is intentionally excluded — implementation kept
// for re-enable but the kind doesn't spawn or resolve from a surprise box.
export const POWERUP_WEIGHTS: ReadonlyArray<readonly [PowerUpKind, number]> = [
  ["triple", 1],
  ["slowmo", 1],
  ["magnet", 1],
  ["kfc", 1],
  ["ghost", 1],
  ["grow", 1],
  ["surprise", 1],
];

// Local-storage keys (browser persistence).
export const SAVE_KEY = "skybit_save";
export const SCORES_KEY = "skybit_scores";
