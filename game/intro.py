"""
Skybit intro — a tiny pixel-art cinematic that introduces Pip the courier
parrot, his boss Mr. Garrick, the day-cycle, and the delivery loop.

The piece runs at a 90x160 logical resolution and is upscaled NEAREST to
the 360x640 game window for that chunky pixel feel. All sprites are tiny
multi-line string blueprints decoded into Surfaces at import.

Plays once on first launch (gated by `intro_seen` in skybit_save.json),
skippable on any tap/click/key.

Five beats:
  0.0–2.0  "Dawn"     – pillar at first light, Pip lands by mailbag + parcel
  2.0–3.8  "Briefing" – Mr. Garrick on the next pillar, parcel hands off
  3.8–9.0  "Journey"  – Pip flies right; sky cycles day → sunset → night → dawn
  9.0–10.5 "Arrival"  – Pip drops the parcel into a pillar-top mailbox
  10.5–12.0 "Title"   – SKYBIT logo + "TAP TO FLY"
"""
from __future__ import annotations

import math
import pygame

from game.config import W, H
from game import audio as _audio


DURATION = 12.0

# Logical pixel grid. The whole intro renders into this size, then a single
# NEAREST upscale to 360x640 (the game's window) gives chunky pixels.
LW, LH = 90, 160
SCALE = W // LW   # 4x; W=360, LW=90 → SCALE=4


# ── 16-colour pastel palette ─────────────────────────────────────────────────

PAL = {
    '.': None,                 # transparent
    'k': (10, 12, 28),         # near-black ink
    'K': (40, 30, 60),         # dark purple ink
    'w': (245, 245, 250),      # off-white
    'r': (230, 70, 75),        # macaw red
    'R': (160, 30, 40),        # red shadow
    'y': (255, 210, 80),       # gold
    'Y': (220, 150, 50),       # gold shadow
    'b': (70, 130, 230),       # macaw blue
    'B': (40, 80, 160),        # blue shadow
    'g': (100, 200, 110),      # leaf green
    'G': (50, 130, 70),        # green shadow
    'p': (255, 200, 200),      # pelican pink
    'P': (210, 150, 160),      # pelican shadow
    'o': (240, 130, 70),       # warm orange (beak / sunset)
    'n': (140, 100, 70),       # parcel kraft brown
    'N': (90, 60, 40),         # parcel shadow
    's': (190, 150, 110),      # sandstone pillar
    'S': (130, 95, 65),        # pillar shadow
    'm': (60, 50, 90),         # mountain silhouette
    'M': (35, 28, 60),         # far mountain
    'l': (200, 220, 255),      # moonlight star
}


def _decode(rows: list[str]) -> pygame.Surface:
    """Turn a list of palette-letter strings into a pygame Surface.
    '.' is transparent."""
    h = len(rows)
    w = max(len(r) for r in rows) if rows else 0
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            col = PAL.get(ch)
            if col is not None:
                surf.set_at((x, y), col)
    return surf


def _flip(surf: pygame.Surface, x: bool = False, y: bool = False) -> pygame.Surface:
    return pygame.transform.flip(surf, x, y)


# Filled in by the next slice.
_SPRITES: dict[str, pygame.Surface] = {}


def _build_sprites() -> None:
    """Build every pixel sprite once and cache it in `_SPRITES`."""

    # Pip — side-on, head facing right, 14x12. Goggles are the gold band
    # across his eye. Wings have three frames (up / mid / down).
    pip_base_rows = [
        "....rrr.......",
        "...rrrrr.....r",
        "..rrrwwrrr..rr",
        "..rrwkkwrr.rr.",
        "..rryyyyyrrr..",
        "...rrrrrrrr...",
        "...bbrrrroo...",
        "...BBbrrro....",
        "....BB..oo....",
        "....bb........",
        ".....b........",
        ".....b........",
    ]
    pip_wing_up = [
        "..............",
        "...bbb........",
        "..bBBBb.......",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
    ]
    pip_wing_mid = [
        "..............",
        "..............",
        "..............",
        "..............",
        "..bbb.........",
        ".bBBBb........",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
    ]
    pip_wing_down = [
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..............",
        "..bBBb........",
        ".bBBBBb.......",
        ".bBBBb........",
        "..............",
        "..............",
    ]

    def _stack(*rowsets):
        # Composite multiple row sets onto one surface, top-to-bottom layer.
        layers = [_decode(rs) for rs in rowsets]
        w = max(l.get_width() for l in layers)
        h = max(l.get_height() for l in layers)
        out = pygame.Surface((w, h), pygame.SRCALPHA)
        for l in layers:
            out.blit(l, (0, 0))
        return out

    _SPRITES["pip_0"] = _stack(pip_base_rows, pip_wing_up)
    _SPRITES["pip_1"] = _stack(pip_base_rows, pip_wing_mid)
    _SPRITES["pip_2"] = _stack(pip_base_rows, pip_wing_down)
    # Mirror — Pip facing left
    _SPRITES["pip_l_0"] = _flip(_SPRITES["pip_0"], x=True)
    _SPRITES["pip_l_1"] = _flip(_SPRITES["pip_1"], x=True)
    _SPRITES["pip_l_2"] = _flip(_SPRITES["pip_2"], x=True)

    # Mr. Garrick — pelican, side-on facing right, 14x16
    _SPRITES["garrick"] = _decode([
        "..............",
        "....pppp......",
        "...ppppppoooo.",
        "...pkpppoooooo",
        "...pppppoooo..",
        "..pppppppp....",
        ".ppppwwppp....",
        ".ppppwwppp....",
        ".pppwwwwpp....",
        ".PPPwwwwPP....",
        "..PPPPPPP.....",
        "...PPPPP......",
        "....PPP.......",
        "....PP........",
        "....pp........",
        "....PP........",
    ])

    # Parcel — small kraft cube with red ribbon, 6x6
    _SPRITES["parcel"] = _decode([
        "..nrn.",
        ".nnrnn",
        "nnnrnn",
        "rrrrrr",
        "NnnrnN",
        ".NNrN.",
    ])

    # Mailbag — 8x6 canvas sack with brass buckle
    _SPRITES["mailbag"] = _decode([
        ".nnnnn..",
        "nnNNNnn.",
        "nNNyyNn.",
        "nNNyyNn.",
        "nNNNNNn.",
        ".nnnnn..",
    ])

    # Mailbox — 8x9 small wooden box on a post, with red flag raised
    _SPRITES["mailbox"] = _decode([
        ".......r",
        "......rr",
        "..nnn.rr",
        ".nnnnnr.",
        ".nNNNn..",
        ".nnnnn..",
        "...n....",
        "...n....",
        "..nnn...",
    ])

    # Pillar tile (10 wide, repeats vertically as needed)
    _SPRITES["pillar_top"] = _decode([
        "..gggg....",
        ".ggggGg...",
        "ggGGGggg..",
        ".ssssss...",
        "ssSSsSSss.",
        "ssssssssS.",
        "sSsssssSS.",
        "ssSssSsSS.",
    ])
    _SPRITES["pillar_mid"] = _decode([
        "ssSssssSS.",
        "sSsssSsss.",
        "ssssSssSs.",
        "sSSssssSS.",
        "sSsssSsss.",
        "ssssSssSs.",
        "sSSssssSS.",
        "ssSssSsss.",
    ])

    # Soundwave bubble (Garrick's earpiece squawk) — 7x7 dotted swirl
    _SPRITES["squawk"] = _decode([
        ".kkkkk.",
        "k.....k",
        "k.kkk.k",
        "k.k.k.k",
        "k.kkk.k",
        "k.....k",
        ".kkkkk.",
    ])

    # Sun / moon disc — 9x9 round
    _SPRITES["sun"] = _decode([
        "...yyy...",
        "..yyyyy..",
        ".yyyyYyy.",
        "yyyyyyYyy",
        "yyyyyYYyy",
        "yyyyYYYyy",
        ".yyYYYYy.",
        "..yyYYy..",
        "...yyy...",
    ])
    _SPRITES["moon"] = _decode([
        "...www...",
        "..wwwww..",
        ".www.www.",
        "ww.....ww",
        "ww.....ww",
        "ww.....ww",
        ".www.www.",
        "..wwwww..",
        "...www...",
    ])


# ── tiny 5x7 pixel font for SKIP / SKYBIT / TAP TO FLY ───────────────────────

_PIXEL_FONT: dict[str, list[str]] = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11100", "10010", "10001", "10001", "10001", "10010", "11100"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10101", "10101", "10011", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "10001", "01010", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '.': ["00000", "00000", "00000", "00000", "00000", "00000", "00100"],
    '·': ["00000", "00000", "00000", "00100", "00000", "00000", "00000"],
}


def _draw_pixel_label(surf, text, x, y, scale=1, color=(255, 255, 255, 255)):
    """Draw `text` as a 5x7 pixel font at (x, y) with NEAREST scaling."""
    cx = x
    for ch in text.upper():
        glyph = _PIXEL_FONT.get(ch, _PIXEL_FONT[' '])
        for gy, row in enumerate(glyph):
            for gx, cell in enumerate(row):
                if cell == '1':
                    rect = pygame.Rect(
                        cx + gx * scale, y + gy * scale, scale, scale)
                    if len(color) == 4:
                        s = pygame.Surface((scale, scale), pygame.SRCALPHA)
                        s.fill(color)
                        surf.blit(s, rect.topleft)
                    else:
                        pygame.draw.rect(surf, color, rect)
        cx += 6 * scale  # 5 glyph cols + 1 space


# ── scene class ──────────────────────────────────────────────────────────────

class IntroScene:
    DURATION = DURATION

    def __init__(self):
        self.t = 0.0
        self.done = False
        self._pad_started = False
        self._crackle_played = False
        self._title_t = 0.0
        # The logical-pixel canvas everything draws to before upscale.
        self._canvas = pygame.Surface((LW, LH))
        if not _SPRITES:
            _build_sprites()

    def update(self, dt: float) -> None:
        self.t += dt
        self._title_t += dt
        if not self._pad_started:
            try: _audio.play_intro_pad()
            except Exception: pass
            self._pad_started = True
        if 2.4 <= self.t < 2.5 and not self._crackle_played:
            try: _audio.play_intro_crackle()
            except Exception: pass
            self._crackle_played = True
        if self.t >= self.DURATION:
            self.done = True

    def skip(self) -> None:
        self.done = True

    def render(self, surf: pygame.Surface) -> None:
        # Draw the whole frame at logical resolution, then scale up.
        self._canvas.fill((10, 12, 28))
        _dispatch(self, self._canvas)
        scaled = pygame.transform.scale(self._canvas, (W, H))
        surf.blit(scaled, (0, 0))
        _draw_skip(surf, self.t)


def _draw_skip(surf: pygame.Surface, t: float) -> None:
    if t < 1.5: return
    fade = max(0.0, min(1.0, (t - 1.5) / 0.4))
    a = int(140 * fade)
    if a <= 0: return
    pill_w, pill_h = 56, 22
    pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
    pygame.draw.rect(pill, (10, 12, 28, a + 60),
                     pill.get_rect(), border_radius=6)
    pygame.draw.rect(pill, (245, 245, 250, a + 100),
                     pill.get_rect(), width=1, border_radius=6)
    surf.blit(pill, (W - pill_w - 12, 14))
    # Tiny "SKIP" label drawn manually as 5x7 letters at 2x.
    _draw_pixel_label(surf, "SKIP", W - pill_w - 12 + 12, 14 + 6,
                      scale=2, color=(245, 245, 250, a + 100))


# ── world / landscape painters (all on the 90x160 logical canvas) ────────────

# Sky palettes per beat — top, middle, bottom row colours.
_SKY = {
    "predawn": ((40, 30, 70),  (90, 60, 110), (200, 130, 140)),
    "dawn":    ((90, 90, 180), (220, 160, 180), (255, 210, 170)),
    "day":     ((80, 160, 230), (140, 200, 240), (200, 230, 245)),
    "golden":  ((120, 80, 160), (240, 150, 120), (255, 200, 130)),
    "sunset":  ((90, 50, 130),  (220, 90, 110),  (255, 150, 90)),
    "night":   ((10, 12, 35),   (20, 25, 70),    (40, 50, 110)),
    "sunrise": ((150, 110, 200), (255, 160, 150), (255, 220, 170)),
}


def _lerp_col(a, b, t):
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


def _blend_sky(name_a: str, name_b: str, t: float) -> tuple:
    a = _SKY[name_a]; b = _SKY[name_b]
    return tuple(_lerp_col(a[i], b[i], t) for i in range(3))


def _paint_sky(canvas: pygame.Surface, sky_top, sky_mid, sky_bot,
               horizon_y: int = 110) -> None:
    """Three-band gradient drawn as discrete pixel rows for a true pixel feel
    (no smoothing). 5-step bands."""
    bands = (
        (0,  horizon_y // 2,                       sky_top),
        (horizon_y // 2,  horizon_y - 8,           _lerp_col(sky_top, sky_mid, 0.5)),
        (horizon_y - 8,   horizon_y,               sky_mid),
        (horizon_y,       horizon_y + 12,          _lerp_col(sky_mid, sky_bot, 0.5)),
        (horizon_y + 12,  LH,                      sky_bot),
    )
    for y0, y1, col in bands:
        pygame.draw.rect(canvas, col, (0, y0, LW, y1 - y0))


def _paint_stars(canvas: pygame.Surface, alpha: int) -> None:
    if alpha <= 0: return
    seeds = [(7, 11), (15, 6), (24, 14), (32, 5), (41, 18), (49, 9),
             (58, 13), (66, 4), (74, 17), (82, 8), (12, 22), (28, 27),
             (45, 30), (62, 25), (79, 32)]
    s = pygame.Surface((1, 1), pygame.SRCALPHA)
    for x, y in seeds:
        s.fill((230, 230, 255, alpha))
        canvas.blit(s, (x, y))
    # Brighter star
    pygame.draw.rect(canvas, (255, 255, 240), (35, 12, 1, 1))


def _paint_mountains(canvas: pygame.Surface, scroll: float, horizon_y: int,
                     near=(60, 50, 90), far=(95, 80, 130)) -> None:
    # Far mountains — three triangle peaks
    far_peaks = (
        (-10, horizon_y - 10), (5, horizon_y - 18), (20, horizon_y - 12),
        (35, horizon_y - 22), (50, horizon_y - 14), (65, horizon_y - 20),
        (78, horizon_y - 12), (LW + 10, horizon_y - 16),
    )
    pts = [(-2, horizon_y)] + [(int(x - scroll * 0.1) % (LW + 30) - 5, y)
                                for x, y in far_peaks] + [(LW + 2, horizon_y)]
    # Sort by x to keep a clean silhouette
    pts.sort(key=lambda p: p[0])
    pygame.draw.polygon(canvas, far,
                        [(-2, horizon_y)] + pts + [(LW + 2, horizon_y)])

    # Near mountains — fewer, taller, darker
    near_peaks = (
        (0, horizon_y - 4), (15, horizon_y - 14), (32, horizon_y - 6),
        (48, horizon_y - 18), (66, horizon_y - 8), (85, horizon_y - 14),
    )
    npts = [(-2, horizon_y)] + [(int(x - scroll * 0.25) % (LW + 30) - 5, y)
                                 for x, y in near_peaks] + [(LW + 2, horizon_y)]
    npts.sort(key=lambda p: p[0])
    pygame.draw.polygon(canvas, near,
                        [(-2, horizon_y)] + npts + [(LW + 2, horizon_y)])


def _paint_pillar(canvas: pygame.Surface, x: int, top_y: int) -> None:
    """A pillar from `top_y` down to the bottom of the canvas."""
    top = _SPRITES["pillar_top"]
    mid = _SPRITES["pillar_mid"]
    canvas.blit(top, (x, top_y))
    y = top_y + top.get_height()
    while y < LH:
        canvas.blit(mid, (x, y))
        y += mid.get_height()


def _paint_pip(canvas: pygame.Surface, x: int, y: int, frame_t: float,
               facing: str = "r") -> None:
    f = int(frame_t) % 3
    key = ("pip_" if facing == "r" else "pip_l_") + str(f)
    canvas.blit(_SPRITES[key], (x, y))


# ── beat 1: Dawn at the perch (0.0 – 2.0) ────────────────────────────────────

def _beat_dawn(scene, canvas, u: float) -> None:
    sky = _blend_sky("predawn", "dawn", u)
    _paint_sky(canvas, *sky, horizon_y=108)
    _paint_stars(canvas, alpha=int(180 * (1.0 - u)))
    _paint_mountains(canvas, scroll=0, horizon_y=108)

    # Hero pillar — centred, top at y=70
    px = 38
    pillar_top_y = 70
    _paint_pillar(canvas, px, pillar_top_y)

    # Mailbag + parcel on the ledge
    bag = _SPRITES["mailbag"]
    par = _SPRITES["parcel"]
    canvas.blit(bag, (px - 2, pillar_top_y - 2))
    canvas.blit(par, (px + 6, pillar_top_y - 4))

    # Pip flies in from upper-right and lands by u≈0.7
    if u < 0.7:
        a = u / 0.7
        pip_x = int(LW + 10 - a * (LW + 10 - (px + 8)))
        pip_y = int(40 + a * (pillar_top_y - 12 - 40))
        _paint_pip(canvas, pip_x, pip_y, scene.t * 14, facing="l")
    else:
        # Perched
        _paint_pip(canvas, px + 8, pillar_top_y - 9, frame_t=0, facing="l")


# ── beat 2: Briefing (2.0 – 3.8) ─────────────────────────────────────────────

def _beat_briefing(scene, canvas, u: float) -> None:
    sky = _blend_sky("dawn", "day", u)
    _paint_sky(canvas, *sky, horizon_y=108)
    _paint_mountains(canvas, scroll=10, horizon_y=108)

    # Two pillars side by side
    boss_x, boss_top = 18, 60
    hero_x, hero_top = 56, 70
    _paint_pillar(canvas, boss_x, boss_top)
    _paint_pillar(canvas, hero_x, hero_top)

    # Garrick on the boss pillar, facing right
    g = _SPRITES["garrick"]
    canvas.blit(g, (boss_x - 2, boss_top - g.get_height() + 4))

    # Squawk bubble — pops on between u 0.20 and 0.65
    if 0.20 < u < 0.65:
        sq = _SPRITES["squawk"]
        bob = int(math.sin(scene.t * 12) * 1)
        canvas.blit(sq, (boss_x + 12, boss_top - 18 + bob))

    # Pip on his pillar
    canvas.blit(_SPRITES["pip_l_0"], (hero_x + 2, hero_top - 9))
    # Mailbag stays on the hero ledge
    canvas.blit(_SPRITES["mailbag"], (hero_x - 1, hero_top - 2))

    # Parcel hops from Garrick's pillar to Pip's between u 0.55 and 0.95
    par = _SPRITES["parcel"]
    if u < 0.55:
        canvas.blit(par, (boss_x + 4, boss_top - 4))
    elif u < 0.95:
        a = (u - 0.55) / 0.40
        # Arc trajectory
        sx, sy = boss_x + 4, boss_top - 4
        ex, ey = hero_x + 6, hero_top - 4
        cx = sx + (ex - sx) * a
        cy = sy + (ey - sy) * a - int(math.sin(a * math.pi) * 14)
        canvas.blit(par, (int(cx), int(cy)))
    else:
        canvas.blit(par, (hero_x + 6, hero_top - 4))


# ── beat 3: Journey (3.8 – 9.0) ──────────────────────────────────────────────

# Flight-beat phase waypoints (u in [0, 1]) → sky-name pair + blend t.
def _journey_sky(u: float) -> tuple:
    stops = [
        (0.00, "day",     "day"),
        (0.20, "day",     "golden"),
        (0.40, "golden",  "sunset"),
        (0.60, "sunset",  "night"),
        (0.85, "night",   "sunrise"),
        (1.00, "sunrise", "sunrise"),
    ]
    for i in range(len(stops) - 1):
        u0, a0, _ = stops[i]
        u1, a1, b1 = stops[i + 1]
        if u <= u1:
            seg = 0.0 if u1 <= u0 else (u - u0) / (u1 - u0)
            return a1, b1, seg
    return stops[-1][1], stops[-1][2], 1.0


def _beat_journey(scene, canvas, u: float) -> None:
    a_name, b_name, seg = _journey_sky(u)
    sky = _blend_sky(a_name, b_name, seg)
    _paint_sky(canvas, *sky, horizon_y=120)

    # Sun / moon glides across the sky in a slow arc.
    # Day/golden → sun; sunset transition; night → moon; sunrise → sun
    if u < 0.55 or u > 0.85:
        disc = _SPRITES["sun"]
    else:
        disc = _SPRITES["moon"]
    # arc x: drifts left across the sky as the world scrolls right
    disc_x = int(70 - u * 90)
    disc_y = int(20 + math.sin(u * math.pi) * 10)
    canvas.blit(disc, (disc_x, disc_y))

    # Stars fade in around the night portion.
    if 0.55 < u < 0.90:
        a = 1.0 - abs((u - 0.72) / 0.18)
        _paint_stars(canvas, alpha=int(220 * max(0.0, min(1.0, a))))

    # Parallax mountains scroll right→left under Pip's flight.
    scroll = u * 380.0
    _paint_mountains(canvas, scroll=scroll, horizon_y=120)

    # A few distant pillars scroll past at mid-parallax
    pal_dark = (60, 50, 90)
    for i in range(5):
        base = i * 28 + 10
        x = int((base - scroll * 0.5) % (LW + 24)) - 12
        h = 28 - (i * 3) % 8
        pygame.draw.rect(canvas, pal_dark, (x, 120 - h, 6, h + 36))

    # Pip — bobbing in the centre. Frame cycles fast enough to read as flap
    pip_x = LW // 2 - 6 + int(math.sin(scene.t * 1.2) * 4)
    pip_y = 64 + int(math.sin(scene.t * 2.0) * 6)
    _paint_pip(canvas, pip_x, pip_y, frame_t=scene.t * 14, facing="r")
    # Carried parcel just below Pip
    canvas.blit(_SPRITES["parcel"], (pip_x + 4, pip_y + 12))


# ── beat 4: Arrival (9.0 – 10.5) ─────────────────────────────────────────────

def _beat_arrival(scene, canvas, u: float) -> None:
    sky = _blend_sky("sunrise", "day", u * 0.5)
    _paint_sky(canvas, *sky, horizon_y=110)
    _paint_mountains(canvas, scroll=400, horizon_y=110)

    # Destination pillar — centred
    px, ptop = 36, 64
    _paint_pillar(canvas, px, ptop)
    # Mailbox sits on the ledge
    mb = _SPRITES["mailbox"]
    canvas.blit(mb, (px + 6, ptop - mb.get_height() + 2))

    # Pip glides in from upper-right, lands beside the box
    end_x, end_y = px + 18, ptop - 10
    if u < 0.6:
        a = u / 0.6
        a3 = 1 - (1 - a) ** 3
        pip_x = int(LW + 10 - a3 * (LW + 10 - end_x))
        pip_y = int(20 + a3 * (end_y - 20))
        _paint_pip(canvas, pip_x, pip_y, scene.t * 12, facing="l")
        # Parcel still in talons
        canvas.blit(_SPRITES["parcel"], (pip_x - 4, pip_y + 12))
    else:
        _paint_pip(canvas, end_x, end_y, frame_t=0, facing="l")
        # Parcel drops into the box; flag flick happens via the existing
        # mailbox sprite (its flag is part of the sprite, already raised)
        # Simulate a happy wiggle by drawing a small "ting" line
        if u > 0.7:
            tt = (u - 0.7) / 0.30
            for i, off in enumerate((-4, 0, 4)):
                if tt > i * 0.15:
                    a = max(0, 1 - tt)
                    col = (255, 230, 120)
                    pygame.draw.rect(canvas, col,
                                     (px + 10 + off, ptop - 14 - int(tt * 6),
                                      1, 1))


# ── beat 5: Title (10.5 – 12.0) ──────────────────────────────────────────────

def _label_width(text: str, scale: int) -> int:
    return len(text) * (5 * scale + scale) - scale


def _beat_title(scene, canvas, u: float) -> None:
    sky = _blend_sky("sunrise", "day", min(1.0, u + 0.2))
    _paint_sky(canvas, *sky, horizon_y=130)
    _paint_mountains(canvas, scroll=420 + scene.t * 6, horizon_y=130)

    # Pip drifts gently across the lower frame.
    pip_x = int((scene.t * 18) % (LW + 20)) - 10
    pip_y = 100 + int(math.sin(scene.t * 1.6) * 3)
    _paint_pip(canvas, pip_x, pip_y, frame_t=scene.t * 12, facing="r")

    # SKYBIT — scale 2 so the 6 chars fit in 90 px (width = 70 px, 10 px gutter).
    if u > 0.05:
        title = "SKYBIT"
        ts = 2
        tw = _label_width(title, ts)
        tx = (LW - tw) // 2
        ty = 38
        # Soft dark plate behind the title for readability against any sky.
        plate = pygame.Surface((tw + 8, 7 * ts + 6), pygame.SRCALPHA)
        plate.fill((10, 12, 28, 140))
        canvas.blit(plate, (tx - 4, ty - 3))
        _draw_pixel_label(canvas, title, tx + 1, ty + 1, scale=ts,
                          color=(20, 18, 30))   # drop shadow
        _draw_pixel_label(canvas, title, tx, ty, scale=ts,
                          color=(255, 220, 80))  # gold

    # Subtitle — 12 chars fits at scale 1 (71 px).
    if u > 0.25:
        sub = "BY PIP THE BIRD"
        sw = _label_width(sub, 1)
        sx = (LW - sw) // 2
        _draw_pixel_label(canvas, sub, sx, 60, scale=1,
                          color=(245, 245, 250))

    # Pulsing TAP TO FLY — toggle visibility on a sin pulse for a clean read
    # without alpha-blend headaches on a non-SRCALPHA canvas.
    if u > 0.45:
        pulse = 0.5 + 0.5 * math.sin(scene._title_t * 3.6)
        col = (255, 255, 255) if pulse > 0.35 else (180, 180, 200)
        tap = "TAP TO FLY"
        tw = _label_width(tap, 1)
        tpx = (LW - tw) // 2
        _draw_pixel_label(canvas, tap, tpx, 130, scale=1, color=col)


# ── dispatcher ───────────────────────────────────────────────────────────────

def _dispatch(scene: "IntroScene", canvas: pygame.Surface) -> None:
    t = scene.t
    if t < 2.0:
        _beat_dawn(scene, canvas, t / 2.0)
    elif t < 3.8:
        _beat_briefing(scene, canvas, (t - 2.0) / 1.8)
    elif t < 9.0:
        _beat_journey(scene, canvas, (t - 3.8) / 5.2)
    elif t < 10.5:
        _beat_arrival(scene, canvas, (t - 9.0) / 1.5)
    elif t < DURATION:
        _beat_title(scene, canvas, (t - 10.5) / 1.5)
    else:
        _beat_title(scene, canvas, 1.0)
