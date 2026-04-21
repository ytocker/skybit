import {
    GRAVITY, FLAP_V, MAX_FALL, BIRD_X, BIRD_R, GROUND_Y,
    PIPE_W, COIN_R,
} from './config.js';
import { C } from './palette.js';
import { BIRD_FRAMES, COIN_FRAMES, MUSHROOM, PIPE_BODY, PIPE_CAP_28 } from './sprites.js';

export class Bird {
    constructor() {
        this.x = BIRD_X;
        this.y = 140;
        this.vy = 0;
        this.r = BIRD_R;
        this.alive = true;
        this.animT = 0;
        this.trail = [];
        this.flapPulse = 0; // non-zero briefly after a flap (for bigger wing)
    }

    reset() {
        this.x = BIRD_X; this.y = 140; this.vy = 0;
        this.alive = true; this.animT = 0; this.trail = []; this.flapPulse = 0;
    }

    flap() {
        if (!this.alive) return;
        this.vy = FLAP_V;
        this.flapPulse = 0.12;
    }

    update(dt) {
        this.vy += GRAVITY * dt;
        if (this.vy > MAX_FALL) this.vy = MAX_FALL;
        this.y += this.vy * dt;
        this.animT += dt;
        if (this.flapPulse > 0) this.flapPulse -= dt;

        // Trail
        this.trail.push({ x: this.x, y: this.y });
        if (this.trail.length > 8) this.trail.shift();
    }

    frame() {
        // Fast flutter; force wing-down when falling fast.
        if (this.vy > 180) return 2;
        const t = this.animT;
        const f = Math.floor(t * 14) % 3;
        return f;
    }

    angle() {
        // Nose tilt based on vy: up when flapping, down when diving.
        const a = this.vy / 380;
        return Math.max(-0.5, Math.min(1.0, a));
    }

    draw(buf) {
        // Draw trail first (4-point low-alpha ghost circles).
        for (let i = 0; i < this.trail.length; i++) {
            const p = this.trail[i];
            const k = i / this.trail.length;
            if (k < 0.4) continue;
            const r = 2 + k * 2;
            buf.disc(p.x, p.y, r, k > 0.8 ? C.CREAM : C.DUSK);
        }
        const spr = BIRD_FRAMES[this.frame()];
        buf.blit(spr, Math.round(this.x - spr.w / 2), Math.round(this.y - spr.h / 2));
    }

    // Bounding circle hit test used against pipes / ground.
    hitsRect(rx, ry, rw, rh) {
        const cx = Math.max(rx, Math.min(this.x, rx + rw));
        const cy = Math.max(ry, Math.min(this.y, ry + rh));
        const dx = this.x - cx, dy = this.y - cy;
        return (dx * dx + dy * dy) <= this.r * this.r;
    }
}

export class Pipe {
    constructor(x, gapY, gapH) {
        this.x = x;                // left edge
        this.gapY = gapY;          // top of the gap
        this.gapH = gapH;
        this.passed = false;
        this.spawnIndex = 0;       // used to avoid double-spawning collectibles
        this.w = PIPE_W;
    }

    get topRect() { return { x: this.x, y: 0, w: this.w, h: this.gapY }; }
    get botRect() { return { x: this.x, y: this.gapY + this.gapH, w: this.w, h: GROUND_Y - (this.gapY + this.gapH) }; }

    update(dt, scrollSpeed) {
        this.x -= scrollSpeed * dt;
    }

    draw(buf) {
        const topH = this.gapY;
        const botY = this.gapY + this.gapH;
        const botH = GROUND_Y - botY;

        // Top pipe body (descending) then cap at the bottom of this segment.
        const bodyTopH = Math.max(0, topH - PIPE_CAP_28.h);
        for (let y = 0; y < bodyTopH; y++) {
            // repeat the 1-row body
            for (let i = 0; i < PIPE_BODY.w; i++) {
                const ci = PIPE_BODY.data[i];
                if (ci < 0) continue;
                buf.put(this.x + i, y, ci);
            }
        }
        if (topH >= PIPE_CAP_28.h) {
            buf.blit(PIPE_CAP_28, this.x, bodyTopH);
        }

        // Bottom pipe: cap first, body below.
        if (botH >= PIPE_CAP_28.h) {
            buf.blit(PIPE_CAP_28, this.x, botY);
            for (let y = botY + PIPE_CAP_28.h; y < GROUND_Y; y++) {
                for (let i = 0; i < PIPE_BODY.w; i++) {
                    const ci = PIPE_BODY.data[i];
                    if (ci < 0) continue;
                    buf.put(this.x + i, y, ci);
                }
            }
        }
    }
}

export class Coin {
    constructor(x, y) {
        this.x = x; this.y = y;
        this.r = COIN_R;
        this.alive = true;
        this.t = Math.random() * 10;
        this.bobY = 0;
    }

    update(dt, scrollSpeed) {
        this.x -= scrollSpeed * dt;
        this.t += dt;
        this.bobY = Math.sin(this.t * 4) * 1.2;
    }

    draw(buf) {
        const frame = Math.floor(this.t * 8) % COIN_FRAMES.length;
        const spr = COIN_FRAMES[frame];
        buf.blit(spr, Math.round(this.x - spr.w / 2), Math.round(this.y + this.bobY - spr.h / 2));
    }

    hits(bird) {
        const dx = this.x - bird.x;
        const dy = this.y + this.bobY - bird.y;
        const rr = this.r + bird.r;
        return dx * dx + dy * dy <= rr * rr;
    }
}

export class Mushroom {
    constructor(x, y) {
        this.x = x; this.y = y;
        this.r = 6;
        this.alive = true;
        this.t = 0;
    }

    update(dt, scrollSpeed) {
        this.x -= scrollSpeed * dt;
        this.t += dt;
    }

    draw(buf) {
        // Gentle bob + a faint halo ring that pulses.
        const bob = Math.sin(this.t * 3) * 1.5;
        const r = 9 + Math.sin(this.t * 4) * 1.2;
        buf.ring(this.x, this.y + bob, r, C.CREAM);
        buf.ring(this.x, this.y + bob, r + 2, C.ORANGE);
        buf.blit(MUSHROOM, Math.round(this.x - MUSHROOM.w / 2), Math.round(this.y + bob - MUSHROOM.h / 2));
    }

    hits(bird) {
        const dx = this.x - bird.x;
        const dy = this.y - bird.y;
        const rr = this.r + bird.r;
        return dx * dx + dy * dy <= rr * rr;
    }
}

export class Particle {
    constructor(x, y, vx, vy, life, color, size = 1, gravity = 0) {
        this.x = x; this.y = y;
        this.vx = vx; this.vy = vy;
        this.life = life; this.maxLife = life;
        this.color = color;
        this.size = size;
        this.gravity = gravity;
        this.alive = true;
    }

    update(dt) {
        this.life -= dt;
        if (this.life <= 0) { this.alive = false; return; }
        this.vy += this.gravity * dt;
        this.x += this.vx * dt;
        this.y += this.vy * dt;
    }

    draw(buf) {
        if (this.size <= 1) buf.put(this.x, this.y, this.color);
        else buf.rect(this.x - (this.size / 2 | 0), this.y - (this.size / 2 | 0), this.size, this.size, this.color);
    }
}

// Floating "+1" / "+3" labels.
export class FloatText {
    constructor(x, y, text, color) {
        this.x = x; this.y = y;
        this.text = text;
        this.color = color;
        this.life = 0.7;
        this.maxLife = 0.7;
        this.alive = true;
    }

    update(dt) {
        this.life -= dt;
        this.y -= 22 * dt;
        if (this.life <= 0) this.alive = false;
    }
}
