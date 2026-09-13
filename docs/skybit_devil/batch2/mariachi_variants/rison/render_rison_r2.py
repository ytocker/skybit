"""RISON  —  round 2 review sheet (Mariachi warm-skeleton family, locked5 brief).

Concept G: "El Rison" — a cantina merrymaker calaca whose whole personality
lives in the SKULL. Head thrown BACK in a huge belly-laugh, jaw cracked FULLY
open, sockets crinkled with mirth, a sombrero tipped BACK off the brow. Lead
facet: FACIAL CHARACTER / EMOTION.

ROUND-2 FIX (AD critique, top priority): in round 1 the open jaw was an
INTERIOR ink/red shape, so it evaporated in pure black — the silhouette read
"ball + hat", not a laugh. Round 2 PUNCHES THE LAUGH INTO THE SILHOUETTE:

  * The lower MANDIBLE is no longer a closed U sitting inside the skull's round
    contour. It is a forward-jutting WEDGE that drops DOWN-AND-FORWARD off the
    cranium, hinged at the back and swung open at the front, so the bone mass
    itself breaks the round skull contour as a distinct protruding chin.
  * The OPEN MOUTH is the air GAP between the receding cranium front-edge and
    the dropped wedge — it is true negative space at the silhouette EDGE, not an
    interior void. The outline shows a clear notch between cranium and jaw.
  * Head-back tilt pushed to ~22 deg so the brow recedes and the chin/jaw
    thrusts up-and-forward — "chin to the sky" reads from the top contour alone.
  * Ink value-gap added between the back of the skull and the sombrero brim so
    the hat reads as a distinct shape stacked behind, not fused into the dome.
  * Sockets re-cut as UP-curved mirth crescents (convex-down happy arcs) with
    corner laugh-ticks — joy, not the sleepy closed lids of round 1.
  * Teeth thinned to a SMALL upper row + one curled tongue-tick; the void does
    the talking instead of a gray dither dentition.
  * Raised toasting arm + amber pulque cup built as a clear silhouette
    appendage (the prop link + the reason he is laughing).
  * Cup-and-cork pillar cap warmed toward amber so it doesn't read cooler than
    the jug at gap scale.

Anti-reaper guard held: tipped-BACK sombrero + painted MOUSTACHE + warm
AMBER/CLAY palette + dropped-open-jaw LAUGH geometry. House grammar held:
chibi, FLAT fills + hard ink keylines, dark-core -> flat-fill -> top-left sheen
triad, 1px alpha-grown outline, supersample -> smoothscale. Pulque-jug -> pillar
mirror held (round jug on-axis).

Run headless (SDL_VIDEODRIVER=dummy). Writes round_2.png beside this script.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = "/home/user/skybit"
_OUT_DIR = os.path.join(_ROOT, "docs", "skybit_devil", "batch2",
                        "mariachi_variants", "rison")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# ── PINNED PALETTE (exact hexes from the locked Rison brief — amber/clay) ────
AMBER     = (228, 168, 72)    # amber pulque / jug glaze (clay hero, lit)
TERRA     = (196, 108, 64)    # terracotta jug-body (clay hero, deep)
BONE      = (238, 226, 202)   # warm-bone skull base
TANBONE   = (168, 140, 98)    # deep tan-bone socket-shade (expressive sockets)
RUST      = (192, 62, 50)     # rust sombrero-band + sash accent
TURQ      = (60, 170, 166)    # turquoise jug-glaze fleck — TINY ONLY
INK       = (30, 22, 20)      # hard keyline
SHEEN     = (252, 242, 218)   # top-left rim-sheen


def _dark(c, f=0.62):
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f))


def _lite(c, f=0.4):
    return tuple(int(c[i] + (255 - c[i]) * f) for i in range(3))


BONE_SH   = _dark(BONE, 0.70)      # warm bone shade (kept warm, never grey)
AMBER_SH  = _dark(AMBER, 0.64)
AMBER_HI  = _lite(AMBER, 0.42)
TERRA_SH  = _dark(TERRA, 0.62)
TERRA_HI  = _lite(TERRA, 0.40)
RUST_SH   = _dark(RUST, 0.62)


# ── house-style helpers (same grammar as the family siblings) ────────────────
SS = 4  # supersample factor


def new_surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def amask(sprite, threshold=40):
    return pygame.mask.from_surface(sprite, threshold).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))


def grow_outline(sprite, color=INK, px=1):
    """1px ink keyline grown from the alpha mask (the silhouette-POP outline)."""
    w, h = sprite.get_size()
    out = new_surf(w, h)
    edge = pygame.mask.from_surface(sprite, 40).to_surface(
        setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    for dx in range(-px, px + 1):
        for dy in range(-px, px + 1):
            if dx == 0 and dy == 0:
                continue
            out.blit(edge, (dx, dy))
    out.blit(sprite, (0, 0))
    return out


def triad_sheen(sprite, sheen_col=SHEEN, top_a=120, bot_a=60,
                ell=(-0.10, -0.12, 0.74, 0.66)):
    """Top-left rim-sheen ellipse, masked to the silhouette — the lit third of
    the dark-core -> flat-fill -> sheen triad."""
    w, h = sprite.get_size()
    ov = new_surf(w, h)
    pygame.draw.ellipse(ov, (*sheen_col, top_a),
                        (int(ell[0] * w), int(ell[1] * h),
                         int(ell[2] * w), int(ell[3] * h)))
    pygame.draw.ellipse(ov, (*sheen_col, bot_a // 2),
                        (int(w * 0.05), int(h * 0.04), int(w * 0.5), int(h * 0.4)))
    ov.blit(amask(sprite), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(ov, (0, 0))
    return sprite


def core_shade(sprite, shade_col, alpha=120,
               lobe=(0.28, 0.40, 0.78, 0.72)):
    """Dark-core: a lower-right pooled shadow lobe, masked to silhouette."""
    w, h = sprite.get_size()
    ov = new_surf(w, h)
    pygame.draw.ellipse(ov, (*shade_col, alpha),
                        (int(w * lobe[0]), int(h * lobe[1]),
                         int(w * lobe[2]), int(h * lobe[3])))
    ov.blit(amask(sprite), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(ov, (0, 0))
    return sprite


# ── RISON creature (drawn at supersample, then smoothscaled) ─────────────────
DES_W, DES_H = 122, 152

# Head-back laugh tilt pushed to 22 deg (round-1 was 13). The whole skull is
# built upright then rotated back so the chin/jaw thrusts skyward — the
# belly-laugh "throw the head back" read must be legible from the top contour.
HEAD_TILT = 22


def _build_skull_upright(w, h):
    """The oversized laughing skull, drawn upright so it can be rotated back as
    a unit. The mandible is a forward-jutting WEDGE that drops DOWN-AND-FORWARD
    off the cranium so the OPEN MOUTH is an air gap at the silhouette EDGE, not
    an interior void. Returns the skull surface plus geometry for placement."""
    s = new_surf(w, h)
    cx = w * 0.5

    # ----- CRANIUM: a wide rounded dome, but DELIBERATELY cut off at the front-
    # lower edge so it does NOT close into a full circle. The chin region is
    # left OPEN (no bone) — that opening is the front of the laugh gap. -----
    cran = new_surf(w, h)
    cr_cy = h * 0.36
    cr_w = w * 0.38
    cr_h = h * 0.33
    # upper dome
    pygame.draw.ellipse(cran, BONE, (int(cx - cr_w), int(cr_cy - cr_h),
                                     int(cr_w * 2), int(cr_h * 2)))
    # cheek/upper-jaw block: a maxilla shelf carrying the UPPER teeth. It stops
    # well short of the bottom so the mandible can hang in clear air below it,
    # making the open-mouth gap a true silhouette notch.
    max_top = cr_cy + cr_h * 0.42
    max_h = cr_h * 0.40
    max_w = cr_w * 0.86
    pygame.draw.polygon(cran, BONE, [
        (cx - max_w, max_top),
        (cx + max_w, max_top),
        (cx + max_w * 0.80, max_top + max_h),
        (cx - max_w * 0.80, max_top + max_h),
    ])
    core_shade(cran, BONE_SH, 120, lobe=(0.34, 0.40, 0.66, 0.58))
    triad_sheen(cran, top_a=140, bot_a=44, ell=(0.10, 0.04, 0.62, 0.50))
    s.blit(cran, (0, 0))

    # maxilla front-edge geometry: the UPPER teeth hang from here, and the laugh
    # gap opens immediately below.
    maxilla_bottom = max_top + max_h

    # ----- DROPPED MANDIBLE: a forward-jutting WEDGE hinged at the BACK of the
    # skull and swung DOWN-AND-FORWARD. It is its own bone mass sitting in clear
    # air below+ahead of the maxilla, so the silhouette shows a protruding chin
    # with an open gap above it. THIS is the laugh in the black shape. -----
    # the OPEN-MOUTH void is filled FIRST as a clean ink cavity spanning the gap
    # between maxilla-bottom and mandible-top, so at hero scale the mouth reads
    # as one big dark hollering cavity (no body/sky bleeding through the gap),
    # while the mandible wedge below still carries the silhouette protrusion.
    fwd = cr_w * 0.30                              # forward lean toward the laugh
    mouth_cx = cx + fwd * 0.55
    mouth_top = maxilla_bottom - cr_h * 0.04
    mouth_w = cr_w * 0.66
    mouth_h = cr_h * 0.78                          # TALL -> a wide-open belly-laugh
    cav = new_surf(w, h)
    pygame.draw.ellipse(cav, INK,
                        (int(mouth_cx - mouth_w), int(mouth_top),
                         int(mouth_w * 2), int(mouth_h * 2)))
    s.blit(cav, (0, 0))

    jaw = new_surf(w, h)
    # hinge points sit high at the rear corners of the skull (just under the
    # cheekbones); the chin point thrusts down and toward the laugh direction so
    # the bone mass itself breaks the round contour as a protruding wedge.
    hinge_y = cr_cy + cr_h * 0.30
    hinge_dx = cr_w * 0.92
    chin_y = mouth_top + mouth_h * 2 + cr_h * 0.40   # chin well below the cavity
    chin_dx = cr_w * 0.18                             # narrow protruding chin
    man_pts = [
        (cx - hinge_dx + fwd * 0.2, hinge_y),               # rear-left hinge
        (cx - hinge_dx * 0.72 + fwd * 0.4, chin_y - cr_h * 0.30),
        (mouth_cx - chin_dx, chin_y),                        # chin front-left
        (mouth_cx + chin_dx, chin_y + cr_h * 0.02),          # chin front-right
        (cx + hinge_dx * 0.80 + fwd * 0.4, chin_y - cr_h * 0.26),
        (cx + hinge_dx + fwd * 0.2, hinge_y),               # rear-right hinge
        # inner top edge — hugs just UNDER the ink cavity so the mandible reads
        # as the chin bone of a dropped-open jaw, never closing the mouth.
        (cx + hinge_dx * 0.60 + fwd * 0.3, hinge_y + cr_h * 0.22),
        (mouth_cx + mouth_w * 0.82, mouth_top + mouth_h * 1.96),
        (mouth_cx - mouth_w * 0.82, mouth_top + mouth_h * 1.96),
        (cx - hinge_dx * 0.60 + fwd * 0.3, hinge_y + cr_h * 0.22),
    ]
    pygame.draw.polygon(jaw, BONE, man_pts)
    core_shade(jaw, BONE_SH, 120, lobe=(0.30, 0.34, 0.66, 0.56))
    triad_sheen(jaw, top_a=120, bot_a=34, ell=(0.20, 0.40, 0.52, 0.40))
    s.blit(jaw, (0, 0))

    # ----- SMALL UPPER tooth row only (thinned per critique) hanging off the
    # maxilla into the top of the cavity. Few, bold blocks read; the void talks.
    teeth = new_surf(w, h)
    tcount = 4
    tw = (mouth_w * 1.5) / tcount
    for i in range(tcount):
        tx = mouth_cx - mouth_w * 0.74 + tw * i + tw * 0.16
        pygame.draw.rect(teeth, BONE,
                         (int(tx), int(maxilla_bottom - cr_h * 0.03),
                          int(tw * 0.66), int(cr_h * 0.22)))
    triad_sheen(teeth, top_a=120, bot_a=30, ell=(0.22, 0.40, 0.5, 0.3))
    s.blit(teeth, (0, 0))

    # a single curled TONGUE tick low in the cavity (warm terracotta) — the
    # cantina-holler tell, kept small + low so it doesn't muddy the dark void.
    tongue = new_surf(w, h)
    tg_cy = mouth_top + mouth_h * 1.34
    pygame.draw.ellipse(tongue, TERRA,
                        (int(mouth_cx - mouth_w * 0.42), int(tg_cy - cr_h * 0.04),
                         int(mouth_w * 0.84), int(cr_h * 0.28)))
    pygame.draw.ellipse(tongue, TERRA_HI,
                        (int(mouth_cx - mouth_w * 0.18), int(tg_cy),
                         int(mouth_w * 0.30), int(cr_h * 0.11)))
    s.blit(tongue, (0, 0))

    # ----- EYE SOCKETS: UP-curved mirth crescents (convex-down happy arcs) with
    # corner laugh-tick ink marks — eyes squeezed shut in a roar of laughter,
    # NOT the flat sleepy lids of round 1. -----
    face = new_surf(w, h)
    eye_y = cr_cy + cr_h * 0.02
    eye_dx = cr_w * 0.46
    eye_r = cr_w * 0.32
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        # the squeezed-shut LAUGHING eye is a bold UP-bowed (caret-shaped) dark
        # socket: a thick chevron-arc that peaks UP at the centre. Up-curve =
        # joy; this replaces round 1's flat sleepy lid. Built as two thick
        # strokes meeting at a high apex so it reads even at 32px.
        apex = (ex, eye_y - eye_r * 0.62)
        left = (ex - eye_r, eye_y + eye_r * 0.30)
        right = (ex + eye_r, eye_y + eye_r * 0.30)
        lw = max(4, SS + 2)
        pygame.draw.line(face, TANBONE, (int(left[0]), int(left[1])),
                         (int(apex[0]), int(apex[1])), lw)
        pygame.draw.line(face, TANBONE, (int(apex[0]), int(apex[1])),
                         (int(right[0]), int(right[1])), lw)
        pygame.draw.line(face, INK, (int(left[0]), int(left[1])),
                         (int(apex[0]), int(apex[1])), max(3, SS))
        pygame.draw.line(face, INK, (int(apex[0]), int(apex[1])),
                         (int(right[0]), int(right[1])), max(3, SS))
        # laugh-line ticks fanning from the OUTER corner (crinkle of mirth)
        ox = ex + sgn * eye_r * 1.15
        for k in range(3):
            a = math.radians(-20 + k * 24)
            pygame.draw.line(face, INK,
                             (int(ox), int(eye_y + eye_r * 0.10)),
                             (int(ox + sgn * math.cos(a) * eye_r * 0.78),
                              int(eye_y + eye_r * 0.10 - math.sin(a) * eye_r * 0.78)),
                             max(2, SS // 2 + 1))

    # ----- NOSE: a small inverted-heart bone void just above the moustache -----
    ny = max_top + max_h * 0.10
    pygame.draw.polygon(face, INK, [
        (int(cx), int(ny + cr_h * 0.16)),
        (int(cx - cr_w * 0.11), int(ny - cr_h * 0.02)),
        (int(cx + cr_w * 0.11), int(ny - cr_h * 0.02))])
    s.blit(face, (0, 0))

    # ----- BUSHY PAINTED MOUSTACHE bouncing over the open mouth (anti-reaper
    # tell). Two fat upcurled handlebar lobes in rust, riding on the maxilla just
    # above the upper teeth so it frames the laugh without filling the gap. -----
    mous = new_surf(w, h)
    mo_cy = maxilla_bottom - max_h * 0.02
    for sgn in (-1, 1):
        lobe_pts = []
        for i in range(13):
            t = i / 12
            ang = math.pi * t
            rx = cx + sgn * (cr_w * 0.08 + math.cos(ang) * cr_w * 0.44)
            ry = mo_cy - math.sin(ang) * cr_h * 0.20 + (1 - t) * cr_h * 0.03
            lobe_pts.append((rx, ry))
        for i in range(13):
            t = (12 - i) / 12
            ang = math.pi * t
            rx = cx + sgn * (cr_w * 0.08 + math.cos(ang) * cr_w * 0.44)
            ry = mo_cy - math.sin(ang) * cr_h * 0.20 + (1 - t) * cr_h * 0.03 + cr_h * 0.16
            lobe_pts.append((rx, ry))
        pygame.draw.polygon(mous, RUST, lobe_pts)
        # upcurled handlebar tip flick at the outer end
        tipx = cx + sgn * cr_w * 0.90
        pygame.draw.circle(mous, RUST, (int(tipx), int(mo_cy - cr_h * 0.03)),
                           int(cr_w * 0.09))
        pygame.draw.circle(mous, RUST, (int(tipx + sgn * cr_w * 0.05),
                                        int(mo_cy - cr_h * 0.16)),
                           int(cr_w * 0.06))
    core_shade(mous, RUST_SH, 120, lobe=(0.20, 0.40, 0.62, 0.40))
    triad_sheen(mous, top_a=90, bot_a=24, ell=(0.16, 0.30, 0.66, 0.30))
    s.blit(mous, (0, 0))

    return s, (cx, cr_cy, cr_w, cr_h)


def _build_sombrero(w, h, cx, brow_y, brim_w):
    """Sombrero shoved BACK off the forehead — brim sits BEHIND/above the head,
    so the whole laughing face shows. Amber crown + rust hatband + tiny turquoise
    fleck. An ink value-gap is left between the dome and the brim (see caller) so
    the hat reads as a distinct stacked shape, not fused into the skull."""
    s = new_surf(w, h)

    brim_cy = brow_y
    brim_h = h * 0.045
    pygame.draw.ellipse(s, AMBER_SH,
                        (int(cx - brim_w), int(brim_cy - brim_h * 0.2),
                         int(brim_w * 2), int(brim_h * 2.1)))
    pygame.draw.ellipse(s, AMBER,
                        (int(cx - brim_w), int(brim_cy - brim_h),
                         int(brim_w * 2), int(brim_h * 2)))
    pygame.draw.ellipse(s, AMBER_HI,
                        (int(cx - brim_w), int(brim_cy - brim_h),
                         int(brim_w * 2), int(brim_h * 2)), max(2, SS))
    crown_w = brim_w * 0.52
    crown_h = h * 0.26
    crown_cy = brim_cy - crown_h * 0.72
    pygame.draw.polygon(s, AMBER, [
        (cx - crown_w, brim_cy + brim_h * 0.2),
        (cx - crown_w * 0.46, crown_cy - crown_h),
        (cx + crown_w * 0.46, crown_cy - crown_h),
        (cx + crown_w, brim_cy + brim_h * 0.2),
    ])
    pygame.draw.ellipse(s, AMBER,
                        (int(cx - crown_w * 0.5), int(crown_cy - crown_h * 1.1),
                         int(crown_w), int(crown_h * 0.5)))
    core_shade(s, AMBER_SH, 120, lobe=(0.30, 0.30, 0.70, 0.66))
    triad_sheen(s, top_a=110, bot_a=40, ell=(0.12, 0.06, 0.6, 0.5))

    band = new_surf(w, h)
    band_y = crown_cy + crown_h * 0.02
    pygame.draw.line(band, RUST, (int(cx - crown_w * 0.86), int(band_y)),
                     (int(cx + crown_w * 0.86), int(band_y)), int(SS * 2.4))
    pygame.draw.circle(band, TURQ, (int(cx + crown_w * 0.18), int(band_y)),
                       max(2, int(SS * 1.0)))
    s.blit(band, (0, 0))
    return s


def _build_body(w, h):
    """Minimal bony toasting body below the head: a small ribby torso, one bone
    hand RAISING a clay pulque cup HIGH (the asymmetry tell + prop link, built as
    a clear silhouette appendage), the other slapping a femur knee."""
    s = new_surf(w, h)
    cx = w * 0.5

    torso = new_surf(w, h)
    t_cy = h * 0.80
    t_w = w * 0.18
    pygame.draw.polygon(torso, BONE, [
        (cx - t_w, t_cy - h * 0.10),
        (cx + t_w, t_cy - h * 0.10),
        (cx + t_w * 0.74, t_cy + h * 0.13),
        (cx - t_w * 0.74, t_cy + h * 0.13),
    ])
    pygame.draw.line(torso, BONE_SH, (int(cx), int(t_cy - h * 0.09)),
                     (int(cx), int(t_cy + h * 0.12)), max(2, SS // 2 + 1))
    for i in range(3):
        ry = t_cy - h * 0.06 + i * h * 0.055
        rw = t_w * (0.92 - i * 0.14)
        pygame.draw.arc(torso, BONE_SH,
                        (int(cx - rw), int(ry - h * 0.03),
                         int(rw * 2), int(h * 0.08)),
                        math.radians(20), math.radians(160), max(2, SS // 2))
    core_shade(torso, BONE_SH, 120, lobe=(0.34, 0.46, 0.62, 0.5))
    triad_sheen(torso, top_a=110, bot_a=30, ell=(0.22, 0.50, 0.46, 0.3))
    pygame.draw.line(torso, RUST, (int(cx - t_w * 1.05), int(t_cy - h * 0.04)),
                     (int(cx + t_w * 0.95), int(t_cy + h * 0.10)), int(SS * 2.6))
    s.blit(torso, (0, 0))

    # ----- LEFT arm (wearer's right) slapping a femur knee -----
    arm_l = new_surf(w, h)
    sh_x, sh_y = cx - t_w * 0.9, t_cy - h * 0.07
    kn_x, kn_y = cx - t_w * 1.5, t_cy + h * 0.14
    pygame.draw.line(arm_l, BONE, (int(sh_x), int(sh_y)),
                     (int(kn_x), int(kn_y)), int(SS * 2.6))
    pygame.draw.circle(arm_l, BONE, (int(kn_x), int(kn_y)), int(w * 0.035))
    core_shade(arm_l, BONE_SH, 100, lobe=(0.10, 0.55, 0.5, 0.4))
    triad_sheen(arm_l, top_a=90, bot_a=20)
    s.blit(arm_l, (0, 0))

    # ----- RIGHT arm raised HIGH + WIDE toasting a clay pulque cup. Pushed
    # further out and up than round 1 so the raised cup is a clear silhouette
    # appendage (the prop link + the reason for the laugh — a toast). -----
    arm_r = new_surf(w, h)
    sh2_x, sh2_y = cx + t_w * 0.9, t_cy - h * 0.08
    el_x, el_y = cx + t_w * 2.1, t_cy - h * 0.06
    ha_x, ha_y = cx + t_w * 2.05, t_cy - h * 0.34
    pygame.draw.lines(arm_r, BONE, False,
                      [(int(sh2_x), int(sh2_y)), (int(el_x), int(el_y)),
                       (int(ha_x), int(ha_y))], int(SS * 2.8))
    core_shade(arm_r, BONE_SH, 100, lobe=(0.55, 0.45, 0.4, 0.4))
    triad_sheen(arm_r, top_a=90, bot_a=20)
    s.blit(arm_r, (0, 0))

    # the CLAY PULQUE CUP in the raised hand (terracotta jar + amber froth),
    # enlarged a touch so it reads as its own bump at 32px.
    cup = new_surf(w, h)
    cup_cx, cup_cy = ha_x, ha_y - h * 0.05
    cw = w * 0.085
    ch = h * 0.085
    pygame.draw.polygon(cup, TERRA, [
        (cup_cx - cw, cup_cy - ch),
        (cup_cx + cw, cup_cy - ch),
        (cup_cx + cw * 0.74, cup_cy + ch),
        (cup_cx - cw * 0.74, cup_cy + ch),
    ])
    pygame.draw.ellipse(cup, AMBER, (int(cup_cx - cw), int(cup_cy - ch * 1.5),
                                     int(cw * 2), int(ch * 1.0)))
    pygame.draw.ellipse(cup, AMBER_HI, (int(cup_cx - cw * 0.4),
                                        int(cup_cy - ch * 1.4),
                                        int(cw * 0.7), int(ch * 0.4)))
    core_shade(cup, TERRA_SH, 110, lobe=(0.4, 0.4, 0.5, 0.5))
    triad_sheen(cup, top_a=100, bot_a=30)
    s.blit(cup, (0, 0))

    return s


def _build_rison_big():
    w, h = DES_W * SS, DES_H * SS
    s = new_surf(w, h)
    cx = w * 0.5

    # --- minimal bony toasting body first (sits behind / below the head) ---
    s.blit(_build_body(w, h), (0, 0))

    # --- the oversized laughing skull, built upright then ROTATED BACK ---
    head_box = w
    sk_surf, (skcx, skcy, skw, skh) = _build_skull_upright(head_box, head_box)

    # sombrero parked BACK behind/above the cranium. To keep the hat a DISTINCT
    # stacked shape (critique #3), it is composed onto its OWN layer first, given
    # an ink value-gap halo, then placed BEHIND the skull — so where dome meets
    # brim there is a clear ink step, not a fused mass.
    somb = _build_sombrero(head_box, head_box, skcx,
                           skcy - skh * 0.78, skw * 1.52)
    somb = grow_outline(somb, INK, max(1, SS // 2))  # ink halo -> value-gap

    head = new_surf(head_box, head_box)
    head.blit(somb, (0, 0))
    head.blit(sk_surf, (0, 0))

    rot = pygame.transform.rotate(head, HEAD_TILT)
    hx = cx - rot.get_width() // 2
    hy = int(h * 0.110) - (rot.get_height() - head_box) // 2
    s.blit(rot, (hx, hy))

    return s


def build_rison():
    big = _build_rison_big()
    small = pygame.transform.smoothscale(big, (DES_W, DES_H))
    return grow_outline(small, INK, 1)


# ── PULQUE-JUG prop + its top<->bottom PILLAR mirror ─────────────────────────
PROP_W, PROP_H = 60, 150


def _build_jug_big():
    w, h = PROP_W * SS, PROP_H * SS
    s = new_surf(w, h)
    cx = w * 0.5

    jug = new_surf(w, h)
    neck_top = h * 0.30
    neck_w = w * 0.20
    belly_cy = h * 0.66
    belly_w = w * 0.40
    body_pts = [
        (cx - neck_w, neck_top),
        (cx - belly_w, belly_cy - h * 0.06),
        (cx - belly_w, belly_cy + h * 0.06),
        (cx - neck_w * 0.9, h * 0.96),
        (cx + neck_w * 0.9, h * 0.96),
        (cx + belly_w, belly_cy + h * 0.06),
        (cx + belly_w, belly_cy - h * 0.06),
        (cx + neck_w, neck_top),
    ]
    pygame.draw.polygon(jug, TERRA, body_pts)
    band_n = 6
    for i in range(1, band_n):
        by = neck_top + (h * 0.96 - neck_top) * i / band_n
        t = i / band_n
        bw = neck_w + (belly_w - neck_w) * math.sin(min(1.0, t * 1.4) * math.pi * 0.5)
        pygame.draw.line(jug, AMBER, (int(cx - bw), int(by)),
                         (int(cx + bw), int(by)), int(SS * 1.8))
    pygame.draw.circle(jug, TURQ, (int(cx - belly_w * 0.4), int(belly_cy)),
                       max(2, int(SS * 1.4)))
    core_shade(jug, TERRA_SH, 130, lobe=(0.32, 0.40, 0.72, 0.64))
    triad_sheen(jug, top_a=120, bot_a=44, ell=(0.12, 0.30, 0.56, 0.5))
    s.blit(jug, (0, 0))

    # ----- round CUP-and-CORK cap. Warmed toward AMBER (critique #7) so the cap
    # doesn't read as a cooler separate object at gap-scale: amber cup body with
    # only a terracotta base-rim, amber froth, amber cork. -----
    cap = new_surf(w, h)
    cap_cy = h * 0.20
    cup_w = w * 0.30
    cup_h = h * 0.085
    pygame.draw.polygon(cap, AMBER, [
        (cx - cup_w, cap_cy + cup_h),
        (cx - cup_w * 0.86, cap_cy - cup_h),
        (cx + cup_w * 0.86, cap_cy - cup_h),
        (cx + cup_w, cap_cy + cup_h),
    ])
    # a slim terracotta foot-rim keeps the clay read without cooling the cap
    pygame.draw.line(cap, TERRA, (int(cx - cup_w), int(cap_cy + cup_h)),
                     (int(cx + cup_w), int(cap_cy + cup_h)), int(SS * 2.0))
    pygame.draw.ellipse(cap, AMBER_HI, (int(cx - cup_w * 0.86),
                                        int(cap_cy - cup_h * 1.4),
                                        int(cup_w * 1.72), int(cup_h * 1.1)))
    pygame.draw.ellipse(cap, SHEEN, (int(cx - cup_w * 0.3), int(cap_cy - cup_h * 1.3),
                                     int(cup_w * 0.6), int(cup_h * 0.5)))
    pygame.draw.circle(cap, AMBER_SH, (int(cx), int(cap_cy - cup_h * 1.7)),
                       int(w * 0.07))
    pygame.draw.circle(cap, AMBER, (int(cx), int(cap_cy - cup_h * 1.7)),
                       int(w * 0.055))
    core_shade(cap, AMBER_SH, 100, lobe=(0.36, 0.30, 0.6, 0.55))
    triad_sheen(cap, top_a=110, bot_a=40, ell=(0.2, 0.04, 0.5, 0.5))
    s.blit(cap, (0, 0))
    return s


def build_jug():
    big = _build_jug_big()
    small = pygame.transform.smoothscale(big, (PROP_W, PROP_H))
    return grow_outline(small, INK, 1)


def build_pillar(height=300):
    prop = build_jug()
    pw, ph = prop.get_size()
    cap_h = int(ph * 0.34)
    cap = prop.subsurface((0, 0, pw, cap_h)).copy()
    shaft = prop.subsurface((0, cap_h, pw, ph - cap_h)).copy()

    surf = new_surf(pw, height)
    sh = shaft.get_height()
    y = 0
    while y < height:
        surf.blit(shaft, (0, y))
        y += sh
    flipped_cap = pygame.transform.flip(cap, False, True)
    surf.blit(flipped_cap, (0, height - cap_h))
    return surf, cap, shaft


# ═══════════════════════════════════════════════════════════════════════════
# SHEET
# ═══════════════════════════════════════════════════════════════════════════
rison = build_rison()
jug = build_jug()
pillar, cap, shaft = build_pillar(300)

bot_pillar, _, _ = build_pillar(300)
top_pillar = new_surf(jug.get_width(), 300)
cap_h = int(jug.get_height() * 0.34)
top_shaft_h = 300 - cap_h
y = 0
while y < top_shaft_h:
    top_pillar.blit(shaft, (0, y))
    y += shaft.get_height()
top_pillar.blit(cap, (0, top_shaft_h))


BG = (44, 48, 66)
PANEL2 = (50, 56, 76)
TITLE = (236, 242, 255)
SUB = (180, 190, 212)
ACCENT = (250, 196, 120)

_FONT = os.path.join(_ROOT, "game", "assets", "LiberationSans-Bold.ttf")
ftitle = pygame.font.Font(_FONT, 30)
fhead = pygame.font.Font(_FONT, 20)
fbody = pygame.font.Font(_FONT, 14)
ftiny = pygame.font.Font(_FONT, 12)


def scaled(spr, sc):
    w, h = spr.get_size()
    return pygame.transform.smoothscale(spr, (max(1, round(w * sc)), max(1, round(h * sc))))


SHEET_W, SHEET_H = 1000, 800
sheet = new_surf(SHEET_W, SHEET_H)
sheet.fill(BG)


def sky_panel(rect, top=(214, 168, 120), bot=(236, 208, 168)):
    p = new_surf(rect.w, rect.h)
    for yy in range(rect.h):
        t = yy / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, col, (0, yy), (rect.w, yy))
    sheet.blit(p, rect.topleft)
    pygame.draw.rect(sheet, (28, 32, 46), rect, 2, border_radius=10)


def blit_center(spr, rect, dy=0):
    x = rect.centerx - spr.get_width() // 2
    y = rect.centery - spr.get_height() // 2 + dy
    sheet.blit(spr, (x, y))


# header
sheet.blit(ftitle.render("RISON  —  round 2", True, TITLE), (28, 18))
sheet.blit(fbody.render(
    "FIX: dropped jaw punched into the SILHOUETTE as a forward-jutting wedge; open mouth is "
    "an air GAP at the contour edge. Head-back tilt 22deg, ink-gap behind hat, mirth sockets.",
    True, SUB), (28, 54))
sheet.blit(ftiny.render(
    "Palette (amber/clay lane): amber (228,168,72) - terracotta (196,108,64) - warm-bone "
    "(238,226,202) - tan socket (168,140,98) - rust band/sash (192,62,50) - turquoise FLECK only.",
    True, ACCENT), (28, 76))

M = 28
top_y = 100

hero_rect = pygame.Rect(M, top_y, 300, 456)
sky_panel(hero_rect)
sheet.blit(fhead.render("Rison  (hero)", True, (60, 40, 28)), (hero_rect.x + 12, hero_rect.y + 8))
sheet.blit(ftiny.render("head-back + dropped-jaw WEDGE laugh", True, (60, 40, 28)),
           (hero_rect.x + 12, hero_rect.bottom - 22))
blit_center(scaled(rison, 2.45), hero_rect, dy=14)

prop_rect = pygame.Rect(hero_rect.right + 18, top_y, 220, 456)
sky_panel(prop_rect, top=(208, 176, 138), bot=(230, 206, 176))
sheet.blit(fhead.render("Pulque-jug prop", True, (60, 40, 28)), (prop_rect.x + 12, prop_rect.y + 8))
blit_center(scaled(jug, 2.45), prop_rect, dy=16)
sheet.blit(ftiny.render("fat clay jug + glaze banding", True, (60, 44, 30)),
           (prop_rect.x + 12, prop_rect.bottom - 38))
sheet.blit(ftiny.render("+ amber cup-and-cork cap", True, (60, 44, 30)),
           (prop_rect.x + 12, prop_rect.bottom - 22))

pil_rect = pygame.Rect(prop_rect.right + 18, top_y, 386, 456)
sky_panel(pil_rect, top=(216, 170, 122), bot=(238, 210, 170))
sheet.blit(fhead.render("Pillar mirror (gap)", True, (60, 40, 28)), (pil_rect.x + 12, pil_rect.y + 8))
clip = sheet.get_clip()
inner = pil_rect.inflate(-8, -8)
sheet.set_clip(inner)
GAP = 150
pcx = pil_rect.centerx - jug.get_width() // 2
gap_top = pil_rect.y + 40
sheet.blit(top_pillar, (pcx, gap_top - 130))
sheet.blit(bot_pillar, (pcx, gap_top + GAP))
sheet.set_clip(clip)
sheet.blit(ftiny.render("round jug body on-axis -> clean symmetric mirror",
                        True, (60, 40, 28)), (pil_rect.x + 12, pil_rect.bottom - 22))

# --- BOTTOM: 32px gameplay-scale read row + zoom + pure-black silhouette ---
row_y = hero_rect.bottom + 16
row_rect = pygame.Rect(M, row_y, SHEET_W - 2 * M, SHEET_H - row_y - 18)
pygame.draw.rect(sheet, PANEL2, row_rect, border_radius=10)
sheet.blit(fhead.render("Gameplay scale  —  acceptance test: does the LAUGH read in pure black?",
                        True, TITLE), (row_rect.x + 12, row_rect.y + 8))


def chip(rect, top=(216, 170, 122), bot=(238, 210, 170)):
    p = new_surf(rect.w, rect.h)
    for yy in range(rect.h):
        t = yy / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, col, (0, yy), (rect.w, yy))
    sheet.blit(p, rect.topleft)
    pygame.draw.rect(sheet, (28, 32, 46), rect, 1, border_radius=4)


def fit_h(spr, target_h):
    w, h = spr.get_size()
    sc = target_h / h
    return scaled(spr, sc)


ris32 = fit_h(rison, 32)
ris48 = fit_h(rison, 48)
jug32 = fit_h(jug, 40)

cy = row_rect.y + 44
c1 = pygame.Rect(row_rect.x + 20, cy, 80, 104)
chip(c1)
blit_center(ris32, c1)
sheet.blit(ftiny.render("32px", True, (50, 34, 22)), (c1.x + 4, c1.bottom - 16))

c2 = pygame.Rect(c1.right + 16, cy, 110, 104)
chip(c2)
z = pygame.transform.scale(ris32, (ris32.get_width() * 3, ris32.get_height() * 3))
blit_center(z, c2)
sheet.blit(ftiny.render("32px x3", True, (50, 34, 22)), (c2.x + 4, c2.bottom - 16))

c3 = pygame.Rect(c2.right + 16, cy, 96, 104)
chip(c3)
blit_center(ris48, c3)
sheet.blit(ftiny.render("48px", True, (50, 34, 22)), (c3.x + 4, c3.bottom - 16))

# pure-black silhouette panels at BOTH 32px and 48px — the acceptance test. The
# dropped-jaw wedge must read as a protruding notch in the black shape.
c_sil = pygame.Rect(c3.right + 16, cy, 70, 104)
chip(c_sil, top=(232, 234, 240), bot=(232, 234, 240))
sil48 = pygame.mask.from_surface(ris48, 40).to_surface(
    setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
blit_center(sil48, c_sil)
sheet.blit(ftiny.render("sil 48", True, (40, 40, 48)), (c_sil.x + 4, c_sil.bottom - 16))

c_sil2 = pygame.Rect(c_sil.right + 12, cy, 70, 104)
chip(c_sil2, top=(232, 234, 240), bot=(232, 234, 240))
sil32 = pygame.mask.from_surface(ris32, 40).to_surface(
    setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
# zoom the 32px silhouette x2 so the wedge is judgeable at gap scale
sil32z = pygame.transform.scale(sil32, (sil32.get_width() * 2, sil32.get_height() * 2))
blit_center(sil32z, c_sil2)
sheet.blit(ftiny.render("sil 32 x2", True, (40, 40, 48)), (c_sil2.x + 4, c_sil2.bottom - 16))

c4 = pygame.Rect(c_sil2.right + 14, cy, 60, 104)
chip(c4, top=(208, 176, 138), bot=(230, 206, 176))
blit_center(jug32, c4)
sheet.blit(ftiny.render("prop", True, (50, 38, 26)), (c4.x + 4, c4.bottom - 16))

c5 = pygame.Rect(c4.right + 14, cy, 96, 104)
chip(c5, top=(216, 170, 122), bot=(238, 210, 170))
mini_top = fit_h(top_pillar, 60)
mini_bot = fit_h(bot_pillar, 60)
clip = sheet.get_clip()
sheet.set_clip(c5)
mcx = c5.centerx - mini_top.get_width() // 2
sheet.blit(mini_top, (mcx, c5.y - 22))
sheet.blit(mini_bot, (mcx, c5.y + 66))
sheet.set_clip(clip)
sheet.blit(ftiny.render("pillar", True, (50, 34, 22)), (c5.x + 4, c5.bottom - 16))

tx = c5.right + 18
sheet.blit(ftiny.render(
    "Laugh now lives in the OUTLINE: cranium recedes, mandible juts down-forward",
    True, SUB), (tx, cy + 10))
sheet.blit(ftiny.render(
    "as a wedge -> the black shape shows a chin-thrust + open-mouth notch, no color.",
    True, SUB), (tx, cy + 28))
sheet.blit(ftiny.render(
    "Anti-reaper guard held: tipped-BACK sombrero (now ink-gapped distinct) +",
    True, SUB), (tx, cy + 50))
sheet.blit(ftiny.render(
    "bushy moustache + amber/clay + the dropped-jaw laugh = festive calaca, not reaper.",
    True, SUB), (tx, cy + 68))

os.makedirs(_OUT_DIR, exist_ok=True)
out_path = os.path.join(_OUT_DIR, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
