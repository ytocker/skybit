"""POISON VIAL — Round 5 skull-CONTAINED-inside-flask micro-variants.

Round-4 review note: the skull-and-crossbones glyph sat too large on the
cone; the femur knobs poked past the green glass silhouette on all four
variants, which broke the "label on a vial" read and made the X feel
pasted on top instead of painted on the flask.

Round 5 keeps every other Round-4 property (erlenmeyer body, sickly
green liquid, cork, yellow-green vapor, ~190-alpha warning halo, aged
bone tone, cylindrical femurs) but:

- Glyph bounding box shrinks ~38% so the bone tips clear the inner
  green wall on every variant.
- Glyph recentres a touch ABOVE geometric centre — the cone narrows
  upward, and a centred-on-mean-y placement would let the femurs
  splay back outside the silhouette near the base.

Detail loss at the smaller skull size is expected; silhouette
(cranium dome + two eye sockets + jaw notch) carries the read.
"""
from __future__ import annotations

import math
import os
import sys

# WHY headless: tool must render in CI / sandbox with no display server.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame


# Layout
PANEL_W, PANEL_H = 420, 280
COLS, ROWS       = 2, 2
TITLE_H          = 64
GUTTER           = 14
SHEET_W          = PANEL_W * COLS + GUTTER * (COLS + 1)
SHEET_H          = TITLE_H + (PANEL_H + GUTTER) * ROWS + GUTTER

DAWN_TEAL        = (38, 44, 66)
INK              = (235, 240, 250)
DIM              = (150, 158, 178)
PANEL_BG         = (24, 28, 42)
GRID             = (54, 62, 86)

NATIVE_PX        = 48
SS               = 5
ZOOM_FACTOR      = 4


# Palette — kit-matched to Round 3/4 vial
BLACK_DOME    = (10, 10, 18)
GREEN_TOX     = (120, 200,  90)
GREEN_LO      = (40,  100,  50)
GREEN_GLASS   = (35, 90, 50)
VAPOR_HI      = (200, 224,  96)
WOOD_DARK     = (60,  38,  22)
# Aged off-white bone — deliberately darker / warmer than SKATEBOARD's
# helmet cream (240,240,230) so the two pickups don't twin in palette.
BONE          = (220, 215, 200)
BONE_SHADE    = (175, 168, 150)
BONE_OUTLINE  = (20,  16,  22)
SOCKET        = (18,  14,  24)


# Helpers
def _ss_canvas(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _resolve(big: pygame.Surface, w: int, h: int) -> pygame.Surface:
    return pygame.transform.smoothscale(big, (w, h))


def _radial_glow(radius: int, color, max_alpha: int = 160) -> pygame.Surface:
    d = radius * 2 + 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    cx = d // 2
    for r in range(radius, 0, -1):
        t = r / radius
        a = int(max_alpha * (1 - t) ** 1.6)
        pygame.draw.circle(g, (*color, a), (cx, cx), r)
    return g


def _warning_glow_blit(surf, cx, cy, pulse_phase,
                       color=(235, 35, 45),
                       core_alpha=190, core_r=14, halo_r=19,
                       outer_alpha=95):
    breath = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse_phase))
    outer = _radial_glow(halo_r, color, max_alpha=int(outer_alpha * breath))
    surf.blit(outer, (cx - outer.get_width() // 2,
                      cy - outer.get_height() // 2))
    inner = _radial_glow(core_r, color, max_alpha=int(core_alpha * breath))
    surf.blit(inner, (cx - inner.get_width() // 2,
                      cy - inner.get_height() // 2))


# Flask body — Round 3/4 panel 4, untouched except the label budget
# shrinks and recentres so the glyph fits inside the conical glass.
def _draw_flask_body(big, cx, cy, pulse, paint_label):
    """Erlenmeyer body, liquid, neck, cork. Calls back to paint_label
    with (big, label_cx, label_cy, label_h, label_w) so the four
    variants reuse the SAME flask under the SAME conditions."""
    base_y     = cy + 16 * SS
    shoulder_y = cy - 2 * SS
    neck_top_y = shoulder_y - 6 * SS
    base_half  = 14 * SS
    shoulder_half = 4 * SS

    # Conical body outline + interior
    body_pts = [
        (cx - shoulder_half, shoulder_y),
        (cx - base_half,     base_y - 2 * SS),
        (cx - base_half + 2 * SS, base_y),
        (cx + base_half - 2 * SS, base_y),
        (cx + base_half,     base_y - 2 * SS),
        (cx + shoulder_half, shoulder_y),
    ]
    pygame.draw.polygon(big, BLACK_DOME, body_pts)
    inner_pts = [
        (cx - shoulder_half + SS, shoulder_y + SS),
        (cx - base_half + SS,     base_y - 3 * SS),
        (cx - base_half + 3 * SS, base_y - SS),
        (cx + base_half - 3 * SS, base_y - SS),
        (cx + base_half - SS,     base_y - 3 * SS),
        (cx + shoulder_half - SS, shoulder_y + SS),
    ]
    pygame.draw.polygon(big, GREEN_GLASS, inner_pts)

    # Liquid fill with wavy meniscus
    fill_top_y = shoulder_y + 7 * SS
    t_fill = (fill_top_y - shoulder_y) / (base_y - shoulder_y)
    fill_left_x  = cx - int(shoulder_half + (base_half - shoulder_half) * t_fill) + SS
    fill_right_x = cx + int(shoulder_half + (base_half - shoulder_half) * t_fill) - SS
    meniscus = []
    for i in range(15):
        t = i / 14
        mx = int(fill_left_x + (fill_right_x - fill_left_x) * t)
        wave = math.sin(pulse * 2.2 + i * 0.9) * (SS // 2 + 1)
        meniscus.append((mx, fill_top_y + int(wave)))
    liquid_pts = (
        meniscus
        + [(cx + base_half - SS,     base_y - 3 * SS),
           (cx + base_half - 3 * SS, base_y - SS),
           (cx - base_half + 3 * SS, base_y - SS),
           (cx - base_half + SS,     base_y - 3 * SS)]
    )
    pygame.draw.polygon(big, GREEN_LO, liquid_pts)
    pygame.draw.lines(big, GREEN_TOX, False, meniscus, max(1, SS // 2 + 1))
    band_pts = [(p[0], p[1] + 3 * SS) for p in meniscus]
    pygame.draw.lines(big, (90, 160, 70), False, band_pts, max(1, SS // 2))

    # Bubbles
    for i, (bx_off, by_off, br) in enumerate(((-4, 5, 2),
                                              (3, 8, 1),
                                              (-1, 11, 1))):
        drift = math.sin(pulse * 1.6 + i * 1.7) * SS
        pygame.draw.circle(big, (180, 240, 180, 220),
                           (cx + bx_off * SS,
                            fill_top_y + by_off * SS + int(drift)),
                           br * SS)

    # Glass rim highlight
    pygame.draw.line(big, (90, 170, 110),
                     (cx - shoulder_half + SS, shoulder_y + 2 * SS),
                     (cx - base_half + 2 * SS, base_y - 3 * SS),
                     max(1, SS // 2 + 1))

    # Neck
    neck_rect = pygame.Rect(cx - 4 * SS, neck_top_y + SS,
                            8 * SS, shoulder_y - neck_top_y)
    pygame.draw.rect(big, BLACK_DOME, neck_rect)
    pygame.draw.rect(big, (30, 60, 40),
                     neck_rect.inflate(-2 * SS, 0))
    pygame.draw.line(big, (90, 170, 110),
                     (neck_rect.left + SS, neck_rect.top + SS),
                     (neck_rect.left + SS, neck_rect.bottom - SS),
                     max(1, SS // 2))

    # Cork
    cork_rect = pygame.Rect(cx - 5 * SS, neck_top_y - 4 * SS,
                            10 * SS, 5 * SS)
    pygame.draw.rect(big, WOOD_DARK, cork_rect, border_radius=SS)
    pygame.draw.rect(big, (170, 110, 60),
                     cork_rect.inflate(-2 * SS, -SS), border_radius=SS)
    pygame.draw.line(big, (220, 170, 110),
                     (cork_rect.left + 2 * SS, cork_rect.top + SS),
                     (cork_rect.right - 2 * SS, cork_rect.top + SS),
                     max(1, SS // 2))

    # === Hand off to label painter ====================================
    # Round-5 containment: shrink the glyph ~38% and bias it upward so
    # the bone tips clear the inner green wall on every variant. The
    # cone narrows toward the top — a small upward bias keeps the bones
    # away from the wider base diagonal that previously clipped them.
    label_cx = cx
    label_cy = (fill_top_y + base_y) // 2 - 2 * SS    # bias upward
    label_h  = 8 * SS          # was 13 * SS  -> ~38% smaller
    label_w  = 10 * SS         # was 16 * SS  -> ~38% smaller
    paint_label(big, label_cx, label_cy, label_h, label_w)

    # === Vapour puffs — sickly yellow-green ==========================
    puffs = (
        (-1, -10, 4, 170),
        (2,  -16, 5, 130),
        (-2, -22, 6, 85),
    )
    for i, (dx, dy, r, a) in enumerate(puffs):
        drift = math.sin(pulse * 1.0 + i * 0.7) * SS
        pw = pygame.Surface((r * 2 * SS + 2, r * 2 * SS + 2),
                            pygame.SRCALPHA)
        pygame.draw.circle(pw, (*VAPOR_HI, a),
                           (r * SS + 1, r * SS + 1), r * SS)
        if i < 2:
            pygame.draw.circle(pw, (230, 240, 150,
                                    min(255, a + 50)),
                               (r * SS + 1 - SS, r * SS + 1 - SS),
                               max(1, r * SS - 2 * SS))
        big.blit(pw, (cx + dx * SS + int(drift) - r * SS - 1,
                      cork_rect.top + dy * SS - r * SS - 1))


# === Shared crossbone primitives =====================================
def _cyl_femur(big, p0, p1, thickness, knob_r,
               body_col=BONE, shade_col=BONE_SHADE, outline=BONE_OUTLINE):
    """Straight tapered femur — outline-thick rectangle along p0->p1 with
    a rounded epiphysis knob at each end. Two-tone fill so the bone
    survives at 48 px without going flat."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L           # perpendicular unit
    # Outline polygon — slightly fatter than the fill so it ringed
    quad_out = [
        (p0[0] + nx * (thickness + SS), p0[1] + ny * (thickness + SS)),
        (p1[0] + nx * (thickness + SS), p1[1] + ny * (thickness + SS)),
        (p1[0] - nx * (thickness + SS), p1[1] - ny * (thickness + SS)),
        (p0[0] - nx * (thickness + SS), p0[1] - ny * (thickness + SS)),
    ]
    pygame.draw.polygon(big, outline,
                        [(int(p[0]), int(p[1])) for p in quad_out])

    # Knob outlines
    pygame.draw.circle(big, outline,
                       (int(p0[0]), int(p0[1])), int(knob_r + SS))
    pygame.draw.circle(big, outline,
                       (int(p1[0]), int(p1[1])), int(knob_r + SS))

    # Body fill
    quad = [
        (p0[0] + nx * thickness, p0[1] + ny * thickness),
        (p1[0] + nx * thickness, p1[1] + ny * thickness),
        (p1[0] - nx * thickness, p1[1] - ny * thickness),
        (p0[0] - nx * thickness, p0[1] - ny * thickness),
    ]
    pygame.draw.polygon(big, body_col,
                        [(int(p[0]), int(p[1])) for p in quad])
    pygame.draw.circle(big, body_col,
                       (int(p0[0]), int(p0[1])), int(knob_r))
    pygame.draw.circle(big, body_col,
                       (int(p1[0]), int(p1[1])), int(knob_r))

    # Shade band along bottom side of shaft for roundness
    shade_quad = [
        (p0[0] - nx * (thickness * 0.2), p0[1] - ny * (thickness * 0.2)),
        (p1[0] - nx * (thickness * 0.2), p1[1] - ny * (thickness * 0.2)),
        (p1[0] - nx * thickness * 0.9,   p1[1] - ny * thickness * 0.9),
        (p0[0] - nx * thickness * 0.9,   p0[1] - ny * thickness * 0.9),
    ]
    pygame.draw.polygon(big, shade_col,
                        [(int(p[0]), int(p[1])) for p in shade_quad])

    # 1-px highlight along top edge for cylinder cue
    pygame.draw.line(big, (240, 235, 225),
                     (int(p0[0] + nx * thickness * 0.55),
                      int(p0[1] + ny * thickness * 0.55)),
                     (int(p1[0] + nx * thickness * 0.55),
                      int(p1[1] + ny * thickness * 0.55)),
                     max(1, SS // 2))


def _crossed_bones(big, cx, cy, length, thickness, knob_r,
                   angle_a=math.radians(35),
                   angle_b=math.radians(-35)):
    """Two femurs crossing through (cx, cy). Drawn BEHIND the skull —
    caller paints the skull on top to occlude the crossing knot. Default
    angles give the universal +-35deg X pattern."""
    for ang in (angle_a, angle_b):
        cosA, sinA = math.cos(ang), math.sin(ang)
        p0 = (cx - cosA * length, cy - sinA * length)
        p1 = (cx + cosA * length, cy + sinA * length)
        _cyl_femur(big, p0, p1, thickness, knob_r)


# === Variant A — Classic poison label ================================
def _label_classic(big, cx, cy, label_h, label_w):
    """Universal pictogram: round-cranium skull, square jaw, two simple
    eye sockets, NO nose. Straight crossed femurs behind. The reference
    against which the others are tuned. Bone metrics scale down with
    the shrunk budget so the shaft thickness still reads at 48 px."""
    bone_len   = int(label_w * 0.55)
    bone_thick = max(2, int(SS * 0.95))      # was 1.4 * SS
    knob_r     = max(2, int(SS * 1.25))      # was 1.9 * SS
    _crossed_bones(big, cx, cy + int(SS * 1.2), bone_len, bone_thick, knob_r,
                   angle_a=math.radians(32),
                   angle_b=math.radians(-32))

    # Skull cranium
    skull_r = max(3, int(label_h * 0.36))
    pygame.draw.circle(big, BONE_OUTLINE, (cx, cy - SS), skull_r + SS // 2 + 1)
    pygame.draw.circle(big, BONE,         (cx, cy - SS), skull_r)
    # Subtle shade on the lower-right
    shade = pygame.Surface((skull_r * 2 + 4, skull_r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(shade, (*BONE_SHADE, 130),
                       (skull_r + 2 + SS // 2, skull_r + 2 + SS // 2),
                       max(1, skull_r - SS // 2))
    big.blit(shade, (cx - skull_r - 2, cy - SS - skull_r - 2))

    # Square jaw block — slightly narrower than cranium
    jaw_w = max(3, int(skull_r * 1.15))
    jaw_h = max(2, int(skull_r * 0.55))
    jaw_rect = pygame.Rect(cx - jaw_w // 2, cy + skull_r - SS,
                           jaw_w, jaw_h)
    pygame.draw.rect(big, BONE_OUTLINE,
                     jaw_rect.inflate(SS, SS),
                     border_radius=max(1, SS))
    pygame.draw.rect(big, BONE, jaw_rect, border_radius=max(1, SS // 2))
    # Center jaw notch — single tooth slit
    pygame.draw.line(big, BONE_OUTLINE,
                     (cx, jaw_rect.top + 1),
                     (cx, jaw_rect.bottom - 1),
                     max(1, SS // 2))

    # Eye sockets — two simple dark circles, no nose
    eye_r = max(2, int(skull_r * 0.42))
    eye_y = cy - SS
    eye_dx = max(2, int(skull_r * 0.50))
    pygame.draw.circle(big, SOCKET, (cx - eye_dx, eye_y), eye_r)
    pygame.draw.circle(big, SOCKET, (cx + eye_dx, eye_y), eye_r)


# === Variant B — Cartoon menace ======================================
def _label_cartoon(big, cx, cy, label_h, label_w):
    """Skybit-friendly cartoon take: rounder skull, BIGGER sockets, a
    tiny triangular nose, crossed bones with rounded ends. At the new
    smaller size the nose collapses to a single dark dot — that's
    intentional, the eye sockets carry the read."""
    bone_len   = int(label_w * 0.56)
    bone_thick = max(2, int(SS * 1.05))
    knob_r     = max(2, int(SS * 1.4))
    _crossed_bones(big, cx, cy + int(SS * 1.2), bone_len, bone_thick, knob_r,
                   angle_a=math.radians(30),
                   angle_b=math.radians(-30))

    # Skull cranium — slightly oval (taller) for roundness
    skull_w = max(4, int(label_h * 0.82))
    skull_h = max(4, int(label_h * 0.76))
    cranium = pygame.Rect(0, 0, skull_w, skull_h)
    cranium.center = (cx, cy - SS)
    pygame.draw.ellipse(big, BONE_OUTLINE, cranium.inflate(SS, SS))
    pygame.draw.ellipse(big, BONE, cranium)
    # Shade
    shade = pygame.Surface(cranium.size, pygame.SRCALPHA)
    pygame.draw.ellipse(shade, (*BONE_SHADE, 110),
                        pygame.Rect(SS // 2, SS // 2,
                                    max(1, cranium.width - SS),
                                    max(1, cranium.height - SS)))
    big.blit(shade, cranium.topleft)

    # Rounded jaw (NOT square — softer)
    jaw_w = max(3, int(skull_w * 0.72))
    jaw_h = max(2, int(skull_h * 0.40))
    jaw_rect = pygame.Rect(cx - jaw_w // 2,
                           cranium.bottom - SS, jaw_w, jaw_h)
    pygame.draw.ellipse(big, BONE_OUTLINE, jaw_rect.inflate(SS, SS))
    pygame.draw.ellipse(big, BONE, jaw_rect)

    # Bigger sockets
    eye_r = max(2, int(skull_w * 0.24))
    eye_y = cy - SS
    eye_dx = max(2, int(skull_w * 0.24))
    pygame.draw.circle(big, SOCKET, (cx - eye_dx, eye_y), eye_r)
    pygame.draw.circle(big, SOCKET, (cx + eye_dx, eye_y), eye_r)

    # Tiny dot nose — at this scale a triangle becomes mush
    pygame.draw.circle(big, SOCKET,
                       (cx, cy + int(SS * 1.3)),
                       max(1, SS // 2 + 1))


# === Variant C — Stark minimalist ====================================
def _label_minimalist(big, cx, cy, label_h, label_w):
    """Highest legibility at 48 px: rounded-square skull, two circle
    sockets, NO nose, NO teeth. Bones reduced to two thick rectangle
    slabs in an X. Lives or dies on silhouette."""
    bone_len   = int(label_w * 0.55)
    bone_thick = max(2, int(SS * 1.2))         # fatter slabs
    knob_r     = max(2, int(SS * 1.0))         # minimal knobs
    for ang in (math.radians(34), math.radians(-34)):
        cosA, sinA = math.cos(ang), math.sin(ang)
        p0 = (cx - cosA * bone_len, cy + int(SS * 1.0) - sinA * bone_len)
        p1 = (cx + cosA * bone_len, cy + int(SS * 1.0) + sinA * bone_len)
        _cyl_femur(big, p0, p1, bone_thick, knob_r)

    # Rounded-square cranium — corner radius small enough that it reads
    # geometric, not blob-skull.
    crm_w = max(4, int(label_h * 0.78))
    crm_h = max(4, int(label_h * 0.70))
    crm = pygame.Rect(0, 0, crm_w, crm_h)
    crm.center = (cx, cy - SS)
    pygame.draw.rect(big, BONE_OUTLINE,
                     crm.inflate(SS, SS),
                     border_radius=max(1, int(SS * 1.2)))
    pygame.draw.rect(big, BONE, crm, border_radius=max(1, SS))

    # Single-pixel shade band across bottom
    shade_band = pygame.Rect(crm.left + SS // 2, crm.bottom - 2 * SS,
                             max(1, crm.width - SS), max(1, SS))
    sb = pygame.Surface(shade_band.size, pygame.SRCALPHA)
    pygame.draw.rect(sb, (*BONE_SHADE, 140),
                     pygame.Rect(0, 0, *shade_band.size),
                     border_radius=max(1, SS // 2))
    big.blit(sb, shade_band.topleft)

    # Square jaw — narrower notch under the cranium
    jw = max(3, int(crm_w * 0.58))
    jh = max(2, int(crm_h * 0.30))
    jaw = pygame.Rect(0, 0, jw, jh)
    jaw.midtop = (cx, crm.bottom - SS // 2)
    pygame.draw.rect(big, BONE_OUTLINE, jaw.inflate(SS, SS),
                     border_radius=max(1, SS // 2))
    pygame.draw.rect(big, BONE, jaw, border_radius=max(1, SS // 2))

    # Two big circle sockets
    eye_r = max(2, int(crm_w * 0.24))
    eye_y = cy - SS
    eye_dx = max(2, int(crm_w * 0.26))
    pygame.draw.circle(big, SOCKET, (cx - eye_dx, eye_y), eye_r)
    pygame.draw.circle(big, SOCKET, (cx + eye_dx, eye_y), eye_r)


# === Variant D — Tilted dynamic ======================================
def _label_tilted(big, cx, cy, label_h, label_w):
    """~10 deg clockwise tilt on the skull, off-90 bone angles, slight
    grin. Paint everything on a separate SRCALPHA buffer then rotozoom
    so the tilt is clean. Buffer is sized to the SHRUNK glyph budget so
    rotation doesn't push the bones outside the cone."""
    buf_w = label_w + 4 * SS
    buf_h = label_h + 4 * SS
    buf = pygame.Surface((buf_w, buf_h), pygame.SRCALPHA)
    bx, by = buf_w // 2, buf_h // 2

    # Bones at off-90 angles (40 and -28) — slightly shorter than the
    # other variants so the 10deg rotation doesn't punch out the sides.
    bone_len   = int(label_w * 0.50)
    bone_thick = max(2, int(SS * 1.0))
    knob_r     = max(2, int(SS * 1.25))
    _crossed_bones(buf, bx, by + int(SS * 1.2),
                   bone_len, bone_thick, knob_r,
                   angle_a=math.radians(40),
                   angle_b=math.radians(-26))

    # Skull cranium — slightly oval
    skull_w = max(4, int(label_h * 0.80))
    skull_h = max(4, int(label_h * 0.74))
    cranium = pygame.Rect(0, 0, skull_w, skull_h)
    cranium.center = (bx, by - SS)
    pygame.draw.ellipse(buf, BONE_OUTLINE, cranium.inflate(SS, SS))
    pygame.draw.ellipse(buf, BONE, cranium)
    shade = pygame.Surface(cranium.size, pygame.SRCALPHA)
    pygame.draw.ellipse(shade, (*BONE_SHADE, 130),
                        pygame.Rect(SS // 2, SS // 2,
                                    max(1, cranium.width - SS),
                                    max(1, cranium.height - SS)))
    buf.blit(shade, cranium.topleft)

    # Jaw
    jaw_w = max(3, int(skull_w * 0.72))
    jaw_h = max(2, int(skull_h * 0.38))
    jaw_rect = pygame.Rect(bx - jaw_w // 2,
                           cranium.bottom - SS, jaw_w, jaw_h)
    pygame.draw.ellipse(buf, BONE_OUTLINE, jaw_rect.inflate(SS, SS))
    pygame.draw.ellipse(buf, BONE, jaw_rect)

    # Eyes — slightly asymmetric (right eye a touch lower) for personality
    eye_r = max(2, int(skull_w * 0.22))
    eye_y = by - SS
    eye_dx = max(2, int(skull_w * 0.24))
    pygame.draw.circle(buf, SOCKET, (bx - eye_dx, eye_y), eye_r)
    pygame.draw.circle(buf, SOCKET, (bx + eye_dx, eye_y + SS // 2), eye_r)

    # Tiny dot nose (triangle at this scale collapses)
    pygame.draw.circle(buf, SOCKET,
                       (bx, by + int(SS * 1.3)),
                       max(1, SS // 2 + 1))

    # Rotate the whole label buffer 10 deg clockwise
    rotated = pygame.transform.rotate(buf, -10.0)
    big.blit(rotated, (cx - rotated.get_width() // 2,
                       cy - rotated.get_height() // 2))


# === Variant draw entry points =======================================
def _make_variant(label_fn):
    """Returns a function (out_size, pulse) -> Surface that draws the
    shared erlenmeyer with the given label painter."""
    def _draw(out_size, pulse):
        surf = pygame.Surface((out_size, out_size), pygame.SRCALPHA)
        # Round-3 halo numbers for the vial (green absorbs red — boosted)
        _warning_glow_blit(surf, out_size // 2, out_size // 2 + 4, pulse,
                           color=(235, 50, 50),
                           core_alpha=190, core_r=14, halo_r=19,
                           outer_alpha=95)
        big = _ss_canvas(out_size, out_size)
        cx = out_size * SS // 2
        cy = out_size * SS // 2 + 4 * SS
        _draw_flask_body(big, cx, cy, pulse, label_fn)
        surf.blit(_resolve(big, out_size, out_size), (0, 0))
        return surf
    return _draw


VARIANTS = [
    ("A",  "CLASSIC",      "universal pictogram | round cranium, square jaw, no nose",
     _make_variant(_label_classic)),
    ("B",  "CARTOON",      "rounder skull + bigger sockets + dot nose | Skybit-leaning",
     _make_variant(_label_cartoon)),
    ("C",  "MINIMALIST",   "rounded-square skull, slab bones | highest 48-px read",
     _make_variant(_label_minimalist)),
    ("D",  "TILTED",       "skull tilted ~10 deg, off-90 bones",
     _make_variant(_label_tilted)),
]


# === Sheet composition ===============================================
def _panel_bg(surf, rect):
    pygame.draw.rect(surf, PANEL_BG, rect, border_radius=10)
    pygame.draw.rect(surf, GRID, rect, width=1, border_radius=10)


def _draw_label(surf, text, x, y, font, color=INK):
    surf.blit(font.render(text, True, color), (x, y))


def build_sheet():
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(DAWN_TEAL)

    font_title = pygame.font.SysFont("dejavusansmono", 22, bold=True)
    font_h     = pygame.font.SysFont("dejavusans", 16, bold=True)
    font_s     = pygame.font.SysFont("dejavusans", 12)
    font_xs    = pygame.font.SysFont("dejavusans", 10)

    _draw_label(sheet,
                "POISON VIAL  —  skull contained inside flask outline, 4 variants",
                16, 12, font_title)
    _draw_label(sheet,
                "Round-5: glyph ~38% smaller + biased upward so bone tips clear the "
                "inner green wall on every variant. Bottle is the outermost shape.",
                16, 40, font_s, color=DIM)

    base_pulse = {
        "A": 0.5,
        "B": 1.1,
        "C": 1.8,
        "D": 2.5,
    }

    for i, (tag, name, blurb, fn) in enumerate(VARIANTS):
        col = i % COLS
        row = i // COLS
        panel_x = GUTTER + col * (PANEL_W + GUTTER)
        panel_y = TITLE_H + row * (PANEL_H + GUTTER) + GUTTER
        rect = pygame.Rect(panel_x, panel_y, PANEL_W, PANEL_H)
        _panel_bg(sheet, rect)

        _draw_label(sheet, f"{tag}.  {name}",
                    rect.left + 14, rect.top + 10, font_h)
        _draw_label(sheet, blurb,
                    rect.left + 14, rect.top + 30, font_s, color=DIM)

        # Left: at-size 48 px with idle bob
        icon = fn(NATIVE_PX, base_pulse[tag])
        bob = int(math.sin(base_pulse[tag] * 1.0) * 2)
        left_cx = rect.left + 78
        left_cy = rect.top + rect.height // 2 + 18 + bob
        swatch = pygame.Surface((92, 92), pygame.SRCALPHA)
        pygame.draw.circle(swatch, DAWN_TEAL, (46, 46), 46)
        pygame.draw.circle(swatch, (28, 32, 50), (46, 46), 46, 2)
        sheet.blit(swatch, (left_cx - 46, left_cy - 46))
        sheet.blit(icon, (left_cx - icon.get_width() // 2,
                          left_cy - icon.get_height() // 2))
        _draw_label(sheet, "in-world  48 px", left_cx - 38,
                    rect.bottom - 22, font_xs, color=DIM)

        # Right: 4x zoom
        zoomed = pygame.transform.scale(
            icon,
            (NATIVE_PX * ZOOM_FACTOR, NATIVE_PX * ZOOM_FACTOR),
        )
        right_cx = rect.right - 116
        right_cy = rect.top + rect.height // 2 + 16
        z_rect = pygame.Rect(0, 0, NATIVE_PX * ZOOM_FACTOR + 16,
                             NATIVE_PX * ZOOM_FACTOR + 16)
        z_rect.center = (right_cx, right_cy)
        pygame.draw.rect(sheet, (18, 22, 34), z_rect, border_radius=6)
        pygame.draw.rect(sheet, GRID, z_rect, width=1, border_radius=6)
        sheet.blit(zoomed, (right_cx - zoomed.get_width() // 2,
                            right_cy - zoomed.get_height() // 2))
        _draw_label(sheet, "4x zoom",
                    z_rect.left + 6, z_rect.bottom + 4, font_xs, color=DIM)

    footer = ("Round-5 fix: skull-and-crossbones fully INSIDE the conical glass | "
              "bottle silhouette is the outermost shape on every variant")
    foot_s = font_xs.render(footer, True, DIM)
    sheet.blit(foot_s, (GUTTER + 4, SHEET_H - 16))

    return sheet


def main():
    pygame.init()
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "death_pickup")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    sheet = build_sheet()
    out_path = os.path.join(out_dir, "round_5_vial_skull_contained.png")
    pygame.image.save(sheet, out_path)
    print(out_path)


if __name__ == "__main__":
    main()
    sys.exit(0)
