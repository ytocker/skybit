"""The night's main events, one real game frame each, named and numbered.

Dev-only. Renders the live build — no mock-ups — so the sheet is a truthful
index of what actually happens after dark on the street.

Staging matters here. `foreground_weekend.happening()` latches on the FIRST
frame `phase` falls inside a beat's window, so jumping straight to a
timestamp always yields progress 0 — the act at its opening instant, usually
still off-screen. Each panel therefore scrolls in from before the window and
steps forward at 1/30 s to the chosen progress, exactly as a run would, and
asserts the beat is mid-play at the moment of capture.

    SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/night_events.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y                       # noqa: E402
from game import biome as _biome                             # noqa: E402
from game import foreground                                  # noqa: E402
from game import foreground_weekend as _wk                    # noqa: E402
from game.sidewalk_crowd import SidewalkCrowd                # noqa: E402
from game.draw import get_sky_surface_biome, draw_mountains  # noqa: E402
from tools._family_showcase import _font                     # noqa: E402
from tools.weekend_filmstrips import _wetness, _snow_cover   # noqa: E402

CYCLE = 393.5

# (id, title, subtitle, beat-name or None, window start phase, capture time).
# A beat-name panel is staged to mid-performance; a None panel is a standing
# state of the night rather than a timed act, so it is simply rendered at its
# own moment.
EVENTS = [
    ("N1", "Lanterns Up",        "the market floods the dark street",
     None,               0.680, 0.691),
    ("N2", "The Iron Flower",    "molten iron thrown at the splash wall",
     "festival_fire",    0.706, None),
    ("N3", "The Stilt-Walker",   "one tall figure crossing the crowd",
     "festival_stilts",  0.730, None),
    ("N4", "Monkey King's Troupe", "the second crest of the market",
     "festival_troupe",  0.744, None),
    ("N5", "The Lion",           "a shorter, self-contained act",
     "festival_lion",    0.762, None),
    ("N6", "The Dragon",         "the crown — the market pauses for it",
     "festival_dragon",  0.788, None),
    ("N7", "The Dragon Goes Home", "carried off, the afterglow",
     "dragon_home",      0.822, None),
    ("N8", "Snowball Fight",     "small hours, first snow on the ground",
     "snowball",         0.845, None),
    ("N9", "Small Hours",        "near-empty street, braziers warm",
     None,               0.880, 0.892),
]
# how far into a beat to capture it (0..1)
PROGRESS = 0.45
DT = 1.0 / 30.0


def _signals(t):
    foreground.set_world_signals(
        clown_active=False, newbie_calm=False, score=int(t), near_misses=0,
        finale_active=False, wetness=_wetness(t), snow_cover=_snow_cover(t))


def _paint(surf, t, crowd):
    """One full frame in the play scene's order (no pillars — this sheet is
    about the street, and a pillar column would hide the act)."""
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
    _signals(t)
    foreground.draw_promenade(surf, scroll, pal, phase, t)
    foreground.draw_near_lane(surf, scroll, pal, phase, t)
    return phase


def _capture(beat, win_start, fixed_phase):
    """Run the street up to the moment of capture and return (frame, t, live)."""
    foreground.reset_street()
    crowd = SidewalkCrowd()
    foreground.set_crowd(crowd)
    scratch = pygame.Surface((W, H))

    t_enter = win_start * CYCLE
    t_stop = fixed_phase * CYCLE if beat is None else None

    # Settle the living crowd and the slot latches before the beat opens.
    t = (t_stop if t_stop is not None else t_enter) - 12.0
    sc = t * 160.0
    for _ in range(int(12.0 / DT)):
        sc += 160.0 * DT
        t += DT
        crowd.update(sc, 160.0, DT, (t / CYCLE) % 1.0, t)
    for _ in range(2):
        _paint(scratch, t, crowd)

    if beat is None:
        while t < t_stop:
            t += DT
            crowd.update(t * 160.0, 160.0, DT, (t / CYCLE) % 1.0, t)
            _paint(scratch, t, crowd)
        surf = pygame.Surface((W, H))
        _paint(surf, t, crowd)
        return surf, t, True

    # Cross into the window so happening() latches, then step to PROGRESS.
    t0 = None
    for _ in range(int(40.0 / DT)):
        t += DT
        crowd.update(t * 160.0, 160.0, DT, (t / CYCLE) % 1.0, t)
        _paint(scratch, t, crowd)
        if t0 is None and _wk.happening_active(beat):
            t0 = t
        if t0 is not None:
            rec = _wk._h_started.get(beat)
            if rec and (t - rec[0]) >= PROGRESS * _beat_dur(beat):
                break
    surf = pygame.Surface((W, H))
    _paint(surf, t, crowd)
    return surf, t, _wk.happening_active(beat)


_DURS = {"festival_fire": 8.0, "festival_stilts": 6.0, "festival_troupe": 7.0,
         "festival_lion": 6.0, "festival_dragon": 10.5, "dragon_home": 6.0,
         "snowball": 4.5}


def _beat_dur(name):
    return _DURS[name]


def main():
    scale = 0.62
    fw, fh = int(W * scale), int(H * scale)
    cols, rows = 3, 3
    gap, head, foot = 10, 54, 40
    sheet = pygame.Surface((cols * fw + (cols + 1) * gap,
                            head + rows * (fh + foot + gap) + gap))
    sheet.fill((7, 7, 18))
    sheet.blit(_font(17, bold=True).render(
        "THE NIGHT — main events on the street, in order",
        True, (234, 228, 216)), (gap + 2, 12))
    sheet.blit(_font(11).render(
        "live build, one real frame each; timed acts captured mid-performance",
        True, (150, 154, 172)), (gap + 3, 34))
    idf = _font(15, bold=True)
    nf = _font(13, bold=True)
    sf = _font(10)
    ok_all = True
    for i, (eid, title, sub, beat, win, fixed) in enumerate(EVENTS):
        frame, t, live = _capture(beat, win, fixed)
        if not live:
            ok_all = False
        print(f"{eid} {title:24s} t={t:6.1f}s  phase={(t/CYCLE)%1.0:.3f}  "
              f"beat={'-' if beat is None else beat:16s} live={live}")
        cx = gap + (i % cols) * (fw + gap)
        cy = head + (i // cols) * (fh + foot + gap)
        sheet.blit(pygame.transform.smoothscale(frame, (fw, fh)), (cx, cy))
        pygame.draw.rect(sheet, (76, 76, 98), (cx, cy, fw, fh), 1)
        sheet.blit(idf.render(eid, True, (245, 205, 90)), (cx + 3, cy + fh + 5))
        sheet.blit(nf.render(title, True, (232, 228, 218)), (cx + 32, cy + fh + 6))
        sheet.blit(sf.render(f"{sub}   ·   t={t:.0f}s  φ{(t/CYCLE)%1.0:.3f}",
                             True, (154, 158, 176)), (cx + 3, cy + fh + 24))
    out = "docs/sidewalk_overhaul/night_events.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    if not ok_all:
        print("WARNING: at least one beat was NOT live at capture")


if __name__ == "__main__":
    main()
