"""Skateboard pickup redesign — round 2 exploration sheet.

Round-1 verdict was ITERATE with D (PUNK STUDDED SKULL-BUNNY) as the clear
winner. Round 2 promotes D to slot A with the AD's three specific fixes
(real BONE buck teeth dropping below the jaw, outlined studs that read on
the CHROME face, one extra punk cue at the head), and explores four
alternative directions to compare against:

  A. PUNK STUDDED SKULL-BUNNY (refined lead)
  B. SKULL-BUNNY HYBRID + MOHAWK (round-1 A revised — bunny ears restored)
  C. STICKER TAG, TORN EDGE (round-1 B revised — torn corner + deck behind)
  D. PUNK PATCH BUNNY (new — sewn battle-vest patch with safety pins)
  E. SHRED-DECK GRAFFITI BUNNY (round-1 C revised — face breaks deck edge)

Every concept MUST show two oversized BONE buck teeth dropping below
whatever its lower jaw line is. AD locked that as the #1 priority fix.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \\
        python3 tools/render_skateboard_redesign_round_2.py
"""

import math
import os
import sys
import pygame


# ---------------------------------------------------------------------------
# Palette — LOCKED. Five colours plus CARD_BG. The round-1 sticker-tag
# nose read as pink because a CREAM under-layer leaked through the RED;
# round-2 paints RED nose pixels directly on BONE so the locked tuple
# (200, 50, 50) reads clean.
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
# Small geometry helpers shared across concepts. Kept local so the renderer
# stays standalone (no game/ imports — pure pygame, no surfarray/numpy).
# ---------------------------------------------------------------------------
def _supersurf():
    return pygame.Surface((NATIVE * SS, NATIVE * SS), pygame.SRCALPHA)


def _draw_deck(sub, length_units, height_units, tilt_deg, color_deck=CHROME,
               color_top=DOME, color_hub=CREAM, color_dot=RED):
    """One skateboard deck with trucks + wheels, returned as its own
    rotated Surface so we can composite multiple decks at angles."""
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
    """Two oversized cartoon buck teeth dropping below an upper jaw.
    Outlined in DOME, with a thin CREAM sheen down the left edge of each
    tooth so the cartoon-bunny incisor read holds at 96 px."""
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
    """One CHROME stud with an outline ring so it reads on a CHROME
    background. Round-1 made every stud invisible by sitting CHROME on
    CHROME; the DOME ring is the AD-mandated fix."""
    pygame.draw.circle(big, CHROME, (cx, cy), radius)
    pygame.draw.circle(big, ring_color, (cx, cy), radius,
                       max(1, int(radius * ring_thick_factor)))
    # Tiny DOME centre dot — adds the metal-rivet read at zoom without
    # overwhelming the 96 px native footprint.
    pygame.draw.circle(big, ring_color, (cx, cy), max(1, radius // 3))


# ---------------------------------------------------------------------------
# Shipped baseline — mirror of game.entities._draw_skateboard_icon at 96 px.
# Verbatim from round 1 so the reference panel keeps reflecting what ships.
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
# A. PUNK STUDDED SKULL-BUNNY (round-1 D, refined lead)
# AD-mandated fixes:
#  - Two oversized BONE buck teeth dropping CLEARLY below the jaw line
#    (sized like cartoon-rabbit incisors, not chrome tabs).
#  - Chinstrap studs now ride a thin DOME band so the CHROME studs read
#    against a CHROME-adjacent skull; each stud is also DOME-outlined.
#  - One added punk cue: a small RED bandana knot at the base of the
#    left ear. Picked over the torn-ear / safety-pin variants because
#    the knot adds a recognisable colour pop without nibbling silhouette.
#  - Kept: skull-bunny hybrid head with long bunny ears, RED bandage
#    cross over the left eye socket, DOME nose triangle.
# ---------------------------------------------------------------------------
def render_concept_a():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Long bunny ears behind the skull. Slight outward tilt so the
    # silhouette doesn't read as antennae.
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

    # Skull silhouette — wider than tall for a bunny-cheek read.
    SK_W = 44
    SK_H = 38
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by + 2 * SS)
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.4 * SS))

    # Eyes — big DOME sockets. Left socket gets the RED bandage cross.
    eye_r = int(SK_W * SS * 0.13)
    eye_x_off = int(SK_W * SS * 0.20)
    eye_y = sk.top + int(SK_H * SS * 0.38)
    for sign in (-1, 1):
        ex = sk.centerx + sign * eye_x_off
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)

    # RED bandage cross over the left socket — DOME outlined so it pops
    # against the BONE skull.
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

    # CHINSTRAP — thin DOME band hugging the lower skull. Curves down at
    # the centre so it reads as a strap, not a bar. CHROME studs ride
    # the band so the stud row is visible (round-1 had CHROME-on-CHROME
    # invisibility); each stud also gets a DOME outline ring.
    strap_thk = int(2.4 * SS)
    strap_center_y = sk.bottom - int(5 * SS)
    # Build the strap as a series of overlapping circles for a curved
    # band, then stud over it.
    strap_pts = []
    for i in range(-4, 5):
        t = i / 4.0
        bow = int((1 - t * t) * 2.5 * SS)
        cxs = sk.centerx + i * int(4 * SS)
        cys = strap_center_y + bow
        strap_pts.append((cxs, cys))
    # Thick DOME band underneath the studs.
    for i in range(len(strap_pts) - 1):
        pygame.draw.line(big, DOME, strap_pts[i], strap_pts[i + 1],
                         strap_thk)
    pygame.draw.circle(big, DOME, strap_pts[0], strap_thk // 2)
    pygame.draw.circle(big, DOME, strap_pts[-1], strap_thk // 2)
    # Studs on top of the band.
    for cxs, cys in strap_pts[1:-1]:
        _stud(big, cxs, cys, int(1.7 * SS))

    # ── BUCK TEETH — the headline AD fix. Sized like cartoon rabbit
    # incisors, dropping clearly below the skull's lower silhouette
    # so they read as teeth, not as skull jaw detail.
    teeth_top_y = jaw_y + int(0.5 * SS)
    _draw_buck_teeth(
        big, sk.centerx, teeth_top_y,
        tooth_w=int(5.0 * SS),
        tooth_h=int(11 * SS),
        gap=int(1.2 * SS),
    )

    # RED bandana knot at the base of the left ear — single added punk
    # cue. Small bow-tie polygon plus two short tail lines.
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
# B. SKULL-BUNNY HYBRID + MOHAWK (round-1 A revised)
# Round-1 A lost the ear silhouette entirely. Here the BONE bunny EARS
# rise tall + clear above the skull, with a THIN DOME mohawk crest
# running BETWEEN the ears (not replacing them). Crossed CHROME decks
# behind keep the skate read unambiguous. Buck teeth are oversized BONE
# below the skull jaw.
# ---------------------------------------------------------------------------
def render_concept_b():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Crossed decks behind the head — anchor the icon's skate identity.
    for angle in (35, -35):
        deck = _draw_deck(None, 52, 10, angle)
        big.blit(deck, deck.get_rect(center=(bx, by + 8 * SS)))

    # Tall BONE bunny ears, planted clearly above the skull. Slight
    # outward tilt keeps "ears" reading over "horns".
    ear_tops = []
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
        rect = rot.get_rect(center=er.center)
        big.blit(rot, rect)
        ear_tops.append((er.center, ang))

    # Skull.
    SK_W = 36
    SK_H = 32
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by - int(2 * SS))
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.4 * SS))

    # Thin mohawk crest BETWEEN the ears. Five DOME fins running the
    # cranium midline, peaking at the centre — punk arc, not a flat row.
    # Sits BEHIND the skull outline (drawn after the skull body but the
    # base anchors inside the skull's top edge so it doesn't float).
    base_y = sk.top + int(SK_H * SS * 0.16)
    fin_count = 5
    fin_step = int(SK_W * SS * 0.30) / (fin_count - 1)
    fin_h_peak = int(SK_H * SS * 0.95)
    for i in range(fin_count):
        cxf = int(sk.centerx - SK_W * SS * 0.15 + i * fin_step)
        bell = 1.0 - abs((i - (fin_count - 1) / 2) / ((fin_count - 1) / 2))
        height = int(fin_h_peak * (0.45 + 0.55 * bell))
        half = int(2.4 * SS)
        pygame.draw.polygon(big, DOME, [
            (cxf - half, base_y),
            (cxf + half, base_y),
            (cxf, base_y - height),
        ])

    # Eyes — DOME sockets.
    eye_r = int(SK_W * SS * 0.13)
    eye_x_off = int(SK_W * SS * 0.22)
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

    # Jaw line + oversized buck teeth dropping below the skull silhouette.
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
# C. STICKER TAG, TORN EDGE (round-1 B revised)
# Same bunny-face-on-square idea but the sticker has a torn / peeled
# corner (top-right curl), tilted ~12° off axis, stacked over a partial
# single skateboard deck silhouette behind. RED drips below preserved.
# AD flagged the round-1 nose as reading pink; here the nose is drawn
# DIRECTLY as the locked RED tuple on BONE, no under-layer.
# ---------------------------------------------------------------------------
def render_concept_c():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Partial single deck behind — tilted, peeking out at the lower left
    # so the sticker reads as stuck onto a real board.
    deck = _draw_deck(None, 64, 12, -16)
    big.blit(deck, deck.get_rect(center=(bx - int(3 * SS), by + int(16 * SS))))

    # Sticker — square BONE base, thick DOME outline, then tilted 12°.
    sw = 52 * SS
    pad = 8 * SS
    sticker = pygame.Surface((sw + pad * 2, sw + pad * 2), pygame.SRCALPHA)
    s_rect = pygame.Rect(0, 0, sw, sw)
    s_rect.center = (sticker.get_width() // 2, sticker.get_height() // 2)
    pygame.draw.rect(sticker, BONE, s_rect, border_radius=int(2 * SS))
    pygame.draw.rect(sticker, DOME, s_rect, max(1, int(1.4 * SS)),
                     border_radius=int(2 * SS))

    # Torn / peeled top-right corner. Cut a jagged triangle of the
    # BONE+border out, then paint the underside (CREAM curl) showing
    # behind it, with a DOME crease line marking the fold.
    tear_pts = [
        (s_rect.right, s_rect.top),
        (s_rect.right - int(18 * SS), s_rect.top),
        (s_rect.right - int(14 * SS), s_rect.top + int(4 * SS)),
        (s_rect.right - int(10 * SS), s_rect.top + int(2 * SS)),
        (s_rect.right - int(5 * SS), s_rect.top + int(6 * SS)),
        (s_rect.right - int(2 * SS), s_rect.top + int(3 * SS)),
        (s_rect.right, s_rect.top + int(14 * SS)),
    ]
    # Erase the torn wedge (cut through to transparent).
    pygame.draw.polygon(sticker, (0, 0, 0, 0), tear_pts)
    # Re-outline the ragged edge in DOME so the tear has a hand-inked
    # rim instead of a clean shape edge.
    pygame.draw.lines(sticker, DOME, False, tear_pts[1:-1],
                      max(1, int(1.4 * SS)))

    # Peeled curl — a small CREAM flap behind the tear, suggesting the
    # sticker's underside lifting up.
    curl_pts = [
        (s_rect.right - int(13 * SS), s_rect.top - int(2 * SS)),
        (s_rect.right - int(2 * SS), s_rect.top - int(7 * SS)),
        (s_rect.right + int(2 * SS), s_rect.top + int(2 * SS)),
        (s_rect.right - int(4 * SS), s_rect.top + int(3 * SS)),
    ]
    pygame.draw.polygon(sticker, CREAM, curl_pts)
    pygame.draw.polygon(sticker, DOME, curl_pts, max(1, int(1.2 * SS)))
    # Crease line from the tear root.
    pygame.draw.line(sticker, DOME,
                     (s_rect.right - int(13 * SS),
                      s_rect.top - int(1 * SS)),
                     (s_rect.right - int(2 * SS),
                      s_rect.top + int(3 * SS)),
                     max(1, int(1.0 * SS)))

    sx_c = s_rect.centerx
    sy_c = s_rect.centery + int(1 * SS)

    # Ears — two tall ovals rising from the upper third.
    ear_w = int(6 * SS)
    ear_h = int(14 * SS)
    for sign in (-1, 1):
        er = pygame.Rect(0, 0, ear_w, ear_h)
        er.center = (sx_c + sign * int(8 * SS), sy_c - int(15 * SS))
        pygame.draw.ellipse(sticker, DOME, er)
        inner = er.inflate(-int(2.5 * SS), -int(5 * SS))
        pygame.draw.ellipse(sticker, BONE, inner)

    # Eyes — solid DOME dots.
    eye_r = int(2.4 * SS)
    for sign in (-1, 1):
        pygame.draw.circle(sticker, DOME,
                           (sx_c + sign * int(7 * SS),
                            sy_c - int(3 * SS)),
                           eye_r)

    # Nose — pure RED triangle painted directly on BONE so the locked
    # (200,50,50) tuple reads. Bumped slightly bigger than round-1 to
    # survive smoothscale without lifting toward pink.
    nose_pts = [
        (sx_c - int(2.6 * SS), sy_c + int(3.5 * SS)),
        (sx_c + int(2.6 * SS), sy_c + int(3.5 * SS)),
        (sx_c,                 sy_c + int(6.5 * SS)),
    ]
    pygame.draw.polygon(sticker, RED, nose_pts)
    pygame.draw.polygon(sticker, DOME, nose_pts, max(1, SS // 3))

    # Mouth — buck-tooth grin under a short DOME upper-jaw line.
    jaw_y = sy_c + int(9 * SS)
    pygame.draw.line(sticker, DOME,
                     (sx_c - int(7 * SS), jaw_y),
                     (sx_c + int(7 * SS), jaw_y),
                     max(1, int(1.0 * SS)))
    _draw_buck_teeth(sticker, sx_c, jaw_y + int(0.4 * SS),
                     tooth_w=int(3.8 * SS),
                     tooth_h=int(7.2 * SS),
                     gap=int(1.0 * SS))

    rotated = pygame.transform.rotate(sticker, 12)
    big.blit(rotated, rotated.get_rect(center=(bx, by - 2 * SS)))

    # RED ink drips bleeding from the sticker's bottom edge. Hand-placed
    # asymmetric drip lengths so it reads as rebellious paint, not pattern.
    drip_origins = [
        (bx - 18 * SS, by + 18 * SS, 6 * SS),
        (bx - 4 * SS,  by + 24 * SS, 9 * SS),
        (bx + 12 * SS, by + 20 * SS, 5 * SS),
    ]
    for dx, dy, dl in drip_origins:
        pygame.draw.line(big, RED, (dx, dy), (dx, dy + dl),
                         max(1, int(1.6 * SS)))
        pygame.draw.circle(big, RED, (dx, dy + dl), max(1, int(1.6 * SS)))

    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


# ---------------------------------------------------------------------------
# D. PUNK PATCH BUNNY (new — replaces round-1 E bunny-wheel cross)
# A's punk skull-bunny head sitting on a torn BONE patch with visible
# RED stitching marks around the patch border (a band-aid / battle-vest
# patch). Two crossed CHROME safety pins below the patch as the punk
# seal. No deck behind — the patch IS the icon. Reads as a sewn-on
# punk-vest emblem.
# ---------------------------------------------------------------------------
def render_concept_d():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Patch base — irregular BONE quad with ragged edges so it reads as
    # a torn-fabric patch rather than a clean square sticker.
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
    pygame.draw.polygon(big, BONE, patch_pts)
    pygame.draw.polygon(big, DOME, patch_pts, max(1, int(1.4 * SS)))

    # RED stitching dashes around the patch border — runs just inside
    # the patch outline so the stitches read on the BONE field, not on
    # the dark backdrop.
    n = len(patch_pts)
    for i in range(n):
        p1 = patch_pts[i]
        p2 = patch_pts[(i + 1) % n]
        # Inset toward the centroid by ~3 px (SS).
        cx, cy = bx, by - int(6 * SS)
        seg_steps = 5
        for s in range(seg_steps):
            t1 = (s + 0.05) / seg_steps
            t2 = (s + 0.55) / seg_steps
            ax = int(p1[0] * (1 - t1) + p2[0] * t1)
            ay = int(p1[1] * (1 - t1) + p2[1] * t1)
            bx2 = int(p1[0] * (1 - t2) + p2[0] * t2)
            by2 = int(p1[1] * (1 - t2) + p2[1] * t2)
            # Inset each dash toward the patch interior.
            def _ins(px, py):
                dx = cx - px
                dy = cy - py
                d = math.hypot(dx, dy) or 1
                ins = int(3 * SS)
                return (px + int(dx / d * ins), py + int(dy / d * ins))
            ai = _ins(ax, ay)
            bi = _ins(bx2, by2)
            pygame.draw.line(big, RED, ai, bi, max(1, int(1.4 * SS)))

    # Skull-bunny head — compact version of A, scaled to fit the patch.
    head_cx = bx
    head_cy = by - int(8 * SS)

    # Bunny ears behind the head.
    ear_centers = {}
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
        ear_centers[sign] = er.center

    # Head silhouette (BONE-on-BONE would vanish, so the head is DOME-
    # filled to pop against the patch).
    SK_W = 32
    SK_H = 28
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (head_cx, head_cy)
    pygame.draw.ellipse(big, DOME, sk)

    # Eyes — BONE sockets (inverted contrast so they read on DOME head).
    eye_r = int(SK_W * SS * 0.13)
    eye_x_off = int(SK_W * SS * 0.22)
    eye_y = sk.top + int(SK_H * SS * 0.40)
    for sign in (-1, 1):
        ex = sk.centerx + sign * eye_x_off
        pygame.draw.circle(big, BONE, (ex, eye_y), eye_r)
        pygame.draw.circle(big, DOME, (ex, eye_y), max(1, int(1.0 * SS)))

    # Nose — RED triangle.
    nose_top_y = sk.top + int(SK_H * SS * 0.58)
    nose_bot_y = nose_top_y + int(2.6 * SS)
    nose_pts = [
        (sk.centerx - int(1.4 * SS), nose_top_y),
        (sk.centerx + int(1.4 * SS), nose_top_y),
        (sk.centerx,                 nose_bot_y),
    ]
    pygame.draw.polygon(big, RED, nose_pts)

    # Jaw line + buck teeth dropping below the dark head silhouette and
    # extending well past the patch's lower edge.
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

    # Two crossed CHROME safety pins below the patch — the punk seal.
    pin_cx = bx
    pin_cy = by + int(28 * SS)
    for ang in (28, -28):
        pin = pygame.Surface((40 * SS, 14 * SS), pygame.SRCALPHA)
        pcx = pin.get_width() // 2
        pcy = pin.get_height() // 2
        # Pin shaft.
        pygame.draw.line(pin, CHROME,
                         (pcx - int(15 * SS), pcy),
                         (pcx + int(15 * SS), pcy),
                         max(1, int(1.8 * SS)))
        pygame.draw.line(pin, DOME,
                         (pcx - int(15 * SS), pcy),
                         (pcx + int(15 * SS), pcy),
                         max(1, int(0.5 * SS)))
        # Pin loop (round end on the left).
        pygame.draw.circle(pin, CHROME,
                           (pcx - int(15 * SS), pcy), int(3.5 * SS),
                           max(1, int(1.4 * SS)))
        # Pin clasp tip on the right — small DOME triangle.
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
# E. SHRED-DECK GRAFFITI BUNNY (round-1 C revised)
# Single skateboard deck tilted on the diagonal, with a LARGE bunny face
# airbrushed in DOME on BONE filling most of the deck top. EARS poke
# ABOVE the deck's top edge (breaking the silhouette); BUCK TEETH poke
# BELOW the deck's bottom edge. CHROME trucks + RED wheels at each end.
# This time the face is BIG and BREAKS the deck silhouette — that's the
# AD-mandated fix vs. round-1 C, which kept everything inside the deck
# and didn't read at 96 px.
# ---------------------------------------------------------------------------
def render_concept_e():
    big = _supersurf()
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Deck + face are built on a sub-surface so we can rotate the whole
    # composition together and the silhouette-breaking ears / teeth keep
    # their relationship to the deck edges through the rotate.
    deck_w = 78 * SS
    deck_h = 30 * SS
    sub_w = deck_w + 28 * SS  # extra room for ears + teeth to extend
    sub_h = deck_h + 28 * SS
    sub = pygame.Surface((sub_w, sub_h), pygame.SRCALPHA)

    rim = pygame.Rect(0, 0, deck_w, deck_h)
    rim.center = (sub_w // 2, sub_h // 2)

    # Trucks — CHROME nubs under the deck.
    for sign in (-1, 1):
        tx = rim.centerx + sign * int(deck_w * 0.34)
        tr = pygame.Rect(0, 0, int(4 * SS), int(rim.height + 4 * SS))
        tr.center = (tx, rim.centery)
        pygame.draw.rect(sub, CHROME, tr, border_radius=int(1.5 * SS))
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

    # EARS — tall DOME pills rising well ABOVE the deck top edge so they
    # break the silhouette. RED inner-ear marks for the cartoon cue.
    for sign in (-1, 1):
        er = pygame.Rect(0, 0, int(7 * SS), int(22 * SS))
        er.center = (fx + sign * int(7 * SS), fy - int(18 * SS))
        pygame.draw.ellipse(sub, DOME, er)
        inner = er.inflate(-int(2.5 * SS), -int(7 * SS))
        pygame.draw.ellipse(sub, RED, inner)

    # Bunny face — LARGE airbrushed DOME silhouette filling the deck top.
    # A rounded DOME blob with inner BONE features. The blob is wider
    # than tall so it reads as a head on the deck plank.
    face_blob = pygame.Rect(0, 0, int(46 * SS), int(22 * SS))
    face_blob.center = (fx, fy + int(1 * SS))
    pygame.draw.ellipse(sub, DOME, face_blob)

    # Angry slit eyes — BONE on DOME, angled inward for the punk attitude.
    for sign in (-1, 1):
        sx_ = fx + sign * int(9 * SS)
        sy_ = fy - int(3 * SS)
        pygame.draw.line(sub, BONE,
                         (sx_ - sign * int(3.5 * SS), sy_ - int(1.2 * SS)),
                         (sx_ + sign * int(3.5 * SS), sy_ + int(1.2 * SS)),
                         max(1, int(2.0 * SS)))

    # Nose — RED dot painted on the DOME face.
    pygame.draw.circle(sub, RED, (fx, fy + int(3 * SS)), int(2.0 * SS))

    # Snarl line + BIG buck teeth dropping BELOW the deck silhouette.
    # The teeth top sits at the deck's lower edge so they hang past it,
    # which is the AD's silhouette-breaking requirement.
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

    rotated = pygame.transform.rotate(sub, -22)
    big.blit(rotated, rotated.get_rect(center=(bx, by)))

    return pygame.transform.smoothscale(big, (NATIVE, NATIVE))


# ---------------------------------------------------------------------------
# Sheet composition
# ---------------------------------------------------------------------------
CONCEPTS = [
    ("A", "PUNK STUDDED SKULL-BUNNY (lead)", render_concept_a),
    ("B", "SKULL-BUNNY HYBRID + MOHAWK",     render_concept_b),
    ("C", "STICKER TAG, TORN EDGE",          render_concept_c),
    ("D", "PUNK PATCH BUNNY",                render_concept_d),
    ("E", "SHRED-DECK GRAFFITI BUNNY",       render_concept_e),
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

    # 1 reference panel + 5 concept panels in a single column.
    sheet_w = PANEL_W + PAD * 2
    sheet_h = TITLE_H + PAD + PANEL_H * 6 + PAD * 6

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    title_font = _font(26, bold=True)
    sub_font = _font(16)
    title_text = "SKATEBOARD redesign  —  round 2 (punk bunny v2)"
    sub_text = "D promoted to A; teeth pushed below jaw on every concept."
    title = title_font.render(title_text, True, LABEL)
    sub = sub_font.render(sub_text, True, SUBLABEL)

    # Round 1 clipped its title on the right; verify the title fits the
    # sheet width before drawing and shorten if it doesn't.
    max_title_w = sheet_w - PAD * 4
    if title.get_width() > max_title_w:
        print(f"WARNING title pixel width {title.get_width()} > "
              f"max {max_title_w}; consider shortening.")
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
        "docs", "skateboard_redesign", "round_2.png",
    )
    pygame.image.save(sheet, out_path)
    print(f"wrote {out_path} ({sheet.get_width()}x{sheet.get_height()})")

    # ------------------------------------------------------------------
    # Diagnostic palette + buck-teeth probes. Print samples and warn on
    # misses (smoothscale anti-aliasing produces intermediate RGB values
    # that aren't true palette violations; the visual is what AD judges).
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
    # Approximate centres in 96 px native where each concept's teeth live.
    # Round-2 teeth all drop further below the jaw than round-1, so the
    # probe Y coords shift down vs. round 1.
    teeth_probes = {
        "A": [(44, 68), (52, 68), (44, 74), (52, 74)],
        "B": [(44, 64), (52, 64), (44, 70), (52, 70)],
        "C": [(46, 60), (52, 60), (46, 66), (52, 66)],
        "D": [(44, 56), (52, 56), (44, 62), (52, 62)],
        "E": [(44, 56), (54, 56), (44, 62), (54, 62)],
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
        print(f"\nWARNING palette samples outside locked tol "
              f"(likely smoothscale interpolation): "
              f"{palette_warnings[:5]}")
    if teeth_warnings:
        print(f"WARNING teeth probe missed on: {teeth_warnings} "
              f"(probe coords approximate; check the rendered PNG)")
    print("\nDONE — round 2 sheet saved; art-director will judge visually.")


if __name__ == "__main__":
    main()
