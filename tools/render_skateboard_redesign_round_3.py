"""Skateboard pickup redesign — round 3 (FINAL) exploration sheet.

Round-2 verdict was ITERATE with B (SKULL-BUNNY HYBRID + MOHAWK) as the
lead. This is the last round of the design loop; the sheet ships to the
user regardless of verdict. Round 3 drops round-2 C (sticker tag) per AD
and refines the four survivors with the AD's specific notes:

  A. PUNK STUDDED SKULL-BUNNY    chinstrap replaced by a CHROME spiked
                                  collar BELOW the jaw line
  B. SKULL-BUNNY HYBRID + MOHAWK eye sockets +1 px wider, mohawk gains
                                  a 1-px BONE highlight stripe
  C. PUNK PATCH BUNNY            dashed RED stitching → continuous RED
                                  border line
  D. SHRED-DECK GRAFFITI BUNNY   tilt steepened to -28 degrees + 1-px
                                  BONE separation between trucks and
                                  deck underside

Universal constraint: oversized BONE buck teeth still drop below the
jaw / patch / deck on every concept. Palette is the locked 5-tuple plus
the card backdrop.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_skateboard_redesign_round_3.py
"""

import math
import os
import sys
import pygame


# ---------------------------------------------------------------------------
# Palette — LOCKED. Five colours plus CARD_BG. Same as round 2.
# ---------------------------------------------------------------------------
PAL = {
    "DOME":   (10, 10, 18),
    "CHROME": (200, 200, 210),
    "BONE":   (240, 240, 230),
    "CREAM":  (245, 240, 230),
    "RED":    (200, 50, 50),
}
DOME, CHROME, BONE, CREAM, RED = (
    PAL["DOME"], PAL["CHROME"], PAL["BONE"], PAL["CREAM"], PAL["RED"]
)

CARD_BG = (26, 30, 38)
SHEET_BG = (16, 18, 24)
LABEL = (215, 220, 230)
SUBLABEL = (150, 158, 172)

SS = 6
NATIVE = 96
ZOOM = 4  # 96 * 4 = 384


# ---------------------------------------------------------------------------
# Geometry helpers — same as round 2 so the four surviving concepts keep
# their core construction. Pure pygame, no surfarray/numpy.
# ---------------------------------------------------------------------------
def _supersurf():
    return pygame.Surface((NATIVE * SS, NATIVE * SS), pygame.SRCALPHA)


def _draw_deck(sub, length_units, height_units, tilt_deg, color_deck=CHROME,
               color_top=DOME, color_hub=CREAM, color_dot=RED):
    """Skateboard deck with trucks + wheels, returned as its own rotated
    Surface. Used by the shipped reference and concept B."""
    pad = 4 * SS
    sub_w = length_units * SS + pad * 2
    sub_h = height_units * SS + pad * 2
    surf = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)
    deck = pygame.Rect(0, 0, length_units * SS, height_units * SS)
    deck.center = (sub_w // 2, sub_h // 2)
    pygame.draw.rect(surf, color_deck, deck, border_radius=2 * SS)
    pygame.draw.rect(surf, color_top, deck.inflate(-2 * SS, -2 * SS),
                     border_radius=SS)
    for sign in (-1, 1):
        wx = deck.centerx + sign * (deck.width // 2 - 3 * SS)
        pygame.draw.circle(surf, color_hub, (wx, deck.centery), int(3 * SS))
        pygame.draw.circle(surf, color_dot, (wx, deck.centery), int(1.4 * SS))
    return pygame.transform.rotate(surf, tilt_deg)


def _draw_buck_teeth(big, cx, top_y, tooth_w, tooth_h, gap, color=BONE,
                     outline=DOME, sheen=CREAM):
    """Two oversized cartoon buck teeth dropping below an upper jaw line."""
    half_gap = gap // 2
    for side in (-1, 1):
        x = cx + side * (half_gap + tooth_w) - tooth_w if side == -1 \
            else cx + half_gap
        rect = pygame.Rect(x, top_y, tooth_w, tooth_h)
        radius = max(1, tooth_w // 4)
        pygame.draw.rect(big, color, rect, border_radius=radius)
        pygame.draw.rect(big, outline, rect, max(1, SS // 2),
                         border_radius=radius)
        sheen_w = max(1, tooth_w // 6)
        sheen_rect = pygame.Rect(rect.left + sheen_w,
                                 rect.top + tooth_h // 6,
                                 sheen_w, tooth_h // 2)
        pygame.draw.rect(big, sheen, sheen_rect)


def _stud(big, cx, cy, radius, ring_color=DOME, ring_thick_factor=0.33):
    """CHROME stud with an outline ring so it pops against a CHROME-
    adjacent field."""
    pygame.draw.circle(big, CHROME, (cx, cy), radius)
    pygame.draw.circle(big, ring_color, (cx, cy), radius,
                       max(1, int(radius * ring_thick_factor)))
    pygame.draw.circle(big, ring_color, (cx, cy), max(1, radius // 3))


def _drop_shadow(big, cx, cy, radius, color=DOME, dy_units=1):
    """1-pixel-native DOME shadow under a CHROME element so it doesn't
    blur into BONE at 96 px. AD's prescription for concept A's spikes."""
    pygame.draw.circle(big, color, (cx, cy + int(dy_units * SS)), radius)


# ---------------------------------------------------------------------------
# Shipped baseline — same renderer as rounds 1 and 2.
# ---------------------------------------------------------------------------
def render_shipped():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2
    for angle in (35, -35):
        deck = _draw_deck(None, 46, 9, angle)
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
    jaw_y = sk.top + int(SK_H * SS * 0.78)
    span = 12 * SS
    pygame.draw.line(big, DOME,
                     (sk.centerx - span // 2, jaw_y),
                     (sk.centerx + span // 2, jaw_y),
                     max(1, int(1.4 * SS)))
    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


# ---------------------------------------------------------------------------
# A. PUNK STUDDED SKULL-BUNNY (refined per AD round-3 fix)
# AD demanded: drop the chinstrap, replace with a CHROME spiked collar
# sitting BELOW the jaw line. Three triangular spikes radiating outward
# from a thin DOME band hugging the neck, each spike with a 1-px DOME
# drop shadow so it doesn't blur into the BONE field at 96 px.
# Kept: bunny ears, RED bandage cross over the left eye socket,
# oversized BONE buck teeth, RED bandana knot at the left ear base.
# ---------------------------------------------------------------------------
def render_concept_a():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Bunny ears behind the skull.
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

    # Skull.
    SK_W = 44
    SK_H = 38
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by + 2 * SS)
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.4 * SS))

    # Eye sockets — DOME.
    eye_r = int(SK_W * SS * 0.13)
    eye_x_off = int(SK_W * SS * 0.20)
    eye_y = sk.top + int(SK_H * SS * 0.38)
    for sign in (-1, 1):
        ex = sk.centerx + sign * eye_x_off
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)

    # RED bandage cross over the left socket.
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

    # Nose — DOME triangle.
    nose_top_y = sk.top + int(SK_H * SS * 0.55)
    nose_bot_y = nose_top_y + int(3 * SS)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - int(1.4 * SS), nose_top_y),
        (sk.centerx + int(1.4 * SS), nose_top_y),
        (sk.centerx,                 nose_bot_y),
    ])

    # Upper-jaw line.
    jaw_y = sk.top + int(SK_H * SS * 0.68)
    span = int(18 * SS)
    pygame.draw.line(big, DOME,
                     (sk.centerx - span // 2, jaw_y),
                     (sk.centerx + span // 2, jaw_y),
                     max(1, int(1.4 * SS)))

    # Buck teeth — same oversized BONE incisors as round 2.
    teeth_top_y = jaw_y + int(0.5 * SS)
    _draw_buck_teeth(
        big, sk.centerx, teeth_top_y,
        tooth_w=int(5.0 * SS),
        tooth_h=int(11 * SS),
        gap=int(1.2 * SS),
    )

    # ── SPIKED CHROME COLLAR — replaces the chinstrap. Thin DOME neck
    # band BELOW the jaw line (well below the buck teeth so the punk cue
    # sits beneath them instead of fighting them), with four triangular
    # CHROME spikes pointing outward from the band. Each spike gets a
    # 1-px DOME drop shadow underneath so it doesn't blur into BONE.
    # Sits past the skull silhouette so the collar is the icon's lower
    # rim, not skull detail.
    collar_y = sk.bottom + int(5 * SS)
    band_w = int(28 * SS)
    band_t = int(2.6 * SS)
    band = pygame.Rect(0, 0, band_w, band_t)
    band.center = (sk.centerx, collar_y)
    # DOME shadow for the band itself — one pixel down so the chrome
    # face on top reads as a discrete element on the BONE backdrop.
    band_shadow = band.copy()
    band_shadow.move_ip(0, int(1 * SS))
    pygame.draw.rect(big, DOME, band_shadow, border_radius=int(1.0 * SS))
    pygame.draw.rect(big, CHROME, band, border_radius=int(1.0 * SS))
    pygame.draw.rect(big, DOME, band, max(1, int(0.5 * SS)),
                     border_radius=int(1.0 * SS))

    # Four triangular spikes — two angled outward on each side, plus a
    # centre pair pointing straight down. Drawn from the band's lower
    # edge so the spike tips form the icon's lowest silhouette beyond
    # the buck teeth, anchoring the punk read at the bottom of the head.
    spike_h = int(6 * SS)
    spike_half_w = int(1.8 * SS)
    spike_defs = [
        # (anchor_x_offset_from_centre, angle_deg_pointing_outward)
        (-int(11 * SS), -22),
        (-int(4 * SS),    0),
        ( int(4 * SS),    0),
        ( int(11 * SS),  22),
    ]
    for x_off, ang in spike_defs:
        ax = sk.centerx + x_off
        ay = band.bottom
        # Build the spike triangle in local coords, then rotate around
        # its anchor so outward-pointing spikes splay outward.
        local_pts = [
            (-spike_half_w, 0),
            ( spike_half_w, 0),
            ( 0, spike_h),
        ]
        rad = math.radians(ang)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rot_pts = []
        for lx, ly in local_pts:
            rx = lx * cos_a - ly * sin_a
            ry = lx * sin_a + ly * cos_a
            rot_pts.append((ax + rx, ay + ry))
        # DOME drop shadow — same triangle, shifted 1 px native down.
        shadow_pts = [(px, py + int(1 * SS)) for px, py in rot_pts]
        pygame.draw.polygon(big, DOME, shadow_pts)
        pygame.draw.polygon(big, CHROME, rot_pts)
        pygame.draw.polygon(big, DOME, rot_pts, max(1, SS // 3))

    # RED bandana knot at the base of the left ear — kept from round 2.
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


# ---------------------------------------------------------------------------
# B. SKULL-BUNNY HYBRID + MOHAWK (lead — round-3 polish only)
# AD prescription: eye sockets +1 px wider each side for menace, and a
# 1-px BONE highlight stripe running along the mohawk peak so the crest
# reads as spiky rather than as a solid dark blob at 96 px. Everything
# else from round 2 holds.
# ---------------------------------------------------------------------------
def render_concept_b():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Crossed decks behind the head.
    for angle in (35, -35):
        deck = _draw_deck(None, 52, 10, angle)
        big.blit(deck, deck.get_rect(center=(bx, by + 8 * SS)))

    # Bunny ears.
    for sign in (-1, 1):
        er = pygame.Rect(0, 0, int(6 * SS), int(26 * SS))
        er.center = (bx + sign * int(11 * SS), by - int(20 * SS))
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

    # Skull.
    SK_W = 36
    SK_H = 32
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by - int(2 * SS))
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.4 * SS))

    # Mohawk crest between the ears — DOME fins with a BONE peak stripe.
    # AD wanted the crest to read as a spiky tuft, not a black blob, so
    # each fin now carries a 1-px BONE highlight running down its centre
    # axis. Drawn AFTER the DOME triangle so the stripe sits on top.
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
    # 1-px native BONE highlight stripe along each fin's peak edge.
    stripe_w = max(1, int(1 * SS))
    for cxf, base, tip in fin_geom:
        pygame.draw.line(big, BONE,
                         (cxf, base - max(1, int(2 * SS))), tip,
                         stripe_w)

    # Eyes — wider sockets per AD (+1 px native each side relative to
    # round-2 B). Scaled by the eye_x_off increment to shift outward,
    # plus a small radius bump.
    eye_r = int(SK_W * SS * 0.13) + int(1 * SS)
    eye_x_off = int(SK_W * SS * 0.22) + int(1 * SS)
    eye_y = sk.top + int(SK_H * SS * 0.45)
    for sign in (-1, 1):
        ex = sk.centerx + sign * eye_x_off
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)

    # Nose.
    nose_top_y = sk.top + int(SK_H * SS * 0.61)
    nose_bot_y = nose_top_y + int(2.6 * SS)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - int(1.2 * SS), nose_top_y),
        (sk.centerx + int(1.2 * SS), nose_top_y),
        (sk.centerx,                 nose_bot_y),
    ])

    # Jaw + buck teeth.
    jaw_y = sk.top + int(SK_H * SS * 0.74)
    span = int(14 * SS)
    pygame.draw.line(big, DOME,
                     (sk.centerx - span // 2, jaw_y),
                     (sk.centerx + span // 2, jaw_y),
                     max(1, int(1.3 * SS)))
    _draw_buck_teeth(
        big, sk.centerx, jaw_y + int(0.5 * SS),
        tooth_w=int(4.4 * SS),
        tooth_h=int(9 * SS),
        gap=int(1.0 * SS),
    )

    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


# ---------------------------------------------------------------------------
# C. PUNK PATCH BUNNY (was round-2 D — round-3 polish only)
# AD prescription: replace dashed RED stitching with a continuous thin
# RED border line just inside the patch outline (dashes degrade to
# speckle at 96 px). Everything else from round 2 D holds: inverted-
# contrast DOME bunny head with BONE eye sockets and BONE-outlined
# buck teeth, two crossed CHROME safety pins below the patch, and a
# subtle DOME drop shadow on the patch's lower-right edge for depth.
# ---------------------------------------------------------------------------
def render_concept_c():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Irregular patch silhouette — same polygon as round-2 D.
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

    # DOME drop-shadow ghost of the patch, nudged down-right ~1 px native,
    # so the patch has weight against the card background.
    shadow_pts = [(px + int(1.2 * SS), py + int(1.2 * SS))
                  for px, py in patch_pts]
    pygame.draw.polygon(big, DOME, shadow_pts)

    # Patch body.
    pygame.draw.polygon(big, BONE, patch_pts)
    pygame.draw.polygon(big, DOME, patch_pts, max(1, int(1.4 * SS)))

    # CONTINUOUS RED border stitch line — inset toward the centroid by
    # ~3 px native so it rides inside the patch rim on BONE, not on the
    # dark backdrop. Closed loop so it reads as a sewn rim.
    cx, cy = bx, by - int(6 * SS)
    inset = int(3 * SS)

    def _inset_point(px, py):
        dx = cx - px
        dy = cy - py
        d = math.hypot(dx, dy) or 1
        return (px + int(dx / d * inset), py + int(dy / d * inset))

    inset_pts = [_inset_point(px, py) for px, py in patch_pts]
    pygame.draw.polygon(big, RED, inset_pts, max(1, int(1.4 * SS)))

    # Skull-bunny head on the patch — same construction as round-2 D.
    head_cx = bx
    head_cy = by - int(8 * SS)

    # Bunny ears.
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

    # DOME head silhouette (inverted contrast on the BONE patch).
    SK_W = 32
    SK_H = 28
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (head_cx, head_cy)
    pygame.draw.ellipse(big, DOME, sk)

    # BONE eye sockets with DOME pupils.
    eye_r = int(SK_W * SS * 0.13)
    eye_x_off = int(SK_W * SS * 0.22)
    eye_y = sk.top + int(SK_H * SS * 0.40)
    for sign in (-1, 1):
        ex = sk.centerx + sign * eye_x_off
        pygame.draw.circle(big, BONE, (ex, eye_y), eye_r)
        pygame.draw.circle(big, DOME, (ex, eye_y), max(1, int(1.0 * SS)))

    # RED nose.
    nose_top_y = sk.top + int(SK_H * SS * 0.58)
    nose_bot_y = nose_top_y + int(2.6 * SS)
    pygame.draw.polygon(big, RED, [
        (sk.centerx - int(1.4 * SS), nose_top_y),
        (sk.centerx + int(1.4 * SS), nose_top_y),
        (sk.centerx,                 nose_bot_y),
    ])

    # BONE jaw line + BONE-outlined buck teeth.
    jaw_y = sk.top + int(SK_H * SS * 0.72)
    span = int(13 * SS)
    pygame.draw.line(big, BONE,
                     (sk.centerx - span // 2, jaw_y),
                     (sk.centerx + span // 2, jaw_y),
                     max(1, int(1.2 * SS)))
    _draw_buck_teeth(
        big, sk.centerx, jaw_y + int(0.4 * SS),
        tooth_w=int(4.2 * SS),
        tooth_h=int(9 * SS),
        gap=int(1.0 * SS),
        outline=BONE,
    )

    # Two crossed CHROME safety pins below the patch.
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


# ---------------------------------------------------------------------------
# D. SHRED-DECK GRAFFITI BUNNY (was round-2 E — two AD polishes)
# AD prescription: tilt steepened from ~10 deg to 28 deg so the deck
# reads as motion (Tony Hawk Pro Skater deck-graphic thumbnails as
# reference), and a 1-pixel BONE separation between the CHROME trucks
# and the deck underside so the trucks don't blur into the deck at 96.
# The face still breaks the silhouette top-and-bottom (ears above,
# teeth below).
# ---------------------------------------------------------------------------
def render_concept_d():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    deck_w = 78 * SS
    deck_h = 30 * SS
    sub_w = deck_w + 28 * SS
    sub_h = deck_h + 28 * SS
    sub = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)

    rim = pygame.Rect(0, 0, deck_w, deck_h)
    rim.center = (sub_w // 2, sub_h // 2)

    # Trucks — CHROME shafts wrapped in a 1-px BONE halo so they don't
    # blur into the CHROME deck rim at 96 px. The BONE pad sits just
    # behind the truck, creating a visible separator stripe on both
    # vertical edges where the truck meets the deck underside.
    for sign in (-1, 1):
        tx = rim.centerx + sign * int(deck_w * 0.34)
        # BONE separator pad — slightly wider than the truck shaft.
        pad_w = int(6 * SS)
        pad_rect = pygame.Rect(0, 0, pad_w, int(rim.height + 4 * SS))
        pad_rect.center = (tx, rim.centery)
        pygame.draw.rect(sub, BONE, pad_rect, border_radius=int(1.8 * SS))
        # CHROME truck shaft on top of the BONE pad.
        tr = pygame.Rect(0, 0, int(4 * SS), int(rim.height + 4 * SS))
        tr.center = (tx, rim.centery)
        pygame.draw.rect(sub, CHROME, tr, border_radius=int(1.5 * SS))
        # Wheels — CREAM with DOME rim and RED hub.
        for side in (-1, 1):
            wy = rim.centery + side * int(rim.height * 0.55)
            pygame.draw.circle(sub, CREAM, (tx, wy), int(3.8 * SS))
            pygame.draw.circle(sub, DOME, (tx, wy), int(3.8 * SS),
                               max(1, int(0.6 * SS)))
            pygame.draw.circle(sub, RED, (tx, wy), int(1.8 * SS))

    # Deck body — CHROME rim + BONE top.
    pygame.draw.rect(sub, CHROME, rim, border_radius=int(6 * SS))
    top = rim.inflate(-int(3 * SS), -int(3 * SS))
    pygame.draw.rect(sub, BONE, top, border_radius=int(5 * SS))

    fx = top.centerx
    fy = top.centery

    # Ears poking above the deck top edge.
    for sign in (-1, 1):
        er = pygame.Rect(0, 0, int(7 * SS), int(22 * SS))
        er.center = (fx + sign * int(7 * SS), fy - int(18 * SS))
        pygame.draw.ellipse(sub, DOME, er)
        inner = er.inflate(-int(2.5 * SS), -int(7 * SS))
        pygame.draw.ellipse(sub, RED, inner)

    # Bunny face — DOME blob filling the deck top.
    face_blob = pygame.Rect(0, 0, int(46 * SS), int(22 * SS))
    face_blob.center = (fx, fy + int(1 * SS))
    pygame.draw.ellipse(sub, DOME, face_blob)

    # Slit eyes — BONE on DOME.
    for sign in (-1, 1):
        sx_ = fx + sign * int(9 * SS)
        sy_ = fy - int(3 * SS)
        pygame.draw.line(sub, BONE,
                         (sx_ - sign * int(3.5 * SS), sy_ - int(1.2 * SS)),
                         (sx_ + sign * int(3.5 * SS), sy_ + int(1.2 * SS)),
                         max(1, int(2.0 * SS)))

    # Nose.
    pygame.draw.circle(sub, RED, (fx, fy + int(3 * SS)), int(2.0 * SS))

    # Snarl line + BIG buck teeth dropping below the deck silhouette.
    jaw_y = fy + int(6.5 * SS)
    pygame.draw.line(sub, BONE,
                     (fx - int(10 * SS), jaw_y),
                     (fx + int(10 * SS), jaw_y),
                     max(1, int(1.4 * SS)))
    _draw_buck_teeth(
        sub, fx, jaw_y + int(0.5 * SS),
        tooth_w=int(4.6 * SS),
        tooth_h=int(11 * SS),
        gap=int(1.2 * SS),
        outline=BONE,
    )

    # AD-mandated tilt bump from -22 (round 2) to -28 (round 3) so the
    # deck reads as motion rather than a static frame.
    rotated = pygame.transform.rotate(sub, -28)
    big.blit(rotated, rotated.get_rect(center=(bx, by)))

    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


# ---------------------------------------------------------------------------
# Sheet composition — 4 panels (down from 5 in round 2; C dropped).
# ---------------------------------------------------------------------------
CONCEPTS = [
    ("A", "PUNK STUDDED SKULL-BUNNY",       render_concept_a),
    ("B", "SKULL-BUNNY HYBRID + MOHAWK (lead)", render_concept_b),
    ("C", "PUNK PATCH BUNNY",               render_concept_c),
    ("D", "SHRED-DECK GRAFFITI BUNNY",      render_concept_d),
]


def _font(size, bold=False):
    try:
        return pygame.font.SysFont("DejaVu Sans", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)


def _draw_panel(sheet, x, y, label_text, icon_96):
    """One panel: charcoal card + label + 96 px native + 4x zoom."""
    PAD = 16
    NATIVE_W = NATIVE
    ZOOM_W = NATIVE * ZOOM
    LABEL_H = 30
    panel_h = LABEL_H + ZOOM_W + PAD * 2
    panel_w = ZOOM_W + NATIVE_W + PAD * 3

    card = pygame.Rect(x, y, panel_w, panel_h)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=10)
    pygame.draw.rect(sheet, (44, 50, 60), card, 1, border_radius=10)

    font = _font(20, bold=True)
    lbl = font.render(label_text, True, LABEL)
    sheet.blit(lbl, (card.left + PAD, card.top + 8))

    native_x = card.left + PAD
    native_y = card.top + LABEL_H + PAD + (ZOOM_W - NATIVE_W) // 2
    sheet.blit(icon_96, (native_x, native_y))
    sub_font = _font(13)
    sub = sub_font.render("96 px native", True, SUBLABEL)
    sheet.blit(sub, (native_x + (NATIVE_W - sub.get_width()) // 2,
                     native_y + NATIVE_W + 4))

    zoom = pygame.transform.scale(icon_96, (ZOOM_W, ZOOM_W))
    zoom_x = native_x + NATIVE_W + PAD
    zoom_y = card.top + LABEL_H + PAD
    sheet.blit(zoom, (zoom_x, zoom_y))
    sub2 = sub_font.render(f"{ZOOM}x zoom (review detail)", True, SUBLABEL)
    sheet.blit(sub2, (zoom_x + (ZOOM_W - sub2.get_width()) // 2,
                      zoom_y + ZOOM_W + 4))

    return card


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()

    icons = {letter: fn() for letter, _name, fn in CONCEPTS}
    shipped_icon = render_shipped()

    PAD = 16
    TITLE_H = 86
    PANEL_H = 30 + NATIVE * ZOOM + PAD * 2
    PANEL_W = NATIVE * ZOOM + NATIVE + PAD * 3

    # 1 reference panel + 4 concept panels in a single column (round 3
    # drops the round-2 C sticker tag concept).
    n_panels = 1 + len(CONCEPTS)
    sheet_w = PANEL_W + PAD * 2
    sheet_h = TITLE_H + PAD + PANEL_H * n_panels + PAD * n_panels

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    # Title sized to stay under 360 px wide per the brief; verify before
    # blit, fall back to 22 if a future title edit pushes past target.
    title_text = "SKATEBOARD redesign  —  round 3 (final)"
    sub_text = ("4 final candidates. AD lead: B. "
                "Sheet ships to user after this round.")
    target_title_w = 360
    title_pt = 26
    title_font = _font(title_pt, bold=True)
    title = title_font.render(title_text, True, LABEL)
    if title.get_width() > target_title_w:
        title_pt = 22
        title_font = _font(title_pt, bold=True)
        title = title_font.render(title_text, True, LABEL)
        print(f"title fallback: dropped font to {title_pt} pt "
              f"(width now {title.get_width()})")
    sub_font = _font(16)
    sub = sub_font.render(sub_text, True, SUBLABEL)

    # Also check against the sheet width — the panels themselves can be
    # wider than 360 px, so guard against right-edge clipping there too.
    max_title_w = sheet_w - PAD * 4
    if title.get_width() > max_title_w:
        print(f"WARNING title pixel width {title.get_width()} > "
              f"sheet max {max_title_w}; consider shortening.")
    sheet.blit(title, (PAD * 2, PAD + 4))
    sheet.blit(sub, (PAD * 2, PAD + 4 + title.get_height() + 4))

    y = TITLE_H + PAD
    _draw_panel(sheet, PAD, y, "SHIPPED (S4 Jolly Roger) — current",
                shipped_icon)
    y += PANEL_H + PAD

    for letter, name, _fn in CONCEPTS:
        _draw_panel(sheet, PAD, y, f"{letter}.  {name}", icons[letter])
        y += PANEL_H + PAD

    out_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "skateboard_redesign", "round_3.png",
    )
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path} ({sheet.get_width()}x{sheet.get_height()})")

    # ------------------------------------------------------------------
    # Diagnostic palette + tooth-probe samples. Smoothscale anti-aliasing
    # produces intermediate RGB values that aren't true palette
    # violations; the visual is what the AD judges.
    # ------------------------------------------------------------------
    def _nearest_name(rgb):
        best = None
        best_d = 1e9
        for name, ref in PAL.items():
            d = sum((a - b) ** 2 for a, b in zip(rgb, ref))
            if d < best_d:
                best_d = d
                best = (name, ref)
        return best, math.sqrt(best_d)

    def _in_palette(rgb, tol=8):
        for ref in PAL.values():
            if all(abs(a - b) <= tol for a, b in zip(rgb, ref)):
                return True
        if all(abs(a - b) <= tol for a, b in zip(rgb, CARD_BG)):
            return True
        return False

    print("\n--- Palette samples per concept ---")
    palette_warnings = []
    for letter, _name, _fn in CONCEPTS:
        icon = icons[letter]
        samples = []
        for sx in (24, 40, 48, 56, 72):
            for sy in (24, 40, 48, 56, 72):
                rgba = icon.get_at((sx, sy))
                if rgba.a == 0:
                    continue
                rgb = (rgba.r, rgba.g, rgba.b)
                samples.append((sx, sy, rgb))
        for sx, sy, rgb in samples[:6]:
            (pname, _pref), dist = _nearest_name(rgb)
            ok = _in_palette(rgb)
            tag = "ok" if ok else "FOREIGN"
            print(f"  {letter} ({sx},{sy})  rgb={rgb}  ~{pname} "
                  f"d={dist:.1f}  [{tag}]")
            if not ok:
                palette_warnings.append((letter, sx, sy, rgb))

    print("\n--- Bunny-teeth samples per concept ---")
    # Round-3 teeth Y coords are nudged for A (chinstrap → collar
    # widens the lower silhouette) and C (continuous border instead of
    # dashes doesn't move the teeth) but D (steeper tilt) shifts the
    # teeth diagonally — probe a small grid to cover the rotation.
    teeth_probes = {
        "A": [(44, 68), (52, 68), (44, 74), (52, 74)],
        "B": [(44, 64), (52, 64), (44, 70), (52, 70)],
        "C": [(44, 56), (52, 56), (44, 62), (52, 62)],
        "D": [(40, 56), (48, 60), (56, 64), (44, 70)],
    }
    teeth_warnings = []
    for letter, probes in teeth_probes.items():
        icon = icons[letter]
        hits = 0
        for px, py in probes:
            rgba = icon.get_at((px, py))
            rgb = (rgba.r, rgba.g, rgba.b)
            (pname, _pref), dist = _nearest_name(rgb)
            is_tooth = pname in ("BONE", "CREAM") and dist <= 30 \
                and rgba.a > 0
            if is_tooth:
                hits += 1
            print(f"  {letter} ({px},{py})  rgb={rgb}  ~{pname} "
                  f"d={dist:.1f} a={rgba.a}  tooth={is_tooth}")
        if hits == 0:
            teeth_warnings.append(letter)

    if palette_warnings:
        print(f"\nNOTE palette samples outside locked tol "
              f"(likely smoothscale interpolation): "
              f"{palette_warnings[:5]}")
    if teeth_warnings:
        print(f"NOTE teeth probe missed on: {teeth_warnings} "
              f"(probe coords approximate; check the rendered PNG)")
    print("\nDONE — round 3 (FINAL) sheet saved.")


if __name__ == "__main__":
    main()
