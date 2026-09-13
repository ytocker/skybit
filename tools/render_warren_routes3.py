"""Five extra Pagoda Warren routes, each built around at least one SERIOUS drop —
a steep, committed plunge where the parrot plummets a big chunk of the screen.

Reuses the advanced-route builder (and its physics `assert_passable`) from
`tools/render_warren_routes2.py`, so every drop here is dramatic but still fair:
the corridor dives near the per-step drift ceiling, the pace tightens as you fall,
and the gap stays wide through the plunge so the bird has room to commit. No
game/ files are touched.

    PYTHONPATH=. python tools/render_warren_routes3.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import H, SCROLL_BASE
from tools.render_warren_mockup import assert_passable, DRIFT_MAX
from tools.render_warren_routes2 import (
    RB, hold_vals, ramp_vals, sine_vals, render_route_strip, _wrap,
    START_X, SP, SP_TIGHT, SP_WIDE,
)


def build_routes():
    R = []

    # 1 — THE PLUMMET: a calm perch, then ONE huge committed free-fall spanning
    # almost the whole screen, pace accelerating the whole way down, then a hard
    # pull-up. The signature serious drop.
    r = RB("The Plummet", "One huge committed free-fall, then pull up")
    r.seg("perch", hold_vals(186, 4), gap=180, sp=SP_WIDE)
    r.seg("THE PLUMMET", ramp_vals(186, 422, 6),
          gap=184, sp=[80, 76, 70, 66, 64, 64])      # accelerating fall
    r.seg("hard deck", hold_vals(422, 3), gap=176, sp=SP)
    r.seg("pull up", ramp_vals(422, 300, 5), gap=180, sp=SP_WIDE)
    r.seg("settle", hold_vals(300, 2), gap=178, sp=SP)
    R.append(r)

    # 2 — THE CLIFFS: two serious drops in a row, separated by a thin ledge — a
    # staircase of plunges down to the basin.
    r = RB("The Cliffs", "Two plunges down a thin-ledge staircase")
    r.seg("rim", hold_vals(185, 3), gap=178, sp=SP_WIDE)
    r.seg("DROP 1", ramp_vals(185, 300, 3), gap=182, sp=[76, 68, 64])
    r.seg("thin ledge", hold_vals(300, 2), gap=168, sp=SP)
    r.seg("DROP 2", ramp_vals(300, 425, 3), gap=182, sp=[70, 66, 64])
    r.seg("basin", hold_vals(425, 3), gap=176, sp=SP)
    r.seg("climb out", ramp_vals(425, 210, 7), gap=180, sp=SP_WIDE)
    R.append(r)

    # 3 — THE WATERFALL: the longest single drop — a maximal cascade from the
    # ceiling to the plunge-pool, with a few pinch "rocks" jutting into the falls.
    r = RB("The Waterfall", "A long cascade with rocks in the falls")
    r.seg("brink", hold_vals(178, 3), gap=182, sp=SP_WIDE)
    r.seg("CASCADE", ramp_vals(178, 428, 8),
          gap=[178, 184, 160, 184, 160, 184, 184, 182],   # pinch rocks mid-fall
          sp=[80, 76, 72, 68, 66, 64, 64, 64])
    r.seg("plunge pool", hold_vals(428, 4), gap=176, sp=SP)
    r.seg("climb out", ramp_vals(428, 250, 8), gap=180, sp=SP_WIDE)
    R.append(r)

    # 4 — SKY-DIVE: a high gentle weave, then THE dive straight into a tight,
    # scary low-altitude chop near the floor, then a climb back to safety.
    r = RB("Sky-Dive", "Dive from on high into a tight floor-skim")
    r.seg("high cruise", sine_vals(200, 26, 12, 8), gap=178, sp=SP_WIDE)
    r.seg("THE DIVE", ramp_vals(r.last(), 410, 6),
          gap=184, sp=[78, 74, 70, 66, 64, 64])
    r.seg("FLOOR-SKIM (tight)", sine_vals(400, 22, 5, 10), gap=158, sp=66)
    r.seg("climb out", ramp_vals(r.last(), 230, 7), gap=178, sp=SP_WIDE)
    r.seg("settle", hold_vals(230, 2), gap=178, sp=SP)
    R.append(r)

    # 5 — THE TRAPDOOR: a long, lulling calm cruise with a tiny harmless wobble —
    # then the floor drops out from under you. A surprise serious drop.
    r = RB("The Trapdoor", "A calm lull, then the floor drops out")
    r.seg("calm cruise  (the lull)", hold_vals(230, 8), gap=178, sp=SP_WIDE)
    r.seg("harmless wobble", sine_vals(230, 14, 8, 6), gap=178, sp=SP_WIDE)
    r.seg("TRAPDOOR!", ramp_vals(r.last(), 425, 5),
          gap=184, sp=[76, 70, 66, 64, 64])
    r.seg("scramble", hold_vals(425, 2), gap=174, sp=SP)
    r.seg("climb out", ramp_vals(425, 250, 6), gap=180, sp=SP_WIDE)
    r.seg("settle", hold_vals(250, 2), gap=178, sp=SP)
    R.append(r)

    for r in R:
        pg = r.pagodas()
        assert_passable(r.name, pg)
        for (xa, ca, _g, _s), (xb, cb, _g2, _s2) in zip(pg, pg[1:]):
            assert abs(cb - ca) <= DRIFT_MAX, \
                f"{r.name}: drift {abs(cb-ca)} > {DRIFT_MAX}"
    return R


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    routes = build_routes()

    max_native = max(r.pagodas()[-1][0] + SP + 40 for r in routes)
    CONTENT_W = 2300
    factor = min(0.62, CONTENT_W / max_native)
    row_h = int(H * factor)

    PAD, LEFT, ROW_GAP, TITLE_H, LBL_BAND = 24, 250, 20, 80, 30
    canvas_w = PAD + LEFT + int(max_native * factor) + PAD
    canvas_h = TITLE_H + len(routes) * (row_h + ROW_GAP) + PAD
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((20, 22, 30))

    f_title = pygame.font.SysFont(None, 40, bold=True)
    f_sub = pygame.font.SysFont(None, 24, bold=True)
    f_name = pygame.font.SysFont(None, 30, bold=True)
    f_meta = pygame.font.SysFont(None, 23, bold=True)
    f_lesson = pygame.font.SysFont(None, 21, bold=False)
    f_seg = pygame.font.SysFont(None, 19, bold=True)

    canvas.blit(f_title.render("PAGODA WARREN — 5 routes with a serious drop",
                               True, (245, 245, 250)), (PAD, PAD - 2))
    canvas.blit(f_sub.render(
        "each features at least one committed plunge  ·  wide gap + "
        "accelerating pace through the fall  ·  all physics-passable", True,
        (170, 200, 235)), (PAD, PAD + 36))

    y = TITLE_H
    for r in routes:
        strip, native_w, pg = render_route_strip(r)
        disp_w = int(native_w * factor)
        scaled = pygame.transform.smoothscale(strip, (disp_w, row_h))
        rx = PAD + LEFT
        canvas.blit(scaled, (rx, y))
        pygame.draw.rect(canvas, (64, 72, 92),
                         pygame.Rect(rx - 1, y - 1, disp_w + 2, row_h + 2), 1)

        canvas.blit(f_name.render(r.name, True, (240, 228, 165)), (PAD, y + 8))
        canvas.blit(f_meta.render(f"{r.n} pagodas  ·  ~{r.duration:.0f}s", True,
                                  (180, 210, 175)), (PAD, y + 38))
        for li, line in enumerate(_wrap(r.lesson, 26)):
            canvas.blit(f_lesson.render(line, True, (190, 195, 205)),
                        (PAD, y + 64 + li * 18))

        for si, (i0, i1, label) in enumerate(r.segs):
            xa = rx + int(pg[i0][0] * factor)
            if i0 > 0:
                pygame.draw.line(canvas, (255, 255, 255),
                                 (xa, y + 2), (xa, y + row_h - 2), 1)
            if not label or label.islower():
                continue
            txt = f_seg.render(label, True, (255, 245, 200))
            tx = min(max(xa + 4, rx + 2), rx + disp_w - txt.get_width() - 2)
            ty = y + LBL_BAND + (si % 2) * 20
            shade = pygame.Surface((txt.get_width() + 6, txt.get_height() + 2),
                                   pygame.SRCALPHA)
            shade.fill((0, 0, 0, 120))
            canvas.blit(shade, (tx - 3, ty - 1))
            canvas.blit(txt, (tx, ty))

        y += row_h + ROW_GAP

    out_dir = os.path.join("docs", "pagoda_warren")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "routes_drops.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})  scale={factor:.3f}")
    for r in routes:
        print(f"  {r.name:18s} {r.n:3d} pagodas  ~{r.duration:4.1f}s")
    print("all drop-route passability asserts passed")


if __name__ == "__main__":
    main()
