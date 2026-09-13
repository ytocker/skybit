"""Top-left slot-machine renderer for the LOTTERY power-up reveal.

The reveal animation runs in the corner of the HUD rather than over the
bird so it never sits in the pillar-approach lane. Compact ~124x82 px
cabinet; three reels lock in stagger (0.5 s, 0.7 s, 0.9 s into the
animation) so by LOTTERY_REVEAL_TIME (1.0 s) all three symbols are
visible and the result strip flips from "LOTTERY" to the tier label.

Symbol -> tier mapping mirrors the design mock-ups under
archive/lottery_design/ and the LOTTERY_TIERS in config.py:

    $ $ $   ->  JACKPOT
    7 7 7   ->  BIG WIN
    * * *   ->  WIN
    mixed   ->  NOTHING
    X X *   ->  LOSS
    X X X   ->  BUST

All sprites are drawn from code (no PNG assets) per the project's
procedural-art rule. Symbol surfaces are built once on first use and
re-blit each frame — keeps the per-frame cost flat across the ~2.2 s
the animation is on screen.

Reveal feedback is asymmetric: positive tiers get confetti pouring out
the bottom of the cabinet; negative tiers and NOTHING stay quiet. The
result strip's sign-tinted rim already signals win-vs-loss, so the
confetti reads as pure celebration on top.
"""
from __future__ import annotations

import math
import random
from typing import Callable

import pygame

from game.hud import _font

# ── palette (matches the score-plaque recipe in hud.py) ─────────────────────
_CREAM_FACE   = (252, 244, 220)
_RIM_GOLD     = (180, 130,  20)
_RIM_RED      = (140,  25,  18)
_RIM_NEUTRAL  = (110,  80,  30)
_NEAR_BLACK   = ( 15,  15,  30)
_GOLD_BRIGHT  = (240, 192,  64)
_GOLD_DEEP    = (180, 130,  20)
_GOLD_PALE    = (255, 232, 168)
_RED_OUTLINE  = (168,  32,  16)
_RED_DEEP     = (110,  18,  10)
_CREAM        = (245, 230, 200)

# Cabinet footprint in the top-left, anchored just BELOW the coins pill
# (10..70, 14..44 in hud.draw_play). The body reclaims the pixels the
# old drop shadow used to occupy (3 px each side, 10 px below the
# original 118x72 body) so the panel reads a touch larger without a
# separate shadow. The HUD also draws after this renderer, so any
# incidental overlap is the HUD on top of us — never the reverse.
CAB_X, CAB_Y = 5, 48
CAB_W, CAB_H = 124, 82


# ── engraved text (cream face + tinted rim + dark shadow) ───────────────────
def _engraved_text(text: str, size: int,
                   rim: tuple[int, int, int] = _RIM_GOLD,
                   face: tuple[int, int, int] = _CREAM_FACE
                   ) -> pygame.Surface:
    f = _font(size, True)
    face_img = f.render(text, True, face)
    rim_img  = f.render(text, True, rim)
    sh_img   = f.render(text, True, _NEAR_BLACK)
    pad = 4
    w = face_img.get_width() + pad * 2
    h = face_img.get_height() + pad * 2
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    sh_img.set_alpha(170)
    s.blit(sh_img, (pad + 1, pad + 2))
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            if ox or oy:
                s.blit(rim_img, (pad + ox, pad + oy))
    s.blit(face_img, (pad, pad))
    return s


# ── reel symbols (cached on first build) ────────────────────────────────────
_sym_cache: dict[tuple[str, int], pygame.Surface] = {}


def _sym_dollar(size: int) -> pygame.Surface:
    key = ("$", size)
    s = _sym_cache.get(key)
    if s is None:
        s = _engraved_text("$", size, rim=_RIM_GOLD, face=(240, 200, 80))
        _sym_cache[key] = s
    return s


def _sym_seven(size: int) -> pygame.Surface:
    key = ("7", size)
    s = _sym_cache.get(key)
    if s is None:
        s = _engraved_text("7", size, rim=_RIM_RED, face=(220, 60, 50))
        _sym_cache[key] = s
    return s


def _sym_star(size: int) -> pygame.Surface:
    """Five-point gold star polygon — clearer than a "*" glyph at small
    sizes."""
    key = ("*", size)
    s = _sym_cache.get(key)
    if s is not None:
        return s
    pad = 4
    outer = size // 2
    inner = max(2, outer // 2)
    cx = cy = outer + pad
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        r = outer if k % 2 == 0 else inner
        pts.append((cx + math.cos(ang) * r,
                    cy + math.sin(ang) * r))
    s = pygame.Surface((outer * 2 + pad * 2, outer * 2 + pad * 2),
                       pygame.SRCALPHA)
    sh_pts = [(x + 1, y + 2) for (x, y) in pts]
    pygame.draw.polygon(s, (0, 0, 0, 150), sh_pts)
    pygame.draw.polygon(s, (255, 210, 90), pts)
    pygame.draw.polygon(s, _RIM_GOLD, pts, 1)
    inner_pts = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55)
                 for (x, y) in pts]
    pygame.draw.polygon(s, (255, 240, 180), inner_pts[:5], 0)
    _sym_cache[key] = s
    return s


def _sym_skull(size: int) -> pygame.Surface:
    """Bone-coloured skull — drawn from code so it stays sharp at any
    target reel size."""
    key = ("X", size)
    s = _sym_cache.get(key)
    if s is not None:
        return s
    sz = size + 6
    s = pygame.Surface((sz, sz), pygame.SRCALPHA)
    cx = cy = sz // 2
    skull_r = size // 2
    pygame.draw.circle(s, (0, 0, 0, 150), (cx + 1, cy + 1), skull_r + 1)
    pygame.draw.circle(s, (235, 230, 210), (cx, cy - 1), skull_r)
    pygame.draw.circle(s, ( 90,  60,  40), (cx, cy - 1), skull_r, 1)
    jaw_w = skull_r
    jaw = [
        (cx - jaw_w // 2,       cy + skull_r - 2),
        (cx + jaw_w // 2,       cy + skull_r - 2),
        (cx + jaw_w // 2 - 1,   cy + skull_r + 3),
        (cx - jaw_w // 2 + 1,   cy + skull_r + 3),
    ]
    pygame.draw.polygon(s, (235, 230, 210), jaw)
    pygame.draw.polygon(s, ( 90,  60,  40), jaw, 1)
    eye_r = max(2, skull_r // 3)
    pygame.draw.circle(s, (40, 20, 30), (cx - skull_r // 2 + 1, cy - 1), eye_r)
    pygame.draw.circle(s, (40, 20, 30), (cx + skull_r // 2 - 1, cy - 1), eye_r)
    nose = [(cx, cy + 1), (cx - 1, cy + 3), (cx + 1, cy + 3)]
    pygame.draw.polygon(s, (40, 20, 30), nose)
    for tx in (cx - 2, cx, cx + 2):
        pygame.draw.line(s, (90, 60, 40),
                         (tx, cy + skull_r - 1),
                         (tx, cy + skull_r + 2), 1)
    _sym_cache[key] = s
    return s


_SYM_FN: dict[str, Callable[[int], pygame.Surface]] = {
    "$": _sym_dollar,
    "7": _sym_seven,
    "*": _sym_star,
    "X": _sym_skull,
}

# Tier label -> (reel_0, reel_1, reel_2). NOTHING is intentionally three
# different symbols so the player sees "almost" a match.
_TIER_COMBOS = {
    "JACKPOT": ("$", "$", "$"),
    "BIG WIN": ("7", "7", "7"),
    "WIN":     ("*", "*", "*"),
    "NOTHING": ("$", "7", "*"),
    "LOSS":    ("X", "X", "*"),
    "BUST":    ("X", "X", "X"),
}

# Cycled by the spinning reels before they lock.
_SPIN_CYCLE = ("$", "7", "*", "X", "7", "$")


# ── effect helpers ──────────────────────────────────────────────────────────
def _rim_for_delta(d: int) -> tuple[int, int, int]:
    if d > 0:
        return _RIM_GOLD
    if d < 0:
        return _RIM_RED
    return _RIM_NEUTRAL


def _confetti_burst(surf, cx, cy, t, seed):
    """Deterministic celebratory spray. Seeded so the same JACKPOT
    plays the same confetti pattern run-to-run, which keeps the
    proof-chain test deterministic."""
    rng = random.Random(seed)
    n = 50
    for _ in range(n):
        ang = rng.uniform(0, math.tau)
        speed = rng.uniform(40, 220)
        col = rng.choice(((240, 192, 64), (255, 232, 168),
                          (245, 230, 200), (255, 155, 30),
                          (168, 32, 16)))
        d = speed * t
        x = cx + math.cos(ang) * d
        y = cy + math.sin(ang) * d - 60 * t * t
        sz = rng.choice((2, 3, 4))
        if rng.random() < 0.5:
            pygame.draw.circle(surf, col, (int(x), int(y)), sz // 2 + 1)
        else:
            pygame.draw.rect(surf, col, (int(x), int(y), sz, sz))


# ── cabinet renderer ────────────────────────────────────────────────────────
def _draw_cabinet(surf, t, *, locked_tier, reel_progress):
    cabinet = pygame.Rect(CAB_X, CAB_Y, CAB_W, CAB_H)

    # Cabinet body — red outer / gold middle / dark inner.
    pygame.draw.rect(surf, _RED_OUTLINE, cabinet, border_radius=8)
    pygame.draw.rect(surf, _GOLD_DEEP, cabinet.inflate(-4, -4),
                     border_radius=6)
    pygame.draw.rect(surf, (16, 10, 36), cabinet.inflate(-10, -10),
                     border_radius=5)

    # Marquee.
    marquee = pygame.Rect(cabinet.x + 6, cabinet.y + 5,
                          cabinet.width - 12, 14)
    pygame.draw.rect(surf, _RED_DEEP, marquee, border_radius=3)
    pygame.draw.rect(surf, _GOLD_BRIGHT, marquee, width=1, border_radius=3)
    for i in range(7):
        bx = marquee.x + 6 + i * (marquee.width - 12) // 6
        on = (int(t * 8) + i) % 2 == 0
        pygame.draw.circle(surf, _GOLD_PALE if on else _GOLD_DEEP,
                           (bx, marquee.y + 2), 1)
    lbl = _engraved_text("LOTTERY", 11, rim=_RIM_GOLD)
    surf.blit(lbl, lbl.get_rect(center=marquee.center))

    # Reels. Three equal wheels centred in the cabinet: equal side
    # margins and inter-reel gaps (10 px each -> 10+28+10+28+10+28+10 =
    # 124 = cabinet width). reel_y + the matching gaps centre the band
    # vertically between the marquee and the result strip.
    reel_w, reel_h = 28, 32
    reel_y = marquee.bottom + 6
    reels_x0 = cabinet.x + 10
    reel_gap = 10

    for i in range(3):
        rx = reels_x0 + i * (reel_w + reel_gap)
        reel = pygame.Rect(rx, reel_y, reel_w, reel_h)
        pygame.draw.rect(surf, _CREAM, reel, border_radius=3)
        pygame.draw.rect(surf, _GOLD_DEEP, reel, width=1, border_radius=3)
        for k in range(3):
            a = max(0, 60 - k * 20)
            pygame.draw.line(surf, (0, 0, 0, a),
                             (reel.x + 1, reel.y + 1 + k),
                             (reel.right - 1, reel.y + 1 + k))

        if reel_progress[i] >= 1.0 and locked_tier is not None:
            sym = _SYM_FN[_TIER_COMBOS[locked_tier][i]](18)
            surf.blit(sym, sym.get_rect(center=reel.center))
        else:
            speed = 14 + i * 2
            offset = (t * speed * (reel_h - 6)) % (reel_h - 6)
            for k in (-1, 0, 1, 2):
                idx = (int(t * speed) + k + i) % len(_SPIN_CYCLE)
                sym = _SYM_FN[_SPIN_CYCLE[idx]](15)
                sy = reel.y + 6 + k * (reel_h - 6) - int(offset)
                if -14 < sy - reel.y < reel.height:
                    sub_rect = sym.get_rect(center=(reel.centerx,
                                                    sy + sym.get_height() // 2))
                    clip = sub_rect.clip(reel)
                    if clip.width > 0 and clip.height > 0:
                        ox = (clip.x - sub_rect.x, clip.y - sub_rect.y)
                        surf.blit(sym, clip.topleft,
                                  pygame.Rect(ox, clip.size))
            streak = pygame.Surface((reel.width - 4, reel.height - 4),
                                    pygame.SRCALPHA)
            for s_y in range(0, reel.height, 4):
                streak.fill((255, 255, 255, 25),
                            (0, s_y, reel.width - 4, 1))
            surf.blit(streak, (reel.x + 2, reel.y + 2))

    # Pay-line.
    pl_y = reel_y + reel_h // 2
    pygame.draw.line(surf, _GOLD_BRIGHT,
                     (reels_x0 - 2, pl_y),
                     (reels_x0 + 3 * reel_w + 2 * reel_gap + 2, pl_y), 1)

    # Result strip — "LOTTERY" + three "?" hints during the spin,
    # tier name + value at reveal with sign-tinted rim.
    strip = pygame.Rect(cabinet.x + 8, reel_y + reel_h + 6,
                        cabinet.width - 16, 14)
    if locked_tier is None:
        pygame.draw.rect(surf, (8, 6, 22), strip, border_radius=3)
        pygame.draw.rect(surf, _GOLD_DEEP, strip, width=1, border_radius=3)
        q = _engraved_text("?", 11, rim=_RIM_GOLD)
        for x in (strip.x + 10, strip.centerx, strip.right - 10):
            surf.blit(q, q.get_rect(center=(x, strip.centery)))


def _draw_result_strip(surf, tier, delta):
    """Cream pill with tier name + value. Rim tinted by sign so the
    player's eye catches win-vs-loss before parsing the digits. Layout
    math here mirrors _draw_cabinet (top_pad 5 + marquee 14 + gap 6 +
    reel_h 32 + gap 6) — keep them in sync if either is retuned."""
    cabinet = pygame.Rect(CAB_X, CAB_Y, CAB_W, CAB_H)
    reel_y = cabinet.y + 5 + 14 + 6
    strip = pygame.Rect(cabinet.x + 8, reel_y + 32 + 6,
                        cabinet.width - 16, 14)
    rim = _rim_for_delta(delta)
    pygame.draw.rect(surf, _CREAM_FACE, strip,
                     border_radius=strip.height // 2)
    pygame.draw.rect(surf, rim, strip, width=1,
                     border_radius=strip.height // 2)
    tname_img = _engraved_text(tier, 10, rim=rim)
    if delta > 0:
        v_str = f"+{delta}"
    elif delta < 0:
        v_str = str(delta)
    else:
        v_str = "0"
    vstr_img = _engraved_text(v_str, 11, rim=rim)
    gap = 4
    total_w = tname_img.get_width() + gap + vstr_img.get_width()
    start_x = strip.centerx - total_w // 2
    surf.blit(tname_img, tname_img.get_rect(
        midleft=(start_x, strip.centery)))
    surf.blit(vstr_img, vstr_img.get_rect(
        midleft=(start_x + tname_img.get_width() + gap - 4,
                 strip.centery)))


def draw_reveal(surf, anim):
    """Render the slot-machine reveal for ``World.lottery_anim``.

    The anim dict carries:
        t        seconds since the powerup was picked up
        tier     label from LOTTERY_TIERS (one of JACKPOT/BIG WIN/WIN/
                 NOTHING/LOSS/BUST)
        delta    coin delta to apply when reveal lands
        x, y     legacy pickup position — unused now (cabinet is at a
                 fixed top-left anchor)
        applied  whether World already applied the score delta
    """
    from game.config import LOTTERY_REVEAL_TIME

    t = anim["t"]
    tier = anim["tier"]
    delta = anim["delta"]

    # Each reel locks at a fraction of LOTTERY_REVEAL_TIME — by the
    # full reveal time all three are settled.
    stops = (LOTTERY_REVEAL_TIME * 0.5,
             LOTTERY_REVEAL_TIME * 0.7,
             LOTTERY_REVEAL_TIME * 0.9)
    reel_progress = tuple(1.0 if t >= s else (t / s) for s in stops)
    locked_tier = tier if t >= stops[-1] else None

    _draw_cabinet(surf, t,
                  locked_tier=locked_tier,
                  reel_progress=reel_progress)
    if locked_tier is not None:
        _draw_result_strip(surf, tier, delta)

    # Confetti pours from the bottom of the cabinet once all three reels
    # lock on a positive tier. Negative tiers and NOTHING stay quiet —
    # the result strip's red-tinted rim already carries the sting.
    if t >= LOTTERY_REVEAL_TIME and delta > 0:
        seed_for_tier = {"JACKPOT": 11, "BIG WIN": 12, "WIN": 13}.get(
            tier, 11)
        _confetti_burst(surf, CAB_X + CAB_W // 2,
                        CAB_Y + CAB_H + 6,
                        (t - LOTTERY_REVEAL_TIME) * 8,
                        seed=seed_for_tier)
