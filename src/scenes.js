import { VIEW_W, VIEW_H, GROUND_Y } from './config.js';
import { C, PAL } from './palette.js';
import { World } from './world.js';
import { CLOUD, drawText, drawTextCentered, measureText } from './sprites.js';
import { drawHUD, drawStartHint, drawTitle, drawGameOver } from './hud.js';
import { loadHighScore, saveHighScore } from './storage.js';
import { sfx } from './audio.js';

function drawSky(buf, t) {
    // Multi-band dithered gradient for a lush dusk-to-day sky.
    buf.gradientBand(0, 0, buf.w, 70, C.INDIGO, C.DUSK);
    buf.gradientBand(0, 70, buf.w, 80, C.DUSK, C.SKY);
    buf.gradientBand(0, 150, buf.w, GROUND_Y - 150, C.SKY, C.CREAM);

    // A low sun / moon disc that slowly drifts.
    const sx = 140, sy = 60 + Math.sin(t * 0.3) * 2;
    buf.disc(sx, sy, 10, C.CREAM);
    buf.disc(sx, sy, 8, C.GOLD);
    buf.disc(sx, sy, 5, C.ORANGE);
    // Rays/halo
    buf.ring(sx, sy, 13, C.GOLD);
}

function drawMountains(buf, mountains, scroll) {
    // Far mountains — dark indigo silhouette.
    const len = mountains.length;
    for (let x = 0; x < buf.w; x++) {
        const idx = (x + Math.floor(scroll * 0.5)) % len;
        const h = mountains[idx];
        buf.rect(x, GROUND_Y - h, 1, h, C.INDIGO);
    }
    // Near mountains — medium indigo, shifted.
    for (let x = 0; x < buf.w; x++) {
        const idx = (x + Math.floor(scroll * 0.9) + 40) % len;
        const h = mountains[idx] * 0.75;
        buf.rect(x, GROUND_Y - h, 1, h, C.NAVY);
    }
}

function drawClouds(buf, clouds) {
    for (const c of clouds) {
        buf.blit(CLOUD, c.x | 0, c.y | 0);
    }
}

function drawGround(buf, scroll) {
    // Dirt band
    buf.rect(0, GROUND_Y, buf.w, VIEW_H - GROUND_Y, C.WOOD);
    // Grass strip on top
    buf.rect(0, GROUND_Y, buf.w, 4, C.GRASS);
    buf.rect(0, GROUND_Y + 2, buf.w, 1, C.LEAF);

    // Moving grass tufts + speckles
    const off = (scroll | 0) % 8;
    for (let x = -off; x < buf.w; x += 8) {
        buf.put(x + 1, GROUND_Y - 1, C.LIME);
        buf.put(x + 5, GROUND_Y - 1, C.LIME);
    }
    // Dirt speckles
    for (let y = GROUND_Y + 6; y < VIEW_H; y += 6) {
        for (let x = -((scroll * 1.2) | 0) % 10; x < buf.w; x += 10) {
            buf.put(x + 3, y, C.AMBER);
        }
    }
}

function drawParticles(world, buf) {
    for (const p of world.particles) p.draw(buf);
}

export class Game {
    constructor() {
        this.scene = 'menu';
        this.world = new World();
        this.highScore = loadHighScore();
        this.newBest = false;
        this.menuT = 0;
        this.paused = false;
        this.crt = true;
    }

    toMenu() {
        this.scene = 'menu';
        this.world.reset();
        this.newBest = false;
    }

    startPlay() {
        this.scene = 'play';
        this.world.reset();
        this.newBest = false;
    }

    toGameOver() {
        this.scene = 'gameover';
        if (this.world.score > this.highScore) {
            this.highScore = this.world.score;
            this.newBest = true;
            saveHighScore(this.highScore);
        }
    }

    handleFlap() {
        if (this.paused) { this.paused = false; return; }
        if (this.scene === 'menu') {
            this.startPlay();
            this.world.flap();
        } else if (this.scene === 'play') {
            this.world.flap();
        } else if (this.scene === 'gameover') {
            // Tiny debounce so the death tap doesn't instantly retry.
            if (this.world.elapsed > 0.6) this.toMenu();
        }
    }

    handlePause() {
        if (this.scene === 'play') this.paused = !this.paused;
        sfx.click();
    }

    update(dt) {
        if (this.scene === 'menu') {
            this.menuT += dt;
            // Keep world ticking softly so parallax moves under the title.
            this.world.started = false;
            this.world.update(dt * 0.4);
            return;
        }
        if (this.paused) return;

        // Time-slow during mushroom pickup briefly affects gameplay speed.
        const scale = this.world.fx.timeScale;
        this.world.update(dt * scale);

        if (this.scene === 'play' && this.world.gameOver) {
            // brief delay so the death anim plays before the UI pops in.
            if (this.world.elapsed > 0.5 || this.world.bird.y >= GROUND_Y - this.world.bird.r - 1) {
                this.toGameOver();
            }
        }
    }

    render(buf) {
        const w = this.world;
        const shake = w.fx.shakeOffset();

        buf.clear(C.NIGHT);

        // Sky + sun
        drawSky(buf, w.elapsed);

        // Clouds (parallax)
        drawClouds(buf, w.clouds);

        // Mountains (parallax)
        drawMountains(buf, w.mountains, w.mountainScroll);

        // Ground
        drawGround(buf, w.groundScroll);

        // Pipes
        for (const p of w.pipes) p.draw(buf);

        // Coins
        for (const c of w.coins) c.draw(buf);

        // Mushrooms
        for (const m of w.mushrooms) m.draw(buf);

        // Particles (behind bird for subtlety)
        drawParticles(w, buf);

        // Bird (with pseudo-rotation: we just offset y by angle * 2 px for tilt feel)
        w.bird.draw(buf);

        // If mushroom buff active, draw a pulsing aura behind the bird.
        if (w.tripleTimer > 0) {
            const r = 10 + Math.round(Math.sin(w.elapsed * 10) * 2);
            buf.ring(w.bird.x, w.bird.y, r, C.ORANGE);
            buf.ring(w.bird.x, w.bird.y, r + 2, C.GOLD);
        }

        // Apply shake by translating the pixel buffer contents (nudge next overlay only; simpler: draw HUD at shaken coords? We'll shake the scene by drawing next frame offset — here we just offset HUD screen text so gameplay jiggles aren't needed; keep HUD steady.)

        // Scene overlays
        if (this.scene === 'menu') {
            drawTitle(buf, this.menuT);
            drawStartHint(buf);
        } else if (this.scene === 'play') {
            if (!w.started) drawStartHint(buf);
            const pr = drawHUD(buf, w, this.highScore);
            this._pauseRect = pr;
            if (this.paused) {
                // Dim + PAUSED text
                for (let i = 0; i < buf.u32.length; i++) {
                    const p = buf.u32[i];
                    const r = (p & 0xff) * 0.55 | 0;
                    const g = ((p >> 8) & 0xff) * 0.55 | 0;
                    const b = ((p >> 16) & 0xff) * 0.55 | 0;
                    buf.u32[i] = (0xff << 24) | (b << 16) | (g << 8) | r;
                }
                drawTextCentered(buf, 'PAUSED', 150, C.NIGHT, 2);
                drawTextCentered(buf, 'PAUSED', 149, C.WHITE, 2);
                drawTextCentered(buf, 'TAP TO RESUME', 170, C.CREAM);
            }
        } else if (this.scene === 'gameover') {
            drawHUD(buf, w, this.highScore);
            drawGameOver(buf, w.score, this.highScore, this.newBest);
        }

        // Full-frame flash (death / mushroom)
        w.fx.applyFlash(buf);

        // CRT overlay
        if (this.crt) {
            buf.scanlines(0, 2);
            buf.vignette(0.35);
        }

        // Screen shake: simple vertical/horizontal nudge by copying pixels.
        if (shake.x || shake.y) {
            // Copy into temp then blit back offset.
            const tmp = new Uint32Array(buf.u32);
            buf.u32.fill(PAL[C.NIGHT]);
            const W = buf.w, H = buf.h;
            for (let y = 0; y < H; y++) {
                const sy = y - shake.y;
                if (sy < 0 || sy >= H) continue;
                for (let x = 0; x < W; x++) {
                    const sx = x - shake.x;
                    if (sx < 0 || sx >= W) continue;
                    buf.u32[y * W + x] = tmp[sy * W + sx];
                }
            }
        }
    }

    pauseRect() { return this._pauseRect; }
}
