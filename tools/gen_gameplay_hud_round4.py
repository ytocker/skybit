"""Round-4 CORRECTION of gameplay-HUD direction C ("Adventure Plaques").

Strictly faithful to the round-1 candidate C (carved wood + parchment plaques,
gold rope-band edges, corner rivets, rope hangers on the score plaque, the
score numerals as C drew them, the centered power-up timer with its gold/amber
wood bar). ONLY four edits are applied versus C:

  1. All drop / cast shadows removed (flat). The carved relief is kept — it
     comes from the gradient + inner groove + rope-band rim, not a cast shadow.
  2. Score plaque + power-up timer moved up into the top band. Both stay
     centered; the timer keeps C's exact width and gold/amber wood styling.
  3. Pause re-shaped from C's round wood medallion into a larger wood PILL
     (~84x54) with the same gold rope-band rim + carved double-bar glyph.
  4. Coin counter re-themed to a carved-wood/parchment plaque with gold
     rope-band edge (same family as the score plaque).

Everything else is byte-for-byte the same drawing as C.

Standalone review tooling — does NOT touch game/. Composites at 4x then
smoothscales, exactly like C. Run from repo root:
    python tools/gen_gameplay_hud_round4.py
Output: docs/gameplay_hud/round_4_C_corrected.png
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
import math
import random

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game.config import W, H, MAGNET_DURATION
from game.scenes import App, STATE_PLAY
from game.world import World
from game.hud import (
    _font, _coin_icon,
    _GOLD_BRIGHT, _GOLD_MUTED, _GOLD_DEEP, _GOLD_PALE, _RED_OUTLINE,
    _SCARLET_TOP, _SCARLET_BOT, _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP,
)
from game.draw import (
    lerp_color, UI_CREAM, UI_GOLD, UI_ORANGE, UI_RED, WHITE, NEAR_BLACK,
)
from game.powerup_help import _powerup_icon

OUT = os.path.join(_ROOT, "docs", "gameplay_hud", "round_4_C_corrected.png")

# Representative live values the brief asked for.
SCORE = "12"
COINS = 7
PU_KIND = "magnet"
PU_REMAIN = 5.5
PU_TOTAL = MAGNET_DURATION  # 8.0

SS = 4  # supersample factor — composite big, smoothscale to native (as C did).


# ── Backdrop: a real seeded gameplay frame with the HUD suppressed ──────────
# Reused verbatim from the round-1 generator so the corrected C is judged over
# the same in-context playfield.
def build_backdrop():
    best = None
    for seed in range(60):
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
        for _ in range(int(7.0 / dt)):
            target = H * 0.45
            ahead = [p for p in w.pipes if p.x > w.bird.x - 18]
            if ahead:
                target = min(ahead, key=lambda p: p.x).gap_y - 12
            if w.bird.y > target:
                w.flap()
            w.update(dt)
            if w.game_over:
                break
        on_screen_coin = any(0 < c.x < W for c in w.coins)
        if (not w.game_over and w.score >= 3 and on_screen_coin
                and 140 < w.bird.y < 470):
            best = (app, w)
            break
        if best is None and not w.game_over and w.score >= 2:
            best = (app, w)
    app, w = best
    app.hud.draw_play = lambda *a, **k: None
    app._render()
    return app.screen.copy()


# ── shared supersampled-surface helpers (identical to C) ────────────────────
def _ss_surf(w, h):
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _blit_ss(dst, ss, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(ss, (w, h)), (x, y))


def _vgrad_rounded(surf, rect, top, bot, radius, alpha=255):
    ow, oh = rect.width * SS, rect.height * SS
    orad = radius * SS
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(top, bot, t)
        pygame.draw.line(body, (*c, alpha), (0, yy), (ow - 1, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (rect.x * SS, rect.y * SS))


def _timer_colors(frac):
    if frac > 0.5:
        return UI_GOLD, UI_ORANGE
    if frac > 0.25:
        t = (frac - 0.25) / 0.25
        return lerp_color(UI_ORANGE, UI_GOLD, t), lerp_color(UI_RED, UI_ORANGE, t)
    return UI_RED, (180, 20, 20)


# Text helper — edit 1 removes the cast-text-shadow path entirely (flat).
def _outlined(surf, txt, center, size, fill, outline, px):
    f = _font(size, True)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    for ox, oy in ((-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)):
        surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)
    return r


# =============================================================================
# CANDIDATE C — "Adventure Plaques" (corrected)
# =============================================================================
_WOOD_LT = (96, 62, 34)
_WOOD_MD = (70, 44, 24)
_WOOD_DK = (44, 27, 14)
_PARCH_LT = (236, 214, 164)
_PARCH_DK = (198, 168, 112)


def _rivets(ss, ow, oh, m):
    # C's corner rivets — kept exactly.
    for px, py in ((m, m), (ow - m, m), (m, oh - m), (ow - m, oh - m)):
        pygame.draw.circle(ss, _GOLD_DEEP, (px, py), 3 * SS)
        pygame.draw.circle(ss, _GOLD_BRIGHT, (px, py), 3 * SS, SS)
        pygame.draw.circle(ss, _GOLD_PALE, (px - SS, py - SS), SS)


def cand_plaques(surf):
    def wood_plaque(rect, radius, parchment=False, solid=False):
        # C's plaque, with the cast-shadow blit removed (edit 1). The beveled
        # carved relief is preserved — it lives in the gradient, the inner
        # groove and the gold rope-band rim, none of which are cast shadows.
        # ``solid=True`` fills a single opaque brown instead of the gradient +
        # wood-grain lines, for a clean solid background.
        ss = _ss_surf(rect.width, rect.height)
        ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
        if solid:
            pygame.draw.rect(ss, (*_WOOD_MD, 255), (0, 0, ow, oh),
                             border_radius=orad)
        else:
            if parchment:
                top, bot = _PARCH_LT, _PARCH_DK
            else:
                top, bot = _WOOD_LT, _WOOD_DK
            _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height), top,
                           bot, radius, alpha=248)
            # wood grain / parchment mottling
            rng = random.Random(rect.x * 13 + rect.y)
            for _ in range(int(rect.width * 0.5)):
                yy = rng.randint(2 * SS, oh - 2 * SS)
                a = rng.randint(14, 34)
                col = (30, 18, 8) if not parchment else (150, 120, 70)
                pygame.draw.line(ss, (*col, a), (orad, yy), (ow - orad, yy))
        # carved inner groove — only on the textured (non-solid) plaques; on a
        # solid fill it reads as an unwanted dark line inside the rim.
        if not solid:
            pygame.draw.rect(ss, (0, 0, 0, 120),
                             (3 * SS, 3 * SS, ow - 6 * SS, oh - 6 * SS),
                             width=2 * SS, border_radius=max(1, orad - 3 * SS))
        # gold rope-style outer band
        pygame.draw.rect(ss, _GOLD_DEEP, (0, 0, ow, oh), width=2 * SS,
                         border_radius=orad)
        pygame.draw.rect(ss, (*_GOLD_BRIGHT, 230), (0, 0, ow, oh), width=SS,
                         border_radius=orad)
        _rivets(ss, ow, oh, 8 * SS)
        _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)

    # ── SCORE — hanging center wooden plaque, MOVED UP into the top band
    # (edit 2). Same materials/size/numerals/rope-hangers/rivets as C; only
    # the y-origin changes, and the text cast shadow is dropped (edit 1).
    sf = _font(40, True)
    sw = max(sf.size(SCORE)[0] + 56, 96)
    sp = pygame.Rect((W - sw) // 2, 18, sw, 50)
    # rope hangers up to a notional rail near the very top edge.
    rail_y = 8
    for hx in (sp.x + 16, sp.right - 16):
        pygame.draw.line(surf, _WOOD_DK, (hx, rail_y), (hx, sp.y + 4), 4)
        pygame.draw.line(surf, _GOLD_DEEP, (hx, rail_y), (hx, sp.y + 4), 2)
        pygame.draw.circle(surf, _GOLD_BRIGHT, (hx, rail_y), 3)
    wood_plaque(sp, 12, solid=True)
    _outlined(surf, SCORE, sp.center, 38, _GOLD_PALE, _WOOD_DK, 2)

    # ── COINS — re-themed carved parchment plaque w/ gold rope-band edge
    # (edit 4). C already drew this as a parchment plaque; it now uses the same
    # flat (shadow-free) wood_plaque so it reads as the score plaque's family.
    ct = f"x{COINS}"
    cw = _font(19, True).size(ct)[0] + 42
    cp = pygame.Rect(10, 14, cw, 34)
    wood_plaque(cp, 9, parchment=True)
    _coin_icon(surf, cp.x + 18, cp.centery, 10)
    # Edit 4 spec: "x7" in gold (with a dark wood outline so it stays legible
    # over the pale parchment, matching the score plaque's gold-on-wood read).
    _outlined(surf, ct, (cp.x + 31 + _font(19, True).size(ct)[0] // 2,
                         cp.centery), 19, _GOLD_PALE, _WOOD_DK, 1)

    # ── PAUSE — larger wood PILL (edit 3), replacing C's round medallion.
    # Same wood body + gold rope-band rim + corner rivets + carved double-bar
    # glyph as the rest of the family; rounded-rect, wider than tall, inset
    # ~10px from the top-right corner. No cast shadow (edit 1).
    pw, ph = 84, 54
    px, py = W - pw - 10, 10
    pp = pygame.Rect(px, py, pw, ph)
    rad = ph // 2
    ss = _ss_surf(pw, ph)
    ow, oh, orad = pw * SS, ph * SS, rad * SS
    pygame.draw.rect(ss, (*_WOOD_MD, 255), (0, 0, ow, oh), border_radius=orad)
    pygame.draw.rect(ss, _GOLD_DEEP, (0, 0, ow, oh), width=2 * SS,
                     border_radius=orad)
    pygame.draw.rect(ss, (*_GOLD_BRIGHT, 230), (0, 0, ow, oh), width=SS,
                     border_radius=orad)
    _rivets(ss, ow, oh, 8 * SS)
    # carved double-bar pause glyph (same proportions/colour as C's medallion).
    bw, bh, gap = 6 * SS, 26 * SS, 7 * SS
    midx, midy = ow // 2, oh // 2
    pygame.draw.rect(ss, _GOLD_PALE, (midx - gap - bw, midy - bh // 2, bw, bh),
                     border_radius=2 * SS)
    pygame.draw.rect(ss, _GOLD_PALE, (midx + gap, midy - bh // 2, bw, bh),
                     border_radius=2 * SS)
    _blit_ss(surf, ss, pp.x, pp.y, pw, ph)

    # ── TIMER ROW — MOVED UP (edit 2). Identical icon medallion, identical
    # bar_w / bar_h, identical gold/amber wood track + fill + label as C; only
    # top_y changes so it sits just under the score plaque in the top band.
    icon = 28
    bar_w = 126
    bar_h = 16
    row_w = icon + 6 + bar_w
    base_x = (W - row_w) // 2
    top_y = 80
    frac = PU_REMAIN / PU_TOTAL
    ic = pygame.Rect(base_x, top_y - 6, icon, icon)
    n2 = icon * SS
    chip = _ss_surf(icon, icon)
    for r in range(n2 // 2, 0, -1):
        t = 1 - r / (n2 / 2)
        pygame.draw.circle(chip, lerp_color(_WOOD_LT, _WOOD_DK, t),
                           (n2 // 2, n2 // 2), r)
    pygame.draw.circle(chip, _GOLD_DEEP, (n2 // 2, n2 // 2), n2 // 2, 2 * SS)
    pygame.draw.circle(chip, _GOLD_BRIGHT, (n2 // 2, n2 // 2), n2 // 2 - SS, SS)
    _blit_ss(surf, chip, ic.x, ic.y, icon, icon)
    _powerup_icon(surf, PU_KIND, ic.centerx, ic.centery, icon - 8)
    bx = ic.right + 6
    tr = pygame.Rect(bx, top_y, bar_w, bar_h)
    track = _ss_surf(bar_w, bar_h)
    _vgrad_rounded(track, pygame.Rect(0, 0, bar_w, bar_h), _WOOD_DK, (28, 16, 8),
                   bar_h // 2, alpha=245)
    pygame.draw.rect(track, _GOLD_DEEP, (0, 0, bar_w * SS, bar_h * SS),
                     width=2 * SS, border_radius=bar_h * SS // 2)
    _blit_ss(surf, track, tr.x, tr.y, bar_w, bar_h)
    fhi, flo = _timer_colors(frac)
    fillw = int((bar_w - 6) * frac)
    if fillw > 4:
        fill = _ss_surf(fillw, bar_h - 6)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, bar_h - 6), fhi, flo,
                       (bar_h - 6) // 2)
        _blit_ss(surf, fill, bx + 3, tr.y + 3, fillw, bar_h - 6)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (bx + bar_w // 2, tr.centery), 11,
              _PARCH_LT, _WOOD_DK, 1)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    backdrop = build_backdrop()
    frame = backdrop.copy()
    cand_plaques(frame)
    pygame.image.save(frame, OUT)
    print(f"saved {OUT}  ({W}x{H})")


if __name__ == "__main__":
    main()
