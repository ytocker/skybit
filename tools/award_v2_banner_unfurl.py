"""award_interstitial_v2 / banner-unfurl — heraldic textile commendation.

A long vertical heraldic BANNER drops from offscreen-top: a hanging navy/gold
weave cloth with sine-waved side edges and a notched foot, the REAL gold/navy
hero medallion pinned at its head like a medal on a sash, a second campaign
medal pinned below it (the 2-unlock multiplicity cue), the engraved gold title
woven down the cloth, and scarlet tassels at the foot. Scratch tooling only —
nothing here is imported by the game; game/ is untouched.
"""
import os
import math

import pygame

from tools.unlock_notice_common import render_backdrop, demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import (blit_glow, make_gradient_surface, lerp_color)
from game.hud import (_font, _outlined_text, _pill_btn,
                      _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H


# Cloth weave — kept DEEP and DULL so the gold pin stays the brightest object.
_CLOTH_TOP = (24, 20, 70)     # lit head of the banner
_CLOTH_MID = (17, 13, 52)     # body navy
_CLOTH_BOT = (10, 7, 34)      # shadowed foot
_CLOTH_EDGE_HI = (54, 44, 112)  # raised weave highlight at the sun-side edge
_CLOTH_EDGE_LO = (6, 4, 22)     # shade-side fold

# Heraldic gold trim braid running the cloth borders (muted, not focal).
_BRAID_HI = (188, 146, 56)
_BRAID_LO = (96, 66, 18)

# Scarlet reserved for tassels + foot fringe ONLY.
_SCARLET = (172, 34, 30)
_SCARLET_HI = (212, 64, 56)
_SCARLET_LO = (104, 18, 18)


def _vignette(surf):
    """Deep-night vignette so the lit banner column reads as a spotlit relic."""
    vg = pygame.Surface((W, H), pygame.SRCALPHA)
    cx, cy = W // 2, int(H * 0.34)
    maxd = math.hypot(W, H) * 0.62
    for ring in range(0, int(maxd), 6):
        t = ring / maxd
        a = int(150 * (t ** 1.7))
        pygame.draw.circle(vg, (0, 0, 0, a), (cx, cy), int(maxd - ring), 7)
    surf.blit(vg, (0, 0))


def _banner_edge(y, top, bot, base_half, sway_px):
    """Half-width of the hanging cloth at row ``y`` — a gentle sine sway gives
    the silhouette the soft billow of cloth hung from a pole rather than a
    rigid rectangle. Narrows slightly toward the foot like a weighted drape."""
    span = max(1, bot - top)
    f = (y - top) / span
    taper = 1.0 - 0.06 * f
    sway = math.sin(f * math.pi * 1.6 + 0.4) * sway_px * (0.4 + 0.6 * f)
    return base_half * taper + sway


def draw_banner(surf):
    top, bot = -6, 532            # hangs from offscreen-top down to the foot
    cx = W // 2 - 4              # slightly left of centre per brief
    base_half = 86
    sway_px = 7.0

    # Soft cloth shadow cast on the night behind the drape (depth off the wall).
    sh = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, bot + 26):
        hw = _banner_edge(y, top, bot, base_half, sway_px)
        a = int(70 * min(1.0, y / 120))
        pygame.draw.line(sh, (0, 0, 0, a),
                         (cx - hw + 10, y + 12), (cx + hw + 12, y + 12))
    surf.blit(sh, (0, 0))

    # Pre-rendered vertical weave gradient, then carved to the swayed silhouette
    # row by row so the cloth keeps its lit-head→shadow-foot ramp.
    grad = make_gradient_surface(base_half * 2 + 24, bot - top + 8,
                                 [(0.0, _CLOTH_TOP), (0.42, _CLOTH_MID),
                                  (1.0, _CLOTH_BOT)])
    for y in range(top + 1, bot):
        hw = _banner_edge(y, top, bot, base_half, sway_px)
        gy = min(grad.get_height() - 1, max(0, y - top))
        # sample the gradient's centre colour for this row
        base = grad.get_at((grad.get_width() // 2, gy))
        f = (y - top) / max(1, bot - top)
        left = int(cx - hw)
        right = int(cx + hw)
        # Cross-sash shading: a soft cylindrical light — brighter on the sun
        # (right) side, falling into shade at the shade (left) edge — so the
        # cloth reads as a hanging drape with body, not a flat panel.
        for x in range(left, right + 1):
            u = (x - left) / max(1, right - left)        # 0=shade edge, 1=sun
            shade = math.sin(u * math.pi)                # bright mid, dim edges
            col = lerp_color(_CLOTH_EDGE_LO, base, 0.45 + 0.55 * shade)
            col = lerp_color(col, _CLOTH_EDGE_HI, 0.18 * max(0.0, u - 0.55))
            surf.set_at((x, y), col)
        # faint interior weave ribs (slow vertical undulation) so it isn't flat
        rib = math.sin(f * math.pi * 7.0)
        for rx in (cx - 30, cx - 4, cx + 22):
            surf.set_at((int(rx + rib * 3), y),
                        lerp_color(base, _CLOTH_EDGE_HI, 0.22)) if y % 4 else None

    # Continuous gold braid trim running both long edges — a twist-rope of two
    # offset highlight beads so it reads as a woven cord, not a dashed line.
    for y in range(top + 2, bot):
        hw = _banner_edge(y, top, bot, base_half, sway_px)
        f = (y - top) / max(1, bot - top)
        dull = 0.22 + 0.34 * f                            # fade toward the foot
        twist = math.sin(y * 0.5)                         # rope twist phase
        for sgn in (-1, 1):
            ex = int(cx + sgn * (hw - 4))
            core = lerp_color(_BRAID_LO, _CLOTH_BOT, dull)
            pygame.draw.line(surf, core, (ex - 2, y), (ex + 2, y))
            hi = lerp_color(_BRAID_HI, _CLOTH_BOT, dull * 0.7)
            surf.set_at((ex + (1 if twist > 0 else -1), y), hi)

    # Notched/triangulated foot — a pointed pennant tail with a centre swallow
    # tail, plus a repeated triangle engrave just above it (heraldic dagging).
    hw_foot = _banner_edge(bot - 1, top, bot, base_half, sway_px)
    foot_pts = [
        (cx - hw_foot, bot - 1),
        (cx - hw_foot * 0.5, bot + 26),
        (cx, bot + 6),                      # centre swallowtail notch
        (cx + hw_foot * 0.5, bot + 26),
        (cx + hw_foot, bot - 1),
    ]
    pygame.draw.polygon(surf, _CLOTH_BOT, [(int(x), int(y)) for x, y in foot_pts])
    pygame.draw.polygon(surf, _BRAID_LO,
                        [(int(x), int(y)) for x, y in foot_pts], 2)
    # dagging triangles above the foot
    n = 7
    for i in range(n):
        tx = cx - hw_foot + (2 * hw_foot) * (i + 0.5) / n
        pygame.draw.polygon(surf, lerp_color(_BRAID_LO, _CLOTH_BOT, 0.3),
                            [(tx - 7, bot - 12), (tx + 7, bot - 12),
                             (tx, bot - 1)])

    return cx, top, bot, base_half, sway_px, hw_foot


def draw_tassels(surf, cx, bot, hw_foot):
    """Scarlet tassels hanging off the foot corners + a centre drop — the only
    saturated red on screen, well below the focal gold pins."""
    for sgn in (-1, -0.42, 0.42, 1):
        tx = int(cx + sgn * hw_foot * 0.92)
        ty = bot + 4
        # cord
        pygame.draw.line(surf, _BRAID_LO, (tx, ty), (tx, ty + 10), 2)
        # knot
        pygame.draw.circle(surf, lerp_color(_SCARLET_HI, _GOLD_DEEP, 0.3),
                           (tx, ty + 12), 4)
        # fringe skirt
        for k in range(-3, 4):
            fx = tx + k * 2
            col = _SCARLET_HI if k % 2 == 0 else _SCARLET
            pygame.draw.line(surf, col, (tx, ty + 13),
                             (fx, ty + 13 + 16 + abs(k)), 2)
        pygame.draw.line(surf, _SCARLET_LO, (tx - 6, ty + 13 + 18),
                         (tx + 6, ty + 13 + 18), 1)


def draw_pin(surf, cx, cy, size, icon_key, title=None):
    """Pin the REAL medallion to the sash: a small navy ribbon-fold + a warm
    glow halo so the gold/navy badge is the brightest object on the cloth."""
    # ribbon fold behind the pin (a chevron of darker cloth catching the medal)
    fold = [(cx - size * 0.42, cy - size * 0.34),
            (cx, cy - size * 0.18),
            (cx + size * 0.42, cy - size * 0.34),
            (cx + size * 0.30, cy + size * 0.10),
            (cx - size * 0.30, cy + size * 0.10)]
    pygame.draw.polygon(surf, _CLOTH_EDGE_LO,
                        [(int(x), int(y)) for x, y in fold])
    pygame.draw.polygon(surf, _BRAID_LO,
                        [(int(x), int(y)) for x, y in fold], 1)
    # warm halo so the pinned gold reads as the screen's brightest point —
    # kept tight to the medal so it crowns the badge rather than washing cloth
    blit_glow(surf, cx, cy, int(size * 0.56), (255, 198, 96), 110)
    r = pygame.Rect(0, 0, size, size)
    r.center = (cx, cy)
    draw_badge(surf, icon_key, r, unlocked=True)
    # a little pin-stud at the top where it meets the cloth
    pygame.draw.circle(surf, _GOLD_PALE, (cx, int(cy - size * 0.46)), 3)
    pygame.draw.circle(surf, _GOLD_DEEP, (cx, int(cy - size * 0.46)), 3, 1)


def main():
    ids = demo_ids(2)
    a0 = ach.BY_ID[ids[0]]
    a1 = ach.BY_ID[ids[1]]

    surf = pygame.Surface((W, H))

    # Deep-night ground: a near-black vertical wash so the spotlit banner pops.
    bg = make_gradient_surface(W, H, [(0.0, _NIGHT_DEEP), (0.5, (9, 5, 26)),
                                      (1.0, (4, 2, 14))])
    surf.blit(bg, (0, 0))

    # Dim ghost of the run summary, far in the back so the screen feels earned.
    ghost = render_backdrop()
    ghost.set_alpha(26)
    surf.blit(ghost, (0, 0))
    _vignette(surf)

    cx, top, bot, base_half, sway_px, hw_foot = draw_banner(surf)
    draw_tassels(surf, cx, bot, hw_foot)

    # Kicker at the very top of the cloth.
    _outlined_text(surf, "COMMENDATION", (cx, 48), 19,
                   fill=_GOLD_PALE, px=2, shadow_offset=(2, 3))
    _outlined_text(surf, "EARNED", (cx, 73), 16,
                   fill=_GOLD_BRIGHT, px=2, shadow_offset=(2, 3))
    # a hairline rule under the kicker
    pygame.draw.line(surf, _BRAID_HI, (cx - 44, 92), (cx + 44, 92), 2)

    # Hero pin (large) + campaign pin (smaller) down the sash — the 2-unlock cue.
    draw_pin(surf, cx, 174, 118, a0.icon_key, a0.title)

    # Woven gold title down the cloth, beneath the hero pin.
    _outlined_text(surf, a0.title.upper(), (cx, 256), 21,
                   fill=_GOLD_BRIGHT, px=2, shadow_offset=(2, 3))

    draw_pin(surf, cx, 348, 74, a1.icon_key, a1.title)
    # the second unlock's title, quieter, by its campaign pin
    _outlined_text(surf, a1.title.upper(), (cx, 404), 14,
                   fill=_GOLD_PALE, px=2, shadow_offset=(1, 2))
    # count woven near the foot to reinforce multiplicity
    cnt = _font(13, True).render("2 COMMENDATIONS", True, _GOLD_DEEP)
    surf.blit(cnt, cnt.get_rect(center=(cx, 460)))

    # Tap-to-continue affordance below the banner foot.
    _pill_btn(surf, (W // 2, 604), "TAP TO CONTINUE", size=17, primary=True)

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice",
                       "award_interstitial_v2", "banner-unfurl")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "round_1.png")
    pygame.image.save(surf, path)
    print(path)


if __name__ == "__main__":
    main()
