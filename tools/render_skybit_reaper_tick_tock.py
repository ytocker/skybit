"""TICK-TOCK — the bureaucrat-of-time Death boss (chibi house style).

Death as a smug little CLERK who doesn't reap — he just turns your hourglass
over with an "I have all the time in the world; you don't" smirk. Menace via
patience, the non-blade archetype. A wide squat trapezoid robe (very low centre
of gravity) under a small flat-topped hood, one sleeve cradling a tall
HOURGLASS-STAFF and the other tucked smugly behind his back.

House-style spec (NOT the seed's grim-realist finish): FLAT saturated fills,
1-2px hard ink keylines (28,22,30), form via the dark-core -> light-fill ->
top-left rim-sheen triad (the `_marotte_ruff` recipe), playful scary-cute. The
hourglass-staff is the prop->pillar mirror: a clean vertical pole with the
pinch-waist hourglass sitting at the GAP-EDGE as the "eye" of the pillar, so the
falling sand can animate in-game. Palette family: teal-blue + brass + amber.

Headless review tool — imports the REAL game helpers so the explorations look
like shipped art. Writes a labelled sheet; does not wire anything into the game.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from game.draw import _shade_c, lerp_color, blit_glow  # noqa: F401

# ── TICK-TOCK palette ("ink & amber") ─────────────────────────────────────────
# Robe lifted to a CONFIDENT saturated blue-green that pops on a phone and sits a
# clear value-step above the night sky NIGHT_BOT (35,55,115) so it never merges —
# the prior dull dark-navy was the failure this round corrects.
ROBE = (38, 124, 152)         # bold saturated teal-blue (blue-green, not navy)
ROBE_DK = (24, 84, 106)       # dark-core (lifted off near-ink)
ROBE_HI = (96, 176, 200)      # bright top-left sheen
CAVITY = (28, 70, 84)         # inner-hood recess: a readable DARK TEAL, not a black hole
HOOD_FACE = (244, 236, 214)   # bone-cream skull-pale
FRAME = (200, 144, 46)        # brass hourglass frame
FRAME_DK = (140, 96, 26)
FRAME_HI = (255, 228, 154)
# Amber sand pulled down a notch (was 255,194,61 / 255,228,154) so the hourglass
# stops being the single brightest mass and the skull-pale FACE leads the read.
SAND = (236, 170, 48)         # amber sand (deeper, less near-white-yellow)
SAND_HI = (250, 206, 120)
SASH = (214, 62, 90)          # rose sash
SASH_DK = (150, 38, 60)
GLASS = (180, 224, 232)       # faint cold glass tint
INK = (28, 22, 30)

# Day/night biome keyframes (game/biome.py) so the boss is judged on the real sky.
DAY_TOP, DAY_BOT = (40, 110, 200), (170, 220, 245)
NIGHT_TOP, NIGHT_BOT = (5, 8, 30), (35, 55, 115)


def _triad_circle(surf, cx, cy, r, col, ss):
    """The house form-recipe in a disc: a THIN dark-core keyline -> dominant flat
    fill -> a small top-left sheen. The fill carries the mass (fill-forward); the
    dark edge is a single crisp ink line, not a thick cored ring."""
    pygame.draw.circle(surf, _shade_c(col, -38), (int(cx), int(cy)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), max(1, int(r - ss)))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - r * 0.34), int(cy - r * 0.34)),
                       max(1, int(r * 0.34)))


def _triad_poly(surf, pts, col, ss, *, sheen_pts=None):
    """Flat poly with a 1px dark keyline and an optional top-left sheen wedge — the
    poly version of the triad. Fill-forward: the bright flat fill dominates the
    mass and the internal keyline is a single thin line (the grown silhouette
    outline supplies the real edge), so the body never reads as an inked slab."""
    ipts = [(int(p[0]), int(p[1])) for p in pts]
    pygame.draw.polygon(surf, col, ipts)
    if sheen_pts is not None:
        pygame.draw.polygon(surf, _shade_c(col, 55),
                            [(int(p[0]), int(p[1])) for p in sheen_pts])
    pygame.draw.polygon(surf, _shade_c(col, -38), ipts, max(1, int(ss)))


# ── the hourglass: the shared identity unit of boss + pillar ──────────────────

def _hourglass(surf, cx, cy, half_w, half_h, ss, *, sand_t=0.5, glow=True):
    """A pinch-waist hourglass centred at (cx, cy): two stacked triangles meeting
    at a narrow neck, brass-keyed frame, amber sand split top/bottom by `sand_t`
    (0 = all fallen to the bottom bulb, 1 = all in the top). This SAME unit is the
    boss's staff head AND the pillar's gap-eye, so the prop->pillar mirror is one
    literal shape, not a re-draw. The falling-sand split is the animation hook."""
    neck = max(2, int(half_w * 0.16))     # the pinch waist
    top = cy - half_h
    bot = cy + half_h

    # Glass bulbs FIRST (a faint cold tint) so the amber sand reads as sitting
    # inside real glass, not floating.
    upper_glass = [(cx - half_w, top), (cx + half_w, top), (cx + neck, cy),
                   (cx - neck, cy)]
    lower_glass = [(cx - neck, cy), (cx + neck, cy), (cx + half_w, bot),
                   (cx - half_w, bot)]
    for g in (upper_glass, lower_glass):
        pygame.draw.polygon(surf, GLASS, [(int(p[0]), int(p[1])) for p in g])

    # Amber sand. The upper bulb keeps a top-anchored cone of sand; the lower bulb
    # piles a heap from the floor up. `sand_t` shifts the balance between them.
    up_fill = max(0.0, min(1.0, sand_t))
    if up_fill > 0.02:
        sy = top + (cy - top) * (1.0 - up_fill)   # sand surface descends as it drains
        sand_up = [(cx - half_w + (half_w - neck) * (sy - top) / max(1, cy - top), sy),
                   (cx + half_w - (half_w - neck) * (sy - top) / max(1, cy - top), sy),
                   (cx + neck, cy), (cx - neck, cy)]
        pygame.draw.polygon(surf, SAND, [(int(p[0]), int(p[1])) for p in sand_up])
        pygame.draw.line(surf, SAND_HI, (int(sand_up[0][0]), int(sy)),
                         (int(sand_up[1][0]), int(sy)), max(1, int(1.2 * ss)))
    dn_fill = max(0.0, min(1.0, 1.0 - sand_t))
    if dn_fill > 0.02:
        hy = bot - (bot - cy) * dn_fill           # heap height grows as sand piles
        heap_hw = neck + (half_w - neck) * (bot - hy) / max(1, bot - cy)
        sand_dn = [(cx - neck, cy + (hy - cy) * 0.0), (cx + neck, cy),
                   (cx + heap_hw, bot), (cx - heap_hw, bot)]
        # A rounded heap: clamp the mid surface so it reads as a poured pile.
        sand_dn = [(cx - heap_hw, hy + (bot - hy) * 0.25), (cx + heap_hw, hy + (bot - hy) * 0.25),
                   (cx + half_w, bot), (cx - half_w, bot)]
        pygame.draw.polygon(surf, SAND, [(int(p[0]), int(p[1])) for p in sand_dn])
        pygame.draw.line(surf, SAND_HI,
                         (int(cx - heap_hw), int(hy + (bot - hy) * 0.25)),
                         (int(cx + heap_hw), int(hy + (bot - hy) * 0.25)),
                         max(1, int(1.2 * ss)))

    # The thin falling-sand thread through the neck (the live beat), with a soft
    # amber glow so it reads as luminous trickling time. Glow pulled DOWN one more
    # notch (was 66) so the bright amber mass stops out-shouting the FACE at 1x —
    # the head is the focal point, the glass the supporting beat.
    if glow:
        blit_glow(surf, int(cx), int(cy), max(3, int(half_w * 0.42)), SAND, alpha=40)
    pygame.draw.line(surf, SAND_HI, (int(cx), int(cy - half_h * 0.18)),
                     (int(cx), int(cy + half_h * 0.5)), max(1, int(1.4 * ss)))

    # Brass FRAME last so the ink-keyed metal owns the silhouette. Two bowed
    # triangles + capped pinch + top/bottom plates with rivets.
    for tri in (upper_glass, lower_glass):
        pygame.draw.polygon(surf, FRAME, [(int(p[0]), int(p[1])) for p in tri],
                            max(2, int(2.4 * ss)))
    # End plates (the brass caps top + bottom).
    for py, lit in ((top, True), (bot, False)):
        plate = pygame.Rect(int(cx - half_w - 1.5 * ss), int(py - 1.5 * ss),
                            int((half_w + 1.5 * ss) * 2), int(3.2 * ss))
        pygame.draw.rect(surf, FRAME, plate)
        pygame.draw.rect(surf, FRAME_DK, plate, max(1, int(ss)))
        pygame.draw.line(surf, FRAME_HI, (plate.left, plate.top + ss),
                         (plate.right, plate.top + ss), max(1, int(ss)))
    # The pinch collar (brass band cinching the neck).
    pygame.draw.rect(surf, FRAME, (int(cx - neck - ss), int(cy - 1.6 * ss),
                                   int((neck + ss) * 2), int(3.2 * ss)))
    pygame.draw.rect(surf, FRAME_DK, (int(cx - neck - ss), int(cy - 1.6 * ss),
                                      int((neck + ss) * 2), int(3.2 * ss)), max(1, int(ss)))
    # A single lit rail down the left frame edge reads the glass as round.
    pygame.draw.line(surf, FRAME_HI, (int(cx - half_w + ss), int(top + 2 * ss)),
                     (int(cx - neck + ss), int(cy)), max(1, int(1.2 * ss)))
    # Hard ink corner keylines so the bulbs pop on any sky.
    pygame.draw.polygon(surf, INK, [(int(p[0]), int(p[1])) for p in upper_glass],
                        max(1, int(ss)))
    pygame.draw.polygon(surf, INK, [(int(p[0]), int(p[1])) for p in lower_glass],
                        max(1, int(ss)))


def _smug_face(surf, cx, cy, hw, ss, *, look=-1):
    """The whole point of TICK-TOCK: a smug sidelong HALF-LIDDED glower with one
    arched eyebrow-ridge, on a skull-pale crescent inside the hood. Charming, not
    a sneer — the 'I have all the time in the world; you don't' clerk. `look`
    aims the gaze (negative = toward the held hourglass on the right)."""
    # Bone-cream face crescent recessed in the hood shadow. Enlarged ~22% over the
    # prior round so the SMIRK (the character) wins the read at 1x and out-reads the
    # amber hourglass — the head is the focal point, the glass the supporting beat.
    hw = hw * 1.22
    face = pygame.Rect(int(cx - hw), int(cy - hw * 0.62),
                       int(hw * 2), int(hw * 1.5))
    pygame.draw.ellipse(surf, _shade_c(HOOD_FACE, -38), face)
    pygame.draw.ellipse(surf, HOOD_FACE, face.inflate(int(-2 * ss), int(-2 * ss)))

    ex = hw * 0.46
    ey = cy - hw * 0.06
    for s in (-1, 1):
        exx = cx + s * ex
        # HALF-LIDDED eye: a wide flat ellipse with a heavy ink top lid bar pulled
        # DOWN over it, leaving only a smug sliver — the lazy bureaucrat glower.
        eye = pygame.Rect(int(exx - hw * 0.30), int(ey - hw * 0.16),
                          int(hw * 0.60), int(hw * 0.30))
        pygame.draw.ellipse(surf, (250, 248, 244), eye)
        # Pinprick pupil shoved to the gaze side (sidelong, looking AT you slyly).
        pr = max(1, int(hw * 0.10))
        pygame.draw.circle(surf, INK,
                           (int(exx + look * hw * 0.14), int(ey + hw * 0.02)), pr)
        # The half-lid: a STEEPER, heavier ink bar dragged further DOWN over the eye
        # so only a knowing sliver survives — the menace lives in the lid, not the
        # palette. Pushed down ~1px (ey-0.20 -> ey-0.14) and thickened (2.2 -> 2.8ss)
        # so the slit reads as smug DEATH, not a neutral open eye, even at the 1x inset.
        pygame.draw.arc(surf, INK,
                        (int(exx - hw * 0.34), int(ey - hw * 0.14),
                         int(hw * 0.68), int(hw * 0.42)),
                        math.pi * 0.02, math.pi * 0.98, max(3, int(2.8 * ss)))
        # ONE arched eyebrow-ridge above — inner-LOW, outer raised: the "oh-really"
        # arch that reads patient-condescending. Inner end dragged down + closer to
        # the lid so the brow/lid pinch reads as a steeper knowing squint, not a
        # pleasant open arch.
        inner = (exx - s * hw * 0.12, ey - hw * 0.28)
        mid = (exx + s * hw * 0.20, ey - hw * 0.46)
        outer = (exx + s * hw * 0.44, ey - hw * 0.38)
        pygame.draw.lines(surf, _shade_c(HOOD_FACE, -78), False,
                          [(int(inner[0]), int(inner[1])), (int(mid[0]), int(mid[1])),
                           (int(outer[0]), int(outer[1]))], max(2, int(2.0 * ss)))
    # (No nose-bridge tick — it reads as noise at the 1x inset; the half-lids +
    #  smirk carry the smug clerk on their own.)
    # The SMUG closed mouth: a flat line with the gaze-side corner cocked sharply UP
    # into a deepened dimple — the patient smirk. No teeth, no grimace. The cocked
    # corner is pushed harder (0.10 -> 0.16 lift) so the asymmetry is unmistakably a
    # knowing smirk, not a neutral smile, and survives the 1x shrink.
    my = cy + hw * 0.56
    mouth = []
    for k in range(11):
        t = k / 10.0
        mx = cx - hw * 0.44 + hw * 0.86 * t
        # Hard lift on the left (gaze) corner; let the right droop for the lopsided read.
        myy = my - hw * 0.16 * (1.0 - t) ** 1.4 + hw * 0.07 * t
        mouth.append((int(mx), int(myy)))
    pygame.draw.lines(surf, _shade_c(SASH, -34), False, mouth, max(2, int(2.2 * ss)))
    # Deepened dimple tick seating the raised corner so the cocked smirk survives
    # shrinking — the gaze-side fold that sells the smug, clock-running-out read.
    pygame.draw.line(surf, _shade_c(HOOD_FACE, -64),
                     (int(cx - hw * 0.44), int(my - hw * 0.16)),
                     (int(cx - hw * 0.54), int(my - hw * 0.34)), max(2, int(1.6 * ss)))


def draw_tick_tock(surf, cx, feet_y, scale=1.0, ss=2):
    """Draw the TICK-TOCK boss: a wide squat trapezoid robe (low centre of
    gravity), a small flat-topped hood with a skull-pale smug face, one sleeve-stub
    arm cradling the tall hourglass-staff at his side and the other tucked smugly
    behind his back. Built from primitives + the triad recipe, post-pass ink so the
    silhouette pops on any sky."""
    u = scale * ss                       # one dimensionless body unit -> ss pixels

    def U(v):
        return v * u

    # ── proportions: CHIBI, head a big fraction, body short + very wide hem ──────
    hem_y = feet_y
    shoulder_y = feet_y - U(58)          # short torso
    hood_cy = shoulder_y - U(22)         # head sits LOW and big
    hr = U(30)                           # hood radius (the big chibi head)

    # ── the held HOURGLASS-STAFF, drawn FIRST behind the body so the cradling ──
    #    sleeve overlaps the pole. Stands tall at his right side (viewer-left of
    #    centre is his right; place it viewer-RIGHT so the smug behind-back arm
    #    reads on the other side).
    staff_x = cx + U(40)
    pole_top = hood_cy - U(40)
    pole_bot = hem_y + U(6)
    pole_hw = U(3.2)
    # Pole shaft: dark-core + brass fill + lit rail (a clean tileable post read).
    pygame.draw.rect(surf, _shade_c(FRAME, -55),
                     (int(staff_x - pole_hw - ss), int(pole_top),
                      int((pole_hw + ss) * 2), int(pole_bot - pole_top)))
    pygame.draw.rect(surf, FRAME,
                     (int(staff_x - pole_hw), int(pole_top),
                      int(pole_hw * 2), int(pole_bot - pole_top)))
    pygame.draw.line(surf, FRAME_HI, (int(staff_x - pole_hw * 0.5), int(pole_top)),
                     (int(staff_x - pole_hw * 0.5), int(pole_bot)), max(1, int(1.2 * ss)))
    # Banded grip ferrules along the pole = banding the pillar mirror will reuse.
    for gy in (pole_top + U(46), pole_bot - U(20)):
        pygame.draw.rect(surf, FRAME, (int(staff_x - pole_hw - 2 * ss), int(gy - 2 * ss),
                                       int((pole_hw + 2 * ss) * 2), int(4 * ss)))
        pygame.draw.rect(surf, FRAME_DK, (int(staff_x - pole_hw - 2 * ss), int(gy - 2 * ss),
                                          int((pole_hw + 2 * ss) * 2), int(4 * ss)), max(1, int(ss)))
    # The hourglass head, draining (sand mostly in the lower bulb — he just flipped
    # YOUR glass, his is running out the smug way).
    _hourglass(surf, staff_x, pole_top + U(20), U(15), U(20), ss, sand_t=0.34)

    # ── the squat TRAPEZOID robe (wide hem, narrow shoulders) ──────────────────
    sh_hw = U(30)
    hem_hw = U(50)
    robe = [(cx - sh_hw, shoulder_y), (cx + sh_hw, shoulder_y),
            (cx + hem_hw, hem_y), (cx - hem_hw, hem_y)]
    robe_sheen = [(cx - sh_hw, shoulder_y), (cx - sh_hw * 0.3, shoulder_y),
                  (cx - hem_hw * 0.45, hem_y), (cx - hem_hw, hem_y)]
    _triad_poly(surf, robe, ROBE, ss, sheen_pts=robe_sheen)
    # A scalloped flat hem (chibi lobes, ink-keyed) so the foot reads costume, not
    # a sawn-off block.
    lobes = 7
    for i in range(lobes):
        t = (i + 0.5) / lobes
        lx = cx - hem_hw + 2 * hem_hw * t
        lr = (2 * hem_hw / lobes) * 0.58
        pygame.draw.circle(surf, ROBE, (int(lx), int(hem_y)), int(lr))
        pygame.draw.circle(surf, _shade_c(ROBE, -55), (int(lx), int(hem_y)), int(lr), max(1, int(ss)))

    # Flat SASH belt across the waist — a bold warm horizontal that breaks the tall
    # teal mass and gives the body a key legibility band. Widened + taller so it
    # reads clearly at showcase scale and survives the 1x shrink.
    waist_y = shoulder_y + U(19)
    wl = sh_hw + (hem_hw - sh_hw) * 0.46
    sash_h = U(13)
    sash = [(cx - wl, waist_y), (cx + wl, waist_y),
            (cx + wl, waist_y + sash_h), (cx - wl, waist_y + sash_h)]
    _triad_poly(surf, sash, SASH, ss)
    _triad_circle(surf, cx, waist_y + sash_h * 0.5, U(7), FRAME, ss)
    pygame.draw.circle(surf, SAND, (int(cx), int(waist_y + sash_h * 0.5)), int(U(2.8)))

    # ── arms: one sleeve-stub CRADLING the staff, one tucked smugly behind ──────
    # Cradling arm (his right; viewer-right) — one CONTINUOUS sleeve springing from
    # the shoulder seam and sweeping out to clasp the pole (no detached floating
    # slab). Top edge starts at the shoulder; bottom edge curves under to the mitt.
    # Inner edge runs as a smooth convex sweep from deep inside the shoulder mass
    # out to the forearm — the prior inner-anchor notch cut a flat dark facet that
    # read as a stuck-on tab at the elbow, so it is removed and the underside now
    # springs cleanly from the shoulder.
    cradle = [(cx + sh_hw - U(2), shoulder_y + U(1)),       # shoulder seam (top)
              (cx + sh_hw * 0.78, shoulder_y + U(14)),       # inner shoulder (eased in)
              (cx + sh_hw * 0.96, shoulder_y + U(30)),       # smooth elbow underside
              (staff_x - U(12), pole_top + U(50)),           # underside reaching pole
              (staff_x - U(1), pole_top + U(46)),            # at the pole (forearm)
              (staff_x - U(3), pole_top + U(36)),            # top of forearm
              (cx + sh_hw + U(8), shoulder_y + U(4))]        # outer shoulder (top)
    _triad_poly(surf, cradle, ROBE, ss)
    # A small mitt hand on the pole, one stubby finger TAPPING the glass (waiting).
    _triad_circle(surf, staff_x - U(8), pole_top + U(44), U(7), HOOD_FACE, ss)
    pygame.draw.line(surf, _shade_c(HOOD_FACE, -55),
                     (int(staff_x - U(8)), int(pole_top + U(38))),
                     (int(staff_x - U(3)), int(pole_top + U(30))), max(2, int(2.0 * ss)))

    # Behind-the-back arm (his left; viewer-left) — just a small sleeve nub poking
    # out at the far hip, the rest hidden, the smug "hands clasped behind" tell.
    nub = [(cx - sh_hw * 0.6, shoulder_y + U(8)),
           (cx - sh_hw - U(8), shoulder_y + U(16)),
           (cx - sh_hw - U(4), shoulder_y + U(30)),
           (cx - sh_hw * 0.5, shoulder_y + U(24))]
    _triad_poly(surf, nub, _shade_c(ROBE, -18), ss)

    # ── the HOOD: a small flat-topped half-circle pulled low, big chibi head ────
    # Hood mass (the cowl) — a rounded trapezoid capping the shoulders.
    hood = [(cx - hr * 0.92, hood_cy + hr * 0.7),
            (cx - hr * 0.78, hood_cy - hr * 0.5),
            (cx - hr * 0.34, hood_cy - hr * 1.02),    # flat-ish top-left
            (cx + hr * 0.34, hood_cy - hr * 1.02),    # flat top
            (cx + hr * 0.78, hood_cy - hr * 0.5),
            (cx + hr * 0.92, hood_cy + hr * 0.7)]
    hood_sheen = [(cx - hr * 0.78, hood_cy - hr * 0.5),
                  (cx - hr * 0.34, hood_cy - hr * 1.02),
                  (cx - hr * 0.1, hood_cy - hr * 0.9),
                  (cx - hr * 0.5, hood_cy + hr * 0.4),
                  (cx - hr * 0.85, hood_cy + hr * 0.2)]
    _triad_poly(surf, hood, ROBE, ss, sheen_pts=hood_sheen)
    # The dark inner-hood cavity the face nests in.
    cavity = [(cx - hr * 0.66, hood_cy + hr * 0.62),
              (cx - hr * 0.56, hood_cy - hr * 0.42),
              (cx, hood_cy - hr * 0.74),
              (cx + hr * 0.56, hood_cy - hr * 0.42),
              (cx + hr * 0.66, hood_cy + hr * 0.62)]
    pygame.draw.polygon(surf, CAVITY,
                        [(int(p[0]), int(p[1])) for p in cavity])
    # A brass collar trim where hood meets robe.
    pygame.draw.line(surf, FRAME, (int(cx - hr * 0.9), int(hood_cy + hr * 0.66)),
                     (int(cx + hr * 0.9), int(hood_cy + hr * 0.66)), max(2, int(2.4 * ss)))
    pygame.draw.line(surf, FRAME_HI, (int(cx - hr * 0.9), int(hood_cy + hr * 0.66 - ss)),
                     (int(cx + hr * 0.9), int(hood_cy + hr * 0.66 - ss)), max(1, int(ss)))

    # The smug face inside the cavity, gaze toward the held glass.
    _smug_face(surf, cx, hood_cy + hr * 0.06, hr * 0.5, ss, look=1)


def _add_outline(src, outline_color=(20, 12, 18, 230)):
    """Grow a 1px dark silhouette outline (parrot._add_outline grammar) so the boss
    pops on any sky. Operates in supersampled space before the downscale."""
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


# ── the hourglass-staff PILLAR (the prop->pillar mirror) ──────────────────────

def draw_hourglass_pillar(surf, cx, gap_edge, far_edge, w, ss, *, flip):
    """One TOP or BOTTOM hourglass-staff obstacle. The brass POLE runs the full
    obstacle height (a clean tileable vertical post); the pinch-waist HOURGLASS
    rides the GAP-EDGE as the 'eye' of the pillar — the same `_hourglass` unit the
    boss carries, so prop and pillar are literally one shape. `gap_edge` is the y
    nearest the gameplay gap, `far_edge` the ceiling/floor end. `flip` is accepted
    for API parity with the staff pillar; the build is symmetric about the pole."""
    _ = flip
    span = abs(far_edge - gap_edge)
    sign = 1 if gap_edge < far_edge else -1     # +1: gap above (top pier), grows down

    # The full-height pole: dark-core + brass + lit rail, with ferrule banding so a
    # long post reads as a repeatable mid-section, not a blank bar.
    pole_hw = w * 0.5
    body_top = min(gap_edge, far_edge)
    body_bot = max(gap_edge, far_edge)
    pygame.draw.rect(surf, _shade_c(FRAME, -55),
                     (int(cx - pole_hw - ss), int(body_top),
                      int((pole_hw + ss) * 2), int(body_bot - body_top)))
    pygame.draw.rect(surf, FRAME,
                     (int(cx - pole_hw), int(body_top),
                      int(pole_hw * 2), int(body_bot - body_top)))
    pygame.draw.line(surf, FRAME_HI, (int(cx - pole_hw * 0.5), int(body_top)),
                     (int(cx - pole_hw * 0.5), int(body_bot)), max(1, int(1.4 * ss)))
    # Repeatable mid-section banding (the tileable rhythm).
    band = int(48 * ss)
    gy = body_top + band
    while gy < body_bot - band * 0.5:
        pygame.draw.rect(surf, FRAME, (int(cx - pole_hw - 2 * ss), int(gy - 2 * ss),
                                       int((pole_hw + 2 * ss) * 2), int(4 * ss)))
        pygame.draw.rect(surf, FRAME_DK, (int(cx - pole_hw - 2 * ss), int(gy - 2 * ss),
                                          int((pole_hw + 2 * ss) * 2), int(4 * ss)), max(1, int(ss)))
        gy += band

    # The hourglass CAP at the gap edge — the silhouette bulge that owns the
    # gameplay read. Sand drains toward the gap so the live falling-sand reads. The
    # glass half-WIDTH and the half-width:half-height ratio (0.75) are locked to the
    # boss's staff glass so the "one literal shape" prop->pillar mirror reads
    # IDENTICAL at a glance — the pier glass had been reading marginally wide, so the
    # absolute half-width is now pinned to the boss value (25.5*ss at boss scale 1.7).
    hg_hw = min(span * 0.32 * 0.75, 25.5 * ss)
    hg_hh = hg_hw / 0.75
    hg_cy = gap_edge + sign * (hg_hh + 6 * ss)
    _hourglass(surf, cx, hg_cy, hg_hw, hg_hh, ss, sand_t=0.5)


# ── sheet rendering ───────────────────────────────────────────────────────────

def _sky_panel(w, h, night):
    surf = pygame.Surface((w, h))
    top, bot = (NIGHT_TOP, NIGHT_BOT) if night else (DAY_TOP, DAY_BOT)
    for y in range(h):
        pygame.draw.line(surf, lerp_color(top, bot, y / h), (0, y), (w, y))
    return surf


def _boss_panel(w, h, night, ss):
    ground_y = h - 64
    big = pygame.Surface((w * ss, h * ss), pygame.SRCALPHA)
    draw_tick_tock(big, int(w * 0.5 * ss), int(ground_y * ss), scale=1.7, ss=ss)
    big = _add_outline(big)
    small = pygame.transform.smoothscale(big, (w, h))
    panel = _sky_panel(w, h, night)
    pygame.draw.rect(panel, (40, 34, 30) if not night else (22, 20, 30),
                     (0, ground_y, w, h - ground_y))
    pygame.draw.line(panel, (60, 52, 44) if not night else (50, 44, 58),
                     (0, ground_y), (w, ground_y), 2)
    panel.blit(small, (-2, -2))
    return panel


def main():
    ss = 3
    P_W, P_H = 360, 560          # boss showcase panel
    GAP = 28
    PILL_W = 240                 # pillar-pair panel
    INS_H = 168
    SHEET_W = P_W + GAP * 3 + PILL_W
    SHEET_H = 80 + P_H + 40 + INS_H + 40

    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((26, 24, 32))

    title_f = pygame.font.SysFont("dejavusans", 26, bold=True)
    label_f = pygame.font.SysFont("dejavusans", 17, bold=True)
    note_f = pygame.font.SysFont("dejavusans", 13)

    sheet.blit(title_f.render("SKYBIT REAPER  —  TICK-TOCK  —  round 3", True,
                              (236, 236, 240)), (24, 18))
    sheet.blit(note_f.render(
        "Bureaucrat of time: squat teal trapezoid robe, smug half-lidded glower, cradles an HOURGLASS-STAFF. "
        "Menace via patience, no blade. Teal-blue + brass + amber.", True,
        (170, 170, 184)), (24, 50))

    # (a) Boss at showcase scale, on a day ground line.
    px, py = GAP, 80
    sheet.blit(_boss_panel(P_W, P_H, False, ss), (px, py))
    pygame.draw.rect(sheet, (70, 64, 80), (px, py, P_W, P_H), 1)
    sheet.blit(label_f.render("(a) BOSS  —  showcase scale", True, (236, 236, 240)),
               (px, py + P_H + 8))

    # (b) The hourglass-staff as a tileable PILLAR PAIR (top cap + repeatable mid),
    #     proving the prop->pillar mirror. A gameplay gap between the two piers.
    tx = GAP * 2 + P_W
    ty = 80
    th = P_H
    tw = PILL_W
    pillar = _sky_panel(tw, th, False)
    gap_top = int(th * 0.40)
    gap_bot = int(th * 0.60)
    col_x = tw // 2
    # Pole width pinned to the BOSS staff pole (U(3.2) at boss scale 1.7 = 5.44*ss,
    # so half-width 5.44 -> full ~10.9*ss) so the pole:glass proportion matches the
    # staff and the pier stops reading as a fat post under a small glass.
    post_w = max(4, int(10.9 * ss))
    big_p = pygame.Surface((tw * ss, th * ss), pygame.SRCALPHA)
    # Top pier: hangs from the ceiling, hourglass eye flourishes DOWN into the gap.
    draw_hourglass_pillar(big_p, col_x * ss, gap_top * ss, 4 * ss, post_w, ss, flip=True)
    # Bottom pier: rises from the floor, hourglass eye flourishes UP into the gap.
    draw_hourglass_pillar(big_p, col_x * ss, gap_bot * ss, (th - 4) * ss, post_w, ss, flip=False)
    big_p = _add_outline(big_p)
    small_p = pygame.transform.smoothscale(big_p, (tw, th))
    pillar.blit(small_p, (-2, -2))
    sheet.blit(pillar, (tx, ty))
    pygame.draw.rect(sheet, (70, 64, 80), (tx, ty, tw, th), 1)
    sheet.blit(label_f.render("(b) HOURGLASS-STAFF -> PILLAR PAIR", True,
                              (236, 236, 240)), (tx, ty + th + 8))
    sheet.blit(note_f.render("pinch-waist eye at the gap; pole = tileable post; sand can animate",
                             True, (160, 160, 174)), (tx, ty + th + 28))

    # (c) 1x in-game-scale insets on BOTH day and night skies — true gameplay size.
    # Plus a GRAYSCALE re-confirm: the face must be the highest-contrast read on the
    # figure, the hourglass second (focal-hierarchy verification per the critique).
    ins_w, ins_h = 96, INS_H
    in_ss = 3
    iy = py + P_H + 40
    for j, (night, nm) in enumerate([(False, "DAY"), (True, "NIGHT")]):
        big_i = pygame.Surface((ins_w * in_ss, ins_h * in_ss), pygame.SRCALPHA)
        draw_tick_tock(big_i, int(ins_w * 0.5 * in_ss), int((ins_h - 8) * in_ss),
                       scale=0.42, ss=in_ss)
        big_i = _add_outline(big_i)
        small_i = pygame.transform.smoothscale(big_i, (ins_w, ins_h))
        sky_i = _sky_panel(ins_w, ins_h, night)
        sky_i.blit(small_i, (-2, -2))
        fx = GAP + j * (ins_w + 24)
        sheet.blit(sky_i, (fx, iy))
        pygame.draw.rect(sheet, (90, 84, 104), (fx, iy, ins_w, ins_h), 1)
        sheet.blit(note_f.render("(c) 1x  " + nm, True, (220, 222, 230)),
                   (fx, iy + ins_h + 4))

    # (d) Grayscale check — showcase-scale boss desaturated, on a flat mid sky so
    #     only value matters: the head/smirk should lead, the hourglass second.
    gw, gh = 150, INS_H
    g_ss = 3
    big_g = pygame.Surface((gw * g_ss, gh * g_ss), pygame.SRCALPHA)
    draw_tick_tock(big_g, int(gw * 0.5 * g_ss), int((gh - 6) * g_ss),
                   scale=0.62, ss=g_ss)
    big_g = _add_outline(big_g)
    small_g = pygame.transform.smoothscale(big_g, (gw, gh))
    gpanel = pygame.Surface((gw, gh))
    gpanel.fill((118, 118, 122))
    gpanel.blit(small_g, (-2, -2))
    # Desaturate in place (luminance) so the value structure is judged honestly.
    arr = pygame.surfarray.pixels3d(gpanel)
    lum = (arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587
           + arr[:, :, 2] * 0.114).astype("uint8")
    arr[:, :, 0] = lum
    arr[:, :, 1] = lum
    arr[:, :, 2] = lum
    del arr
    gx = GAP + 2 * (ins_w + 24)
    sheet.blit(gpanel, (gx, iy))
    pygame.draw.rect(sheet, (90, 84, 104), (gx, iy, gw, gh), 1)
    sheet.blit(note_f.render("(d) GRAYSCALE  face leads, glass 2nd", True,
                             (220, 222, 230)), (gx, iy + ins_h + 4))

    out_dir = "/home/user/skybit/docs/skybit_reaper/tick_tock"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.font.init()
    main()
