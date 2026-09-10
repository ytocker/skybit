"""CATRINA — round 2 review sheet (Section 2 Skeletons, locked15 brief).

Round-1 critique gate (AD, ITERATE): the HAT read as a flat sombrero disc —
the same circular platter Mariachi owns. The single thin pink feather vanished
by 48px. Catrina exists to NOT be a sombrero skeleton, so the silhouette has to
say "plumed couture hat" on its own.

Round-2 resolves every actionable note:
  1. PLUME = the silhouette. A bouquet of FOUR bold ostrich-style plumes arcing
     up+out past the brim (asymmetric, tallest at back), each a fat triad-lit
     lobe with a barb-notched edge — adds ~45% to the hat's bounding height and
     clearly breaks the circular outline.
  2. Brim is upswept + elliptical + asymmetric (cavalier dip on the wearer's
     left), never Mariachi's flat horizontal disc.
  3. Marigolds demoted from a centred crown-bump to a side hatband cluster at
     the brim/crown join; plumes rise BEHIND them.
  4. Brim+plume verified dominant over the gown at 32px.
  5. Parasol canopy gets visible rib spokes + a pointed ferrule finial so the
     gap-cap reads "parasol", never a dome/lollipop. Marigold fringe kept.
  6. Pillar-mirror cap pushes ribs + pointed finial so it survives gap scale.
  7. Face: 3 bold petal points per socket + high-contrast stitch line.
  8. Gown sheen tightened to a narrow shoulder highlight.

House grammar: chibi proportions, FLAT saturated fills + hard ink keylines,
form via dark-core -> flat-fill -> top-left rim-sheen TRIAD, a 1px outline
grown from the alpha mask, supersample -> smoothscale. Scary-CUTE, festive.

Run headless (SDL_VIDEODRIVER=dummy). Writes round_2.png beside this script.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = "/home/user/skybit"
_OUT_DIR = os.path.join(_ROOT, "docs", "skybit_devil", "batch2", "catrina")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# ── PINNED PALETTE (exact hexes from the locked brief) ───────────────────────
BONE      = (238, 230, 222)   # ash-white bone base
BONE_SH   = (176, 168, 166)   # cool-grey shade (dark-core)
MARIGOLD  = (244, 150, 44)    # marigold-orange accent
PINK      = (228, 86, 140)    # hot-pink bloom
TEAL      = (54, 150, 150)    # teal gown
GOLD      = (226, 186, 84)    # gold trim
INK       = (28, 22, 26)      # hard keyline
SHEEN     = (255, 248, 242)   # top-left rim-sheen


def _dark(c, f=0.62):
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f))


def _lite(c, f=0.4):
    return tuple(int(c[i] + (255 - c[i]) * f) for i in range(3))


TEAL_SH   = _dark(TEAL, 0.58)
MARI_SH   = _dark(MARIGOLD, 0.66)
MARI_HI   = _lite(MARIGOLD, 0.45)
PINK_SH   = _dark(PINK, 0.66)
PINK_HI   = _lite(PINK, 0.5)


# ── house-style helpers ──────────────────────────────────────────────────────
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
    the dark-core -> flat-fill -> sheen triad. `ell` lets callers tighten the
    highlight (e.g. a narrow shoulder sheen on the slim gown)."""
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


def core_shade(sprite, shade_col, alpha=120):
    """Dark-core: a lower-right pooled shadow lobe, masked to silhouette."""
    w, h = sprite.get_size()
    ov = new_surf(w, h)
    pygame.draw.ellipse(ov, (*shade_col, alpha),
                        (int(w * 0.28), int(h * 0.40), int(w * 0.78), int(h * 0.72)))
    ov.blit(amask(sprite), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sprite.blit(ov, (0, 0))
    return sprite


# ── marigold-petal motif (flat triad rosette) ───────────────────────────────
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
    for ang_i in range(petals):
        a = (ang_i / petals) * math.tau + (math.tau / petals) * 0.5
        if math.cos(a) < 0.1 and math.sin(a) < 0.1:
            px = cx + math.cos(a) * r * 0.62
            py = cy + math.sin(a) * r * 0.62
            pygame.draw.circle(surf, hi, (int(px), int(py)), int(r * 0.24))
    pygame.draw.circle(surf, INK, (int(cx), int(cy)), int(r * 0.42))
    pygame.draw.circle(surf, core or GOLD, (int(cx), int(cy)), int(r * 0.34))
    pygame.draw.circle(surf, _lite(core or GOLD, 0.5),
                       (int(cx - r * 0.1), int(cy - r * 0.1)), int(r * 0.16))


# ── ostrich PLUME (fat triad-lit lobe, barb-notched, curling) ────────────────
def draw_plume(surf, base_x, base_y, length, max_w, tilt_deg, curl,
               base_col=PINK, shade_col=PINK_SH, hi_col=PINK_HI):
    """One bold ostrich plume: a teardrop lobe swept along a curling spine, with
    a soft barb-notched edge so the SILHOUETTE alone reads 'feather'. `tilt_deg`
    is the launch angle from vertical (deg, +ve sweeps right); `curl` bends the
    tip outward over the run so plumes nod like real ostrich feathers."""
    spine = []
    N = 18
    ang0 = math.radians(-90 + tilt_deg)  # screen up == -90
    for i in range(N + 1):
        t = i / N
        a = ang0 + math.radians(curl) * t        # progressive tip curl
        # ease the step so the plume is denser near the fat mid-body
        step = length / N
        if not spine:
            spine.append((base_x, base_y))
        else:
            px, py = spine[-1]
            spine.append((px + math.cos(a) * step, py + math.sin(a) * step))
    # half-width profile: thin at the quill, fat at ~40%, tapering to a point
    def half_w(t):
        return max_w * (math.sin(min(1.0, t * 1.15) * math.pi) ** 0.7) * 0.5 + max_w * 0.06

    left, right = [], []
    for i, (x, y) in enumerate(spine):
        t = i / N
        if i < N:
            nx, ny = spine[i + 1]
        else:
            nx, ny = x + (x - spine[i - 1][0]), y + (y - spine[i - 1][1])
        dx, dy = nx - x, ny - y
        d = math.hypot(dx, dy) or 1.0
        # perpendicular (left/right of the spine)
        ox, oy = -dy / d, dx / d
        hw = half_w(t)
        left.append((x + ox * hw, y + oy * hw))
        right.append((x - ox * hw, y - oy * hw))
    poly = left + right[::-1]
    pygame.draw.polygon(surf, base_col, poly)
    # shaded far half (the spine splits lit near-half from shaded far-half)
    pygame.draw.polygon(surf, shade_col, right + [spine[i] for i in range(N, -1, -1)])
    # lit central quill highlight
    pygame.draw.lines(surf, hi_col, False,
                      [(x, y) for x, y in spine], max(1, SS))
    # barb notches along BOTH edges so the silhouette edge is feathery, not smooth
    for i in range(2, N, 1):
        x, y = spine[i]
        t = i / N
        hw = half_w(t)
        nx, ny = spine[i + 1] if i < N else spine[i]
        dx, dy = nx - x, ny - y
        d = math.hypot(dx, dy) or 1.0
        ox, oy = -dy / d, dx / d
        # outward-and-down barb flicks read as ostrich fronds in silhouette
        bl = hw * 0.55
        pygame.draw.line(surf, base_col,
                         (x + ox * hw, y + oy * hw),
                         (x + ox * (hw + bl), y + oy * (hw + bl) + bl * 0.4),
                         max(1, SS))
        pygame.draw.line(surf, shade_col,
                         (x - ox * hw, y - oy * hw),
                         (x - ox * (hw + bl), y - oy * (hw + bl) + bl * 0.4),
                         max(1, SS))


# ── CATRINA creature (drawn at supersample, then smoothscaled) ───────────────
# The plume bouquet now claims the TOP of the canvas, so the design box grows
# taller; the hat (brim + plume) stays the dominant wide+tall mass.
DES_W, DES_H = 104, 152


def _build_catrina_big():
    w, h = DES_W * SS, DES_H * SS
    s = new_surf(w, h)

    def P(fx, fy):
        return (int(fx * w), int(fy * h))

    cx = w * 0.5

    # ----- GOWN: long-necked hourglass body (teal), drawn first (behind) -----
    gown = new_surf(w, h)
    top_y = 0.56
    waist_y = 0.70
    hem_y = 0.985
    gpoly = [
        P(0.5 - 0.115, top_y),
        P(0.5 - 0.085, waist_y),
        P(0.5 - 0.215, hem_y),
        P(0.5 + 0.215, hem_y),
        P(0.5 + 0.085, waist_y),
        P(0.5 + 0.115, top_y),
    ]
    pygame.draw.polygon(gown, TEAL, gpoly)
    for fxp in (0.40, 0.46, 0.54, 0.60):
        x = int(fxp * w)
        pygame.draw.line(gown, TEAL_SH, (x, int(waist_y * h)),
                         (int((0.5 + (fxp - 0.5) * 1.9) * w), int(hem_y * h)), max(2, SS))
    pygame.draw.polygon(gown, GOLD, [
        P(0.5 - 0.215, hem_y), P(0.5 + 0.215, hem_y),
        P(0.5 + 0.20, hem_y - 0.045), P(0.5 - 0.20, hem_y - 0.045)])
    pygame.draw.line(gown, GOLD, P(0.5 - 0.086, waist_y), P(0.5 + 0.086, waist_y), int(SS * 1.6))
    draw_marigold(gown, cx, waist_y * h, w * 0.05, base=PINK, shade=PINK_SH,
                  hi=PINK_HI, petals=7, core=GOLD)
    core_shade(gown, TEAL_SH, 120)
    # tightened, NARROW shoulder/collarbone sheen (no longer a broad wash that
    # flattens the hourglass)
    triad_sheen(gown, top_a=90, bot_a=24, ell=(0.20, 0.50, 0.34, 0.30))
    s.blit(gown, (0, 0))

    # ----- LONG bone NECK (slim, elegant) -----
    neck = new_surf(w, h)
    pygame.draw.rect(neck, BONE, (int(cx - w * 0.045), int(0.485 * h),
                                  int(w * 0.09), int(0.11 * h)))
    for ny in (0.515, 0.55):
        pygame.draw.line(neck, BONE_SH, (int(cx - w * 0.045), int(ny * h)),
                         (int(cx + w * 0.045), int(ny * h)), max(2, SS // 2))
    core_shade(neck, BONE_SH, 110)
    triad_sheen(neck, top_a=110, bot_a=40)
    s.blit(neck, (0, 0))

    # ----- gloved bone HANDS holding a folding FAN -----
    hands = new_surf(w, h)
    fan_cx, fan_cy = cx + w * 0.13, h * 0.66
    r1 = w * 0.13
    a_start, a_end = math.radians(-118), math.radians(-18)
    n = 9
    fpts = []
    for i in range(n + 1):
        a = a_start + (a_end - a_start) * i / n
        fpts.append((fan_cx + math.cos(a) * r1, fan_cy + math.sin(a) * r1))
    fpts.append((fan_cx, fan_cy))
    pygame.draw.polygon(hands, MARIGOLD, fpts)
    for i in range(n + 1):
        a = a_start + (a_end - a_start) * i / n
        pygame.draw.line(hands, GOLD, (fan_cx, fan_cy),
                         (fan_cx + math.cos(a) * r1, fan_cy + math.sin(a) * r1), max(2, SS // 2))
    pygame.draw.circle(hands, GOLD, (int(fan_cx), int(fan_cy)), int(w * 0.018))
    pygame.draw.circle(hands, TEAL, (int(fan_cx), int(fan_cy + h * 0.005)), int(w * 0.03))
    pygame.draw.circle(hands, TEAL, (int(cx - w * 0.11), int(h * 0.665)), int(w * 0.03))
    core_shade(hands, MARI_SH, 90)
    triad_sheen(hands, top_a=90, bot_a=30)
    s.blit(hands, (0, 0))

    # ----- SKULL face (small, delicate sugar-skull) -----
    skull = new_surf(w, h)
    skh_cy = h * 0.405
    skw = w * 0.19
    skh = h * 0.135
    pygame.draw.ellipse(skull, BONE, (int(cx - skw), int(skh_cy - skh),
                                      int(skw * 2), int(skh * 2.0)))
    pygame.draw.polygon(skull, BONE, [
        (int(cx - skw * 0.7), int(skh_cy + skh * 0.6)),
        (int(cx + skw * 0.7), int(skh_cy + skh * 0.6)),
        (int(cx + skw * 0.34), int(skh_cy + skh * 1.5)),
        (int(cx - skw * 0.34), int(skh_cy + skh * 1.5)),
    ])
    core_shade(skull, BONE_SH, 110)
    triad_sheen(skull, top_a=130, bot_a=40)
    s.blit(skull, (0, 0))

    # face decoration drawn AFTER triad so painted motifs stay crisp
    face = new_surf(w, h)
    eye_y = skh_cy - skh * 0.05
    eye_dx = skw * 0.46
    eye_r = skw * 0.32
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        # dark socket
        pygame.draw.circle(face, INK, (int(ex), int(eye_y)), int(eye_r))
        b, sh = (MARIGOLD, MARI_SH) if sgn < 0 else (PINK, PINK_SH)
        # 3 bold petal points radiating from the socket (the sugar-skull tell,
        # simplified so it survives shrink to 48px)
        for k in range(3):
            pa = math.radians(-90 + (k - 1) * 70)
            tipx = ex + math.cos(pa) * eye_r * 1.55
            tipy = eye_y + math.sin(pa) * eye_r * 1.55
            perp = pa + math.pi / 2
            bw = eye_r * 0.5
            pygame.draw.polygon(face, INK, [
                (ex + math.cos(perp) * bw, eye_y + math.sin(perp) * bw),
                (ex - math.cos(perp) * bw, eye_y - math.sin(perp) * bw),
                (tipx, tipy)])
            pygame.draw.polygon(face, b, [
                (ex + math.cos(perp) * bw * 0.7, eye_y + math.sin(perp) * bw * 0.7),
                (ex - math.cos(perp) * bw * 0.7, eye_y - math.sin(perp) * bw * 0.7),
                (ex + math.cos(pa) * eye_r * 1.32, eye_y + math.sin(pa) * eye_r * 1.32)])
        # bright bead in the socket centre
        pygame.draw.circle(face, b, (int(ex), int(eye_y)), int(eye_r * 0.42))
        pygame.draw.circle(face, _lite(b, 0.5),
                           (int(ex - eye_r * 0.18), int(eye_y - eye_r * 0.18)),
                           int(eye_r * 0.2))
    # nose: small inverted heart
    ny = skh_cy + skh * 0.30
    pygame.draw.polygon(face, INK, [
        (int(cx), int(ny + skh * 0.20)),
        (int(cx - skw * 0.12), int(ny - skh * 0.02)),
        (int(cx + skw * 0.12), int(ny - skh * 0.02))])
    # high-contrast stitched smile across the jaw
    smy = skh_cy + skh * 0.92
    pygame.draw.arc(face, INK, (int(cx - skw * 0.55), int(smy - skh * 0.5),
                               int(skw * 1.1), int(skh * 0.9)),
                    math.radians(200), math.radians(340), max(3, SS + 1))
    for i in range(-3, 4):
        sx = cx + i * skw * 0.16
        sy = smy + abs(i) * skh * 0.03
        pygame.draw.line(face, INK, (int(sx), int(sy - skh * 0.13)),
                         (int(sx), int(sy + skh * 0.13)), max(2, SS // 2 + 1))
    s.blit(face, (0, 0))

    # ===== HAT: upswept couture brim + a BOLD 4-PLUME bouquet that breaks the
    # silhouette (the make-or-break read). Plumes are drawn BEHIND the brim so
    # they rise from the crown; the brim then overlaps their quills. =====
    crown_cx = cx - w * 0.02
    crown_cy = h * 0.235
    brim_cy = h * 0.255

    # --- plume bouquet (behind brim) --------------------------------------
    plumes = new_surf(w, h)
    px0 = crown_cx + w * 0.02
    py0 = crown_cy - h * 0.01
    # four plumes, tallest at BACK, fanning asymmetrically up+out; mixed
    # pink/marigold so the bouquet reads festive even in silhouette.
    plume_specs = [
        # (dx,        dy,        length,     max_w,     tilt,  curl, cols)
        (-0.04, 0.00, h * 0.40, w * 0.115, -22, -34, (PINK, PINK_SH, PINK_HI)),
        (0.01, -0.01, h * 0.46, w * 0.10, -4, -14, (MARIGOLD, MARI_SH, MARI_HI)),
        (0.05, 0.00, h * 0.40, w * 0.105, 16, 30, (PINK, PINK_SH, PINK_HI)),
        (0.10, 0.02, h * 0.31, w * 0.09, 34, 48, (MARIGOLD, MARI_SH, MARI_HI)),
    ]
    for dx, dy, length, mw, tilt, curl, cols in plume_specs:
        draw_plume(plumes, px0 + dx * w, py0 + dy * h, length, mw, tilt, curl,
                   base_col=cols[0], shade_col=cols[1], hi_col=cols[2])
    s.blit(plumes, (0, 0))

    # --- crown dome (small, off-centre under the bouquet) ------------------
    hat = new_surf(w, h)
    pygame.draw.ellipse(hat, TEAL, (int(crown_cx - w * 0.155), int(crown_cy - h * 0.075),
                                    int(w * 0.31), int(h * 0.135)))

    # --- upswept ASYMMETRIC brim (an ellipse tilted off-axis; the wearer's
    # left edge sweeps UP in a cavalier dip, far from Mariachi's flat disc). The
    # brim is built tilted then composited so its outline is non-horizontal.
    brim_w = w * 0.50
    brim_h = h * 0.066
    brim_layer = new_surf(w, h)
    # underside (teal shade) offset down for thickness
    pygame.draw.ellipse(brim_layer, TEAL_SH,
                        (int(crown_cx - brim_w), int(brim_cy - brim_h * 0.3),
                         int(brim_w * 2), int(brim_h * 2.0)))
    pygame.draw.ellipse(brim_layer, TEAL,
                        (int(crown_cx - brim_w), int(brim_cy - brim_h),
                         int(brim_w * 2), int(brim_h * 2)))
    pygame.draw.ellipse(brim_layer, GOLD,
                        (int(crown_cx - brim_w), int(brim_cy - brim_h),
                         int(brim_w * 2), int(brim_h * 2)), max(2, SS))
    # rotate the whole brim a few degrees so the silhouette is an UPSWEPT
    # ellipse — the asymmetric cavalier tilt Mariachi's flat disc never has
    brim_rot = pygame.transform.rotate(brim_layer, 9)
    hat.blit(brim_rot, ((w - brim_rot.get_width()) // 2 - int(w * 0.01),
                        (h - brim_rot.get_height()) // 2 + int(h * 0.005)))
    core_shade(hat, TEAL_SH, 110)
    triad_sheen(hat, top_a=80, bot_a=36)
    s.blit(hat, (0, 0))

    # --- hatband marigold cluster, off to ONE side at the brim/crown join
    # (demoted from the centred crown-bump; plumes rise behind it) ----------
    band = new_surf(w, h)
    join_y = brim_cy - h * 0.018
    pygame.draw.line(band, GOLD,
                     (int(crown_cx - w * 0.15), int(join_y)),
                     (int(crown_cx + w * 0.15), int(join_y)), max(3, SS + 1))
    cluster = [(-0.135, 0.0, 0.052, MARIGOLD, MARI_SH, MARI_HI),
               (-0.085, -0.012, 0.06, PINK, PINK_SH, PINK_HI),
               (-0.028, 0.0, 0.05, MARIGOLD, MARI_SH, MARI_HI)]
    for fxp, fyp, rr, b, sh, hi in cluster:
        draw_marigold(band, crown_cx + fxp * w, join_y + fyp * h, w * rr,
                      base=b, shade=sh, hi=hi, petals=8, core=GOLD)
    s.blit(band, (0, 0))

    return s


def build_catrina():
    big = _build_catrina_big()
    small = pygame.transform.smoothscale(big, (DES_W, DES_H))
    return grow_outline(small, INK, 1)


# ── PARASOL prop + its top<->bottom PILLAR mirror ────────────────────────────
PROP_W, PROP_H = 56, 150


def _build_parasol_big():
    w, h = PROP_W * SS, PROP_H * SS
    s = new_surf(w, h)
    cx = w * 0.5

    # fluted POLE shaft (the repeatable pillar body) — rib banding
    pole_w = w * 0.13
    pole_top = h * 0.24
    pole_bot = h * 0.97
    pole = new_surf(w, h)
    pygame.draw.rect(pole, BONE, (int(cx - pole_w / 2), int(pole_top),
                                  int(pole_w), int(pole_bot - pole_top)))
    band_n = 7
    for i in range(band_n + 1):
        by = pole_top + (pole_bot - pole_top) * i / band_n
        pygame.draw.line(pole, GOLD, (int(cx - pole_w / 2), int(by)),
                         (int(cx + pole_w / 2), int(by)), max(2, SS // 2))
    core_shade(pole, BONE_SH, 120)
    triad_sheen(pole, top_a=120, bot_a=40)
    s.blit(pole, (0, 0))

    # scalloped open parasol CANOPY (gap-edge cap). Round + on-axis for a clean
    # mirror, but now with strong RIB SPOKES + a POINTED FERRULE finial so it
    # reads unmistakably as a parasol (not a dome / lollipop / sombrero).
    canopy = new_surf(w, h)
    cnp_cy = h * 0.235
    cnp_hw = w * 0.46
    cnp_h = h * 0.175
    seg = 16
    # scalloped lower rim: lobes between rib tips give a lace silhouette edge
    ribs = 6
    rim_pts = []
    for i in range(ribs * 4 + 1):
        t = i / (ribs * 4)
        a = math.pi + math.pi * t
        scallop = math.sin(t * ribs * math.pi) * cnp_h * 0.10
        rim_pts.append((cx + math.cos(a) * cnp_hw,
                        cnp_cy + abs(math.sin(a)) * 0 + scallop))
    dome_pts = [(cx - cnp_hw, cnp_cy)]
    for i in range(seg + 1):
        a = math.pi + math.pi * i / seg
        dome_pts.append((cx + math.cos(a) * cnp_hw, cnp_cy + math.sin(a) * cnp_h))
    dome_pts += rim_pts[::-1]
    pygame.draw.polygon(canopy, TEAL, dome_pts)
    # rib spokes radiating from the finial down to each scallop notch
    for i in range(ribs + 1):
        rx = cx - cnp_hw + (2 * cnp_hw) * i / ribs
        pygame.draw.line(canopy, GOLD, (int(cx), int(cnp_cy - cnp_h * 1.02)),
                         (int(rx), int(cnp_cy)), max(2, SS // 2 + 1))
    # rim arc
    pygame.draw.arc(canopy, GOLD, (int(cx - cnp_hw), int(cnp_cy - cnp_h),
                                   int(cnp_hw * 2), int(cnp_h * 2)),
                    math.radians(180), math.radians(360), max(2, SS // 2 + 1))
    # POINTED FERRULE finial spike at the very top (the parasol tell)
    fin_h = h * 0.075
    pygame.draw.polygon(canopy, GOLD, [
        (int(cx - w * 0.03), int(cnp_cy - cnp_h * 1.0)),
        (int(cx + w * 0.03), int(cnp_cy - cnp_h * 1.0)),
        (int(cx), int(cnp_cy - cnp_h * 1.0 - fin_h))])
    pygame.draw.circle(canopy, GOLD, (int(cx), int(cnp_cy - cnp_h * 1.0)), int(w * 0.035))
    core_shade(canopy, TEAL_SH, 120)
    triad_sheen(canopy, top_a=90, bot_a=40)
    s.blit(canopy, (0, 0))

    # marigold fringe hung along the canopy rim (the festive cap tell)
    fr = new_surf(w, h)
    for i in range(ribs):
        fx = cx - cnp_hw + (2 * cnp_hw) * (i + 0.5) / ribs
        b, sh, hi = ((MARIGOLD, MARI_SH, MARI_HI) if i % 2 == 0
                     else (PINK, PINK_SH, PINK_HI))
        draw_marigold(fr, fx, cnp_cy + h * 0.012, w * 0.05,
                      base=b, shade=sh, hi=hi, petals=7, core=GOLD)
    s.blit(fr, (0, 0))
    return s


def build_parasol():
    big = _build_parasol_big()
    small = pygame.transform.smoothscale(big, (PROP_W, PROP_H))
    return grow_outline(small, INK, 1)


def build_pillar(height=300):
    """Mirror the parasol top<->bottom into a repeatable pillar: a tileable
    fluted-pole SHAFT body with a scalloped marigold canopy gap-edge CAP at the
    gap (bottom-pillar canopy blooms UP)."""
    prop = build_parasol()
    pw, ph = prop.get_size()
    cap_h = int(ph * 0.42)
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
catrina = build_catrina()
parasol = build_parasol()
pillar, cap, shaft = build_pillar(300)

top_pillar = new_surf(parasol.get_width(), 300)
bot_pillar, _, _ = build_pillar(300)
cap_h = int(parasol.get_height() * 0.42)
top_shaft_h = 300 - cap_h
y = 0
while y < top_shaft_h:
    top_pillar.blit(shaft, (0, y))
    y += shaft.get_height()
top_pillar.blit(cap, (0, top_shaft_h))   # canopy blooms DOWN at the gap


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
sheet.blit(ftitle.render("CATRINA  —  round 2", True, TITLE), (28, 18))
sheet.blit(fbody.render(
    "Plume = silhouette: a 4-feather bouquet breaks the brim outline; brim upswept + "
    "asymmetric (cavalier dip), NOT Mariachi's flat sombrero disc.",
    True, SUB), (28, 54))
sheet.blit(ftiny.render(
    "Palette: ash-white bone (238,230,222) - cool-grey - marigold (244,150,44) - "
    "hot-pink (228,86,140) - teal gown (54,150,150) - gold trim - ink. Couture festive.",
    True, ACCENT), (28, 76))

M = 28
top_y = 100

hero_rect = pygame.Rect(M, top_y, 300, 446)
sky_panel(hero_rect)
sheet.blit(fhead.render("Catrina  (hero)", True, TITLE), (hero_rect.x + 12, hero_rect.y + 8))
blit_center(scaled(catrina, 2.55), hero_rect, dy=22)

prop_rect = pygame.Rect(hero_rect.right + 18, top_y, 220, 446)
sky_panel(prop_rect, top=(196, 184, 214), bot=(214, 200, 222))
sheet.blit(fhead.render("Parasol prop", True, TITLE), (prop_rect.x + 12, prop_rect.y + 8))
blit_center(scaled(parasol, 2.3), prop_rect, dy=20)
sheet.blit(ftiny.render("fluted pole + ribbed", True, (60, 50, 70)),
           (prop_rect.x + 12, prop_rect.bottom - 38))
sheet.blit(ftiny.render("canopy + pointed ferrule", True, (60, 50, 70)),
           (prop_rect.x + 12, prop_rect.bottom - 22))

pil_rect = pygame.Rect(prop_rect.right + 18, top_y, 386, 446)
sky_panel(pil_rect, top=(120, 178, 218), bot=(190, 218, 234))
sheet.blit(fhead.render("Pillar mirror (gap)", True, TITLE), (pil_rect.x + 12, pil_rect.y + 8))
clip = sheet.get_clip()
inner = pil_rect.inflate(-8, -8)
sheet.set_clip(inner)
GAP = 150
pcx = pil_rect.centerx - parasol.get_width() // 2
gap_top = pil_rect.y + 38
sheet.blit(top_pillar, (pcx, gap_top - 130))
sheet.blit(bot_pillar, (pcx, gap_top + GAP))
sheet.set_clip(clip)
sheet.blit(ftiny.render("ribbed canopy + pointed ferrule reads 'parasol' at the gap",
                        True, (235, 242, 252)), (pil_rect.x + 12, pil_rect.bottom - 22))

# --- BOTTOM: 32px gameplay-scale read row + zoom ---
row_y = hero_rect.bottom + 16
row_rect = pygame.Rect(M, row_y, SHEET_W - 2 * M, SHEET_H - row_y - 20)
pygame.draw.rect(sheet, PANEL2, row_rect, border_radius=10)
sheet.blit(fhead.render("Gameplay scale", True, TITLE), (row_rect.x + 12, row_rect.y + 8))


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


cat32 = fit_h(catrina, 32)
cat48 = fit_h(catrina, 48)
para32 = fit_h(parasol, 40)

cy = row_rect.y + 44
c1 = pygame.Rect(row_rect.x + 20, cy, 80, 100)
chip(c1)
blit_center(cat32, c1)
sheet.blit(ftiny.render("32px", True, (24, 30, 44)), (c1.x + 4, c1.bottom - 16))

c2 = pygame.Rect(c1.right + 16, cy, 110, 100)
chip(c2)
z = pygame.transform.scale(cat32, (cat32.get_width() * 3, cat32.get_height() * 3))
blit_center(z, c2)
sheet.blit(ftiny.render("32px x3", True, (24, 30, 44)), (c2.x + 4, c2.bottom - 16))

c3 = pygame.Rect(c2.right + 16, cy, 96, 100)
chip(c3)
blit_center(cat48, c3)
sheet.blit(ftiny.render("48px", True, (24, 30, 44)), (c3.x + 4, c3.bottom - 16))

# silhouette-only chip: proves the plume breaks the outline with zero hue
c_sil = pygame.Rect(c3.right + 16, cy, 80, 100)
chip(c_sil, top=(228, 232, 240), bot=(228, 232, 240))
sil = amask(cat48)
sil_ink = new_surf(*sil.get_size())
sil_ink.fill((24, 24, 28, 0))
sil_ink.blit(sil, (0, 0))
# recolor white mask to ink
arr = sil
black = new_surf(*arr.get_size())
pygame.draw.rect(black, (0, 0, 0, 0), black.get_rect())
black.blit(arr, (0, 0))
inkmask = pygame.mask.from_surface(cat48, 40).to_surface(
    setcolor=(26, 26, 30, 255), unsetcolor=(0, 0, 0, 0))
blit_center(inkmask, c_sil)
sheet.blit(ftiny.render("silhouette", True, (40, 40, 48)), (c_sil.x + 4, c_sil.bottom - 16))

c4 = pygame.Rect(c_sil.right + 16, cy, 64, 100)
chip(c4, top=(196, 184, 214), bot=(214, 200, 222))
blit_center(para32, c4)
sheet.blit(ftiny.render("prop", True, (40, 34, 54)), (c4.x + 4, c4.bottom - 16))

c5 = pygame.Rect(c4.right + 16, cy, 110, 100)
chip(c5, top=(120, 178, 218), bot=(190, 218, 234))
mini_top = fit_h(top_pillar, 60)
mini_bot = fit_h(bot_pillar, 60)
clip = sheet.get_clip()
sheet.set_clip(c5)
mcx = c5.centerx - mini_top.get_width() // 2
sheet.blit(mini_top, (mcx, c5.y - 20))
sheet.blit(mini_bot, (mcx, c5.y + 66))
sheet.set_clip(clip)
sheet.blit(ftiny.render("pillar", True, (235, 242, 252)), (c5.x + 4, c5.bottom - 16))

sheet.blit(ftiny.render(
    "Read: plume bouquet breaks the brim outline -> the 1px silhouette alone says",
    True, SUB), (c5.right + 22, cy + 24))
sheet.blit(ftiny.render(
    "'plumed couture hat', never sombrero disc. Hat (brim+plume) stays the dominant mass.",
    True, SUB), (c5.right + 22, cy + 42))
sheet.blit(ftiny.render(
    "Triad: dark-core -> flat bone/teal fill -> tightened shoulder sheen; 1px ink keyline.",
    True, SUB), (c5.right + 22, cy + 60))

os.makedirs(_OUT_DIR, exist_ok=True)
out_path = os.path.join(_OUT_DIR, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
