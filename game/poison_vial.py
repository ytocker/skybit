"""Poison vial pickup sprite.

Variant A (CLASSIC) from `tools/render_death_trap_round_7_A_final.py`:
erlenmeyer flask, sickly green liquid, skull-and-crossbones label sitting
INSIDE the cone, vapor puffs above the cork, warning halo recoloured to
vapor yellow-green so halo + vapor + bone palette stay coherent.

The flask + label + bones are expensive to redraw (supersampled at 5x
then smoothscaled), so they're cached once at module load. The breathing
warning halo is cheap and drawn live each frame around the cached sprite.
"""
from __future__ import annotations

import math

import pygame


NATIVE_PX = 48
# In-world pickup display size after the final smoothscale — picked
# to match the SKATEBOARD / KNIGHT / GENIE icons so all four pickups
# read at the same visual weight.
DISPLAY_PX = 56
SS        = 5

# Kit-matched palette (from round 5/7 design)
BLACK_DOME   = (28, 42, 30)
GREEN_TOX    = (185, 225, 140)
GREEN_LO     = (160, 215, 125)
GREEN_GLASS  = (130, 195, 110)
# Vapor + warning aura share the liquid colour so the bubbles above
# the cork and the breathing halo behind the bottle both read as the
# same neon green the player sees inside the glass.
VAPOR_HI     = (160, 215, 125)
WOOD_DARK    = (60,  38,   22)
# Aged off-white bone — deliberately darker / warmer than SKATEBOARD's
# helmet cream so the two pickups don't twin in palette.
BONE         = (220, 215, 200)
BONE_SHADE   = (175, 168, 150)
BONE_OUTLINE = (20,  16,   22)
SOCKET       = (18,  14,   24)


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
                       color=VAPOR_HI,
                       core_alpha=230, core_r=19, halo_r=27,
                       outer_alpha=140):
    breath = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(pulse_phase))
    outer = _radial_glow(halo_r, color, max_alpha=int(outer_alpha * breath))
    surf.blit(outer, (cx - outer.get_width() // 2,
                      cy - outer.get_height() // 2))
    inner = _radial_glow(core_r, color, max_alpha=int(core_alpha * breath))
    surf.blit(inner, (cx - inner.get_width() // 2,
                      cy - inner.get_height() // 2))


def _cyl_femur(big, p0, p1, thickness, knob_r):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    quad_out = [
        (p0[0] + nx * (thickness + SS), p0[1] + ny * (thickness + SS)),
        (p1[0] + nx * (thickness + SS), p1[1] + ny * (thickness + SS)),
        (p1[0] - nx * (thickness + SS), p1[1] - ny * (thickness + SS)),
        (p0[0] - nx * (thickness + SS), p0[1] - ny * (thickness + SS)),
    ]
    pygame.draw.polygon(big, BONE_OUTLINE,
                        [(int(p[0]), int(p[1])) for p in quad_out])
    pygame.draw.circle(big, BONE_OUTLINE,
                       (int(p0[0]), int(p0[1])), int(knob_r + SS))
    pygame.draw.circle(big, BONE_OUTLINE,
                       (int(p1[0]), int(p1[1])), int(knob_r + SS))

    quad = [
        (p0[0] + nx * thickness, p0[1] + ny * thickness),
        (p1[0] + nx * thickness, p1[1] + ny * thickness),
        (p1[0] - nx * thickness, p1[1] - ny * thickness),
        (p0[0] - nx * thickness, p0[1] - ny * thickness),
    ]
    pygame.draw.polygon(big, BONE,
                        [(int(p[0]), int(p[1])) for p in quad])
    pygame.draw.circle(big, BONE,
                       (int(p0[0]), int(p0[1])), int(knob_r))
    pygame.draw.circle(big, BONE,
                       (int(p1[0]), int(p1[1])), int(knob_r))

    shade_quad = [
        (p0[0] - nx * (thickness * 0.2), p0[1] - ny * (thickness * 0.2)),
        (p1[0] - nx * (thickness * 0.2), p1[1] - ny * (thickness * 0.2)),
        (p1[0] - nx * thickness * 0.9,   p1[1] - ny * thickness * 0.9),
        (p0[0] - nx * thickness * 0.9,   p0[1] - ny * thickness * 0.9),
    ]
    pygame.draw.polygon(big, BONE_SHADE,
                        [(int(p[0]), int(p[1])) for p in shade_quad])
    pygame.draw.line(big, (240, 235, 225),
                     (int(p0[0] + nx * thickness * 0.55),
                      int(p0[1] + ny * thickness * 0.55)),
                     (int(p1[0] + nx * thickness * 0.55),
                      int(p1[1] + ny * thickness * 0.55)),
                     max(1, SS // 2))


def _crossed_bones(big, cx, cy, length, thickness, knob_r):
    for ang in (math.radians(32), math.radians(-32)):
        cosA, sinA = math.cos(ang), math.sin(ang)
        p0 = (cx - cosA * length, cy - sinA * length)
        p1 = (cx + cosA * length, cy + sinA * length)
        _cyl_femur(big, p0, p1, thickness, knob_r)


def _label_classic(big, cx, cy, label_h, label_w):
    bone_len   = int(label_w * 0.55)
    bone_thick = max(2, int(SS * 0.95))
    knob_r     = max(2, int(SS * 1.25))
    _crossed_bones(big, cx, cy + int(SS * 1.2), bone_len, bone_thick, knob_r)

    skull_r = max(3, int(label_h * 0.36))
    pygame.draw.circle(big, BONE_OUTLINE, (cx, cy - SS), skull_r + SS // 2 + 1)
    pygame.draw.circle(big, BONE,         (cx, cy - SS), skull_r)
    shade = pygame.Surface((skull_r * 2 + 4, skull_r * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(shade, (*BONE_SHADE, 130),
                       (skull_r + 2 + SS // 2, skull_r + 2 + SS // 2),
                       max(1, skull_r - SS // 2))
    big.blit(shade, (cx - skull_r - 2, cy - SS - skull_r - 2))

    jaw_w = max(3, int(skull_r * 1.15))
    jaw_h = max(2, int(skull_r * 0.55))
    jaw_rect = pygame.Rect(cx - jaw_w // 2, cy + skull_r - SS,
                           jaw_w, jaw_h)
    pygame.draw.rect(big, BONE_OUTLINE,
                     jaw_rect.inflate(SS, SS),
                     border_radius=max(1, SS))
    pygame.draw.rect(big, BONE, jaw_rect, border_radius=max(1, SS // 2))
    pygame.draw.line(big, BONE_OUTLINE,
                     (cx, jaw_rect.top + 1),
                     (cx, jaw_rect.bottom - 1),
                     max(1, SS // 2))

    eye_r = max(2, int(skull_r * 0.42))
    eye_y = cy - SS
    eye_dx = max(2, int(skull_r * 0.50))
    pygame.draw.circle(big, SOCKET, (cx - eye_dx, eye_y), eye_r)
    pygame.draw.circle(big, SOCKET, (cx + eye_dx, eye_y), eye_r)


def _draw_flask_body(big, cx, cy, pulse):
    base_y     = cy + 16 * SS
    shoulder_y = cy - 2 * SS
    neck_top_y = shoulder_y - 6 * SS
    base_half  = 14 * SS
    shoulder_half = 4 * SS

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

    for i, (bx_off, by_off, br) in enumerate(((-4, 5, 2),
                                              (3, 8, 1),
                                              (-1, 11, 1))):
        drift = math.sin(pulse * 1.6 + i * 1.7) * SS
        pygame.draw.circle(big, (180, 240, 180, 220),
                           (cx + bx_off * SS,
                            fill_top_y + by_off * SS + int(drift)),
                           br * SS)

    pygame.draw.line(big, (90, 170, 110),
                     (cx - shoulder_half + SS, shoulder_y + 2 * SS),
                     (cx - base_half + 2 * SS, base_y - 3 * SS),
                     max(1, SS // 2 + 1))

    neck_rect = pygame.Rect(cx - 4 * SS, neck_top_y + SS,
                            8 * SS, shoulder_y - neck_top_y)
    pygame.draw.rect(big, BLACK_DOME, neck_rect)
    pygame.draw.rect(big, (30, 60, 40),
                     neck_rect.inflate(-2 * SS, 0))
    pygame.draw.line(big, (90, 170, 110),
                     (neck_rect.left + SS, neck_rect.top + SS),
                     (neck_rect.left + SS, neck_rect.bottom - SS),
                     max(1, SS // 2))

    cork_rect = pygame.Rect(cx - 5 * SS, neck_top_y - 4 * SS,
                            10 * SS, 5 * SS)
    pygame.draw.rect(big, WOOD_DARK, cork_rect, border_radius=SS)
    pygame.draw.rect(big, (170, 110, 60),
                     cork_rect.inflate(-2 * SS, -SS), border_radius=SS)
    pygame.draw.line(big, (220, 170, 110),
                     (cork_rect.left + 2 * SS, cork_rect.top + SS),
                     (cork_rect.right - 2 * SS, cork_rect.top + SS),
                     max(1, SS // 2))

    label_cx = cx
    label_cy = (fill_top_y + base_y) // 2 - 2 * SS
    label_h  = 8 * SS
    label_w  = 10 * SS
    _label_classic(big, label_cx, label_cy, label_h, label_w)

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
            pygame.draw.circle(pw, (200, 240, 170,
                                    min(255, a + 50)),
                               (r * SS + 1 - SS, r * SS + 1 - SS),
                               max(1, r * SS - 2 * SS))
        big.blit(pw, (cx + dx * SS + int(drift) - r * SS - 1,
                      cork_rect.top + dy * SS - r * SS - 1))


_VIAL_CACHE: pygame.Surface | None = None


def _build_vial_sprite() -> pygame.Surface:
    """Static flask + label + bones + vapor at pulse=0. Halo drawn live."""
    big = _ss_canvas(NATIVE_PX, NATIVE_PX)
    cx = NATIVE_PX * SS // 2
    cy = NATIVE_PX * SS // 2 + 4 * SS
    _draw_flask_body(big, cx, cy, pulse=0.0)
    return _resolve(big, DISPLAY_PX, DISPLAY_PX)


def get_vial_sprite() -> pygame.Surface:
    global _VIAL_CACHE
    if _VIAL_CACHE is None:
        _VIAL_CACHE = _build_vial_sprite()
    return _VIAL_CACHE


def draw(surf, cx, cy, pulse):
    """Render the poison vial centered on (cx, cy). Pulse drives the
    breathing warning halo only; flask interior is frozen at pulse=0."""
    _warning_glow_blit(surf, cx, cy + 4, pulse)
    sprite = get_vial_sprite()
    surf.blit(sprite, sprite.get_rect(center=(cx, cy)))
