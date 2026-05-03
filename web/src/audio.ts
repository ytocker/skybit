// Audio playback via the Web Audio API. Loads OGG samples lazily on first
// play, decodes once, then triggers via short-lived BufferSourceNode + GainNode.
//
// Mirrors game/audio.py's public API and the inject_theme.py skyPlay()
// JS implementation — same files, same volumes, same lazy-load semantics.

let _ctx: AudioContext | null = null;
const _cache = new Map<string, AudioBuffer>();
const _pending = new Map<string, Promise<AudioBuffer>>();
let _failedOnce = false;

function getCtx(): AudioContext {
  if (!_ctx) {
    const Ctor = (window as any).AudioContext || (window as any).webkitAudioContext;
    _ctx = new Ctor();
  }
  if (_ctx!.state === "suspended") void _ctx!.resume();
  return _ctx!;
}

// Web Audio is gated on a user gesture (UME). Unlock the shared context
// inside the first listener that fires during a real tap/click — the
// loading overlay's dismiss handler in main.ts calls this.
export function unlockAudio(): void {
  try { getCtx(); } catch { /* device may not have an audio output; ignore */ }
}

async function loadSnd(name: string): Promise<AudioBuffer> {
  const cached = _cache.get(name);
  if (cached) return cached;
  const inflight = _pending.get(name);
  if (inflight) return inflight;
  const ac = getCtx();
  const p = (async () => {
    const r = await fetch(`./sounds/${name}.ogg`);
    const buf = await r.arrayBuffer();
    const decoded = await ac.decodeAudioData(buf);
    _cache.set(name, decoded);
    _pending.delete(name);
    return decoded;
  })().catch((e) => {
    _pending.delete(name);
    throw e;
  });
  _pending.set(name, p);
  return p;
}

function play(name: string, volume: number): void {
  loadSnd(name).then((buf) => {
    const ac = getCtx();
    const src = ac.createBufferSource();
    src.buffer = buf;
    const g = ac.createGain();
    g.gain.value = volume;
    src.connect(g); g.connect(ac.destination);
    src.start();
  }).catch((e) => {
    if (!_failedOnce) {
      _failedOnce = true;
      console.warn("audio.ts: play failed for", name, e);
    }
  });
}

// Voice-limiting (cap on currently-playing channels for high-frequency
// events) is delegated to the browser — Web Audio handles many concurrent
// sources fine, and the perceptual issue the Python build addressed
// (mixer channel exhaustion on 14-coin rushes) doesn't apply here.

// ── Public API — identical surface to game/audio.py ────────────────────────

export function init(): void { /* lazy — resolved on first play() */ }

export const playFlap        = (): void => play("flap", 0.55);
export const playCoin        = (): void => play("coin", 0.75);
export const playCoinTriple  = (): void => play("coin_triple", 0.85);
export const playTripleCoin  = (): void => play("triple_coin", 0.85);
export const playMagnet      = (): void => play("magnet", 0.75);
export const playSlowmo      = (): void => play("slowmo", 0.75);
export const playThunder     = (): void => play("thunder", 0.85);
export const playDeath       = (): void => play("death", 0.75);
export const playGameover    = (): void => play("gameover", 0.70);
export const playPoof        = (): void => play("poof", 0.88);
export const playGhost       = (): void => play("ghost", 0.70);
export const playGrow        = (): void => play("grow", 0.80);
