"""What the Iron Flower (night event N2) actually is, in four real frames.

Dev-only. N2 is not just its 8-second act: the SAME object,
`festival.draw_scaffold`, appears in three states across the day — planted
bare through the afternoon and the storm, manned and bursting for the show,
then cold and scorched at dawn. This sheet renders each so the scope of a
removal can be judged from the pixels rather than from prose.

Two staging problems the tool has to solve, or the panels lie:

  * The rig sits on a 900px block lattice at x0=402 and only ~1 block in 3
    carries it, so most frames contain none. Each panel SCANS a continuous
    scroll for a frame where the drawer actually fires, then re-runs to that
    moment — it never assumes a rig is present.
  * `happening()` latches on the first frame inside its window, so jumping to
    a timestamp renders progress 0 — the crew before anything is thrown. The
    show panel scrolls in, then picks the frame with the most live sparks.

    SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/iron_flower_states.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import random

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y                       # noqa: E402
from game import biome as _biome                             # noqa: E402
from game import foreground                                  # noqa: E402
from game import festival as _fest                           # noqa: E402
from game import foreground_props as fp                      # noqa: E402
from game.sidewalk_crowd import SidewalkCrowd                # noqa: E402
from game.draw import get_sky_surface_biome, draw_mountains  # noqa: E402
from tools._family_showcase import _font                     # noqa: E402
from tools.weekend_filmstrips import _wetness, _snow_cover   # noqa: E402

CYCLE = 393.5
DT = 1.0 / 30.0
CROP_TOP, CROP_H = 400, 240

_hits = []          # (sx,) recorded by whichever drawer we are hunting


def _spy(name):
    real = getattr(_fest, name)

    def wrapped(surf, sx, *a, **k):
        _hits.append((name, sx))
        return real(surf, sx, *a, **k)
    setattr(_fest, name, wrapped)
    return real


_REAL = {n: _spy(n) for n in ("draw_scaffold", "draw_scorch_fan",
                              "draw_fire_show")}


def _paint(surf, t, crowd):
    phase = (t / CYCLE) % 1.0
    scroll = t * 160.0
    pal = _biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal,
                                int(phase * _biome.PHASE_BUCKETS))
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))
    draw_mountains(surf, scroll, GROUND_Y, W, phase=phase)
    foreground.draw_foreground_floor(surf, scroll, pal, phase)
    foreground.draw_ground_weather(surf, scroll, pal, _wetness(t), _snow_cover(t))
    foreground.set_world_signals(clown_active=False, newbie_calm=False,
                                 score=int(t), near_misses=0,
                                 finale_active=False, wetness=_wetness(t),
                                 snow_cover=_snow_cover(t))
    foreground.draw_promenade(surf, scroll, pal, phase, t)
    foreground.draw_near_lane(surf, scroll, pal, phase, t)


def _fresh(seed=0):
    fp._LATCH.clear()
    fp._LATCH_SEEN.clear()
    random.seed(seed)
    foreground.reset_street()
    crowd = SidewalkCrowd()
    foreground.set_crowd(crowd)
    return crowd


def _scan(t0, span, seed, score):
    """Scroll from t0 for `span` seconds; return (best t, best score)."""
    crowd = _fresh(seed)
    scratch = pygame.Surface((W, H))
    t = t0
    best = (-1e9, None)
    for _ in range(int(span / DT)):
        t += DT
        crowd.update(t * 160.0, 160.0, DT, (t / CYCLE) % 1.0, t)
        _hits.clear()
        _paint(scratch, t, crowd)
        s = score(list(_hits), scratch)
        if s > best[0]:
            best = (s, t)
    return best[1], best[0]


def _centred(hits, _surf):
    """Prefer a frame whose rig sits nearest the middle of the screen."""
    if not hits:
        return -1e9
    return -min(abs(sx - W // 2) for _n, sx in hits)


def _residue(hits, _surf):
    """Residue comes in three modes and only the richest (mode 1) carries the
    cold scaffold as well as the scorch fan, so hold out for that one."""
    if not hits:
        return -1e9
    rig = [sx for n, sx in hits if n == 'draw_scaffold']
    if rig:
        return 10000 - min(abs(sx - W // 2) for sx in rig)
    return -min(abs(sx - W // 2) for _n, sx in hits)


def _sparkiest(hits, surf):
    """Prefer the frame with the most hot spark pixels in the street band."""
    if not hits:
        return -1e9
    n = 0
    for y in range(CROP_TOP, min(H, CROP_TOP + CROP_H), 2):
        for x in range(0, W, 2):
            r, g, b = surf.get_at((x, y))[:3]
            if r > 180 and g > 120 and b < 130:
                n += 1
    return n


def _capture(t_target, seed=0):
    crowd = _fresh(seed)
    scratch = pygame.Surface((W, H))
    t = t_target - 9.0
    for _ in range(int(9.0 / DT)):
        t += DT
        crowd.update(t * 160.0, 160.0, DT, (t / CYCLE) % 1.0, t)
        _paint(scratch, t, crowd)
    surf = pygame.Surface((W, H))
    _hits.clear()
    _paint(surf, t, crowd)
    return surf, t, len(_hits)


# (id, title, subtitle, day, phase, scan span, scorer).
# The `day` matters: residue mode is a pure function of the block index, so a
# given night's pattern is fixed and the richest variant (the burnt rig, 1
# block in 8) simply does not occur on day 0. Computed: it lands on days 1
# and 3 of the first six, so panel 4 is staged on night 1 rather than faked.
PANELS = [
    ("1", "THE PLANT", "a bare scaffold goes up mid-afternoon (6 blocks a day)",
     0, 0.505, 26.0, _centred),
    ("2", "IT STANDS IN THE STORM", "the same rig, dark and empty, through the rain",
     0, 0.610, 26.0, _centred),
    ("3", "THE SHOW", "8 s: molten iron thrown at the splash wall",
     0, 0.706, 8.0, _sparkiest),
    ("4", "THE RESIDUE", "at dawn: the burnt rig + scorch fan (~1 night in 3)",
     1, 0.878, 34.0, _residue),
]


def main():
    frames = []
    for pid, title, sub, day, ph, span, score in PANELS:
        t0 = (day + ph) * CYCLE
        # The block layout is reseeded per run, so when a panel wants a rare
        # variant (the residue's mode 1 is 1 block in 8) try a few seeds
        # rather than settle for whatever the first run happened to lay down.
        t_best = seed_best = None
        best_score = -1e18
        for seed in range(8):
            cand, sc = _scan(t0, span, seed, score)
            if cand is not None and sc > best_score:
                t_best, seed_best, best_score = cand, seed, sc
            if best_score >= 1000:        # got the rich variant, stop looking
                break
        if t_best is None:
            raise SystemExit(
                f"panel {pid}: subject never drawn in {span:.0f}s from "
                f"phase {ph:.3f} — widen the scan rather than ship a panel "
                f"that silently shows an empty street")
        frame, t, nhits = _capture(t_best, seed_best)
        drawers = sorted({n for n, _ in _hits})
        print(f"panel {pid} {title:24s} t={t:6.1f}s  phase={(t/CYCLE)%1.0:.3f}  "
              f"seed={seed_best}  drew={drawers}")
        frames.append((pid, title, sub, frame, t, nhits))

    zoom = 1.7
    pw, ph_ = int(W * zoom), int(CROP_H * zoom)
    cols, gap, head, foot = 2, 12, 60, 46
    rows = 2
    sheet = pygame.Surface((cols * pw + (cols + 1) * gap,
                            head + rows * (ph_ + foot + gap) + gap))
    sheet.fill((7, 7, 18))
    sheet.blit(_font(18, bold=True).render(
        "N2 — THE IRON FLOWER, all of it", True, (236, 230, 218)), (gap + 2, 13))
    sheet.blit(_font(11).render(
        "one object in three states across the day; live build, real frames",
        True, (150, 154, 172)), (gap + 3, 38))
    idf, nf, sf = _font(17, bold=True), _font(14, bold=True), _font(11)
    for i, (pid, title, sub, frame, t, nhits) in enumerate(frames):
        crop = frame.subsurface(pygame.Rect(0, CROP_TOP, W, CROP_H))
        big = pygame.transform.scale(crop, (pw, ph_))
        cx = gap + (i % cols) * (pw + gap)
        cy = head + (i // cols) * (ph_ + foot + gap)
        sheet.blit(big, (cx, cy))
        pygame.draw.rect(sheet, (78, 78, 100), (cx, cy, pw, ph_), 1)
        sheet.blit(idf.render(pid, True, (245, 205, 90)), (cx + 4, cy + ph_ + 6))
        sheet.blit(nf.render(title, True, (233, 229, 219)), (cx + 26, cy + ph_ + 7))
        sheet.blit(sf.render(f"{sub}   ·   t={t:.0f}s  φ{(t/CYCLE)%1.0:.3f}",
                             True, (154, 158, 176)), (cx + 4, cy + ph_ + 28))
    out = "docs/sidewalk_overhaul/iron_flower/states.png"
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
