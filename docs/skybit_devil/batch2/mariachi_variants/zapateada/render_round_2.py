"""ZAPATEADA — round 2 review sheet (Mariachi warm-skeleton family, locked5).

Lead facet DANCE / MOTION: a ballet folklorico dancer calaca frozen mid-twirl —
one bony arm arced overhead with a sky-gap to the skull, a huge ruffled skirt
fanned OFF-AXIS by the spin into a counter-swung comma-curve, bone legs in a
pointed zapateado stomp. The asymmetric in-motion silhouette is the signature:
the family's ONLY off-axis, leaning, in-motion read.

Round-2 resolves the AD critique:
  - FIX1 (CRITICAL palette): the hero skirt was rendering as a dull salmon-brick
    (~(174,118,115)) — converging with Jinete's rust. Root cause was the triad
    helpers: `_dark` shade scaled the rose toward brown-brick AND a warm-bone
    sheen ellipse was washing the lit fill warm. Fixed by giving the skirt its
    OWN cool triad — a deep COOL magenta-rose dark-core and a bright COOL pink
    sheen — and by NOT running the warm-bone sheen / warm core overlays over the
    skirt. The lit flat-fill now stays firmly in the pinned (214,72,86)
    rose-magenta lane, leaning PINKER/COOLER than chile and rust. A proof chip
    strip puts rose vs chile vs rust at 32px.
  - FIX2 (CRITICAL motion): torso+skull tilted ~18deg INTO the spin (clear
    diagonal spine), the raised arm lifted + separated with a sky-gap clear of
    the cranium, and the skirt hem counter-swung to the opposite side.
  - FIX3: ribcage/arm tangle simplified — clean readable ribcage, one arced
    raised arm, one trailing arm; fewer interior rib lines.
  - FIX4: turquoise ribbon trails in a longer curve following the spin.
  - FIX5: skirt value restored to hard triad BANDS per tier (no soft overlay).

Prop->pillar keeps the SHIP-GRADE symmetric radial ribbon-rosette on the pole
axis (only inheriting the corrected cool hero hue).

House grammar: chibi proportions, FLAT saturated fills + hard ink keylines, form
via dark-core -> flat-fill -> top-left rim-sheen TRIAD (never soft gradient), a
1px outline grown from the alpha mask, supersample -> smoothscale. Scary-CUTE.

Run headless (SDL_VIDEODRIVER=dummy). Writes round_2.png beside this script.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = "/home/user/skybit"
_OUT_DIR = os.path.join(_ROOT, "docs", "skybit_devil", "batch2",
                        "mariachi_variants", "zapateada")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# ── PINNED PALETTE (exact hexes from the locked brief) ───────────────────────
ROSE      = (214, 72, 86)     # rose-magenta — HERO swept-skirt mass (pinker/cooler)
BONE      = (236, 224, 200)   # warm-bone base
BONE_SH   = (178, 154, 112)   # tan-bone shade (dark-core)
MARIGOLD  = (232, 184, 80)    # marigold-gold ruffle-trim
TEAL      = (58, 172, 166)    # turquoise ribbon (cool accent)
CORAL     = (238, 116, 92)    # coral temple-rose
INK       = (28, 22, 24)      # hard keyline
SHEEN     = (250, 242, 222)   # top-left rim-sheen (warm-bone — for BONE only)

# split chips: the three warm reds the cross-set mandate must keep apart
CHILE     = (214, 86, 44)     # Comelona — orange-leaning accent
RUST      = (176, 70, 56)     # Jinete — desaturated brick/brown


def _dark(c, f=0.62):
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f))


def _lite(c, f=0.4):
    return tuple(int(c[i] + (255 - c[i]) * f) for i in range(3))


# WHY: the round-1 skirt muddied to salmon-brick because `_dark` just scales
# every channel toward black, which warms a red toward brick (red survives,
# blue dies). The rose must instead get COOLER as it darkens — keep blue from
# collapsing and let red drop faster — so the trough reads as a deep MAGENTA-rose,
# never a brown. Likewise the lit lip must gain blue (cool pink), not cream.
ROSE_SH   = (138, 36, 64)            # deep COOL magenta-rose trough (not brick)
ROSE_HI   = (244, 130, 162)          # bright COOL pink lit lip (gains blue)
ROSE_MID  = ROSE                     # flat fill held EXACTLY on the pinned hex
MARI_SH   = _dark(MARIGOLD, 0.64)
MARI_HI   = _lite(MARIGOLD, 0.46)
TEAL_SH   = _dark(TEAL, 0.58)
CORAL_SH  = _dark(CORAL, 0.62)


# ── house-style helpers (shared grammar across the family) ───────────────────
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
               ell=(0.28, 0.40, 0.78, 0.72)):
    """Dark-core: a lower-right pooled shadow lobe, masked to silhouette."""
    w, h = sprite.get_size()
    ov = new_surf(w, h)
    pygame.draw.ellipse(ov, (*shade_col, alpha),
                        (int(ell[0] * w), int(ell[1] * h),
                         int(ell[2] * w), int(ell[3] * h)))
    ov.blit(amask(sprite), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(ov, (0, 0))
    return sprite


# ── marigold-petal motif (flat triad rosette; family shared) ─────────────────
def draw_marigold(surf, cx, cy, r, base=MARIGOLD, shade=MARI_SH, hi=MARI_HI,
                  petals=8, core=None):
    for ang_i in range(petals):
        a = (ang_i / petals) * math.tau
        px = cx + math.cos(a) * r
        py = cy + math.sin(a) * r
        pygame.draw.circle(surf, INK, (int(px), int(py)), int(r * 0.46) + 1)
        pygame.draw.circle(surf, shade, (int(px), int(py)), int(r * 0.46))
    for ang_i in range(petals):
        a = (ang_i / petals) * math.tau + (math.tau / petals) * 0.5
        px = cx + math.cos(a) * r * 0.62
        py = cy + math.sin(a) * r * 0.62
        pygame.draw.circle(surf, base, (int(px), int(py)), int(r * 0.42))
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r * 0.42))
    pygame.draw.circle(surf, core or MARIGOLD, (int(cx), int(cy)), int(r * 0.34))
    pygame.draw.circle(surf, _lite(core or MARIGOLD, 0.5),
                       (int(cx - r * 0.1), int(cy - r * 0.1)), int(r * 0.16))


# ── ruffle tier: a fanned scalloped lobe-strip, all lobes LEANING ONE WAY ─────
def draw_ruffle_tier(surf, cx, top_y, span_l, span_r, drop, lobes, lean,
                     base, shade, hi):
    """One hard triad-lit RUFFLE tier — a scalloped lower edge fanned between
    span_l (the swept side) and span_r. `lean` skews every lobe's bottom toward
    the swept side so the tier reads as motion in the LEAN. Drawn as hard BANDS:
    a dark-core trough band tucked under the scallops, the flat rose front-face
    over it, then a bright cool-pink sheen lip along the lit top edge — three
    distinct lit bands per tier, never a soft wash."""
    n = lobes
    top_pts = []
    for i in range(n + 1):
        t = i / n
        x = cx + span_l + (span_r - span_l) * t
        y = top_y + math.sin(t * math.pi) * drop * 0.18
        top_pts.append((x, y))
    bot_pts = []
    for i in range(n + 1):
        t = i / n
        x = cx + span_l + (span_r - span_l) * t
        swell = 0.6 + 0.7 * (1.0 - t)
        scal = abs(math.sin(t * n * math.pi)) * drop * 0.30
        lx = x + lean * (0.4 + 0.6 * (1.0 - t))
        y = top_y + drop * swell + scal
        bot_pts.append((lx, y))
    # full tier silhouette in the flat pinned rose first
    poly = top_pts + bot_pts[::-1]
    pygame.draw.polygon(surf, base, poly)
    # dark-core trough: a THIN cool-magenta band hugging only the underside of
    # the scallops — kept shallow so the lit flat rose, not the shade, dominates
    # the mass (the round-1 trough was too deep and darkened the whole skirt).
    trough = []
    for (x, y) in bot_pts:
        trough.append((x, y))
    for i in range(len(bot_pts) - 1, -1, -1):
        x, y = bot_pts[i]
        trough.append((x, y - drop * 0.18))
    pygame.draw.polygon(surf, shade, trough)
    # re-lay the bright FLAT front lobes over the trough so only the very deep
    # notch tips keep the cool-magenta shade (flat banding, never a gradient).
    # The flat-fill front now covers most of each lobe so rose is the dominant
    # value the eye reads at 32px.
    front = []
    for i in range(n + 1):
        t = i / n
        x = cx + span_l + (span_r - span_l) * t
        y = top_y + math.sin(t * math.pi) * drop * 0.18
        front.append((x, y))
    for i in range(n, -1, -1):
        t = i / n
        x = cx + span_l + (span_r - span_l) * t
        swell = 0.6 + 0.7 * (1.0 - t)
        lx = x + lean * (0.4 + 0.6 * (1.0 - t))
        scal = abs(math.sin(t * n * math.pi)) * drop * 0.30
        y = top_y + drop * swell + scal - drop * 0.10
        front.append((lx, y))
    pygame.draw.polygon(surf, base, front)
    # cool-pink sheen lip as a hard band hugging the lit top edge
    hi_pts = [(x, y) for x, y in top_pts]
    hi_lo = [(x, y + drop * 0.20) for x, y in top_pts[::-1]]
    pygame.draw.polygon(surf, hi, hi_pts + hi_lo)
    # re-lay flat rose just under the sheen band so the lip stays a thin band
    relay = [(x, y + drop * 0.16) for x, y in top_pts]
    relay += [(x, y + drop * 0.22) for x, y in top_pts[::-1]]
    pygame.draw.polygon(surf, base, relay)
    # marigold-gold trim picking out each scallop notch tip
    for i in range(n):
        t = (i + 0.5) / n
        x = cx + span_l + (span_r - span_l) * t
        swell = 0.6 + 0.7 * (1.0 - t)
        lx = x + lean * (0.4 + 0.6 * (1.0 - t))
        y = top_y + drop * swell
        pygame.draw.circle(surf, MARIGOLD, (int(lx), int(y)), max(2, int(SS * 0.9)))


# ── ZAPATEADA creature (drawn at supersample, then smoothscaled) ─────────────
DES_W, DES_H = 132, 158


def _build_zapateada_big():
    w, h = DES_W * SS, DES_H * SS
    s = new_surf(w, h)

    def P(fx, fy):
        return (int(fx * w), int(fy * h))

    # FIX2: the whole figure tilts ~18deg INTO the spin. The spine is a clear
    # DIAGONAL — skull/shoulders thrown to the upper-RIGHT, hips planted left,
    # the skirt mass counter-swung hard to the LOWER-LEFT. cx_top sits the
    # skull/ribcage high-right; cx_skirt piles the bell low-left.
    cx_top = w * 0.62
    cx_skirt = w * 0.40

    # ===== SWEPT SKIRT — drawn FIRST (behind torso). Hard triad-banded tiers,
    # all leaning LEFT, exaggerated counter-swing comma-curve. Hero rose mass. ==
    skirt = new_surf(w, h)
    # under-shadow petticoat lobe — kept SHALLOW (only the lower hem edge) so it
    # hints volume behind the front ruffles without darkening the whole mass; the
    # lit rose tiers below claim the bulk of the bell.
    pygame.draw.polygon(skirt, ROSE_SH, [
        P(0.28, 0.760), P(0.15, 0.860), P(0.26, 0.948),
        P(0.58, 0.948), P(0.64, 0.840), P(0.56, 0.760)])
    # three ruffle tiers, each wider + lower + swept further LEFT than the last.
    tier_specs = [
        # (top_y,   span_l,        span_r,       drop,        lobes, lean)
        (0.520, -w * 0.165, w * 0.115, h * 0.110, 4, -w * 0.060),
        (0.612, -w * 0.265, w * 0.130, h * 0.150, 5, -w * 0.110),
        (0.720, -w * 0.375, w * 0.145, h * 0.205, 6, -w * 0.165),
    ]
    for top_y, sl, sr, drop, lobes, lean in tier_specs:
        draw_ruffle_tier(skirt, cx_skirt, top_y * h, sl, sr, drop, lobes, lean,
                         ROSE_MID, ROSE_SH, ROSE_HI)
    # WHY: NO warm-bone triad_sheen + NO warm core_shade on the skirt — those
    # were what washed the lit fill toward salmon-brick in round 1. Curvature is
    # carried entirely by the per-tier hard rose bands, so the mass stays in the
    # cool rose-magenta lane.
    s.blit(skirt, (0, 0))

    # ===== BONE LEGS in a zapateado stomp — over the petticoat hem. One planted,
    # one toe-down kicked back. ================================================
    legs = new_surf(w, h)
    hip = (cx_skirt + w * 0.05, h * 0.555)
    pygame.draw.line(legs, BONE, (int(hip[0] - w * 0.02), int(hip[1])),
                     (int(cx_skirt - w * 0.05), int(h * 0.915)), max(4, int(SS * 1.6)))
    pygame.draw.polygon(legs, BONE, [
        P(0.28, 0.910), P(0.37, 0.910), P(0.41, 0.960), P(0.26, 0.960)])
    pygame.draw.line(legs, BONE, (int(hip[0] + w * 0.03), int(hip[1] + h * 0.01)),
                     (int(cx_skirt + w * 0.18), int(h * 0.885)), max(4, int(SS * 1.6)))
    pygame.draw.polygon(legs, BONE, [
        P(0.56, 0.862), P(0.63, 0.878), P(0.61, 0.948), P(0.55, 0.912)])
    for kx, ky in ((0.350, 0.748), (0.520, 0.748)):
        pygame.draw.circle(legs, INK, P(kx, ky), max(2, SS))
    core_shade(legs, BONE_SH, 110)
    triad_sheen(legs, top_a=110, bot_a=40)
    s.blit(legs, (0, 0))

    # ===== SLIM RIBCAGE + SPINE torso, a clear DIAGONAL leaning into the turn.
    # FIX3: clean readable ribcage — fewer, cleaner rib arcs. ==================
    torso = new_surf(w, h)
    spine_top = (cx_top, h * 0.285)
    spine_bot = (cx_skirt + w * 0.06, h * 0.520)
    pygame.draw.line(torso, BONE, (int(spine_top[0]), int(spine_top[1])),
                     (int(spine_bot[0]), int(spine_bot[1])), max(5, int(SS * 1.7)))
    # FIX3: only 3 clean rib arcs slung off the diagonal spine, narrowing down
    for i in range(3):
        t = i / 2.0
        ry = spine_top[1] + (spine_bot[1] - spine_top[1]) * (0.22 + 0.58 * t)
        rcx = spine_top[0] + (spine_bot[0] - spine_top[0]) * (0.22 + 0.58 * t)
        rw = w * (0.110 - 0.040 * t)
        rh = h * (0.044 - 0.010 * t)
        rect = (int(rcx - rw), int(ry - rh), int(rw * 2), int(rh * 2))
        pygame.draw.arc(torso, BONE, rect, math.radians(192), math.radians(348),
                        max(4, SS + 1))
    pygame.draw.polygon(torso, BONE, [
        (int(spine_bot[0] - w * 0.055), int(spine_bot[1] - h * 0.02)),
        (int(spine_bot[0] + w * 0.055), int(spine_bot[1] - h * 0.02)),
        (int(spine_bot[0] + w * 0.03), int(spine_bot[1] + h * 0.04)),
        (int(spine_bot[0] - w * 0.03), int(spine_bot[1] + h * 0.04))])
    core_shade(torso, BONE_SH, 110, ell=(0.42, 0.32, 0.48, 0.40))
    triad_sheen(torso, top_a=120, bot_a=40, ell=(0.38, 0.22, 0.40, 0.36))
    s.blit(torso, (0, 0))

    # ===== ARMS — FIX2: the raised arm arcs HIGH and SEPARATE, with a clear
    # sky-gap between the arm and the cranium (that negative space is what reads
    # as "arm thrown overhead" at 32px). One trailing low arm flicked out. =====
    arms = new_surf(w, h)
    shoulder = (cx_top + w * 0.01, h * 0.320)
    # raised arm: shoulder -> elbow swung OUT to the right -> wrist arced ABOVE
    # and to the right of the skull (NOT over the crown — leaves the sky-gap)
    elbow_up = (cx_top + w * 0.185, h * 0.215)
    wrist_up = (cx_top + w * 0.165, h * 0.060)
    pygame.draw.lines(arms, BONE, False,
                      [(int(shoulder[0]), int(shoulder[1])),
                       (int(elbow_up[0]), int(elbow_up[1])),
                       (int(wrist_up[0]), int(wrist_up[1]))], max(4, int(SS * 1.5)))
    pygame.draw.circle(arms, INK, (int(elbow_up[0]), int(elbow_up[1])), max(2, SS))
    pygame.draw.circle(arms, BONE, (int(wrist_up[0]), int(wrist_up[1])),
                       max(3, int(SS * 1.3)))
    # trailing low arm: shoulder -> elbow low-left -> wrist flicked out far LEFT
    elbow_lo = (cx_top - w * 0.130, h * 0.430)
    wrist_lo = (cx_skirt - w * 0.175, h * 0.500)
    pygame.draw.lines(arms, BONE, False,
                      [(int(shoulder[0] - w * 0.02), int(shoulder[1] + h * 0.01)),
                       (int(elbow_lo[0]), int(elbow_lo[1])),
                       (int(wrist_lo[0]), int(wrist_lo[1]))], max(4, int(SS * 1.4)))
    pygame.draw.circle(arms, INK, (int(elbow_lo[0]), int(elbow_lo[1])), max(2, SS))
    pygame.draw.circle(arms, BONE, (int(wrist_lo[0]), int(wrist_lo[1])),
                       max(3, int(SS * 1.2)))
    core_shade(arms, BONE_SH, 100)
    triad_sheen(arms, top_a=110, bot_a=36)
    s.blit(arms, (0, 0))

    # FIX4: turquoise ribbon trailing from the raised wrist in a LONG curl that
    # follows the spin direction — a strong motion cue + restates the cool accent.
    ribbon = new_surf(w, h)
    rpts = []
    for i in range(20):
        t = i / 19
        # a long S-curl sweeping up, back over to the left, then down — trailing
        a = math.radians(-60 + 300 * t)
        rad = w * 0.20 * (0.3 + 1.1 * t)
        rx2 = wrist_up[0] + math.cos(a) * rad - w * 0.18 * t
        ry2 = wrist_up[1] - h * 0.02 + math.sin(a) * rad * 0.55 - h * 0.04 * t
        rpts.append((rx2, ry2))
    pygame.draw.lines(ribbon, TEAL, False,
                      [(int(x), int(y)) for x, y in rpts], max(3, int(SS * 1.2)))
    pygame.draw.lines(ribbon, TEAL_SH, False,
                      [(int(x), int(y + SS)) for x, y in rpts], max(2, SS // 2))
    s.blit(ribbon, (0, 0))

    # ===== SKULL — small, delicate; tilted INTO the lean (sits high-right on the
    # diagonal). Painted lash-flicks, joyful open grin, coral temple-rose. ======
    skull = new_surf(w, h)
    sk_cx = cx_top + w * 0.015
    sk_cy = h * 0.205
    skw = w * 0.112
    skh = h * 0.100
    pygame.draw.ellipse(skull, BONE, (int(sk_cx - skw), int(sk_cy - skh),
                                      int(skw * 2), int(skh * 2.0)))
    pygame.draw.polygon(skull, BONE, [
        (int(sk_cx - skw * 0.66), int(sk_cy + skh * 0.55)),
        (int(sk_cx + skw * 0.66), int(sk_cy + skh * 0.55)),
        (int(sk_cx + skw * 0.32), int(sk_cy + skh * 1.5)),
        (int(sk_cx - skw * 0.32), int(sk_cy + skh * 1.5))])
    core_shade(skull, BONE_SH, 110, ell=(0.42, 0.14, 0.40, 0.34))
    triad_sheen(skull, top_a=130, bot_a=40, ell=(0.38, 0.08, 0.34, 0.30))
    s.blit(skull, (0, 0))

    face = new_surf(w, h)
    eye_y = sk_cy - skh * 0.05
    eye_dx = skw * 0.46
    eye_r = skw * 0.34
    for sgn in (-1, 1):
        ex = sk_cx + sgn * eye_dx
        pygame.draw.circle(face, INK, (int(ex), int(eye_y)), int(eye_r))
        pygame.draw.circle(face, ROSE, (int(ex), int(eye_y)), int(eye_r * 0.6))
        pygame.draw.circle(face, _lite(ROSE, 0.5),
                           (int(ex - eye_r * 0.2), int(eye_y - eye_r * 0.2)),
                           int(eye_r * 0.28))
        for k in range(3):
            la = math.radians(-150 + sgn * (10 + k * 22))
            lx0 = ex + math.cos(la) * eye_r
            ly0 = eye_y + math.sin(la) * eye_r
            lx1 = ex + math.cos(la) * eye_r * 1.7
            ly1 = eye_y + math.sin(la) * eye_r * 1.7
            pygame.draw.line(face, INK, (int(lx0), int(ly0)),
                             (int(lx1), int(ly1)), max(2, SS // 2 + 1))
    ny = sk_cy + skh * 0.34
    pygame.draw.polygon(face, INK, [
        (int(sk_cx), int(ny + skh * 0.22)),
        (int(sk_cx - skw * 0.12), int(ny - skh * 0.02)),
        (int(sk_cx + skw * 0.12), int(ny - skh * 0.02))])
    smy = sk_cy + skh * 0.98
    mouth = pygame.Rect(int(sk_cx - skw * 0.5), int(smy - skh * 0.22),
                        int(skw * 1.0), int(skh * 0.55))
    pygame.draw.arc(face, INK, mouth, math.radians(196), math.radians(344),
                    max(4, SS + 1))
    pygame.draw.ellipse(face, INK, (int(sk_cx - skw * 0.42), int(smy - skh * 0.04),
                                    int(skw * 0.84), int(skh * 0.46)))
    for i in range(-2, 3):
        tx = sk_cx + i * skw * 0.20
        pygame.draw.line(face, BONE, (int(tx), int(smy)),
                         (int(tx), int(smy + skh * 0.22)), max(2, SS // 2))
    s.blit(face, (0, 0))

    rose = new_surf(w, h)
    rose_x = sk_cx - skw * 1.05
    rose_y = sk_cy - skh * 0.55
    draw_marigold(rose, rose_x, rose_y, w * 0.052,
                  base=CORAL, shade=CORAL_SH, hi=_lite(CORAL, 0.5),
                  petals=7, core=ROSE)
    s.blit(rose, (0, 0))

    return s


def build_zapateada():
    big = _build_zapateada_big()
    small = pygame.transform.smoothscale(big, (DES_W, DES_H))
    return grow_outline(small, INK, 1)


# ── PROP: ribbon-dance / liston maypole + its top<->bottom PILLAR mirror ──────
PROP_W, PROP_H = 64, 150


def _build_dancepole_big():
    w, h = PROP_W * SS, PROP_H * SS
    s = new_surf(w, h)
    cx = w * 0.5

    pole_w = w * 0.16
    pole_top = h * 0.300
    pole_bot = h * 0.975
    pole = new_surf(w, h)
    pygame.draw.rect(pole, BONE, (int(cx - pole_w / 2), int(pole_top),
                                  int(pole_w), int(pole_bot - pole_top)))
    band_n = 11
    for i in range(band_n):
        by = pole_top + (pole_bot - pole_top) * i / band_n
        by2 = pole_top + (pole_bot - pole_top) * (i + 0.5) / band_n
        col = TEAL if i % 2 == 0 else ROSE
        pygame.draw.line(pole, col, (int(cx - pole_w / 2), int(by)),
                         (int(cx + pole_w / 2), int(by2)), max(3, int(SS * 0.9)))
    core_shade(pole, BONE_SH, 120)
    triad_sheen(pole, top_a=120, bot_a=40)
    s.blit(pole, (0, 0))

    # gap-edge CAP: a SYMMETRIC RADIAL ribbon-rosette + a castanet pair finial.
    cap = new_surf(w, h)
    ros_cx, ros_cy = cx, h * 0.255
    R_out = w * 0.42
    R_in = w * 0.24
    for ring, (rr, col, sh) in enumerate(((R_out, ROSE, ROSE_SH),
                                          (R_in, ROSE_HI, ROSE_SH))):
        petals = 12 if ring == 0 else 9
        for k in range(petals):
            a = (k / petals) * math.tau + (0.0 if ring == 0
                                           else math.tau / (petals * 2))
            tip = (ros_cx + math.cos(a) * rr, ros_cy + math.sin(a) * rr)
            perp = a + math.pi / 2
            bw = rr * 0.30
            base_pt = (ros_cx + math.cos(a) * rr * 0.32,
                       ros_cy + math.sin(a) * rr * 0.32)
            pygame.draw.polygon(cap, sh, [
                (base_pt[0] + math.cos(perp) * bw, base_pt[1] + math.sin(perp) * bw),
                (base_pt[0] - math.cos(perp) * bw, base_pt[1] - math.sin(perp) * bw),
                tip])
            pygame.draw.polygon(cap, col, [
                (base_pt[0] + math.cos(perp) * bw * 0.7,
                 base_pt[1] + math.sin(perp) * bw * 0.7),
                (base_pt[0] - math.cos(perp) * bw * 0.7,
                 base_pt[1] - math.sin(perp) * bw * 0.7),
                (ros_cx + math.cos(a) * rr * 0.86,
                 ros_cy + math.sin(a) * rr * 0.86)])
    pygame.draw.circle(cap, MARIGOLD, (int(ros_cx), int(ros_cy)), int(R_in * 0.7))
    pygame.draw.circle(cap, INK, (int(ros_cx), int(ros_cy)), int(R_in * 0.46))
    pygame.draw.circle(cap, TEAL, (int(ros_cx), int(ros_cy)), int(R_in * 0.38))
    pygame.draw.circle(cap, _lite(TEAL, 0.5),
                       (int(ros_cx - R_in * 0.14), int(ros_cy - R_in * 0.14)),
                       int(R_in * 0.18))
    # WHY: skip the warm core_shade on the rosette (same salmon-mud risk); the
    # cool ROSE_SH lobes already carry the form, keeping the cap in the rose lane.
    triad_sheen(cap, top_a=80, bot_a=28, ell=(0.16, 0.08, 0.50, 0.46))
    s.blit(cap, (0, 0))

    cast = new_surf(w, h)
    cast_y = h * 0.470
    for sgn in (-1, 1):
        cxr = cx + sgn * w * 0.135
        pygame.draw.circle(cast, MARIGOLD, (int(cxr), int(cast_y)), int(w * 0.10))
        pygame.draw.circle(cast, MARI_SH, (int(cxr), int(cast_y)), int(w * 0.10),
                           max(2, SS // 2))
        pygame.draw.circle(cast, _lite(MARIGOLD, 0.5),
                           (int(cxr - w * 0.03), int(cast_y - w * 0.03)),
                           int(w * 0.035))
    pygame.draw.line(cast, TEAL, (int(cx - w * 0.135), int(cast_y)),
                     (int(cx + w * 0.135), int(cast_y)), max(2, SS // 2))
    s.blit(cast, (0, 0))
    return s


def build_dancepole():
    big = _build_dancepole_big()
    small = pygame.transform.smoothscale(big, (PROP_W, PROP_H))
    return grow_outline(small, INK, 1)


def build_pillar(height=300):
    prop = build_dancepole()
    pw, ph = prop.get_size()
    cap_h = int(ph * 0.44)
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
zap = build_zapateada()
pole = build_dancepole()
pillar, cap, shaft = build_pillar(300)

top_pillar = new_surf(pole.get_width(), 300)
cap_h = int(pole.get_height() * 0.44)
top_shaft_h = 300 - cap_h
y = 0
while y < top_shaft_h:
    top_pillar.blit(shaft, (0, y))
    y += shaft.get_height()
top_pillar.blit(cap, (0, top_shaft_h))
bot_pillar, _, _ = build_pillar(300)


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
    return pygame.transform.smoothscale(
        spr, (max(1, round(w * sc)), max(1, round(h * sc))))


SHEET_W, SHEET_H = 1000, 820
sheet = new_surf(SHEET_W, SHEET_H)
sheet.fill(BG)


def sky_panel(rect, top=(108, 170, 214), bot=(184, 214, 232)):
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
sheet.blit(ftitle.render("ZAPATEADA  —  round 2", True, TITLE), (28, 18))
sheet.blit(fbody.render(
    "Ballet folklorico calaca MID-TWIRL: skull+torso tilted INTO the spin, arm thrown overhead "
    "(sky-gap clear of the head), skirt counter-swung off-axis. The family's ONLY asymmetric read.",
    True, SUB), (28, 54))
sheet.blit(ftiny.render(
    "FIX: hero skirt repainted to pinned ROSE-MAGENTA (214,72,86) with its OWN cool triad "
    "(magenta trough / cool-pink sheen) - no warm-bone wash. Pinker/cooler than chile + rust.",
    True, ACCENT), (28, 76))

M = 28
top_y = 100

hero_rect = pygame.Rect(M, top_y, 320, 456)
sky_panel(hero_rect)
sheet.blit(fhead.render("Zapateada  (hero)", True, TITLE),
           (hero_rect.x + 12, hero_rect.y + 8))
sheet.blit(ftiny.render("diagonal lean + overhead arm + counter-swung skirt = MOTION",
                        True, (235, 242, 252)),
           (hero_rect.x + 12, hero_rect.bottom - 22))
blit_center(scaled(zap, 2.6), hero_rect, dy=20)

prop_rect = pygame.Rect(hero_rect.right + 18, top_y, 220, 456)
sky_panel(prop_rect, top=(196, 184, 214), bot=(214, 200, 222))
sheet.blit(fhead.render("Dance-pole prop", True, TITLE),
           (prop_rect.x + 12, prop_rect.y + 8))
blit_center(scaled(pole, 2.5), prop_rect, dy=18)
sheet.blit(ftiny.render("wound-ribbon pole +", True, (60, 50, 70)),
           (prop_rect.x + 12, prop_rect.bottom - 38))
sheet.blit(ftiny.render("RADIAL rosette + castanets", True, (60, 50, 70)),
           (prop_rect.x + 12, prop_rect.bottom - 22))

pil_rect = pygame.Rect(prop_rect.right + 18, top_y, 366, 456)
sky_panel(pil_rect, top=(120, 178, 218), bot=(190, 218, 234))
sheet.blit(fhead.render("Pillar mirror (gap)", True, TITLE),
           (pil_rect.x + 12, pil_rect.y + 8))
clip = sheet.get_clip()
inner = pil_rect.inflate(-8, -8)
sheet.set_clip(inner)
GAP = 150
pcx = pil_rect.centerx - pole.get_width() // 2
gap_top = pil_rect.y + 38
sheet.blit(top_pillar, (pcx, gap_top - 130))
sheet.blit(bot_pillar, (pcx, gap_top + GAP))
sheet.set_clip(clip)
sheet.blit(ftiny.render("swept skirt resolved to a SYMMETRIC radial rosette on-axis",
                        True, (235, 242, 252)), (pil_rect.x + 12, pil_rect.bottom - 22))

# --- BOTTOM: gameplay-scale read row + silhouette + RED-SPLIT proof chips ---
row_y = hero_rect.bottom + 16
row_rect = pygame.Rect(M, row_y, SHEET_W - 2 * M, SHEET_H - row_y - 18)
pygame.draw.rect(sheet, PANEL2, row_rect, border_radius=10)
sheet.blit(fhead.render("Gameplay scale + red-split proof", True, TITLE),
           (row_rect.x + 12, row_rect.y + 8))


def chip(rect, top=(112, 172, 216), bot=(186, 216, 232)):
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


zap32 = fit_h(zap, 32)
zap48 = fit_h(zap, 48)
pole32 = fit_h(pole, 40)

cy = row_rect.y + 44
c1 = pygame.Rect(row_rect.x + 16, cy, 84, 104)
chip(c1)
blit_center(zap32, c1)
sheet.blit(ftiny.render("32px", True, (24, 30, 44)), (c1.x + 4, c1.bottom - 16))

c2 = pygame.Rect(c1.right + 12, cy, 110, 104)
chip(c2)
z = pygame.transform.scale(zap32, (zap32.get_width() * 3, zap32.get_height() * 3))
blit_center(z, c2)
sheet.blit(ftiny.render("32px x3", True, (24, 30, 44)), (c2.x + 4, c2.bottom - 16))

c3 = pygame.Rect(c2.right + 12, cy, 96, 104)
chip(c3)
blit_center(zap48, c3)
sheet.blit(ftiny.render("48px", True, (24, 30, 44)), (c3.x + 4, c3.bottom - 16))

# pure-black silhouette panel: proves the asymmetric twirl reads with zero hue
c_sil = pygame.Rect(c3.right + 12, cy, 90, 104)
chip(c_sil, top=(230, 234, 240), bot=(230, 234, 240))
inkmask = pygame.mask.from_surface(zap48, 40).to_surface(
    setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
blit_center(inkmask, c_sil)
sheet.blit(ftiny.render("silhouette", True, (40, 40, 48)),
           (c_sil.x + 4, c_sil.bottom - 16))

c4 = pygame.Rect(c_sil.right + 12, cy, 58, 104)
chip(c4, top=(196, 184, 214), bot=(214, 200, 222))
blit_center(pole32, c4)
sheet.blit(ftiny.render("prop", True, (40, 34, 54)), (c4.x + 4, c4.bottom - 16))

c5 = pygame.Rect(c4.right + 12, cy, 100, 104)
chip(c5, top=(120, 178, 218), bot=(190, 218, 234))
mini_top = fit_h(top_pillar, 64)
mini_bot = fit_h(bot_pillar, 64)
clip = sheet.get_clip()
sheet.set_clip(c5)
mcx = c5.centerx - mini_top.get_width() // 2
sheet.blit(mini_top, (mcx, c5.y - 18))
sheet.blit(mini_bot, (mcx, c5.y + 70))
sheet.set_clip(clip)
sheet.blit(ftiny.render("pillar", True, (235, 242, 252)), (c5.x + 4, c5.bottom - 16))

# RED-SPLIT proof: three 32px swatches side by side, same dark bg, with the
# skirt's actual sampled flat-fill to PROVE rose != chile != rust.
proof_x = c5.right + 18
sheet.blit(ftiny.render("RED SPLIT @32px:", True, ACCENT), (proof_x, cy - 2))
sw = 44
sgap = 8
labels = [("Zapateada", ROSE, "rose-magenta"),
          ("Comelona", CHILE, "chile-orange"),
          ("Jinete", RUST, "brick-rust")]
for i, (nm, col, lane) in enumerate(labels):
    sx = proof_x + i * (sw + sgap)
    sy = cy + 18
    pygame.draw.rect(sheet, (24, 28, 40), (sx - 2, sy - 2, sw + 4, sw + 4),
                     border_radius=5)
    pygame.draw.rect(sheet, col, (sx, sy, sw, sw), border_radius=4)
    pygame.draw.rect(sheet, INK, (sx, sy, sw, sw), 1, border_radius=4)
    sheet.blit(ftiny.render(nm, True, (230, 234, 244)), (sx - 2, sy + sw + 2))
    sheet.blit(ftiny.render(str(col), True, (170, 178, 200)), (sx - 4, sy + sw + 16))

# sampled-from-render proof: pull the actual flat-fill pixel off the rendered
# 48px hero skirt so the chip can't lie about what shipped.
sample_pt = None
for (fx, fy) in ((0.30, 0.78), (0.34, 0.74), (0.28, 0.82)):
    px = int(zap48.get_width() * fx)
    py = int(zap48.get_height() * fy)
    c = zap48.get_at((px, py))
    if c.a > 200 and c.r > 120 and c.r > c.b:
        sample_pt = (c.r, c.g, c.b)
        break
sx0 = proof_x
sy0 = cy + 18 + sw + 32
sheet.blit(ftiny.render("sampled from rendered skirt:", True, (200, 208, 226)),
           (sx0, sy0))
if sample_pt:
    pygame.draw.rect(sheet, sample_pt, (sx0, sy0 + 16, 40, 26), border_radius=4)
    pygame.draw.rect(sheet, INK, (sx0, sy0 + 16, 40, 26), 1, border_radius=4)
    sheet.blit(ftiny.render(str(sample_pt) + "  (target 214,72,86)", True,
                            (220, 226, 240)), (sx0 + 48, sy0 + 22))

sheet.blit(ftiny.render(
    "Read: diagonal spine + overhead arm with a sky-gap + counter-swung hem = the family's only",
    True, SUB), (proof_x, sy0 + 50))
sheet.blit(ftiny.render(
    "in-MOTION silhouette. Hero skirt now firmly in the cool rose-magenta lane, clear of rust.",
    True, SUB), (proof_x, sy0 + 66))

os.makedirs(_OUT_DIR, exist_ok=True)
out_path = os.path.join(_OUT_DIR, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
if sample_pt:
    print("sampled skirt flat-fill:", sample_pt, "target (214,72,86)")
