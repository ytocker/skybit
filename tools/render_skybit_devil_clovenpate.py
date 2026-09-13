"""Look-dev sheet for the Skybit DEVIL boss — GROUP A take A3 "CLOVENPATE".

Big Reapy's scale read, INVERTED. Where Big Reapy is a giant head on a tiny body
(top-heavy), Clovenpate is a wee bone skull-and-ribcage torso teetering on two
ABSURDLY oversized maroon cloven hoof-legs — the set's only BOTTOM-heavy figure.
The comedy moves to the feet: a knock-kneed, one-gust-from-toppling stance on
hooves far too big for the little skull. Skull + ribs read DEATH; cloven hooves
+ goat legs read DEVIL. No big curved horns — the hooves ARE the gag (set-wide
guardrail: this concept must never grow a second ram-horn pair).

House style this obeys (the warren-clown / Big-Reapy grammar):
  - CHIBI proportions, but deliberately BOTTOM-heavy (legs ~55% of the height).
  - FLAT fills + hard 1-2px ink keylines (28,22,30). No within-shape gradients,
    no feathered edges, no bevels.
  - Form via the triad: dark-core ring -> flat fill -> top-left rim sheen.
  - Silhouette POP via a 1px keyline grown from the alpha mask (parrot recipe).
  - SUPERSAMPLE then smoothscale.

Distinct palette (NOT Brimstone's basalt, NOT Big Reapy's ash-blue): pale-bone
skull/ribs, OXBLOOD-MAROON hoof-legs, hoof-black split toes, BRASS hoof-rings,
sulphur-yellow eyes. The maroon legs are the value anchor that holds the
bottom-heavy silhouette on a warm day sky.

Prop -> pillar: a bone PITCHFORK. A femur-knuckle shaft = the tileable PILLAR
BODY; the THREE-tine fork head = the detachable gap-edge CAP (three prongs vs
Big Reapy's two — distinct cap silhouette; bone femur vs B1's iron / B8's fire).

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/render_skybit_devil_clovenpate.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── "bone & oxblood-hoof" palette (take A3) ──────────────────────────────────
BONE        = (244, 236, 214)   # skull / rib fill
BONE_DK     = (176, 166, 150)   # grey-bone dark-core + rib shadow seat
BONE_SHEEN  = (255, 250, 236)   # top-left rim sheen
TOOTH       = (250, 244, 226)
TOOTH_DK    = (150, 140, 118)

HOOF        = (150, 40, 48)     # oxblood-maroon goat-leg fill (lifted a step so
                                # the BLACK hoof reads off it instead of muddying)
HOOF_DK     = (92, 22, 30)      # leg dark-core / digitigrade-knee notch seat
HOOF_SHEEN  = (196, 78, 84)     # leg top-left rim sheen (hard flat plane)
HOOF_BLACK  = (26, 20, 24)      # the cloven hoof horn (split toe) — near-black so
                                # it is the darkest mass on both day AND night sky
HOOF_BLACK2 = (66, 54, 60)      # hoof top sheen plane (the lit horn surface)
HOOF_RIM    = (236, 224, 200)   # bone-white hoof crown rim — the hard value break
                                # that forces the black hoof to pop on any sky

BRASS       = (200, 150, 54)    # hoof-ring trim accent
BRASS_HI    = (255, 224, 150)

SULPHUR     = (236, 206, 58)    # sulphur eye dot
SULPHUR_HOT = (255, 240, 150)   # eye hot pinprick

INK         = (28, 22, 30)      # the house keyline


def _triad_circle(surf, cx, cy, r, col, *, sheen=True):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left sheen."""
    pygame.draw.circle(surf, _shade_c(col, -46), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), max(1, int(r - max(1, r * 0.07))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, 26),
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.32)))


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot `_add_outline` recipe). Returns a padded surface."""
    w, h = src.get_size()
    pad = 2
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(src, threshold=8)
    sil = mask.to_surface(setcolor=outline_color, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── the little bone skull (kept NORMAL-sized — the gag is below it) ───────────

def _skull_head(surf, cx, cy, r, ss, *, night=False):
    """A small, calm bone skull: rounded cranium with the triad, a squared chin,
    two sulphur EYE-DOTS (not big empty sockets — keeps it imp-cute, distinct from
    Big Reapy's huge round holes), a heart nose, and a tiny stitched grin. No big
    horns: a single ribbon of bone stub between the eyes is the only nod, so the
    hooves stay the silhouette payoff. `night` pushes the sulphur eye-glow so the
    spark stays lit on a dark sky instead of two dead dots."""
    _triad_circle(surf, cx, cy, r, BONE)

    # Squared chin hung under the dome so the head reads SKULL, not a ball.
    chin_top = cy + r * 0.34
    chin_bot = cy + r * 0.98
    chin = [(cx - r * 0.62, chin_top), (cx - r * 0.44, chin_bot),
            (cx + r * 0.44, chin_bot), (cx + r * 0.62, chin_top)]
    pygame.draw.polygon(surf, _shade_c(BONE, -46), [(int(x), int(y)) for x, y in chin])
    inset = [(cx - r * 0.56, chin_top + ss), (cx - r * 0.40, chin_bot - ss),
             (cx + r * 0.40, chin_bot - ss), (cx + r * 0.56, chin_top + ss)]
    pygame.draw.polygon(surf, BONE, [(int(x), int(y)) for x, y in inset])
    _triad_circle(surf, cx, cy, r, BONE, sheen=True)

    # Cheek hollows — shallow scoops so the lower face reads bone.
    for s in (-1, 1):
        hr = pygame.Rect(0, 0, int(r * 0.26), int(r * 0.30))
        hr.center = (int(cx + s * r * 0.52), int(cy + r * 0.42))
        pygame.draw.ellipse(surf, _shade_c(BONE, -30), hr)

    # Eye sockets: dark ink scoops, but small + slightly oval (imp, not skull-giant).
    eye_dx = r * 0.38
    eye_dy = -r * 0.02
    sock_r = r * 0.26
    for s in (-1, 1):
        ex, ey = cx + s * eye_dx, cy + eye_dy
        sock = pygame.Rect(0, 0, int(sock_r * 2.0), int(sock_r * 2.3))
        sock.center = (int(ex), int(ey))
        pygame.draw.ellipse(surf, INK, sock)
        pygame.draw.ellipse(surf, _shade_c(BONE, -44), sock, max(1, int(2 * ss)))
        # Sulphur eye dot — two little hellfire pinpricks, the imp's living spark.
        halo_a = 235 if night else 200
        halo_r = sock_r * (1.7 if night else 1.3)
        glow = make_glow_surface(int(halo_r), SULPHUR, alpha_center=halo_a, falloff=2.2)
        surf.blit(glow, (int(ex - halo_r - 1), int(ey - halo_r - 1)),
                  special_flags=pygame.BLEND_ADD)
        pygame.draw.circle(surf, SULPHUR, (int(ex), int(ey + sock_r * 0.18)),
                           max(2, int(sock_r * 0.5)))
        pygame.draw.circle(surf, SULPHUR_HOT, (int(ex - s * sock_r * 0.16), int(ey)),
                           max(1, int(sock_r * 0.26)))
        # Bowed-UP bone brow so the wee skull reads eager, not angry.
        pygame.draw.arc(surf, _shade_c(BONE, -30),
                        (int(ex - sock_r * 1.2), int(ey - sock_r * 1.6),
                         int(sock_r * 2.4), int(sock_r * 1.6)),
                        math.radians(20), math.radians(160), max(2, int(2 * ss)))

    # Heart-triangle nose hole.
    nose_y = cy + r * 0.42
    nose = [(cx, nose_y - r * 0.08), (cx - r * 0.10, nose_y + r * 0.12),
            (cx + r * 0.10, nose_y + r * 0.12)]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in nose])

    # Tiny stitched grin: a short dark seam with 3 cross-stitches (cute, not a
    # toothy rictus — the menace is all in the legs).
    gy = cy + r * 0.70
    gx0, gx1 = cx - r * 0.34, cx + r * 0.34
    pygame.draw.line(surf, INK, (int(gx0), int(gy)), (int(gx1), int(gy)),
                     max(2, int(2.2 * ss)))
    for t in (0.2, 0.5, 0.8):
        sx = gx0 + (gx1 - gx0) * t
        pygame.draw.line(surf, INK, (int(sx), int(gy - r * 0.10)),
                         (int(sx), int(gy + r * 0.10)), max(1, int(1.8 * ss)))

    # The only "horn" nod: a tiny upright bone ribbon-stub centred on the brow —
    # minimal by design so it never reads as a horn pair.
    nub = [(cx - r * 0.10, cy - r * 0.92), (cx, cy - r * 1.18),
           (cx + r * 0.10, cy - r * 0.92)]
    pygame.draw.polygon(surf, _shade_c(BONE, -30), [(int(x), int(y)) for x, y in nub])
    pygame.draw.polygon(surf, BONE,
                        [(int(cx - r * 0.06), int(cy - r * 0.92)),
                         (int(cx), int(cy - r * 1.10)),
                         (int(cx + r * 0.06), int(cy - r * 0.92))])


# ── the exposed bone ribcage torso (3 BOLD ribs — AD guardrail) ───────────────

def _ribcage(surf, cx, top_y, w, h, ss):
    """A small exposed-bone ribcage torso: a central sternum-spine with exactly
    THREE bold rib arcs per side (the guardrail cap so it never turns to 1x
    noise), narrowing to a little pelvis the legs hang from. Triad-shaded bone."""
    spine_x = cx
    bot_y = top_y + h
    # Spine: a chunky bone column with the triad.
    sp_w = w * 0.16
    pygame.draw.rect(surf, _shade_c(BONE, -46),
                     (int(spine_x - sp_w), int(top_y), int(sp_w * 2), int(h)),
                     border_radius=max(2, int(sp_w)))
    pygame.draw.rect(surf, BONE,
                     (int(spine_x - sp_w + ss), int(top_y + ss),
                      int(sp_w * 2 - 2 * ss), int(h - 2 * ss)),
                     border_radius=max(2, int(sp_w)))

    # Three bold rib pairs, widest at the top, sweeping down-and-in to the spine.
    rib_ys = (top_y + h * 0.16, top_y + h * 0.42, top_y + h * 0.66)
    rib_ws = (w * 0.92, w * 0.80, w * 0.60)
    for ry, rw in zip(rib_ys, rib_ws):
        for s in (-1, 1):
            # Each rib = a fat arc from the spine out and curling under.
            n = 10
            pts = []
            for i in range(n + 1):
                t = i / n
                ang = math.pi * (0.04 + 0.52 * t)            # quarter sweep down-out
                px = spine_x + s * (rw * 0.5) * math.sin(ang)
                py = ry + (h * 0.16) * (1 - math.cos(ang))
                pts.append((px, py))
            # Dark-core stroke then bone fill then a sheen tick on the upper rib.
            for col, wid in ((BONE_DK, 7 * ss), (BONE, 4.5 * ss)):
                for i in range(len(pts) - 1):
                    pygame.draw.line(surf, col,
                                     (int(pts[i][0]), int(pts[i][1])),
                                     (int(pts[i + 1][0]), int(pts[i + 1][1])),
                                     max(1, int(wid)))
                for px, py in pts[::3]:
                    pygame.draw.circle(surf, col, (int(px), int(py)),
                                       max(1, int(wid * 0.5)))
            # Top-left sheen tick near the spine end of the lit-side rib.
            if s == -1:
                pygame.draw.line(surf, BONE_SHEEN,
                                 (int(pts[1][0]), int(pts[1][1] - ss)),
                                 (int(pts[3][0]), int(pts[3][1] - ss)), max(1, int(ss)))

    # Little pelvis cradle the legs hang from.
    pel = pygame.Rect(0, 0, int(w * 0.66), int(h * 0.26))
    pel.center = (int(cx), int(bot_y - ss))
    pygame.draw.ellipse(surf, _shade_c(BONE, -46), pel)
    pygame.draw.ellipse(surf, BONE, pel.inflate(-int(2 * ss), -int(2 * ss)))


# ── tiny arms + a spaded bone tail ────────────────────────────────────────────

def _arms(surf, cx, sh_y, w, ss):
    """Two tiny bone stick-arms with knob hands held out for balance (sells the
    wobbly stance). Held LOW + close to the ribs so they never crown the skull or
    read as antennae at 1x — they drop down-and-out from the shoulder."""
    for s in (-1, 1):
        sx = cx + s * w * 0.30
        ex = cx + s * w * 0.52
        ey = sh_y + w * 0.46                          # hands hang BELOW the shoulder
        for col, wid in ((BONE_DK, 6 * ss), (BONE, 3.5 * ss)):
            pygame.draw.line(surf, col, (int(sx), int(sh_y)), (int(ex), int(ey)),
                             max(1, int(wid)))
        _triad_circle(surf, ex, ey, w * 0.15, BONE)


def _tail(surf, hip_x, hip_y, scale_len, ss):
    """A spaded bone tail that curls tight DOWN-and-out off the hip, then hooks
    back up — short and clearly hip-anchored so it never reads as a stray third
    limb at 1x. A vertebra chain ending in a little bone spade (the devil tell)."""
    pts = []
    n = 12
    for i in range(n + 1):
        t = i / n
        # A tight downward hook off the hip (anchored low), curling back up at the
        # tip — short reach so the spade clearly belongs to this hip.
        px = hip_x + scale_len * (0.12 + 0.62 * t)
        py = hip_y + scale_len * (0.55 * math.sin(t * math.pi) - 0.30 * t)
        pts.append((px, py))
    for col, wid in ((BONE_DK, 6.5 * ss), (BONE, 3.6 * ss)):
        for i in range(len(pts) - 1):
            pygame.draw.line(surf, col, (int(pts[i][0]), int(pts[i][1])),
                             (int(pts[i + 1][0]), int(pts[i + 1][1])), max(1, int(wid)))
    # Bone spade tip.
    tx, ty = pts[-1]
    spade = [(tx, ty - scale_len * 0.18), (tx + scale_len * 0.22, ty),
             (tx, ty + scale_len * 0.18), (tx - scale_len * 0.05, ty)]
    pygame.draw.polygon(surf, _shade_c(BONE, -46), [(int(x), int(y)) for x, y in spade])
    pygame.draw.polygon(surf, BONE,
                        [(int(tx + (px - tx) * 0.7), int(ty + (py - ty) * 0.7))
                         for px, py in spade])


# ── the ABSURD oversized cloven hoof-legs (the whole gag) ─────────────────────

def _hoof_leg(surf, hip_x, hip_y, foot_y, lw, ss, *, knee_out):
    """One ABSURD goat-leg ending in an enormous splayed black cloven hoof — the
    whole gag. `knee_out` (+/-1) is the outward side. The leg is articulated like a
    real beast leg so it NEVER reads as a trouser tube: a fat thigh kicks OUT to a
    hard reverse (backward) digitigrade KNEE notch, a slim cannon-bone kicks back
    IN to a narrow fetlock, then the hoof flares out WIDER than the thigh is long.
    Bone-white crown rim + wide brass break force the near-black hoof to pop on any
    sky. The hoof is deliberately the boldest, widest, darkest mass in the figure."""
    leg_h = foot_y - hip_y

    # Three hard-bent joints so the silhouette is unmistakably a beast leg.
    #   hip -> knee (kicked far OUT)  ->  fetlock (tucked hard back IN)  ->  hoof.
    knee_y = hip_y + leg_h * 0.32
    knee_x = hip_x + knee_out * lw * 2.6            # hard outward knock-knee kick
    fet_y = hip_y + leg_h * 0.58                    # fetlock higher -> taller hoof
    fet_x = hip_x + knee_out * lw * 0.30            # cannon kicks sharply back in
    hoof_cx = hip_x + knee_out * lw * 0.85          # hoof splays back outward, planted

    def _segment(ax, ay, bx, by, wa, wb):
        """A fat tapering capsule via stacked circles; dark-core pass then fill."""
        for col, dw in ((HOOF_DK, 2.6), (HOOF, 0.0)):
            steps = 18
            for i in range(steps):
                t = i / (steps - 1)
                px = ax + (bx - ax) * t
                py = ay + (by - ay) * t
                rw = (wa + (wb - wa) * t) + dw * ss
                pygame.draw.circle(surf, col, (int(px), int(py)), max(1, int(rw)))

    thigh_w0 = lw * 1.30
    thigh_w1 = lw * 0.86
    cannon_w0 = lw * 0.74
    cannon_w1 = lw * 0.50                            # the slim cannon — reads "shin bone"
    _segment(hip_x, hip_y, knee_x, knee_y, thigh_w0, thigh_w1)
    _segment(knee_x, knee_y, fet_x, fet_y, cannon_w0 * 1.05, cannon_w1)

    # Hard reverse-KNEE notch: a dark wedge poking BACKWARD off the joint so the
    # bend registers as a digitigrade hock at 1x (a recognised goat/devil tell).
    nx = knee_x + knee_out * thigh_w1 * 0.9
    knee_pts = [(knee_x, knee_y - thigh_w1 * 0.5),
                (nx, knee_y - thigh_w1 * 0.1),
                (nx, knee_y + thigh_w1 * 0.7),
                (knee_x, knee_y + thigh_w1 * 0.5)]
    pygame.draw.polygon(surf, HOOF_DK, [(int(x), int(y)) for x, y in knee_pts])

    # Top-left rim sheen as HARD FLAT planes (no soft diagonal streak) — a stubby
    # lit facet on the inner edge of each segment, matching the skull/pillar triad.
    in_s = -knee_out                                 # lit edge faces the body centre
    pygame.draw.polygon(surf, HOOF_SHEEN, [
        (int(hip_x + in_s * thigh_w0 * 0.5), int(hip_y + leg_h * 0.02)),
        (int(hip_x + in_s * thigh_w0 * 0.22), int(hip_y + leg_h * 0.04)),
        (int(knee_x + in_s * thigh_w1 * 0.2), int(knee_y - thigh_w1 * 0.2)),
        (int(knee_x + in_s * thigh_w1 * 0.5), int(knee_y - thigh_w1 * 0.2)),
    ])

    # Fetlock fur-tuft: a bold, hard-lobed ragged ring above the hoof — committed,
    # not a bulge (the goat tell). Three chunky flat lobes, no feathering.
    for k in (-1, 0, 1):
        lx = fet_x + k * lw * 0.6
        ly = fet_y + lw * 0.5 + abs(k) * lw * 0.18
        pygame.draw.circle(surf, HOOF_DK, (int(lx), int(ly)), int(lw * 0.55))
        pygame.draw.circle(surf, HOOF, (int(lx), int(ly - ss)), max(1, int(lw * 0.44)))

    # Wide brass ankle-ring — the value BREAK between maroon leg and black hoof,
    # set clear of the hoof block so it always reads as a band, not lost in black.
    ank_y = fet_y + lw * 0.95
    ring = pygame.Rect(0, 0, int(lw * 1.9), int(lw * 0.7))
    ring.center = (int(hoof_cx), int(ank_y))
    pygame.draw.ellipse(surf, _shade_c(BRASS, -50), ring)
    pygame.draw.ellipse(surf, BRASS, ring.inflate(-int(2.5 * ss), -int(2 * ss)))
    pygame.draw.circle(surf, BRASS_HI, (ring.left + int(lw * 0.45), ring.centery),
                       max(1, int(lw * 0.16)))

    # ── THE CLOVEN HOOF — the headline gag. A chunky, TALL two-toed black hoof
    # block that flares wider than the thigh, with a deep cleft so it reads as
    # two splayed toes, not a flat platform. Each toe is drawn on its own so the
    # silhouette has a real cloven notch up the front and a gap between the toes.
    hoof_top = ank_y + lw * 0.35
    hoof_bot = foot_y
    hh = hoof_bot - hoof_top
    hw = lw * 1.9                                    # outer half-width >> leg width
    inner = hw * 0.16                                # the gap each toe leaves at centre

    def _toe(side):
        """One splayed toe: tall block, narrow at the crown, flaring to a rounded
        outer base, leaving a hard cleft gap at the centre."""
        ox = hoof_cx + side * inner                  # inner edge (cleft side)
        bx = hoof_cx + side * hw                      # outer base edge (splayed)
        cx_top = hoof_cx + side * hw * 0.42           # crown sits over the ankle
        # Bone-white crown rim behind the toe for the hard value pop.
        crown = [(cx_top - side * hw * 0.34 - side * 1.5 * ss, hoof_top - 1.5 * ss),
                 (cx_top + side * hw * 0.30 + side * 1.5 * ss, hoof_top - 1.5 * ss),
                 (cx_top + side * hw * 0.30, hoof_top + hh * 0.26),
                 (cx_top - side * hw * 0.34, hoof_top + hh * 0.26)]
        pygame.draw.polygon(surf, HOOF_RIM, [(int(x), int(y)) for x, y in crown])
        # The black toe block: crown -> flares down-and-out to a wide rounded base.
        block = [(cx_top - side * hw * 0.30, hoof_top),
                 (cx_top + side * hw * 0.30, hoof_top),
                 (bx, hoof_bot - hh * 0.16),
                 (bx - side * hw * 0.10, hoof_bot),
                 (ox + side * inner * 0.4, hoof_bot),
                 (ox, hoof_bot - hh * 0.30)]
        pygame.draw.polygon(surf, HOOF_BLACK, [(int(x), int(y)) for x, y in block])
        # Rounded toe-tip so it reads as a hoof, not a wedge.
        pygame.draw.circle(surf, HOOF_BLACK,
                           (int(bx - side * hw * 0.16), int(hoof_bot - hh * 0.16)),
                           max(2, int(hh * 0.20)))
        # Hard flat sheen facet on the lit (inner-body) side of the toe.
        if side == in_s:
            pygame.draw.polygon(surf, HOOF_BLACK2,
                                [(int(cx_top - side * hw * 0.26), int(hoof_top + ss)),
                                 (int(cx_top + side * hw * 0.02), int(hoof_top + ss)),
                                 (int(ox + side * hw * 0.06), int(hoof_bot - hh * 0.34))])
        # Bone rim along the outer base edge so light catches the splayed toe.
        pygame.draw.line(surf, HOOF_RIM,
                         (int(ox + side * inner), int(hoof_bot - 1)),
                         (int(bx - side * hw * 0.10), int(hoof_bot - 1)),
                         max(1, int(1.8 * ss)))

    _toe(-1)
    _toe(+1)
    # The deep ink CLEFT between the toes — the unmistakable cloven read, cut from
    # the base most of the way up the hoof.
    pygame.draw.polygon(surf, INK,
                        [(int(hoof_cx - inner * 1.1), int(hoof_bot + 1)),
                         (int(hoof_cx + inner * 1.1), int(hoof_bot + 1)),
                         (int(hoof_cx + 1.5 * ss), int(hoof_top + hh * 0.22)),
                         (int(hoof_cx - 1.5 * ss), int(hoof_top + hh * 0.22))])


def build_clovenpate(scale=1.0, ss=3, *, night=False):
    """The full boss on its own transparent surface — deliberately BOTTOM-heavy:
    legs ~55% of the height, a small skull+ribs torso ~45% on top. Returns an
    outlined surface and its baseline (hoof) y. `night` brightens the eye sulphur
    so the imp stays lit on a dark sky."""
    H = int(280 * scale)
    W = int(160 * scale)
    pad = int(76 * scale)                            # wider pad — the splayed hooves
                                                     # now reach well past the legs
    surf = pygame.Surface(((W + pad * 2) * ss, (H + pad) * ss), pygame.SRCALPHA)
    cx = (W // 2 + pad) * ss

    # Upper ~45% = skull + ribcage; lower ~55% = the giant legs.
    torso_band = int(H * 0.45) * ss
    skull_r = torso_band * 0.30
    skull_cy = int(pad * 0.35) * ss + skull_r
    skull_cx = cx

    # Ribcage hangs just under the chin.
    rib_top = skull_cy + skull_r * 1.05
    rib_w = W * 0.50 * ss
    rib_h = torso_band - skull_r * 1.1

    # Pelvis / hip line where the big legs begin; hooves plant near the bottom pad.
    hip_y = rib_top + rib_h
    foot_y = int((pad * 0.35 + H * 0.97) * ss)

    # The bone pitchfork, braced at the figure's right. Shaft runs past the hooves;
    # the 3-tine fork rises above the skull.
    fx = cx + W * 0.52 * ss
    fhw = 7 * ss
    fork_base = skull_cy - skull_r * 1.2
    _femur_shaft(surf, fx, fork_base, foot_y + 6 * ss, fhw, ss)
    _trident_fork(surf, fx, fork_base, fhw, ss, point_up=True)

    # Tail curls tight off the right hip, low (drawn before legs so legs overlap).
    _tail(surf, cx + rib_w * 0.46, hip_y + rib_h * 0.05, W * 0.20 * ss, ss)

    # The two ABSURD legs — hips set CLOSE together (knees kick out, hooves splay
    # WIDE), so the widest mass at the floor is the pair of hooves, not the legs.
    # Slim cannon-bone width so the hooves dwarf the legs.
    lw = W * 0.105 * ss
    _hoof_leg(surf, cx - rib_w * 0.22, hip_y, foot_y, lw, ss, knee_out=-1)
    _hoof_leg(surf, cx + rib_w * 0.22, hip_y, foot_y, lw, ss, knee_out=+1)

    # Ribcage + arms + skull on top (drawn last so the torso sits over the hips).
    _ribcage(surf, skull_cx, rib_top, rib_w, rib_h, ss)
    _arms(surf, skull_cx, rib_top + rib_h * 0.18, rib_w, ss)
    _skull_head(surf, skull_cx, skull_cy, skull_r, ss, night=night)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(small), foot_y / ss


# ── the bone-pitchfork prop (and its pillar-tile components) ──────────────────

def _femur_shaft(surf, cx, top_y, bot_y, hw, ss):
    """The femur shaft = the tileable PILLAR BODY: a stack of long bone segments,
    each a fat triad-lit drum with a knobbed double-condyle JOINT between it and
    the next (the femur tell), with a dark groove ring so neighbours read
    separated through smoothscale. No fork here — the fork is the detachable cap."""
    length = bot_y - top_y
    seg_h = max(int(26 * ss), int(hw * 3.0))
    n = max(2, round(length / seg_h))
    seg_h = length / n
    for i in range(n):
        sy = top_y + i * seg_h
        cyc = sy + seg_h * 0.5
        # Dark groove gutter behind the segment.
        pygame.draw.rect(surf, INK,
                         (int(cx - hw), int(sy), int(2 * hw), int(seg_h)))
        # Femur drum: a slim triad-lit shaft barrel.
        drum = pygame.Rect(0, 0, int(1.5 * hw), int(seg_h * 0.78))
        drum.center = (int(cx), int(cyc))
        pygame.draw.rect(surf, _shade_c(BONE, -46), drum, border_radius=max(2, int(hw * 0.4)))
        pygame.draw.rect(surf, BONE, drum.inflate(-int(2 * ss), -int(2 * ss)),
                         border_radius=max(2, int(hw * 0.4)))
        # Double-condyle joint knobs at the segment ends (the femur signature).
        for jy in (sy + seg_h * 0.04, sy + seg_h * 0.96):
            for s in (-1, 1):
                pygame.draw.circle(surf, _shade_c(BONE, -46),
                                   (int(cx + s * hw * 0.7), int(jy)), int(hw * 0.62))
                pygame.draw.circle(surf, BONE,
                                   (int(cx + s * hw * 0.7), int(jy)),
                                   max(1, int(hw * 0.50)))
        # Top-left sheen tick.
        pygame.draw.circle(surf, BONE_SHEEN,
                           (int(cx - hw * 0.35), int(cyc - seg_h * 0.16)),
                           max(1, int(hw * 0.28)))


def _trident_fork(surf, cx, base_y, hw, ss, *, point_up=True):
    """The THREE-tine bone fork = the detachable PILLAR TOP CAP that rides the gap-
    edge only. Three straight tapering bone prongs (a centre prong + two outers)
    on a bone crossbar — three prongs is the distinct cap silhouette vs Big Reapy's
    two-prong cradle, and bone-femur vs B1's iron / B8's fire. `point_up` orients
    the tines away from the shaft (into the gap)."""
    d = -1 if point_up else 1
    prong_len = 46 * ss
    spread = hw * 2.2
    # Bone crossbar the three tines spring from.
    bar = pygame.Rect(0, 0, int(spread * 2.4), int(hw * 1.3))
    bar.center = (int(cx), int(base_y))
    pygame.draw.rect(surf, _shade_c(BONE, -46), bar, border_radius=max(2, int(hw * 0.5)))
    pygame.draw.rect(surf, BONE, bar.inflate(-int(2 * ss), -int(2 * ss)),
                     border_radius=max(2, int(hw * 0.5)))

    for off in (-1, 0, 1):
        tx0 = cx + off * spread
        tx1 = cx + off * spread * 1.06            # outer tines splay a touch
        ty1 = base_y + d * prong_len
        for col, wid in ((BONE_DK, 11 * ss), (BONE, 7 * ss), (BONE_SHEEN, 2.4 * ss)):
            ax = tx0 - (ss if col is BONE_SHEEN else 0)
            pygame.draw.line(surf, col, (int(ax), int(base_y)),
                             (int(tx1 - (ss if col is BONE_SHEEN else 0)), int(ty1)),
                             max(1, int(wid)))
        # Sharp ink-tipped bone point on each tine.
        pygame.draw.circle(surf, BONE_DK, (int(tx1), int(ty1)), max(2, int(4 * ss)))
        pygame.draw.circle(surf, BONE, (int(tx1), int(ty1)), max(1, int(2.6 * ss)))
        pygame.draw.circle(surf, INK, (int(tx1), int(ty1 + d * 3 * ss)), max(1, int(2 * ss)))


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _fork_pillar_obstacle(height, ss, *, flip):
    """One bone-pitchfork PILLAR obstacle: the femur shaft fills the post, the
    three-tine fork cap sits at the gap end. `flip` makes the top pillar's tines
    point DOWN into the gap; the bottom pillar's point UP — proving the prop
    mirrors top<->bottom into a clean vertical bone post with the trident
    flourishing into the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 8 * ss
    cap_band = int(58 * ss)
    _femur_shaft(surf, cx, 0, bh - cap_band, hw, ss)
    _trident_fork(surf, cx, bh - cap_band, hw, ss, point_up=False)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    out = _add_outline(out)
    if flip:
        out = pygame.transform.flip(out, False, True)
    return out


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(245, 240, 230)):
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def _sky(w, h, top, mid, bot):
    s = pygame.Surface((w, h))
    for i in range(h):
        t = i / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(top, mid, t / 0.5)
        else:
            c = lerp_color(mid, bot, (t - 0.5) / 0.5)
        pygame.draw.line(s, c, (0, i), (w, i))
    return s


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    SW, SH = 1180, 760
    sheet = pygame.Surface((SW, SH))
    sheet.fill((34, 30, 36))
    _label(sheet, font, "CLOVENPATE  —  GROUP A take A3  —  bone & oxblood-hoof  —  round 2", 18, 12)
    _label(sheet, small, "the BOTTOM-heavy hoof-imp: a wee bone skull+ribcage teetering on absurd oversized cloven hoof-legs (inverts Big Reapy's giant head)",
            18, 32, (206, 196, 200))

    # — Cell A: boss at showcase scale.
    panel = pygame.Rect(18, 56, 360, 560)
    pygame.draw.rect(sheet, (50, 46, 54), panel, border_radius=8)
    pygame.draw.rect(sheet, (96, 88, 98), panel, 2, border_radius=8)
    boss, _ = build_clovenpate(scale=1.6, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.bottom - boss.get_height() - 16))
    _label(sheet, font, "(a) BOSS  showcase scale", panel.x + 8, panel.y + 8)
    _label(sheet, small, "skull+ribs = death; GIANT splayed", panel.x + 8, panel.bottom - 40, (210, 200, 204))
    _label(sheet, small, "cloven hooves = devil; goat-leg hocks", panel.x + 8, panel.bottom - 24, (210, 200, 204))

    # — Cell B: the pitchfork as a tileable PILLAR pair at TRUE obstacle scale.
    panelB = pygame.Rect(394, 56, 360, 560)
    bg = _sky(panelB.w, panelB.h, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (96, 88, 98), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE obstacle scale", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG                  # 82px — the real obstacle width
    slice_h = 470
    slice_x = panelB.x + 26
    slice_y = panelB.y + 46
    gap_top = 168
    gap_h = 120
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _fork_pillar_obstacle(top_h, 3, flip=True)
    bot_pillar = _fork_pillar_obstacle(bot_h, 3, flip=False)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (255, 255, 255), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px wide):", slice_x - 2, slice_y + slice_h + 6, (20, 20, 30))
    _label(sheet, small, "femur joints band the shaft", slice_x - 2, slice_y + slice_h + 22, (20, 20, 30))

    # 2x zoom of the gap so the 3-tine fork + femur joints are legible.
    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    zoom_src.blit(top_pillar, (-2, -(gap_top - 70) - 2))
    zoom_src.blit(bot_pillar, (-2, gap_h + 70 - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 184
    zy = panelB.y + 70
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the gap:", zx - 4, zy - 16, (255, 255, 255))
    _label(sheet, small, "THREE bone tines (vs", zx - 4, zy + zh * 2 + 6, (20, 20, 30))
    _label(sheet, small, "Reapy's 2); top<->bottom", zx - 4, zy + zh * 2 + 22, (20, 20, 30))
    _label(sheet, small, "mirror; femur-joint banding", zx - 4, zy + zh * 2 + 38, (20, 20, 30))

    # — Cell C: 1x in-game-scale INSET on BOTH day and night skies + grayscale.
    panelC = pygame.Rect(770, 56, 392, 560)
    pygame.draw.rect(sheet, (50, 46, 54), panelC, border_radius=8)
    pygame.draw.rect(sheet, (96, 88, 98), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) 1x in-game scale  —  day / night legibility", panelC.x + 8, panelC.y + 8)

    boss1x, _ = build_clovenpate(scale=0.62, ss=3)
    boss1x_n, _ = build_clovenpate(scale=0.62, ss=3, night=True)
    day = _sky(180, 250, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 250, (5, 8, 30), (15, 25, 70), (35, 55, 115))
    for sx, sy in ((24, 40), (150, 26), (96, 70), (40, 120), (160, 150), (70, 200)):
        pygame.draw.circle(night, (220, 230, 255), (sx, sy), 1)

    dy = panelC.y + 40
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2,
                        dy + 250 - boss1x.get_height() - 6))
    sheet.blit(boss1x_n, (panelC.x + 200 + 90 - boss1x_n.get_width() // 2,
                          dy + 250 - boss1x_n.get_height() - 6))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 20, 30))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (210, 220, 255))

    # — Grayscale silhouette check: bottom-heavy read must survive without colour.
    gy = dy + 270
    gray = pygame.Surface((boss1x.get_width(), boss1x.get_height()), pygame.SRCALPHA)
    gray.blit(boss1x, (0, 0))
    arr = pygame.surfarray.pixels3d(gray)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    gpanel = pygame.Rect(panelC.x + 14, gy, 360, 230)
    pygame.draw.rect(sheet, (120, 120, 124), gpanel, border_radius=6)
    sheet.blit(gray, (gpanel.centerx - gray.get_width() // 2,
                      gpanel.bottom - gray.get_height() - 8))
    _label(sheet, small, "grayscale: the two WIDEST/DARKEST masses at the floor are the HOOVES",
            gpanel.x + 6, gpanel.y + 6, (30, 30, 30))

    # — Footer captions.
    _label(sheet, small,
           "scary-cute: knock-kneed wobble on hooves too big for the wee skull; balance-arms out; sulphur eye-dots; stitched grin.",
           18, SH - 124, (210, 202, 206))
    _label(sheet, small,
           "house style: FLAT fills, hard ink keyline grown from the alpha mask, dark-core->fill->top-left-sheen triad, ss=3 -> smoothscale.",
           18, SH - 104, (210, 202, 206))
    _label(sheet, small,
           "set guardrails: NO second ram-horn pair (hooves are the gag); 3 bold ribs max; bone 3-tine fork distinct from Reapy's 2-prong cap.",
           18, SH - 84, (210, 202, 206))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "reapy_devil", "clovenpate")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
