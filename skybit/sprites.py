"""
All sprite drawing.  Every entity draws itself by calling pyxel primitives
directly, so there are no image banks, no colkey issues, and sprites are
trivially editable as code.
"""
import math
import pyxel
from .palette import (INK, NAVY, BLUE, SKY, CYAN, DKGRN, GREEN, CREAM,
                      RED, ORNG, GOLD, RBLU, WGRN, DIRT, DKRED, WHITE)


# ───────────────────────────── helpers ──────────────────────────────────────

def _px(x, y, c):
    if 0 <= x < pyxel.width and 0 <= y < pyxel.height:
        pyxel.pset(int(x), int(y), c)


def _grid(rows, x0, y0, key):
    """Blit an ASCII pixel-grid; '.' = skip, anything else → palette via key."""
    for row_i, row in enumerate(rows):
        for col_i, ch in enumerate(row):
            if ch == '.':
                continue
            c = key.get(ch, INK)
            _px(x0 + col_i, y0 + row_i, c)


# ───────────────────────────── PARROT ───────────────────────────────────────
# Vivid scarlet-macaw parrot, 16 × 14 px, 4-frame wing cycle.
# Faces RIGHT.  Key:
#   K=ink  R=red-body  D=dark-scarlet(shadow)  O=orange(belly)
#   B=royalblue(wing)  G=bright-green(wing-tip) A=gold(beak)
#   W=white(eye-patch) N=navy(wing-shadow)      E=green (wing edge)

_PARROT_KEY = {
    'K': INK, 'R': RED, 'D': DKRED, 'O': ORNG,
    'B': RBLU, 'G': WGRN, 'A': GOLD,
    'W': WHITE, 'N': NAVY, 'E': GREEN,
}

# 4 frames – the wing sweeps from fully-raised to fully-lowered.
# Body stays the same; only the wing rows change.
_BODY = [            # rows 5-13 shared across all frames
    "....KKKKKKKK...",   # 5  – top of torso
    "...KRRRRRRRRK..",   # 6
    "..KRRRRRRRRRDK.",   # 7  – wide body
    ".KRRRRWKWRRRDK.",   # 8  – white eye + dark pupil
    ".KRRRROWRRRAAAK",   # 9  – orange eye-ring, gold beak
    ".KOOORRRRRRRDKK",   # 10 – orange belly
    ".KORRRRRRRRRKK.",   # 11
    "..KRRRRRRRRK...",   # 12
    "...KKKKKKK.....",   # 13
]

PARROT_FRAMES = [
    # ── frame 0: wings fully UP ──────────────────────────────────────────
    [
        "..KBBBBBK......",   # 0
        ".KBGGGGGBK.....",   # 1
        "KBGGEGGGGBK....",   # 2  E=bright-green tip
        "KBGGAGGGGBK....",   # 3  A=gold highlight
        ".KBBBBBBBK.....",   # 4
    ] + _BODY,

    # ── frame 1: wings half-up ────────────────────────────────────────────
    [
        "...............",   # 0
        "...KBBBBK......",   # 1
        "..KBGGGGBK.....",   # 2
        ".KBGGAGGBK.....",   # 3
        "KBBBBBBBBBBK...",   # 4  wing sweeps wide
    ] + _BODY,

    # ── frame 2: wings level / mid-down ──────────────────────────────────
    [
        "...............",   # 0
        "...............",   # 1
        "...............",   # 2
        "...............",   # 3
        ".KBBBBBBBBBBK..",   # 4  flat stroke
    ] + _BODY,

    # ── frame 3: wings fully DOWN ────────────────────────────────────────
    [
        "...............",   # 0  (body rows first now)
        "...............",   # 1
        "...............",   # 2
        "...............",   # 3
        "...............",   # 4
    ] + _BODY[:4] + [
        ".KOOORRRRRRRDKK",   # 10 – (same belly)
        ".KORRRRRRRRRKK.",   # 11
        "..KRRRRRRRRK...",   # 12
        "KBBBBBBBBBBK...",   # 13 – wing sweeps OUT below body
    ] + [
        ".KBGGGGGGBK....",   # 14
        "..KBGAGGBK.....",   # 15
        "...KBBBK.......",   # 16
    ],
]

# Normalize: pad all frames to same height
_MAX_H = max(len(f) for f in PARROT_FRAMES)
for _f in PARROT_FRAMES:
    while len(_f) < _MAX_H:
        _f.append(".................")

PARROT_W = 16
PARROT_H = _MAX_H


def draw_parrot(cx, cy, frame, flap_up=False):
    """Draw parrot centred at (cx,cy). frame=0-3."""
    rows = PARROT_FRAMES[frame % 4]
    x0 = int(cx) - PARROT_W // 2
    y0 = int(cy) - PARROT_H // 2
    _grid(rows, x0, y0, _PARROT_KEY)
    # Bright red specular dot on back to make colours pop
    pyxel.pset(x0 + 7, y0 + 6, WHITE)


def draw_parrot_tilt(cx, cy, frame, vy):
    """Draw parrot with nose-tilt: shift top half up or down by ±1-2px."""
    tilt = max(-2, min(2, int(vy / 120)))
    rows = PARROT_FRAMES[frame % 4]
    x0 = int(cx) - PARROT_W // 2
    y0 = int(cy) - PARROT_H // 2
    pivot = 6  # row where tilt pivots
    for ri, row in enumerate(rows):
        dy = tilt if ri < pivot else 0
        for ci, ch in enumerate(row):
            if ch != '.':
                _px(x0 + ci, y0 + ri + dy, _PARROT_KEY.get(ch, INK))
    pyxel.pset(x0 + 7, y0 + 6 + (tilt if 6 < pivot else 0), WHITE)


# ───────────────────────────── TRAIL ────────────────────────────────────────

def draw_trail(points):
    """Feathery motion trail: fading discs."""
    n = len(points)
    for i, (tx, ty) in enumerate(points):
        k = i / n
        if k < 0.3:
            continue
        r = 1 + int(k * 3)
        c = CREAM if k > 0.75 else SKY
        pyxel.circ(int(tx), int(ty), r, c)


# ───────────────────────────── PIPE ─────────────────────────────────────────

def draw_pipe(x, gap_y, gap_h, ground_y):
    w = 22
    cap_h = 8
    cap_extra = 3  # cap is cap_extra wider on each side

    def _cap(cx, cy, flipped=False):
        # Wider green cap with highlight and shadow edges
        pyxel.rect(cx - cap_extra, cy, w + cap_extra * 2, cap_h, GREEN)
        pyxel.rect(cx - cap_extra, cy, w + cap_extra * 2, 1, CREAM)       # top highlight
        pyxel.rect(cx - cap_extra, cy + cap_h - 1, w + cap_extra * 2, 1, DKGRN)  # bottom shadow
        pyxel.rect(cx - cap_extra, cy, 1, cap_h, CREAM)                   # left highlight
        pyxel.rect(cx + w + cap_extra - 1, cy, 1, cap_h, DKGRN)           # right shadow

    def _body(cx, y_start, height):
        if height <= 0:
            return
        pyxel.rect(cx, y_start, w, height, DKGRN)
        # Stripe
        pyxel.rect(cx + 3, y_start, 3, height, GREEN)
        # Edges
        pyxel.rect(cx, y_start, 1, height, GREEN)
        pyxel.rect(cx + w - 1, y_start, 1, height, INK)

    # ── top pipe ──
    top_body_h = max(0, gap_y - cap_h)
    _body(x, 0, top_body_h)
    if gap_y >= cap_h:
        _cap(x, gap_y - cap_h)

    # ── bottom pipe ──
    bot_y = gap_y + gap_h
    bot_body_h = max(0, ground_y - bot_y - cap_h)
    _cap(x, bot_y)
    _body(x, bot_y + cap_h, bot_body_h)


# ───────────────────────────── COIN ─────────────────────────────────────────

def draw_coin(x, y, t):
    """Spinning coin with shimmer."""
    frame = int(t * 8) % 4
    bob = math.sin(t * 4.5) * 1.5
    cy = int(y + bob)
    cx = int(x)
    if frame == 0:
        pyxel.circ(cx, cy, 5, GOLD)
        pyxel.circ(cx, cy, 3, 10)   # inner lighter gold
        pyxel.pset(cx - 1, cy - 2, WHITE)  # shine
    elif frame == 1:
        pyxel.rect(cx - 3, cy - 5, 6, 10, GOLD)
        pyxel.rect(cx - 1, cy - 5, 2, 10, 10)
        pyxel.pset(cx - 2, cy - 3, WHITE)
    elif frame == 2:
        pyxel.rect(cx - 1, cy - 5, 2, 10, GOLD)
        pyxel.pset(cx - 1, cy - 4, WHITE)
    else:
        pyxel.rect(cx - 3, cy - 5, 6, 10, GOLD)
        pyxel.rect(cx - 1, cy - 5, 2, 10, 10)
        pyxel.pset(cx - 2, cy - 3, WHITE)


# ───────────────────────────── MUSHROOM ─────────────────────────────────────
# Red-capped mushroom (power-up).

def draw_mushroom(x, y, t):
    bob = math.sin(t * 3.0) * 1.5
    cx, cy = int(x), int(y + bob)
    r = 8 + math.sin(t * 5) * 1.0  # pulsing halo

    # Halo rings
    pyxel.circb(cx, cy, int(r),     ORNG)
    pyxel.circb(cx, cy, int(r) + 2, GOLD)

    # Stem
    pyxel.rect(cx - 4, cy + 2, 8, 7, CREAM)
    pyxel.rect(cx - 3, cy + 3, 6, 5, WHITE)

    # Cap
    pyxel.circ(cx, cy, 7, DKRED)
    pyxel.circ(cx, cy - 1, 6, RED)
    # White spots
    pyxel.circ(cx - 3, cy - 2, 2, WHITE)
    pyxel.circ(cx + 3, cy - 2, 2, WHITE)
    pyxel.circ(cx,     cy + 1, 1, WHITE)
    # Cap highlight
    pyxel.pset(cx - 1, cy - 4, CREAM)


# ───────────────────────────── CLOUD ────────────────────────────────────────

def draw_cloud(x, y):
    cx, cy = int(x), int(y)
    pyxel.circ(cx,      cy,     5, WHITE)
    pyxel.circ(cx + 7,  cy - 1, 7, WHITE)
    pyxel.circ(cx + 14, cy,     5, WHITE)
    pyxel.circ(cx + 4,  cy + 2, 5, WHITE)
    pyxel.circ(cx + 10, cy + 2, 5, WHITE)
    # Slight shadow underside
    pyxel.rect(cx - 1, cy + 4, 17, 2, CYAN)


# ───────────────────────────── BACKGROUND ───────────────────────────────────

def draw_sky(ground_y):
    h = ground_y
    band = h // 4
    pyxel.rect(0, 0,      pyxel.width, band,     NAVY)
    pyxel.rect(0, band,   pyxel.width, band,     BLUE)
    pyxel.rect(0, band*2, pyxel.width, band,     SKY)
    pyxel.rect(0, band*3, pyxel.width, h-band*3, CYAN)
    # Sun
    pyxel.circ(135, 38, 11, CREAM)
    pyxel.circ(135, 38, 9,  GOLD)
    pyxel.circ(135, 38, 6,  ORNG)
    pyxel.circb(135, 38, 14, GOLD)


def draw_mountains(scroll, ground_y):
    import math
    W = pyxel.width
    # Far range (indigo/blue)
    for x in range(W):
        hh = int(38 + math.sin((x + scroll * 0.18) * 0.035) * 20
                    + math.sin((x + scroll * 0.18) * 0.08) * 10)
        pyxel.rect(x, ground_y - hh, 1, hh, BLUE)
    # Near range (darker)
    for x in range(W):
        hh = int(24 + math.sin((x + scroll * 0.4) * 0.05 + 1.2) * 16
                    + math.sin((x + scroll * 0.4) * 0.13 + 0.8) * 8)
        pyxel.rect(x, ground_y - hh, 1, hh, NAVY)


def draw_ground(scroll, ground_y):
    W = pyxel.width
    H = pyxel.height
    # Dirt
    pyxel.rect(0, ground_y, W, H - ground_y, DIRT)
    # Grass strip
    pyxel.rect(0, ground_y,     W, 4, GREEN)
    pyxel.rect(0, ground_y + 2, W, 1, DKGRN)
    # Scrolling grass tufts
    off = int(scroll) % 10
    for gx in range(-off, W, 10):
        pyxel.pset(gx + 2, ground_y - 1, CREAM)
        pyxel.pset(gx + 6, ground_y - 1, GREEN)
    # Dirt speckles
    off2 = int(scroll * 1.3) % 14
    for gy in range(ground_y + 5, H, 7):
        for gx in range(-off2, W, 14):
            pyxel.pset(gx + 5, gy, ORNG)


# ───────────────────────────── PIXEL FONT ───────────────────────────────────
# 3×5 bitmap glyphs drawn as pyxel.pset calls.

_GLYPHS = {
    '0':['111','101','101','101','111'], '1':['010','110','010','010','111'],
    '2':['111','001','111','100','111'], '3':['111','001','111','001','111'],
    '4':['101','101','111','001','001'], '5':['111','100','111','001','111'],
    '6':['111','100','111','101','111'], '7':['111','001','010','100','100'],
    '8':['111','101','111','101','111'], '9':['111','101','111','001','111'],
    'A':['111','101','111','101','101'], 'B':['110','101','110','101','110'],
    'C':['111','100','100','100','111'], 'D':['110','101','101','101','110'],
    'E':['111','100','110','100','111'], 'F':['111','100','110','100','100'],
    'G':['111','100','101','101','111'], 'H':['101','101','111','101','101'],
    'I':['111','010','010','010','111'], 'J':['111','001','001','101','111'],
    'K':['101','110','100','110','101'], 'L':['100','100','100','100','111'],
    'M':['101','111','111','101','101'], 'N':['101','111','111','111','101'],
    'O':['111','101','101','101','111'], 'P':['111','101','111','100','100'],
    'Q':['111','101','101','111','011'], 'R':['110','101','110','101','101'],
    'S':['111','100','111','001','111'], 'T':['111','010','010','010','010'],
    'U':['101','101','101','101','111'], 'V':['101','101','101','101','010'],
    'W':['101','101','111','111','101'], 'X':['101','101','010','101','101'],
    'Y':['101','101','010','010','010'], 'Z':['111','001','010','100','111'],
    '!':['010','010','010','000','010'], '?':['111','001','010','000','010'],
    '.':['000','000','000','000','010'], ',':['000','000','000','010','100'],
    ':':['000','010','000','010','000'], '-':['000','000','111','000','000'],
    '+':['000','010','111','010','000'], 'x':['000','101','010','101','000'],
    "'":['010','010','000','000','000'], ' ':['000','000','000','000','000'],
}


def text_w(s, scale=1): return (len(s) * 4 - 1) * scale


def draw_text(s, x, y, col, scale=1, shadow_col=None):
    if shadow_col is not None:
        draw_text(s, x + scale, y + scale, shadow_col, scale)
    for i, ch in enumerate(s.upper()):
        g = _GLYPHS.get(ch, _GLYPHS[' '])
        for gy in range(5):
            for gx in range(3):
                if g[gy][gx] == '1':
                    if scale == 1:
                        _px(x + i*4 + gx, y + gy, col)
                    else:
                        pyxel.rect(x + i*4*scale + gx*scale,
                                   y + gy*scale, scale, scale, col)


def draw_text_c(s, y, col, scale=1, shadow_col=None):
    x = (pyxel.width - text_w(s, scale)) // 2
    draw_text(s, x, y, col, scale, shadow_col)
