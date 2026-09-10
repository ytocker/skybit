"""CERNUN — the antlered forest stag-devil — round 2 review sheet.

Concept: Section-1 Devilish, GREEN-BAND #1 DEEP PINE. A wee Celtic Cernunnos
woodland devil — a crowned stag-skull druid ringed with antlers and torcs,
seated cross-legged on a mound, a ram-horned serpent coiling at the base.

Round 2 resolves the AD round-1 critique. The pine palette + bone/pine value
split + the top-heavy pillar fix were signed off and are kept untouched. The
fixes here all target the FACE losing the fight to the rack at 32px:

  - Muzzle widened ~18% and shortened so the face is a distinct mass BELOW the
    crown, not a continuation of the antler stalk.
  - An ink keyline + a hair-darker shade band at the brow DETACHES the rack
    from the head so the crown reads as worn-over, not grown-from.
  - Eyes gain a warm high-contrast catch (birch inner ring + torc-gold pupil
    + top-left sheen) — the scary-CUTE glint the shipped parrot uses to stay
    friendly small. They beat the pine instead of sinking into it.
  - Torc value/contrast raised to a clean gold smile-curve focal at the throat
    (kept a THIN ring — not broadened toward Pazul ochre).
  - Antlers dropped to a clean 3-tine fork per side with fatter tines so no
    branch turns to anti-alias speckle on the downscale.
  - Seated body gets a weight-shift / shoulder asymmetry + a clearer coin-pouch
    so the chibi body is weight-shifted, not a symmetric pentagon.

House grammar (inherited from the warren-clown / Big-Reapy / Pyrecrown line):
chibi proportions, FLAT saturated fills + hard ink keylines, form via the
dark-core -> flat-fill -> top-left rim-sheen TRIAD, silhouette POP via a 1px
outline grown from the alpha mask, supersample -> smoothscale.

Run headless (SDL_VIDEODRIVER=dummy). Writes round_2.png beside this script.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = "/home/user/skybit"
_HERE = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# ── PINNED PALETTE (exact hexes from the locked brief — DO NOT TOUCH hues) ───
PINE        = (54, 92, 68)     # DEEP DESATURATED PINE fur base
PINE_DK     = (32, 62, 46)     # near-black pine shade (dark-core)
BONE        = (228, 214, 180)  # birch-bone antler / skull accent
BONE_DK     = (176, 162, 128)  # birch shade (derived for antler dark-core)
BARK        = (108, 78, 48)    # bark-umber staff
BARK_DK     = (74, 52, 30)     # bark shade (derived)
TORC        = (224, 184, 84)   # torc-gold thin accent
TORC_DK     = (168, 132, 52)   # torc shade (derived)
TORC_HI     = (248, 220, 132)  # torc top-left catch (derived, raises focal value)
INK         = (26, 28, 22)     # ink keyline
SHEEN       = (150, 186, 150)  # top-left pine rim-sheen (pinned)
BONE_SHEEN  = (246, 238, 214)  # birch rim-sheen (derived, lighter than bone)
MOSS        = (96, 132, 78)    # moss tuft on staff bands (woodland green, off-pine)

SS = 4  # supersample factor


# ── triad + outline helpers (house grammar) ──────────────────────────────────
def _grow_outline(surf, col, alpha=255, width=1):
    """1px ink line grown from the alpha mask — the silhouette POP."""
    mask = pygame.mask.from_surface(surf, 40)
    line = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for comp in mask.connected_components():
        pts = comp.outline(1)
        if len(pts) >= 2:
            pygame.draw.lines(line, (*col, alpha), True, pts, width)
    out = surf.copy()
    out.blit(line, (0, 0))
    return out


def _triad_blob(target, pts, base, dark, sheen, *, core_shift=(0.10, 0.16),
                sheen_shift=(-0.12, -0.14), sheen_scale=0.5, sheen_a=200):
    """Draw a flat polygon, then a dark-core lobe shifted DOWN-RIGHT and a
    rim-sheen lobe shifted UP-LEFT — the house dark-core / fill / sheen triad."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    w = maxx - minx
    h = maxy - miny
    cx = (minx + maxx) * 0.5
    cy = (miny + maxy) * 0.5

    pygame.draw.polygon(target, base, pts)

    def _shrink(scale, sx, sy):
        return [(cx + (p[0] - cx) * scale + w * sx,
                 cy + (p[1] - cy) * scale + h * sy) for p in pts]

    core = _shrink(0.72, core_shift[0], core_shift[1])
    pygame.draw.polygon(target, dark, core)
    pygame.draw.polygon(target, base, _shrink(0.50, core_shift[0] * 1.4,
                                              core_shift[1] * 1.4))

    sh = _shrink(sheen_scale, sheen_shift[0], sheen_shift[1])
    glow = pygame.Surface(target.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(glow, (*sheen, sheen_a), sh)
    target.blit(glow, (0, 0))


# ── ANTLER builder — a CLEAN 3-tine fork per side (no fine twig speckle) ─────
def _tine(surf, root, ang, length, thick0, thick1):
    """One fat triad-lit tapered bone limb root->tip, with a rounded tip knuckle.
    Drawn as a single deliberate shape that survives the 32px downscale."""
    x0, y0 = root
    x1 = x0 + math.cos(ang) * length
    y1 = y0 + math.sin(ang) * length
    perp = ang + math.pi / 2
    quad = [
        (x0 + math.cos(perp) * thick0, y0 + math.sin(perp) * thick0),
        (x0 - math.cos(perp) * thick0, y0 - math.sin(perp) * thick0),
        (x1 - math.cos(perp) * thick1, y1 - math.sin(perp) * thick1),
        (x1 + math.cos(perp) * thick1, y1 + math.sin(perp) * thick1),
    ]
    _triad_blob(surf, quad, BONE, BONE_DK, BONE_SHEEN,
                core_shift=(0.06, 0.10), sheen_shift=(-0.12, -0.14),
                sheen_scale=0.55, sheen_a=170)
    pygame.draw.circle(surf, BONE, (int(x1), int(y1)), int(max(2 * SS, thick1)))
    pygame.draw.circle(surf, BONE_SHEEN,
                       (int(x1 - thick1 * 0.4), int(y1 - thick1 * 0.4)),
                       int(max(SS, thick1 * 0.5)))
    return (x1, y1)


def _antler(surf, root, side):
    """A deliberate 3-tine fork fanning into a tree-crown half. `side` (+1 = right,
    -1 = left) mirrors the rack. Fat beam -> brow tine + mid tine + tall crown
    tine, each a single fat shape. Tree-crown read, never a horn pair."""
    base_len = 40 * SS
    # main beam sweeps OUTWARD as it rises so the rack fans into a wide tree-crown
    # (not an inward X over the head) — the silhouette must read as a crown.
    beam_ang = math.radians(-90 - side * 46)
    j1 = _tine(surf, root, beam_ang, base_len, 7 * SS, 5 * SS)
    # tine 1 — low brow prong sweeping further outward
    _tine(surf, j1, beam_ang + side * 0.78, 30 * SS, 5 * SS, 3 * SS)
    # continue the beam up, still leaning outward
    j2 = _tine(surf, j1, beam_ang + side * 0.04, 36 * SS, 5 * SS, 4 * SS)
    # tine 2 — mid prong fanning outward
    _tine(surf, j2, beam_ang + side * 0.62, 30 * SS, 4 * SS, 3 * SS)
    # tine 3 — tall crown tip, near-vertical (the crown peak)
    _tine(surf, j2, beam_ang - side * 0.16, 34 * SS, 4 * SS, 3 * SS)


# ── THE CREATURE ──────────────────────────────────────────────────────────────
def build_cernun():
    """Full Cernun: antler rack + WIDENED stag skull-muzzle (detached from the
    rack by an ink/shade brow band) + warm-eyed face + raised gold throat-torc +
    weight-shifted seated fur body clutching a coin-pouch + ram-horned serpent."""
    W = 224 * SS
    H = 236 * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    body_cy = int(H * 0.72)
    head_cy = int(H * 0.42)
    skull_top = int(H * 0.30)

    # ── ANTLER RACK first (behind head) — clean 3-tine fork each side ─────────
    rack_root_y = skull_top + 4 * SS
    _antler(s, (cx - 14 * SS, rack_root_y), -1)
    _antler(s, (cx + 14 * SS, rack_root_y), +1)

    # ── SEATED FUR BODY (chibi, cross-legged) — weight-shifted, not a pentagon ─
    # Asymmetric: right shoulder rides higher, body leans subtly to its left so
    # the silhouette has the weight-shifted house posture.
    body = [
        (cx - 50 * SS, body_cy - 34 * SS),   # left shoulder (lower)
        (cx - 10 * SS, body_cy - 40 * SS),
        (cx + 30 * SS, body_cy - 44 * SS),   # right shoulder (raised)
        (cx + 56 * SS, body_cy - 18 * SS),
        (cx + 62 * SS, body_cy + 30 * SS),
        (cx + 40 * SS, body_cy + 48 * SS),
        (cx - 44 * SS, body_cy + 48 * SS),
        (cx - 62 * SS, body_cy + 26 * SS),
        (cx - 58 * SS, body_cy - 8 * SS),
    ]
    _triad_blob(s, body, PINE, PINE_DK, SHEEN,
                core_shift=(0.12, 0.18), sheen_shift=(-0.16, -0.18),
                sheen_scale=0.44, sheen_a=180)

    # crossed legs as two fur lobes at the front of the mound (asymmetric overlap)
    for sgn, lift in ((-1, 0), (+1, -4 * SS)):
        leg = [
            (cx + sgn * 4 * SS, body_cy + 22 * SS + lift),
            (cx + sgn * 56 * SS, body_cy + 30 * SS + lift),
            (cx + sgn * 44 * SS, body_cy + 50 * SS + lift),
            (cx - sgn * 4 * SS, body_cy + 46 * SS + lift),
        ]
        _triad_blob(s, leg, PINE, PINE_DK, SHEEN,
                    core_shift=(0.08, 0.14), sheen_shift=(-0.12, -0.12),
                    sheen_scale=0.4, sheen_a=130)

    # ── COIN-POUCH clutched in the lap — clearer round drawstring sack ───────
    pouch_cx, pouch_cy = cx - 4 * SS, body_cy + 22 * SS
    pouch = [
        (pouch_cx - 20 * SS, pouch_cy - 8 * SS),
        (pouch_cx - 12 * SS, pouch_cy - 16 * SS),
        (pouch_cx + 12 * SS, pouch_cy - 16 * SS),
        (pouch_cx + 22 * SS, pouch_cy - 6 * SS),
        (pouch_cx + 18 * SS, pouch_cy + 18 * SS),
        (pouch_cx - 18 * SS, pouch_cy + 18 * SS),
    ]
    _triad_blob(s, pouch, BARK, BARK_DK, (170, 134, 92),
                core_shift=(0.10, 0.16), sheen_shift=(-0.14, -0.14),
                sheen_scale=0.4, sheen_a=150)
    # cinched neck + a peeking gold coin (raised value so it pops in the lap)
    pygame.draw.line(s, BARK_DK, (pouch_cx - 11 * SS, pouch_cy - 14 * SS),
                     (pouch_cx + 11 * SS, pouch_cy - 14 * SS), 3 * SS)
    pygame.draw.circle(s, TORC, (pouch_cx, pouch_cy - 18 * SS), 6 * SS)
    pygame.draw.circle(s, TORC_HI, (pouch_cx - 2 * SS, pouch_cy - 20 * SS), 2 * SS)
    pygame.draw.circle(s, TORC_DK, (pouch_cx, pouch_cy - 18 * SS), 6 * SS, SS)

    # little clawed hands cupping the pouch
    for sgn in (-1, +1):
        hand = [
            (pouch_cx + sgn * 18 * SS, pouch_cy - 4 * SS),
            (pouch_cx + sgn * 30 * SS, pouch_cy + 2 * SS),
            (pouch_cx + sgn * 26 * SS, pouch_cy + 16 * SS),
            (pouch_cx + sgn * 14 * SS, pouch_cy + 10 * SS),
        ]
        _triad_blob(s, hand, PINE, PINE_DK, SHEEN,
                    core_shift=(0.08, 0.12), sheen_shift=(-0.10, -0.10),
                    sheen_scale=0.4, sheen_a=120)

    # ── THROAT TORC — thin gold ring, value RAISED to a clean smile-curve focal ─
    torc_cy = head_cy + 52 * SS
    # shade arc behind for contrast against the pine throat
    pygame.draw.arc(s, TORC_DK,
                    (cx - 30 * SS, torc_cy - 16 * SS, 60 * SS, 34 * SS),
                    math.radians(192), math.radians(348), 6 * SS)
    pygame.draw.arc(s, TORC,
                    (cx - 30 * SS, torc_cy - 18 * SS, 60 * SS, 34 * SS),
                    math.radians(196), math.radians(344), 5 * SS)
    # bright top-left catch on the smile-curve so the gold reads as a focal at 32px
    pygame.draw.arc(s, TORC_HI,
                    (cx - 30 * SS, torc_cy - 20 * SS, 60 * SS, 34 * SS),
                    math.radians(206), math.radians(286), 3 * SS)
    for sgn in (-1, +1):
        pygame.draw.circle(s, TORC, (cx + sgn * 29 * SS, torc_cy + 7 * SS), 7 * SS)
        pygame.draw.circle(s, TORC_HI,
                           (cx + sgn * 29 * SS - 2 * SS, torc_cy + 5 * SS), 3 * SS)
        pygame.draw.circle(s, TORC_DK, (cx + sgn * 29 * SS, torc_cy + 7 * SS),
                           7 * SS, SS)

    # small deer ears tucked at the skull base, behind the antler roots
    for sgn in (-1, +1):
        ear = [
            (cx + sgn * 26 * SS, head_cy - 22 * SS),
            (cx + sgn * 42 * SS, head_cy - 12 * SS),
            (cx + sgn * 30 * SS, head_cy + 2 * SS),
        ]
        _triad_blob(s, ear, PINE, PINE_DK, SHEEN,
                    core_shift=(0.06, 0.10), sheen_shift=(-0.10, -0.10),
                    sheen_scale=0.5, sheen_a=140)

    # ── STAG SKULL-MUZZLE — WIDENED ~18%, SHORTENED, a distinct mass below rack ─
    # Wider brow + cheeks, shorter nose drop. The face is now its own broad lobe,
    # not a thin pale stalk continuing the antler beam.
    skull = [
        (cx - 32 * SS, head_cy - 24 * SS),   # brow left (wider)
        (cx + 32 * SS, head_cy - 24 * SS),   # brow right (wider)
        (cx + 28 * SS, head_cy + 6 * SS),    # cheek right
        (cx + 15 * SS, head_cy + 34 * SS),   # muzzle taper right (shorter)
        (cx, head_cy + 42 * SS),             # nose tip (shorter drop)
        (cx - 15 * SS, head_cy + 34 * SS),   # muzzle taper left
        (cx - 28 * SS, head_cy + 6 * SS),    # cheek left
    ]
    _triad_blob(s, skull, BONE, BONE_DK, BONE_SHEEN,
                core_shift=(0.08, 0.12), sheen_shift=(-0.14, -0.16),
                sheen_scale=0.5, sheen_a=185)

    # ── BROW DETACH BAND — a hair-darker shade band + ink keyline where the
    # antler bases meet the skull, so the crown reads as worn-over the head, not
    # grown out of a single pale stalk. This is the headline 32px legibility fix.
    brow = [
        (cx - 33 * SS, head_cy - 24 * SS),
        (cx + 33 * SS, head_cy - 24 * SS),
        (cx + 30 * SS, head_cy - 16 * SS),
        (cx - 30 * SS, head_cy - 16 * SS),
    ]
    pygame.draw.polygon(s, BONE_DK, brow)
    pygame.draw.line(s, INK, (cx - 33 * SS, head_cy - 24 * SS),
                     (cx + 33 * SS, head_cy - 24 * SS), 2 * SS)

    # ── WARM HIGH-CONTRAST EYES — birch ring + gold pupil + sheen catch ──────
    # The scary-CUTE glint: a warm focal that beats the pine, the same trick the
    # shipped parrot uses to stay friendly at small scale.
    for sgn in (-1, +1):
        ex = cx + sgn * 15 * SS
        ey = head_cy - 1 * SS
        # ENLARGED dark socket mask — the dark surround is what lets the warm
        # gold iris survive the 32px downscale instead of bleeding into bone.
        socket = [
            (ex - sgn * 14 * SS, ey - 11 * SS),
            (ex + sgn * 13 * SS, ey - 13 * SS),
            (ex + sgn * 11 * SS, ey + 12 * SS),
            (ex - sgn * 13 * SS, ey + 10 * SS),
        ]
        pygame.draw.polygon(s, PINE_DK, socket)
        # thin warm birch inner ring framing the iris
        pygame.draw.circle(s, BONE_SHEEN, (int(ex), int(ey)), 8 * SS)
        # torc-gold iris (the warm catch) — bigger so it carries at 32px
        pygame.draw.circle(s, TORC, (int(ex), int(ey)), 6 * SS)
        pygame.draw.circle(s, TORC_HI, (int(ex), int(ey)), 6 * SS, SS)
        # dark pupil + top-left highlight glint
        pygame.draw.circle(s, INK, (int(ex), int(ey + SS)), int(3.4 * SS))
        pygame.draw.circle(s, (252, 246, 226),
                           (int(ex - 2 * SS), int(ey - 2 * SS)), int(1.8 * SS))

    # nasal cavity + nostril slits + a quiet stitched tooth-line (cute, not grim)
    pygame.draw.polygon(s, PINE_DK, [
        (cx, head_cy + 18 * SS), (cx - 5 * SS, head_cy + 28 * SS),
        (cx + 5 * SS, head_cy + 28 * SS)])
    for sgn in (-1, +1):
        pygame.draw.line(s, INK, (cx + sgn * 3 * SS, head_cy + 36 * SS),
                         (cx + sgn * 5 * SS, head_cy + 40 * SS), 2 * SS)
    pygame.draw.line(s, BONE_DK, (cx - 11 * SS, head_cy + 30 * SS),
                     (cx + 11 * SS, head_cy + 30 * SS), 2 * SS)

    # ── RAM-HORNED SERPENT coiling at the base (Cernunnos signature) ─────────
    serp_cy = body_cy + 46 * SS
    seg_x = cx + 42 * SS
    seg_y = serp_cy
    for i in range(5):
        r = (10 - i) * SS + 4 * SS
        pygame.draw.circle(s, PINE_DK, (int(seg_x), int(seg_y)), r)
        pygame.draw.circle(s, MOSS, (int(seg_x - r * 0.3), int(seg_y - r * 0.3)),
                           int(r * 0.55))
        seg_x += 11 * SS
        seg_y += (-6 * SS if i % 2 == 0 else 7 * SS)
    hx, hy = seg_x - 2 * SS, seg_y
    pygame.draw.circle(s, MOSS, (int(hx), int(hy)), 9 * SS)
    pygame.draw.circle(s, PINE_DK, (int(hx), int(hy)), 9 * SS, SS)
    for sgn in (-1, +1):
        pygame.draw.arc(s, BONE,
                        (hx - 10 * SS, hy - 14 * SS, 12 * SS, 12 * SS),
                        math.radians(20 if sgn > 0 else 100),
                        math.radians(200 if sgn > 0 else 280), 3 * SS)
    pygame.draw.circle(s, TORC, (int(hx + 3 * SS), int(hy - 1 * SS)), 2 * SS)

    return _grow_outline(s, INK, 255, max(1, SS))


# ── THE PROP -> PILLAR (antler-staff / world-branch) ─────────────────────────
def build_pillar(*, shaft_h=520, cap=True, top=True):
    """Living antler-staff mirrored into a pillar: bark-banded wooden shaft =
    repeatable body; a SINGLE compact two-tine antler crook = gap-edge cap, with
    the torc-ring hung BELOW the fork (AD top-heavy fix, kept) so mass drops to
    the gap line. Round-2 polish: torc-ring nudged smaller, moss tufts made a
    clean deliberate band marker rather than green noise."""
    W = 96 * SS
    H = shaft_h * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    shaft_w = 30 * SS

    shaft = [
        (cx - shaft_w, 0), (cx + shaft_w, 0),
        (cx + shaft_w, H), (cx - shaft_w, H),
    ]
    _triad_blob(s, shaft, BARK, BARK_DK, (168, 132, 92),
                core_shift=(0.18, 0.0), sheen_shift=(-0.30, 0.0),
                sheen_scale=0.32, sheen_a=150)

    # bark banding (repeatable) + a single clean moss tuft per band, alternating
    band_gap = 64 * SS
    y = band_gap // 2
    while y < H:
        pygame.draw.line(s, BARK_DK, (cx - shaft_w, y), (cx + shaft_w, y), 2 * SS)
        pygame.draw.line(s, (150, 120, 84), (cx - shaft_w, y - 2 * SS),
                         (cx + shaft_w, y - 2 * SS), SS)
        ms = -1 if (y // band_gap) % 2 == 0 else 1
        # one fatter, more compact moss lobe so it reads as a deliberate tuft
        moss_pts = [
            (cx + ms * shaft_w, y - 6 * SS),
            (cx + ms * (shaft_w + 16 * SS), y - 2 * SS),
            (cx + ms * (shaft_w + 12 * SS), y + 10 * SS),
            (cx + ms * shaft_w, y + 8 * SS),
        ]
        _triad_blob(s, moss_pts, MOSS, PINE_DK, SHEEN,
                    core_shift=(0.06, 0.10), sheen_shift=(-0.12, -0.12),
                    sheen_scale=0.5, sheen_a=150)
        y += band_gap

    if cap:
        crook = pygame.Surface((W, 150 * SS), pygame.SRCALPHA)
        ccx = W // 2
        stub = [
            (ccx - shaft_w, 0), (ccx + shaft_w, 0),
            (ccx + int(shaft_w * 0.7), 46 * SS),
            (ccx - int(shaft_w * 0.7), 46 * SS),
        ]
        _triad_blob(crook, stub, BARK, BARK_DK, (168, 132, 92),
                    core_shift=(0.18, 0.0), sheen_shift=(-0.30, 0.0),
                    sheen_scale=0.3, sheen_a=140)
        fork_root = (ccx, 44 * SS)
        for sgn in (-1, +1):
            tine = [
                (fork_root[0] + sgn * 6 * SS, fork_root[1]),
                (fork_root[0] + sgn * 26 * SS, fork_root[1] + 36 * SS),
                (fork_root[0] + sgn * 22 * SS, fork_root[1] + 58 * SS),
                (fork_root[0] + sgn * 10 * SS, fork_root[1] + 36 * SS),
                (fork_root[0] + sgn * 2 * SS, fork_root[1] + 6 * SS),
            ]
            _triad_blob(crook, tine, BONE, BONE_DK, BONE_SHEEN,
                        core_shift=(0.06, 0.10), sheen_shift=(-0.12, -0.14),
                        sheen_scale=0.5, sheen_a=170)
            pygame.draw.circle(crook, BONE,
                               (int(fork_root[0] + sgn * 22 * SS),
                                int(fork_root[1] + 58 * SS)), 5 * SS)
            pygame.draw.circle(crook, BONE_SHEEN,
                               (int(fork_root[0] + sgn * 20 * SS),
                                int(fork_root[1] + 56 * SS)), 2 * SS)
        # torc-ring hung BELOW the fork — nudged smaller per AD polish note
        ring_cy = fork_root[1] + 82 * SS
        pygame.draw.circle(crook, TORC_DK, (ccx, int(ring_cy)), 13 * SS, 5 * SS)
        pygame.draw.circle(crook, TORC, (ccx, int(ring_cy)), 11 * SS, 4 * SS)
        pygame.draw.circle(crook, TORC_HI, (ccx - 4 * SS, int(ring_cy - 7 * SS)),
                           3 * SS)
        pygame.draw.circle(crook, TORC_DK, (ccx, int(ring_cy - 11 * SS)), 4 * SS)
        crook = _grow_outline(crook, INK, 255, max(1, SS))

        if top:
            s.blit(crook, (0, H - crook.get_height()))
        else:
            flipped = pygame.transform.flip(crook, False, True)
            s.blit(flipped, (0, 0))

    return _grow_outline(s, INK, 255, max(1, SS)) if not cap else s


# ── render helpers ────────────────────────────────────────────────────────────
def smooth(spr, target_w):
    w, h = spr.get_size()
    sc = target_w / w
    return pygame.transform.smoothscale(spr, (round(w * sc), round(h * sc)))


def name_test(spr, px):
    """Downscale to a true ~px tall (in-world size), then NN-upscale x6 so the
    32px read is provable without smoothing-blur hiding the truth."""
    w, h = spr.get_size()
    sc = px / h
    small = pygame.transform.smoothscale(spr, (max(1, round(w * sc)), px))
    return pygame.transform.scale(small,
                                  (small.get_width() * 6, small.get_height() * 6))


# ── sky backdrops (day + night legibility) ───────────────────────────────────
def day_sky(surf, rect):
    for j in range(rect.h):
        t = j / rect.h
        col = (int(96 + 120 * (1 - t)), int(170 + 60 * (1 - t)), int(230 - 40 * t))
        pygame.draw.line(surf, col, (rect.x, rect.y + j), (rect.right, rect.y + j))


def night_sky(surf, rect):
    import random
    for j in range(rect.h):
        t = j / rect.h
        col = (int(18 + 26 * t), int(22 + 30 * t), int(46 + 40 * t))
        pygame.draw.line(surf, col, (rect.x, rect.y + j), (rect.right, rect.y + j))
    rng = random.Random(13)
    for _ in range(40):
        px = rect.x + rng.randint(0, rect.w - 1)
        py = rect.y + rng.randint(0, rect.h - 1)
        pygame.draw.circle(surf, (220, 228, 255), (px, py), rng.randint(0, 1) + 1)


# ── SHEET LAYOUT ──────────────────────────────────────────────────────────────
BG = (38, 44, 38)
PANEL = (50, 60, 50)
INKTXT = (236, 242, 226)
SUB = (176, 192, 172)
ACC = (224, 184, 84)
GOOD = (150, 210, 150)

_FONT = os.path.join(_ROOT, "game", "assets", "LiberationSans-Bold.ttf")
ftitle = pygame.font.Font(_FONT, 30)
font = pygame.font.Font(_FONT, 20)
fsmall = pygame.font.Font(_FONT, 14)
ftiny = pygame.font.Font(_FONT, 12)

SHEET_W = 1180
SHEET_H = 880
sheet = pygame.Surface((SHEET_W, SHEET_H), pygame.SRCALPHA)
sheet.fill(BG)

sheet.blit(ftitle.render("CERNUN  —  the antlered forest stag-devil   (round 2)", True, INKTXT), (24, 16))
sheet.blit(fsmall.render("Round-2 fixes: muzzle WIDENED ~18% + shortened into its own mass; ink + shade BROW BAND detaches the rack; "
                         "WARM gold-iris eyes with a sheen glint;", True, SUB), (24, 52))
sheet.blit(fsmall.render("torc value raised to a clean gold smile-curve focal; antlers dropped to a fat clean 3-tine fork (no twig speckle); "
                         "weight-shifted body + clearer coin-pouch.", True, SUB), (24, 70))
sheet.blit(fsmall.render("KEPT (AD sign-off): deep-pine palette + bone/pine value split, antler tree-crown fan, two-tine crook pillar cap "
                         "with the torc hung below the fork.", True, ACC), (24, 88))

cernun = build_cernun()
pillar_top = build_pillar(shaft_h=300, cap=True, top=True)
pillar_bot = build_pillar(shaft_h=300, cap=True, top=False)

# ── panel A: hero creature, day + night, large ──
ay = 116
pa = pygame.Rect(24, ay, 560, 380)
pygame.draw.rect(sheet, PANEL, pa, border_radius=12)
sheet.blit(font.render("(a)  the creature — large, day & night", True, INKTXT), (pa.x + 14, pa.y + 8))

for i, (kind, lbl) in enumerate((("day", "day sky"), ("night", "night sky"))):
    box = pygame.Rect(pa.x + 14 + i * 268, pa.y + 42, 254, 300)
    if kind == "day":
        day_sky(sheet, box)
    else:
        night_sky(sheet, box)
    pygame.draw.rect(sheet, INK, box, 2, border_radius=6)
    big = smooth(cernun, 230)
    clip = sheet.get_clip()
    sheet.set_clip(box)
    sheet.blit(big, (box.centerx - big.get_width() // 2,
                     box.bottom - big.get_height() - 6))
    sheet.set_clip(clip)
    cap = fsmall.render(lbl, True, SUB)
    sheet.blit(cap, (box.centerx - cap.get_width() // 2, box.bottom - 20))

# ── panel B: prop -> pillar mirror ──
pb = pygame.Rect(600, ay, 312, 380)
pygame.draw.rect(sheet, PANEL, pb, border_radius=12)
sheet.blit(font.render("(b)  prop -> PILLAR mirror", True, INKTXT), (pb.x + 14, pb.y + 8))
sheet.blit(ftiny.render("antler-staff  ·  two-tine crook caps both gap edges", True, SUB), (pb.x + 14, pb.y + 32))
mbox = pygame.Rect(pb.x + 14, pb.y + 50, 284, 292)
night_sky(sheet, mbox)
pygame.draw.rect(sheet, INK, mbox, 2, border_radius=6)
clip = sheet.get_clip()
sheet.set_clip(mbox)
pt = smooth(pillar_top, 120)
pbm = smooth(pillar_bot, 120)
gap = 70
sheet.blit(pt, (mbox.centerx - pt.get_width() // 2, mbox.top - pt.get_height()
                + (mbox.h - gap) // 2))
sheet.blit(pbm, (mbox.centerx - pbm.get_width() // 2,
                 mbox.top + (mbox.h - gap) // 2 + gap))
sheet.set_clip(clip)
pygame.draw.line(sheet, ACC, (mbox.x + 4, mbox.centery), (mbox.right - 4, mbox.centery), 1)
gl = ftiny.render("GAP", True, ACC)
sheet.blit(gl, (mbox.right - gl.get_width() - 6, mbox.centery - 14))

# ── panel C: detail zoom (face + antler triad) ──
pc = pygame.Rect(928, ay, 228, 380)
pygame.draw.rect(sheet, PANEL, pc, border_radius=12)
sheet.blit(font.render("(c)  detail", True, INKTXT), (pc.x + 14, pc.y + 8))
zbox = pygame.Rect(pc.x + 14, pc.y + 42, 200, 300)
day_sky(sheet, zbox)
pygame.draw.rect(sheet, INK, zbox, 2, border_radius=6)
clip = sheet.get_clip()
sheet.set_clip(zbox)
zoom = smooth(cernun, 320)
sheet.blit(zoom, (zbox.centerx - zoom.get_width() // 2, zbox.top - 30))
sheet.set_clip(clip)
sheet.blit(ftiny.render("wide muzzle + brow detach + warm eyes", True, SUB), (zbox.x + 6, zbox.bottom - 20))

# ── bottom strip: 32px NAME-TEST row ──
by = ay + 396
ps = pygame.Rect(24, by, SHEET_W - 48, 340)
pygame.draw.rect(sheet, PANEL, ps, border_radius=12)
sheet.blit(font.render("(d)  32px NAME-TEST  —  true in-world scale, x6 nearest-neighbour upscale", True, INKTXT), (ps.x + 14, ps.y + 8))
sheet.blit(ftiny.render("Proves the FACE now reads as its own mass below the rack (wide muzzle + brow detach + warm gold eyes) on both skies, "
                        "and the crook cap holds.", True, SUB), (ps.x + 14, ps.y + 32))

nt_creature = name_test(cernun, 32)
nt_ptop = name_test(pillar_top, 32)
nt_pbot = name_test(pillar_bot, 32)

cells = [
    ("creature  32px / day", nt_creature, "day"),
    ("creature  32px / night", nt_creature, "night"),
    ("pillar cap (top) 32px", nt_ptop, "night"),
    ("pillar cap (bot) 32px", nt_pbot, "night"),
]
cw = (ps.w - 28) // 4
for i, (lbl, spr, kind) in enumerate(cells):
    box = pygame.Rect(ps.x + 14 + i * cw, ps.y + 54, cw - 12, 250)
    if kind == "day":
        day_sky(sheet, box)
    else:
        night_sky(sheet, box)
    pygame.draw.rect(sheet, INK, box, 2, border_radius=6)
    clip = sheet.get_clip()
    sheet.set_clip(box)
    sheet.blit(spr, (box.centerx - spr.get_width() // 2,
                     box.centery - spr.get_height() // 2))
    sheet.set_clip(clip)
    cap = fsmall.render(lbl, True, GOOD)
    sheet.blit(cap, (box.centerx - cap.get_width() // 2, box.bottom + 6))

out_path = os.path.join(_HERE, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
