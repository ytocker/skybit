"""Round-1 exploration sheet for the in-gameplay HUD redesign (STATE_PLAY).

Five distinct visual directions for the score / coins / pause / power-up-timer
lockup, each drawn over a REAL seeded gameplay backdrop (not a flat fill) so the
candidates are judged in context. Each candidate is composited at 4x supersample
then smoothscaled to the 360x640 native canvas (the project's crisp-edge trick,
as in powerup_help._dark_panel) so rims / bevels / gloss don't pixel-step.

Standalone review tooling — does NOT touch game/hud.py or game/scenes.py.
Run from repo root: python tools/gen_gameplay_hud_round1.py
Output: docs/gameplay_hud/round_1.png
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

OUT = os.path.join(_ROOT, "docs", "gameplay_hud", "round_1.png")

# Representative live values the brief asked for.
SCORE = "12"
COINS = 7
PU_KIND = "magnet"
PU_REMAIN = 5.5
PU_TOTAL = MAGNET_DURATION  # 8.0

SS = 4  # supersample factor — composite big, smoothscale to native.


# ── Backdrop: a real seeded gameplay frame with the HUD suppressed ──────────
def build_backdrop():
    """Run a short seeded sim that threads pillars, then render the live App in
    STATE_PLAY with draw_play monkeypatched out so we get a clean playfield
    (sky + pillars + coins + bird) with no HUD on top. Returns a 360x640 surf."""
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
        # Prefer a frame with the bird mid-screen (so the HUD overlaps sky, not
        # the bird) and at least one on-screen coin for a busy, honest backdrop.
        if (not w.game_over and w.score >= 3 and on_screen_coin
                and 140 < w.bird.y < 470):
            best = (app, w)
            break
        if best is None and not w.game_over and w.score >= 2:
            best = (app, w)
    app, w = best
    # Suppress the live HUD so only the playfield paints.
    app.hud.draw_play = lambda *a, **k: None
    app._render()
    return app.screen.copy()


# ── shared supersampled-surface helpers ─────────────────────────────────────
def _ss_surf(w, h):
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _blit_ss(dst, ss, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(ss, (w, h)), (x, y))


def _vgrad_rounded(surf, rect, top, bot, radius, alpha=255):
    """Vertical gradient clipped to a rounded rect, drawn onto a SUPERSAMPLED
    `surf` whose pixel size is ``SS`` × the given native ``rect``. The gradient
    + mask are computed at the full supersampled resolution so the body fills
    the whole oversized surface (not just its top-left 1/SS corner)."""
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
    """Gold -> orange -> red fill pair as the buff depletes (mirrors hud)."""
    if frac > 0.5:
        return UI_GOLD, UI_ORANGE
    if frac > 0.25:
        t = (frac - 0.25) / 0.25
        return lerp_color(UI_ORANGE, UI_GOLD, t), lerp_color(UI_RED, UI_ORANGE, t)
    return UI_RED, (180, 20, 20)


def _outlined(surf, txt, center, size, fill, outline, px, shadow=(0, 0)):
    f = _font(size, True)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    for ox, oy in ((-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)):
        surf.blit(out, (r.x + ox, r.y + oy))
    if shadow != (0, 0):
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(160)
        surf.blit(sh, (r.x + shadow[0], r.y + shadow[1]))
    surf.blit(img, r.topleft)
    return r


# =============================================================================
# CANDIDATE A — "Glass HUD 2.0"
# Frosted navy glass capsules: crisp 2px gold rim, bright inner top sheen,
# soft inner bottom shadow, soft cast shadow under each. Refined / cohesive.
# Pause: 52px frosted-glass disc, inset from the corner for thumb reach.
# =============================================================================
def cand_glass(surf):
    def glass_pill(rect, radius, rim_a=200, body_a=120):
        ss = _ss_surf(rect.width, rect.height)
        ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
        # soft cast shadow baked into a slightly larger pad below
        _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height),
                       lerp_color(_PANEL_LIGHTER, _PANEL_DARK, 0.2),
                       _NIGHT_DEEP, radius, alpha=body_a)
        # bright top sheen — upper third, fading down
        sheen = pygame.Surface((ow, oh), pygame.SRCALPHA)
        for yy in range(oh // 2):
            a = int(70 * (1 - yy / (oh / 2)))
            pygame.draw.line(sheen, (255, 248, 224, a),
                             (orad // 2, yy + SS), (ow - orad // 2, yy + SS))
        smask = pygame.Surface((ow, oh), pygame.SRCALPHA)
        pygame.draw.rect(smask, (255, 255, 255, 255), (0, 0, ow, oh),
                         border_radius=orad)
        sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        ss.blit(sheen, (0, 0))
        # inner bottom shadow
        bsh = pygame.Surface((ow, oh), pygame.SRCALPHA)
        for yy in range(oh // 2, oh):
            a = int(60 * (yy - oh // 2) / (oh / 2))
            pygame.draw.line(bsh, (0, 0, 0, a), (0, yy), (ow, yy))
        bsh.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        ss.blit(bsh, (0, 0))
        # crisp 2px gold rim + 1px pale inner highlight line
        pygame.draw.rect(ss, (*_GOLD_BRIGHT, rim_a), (0, 0, ow, oh),
                         width=2 * SS, border_radius=orad)
        pygame.draw.rect(ss, (*_GOLD_PALE, 120),
                         (2 * SS, 2 * SS, ow - 4 * SS, oh - 4 * SS),
                         width=max(1, SS // 2), border_radius=max(1, orad - 2 * SS))
        # cast shadow underneath, blit first
        sh = pygame.Surface((rect.width + 6, rect.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 75),
                         (0, 0, rect.width + 6, rect.height + 8),
                         border_radius=radius)
        surf.blit(sh, (rect.x - 3, rect.y + 5))
        _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)

    # SCORE — centered glass capsule
    sf = _font(46, True)
    sw = max(sf.size(SCORE)[0] + 52, 92)
    srect = pygame.Rect((W - sw) // 2, 70, sw, 52)
    glass_pill(srect, 26)
    _outlined(surf, SCORE, srect.center, 46, UI_CREAM, _GOLD_DEEP, 2,
              shadow=(2, 3))

    # COINS — top-left glass capsule
    ct = f"x{COINS}"
    cw = _font(18, True).size(ct)[0] + 40
    crect = pygame.Rect(10, 14, cw, 34)
    glass_pill(crect, 12)
    _coin_icon(surf, crect.x + 17, crect.centery, 10)
    ci = _font(18, True).render(ct, True, _GOLD_BRIGHT)
    surf.blit(ci, ci.get_rect(midleft=(crect.x + 30, crect.centery)))

    # PAUSE — 52px frosted glass disc, inset from corner
    pd = 52
    px, py = W - pd - 10, 12
    cx, cy = px + pd // 2, py + pd // 2
    ds = _ss_surf(pd, pd)
    pygame.draw.circle(ds, (*_PANEL_DARK, 150), (pd * SS // 2, pd * SS // 2),
                       pd * SS // 2)
    sheen = pygame.Surface((pd * SS, pd * SS), pygame.SRCALPHA)
    for yy in range(pd * SS // 2):
        a = int(70 * (1 - yy / (pd * SS / 2)))
        pygame.draw.line(sheen, (255, 248, 224, a), (0, yy), (pd * SS, yy))
    smask = pygame.Surface((pd * SS, pd * SS), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255),
                       (pd * SS // 2, pd * SS // 2), pd * SS // 2)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ds.blit(sheen, (0, 0))
    pygame.draw.circle(ds, (*_GOLD_BRIGHT, 210), (pd * SS // 2, pd * SS // 2),
                       pd * SS // 2, 2 * SS)
    bw = 4 * SS
    bh = 18 * SS
    gap = 5 * SS
    midx = pd * SS // 2
    midy = pd * SS // 2
    pygame.draw.rect(ds, _GOLD_BRIGHT, (midx - gap - bw, midy - bh // 2, bw, bh),
                     border_radius=2 * SS)
    pygame.draw.rect(ds, _GOLD_BRIGHT, (midx + gap, midy - bh // 2, bw, bh),
                     border_radius=2 * SS)
    sh = pygame.Surface((pd + 6, pd + 8), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 80), ((pd + 6) // 2, (pd + 8) // 2), pd // 2)
    surf.blit(sh, (px - 3, py + 5))
    _blit_ss(surf, ds, px, py, pd, pd)

    # TIMER ROW — glass-rim icon chip + glass track
    _glass_timer_row(surf, 132, rim=_GOLD_BRIGHT)


def _glass_timer_row(surf, top_y, rim):
    icon = 26
    bar_w = 128
    bar_h = 14
    row_w = icon + 6 + bar_w + 4
    base_x = (W - row_w) // 2
    frac = PU_REMAIN / PU_TOTAL
    # icon chip
    ic = pygame.Rect(base_x, top_y - (icon - bar_h) // 2 - 2, icon, icon)
    chip = _ss_surf(icon, icon)
    _vgrad_rounded(chip, pygame.Rect(0, 0, icon, icon),
                   _PANEL_LIGHTER, _PANEL_DARK, 8, alpha=215)
    pygame.draw.rect(chip, (*rim, 200), (0, 0, icon * SS, icon * SS),
                     width=2 * SS, border_radius=8 * SS)
    _blit_ss(surf, chip, ic.x, ic.y, icon, icon)
    _powerup_icon(surf, PU_KIND, ic.centerx, ic.centery, icon - 4)
    # track
    bx = ic.right + 6
    tr = pygame.Rect(bx, top_y, bar_w, bar_h)
    track = _ss_surf(bar_w, bar_h)
    _vgrad_rounded(track, pygame.Rect(0, 0, bar_w, bar_h),
                   (24, 30, 60), (12, 16, 38), bar_h // 2, alpha=220)
    pygame.draw.rect(track, (*rim, 170), (0, 0, bar_w * SS, bar_h * SS),
                     width=SS, border_radius=bar_h * SS // 2)
    _blit_ss(surf, track, tr.x, tr.y, bar_w, bar_h)
    fhi, flo = _timer_colors(frac)
    fillw = int((bar_w - 4) * frac)
    if fillw > 4:
        fill = _ss_surf(fillw, bar_h - 4)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, bar_h - 4), fhi, flo,
                       (bar_h - 4) // 2)
        _blit_ss(surf, fill, bx + 2, tr.y + 2, fillw, bar_h - 4)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (bx + bar_w // 2, tr.centery), 11,
              UI_CREAM, NEAR_BLACK, 1)


# =============================================================================
# CANDIDATE B — "Gilded Control Bar"
# One embossed brushed-gold bar spans the top, tying coins (left) + score
# (center, on a recessed scarlet plate) + pause (right) into a single console.
# Pause: 50px raised gold knob set into the bar's right end.
# =============================================================================
def cand_controlbar(surf):
    bar_h = 56
    bar = _ss_surf(W, bar_h)
    ow, oh = W * SS, bar_h * SS
    # brushed gold gradient body
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        if t < 0.45:
            c = lerp_color(_GOLD_PALE, _GOLD_BRIGHT, t / 0.45)
        else:
            c = lerp_color(_GOLD_BRIGHT, _GOLD_DEEP, (t - 0.45) / 0.55)
        pygame.draw.line(bar, (*c, 245), (0, yy), (ow, yy))
    # subtle brushed striations
    rng = random.Random(7)
    for _ in range(60):
        yy = rng.randint(0, oh - 1)
        a = rng.randint(12, 30)
        pygame.draw.line(bar, (255, 245, 210, a), (0, yy), (ow, yy))
    # bottom bevel edge: bright lip then deep shadow under the bar
    pygame.draw.line(bar, (*_GOLD_PALE, 220), (0, oh - 3 * SS), (ow, oh - 3 * SS),
                     SS)
    pygame.draw.rect(bar, (*_RED_OUTLINE, 230), (0, oh - 2 * SS, ow, 2 * SS))
    _blit_ss(surf, bar, 0, 0, W, bar_h)
    # cast shadow under the bar
    sh = pygame.Surface((W, 8), pygame.SRCALPHA)
    for i in range(8):
        pygame.draw.line(sh, (0, 0, 0, 60 - i * 7), (0, i), (W, i))
    surf.blit(sh, (0, bar_h))

    # SCORE — recessed scarlet plate, center
    sf = _font(36, True)
    sw = max(sf.size(SCORE)[0] + 44, 84)
    sp = pygame.Rect((W - sw) // 2, 8, sw, 40)
    plate = _ss_surf(sw, 40)
    _vgrad_rounded(plate, pygame.Rect(0, 0, sw, 40), _SCARLET_TOP, _SCARLET_BOT,
                   10)
    # recessed: dark top inner shadow + pale bottom inner lip
    pygame.draw.line(plate, (0, 0, 0, 150), (10 * SS, 2 * SS), (sw * SS - 10 * SS,
                     2 * SS), 2 * SS)
    pygame.draw.rect(plate, (*_GOLD_DEEP, 255), (0, 0, sw * SS, 40 * SS),
                     width=2 * SS, border_radius=10 * SS)
    _blit_ss(surf, plate, sp.x, sp.y, sw, 40)
    _outlined(surf, SCORE, sp.center, 32, UI_CREAM, _RED_OUTLINE, 2,
              shadow=(2, 2))

    # COINS — engraved into the gold at left (dark recessed slot)
    ct = f"x{COINS}"
    cw = _font(20, True).size(ct)[0] + 42
    cp = pygame.Rect(8, 12, cw, 32)
    slot = _ss_surf(cw, 32)
    pygame.draw.rect(slot, (*_NIGHT_DEEP, 235), (0, 0, cw * SS, 32 * SS),
                     border_radius=9 * SS)
    pygame.draw.rect(slot, (0, 0, 0, 180), (0, 0, cw * SS, 4 * SS))
    pygame.draw.rect(slot, (*_GOLD_DEEP, 255), (0, 0, cw * SS, 32 * SS),
                     width=2 * SS, border_radius=9 * SS)
    _blit_ss(surf, slot, cp.x, cp.y, cw, 32)
    _coin_icon(surf, cp.x + 18, cp.centery, 10)
    ci = _font(20, True).render(ct, True, _GOLD_PALE)
    surf.blit(ci, ci.get_rect(midleft=(cp.x + 32, cp.centery)))

    # PAUSE — 50px raised gold knob at the right end of the bar
    pd = 50
    px, py = W - pd - 8, 3
    cx, cy = px + pd // 2, py + pd // 2
    knob = _ss_surf(pd, pd)
    n = pd * SS
    for r in range(n // 2, 0, -1):
        t = 1 - r / (n / 2)
        c = lerp_color(_GOLD_DEEP, _GOLD_PALE, t)
        pygame.draw.circle(knob, c, (n // 2, n // 2 - int(n * 0.04)), r)
    pygame.draw.circle(knob, _RED_OUTLINE, (n // 2, n // 2), n // 2, 2 * SS)
    pygame.draw.circle(knob, (*_NIGHT_DEEP, 230), (n // 2, n // 2),
                       int(n * 0.34))
    bw, bh, gap = 4 * SS, 18 * SS, 5 * SS
    pygame.draw.rect(knob, _GOLD_PALE, (n // 2 - gap - bw, n // 2 - bh // 2, bw, bh),
                     border_radius=2 * SS)
    pygame.draw.rect(knob, _GOLD_PALE, (n // 2 + gap, n // 2 - bh // 2, bw, bh),
                     border_radius=2 * SS)
    sh = pygame.Surface((pd + 6, pd + 6), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 90), ((pd + 6) // 2, (pd + 6) // 2), pd // 2)
    surf.blit(sh, (px - 3, py + 4))
    _blit_ss(surf, knob, px, py, pd, pd)

    # TIMER ROW — sits just under the bar, gold-rimmed
    _bar_timer_row(surf, 70)


def _bar_timer_row(surf, top_y):
    icon = 26
    bar_w = 130
    bar_h = 16
    row_w = icon + 6 + bar_w
    base_x = (W - row_w) // 2
    frac = PU_REMAIN / PU_TOTAL
    ic = pygame.Rect(base_x, top_y - 5, icon, icon)
    chip = _ss_surf(icon, icon)
    for r in range(icon * SS // 2, 0, -1):
        t = 1 - r / (icon * SS / 2)
        pygame.draw.circle(chip, lerp_color(_GOLD_DEEP, _GOLD_BRIGHT, t),
                           (icon * SS // 2, icon * SS // 2), r)
    pygame.draw.circle(chip, _RED_OUTLINE, (icon * SS // 2, icon * SS // 2),
                       icon * SS // 2, 2 * SS)
    pygame.draw.circle(chip, (*_NIGHT_DEEP, 220), (icon * SS // 2, icon * SS // 2),
                       int(icon * SS * 0.32))
    _blit_ss(surf, chip, ic.x, ic.y, icon, icon)
    _powerup_icon(surf, PU_KIND, ic.centerx, ic.centery, icon - 6)
    bx = ic.right + 6
    tr = pygame.Rect(bx, top_y, bar_w, bar_h)
    track = _ss_surf(bar_w, bar_h)
    pygame.draw.rect(track, (*_NIGHT_DEEP, 235), (0, 0, bar_w * SS, bar_h * SS),
                     border_radius=bar_h * SS // 2)
    pygame.draw.rect(track, (*_GOLD_DEEP, 255), (0, 0, bar_w * SS, bar_h * SS),
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
              UI_CREAM, NEAR_BLACK, 1)


# =============================================================================
# CANDIDATE C — "Adventure Plaques"
# Carved wood/parchment plaques with riveted gold corners + rope-bound edges.
# Storybook adventure feel. Score on a hanging center plaque.
# Pause: 52px round wooden medallion with gold ring + rivets.
# =============================================================================
_WOOD_LT = (96, 62, 34)
_WOOD_MD = (70, 44, 24)
_WOOD_DK = (44, 27, 14)
_PARCH_LT = (236, 214, 164)
_PARCH_DK = (198, 168, 112)


def _rivets(ss, ow, oh, m):
    for px, py in ((m, m), (ow - m, m), (m, oh - m), (ow - m, oh - m)):
        pygame.draw.circle(ss, _GOLD_DEEP, (px, py), 3 * SS)
        pygame.draw.circle(ss, _GOLD_BRIGHT, (px, py), 3 * SS, SS)
        pygame.draw.circle(ss, _GOLD_PALE, (px - SS, py - SS), SS)


def cand_plaques(surf):
    def wood_plaque(rect, radius, parchment=False):
        ss = _ss_surf(rect.width, rect.height)
        ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
        if parchment:
            top, bot = _PARCH_LT, _PARCH_DK
        else:
            top, bot = _WOOD_LT, _WOOD_DK
        _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height), top, bot,
                       radius, alpha=248)
        # wood grain / parchment mottling
        rng = random.Random(rect.x * 13 + rect.y)
        for _ in range(int(rect.width * 0.5)):
            yy = rng.randint(2 * SS, oh - 2 * SS)
            a = rng.randint(14, 34)
            col = (30, 18, 8) if not parchment else (150, 120, 70)
            pygame.draw.line(ss, (*col, a), (orad, yy), (ow - orad, yy))
        # carved inner groove
        pygame.draw.rect(ss, (0, 0, 0, 120),
                         (3 * SS, 3 * SS, ow - 6 * SS, oh - 6 * SS),
                         width=2 * SS, border_radius=max(1, orad - 3 * SS))
        # gold rope-style outer band
        pygame.draw.rect(ss, _GOLD_DEEP, (0, 0, ow, oh), width=2 * SS,
                         border_radius=orad)
        pygame.draw.rect(ss, (*_GOLD_BRIGHT, 230), (0, 0, ow, oh), width=SS,
                         border_radius=orad)
        _rivets(ss, ow, oh, 8 * SS)
        sh = pygame.Surface((rect.width + 6, rect.height + 8), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 90), (0, 0, rect.width + 6, rect.height + 8),
                         border_radius=radius)
        surf.blit(sh, (rect.x - 3, rect.y + 5))
        _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)

    # SCORE — hanging center wooden plaque with two little rope hangers
    sf = _font(40, True)
    sw = max(sf.size(SCORE)[0] + 56, 96)
    sp = pygame.Rect((W - sw) // 2, 60, sw, 50)
    # rope hangers up to a notional rail
    for hx in (sp.x + 16, sp.right - 16):
        pygame.draw.line(surf, _WOOD_DK, (hx, 52), (hx, sp.y + 4), 4)
        pygame.draw.line(surf, _GOLD_DEEP, (hx, 52), (hx, sp.y + 4), 2)
        pygame.draw.circle(surf, _GOLD_BRIGHT, (hx, 52), 3)
    wood_plaque(sp, 12)
    _outlined(surf, SCORE, sp.center, 38, _GOLD_PALE, _WOOD_DK, 2, shadow=(2, 3))

    # COINS — small parchment scroll plaque top-left
    ct = f"x{COINS}"
    cw = _font(19, True).size(ct)[0] + 42
    cp = pygame.Rect(10, 14, cw, 34)
    wood_plaque(cp, 9, parchment=True)
    _coin_icon(surf, cp.x + 18, cp.centery, 10)
    ci = _font(19, True).render(ct, True, _WOOD_DK)
    surf.blit(ci, ci.get_rect(midleft=(cp.x + 31, cp.centery)))

    # PAUSE — 52px round wood medallion, inset from corner
    pd = 52
    px, py = W - pd - 10, 12
    n = pd * SS
    med = _ss_surf(pd, pd)
    for r in range(n // 2, 0, -1):
        t = 1 - r / (n / 2)
        pygame.draw.circle(med, lerp_color(_WOOD_LT, _WOOD_DK, t),
                           (n // 2, n // 2), r)
    pygame.draw.circle(med, _GOLD_DEEP, (n // 2, n // 2), n // 2, 3 * SS)
    pygame.draw.circle(med, _GOLD_BRIGHT, (n // 2, n // 2), n // 2 - 2 * SS, SS)
    # rivets around the ring
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        rx = n // 2 + int(math.cos(a) * (n // 2 - 6 * SS))
        ry = n // 2 + int(math.sin(a) * (n // 2 - 6 * SS))
        pygame.draw.circle(med, _GOLD_BRIGHT, (rx, ry), 2 * SS)
    bw, bh, gap = 4 * SS, 18 * SS, 5 * SS
    pygame.draw.rect(med, _GOLD_PALE, (n // 2 - gap - bw, n // 2 - bh // 2, bw, bh),
                     border_radius=2 * SS)
    pygame.draw.rect(med, _GOLD_PALE, (n // 2 + gap, n // 2 - bh // 2, bw, bh),
                     border_radius=2 * SS)
    sh = pygame.Surface((pd + 6, pd + 8), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 95), ((pd + 6) // 2, (pd + 8) // 2), pd // 2)
    surf.blit(sh, (px - 3, py + 5))
    _blit_ss(surf, med, px, py, pd, pd)

    # TIMER ROW — wooden icon medallion + carved track with gold fill
    icon = 28
    bar_w = 126
    bar_h = 16
    row_w = icon + 6 + bar_w
    base_x = (W - row_w) // 2
    top_y = 130
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


# =============================================================================
# CANDIDATE D — "Gold Medallion Cluster"
# Score + coins read as struck gold medals: minted disc with raised rim,
# beveled face, embossed numerals. Coins is a smaller satellite medal.
# Pause: 50px scarlet enamel medal with gold ring (matches the family).
# =============================================================================
def _medal(surf, cx, cy, r, face_top, face_bot, ring=_GOLD_BRIGHT):
    n = r * 2 * SS
    s = _ss_surf(r * 2, r * 2)
    cc = n // 2
    # outer raised gold ring
    for rr in range(cc, int(cc * 0.82), -1):
        t = (cc - rr) / max(1, cc - int(cc * 0.82))
        pygame.draw.circle(s, lerp_color(_GOLD_DEEP, _GOLD_PALE, t), (cc, cc), rr)
    # face
    for rr in range(int(cc * 0.82), 0, -1):
        t = 1 - rr / (cc * 0.82)
        pygame.draw.circle(s, lerp_color(face_top, face_bot, t), (cc, cc), rr)
    # face inner bevel highlight (top-left) + shadow (bottom-right)
    pygame.draw.arc(s, (*_GOLD_PALE, 200),
                    (int(cc * 0.18), int(cc * 0.18), int(cc * 1.64), int(cc * 1.64)),
                    math.radians(60), math.radians(220), 2 * SS)
    pygame.draw.arc(s, (0, 0, 0, 120),
                    (int(cc * 0.18), int(cc * 0.18), int(cc * 1.64), int(cc * 1.64)),
                    math.radians(240), math.radians(400), 2 * SS)
    # ring outline
    pygame.draw.circle(s, _RED_OUTLINE, (cc, cc), cc, SS)
    # tiny ridges around the ring (milled edge)
    for ang in range(0, 360, 12):
        a = math.radians(ang)
        x1 = cc + int(math.cos(a) * cc)
        y1 = cc + int(math.sin(a) * cc)
        x2 = cc + int(math.cos(a) * (cc - 2 * SS))
        y2 = cc + int(math.sin(a) * (cc - 2 * SS))
        pygame.draw.line(s, (*_GOLD_DEEP, 200), (x1, y1), (x2, y2), SS)
    sh = pygame.Surface((r * 2 + 6, r * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 90), (r + 3, r + 4), r)
    surf.blit(sh, (cx - r - 3, cy - r + 1))
    _blit_ss(surf, s, cx - r, cy - r, r * 2, r * 2)


def cand_medallion(surf):
    # SCORE — big struck-gold medal, centered
    sr = 34
    _medal(surf, W // 2, 92, sr, _GOLD_BRIGHT, _GOLD_DEEP)
    _outlined(surf, SCORE, (W // 2, 92), 34, _NIGHT_DEEP, _GOLD_PALE, 1,
              shadow=(0, 0))
    # re-stamp the numerals embossed (dark face engraving + pale top light)
    ef = _font(34, True)
    light = ef.render(SCORE, True, _GOLD_PALE)
    surf.blit(light, light.get_rect(center=(W // 2 - 1, 91)))
    dark = ef.render(SCORE, True, (90, 60, 8))
    surf.blit(dark, dark.get_rect(center=(W // 2, 92)))

    # COINS — smaller satellite gold medal top-left with coin face + count tag
    cr = 19
    _medal(surf, 10 + cr, 14 + cr, cr, _GOLD_BRIGHT, _GOLD_DEEP)
    _coin_icon(surf, 10 + cr, 14 + cr, 12)
    # count on a little scarlet ribbon tag to the medal's right
    ct = f"x{COINS}"
    tw = _font(17, True).size(ct)[0] + 18
    tag = pygame.Rect(10 + cr * 2 - 4, 14 + cr - 11, tw, 22)
    tg = _ss_surf(tag.width, tag.height)
    _vgrad_rounded(tg, pygame.Rect(0, 0, tag.width, tag.height), _SCARLET_TOP,
                   _SCARLET_BOT, 7)
    pygame.draw.rect(tg, (*_GOLD_BRIGHT, 230), (0, 0, tag.width * SS, tag.height * SS),
                     width=SS, border_radius=7 * SS)
    _blit_ss(surf, tg, tag.x, tag.y, tag.width, tag.height)
    ci = _font(17, True).render(ct, True, UI_CREAM)
    surf.blit(ci, ci.get_rect(center=(tag.x + tw // 2 + 2, tag.centery)))

    # PAUSE — 50px scarlet-enamel medal w/ gold ring, inset from corner
    pd = 50
    pr = pd // 2
    cx, cy = W - pr - 11, 11 + pr
    _medal(surf, cx, cy, pr, _SCARLET_TOP, _SCARLET_BOT)
    bw, bh, gap = 4, 18, 5
    pygame.draw.rect(surf, _GOLD_PALE, (cx - gap - bw, cy - bh // 2, bw, bh),
                     border_radius=2)
    pygame.draw.rect(surf, _GOLD_PALE, (cx + gap, cy - bh // 2, bw, bh),
                     border_radius=2)

    # TIMER ROW — coin-medal icon + gold-rimmed enamel track
    icon = 28
    bar_w = 126
    bar_h = 15
    row_w = icon + 8 + bar_w
    base_x = (W - row_w) // 2
    top_y = 134
    frac = PU_REMAIN / PU_TOTAL
    ir = icon // 2
    _medal(surf, base_x + ir, top_y + bar_h // 2, ir, _GOLD_BRIGHT, _GOLD_DEEP)
    _powerup_icon(surf, PU_KIND, base_x + ir, top_y + bar_h // 2, icon - 8)
    bx = base_x + icon + 8
    tr = pygame.Rect(bx, top_y, bar_w, bar_h)
    track = _ss_surf(bar_w, bar_h)
    _vgrad_rounded(track, pygame.Rect(0, 0, bar_w, bar_h), (30, 14, 14),
                   (14, 6, 6), bar_h // 2, alpha=235)
    pygame.draw.rect(track, _GOLD_BRIGHT, (0, 0, bar_w * SS, bar_h * SS),
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
              UI_CREAM, NEAR_BLACK, 1)


# =============================================================================
# CANDIDATE E — "Bold Capsules"
# Sleek modern, high-contrast: chunky scarlet capsules with a heavy gold
# outline + hard gloss band, near-black drop shadow. Maximum prominence.
# Pause: 56px bold scarlet capsule-square with chunky gold pause glyph.
# =============================================================================
def cand_bold(surf):
    def bold_capsule(rect, radius, body_top=_SCARLET_TOP, body_bot=_SCARLET_BOT,
                     out_w=3):
        ss = _ss_surf(rect.width, rect.height)
        ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
        _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height),
                       body_top, body_bot, radius, alpha=255)
        # hard gloss band across the top third
        gloss = pygame.Surface((ow, oh), pygame.SRCALPHA)
        gh = int(oh * 0.38)
        for yy in range(gh):
            a = int(120 * (1 - yy / gh))
            pygame.draw.line(gloss, (255, 250, 235, a),
                             (orad, yy + 2 * SS), (ow - orad, yy + 2 * SS))
        gm = pygame.Surface((ow, oh), pygame.SRCALPHA)
        pygame.draw.rect(gm, (255, 255, 255, 255), (0, 0, ow, oh),
                         border_radius=orad)
        gloss.blit(gm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        ss.blit(gloss, (0, 0))
        # heavy gold outline
        pygame.draw.rect(ss, _GOLD_BRIGHT, (0, 0, ow, oh), width=out_w * SS,
                         border_radius=orad)
        sh = pygame.Surface((rect.width + 8, rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 130),
                         (0, 0, rect.width + 8, rect.height + 10),
                         border_radius=radius)
        surf.blit(sh, (rect.x - 4, rect.y + 6))
        _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)

    # SCORE — big bold scarlet capsule, centered
    sf = _font(48, True)
    sw = max(sf.size(SCORE)[0] + 56, 100)
    sp = pygame.Rect((W - sw) // 2, 66, sw, 58)
    bold_capsule(sp, 18, out_w=3)
    _outlined(surf, SCORE, sp.center, 48, UI_CREAM, _RED_OUTLINE, 3, shadow=(3, 4))

    # COINS — chunky navy capsule with gold outline, top-left
    ct = f"x{COINS}"
    cw = _font(20, True).size(ct)[0] + 46
    cp = pygame.Rect(10, 14, cw, 38)
    bold_capsule(cp, 12, body_top=_PANEL_LIGHTER, body_bot=_PANEL_DARK, out_w=3)
    _coin_icon(surf, cp.x + 20, cp.centery, 12)
    ci = _font(20, True).render(ct, True, _GOLD_BRIGHT)
    surf.blit(ci, ci.get_rect(midleft=(cp.x + 35, cp.centery)))

    # PAUSE — 56px bold scarlet rounded-square, inset from corner
    pd = 56
    px, py = W - pd - 8, 10
    pp = pygame.Rect(px, py, pd, pd)
    bold_capsule(pp, 16, out_w=3)
    cx, cy = pp.center
    bw, bh, gap = 6, 22, 6
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - gap - bw, cy - bh // 2, bw, bh),
                     border_radius=3)
    pygame.draw.rect(surf, _GOLD_BRIGHT, (cx + gap, cy - bh // 2, bw, bh),
                     border_radius=3)
    # dark inner edge on the glyph for punch
    pygame.draw.rect(surf, _RED_OUTLINE, (cx - gap - bw, cy - bh // 2, bw, bh),
                     width=1, border_radius=3)
    pygame.draw.rect(surf, _RED_OUTLINE, (cx + gap, cy - bh // 2, bw, bh),
                     width=1, border_radius=3)

    # TIMER ROW — chunky icon square + thick gold-outlined track
    icon = 30
    bar_w = 128
    bar_h = 18
    row_w = icon + 8 + bar_w
    base_x = (W - row_w) // 2
    top_y = 134
    frac = PU_REMAIN / PU_TOTAL
    ic = pygame.Rect(base_x, top_y - 6, icon, icon)
    bold_capsule(ic, 9, body_top=_PANEL_LIGHTER, body_bot=_PANEL_DARK, out_w=2)
    _powerup_icon(surf, PU_KIND, ic.centerx, ic.centery, icon - 6)
    bx = ic.right + 8
    tr = pygame.Rect(bx, top_y, bar_w, bar_h)
    track = _ss_surf(bar_w, bar_h)
    pygame.draw.rect(track, (*_PANEL_DARK, 245), (0, 0, bar_w * SS, bar_h * SS),
                     border_radius=bar_h * SS // 2)
    pygame.draw.rect(track, _GOLD_BRIGHT, (0, 0, bar_w * SS, bar_h * SS),
                     width=2 * SS, border_radius=bar_h * SS // 2)
    _blit_ss(surf, track, tr.x, tr.y, bar_w, bar_h)
    fhi, flo = _timer_colors(frac)
    fillw = int((bar_w - 8) * frac)
    if fillw > 4:
        fill = _ss_surf(fillw, bar_h - 8)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, bar_h - 8), fhi, flo,
                       (bar_h - 8) // 2)
        _blit_ss(surf, fill, bx + 4, tr.y + 4, fillw, bar_h - 8)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (bx + bar_w // 2, tr.centery), 12,
              UI_CREAM, NEAR_BLACK, 1)


# ── sheet assembly ──────────────────────────────────────────────────────────
CANDIDATES = [
    ("Glass HUD 2.0", "Frosted navy glass capsules, crisp gold rims + inner sheen",
     "Pause: 52px glass disc", cand_glass),
    ("Gilded Control Bar", "One embossed brushed-gold bar ties score+coins+pause",
     "Pause: 50px raised gold knob", cand_controlbar),
    ("Adventure Plaques", "Carved wood + parchment plaques, gold rivets + rope",
     "Pause: 52px wood medallion", cand_plaques),
    ("Gold Medallions", "Score + coins struck as minted gold medals (badge set)",
     "Pause: 50px scarlet enamel medal", cand_medallion),
    ("Bold Capsules", "Chunky high-contrast scarlet capsules, heavy gold outline",
     "Pause: 56px bold capsule", cand_bold),
]


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    backdrop = build_backdrop()

    pad = 18
    label_h = 64
    cols = len(CANDIDATES)
    cell_w = W + pad
    sheet_w = pad + cols * cell_w
    sheet_h = pad + label_h + H + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 14, 30))

    title_f = _font(20, True)
    name_f = _font(17, True)
    desc_f = _font(12, True)
    callout_f = _font(12, True)

    for i, (name, desc, callout, fn) in enumerate(CANDIDATES):
        x = pad + i * cell_w
        # labels
        ni = name_f.render(f"{chr(65 + i)}.  {name}", True, _GOLD_BRIGHT)
        sheet.blit(ni, (x, pad + 2))
        # wrap description
        words = desc.split()
        line, lines = "", []
        for wd in words:
            test = (line + " " + wd).strip()
            if desc_f.size(test)[0] <= W - 4:
                line = test
            else:
                lines.append(line)
                line = wd
        if line:
            lines.append(line)
        for li, ln in enumerate(lines[:2]):
            di = desc_f.render(ln, True, UI_CREAM)
            sheet.blit(di, (x, pad + 24 + li * 14))
        co = callout_f.render(callout, True, UI_ORANGE)
        sheet.blit(co, (x, pad + 24 + len(lines[:2]) * 14))

        # candidate frame
        frame = backdrop.copy()
        fn(frame)
        fy = pad + label_h
        sheet.blit(frame, (x, fy))
        pygame.draw.rect(sheet, _GOLD_DEEP, (x, fy, W, H), 1)

    # sheet title strip at very top would overlap; place a footer tag instead
    foot = title_f.render(
        "Skybit — Gameplay HUD redesign  ·  Round 1  ·  score 12 · coins x7 · magnet 5.5s/8s",
        True, _GOLD_PALE)
    # draw footer on a fresh taller sheet to avoid overlap
    final = pygame.Surface((sheet_w, sheet_h + 30))
    final.fill((12, 9, 22))
    final.blit(sheet, (0, 30))
    final.blit(foot, (pad, 8))

    pygame.image.save(final, OUT)
    print(f"saved {OUT}  ({sheet_w}x{sheet_h + 30})")


if __name__ == "__main__":
    main()
