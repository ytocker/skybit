"""Five Pagoda Warren routes built around an AGGRESSIVE drop.

The parrot free-falls ~136px in a single pagoda-time (gravity 1600 → terminal
700px/s) — sharper than any gentle ramp. The honest way to author a drop the
player can actually fly is the way a player flies one: TAP ONCE to commit at the
lip, then RIDE the gravity arc straight down. So each drop's gap centres ARE that
post-tap trajectory (a small wind-up, then a hard plunge to the deck). Because the
commit-tap pins the entry velocity, the corridor and the flown path match exactly.

Validated by a canonical-input trajectory sim on the REAL physics: it taps once at
each marked lip, glides the plunge, and floor-avoids everywhere else, confirming
every pagoda gap is cleared with margin. No game/ files are touched.

    PYTHONPATH=. python tools/render_warren_routes4.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import (
    H, SCROLL_BASE, GRAVITY, FLAP_V, MAX_FALL, BIRD_R, PIPE_HITBOX_SHRINK,
)
from tools.render_warren_routes2 import (
    RB, hold_vals, ramp_vals, sine_vals, render_route_strip, _wrap,
    SP, SP_TIGHT, SP_WIDE,
)

EFFECTIVE_R = BIRD_R - PIPE_HITBOX_SHRINK     # 10 px forgiven hitbox
DT = 1.0 / 60.0
GAP_CY_MIN, GAP_CY_MAX = 164, 431


def _advance(y, vy, T, flap=False):
    """Integrate flight for T seconds (optionally flapping at the start)."""
    if flap:
        vy = FLAP_V
    sub = max(1, int(round(T / (1.0 / 240))))
    ddt = T / sub
    for _ in range(sub):
        vy = min(vy + GRAVITY * ddt, MAX_FALL)
        y += vy * ddt
    return y, vy


# ── the commit-tap dive: gap centres follow the real post-tap gravity arc ─────

def flap_dive(lip_cy, sp, bottom):
    """Sample the parrot's trajectory after ONE commit-tap at the lip: it winds
    up slightly, arcs over, then plunges hard. Sampling at each pagoda plane
    gives the drop's gap centres, so a player who taps once and releases rides
    it exactly. The dive ENDS at `bottom` (held above the screen floor so the
    following deck has room to arrest the ~terminal-speed fall)."""
    dt_p = sp / SCROLL_BASE
    y, vy = float(lip_cy), FLAP_V
    out = []
    for _ in range(9):
        y, vy = _advance(y, vy, dt_p)
        if y >= bottom:
            break                # stop BEFORE the unreachable bottom; the
                                 # following climb-out arrests the fast fall
        out.append(y)
    return out


def climb_to(start_cy, target_cy, sp):
    """Gap centres for the climb-OUT, following the bird's real flap arc: the
    player taps every pagoda, each tap netting an upward step, until reaching the
    target altitude. Modelling the recovery as the actual flap arc (not a straight
    ramp) keeps the flapped-out bird in the centre of the channel — that's what
    gives the drop a fair recovery margin instead of a frame-perfect one."""
    dt_p = sp / SCROLL_BASE
    y = float(start_cy)
    out = []
    for _ in range(12):
        y, _vy = _advance(y, FLAP_V, dt_p)     # one commit-flap per pagoda
        out.append(max(y, GAP_CY_MIN))
        if y <= target_cy:
            break
    return out


# ── canonical-input trajectory sim (the passability proof) ───────────────────

def simulate(pagodas, dives):
    """Fly the canonical input: tap once at each dive lip, glide the plunge,
    floor-avoid elsewhere. Returns (ok, min_margin, info)."""
    xs = [p[0] for p in pagodas]
    cys = [p[1] for p in pagodas]
    gaps = [p[2] for p in pagodas]
    SAFE = 2.0
    entries = {e for (e, _end) in dives}

    def in_dive(i):
        return any(e <= i <= end for (e, end) in dives)

    x, y, vy = xs[0], float(cys[0]), 0.0
    idx = 1
    committed = set()
    min_margin = 1e9

    while idx < len(xs):
        dt_next = (xs[idx] - x) / SCROLL_BASE
        bot = cys[idx] + gaps[idx] / 2 - EFFECTIVE_R - SAFE
        top = cys[idx] - gaps[idx] / 2 + EFFECTIVE_R + SAFE

        if idx in entries and idx not in committed:
            flap = True                      # the commit tap at the lip
            committed.add(idx)
        elif in_dive(idx):
            flap = False                     # ride the plunge
        else:
            y_keep, _ = _advance(y, vy, dt_next)
            y_flap, _ = _advance(y, vy, dt_next, flap=True)
            # Centre-seeking (a real player keeps to the middle of the channel):
            # tap when we'd otherwise drift below the next gap's centre, unless
            # that tap would punch the ceiling.
            flap = y_keep > cys[idx]
            if flap and y_flap < top:
                flap = False

        if flap:
            vy = FLAP_V
        vy = min(vy + GRAVITY * DT, MAX_FALL)
        y += vy * DT
        x += SCROLL_BASE * DT

        while idx < len(xs) and x >= xs[idx]:
            cy, gap = cys[idx], gaps[idx]
            margin = min(y - (cy - gap / 2 + EFFECTIVE_R),
                         (cy + gap / 2 - EFFECTIVE_R) - y)
            min_margin = min(min_margin, margin)
            if margin < 0:
                return False, margin, f"clipped pagoda {idx} (y={y:.0f}, " \
                                      f"gap=[{cy-gap/2:.0f},{cy+gap/2:.0f}])"
            idx += 1

    return True, min_margin, "ok"


# ── helper: append a commit-tap dive and record its span ─────────────────────

def add_dive(r, label, sp, floor):
    lip = r.last()
    entry = len(r.cy)
    vals = flap_dive(lip, sp, floor)
    r.seg(label, vals, gap=184, sp=sp)
    r.dives.append((entry, len(r.cy) - 1))


DIVE_FLOOR = 460          # only gates when the dive sampler stops (well below the
                          # natural mid-screen bottom) — the plunge ends itself


def build_routes():
    R = []

    # 1 — THE DROP: a high cruise, ONE commit-tap, a hard ~190px plunge, then flap
    # straight back out. The signature aggressive drop.
    r = RB("The Drop", "Tap once to commit, then a hard ~190px plunge")
    r.dives = []
    r.seg("high cruise", hold_vals(300, 5), gap=178, sp=SP_WIDE)
    add_dive(r, "COMMIT → PLUNGE", 66, DIVE_FLOOR)
    r.seg("flap out", climb_to(r.last(), 300, 82), gap=180, sp=82)
    r.seg("settle", hold_vals(300, 2), gap=178, sp=SP)
    R.append(r)

    # 2 — DOUBLE PLUNGE: two committed plunges with a climb between.
    r = RB("Double Plunge", "Two committed plunges, climb between")
    r.dives = []
    r.seg("perch", hold_vals(292, 4), gap=178, sp=SP_WIDE)
    add_dive(r, "PLUNGE 1", 66, DIVE_FLOOR)
    r.seg("flap out", climb_to(r.last(), 288, 82), gap=180, sp=82)
    add_dive(r, "PLUNGE 2", 66, DIVE_FLOOR)
    r.seg("flap out", climb_to(r.last(), 262, 82), gap=180, sp=82)
    R.append(r)

    # 3 — THE BIG DROP: commit from the ceiling for the deepest single plunge,
    # then a long climb back to the top.
    r = RB("The Big Drop", "The deepest single plunge, then a long climb")
    r.dives = []
    r.seg("ceiling cruise", hold_vals(308, 6), gap=176, sp=SP_WIDE)
    add_dive(r, "BIG PLUNGE", 64, DIVE_FLOOR)
    r.seg("long flap out", climb_to(r.last(), 235, 82), gap=180, sp=82)
    R.append(r)

    # 4 — INTO THE DEEP: a committed plunge straight into a tense low-altitude
    # cruise skimming just over the floor, then a long climb back to safety.
    r = RB("Into the Deep", "Plunge into a tense floor-skimming cruise")
    r.dives = []
    r.seg("cruise", hold_vals(296, 4), gap=178, sp=SP_WIDE)
    add_dive(r, "PLUNGE", 66, DIVE_FLOOR)
    r.seg("floor-skim cruise", hold_vals(404, 7), gap=176, sp=SP_WIDE)
    r.seg("long flap out", climb_to(404, 250, 82), gap=180, sp=82)
    r.seg("settle", hold_vals(250, 2), gap=178, sp=SP)
    R.append(r)

    # 5 — SAWTOOTH PLUNGES: commit, plummet, climb — three times. A sawtooth of
    # stomach-drops.
    r = RB("Sawtooth Plunges", "Commit, plummet, climb — three times")
    r.dives = []
    r.seg("start", hold_vals(300, 3), gap=178, sp=SP_WIDE)
    add_dive(r, "PLUNGE 1", 66, DIVE_FLOOR)
    r.seg("flap out", climb_to(r.last(), 300, 82), gap=178, sp=82)
    add_dive(r, "PLUNGE 2", 66, DIVE_FLOOR)
    r.seg("flap out", climb_to(r.last(), 300, 82), gap=178, sp=82)
    add_dive(r, "PLUNGE 3", 66, DIVE_FLOOR)
    r.seg("survive", climb_to(r.last(), 320, 82), gap=178, sp=82)
    R.append(r)

    for r in R:
        pg = r.pagodas()
        for (_x, cy, gap, _s) in pg:
            assert GAP_CY_MIN <= cy <= GAP_CY_MAX, f"{r.name}: cy {cy} OOB"
            assert 150 <= gap <= 185, f"{r.name}: gap {gap} OOB"
        ok, margin, info = simulate(pg, r.dives)
        assert ok, f"{r.name}: NOT flyable — {info}"
        r.sim_margin = margin
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

    canvas.blit(f_title.render("PAGODA WARREN — 5 routes with an AGGRESSIVE drop",
                               True, (245, 245, 250)), (PAD, PAD - 2))
    canvas.blit(f_sub.render(
        "drops follow the parrot's real gravity arc (commit-tap, then plunge "
        "to ~700px/s)  ·  flown-trajectory validated", True,
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
        canvas.blit(f_meta.render(
            f"{r.n} pagodas  ·  ~{r.duration:.0f}s  ·  clr {r.sim_margin:.0f}px",
            True, (180, 210, 175)), (PAD, y + 38))
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
    out_path = os.path.join(out_dir, "routes_drops_aggressive.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})  scale={factor:.3f}")
    for r in routes:
        print(f"  {r.name:18s} {r.n:3d} pagodas  ~{r.duration:4.1f}s  "
              f"min-clearance {r.sim_margin:4.0f}px")
    print("all aggressive-drop routes flyable (trajectory sim passed)")


if __name__ == "__main__":
    main()
