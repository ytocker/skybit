"""Game-side seam for the Skull-King demo: stacked-skull totem PILLARS (and the
rolling king-skull "die") rendered by reusing the design-time skull engine.

This backs a native-only R&D harness, exactly like game/pillar_staff.py backs the
clown demo. The skull engine and the 20 column recipes live under docs/ (not
bundled in the web build), so they are lazy-imported the first time a skull pillar
is drawn — after the real display already exists, and never on web. Every reuse
point is guarded: if the engine or a design module is missing (stripped / web
checkout) the caller is told so it can fall back to a plain pillar, so a run never
crashes on the skull path.
"""
import os
import sys
import importlib.util

import pygame

from game.config import PIPE_W

# Seat the focal skull right at the gap edge so pillars frame the channel tightly —
# matches the approved route figure (tools/render_skull_routes.py forces 1.05 for all).
ROUTE_MARGIN_R = 1.05

# The twenty designs in P1..P20 order — mirrors tools/render_skull_routes.DESIGN_FILES
# (the same source the approved route figure draws from).
_DESIGN_FILES = [
    ("relic-reliquary-totem",        "render_relic_reliquary_totem.py"),
    ("horned-warband",               "render_horned_warband.py"),
    ("keystone-cairn",               "render_keystone_cairn.py"),
    ("gaunt-hollow-spire",           "render_gaunt_hollow_spire.py"),
    ("broken-bone-pile",             "render_broken_bone_pile.py"),
    ("plain-bone-spit",              "render_plain_bone_spit.py"),
    ("gold-cored-scepter",           "render_gold_cored_scepter.py"),
    ("ring-eye-washer-axle",         "render_ring_eye_washer_axle.py"),
    ("barbed-fang-harpoon",          "render_barbed_fang_harpoon.py"),
    ("bead-threaded-strand-spindle", "render_bead_threaded_strand_spindle.py"),
    ("runt-cairn-taper",             "render_runt_cairn_taper.py"),
    ("thirdeye-watchtower",          "render_thirdeye_watchtower.py"),
    ("lopsided-fang-lean",           "render_lopsided_fang_lean.py"),
    ("child-relic-shrine",           "render_child_relic_shrine.py"),
    ("darkblue-bone-rosary",         "render_darkblue_bone_rosary.py"),
    ("broad-block-bastion",          "render_broad_block_bastion.py"),
    ("cracked-ruin-lean",            "render_cracked_ruin_lean.py"),
    ("palm-jewel-pagoda",            "render_palm_jewel_pagoda.py"),
    ("necklace-draped-warlord",      "render_necklace_draped_warlord.py"),
    ("mongrel-generations-totem",    "render_mongrel_generations_totem.py"),
]

_engine = None     # pillar_engine module once loaded, or False if unavailable
_designs = None     # list of dict(recipe, with_skewer, skewer_style, lean), or None
_die_mod = None     # the docs/ skull-die render module, or False if unavailable


def _repo_root():
    # game/pillar_skull.py -> <repo>/game -> <repo>; derived (not hard-coded) so the
    # demo runs from any checkout location.
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _add_paths(*dirs):
    for p in dirs:
        if p and p not in sys.path:
            sys.path.insert(0, p)


def _load_engine():
    """Import the skull engine + the 20 recipes once. Returns (engine, designs) or
    (None, None) if docs/ isn't present in this checkout. Cached after first call."""
    global _engine, _designs
    if _engine is not None:
        return (_engine or None), _designs
    try:
        root = _repo_root()
        pillars_dir = os.path.join(root, "docs", "skull_king_stack", "pillars")
        # pillar_engine itself reaches into tools/ for the element draw fns; put both
        # on the path (its own hard-coded ROOT insert is then a harmless no-op).
        _add_paths(pillars_dir, os.path.join(root, "tools"))
        import pillar_engine as PE
        designs = []
        for slug, fname in _DESIGN_FILES:
            spec = importlib.util.spec_from_file_location(
                "skdsn_" + slug.replace("-", "_"),
                os.path.join(pillars_dir, slug, fname))
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            designs.append(dict(recipe=m.RECIPE, with_skewer=m.WITH_SKEWER,
                                skewer_style=m.SKEWER_STYLE,
                                lean=getattr(m, "LEAN", 0.0)))
        _engine, _designs = PE, designs
    except Exception:
        _engine, _designs = False, None
    return (_engine or None), _designs


def available():
    """True if the skull engine + recipes loaded (docs/ present)."""
    return _load_engine()[0] is not None


def design_count():
    _, d = _load_engine()
    return len(d) if d else 0


def _fill(recipe, hpx):
    """Tile a recipe to fill a pillar of height hpx: focal at the gap, then cycle the
    body up the column (extra tiers past the surface clip harmlessly). Matches
    tools/render_skull_routes._fill so the demo reads like the approved figure."""
    n = max(len(recipe), int(hpx / 34) + 2)
    body = recipe[1:] if len(recipe) > 1 else recipe
    return [recipe[0]] + [body[i % len(body)] for i in range(n - 1)]


def _half(PE, design, hpx, cap):
    return PE.render_pillar_half(int(hpx), cap=cap, recipe=_fill(design["recipe"], hpx),
                                 with_skewer=design["with_skewer"],
                                 skewer_style=design["skewer_style"],
                                 lean=design["lean"], margin_r=ROUTE_MARGIN_R)


def draw_pillar_pair_skull(surf, top_rect, bot_rect, palette, seed, design_idx=0):
    """Paint a stacked-skull totem pair (top + bottom halves framing the gap) onto
    `surf`, using design `design_idx` of the 20. Same call contract as
    game/pillar_staff.draw_pillar_pair_staff (+ which design). Returns True on
    success, False if the engine/recipes are unavailable so the caller can fall
    back to a plain pillar. `palette`/`seed` are accepted for parity (the skull art
    carries its own bone/gold palette)."""
    PE, designs = _load_engine()
    if PE is None or not designs:
        return False
    design = designs[design_idx % len(designs)]
    th, bh = int(top_rect.height), int(bot_rect.height)
    if th > 6:
        surf.blit(_half(PE, design, th, "bottom"), (int(top_rect.x), int(top_rect.y)))
    if bh > 6:
        surf.blit(_half(PE, design, bh, "top"), (int(bot_rect.x), int(bot_rect.y)))
    return True


# ── rolling king-skull "die" ──────────────────────────────────────────────────
def _load_die():
    """Import the docs/ skull-die art module once (the king-skull + difficulty
    faces). Returns the module or None if missing. Cached."""
    global _die_mod
    if _die_mod is not None:
        return _die_mod or None
    try:
        root = _repo_root()
        die_dir = os.path.join(root, "docs", "skull_king_stack", "die")
        _add_paths(die_dir,
                   os.path.join(root, "docs", "skull_king_stack", "pillars"),
                   os.path.join(root, "tools"))
        spec = importlib.util.spec_from_file_location(
            "skull_die_mod", os.path.join(die_dir, "render_skull_die.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _die_mod = m
    except Exception:
        _die_mod = False
    return _die_mod or None


def draw_rolling_skull(surf, cx, cy, px, *, angle=0.0, difficulty=None, neutral=False):
    """Draw the king-skull "die" centred at (cx, cy): the tumbling skull (neutral or
    a flicker face) and, once settled, the distinctive difficulty face. Rotated by
    `angle` degrees for the tumble. Falls back to a plain bone glyph if the die art
    module is absent, so the beat still plays.

    The die art is supersampled (SS=8) procedural work — far too heavy to redraw
    every frame, which made the roll + the growing reveal stutter. Each distinct face
    (neutral + difficulties 6-10) is baked ONCE at a canonical size and cached; per
    frame we only cheap-scale to `px` and rotate, so the whole beat costs at most six
    real renders total."""
    base = _die_scaled(px, difficulty, neutral)
    img = pygame.transform.rotate(base, angle) if angle else base
    surf.blit(img, img.get_rect(center=(int(cx), int(cy))))


_CANON_DIE_PX = 128       # one bake per face at this size; all draws scale DOWN from it
_die_base_cache = {}      # (difficulty|None, neutral) -> canonical-size base Surface
_die_scaled_cache = {}    # (int(px), difficulty|None, neutral) -> base scaled to px

# The faces the roll flickers through (neutral hovers pre-grab; 6-10 are the outcomes).
_PREWARM_FACES = [(None, True)] + [(d, False) for d in (6, 7, 8, 9, 10)]


def prewarm_die_face():
    """Bake ONE not-yet-cached die face (the heavy SS=8 render). Call across the calm
    frames before the grab so the tumble + reveal never pay a bake mid-roll. Returns
    True while faces remain, False once every face is cached."""
    for difficulty, neutral in _PREWARM_FACES:
        if (difficulty, bool(neutral)) not in _die_base_cache:
            _die_base(difficulty, neutral)
            return True
    return False


def _die_base(difficulty, neutral):
    """Bake one face (neutral or a difficulty) at the canonical size, cached forever."""
    key = (None if neutral else difficulty, bool(neutral))
    s = _die_base_cache.get(key)
    if s is None:
        px = _CANON_DIE_PX
        box = int(px * 1.7) + 10
        s = pygame.Surface((box, box), pygame.SRCALPHA)
        mod = _load_die()
        drawn = False
        if mod is not None and hasattr(mod, "draw_skull_die"):
            try:
                mod.draw_skull_die(s, box // 2, box // 2, int(px),
                                   difficulty=difficulty, neutral=neutral)
                drawn = True
            except Exception:
                drawn = False
        if not drawn:
            _fallback_skull(s, box // 2, box // 2, int(px), difficulty, neutral)
        _die_base_cache[key] = s
    return s


def _die_scaled(px, difficulty, neutral):
    """The canonical base scaled to `px`, cached per size so the constant-size tumble
    never re-scales and the growing reveal bakes one cheap scale per pop frame."""
    ipx = int(px)
    key = (ipx, None if neutral else difficulty, bool(neutral))
    s = _die_scaled_cache.get(key)
    if s is None:
        base = _die_base(difficulty, neutral)
        if ipx == _CANON_DIE_PX:
            s = base
        else:
            f = px / _CANON_DIE_PX
            s = pygame.transform.smoothscale(
                base, (max(1, int(base.get_width() * f)),
                       max(1, int(base.get_height() * f))))
        _die_scaled_cache[key] = s
    return s


_DIFF_GLOW = {6: (245, 196, 90), 7: (245, 156, 70), 8: (242, 110, 60),
              9: (232, 70, 56), 10: (220, 40, 48)}


def _fallback_skull(surf, cx, cy, px, difficulty, neutral):
    """A minimal procedural skull glyph used only when the docs/ die art is missing:
    bone dome + jaw, two glowing sockets, and the difficulty number on the brow."""
    bone, bone_d, ink = (232, 226, 210), (176, 168, 150), (28, 24, 30)
    r = px // 2
    pygame.draw.circle(surf, ink, (cx, cy), r + 2)
    pygame.draw.circle(surf, bone, (cx, cy), r)
    pygame.draw.rect(surf, bone, (cx - int(r * 0.5), cy + int(r * 0.55),
                                  int(r), int(r * 0.5)), border_radius=3)
    pygame.draw.rect(surf, ink, (cx - int(r * 0.5), cy + int(r * 0.55),
                                 int(r), int(r * 0.5)), width=2, border_radius=3)
    glow = (120, 200, 220) if (neutral or difficulty is None) else _DIFF_GLOW.get(difficulty, (230, 60, 50))
    er = max(2, int(r * 0.26))
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.42)
        ey = cy - int(r * 0.10)
        pygame.draw.circle(surf, ink, (ex, ey), er + 2)
        pygame.draw.circle(surf, glow, (ex, ey), er)
    if not neutral and difficulty is not None:
        try:
            f = pygame.font.SysFont(None, max(12, int(px * 0.42)), bold=True)
            t = f.render(str(difficulty), True, ink)
            surf.blit(t, t.get_rect(center=(cx, cy - int(r * 0.52))))
        except Exception:
            pass


# ── King-Skull CHARACTER (Asthi-Dakini, latest design SWITCHED + BIG) ──────────
_asthi_mod = None        # render_switchbig module, or False if unavailable
_king_cache = {}         # px -> rendered character Surface (one bake per size)


def _load_asthi():
    """Import the chosen king-skull character design (Asthi-Dakini SWITCHED+BIG)
    once. Returns the render_switchbig module or None if docs/ isn't present.
    Cached. The figure is the same design the stacked-skull pillars derive from."""
    global _asthi_mod
    if _asthi_mod is not None:
        return _asthi_mod or None
    try:
        root = _repo_root()
        _add_paths(os.path.join(root, "docs", "skybit_devil", "batch2", "asthi_ringeye"))
        import render_switchbig as RS
        _asthi_mod = RS
    except Exception:
        _asthi_mod = False
    return _asthi_mod or None


def render_king_skull(px):
    """Return a cached Surface of the full King-Skull character (Asthi-Dakini) exactly
    `px` tall, ready to blit (the demo strolls it through the scene like the clown).
    One bake per size. Returns None if the design module isn't present (caller falls
    back).

    The figure is six-armed and far wider than it is centred: a naive box clips the
    outer arms (the "trimmed rectangle" look). So render at the known-good hero
    framing — where the whole figure provably fits — crop to the TRUE non-transparent
    bounds, then scale so the COMPLETE figure stands `px` tall (width follows its real
    ~0.86 aspect). Nothing is cut off."""
    if px in _king_cache:
        return _king_cache[px]
    RS = _load_asthi()
    if RS is None:
        return None
    try:
        full = RS.render_creature_chip(760, 1024, 380, 540, 3.7, ss=4)
        rect = full.get_bounding_rect()          # tight figure bounds (arms included)
        cropped = full.subsurface(rect).copy()
        w = max(1, round(cropped.get_width() * px / cropped.get_height()))
        chip = pygame.transform.smoothscale(cropped, (w, int(px)))
    except Exception:
        chip = None
    _king_cache[px] = chip
    return chip
