import { C } from './palette.js';

// Compact sprite maker: takes a string grid and a key string, returns { w, h, data }.
// '.' = transparent; any other char looks up in `key` to a palette index.
function makeSprite(rows, key) {
    const h = rows.length;
    const w = rows[0].length;
    const data = new Int8Array(w * h);
    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            const ch = rows[y][x];
            if (ch === '.') { data[y * w + x] = -1; continue; }
            const k = key.indexOf(ch);
            data[y * w + x] = k === -1 ? -1 : keyToPal(key[k]);
        }
    }
    return { w, h, data };
}

// Key char → palette index. We use a tiny scheme so sprite strings stay readable.
function keyToPal(ch) {
    switch (ch) {
        case 'K': return C.NIGHT;      // black-ish outline
        case 'N': return C.NAVY;
        case 'I': return C.INDIGO;
        case 'D': return C.DUSK;
        case 'S': return C.SKY;
        case 'C': return C.CREAM;
        case 'G': return C.GOLD;
        case 'O': return C.ORANGE;
        case 'R': return C.CRIMSON;
        case 'P': return C.PLUM;
        case 'L': return C.LEAF;
        case 'E': return C.GRASS;
        case 'M': return C.LIME;
        case 'W': return C.WOOD;
        case 'A': return C.AMBER;
        case 'F': return C.WHITE;
        default: return -1;
    }
}

// ---------- Bird (13x10 px, 3 frames) -----------
// Frames differ by wing position: up, mid, down.
// K = outline, O = orange body, G = gold accent, F = white, C = cream, R = crimson beak.
export const BIRD_FRAMES = [
    // wing UP
    makeSprite([
        '....KKKKK....',
        '..KKOOOOOKK..',
        '.KOOOOOOOGGK.',
        'KOOOFFOOOGGGK',
        'KOOFKFOOOGGGK',
        'KOOFFFOOOGGOK',
        'KKKKOOOOOOKRK',
        '.KOOOOOOOKRRK',
        '..KKOOOOKK...',
        '....KKKK.....',
    ], 'KOGFCR'),
    // wing MID
    makeSprite([
        '....KKKKK....',
        '..KKOOOOOKK..',
        '.KOOOOOOOGGK.',
        'KOOOFFOOOGGGK',
        'KOOFKFOOOGGGK',
        'KKKKFOOOOGOOK',
        'KGGGKOOOOOKRK',
        'KKKKOOOOOKRRK',
        '..KKOOOOKK...',
        '....KKKK.....',
    ], 'KOGFCR'),
    // wing DOWN
    makeSprite([
        '....KKKKK....',
        '..KKOOOOOKK..',
        '.KOOOOOOOGGK.',
        'KOOOFFOOOGGGK',
        'KOOFKFOOOGGGK',
        'KOOFFFOOOGOOK',
        'KOOOOOOOOOKRK',
        'KKGGKOOOOKRRK',
        'KGGGGKKOKK...',
        '.KKKKKK.KK...',
    ], 'KOGFCR'),
];

// ---------- Coin (9x9, 4 frames for spin) ----------
export const COIN_FRAMES = [
    makeSprite([
        '...KKKKK.',
        '.KKCCCGGK',
        '.KCCGGGGK',
        'KCCGGGGGK',
        'KCGGGGGGK',
        'KCGGGGGGK',
        'KKGGGGGGK',
        '.KKGGGGK.',
        '..KKKKKK.',
    ], 'KCG'),
    makeSprite([
        '...KKK...',
        '..KCGGK..',
        '..KGGGK..',
        '.KCGGGGK.',
        '.KGGGGGK.',
        '.KCGGGGK.',
        '..KGGGK..',
        '..KCGGK..',
        '...KKK...',
    ], 'KCG'),
    makeSprite([
        '...KKKKK.',
        '.KGGGGGCK',
        '.KGGGGGCK',
        'KGGGGGGCK',
        'KGGGGGGCK',
        'KGGGGGGCK',
        'KKGGGGGCK',
        '.KKGGGCK.',
        '..KKKKKK.',
    ], 'KCG'),
    makeSprite([
        '....K....',
        '...KGK...',
        '...KGK...',
        '..KGGGK..',
        '..KGGGK..',
        '..KGGGK..',
        '...KGK...',
        '...KGK...',
        '....K....',
    ], 'KCG'),
];

// ---------- Mushroom (11x11) ----------
export const MUSHROOM = makeSprite([
    '...KKKKK...',
    '.KKRRRRRKK.',
    'KRRRRFFRRRK',
    'KRFFRRRRFFK',
    'KRRRRRRRRRK',
    'KKRRRRRRRKK',
    '..KKCCCCKK.',
    '...KCCCCK..',
    '...KCCCCK..',
    '....KCCK...',
    '.....KK....',
], 'KRFC');

// ---------- Pipe cap + body pieces (drawn separately so pipes can be any height) ----------
export const PIPE_CAP = makeSprite([
    'KEEEEEEEEEEEEEEEEEEEEEEEEEEK',
    'KEEMMMMMMMMMMMMMMMMMMMMMMEEK',
    'KEMEEEEEEEEEEEEEEEEEEEEEMEEK',
    'KEMEEEEEEEEEEEEEEEEEEEEEMEEK',
    'KEMEEEEEEEEEEEEEEEEEEEEEMEEK',
    'KEMEEEEEEEEEEEEEEEEEEEEEMEEK',
    'KEMEEEEEEEEEEEEEEEEEEEEEMEEK',
    'KEEMMMMMMMMMMMMMMMMMMMMMMEEK',
    'KEEEEEEEEEEEEEEEEEEEEEEEEEEK',
    'KKKKKKKKKKKKKKKKKKKKKKKKKKKK',
], 'KEM');

export const PIPE_BODY = (() => {
    // 28 wide x 1 tall row using colors: K outline, E grass, M lime stripe.
    const w = 28, h = 1;
    const data = new Int8Array(w * h);
    for (let i = 0; i < w; i++) {
        if (i === 0 || i === w - 1) data[i] = C.NIGHT;
        else if (i === 2 || i === w - 3) data[i] = C.LIME;
        else data[i] = C.GRASS;
    }
    return { w, h, data };
})();

// Pipe cap sized to 28 wide (matches PIPE_W) regardless of above.
export const PIPE_CAP_28 = (() => {
    const w = 28, h = 10;
    const data = new Int8Array(w * h).fill(C.GRASS);
    for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
            let c = C.GRASS;
            if (y === 0 || y === h - 1 || x === 0 || x === w - 1) c = C.NIGHT;
            else if (y === 1 && x >= 2 && x <= w - 3) c = C.LIME;
            else if (y === h - 2 && x >= 2 && x <= w - 3) c = C.LIME;
            else if (x === 2 || x === w - 3) c = C.LIME;
            data[y * w + x] = c;
        }
    }
    return { w, h, data };
})();

// ---------- Cloud (14x6) ----------
export const CLOUD = makeSprite([
    '...SSSS.......',
    '..SFFFFS......',
    '.SFFFFFFSS....',
    'SFFFFFFFFSS...',
    '.SSFFFFFSS....',
    '...SSSSSS.....',
], 'SF');

// ---------- 3x5 pixel font ----------
const GLYPHS = {
    '0': ['111','101','101','101','111'],
    '1': ['010','110','010','010','111'],
    '2': ['111','001','111','100','111'],
    '3': ['111','001','111','001','111'],
    '4': ['101','101','111','001','001'],
    '5': ['111','100','111','001','111'],
    '6': ['111','100','111','101','111'],
    '7': ['111','001','010','100','100'],
    '8': ['111','101','111','101','111'],
    '9': ['111','101','111','001','111'],
    'A': ['111','101','111','101','101'],
    'B': ['110','101','110','101','110'],
    'C': ['111','100','100','100','111'],
    'D': ['110','101','101','101','110'],
    'E': ['111','100','110','100','111'],
    'F': ['111','100','110','100','100'],
    'G': ['111','100','101','101','111'],
    'H': ['101','101','111','101','101'],
    'I': ['111','010','010','010','111'],
    'J': ['111','001','001','101','111'],
    'K': ['101','110','100','110','101'],
    'L': ['100','100','100','100','111'],
    'M': ['101','111','111','101','101'],
    'N': ['101','111','111','111','101'],
    'O': ['111','101','101','101','111'],
    'P': ['111','101','111','100','100'],
    'Q': ['111','101','101','111','011'],
    'R': ['110','101','110','101','101'],
    'S': ['111','100','111','001','111'],
    'T': ['111','010','010','010','010'],
    'U': ['101','101','101','101','111'],
    'V': ['101','101','101','101','010'],
    'W': ['101','101','111','111','101'],
    'X': ['101','101','010','101','101'],
    'Y': ['101','101','010','010','010'],
    'Z': ['111','001','010','100','111'],
    '!': ['010','010','010','000','010'],
    '?': ['111','001','010','000','010'],
    '.': ['000','000','000','000','010'],
    ',': ['000','000','000','010','100'],
    ':': ['000','010','000','010','000'],
    '-': ['000','000','111','000','000'],
    '+': ['000','010','111','010','000'],
    '/': ['001','001','010','100','100'],
    "'": ['010','010','000','000','000'],
    '"': ['101','101','000','000','000'],
    'x': ['000','101','010','101','000'],
    ' ': ['000','000','000','000','000'],
};

export function measureText(str, scale = 1) {
    return (str.length * 4 - 1) * scale;
}

export function drawText(buf, str, x, y, colorIdx, scale = 1) {
    let cx = x;
    for (let i = 0; i < str.length; i++) {
        const ch = str[i].toUpperCase();
        const glyph = GLYPHS[ch] || GLYPHS[str[i]] || GLYPHS[' '];
        for (let gy = 0; gy < 5; gy++) {
            for (let gx = 0; gx < 3; gx++) {
                if (glyph[gy][gx] === '1') {
                    if (scale === 1) buf.put(cx + gx, y + gy, colorIdx);
                    else buf.rect(cx + gx * scale, y + gy * scale, scale, scale, colorIdx);
                }
            }
        }
        cx += 4 * scale;
    }
}

export function drawTextCentered(buf, str, y, colorIdx, scale = 1) {
    const w = measureText(str, scale);
    drawText(buf, str, ((buf.w - w) / 2) | 0, y, colorIdx, scale);
}
