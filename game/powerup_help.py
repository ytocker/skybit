"""
Power-ups explainer screen — shown once at the end of the intro cinematic.

Layout matches the chosen candidate (candidate_2_grid): gold-on-red
"POWER-UPS" title, 2x3 card grid for the six real kinds, a wide footer
card for the surprise gift box, and an "EFFECTS LAST 8 SECONDS" footer.

Lifecycle:
  * Built when the intro auto-completes (not when the user skips it).
  * Renders deterministically — the only animated element is the
    twinkling star field, driven by an internal time counter.
  * Any tap during this state advances to STATE_MENU.
"""
from __future__ import annotations

import math
import random
import pygame

from game.config import W, H
from game.draw import (
    rounded_rect, lerp_color,
    UI_CREAM, NEAR_BLACK, WHITE,
)
from game.hud import (
    _font, _draw_overlay_stars,
    _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP, _ORANGE_BORDER, _RED_OUTLINE,
    _PANEL_DARK, _PANEL_LIGHTER,
)
from game.entities import PowerUp


# Duration is reported once in the footer, never per-row.
POWERUPS = (
    ("triple",   "TRIPLE",   "Coins are worth 3x"),
    ("magnet",   "MAGNET",   "Pulls nearby coins"),
    ("slowmo",   "SLOW-MO",  "Slows the world, jumps are the same"),
    ("kfc",      "KFC",      "Fried chicken theme"),
    ("ghost",    "GHOST",    "Go through pillars safely"),
    ("shrink",   "SHRINK",   "0.6x smaller"),
    ("surprise", "SURPRISE", "Picks random from above"),
)


# ── one-time star field ─────────────────────────────────────────────────────
def _seeded_stars():
    rng = random.Random(22)
    return [
        (rng.randint(8, W - 8), rng.randint(8, H - 30),
         rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28))
        for _ in range(60)
    ]


# ── helpers ─────────────────────────────────────────────────────────────────
def _gradient_bg(surf):
    TOP = (8, 4, 32)
    MID = (16, 8, 50)
    BOT = (24, 14, 70)
    h = surf.get_height()
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.5:
            c = lerp_color(TOP, MID, t * 2)
        else:
            c = lerp_color(MID, BOT, (t - 0.5) * 2)
        pygame.draw.line(surf, c, (0, y), (surf.get_width() - 1, y))


def _outlined_title(surf, txt, center, size, px, shadow_offset):
    f = _font(size, True)
    img = f.render(txt, True, _GOLD_BRIGHT)
    out = f.render(txt, True, _RED_OUTLINE)
    sh = f.render(txt, True, NEAR_BLACK)
    r = img.get_rect(center=center)
    for ox, oy in ((-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)):
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + shadow_offset[0], r.y + shadow_offset[1]))
    surf.blit(img, r.topleft)


_PANEL_OS = 4  # supersample factor for the card frame


def _panel_body_gradient(pnl, ow, oh, orad, alpha):
    """Faint vertical lift on the card body — top a touch brighter than the
    floor — so the tile reads as gently lit. The swing is held to ~11% of
    the _PANEL_DARK→_PANEL_LIGHTER span and anchored on _PANEL_DARK so the
    interior never drops below the flat panel tone under the blurb
    (legibility) and never bands at downscale."""
    top = lerp_color(_PANEL_DARK, _PANEL_LIGHTER, 0.11)
    grad = pygame.Surface((ow, oh), pygame.SRCALPHA)
    for y in range(oh):
        c = lerp_color(top, _PANEL_DARK, y / max(1, oh - 1))
        pygame.draw.line(grad, (*c, alpha), (0, y), (ow - 1, y))
    mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ow, oh),
                     border_radius=orad)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    pnl.blit(grad, (0, 0))


def _panel_two_tone_rim(pnl, ow, oh, orad, os_):
    """Metallic 2px rim: a _GOLD_DEEP under-ply (the milled shadow side) with
    a _GOLD_BRIGHT top ply pulled in 1px so a sliver of the deep edge shows.
    Held to a 2px weight at sub-opaque alpha so a grid of six cards doesn't
    read as a wall of gold."""
    pygame.draw.rect(pnl, (*_GOLD_DEEP, 200), (0, 0, ow, oh),
                     width=2 * os_, border_radius=orad)
    pygame.draw.rect(pnl, (*_GOLD_BRIGHT, 175),
                     (os_, os_, ow - 2 * os_, oh - 2 * os_),
                     width=os_, border_radius=max(1, orad - os_))


def _panel_inner_bevel(pnl, ow, oh, orad, os_):
    """The detail that sells the raise: a pale highlight wrapping the
    top-left inner edge and a pure-black accent wrapping the bottom-right,
    one px inboard of the rim, as if lit from top-left. Pure black (not the
    near-black panel ink, which is a hair lighter than the floor and would
    vanish) is the only value that actually recedes below the interior. A
    full rounded stroke split by a diagonal mask keeps the bevel following
    the corner radius cleanly."""
    inset = 3 * os_
    bw = 3  # pre-scale stroke; resolves to a clean ~1px line after downscale
    band = (inset, inset, ow - 2 * inset, oh - 2 * inset)
    brad = max(1, orad - inset)

    def _half(color, alpha, top_left):
        layer = pygame.Surface((ow, oh), pygame.SRCALPHA)
        pygame.draw.rect(layer, (*color, alpha), band, width=bw,
                         border_radius=brad)
        mask = pygame.Surface((ow, oh), pygame.SRCALPHA)
        tri = ([(0, 0), (ow, 0), (0, oh)] if top_left
               else [(ow, 0), (ow, oh), (0, oh)])
        pygame.draw.polygon(mask, (255, 255, 255, 255), tri)
        layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pnl.blit(layer, (0, 0))

    _half(_GOLD_PALE, 115, top_left=True)
    _half((0, 0, 0), 85, top_left=False)


def _dark_panel(surf, rect, radius, alpha):
    """Gold-trimmed Pip Scarlet card — the frame around each power-up tile.
    A "raised metal" treatment: a faint lit body gradient, a two-tone
    metallic rim, and an inner light/dark bevel so the tile sits up off the
    night-sky field. Composited at ``_PANEL_OS``× then smoothscaled so every
    edge reads crisp at the native 360 px canvas. Kept local to avoid a
    circular import with hud (derives from tools/gen_scarlet_set.py::card)."""
    os_ = _PANEL_OS
    ow, oh = rect.width * os_, rect.height * os_
    orad = radius * os_
    pnl = pygame.Surface((ow, oh), pygame.SRCALPHA)
    _panel_body_gradient(pnl, ow, oh, orad, alpha)
    _panel_two_tone_rim(pnl, ow, oh, orad, os_)
    _panel_inner_bevel(pnl, ow, oh, orad, os_)
    surf.blit(pygame.transform.smoothscale(pnl, rect.size), rect.topleft)


_PULSE_FOR_ICON = 1.6
# Each in-world PowerUp.draw applies a per-kind vertical bob driven by
# `self.pulse` so the floating sprite waftily rises and falls during
# play. In static icon contexts (help cards, run-summary chips) the
# bob makes the icon sit visibly low on its anchor point — most
# noticeably the ghost, whose bob sums two sin terms (~+4 px at the
# canonical pulse of 1.6). We compute the bob analytically per kind
# and subtract it from the blit center so the rendered icon visually
# centers on (cx, cy) regardless of where in its idle-cycle it sits.
_ICON_BOB_AT_PULSE = {
    "ghost":    math.sin(_PULSE_FOR_ICON * 0.9) * 4
              + math.sin(_PULSE_FOR_ICON * 1.8) * 1.5,
    "magnet":   math.sin(_PULSE_FOR_ICON * 1.1) * 3,
    "megamagnet": math.sin(_PULSE_FOR_ICON * 1.1) * 3,
    "slowmo":   math.sin(_PULSE_FOR_ICON * 0.7) * 3,
    "kfc":      math.sin(_PULSE_FOR_ICON * 0.9) * 2.5,
    "surprise": math.sin(_PULSE_FOR_ICON * 0.7) * 2,
    "shrink":   math.sin(_PULSE_FOR_ICON * 1.1) * 2,
    # Secret kinds are not documented on the help screen, but keep their bob
    # offsets here so any icon render (e.g. debug) stays visually centered.
    "genie":    math.sin(_PULSE_FOR_ICON * 0.9) * 2,
    "skateboard": math.sin(_PULSE_FOR_ICON * 1.0) * 2,
    "knight":   math.sin(_PULSE_FOR_ICON * 0.9) * 2,
}


def _powerup_icon(surf, kind, cx, cy, size_px):
    """Render the in-world PowerUp sprite at native ~28px footprint, then
    smoothscale to size_px. Keeps the procedural detail pixel-true.
    Compensates for the kind's bob so the icon visually centers on
    (cx, cy) — see ``_ICON_BOB_AT_PULSE``."""
    small = pygame.Surface((64, 64), pygame.SRCALPHA)
    p = PowerUp(32, 32, kind)
    p.pulse = _PULSE_FOR_ICON
    p.draw(small)
    big = pygame.transform.smoothscale(small, (size_px, size_px))
    bob = _ICON_BOB_AT_PULSE.get(kind, 0.0)
    y_adj = -int(round(bob * size_px / 64))
    surf.blit(big, big.get_rect(center=(cx, cy + y_adj)))


def _wrap(font_obj, blurb, max_w):
    words = blurb.split()
    cur = ""
    lines = []
    for w in words:
        test = (cur + " " + w).strip()
        if font_obj.size(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ── scene class ─────────────────────────────────────────────────────────────
class PowerUpHelpScene:
    """Owns the entire frame for STATE_POWERUPS. The App's `_render` hands
    the screen surface to `render`. Any tap routes to STATE_MENU via the
    App's `_flap_input`, not this class."""

    def __init__(self) -> None:
        self.t = 0.0
        self._stars = _seeded_stars()

    def update(self, dt: float) -> None:
        self.t += dt

    def render(self, surf: pygame.Surface) -> None:
        _gradient_bg(surf)
        _draw_overlay_stars(surf, self._stars, self.t + 1.4)

        _outlined_title(surf, "POWER-UPS", (W // 2, 36),
                        size=32, px=2, shadow_offset=(2, 3))
        _outlined_title(surf, "COLLECT  TO  BOOST", (W // 2, 70),
                        size=14, px=1, shadow_offset=(1, 2))
        # Divider under the subtitle to mirror the menu/run-summary lockup.
        pygame.draw.line(surf, (*_GOLD_BRIGHT, 130),
                         (W // 2 - 60, 90),
                         (W // 2 + 60, 90), 1)

        # 2x3 grid for the six real kinds.
        grid_top = 110
        card_w = 162
        card_h = 124
        gap = 8
        base_x = (W - (card_w * 2 + gap)) // 2

        for idx, (kind, name, blurb) in enumerate(POWERUPS[:6]):
            col = idx % 2
            row = idx // 2
            x = base_x + col * (card_w + gap)
            y = grid_top + row * (card_h + gap)
            card = pygame.Rect(x, y, card_w, card_h)
            _dark_panel(surf, card, radius=14, alpha=215)

            _powerup_icon(surf, kind, card.centerx, card.y + 32, 48)
            nimg = _font(14, True).render(name, True, _GOLD_BRIGHT)
            surf.blit(nimg, nimg.get_rect(center=(card.centerx, card.y + 66)))

            f = _font(12, True)
            for li, line in enumerate(_wrap(f, blurb, card_w - 16)[:3]):
                img = f.render(line, True, UI_CREAM)
                surf.blit(img,
                          img.get_rect(center=(card.centerx,
                                               card.y + 84 + li * 14)))

        # Wide surprise card sitting below the grid.
        sy = grid_top + 3 * (card_h + gap) + 4
        surprise_card = pygame.Rect(base_x, sy, card_w * 2 + gap, 64)
        _dark_panel(surf, surprise_card, radius=14, alpha=220)
        _powerup_icon(surf, "surprise",
                      surprise_card.x + 40, surprise_card.centery, 50)
        nimg = _font(15, True).render("SURPRISE", True, _GOLD_BRIGHT)
        surf.blit(nimg, (surprise_card.x + 80, surprise_card.y + 10))

        f = _font(12, True)
        blurb = POWERUPS[-1][2]
        text_left = surprise_card.x + 80
        text_right = surprise_card.right - 12
        for li, line in enumerate(_wrap(f, blurb, text_right - text_left)[:2]):
            img = f.render(line, True, UI_CREAM)
            surf.blit(img, (text_left, surprise_card.y + 32 + li * 14))

        # Footer: duration applies to every effect.
        pygame.draw.line(surf, (*_ORANGE_BORDER, 110),
                         (W // 2 - 80, H - 36), (W // 2 + 80, H - 36), 1)
        foot = _font(12, True).render("EFFECTS LAST 8 SECONDS",
                                      True, _GOLD_BRIGHT)
        foot.set_alpha(230)
        surf.blit(foot, foot.get_rect(center=(W // 2, H - 22)))
