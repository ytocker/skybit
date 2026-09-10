"""ZAPATEADA — round 1 review sheet (Mariachi warm-skeleton family, locked5).

Lead facet DANCE / MOTION: a ballet folklorico dancer calaca frozen mid-twirl —
one bony arm arced overhead, a huge ruffled skirt fanned OFF-AXIS by the spin,
bone legs in a pointed zapateado stomp. The asymmetric in-motion silhouette is
the signature: it is the family's ONLY off-axis, leaning, in-motion read, so the
swept skirt + lean carry the whole design.

Red-split pin: the hero skirt mass is ROSE-MAGENTA (214,72,86) — pinker/cooler,
clearly off Comelona's orange-chile and Jinete's brown-rust.

Prop->pillar resolves the off-axis swept skirt into a SYMMETRIC radial
ribbon-rosette on the pole axis (a fluted dance/maypole shaft + a radial fan
rosette + castanet pair as the gap-edge cap) so the mirror reads balanced even
though the creature stays deliberately asymmetric.

House grammar: chibi proportions, FLAT saturated fills + hard ink keylines, form
via dark-core -> flat-fill -> top-left rim-sheen TRIAD (never soft gradient), a
1px outline grown from the alpha mask, supersample -> smoothscale. Scary-CUTE.

Run headless (SDL_VIDEODRIVER=dummy). Writes round_1.png beside this script.
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
SHEEN     = (250, 242, 222)   # top-left rim-sheen


def _dark(c, f=0.62):
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f))


def _lite(c, f=0.4):
    return tuple(int(c[i] + (255 - c[i]) * f) for i in range(3))


ROSE_SH   = _dark(ROSE, 0.60)        # ruffle trough dark-core
ROSE_HI   = _lite(ROSE, 0.42)        # ruffle lit lip
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
    span_l (wearer's right, the side the spin throws the skirt to) and span_r.
    `lean` (px) skews every lobe's bottom toward the swept side so the tier
    reads as motion in the LEAN, not as extra tiers. Drawn flat: front-face
    fill, a dark-core trough band, then a sheen lip along the top."""
    # top edge is a shallow arc tucked under the previous tier; bottom edge is
    # a row of scallop lobes whose depth swells toward the swept (left) side.
    n = lobes
    top_pts = []
    for i in range(n + 1):
        t = i / n
        x = cx + span_l + (span_r - span_l) * t
        # tuck the tier top into a gentle smile so tiers stack like a bell
        y = top_y + math.sin(t * math.pi) * drop * 0.18
        top_pts.append((x, y))
    bot_pts = []
    for i in range(n + 1):
        t = i / n
        x = cx + span_l + (span_r - span_l) * t
        # scallop: each lobe dips; lobes deeper on the swept (left, t->0) side
        swell = 0.6 + 0.7 * (1.0 - t)
        scal = abs(math.sin(t * n * math.pi)) * drop * 0.30
        # the LEAN: bottom edge slides toward the swept side proportional to drop
        lx = x + lean * (0.4 + 0.6 * (1.0 - t))
        y = top_y + drop * swell + scal
        bot_pts.append((lx, y))
    poly = top_pts + bot_pts[::-1]
    pygame.draw.polygon(surf, base, poly)
    # dark-core trough: a band hugging the underside of the scallops
    trough = []
    for i, (x, y) in enumerate(bot_pts):
        trough.append((x, y))
    for i in range(len(bot_pts) - 1, -1, -1):
        x, y = bot_pts[i]
        trough.append((x, y - drop * 0.34))
    pygame.draw.polygon(surf, shade, trough)
    # re-lay the bright front lobes over the trough so only the deep notches
    # stay shaded (flat banding, never a gradient)
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
        y = top_y + drop * swell + scal - drop * 0.30
        front.append((lx, y))
    pygame.draw.polygon(surf, base, front)
    # marigold-gold trim picking out each scallop notch tip
    for i in range(n):
        t = (i + 0.5) / n
        x = cx + span_l + (span_r - span_l) * t
        swell = 0.6 + 0.7 * (1.0 - t)
        lx = x + lean * (0.4 + 0.6 * (1.0 - t))
        scal = abs(math.sin((i + 0.5) * math.pi)) * drop * 0.30
        y = top_y + drop * swell + scal
        pygame.draw.circle(surf, MARIGOLD, (int(lx), int(y)), max(2, int(SS * 0.9)))
    # sheen lip along the lit top edge
    pygame.draw.lines(surf, hi, False, [(int(x), int(y)) for x, y in top_pts],
                      max(2, SS))


# ── ZAPATEADA creature (drawn at supersample, then smoothscaled) ─────────────
# Wide design box: the swept skirt claims the lower-LEFT, the raised arm + skull
# claim the upper-RIGHT, so the figure reads as a diagonal in-motion twirl.
DES_W, DES_H = 132, 150


def _build_zapateada_big():
    w, h = DES_W * SS, DES_H * SS
    s = new_surf(w, h)

    def P(fx, fy):
        return (int(fx * w), int(fy * h))

    # The whole figure leans INTO the turn: torso axis tips right at the top,
    # the skirt mass swings LEFT at the bottom — a comma-curve. cx_top is where
    # the skull/ribcage sit; cx_skirt is where the skirt mass piles up.
    cx_top = w * 0.56
    cx_skirt = w * 0.42

    # ===== SWEPT SKIRT — drawn FIRST (behind torso): 3 hard triad-lit ruffle
    # tiers ALL leaning ONE way (left), built into a comma-curve bell that fans
    # off-axis. This is the hero rose-magenta mass + the signature silhouette. =
    skirt = new_surf(w, h)
    waist_y = h * 0.520
    # under-shadow petticoat lobe anchoring the bell to the legs (tan-bone-ish
    # rose shade so the skirt has volume behind the front ruffles)
    pygame.draw.polygon(skirt, ROSE_SH, [
        P(0.30, 0.560), P(0.16, 0.760), P(0.30, 0.940),
        P(0.62, 0.940), P(0.66, 0.700), P(0.58, 0.560)])
    # three ruffle tiers, each wider + lower + swept further LEFT than the last,
    # so the bell flares and the lean accumulates toward the hem.
    tier_specs = [
        # (top_y,   span_l,        span_r,       drop,        lobes, lean)
        (0.520, -w * 0.150, w * 0.120, h * 0.110, 4, -w * 0.045),
        (0.610, -w * 0.235, w * 0.135, h * 0.150, 5, -w * 0.085),
        (0.715, -w * 0.330, w * 0.150, h * 0.200, 6, -w * 0.130),
    ]
    for top_y, sl, sr, drop, lobes, lean in tier_specs:
        draw_ruffle_tier(skirt, cx_skirt, top_y * h, sl, sr, drop, lobes, lean,
                         ROSE, ROSE_SH, ROSE_HI)
    core_shade(skirt, ROSE_SH, 120, ell=(0.18, 0.62, 0.62, 0.42))
    triad_sheen(skirt, top_a=96, bot_a=30, ell=(0.10, 0.50, 0.50, 0.34))
    s.blit(skirt, (0, 0))

    # ===== BONE LEGS in a zapateado stomp — drawn over the petticoat hem so the
    # pointed feet read below the skirt. One leg planted, one toe-down mid-stomp.
    legs = new_surf(w, h)
    hip = (cx_skirt + w * 0.04, h * 0.560)
    # planted leg (wearer's right, screen left) — bowed femur to a flat foot
    pygame.draw.line(legs, BONE, (int(hip[0] - w * 0.02), int(hip[1])),
                     (int(cx_skirt - w * 0.06), int(h * 0.910)), max(4, int(SS * 1.6)))
    # pointed planted foot
    pygame.draw.polygon(legs, BONE, [
        P(0.27, 0.905), P(0.36, 0.905), P(0.40, 0.955), P(0.25, 0.955)])
    # stomp leg (toe-down, kicked back to the right) — the motion tell
    pygame.draw.line(legs, BONE, (int(hip[0] + w * 0.03), int(hip[1] + h * 0.01)),
                     (int(cx_skirt + w * 0.17), int(h * 0.880)), max(4, int(SS * 1.6)))
    # pointed toe-down foot
    pygame.draw.polygon(legs, BONE, [
        P(0.55, 0.860), P(0.62, 0.875), P(0.60, 0.945), P(0.54, 0.910)])
    # knee + ankle ink ticks
    for kx, ky in ((0.345, 0.745), (0.515, 0.745)):
        pygame.draw.circle(legs, INK, P(kx, ky), max(2, SS))
    core_shade(legs, BONE_SH, 110)
    triad_sheen(legs, top_a=110, bot_a=40)
    s.blit(legs, (0, 0))

    # ===== SLIM RIBCAGE + SPINE torso (bare bone above the skirt waist), leaning
    # INTO the turn so the figure reads dynamic, not standing. =================
    torso = new_surf(w, h)
    spine_top = (cx_top, h * 0.300)
    spine_bot = (cx_skirt + w * 0.05, h * 0.520)
    # spine column
    pygame.draw.line(torso, BONE, (int(spine_top[0]), int(spine_top[1])),
                     (int(spine_bot[0]), int(spine_bot[1])), max(4, int(SS * 1.5)))
    # ribcage: 4 leaning rib arcs slung off the spine, narrowing to the waist
    for i in range(4):
        t = i / 3.0
        ry = spine_top[1] + (spine_bot[1] - spine_top[1]) * (0.18 + 0.62 * t)
        rcx = spine_top[0] + (spine_bot[0] - spine_top[0]) * (0.18 + 0.62 * t)
        rw = w * (0.115 - 0.052 * t)
        rh = h * (0.045 - 0.010 * t)
        rect = (int(rcx - rw), int(ry - rh), int(rw * 2), int(rh * 2))
        pygame.draw.arc(torso, BONE, rect, math.radians(186), math.radians(354),
                        max(3, SS))
    # a small pelvis wedge tucking into the skirt waist
    pygame.draw.polygon(torso, BONE, [
        (int(spine_bot[0] - w * 0.055), int(spine_bot[1] - h * 0.02)),
        (int(spine_bot[0] + w * 0.055), int(spine_bot[1] - h * 0.02)),
        (int(spine_bot[0] + w * 0.03), int(spine_bot[1] + h * 0.04)),
        (int(spine_bot[0] - w * 0.03), int(spine_bot[1] + h * 0.04))])
    core_shade(torso, BONE_SH, 110, ell=(0.40, 0.34, 0.50, 0.40))
    triad_sheen(torso, top_a=120, bot_a=40, ell=(0.34, 0.24, 0.40, 0.36))
    s.blit(torso, (0, 0))

    # ===== ARMS — one arced OVERHEAD (the dance flourish), one swept low across
    # the body. Turquoise ribbon trails from the raised wrist. =================
    arms = new_surf(w, h)
    shoulder = (cx_top + w * 0.01, h * 0.330)
    # raised arm: shoulder -> elbow up-right -> wrist arced over the skull
    elbow_up = (cx_top + w * 0.155, h * 0.230)
    wrist_up = (cx_top + w * 0.075, h * 0.110)
    pygame.draw.lines(arms, BONE, False,
                      [(int(shoulder[0]), int(shoulder[1])),
                       (int(elbow_up[0]), int(elbow_up[1])),
                       (int(wrist_up[0]), int(wrist_up[1]))], max(4, int(SS * 1.4)))
    pygame.draw.circle(arms, INK, (int(elbow_up[0]), int(elbow_up[1])), max(2, SS))
    # hand at the arc top
    pygame.draw.circle(arms, BONE, (int(wrist_up[0]), int(wrist_up[1])),
                       max(3, int(SS * 1.2)))
    # low sweeping arm: shoulder -> elbow low-left -> wrist flicked out left
    elbow_lo = (cx_top - w * 0.110, h * 0.420)
    wrist_lo = (cx_skirt - w * 0.140, h * 0.470)
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

    # turquoise ribbon trailing from the raised wrist, curling up + back (motion)
    ribbon = new_surf(w, h)
    rpts = []
    rx, ry = wrist_up
    for i in range(14):
        t = i / 13
        a = math.radians(-150 + 220 * t)          # sweep up and around
        rx2 = wrist_up[0] + math.cos(a) * w * 0.16 * (0.4 + t)
        ry2 = wrist_up[1] - h * 0.10 * t + math.sin(a) * h * 0.05
        rpts.append((rx2, ry2))
    if len(rpts) >= 2:
        pygame.draw.lines(ribbon, TEAL, False,
                          [(int(x), int(y)) for x, y in rpts], max(3, int(SS * 1.1)))
        pygame.draw.lines(ribbon, TEAL_SH, False,
                          [(int(x), int(y + SS)) for x, y in rpts], max(2, SS // 2))
    s.blit(ribbon, (0, 0))

    # ===== SKULL — small, delicate; tilted INTO the lean. Painted lash-flicks,
    # joyful open grin, a coral rose tucked at the temple. =====================
    skull = new_surf(w, h)
    sk_cx = cx_top + w * 0.015
    sk_cy = h * 0.215
    skw = w * 0.115
    skh = h * 0.105
    pygame.draw.ellipse(skull, BONE, (int(sk_cx - skw), int(sk_cy - skh),
                                      int(skw * 2), int(skh * 2.0)))
    # jaw wedge
    pygame.draw.polygon(skull, BONE, [
        (int(sk_cx - skw * 0.66), int(sk_cy + skh * 0.55)),
        (int(sk_cx + skw * 0.66), int(sk_cy + skh * 0.55)),
        (int(sk_cx + skw * 0.32), int(sk_cy + skh * 1.5)),
        (int(sk_cx - skw * 0.32), int(sk_cy + skh * 1.5))])
    core_shade(skull, BONE_SH, 110, ell=(0.40, 0.16, 0.40, 0.34))
    triad_sheen(skull, top_a=130, bot_a=40, ell=(0.36, 0.10, 0.34, 0.30))
    s.blit(skull, (0, 0))

    # face decoration drawn AFTER triad so painted motifs stay crisp
    face = new_surf(w, h)
    eye_y = sk_cy - skh * 0.05
    eye_dx = skw * 0.46
    eye_r = skw * 0.34
    for sgn in (-1, 1):
        ex = sk_cx + sgn * eye_dx
        pygame.draw.circle(face, INK, (int(ex), int(eye_y)), int(eye_r))
        # painted rose-magenta socket bead with a bright bead
        pygame.draw.circle(face, ROSE, (int(ex), int(eye_y)), int(eye_r * 0.6))
        pygame.draw.circle(face, _lite(ROSE, 0.5),
                           (int(ex - eye_r * 0.2), int(eye_y - eye_r * 0.2)),
                           int(eye_r * 0.28))
        # lash-flicks: 3 ink ticks curling up+out from the upper-outer socket
        for k in range(3):
            la = math.radians(-150 + sgn * (10 + k * 22))
            lx0 = ex + math.cos(la) * eye_r
            ly0 = eye_y + math.sin(la) * eye_r
            lx1 = ex + math.cos(la) * eye_r * 1.7
            ly1 = eye_y + math.sin(la) * eye_r * 1.7
            pygame.draw.line(face, INK, (int(lx0), int(ly0)),
                             (int(lx1), int(ly1)), max(2, SS // 2 + 1))
    # nose: small inverted heart
    ny = sk_cy + skh * 0.34
    pygame.draw.polygon(face, INK, [
        (int(sk_cx), int(ny + skh * 0.22)),
        (int(sk_cx - skw * 0.12), int(ny - skh * 0.02)),
        (int(sk_cx + skw * 0.12), int(ny - skh * 0.02))])
    # joyful open grin: a filled ink mouth with tooth ticks (open, not stitched)
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

    # coral temple-rose tucked at the wearer's-left temple (a small layered bloom)
    rose = new_surf(w, h)
    rose_x = sk_cx - skw * 1.05
    rose_y = sk_cy - skh * 0.55
    draw_marigold(rose, rose_x, rose_y, w * 0.052,
                  base=CORAL, shade=CORAL_SH, hi=_lite(CORAL, 0.5),
                  petals=7, core=ROSE)
    # a couple of green-free leaf ticks omitted to keep the palette pinned
    s.blit(rose, (0, 0))

    return s


def build_zapateada():
    big = _build_zapateada_big()
    small = pygame.transform.smoothscale(big, (DES_W, DES_H))
    return grow_outline(small, INK, 1)


# ── PROP: ribbon-dance / liston maypole + its top<->bottom PILLAR mirror ──────
# AD pin: the creature's swept skirt is asymmetric, but the PROP must NOT inherit
# that swing — the prop resolves the skirt into a SYMMETRIC RADIAL ribbon-rosette
# centered on the pole axis (a radial fan, not a one-sided sweep), so the mirror
# reads balanced on-axis.
PROP_W, PROP_H = 64, 150


def _build_dancepole_big():
    w, h = PROP_W * SS, PROP_H * SS
    s = new_surf(w, h)
    cx = w * 0.5

    # fluted dance POLE shaft (repeatable pillar body) — wound-ribbon banding:
    # alternating turquoise + rose diagonal wraps so the shaft reads as a liston
    # maypole, on-axis and symmetric.
    pole_w = w * 0.16
    pole_top = h * 0.300
    pole_bot = h * 0.975
    pole = new_surf(w, h)
    pygame.draw.rect(pole, BONE, (int(cx - pole_w / 2), int(pole_top),
                                  int(pole_w), int(pole_bot - pole_top)))
    # diagonal wound ribbons, mirrored L/R so the wrap reads centered
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

    # gap-edge CAP: a SYMMETRIC RADIAL ribbon-rosette (the swept skirt resolved
    # to a balanced fan on the pole axis) + a castanet pair finial.
    cap = new_surf(w, h)
    ros_cx, ros_cy = cx, h * 0.255
    # radial ruffle-fan rosette: rose-magenta lobes fanned EVENLY all the way
    # around the axis (no one-sided sweep), in two staggered rings.
    R_out = w * 0.42
    R_in = w * 0.24
    for ring, (rr, col, sh) in enumerate(((R_out, ROSE, ROSE_SH),
                                          (R_in, _lite(ROSE, 0.18), ROSE_SH))):
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
    # marigold-gold trim ring picking out the rosette
    pygame.draw.circle(cap, MARIGOLD, (int(ros_cx), int(ros_cy)), int(R_in * 0.7))
    pygame.draw.circle(cap, INK, (int(ros_cx), int(ros_cy)), int(R_in * 0.46))
    pygame.draw.circle(cap, TEAL, (int(ros_cx), int(ros_cy)), int(R_in * 0.38))
    pygame.draw.circle(cap, _lite(TEAL, 0.5),
                       (int(ros_cx - R_in * 0.14), int(ros_cy - R_in * 0.14)),
                       int(R_in * 0.18))
    core_shade(cap, ROSE_SH, 110, ell=(0.20, 0.30, 0.60, 0.55))
    triad_sheen(cap, top_a=96, bot_a=34, ell=(0.16, 0.08, 0.50, 0.46))
    s.blit(cap, (0, 0))

    # castanet PAIR seated symmetrically on the axis just below the rosette
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
    # a turquoise cord linking the castanets across the axis
    pygame.draw.line(cast, TEAL, (int(cx - w * 0.135), int(cast_y)),
                     (int(cx + w * 0.135), int(cast_y)), max(2, SS // 2))
    s.blit(cast, (0, 0))
    return s


def build_dancepole():
    big = _build_dancepole_big()
    small = pygame.transform.smoothscale(big, (PROP_W, PROP_H))
    return grow_outline(small, INK, 1)


def build_pillar(height=300):
    """Mirror the dance-pole top<->bottom into a repeatable pillar: a tileable
    wound-ribbon SHAFT body with a radial ribbon-rosette + castanet gap-edge CAP
    (bottom-pillar rosette blooms UP)."""
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
top_pillar.blit(cap, (0, top_shaft_h))   # rosette blooms DOWN at the gap
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


SHEET_W, SHEET_H = 1000, 800
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
sheet.blit(ftitle.render("ZAPATEADA  —  round 1", True, TITLE), (28, 18))
sheet.blit(fbody.render(
    "Ballet folklorico calaca frozen MID-TWIRL: arm arced overhead, ruffled skirt swept "
    "OFF-AXIS by the spin, bone legs in a zapateado stomp. The family's ONLY asymmetric read.",
    True, SUB), (28, 54))
sheet.blit(ftiny.render(
    "Palette: rose-magenta skirt (214,72,86) HERO - warm-bone (236,224,200) - marigold trim "
    "(232,184,80) - turquoise ribbon (58,172,166) - coral temple-rose (238,116,92) - ink.",
    True, ACCENT), (28, 76))

M = 28
top_y = 100

hero_rect = pygame.Rect(M, top_y, 320, 456)
sky_panel(hero_rect)
sheet.blit(fhead.render("Zapateada  (hero)", True, TITLE),
           (hero_rect.x + 12, hero_rect.y + 8))
sheet.blit(ftiny.render("off-axis swept skirt + lean + raised arm = motion",
                        True, (235, 242, 252)),
           (hero_rect.x + 12, hero_rect.bottom - 22))
blit_center(scaled(zap, 2.7), hero_rect, dy=20)

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

# --- BOTTOM: gameplay-scale read row + zoom + pure-black silhouette ---
row_y = hero_rect.bottom + 16
row_rect = pygame.Rect(M, row_y, SHEET_W - 2 * M, SHEET_H - row_y - 18)
pygame.draw.rect(sheet, PANEL2, row_rect, border_radius=10)
sheet.blit(fhead.render("Gameplay scale", True, TITLE),
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
c1 = pygame.Rect(row_rect.x + 20, cy, 90, 104)
chip(c1)
blit_center(zap32, c1)
sheet.blit(ftiny.render("32px", True, (24, 30, 44)), (c1.x + 4, c1.bottom - 16))

c2 = pygame.Rect(c1.right + 16, cy, 120, 104)
chip(c2)
z = pygame.transform.scale(zap32, (zap32.get_width() * 3, zap32.get_height() * 3))
blit_center(z, c2)
sheet.blit(ftiny.render("32px x3", True, (24, 30, 44)), (c2.x + 4, c2.bottom - 16))

c3 = pygame.Rect(c2.right + 16, cy, 104, 104)
chip(c3)
blit_center(zap48, c3)
sheet.blit(ftiny.render("48px", True, (24, 30, 44)), (c3.x + 4, c3.bottom - 16))

# pure-black silhouette panel: proves the asymmetric twirl reads with zero hue
c_sil = pygame.Rect(c3.right + 16, cy, 96, 104)
chip(c_sil, top=(230, 234, 240), bot=(230, 234, 240))
inkmask = pygame.mask.from_surface(zap48, 40).to_surface(
    setcolor=(0, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
blit_center(inkmask, c_sil)
sheet.blit(ftiny.render("silhouette", True, (40, 40, 48)),
           (c_sil.x + 4, c_sil.bottom - 16))

c4 = pygame.Rect(c_sil.right + 16, cy, 64, 104)
chip(c4, top=(196, 184, 214), bot=(214, 200, 222))
blit_center(pole32, c4)
sheet.blit(ftiny.render("prop", True, (40, 34, 54)), (c4.x + 4, c4.bottom - 16))

c5 = pygame.Rect(c4.right + 16, cy, 110, 104)
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

sheet.blit(ftiny.render(
    "Read: the off-axis swept-skirt + lean + raised arm give a DIAGONAL in-motion",
    True, SUB), (c5.right + 22, cy + 20))
sheet.blit(ftiny.render(
    "silhouette — the family's only asymmetric one. Hero rose-magenta skirt stays",
    True, SUB), (c5.right + 22, cy + 38))
sheet.blit(ftiny.render(
    "PINKER/COOLER than chile + rust. Triad: dark trough -> flat rose -> sheen lip.",
    True, SUB), (c5.right + 22, cy + 56))
sheet.blit(ftiny.render(
    "Prop mirror is SYMMETRIC: swept skirt -> radial rosette on the pole axis.",
    True, SUB), (c5.right + 22, cy + 74))

os.makedirs(_OUT_DIR, exist_ok=True)
out_path = os.path.join(_OUT_DIR, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
