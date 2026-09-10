"""HUD: score, hi-score, coin count, power-up timer bar, pause button."""
import math
import os
import random
import pygame

from game.config import W, H, TRIPLE_DURATION, MAGNET_DURATION, MEGAMAGNET_DURATION, SLOWMO_DURATION, KFC_DURATION, GHOST_DURATION, GROW_DURATION, REVERSE_DURATION, SHRINK_DURATION, SKATEBOARD_DURATION, KNIGHT_DURATION, POISON_DURATION, UMBRELLA_DURATION, LIVES_PER_RUN
from game.draw import (
    rounded_rect, rounded_rect_grad, lerp_color,
    UI_SCORE, UI_GOLD, UI_ORANGE, UI_SHADOW, UI_CREAM, UI_RED,
    COIN_GOLD, COIN_DARK,
    WHITE, NEAR_BLACK,
)
from game import parrot
# Run-summary stat-tile icons reuse the actual in-game art so the
# COINS tile shows the spinning coin face the player saw mid-flight.
# (game.powerup_help imports from game.hud — its `_powerup_icon` is
# imported lazily inside draw_stats to avoid the circular import.)
from game.entities import _get_coin_face as _ingame_coin_face
from game.config import COIN_R

_grow_parrot_hud: "pygame.Surface | None" = None

def _get_grow_parrot_hud() -> "pygame.Surface":
    global _grow_parrot_hud
    if _grow_parrot_hud is None:
        src = parrot.FRAMES[1]
        target_w = 16
        ratio = target_w / src.get_width()
        target_h = int(src.get_height() * ratio)
        _grow_parrot_hud = pygame.transform.smoothscale(src, (target_w, target_h))
    return _grow_parrot_hud

# ── Theme palette matching the HTML welcome screen ───────────────────────────
_GOLD_BRIGHT    = (240, 192,  64)   # #f0c040
_GOLD_MUTED     = (216, 184,  85)   # #d8b855
_RED_OUTLINE    = (168,  32,  16)   # #a82010
_ORANGE_BORDER  = (232, 104,  40)   # #e86828
_SCARLET_TOP    = (240,  55,  55)   # #f03737  pill gradient top
_SCARLET_BOT    = (148,  20,  20)   # #941414  pill gradient bottom
# Dim pill colours used by the menu's three CTAs. Tuned so the gradient
# is anchored on _RED_OUTLINE — the rust red that rims the SKYBIT title
# on the same screen — with a brighter highlight above it and a darker
# shade below. The dim path also skips the cream frost overlay (see
# _pill_btn): on a saturated rust gradient the cream tinted the top
# pinkish, which is exactly what made the buttons read as a different
# colour family from the title.
_SCARLET_TOP_DIM = (220,  45,  22)  # #dc2d16  brighter rust (top of grad)
_SCARLET_BOT_DIM = (110,  22,  10)  # #6e160a  darker rust  (bottom of grad)
_SCARLET_SHADOW = ( 60,   8,   8)   # #3c0808  pill text shadow
_GOLD_DEEP      = (180, 130,  20)   # #b48214  inner laurel/ring tone
_GOLD_MID       = (212, 160,  44)   # #d4a02c  mid step for struck bevels
_GOLD_PALE      = (255, 232, 168)   # #ffe8a8  bright highlight for engraving
_PANEL_DARK     = ( 12,   8,  38)   # deep purple panel
_PANEL_LIGHTER  = ( 26,  18,  62)   # navy gradient stop above PANEL_DARK
_NIGHT_DEEP     = (  6,   1,  21)   # #060115

_AWSTAR_SS   = 4
_AWSTAR_GOLD = (240, 192,  64)
_AWSTAR_HI   = (255, 230, 150)
_AWSTAR_RIM  = (140,  90,   8)
_AWSTAR_RIMD = (110,  72,   8)
_AWSTAR_NAVY = ( 12,   8,  38)   # gear centre-hole fill (navy panel family)


_fonts: dict = {}

# ── V15 smooth-taper-weave nest lives display ─────────────────────────────────
_NEST_S          = 0.80
_NEST_CX         = 31
_NEST_CY         = 73
_NEST_DX_LIST    = [0, 40]
_NEST_SCRATCH: "pygame.Surface | None" = None
_NEST_PANEL_DARK   = (12, 8, 38)
_NEST_GOLD_BRIGHT  = (240, 192, 64)
_NEST_OUTER_SHADOW = (4, 4, 12)
_NEST_TWIG_BRIGHT  = (160, 110, 55)
_NEST_TWIG_MID     = (110, 75, 35)
_NEST_TWIG_DARK    = (70, 45, 18)
_NEST_STICK_COL    = (130, 90, 42)
_NEST_STICK_HI     = (170, 120, 60)
_NEST_STICK_SH     = (80,  55, 22)
_NEST_COURSE_TOP   = (180, 130, 65)
_NEST_COURSE_BOT   = (80,  55, 22)
_NEST_HOLLOW_COL   = (50,  35, 14)
_NEST_STICK_X_OFF  = (-1, 0, 1, 2)

_nest_bird: "pygame.Surface | None" = None
_nest_bird_w: int = 0
_nest_bird_h: int = 34
_nest_params: "tuple | None" = None


def _nest_cy_sag(x, x1, x2, base_y, sag):
    half_w = (x2 - x1) / 2.0
    if half_w <= 0:
        return base_y
    t = ((x - x1) / half_w) - 1.0
    return base_y + int(round(sag * (1.0 - t * t)))


def _nest_stick_row(surf, vx, y):
    surf.set_at((vx - 1, y), _NEST_STICK_HI)
    surf.set_at((vx,     y), _NEST_STICK_COL)
    surf.set_at((vx + 1, y), _NEST_STICK_COL)
    surf.set_at((vx + 2, y), _NEST_STICK_SH)


def _nest_stick_span(surf, vx, y1, y2):
    for y in range(y1, y2 + 1):
        _nest_stick_row(surf, vx, y)


def _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col):
    y = _nest_cy_sag(x, x1, x2, base_y, sag)
    surf.set_at((x, y),     _NEST_COURSE_TOP)
    surf.set_at((x, y + 1), mid_col)
    surf.set_at((x, y + 2), mid_col)
    surf.set_at((x, y + 3), _NEST_COURSE_BOT)


def _nest_course_full(surf, x1, x2, base_y, sag, mid_col, skip_xs):
    skip_set = set()
    for sx in skip_xs:
        for dx in _NEST_STICK_X_OFF:
            skip_set.add(sx + dx)
    for x in range(x1, x2 + 1):
        if x not in skip_set:
            _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)


def _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, mid_col):
    for dx in _NEST_STICK_X_OFF:
        x = vx + dx
        if x1 <= x <= x2:
            _nest_course_col(surf, x, x1, x2, base_y, sag, mid_col)


def _nest_stick_at_course(surf, vx, x1, x2, base_y, sag):
    y_top = _nest_cy_sag(vx, x1, x2, base_y, sag)
    for y in range(y_top, y_top + 4):
        _nest_stick_row(surf, vx, y)


def _nest_notches(surf, cy, courses, stick_wins):
    for ci, (offset, col, x1, x2, sag) in enumerate(courses):
        base_y = cy + offset
        for (cii, vx), wins in stick_wins.items():
            if cii != ci:
                continue
            y_cross = _nest_cy_sag(vx, x1, x2, base_y, sag)
            if wins:
                for x in [vx - 2, vx + 3]:
                    if x1 <= x <= x2:
                        surf.set_at((x, y_cross + 1), _NEST_TWIG_DARK)
                        surf.set_at((x, y_cross + 2), _NEST_TWIG_DARK)
            else:
                for dy in (-1, 4):
                    surf.set_at((vx,     y_cross + dy), _NEST_TWIG_DARK)
                    surf.set_at((vx + 1, y_cross + dy), _NEST_TWIG_DARK)


def _nest_weave(surf, cy, ci_range, courses, stick_wins):
    for ci in ci_range:
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        skip = [vx for (cii, vx), wins in stick_wins.items()
                if cii == ci and wins]
        _nest_course_full(surf, x1, x2, base_y, sag, col, skip_xs=skip)
        for (cii, vx), wins in stick_wins.items():
            if cii == ci and not wins:
                _nest_course_at_vx(surf, vx, x1, x2, base_y, sag, col)


def _nest_get_params():
    global _nest_params, _nest_bird, _nest_bird_w
    if _nest_params is not None:
        return _nest_params
    s  = _NEST_S
    cx = _NEST_CX
    r  = lambda v: round(v * s)
    verts = [cx - r(9), cx + r(9)]
    courses = [
        (r(2),  _NEST_TWIG_BRIGHT, cx - r(21), cx + r(21), max(1, r(2))),
        (r(6),  _NEST_TWIG_MID,    cx - r(20), cx + r(20), max(1, r(2))),
        (r(10), _NEST_TWIG_BRIGHT, cx - r(18), cx + r(18), max(1, r(2))),
        (r(14), _NEST_TWIG_MID,    cx - r(16), cx + r(16), max(1, r(2))),
        (r(18), _NEST_TWIG_BRIGHT, cx - r(14), cx + r(14), max(1, r(3))),
    ]
    vxL, vxR = verts
    stick_wins = {(ci, vxL): (ci % 2 == 0) for ci in range(5)}
    stick_wins.update({(ci, vxR): (ci % 2 == 1) for ci in range(5)})
    rim_rect     = (cx - r(21), -r(5), r(42), max(4, r(12)))
    stick_bottom = r(18)
    hollow       = (cx - r(11), r(16), r(22), max(2, r(3)))
    _nest_params = (verts, courses, stick_wins, rim_rect, stick_bottom, hollow)
    src = parrot._get_frames()[1]
    _nest_bird_w = max(1, int(src.get_width() * _nest_bird_h / src.get_height()))
    _nest_bird = pygame.transform.smoothscale(src, (_nest_bird_w, _nest_bird_h))
    return _nest_params


def _nest_draw_chrome_back(surf, cy, verts, courses, stick_wins, rim_rect,
                           stick_bottom, back_arc=False):
    """Everything drawn behind the bird: rim ring, sticks, upper weave."""
    rx, ry_off, rw, rh = rim_rect
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, cy + ry_off, rw, rh))
    if back_arc:
        pygame.draw.arc(surf, _NEST_TWIG_MID, (rx, cy + ry_off, rw, rh),
                        math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, _NEST_TWIG_BRIGHT, (rx, cy + ry_off, rw, rh), 0, math.pi, 2)
    # The arc stop at π leaves a small gap on the bottom-left of the ellipse rim;
    # paint those pixels explicitly so the left stick has no black cap above it.
    _vxL = verts[0]
    for _dy in (-2, -1):
        _y = cy + ry_off + rh + _dy
        for _dx in _NEST_STICK_X_OFF:
            surf.set_at((_vxL + _dx, _y), _NEST_TWIG_BRIGHT)
    for vx in verts:
        _nest_stick_span(surf, vx, cy + ry_off + rh, cy + stick_bottom)
    _nest_weave(surf, cy, (0, 1), courses, stick_wins)


def _nest_draw_chrome_front(surf, cy, courses, stick_wins):
    """Everything drawn in front of the bird: lower weave, sticks, notches."""
    _nest_weave(surf, cy, (2, 3, 4), courses, stick_wins)
    for ci in (2, 3, 4):
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        for (cii, vx), wins in stick_wins.items():
            if cii == ci and wins:
                _nest_stick_at_course(surf, vx, x1, x2, base_y, sag)
    _nest_notches(surf, cy, courses, stick_wins)


_NEST_EMPTY_SPRITE: "pygame.Surface | None" = None
_NEST_EMPTY_SPRITE_CY: int = -1
_NEST_ALIVE_SPRITE: "pygame.Surface | None" = None
_NEST_ALIVE_SPRITE_CY: int = -1


def _nest_build_empty_sprite(cy):
    """Empty-slot art: the nest cup holds a parrot-shaped black void.

    The bird silhouette (zeroed RGB, original alpha) reads as the shadow of
    the missing parrot; the rim ring is kept closed on top of it and stray
    weave/notch marks that land on the void are swept to pure black. Built
    once on a transparent canvas and cached — the art is static.
    """
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow = _nest_get_params()
    cx = _NEST_CX
    rx, ry_off, rw, rh = rim_rect
    # Height covers the lowest weave course (offset + sag + 4 course rows).
    canvas = pygame.Surface((rx + rw + 4, cy + stick_bottom + 10), pygame.SRCALPHA)

    _nest_draw_chrome_back(canvas, cy, verts, courses, stick_wins, rim_rect,
                           stick_bottom, back_arc=True)
    snap = canvas.copy()

    ecx = rx + rw / 2.0
    ecy = cy + ry_off + rh / 2.0
    ra, rb = rw / 2.0, rh / 2.0
    bx = cx - _nest_bird_w // 2
    by = cy - _nest_bird_h // 2 + 5

    # Bird-shaped void: black RGB, bird alpha; clipped to the rim rows and,
    # in the oval's top half, to the oval itself so the head cannot bulge
    # through the back rim.
    sil = pygame.Surface((_nest_bird_w, _nest_bird_h), pygame.SRCALPHA)
    for sy in range(_nest_bird_h):
        py = by + sy
        if py < cy + ry_off:
            continue
        for sx in range(_nest_bird_w):
            a = _nest_bird.get_at((sx, sy))[3]
            if a == 0:
                continue
            px = bx + sx
            if py < ecy and ((px - ecx) / ra) ** 2 + ((py - ecy) / rb) ** 2 > 1.0:
                continue
            sil.set_at((sx, sy), (0, 0, 0, a))
    canvas.blit(sil, (bx, by))

    # The void covered parts of the ring — restore the top rim band from the
    # pre-blit snapshot so the crib mouth stays a closed oval.
    for y in range(cy + ry_off, int(ecy) + 1):
        for x in range(rx, rx + rw + 1):
            c = snap.get_at((x, y))[:3]
            if c in (_NEST_TWIG_BRIGHT, _NEST_TWIG_MID):
                canvas.set_at((x, y), c)
    # Narrow bridge at the far-left edge keeps the wall column continuous
    # between the rim tip and the weave below.
    _by2 = int(ecy) + 1
    for bxp, byp in ((rx, _by2), (rx + 1, _by2), (rx + 1, _by2 + 1)):
        c = snap.get_at((bxp, byp))[:3]
        if c in (_NEST_TWIG_BRIGHT, _NEST_TWIG_MID,
                 _NEST_COURSE_TOP, _NEST_COURSE_BOT):
            canvas.set_at((bxp, byp), c)

    _nest_draw_chrome_front(canvas, cy, courses, stick_wins)

    # The void eats the outer-left wall to a sliver — copy the 3 leftmost
    # wall columns back from a bird-free reference for those rows.
    ref = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
    _nest_draw_chrome_back(ref, cy, verts, courses, stick_wins, rim_rect,
                           stick_bottom, back_arc=True)
    _nest_draw_chrome_front(ref, cy, courses, stick_wins)
    for y in range(cy + 4, cy + 9):
        xl = None
        for x in range(ref.get_width()):
            if ref.get_at((x, y))[3] > 0:
                xl = x
                break
        if xl is None:
            continue
        for x in range(xl, xl + 3):
            canvas.set_at((x, y), ref.get_at((x, y))[:3])

    # Interior sharpen: everything strictly inside the rim ring is pure black.
    ira, irb = ra - 2.0, rb - 2.0
    for y in range(cy + ry_off, cy + ry_off + rh + 1):
        for x in range(rx, rx + rw + 1):
            if ((x - ecx) / ira) ** 2 + ((y - ecy) / irb) ** 2 <= 1.0:
                canvas.set_at((x, y), (0, 0, 0))

    # Stray sweep: weave/notch marks that land on the void read as noise.
    # A brown pixel flanked by opaque near-black within 3 px on both sides
    # sits inside the void, not on the visible weave.
    def _blk(x, y):
        c = canvas.get_at((x, y))
        return c[3] == 255 and c[0] < 12 and c[1] < 12 and c[2] < 12

    # Both sweeps stop above the dark row that joins the right wall to the
    # bottom weave — that line is real border, not noise.
    def _enclosed_sweep():
        for y in range(cy + ry_off, cy + 9):
            for x in range(rx + 1, rx + rw):
                c = canvas.get_at((x, y))
                if c[3] == 0 or c[0] <= 30 or not (c[0] > c[2]):
                    continue
                if _blk(x, y):
                    continue
                lb = any(_blk(x - d, y) for d in (1, 2, 3))
                rb_ = any(_blk(x + d, y) for d in (1, 2, 3))
                if lb and rb_:
                    canvas.set_at((x, y), (0, 0, 0))

    _enclosed_sweep()
    # Bottom-right shoulder: right-stick notch marks land on the black body.
    # Only dark browns go — the bright right-wall / course pixels stay.
    for y in range(cy + 7, cy + 9):
        for x in range(cx + 2, cx + 11):
            c = canvas.get_at((x, y))
            if c[3] == 0 or _blk(x, y):
                continue
            if c[0] < 120 and c[0] > c[2]:
                if any(_blk(x - d, y) for d in (1, 2, 3, 4)):
                    canvas.set_at((x, y), (0, 0, 0))
    # Re-run: the pass above may have freshly enclosed a bright speck.
    _enclosed_sweep()
    # Upper-right shoulder thickening: the ring arc runs 1-2 px there while
    # its left mirror runs 3 — pad each thin column inward with one bright
    # pixel (and close the tip gap) so both shoulders match.
    for px_, dy_ in ((42, -1), (44, 0), (45, 0), (45, 1), (46, 1), (47, 2), (48, 2)):
        canvas.set_at((px_, cy + dy_), _NEST_TWIG_BRIGHT)
    return canvas


def _nest_build_alive_sprite(cy):
    """Alive-slot art: Pip sitting in the nest cup.

    Static, exactly like the empty slot, so it is built once on a transparent
    canvas and cached. Drawn live it costs a few hundred per-pixel twig writes
    every frame, which is invisible natively and expensive in the browser."""
    verts, courses, stick_wins, rim_rect, stick_bottom, hollow = _nest_get_params()
    rx, ry_off, rw, rh = rim_rect
    canvas = pygame.Surface((rx + rw + 4, cy + stick_bottom + 10), pygame.SRCALPHA)
    _nest_draw_chrome_back(canvas, cy, verts, courses, stick_wins, rim_rect,
                           stick_bottom)
    canvas.blit(_nest_bird, (_NEST_CX - _nest_bird_w // 2,
                             cy - _nest_bird_h // 2 + 5))
    _nest_draw_chrome_front(canvas, cy, courses, stick_wins)
    return canvas


def _nest_draw_slot(surf, cy, alive):
    if alive:
        global _NEST_ALIVE_SPRITE, _NEST_ALIVE_SPRITE_CY
        if _NEST_ALIVE_SPRITE is None or _NEST_ALIVE_SPRITE_CY != cy:
            _NEST_ALIVE_SPRITE = _nest_build_alive_sprite(cy)
            _NEST_ALIVE_SPRITE_CY = cy
        surf.blit(_NEST_ALIVE_SPRITE, (0, 0))
    else:
        global _NEST_EMPTY_SPRITE, _NEST_EMPTY_SPRITE_CY
        if _NEST_EMPTY_SPRITE is None or _NEST_EMPTY_SPRITE_CY != cy:
            _NEST_EMPTY_SPRITE = _nest_build_empty_sprite(cy)
            _NEST_EMPTY_SPRITE_CY = cy
        surf.blit(_NEST_EMPTY_SPRITE, (0, 0))


def _draw_pip_lives_row(surf, lives_remaining, lives_total):
    global _NEST_SCRATCH
    n = max(lives_total, 2)
    for i, dx in enumerate(_NEST_DX_LIST[:n]):
        alive = i < lives_remaining
        if dx == 0:
            _nest_draw_slot(surf, _NEST_CY, alive)
        else:
            W, H = surf.get_size()
            if _NEST_SCRATCH is None or _NEST_SCRATCH.get_size() != (W, H):
                _NEST_SCRATCH = pygame.Surface((W, H), pygame.SRCALPHA)
            _NEST_SCRATCH.fill((0, 0, 0, 0))
            _nest_draw_slot(_NEST_SCRATCH, _NEST_CY, alive)
            surf.blit(_NEST_SCRATCH, (dx, 0))


# ── Theme drawing helpers ────────────────────────────────────────────────────

def _outlined_text(surf, txt, center, size, fill=_GOLD_BRIGHT,
                   outline=_RED_OUTLINE, px=3, shadow_offset=(3, 5)):
    """Gold text with red pixel outline — matches the welcome screen title.
    ``shadow_offset=None`` skips the drop shadow for a flat title."""
    f = _font(size, True)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    offsets = [(-px, 0), (px, 0), (0, -px), (0, px),
               (-px, -px), (px, -px), (-px, px), (px, px)]
    for ox, oy in offsets:
        surf.blit(out, (r.x + ox, r.y + oy))
    if shadow_offset is not None:
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(170)
        surf.blit(sh, (r.x + shadow_offset[0], r.y + shadow_offset[1]))
    surf.blit(img, r.topleft)
    return r


# ── Score numerals match the `main` deployment: a cream face over a 2px
# deep-gold rim (a uniform 8-offset stamp) and a soft near-black drop — one
# clear bright shape that reads over a bright-sky pillar and at night. No
# per-frame supersample (just three small text renders per draw), so it is cheap
# enough to run uncached. Drawn inline in draw_play.
_SCORE_FACE = (252, 244, 220)      # warm-cream digit face (the `main` value)


def _pill_btn(surf, center, text, size=20, alpha=255, wide=False,
              min_width=None, primary=False, dim=False, shadow=True):
    """Scarlet body + gold border + cream text, with drop shadow, top-half
    frosting, gold accent line and (optionally) a gold glow when
    ``primary=True`` — the canonical Pip Scarlet pill from the menu
    mockup (see tools/gen_scarlet_set.py::pill). Returns the rect so
    callers can hit-test clicks. ``min_width`` lets paired buttons
    (SUBMIT + SKIP) share one width regardless of label length.
    ``dim=True`` swaps the bright scarlet gradient for the dimmer
    bordeaux pair so the menu trio sits more quietly in the night-sky
    palette. ``shadow=False`` drops the cast shadow — stacked tightly on
    the menu the offset shade read as a detached smudge under each pill,
    so the trio sits flat on the night sky instead."""
    f = _font(size, True)
    img = f.render(text, True, WHITE)
    pad_x = 64 if wide else 44
    pw = img.get_width() + pad_x
    if min_width is not None:
        pw = max(pw, min_width)
    ph = img.get_height() + 22
    cx, cy = center
    x = cx - pw // 2
    y = cy - ph // 2
    grad_top = _SCARLET_TOP_DIM if dim else _SCARLET_TOP
    grad_bot = _SCARLET_BOT_DIM if dim else _SCARLET_BOT

    # Optional gold halo on the primary action button.
    if primary:
        glow = pygame.Surface((pw + 24, ph + 24), pygame.SRCALPHA)
        for r in range(12, 0, -1):
            a = int(48 * r / 12 / 4)
            pygame.draw.rect(glow, (*_GOLD_BRIGHT, a),
                             (12 - r, 12 - r, pw + r * 2, ph + r * 2),
                             border_radius=(ph + r * 2) // 2)
        surf.blit(glow, (x - 12, y - 12))

    # Drop shadow.
    if shadow:
        sh = pygame.Surface((pw + 4, ph + 4), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 90),
                         (0, 0, pw + 4, ph + 4),
                         border_radius=(ph + 4) // 2)
        surf.blit(sh, (x - 2, y + 6))

    # Body: scarlet vertical gradient.
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for yy in range(ph):
        t = yy / max(1, ph - 1)
        c = lerp_color(grad_top, grad_bot, t)
        pygame.draw.line(pill, c, (0, yy), (pw - 1, yy))

    # Frosting on the top half + bottom darkening on the lower half so the
    # gradient reads as a glossy 3D pill rather than a flat colour ramp.
    # On dim pills the cream tinted the saturated rust gradient pinkish
    # — exactly what made the menu CTAs read as a different colour
    # family from the SKYBIT title outline — so we skip the cream
    # frost there and rely on the gradient alone for top highlight.
    if not dim:
        frost = pygame.Surface((pw, ph), pygame.SRCALPHA)
        for yy in range(ph // 2):
            a = int(50 * (1 - yy / (ph / 2)))
            pygame.draw.line(frost, (255, 245, 220, a), (0, yy), (pw, yy))
        pill.blit(frost, (0, 0))
    bsh = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for yy in range(ph // 2, ph):
        a = int(55 * (yy - ph // 2) / (ph / 2))
        pygame.draw.line(bsh, (0, 0, 0, a), (0, yy), (pw, yy))
    pill.blit(bsh, (0, 0))

    # Clip to a rounded-rect mask.
    mask = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, pw, ph),
                     border_radius=ph // 2)
    pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Gold border + thin gold accent line just inside the top.
    pygame.draw.rect(pill, _GOLD_BRIGHT, (0, 0, pw, ph),
                     width=2, border_radius=ph // 2)
    pygame.draw.line(pill, (*_GOLD_BRIGHT, 110),
                     (ph // 2, 3), (pw - ph // 2, 3), 1)

    pill.set_alpha(alpha)
    surf.blit(pill, (x, y))

    # Label: scarlet shadow then cream face, so the text feels embossed
    # rather than floating on top of the gradient.
    sh_img = f.render(text, True, _SCARLET_SHADOW)
    sh_img.set_alpha(220)
    tr = img.get_rect(center=(cx, cy))
    surf.blit(sh_img, (tr.x + 1, tr.y + 1))
    surf.blit(img, tr)

    return pygame.Rect(x, y, pw, ph)


def _dark_panel(surf, rect, radius=16, alpha=210):
    """Deep-navy panel with a thin gold trim, a gold accent rail just
    under the top edge and a soft drop shadow — the canonical Pip
    Scarlet card treatment shared by every menu / overlay screen.
    Visual reference: tools/gen_scarlet_set.py::card."""
    # Drop shadow under the card.
    sh = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, rect.width + 4, rect.height + 4),
                     border_radius=radius)
    surf.blit(sh, (rect.x - 2, rect.y + 4))

    # Body + thin gold border.
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*_PANEL_DARK, alpha),
                     (0, 0, rect.width, rect.height),
                     border_radius=radius)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 130),
                     (0, 0, rect.width, rect.height),
                     width=1, border_radius=radius)

    # Gold accent rail just inside the top.
    inset = max(radius - 2, 6)
    rail_w = max(rect.width - inset * 2, 0)
    if rail_w > 0:
        accent = pygame.Surface((rail_w, 2), pygame.SRCALPHA)
        accent.fill((*_GOLD_BRIGHT, 110))
        pnl.blit(accent, (inset, 4))
        pygame.draw.line(pnl, (255, 220, 140, 90),
                         (inset, 2),
                         (rect.width - inset, 2), 1)
    surf.blit(pnl, rect.topleft)


def _volume_panel(surf, rect, radius=14, alpha=235):
    """Heavier emboss treatment for menu stat panels — gradient body
    (_PANEL_LIGHTER → _PANEL_DARK), 2 px gold border, inner top sheen
    + bottom shadow, and a 4-step drop shadow. Used by ``draw_menu`` for
    the BEST + TOP 10 cards so they sit with real volume against the
    scarlet pill buttons above them."""
    # 4-step drop shadow — softer, more diffuse than _dark_panel's.
    sh = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
    for k in range(4):
        a = 80 - k * 16
        pygame.draw.rect(sh, (0, 0, 0, a),
                         (k, k * 2, rect.width + 8 - k * 2,
                          rect.height + 8 - k * 2),
                         border_radius=radius)
    surf.blit(sh, (rect.x - 4, rect.y + 2))

    # Gradient body — lighter at top, dark at bottom, fixed alpha.
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    for yy in range(rect.height):
        t = yy / max(1, rect.height - 1)
        r = int(_PANEL_LIGHTER[0] * (1 - t) + _PANEL_DARK[0] * t)
        g = int(_PANEL_LIGHTER[1] * (1 - t) + _PANEL_DARK[1] * t)
        b = int(_PANEL_LIGHTER[2] * (1 - t) + _PANEL_DARK[2] * t)
        pygame.draw.line(pnl, (r, g, b, alpha),
                         (0, yy), (rect.width - 1, yy))
    # Clip to a rounded-rect mask.
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, rect.width, rect.height), border_radius=radius)
    pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # 2 px gold border + inner top sheen + inner bottom shadow.
    pygame.draw.rect(pnl, _GOLD_BRIGHT, (0, 0, rect.width, rect.height),
                     width=2, border_radius=radius)
    pygame.draw.line(pnl, (*_GOLD_PALE, 140),
                     (10, 3), (rect.width - 10, 3), 1)
    pygame.draw.line(pnl, (0, 0, 0, 80),
                     (10, rect.height - 4),
                     (rect.width - 10, rect.height - 4), 1)
    surf.blit(pnl, rect.topleft)


def _draw_overlay_stars(surf, stars, t):
    """Twinkle star field. `stars` = list of (x,y,r,phase) from HUD.__init__."""
    for x, y, r, phase in stars:
        a = int(30 + 200 * (0.5 + 0.5 * math.sin(t * 1.4 + phase)))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, a), (r + 1, r + 1), r)
        surf.blit(s, (x - r - 1, y - r - 1))


# ── Top-10 #1 crown sprite + medal-row gradient helpers ─────────────────────
# Procedural narrow-E3 ("Diamond Trio") crown that perches on the rank-1 row's
# gold badge. Sprite is built once, then cached + blit each frame.

_CROWN_OS = 2  # oversample factor — drawn at 2× target then smoothscaled

_CROWN_GOLD_HI    = (255, 232, 132)
_CROWN_GOLD       = (240, 192,  64)
_CROWN_GOLD_LO    = (188, 138,  28)
_CROWN_GOLD_DEEP  = (110,  72,   8)
_CROWN_OUTLINE    = ( 28,  18,   4)
_CROWN_RUBY       = (220,  40,  50)
_CROWN_RUBY_HI    = (255, 180, 190)
_CROWN_SAPPHIRE   = ( 64, 102, 220)
_CROWN_SAPPHIRE_HI= (172, 200, 255)
_CROWN_WHITE_HI   = (255, 255, 255)
_CROWN_PEARL      = (240, 232, 215)   # warm off-white gem face
_CROWN_PEARL_HI   = (255, 248, 230)   # bright highlight on the pearl gem

# Medal-row vertical gradients used on ranks 1, 2, 3 in draw_leaderboard
_MEDAL_GRADIENTS = {
    1: ((240, 192,  64), (180, 130,  20)),     # gold
    2: ((215, 222, 232), (110, 125, 145)),     # silver
    3: ((215, 150,  85), (125,  74,  28)),     # bronze
}


def _crown_aura(surf, cx, cy, radii, alphas):
    """Soft concentric golden halo behind the crown."""
    for r, a in zip(radii, alphas):
        glow = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(glow,
                            (_CROWN_GOLD[0], _CROWN_GOLD[1],
                             _CROWN_GOLD[2], a),
                            (0, 0, r * 2, r * 2))
        surf.blit(glow, (cx - r, cy - r))


def _crown_band(big, s, l, top, r, bot):
    """Gold-gradient band with NEAR_BLACK perimeter outline."""
    pygame.draw.rect(big, _CROWN_OUTLINE,
                     (l - 1, top + s, r - l + 2, bot - top),
                     border_radius=s)
    h = bot - top
    for yy in range(h):
        u = yy / max(1, h - 1)
        col = tuple(int(_CROWN_GOLD_HI[i] * (1 - u) + _CROWN_GOLD_LO[i] * u)
                    for i in range(3))
        pygame.draw.line(big, col + (255,),
                         (l, top + yy), (r - 1, top + yy))
    pygame.draw.rect(big, _CROWN_OUTLINE,
                     (l, top, r - l, bot - top),
                     border_radius=s, width=2 * s)


def _crown_sheen(big, s, band_top, band_bot, band_l, band_r):
    """Single GOLD_HI horizontal stripe ~25 % down the band — metallic glint."""
    y = band_top + (band_bot - band_top) // 4
    pygame.draw.line(big, _CROWN_GOLD_HI,
                     (band_l + 2 * s, y), (band_r - 2 * s, y),
                     max(1, s // 2))


def _crown_outlined_polygon(surf, pts, fill, hi=None):
    """Filled polygon with a NEAR_BLACK outline + optional highlight."""
    pygame.draw.polygon(surf, _CROWN_OUTLINE, pts, max(2, _CROWN_OS * 2))
    pygame.draw.polygon(surf, fill, pts)
    if hi is not None and len(pts) >= 3:
        mid = ((pts[0][0] + pts[1][0]) / 2,
               (pts[0][1] + pts[1][1]) / 2)
        pygame.draw.polygon(surf, hi, [pts[0], pts[1], mid])


def _crown_outlined_gem(surf, cx, cy, r, col, hi):
    """Round cabochon with NEAR_BLACK outline + white highlight."""
    pygame.draw.circle(surf, _CROWN_OUTLINE, (cx, cy + 1), r + 1)
    pygame.draw.circle(surf, col, (cx, cy), r)
    pygame.draw.circle(surf, hi,
                       (cx - max(1, r // 3), cy - max(1, r // 3)),
                       max(1, r // 2))
    pygame.draw.circle(surf, _CROWN_OUTLINE, (cx, cy), r,
                       max(1, _CROWN_OS // 2))


def _crown_with_shadow(img, offset=(2, 2), alpha=110):
    """Composite soft drop shadow under the crown sprite."""
    shadow = img.copy()
    shadow.fill((0, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
    shadow.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    composite = pygame.Surface(
        (img.get_width() + offset[0], img.get_height() + offset[1]),
        pygame.SRCALPHA)
    composite.blit(shadow, offset)
    composite.blit(img, (0, 0))
    return composite


def _crown_draw_e3_narrow(big, s):
    """Narrow Diamond Trio — 3 peaks with kite-cut sapphire/ruby/sapphire,
    aura behind, sparkles around. Sized for a 24 × 28 bbox so it tucks
    inside the rank-1 gold badge (radius 13)."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    _crown_aura(big, cx, bh - 9 * s,
                radii=[9 * s, 6 * s, 4 * s],
                alphas=[40, 65, 95])

    band_h = 6 * s
    band_top = bh - band_h
    band_bot = bh
    band_l = 1 * s
    band_r = bw - 1 * s
    _crown_band(big, s, band_l, band_top, band_r, band_bot)
    _crown_sheen(big, s, band_top, band_bot, band_l, band_r)

    band_cy = (band_top + band_bot) // 2
    _crown_outlined_gem(big, cx, band_cy, int(1.2 * s),
                        _CROWN_RUBY, _CROWN_RUBY_HI)

    # V4 tiered: 3 tall vertical main peaks + 2 shorter outer peaks
    # leaning outward. Gem palette: ruby on the three centre peaks,
    # sapphire on the two outer leaning peaks. Sits inside the original
    # 24×28 bbox so the crown stays the same width as before.
    full_peak_h  = bh - band_h - 5 * s
    short_peak_h = int(full_peak_h * 0.62)
    full_tip_y   = band_top - full_peak_h
    short_tip_y  = band_top - short_peak_h

    def _peak(base_x, tip_x, tip_y, base_pw, gem_half_w, gem_fill, gem_hi):
        l   = (base_x - base_pw, band_top)
        r   = (base_x + base_pw, band_top)
        tip = (tip_x, tip_y)
        _crown_outlined_polygon(big, [tip, l, r],
                                _CROWN_GOLD, _CROWN_GOLD_HI)
        gem_top   = (tip_x, tip_y - int(2.5 * s))
        gem_bot   = (tip_x, tip_y - int(0.3 * s))
        gem_left  = (tip_x - int(gem_half_w * s), tip_y - int(1.4 * s))
        gem_right = (tip_x + int(gem_half_w * s), tip_y - int(1.4 * s))
        _crown_outlined_polygon(big,
                                [gem_top, gem_right, gem_bot, gem_left],
                                gem_fill, gem_hi)
        pygame.draw.line(big, _CROWN_WHITE_HI,
                         (gem_top[0] - 1, gem_top[1] + 1),
                         (gem_top[0] - 1, gem_top[1] + int(1.5 * s)),
                         max(1, s // 2))

    # Gem pattern numbered left-to-right (1..5):
    #   1 sapphire — 2 pearl — 3 ruby — 4 pearl — 5 sapphire
    inner_gems = [
        (_CROWN_PEARL, _CROWN_PEARL_HI),   # peak 2 (left centre)
        (_CROWN_RUBY,  _CROWN_RUBY_HI),    # peak 3 (centre)
        (_CROWN_PEARL, _CROWN_PEARL_HI),   # peak 4 (right centre)
    ]
    # 3 tall vertical centre peaks
    for px, (fill, hi) in zip((cx - 6 * s, cx, cx + 6 * s), inner_gems):
        _peak(px, px, full_tip_y, max(2, int(1.4 * s)), 1.2, fill, hi)

    # 2 outer shorter peaks leaning outward — sapphire gems (peaks 1, 5)
    for sign in (-1, 1):
        base_x = cx + sign * 9 * s
        tip_x  = cx + sign * 11 * s
        _peak(base_x, tip_x, short_tip_y, max(2, int(1.0 * s)), 0.7,
              _CROWN_SAPPHIRE, _CROWN_SAPPHIRE_HI)

    # Tight sparkles around the bbox
    cx_pix = bw // 2
    cy_pix = bh // 2
    for x_frac, y_frac in [(-0.85, -0.55), (0.85, -0.55),
                            (-0.70,  0.25), (0.70,  0.25)]:
        sx = int(cx_pix + x_frac * (bw // 2))
        sy = int(cy_pix + y_frac * (bh // 2))
        sx = max(2, min(bw - 2, sx))
        sy = max(2, min(bh - 2, sy))
        pygame.draw.line(big, _CROWN_WHITE_HI,
                         (sx - int(1.5 * s), sy),
                         (sx + int(1.5 * s), sy),
                         max(1, s // 2))
        pygame.draw.line(big, _CROWN_WHITE_HI,
                         (sx, sy - int(1.5 * s)),
                         (sx, sy + int(1.5 * s)),
                         max(1, s // 2))


_CROWN_SPRITE_CACHE: "pygame.Surface | None" = None
_CROWN_HD_CACHE: "dict[int, pygame.Surface]" = {}


def _get_crown_sprite() -> "pygame.Surface":
    """Build the rank-1 crown sprite once, cache it. Identical every
    frame — no animation, no per-row state."""
    global _CROWN_SPRITE_CACHE
    if _CROWN_SPRITE_CACHE is None:
        bw, bh = 24, 28
        big = pygame.Surface((bw * _CROWN_OS, bh * _CROWN_OS),
                             pygame.SRCALPHA)
        _crown_draw_e3_narrow(big, _CROWN_OS)
        small = pygame.transform.smoothscale(big, (bw, bh))
        _CROWN_SPRITE_CACHE = _crown_with_shadow(small)
    return _CROWN_SPRITE_CACHE


def _get_crown_sprite_hd(S: int) -> "pygame.Surface":
    """HD crown sprite at S × native, cached per scale factor."""
    if S == 1:
        return _get_crown_sprite()
    cached = _CROWN_HD_CACHE.get(S)
    if cached is None:
        bw, bh = 24, 28
        os_factor = _CROWN_OS * S
        big = pygame.Surface((bw * os_factor, bh * os_factor),
                             pygame.SRCALPHA)
        _crown_draw_e3_narrow(big, os_factor)
        small = pygame.transform.smoothscale(big, (bw * S, bh * S))
        cached = _crown_with_shadow(small, offset=(2 * S, 2 * S))
        _CROWN_HD_CACHE[S] = cached
    return cached


def _medal_row_pill(card_w, row_h, row_radius, rank):
    """Render the gold/silver/bronze gradient pill surface for a top-3
    rank. Returns a SRCALPHA surface ready to blit at the row origin."""
    top_col, bot_col = _MEDAL_GRADIENTS[rank]
    pnl = pygame.Surface((card_w, row_h), pygame.SRCALPHA)
    for yy in range(row_h):
        u = yy / max(1, row_h - 1)
        r = int(top_col[0] * (1 - u) + bot_col[0] * u)
        g = int(top_col[1] * (1 - u) + bot_col[1] * u)
        b = int(top_col[2] * (1 - u) + bot_col[2] * u)
        pygame.draw.line(pnl, (r, g, b, 255), (0, yy), (card_w, yy))
    mask = pygame.Surface((card_w, row_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, card_w, row_h),
                     border_radius=row_radius)
    pnl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    pygame.draw.rect(pnl, NEAR_BLACK, (0, 0, card_w, row_h),
                     width=2, border_radius=row_radius)
    return pnl


# ── Tabbed leaderboard (live CURRENT board + read-only LEGACY board) ──────────
# Geometry in native (W×H) units; multiplied by S when drawn into the
# supersampled cache, and reused as-is for screen-space hit rects because the
# game window is exactly W×H (scenes.py: set_mode((W, H))).
_LB_HEADER_Y = 32
_LB_TAB_Y    = 52
_LB_TAB_H    = 30
_LB_SUB_Y    = 90
_LB_CARD_Y   = 124
_LB_ROW_H    = 35
_LB_ROW_GAP  = 4
_LB_SEAL_R   = 30
_LB_BRONZE   = (150, 105, 55)   # tarnished legacy coin (vs bright gold = live)


def _lb_tab_geometry():
    """Native-unit (x, y, w, h) of the segmented CURRENT|LEGACY tab strip."""
    return 14, _LB_TAB_Y, W - 28, _LB_TAB_H


def _draw_lb_tabs(surf, S, selected_tab):
    """Segmented two-tab control: filled-gold selected half vs hollow-navy
    deselected, each carrying its era coin (bright gold = live CURRENT,
    tarnished bronze = frozen LEGACY) so the boards read apart by value +
    shape, not colour alone."""
    tx, ty, tw, th = _lb_tab_geometry()
    x, y, w, h = tx * S, ty * S, tw * S, th * S
    rad = h // 2
    track = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(track, (*_PANEL_DARK, 235), (0, 0, w, h),
                     border_radius=rad)
    surf.blit(track, (x, y))

    half = w // 2
    f = _font(14 * S, True)
    coin_r = 6 * S
    tabs = (("CURRENT", _GOLD_BRIGHT), ("LEGACY", _LB_BRONZE))
    for idx, (label, coin_col) in enumerate(tabs):
        hx = x + (0 if idx == 0 else half)
        hw = half if idx == 0 else (w - half)
        selected = (idx == selected_tab)
        if selected:
            fill = pygame.Surface((hw, h), pygame.SRCALPHA)
            for yy in range(h):
                fc = lerp_color(_GOLD_BRIGHT, _GOLD_DEEP, yy / max(1, h - 1))
                pygame.draw.line(fill, fc, (0, yy), (hw, yy))
            mask = pygame.Surface((hw, h), pygame.SRCALPHA)
            if idx == 0:
                pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, hw, h),
                                 border_top_left_radius=rad,
                                 border_bottom_left_radius=rad)
            else:
                pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, hw, h),
                                 border_top_right_radius=rad,
                                 border_bottom_right_radius=rad)
            fill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            surf.blit(fill, (hx, y))
            txt_col = NEAR_BLACK
        else:
            txt_col = _GOLD_BRIGHT

        img = f.render(label, True, txt_col)
        if not selected:
            img.set_alpha(216)   # deselected reads "tappable", never disabled
        group_w = coin_r * 2 + 5 * S + img.get_width()
        gx = hx + (hw - group_w) // 2
        ccx, ccy = gx + coin_r, y + h // 2
        pygame.draw.circle(surf, coin_col, (ccx, ccy), coin_r)
        pygame.draw.circle(surf, NEAR_BLACK, (ccx, ccy), coin_r, max(1, S))
        pygame.draw.circle(surf, (*WHITE, 150),
                           (ccx - coin_r // 3, ccy - coin_r // 3),
                           max(1, coin_r // 3))
        surf.blit(img, (gx + coin_r * 2 + 5 * S, ccy - img.get_height() // 2))

    pygame.draw.rect(surf, _GOLD_BRIGHT, (x, y, w, h),
                     width=max(1, 2 * S), border_radius=rad)
    pygame.draw.line(surf, (*_GOLD_BRIGHT, 120),
                     (x + half, y + 4 * S), (x + half, y + h - 4 * S),
                     max(1, S))


def _draw_lb_subline(surf, S, selected_tab):
    """CURRENT shows a plain 'LIVE' tag; LEGACY shows a one-line frozen
    ribbon so a low live score never reads as broken next to the older,
    higher hall-of-fame numbers."""
    cx = (W * S) // 2
    cy = _LB_SUB_Y * S
    if selected_tab == 0:
        _text(surf, "LIVE", (cx, cy), size=12 * S, color=_GOLD_MUTED,
              shadow=False)
        return
    f = _font(11 * S, True)
    img = f.render("FROZEN   ·   HALL OF FAME", True, _GOLD_PALE)
    rw, rh = img.get_width() + 30 * S, img.get_height() + 8 * S
    rx, ry = cx - rw // 2, cy - rh // 2
    bar = pygame.Surface((rw, rh), pygame.SRCALPHA)
    for yy in range(rh):
        bc = lerp_color((40, 46, 86), (74, 60, 30), yy / max(1, rh - 1))
        pygame.draw.line(bar, bc, (0, yy), (rw, yy))
    mask = pygame.Surface((rw, rh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rw, rh),
                     border_radius=rh // 2)
    bar.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(bar, (*_GOLD_DEEP, 210), (0, 0, rw, rh),
                     width=max(1, S), border_radius=rh // 2)
    surf.blit(bar, (rx, ry))
    surf.blit(img, (cx - img.get_width() // 2, cy - img.get_height() // 2))
    # Two hard frost ticks at the ribbon ends (flat, no feathery flourishes).
    for ex in (rx - 4 * S, rx + rw):
        pts = [(ex, cy), (ex + 3 * S, cy - 3 * S),
               (ex + 6 * S, cy), (ex + 3 * S, cy + 3 * S)]
        pygame.draw.polygon(surf, _GOLD_PALE, pts)


def _draw_final_seal(surf, cx, cy, r, S):
    """Procedural wax 'FINAL' seal — a scalloped scarlet disc — marking the
    legacy board as a closed, frozen archive rather than an error state."""
    n = 18
    for k in range(n):
        ang = 2 * math.pi * k / n
        ex = cx + int(math.cos(ang) * r)
        ey = cy + int(math.sin(ang) * r)
        pygame.draw.circle(surf, _SCARLET_BOT, (ex, ey), int(r * 0.2))
    pygame.draw.circle(surf, _SCARLET_TOP, (cx, cy), r)
    pygame.draw.circle(surf, _SCARLET_BOT, (cx, cy), r, max(1, 2 * S))
    pygame.draw.circle(surf, (*_GOLD_PALE, 90), (cx, cy), int(r * 0.72),
                       max(1, S))
    f = _font(int(r * 0.46), True)
    img = pygame.transform.rotate(f.render("FINAL", True, _GOLD_PALE), 12)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def _draw_trophy(surf, cx, cy, size):
    """Gold procedural trophy icon. `size` is approximate half-height.
    Drawn fully symmetric about a vertical axis through (cx, cy):
      * Cup widths use the same ±half-width on left & right
      * Handles drawn on a temp surface and mirrored via transform.flip
      * Stem / base / foot use odd widths so they centre exactly
    All sub-element widths/thicknesses scale with ``size`` so the
    silhouette reads as a trophy (cup + handles + base) at any render
    scale — at retina S=2/3, hardcoded 2-3 px features would otherwise
    smoothscale into invisible threads.
    """
    s = int(round(size))
    # Scaled sub-element dimensions
    h_w           = max(5, s // 3)        # handle ear half-width
    arc_thickness = max(2, s // 6)        # handle stroke
    stem_w        = max(3, (s // 6) | 1)  # stem width — odd for centring
    rim_h         = max(1, s // 10)       # cup-rim highlight
    base_h        = max(3, s // 6)        # base height
    foot_h        = max(2, s // 9)        # foot pad height

    pad   = h_w + 2
    g_w   = (s + pad) * 2 + 1   # odd → exact centre column
    g_h   = s * 3 + 6
    g     = pygame.Surface((g_w, g_h), pygame.SRCALPHA)
    gx    = g_w // 2
    gy    = s + 2

    GOLD  = (240, 192,  64, 255)
    DARK  = (140,  90,   8, 255)
    WHITE = (255, 248, 200, 180)

    # ── Cup body — symmetric trapezoid (wider at top) ──────────────────────
    half_top = s
    half_bot = s - 3
    top_y = gy - s + 2
    bot_y = gy + 2
    cup_pts = [
        (gx - half_top, top_y),
        (gx + half_top, top_y),
        (gx + half_bot, bot_y),
        (gx - half_bot, bot_y),
    ]
    # Symmetric drop shadow — grow the silhouette down + on both sides
    cup_shadow = [
        (gx - half_top - 1, top_y + 1),
        (gx + half_top + 1, top_y + 1),
        (gx + half_bot + 1, bot_y + 1),
        (gx - half_bot - 1, bot_y + 1),
    ]
    pygame.draw.polygon(g, DARK, cup_shadow)
    pygame.draw.polygon(g, GOLD, cup_pts)
    # pygame.draw.polygon excludes the right/bottom boundary by convention,
    # which leaves a one-pixel gap on the right slope. Draw the slope as a
    # line explicitly so left/right edges are pixel-symmetric.
    pygame.draw.line(g, GOLD,
                     (gx + half_top, top_y),
                     (gx + half_bot, bot_y), 1)
    pygame.draw.line(g, WHITE,
                     (gx - half_top + 2, top_y + 1),
                     (gx + half_top - 2, top_y + 1), rim_h)

    # ── Handles — draw the left ear once, then horizontal-flip for right ──
    h_h  = max(4, s - 2)
    h_y  = top_y + 2
    ear  = pygame.Surface((h_w, h_h), pygame.SRCALPHA)
    # Left half of an ellipse — gives a nice C-shape opening right
    pygame.draw.arc(ear, GOLD, (0, 0, h_w * 2 - 1, h_h),
                    math.pi * 0.5, math.pi * 1.5, arc_thickness)
    # Mirror about the cup's vertical centre. Left ear ends at gx - half_top;
    # right ear starts at gx + half_top + 1 so the two ears occupy mirrored
    # column ranges.
    left_ear_x  = gx - half_top - h_w + 1
    right_ear_x = gx + half_top
    g.blit(ear, (left_ear_x, h_y))
    g.blit(pygame.transform.flip(ear, True, False),
           (right_ear_x, h_y))

    # ── Stem — odd width, exact centre ────────────────────────────────────
    stem_h  = s // 2
    stem_x  = gx - stem_w // 2
    pygame.draw.rect(g, DARK,  (stem_x - 1, bot_y + 1, stem_w + 2, stem_h + 1))
    pygame.draw.rect(g, GOLD,  (stem_x,     bot_y,     stem_w,     stem_h))

    # ── Base + foot — both odd-width so they centre exactly ───────────────
    base_w = (s - 1) * 2 + 1
    base_x = gx - base_w // 2
    base_y = bot_y + stem_h
    pygame.draw.rect(g, DARK,  (base_x - 1, base_y + 1, base_w + 2, base_h + 1))
    pygame.draw.rect(g, GOLD,  (base_x,     base_y,     base_w,     base_h))

    foot_w = base_w + 2
    foot_x = gx - foot_w // 2
    foot_y = base_y + base_h
    pygame.draw.rect(g, DARK,  (foot_x - 1, foot_y + 1, foot_w + 2, foot_h + 1))
    pygame.draw.rect(g, GOLD,  (foot_x,     foot_y,     foot_w,     foot_h))

    surf.blit(g, (cx - gx, cy - gy))


def _draw_mountain_silhouette(surf, alpha=200):
    """Mountain silhouettes at the bottom — matches the welcome-screen SVG."""
    mtn = pygame.Surface((W, H), pygame.SRCALPHA)
    far = [(0,H),(0,490),(60,420),(120,450),(200,375),(280,430),
           (360,360),(W,400),(W,H)]
    near= [(0,H),(0,530),(80,505),(160,520),(240,490),(320,510),(W,495),(W,H)]
    pygame.draw.polygon(mtn, (14, 26, 12, alpha), far)
    pygame.draw.polygon(mtn, (10, 18,  8, alpha), near)
    surf.blit(mtn, (0, 0))


# Vendored Liberation Sans (metric-compatible Arial replacement) so the
# browser/pygbag build doesn't depend on a system font that isn't there.
_FONT_DIR = os.path.join(os.path.dirname(__file__), "assets")
_FONT_BOLD = os.path.join(_FONT_DIR, "LiberationSans-Bold.ttf")
# LiberationSans-Regular.ttf used to live alongside Bold and back the
# `bold=False` path here, but only two call sites ever passed False
# (a stats-row caption + a name-entry placeholder) and visually they
# read fine in the Bold face. Shipping the Regular file added ~400 KB
# to the WASM bundle for no real gain, so the file was retired and
# `bold=False` now falls through to the Bold ttf.


def _font(size, bold=True):
    k = (size, True)
    f = _fonts.get(k)
    if f is None:
        f = pygame.font.Font(_FONT_BOLD, size)
        _fonts[k] = f
    return f


def _text(surf, txt, center, size=36, color=WHITE, shadow=True):
    f = _font(size, True)
    img = f.render(txt, True, color)
    r = img.get_rect(center=center)
    if shadow:
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(170)
        surf.blit(sh, (r.x + 2, r.y + 3))
    surf.blit(img, r.topleft)
    return r


def _coin_icon(surf, cx, cy, r=10):
    # Reuse the cached high-quality coin face from entities so the HUD pill
    # carries the same gradient + bold outline + embossed parrot + specular
    # highlight as the in-world coin.
    from game.entities import _get_coin_face
    face = _get_coin_face()
    target = pygame.transform.smoothscale(face, (r * 2 + 2, r * 2 + 2))
    rect = target.get_rect(center=(cx, cy))
    surf.blit(target, rect.topleft)


def _draw_gear(surf, cx, cy, R, teeth=None):
    """Struck-metal cog — the SETTINGS sibling to the AWARDS star + TOP 10
    trophy. Supersampled then smoothscaled so teeth + hole stay crisp at the
    ~18 px tile size. At R<=10 a 6-tooth cog + tight hole keeps the same solid
    disc-with-teeth weight as the star/trophy; larger renders keep 8 teeth."""
    if teeth is None:
        teeth = 6 if R <= 10 else 8
    hole = 0.24 if R <= 10 else 0.30
    SS = _AWSTAR_SS
    box = int(R * 2 + 6)
    B = box * SS
    c = B / 2
    g = pygame.Surface((B, B), pygame.SRCALPHA)
    Ro = R * SS                 # tooth-tip radius
    Rb = R * SS * 0.74          # gear-body radius
    hw = math.radians(360.0 / teeth * 0.34)   # tooth half-angle at the base
    for i in range(teeth):
        a = 2 * math.pi * i / teeth
        pts = [
            (c + Rb * math.cos(a - hw), c + Rb * math.sin(a - hw)),
            (c + Ro * math.cos(a - hw * 0.62), c + Ro * math.sin(a - hw * 0.62)),
            (c + Ro * math.cos(a + hw * 0.62), c + Ro * math.sin(a + hw * 0.62)),
            (c + Rb * math.cos(a + hw), c + Rb * math.sin(a + hw)),
        ]
        pygame.draw.polygon(g, _AWSTAR_RIM, pts)
        inset = [(px - (px - c) * 0.10, py - (py - c) * 0.10) for px, py in pts]
        pygame.draw.polygon(g, _AWSTAR_GOLD, inset)
    pygame.draw.circle(g, _AWSTAR_GOLD, (c, c), Rb)
    pygame.draw.circle(g, _AWSTAR_RIM, (c, c), Rb, max(1, int(0.9 * SS)))
    pygame.draw.circle(g, _AWSTAR_HI, (c - Rb * 0.24, c - Rb * 0.24), Rb * 0.30)
    pygame.draw.circle(g, _AWSTAR_GOLD, (c, c), Rb * 0.70)
    pygame.draw.circle(g, _AWSTAR_NAVY, (c, c), R * SS * hole)
    pygame.draw.circle(g, _AWSTAR_RIMD, (c, c), R * SS * hole, max(1, int(0.9 * SS)))
    small = pygame.transform.smoothscale(g, (box, box))
    surf.blit(small, (int(round(cx - box / 2)), int(round(cy - box / 2))))


def _tracked_label(surf, text, center, size, color=_GOLD_PALE, track=0, alpha=230):
    """Render a label with optional per-letter tracking, so a tight menu chip
    can pull a caption in without the wide 'A W A R D S' letter spacing."""
    f = _font(size, True)
    if track == 0:
        img = f.render(text, True, color)
        img.set_alpha(alpha)
        surf.blit(img, img.get_rect(center=center))
        return
    glyphs = [f.render(ch, True, color) for ch in text]
    total = sum(gg.get_width() for gg in glyphs) + track * (len(glyphs) - 1)
    x = center[0] - total // 2
    for gg in glyphs:
        gg.set_alpha(alpha)
        surf.blit(gg, (x, center[1] - gg.get_height() // 2))
        x += gg.get_width() + track


def _profile_tri(surf, cx, cy, size, color):
    """Right-pointing 'tap through' chevron for the PROFILE nameplate — the
    vendored font has no such glyph, so it is a small filled triangle."""
    pygame.draw.polygon(surf, color, [(cx - size // 2, cy - size),
                                      (cx + size // 2, cy),
                                      (cx - size // 2, cy + size)])


# ── Harbour-post menu furniture ─────────────────────────────────────────────
# The main menu's signage: three plank signs slung on ropes from the cottage's
# cloud, START planted on its own post in the bottom-right, and the square
# jewel frame that turns the standing-Pip diorama into the PROFILE entry.
#
# None of it reads game state, so the whole set is baked once into a single
# transparent layer and blitted — the same cache discipline as the nest slots
# above. Rebuilt per frame it would cost four board builds and two rotozoom
# calls every tick for a picture that never changes, which is exactly the kind
# of waste the browser build cannot absorb.

_T_HI    = (188, 138,  78)
_T_LIT   = (150,  99,  53)
_T_MID   = (112,  70,  38)
_T_DARK  = ( 68,  40,  22)
# Softer than a true shadow tone: at the 1-2px widths these are stroked at, a
# near-black edge made every board look ink-outlined.
_T_EDGE  = ( 60,  36,  20)
_IRON    = ( 62,  56,  60)
_IRON_HI = (132, 128, 134)
_ROPE    = (198, 166, 106)
_ROPE_D  = (128,  96,  52)

# Shadows are tinted off the day sky rather than neutral black, so one reads as
# "less light reached here" instead of a grey shape laid over the artwork.
_SH_TINT = (14, 38, 52)
# (contact_a, ambient_a, dy, spread) per elevation tier, following Material's
# opacity budget — umbra .20, ambient .12. Every element used to invent its own
# shadow at .43-.47, which is why they all read as pasted on.
_SH_TIERS = {
    "contact": (44, 24, 1, 3),
    "low":     (40, 22, 2, 4),   # the hanging sign planks
    "raised":  (50, 28, 2, 5),   # START, the one primary control
}

# Geometry, all measured against fixed art: Pip is blitted centred on
# (BIRD_X, H*0.42) and a fresh Bird respawns there the instant START is hit, so
# he is the one anchor the menu cannot move.
_MENU_CLOUD_ANCHOR_Y = 316        # just inside the cloud's lower mass
_MENU_CLOUD_HOOKS = (42, 174)     # the cloud's outer lobes
# The PROFILE frame: a true square whose bottom clears the STORE plank's
# rotated bbox (y359) by 12px, and whose tag sits flush in the inner rule's
# bottom-left corner. Both are locked values — the square was chosen against a
# grid of sizes and lifts, and every clearance in it (Pip's silhouette, the
# rope columns, the roofline, the subtitle) was measured, not estimated.
_MENU_FRAME = pygame.Rect(19, 204, 144, 144)
_MENU_TAG = pygame.Rect(25, 320, 84, 22)
_MENU_START = pygame.Rect(208, 494, 136, 100)
# Fixed grain seeds. These were hash(label) % 997, which Python salts per
# process — the same code drew a measurably different sign every launch.
# Centres already carry the 10px left shift that clears the START post.
_MENU_PLANKS = (("STORE", "coin", (102, 386), -3.0, 344),
                ("TOP 10", "trophy", (108, 446), 2.4, 429),
                ("SETTINGS", "gear", (100, 506), -1.6, 510))


def _soft_shadow(surf, shape, tier, mask=None):
    """Material-style stacked pair: a tight contact shadow plus a wider ambient
    one that actually falls off, instead of a single hard-edged slab. `mask`
    supplies a silhouette for rotated boards; without it the shape is treated
    as a rounded rect."""
    contact_a, ambient_a, dy, spread = _SH_TIERS[tier]
    pad = spread + 2
    layer = pygame.Surface((shape.width + pad * 2, shape.height + pad * 2),
                           pygame.SRCALPHA)
    if mask is not None:
        for k in range(spread, 0, -1):
            a = int(ambient_a * (k / spread) * 0.5)
            tinted = mask.copy()
            tinted.fill((*_SH_TINT, a), special_flags=pygame.BLEND_RGBA_MULT)
            for ox, oy in ((-k, 0), (k, 0), (0, -k), (0, k)):
                layer.blit(tinted, (pad + ox, pad + oy + dy))
        tinted = mask.copy()
        tinted.fill((*_SH_TINT, contact_a), special_flags=pygame.BLEND_RGBA_MULT)
        layer.blit(tinted, (pad, pad + dy))
    else:
        for k in range(spread, 0, -1):
            a = int(ambient_a * (1.0 - (k - 1) / max(1, spread)))
            pygame.draw.rect(layer, (*_SH_TINT, a),
                             pygame.Rect(pad - k, pad - k + dy,
                                         shape.width + k * 2,
                                         shape.height + k * 2),
                             border_radius=8 + k)
        pygame.draw.rect(layer, (*_SH_TINT, contact_a),
                         pygame.Rect(pad, pad + dy, shape.width, shape.height),
                         border_radius=8)
    surf.blit(layer, (shape.x - pad, shape.y - pad))


def _under_shade(surf, rect, height=4, alpha=46):
    """The object's own underside catching less light. This is what sells 3D
    form for something floating against open sky, where a projected cast
    shadow has nothing to fall on."""
    layer = pygame.Surface((rect.width, height), pygame.SRCALPHA)
    for y in range(height):
        a = int(alpha * (1.0 - y / max(1, height)))
        pygame.draw.line(layer, (*_SH_TINT, a), (0, y), (rect.width, y))
    surf.blit(layer, (rect.x, rect.bottom - height))


def _grad_fill(surf, rect, top, bot):
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        pygame.draw.line(surf, (int(top[0] + (bot[0] - top[0]) * t),
                                int(top[1] + (bot[1] - top[1]) * t),
                                int(top[2] + (bot[2] - top[2]) * t)),
                         (x, y + i), (x + w - 1, y + i))


def _board_points(w, h, chamfer=5, notch=5):
    """Chamfered corners plus a shallow V bitten out of each end face — the
    hand-cut sign silhouette, not a plain rectangle."""
    return [(chamfer, 0), (w - chamfer, 0), (w, chamfer),
            (w - notch, h * 0.5), (w, h - chamfer), (w - chamfer, h),
            (chamfer, h), (0, h - chamfer), (notch, h * 0.5), (0, chamfer)]


def _timber_board(w, h, seed=0, chamfer=5, notch=5, plain=False):
    """One planed board: lit-from-above gradient, drifting grain, a knot or
    two, chamfer highlights and a shadow lip along the bottom."""
    rnd = random.Random(seed)
    w, h = int(w), int(h)
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    _grad_fill(body, (0, 0, w, h), _T_LIT, _T_DARK)

    for _ in range(max(3, h // 5)):
        gy = rnd.uniform(h * 0.12, h * 0.9)
        col = _T_MID if rnd.random() < 0.6 else _T_EDGE
        pts = [(gx, gy + math.sin(gx * 0.05 + seed) * 1.4 + rnd.uniform(-0.5, 0.5))
               for gx in range(0, w + 6, 6)]
        if len(pts) > 1:
            pygame.draw.lines(body, col, False, pts, 1)

    for _ in range(1 if w < 90 else 2):
        kx = rnd.uniform(w * 0.15, w * 0.85)
        ky = rnd.uniform(h * 0.3, h * 0.7)
        kr = rnd.uniform(2.0, 3.2)
        pygame.draw.ellipse(body, _T_EDGE,
                            (kx - kr, ky - kr * 0.72, kr * 2, kr * 1.45))
        pygame.draw.ellipse(body, _T_MID,
                            (kx - kr * 1.9, ky - kr * 1.3, kr * 3.8, kr * 2.6), 1)

    pygame.draw.line(body, _T_HI, (chamfer, 1), (w - chamfer, 1), 2)
    pygame.draw.line(body, (200, 156, 96), (chamfer + 2, 0), (w - chamfer - 2, 0), 1)
    pygame.draw.line(body, _T_EDGE, (chamfer, h - 1), (w - chamfer, h - 1), 1)

    if plain:
        pygame.draw.rect(body, _T_EDGE, (0, 0, w, h), 1)
        return body

    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pts = _board_points(w, h, chamfer, notch)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.polygon(body, _T_EDGE, pts, 1)
    return body


def _iron_nail(surf, x, y, r=3):
    pygame.draw.circle(surf, _T_EDGE, (int(x), int(y + 1)), max(1, r - 1))
    pygame.draw.circle(surf, _IRON, (int(x), int(y)), r)
    pygame.draw.circle(surf, _IRON_HI, (int(x - r * 0.3), int(y - r * 0.35)),
                       max(1, r - 2))


def _hemp_rope(surf, p0, p1, sag=6, width=3):
    """A sagging catenary in two tones, so the twist reads at this size."""
    x0, y0 = p0
    x1, y1 = p1
    pts = [(x0 + (x1 - x0) * (i / 12),
            y0 + (y1 - y0) * (i / 12) + math.sin(math.pi * i / 12) * sag)
           for i in range(13)]
    pygame.draw.lines(surf, _ROPE_D, False, pts, width + 1)
    pygame.draw.lines(surf, _ROPE, False, pts, max(1, width - 1))


_MENU_CLOUD_RECT: "pygame.Rect | None" = None


def _menu_cloud_rect():
    """Screen bbox of the cloud lobes inside the blitted cottage sprite.

    Derived from the sprite's own alpha rather than hardcoded, so the rope
    anchors can never end up hanging in open sky beside the cloud if the art
    changes. Cached — it walks a mask."""
    global _MENU_CLOUD_RECT
    if _MENU_CLOUD_RECT is None:
        from game import intro as _intro
        house = _intro.get_sprite("skyhouse_post")
        hx = int(W * 0.30) - house.get_width() // 2
        hy = int(H * 0.42) - house.get_height() // 2
        # The cloud occupies sprite rows 88 and below; above that is cottage.
        sub = house.subsurface(pygame.Rect(0, 88, house.get_width(),
                                           house.get_height() - 88))
        bb = pygame.mask.from_surface(sub, threshold=8).get_bounding_rects()
        r = bb[0]
        for extra in bb[1:]:
            r = r.union(extra)
        _MENU_CLOUD_RECT = pygame.Rect(hx + r.x, hy + 88 + r.y, r.width, r.height)
    return _MENU_CLOUD_RECT


def _menu_sign_chain(surf):
    """The three utility signs, hung from the cloud Pip is standing on.

    They used to be slung off a separately mounted START signboard, which put
    the primary control ABOVE all three utilities. Hanging them from the cloud
    fixes both things: the ropes leave the object Pip actually stands on, and
    START drops out of the chain entirely to sit lowest and nearest the thumb.
    """
    cloud = _menu_cloud_rect()
    # 44, not 40: at a shallow hang angle a 40px board published a 46px tap
    # rect once rotated, under the 48dp floor. 44 clears it at every angle.
    bw, bh = 172, 44
    chamfer, notch = 6, 7
    label_cx = (44 + (bw - notch)) // 2
    anchors = [(min(max(x, cloud.left + 14), cloud.right - 14),
                _MENU_CLOUD_ANCHOR_Y) for x in _MENU_CLOUD_HOOKS]

    rects = {}
    for label, kind, (cx, cy), ang, seed in _MENU_PLANKS:
        rad = math.radians(-ang)
        for sgn, apt in zip((-1, 1), anchors):
            ox = sgn * (bw * 0.36)
            hx = cx + ox * math.cos(rad)
            hy = cy + ox * math.sin(rad) - bh * 0.5
            _hemp_rope(surf, apt, (hx, hy), sag=5, width=3)
            pygame.draw.circle(surf, _IRON, (int(hx), int(hy)), 3)

        board = _timber_board(bw, bh, seed=seed, chamfer=chamfer, notch=notch)
        if kind == "coin":
            _coin_icon(board, 30, bh // 2, 12)
        elif kind == "trophy":
            _draw_trophy(board, 30, bh // 2, 10)
        else:
            _draw_gear(board, 30, bh // 2, 12)
        _tracked_label(board, label, (label_cx, bh // 2 + 1), 17,
                       color=(46, 26, 14), track=2, alpha=120)
        _tracked_label(board, label, (label_cx, bh // 2 - 1), 17,
                       color=_GOLD_PALE, track=2, alpha=250)

        rot = pygame.transform.rotozoom(board, ang, 1.0)
        rr = rot.get_rect(center=(cx, cy))
        _soft_shadow(surf, rr, "low", mask=rot)
        surf.blit(rot, rr.topleft)
        rects[label] = rr

        anchors = [(cx - bw * 0.34 * math.cos(rad),
                    cy - bw * 0.34 * math.sin(rad) + bh * 0.42),
                   (cx + bw * 0.34 * math.cos(rad),
                    cy + bw * 0.34 * math.sin(rad) + bh * 0.42)]
    return rects


def _menu_start_post(surf):
    """START, planted on its own post in the dead bottom-right quadrant.

    It leaves the sign chain because the body's ink centroid sat at x113 while
    the title spine is x180 — two vertical axes that disagreed under four
    near-identical horizontal bands. Standing it apart also terminates the
    chain instead of adding a fifth parallel edge to it."""
    rect = pygame.Rect(_MENU_START)
    surf.blit(_timber_board(24, 120, seed=7, plain=True), (264, 494))
    brace = pygame.transform.rotozoom(_timber_board(74, 12, seed=11, plain=True),
                                      38, 1.0)
    surf.blit(brace, brace.get_rect(center=(236, 566)).topleft)
    _soft_shadow(surf, pygame.Rect(264, 588, 24, 22), "contact")
    _soft_shadow(surf, rect, "raised")

    board = _timber_board(rect.width, rect.height, seed=21, chamfer=9, notch=0)
    face = pygame.Rect(0, 0, 110, 46)
    face.center = (rect.width // 2, rect.height // 2)
    _grad_fill(board, (face.x, face.y, face.width, face.height),
               _SCARLET_TOP, _SCARLET_BOT)
    frost = pygame.Surface((face.width, face.height // 2), pygame.SRCALPHA)
    frost.fill((255, 255, 255, 34))
    board.blit(frost, face.topleft)
    pygame.draw.rect(board, _GOLD_BRIGHT, face, 2)
    pygame.draw.rect(board, _T_EDGE, face.inflate(3, 3), 1)
    pygame.draw.line(board, (*_GOLD_PALE, 150), (face.left + 8, face.top + 5),
                     (face.right - 8, face.top + 5), 1)
    f = _font(28, True)
    img = f.render("START", True, (255, 244, 222))
    ir = img.get_rect(center=(face.centerx, face.centery - 1))
    out = f.render("START", True, (108, 20, 14))
    out.set_alpha(190)
    for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        board.blit(out, (ir.x + ox, ir.y + oy))
    board.blit(img, ir.topleft)

    # Gold double-chevron under the word: the extra board height carries the
    # emphasis a narrower slab gives up.
    for oy in (14, 21):
        cy2 = face.bottom + oy - 6
        pygame.draw.lines(board, _GOLD_PALE, False,
                          [(rect.width // 2 - 11, cy2 - 4),
                           (rect.width // 2, cy2),
                           (rect.width // 2 + 11, cy2 - 4)], 2)
    surf.blit(board, rect.topleft)
    _under_shade(surf, rect, height=6, alpha=42)
    return rect


def _menu_profile_frame(surf):
    """The square jewel frame around the standing-Pip diorama, plus its brass
    PROFILE tag.

    Two rules, not one: the outer at radius 13 and the inner 5px in at radius
    8, with a pale sheen along the top so the gold reads as struck metal
    rather than a drawn outline. The tag is seated flush into the inner rule's
    bottom-left corner — against its left run and on its bottom run — so it
    belongs to the frame instead of floating inside it."""
    fr, tag = pygame.Rect(_MENU_FRAME), pygame.Rect(_MENU_TAG)
    pygame.draw.rect(surf, _GOLD_MID, fr, width=1, border_radius=13)
    pygame.draw.rect(surf, _GOLD_BRIGHT, fr.inflate(-10, -10), width=1,
                     border_radius=8)
    pygame.draw.line(surf, (*_GOLD_PALE, 200), (fr.left + 14, fr.top + 2),
                     (fr.right - 14, fr.top + 2), 1)

    pygame.draw.rect(surf, _GOLD_DEEP, tag, border_radius=8)
    pygame.draw.rect(surf, _GOLD_MID, tag.inflate(-3, -3), border_radius=7)
    pygame.draw.line(surf, _GOLD_PALE, (tag.left + 8, tag.top + 3),
                     (tag.right - 8, tag.top + 3), 1)
    pygame.draw.line(surf, (86, 60, 16), (tag.left + 8, tag.bottom - 3),
                     (tag.right - 8, tag.bottom - 3), 1)
    inset = tag.inflate(-7, -7)
    pygame.draw.rect(surf, (52, 34, 14), inset, border_radius=5)
    # 12/1, not the 13/2 the larger plates use: PROFILE at 13/2 plus the
    # chevron measures 84px against this tag's 77px recess.
    lx = inset.centerx - 6
    _tracked_label(surf, "PROFILE", (lx, inset.centery + 1), 12,
                   color=(34, 20, 8), track=1, alpha=150)
    _tracked_label(surf, "PROFILE", (lx, inset.centery), 12,
                   color=_GOLD_PALE, track=1, alpha=250)
    _profile_tri(surf, inset.right - 9, inset.centery, 4, _GOLD_PALE)
    return fr


_MENU_STAR_FIELD: "list | None" = None


def _menu_star_field(stars):
    """The overlay star field with the sparkles that fall on the island removed,
    so they read as being BEHIND the cottage and Pip instead of twinkling on his
    chest.

    They cannot just be drawn earlier to get behind him. The night veil has to
    keep landing ON the diorama to hold it dim, and the veil goes down before
    the stars — draw the stars first and the veil dims them too. Dropping the
    occluded ones puts them behind without touching that order.

    The cottage never moves and Pip's idle hover stays inside a measured
    envelope, so the surviving set is constant and is worked out once. Only the
    menu uses it; every other overlay screen draws the full field, having no
    diorama to sit behind.
    """
    global _MENU_STAR_FIELD
    if _MENU_STAR_FIELD is None:
        from game import intro as _intro
        house = _intro.get_sprite("skyhouse_post")
        hw, hh = house.get_size()
        hx = int(W * 0.30) - hw // 2
        hy = int(H * 0.42) - hh // 2
        mask = pygame.mask.from_surface(house, 8)
        # Pip's full idle-bob envelope, measured across 15s of world_idle_tick:
        # he floats +-12px, so a star cleared at one phase of the hover would
        # wink back on as he rises.
        pip = pygame.Rect(58, 230, 65, 74)

        def hidden(x, y):
            if pip.collidepoint(x, y):
                return True
            lx, ly = x - hx, y - hy
            return 0 <= lx < hw and 0 <= ly < hh and mask.get_at((lx, ly))

        _MENU_STAR_FIELD = [st for st in stars if not hidden(st[0], st[1])]
    return _MENU_STAR_FIELD


_MENU_FURNITURE: "pygame.Surface | None" = None
_MENU_FURNITURE_RECTS: "dict | None" = None


def _menu_furniture():
    """The whole static menu set, baked once. Returns (layer, tap rects)."""
    global _MENU_FURNITURE, _MENU_FURNITURE_RECTS
    if _MENU_FURNITURE is None:
        layer = pygame.Surface((W, H), pygame.SRCALPHA)
        rects = _menu_sign_chain(layer)
        rects["START"] = _menu_start_post(layer)
        rects["PROFILE"] = _menu_profile_frame(layer)
        _MENU_FURNITURE, _MENU_FURNITURE_RECTS = layer, rects
    return _MENU_FURNITURE, _MENU_FURNITURE_RECTS



# ── Neon-Arcade HUD kit (E2 layout, menu-yellow accent) ──────────────────────
# Shipped from the gameplay-HUD design loop. The score/coins/pause sit on opaque
# softened cut-corner slate plates: an OPAQUE body is the hard value floor that
# keeps the readout legible over a bright-sky brown pillar AND at night — the
# legibility the old translucent pills never had. The accent is the menu's
# SKYBIT yellow (`_GOLD_BRIGHT`) so the HUD reads as one family with the title.
# The power-up timer is a recessed-track energy bar that drains yellow→amber;
# kept a horizontal meter in a dark cool track on purpose so it can never be
# misread as the round gold coin.
_SS = 4  # supersample factor — composite big, smoothscale down for crisp edges
_NA_PAD = 11  # padding baked around each cached plate so its soft glow can bleed

_NA_SLATE    = ( 40,  38,  36)   # warm slate plate body (opaque value floor)
_NA_SLATE_D  = ( 22,  18,  16)
_NA_ACCENT   = _GOLD_BRIGHT       # menu-text yellow: rim + glow + glyphs
_NA_WARM     = ( 96,  64,  36)   # faint sandstone wash low in the score plate
_ENERGY_FULL   = _GOLD_BRIGHT     # timer fill at full charge (yellow)
_ENERGY_FULL_D = (170, 120,  28)
_ENERGY_LOW    = (255, 168,  70)  # draining toward amber
_ENERGY_LOW_D  = (196,  96,  28)
# Timer-bar fill stops — the meter reads its remaining time by colour:
# green when full, yellow at the midpoint, red when nearly out. Each stop is
# a bright core + darker edge for the recessed-track vertical gradient.
_BAR_GREEN   = (  0, 235,  60);  _BAR_GREEN_D  = (  0, 150,  30)
_BAR_YELLOW  = (255, 220,   0);  _BAR_YELLOW_D = (220, 160,   0)
_BAR_RED     = (255,  30,  30);  _BAR_RED_D    = (180,  10,  10)

_na_plate_cache: dict = {}
_na_track_cache: dict = {}


def _ss_surf(w, h):
    return pygame.Surface((w * _SS, h * _SS), pygame.SRCALPHA)


def _blit_ss(dst, ss, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(ss, (w, h)), (x, y))


def _vgrad_rounded_ss(surf, w, h, top, bot, radius, alpha=255):
    """Vertical gradient clipped to a rounded rect, drawn onto a SUPERSAMPLED
    `surf` whose pixel size is `_SS` × the given native `w`/`h`."""
    ow, oh, orad = w * _SS, h * _SS, radius * _SS
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(top, bot, t)
        pygame.draw.line(body, (*c, alpha), (0, yy), (ow - 1, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (0, 0))


def _cut_pts(x, y, w, h, cut):
    """Cut-corner (octagon) outline. The corner faces are softened into a
    chamfer-with-fillet by intersecting with a rounded-rect mask in the plate
    builder, so the silhouette reads friendly-arcade rather than hard bezel."""
    return [
        (x + cut, y), (x + w - cut, y), (x + w, y + cut),
        (x + w, y + h - cut), (x + w - cut, y + h), (x + cut, y + h),
        (x, y + h - cut), (x, y + cut),
    ]


def _na_plate_build(w, h, cut, round_r, accent, top, bot, inner_warm, glow):
    pad = _NA_PAD
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    if glow:
        gpts = _cut_pts(pad, pad, w, h, cut)
        for i in range(5, 0, -1):
            a = int(34 * i / 5 / 5)
            pygame.draw.polygon(out, (*accent, a), gpts, width=i)
    ow, oh = w * _SS, h * _SS
    sspts = [(round(px * _SS), round(py * _SS))
             for px, py in _cut_pts(0, 0, w, h, cut)]
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(top, bot, t)
        if inner_warm is not None and t > 0.55:
            c = lerp_color(c, inner_warm, (t - 0.55) / 0.45 * 0.5)
        pygame.draw.line(body, (*c, 255), (0, yy), (ow, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), sspts)
    if round_r > 0:
        rr = pygame.Surface((ow, oh), pygame.SRCALPHA)
        pygame.draw.rect(rr, (255, 255, 255, 255), (0, 0, ow, oh),
                         border_radius=round_r * _SS)
        mask.blit(rr, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss = pygame.Surface((ow, oh), pygame.SRCALPHA)
    ss.blit(body, (0, 0))
    pygame.draw.polygon(ss, (*accent, 255), sspts, width=2 * _SS)
    hi = lerp_color(accent, UI_CREAM, 0.4)
    pygame.draw.line(ss, (*hi, 110), sspts[0], sspts[1], _SS)
    out.blit(pygame.transform.smoothscale(ss, (w, h)), (pad, pad))
    return out


def _na_plate(surf, rect, cut, round_r, accent=_NA_ACCENT,
              top=_NA_SLATE, bot=_NA_SLATE_D, inner_warm=None, glow=True):
    """Blit a (cached) cut-corner slate plate so its body fills `rect`; the
    baked soft glow bleeds into the `_NA_PAD` margin around it."""
    key = (rect.width, rect.height, cut, round_r, accent, top, bot,
           inner_warm, glow)
    out = _na_plate_cache.get(key)
    if out is None:
        out = _na_plate_build(rect.width, rect.height, cut, round_r, accent,
                              top, bot, inner_warm, glow)
        _na_plate_cache[key] = out
    surf.blit(out, (rect.x - _NA_PAD, rect.y - _NA_PAD))


def _na_track_bg(w, h, radius):
    key = (w, h, radius)
    out = _na_track_cache.get(key)
    if out is None:
        ss = _ss_surf(w, h)
        _vgrad_rounded_ss(ss, w, h, (20, 30, 38), (8, 14, 20), radius, alpha=245)
        pygame.draw.rect(ss, (*_NA_ACCENT, 150), (0, 0, w * _SS, h * _SS),
                         width=_SS, border_radius=radius * _SS)
        out = pygame.transform.smoothscale(ss, (w, h))
        _na_track_cache[key] = out
    return out


def _na_energy_bar(surf, rect, frac):
    """Recessed-track energy bar; fill drains green→yellow→red as time runs
    out. A horizontal meter in a dark cool track on purpose, so it never reads
    as a gold coin."""
    radius = rect.height // 2
    surf.blit(_na_track_bg(rect.width, rect.height, radius), (rect.x, rect.y))
    # Two-segment traffic-light map: green at full, through yellow at the
    # midpoint, to red as the meter empties.
    if frac >= 0.5:
        t = (frac - 0.5) / 0.5
        core = lerp_color(_BAR_YELLOW, _BAR_GREEN, t)
        edge = lerp_color(_BAR_YELLOW_D, _BAR_GREEN_D, t)
    else:
        t = frac / 0.5
        core = lerp_color(_BAR_RED, _BAR_YELLOW, t)
        edge = lerp_color(_BAR_RED_D, _BAR_YELLOW_D, t)
    inset = 4
    fillw = int((rect.width - inset * 2) * frac)
    fh = rect.height - inset * 2
    if fillw > 4:
        fill = _ss_surf(fillw, fh)
        _vgrad_rounded_ss(fill, fillw, fh, core, edge, max(1, fh // 2))
        pygame.draw.line(fill, (255, 255, 255, 170), (2 * _SS, 3 * _SS),
                         (fillw * _SS - 2 * _SS, 3 * _SS), _SS)
        _blit_ss(surf, fill, rect.x + inset, rect.y + inset, fillw, fh)


# ── Active-buff emblem family ────────────────────────────────────────────────
# Every active power-up shows a small emblem on the slate plate left of its
# timer bar. The whole set shares one visual language so the buff stack reads as
# a cohesive family: each emblem is supersampled then smoothscaled (crisp arcs
# + real gradient shading at the 32px HUD footprint), lit from one top-left key
# light, carries a uniform dark outline weight, and sits on one soft contact
# shadow. To stay faithful to what the player actually grabs, most kinds blit
# the REAL in-world pickup sprite (via powerup_help._powerup_icon, the same
# renderer the run-summary chips use). The two pickups that turn to mush at HUD
# size — the photographic KFC logo and the text-captioned rail ticket — get a
# purpose-built simplified emblem here, drawn in their in-world palette.

_EMB_OUTLINE = (28, 24, 38)
_EMB_OW = max(2, 3 * _SS // 2)  # ~1.5px at the 32px footprint


def _emb_lerp(a, b, t):
    return a + (b - a) * t


def _emb_mix(c1, c2, t):
    return (int(_emb_lerp(c1[0], c2[0], t)),
            int(_emb_lerp(c1[1], c2[1], t)),
            int(_emb_lerp(c1[2], c2[2], t)))


def _emb_shade(c, f):
    # f<1 darkens, f>1 lightens; clamps to byte range.
    return (max(0, min(255, int(c[0] * f))),
            max(0, min(255, int(c[1] * f))),
            max(0, min(255, int(c[2] * f))))


def _emb_raw(size):
    return pygame.Surface((size * _SS, size * _SS), pygame.SRCALPHA)


def _emb_vgrad_circle(surf, cx, cy, r, top, bottom):
    # Vertical gradient clipped to a circle — a top-lit sphere/disc at SS scale.
    if r <= 0:
        return
    grad = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for y in range(r * 2):
        t = y / max(1, (r * 2 - 1))
        pygame.draw.line(grad, _emb_mix(top, bottom, t), (0, y), (r * 2, y))
    mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (cx - r, cy - r))


def _emb_vgrad_mask(surf, mask_pts, y0, y1, top, bottom):
    """Vertical gradient clipped to an arbitrary polygon mask."""
    W_, H_ = surf.get_size()
    band = pygame.Surface((W_, H_), pygame.SRCALPHA)
    for y in range(max(0, y0), min(H_, y1)):
        t = (y - y0) / max(1, (y1 - y0))
        pygame.draw.line(band, _emb_mix(top, bottom, t), (0, y), (W_, y))
    mask = pygame.Surface((W_, H_), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), mask_pts)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(band, (0, 0))


def _emb_key_light(surf, cx, cy, r, strength=64):
    # One shared top-left specular bloom => one light direction across the set.
    if r <= 0:
        return
    hl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, strength),
                       (int(r * 0.7), int(r * 0.62)), int(r * 0.55))
    hl = pygame.transform.smoothscale(hl, (r * 2, r * 2))
    mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (cx - r, cy - r))


def _emb_contact_shadow(out, size):
    # Soft ellipse under the emblem grounds it on the plate — same for all ten.
    sh = pygame.Surface((size, size), pygame.SRCALPHA)
    w = int(size * 0.60)
    h = max(2, int(size * 0.15))
    cx = size // 2
    cy = int(size * 0.87)
    pygame.draw.ellipse(sh, (0, 0, 0, 55), (cx - w // 2, cy - h // 2, w, h))
    out.blit(sh, (0, 0))


def _emb_finish(size, ss):
    """Downsample the SS emblem onto a size×size surface over one contact
    shadow (drawn first so the emblem sits on top)."""
    out = pygame.Surface((size, size), pygame.SRCALPHA)
    _emb_contact_shadow(out, size)
    out.blit(pygame.transform.smoothscale(ss, (size, size)), (0, 0))
    return out


# Palette for the two purpose-built stand-in emblems (kfc + rail). The other
# eight kinds blit the real in-world sprite, so they need no palette here.
_EMB_PAL = {
    "kfc_red": (210, 38, 40), "kfc_red_d": (150, 22, 26),
    "kfc_white": (248, 244, 238), "drum_brown": (190, 122, 60),
    "drum_brown_d": (138, 80, 36), "bone": (245, 238, 224),
    # rail ticket palette, lifted from the in-world rail pickup (entities.py
    # _draw_rail_icon) so the emblem reads as the same sepia locomotive card.
    "rail_sepia": (228, 210, 170), "rail_sepia_d": (196, 176, 134),
    "rail_ink": (30, 25, 20), "rail_cream": (238, 225, 195),
    "rail_frame": (18, 14, 10),
}


def _emb_build_kfc(size):
    ss = _emb_raw(size)
    S = size * _SS
    cx = S // 2
    top_y = int(S * 0.42)
    bot_y = int(S * 0.82)
    half_top = int(S * 0.31)   # FLARED wide at the top (chicken bucket, not box)
    half_bot = int(S * 0.19)
    body = [(cx - half_top, top_y), (cx + half_top, top_y),
            (cx + half_bot, bot_y), (cx - half_bot, bot_y)]
    pygame.draw.polygon(ss, _EMB_PAL["kfc_white"], body)
    for i in range(3):
        t = (i + 0.5) / 3
        xt = _emb_lerp(cx - half_top, cx + half_top, t)
        xb = _emb_lerp(cx - half_bot, cx + half_bot, t)
        pygame.draw.line(ss, _EMB_PAL["kfc_red"], (xt, top_y), (xb, bot_y), int(S * 0.055))
    pygame.draw.polygon(ss, _EMB_OUTLINE, body, _EMB_OW)
    rim_top = top_y - int(S * 0.06)
    rrect = (cx - half_top, rim_top, half_top * 2, int(S * 0.12))
    pygame.draw.ellipse(ss, _EMB_PAL["kfc_red"], rrect)
    pygame.draw.ellipse(ss, _EMB_OUTLINE, rrect, _EMB_OW)
    # ONE drumstick OVERLAPPING the rim => "chicken IN bucket", not a stray dot.
    dx = cx + int(S * 0.05)
    lobe_r = int(S * 0.13)
    dy = rim_top - lobe_r + int(S * 0.05)
    _emb_vgrad_circle(ss, dx, dy, lobe_r, _emb_shade(_EMB_PAL["drum_brown"], 1.25),
                      _EMB_PAL["drum_brown_d"])
    pygame.draw.circle(ss, _EMB_OUTLINE, (dx, dy), lobe_r, _EMB_OW)
    pygame.draw.ellipse(ss, _EMB_OUTLINE, rrect, _EMB_OW)  # rim crosses behind lobe
    bx, by = dx + int(S * 0.05), dy - int(S * 0.11)
    pygame.draw.line(ss, _EMB_PAL["bone"], (dx, dy - int(lobe_r * 0.4)), (bx, by),
                     int(S * 0.05))
    pygame.draw.circle(ss, _EMB_PAL["bone"], (bx, by), max(2, int(S * 0.04)))
    pygame.draw.circle(ss, _EMB_OUTLINE, (bx, by), max(2, int(S * 0.04)),
                       max(2, _EMB_OW - 2))
    _emb_key_light(ss, dx, dy, lobe_r, 55)
    return _emb_finish(size, ss)


def _emb_build_rail(size):
    # Simplified sepia locomotive ticket — evokes the in-world rail pickup
    # (entities.py _draw_rail_icon: a sepia card stamped with a side-view steam
    # engine) without its "TRAIN" caption, which is illegible at HUD size.
    ss = _emb_raw(size)
    S = size * _SS
    # Sepia ticket card with a dark frame + engraved inner border.
    card = pygame.Rect(int(S * 0.10), int(S * 0.20), int(S * 0.80), int(S * 0.60))
    pygame.draw.rect(ss, _EMB_PAL["rail_frame"], card, border_radius=int(S * 0.06))
    inner = card.inflate(-int(S * 0.06), -int(S * 0.06))
    _emb_vgrad_mask(
        ss,
        [inner.topleft, inner.topright, inner.bottomright, inner.bottomleft],
        inner.top, inner.bottom,
        _emb_shade(_EMB_PAL["rail_sepia"], 1.05), _EMB_PAL["rail_sepia_d"])
    pygame.draw.rect(ss, _EMB_PAL["rail_cream"], inner.inflate(-int(S * 0.04),
                     -int(S * 0.04)), max(2, _EMB_OW - 1), border_radius=int(S * 0.04))
    # Side-view steam locomotive, ink-dark on the card. Drawn facing LEFT on its
    # own layer, then mirrored so it faces RIGHT before stamping on the card.
    loco = pygame.Surface((S, S), pygame.SRCALPHA)
    ink = _EMB_PAL["rail_ink"]
    base_y = int(S * 0.62)
    boiler = pygame.Rect(int(S * 0.26), int(S * 0.40), int(S * 0.42), int(S * 0.18))
    pygame.draw.rect(loco, ink, boiler, border_radius=int(S * 0.04))
    cab = pygame.Rect(int(S * 0.55), int(S * 0.32), int(S * 0.16), int(S * 0.20))
    pygame.draw.rect(loco, ink, cab, border_radius=int(S * 0.02))
    # Smokestack ahead of the boiler.
    pygame.draw.rect(loco, ink, (int(S * 0.30), int(S * 0.30),
                                 int(S * 0.07), int(S * 0.12)))
    pygame.draw.rect(loco, ink, (int(S * 0.28), int(S * 0.28),
                                 int(S * 0.11), int(S * 0.04)))
    # Cow-catcher wedge at the front.
    pygame.draw.polygon(loco, ink, [(int(S * 0.26), int(S * 0.50)),
                                    (int(S * 0.26), int(S * 0.58)),
                                    (int(S * 0.18), int(S * 0.58))])
    # Two spoked wheels on a connecting rod.
    wy = base_y
    for wx in (int(S * 0.34), int(S * 0.56)):
        pygame.draw.circle(loco, ink, (wx, wy), int(S * 0.09))
        pygame.draw.circle(loco, _EMB_PAL["rail_cream"], (wx, wy), int(S * 0.09),
                           max(2, _EMB_OW - 1))
        for ang in range(0, 360, 60):
            a = math.radians(ang)
            pygame.draw.line(loco, _EMB_PAL["rail_cream"], (wx, wy),
                             (wx + math.cos(a) * int(S * 0.07),
                              wy + math.sin(a) * int(S * 0.07)), max(1, _EMB_OW - 2))
        pygame.draw.circle(loco, ink, (wx, wy), max(2, int(S * 0.025)))
    pygame.draw.line(loco, ink, (int(S * 0.34), wy), (int(S * 0.56), wy),
                     max(2, _EMB_OW - 1))
    ss.blit(pygame.transform.flip(loco, True, False), (0, 0))
    return _emb_finish(size, ss)


# kfc + rail get the purpose-built simplified emblems above; every other kind
# is rendered from its REAL in-world pickup sprite (see _get_buff_emblem).
_EMB_BUILDERS = {
    "kfc": _emb_build_kfc,
    "rail": _emb_build_rail,
}

# Kinds whose in-world pickup downscales cleanly are blitted verbatim from the
# real sprite so the HUD emblem always matches what the player grabbed.
_EMB_FROM_PICKUP = frozenset({
    "triple", "magnet", "megamagnet", "slowmo", "reverse", "ghost",
    "grow", "shrink",
    # Secret late-game kinds — rendered from their in-world PowerUp sprites
    # so the HUD emblem matches the pickup the player grabbed.
    "skateboard", "knight", "poison", "genie", "umbrella",
})

# Emblems are static, so render each (kind, size) once and reuse the surface;
# both the supersampled custom draws and the PowerUp.draw() pickup render are
# far too heavy to run per frame.
_buff_emblem_cache: dict = {}
# Lazily bound to powerup_help._powerup_icon — that module imports from hud, so
# we defer the import to first use to dodge the import cycle (same pattern as
# draw_stats' run-summary chips).
_emb_powerup_icon = None


def _emb_from_pickup(kind, size):
    """Render the real in-world pickup sprite, scaled to fill the HUD plate."""
    global _emb_powerup_icon
    if _emb_powerup_icon is None:
        from game.powerup_help import _powerup_icon
        _emb_powerup_icon = _powerup_icon
    emb = pygame.Surface((size, size), pygame.SRCALPHA)
    # The pickups carry their own padding, so draw a touch larger than the plate
    # to match the visual weight of the run-summary chips (icon_size * 1.5).
    _emb_powerup_icon(emb, kind, size // 2, size // 2, int(size * 1.4))
    return emb


def _get_buff_emblem(kind, size):
    key = (kind, size)
    emb = _buff_emblem_cache.get(key)
    if emb is None:
        if kind in _EMB_FROM_PICKUP:
            emb = _emb_from_pickup(kind, size)
        else:
            builder = _EMB_BUILDERS.get(kind)
            if builder is None:
                return None
            emb = builder(size)
        _buff_emblem_cache[key] = emb
    return emb


def _draw_buff_icon(surf, rect, kind):
    """Emblem for an active buff, centered in ``rect`` and cached per
    (kind, size). Most kinds blit the real in-world pickup sprite so the HUD
    matches what the player grabbed; kfc + rail use a legible stand-in drawn
    in their in-world palette (see the module comment above)."""
    size = min(rect.width, rect.height)
    if size <= 0:
        return
    emb = _get_buff_emblem(kind, size)
    if emb is not None:
        surf.blit(emb, emb.get_rect(center=rect.center))


class PauseButton:
    # Cut-corner power tile, top-right — sized and cornered to match the coins
    # plate's INITIAL footprint at the opposite corner (68x38: its 1-digit
    # baseline; same corner kit), vertically aligned, so the two top chips read
    # as a matched pair. Fixed footprint on purpose: the coins plate auto-grows
    # with its digit count, but the pause tile never does. Inset 18 px from the
    # right edge for safe-area margin against notched / rounded web corners; the
    # yellow accent + glow keep it from reading as the quietest tile.
    TILE = pygame.Rect(W - 68 - 18, 14, 68, 38)

    def __init__(self):
        # Hit-test area is the tile generously inflated (~54 px target, well over
        # the 44 px minimum, and survives rounded/notched web-portrait corners);
        # the visible tile is smaller.
        self.rect = PauseButton.TILE.inflate(16, 16)
        self.hover = False

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surf, paused=False):
        tile = PauseButton.TILE
        _na_plate(surf, tile, cut=7, round_r=8, glow=True)
        cx, cy = tile.center
        if paused:
            pygame.draw.polygon(surf, _NA_ACCENT, [
                (cx - 5, cy - 7),
                (cx - 5, cy + 7),
                (cx + 6, cy),
            ])
        else:
            bw, bh, gap = 5, 17, 4
            for dx in (-gap - bw, gap):
                pygame.draw.rect(surf, _NA_ACCENT,
                                 (cx + dx, cy - bh // 2, bw, bh), border_radius=2)
                pygame.draw.rect(surf, lerp_color(_NA_ACCENT, UI_CREAM, 0.5),
                                 (cx + dx + 1, cy - bh // 2 + 1, max(1, bw - 3), 4))


class HelpButton:
    """Top-left "?" button on the menu. Click opens the power-ups
    explainer (STATE_POWERUPS). Mirrors PauseButton's panel styling so
    the two top-corner buttons feel like a consistent family."""
    def __init__(self):
        self.rect = pygame.Rect(12, 12, 44, 44)

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surf):
        rounded_rect(surf, self.rect, 10, _PANEL_DARK, 200)
        border = pygame.Surface((self.rect.width, self.rect.height),
                                pygame.SRCALPHA)
        pygame.draw.rect(border, (*_ORANGE_BORDER, 120),
                         (0, 0, self.rect.width, self.rect.height),
                         border_radius=10, width=1)
        surf.blit(border, self.rect.topleft)
        cx, cy = self.rect.center
        # Bold gold "?" with a soft shadow.
        f = _font(28, True)
        sh = f.render("?", True, NEAR_BLACK)
        sh.set_alpha(150)
        surf.blit(sh, sh.get_rect(center=(cx + 1, cy + 2)))
        q = f.render("?", True, _GOLD_BRIGHT)
        surf.blit(q, q.get_rect(center=(cx, cy)))


# ── Run-summary helpers ──────────────────────────────────────────────────────

def _outline_pill_btn(surf, center, text, size=14, alpha=230,
                      min_width=120, pad_x=24, pad_y=12):
    """Secondary CTA — dark navy fill + gold border + gold text. Used
    for MAIN MENU under the primary PLAY AGAIN pill so the hierarchy
    reads cleanly. Returns the rect for hit-testing."""
    f = _font(size, True)
    img = f.render(text, True, _GOLD_BRIGHT)
    pw = max(min_width, img.get_width() + pad_x)
    ph = img.get_height() + pad_y
    cx, cy = center
    x = cx - pw // 2
    y = cy - ph // 2
    body = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(body, (*_PANEL_DARK, 200),
                     (0, 0, pw, ph), border_radius=ph // 2)
    pygame.draw.rect(body, _GOLD_BRIGHT, (0, 0, pw, ph),
                     width=2, border_radius=ph // 2)
    body.set_alpha(alpha)
    surf.blit(body, (x, y))
    surf.blit(img, img.get_rect(center=(cx, cy)))
    return pygame.Rect(x, y, pw, ph)


def _stat_tile_icon(surf, kind, cx, cy, size):
    """Stat-tile icon glyph. ``size`` is the half-extent in pixels.
    Supported kinds: ``time`` (clock face with hands), ``coin`` (real
    in-game coin face, capped at native display size), ``pillar``
    (small stone-column silhouette), ``flap`` (falcon wings pair)."""
    s = size
    if kind == "time":
        pygame.draw.circle(surf, _GOLD_BRIGHT, (cx, cy), s, 2)
        for ang in range(0, 360, 90):
            a = math.radians(ang - 90)
            x1 = cx + math.cos(a) * (s - 2)
            y1 = cy + math.sin(a) * (s - 2)
            x2 = cx + math.cos(a) * (s - 5)
            y2 = cy + math.sin(a) * (s - 5)
            pygame.draw.line(surf, _GOLD_BRIGHT, (x1, y1), (x2, y2), 1)
        ha = math.radians(45 - 90)
        ma = math.radians(160 - 90)
        pygame.draw.line(surf, _GOLD_BRIGHT, (cx, cy),
                         (cx + math.cos(ha) * s * 0.5,
                          cy + math.sin(ha) * s * 0.5), 2)
        pygame.draw.line(surf, _GOLD_BRIGHT, (cx, cy),
                         (cx + math.cos(ma) * s * 0.7,
                          cy + math.sin(ma) * s * 0.7), 2)
        pygame.draw.circle(surf, _GOLD_DEEP, (cx, cy), 2)
    elif kind == "coin":
        face = _ingame_coin_face()
        in_game_d = (COIN_R * 2 + 4)
        target_d = min(int(s * 2.6), in_game_d)
        scaled = pygame.transform.smoothscale(face, (target_d, target_d))
        surf.blit(scaled, scaled.get_rect(center=(cx, cy)))
    elif kind == "pillar":
        w = int(s * 1.0)
        pygame.draw.rect(surf, _GOLD_BRIGHT,
                         (cx - w // 2, cy - s, w, s * 2),
                         border_radius=2)
        pygame.draw.rect(surf, _GOLD_DEEP,
                         (cx - w // 2, cy - s, w, s * 2),
                         width=1, border_radius=2)
        pygame.draw.rect(surf, _GOLD_BRIGHT,
                         (cx - w // 2 - 2, cy - s - 2, w + 4, 4),
                         border_radius=1)
        pygame.draw.rect(surf, _GOLD_DEEP,
                         (cx - w // 2 - 2, cy - s - 2, w + 4, 4),
                         width=1, border_radius=1)
    elif kind == "flap":
        # Falcon wings — slim swept-back pair, tile-tuned (chosen wing
        # variant from docs/run_summary_redesign/wing_options_r9.png).
        for sign in (-1, 1):
            wing_pts = [
                (cx + sign * s * 0.04, cy - s * 0.30),
                (cx + sign * s * 0.30, cy - s * 0.60),
                (cx + sign * s * 0.80, cy - s * 0.62),
                (cx + sign * s * 1.20, cy - s * 0.18),
                (cx + sign * s * 1.35, cy + s * 0.10),
                (cx + sign * s * 1.05, cy + s * 0.20),
                (cx + sign * s * 0.95, cy + s * 0.50),
                (cx + sign * s * 0.65, cy + s * 0.25),
                (cx + sign * s * 0.45, cy + s * 0.35),
                (cx + sign * s * 0.22, cy + s * 0.12),
                (cx + sign * s * 0.04, cy + s * 0.00),
            ]
            pygame.draw.polygon(surf, _GOLD_BRIGHT, wing_pts)
            pygame.draw.polygon(surf, _GOLD_DEEP, wing_pts, 1)
            for sf, tf in [((0.20, -0.42), (1.30, 0.05)),
                           ((0.25, -0.32), (1.05, 0.18)),
                           ((0.30, -0.15), (0.85, 0.40)),
                           ((0.35, -0.00), (0.60, 0.25))]:
                pygame.draw.line(
                    surf, _GOLD_DEEP,
                    (cx + sign * sf[0] * s, cy + sf[1] * s),
                    (cx + sign * tf[0] * s, cy + tf[1] * s), 1)


def _stat_tile_chunky(surf, rect, icon_kind, value, label, subline=None):
    """Single stat tile — beveled navy card with gradient body, gold
    rim, icon at top, large value, optional subline ("61%"), bottom
    label. Auto-shrinks the label one step if it would crowd."""
    # Body — vertical gradient
    body = pygame.Surface(rect.size, pygame.SRCALPHA)
    for yy in range(rect.h):
        t = yy / max(1, rect.h - 1)
        c = lerp_color(_PANEL_LIGHTER, _PANEL_DARK, t)
        pygame.draw.line(body, (*c, 245), (0, yy), (rect.w, yy))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, rect.w, rect.h), border_radius=10)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(body, (*_GOLD_BRIGHT, 160), (0, 0, rect.w, rect.h),
                     width=1, border_radius=10)
    pygame.draw.line(body, (*_GOLD_PALE, 100),
                     (10, 3), (rect.w - 10, 3), 1)
    surf.blit(body, rect.topleft)
    # Icon
    _stat_tile_icon(surf, icon_kind, rect.centerx, rect.y + 22, size=15)
    # Value
    vf = _font(26, True).render(str(value), True, _GOLD_BRIGHT)
    vs = _font(26, True).render(str(value), True, NEAR_BLACK)
    vs.set_alpha(170)
    vy = rect.y + 52 if subline else rect.y + 58
    vr = vf.get_rect(center=(rect.centerx, vy))
    surf.blit(vs, (vr.x + 1, vr.y + 2))
    surf.blit(vf, vr)
    # Optional subline — bumped from 11pt muted to 13pt bright gold
    # with a near-black shadow so the COINS percentage reads at a
    # glance instead of fading into the tile shading.
    if subline:
        sf = _font(13, True).render(subline, True, _GOLD_BRIGHT)
        ss = _font(13, True).render(subline, True, NEAR_BLACK)
        ss.set_alpha(200)
        sub_center = (rect.centerx, rect.y + 76)
        sr = sf.get_rect(center=sub_center)
        surf.blit(ss, (sr.x + 1, sr.y + 2))
        surf.blit(sf, sr)
    # Label — auto-shrink for the longer captions
    max_label_w = rect.w - 10
    lbl_size = 12
    lf = _font(lbl_size, True).render(label, True, _GOLD_MUTED)
    while lf.get_width() > max_label_w and lbl_size > 10:
        lbl_size -= 1
        lf = _font(lbl_size, True).render(label, True, _GOLD_MUTED)
    lf.set_alpha(230)
    surf.blit(lf, lf.get_rect(center=(rect.centerx, rect.y + rect.h - 12)))


def _score_plaque(surf, rect, score: int, best: int, new_best: bool):
    """Engraved gold-frame plaque with FINAL SCORE caption, massive
    inset score numeral, and a BEST/delta line at the bottom."""
    # Outer gold frame
    pygame.draw.rect(surf, _GOLD_BRIGHT, rect, border_radius=20)
    # Inner darker bevel
    inner = rect.inflate(-8, -8)
    pygame.draw.rect(surf, _GOLD_DEEP, inner, border_radius=16)
    # Engraved face — gradient
    face = inner.inflate(-6, -6)
    grad = pygame.Surface(face.size, pygame.SRCALPHA)
    for yy in range(face.h):
        t = yy / max(1, face.h - 1)
        c = lerp_color(_PANEL_LIGHTER, _NIGHT_DEEP, t)
        pygame.draw.line(grad, (*c, 255), (0, yy), (face.w, yy))
    mask = pygame.Surface(face.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, face.w, face.h), border_radius=12)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, face.topleft)
    # Radial light hint upper-left of face
    glow = pygame.Surface(face.size, pygame.SRCALPHA)
    for rr in range(int(face.w * 0.6), 0, -2):
        a = int(18 * (1 - rr / (face.w * 0.6)))
        pygame.draw.circle(glow, (255, 220, 140, a),
                           (int(face.w * 0.35), int(face.h * 0.25)), rr)
    glow.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(glow, face.topleft)
    # FINAL SCORE caption
    sc = _font(15, True).render("F I N A L   S C O R E", True, _GOLD_MUTED)
    sc.set_alpha(230)
    surf.blit(sc, sc.get_rect(center=(rect.centerx, rect.y + 26)))
    # Massive engraved number
    big_num = str(score)
    nf = _font(88, True).render(big_num, True, _GOLD_BRIGHT)
    no = _font(88, True).render(big_num, True, _RED_OUTLINE)
    nsh = _font(88, True).render(big_num, True, NEAR_BLACK)
    deep_inner = _font(88, True).render(big_num, True, _GOLD_DEEP)
    nr = nf.get_rect(center=(rect.centerx, rect.centery + 4))
    px = 4
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(no, (nr.x + ox, nr.y + oy))
    nsh.set_alpha(180)
    surf.blit(nsh, (nr.x + 4, nr.y + 6))
    deep_inner.set_alpha(180)
    surf.blit(deep_inner, (nr.x - 1, nr.y - 1))
    surf.blit(nf, nr)
    # Best/delta line
    delta = score - best
    if new_best:
        cmp_text = f"NEW BEST  +{abs(delta)}"
        cmp_color = _GOLD_BRIGHT
    else:
        cmp_text = f"BEST {best}    {delta:+d}"
        cmp_color = _GOLD_MUTED
    cf = _font(13, True).render(cmp_text, True, cmp_color)
    cf.set_alpha(230)
    surf.blit(cf, cf.get_rect(center=(rect.centerx, rect.bottom - 20)))


class HUD:
    def __init__(self):
        self.pause_btn = PauseButton()
        self.help_btn = HelpButton()
        self.title_t = 0.0
        # Cached leaderboard layout (static parts). Rebuilt only when
        # scores / rank / error / pending / target size change.
        self._lb_cache: "pygame.Surface | None" = None
        self._lb_cache_key: tuple = ()
        # Name-entry button rects — populated each frame by draw_name_entry,
        # read by scenes.py click-handling. Pre-init to empty rects so the
        # first click before any draw is harmless.
        self.name_submit_rect = pygame.Rect(0, 0, 0, 0)
        self.name_skip_rect   = pygame.Rect(0, 0, 0, 0)
        # Run-summary button rects — populated by draw_stats each frame
        # so the STATE_STATS click handler in scenes.py can hit-test
        # PLAY AGAIN vs MAIN MENU.
        self.stats_play_again_rect = pygame.Rect(0, 0, 0, 0)
        self.stats_main_menu_rect  = pygame.Rect(0, 0, 0, 0)
        # Precompute star positions for overlay screens (seeded for consistency)
        rng = random.Random(42)
        self._stars = [
            (rng.randint(8, W - 8), rng.randint(8, H - 180),
             rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28))
            for _ in range(38)
        ]
        # Menu pill hit-test rects — populated each frame by draw_menu, read
        # by scenes.py click-handling. Pre-init to None so a click that
        # arrives before the first menu render falls through harmlessly.
        self.menu_start_rect: "pygame.Rect | None" = None
        self.menu_howto_rect: "pygame.Rect | None" = None
        self.menu_powerups_rect: "pygame.Rect | None" = None
        self.menu_top10_rect: "pygame.Rect | None" = None
        self.menu_settings_rect: "pygame.Rect | None" = None
        self.menu_profile_rect: "pygame.Rect | None" = None
        self.menu_store_rect: "pygame.Rect | None" = None
        self.store_toast_t = 0.0
        # Leaderboard tab hit-rects (CURRENT | LEGACY) — populated each frame
        # by draw_leaderboard in screen space, read by scenes.py to switch
        # boards without dismissing the screen. None until the first draw.
        self._lb_tab_current_rect: "pygame.Rect | None" = None
        self._lb_tab_legacy_rect: "pygame.Rect | None" = None

    def trigger_store_toast(self):
        """Arm the transient STORE 'coming soon' toast; draw_menu ticks it down."""
        self.store_toast_t = 1.6

    def draw_pause_overlay(self, surf, score: int = 0):
        # Deep blue-purple dim. The current score and coins pills from
        # draw_play sit underneath and read through the dim — no dedicated
        # pause score panel.
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 2, 28, 165))
        surf.blit(dim, (0, 0))

        # Title in the canonical gold-on-red run-summary treatment; only the
        # original size-pulse animation is dropped so it sits calm.
        cy = H // 2 + 30
        _outlined_text(surf, "PAUSED", (W // 2, cy), size=52, px=3)

        # Same flat dim-scarlet pill as the main-menu CTAs.
        _pill_btn(surf, (W // 2, cy + 72), "TAP TO GAME",
                  size=18, alpha=230, min_width=220, dim=True, shadow=False)

    def draw_menu(self, surf, dt, best: int):
        self.title_t += dt
        # Night-sky tint overlay
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 1, 21, 110))
        surf.blit(dim, (0, 0))

        # Minus the handful that land on the cottage and Pip — see
        # _menu_star_field. The veil above still dims the diorama; only the
        # sparkles move behind it.
        _draw_overlay_stars(surf, _menu_star_field(self._stars), self.title_t)

        # Mountain silhouette belongs to the background, drawn before the
        # foreground UI so the pill / profile card / chips sit cleanly
        # on top of it instead of being darkened by the alpha-180 layer.
        _draw_mountain_silhouette(surf, alpha=180)

        # Floating title — sits above the gameplay-opener post-house +
        # Pip composition (cottage top is at y≈208) so the text never
        # crosses the parrot.
        pulse = 1.0 + math.sin(self.title_t * 2.4) * 0.04
        float_y = int(7 * math.sin(self.title_t * 1.8))
        _outlined_text(surf, "SKYBIT", (W // 2, 112 + float_y),
                        size=int(72 * pulse), px=3, shadow_offset=(2, 3))

        # Subtitle — same gold-on-red outline as SKYBIT, just smaller and
        # with a tighter pixel outline so it reads as a partner line. The whole
        # block sits higher than it used to, and the divider that used to close
        # it is gone: the PROFILE frame now opens at y204, which the old rule
        # at y208 ran straight through.
        _outlined_text(surf, "POCKET  SKY  FLYER", (W // 2, 168),
                        size=20, px=2, shadow_offset=(1, 2))

        # The menu's furniture: three plank signs hung from Pip's cloud, START
        # planted on its own post bottom-right, and the jewel frame that makes
        # the standing-Pip diorama the PROFILE entry. One cached layer, blitted
        # over the already-drawn diorama so the frame sits on top of Pip.
        #
        # START left the sign chain deliberately. As a centred pill above the
        # utilities it put the primary control ABOVE them and shared a column
        # with nothing; planted low and right it is the lowest, largest target
        # on the screen and nearest the thumb.
        furniture, rects = _menu_furniture()
        surf.blit(furniture, (0, 0))
        self.menu_start_rect = rects["START"]
        self.menu_profile_rect = rects["PROFILE"]
        self.menu_store_rect = rects["STORE"]
        self.menu_top10_rect = rects["TOP 10"]
        self.menu_settings_rect = rects["SETTINGS"]

        # Transient STORE "coming soon" toast — a small gold-rimmed tag above
        # the STORE chip, fading via the countdown armed on a STORE tap.
        if self.store_toast_t > 0 and self.menu_store_rect is not None:
            self.store_toast_t = max(0.0, self.store_toast_t - dt)
            img = _font(11, True).render("COMING SOON", True, _GOLD_PALE)
            bg = img.get_rect().inflate(16, 8)
            bg.center = (self.menu_store_rect.centerx,
                         self.menu_store_rect.top - 16)
            tag = pygame.Surface(bg.size, pygame.SRCALPHA)
            tag.fill((16, 10, 34, 232))
            surf.blit(tag, bg.topleft)
            pygame.draw.rect(surf, _GOLD_BRIGHT, bg, width=1, border_radius=6)
            surf.blit(img, img.get_rect(center=bg.center))

    def draw_play(self, surf, world, best: int, paused: bool = False):
        # ── Score plate. SKATEBOARD wraps the score inside the deck banner
        # (`render_caption_overlay`) — coin + pause render first, then the
        # deck composites on top of them, then the live halftone burst from
        # `render_skateboard_score_e3` lands at the deck centre. Outside
        # skateboard mode the slate NA plate is the standard score plate.
        skateboard_active = getattr(world.bird, "skateboard_active", False)
        skateboard_score_paint = None
        if skateboard_active and not paused:
            from game.skateboard_fx import render_skateboard_score_e3
            cap_t = getattr(world, "skateboard_caption_t", 0.0)
            FADE = 0.8
            if cap_t > FADE:
                score_alpha = 255
            elif cap_t > 0:
                x = 1.0 - cap_t / FADE
                score_alpha = int(255 * (1.0 - x) ** 2)
            else:
                score_alpha = 0
            if score_alpha > 0:
                lift_y = getattr(world, "_skateboard_lift_y", 0)
                deck_overlay = getattr(
                    world, "skateboard_caption_overlay", None)

                def paint():
                    if deck_overlay is not None:
                        deck_overlay.set_alpha(score_alpha)
                        surf.blit(deck_overlay, (0, -lift_y))
                    score_surf = render_skateboard_score_e3(world.score)
                    score_surf.set_alpha(score_alpha)
                    surf.blit(score_surf, (0, -lift_y))

                skateboard_score_paint = paint
        else:
            score_txt = str(world.score)
            sf = _font(46, True)
            sw = max(sf.size("8" * len(score_txt))[0] + 54, 102)
            sp = pygame.Rect((W - sw) // 2, 42, sw, 56)
            _na_plate(surf, sp, cut=9, round_r=9, inner_warm=_NA_WARM, glow=True)
            cf = _font(48, True)
            face = cf.render(score_txt, True, _SCORE_FACE)
            rim  = cf.render(score_txt, True, _GOLD_DEEP)
            sh   = cf.render(score_txt, True, NEAR_BLACK)
            r = face.get_rect(center=sp.center)
            for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                           (-2, -2), (2, -2), (-2, 2), (2, 2)):
                surf.blit(rim, (r.x + ox, r.y + oy))
            sh.set_alpha(180)
            surf.blit(sh, (r.x + 2, r.y + 4))
            surf.blit(face, r.topleft)

        # ── Pill alpha fades when bird is near top
        bird_y = world.bird.y
        if bird_y >= 80:
            ui_alpha = 255
        elif bird_y <= 20:
            ui_alpha = 40
        else:
            ui_alpha = int(40 + 215 * (bird_y - 20) / 60)

        # ── Coins plate: same slate cut-corner kit at top-left, auto-grows with
        # count so triple-/quadruple-digit values don't clip. The plate + coin
        # icon + gold count are composited on one surface so the whole element
        # fades together as the bird nears the top edge.
        coin_text = f"x{world.coin_count}"
        cf2 = _font(20, True)
        cw = cf2.size("8" * len(coin_text))[0] + 46
        cp = pygame.Rect(12, 14, cw, 38)
        pad = _NA_PAD
        coin_surf = pygame.Surface((cw + pad * 2, 38 + pad * 2), pygame.SRCALPHA)
        _na_plate(coin_surf, pygame.Rect(pad, pad, cw, 38), cut=7, round_r=8,
                  glow=False)
        _coin_icon(coin_surf, pad + 19, pad + 19, 12)
        tw = cf2.size(coin_text)[0]
        _outlined_text(coin_surf, coin_text, (pad + 36 + tw // 2, pad + 19), 20,
                       fill=UI_GOLD, outline=NEAR_BLACK, px=2, shadow_offset=None)
        coin_surf.set_alpha(ui_alpha)
        surf.blit(coin_surf, (cp.x - pad, cp.y - pad))

        # Pause button
        self.pause_btn.draw(surf, paused=paused)

        # SKATEBOARD deck banner sits ON TOP of coin + pause so the deck
        # silhouette covers the chrome where they overlap; the live
        # halftone score then lands at the deck centre.
        if skateboard_score_paint is not None:
            skateboard_score_paint()

        # "Get ready" prompt while the pre-start freeze is active.
        if world.ready_t > 0:
            pulse = 0.5 + 0.5 * math.sin(self.title_t * 5)
            alpha = int(180 + 60 * pulse)
            font_big = _font(22, True)
            label = font_big.render("TAP TO FLY", True, WHITE)
            label.set_alpha(alpha)
            lr = label.get_rect(center=(W // 2, 340))
            # dark plate behind for legibility
            plate = pygame.Surface((lr.width + 36, lr.height + 18),
                                   pygame.SRCALPHA)
            pygame.draw.ellipse(plate, (0, 0, 20, 140), plate.get_rect())
            surf.blit(plate, (W // 2 - plate.get_width() // 2,
                              lr.y - 9))
            surf.blit(label, lr.topleft)

        # Nest lives display — side-by-side woven cups, top-left corner.
        _draw_pip_lives_row(surf,
                            getattr(world, "lives_remaining", LIVES_PER_RUN),
                            LIVES_PER_RUN)

        # Active-buff timer bars — every active power-up gets its own
        # progress bar at the top of the screen with the buff's logo on the
        # left. Stacks vertically when multiple are active. Each bar's fill
        # shifts green → yellow → red as its time depletes, so remaining
        # duration reads at a glance from colour alone.
        active = []
        if world.triple_timer > 0:
            active.append(("triple", world.triple_timer, TRIPLE_DURATION))
        if world.magnet_timer > 0:
            active.append(("magnet", world.magnet_timer, MAGNET_DURATION))
        if getattr(world, "megamagnet_timer", 0) > 0:
            active.append(("megamagnet", world.megamagnet_timer, MEGAMAGNET_DURATION))
        if world.slowmo_timer > 0:
            active.append(("slowmo", world.slowmo_timer, SLOWMO_DURATION))
        if world.kfc_timer > 0:
            active.append(("kfc", world.kfc_timer, KFC_DURATION))
        if world.ghost_timer > 0:
            active.append(("ghost", world.ghost_timer, GHOST_DURATION))
        if world.grow_timer > 0:
            active.append(("grow", world.grow_timer, GROW_DURATION))
        if world.reverse_timer > 0:
            active.append(("reverse", world.reverse_timer, REVERSE_DURATION))
        if getattr(world, "shrink_timer", 0) > 0:
            active.append(("shrink", world.shrink_timer, SHRINK_DURATION))
        if getattr(world, "skateboard_timer", 0) > 0:
            active.append(("skateboard", world.skateboard_timer, SKATEBOARD_DURATION))
        if getattr(world, "knight_timer", 0) > 0:
            active.append(("knight", world.knight_timer, KNIGHT_DURATION))
        # Poison: ticks down for POISON_DURATION; at t=1.0 the bar drops
        # off and the flap guard kicks in (Pip dives until collision).
        if (getattr(world.bird, "poison_active", False)
                and world.bird.poison_t < 1.0):
            poison_remain = POISON_DURATION * (1.0 - world.bird.poison_t)
            active.append(("poison", poison_remain, POISON_DURATION))
        if getattr(world, "umbrella_timer", 0) > 0:
            active.append(("umbrella", world.umbrella_timer, UMBRELLA_DURATION))
        # Genie has no timer bar — it's an instantaneous meta-powerup.
        # Rail intentionally has NO HUD timer bar: it's pillar-budgeted
        # rather than seconds-budgeted, and the on-world track + cart
        # already show the remaining ride at a glance.
        # Lottery is one-shot — the slot-machine reveal overlay carries
        # the result feedback; no HUD bar needed.

        if active:
            icon_size = 32
            bar_w     = 132
            bar_h     = 18
            row_gap   = 8
            row_pitch = icon_size + row_gap
            row_w     = icon_size + 8 + bar_w
            base_x    = (W - row_w) // 2
            # Buff stack always anchors at the normal y; the SKATEBOARD
            # deck banner above can graze the top edge of the first bar
            # — bars paint after the deck so they sit on top of that
            # overlap zone cleanly. Keeping one fixed y means the row
            # never JUMPS when skateboard activates/expires.
            top_y = 110

            for i, (kind, remain, total) in enumerate(active):
                y = top_y + i * row_pitch
                # Icon plate on the left — the slate kit plate with the WARM
                # energy accent so it reads as part of the timer, not the score.
                icon_rect = pygame.Rect(base_x, y, icon_size, icon_size)
                _na_plate(surf, icon_rect, cut=7, round_r=7,
                          accent=_ENERGY_FULL, glow=False)
                # Emblem fills the plate; its own padding + contact shadow give
                # the inset, so no inflate here (the silhouette sits ~24px).
                _draw_buff_icon(surf, icon_rect, kind)

                # Energy bar to the right (drains yellow→amber, recessed track).
                bx = icon_rect.right + 8
                by = y + (icon_size - bar_h) // 2
                frac = max(0.0, min(1.0, remain / total))
                bar = pygame.Rect(bx, by, bar_w, bar_h)
                _na_energy_bar(surf, bar, frac)
                _text(surf, f"{remain:.1f}s", (bar.centerx, bar.centery),
                      size=11, color=UI_CREAM, shadow=True)

        # Float texts
        for ft in world.float_texts:
            ft.draw(surf)

        # Cycle-finale "DAY N COMPLETE!" banner — screen-space overlay
        # drawn after float texts so the "+100!" pops UNDER the banner
        # text. The banner's own envelope (drop-in / bounce / hold /
        # fade) advances in World.update.
        for tb in getattr(world, "treasure_banners", ()):
            tb.draw(surf)

        # SKATEBOARD trick bubbles — comic halftone bursts stacked
        # near the score so the pop-art badge reads as part of the
        # score visual when a trick lands.
        for tb in getattr(world, "trick_bubbles", ()):
            tb.draw(surf)

    def draw_stats(self, surf, world, dt, elapsed,
                   best: int = 0, new_best: bool = False,
                   show_prompt: bool = True):
        """Run-summary screen — Trophy Cinema layout. RUN SUMMARY title,
        engraved score plaque, 4 stat tiles (TIME · COINS+% · PILLARS ·
        FLAPS), compact power-up icon strip, PLAY AGAIN primary +
        MAIN MENU secondary buttons. ``show_prompt`` is kept for caller
        compatibility but no longer drives a tap-to-continue prompt —
        the buttons replace that affordance."""
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((*_NIGHT_DEEP, 190))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)
        _draw_mountain_silhouette(surf, alpha=160)

        # The power-up strip drives the whole layout. A run that grabbed
        # enough distinct kinds to need three rows uses the compact
        # arrangement (lifted title, shorter plaque, raised tiles) so the
        # rows fit; every other run keeps the original, roomier layout. The
        # bright bold gold-ruled caption is shared by both.
        pu = [(k, c) for k, c in world.powerups_picked.items() if c > 0]
        chip_h = 40
        icon_size = 30
        chip_radius = chip_h // 2
        pad_l, pad_r = 3, 8
        gap = 5
        available = W - 10
        pitch = chip_h + 8
        chips, rows, n_rows = [], [], 0
        if pu:
            # Lazy import: game.powerup_help imports from game.hud, so
            # we defer this until the first stats-screen render.
            from game.powerup_help import (
                _powerup_icon as _ingame_powerup_icon,
            )
            count_font = _font(16, True)
            for kind, count in pu:
                tf = count_font.render(f"×{count}", True, _GOLD_BRIGHT)
                chip_w = pad_l + icon_size + 2 + tf.get_width() + pad_r
                chips.append((kind, count, chip_w, tf))

            def _split(n):
                # Even split, any remainder loaded onto the earlier rows.
                base, extra = divmod(len(chips), n)
                out, i = [], 0
                for r in range(n):
                    k = base + (1 if r < extra else 0)
                    out.append(chips[i:i + k])
                    i += k
                return out

            n_rows = 3
            for n in (1, 2, 3):
                trial = _split(n)
                if all(sum(c[2] for c in row) + gap * (len(row) - 1)
                       <= available for row in trial if row):
                    n_rows = n
                    break
            rows = _split(n_rows)

        # Only a run that genuinely needs a third row gets the compact
        # geometry; everything else (incl. no power-ups) stays original.
        compact = (n_rows == 3)
        if compact:
            title_y = 50
            plaque = pygame.Rect(18, 88, W - 36, 140)
            tile_y = 244
            cap_y = 374
            # Centre the three-row block in the band between caption and
            # the PLAY AGAIN button so it stays balanced and clears it.
            first_row_y = 468 - (n_rows - 1) * pitch // 2
            play_y, menu_y = 572, 618
        else:
            title_y = 56
            plaque = pygame.Rect(18, 104, W - 36, 156)
            tile_y = 282
            cap_y = 414
            # Anchor the row(s) just below the caption, as the original
            # did; the +44 offset leaves the bigger bold caption clear air.
            first_row_y = cap_y + 44
            play_y, menu_y = 568, 618

        # Title — canonical gold-on-red treatment, same family as SKYBIT.
        _outlined_text(surf, "RUN  SUMMARY", (W // 2, title_y),
                       size=34, px=3, shadow_offset=(3, 5))

        # Hero score plaque
        _score_plaque(surf, plaque, world.score, best, new_best)

        # Stat tiles (TIME · COINS+% · PILLARS · FLAPS)
        mins = int(world.time_alive) // 60
        secs = int(world.time_alive) % 60
        time_str = f"{mins}:{secs:02d}" if mins else f"{secs}s"
        # "Coins encountered" = coins that left the player's reach.
        # Coins still on screen don't count as missed yet.
        coins_encountered = max(0, world.coins_spawned - len(world.coins))
        coins_pct = (round(world.coin_count / coins_encountered * 100)
                     if coins_encountered > 0 else None)
        coins_sub = f"{coins_pct}%" if coins_pct is not None else None
        tiles = [
            ("time",   time_str,                       "TIME",    None),
            ("coin",   str(world.coin_count),          "COINS",   coins_sub),
            ("pillar", str(world.pillars_passed),      "PILLARS", None),
            ("flap",   str(world.flap_count),          "FLAPS",   None),
        ]
        tile_w = 78
        # Tile height grew from 98 → 104 to give the bigger COINS-%
        # subline (now 13pt bright) breathing room above the label.
        tile_h = 104
        tile_gap = 8
        total_w = len(tiles) * tile_w + (len(tiles) - 1) * tile_gap
        start_x = (W - total_w) // 2
        for i, (kind, val, lbl, sub) in enumerate(tiles):
            r = pygame.Rect(start_x + i * (tile_w + tile_gap), tile_y,
                            tile_w, tile_h)
            _stat_tile_chunky(surf, r, kind, val, lbl, subline=sub)

        # Power-ups row — Variant C "Horizontal Pills": each power-up
        # rendered as a navy gold-bordered chip with [icon | ×N] laid
        # out side-by-side. Strong text legibility and clear visual
        # separation between kinds, under a bright bold gold-ruled caption.
        if pu:
            total_pu = sum(c for _, c in pu)
            # Bright heavy-bold caption flanked by short gold rules — a
            # section-header treatment that gives the line clear presence
            # in its own band, above the pill strip. _font already returns
            # the bold face, so set_bold stacks synthetic weight on top;
            # unset right after to leave the cached font untouched for
            # other callers.
            cf = _font(20, True)
            cf.set_bold(True)
            cap = cf.render(
                f"{total_pu}  POWER-UPS USED",
                True, _GOLD_BRIGHT)
            cf.set_bold(False)
            cap_rect = cap.get_rect(center=(W // 2, cap_y))
            surf.blit(cap, cap_rect)
            rule_run, rule_gap = 56, 14
            pygame.draw.line(surf, _GOLD_BRIGHT,
                             (cap_rect.left - rule_gap - rule_run, cap_y),
                             (cap_rect.left - rule_gap, cap_y), 2)
            pygame.draw.line(surf, _GOLD_BRIGHT,
                             (cap_rect.right + rule_gap, cap_y),
                             (cap_rect.right + rule_gap + rule_run, cap_y), 2)

            for ri, row_chips in enumerate(rows):
                row_total = (sum(c[2] for c in row_chips)
                             + gap * (len(row_chips) - 1))
                sx = (W - row_total) // 2
                y = first_row_y + ri * pitch
                for kind, count, chip_w, tf in row_chips:
                    # Render the chip body at 2× then smoothscale down so
                    # the rounded corners + gold border are anti-aliased
                    # instead of pixel-stepped.
                    OS = 2
                    ow, oh = chip_w * OS, chip_h * OS
                    o_radius = chip_radius * OS
                    body_big = pygame.Surface((ow, oh), pygame.SRCALPHA)
                    for yy in range(oh):
                        t = yy / max(1, oh - 1)
                        c = lerp_color(_PANEL_LIGHTER, _PANEL_DARK, t)
                        pygame.draw.line(body_big, (*c, 245),
                                         (0, yy), (ow, yy))
                    mask_big = pygame.Surface((ow, oh), pygame.SRCALPHA)
                    pygame.draw.rect(mask_big, (255, 255, 255, 255),
                                     (0, 0, ow, oh),
                                     border_radius=o_radius)
                    body_big.blit(mask_big, (0, 0),
                                  special_flags=pygame.BLEND_RGBA_MIN)
                    pygame.draw.rect(body_big, _GOLD_BRIGHT,
                                     (0, 0, ow, oh),
                                     width=2 * OS, border_radius=o_radius)
                    body = pygame.transform.smoothscale(body_big,
                                                       (chip_w, chip_h))
                    surf.blit(body, (sx, y - chip_h // 2))
                    _ingame_powerup_icon(
                        surf, kind,
                        sx + pad_l + icon_size // 2 + 2, y,
                        int(icon_size * 1.5))
                    surf.blit(tf, tf.get_rect(
                        midright=(sx + chip_w - pad_r, y)))
                    sx += chip_w + gap

        # Buttons — PLAY AGAIN primary, MAIN MENU secondary.
        # Hide button hit rects until the 0.6s reveal gate has elapsed
        # (matches the previous "tap to continue" debounce window so a
        # stray tap from the death event doesn't immediately fire).
        if elapsed >= 0.6:
            self.stats_play_again_rect = _pill_btn(
                surf, (W // 2, play_y), "PLAY  AGAIN",
                size=22, alpha=255, min_width=240, primary=True, dim=True,
                shadow=False)
            self.stats_main_menu_rect = _outline_pill_btn(
                surf, (W // 2, menu_y), "MAIN MENU",
                size=14, min_width=130)
        else:
            self.stats_play_again_rect = pygame.Rect(0, 0, 0, 0)
            self.stats_main_menu_rect = pygame.Rect(0, 0, 0, 0)

    def draw_name_entry(self, surf, dt, buf: str):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((8, 3, 26, 240))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)

        # Trophy above the title — same emblem as the TOP 10 screen.
        _draw_trophy(surf, W // 2, H // 2 - 180, 22)

        # Title — gold + red outline to match the mockup
        _outlined_text(surf, "NEW  HIGH  SCORE!",
                       (W // 2, H // 2 - 130),
                       size=24, px=2, shadow_offset=(2, 3))

        # Divider line under the title (mockup convention).
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 130),
                         (W // 2 - 50, H // 2 - 108),
                         (W // 2 + 50, H // 2 - 108), 1)

        # Engraved nameplate (gold rim + corner rivets + dark navy face)
        # in place of the plain orange-bordered input field.
        fw, fh = 284, 54
        fx, fy = W // 2 - fw // 2, H // 2 - 70
        plate_rect = pygame.Rect(fx, fy, fw, fh)
        pygame.draw.rect(surf, _GOLD_BRIGHT, plate_rect, border_radius=8)
        inner = plate_rect.inflate(-6, -6)
        pygame.draw.rect(surf, _PANEL_DARK, inner, border_radius=6)
        pygame.draw.rect(surf, _GOLD_DEEP, plate_rect,
                         width=2, border_radius=8)
        # Subtle cream highlight just inside the top edge.
        pygame.draw.line(surf, (255, 240, 180),
                         (plate_rect.x + 10, plate_rect.y + 3),
                         (plate_rect.right - 10, plate_rect.y + 3), 1)
        # Four corner rivets.
        for rx, ry in (
            (plate_rect.x + 8, plate_rect.y + 8),
            (plate_rect.right - 8, plate_rect.y + 8),
            (plate_rect.x + 8, plate_rect.bottom - 8),
            (plate_rect.right - 8, plate_rect.bottom - 8),
        ):
            pygame.draw.circle(surf, _GOLD_DEEP, (rx, ry), 3)
            pygame.draw.circle(surf, _GOLD_BRIGHT, (rx, ry), 3, 1)
            pygame.draw.circle(surf, (255, 240, 180), (rx - 1, ry - 1), 1)

        # Typed text — gold with a soft black drop shadow, no cursor.
        tf = _font(26, True)
        if buf:
            sh = tf.render(buf, True, NEAR_BLACK)
            sh.set_alpha(180)
            txt = tf.render(buf, True, _GOLD_BRIGHT)
            tr = txt.get_rect(center=(W // 2, fy + fh // 2))
            surf.blit(sh, (tr.x + 1, tr.y + 2))
            surf.blit(txt, tr)
        else:
            placeholder = _font(18, False).render("TYPE YOUR NAME…",
                                                  True, _GOLD_MUTED)
            placeholder.set_alpha(100)
            surf.blit(placeholder,
                      placeholder.get_rect(center=(W // 2, fy + fh // 2)))

        # Mountain silhouette belongs to the backdrop — drawn before the
        # buttons so SUBMIT / SKIP sit on top of any scenery, never behind it.
        _draw_mountain_silhouette(surf, alpha=160)

        # Paired action buttons — SUBMIT promoted to the primary pill
        # so it carries the gold halo in the mockup.
        self.name_submit_rect = _pill_btn(
            surf, (W // 2, H // 2 + 34), "SUBMIT",
            size=18, alpha=255, min_width=200, primary=True)
        self.name_skip_rect = _pill_btn(
            surf, (W // 2, H // 2 + 92), "SKIP",
            size=18, alpha=255, min_width=200)

    def draw_leaderboard(self, surf, dt, scores: list, player_rank: int,
                         cooldown: float, fetch_error: str = "",
                         legacy_scores: "list | None" = None,
                         legacy_fetch_error: str = "", selected_tab: int = 0,
                         legacy_loading: bool = False):
        # Internally render at 3× supersample so the leaderboard's text
        # and circle edges come out clean on both desktop and mobile.
        # The whole static layout is cached (keyed on both boards' scores +
        # rank + errors + selected tab + target size); only the animated
        # TAP TO MENU prompt is re-rendered per frame.
        self.title_t += dt
        SCALE = 3
        target_w, target_h = surf.get_size()

        cur_key = tuple((e["name"], e["score"]) for e in scores)
        leg_key = tuple((e["name"], e["score"]) for e in (legacy_scores or []))
        key = (target_w, target_h, cur_key, leg_key, player_rank,
               fetch_error, legacy_fetch_error, selected_tab, legacy_loading)

        if self._lb_cache_key != key:
            hd_w, hd_h = W * SCALE, H * SCALE
            hd = pygame.Surface((hd_w, hd_h), pygame.SRCALPHA)
            self._render_leaderboard(hd, scores, player_rank,
                                     fetch_error, SCALE,
                                     legacy_scores=legacy_scores,
                                     legacy_fetch_error=legacy_fetch_error,
                                     selected_tab=selected_tab,
                                     legacy_loading=legacy_loading)
            if (target_w, target_h) == (hd_w, hd_h):
                self._lb_cache = hd
            else:
                self._lb_cache = pygame.transform.smoothscale(
                    hd, (target_w, target_h))
            self._lb_cache_key = key

        surf.blit(self._lb_cache, (0, 0))

        # Expose the tab hit-rects in screen space each frame so scenes.py can
        # switch boards. The window is exactly W×H, so native geometry maps
        # 1:1, but scale by the target ratio defensively for any size.
        tx, ty, tw, th = _lb_tab_geometry()
        sx, sy = target_w / W, target_h / H
        half = tw // 2
        self._lb_tab_current_rect = pygame.Rect(
            int(tx * sx), int(ty * sy), int(half * sx), int(th * sy))
        self._lb_tab_legacy_rect = pygame.Rect(
            int((tx + half) * sx), int(ty * sy),
            int((tw - half) * sx), int(th * sy))

        # TAP TO MENU prompt — pulses every frame, so rendered live on
        # top of the cached static layout. Show whenever the user can
        # dismiss the view (cooldown elapsed) including during loading.
        if cooldown <= 0:
            out_scale = max(1, target_w // W)
            alpha = int(170 + math.sin(self.title_t * 4) * 70)
            f2 = _font(16 * out_scale, True)
            prompt = f2.render("TAP  TO  MENU", True, _GOLD_MUTED)
            prompt.set_alpha(alpha)
            pr = prompt.get_rect(center=(target_w // 2,
                                         target_h - 28 * out_scale))
            surf.blit(prompt, pr.topleft)

    def _render_leaderboard(self, surf, scores: list, player_rank: int,
                            fetch_error: str, S: int,
                            legacy_scores: "list | None" = None,
                            legacy_fetch_error: str = "", selected_tab: int = 0,
                            legacy_loading: bool = False):
        """Static leaderboard layout (no TAP TO MENU prompt) at scale S.
        ``surf`` is sized ``(W*S, H*S)``; every coord, font size and stroke
        width is multiplied by ``S``. Draws the CURRENT|LEGACY tab control
        plus whichever board ``selected_tab`` selects."""
        Ws, Hs = W * S, H * S
        dim = pygame.Surface((Ws, Hs), pygame.SRCALPHA)
        dim.fill((0, 0, 20, 200))
        surf.blit(dim, (0, 0))

        # Header: trophy icon — "TOP 10" — trophy icon
        _outlined_text(surf, "TOP 10", (Ws // 2, _LB_HEADER_Y * S), size=28 * S,
                       px=3 * S, shadow_offset=(3 * S, 5 * S))
        for side in (-1, 1):
            _draw_trophy(surf, Ws // 2 + side * 84 * S, _LB_HEADER_Y * S, 15 * S)

        # Segmented tab control + per-board subline / frozen ribbon.
        _draw_lb_tabs(surf, S, selected_tab)
        _draw_lb_subline(surf, S, selected_tab)

        # The legacy board is read-only and never highlights a player.
        if selected_tab == 1:
            active, active_err, active_rank = (legacy_scores or []), \
                legacy_fetch_error, -1
        else:
            active, active_err, active_rank = scores, fetch_error, player_rank

        card_x, card_w = 14 * S, (W - 28) * S
        card_y = _LB_CARD_Y * S

        n = len(active)
        if n == 0:
            if selected_tab == 1 and legacy_loading:
                _text(surf, "Loading…",
                      (Ws // 2, card_y + 60 * S),
                      size=18 * S, color=UI_CREAM, shadow=True)
            elif selected_tab == 1 and active_err:
                # A legacy RLS/network failure isn't something the player can
                # act on, so skip the developer-facing "browser console" hint.
                _text(surf, "Legacy board unavailable",
                      (Ws // 2, card_y + 60 * S),
                      size=18 * S, color=UI_CREAM, shadow=True)
                _text(surf, "Try again later.",
                      (Ws // 2, card_y + 94 * S),
                      size=14 * S, color=UI_CREAM, shadow=False)
            elif active_err:
                _text(surf, "Top-10 unavailable",
                      (Ws // 2, card_y + 60 * S),
                      size=18 * S, color=UI_CREAM, shadow=True)
                _text(surf, "Check the browser console",
                      (Ws // 2, card_y + 94 * S),
                      size=12 * S, color=UI_CREAM, shadow=False)
                _text(surf, "(" + active_err + ")",
                      (Ws // 2, card_y + 116 * S),
                      size=11 * S, color=UI_CREAM, shadow=False)
            elif selected_tab == 1:
                _text(surf, "No legacy scores",
                      (Ws // 2, card_y + 60 * S),
                      size=18 * S, color=UI_CREAM, shadow=True)
            else:
                _text(surf, "No scores yet!",
                      (Ws // 2, card_y + 60 * S),
                      size=18 * S, color=UI_CREAM, shadow=True)
                _text(surf, "Be the first.",
                      (Ws // 2, card_y + 94 * S),
                      size=14 * S, color=UI_CREAM, shadow=False)
            return

        row_h = _LB_ROW_H * S
        row_gap = _LB_ROW_GAP * S

        SILVER = (185, 195, 205)
        BRONZE = (185, 125,  55)

        f_badge = _font(13 * S, True)
        f_name  = _font(16 * S, True)
        f_you   = _font(10 * S, True)
        f_score = _font(17 * S, True)

        hd_crown = _get_crown_sprite_hd(S)

        ry = card_y
        for i, entry in enumerate(active):
            rank = i + 1
            if rank == 1:    badge_col = _GOLD_BRIGHT
            elif rank == 2:  badge_col = SILVER
            elif rank == 3:  badge_col = BRONZE
            else:            badge_col = _GOLD_BRIGHT

            is_player = (i == active_rank)
            row_cy = ry + row_h // 2
            is_medal = rank in _MEDAL_GRADIENTS

            row_rect = pygame.Rect(card_x, ry, card_w, row_h)
            row_radius = row_h // 2
            if is_medal:
                pnl = _medal_row_pill(card_w, row_h, row_radius, rank)
            else:
                pnl = pygame.Surface(row_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(pnl, (*_PANEL_DARK, 220),
                                 (0, 0, card_w, row_h),
                                 border_radius=row_radius)
                if is_player:
                    pygame.draw.rect(pnl, _GOLD_BRIGHT,
                                     (0, 0, card_w, row_h),
                                     width=3 * S, border_radius=row_radius)
                else:
                    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 110),
                                     (0, 0, card_w, row_h),
                                     width=1 * S, border_radius=row_radius)
            surf.blit(pnl, row_rect.topleft)

            badge_cx = card_x + 24 * S
            badge_r = 13 * S
            if rank <= 3:
                pygame.draw.circle(surf, badge_col,
                                   (badge_cx, row_cy), badge_r)
                pygame.draw.circle(surf, NEAR_BLACK,
                                   (badge_cx, row_cy), badge_r, 1 * S)
                num_col = NEAR_BLACK
            else:
                pygame.draw.circle(surf, badge_col,
                                   (badge_cx, row_cy), badge_r, 2 * S)
                num_col = _GOLD_BRIGHT
            num_img = f_badge.render(str(rank), True, num_col)
            surf.blit(num_img,
                      num_img.get_rect(center=(badge_cx, row_cy)))

            if rank == 1:
                c_w, c_h = hd_crown.get_size()
                surf.blit(hd_crown,
                          (badge_cx - c_w // 2,
                           row_cy - 7 * S - c_h))

            nm = entry["name"][:10]
            if is_medal:
                name_col = NEAR_BLACK
            else:
                name_col = _GOLD_BRIGHT if is_player else WHITE
            nm_img = f_name.render(nm, True, name_col)
            nm_x = card_x + 44 * S
            surf.blit(nm_img,
                      (nm_x, row_cy - nm_img.get_height() // 2))

            if is_player:
                you_img = f_you.render("YOU", True, WHITE)
                pw = you_img.get_width() + 10 * S
                ph = you_img.get_height() + 6 * S
                pxr = nm_x + nm_img.get_width() + 7 * S
                pyr = row_cy - ph // 2
                you_pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
                pygame.draw.rect(you_pill, _SCARLET_TOP,
                                 (0, 0, pw, ph), border_radius=ph // 2)
                pygame.draw.rect(you_pill, _GOLD_BRIGHT,
                                 (0, 0, pw, ph),
                                 width=1 * S, border_radius=ph // 2)
                surf.blit(you_pill, (pxr, pyr))
                surf.blit(you_img, (pxr + 5 * S, pyr + 3 * S))

            score_col = NEAR_BLACK if is_medal else _GOLD_BRIGHT
            sc_img = f_score.render(str(entry["score"]), True, score_col)
            surf.blit(sc_img,
                      (card_x + card_w - 16 * S - sc_img.get_width(),
                       row_cy - sc_img.get_height() // 2))

            ry += row_h + row_gap

        # Legacy board: a cool aged-navy patina wash over the rows + a wax
        # FINAL seal in the dead-zone below the last row, so the frozen hall
        # of fame reads as an intentional archive rather than a broken board.
        if selected_tab == 1:
            rows_bottom = ry - row_gap
            patina = pygame.Surface((card_w, rows_bottom - card_y),
                                    pygame.SRCALPHA)
            patina.fill((26, 36, 78, 40))
            surf.blit(patina, (card_x, card_y))
            seal_cy = (rows_bottom + (H - 30) * S) // 2
            _draw_final_seal(surf, Ws // 2, seal_cy, _LB_SEAL_R * S, S)
