import {
    VIEW_W, VIEW_H, GROUND_Y, CEILING_Y,
    PIPE_W, PIPE_SPACING, PIPE_GAP_START, PIPE_GAP_MIN,
    SCROLL_BASE, SCROLL_MAX, MUSHROOM_CHANCE, MUSHROOM_COOLDOWN,
    TRIPLE_DURATION, TRIPLE_MULT, COMBO_WINDOW,
} from './config.js';
import { Bird, Pipe, Coin, Mushroom, Particle, FloatText } from './entities.js';
import { C } from './palette.js';
import { CLOUD, drawText, drawTextCentered, measureText } from './sprites.js';
import { sfx } from './audio.js';
import { FX } from './fx.js';

function lerp(a, b, t) { return a + (b - a) * t; }
function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }

export class World {
    constructor() {
        this.fx = new FX();
        this.reset();
        // Parallax layers (seeded random for mountains + clouds)
        this.clouds = [];
        for (let i = 0; i < 6; i++) {
            this.clouds.push({
                x: Math.random() * VIEW_W,
                y: 20 + Math.random() * 120,
                speed: 0.12 + Math.random() * 0.22,
            });
        }
        this.mountains = this._buildMountains(VIEW_W * 2);
        this.mountainScroll = 0;
        this.groundScroll = 0;
    }

    _buildMountains(width) {
        // Simple seeded noise silhouette.
        const heights = new Array(width);
        let a = 0.6, b = 1.7, c = 3.3;
        for (let x = 0; x < width; x++) {
            const n =
                Math.sin(x * 0.03 + a) * 0.55 +
                Math.sin(x * 0.07 + b) * 0.3 +
                Math.sin(x * 0.17 + c) * 0.15;
            heights[x] = 120 + n * 22;
        }
        return heights;
    }

    reset() {
        this.bird = new Bird();
        this.pipes = [];
        this.coins = [];
        this.mushrooms = [];
        this.particles = [];
        this.floatTexts = [];
        this.score = 0;
        this.coinCount = 0;
        this.combo = 0;
        this.comboTimer = 0;
        this.tripleTimer = 0;
        this.mushroomCooldown = 0;
        this.spawnX = VIEW_W + 40;
        this.elapsed = 0;
        this.gameOver = false;
        this.started = false;
    }

    scrollSpeed() {
        const t = clamp(this.score / 40, 0, 1);
        return lerp(SCROLL_BASE, SCROLL_MAX, t);
    }

    pipeGap() {
        const t = clamp(this.score / 35, 0, 1);
        return Math.round(lerp(PIPE_GAP_START, PIPE_GAP_MIN, t));
    }

    flap() {
        if (this.gameOver) return;
        if (!this.started) this.started = true;
        this.bird.flap();
        // Flap puff particles
        for (let i = 0; i < 3; i++) {
            this.particles.push(new Particle(
                this.bird.x - 4, this.bird.y + 4,
                -20 - Math.random() * 20, 10 + Math.random() * 20,
                0.35, C.CREAM, 1, 0
            ));
        }
        sfx.flap();
    }

    spawnPipeRun() {
        const gap = this.pipeGap();
        const minTop = 22;
        const maxTop = GROUND_Y - gap - 22;
        const gapY = Math.floor(minTop + Math.random() * (maxTop - minTop));
        const pipe = new Pipe(this.spawnX, gapY, gap);
        this.pipes.push(pipe);

        // Spawn collectibles inside/near this gap.
        this._spawnCoinPattern(pipe);

        if (this.mushroomCooldown <= 0 && Math.random() < MUSHROOM_CHANCE) {
            const my = gapY + gap / 2 + (Math.random() * 10 - 5);
            this.mushrooms.push(new Mushroom(this.spawnX + PIPE_W / 2, my));
            this.mushroomCooldown = MUSHROOM_COOLDOWN;
        }

        this.spawnX += PIPE_SPACING;
    }

    _spawnCoinPattern(pipe) {
        const patterns = ['arc', 'line', 'cluster'];
        const kind = patterns[(Math.random() * patterns.length) | 0];
        const cx = pipe.x + PIPE_W / 2;
        const cy = pipe.gapY + pipe.gapH / 2;

        if (kind === 'line') {
            const n = 4 + ((Math.random() * 3) | 0);
            for (let i = 0; i < n; i++) {
                this.coins.push(new Coin(cx - (n - 1) * 5 + i * 10, cy));
            }
        } else if (kind === 'arc') {
            const n = 5;
            for (let i = 0; i < n; i++) {
                const t = i / (n - 1);
                const ax = cx - 18 + t * 36;
                const ay = cy - Math.sin(t * Math.PI) * 18;
                this.coins.push(new Coin(ax, ay));
            }
        } else {
            // cluster: small bunch in the middle
            this.coins.push(new Coin(cx, cy));
            this.coins.push(new Coin(cx - 7, cy - 4));
            this.coins.push(new Coin(cx + 7, cy - 4));
            this.coins.push(new Coin(cx - 7, cy + 4));
            this.coins.push(new Coin(cx + 7, cy + 4));
        }
    }

    update(dt) {
        this.elapsed += dt;
        if (this.started && !this.gameOver) {
            const scroll = this.scrollSpeed();
            // Spawn
            if (this.pipes.length === 0 || this.pipes[this.pipes.length - 1].x < this.spawnX - PIPE_SPACING) {
                this.spawnPipeRun();
            }

            // Move world
            for (const p of this.pipes) p.update(dt, scroll);
            for (const c of this.coins) c.update(dt, scroll);
            for (const m of this.mushrooms) m.update(dt, scroll);
            this.groundScroll = (this.groundScroll + scroll * dt) % 8;
            this.mountainScroll = (this.mountainScroll + scroll * 0.15 * dt);
            for (const cl of this.clouds) {
                cl.x -= scroll * cl.speed * dt;
                if (cl.x < -20) { cl.x = VIEW_W + Math.random() * 40; cl.y = 20 + Math.random() * 120; }
            }
            this.spawnX -= scroll * dt;

            this.mushroomCooldown = Math.max(0, this.mushroomCooldown - dt);
            if (this.tripleTimer > 0) this.tripleTimer = Math.max(0, this.tripleTimer - dt);
            if (this.comboTimer > 0) {
                this.comboTimer -= dt;
                if (this.comboTimer <= 0) this.combo = 0;
            }
        }

        // Bird always updates (even at game-over so it falls).
        this.bird.update(dt);

        // Particles + float texts
        for (const p of this.particles) p.update(dt);
        this.particles = this.particles.filter(p => p.alive);
        for (const t of this.floatTexts) t.update(dt);
        this.floatTexts = this.floatTexts.filter(t => t.alive);

        // Ground / ceiling clamp
        if (this.bird.y + this.bird.r >= GROUND_Y) {
            this.bird.y = GROUND_Y - this.bird.r;
            if (this.started && !this.gameOver) this._kill('ground');
            this.bird.vy = 0;
        }
        if (this.bird.y - this.bird.r < CEILING_Y) {
            this.bird.y = CEILING_Y + this.bird.r;
            if (this.bird.vy < 0) this.bird.vy = 0;
        }

        if (this.started && !this.gameOver) this._collisions();

        // Cleanup
        this.pipes = this.pipes.filter(p => p.x + PIPE_W > -4);
        this.coins = this.coins.filter(c => c.alive && c.x > -10);
        this.mushrooms = this.mushrooms.filter(m => m.alive && m.x > -10);

        this.fx.update(dt);
    }

    _collisions() {
        const b = this.bird;

        // Pipes: check top + bottom of each pipe.
        for (const p of this.pipes) {
            // Score-on-pass
            if (!p.passed && p.x + PIPE_W < b.x) {
                p.passed = true;
                this.score += 1;
                sfx.score();
            }
            const t = p.topRect, bo = p.botRect;
            if (b.hitsRect(t.x, t.y, t.w, t.h) || b.hitsRect(bo.x, bo.y, bo.w, bo.h)) {
                this._kill('pipe');
                return;
            }
        }

        // Coins
        for (const c of this.coins) {
            if (!c.alive) continue;
            if (c.hits(b)) {
                c.alive = false;
                this._collectCoin(c);
            }
        }

        // Mushrooms
        for (const m of this.mushrooms) {
            if (!m.alive) continue;
            if (m.hits(b)) {
                m.alive = false;
                this._collectMushroom(m);
            }
        }
    }

    _collectCoin(c) {
        const mult = this.tripleTimer > 0 ? TRIPLE_MULT : 1;
        const gain = 1 * mult;
        this.score += gain;
        this.coinCount += 1;
        this.combo += 1;
        this.comboTimer = COMBO_WINDOW;

        // Particles
        for (let i = 0; i < 7; i++) {
            const ang = Math.random() * Math.PI * 2;
            const sp = 30 + Math.random() * 50;
            this.particles.push(new Particle(
                c.x, c.y,
                Math.cos(ang) * sp, Math.sin(ang) * sp,
                0.45, i % 2 ? C.GOLD : C.CREAM, 1, 60
            ));
        }
        this.floatTexts.push(new FloatText(c.x, c.y - 6, '+' + gain, mult > 1 ? C.ORANGE : C.GOLD));
        this.fx.flash(C.CREAM, 0.05);
        sfx.coin();
        if (this.combo >= 3) sfx.combo(this.combo);
    }

    _collectMushroom(m) {
        this.tripleTimer = TRIPLE_DURATION;
        this.fx.shake(2, 0.12);
        this.fx.slowTime(0.35, 0.22);
        this.fx.flash(C.ORANGE, 0.12);
        // Radial burst
        for (let i = 0; i < 22; i++) {
            const ang = (i / 22) * Math.PI * 2;
            const sp = 40 + Math.random() * 40;
            this.particles.push(new Particle(
                m.x, m.y,
                Math.cos(ang) * sp, Math.sin(ang) * sp,
                0.7, i % 3 === 0 ? C.WHITE : (i % 2 ? C.ORANGE : C.CREAM), 1, 20
            ));
        }
        this.floatTexts.push(new FloatText(m.x, m.y - 8, '3X POWER!', C.ORANGE));
        sfx.mushroom();
    }

    _kill(reason) {
        if (this.gameOver) return;
        this.gameOver = true;
        this.bird.alive = false;
        this.fx.shake(6, 0.35);
        this.fx.flash(C.CRIMSON, 0.18);
        for (let i = 0; i < 16; i++) {
            const ang = Math.random() * Math.PI * 2;
            const sp = 40 + Math.random() * 60;
            this.particles.push(new Particle(
                this.bird.x, this.bird.y,
                Math.cos(ang) * sp, Math.sin(ang) * sp,
                0.9, i % 2 ? C.CRIMSON : C.ORANGE, 1, 200
            ));
        }
        sfx.hit();
    }
}
