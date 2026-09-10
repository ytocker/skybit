"""CATRINA — round 1 review sheet (Section 2 Skeletons, locked15 brief).

La Calavera Catrina: the elegant flower-crowned Day-of-the-Dead lady. An
enormous wide-brimmed plumed HAT (the dominant read, far wider than the head)
over a long-necked hourglass gown, sugar-skull face with flower-petal eye
sockets and a stitched smile, gloved bone hands holding a folding fan. Her
prop is a lace PARASOL that mirrors top<->bottom into a clean repeatable
pillar (fluted pole shaft + scalloped marigold-fringed canopy cap).

House grammar: chibi proportions, FLAT saturated fills + hard ink keylines,
form via dark-core -> flat-fill -> top-left rim-sheen TRIAD, a 1px outline
grown from the alpha mask, supersample -> smoothscale. Scary-CUTE, festive.

Run headless (SDL_VIDEODRIVER=dummy). Writes round_1.png beside this script.
"""
import os
import sys
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

# Working shades derived ONLY by darkening/lightening the pinned hues so the
# triad reads as one material family (no new hues introduced).
def _dark(c, f=0.62):
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f))


def _lite(c, f=0.4):
    return tuple(int(c[i] + (255 - c[i]) * f) for i in range(3))


TEAL_SH   = _dark(TEAL, 0.58)
MARI_SH   = _dark(MARIGOLD, 0.66)
MARI_HI   = _lite(MARIGOLD, 0.45)
PINK_SH   = _dark(PINK, 0.66)


# ── house-style helpers (mirror knight_skin / draw grammar) ──────────────────
SS = 4  # supersample factor


def new_surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def amask(sprite, threshold=40):
    return pygame.mask.from_surface(sprite, threshold).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))


def grow_outline(sprite, color=INK, px=1):
    """1px ink keyline grown from the alpha mask (the silhouette-POP outline)."""
    w, h = sprite.get_size()
    mask = pygame.mask.from_surface(sprite, 40)
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


def triad_sheen(sprite, sheen_col=SHEEN, top_a=120, bot_a=60):
    """Top-left rim-sheen ellipse, masked to the silhouette — the lit third of
    the dark-core -> flat-fill -> sheen triad."""
    w, h = sprite.get_size()
    ov = new_surf(w, h)
    pygame.draw.ellipse(ov, (*sheen_col, top_a),
                        (int(-w * 0.10), int(-h * 0.12), int(w * 0.74), int(h * 0.66)))
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
    """A flat layered marigold: ring of outer petals (shade), ring of inner
    petals (base), a sheen-side cluster, and a bright center."""
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
    # top-left lit petals
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


# ── CATRINA creature (drawn at supersample, then smoothscaled) ───────────────
# Logical design canvas is 100 wide x 132 tall; the hat platter spans the full
# width (the dominant wide read), the head is ~38 wide. Built big at SS then
# scaled down so the smoothscale anti-aliases the hard fills.
DES_W, DES_H = 104, 138


def _build_catrina_big():
    w, h = DES_W * SS, DES_H * SS
    s = new_surf(w, h)

    def P(fx, fy):
        return (int(fx * w), int(fy * h))

    cx = w * 0.5

    # ----- GOWN: long-necked hourglass body (teal), drawn first (behind) -----
    gown = new_surf(w, h)
    # high collar -> narrow waist -> flared skirt hem: an hourglass polygon.
    top_y = 0.50
    waist_y = 0.66
    hem_y = 0.985
    coll_hw = w * 0.115
    waist_hw = w * 0.085
    hem_hw = w * 0.215
    gpoly = [
        P(0.5 - 0.115, top_y),
        P(0.5 - 0.085, waist_y),
        P(0.5 - 0.215, hem_y),
        P(0.5 + 0.215, hem_y),
        P(0.5 + 0.085, waist_y),
        P(0.5 + 0.115, top_y),
    ]
    pygame.draw.polygon(gown, TEAL, gpoly)
    # skirt vertical pleat seams (triad-lit grooves)
    for fxp in (0.40, 0.46, 0.54, 0.60):
        x = int(fxp * w)
        pygame.draw.line(gown, TEAL_SH, (x, int(waist_y * h)),
                         (int((0.5 + (fxp - 0.5) * 1.9) * w), int(hem_y * h)), max(2, SS))
    # gold hem trim band + waist sash
    pygame.draw.polygon(gown, GOLD, [
        P(0.5 - 0.215, hem_y), P(0.5 + 0.215, hem_y),
        P(0.5 + 0.20, hem_y - 0.045), P(0.5 - 0.20, hem_y - 0.045)])
    pygame.draw.line(gown, GOLD, P(0.5 - 0.086, waist_y), P(0.5 + 0.086, waist_y), int(SS * 1.6))
    # pink bloom rosette at the waist sash
    draw_marigold(gown, cx, waist_y * h, w * 0.05, base=PINK, shade=PINK_SH,
                  hi=_lite(PINK, 0.5), petals=7, core=GOLD)
    core_shade(gown, TEAL_SH, 120)
    triad_sheen(gown, top_a=70, bot_a=40)
    s.blit(gown, (0, 0))

    # ----- LONG bone NECK (slim, elegant) -----
    neck = new_surf(w, h)
    pygame.draw.rect(neck, BONE, (int(cx - w * 0.045), int(0.42 * h),
                                  int(w * 0.09), int(0.12 * h)))
    # vertebra rings
    for ny in (0.45, 0.49):
        pygame.draw.line(neck, BONE_SH, (int(cx - w * 0.045), int(ny * h)),
                         (int(cx + w * 0.045), int(ny * h)), max(2, SS // 2))
    core_shade(neck, BONE_SH, 110)
    triad_sheen(neck, top_a=110, bot_a=40)
    s.blit(neck, (0, 0))

    # ----- gloved bone HANDS holding a folding FAN -----
    hands = new_surf(w, h)
    fan_cx, fan_cy = cx + w * 0.13, h * 0.60
    # open folding fan: pie of teal slats with gold ribs
    r0, r1 = w * 0.02, w * 0.13
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
    # teal-gloved hand at the fan pivot
    pygame.draw.circle(hands, TEAL, (int(fan_cx), int(fan_cy + h * 0.005)), int(w * 0.03))
    pygame.draw.circle(hands, TEAL, (int(cx - w * 0.11), int(h * 0.605)), int(w * 0.03))
    core_shade(hands, MARI_SH, 90)
    triad_sheen(hands, top_a=90, bot_a=30)
    s.blit(hands, (0, 0))

    # ----- SKULL face (small, delicate sugar-skull) -----
    skull = new_surf(w, h)
    skh_cy = h * 0.345
    skw = w * 0.19
    skh = h * 0.155
    pygame.draw.ellipse(skull, BONE, (int(cx - skw), int(skh_cy - skh),
                                      int(skw * 2), int(skh * 2.0)))
    # jaw taper
    pygame.draw.polygon(skull, BONE, [
        (int(cx - skw * 0.7), int(skh_cy + skh * 0.6)),
        (int(cx + skw * 0.7), int(skh_cy + skh * 0.6)),
        (int(cx + skw * 0.34), int(skh_cy + skh * 1.5)),
        (int(cx - skw * 0.34), int(skh_cy + skh * 1.5)),
    ])
    core_shade(skull, BONE_SH, 110)
    triad_sheen(skull, top_a=130, bot_a=40)
    s.blit(skull, (0, 0))

    # face decoration drawn AFTER triad so the painted motifs stay crisp
    face = new_surf(w, h)
    eye_y = skh_cy - skh * 0.10
    eye_dx = skw * 0.46
    # flower-petal eye sockets (marigold rosettes around dark sockets)
    for sgn in (-1, 1):
        ex = cx + sgn * eye_dx
        pygame.draw.circle(face, INK, (int(ex), int(eye_y)), int(skw * 0.30))
        draw_marigold(face, ex, eye_y, skw * 0.30,
                      base=MARIGOLD if sgn < 0 else PINK,
                      shade=MARI_SH if sgn < 0 else PINK_SH,
                      hi=MARI_HI if sgn < 0 else _lite(PINK, 0.5),
                      petals=7, core=INK)
    # nose: small inverted heart
    ny = skh_cy + skh * 0.28
    pygame.draw.polygon(face, INK, [
        (int(cx), int(ny + skh * 0.18)),
        (int(cx - skw * 0.12), int(ny - skh * 0.02)),
        (int(cx + skw * 0.12), int(ny - skh * 0.02))])
    # stitched smile across the jaw
    smy = skh_cy + skh * 0.78
    pygame.draw.arc(face, INK, (int(cx - skw * 0.55), int(smy - skh * 0.5),
                               int(skw * 1.1), int(skh * 0.8)),
                    math.radians(200), math.radians(340), max(2, SS))
    for i in range(-3, 4):
        sx = cx + i * skw * 0.16
        sy = smy + abs(i) * skh * 0.02
        pygame.draw.line(face, INK, (int(sx), int(sy - skh * 0.10)),
                         (int(sx), int(sy + skh * 0.10)), max(2, SS // 2))
    s.blit(face, (0, 0))

    # ----- the COLOSSAL plumed HAT (dominant read, full canvas width) -----
    hat = new_surf(w, h)
    brim_cy = h * 0.245
    brim_hw = w * 0.495          # nearly the entire canvas width
    brim_h = h * 0.075
    # wide platter brim ellipse (teal underside) with gold edge
    pygame.draw.ellipse(hat, TEAL_SH, (int(cx - brim_hw), int(brim_cy - brim_h * 0.4),
                                       int(brim_hw * 2), int(brim_h * 2.2)))
    pygame.draw.ellipse(hat, TEAL, (int(cx - brim_hw), int(brim_cy - brim_h),
                                    int(brim_hw * 2), int(brim_h * 2)))
    pygame.draw.ellipse(hat, GOLD, (int(cx - brim_hw), int(brim_cy - brim_h),
                                    int(brim_hw * 2), int(brim_h * 2)), max(2, SS))
    # crown dome of the hat
    crown_cy = brim_cy - h * 0.085
    pygame.draw.ellipse(hat, TEAL, (int(cx - w * 0.20), int(crown_cy - h * 0.085),
                                    int(w * 0.40), int(h * 0.16)))
    # gold hat-band
    pygame.draw.rect(hat, GOLD, (int(cx - w * 0.20), int(brim_cy - h * 0.045),
                                 int(w * 0.40), int(h * 0.035)))
    core_shade(hat, TEAL_SH, 120)
    triad_sheen(hat, top_a=80, bot_a=40)
    s.blit(hat, (0, 0))

    # hat trimmings drawn after triad so blooms + plume stay vivid
    trim = new_surf(w, h)
    # heaped marigolds along the crown/brim join
    bloom_spots = [(-0.20, 0.02, 0.058, PINK, PINK_SH, _lite(PINK, 0.5)),
                   (-0.06, -0.03, 0.072, MARIGOLD, MARI_SH, MARI_HI),
                   (0.10, -0.01, 0.062, MARIGOLD, MARI_SH, MARI_HI),
                   (0.235, 0.03, 0.05, PINK, PINK_SH, _lite(PINK, 0.5))]
    for fxp, fyp, rr, b, sh, hi in bloom_spots:
        draw_marigold(trim, cx + fxp * w, crown_cy + h * 0.02 + fyp * h, w * rr,
                      base=b, shade=sh, hi=hi, petals=8, core=GOLD)
    # a tall sweeping feather PLUME rising from behind the crown
    fx0, fy0 = cx + w * 0.04, crown_cy - h * 0.02
    plume = []
    spine = []
    N = 14
    for i in range(N + 1):
        t = i / N
        px = fx0 + (0.04 + 0.18 * t) * w * (1)
        py = fy0 - (0.02 + 0.20 * t) * h
        spine.append((px, py))
    width_at = lambda t: (1 - t) * w * 0.05 + 0.012 * w
    left = [(x - width_at(i / N), y) for i, (x, y) in enumerate(spine)]
    right = [(x + width_at(i / N) * 0.5, y) for i, (x, y) in enumerate(spine)]
    plume = left + right[::-1]
    pygame.draw.polygon(trim, PINK, plume)
    pygame.draw.polygon(trim, PINK_SH, [(x, y) for x, y in left] +
                        [(x, y) for x, y in spine][::-1])
    # feather barbs
    for i in range(1, N, 1):
        x, y = spine[i]
        ww = width_at(i / N)
        pygame.draw.line(trim, _lite(PINK, 0.4), (x, y), (x - ww, y + ww * 0.3), max(1, SS // 2))
    pygame.draw.lines(trim, GOLD, False, spine, max(1, SS // 2))
    s.blit(trim, (0, 0))

    return s


def build_catrina():
    big = _build_catrina_big()
    small = pygame.transform.smoothscale(big, (DES_W, DES_H))
    return grow_outline(small, INK, 1)


# ── PARASOL prop + its top<->bottom PILLAR mirror ────────────────────────────
PROP_W, PROP_H = 56, 150


def _build_parasol_big(canopy_open=True):
    w, h = PROP_W * SS, PROP_H * SS
    s = new_surf(w, h)
    cx = w * 0.5

    # fluted POLE shaft (the repeatable pillar body) — rib banding
    pole_w = w * 0.13
    pole_top = h * 0.22
    pole_bot = h * 0.97
    pole = new_surf(w, h)
    pygame.draw.rect(pole, BONE, (int(cx - pole_w / 2), int(pole_top),
                                  int(pole_w), int(pole_bot - pole_top)))
    # rib bands every so often (banding tell for the repeatable shaft)
    band_n = 7
    for i in range(band_n + 1):
        by = pole_top + (pole_bot - pole_top) * i / band_n
        pygame.draw.line(pole, GOLD, (int(cx - pole_w / 2), int(by)),
                         (int(cx + pole_w / 2), int(by)), max(2, SS // 2))
    core_shade(pole, BONE_SH, 120)
    triad_sheen(pole, top_a=120, bot_a=40)
    s.blit(pole, (0, 0))

    # scalloped open parasol CANOPY (gap-edge cap), round + on-axis for a clean mirror
    canopy = new_surf(w, h)
    cnp_cy = h * 0.205
    cnp_hw = w * 0.46
    cnp_h = h * 0.165
    # teal dome with gold ribs splitting it into lace gores
    pygame.draw.ellipse(canopy, TEAL, (int(cx - cnp_hw), int(cnp_cy - cnp_h),
                                       int(cnp_hw * 2), int(cnp_h * 2)),)
    # clip lower half away to make a dome
    cover = new_surf(w, h)
    pygame.draw.rect(cover, (0, 0, 0, 0), (0, 0, w, h))
    dome = new_surf(w, h)
    pygame.draw.ellipse(dome, TEAL, (int(cx - cnp_hw), int(cnp_cy - cnp_h),
                                     int(cnp_hw * 2), int(cnp_h * 2)))
    pygame.draw.rect(dome, (0, 0, 0, 0), (0, int(cnp_cy), w, h),)
    # rebuild canopy cleanly: dome polygon
    canopy = new_surf(w, h)
    seg = 16
    dome_pts = [(cx - cnp_hw, cnp_cy)]
    for i in range(seg + 1):
        a = math.pi + math.pi * i / seg
        dome_pts.append((cx + math.cos(a) * cnp_hw, cnp_cy + math.sin(a) * cnp_h))
    dome_pts.append((cx + cnp_hw, cnp_cy))
    pygame.draw.polygon(canopy, TEAL, dome_pts)
    # scalloped fringe along the bottom rim
    scallops = 8
    for i in range(scallops):
        fx = cx - cnp_hw + (2 * cnp_hw) * (i + 0.5) / scallops
        pygame.draw.circle(canopy, TEAL, (int(fx), int(cnp_cy)), int(cnp_hw * 0.10))
    # gold lace ribs (gores)
    for i in range(-3, 4):
        rx = cx + i * cnp_hw * 0.26
        pygame.draw.line(canopy, GOLD, (int(cx), int(cnp_cy - cnp_h * 0.98)),
                         (int(rx), int(cnp_cy)), max(2, SS // 2))
    pygame.draw.arc(canopy, GOLD, (int(cx - cnp_hw), int(cnp_cy - cnp_h),
                                   int(cnp_hw * 2), int(cnp_h * 2)),
                    math.radians(180), math.radians(360), max(2, SS // 2))
    # finial knob at the very top
    pygame.draw.circle(canopy, GOLD, (int(cx), int(cnp_cy - cnp_h * 0.98)), int(w * 0.05))
    core_shade(canopy, TEAL_SH, 120)
    triad_sheen(canopy, top_a=90, bot_a=40)
    s.blit(canopy, (0, 0))

    # marigold fringe hung along the canopy rim (the festive cap tell)
    fr = new_surf(w, h)
    for i in range(scallops):
        fx = cx - cnp_hw + (2 * cnp_hw) * (i + 0.5) / scallops
        b, sh, hi = ((MARIGOLD, MARI_SH, MARI_HI) if i % 2 == 0
                     else (PINK, PINK_SH, _lite(PINK, 0.5)))
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
    fluted-pole SHAFT body with a scalloped marigold canopy gap-edge CAP at
    each gap (top cap points DOWN into the gap, bottom cap points UP)."""
    prop = build_parasol()
    pw, ph = prop.get_size()
    # canopy cap occupies the top ~38% of the prop; the rest is shaft.
    cap_h = int(ph * 0.40)
    cap = prop.subsurface((0, 0, pw, cap_h)).copy()
    shaft = prop.subsurface((0, cap_h, pw, ph - cap_h)).copy()

    surf = new_surf(pw, height)
    # tile the shaft down the full height
    sh = shaft.get_height()
    y = 0
    while y < height:
        surf.blit(shaft, (0, y))
        y += sh
    # cap at the bottom gap-edge (canopy blooming UP at the gap)
    flipped_cap = pygame.transform.flip(cap, False, True)
    surf.blit(flipped_cap, (0, height - cap_h))
    return surf, cap, shaft


# ═══════════════════════════════════════════════════════════════════════════
# SHEET
# ═══════════════════════════════════════════════════════════════════════════
catrina = build_catrina()
parasol = build_parasol()
pillar, cap, shaft = build_pillar(300)

# Build a top+bottom mirrored gap pillar pair for the review (the in-game read)
GAP = 150
top_pillar = new_surf(parasol.get_width(), 300)
bot_pillar, _, _ = build_pillar(300)
# top pillar = canopy cap pointing DOWN into gap + shaft above
cap_h = int(parasol.get_height() * 0.40)
top_shaft_h = 300 - cap_h
y = 0
while y < top_shaft_h:
    top_pillar.blit(shaft, (0, y))
    y += shaft.get_height()
top_pillar.blit(cap, (0, top_shaft_h))   # canopy blooms DOWN at the gap


BG = (44, 48, 66)
PANEL = (56, 62, 84)
PANEL2 = (50, 56, 76)
TITLE = (236, 242, 255)
SUB = (180, 190, 212)
ACCENT = (250, 196, 120)

_FONT = os.path.join(_ROOT, "game", "assets", "LiberationSans-Bold.ttf")
ftitle = pygame.font.Font(_FONT, 30)
fhead = pygame.font.Font(_FONT, 20)
fbody = pygame.font.Font(_FONT, 14)
ftiny = pygame.font.Font(_FONT, 12)


def sky_panel(rect, top=(108, 170, 214), bot=(184, 214, 232)):
    """A soft day-sky gradient panel so the sprite reads on its real backdrop."""
    p = new_surf(rect.w, rect.h)
    for yy in range(rect.h):
        t = yy / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, col, (0, yy), (rect.w, yy))
    sheet.blit(p, rect.topleft)
    pygame.draw.rect(sheet, (28, 32, 46), rect, 2, border_radius=10)


def scaled(spr, sc):
    w, h = spr.get_size()
    return pygame.transform.smoothscale(spr, (max(1, round(w * sc)), max(1, round(h * sc))))


def blit_center(spr, rect, dy=0):
    x = rect.centerx - spr.get_width() // 2
    y = rect.centery - spr.get_height() // 2 + dy
    sheet.blit(spr, (x, y))


SHEET_W, SHEET_H = 1000, 760
sheet = new_surf(SHEET_W, SHEET_H)
sheet.fill(BG)

# header
sheet.blit(ftitle.render("CATRINA  —  round 1", True, TITLE), (28, 18))
sheet.blit(fbody.render(
    "La Calavera Catrina — the elegant flower-crowned Day-of-the-Dead lady. "
    "Colossal plumed HAT (far wider than the head) over a long-necked hourglass gown.",
    True, SUB), (28, 54))
sheet.blit(ftiny.render(
    "Palette: ash-white bone (238,230,222) - cool-grey - marigold (244,150,44) - "
    "hot-pink (228,86,140) - teal gown (54,150,150) - gold trim - ink. Couture festive.",
    True, ACCENT), (28, 76))

M = 28
top_y = 100

# --- LEFT: hero creature on day-sky ---
hero_rect = pygame.Rect(M, top_y, 300, 430)
sky_panel(hero_rect)
sheet.blit(fhead.render("Catrina  (hero)", True, TITLE), (hero_rect.x + 12, hero_rect.y + 8))
blit_center(scaled(catrina, 2.7), hero_rect, dy=24)

# --- MID: parasol prop + scale strip ---
prop_rect = pygame.Rect(hero_rect.right + 18, top_y, 220, 430)
sky_panel(prop_rect, top=(196, 184, 214), bot=(214, 200, 222))
sheet.blit(fhead.render("Parasol prop", True, TITLE), (prop_rect.x + 12, prop_rect.y + 8))
blit_center(scaled(parasol, 2.3), prop_rect, dy=20)
sheet.blit(ftiny.render("fluted pole + scalloped", True, (60, 50, 70)),
           (prop_rect.x + 12, prop_rect.bottom - 38))
sheet.blit(ftiny.render("marigold-fringed canopy", True, (60, 50, 70)),
           (prop_rect.x + 12, prop_rect.bottom - 22))

# --- RIGHT: pillar mirror (top + bottom with gap) ---
pil_rect = pygame.Rect(prop_rect.right + 18, top_y, 386, 430)
sky_panel(pil_rect, top=(120, 178, 218), bot=(190, 218, 234))
sheet.blit(fhead.render("Pillar mirror (gap)", True, TITLE), (pil_rect.x + 12, pil_rect.y + 8))
# place a top pillar hanging from the top and a bottom pillar rising, with a gap
clip = sheet.get_clip()
inner = pil_rect.inflate(-8, -8)
sheet.set_clip(inner)
pcx = pil_rect.centerx - parasol.get_width() // 2
# top pillar (canopy points down into gap)
gap_top = pil_rect.y + 38
sheet.blit(top_pillar, (pcx, gap_top - 130))
# bottom pillar (canopy points up at gap)
sheet.blit(bot_pillar, (pcx, gap_top + GAP))
sheet.set_clip(clip)
sheet.blit(ftiny.render("repeatable shaft + canopy gap-cap; round on-axis = clean mirror",
                        True, (235, 242, 252)), (pil_rect.x + 12, pil_rect.bottom - 22))

# --- BOTTOM: 32px gameplay-scale read row + zoom ---
row_y = hero_rect.bottom + 16
row_rect = pygame.Rect(M, row_y, SHEET_W - 2 * M, SHEET_H - row_y - 20)
pygame.draw.rect(sheet, PANEL2, row_rect, border_radius=10)
sheet.blit(fhead.render("Gameplay scale", True, TITLE), (row_rect.x + 12, row_rect.y + 8))

# 32px reads against a small day-sky chip, plus a near-true-pixel and a 2x zoom
def chip(rect, top=(112, 172, 216), bot=(186, 216, 232)):
    p = new_surf(rect.w, rect.h)
    for yy in range(rect.h):
        t = yy / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, col, (0, yy), (rect.w, yy))
    sheet.blit(p, rect.topleft)
    pygame.draw.rect(sheet, (28, 32, 46), rect, 1, border_radius=4)


# Catrina at 32px tall (height-target the gameplay creature size)
def fit_h(spr, target_h):
    w, h = spr.get_size()
    sc = target_h / h
    return scaled(spr, sc)


cat32 = fit_h(catrina, 32)
cat48 = fit_h(catrina, 48)
para32 = fit_h(parasol, 40)

cy = row_rect.y + 44
# chip 1: true 32px Catrina
c1 = pygame.Rect(row_rect.x + 20, cy, 80, 96)
chip(c1)
blit_center(cat32, c1)
sheet.blit(ftiny.render("32px", True, (24, 30, 44)), (c1.x + 4, c1.bottom - 16))

# chip 2: 32px zoomed 3x (nearest) to inspect read
c2 = pygame.Rect(c1.right + 16, cy, 110, 96)
chip(c2)
z = pygame.transform.scale(cat32, (cat32.get_width() * 3, cat32.get_height() * 3))
blit_center(z, c2)
sheet.blit(ftiny.render("32px x3", True, (24, 30, 44)), (c2.x + 4, c2.bottom - 16))

# chip 3: 48px Catrina
c3 = pygame.Rect(c2.right + 16, cy, 96, 96)
chip(c3)
blit_center(cat48, c3)
sheet.blit(ftiny.render("48px", True, (24, 30, 44)), (c3.x + 4, c3.bottom - 16))

# chip 4: parasol prop small
c4 = pygame.Rect(c3.right + 16, cy, 70, 96)
chip(c4, top=(196, 184, 214), bot=(214, 200, 222))
blit_center(para32, c4)
sheet.blit(ftiny.render("prop", True, (40, 34, 54)), (c4.x + 4, c4.bottom - 16))

# chip 5: mini pillar gap pair at small scale
c5 = pygame.Rect(c4.right + 16, cy, 120, 96)
chip(c5, top=(120, 178, 218), bot=(190, 218, 234))
mini_top = fit_h(top_pillar, 60)
mini_bot = fit_h(bot_pillar, 60)
clip = sheet.get_clip()
sheet.set_clip(c5)
mcx = c5.centerx - mini_top.get_width() // 2
sheet.blit(mini_top, (mcx, c5.y - 20))
sheet.blit(mini_bot, (mcx, c5.y + 64))
sheet.set_clip(clip)
sheet.blit(ftiny.render("pillar", True, (235, 242, 252)), (c5.x + 4, c5.bottom - 16))

# read note
sheet.blit(ftiny.render(
    "Accessibility tell: wide-brim HAT silhouette + gown hourglass carry the read "
    "independent of the marigold hue.", True, SUB),
    (c5.right + 24, cy + 30))
sheet.blit(ftiny.render(
    "Triad: dark-core (cool-grey) -> flat bone/teal fill -> top-left sheen; "
    "1px ink keyline; supersample->smoothscale.", True, SUB),
    (c5.right + 24, cy + 50))

os.makedirs(_OUT_DIR, exist_ok=True)
out_path = os.path.join(_OUT_DIR, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
