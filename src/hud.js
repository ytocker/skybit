import { VIEW_W, VIEW_H, TRIPLE_DURATION } from './config.js';
import { C } from './palette.js';
import { drawText, drawTextCentered, measureText } from './sprites.js';

export function drawHUD(buf, world, highScore) {
    // Score (big, top-center)
    const s = String(world.score);
    const w = measureText(s, 2);
    const sx = ((VIEW_W - w) / 2) | 0;
    drawText(buf, s, sx + 1, 11, C.NIGHT, 2);
    drawText(buf, s, sx, 10, C.WHITE, 2);

    // High score (top-left)
    const hs = 'HI ' + String(highScore);
    drawText(buf, hs, 6, 6, C.NIGHT);
    drawText(buf, hs, 5, 5, C.CREAM);

    // Coins (top-right)
    const cs = 'x' + String(world.coinCount);
    const cw = measureText(cs);
    drawText(buf, cs, VIEW_W - cw - 7, 6, C.NIGHT);
    drawText(buf, cs, VIEW_W - cw - 8, 5, C.GOLD);
    // tiny coin icon next to count
    buf.disc(VIEW_W - cw - 12, 7, 2, C.GOLD);
    buf.put(VIEW_W - cw - 12, 6, C.CREAM);

    // Pause button (top-right corner, below coin)
    const pr = { x: VIEW_W - 16, y: 16, w: 12, h: 12 };
    buf.rect(pr.x, pr.y, pr.w, pr.h, C.NIGHT);
    buf.rect(pr.x + 1, pr.y + 1, pr.w - 2, pr.h - 2, C.DUSK);
    buf.rect(pr.x + 3, pr.y + 3, 2, 6, C.CREAM);
    buf.rect(pr.x + 7, pr.y + 3, 2, 6, C.CREAM);

    // Triple power timer bar.
    if (world.tripleTimer > 0) {
        const bw = 80, bh = 5;
        const bx = ((VIEW_W - bw) / 2) | 0;
        const by = 26;
        buf.rect(bx - 1, by - 1, bw + 2, bh + 2, C.NIGHT);
        buf.rect(bx, by, bw, bh, C.NAVY);
        const fill = Math.max(0, Math.min(1, world.tripleTimer / TRIPLE_DURATION));
        buf.rect(bx, by, (bw * fill) | 0, bh, C.ORANGE);
        const label = '3X POWER';
        drawText(buf, label, ((VIEW_W - measureText(label)) / 2) | 0, by - 7, C.CREAM);
    }

    // Combo badge (bottom-center when combo >= 2)
    if (world.combo >= 2) {
        const label = 'X' + world.combo + ' COMBO';
        const lw = measureText(label);
        const ly = 270;
        const lx = ((VIEW_W - lw) / 2) | 0;
        drawText(buf, label, lx + 1, ly + 1, C.NIGHT);
        drawText(buf, label, lx, ly, C.ORANGE);
    }

    // Float texts (coin pickup "+1")
    for (const t of world.floatTexts) {
        const lw = measureText(t.text);
        const fx = (t.x - lw / 2) | 0;
        const fy = t.y | 0;
        drawText(buf, t.text, fx + 1, fy + 1, C.NIGHT);
        drawText(buf, t.text, fx, fy, t.color);
    }

    return pr; // report pause-button hit rect for input.
}

export function drawStartHint(buf) {
    const y1 = 180, y2 = 196;
    drawTextCentered(buf, 'TAP TO FLAP', y1, C.NIGHT);
    drawTextCentered(buf, 'TAP TO FLAP', y1 - 1, C.WHITE);
    drawTextCentered(buf, 'COLLECT COINS', y2, C.NIGHT);
    drawTextCentered(buf, 'COLLECT COINS', y2 - 1, C.GOLD);
    drawTextCentered(buf, 'GRAB THE MUSHROOM FOR 3X!', y2 + 12, C.NIGHT);
    drawTextCentered(buf, 'GRAB THE MUSHROOM FOR 3X!', y2 + 11, C.ORANGE);
}

export function drawTitle(buf, t) {
    // Animated title: bounces a bit.
    const bob = Math.round(Math.sin(t * 2.4) * 2);
    const y = 64 + bob;
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

export function drawGameOver(buf, score, high, best) {
    const y = 100;
    const t = 'GAME OVER';
    const w = measureText(t, 2);
    const x = ((VIEW_W - w) / 2) | 0;
    drawText(buf, t, x + 2, y + 2, C.NIGHT, 2);
    drawText(buf, t, x, y, C.CRIMSON, 2);

    drawTextCentered(buf, 'SCORE ' + score, y + 24, C.NIGHT);
    drawTextCentered(buf, 'SCORE ' + score, y + 23, C.WHITE);
    drawTextCentered(buf, 'BEST  ' + high, y + 38, C.NIGHT);
    drawTextCentered(buf, 'BEST  ' + high, y + 37, C.GOLD);

    if (best) {
        drawTextCentered(buf, 'NEW BEST!', y + 54, C.NIGHT);
        drawTextCentered(buf, 'NEW BEST!', y + 53, C.ORANGE);
    }

    drawTextCentered(buf, 'TAP TO RETRY', y + 82, C.NIGHT);
    drawTextCentered(buf, 'TAP TO RETRY', y + 81, C.CREAM);
}
