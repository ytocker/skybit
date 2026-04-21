// Headless smoke test: imports the World/Game modules and runs the update+render
// loop for ~30 simulated seconds, verifying no exceptions occur.

globalThis.ImageData = class {
    constructor(w, h) {
        this.width = w;
        this.height = h;
        this.data = new Uint8ClampedArray(w * h * 4);
    }
};

globalThis.localStorage = (() => {
    const store = new Map();
    return {
        getItem: (k) => store.has(k) ? store.get(k) : null,
        setItem: (k, v) => store.set(k, String(v)),
        removeItem: (k) => store.delete(k),
    };
})();

// Silence Web Audio: the game calls `sfx.flap()` etc which call `ensure()` which
// touches window.AudioContext. We'll shim it with no-ops.
globalThis.window = globalThis;
globalThis.AudioContext = class {
    constructor() { this.currentTime = 0; this.sampleRate = 48000; this.destination = {}; this.state = 'running'; }
    createGain() { return { gain: { value: 1, setValueAtTime(){}, linearRampToValueAtTime(){}, exponentialRampToValueAtTime(){} }, connect() { return this; } }; }
    createOscillator() { return { frequency: { setValueAtTime(){}, exponentialRampToValueAtTime(){} }, connect() { return this; }, start(){}, stop(){}, type: 'square' }; }
    createBuffer() { return { getChannelData: () => new Float32Array(1) }; }
    createBufferSource() { return { connect() { return this; }, start(){}, stop(){}, buffer: null }; }
    createBiquadFilter() { return { frequency: { value: 0 }, type: '', connect() { return this; } }; }
    resume() { return Promise.resolve(); }
};
globalThis.performance = { now: () => Date.now() };

const { PixelBuffer } = await import('../src/gfx.js');
const { Game } = await import('../src/scenes.js');
const { VIEW_W, VIEW_H, DT } = await import('../src/config.js');

const buf = new PixelBuffer(VIEW_W, VIEW_H);
const game = new Game();

// Simulate: menu → flap (starts play) → flap every ~0.4s for 30s
const totalSeconds = 30;
const steps = Math.floor(totalSeconds / DT);
let tapAccum = 0;
let died = false;
let deaths = 0;

for (let i = 0; i < steps; i++) {
    tapAccum += DT;
    if (tapAccum >= 0.38) {
        tapAccum = 0;
        game.handleFlap();
    }
    game.update(DT);
    // Render every 3 steps (20 renders/sec is enough to catch render-time bugs).
    if (i % 3 === 0) game.render(buf);
    if (game.scene === 'gameover') {
        deaths++;
        // Retry after 0.7s sim time
        setTimeout(() => {}, 0); // noop
        if (deaths < 3) {
            // Simulate the retry tap (after debounce)
            for (let j = 0; j < 50; j++) game.update(DT);
            game.handleFlap();
        }
    }
}

console.log('ok, scene:', game.scene, 'score:', game.world.score, 'high:', game.highScore, 'deaths:', deaths);
