"""SIDEWALK-OVERHAUL SHOWCASE — 14 catalogue + gameplay images, 2 per family.

For each of the 7 sidewalk-overhaul families this writes TWO PNGs under
docs/sidewalk_overhaul/showcase/ :

  <family>_designs.png   a clean, titled catalogue grid — EVERY variant in the
                         family's shipped pool(s) drawn by the SHIPPED production
                         drawer at DAY on a neutral promenade strip, at true
                         in-game scale, each cell labelled, with an adult +
                         gold-coin yardstick once per sheet.
  <family>_gameplay.png  a real game frame — the shipped engine's biome sky +
                         mountains + ambient + the buff sidewalk floor + the
                         promenade far lane + a couple of pillars + the near
                         lane, with SEVERAL members of THIS family forced into
                         frame among a little ambient life + the gold coin, at a
                         flattering time-of-day. Cropped to a clean landscape band.

  families: pedestrians, day_cast, food_stalls, animals, greenery, props, performers

EVERYTHING is drawn by the SHIPPED drawers / in-scene wrappers — no art is
re-implemented here. The catalogue calls the shipped per-figure drawers
(ped_cast._draw_one, day_cast.draw_kid/elder/vendor, animals_cast.draw_dog/
critter, greenery_cast.draw_greenery, props_cast.draw_lamp/banner/fire/bench/
dressing, performers_cast.draw_act, food_stalls.stall_*). The gameplay frames
build the real background exactly as scenes.PlayScene._draw_background does
(sky/mountains/ambient/floor/promenade) then place the family through their
production in-scene wrappers in foreground_promenade (draw_strollers, draw_kids/
vendor/old_man, draw_food_stall, draw_dog/critter, draw_greenery, draw_prop_*)
or the near-lane performer path — so the placement matches production.

POOL ENUMERATION / SIGNATURE NOTES (vs the brief summary — flagged for the
orchestrator):
  * pedestrians : pool family is 'pedestrian' (singular); one-figure drawer is
    ped_cast._draw_one(surf, cx, base_y, pal, v, night, t)  [takes a `pal` arg,
    unlike the others]; in-scene wrapper is foreground_promenade.draw_strollers
    (one figure per call). 50 variants.
  * day_cast    : pools 'kid'/'elder'/'vendor'; drawers draw_kid/draw_elder/
    draw_vendor(surf, cx, base_y, v, night, t). 6 + 6 + 7 = 19 variants.
  * food_stalls : NOT an fv pool + NOT a `v`-variant drawer. It exposes a
    food_stalls.STALLS dict of 5 named stall fns stall_*(surf, sx, base_y,
    night, t) (steamer/cauldron/grill/wok/tea); in-scene wrapper
    foreground_promenade.draw_food_stall(surf, sx, pal, t=, kind=). 5 stalls.
  * animals     : pools 'dog' (5) + 'critter' (4); drawers draw_dog/draw_critter
    (surf, cx, base_y, v, night, t). There is NO draw_flock in animals_cast — the
    woolly-sheep draw_flock lives in foreground_promenade (a bespoke ambient
    drawer, not part of the animals_cast pool), so it is NOT a catalogue member.
    9 variants (5 dogs + 4 critters).
  * greenery    : pool 'greenery'; draw_greenery(surf, cx, base_y, v, night, t).
    30 variants.
  * props       : 5 pools prop_lamp/prop_banner/prop_fire/prop_bench/prop_dress
    (3 each = 15); drawers draw_lamp/draw_banner/draw_fire/draw_bench/
    draw_dressing(surf, cx, base_y, v, night, t). NOTE: there is NO
    draw_prop_bench in-scene wrapper in foreground_promenade (only lamp/banner/
    fire/dress), so the bench gameplay placement calls the shipped
    props_cast.draw_bench directly. 15 variants.
  * performers  : pool 'performer'; draw_act(surf, sx, base_y, v, night, t). The
    in-scene path is the NEAR lane (foreground_near_lane._pooled_perf), not a
    foreground_promenade wrapper. 8 acts.

Pure-Pygame / pygbag-safe: pygame.draw / Surface / transform.scale (nearest) /
BLEND_RGB_ADD only — the same primitives the shipped engine already uses. No
numpy / gfxdraw / PIL / smoothscale. Headless (SDL_VIDEODRIVER=dummy).

Run from anywhere: python tools/_family_showcase.py
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

# Make `from game import ...` work no matter the cwd.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y  # noqa: E402
from game import biome as _biome  # noqa: E402
from game import foreground_variants as fv  # noqa: E402
from game import foreground_promenade as fp  # noqa: E402
from game import foreground as foreground  # noqa: E402
from game.draw import (  # noqa: E402
    get_sky_surface_biome, draw_mountains, draw_cloud,
)

# Shipped per-figure drawers (catalogue draws these directly at true scale).
from game import ped_cast as _ped  # noqa: E402
from game import day_cast as _day  # noqa: E402
from game import animals_cast as _animals  # noqa: E402
from game import greenery_cast as _green  # noqa: E402
from game import props_cast as _props  # noqa: E402
from game import performers_cast as _perf  # noqa: E402
from game import food_stalls as _food  # noqa: E402


OUT_DIR = os.path.join(_ROOT, "docs", "sidewalk_overhaul", "showcase")


# ════════════════════════════════════════════════════════════════════════════
# Shared helpers — neutral catalogue chrome + yardstick + a real-frame palette.
# ════════════════════════════════════════════════════════════════════════════

# A muted neutral promenade-ground band for the catalogue (NOT the busy review
# chrome): a warm buff strip + a single ground line, in the buff-sidewalk family.
CAT_BG = (206, 196, 178)         # soft sky-neutral above the strip
CAT_DECK = (188, 174, 150)       # the promenade ground band
CAT_DECK_LINE = (150, 136, 112)  # the ground line
CAT_INK = (58, 50, 42)           # label ink
CAT_INK_SOFT = (104, 94, 80)


def _font(sz, bold=False):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _text(surf, s, x, y, sz=11, col=CAT_INK, bold=False):
    surf.blit(_font(sz, bold).render(s, True, col), (x, y))


def _text_center(surf, s, cx, y, sz=10, col=CAT_INK, bold=False):
    img = _font(sz, bold).render(s, True, col)
    surf.blit(img, (cx - img.get_width() // 2, y))


def _gold_coin(surf, cx, cy, r=8):
    """The in-game gold coin yardstick — the sole-brightest reference element."""
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, (255, 232, 150))):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(max(8, r + 1), True).render("$", True, (150, 100, 20)),
              (cx - r // 2, cy - r))


def _adult_ref(surf, cx, base_y):
    """A coarse adult-pedestrian stand-in (PED_H ~18) so every variant reads at a
    true human-relative size. Lifted from the family round generators."""
    coat = (96, 104, 140); coat_dk = (60, 66, 92)
    skin = (222, 178, 132); hair = (52, 42, 34)
    g = int(base_y)
    head_r = 3; torso_h = 9
    torso_top = g - 6 - torso_h
    for sgn in (-1, 1):
        pygame.draw.line(surf, coat_dk, (cx + sgn * 2, torso_top + torso_h), (cx + sgn * 2, g), 2)
    pygame.draw.polygon(surf, coat, [(cx - 3, torso_top), (cx + 3, torso_top),
                                     (cx + 4, torso_top + torso_h), (cx - 4, torso_top + torso_h)])
    pygame.draw.circle(surf, skin, (cx, torso_top - head_r), head_r)
    pygame.draw.circle(surf, hair, (cx, torso_top - head_r - 1), head_r)


# ── catalogue-grid renderer ──────────────────────────────────────────────────

def render_catalogue(out_path, title, subtitle, cells, *, cols, cell_w, cell_h,
                     base_off=16):
    """A tidy titled grid. `cells` is a list of (label, draw_fn) where draw_fn is
    draw(cell_surface, cx, base_y) — the SHIPPED drawer seated on the cell's
    neutral ground strip at true scale. The first row carries an adult + coin
    yardstick cell so scale is unambiguous once per sheet."""
    pad = 14
    head_h = 58
    yard_h = cell_h
    rows = (len(cells) + cols - 1) // cols
    width = pad * 2 + cols * cell_w + (cols - 1) * 8
    height = head_h + yard_h + 10 + rows * (cell_h + 8) + pad

    sheet = pygame.Surface((width, height))
    sheet.fill((232, 226, 214))

    _text(sheet, title, pad, 12, 18, (44, 38, 32), bold=True)
    _text(sheet, subtitle, pad, 36, 11, (108, 98, 84))

    def _cell_strip(w, h):
        c = pygame.Surface((w, h))
        c.fill(CAT_BG)
        base = h - base_off
        pygame.draw.rect(c, CAT_DECK, (0, base, w, h - base))
        pygame.draw.line(c, CAT_DECK_LINE, (0, base), (w, base), 1)
        return c, base

    # Yardstick row (full width): an adult + the gold coin, true scale.
    yard, yb = _cell_strip(width - pad * 2, yard_h)
    _adult_ref(yard, 40, yb)
    _text_center(yard, "adult (~18px)", 40, yb + 3, 9, CAT_INK_SOFT)
    _gold_coin(yard, 120, yb - 14, r=8)
    _text_center(yard, "gold coin", 120, yb + 3, 9, CAT_INK_SOFT)
    _text(yard, "SCALE YARDSTICK — every variant below is drawn by the SHIPPED "
                "drawer at the same true in-game scale.", 170, yb - 14, 10, CAT_INK_SOFT)
    sheet.blit(yard, (pad, head_h))
    pygame.draw.rect(sheet, (170, 158, 138), (pad, head_h, width - pad * 2, yard_h), 1)

    y0 = head_h + yard_h + 10
    for i, (label, draw_fn) in enumerate(cells):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + 8)
        y = y0 + r * (cell_h + 8)
        cell, base = _cell_strip(cell_w, cell_h)
        try:
            draw_fn(cell, cell_w // 2, base)
        except Exception as exc:  # keep the sheet rendering even if one cell fails
            _text(cell, f"ERR {exc}", 4, 4, 8, (170, 60, 50))
        _text_center(cell, label, cell_w // 2, base + 3, 9, CAT_INK)
        sheet.blit(cell, (x, y))
        pygame.draw.rect(sheet, (170, 158, 138), (x, y, cell_w, cell_h), 1)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(sheet, out_path)
    return out_path, sheet.get_size()


# ════════════════════════════════════════════════════════════════════════════
# Real gameplay-frame background — mirrors scenes.PlayScene._draw_background.
# ════════════════════════════════════════════════════════════════════════════

# A handful of cloud slots, matching the live look (scenes._CLOUD_SLOTS shape).
_CLOUD_SLOTS = [(60, 90, 1.0), (210, 60, 0.8), (300, 120, 1.1), (140, 150, 0.7)]


def _build_background(surf, scroll, phase, t):
    """Paint the shipped background into `surf` the way the play scene does:
    biome sky (bucket-blended) + clouds + mountains + ambient floor + promenade
    far lane. `phase` is the biome day-cycle position (sets time-of-day)."""
    palette = _biome.palette_for_phase(phase)

    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    tt = bucket_f - int(bucket_f)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if tt > 0:
        sky_b.set_alpha(int(tt * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)

    for i, (bx, by, sc) in enumerate(_CLOUD_SLOTS):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(0.3 * i) * 3, sc, variant=0, palette=palette)

    draw_mountains(surf, scroll, GROUND_Y, W, phase=phase)

    foreground.draw_foreground_floor(surf, scroll, palette, phase)
    foreground.draw_promenade(surf, scroll, palette, phase, t)
    return palette


def _draw_pillars(surf, palette, phase, columns):
    """A couple of sandstone pillars via the shipped Pipe drawer, so the frame
    reads as real gameplay. `columns` is a list of (x, gap_y, gap_h)."""
    from game.entities import Pipe
    import random as _r
    _r.seed(7)
    for x, gap_y, gap_h in columns:
        p = Pipe(float(x), float(gap_y), float(gap_h))
        p.draw(surf, palette, kfc_visual=False, phase=phase)


def render_gameplay(out_path, title, phase, place_family, *, place_near=None,
                    columns=None, t=2.4, scroll=210.0,
                    crop=(0, 340, W, 300)):
    """Compose a real game frame: background + pillars + the family forced in via
    `place_family(surf, palette)` (the family's production in-scene wrappers) +
    the near lane, then crop to a clean landscape band. `place_near` runs AFTER
    the near lane (for performers, who live in the near deck)."""
    frame = pygame.Surface((W, H))
    palette = _build_background(frame, scroll, phase, t)

    if columns:
        _draw_pillars(frame, palette, phase, columns)

    # Force THIS family into frame deterministically at chosen deck x's, using the
    # production in-scene wrappers (same call shape the day-arc director uses).
    place_family(frame, palette)

    # The near/front lane (matches production: drawn after pillars).
    foreground.draw_near_lane(frame, scroll, palette, phase, t)
    if place_near is not None:
        place_near(frame, palette)

    # A gold coin in the play corridor for scale + brightness reference.
    _gold_coin(frame, int(W * 0.62), int(H * 0.66), r=9)

    cx, cy, cw, ch = crop
    band = frame.subsurface(pygame.Rect(cx, cy, cw, ch)).copy()

    # A slim title bar so each gameplay shot is self-labelling, kept off the play
    # area (the brief wants a clean landscape framing, so the bar is unobtrusive).
    bar = pygame.Surface((cw, 20), pygame.SRCALPHA)
    bar.fill((20, 22, 30, 170))
    out = pygame.Surface((cw, ch + 20))
    out.blit(bar, (0, 0))
    _text(out, title, 8, 4, 11, (236, 230, 216), bold=True)
    out.blit(band, (0, 20))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(out, out_path)
    return out_path, out.get_size()


# ════════════════════════════════════════════════════════════════════════════
# Per-family catalogue cell builders (label, drawer) — true scale, DAY.
# ════════════════════════════════════════════════════════════════════════════

# The promenade wrappers read night-ness off a `pal` dict (sky_top luma). A bright
# day pal makes _nightf -> 0, so the catalogue draws every figure at its DAY look.
_DAY_PAL = _biome.palette_for_phase(0.30)   # afternoon stroll — fully day-lit


def _ped_cells():
    cells = []
    pool = fv.pool("pedestrian")
    for i, v in enumerate(pool):
        arch = v.attrs.get("arch", "?")
        acc = "+".join(sorted(v.accessory)) if v.accessory else ""
        label = f"P{i:02d} {arch}" + (f" · {acc}" if acc else "")
        cells.append((label, lambda c, cx, by, v=v:
                      _ped._draw_one(c, cx, by, _DAY_PAL, v, 0.0, 0.6 + (id(v) % 5) * 0.3)))
    return cells


def _day_cast_cells():
    cells = []
    for fam, drawer, pre in (("kid", _day.draw_kid, "K"),
                             ("elder", _day.draw_elder, "E"),
                             ("vendor", _day.draw_vendor, "V")):
        for i, v in enumerate(fv.pool(fam)):
            kind = (v.attrs.get("arch") or v.attrs.get("stance")
                    or v.attrs.get("pose") or fam)
            label = f"{pre}{i+1} {fam}:{kind}"
            cells.append((label, lambda c, cx, by, drawer=drawer, v=v, i=i:
                          drawer(c, cx, by, v, 0.0, 0.7 + i * 0.5)))
    return cells


def _food_cells():
    cells = []
    for i, (kind, (fn, _pose)) in enumerate(_food.STALLS.items()):
        label = f"S{i+1} {kind}"
        cells.append((label, lambda c, cx, by, fn=fn:
                      fn(c, cx, by, 0.0, 1.1)))
    return cells


def _dog_name(v):
    tail = v.attrs.get("tail", ""); ear = v.attrs.get("ear", "")
    return {"low": "hound", "stub": "dash", "plume": "spitz",
            "tightcurl": "shiba", "lowpup": "long-ear pup"}.get(tail, f"{tail}/{ear}")


def _animals_cells():
    cells = []
    for i, v in enumerate(fv.pool("dog")):
        label = f"D{i+1} dog:{_dog_name(v)}"
        cells.append((label, lambda c, cx, by, v=v, i=i:
                      _animals.draw_dog(c, cx, by, v, 0.0, 0.6 + i * 0.4)))
    for i, v in enumerate(fv.pool("critter")):
        kind = v.attrs.get("kind", "?")
        label = f"C{i+1} critter:{kind}"
        cells.append((label, lambda c, cx, by, v=v, i=i:
                      _animals.draw_critter(c, cx, by, v, 0.0, 0.7 + i * 0.5)))
    return cells


def _greenery_cells():
    cells = []
    for i, v in enumerate(fv.pool("greenery")):
        vessel = v.attrs.get("vessel", "?"); species = v.attrs.get("species", "?")
        label = f"G{i+1} {species}/{vessel}"
        cells.append((label, lambda c, cx, by, v=v, i=i:
                      _green.draw_greenery(c, cx, by, v, 0.0, 0.4 + (i % 4) * 0.5)))
    return cells


def _props_cells():
    cells = []
    fams = (("prop_lamp", _props.draw_lamp, "L"),
            ("prop_banner", _props.draw_banner, "B"),
            ("prop_fire", _props.draw_fire, "F"),
            ("prop_bench", _props.draw_bench, "S"),
            ("prop_dress", _props.draw_dressing, "D"))
    for fam, drawer, pre in fams:
        for i, v in enumerate(fv.pool(fam)):
            style = v.attrs.get("style", "?")
            label = f"{pre}{i+1} {fam.split('_')[1]}:{style}"
            cells.append((label, lambda c, cx, by, drawer=drawer, v=v:
                          drawer(c, cx, by, v, 0.0, 0.9)))
    return cells


def _performers_cells():
    cells = []
    for i, v in enumerate(fv.pool("performer")):
        act = v.attrs.get("act", "?")
        label = f"A{i+1} {act}"
        cells.append((label, lambda c, cx, by, v=v, i=i:
                      _perf.draw_act(c, cx, by, v, 0.0, 0.5 + i * 0.4)))
    return cells


# ════════════════════════════════════════════════════════════════════════════
# Per-family gameplay placements — force several members into the real frame via
# the SHIPPED in-scene wrappers (foreground_promenade.draw_*), plus a little
# ambient life (a few strollers + the family stars).
# ════════════════════════════════════════════════════════════════════════════

def _ambient_strollers(surf, pal, t, xs):
    """A couple of ambient adult pedestrians for street context (production
    wrapper), so the family star reads inside a living scene."""
    n = fv.variant_count("pedestrian")
    for j, x in enumerate(xs):
        fp.draw_strollers(surf, x, pal, t=t + j * 0.7, variant=(7 + j * 11) % n)


def _place_pedestrians(surf, pal):
    t = 2.4
    n = fv.variant_count("pedestrian")
    # A spread of silhouette-distinct walkers across the deck — the family stars.
    picks = [0, 5, 10, 22, 35, 44]   # robe / skirt / tunic / elder / yoke / parasol
    xs = [40, 92, 150, 210, 268, 320]
    for x, idx in zip(xs, picks):
        fp.draw_strollers(surf, x, pal, t=t + x * 0.01, variant=idx % n)


def _place_day_cast(surf, pal):
    t = 2.4
    # Kids running, a temple elder, two market vendors — the daytime cast.
    fp.draw_kids(surf, 56, pal, t=t, n=3, variant=0)
    fp.draw_old_man(surf, 150, pal, t=t, variant=1)
    fp.draw_vendor(surf, 214, pal, t=t, variant=0)
    fp.draw_vendor(surf, 300, pal, t=t, variant=4)
    _ambient_strollers(surf, pal, t, [110, 260])


def _place_food_stalls(surf, pal):
    t = 2.4
    # Three different stalls + their working vendors + foraging critters — the
    # _scene_food composite, hand-placed so several stall TYPES share one frame.
    fp.draw_food_stall(surf, 64, pal, t=t, kind="grill")
    fp.draw_vendor(surf, 58, pal, t=t, variant=2)
    fp.draw_critter(surf, 84, pal, t=t, kind="pigeons")
    fp.draw_food_stall(surf, 196, pal, t=t, kind="steamer")
    fp.draw_vendor(surf, 190, pal, t=t, variant=0)
    fp.draw_food_stall(surf, 312, pal, t=t, kind="tea")
    fp.draw_vendor(surf, 306, pal, t=t, variant=1)
    _ambient_strollers(surf, pal, t, [128, 252])


def _place_animals(surf, pal):
    t = 2.4
    # Several breeds + critters ambling among a couple of pedestrians.
    fp.draw_dog(surf, 60, pal, t=t, variant=0)        # hound
    fp.draw_dog(surf, 150, pal, t=t, variant=2)       # spitz
    fp.draw_dog(surf, 300, pal, t=t, variant=1)       # dash
    fp.draw_critter(surf, 104, pal, t=t, kind="hen")
    fp.draw_critter(surf, 210, pal, t=t, kind="pigeons")
    fp.draw_critter(surf, 256, pal, t=t, kind="duck")
    fp.draw_critter(surf, 330, pal, t=t, kind="cat")
    _ambient_strollers(surf, pal, t, [40, 268])


def _place_greenery(surf, pal):
    # Greenery now plants as static cluster beds directly on the sidewalk rather than
    # lone pots — show a few across the deck, varied by slot key so the frame carries
    # both the 3-pot triad (even k) and the 2-pot pair (odd k) footprints.
    for sx, k in [(70, 0), (200, 3), (322, 2)]:
        fp._draw_greenery_cluster(surf, sx, pal, k)
    _ambient_strollers(surf, pal, 1.0, [130, 264])


def _place_props(surf, pal):
    t = 2.0
    # One of each prop TYPE across the deck (lamp/banner/fire/bench/dressing).
    fp.draw_prop_lamp(surf, 50, pal, t=t, variant=0)
    fp.draw_prop_banner(surf, 120, pal, t=t, variant=1)
    fp.draw_prop_fire(surf, 196, pal, t=t, variant=0)
    # No draw_prop_bench wrapper exists — call the shipped bench drawer directly,
    # seated on GROUND_Y with the live day/night factor (matches the wrappers).
    bench_v = fv.get("prop_bench", 1)
    if bench_v is not None:
        from game.foreground_props import _nightf
        _props.draw_bench(surf, 262, GROUND_Y - 1, bench_v, _nightf(pal), t)
    fp.draw_prop_dress(surf, 326, pal, t=t, variant=0)
    _ambient_strollers(surf, pal, t, [88, 300])


def _place_performers_far(surf, pal):
    # Performers live in the NEAR lane, so the far-lane placement is just a little
    # ambient pedestrian life under the buskers.
    _ambient_strollers(surf, pal, 2.4, [70, 150, 300])


def _place_performers_near(surf, pal):
    """Performers ride the NEAR deck — draw several acts via the shipped draw_act
    at NEAR_GROUND_Y (the production near-lane busker path)."""
    from game.foreground_near_lane import NEAR_GROUND_Y, _nightf
    night = _nightf(pal)
    acts = [0, 6, 2, 7]               # juggler / fan-dancer / stilt / mask-changer
    xs = [58, 150, 244, 326]
    for x, idx in zip(xs, acts):
        v = fv.get("performer", idx)
        if v is not None:
            _perf.draw_act(surf, x, NEAR_GROUND_Y, v, night, 1.4 + x * 0.01)


# ════════════════════════════════════════════════════════════════════════════
# FESTIVAL — the night-marquee special objects (NOT in the day/golden pools):
# the LION DANCE + DRAGON DANCE (red + jade skins) carried high, plus the night
# festival dressing (banner poles + glowing braziers). All live in the NEAR lane
# at NEAR_GROUND_Y and read in the festival NIGHT palette.
# ════════════════════════════════════════════════════════════════════════════

_NIGHT_PAL = _biome.palette_for_phase(0.66)   # festival peak (window 0.58..0.80)


def _festival_cell(draw_fn, *, cap_h, half_w):
    """A render_catalogue-compatible draw(cell, cx, base): the festival act draws at
    the fixed NEAR_GROUND_Y on a full-frame temp, then the band around it is blitted
    into the cell with the act's feet aligned to the cell baseline."""
    from game.foreground_near_lane import NEAR_GROUND_Y

    def _d(cell, cx, base):
        tmp = pygame.Surface((W, H), pygame.SRCALPHA)
        draw_fn(tmp)
        src = pygame.Rect(120 - half_w, NEAR_GROUND_Y - cap_h, half_w * 2, cap_h + 5)
        src = src.clip(tmp.get_rect())
        crop = tmp.subsurface(src).copy()
        cell.blit(crop, (cx - crop.get_width() // 2, base + 5 - crop.get_height()))
    return _d


def _festival_cells():
    from game import foreground_near_lane as fnl
    t = 2.0
    return [
        ("lion dance + drummer",
         _festival_cell(lambda s: fnl.perf_lion_dance(s, 120, _NIGHT_PAL, t),
                        cap_h=58, half_w=62)),
        ("dragon dance (red)",
         _festival_cell(lambda s: fnl.perf_dragon_dance(s, 120, _NIGHT_PAL, t, skin="red"),
                        cap_h=58, half_w=70)),
        ("dragon dance (jade)",
         _festival_cell(lambda s: fnl.perf_dragon_dance(s, 120, _NIGHT_PAL, t, skin="jade"),
                        cap_h=58, half_w=70)),
        ("festival banner pole",
         _festival_cell(lambda s: fnl._near_banner(s, 120, _NIGHT_PAL),
                        cap_h=74, half_w=26)),
        ("glowing brazier",
         _festival_cell(lambda s: fnl._near_brazier(s, 120, _NIGHT_PAL, t=t),
                        cap_h=44, half_w=26)),
    ]


def render_festival_designs(out_path):
    """A dark night-marquee catalogue (the festival objects only read at night)."""
    cells = _festival_cells()
    pad, head_h = 14, 58
    cols, cell_w, cell_h = 5, 150, 124
    width = pad * 2 + cols * cell_w + (cols - 1) * 8
    height = head_h + cell_h + 10 + (cell_h + 8) + pad

    NIGHT_BG, NIGHT_DECK, NIGHT_LINE = (30, 28, 52), (22, 20, 38), (44, 40, 70)
    sheet = pygame.Surface((width, height))
    sheet.fill((20, 18, 34))
    _text(sheet, "SKYBIT PROMENADE — FESTIVAL (night marquee)", pad, 12, 18,
          (238, 230, 216), bold=True)
    _text(sheet, "Night-festival special objects (phase 0.58..0.80) — the LION & "
                 "DRAGON dance + banner/brazier dressing; NEAR lane, NIGHT.",
          pad, 36, 11, (170, 166, 196))

    def _night_strip(w, h):
        c = pygame.Surface((w, h))
        c.fill(NIGHT_BG)
        base = h - 16
        pygame.draw.rect(c, NIGHT_DECK, (0, base, w, h - base))
        pygame.draw.line(c, NIGHT_LINE, (0, base), (w, base), 1)
        return c, base

    yard, yb = _night_strip(width - pad * 2, cell_h)
    _adult_ref(yard, 40, yb)
    _text_center(yard, "adult (~18px)", 40, yb + 3, 9, (170, 166, 196))
    _gold_coin(yard, 120, yb - 14, r=8)
    _text_center(yard, "gold coin", 120, yb + 3, 9, (170, 166, 196))
    _text(yard, "SCALE YARDSTICK — the lion & dragon are carried HIGH (the tallest "
                "near-lane acts); braziers/drum glow stay capped under the coin.",
          170, yb - 14, 10, (170, 166, 196))
    sheet.blit(yard, (pad, head_h))
    pygame.draw.rect(sheet, (60, 56, 88), (pad, head_h, width - pad * 2, cell_h), 1)

    y0 = head_h + cell_h + 10
    for i, (label, draw_fn) in enumerate(cells):
        x = pad + i * (cell_w + 8)
        cell, base = _night_strip(cell_w, cell_h)
        try:
            draw_fn(cell, cell_w // 2, base)
        except Exception as exc:
            _text(cell, f"ERR {exc}", 4, 4, 8, (220, 110, 100))
        _text_center(cell, label, cell_w // 2, base + 3, 9, (224, 218, 232))
        sheet.blit(cell, (x, y0))
        pygame.draw.rect(sheet, (60, 56, 88), (x, y0, cell_w, cell_h), 1)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(sheet, out_path)
    return out_path, sheet.get_size()


def _place_festival_far(surf, pal):
    # A little ambient crowd behind the marquee (the festival draws its own crowd too).
    _ambient_strollers(surf, pal, 2.4, [70, 320])


def _place_festival_near(surf, pal):
    """The night marquee on the near deck: banner + brazier dressing rows, then the
    lion dance and the marquee dragon carried high."""
    from game import foreground_near_lane as fnl
    t = 2.4
    for sx in (28, 196, 344):
        fnl._near_banner(surf, sx, pal)
    for sx in (118, 286):
        fnl._near_brazier(surf, sx, pal, t=t)
    fnl.perf_lion_dance(surf, 92, pal, t)
    fnl.perf_dragon_dance(surf, 252, pal, t, skin="red")


# ════════════════════════════════════════════════════════════════════════════
# Family registry + the 14-image run.
# ════════════════════════════════════════════════════════════════════════════

# (family, designs-title, designs-subtitle, cell builder, grid spec,
#  gameplay-title, biome phase (time-of-day), place_family, place_near)
FAMILIES = [
    ("pedestrians",
     "SKYBIT PROMENADE — PEDESTRIANS",
     "The 50-strong adult walker pool (fv 'pedestrian'), drawn by ped_cast._draw_one at DAY.",
     _ped_cells, dict(cols=10, cell_w=70, cell_h=74),
     "PEDESTRIANS — daytime promenade stroll", 0.30,
     _place_pedestrians, None),

    ("day_cast",
     "SKYBIT PROMENADE — DAY-CAST",
     "Kids (6) + temple elders (6) + market vendors (7) — fv 'kid'/'elder'/'vendor', day_cast drawers, DAY.",
     _day_cast_cells, dict(cols=7, cell_w=92, cell_h=86),
     "DAY-CAST — kids, elder & vendors at the market", 0.20,
     _place_day_cast, None),

    ("food_stalls",
     "SKYBIT PROMENADE — FOOD STALLS",
     "The 5 market stalls (food_stalls.STALLS: steamer/cauldron/grill/wok/tea), DAY.",
     _food_cells, dict(cols=5, cell_w=120, cell_h=110),
     "FOOD STALLS — the morning market rush", 0.10,
     _place_food_stalls, None),

    ("animals",
     "SKYBIT PROMENADE — ANIMALS",
     "5 dog breeds + 4 street critters (fv 'dog'/'critter', animals_cast drawers), DAY.",
     _animals_cells, dict(cols=5, cell_w=100, cell_h=92),
     "ANIMALS — dogs & critters on the street", 0.30,
     _place_animals, None),

    ("greenery",
     "SKYBIT PROMENADE — GREENERY",
     "The 30-design potted-plant pool (fv 'greenery'), drawn by greenery_cast.draw_greenery, DAY.",
     _greenery_cells, dict(cols=10, cell_w=72, cell_h=86),
     "GREENERY — cluster beds line the sidewalk promenade", 0.33,
     _place_greenery, None),

    ("props",
     "SKYBIT PROMENADE — PROPS / STREET FIXTURES",
     "15 fixtures across 5 pools (prop_lamp/banner/fire/bench/dress), props_cast drawers, DAY.",
     _props_cells, dict(cols=5, cell_w=110, cell_h=100),
     "PROPS — lamps, banners, brazier, bench & market clutter", 0.34,
     _place_props, None),

    ("performers",
     "SKYBIT PROMENADE — PERFORMERS",
     "The 8 busker acts (fv 'performer'), drawn by performers_cast.draw_act, DAY.",
     _performers_cells, dict(cols=8, cell_w=92, cell_h=100),
     "PERFORMERS — the golden-hour festival buskers", 0.36,
     _place_performers_far, _place_performers_near),
]


def run():
    results = []
    counts = {}
    for (fam, dtitle, dsub, cell_fn, grid, gtitle, phase,
         place_fam, place_near) in FAMILIES:
        cells = cell_fn()
        counts[fam] = len(cells)

        dpath = os.path.join(OUT_DIR, f"{fam}_designs.png")
        p, sz = render_catalogue(dpath, dtitle, dsub, cells, **grid)
        results.append((p, sz))
        print("saved", p, sz, f"({len(cells)} variants)")

        # A couple of flanking pillars so the frame reads as real gameplay (gap in
        # the play corridor, away from where the family is placed on the deck).
        columns = [(420, 240, 200), (620, 300, 200)]
        gpath = os.path.join(OUT_DIR, f"{fam}_gameplay.png")
        p, sz = render_gameplay(gpath, gtitle, phase, place_fam,
                                place_near=place_near, columns=columns)
        results.append((p, sz))
        print("saved", p, sz)

    # FESTIVAL — the night marquee (special objects outside the day/golden pools).
    fdpath = os.path.join(OUT_DIR, "festival_designs.png")
    p, sz = render_festival_designs(fdpath)
    results.append((p, sz)); counts["festival"] = len(_festival_cells())
    print("saved", p, sz, f"({counts['festival']} objects)")
    fgpath = os.path.join(OUT_DIR, "festival_gameplay.png")
    p, sz = render_gameplay(fgpath, "FESTIVAL — the night lion & dragon dance",
                            0.66, _place_festival_far,
                            place_near=_place_festival_near,
                            columns=[(420, 240, 200), (620, 300, 200)])
    results.append((p, sz))
    print("saved", p, sz)

    print("\n=== SHOWCASE COMPLETE — 16 images ===")
    for p, sz in results:
        print(" ", p, sz)
    print("\n=== per-family variant counts ===")
    for fam, n in counts.items():
        print(f"  {fam:12s} {n}")


if __name__ == "__main__":
    run()
