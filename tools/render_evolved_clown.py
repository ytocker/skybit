"""Look-dev: the EVOLVED (late-game, boss-tier) Plum & Lime warren clown.

The early-game warren clown (`JESTERS[-1]` in render_jester_variants — plum
costume, lime trim, gold ruff, four-point belled cap, happy-but-mean grin) is
LOCKED. This sheet explores a LATE-game evolution of the SAME character that
turns up near the finish line: physically larger, meaner, nastier — a boss
escalation, not a new IP. The plum/lime/gold family is pushed sinister (bruised
deep plum, sickly venom-lime, tarnished desaturated gold, blood/bruise accents)
and each of the five concepts gets its OWN menacing silhouette, cap
architecture, costume cut, ruff shape, face menace and looming stance.

Reference shape-language (web): Harlequin's literal demonic ancestry —
Hellequin / Alichino, the Dante's-Inferno demon that drove souls to Hell — so a
"darker, meaner" Plum & Lime is a return to the character's own roots, not an
invented monster. Menace cues pulled from evil-jester / carrion-clown / chasm-
demon design: hunched and elongated vs. hulking and top-heavy, oversized clawed
hands, jagged/horned cap silhouettes, dead pinprick or sunken eyes, exposed
fangs, tattered dagged hems, and bells that read as a threat rather than play.

ROUND 2 (art-director ITERATE): lead with the two strongest directions
(Hulking Brute, Carrion Coxcomb); make every concept visibly BIGGER + broader
than the hero; darken the palette into genuine bruise/venom/tarnish; rebuild
every face around hard high-contrast macro shapes (sunken brow band, one bright
eye-glint, hard maw) so menace reads at gameplay scale; keep every cap a MUTATED
3-point jester cap; give hands clear separated claws + rim-light; cut the round-1
Gaunt Stalker (read too small) for a low COILED stalker that still reads big.

Clown-ONLY (no staff — that is a separate later cycle). Cell 0 is the CURRENT
clown for direct comparison, drawn at its native scale so it reads SMALL beside
the boss masses; cells 1-5 are the five evolved concepts, all on ONE matched
ground line. Crispness: each figure is rendered DIRECTLY at K× the logical tile
size (all geometry multiplied by `K`) and blitted 1:1 — no smoothscale upscale,
so edges + eye-glints stay sharp.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_evolved_clown.py
    # -> docs/evolved_clown/round_2.png
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from tools.render_clown_dice import _shade
from tools.render_jester_variants import (
    build_jester, cap_four_point, _bell,
)


# ── the evolved Plum & Lime palette family ───────────────────────────────────
# The original hero spec (kept verbatim for the ORIGINAL reference cell).
ORIG = dict(
    dark=(96, 44, 150), light=(132, 218, 116), gold=(250, 205, 72),
    cap_fn=cap_four_point, motif="quartered", collar="scalloped",
    variant="browcock", collar_in_gold=True,
)

# The SAME three hues pushed sinister, but ROUND-2 darker: round 1 sat almost
# on the hero's bright plum/lime, so the evolution didn't read. The plum is now
# a bruised NEAR-BLACK violet; the lime is dragged down + grey into a true
# "venom" green-gray (not the candy lime); the gold is tarnished hard toward a
# green-gray brass (less yellow). "Same colours, gone rotten." Per-concept
# blood / bruise / bone accents layer on top at eyes, knuckles + cap tips.
E_PLUM = (40, 16, 64)            # bruised near-black violet (was 58,24,92)
E_PLUM_DK = (22, 9, 38)          # deepest plum, near-black core
E_LIME = (118, 150, 54)          # venom green-gray (desaturated + dirtied)
E_LIME_DK = (60, 84, 26)
E_GOLD = (150, 132, 72)          # tarnished green-gray brass (less yellow)
E_GOLD_DK = (92, 78, 40)
BLOOD = (140, 22, 32)            # blood/wound accent
BRUISE = (66, 30, 96)            # bruise-violet accent
BONE = (220, 210, 184)           # tarnished bone/ivory for fangs + claws
SKIN_PALE = (150, 138, 142)      # bruised ashen greasepaint (darkened hard so
                                 # "meaner" reads before any feature resolves)
SKIN_DK = (92, 78, 88)           # the shadowed lower-face / sunken-brow tone
DEAD_EYE = (210, 36, 48)         # the marotte's blood-pinprick dead eye
SICK_EYE = (190, 228, 86)        # sickly luminous venom eye-glint (pops at 1x)
CLAW = (210, 206, 200)           # bone-grey glove so digits read as claws


# Crispness: round 1 drew figures at native px then smoothscaled UP, so every
# edge was a blurry upscale. Now we render the figure tile at K× the logical
# size with ALL geometry multiplied by K, then blit 1:1 (no upscale). `s()`
# scales a scalar, `sw()` scales a line/outline width with a floor of 1 so thin
# strokes never vanish.
K = 2


def s(v):
    return int(round(v * K))


def sw(v):
    return max(1, int(round(v * K)))


# ── shared evolved-menace primitives ─────────────────────────────────────────
# These build BIGGER, nastier figures from scratch (the hero `build_jester` is
# tuned for the small happy presenter). Each concept composes them into its own
# silhouette so no two share a body.

def _claw_hand(surf, wrist, reach, w, glove, *, fingers=4, spread=1.0,
               curl=0.5, side=1, scale=1.0, rim=1.0):
    """An oversized clawed hand — a heavy palm knuckle + long tapering talon
    digits with CLEAR separation, hard bone tips and a single rim-light. Boss
    hands are big: this is the loudest "the clown is now a predator" cue. All
    args are in LOGICAL px and scaled by K here. `side` aims the splay,
    `curl` hooks the talon tips. `scale` shrinks the whole hand and `rim` mutes
    its rim-light so the FACE stays the brightest mass and the hands never steal
    the focal point."""
    wx, wy = int(wrist[0]), int(wrist[1])
    w = s(w * scale)
    reach = s(reach * scale)
    # Knuckle slab — a rounded square so the back of the hand reads as mass,
    # not a pom-pom. Dark keyline + a hot top-left rim-light.
    kr = int(w * 1.25)
    pygame.draw.circle(surf, _shade(glove, -75), (wx, wy), kr + sw(1))
    pygame.draw.circle(surf, glove, (wx, wy), kr)
    pygame.draw.circle(surf, _shade(glove, int(70 * rim)),
                       (wx - kr // 3, wy - kr // 3), max(2, kr // 3))
    for i in range(fingers):
        t = i / max(1, fingers - 1) - 0.5
        a = math.pi * 0.5 + side * t * spread + math.radians(22)
        seg = reach / 3.0
        x0, y0 = wx + math.cos(a) * w, wy + math.sin(a) * w
        a2 = a + side * curl * 0.6
        x1 = x0 + math.cos(a2) * seg
        y1 = y0 + math.sin(a2) * seg
        a3 = a2 + side * curl
        x2 = x1 + math.cos(a3) * seg
        y2 = y1 + math.sin(a3) * seg
        fw = max(sw(2), int(w * 0.55))
        # Each digit gets its own dark keyline so neighbours read as SEPARATE
        # claws, not one mitten. Taper from knuckle to tip.
        pygame.draw.line(surf, _shade(glove, -75), (x0, y0), (x1, y1), fw + sw(2))
        pygame.draw.line(surf, glove, (x0, y0), (x1, y1), fw)
        pygame.draw.line(surf, _shade(glove, -75), (x1, y1), (x2, y2), fw)
        pygame.draw.line(surf, glove, (x1, y1), (x2, y2), max(sw(1), fw - sw(1)))
        pygame.draw.line(surf, _shade(glove, int(60 * rim)), (x0, y0),
                         (x0 + math.cos(a2) * seg * 0.5,
                          y0 + math.sin(a2) * seg * 0.5), max(sw(1), fw // 3))
        # Hard tarnished-bone talon at the very tip.
        ax = x2 + math.cos(a3) * seg * 0.7
        ay = y2 + math.sin(a3) * seg * 0.7
        nail = [(x2 + math.cos(a3 + 1.6) * fw, y2 + math.sin(a3 + 1.6) * fw),
                (x2 + math.cos(a3 - 1.6) * fw, y2 + math.sin(a3 - 1.6) * fw),
                (ax, ay)]
        pygame.draw.polygon(surf, BONE, [(int(p[0]), int(p[1])) for p in nail])
        pygame.draw.polygon(surf, _shade(BONE, -70),
                            [(int(p[0]), int(p[1])) for p in nail], sw(1))


def _tarnished_bell(surf, x, y, r=5, *, glint=1.0):
    """A dull, cracked version of the hero's lit gold bell — tarnished brass
    with a dark crack so even the jingles read sinister. `r` is logical px.
    `glint` scales the brass highlight DOWN (1.0 = full) so a crown's bells can
    be muted to keep the face's eye-glint as the focal contest winner."""
    x, y, r = int(x), int(y), s(r)
    pygame.draw.circle(surf, E_GOLD_DK, (x, y), r + sw(1))
    pygame.draw.circle(surf, E_GOLD, (x, y), r)
    pygame.draw.circle(surf, _shade(E_GOLD, int(60 * glint)),
                       (x - r // 3, y - r // 3), max(1, r // 3))
    pygame.draw.line(surf, E_GOLD_DK, (x, y - r), (x - sw(1), y + r), sw(1))


def _dagged_hem(surf, cx, y, half_w, teeth, col, *, drop=14):
    """A tattered DAGGED hem of long jagged points hanging off the tunic bottom
    (the carrion/demon-rag silhouette), each tipped with a dull bell. Logical
    px in; scaled by K. Fewer, LARGER teeth so it reads as ragged mass at scale
    rather than fine noise."""
    cx, y = int(cx), int(y)
    half_w, drop = s(half_w), s(drop)
    n = teeth
    for i in range(n):
        t = i / (n - 1)
        x = cx - half_w + 2 * half_w * t
        nx = cx - half_w + 2 * half_w * (t + 1.0 / (n - 1)) if i < n - 1 else x
        tip = ((x + nx) / 2, y + drop + (s(4) if i % 2 else 0))
        col2 = col if i % 2 == 0 else _shade(col, -34)
        pygame.draw.polygon(surf, col2,
                            [(int(x), y), (int(nx), y),
                             (int(tip[0]), int(tip[1]))])
        pygame.draw.polygon(surf, _shade(col2, -65),
                            [(int(x), y), (int(nx), y),
                             (int(tip[0]), int(tip[1]))], sw(1))
        _tarnished_bell(surf, int(tip[0]), int(tip[1]) + s(2), r=3)


def _harlequin_torso(surf, cx, top_y, bot_y, half_top, half_bot, dark, light,
                     *, lean=0, diamonds=True, rot=False):
    """A tapering diamond-patched torso (the commedia harlequin lozenge motif,
    bruised). Logical px in; all geometry scaled by K. `lean` shears the top
    toward the looming side. Carries a dark core-shadow up the right + a lit
    left rim so the slab reads as round MASS at gameplay scale. `rot` breaks the
    diamond grid with 1-2 deterministic CRACKED / MISSING lozenges so the brute
    reads as decayed rather than freshly patterned."""
    # `cx`, `top_y`, `bot_y` arrive as already-scaled absolute tile coords (they
    # derive from the scaled `hip_y`); the half-widths + lean are logical px.
    cx, top_y, bot_y = int(cx), int(top_y), int(bot_y)
    half_top, half_bot, lean = s(half_top), s(half_bot), s(lean)
    quad = [(cx - half_bot, bot_y), (cx + half_bot, bot_y),
            (cx + half_top + lean, top_y), (cx - half_top + lean, top_y)]
    pygame.draw.polygon(surf, dark, quad)
    pygame.draw.polygon(surf, _shade(dark, -65), quad, sw(2))
    if diamonds:
        prev = surf.get_clip()
        minx = min(p[0] for p in quad)
        maxx = max(p[0] for p in quad)
        surf.set_clip(pygame.Rect(int(minx), int(top_y),
                                  int(maxx - minx) + 1,
                                  int(bot_y - top_y) + 1).clip(prev))
        d = s(20)
        rows = int((bot_y - top_y) / d) + 2
        cols = int((2 * half_bot) / d) + 3
        # Two fixed lozenges read as rot: one upper-chest lozenge is gone to
        # bare bruise (missing), one is fractured by a dark crack (cracked).
        # Keyed to the chest band (r 2-3) so the decay sits at the focal torso,
        # not lost in the hem.
        missing = (3, cols // 2)
        cracked = (2, cols // 2 + 1)
        for r in range(rows):
            for c in range(cols):
                offs = (d // 2) if r % 2 else 0
                px = cx - half_bot + c * d - d + offs
                py = int(top_y) + r * d
                if (r + c) % 2 == 0:
                    continue
                lo = [(px, py - d // 2), (px + d // 2, py),
                      (px, py + d // 2), (px - d // 2, py)]
                if rot and (r, c) == missing:
                    # Missing patch: bare bruised plum where the lime once was.
                    pygame.draw.polygon(surf, _shade(dark, -30), lo)
                    pygame.draw.polygon(surf, _shade(dark, -70), lo, sw(1))
                    continue
                pygame.draw.polygon(surf, light, lo)
                pygame.draw.polygon(surf, _shade(light, -45), lo, sw(1))
                if rot and (r, c) == cracked:
                    # A jagged dark fracture splitting the lozenge in two.
                    pygame.draw.lines(surf, _shade(dark, -70), False,
                                      [(px, py - d // 2),
                                       (px + d // 6, py - d // 6),
                                       (px - d // 8, py + d // 8),
                                       (px, py + d // 2)], sw(2))
        surf.set_clip(prev)
    # Lit left rim + a heavy bruise core-shadow up the right so it reads round.
    pygame.draw.line(surf, _shade(dark, 55),
                     (cx - half_top + lean + sw(2), top_y + s(3)),
                     (cx - half_bot + sw(2), bot_y - s(3)), sw(3))
    smear = pygame.Surface((int(half_bot), int(bot_y - top_y)), pygame.SRCALPHA)
    pygame.draw.ellipse(smear, (*_shade(dark, -55), 150), smear.get_rect())
    surf.blit(smear, (int(cx + half_bot * 0.05), int(top_y + s(4))))


def _ruff(surf, cx, neck_y, half_w, lobes, *, dip=0, lift=0):
    """The hero's gold scalloped ruff bloated + tarnished. A doubled row of fat
    overlapping brass lobes so the shoulder line reads BROAD — the simplest way
    to add the boss's wide silhouette mass. Logical px in."""
    cx, neck_y = int(cx), int(neck_y)
    half_w = s(half_w)
    r = max(sw(7), int(half_w / lobes * 1.35))
    for i in range(lobes):
        t = i / (lobes - 1)
        lx = int(cx - half_w + 2 * half_w * t)
        ly = int(neck_y + s(dip) + math.sin(t * math.pi) * s(lift))
        pygame.draw.circle(surf, E_GOLD_DK, (lx, ly), r + sw(1))
        pygame.draw.circle(surf, E_GOLD, (lx, ly), r)
        pygame.draw.circle(surf, _shade(E_GOLD, 65), (lx - r // 3, ly - r // 3),
                           max(2, r // 3))


def _evolved_head(surf, cx, cy, hr, *, eye="dead", mouth="fangs", gaunt=False,
                  tilt=0):
    """A bigger, MEANER head built around 2-3 HIGH-CONTRAST MACRO shapes so the
    menace survives downscale: a dark sunken brow band, one bright sick eye-
    glint, and a hard-edged maw/grin. The soft pale face FILL is dropped —
    the face is bruised + bottom-shadowed so "meaner" reads before any feature
    resolves. Logical px in; geometry scaled by K and drawn onto a scratch
    surface so the tilt is real."""
    cx, cy, hr = int(cx), int(cy), s(hr)
    pad = hr * 3
    sc = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    sx, sy = pad, pad
    # MACRO 1 — the head as a bruised mass: dark keyline, ashen upper face,
    # and a hard core-shadow flooding the LOWER half so the maw sits in gloom.
    pygame.draw.circle(sc, _shade(SKIN_PALE, -70), (sx, sy), hr + sw(2))
    pygame.draw.circle(sc, SKIN_PALE, (sx, sy), hr)
    shadow = pygame.Surface((hr * 2, hr * 2), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (*SKIN_DK, 200), (hr, hr), hr)
    sc.set_clip(pygame.Rect(sx - hr, sy, hr * 2, hr * 2))
    sc.blit(shadow, (sx - hr, sy - hr))
    sc.set_clip(None)
    if gaunt:
        for sg in (-1, 1):
            hollow = pygame.Surface((hr, hr), pygame.SRCALPHA)
            pygame.draw.ellipse(hollow, (*E_PLUM_DK, 150), hollow.get_rect())
            sc.blit(hollow, (sx + sg * hr // 2 - hr // 2, sy - hr // 5))
    # MACRO 2 — a single HARD dark brow band slammed across the eyes, dipping
    # to a centre V. This one shape carries most of the menace at small size.
    brow_y = sy - int(hr * 0.30)
    brow = [(sx - hr + sw(2), brow_y - s(3)),
            (sx + hr - sw(2), brow_y - s(3)),
            (sx + int(hr * 0.55), brow_y + s(5)),
            (sx, brow_y + int(hr * 0.32)),
            (sx - int(hr * 0.55), brow_y + s(5))]
    pygame.draw.polygon(sc, _shade(E_PLUM_DK, -10), brow)
    ex = max(sw(7), int(hr * 0.42))
    ey = sy - int(hr * 0.04)
    for sgn in (-1, 1):
        exx = sx + sgn * ex
        # Deep socket pocket under the brow band.
        sock = pygame.Surface((ex + s(4), ex), pygame.SRCALPHA)
        pygame.draw.ellipse(sock, (*E_PLUM_DK, 170), sock.get_rect())
        sc.blit(sock, (exx - (ex + s(4)) // 2, ey - ex // 2))
        # MACRO 3 — the bright eye-glint: a small hot dot that POPS at 1x.
        if eye == "sick":
            pygame.draw.circle(sc, _shade(SICK_EYE, -50), (exx, ey),
                               max(sw(3), hr // 5) + sw(1))
            pygame.draw.circle(sc, SICK_EYE, (exx, ey), max(sw(3), hr // 5))
            pygame.draw.circle(sc, (240, 255, 210), (exx - sw(1), ey - sw(1)),
                               max(sw(1), hr // 12))
            pygame.draw.ellipse(sc, (16, 20, 8),
                                (exx - sw(1), ey - hr // 5, sw(2), hr * 2 // 5))
        elif eye == "dead":
            pygame.draw.circle(sc, BONE, (exx, ey), max(sw(3), hr // 5))
            pygame.draw.circle(sc, DEAD_EYE, (exx, ey), max(sw(2), hr // 8))
            pygame.draw.circle(sc, (255, 210, 200),
                               (exx - sw(1), ey - sw(1)), max(1, hr // 16))
        else:  # "leer" — a hot pinprick jammed to the inner corner, sidelong
            pygame.draw.circle(sc, BONE, (exx, ey), max(sw(3), hr // 5))
            pygame.draw.circle(sc, SICK_EYE,
                               (exx - sgn * (hr // 7), ey), max(sw(2), hr // 8))
    # The bruise-dark nose (the red ball gone wound-dark, shrunk + seated low).
    pygame.draw.circle(sc, _shade(BLOOD, -40), (sx, sy + hr // 4),
                       max(sw(3), hr // 6))
    pygame.draw.circle(sc, BLOOD, (sx, sy + hr // 4), max(sw(2), hr // 8))
    pygame.draw.circle(sc, _shade(BLOOD, 50), (sx - sw(1), sy + hr // 4 - sw(1)),
                       max(1, hr // 14))
    # MOUTH — a hard-edged maw / grin sitting in the lower shadow.
    my = sy + int(hr * 0.55)
    if mouth == "fangs":
        mw = int(hr * 0.78)
        maw = pygame.Rect(sx - mw, my - s(2), mw * 2, int(hr * 0.62))
        pygame.draw.ellipse(sc, (28, 6, 12), maw)
        n = 6
        for i in range(n):
            t = i / (n - 1)
            tx = sx - mw + 2 * mw * t
            fw = s(5)
            pygame.draw.polygon(sc, BONE, [(int(tx - fw), maw.top),
                                           (int(tx + fw), maw.top),
                                           (int(tx), maw.top + hr // 3)])
            pygame.draw.polygon(sc, _shade(BONE, -70),
                                [(int(tx - fw), maw.top),
                                 (int(tx + fw), maw.top),
                                 (int(tx), maw.top + hr // 3)], sw(1))
        pygame.draw.ellipse(sc, BLOOD, maw, sw(2))
    elif mouth == "grin":
        mw = int(hr * 0.88)
        lip = []
        for kk in range(15):
            t = kk / 14.0
            lx = sx - mw + 2 * mw * t
            ly = my + (1.0 - (2.0 * t - 1.0) ** 2) * (-hr * 0.62)
            lip.append((int(lx), int(ly)))
        # A solid dark grin gap with a fang row so it reads at 1x, not a thin
        # line. Build a closed maw under the lip curve.
        gap = lip + [(int(sx + mw), my + s(2)), (int(sx - mw), my + s(2))]
        pygame.draw.polygon(sc, (28, 6, 12), gap)
        for i in range(7):
            t = i / 6.0
            tx = sx - mw + 2 * mw * t
            ty = my + (1.0 - (2.0 * t - 1.0) ** 2) * (-hr * 0.5)
            pygame.draw.polygon(sc, BONE, [(int(tx - s(4)), int(ty)),
                                           (int(tx + s(4)), int(ty)),
                                           (int(tx), int(ty + hr // 4))])
        for sgn in (-1, 1):
            pygame.draw.line(sc, BLOOD, (sx + sgn * mw, my),
                             (sx + sgn * (mw + hr // 4), my - hr // 4), sw(2))
    else:  # "smirk" — one corner hooked hard up, cold knowing leer
        mw = int(hr * 0.74)
        smirk = [(sx - mw, my + hr // 6), (sx + mw, my - hr // 3),
                 (sx + mw, my - hr // 6), (sx - mw, my + hr // 3)]
        pygame.draw.polygon(sc, (28, 6, 12), smirk)
        fx = sx + mw
        pygame.draw.polygon(sc, BONE, [(fx - s(4), my - hr // 3),
                                       (fx + s(2), my - hr // 3),
                                       (fx - sw(1), my)])
        pygame.draw.line(sc, BLOOD, (sx - mw, my + hr // 6),
                         (sx - mw - hr // 5, my + hr // 6 + s(3)), sw(2))
    # Dark keyline re-stated on top so the whole head pops off the body.
    pygame.draw.circle(sc, _shade(SKIN_PALE, -90), (sx, sy), hr, sw(2))
    rot = pygame.transform.rotate(sc, tilt)
    surf.blit(rot, (cx - rot.get_width() // 2, cy - rot.get_height() // 2))


# ── evolved cap architectures — every one a MUTATED 3-point jester cap ───────

def cap_coil_droop(surf, cx, base_y, hr, cols):
    """A heavy mutated 3-point jester cap, points drooping low + asymmetric,
    each ending in a fat tarnished bell — the coiled stalker's wilted crown."""
    cx, base_y, hr = int(cx), int(base_y), s(hr)
    a, b, c = cols
    span = s(18)
    for dx, dy, col in ((s(-6), s(-14), a), (s(-34), s(28), b),
                        (s(40), s(20), c)):
        bx, by = cx + dx, base_y + dy
        pts = [(cx - span, base_y + s(2)), (cx + span, base_y + s(2)),
               (bx + span // 2, (base_y + by) // 2 - s(6)),
               (bx, by), (bx - span // 2, (base_y + by) // 2 + s(2))]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, -65), pts, sw(2))
    for dx, dy in ((s(-6), s(-14)), (s(-34), s(28)), (s(40), s(20))):
        _tarnished_bell(surf, cx + dx, base_y + dy, r=6)


def cap_brute_crown(surf, cx, base_y, hr, cols, *, glint=1.0):
    """A HEAVY canted 3-point jester cap bloated into a brutish slab crown:
    three thick points (one big centre, two splayed past the wide skull),
    the whole crown tipped a few degrees so it reads as a mean, lopsided
    weight pressing down on the brow. Keeps the 3-point lineage, escalated.
    `glint` pulls the crown's brass highlights DOWN so the face's eye-glint
    wins the focal contest (the crown shouldn't out-sparkle the eyes)."""
    cx, base_y, hr = int(cx), int(base_y), s(hr)
    a, b, c = cols[0], cols[1], cols[2]
    cant = s(6)
    span = s(26)
    for dx, dy, col in ((-hr - s(14), s(2), a), (s(2), -s(38), b),
                        (hr + s(16), -s(2), c)):
        bx, by = cx + dx + cant, base_y + dy
        pts = [(cx - span, base_y + s(2)), (cx + span, base_y + s(2)), (bx, by)]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, int(50 * glint)),
                            [(cx - span, base_y + s(2)), (cx, base_y + s(2)),
                             (bx, by)])
        pygame.draw.polygon(surf, _shade(col, -70), pts, sw(2))
        _tarnished_bell(surf, bx, by, r=7, glint=glint)
    # A thick canted brim-band rooting the crown to the wide skull.
    band = pygame.Rect(0, 0, hr * 2 + s(20), s(16))
    band.center = (cx + cant // 2, base_y + s(4))
    pygame.draw.ellipse(surf, _shade(a, -25), band)
    pygame.draw.ellipse(surf, _shade(a, -70), band, sw(2))


def cap_horn_droop(surf, cx, base_y, hr, cols):
    """A mutated 3-point cap whose two SIDE points have stiffened + curled into
    heavy back-swept horn-lobes (bone-tipped), with the centre point still a
    clear belled jester spike between them — devil read, but unmistakably still
    OUR cap, not a generic demon horn-pair."""
    cx, base_y, hr = int(cx), int(base_y), s(hr)
    a, b = cols[0], cols[1]
    pygame.draw.ellipse(surf, _shade(a, -30),
                        (cx - hr - s(2), base_y - s(8), hr * 2 + s(4), s(20)))
    # Centre jester spike (keeps the lineage explicit).
    sp = [(cx - s(9), base_y), (cx + s(9), base_y), (cx + s(2), base_y - s(40))]
    pygame.draw.polygon(surf, b, sp)
    pygame.draw.polygon(surf, _shade(b, -65), sp, sw(2))
    _tarnished_bell(surf, cx + s(2), base_y - s(40), r=5)
    for sgn, col in ((-1, a), (1, b)):
        # A thick cap-point that stiffens, sweeps up + curls BACK to a bone tip.
        bx0 = cx + sgn * (hr - s(2))
        pts = [(bx0, base_y + s(2)), (bx0 + sgn * s(8), base_y - s(20)),
               (bx0 + sgn * s(4), base_y - s(42)),
               (bx0 - sgn * s(12), base_y - s(56)),
               (bx0 - sgn * s(20), base_y - s(44)),
               (bx0 - sgn * s(6), base_y - s(26)),
               (bx0 - sgn * s(10), base_y + s(2))]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, -70), pts, sw(2))
        tip = (bx0 - sgn * s(12), base_y - s(56))
        pygame.draw.circle(surf, BONE, tip, sw(4))
        pygame.draw.circle(surf, _shade(BONE, -65), tip, sw(4), sw(1))


def cap_carrion_crest(surf, cx, base_y, hr, cols):
    """A mutated 3-point cap whose points have torn + multiplied into a ragged
    carrion COXCOMB — a few BIG jagged spikes (not fine noise) rooted in a dark
    band, the three tallest bell-tipped to keep the jester read."""
    cx, base_y, hr = int(cx), int(base_y), s(hr)
    a, b = cols[0], cols[1]
    band = [(cx - hr, base_y + s(4)), (cx - hr // 2, base_y - s(12)),
            (cx + s(2), base_y - s(16)), (cx + hr // 2, base_y - s(10)),
            (cx + hr, base_y + s(4))]
    pygame.draw.polygon(surf, _shade(a, -35), band)
    pygame.draw.polygon(surf, _shade(a, -75), band, sw(2))
    spikes = [(-hr + s(6), -s(20), s(6)), (-hr // 3, -s(46), s(9)),
              (s(2), -s(58), s(10)), (hr // 3, -s(44), s(9)),
              (hr - s(6), -s(18), s(6))]
    for i, (dx, dy, hw) in enumerate(spikes):
        col = a if i % 2 == 0 else b
        bx, by = cx + dx, base_y + dy
        pts = [(bx - hw, base_y - s(4)), (bx + hw, base_y - s(4)), (bx, by)]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, 45),
                            [(bx - hw, base_y - s(4)), (bx, base_y - s(4)),
                             (bx, by)])
        pygame.draw.polygon(surf, _shade(col, -70), pts, sw(2))
        if i in (1, 2, 3):
            _tarnished_bell(surf, bx, by, r=4)


def cap_puppet_ears(surf, cx, base_y, hr, cols):
    """A mutated 3-point cap whose two side points have grown into heavy droopy
    donkey-ear lobes, the centre still a tall belled jester spike — the regal-
    grotesque puppeteer's distinctive eared crown."""
    cx, base_y, hr = int(cx), int(base_y), s(hr)
    a, b, c = cols[0], cols[1], cols[2]
    sp = [(cx - s(12), base_y + s(2)), (cx + s(12), base_y + s(2)),
          (cx + s(2), base_y - s(56))]
    pygame.draw.polygon(surf, b, sp)
    pygame.draw.polygon(surf, _shade(b, -65), sp, sw(2))
    _tarnished_bell(surf, cx + s(2), base_y - s(56), r=6)
    for sgn, col in ((-1, a), (1, c)):
        tipx, tipy = cx + sgn * (hr + s(18)), base_y + s(34)
        spine = [(cx + sgn * s(6), base_y), (cx + sgn * s(22), base_y - s(6)),
                 (cx + sgn * (hr + s(12)), base_y - s(20)), (tipx, tipy),
                 (cx + sgn * (hr + s(2)), base_y + s(6)),
                 (cx + sgn * s(14), base_y + s(12))]
        pygame.draw.polygon(surf, col, spine)
        pygame.draw.polygon(surf, _shade(col, -65), spine, sw(2))
        _tarnished_bell(surf, tipx, tipy, r=6)


# ── the FIVE evolved concepts (each its own builder + stance) ────────────────
# Concepts are written in LEAD order in the sheet: #1 = Hulking Brute (best),
# #2 = Carrion Coxcomb (2nd). Every figure is built CLEARLY taller AND broader
# than the hero's ~160px body so the size jump reads at a glance, and every
# silhouette passes the blackout test (reads as "the jester, bigger, meaner").

def concept_hulking_brute(surf, cx, feet_y):
    """LEAD 1. HULKING BRUTE — massive, top-heavy slab; low planted power
    stance; wide shoulder-doubling ruff; canted heavy crown; both fists planted
    with knuckle facets + rim-light; a wide fanged maw as the focal point."""
    hip_y = feet_y - s(116)
    # Short thick legs splayed wide + planted — the low boss stance.
    for sgn in (-1, 1):
        col = E_PLUM if sgn < 0 else E_LIME_DK
        hip = (cx + sgn * s(26), hip_y)
        ankle = (cx + sgn * s(42), feet_y - s(8))
        pygame.draw.line(surf, _shade(col, -60), hip, ankle, sw(24))
        pygame.draw.line(surf, col, hip, ankle, sw(20))
        shoe = pygame.Rect(0, 0, s(50), s(24))
        shoe.center = (ankle[0] + sgn * s(8), feet_y - s(2))
        pygame.draw.ellipse(surf, E_PLUM_DK, shoe)
        pygame.draw.ellipse(surf, _shade(E_PLUM_DK, 35), shoe.inflate(-s(8), -s(10)))
        _tarnished_bell(surf, shoe.centerx + sgn * s(22), shoe.top, r=4)
    # Huge barrel torso, widest at the chest — clearly broader than the hero.
    # `rot` breaks the diamond grid with 1-2 cracked/missing lozenges.
    _harlequin_torso(surf, cx, hip_y - s(100), hip_y + s(10), 30, 64,
                     E_PLUM, E_LIME, rot=True)
    _dagged_hem(surf, cx, hip_y + s(8), 64, 7, E_PLUM, drop=14)
    neck_y = hip_y - s(94)
    # Both arms spread wide + heavy, doubling the shoulder mass, ending in big
    # planted claw-fists (drawn BEFORE the ruff so the ruff caps the shoulders).
    for sgn in (-1, 1):
        col = E_LIME_DK if sgn < 0 else E_PLUM
        sh = (cx + sgn * s(58), neck_y + s(12))
        elbow = (cx + sgn * s(84), neck_y + s(58))
        wrist = (cx + sgn * s(70), hip_y + s(8))
        for a, b in ((sh, elbow), (elbow, wrist)):
            pygame.draw.line(surf, _shade(col, -60), a, b, sw(26))
            pygame.draw.line(surf, col, a, b, sw(22))
        _claw_hand(surf, wrist, 22, 9, CLAW, side=sgn, curl=0.55)
    # A massive shoulder-doubling brass ruff slung wide across the top.
    _ruff(surf, cx, neck_y + s(6), 70, 15, dip=4, lift=-6)
    # Head sunk low between the shoulders — the wide fanged maw is the focal.
    head_cx, head_cy, hr = cx, neck_y - s(6), 28
    # Crown glint pulled DOWN ~15% so the bright eye-glint wins the focal fight.
    cap_brute_crown(surf, head_cx, head_cy - s(hr) + s(10), hr,
                    (E_PLUM, E_LIME, E_GOLD), glint=0.85)
    _evolved_head(surf, head_cx, head_cy, hr, eye="dead", mouth="fangs",
                  tilt=-4)


def concept_carrion(surf, cx, feet_y):
    """LEAD 2. CARRION COXCOMB — vulture hunch with raised shoulders + head
    thrust LOW and forward; a BROAD torso (bigger than the hero, not merely
    hunched); a FEW big ragged tatters; a clear shadowed brow + one sharp
    eye-glint; the meanest, most unique silhouette."""
    hip_y = feet_y - s(112)
    for sgn in (-1, 1):
        col = E_PLUM if sgn < 0 else E_LIME_DK
        hip = (cx + sgn * s(16), hip_y)
        knee = (cx + sgn * s(26), hip_y + s(52))
        ankle = (cx + sgn * s(18), feet_y - s(6))
        for a, b in ((hip, knee), (knee, ankle)):
            pygame.draw.line(surf, _shade(col, -60), a, b, sw(18))
            pygame.draw.line(surf, col, a, b, sw(15))
        toe = [(ankle[0] - s(15), feet_y), (ankle[0] + s(22), feet_y),
               (ankle[0] + s(30), feet_y - s(10))]
        pygame.draw.polygon(surf, E_PLUM_DK, [(int(p[0]), int(p[1])) for p in toe])
        _tarnished_bell(surf, ankle[0] + s(30), feet_y - s(10), r=4)
    # Broad hunched torso: top sheared hard forward, but WIDE so it still reads
    # bigger than the hero — not a thin hunch.
    _harlequin_torso(surf, cx, hip_y - s(92), hip_y + s(4), 30, 46, E_PLUM,
                     E_LIME, lean=-s(18))
    # A FEW big ragged tatters (not many small = noise) hanging off the hem.
    _dagged_hem(surf, cx, hip_y + s(2), 46, 5, E_PLUM, drop=24)
    neck_y = hip_y - s(86)
    # Raised hunched shoulders (toward the ears) with long arms dangling fwd,
    # hooked claws — drawn before the lopsided ruff caps them.
    for sgn in (-1, 1):
        col = E_LIME_DK if sgn < 0 else E_PLUM
        sh = (cx + sgn * s(44), neck_y - s(10))    # raised high, hunched
        elbow = (cx + sgn * s(50), neck_y + s(46))
        wrist = (cx + sgn * s(28), hip_y + s(22))  # dangling forward + in
        for a, b in ((sh, elbow), (elbow, wrist)):
            pygame.draw.line(surf, _shade(col, -60), a, b, sw(18))
            pygame.draw.line(surf, col, a, b, sw(14))
        _claw_hand(surf, wrist, 20, 8, CLAW, side=sgn, curl=0.95)
    # A lopsided tattered brass ruff slumped forward off the hunch.
    _ruff(surf, cx - s(6), neck_y + s(8), 44, 11, dip=4, lift=7)
    # Head thrust LOW + forward off the hunch (vulture peer), tilted, smirking.
    head_cx, head_cy, hr = cx - s(22), neck_y + s(6), 25
    pygame.draw.line(surf, _shade(SKIN_DK, -30),
                     (cx - s(4), neck_y), (head_cx + s(8), head_cy), sw(16))
    cap_carrion_crest(surf, head_cx, head_cy - s(hr) + s(8), hr, (E_PLUM, E_LIME))
    _evolved_head(surf, head_cx, head_cy, hr, eye="sick", mouth="smirk",
                  gaunt=True, tilt=20)


def concept_horned_imp(surf, cx, feet_y):
    """3. HORNED IMP-LORD — tall + broad-shouldered devil; mutated 3-point cap
    with back-swept horn-lobes + a centre belled spike (still OUR cap); one big
    clawed hand raised in a beckoning curl; luminous sick eyes."""
    hip_y = feet_y - s(126)
    for sgn in (-1, 1):
        col = E_LIME_DK if sgn < 0 else E_PLUM
        hip = (cx + sgn * s(13), hip_y)
        knee = (cx + sgn * s(22), hip_y + s(54))
        ankle = (cx + sgn * s(12), feet_y - s(6))
        for a, b in ((hip, knee), (knee, ankle)):
            pygame.draw.line(surf, _shade(col, -60), a, b, sw(16))
            pygame.draw.line(surf, col, a, b, sw(13))
        toe = [(ankle[0] - s(13), feet_y), (ankle[0] + s(18), feet_y),
               (ankle[0] + s(26), feet_y - s(11))]
        pygame.draw.polygon(surf, E_PLUM_DK, [(int(p[0]), int(p[1])) for p in toe])
        _tarnished_bell(surf, ankle[0] + s(26), feet_y - s(11), r=4)
    _harlequin_torso(surf, cx, hip_y - s(90), hip_y + s(4), 26, 38, E_PLUM,
                     E_LIME)
    _dagged_hem(surf, cx, hip_y + s(2), 38, 6, E_PLUM, drop=18)
    neck_y = hip_y - s(84)
    # Right arm hangs with a big claw; left raised, claw curling in a beckon.
    sh_r = (cx + s(30), neck_y + s(10))
    wrist_r = (cx + s(42), hip_y - s(6))
    pygame.draw.line(surf, _shade(E_LIME_DK, -60), sh_r, wrist_r, sw(16))
    pygame.draw.line(surf, E_LIME_DK, sh_r, wrist_r, sw(13))
    _claw_hand(surf, wrist_r, 18, 8, CLAW, side=1, curl=0.7)
    sh_l = (cx - s(30), neck_y + s(10))
    elbow_l = (cx - s(52), neck_y - s(20))
    wrist_l = (cx - s(36), neck_y - s(56))
    for a, b in ((sh_l, elbow_l), (elbow_l, wrist_l)):
        pygame.draw.line(surf, _shade(E_PLUM, -60), a, b, sw(16))
        pygame.draw.line(surf, E_PLUM, a, b, sw(13))
    _claw_hand(surf, wrist_l, 22, 9, CLAW, side=-1, curl=1.15)
    # A pointed dagged lime collar (sharp points, not soft scallops) + wide ruff.
    _ruff(surf, cx, neck_y + s(6), 46, 12, dip=4, lift=-4)
    head_cx, head_cy, hr = cx + s(2), neck_y - s(20), 26
    cap_horn_droop(surf, head_cx, head_cy - s(hr) + s(10), hr,
                   (E_PLUM, E_PLUM_DK))
    _evolved_head(surf, head_cx, head_cy, hr, eye="sick", mouth="grin",
                  tilt=-8)


def concept_puppeteer(surf, cx, feet_y):
    """4. RINGMASTER PUPPETEER — towering + broad; arms lowered + CLAWED in a
    looming menacing reach (not a celebratory flourish); donkey-ear spike cap;
    broad diamond robe; a too-wide corner-cracked grin."""
    hip_y = feet_y - s(122)
    for sgn in (-1, 1):
        col = E_PLUM if sgn < 0 else E_LIME_DK
        hip = (cx + sgn * s(16), hip_y)
        ankle = (cx + sgn * s(18), feet_y - s(8))
        pygame.draw.line(surf, _shade(col, -60), hip, ankle, sw(18))
        pygame.draw.line(surf, col, hip, ankle, sw(15))
        toe = [(ankle[0] - s(16), feet_y), (ankle[0] + s(22), feet_y),
               (ankle[0] + s(32), feet_y - s(14)),
               (ankle[0] + s(26), feet_y - s(22))]
        pygame.draw.polygon(surf, E_PLUM_DK, [(int(p[0]), int(p[1])) for p in toe])
        _tarnished_bell(surf, ankle[0] + s(26), feet_y - s(22), r=5)
    _harlequin_torso(surf, cx, hip_y - s(100), hip_y + s(8), 32, 52, E_PLUM,
                     E_LIME)
    _dagged_hem(surf, cx, hip_y + s(6), 52, 7, E_PLUM, drop=24)
    neck_y = hip_y - s(94)
    # Arms held out + DOWN, clawed and reaching toward the viewer — a looming,
    # menacing "closing in" gesture, not a celebratory V.
    for sgn in (-1, 1):
        col = E_LIME_DK if sgn < 0 else E_PLUM
        sh = (cx + sgn * s(36), neck_y + s(10))
        elbow = (cx + sgn * s(66), neck_y + s(34))
        wrist = (cx + sgn * s(74), neck_y + s(80))
        for a, b in ((sh, elbow), (elbow, wrist)):
            pygame.draw.line(surf, _shade(col, -60), a, b, sw(18))
            pygame.draw.line(surf, col, a, b, sw(14))
        # A trailing dagged sleeve hanging off the forearm.
        drape = [(elbow[0], elbow[1]), (wrist[0], wrist[1]),
                 (wrist[0] - sgn * s(8), wrist[1] + s(26)),
                 ((elbow[0] + wrist[0]) // 2 - sgn * s(10),
                  (elbow[1] + wrist[1]) // 2 + s(30))]
        pygame.draw.polygon(surf, _shade(col, -28),
                            [(int(p[0]), int(p[1])) for p in drape])
        pygame.draw.polygon(surf, _shade(col, -65),
                            [(int(p[0]), int(p[1])) for p in drape], sw(1))
        # Hands tamed to 80% with the rim-light down 25% so the FACE out-brights
        # them and they stop stealing the focal point.
        _claw_hand(surf, wrist, 22, 9, CLAW, side=sgn, curl=1.0,
                   scale=0.8, rim=0.75)
    # A grand wide brass ruff capping the broad shoulders.
    _ruff(surf, cx, neck_y + s(6), 60, 15, dip=4, lift=-5)
    head_cx, head_cy, hr = cx, neck_y - s(22), 27
    cap_puppet_ears(surf, head_cx, head_cy - s(hr) + s(10), hr,
                    (E_PLUM, E_LIME, E_LIME_DK))
    _evolved_head(surf, head_cx, head_cy, hr, eye="dead", mouth="grin",
                  tilt=0)


def concept_coiled_stalker(surf, cx, feet_y):
    """5. COILED STALKER — replaces round-1's too-small Gaunt Stalker. A big
    low-CROUCHING predator coiled to spring: deep-bent legs spread wide, torso
    pitched forward + low over a broad hunched back, one big claw planted on the
    ground + one raised mid-pounce. Reads BIG via width + forward mass even
    though crouched. Mutated coil-droop 3-point cap, dead-eye smirk."""
    # Crouched: hips sit LOW, but the spread + forward pitch make it read big.
    hip_y = feet_y - s(70)
    for sgn in (-1, 1):
        col = E_PLUM if sgn < 0 else E_LIME_DK
        hip = (cx + sgn * s(20), hip_y)
        knee = (cx + sgn * s(48), hip_y + s(8))    # knees kicked WIDE + up
        ankle = (cx + sgn * s(40), feet_y - s(6))
        for a, b in ((hip, knee), (knee, ankle)):
            pygame.draw.line(surf, _shade(col, -60), a, b, sw(20))
            pygame.draw.line(surf, col, a, b, sw(16))
        toe = [(ankle[0] - s(16), feet_y), (ankle[0] + s(20), feet_y),
               (ankle[0] + s(28), feet_y - s(10))]
        pygame.draw.polygon(surf, E_PLUM_DK, [(int(p[0]), int(p[1])) for p in toe])
        _tarnished_bell(surf, ankle[0] + s(28), feet_y - s(10), r=4)
    # Broad back pitched forward + low over the coil (sheared hard, wide base).
    _harlequin_torso(surf, cx, hip_y - s(70), hip_y + s(6), 34, 48, E_PLUM,
                     E_LIME, lean=-s(28))
    _dagged_hem(surf, cx, hip_y + s(4), 48, 5, E_PLUM, drop=20)
    neck_y = hip_y - s(64)
    # One big claw planted forward on the GROUND (coiled), one raised to strike.
    plant_sh = (cx - s(30), neck_y + s(6))
    plant_wrist = (cx - s(58), feet_y - s(18))
    for a, b in ((plant_sh, plant_wrist),):
        pygame.draw.line(surf, _shade(E_PLUM, -60), a, b, sw(18))
        pygame.draw.line(surf, E_PLUM, a, b, sw(15))
    _claw_hand(surf, plant_wrist, 22, 9, CLAW, side=-1, curl=0.4)
    raise_sh = (cx + s(34), neck_y - s(4))
    raise_elbow = (cx + s(54), neck_y - s(30))
    raise_wrist = (cx + s(40), neck_y - s(62))
    for a, b in ((raise_sh, raise_elbow), (raise_elbow, raise_wrist)):
        pygame.draw.line(surf, _shade(E_LIME_DK, -60), a, b, sw(18))
        pygame.draw.line(surf, E_LIME_DK, a, b, sw(14))
    _claw_hand(surf, raise_wrist, 22, 9, CLAW, side=1, curl=1.0)
    # A lopsided ruff slumped forward off the low hunch.
    _ruff(surf, cx - s(8), neck_y + s(6), 42, 11, dip=4, lift=6)
    # Head thrust far forward + low along the coil, dead-eye smirk, tilted.
    head_cx, head_cy, hr = cx - s(30), neck_y + s(4), 25
    pygame.draw.line(surf, _shade(SKIN_DK, -30),
                     (cx - s(6), neck_y), (head_cx + s(8), head_cy), sw(16))
    cap_coil_droop(surf, head_cx, head_cy - s(hr) + s(8), hr,
                   (E_PLUM, E_LIME_DK, E_GOLD))
    _evolved_head(surf, head_cx, head_cy, hr, eye="dead", mouth="smirk",
                  gaunt=True, tilt=22)


# ── the original reference (clown-only, from build_jester) ───────────────────

def concept_original(surf, cx, feet_y):
    """Cell 0: the CURRENT hero clown, drawn clown-only (no staff). It must look
    SMALL beside the evolved leads — drawn at the hero's native scale (no K), so
    its ~160px body sits clearly under the boss masses around it."""
    hand_up = (cx - 30, feet_y - 92)
    build_jester(surf, cx, feet_y, hand_up, **ORIG)


# ── the combined sheet ───────────────────────────────────────────────────────

# Leads first: the two strongest directions (Hulking Brute, Carrion Coxcomb)
# open the sheet so the eye lands on them before the supporting concepts.
CONCEPTS = [
    ("ORIGINAL — Plum & Lime (locked)", concept_original),
    ("1. HULKING BRUTE  ★lead", concept_hulking_brute),
    ("2. CARRION COXCOMB  ★lead", concept_carrion),
    ("3. HORNED IMP-LORD", concept_horned_imp),
    ("4. RINGMASTER PUPPETEER", concept_puppeteer),
    ("5. COILED STALKER", concept_coiled_stalker),
]

# Sub-captions describing each concept's distinct read.
SUBS = [
    "the early-game clown, clown-only · drawn SMALL for scale + menace comparison",
    "massive top-heavy slab · low planted stance · doubling ruff · canted crown · fanged maw",
    "vulture hunch · raised shoulders · head thrust LOW · few big tatters · sick eye-glint",
    "tall broad devil · mutated 3-pt cap w/ horn-lobes + belled spike · beckoning claw",
    "towering · arms lowered + CLAWED, looming in · donkey-ear spike cap · too-wide grin",
    "low CROUCH coiled to spring · spread wide · one claw planted, one raised · dead-eye smirk",
]


def _wrap(font, text, max_w):
    """Greedy word-wrap `text` to lines no wider than `max_w` px."""
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.size(t)[0] <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    # Crispness fix: the figure tile is rendered DIRECTLY at K× the logical size
    # (every concept multiplies its geometry by K), then blitted 1:1 into the
    # cell — no smoothscale upscale, so edges stay sharp and eye-glints stay
    # crisp dots. The cell IS the K-rendered tile, so there is no resampling.
    FIG_W, FIG_H = 260, 360                 # logical figure-tile size
    GROUND_Y = FIG_H - 36                   # logical matched ground line
    TILE_W, TILE_H = FIG_W * K, FIG_H * K   # actual rendered (crisp) tile
    GROUND_Y_K = GROUND_Y * K
    CELL_W, CELL_H = TILE_W, TILE_H
    cols, rows = 3, 2
    PAD, GAP = 60, 34

    # Fonts bumped to match the larger K× canvas so captions stay legible.
    f_title = pygame.font.SysFont(None, 72, bold=True)
    f_sub = pygame.font.SysFont(None, 36, bold=True)
    f_cap = pygame.font.SysFont(None, 46, bold=True)
    f_caps = pygame.font.SysFont(None, 32, bold=True)

    canvas_w = PAD * 2 + cols * CELL_W + (cols - 1) * GAP
    inner_w = canvas_w - 2 * PAD

    title_lines = _wrap(
        f_title, "EVOLVED WARREN CLOWN — late-game boss escalation (round 2)",
        inner_w)
    sub_lines = _wrap(
        f_sub, "The SAME Plum & Lime character, gone ROTTEN + BIG: near-black "
        "bruise plum, venom green-gray lime, tarnished brass gold + blood/bruise "
        "accents. Each face is built on hard macro shapes (sunken brow, bright "
        "eye-glint, hard maw) so menace survives at gameplay scale. Leads ★ first; "
        "the hero is drawn SMALL for scale. No staff (separate cycle).", inner_w)
    # Per-cell sub-captions wrapped to the cell width.
    sub_wrapped = [_wrap(f_caps, txt, CELL_W - 10) for txt in SUBS]
    max_sub_lines = max(len(x) for x in sub_wrapped)

    th = f_title.get_height() + 2
    sh_ = f_sub.get_height() + 2
    TITLE_H = len(title_lines) * th + 10 + len(sub_lines) * sh_ + 18
    CAP_H = 8 + f_cap.get_height() + 4 + max_sub_lines * (f_caps.get_height() + 1) + 12
    canvas_h = PAD * 2 + TITLE_H + rows * (CELL_H + CAP_H) + (rows - 1) * GAP

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((92, 92, 100))      # neutral mid-tone background per the brief

    yy = PAD
    for ln in title_lines:
        canvas.blit(f_title.render(ln, True, (244, 238, 224)), (PAD, yy))
        yy += th
    yy += 8
    for ln in sub_lines:
        canvas.blit(f_sub.render(ln, True, (210, 212, 218)), (PAD, yy))
        yy += sh_

    y0 = PAD + TITLE_H
    for i, (name, fn) in enumerate(CONCEPTS):
        r, c = divmod(i, cols)
        cx = PAD + c * (CELL_W + GAP)
        cy = y0 + r * (CELL_H + CAP_H + GAP)

        # Crisp K× figure tile: a slightly DARKER backdrop than round 1 so the
        # darkened evolved palette has somewhere to sit, with the matched floor
        # + a contact shadow. The original (cell 0) is drawn at the hero's native
        # scale so it reads small; the evolved concepts are K-scaled to fill.
        tile = pygame.Surface((TILE_W, TILE_H))
        for yyf in range(TILE_H):
            t = yyf / TILE_H
            col = (int(78 - 18 * t), int(76 - 18 * t), int(86 - 16 * t))
            pygame.draw.line(tile, col, (0, yyf), (TILE_W, yyf))
        pygame.draw.rect(tile, (52, 50, 60),
                         (0, GROUND_Y_K, TILE_W, TILE_H - GROUND_Y_K))
        pygame.draw.line(tile, (104, 102, 114), (0, GROUND_Y_K), (TILE_W, GROUND_Y_K),
                         sw(2))
        shsurf = pygame.Surface((TILE_W, s(22)), pygame.SRCALPHA)
        pygame.draw.ellipse(shsurf, (14, 12, 20, 140),
                            (TILE_W // 2 - s(78), 0, s(156), s(22)))
        tile.blit(shsurf, (0, GROUND_Y_K - s(8)))

        # Cell 0 draws the hero at its native fixed-offset scale (so it reads
        # SMALL); the evolved concepts internally multiply geometry by K and so
        # fill the crisp tile. Both anchor to the same K-scaled ground line.
        fn(tile, TILE_W // 2, GROUND_Y_K)

        scaled = tile        # 1:1 blit — no upscale resample
        frame = (236, 196, 90) if i == 0 else (60, 58, 70)
        pygame.draw.rect(canvas, frame,
                         pygame.Rect(cx - 3, cy - 3, CELL_W + 6, CELL_H + 6), 4)
        canvas.blit(scaled, (cx, cy))

        cap = f_cap.render(name, True,
                           (244, 224, 150) if i == 0 else (236, 230, 220))
        canvas.blit(cap, (cx + (CELL_W - cap.get_width()) // 2, cy + CELL_H + 8))
        ly = cy + CELL_H + 8 + f_cap.get_height() + 4
        for ln in sub_wrapped[i]:
            s2 = f_caps.render(ln, True, (198, 200, 208))
            canvas.blit(s2, (cx + (CELL_W - s2.get_width()) // 2, ly))
            ly += f_caps.get_height() + 1

    out_dir = os.path.join("docs", "evolved_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
