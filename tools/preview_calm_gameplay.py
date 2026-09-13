"""Headless UX check: a SHORTLIST of the calm sky concepts behind REAL gameplay.

Same swap trick as tools/preview_sky_designs_gameplay.py — monkeypatch
`scenes.get_sky_surface_biome` so the live `App._render` paints one of our calm
concepts as the sky, with the real bird / pipes / coins / foreground / HUD on
top — so foreground readability (scarlet bird, gold coins, tan pillars, white
HUD) is judged in situ, not as a bare gradient. Uses the SAME smoother
Catmull-Rom sky bake as the figure (inlined to avoid display-mode import side
effects). Dev aid only; the game never imports this.

Output: docs/biome_redesign/round_14_gameplay_check.png

    python tools/preview_calm_gameplay.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import random

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame  # noqa: E402

pygame.init()

import game.scenes as scenes                       # noqa: E402
import game.sky_designs as _sky_designs            # noqa: E402
from game.config import W, H, GROUND_Y             # noqa: E402
from game.scenes import App, STATE_PLAY            # noqa: E402
from game.world import World                       # noqa: E402
from game import biome_sky_field as sf             # noqa: E402
from game.biome_sky import _sky_stops, _scatter_stars  # noqa: E402
from tools.sky_concepts_calm import CONCEPTS       # noqa: E402

_sky_designs.ACTIVE_SKY_DESIGN = None  # force the live-bake path so the shim runs

OUT = os.path.join(_ROOT, "docs", "biome_redesign", "round_14_gameplay_check.png")
CYCLE_SECONDS = 320.0

_BY_ID = dict(CONCEPTS)
# Shortlist + a representative spread of families (art-director's top picks first).
SHORTLIST = ["starlit_navy", "dawn_rose_grey", "lavender_dusk", "slate_blue_hour", "pearl_overcast"]
COLUMNS = [("morning", 0.10), ("midday", 0.20), ("golden", 0.42),
           ("sunset", 0.50), ("dusk", 0.60), ("night", 0.74)]

TILE_SCALE = 0.62
TW, TH = int(W * TILE_SCALE), int(H * TILE_SCALE)
GUT = 168
PAD = 6
HEAD = 30


# ── smoother sky bake (same Catmull-Rom as the figure) ───────────────────────
def _catmull_rows(stops, n):
    st = sorted(stops, key=lambda s: s[0])
    P = [sf.srgb_to_oklab(c) for _, c in st]
    pos = [p for p, _ in st]
    out = []
    for i in range(n):
        u = i / max(1, n - 1)
        seg = 0
        while seg < len(pos) - 2 and u > pos[seg + 1]:
            seg += 1
        p0, p1 = pos[seg], pos[seg + 1]
        span = p1 - p0 if p1 > p0 else 1e-6
        t = min(1.0, max(0.0, (u - p0) / span))
        P1, P2 = P[seg], P[seg + 1]
        P0 = P[seg - 1] if seg - 1 >= 0 else P[seg]
        P3 = P[seg + 2] if seg + 2 < len(P) else P[seg + 1]
        c = tuple(
            0.5 * ((2 * P1[k]) + (-P0[k] + P2[k]) * t
                   + (2 * P0[k] - 5 * P1[k] + 4 * P2[k] - P3[k]) * t * t
                   + (-P0[k] + 3 * P1[k] - 3 * P2[k] + P3[k]) * t * t * t)
            for k in range(3)
        )
        out.append(sf.oklab_to_srgb(c))
    return out


def _bake(spec, phase):
    surf = pygame.Surface((W, H))
    pal = spec.palette_for_phase(phase)
    stops = _sky_stops(spec, pal)
    for y, col in enumerate(_catmull_rows(stops, H)):
        pygame.draw.line(surf, col, (0, y), (W - 1, y))
    amp = max(spec.sky.dither_amp, 3.0)
    pos, neg = sf._dither_overlays(W, H, amp)
    surf.blit(pos, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(neg, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    sa = int(pal.get('star_alpha', 0))
    if sa > 0:
        _scatter_stars(surf, W, GROUND_Y, sa)
    return surf


_CUR = {"spec": None, "phase": 0.0}
_cache = {}


def _design_sky_shim(w, h, ground_y, palette, phase_bucket):
    key = (id(_CUR["spec"]), _CUR["phase"])
    surf = _cache.get(key)
    if surf is None:
        surf = _bake(_CUR["spec"], _CUR["phase"])
        _cache[key] = surf
    return surf.copy()


def build_gameplay_frame(seconds=7.0):
    def run(seed):
        random.seed(seed)
        app = App()
        if hasattr(app, "_splash_covering"):
            app._splash_covering = False
        w = World()
        w.ready_t = 0.0
        w.flap()
        app.world = w
        app.state = STATE_PLAY
        dt = 1 / 60
        for _ in range(int(seconds / dt)):
            target = H * 0.45
            ahead = [p for p in w.pipes if p.x > w.bird.x - 18]
            if ahead:
                target = min(ahead, key=lambda p: p.x).gap_y - 12
            if w.bird.y > target:
                w.flap()
            w.update(dt)
            if w.game_over:
                break
        return app, w

    best = None
    for seed in range(40):
        app, w = run(seed)
        on_screen_coin = any(0 < c.x < W for c in w.coins)
        if not w.game_over and w.score >= 3 and on_screen_coin:
            return app, w
        if best is None and not w.game_over and w.score >= 2:
            best = (app, w)
    return best if best else (app, w)


def main():
    app, world = build_gameplay_frame()
    app._cloud_phase = 0.0
    if hasattr(app, "_cloud_variant"):
        app._cloud_variant = 0
    scenes.get_sky_surface_biome = _design_sky_shim

    rows, cols = SHORTLIST, COLUMNS
    sheet_w = GUT + PAD + len(cols) * (TW + PAD)
    sheet_h = HEAD + PAD + len(rows) * (TH + PAD)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))

    f_head = pygame.font.SysFont("dejavusans", 15, bold=True)
    f_name = pygame.font.SysFont("dejavusans", 13, bold=True)
    f_tag = pygame.font.SysFont("dejavusans", 11)

    sheet.blit(f_head.render(
        "CALM SKY CONCEPTS x GAMEPLAY — foreground readability check "
        "(sky swapped; real bird/pillars/coins/HUD)", True, (240, 240, 245)),
        (GUT + PAD, 7))
    for ci, (label, _ph) in enumerate(cols):
        x = GUT + PAD + ci * (TW + PAD)
        lbl = f_name.render(label, True, (250, 230, 180))
        sheet.blit(lbl, (x + (TW - lbl.get_width()) // 2, HEAD - 15))

    for ri, cid in enumerate(rows):
        spec = _BY_ID[cid]
        _CUR["spec"] = spec
        y = HEAD + PAD + ri * (TH + PAD)
        nm = f_name.render(spec.name, True, (245, 245, 250))
        sheet.blit(nm, (8, y + TH // 2 - 8))
        for ci, (label, phase) in enumerate(cols):
            x = GUT + PAD + ci * (TW + PAD)
            _CUR["phase"] = phase
            world.biome_time = phase * CYCLE_SECONDS
            app._render()
            sheet.blit(pygame.transform.smoothscale(app.screen, (TW, TH)), (x, y))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print(f"wrote {OUT}  ({sheet.get_width()}x{sheet.get_height()}, "
          f"{len(rows)} rows x {len(cols)} cols)")


if __name__ == "__main__":
    main()
