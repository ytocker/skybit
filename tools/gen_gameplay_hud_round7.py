"""Round-7 exploration sheet for the in-gameplay HUD (STATE_PLAY top strip).

Rounds 1-6 all converged on the SAME idea (carved wood + parchment + gold
rope-band + corner rivets) and were rejected. This round is a hard reset: five
GENUINELY DIFFERENT visual languages, none of which is a wood plaque and none
of which is just a re-skin of the current navy-glass pills. Each is researched
against modern casual-mobile HUDs (Alto's Odyssey / Sky: Children of the Light
minimalism, Subway Surfers / Crossy Road chunky stickers, radial-ring timer
conveyance) so the directions are fresh.

Every concept is a full kit (score / coins / pause / power-up timer) and is
judged over BOTH a real DAY frame and a real NIGHT frame so legibility holds in
both biomes. A sixth column shows the CURRENT live HUD for comparison.

Standalone review tooling — does NOT touch game/ runtime code.
Run from repo root: python tools/gen_gameplay_hud_round7.py
Output: docs/gameplay_hud/round_7.png
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
    _GOLD_BRIGHT, _GOLD_DEEP, _GOLD_PALE, _RED_OUTLINE,
    _SCARLET_TOP, _SCARLET_BOT, _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP,
)
from game.draw import (
    lerp_color, UI_CREAM, UI_GOLD, UI_ORANGE, UI_RED, WHITE, NEAR_BLACK,
)
from game.powerup_help import _powerup_icon

OUT = os.path.join(_ROOT, "docs", "gameplay_hud", "round_7.png")

# Representative live values the brief asked for.
SCORE = "12"
COINS = 7
PU_KIND = "magnet"
PU_REMAIN = 5.5
PU_TOTAL = MAGNET_DURATION  # 8.0

SS = 4  # supersample factor — composite big, smoothscale to native.

# Night keyframe sits at phase 0.64375 of the 320 s biome cycle.
NIGHT_TIME = 0.64375 * 320.0


# ── Backdrop: a real seeded gameplay frame with the HUD suppressed ──────────
def build_backdrop(biome_time=0.0):
    """Run a short seeded sim that threads pillars, then render the live App in
    STATE_PLAY with draw_play monkeypatched out so we get a clean playfield
    (sky + pillars + coins + bird) and no HUD. ``biome_time`` selects the day
    or night palette. Returns a 360x640 surf."""
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
    # Force the chosen biome (day vs night) by overriding elapsed biome time,
    # then drop the live HUD so only the playfield paints.
    w.biome_time = biome_time
    app.hud.draw_play = lambda *a, **k: None
    app._render()
    return app.screen.copy()


def current_hud_frame(biome_time=0.0):
    """The real current HUD (HUD.draw_play) over a frame with score 12 /
    coins x7 / magnet 5.5s, for the reference tile. Built the same way as
    build_backdrop but WITHOUT suppressing the HUD."""
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
    w.biome_time = biome_time
    w.score = 12
    w.coin_count = 7
    w.magnet_timer = PU_REMAIN  # light a magnet timer bar
    app._render()
    return app.screen.copy()


# ── shared supersampled-surface helpers ─────────────────────────────────────
def _ss_surf(w, h):
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _blit_ss(dst, ss, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(ss, (w, h)), (x, y))


def _vgrad_rounded(surf, rect, top, bot, radius, alpha=255):
    """Vertical gradient clipped to a rounded rect, drawn onto a SUPERSAMPLED
    `surf` whose pixel size is ``SS`` × the given native ``rect``."""
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


def _soft_scrim(surf, center, w, h, alpha=150, color=(8, 6, 20)):
    """A soft radial dark scrim used by container-less concepts so a number
    stays legible over a bright-sky-PLUS-brown-pillar worst case WITHOUT a
    hard panel edge. Drawn supersampled as a stack of fading ellipses."""
    pad = 18
    ow, oh = (w + pad * 2) * SS, (h + pad * 2) * SS
    s = pygame.Surface((ow, oh), pygame.SRCALPHA)
    steps = 16
    for i in range(steps):
        t = i / (steps - 1)
        a = int(alpha * (1 - t) ** 1.6)
        rx = int(ow / 2 * (0.42 + 0.58 * t))
        ry = int(oh / 2 * (0.42 + 0.58 * t))
        pygame.draw.ellipse(s, (*color, a),
                            (ow // 2 - rx, oh // 2 - ry, rx * 2, ry * 2))
    small = pygame.transform.smoothscale(s, (w + pad * 2, h + pad * 2))
    surf.blit(small, (center[0] - (w + pad * 2) // 2,
                      center[1] - (h + pad * 2) // 2))


# =============================================================================
# CANDIDATE A — "Floating Ink"
# Alto / Sky minimalism: NO container chrome at all. Score is a big cream
# numeral riding on a soft radial dark scrim (baked behind the glyphs only),
# coins float with the coin face + a soft halo, pause is a hairline ring disc.
# Timer is the icon + a thin underline tick that fills, with halo'd text.
# Reads on landscape; the only "panel" is light, which is the whole point.
# =============================================================================
def cand_floating(surf):
    # SCORE — big cream numerals, soft dark halo only behind the glyphs.
    _soft_scrim(surf, (W // 2, 96), 66, 56, alpha=150)
    _outlined(surf, SCORE, (W // 2, 94), 52, UI_CREAM, NEAR_BLACK, 2,
              shadow=(2, 3))

    # COINS — coin face + count, floating with a soft halo (no pill).
    _soft_scrim(surf, (40, 30), 70, 26, alpha=120)
    _coin_icon(surf, 22, 30, 11)
    _outlined(surf, f"{COINS}", (52, 30), 21, UI_GOLD, NEAR_BLACK, 2)

    # PAUSE — hairline ring disc, cream glyph; soft halo for tap clarity.
    pd = 52
    cx, cy = W - pd // 2 - 10, 12 + pd // 2
    _soft_scrim(surf, (cx, cy), pd, pd, alpha=120)
    ring = _ss_surf(pd, pd)
    n = pd * SS
    pygame.draw.circle(ring, (*UI_CREAM, 230), (n // 2, n // 2), n // 2 - SS,
                       max(2, SS // 2 + SS))
    pygame.draw.circle(ring, (*NEAR_BLACK, 160), (n // 2, n // 2), n // 2, SS)
    bw, bh, gap = 5 * SS, 20 * SS, 6 * SS
    pygame.draw.rect(ring, UI_CREAM, (n // 2 - gap - bw, n // 2 - bh // 2, bw, bh),
                     border_radius=2 * SS)
    pygame.draw.rect(ring, UI_CREAM, (n // 2 + gap, n // 2 - bh // 2, bw, bh),
                     border_radius=2 * SS)
    _blit_ss(surf, ring, cx - pd // 2, cy - pd // 2, pd, pd)

    # TIMER — bare icon + thin underline tick that depletes, halo'd time text.
    icon = 26
    bar_w = 120
    bar_h = 5
    row_w = icon + 8 + bar_w
    base_x = (W - row_w) // 2
    top_y = 134
    frac = PU_REMAIN / PU_TOTAL
    _soft_scrim(surf, (W // 2, top_y + 4), row_w + 8, 30, alpha=110)
    _powerup_icon(surf, PU_KIND, base_x + icon // 2, top_y + 4, icon)
    bx = base_x + icon + 8
    # faint full-length track baseline so the remaining length reads
    track = _ss_surf(bar_w, bar_h)
    pygame.draw.rect(track, (*NEAR_BLACK, 150), (0, 0, bar_w * SS, bar_h * SS),
                     border_radius=bar_h * SS // 2)
    _blit_ss(surf, track, bx, top_y + 10, bar_w, bar_h)
    fhi, flo = _timer_colors(frac)
    fillw = max(6, int(bar_w * frac))
    fill = _ss_surf(fillw, bar_h)
    _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, bar_h), fhi, flo, bar_h // 2)
    _blit_ss(surf, fill, bx, top_y + 10, fillw, bar_h)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (bx + bar_w + 18, top_y + 4), 12,
              UI_CREAM, NEAR_BLACK, 1)


# =============================================================================
# CANDIDATE B — "Sticker Pop"
# Subway Surfers / Crossy Road chunky cartoon: FLAT fills, heavy clean dark
# outlines, NO skeuomorphic bevel. Friendly rounded badges that feel like
# stickers slapped on the screen. Coins = teal chip, score = fat sunny badge,
# pause = chunky rounded-square, timer = a sticker pill with the icon popping
# off its left edge. Toy-like, high energy, very legible.
# =============================================================================
_INK = (28, 20, 36)          # the heavy cartoon outline ink
_STICKER_SUN = (255, 206, 64)
_STICKER_SUN_D = (240, 170, 40)
_STICKER_TEAL = (54, 196, 178)
_STICKER_TEAL_D = (28, 150, 142)
_STICKER_VIOLET = (138, 96, 224)
_STICKER_VIOLET_D = (104, 64, 190)


def _sticker(surf, rect, radius, top, bot, ink=_INK, ink_w=3):
    """Flat-ish rounded sticker: solid two-stop fill, thick dark outline,
    a soft drop shadow, and a small top gloss dab. No metal bevel."""
    sh = pygame.Surface((rect.width + 8, rect.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90), (0, 0, rect.width + 8, rect.height + 10),
                     border_radius=radius + 2)
    surf.blit(sh, (rect.x - 4, rect.y + 5))
    ss = _ss_surf(rect.width, rect.height)
    _vgrad_rounded(ss, pygame.Rect(0, 0, rect.width, rect.height), top, bot,
                   radius)
    ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
    # top gloss dab
    gl = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.ellipse(gl, (255, 255, 255, 70),
                        (orad, 2 * SS, ow - 2 * orad, oh // 2))
    gm = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(gm, (255, 255, 255, 255), (0, 0, ow, oh), border_radius=orad)
    gl.blit(gm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(gl, (0, 0))
    pygame.draw.rect(ss, ink, (0, 0, ow, oh), width=ink_w * SS,
                     border_radius=orad)
    _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)


def cand_sticker(surf):
    # SCORE — fat sunny badge, centered, with inked cream numerals.
    sf = _font(46, True)
    sw = max(sf.size(SCORE)[0] + 52, 96)
    sp = pygame.Rect((W - sw) // 2, 68, sw, 54)
    _sticker(surf, sp, 22, _STICKER_SUN, _STICKER_SUN_D, ink_w=3)
    _outlined(surf, SCORE, sp.center, 46, UI_CREAM, _INK, 3, shadow=(0, 0))

    # COINS — teal chip top-left; coin face pops slightly off the left edge.
    ct = f"{COINS}"
    cw = _font(20, True).size(ct)[0] + 44
    cp = pygame.Rect(16, 14, cw, 36)
    _sticker(surf, cp, 14, _STICKER_TEAL, _STICKER_TEAL_D, ink_w=3)
    _coin_icon(surf, cp.x + 4, cp.centery, 12)
    _outlined(surf, ct, (cp.x + 30 + _font(20, True).size(ct)[0] // 2, cp.centery),
              20, UI_CREAM, _INK, 2)

    # PAUSE — chunky rounded-square sticker, inked pause glyph.
    pd = 54
    pp = pygame.Rect(W - pd - 10, 12, pd, pd)
    _sticker(surf, pp, 16, _STICKER_VIOLET, _STICKER_VIOLET_D, ink_w=3)
    cx, cy = pp.center
    bw, bh, gap = 6, 22, 6
    for dx in (-gap - bw, gap):
        pygame.draw.rect(surf, UI_CREAM, (cx + dx, cy - bh // 2, bw, bh),
                         border_radius=3)
        pygame.draw.rect(surf, _INK, (cx + dx, cy - bh // 2, bw, bh),
                         width=2, border_radius=3)

    # TIMER — sticker pill, icon medallion pops off the left edge, flat track.
    bar_w = 134
    bar_h = 22
    icon = 30
    base_x = (W - (bar_w + icon // 2)) // 2
    top_y = 132
    frac = PU_REMAIN / PU_TOTAL
    pill = pygame.Rect(base_x + icon // 2, top_y, bar_w, bar_h)
    # recessed dark track inside the sticker so the gold fill cannot read as
    # a free coin (separation from the gold economy, sticker idiom).
    _sticker(surf, pill, bar_h // 2, (44, 36, 64), (26, 20, 42), ink_w=3)
    fhi, flo = _timer_colors(frac)
    inset = 5
    fillw = int((bar_w - inset * 2) * frac)
    if fillw > 4:
        fill = _ss_surf(fillw, bar_h - inset * 2)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, bar_h - inset * 2),
                       fhi, flo, (bar_h - inset * 2) // 2)
        _blit_ss(surf, fill, pill.x + inset, pill.y + inset, fillw,
                 bar_h - inset * 2)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (pill.centerx + 6, pill.centery), 12,
              UI_CREAM, _INK, 1)
    # icon medallion popping off the left edge
    ic_cx, ic_cy = base_x + icon // 2, top_y + bar_h // 2
    med = _ss_surf(icon, icon)
    n = icon * SS
    pygame.draw.circle(med, _STICKER_VIOLET, (n // 2, n // 2), n // 2 - SS)
    pygame.draw.circle(med, _INK, (n // 2, n // 2), n // 2, 3 * SS)
    _blit_ss(surf, med, ic_cx - icon // 2, ic_cy - icon // 2, icon, icon)
    _powerup_icon(surf, PU_KIND, ic_cx, ic_cy, icon - 8)


# =============================================================================
# CANDIDATE C — "Radial Orbit"
# A "rings" kit. The power-up TIMER is a RADIAL RING countdown sweeping around
# the icon medallion (DOOM / casual timer-conveyance pattern) — NOT a bar — so
# it can never be mistaken for a gold coin or a lit pillar edge. Coins + pause
# echo the ring motif. Score sits in a clean dark recessed lozenge with a thin
# cyan accent so the kit feels like one system of rings.
# =============================================================================
_ORBIT_DARK = (18, 22, 42)
_ORBIT_DARK2 = (10, 12, 28)
_ORBIT_CYAN = (96, 214, 224)
_ORBIT_CYAN_D = (40, 150, 170)


def _ring_disc(surf, cx, cy, d, fill_dark=True):
    """A dark recessed disc with a cyan rim — the kit's base token."""
    s = _ss_surf(d, d)
    n = d * SS
    if fill_dark:
        for r in range(n // 2, 0, -1):
            t = 1 - r / (n / 2)
            c = lerp_color(_ORBIT_DARK, _ORBIT_DARK2, t)
            pygame.draw.circle(s, (*c, 235), (n // 2, n // 2), r)
    pygame.draw.circle(s, (*_ORBIT_CYAN_D, 255), (n // 2, n // 2), n // 2, 2 * SS)
    pygame.draw.circle(s, (*_ORBIT_CYAN, 200), (n // 2, n // 2), n // 2 - 2 * SS,
                       SS)
    sh = pygame.Surface((d + 6, d + 8), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 90), ((d + 6) // 2, (d + 8) // 2), d // 2)
    surf.blit(sh, (cx - (d + 6) // 2, cy - d // 2 + 4))
    _blit_ss(surf, s, cx - d // 2, cy - d // 2, d, d)


def _radial_timer(surf, cx, cy, d, frac):
    """Thick arc that sweeps clockwise from 12 o'clock, depleting with frac.
    Uses the gold->orange->red colour as it empties (kept distinct from the
    coin by being an open ARC on a dark ring, not a filled gold disc)."""
    s = _ss_surf(d, d)
    n = d * SS
    cc = n // 2
    rad = cc - 3 * SS
    # faint full track
    pygame.draw.circle(s, (*NEAR_BLACK, 150), (cc, cc), rad, 4 * SS)
    fhi, _ = _timer_colors(frac)
    # supersampled arc as a fan of short segments for clean thickness
    start = -math.pi / 2
    end = start + 2 * math.pi * frac
    steps = max(2, int(120 * frac))
    pts_out, pts_in = [], []
    for i in range(steps + 1):
        a = start + (end - start) * i / steps
        pts_out.append((cc + math.cos(a) * (rad + 2 * SS),
                        cc + math.sin(a) * (rad + 2 * SS)))
        pts_in.append((cc + math.cos(a) * (rad - 2 * SS),
                       cc + math.sin(a) * (rad - 2 * SS)))
    if len(pts_out) > 1:
        poly = pts_out + pts_in[::-1]
        pygame.draw.polygon(s, fhi, poly)
    _blit_ss(surf, s, cx - d // 2, cy - d // 2, d, d)


def cand_orbit(surf):
    # SCORE — clean dark recessed lozenge with a thin cyan accent.
    sf = _font(44, True)
    sw = max(sf.size(SCORE)[0] + 50, 94)
    sp = pygame.Rect((W - sw) // 2, 68, sw, 52)
    ss = _ss_surf(sw, 52)
    _vgrad_rounded(ss, pygame.Rect(0, 0, sw, 52), _ORBIT_DARK, _ORBIT_DARK2, 16,
                   alpha=232)
    pygame.draw.rect(ss, (*_ORBIT_CYAN_D, 255), (0, 0, sw * SS, 52 * SS),
                     width=2 * SS, border_radius=16 * SS)
    pygame.draw.line(ss, (*_ORBIT_CYAN, 180), (16 * SS, 3 * SS),
                     (sw * SS - 16 * SS, 3 * SS), SS)
    _blit_ss(surf, ss, sp.x, sp.y, sw, 52)
    _outlined(surf, SCORE, sp.center, 44, UI_CREAM, NEAR_BLACK, 2, shadow=(2, 3))

    # COINS — small ring disc with the coin face + count to its right.
    cd = 36
    _ring_disc(surf, 14 + cd // 2, 14 + cd // 2, cd)
    _coin_icon(surf, 14 + cd // 2, 14 + cd // 2, 12)
    _outlined(surf, f"{COINS}", (14 + cd + 14, 14 + cd // 2), 20, _ORBIT_CYAN,
              NEAR_BLACK, 2)

    # PAUSE — ring disc with cream pause glyph (matches the kit).
    pd = 52
    cx, cy = W - pd // 2 - 10, 12 + pd // 2
    _ring_disc(surf, cx, cy, pd)
    bw, bh, gap = 5, 20, 6
    for dx in (-gap - bw, gap):
        pygame.draw.rect(surf, UI_CREAM, (cx + dx, cy - bh // 2, bw, bh),
                         border_radius=2)

    # TIMER — RADIAL RING countdown around the power-up medallion + side text.
    td = 40
    tcx, tcy = W // 2 - 24, 150
    frac = PU_REMAIN / PU_TOTAL
    _ring_disc(surf, tcx, tcy, td)
    _powerup_icon(surf, PU_KIND, tcx, tcy, td - 14)
    _radial_timer(surf, tcx, tcy, td, frac)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (tcx + td // 2 + 26, tcy), 14,
              UI_CREAM, NEAR_BLACK, 2)


# =============================================================================
# CANDIDATE D — "Sky Ribbon"
# Sky: Children of the Light airiness: soft frosted-translucent rounded ribbons
# with a faint warm-cream tint and a hairline light rim — barely-there chrome
# that lets the landscape shine through. Score on a wide soft ribbon, coins on
# a small one, pause a soft circle, timer a soft capsule with a RECESSED cool
# track so its fill never reads as a coin. Gentle, premium, modern.
# =============================================================================
_RIBBON_TINT = (250, 246, 236)
_RIBBON_RIM = (255, 255, 255)
_RIBBON_TRACK = (70, 86, 120)
_RIBBON_TRACK_D = (44, 56, 86)


def _ribbon(surf, rect, radius, tint=_RIBBON_TINT, body_a=70):
    """Frosted translucent ribbon: a soft white-cream fill at low alpha, a
    thin bright top rim and a faint dark bottom line for a glassy lift, plus
    a gentle drop shadow. Intentionally light so the sky reads through it."""
    sh = pygame.Surface((rect.width + 6, rect.height + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (10, 12, 30, 60), (0, 0, rect.width + 6, rect.height + 8),
                     border_radius=radius)
    surf.blit(sh, (rect.x - 3, rect.y + 4))
    ss = _ss_surf(rect.width, rect.height)
    ow, oh, orad = rect.width * SS, rect.height * SS, radius * SS
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        a = int(body_a * (1.0 - 0.35 * t))
        c = lerp_color(tint, (210, 214, 226), t)
        pygame.draw.line(body, (*c, a), (0, yy), (ow, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(body, (0, 0))
    pygame.draw.rect(ss, (*_RIBBON_RIM, 170), (0, 0, ow, oh), width=SS,
                     border_radius=orad)
    pygame.draw.line(ss, (255, 255, 255, 210), (orad, 2 * SS),
                     (ow - orad, 2 * SS), SS)
    pygame.draw.line(ss, (10, 14, 36, 70), (orad, oh - 2 * SS),
                     (ow - orad, oh - 2 * SS), SS)
    _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)


def cand_ribbon(surf):
    # SCORE — wide soft ribbon. Numerals get a darker scrim band behind them
    # so they stay readable even though the ribbon itself is light.
    sf = _font(46, True)
    sw = max(sf.size(SCORE)[0] + 64, 110)
    sp = pygame.Rect((W - sw) // 2, 68, sw, 54)
    _ribbon(surf, sp, 26)
    # inner cool scrim ONLY behind the digits for worst-case legibility
    scrim = _ss_surf(60, 44)
    _vgrad_rounded(scrim, pygame.Rect(0, 0, 60, 44), (30, 38, 64), (16, 22, 44),
                   18, alpha=170)
    _blit_ss(surf, scrim, sp.centerx - 30, sp.centery - 22, 60, 44)
    _outlined(surf, SCORE, sp.center, 46, UI_CREAM, NEAR_BLACK, 2, shadow=(2, 3))

    # COINS — small soft ribbon, coin face + count.
    cw = _font(19, True).size(f"{COINS}")[0] + 46
    cp = pygame.Rect(12, 14, cw, 36)
    _ribbon(surf, cp, 16)
    _coin_icon(surf, cp.x + 19, cp.centery, 12)
    _outlined(surf, f"{COINS}", (cp.x + 36 + _font(19, True).size(f"{COINS}")[0] // 2,
              cp.centery), 19, UI_CREAM, (40, 50, 80), 2)

    # PAUSE — soft frosted circle with a cool pause glyph.
    pd = 52
    px, py = W - pd - 10, 12
    cx, cy = px + pd // 2, py + pd // 2
    sh = pygame.Surface((pd + 6, pd + 8), pygame.SRCALPHA)
    pygame.draw.circle(sh, (10, 12, 30, 60), ((pd + 6) // 2, (pd + 8) // 2), pd // 2)
    surf.blit(sh, (px - 3, py + 4))
    disc = _ss_surf(pd, pd)
    n = pd * SS
    for r in range(n // 2, 0, -1):
        t = 1 - r / (n / 2)
        a = int(80 * (1 - 0.3 * t))
        c = lerp_color(_RIBBON_TINT, (210, 214, 226), t)
        pygame.draw.circle(disc, (*c, a), (n // 2, n // 2), r)
    pygame.draw.circle(disc, (*_RIBBON_RIM, 170), (n // 2, n // 2), n // 2, SS)
    _blit_ss(surf, disc, px, py, pd, pd)
    bw, bh, gap = 5, 20, 6
    for dx in (-gap - bw, gap):
        pygame.draw.rect(surf, (44, 56, 92), (cx + dx, cy - bh // 2, bw, bh),
                         border_radius=2)
        pygame.draw.rect(surf, (245, 248, 255), (cx + dx, cy - bh // 2, bw, bh),
                         width=1, border_radius=2)

    # TIMER — soft ribbon capsule with a RECESSED cool track + warm fill.
    bar_w = 132
    bar_h = 22
    icon = 28
    row_w = icon + 8 + bar_w
    base_x = (W - row_w) // 2
    top_y = 132
    frac = PU_REMAIN / PU_TOTAL
    # icon on a soft circle
    icx, icy = base_x + icon // 2, top_y + bar_h // 2
    idisc = _ss_surf(icon, icon)
    pygame.draw.circle(idisc, (*_RIBBON_TINT, 80), (icon * SS // 2, icon * SS // 2),
                       icon * SS // 2)
    pygame.draw.circle(idisc, (*_RIBBON_RIM, 170), (icon * SS // 2, icon * SS // 2),
                       icon * SS // 2, SS)
    _blit_ss(surf, idisc, icx - icon // 2, icy - icon // 2, icon, icon)
    _powerup_icon(surf, PU_KIND, icx, icy, icon - 6)
    bx = base_x + icon + 8
    tr = pygame.Rect(bx, top_y, bar_w, bar_h)
    track = _ss_surf(bar_w, bar_h)
    _vgrad_rounded(track, pygame.Rect(0, 0, bar_w, bar_h), _RIBBON_TRACK,
                   _RIBBON_TRACK_D, bar_h // 2, alpha=215)
    pygame.draw.rect(track, (*_RIBBON_RIM, 150), (0, 0, bar_w * SS, bar_h * SS),
                     width=SS, border_radius=bar_h * SS // 2)
    _blit_ss(surf, track, tr.x, tr.y, bar_w, bar_h)
    fhi, flo = _timer_colors(frac)
    inset = 5
    fillw = int((bar_w - inset * 2) * frac)
    if fillw > 4:
        fill = _ss_surf(fillw, bar_h - inset * 2)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, bar_h - inset * 2), fhi, flo,
                       (bar_h - inset * 2) // 2)
        _blit_ss(surf, fill, bx + inset, tr.y + inset, fillw, bar_h - inset * 2)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (bx + bar_w // 2, tr.centery), 12,
              UI_CREAM, NEAR_BLACK, 1)


# =============================================================================
# CANDIDATE E — "Neon Arcade"
# Punchy modern arcade: dark slate chips with a sharp cut-corner tech frame and
# a bright accent edge (cyan for the system tokens, warm amber for the buff).
# Energetic and clearly NOT the gold-rim-navy baseline. Score in a hard-edged
# slate plate with a cyan underglow; timer track glows teal->amber so it is
# unmistakably an energy bar, never a coin. Pause is a cut-corner power tile.
# =============================================================================
_SLATE = (24, 28, 40)
_SLATE_D = (12, 14, 24)
_NEON_CYAN = (78, 224, 232)
_NEON_AMBER = (255, 176, 64)


def _cut_corner_pts(rect, cut):
    """Octagonal-ish cut-corner rectangle point list (in supersampled space
    when callers multiply by SS). Returns native coords."""
    x, y, w, h = rect
    return [
        (x + cut, y), (x + w - cut, y), (x + w, y + cut), (x + w, y + h - cut),
        (x + w - cut, y + h), (x + cut, y + h), (x, y + h - cut), (x, y + cut),
    ]


def _neon_plate(surf, rect, cut, accent, glow=True):
    """Dark slate cut-corner plate with an accent edge + soft outer glow."""
    if glow:
        g = pygame.Surface((rect.width + 24, rect.height + 24), pygame.SRCALPHA)
        gpts = _cut_corner_pts((12, 12, rect.width, rect.height), cut)
        for i in range(6, 0, -1):
            a = int(50 * i / 6 / 5)
            pygame.draw.polygon(g, (*accent, a), gpts, width=i)
        surf.blit(g, (rect.x - 12, rect.y - 12))
    ss = _ss_surf(rect.width, rect.height)
    ow, oh = rect.width * SS, rect.height * SS
    pts = _cut_corner_pts((0, 0, rect.width, rect.height), cut)
    sspts = [(px * SS, py * SS) for px, py in pts]
    # body gradient via clipped vgrad on a polygon mask
    body = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for yy in range(oh):
        t = yy / max(1, oh - 1)
        c = lerp_color(_SLATE, _SLATE_D, t)
        pygame.draw.line(body, (*c, 235), (0, yy), (ow, yy))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), sspts)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(body, (0, 0))
    # accent edge + a top inner highlight line
    pygame.draw.polygon(ss, (*accent, 255), sspts, width=2 * SS)
    pygame.draw.line(ss, (*accent, 120), sspts[0], sspts[1], SS)
    sh = pygame.Surface((rect.width + 6, rect.height + 8), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 90),
                        _cut_corner_pts((0, 4, rect.width, rect.height), cut))
    surf.blit(sh, (rect.x - 2, rect.y))
    _blit_ss(surf, ss, rect.x, rect.y, rect.width, rect.height)


def cand_neon(surf):
    # SCORE — hard slate plate, cyan edge + underglow, cream numerals.
    sf = _font(46, True)
    sw = max(sf.size(SCORE)[0] + 52, 100)
    sp = pygame.Rect((W - sw) // 2, 68, sw, 54)
    _neon_plate(surf, sp, 12, _NEON_CYAN)
    _outlined(surf, SCORE, sp.center, 46, UI_CREAM, NEAR_BLACK, 2, shadow=(2, 3))

    # COINS — small slate cut-corner chip, coin face + count.
    cw = _font(20, True).size(f"{COINS}")[0] + 44
    cp = pygame.Rect(12, 14, cw, 36)
    _neon_plate(surf, cp, 9, _NEON_CYAN, glow=False)
    _coin_icon(surf, cp.x + 18, cp.centery, 12)
    _outlined(surf, f"{COINS}", (cp.x + 34 + _font(20, True).size(f"{COINS}")[0] // 2,
              cp.centery), 20, UI_GOLD, NEAR_BLACK, 2)

    # PAUSE — cut-corner power tile, cyan glyph.
    pd = 54
    pp = pygame.Rect(W - pd - 10, 12, pd, pd)
    _neon_plate(surf, pp, 12, _NEON_CYAN)
    cx, cy = pp.center
    bw, bh, gap = 6, 22, 6
    for dx in (-gap - bw, gap):
        pygame.draw.rect(surf, _NEON_CYAN, (cx + dx, cy - bh // 2, bw, bh),
                         border_radius=2)
        pygame.draw.rect(surf, (240, 255, 255), (cx + dx + 1, cy - bh // 2 + 1,
                         max(1, bw - 2), 4))

    # TIMER — slate chip + a teal->amber glowing energy track (NOT coin gold).
    bar_w = 132
    bar_h = 18
    icon = 30
    row_w = icon + 8 + bar_w
    base_x = (W - row_w) // 2
    top_y = 132
    frac = PU_REMAIN / PU_TOTAL
    ic = pygame.Rect(base_x, top_y - 6, icon, icon)
    _neon_plate(surf, ic, 8, _NEON_AMBER, glow=False)
    _powerup_icon(surf, PU_KIND, ic.centerx, ic.centery, icon - 8)
    bx = ic.right + 8
    tr = pygame.Rect(bx, top_y, bar_w, bar_h)
    track = _ss_surf(bar_w, bar_h)
    _vgrad_rounded(track, pygame.Rect(0, 0, bar_w, bar_h), (20, 26, 40),
                   (10, 12, 22), bar_h // 2, alpha=240)
    pygame.draw.rect(track, (*_NEON_AMBER, 150), (0, 0, bar_w * SS, bar_h * SS),
                     width=SS, border_radius=bar_h * SS // 2)
    _blit_ss(surf, track, tr.x, tr.y, bar_w, bar_h)
    # energy fill: teal at full -> amber as it drains, with a bright core line
    core = lerp_color(_NEON_AMBER, _NEON_CYAN, frac)
    edge = lerp_color((200, 90, 20), (20, 130, 150), frac)
    inset = 4
    fillw = int((bar_w - inset * 2) * frac)
    if fillw > 4:
        fill = _ss_surf(fillw, bar_h - inset * 2)
        _vgrad_rounded(fill, pygame.Rect(0, 0, fillw, bar_h - inset * 2), core,
                       edge, (bar_h - inset * 2) // 2)
        pygame.draw.line(fill, (255, 255, 255, 180), (2 * SS, 3 * SS),
                         (fillw * SS - 2 * SS, 3 * SS), SS)
        _blit_ss(surf, fill, bx + inset, tr.y + inset, fillw, bar_h - inset * 2)
    _outlined(surf, f"{PU_REMAIN:.1f}s", (bx + bar_w // 2, tr.centery), 11,
              UI_CREAM, NEAR_BLACK, 1)


# ── sheet assembly ──────────────────────────────────────────────────────────
CANDIDATES = [
    ("Floating Ink",
     "No chrome: cream numerals on a soft halo. Alto/Sky minimal.",
     "Timer: icon + thin tick. Pause: hairline ring.", cand_floating),
    ("Sticker Pop",
     "Chunky flat cartoon stickers, heavy ink outlines. Subway/Crossy.",
     "Timer: pill w/ icon medallion. Pause: violet tile.", cand_sticker),
    ("Radial Orbit",
     "A rings kit: timer is a RADIAL countdown sweep around the icon.",
     "Cyan dark discs. Pause + coins are rings too.", cand_orbit),
    ("Sky Ribbon",
     "Airy frosted-translucent ribbons, hairline light rim. Sky vibe.",
     "Timer: recessed cool track. Pause: soft circle.", cand_ribbon),
    ("Neon Arcade",
     "Dark slate cut-corner tech plates, cyan edge + glow.",
     "Timer: teal->amber energy bar (never coin gold).", cand_neon),
]


def _draw_concept_tile(sheet, x, y, name, sub1, sub2, fn, day_bg, night_bg,
                       idx):
    """Draw one concept column: a header, a DAY frame and a NIGHT inset."""
    name_f = _font(18, True)
    sub_f = _font(11, True)
    ni = name_f.render(f"{chr(65 + idx)}.  {name}", True, _GOLD_BRIGHT)
    sheet.blit(ni, (x, y))
    s1 = sub_f.render(sub1, True, UI_CREAM)
    s2 = sub_f.render(sub2, True, UI_ORANGE)
    sheet.blit(s1, (x, y + 23))
    sheet.blit(s2, (x, y + 37))

    # DAY frame (full).
    day = day_bg.copy()
    fn(day)
    fy = y + 54
    sheet.blit(day, (x, fy))
    pygame.draw.rect(sheet, _GOLD_DEEP, (x, fy, W, H), 1)
    dl = sub_f.render("DAY", True, (245, 240, 210))
    sheet.blit(dl, (x + 6, fy + 4))

    # NIGHT inset: just the top band, scaled to the column width and stacked
    # under the day frame (the HUD lives in the top ~160px so a crop is honest).
    night = night_bg.copy()
    fn(night)
    band = night.subsurface((0, 0, W, 200)).copy()
    ny = fy + H + 8
    sheet.blit(band, (x, ny))
    pygame.draw.rect(sheet, _GOLD_DEEP, (x, ny, W, 200), 1)
    nl = sub_f.render("NIGHT (top band)", True, (200, 210, 255))
    sheet.blit(nl, (x + 6, ny + 4))


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    day_bg = build_backdrop(0.0)
    night_bg = build_backdrop(NIGHT_TIME)

    pad = 18
    header_h = 54
    col_gap = 16
    cols = len(CANDIDATES) + 1  # +1 reference column
    col_w = W
    cell_w = col_w + col_gap
    sheet_w = pad + cols * cell_w
    # concept tile height: header + day frame + gap + night band
    tile_h = 54 + H + 8 + 200
    sheet_h = pad + 36 + tile_h + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((16, 13, 28))

    # title strip
    title_f = _font(22, True)
    sub_f = _font(13, True)
    title = title_f.render(
        "Skybit — Gameplay HUD  ·  Round 7  ·  fresh reset (no wood plaques)",
        True, _GOLD_PALE)
    sheet.blit(title, (pad, 10))
    sub = sub_f.render(
        "score 12 · coins x7 · magnet 5.5s/8.0s · each concept shown DAY + "
        "NIGHT · last column = current live HUD",
        True, UI_CREAM)
    sheet.blit(sub, (pad, 36))

    top = pad + 36
    for i, (name, s1, s2, fn) in enumerate(CANDIDATES):
        x = pad + i * cell_w
        _draw_concept_tile(sheet, x, top, name, s1, s2, fn, day_bg, night_bg, i)

    # Reference column — the CURRENT live HUD, day + night.
    rx = pad + len(CANDIDATES) * cell_w
    ref_name_f = _font(18, True)
    ref_sub_f = _font(11, True)
    rn = ref_name_f.render("REF.  Current live HUD", True, (200, 200, 215))
    sheet.blit(rn, (rx, top))
    rs1 = ref_sub_f.render("navy-glass pills + thin gold rim + cream text",
                           True, UI_CREAM)
    rs2 = ref_sub_f.render("the tired baseline — for comparison only",
                           True, (170, 170, 190))
    sheet.blit(rs1, (rx, top + 23))
    sheet.blit(rs2, (rx, top + 37))

    ref_day = current_hud_frame(0.0)
    ref_night = current_hud_frame(NIGHT_TIME)
    fy = top + 54
    sheet.blit(ref_day, (rx, fy))
    pygame.draw.rect(sheet, (110, 110, 130), (rx, fy, W, H), 1)
    dl = ref_sub_f.render("DAY", True, (245, 240, 210))
    sheet.blit(dl, (rx + 6, fy + 4))
    band = ref_night.subsurface((0, 0, W, 200)).copy()
    ny = fy + H + 8
    sheet.blit(band, (rx, ny))
    pygame.draw.rect(sheet, (110, 110, 130), (rx, ny, W, 200), 1)
    nl = ref_sub_f.render("NIGHT (top band)", True, (200, 210, 255))
    sheet.blit(nl, (rx + 6, ny + 4))

    pygame.image.save(sheet, OUT)
    print(f"saved {OUT}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
