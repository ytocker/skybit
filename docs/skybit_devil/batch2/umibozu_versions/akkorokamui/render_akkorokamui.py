"""Look-dev sheet for the Skybit BOSS — "AKKOROKAMUI" (Umibozu-versions #2).

The akkorokamui: a vast sunset-red kraken-DEITY rising from a dusk sea. Cuted
down to the Leyak/Umibozu epic lineage — a rounded MANTLE-HEAD mass from which a
bloom of nine FAT curling arms unfurls. One calm cyclopean gold eye + a tiny
ink beak: a benevolent little sea-god waving hello with arms that sink ships.

KIND = nine-arm radial. It owns the SOLE RED lane of the abyss brood, the warm
counterweight to the teal/bone/pearl siblings.

House style this obeys (the elevated "epic" Leyak grammar):
  - CHIBI proportions — one oversized rounded mantle-head; the mass sits in the
    head, with the arms blooming OUT of it (not a spider of equal spokes).
  - FLAT saturated fills + a hard 1-2px ink keyline (28,22,30). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core -> flat fill -> top-left warm-coral rim sheen.
  - Scary-CUTE not grim: one big calm gold eye + a small placid beak — a sea-god
    waving, never a snarl.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC pass: render BIG at SS=5-6, then smoothscale for crisp downscale.

RE-SPEC (cross-set pin): arms read as 8-9 FAT, CURLING, TAPERING rays with
sucker-DOTS + ASYMMETRIC curl — never thin straight spokes — and the mass sits
in the rounded mantle-head. So the 32px read is unambiguously "octopus deity,"
clear of Tzitzimitl's rigid bone star-corona and Raijin's round drum-ring.

Prop -> pillar mirror: a single ARM is the pillar BODY — a tapering sucker-
banded tentacle-COLUMN whose cream sucker-rings = the tiling repeats. The
GAP-EDGE cap is a curled arm-TIP coil (~shaft+30%) with one divine-gold
glow-sucker radiating into the gap. The other eight arms stay in the head-mass.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python \
        docs/skybit_devil/batch2/umibozu_versions/akkorokamui/render_akkorokamui.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (akkorokamui) ─────────────────────────────────────────────
# The sole RED lane. Sunset-vermilion body over a wine-oxblood shade carries the
# whole creature warm; warm-coral is the top-left lit sheen. Cream sucker-rings
# are the tentacle TELL (and the pillar tiling cadence). Divine-GOLD is the ONLY
# bright pip — confined to the single eye + the glow-suckers, so it lanterns the
# gap without washing the warm body. Ink-beak is the deepest value note.
BODY        = (206, 84, 64)     # sunset-vermilion fill
BODY_DK     = (132, 42, 46)     # wine-oxblood shade (dark-core / hollows)
BODY_SHEEN  = (238, 150, 120)   # warm-coral rim sheen (top-left lit lobe)
BODY_DEEP   = (96, 28, 34)      # deepest oxblood (sucker pits / under-mass)

CREAM       = (228, 210, 184)   # cream sucker-rings — the tentacle tell
CREAM_DK    = (176, 150, 120)   # cream ring shade

GOLD        = (244, 200, 96)    # divine-gold — eye + glow-suckers ONLY
GOLD_CORE   = (255, 240, 196)   # hot twinkle core inside the eye / glow-suckers
GOLD_DK     = (190, 142, 56)    # gold dark-core ring

INK         = (28, 22, 30)      # the house keyline
BEAK_INK    = (30, 20, 22)      # ink-beak (its own deep warm-black)

# Night lifts a warm-cream keyline so the red mantle edge survives on a midnight
# sky (dark ink would vanish on the deep blue); grown 2px for shape-read.
INK_NIGHT   = (244, 196, 150)


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_col=None):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen lobe. Sculpted volume while staying flat-shaded."""
    pygame.draw.circle(surf, _shade_c(col, -36), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.06))))
    if sheen:
        sc = sheen_col if sheen_col is not None else BODY_SHEEN
        pygame.draw.circle(surf, sc,
                           (int(cx - r * 0.34), int(cy - r * 0.36)),
                           max(2, int(r * 0.28)))


def _add_outline(src, outline_color=(*INK, 235), width=1):
    """Grow a keyline from the alpha mask so the silhouette POPS on any sky (the
    parrot `_add_outline` recipe). On night the keyline is a lifted warm-cream
    tone, grown thicker (width=2) so the red mantle edge reads on shape."""
    w, h = src.get_size()
    pad = width + 1
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    offs = [(dx, dy) for dx in range(-width, width + 1)
            for dy in range(-width, width + 1) if (dx, dy) != (0, 0)]
    for dx, dy in offs:
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


def _glow_sucker(surf, cx, cy, r, ss, *, glow=True, night=False, glow_mult=1.0):
    """A divine-GOLD glow-PIP — the only place the bright pip is allowed off the
    eye. Kept SMALL and radiating (a halo that bleeds into the gap) rather than a
    flat solid coin, so it never rivals the hero eye as a second focal. Used once,
    on the gap-cap arm-tip."""
    if glow:
        # Larger, softer halo so the pip READS as a lantern radiating into the
        # gap rather than as a hard disc on the shaft.
        gr = int(r * (4.0 if night else 2.8) * glow_mult)
        gl = make_glow_surface(max(1, gr), GOLD,
                               alpha_center=190 if night else 120, falloff=2.3)
        surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)
    # A single small lit pip — a thin gold rim + a hot core — not a fat coin.
    pygame.draw.circle(surf, GOLD_DK, (int(cx), int(cy)), max(1, int(r * 0.78)))
    pygame.draw.circle(surf, GOLD, (int(cx), int(cy)), max(1, int(r * 0.56)))
    pygame.draw.circle(surf, GOLD_CORE, (int(cx), int(cy)), max(1, int(r * 0.26)))


# ── one FAT curling tapering arm (the kraken-deity ray) ───────────────────────

def _arm(surf, root_x, root_y, length, hw, ss, *, ang0, curl, body=BODY,
         sucker_side=1, n_suckers=6, taper=0.82, night=False, glow_tip=False,
         behind=False, sheen=True, curl_accel=1.3):
    """A single FAT curling TAPERING arm — the kraken-deity ray. Built as a
    centerline that sweeps from `ang0` and bends by `curl` (asymmetric per arm),
    with a fat root that necks to a fine tip. Drawn as a hard flat triad ribbon
    (dark-core -> fill -> top-left warm-coral sheen stripe). Cream sucker-RINGS
    march down the inner edge — the octopus tell that reads at 32px.

    The arms are deliberately FAT (hw stays wide for the first half) and CURLING
    (the centerline arcs), so they never read as thin straight spokes.

    `behind` paints the arm in the deep wine-oxblood under-shade with no sheen
    and dimmed suckers, so depth-layered arms tucked BEHIND the mantle recede —
    the octopus reads head-forward, not a flat radial pinwheel.
    """
    steps = 40
    # Centerline: start at root, advance by arc length, sweep the heading.
    cl = []
    x, y, a = root_x, root_y, ang0
    seg = length / steps
    for i in range(steps + 1):
        cl.append((x, y))
        # Curl accelerates toward the tip so the arm hooks into a coil; the rate
        # is tunable per-arm so curls vary (some lazy, some tight hooks).
        a += curl * (0.4 + curl_accel * (i / steps))
        x += math.cos(a) * seg
        y += math.sin(a) * seg

    # Behind-arms use the deep oxblood under-shade so they recede into the mass.
    if behind:
        body = BODY_DEEP
        sheen = False

    def _hw_at(t):
        # Fat for the first third, then necks hard to a fine tip.
        return hw * (1.0 - taper * (t ** 1.35))

    # Build offset rails perpendicular to the centerline.
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        px, py = cl[i]
        if i < steps:
            nx, ny = cl[i + 1]
        else:
            nx, ny = cl[i]
            px, py = cl[i - 1]
        dx, dy = nx - px, ny - py
        dlen = math.hypot(dx, dy) or 1.0
        ox, oy = -dy / dlen, dx / dlen
        w = _hw_at(t)
        cx, cy = cl[i]
        left.append((cx + ox * w, cy + oy * w))
        right.append((cx - ox * w, cy - oy * w))

    shape = left + right[::-1]
    pygame.draw.polygon(surf, _shade_c(body, -36),
                        [(int(px), int(py)) for px, py in shape])
    inner = [(px + (cl[i][0] - px) * 0.16, py + (cl[i][1] - py) * 0.16)
             for i, (px, py) in enumerate(left)]
    inner_r = [(px + (cl[i][0] - px) * 0.16, py + (cl[i][1] - py) * 0.16)
               for i, (px, py) in enumerate(right)]
    pygame.draw.polygon(surf, body,
                        [(int(px), int(py)) for px, py in (inner + inner_r[::-1])])

    # Top-left warm-coral sheen stripe down the lit (outer-left) rail. Lifted a
    # touch on night so the leading arms keep a luminous value edge on a dark sky.
    if sheen:
        sheen_col = _shade_c(BODY_SHEEN, 18) if night else BODY_SHEEN
        sheen_pts = [(int(px), int(py)) for px, py in left[::2]]
        if len(sheen_pts) >= 2:
            pygame.draw.lines(surf, sheen_col, False, sheen_pts, max(1, int(1.5 * ss)))

    # Cream sucker-RINGS marching down the inner edge — the octopus tell. Drawn
    # as a cream ring (CREAM_DK rim + CREAM fill + oxblood pit) so they read as
    # discrete suckers, not a dotted line.
    for k in range(n_suckers):
        t = (k + 0.5) / (n_suckers + 0.4)
        idx = int(t * steps)
        px, py = cl[idx]
        w = _hw_at(t)
        # Seat the sucker toward the inner (curl-side) edge of the arm.
        nx, ny = cl[min(idx + 1, steps)]
        dx, dy = nx - px, ny - py
        dlen = math.hypot(dx, dy) or 1.0
        ox, oy = -dy / dlen, dx / dlen
        sx = px - ox * w * 0.36 * sucker_side
        sy = py - oy * w * 0.36 * sucker_side
        rr = max(1.5, w * 0.40)
        # Behind-arms get dim oxblood pits only (no bright cream), so they don't
        # twinkle forward out of the receding mass.
        if behind:
            pygame.draw.circle(surf, BODY_DEEP, (int(sx), int(sy)), max(1, int(rr)))
            pygame.draw.circle(surf, _shade_c(BODY_DEEP, -18), (int(sx), int(sy)), max(1, int(rr * 0.5)))
            continue
        pygame.draw.circle(surf, BODY_DEEP, (int(sx), int(sy)), max(1, int(rr)))
        pygame.draw.circle(surf, CREAM_DK, (int(sx), int(sy)), max(1, int(rr * 0.80)))
        pygame.draw.circle(surf, CREAM, (int(sx), int(sy)), max(1, int(rr * 0.54)))
        pygame.draw.circle(surf, BODY_DEEP, (int(sx), int(sy)), max(1, int(rr * 0.22)))

    # The tip arm of the pillar cap carries one divine-gold glow-sucker.
    if glow_tip:
        # Seat the pip a step back from the very tip (on the inner coil) and keep
        # it SMALL so it radiates into the gap rather than capping as a coin.
        tx, ty = cl[-4]
        _glow_sucker(surf, tx, ty, max(2, hw * 0.22), ss, night=night)
    return cl[-1]


# ── the rounded mantle-head (where the mass sits) ─────────────────────────────

def _mantle_head(surf, cx, cy, r, ss, *, night=False, tell=False):
    """The oversized rounded MANTLE-HEAD — the bulb where the kraken-deity's mass
    sits. A tall rounded mantle (octopus head) with the triad, a warm-coral rim
    sheen on the pate, ONE big calm divine-gold cyclops eye, and a tiny ink beak
    below it. Scary-CUTE: the single serene gold eye + small placid beak read as
    a benevolent little sea-god."""
    body = _shade_c(BODY, 12) if night else BODY

    # The mantle bulb: a tall rounded dome (mantle crown) over a slightly wider
    # brow mass, so the head reads heavy and rounded — an octopus mantle, not a
    # ball. Lower brow first (occluded by the crown).
    brow = pygame.Rect(0, 0, int(r * 1.86), int(r * 1.46))
    brow.center = (int(cx), int(cy + r * 0.40))
    pygame.draw.ellipse(surf, _shade_c(body, -36), brow)
    pygame.draw.ellipse(surf, body, brow.inflate(-int(r * 0.12), -int(r * 0.12)))

    # Crown dome (the tall mantle top) — triad, sheen suppressed (a dedicated
    # crescent below carries the pate highlight).
    _triad_circle(surf, cx, cy, r, body, sheen=False)

    # ONE hard warm-coral rim-sheen crescent on the pate (lit disc minus a body
    # bite so it reads as one clean crescent, never a dent in the silhouette).
    # Night lifts the sheen brighter + sweeps it WIDER across the crown so the
    # domed head survives as a luminous value rim on the dark sky even if the eye
    # is occluded (the brief: don't let one pip carry the read).
    sheen_col = _shade_c(BODY_SHEEN, 30) if night else BODY_SHEEN
    scx, scy, scr = cx - r * 0.26, cy - r * 0.44, r * (0.40 if night else 0.32)
    pygame.draw.circle(surf, sheen_col, (int(scx), int(scy)), max(2, int(scr)))
    pygame.draw.circle(surf, body,
                       (int(scx + scr * 0.58), int(scy + scr * 0.50)),
                       max(2, int(scr * 0.84)))
    # A second thinner sheen tick wrapping the crown rim toward the right so the
    # luminous top edge spans the whole dome, not just the upper-left lobe.
    pygame.draw.arc(surf, sheen_col,
                    (int(cx - r * 0.74), int(cy - r * 0.92),
                     int(r * 1.48), int(r * 1.2)),
                    math.radians(35), math.radians(150),
                    max(2, int((2.4 if night else 1.8) * ss)))

    # — ONE big calm cyclops eye: a large divine-gold disc with a soft halo, a
    #   cream sclera ring, and a gentle heavy-lidded look (a calm down-curved lid
    #   shading the top), so it reads serene/benevolent, not a glare.
    eye_cx, eye_cy = cx, cy + r * 0.02
    eye_r = r * 0.40
    # Halo so the divine eye glows (the focal pip).
    gr = int(eye_r * (2.4 if night else 1.7))
    gl = make_glow_surface(gr, GOLD, alpha_center=150 if night else 90, falloff=2.1)
    surf.blit(gl, (int(eye_cx - gr), int(eye_cy - gr)), special_flags=pygame.BLEND_ADD)
    # FLAT cyclops iris (chibi triad, no airbrush): dark-core socket -> cream
    # sclera -> ONE flat gold iris -> dark pupil -> one sheen dot. No graduated
    # GOLD_DK band inside the iris (that faceted ring read too realistic).
    pygame.draw.circle(surf, BODY_DEEP, (int(eye_cx), int(eye_cy)), max(2, int(eye_r * 1.04)))
    pygame.draw.circle(surf, CREAM, (int(eye_cx), int(eye_cy)), max(2, int(eye_r * 0.94)))
    pygame.draw.circle(surf, GOLD, (int(eye_cx), int(eye_cy)), max(2, int(eye_r * 0.70)))
    # A calm horizontal slit pupil (sea-god serenity, not a round glare).
    pygame.draw.ellipse(surf, BEAK_INK,
                        (int(eye_cx - eye_r * 0.36), int(eye_cy - eye_r * 0.13),
                         int(eye_r * 0.72), int(eye_r * 0.26)))
    # ONE flat sheen dot top-left of the iris (the only highlight — keeps it flat).
    pygame.draw.circle(surf, GOLD_CORE,
                       (int(eye_cx - eye_r * 0.26), int(eye_cy - eye_r * 0.28)),
                       max(1, int(eye_r * 0.18)))
    # Heavy upper lid: a body-colored crescent dropping over the top of the eye
    # so the gaze reads gentle/half-closed, not a wide stare.
    lid = pygame.Rect(0, 0, int(eye_r * 2.3), int(eye_r * 1.5))
    lid.center = (int(eye_cx), int(eye_cy - eye_r * 1.02))
    pygame.draw.ellipse(surf, body, lid)

    # — Tiny ink BEAK below the eye: a small soft downward chevron (placid), the
    #   deepest value note. Two short converging ink strokes.
    bk_y = cy + r * 0.62
    bw = r * 0.22
    pygame.draw.polygon(surf, BEAK_INK, [
        (int(cx - bw), int(bk_y)),
        (int(cx + bw), int(bk_y)),
        (int(cx), int(bk_y + r * 0.20)),
    ])
    # A faint cream highlight on the beak's lit upper-left facet.
    pygame.draw.line(surf, CREAM_DK,
                     (int(cx - bw * 0.7), int(bk_y + r * 0.02)),
                     (int(cx - bw * 0.1), int(bk_y + r * 0.13)),
                     max(1, int(1.2 * ss)))

    if tell:
        # Baked low-res tell for the 32px read: a bold gold eye-pip + dark beak
        # bar so the creature stays "one-eyed octopus deity" when tiny.
        pygame.draw.circle(surf, GOLD, (int(eye_cx), int(eye_cy)), max(2, int(eye_r * 0.7)))
        pygame.draw.circle(surf, GOLD_CORE, (int(eye_cx), int(eye_cy)), max(1, int(eye_r * 0.30)))
        pygame.draw.line(surf, BEAK_INK, (int(cx - bw), int(bk_y + r * 0.04)),
                         (int(cx + bw), int(bk_y + r * 0.04)), max(2, int(2.2 * ss)))


# ── the whole creature: mantle-head + bloom of nine arms ──────────────────────

def build_akkorokamui(scale=1.0, ss=5, *, night=False, compact=False):
    """The full kraken-deity on a transparent surface: the rounded mantle-head up
    top, a bloom of NINE fat curling tapering arms unfurling from beneath/around
    it. EPIC pass renders BIG at SS then smoothscales. `compact` is the gameplay/
    32px variant — head grown to dominate, arms shortened, baked low-res tell."""
    head_r = int(44 * scale) * ss
    n_arms = 9

    # Arm length/width — fat and long for the hero, stubbier for the compact chip
    # so the head-mass dominates the 32px budget.
    arm_len = head_r * (1.7 if compact else 3.0)
    arm_hw = head_r * (0.40 if compact else 0.34)

    pad = int(arm_len * 0.95) + ss * 4
    W = int(head_r * 2 + pad * 2)
    H = int(head_r * 2 + arm_len + pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    head_cy = int(head_r * 1.05 + ss * 6)

    # ── ASYMMETRIC, DEPTH-LAYERED bloom (NOT a radial pinwheel) ──────────────
    # The arms do NOT sit on an even ring at compass angles. Instead the bloom
    # cascades DOWN-and-FORWARD from a head-dominant mass, with arms in three
    # depth bands so the silhouette reads "octopus deity," never "starfish":
    #   BEHIND   — 3 short stubby arms tucked up behind the mantle (oxblood
    #              under-shade, dimmed, drawn FIRST so the head occludes them).
    #   MID/FRONT— the long hero arms unfurling beneath/forward, drawn AFTER the
    #              head so they overlap the lower mantle (head-forward read).
    # Each entry: (root angle from head center, root-ring radius scale, heading
    # angle, length scale, half-width scale, curl, curl-accel, sucker side, band).
    # Hand-tuned to be lopsided — left side carries 2 long trailing arms, the
    # right a tight hook + a forward-reaching arm; lengths + curls all differ.
    base = math.radians(90)
    cy_lo = head_cy + head_r * 0.34
    arms = [
        # band: 0 = behind (drawn first), 1 = front (drawn after the head)
        # (root_ang,      ring,  heading,        lenS, hwS,  curl,   accel, side, band)
        # BEHIND arms peek out LOW + to the sides of the mantle and head DOWN, so
        # they read as occluded arms behind a head-forward mass (never up-horns).
        (math.radians(168), 0.74, math.radians(158), 0.70, 0.72,  0.050, 1.3,  -1, 0),  # behind far-left, down-out
        (math.radians(22),  0.74, math.radians(28),  0.62, 0.68, -0.054, 1.3,   1, 0),  # behind far-right, down-out
        (math.radians(48),  0.60, math.radians(40),  0.66, 0.66, -0.040, 1.1,   1, 0),  # behind lower-right tuck
        (math.radians(196), 0.88, math.radians(150), 1.06, 1.00,  0.052, 1.5,  -1, 1),  # long trailing left, sweeps out+down
        (math.radians(214), 0.92, math.radians(128), 0.88, 0.90,  0.078, 1.9,  -1, 1),  # mid left, tight inward hook
        (math.radians(120), 0.86, math.radians(70),  0.74, 0.86, -0.090, 2.1,   1, 1),  # short right, crossing forward hook
        (math.radians(150), 0.94, math.radians(108), 1.12, 1.04,  0.040, 1.2,   1, 1),  # longest, central forward drape
        (math.radians(86),  0.78, math.radians(58),  0.96, 0.94, -0.066, 1.7,   1, 1),  # long lower-right, curls out
        (math.radians(104), 0.66, math.radians(95),  0.82, 0.88,  0.024, 1.0,  -1, 1),  # mid central, near-straight drape
    ]

    def _draw_band(band):
        for (rang, ring, head, lenS, hwS, curl, accel, side, b) in arms:
            if b != band:
                continue
            rx = cx + math.cos(rang) * head_r * ring
            ry = cy_lo + math.sin(rang) * head_r * ring * 0.74
            ln = arm_len * lenS
            hw = arm_hw * hwS
            behind = (band == 0)
            # Alternate the front fill value a touch so neighbours separate.
            col = BODY if (side > 0) else _shade_c(BODY, -10)
            _arm(surf, rx, ry, ln, hw, ss, ang0=head, curl=curl, curl_accel=accel,
                 body=col, sucker_side=side, behind=behind,
                 n_suckers=max(4, int(ln / (head_r * 0.5))), night=night)

    _draw_band(0)                                  # behind arms first
    _mantle_head(surf, cx, head_cy, head_r, ss, night=night, tell=compact)
    _draw_band(1)                                  # front arms overlap the head

    out_w = max(1, int(surf.get_width() / ss))
    out_h = max(1, int(surf.get_height() / ss))
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(smallv, outline_color=oc, width=2 if night else 1)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _arm_column(surf, cx, top_y, bot_y, span, ss, *, night=False):
    """The repeatable PILLAR BODY: a SINGLE arm as a straight tapering-banded
    tentacle COLUMN. A fat oxblood-cored shaft with a warm-coral sheen rail and
    CREAM SUCKER-RINGS marching down at a steady cadence — the rings ARE the
    tiling repeats. Drawn vertical so it tiles cleanly top<->bottom."""
    length = bot_y - top_y
    body = _shade_c(BODY, 12) if night else BODY
    hw = span * 0.46

    # Shaft triad: dark-core rail under, flat fill, coral sheen rail on the left.
    left = pygame.Rect(int(cx - hw), int(top_y), int(hw * 2), int(length))
    pygame.draw.rect(surf, _shade_c(body, -36), left)
    pygame.draw.rect(surf, body, left.inflate(-int(hw * 0.12), 0))
    # Warm-coral sheen rail down the lit (left) edge.
    pygame.draw.rect(surf, BODY_SHEEN,
                     (int(cx - hw * 0.86), int(top_y), max(2, int(hw * 0.22)), int(length)))

    # Cream sucker-rings down the center on a steady cadence (the tiling tell).
    ring_pitch = hw * 1.5
    n = max(2, int(length / ring_pitch))
    pitch = length / n
    for k in range(n):
        ry = top_y + (k + 0.5) * pitch
        rr = hw * 0.46
        pygame.draw.circle(surf, BODY_DEEP, (int(cx), int(ry)), max(1, int(rr)))
        pygame.draw.circle(surf, CREAM_DK, (int(cx), int(ry)), max(1, int(rr * 0.80)))
        pygame.draw.circle(surf, CREAM, (int(cx), int(ry)), max(1, int(rr * 0.54)))
        pygame.draw.circle(surf, BODY_DEEP, (int(cx), int(ry)), max(1, int(rr * 0.22)))


def _arm_tip_cap(surf, cx, cap_base_y, span, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: a curled arm-TIP coil (~shaft+30%) that hooks
    off the shaft and curls toward the gap, with ONE divine-gold glow-sucker on
    the inner coil radiating INTO the gap. `point_up` orients the coil so its tip
    + glow-sucker face the gap. Kept compact so the cap is never top-heavy."""
    d = -1 if point_up else 1
    body = _shade_c(BODY, 12) if night else BODY
    # Start the cap at the shaft width so the tip flows out of the column, then
    # NECK it hard to a fine point — a true tapering arm-TIP, not a fat coil.
    hw = span * 0.46

    # The arm tip emerges from the shaft end and curls gently inward toward the
    # gap. A SHORT arm with a strong taper + a softer curl so it visibly NARROWS
    # as it hooks — mass drops toward the gap line, never top-heavy or snail-shell.
    root_y = cap_base_y
    ang0 = math.radians(90) if not point_up else math.radians(-90)
    _arm(surf, cx, root_y, span * 1.10, hw, ss, ang0=ang0, curl=0.058 * (-d),
         curl_accel=1.6, body=body, sucker_side=1, n_suckers=3, taper=0.94,
         night=night, glow_tip=True)


def _arm_pillar_obstacle(height, ss, *, flip, night=False):
    """One arm-column PILLAR obstacle: the single tapering sucker-banded arm fills
    the post and a curled arm-TIP coil CAPS the GAP edge, dropping one gold glow-
    sucker into the gap. `flip=True` is the TOP pillar (cap at bottom/gap edge,
    coil curling DOWN); `flip=False` is the BOTTOM pillar (cap at top/gap edge,
    coil curling UP). Both mirror the same arm body — clean vertical mirror."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    span = (PIPE_W - 8) * ss
    cap_band = int(42 * ss)
    if flip:
        _arm_column(surf, cx, 0, bh - cap_band, span, ss, night=night)
        _arm_tip_cap(surf, cx, bh - cap_band, span, ss, point_up=False, night=night)
    else:
        _arm_column(surf, cx, cap_band, bh, span, ss, night=night)
        _arm_tip_cap(surf, cx, cap_band, span, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(out, outline_color=oc, width=2 if night else 1)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(238, 240, 244)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot, *, stars=False):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    if stars:
        import random as _r
        rng = _r.Random(77)
        for _ in range(26):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, int(h * 0.7))
            pygame.draw.circle(s, (255, 235, 205), (sx, sy), rng.choice((1, 1, 2)))
    return s


def _to_gray(src):
    g = pygame.Surface(src.get_size(), pygame.SRCALPHA)
    g.blit(src, (0, 0))
    arr = pygame.surfarray.pixels3d(g)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    return g


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1040, 770
    sheet = pygame.Surface((SW, SH))
    sheet.fill((50, 48, 52))          # neutral warm-grey bg
    _label(sheet, font,
            "AKKOROKAMUI  —  Umibozu-versions #2  —  sunset-red kraken-deity (nine-arm radial, the sole RED lane)  —  round 2", 18, 12)
    _label(sheet, small,
            "RE-SPEC: 8-9 FAT CURLING TAPERING arms w/ cream sucker-rings + asymmetric curl; mass in the rounded mantle-head; one calm gold cyclops eye + ink beak. Octopus-deity read, clear of bone star-corona / drum-ring.",
            18, 32, (236, 200, 170))

    # — Cell A: BIG hero on a dusk-sea sunset sky.
    panel = pygame.Rect(18, 56, 320, 660)
    bgA = _sky(panel.w, panel.h, (40, 30, 60), (150, 70, 70), (236, 150, 96))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (150, 110, 110), panel, 2, border_radius=8)
    hero = build_akkorokamui(scale=1.7, ss=5)
    # Fit hero into the panel.
    maxw, maxh = panel.w - 24, panel.h - 96
    if hero.get_width() > maxw or hero.get_height() > maxh:
        sc = min(maxw / hero.get_width(), maxh / hero.get_height())
        hero = pygame.transform.smoothscale(
            hero, (int(hero.get_width() * sc), int(hero.get_height() * sc)))
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 60))
    _label(sheet, font, "(a) HERO  big scale (SS=5)", panel.x + 8, panel.y + 8)
    _label(sheet, small, "mantle-head + bloom of 9 fat curling arms",
           panel.x + 8, panel.y + 28, (236, 210, 180))

    # — Cell B: arm-column PILLAR pair at TRUE scale (night) + 2x cap zoom proving
    #   the curled arm-tip coil drops a gold glow-sucker into the gap, MIRROR shown.
    panelB = pygame.Rect(352, 56, 330, 660)
    bg = _sky(panelB.w, panelB.h, (20, 16, 36), (40, 26, 48), (70, 40, 52), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (150, 110, 110), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "1 arm-column tiles (cream rings) + arm-tip coil cap (~shaft+30%)",
           panelB.x + 8, panelB.y + 28, (236, 210, 180))

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 540
    slice_x = panelB.x + 22
    slice_y = panelB.y + 50
    gap_top = 178
    gap_h = 132
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _arm_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _arm_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (210, 180, 170), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px): arm", slice_x - 2, slice_y + slice_h + 6, (230, 210, 190))
    _label(sheet, small, "tiles; coil lanterns gap", slice_x - 2, slice_y + slice_h + 22, (255, 210, 150))

    # 2x zoom of the cap band (MIRROR visible: top coil curls down, bottom up).
    cap_band = 42
    zw, zh = pw, 170
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    top_anchor = 16
    zoom_src.blit(top_pillar, (-2, -(top_h - cap_band - top_anchor) - 2))
    zoom_gap = zh - 2 * cap_band - 2 * top_anchor
    bot_anchor = top_anchor + cap_band + zoom_gap
    zoom_src.blit(bot_pillar, (-2, bot_anchor - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 168
    zy = panelB.y + 116
    zbg = _sky(zw * 2, zh * 2, (20, 14, 32), (36, 24, 44), (60, 36, 48))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (210, 180, 170), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom: arm-tip coils", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "mirror + gold glow-sucker", zx - 2, zy + zh * 2 + 6, (255, 210, 150))

    # — Cell C: TRUE 32px chip on day + night + a mid-scale compact + 4x/gray audit.
    panelC = pygame.Rect(696, 56, 326, 660)
    pygame.draw.rect(sheet, (44, 42, 46), panelC, border_radius=8)
    pygame.draw.rect(sheet, (150, 110, 110), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "head-dominant compact / day + night sky", panelC.x + 8, panelC.y + 28,
           (236, 210, 180))

    boss_day = build_akkorokamui(scale=0.6, ss=5, compact=True)
    boss_night = build_akkorokamui(scale=0.6, ss=5, night=True, compact=True)
    day = _sky(150, 300, (96, 165, 225), (150, 200, 238), (200, 228, 246))
    night = _sky(150, 300, (20, 16, 36), (40, 26, 48), (72, 42, 54), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 12, dy))
    sheet.blit(night, (panelC.x + 170, dy))
    # Fit compacts.
    for srf in (boss_day, boss_night):
        pass
    bd = boss_day
    bn = boss_night
    if bd.get_height() > 284:
        sc = 284 / bd.get_height()
        bd = pygame.transform.smoothscale(bd, (int(bd.get_width() * sc), int(bd.get_height() * sc)))
        bn = pygame.transform.smoothscale(bn, (int(bn.get_width() * sc), int(bn.get_height() * sc)))
    sheet.blit(bd, (panelC.x + 12 + 75 - bd.get_width() // 2, dy + 8))
    sheet.blit(bn, (panelC.x + 170 + 75 - bn.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 18, dy + 6, (16, 28, 40))
    _label(sheet, small, "NIGHT", panelC.x + 176, dy + 6, (255, 210, 150))

    gy = dy + 318
    _label(sheet, small, "TRUE 32px chip on day + night sky:", panelC.x + 12, gy - 2,
           (236, 210, 180))
    icon_src = build_akkorokamui(scale=1.0, ss=5, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))

    chips = [
        (_sky(86, 86, (96, 165, 225), (150, 200, 238), (200, 228, 246)), "day"),
        (_sky(86, 86, (20, 16, 36), (40, 26, 48), (72, 42, 54), stars=True), "night"),
    ]
    sx = panelC.x + 12
    for bg_chip, lab in chips:
        chip = pygame.Rect(sx, gy + 16, 86, 86)
        sheet.blit(bg_chip, chip.topleft)
        pygame.draw.rect(sheet, (180, 150, 145), chip, 1, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 240, 240))
        sx += 96

    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    bx = panelC.x + 12
    byy = gy + 118
    pygame.draw.rect(sheet, (66, 60, 62), (bx - 2, byy - 2, blow.get_width() + 4, blow.get_height() + 4),
                     border_radius=4)
    sheet.blit(blow, (bx, byy))
    _label(sheet, small, "4x blow-up of the 32px chip", bx, byy + blow.get_height() + 4,
           (236, 210, 180))

    gray = _to_gray(blow)
    gx = bx + blow.get_width() + 24
    pygame.draw.rect(sheet, (114, 110, 112), (gx - 2, byy - 2, gray.get_width() + 4, gray.get_height() + 4),
                     border_radius=4)
    sheet.blit(gray, (gx, byy))
    _label(sheet, small, "grayscale value check", gx, byy + gray.get_height() + 4, (24, 24, 24))

    # — Footer captions.
    _label(sheet, small,
           "STYLE: flat saturated fills, hard 1-2px ink keyline (28,22,30), dark-core -> flat-fill -> warm-coral rim-sheen triad, 1px grown outline, chibi, scary-CUTE.",
           18, SH - 40, (236, 200, 170))
    _label(sheet, small,
           "PILLAR: a SINGLE arm IS the shaft (tapering, cream sucker-rings tile top<->bottom); a curled arm-TIP coil (~shaft+30%) caps + drops one gold glow-sucker into the gap. On-axis mirror.",
           18, SH - 22, (236, 200, 170))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
