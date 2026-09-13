"""Look-dev: the HORNED SOVEREIGN — late-game EPIC event boss (round 3).

Thesis: the classic horned devil reimagined as a regal infernal MONARCH —
broad-shouldered, sweeping ram-horns curling up into a CROWN-OF-HORNS, a
bat-wing mantle framing (never blobbing) a crisp V-taper torso, and a grand
barbed TRIDENT held vertical. Final-boss gravitas, clean-sheet — it borrows
NOTHING from the warren clown/jester (no cap/ruff/grin/harlequin, no plum-lime).

The whole design leans its gravitas into the UPPER-RADIATING silhouette: the
horn sweep + the trident tines. That is the part that survives at 1x and the
part that later tiles into the scrolling pillar — so it is drawn boldest and
darkest-cored, to hold value against a BRIGHT day sky.

Palette is fixed (not biome-driven) so the boss read stays loud across the
day/night cycle: oxblood crimson body, obsidian shadow-core, molten gold on the
horns + trident + trim. Gold doubles as the night-side rim light; oxblood +
obsidian stay deep and saturated so the figure never washes out on the day sky.

The signature prop is the TRIDENT: tall, vertical, and top/bottom-mirrorable.
In-game the held trident later becomes the scrolling pillar obstacle — mirrored
around the gap, the three barbed prongs tile top+bottom into a forked-spire
pillar and the haft reads as the gap. This sheet proves that fit with a small
mirrored pillar-pair thumbnail off to the side.

    PYTHONPATH=. python tools/render_epic_sovereign.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


# ── fixed sovereign palette ──────────────────────────────────────────────────
# Deep + saturated so the figure survives a bright day sky; gold is the night
# rim light. No plum/lime anywhere — this lineage is oxblood/obsidian/gold.
OXBLOOD      = (150,  28,  40)   # the crimson body north-star
OXBLOOD_DK   = (104,  18,  28)   # shaded oxblood facet
OXBLOOD_LIT  = (190,  52,  60)   # lit oxblood edge
OBSIDIAN     = ( 30,  24,  28)   # near-black shadow-core / keyline
OBSIDIAN_LIT = ( 54,  44,  50)   # lifted obsidian facet
GOLD         = (240, 180,  60)   # molten gold horn + trim + trident
GOLD_LIT     = (255, 222, 138)   # lit gold facet / hot rim
GOLD_DK      = (158, 110,  30)   # gold shadow / keyline
EMBER        = (255, 120,  40)   # eye / maw molten glow (sparse accent)
EMBER_HOT    = (255, 226, 150)   # hottest core of the glow
BONE         = (232, 222, 198)   # fang ivory (used very sparingly)
INK          = ( 16,  12,  16)   # darkest keyline


def _shade(c, d):
    return (max(0, min(255, int(c[0] + d))),
            max(0, min(255, int(c[1] + d))),
            max(0, min(255, int(c[2] + d))))


# ── shared low-level paint helpers (not a figure builder) ────────────────────

def _grad_v(surf, rect, top, bot):
    """Vertical gradient fill into a rect."""
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(surf, c, (x, y + i), (x + w, y + i))


def _glow(surf, x, y, r, col):
    """A soft additive ember bloom — the molten light cue (eyes, maw, trident
    tines), so the gold/ember accents read hot even at small size."""
    g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for k in range(r, 0, -1):
        a = int(120 * (1 - k / r) ** 2)
        pygame.draw.circle(g, (*col, a), (r + 1, r + 1), k)
    surf.blit(g, (int(x - r - 1), int(y - r - 1)), special_flags=pygame.BLEND_RGBA_ADD)


def _rim(surf, pts, col, w):
    """A gold rim-light stroke down the lit edge of a mass — the night-side cue
    that keeps the silhouette legible after dark."""
    pygame.draw.lines(surf, col, False, [(int(p[0]), int(p[1])) for p in pts], w)


# ── the TRIDENT (signature prop, drawn standalone so the pillar can reuse it) ─
# Built top/bottom-MIRRORABLE around its own vertical axis: a forked crown of
# three barbed tines over a banded haft. `head_y` is where the tine fork sits;
# everything above it is the radiating crown that tiles into a pillar spire, and
# the haft below reads as the gap when mirrored. Geometry keys off `s` (the
# native K-scale) so it stays crisp at any size.

def _trident_head(surf, cx, head_y, s, *, hw):
    """A clean THREE-prong fork: a centre blade (longest) and two symmetric
    outer blades, every prong a SOLID tapering gold spear-BLADE — not a
    filament. Each blade is wide at its root (a chunky ≥6-8px wedge that does
    NOT vanish on a bright day sky) and tapers to a needle. The trio springs
    from one gold yoke. No mid-haft cross-guard and no extra tines, so when the
    prop mirrors around the gap the two forks meet as a TIDY 6-POINT STARBURST,
    never a tangle of crossing legs.

    This is both the boss's radiating menace and the pillar's forked spire, so
    it is the boldest, darkest-cored mass on the prop."""
    # The yoke the three blades spring from — one solid gold bar (no arms).
    yoke = [(cx - hw * 1.6, head_y + 1 * s), (cx + hw * 1.6, head_y + 1 * s),
            (cx + hw * 1.25, head_y + 9 * s), (cx - hw * 1.25, head_y + 9 * s)]
    pygame.draw.polygon(surf, GOLD_DK, [(int(p[0]), int(p[1])) for p in yoke])
    pygame.draw.polygon(surf, GOLD,
                        [(int(cx - hw * 1.4), int(head_y + 2 * s)),
                         (int(cx + hw * 1.4), int(head_y + 2 * s)),
                         (int(cx + hw * 1.05), int(head_y + 8 * s)),
                         (int(cx - hw * 1.05), int(head_y + 8 * s))])
    pygame.draw.line(surf, GOLD_LIT, (int(cx - hw * 1.35), int(head_y + 3 * s)),
                     (int(cx + hw * 1.35), int(head_y + 3 * s)), max(1, s))

    # Three SOLID blades. Centre runs longest + dead vertical; the two outer are
    # mirror-equal, leaning out so the trio fans symmetrically. Each blade is a
    # broad isosceles wedge (root half-width >= ~3.5px*scale) tapering to a
    # single needle tip — drawn as one clean polygon so nothing reads as a wire.
    base_half = max(3.5 * s, hw * 0.55)      # half-width at the blade root (chunky)
    centre_len = 52 * s
    outer_len = 42 * s
    outer_lean = hw * 1.35                    # how far out the outer tips sit
    yoke_y = head_y + 2 * s                    # blade roots sit on the yoke
    for dx in (-1, 0, 1):
        if dx == 0:
            root_x = cx
            tip = (cx, head_y - centre_len)
        else:
            root_x = cx + dx * hw * 0.85
            tip = (root_x + dx * outer_lean, head_y - outer_len)
        # Solid tapering blade root-quad → needle: two root corners, a slight
        # shoulder a third of the way up (gives the blade a leaf belly), the tip.
        sh_y = yoke_y + (tip[1] - yoke_y) * 0.34    # belly point a third up
        belly = base_half * 1.18
        blade = [(root_x - base_half, yoke_y),
                 (root_x - belly, sh_y),
                 (tip[0], tip[1]),
                 (root_x + belly, sh_y),
                 (root_x + base_half, yoke_y)]
        pygame.draw.polygon(surf, GOLD_DK, [(int(p[0]), int(p[1])) for p in blade])
        # Lit inner wedge so the blade reads as struck metal, not flat paint.
        lit = [(root_x - base_half * 0.5, yoke_y),
               (tip[0], tip[1] + 3 * s),
               (root_x + base_half * 0.5, yoke_y)]
        pygame.draw.polygon(surf, GOLD, [(int(p[0]), int(p[1])) for p in lit])
        pygame.draw.line(surf, GOLD_LIT, (int(tip[0]), int(tip[1] + 3 * s)),
                         (int(root_x), int(yoke_y)), max(1, s))
        _glow(surf, tip[0], tip[1], 4 * s, EMBER)
        pygame.draw.circle(surf, EMBER_HOT, (int(tip[0]), int(tip[1])), max(1, s))


def build_trident(surf, cx, head_y, foot_y, s, *, hw=6):
    """The full grand trident: a banded obsidian-and-gold haft with the barbed
    fork crown on top. Drawn so the upper crown carries the gravitas and the
    haft below it can read as the pillar gap when the prop is mirrored."""
    # Haft: a dark obsidian shaft with a slim gold lit rail (reads round, not
    # flat) and three gold binding-rings, ending in a spike-pommel.
    pygame.draw.line(surf, INK, (cx, head_y + 4 * s), (cx, foot_y), hw * 2 + 2 * s)
    pygame.draw.line(surf, OBSIDIAN, (cx, head_y + 4 * s), (cx, foot_y), hw * 2)
    pygame.draw.line(surf, OBSIDIAN_LIT, (cx - hw * 0.5, head_y + 4 * s),
                     (cx - hw * 0.5, foot_y), max(1, s))
    span = foot_y - head_y
    for t in (0.30, 0.55, 0.80):
        ry = head_y + span * t
        pygame.draw.rect(surf, GOLD_DK,
                         (int(cx - hw - 2 * s), int(ry - 3 * s),
                          int(2 * hw + 4 * s), int(6 * s)))
        pygame.draw.rect(surf, GOLD,
                         (int(cx - hw - 2 * s), int(ry - 2 * s),
                          int(2 * hw + 4 * s), int(3 * s)))
    # Spike pommel foot (so the haft also barbs at the bottom — symmetric menace
    # that helps the mirrored pillar tile read cleanly top + bottom).
    pommel = [(cx - hw, foot_y - 6 * s), (cx + hw, foot_y - 6 * s),
              (cx, foot_y + 10 * s)]
    pygame.draw.polygon(surf, GOLD_DK, pommel)
    pygame.draw.polygon(surf, GOLD, [(cx - hw + s, foot_y - 6 * s),
                                     (cx + hw - s, foot_y - 6 * s),
                                     (cx, foot_y + 8 * s)])
    _trident_head(surf, cx, head_y, s, hw=hw)


# ── the SOVEREIGN figure ─────────────────────────────────────────────────────

def build_sovereign(surf, cx, feet_y, s, *, night=False):
    """The horned infernal monarch standing on the ground line. Layered back to
    front: bat-wing mantle → legs → V-taper torso → pauldrons + arms → head +
    crown-of-horns → the held trident."""
    # On the night side a faint ember pool seeps from under the hooves — the
    # infernal-heat cue that reads only after dark, never haloing on day sky.
    if night:
        for r, a in ((48 * s, 60), (30 * s, 70)):
            pool = pygame.Surface((int(r * 2), int(r)), pygame.SRCALPHA)
            pygame.draw.ellipse(pool, (255, 90, 30, a), pool.get_rect())
            surf.blit(pool, (int(cx - r), int(feet_y - r * 0.5)),
                      special_flags=pygame.BLEND_RGBA_ADD)
    # Top-heavy boss proportions: shoulders sit HIGH + WIDE, legs are short and
    # planted — the figure out-scales a peer because its mass is up top. The
    # shoulder line is ~15% broader than round 1 so the monarch reads as a
    # towering boss, not a humanoid peer.
    hip_y = feet_y - 92 * s           # short, planted legs
    chest_y = hip_y - 82 * s          # the broad shoulder line, raised + heavy
    neck_y = chest_y - 6 * s

    # ── BAT-WING MANTLE (drawn FIRST, behind the body) ───────────────────────
    # A membranous wing-cape pulled BACK and DOWN, well behind + below the
    # shoulders, so a clear band of NEGATIVE SPACE sits between the inner wing
    # edge and the oxblood torso — the V-taper reads as its OWN crisp shape, not
    # a blob. The root tucks UNDER the pauldron and the inner edge stays far out
    # past the waist; the membrane never touches the torso. The membrane is the
    # DARKEST oxblood facet so it sits a clear value step BEHIND the brighter
    # torso (the V pops in blackout).
    for sgn in (-1, 1):
        # Root tucked behind/below the pauldron; spurs sweep DOWN-and-out so the
        # mass hangs as a cape behind the figure rather than fanning up beside
        # the head (which previously fattened the silhouette into a triangle).
        root = (cx + sgn * 50 * s, chest_y + 18 * s)
        spur_top = (cx + sgn * 98 * s, chest_y - 6 * s)
        spur_mid = (cx + sgn * 112 * s, hip_y - 10 * s)
        spur_low = (cx + sgn * 92 * s, hip_y + 40 * s)
        # Inner membrane edge held well OUT from the torso — a clean vertical
        # gutter of sky between wing and waist (the negative-space band).
        inner_hi = (cx + sgn * 62 * s, chest_y + 16 * s)
        inner_lo = (cx + sgn * 70 * s, hip_y + 30 * s)
        membrane = [root, spur_top, spur_mid, spur_low, inner_lo, inner_hi]
        pygame.draw.polygon(surf, OXBLOOD_DK,
                            [(int(p[0]), int(p[1])) for p in membrane])
        # Scalloped trailing edge (the bat-wing tell) cut as dark notches.
        for a, b in ((spur_top, spur_mid), (spur_mid, spur_low)):
            for j in range(3):
                t0 = j / 3
                t1 = (j + 0.5) / 3
                p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
                p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
                inner = (cx + sgn * 66 * s, (p0[1] + p1[1]) * 0.5)
                pygame.draw.polygon(surf, INK,
                                    [(int(p0[0]), int(p0[1])),
                                     (int(p1[0]), int(p1[1])),
                                     (int(inner[0]), int(inner[1]))])
        # Ribbed wing struts (finger bones) in gold — radiating, regal — keep
        # the fan texture + its day/night value behaviour.
        for tip in (spur_top, spur_mid, spur_low):
            pygame.draw.line(surf, GOLD_DK, (int(root[0]), int(root[1])),
                             (int(tip[0]), int(tip[1])), max(1, int(2 * s)))
            pygame.draw.line(surf, GOLD, (int(root[0]), int(root[1])),
                             (int(tip[0]), int(tip[1])), max(1, s))
            pygame.draw.circle(surf, GOLD_LIT, (int(tip[0]), int(tip[1])), max(1, int(2 * s)))
        pygame.draw.polygon(surf, INK,
                            [(int(p[0]), int(p[1])) for p in membrane], max(1, int(2 * s)))

    # ── LEGS — stout digitigrade goat-legs with cloven hooves, planted wide and
    # SHORT (so the broad-shouldered top reads as a towering boss, not a peer).
    for sgn in (-1, 1):
        hipp = (cx + sgn * 16 * s, hip_y)
        knee = (cx + sgn * 26 * s, hip_y + 44 * s)
        ankle = (cx + sgn * 18 * s, feet_y - 16 * s)
        for a, b, w in ((hipp, knee, 16 * s), (knee, ankle, 11 * s)):
            pygame.draw.line(surf, INK, a, b, int(w) + 2 * s)
            pygame.draw.line(surf, OXBLOOD_DK, a, b, int(w))
        pygame.draw.line(surf, OXBLOOD, (hipp[0] - sgn * 3 * s, hipp[1]),
                         (knee[0] - sgn * 3 * s, knee[1]), max(1, int(4 * s)))
        # Cloven hoof — a dark wedge split down the middle, gold-shod at the toe.
        hoof = [(ankle[0] - 10 * s, ankle[1]), (ankle[0] + 12 * s, ankle[1]),
                (ankle[0] + 14 * s, feet_y), (ankle[0] - 8 * s, feet_y)]
        pygame.draw.polygon(surf, OBSIDIAN, hoof)
        pygame.draw.polygon(surf, INK, hoof, max(1, s))
        pygame.draw.line(surf, INK, (ankle[0] + 3 * s, feet_y - 12 * s),
                         (ankle[0] + 3 * s, feet_y), max(1, int(2 * s)))
        pygame.draw.line(surf, GOLD, (ankle[0] - 8 * s, feet_y - 2 * s),
                         (ankle[0] + 14 * s, feet_y - 2 * s), max(1, int(2 * s)))

    # ── TORSO — a crisp inverted-V cuirass: VERY broad shoulders tapering hard
    # to a narrow waist. Drawn in the BRIGHTER oxblood (a clear value step above
    # the dark wing membrane) so the V reads as its own crisp shape in blackout.
    # Shoulders are ~15% wider than round 1 so the chest mass top-heavies the
    # figure into a boss read; the waist pinches hard to keep the V sharp. Mid-
    # body is left CLEAN — no chevron ribs — so the only gold focal here is the
    # single chest gem.
    chest_half = 50 * s               # broader shoulder mass (was 44)
    waist = 17 * s
    torso = [(cx - chest_half, chest_y), (cx + chest_half, chest_y),
             (cx + 32 * s, chest_y + 36 * s),
             (cx + waist, hip_y), (cx - waist, hip_y),
             (cx - 32 * s, chest_y + 36 * s)]
    pygame.draw.polygon(surf, OXBLOOD_LIT, torso)     # brighter than the wings
    # A darker right facet sculpts the volume without adding line noise.
    pygame.draw.polygon(surf, OXBLOOD,
                        [(cx + 6 * s, chest_y), (cx + chest_half, chest_y),
                         (cx + 32 * s, chest_y + 36 * s), (cx + waist, hip_y),
                         (cx, hip_y), (cx + 4 * s, chest_y + 36 * s)])
    pygame.draw.polygon(surf, INK, torso, max(1, int(2 * s)))
    # ONE focal gold element on the chest: a molten sternum gem in a gold bezel,
    # seated at the collar. Nothing else competes on the mid-body.
    gem_y = chest_y + 18 * s
    _glow(surf, cx, gem_y, 11 * s, EMBER)
    pygame.draw.circle(surf, GOLD_DK, (cx, int(gem_y)), int(8 * s))
    pygame.draw.circle(surf, GOLD, (cx, int(gem_y)), int(6 * s))
    pygame.draw.circle(surf, EMBER, (cx, int(gem_y)), int(4 * s))
    pygame.draw.circle(surf, EMBER_HOT, (cx, int(gem_y - s)), max(1, int(1.8 * s)))

    # ── PAULDRONS — broad spiked gold shoulder shelves that cap the wide chest
    # and push the top-heavy breadth even further (the regal, towering read)
    # without softening the waist taper. No rivet studs — the pauldron + its one
    # upswept spike are the only detail, keeping the top clean.
    for sgn in (-1, 1):
        shx = cx + sgn * 46 * s
        pauld = [(cx + sgn * 16 * s, chest_y - 4 * s),
                 (shx + sgn * 26 * s, chest_y - 12 * s),
                 (shx + sgn * 20 * s, chest_y + 16 * s),
                 (cx + sgn * 18 * s, chest_y + 18 * s)]
        pygame.draw.polygon(surf, GOLD_DK, [(int(p[0]), int(p[1])) for p in pauld])
        pygame.draw.polygon(surf, GOLD,
                            [(int(cx + sgn * 18 * s), int(chest_y - 2 * s)),
                             (int(shx + sgn * 21 * s), int(chest_y - 9 * s)),
                             (int(shx + sgn * 16 * s), int(chest_y + 11 * s)),
                             (int(cx + sgn * 19 * s), int(chest_y + 13 * s))])
        pygame.draw.line(surf, GOLD_LIT, (int(cx + sgn * 18 * s), int(chest_y - 2 * s)),
                         (int(shx + sgn * 21 * s), int(chest_y - 9 * s)), max(1, s))
        # An upswept spike off the pauldron crest.
        spk = (shx + sgn * 34 * s, chest_y - 30 * s)
        pygame.draw.polygon(surf, GOLD_DK,
                            [(int(shx + sgn * 10 * s), int(chest_y - 9 * s)),
                             (int(shx + sgn * 23 * s), int(chest_y - 7 * s)),
                             (int(spk[0]), int(spk[1]))])
        pygame.draw.polygon(surf, GOLD,
                            [(int(shx + sgn * 12 * s), int(chest_y - 9 * s)),
                             (int(shx + sgn * 21 * s), int(chest_y - 8 * s)),
                             (int(spk[0]), int(spk[1]))], max(1, s))

    # ── ARMS — the LEFT (viewer) arm hangs gripping the trident; the RIGHT
    # rests as a fist on the hip. Stout, oxblood, gold-cuffed, dwarfed by the
    # pauldrons so breadth stays at the shoulders.
    # Right (viewer) arm — fist on hip.
    sh_r = (cx + 42 * s, chest_y + 8 * s)
    elb_r = (cx + 56 * s, chest_y + 40 * s)
    fist_r = (cx + 32 * s, hip_y - 6 * s)
    for a, b in ((sh_r, elb_r), (elb_r, fist_r)):
        pygame.draw.line(surf, INK, a, b, int(13 * s))
        pygame.draw.line(surf, OXBLOOD, a, b, int(10 * s))
    pygame.draw.circle(surf, GOLD_DK, (int(fist_r[0]), int(fist_r[1])), int(8 * s))
    pygame.draw.circle(surf, OXBLOOD_DK, (int(fist_r[0]), int(fist_r[1])), int(6 * s))
    # Left (viewer) arm — reaches down-out to grip the trident haft.
    sh_l = (cx - 42 * s, chest_y + 8 * s)
    elb_l = (cx - 58 * s, chest_y + 42 * s)
    grip_l = (cx - 72 * s, hip_y + 6 * s)
    for a, b in ((sh_l, elb_l), (elb_l, grip_l)):
        pygame.draw.line(surf, INK, a, b, int(13 * s))
        pygame.draw.line(surf, OXBLOOD, a, b, int(10 * s))
    pygame.draw.line(surf, OXBLOOD_LIT, (sh_l[0] - 2 * s, sh_l[1]),
                     (elb_l[0] - 2 * s, elb_l[1]), max(1, int(3 * s)))

    # ── HEAD — a lean angular infernal skull-face, brow-shadowed, ember eyes ──
    hr = 22 * s
    hy = neck_y - hr
    # Jaw is squared/tapered (not a soft ball) so the head reads regal + mean.
    head = [(cx - hr, hy - 6 * s), (cx + hr, hy - 6 * s),
            (cx + hr - 3 * s, hy + 10 * s), (cx + 10 * s, hy + hr),
            (cx - 10 * s, hy + hr), (cx - hr + 3 * s, hy + 10 * s)]
    pygame.draw.polygon(surf, OXBLOOD_DK, head)
    pygame.draw.polygon(surf, OXBLOOD,
                        [(cx - hr + 2 * s, hy - 4 * s), (cx + hr - 2 * s, hy - 4 * s),
                         (cx + hr - 5 * s, hy + 9 * s), (cx + 9 * s, hy + hr - 2 * s),
                         (cx - 9 * s, hy + hr - 2 * s), (cx - hr + 5 * s, hy + 9 * s)])
    pygame.draw.polygon(surf, INK, head, max(1, int(2 * s)))
    # Heavy brow shelf (the mean macro shape) + two molten ember eyes glaring.
    pygame.draw.polygon(surf, INK,
                        [(cx - 16 * s, hy - 2 * s), (cx + 16 * s, hy - 2 * s),
                         (cx + 12 * s, hy + 5 * s), (cx - 12 * s, hy + 5 * s)])
    for sgn in (-1, 1):
        ex = cx + sgn * 8 * s
        _glow(surf, ex, hy + 6 * s, 6 * s, EMBER)
        # An angry slit eye angled inward/down (the V-frown that reads as menace).
        eye = [(ex - sgn * 5 * s, hy + 3 * s), (ex + sgn * 5 * s, hy + 5 * s),
               (ex + sgn * 4 * s, hy + 9 * s), (ex - sgn * 4 * s, hy + 8 * s)]
        pygame.draw.polygon(surf, EMBER, eye)
        pygame.draw.circle(surf, EMBER_HOT, (int(ex), int(hy + 6 * s)), max(1, int(1.6 * s)))
    # A short snarling maw with two bone fangs (sparse — not a clown grin).
    my = hy + 15 * s
    pygame.draw.polygon(surf, INK,
                        [(cx - 9 * s, my), (cx + 9 * s, my),
                         (cx + 6 * s, my + 5 * s), (cx - 6 * s, my + 5 * s)])
    for fx in (-5, 5):
        pygame.draw.polygon(surf, BONE,
                            [(cx + fx * s - 2 * s, my + s), (cx + fx * s + 2 * s, my + s),
                             (cx + fx * s, my + 5 * s)])

    # ── CROWN-OF-HORNS — the silhouette signature. In blackout the eye must read
    # ONE crowning gold MASS (Diablo / Doom-Slayer boss read), never three thin
    # slivers. So the two ram-horns no longer float off the temples: they spring
    # from a SOLID crown band laid across the brow, and they are re-arced with
    # MASS — thick at the skull, lifting UP-and-outward (more vertical lift, less
    # horizontal spread) so the tips land high and stay INBOARD of the shoulders.
    # The central crest is the widest gold point so it dominates as the apex and
    # ties the trio into a single regal silhouette.
    #
    # The crown band first: a solid gold arc bridging temple to temple just above
    # the brow, so the horns read as growing OUT OF the crown, not detached. It
    # is drawn before the horns so the horn roots overlap and fuse onto it.
    band_y = hy - 6 * s
    band = [(cx - 22 * s, band_y + 6 * s), (cx - 18 * s, band_y - 4 * s),
            (cx, band_y - 8 * s), (cx + 18 * s, band_y - 4 * s),
            (cx + 22 * s, band_y + 6 * s), (cx + 16 * s, band_y + 9 * s),
            (cx - 16 * s, band_y + 9 * s)]
    pygame.draw.polygon(surf, GOLD_DK, [(int(p[0]), int(p[1])) for p in band])
    pygame.draw.polygon(surf, GOLD,
                        [(int(cx - 19 * s), int(band_y + 4 * s)),
                         (int(cx), int(band_y - 5 * s)),
                         (int(cx + 19 * s), int(band_y + 4 * s)),
                         (int(cx + 14 * s), int(band_y + 7 * s)),
                         (int(cx - 14 * s), int(band_y + 7 * s))])
    pygame.draw.line(surf, GOLD_LIT, (int(cx - 17 * s), int(band_y + 2 * s)),
                     (int(cx + 17 * s), int(band_y + 2 * s)), max(1, s))

    for sgn in (-1, 1):
        # Horn roots sit ON the crown band (wide, so the base fuses into it), and
        # the curve LIFTS hard upward: the control point rises steeply while only
        # nudging outward, and the tip lands HIGH but pulled INBOARD (tip x well
        # inside the shoulder line) so nothing reads as a horizontal antenna and
        # nothing clips at 58px. A short tip flick gives the ram-horn its tell.
        base = (cx + sgn * 18 * s, band_y + 2 * s)
        ctrl = (base[0] + sgn * 26 * s, base[1] - 44 * s)  # LIFT first, slight out
        tip = (base[0] + sgn * 30 * s, base[1] - 84 * s)   # high, kept INBOARD
        spine = []
        n = 18
        for i in range(n + 1):
            t = i / n
            mt = 1 - t
            px = mt * mt * base[0] + 2 * mt * t * ctrl[0] + t * t * tip[0]
            py = mt * mt * base[1] + 2 * mt * t * ctrl[1] + t * t * tip[1]
            spine.append((px, py))
        # Walk the spine offsetting perpendicular by a tapering half-width to
        # build a solid horn polygon. The perpendicular is forced to point so
        # that `outer` is always the AWAY-from-centre side, keeping both horns
        # symmetric regardless of the curve's local direction. The root half-
        # width is ~40% chunkier than round 2 so the base reads as MASS where it
        # meets the crown, then it tapers to a needle.
        inner, outer = [], []
        for i, (px, py) in enumerate(spine):
            t = i / n
            wseg = (20 - 17 * t) * s                  # heavy root → needle tip
            j = min(i + 1, n)
            k = max(i - 1, 0)
            tx, ty = spine[j][0] - spine[k][0], spine[j][1] - spine[k][1]
            tl = math.hypot(tx, ty) or 1
            nx, ny = -ty / tl, tx / tl
            if nx * sgn < 0:                          # keep outer = away from centre
                nx, ny = -nx, -ny
            inner.append((px - nx * wseg * 0.5, py - ny * wseg * 0.5))
            outer.append((px + nx * wseg * 0.5, py + ny * wseg * 0.5))
        horn = outer + list(reversed(inner))
        pygame.draw.polygon(surf, GOLD_DK, [(int(p[0]), int(p[1])) for p in horn])
        # Lit inner facet (the volume-defining highlight, night rim too).
        litband = [(p[0], p[1]) for p in inner] + \
                  [((inner[i][0] + spine[i][0]) * 0.5, (inner[i][1] + spine[i][1]) * 0.5)
                   for i in range(n, -1, -1)]
        pygame.draw.polygon(surf, GOLD, [(int(p[0]), int(p[1])) for p in litband])
        # Ribbed ram-growth ridges across the curve + a hot lit rail (night rim).
        for i in range(2, n, 2):
            a = inner[i]
            b = outer[i]
            pygame.draw.line(surf, GOLD_DK, (int(a[0]), int(a[1])),
                             (int(b[0]), int(b[1])), max(1, s))
        _rim(surf, outer, GOLD_LIT, max(1, s))
    # A SINGLE dominant central crest spire crowning the head — the apex of the
    # crown. Beefed ~30% wider than round 2 so it out-masses each horn root and
    # the trio reads as one regal silhouette, not three competing slivers.
    crest_base_y = hy - 4 * s
    crest_tip_y = hy - 66 * s
    crest = [(cx - 12 * s, crest_base_y), (cx + 12 * s, crest_base_y),
             (cx + 4 * s, crest_tip_y + 12 * s), (cx, crest_tip_y),
             (cx - 4 * s, crest_tip_y + 12 * s)]
    pygame.draw.polygon(surf, GOLD_DK, [(int(p[0]), int(p[1])) for p in crest])
    pygame.draw.polygon(surf, GOLD,
                        [(int(cx - 6 * s), int(crest_base_y)),
                         (int(cx + 6 * s), int(crest_base_y)),
                         (int(cx), int(crest_tip_y + 6 * s))])
    pygame.draw.line(surf, GOLD_LIT, (int(cx), int(crest_tip_y + 6 * s)),
                     (int(cx - 4 * s), int(crest_base_y)), max(1, s))
    # A small ember jewel seating the crest into the crown band.
    _glow(surf, cx, crest_base_y, 6 * s, EMBER)
    pygame.draw.circle(surf, EMBER, (cx, int(crest_base_y)), max(1, int(2.4 * s)))
    pygame.draw.circle(surf, EMBER_HOT, (cx, int(crest_base_y - s)), max(1, int(1.2 * s)))

    # ── THE HELD TRIDENT — gripped in the left fist, planted on the ground. ──
    t_cx = cx - 72 * s
    build_trident(surf, t_cx, chest_y - 30 * s, feet_y + 2 * s, s, hw=6 * s // 1)
    # The gripping fist over the haft (drawn last so it reads in front).
    pygame.draw.circle(surf, GOLD_DK, (int(grip_l[0]), int(grip_l[1])), int(9 * s))
    pygame.draw.circle(surf, OXBLOOD, (int(grip_l[0]), int(grip_l[1])), int(7 * s))
    pygame.draw.line(surf, INK, (int(grip_l[0] - 7 * s), int(grip_l[1] - 2 * s)),
                     (int(grip_l[0] + 7 * s), int(grip_l[1] - 2 * s)), max(1, int(2 * s)))


# ── scene composition ────────────────────────────────────────────────────────

def _day_bg(surf, rect):
    """A BRIGHT day sky — the hard contrast test for the deep oxblood/obsidian."""
    x, y, w, h = rect
    sky = surf.subsurface(rect)
    _grad_v(sky, (0, 0, w, int(h * 0.72)), (96, 188, 240), (188, 226, 246))
    # Warm horizon haze.
    _grad_v(sky, (0, int(h * 0.62), w, int(h * 0.16)), (228, 232, 220), (236, 224, 188))
    # Sun-bleached ground band.
    _grad_v(sky, (0, int(h * 0.78), w, h - int(h * 0.78)), (196, 170, 110), (150, 124, 78))
    pygame.draw.line(sky, (120, 98, 60), (0, int(h * 0.78)), (w, int(h * 0.78)), 2)


def _night_bg(surf, rect):
    """A deep night sky — the test that the GOLD rim carries the read after
    dark while oxblood/obsidian stay legible."""
    x, y, w, h = rect
    sky = surf.subsurface(rect)
    _grad_v(sky, (0, 0, w, int(h * 0.78)), (14, 16, 40), (40, 30, 58))
    # A blood moon low on the horizon (sets the infernal mood).
    pygame.draw.circle(sky, (120, 40, 44), (int(w * 0.74), int(h * 0.40)), int(h * 0.10))
    pygame.draw.circle(sky, (164, 70, 66), (int(w * 0.74), int(h * 0.40)), int(h * 0.085))
    # Stars.
    import random
    rnd = random.Random(7)
    for _ in range(60):
        sx = rnd.randint(0, w)
        sy = rnd.randint(0, int(h * 0.7))
        pygame.draw.circle(sky, (200, 200, 220), (sx, sy), rnd.choice((1, 1, 2)))
    _grad_v(sky, (0, int(h * 0.78), w, h - int(h * 0.78)), (40, 30, 36), (20, 14, 20))
    pygame.draw.line(sky, (70, 50, 56), (0, int(h * 0.78)), (w, int(h * 0.78)), 2)


# True in-game obstacle metrics (game/config.py) — the pillar-fit MUST be shown
# at these, since legibility at native size on a bright day sky is the gate.
PIPE_W = 58
GAP_H = 150


def _pillar_thumb(surf, ox, oy, th, *, night):
    """Prove the trident PROP mirrors into a clean vertical pillar PAIR at TRUE
    in-game width (PIPE_W=58) and a 1x inset — the same `build_trident` head,
    top-half flipped to point DOWN into the gap, bottom-half upright pointing
    UP, the haft running off-tile as the body of the pillar. The fork sits AT
    the gap so the mirror reads as a tidy 6-point starburst, not a tangle.

    Drawn at native scale (ps=2, the K-scale the scrolling tile uses) so what
    you see here is exactly what ships. `night` swaps the sky behind so the
    make-or-break day-sky read AND the gold-rim night read are both shown."""
    tw = PIPE_W
    # Sky strip behind so the contrast test is real.
    skin = pygame.Surface((tw, th), pygame.SRCALPHA)
    if night:
        _grad_v(skin, (0, 0, tw, th), (14, 16, 40), (40, 30, 58))
    else:
        _grad_v(skin, (0, 0, tw, th), (108, 192, 240), (188, 226, 246))
    surf.blit(skin, (ox, oy))
    gap_top = oy + (th - GAP_H) // 2
    gap_bot = gap_top + GAP_H
    ps = 2  # native K-scale, like the scrolling route
    half_h = max(gap_top - oy, oy + th - gap_bot) + 60
    # BOTTOM pillar: trident upright, fork crown pointing UP at the gap.
    bot = pygame.Surface((tw, half_h), pygame.SRCALPHA)
    build_trident(bot, tw // 2, int(40 * ps), half_h + 8 * ps, ps, hw=4 * ps)
    surf.blit(bot, (ox, gap_bot - int(40 * ps)))
    # TOP pillar: the SAME prop flipped vertically — fork crown points DOWN.
    top = pygame.Surface((tw, half_h), pygame.SRCALPHA)
    build_trident(top, tw // 2, int(40 * ps), half_h + 8 * ps, ps, hw=4 * ps)
    top = pygame.transform.flip(top, False, True)
    surf.blit(top, (ox, gap_top + int(40 * ps) - half_h))
    # Frame + faint gap guides.
    pygame.draw.rect(surf, (90, 96, 108), (ox, oy, tw, th), 1)
    guide = (255, 220, 90) if not night else (255, 200, 120)
    pygame.draw.line(surf, guide, (ox, gap_top), (ox + tw, gap_top), 1)
    pygame.draw.line(surf, guide, (ox, gap_bot), (ox + tw, gap_bot), 1)


def main():
    pygame.init()
    W, H = 1260, 760
    surf = pygame.Surface((W, H))
    surf.fill((26, 28, 34))

    font = pygame.font.SysFont("dejavusans", 26, bold=True)
    sub = pygame.font.SysFont("dejavusans", 16)
    tag = pygame.font.SysFont("dejavusans", 15, bold=True)

    # Two figure panels: DAY (left) and NIGHT (right), same figure, same scale.
    pan_w, pan_h = 410, 600
    pan_y = 96
    day_rect = pygame.Rect(40, pan_y, pan_w, pan_h)
    night_rect = pygame.Rect(40 + pan_w + 20, pan_y, pan_w, pan_h)
    _day_bg(surf, day_rect)
    _night_bg(surf, night_rect)

    # Supersample each figure panel for crisp anti-aliased curves, then blit.
    K = 2
    ground_frac = 0.86
    for rect, dark in ((day_rect, False), (night_rect, True)):
        fig = pygame.Surface((pan_w * K, pan_h * K), pygame.SRCALPHA)
        feet_y = int(pan_h * ground_frac) * K
        build_sovereign(fig, (pan_w // 2) * K, feet_y, K, night=dark)
        small = pygame.transform.smoothscale(fig, (pan_w, pan_h))
        surf.blit(small, rect.topleft)
        # Ground shadow ellipse under the hooves.
        gy = rect.y + int(pan_h * ground_frac)
        sh = pygame.Surface((180, 26), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 90), sh.get_rect())
        surf.blit(sh, (rect.centerx - 90, gy - 6))

    pygame.draw.rect(surf, (90, 96, 108), day_rect, 2)
    pygame.draw.rect(surf, (90, 96, 108), night_rect, 2)
    surf.blit(tag.render("DAY SKY", True, (40, 40, 50)), (day_rect.x + 10, day_rect.y + 8))
    surf.blit(tag.render("NIGHT SKY", True, (220, 220, 235)),
              (night_rect.x + 10, night_rect.y + 8))

    # Right column: the make-or-break PILLAR-FIT — the trident prop mirrored
    # into a scrolling pair, shown at TRUE in-game width (58px) on BOTH skies,
    # 1x inset, since day-sky legibility at native size is the gate.
    col_x = night_rect.right + 30
    surf.blit(sub.render("PILLAR-FIT — true 58px, 1x", True, (235, 235, 240)),
              (col_x, pan_y + 4))
    surf.blit(sub.render("trident prop mirrored at the gap", True, (170, 174, 184)),
              (col_x, pan_y + 24))
    th = 420
    _pillar_thumb(surf, col_x, pan_y + 52, th, night=False)
    surf.blit(tag.render("DAY", True, (40, 40, 50)), (col_x + 4, pan_y + 56))
    _pillar_thumb(surf, col_x + PIPE_W + 26, pan_y + 52, th, night=True)
    surf.blit(tag.render("NIGHT", True, (220, 220, 235)),
              (col_x + PIPE_W + 30, pan_y + 56))

    # A 1x blackout-ish silhouette read of the figure (does the upper-radiating
    # crown + horns hold at small size?).
    sil_x = col_x
    sil_y = pan_y + 52 + th + 18
    surf.blit(sub.render("1x SILHOUETTE READ", True, (235, 235, 240)), (sil_x, sil_y))
    sil_w, sil_h = PIPE_W * 2 + 26, 88
    sil = pygame.Surface((sil_w * 3, sil_h * 3), pygame.SRCALPHA)
    build_sovereign(sil, (sil_w // 2) * 3, int(sil_h * 0.94) * 3, 1)
    sil_small = pygame.transform.smoothscale(sil, (sil_w, sil_h))
    surf.blit(sil_small, (sil_x, sil_y + 22))
    pygame.draw.rect(surf, (90, 96, 108), (sil_x, sil_y + 22, sil_w, sil_h), 1)

    # Header.
    surf.blit(font.render("HORNED SOVEREIGN", True, GOLD_LIT), (40, 24))
    surf.blit(sub.render("infernal monarch event boss — crown-of-horns + grand trident — round 3",
                         True, (210, 196, 168)), (40, 60))
    # Palette swatches.
    px = 470
    for name, col in (("oxblood", OXBLOOD), ("obsidian", OBSIDIAN), ("gold", GOLD)):
        pygame.draw.rect(surf, col, (px, 30, 28, 28))
        pygame.draw.rect(surf, (90, 96, 108), (px, 30, 28, 28), 1)
        surf.blit(sub.render(name, True, (210, 210, 220)), (px + 34, 36))
        px += 130

    out = "docs/epic_boss/horned-sovereign/round_3.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
