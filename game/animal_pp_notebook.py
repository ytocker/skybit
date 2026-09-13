"""Production PAPER PLANE skin — concept NOTEBOOK PAPER — round-2 convergence.

A secret ultra-premium NON-creature flyer: the player's flapping bird becomes
a dart folded from BLUE-RULED schoolyard loose-leaf. The 40px tell is a DARK
warm-red margin band along the keel + two heavy blue rules lifted onto the lit
facet, reading as "lined paper" even small. There are no wings — the 4 base
wing poses are reinterpreted as a gentle BANK/FLUTTER: the dart rolls a few
degrees and the nose bobs as it catches air.

This is the single ship-ready build distilled from the V5 · BOLD LOOSE-LEAF
exploration (art-director winner). Contract mirrors game/animal_paper_plane.py
so it lifts straight in:

  * `build_notebook(wing_angle_deg) -> pygame.Surface`  draws one flat frame on
    a 64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84).
  * mass centred at the BODY anchor (32, 44) — collision is a fixed 14px circle
    there, so the dart keeps its centre of mass on that point.
  * NOSE POINTS RIGHT (forward).
  * `get_notebook = _make_prebuilt_skin(build_notebook)` cached getter.
  * `BUILDERS = {"skin_notebook": get_notebook}` at the bottom.

North star: "a skin lives or dies at 40px in motion." The dart leans on ONE
bold triangular silhouette + a HARD-value FOLD — a soft warm off-white lit
facet and a distinctly darker under-fold meeting at a crisp keel crease, with
the value split made the boldest step in the skin so the fold reads as a fold
in BOTH level and banked-dive poses. The lit facet is knocked off pure white so
its top edge holds a silhouette against bright day clouds, and a baked 1px
self-rim does the edge work on both day AND night skies without any host
outline. Colourblind safety: the margin leans on VALUE (a dark warm band, not a
bright hue) and the two blue rules add a second independent value cue.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline,
)


# ── canvas constants (match game/animal_paper_plane.py) ──────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body / mass centre → (32, 44)


# ── shared factory (local copy of _make_prebuilt_skin) ───────────────────────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache,
    each frame outlined with the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flutter(angle_deg):
    """Map a base wing angle (_WING_ANGLES runs 50→-40) to a centred −1..+1
    'catching air' factor. Drives the gentle bank-roll + nose-bob; there are no
    wings, so the flap energy goes entirely into the craft swaying."""
    return ((angle_deg + 40) / 90.0 - 0.5) * 2.0


def _poly(surf, color, pts, width=0):
    pygame.draw.polygon(surf, color, pts, width)


def _bank(pts, cx, cy, roll_deg, bob):
    """Roll a point list a few degrees about (cx, cy) and lift it by `bob`.

    The whole craft pivots about its mass centre so the silhouette banks as one
    rigid folded sheet — the cheapest, most paper-plane-honest read of 'flap'."""
    r = math.radians(roll_deg)
    cos_r, sin_r = math.cos(r), math.sin(r)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * cos_r - dy * sin_r,
                    cy + dx * sin_r + dy * cos_r + bob))
    return out


def _self_rim(surf, rim_col):
    """Bake a 1px darker self-rim hugging the WHOLE dart silhouette so it never
    depends on the host outline — stamped UNDER the art so it reads as a clean
    1px lip, no glow halo (glow restraint). This is what holds the lit top edge
    against bright day clouds once the facet is knocked off pure white."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=rim_col, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


def _clip_to_poly(stamp_fn, clip_pts):
    """Run `stamp_fn(tmp)` onto a scratch surface, then keep only the pixels
    inside `clip_pts` — lets us draw rules that stop cleanly at the paper's
    folded facet edge instead of bleeding past the silhouette."""
    tmp = _new()
    stamp_fn(tmp)
    mask_surf = _new()
    pygame.draw.polygon(mask_surf, (255, 255, 255, 255),
                        [(int(x), int(y)) for x, y in clip_pts])
    mask = pygame.mask.from_surface(mask_surf, threshold=8)
    inside = mask.to_surface(setcolor=(255, 255, 255, 255),
                             unsetcolor=(0, 0, 0, 0))
    tmp.blit(inside, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tmp


# Roll is clamped so the bank-roll "flap" never flattens the dart to a sliver:
# at 3/4 view the under-fold collapses if the craft rolls too far edge-on.
_ROLL_MAX = 5.5


# ═════════════════════════════════════════════════════════════════════════════
# Shared dart geometry. A crisp triangular dart nosing RIGHT, mass centred on
# (BCX, BCY). The top swept edge is a single straight nose→far_tip line so the
# triangular silhouette is unambiguous; the keel crease splits a LIT top facet
# from a darker UNDER-fold.
# ═════════════════════════════════════════════════════════════════════════════
def _dart_pts():
    # The lit facet is given extra vertical room (far_tip pushed higher) so the
    # two blue rules + the margin band can each sit in their OWN value-separated
    # lane and still resolve as distinct features at 40px.
    nose       = (BCX + 25, BCY - 1)
    far_tip    = (BCX - 14, BCY - 16)     # upper trailing corner
    near_tip   = (BCX - 12, BCY + 14)     # lower trailing corner
    centre_back = (BCX - 16, BCY)         # keel meets trailing edge
    return nose, far_tip, near_tip, centre_back


# ── production palette ───────────────────────────────────────────────────────
# The lit facet is a SOFT WARM-NEUTRAL off-white, not pure white, so its top
# edge holds a silhouette against bright pale-blue day clouds (the rim does the
# rest). The under-fold drops ~19% in value off the lit facet so the keel reads
# as a HARD fold — this is the boldest value step in the whole skin, and it
# survives the banked dive where a shallower split would flatten.
_PAPER     = (243, 241, 230)         # warm off-white lit facet (not pure white)
_PAPER_H   = (252, 250, 240)         # faint leading-edge lift at the nose
_UNDER     = (164, 167, 174)         # shadowed under-sheet — ~20% darker
_UNDER_D   = (132, 137, 148)         # deepest crease-side shadow
_CREASE    = (88, 92, 106)           # hard keel value break (3px)
_RIM       = (80, 86, 100)           # baked self-rim (cool, holds on day + night)

# Blue rules: both heavy. Two independent value cues that also survive a
# red-blind eye. Lifted HIGH onto the lit facet with a clear body-value gap
# between them so they never smear into one bar at 40px.
_RULE_B    = (54, 104, 182)          # heavy ink-blue rule

# Red margin: a DARK WARM band (lean on VALUE, not bright hue) so a red-blind
# player still reads a dark margin rule. Given its own clear band along the keel,
# separated from the blue rules by the lit-facet body value.
_MARGIN    = (158, 44, 46)           # dark warm-red margin band
_MARGIN_SH = (118, 30, 34)           # 1px under-shade so the band reads as ink

# Binder ring-holes: trimmed to TWO so they don't read as edge noise at 40px.
_HOLE_FILL = (206, 210, 214)
_HOLE_RING = (132, 140, 154)


def build_notebook(wing_angle_deg):
    """Draw one flat NOTEBOOK-PAPER dart frame, nose RIGHT, on a 64×84 canvas.

    Layer order is load-bearing: under-fold → lit facet → ring-holes → blue
    rules (clipped to the lit facet) → red margin band → keel crease → baked
    self-rim. The crease overpaints the rules so the fold spine always reads
    crisp, and the margin sits in its own band BELOW the rules so red and blue
    never touch.
    """
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3

    nose, far_tip, near_tip, centre_back = _dart_pts()

    def B(pts):
        return _bank(pts, BCX, BCY, roll, bob)

    # ── UNDER-fold first (lower facet, in shadow) ────────────────────────────
    near = B([nose, near_tip, centre_back])
    _poly(surf, _UNDER, near)
    # Deepen the crease-side wedge so the value step is widest right at the fold,
    # which is where the eye reads "this is a fold" even in the banked dive.
    _poly(surf, _UNDER_D, B([nose, near_tip, (BCX - 5, BCY + 5)]))

    # ── TOP facet (lit upper sheet) ──────────────────────────────────────────
    far = B([nose, far_tip, centre_back])
    _poly(surf, _PAPER, far)
    # Leading-edge lift at the nose where the top folds meet.
    _poly(surf, _PAPER_H, B([nose, (BCX + 7, BCY - 6), (BCX + 9, BCY - 1)]))

    # ── TWO binder ring-holes punched along the upper trailing edge. ─────────
    for hx, hy in B([(BCX - 11, BCY - 13), (BCX - 13, BCY - 8)]):
        pygame.draw.circle(surf, _HOLE_FILL, (int(hx), int(hy)), 2)
        pygame.draw.circle(surf, _HOLE_RING, (int(hx), int(hy)), 2, 1)

    # ── TWO heavy blue rules, lifted HIGH onto the lit facet. ────────────────
    # A clear ≥1 body-value-pixel gap is kept between them (BCY-11 vs BCY-7) so
    # they stay two distinct rules at 40px instead of merging into a muddy bar.
    # They bend a touch to follow the lit facet's slope — V2's 3D charm, tested
    # to still resolve as two rules at 40px because the gap is wide enough.
    def _rules(tmp):
        # ~5px source spacing keeps a clear band-value lane between the two
        # rules so they downscale to two distinct lines, not one muddy bar.
        for ry in (BCY - 13, BCY - 8):
            p = _bank([(BCX - 9, ry + 1), (BCX + 17, ry - 3)],
                      BCX, BCY, roll, bob)
            pygame.draw.line(tmp, _RULE_B, (int(p[0][0]), int(p[0][1])),
                             (int(p[1][0]), int(p[1][1])), 2)
    surf.blit(_clip_to_poly(_rules, far), (0, 0))

    # ── DARK red margin band — its own clear lane LOW on the lit facet, kept a
    #    clear body-value gap below the blue rules so red and blue never touch.
    #    A 1px under-shade reads it as a printed rule; the band leans on VALUE
    #    (dark warm) so a red-blind player still reads a dark margin line.
    msh_a, msh_b = B([(BCX + 18, BCY - 3), (BCX - 13, BCY - 2)])
    pygame.draw.line(surf, _MARGIN_SH, (int(msh_a[0]), int(msh_a[1])),
                     (int(msh_b[0]), int(msh_b[1])), 2)
    ma, mb = B([(BCX + 18, BCY - 4), (BCX - 13, BCY - 3)])
    pygame.draw.line(surf, _MARGIN, (int(ma[0]), int(ma[1])),
                     (int(mb[0]), int(mb[1])), 2)

    # ── HARD keel crease (the fold spine) — 3px hard value break at 40px,
    #    drawn last so it overpaints any rule/margin tails cleanly.
    a, b = B([nose, centre_back])
    pygame.draw.line(surf, _CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)

    return _self_rim(surf, _RIM)


get_notebook = _make_prebuilt_skin(build_notebook)

# Label→getter registry (liftable into game/animal_paper_plane.py).
BUILDERS = {"skin_notebook": get_notebook}
