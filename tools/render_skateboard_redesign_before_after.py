"""Skateboard pickup redesign — original-mouth BEFORE/AFTER sheet (v3).

This v3 uses the ORIGINAL Jolly Roger mouth from the S4 "kit-matched"
icon (commit 1ed65ce, the pickup's very first design before any mouth
iteration): horizontal jaw bar at sk.bottom - 2*SS with 3 vertical
tooth-dividers at offsets -4*SS, 0, +4*SS spanning sk.bottom-5*SS to
sk.bottom-SS. That recipe was sized for the original SK_W=23 skull, so
we scale every metric proportional to each candidate's skull width.

Recipe (literal from entities.py at 1ed65ce):

    span_units = 12        # full mouth width
    tooth_h_units = 4      # vertical-divider height
    stroke = 1.2 * SS
    jaw_y = sk.bottom - 2 * SS
    teeth_top = sk.bottom - 5 * SS
    teeth_bot = sk.bottom - SS
    Mouth horizontal bar + 3 vertical dividers (-4*SS, 0, +4*SS), all
    DOME (BONE on inverted-contrast C / D).

BEFORE column = round-3 buck teeth (bit-identical to round_3.png).
AFTER  column = same candidate with the buck-teeth + per-candidate jaw
line replaced by the original Jolly Roger mouth, scaled to fit each
candidate's skull.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_skateboard_redesign_before_after.py
"""

import math
import os
import sys
import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_skateboard_redesign_round_3 as r3  # noqa: E402


PAL = r3.PAL
DOME, CHROME, BONE, CREAM, RED = (
    r3.DOME, r3.CHROME, r3.BONE, r3.CREAM, r3.RED,
)
CARD_BG = r3.CARD_BG
SHEET_BG = r3.SHEET_BG
LABEL = r3.LABEL
SUBLABEL = r3.SUBLABEL
NATIVE = r3.NATIVE
ZOOM = r3.ZOOM
SS = r3.SS


def _draw_jolly_roger_mouth(big, cx, sk_top, SK_H, SK_W, color=DOME,
                        sk_bottom=None):
    """Original S4 Jolly Roger mouth with the user's curly bottom:
    3 vertical tooth dividers, no straight jaw bar, plus a wavy curl
    line connecting the bottoms of adjacent teeth (each pair joined by
    a downward sine-arc dip). Metrics scale proportional to SK_W so the
    mouth occupies the same fractional skull width as the original
    (SK_W=23, dividers at -4 / 0 / +4 SS, height 4 SS)."""
    if sk_bottom is None:
        sk_bottom = sk_top + SK_H * SS
    scale = SK_W / 23.0
    stroke = max(1, int(1.2 * SS * scale))
    teeth_top = sk_bottom - int(7 * SS * scale)
    teeth_bot = sk_bottom - int(4 * SS * scale)
    divider_offsets = (-int(4 * SS * scale), 0, int(4 * SS * scale))
    outer_shorten = max(1, int(1.0 * SS * scale))
    tooth_bottoms = []
    for idx, dx in enumerate(divider_offsets):
        top_y = teeth_top + (outer_shorten if idx != 1 else 0)
        pygame.draw.line(big, color,
                         (cx + dx, top_y),
                         (cx + dx, teeth_bot),
                         stroke)
        tooth_bottoms.append((cx + dx, teeth_bot))
    dip = max(2, int(1.6 * SS * scale))
    segs_per_gap = 14
    for (x0, y0), (x1, y1) in zip(tooth_bottoms, tooth_bottoms[1:]):
        pts = []
        for i in range(segs_per_gap + 1):
            t = i / segs_per_gap
            x = x0 + (x1 - x0) * t
            y_base = y0 + (y1 - y0) * t
            y = y_base + dip * math.sin(math.pi * t)
            pts.append((x, y))
        pygame.draw.lines(big, color, False, pts, stroke)


# ---------------------------------------------------------------------------
# AFTER renderers — copy each round-3 candidate verbatim, drop the
# per-candidate jaw line + buck teeth, and draw the L2 Misfits mouth at
# the L2 fractional position. Everything else (ears, mohawk, spiked
# collar, RED bandage, patch, deck, pins) is identical.
# ---------------------------------------------------------------------------

def render_shipped_after():
    """Shipped baseline with the L2 Misfits mouth restored."""
    big = r3._supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2
    for angle in (35, -35):
        deck = r3._draw_deck(None, 46, 9, angle)
        big.blit(deck, deck.get_rect(center=(bx, by)))

    SK_W = 27
    SK_H = 22
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by - SS)
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.2 * SS))
    eye_r = int(SK_W * SS * 0.108)
    eye_x_off = int(SK_W * SS * 0.20)
    eye_y = sk.top + int(SK_H * SS * 0.36)
    for ex in (sk.centerx - eye_x_off, sk.centerx + eye_x_off):
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)
    nose_top_y = sk.top + int(SK_H * SS * 0.55)
    nose_bot_y = nose_top_y + int(2.5 * SS)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - SS, nose_top_y),
        (sk.centerx + SS, nose_top_y),
        (sk.centerx,      nose_bot_y),
    ])
    _draw_jolly_roger_mouth(big, sk.centerx, sk.top, SK_H, SK_W, color=DOME)
    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


def render_concept_a_after():
    """A with L2 Misfits mouth (no buck teeth, no plain-bar jaw line)."""
    big = r3._supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    ear_centers = {}
    for sign in (-1, 1):
        er = pygame.Rect(0, 0, int(7 * SS), int(28 * SS))
        er.center = (bx + sign * int(9 * SS), by - int(22 * SS))
        ang = -12 * sign
        ear_sub = pygame.Surface(
            (er.width + 4 * SS, er.height + 4 * SS), pygame.SRCALPHA)
        local = pygame.Rect(0, 0, er.width, er.height)
        local.center = (ear_sub.get_width() // 2, ear_sub.get_height() // 2)
        pygame.draw.ellipse(ear_sub, BONE, local)
        pygame.draw.ellipse(ear_sub, DOME, local, max(1, int(1.2 * SS)))
        inner = local.inflate(-int(2.5 * SS), -int(8 * SS))
        pygame.draw.ellipse(ear_sub, RED, inner)
        rot = pygame.transform.rotate(ear_sub, ang)
        rect = rot.get_rect(center=er.center)
        big.blit(rot, rect)
        ear_centers[sign] = er.center

    SK_W = 44
    SK_H = 38
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by + 2 * SS)
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.4 * SS))

    eye_r = int(SK_W * SS * 0.13)
    eye_x_off = int(SK_W * SS * 0.20)
    eye_y = sk.top + int(SK_H * SS * 0.38)
    for sign in (-1, 1):
        ex = sk.centerx + sign * eye_x_off
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)

    cross_cx = sk.centerx - eye_x_off
    cross_cy = eye_y
    bar_l = int(7 * SS)
    bar_t = int(2.2 * SS)
    horiz = pygame.Rect(0, 0, bar_l, bar_t)
    horiz.center = (cross_cx, cross_cy)
    vert = pygame.Rect(0, 0, bar_t, bar_l)
    vert.center = (cross_cx, cross_cy)
    pygame.draw.rect(big, RED, horiz, border_radius=int(0.5 * SS))
    pygame.draw.rect(big, RED, vert, border_radius=int(0.5 * SS))
    pygame.draw.rect(big, DOME, horiz, max(1, SS // 3),
                     border_radius=int(0.5 * SS))
    pygame.draw.rect(big, DOME, vert, max(1, SS // 3),
                     border_radius=int(0.5 * SS))

    nose_top_y = sk.top + int(SK_H * SS * 0.55)
    nose_bot_y = nose_top_y + int(3 * SS)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - int(1.4 * SS), nose_top_y),
        (sk.centerx + int(1.4 * SS), nose_top_y),
        (sk.centerx,                 nose_bot_y),
    ])

    # Jolly Roger mouth on the skull.
    _draw_jolly_roger_mouth(big, sk.centerx, sk.top, SK_H, SK_W, color=DOME)

    knot_cx, knot_cy = ear_centers[-1]
    knot_cy = knot_cy + int(11 * SS)
    knot_cx = knot_cx + int(3 * SS)
    bow_w = int(5 * SS)
    bow_h = int(3 * SS)
    pygame.draw.polygon(big, RED, [
        (knot_cx - bow_w, knot_cy - bow_h),
        (knot_cx - int(0.5 * SS), knot_cy),
        (knot_cx - bow_w, knot_cy + bow_h),
    ])
    pygame.draw.polygon(big, RED, [
        (knot_cx + bow_w, knot_cy - bow_h),
        (knot_cx + int(0.5 * SS), knot_cy),
        (knot_cx + bow_w, knot_cy + bow_h),
    ])
    pygame.draw.circle(big, RED, (knot_cx, knot_cy), int(1.5 * SS))
    pygame.draw.polygon(big, DOME, [
        (knot_cx - bow_w, knot_cy - bow_h),
        (knot_cx - int(0.5 * SS), knot_cy),
        (knot_cx - bow_w, knot_cy + bow_h),
    ], max(1, SS // 3))
    pygame.draw.polygon(big, DOME, [
        (knot_cx + bow_w, knot_cy - bow_h),
        (knot_cx + int(0.5 * SS), knot_cy),
        (knot_cx + bow_w, knot_cy + bow_h),
    ], max(1, SS // 3))

    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


def render_concept_b_after():
    """B with L2 Misfits mouth (no buck teeth, no plain-bar jaw line)."""
    big = r3._supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    for angle in (35, -35):
        deck = r3._draw_deck(None, 52, 10, angle)
        big.blit(deck, deck.get_rect(center=(bx, by + 8 * SS)))

    for sign in (-1, 1):
        er = pygame.Rect(0, 0, int(6 * SS), int(26 * SS))
        er.center = (bx + sign * int(11 * SS), by - int(10 * SS))
        ang = -10 * sign
        ear_sub = pygame.Surface(
            (er.width + 4 * SS, er.height + 4 * SS), pygame.SRCALPHA)
        local = pygame.Rect(0, 0, er.width, er.height)
        local.center = (ear_sub.get_width() // 2, ear_sub.get_height() // 2)
        pygame.draw.ellipse(ear_sub, BONE, local)
        pygame.draw.ellipse(ear_sub, DOME, local, max(1, int(1.2 * SS)))
        inner = local.inflate(-int(2 * SS), -int(8 * SS))
        pygame.draw.ellipse(ear_sub, RED, inner)
        rot = pygame.transform.rotate(ear_sub, ang)
        big.blit(rot, rot.get_rect(center=er.center))

    SK_W = 36
    SK_H = 32
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by + int(8 * SS))
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.4 * SS))

    base_y = sk.top + int(SK_H * SS * 0.16)
    fin_count = 5
    fin_step = int(SK_W * SS * 0.30) / (fin_count - 1)
    fin_h_peak = int(SK_H * SS * 0.95)
    fin_geom = []
    for i in range(fin_count):
        cxf = int(sk.centerx - SK_W * SS * 0.15 + i * fin_step)
        bell = 1.0 - abs((i - (fin_count - 1) / 2) / ((fin_count - 1) / 2))
        height = int(fin_h_peak * (0.45 + 0.55 * bell))
        half = int(2.4 * SS)
        tip = (cxf, base_y - height)
        pygame.draw.polygon(big, DOME, [
            (cxf - half, base_y),
            (cxf + half, base_y),
            tip,
        ])
        fin_geom.append((cxf, base_y, tip))
    stripe_w = max(1, int(1 * SS))
    for cxf, base, tip in fin_geom:
        pygame.draw.line(big, BONE,
                         (cxf, base - max(1, int(2 * SS))), tip,
                         stripe_w)

    eye_r = int(SK_W * SS * 0.13) + int(1 * SS)
    eye_x_off = int(SK_W * SS * 0.22) + int(1 * SS)
    eye_y = sk.top + int(SK_H * SS * 0.45)
    for sign in (-1, 1):
        ex = sk.centerx + sign * eye_x_off
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)

    nose_top_y = sk.top + int(SK_H * SS * 0.61)
    nose_bot_y = nose_top_y + int(2.6 * SS)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - int(1.2 * SS), nose_top_y),
        (sk.centerx + int(1.2 * SS), nose_top_y),
        (sk.centerx,                 nose_bot_y),
    ])

    _draw_jolly_roger_mouth(big, sk.centerx, sk.top, SK_H, SK_W, color=DOME)

    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


def render_concept_c_after():
    """C with L2 Misfits mouth (inverted contrast → BONE colour)."""
    big = r3._supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    patch_pts = [
        (bx - int(36 * SS), by - int(30 * SS)),
        (bx - int(28 * SS), by - int(34 * SS)),
        (bx - int(14 * SS), by - int(33 * SS)),
        (bx,                by - int(36 * SS)),
        (bx + int(16 * SS), by - int(32 * SS)),
        (bx + int(30 * SS), by - int(33 * SS)),
        (bx + int(36 * SS), by - int(26 * SS)),
        (bx + int(34 * SS), by - int(10 * SS)),
        (bx + int(37 * SS), by + int(6 * SS)),
        (bx + int(30 * SS), by + int(16 * SS)),
        (bx + int(14 * SS), by + int(18 * SS)),
        (bx,                by + int(20 * SS)),
        (bx - int(16 * SS), by + int(17 * SS)),
        (bx - int(32 * SS), by + int(14 * SS)),
        (bx - int(36 * SS), by + int(2 * SS)),
        (bx - int(34 * SS), by - int(14 * SS)),
    ]
    shadow_pts = [(px + int(1.2 * SS), py + int(1.2 * SS))
                  for px, py in patch_pts]
    pygame.draw.polygon(big, DOME, shadow_pts)
    pygame.draw.polygon(big, BONE, patch_pts)
    pygame.draw.polygon(big, DOME, patch_pts, max(1, int(1.4 * SS)))

    cx, cy = bx, by - int(6 * SS)
    inset = int(3 * SS)

    def _inset_point(px, py):
        dx = cx - px
        dy = cy - py
        d = math.hypot(dx, dy) or 1
        return (px + int(dx / d * inset), py + int(dy / d * inset))

    inset_pts = [_inset_point(px, py) for px, py in patch_pts]
    pygame.draw.polygon(big, RED, inset_pts, max(1, int(1.4 * SS)))

    head_cx = bx
    head_cy = by - int(8 * SS)

    for sign in (-1, 1):
        er = pygame.Rect(0, 0, int(5 * SS), int(20 * SS))
        er.center = (head_cx + sign * int(7 * SS),
                     head_cy - int(18 * SS))
        ang = -10 * sign
        ear_sub = pygame.Surface(
            (er.width + 4 * SS, er.height + 4 * SS), pygame.SRCALPHA)
        local = pygame.Rect(0, 0, er.width, er.height)
        local.center = (ear_sub.get_width() // 2, ear_sub.get_height() // 2)
        pygame.draw.ellipse(ear_sub, BONE, local)
        pygame.draw.ellipse(ear_sub, DOME, local, max(1, int(1.2 * SS)))
        inner = local.inflate(-int(1.8 * SS), -int(6 * SS))
        pygame.draw.ellipse(ear_sub, RED, inner)
        rot = pygame.transform.rotate(ear_sub, ang)
        big.blit(rot, rot.get_rect(center=er.center))

    SK_W = 32
    SK_H = 28
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (head_cx, head_cy)
    pygame.draw.ellipse(big, DOME, sk)

    eye_r = int(SK_W * SS * 0.13)
    eye_x_off = int(SK_W * SS * 0.22)
    eye_y = sk.top + int(SK_H * SS * 0.40)
    for sign in (-1, 1):
        ex = sk.centerx + sign * eye_x_off
        pygame.draw.circle(big, BONE, (ex, eye_y), eye_r)
        pygame.draw.circle(big, DOME, (ex, eye_y), max(1, int(1.0 * SS)))

    nose_top_y = sk.top + int(SK_H * SS * 0.58)
    nose_bot_y = nose_top_y + int(2.6 * SS)
    pygame.draw.polygon(big, RED, [
        (sk.centerx - int(1.4 * SS), nose_top_y),
        (sk.centerx + int(1.4 * SS), nose_top_y),
        (sk.centerx,                 nose_bot_y),
    ])

    # Inverted contrast — BONE mouth on DOME head silhouette.
    _draw_jolly_roger_mouth(big, sk.centerx, sk.top, SK_H, SK_W, color=BONE)

    pin_cx = bx
    pin_cy = by + int(28 * SS)
    for ang in (28, -28):
        pin = pygame.Surface((40 * SS, 14 * SS), pygame.SRCALPHA)
        pcx = pin.get_width() // 2
        pcy = pin.get_height() // 2
        pygame.draw.line(pin, CHROME,
                         (pcx - int(15 * SS), pcy),
                         (pcx + int(15 * SS), pcy),
                         max(1, int(1.8 * SS)))
        pygame.draw.line(pin, DOME,
                         (pcx - int(15 * SS), pcy),
                         (pcx + int(15 * SS), pcy),
                         max(1, int(0.5 * SS)))
        pygame.draw.circle(pin, CHROME,
                           (pcx - int(15 * SS), pcy), int(3.5 * SS),
                           max(1, int(1.4 * SS)))
        pygame.draw.polygon(pin, CHROME, [
            (pcx + int(15 * SS), pcy - int(1.5 * SS)),
            (pcx + int(18 * SS), pcy),
            (pcx + int(15 * SS), pcy + int(1.5 * SS)),
        ])
        pygame.draw.polygon(pin, DOME, [
            (pcx + int(15 * SS), pcy - int(1.5 * SS)),
            (pcx + int(18 * SS), pcy),
            (pcx + int(15 * SS), pcy + int(1.5 * SS)),
        ], max(1, SS // 3))
        rot = pygame.transform.rotate(pin, ang)
        big.blit(rot, rot.get_rect(center=(pin_cx, pin_cy)))

    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


def render_concept_d_after():
    """D with L2 Misfits mouth — face_blob acts as the skull for
    mouth-position computation; inverted contrast → BONE colour."""
    big = r3._supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    deck_w = 78 * SS
    deck_h = 30 * SS
    sub_w = deck_w + 28 * SS
    sub_h = deck_h + 28 * SS
    sub = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)

    rim = pygame.Rect(0, 0, deck_w, deck_h)
    rim.center = (sub_w // 2, sub_h // 2)

    for sign in (-1, 1):
        tx = rim.centerx + sign * int(deck_w * 0.34)
        pad_w = int(6 * SS)
        pad_rect = pygame.Rect(0, 0, pad_w, int(rim.height + 4 * SS))
        pad_rect.center = (tx, rim.centery)
        pygame.draw.rect(sub, BONE, pad_rect, border_radius=int(1.8 * SS))
        tr = pygame.Rect(0, 0, int(4 * SS), int(rim.height + 4 * SS))
        tr.center = (tx, rim.centery)
        pygame.draw.rect(sub, CHROME, tr, border_radius=int(1.5 * SS))
        for side in (-1, 1):
            wy = rim.centery + side * int(rim.height * 0.55)
            pygame.draw.circle(sub, CREAM, (tx, wy), int(3.8 * SS))
            pygame.draw.circle(sub, DOME, (tx, wy), int(3.8 * SS),
                               max(1, int(0.6 * SS)))
            pygame.draw.circle(sub, RED, (tx, wy), int(1.8 * SS))

    pygame.draw.rect(sub, CHROME, rim, border_radius=int(6 * SS))
    top = rim.inflate(-int(3 * SS), -int(3 * SS))
    pygame.draw.rect(sub, BONE, top, border_radius=int(5 * SS))

    fx = top.centerx
    fy = top.centery

    for sign in (-1, 1):
        er = pygame.Rect(0, 0, int(7 * SS), int(22 * SS))
        er.center = (fx + sign * int(7 * SS), fy - int(18 * SS))
        pygame.draw.ellipse(sub, DOME, er)
        inner = er.inflate(-int(2.5 * SS), -int(7 * SS))
        pygame.draw.ellipse(sub, RED, inner)

    face_w_units = 46
    face_h_units = 22
    face_blob = pygame.Rect(0, 0, face_w_units * SS, face_h_units * SS)
    face_blob.center = (fx, fy + int(1 * SS))
    pygame.draw.ellipse(sub, DOME, face_blob)

    for sign in (-1, 1):
        sx_ = fx + sign * int(9 * SS)
        sy_ = fy - int(3 * SS)
        pygame.draw.line(sub, BONE,
                         (sx_ - sign * int(3.5 * SS), sy_ - int(1.2 * SS)),
                         (sx_ + sign * int(3.5 * SS), sy_ + int(1.2 * SS)),
                         max(1, int(2.0 * SS)))

    pygame.draw.circle(sub, RED, (fx, fy + int(3 * SS)), int(2.0 * SS))

    # Treat the face_blob ellipse as the "skull" for the original
    # Jolly Roger mouth. face_w_units is 46 but the L2 base was 23 —
    # using the full face width 2x'd the mouth size; clamp to ~30 so
    # the dividers stay icon-sized rather than swallowing the deck.
    _draw_jolly_roger_mouth(
        sub, fx, face_blob.top, face_h_units, 30, color=BONE,
        sk_bottom=face_blob.bottom)

    rotated = pygame.transform.rotate(sub, -28)
    big.blit(rotated, rotated.get_rect(center=(bx, by)))

    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


CONCEPTS = [
    ("A", "PUNK STUDDED SKULL-BUNNY",       r3.render_concept_a, render_concept_a_after),
    ("B", "SKULL-BUNNY HYBRID + MOHAWK",    r3.render_concept_b, render_concept_b_after),
    ("C", "PUNK PATCH BUNNY",               r3.render_concept_c, render_concept_c_after),
    ("D", "SHRED-DECK GRAFFITI BUNNY",      r3.render_concept_d, render_concept_d_after),
]


def _font(size, bold=False):
    try:
        return pygame.font.SysFont("DejaVu Sans", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def _draw_cell(sheet, x, y, label_text, sub_tag, icon_96, panel_w, panel_h):
    PAD = 16
    NATIVE_W = NATIVE
    ZOOM_W = NATIVE * ZOOM

    card = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=10)
    pygame.draw.rect(sheet, (44, 50, 60), card, 1, border_radius=10)

    head_font = _font(18, bold=True)
    head = head_font.render(label_text, True, LABEL)
    sheet.blit(head, (card.left + PAD, card.top + 8))

    tag_font = _font(13)
    tag = tag_font.render(sub_tag, True, SUBLABEL)
    sheet.blit(tag, (card.left + PAD,
                     card.top + 8 + head.get_height() + 2))

    header_h = 8 + head.get_height() + 2 + tag.get_height() + 6

    native_x = card.left + PAD
    native_y = card.top + header_h + PAD + (ZOOM_W - NATIVE_W) // 2
    sheet.blit(icon_96, (native_x, native_y))
    sub_font = _font(12)
    sub = sub_font.render("96 px native", True, SUBLABEL)
    sheet.blit(sub, (native_x + (NATIVE_W - sub.get_width()) // 2,
                     native_y + NATIVE_W + 4))

    zoom = pygame.transform.scale(icon_96, (ZOOM_W, ZOOM_W))
    zoom_x = native_x + NATIVE_W + PAD
    zoom_y = card.top + header_h + PAD
    sheet.blit(zoom, (zoom_x, zoom_y))
    sub2 = sub_font.render(f"{ZOOM}x zoom (review detail)", True, SUBLABEL)
    sheet.blit(sub2, (zoom_x + (ZOOM_W - sub2.get_width()) // 2,
                      zoom_y + ZOOM_W + 4))

    return card


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()

    shipped_before = r3.render_shipped()
    shipped_after = render_shipped_after()
    before_icons = {l: bfn() for l, _n, bfn, _afn in CONCEPTS}
    after_icons = {l: afn() for l, _n, _bfn, afn in CONCEPTS}

    PAD = 16
    TITLE_H = 96
    NATIVE_W = NATIVE
    ZOOM_W = NATIVE * ZOOM

    HEADER_H = 8 + 24 + 2 + 18 + 6
    PANEL_H = HEADER_H + ZOOM_W + PAD * 2 + 20
    PANEL_W = ZOOM_W + NATIVE_W + PAD * 3
    COL_GAP = 24

    n_rows = 1 + len(CONCEPTS)
    sheet_w = PANEL_W * 2 + COL_GAP + PAD * 2
    sheet_h = TITLE_H + PAD + (PANEL_H + PAD) * n_rows

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    title_text = ("SKATEBOARD redesign  —  original Jolly Roger mouth "
                  "before/after")
    sub_text = ("BEFORE = round-3 buck teeth (LEFT). AFTER = 3 vertical "
                "tooth dividers from the original S4 Jolly Roger (RIGHT), "
                "shifted up and stripped of the bottom bar.")
    target_title_w = sheet_w - PAD * 4
    title_pt = 26
    title_font = _font(title_pt, bold=True)
    title = title_font.render(title_text, True, LABEL)
    if title.get_width() > target_title_w:
        title_pt = 22
        title_font = _font(title_pt, bold=True)
        title = title_font.render(title_text, True, LABEL)
        print(f"title fallback: dropped to {title_pt} pt "
              f"(width now {title.get_width()})")
    sub_font = _font(14)
    sub = sub_font.render(sub_text, True, SUBLABEL)
    sheet.blit(title, (PAD * 2, PAD + 4))
    sheet.blit(sub, (PAD * 2, PAD + 4 + title.get_height() + 4))

    y = TITLE_H + PAD
    x_left = PAD
    x_right = PAD + PANEL_W + COL_GAP

    _draw_cell(sheet, x_left, y,
               "SHIPPED (S4 Jolly Roger)",
               "BEFORE — current plain-bar mouth",
               shipped_before, PANEL_W, PANEL_H)
    _draw_cell(sheet, x_right, y,
               "SHIPPED (S4 Jolly Roger)",
               "AFTER — original Jolly Roger mouth",
               shipped_after, PANEL_W, PANEL_H)
    y += PANEL_H + PAD

    for letter, name, _bfn, _afn in CONCEPTS:
        _draw_cell(sheet, x_left, y,
                   f"{letter}.  {name}",
                   "BEFORE — buck teeth (round 3)",
                   before_icons[letter], PANEL_W, PANEL_H)
        _draw_cell(sheet, x_right, y,
                   f"{letter}.  {name}",
                   "AFTER — original Jolly Roger mouth",
                   after_icons[letter], PANEL_W, PANEL_H)
        y += PANEL_H + PAD

    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "skateboard_redesign", "before_after.png",
    )
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path} ({sheet.get_width()}x{sheet.get_height()})")

    print("\nDONE — before/after sheet saved with L2 Misfits AFTER mouth.")


if __name__ == "__main__":
    main()
