"""Route design for the "Pagoda Warren" event — gameplay, not graphics.

The graphics direction (fused-masonry corridor) is settled. This script is a
DESIGN consultation: it lays out 10 distinct, LONG warren routes — each built to
teach a specific one-button maneuver — and renders them as one figure where every
row is the whole route drawn at a uniform pixels-per-pagoda scale, so route
lengths are directly comparable ("how long should a warren be?").

It reuses the round-3 look-dev renderer wholesale (the real pagoda art, the carved
corridor glow, the parabolic flight path, the parrot, and — crucially — the
physics `assert_passable` budget) so every route here is provably flyable by the
real bird. No game/ files are touched; we only call existing draw entry points and
pass locally-tinted copies of the biome palette.

    PYTHONPATH=. python tools/render_warren_routes.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import PIPE_W, GROUND_Y, H, SCROLL_BASE
from game.parrot import get_parrot
from game.pillar_pagodas import draw_pillar_pair

# Reuse the round-3 corridor renderer + the physics passability budget verbatim.
from tools.render_warren_mockup import (
    assert_passable, shaped_palette, draw_sky_ground, draw_corridor_glow,
    draw_flight_path, _path_y_at, _channel_polys,
    DRIFT_MAX, GAP_CY_MIN, GAP_CY_MAX, GAP_H_MIN, GAP_H_MAX,
)

# ── route geometry constants ─────────────────────────────────────────────────
SP = 72                 # centre-to-centre spacing (inside the fused 62-84 window)
START_X = 80            # first pagoda x
SEED = 0                # ONE pagoda variant for every route (stupa_canopy family)
DAY = 0.05              # render everything at DAY for max gameplay clarity
SECONDS_PER_PAGODA = SP / SCROLL_BASE      # ~0.45 s


class Route:
    """Builds a route as a list of pagodas (x, gap_cy, gap_h, seed) plus labeled
    maneuver segments. Every primitive keeps the per-step drift inside the
    physics budget; `assert_passable` is the final gate."""

    def __init__(self, name, lesson):
        self.name = name
        self.lesson = lesson
        self.pagodas = []
        self.segments = []          # (i_start, i_end, label)
        self.cy = None

    def _step(self, n):
        return range(n)

    def _push(self, cy, gap):
        cy = max(GAP_CY_MIN, min(GAP_CY_MAX, cy))
        x = START_X + len(self.pagodas) * SP
        self.pagodas.append((x, int(round(cy)), int(gap), SEED))
        self.cy = cy

    def _seg(self, label, fn):
        i0 = len(self.pagodas)
        fn()
        self.segments.append((i0, len(self.pagodas), label))
        return self

    def hold(self, label, n, cy, gap):
        def fn():
            for _ in self._step(n):
                self._push(cy, gap)
        return self._seg(label, fn)

    def ramp(self, label, target, n, gap):
        """Linear glide of the gap centre from the current cy to target over n
        pagodas. Used for plunges (down) and climbs (up)."""
        start = self.cy if self.cy is not None else target
        def fn():
            for i in self._step(n):
                cy = start + (target - start) * (i + 1) / n
                self._push(cy, gap)
        return self._seg(label, fn)

    def sine(self, label, amp, wl, n, gap, base=None):
        """n pagodas of a sine wave (wavelength wl pagodas). base defaults to the
        current cy so the wave joins smoothly."""
        b = base if base is not None else (self.cy if self.cy is not None else 300)
        def fn():
            for i in self._step(n):
                cy = b + math.sin((i / wl) * 2 * math.pi) * amp
                self._push(cy, gap)
        return self._seg(label, fn)

    def accel(self, label, n, base, amp0, amp1, wl0, wl1, gap):
        """A sine whose wavelength shrinks and amplitude eases across n pagodas —
        a difficulty ramp. Phase is integrated so steps stay bounded."""
        def fn():
            theta = 0.0
            for i in self._step(n):
                f = i / max(1, n - 1)
                amp = amp0 + (amp1 - amp0) * f
                wl = wl0 + (wl1 - wl0) * f
                theta += 2 * math.pi / wl
                self._push(base + math.sin(theta) * amp, gap)
        return self._seg(label, fn)

    def squeeze(self, label, n, cy, gap_wide, gap_tight):
        """Near-flat line whose gap height pinches to gap_tight at the midpoint
        then re-opens — a precision section. A tiny wander keeps it alive."""
        mid = (n - 1) / 2
        def fn():
            for i in self._step(n):
                t = 1 - abs(i - mid) / mid           # 0 at ends, 1 at centre
                gap = gap_wide - (gap_wide - gap_tight) * t
                wob = math.sin(i * 0.5) * 10
                self._push(cy + wob, gap)
        return self._seg(label, fn)

    @property
    def n(self):
        return len(self.pagodas)

    @property
    def duration(self):
        return self.n * SECONDS_PER_PAGODA


def build_routes():
    routes = []

    # 1 — THE LONG PLUNGE: the showcase "long dip". Mostly fall, tap only to keep
    # off the floor. Gentle ~10 px/pagoda descent ≪ terminal fall.
    routes.append(
        Route("The Long Plunge", "Controlled falling — tap only to brake")
        .hold("ease in", 3, 188, 180)
        .ramp("LONG GLIDE-DOWN — just fall", 408, 22, 180)
        .hold("level out", 4, 408, 180))

    # 2 — THE ASCENT: sustained rhythmic climb, ~1 flap/pagoda.
    routes.append(
        Route("The Ascent", "Steady climb cadence — tap, tap, tap")
        .hold("ease in", 3, 412, 178)
        .ramp("STEADY CLIMB", 190, 24, 178)
        .hold("crest", 3, 190, 178))

    # 3 — ROLLING HILLS: smooth alternation; flap on the up, ease on the down.
    routes.append(
        Route("Rolling Hills", "Smooth alternation — flap up, ease down")
        .hold("enter", 2, 300, 176)
        .sine("S-WEAVE  (x3)", 100, 12, 36, 176, base=300)
        .hold("exit", 2, 300, 176))

    # 4 — THE VALLEY: long fall into a basin, then long climb out.
    routes.append(
        Route("The Valley", "Falling → climbing transition")
        .hold("rim", 2, 198, 178)
        .ramp("PLUNGE IN", 410, 15, 178)
        .hold("basin", 3, 410, 178)
        .ramp("CLIMB OUT", 198, 15, 178)
        .hold("rim", 2, 198, 178))

    # 5 — THE CREST: long climb to a summit, then a long plunge — apex control.
    routes.append(
        Route("The Crest", "Apex management — don't overshoot the top")
        .hold("base", 2, 412, 178)
        .ramp("ASCENT", 188, 15, 178)
        .hold("summit", 3, 188, 178)
        .ramp("PLUNGE DOWN", 412, 15, 178)
        .hold("base", 2, 412, 178))

    # 6 — THE CHOP: rapid tight waves; fine rhythmic micro-control.
    routes.append(
        Route("The Chop", "Fine rhythmic micro-control")
        .hold("enter", 2, 300, 170)
        .sine("RAPID CHOP", 45, 6, 38, 170, base=300)
        .hold("exit", 2, 300, 170))

    # 7 — ACCELERANDO: gentle → frantic; the difficulty ramp.
    routes.append(
        Route("Accelerando", "Escalating adaptation — it speeds up on you")
        .hold("calm", 4, 300, 172)
        .accel("BUILDING  →  FRANTIC", 40, 300, 70, 46, 14.0, 6.0, 172)
        .hold("breathe", 3, 300, 172))

    # 8 — THE LEDGE: a long calm lull, then a sudden steep drop — reaction.
    routes.append(
        Route("The Ledge", "React to a sudden drop after the calm")
        .hold("CALM CRUISE — high lane", 11, 206, 178)
        .ramp("SUDDEN DROP!", 396, 5, 180)
        .hold("low lane", 9, 396, 178)
        .ramp("recover", 232, 6, 178)
        .hold("settle", 3, 232, 178))

    # 9 — THE TIGHTROPE: near-flat, but the gap pinches to its tightest mid-route.
    routes.append(
        Route("The Tightrope", "Precision line-holding through the pinch")
        .hold("wide", 3, 300, 184)
        .squeeze("SQUEEZE — tightest channel", 30, 300, 184, 152)
        .hold("wide", 3, 300, 184))

    # 10 — THE FINAL EXAM: the graduation medley, the longest route.
    routes.append(
        Route("The Final Exam", "Graduation — everything at once")
        .hold("start", 2, 196, 172)
        .ramp("PLUNGE", 392, 8, 172)
        .sine("CHOP", 40, 6, 12, 172, base=360)
        .ramp("CLIMB", 190, 9, 172)
        .hold("summit", 2, 190, 172)
        .ramp("DIVE", 388, 8, 172)
        .ramp("recover", 250, 6, 172)
        .hold("runout", 4, 250, 172))

    # Final gate: every route must be physics-passable, and stay in bounds.
    for r in routes:
        assert_passable(r.name, r.pagodas)
        # Extra guard: report any per-step drift that sneaks over budget.
        for (xa, ca, _ga, _s), (xb, cb, _gb, _s2) in zip(r.pagodas, r.pagodas[1:]):
            assert abs(cb - ca) <= DRIFT_MAX, \
                f"{r.name}: drift {abs(cb-ca)} > {DRIFT_MAX}"
    return routes


# ── render one full route as a long native-resolution strip ──────────────────

def render_route_strip(route):
    native_w = START_X + route.n * SP + 40
    palette = shaped_palette(DAY, dense=False)
    surf = pygame.Surface((native_w, H))
    draw_sky_ground(surf, native_w, H, palette)

    for idx, (x, cy, gap_h, seed) in enumerate(route.pagodas):
        top_h = cy - gap_h / 2
        bot_y = cy + gap_h / 2
        top_rect = pygame.Rect(int(x - PIPE_W / 2), 0, PIPE_W, int(top_h))
        bot_rect = pygame.Rect(int(x - PIPE_W / 2), int(bot_y),
                               PIPE_W, int(GROUND_Y - bot_y))
        draw_pillar_pair(surf, top_rect, bot_rect, palette, seed,
                         phase=DAY, is_rush=False, pillar_index=idx + 1)

    draw_corridor_glow(surf, route.pagodas, DAY, dense=False)
    draw_flight_path(surf, route.pagodas)

    # Parrot threading an early gap so each row opens with the bird on the line.
    bx = route.pagodas[min(3, route.n - 1)][0]
    by = _path_y_at(route.pagodas, bx)
    nxt = _path_y_at(route.pagodas, bx + 24)
    bird = get_parrot(1, -12 if nxt > by else 12)
    surf.blit(bird, (int(bx - bird.get_width() / 2),
                     int(by - bird.get_height() / 2)))
    return surf, native_w


# ── assemble the figure: 10 rows at one uniform scale ────────────────────────

def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((360, 640))

    routes = build_routes()

    # Uniform pixels-per-pagoda: scale every row by the SAME factor, set by the
    # longest route, so row length on the page == real route length.
    max_native = max(START_X + r.n * SP + 40 for r in routes)
    CONTENT_W = 2300                      # target on-page width of the longest row
    factor = min(0.62, CONTENT_W / max_native)
    row_h = int(H * factor)

    PAD = 24
    LEFT = 250                            # gutter for route name + lesson
    ROW_GAP = 20
    TITLE_H = 80
    LBL_BAND = 30                         # maneuver labels sit just under the row top

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

    canvas.blit(f_title.render("PAGODA WARREN — 10 route designs", True,
                               (245, 245, 250)), (PAD, PAD - 2))
    canvas.blit(f_sub.render(
        "each row = one full route at uniform scale  ·  ~0.45s / pagoda  ·  "
        "all physics-passable", True, (170, 200, 235)), (PAD, PAD + 36))

    y = TITLE_H
    for r in routes:
        strip, native_w = render_route_strip(r)
        disp_w = int(native_w * factor)
        scaled = pygame.transform.smoothscale(strip, (disp_w, row_h))
        rx = PAD + LEFT
        canvas.blit(scaled, (rx, y))
        pygame.draw.rect(canvas, (64, 72, 92),
                         pygame.Rect(rx - 1, y - 1, disp_w + 2, row_h + 2), 1)

        # Left gutter: name, length/duration, lesson.
        canvas.blit(f_name.render(r.name, True, (240, 228, 165)), (PAD, y + 8))
        canvas.blit(f_meta.render(f"{r.n} pagodas  ·  ~{r.duration:.0f}s", True,
                                  (180, 210, 175)), (PAD, y + 38))
        for li, line in enumerate(_wrap(r.lesson, 26)):
            canvas.blit(f_lesson.render(line, True, (190, 195, 205)),
                        (PAD, y + 64 + li * 18))

        # Maneuver segment labels + faint boundary ticks along the row.
        for si, (i0, i1, label) in enumerate(r.segments):
            xa = rx + int((START_X + i0 * SP) * factor)
            xb = rx + int((START_X + (i1 - 1) * SP) * factor)
            if i0 > 0:                       # boundary tick
                pygame.draw.line(canvas, (255, 255, 255, 60),
                                 (xa, y + 2), (xa, y + row_h - 2), 1)
            if not label or label.islower():
                continue                     # skip tiny "ease in"-type joins
            txt = f_seg.render(label, True, (255, 245, 200))
            tx = min(max(xa + 4, rx + 2),
                     rx + disp_w - txt.get_width() - 2)
            ty = y + LBL_BAND + (si % 2) * 20    # stagger to reduce overlap
            shade = pygame.Surface((txt.get_width() + 6, txt.get_height() + 2),
                                   pygame.SRCALPHA)
            shade.fill((0, 0, 0, 110))
            canvas.blit(shade, (tx - 3, ty - 1))
            canvas.blit(txt, (tx, ty))

        y += row_h + ROW_GAP

    out_dir = os.path.join("docs", "pagoda_warren")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "routes.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})  scale={factor:.3f}")
    for r in routes:
        print(f"  {r.name:22s} {r.n:3d} pagodas  ~{r.duration:4.1f}s")
    print("all route passability asserts passed")


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
