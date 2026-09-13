"""Mockup: the `postmark-routing-map` award-list concept — a stylised aerial
COURIER ROUTE for a 3-achievement unlock screen.

The metaphor: the run's commendation arrives like a parcel that flew a route.
A dashed flight-path snakes top->bottom in a shallow S; the three unlocked
achievements are franked postmark STOPS plotted along it, each a real struck
badge node with a HORIZONTAL nameplate tag (NAME + short desc) flagging off the
line. The route reads as a completed journey: every segment BEHIND a node is a
warm-gold lit path (delivered), the run-out AHEAD of the last node is a dim
dotted line, and the route ends at a "TAP TO CONTINUE ->" terminus that hands
off to the run summary. Pip rides the lead node.

The make-or-break reads this still must sell:
  * "journey completed" — the path is GOLD/lit up to and between the three
    earned stops, then goes DIM/dotted on the final run-out to the terminus.
  * node-badge clarity — each stop is the REAL draw_badge medallion, seated ON
    the line, large enough to read its glyph at 1x.
  * a clean LIST of 3 — all three nameplates are HORIZONTAL, equally weighted,
    fully on-canvas; the shallow S never pushes a tag off-screen or cramps row 3.

Scratch tooling only — nothing here is imported by the game; `game/` untouched.
"""
import os
import math
import pygame

from tools.unlock_notice_common import demo_varied_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, make_gradient_surface, lerp_color
from game.hud import (_font, _outlined_text, _draw_overlay_stars,
                      _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H


# Deep-night sky stops for the route's backdrop — same family as the menu's
# navy field, kept dark and low-contrast so the gold route + badges own the eye.
_SKY_TOP = _NIGHT_DEEP
_SKY_MID = (14, 9, 40)
_SKY_BOT = (22, 14, 54)

# The lit (delivered) path tones vs. the dim (run-out, ahead) tones — the whole
# "journey completed" read hinges on this contrast.
_PATH_LIT_CORE = _GOLD_PALE
_PATH_LIT_EDGE = _GOLD_DEEP
_PATH_DIM = (78, 70, 112)        # cool dim violet-grey for the un-flown run-out


# Control x's the flight-path threads through, at evenly spaced route-progress
# knots. Chosen so the three node stops (t = 0.10 / 0.42 / 0.74) land LEFT /
# RIGHT / LEFT of centre with a clear offset — each node's open side has room
# for its full horizontal nameplate, and the swing stays shallow so nothing
# crowds an edge.
_ROUTE_KNOTS = (
    (0.00, W * 0.50),
    (0.10, W * 0.38),     # node 1 — left, tag flies right
    (0.30, W * 0.50),
    (0.42, W * 0.62),     # node 2 — right, tag flies left
    (0.58, W * 0.52),
    (0.74, W * 0.38),     # node 3 — left, tag flies right
    (0.88, W * 0.46),
    (1.00, W * 0.50),     # terminus — centred under the route
)


def _route_x(t: float) -> float:
    """Smooth x along the flight-path: piecewise-cosine interpolation between
    the control knots, so the route is a gentle S that passes EXACTLY through
    each node's chosen x (keeping its nameplate's open side roomy)."""
    knots = _ROUTE_KNOTS
    t = max(0.0, min(1.0, t))
    for i in range(len(knots) - 1):
        t0, x0 = knots[i]
        t1, x1 = knots[i + 1]
        if t <= t1:
            u = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            s = 0.5 - 0.5 * math.cos(u * math.pi)   # ease-in-out
            return x0 + (x1 - x0) * s
    return knots[-1][1]


def _route_point(t, top, bot):
    return _route_x(t), top + (bot - top) * t


def _draw_path_segment(surf, t0, t1, top, bot, lit, samples=26):
    """Draw a sub-stretch of the flight-path as dashes/dots between route
    progress t0..t1. Lit segments are a glowing gold dash; the run-out is a
    quiet dotted line so 'delivered vs. ahead' reads at a glance."""
    pts = [_route_point(t0 + (t1 - t0) * i / samples, top, bot)
           for i in range(samples + 1)]
    if lit:
        # A soft gold underglow tube, then bright dashes riding on top.
        for (x, y) in pts:
            blit_glow(surf, int(x), int(y), 9, (255, 196, 96), 26)
        dash = True
        for i in range(len(pts) - 1):
            if dash:
                pygame.draw.line(surf, _PATH_LIT_EDGE, pts[i], pts[i + 1], 7)
                pygame.draw.line(surf, _PATH_LIT_CORE, pts[i], pts[i + 1], 3)
            dash = not dash
    else:
        # Quiet dotted run-out — small dim dots with gaps.
        for i in range(0, len(pts), 2):
            x, y = pts[i]
            pygame.draw.circle(surf, _PATH_DIM, (int(x), int(y)), 3)


def _nameplate(surf, anchor, side, name, desc):
    """A horizontal nameplate tag flagging off the route node. ``anchor`` is the
    node centre; ``side`` (-1 left / +1 right) is the PREFERRED direction the
    tag flies — flipped automatically when that side lacks room, so every tag
    lands FULLY on-canvas. A short stub connects the node to a rounded navy
    plate carrying NAME (bold gold) over a short desc (pale grey)."""
    f_name = _font(17, True)
    f_desc = _font(12, False)
    name_img = f_name.render(name, True, _GOLD_BRIGHT)
    desc_img = f_desc.render(desc, True, (206, 198, 224))

    pad_x, pad_y, gap = 12, 8, 3
    plate_w = max(name_img.get_width(), desc_img.get_width()) + pad_x * 2
    plate_h = name_img.get_height() + gap + desc_img.get_height() + pad_y * 2

    ax, ay = anchor
    stub = 14
    badge_r = 27
    margin = 6
    # Flip the preferred side if the plate wouldn't fit fully on that side.
    room_right = W - margin - (ax + badge_r + stub)
    room_left = (ax - badge_r - stub) - margin
    if side > 0 and room_right < plate_w and room_left >= plate_w:
        side = -1
    elif side < 0 and room_left < plate_w and room_right >= plate_w:
        side = +1
    if side > 0:
        px = ax + badge_r + stub
    else:
        px = ax - badge_r - stub - plate_w
    px = int(max(margin, min(px, W - plate_w - margin)))
    py = int(ay - plate_h / 2)

    # Connector stub from the badge rim to the plate edge.
    stub_y = ay
    sx0 = ax + side * badge_r
    sx1 = px if side > 0 else px + plate_w
    pygame.draw.line(surf, _GOLD_DEEP, (sx0, stub_y), (sx1, stub_y), 4)
    pygame.draw.line(surf, _GOLD_PALE, (sx0, stub_y), (sx1, stub_y), 2)

    # Plate body — navy gradient, gold trim, drop shadow.
    rect = pygame.Rect(px, py, plate_w, plate_h)
    sh = pygame.Surface((plate_w + 6, plate_h + 6), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 110), (0, 0, plate_w + 6, plate_h + 6),
                     border_radius=12)
    surf.blit(sh, (px - 3, py + 3))
    grad = make_gradient_surface(plate_w, plate_h, [(0.0, _PANEL_LIGHTER),
                                                    (1.0, _PANEL_DARK)])
    mask = pygame.Surface((plate_w, plate_h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, plate_w, plate_h),
                     border_radius=11)
    plate = pygame.Surface((plate_w, plate_h), pygame.SRCALPHA)
    plate.blit(grad, (0, 0))
    plate.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(plate, _GOLD_BRIGHT, (0, 0, plate_w, plate_h),
                     width=2, border_radius=11)
    pygame.draw.line(plate, (*_GOLD_PALE, 150), (10, 3), (plate_w - 10, 3), 1)
    surf.blit(plate, rect.topleft)

    surf.blit(name_img, (px + pad_x, py + pad_y))
    surf.blit(desc_img, (px + pad_x, py + pad_y + name_img.get_height() + gap))
    return rect


def _banner(surf, cy):
    """The top headline banner — a wide navy ribbon carrying the gold-on-red
    'ACHIEVEMENT EARNED!' title, so it reads as the dispatch's franking header."""
    bw, bh = W - 24, 56
    bx, by = 12, cy - bh // 2
    grad = make_gradient_surface(bw, bh, [(0.0, _PANEL_LIGHTER),
                                          (1.0, _PANEL_DARK)])
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bw, bh),
                     border_radius=14)
    ribbon = pygame.Surface((bw, bh), pygame.SRCALPHA)
    ribbon.blit(grad, (0, 0))
    ribbon.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(ribbon, _GOLD_BRIGHT, (0, 0, bw, bh), width=2,
                     border_radius=14)
    # Inner double-keyline — a postal-frank feel.
    pygame.draw.rect(ribbon, (*_GOLD_DEEP, 180), (5, 5, bw - 10, bh - 10),
                     width=1, border_radius=10)
    surf.blit(ribbon, (bx, by))
    _outlined_text(surf, "ACHIEVEMENT EARNED!", (W // 2, cy), 25,
                   shadow_offset=(2, 3))


def _terminus(surf, anchor):
    """The route's end — a 'RUN SUMMARY' destination pin + a 'TAP TO CONTINUE ->'
    affordance handing off to the summary screen."""
    ax, ay = anchor
    # Destination disc (a dim navy pin, distinct from the gold badge nodes).
    blit_glow(surf, int(ax), int(ay), 14, (120, 110, 170), 26)
    pygame.draw.circle(surf, _PANEL_LIGHTER, (int(ax), int(ay)), 11)
    pygame.draw.circle(surf, _GOLD_BRIGHT, (int(ax), int(ay)), 11, 2)
    pygame.draw.circle(surf, _GOLD_PALE, (int(ax), int(ay)), 4)

    f_dest = _font(13, True)
    dest = f_dest.render("RUN SUMMARY", True, (210, 202, 230))
    surf.blit(dest, dest.get_rect(center=(int(ax), int(ay) + 26)))

    # The tap affordance, bright at the very bottom.
    cy = int(ay) + 56
    _outlined_text(surf, "TAP TO CONTINUE  ->", (W // 2, cy), 18,
                   shadow_offset=(2, 3))


def render():
    surf = pygame.Surface((W, H))
    # Deep-night sky field.
    sky = make_gradient_surface(W, H, [(0.0, _SKY_TOP), (0.55, _SKY_MID),
                                       (1.0, _SKY_BOT)])
    surf.blit(sky, (0, 0))
    # A few faint stars behind the route (kept sparse so they don't compete).
    stars = [(40, 150, 1, 0.0), (300, 120, 2, 1.0), (70, 470, 1, 2.0),
             (320, 430, 1, 3.0), (180, 90, 1, 4.0), (28, 320, 2, 5.0),
             (335, 300, 1, 1.5), (210, 560, 1, 2.5), (110, 250, 1, 3.5)]
    _draw_overlay_stars(surf, stars, 0.6)

    _banner(surf, 40)

    # Route geometry — runs from just under the banner to the terminus pin.
    top, bot = 96, 548
    # Three node progress positions, staggered so their nameplates alternate
    # sides and stay roomy; the terminus sits at t=1.0.
    node_ts = [0.10, 0.42, 0.74]
    term_t = 1.00

    items = [(ach.BY_ID[i].icon_key, ach.BY_ID[i].title, ach.BY_ID[i].desc)
             for i in demo_varied_ids(3)]

    # PATH: lit/gold from the banner through the last earned node (delivered),
    # then a dim dotted run-out from the last node to the terminus (ahead).
    _draw_path_segment(surf, 0.0, node_ts[-1], top, bot, lit=True, samples=70)
    _draw_path_segment(surf, node_ts[-1], term_t, top, bot, lit=False,
                       samples=22)

    # Nameplates first (behind the badges so the badge rim overlaps the stub),
    # alternating sides; clamped on-canvas by _nameplate.
    sides = [+1, -1, +1]
    anchors = [_route_point(t, top, bot) for t in node_ts]
    for (icon, name, desc), anchor, side in zip(items, anchors, sides):
        _nameplate(surf, anchor, side, name, desc)

    # Badge NODES seated on the line.
    for idx, ((icon, name, desc), anchor) in enumerate(zip(items, anchors)):
        ax, ay = int(anchor[0]), int(anchor[1])
        # A small "checkpoint" lit ring under each delivered node.
        blit_glow(surf, ax, ay, 26, (255, 200, 96), 30)
        r = pygame.Rect(0, 0, 52, 52)
        r.center = (ax, ay)
        draw_badge(surf, icon, r, unlocked=True)

    # Pip the macaw rides the lead node — a small silhouette tucked at the
    # first stop so the route reads as "Pip's delivery flight".
    try:
        from game.parrot import get_parrot
        pip = get_parrot(0, 14.0)
        pip = pygame.transform.smoothscale(pip, (40, 40))
        lead = anchors[0]
        # Perch Pip above-left of the lead node, clear of the badge + tag, as
        # if just touching down on the first stop of the route.
        surf.blit(pip, pip.get_rect(center=(int(lead[0]) - 38,
                                            int(lead[1]) - 34)))
    except Exception:
        pass

    _terminus(surf, _route_point(term_t, top, bot))
    return surf


def main():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    if not pygame.get_init():
        pygame.init()
    surf = render()
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "docs", "achievements", "unlock_notice", "award_list",
        "postmark-routing-map")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    pygame.image.save(surf, out)
    print(out)


if __name__ == "__main__":
    main()
