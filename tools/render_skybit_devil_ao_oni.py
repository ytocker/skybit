"""Look-dev sheet for the Skybit DEVIL-boss Group-B take #4 — "AO-ONI".

A sulky cobalt-BLUE Japanese oni: a heavy broad sumo-slab body (the set's
max mass-contrast — opposite mass-language to B1's egg and B8's pear), two
ivory tusks jutting UP from the lower jaw, a single stubby OX horn + wild
topknot, thick angry brows over a big grumpy lower-lip pout, a tiger-stripe
loincloth, and a studded iron KANABO club gripped in one fist. The brawler
devil; deliberately cool-cobalt so it owns the BLUE lane against the reds.

House style this obeys (the warren-clown / Big-Reapy grammar):
  - CHIBI proportions, but built RECTANGULAR/HEAVY: a low wide centre of
    gravity (huge square shoulders, tiny legs) — its own mass-language.
  - FLAT fills + hard 1-2px ink keylines (20,22,34). No within-shape
    gradients, no soft edges, no bevels, no realism.
  - Form via the triad: dark-core -> flat fill -> top-left rim sheen, so the
    slab reads sculpted-but-flat (the cobalt body, the iron club drum).
  - Silhouette POP via a post-pass 1px ink keyline grown from the alpha mask
    (the parrot `_add_outline` recipe).
  - SUPERSAMPLE then smoothscale.

Set guardrails honoured: (1) the OX horn is short + stubby, NOT a curved-ram
pair (no ram horns survive anywhere in the set); the tusks point UP and are
ivory, distinct from any horn primitive. (2) Cobalt-blue + ivory + tiger-gold
is its own palette; no other devil is blue.

Prop -> pillar mirror: the studded KANABO is the tileable PILLAR BODY — a fat
iron shaft whose rivet STUDS band the shaft in repeatable rows (the most
rivet-readable post in the set), so a top/bottom mirror reads as a clean iron
post with the bulbous spiked club-HEAD as the detachable gap-edge cap.

Imports the real game colour/shape kit only; nothing under game/ is touched.
Headless + deterministic.

    SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python tools/render_skybit_devil_ao_oni.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.draw import _shade_c, lerp_color
from game.config import PIPE_W


pygame.init()

# ── "cobalt-oni & tiger-gold" palette (take B4) ──────────────────────────────
# Cobalt-blue DOMINANT (bold + saturated, never a grey realistic ogre); deep
# indigo as the dark-core/shade anchor that holds the slab on a BRIGHT day sky;
# a sky-blue top-left sheen; ivory tusks + topknot tie; tiger-gold loincloth as
# the one warm accent that pops the blue; iron-grey kanabo. The dark ink mask +
# brow SHAPE must read in grayscale too — colour is never the only cue.
COBALT      = (54,  96, 176)    # oni-skin fill
COBALT_DK   = (30,  56, 122)    # dark-core ring / muscle grooves
COBALT_SHADE= (38,  62, 128)    # deep-indigo seat under the slab
SKY_SHEEN   = (122, 162, 224)   # top-left rim sheen
SKY_SHEEN_HI= (170, 202, 248)   # brightest rim tick

IVORY       = (238, 232, 210)   # tusks / topknot tie / claws
IVORY_DK    = (188, 178, 148)   # tusk dark-core seat
IVORY_SHEEN = (255, 250, 234)   # tusk rim sheen

HAIR        = (28,  30,  52)    # wild blue-black topknot
HAIR_HI     = (58,  66,  104)   # hair top-left sheen

HORN        = (210, 168,  86)   # ox stub-horn (warm bone-amber, NOT ivory)
HORN_DK     = (150, 112,  52)
HORN_HI     = (244, 210, 140)

TIGER       = (228, 168,  52)   # tiger-gold loincloth
TIGER_DK    = (176, 120,  28)
TIGER_STRIPE= (40,  30,  22)    # loincloth black stripes

IRON        = (108, 116, 134)   # kanabo club body
IRON_DK     = (60,  66,  84)    # iron dark-core / groove
IRON_SHEEN  = (172, 182, 202)   # iron top-left sheen
RIVET       = (224, 230, 244)   # bright stud highlight (pushed up for 1x punch)
RIVET_DK    = (28,  32,  46)    # stud seat ring (pushed down so the dome pops)
GROOVE      = (40,  44,  58)    # full-width dark band between rivet rows

MOUTH       = (90,  30,  46)    # sulky open-mouth interior (dark plum)
LIP         = (96,  150, 214)   # the pouting lower lip (lighter cobalt)

INK         = (20,  22,  34)    # the house keyline


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


def _triad_rrect(surf, rect, rad, col, ss, *, sheen=True):
    """The house form triad on a rounded rect: dark-core ring -> flat fill ->
    top-left rim sheen. The slab's flesh primitive (square + soft corners)."""
    pygame.draw.rect(surf, _shade_c(col, -42), rect, border_radius=rad)
    inner = rect.inflate(-int(2.4 * ss), -int(2.4 * ss))
    pygame.draw.rect(surf, col, inner, border_radius=max(1, rad - int(ss)))
    if sheen:
        # A top-left sheen wedge tucked inside the upper-left corner.
        sh = pygame.Rect(0, 0, int(rect.w * 0.42), int(rect.h * 0.30))
        sh.topleft = (rect.x + int(3 * ss), rect.y + int(3 * ss))
        pygame.draw.rect(surf, _shade_c(col, 26), sh,
                         border_radius=max(1, rad - int(ss)))


def _triad_circle(surf, cx, cy, r, col, *, sheen=True):
    pygame.draw.circle(surf, _shade_c(col, -42), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)),
                       max(1, int(r - max(1, r * 0.08))))
    if sheen:
        pygame.draw.circle(surf, _shade_c(col, 26),
                           (int(cx - r * 0.32), int(cy - r * 0.34)),
                           max(2, int(r * 0.34)))


# ── the sumo-slab body ───────────────────────────────────────────────────────

def _slab_body(surf, cx, top_y, w, h, ss):
    """The heavy broad sumo-slab: HUGE square shoulders tapering only slightly to
    a wide belly, sat on two stubby legs — a low wide centre of gravity that is
    the figure's whole mass-language. Two thick arms; the right grips the kanabo
    (drawn by the caller), the left is a stub fist. Tiger-gold loincloth wraps
    the lower slab. Cobalt triad throughout. Returns the right-fist grip point."""
    # Stubby legs first (behind the slab so the belly overhangs them).
    leg_y = top_y + h
    for s in (-1, 1):
        lx = cx + s * w * 0.30
        leg = pygame.Rect(0, 0, int(w * 0.30), int(h * 0.26))
        leg.midtop = (int(lx), int(leg_y - h * 0.10))
        _triad_rrect(surf, leg, max(2, int(w * 0.10)), COBALT, ss)
        # Tiny three-claw foot.
        for k in (-1, 0, 1):
            fx = lx + k * w * 0.07
            pygame.draw.circle(surf, IVORY_DK,
                               (int(fx), int(leg.bottom)), max(1, int(2.2 * ss)))
            pygame.draw.circle(surf, IVORY,
                               (int(fx), int(leg.bottom - ss)), max(1, int(1.5 * ss)))

    # The slab torso: a broad rounded rectangle, widest at the shoulders.
    torso = pygame.Rect(0, 0, int(w * 1.06), int(h * 0.92))
    torso.midtop = (int(cx), int(top_y))
    _triad_rrect(surf, torso, max(3, int(w * 0.16)), COBALT, ss)

    # Big square shoulder caps bulging past the torso so the read is BROAD —
    # max shoulder mass is the silhouette signature.
    for s in (-1, 1):
        sh = pygame.Rect(0, 0, int(w * 0.40), int(h * 0.40))
        sh.center = (int(cx + s * w * 0.50), int(top_y + h * 0.14))
        _triad_rrect(surf, sh, max(3, int(w * 0.18)), COBALT, ss)

    # Pec / belly muscle grooves — two bold dark-core seams so the slab reads
    # as a heavy torso, not a flat box (kept few + bold to survive 1x).
    pygame.draw.line(surf, COBALT_DK,
                     (int(cx), int(top_y + h * 0.18)),
                     (int(cx), int(top_y + h * 0.50)), max(1, int(2 * ss)))
    pygame.draw.arc(surf, COBALT_DK,
                    (int(cx - w * 0.34), int(top_y + h * 0.06),
                     int(w * 0.68), int(h * 0.40)),
                    math.radians(202), math.radians(338), max(1, int(2 * ss)))
    # A round belly dimple (cute heft tell).
    pygame.draw.circle(surf, COBALT_DK, (int(cx), int(top_y + h * 0.58)),
                       max(1, int(2.2 * ss)))

    # — Arms: two thick stubby cobalt arms. Left = a resting fist; the right grip
    #   point is returned for the kanabo. Built fat + short = heft, not reach.
    arm_y = top_y + h * 0.22
    # Left arm + fist.
    lax = cx - w * 0.62
    pygame.draw.line(surf, COBALT_DK, (int(cx - w * 0.46), int(arm_y)),
                     (int(lax), int(arm_y + h * 0.30)), max(5, int(9 * ss)))
    pygame.draw.line(surf, COBALT, (int(cx - w * 0.46), int(arm_y)),
                     (int(lax), int(arm_y + h * 0.30)), max(3, int(6 * ss)))
    _triad_circle(surf, lax, arm_y + h * 0.30, w * 0.17, COBALT)
    # Right arm (toward the club) — drawn here so the club fist overlaps it.
    rax = cx + w * 0.64
    ray = arm_y + h * 0.10
    pygame.draw.line(surf, COBALT_DK, (int(cx + w * 0.46), int(arm_y)),
                     (int(rax), int(ray)), max(5, int(9 * ss)))
    pygame.draw.line(surf, COBALT, (int(cx + w * 0.46), int(arm_y)),
                     (int(rax), int(ray)), max(3, int(6 * ss)))

    # — Tiger-gold loincloth: a wide gold belt-wrap with a knotted side-tie and
    #   bold black tiger stripes (the one warm accent). Sits low on the slab.
    belt_y = top_y + h * 0.66
    belt = pygame.Rect(0, 0, int(w * 1.02), int(h * 0.26))
    belt.midtop = (int(cx), int(belt_y))
    pygame.draw.rect(surf, TIGER_DK, belt, border_radius=max(2, int(ss * 2)))
    pygame.draw.rect(surf, TIGER, belt.inflate(-int(2 * ss), -int(2 * ss)),
                     border_radius=max(2, int(ss * 2)))
    # Tiger stripes — short bold black chevrons along the belt.
    for i in range(6):
        t = (i + 0.5) / 6
        sx = belt.x + int(belt.w * t)
        pygame.draw.line(surf, TIGER_STRIPE,
                         (sx, belt.y + int(belt.h * 0.18)),
                         (sx + int(3 * ss), belt.y + int(belt.h * 0.82)),
                         max(1, int(2.4 * ss)))
    # A knotted hanging tab on the right hip.
    tab = pygame.Rect(0, 0, int(w * 0.22), int(h * 0.22))
    tab.midtop = (int(cx + w * 0.32), int(belt.bottom - ss))
    pygame.draw.polygon(surf, TIGER_DK, [
        (tab.left, tab.top), (tab.right, tab.top),
        (tab.centerx + int(3 * ss), tab.bottom), (tab.centerx - int(3 * ss), tab.bottom)])
    pygame.draw.polygon(surf, TIGER, [
        (tab.left + int(ss), tab.top + int(ss)), (tab.right - int(ss), tab.top + int(ss)),
        (tab.centerx + int(2 * ss), tab.bottom - int(ss)),
        (tab.centerx - int(2 * ss), tab.bottom - int(ss))])

    return rax, ray


# ── the broad scowling oni head ──────────────────────────────────────────────

def _oni_head(surf, cx, cy, r, ss, *, night=False):
    """The broad oni head: wider-than-tall so it reads SUMO-heavy, thick angry
    brows, two big eyes, a single short OX stub-horn, a wild topknot, and the
    scary-CUTE signature — a big sulky lower-lip POUT with two ivory tusks
    jutting UP from it. `night` lifts a faint sky rim so the cobalt reads on a
    dark sky. The brow + tusk SHAPE carries the read in grayscale."""
    hw = r * 1.18                     # head is wider than tall
    hh = r * 0.98

    # — One bold topknot FIRST so the head overlaps it. Simplified to a single
    #   decisive blue-black bulb with 3 confident spikes + an ivory tie band — the
    #   crowd of side tufts is gone so the head reads clean at 1x and the amber
    #   ox-horn stays clearly separate from the hair mass.
    knot_cx = cx
    knot_cy = cy - hh * 0.90
    knot_r = r * 0.50
    # The topknot bulb on top (bigger + bolder than the fiddly r1 ball).
    pygame.draw.circle(surf, HAIR, (int(knot_cx), int(knot_cy)), int(knot_r))
    pygame.draw.circle(surf, HAIR_HI,
                       (int(knot_cx - knot_r * 0.32), int(knot_cy - knot_r * 0.36)),
                       int(knot_r * 0.34))
    # Three decisive spikes bursting from the knot (fewer + thicker than r1).
    for ang in (-46, 0, 46):
        a = math.radians(ang - 90)
        tx = knot_cx + math.cos(a) * knot_r * 0.7
        ty = knot_cy + math.sin(a) * knot_r * 0.7
        ex = knot_cx + math.cos(a) * knot_r * 1.7
        ey = knot_cy + math.sin(a) * knot_r * 1.7
        pygame.draw.line(surf, HAIR, (int(tx), int(ty)), (int(ex), int(ey)),
                         max(3, int(6 * ss)))
    # Ivory tie band around the knot base.
    band = pygame.Rect(0, 0, int(r * 0.5), int(r * 0.22))
    band.center = (int(knot_cx), int(knot_cy + knot_r * 0.62))
    pygame.draw.rect(surf, IVORY_DK, band, border_radius=max(1, int(ss)))
    pygame.draw.rect(surf, IVORY, band.inflate(-int(2 * ss), -int(2 * ss)),
                     border_radius=max(1, int(ss)))

    # — The single OX stub-horn: a BOLD, blunt, fat amber NUB set out on the brow
    #   ridge, clearly SEPARATE from the topknot so it reads as a horn (not a hair
    #   tuft) in colour AND grayscale (the "one short ox horn, no ram pair"
    #   guardrail). Fattened + given a dark seat ring + bright cap so the eye
    #   catches it at a glance and the value carries with no colour.
    hx = cx - hw * 0.62
    hy = cy - hh * 0.66
    hwid = r * 0.30                   # fat: a stub nub wider than a finger
    hht = r * 0.46
    # Dark seat ring at the base so the nub reads as a separate growth.
    pygame.draw.ellipse(surf, HORN_DK,
                        (int(hx - hwid * 1.18), int(hy + hht * 0.30),
                         int(hwid * 2.36), int(hht * 0.62)))
    horn = [
        (hx - hwid, hy + hht * 0.52),
        (hx + hwid, hy + hht * 0.52),
        (hx + hwid * 0.42, hy - hht * 0.52),
        (hx - hwid * 0.42, hy - hht * 0.52),
    ]
    pygame.draw.polygon(surf, HORN_DK, [(int(x), int(y)) for x, y in horn])
    inner = [(hx - hwid * 0.74, hy + hht * 0.48), (hx + hwid * 0.78, hy + hht * 0.48),
             (hx + hwid * 0.30, hy - hht * 0.42), (hx - hwid * 0.26, hy - hht * 0.42)]
    pygame.draw.polygon(surf, HORN, [(int(x), int(y)) for x, y in inner])
    # Blunt rounded cap (ox stub, never a sharp ram point).
    pygame.draw.circle(surf, HORN,
                       (int(hx + hwid * 0.02), int(hy - hht * 0.42)),
                       max(2, int(hwid * 0.42)))
    pygame.draw.circle(surf, HORN_HI,
                       (int(hx - hwid * 0.16), int(hy - hht * 0.48)),
                       max(1, int(hwid * 0.26)))
    # A left-edge sheen + ridge groove so the blunt stub reads sculpted ox-horn.
    pygame.draw.line(surf, HORN_HI, (int(hx - hwid * 0.34), int(hy + hht * 0.30)),
                     (int(hx - hwid * 0.16), int(hy - hht * 0.30)), max(1, int(2 * ss)))
    pygame.draw.line(surf, HORN_DK, (int(hx + hwid * 0.20), int(hy + hht * 0.34)),
                     (int(hx + hwid * 0.30), int(hy - hht * 0.30)), max(1, int(1.4 * ss)))

    # — Head flesh: a broad rounded-square so the face reads heavy + jowly.
    head = pygame.Rect(0, 0, int(hw * 2), int(hh * 2))
    head.center = (int(cx), int(cy))
    _triad_rrect(surf, head, max(4, int(r * 0.42)), COBALT, ss)
    # Two jowl cheeks bulging at the lower sides (sumo heft).
    for s in (-1, 1):
        pygame.draw.circle(surf, _shade_c(COBALT, -10),
                           (int(cx + s * hw * 0.74), int(cy + hh * 0.40)),
                           int(r * 0.30))
        pygame.draw.circle(surf, COBALT,
                           (int(cx + s * hw * 0.74 - s * ss), int(cy + hh * 0.40 - ss)),
                           int(r * 0.24))

    if night:
        # No additive halo — it washed the head to pale cyan and KILLED the
        # cobalt. Instead a crisp cool rim-sheen ticks the upper-left slab edge so
        # the body stays unmistakably COBALT against the dark sky (a sharp lit
        # contour, not a glow). Drawn as a bright arc hugging the head silhouette.
        rim = head.inflate(-int(2 * ss), -int(2 * ss))
        pygame.draw.arc(surf, SKY_SHEEN_HI, rim,
                        math.radians(78), math.radians(196), max(2, int(2.6 * ss)))
        pygame.draw.arc(surf, SKY_SHEEN, rim,
                        math.radians(196), math.radians(252), max(2, int(2.0 * ss)))

    # — Thick angry BROWS: two heavy ivory-pale ridges slanting down toward the
    #   nose (the inner-down V = scowl), the grayscale-legible menace cue. Drawn
    #   as fat cobalt-dark wedges with a pale top edge.
    brow_y = cy - hh * 0.18
    for s in (-1, 1):
        # Thicker + darker than r1 so the inner-down scowl is the face's loudest
        # cue and survives the 1x downscale.
        b = [
            (cx + s * hw * 0.18, brow_y + r * 0.04),     # inner (low)
            (cx + s * hw * 0.78, brow_y - r * 0.34),     # outer (high)
            (cx + s * hw * 0.78, brow_y - r * 0.06),
            (cx + s * hw * 0.18, brow_y + r * 0.26),
        ]
        pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in b])
        pygame.draw.line(surf, _shade_c(COBALT, 18),
                         (int(cx + s * hw * 0.22), int(brow_y - r * 0.02)),
                         (int(cx + s * hw * 0.72), int(brow_y - r * 0.30)),
                         max(1, int(2.4 * ss)))

    # — Eyes: big round whites with a small dark pupil aimed slightly together +
    #   down (sulky, not a piercing glare) under the heavy brows. Big round eyes
    #   on the broad head = the cute lever.
    eye_dx = hw * 0.46
    eye_y = cy + r * 0.02
    eye_r = r * 0.26
    for s in (-1, 1):
        ex = cx + s * eye_dx
        pygame.draw.circle(surf, INK, (int(ex), int(eye_y)), int(eye_r + ss))
        pygame.draw.circle(surf, IVORY, (int(ex), int(eye_y)), int(eye_r))
        # Pupil low + inward = grumpy sulk.
        pupil = (int(ex - s * eye_r * 0.20), int(eye_y + eye_r * 0.30))
        pygame.draw.circle(surf, INK, pupil, max(2, int(eye_r * 0.46)))
        pygame.draw.circle(surf, IVORY_SHEEN,
                           (int(ex - s * eye_r * 0.34), int(eye_y - eye_r * 0.30)),
                           max(1, int(eye_r * 0.18)))

    # — Flat broad nose (two nostril dots on a soft bump) between the eyes.
    nose_y = cy + r * 0.36
    pygame.draw.ellipse(surf, _shade_c(COBALT, -22),
                        (int(cx - r * 0.22), int(nose_y - r * 0.10),
                         int(r * 0.44), int(r * 0.26)))
    for s in (-1, 1):
        pygame.draw.circle(surf, INK,
                           (int(cx + s * r * 0.10), int(nose_y + r * 0.04)),
                           max(1, int(2.2 * ss)))

    # — The sulky POUT + UP-tusks: the scary-CUTE signature. A wide downturned
    #   lower lip pushes out below the mouth; from behind it, two fat ivory tusks
    #   curve UP past the upper lip. A dark open-mouth crescent sits above the lip.
    mouth_y = cy + hh * 0.56
    mouth_w = hw * 0.78
    # Dark mouth interior — a downturned frown crescent.
    seat = [
        (cx - mouth_w * 0.5, mouth_y - r * 0.04),
        (cx, mouth_y + r * 0.18),
        (cx + mouth_w * 0.5, mouth_y - r * 0.04),
        (cx + mouth_w * 0.42, mouth_y + r * 0.10),
        (cx, mouth_y + r * 0.30),
        (cx - mouth_w * 0.42, mouth_y + r * 0.10),
    ]
    pygame.draw.polygon(surf, MOUTH, [(int(x), int(y)) for x, y in seat])
    # The pouting lower lip — a fat lighter-cobalt lozenge pushed out + down.
    lip = pygame.Rect(0, 0, int(mouth_w * 0.92), int(r * 0.36))
    lip.center = (int(cx), int(mouth_y + r * 0.34))
    pygame.draw.ellipse(surf, _shade_c(LIP, -34), lip)
    pygame.draw.ellipse(surf, LIP, lip.inflate(-int(2 * ss), -int(2 * ss)))
    pygame.draw.line(surf, SKY_SHEEN_HI,
                     (int(lip.left + lip.w * 0.2), int(lip.centery)),
                     (int(lip.left + lip.w * 0.5), int(lip.centery)), max(1, int(1.6 * ss)))

    # Two ivory tusks jutting UP from the lower jaw, past the upper lip — the
    # unmistakable oni read. Fat triad-lit ivory cones curving slightly inward.
    for s in (-1, 1):
        bx = cx + s * mouth_w * 0.30
        base_y = mouth_y + r * 0.14
        tip = (bx - s * r * 0.06, base_y - r * 0.46)
        tusk = [
            (bx - r * 0.13, base_y),
            (bx + r * 0.13, base_y),
            (tip[0] + r * 0.04, tip[1]),
            (tip[0] - r * 0.04, tip[1]),
        ]
        pygame.draw.polygon(surf, IVORY_DK, [(int(x), int(y)) for x, y in tusk])
        innt = [(bx - r * 0.08, base_y - ss), (bx + r * 0.08, base_y - ss),
                (tip[0] + r * 0.02, tip[1] + ss), (tip[0] - r * 0.02, tip[1] + ss)]
        pygame.draw.polygon(surf, IVORY, [(int(x), int(y)) for x, y in innt])
        pygame.draw.line(surf, IVORY_SHEEN,
                         (int(bx - r * 0.05), int(base_y - r * 0.04)),
                         (int(tip[0] - r * 0.02), int(tip[1] + r * 0.04)),
                         max(1, int(1.6 * ss)))


# ── the studded KANABO club (and its pillar-tile components) ──────────────────

def _kanabo_shaft(surf, cx, top_y, bot_y, hw, ss):
    """The iron shaft = the tileable PILLAR BODY: a fat iron post BANDED with
    repeatable rows of rivet STUDS. The studs are the signature — bold, high-
    contrast hemispheres in regular rows so the rivet banding SURVIVES smoothscale
    instead of washing to a blank grey bar (the kanabo's whole point). No club
    head here; the spiked head is the detachable cap."""
    length = bot_y - top_y
    # Iron post body with the triad.
    post = pygame.Rect(int(cx - hw), int(top_y), int(2 * hw), int(length))
    pygame.draw.rect(surf, IRON_DK, post, border_radius=max(2, int(hw * 0.32)))
    pygame.draw.rect(surf, IRON, post.inflate(-int(2 * ss), 0),
                     border_radius=max(2, int(hw * 0.30)))
    # Top-left sheen strip so the iron reads cylindrical + lit.
    pygame.draw.line(surf, IRON_SHEEN,
                     (int(cx - hw * 0.46), int(top_y + 3 * ss)),
                     (int(cx - hw * 0.46), int(bot_y - 3 * ss)), max(2, int(2.4 * ss)))

    # Rivet rows: FEWER, BIGGER, higher-contrast studs so the banding reads as
    # rhythm at 1x instead of washing to a blank grey bar (the rivet rows ARE the
    # pillar's identity). Now the shaft is fat, three big studs straddle each row.
    # Row pitch is generous so the rows stay distinct after the 1x downscale.
    row_pitch = max(int(26 * ss), int(hw * 0.92))
    n_rows = max(2, int(round(length / row_pitch)))
    row_pitch = length / n_rows
    stud_r = hw * 0.30
    cols = (-0.58, 0.0, 0.58)
    for i in range(n_rows):
        ry = top_y + (i + 0.5) * row_pitch
        # A FULL-WIDTH dark groove band between every row so the banding is a
        # bold rhythm that survives smoothscale — not a faint hairline.
        band_y = ry - row_pitch * 0.5
        band = pygame.Rect(int(cx - hw + 1.5 * ss), int(band_y - 2.2 * ss),
                           int(2 * hw - 3 * ss), max(2, int(4.4 * ss)))
        pygame.draw.rect(surf, GROOVE, band, border_radius=max(1, int(ss)))
        for f in cols:
            sx = cx + f * hw
            # Seat ring -> bright dome -> dark contact shadow -> hot pinprick: a
            # high-contrast riveted hemisphere that survives the downscale.
            pygame.draw.circle(surf, RIVET_DK, (int(sx), int(ry)), int(stud_r + 1.4 * ss))
            pygame.draw.circle(surf, IRON_SHEEN, (int(sx), int(ry)), int(stud_r))
            pygame.draw.circle(surf, IRON_DK,
                               (int(sx + stud_r * 0.34), int(ry + stud_r * 0.40)),
                               max(1, int(stud_r * 0.42)))
            pygame.draw.circle(surf, RIVET,
                               (int(sx - stud_r * 0.30), int(ry - stud_r * 0.32)),
                               max(1, int(stud_r * 0.40)))


def _kanabo_head(surf, cx, base_y, hw, ss, *, point_up=True, head_r=None,
                 spike_reach=1.44):
    """The bulbous spiked club-HEAD = the detachable PILLAR TOP CAP that rides the
    gap-edge ONLY. A fat iron drum studded with the same rivets PLUS a ring of
    short blunt iron spikes around it (the kanabo's heavy business end). Bold +
    chunky so the spiked-head read survives the 1x pillar downscale; mirrors with
    the shaft into a clean iron post. `point_up` aims the spikes away from the
    shaft (toward the gap). `head_r` + `spike_reach` let the pillar cap the drum
    and shorten the spikes so the ring stays inside the footprint when the shaft
    is full-width."""
    d = -1 if point_up else 1
    if head_r is None:
        head_r = hw * 2.05
    head_cy = base_y + d * head_r * 0.9

    # Ring of short blunt spikes around the head (drawn first, behind the drum).
    n_sp = 11
    mid_reach = 1.0 + (spike_reach - 1.0) * 0.64
    for i in range(n_sp):
        a = math.tau * i / n_sp - math.pi / 2 * d
        sx = cx + math.cos(a) * head_r
        sy = head_cy + math.sin(a) * head_r
        ex = cx + math.cos(a) * head_r * spike_reach
        ey = head_cy + math.sin(a) * head_r * spike_reach
        # Fat blunt spike: a short triangle, dark-core then iron fill.
        perp = a + math.pi / 2
        bwid = head_r * 0.22
        p1 = (sx + math.cos(perp) * bwid, sy + math.sin(perp) * bwid)
        p2 = (sx - math.cos(perp) * bwid, sy - math.sin(perp) * bwid)
        pygame.draw.polygon(surf, IRON_DK,
                            [(int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])),
                             (int(ex), int(ey))])
        p1b = (sx + math.cos(perp) * bwid * 0.6, sy + math.sin(perp) * bwid * 0.6)
        p2b = (sx - math.cos(perp) * bwid * 0.6, sy - math.sin(perp) * bwid * 0.6)
        mx = cx + math.cos(a) * head_r * mid_reach
        my = head_cy + math.sin(a) * head_r * mid_reach
        pygame.draw.polygon(surf, IRON,
                            [(int(p1b[0]), int(p1b[1])), (int(p2b[0]), int(p2b[1])),
                             (int(mx), int(my))])

    # The bulbous iron drum with the triad.
    pygame.draw.circle(surf, IRON_DK, (int(cx), int(head_cy)), int(head_r))
    pygame.draw.circle(surf, IRON, (int(cx), int(head_cy)),
                       max(1, int(head_r - 2 * ss)))
    pygame.draw.circle(surf, IRON_SHEEN,
                       (int(cx - head_r * 0.34), int(head_cy - head_r * 0.36)),
                       int(head_r * 0.34))
    # Big bold rivet studs across the head (the rivet banding carried onto the cap).
    studs = ((-0.34, -0.10), (0.30, -0.18), (0.04, 0.30),
             (-0.30, 0.34), (0.40, 0.28), (0.0, -0.02))
    for fx, fy in studs:
        sx = cx + fx * head_r
        sy = head_cy + fy * head_r
        rr = head_r * 0.20
        pygame.draw.circle(surf, RIVET_DK, (int(sx), int(sy)), int(rr + ss))
        pygame.draw.circle(surf, IRON_SHEEN, (int(sx), int(sy)), int(rr))
        pygame.draw.circle(surf, RIVET,
                           (int(sx - rr * 0.3), int(sy - rr * 0.3)),
                           max(1, int(rr * 0.38)))


def build_ao_oni(scale=1.0, ss=3, *, night=False):
    """The full boss figure on its own transparent surface — a heavy broad slab
    (low wide centre of gravity), the broad scowling head with UP-tusks + topknot
    + ox stub-horn on top, gripping the studded kanabo upright in its right fist.
    Returns an outlined surface and its baseline (feet) y for placement."""
    H = int(250 * scale)
    W = int(190 * scale)
    pad = int(78 * scale)
    surf = pygame.Surface(((W + pad * 2) * ss, (H + pad) * ss), pygame.SRCALPHA)
    cx = (W // 2 + pad) * ss

    # Head occupies the top ~40% (smaller than Big Reapy — the BODY is the mass
    # here). Body slab fills the lower ~60%, sat low + wide.
    head_r = int(H * 0.20) * ss
    head_cy = int(pad * 0.5) * ss + head_r * 1.4
    body_top = head_cy + head_r * 0.92
    body_w = W * 0.46 * ss
    body_h = int(H * 0.56) * ss

    # The kanabo: gripped in the right fist, shaft running DOWN past the hip, the
    # spiked head rising ABOVE the shoulder (shouldered like a brawler).
    grip_x, grip_y = _slab_body(surf, cx, body_top, body_w, body_h, ss)
    # A fatter shouldered club so the prop reads as the same heavy iron kanabo the
    # pillar mirror fills — and the bigger studs carry onto the boss figure.
    khw = 13 * ss
    kx = grip_x + khw * 0.2
    head_base = body_top - head_r * 0.2          # spiked head up by the shoulder
    foot_y = body_top + body_h
    shaft_bot = body_top + body_h * 0.62
    _kanabo_shaft(surf, kx, head_base, shaft_bot, khw, ss)
    _kanabo_head(surf, kx, head_base, khw, ss, point_up=True)
    # The cobalt fist gripping the shaft (over the iron so it reads held).
    _triad_circle(surf, grip_x, grip_y, body_w * 0.20, COBALT)
    # Two ivory claw-nails on the grip.
    for k in (-1, 1):
        pygame.draw.circle(surf, IVORY,
                           (int(grip_x + k * body_w * 0.10), int(grip_y - body_w * 0.12)),
                           max(1, int(2 * ss)))

    _oni_head(surf, cx, head_cy, head_r, ss, night=night)

    out_w = int(surf.get_width() / ss)
    out_h = int(surf.get_height() / ss)
    smallsurf = pygame.transform.smoothscale(surf, (out_w, out_h))
    return _add_outline(smallsurf), foot_y / ss


# ── pillar pair (prop -> pillar mirror proof) ────────────────────────────────

OVERHANG = 12


def _kanabo_pillar_obstacle(height, ss, *, flip):
    """One kanabo PILLAR obstacle: the studded iron shaft fills the post, the
    spiked club-head sits at the gap end. `flip` makes the top pillar's head point
    DOWN into the gap; the bottom pillar's head points UP — proving the prop
    mirrors top<->bottom into a clean iron post with rivet banding + a spiked cap
    flourishing into the gap."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(height)) * ss
    surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
    cx = bw // 2
    # A Skybit pillar IS the full-width obstacle: the iron shaft must FILL the
    # footprint (~84% of pw) so it reads as a heavy iron kanabo, not a thin pole
    # stranded in empty sky. Studs scale off hw, so widening auto-fattens them.
    hw = int((PIPE_W + 2 * OVERHANG) * 0.42 * ss)
    cap_band = int(64 * ss)
    _kanabo_shaft(surf, cx, 0, bh - cap_band, hw, ss)
    # Cap the drum to ~shaft width + short spikes so the spiked club-head stays
    # inside the now-full-width footprint instead of clipping at the panel edge.
    _kanabo_head(surf, cx, bh - cap_band, hw, ss, point_up=False,
                 head_r=hw * 1.06, spike_reach=1.14)
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
    sheet.fill((30, 32, 46))
    _label(sheet, font, "AO-ONI  —  Group B take #4  —  cobalt-oni & tiger-gold  —  round 2", 18, 12)
    _label(sheet, small,
           "the grumpy blue sumo-ogre: a HEAVY broad slab (low wide CoG), UP-tusks + topknot + ox stub-horn, a studded KANABO club",
           18, 32, (200, 200, 214))

    # — Cell A: boss at showcase scale.
    panel = pygame.Rect(18, 56, 360, 560)
    pygame.draw.rect(sheet, (48, 50, 64), panel, border_radius=8)
    pygame.draw.rect(sheet, (86, 90, 110), panel, 2, border_radius=8)
    boss, _ = build_ao_oni(scale=1.55, ss=3)
    sheet.blit(boss, (panel.centerx - boss.get_width() // 2,
                      panel.bottom - boss.get_height() - 14))
    _label(sheet, font, "(a) BOSS  showcase scale", panel.x + 8, panel.y + 8)

    # — Cell B: the kanabo as a tileable PILLAR pair at TRUE obstacle scale.
    panelB = pygame.Rect(394, 56, 360, 560)
    bg = _sky(panelB.w, panelB.h, (40, 110, 200), (90, 170, 230), (170, 220, 245))
    sheet.blit(bg, panelB.topleft)
    pygame.draw.rect(sheet, (86, 90, 110), panelB, 2, border_radius=8)
    _label(sheet, font, "(b) PROP -> PILLAR  @ TRUE obstacle scale", panelB.x + 8, panelB.y + 8)

    pw = PIPE_W + 2 * OVERHANG
    slice_h = 470
    slice_x = panelB.x + 26
    slice_y = panelB.y + 46
    gap_top = 168
    gap_h = 120
    top_h = gap_top
    bot_h = slice_h - gap_top - gap_h
    top_pillar = _kanabo_pillar_obstacle(top_h, 3, flip=True)
    bot_pillar = _kanabo_pillar_obstacle(bot_h, 3, flip=False)
    sheet.blit(top_pillar, (slice_x - 2, slice_y - 2))
    sheet.blit(bot_pillar, (slice_x - 2, slice_y + gap_top + gap_h - 2))
    pygame.draw.rect(sheet, (255, 255, 255), (slice_x - 4, slice_y - 4, pw + 8, slice_h + 8), 1)
    _label(sheet, small, "1x native (82px wide): shaft now FILLS", slice_x - 2, slice_y + slice_h + 6, (20, 20, 30))
    _label(sheet, small, "the footprint; bold rivet rows band it", slice_x - 2, slice_y + slice_h + 22, (20, 20, 30))

    # 2x zoom of the gap so the spiked head + rivet banding is legible.
    zw, zh = pw, 150
    zoom_src = pygame.Surface((zw, zh), pygame.SRCALPHA)
    zoom_src.blit(top_pillar, (-2, -(gap_top - 70) - 2))
    zoom_src.blit(bot_pillar, (-2, gap_h + 70 - 2))
    zoom = pygame.transform.scale(zoom_src, (zw * 2, zh * 2))
    zx = panelB.x + 184
    zy = panelB.y + 70
    sheet.blit(zoom, (zx, zy))
    _label(sheet, small, "2x zoom of the gap:", zx - 4, zy - 16, (255, 255, 255))
    _label(sheet, small, "spiked club-head cap;", zx - 4, zy + zh * 2 + 6, (20, 20, 30))
    _label(sheet, small, "rivet studs = repeatable", zx - 4, zy + zh * 2 + 22, (20, 20, 30))
    _label(sheet, small, "mid banding; top<->bottom mirror", zx - 4, zy + zh * 2 + 38, (20, 20, 30))

    # — Cell C: 1x in-game-scale INSET on BOTH day and night skies.
    panelC = pygame.Rect(770, 56, 392, 560)
    pygame.draw.rect(sheet, (48, 50, 64), panelC, border_radius=8)
    pygame.draw.rect(sheet, (86, 90, 110), panelC, 2, border_radius=8)
    _label(sheet, font, "(c) 1x in-game scale  —  day / night legibility", panelC.x + 8, panelC.y + 8)

    boss1x, _ = build_ao_oni(scale=0.62, ss=3)
    boss1x_n, _ = build_ao_oni(scale=0.62, ss=3, night=True)
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

    # — Grayscale silhouette check.
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
    pygame.draw.rect(sheet, (120, 122, 130), gpanel, border_radius=6)
    sheet.blit(gray, (gpanel.centerx - gray.get_width() // 2,
                      gpanel.bottom - gray.get_height() - 8))
    _label(sheet, small, "grayscale: brows + UP-tusks + broad slab carry the read (no colour reliance)",
           gpanel.x + 6, gpanel.y + 6, (30, 30, 30))

    # — Footer.
    _label(sheet, small,
           "scary-cute: a big sulky lower-lip POUT + tiny legs under the slab = a grumpy strongman, menace softened to a sulk.",
           18, SH - 124, (208, 208, 222))
    _label(sheet, small,
           "house style: FLAT fills, hard ink keyline grown from the alpha mask, dark-core->fill->top-left-sheen triad, ss=3 -> smoothscale.",
           18, SH - 104, (208, 208, 222))
    _label(sheet, small,
           "prop->pillar: rivet STUD rows are the repeatable shaft banding; the spiked iron head is the gap-edge cap. Cobalt owns the BLUE lane.",
           18, SH - 84, (208, 208, 222))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "skybit_devil", "devil", "ao_oni")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
