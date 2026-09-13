"""Round-5 fine-tune of the APPROVED gameplay-HUD direction C ("Adventure
Plaques"). Strictly a background-fill tweak on TWO elements only — the SCORE
plaque and the PAUSE pill — versus the round-4 corrected candidate.

Round 4 drew those two as a SOLID OPAQUE dark brown (_WOOD_MD, alpha 255) with
a gold rope rim + rivets. The user found that too heavy/dark. This round keeps
round-4's exact layout/positions/sizes, the four prior edits, the rope hangers,
the rivets, the COIN parchment plaque and the TIMER bar all byte-for-byte; the
ONLY change is the score+pause fill (lighter wood, half-transparent, one flat
clean colour — no grain, no inner groove) plus a legibility-preserving numeral/
glyph treatment so the cream score digits and the pause double-bar stay
high-contrast over the now-translucent panel.

Three variants of that fill are rendered as full 360x640 in-context screens
over the shared gameplay backdrop so the exact feel can be locked:

  V1: lighter wood (_WOOD_LT 96,62,34), alpha 165.
  V2: a touch lighter still (108,72,40), alpha 150 (more see-through).
  V3: premium pick — lighter wood (102,68,38), alpha 170 + one soft top sheen.

Standalone review tooling — does NOT touch game/. Composites at 4x then
smoothscales, exactly like C. Run from repo root:
    python tools/gen_gameplay_hud_round5.py
Output: docs/gameplay_hud/round_5.png
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
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
    _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE,
)
from game.draw import lerp_color, UI_GOLD, UI_ORANGE, UI_RED
from game.powerup_help import _powerup_icon

OUT = os.path.join(_ROOT, "docs", "gameplay_hud", "round_6_transparency.png")

# Representative live values the brief asked for.
SCORE = "12"
COINS = 7
PU_KIND = "magnet"
PU_REMAIN = 5.5
PU_TOTAL = MAGNET_DURATION  # 8.0

SS = 4  # supersample factor — composite big, smoothscale to native (as C did).


# ── Backdrop: a real seeded gameplay frame with the HUD suppressed ──────────
# Reused verbatim from the round-4 generator so the tweak is judged over the
# same in-context playfield.
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


# A heavier double-ring outline for glyphs that now sit over a TRANSLUCENT
# panel — keeps the cream digits crisp against bright sky read-through without
# changing the typeface, size or position the brief froze. The inner ring is a
# near-black halo, the outer a thin dark-wood edge, so the numerals stay legible
# whether the panel happens to overlap pale cloud or blue sky.
def _outlined2(surf, txt, center, size, fill, inner, outer):
    f = _font(size, True)
    img = f.render(txt, True, fill)
    in_img = f.render(txt, True, inner)
    out_img = f.render(txt, True, outer)
    r = img.get_rect(center=center)
    for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        surf.blit(out_img, (r.x + ox, r.y + oy))
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2),
                   (-1, -1), (1, -1), (-1, 1), (1, 1)):
        surf.blit(in_img, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)
    return r


# =============================================================================
# CANDIDATE C — "Adventure Plaques" (round-5 score+pause fill tune)
# =============================================================================
_WOOD_LT = (96, 62, 34)
_WOOD_DK = (44, 27, 14)
_PARCH_LT = (236, 214, 164)
_PARCH_DK = (198, 168, 112)
_GLYPH_HALO = (28, 16, 8)  # near-black halo seating cream glyphs over sky


def _rivets(ss, ow, oh, m):
    # C's corner rivets — kept exactly.
    for px, py in ((m, m), (ow - m, m), (m, oh - m), (ow - m, oh - m)):
        pygame.draw.circle(ss, _GOLD_DEEP, (px, py), 3 * SS)
        pygame.draw.circle(ss, _GOLD_BRIGHT, (px, py), 3 * SS, SS)
        pygame.draw.circle(ss, _GOLD_PALE, (px - SS, py - SS), SS)


def _gold_rim(ss, ow, oh, orad):
    # Crisp refined two-tone rope rim: deep-gold body band, bright-gold hairline
    # highlight just inside it. Quality polish only — same construction as C.
    pygame.draw.rect(ss, _GOLD_DEEP, (0, 0, ow, oh), width=2 * SS,
                     border_radius=orad)
    pygame.draw.rect(ss, (*_GOLD_BRIGHT, 235), (0, 0, ow, oh), width=SS,
                     border_radius=orad)


def _top_sheen(ss, ow, oh, orad):
    # ONE very soft top sheen (V3 only) — a faint pale band fading out over the
    # upper third, clipped to the rounded rect, reading as glassy-wood. No grain,
    # no groove: it is a single low-alpha gradient, not a drawn line.
    sheen = pygame.Surface((ow, oh), pygame.SRCALPHA)
    band = int(oh * 0.42)
    for yy in range(band):
        t = yy / max(1, band - 1)
        a = int(70 * (1 - t) ** 2)
        pygame.draw.line(sheen, (255, 244, 222, a), (0, yy), (ow - 1, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(sheen, (0, 0))


def cand_plaques(surf, wood, alpha, sheen=False):
    """Draw the full HUD. Only the SCORE plaque + PAUSE pill consult ``wood`` /
    ``alpha`` / ``sheen``; everything else is the round-4 drawing verbatim."""

    def wood_plaque(rect, radius, parchment=False, solid=False):
        # Round-4 wood_plaque, byte-for-byte. Used here ONLY for the COIN
        # parchment plaque (parchment=True), which must not change.
        ss = _ss_surf(rect.width, rect.height)
        ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
        if solid:
            pygame.draw.rect(ss, (*(70, 44, 24), 255), (0, 0, ow, oh),
                             border_radius=orad)
        else:
            if parchment:
                top, bot = _PARCH_LT, _PARCH_DK
            else:
                top, bot = _WOOD_LT, _WOOD_DK
            _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height), top,
                           bot, radius, alpha=248)
            rng = random.Random(rect.x * 13 + rect.y)
            for _ in range(int(rect.width * 0.5)):
                yy = rng.randint(2 * SS, oh - 2 * SS)
                a = rng.randint(14, 34)
                col = (30, 18, 8) if not parchment else (150, 120, 70)
                pygame.draw.line(ss, (*col, a), (orad, yy), (ow - orad, yy))
        if not solid:
            pygame.draw.rect(ss, (0, 0, 0, 120),
                             (3 * SS, 3 * SS, ow - 6 * SS, oh - 6 * SS),
                             width=2 * SS, border_radius=max(1, orad - 3 * SS))
        _gold_rim(ss, ow, oh, orad)
        _rivets(ss, ow, oh, 8 * SS)
        _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)

    def translucent_panel(rect, radius):
        # ROUND-5 score/pause body: one flat translucent wood colour under the
        # gold rim — NO gradient, NO grain, NO inner groove (all explicitly
        # rejected as "drawn lines"). Sky/pillars read through the fill.
        ss = _ss_surf(rect.width, rect.height)
        ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
        pygame.draw.rect(ss, (*wood, alpha), (0, 0, ow, oh),
                         border_radius=orad)
        if sheen:
            _top_sheen(ss, ow, oh, orad)
        _gold_rim(ss, ow, oh, orad)
        _rivets(ss, ow, oh, 8 * SS)
        _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)

    # ── SCORE — hanging center wooden plaque (round-4 geometry exactly).
    sf = _font(40, True)
    sw = max(sf.size(SCORE)[0] + 56, 96)
    sp = pygame.Rect((W - sw) // 2, 18, sw, 50)
    rail_y = 8
    for hx in (sp.x + 16, sp.right - 16):
        pygame.draw.line(surf, _WOOD_DK, (hx, rail_y), (hx, sp.y + 4), 4)
        pygame.draw.line(surf, _GOLD_DEEP, (hx, rail_y), (hx, sp.y + 4), 2)
        pygame.draw.circle(surf, _GOLD_BRIGHT, (hx, rail_y), 3)
    translucent_panel(sp, 12)
    # High-contrast numerals: cream fill on a near-black halo + thin dark-wood
    # edge so the digits stay legible over bright sky read-through.
    _outlined2(surf, SCORE, sp.center, 38, _GOLD_PALE, _GLYPH_HALO, _WOOD_DK)

    # ── COINS — round-4 carved parchment plaque, UNCHANGED.
    ct = f"x{COINS}"
    cw = _font(19, True).size(ct)[0] + 42
    cp = pygame.Rect(10, 14, cw, 34)
    wood_plaque(cp, 9, parchment=True)
    _coin_icon(surf, cp.x + 18, cp.centery, 10)
    _outlined(surf, ct, (cp.x + 31 + _font(19, True).size(ct)[0] // 2,
                         cp.centery), 19, _GOLD_PALE, _WOOD_DK, 1)

    # ── PAUSE — larger wood PILL (round-4 geometry exactly); body now the
    # translucent round-5 fill + a high-contrast double-bar glyph.
    pw, ph = 84, 54
    px, py = W - pw - 10, 10
    pp = pygame.Rect(px, py, pw, ph)
    rad = ph // 2
    ss = _ss_surf(pw, ph)
    ow, oh, orad = pw * SS, ph * SS, rad * SS
    pygame.draw.rect(ss, (*wood, alpha), (0, 0, ow, oh), border_radius=orad)
    if sheen:
        _top_sheen(ss, ow, oh, orad)
    _gold_rim(ss, ow, oh, orad)
    _rivets(ss, ow, oh, 8 * SS)
    bw, bh, gap = 6 * SS, 26 * SS, 7 * SS
    midx, midy = ow // 2, oh // 2
    # Halo behind each bar first so the cream glyph reads over translucent wood.
    for cx in (midx - gap - bw, midx + gap):
        pygame.draw.rect(ss, (*_GLYPH_HALO, 235),
                         (cx - SS, midy - bh // 2 - SS, bw + 2 * SS, bh + 2 * SS),
                         border_radius=3 * SS)
    pygame.draw.rect(ss, _GOLD_PALE, (midx - gap - bw, midy - bh // 2, bw, bh),
                     border_radius=2 * SS)
    pygame.draw.rect(ss, _GOLD_PALE, (midx + gap, midy - bh // 2, bw, bh),
                     border_radius=2 * SS)
    _blit_ss(surf, ss, pp.x, pp.y, pw, ph)

    # ── TIMER ROW — round-4 drawing, UNCHANGED.
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


# ── variant definitions (the only thing that differs between the screens) ────
VARIANTS = [
    ("40% opacity  (a102)", (102, 68, 38), 102, False),
    ("55% opacity  (a140)", (102, 68, 38), 140, False),
    ("70% opacity  (a178)", (102, 68, 38), 178, False),
    ("85% opacity  (a217)", (102, 68, 38), 217, False),
    ("100% solid   (a255)", (102, 68, 38), 255, False),
]


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    backdrop = build_backdrop()

    pad = 14
    label_h = 26
    cols = len(VARIANTS)
    sheet_w = pad + cols * (W + pad)
    sheet_h = pad + label_h + H + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 26, 30))

    lf = pygame.font.SysFont("dejavusans", 13, bold=True)
    for i, (label, wood, alpha, sheen) in enumerate(VARIANTS):
        frame = backdrop.copy()
        cand_plaques(frame, wood, alpha, sheen=sheen)
        x = pad + i * (W + pad)
        sheet.blit(frame, (x, pad + label_h))
        img = lf.render(label, True, (236, 224, 204))
        sheet.blit(img, (x + (W - img.get_width()) // 2, pad + 5))

    pygame.image.save(sheet, OUT)
    print(f"saved {OUT}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
