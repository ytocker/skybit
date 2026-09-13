"""SKATEBOARD icon — face-scale comparison sheet.

Five variants of the live pickup icon, identical except for the
skull-bunny FACE scale factor (1.00 / 0.85 / 0.70 / 0.55 / 0.40).
The X-board backdrop stays at original size in every cell so only
the face shrinks. Each cell shows Pip + the icon at gameplay scale.

Output: docs/screenshots/icon_sizes/skateboard_face_variants.png
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game import parrot, biome


# ── palette + recipe constants ──────────────────────────────────────────────
DOME   = (10, 10, 18)
CHROME = (200, 200, 210)
BONE   = (240, 240, 230)
CREAM  = (245, 240, 230)
RED    = (200, 50, 50)

SS         = 6
AUTHORED_N = 96     # authored footprint of the icon recipe
DISPLAY_N  = 40     # what production shows on the playfield


def _draw_icon_with_face_scale(face_scale: float) -> pygame.Surface:
    """Port of PowerUp._draw_skateboard_icon with a face_scale factor
    applied to every face-layer dimension and offset. X boards stay
    at original scale. Returns a DISPLAY_N × DISPLAY_N native sprite."""
    big = pygame.Surface(
        (AUTHORED_N * SS, AUTHORED_N * SS), pygame.SRCALPHA)
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # ── X boards (BACKDROP — unscaled) ──────────────────────────────
    for angle in (35, -35):
        sub_w = 64 * SS
        sub_h = 9 * SS
        sub = pygame.Surface(
            (sub_w + 4 * SS, sub_h + 4 * SS), pygame.SRCALPHA)
        d = pygame.Rect(0, 0, sub_w, sub_h)
        d.center = (sub.get_width() // 2, sub.get_height() // 2)
        pygame.draw.rect(sub, CHROME, d, border_radius=2 * SS)
        pygame.draw.rect(sub, DOME,
                         d.inflate(-2 * SS, -2 * SS),
                         border_radius=SS)
        for sign in (-1, 1):
            wx = d.centerx + sign * (sub_w // 2 - 3 * SS)
            pygame.draw.circle(sub, CREAM, (wx, d.centery), int(3 * SS))
            pygame.draw.circle(sub, RED,   (wx, d.centery), int(1.4 * SS))
        rotated = pygame.transform.rotate(sub, angle)
        big.blit(rotated, rotated.get_rect(center=(bx, by)))

    # ── FACE block — every dimension and offset multiplied by face_scale ──
    fs = face_scale

    ear_w = max(1, int(7 * SS * fs))
    ear_h = max(1, int(28 * SS * fs))
    ear_dx = int(9 * SS * fs)
    ear_dy = int(22 * SS * fs)
    ear_outline_w = max(1, int(1.2 * SS * fs))
    ear_inner_shrink_w = int(2.5 * SS * fs)
    ear_inner_shrink_h = int(8 * SS * fs)
    ear_pad = max(1, int(4 * SS * fs))

    ear_centers = {}
    for sign in (-1, 1):
        er = pygame.Rect(0, 0, ear_w, ear_h)
        er.center = (bx + sign * ear_dx, by - ear_dy)
        ang = -12 * sign
        ear_sub = pygame.Surface(
            (er.width + ear_pad * 2, er.height + ear_pad * 2),
            pygame.SRCALPHA)
        local = pygame.Rect(0, 0, er.width, er.height)
        local.center = (ear_sub.get_width() // 2,
                        ear_sub.get_height() // 2)
        pygame.draw.ellipse(ear_sub, BONE, local)
        pygame.draw.ellipse(ear_sub, DOME, local, ear_outline_w)
        inner = local.inflate(-ear_inner_shrink_w, -ear_inner_shrink_h)
        pygame.draw.ellipse(ear_sub, RED, inner)
        rot = pygame.transform.rotate(ear_sub, ang)
        big.blit(rot, rot.get_rect(center=er.center))
        ear_centers[sign] = er.center

    SK_W = max(2, int(44 * fs))
    SK_H = max(2, int(38 * fs))
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by + int(2 * SS * fs))
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, max(1, int(1.4 * SS * fs)))

    eye_r = max(1, int(SK_W * SS * 0.13))
    eye_x_off = int(SK_W * SS * 0.20)
    eye_y = sk.top + int(SK_H * SS * 0.38)
    for sign in (-1, 1):
        ex = sk.centerx + sign * eye_x_off
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)

    cross_cx = sk.centerx - eye_x_off
    cross_cy = eye_y
    bar_l = max(2, int(7 * SS * fs))
    bar_t = max(1, int(2.2 * SS * fs))
    horiz = pygame.Rect(0, 0, bar_l, bar_t)
    horiz.center = (cross_cx, cross_cy)
    vert = pygame.Rect(0, 0, bar_t, bar_l)
    vert.center = (cross_cx, cross_cy)
    rad = max(1, int(0.5 * SS * fs))
    pygame.draw.rect(big, RED, horiz, border_radius=rad)
    pygame.draw.rect(big, RED, vert, border_radius=rad)
    pygame.draw.rect(big, DOME, horiz, max(1, SS // 3), border_radius=rad)
    pygame.draw.rect(big, DOME, vert, max(1, SS // 3), border_radius=rad)

    nose_top_y = sk.top + int(SK_H * SS * 0.55)
    nose_bot_y = nose_top_y + max(1, int(3 * SS * fs))
    nose_w = max(1, int(1.4 * SS * fs))
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - nose_w, nose_top_y),
        (sk.centerx + nose_w, nose_top_y),
        (sk.centerx,          nose_bot_y),
    ])

    mouth_scale = SK_W / 23.0
    mouth_stroke = max(1, int(1.2 * SS * mouth_scale))
    teeth_top = sk.bottom - int(7 * SS * mouth_scale)
    teeth_bot = sk.bottom - int(4 * SS * mouth_scale)
    divider_offsets = (-int(4 * SS * mouth_scale), 0,
                       int(4 * SS * mouth_scale))
    outer_shorten = max(1, int(1.0 * SS * mouth_scale))
    tooth_bottoms = []
    for idx, dx in enumerate(divider_offsets):
        top_y = teeth_top + (outer_shorten if idx != 1 else 0)
        pygame.draw.line(big, DOME,
                         (sk.centerx + dx, top_y),
                         (sk.centerx + dx, teeth_bot),
                         mouth_stroke)
        tooth_bottoms.append((sk.centerx + dx, teeth_bot))
    dip = max(2, int(1.6 * SS * mouth_scale))
    for (x0, y0), (x1, y1) in zip(tooth_bottoms, tooth_bottoms[1:]):
        pts = []
        for i in range(15):
            t = i / 14
            x = x0 + (x1 - x0) * t
            y_base = y0 + (y1 - y0) * t
            y = y_base + dip * math.sin(math.pi * t)
            pts.append((x, y))
        pygame.draw.lines(big, DOME, False, pts, mouth_stroke)

    knot_cx, knot_cy = ear_centers[-1]
    knot_cy = knot_cy + int(11 * SS * fs)
    knot_cx = knot_cx + int(3 * SS * fs)
    bow_w = max(1, int(5 * SS * fs))
    bow_h = max(1, int(3 * SS * fs))
    bow_left = [
        (knot_cx - bow_w,             knot_cy - bow_h),
        (knot_cx - int(0.5 * SS * fs), knot_cy),
        (knot_cx - bow_w,             knot_cy + bow_h),
    ]
    bow_right = [
        (knot_cx + bow_w,             knot_cy - bow_h),
        (knot_cx + int(0.5 * SS * fs), knot_cy),
        (knot_cx + bow_w,             knot_cy + bow_h),
    ]
    pygame.draw.polygon(big, RED, bow_left)
    pygame.draw.polygon(big, RED, bow_right)
    pygame.draw.circle(big, RED, (knot_cx, knot_cy),
                       max(1, int(1.5 * SS * fs)))
    pygame.draw.polygon(big, DOME, bow_left, max(1, SS // 3))
    pygame.draw.polygon(big, DOME, bow_right, max(1, SS // 3))

    icon = pygame.transform.smoothscale(big, (DISPLAY_N, DISPLAY_N))
    return icon


# ── sheet composition ──────────────────────────────────────────────────────

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)

VARIANTS = (
    ("F1", 1.00),
    ("F2", 0.85),
    ("F3", 0.70),
    ("F4", 0.55),
    ("F5", 0.40),
)

CELL_W = 200
CELL_H = 160
ZOOM   = 4
PAD    = 16


def _sky_strip(w, h):
    pal = biome.palette_for_phase(0.46)
    top = pal.get("sky_top", (110, 165, 220))
    bot = pal.get("sky_bot", (220, 200, 200))
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(surf, c, (0, y), (w - 1, y))
    return surf


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "skateboard_face_variants.png")

    sheet_w = PAD * 2 + len(VARIANTS) * (CELL_W + PAD) - PAD
    sheet_h = 64 + CELL_H + 80
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(20, bold=True).render(
        "SKATEBOARD icon — face-scale variants (X boards unchanged)",
        True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "Each cell shows Pip + the pickup at the live 40-px display "
        "footprint. Pick a face_scale.",
        True, SUB)
    sheet.blit(sub, (PAD, 38))

    pip = parrot.get_parrot(0, 0.0)

    for i, (code, fs) in enumerate(VARIANTS):
        x = PAD + i * (CELL_W + PAD)
        y = 64
        cell = _sky_strip(CELL_W, CELL_H)
        # Pip on the left
        cell.blit(pip, pip.get_rect(center=(46, CELL_H // 2)))
        # Icon at gameplay scale on the right
        icon = _draw_icon_with_face_scale(fs)
        cell.blit(icon, icon.get_rect(center=(CELL_W - 46, CELL_H // 2)))
        pygame.draw.rect(cell, (45, 50, 62), cell.get_rect(), 1)
        sheet.blit(cell, (x, y))
        cap = _font(14, bold=True).render(
            f"{code} — face_scale {fs:.2f}", True, LABEL)
        sheet.blit(cap, (x + (CELL_W - cap.get_width()) // 2,
                         y + CELL_H + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
