"""Five SMALLER, more forgiving Pagoda Warren drop routes.

The max-aggressive drops (routes4) bottom out at terminal velocity, so arresting
them is nearly frame-perfect — fun only for top-tier players. These relax that:
the plunge is a CONTROLLED fast fall (~70-85px/pagoda — still roughly double the
old timid ramps, so it clearly reads as a sharp drop) inside a wide gap, and the
fairness rule guarantees a CONTINUOUS ≥90px channel (about three bird-heights) the
whole way down. That means a skilled player has real timing slack — they ride the
drop, not thread a needle. No game/ files are touched.

    PYTHONPATH=. python tools/render_warren_routes5.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import H
from tools.render_warren_routes2 import (
    RB, hold_vals, ramp_vals, sine_vals, render_route_strip, _wrap,
    SP, SP_TIGHT, SP_WIDE,
)

GAP_CY_MIN, GAP_CY_MAX = 164, 431
DOWN_DRIFT_MAX = 84      # a skilled controlled fall (< the ~136px free-fall)
UP_DRIFT_MAX = 56        # one flap's climb
CHANNEL_MIN = 90         # continuous channel width ≈ 3 bird-heights → forgiving


def assert_forgiving(name, pagodas):
    """A skilled-but-fair drop guarantee: every consecutive pair of gaps overlaps
    by at least CHANNEL_MIN, so the threadable corridor never narrows below ~3
    bird-heights; descents stay within a controlled fall and climbs within one
    flap."""
    for (xa, ca, ga, _s), (xb, cb, gb, _s2) in zip(pagodas, pagodas[1:]):
        assert GAP_CY_MIN <= cb <= GAP_CY_MAX, f"{name}: cy {cb} OOB"
        assert 150 <= gb <= 185, f"{name}: gap {gb} OOB"
        drift = cb - ca
        if drift >= 0:
            assert drift <= DOWN_DRIFT_MAX, f"{name}: fall {drift} > {DOWN_DRIFT_MAX}"
        else:
            assert -drift <= UP_DRIFT_MAX, f"{name}: climb {-drift} > {UP_DRIFT_MAX}"
        overlap = min(ca + ga / 2, cb + gb / 2) - max(ca - ga / 2, cb - gb / 2)
        assert overlap >= CHANNEL_MIN, \
            f"{name}: channel {overlap:.0f} < {CHANNEL_MIN} between gaps"
    return True


def build_routes():
    R = []

    # 1 — QUICK DIP: a single clean ~155px drop you ride down, then ease back up.
    r = RB("Quick Dip", "One clean dip — ride it down, ease back up")
    r.seg("cruise", hold_vals(205, 4), gap=182, sp=SP_WIDE)
    r.seg("DIP", ramp_vals(205, 360, 2), gap=184, sp=72)
    r.seg("recover", ramp_vals(360, 250, 6), gap=182, sp=SP_WIDE)
    r.seg("settle", hold_vals(250, 2), gap=180, sp=SP)
    R.append(r)

    # 2 — STAIR DIP: two friendly drops with a ledge to breathe between.
    r = RB("Stair Dip", "Two friendly drops with a breather ledge")
    r.seg("rim", hold_vals(196, 3), gap=182, sp=SP_WIDE)
    r.seg("DROP 1", ramp_vals(196, 326, 2), gap=184, sp=72)
    r.seg("ledge", hold_vals(326, 3), gap=178, sp=SP_WIDE)
    r.seg("DROP 2", ramp_vals(326, 424, 2), gap=184, sp=72)
    r.seg("basin", hold_vals(424, 3), gap=178, sp=SP)
    r.seg("climb out", ramp_vals(424, 240, 9), gap=182, sp=SP_WIDE)
    R.append(r)

    # 3 — THE SLIDE: a longer ~235px drop spread over three steps — a smooth,
    # readable slide you can settle into.
    r = RB("The Slide", "A long smooth slide you settle into")
    r.seg("brink", hold_vals(188, 3), gap=182, sp=SP_WIDE)
    r.seg("SLIDE", ramp_vals(188, 424, 3), gap=184, sp=[76, 70, 66])
    r.seg("pool", hold_vals(424, 3), gap=178, sp=SP)
    r.seg("climb out", ramp_vals(424, 235, 9), gap=182, sp=SP_WIDE)
    R.append(r)

    # 4 — DIP & LOW: drop into a low cruise that skims the floor, then climb back.
    r = RB("Dip & Low", "Drop into a low cruise, then climb back")
    r.seg("cruise", hold_vals(214, 3), gap=182, sp=SP_WIDE)
    r.seg("DIP", ramp_vals(214, 398, 3), gap=184, sp=[74, 70, 68])
    r.seg("low cruise", hold_vals(398, 6), gap=180, sp=SP_WIDE)
    r.seg("climb out", ramp_vals(398, 240, 8), gap=182, sp=SP_WIDE)
    R.append(r)

    # 5 — ROLLING DIPS: a descending sawtooth of friendly dips and half-climbs.
    r = RB("Rolling Dips", "A descending sawtooth of friendly dips")
    r.seg("start", hold_vals(220, 2), gap=180, sp=SP_WIDE)
    r.seg("DIP 1", ramp_vals(220, 330, 2), gap=184, sp=72)
    r.seg("rise", ramp_vals(330, 280, 2), gap=182, sp=SP_WIDE)
    r.seg("DIP 2", ramp_vals(280, 392, 2), gap=184, sp=72)
    r.seg("rise", ramp_vals(392, 338, 2), gap=182, sp=SP_WIDE)
    r.seg("DIP 3", ramp_vals(338, 424, 2), gap=184, sp=72)
    r.seg("survive", hold_vals(424, 3), gap=178, sp=SP)
    R.append(r)

    for r in R:
        assert_forgiving(r.name, r.pagodas())
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

    canvas.blit(f_title.render(
        "PAGODA WARREN — 5 SMALLER drops (skilled-but-fair)", True,
        (245, 245, 250)), (PAD, PAD - 2))
    canvas.blit(f_sub.render(
        "controlled fast falls (~70-85px/pagoda) inside a continuous ≥90px "
        "channel  ·  real timing slack, not frame-perfect", True,
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
    out_path = os.path.join(out_dir, "routes_drops_smaller.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})  scale={factor:.3f}")
    for r in routes:
        print(f"  {r.name:14s} {r.n:3d} pagodas  ~{r.duration:4.1f}s")
    print("all smaller-drop routes pass the ≥90px continuous-channel rule")


if __name__ == "__main__":
    main()
