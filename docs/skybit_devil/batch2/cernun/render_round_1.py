"""CERNUN — the antlered forest stag-devil — round 1 review sheet.

Concept: Section-1 Devilish, GREEN-BAND #1 DEEP PINE. A wee Celtic Cernunnos
woodland devil — a crowned stag-skull druid ringed with antlers and torcs,
seated cross-legged on a mound, a ram-horned serpent coiling at the base.

House grammar (inherited from the warren-clown / Big-Reapy / Pyrecrown line):
chibi proportions, FLAT saturated fills + hard ink keylines, form via the
dark-core -> flat-fill -> top-left rim-sheen TRIAD, silhouette POP via a 1px
outline grown from the alpha mask, supersample -> smoothscale. The creature is
drawn at a large supersample then downscaled; a 32px name-test proves the read.

Top-heavy ANTLER-STAFF fix (AD-pinned): the prop->pillar CAP is a SINGLE compact
two-tine crook tucked tight to the shaft axis, with the torc-ring hung BELOW the
fork so the visual mass drops toward the gap line — a slim branch-finial, NOT a
second antler head.

Run headless (SDL_VIDEODRIVER=dummy). Writes round_1.png beside this script.
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

# ── PINNED PALETTE (exact hexes from the locked brief) ───────────────────────
PINE        = (54, 92, 68)     # DEEP DESATURATED PINE fur base
PINE_DK     = (32, 62, 46)     # near-black pine shade (dark-core)
BONE        = (228, 214, 180)  # birch-bone antler / skull accent
BONE_DK     = (176, 162, 128)  # birch shade (derived for antler dark-core)
BARK        = (108, 78, 48)    # bark-umber staff
BARK_DK     = (74, 52, 30)     # bark shade (derived)
TORC        = (224, 184, 84)   # torc-gold thin accent
TORC_DK     = (168, 132, 52)   # torc shade (derived)
INK         = (26, 28, 22)     # ink keyline
SHEEN       = (150, 186, 150)  # top-left pine rim-sheen
BONE_SHEEN  = (246, 238, 214)  # birch rim-sheen (derived, lighter than bone)
MOSS        = (96, 132, 78)    # moss tuft on staff bands (woodland green, off-pine)
EYE_GLOW    = (138, 196, 140)  # hollow socket inner-glow (cool, faint)

SS = 4  # supersample factor


# ── triad + outline helpers (house grammar) ──────────────────────────────────
def _amask(surf):
    """Alpha-only copy of a surface, for clamping overlays to the silhouette."""
    m = surf.copy()
    m.fill((255, 255, 255, 0))
    m.blit(surf, (0, 0))
    a = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    a.blit(surf, (0, 0))
    return a


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

    # dark-core: a shrunken copy of the hull, pushed down-right (recedes from light)
    def _shrink(scale, sx, sy):
        return [(cx + (p[0] - cx) * scale + w * sx,
                 cy + (p[1] - cy) * scale + h * sy) for p in pts]

    core = _shrink(0.72, core_shift[0], core_shift[1])
    pygame.draw.polygon(target, dark, core)
    # re-lay a thin base ring so the fill stays the hero value, core is just a lobe
    pygame.draw.polygon(target, base, _shrink(0.50, core_shift[0] * 1.4,
                                              core_shift[1] * 1.4))

    # rim-sheen: small bright lobe up-left
    sh = _shrink(sheen_scale, sheen_shift[0], sheen_shift[1])
    glow = pygame.Surface(target.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(glow, (*sheen, sheen_a), sh)
    target.blit(glow, (0, 0))


# ── ANTLER builder — a branching fork of tines (tree-crown read) ─────────────
def _antler(surf, root, ang, length, tines, side, depth=0):
    """Recursively grown bone antler: a thick beam that forks into tines. Each
    segment is a triad-lit tapered limb so the rack reads as branching bone, not
    a flat horn pair. `side` (+1/-1) biases forks outward to fan the crown wide."""
    if depth > 3 or length < 14 * SS:
        return
    x0, y0 = root
    x1 = x0 + math.cos(ang) * length
    y1 = y0 + math.sin(ang) * length
    thick = max(3 * SS, int(length * 0.16))

    # tapered limb as a quad, triad-lit
    perp = ang + math.pi / 2
    t0 = thick
    t1 = max(2 * SS, int(thick * 0.6))
    quad = [
        (x0 + math.cos(perp) * t0, y0 + math.sin(perp) * t0),
        (x0 - math.cos(perp) * t0, y0 - math.sin(perp) * t0),
        (x1 - math.cos(perp) * t1, y1 - math.sin(perp) * t1),
        (x1 + math.cos(perp) * t1, y1 + math.sin(perp) * t1),
    ]
    _triad_blob(surf, quad, BONE, BONE_DK, BONE_SHEEN,
                core_shift=(0.06, 0.10), sheen_shift=(-0.10, -0.12),
                sheen_scale=0.55, sheen_a=150)
    # rounded knuckle at the joint so forks read organic
    pygame.draw.circle(surf, BONE, (int(x1), int(y1)), int(t1))

    # branch: a forward continuation + an outward tine
    grow = ang - 0.34 * side                      # main beam curls slightly up/out
    fork = ang - 0.92 * side                       # outward tine fans wide
    _antler(surf, (x1, y1), grow, length * 0.74, tines, side, depth + 1)
    if depth < 3:
        _antler(surf, (x1, y1), fork, length * 0.60, tines, side, depth + 1)
    # a small inner upward pricket on the lower joints (3-tine fork read)
    if depth == 1:
        _antler(surf, (x1, y1), ang + 0.55 * side, length * 0.42, tines, side,
                depth + 2)


# ── THE CREATURE ──────────────────────────────────────────────────────────────
def build_cernun():
    """Full Cernun: antler rack + stag skull-muzzle + throat torc + seated fur
    body clutching a coin-pouch + ram-horned serpent at the base. Built large
    (supersampled) then returned at SS resolution; caller downscales."""
    W = 220 * SS
    H = 232 * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    # anchors (in supersampled px)
    body_cy = int(H * 0.70)
    head_cy = int(H * 0.40)
    skull_top = int(H * 0.28)

    # ── ANTLER RACK first (drawn behind head) — big branching fork each side ──
    rack_root_y = skull_top + 6 * SS
    base_len = 56 * SS
    # two main beams sweeping up-and-out from the brow, fanning into a tree-crown
    _antler(s, (cx - 8 * SS, rack_root_y), math.radians(-118), base_len, 3, +1)
    _antler(s, (cx + 8 * SS, rack_root_y), math.radians(-62), base_len, 3, -1)

    # ── SEATED FUR BODY (chibi, cross-legged, weight low and wide) ───────────
    body = [
        (cx - 48 * SS, body_cy - 30 * SS),
        (cx + 48 * SS, body_cy - 30 * SS),
        (cx + 60 * SS, body_cy + 30 * SS),
        (cx + 40 * SS, body_cy + 46 * SS),
        (cx - 40 * SS, body_cy + 46 * SS),
        (cx - 60 * SS, body_cy + 30 * SS),
    ]
    _triad_blob(s, body, PINE, PINE_DK, SHEEN,
                core_shift=(0.10, 0.18), sheen_shift=(-0.14, -0.16),
                sheen_scale=0.46, sheen_a=170)

    # crossed legs as two fur lobes at the front of the mound
    for sgn in (-1, +1):
        leg = [
            (cx + sgn * 6 * SS, body_cy + 22 * SS),
            (cx + sgn * 54 * SS, body_cy + 30 * SS),
            (cx + sgn * 44 * SS, body_cy + 48 * SS),
            (cx + sgn * 2 * SS, body_cy + 44 * SS),
        ]
        _triad_blob(s, leg, PINE, PINE_DK, SHEEN,
                    core_shift=(0.08, 0.14), sheen_shift=(-0.10, -0.12),
                    sheen_scale=0.4, sheen_a=120)

    # little clawed hands clutching a coin-pouch in the lap
    pouch_cx, pouch_cy = cx, body_cy + 18 * SS
    pygame.draw.ellipse(s, BARK_DK,
                        (pouch_cx - 18 * SS, pouch_cy - 14 * SS,
                         36 * SS, 30 * SS))
    pygame.draw.ellipse(s, BARK,
                        (pouch_cx - 16 * SS, pouch_cy - 14 * SS,
                         30 * SS, 24 * SS))
    # pouch drawstring + a peeking gold coin
    pygame.draw.line(s, TORC_DK, (pouch_cx - 8 * SS, pouch_cy - 12 * SS),
                     (pouch_cx + 8 * SS, pouch_cy - 12 * SS), 2 * SS)
    pygame.draw.circle(s, TORC, (pouch_cx, pouch_cy - 16 * SS), 5 * SS)
    pygame.draw.circle(s, TORC_DK, (pouch_cx, pouch_cy - 16 * SS), 5 * SS, SS)
    for sgn in (-1, +1):
        hand = [
            (pouch_cx + sgn * 14 * SS, pouch_cy - 6 * SS),
            (pouch_cx + sgn * 26 * SS, pouch_cy - 2 * SS),
            (pouch_cx + sgn * 24 * SS, pouch_cy + 12 * SS),
            (pouch_cx + sgn * 12 * SS, pouch_cy + 8 * SS),
        ]
        _triad_blob(s, hand, PINE, PINE_DK, SHEEN,
                    core_shift=(0.08, 0.12), sheen_shift=(-0.10, -0.10),
                    sheen_scale=0.4, sheen_a=110)

    # ── THROAT TORC — a thin gold ring (small accent only, kept off the body) ─
    torc_cy = head_cy + 50 * SS
    pygame.draw.arc(s, TORC_DK,
                    (cx - 30 * SS, torc_cy - 16 * SS, 60 * SS, 34 * SS),
                    math.radians(196), math.radians(344), 5 * SS)
    pygame.draw.arc(s, TORC,
                    (cx - 30 * SS, torc_cy - 18 * SS, 60 * SS, 34 * SS),
                    math.radians(200), math.radians(340), 4 * SS)
    # two terminal balls of the Celtic torc
    for sgn in (-1, +1):
        pygame.draw.circle(s, TORC, (cx + sgn * 28 * SS, torc_cy + 8 * SS), 6 * SS)
        pygame.draw.circle(s, TORC_DK, (cx + sgn * 28 * SS, torc_cy + 8 * SS),
                           6 * SS, SS)

    # ── STAG SKULL-MUZZLE — long, narrow, birch-bone, triad-lit ──────────────
    skull = [
        (cx - 26 * SS, head_cy - 26 * SS),   # brow left
        (cx + 26 * SS, head_cy - 26 * SS),   # brow right
        (cx + 22 * SS, head_cy + 2 * SS),    # cheek right
        (cx + 12 * SS, head_cy + 40 * SS),   # muzzle taper right
        (cx, head_cy + 52 * SS),             # nose tip
        (cx - 12 * SS, head_cy + 40 * SS),   # muzzle taper left
        (cx - 22 * SS, head_cy + 2 * SS),    # cheek left
    ]
    _triad_blob(s, skull, BONE, BONE_DK, BONE_SHEEN,
                core_shift=(0.08, 0.14), sheen_shift=(-0.12, -0.14),
                sheen_scale=0.5, sheen_a=170)

    # hollow eye-sockets — angled, with a faint cool inner glow (scary-cute)
    for sgn in (-1, +1):
        ex = cx + sgn * 13 * SS
        ey = head_cy - 4 * SS
        socket = [
            (ex - sgn * 9 * SS, ey - 7 * SS),
            (ex + sgn * 9 * SS, ey - 9 * SS),
            (ex + sgn * 7 * SS, ey + 9 * SS),
            (ex - sgn * 8 * SS, ey + 7 * SS),
        ]
        pygame.draw.polygon(s, PINE_DK, socket)
        pygame.draw.circle(s, EYE_GLOW, (int(ex), int(ey + 1 * SS)), 4 * SS)
        pygame.draw.circle(s, INK, (int(ex), int(ey + 1 * SS)), 2 * SS)

    # nasal cavity + nostril slits + a quiet stitched tooth-line (cute, not grim)
    pygame.draw.polygon(s, PINE_DK, [
        (cx, head_cy + 22 * SS), (cx - 5 * SS, head_cy + 34 * SS),
        (cx + 5 * SS, head_cy + 34 * SS)])
    for sgn in (-1, +1):
        pygame.draw.line(s, INK, (cx + sgn * 3 * SS, head_cy + 44 * SS),
                         (cx + sgn * 5 * SS, head_cy + 49 * SS), 2 * SS)
    pygame.draw.line(s, BONE_DK, (cx - 9 * SS, head_cy + 36 * SS),
                     (cx + 9 * SS, head_cy + 36 * SS), 2 * SS)

    # small deer ears tucked at the skull base, behind the antler roots
    for sgn in (-1, +1):
        ear = [
            (cx + sgn * 24 * SS, head_cy - 18 * SS),
            (cx + sgn * 40 * SS, head_cy - 10 * SS),
            (cx + sgn * 30 * SS, head_cy + 4 * SS),
        ]
        _triad_blob(s, ear, PINE, PINE_DK, SHEEN,
                    core_shift=(0.06, 0.10), sheen_shift=(-0.10, -0.10),
                    sheen_scale=0.5, sheen_a=140)

    # ── RAM-HORNED SERPENT coiling at the base (Cernunnos signature) ─────────
    serp_cy = body_cy + 44 * SS
    # a low S-coil of green segments emerging from the right of the mound
    seg_x = cx + 40 * SS
    seg_y = serp_cy
    for i in range(5):
        r = (10 - i) * SS + 4 * SS
        pygame.draw.circle(s, PINE_DK, (int(seg_x), int(seg_y)), r)
        pygame.draw.circle(s, MOSS, (int(seg_x - r * 0.3), int(seg_y - r * 0.3)),
                           int(r * 0.55))
        seg_x += 11 * SS
        seg_y += (-6 * SS if i % 2 == 0 else 7 * SS)
    # serpent head with two little ram-horn curls
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
    the torc-ring hung BELOW the fork (AD top-heavy fix) so mass drops to the gap
    line — a slim branch-finial, not a second antler head. `top` flips the cap so
    the top pillar's crook hangs DOWN into the gap and the bottom's points UP."""
    W = 96 * SS
    H = shaft_h * SS
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    shaft_w = 30 * SS

    # ── repeatable bark shaft ────────────────────────────────────────────────
    shaft = [
        (cx - shaft_w, 0), (cx + shaft_w, 0),
        (cx + shaft_w, H), (cx - shaft_w, H),
    ]
    _triad_blob(s, shaft, BARK, BARK_DK, (168, 132, 92),
                core_shift=(0.18, 0.0), sheen_shift=(-0.30, 0.0),
                sheen_scale=0.32, sheen_a=150)

    # bark banding (repeatable) + moss tufts marking the bands
    band_gap = 64 * SS
    y = band_gap // 2
    while y < H:
        pygame.draw.line(s, BARK_DK, (cx - shaft_w, y), (cx + shaft_w, y), 2 * SS)
        pygame.draw.line(s, (150, 120, 84), (cx - shaft_w, y - 2 * SS),
                         (cx + shaft_w, y - 2 * SS), SS)
        # moss tuft on alternating sides of the band
        ms = -1 if (y // band_gap) % 2 == 0 else 1
        moss_pts = [
            (cx + ms * shaft_w, y - 4 * SS),
            (cx + ms * (shaft_w + 12 * SS), y - 2 * SS),
            (cx + ms * (shaft_w + 8 * SS), y + 8 * SS),
            (cx + ms * shaft_w, y + 6 * SS),
        ]
        _triad_blob(s, moss_pts, MOSS, PINE_DK, SHEEN,
                    core_shift=(0.06, 0.10), sheen_shift=(-0.10, -0.10),
                    sheen_scale=0.5, sheen_a=130)
        y += band_gap

    if cap:
        # gap-edge cap zone is the END nearest the gap. For the TOP pillar the
        # crook hangs DOWN (gap is at bottom, y=H); for the BOTTOM pillar it
        # points UP (gap at top, y=0). We build the crook pointing toward +y
        # then flip for the top.
        crook = pygame.Surface((W, 150 * SS), pygame.SRCALPHA)
        ccx = W // 2
        base_y = 8 * SS
        # short stub continuing the shaft into the fork
        stub = [
            (ccx - shaft_w, 0), (ccx + shaft_w, 0),
            (ccx + int(shaft_w * 0.7), 46 * SS),
            (ccx - int(shaft_w * 0.7), 46 * SS),
        ]
        _triad_blob(crook, stub, BARK, BARK_DK, (168, 132, 92),
                    core_shift=(0.18, 0.0), sheen_shift=(-0.30, 0.0),
                    sheen_scale=0.3, sheen_a=140)
        # SINGLE compact two-tine antler crook, tight to the axis (narrow fan)
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
                        core_shift=(0.06, 0.10), sheen_shift=(-0.10, -0.12),
                        sheen_scale=0.5, sheen_a=150)
            # tip knuckle
            pygame.draw.circle(crook, BONE,
                               (int(fork_root[0] + sgn * 22 * SS),
                                int(fork_root[1] + 58 * SS)), 5 * SS)
        # torc-ring hung BELOW the fork (drops the visual mass toward the gap)
        ring_cy = fork_root[1] + 86 * SS
        pygame.draw.circle(crook, TORC_DK, (ccx, int(ring_cy)), 16 * SS, 5 * SS)
        pygame.draw.circle(crook, TORC, (ccx, int(ring_cy)), 14 * SS, 4 * SS)
        pygame.draw.circle(crook, TORC_DK, (ccx, int(ring_cy - 14 * SS)), 4 * SS)
        crook = _grow_outline(crook, INK, 255, max(1, SS))

        if top:
            # top pillar: cap at the BOTTOM edge, crook hanging DOWN into the gap
            s.blit(crook, (0, H - crook.get_height()))
        else:
            # bottom pillar: cap at the TOP edge, crook pointing UP into the gap
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

# header
sheet.blit(ftitle.render("CERNUN  —  the antlered forest stag-devil   (round 1)", True, INKTXT), (24, 16))
sheet.blit(fsmall.render("Section 1 Devilish  ·  GREEN-BAND #1: DEEP PINE.  Crowned stag-skull druid, branching antler "
                         "rack (tree-crown read), gold throat-torc, seated fur body clutching a coin-pouch,", True, SUB), (24, 52))
sheet.blit(fsmall.render("ram-horned serpent at the base.  Palette: DEEP DESATURATED PINE fur (54,92,68) + birch-bone "
                         "antler (228,214,180) + bark-umber staff + thin torc-gold.", True, SUB), (24, 70))
sheet.blit(fsmall.render("Prop->pillar antler-staff top-heavy FIX applied: cap = SINGLE compact two-tine crook on-axis, "
                         "torc-ring hung BELOW the fork.", True, ACC), (24, 88))

# build assets once
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

# ── panel B: prop -> pillar mirror (the headline payoff) ──
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
# gap-line marker
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
sheet.blit(ftiny.render("skull-muzzle + rack triad", True, SUB), (zbox.x + 6, zbox.bottom - 20))

# ── bottom strip: 32px NAME-TEST row (creature + both pillars, day & night) ──
by = ay + 396
ps = pygame.Rect(24, by, SHEET_W - 48, 340)
pygame.draw.rect(sheet, PANEL, ps, border_radius=12)
sheet.blit(font.render("(d)  32px NAME-TEST  —  true in-world scale, x6 nearest-neighbour upscale", True, INKTXT), (ps.x + 14, ps.y + 8))
sheet.blit(ftiny.render("Proves the deep-pine read, antler tree-crown silhouette, and slim two-tine crook cap hold at 32px on both skies.", True, SUB), (ps.x + 14, ps.y + 32))

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

out_path = os.path.join(_HERE, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
