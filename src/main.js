import { VIEW_W, VIEW_H, DT } from './config.js';
import { PixelBuffer, fitCanvasToViewport } from './gfx.js';
import { Input } from './input.js';
import { Game } from './scenes.js';
import { unlock, setMuted } from './audio.js';
import { loadSettings, saveSettings } from './storage.js';

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
ctx.imageSmoothingEnabled = false;

const buf = new PixelBuffer(VIEW_W, VIEW_H);
const game = new Game();
const input = new Input(canvas);

// Load settings
const settings = loadSettings();
game.crt = settings.crt !== false;
setMuted(!!settings.muted);

input.onFlap = () => {
    unlock();
    game.handleFlap();
};
input.onPause = () => {
    unlock();
    game.handlePause();
};

function resize() { fitCanvasToViewport(canvas); }
resize();
window.addEventListener('resize', resize);
window.addEventListener('orientationchange', resize);

// Fixed-timestep loop.
let last = performance.now() / 1000;
let accum = 0;
const MAX_STEPS = 5;

function frame(now) {
    const t = now / 1000;
    let dt = t - last;
    last = t;
    if (dt > 0.25) dt = 0.25; // clamp after tab switch
    accum += dt;
    let steps = 0;
    while (accum >= DT && steps < MAX_STEPS) {
        game.update(DT);
        accum -= DT;
        steps++;
    }
    // Render one frame.
    game.render(buf);
    ctx.putImageData(buf.image, 0, 0);

    // Update input pause-hit rect from current HUD.
    const pr = game.pauseRect();
    if (pr) input.setPauseRect(pr);

    requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

// Persist CRT toggle on a key so we don't build a full settings menu.
window.addEventListener('keydown', (e) => {
    if (e.code === 'KeyC') {
        game.crt = !game.crt;
        saveSettings(Object.assign(loadSettings(), { crt: game.crt }));
    }
    if (e.code === 'KeyM') {
        const s = loadSettings();
        s.muted = !s.muted;
        setMuted(s.muted);
        saveSettings(s);
    }
});
