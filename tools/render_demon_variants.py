"""Look-dev mockup: the EVOLVED "Demon Jester" boss pushed into FIVE distinct
DEMON variations — all UNMISTAKABLY RED, MORE MASSIVE and MEANER (round 2).

Round 1 kept the Demon DNA but the art-director pixel-sampled the bodies as
GREEN-dominant (lime legs read plum/LIME, not "red demon"). Round 2 is a palette
RE-BASE, not a nudge — every body now reads RED at a glance:

  - The costume's TWO roles are both RED now: `dark` is a TRUE CRIMSON
    (~180/40/40 core) and `light` — which the legs lean on hardest — is moved off
    lime onto a desaturated OXBLOOD / MAROON, so green stops dominating the
    silhouette. Lime survives ONLY as a tiny TRIM accent (a collar/cuff edge) via
    a per-figure `_lime_trim` overlay.

The five climactic demons, each a distinct SILHOUETTE hook (tellable at 1x), all
clearly heavier than the original Demon and clearly different from each other:

  1. INFERNO DEMON   — flame-tip shoulders / rising flame accents; the biggest
                       flaming aura + most embers. The "flame" one.
  2. CRIMSON BRUTE   — genuinely the MOST MASSIVE: ~25% wider shoulders, a
                       thicker torso block, heavier stubby limbs, a low wide
                       stance. A wall of true-crimson muscle.
  3. ARCHFIEND       — the regal CROWN-horns (the best hook), lifted off near-
                       black so it holds contrast at 1x.
  4. MOLTEN MAGMA    — glowing red-orange body-CRACKS across the torso/limbs; the
                       best red-hot read, pushed. The lead direction's heat
                       treatment.
  5. ASH OGRE        — a hunched horned heavyweight: smoke wisps + the darkest
                       mood, but RE-ROLLED off the sleeker "Shadowflame" into a
                       distinct stooped ogre so it reads apart AND reddish.

Lead direction (art-director): Molten Magma's red-hot body treatment rebuilt on
the Brute's heavy proportions — a true-crimson, genuinely-bulky boss.

Panel 0 is the UNCHANGED original Demon Jester (boss #3 verbatim) for the side-
by-side comparison.

Three DIE ("cube") fixes, applied to every NEW panel:
  1. The die is CRADLED in the mitt — the raised hand cups/overlaps the die into
     ONE shape (no air-gap), seated down-and-right of the head so it clears the
     horns/shoulder silhouette.
  2. The die is BIGGER — `size≈70` (up ~30% from round 1's 54), so it doesn't
     shrink against the bigger bodies; same 3D isometric cube + pips.
  3. The die aura is a layered CRIMSON→EMBER radial glow (restrained, no neon
     rim), so it reads as a DANGEROUS power object — not a friendly bonus pip.

All of that lives in a LOCAL `draw_boss_die` here — the friendly #13 die in
`render_jester_variants.py` is left untouched.

Nothing under `game/` is touched; we import the real kit and the boss kit and
mutate no state. Headless + deterministic. Output: docs/jester/demon_round_2.png.

    PYTHONPATH=. python tools/render_demon_variants.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from game.draw import lerp_color, blit_glow
from game.parrot import get_parrot
from tools.render_warren_mockup import shaped_palette

from tools.render_clown_dice import (
    _shade, DAY_PHASE, SS, VIEW_W, VIEW_H, HERO_PIPS,
)

# Reuse the approved jester body kit + the friendly die machinery so the demons
# stay in the SAME family and the boss die is pixel-derived from the real prop.
from tools.render_jester_variants import (
    build_jester, cap_four_point, _bell, _cap_point,
    _draw_die_face_noshadow,
)

# Reuse the whole boss kit verbatim: the round-4 amorphous shadow-pool aura, the
# palette-corruption helpers, the menace face/eyes/fangs, the demon cap, the
# brawler-mass shoulders, the corruption seams and the boss build path. We only
# ADD reddish/massive demon flavour on top — we don't fork the boss code.
from tools.render_jester_boss import (
    BASE, corrupt, _deepen, _desat,
    silhouette_aura, build_boss, _add_seams,
    _horn,
    PANEL_W, PANEL_H, FEET_Y, _scene_bg, _blit_parrot,
    BOSSES,
)


# ── reddish-massive demon cap variants ───────────────────────────────────────
# Each demon owns a distinct HORN silhouette so the five read apart at a glance,
# all rooted on the approved four-point fool's cap so they stay demon-JESTERS.

def cap_demon_blunt(surf, cx, base_y, hr, cols):
    """The Brute's cap: two THICK BLUNT horns — short, heavy, brawler-cattle
    horns sweeping low and out, far chunkier than the slim `cap_demon` spikes."""
    cap_four_point(surf, cx, base_y, hr, cols)
    horn = (34, 16, 18)
    for s in (-1, 1):
        bx, by = cx + s * 13, base_y - 2
        tx, ty = cx + s * 30, base_y - 16
        midx, midy = cx + s * 26, base_y - 4
        pts = [(bx - 6, by + 3), (bx + 6, by - 3), (midx, midy),
               (tx, ty), (tx - s * 5, ty + 7)]
        pygame.draw.polygon(surf, horn, pts)
        pygame.draw.polygon(surf, _shade(horn, 40),
                            [(bx - 6, by + 3), (bx + 4, by - 2),
                             (midx, midy)])
        pygame.draw.polygon(surf, _shade(horn, -70), pts, 2)
        # A bone-pale tip so the blunt horn reads heavy + solid, not a dark blob.
        pygame.draw.circle(surf, (196, 150, 120), (tx, ty), 3)


def cap_crown_horns(surf, cx, base_y, hr, cols):
    """The Archfiend's CROWN of horns: a big pair of curved horns arcing UP and
    OUT like a hell-king's crown, plus two short inner prongs — regal menace."""
    cap_four_point(surf, cx, base_y, hr, cols)
    horn = (30, 10, 12)
    # Big outer crown-horns sweeping up + out then curling back inward.
    for s in (-1, 1):
        bx, by = cx + s * 14, base_y - 3
        tip = (cx + s * 22, base_y - 40)
        mid = (cx + s * 30, base_y - 18)
        pts = [(bx - 5, by + 2), (bx + 5, by - 2), mid, tip,
               (tip[0] - s * 6, tip[1] + 8)]
        pygame.draw.polygon(surf, horn, pts)
        pygame.draw.polygon(surf, _shade(horn, 45),
                            [(bx - 5, by + 2), (bx + 3, by - 1), mid])
        pygame.draw.polygon(surf, _shade(horn, -75), pts, 2)
        pygame.draw.circle(surf, (170, 60, 48), tip, 3)
    # Short inner prongs flanking the centre for the crowned, three-tier read.
    for s in (-1, 1):
        _horn(surf, (cx + s * 5, base_y - 4), (cx + s * 9, base_y - 22), horn)


def cap_demon_tall(surf, cx, base_y, hr, cols):
    """Inferno/Molten slim-but-TALLER horns: the demon spikes of `cap_demon`
    lengthened + raked back so they read sharper and meaner."""
    cap_four_point(surf, cx, base_y, hr, cols)
    horn = (32, 12, 16)
    _horn(surf, (cx - 13, base_y - 4), (cx - 26, base_y - 34), horn)
    _horn(surf, (cx + 13, base_y - 4), (cx + 26, base_y - 34), horn)


def cap_ogre(surf, cx, base_y, hr, cols):
    """The Ash Ogre's brutish low horns: a single pair of short, in-curving tusk-
    horns sweeping forward + down off a heavy brow line, set wider + lower than
    the Brute's so the hunched ogre reads apart at a glance."""
    cap_four_point(surf, cx, base_y, hr, cols)
    horn = (30, 14, 16)
    for s in (-1, 1):
        bx, by = cx + s * 15, base_y + 1
        tip = (cx + s * 27, base_y + 6)              # sweeps DOWN + forward (ogre)
        mid = (cx + s * 24, base_y - 8)
        pts = [(bx - 5, by + 2), (bx + 5, by - 3), mid, tip,
               (tip[0] - s * 4, tip[1] + 5)]
        pygame.draw.polygon(surf, horn, pts)
        pygame.draw.polygon(surf, _shade(horn, 42),
                            [(bx - 5, by + 2), (bx + 3, by - 1), mid])
        pygame.draw.polygon(surf, _shade(horn, -72), pts, 2)
        pygame.draw.circle(surf, (188, 142, 116), tip, 3)


# ── the reddish, MASSIVE, mean BOSS die ──────────────────────────────────────
# The friendly #13 die (and the boss sheet's reused die) wear a YELLOW power-up
# aura at `size=40`. The demon boss presents a DANGEROUS reward: a BIGGER cube in
# a CRIMSON → ember-orange aura that is also WIDER/more massive. This is a local
# routine so the friendly die in render_jester_variants stays untouched.

def _boss_aura_surface(radius, breathe, *, core, mid, edge):
    """A layered CRIMSON→EMBER power-up halo. Round-1's halo still read pale-
    yellow/white because the bright core dominated the broad falloff. Round 2
    rebuilds it so CRIMSON is the dominant body of the glow and the hot core is a
    tight, contained ember — the halo reads RED-hot + dangerous, not a friendly
    yellow bonus pip. Same alpha-stop construction as the friendly `_aura_surface`
    so it stays in-family; bigger radius is passed in by the caller so the whole
    aura looms more massive. NO neon ring (matches the approved shadow-pool aura)."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    stops = [
        (1.00, edge, 0),                  # deep-red edge fades to nothing
        (0.92, edge, 150),                # deep crimson edge body
        (0.74, edge, 210),                # crimson is the DOMINANT band now
        (0.50, mid, 234),                 # ember-red shoulder
        (0.30, mid, 250),                 # bright ember-orange
        (0.15, core, 255),               # tight hot ember core (contained)
    ]
    for t_out, col, a_in in stops:
        r = max(1, int(radius * t_out))
        steps = max(3, r // 4)
        for k in range(steps):
            rr = int(r * (1 - k / steps))
            if rr < 1:
                break
            a = int(a_in * (k / steps) ** 0.4)
            a = min(255, int(a * (0.78 + 0.22 * breathe)))
            pygame.draw.circle(s, (*col, a), (c, c), rr)
    return s


def draw_boss_die(surf, cx, base_y, pulse, *, size=70,
                  core=(255, 196, 86), mid=(240, 96, 30),
                  edge=(150, 16, 16), spark=(255, 170, 96)):
    """The demon's presented die: a BIGGER 3D isometric cube (`size≈70`, up ~30%
    from round 1's 54) inside a MASSIVE crimson→ember aura, with red-hot orbiting
    sparkles. Per-demon `core`/`mid`/`edge` let each version's die echo its own
    fire (oxblood Brute, blood-red Archfiend, magma, ash-ember…)."""
    cy = int(base_y + math.sin(pulse * 1.1) * 3)
    breathe = 0.5 + 0.5 * math.sin(pulse * 1.3)
    pr = 1.0 + 0.10 * breathe
    # MORE MASSIVE than the friendly die's ~50px: ~1.5x the bigger cube footprint
    # so the reddish aura looms as a dangerous heat-bloom around the reward.
    # A bright warm ADDITIVE ember glow. A dark alpha-crimson halo just read muddy/
    # cool over the bright day sky; a hot REWARD die must GLOW. Layered additive
    # rings — red edge → ember mid → bright orange core — read as HEAT at 1x while
    # staying warm (cores orange, never pale-white).
    b = 0.82 + 0.18 * breathe
    aura_r = int(size * 1.6 * pr)
    for r_mul, col, al in ((1.05, edge, 80), (0.72, mid, 110),
                           (0.46, mid, 135), (0.26, core, 155)):
        blit_glow(surf, cx, cy, max(2, int(aura_r * r_mul)), col,
                  alpha=int(al * b))

    # The 3D isometric cube prop — same form as the friendly die, just bigger.
    _draw_die_face_noshadow(surf, cx, cy, size, pips=HERO_PIPS)

    # Red-hot orbiting embers replace the friendly cream sparkles.
    for i in range(5):
        a = i * math.tau / 5 + pulse * 0.4
        rr = (size * 0.78) + 5 * math.sin(pulse * 0.9 + i)
        sx = int(cx + math.cos(a) * rr)
        sy = int(cy + math.sin(a) * rr * 0.85)
        tw = 0.5 + 0.5 * math.sin(pulse * 2.0 + i * 1.7)
        al = int(120 + 120 * tw)
        sz = 3 + int(2 * tw)
        s = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
        col = (*spark, al)
        pygame.draw.line(s, col, (sz * 2, 0), (sz * 2, sz * 4), 1)
        pygame.draw.line(s, col, (0, sz * 2), (sz * 4, sz * 2), 1)
        pygame.draw.circle(s, (255, 230, 180, al), (sz * 2, sz * 2), sz)
        surf.blit(s, (sx - sz * 2, sy - sz * 2),
                  special_flags=pygame.BLEND_ADD)


# ── magma seams (fiery re-tint of the Corrupted's glitch cracks) ─────────────

def _add_magma_seams(surf, cx, feet_y):
    """Glowing red-orange MAGMA cracks across the Molten boss's torso AND limbs —
    the lead direction's red-hot read, pushed: deep-red fissures with a hot
    orange-yellow molten core glowing along each, plus a few small glowing nodes
    where seams branch, so the body reads as cracked cooling lava. Spread wider +
    onto the legs this round so the heat covers the whole silhouette, not just a
    torso patch."""
    hip_y = feet_y - 84
    top = hip_y - 50
    rng = __import__('random').Random(909)

    def _seam(x0, y0, segs, span):
        pts = [(x0, y0)]
        for _ in range(segs):
            x0 += rng.randint(-span, span)
            y0 += rng.randint(8, 16)
            pts.append((x0, y0))
        # Dark fissure walls, a hot molten core line, then a white-hot centre.
        pygame.draw.lines(surf, (60, 8, 4), False, pts, 4)
        pygame.draw.lines(surf, (236, 92, 20), False, pts, 2)
        pygame.draw.lines(surf, (255, 224, 128), False, pts, 1)
        # A glowing node at a branch point so the magma reads as pooling, not lines.
        nx, ny = pts[len(pts) // 2]
        blit_glow(surf, nx, ny, 5, (255, 150, 40), alpha=120)

    # Torso fissures.
    for _ in range(5):
        _seam(cx + rng.randint(-24, 24), top + rng.randint(2, 10), 3, 7)
    # Limb fissures — short cracks down each thigh so the legs glow red-hot too.
    for s in (-1, 1):
        _seam(cx + s * 12, hip_y + rng.randint(4, 10), 2, 4)


def _lime_trim(surf, cx, feet_y, lime):
    """The ONLY surviving lime: a tiny harlequin TRIM accent so the costume keeps
    a whisper of its plum/LIME jester DNA without letting green dominate the now-
    RED silhouette — a thin lime piping along the collar lobes + a small lime cuff
    band on each ankle. Restrained on purpose (the bodies must read RED first)."""
    hip_y = feet_y - 84
    neck_y = hip_y - 50
    hip_cx = cx - 6
    # A short lime arc piping under the collar ruff.
    pygame.draw.arc(surf, lime, (hip_cx - 16, neck_y - 4, 32, 18),
                    math.pi * 0.12, math.pi * 0.88, 2)
    # A thin lime cuff ring at each ankle.
    for ax in (cx - 12, cx + 15):
        pygame.draw.circle(surf, lime, (ax, feet_y - 12), 5, 2)


def _flame_shoulders(surf, cx, feet_y, flame, ember):
    """Inferno's hook: flame-tip SHOULDERS — a fan of rising flame tongues
    licking up off each shoulder so the silhouette itself reads as fire, not just
    a red body in a fiery aura. Drawn on the figure layer so it scales WITH the
    boss and stays part of the silhouette."""
    hip_y = feet_y - 84
    sh_y = hip_y - 48
    for s in (-1, 1):
        base_x = cx - 6 + s * 24
        for j, (dx, dh) in enumerate(((0, 26), (-s * 6, 18), (s * 7, 20))):
            tipx = base_x + dx + s * 2
            tipy = sh_y - dh
            flick = s * 5
            pts = [(base_x - 5, sh_y + 2), (base_x + 5, sh_y + 2),
                   (tipx + flick, tipy + 6), (tipx, tipy)]
            pygame.draw.polygon(surf, flame, pts)
            # Hot inner core tongue.
            pygame.draw.polygon(surf, ember,
                                [(base_x - 2, sh_y), (base_x + 2, sh_y),
                                 (tipx, tipy + 5)])


# ── the demon palette helper (ROUND 2 — a full RED RE-BASE) ──────────────────
# Round 1 read GREEN-dominant because the legs lean on `light`, which was a lime.
# Round 2 RE-BASES both costume roles onto RED so the silhouette reads
# unmistakably red at a glance:
#   - `dark`  → a TRUE CRIMSON anchored on (180, 40, 40), nudged per demon.
#   - `light` → a desaturated OXBLOOD / MAROON (NOT lime) — this is the colour
#     the legs use most, so green no longer dominates the legs.
# Both roles stay close in HUE (two reds) but apart in VALUE so the quartered
# harlequin torso + two-tone hose still read as a costume, just a RED one. Lime
# survives only as the tiny `_lime_trim` accent, never as a body role.

CRIMSON_CORE = (182, 42, 42)            # the true-crimson torso anchor
OXBLOOD_LEG = (120, 34, 36)            # the desaturated maroon the legs ride on


def demon_palette(red, *, deep=0.0, light_deep=0.0, desat=0.0, tint=0.0,
                  gold_lift=0.0, lift=0.0):
    """A fully RED demon costume. `dark` is the true crimson torso anchor pulled
    a touch toward this demon's own `red` (so the five read apart on hue/value
    without any leaving red); `light` is the oxblood/maroon leg+panel role,
    deepened by `light_deep` for the moodier demons. `lift` raises the whole
    value (Archfiend, so it doesn't crush near-black at 1x); `desat` greys both
    roles slightly (the Ash Ogre's ashen read)."""
    dark = lerp_color(CRIMSON_CORE, red, tint)
    light = lerp_color(OXBLOOD_LEG, red, tint * 0.5)
    if deep:
        dark = _deepen(dark, deep)
    if light_deep:
        light = _deepen(light, light_deep)
    if desat:
        dark = _desat(dark, desat)
        light = _desat(light, desat)
    if lift:
        dark = lerp_color(dark, (210, 96, 80), lift)
        light = lerp_color(light, (170, 70, 64), lift)
    gold = corrupt(BASE["gold"], red, deep=0.18, desat=0.12, tint=0.18)
    if gold_lift:
        gold = lerp_color(gold, (236, 184, 56), gold_lift)
    # The lime that now survives only as a trim accent — kept here so each spec
    # can pass its own (slightly desaturated so it never shouts over the red).
    lime = _desat((132, 218, 116), 0.22)
    return {"dark": dark, "light": light, "gold": gold, "lime": lime}


# ── the five reddish/massive demons ──────────────────────────────────────────
# Every entry keeps the Demon DNA (horns, RED-shifted plum/lime, fangs, glowing
# eyes, the amorphous reddish shadow-pool aura) and is CLEARLY more massive than
# the original Demon (scale 1.40) and distinct from the others. `die` carries the
# per-demon crimson→ember die tint so the dangerous reward echoes each fire.

# Per-demon RED anchors — all reds, spread across hue/value so the five read
# apart while every body stays unmistakably RED. The torso/legs are RE-BASED onto
# crimson/oxblood (demon_palette); these only NUDGE that base toward each fire.
INFERNO = (236, 92, 30)            # orange-leaning crimson (fire)
BRUTE_RED = (176, 44, 40)          # broad true crimson (muscle)
BLOOD = (150, 40, 44)              # blood-red, lifted so it holds at 1x
MAGMA = (210, 70, 26)              # smouldering orange-red (lava)
ASH_RED = (140, 48, 46)            # ashen desaturated red (the ogre)

DEMONS = [
    # 1 — INFERNO DEMON: the FLAME one. Flame-tip shoulders rising off the
    # silhouette + the biggest flaming aura + most embers. Orange-leaning crimson.
    dict(name="Inferno Demon",
         vibe="FLAME-TIP shoulders · biggest flame aura · most embers",
         pal=demon_palette(INFERNO, tint=0.40),
         aura_hue=(248, 120, 24), aura_dark=(40, 10, 4), rim=(255, 150, 40),
         glow=(255, 196, 40), cap=cap_demon_tall, scale=1.50, fang_xtra=5,
         mass=1.08, aura_bulk=1.35, ember_boost=True, flames=True, lime_trim=True,
         die=dict(core=(255, 196, 96), mid=(248, 110, 28),
                  edge=(176, 30, 8), spark=(255, 176, 96))),
    # 2 — CRIMSON BRUTE: genuinely the MOST MASSIVE — ~25% wider shoulders, a
    # thicker torso block, heavier stubby limbs, a low wide stance. True crimson.
    dict(name="Crimson Brute",
         vibe="MOST MASSIVE · wide shoulders · thick block · low stance",
         pal=demon_palette(BRUTE_RED, tint=0.30),
         aura_hue=(196, 30, 30), aura_dark=(28, 4, 6), rim=(200, 36, 40),
         glow=(255, 84, 56), cap=cap_demon_blunt, scale=1.62, fang_xtra=4,
         mass=1.52, head_tilt=-3, aura_bulk=1.25, lime_trim=True,
         die=dict(core=(255, 170, 84), mid=(222, 70, 30),
                  edge=(132, 14, 14), spark=(255, 140, 84))),
    # 3 — ARCHFIEND: the regal CROWN-horns (the best hook). LIFTED off near-black
    # (~+15% value) so it holds contrast at 1x — blood-red, commanding.
    dict(name="Archfiend",
         vibe="regal CROWN-horns · blood-red · lifted, holds at 1x",
         pal=demon_palette(BLOOD, tint=0.34, lift=0.18, gold_lift=0.34),
         aura_hue=(180, 26, 30), aura_dark=(26, 6, 8), rim=(196, 36, 40),
         glow=(255, 80, 56), cap=cap_crown_horns, scale=1.54, fang_xtra=3,
         mass=1.14, head_tilt=-2, aura_bulk=1.2, lime_trim=True,
         die=dict(core=(255, 178, 96), mid=(224, 64, 30),
                  edge=(140, 18, 16), spark=(255, 150, 90))),
    # 4 — MOLTEN MAGMA (the lead direction): the red-hot body-CRACKS pushed across
    # torso AND limbs, rebuilt on heavy proportions — a true-crimson, bulky boss.
    dict(name="Molten Magma",
         vibe="red-hot CRACKS torso+limbs · heavy · smouldering volcanic",
         pal=demon_palette(MAGMA, tint=0.42),
         aura_hue=(228, 84, 18), aura_dark=(34, 8, 4), rim=(244, 110, 26),
         glow=(255, 170, 36), cap=cap_demon_tall, scale=1.52, fang_xtra=4,
         mass=1.32, head_tilt=-2, magma=True, aura_bulk=1.28, ember_boost=True,
         lime_trim=True,
         die=dict(core=(255, 196, 100), mid=(244, 110, 24),
                  edge=(160, 32, 8), spark=(255, 170, 96))),
    # 5 — ASH OGRE (re-rolled off the sleek "Shadowflame"): a HUNCHED horned
    # heavyweight — the darkest mood + smoke wisps, but a distinct stooped ogre
    # silhouette (forward lean, low tusk-horns) so it reads apart AND reddish.
    dict(name="Ash Ogre",
         vibe="HUNCHED heavyweight · low tusk-horns · ashen red · smoke",
         pal=demon_palette(ASH_RED, tint=0.30, light_deep=0.18, desat=0.18),
         aura_hue=(150, 30, 30), aura_dark=(14, 4, 6), rim=(168, 36, 38),
         glow=(255, 78, 58), cap=cap_ogre, scale=1.50, fang_xtra=5,
         mass=1.34, lean=0.12, head_tilt=6, skin=(168, 124, 118),
         aura_bulk=1.2, lime_trim=True,
         die=dict(core=(255, 164, 88), mid=(212, 66, 34),
                  edge=(120, 18, 16), spark=(255, 132, 86))),
]


# ── per-cell scene (mirrors render_jester_boss.render_boss, demon die + dies) ─
# Same taller day-clearing panel + un-scaled parrot ruler as the boss sheet, but
# the die is repositioned UP-LEFT to track the ENLARGED raised arm and drawn with
# the bigger reddish boss die.

def _die_seat(scale, *, original=False):
    """Where the die sits. Panel 0 (`original`) keeps its round-1 BEFORE placement
    verbatim so the comparison baseline is unchanged. The new demons use the
    round-2 CRADLE seat (round 1 left an air-gap up-right of the cube and the die
    clipped the horns): the die is pulled IN (less far left) so it clears the
    horn/shoulder silhouette and seated a touch LOWER so the raised mitt can come
    up under it; both still rise with scale (the figure is scaled about the feet)."""
    jester_cx = PANEL_W // 2 + 12
    if original:
        die_x = int(jester_cx - 60 * scale)
        die_base_y = int(36 - 30 * (scale - 1.0))
        return jester_cx, die_x, die_base_y
    die_x = int(jester_cx - 64 * scale)            # OUTWARD (left) so it clears horns
    die_base_y = int(38 - 28 * (scale - 1.0))       # + a touch higher, off the head
    return jester_cx, die_x, die_base_y


def render_original(idx):
    """Panel 0: the UNCHANGED original Demon Jester (boss #3 verbatim), drawn so
    its FEET land on FEET_Y, with its ORIGINAL die placement + yellow-ish boss
    die — the comparison baseline."""
    spec = next(b for b in BOSSES if b["name"] == "The Demon Jester")
    return _render_demon(spec, idx, original=True)


def render_demon(spec, idx):
    return _render_demon(spec, idx, original=False)


def _render_demon(spec, idx, *, original):
    bw, bh = PANEL_W * SS, PANEL_H * SS
    big = pygame.Surface((bw, bh))
    _scene_bg(big, bw, bh, idx)

    breathe = 0.5 + 0.5 * math.sin((idx * 1.7 + 2.0) * 1.3)
    scale = spec["scale"]
    jester_cx, die_x, die_base_y = _die_seat(scale, original=original)
    base_feet = FEET_Y

    # The raised LEFT arm CRADLES the die. Built at base, the hand seat must point
    # at the die's pre-scale position so that AFTER the about-the-feet scale it
    # lands where we want on the die. Solve the inverse: a point P on the figure
    # maps to jester_cx + (P - jester_cx)*scale; we want that to equal the cradle
    # point, so P = jester_cx + (target - jester_cx)/scale. Round-2 cradle fix: the
    # mitt is seated UNDER + slightly LEFT of the die centre so the round glove cups
    # the cube's lower-left corner and overlaps it into ONE shape (round 1 sat the
    # mitt ~5px below the smaller cube's bottom edge → a visible air-gap up-right).
    # `build_boss` also widens the figure horizontally by `mass` ABOUT jester_cx
    # before this about-feet scale, so the hand's net horizontal factor from the
    # centreline is mass*scale (vertical is scale only). Fold mass into the inverse
    # solve so the cradle stays married on the heavy (high-mass) demons too. Panel
    # 0 keeps its round-1 BEFORE reach verbatim (no cradle offset, mass 1.0).
    mass = spec.get("mass", 1.0)
    if original:
        cradle_x, cradle_y = die_x + 6, die_base_y + 34
    else:
        cradle_x = die_x - 8                   # cup the die's LOWER-LEFT corner
        cradle_y = die_base_y + 26             # tucked UP into the cube's belly
    hand_x = int(jester_cx + (cradle_x - jester_cx) / (scale * mass))
    hand_y = int(base_feet + (cradle_y - base_feet) / scale)
    hand_up = (hand_x, hand_y)

    fig = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pal = spec["pal"]
    build_boss(fig, jester_cx, base_feet, hand_up,
               dark=pal["dark"], light=pal["light"], gold=pal["gold"],
               cap_fn=spec["cap"], glow_col=spec["glow"],
               fang_xtra=spec.get("fang_xtra", 0),
               narrow_eyes=spec.get("narrow_eyes", False),
               skin=spec.get("skin", (200, 150, 140)),
               shadow_face=spec.get("shadow_face", False),
               mass=spec.get("mass", 1.0), lean=spec.get("lean", 0.0),
               head_extra_tilt=spec.get("head_tilt", 0))
    if spec.get("flames"):
        # Drawn on the figure layer (pre-scale) so the flame-tips scale WITH the
        # boss and become part of the silhouette — Inferno's distinct hook.
        _flame_shoulders(fig, jester_cx, base_feet, spec["aura_hue"],
                         (255, 224, 130))
    if spec.get("magma"):
        _add_magma_seams(fig, jester_cx, base_feet)
    if spec.get("seams"):
        _add_seams(fig, jester_cx, base_feet, spec["glow"])
    if spec.get("lime_trim"):
        # The ONLY surviving lime — a tiny harlequin trim accent so the now-RED
        # costume keeps a whisper of its plum/lime jester DNA.
        _lime_trim(fig, jester_cx, base_feet, pal["lime"])

    # Scale the figure UP about the FEET so it looms taller/broader yet stays
    # planted, then grow the amorphous reddish shadow-pool aura from its own
    # silhouette (the round-4 approved look, just reddish hues).
    sw, sh = int(PANEL_W * scale), int(PANEL_H * scale)
    fig_big = pygame.transform.smoothscale(fig, (sw, sh))
    off_x = int(jester_cx - jester_cx * scale)
    off_y = int(base_feet - base_feet * scale)
    boss_layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    boss_layer.blit(fig_big, (off_x, off_y))

    boss_ss = pygame.transform.smoothscale(boss_layer, (bw, bh))
    torso_x = int(jester_cx * SS)
    torso_y = int((FEET_Y - 70) * SS)
    # `aura_bulk` widens the dark pool per demon — Inferno/Brute/Archfiend read
    # MORE MASSIVE than the original Demon's pool.
    silhouette_aura(big, boss_ss, torso_x, torso_y, spec["aura_hue"], breathe,
                    dark=spec["aura_dark"], rim=spec.get("rim"),
                    embers=True, smoke=True, seed=idx, scl=SS,
                    bulk=spec.get("aura_bulk", 1.0))
    if spec.get("ember_boost"):
        # Inferno/Molten smoulder hardest — a second ember pass for the most
        # flame, seeded apart so the two passes don't overlap.
        silhouette_aura(big, boss_ss, torso_x, torso_y, spec["aura_hue"],
                        breathe, dark=spec["aura_dark"], rim=spec.get("rim"),
                        embers=True, smoke=False, seed=idx + 97, scl=SS,
                        bulk=spec.get("aura_bulk", 1.0))

    big.blit(boss_ss, (0, 0))

    # The reddish, MASSIVE, mean BOSS die — repositioned UP-LEFT into the cup of
    # the enlarged mitt. The original-Demon panel keeps the SMALLER die at the
    # base seat (its yellow-leaning tint) so the comparison is fair; the five new
    # demons get the bigger reddish die.
    overlay = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    if original:
        # Original Demon: baseline die placement + the original yellow-warm aura
        # at the smaller base size, so panel 0 shows the BEFORE die.
        draw_boss_die(overlay, die_x, die_base_y, idx * 1.7 + 2.0, size=40,
                      core=(255, 240, 150), mid=(255, 196, 60),
                      edge=(232, 150, 30), spark=(255, 236, 140))
    else:
        dk = spec["die"]
        draw_boss_die(overlay, die_x, die_base_y, idx * 1.7 + 2.0, size=70,
                      core=dk["core"], mid=dk["mid"], edge=dk["edge"],
                      spark=dk["spark"])
    _blit_parrot(overlay)
    big.blit(pygame.transform.smoothscale(overlay, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


# ── sheet layout ──────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    cells = []
    captions = []
    cells.append(render_original(0))
    captions.append(("ORIGINAL Demon Jester",
                     "boss #3 verbatim · scale 1.40 · base die placement "
                     "(the BEFORE — note the LIME legs)"))
    for i, spec in enumerate(DEMONS, start=1):
        cells.append(render_demon(spec, i))
        captions.append((spec["name"], spec["vibe"]))

    cols, rows = 3, 2
    sw, sh = int(PANEL_W * 3.1), int(PANEL_H * 3.1)

    PAD = 48
    GAP = 26
    TITLE_H = 100
    CAP_H = 70
    FOOT_H = PANEL_H + 40

    canvas_w = PAD * 2 + cols * sw + (cols - 1) * GAP
    canvas_h = (PAD * 2 + TITLE_H + rows * (sh + CAP_H) + (rows - 1) * GAP
                + FOOT_H)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((16, 10, 12))

    f_title = pygame.font.SysFont(None, 74, bold=True)
    f_sub = pygame.font.SysFont(None, 32, bold=True)
    f_cap = pygame.font.SysFont(None, 40, bold=True)
    f_caps = pygame.font.SysFont(None, 28, bold=True)

    title = f_title.render(
        "DEMON JESTER — 5 RED-rebased · massive · meaner variations (round 3 (final): warm-glow die · cleared horns · no torso cross)",
        True, (255, 214, 200))
    canvas.blit(title, (PAD, PAD - 2))
    sub = f_sub.render(
        "Round 2 RE-BASES the lineup to RED: torsos true CRIMSON, legs OXBLOOD/"
        "MAROON (off lime — lime survives only as a tiny collar/cuff trim). "
        "Structurally distinct: Inferno = FLAME-TIP shoulders · Brute = MOST "
        "MASSIVE (wide block, low stance) · Archfiend = regal CROWN-horns "
        "(lifted off black) · Molten = red-hot CRACKS on torso+limbs · Ash Ogre "
        "= hunched tusk-horn heavyweight. DIE FIXES: CRADLED in the mitt (no air-"
        "gap, clears horns) · BIGGER cube (70 vs 54) · CRIMSON->EMBER aura.",
        True, (210, 184, 184))
    canvas.blit(sub, (PAD, PAD + 54))

    y0 = PAD + TITLE_H
    STRONG = {2, 4}              # the lead heavyweights (Brute, Molten) flagged
    inset_cells = {}
    for i, cell in enumerate(cells):
        r, c = divmod(i, cols)
        cx = PAD + c * (sw + GAP)
        cy = y0 + r * (sh + CAP_H + GAP)
        scaled = pygame.transform.smoothscale(cell, (sw, sh))
        border = (220, 60, 40) if i in STRONG else (80, 50, 50)
        pygame.draw.rect(canvas, border,
                         pygame.Rect(cx - 2, cy - 2, sw + 4, sh + 4), 2)
        canvas.blit(scaled, (cx, cy))
        name, vibe = captions[i]
        tag = "0. " + name if i == 0 else f"{i}. {name}"
        cap = f_cap.render(tag, True, (252, 220, 200))
        canvas.blit(cap, (cx + (sw - cap.get_width()) // 2, cy + sh + 8))
        sub2 = f_caps.render(vibe, True, (206, 178, 178))
        canvas.blit(sub2, (cx + (sw - sub2.get_width()) // 2, cy + sh + 42))
        if i in (2, 4):           # Brute + Molten — the two 1x validation cells
            inset_cells[i] = cell

    # TWO 1x insets — the validation GATE at in-game scale: (a) the enlarged mitt
    # must CRADLE the bigger die into one shape, and (b) the die aura must read
    # CRIMSON/ember (dangerous), not friendly yellow. Brute = the mass + cradle
    # read; Molten = the red-hot cracks + die-aura read (the lead direction).
    foot_y = y0 + rows * (sh + CAP_H) + (rows - 1) * GAP + 16
    cap_intro = f_cap.render(
        "1x in-game scale — die CRADLED in the mitt (one shape, clears horns) + "
        "CRIMSON/ember die aura?",
        True, (252, 200, 190))
    canvas.blit(cap_intro, (PAD, foot_y - 4))
    iy = foot_y + 40
    insets = (
        (2, "Crimson Brute — the heaviest · die cradled in the mitt",
         "most massive silhouette · crimson->ember die aura · long fangs"),
        (4, "Molten Magma — red-hot cracks torso+limbs · die cradled",
         "the lead direction · crimson body · dangerous ember die aura"),
    )
    for n, (idx_s, lab_t, lab2_t) in enumerate(insets):
        cell = inset_cells.get(idx_s)
        if cell is None:
            continue
        ix = PAD + n * (PANEL_W + 360)
        pygame.draw.rect(canvas, (220, 60, 40),
                         pygame.Rect(ix - 2, iy - 2, PANEL_W + 4,
                                     PANEL_H + 4), 2)
        canvas.blit(cell, (ix, iy))
        lab = f_caps.render(lab_t, True, (216, 188, 188))
        canvas.blit(lab, (ix + PANEL_W + 16, iy + PANEL_H // 2 - 30))
        lab2 = f_caps.render(lab2_t, True, (186, 162, 162))
        canvas.blit(lab2, (ix + PANEL_W + 16, iy + PANEL_H // 2 + 2))

    out_dir = os.path.join("docs", "jester")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "demon_round_3.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
