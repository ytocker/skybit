"""RISON  —  round 1 review sheet (Mariachi warm-skeleton family, locked5 brief).

Concept G: "El Rison" — a cantina merrymaker calaca whose whole personality
lives in the SKULL. Head thrown back in a huge belly-laugh, jaw cracked FULLY
open, sockets crinkled with mirth, a sombrero tipped BACK off the brow. The
lead facet is FACIAL CHARACTER / EMOTION — the dropped-open-jaw laugh carries
the entire 32px read, so the head is the dominant mass and the body is minimal
and bony (one bone hand raising a clay pulque cup, the other slapping a knee).

ANTI-REAPER GUARD (AD hard pin, non-negotiable): an oversized expressive skull
risks reading as the cool grim batch-1 reapers, so four warm tells are pinned
in — the tipped-BACK sombrero, the painted MOUSTACHE, the warm AMBER/CLAY
palette, and the dropped-open-jaw LAUGH geometry. Never a bare neutral cranium.

PALETTE is the AMBER/CLAY lane (distinct from Jinete's ochre): the clay HERO
mass is amber + terracotta; warm bone skull; deep tan-bone socket shade for
expressive sockets; rust sombrero-band + sash accent; turquoise reduced to a
TINY jug-glaze fleck only (no turquoise body mass, so it stays clear of the
turquoise-mass concepts).

House grammar: chibi proportions, FLAT saturated fills + hard 1-2px ink
keylines, form via the dark-core -> flat-fill -> top-left rim-sheen TRIAD (never
soft gradient), a 1px outline grown from the alpha mask, supersample ->
smoothscale. Scary-CUTE, festive — never grim.

Run headless (SDL_VIDEODRIVER=dummy). Writes round_1.png beside this script.
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
# The head is the dominant mass: an OVERSIZED skull tilted back in a laugh, so
# the design box is head-heavy. A small bony toasting body hangs below.
DES_W, DES_H = 116, 150

# Head-back laugh tilt — the whole skull is built upright then rotated back so
# the chin lifts skyward (the belly-laugh "throwing the head back" read). The
# dropped jaw swings open from that tilted skull.
HEAD_TILT = 13  # deg, head leans back to the wearer's right (laughing upward)


def _build_skull_upright(w, h):
    """The oversized laughing skull on its own surface, drawn upright so it can
    be rotated back as a unit. Cranium + crinkled sockets + a FULLY dropped jaw
    whose open negative space is the focal, + a bushy moustache."""
    s = new_surf(w, h)
    cx = w * 0.5

    # ----- CRANIUM: a wide rounded dome (big-head chibi) -----
    cran = new_surf(w, h)
    cr_cy = h * 0.40
    cr_w = w * 0.40
    cr_h = h * 0.36
    pygame.draw.ellipse(cran, BONE, (int(cx - cr_w), int(cr_cy - cr_h),
                                     int(cr_w * 2), int(cr_h * 2)))
    # cheekbones flare the lower cranium so the jaw can swing wide beneath
    pygame.draw.ellipse(cran, BONE,
                        (int(cx - cr_w * 0.95), int(cr_cy + cr_h * 0.10),
                         int(cr_w * 1.9), int(cr_h * 1.05)))
    core_shade(cran, BONE_SH, 120, lobe=(0.34, 0.42, 0.66, 0.62))
    triad_sheen(cran, top_a=140, bot_a=44, ell=(0.10, 0.06, 0.62, 0.52))
    s.blit(cran, (0, 0))

    # ----- DROPPED JAW: a hinged mandible swung FULLY open below the cheeks.
    # The dark open MOUTH cavity between cranium and jaw is the focal negative
    # space (the laugh) — drawn as an ink void with tooth rows + a tongue tick.
    jaw_top = cr_cy + cr_h * 0.66      # hinge line (mouth opening top)
    mouth_cy = cr_cy + cr_h * 1.02     # centre of the open cavity
    jaw = new_surf(w, h)

    # 1) the open MOUTH cavity — a big rounded ink void (the dropped-jaw gap)
    mw = cr_w * 0.74
    mh = cr_h * 0.62
    pygame.draw.ellipse(jaw, INK, (int(cx - mw), int(jaw_top),
                                   int(mw * 2), int(mh * 2)))

    # 2) the lower MANDIBLE (a U of bone hung beneath the cavity) — this is what
    # makes the jaw read as DROPPED open, not a closed grin.
    man_pts = [
        (cx - mw * 1.06, jaw_top + mh * 0.55),
        (cx - mw * 0.92, jaw_top + mh * 1.55),
        (cx - mw * 0.40, jaw_top + mh * 2.05),
        (cx + mw * 0.40, jaw_top + mh * 2.05),
        (cx + mw * 0.92, jaw_top + mh * 1.55),
        (cx + mw * 1.06, jaw_top + mh * 0.55),
        (cx + mw * 0.80, jaw_top + mh * 0.92),
        (cx + mw * 0.34, jaw_top + mh * 1.30),
        (cx - mw * 0.34, jaw_top + mh * 1.30),
        (cx - mw * 0.80, jaw_top + mh * 0.92),
    ]
    pygame.draw.polygon(jaw, BONE, man_pts)
    core_shade(jaw, BONE_SH, 110, lobe=(0.30, 0.58, 0.66, 0.46))
    triad_sheen(jaw, top_a=110, bot_a=36, ell=(0.18, 0.62, 0.50, 0.26))
    s.blit(jaw, (0, 0))

    # 3) UPPER tooth row hanging from the cranium into the cavity + LOWER tooth
    # row standing on the mandible. Gapped blocks read as a laugh, not a grimace.
    teeth = new_surf(w, h)
    tcount = 6
    tw = (mw * 1.5) / tcount
    for i in range(tcount):
        tx = cx - mw * 0.75 + tw * i + tw * 0.12
        # upper teeth (drop down from the cranium edge)
        pygame.draw.rect(teeth, BONE,
                         (int(tx), int(jaw_top + mh * 0.04),
                          int(tw * 0.76), int(mh * 0.52)))
        # lower teeth (rise up off the mandible top)
        pygame.draw.rect(teeth, BONE,
                         (int(tx), int(jaw_top + mh * 1.04),
                          int(tw * 0.76), int(mh * 0.44)))
    triad_sheen(teeth, top_a=120, bot_a=30, ell=(0.20, 0.55, 0.5, 0.3))
    s.blit(teeth, (0, 0))

    # 4) a curled TONGUE tick deep in the cavity (warm terracotta) — a tiny
    # cantina-merry tell that the mouth is wide in a holler, not just bone.
    tongue = new_surf(w, h)
    pygame.draw.ellipse(tongue, TERRA,
                        (int(cx - mw * 0.34), int(mouth_cy - mh * 0.02),
                         int(mw * 0.68), int(mh * 0.50)))
    pygame.draw.ellipse(tongue, TERRA_HI,
                        (int(cx - mw * 0.18), int(mouth_cy + mh * 0.02),
                         int(mw * 0.30), int(mh * 0.18)))
    s.blit(tongue, (0, 0))

    # ----- EYE SOCKETS: deep tan-bone crescents CRINKLED with mirth. Drawn as
    # squinted half-moons (laugh-scrunch) with ink laugh-line ticks fanning from
    # the outer corners — the "eyes shut laughing" read. -----
    face = new_surf(w, h)
    eye_y = cr_cy - cr_h * 0.04
    eye_dx = cr_w * 0.50
    eye_r = cr_w * 0.30
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        # deep tan-bone socket bowl
        pygame.draw.circle(face, TANBONE, (int(ex), int(eye_y)), int(eye_r))
        pygame.draw.circle(face, INK, (int(ex), int(eye_y)), int(eye_r), max(2, SS))
        # the mirth CRESCENT: bone fills the lower half of the socket so the eye
        # reads squeezed-shut-laughing (a happy upward arc, not a hollow stare)
        pygame.draw.polygon(face, BONE, [
            (ex - eye_r, eye_y),
            (ex + eye_r, eye_y),
            (ex + eye_r * 0.7, eye_y + eye_r * 0.95),
            (ex - eye_r * 0.7, eye_y + eye_r * 0.95),
        ])
        # a happy curved squint stroke across the socket
        pygame.draw.arc(face, INK,
                        (int(ex - eye_r * 0.9), int(eye_y - eye_r * 0.5),
                         int(eye_r * 1.8), int(eye_r * 1.4)),
                        math.radians(186), math.radians(354), max(2, SS))
        # laugh-line ticks fanning from the OUTER corner (crinkle of mirth)
        ox = ex + sgn * eye_r * 1.05
        for k in range(3):
            a = math.radians(-30 + k * 26)
            pygame.draw.line(face, INK, (int(ox), int(eye_y - eye_r * 0.2)),
                             (int(ox + sgn * math.cos(a) * eye_r * 0.7),
                              int(eye_y - eye_r * 0.2 - math.sin(a) * eye_r * 0.7)),
                             max(2, SS // 2 + 1))

    # ----- NOSE: a small inverted-heart bone void above the moustache -----
    ny = cr_cy + cr_h * 0.44
    pygame.draw.polygon(face, INK, [
        (int(cx), int(ny + cr_h * 0.18)),
        (int(cx - cr_w * 0.12), int(ny - cr_h * 0.02)),
        (int(cx + cr_w * 0.12), int(ny - cr_h * 0.02))])
    s.blit(face, (0, 0))

    # ----- BUSHY PAINTED MOUSTACHE bouncing over the open jaw (anti-reaper
    # tell). Two fat upcurled handlebar lobes in rust, riding above the teeth. --
    mous = new_surf(w, h)
    mo_cy = jaw_top - mh * 0.06
    for sgn in (-1, 1):
        # fat lobe body
        lobe_pts = []
        for i in range(13):
            t = i / 12
            ang = math.pi * t
            rx = cx + sgn * (cr_w * 0.10 + math.cos(ang) * cr_w * 0.46)
            ry = mo_cy - math.sin(ang) * mh * 0.30 + (1 - t) * mh * 0.04
            lobe_pts.append((rx, ry))
        # close along a lower edge to give the moustache thickness
        for i in range(13):
            t = (12 - i) / 12
            ang = math.pi * t
            rx = cx + sgn * (cr_w * 0.10 + math.cos(ang) * cr_w * 0.46)
            ry = mo_cy - math.sin(ang) * mh * 0.30 + (1 - t) * mh * 0.04 + mh * 0.22
            lobe_pts.append((rx, ry))
        pygame.draw.polygon(mous, RUST, lobe_pts)
        # upcurled tip flick (handlebar) at the outer end
        tipx = cx + sgn * cr_w * 0.96
        pygame.draw.circle(mous, RUST, (int(tipx), int(mo_cy - mh * 0.04)),
                           int(cr_w * 0.10))
        pygame.draw.circle(mous, RUST, (int(tipx + sgn * cr_w * 0.05),
                                        int(mo_cy - mh * 0.20)),
                           int(cr_w * 0.07))
    core_shade(mous, RUST_SH, 120, lobe=(0.20, 0.50, 0.62, 0.40))
    triad_sheen(mous, top_a=90, bot_a=24, ell=(0.16, 0.40, 0.66, 0.30))
    s.blit(mous, (0, 0))

    return s, (cx, cr_cy, cr_w, cr_h)


def _build_sombrero(w, h, cx, brow_y, brim_w):
    """Sombrero shoved BACK off the forehead — the brim sits BEHIND/above the
    head (not shading the face), so the whole laughing face shows. Amber crown
    with a rust hatband + a tiny turquoise glaze fleck on the band."""
    s = new_surf(w, h)

    # wide upswept brim, parked high and back behind the cranium
    brim_cy = brow_y
    brim_h = h * 0.045
    pygame.draw.ellipse(s, AMBER_SH,
                        (int(cx - brim_w), int(brim_cy - brim_h * 0.2),
                         int(brim_w * 2), int(brim_h * 2.1)))
    pygame.draw.ellipse(s, AMBER,
                        (int(cx - brim_w), int(brim_cy - brim_h),
                         int(brim_w * 2), int(brim_h * 2)))
    # gold-toned upturned brim rim
    pygame.draw.ellipse(s, AMBER_HI,
                        (int(cx - brim_w), int(brim_cy - brim_h),
                         int(brim_w * 2), int(brim_h * 2)), max(2, SS))
    # tall conical crown rising clearly behind/above the cranium dome
    crown_w = brim_w * 0.52
    crown_h = h * 0.26
    crown_cy = brim_cy - crown_h * 0.72
    pygame.draw.polygon(s, AMBER, [
        (cx - crown_w, brim_cy + brim_h * 0.2),
        (cx - crown_w * 0.46, crown_cy - crown_h),
        (cx + crown_w * 0.46, crown_cy - crown_h),
        (cx + crown_w, brim_cy + brim_h * 0.2),
    ])
    # rounded crown peak
    pygame.draw.ellipse(s, AMBER,
                        (int(cx - crown_w * 0.5), int(crown_cy - crown_h * 1.1),
                         int(crown_w), int(crown_h * 0.5)))
    core_shade(s, AMBER_SH, 120, lobe=(0.30, 0.30, 0.70, 0.66))
    triad_sheen(s, top_a=110, bot_a=40, ell=(0.12, 0.06, 0.6, 0.5))

    # rust HATBAND around the crown base + tiny turquoise glaze fleck
    band = new_surf(w, h)
    band_y = crown_cy + crown_h * 0.02
    pygame.draw.line(band, RUST, (int(cx - crown_w * 0.86), int(band_y)),
                     (int(cx + crown_w * 0.86), int(band_y)), int(SS * 2.4))
    # tiny turquoise fleck on the band (the ONLY cool note — kept minimal)
    pygame.draw.circle(band, TURQ, (int(cx + crown_w * 0.18), int(band_y)),
                       max(2, int(SS * 1.0)))
    s.blit(band, (0, 0))
    return s


def _build_body(w, h):
    """Minimal bony toasting body below the head: a small ribby torso, one bone
    hand raising a CLAY PULQUE CUP (the character + asymmetry tell), the other
    slapping a femur knee. Kept small so the head stays the dominant mass."""
    s = new_surf(w, h)
    cx = w * 0.5

    # ----- short rib torso (warm bone) -----
    torso = new_surf(w, h)
    t_cy = h * 0.78
    t_w = w * 0.17
    pygame.draw.polygon(torso, BONE, [
        (cx - t_w, t_cy - h * 0.10),
        (cx + t_w, t_cy - h * 0.10),
        (cx + t_w * 0.74, t_cy + h * 0.13),
        (cx - t_w * 0.74, t_cy + h * 0.13),
    ])
    # spine + 3 rib bands (exposed ribby read)
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
    # rust SASH slung across the torso (warm accent that ties to the hatband)
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

    # ----- RIGHT arm raised high TOASTING a clay pulque cup -----
    arm_r = new_surf(w, h)
    sh2_x, sh2_y = cx + t_w * 0.9, t_cy - h * 0.07
    el_x, el_y = cx + t_w * 1.7, t_cy - h * 0.02
    ha_x, ha_y = cx + t_w * 1.55, t_cy - h * 0.20
    pygame.draw.lines(arm_r, BONE, False,
                      [(int(sh2_x), int(sh2_y)), (int(el_x), int(el_y)),
                       (int(ha_x), int(ha_y))], int(SS * 2.6))
    core_shade(arm_r, BONE_SH, 100, lobe=(0.45, 0.45, 0.5, 0.4))
    triad_sheen(arm_r, top_a=90, bot_a=20)
    s.blit(arm_r, (0, 0))

    # the CLAY PULQUE CUP in the raised hand (terracotta jar with amber froth)
    cup = new_surf(w, h)
    cup_cx, cup_cy = ha_x, ha_y - h * 0.05
    cw = w * 0.07
    ch = h * 0.075
    pygame.draw.polygon(cup, TERRA, [
        (cup_cx - cw, cup_cy - ch),
        (cup_cx + cw, cup_cy - ch),
        (cup_cx + cw * 0.74, cup_cy + ch),
        (cup_cx - cw * 0.74, cup_cy + ch),
    ])
    # amber pulque froth brimming over the rim
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

    # --- the oversized laughing skull, built upright then ROTATED BACK as a
    # unit so the chin lifts skyward (head thrown back in the belly-laugh) ---
    head_box = w  # square head canvas for clean rotation about its centre
    sk_surf, (skcx, skcy, skw, skh) = _build_skull_upright(head_box, head_box)

    # the sombrero is shoved BACK behind/above the cranium (brim doesn't shade
    # the face) — composed onto the head canvas BEHIND the skull so the whole
    # laughing face stays clear. The brim is wide + the crown rises clearly
    # above the dome so the sombrero is unmistakable (the anti-reaper tell).
    somb = _build_sombrero(head_box, head_box, skcx,
                           skcy - skh * 0.74, skw * 1.55)
    head = new_surf(head_box, head_box)
    head.blit(somb, (0, 0))
    head.blit(sk_surf, (0, 0))

    rot = pygame.transform.rotate(head, HEAD_TILT)
    # seat the rotated head high on the canvas, centred horizontally; its chin
    # overlaps the torso top so head + body are one continuous silhouette.
    hx = cx - rot.get_width() // 2
    hy = int(h * 0.135) - (rot.get_height() - head_box) // 2
    s.blit(rot, (hx, hy))

    return s


def build_rison():
    big = _build_rison_big()
    small = pygame.transform.smoothscale(big, (DES_W, DES_H))
    return grow_outline(small, INK, 1)


# ── PULQUE-JUG prop + its top<->bottom PILLAR mirror ─────────────────────────
# A fat-bellied clay jug (repeatable shaft, glaze banding) topped by a round
# cup-and-cork (gap-edge cap). Round + on-axis for a clean symmetric mirror.
PROP_W, PROP_H = 60, 150


def _build_jug_big():
    w, h = PROP_W * SS, PROP_H * SS
    s = new_surf(w, h)
    cx = w * 0.5

    # ----- fat-bellied JUG body (the repeatable pillar shaft) -----
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
    # AMBER glaze banding (the repeatable shaft tile rhythm)
    band_n = 6
    for i in range(1, band_n):
        by = neck_top + (h * 0.96 - neck_top) * i / band_n
        # width follows the belly bulge so bands hug the form
        t = i / band_n
        bw = neck_w + (belly_w - neck_w) * math.sin(min(1.0, t * 1.4) * math.pi * 0.5)
        pygame.draw.line(jug, AMBER, (int(cx - bw), int(by)),
                         (int(cx + bw), int(by)), int(SS * 1.8))
    # a tiny turquoise glaze fleck on the belly (the only cool note)
    pygame.draw.circle(jug, TURQ, (int(cx - belly_w * 0.4), int(belly_cy)),
                       max(2, int(SS * 1.4)))
    core_shade(jug, TERRA_SH, 130, lobe=(0.32, 0.40, 0.72, 0.64))
    triad_sheen(jug, top_a=120, bot_a=44, ell=(0.12, 0.30, 0.56, 0.5))
    s.blit(jug, (0, 0))

    # ----- round CUP-and-CORK cap (gap-edge cap) — sits on-axis, symmetric ----
    cap = new_surf(w, h)
    cap_cy = h * 0.20
    # a stout clay cup mouth
    cup_w = w * 0.30
    cup_h = h * 0.085
    pygame.draw.polygon(cap, TERRA, [
        (cx - cup_w, cap_cy + cup_h),
        (cx - cup_w * 0.86, cap_cy - cup_h),
        (cx + cup_w * 0.86, cap_cy - cup_h),
        (cx + cup_w, cap_cy + cup_h),
    ])
    # amber pulque froth filling the cup mouth
    pygame.draw.ellipse(cap, AMBER, (int(cx - cup_w * 0.86), int(cap_cy - cup_h * 1.4),
                                     int(cup_w * 1.72), int(cup_h * 1.1)))
    pygame.draw.ellipse(cap, AMBER_HI, (int(cx - cup_w * 0.3), int(cap_cy - cup_h * 1.3),
                                        int(cup_w * 0.6), int(cup_h * 0.5)))
    # round cork bobbing on top (the finial)
    pygame.draw.circle(cap, AMBER_SH, (int(cx), int(cap_cy - cup_h * 1.7)),
                       int(w * 0.07))
    pygame.draw.circle(cap, AMBER, (int(cx), int(cap_cy - cup_h * 1.7)),
                       int(w * 0.055))
    core_shade(cap, TERRA_SH, 110, lobe=(0.36, 0.30, 0.6, 0.6))
    triad_sheen(cap, top_a=110, bot_a=40, ell=(0.2, 0.04, 0.5, 0.5))
    s.blit(cap, (0, 0))
    return s


def build_jug():
    big = _build_jug_big()
    small = pygame.transform.smoothscale(big, (PROP_W, PROP_H))
    return grow_outline(small, INK, 1)


def build_pillar(height=300):
    """Mirror the jug top<->bottom into a repeatable pillar: a tileable jug
    glaze-banded SHAFT with a round cup-and-cork gap-edge CAP at the gap."""
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
top_pillar.blit(cap, (0, top_shaft_h))   # cup blooms DOWN into the gap


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


SHEET_W, SHEET_H = 1000, 780
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
sheet.blit(ftitle.render("RISON  —  round 1", True, TITLE), (28, 18))
sheet.blit(fbody.render(
    "Cantina merrymaker calaca: head thrown BACK in a belly-laugh, jaw cracked FULLY open "
    "(open-mouth void = focal), sombrero shoved BACK, bushy moustache, toasting a clay cup.",
    True, SUB), (28, 54))
sheet.blit(ftiny.render(
    "Palette (amber/clay lane): amber (228,168,72) - terracotta (196,108,64) - warm-bone "
    "(238,226,202) - tan socket (168,140,98) - rust band/sash (192,62,50) - turquoise FLECK only.",
    True, ACCENT), (28, 76))

M = 28
top_y = 100

hero_rect = pygame.Rect(M, top_y, 300, 446)
sky_panel(hero_rect)
sheet.blit(fhead.render("Rison  (hero)", True, (60, 40, 28)), (hero_rect.x + 12, hero_rect.y + 8))
sheet.blit(ftiny.render("head-back + dropped-open-jaw laugh", True, (60, 40, 28)),
           (hero_rect.x + 12, hero_rect.bottom - 22))
blit_center(scaled(rison, 2.45), hero_rect, dy=14)

prop_rect = pygame.Rect(hero_rect.right + 18, top_y, 220, 446)
sky_panel(prop_rect, top=(208, 176, 138), bot=(230, 206, 176))
sheet.blit(fhead.render("Pulque-jug prop", True, (60, 40, 28)), (prop_rect.x + 12, prop_rect.y + 8))
blit_center(scaled(jug, 2.45), prop_rect, dy=16)
sheet.blit(ftiny.render("fat clay jug + glaze", True, (60, 44, 30)),
           (prop_rect.x + 12, prop_rect.bottom - 38))
sheet.blit(ftiny.render("banding + cup-and-cork cap", True, (60, 44, 30)),
           (prop_rect.x + 12, prop_rect.bottom - 22))

pil_rect = pygame.Rect(prop_rect.right + 18, top_y, 386, 446)
sky_panel(pil_rect, top=(216, 170, 122), bot=(238, 210, 170))
sheet.blit(fhead.render("Pillar mirror (gap)", True, (60, 40, 28)), (pil_rect.x + 12, pil_rect.y + 8))
clip = sheet.get_clip()
inner = pil_rect.inflate(-8, -8)
sheet.set_clip(inner)
GAP = 150
pcx = pil_rect.centerx - jug.get_width() // 2
gap_top = pil_rect.y + 38
sheet.blit(top_pillar, (pcx, gap_top - 130))
sheet.blit(bot_pillar, (pcx, gap_top + GAP))
sheet.set_clip(clip)
sheet.blit(ftiny.render("round jug body on-axis -> clean symmetric mirror",
                        True, (60, 40, 28)), (pil_rect.x + 12, pil_rect.bottom - 22))

# --- BOTTOM: 32px gameplay-scale read row + zoom + pure-black silhouette ---
row_y = hero_rect.bottom + 16
row_rect = pygame.Rect(M, row_y, SHEET_W - 2 * M, SHEET_H - row_y - 20)
pygame.draw.rect(sheet, PANEL2, row_rect, border_radius=10)
sheet.blit(fhead.render("Gameplay scale", True, TITLE), (row_rect.x + 12, row_rect.y + 8))


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
c1 = pygame.Rect(row_rect.x + 20, cy, 80, 100)
chip(c1)
blit_center(ris32, c1)
sheet.blit(ftiny.render("32px", True, (50, 34, 22)), (c1.x + 4, c1.bottom - 16))

c2 = pygame.Rect(c1.right + 16, cy, 110, 100)
chip(c2)
z = pygame.transform.scale(ris32, (ris32.get_width() * 3, ris32.get_height() * 3))
blit_center(z, c2)
sheet.blit(ftiny.render("32px x3", True, (50, 34, 22)), (c2.x + 4, c2.bottom - 16))

c3 = pygame.Rect(c2.right + 16, cy, 96, 100)
chip(c3)
blit_center(ris48, c3)
sheet.blit(ftiny.render("48px", True, (50, 34, 22)), (c3.x + 4, c3.bottom - 16))

# pure-black silhouette panel — proves the head-back dropped-jaw read holds
# with zero hue (the FACIAL-CHARACTER lead facet at gap scale).
c_sil = pygame.Rect(c3.right + 16, cy, 80, 100)
chip(c_sil, top=(232, 234, 240), bot=(232, 234, 240))
inkmask = pygame.mask.from_surface(ris48, 40).to_surface(
    setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
blit_center(inkmask, c_sil)
sheet.blit(ftiny.render("silhouette", True, (40, 40, 48)), (c_sil.x + 4, c_sil.bottom - 16))

c4 = pygame.Rect(c_sil.right + 16, cy, 64, 100)
chip(c4, top=(208, 176, 138), bot=(230, 206, 176))
blit_center(jug32, c4)
sheet.blit(ftiny.render("prop", True, (50, 38, 26)), (c4.x + 4, c4.bottom - 16))

c5 = pygame.Rect(c4.right + 16, cy, 110, 100)
chip(c5, top=(216, 170, 122), bot=(238, 210, 170))
mini_top = fit_h(top_pillar, 60)
mini_bot = fit_h(bot_pillar, 60)
clip = sheet.get_clip()
sheet.set_clip(c5)
mcx = c5.centerx - mini_top.get_width() // 2
sheet.blit(mini_top, (mcx, c5.y - 20))
sheet.blit(mini_bot, (mcx, c5.y + 66))
sheet.set_clip(clip)
sheet.blit(ftiny.render("pillar", True, (50, 34, 22)), (c5.x + 4, c5.bottom - 16))

sheet.blit(ftiny.render(
    "Anti-reaper guard: tipped-BACK sombrero + bushy moustache + amber/clay + the",
    True, SUB), (c5.right + 22, cy + 18))
sheet.blit(ftiny.render(
    "dropped-open-jaw LAUGH geometry keep it clear of the batch-1 grim grinning skulls.",
    True, SUB), (c5.right + 22, cy + 36))
sheet.blit(ftiny.render(
    "Lead facet FACIAL CHARACTER: the open-mouth void carries the read in pure silhouette.",
    True, SUB), (c5.right + 22, cy + 54))
sheet.blit(ftiny.render(
    "Triad: dark-core -> flat amber/bone fill -> top-left sheen; 1px ink keyline.",
    True, SUB), (c5.right + 22, cy + 72))

os.makedirs(_OUT_DIR, exist_ok=True)
out_path = os.path.join(_OUT_DIR, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
