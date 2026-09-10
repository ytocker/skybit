"""Advanced route design for the "Pagoda Warren" event — round 2 of gameplay.

The first ten routes were single monotone shapes (one plunge, one climb, one
sine...). These ten are built to AMAZE: they use the full lever set the corridor
allows while staying inside the exact same physics passability budget —

  * gap-WIDTH modulation   → pinch-gates that tighten right at the hard moment
  * pace modulation        → spacing legally varies 62-84px, so a route can
                             speed up (tight) into a crunch then breathe (wide)
  * two-frequency stacking → a fast ripple riding a slow swell (constant micro-
                             correction WHILE tracking a big arc)
  * amplitude envelopes    → swings that grow then shrink
  * feints / multi-drops   → the corridor sets an expectation then breaks it

Everything is gated by the round-3 `assert_passable`, so each route is provably
flyable by the real one-button bird. No game/ files are touched.

    PYTHONPATH=. python tools/render_warren_routes2.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import PIPE_W, GROUND_Y, H, SCROLL_BASE
from game.parrot import get_parrot
from game.pillar_pagodas import draw_pillar_pair

from tools.render_warren_mockup import (
    assert_passable, shaped_palette, draw_sky_ground, draw_corridor_glow,
    draw_flight_path, _path_y_at,
    DRIFT_MAX, GAP_CY_MIN, GAP_CY_MAX,
)

START_X = 80
SEED = 0
DAY = 0.05
SP = 72                                   # default spacing
SP_TIGHT, SP_WIDE = 64, 82                # legal pace extremes (inside 62-84)


def clamp_cy(v):
    return max(GAP_CY_MIN, min(GAP_CY_MAX, v))


# ── value generators (sequences of gap-centre y, one per pagoda) ─────────────

def hold_vals(v, n):
    return [v] * n


def ramp_vals(a, b, n):
    return [a + (b - a) * (k + 1) / n for k in range(n)]


def sine_vals(base, amp, wl, n, phase=0.0):
    return [base + amp * math.sin(2 * math.pi * (k / wl) + phase) for k in range(n)]


def comp_vals(base, comps, n):
    """Sum of sine components [(amp, wl, phase), ...] — two-frequency terrain."""
    out = []
    for k in range(n):
        v = base
        for amp, wl, ph in comps:
            v += amp * math.sin(2 * math.pi * (k / wl) + ph)
        out.append(v)
    return out


def env_sine_vals(base, amp_peak, wl, n):
    """Sine whose amplitude swells to a mid-route peak then shrinks (pendulum)."""
    return [base + amp_peak * math.sin(math.pi * k / (n - 1)) *
            math.sin(2 * math.pi * k / wl) for k in range(n)]


def delta_vals(start, deltas):
    """Accumulate signed per-step deltas (hairpins / spikes)."""
    out, cur = [], start
    for d in deltas:
        cur += d
        out.append(cur)
    return out


# ── route builder (per-pagoda gap + spacing) ─────────────────────────────────

class RB:
    def __init__(self, name, lesson):
        self.name = name
        self.lesson = lesson
        self.cy, self.gap, self.sp = [], [], []
        self.segs = []                    # (i0, i1, label)

    def last(self):
        return self.cy[-1] if self.cy else 300

    def seg(self, label, cy_vals, gap=170, sp=SP):
        n = len(cy_vals)
        i0 = len(self.cy)
        self.cy += [clamp_cy(v) for v in cy_vals]
        self.gap += gap if isinstance(gap, list) else [gap] * n
        self.sp += sp if isinstance(sp, list) else [sp] * n
        self.segs.append((i0, i0 + n, label))
        return self

    def pagodas(self):
        out, x = [], START_X
        for k in range(len(self.cy)):
            out.append((x, int(round(self.cy[k])), int(self.gap[k]), SEED))
            x += self.sp[k]
        return out

    @property
    def n(self):
        return len(self.cy)

    def xspan(self):
        return sum(self.sp[:-1]) if self.n > 1 else 0

    @property
    def duration(self):
        return self.xspan() / SCROLL_BASE


# helper: gap that pinches to `tight` at the extremes of a turn pattern, stays
# `wide` mid-transition. `closeness` in [0,1], 1 = at an apex.
def pinch_gap(closeness, wide=180, tight=152):
    return wide - (wide - tight) * closeness


def build_routes():
    R = []

    # 1 — THE SNAKEBITE: a lazy sway lulls you, then a sudden max-amplitude
    # zig-zag strikes. Teaches: don't get complacent; read ahead.
    r = RB("The Snakebite", "Feint then strike — punish complacency")
    r.seg("settle", hold_vals(300, 2), gap=176, sp=SP_WIDE)
    r.seg("lazy sway  (the feint)", sine_vals(300, 60, 16, 16), gap=176, sp=SP_WIDE)
    bite = delta_vals(r.last(), [-52, -52, 54, 54, 54, -54, -54, 54, 50])
    r.seg("SNAKEBITE!", bite, gap=168, sp=SP_TIGHT)
    r.seg("recover", hold_vals(r.last(), 3), gap=176, sp=SP)
    R.append(r)

    # 2 — HEARTBEAT: flat baseline punctuated by sharp spikes, pace tightening on
    # each spike. Teaches: explosive bursts from rest + anticipation/rhythm.
    r = RB("Heartbeat", "Bursts from calm — timing & anticipation")
    r.seg("flatline", hold_vals(300, 6), gap=176, sp=SP_WIDE)
    r.seg("SPIKE", delta_vals(300, [-54, -54, 54, 54]), gap=168, sp=SP_TIGHT)
    r.seg("flatline", hold_vals(300, 5), gap=176, sp=SP_WIDE)
    r.seg("DOUBLE SPIKE",
          delta_vals(300, [-54, -52, 52, -52, 52, 54]), gap=166, sp=SP_TIGHT)
    r.seg("flatline", hold_vals(300, 5), gap=176, sp=SP_WIDE)
    r.seg("FLATLINE!  big spike",
          delta_vals(300, [-56, -54, 0, 54, 56]), gap=168, sp=SP_TIGHT)
    r.seg("settle", hold_vals(300, 3), gap=176, sp=SP)
    R.append(r)

    # 3 — THE GAUNTLET: alternating high/low gates whose channel PINCHES right at
    # each turn apex, at a fast pace. Teaches: precision exactly when turning.
    r = RB("The Gauntlet", "Precision pinch-gates at every turn")
    cy, gap = [], []
    apex = [222, 378, 222, 378, 222, 378, 222]
    cur = 300
    for a in apex:
        leg = ramp_vals(cur, a, 3)
        cy += leg
        gap += [178, 170, pinch_gap(1.0)]      # tightest at the apex (3rd)
        cur = a
    r.seg("PINCH-GATE GAUNTLET", cy, gap=gap, sp=66)
    r.seg("exit", hold_vals(cur, 3), gap=178, sp=SP)
    R.append(r)

    # 4 — CRESCENDO: a gentle sway swells in amplitude AND frequency into a
    # frantic chop, then ONE big release plunge to a wide breather. Tension→payoff.
    r = RB("Crescendo", "Build to chaos, then a big release")
    r.seg("gentle sway", sine_vals(280, 38, 16, 10), gap=176)
    build = []
    theta = 0.0
    for k in range(20):
        f = k / 19
        amp = 38 + 12 * f                  # peak ~50
        wl = 15 - 8 * f                    # min ~7 → max step ~46 < budget
        theta += 2 * math.pi / wl
        build.append(290 + amp * math.sin(theta))
    r.seg("BUILDING  →  FRANTIC", build, gap=168, sp=list(
        [int(SP - (SP - SP_TIGHT) * (k / 19)) for k in range(20)]))
    r.seg("RELEASE — big plunge", ramp_vals(r.last(), 410, 8), gap=184, sp=SP_WIDE)
    r.seg("breathe", hold_vals(410, 3), gap=184, sp=SP_WIDE)
    R.append(r)

    # 5 — THE WASHBOARD: a fast ripple riding a slow swell. Two frequencies at
    # once — constant micro-correction WHILE tracking the macro arc. Demanding.
    r = RB("The Washboard", "Two rhythms at once — ripple on a swell")
    r.seg("enter", hold_vals(300, 2), gap=174)
    r.seg("RIPPLE ON A SWELL",
          comp_vals(300, [(92, 22, 0.0), (17, 5, 0.0)], 40), gap=170)
    r.seg("exit", hold_vals(r.last(), 2), gap=174)
    R.append(r)

    # 6 — STUTTER-STEP: a syncopated PACE — two quick hops then a held beat,
    # repeating. The rhythm itself stutters (spacing carries the groove).
    r = RB("Stutter-Step", "Syncopated pace — quick-quick-hold")
    cy, sp = [], []
    cur = 300
    up = True
    for beat in range(10):
        for j in range(3):
            if j < 2:                          # two quick small hops
                cur += (-38 if up else 38)
                sp.append(SP_TIGHT)
            else:                              # held beat (wide breather)
                sp.append(SP_WIDE)
            cy.append(cur)
        up = not up
    r.seg("QUICK-QUICK-HOLD  (x10)", cy, gap=170, sp=sp)
    r.seg("end", hold_vals(cur, 2), gap=174, sp=SP)
    R.append(r)

    # 7 — THE PENDULUM: swings that GROW to a mid peak then shrink, while the gap
    # BREATHES — wide at centre crossings, pinched at the extremes. It feels alive.
    r = RB("The Pendulum", "Growing/shrinking swings; the gap breathes")
    n = 40
    cy = env_sine_vals(300, 96, 12, n)
    gap = []
    for k in range(n):
        ext = abs(math.sin(2 * math.pi * k / 12))   # 1 at the swing extremes
        gap.append(pinch_gap(ext, wide=184, tight=156))
    r.seg("BREATHING PENDULUM", cy, gap=gap, sp=SP)
    r.seg("rest", hold_vals(r.last(), 2), gap=180, sp=SP)
    R.append(r)

    # 8 — FREE-FALL EXPRESS: an elevator drop — steep dives with the pace
    # tightening as you fall, brief ledges, and pinch-gates mid-plunge. Adrenaline.
    r = RB("Free-Fall Express", "Adrenaline elevator — dive, ledge, dive")
    r.seg("perch", hold_vals(196, 3), gap=180, sp=SP_WIDE)
    r.seg("DIVE", ramp_vals(196, 360, 5),
          gap=[176, 170, 156, 170, 176], sp=[78, 74, 70, 66, 64])
    r.seg("ledge", hold_vals(360, 2), gap=180, sp=SP_WIDE)
    r.seg("DIVE AGAIN", ramp_vals(360, 412, 4),
          gap=[172, 156, 156, 176], sp=[70, 66, 64, 64])
    r.seg("pull up", ramp_vals(412, 300, 5), gap=180, sp=SP_WIDE)
    r.seg("settle", hold_vals(300, 3), gap=180, sp=SP)
    R.append(r)

    # 9 — SWITCHBACK LADDER: a relentless net CLIMB done as zig-zag rungs (up
    # hard, half-step down, up hard...) at a tight pace. Sustained precise climbing.
    r = RB("Switchback Ladder", "Relentless zig-zag climb — precise rungs")
    cy = []
    cur = 412
    for rung in range(9):
        cur -= 50                              # up a rung
        cy.append(cur)
        cur += 22                              # half-step down (the switchback)
        cy.append(cur)
        cur -= 4
        cy.append(cur)
    r.seg("LADDER CLIMB", cy, gap=168, sp=66)
    r.seg("top", hold_vals(cur, 3), gap=176, sp=SP)
    R.append(r)

    # 10 — THE LABYRINTH (FINALE): a medley of the above — feint, snakebite,
    # washboard, pinch-gauntlet, free-fall, crescendo-release. The showpiece.
    r = RB("The Labyrinth", "The finale — every trick, back to back")
    r.seg("enter", hold_vals(300, 2), gap=174, sp=SP)
    r.seg("feint sway", sine_vals(300, 50, 14, 10), gap=174, sp=SP_WIDE)
    r.seg("recentre", ramp_vals(r.last(), 300, 2), gap=172, sp=SP)
    r.seg("snakebite", delta_vals(300, [-50, 50, -50, 50, -50, 50]),
          gap=168, sp=SP_TIGHT)
    r.seg("washboard", comp_vals(r.last(), [(70, 18, 0.0), (16, 5, 0.0)], 14),
          gap=170)
    r.seg("recentre", ramp_vals(r.last(), 300, 2), gap=172, sp=SP)
    # pinch gauntlet (two gates)
    cy, gap = [], []
    cur = 300
    for a in (224, 376, 224):
        cy += ramp_vals(cur, a, 3)
        gap += [176, 168, pinch_gap(1.0)]
        cur = a
    r.seg("pinch gauntlet", cy, gap=gap, sp=66)
    r.seg("climb to perch", ramp_vals(cur, 196, 3), gap=176, sp=SP)
    r.seg("free-fall", ramp_vals(196, 410, 6),
          gap=[174, 158, 174, 158, 174, 182], sp=[74, 70, 66, 64, 64, 66])
    r.seg("crescendo release", ramp_vals(410, 250, 7), gap=182, sp=SP_WIDE)
    r.seg("survive", hold_vals(250, 4), gap=180, sp=SP)
    R.append(r)

    # Final gate: physics-passable + bounded drift on every route.
    for r in R:
        pg = r.pagodas()
        assert_passable(r.name, pg)
        for (xa, ca, _g, _s), (xb, cb, _g2, _s2) in zip(pg, pg[1:]):
            assert abs(cb - ca) <= DRIFT_MAX, \
                f"{r.name}: drift {abs(cb-ca)} > {DRIFT_MAX}"
    return R


# ── render one route as a long native strip ──────────────────────────────────

def render_route_strip(route):
    pg = route.pagodas()
    native_w = pg[-1][0] + SP + 40
    palette = shaped_palette(DAY, dense=False)
    surf = pygame.Surface((native_w, H))
    draw_sky_ground(surf, native_w, H, palette)

    for idx, (x, cy, gap_h, seed) in enumerate(pg):
        top_h = cy - gap_h / 2
        bot_y = cy + gap_h / 2
        top_rect = pygame.Rect(int(x - PIPE_W / 2), 0, PIPE_W, int(top_h))
        bot_rect = pygame.Rect(int(x - PIPE_W / 2), int(bot_y),
                               PIPE_W, int(GROUND_Y - bot_y))
        draw_pillar_pair(surf, top_rect, bot_rect, palette, seed,
                         phase=DAY, is_rush=False, pillar_index=idx + 1)

    draw_corridor_glow(surf, pg, DAY, dense=False)
    draw_flight_path(surf, pg)

    bx = pg[min(2, len(pg) - 1)][0]
    by = _path_y_at(pg, bx)
    nxt = _path_y_at(pg, bx + 24)
    bird = get_parrot(1, -12 if nxt > by else 12)
    surf.blit(bird, (int(bx - bird.get_width() / 2),
                     int(by - bird.get_height() / 2)))
    return surf, native_w, pg


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    routes = build_routes()

    max_native = max(r.pagodas()[-1][0] + SP + 40 for r in routes)
    CONTENT_W = 2300
    factor = min(0.62, CONTENT_W / max_native)
    row_h = int(H * factor)

    PAD = 24
    LEFT = 250
    ROW_GAP = 20
    TITLE_H = 80
    LBL_BAND = 30

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

    canvas.blit(f_title.render("PAGODA WARREN — 10 advanced routes", True,
                               (245, 245, 250)), (PAD, PAD - 2))
    canvas.blit(f_sub.render(
        "gap-pinch · pace shifts · two-frequency · feints  —  all "
        "physics-passable  ·  ~0.40-0.52s / pagoda", True,
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
    out_path = os.path.join(out_dir, "routes_advanced.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})  scale={factor:.3f}")
    for r in routes:
        print(f"  {r.name:20s} {r.n:3d} pagodas  ~{r.duration:4.1f}s")
    print("all advanced route passability asserts passed")


def _wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    main()
