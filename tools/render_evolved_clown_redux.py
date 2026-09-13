"""Look-dev: the LATE-GAME EVOLVED warren clown — boss escalation (REDUX r1).

ONE figure, SIX cells, all on a single shared ground line:
  cell 0  the FAITHFUL CURRENT clown (Plum & Lime FINAL), clown-only, no die/staff
  cells 1-5  five GROUND-UP boss escalations of the SAME warren jester lineage —
             nastier, meaner, FUNNIER, grandiose and physically LARGER.

The DOCTRINE this sheet obeys: the five evolved bosses are five separate
designs, not one shown five ways. They differ in KIND across concept,
silhouette, construction and shape language. There is NO shared figure/body
builder among them — each boss owns its own builder + primitives. Only the
low-level paint helpers (`_shade`, `_bell`, a gradient line) are shared, which
is allowed. Quick proof of the five silhouettes (the blackout test):

  1 COLOSSUS   wide bottom-heavy TRIANGLE (huge coat-skirt + plumed mitre)
  2 PUPPETEER  tall gaunt VERTICAL stick (stilt legs + drooping spire bundle)
  3 GLUTTON    a single dominant CIRCLE orb (belly is the whole body)
  4 SPIDER     a radial STAR/BURST (six arms fanned off a diamond carapace)
  5 JANUS      an asymmetric SPLIT with a billowing banner SAIL behind it

Evolved palette across all five (the lineage GROWN, soured + tarnished):
  bruised deep plum, soured venom lime, tarnished dirty gold, blood/bruise
  accents. Each boss is drawn at native K-scale (geometry multiplied by K) and
  blit 1:1 — no smoothscale upscale — so faces stay crisp.

    PYTHONPATH=. python tools/render_evolved_clown_redux.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

# Cell 0 reproduces the REAL current clown verbatim through the shipped builder.
from tools.render_jester_variants import build_jester, JESTERS
from tools.render_clown_dice import _shade


# ── evolved lineage palette (the Plum & Lime jester GROWN + soured) ──────────
# Deeper bruised plum, a soured venom lime, tarnished dirty gold, blood/bruise
# accents. Shared across the five bosses so they read as ONE evolved family even
# though their silhouettes diverge hard.
PLUM_DEEP   = (58, 24, 78)      # bruised deep plum (the body north-star dark)
PLUM_DARK   = (40, 16, 56)      # near-black plum for shadow cores / keylines
PLUM_BRUISE = (96, 38, 110)     # lifted plum highlight / facet
VENOM       = (150, 196, 60)    # soured venom lime (the loud accent)
VENOM_DEEP  = (96, 132, 36)     # shaded venom
VENOM_LIT   = (196, 228, 110)   # lit venom edge
GOLD        = (196, 158, 54)    # tarnished dirty gold
GOLD_LIT    = (236, 204, 110)   # lit gold facet
GOLD_DARK   = (120, 92, 28)     # gold shadow / keyline
BLOOD       = (158, 30, 42)     # blood / bruise accent (maw, wounds, tongue)
BLOOD_DARK  = (96, 14, 26)
BONE        = (236, 226, 198)   # aged ivory teeth / bone
SKIN        = (214, 196, 176)   # greyed sickly clown skin (was warm peach)
SKIN_SHADE  = (150, 132, 120)
INK         = (18, 12, 22)
EYE_GLINT   = (210, 248, 120)   # venom-lit eye glint (the one bright cue)
WHITE       = (240, 240, 232)    # sclera / eye-white

GROUND_COL  = (74, 96, 52)      # matched ground band under all six
GROUND_LIT  = (104, 132, 74)
BG_TOP      = (96, 92, 110)     # neutral mid-tone backdrop, slightly cool
BG_BOT      = (78, 74, 92)

# Round-2 development accents — the art-director flagged round-1's Janus banner
# as "fire-red"; the evolved lineage wants a BRUISED OXBLOOD / maroon instead,
# darker and more soured than a clean blood scarlet.
OXBLOOD      = (112, 28, 36)    # bruised oxblood banner/sail body
OXBLOOD_DARK = (70, 16, 24)     # banner shadow / keyline
OXBLOOD_LIT  = (146, 46, 52)    # lit oxblood fold
STRING_COL   = (206, 200, 182)  # taut marionette filament (aged ivory thread)
STRING_DARK  = (150, 144, 126)


# ── shared LOW-LEVEL paint helpers (allowed — not a figure builder) ──────────

def _grad_v(surf, rect, top, bot):
    """Vertical gradient fill into a rect (shared primitive)."""
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(surf, c, (x, y + i), (x + w, y + i))


def _bell(surf, x, y, r, col=GOLD):
    """A tarnished gold bell sphere with a lit cap + a dark base nub."""
    pygame.draw.circle(surf, GOLD_DARK, (int(x), int(y)), r + 1)
    pygame.draw.circle(surf, col, (int(x), int(y)), r)
    pygame.draw.circle(surf, GOLD_LIT, (int(x - r // 2), int(y - r // 2)),
                       max(1, r // 2))
    pygame.draw.line(surf, GOLD_DARK, (x - r // 2, y + r - 1),
                     (x + r // 2, y + r - 1), 1)


def _glint(surf, x, y, r):
    """The single bright eye-glint cue every boss face must carry, so the face
    holds at small size."""
    pygame.draw.circle(surf, EYE_GLINT, (int(x), int(y)), r)
    pygame.draw.circle(surf, (255, 255, 240), (int(x), int(y)), max(1, r // 2))


def _bruise(surf, x, y, rx, ry, alpha=90):
    """A soft bruise/blood blotch (bruised-lineage skin damage), alpha-blended."""
    s = pygame.Surface((rx * 2 + 2, ry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*BLOOD, alpha), s.get_rect())
    surf.blit(s, (int(x - rx), int(y - ry)))


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 1 — THE RINGMASTER COLOSSUS
# Thesis: a towering BAROQUE circus-ringmaster boss — a wide bottom-heavy
# triangle dominated by a colossal dagged tailcoat-skirt and an immense
# plume-crested mitre fused to the jester cap; arms flung wide in a "BEHOLD!"
# showman flare. Construction: stacked trapezoidal dagged coat panels (its own
# skirt builder), epaulet shoulder shelves, a tall plumed mitre. NOTHING shared
# with the other four builders.
# ─────────────────────────────────────────────────────────────────────────────

def build_colossus(surf, cx, feet_y, K):
    s = K
    # The grand triangular coat-skirt: a wide dagged hem sweeping up to narrow
    # shoulders — drawn as its OWN trapezoid + a row of hanging dagges.
    hem_y = feet_y - 6 * s
    skirt_w = 96 * s
    shoulder_w = 52 * s
    waist_y = feet_y - 96 * s
    skirt = [(cx - shoulder_w, waist_y), (cx + shoulder_w, waist_y),
             (cx + skirt_w, hem_y), (cx - skirt_w, hem_y)]
    pygame.draw.polygon(surf, PLUM_DEEP, skirt)
    # Sculpt: lit left facet + dark right.
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - shoulder_w, waist_y), (cx - 6 * s, waist_y),
                         (cx - 30 * s, hem_y), (cx - skirt_w, hem_y)])
    pygame.draw.polygon(surf, PLUM_DARK,
                        [(cx + 14 * s, waist_y), (cx + shoulder_w, waist_y),
                         (cx + skirt_w, hem_y), (cx + 40 * s, hem_y)])
    pygame.draw.polygon(surf, PLUM_DARK, skirt, 2 * s)
    # A venom centre-placket running up the coat with gold frog-buttons.
    pygame.draw.polygon(surf, VENOM_DEEP,
                        [(cx - 10 * s, waist_y), (cx + 10 * s, waist_y),
                         (cx + 16 * s, hem_y), (cx - 16 * s, hem_y)])
    pygame.draw.polygon(surf, VENOM,
                        [(cx - 8 * s, waist_y), (cx + 4 * s, waist_y),
                         (cx + 8 * s, hem_y), (cx - 12 * s, hem_y)])
    for i in range(5):
        by = waist_y + (hem_y - waist_y) * (i + 0.5) / 5
        _bell(surf, cx - s, by, 3 * s)
    # Dagged hem: a row of hanging venom-tipped triangles along the bottom.
    n = 9
    for i in range(n):
        t0 = i / n
        t1 = (i + 1) / n
        x0 = cx - skirt_w + 2 * skirt_w * t0
        x1 = cx - skirt_w + 2 * skirt_w * t1
        mid = (x0 + x1) / 2
        col = VENOM if i % 2 else GOLD
        dag = [(x0, hem_y - 2 * s), (x1, hem_y - 2 * s), (mid, hem_y + 12 * s)]
        pygame.draw.polygon(surf, col, dag)
        pygame.draw.polygon(surf, _shade(col, -60), dag, s)
        _bell(surf, mid, hem_y + 12 * s, 2 * s)

    # Two stout legs just peeking below the skirt in harlequin hose.
    for sgn, col in ((-1, VENOM), (1, PLUM_BRUISE)):
        lx = cx + sgn * 26 * s
        pygame.draw.line(surf, _shade(col, -50), (lx, hem_y), (lx, feet_y - 4 * s),
                         9 * s)
        pygame.draw.line(surf, col, (lx, hem_y), (lx, feet_y - 4 * s), 6 * s)
    # Big curled-toe boots planted wide.
    for sgn in (-1, 1):
        bx = cx + sgn * 26 * s
        boot = pygame.Rect(0, 0, 26 * s, 12 * s)
        boot.center = (bx + sgn * 6 * s, feet_y - 2 * s)
        pygame.draw.ellipse(surf, PLUM_DARK, boot)
        pygame.draw.ellipse(surf, PLUM_DEEP, boot.inflate(-3 * s, -3 * s))
        tip = (bx + sgn * 20 * s, feet_y - 2 * s)
        curl = [(bx + sgn * 12 * s, feet_y + 3 * s),
                (bx + sgn * 12 * s, feet_y - 7 * s), tip]
        pygame.draw.polygon(surf, GOLD, curl)
        _bell(surf, tip[0], tip[1] - 2 * s, 3 * s)

    # Shoulder shelf / epaulets: broad ornamental gold shelves the arms hang off.
    for sgn in (-1, 1):
        shx = cx + sgn * shoulder_w
        ep = [(cx + sgn * 18 * s, waist_y - 2 * s),
              (shx + sgn * 18 * s, waist_y - 6 * s),
              (shx + sgn * 14 * s, waist_y + 14 * s),
              (cx + sgn * 16 * s, waist_y + 12 * s)]
        pygame.draw.polygon(surf, GOLD, ep)
        pygame.draw.polygon(surf, GOLD_DARK, ep, s)
        # Bullion fringe under the epaulet.
        for k in range(4):
            fx = shx + sgn * (4 + k * 4) * s
            pygame.draw.line(surf, GOLD_LIT, (fx, waist_y + 12 * s),
                             (fx, waist_y + 20 * s), max(1, s))

    # Arms flung wide + UP in the grandiose BEHOLD flare, ending in gauntlets.
    sh_y = waist_y + 2 * s
    for sgn, hand_up in ((-1, (cx - 78 * s, waist_y - 40 * s)),
                         (1, (cx + 78 * s, waist_y - 44 * s))):
        sh = (cx + sgn * (shoulder_w - 6 * s), sh_y)
        elbow = (cx + sgn * 70 * s, waist_y - 8 * s)
        pygame.draw.line(surf, PLUM_DARK, sh, elbow, 11 * s)
        pygame.draw.line(surf, PLUM_DEEP, sh, elbow, 8 * s)
        pygame.draw.line(surf, PLUM_DARK, elbow, hand_up, 9 * s)
        pygame.draw.line(surf, PLUM_DEEP, elbow, hand_up, 6 * s)
        # Flared venom cuff + a big gold gauntlet fist presenting upward.
        pygame.draw.circle(surf, VENOM_DEEP, elbow, 7 * s)
        pygame.draw.circle(surf, GOLD_DARK, hand_up, 9 * s)
        pygame.draw.circle(surf, GOLD, hand_up, 8 * s)
        pygame.draw.circle(surf, GOLD_LIT, (hand_up[0] - 2 * s, hand_up[1] - 2 * s),
                           3 * s)

    # A grand layered ruff between the shoulders.
    neck_y = waist_y - 6 * s
    for i in range(11):
        t = i / 10
        rx = cx + int((-1 + 2 * t) * 30 * s)
        ry = neck_y + int(math.sin(t * math.pi) * -4 * s)
        pygame.draw.circle(surf, GOLD_DARK, (rx, ry), 7 * s)
        pygame.draw.circle(surf, GOLD, (rx, ry), 6 * s)
        pygame.draw.circle(surf, GOLD_LIT, (rx - 2 * s, ry - 2 * s), 2 * s)

    # HEAD — broad sneering ringmaster face.
    hr = 22 * s
    hy = neck_y - hr - 2 * s
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr + s)
    pygame.draw.circle(surf, SKIN, (cx, hy), hr)
    _bruise(surf, cx + 12 * s, hy + 6 * s, 7 * s, 5 * s, 70)
    _colossus_face(surf, cx, hy, hr, s)

    # The IMMENSE plumed mitre — a tall pointed hat fused with two flung jester
    # horns, crowned by an extravagant feather plume. This is the grandiosity.
    cap_base = hy - hr + 4 * s
    mitre = [(cx - 20 * s, cap_base), (cx + 20 * s, cap_base),
             (cx + 8 * s, cap_base - 52 * s), (cx - 8 * s, cap_base - 52 * s)]
    pygame.draw.polygon(surf, PLUM_DEEP, mitre)
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - 20 * s, cap_base), (cx - 4 * s, cap_base),
                         (cx - 8 * s, cap_base - 52 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, mitre, 2 * s)
    # Venom chevron band across the mitre.
    pygame.draw.polygon(surf, VENOM,
                        [(cx - 18 * s, cap_base - 14 * s),
                         (cx + 18 * s, cap_base - 14 * s),
                         (cx + 16 * s, cap_base - 24 * s),
                         (cx - 16 * s, cap_base - 24 * s)])
    # Two flung jester horns off the mitre sides, each belled.
    for sgn in (-1, 1):
        tip = (cx + sgn * 40 * s, cap_base - 30 * s)
        horn = [(cx + sgn * 14 * s, cap_base - 8 * s),
                (cx + sgn * 18 * s, cap_base - 22 * s), tip]
        pygame.draw.polygon(surf, GOLD, horn)
        pygame.draw.polygon(surf, GOLD_DARK, horn, s)
        _bell(surf, tip[0], tip[1], 3 * s)
    # Extravagant feather plume bursting from the mitre peak.
    peak = (cx, cap_base - 52 * s)
    for k, ang in enumerate((-0.5, -0.15, 0.2, 0.55)):
        col = VENOM if k % 2 else GOLD
        tipx = peak[0] + math.sin(ang) * 34 * s
        tipy = peak[1] - 30 * s + abs(ang) * 8 * s
        plume = [(peak[0] - 3 * s, peak[1]), (peak[0] + 3 * s, peak[1]),
                 ((peak[0] + tipx) / 2 + 5 * s, (peak[1] + tipy) / 2),
                 (tipx, tipy),
                 ((peak[0] + tipx) / 2 - 4 * s, (peak[1] + tipy) / 2)]
        pygame.draw.polygon(surf, col, plume)
        pygame.draw.polygon(surf, _shade(col, -55), plume, s)
    pygame.draw.circle(surf, GOLD_DARK, peak, 4 * s)
    pygame.draw.circle(surf, GOLD, peak, 3 * s)


def _colossus_face(surf, cx, hy, hr, s):
    # Heavy sunken brow shelf — a hard dark bar (macro shape that reads small).
    pygame.draw.polygon(surf, PLUM_DARK,
                        [(cx - 15 * s, hy - 5 * s), (cx + 15 * s, hy - 5 * s),
                         (cx + 12 * s, hy + 2 * s), (cx - 12 * s, hy + 2 * s)])
    for sgn in (-1, 1):
        ex = cx + sgn * 8 * s
        # Glaring eye — narrow venom slit under the shelf.
        pygame.draw.ellipse(surf, INK, (ex - 5 * s, hy, 10 * s, 8 * s))
        _glint(surf, ex - sgn * 1 * s, hy + 3 * s, 3 * s)
        # Curled showman moustache flourish.
    pygame.draw.circle(surf, BLOOD, (cx, hy + 9 * s), 4 * s)  # red nose, smaller
    pygame.draw.circle(surf, _shade(BLOOD, 70), (cx - s, hy + 8 * s), 2 * s)
    # A wide grinning sneer with a moustache curling over it + one fang.
    grin = pygame.Rect(cx - 14 * s, hy + 12 * s, 28 * s, 12 * s)
    pygame.draw.arc(surf, BLOOD_DARK, grin, math.pi, math.tau, 3 * s)
    teeth_y = hy + 16 * s
    pygame.draw.polygon(surf, BONE,
                        [(cx - 12 * s, teeth_y), (cx + 12 * s, teeth_y),
                         (cx + 9 * s, teeth_y + 4 * s), (cx - 9 * s, teeth_y + 4 * s)])
    for tx in range(-2, 3):
        gx = cx + tx * 5 * s
        pygame.draw.line(surf, BLOOD_DARK, (gx, teeth_y), (gx, teeth_y + 4 * s), s)
    # One fang.
    pygame.draw.polygon(surf, BONE, [(cx - 9 * s, teeth_y + 4 * s),
                                     (cx - 5 * s, teeth_y + 4 * s),
                                     (cx - 7 * s, teeth_y + 9 * s)])
    # Up-curled gold moustache over the lip.
    for sgn in (-1, 1):
        pygame.draw.arc(surf, GOLD_DARK,
                        (cx + sgn * 2 * s - 12 * s, hy + 9 * s, 24 * s, 12 * s),
                        (math.pi * 1.1 if sgn < 0 else math.tau * 0.0),
                        (math.tau if sgn < 0 else math.pi * 0.9), 3 * s)


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 2 — THE PUPPETEER ABOVE
# Thesis: a long, looming MARIONETTE-MASTER — impossibly tall + gaunt, on
# stilt-thin bird legs, with dangling control-strings off clawed hands and a
# drooping bundle of cap-spires collapsing over the skull. Construction: an
# elongated stick-and-knob limb spine (its OWN segmented limb builder), a
# drooping spire-bundle cap, hanging string filaments + a crossbar control.
# Tall thin VERTICAL silhouette — the opposite of boss 1's wide triangle.
# ─────────────────────────────────────────────────────────────────────────────

def _stick_limb(surf, pts, w, col):
    """A gaunt segmented limb: thin shafts with knobby joints (puppeteer's OWN
    limb primitive — bones-on-strings read, not the chunky tapered arm)."""
    for i in range(len(pts) - 1):
        pygame.draw.line(surf, _shade(col, -60), pts[i], pts[i + 1], w + 2)
        pygame.draw.line(surf, col, pts[i], pts[i + 1], w)
    for p in pts:
        pygame.draw.circle(surf, _shade(col, -50), p, w // 2 + 2)
        pygame.draw.circle(surf, col, p, w // 2 + 1)
        pygame.draw.circle(surf, _shade(col, 40), (p[0] - 1, p[1] - 1), max(1, w // 3))


def build_puppeteer(surf, cx, feet_y, K):
    s = K
    # Stilt-thin bird legs splayed to a narrow stance — long bones + knee knobs.
    hip_y = feet_y - 130 * s
    for sgn in (-1, 1):
        ankle = (cx + sgn * 16 * s, feet_y - 6 * s)
        knee = (cx + sgn * 22 * s, feet_y - 64 * s)
        hip = (cx + sgn * 8 * s, hip_y)
        _stick_limb(surf, [hip, knee, ankle], 6 * s,
                    VENOM if sgn < 0 else PLUM_BRUISE)
        # Long pointed slipper foot, curled, belled.
        toe = (ankle[0] + sgn * 18 * s, ankle[1] - 8 * s)
        foot = [(ankle[0] - sgn * 4 * s, ankle[1] + 4 * s),
                (ankle[0] - sgn * 4 * s, ankle[1] - 5 * s), toe]
        pygame.draw.polygon(surf, PLUM_DEEP, foot)
        pygame.draw.polygon(surf, PLUM_DARK, foot, s)
        _bell(surf, toe[0], toe[1], 3 * s)

    # A long lean torso — a narrow tapering column, not a chunky block.
    torso = [(cx - 14 * s, hip_y + 4 * s), (cx + 14 * s, hip_y + 4 * s),
             (cx + 10 * s, hip_y - 70 * s), (cx - 10 * s, hip_y - 70 * s)]
    pygame.draw.polygon(surf, PLUM_DEEP, torso)
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - 14 * s, hip_y + 4 * s), (cx - 4 * s, hip_y + 4 * s),
                         (cx - 4 * s, hip_y - 70 * s), (cx - 10 * s, hip_y - 70 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, torso, 2 * s)
    # Venom rib-lacing chevrons down the gaunt torso (skeletal cage read).
    for i in range(5):
        ry = hip_y - 6 * s - i * 14 * s
        wv = (12 - i) * s
        pygame.draw.line(surf, VENOM, (cx - wv, ry), (cx, ry + 4 * s), 2 * s)
        pygame.draw.line(surf, VENOM, (cx, ry + 4 * s), (cx + wv, ry), 2 * s)
    shoulder_y = hip_y - 70 * s

    # Long spidery arms reaching DOWN-and-OUT, ending in clawed hands that hold
    # the marionette control crossbar; strings dangle from the claws.
    for sgn in (-1, 1):
        sh = (cx + sgn * 10 * s, shoulder_y + 4 * s)
        elbow = (cx + sgn * 40 * s, shoulder_y + 30 * s)
        wrist = (cx + sgn * 34 * s, shoulder_y + 64 * s)
        _stick_limb(surf, [sh, elbow, wrist], 5 * s,
                    PLUM_BRUISE if sgn < 0 else VENOM)
        # Clawed three-finger hand.
        for f in (-1, 0, 1):
            fx = wrist[0] + sgn * 2 * s + f * 4 * s
            pygame.draw.line(surf, GOLD_DARK, wrist,
                             (fx, wrist[1] + 12 * s), 2 * s)
            pygame.draw.circle(surf, GOLD, (fx, wrist[1] + 12 * s), 2 * s)
        # Dangling control strings from each claw down past the feet.
        for f in (-1, 1):
            sx = wrist[0] + f * 4 * s
            pygame.draw.line(surf, (210, 206, 190),
                             (sx, wrist[1] + 12 * s), (sx + f * 2 * s, feet_y - 8 * s), 1)

    # A small marionette control crossbar gripped between the hands — the
    # gleeful "I pull the strings" gag prop.
    bar_y = shoulder_y + 70 * s
    pygame.draw.line(surf, GOLD_DARK, (cx - 28 * s, bar_y), (cx + 28 * s, bar_y), 4 * s)
    pygame.draw.line(surf, GOLD, (cx - 28 * s, bar_y), (cx + 28 * s, bar_y), 2 * s)

    # A tall narrow heraldic collar — a thin ruff of long dagged points.
    neck_y = shoulder_y - 2 * s
    for i in range(7):
        t = (i - 3) / 3
        tx = cx + int(t * 18 * s)
        pygame.draw.polygon(surf, GOLD,
                            [(cx, neck_y - 6 * s), (tx - 4 * s, neck_y + 10 * s),
                             (tx + 4 * s, neck_y + 10 * s)])
        pygame.draw.polygon(surf, GOLD_DARK,
                            [(cx, neck_y - 6 * s), (tx - 4 * s, neck_y + 10 * s),
                             (tx + 4 * s, neck_y + 10 * s)], s)
        _bell(surf, tx, neck_y + 11 * s, 2 * s)

    # HEAD — long gaunt skull, hollow-cheeked.
    hr = 18 * s
    hy = neck_y - hr - 8 * s
    head = pygame.Rect(0, 0, hr * 2, int(hr * 2.4))
    head.center = (cx, hy)
    pygame.draw.ellipse(surf, SKIN_SHADE, head.inflate(2 * s, 2 * s))
    pygame.draw.ellipse(surf, SKIN, head)
    # Hollow cheek shadows (gaunt).
    _bruise(surf, cx - 12 * s, hy + 4 * s, 5 * s, 9 * s, 60)
    _bruise(surf, cx + 12 * s, hy + 4 * s, 5 * s, 9 * s, 60)
    _puppeteer_face(surf, cx, hy, hr, s)

    # Drooping spire-bundle cap: a fan of long limp spires flopping over the
    # skull like dead branches, each belled. Grandiose-decrepit, not perky.
    cap_y = hy - int(hr * 1.2)
    for sgn, dx, dy, col in ((-1, -34, 18, VENOM), (-1, -20, -10, PLUM_BRUISE),
                             (0, 0, -34, GOLD), (1, 22, -8, VENOM),
                             (1, 36, 16, PLUM_BRUISE)):
        tip = (cx + dx * s, cap_y + dy * s)
        spire = [(cx - 8 * s, cap_y + 4 * s), (cx + 8 * s, cap_y + 4 * s), tip]
        pygame.draw.polygon(surf, col, spire)
        pygame.draw.polygon(surf, _shade(col, -55), spire, s)
        _bell(surf, tip[0], tip[1], 3 * s)


def _puppeteer_face(surf, cx, hy, hr, s):
    # Deep sunken eye sockets — dark hollows with a single venom pinprick glint.
    for sgn in (-1, 1):
        ex = cx + sgn * 8 * s
        pygame.draw.ellipse(surf, INK, (ex - 6 * s, hy - 6 * s, 12 * s, 11 * s))
        _glint(surf, ex - sgn * 2 * s, hy - 2 * s, 2 * s)
        # Sharp arched-up cruel brow over each socket.
        pygame.draw.line(surf, PLUM_DARK, (ex - 6 * s, hy - 4 * s),
                         (ex + sgn * 7 * s, hy - 9 * s), 3 * s)
    # Small mean red nose.
    pygame.draw.circle(surf, BLOOD, (cx, hy + 5 * s), 3 * s)
    pygame.draw.circle(surf, _shade(BLOOD, 70), (cx - s, hy + 4 * s), s)
    # A long stitched ear-to-ear grin — a thin gleeful slash with cross-stitches.
    gy = hy + 14 * s
    pygame.draw.arc(surf, BLOOD_DARK, (cx - 14 * s, gy - 6 * s, 28 * s, 16 * s),
                    math.pi * 0.05, math.pi * 0.95, 3 * s)
    for k in range(-3, 4):
        sx = cx + k * 4 * s
        sy = gy + int(abs(k) * 0.6 * s)
        pygame.draw.line(surf, INK, (sx, sy - 4 * s), (sx, sy + 4 * s), s)


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 3 — THE BLOATED GLUTTON KING
# Thesis: a gross, near-SPHERICAL bouncing fat-jester — ONE enormous belly orb
# IS the whole body, with tiny vestigial limbs, a squashed wide grin splitting
# the lower sphere, and a sagging belt of bells girdling the gut. Construction:
# a single dominant circle (its OWN orb builder), bilateral bell-fringe belt,
# stubby radial nub-limbs, a tiny crown perched on top. Round bottom-heavy
# silhouette — nothing like the other four.
# ─────────────────────────────────────────────────────────────────────────────

def build_glutton(surf, cx, feet_y, K):
    s = K
    R = 74 * s                     # the colossal belly radius (the whole body)
    bcy = feet_y - R - 4 * s       # belly centre

    # Tiny stubby legs poking out the bottom of the gut.
    for sgn in (-1, 1):
        lx = cx + sgn * 22 * s
        pygame.draw.line(surf, _shade(VENOM, -50), (lx, bcy + R - 10 * s),
                         (lx + sgn * 4 * s, feet_y - 6 * s), 11 * s)
        pygame.draw.line(surf, VENOM, (lx, bcy + R - 10 * s),
                         (lx + sgn * 4 * s, feet_y - 6 * s), 8 * s)
        # Squashed bell-toe bootie.
        boot = pygame.Rect(0, 0, 22 * s, 11 * s)
        boot.center = (lx + sgn * 8 * s, feet_y - 3 * s)
        pygame.draw.ellipse(surf, PLUM_DARK, boot)
        pygame.draw.ellipse(surf, PLUM_DEEP, boot.inflate(-3 * s, -2 * s))
        _bell(surf, boot.centerx + sgn * 11 * s, boot.centery - 2 * s, 3 * s)

    # THE GUT — a single huge plum sphere, harlequin-quartered, with stretched
    # diamond panels that read as a too-tight costume bursting at the seams.
    pygame.draw.circle(surf, PLUM_DARK, (cx, bcy), R + 2 * s)
    pygame.draw.circle(surf, PLUM_DEEP, (cx, bcy), R)
    # Quartered colour split painted as clipped wedges.
    quad = pygame.Surface((R * 2 + 4 * s, R * 2 + 4 * s), pygame.SRCALPHA)
    qc = (R + 2 * s, R + 2 * s)
    pygame.draw.polygon(quad, (*VENOM_DEEP, 255),
                        [qc, (qc[0] + R + 2 * s, qc[1] - R - 2 * s),
                         (qc[0] + R + 2 * s, qc[1])])
    pygame.draw.polygon(quad, (*VENOM_DEEP, 255),
                        [qc, (qc[0] - R - 2 * s, qc[1] + R + 2 * s),
                         (qc[0] - R - 2 * s, qc[1])])
    mask = pygame.Surface(quad.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), qc, R)
    quad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(quad, (cx - R - 2 * s, bcy - R - 2 * s))
    # Top-left sheen on the bulging gut.
    sheen = pygame.Surface((R, R), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 60), sheen.get_rect())
    surf.blit(sheen, (cx - R + 6 * s, bcy - R + 6 * s))
    # Stretched gold diamond buttons straining in a row down the centre.
    for i in range(4):
        dy = bcy - 30 * s + i * 22 * s
        dw = 7 * s
        pygame.draw.polygon(surf, GOLD,
                            [(cx, dy - dw), (cx + dw, dy), (cx, dy + dw), (cx - dw, dy)])
        pygame.draw.polygon(surf, GOLD_DARK,
                            [(cx, dy - dw), (cx + dw, dy), (cx, dy + dw), (cx - dw, dy)], s)
    # Straining seam-stitch lines arcing over the belly (about to burst).
    for off in (-1, 1):
        pygame.draw.arc(surf, BONE,
                        (cx - R + 10 * s, bcy - R // 2 + off * 6 * s,
                         R * 2 - 20 * s, R), math.pi * 0.15, math.pi * 0.85, s)

    # The SAGGING BELT OF BELLS girdling the widest part of the gut.
    belt_y = bcy + 8 * s
    pygame.draw.arc(surf, GOLD_DARK, (cx - R, belt_y - 8 * s, R * 2, 30 * s),
                    math.pi * 0.08, math.pi * 0.92, 6 * s)
    pygame.draw.arc(surf, GOLD, (cx - R, belt_y - 8 * s, R * 2, 30 * s),
                    math.pi * 0.08, math.pi * 0.92, 3 * s)
    for i in range(7):
        t = i / 6
        bx = cx - R + 12 * s + (R * 2 - 24 * s) * t
        by = belt_y + int(math.sin(t * math.pi) * 14 * s) + 8 * s
        _bell(surf, bx, by, 4 * s)

    # Tiny vestigial arms — one tucked greedily on the gut, one raised with a
    # gnawed bone (the GLUTTON gag). Stubby, dwarfed by the belly.
    # Left tiny arm resting on belly.
    pygame.draw.line(surf, _shade(PLUM_BRUISE, -50),
                     (cx - R + 14 * s, bcy - 8 * s), (cx - R + 30 * s, bcy + 6 * s), 9 * s)
    pygame.draw.line(surf, PLUM_BRUISE,
                     (cx - R + 14 * s, bcy - 8 * s), (cx - R + 30 * s, bcy + 6 * s), 6 * s)
    pygame.draw.circle(surf, GOLD, (cx - R + 30 * s, bcy + 6 * s), 6 * s)
    # Right tiny arm raised waving a gnawed drumstick bone.
    rh = (cx + R - 2 * s, bcy - 30 * s)
    pygame.draw.line(surf, _shade(PLUM_BRUISE, -50),
                     (cx + R - 16 * s, bcy - 6 * s), rh, 9 * s)
    pygame.draw.line(surf, PLUM_BRUISE, (cx + R - 16 * s, bcy - 6 * s), rh, 6 * s)
    pygame.draw.circle(surf, GOLD, rh, 6 * s)
    # Gnawed bone in the fist.
    pygame.draw.line(surf, BONE, (rh[0] - 2 * s, rh[1] + 2 * s),
                     (rh[0] + 12 * s, rh[1] - 12 * s), 4 * s)
    pygame.draw.circle(surf, BONE, (rh[0] + 12 * s, rh[1] - 12 * s), 4 * s)
    pygame.draw.circle(surf, BONE, (rh[0] - 2 * s, rh[1] + 2 * s), 3 * s)

    # Small head squashed down INTO the gut (chinless, gluttonous), with a tiny
    # too-small crown jester-cap perched comically on top.
    hr = 22 * s
    hy = bcy - R - hr + 14 * s
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr + s)
    pygame.draw.circle(surf, SKIN, (cx, hy), hr)
    # Multiple chins merging into the gut.
    for c in range(2):
        pygame.draw.arc(surf, SKIN_SHADE,
                        (cx - hr + 4 * s, hy + 6 * s + c * 6 * s, hr * 2 - 8 * s, 16 * s),
                        math.pi * 0.1, math.pi * 0.9, 2 * s)
    _glutton_face(surf, cx, hy, hr, s)
    # Comically TINY three-point cap perched on the crown.
    cap_y = hy - hr + 2 * s
    for sgn, dx, dy, col in ((-1, -14, -16, VENOM), (0, 0, -22, GOLD),
                             (1, 14, -16, PLUM_BRUISE)):
        tip = (cx + dx * s, cap_y + dy * s)
        pygame.draw.polygon(surf, col,
                            [(cx - 9 * s, cap_y + 2 * s), (cx + 9 * s, cap_y + 2 * s), tip])
        pygame.draw.polygon(surf, _shade(col, -55),
                            [(cx - 9 * s, cap_y + 2 * s), (cx + 9 * s, cap_y + 2 * s), tip], s)
        _bell(surf, tip[0], tip[1], 2 * s)


def _glutton_face(surf, cx, hy, hr, s):
    # Greedy half-closed gleeful eyes — fat happy squints with a hungry glint.
    for sgn in (-1, 1):
        ex = cx + sgn * 9 * s
        pygame.draw.ellipse(surf, WHITE, (ex - 6 * s, hy - 4 * s, 12 * s, 9 * s))
        pygame.draw.circle(surf, INK, (ex + sgn * 2 * s, hy + s), 3 * s)
        _glint(surf, ex + sgn * 1 * s, hy - s, 2 * s)
        # Heavy fatty upper lid drooping over (greedy squint).
        pygame.draw.arc(surf, SKIN_SHADE, (ex - 7 * s, hy - 7 * s, 14 * s, 12 * s),
                        math.pi * 0.05, math.pi * 0.95, 3 * s)
    pygame.draw.circle(surf, BLOOD, (cx, hy + 5 * s), 5 * s)
    pygame.draw.circle(surf, _shade(BLOOD, 80), (cx - 2 * s, hy + 3 * s), 2 * s)
    # A HUGE wide-open gluttonous grin splitting the lower face — tongue lolling.
    mouth = pygame.Rect(cx - 16 * s, hy + 10 * s, 32 * s, 18 * s)
    pygame.draw.ellipse(surf, BLOOD_DARK, mouth)
    pygame.draw.ellipse(surf, INK, mouth, 2 * s)
    # Lolling tongue.
    pygame.draw.ellipse(surf, BLOOD, (cx - 6 * s, hy + 18 * s, 16 * s, 12 * s))
    pygame.draw.line(surf, BLOOD_DARK, (cx + 2 * s, hy + 19 * s),
                     (cx + 2 * s, hy + 28 * s), s)
    # Upper teeth row + one fat fang.
    pygame.draw.polygon(surf, BONE,
                        [(cx - 14 * s, hy + 11 * s), (cx + 14 * s, hy + 11 * s),
                         (cx + 12 * s, hy + 15 * s), (cx - 12 * s, hy + 15 * s)])
    pygame.draw.polygon(surf, BONE, [(cx - 9 * s, hy + 15 * s),
                                     (cx - 4 * s, hy + 15 * s),
                                     (cx - 6 * s, hy + 22 * s)])


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 4 — THE SPIDER-FOOL (MANY-ARMED HARLEQUIN)
# Thesis: a demonic commedia HARLEQUIN with SIX arms fanned like a peacock /
# spider off a diamond-lattice segmented carapace torso, crowned by a sharp
# horned cap-mask. Construction: a radial multi-arm fan (its OWN radial-arm
# builder), a diamond-tiled insectile carapace, segmented sharp shape language.
# A STAR/BURST silhouette — radial, not the columnar/round/triangle others.
# ─────────────────────────────────────────────────────────────────────────────

def build_spider(surf, cx, feet_y, K):
    s = K
    core_y = feet_y - 96 * s        # the carapace centre
    # Two sharp insect legs planted, but the silhouette star is the ARMS.
    for sgn in (-1, 1):
        hip = (cx + sgn * 12 * s, core_y + 30 * s)
        knee = (cx + sgn * 30 * s, feet_y - 40 * s)
        ankle = (cx + sgn * 18 * s, feet_y - 6 * s)
        for a, b in ((hip, knee), (knee, ankle)):
            pygame.draw.line(surf, PLUM_DARK, a, b, 8 * s)
            pygame.draw.line(surf, PLUM_DEEP, a, b, 5 * s)
        pygame.draw.circle(surf, VENOM_DEEP, knee, 4 * s)
        # Sharp pointed harlequin foot.
        toe = (ankle[0] + sgn * 14 * s, ankle[1] - 6 * s)
        pygame.draw.polygon(surf, PLUM_DEEP,
                            [(ankle[0], ankle[1] + 4 * s),
                             (ankle[0], ankle[1] - 4 * s), toe])
        _bell(surf, toe[0], toe[1], 2 * s)

    # SIX radial arms fanned out in a burst — three per side, each a segmented
    # spider limb ending in a clawed gold mitt. The fan IS the silhouette.
    arm_specs = [(-150, 78), (-118, 92), (-92, 70),
                 (-30, 78), (-62, 92), (-88, 70)]
    # angles measured in degrees; left set sweeps up-left, right mirrored.
    for i, (deg, length) in enumerate(arm_specs):
        sgn = -1 if i < 3 else 1
        base_deg = deg if sgn < 0 else (180 - deg)
        ang = math.radians(base_deg)
        sh = (cx + sgn * 6 * s, core_y - 10 * s + (i % 3) * 14 * s)
        elbow = (sh[0] + math.cos(ang) * length * 0.55 * s,
                 sh[1] - math.sin(ang) * length * 0.55 * s)
        hand = (sh[0] + math.cos(ang) * length * s,
                sh[1] - math.sin(ang) * length * s)
        col = VENOM if i % 2 else PLUM_BRUISE
        pygame.draw.line(surf, _shade(col, -55), sh, elbow, 6 * s)
        pygame.draw.line(surf, _shade(col, -55), elbow, hand, 5 * s)
        pygame.draw.line(surf, col, sh, elbow, 4 * s)
        pygame.draw.line(surf, col, elbow, hand, 3 * s)
        pygame.draw.circle(surf, VENOM_DEEP, (int(elbow[0]), int(elbow[1])), 3 * s)
        # Clawed gold mitt.
        pygame.draw.circle(surf, GOLD_DARK, (int(hand[0]), int(hand[1])), 5 * s)
        pygame.draw.circle(surf, GOLD, (int(hand[0]), int(hand[1])), 4 * s)
        for f in (-0.4, 0, 0.4):
            cx2 = hand[0] + math.cos(ang + f) * 8 * s
            cy2 = hand[1] - math.sin(ang + f) * 8 * s
            pygame.draw.line(surf, INK, (int(hand[0]), int(hand[1])),
                             (int(cx2), int(cy2)), 2 * s)

    # The DIAMOND-LATTICE carapace: a segmented angular torso plate built from a
    # tessellated harlequin diamond grid (its own tiling), reading insectile.
    cw, ch = 34 * s, 60 * s
    plate = [(cx, core_y - ch), (cx + cw, core_y - ch // 3),
             (cx + cw - 6 * s, core_y + ch // 2), (cx, core_y + ch // 2 + 8 * s),
             (cx - cw + 6 * s, core_y + ch // 2), (cx - cw, core_y - ch // 3)]
    pygame.draw.polygon(surf, PLUM_DARK, plate)
    # Tessellated diamonds clipped to the plate.
    tile = pygame.Surface((cw * 2 + 2, ch * 2 + 2), pygame.SRCALPHA)
    ox, oy = cw, ch
    d = 11 * s
    for row in range(-1, 7):
        for coli in range(-3, 4):
            dx = ox + coli * d + (d // 2 if row % 2 else 0)
            dy = oy + row * d - ch + ch // 3
            col = VENOM if (row + coli) % 2 else PLUM_BRUISE
            pygame.draw.polygon(tile, (*col, 255),
                                [(dx, dy - d // 2 + 1), (dx + d // 2 - 1, dy),
                                 (dx, dy + d // 2 - 1), (dx - d // 2 + 1, dy)])
    mask = pygame.Surface(tile.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - cx + ox, p[1] - core_y + oy) for p in plate])
    tile.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(tile, (cx - ox, core_y - oy))
    pygame.draw.polygon(surf, PLUM_DARK, plate, 2 * s)
    # Segment ridge lines across the carapace (insect plates).
    for sy in range(-2, 3):
        ry = core_y + sy * 12 * s
        half = int(cw * (1 - abs(sy) * 0.12))
        pygame.draw.line(surf, GOLD_DARK, (cx - half, ry), (cx + half, ry), s)
    # A gold gorget collar at the throat.
    pygame.draw.arc(surf, GOLD, (cx - 20 * s, core_y - ch - 6 * s, 40 * s, 22 * s),
                    math.pi, math.tau, 5 * s)

    # HEAD — a sharp angular horned mask-head (diamond-shaped, not round).
    hr = 20 * s
    hy = core_y - ch - hr + 4 * s
    head = [(cx, hy - hr - 2 * s), (cx + hr, hy), (cx, hy + hr + 4 * s),
            (cx - hr, hy)]
    pygame.draw.polygon(surf, SKIN_SHADE, head)
    pygame.draw.polygon(surf, SKIN,
                        [(cx, hy - hr), (cx + hr - 2 * s, hy),
                         (cx, hy + hr + 2 * s), (cx - hr + 2 * s, hy)])
    _bruise(surf, cx, hy + 8 * s, 8 * s, 5 * s, 60)
    _spider_face(surf, cx, hy, hr, s)
    # Sharp horned cap-mask: two long swept-back horns + a central spike, belled.
    cap_y = hy - hr + 2 * s
    for sgn, dx, dy in ((-1, -28, -26), (0, 0, -40), (1, 28, -26)):
        tip = (cx + dx * s, cap_y + dy * s)
        horn = [(cx - 7 * s, cap_y), (cx + 7 * s, cap_y), tip]
        col = GOLD if dx == 0 else (VENOM if sgn < 0 else PLUM_BRUISE)
        pygame.draw.polygon(surf, col, horn)
        pygame.draw.polygon(surf, _shade(col, -60), horn, s)
        _bell(surf, tip[0], tip[1], 2 * s)


def _spider_face(surf, cx, hy, hr, s):
    # FOUR small spider eyes in two rows — venom glints in the dark, plus a
    # bigger pair for the read. Macro shape: a sharp dark brow chevron.
    pygame.draw.polygon(surf, PLUM_DARK,
                        [(cx - 12 * s, hy - 4 * s), (cx, hy - 8 * s),
                         (cx + 12 * s, hy - 4 * s), (cx, hy - 2 * s)])
    for sgn in (-1, 1):
        ex = cx + sgn * 7 * s
        pygame.draw.ellipse(surf, INK, (ex - 5 * s, hy - s, 10 * s, 8 * s))
        _glint(surf, ex, hy + 2 * s, 3 * s)
        # A smaller upper eye pair (the extra spider eyes).
        pygame.draw.circle(surf, INK, (cx + sgn * 4 * s, hy - 6 * s), 2 * s)
        pygame.draw.circle(surf, EYE_GLINT, (cx + sgn * 4 * s, hy - 7 * s), s)
    pygame.draw.circle(surf, BLOOD, (cx, hy + 6 * s), 3 * s)
    # A sharp toothy chevron grin (angular to match the diamond head).
    pygame.draw.polygon(surf, BLOOD_DARK,
                        [(cx - 12 * s, hy + 10 * s), (cx + 12 * s, hy + 10 * s),
                         (cx, hy + 18 * s)])
    pygame.draw.polygon(surf, BONE,
                        [(cx - 11 * s, hy + 10 * s), (cx + 11 * s, hy + 10 * s),
                         (cx, hy + 16 * s)])
    for tx in range(-3, 4):
        gx = cx + tx * 3 * s
        pygame.draw.line(surf, BLOOD_DARK, (gx, hy + 10 * s),
                         (cx, hy + 16 * s), s)


# ─────────────────────────────────────────────────────────────────────────────
# BOSS 5 — THE JANUS HERALD (TWO-FACED MARQUEE)
# Thesis: a grandiose theatrical herald SPLIT down the middle into comedy &
# tragedy halves, a billowing banner-cape SAIL ballooning behind, a single
# DOUBLE-faced head (one half a wide grin, the other a weeping snarl) held high
# on a flared heraldic mantle. Construction: a vertical mirror-split body with a
# MISMATCHED bilateral face (its own split-face builder) + a sweeping banner
# sail. An asymmetric split silhouette with a cape — unlike any other.
# ─────────────────────────────────────────────────────────────────────────────

def build_janus(surf, cx, feet_y, K):
    s = K
    hip_y = feet_y - 92 * s
    top_y = hip_y - 78 * s

    # The billowing BANNER-CAPE SAIL behind — a great curved flag ballooning to
    # one side, the marquee grandeur. Drawn FIRST so the body sits in front.
    sail = [(cx + 6 * s, top_y - 6 * s),
            (cx + 90 * s, top_y + 6 * s),
            (cx + 110 * s, hip_y - 10 * s),
            (cx + 96 * s, hip_y + 40 * s),
            (cx + 64 * s, hip_y + 50 * s),
            (cx + 30 * s, hip_y + 30 * s)]
    pygame.draw.polygon(surf, BLOOD_DARK, sail)
    pygame.draw.polygon(surf, BLOOD,
                        [(cx + 6 * s, top_y - 6 * s), (cx + 60 * s, top_y),
                         (cx + 70 * s, hip_y), (cx + 30 * s, hip_y + 30 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, sail, 2 * s)
    # Gold tassel fringe along the sail's trailing (right) edge.
    for k in range(6):
        t = k / 5
        fx = int((110 - (110 - 64) * t) * s)
        fy = int((hip_y - 10 * s) + (hip_y + 50 * s - (hip_y - 10 * s)) * t)
        _bell(surf, cx + fx, fy, 2 * s)
    # A venom heraldic emblem (a jester-skull motif) on the banner.
    em = (cx + 56 * s, hip_y - 2 * s)
    pygame.draw.circle(surf, VENOM, em, 12 * s)
    pygame.draw.circle(surf, VENOM_DEEP, em, 12 * s, s)
    pygame.draw.circle(surf, INK, (em[0] - 4 * s, em[1] - 2 * s), 2 * s)
    pygame.draw.circle(surf, INK, (em[0] + 4 * s, em[1] - 2 * s), 2 * s)
    pygame.draw.arc(surf, INK, (em[0] - 6 * s, em[1] + 2 * s, 12 * s, 8 * s),
                    math.pi, math.tau, 2 * s)

    # The body: a vertical MIRROR-SPLIT robe — comedy (venom/gold, bright) on the
    # viewer-LEFT half, tragedy (deep plum/blood, dark) on the right half. Each
    # half is its OWN tall panel meeting at the centre seam.
    left_half = [(cx, hip_y + 14 * s), (cx, top_y),
                 (cx - 30 * s, top_y + 6 * s), (cx - 40 * s, hip_y + 14 * s)]
    right_half = [(cx, hip_y + 14 * s), (cx, top_y),
                  (cx + 30 * s, top_y + 6 * s), (cx + 40 * s, hip_y + 14 * s)]
    pygame.draw.polygon(surf, VENOM_DEEP, left_half)
    pygame.draw.polygon(surf, VENOM,
                        [(cx - 4 * s, top_y + 2 * s), (cx - 26 * s, top_y + 6 * s),
                         (cx - 32 * s, hip_y + 10 * s), (cx - 6 * s, hip_y + 12 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, right_half)
    pygame.draw.polygon(surf, PLUM_DEEP,
                        [(cx + 4 * s, top_y + 2 * s), (cx + 26 * s, top_y + 6 * s),
                         (cx + 32 * s, hip_y + 10 * s), (cx + 6 * s, hip_y + 12 * s)])
    # Contrasting accents per half: gold dots on the bright half, bone teardrop
    # tears stitched down the dark half.
    for i in range(3):
        dy = top_y + 20 * s + i * 22 * s
        pygame.draw.circle(surf, GOLD, (cx - 18 * s, dy), 4 * s)
        pygame.draw.circle(surf, GOLD_DARK, (cx - 18 * s, dy), 4 * s, s)
        # tragedy tear.
        pygame.draw.polygon(surf, (170, 190, 210),
                            [(cx + 18 * s, dy - 4 * s), (cx + 22 * s, dy + 2 * s),
                             (cx + 14 * s, dy + 2 * s)])
    pygame.draw.line(surf, BONE, (cx, top_y), (cx, hip_y + 14 * s), 2 * s)
    pygame.draw.polygon(surf, INK, left_half, 2 * s)
    pygame.draw.polygon(surf, INK, right_half, 2 * s)

    # Legs — harlequin, each matching its half's mood.
    for sgn, col in ((-1, VENOM), (1, PLUM_BRUISE)):
        lx = cx + sgn * 18 * s
        pygame.draw.line(surf, _shade(col, -50), (lx, hip_y + 10 * s),
                         (lx + sgn * 4 * s, feet_y - 6 * s), 11 * s)
        pygame.draw.line(surf, col, (lx, hip_y + 10 * s),
                         (lx + sgn * 4 * s, feet_y - 6 * s), 8 * s)
        boot = pygame.Rect(0, 0, 22 * s, 11 * s)
        boot.center = (lx + sgn * 8 * s, feet_y - 3 * s)
        pygame.draw.ellipse(surf, PLUM_DARK, boot)
        pygame.draw.ellipse(surf, PLUM_DEEP, boot.inflate(-3 * s, -2 * s))
        _bell(surf, boot.centerx + sgn * 11 * s, boot.centery - 2 * s, 3 * s)

    # One arm raised high holding a herald's trumpet/sceptre flourish; the other
    # planted on the hip — theatrical proclamation.
    # Raised left arm.
    sh_l = (cx - 24 * s, top_y + 12 * s)
    hand_l = (cx - 58 * s, top_y - 34 * s)
    pygame.draw.line(surf, VENOM_DEEP, sh_l, hand_l, 9 * s)
    pygame.draw.line(surf, VENOM, sh_l, hand_l, 6 * s)
    pygame.draw.circle(surf, GOLD, hand_l, 6 * s)
    # A flared herald trumpet held aloft.
    pygame.draw.line(surf, GOLD, hand_l, (hand_l[0] - 4 * s, hand_l[1] - 26 * s), 4 * s)
    pygame.draw.polygon(surf, GOLD,
                        [(hand_l[0] - 10 * s, hand_l[1] - 38 * s),
                         (hand_l[0] + 2 * s, hand_l[1] - 38 * s),
                         (hand_l[0] - 4 * s, hand_l[1] - 26 * s)])
    pygame.draw.polygon(surf, GOLD_DARK,
                        [(hand_l[0] - 10 * s, hand_l[1] - 38 * s),
                         (hand_l[0] + 2 * s, hand_l[1] - 38 * s),
                         (hand_l[0] - 4 * s, hand_l[1] - 26 * s)], s)
    # Right arm planted on hip.
    sh_r = (cx + 24 * s, top_y + 12 * s)
    hand_r = (cx + 38 * s, hip_y - 6 * s)
    pygame.draw.line(surf, PLUM_DARK, sh_r, (cx + 40 * s, top_y + 36 * s), 9 * s)
    pygame.draw.line(surf, PLUM_DEEP, sh_r, (cx + 40 * s, top_y + 36 * s), 6 * s)
    pygame.draw.line(surf, PLUM_DARK, (cx + 40 * s, top_y + 36 * s), hand_r, 8 * s)
    pygame.draw.line(surf, PLUM_DEEP, (cx + 40 * s, top_y + 36 * s), hand_r, 5 * s)
    pygame.draw.circle(surf, (240, 240, 244), hand_r, 6 * s)

    # A grand FLARED heraldic mantle/collar — a wide split wing-collar framing
    # the double face, mismatched per side.
    neck_y = top_y + 2 * s
    for sgn, col in ((-1, GOLD), (1, PLUM_DEEP)):
        wing = [(cx, neck_y - 6 * s), (cx + sgn * 34 * s, neck_y - 18 * s),
                (cx + sgn * 30 * s, neck_y + 10 * s), (cx + sgn * 6 * s, neck_y + 8 * s)]
        pygame.draw.polygon(surf, col, wing)
        pygame.draw.polygon(surf, _shade(col, -60), wing, 2 * s)
        _bell(surf, cx + sgn * 32 * s, neck_y - 16 * s, 3 * s)

    # HEAD — ONE head, the DOUBLE FACE: split vertically, comedy half + tragedy
    # half. The macro split + one bright glint per half holds at small size.
    hr = 23 * s
    hy = neck_y - hr - 4 * s
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr + s)
    # Left (comedy) half painted on warm-lit skin; right (tragedy) half greyed.
    pygame.draw.polygon(surf, SKIN,
                        [(cx, hy - hr), (cx, hy + hr),
                         (cx - hr, hy + hr), (cx - hr, hy - hr)],)
    pygame.draw.circle(surf, SKIN, (cx, hy), hr)
    grey = pygame.Surface((hr * 2 + 2, hr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.polygon(grey, (60, 64, 78, 120),
                        [(hr, 0), (hr * 2, 0), (hr * 2, hr * 2), (hr, hr * 2)])
    cmask = pygame.Surface(grey.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(cmask, (255, 255, 255, 255), (hr, hr), hr)
    grey.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grey, (cx - hr, hy - hr))
    pygame.draw.line(surf, INK, (cx, hy - hr), (cx, hy + hr), 2 * s)
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr, 2 * s)
    _janus_face(surf, cx, hy, hr, s)
    # Split crown: a tall comedy spike on the bright side, a drooping tragedy
    # spire on the dark side, asymmetric.
    cap_y = hy - hr + 2 * s
    # Comedy spike (left) — tall, perky.
    lt = (cx - 26 * s, cap_y - 36 * s)
    pygame.draw.polygon(surf, VENOM, [(cx - 12 * s, cap_y), (cx - s, cap_y - 4 * s), lt])
    pygame.draw.polygon(surf, VENOM_DEEP, [(cx - 12 * s, cap_y), (cx - s, cap_y - 4 * s), lt], s)
    _bell(surf, lt[0], lt[1], 3 * s)
    # Tragedy spire (right) — drooping, heavy.
    rt = (cx + 30 * s, cap_y - 6 * s)
    pygame.draw.polygon(surf, PLUM_DEEP, [(cx + s, cap_y - 4 * s), (cx + 12 * s, cap_y), rt])
    pygame.draw.polygon(surf, PLUM_DARK, [(cx + s, cap_y - 4 * s), (cx + 12 * s, cap_y), rt], s)
    _bell(surf, rt[0], rt[1], 3 * s)
    # A central gold spike between them.
    ct = (cx + 2 * s, cap_y - 30 * s)
    pygame.draw.polygon(surf, GOLD, [(cx - 6 * s, cap_y - 2 * s), (cx + 8 * s, cap_y - 2 * s), ct])
    _bell(surf, ct[0], ct[1], 2 * s)


def _janus_face(surf, cx, hy, hr, s):
    # LEFT (comedy) half — bright wide grin, raised cheery brow, bright eye.
    pygame.draw.line(surf, PLUM_DARK, (cx - 16 * s, hy - 6 * s),
                     (cx - 4 * s, hy - 9 * s), 3 * s)  # raised brow
    pygame.draw.ellipse(surf, WHITE, (cx - 14 * s, hy - 4 * s, 10 * s, 9 * s))
    pygame.draw.circle(surf, INK, (cx - 9 * s, hy + s), 3 * s)
    _glint(surf, cx - 10 * s, hy - s, 2 * s)
    # comedy grin: big upturned half.
    pygame.draw.arc(surf, BLOOD, (cx - 18 * s, hy + 6 * s, 22 * s, 18 * s),
                    math.pi * 0.5, math.pi * 1.0, 3 * s)
    pygame.draw.polygon(surf, BONE,
                        [(cx - 14 * s, hy + 12 * s), (cx - s, hy + 13 * s),
                         (cx - 2 * s, hy + 16 * s), (cx - 13 * s, hy + 16 * s)])

    # RIGHT (tragedy) half — downturned snarl, furrowed-down brow, weeping eye.
    pygame.draw.line(surf, INK, (cx + 4 * s, hy - 9 * s),
                     (cx + 16 * s, hy - 4 * s), 3 * s)  # angry/sad down brow
    pygame.draw.ellipse(surf, (220, 224, 230), (cx + 4 * s, hy - 4 * s, 10 * s, 9 * s))
    pygame.draw.circle(surf, INK, (cx + 9 * s, hy + 2 * s), 3 * s)
    _glint(surf, cx + 8 * s, hy, 2 * s)
    # A blue tear running down the tragedy cheek.
    pygame.draw.polygon(surf, (150, 180, 210),
                        [(cx + 9 * s, hy + 6 * s), (cx + 11 * s, hy + 14 * s),
                         (cx + 7 * s, hy + 14 * s)])
    # tragedy snarl: downturned half with a fang.
    pygame.draw.arc(surf, BLOOD_DARK, (cx + s, hy + 10 * s, 22 * s, 20 * s),
                    math.pi * 1.0, math.pi * 1.5, 3 * s)
    pygame.draw.polygon(surf, BONE, [(cx + 4 * s, hy + 12 * s),
                                     (cx + 8 * s, hy + 12 * s),
                                     (cx + 6 * s, hy + 18 * s)])

    # A shared blood nose straddling the seam.
    pygame.draw.circle(surf, BLOOD, (cx, hy + 6 * s), 4 * s)
    pygame.draw.circle(surf, _shade(BLOOD, 80), (cx - s, hy + 4 * s), 2 * s)


# ═════════════════════════════════════════════════════════════════════════════
# ROUND 2 — DEVELOPMENT of the two chosen directions: THE PUPPETEER and THE
# JANUS HERALD. Two distinct takes per direction, all carrying the mandatory
# lineage anchors (belled jester cap, gold scalloped ruff, browcock grin+fang),
# all in the soured/bruised Plum & Lime palette. The art-director fixes are
# folded in: the Puppeteer silhouette is now MASS (coat/robe + cuffed limbs,
# never thin black sticks); the Janus faces are now PAINTED HARLEQUIN MASKS
# (no emoji smiley) over a BRUISED OXBLOOD banner.
# ═════════════════════════════════════════════════════════════════════════════


def _scallop_ruff(surf, cx, neck_y, half_w, s, lobes=9, r=7):
    """The lineage GOLD SCALLOPED RUFF — a fan of overlapping tarnished-gold
    lobes at the neck. Shared lineage anchor across all four bosses."""
    for i in range(lobes):
        t = i / (lobes - 1)
        rx = cx + int((-1 + 2 * t) * half_w)
        ry = neck_y + int(math.sin(t * math.pi) * -4 * s)
        pygame.draw.circle(surf, GOLD_DARK, (rx, ry), r * s + s)
        pygame.draw.circle(surf, GOLD, (rx, ry), r * s)
        pygame.draw.circle(surf, GOLD_LIT, (rx - 2 * s, ry - 2 * s), max(s, r * s // 3))


def _harlequin_band(surf, p0, p1, w, s, col_a, col_b, n=5):
    """A thick limb drawn as alternating harlequin colour bands between two
    points — the FILLED, MASS limb the art-director asked for (never a thin
    black stick). Returns the endpoint for chaining."""
    pygame.draw.line(surf, INK, p0, p1, w + 2 * s)
    for i in range(n):
        a = (p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n)
        b = (p0[0] + (p1[0] - p0[0]) * (i + 1) / n,
             p0[1] + (p1[1] - p0[1]) * (i + 1) / n)
        col = col_a if i % 2 else col_b
        pygame.draw.line(surf, col, a, b, w)
    return p1


def _gold_cuff(surf, x, y, r, s):
    """A flared tarnished-gold cuff ring at a hand/foot — replaces the thin
    black stick-ends the critique flagged."""
    pygame.draw.circle(surf, GOLD_DARK, (int(x), int(y)), r + s)
    pygame.draw.circle(surf, GOLD, (int(x), int(y)), r)
    pygame.draw.circle(surf, GOLD_LIT, (int(x - r // 2), int(y - r // 2)),
                       max(s, r // 2))


def _villain_face(surf, cx, hy, hr, s, brow_left=True, mood="grin"):
    """The lineage BROWCOCK GRIN + ONE FANG villain face — one cocked brow, a
    bright eye-glint per eye, a blood nose and a gleeful grin with a single
    fang. `mood='grin'` is the gleeful comedy read; `mood='tragedy'` keeps the
    SAME hard macro shapes but flips the grin into a sinister down-snarl with a
    weeping eye — still menacing, never sad-cute, never an emoji smiley."""
    bsgn = -1 if brow_left else 1
    # Cocked brow — one slammed-up hard bar (the macro shape that reads small).
    pygame.draw.line(surf, INK, (cx + bsgn * 13 * s, hy - 10 * s),
                     (cx + bsgn * 2 * s, hy - 6 * s), 4 * s)
    # The other brow low + level.
    pygame.draw.line(surf, INK, (cx - bsgn * 3 * s, hy - 5 * s),
                     (cx - bsgn * 13 * s, hy - 4 * s), 4 * s)
    for sgn in (-1, 1):
        ex = cx + sgn * 8 * s
        pygame.draw.ellipse(surf, WHITE, (ex - 6 * s, hy - 4 * s, 12 * s, 10 * s))
        pygame.draw.circle(surf, INK, (ex + sgn * 2 * s, hy + s), 3 * s)
        _glint(surf, ex + sgn * 1 * s, hy - s, 2 * s)
    if mood == "tragedy":
        # A painted weep-streak under the cocked eye (theatrical greasepaint,
        # not a cutesy cartoon tear) + a venom diamond mask-marking.
        pygame.draw.polygon(surf, VENOM_DEEP,
                            [(cx + bsgn * 8 * s, hy + 4 * s),
                             (cx + bsgn * 11 * s, hy + 16 * s),
                             (cx + bsgn * 5 * s, hy + 16 * s)])
    # Blood nose.
    pygame.draw.circle(surf, BLOOD, (cx, hy + 6 * s), 4 * s)
    pygame.draw.circle(surf, _shade(BLOOD, 80), (cx - s, hy + 4 * s), 2 * s)
    teeth_y = hy + 14 * s
    if mood == "tragedy":
        # Sinister downturned snarl — same width, flipped curve, baring a fang.
        pygame.draw.arc(surf, BLOOD_DARK, (cx - 14 * s, hy + 12 * s, 28 * s, 16 * s),
                        math.pi * 1.0, math.pi * 2.0, 3 * s)
        gum = [(cx - 12 * s, teeth_y + 8 * s), (cx + 12 * s, teeth_y + 8 * s),
               (cx + 9 * s, teeth_y + 4 * s), (cx - 9 * s, teeth_y + 4 * s)]
    else:
        # Gleeful wide grin — upturned, baring a tooth row.
        pygame.draw.arc(surf, BLOOD_DARK, (cx - 14 * s, hy + 9 * s, 28 * s, 14 * s),
                        math.pi, math.tau, 3 * s)
        gum = [(cx - 12 * s, teeth_y), (cx + 12 * s, teeth_y),
               (cx + 9 * s, teeth_y + 4 * s), (cx - 9 * s, teeth_y + 4 * s)]
    pygame.draw.polygon(surf, BONE, gum)
    base_y = gum[2][1]
    for tx in range(-2, 3):
        gx = cx + tx * 5 * s
        pygame.draw.line(surf, BLOOD_DARK, (gx, gum[0][1]), (gx, base_y), s)
    # The ONE fang.
    fang_top = base_y if mood != "tragedy" else gum[0][1]
    pygame.draw.polygon(surf, BONE,
                        [(cx - 9 * s, fang_top), (cx - 5 * s, fang_top),
                         (cx - 7 * s, fang_top + (5 * s if mood != "tragedy" else 6 * s))])


def _evolved_cap(surf, cx, cap_y, s, lean=0, scale=1.0):
    """The lineage BELLED JESTER CAP, EVOLVED — three asymmetric, split-colour
    points (taller, leaning), each tipped with a tarnished-gold bell. `lean`
    skews the whole cap; `scale` stretches it. Clearly OUR cap, grown nastier."""
    pts = [(-1, -16, -38, VENOM, VENOM_DEEP),
           (0, 4, -48, GOLD, GOLD_DARK),
           (1, 22, -34, PLUM_BRUISE, PLUM_DARK)]
    for sgn, dx, dy, col, dk in pts:
        dx = dx * scale + lean * abs(dy) * 0.3
        dy = dy * scale
        tip = (cx + dx * s, cap_y + dy * s)
        base = [(cx - 10 * s, cap_y + 2 * s), (cx + 10 * s, cap_y + 2 * s), tip]
        pygame.draw.polygon(surf, col, base)
        pygame.draw.polygon(surf, dk, base, s)
        # Split-colour stripe down the spire.
        mid = ((base[0][0] + tip[0]) / 2, (base[0][1] + tip[1]) / 2)
        pygame.draw.line(surf, _shade(col, -50), mid, tip, s)
        _bell(surf, tip[0], tip[1], 3 * s)


# ─────────────────────────────────────────────────────────────────────────────
# PUPPETEER TAKE A — THE STRING-MASTER
# A TOWERING, robed mastermind holding a marionette CONTROL-CROSS aloft in both
# fists, strings cascading from it. The body is FILLED by a long dramatic
# bell-fringed robe; arms are thick harlequin-banded with gold cuffs. Grandiose
# gleeful "I work the strings" menace.
# ─────────────────────────────────────────────────────────────────────────────

def build_string_master(surf, cx, feet_y, K):
    s = K
    # Long dramatic robe — a tall flaring column that gives the figure MASS
    # (the fix for the round-1 stilt-void). Hem flares wide at the ground.
    hem_y = feet_y - 8 * s
    shoulder_y = feet_y - 168 * s
    hem_w = 56 * s
    sh_w = 30 * s
    robe = [(cx - sh_w, shoulder_y + 8 * s), (cx + sh_w, shoulder_y + 8 * s),
            (cx + hem_w, hem_y), (cx - hem_w, hem_y)]
    pygame.draw.polygon(surf, PLUM_DEEP, robe)
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - sh_w, shoulder_y + 8 * s), (cx - 6 * s, shoulder_y + 8 * s),
                         (cx - 18 * s, hem_y), (cx - hem_w, hem_y)])
    pygame.draw.polygon(surf, PLUM_DARK,
                        [(cx + 10 * s, shoulder_y + 8 * s), (cx + sh_w, shoulder_y + 8 * s),
                         (cx + hem_w, hem_y), (cx + 24 * s, hem_y)])
    pygame.draw.polygon(surf, PLUM_DARK, robe, 2 * s)
    # Venom centre-placket with gold frog-bells running the robe.
    pygame.draw.polygon(surf, VENOM_DEEP,
                        [(cx - 9 * s, shoulder_y + 10 * s), (cx + 9 * s, shoulder_y + 10 * s),
                         (cx + 14 * s, hem_y - 2 * s), (cx - 14 * s, hem_y - 2 * s)])
    pygame.draw.polygon(surf, VENOM,
                        [(cx - 6 * s, shoulder_y + 10 * s), (cx + 4 * s, shoulder_y + 10 * s),
                         (cx + 7 * s, hem_y - 2 * s), (cx - 9 * s, hem_y - 2 * s)])
    for i in range(6):
        by = shoulder_y + 18 * s + (hem_y - shoulder_y - 20 * s) * i / 5
        _bell(surf, cx - s, by, 3 * s)
    # Dagged bell-fringed hem giving the robe a theatrical skirt.
    n = 9
    for i in range(n):
        x0 = cx - hem_w + 2 * hem_w * i / n
        x1 = cx - hem_w + 2 * hem_w * (i + 1) / n
        mid = (x0 + x1) / 2
        col = VENOM if i % 2 else GOLD
        dag = [(x0, hem_y - 2 * s), (x1, hem_y - 2 * s), (mid, hem_y + 10 * s)]
        pygame.draw.polygon(surf, col, dag)
        pygame.draw.polygon(surf, _shade(col, -60), dag, s)
        _bell(surf, mid, hem_y + 10 * s, 2 * s)
    # Two robe-hem feet peeking, in gold cuffs (no thin sticks).
    for sgn in (-1, 1):
        fx = cx + sgn * 28 * s
        _gold_cuff(surf, fx, feet_y - 4 * s, 6 * s, s)

    # Broad gold epaulet shelves the thick arms hang off.
    for sgn in (-1, 1):
        shx = cx + sgn * sh_w
        ep = [(cx + sgn * 14 * s, shoulder_y + 6 * s),
              (shx + sgn * 12 * s, shoulder_y),
              (shx + sgn * 8 * s, shoulder_y + 16 * s),
              (cx + sgn * 12 * s, shoulder_y + 16 * s)]
        pygame.draw.polygon(surf, GOLD, ep)
        pygame.draw.polygon(surf, GOLD_DARK, ep, s)

    # The CONTROL-CROSS held ALOFT in both fists — the marionette gag, raised
    # like a trophy. Drawn above the head between the two raised hands.
    cross_y = shoulder_y - 44 * s
    bar_x0, bar_x1 = cx - 40 * s, cx + 40 * s
    # Thick arms reaching UP to the cross ends — harlequin-banded, gold cuffs.
    for sgn, col_a, col_b in ((-1, VENOM, PLUM_BRUISE), (1, PLUM_BRUISE, VENOM)):
        sh = (cx + sgn * (sh_w - 4 * s), shoulder_y + 12 * s)
        elbow = (cx + sgn * 44 * s, shoulder_y - 6 * s)
        hand = (cx + sgn * 40 * s, cross_y + 2 * s)
        _harlequin_band(surf, sh, elbow, 10 * s, s, col_a, col_b)
        _harlequin_band(surf, elbow, hand, 8 * s, s, col_b, col_a)
        _gold_cuff(surf, hand[0], hand[1], 7 * s, s)
    # The wooden control-cross itself: a horizontal bar + a short vertical, in
    # tarnished gold, with string anchor-pegs.
    pygame.draw.line(surf, GOLD_DARK, (bar_x0, cross_y + 2 * s), (bar_x1, cross_y + 2 * s), 7 * s)
    pygame.draw.line(surf, GOLD, (bar_x0, cross_y), (bar_x1, cross_y), 4 * s)
    pygame.draw.line(surf, GOLD_DARK, (cx, cross_y - 18 * s), (cx, cross_y + 6 * s), 7 * s)
    pygame.draw.line(surf, GOLD, (cx, cross_y - 18 * s), (cx, cross_y + 6 * s), 4 * s)
    pygame.draw.line(surf, GOLD, (cx - 16 * s, cross_y - 12 * s), (cx + 16 * s, cross_y - 12 * s), 4 * s)
    for px in (bar_x0 + 6 * s, cx - 16 * s, cx + 16 * s, bar_x1 - 6 * s):
        pygame.draw.circle(surf, GOLD_LIT, (int(px), int(cross_y)), 2 * s)
    # Strings cascading from the cross pegs down past the robe — taut filaments.
    anchors = [(bar_x0 + 6 * s, cross_y), (cx - 16 * s, cross_y - 12 * s),
               (cx + 16 * s, cross_y - 12 * s), (bar_x1 - 6 * s, cross_y)]
    drops = [cx - 36 * s, cx - 12 * s, cx + 12 * s, cx + 36 * s]
    for (ax, ay), dx in zip(anchors, drops):
        pygame.draw.line(surf, STRING_DARK, (ax + s, ay), (dx + s, hem_y + 6 * s), s)
        pygame.draw.line(surf, STRING_COL, (ax, ay), (dx, hem_y + 6 * s), s)

    # The lineage GOLD SCALLOPED RUFF.
    _scallop_ruff(surf, cx, shoulder_y, 30 * s, s, lobes=9, r=7)

    # HEAD — gaunt but not skeletal; the gleeful mastermind face.
    hr = 20 * s
    hy = shoulder_y - hr - 4 * s
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr + s)
    pygame.draw.circle(surf, SKIN, (cx, hy), hr)
    _bruise(surf, cx + 11 * s, hy + 6 * s, 6 * s, 5 * s, 70)
    _villain_face(surf, cx, hy, hr, s, brow_left=True, mood="grin")

    # The EVOLVED belled jester cap — tall, leaning, split-colour.
    _evolved_cap(surf, cx, hy - hr + 4 * s, s, lean=0.15, scale=1.0)


# ─────────────────────────────────────────────────────────────────────────────
# PUPPETEER TAKE B — THE TANGLE-LORD
# A HUNCHED schemer crouched over a tangle of strings, with two tiny dangling
# marionette-MINIONS swinging off its clawed, gold-cuffed hands. A heavy
# hunched robe gives the body mass; the cap flops forward conspiratorially.
# Reads as the same string-master lineage, lower and meaner.
# ─────────────────────────────────────────────────────────────────────────────

def _mini_marionette(surf, x, top_y, foot_y, s, col):
    """A tiny dangling marionette-minion: a string, a bead head, a banded body
    and limp little limbs — a small puppet hanging off the boss's hand."""
    pygame.draw.line(surf, STRING_COL, (x, top_y), (x, top_y + 14 * s), s)
    hx, hcy = x, top_y + 18 * s
    pygame.draw.circle(surf, SKIN, (hx, hcy), 5 * s)
    pygame.draw.circle(surf, SKIN_SHADE, (hx, hcy), 5 * s, s)
    pygame.draw.circle(surf, INK, (hx - 2 * s, hcy - s), s)
    pygame.draw.circle(surf, INK, (hx + 2 * s, hcy - s), s)
    # Tiny cap nub.
    pygame.draw.polygon(surf, col, [(hx - 4 * s, hcy - 4 * s),
                                    (hx + 4 * s, hcy - 4 * s), (hx, hcy - 11 * s)])
    _bell(surf, hx, hcy - 11 * s, 2 * s)
    # Banded body.
    bo_y = hcy + 5 * s
    _harlequin_band(surf, (hx, bo_y), (hx, bo_y + 14 * s), 7 * s, s, col, GOLD, n=3)
    # Limp dangling limbs + foot strings.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _shade(col, -50), (hx, bo_y + 2 * s),
                         (hx + sgn * 7 * s, bo_y + 12 * s), 3 * s)
        pygame.draw.line(surf, _shade(col, -50), (hx, bo_y + 14 * s),
                         (hx + sgn * 5 * s, foot_y), 3 * s)
        _bell(surf, hx + sgn * 5 * s, foot_y, 2 * s)


def build_tangle_lord(surf, cx, feet_y, K):
    s = K
    # A heavy HUNCHED robe — a broad rounded mass leaning forward, hem pooling on
    # the ground. The hunch is the silhouette signature.
    hem_y = feet_y - 8 * s
    waist_y = feet_y - 96 * s
    hump_y = feet_y - 132 * s
    hem_w = 60 * s
    robe = [(cx - 26 * s, hump_y + 6 * s), (cx + 30 * s, hump_y - 2 * s),
            (cx + 40 * s, waist_y), (cx + hem_w, hem_y),
            (cx - hem_w, hem_y), (cx - 38 * s, waist_y)]
    pygame.draw.polygon(surf, PLUM_DEEP, robe)
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - 26 * s, hump_y + 6 * s), (cx - 4 * s, hump_y + 2 * s),
                         (cx - 20 * s, hem_y), (cx - hem_w, hem_y), (cx - 38 * s, waist_y)])
    pygame.draw.polygon(surf, PLUM_DARK, robe, 2 * s)
    # A bulging hunched-back hump rounding the top-right of the robe.
    hump = pygame.Rect(0, 0, 64 * s, 56 * s)
    hump.center = (cx + 6 * s, hump_y + 18 * s)
    pygame.draw.ellipse(surf, PLUM_DARK, hump)
    pygame.draw.ellipse(surf, PLUM_DEEP, hump.inflate(-4 * s, -4 * s))
    pygame.draw.arc(surf, PLUM_BRUISE, hump.inflate(-8 * s, -8 * s),
                    math.pi * 0.9, math.pi * 1.5, 2 * s)
    # Venom diamonds scattered down the robe (harlequin motif, MASS not void).
    for (dx, dy) in ((-22, 40), (4, 56), (-30, 72), (10, 82), (-12, 64)):
        px, py = cx + dx * s, waist_y + dy * s
        d = 6 * s
        pygame.draw.polygon(surf, VENOM, [(px, py - d), (px + d, py), (px, py + d), (px - d, py)])
        pygame.draw.polygon(surf, VENOM_DEEP, [(px, py - d), (px + d, py), (px, py + d), (px - d, py)], s)
    # Bell-fringed hem.
    n = 9
    for i in range(n):
        x0 = cx - hem_w + 2 * hem_w * i / n
        x1 = cx - hem_w + 2 * hem_w * (i + 1) / n
        mid = (x0 + x1) / 2
        col = GOLD if i % 2 else VENOM
        dag = [(x0, hem_y - 2 * s), (x1, hem_y - 2 * s), (mid, hem_y + 10 * s)]
        pygame.draw.polygon(surf, col, dag)
        pygame.draw.polygon(surf, _shade(col, -60), dag, s)
        _bell(surf, mid, hem_y + 10 * s, 2 * s)
    for sgn in (-1, 1):
        _gold_cuff(surf, cx + sgn * 30 * s, feet_y - 4 * s, 6 * s, s)

    # Both thick arms reach DOWN-and-FORWARD over the tangle, clawed gold-cuffed
    # hands each dangling a tiny marionette-minion. Harlequin-banded — MASS.
    hands = []
    for sgn, col_a, col_b in ((-1, VENOM, PLUM_BRUISE), (1, PLUM_BRUISE, VENOM)):
        sh = (cx + sgn * 20 * s, waist_y - 6 * s)
        elbow = (cx + sgn * 48 * s, waist_y + 12 * s)
        hand = (cx + sgn * 40 * s, waist_y + 40 * s)
        _harlequin_band(surf, sh, elbow, 10 * s, s, col_a, col_b)
        _harlequin_band(surf, elbow, hand, 8 * s, s, col_b, col_a)
        _gold_cuff(surf, hand[0], hand[1], 7 * s, s)
        # Three clawed gold fingers spreading the strings.
        for f in (-1, 0, 1):
            fx = hand[0] + f * 5 * s
            pygame.draw.line(surf, GOLD_DARK, hand, (fx, hand[1] + 10 * s), 2 * s)
            pygame.draw.circle(surf, GOLD, (fx, hand[1] + 10 * s), 2 * s)
        hands.append(hand)
    # The TANGLE of crossing control-strings sagging between the two hands.
    lh, rh = hands
    for k in range(5):
        t = k / 4
        sag = 18 * s + int(math.sin(t * math.pi) * 10 * s)
        ax = lh[0] + (rh[0] - lh[0]) * t
        pygame.draw.line(surf, STRING_DARK, (lh[0], lh[1] + 10 * s),
                         (ax, lh[1] + sag), s)
        pygame.draw.line(surf, STRING_COL, (rh[0], rh[1] + 10 * s),
                         (ax, rh[1] + sag), s)
    # Two tiny dangling marionette-minions swinging off the hands.
    _mini_marionette(surf, lh[0] - 4 * s, lh[1] + 12 * s, waist_y + 92 * s, s, VENOM)
    _mini_marionette(surf, rh[0] + 4 * s, rh[1] + 12 * s, waist_y + 86 * s, s, PLUM_BRUISE)

    # The lineage GOLD SCALLOPED RUFF, tilted with the hunch.
    _scallop_ruff(surf, cx + 4 * s, hump_y + 6 * s, 26 * s, s, lobes=8, r=7)

    # HEAD — craned forward off the hunch, conspiratorial.
    hr = 20 * s
    hy = hump_y - hr + 2 * s
    hcx = cx + 6 * s
    pygame.draw.circle(surf, SKIN_SHADE, (hcx, hy), hr + s)
    pygame.draw.circle(surf, SKIN, (hcx, hy), hr)
    _bruise(surf, hcx + 10 * s, hy + 7 * s, 6 * s, 5 * s, 70)
    _villain_face(surf, hcx, hy, hr, s, brow_left=False, mood="grin")

    # The EVOLVED belled cap flopping FORWARD over the brow (conspiratorial).
    _evolved_cap(surf, hcx, hy - hr + 4 * s, s, lean=-0.45, scale=0.92)


# ─────────────────────────────────────────────────────────────────────────────
# TANGLE-LORD — SHIP POLISH
# The chosen late-game boss, refined to a hero read. Round-2's tangle-lord was
# the right idea but soft: the hunch read as a separate bubble, the minions were
# muddy beads, the tangle floated mid-body instead of cradling LOW. This polish
# fuses hunch + cap + cradled tangle into ONE menacing schemer shape, enlarges
# the two minions into legible limp puppets, and hardens the face so it survives
# the 90px gameplay scale. Same character, evolved — not a redraw.
# ─────────────────────────────────────────────────────────────────────────────

def _minion_polish(surf, top_x, top_y, s, col, swing=0, scale=1.0):
    """A miniature limp JESTER — unmistakably "tiny HIM": a 2-point belled cap
    mirroring the parent's colours, a round dot-grin face, a banded barrel body,
    and a wholly limp dead-weight pose (arms dropped straight down, legs hanging
    X-crossed, belled feet). The dual belled cap + the dot-grin are what make it
    read as a mini-jester rather than an egg/skull at the in-game downscale.
    `swing` skews the puppet so the pair read as caught mid-jerk; `scale` sizes
    it up so the joke survives the ~92px gameplay read. `col` is the puppet's
    own loud half (one lime, one plum) — the other cap point + the body take the
    complementary lineage colour."""
    u = s * scale
    other = PLUM_BRUISE if col == VENOM else VENOM
    # Two taut control filaments converging onto the puppet head.
    hx = top_x + int(swing * 9 * u)
    hcy = top_y + int(16 * u)
    for fx in (-4, 4):
        pygame.draw.line(surf, STRING_DARK, (top_x + fx * s, top_y),
                         (hx, hcy - 6 * u), max(1, s))
    pygame.draw.line(surf, STRING_COL, (top_x, top_y), (hx, hcy - 7 * u),
                     max(1, s))
    # Round head with a hard dark keyline (reads as a head, not a bead).
    hrad = int(8 * u)
    pygame.draw.circle(surf, INK, (hx, hcy), hrad + s)
    pygame.draw.circle(surf, SKIN_SHADE, (hx, hcy), hrad)
    pygame.draw.circle(surf, SKIN, (hx, hcy), hrad - s)
    # Dot-grin face — two ink dot eyes + an upturned grin arc (clearly a jester
    # face, the comedy cue that separates it from a skull).
    for ex in (-3, 3):
        pygame.draw.circle(surf, INK, (hx + int(ex * u), hcy - int(1.5 * u)),
                           max(1, int(2 * u)))
    pygame.draw.arc(surf, BLOOD_DARK,
                    (hx - int(4 * u), hcy, int(8 * u), int(6 * u)),
                    math.pi, math.tau, max(1, int(1.4 * u)))
    # The TWO-POINT belled jester cap — one point in the puppet's loud colour,
    # one in the complement, mirroring the parent. THIS is the "mini-HIM" cue.
    cap_b = hcy - hrad + s
    for psgn, pcol in ((-1, col), (1, other)):
        tip = (hx + int((psgn * 7 + swing * 4) * u), cap_b - int(13 * u))
        base = [(hx - int(7 * u), cap_b), (hx + int(7 * u), cap_b), tip]
        pygame.draw.polygon(surf, pcol, base)
        pygame.draw.polygon(surf, _shade(pcol, -55), base, s)
        _bell(surf, tip[0], tip[1], max(2, int(2 * u)))
    # Banded barrel body — a clear harlequin torso under the head.
    bo_y = hcy + hrad
    bo_bot = bo_y + int(16 * u)
    body_cx = hx + int(swing * 5 * u)
    _harlequin_band(surf, (hx, bo_y), (body_cx, bo_bot), int(11 * u), s,
                    col, other, n=3)
    # LIMP arms hanging straight DOWN off the shoulders (dead-weight, belled).
    for sgn in (-1, 1):
        sh = (hx + int(sgn * 5 * u), bo_y + int(2 * u))
        hand = (sh[0] + int(sgn * 3 * u), bo_y + int(13 * u))
        pygame.draw.line(surf, _shade(col, -45), sh, hand, max(2, int(3.5 * u)))
        _bell(surf, hand[0], hand[1], max(1, int(1.8 * u)))
    # X-crossed limp legs, belled feet — the unmistakable lifeless-doll dangle.
    crot = (body_cx, bo_bot)
    for sgn in (-1, 1):
        knee = (body_cx - int(sgn * 4 * u), bo_bot + int(7 * u))
        foot = (body_cx + int(sgn * 9 * u), bo_bot + int(13 * u))
        pygame.draw.line(surf, _shade(col, -45), crot, knee, max(2, int(3.5 * u)))
        pygame.draw.line(surf, _shade(col, -45), knee, foot, max(2, int(3.5 * u)))
        _bell(surf, foot[0], foot[1], max(1, int(2 * u)))


def build_tangle_lord_polish(surf, cx, feet_y, K):
    s = K
    # Anchor everything to a forward-leaning lean axis: the whole figure tilts
    # left over its strings so the hunch + craned head + cradled tangle read as
    # ONE continuous schemer arc rather than a robe with parts stuck on.
    hem_y = feet_y - 8 * s
    waist_y = feet_y - 100 * s
    hump_y = feet_y - 150 * s
    hem_w = 64 * s
    # The robe: a heavy mass whose top-left shoulder RISES into the hunch, so the
    # back-hump is part of the body outline, not a separate bubble.
    robe = [(cx - 40 * s, hump_y + 10 * s),    # high hunched shoulder (back)
            (cx + 4 * s, hump_y - 6 * s),       # crest of the hunch
            (cx + 30 * s, waist_y - 18 * s),    # front shoulder, lower
            (cx + 46 * s, waist_y + 6 * s),
            (cx + hem_w, hem_y),
            (cx - hem_w + 6 * s, hem_y),
            (cx - 50 * s, waist_y)]
    pygame.draw.polygon(surf, PLUM_DEEP, robe)
    # Lit front-left facet + dark back-right to sculpt the hunch volume.
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - 50 * s, waist_y), (cx - 18 * s, waist_y + 6 * s),
                         (cx - 30 * s, hem_y), (cx - hem_w + 6 * s, hem_y)])
    pygame.draw.polygon(surf, PLUM_DARK,
                        [(cx + 4 * s, hump_y - 6 * s), (cx + 30 * s, waist_y - 18 * s),
                         (cx + 46 * s, waist_y + 6 * s), (cx + 22 * s, waist_y + 10 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, robe, 2 * s)
    # The hunched-back hump: an over-the-shoulder bulge fused onto the back-left
    # so the silhouette crests there. A lit ridge sells it as rounded muscle/cloth.
    hump = pygame.Rect(0, 0, 72 * s, 64 * s)
    hump.center = (cx - 12 * s, hump_y + 22 * s)
    pygame.draw.ellipse(surf, PLUM_DARK, hump)
    pygame.draw.ellipse(surf, PLUM_DEEP, hump.inflate(-5 * s, -5 * s))
    pygame.draw.arc(surf, PLUM_BRUISE, hump.inflate(-10 * s, -10 * s),
                    math.pi * 0.85, math.pi * 1.45, 3 * s)
    # ONE clean venom-diamond ridge running down the crest of the hunch — a
    # single descending-size spine, the boss's "armoured back" read. The rest of
    # the robe is deliberately CLEARED of diamonds so the silhouette stays clean
    # and the focal hierarchy (face -> tangle+minions) wins.
    crest = [(cx - 22 * s, hump_y - 2 * s), (cx - 8 * s, hump_y + 16 * s),
             (cx + 4 * s, hump_y + 38 * s), (cx + 12 * s, hump_y + 62 * s),
             (cx + 18 * s, hump_y + 86 * s)]
    for k, (px, py) in enumerate(crest):
        d = (5 - k) * s + 5 * s
        # Dark seat so each diamond sits proud of the plum (separation).
        pygame.draw.polygon(surf, PLUM_DARK,
                            [(px, py - d - s), (px + d + s, py),
                             (px, py + d + s), (px - d - s, py)])
        pygame.draw.polygon(surf, VENOM_DEEP,
                            [(px, py - d), (px + d, py), (px, py + d), (px - d, py)])
        pygame.draw.polygon(surf, VENOM,
                            [(px, py - d + s), (px + d - s, py), (px, py + d - s),
                             (px - d + s, py)])
    # Bell-fringed hem — QUIETED: ~40% fewer dags/bells so the lower third reads
    # as a calm dark base and the minions own it.
    n = 6
    for i in range(n):
        x0 = cx - hem_w + 6 * s + (2 * hem_w - 6 * s) * i / n
        x1 = cx - hem_w + 6 * s + (2 * hem_w - 6 * s) * (i + 1) / n
        mid = (x0 + x1) / 2
        col = GOLD if i % 2 else VENOM
        dag = [(x0, hem_y - 2 * s), (x1, hem_y - 2 * s), (mid, hem_y + 11 * s)]
        pygame.draw.polygon(surf, col, dag)
        pygame.draw.polygon(surf, _shade(col, -60), dag, s)
        # Only every other dag carries a bell — thins the gold clutter further.
        if i % 2 == 0:
            _bell(surf, mid, hem_y + 11 * s, 2 * s)
    for sgn in (-1, 1):
        _gold_cuff(surf, cx + sgn * 30 * s - 6 * s, feet_y - 4 * s, 6 * s, s)

    # Both thick arms reach DOWN-and-OUT, cradling the tangle LOW and WIDE in
    # front of the gut — the downward cradle is the "hunched over his strings"
    # read. Hands sit WIDE apart and well below the waist so the two minions hang
    # outboard of the robe edge (the robe must not swallow them) and the tangle
    # slings in a deep bowl between them.
    hands = []
    for sgn, col_a, col_b in ((-1, VENOM, PLUM_BRUISE), (1, PLUM_BRUISE, VENOM)):
        sh = (cx + sgn * 24 * s - 6 * s, waist_y - 10 * s)
        elbow = (cx + sgn * 54 * s - 4 * s, waist_y + 16 * s)
        hand = (cx + sgn * 50 * s - 4 * s, waist_y + 40 * s)
        _harlequin_band(surf, sh, elbow, 11 * s, s, col_a, col_b)
        _harlequin_band(surf, elbow, hand, 9 * s, s, col_b, col_a)
        _gold_cuff(surf, hand[0], hand[1], 8 * s, s)
        # Three clawed gold fingers curling DOWN over the strings (a grip, not a
        # splay) — claws hook toward the puppets below.
        for f in (-1, 0, 1):
            tipx = hand[0] + f * 5 * s
            tipy = hand[1] + 12 * s + abs(f) * 2 * s
            pygame.draw.line(surf, GOLD_DARK, hand, (tipx, tipy), 3 * s)
            pygame.draw.line(surf, GOLD, hand, (tipx, tipy), s)
            pygame.draw.circle(surf, GOLD_DARK, (tipx, tipy), 2 * s)
        hands.append(hand)
    lh, rh = hands
    # The cradled TANGLE rebuilt as a SHAPE, not a mesh: three BOLD confident
    # sagging catenary lines slung hand-to-hand, each first laid down as a faint
    # plum drop-shadow (separation against the dark robe) then a thick off-white
    # cord with a brighter rim-light on top. Exaggerated sag so it reads as
    # "holding strings" even at the 92px gameplay scale.
    def _catenary(y0, dip, weight, col, shadow=True):
        pts = []
        for k in range(0, 21):
            t = k / 20
            x = lh[0] + 4 * s + (rh[0] - lh[0] - 8 * s) * t
            y = y0 + int(math.sin(t * math.pi) * dip)
            pts.append((x, y))
        if shadow:
            shp = [(x, y + 3 * s) for x, y in pts]
            pygame.draw.lines(surf, PLUM_DARK, False, shp, weight + 2 * s)
        pygame.draw.lines(surf, STRING_DARK, False, pts, weight + s)
        pygame.draw.lines(surf, col, False, pts, weight)
        rim = [(x, y - max(1, weight // 2)) for x, y in pts]
        pygame.draw.lines(surf, (245, 242, 228), False, rim, max(1, s))
        return pts
    base_y = max(lh[1], rh[1]) + 16 * s
    _catenary(base_y, 26 * s, 3 * s, STRING_COL)
    _catenary(base_y + 8 * s, 34 * s, 4 * s, STRING_COL)
    _catenary(base_y - 4 * s, 18 * s, 2 * s, STRING_DARK, shadow=False)
    # Two deliberate KNOT-BLOBS where the cords snarl (bold, not specks).
    knot_y = base_y + 30 * s
    for kx, kr in ((-12, 5), (8, 6)):
        kxx = cx + kx * s - 4 * s
        pygame.draw.circle(surf, PLUM_DARK, (kxx, knot_y + 3 * s), kr * s + s)
        pygame.draw.circle(surf, STRING_DARK, (kxx, knot_y), kr * s)
        pygame.draw.circle(surf, STRING_COL, (kxx, knot_y), kr * s - 2 * s)
        pygame.draw.circle(surf, (245, 242, 228),
                           (kxx - 2 * s, knot_y - 2 * s), max(1, kr * s // 3))
    # The two MINIONS — enlarged + pushed OUTBOARD so the robe can't swallow them.
    # They hang at staggered heights (caught mid-jerk) and own the lower third.
    _minion_polish(surf, lh[0] - 4 * s, lh[1] + 14 * s, s, VENOM,
                   swing=-0.55, scale=1.25)
    _minion_polish(surf, rh[0] + 4 * s, rh[1] + 14 * s, s, PLUM_BRUISE,
                   swing=0.5, scale=1.4)

    # The lineage GOLD SCALLOPED RUFF, tilted forward off the craned neck.
    _scallop_ruff(surf, cx - 6 * s, hump_y + 8 * s, 26 * s, s, lobes=8, r=7)

    # HEAD — craned forward + down off the hunch crest, conspiratorial. Sits
    # OVER the tangle so the eyeline leads straight to the puppets (the schemer
    # watching his strings).
    hr = 22 * s
    hcx = cx - 4 * s
    hy = hump_y - hr + 6 * s
    pygame.draw.circle(surf, SKIN_SHADE, (hcx, hy), hr + s)
    pygame.draw.circle(surf, SKIN, (hcx, hy), hr)
    _bruise(surf, hcx + 11 * s, hy + 8 * s, 6 * s, 5 * s, 70)
    _bruise(surf, hcx - 13 * s, hy + 2 * s, 4 * s, 6 * s, 55)
    _villain_face(surf, hcx, hy, hr, s, brow_left=False, mood="grin")

    # The EVOLVED belled cap flopping hard FORWARD over the brow — the flop is a
    # signature, and its bell tips lead the eye down toward the strings.
    _evolved_cap(surf, hcx, hy - hr + 5 * s, s, lean=-0.6, scale=1.0)


# ─────────────────────────────────────────────────────────────────────────────
# TANGLE-LORD — SHIP POLISH r2
# The face, soured palette, gold ruff, and hunched grandiose silhouette of
# polish r1 were called SHIP-QUALITY and are carried over UNCHANGED (same robe,
# hump, crest-ridge spine, quieted hem, craned head + KEPT face, forward cap).
# r2 fixes ONLY the defining feature that failed the ~92px gameplay gate: the
# minions and the tangle. The minions become OBVIOUS mini-jesters — each a tiny
# HIM, with a 2-point belled cap mirroring the parent, a dot-grin, and a limp
# X-legged dangle — enlarged and pushed OUTBOARD/FORWARD so the robe can't
# swallow them. The tangle becomes a confident SHAPE — two-to-three bold sagging
# cords with deliberate knots and a rim-light that lifts it off the dark plum.
# ─────────────────────────────────────────────────────────────────────────────

def _minion_polish_2(surf, top_x, top_y, s, col, swing=0, scale=1.0):
    """An OBVIOUS miniature limp jester — "tiny HIM" at gameplay scale. Reads as
    a mini-jester (not an egg/skull) because of three loud cues that survive the
    downscale: a clear TWO-POINT belled cap split into the parent's lime+plum, a
    bold dot-grin face (two big ink eyes + an upturned blood grin), and a wholly
    LIMP dead-doll pose — arms dropped straight down, legs hanging X-crossed,
    every tip belled. Drawn with a hard INK keyline and a lit body band so the
    puppet wins ~20% more contrast against both the dark robe and the sky.
    `swing` skews the puppet so the pair read as caught mid-jerk; `col` is the
    puppet's own loud half (one lime, one plum), the complement filling the rest."""
    u = s * scale
    other = PLUM_BRUISE if col == VENOM else VENOM
    # Two taut control filaments converging onto the puppet head (with a faint
    # dark backing so the threads separate from the sky and the robe).
    hx = top_x + int(swing * 10 * u)
    hcy = top_y + int(18 * u)
    for fx in (-5, 5):
        pygame.draw.line(surf, STRING_DARK, (top_x + fx * s, top_y),
                         (hx, hcy - int(9 * u)), max(1, s))
    pygame.draw.line(surf, (245, 242, 228), (top_x, top_y),
                     (hx, hcy - int(10 * u)), max(1, s))
    # Round head — a hard INK keyline rings it so it reads as a head, never a
    # bead, even at the in-game downscale.
    hrad = int(9 * u)
    pygame.draw.circle(surf, INK, (hx, hcy), hrad + 2 * s)
    pygame.draw.circle(surf, SKIN_SHADE, (hx, hcy), hrad)
    pygame.draw.circle(surf, SKIN, (hx - s, hcy - s), hrad - s)
    # Bold dot-grin face — big ink eyes + an upturned blood grin. This is the
    # comedy cue that says "jester", not "skull".
    for ex in (-4, 4):
        pygame.draw.circle(surf, INK, (hx + int(ex * u), hcy - int(2 * u)),
                           max(1, int(2.4 * u)))
        pygame.draw.circle(surf, WHITE, (hx + int(ex * u) - s, hcy - int(3 * u)),
                           max(1, int(0.9 * u)))
    pygame.draw.arc(surf, BLOOD,
                    (hx - int(5 * u), hcy + int(1 * u), int(10 * u), int(8 * u)),
                    math.pi * 1.05, math.pi * 1.95, max(2, int(2 * u)))
    # The TWO-POINT belled jester cap — one point in the puppet's loud colour,
    # one in the complement, mirroring the PARENT's lime/plum. The single
    # loudest "mini-HIM" cue; tips splay outward + flop with the swing.
    cap_b = hcy - hrad + s
    for psgn, pcol in ((-1, col), (1, other)):
        tip = (hx + int((psgn * 9 + swing * 5) * u), cap_b - int(15 * u))
        base = [(hx - int(8 * u), cap_b + s), (hx + int(8 * u), cap_b + s), tip]
        pygame.draw.polygon(surf, INK, base, max(1, s))   # keyline first (mass)
        pygame.draw.polygon(surf, pcol, base)
        pygame.draw.polygon(surf, _shade(pcol, -55), base, s)
        _bell(surf, tip[0], tip[1], max(2, int(2.4 * u)))
    # Banded barrel body — a clear harlequin torso, lit one band brighter than r1
    # so the puppet body separates from the robe behind it.
    bo_y = hcy + hrad
    bo_bot = bo_y + int(18 * u)
    body_cx = hx + int(swing * 6 * u)
    pygame.draw.line(surf, INK, (hx, bo_y), (body_cx, bo_bot), int(13 * u) + 2 * s)
    _harlequin_band(surf, (hx, bo_y), (body_cx, bo_bot), int(12 * u), s,
                    _shade(col, 30), other, n=3)
    # A tiny gold belt-bell at the waist — extra "dressed jester" read.
    _bell(surf, (hx + body_cx) // 2, (bo_y + bo_bot) // 2, max(1, int(2 * u)))
    # LIMP arms hanging straight DOWN off the shoulders (dead-weight, belled).
    for sgn in (-1, 1):
        sh = (hx + int(sgn * 6 * u), bo_y + int(2 * u))
        hand = (sh[0] + int(sgn * 3 * u), bo_y + int(15 * u))
        pygame.draw.line(surf, INK, sh, hand, max(2, int(4.2 * u)))
        pygame.draw.line(surf, col, sh, hand, max(2, int(3.2 * u)))
        _bell(surf, hand[0], hand[1], max(1, int(2 * u)))
    # X-crossed limp legs, belled feet — the unmistakable lifeless-doll dangle.
    crot = (body_cx, bo_bot)
    for sgn in (-1, 1):
        knee = (body_cx - int(sgn * 5 * u), bo_bot + int(8 * u))
        foot = (body_cx + int(sgn * 11 * u), bo_bot + int(15 * u))
        for a, b in ((crot, knee), (knee, foot)):
            pygame.draw.line(surf, INK, a, b, max(2, int(4.2 * u)))
            pygame.draw.line(surf, other, a, b, max(2, int(3.2 * u)))
        _bell(surf, foot[0], foot[1], max(1, int(2.2 * u)))


def build_tangle_lord_polish_2(surf, cx, feet_y, K):
    s = K
    # ── KEPT FROM r1 (ship-quality): the forward-leaning robe mass + back-hump,
    # the single venom-diamond crest-ridge spine, the quieted bell-fringe hem,
    # the gold scalloped ruff, the craned head + KEPT villain face, the forward-
    # flopped belled cap, the clawed gold-cuffed hooked grip. Geometry verbatim.
    hem_y = feet_y - 8 * s
    waist_y = feet_y - 100 * s
    hump_y = feet_y - 150 * s
    hem_w = 64 * s
    robe = [(cx - 40 * s, hump_y + 10 * s),
            (cx + 4 * s, hump_y - 6 * s),
            (cx + 30 * s, waist_y - 18 * s),
            (cx + 46 * s, waist_y + 6 * s),
            (cx + hem_w, hem_y),
            (cx - hem_w + 6 * s, hem_y),
            (cx - 50 * s, waist_y)]
    pygame.draw.polygon(surf, PLUM_DEEP, robe)
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx - 50 * s, waist_y), (cx - 18 * s, waist_y + 6 * s),
                         (cx - 30 * s, hem_y), (cx - hem_w + 6 * s, hem_y)])
    pygame.draw.polygon(surf, PLUM_DARK,
                        [(cx + 4 * s, hump_y - 6 * s), (cx + 30 * s, waist_y - 18 * s),
                         (cx + 46 * s, waist_y + 6 * s), (cx + 22 * s, waist_y + 10 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, robe, 2 * s)
    hump = pygame.Rect(0, 0, 72 * s, 64 * s)
    hump.center = (cx - 12 * s, hump_y + 22 * s)
    pygame.draw.ellipse(surf, PLUM_DARK, hump)
    pygame.draw.ellipse(surf, PLUM_DEEP, hump.inflate(-5 * s, -5 * s))
    pygame.draw.arc(surf, PLUM_BRUISE, hump.inflate(-10 * s, -10 * s),
                    math.pi * 0.85, math.pi * 1.45, 3 * s)
    crest = [(cx - 22 * s, hump_y - 2 * s), (cx - 8 * s, hump_y + 16 * s),
             (cx + 4 * s, hump_y + 38 * s), (cx + 12 * s, hump_y + 62 * s),
             (cx + 18 * s, hump_y + 86 * s)]
    for k, (px, py) in enumerate(crest):
        d = (5 - k) * s + 5 * s
        pygame.draw.polygon(surf, PLUM_DARK,
                            [(px, py - d - s), (px + d + s, py),
                             (px, py + d + s), (px - d - s, py)])
        pygame.draw.polygon(surf, VENOM_DEEP,
                            [(px, py - d), (px + d, py), (px, py + d), (px - d, py)])
        pygame.draw.polygon(surf, VENOM,
                            [(px, py - d + s), (px + d - s, py), (px, py + d - s),
                             (px - d + s, py)])
    # Hem — quieted one notch further than r1 (n=5) so the minions own the lower
    # third even more decisively. KEEP intent, slightly stronger.
    n = 5
    for i in range(n):
        x0 = cx - hem_w + 6 * s + (2 * hem_w - 6 * s) * i / n
        x1 = cx - hem_w + 6 * s + (2 * hem_w - 6 * s) * (i + 1) / n
        mid = (x0 + x1) / 2
        col = GOLD if i % 2 else VENOM
        dag = [(x0, hem_y - 2 * s), (x1, hem_y - 2 * s), (mid, hem_y + 11 * s)]
        pygame.draw.polygon(surf, col, dag)
        pygame.draw.polygon(surf, _shade(col, -60), dag, s)
        if i % 2 == 0:
            _bell(surf, mid, hem_y + 11 * s, 2 * s)
    for sgn in (-1, 1):
        _gold_cuff(surf, cx + sgn * 30 * s - 6 * s, feet_y - 4 * s, 6 * s, s)

    # Arms reach DOWN-and-OUT cradling the tangle low + WIDE. r2 spreads the
    # hands a touch wider still and drops them slightly so the bigger outboard
    # minions clear the robe edge with room to spare.
    hands = []
    for sgn, col_a, col_b in ((-1, VENOM, PLUM_BRUISE), (1, PLUM_BRUISE, VENOM)):
        sh = (cx + sgn * 24 * s - 6 * s, waist_y - 10 * s)
        elbow = (cx + sgn * 58 * s - 4 * s, waist_y + 16 * s)
        hand = (cx + sgn * 56 * s - 4 * s, waist_y + 44 * s)
        _harlequin_band(surf, sh, elbow, 11 * s, s, col_a, col_b)
        _harlequin_band(surf, elbow, hand, 9 * s, s, col_b, col_a)
        _gold_cuff(surf, hand[0], hand[1], 8 * s, s)
        for f in (-1, 0, 1):
            tipx = hand[0] + f * 5 * s
            tipy = hand[1] + 12 * s + abs(f) * 2 * s
            pygame.draw.line(surf, GOLD_DARK, hand, (tipx, tipy), 3 * s)
            pygame.draw.line(surf, GOLD, hand, (tipx, tipy), s)
            pygame.draw.circle(surf, GOLD_DARK, (tipx, tipy), 2 * s)
        hands.append(hand)
    lh, rh = hands
    # The cradled TANGLE as a confident SHAPE: just TWO bold sagging cords slung
    # hand-to-hand, each laid as a faint plum drop-shadow (separation against the
    # dark robe), a dark backing, a thick off-white cord, then a bright rim-light
    # on the crest so it lifts clear of the plum. Exaggerated deep sag so the
    # "holding strings" read survives the 92px gameplay scale.
    def _catenary(y0, dip, weight, col):
        pts = []
        for k in range(0, 21):
            t = k / 20
            x = lh[0] + 4 * s + (rh[0] - lh[0] - 8 * s) * t
            y = y0 + int(math.sin(t * math.pi) * dip)
            pts.append((x, y))
        shp = [(x, y + 4 * s) for x, y in pts]
        pygame.draw.lines(surf, PLUM_DARK, False, shp, weight + 3 * s)
        pygame.draw.lines(surf, STRING_DARK, False, pts, weight + 2 * s)
        pygame.draw.lines(surf, col, False, pts, weight)
        rim = [(x, y - max(1, weight // 2)) for x, y in pts]
        pygame.draw.lines(surf, (250, 248, 236), False, rim, max(1, s))
        return pts
    base_y = max(lh[1], rh[1]) + 18 * s
    _catenary(base_y, 30 * s, 5 * s, STRING_COL)
    _catenary(base_y + 12 * s, 40 * s, 6 * s, STRING_COL)
    # Two deliberate, bold KNOT-BLOBS where the cords snarl (clear shapes, not
    # specks) with a plum shadow + a white catchlight so they pop off the robe.
    knot_y = base_y + 38 * s
    for kx, kr in ((-14, 7), (10, 8)):
        kxx = cx + kx * s - 4 * s
        pygame.draw.circle(surf, PLUM_DARK, (kxx + s, knot_y + 4 * s), kr * s + 2 * s)
        pygame.draw.circle(surf, STRING_DARK, (kxx, knot_y), kr * s)
        pygame.draw.circle(surf, STRING_COL, (kxx, knot_y), kr * s - 2 * s)
        pygame.draw.circle(surf, (250, 248, 236),
                           (kxx - 2 * s, knot_y - 2 * s), max(1, kr * s // 3))
    # The two MINIONS — bigger again (~15% over r1) and pushed further OUTBOARD,
    # hung at staggered heights so the pair read as caught mid-jerk and clearly
    # own the lower third. These are the joke; they must win the eye after face.
    _minion_polish_2(surf, lh[0] - 6 * s, lh[1] + 14 * s, s, VENOM,
                     swing=-0.6, scale=1.45)
    _minion_polish_2(surf, rh[0] + 6 * s, rh[1] + 14 * s, s, PLUM_BRUISE,
                     swing=0.55, scale=1.6)

    # KEPT: ruff, head + face, forward-flopped cap — verbatim from r1.
    _scallop_ruff(surf, cx - 6 * s, hump_y + 8 * s, 26 * s, s, lobes=8, r=7)
    hr = 22 * s
    hcx = cx - 4 * s
    hy = hump_y - hr + 6 * s
    pygame.draw.circle(surf, SKIN_SHADE, (hcx, hy), hr + s)
    pygame.draw.circle(surf, SKIN, (hcx, hy), hr)
    _bruise(surf, hcx + 11 * s, hy + 8 * s, 6 * s, 5 * s, 70)
    _bruise(surf, hcx - 13 * s, hy + 2 * s, 4 * s, 6 * s, 55)
    _villain_face(surf, hcx, hy, hr, s, brow_left=False, mood="grin")
    _evolved_cap(surf, hcx, hy - hr + 5 * s, s, lean=-0.6, scale=1.0)


# ─────────────────────────────────────────────────────────────────────────────
# JANUS TAKE A — THE TWIN-MASK MARQUEE
# A grand front-facing herald, ONE head split down the middle into TWO PAINTED
# HARLEQUIN MASKS (comedy grin+fang on the bright half, sinister weeping-tragedy
# on the dark half), both menacing + browcock. A great BRUISED-OXBLOOD banner
# sail balloons behind, blazoned with a painted twin-mask emblem (NOT a smiley).
# ─────────────────────────────────────────────────────────────────────────────

def build_twin_mask(surf, cx, feet_y, K):
    s = K
    hip_y = feet_y - 104 * s
    top_y = hip_y - 86 * s

    # The billowing OXBLOOD banner sail behind (bruised maroon, NOT fire-red).
    sail = [(cx + 8 * s, top_y - 8 * s), (cx + 92 * s, top_y + 8 * s),
            (cx + 112 * s, hip_y - 8 * s), (cx + 98 * s, hip_y + 46 * s),
            (cx + 64 * s, hip_y + 56 * s), (cx + 32 * s, hip_y + 34 * s)]
    pygame.draw.polygon(surf, OXBLOOD_DARK, sail)
    pygame.draw.polygon(surf, OXBLOOD,
                        [(cx + 8 * s, top_y - 8 * s), (cx + 62 * s, top_y),
                         (cx + 72 * s, hip_y), (cx + 32 * s, hip_y + 34 * s)])
    pygame.draw.polygon(surf, OXBLOOD_LIT,
                        [(cx + 14 * s, top_y - 2 * s), (cx + 40 * s, top_y + 4 * s),
                         (cx + 30 * s, hip_y), (cx + 18 * s, hip_y - 12 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, sail, 2 * s)
    for k in range(6):
        t = k / 5
        fx = (112 - (112 - 64) * t) * s
        fy = (hip_y - 8 * s) + (hip_y + 56 * s - (hip_y - 8 * s)) * t
        _bell(surf, cx + fx, fy, 2 * s)
    # The banner blazon: a small PAINTED twin-mask emblem (comedy|tragedy split
    # face), the marquee crest — explicitly a harlequin mask motif, not a smiley.
    em = (cx + 58 * s, hip_y - 4 * s)
    er = 13 * s
    pygame.draw.circle(surf, BONE, em, er)
    pygame.draw.line(surf, INK, (em[0], em[1] - er), (em[0], em[1] + er), s)
    # comedy half (left of emblem): up-grin.
    pygame.draw.arc(surf, BLOOD_DARK, (em[0] - 9 * s, em[1], 9 * s, 8 * s),
                    math.pi, math.tau, 2 * s)
    pygame.draw.circle(surf, INK, (em[0] - 5 * s, em[1] - 4 * s), 2 * s)
    # tragedy half (right): down-snarl + weep streak.
    pygame.draw.arc(surf, BLOOD_DARK, (em[0], em[1] + 2 * s, 9 * s, 8 * s),
                    0, math.pi, 2 * s)
    pygame.draw.circle(surf, INK, (em[0] + 5 * s, em[1] - 4 * s), 2 * s)
    pygame.draw.line(surf, VENOM_DEEP, (em[0] + 5 * s, em[1] - 2 * s),
                     (em[0] + 5 * s, em[1] + 6 * s), s)

    # The MIRROR-SPLIT robe: comedy (venom/gold bright) viewer-left, tragedy
    # (deep plum/bruise dark) viewer-right, meeting at a bone centre seam.
    left_half = [(cx, hip_y + 16 * s), (cx, top_y),
                 (cx - 34 * s, top_y + 8 * s), (cx - 46 * s, hip_y + 16 * s)]
    right_half = [(cx, hip_y + 16 * s), (cx, top_y),
                  (cx + 34 * s, top_y + 8 * s), (cx + 46 * s, hip_y + 16 * s)]
    pygame.draw.polygon(surf, VENOM_DEEP, left_half)
    pygame.draw.polygon(surf, VENOM,
                        [(cx - 4 * s, top_y + 2 * s), (cx - 30 * s, top_y + 8 * s),
                         (cx - 36 * s, hip_y + 12 * s), (cx - 6 * s, hip_y + 14 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, right_half)
    pygame.draw.polygon(surf, PLUM_DEEP,
                        [(cx + 4 * s, top_y + 2 * s), (cx + 30 * s, top_y + 8 * s),
                         (cx + 36 * s, hip_y + 12 * s), (cx + 6 * s, hip_y + 14 * s)])
    # Per-half motifs: gold bell-buttons on comedy, bruise-violet teardrop
    # diamonds on tragedy.
    for i in range(3):
        dy = top_y + 24 * s + i * 22 * s
        _bell(surf, cx - 20 * s, dy, 3 * s)
        pygame.draw.polygon(surf, PLUM_BRUISE,
                            [(cx + 20 * s, dy - 5 * s), (cx + 25 * s, dy),
                             (cx + 20 * s, dy + 7 * s), (cx + 15 * s, dy)])
    pygame.draw.line(surf, BONE, (cx, top_y), (cx, hip_y + 16 * s), 2 * s)
    pygame.draw.polygon(surf, INK, left_half, 2 * s)
    pygame.draw.polygon(surf, INK, right_half, 2 * s)

    # Harlequin legs, each matching its half.
    for sgn, col in ((-1, VENOM), (1, PLUM_BRUISE)):
        lx = cx + sgn * 20 * s
        _harlequin_band(surf, (lx, hip_y + 12 * s), (lx + sgn * 4 * s, feet_y - 8 * s),
                        11 * s, s, col, _shade(col, -45))
        boot = pygame.Rect(0, 0, 24 * s, 12 * s)
        boot.center = (lx + sgn * 8 * s, feet_y - 4 * s)
        pygame.draw.ellipse(surf, PLUM_DARK, boot)
        pygame.draw.ellipse(surf, PLUM_DEEP, boot.inflate(-3 * s, -2 * s))
        _bell(surf, boot.centerx + sgn * 12 * s, boot.centery - 2 * s, 3 * s)

    # One arm flung wide presenting the masks, one planted — herald flare.
    sh_l = (cx - 28 * s, top_y + 14 * s)
    hand_l = (cx - 62 * s, top_y - 30 * s)
    _harlequin_band(surf, sh_l, hand_l, 9 * s, s, VENOM, PLUM_BRUISE)
    _gold_cuff(surf, hand_l[0], hand_l[1], 7 * s, s)
    sh_r = (cx + 28 * s, top_y + 14 * s)
    hand_r = (cx + 44 * s, hip_y - 8 * s)
    _harlequin_band(surf, sh_r, (cx + 46 * s, top_y + 40 * s), 9 * s, s,
                    PLUM_BRUISE, VENOM)
    _harlequin_band(surf, (cx + 46 * s, top_y + 40 * s), hand_r, 8 * s, s,
                    VENOM, PLUM_BRUISE)
    _gold_cuff(surf, hand_r[0], hand_r[1], 7 * s, s)

    # The lineage GOLD SCALLOPED RUFF framing the double face.
    _scallop_ruff(surf, cx, top_y + 2 * s, 32 * s, s, lobes=11, r=7)

    # HEAD — ONE head, split into two PAINTED HARLEQUIN MASKS.
    hr = 24 * s
    hy = top_y - hr - 2 * s
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr + s)
    pygame.draw.circle(surf, SKIN, (cx, hy), hr)
    # Dark greasepaint wash over the tragedy (right) half.
    grey = pygame.Surface((hr * 2 + 2, hr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.polygon(grey, (52, 40, 70, 150),
                        [(hr, 0), (hr * 2, 0), (hr * 2, hr * 2), (hr, hr * 2)])
    cmask = pygame.Surface(grey.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(cmask, (255, 255, 255, 255), (hr, hr), hr)
    grey.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grey, (cx - hr, hy - hr))
    pygame.draw.line(surf, INK, (cx, hy - hr), (cx, hy + hr), 2 * s)
    pygame.draw.circle(surf, SKIN_SHADE, (cx, hy), hr, 2 * s)
    _twin_mask_face(surf, cx, hy, hr, s)

    # The EVOLVED belled cap — split-colour, asymmetric: comedy spike tall on the
    # bright side, tragedy spire drooping on the dark side, central gold point.
    cap_y = hy - hr + 2 * s
    lt = (cx - 28 * s, cap_y - 40 * s)
    pygame.draw.polygon(surf, VENOM, [(cx - 12 * s, cap_y), (cx - s, cap_y - 4 * s), lt])
    pygame.draw.polygon(surf, VENOM_DEEP, [(cx - 12 * s, cap_y), (cx - s, cap_y - 4 * s), lt], s)
    _bell(surf, lt[0], lt[1], 3 * s)
    ct = (cx + 2 * s, cap_y - 46 * s)
    pygame.draw.polygon(surf, GOLD, [(cx - 7 * s, cap_y - 2 * s), (cx + 9 * s, cap_y - 2 * s), ct])
    pygame.draw.polygon(surf, GOLD_DARK, [(cx - 7 * s, cap_y - 2 * s), (cx + 9 * s, cap_y - 2 * s), ct], s)
    _bell(surf, ct[0], ct[1], 3 * s)
    rt = (cx + 32 * s, cap_y - 8 * s)
    pygame.draw.polygon(surf, PLUM_BRUISE, [(cx + s, cap_y - 4 * s), (cx + 12 * s, cap_y), rt])
    pygame.draw.polygon(surf, PLUM_DARK, [(cx + s, cap_y - 4 * s), (cx + 12 * s, cap_y), rt], s)
    _bell(surf, rt[0], rt[1], 3 * s)


def _twin_mask_face(surf, cx, hy, hr, s):
    # LEFT (comedy) half — a PAINTED harlequin half-mask: cocked-up brow, bright
    # eye+glint, venom diamond eye-patch marking, gleeful up-grin baring a fang.
    pygame.draw.polygon(surf, VENOM_DEEP,
                        [(cx - 13 * s, hy - 7 * s), (cx - 4 * s, hy - 4 * s),
                         (cx - 8 * s, hy + 4 * s), (cx - 16 * s, hy)])  # mask patch
    pygame.draw.line(surf, INK, (cx - 16 * s, hy - 8 * s),
                     (cx - 4 * s, hy - 11 * s), 4 * s)  # cocked-up brow
    pygame.draw.ellipse(surf, WHITE, (cx - 14 * s, hy - 4 * s, 11 * s, 10 * s))
    pygame.draw.circle(surf, INK, (cx - 9 * s, hy + s), 3 * s)
    _glint(surf, cx - 10 * s, hy - s, 2 * s)
    pygame.draw.arc(surf, BLOOD, (cx - 18 * s, hy + 5 * s, 22 * s, 20 * s),
                    math.pi * 0.5, math.pi * 1.0, 3 * s)
    pygame.draw.polygon(surf, BONE,
                        [(cx - 14 * s, hy + 12 * s), (cx - s, hy + 13 * s),
                         (cx - 2 * s, hy + 16 * s), (cx - 13 * s, hy + 17 * s)])
    pygame.draw.polygon(surf, BONE, [(cx - 11 * s, hy + 16 * s),  # fang
                                     (cx - 7 * s, hy + 16 * s), (cx - 9 * s, hy + 22 * s)])

    # RIGHT (tragedy) half — PAINTED harlequin half-mask: down-furrowed brow,
    # weeping eye with a painted greasepaint streak, sinister down-snarl + fang.
    # Menacing, NOT sad-cute — sharp angles, baring teeth.
    pygame.draw.polygon(surf, BLOOD_DARK,
                        [(cx + 13 * s, hy - 7 * s), (cx + 4 * s, hy - 4 * s),
                         (cx + 8 * s, hy + 4 * s), (cx + 16 * s, hy)])  # mask patch
    pygame.draw.line(surf, INK, (cx + 4 * s, hy - 11 * s),
                     (cx + 16 * s, hy - 6 * s), 4 * s)  # furrowed-down brow
    pygame.draw.ellipse(surf, (220, 224, 230), (cx + 4 * s, hy - 4 * s, 11 * s, 10 * s))
    pygame.draw.circle(surf, INK, (cx + 9 * s, hy + 2 * s), 3 * s)
    _glint(surf, cx + 8 * s, hy, 2 * s)
    # Painted weep-streak (greasepaint), venom-soured, not a baby-blue teardrop.
    pygame.draw.polygon(surf, VENOM_DEEP,
                        [(cx + 9 * s, hy + 5 * s), (cx + 11 * s, hy + 17 * s),
                         (cx + 7 * s, hy + 17 * s)])
    pygame.draw.arc(surf, BLOOD_DARK, (cx + s, hy + 11 * s, 22 * s, 22 * s),
                    math.pi * 1.0, math.pi * 2.0, 3 * s)
    pygame.draw.polygon(surf, BONE,
                        [(cx + s, hy + 13 * s), (cx + 14 * s, hy + 12 * s),
                         (cx + 13 * s, hy + 9 * s), (cx + 2 * s, hy + 10 * s)])
    pygame.draw.polygon(surf, BONE, [(cx + 7 * s, hy + 10 * s),  # fang
                                     (cx + 11 * s, hy + 10 * s), (cx + 9 * s, hy + 16 * s)])

    # Shared blood nose straddling the seam.
    pygame.draw.circle(surf, BLOOD, (cx, hy + 6 * s), 4 * s)
    pygame.draw.circle(surf, _shade(BLOOD, 80), (cx - s, hy + 4 * s), 2 * s)


# ─────────────────────────────────────────────────────────────────────────────
# JANUS TAKE B — THE TWO-HEADED HERALD
# The duality made LITERAL: TWO heads on two craning necks splaying apart off
# one body, each a PAINTED HARLEQUIN MASK (one gleeful comedy grin+fang, one
# sinister weeping-tragedy), both browcock + menacing. TWIN oxblood pennants
# stream behind. A single belled cap bridges BOTH skulls. Differs from Take A by
# the two-neck silhouette vs. the single split head.
# ─────────────────────────────────────────────────────────────────────────────

def build_two_headed(surf, cx, feet_y, K):
    s = K
    hip_y = feet_y - 100 * s
    top_y = hip_y - 70 * s

    # TWIN oxblood pennants streaming behind, one to each side — the marquee.
    for sgn in (-1, 1):
        base = (cx + sgn * 14 * s, top_y - 4 * s)
        pennant = [base, (cx + sgn * 84 * s, top_y - 18 * s),
                   (cx + sgn * 100 * s, top_y + 18 * s),
                   (cx + sgn * 74 * s, top_y + 22 * s),
                   (cx + sgn * 40 * s, hip_y)]
        pygame.draw.polygon(surf, OXBLOOD_DARK, pennant)
        pygame.draw.polygon(surf, OXBLOOD,
                            [base, (cx + sgn * 60 * s, top_y - 10 * s),
                             (cx + sgn * 48 * s, top_y + 14 * s),
                             (cx + sgn * 30 * s, hip_y - 8 * s)])
        pygame.draw.polygon(surf, PLUM_DARK, pennant, 2 * s)
        _bell(surf, cx + sgn * 98 * s, top_y + 16 * s, 3 * s)
        _bell(surf, cx + sgn * 88 * s, top_y - 14 * s, 2 * s)

    # A single broad herald robe (mass), split-colour down the middle.
    hem_w = 48 * s
    hem_y = feet_y - 8 * s
    robe = [(cx - 32 * s, top_y + 6 * s), (cx + 32 * s, top_y + 6 * s),
            (cx + hem_w, hem_y), (cx - hem_w, hem_y)]
    pygame.draw.polygon(surf, VENOM_DEEP,
                        [(cx, top_y + 6 * s), (cx - 32 * s, top_y + 6 * s),
                         (cx - hem_w, hem_y), (cx, hem_y)])
    pygame.draw.polygon(surf, PLUM_DEEP,
                        [(cx, top_y + 6 * s), (cx + 32 * s, top_y + 6 * s),
                         (cx + hem_w, hem_y), (cx, hem_y)])
    pygame.draw.polygon(surf, VENOM,
                        [(cx - 6 * s, top_y + 8 * s), (cx - 28 * s, top_y + 8 * s),
                         (cx - hem_w + 8 * s, hem_y - 2 * s), (cx - 8 * s, hem_y - 2 * s)])
    pygame.draw.polygon(surf, PLUM_BRUISE,
                        [(cx + 22 * s, top_y + 8 * s), (cx + 30 * s, top_y + 8 * s),
                         (cx + hem_w - 4 * s, hem_y - 2 * s), (cx + 30 * s, hem_y - 2 * s)])
    pygame.draw.polygon(surf, PLUM_DARK, robe, 2 * s)
    pygame.draw.line(surf, BONE, (cx, top_y + 6 * s), (cx, hem_y), 2 * s)
    # Gold frog-bells down the seam + bell-fringed hem.
    for i in range(5):
        _bell(surf, cx, top_y + 18 * s + i * 16 * s, 3 * s)
    n = 8
    for i in range(n):
        x0 = cx - hem_w + 2 * hem_w * i / n
        x1 = cx - hem_w + 2 * hem_w * (i + 1) / n
        mid = (x0 + x1) / 2
        col = VENOM if i % 2 else GOLD
        dag = [(x0, hem_y - 2 * s), (x1, hem_y - 2 * s), (mid, hem_y + 10 * s)]
        pygame.draw.polygon(surf, col, dag)
        pygame.draw.polygon(surf, _shade(col, -60), dag, s)
        _bell(surf, mid, hem_y + 10 * s, 2 * s)
    for sgn in (-1, 1):
        _gold_cuff(surf, cx + sgn * 26 * s, feet_y - 4 * s, 6 * s, s)

    # Two arms flung wide in a double herald proclamation — harlequin-banded.
    for sgn, col_a, col_b in ((-1, VENOM, PLUM_BRUISE), (1, PLUM_BRUISE, VENOM)):
        sh = (cx + sgn * 26 * s, top_y + 14 * s)
        elbow = (cx + sgn * 50 * s, top_y - 6 * s)
        hand = (cx + sgn * 58 * s, top_y - 34 * s)
        _harlequin_band(surf, sh, elbow, 9 * s, s, col_a, col_b)
        _harlequin_band(surf, elbow, hand, 8 * s, s, col_b, col_a)
        _gold_cuff(surf, hand[0], hand[1], 7 * s, s)

    # A wide GOLD SCALLOPED RUFF spanning both necks (lineage anchor).
    _scallop_ruff(surf, cx, top_y + 4 * s, 36 * s, s, lobes=11, r=7)

    # TWO craning necks splaying apart, each topped by a head.
    hr = 18 * s
    necks = []
    for sgn in (-1, 1):
        neck_base = (cx + sgn * 8 * s, top_y)
        head_cx = cx + sgn * 26 * s
        head_cy = top_y - hr - 22 * s
        # Banded neck giving each head a stalk (mass, not a stick).
        _harlequin_band(surf, neck_base, (head_cx, head_cy + hr - 2 * s), 10 * s, s,
                        VENOM if sgn < 0 else PLUM_BRUISE,
                        PLUM_DEEP if sgn < 0 else VENOM_DEEP, n=3)
        necks.append((head_cx, head_cy, sgn))

    for head_cx, head_cy, sgn in necks:
        pygame.draw.circle(surf, SKIN_SHADE, (head_cx, head_cy), hr + s)
        pygame.draw.circle(surf, SKIN, (head_cx, head_cy), hr)
        if sgn < 0:
            # Comedy head — gleeful grin+fang, cocked brow.
            _bruise(surf, head_cx + 9 * s, head_cy + 6 * s, 5 * s, 4 * s, 70)
            _villain_face(surf, head_cx, head_cy, hr, s, brow_left=True, mood="grin")
            cap_lean = -0.2
        else:
            # Tragedy head — sinister weeping-snarl, cocked brow, greasepaint.
            grey = pygame.Surface((hr * 2 + 2, hr * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(grey, (52, 40, 70, 110), (hr, hr), hr)
            surf.blit(grey, (head_cx - hr, head_cy - hr))
            _villain_face(surf, head_cx, head_cy, hr, s, brow_left=False, mood="tragedy")
            cap_lean = 0.2
        # Each head wears one evolved belled spire of the shared cap.
        _evolved_cap(surf, head_cx, head_cy - hr + 4 * s, s, lean=cap_lean, scale=0.7)


# ─────────────────────────────────────────────────────────────────────────────
# Cell 0 — the FAITHFUL CURRENT clown, reproduced verbatim via the shipped
# builder (NO die, NO staff).
# ─────────────────────────────────────────────────────────────────────────────

def build_current(surf, cx, feet_y):
    spec = dict(JESTERS[-1][1])      # "Plum & Lime — FINAL"
    spec.pop("no_shadow", None)
    hand_up = (cx - 60, feet_y - 156)   # the true up-left point pose
    build_jester(surf, cx, feet_y, hand_up, **spec)


# ─────────────────────────────────────────────────────────────────────────────
# Sheet composition — six cells on ONE shared ground line.
# ─────────────────────────────────────────────────────────────────────────────

BOSSES = [
    ("THE RINGMASTER COLOSSUS", build_colossus,
     "baroque circus-ringmaster - wide TRIANGLE, plumed mitre, BEHOLD flare"),
    ("THE PUPPETEER ABOVE", build_puppeteer,
     "gaunt marionette-master - TALL stilt legs, drooping spires, strings"),
    ("THE BLOATED GLUTTON KING", build_glutton,
     "spherical fat-jester - ONE belly ORB, bell-belt, gnawed bone"),
    ("THE SPIDER-FOOL", build_spider,
     "six-armed harlequin demon - radial BURST, diamond carapace, horns"),
    ("THE JANUS HERALD", build_janus,
     "two-faced marquee herald - SPLIT body, banner sail, double face"),
]


def _wrap(text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.size(trial)[0] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_cell(idx, builder, K, current=False):
    """Each cell is drawn at native K-scale onto its OWN surface, then blit 1:1
    (no smoothscale upscale) so faces stay crisp. The shared ground line sits at
    a fixed fraction so all six align across the sheet."""
    cw, ch = 300, 470
    surf = pygame.Surface((cw, ch))
    _grad_v(surf, (0, 0, cw, ch), BG_TOP, BG_BOT)
    # Shared ground band.
    g_y = ch - 40
    _grad_v(surf, (0, g_y, cw, ch - g_y), GROUND_LIT, GROUND_COL)
    pygame.draw.line(surf, _shade(GROUND_LIT, 30), (0, g_y), (cw, g_y), 2)
    # Soft cast shadow under the figure.
    sh = pygame.Surface((140, 26), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (10, 8, 16, 120), sh.get_rect())
    surf.blit(sh, (cw // 2 - 70, g_y - 12))

    feet_y = g_y - 2
    cx = cw // 2
    if current:
        build_current(surf, cx, feet_y)
    else:
        builder(surf, cx, feet_y, K)
    return surf


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    # Cell 0 renders at the shipped builder's native scale (~feet-to-cap ~200px);
    # the five bosses render LARGER via K so the size jump reads on one ground
    # line. K=2 gives crisp native geometry at roughly 1.4-1.6x the original.
    K = 2

    cols, rows = 3, 2
    cw, ch = 300, 470
    PAD = 40
    GAP = 18
    CAP_H = 116

    f_title = pygame.font.SysFont(None, 48, bold=True)
    f_sub = pygame.font.SysFont(None, 28, bold=True)
    f_cap = pygame.font.SysFont(None, 30, bold=True)
    f_desc = pygame.font.SysFont(None, 26, bold=True)

    canvas_w = PAD * 2 + cols * cw + (cols - 1) * GAP

    # Title + sub wrapped to the canvas width so nothing clips/overflows.
    title_lines = _wrap("EVOLVED WARREN CLOWN - boss escalation (redux r1)",
                        f_title, canvas_w - PAD * 2)
    sub_lines = _wrap(
        "Cell 0 = the faithful CURRENT Plum & Lime jester (clown-only). "
        "Cells 1-5 = five GROUND-UP boss escalations - bigger, meaner, "
        "funnier, grandiose - in the soured/bruised evolved lineage palette. "
        "Five distinct silhouettes: triangle / column / orb / radial burst / "
        "split-with-sail.", f_sub, canvas_w - PAD * 2)
    TITLE_H = len(title_lines) * (f_title.get_height() + 2) + 10 \
        + len(sub_lines) * 26 + 14

    canvas_h = PAD * 2 + TITLE_H + rows * (ch + CAP_H) + (rows - 1) * GAP
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((30, 28, 38))

    yy = PAD - 2
    for line in title_lines:
        canvas.blit(f_title.render(line, True, (236, 224, 196)), (PAD, yy))
        yy += f_title.get_height() + 2
    yy += 8
    for line in sub_lines:
        canvas.blit(f_sub.render(line, True, (188, 192, 204)), (PAD, yy))
        yy += 26

    cells = []
    cells.append(("0. ORIGINAL (current)", render_cell(0, None, K, current=True),
                  "Plum & Lime FINAL - chunky chibi jester, 4-point belled cap, "
                  "gold ruff, quartered body, harlequin legs, grin+fang"))
    for i, (name, builder, desc) in enumerate(BOSSES, start=1):
        cells.append((f"{i}. {name}", render_cell(i, builder, K), desc))

    y0 = PAD + TITLE_H
    for i, (name, cell, desc) in enumerate(cells):
        r, c = divmod(i, cols)
        x = PAD + c * (cw + GAP)
        y = y0 + r * (ch + CAP_H + GAP)
        pygame.draw.rect(canvas, (66, 72, 92),
                         pygame.Rect(x - 1, y - 1, cw + 2, ch + 2), 1)
        canvas.blit(cell, (x, y))
        cy = y + ch + 6
        for line in _wrap(name, f_cap, cw - 6):
            cap = f_cap.render(line, True, (234, 224, 168))
            canvas.blit(cap, (x + (cw - cap.get_width()) // 2, cy))
            cy += f_cap.get_height()
        cy += 4
        for line in _wrap(desc, f_desc, cw - 8):
            ds = f_desc.render(line, True, (186, 192, 204))
            canvas.blit(ds, (x + (cw - ds.get_width()) // 2, cy))
            cy += 22

    out_dir = os.path.join("docs", "evolved_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "redux_round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


# ═════════════════════════════════════════════════════════════════════════════
# ROUND 2 SHEET — five cells: cell 0 = ORIGINAL for lineage/scale, cells 1-2 =
# two PUPPETEER takes, cells 3-4 = two JANUS takes. Bosses render at K so they
# read LARGER than the original. Reuses the round-1 cell/sheet machinery.
# ═════════════════════════════════════════════════════════════════════════════

R2_TAKES = [
    ("1. STRING-MASTER", build_string_master,
     "Puppeteer A - towering robed mastermind, control-cross held ALOFT, "
     "strings cascading; harlequin-banded gold-cuffed arms"),
    ("2. TANGLE-LORD", build_tangle_lord,
     "Puppeteer B - hunched over a string-tangle, two dangling marionette-"
     "minions off clawed gold-cuffed hands; cap flopped forward"),
    ("3. TWIN-MASK MARQUEE", build_twin_mask,
     "Janus A - front-facing, ONE head split into two painted harlequin masks "
     "(comedy grin+fang | weeping-tragedy); oxblood banner sail"),
    ("4. TWO-HEADED HERALD", build_two_headed,
     "Janus B - TWO craning necks + heads splaying apart, each a painted "
     "harlequin mask; twin oxblood pennants, one belled cap per skull"),
]


def main_round2():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    # Same native-K render as round 1 so the size jump off the original reads.
    K = 2

    cols, rows = 3, 2
    cw, ch = 300, 470
    PAD = 40
    GAP = 18
    CAP_H = 140

    f_title = pygame.font.SysFont(None, 48, bold=True)
    f_sub = pygame.font.SysFont(None, 28, bold=True)
    f_cap = pygame.font.SysFont(None, 30, bold=True)
    f_desc = pygame.font.SysFont(None, 26, bold=True)

    canvas_w = PAD * 2 + cols * cw + (cols - 1) * GAP

    title_lines = _wrap("EVOLVED WARREN CLOWN - PUPPETEER + JANUS (redux r2)",
                        f_title, canvas_w - PAD * 2)
    sub_lines = _wrap(
        "DEVELOPMENT of the two chosen directions. Cell 0 = faithful CURRENT "
        "jester (lineage/scale). Cells 1-2 = two PUPPETEER takes (string-master "
        "/ tangle-lord). Cells 3-4 = two JANUS takes (twin-mask / two-headed). "
        "All carry the belled cap + gold scalloped ruff + browcock grin+fang; "
        "Janus faces are PAINTED HARLEQUIN MASKS over a BRUISED-OXBLOOD banner.",
        f_sub, canvas_w - PAD * 2)
    TITLE_H = len(title_lines) * (f_title.get_height() + 2) + 10 \
        + len(sub_lines) * 26 + 14

    canvas_h = PAD * 2 + TITLE_H + rows * (ch + CAP_H) + (rows - 1) * GAP
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((30, 28, 38))

    yy = PAD - 2
    for line in title_lines:
        canvas.blit(f_title.render(line, True, (236, 224, 196)), (PAD, yy))
        yy += f_title.get_height() + 2
    yy += 8
    for line in sub_lines:
        canvas.blit(f_sub.render(line, True, (188, 192, 204)), (PAD, yy))
        yy += 26

    cells = [("0. ORIGINAL (current)",
              render_cell(0, None, K, current=True),
              "Plum & Lime FINAL - the lineage all four bosses evolve FROM: "
              "belled cap, gold ruff, quartered body, grin+fang")]
    for name, builder, desc in R2_TAKES:
        cells.append((name, render_cell(1, builder, K), desc))

    y0 = PAD + TITLE_H
    for i, (name, cell, desc) in enumerate(cells):
        r, c = divmod(i, cols)
        x = PAD + c * (cw + GAP)
        y = y0 + r * (ch + CAP_H + GAP)
        pygame.draw.rect(canvas, (66, 72, 92),
                         pygame.Rect(x - 1, y - 1, cw + 2, ch + 2), 1)
        canvas.blit(cell, (x, y))
        cy = y + ch + 6
        for line in _wrap(name, f_cap, cw - 6):
            cap = f_cap.render(line, True, (234, 224, 168))
            canvas.blit(cap, (x + (cw - cap.get_width()) // 2, cy))
            cy += f_cap.get_height()
        cy += 4
        for line in _wrap(desc, f_desc, cw - 8):
            ds = f_desc.render(line, True, (186, 192, 204))
            canvas.blit(ds, (x + (cw - ds.get_width()) // 2, cy))
            cy += 22

    out_dir = os.path.join("docs", "evolved_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "redux_round_2.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


# ═════════════════════════════════════════════════════════════════════════════
# TANGLE-LORD SHIP-POLISH SHEET — four cells proving the hero reads at every
# scale: HERO (large native-K, crisp), IN-GAME SCALE (~90px tall on sky-blue),
# FACE DETAIL (zoomed head crop), ORIGINAL (the faithful current clown for
# lineage/scale). Renders the polished figure on its own surface, then derives
# the small + crop cells from that same render so they prove the SAME art.
# ═════════════════════════════════════════════════════════════════════════════

SKY_TOP = (132, 196, 236)       # gameplay sky blue (proves the in-game read)
SKY_BOT = (176, 220, 244)


def _figure_surface(builder, K, bg_top, bg_bot, w, h, feet_frac=0.94):
    """Draw a boss builder onto its own transparent-grounded panel at native K,
    so the result can be blit 1:1 (hero / original) or smoothscaled DOWN (the
    in-game proof — downscale is fine, only UPscale blurs)."""
    surf = pygame.Surface((w, h))
    _grad_v(surf, (0, 0, w, h), bg_top, bg_bot)
    feet_y = int(h * feet_frac)
    # Soft cast shadow grounding the figure.
    sh = pygame.Surface((int(w * 0.5), 24), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (10, 8, 16, 110), sh.get_rect())
    surf.blit(sh, (w // 2 - int(w * 0.25), feet_y - 12))
    if builder is None:
        build_current(surf, w // 2, feet_y)
    else:
        builder(surf, w // 2, feet_y, K)
    return surf


def main_tanglelord():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    K = 3                        # ship-polish hero at a richer native scale

    f_title = pygame.font.SysFont(None, 52, bold=True)
    f_sub = pygame.font.SysFont(None, 28, bold=True)
    f_cap = pygame.font.SysFont(None, 32, bold=True)
    f_desc = pygame.font.SysFont(None, 26, bold=True)

    PAD = 44
    GAP = 22

    # HERO — drawn large at native K (no upscale).
    hero_w, hero_h = 460, 760
    hero = _figure_surface(build_tangle_lord_polish, K, BG_TOP, BG_BOT,
                           hero_w, hero_h, feet_frac=0.95)

    # IN-GAME SCALE — same figure rendered tall on sky, then smoothscaled DOWN so
    # the silhouette is ~90px tall on a sky-blue field (proves the gameplay read).
    # The source is trimmed to the figure's own bounding box first so the 90px is
    # the FIGURE, not the padded panel.
    proof_src = _figure_surface(build_tangle_lord_polish, K, SKY_TOP, SKY_BOT,
                                hero_w, hero_h, feet_frac=0.92)
    # The figure spans roughly cap-tip to minion-feet; crop that vertical band.
    fig_feet = int(hero_h * 0.92)
    fig_top = fig_feet - 235 * K          # cap tip clearance
    fig_bot = fig_feet + 6 * K            # a touch below the hem/minion feet
    fig_crop = pygame.Rect(0, fig_top, hero_w, fig_bot - fig_top).clip(
        proof_src.get_rect())
    fig = proof_src.subsurface(fig_crop).copy()
    target_h = 92                          # the brief's ~90px gameplay read
    scale_f = target_h / fig.get_height()
    small_fig = pygame.transform.smoothscale(
        fig, (max(1, int(fig.get_width() * scale_f)), target_h))
    ingame_w, ingame_h = 300, 760
    ingame = pygame.Surface((ingame_w, ingame_h))
    _grad_v(ingame, (0, 0, ingame_w, ingame_h), SKY_TOP, SKY_BOT)
    # A reference pipe-gap pair so the boss's gameplay size reads in context — a
    # ~90px gap between two green pillars is the obstacle the boss would loom in.
    gap_top = ingame_h // 2 - 60
    gap_bot = ingame_h // 2 + 60
    for ry in (0, gap_bot):
        rh = gap_top if ry == 0 else ingame_h - gap_bot
        pygame.draw.rect(ingame, (74, 132, 84),
                         pygame.Rect(ingame_w - 64, ry, 64, rh))
        pygame.draw.rect(ingame, (104, 168, 110),
                         pygame.Rect(ingame_w - 64, ry, 64, rh), 3)
    ingame.blit(small_fig,
                (ingame_w // 2 - small_fig.get_width() // 2 - 30,
                 ingame_h // 2 - target_h // 2))

    # FACE DETAIL — crop the head region of the hero and blit it (sharp integer
    # scale, no smoothing). The head centre tracks the builder's geometry:
    # hy = feet_y - (150 + 22 - 6)*K, hcx = cx - 4*K.
    feet_y_hero = int(hero_h * 0.95)
    head_cx = hero_w // 2 - 4 * K
    head_cy = feet_y_hero - 166 * K
    crop = pygame.Rect(0, 0, 64 * K, 88 * K)        # head + flopped cap + ruff top
    crop.center = (head_cx, head_cy - 18 * K)
    crop = crop.clip(hero.get_rect())
    face_src = hero.subsurface(crop).copy()
    face_w, face_h = 300, 360
    face = pygame.Surface((face_w, face_h))
    _grad_v(face, (0, 0, face_w, face_h), BG_TOP, BG_BOT)
    fz = min(face_w / crop.w, (face_h - 4) / crop.h)
    face_zoom = pygame.transform.scale(
        face_src, (int(crop.w * fz), int(crop.h * fz)))
    face.blit(face_zoom,
              (face_w // 2 - face_zoom.get_width() // 2,
               face_h // 2 - face_zoom.get_height() // 2))

    # ORIGINAL — the faithful current clown, small, for lineage/scale.
    orig_w, orig_h = 300, 360
    orig = _figure_surface(None, K, BG_TOP, BG_BOT, orig_w, orig_h,
                           feet_frac=0.92)

    # ── compose: HERO on the left, a stacked column of the three proof cells on
    # the right (in-game / face / original), all under one title. ──────────────
    right_w = max(ingame_w, face_w, orig_w)
    col_x = PAD + hero_w + GAP * 2

    canvas_w = col_x + right_w + PAD
    f_cap_h = f_cap.get_height()
    f_desc_h = 24

    title_lines = _wrap("EVOLVED WARREN CLOWN - THE TANGLE-LORD (ship polish r1)",
                        f_title, canvas_w - PAD * 2)
    sub_lines = _wrap(
        "The chosen LATE-GAME boss, refined to a hero: a hunched marionette-"
        "schemer crouched over a cradled string-tangle, two limp puppet-MINIONS "
        "dangling from clawed tarnished-gold hands, cap flopped forward. Soured "
        "Plum & Lime - bruised plum, venom lime, tarnished gold, oxblood. Cells "
        "prove it reads at gameplay scale + holds its face.",
        f_sub, canvas_w - PAD * 2)
    TITLE_H = len(title_lines) * (f_title.get_height() + 2) + 12 \
        + len(sub_lines) * 26 + 16

    # Right-column layout heights (cell + caption + desc each).
    def block_h(cell_h, desc):
        return cell_h + 6 + f_cap_h + 4 + len(_wrap(desc, f_desc, right_w - 8)) * f_desc_h + 8

    ingame_desc = ("IN-GAME SCALE - the SAME figure downscaled to ~90px tall on "
                   "a sky field beside a pipe-gap: hunch + forward cap + cradled "
                   "tangle + minion silhouette must read at gameplay size")
    face_desc = ("FACE DETAIL - browcock grin + ONE fang, bright venom eye-"
                 "glint, blood nose; hard macro shapes that survive the "
                 "downscale")
    orig_desc = ("ORIGINAL (current) - the faithful Plum & Lime jester the "
                 "Tangle-Lord evolves FROM, for lineage + size comparison")
    hero_desc = ("HERO - polished Tangle-Lord at native K (crisp, no upscale): "
                 "one menacing schemer arc - hunched back, forward-flopped "
                 "belled cap, gold scalloped ruff, clawed gold-cuffed hands "
                 "cradling the tangle, two limp belled marionette-minions")

    right_total = (block_h(ingame_h, ingame_desc) + GAP
                   + block_h(face_h, face_desc) + GAP
                   + block_h(orig_h, orig_desc))
    hero_block = block_h(hero_h, hero_desc)
    canvas_h = PAD + TITLE_H + max(hero_block, right_total) + PAD

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((30, 28, 38))

    yy = PAD - 2
    for line in title_lines:
        canvas.blit(f_title.render(line, True, (236, 224, 196)), (PAD, yy))
        yy += f_title.get_height() + 2
    yy += 10
    for line in sub_lines:
        canvas.blit(f_sub.render(line, True, (190, 196, 208)), (PAD, yy))
        yy += 26

    def place(x, y, cell, name, desc, max_w):
        pygame.draw.rect(canvas, (66, 72, 92),
                         pygame.Rect(x - 1, y - 1, cell.get_width() + 2,
                                     cell.get_height() + 2), 1)
        canvas.blit(cell, (x, y))
        cy = y + cell.get_height() + 6
        for line in _wrap(name, f_cap, max_w - 6):
            cap = f_cap.render(line, True, (234, 224, 168))
            canvas.blit(cap, (x + (cell.get_width() - cap.get_width()) // 2, cy))
            cy += f_cap_h
        cy += 4
        for line in _wrap(desc, f_desc, max_w - 8):
            ds = f_desc.render(line, True, (188, 194, 206))
            canvas.blit(ds, (x + (cell.get_width() - ds.get_width()) // 2, cy))
            cy += f_desc_h
        return cy + 8

    y0 = PAD + TITLE_H
    place(PAD, y0, hero, "1. HERO - THE TANGLE-LORD", hero_desc, hero_w)

    ry = y0
    ry = place(col_x, ry, ingame, "2. IN-GAME SCALE", ingame_desc, right_w) + GAP - 8
    ry = place(col_x, ry, face, "3. FACE DETAIL", face_desc, right_w) + GAP - 8
    place(col_x, ry, orig, "4. ORIGINAL (current)", orig_desc, right_w)

    out_dir = os.path.join("docs", "evolved_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tanglelord_polish_1.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


def main_tanglelord_2():
    """Ship-polish r2 sheet — SAME four-cell layout as r1, rendering the r2
    builder (rebuilt mini-jester minions + bold catenary tangle) to a NEW file
    so r1 stays intact. The in-game cell is the gate: ~92px on sky beside a
    pipe-gap. r2 also re-asserts the bright venom eye-glint AFTER the downscale
    so the face doesn't flatten to dark slits at gameplay size."""
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    K = 3

    f_title = pygame.font.SysFont(None, 52, bold=True)
    f_sub = pygame.font.SysFont(None, 28, bold=True)
    f_cap = pygame.font.SysFont(None, 32, bold=True)
    f_desc = pygame.font.SysFont(None, 26, bold=True)

    PAD = 44
    GAP = 22

    hero_w, hero_h = 460, 760
    hero = _figure_surface(build_tangle_lord_polish_2, K, BG_TOP, BG_BOT,
                           hero_w, hero_h, feet_frac=0.95)

    # IN-GAME SCALE — same figure, trimmed to its own bounding band then
    # smoothscaled DOWN to ~92px on sky-blue beside a reference pipe-gap.
    proof_src = _figure_surface(build_tangle_lord_polish_2, K, SKY_TOP, SKY_BOT,
                                hero_w, hero_h, feet_frac=0.92)
    fig_feet = int(hero_h * 0.92)
    fig_top = fig_feet - 235 * K
    fig_bot = fig_feet + 8 * K
    fig_crop = pygame.Rect(0, fig_top, hero_w, fig_bot - fig_top).clip(
        proof_src.get_rect())
    fig = proof_src.subsurface(fig_crop).copy()
    target_h = 92
    scale_f = target_h / fig.get_height()
    small_w = max(1, int(fig.get_width() * scale_f))
    small_fig = pygame.transform.smoothscale(fig, (small_w, target_h))
    # Re-assert the venom eye-glint at the downscaled head so it doesn't sink to
    # a dark slit — the head centre maps from the builder geometry through the
    # same crop + scale used above (carries the cell-3 win into the gate cell).
    head_cx_src = hero_w // 2 - 4 * K
    head_cy_src = fig_feet - 166 * K
    gx = int((head_cx_src - fig_crop.x) * scale_f)
    gy = int((head_cy_src - fig_crop.y) * scale_f)
    for esgn in (-1, 1):
        ex = gx + esgn * max(1, int(2 * scale_f * K))
        pygame.draw.circle(small_fig, EYE_GLINT, (ex, gy), 1)
    ingame_w, ingame_h = 300, 760
    ingame = pygame.Surface((ingame_w, ingame_h))
    _grad_v(ingame, (0, 0, ingame_w, ingame_h), SKY_TOP, SKY_BOT)
    gap_top = ingame_h // 2 - 60
    gap_bot = ingame_h // 2 + 60
    for ry in (0, gap_bot):
        rh = gap_top if ry == 0 else ingame_h - gap_bot
        pygame.draw.rect(ingame, (74, 132, 84),
                         pygame.Rect(ingame_w - 64, ry, 64, rh))
        pygame.draw.rect(ingame, (104, 168, 110),
                         pygame.Rect(ingame_w - 64, ry, 64, rh), 3)
    ingame.blit(small_fig,
                (ingame_w // 2 - small_fig.get_width() // 2 - 30,
                 ingame_h // 2 - target_h // 2))

    # FACE DETAIL — sharp integer-zoom crop of the hero head region.
    feet_y_hero = int(hero_h * 0.95)
    head_cx = hero_w // 2 - 4 * K
    head_cy = feet_y_hero - 166 * K
    crop = pygame.Rect(0, 0, 64 * K, 88 * K)
    crop.center = (head_cx, head_cy - 18 * K)
    crop = crop.clip(hero.get_rect())
    face_src = hero.subsurface(crop).copy()
    face_w, face_h = 300, 360
    face = pygame.Surface((face_w, face_h))
    _grad_v(face, (0, 0, face_w, face_h), BG_TOP, BG_BOT)
    fz = min(face_w / crop.w, (face_h - 4) / crop.h)
    face_zoom = pygame.transform.scale(
        face_src, (int(crop.w * fz), int(crop.h * fz)))
    face.blit(face_zoom,
              (face_w // 2 - face_zoom.get_width() // 2,
               face_h // 2 - face_zoom.get_height() // 2))

    # ORIGINAL — the faithful current clown for lineage/scale.
    orig_w, orig_h = 300, 360
    orig = _figure_surface(None, K, BG_TOP, BG_BOT, orig_w, orig_h,
                           feet_frac=0.92)

    right_w = max(ingame_w, face_w, orig_w)
    col_x = PAD + hero_w + GAP * 2
    canvas_w = col_x + right_w + PAD
    f_cap_h = f_cap.get_height()
    f_desc_h = 24

    title_lines = _wrap("EVOLVED WARREN CLOWN - THE TANGLE-LORD (ship polish r2)",
                        f_title, canvas_w - PAD * 2)
    sub_lines = _wrap(
        "r1's face + soured palette + gold ruff + hunched silhouette KEPT "
        "untouched. r2 fixes ONLY the gate failure: the two MINIONS are rebuilt "
        "as obvious mini-jesters (2-point belled cap mirroring the parent, dot-"
        "grin, limp X-legged dangle), enlarged + pushed OUTBOARD; the tangle is "
        "now two BOLD sagging knotted cords with a rim-light. Cell 2 is the gate.",
        f_sub, canvas_w - PAD * 2)
    TITLE_H = len(title_lines) * (f_title.get_height() + 2) + 12 \
        + len(sub_lines) * 26 + 16

    def block_h(cell_h, desc):
        return cell_h + 6 + f_cap_h + 4 + len(_wrap(desc, f_desc, right_w - 8)) * f_desc_h + 8

    ingame_desc = ("IN-GAME SCALE (THE GATE) - the SAME figure downscaled to "
                   "~92px on sky beside a pipe-gap: must read as a hunched "
                   "schemer cradling two puppets on strings")
    face_desc = ("FACE DETAIL - KEPT browcock grin + ONE fang, bright venom "
                 "eye-glint, blood nose; hard macro shapes that survive the "
                 "downscale (unchanged from r1)")
    orig_desc = ("ORIGINAL (current) - the faithful Plum & Lime jester the "
                 "Tangle-Lord evolves FROM, for lineage + size comparison")
    hero_desc = ("HERO - polished Tangle-Lord at native K (crisp, no upscale): "
                 "KEPT hunch + forward cap + ruff + face + gold-cuffed grip; "
                 "NEW obvious mini-jester minions hung outboard + a bold "
                 "knotted two-cord tangle with rim-light")

    right_total = (block_h(ingame_h, ingame_desc) + GAP
                   + block_h(face_h, face_desc) + GAP
                   + block_h(orig_h, orig_desc))
    hero_block = block_h(hero_h, hero_desc)
    canvas_h = PAD + TITLE_H + max(hero_block, right_total) + PAD

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((30, 28, 38))

    yy = PAD - 2
    for line in title_lines:
        canvas.blit(f_title.render(line, True, (236, 224, 196)), (PAD, yy))
        yy += f_title.get_height() + 2
    yy += 10
    for line in sub_lines:
        canvas.blit(f_sub.render(line, True, (190, 196, 208)), (PAD, yy))
        yy += 26

    def place(x, y, cell, name, desc, max_w):
        pygame.draw.rect(canvas, (66, 72, 92),
                         pygame.Rect(x - 1, y - 1, cell.get_width() + 2,
                                     cell.get_height() + 2), 1)
        canvas.blit(cell, (x, y))
        cy = y + cell.get_height() + 6
        for line in _wrap(name, f_cap, max_w - 6):
            cap = f_cap.render(line, True, (234, 224, 168))
            canvas.blit(cap, (x + (cell.get_width() - cap.get_width()) // 2, cy))
            cy += f_cap_h
        cy += 4
        for line in _wrap(desc, f_desc, max_w - 8):
            ds = f_desc.render(line, True, (188, 194, 206))
            canvas.blit(ds, (x + (cell.get_width() - ds.get_width()) // 2, cy))
            cy += f_desc_h
        return cy + 8

    y0 = PAD + TITLE_H
    place(PAD, y0, hero, "1. HERO - THE TANGLE-LORD", hero_desc, hero_w)

    ry = y0
    ry = place(col_x, ry, ingame, "2. IN-GAME SCALE", ingame_desc, right_w) + GAP - 8
    ry = place(col_x, ry, face, "3. FACE DETAIL", face_desc, right_w) + GAP - 8
    place(col_x, ry, orig, "4. ORIGINAL (current)", orig_desc, right_w)

    out_dir = os.path.join("docs", "evolved_clown")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "tanglelord_polish_2.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
    main_round2()
    main_tanglelord()
    main_tanglelord_2()
