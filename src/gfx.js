import { VIEW_W, VIEW_H } from './config.js';
import { PAL } from './palette.js';

// Offscreen ImageData buffer the whole frame is drawn into as raw pixels.
// Then blitted to the visible canvas once per frame.
export class PixelBuffer {
    constructor(w = VIEW_W, h = VIEW_H) {
        this.w = w;
        this.h = h;
        this.image = new ImageData(w, h);
        this.u32 = new Uint32Array(this.image.data.buffer);
    }

    clear(colorIdx = 0) {
        this.u32.fill(PAL[colorIdx]);
    }

    put(x, y, colorIdx) {
        if (x < 0 || y < 0 || x >= this.w || y >= this.h) return;
        this.u32[(y | 0) * this.w + (x | 0)] = PAL[colorIdx];
    }

    putRaw(x, y, abgr) {
        if (x < 0 || y < 0 || x >= this.w || y >= this.h) return;
        this.u32[(y | 0) * this.w + (x | 0)] = abgr;
    }

    rect(x, y, w, h, colorIdx) {
        const x0 = Math.max(0, x | 0);
        const y0 = Math.max(0, y | 0);
        const x1 = Math.min(this.w, (x + w) | 0);
        const y1 = Math.min(this.h, (y + h) | 0);
        const c = PAL[colorIdx];
        const W = this.w;
        for (let yy = y0; yy < y1; yy++) {
            const row = yy * W;
            for (let xx = x0; xx < x1; xx++) {
                this.u32[row + xx] = c;
            }
        }
    }

    hline(x, y, w, colorIdx) {
        this.rect(x, y, w, 1, colorIdx);
    }

    vline(x, y, h, colorIdx) {
        this.rect(x, y, 1, h, colorIdx);
    }

    // Dithered vertical gradient using 2 colors and Bayer 4x4.
    gradientBand(x, y, w, h, topIdx, botIdx) {
        const x0 = Math.max(0, x | 0);
        const y0 = Math.max(0, y | 0);
        const x1 = Math.min(this.w, (x + w) | 0);
        const y1 = Math.min(this.h, (y + h) | 0);
        const bayer = [
            [ 0,  8,  2, 10],
            [12,  4, 14,  6],
            [ 3, 11,  1,  9],
            [15,  7, 13,  5],
        ];
        const range = y1 - y0;
        for (let yy = y0; yy < y1; yy++) {
            const t = (yy - y0) / Math.max(1, range - 1);
            for (let xx = x0; xx < x1; xx++) {
                const bx = xx & 3, by = yy & 3;
                const thresh = (bayer[by][bx] + 0.5) / 16;
                const use = t > thresh ? botIdx : topIdx;
                this.u32[yy * this.w + xx] = PAL[use];
            }
        }
    }

    // Blit a sprite described by { w, h, data: Int8Array of palette indices, -1 = transparent }.
    blit(sprite, dx, dy, flipX = false, tint = -1) {
        const { w, h, data } = sprite;
        const sx0 = 0, sy0 = 0;
        for (let j = 0; j < h; j++) {
            const yy = dy + j;
            if (yy < 0 || yy >= this.h) continue;
            for (let i = 0; i < w; i++) {
                const xx = dx + (flipX ? (w - 1 - i) : i);
                if (xx < 0 || xx >= this.w) continue;
                const idx = data[(sy0 + j) * w + (sx0 + i)];
                if (idx < 0) continue;
                this.u32[yy * this.w + xx] = PAL[tint >= 0 ? tint : idx];
            }
        }
    }

    // Draw a filled circle (pixel art, no AA).
    disc(cx, cy, r, colorIdx) {
        const r2 = r * r;
        const x0 = Math.max(0, (cx - r) | 0);
        const y0 = Math.max(0, (cy - r) | 0);
        const x1 = Math.min(this.w, (cx + r + 1) | 0);
        const y1 = Math.min(this.h, (cy + r + 1) | 0);
        const c = PAL[colorIdx];
        for (let yy = y0; yy < y1; yy++) {
            const dy = yy - cy;
            for (let xx = x0; xx < x1; xx++) {
                const dx = xx - cx;
                if (dx * dx + dy * dy <= r2) {
                    this.u32[yy * this.w + xx] = c;
                }
            }
        }
    }

    // 1-pixel circle outline.
    ring(cx, cy, r, colorIdx) {
        let x = r, y = 0, err = 0;
        while (x >= y) {
            this.put(cx + x, cy + y, colorIdx);
            this.put(cx + y, cy + x, colorIdx);
            this.put(cx - y, cy + x, colorIdx);
            this.put(cx - x, cy + y, colorIdx);
            this.put(cx - x, cy - y, colorIdx);
            this.put(cx - y, cy - x, colorIdx);
            this.put(cx + y, cy - x, colorIdx);
            this.put(cx + x, cy - y, colorIdx);
            y++;
            err += 1 + 2 * y;
            if (2 * (err - x) + 1 > 0) { x--; err += 1 - 2 * x; }
        }
    }

    // Scanline overlay: darken every other row.
    scanlines(intensityIdx = 0, stride = 2) {
        for (let y = 0; y < this.h; y += stride) {
            for (let x = 0; x < this.w; x++) {
                const p = this.u32[y * this.w + x];
                // Multiply RGB by ~0.78 (shift-based approximation).
                const r = (p & 0xff) * 0.78 | 0;
                const g = ((p >> 8) & 0xff) * 0.78 | 0;
                const b = ((p >> 16) & 0xff) * 0.78 | 0;
                this.u32[y * this.w + x] = (0xff << 24) | (b << 16) | (g << 8) | r;
            }
        }
    }

    // Soft circular vignette (darkens corners).
    vignette(strength = 0.35) {
        const cx = this.w / 2, cy = this.h / 2;
        const maxD = Math.hypot(cx, cy);
        for (let y = 0; y < this.h; y++) {
            for (let x = 0; x < this.w; x++) {
                const d = Math.hypot(x - cx, y - cy) / maxD;
                if (d < 0.55) continue;
                const f = 1 - Math.min(1, (d - 0.55) / 0.45) * strength;
                const i = y * this.w + x;
                const p = this.u32[i];
                const r = (p & 0xff) * f | 0;
                const g = ((p >> 8) & 0xff) * f | 0;
                const b = ((p >> 16) & 0xff) * f | 0;
                this.u32[i] = (0xff << 24) | (b << 16) | (g << 8) | r;
            }
        }
    }
}

// Fit the visible canvas to the viewport at an integer scale.
export function fitCanvasToViewport(canvas) {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const scale = Math.max(1, Math.floor(Math.min(vw / VIEW_W, vh / VIEW_H)));
    canvas.style.width = (VIEW_W * scale) + 'px';
    canvas.style.height = (VIEW_H * scale) + 'px';
    return scale;
}
