"""Look-dev sheet for the Skybit DEVIL boss take B1 — "LIL NICK".

THE storybook cherry-red cartoon devil, played totally straight in chibi: a
round egg-body imp, two short UPTURNED candle-flame horns (never a curved-ram
pair), pointed elf-ears, a pot-belly, stub limbs, a long spade-tipped tail
flicking up behind, and the iconic iron PITCHFORK. The roster's pure cherry-red
anchor — kept SIMPLE so the weirder devils read as deviations off it. No skull
anywhere (the Group-B devil/skull firewall). Scary-cute = pot-bellied, smug,
twirling the fork, a single snaggle-fang and a cheeky wink.

House style this obeys (the warren-clown / Big-Reapy grammar):
  - CHIBI proportions — big head, short wide body, weight-shifted mischief stance.
  - FLAT fills + hard 1-2px ink keylines (28,22,30). No within-shape gradients,
    no soft/feathered edges, no bevels, no realistic shading.
  - Form via the triad: dark-core -> flat fill -> top-left rim sheen. The round
    body + horns read sculpted-but-flat.
  - Silhouette POP via a post-pass 1px dark keyline grown from the alpha mask
    (the parrot/Big-Reapy `_add_outline` recipe).
  - SUPERSAMPLE then smoothscale.

Prop -> pillar mirror: the pitchfork's iron HAFT is the tileable PILLAR BODY (a
banded wrought-iron post with a hard rivet-band rhythm so 2-3 bands stack per
post and survive the 1x downscale); the THREE short iron tines are the
detachable TOP CAP that rides the gap-edge only. A top/bottom mirror reads as a
clean vertical iron post with the trident biting INTO the gap. The tines are
deliberately iron + short + three (vs A3's bone femur fork, B8's slim fire-fork,
B6's neon prongs).

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/render_skybit_devil_lil_nick.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color, make_glow_surface
from game.config import PIPE_W


pygame.init()

# ── "cherry-red devil" palette (take B1) ─────────────────────────────────────
# Cherry-red DOMINANT (the set's ONLY pure red — own it, bold + saturated), a
# crimson shade for the form triad, a warm rose belly/sheen for the lit edge,
# cream candle-flame horns, black spade tail + hooves, gold-iron pitchfork. The
# dark ink keyline + black horn tips carry the silhouette on BOTH skies so the
# warm red never flattens against a warm day sky.
RED        = (214, 44, 40)     # cherry-red body fill
RED_DK     = (150, 26, 28)     # crimson dark-core / fold seat
RED_SHEEN  = (255, 132, 104)   # warm-rose top-left rim sheen
BELLY      = (236, 140, 120)   # skin-pink pot-belly + ear inner + cheek blush
BELLY_DK   = (196, 90, 78)     # belly under-shade seat

HORN       = (248, 222, 160)   # sunny candle-cream horn fill
HORN_DK    = (206, 168, 96)    # horn dark-core / banding
HORN_SHEEN = (255, 248, 214)   # horn rim sheen

SPADE      = (34, 26, 32)      # spade tail / hooves (near-black, own ink family)
SPADE_HI   = (96, 72, 80)      # spade top-left facet

IRON       = (138, 128, 120)   # wrought-iron pitchfork body
IRON_DK    = (78, 70, 68)      # iron dark-core / rivet seat
IRON_HI    = (210, 200, 188)   # iron rim sheen
GOLD       = (228, 182, 64)    # gold ferrule / collar trim
GOLD_HI    = (255, 230, 150)

EYE_WHITE  = (250, 244, 230)   # cream sclera
FANG       = (250, 246, 232)   # snaggle-fang ivory

INK        = (28, 22, 30)      # the house keyline


def _triad_circle(surf, cx, cy, r, col, *, sheen=True):
    """The house form triad on a circle: dark-core ring -> flat fill -> top-left
    rim sheen. Gives the round chibi body sculpted volume while staying flat."""
    pygame.draw.circle(surf, _shade_c(col, -46), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.06))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, 30),
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.34)))


def _add_outline(src, outline_color=(*INK, 235)):
    """Grow a 1px dark keyline from the alpha mask so the silhouette POPS on any
    sky (the parrot/Big-Reapy `_add_outline` recipe). Returns a padded surface."""
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


# ── the upturned candle-flame horns (the unmistakable devil black-read) ───────

def _horn(surf, base_x, base_y, length, hw, ss, *, lean):
    """One short UPTURNED horn: a stubby candle-flame that rises mostly VERTICALLY,
    then hooks back to a sharp inward-upturned point. Deliberately SHORT + upright
    (the set-wide guardrail forbids the outward bull/ram-pair sweep). Triad-lit
    cream with one dark banding groove so it reads as a little horn, not a beak.
    `lean` is the (small) outward bow direction (-1 left horn, +1 right horn)."""
    # Build the horn as a centre-spine of (x, y, half-width) samples, then expand
    # to an outer polygon (dark-core) and a shrunk inner polygon (flat fill) off
    # the SAME spine so the triad can never produce a degenerate ring.
    spine = []
    n = 12
    # Outward bow is cut ~40% off the round-1 sweep (length*0.32 -> length*0.19) so
    # the horn rises near-vertical; the upturn flick is increased so the tip hooks
    # back INWARD into the candle-flame point — never the wide V that reads ram.
    bow = length * 0.19
    for i in range(n + 1):
        t = i / n
        # Bow out only gently in the lower half, then flick the tip back PAST the
        # base line so the point upturns inward (a candle-flame curl, not a spike).
        out = math.sin(min(t, 0.5) / 0.5 * math.pi * 0.5)
        flick = 0.0
        if t > 0.5:
            ft = (t - 0.5) / 0.5
            flick = (ft * ft) * 1.35           # stronger inward hook at the tip
        sx = base_x + lean * (hw * 0.15 + bow * out - bow * flick)
        sy = base_y - length * t
        wgt = hw * (1.0 - 0.82 * t)             # taper to a point
        spine.append((sx, sy, wgt))

    def _horn_poly(shrink, shift):
        left = [(x - max(0.0, w - shrink) + shift, y) for x, y, w in spine]
        right = [(x + max(0.0, w - shrink) + shift, y) for x, y, w in spine]
        return left + right[::-1]

    pygame.draw.polygon(surf, HORN_DK,
                        [(int(x), int(y)) for x, y in _horn_poly(0.0, 0.0)])
    pygame.draw.polygon(surf, HORN,
                        [(int(x), int(y)) for x, y in _horn_poly(ss * 1.2, -lean * ss * 0.4)])
    pts_in = [(x - max(0.0, w - ss) , y) for x, y, w in spine]
    # One dark banding groove low on the horn (candle-flame horn tell).
    band_y = base_y - length * 0.34
    pygame.draw.line(surf, HORN_DK,
                     (int(base_x - lean * hw * 0.1 - hw * 0.7), int(band_y)),
                     (int(base_x - lean * hw * 0.1 + hw * 0.7), int(band_y)),
                     max(1, int(1.6 * ss)))
    # Top-left rim sheen tick along the lit edge.
    pygame.draw.line(surf, HORN_SHEEN,
                     (int(pts_in[1][0]), int(pts_in[1][1])),
                     (int(pts_in[n - 3][0]), int(pts_in[n - 3][1])),
                     max(1, int(1.6 * ss)))


# ── the spade-tipped tail (flicking up behind) ────────────────────────────────

def _spade_tail(surf, root_x, root_y, ss):
    """The long spade-tipped tail looping out behind and flicking UP — the second
    half of the devil black-read. A thin tapering crimson tube ending in a hard
    black SPADE (ace-of-spades), the most iconic non-horn devil cue."""
    n = 16
    pts = []
    for i in range(n + 1):
        t = i / n
        # An S-loop: dips back and down, then sweeps up to flick the spade aloft.
        ang = math.pi * (0.18 + 1.35 * t)
        rad = 46 * ss * (0.5 + 0.5 * t)
        px = root_x + math.cos(ang) * rad
        py = root_y - math.sin(ang) * rad * 0.62 + (1.0 - t) * 10 * ss
        pts.append((px, py))
    # Tapering crimson tube: dark-core stroke -> red fill -> sheen.
    for col, wid in ((RED_DK, 13 * ss), (RED, 8.5 * ss), (RED_SHEEN, 2.4 * ss)):
        for i in range(len(pts) - 1):
            t = i / (len(pts) - 1)
            w = max(1, int(wid * (1.0 - 0.55 * t)))
            a, b = pts[i], pts[i + 1]
            if col is RED_SHEEN:
                a = (a[0], a[1] - ss); b = (b[0], b[1] - ss)
            pygame.draw.line(surf, col, (int(a[0]), int(a[1])),
                             (int(b[0]), int(b[1])), w)
        for px, py in pts[::2]:
            pygame.draw.circle(surf, col, (int(px), int(py)), max(1, int(w * 0.5)))
    # The black spade tip — two lobes + a point, on a short stem (ace of spades).
    tx, ty = pts[-1]
    sw = 16 * ss
    sh = 20 * ss
    spade = [
        (tx, ty - sh * 0.55),                       # top point
        (tx - sw, ty + sh * 0.18),                  # left lobe
        (tx - sw * 0.34, ty + sh * 0.42),
        (tx, ty + sh * 0.30),                       # waist
        (tx + sw * 0.34, ty + sh * 0.42),
        (tx + sw, ty + sh * 0.18),                  # right lobe
    ]
    pygame.draw.polygon(surf, SPADE, [(int(x), int(y)) for x, y in spade])
    # Little stem under the spade.
    pygame.draw.line(surf, SPADE, (int(tx), int(ty + sh * 0.30)),
                     (int(tx), int(ty + sh * 0.62)), max(2, int(3 * ss)))
    # Top-left facet on the spade so the black reads sculpted, not a dead blob.
    pygame.draw.polygon(surf, SPADE_HI, [
        (int(tx), int(ty - sh * 0.42)),
        (int(tx - sw * 0.5), int(ty + sh * 0.05)),
        (int(tx - sw * 0.12), int(ty - sh * 0.02)),
    ])


# ── the chibi devil face ──────────────────────────────────────────────────────

def _devil_face(surf, cx, cy, r, ss):
    """The round cherry-red chibi face: two pointed elf-ears, big cream eyes (one
    winking — the cheeky tell), thick mischief brows, a button nose, a wide smug
    grin with a single snaggle-fang, and a little pointed chin-goatee. Scary-CUTE,
    never grim. Keyed off the head radius `r`."""
    # Pointed elf-ears poking out either side, BEHIND the cheeks.
    for s in (-1, 1):
        ear = [
            (cx + s * r * 0.86, cy - r * 0.10),
            (cx + s * r * 1.34, cy - r * 0.34),
            (cx + s * r * 1.02, cy + r * 0.20),
        ]
        pygame.draw.polygon(surf, RED_DK, [(int(x), int(y)) for x, y in ear])
        inner = [
            (cx + s * r * 0.84, cy - r * 0.08),
            (cx + s * r * 1.20, cy - r * 0.26),
            (cx + s * r * 0.98, cy + r * 0.14),
        ]
        # Ear-inner pink nudged brighter so the pointed elf-ears stay legible
        # against the body mass on the dark night sky.
        pygame.draw.polygon(surf, _shade_c(BELLY, 22),
                            [(int(x), int(y)) for x, y in inner])

    # The round head dome.
    _triad_circle(surf, cx, cy, r, RED)

    # Cheek blush ovals (the cute warmth) — soft rose, low + outward.
    for s in (-1, 1):
        br = pygame.Rect(0, 0, int(r * 0.34), int(r * 0.22))
        br.center = (int(cx + s * r * 0.52), int(cy + r * 0.36))
        pygame.draw.ellipse(surf, BELLY, br)

    # Mischief brows — slim angled wedges lifted clear of the eye so they read as
    # a separate scheming accent at 1x instead of merging into a dark upper band.
    # Thinner + higher than round 1, inner ends still tipped DOWN (gleeful imp).
    for s in (-1, 1):
        bx = cx + s * r * 0.40
        brow = [
            (bx - s * r * 0.26, cy - r * 0.40),
            (bx + s * r * 0.30, cy - r * 0.54),
            (bx + s * r * 0.30, cy - r * 0.46),
            (bx - s * r * 0.26, cy - r * 0.32),
        ]
        pygame.draw.polygon(surf, RED_DK, [(int(x), int(y)) for x, y in brow])

    # Eyes: LEFT is a big open cream eye, RIGHT is a happy closed wink-arc — the
    # cheeky wink is the signature scary-cute beat.
    eye_dx = r * 0.40
    eye_y = cy - r * 0.04
    # Left open eye.
    lx = cx - eye_dx
    pygame.draw.circle(surf, EYE_WHITE, (int(lx), int(eye_y)), int(r * 0.26))
    pygame.draw.circle(surf, INK, (int(lx), int(eye_y)), int(r * 0.26),
                       max(1, int(1.6 * ss)))
    pygame.draw.circle(surf, INK, (int(lx + r * 0.05), int(eye_y + r * 0.02)),
                       int(r * 0.13))                         # pupil
    pygame.draw.circle(surf, EYE_WHITE,
                       (int(lx - r * 0.02), int(eye_y - r * 0.05)),
                       max(1, int(r * 0.05)))                 # catchlight
    # Right wink — a bold bowed-up happy arc. Thicker + wider than round 1 so the
    # closed-eye crescent survives the 1x downscale instead of vanishing to a dot.
    rxc = cx + eye_dx
    pygame.draw.arc(surf, INK,
                    (int(rxc - r * 0.30), int(eye_y - r * 0.12),
                     int(r * 0.60), int(r * 0.42)),
                    math.radians(196), math.radians(344), max(3, int(4.2 * ss)))

    # Button nose — a tiny rose triangle between+below the eyes.
    ny = cy + r * 0.18
    nose = [(cx, ny + r * 0.06), (cx - r * 0.10, ny - r * 0.06),
            (cx + r * 0.10, ny - r * 0.06)]
    pygame.draw.polygon(surf, BELLY_DK, [(int(x), int(y)) for x, y in nose])

    # The smug grin — a wide bowed-UP mouth crescent with one snaggle-fang poking
    # up over the lip. Smug = right corner pulled noticeably higher than the left,
    # asymmetry nudged up from round 1 so it still reads cocky at 1x.
    gy = cy + r * 0.50
    mouth = [
        (cx - r * 0.46, gy),
        (cx, gy + r * 0.22),
        (cx + r * 0.52, gy - r * 0.24),                       # higher right = smug
    ]
    pygame.draw.lines(surf, INK, False,
                      [(int(x), int(y)) for x, y in mouth], max(3, int(3.6 * ss)))
    # Snaggle-fang: an ivory triangle poking UP from the lower lip, off-centre.
    # Enlarged ~30% with a crisp ink keyline so the single tooth survives 1x as a
    # clear scary-cute beat rather than blurring into the mouth line.
    fx = cx - r * 0.17
    fang = [(fx, gy + r * 0.03), (fx - r * 0.10, gy + r * 0.26),
            (fx + r * 0.10, gy + r * 0.26)]
    pygame.draw.polygon(surf, FANG, [(int(x), int(y)) for x, y in fang])
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in fang],
                        max(2, int(1.8 * ss)))

    # Pointed chin-goatee — a tiny dark triangle under the mouth (the classic
    # devil beard), drawn in the spade-black so it groups with horns/tail.
    goat = [(cx, gy + r * 0.30), (cx - r * 0.10, gy + r * 0.18),
            (cx + r * 0.10, gy + r * 0.18)]
    pygame.draw.polygon(surf, SPADE, [(int(x), int(y)) for x, y in goat])


def _devil_body(surf, cx, neck_y, w, h, ss, *, haft_x=None):
    """The short wide chibi body: a round pot-belly torso in cherry-red with a
    rose belly patch, stub arms (one GRIPS the fork haft, one fists on the hip —
    the smug twirl pose), and two little black hooves. Deliberately egg-shaped so
    the big head dominates the chibi read. `haft_x` is the fork-haft centre so the
    right hand lands ON the haft as a clear grip (no floating hand-ball)."""
    belly_cy = neck_y + h * 0.46
    belly_r = w * 0.5
    # Round torso via the triad.
    _triad_circle(surf, cx, belly_cy, belly_r, RED)
    # Pot-belly patch — ONE clean rose oval (no concentric rings) so the body reads
    # bellied rather than target-like and the grayscale body/belly value separates.
    pr = pygame.Rect(0, 0, int(belly_r * 1.06), int(belly_r * 1.18))
    pr.center = (int(cx), int(belly_cy + belly_r * 0.24))
    pygame.draw.ellipse(surf, BELLY, pr)
    # Gold belt cinch at the belly waist (the trim accent + a value break).
    belt = pygame.Rect(0, 0, int(belly_r * 1.7), int(h * 0.16))
    belt.center = (int(cx), int(belly_cy - belly_r * 0.04))
    pygame.draw.rect(surf, _shade_c(GOLD, -54), belt, border_radius=max(2, int(2 * ss)))
    pygame.draw.rect(surf, GOLD, belt.inflate(-int(2 * ss), -int(2 * ss)),
                     border_radius=max(2, int(2 * ss)))
    pygame.draw.circle(surf, GOLD_HI, belt.center, max(1, int(h * 0.04)))

    # Stub arms: LEFT hand fists on the hip (smug), RIGHT grips the fork haft.
    # Left hip arm.
    hipx = cx - belly_r * 0.92
    pygame.draw.line(surf, RED_DK, (int(cx - belly_r * 0.5), int(belly_cy - belly_r * 0.1)),
                     (int(hipx), int(belly_cy + belly_r * 0.18)), max(4, int(7 * ss)))
    pygame.draw.line(surf, RED, (int(cx - belly_r * 0.5), int(belly_cy - belly_r * 0.1)),
                     (int(hipx), int(belly_cy + belly_r * 0.18)), max(2, int(4.5 * ss)))
    _triad_circle(surf, hipx, belly_cy + belly_r * 0.18, w * 0.14, RED)
    # Right arm: a short near-level reach that plants the fist ON the haft so it
    # reads as a confident GRIP (a twirl), not a stiff diagonal to a floating ball.
    grabx = haft_x if haft_x is not None else cx + belly_r * 1.05
    graby = belly_cy - belly_r * 0.10
    sh_x = cx + belly_r * 0.45
    sh_y = belly_cy - belly_r * 0.04
    pygame.draw.line(surf, RED_DK, (int(sh_x), int(sh_y)),
                     (int(grabx), int(graby)), max(4, int(7.5 * ss)))
    pygame.draw.line(surf, RED, (int(sh_x), int(sh_y)),
                     (int(grabx), int(graby)), max(2, int(5 * ss)))
    # The fist closes AROUND the haft — drawn centred on the haft so it wraps it.
    _triad_circle(surf, grabx, graby, w * 0.15, RED)

    # Two little black hooves peeking under the belly (cloven devil feet).
    hoof_y = belly_cy + belly_r * 0.92
    for s in (-1, 1):
        hx = cx + s * belly_r * 0.42
        hr = pygame.Rect(0, 0, int(w * 0.26), int(w * 0.20))
        hr.center = (int(hx), int(hoof_y))
        pygame.draw.ellipse(surf, SPADE, hr)
        pygame.draw.ellipse(surf, SPADE_HI, hr.inflate(-int(4 * ss), -int(hr.h * 0.55)))
        # The cloven split — a hard ink notch up the middle of each hoof.
        pygame.draw.line(surf, INK, (int(hx), int(hoof_y - hr.h * 0.2)),
                         (int(hx), int(hoof_y + hr.h * 0.4)), max(1, int(1.6 * ss)))
    return grabx, graby


# ── the iron pitchfork prop (and its pillar-tile components) ──────────────────

def _iron_haft(surf, cx, top_y, bot_y, hw, ss):
    """The wrought-iron HAFT = the tileable PILLAR BODY: a banded iron post with a
    hard rivet-band rhythm (a gold ferrule ring + dark groove between bands), sized
    so only 2-3 bands stack across a gameplay-height pillar so the banding SURVIVES
    smoothscale instead of washing to a blank grey bar. No tines here; the trident
    head is the detachable top cap."""
    length = bot_y - top_y
    seg_h = max(int(26 * ss), int(hw * 4.2))
    n = max(2, round(length / seg_h))
    seg_h = length / n
    for i in range(n):
        sy = top_y + i * seg_h
        cyb = sy + seg_h * 0.5
        # Dark groove gutter behind the band so neighbours read separated.
        pygame.draw.rect(surf, IRON_DK,
                         (int(cx - hw), int(sy), int(2 * hw), int(seg_h)))
        # The iron band: a fat rounded bar with the form triad.
        band = pygame.Rect(0, 0, int(2 * hw), int(seg_h * 0.84))
        band.center = (int(cx), int(cyb))
        pygame.draw.rect(surf, _shade_c(IRON, -42), band,
                         border_radius=max(2, int(hw * 0.4)))
        pygame.draw.rect(surf, IRON, band.inflate(-int(2 * ss), -int(2 * ss)),
                         border_radius=max(2, int(hw * 0.36)))
        # Top-left rim sheen down the lit edge of the band.
        pygame.draw.line(surf, IRON_HI,
                         (int(cx - hw * 0.55), int(band.top + ss)),
                         (int(cx - hw * 0.55), int(band.bottom - ss)),
                         max(1, int(1.8 * ss)))
        # Gold ferrule ring at each band joint (the rivet-band rhythm).
        fer = pygame.Rect(0, 0, int(2.3 * hw), int(seg_h * 0.16))
        fer.center = (int(cx), int(sy))
        pygame.draw.rect(surf, _shade_c(GOLD, -52), fer,
                         border_radius=max(2, int(fer.h * 0.5)))
        pygame.draw.rect(surf, GOLD, fer.inflate(-int(2 * ss), -int(2 * ss)),
                         border_radius=max(2, int(fer.h * 0.5)))
        pygame.draw.circle(surf, GOLD_HI,
                           (int(cx - hw * 0.4), int(sy)), max(1, int(hw * 0.18)))


def _iron_trident(surf, cx, base_y, hw, ss, *, point_up=True):
    """The THREE short iron tines = the detachable PILLAR TOP CAP that rides the
    gap-edge ONLY. A gold cross-ferrule, then three SHORT straight iron prongs
    (centre tallest, two slightly splayed) each barbed to a sharp point — an iron
    trident, deliberately short + 3-tine (vs A3 bone, B8 fire, B6 neon). Mirrors
    with the haft into a clean vertical iron post that bites INTO the gap.
    `point_up` aims the tines away from the haft (toward the gap)."""
    d = -1 if point_up else 1
    # Gold cross-ferrule binding the head to the haft.
    fer = pygame.Rect(0, 0, int(3.0 * hw), int(11 * ss))
    fer.center = (int(cx), int(base_y))
    pygame.draw.rect(surf, _shade_c(GOLD, -54), fer, border_radius=max(2, int(4 * ss)))
    pygame.draw.rect(surf, GOLD, fer.inflate(-int(2 * ss), -int(2 * ss)),
                     border_radius=max(2, int(4 * ss)))
    pygame.draw.circle(surf, GOLD_HI, (int(cx - hw), int(base_y)), max(1, int(hw * 0.4)))

    # A short crossbar the three tines spring from (the trident yoke).
    yoke_y = base_y + d * 12 * ss
    spread = hw * 2.2
    pygame.draw.line(surf, IRON_DK, (int(cx - spread), int(yoke_y)),
                     (int(cx + spread), int(yoke_y)), max(3, int(7 * ss)))
    pygame.draw.line(surf, IRON, (int(cx - spread), int(yoke_y)),
                     (int(cx + spread), int(yoke_y)), max(2, int(4.5 * ss)))

    # Three short straight prongs: centre tallest, sides splayed + slightly shorter.
    prong_len = 50 * ss
    for k, (off, lenf) in enumerate(((-1, 0.82), (0, 1.0), (1, 0.82))):
        ox = cx + off * spread
        tipx = ox + off * spread * 0.28        # splay the outer tips outward
        tipy = yoke_y + d * prong_len * lenf
        # Iron tine: dark-core -> fill -> sheen, tapering to the barbed point.
        for col, wid in ((IRON_DK, 11 * ss), (IRON, 7 * ss), (IRON_HI, 2 * ss)):
            ax, ay = ox, yoke_y
            bx, by = tipx, tipy
            if col is IRON_HI:
                ax -= ss; bx -= ss
            pygame.draw.line(surf, col, (int(ax), int(ay)), (int(bx), int(by)),
                             max(1, int(wid)))
        # Sharp barbed spear point.
        pygame.draw.polygon(surf, IRON_DK, [
            (int(tipx), int(tipy + d * 9 * ss)),
            (int(tipx - 5 * ss), int(tipy)),
            (int(tipx + 5 * ss), int(tipy)),
        ])
        pygame.draw.polygon(surf, IRON_HI, [
            (int(tipx), int(tipy + d * 7 * ss)),
            (int(tipx - 2 * ss), int(tipy)),
            (int(tipx + 1 * ss), int(tipy)),
        ])


def build_lil_nick(scale=1.0, ss=3):
    """The full boss figure on its own transparent surface. Big head ~46% of total
    height, short wide pot-belly below, fork held tall at the figure's right.
    Returns an outlined surface and its baseline (feet) y for placement."""
    H = int(250 * scale)
    W = int(150 * scale)
    pad = int(80 * scale)
    surf = pygame.Surface(((W + pad * 2) * ss, (H + pad) * ss), pygame.SRCALPHA)
    cx = (W // 2 + pad) * ss

    head_band = int(H * 0.46) * ss
    head_r = head_band * 0.46
    head_cx = cx
    head_cy = int(pad * 0.55) * ss + head_r

    # Body below the head.
    neck_y = head_cy + head_r * 0.78
    body_w = W * 0.66 * ss
    body_h = int(H * 0.46) * ss
    belly_cy = neck_y + body_h * 0.46
    belly_r = body_w * 0.5
    feet_y = belly_cy + belly_r * 0.92 + W * 0.06 * ss

    # Tail rooted at the lower-left of the belly, flicking up behind.
    _spade_tail(surf, head_cx - belly_r * 0.7, belly_cy + belly_r * 0.5, ss)

    # Pitchfork held upright at the figure's right; haft runs past the feet, the
    # trident head rises above the head (twirled aloft).
    bx = cx + W * 0.48 * ss
    bhw = 6.5 * ss
    head_top = head_cy - head_r * 1.05
    _iron_haft(surf, bx, head_top, feet_y + 6 * ss, bhw, ss)
    _iron_trident(surf, bx, head_top, bhw, ss, point_up=True)

    # Body (its right fist grips the haft just drawn), then horns (behind the head
    # dome top), then face on top.
    _devil_body(surf, head_cx, neck_y, body_w, body_h, ss, haft_x=bx)
    # Two short upturned horns springing from the top of the head, bases pulled
    # closer together so the upright pair reads as a tight candle-flame V, never
    # the wide outward span of bull/ram horns.
    horn_len = head_r * 0.96
    horn_hw = head_r * 0.21
    _horn(surf, head_cx - head_r * 0.32, head_cy - head_r * 0.90, horn_len, horn_hw, ss, lean=-1)
    _horn(surf, head_cx + head_r * 0.32, head_cy - head_r * 0.90, horn_len, horn_hw, ss, lean=1)
    _devil_face(surf, head_cx, head_cy, head_r, ss)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallsurf = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallsurf), feet_y / ss


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _pitchfork_pillar_obstacle(height, ss, *, flip):
    """One pitchfork PILLAR obstacle: the iron haft fills the post, the trident cap
    sits at the gap end. `flip` makes the top pillar's tines point DOWN into the
    gap; the bottom pillar's tines point UP — proving the prop mirrors top<->bottom
    into a clean vertical iron post with the trident biting into the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    hw = 9 * ss
    cap_band = int(72 * ss)
    _iron_haft(surf, cx, 0, bh - cap_band, hw, ss)
    _iron_trident(surf, cx, bh - cap_band, hw, ss, point_up=False)
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
    sheet.fill((34, 30, 38))
    _label(sheet, font, "LIL NICK  —  take B1  —  cherry-red storybook devil  —  round 2", 18, 12)
    _label(sheet, small,
            "the canonical chibi red imp: round egg-body, short UPTURNED candle-horns, elf-ears, spade tail, iron pitchfork  (Group-B RED anchor)",
            18, 32, (210, 196, 200))

    # — Cell A: boss at showcase scale, on a neutral panel.
    panel = pygame.Rect(18, 56, 360, 590)
    pygame.draw.rect(sheet, (52, 46, 56), panel, border_radius=8)
    pygame.draw.rect(sheet, (104, 90, 96), panel, 2, border_radius=8)
    boss, _ = build_lil_nick(scale=1.75, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.bottom - boss.get_height() - 16))
    _label(sheet, font, "(a) BOSS  showcase scale", panel.x + 8, panel.y + 8)
    _label(sheet, small, "upright candle-horns, fist GRIPS haft, 1-oval belly",
           panel.x + 8, panel.y + 28, (210, 196, 200))

    # — Cell B: the pitchfork as a tileable PILLAR pair at TRUE obstacle scale.
    panelB = pygame.Rect(394, 56, 360, 590)
    bg = _sky(panelB.w, panelB.h, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (104, 90, 96), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE obstacle scale", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG                  # 82px — the real obstacle width
    slice_h = 500
    slice_x = panelB.x + 26
    slice_y = panelB.y + 46
    gap_top = 178
    gap_h = 120
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _pitchfork_pillar_obstacle(top_h, 3, flip=True)
    bot_pillar = _pitchfork_pillar_obstacle(bot_h, 3, flip=False)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (255, 255, 255), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px wide, as", slice_x - 2, slice_y + slice_h + 6, (20, 20, 30))
    _label(sheet, small, "it scrolls): banded iron haft,", slice_x - 2, slice_y + slice_h + 22, (20, 20, 30))
    _label(sheet, small, "trident cap bites into the gap", slice_x - 2, slice_y + slice_h + 38, (20, 20, 30))

    # 2x zoom of just the GAP region so the trident + banding detail is legible.
    zw, zh = pw, 156
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    zoom_src.blit(top_pillar, (-2, -(gap_top - 76) - 2))
    zoom_src.blit(bot_pillar, (-2, gap_h + 76 - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 188
    zy = panelB.y + 64
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the gap:", zx - 4, zy - 16, (255, 255, 255))
    _label(sheet, small, "3 short iron tines +", zx - 4, zy + zh * 2 + 6, (20, 20, 30))
    _label(sheet, small, "gold ferrule; top<->bottom", zx - 4, zy + zh * 2 + 22, (20, 20, 30))
    _label(sheet, small, "mirror to a clean post", zx - 4, zy + zh * 2 + 38, (20, 20, 30))

    # — Cell C: 1x in-game-scale INSET on BOTH day and night skies.
    panelC = pygame.Rect(770, 56, 392, 590)
    pygame.draw.rect(sheet, (52, 46, 56), panelC, border_radius=8)
    pygame.draw.rect(sheet, (104, 90, 96), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) 1x in-game scale  —  day / night legibility", panelC.x + 8, panelC.y + 8)

    boss1x, _ = build_lil_nick(scale=0.70, ss=3)
    day = _sky(180, 270, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    night = _sky(180, 270, (5, 8, 30), (15, 25, 70), (35, 55, 115))
    for sx, sy in ((24, 40), (150, 26), (96, 70), (40, 120), (160, 150), (70, 220), (130, 250)):
        pygame.draw.circle(night, (220, 230, 255), (sx, sy), 1)

    dy = panelC.y + 40
    sheet.blit(day, (panelC.x + 14, dy))
    sheet.blit(night, (panelC.x + 200, dy))
    sheet.blit(boss1x, (panelC.x + 14 + 90 - boss1x.get_width() // 2,
                        dy + 270 - boss1x.get_height() - 6))
    sheet.blit(boss1x, (panelC.x + 200 + 90 - boss1x.get_width() // 2,
                        dy + 270 - boss1x.get_height() - 6))
    _label(sheet, small, "DAY", panelC.x + 14 + 6, dy + 6, (20, 20, 30))
    _label(sheet, small, "NIGHT", panelC.x + 200 + 6, dy + 6, (210, 220, 255))

    # — Grayscale silhouette check: the devil read (horns/spade/fork) must carry
    #   without the red — the dark horn tips, spade tail + ink keyline do the work.
    gy = dy + 290
    gray = pygame.Surface((boss1x.get_width(), boss1x.get_height()), pygame.SRCALPHA)
    gray.blit(boss1x, (0, 0))
    arr = pygame.surfarray.pixels3d(gray)
    lum = (arr[:, :, 0] * 0.3 + arr[:, :, 1] * 0.59 + arr[:, :, 2] * 0.11).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    gpanel = pygame.Rect(panelC.x + 14, gy, 360, 248)
    pygame.draw.rect(sheet, (120, 118, 122), gpanel, border_radius=6)
    sheet.blit(gray, (gpanel.centerx - gray.get_width() // 2,
                      gpanel.bottom - gray.get_height() - 8))
    _label(sheet, small, "grayscale: horns + spade-tail + fork silhouette read the devil without the red",
            gpanel.x + 6, gpanel.y + 6, (30, 30, 30))

    # — Footer caption.
    _label(sheet, small,
           "scary-cute: pot-bellied + smug, twirling the fork; a cheeky WINK + a single snaggle-fang — gleeful imp, never grim.",
           18, SH - 86, (210, 200, 206))
    _label(sheet, small,
           "house style: FLAT fills, hard ink keyline grown from the alpha mask, dark-core->fill->top-left-sheen triad, ss=3 -> smoothscale.",
           18, SH - 66, (210, 200, 206))
    _label(sheet, small,
           "guardrails: horns are SHORT upturned points (no ram pair); iron + 3-short tines distinct from A3 bone / B8 fire / B6 neon forks.",
           18, SH - 46, (210, 200, 206))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "devil", "lil_nick")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
