"""Look-dev sheet for the Skybit BOSS — "BAKE-KUJIRA" (Umibozu-versions set #3).

The bake-kujira: a colossal skeletal ghost-WHALE that drifts up from the abyss,
hunting whalers. Cuted to the Leyak-epic lineage — a vast blunt whale-skull head
trailing a hung RIB-CAGE that IS the pillar. The body reads as COOL drowned
sea-bone: a teal-grey rib-membrane mass (not warm cream bone), greyed bone ribs
arching off a ghost-spine keel, and two big SAD pale-amber lantern sockets as the
sole warm focal. Three tiny ghost-bird companions wheel near the head for charm.

House style this obeys (the elevated "epic" Leyak grammar):
  - CHIBI proportions — one oversized blunt rounded whale-skull head, NO limbs;
    the rib-cage curtain is the body/trail.
  - FLAT saturated fills + a hard 1-2px ink keyline (28,22,30). No within-shape
    gradients, no soft/feathered edges, no bevels.
  - Form via the TRIAD: dark-core ring -> flat fill -> top-left rim sheen lobe.
  - Scary-CUTE not grim: two big sad lantern-eyes, blunt gentle mouth — almost
    sweet, until you read that it's only bones.
  - Silhouette POP via a 1px ink keyline grown from the alpha mask.
  - EPIC pass: render BIG at SS=6 then smoothscale for a crisp downscale.

Palette (RE-SPECCED, skeleton-gate): COOL sea-rot teal-GREY dominant body value
(96,124,118) for rib-gaps + membrane over greyed bone (160,170,158) — cooler /
greyer than warm calaca cream so it stays off the Catrina/Mariachi/Necrarch
warm-bone lane; drowned-grey shade (118,130,124); pale sea-AMBER socket glow
(236,196,120) (two large sockets, the SOLE warm focal); ink-baleen (28,30,30).

Prop -> pillar mirror: the RIB-CAGE is the pillar. A ghost-spine KEEL down the
axis with one curved rib-PAIR per repeat = the tileable PILLAR BODY; a blunt
whale-SKULL nub (~shaft+30%) dropping one socket-orb glow = the GAP-EDGE CAP.
Naturally vertical + spine-symmetric — a clean mirror, no top-heavy cap.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python docs/skybit_devil/batch2/umibozu_versions/bake_kujira/render_bake_kujira.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── PINNED PALETTE (bake-kujira) ─────────────────────────────────────────────
# COOL drowned sea-bone. The DOMINANT value is the teal-grey membrane / rib-gap
# mass (cool), not warm cream bone — this is the skeleton-gate. Greyed bone ribs
# sit a notch brighter and still cool/grey. The only WARM in the whole creature
# is the pale sea-amber pair of eye sockets.
MEMBRANE    = (96, 124, 118)    # COOL sea-rot teal-grey — dominant body value
MEMBRANE_DK = (66, 92, 90)      # darker membrane (rib-gap depth / dark-core)
MEMBRANE_DP = (48, 70, 70)      # deepest abyss membrane (lowest value)

BONE        = (160, 170, 158)   # greyed bone — cooler/greyer than calaca cream
BONE_DK     = (118, 130, 124)   # drowned-grey bone shade (dark-core ring)
BONE_SHEEN  = (206, 214, 200)   # cool pale rim sheen (top-left lit edge)

AMBER       = (236, 196, 120)   # pale sea-amber socket glow — SOLE warm focal
AMBER_CORE  = (252, 232, 178)   # hot pupil-pip core inside the sockets
AMBER_DK    = (176, 138, 78)    # amber socket dark rim

BALEEN      = (28, 30, 30)      # ink-baleen / deepest mouth bars
INK         = (28, 22, 30)      # the house keyline
INK_NIGHT   = (176, 210, 202)   # cool sea-bone keyline for night — a lifted-value
                                # but COOL (teal-leaning) rim so the body edge
                                # survives the midnight sky without reading warm.

GHOST_BIRD  = (210, 222, 214)   # tiny ghost-bird companions — pale cool spectral


def _triad_circle(surf, cx, cy, r, col, *, sheen=True, sheen_d=30, sheen_col=None):
    """House form triad on a circle: dark-core ring -> flat fill -> top-left rim
    sheen. Sculpted volume while staying flat-shaded."""
    pygame.draw.circle(surf, _shade_c(col, -28), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.055))))
    if sheen:
        sc = sheen_col if sheen_col is not None else _shade_c(col, sheen_d)
        pygame.draw.circle(surf, sc,
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.30)))


def _add_outline(src, outline_color=(*INK, 235), width=1):
    """Grow a keyline from the alpha mask so the silhouette POPS on any sky. On
    night the keyline is a lifted cool sea-bone tone, not dark ink, AND grown
    thicker so the cool body edge survives on the dark sky by shape."""
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


# ── the pale-amber eye-socket — the SOLE warm focal ──────────────────────────

def _socket(surf, cx, cy, r, ss, *, night=False, sad=True):
    """A big SAD lantern eye-socket: a contained amber glow halo + a deep bone
    rim + a flat amber pool + a hot pupil-pip, with a heavy upper lid so the eye
    reads gentle/mournful rather than a blank skull hole. The two sockets are the
    only warm hue allowed anywhere on the creature."""
    # Keep the night halo CONTAINED — a big high-alpha bloom washes the cool cheeks
    # toward warm white (calaca cream), which the skeleton-gate forbids. A tighter,
    # punchier amber core keeps the sockets the SOLE warm focal without bleeding.
    gr = int(r * (2.1 if night else 2.0))
    gl = make_glow_surface(max(1, gr), AMBER, alpha_center=150 if night else 110,
                           falloff=2.4)
    surf.blit(gl, (int(cx - gr), int(cy - gr)), special_flags=pygame.BLEND_ADD)
    # Bone rim of the orbit (cool), then the amber socket pool, then a hot pip.
    pygame.draw.circle(surf, BONE_DK, (int(cx), int(cy)), max(2, int(r * 1.16)))
    pygame.draw.circle(surf, AMBER_DK, (int(cx), int(cy)), max(2, int(r)))
    pygame.draw.circle(surf, AMBER, (int(cx), int(cy)), max(1, int(r * 0.82)))
    pygame.draw.circle(surf, AMBER_CORE, (int(cx - r * 0.18), int(cy - r * 0.10)),
                       max(1, int(r * 0.34)))
    if sad:
        # Heavy bone upper lid bowed DOWN over the top of the socket — the sad,
        # gentle, almost-mournful beat that keeps it scary-CUTE not skull-grim.
        lid = pygame.Rect(0, 0, int(r * 2.5), int(r * 2.0))
        lid.center = (int(cx), int(cy - r * 1.18))
        pygame.draw.ellipse(surf, BONE, lid)
        pygame.draw.ellipse(surf, _shade_c(BONE, -22),
                            lid.inflate(-int(r * 0.4), -int(r * 0.4)))


# ── one curved rib-pair on the spine keel (the pillar repeat) ────────────────

def _rib_pair(surf, cx, y, span, hw, ss, *, col=BONE, night=False):
    """One symmetric pair of curved bone RIBS springing off the ghost-spine keel —
    the tileable pillar repeat. Each rib is a tapering bone C-arc: it leaves the
    keel near-horizontal, BULGES outward to the cage's widest point, then hooks
    back IN toward the axis — the containment curve that makes a rib-cage read as a
    cage, not drooping legs. The arc is held SHORT of a full half-hoop so the fine
    tip closes back ONTO the keel/membrane rather than curling off into open sea
    (no stray hook past the silhouette). The cool teal-grey membrane shows THROUGH
    the gap between the rib's belly and the spine (the dominant body value reads
    inside the cage). Drawn as a hard flat triad ribbon."""
    rib_w = span * 0.46            # how far out the cage bulges
    rib_drop = span * 0.50         # vertical span of one rib's C-arc
    for s in (-1, 1):
        # Parametric C-arc: angle sweeps 8..128deg so the rib goes out, peaks,
        # then curves back toward the axis — stopped before the tip can swing
        # below + outside the membrane, so every tip terminates ON the body.
        steps = 26
        center_pts = []
        for i in range(steps + 1):
            t = i / steps
            ang = math.radians(8 + 120 * t)
            # Pull the tip horizontally back toward the keel over the last third
            # of the sweep so it lands on the spine/membrane, not in open teal.
            pull = max(0.0, (t - 0.58) / 0.42)
            ox = cx + s * rib_w * math.sin(ang) * (1.0 - 0.88 * pull)
            # Ease the vertical drop back near the tip too, so the closing hook
            # tucks UP onto the keel instead of dangling below the silhouette.
            oy = y + rib_drop * (1.0 - math.cos(ang)) * 0.6 - rib_drop * 0.10 * (pull ** 2)
            center_pts.append((ox, oy))
        # Build a tapering ribbon along the centreline (thick at the keel root,
        # necking to a fine tip at the sternum-ward hook).
        upper, lower = [], []
        for i, (ox, oy) in enumerate(center_pts):
            t = i / steps
            w = hw * (1.0 - 0.66 * t)
            upper.append((ox, oy - w))
            lower.append((ox, oy + w))
        shape = upper + lower[::-1]
        pygame.draw.polygon(surf, _shade_c(col, -34),
                            [(int(x), int(yy)) for x, yy in shape])
        inner_u = [(x, yy + ss) for x, yy in upper]
        inner_l = [(x, yy - ss) for x, yy in lower]
        pygame.draw.polygon(surf, col,
                            [(int(x), int(yy)) for x, yy in (inner_u + inner_l[::-1])])
        # Top-left bone sheen stripe along the lit (upper) edge of the rib arc.
        sheen_pts = [(int(x), int(yy - ss * 0.6)) for x, yy in upper[::2]]
        if len(sheen_pts) >= 2:
            pygame.draw.lines(surf, BONE_SHEEN, False, sheen_pts, max(1, int(1.0 * ss)))


def _spine_keel(surf, cx, top_y, bot_y, hw, ss, *, col=BONE, night=False, n_vert=None):
    """The ghost-SPINE keel running down the axis — a continuous bone shaft with a
    stack of stubby vertebra knuckles (one per repeat) that the rib-pairs spring
    from, tapering to a blunt TAIL-STUB at the bottom so the cage terminates in a
    leviathan tail rather than a hard-cropped cage. This is the clean mirror axis
    of the whole cage. The vertebra knuckles are kept SMALL and a notch COOLER than
    bone so they read as structure, never competing with the amber socket-orb for
    the focal — the brief's hierarchy fix."""
    length = bot_y - top_y
    if n_vert is None:
        n_vert = max(3, int(length / (hw * 2.6)))
    # Continuous tapering keel shaft FIRST so rib tips that hook back to the axis
    # always land on solid bone — no rib tip floats in the void.
    keel_l, keel_r = [], []
    for i in range(33):
        t = i / 32
        vy = top_y + length * t
        kw = hw * (0.62 - 0.42 * t)            # necks toward a blunt tail-stub
        keel_l.append((cx - kw, vy))
        keel_r.append((cx + kw, vy))
    pygame.draw.polygon(surf, _shade_c(col, -34),
                        [(int(x), int(yy)) for x, yy in (keel_l + keel_r[::-1])])
    inner = [(cx - hw * (0.50 - 0.34 * (i / 32)), top_y + length * (i / 32)) for i in range(33)]
    inner_r = [(cx + hw * (0.50 - 0.34 * (i / 32)), top_y + length * (i / 32)) for i in range(33)]
    pygame.draw.polygon(surf, _shade_c(col, -10),
                        [(int(x), int(yy)) for x, yy in (inner + inner_r[::-1])])
    # Cool, small vertebra knuckles — desaturated toward the membrane so they sit
    # as structure beads, distinctly NOT bright round pips that rival the orb.
    knuckle = lerp_color(col, MEMBRANE, 0.34)
    for k in range(n_vert + 1):
        t = k / n_vert
        vy = top_y + length * t
        vr = hw * (0.78 - 0.30 * t)
        pygame.draw.circle(surf, _shade_c(knuckle, -26), (int(cx), int(vy)), max(1, int(vr)))
        pygame.draw.circle(surf, knuckle, (int(cx), int(vy)), max(1, int(vr * 0.72)))


# ── the rib-cage curtain (creature trail + pillar body) ──────────────────────

def _ribcage(surf, cx, top_y, bot_y, span, ss, *, night=False, n=None, bold=False):
    """The hung RIB-CAGE: a membrane-dark backing mass, the ghost-spine keel down
    the axis, and a stack of curved rib-PAIRS springing off it. The cool teal-grey
    membrane reads as the dominant value (the gaps + backing), with the greyed
    bone ribs arched over it. This is both the creature's trailing body and the
    band that TILES for the pillar. `bold` is the gameplay/true-scale variant:
    FEWER, THICKER, higher-contrast rib-pairs spaced further apart so the cage
    reads as a CAGE — not a comb of thin C-arcs that mush into hatching at 32px."""
    length = bot_y - top_y
    keel_hw = span * 0.085
    if n is None:
        # Bold: ~half the rib-pairs so each ribs reads bold with a deep dark gap
        # between; hero keeps the denser, more detailed cage.
        spacing = span * 0.74 if bold else span * 0.40
        n = max(2 if bold else 3, int(length / spacing))

    # Membrane backing mass filling the cage INTERIOR — a tapering teal-grey
    # column so the cage gaps read as the dominant COOL body value (not sky). It
    # sits inboard of the rib bulge so the ribs arc OVER it like a real cage.
    mem_w = span * 0.34
    mem = [(cx - mem_w * (1.0 - 0.12 * (i / 24)), top_y + length * (i / 24))
           for i in range(25)]
    mem_r = [(cx + mem_w * (1.0 - 0.12 * (i / 24)), top_y + length * (i / 24))
             for i in range(25)]
    pygame.draw.polygon(surf, MEMBRANE_DP,
                        [(int(x), int(y)) for x, y in (mem + mem_r[::-1])])
    # A flat lighter membrane core stripe down the middle (cool body value), so
    # the dominant read is unmistakably the teal-grey membrane, not the bone.
    core_w = span * 0.24
    core_l = [(cx - core_w * (1.0 - 0.12 * (i / 24)), top_y + length * (i / 24))
              for i in range(25)]
    core_r = [(cx + core_w * (1.0 - 0.12 * (i / 24)), top_y + length * (i / 24))
              for i in range(25)]
    pygame.draw.polygon(surf, MEMBRANE,
                        [(int(x), int(y)) for x, y in (core_l + core_r[::-1])])

    rib_hw = span * (0.108 if bold else 0.066)
    for k in range(n):
        # Seat each rib-pair high on its slot so its C-arc drop overlaps the next,
        # stacking into a continuous hooped cage rather than spaced-out legs.
        y = top_y + length * (k + 0.18) / n
        col = BONE if k % 2 == 0 else _shade_c(BONE, -8)
        _rib_pair(surf, cx, y, span, rib_hw, ss, col=col, night=night)

    _spine_keel(surf, cx, top_y, bot_y, keel_hw, ss, night=night)


# ── tiny ghost-bird companions (charm) ───────────────────────────────────────

def _ghost_bird(surf, cx, cy, w, ss):
    """A tiny spectral ghost-bird companion: a pale cool two-stroke gull silhouette
    (a shallow open V) with a faint glow, small enough not to clutter the 32px
    read. Pure charm — three of them wheel near the head."""
    gl = make_glow_surface(max(1, int(w * 0.9)), GHOST_BIRD, alpha_center=70,
                           falloff=2.2)
    surf.blit(gl, (int(cx - w * 0.9), int(cy - w * 0.9)), special_flags=pygame.BLEND_ADD)
    lw = max(1, int(1.6 * ss))
    # Two swept wing strokes meeting at a soft body dip.
    pygame.draw.lines(surf, GHOST_BIRD, False,
                      [(int(cx - w), int(cy - w * 0.34)),
                       (int(cx - w * 0.18), int(cy + w * 0.12)),
                       (int(cx), int(cy - w * 0.02))], lw)
    pygame.draw.lines(surf, GHOST_BIRD, False,
                      [(int(cx + w), int(cy - w * 0.34)),
                       (int(cx + w * 0.18), int(cy + w * 0.12)),
                       (int(cx), int(cy - w * 0.02))], lw)
    # A single 1px amber pin-eye ties each companion to the whale's warm focal
    # language without adding clutter (hero-only — they're absent at 32px).
    pygame.draw.circle(surf, AMBER_CORE, (int(cx), int(cy - w * 0.04)), max(1, int(0.9 * ss)))


# ── the blunt whale-skull head ───────────────────────────────────────────────

def _head(surf, cx, cy, r, ss, *, night=False, tell=False):
    """The oversized blunt whale-SKULL head: a heavy rounded cranium tapering to a
    wide blunt snout, two big SAD pale-amber lantern sockets (the sole warm
    focal), a row of ink-baleen bars for the gentle blunt mouth, and a cool bone
    rim-sheen on the pate. Looming + almost gentle — the scary-CUTE beat is the
    mournful lantern-eyes on a vast skull. `tell` bakes a bolder low-res face for
    the 32px read."""
    # NIGHT bone is pulled COOLER + lower-value (toward the membrane teal-grey),
    # NOT brightened toward warm white — otherwise the skull eye-mass reads as
    # calaca cream and steals the amber sockets' warm monopoly. Only the two amber
    # sockets stay warm at night.
    body = lerp_color(BONE, MEMBRANE, 0.46) if night else BONE
    sheen = lerp_color(BONE_SHEEN, MEMBRANE, 0.48) if night else BONE_SHEEN

    # Blunt snout/jaw mass FIRST (occluded by the cranium dome) — a wide rounded
    # muzzle dropping below the cranium so the silhouette reads "whale skull,"
    # heavy and blunt, not a ball.
    snout = pygame.Rect(0, 0, int(r * 1.92), int(r * 1.34))
    snout.center = (int(cx), int(cy + r * 0.66))
    pygame.draw.ellipse(surf, _shade_c(body, -30), snout)
    pygame.draw.ellipse(surf, body, snout.inflate(-int(r * 0.12), -int(r * 0.12)))
    # Cool membrane shadow under the brow (the orbit hollow region) so the warm
    # sockets sit in a cool seat — reinforces the cool-dominant read.
    hollow = pygame.Rect(0, 0, int(r * 1.5), int(r * 0.84))
    hollow.center = (int(cx), int(cy + r * 0.16))
    pygame.draw.ellipse(surf, MEMBRANE_DK, hollow)

    # Cranium dome triad (no sheen disc — a dedicated crescent is drawn below).
    _triad_circle(surf, cx, cy, r, body, sheen=False)

    # ONE hard rim-sheen crescent on the pate (top-left), built as a lit disc
    # minus a body-colored bite so the silhouette stays unbroken.
    s_cx, s_cy, s_r = cx - r * 0.30, cy - r * 0.40, r * 0.30
    pygame.draw.circle(surf, _shade_c(sheen, 8), (int(s_cx), int(s_cy)), max(2, int(s_r)))
    pygame.draw.circle(surf, body,
                       (int(s_cx + s_r * 0.52), int(s_cy + s_r * 0.46)),
                       max(2, int(s_r * 0.86)))

    # — Two big SAD lantern sockets — the sole warm focal, set wide and slightly
    #   tilted inward at the top so they read mournful.
    eye_dx = r * 0.46
    eye_y = cy + r * 0.10
    eye_r = r * 0.30
    for s in (-1, 1):
        _socket(surf, cx + s * eye_dx, eye_y, eye_r, ss, night=night, sad=True)

    # — Baleen mouth: a row of short ink bars hung from a blunt smile-line low on
    #   the snout (the gentle blunt mouth — never a snarl).
    mw = r * 0.78
    my = cy + r * 1.06
    smile = []
    for i in range(13):
        t = i / 12
        ax = cx - mw + 2 * mw * t
        ay = my + math.sin(t * math.pi) * r * 0.10   # gentle upward blunt bow
        smile.append((int(ax), int(ay)))
    pygame.draw.lines(surf, BALEEN, False, smile, max(2, int(1.8 * ss)))
    n_bars = 9
    for i in range(n_bars):
        t = (i + 0.5) / n_bars
        ax = cx - mw + 2 * mw * t
        ay = my + math.sin(t * math.pi) * r * 0.10
        bar_h = r * (0.10 + 0.06 * math.sin(t * math.pi))
        pygame.draw.line(surf, BALEEN, (int(ax), int(ay)),
                         (int(ax), int(ay + bar_h)), max(1, int(1.2 * ss)))

    if tell:
        # Baked low-res face tell so the 32px icon keeps a creature read: two bold
        # bright amber socket dots + a dark baleen bar.
        for s in (-1, 1):
            _socket(surf, cx + s * eye_dx, eye_y, eye_r * 1.06, ss, night=night, sad=True)
        pygame.draw.line(surf, BALEEN, (int(cx - mw * 0.7), int(my)),
                         (int(cx + mw * 0.7), int(my)), max(2, int(2.4 * ss)))


# ── the whole creature: skull head + hung rib-cage + ghost birds ─────────────

def build_bake_kujira(scale=1.0, ss=5, *, night=False, compact=False):
    """The full creature on a transparent surface: the blunt whale-skull up top,
    a hung rib-cage trailing straight beneath, three tiny ghost-birds wheeling
    near the head. EPIC pass renders BIG at SS then smoothscales. `compact` is the
    gameplay/32px variant — head grown to dominate, cage shortened, baked tell."""
    head_r = int(48 * scale) * ss
    cage_mult = 1.1 if compact else 2.5
    cage_len = int(head_r * cage_mult)
    span = head_r * (1.4 if compact else 1.6)
    side_pad = int(18 * scale) * ss
    top_pad = int(18 * scale) * ss
    bot_pad = int(18 * scale) * ss

    head_cx_off = side_pad + int(span / 2) + head_r
    head_cy = top_pad + head_r * 1.05

    cage_top_y = head_cy + head_r * 1.02
    cage_bot_y = cage_top_y + cage_len

    W = int(head_cx_off * 2)
    H = int(cage_bot_y + bot_pad)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # Cage first so the skull snout occludes its top (one continuous body).
    # The compact gameplay variant uses the BOLD (fewer/thicker) rib-cage so the
    # true-scale read stays a CAGE, not comb-mush.
    _ribcage(surf, cx, cage_top_y, cage_bot_y, span, ss, night=night, bold=compact)
    _head(surf, cx, head_cy, head_r, ss, night=night, tell=compact)

    # Three tiny ghost-bird companions wheeling near the head (skip on compact so
    # they never clutter the 32px read — the brief's hard constraint).
    if not compact:
        bw = head_r * 0.22
        for bx, by in ((cx - head_r * 1.18, head_cy - head_r * 0.62),
                       (cx + head_r * 1.30, head_cy - head_r * 0.30),
                       (cx + head_r * 0.92, head_cy - head_r * 1.05)):
            _ghost_bird(surf, bx, by, bw, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallv = pygame.transform.smoothscale(surf, (out_w, out_h))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(smallv, outline_color=oc, width=2 if night else 1)


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _skull_cap(surf, cx, cap_base_y, span, ss, *, point_up, night=False):
    """The detachable GAP-EDGE CAP: a blunt whale-SKULL nub (~shaft span +30%)
    sitting at the cage's gap end, dropping ONE socket-orb amber glow INTO the
    gap. `point_up` orients the skull so its blunt face aims at the gap. Kept
    compact so the cap is never top-heavy vs the shaft."""
    d = -1 if point_up else 1
    skull_w = span * 1.30               # ~shaft +30%
    skull_h = skull_w * 0.66
    by = cap_base_y + d * skull_h * 0.58

    body = lerp_color(BONE, MEMBRANE, 0.46) if night else BONE
    sheen = lerp_color(BONE_SHEEN, MEMBRANE, 0.48) if night else BONE_SHEEN

    # Blunt skull dome facing the gap — a flat triad ellipse.
    dome = pygame.Rect(0, 0, int(skull_w), int(skull_h * 1.6))
    dome.center = (int(cx), int(by))
    pygame.draw.ellipse(surf, _shade_c(body, -30), dome)
    pygame.draw.ellipse(surf, body, dome.inflate(-int(skull_w * 0.10), -int(skull_h * 0.10)))
    # Cool membrane orbit-hollow on the gap-facing brow so the warm orb sits cool.
    hollow = pygame.Rect(0, 0, int(skull_w * 0.6), int(skull_h * 0.5))
    hollow.center = (int(cx), int(by + d * skull_h * 0.30))
    pygame.draw.ellipse(surf, MEMBRANE_DK, hollow)
    # Hard rim sheen lobe on the gap-facing pate.
    pygame.draw.circle(surf, sheen,
                       (int(cx - skull_w * 0.16), int(by - d * skull_h * 0.30)),
                       max(2, int(skull_w * 0.15)))

    # ONE socket-orb glow dropped INTO the gap — the single warm focal of the cap.
    # Sized to be unmistakably the LARGEST + warmest round pip on the whole post so
    # the eye locks the cap as the focal and never confuses it with the small cool
    # vertebra knuckles down the keel (the brief's hierarchy fix).
    orb_y = by + d * skull_h * 0.46
    _socket(surf, cx, orb_y, skull_w * 0.20, ss, night=night, sad=False)


def _ribcage_pillar_obstacle(height, ss, *, flip, night=False):
    """One rib-cage PILLAR obstacle: the rib-cage fills the post and a blunt
    whale-skull CAP sits at the GAP-facing edge, dropping one socket-orb INTO the
    gap. `flip=True` is the TOP pillar (cap at the bottom/gap edge, skull facing
    DOWN); `flip=False` is the BOTTOM pillar (cap at the top/gap edge, skull
    facing UP). Both mirror the same rib-cage body on the spine axis — clean
    vertical, no top-heavy cap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    span = (PIPE_W - 4) * ss
    cap_band = int(50 * ss)
    if flip:
        _ribcage(surf, cx, 0, bh - cap_band, span, ss, night=night, bold=True)
        _skull_cap(surf, cx, bh - cap_band, span, ss, point_up=False, night=night)
    else:
        _ribcage(surf, cx, cap_band, bh, span, ss, night=night, bold=True)
        _skull_cap(surf, cx, cap_band, span, ss, point_up=True, night=night)
    out = pygame.transform.smoothscale(surf, (PIPE_W + 2 * OVERHANG, max(1, int(height))))
    oc = (*INK_NIGHT, 245) if night else (*INK, 235)
    return _add_outline(out, outline_color=oc, width=2 if night else 1)


# ── sheet composition ────────────────────────────────────────────────────────

def _label(surf, font, text, x, y, color=(238, 244, 244)):
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
        rng = _r.Random(99)
        for _ in range(26):
            sx = rng.randint(0, w - 1)
            sy = rng.randint(0, int(h * 0.7))
            pygame.draw.circle(s, (220, 230, 255), (sx, sy), rng.choice((1, 1, 2)))
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
    sheet.fill((50, 56, 56))
    _label(sheet, font,
            "BAKE-KUJIRA  —  Umibozu-versions #3  —  skeletal ghost-whale (cool drowned sea-bone)  —  round 2", 18, 12)
    _label(sheet, small,
            "COOL teal-grey membrane DOMINANT (96,124,118) over greyed bone (160,170,158); two big SAD pale-amber sockets = sole warm focal; rib-cage body-as-pillar on a ghost-spine keel; blunt whale-skull cap. 3 tiny ghost-birds for charm.",
            18, 32, (196, 216, 210))

    # — Cell A: BIG hero, on an abyssal sea sky.
    panel = pygame.Rect(18, 56, 320, 660)
    bgA = _sky(panel.w, panel.h, (18, 40, 50), (28, 70, 76), (54, 110, 108))
    sheet.blit(bgA, panel.topleft)
    pygame.draw.rect(sheet, (110, 150, 142), panel, 2, border_radius=8)
    hero = build_bake_kujira(scale=1.7, ss=5)
    sheet.blit(hero, (panel.centerx - hero.get_width() // 2, panel.y + 56))
    _label(sheet, font, "(a) HERO  big scale (SS=5)", panel.x + 8, panel.y + 8)
    _label(sheet, small, "blunt skull + sad lantern sockets + hung rib-cage + ghost-birds",
           panel.x + 8, panel.y + 28, (200, 226, 218))

    # — Cell B: rib-cage as a tileable PILLAR pair at TRUE obstacle scale (night),
    #   plus a 2x zoom on the cap band proving the skull lanterns the gap + mirror.
    panelB = pygame.Rect(352, 56, 330, 660)
    bg = _sky(panelB.w, panelB.h, (8, 16, 28), (12, 30, 46), (18, 52, 62), stars=True)
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (110, 150, 142), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PILLAR  @ TRUE scale  (NIGHT)", panelB.x + 8, panelB.y + 8)
    _label(sheet, small, "rib-cage tiles on spine keel + skull cap (~shaft+30%)",
           panelB.x + 8, panelB.y + 28, (200, 226, 218))

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 540
    slice_x = panelB.x + 22
    slice_y = panelB.y + 50
    gap_top = 178
    gap_h = 132
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _ribcage_pillar_obstacle(top_h, 4, flip=True, night=True)
    bot_pillar = _ribcage_pillar_obstacle(bot_h, 4, flip=False, night=True)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (180, 214, 206), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    # Draw a thin centre axis line to prove the clean spine mirror.
    axis_x = slice_x - 2 + (top_pillar.get_width() // 2)
    for yy in range(slice_y, slice_y + slice_h, 8):
        pygame.draw.line(sheet, (140, 180, 172), (axis_x, yy), (axis_x, yy + 3), 1)
    _label(sheet, small, "1x native (82px): cage", slice_x - 2, slice_y + slice_h + 6, (206, 230, 222))
    _label(sheet, small, "tiles; skull drops orb in gap", slice_x - 2, slice_y + slice_h + 22, (250, 214, 150))

    # 2x zoom of the cap band (proves the gap-cap mirror + socket-orb glow).
    cap_band = 50
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
    zbg = _sky(zw * 2, zh * 2, (8, 16, 28), (12, 28, 42), (16, 44, 56))
    sheet.blit(zbg, (zx, zy))
    pygame.draw.rect(sheet, (180, 214, 206), (zx - 1, zy - 1, zw * 2 + 2, zh * 2 + 2), 1)
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom: skull cap", zx - 2, zy - 16, (255, 255, 255))
    _label(sheet, small, "socket-orb rims the gap", zx - 2, zy + zh * 2 + 6, (250, 214, 150))

    # — Cell C: TRUE 32px gameplay chip on day + night, plus a 4x audit + grayscale.
    panelC = pygame.Rect(696, 56, 326, 660)
    pygame.draw.rect(sheet, (40, 46, 46), panelC, border_radius=8)
    pygame.draw.rect(sheet, (110, 150, 142), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) TRUE 32px gameplay chip", panelC.x + 8, panelC.y + 8)
    _label(sheet, small, "head-dominant compact / day + night sky", panelC.x + 8, panelC.y + 28,
           (200, 226, 218))

    boss_day = build_bake_kujira(scale=0.6, ss=5, compact=True)
    boss_night = build_bake_kujira(scale=0.6, ss=5, night=True, compact=True)
    day = _sky(150, 300, (70, 150, 220), (120, 190, 236), (185, 224, 248))
    night = _sky(150, 300, (8, 16, 28), (12, 30, 46), (20, 54, 66), stars=True)
    dy = panelC.y + 50
    sheet.blit(day, (panelC.x + 12, dy))
    sheet.blit(night, (panelC.x + 170, dy))
    sheet.blit(boss_day, (panelC.x + 12 + 75 - boss_day.get_width() // 2, dy + 8))
    sheet.blit(boss_night, (panelC.x + 170 + 75 - boss_night.get_width() // 2, dy + 8))
    _label(sheet, small, "DAY", panelC.x + 18, dy + 6, (16, 28, 40))
    _label(sheet, small, "NIGHT", panelC.x + 176, dy + 6, (250, 214, 150))

    gy = dy + 318
    _label(sheet, small, "TRUE 32px chip on day + night sky:", panelC.x + 12, gy - 2,
           (206, 228, 220))
    icon_src = build_bake_kujira(scale=1.0, ss=5, compact=True)
    sc32 = 32 / icon_src.get_height()
    icon32 = pygame.transform.smoothscale(
        icon_src, (max(1, int(icon_src.get_width() * sc32)), 32))

    chips = [
        (_sky(86, 86, (70, 150, 220), (120, 190, 236), (185, 224, 248)), "day"),
        (_sky(86, 86, (8, 16, 28), (12, 30, 46), (20, 54, 66), stars=True), "night"),
    ]
    sx = panelC.x + 12
    for bg_chip, lab in chips:
        chip = pygame.Rect(sx, gy + 16, 86, 86)
        sheet.blit(bg_chip, chip.topleft)
        pygame.draw.rect(sheet, (150, 178, 170), chip, 1, border_radius=4)
        sheet.blit(icon32, (chip.centerx - icon32.get_width() // 2,
                            chip.centery - icon32.get_height() // 2))
        _label(sheet, small, lab, chip.x + 4, chip.y + 2, (240, 244, 244))
        sx += 96

    blow = pygame.transform.scale(icon32, (icon32.get_width() * 4, icon32.get_height() * 4))
    bx = panelC.x + 12
    byy = gy + 118
    pygame.draw.rect(sheet, (60, 64, 64), (bx - 2, byy - 2, blow.get_width() + 4, blow.get_height() + 4),
                     border_radius=4)
    sheet.blit(blow, (bx, byy))
    _label(sheet, small, "4x blow-up of the 32px chip", bx, byy + blow.get_height() + 4,
           (206, 228, 220))

    gray = _to_gray(blow)
    gx = bx + blow.get_width() + 24
    pygame.draw.rect(sheet, (110, 114, 112), (gx - 2, byy - 2, gray.get_width() + 4, gray.get_height() + 4),
                     border_radius=4)
    sheet.blit(gray, (gx, byy))
    _label(sheet, small, "grayscale value check", gx, byy + gray.get_height() + 4, (24, 24, 24))

    _label(sheet, small,
           "STYLE: flat fills, hard 1-2px ink keyline (28,22,30), dark-core -> flat-fill -> cool bone rim-sheen triad, 1px grown outline, chibi, scary-CUTE.",
           18, SH - 40, (196, 216, 210))
    _label(sheet, small,
           "PILLAR: the rib-cage IS the shaft (rib-pairs tile on a ghost-spine keel over a COOL membrane backing); a blunt whale-skull (~shaft+30%) caps + drops ONE socket-orb in the gap. On-axis spine mirror, no top-heavy cap.",
           18, SH - 22, (196, 216, 210))

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
