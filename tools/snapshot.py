#!/usr/bin/env python3
"""
Generate PNG screenshots by running the real game drawing code
through a thin Pillow-backed pyxel shim (no display needed).
"""
import sys, os, math, types
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PIL import Image, ImageDraw

W, H  = 160, 240
SCALE = 4          # output size = 640 × 960

OUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'screenshots')
os.makedirs(OUT, exist_ok=True)

# ── Pillow pyxel shim ────────────────────────────────────────────────────────

_PALETTE = [
    0x050D1A, 0x122040, 0x1F3F78, 0x3A72CC, 0x7EC8F0,
    0x194D14, 0x3CC43C, 0xF4F0DC, 0xE81818, 0xFF7800,
    0xFFD700, 0x1A4FFF, 0x22CC55, 0x7A4010, 0xB02020,
    0xFFFFFF,
]

def _rgb(idx):
    v = _PALETTE[idx & 15]
    return ((v >> 16) & 0xff, (v >> 8) & 0xff, v & 0xff)


class _Canvas:
    def __init__(self):
        self.img  = Image.new('RGB', (W, H))
        self.draw = ImageDraw.Draw(self.img)

    def to_png(self, path, scale=SCALE):
        out = self.img.resize((W*scale, H*scale), Image.NEAREST)
        out.save(path)
        print('wrote', path)


_cv: _Canvas = None


def _c(idx): return _rgb(idx)


def _clamp_rect(x, y, w, h):
    x1 = max(0, int(x))
    y1 = max(0, int(y))
    x2 = min(W, int(x + w))
    y2 = min(H, int(y + h))
    return x1, y1, x2, y2


# -- pyxel API stubs that draw into _cv ---------------------------------------

def _pset(x, y, col):
    xi, yi = int(x), int(y)
    if 0 <= xi < W and 0 <= yi < H:
        _cv.draw.point((xi, yi), _c(col))

def _rect(x, y, w, h, col):
    x1, y1, x2, y2 = _clamp_rect(x, y, w, h)
    if x2 > x1 and y2 > y1:
        _cv.draw.rectangle([x1, y1, x2-1, y2-1], fill=_c(col))

def _rectb(x, y, w, h, col):
    x1, y1, x2, y2 = int(x), int(y), int(x+w)-1, int(y+h)-1
    _cv.draw.rectangle([x1, y1, x2, y2], outline=_c(col))

def _circ(x, y, r, col):
    cx, cy, ri = int(x), int(y), int(r)
    _cv.draw.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], fill=_c(col))

def _circb(x, y, r, col):
    cx, cy, ri = int(x), int(y), int(r)
    _cv.draw.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], outline=_c(col))

def _line(x1, y1, x2, y2, col):
    _cv.draw.line([int(x1), int(y1), int(x2), int(y2)], fill=_c(col))

def _cls(col):
    _rect(0, 0, W, H, col)

def _dither(*a, **k): pass
def _noop(*a, **k): pass
_sin = lambda d: math.sin(d * math.pi / 180)

# Build and install the mock before any game import
px = types.ModuleType('pyxel')
px.width  = W;  px.height = H
px.colors = list(_PALETTE)
px.MOUSE_BUTTON_LEFT=0; px.KEY_SPACE=32; px.KEY_UP=273
px.KEY_W=119; px.KEY_P=112; px.KEY_ESCAPE=27
px.mouse_x=0; px.mouse_y=0
px.sin    = _sin
px.pset   = _pset;  px.rect  = _rect;  px.rectb = _rectb
px.circ   = _circ;  px.circb = _circb; px.line  = _line
px.cls    = _cls;   px.dither= _dither
for fn in ['init','run','mouse','btnp','btn','blt','text','sound','play']:
    setattr(px, fn, _noop)
sys.modules['pyxel'] = px

# Now import game drawing modules (safe – no pyxel.init needed)
from skybit.palette import apply as _apply_pal, INK
from skybit.sprites import (draw_sky, draw_mountains, draw_ground,
                             draw_cloud, draw_parrot_tilt, draw_trail,
                             draw_pipe, draw_coin, draw_mushroom,
                             draw_text, draw_text_c, text_w)
from skybit.config  import GROUND_Y
from skybit.palette import (NAVY, ORNG, GOLD, CREAM, WHITE,
                             DKRED, RED, SKY, INK, GREEN, RBLU)

# Apply palette to px.colors so colour names resolve
_apply_pal()
# Patch _PALETTE with the (possibly tweaked) values
for i in range(16):
    _PALETTE[i] = px.colors[i]


# ── scene helpers ────────────────────────────────────────────────────────────

def _base(mountain_scroll=40, ground_scroll=20):
    draw_sky(GROUND_Y)
    for cx, cy in [(20, 35), (85, 60), (140, 28), (55, 95)]:
        draw_cloud(cx, cy)
    draw_mountains(mountain_scroll, GROUND_Y)
    draw_ground(ground_scroll, GROUND_Y)


# ── Scene 1: Title ────────────────────────────────────────────────────────────
def scene_title():
    global _cv; _cv = _Canvas()
    _cls(INK)
    _base()
    # Preview bird + collectibles
    draw_parrot_tilt(40, 158, 1, -40)
    draw_coin(88,  160, 0.0)
    draw_coin(104, 153, 1.2)
    draw_mushroom(134, 164, 0.8)
    # Title
    y = 54
    title = 'SKYBIT'
    sx = (W - text_w(title, 3)) // 2
    draw_text(title, sx+2, y+2, INK,  3)
    draw_text(title, sx+1, y-1, GOLD, 3)
    draw_text(title, sx,   y,   ORNG, 3)
    draw_text_c('A RETRO PIXEL FLYER', y+24, CREAM, 1, shadow_col=INK)
    draw_text_c('TAP TO FLAP',             178, WHITE, 1, shadow_col=INK)
    draw_text_c('COLLECT COINS',           192, GOLD,  1, shadow_col=INK)
    draw_text_c('GRAB MUSHROOM FOR 3X!', 204, ORNG,  1, shadow_col=INK)
    _cv.to_png(os.path.join(OUT, 'title.png'))


# ── Scene 2: Mid-gameplay ─────────────────────────────────────────────────────
def scene_gameplay():
    global _cv; _cv = _Canvas()
    _cls(INK)
    _base(60, 30)
    draw_pipe(85, 95, 80, GROUND_Y)
    # Coin arc
    for i in range(5):
        t = i/4
        draw_coin(85+14 - 18 + t*36,
                  135 - math.sin(t*math.pi)*18,
                  float(i)*0.6)
    trail = [(38+i*3, 142-i*0.5) for i in range(8)]
    draw_trail(trail)
    draw_parrot_tilt(52, 140, 1, -60)
    # HUD
    s = '8'; sw = text_w(s, 2)
    draw_text(s, (W-sw)//2+1, 9, INK,   2)
    draw_text(s, (W-sw)//2,   8, WHITE, 2)
    draw_text('HI 24', 5, 5, CREAM, 1, shadow_col=INK)
    cs = 'x6'; cw = text_w(cs)
    draw_text(cs, W-cw-11, 4, GOLD, 1, shadow_col=INK)
    _circ(W-cw-7, 6, 3, GOLD)
    draw_text_c('X4 COMBO!', H-28, ORNG, 1, shadow_col=INK)
    _cv.to_png(os.path.join(OUT, 'gameplay.png'))


# ── Scene 3: Mushroom 3× active ───────────────────────────────────────────────
def scene_mushroom():
    global _cv; _cv = _Canvas()
    _cls(INK)
    _base(110, 60)
    draw_pipe(95, 75, 78, GROUND_Y)
    for i in range(6):
        draw_coin(65+i*10, 118, float(i)*0.5)
    # Sparkle burst
    bx, by = 50, 150
    for i in range(20):
        ang = i/20*2*math.pi
        r   = 18 + (i%3)*3
        px2 = int(bx + math.cos(ang)*r)
        py2 = int(by + math.sin(ang)*r)
        col = WHITE if i%3==0 else (ORNG if i%2 else CREAM)
        _pset(px2, py2, col)
    _circb(bx, by, 13, ORNG)
    _circb(bx, by, 15, GOLD)
    trail = [(bx-18+i*3, by+2-i*0.3) for i in range(7)]
    draw_trail(trail)
    draw_parrot_tilt(bx, by, 0, -120)
    draw_text('+3', 100, 112, INK,  1)
    draw_text('+3',  99, 111, ORNG, 1)
    # HUD with timer bar
    s = '45'; sw = text_w(s, 2)
    draw_text(s, (W-sw)//2+1, 9,  INK,  2)
    draw_text(s, (W-sw)//2,   8,  WHITE,2)
    draw_text('HI 24', 5, 5, CREAM, 1, shadow_col=INK)
    draw_text_c('3X POWER', 17, CREAM, 1, shadow_col=INK)
    bw=70; bx2=(W-bw)//2; bh=4; bby=24
    _rect(bx2-1, bby-1, bw+2, bh+2, INK)
    _rect(bx2,   bby,   bw,   bh,   NAVY)
    _rect(bx2,   bby,   50,   bh,   ORNG)
    draw_text_c('X5 COMBO!', H-28, ORNG, 1, shadow_col=INK)
    _cv.to_png(os.path.join(OUT, 'mushroom.png'))


# ── Scene 4: Game Over ────────────────────────────────────────────────────────
def scene_gameover():
    global _cv; _cv = _Canvas()
    _cls(INK)
    _base(200, 100)
    draw_pipe(105, 125, 70, GROUND_Y)
    # Dead bird falling
    draw_parrot_tilt(50, 195, 3, 300)
    # Game-over card
    y = 82
    draw_text_c('GAME OVER', y,     DKRED, 2, shadow_col=INK)
    draw_text_c('SCORE 45',  y+26,  WHITE, 1, shadow_col=INK)
    draw_text_c('BEST  45',  y+38,  GOLD,  1, shadow_col=INK)
    draw_text_c('NEW BEST!', y+52,  ORNG,  1, shadow_col=INK)
    draw_text_c('TAP TO RETRY', y+70, CREAM, 1, shadow_col=INK)
    _cv.to_png(os.path.join(OUT, 'gameover.png'))


if __name__ == '__main__':
    scene_title()
    scene_gameplay()
    scene_mushroom()
    scene_gameover()
    print('done')
