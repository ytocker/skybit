import { C, PAL } from './palette.js';

export class FX {
    constructor() {
        this.shakeMag = 0;
        this.shakeT = 0;
        this.flashT = 0;
        this.flashMax = 0;
        this.flashColor = C.WHITE;
        this.timeScale = 1;
        this.timeScaleT = 0;
    }

    shake(mag, dur) {
        if (mag > this.shakeMag) {
            this.shakeMag = mag;
            this.shakeT = dur;
        }
    }

    flash(color = C.WHITE, dur = 0.08) {
        this.flashColor = color;
        this.flashT = dur;
        this.flashMax = dur;
    }

    slowTime(scale = 0.35, dur = 0.25) {
        this.timeScale = scale;
        this.timeScaleT = dur;
    }

    update(dt) {
        if (this.shakeT > 0) {
            this.shakeT -= dt;
            if (this.shakeT <= 0) { this.shakeT = 0; this.shakeMag = 0; }
        }
        if (this.flashT > 0) this.flashT = Math.max(0, this.flashT - dt);
        if (this.timeScaleT > 0) {
            this.timeScaleT -= dt;
            if (this.timeScaleT <= 0) { this.timeScaleT = 0; this.timeScale = 1; }
        }
    }

    shakeOffset() {
        if (this.shakeMag <= 0) return { x: 0, y: 0 };
        const m = this.shakeMag;
        return {
            x: ((Math.random() * 2 - 1) * m) | 0,
            y: ((Math.random() * 2 - 1) * m) | 0,
        };
    }

    applyFlash(buf) {
        if (this.flashT <= 0 || this.flashMax <= 0) return;
        const k = this.flashT / this.flashMax; // 1 → 0
        const c = PAL[this.flashColor];
        const cr = c & 0xff, cg = (c >> 8) & 0xff, cb = (c >> 16) & 0xff;
        const a = Math.max(0, Math.min(1, k)); // blend factor
        for (let i = 0; i < buf.u32.length; i++) {
            const p = buf.u32[i];
            const r = (p & 0xff) * (1 - a) + cr * a | 0;
            const g = ((p >> 8) & 0xff) * (1 - a) + cg * a | 0;
            const b = ((p >> 16) & 0xff) * (1 - a) + cb * a | 0;
            buf.u32[i] = (0xff << 24) | (b << 16) | (g << 8) | r;
        }
    }
}
