// Generates pixel-art screenshot PNGs for the README by re-using the game's
// sprite + palette + gfx modules. Run with: node tools/snapshot.mjs
// Shims: ImageData (browser-only) + zero-dep PNG encoder.

import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

// --- ImageData shim (required by gfx.js) ---
globalThis.ImageData = class {
    constructor(w, h) {
        this.width = w;
        this.height = h;
        this.data = new Uint8ClampedArray(w * h * 4);
    }
};

const { PixelBuffer } = await import('../src/gfx.js');
const { C, PAL } = await import('../src/palette.js');
const {
    BIRD_FRAMES, COIN_FRAMES, MUSHROOM,
    PIPE_BODY, PIPE_CAP_28, CLOUD,
    drawText, drawTextCentered, measureText,
} = await import('../src/sprites.js');
const { VIEW_W, VIEW_H, GROUND_Y, PIPE_W } = await import('../src/config.js');

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outDir = path.resolve(__dirname, '..', 'docs', 'screenshots');
fs.mkdirSync(outDir, { recursive: true });

// ---------- Scene helpers (mirror scenes.js) ----------
function drawSky(buf, t = 0) {
    buf.gradientBand(0, 0, buf.w, 70, C.INDIGO, C.DUSK);
    buf.gradientBand(0, 70, buf.w, 80, C.DUSK, C.SKY);
    buf.gradientBand(0, 150, buf.w, GROUND_Y - 150, C.SKY, C.CREAM);
    const sx = 140, sy = 60;
    buf.disc(sx, sy, 10, C.CREAM);
    buf.disc(sx, sy, 8, C.GOLD);
    buf.disc(sx, sy, 5, C.ORANGE);
    buf.ring(sx, sy, 13, C.GOLD);
}

function buildMountains(width) {
    const heights = new Array(width);
    let a = 0.6, b = 1.7, c = 3.3;
    for (let x = 0; x < width; x++) {
        const n = Math.sin(x * 0.03 + a) * 0.55 + Math.sin(x * 0.07 + b) * 0.3 + Math.sin(x * 0.17 + c) * 0.15;
        heights[x] = 120 + n * 22;
    }
    return heights;
}

function drawMountains(buf, mountains, scroll) {
    const len = mountains.length;
    for (let x = 0; x < buf.w; x++) {
        const idx = (x + Math.floor(scroll * 0.5)) % len;
        const h = mountains[idx];
        buf.rect(x, GROUND_Y - h, 1, h, C.INDIGO);
    }
    for (let x = 0; x < buf.w; x++) {
        const idx = (x + Math.floor(scroll * 0.9) + 40) % len;
        const h = mountains[idx] * 0.75;
        buf.rect(x, GROUND_Y - h, 1, h, C.NAVY);
    }
}

function drawClouds(buf, clouds) {
    for (const c of clouds) buf.blit(CLOUD, c.x | 0, c.y | 0);
}

function drawGround(buf, scroll) {
    buf.rect(0, GROUND_Y, buf.w, VIEW_H - GROUND_Y, C.WOOD);
    buf.rect(0, GROUND_Y, buf.w, 4, C.GRASS);
    buf.rect(0, GROUND_Y + 2, buf.w, 1, C.LEAF);
    const off = (scroll | 0) % 8;
    for (let x = -off; x < buf.w; x += 8) {
        buf.put(x + 1, GROUND_Y - 1, C.LIME);
        buf.put(x + 5, GROUND_Y - 1, C.LIME);
    }
    for (let y = GROUND_Y + 6; y < VIEW_H; y += 6) {
        for (let x = -((scroll * 1.2) | 0) % 10; x < buf.w; x += 10) {
            buf.put(x + 3, y, C.AMBER);
        }
    }
}

function drawPipe(buf, x, gapY, gapH) {
    const topH = gapY;
    const botY = gapY + gapH;
    const bodyTopH = Math.max(0, topH - PIPE_CAP_28.h);
    for (let y = 0; y < bodyTopH; y++) {
        for (let i = 0; i < PIPE_BODY.w; i++) {
            const ci = PIPE_BODY.data[i];
            if (ci < 0) continue;
            buf.put(x + i, y, ci);
        }
    }
    if (topH >= PIPE_CAP_28.h) buf.blit(PIPE_CAP_28, x, bodyTopH);
    if (GROUND_Y - botY >= PIPE_CAP_28.h) {
        buf.blit(PIPE_CAP_28, x, botY);
        for (let y = botY + PIPE_CAP_28.h; y < GROUND_Y; y++) {
            for (let i = 0; i < PIPE_BODY.w; i++) {
                const ci = PIPE_BODY.data[i];
                if (ci < 0) continue;
                buf.put(x + i, y, ci);
            }
        }
    }
}

function drawBird(buf, x, y, frame = 1) {
    const spr = BIRD_FRAMES[frame % BIRD_FRAMES.length];
    buf.blit(spr, Math.round(x - spr.w / 2), Math.round(y - spr.h / 2));
}

function drawCoin(buf, x, y, frame = 0) {
    const spr = COIN_FRAMES[frame % COIN_FRAMES.length];
    buf.blit(spr, Math.round(x - spr.w / 2), Math.round(y - spr.h / 2));
}

function drawMushroom(buf, x, y, t = 0) {
    const bob = Math.sin(t * 3) * 1.5;
    const r = 9 + Math.sin(t * 4) * 1.2;
    buf.ring(x, y + bob, r, C.CREAM);
    buf.ring(x, y + bob, r + 2, C.ORANGE);
    buf.blit(MUSHROOM, Math.round(x - MUSHROOM.w / 2), Math.round(y + bob - MUSHROOM.h / 2));
}

function drawTrail(buf, points) {
    for (let i = 0; i < points.length; i++) {
        const p = points[i];
        const k = i / points.length;
        if (k < 0.4) continue;
        const r = 2 + k * 2;
        buf.disc(p.x, p.y, r, k > 0.8 ? C.CREAM : C.DUSK);
    }
}

function drawTitle(buf) {
    const y = 64;
    const title = 'SKYBIT';
    const w = measureText(title, 3);
    const x = ((VIEW_W - w) / 2) | 0;
    drawText(buf, title, x + 2, y + 2, C.NIGHT, 3);
    drawText(buf, title, x, y, C.ORANGE, 3);
    drawText(buf, title, x + 1, y - 1, C.GOLD, 3);
    const sub = 'A RETRO PIXEL FLYER';
    drawTextCentered(buf, sub, y + 24, C.NIGHT);
    drawTextCentered(buf, sub, y + 23, C.CREAM);
}

function drawStartHint(buf) {
    const y1 = 180, y2 = 196;
    drawTextCentered(buf, 'TAP TO FLAP', y1, C.NIGHT);
    drawTextCentered(buf, 'TAP TO FLAP', y1 - 1, C.WHITE);
    drawTextCentered(buf, 'COLLECT COINS', y2, C.NIGHT);
    drawTextCentered(buf, 'COLLECT COINS', y2 - 1, C.GOLD);
    drawTextCentered(buf, 'GRAB THE MUSHROOM FOR 3X!', y2 + 12, C.NIGHT);
    drawTextCentered(buf, 'GRAB THE MUSHROOM FOR 3X!', y2 + 11, C.ORANGE);
}

function drawHUD(buf, score, high, coins, tripleT = 0, combo = 0) {
    const s = String(score);
    const w = measureText(s, 2);
    const sx = ((VIEW_W - w) / 2) | 0;
    drawText(buf, s, sx + 1, 11, C.NIGHT, 2);
    drawText(buf, s, sx, 10, C.WHITE, 2);

    const hs = 'HI ' + String(high);
    drawText(buf, hs, 6, 6, C.NIGHT);
    drawText(buf, hs, 5, 5, C.CREAM);

    const cs = 'x' + String(coins);
    const cw = measureText(cs);
    drawText(buf, cs, VIEW_W - cw - 7, 6, C.NIGHT);
    drawText(buf, cs, VIEW_W - cw - 8, 5, C.GOLD);
    buf.disc(VIEW_W - cw - 12, 7, 2, C.GOLD);
    buf.put(VIEW_W - cw - 12, 6, C.CREAM);

    // Pause button
    const px = VIEW_W - 16, py = 16;
    buf.rect(px, py, 12, 12, C.NIGHT);
    buf.rect(px + 1, py + 1, 10, 10, C.DUSK);
    buf.rect(px + 3, py + 3, 2, 6, C.CREAM);
    buf.rect(px + 7, py + 3, 2, 6, C.CREAM);

    if (tripleT > 0) {
        const bw = 80, bh = 5;
        const bx = ((VIEW_W - bw) / 2) | 0;
        const by = 26;
        buf.rect(bx - 1, by - 1, bw + 2, bh + 2, C.NIGHT);
        buf.rect(bx, by, bw, bh, C.NAVY);
        buf.rect(bx, by, (bw * tripleT) | 0, bh, C.ORANGE);
        const label = '3X POWER';
        drawText(buf, label, ((VIEW_W - measureText(label)) / 2) | 0, by - 7, C.CREAM);
    }

    if (combo >= 2) {
        const label = 'X' + combo + ' COMBO';
        const lw = measureText(label);
        const ly = 270;
        const lx = ((VIEW_W - lw) / 2) | 0;
        drawText(buf, label, lx + 1, ly + 1, C.NIGHT);
        drawText(buf, label, lx, ly, C.ORANGE);
    }
}

function scanlines(buf) { buf.scanlines(0, 2); }
function vignette(buf) { buf.vignette(0.35); }

// ---------- PNG encoder (zero-dep) ----------
function crc32Table() {
    const t = new Uint32Array(256);
    for (let n = 0; n < 256; n++) {
        let c = n;
        for (let k = 0; k < 8; k++) c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
        t[n] = c >>> 0;
    }
    return t;
}
const CRC_TBL = crc32Table();
function crc32(buf) {
    let c = 0xffffffff >>> 0;
    for (let i = 0; i < buf.length; i++) c = CRC_TBL[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
    return (c ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
    const len = Buffer.alloc(4); len.writeUInt32BE(data.length, 0);
    const t = Buffer.from(type, 'ascii');
    const crc = Buffer.alloc(4);
    crc.writeUInt32BE(crc32(Buffer.concat([t, data])), 0);
    return Buffer.concat([len, t, data, crc]);
}
function writePNG(filepath, w, h, u32) {
    const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
    const ihdr = Buffer.alloc(13);
    ihdr.writeUInt32BE(w, 0);
    ihdr.writeUInt32BE(h, 4);
    ihdr[8] = 8; ihdr[9] = 6; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
    const row = 1 + w * 4;
    const raw = Buffer.alloc(h * row);
    for (let y = 0; y < h; y++) {
        raw[y * row] = 0;
        for (let x = 0; x < w; x++) {
            const p = u32[y * w + x];
            const off = y * row + 1 + x * 4;
            raw[off + 0] = p & 0xff;
            raw[off + 1] = (p >> 8) & 0xff;
            raw[off + 2] = (p >> 16) & 0xff;
            raw[off + 3] = (p >>> 24) & 0xff;
        }
    }
    const idat = zlib.deflateSync(raw);
    const out = Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
    fs.writeFileSync(filepath, out);
}

function upscale(buf, scale) {
    const w = buf.w, h = buf.h;
    const W = w * scale, H = h * scale;
    const out = new Uint32Array(W * H);
    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            const p = buf.u32[y * w + x];
            for (let sy = 0; sy < scale; sy++) {
                for (let sx = 0; sx < scale; sx++) {
                    out[(y * scale + sy) * W + (x * scale + sx)] = p;
                }
            }
        }
    }
    return { w: W, h: H, u32: out };
}

// ---------- Scenes to snapshot ----------
const mountains = buildMountains(VIEW_W * 2);

function sceneTitle() {
    const buf = new PixelBuffer(VIEW_W, VIEW_H);
    buf.clear(C.NIGHT);
    drawSky(buf);
    const clouds = [
        { x: 20, y: 40 }, { x: 90, y: 70 }, { x: 150, y: 30 }, { x: 60, y: 110 },
    ];
    drawClouds(buf, clouds);
    drawMountains(buf, mountains, 20);
    drawGround(buf, 0);
    // Bird hovering in center (menu preview).
    drawBird(buf, 56, 150, 1);
    // A coin and a mushroom to show what you collect
    drawCoin(buf, 104, 158, 0);
    drawCoin(buf, 118, 150, 2);
    drawMushroom(buf, 140, 176, 0.6);
    drawTitle(buf);
    drawStartHint(buf);
    scanlines(buf); vignette(buf);
    return buf;
}

function sceneGameplay() {
    const buf = new PixelBuffer(VIEW_W, VIEW_H);
    buf.clear(C.NIGHT);
    drawSky(buf);
    const clouds = [
        { x: 30, y: 50 }, { x: 110, y: 90 }, { x: 160, y: 40 },
    ];
    drawClouds(buf, clouds);
    drawMountains(buf, mountains, 60);
    drawGround(buf, 30);
    // Two pipes with a coin arc in between.
    drawPipe(buf, 90, 100, 86);
    drawPipe(buf, 90 + 150 - 60, 60, 86); // barely onscreen second pipe peeking
    // Coin arc through the gap
    const cx = 90 + 14, cy = 143;
    for (let i = 0; i < 5; i++) {
        const t = i / 4;
        drawCoin(buf, cx - 18 + t * 36, cy - Math.sin(t * Math.PI) * 18, i);
    }
    // Bird with trail mid-flap
    const trail = [
        { x: 42, y: 146 }, { x: 45, y: 144 }, { x: 48, y: 142 },
        { x: 51, y: 141 }, { x: 53, y: 141 },
    ];
    drawTrail(buf, trail);
    drawBird(buf, 56, 140, 1);
    // HUD: score 7, hi 23, coins 5, combo 3
    drawHUD(buf, 7, 23, 5, 0, 3);
    scanlines(buf); vignette(buf);
    return buf;
}

function sceneMushroom() {
    const buf = new PixelBuffer(VIEW_W, VIEW_H);
    buf.clear(C.NIGHT);
    drawSky(buf);
    const clouds = [{ x: 14, y: 60 }, { x: 130, y: 80 }];
    drawClouds(buf, clouds);
    drawMountains(buf, mountains, 110);
    drawGround(buf, 60);

    drawPipe(buf, 100, 80, 82);
    // Coins line above the bird
    for (let i = 0; i < 6; i++) drawCoin(buf, 70 + i * 10, 120, (i + 1) % 4);

    // Mushroom just collected — show sparkles as particles around bird
    const bx = 56, by = 150;
    // aura
    buf.ring(bx, by, 11, C.ORANGE);
    buf.ring(bx, by, 13, C.GOLD);
    // sparkles
    for (let i = 0; i < 20; i++) {
        const a = (i / 20) * Math.PI * 2;
        const r = 16 + (i % 3) * 3;
        const px = bx + Math.cos(a) * r | 0;
        const py = by + Math.sin(a) * r | 0;
        const col = i % 3 === 0 ? C.WHITE : (i % 2 ? C.ORANGE : C.CREAM);
        buf.put(px, py, col);
    }
    const trail = [
        { x: 44, y: 154 }, { x: 47, y: 152 }, { x: 50, y: 151 }, { x: 53, y: 150 },
    ];
    drawTrail(buf, trail);
    drawBird(buf, bx, by, 0);

    // "+3" float text (as if coin just collected during 3X)
    drawText(buf, '+3', 110, 114, C.NIGHT);
    drawText(buf, '+3', 109, 113, C.ORANGE);

    // HUD with triple timer and combo
    drawHUD(buf, 42, 23, 18, 0.62, 5);
    scanlines(buf); vignette(buf);
    return buf;
}

function sceneGameOver() {
    const buf = new PixelBuffer(VIEW_W, VIEW_H);
    buf.clear(C.NIGHT);
    drawSky(buf);
    drawClouds(buf, [{ x: 30, y: 70 }, { x: 130, y: 100 }]);
    drawMountains(buf, mountains, 200);
    drawGround(buf, 100);
    drawPipe(buf, 110, 130, 70);

    // Bird tilted face-down near ground
    drawBird(buf, 56, 240, 2);

    // Game Over card
    const y = 100;
    const t = 'GAME OVER';
    const w = measureText(t, 2);
    const x = ((VIEW_W - w) / 2) | 0;
    drawText(buf, t, x + 2, y + 2, C.NIGHT, 2);
    drawText(buf, t, x, y, C.CRIMSON, 2);
    drawTextCentered(buf, 'SCORE 42', y + 23, C.WHITE);
    drawTextCentered(buf, 'BEST  42', y + 37, C.GOLD);
    drawTextCentered(buf, 'NEW BEST!', y + 53, C.ORANGE);
    drawTextCentered(buf, 'TAP TO RETRY', y + 81, C.CREAM);

    drawHUD(buf, 42, 42, 18, 0, 0);
    scanlines(buf); vignette(buf);
    return buf;
}

function save(name, buf, scale = 3) {
    const up = upscale(buf, scale);
    const p = path.join(outDir, name);
    writePNG(p, up.w, up.h, up.u32);
    console.log('wrote', p, up.w + 'x' + up.h);
}

save('title.png', sceneTitle(), 3);
save('gameplay.png', sceneGameplay(), 3);
save('mushroom.png', sceneMushroom(), 3);
save('gameover.png', sceneGameOver(), 3);

console.log('done');
