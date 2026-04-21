// AAP-16 style palette by Adigun Polack (public domain) — slightly tuned for this game.
// Colors are provided as #RRGGBB; at init we convert to 0xAABBGGRR for ImageData writes.
const HEX = [
    '#0b1220', // 0  deep night
    '#1c2943', // 1  night blue
    '#3a4e7a', // 2  muted indigo
    '#6686b9', // 3  dusk blue
    '#a8d5ff', // 4  sky cyan
    '#ffe7a8', // 5  cream highlight
    '#ffc24b', // 6  gold
    '#ff7a3d', // 7  orange
    '#c53a3a', // 8  crimson
    '#7a2a6b', // 9  plum
    '#2c7d4f', // 10 leaf green
    '#6bc15a', // 11 grass green
    '#b8e06a', // 12 light green
    '#5a3a21', // 13 dark wood
    '#a56b3c', // 14 amber wood
    '#f3f4f0', // 15 off-white
];

export const PAL = HEX.map(hexToABGR);

// Named indices for clarity.
export const C = {
    NIGHT: 0, NAVY: 1, INDIGO: 2, DUSK: 3, SKY: 4,
    CREAM: 5, GOLD: 6, ORANGE: 7, CRIMSON: 8, PLUM: 9,
    LEAF: 10, GRASS: 11, LIME: 12, WOOD: 13, AMBER: 14, WHITE: 15
};

export function hexToABGR(hex) {
    const n = parseInt(hex.slice(1), 16);
    const r = (n >> 16) & 0xff;
    const g = (n >> 8) & 0xff;
    const b = n & 0xff;
    return (0xff << 24) | (b << 16) | (g << 8) | r;
}

export function rgba(r, g, b, a = 255) {
    return ((a & 0xff) << 24) | ((b & 0xff) << 16) | ((g & 0xff) << 8) | (r & 0xff);
}

export function lerpColor(iA, iB, t) {
    const a = PAL[iA], b = PAL[iB];
    const ar = a & 0xff, ag = (a >> 8) & 0xff, ab = (a >> 16) & 0xff;
    const br = b & 0xff, bg = (b >> 8) & 0xff, bb = (b >> 16) & 0xff;
    const r = Math.round(ar + (br - ar) * t);
    const g = Math.round(ag + (bg - ag) * t);
    const bl = Math.round(ab + (bb - ab) * t);
    return rgba(r, g, bl);
}
