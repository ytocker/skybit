"""Round-3 concept sheet — DRAUGR, the barrow-mound viking bone-warrior.

FINAL designer pass: a two-item surgical recolor of the round-2 sheet, folding
in the round-2 AD critique. Everything else is held exactly as round 2 shipped.

  A. Helm brow-cap recoloured to the CLEAR rust-iron family (150,96,62) -> dark
     core, replacing round 2's brightened cap that drifted pale and read as more
     frost-bone. Value order now: dark iron cap -> bright bone skull -> cyan jaw.
  B. Stray cyan facet on the nose-guard removed — the single crown rime cluster
     is now clamped above the brow line and away from the nose-guard column, so
     cyan stays the jaw + socket-pupil focal only.

--- round-2 notes, retained for context ---
Round-2 resolved the AD critique on round-1:
the oversized neutral-silver helm read as a "grey knight" and stole focus from
the frost-bone skull + ice jaw that ARE the identity. Fixes applied here:

  1. Helm dome shrunk + recoloured toward rust-iron + bronze trim and seated as
     a low BROW-CAP, so the frost-bone skull (the lightest mass) now dominates
     the head and the figure reads "frosted barrow-undead," not "metal helmet."
  2. Ice-cyan disciplined to TWO places only: the glowing jaw and ONE restrained
     rime cluster on the helm crown / brow. Scattered cyan dots over mail,
     shield, and ground are gone (they read as JPEG noise at 1x).
  3. Horns redrawn as short, thick, outward-angled stubby cattle nubs that
     survive a 24px downscale instead of vanishing as salt-and-pepper spikes.
  4. Mail studs thinned + dropped in value so they stop competing with the jaw.
  5. Moss-crust brought UP onto shoulders + helm crown (grave-mound thesis),
     not just a base sliver.
  6. Non-hue cold tell: crystalline WHITE-sheen rime facets so the "cold one"
     read survives for colourblind players, independent of the cyan.
  7. Angry-arched sockets + nose-guard shadow for chibi menace.
  8. The prop -> PILLAR axe mirror is kept essentially as-is (round-1's best
     element per the AD), only nudged for stud/cyan discipline consistency.

Reuses the house supersample kit (dark-core -> flat-fill -> top-left rim-sheen
TRIAD, hard ink keylines, 1px alpha-grown silhouette outline, supersample ->
smoothscale) so the exploration reads like real game art.

Run:  SDL_VIDEODRIVER=dummy python docs/skybit_devil/batch2/draugr/render_round_3.py
Out:  docs/skybit_devil/batch2/draugr/round_3.png

Exploration only; nothing here is wired into the live game.
"""

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))


# ---------------------------------------------------------------------------
# Supersample kit (mirrors the project draw conventions; kept local so the
# exploration is dependency-free). Art is built at SS scale then smoothscaled
# down so curves + the single top-left key-light highlight stay crisp at 32px.
# ---------------------------------------------------------------------------
_SS = 4


def _lerp(a, b, t):
    return a + (b - a) * t


def _mix(c1, c2, t):
    return (int(_lerp(c1[0], c2[0], t)),
            int(_lerp(c1[1], c2[1], t)),
            int(_lerp(c1[2], c2[2], t)))


def _shade(c, f):
    return (max(0, min(255, int(c[0] * f))),
            max(0, min(255, int(c[1] * f))),
            max(0, min(255, int(c[2] * f))))


# ---- PINNED PALETTE (Draugr) — copied verbatim from the locked brief -------
PAL = {
    "bone":    (216, 222, 224),   # frost-bone base
    "slate":   (140, 152, 162),   # cold-slate shade
    "ice":     (150, 212, 224),   # ice-cyan jaw-glow accent
    "rust":    (150,  96,  62),   # rust-iron mail
    "moss":    ( 98, 128,  76),   # moss-green crust
    "bronze":  (178, 134,  70),   # bronze helm-trim
    "ink":     ( 26,  30,  34),   # ink keyline
    "sheen":   (238, 246, 250),   # top-left rim-sheen
}
# Extra in-family steps derived from the pinned hues (darker cores / wood).
PAL["bone_d"]   = _shade(PAL["bone"], 0.74)            # bone dark-core
PAL["bone_hi"]  = (236, 240, 242)                      # near-sheen bone crown
PAL["rust_d"]   = _shade(PAL["rust"], 0.66)            # mail dark-core
PAL["rust_hi"]  = _shade(PAL["rust"], 1.18)            # iron-helm light face
PAL["moss_d"]   = _shade(PAL["moss"], 0.68)
PAL["bronze_d"] = _shade(PAL["bronze"], 0.66)
PAL["bronze_hi"] = _shade(PAL["bronze"], 1.2)
PAL["wood"]     = (120, 86, 54)                        # shield planks (rust-family wood)
PAL["wood_d"]   = _shade((120, 86, 54), 0.66)
PAL["ice_d"]    = _shade(PAL["ice"], 0.74)
PAL["socket"]   = (44, 60, 70)                         # cold dead eye-socket

_OUTLINE = PAL["ink"]
_OW = max(2, 3 * _SS // 2)   # ~1.5px ink keyline at the 32px footprint


def _new_raw(size):
    return pygame.Surface((size * _SS, size * _SS), pygame.SRCALPHA)


# ---------------------------------------------------------------------------
# TRIAD shading primitives: dark-core gradient fill + one top-left key light.
# ---------------------------------------------------------------------------
def _vgrad_poly(surf, pts, top, bottom):
    """Vertical dark-core gradient clipped to a polygon mask (flat-fill body)."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    y0, y1 = int(min(ys)), int(max(ys))
    W, H = surf.get_size()
    band = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(max(0, y0), min(H, y1 + 1)):
        t = (y - y0) / max(1, (y1 - y0))
        pygame.draw.line(band, _mix(top, bottom, t), (0, y), (W, y))
    mask = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(band, (0, 0))


def _vgrad_circle(surf, cx, cy, r, top, bottom):
    if r <= 0:
        return
    grad = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for y in range(r * 2):
        t = y / max(1, (r * 2 - 1))
        pygame.draw.line(grad, _mix(top, bottom, t), (0, y), (r * 2, y))
    mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (cx - r, cy - r))


def _key_light(surf, cx, cy, r, strength=58):
    """Top-left specular bloom — the single shared light direction (rim-sheen)."""
    if r <= 0:
        return
    hl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(hl, (255, 255, 255, strength),
                       (int(r * 0.66), int(r * 0.58)), int(r * 0.6))
    hl = pygame.transform.smoothscale(hl, (r * 2, r * 2))
    mask = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (r, r), r)
    hl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(hl, (cx - r, cy - r))


def _grow_outline(ss):
    """1px (at footprint) ink outline grown from the alpha mask -> a clean POP
    silhouette around the whole figure, the way the live sprites do it."""
    mask = pygame.mask.from_surface(ss)
    if mask.count() == 0:
        return ss
    outline = pygame.Surface(ss.get_size(), pygame.SRCALPHA)
    w = max(1, _SS)
    pts = mask.outline(2)
    if len(pts) >= 2:
        pygame.draw.lines(outline, _OUTLINE, True, pts, w * 2)
    out = pygame.Surface(ss.get_size(), pygame.SRCALPHA)
    out.blit(outline, (0, 0))
    out.blit(ss, (0, 0))
    return out


def _rime_facet(ss, x, y, r):
    """A single crystalline frost facet: a small WHITE-sheen diamond with a
    faint ice-cyan core. The white diamond GEOMETRY is the non-hue cold tell
    (survives for colourblind players); the cyan only tints the centre."""
    diamond = [(x, y - r), (x + int(r * 0.7), y), (x, y + r), (x - int(r * 0.7), y)]
    pygame.draw.polygon(ss, PAL["sheen"], diamond)
    if r >= 4:
        core = [(x, y - r // 2), (x + r // 3, y), (x, y + r // 2), (x - r // 3, y)]
        pygame.draw.polygon(ss, PAL["ice"], core)


def _rime_cluster(ss, S, rnd, cx, cy, spread, n, y_max=None, no_x=None):
    """ONE restrained cluster of crystalline rime facets near a focal point —
    disciplined to the brow/crown only so the cold tell stays a focal, not a
    scattered noise field. `y_max` keeps every facet ABOVE the brow line and
    `no_x=(lo,hi)` excludes the nose-guard column, so the cluster can't drop a
    stray cyan dot onto the nose-guard that would fight the jaw for the focal."""
    placed = 0
    guard = 0
    while placed < n and guard < n * 12:
        guard += 1
        ang = rnd.uniform(0, math.tau)
        dist = rnd.uniform(0.25, 1.0) * spread
        fx = int(cx + math.cos(ang) * dist)
        fy = int(cy + math.sin(ang) * dist * 0.7)
        if y_max is not None and fy > y_max:
            continue
        if no_x is not None and no_x[0] <= fx <= no_x[1]:
            continue
        fr = rnd.randint(max(3, S // 80), max(4, S // 50))
        _rime_facet(ss, fx, fy, fr)
        placed += 1


# ---------------------------------------------------------------------------
# THE CREATURE — bottom-heavy armored draugr brute.
# ---------------------------------------------------------------------------
def build_draugr(size):
    import random
    rnd = random.Random(11)
    ss = _new_raw(size)
    S = size * _SS
    cx = S // 2

    # ---------------------------------------------------------------- body
    # Square mossy ribcage torso in rusted mail. Bottom-heavy: wide blocky
    # base, slight inward shoulder so the head crowns it.
    sh_y = int(S * 0.45)    # shoulder line
    hip_y = int(S * 0.86)   # base (sits low + wide -> brute weight)
    half_sh = int(S * 0.30)
    half_hip = int(S * 0.345)
    torso = [(cx - half_sh, sh_y), (cx + half_sh, sh_y),
             (cx + half_hip, hip_y), (cx - half_hip, hip_y)]
    _vgrad_poly(ss, torso, PAL["rust"], PAL["rust_d"])

    # Mail link banding — thinner, LOWER-value scoops so the rows stop competing
    # with the ice jaw as a second bright field (AD fix #4). Studs are now small
    # rust-dark dimples with only a faint dim sheen, not bright white dots.
    for ri, ry in enumerate(range(sh_y + int(S * 0.05), hip_y, int(S * 0.06))):
        t = (ry - sh_y) / max(1, hip_y - sh_y)
        rw = int(_lerp(half_sh, half_hip, t))
        step = max(3, int(S * 0.055))
        off = (step // 2) if ri % 2 else 0
        for lx in range(cx - rw + off, cx + rw, step):
            pygame.draw.circle(ss, PAL["rust_d"], (lx, ry), max(2, step // 4))
            pygame.draw.circle(ss, _shade(PAL["rust"], 1.12),
                               (lx - 1, ry - 1), max(1, step // 9))

    # Moss-green crust: a broad creeping band up the lower body PLUS shoulder
    # epaulettes, so the "grave-mound, moss-crusted" thesis reads (AD fix #5).
    moss_band = [(cx - half_hip, hip_y - int(S * 0.22)),
                 (cx + half_hip, hip_y - int(S * 0.14)),
                 (cx + half_hip, hip_y), (cx - half_hip, hip_y)]
    _vgrad_poly(ss, moss_band, PAL["moss"], PAL["moss_d"])
    for _ in range(9):
        mx = rnd.randint(cx - half_hip + 6, cx + half_hip - 6)
        my = rnd.randint(hip_y - int(S * 0.18), hip_y - int(S * 0.02))
        pygame.draw.circle(ss, PAL["moss"], (mx, my), rnd.randint(3, max(5, S // 44)))
        pygame.draw.circle(ss, _shade(PAL["moss"], 1.2),
                           (mx - 1, my - 1), max(1, S // 110))
    # moss epaulettes creeping over each shoulder
    for sgn in (-1, 1):
        ex = cx + sgn * int(half_sh * 0.78)
        for _ in range(4):
            mx = ex + rnd.randint(-int(S * 0.06), int(S * 0.06))
            my = sh_y + rnd.randint(-int(S * 0.01), int(S * 0.05))
            pygame.draw.circle(ss, PAL["moss"], (mx, my),
                               rnd.randint(3, max(4, S // 56)))

    # A couple of exposed frost-bone ribs over the mail (skeletal show-through).
    for sgn in (-1, 1):
        for i in range(2):
            ry = sh_y + int(S * 0.10) + i * int(S * 0.075)
            rib = [(cx, ry), (cx + sgn * int(S * 0.18), ry + int(S * 0.02)),
                   (cx + sgn * int(S * 0.17), ry + int(S * 0.05)),
                   (cx, ry + int(S * 0.035))]
            pygame.draw.polygon(ss, PAL["bone"], rib)
            pygame.draw.polygon(ss, PAL["bone_d"], rib, max(1, _SS))

    # ---------------------------------------------------- left arm: SHIELD
    # Round wooden shield held forward on the figure's left (viewer right),
    # iron boss + radial planks + rust rim. Big circular mass = a supporting
    # read once the head pops; rim nudged a hair darker so it doesn't tie the
    # head for "biggest disc" (AD fix on shield weight).
    sx = cx + int(S * 0.27)
    sy = int(S * 0.66)
    sr = int(S * 0.215)
    _vgrad_circle(ss, sx, sy, sr, _shade(PAL["wood"], 1.14), PAL["wood_d"])
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        pygame.draw.line(ss, PAL["wood_d"],
                         (sx, sy), (sx + math.cos(a) * sr, sy + math.sin(a) * sr),
                         max(2, _SS))
    # rust-iron rim band (slightly darker so the head wins the value contest)
    pygame.draw.circle(ss, PAL["rust_d"], (sx, sy), sr, max(3, int(S * 0.035)))
    pygame.draw.circle(ss, _shade(PAL["rust"], 0.55), (sx, sy), sr, max(1, _SS))
    # central iron boss (cold metal glint)
    _vgrad_circle(ss, sx, sy, int(sr * 0.33),
                  _shade(PAL["slate"], 1.18), _shade(PAL["slate"], 0.62))
    pygame.draw.circle(ss, _OUTLINE, (sx, sy), int(sr * 0.33), max(2, _SS))
    pygame.draw.circle(ss, _OUTLINE, (sx, sy), sr, _OW)
    _key_light(ss, sx, sy, sr, 40)

    # ---------------------------------------------- right arm: BEARDED AXE
    # Stubby bearded axe in the figure's right hand (viewer left). Short haft
    # + broad crescent (bearded = long lower lobe) head -> the second hero tell.
    hx = cx - int(S * 0.27)
    haft_top = int(S * 0.31)
    haft_bot = int(S * 0.74)
    haft_w = max(3, int(S * 0.045))
    pygame.draw.line(ss, PAL["wood"], (hx, haft_top), (hx, haft_bot), haft_w)
    pygame.draw.line(ss, PAL["wood_d"], (hx + haft_w // 2, haft_top),
                     (hx + haft_w // 2, haft_bot), max(1, _SS))
    # crescent axe-head: outer arc + concave inner edge, with bearded lower lobe.
    head_cx = hx - int(S * 0.085)
    head_cy = haft_top + int(S * 0.10)
    ar = int(S * 0.165)
    blade = []
    for ang in range(-78, 86, 6):
        a = math.radians(ang)
        blade.append((head_cx + math.cos(a) * ar * 0.55 + ar * 0.55,
                      head_cy + math.sin(a) * ar))
    blade.append((hx - int(S * 0.02), head_cy + ar + int(S * 0.06)))
    blade += [(hx, head_cy + ar - int(S * 0.02)), (hx, head_cy - ar + int(S * 0.02))]
    _vgrad_poly(ss, blade, _shade(PAL["slate"], 1.22), _shade(PAL["slate"], 0.6))
    pygame.draw.polygon(ss, _OUTLINE, blade, _OW)
    pygame.draw.lines(ss, PAL["sheen"], False,
                      [(head_cx + ar * 0.55 + ar * 0.42, head_cy - ar * 0.7),
                       (head_cx + ar * 1.1, head_cy),
                       (hx - int(S * 0.01), head_cy + ar)], max(2, _SS))

    # ---------------------------------------------------------- skull face
    # Half-rotted FROST-BONE skull crowned by a LOW brow-cap helm. The skull is
    # enlarged + lifted so a tall frost-bone cranium shows ABOVE the brow band:
    # bone is now the lightest, largest head mass (AD primary fix).
    fx, fy = cx, int(S * 0.345)
    fw, fh = int(S * 0.235), int(S * 0.225)
    face = [(fx - fw, fy - int(fh * 1.05)), (fx + fw, fy - int(fh * 1.05)),
            (fx + fw, fy + int(fh * 0.35)),
            (fx + int(fw * 0.84), fy + fh), (fx - int(fw * 0.84), fy + fh),
            (fx - fw, fy + int(fh * 0.35))]
    _vgrad_poly(ss, face, PAL["bone"], PAL["bone_d"])
    # cranium crown gets a lighter near-sheen cap so the bone dome reads as the
    # brightest head mass (replacing the old silver helm dome as the value peak)
    crown = [(fx - int(fw * 0.92), fy - int(fh * 0.62)),
             (fx, fy - int(fh * 1.05)),
             (fx + int(fw * 0.92), fy - int(fh * 0.62))]
    _vgrad_poly(ss, crown, PAL["bone_hi"], PAL["bone"])

    # frost-blue lower jaw (focal ice-cyan #1 — the cold glow that IDs the brute)
    jaw = [(fx - int(fw * 0.7), fy + int(fh * 0.28)),
           (fx + int(fw * 0.7), fy + int(fh * 0.28)),
           (fx + int(fw * 0.56), fy + fh + int(S * 0.05)),
           (fx - int(fw * 0.56), fy + fh + int(S * 0.05))]
    _vgrad_poly(ss, jaw, PAL["ice"], PAL["ice_d"])
    # teeth across the jaw line — bone-white, kept modest
    tooth_y = fy + int(fh * 0.4)
    for tx in range(fx - int(fw * 0.54), fx + int(fw * 0.54), max(3, int(S * 0.045))):
        pygame.draw.rect(ss, PAL["bone_hi"],
                         (tx, tooth_y, max(2, int(S * 0.024)), int(S * 0.05)))
        pygame.draw.rect(ss, PAL["ice_d"],
                         (tx, tooth_y, max(2, int(S * 0.024)), int(S * 0.05)),
                         max(1, _SS // 2))
    # a soft ice underglow halo beneath the jaw so the cyan reads as a GLOW
    glow = pygame.Surface((S, S), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (PAL["ice"][0], PAL["ice"][1], PAL["ice"][2], 70),
                        (fx - int(fw * 0.8), fy + int(fh * 0.5),
                         int(fw * 1.6), int(fh * 0.7)))
    ss.blit(glow, (0, 0))

    # deep cold eye-sockets, angry-arched (chibi menace) with a faint ice glint
    for sgn in (-1, 1):
        ex = fx + sgn * int(fw * 0.4)
        ey = fy - int(fh * 0.04)
        er = int(fw * 0.3)
        # angled socket: top edge slants toward the nose -> furrowed scowl
        sock = [(ex - er, ey - int(er * 0.2)),
                (ex + er, ey - int(er * 0.7)) if sgn < 0 else (ex - er, ey - int(er * 0.7)),
                (ex + er, ey - int(er * 0.2)),
                (ex + er, ey + er), (ex - er, ey + er)]
        # simpler reliable angry socket: a circle with a slanted brow shadow
        pygame.draw.circle(ss, PAL["socket"], (ex, ey), er)
        pygame.draw.circle(ss, PAL["bone_d"], (ex, ey), er, max(2, _SS))
        # tiny ice pupil deep inside
        pygame.draw.circle(ss, PAL["ice"], (ex - sgn * er // 5, ey + er // 6),
                           max(2, er // 3))
        # slanted brow-shadow wedge above the inner top of the socket = scowl
        brow = [(ex - sgn * int(er * 1.1), ey - int(er * 1.25)),
                (ex + sgn * int(er * 1.1), ey - int(er * 0.65)),
                (ex + sgn * int(er * 1.1), ey - int(er * 0.3)),
                (ex - sgn * int(er * 1.1), ey - int(er * 0.85))]
        pygame.draw.polygon(ss, PAL["bone_d"], brow)

    # crack across the rotted brow (skeletal damage)
    pygame.draw.lines(ss, PAL["bone_d"], False,
                      [(fx - int(fw * 0.3), fy - int(fh * 0.75)),
                       (fx - int(fw * 0.05), fy - int(fh * 0.5)),
                       (fx + int(fw * 0.12), fy - int(fh * 0.7))], max(2, _SS))

    # ----------------------------------------------- LOW iron brow-cap helm
    # A SMALL rust-iron brow band + nose-guard with bronze trim — NOT a big
    # silver dome. It rides low across the brow and frames the bone cranium
    # above it, so frost-bone wins the head (AD primary fix). Rust-iron family
    # also keeps it clear of Raijin's storm-grey.
    brow_y = fy - int(fh * 0.5)
    brow_h = int(fh * 0.42)
    band = (fx - fw - int(S * 0.01), brow_y, (fw + int(S * 0.01)) * 2, brow_h)
    # Cap fill pinned to the canonical rust-iron (150,96,62) -> dark-core, NOT the
    # brightened rust_hi: round 2 drifted pale and read as more frost-bone, so the
    # value order now lands dark iron cap -> bright bone skull -> cyan jaw.
    _vgrad_poly(ss, [(band[0], band[1]), (band[0] + band[2], band[1]),
                     (band[0] + band[2], band[1] + band[3]),
                     (band[0], band[1] + band[3])],
                PAL["rust"], PAL["rust_d"])
    # bronze trim lines top + bottom of the brow band
    pygame.draw.rect(ss, PAL["bronze_hi"], (band[0], band[1], band[2], max(2, int(S * 0.02))))
    pygame.draw.rect(ss, PAL["bronze"], (band[0], band[1] + band[3] - max(2, int(S * 0.022)),
                                         band[2], max(2, int(S * 0.022))))
    pygame.draw.rect(ss, _OUTLINE,
                     (band[0], band[1], band[2], band[3]), max(1, _SS))
    # nose-guard dropping from the brow band over the face center, with a
    # shaded right side for menace
    ng_w = max(3, int(S * 0.055))
    ng = (fx - ng_w // 2, brow_y + brow_h - max(1, _SS), ng_w, int(fh * 0.95))
    pygame.draw.rect(ss, PAL["rust"], ng)
    pygame.draw.rect(ss, _shade(PAL["rust"], 1.1), (fx - ng_w // 2, ng[1], max(1, _SS), ng[3]))
    pygame.draw.rect(ss, PAL["rust_d"], (fx + ng_w // 2 - max(1, _SS), ng[1],
                                         max(1, _SS), ng[3]))
    pygame.draw.rect(ss, _OUTLINE, ng, max(1, _SS))
    # a single bronze rivet on each side of the brow band
    for sgn in (-1, 1):
        pygame.draw.circle(ss, PAL["bronze"],
                           (fx + sgn * int(fw * 0.7), brow_y + brow_h // 2),
                           max(2, int(S * 0.018)))

    # two SHORT THICK outward-angled cattle-horn nubs from the helm-band corners
    # (AD fix #3) — chunky enough to survive a 24px downscale.
    for sgn in (-1, 1):
        bx = fx + sgn * (fw - int(S * 0.01))
        by = brow_y + int(brow_h * 0.45)
        horn = [(bx - sgn * int(S * 0.02), by + int(S * 0.05)),
                (bx, by - int(S * 0.02)),
                (bx + sgn * int(S * 0.075), by - int(S * 0.075)),
                (bx + sgn * int(S * 0.13), by - int(S * 0.115)),
                (bx + sgn * int(S * 0.115), by - int(S * 0.045)),
                (bx + sgn * int(S * 0.085), by + int(S * 0.02)),
                (bx + sgn * int(S * 0.045), by + int(S * 0.065))]
        _vgrad_poly(ss, horn, PAL["bone"], PAL["bone_d"])
        pygame.draw.polygon(ss, _OUTLINE, horn, _OW)
        # subtle banding ring on the horn
        pygame.draw.line(ss, PAL["bone_d"],
                         (bx + sgn * int(S * 0.04), by - int(S * 0.02)),
                         (bx + sgn * int(S * 0.075), by - int(S * 0.055)),
                         max(1, _SS))

    _key_light(ss, fx - int(fw * 0.2), fy - int(fh * 0.55), int(fw * 0.66), 44)

    # frost rime — ONE restrained crystalline cluster on the bone CROWN above
    # the brow band, with the nose-guard column excluded so no stray cyan facet
    # competes with the jaw for the cold focal (AD fix #2). White-diamond facets
    # are the non-hue cold tell.
    _rime_cluster(ss, S, rnd, fx - int(fw * 0.3), fy - int(fh * 0.8),
                  int(fw * 0.7), n=5,
                  y_max=brow_y - max(2, _SS),
                  no_x=(fx - ng_w, fx + ng_w))

    # silhouette outline grown from the mask, then downsample.
    ss = _grow_outline(ss)
    return pygame.transform.smoothscale(ss, (size, size))


# ---------------------------------------------------------------------------
# PROP -> PILLAR mirror — the bearded battle-axe, haft-down. Kept as round-1's
# best element; only the rune cyan is left as a single restrained tell and the
# rime on the blade is now crystalline facets to match the creature's cold tell.
#   shaft body  = rune-carved haft (repeatable, tileable rune banding)
#   gap cap     = broad crescent axe-head biting the gap (detachable)
# Crescent mass is centered on the haft axis -> clean vertical mirror.
# ---------------------------------------------------------------------------
def build_pillar(width, height, with_cap=True):
    ss = pygame.Surface((width * _SS, height * _SS), pygame.SRCALPHA)
    W, H = width * _SS, height * _SS
    cx = W // 2

    # ---- rune-carved haft shaft (repeatable body) ----
    half_w = int(W * 0.20)
    shaft_top = int(H * 0.30) if with_cap else 0
    shaft = [(cx - half_w, shaft_top), (cx + half_w, shaft_top),
             (cx + half_w, H), (cx - half_w, H)]
    _vgrad_poly(ss, shaft, _shade(PAL["wood"], 1.16), PAL["wood_d"])
    band = int(H * 0.16)
    runes = [["v", "x"], ["x", "v"], ["i", "x"]]
    for i, by in enumerate(range(shaft_top + band, H, band)):
        pygame.draw.rect(ss, PAL["rust"], (cx - half_w, by, half_w * 2, max(3, int(H * 0.018))))
        pygame.draw.rect(ss, PAL["rust_d"], (cx - half_w, by + max(3, int(H * 0.018)),
                                             half_w * 2, max(1, _SS)))
        ry = by + band // 2
        rn = runes[i % len(runes)]
        rx = cx - half_w // 2
        for gl in rn:
            if gl == "v":
                pygame.draw.lines(ss, PAL["ice"], False,
                                  [(rx, ry - band // 6), (rx + half_w // 4, ry + band // 6),
                                   (rx + half_w // 2, ry - band // 6)], max(2, _SS))
            elif gl == "x":
                pygame.draw.line(ss, PAL["ice"], (rx, ry - band // 6),
                                 (rx + half_w // 3, ry + band // 6), max(2, _SS))
                pygame.draw.line(ss, PAL["ice"], (rx + half_w // 3, ry - band // 6),
                                 (rx, ry + band // 6), max(2, _SS))
            else:
                pygame.draw.line(ss, PAL["ice"], (rx + half_w // 6, ry - band // 5),
                                 (rx + half_w // 6, ry + band // 5), max(2, _SS))
            rx += half_w // 2
    pygame.draw.line(ss, _shade(PAL["wood"], 1.4),
                     (cx - half_w + max(2, _SS), shaft_top),
                     (cx - half_w + max(2, _SS), H), max(2, _SS))
    pygame.draw.polygon(ss, _OUTLINE, shaft, _OW)

    # ---- broad crescent axe-head cap (detachable gap-edge cap) ----
    if with_cap:
        hcy = int(H * 0.20)
        ar = int(W * 0.42)
        blade = []
        for ang in range(-90, 91, 6):
            a = math.radians(ang)
            blade.append((cx + math.sin(a) * ar,
                          hcy - math.cos(a) * ar * 0.62))
        blade.append((cx + int(W * 0.18), hcy + int(H * 0.10)))
        blade.append((cx - int(W * 0.18), hcy + int(H * 0.10)))
        _vgrad_poly(ss, blade, _shade(PAL["slate"], 1.22), _shade(PAL["slate"], 0.6))
        pygame.draw.polygon(ss, _OUTLINE, blade, _OW)
        glint = [(cx - ar * 0.92, hcy - ar * 0.18),
                 (cx, hcy - ar * 0.62), (cx + ar * 0.92, hcy - ar * 0.18)]
        pygame.draw.lines(ss, PAL["sheen"], False, glint, max(2, _SS))
        col = (cx - int(W * 0.16), hcy + int(H * 0.085), int(W * 0.32), int(H * 0.045))
        pygame.draw.rect(ss, PAL["bronze"], col)
        pygame.draw.rect(ss, PAL["bronze_d"], col, max(1, _SS))
        # crystalline rime facets on the blade (matches creature's cold tell)
        import random
        rnd = random.Random(5)
        for _ in range(4):
            fx = rnd.randint(cx - int(ar * 0.7), cx + int(ar * 0.7))
            fy = rnd.randint(hcy - int(ar * 0.45), hcy)
            _rime_facet(ss, fx, fy, rnd.randint(max(3, W // 26), max(4, W // 18)))

    ss = _grow_outline(ss)
    return pygame.transform.smoothscale(ss, (width, height))


# ---------------------------------------------------------------------------
# Sky panels (match the buff-emblem kit so the read is the real game).
# ---------------------------------------------------------------------------
def day_sky(w, h):
    s = pygame.Surface((w, h))
    top, bot = (118, 196, 246), (206, 240, 252)
    for y in range(h):
        pygame.draw.line(s, _mix(top, bot, y / max(1, h - 1)), (0, y), (w, y))
    return s


def night_sky(w, h):
    import random
    s = pygame.Surface((w, h))
    top, bot = (18, 22, 46), (52, 40, 78)
    for y in range(h):
        pygame.draw.line(s, _mix(top, bot, y / max(1, h - 1)), (0, y), (w, y))
    rnd = random.Random(7)
    for _ in range(int(w * h / 380)):
        x, y = rnd.randint(0, w - 1), rnd.randint(0, h - 1)
        b = rnd.randint(120, 230)
        s.set_at((x, y), (b, b, min(255, b + 20)))
    return s


def _font(sz, bold=True):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


# ---------------------------------------------------------------------------
# Sheet layout — hero showcase + prop->pillar mirror + 32px legibility + scale.
# ---------------------------------------------------------------------------
def main():
    sheet_w, sheet_h = 1180, 760
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 32, 40))

    f_title = _font(26)
    f_lbl = _font(18)
    f_small = _font(14, bold=False)

    y = 16
    sheet.blit(f_title.render(
        "DRAUGR — barrow-mound viking bone-warrior  (Batch 2 / Skeletons, round 3)",
        True, (236, 242, 248)), (24, y))
    y += 34
    sheet.blit(f_small.render(
        "R3 surgical: helm brow-cap recoloured to clear rust-iron (150,96,62) so "
        "value reads dark cap -> bright bone skull -> cyan jaw; stray cyan dot on "
        "the nose-guard removed (cyan kept to jaw + sockets + ONE crown cluster).",
        True, (170, 190, 205)), (24, y))
    y += 26

    panel_y = y
    # ---- (a) hero showcase on day + night ----
    hero_big = 300
    px = 24
    sheet.blit(f_lbl.render("(a) hero — showcase scale", True, (150, 210, 230)),
               (px, panel_y))
    by = panel_y + 24
    for label, sky in (("day", day_sky(hero_big, hero_big)),
                       ("night", night_sky(hero_big, hero_big))):
        sheet.blit(sky, (px, by))
        pygame.draw.rect(sheet, (60, 64, 72), (px, by, hero_big, hero_big), 2)
        hero = build_draugr(hero_big - 24)
        sheet.blit(hero, (px + 12, by + 12))
        sheet.blit(f_small.render(label, True, (235, 240, 248)),
                   (px + hero_big - 44, by + hero_big - 22))
        px += hero_big + 16

    # ---- (b) prop -> pillar mirror ----
    pcol_x = 24 + 2 * (hero_big + 16) + 16
    sheet.blit(f_lbl.render("(b) prop -> PILLAR", True, (150, 210, 230)),
               (pcol_x, panel_y))
    sheet.blit(f_small.render("bearded battle-axe", True, (170, 190, 205)),
               (pcol_x, panel_y + 22))
    pw, ph = 150, 392
    pby = panel_y + 44
    sheet.blit(night_sky(pw, ph), (pcol_x, pby))
    pygame.draw.rect(sheet, (60, 64, 72), (pcol_x, pby, pw, ph), 2)
    bottom = build_pillar(pw - 16, ph - 16, with_cap=True)
    sheet.blit(bottom, (pcol_x + 8, pby + 8))
    sheet.blit(f_small.render("haft body = repeatable", True, (210, 220, 230)),
               (pcol_x + 6, pby + ph + 4))
    sheet.blit(f_small.render("crescent = gap cap", True, (210, 220, 230)),
               (pcol_x + 6, pby + ph + 20))

    # ---- second panel row: 32px legibility + scale ramp + pillar mirror pair
    y = by + hero_big + 40

    # (c) 32px legibility on day + night
    sheet.blit(f_lbl.render("(c) 32px legibility — day / night", True,
                            (150, 210, 230)), (24, y))
    yy = y + 24
    cell = 48
    for label, mk in (("day", day_sky), ("night", night_sky)):
        sheet.blit(mk(cell * 3, cell), (24, yy))
        for i, s in enumerate((32, 32, 32)):
            spr = build_draugr(s)
            sheet.blit(spr, (24 + i * cell + (cell - s) // 2, yy + (cell - s) // 2))
        sheet.blit(f_small.render(label, True, (235, 240, 248)),
                   (24 + cell * 3 + 8, yy + cell // 2 - 8))
        yy += cell + 8

    # (d) scale ramp 16 / 24 / 32 / 48 / 96 (verifies the face survives downscale)
    sheet.blit(f_lbl.render("(d) scale ramp — face must survive", True,
                            (150, 210, 230)), (340, y))
    ry = y + 24
    rx = 340
    for s in (16, 24, 32, 48, 96):
        spr = build_draugr(s)
        sheet.blit(night_sky(s + 8, s + 8), (rx, ry))
        sheet.blit(spr, (rx + 4, ry + 4))
        sheet.blit(f_small.render(f"{s}px", True, (200, 210, 220)),
                   (rx, ry + s + 12))
        rx += s + 22

    # (e) pillar MIRROR pair (top cap-down + bottom cap-up) on a gap
    mx = 700
    sheet.blit(f_lbl.render("(e) pillar mirror — top / bottom + gap", True,
                            (150, 210, 230)), (mx, y))
    mpy = y + 24
    mw, mh = 110, 150
    gap = 46
    sheet.blit(night_sky(mw, mh * 2 + gap), (mx, mpy))
    pygame.draw.rect(sheet, (60, 64, 72), (mx, mpy, mw, mh * 2 + gap), 2)
    topp = build_pillar(mw - 12, mh - 6, with_cap=True)
    topp = pygame.transform.flip(topp, False, True)
    sheet.blit(topp, (mx + 6, mpy + 3))
    botp = build_pillar(mw - 12, mh - 6, with_cap=True)
    sheet.blit(botp, (mx + 6, mpy + mh + gap + 3))
    sheet.blit(f_small.render("repeatable haft tiles to any height; "
                              "crescent cap detaches at the gap edge",
                              True, (190, 205, 218)), (mx, mpy + mh * 2 + gap + 6))

    # palette swatch strip
    sw_y = sheet_h - 34
    sx = 24
    for name in ("bone", "slate", "ice", "rust", "moss", "bronze", "sheen", "ink"):
        c = PAL[name]
        pygame.draw.rect(sheet, c, (sx, sw_y, 26, 22))
        pygame.draw.rect(sheet, (80, 84, 92), (sx, sw_y, 26, 22), 1)
        sheet.blit(f_small.render(name, True, (200, 208, 218)), (sx + 30, sw_y + 4))
        sx += 30 + 8 + f_small.size(name)[0] + 14

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
