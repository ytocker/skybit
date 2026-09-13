"""Mockup: the `pedestal-spotlight` award-interstitial concept — the unlocked
badge rises out of darkness onto a struck-gold PEDESTAL under a single hard
SPOTLIGHT cone, confetti raining INSIDE the cone. A museum-vitrine unveiling:
theatrical, bottom-weighted, directional light + depth.

The still must sell a true near-black room where the cone is the unmistakable
brightest object and the hero medallion is its single brightest point — so the
unveiling reads volumetric, not a flat navy card. Scratch tooling only; nothing
here is imported by the game and `game/` stays untouched.
"""
import os
import math
import random

from tools.unlock_notice_common import render_backdrop, demo_ids
from game import achievements as ach
from game.achievement_icons import draw_badge
from game.draw import blit_glow, make_gradient_surface, rounded_rect_grad, lerp_color
from game.hud import (_font, _outlined_text, _pill_btn,
                      _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP,
                      _PANEL_DARK, _PANEL_LIGHTER, _NIGHT_DEEP)
from game.config import W, H

import pygame


def _radial_vignette(surf, cx, cy, inner_r, outer_r, edge_col):
    """Near-black vignette pulling the eye to the cone. Painted big-to-small as
    concentric ANNULI so each radius gets exactly its falloff (stacked discs
    would over-accumulate). Pushed to alpha 252 at the corners so the margins
    read TRUE black, not a mid navy — the cone must be the brightest object."""
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    maxd = math.hypot(max(cx, W - cx), max(cy, H - cy))
    step = 2
    for r in range(int(maxd), 0, -step):
        t = max(0.0, (r - inner_r) / max(1, outer_r - inner_r))
        a = int(252 * min(1.0, t) ** 1.25)
        if a <= 0:
            continue
        pygame.draw.circle(vig, (*edge_col, a), (cx, cy), r, step + 1)
    surf.blit(vig, (0, 0))


def _crest_glint(surf, cx, cy, R):
    """Struck-metal glint on the upper-left rim crest plus a tight specular
    bloom — the 'freshly minted, catching the spotlight' beat. Additive."""
    gl = pygame.Surface((W, H), pygame.SRCALPHA)
    light = math.radians(135)
    base = pygame.Rect(cx - R, cy - R, R * 2, R * 2)
    for spread, w, a in ((1.05, 5, 60), (0.72, 4, 90), (0.40, 3, 130)):
        pygame.draw.arc(gl, (255, 250, 235, a), base,
                        light - spread, light + spread, w)
    surf.blit(gl, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    hx = cx + int(math.cos(light) * R * 0.90)
    hy = cy - int(math.sin(light) * R * 0.90)
    blit_glow(surf, hx, hy, int(R * 0.20), (255, 252, 242), 120)
    pygame.draw.circle(surf, (255, 254, 248), (hx, hy), 3)


def _spotlight_cone(surf, apex, badge_cy, floor_y, half_top, half_bot):
    """A hard elliptical spotlight cone descending from offscreen-top. Built as
    a vertical alpha-gradient polygon (warm white at the throat, near-black at
    the floor) so the volume is unmistakable, then crowned with stacked additive
    glows on the badge so the hero sits at the brightest point. Returns the cone
    polygon so confetti can be clipped to live ONLY inside it."""
    apex_x, apex_y = apex
    # The cone's left/right edges widen linearly from a tight throat to the
    # floor. Sampling top→bottom lets the body fade warm-white → dark.
    rows = []
    span = floor_y - apex_y
    for i in range(0, int(span) + 1, 2):
        y = apex_y + i
        f = i / max(1, span)
        half = half_top + (half_bot - half_top) * f
        rows.append((y, apex_x - half, apex_x + half))

    cone = pygame.Surface((W, H), pygame.SRCALPHA)
    # Brightest near the badge plane, falling to near-nothing at the floor so the
    # light visibly dies into the dark plinth base. Drawn as filled quad BANDS
    # (not spaced lines) so the beam is smooth, with no horizontal striping.
    for k in range(len(rows) - 1):
        y0, xl0, xr0 = rows[k]
        y1, xl1, xr1 = rows[k + 1]
        ym = (y0 + y1) * 0.5
        if ym < badge_cy:
            b = 1.0 - (badge_cy - ym) / max(1, (badge_cy - apex_y)) * 0.55
        else:
            b = 1.0 - (ym - badge_cy) / max(1, (floor_y - badge_cy)) * 0.92
        b = max(0.0, b)
        # Soft warm beam — kept low so the cone reads as hanging LIGHT, not a
        # white blob; the badge's own glow is the only truly bright spot.
        col = lerp_color((22, 16, 46), (122, 104, 70), b ** 1.25)
        a = int(74 * b + 8)
        pygame.draw.polygon(cone, (*col, a),
                            [(xl0, y0), (xr0, y0), (xr1, y1), (xl1, y1)])
    surf.blit(cone, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Two crisp rim lines on the cone edges near the throat — the hard-edged
    # cut of a theatrical spot. They fade out before the floor.
    edge = pygame.Surface((W, H), pygame.SRCALPHA)
    for (y, xl, xr) in rows[: len(rows) * 2 // 3]:
        f = (y - apex_y) / max(1, (floor_y - apex_y))
        a = int(60 * (1 - f * 1.4))
        if a <= 0:
            continue
        pygame.draw.line(edge, (255, 236, 196, a), (int(xl), int(y)),
                         (int(xl) + 2, int(y)))
        pygame.draw.line(edge, (255, 236, 196, a), (int(xr) - 2, int(y)),
                         (int(xr), int(y)))
    surf.blit(edge, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return rows


def _gold_text(surf, txt, center, size):
    """Gold engraved title: navy drop shadow under a top-lit gold fill with a
    pale upper sheen — matches the menu's gold-on-navy engraving."""
    f = _font(size, True)
    sh = f.render(txt, True, _NIGHT_DEEP)
    sh.set_alpha(200)
    surf.blit(sh, sh.get_rect(center=(center[0] + 2, center[1] + 3)))
    body = f.render(txt, True, _GOLD_BRIGHT)
    r = body.get_rect(center=center)
    surf.blit(body, r)
    sheen = f.render(txt, True, _GOLD_PALE)
    sheen.set_alpha(120)
    surf.blit(sheen, (r.x, r.y - 1))
    return r


def _pedestal(surf, cx, top_y, bot_y, top_half, bot_half):
    """A struck-gold trapezoid plinth lit from the upper-left. Built as a masked
    vertical gradient (pale gold crown → deep gold shadowed base) inside the
    trapezoid silhouette, with a bright bevel on the top lip, a lit left flank
    and a shadowed right flank so it reads as a solid block catching the cone."""
    h = bot_y - top_y
    # gradient body, then clip to the trapezoid
    grad = make_gradient_surface(W, h, [(0.0, (236, 198, 120)),
                                         (0.30, (208, 162, 78)),
                                         (1.0, (104, 70, 24))])
    body = pygame.Surface((W, h), pygame.SRCALPHA)
    body.blit(grad, (0, 0))
    mask = pygame.Surface((W, h), pygame.SRCALPHA)
    poly = [(cx - top_half, 0), (cx + top_half, 0),
            (cx + bot_half, h), (cx - bot_half, h)]
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (0, top_y))

    # The top deck — a thin lit ellipse cap so the badge sits ON a surface.
    deck_h = 16
    deck = pygame.Rect(cx - top_half, top_y - deck_h // 2, top_half * 2, deck_h)
    pygame.draw.ellipse(surf, (240, 206, 132), deck)
    pygame.draw.ellipse(surf, (170, 124, 56), deck, 2)
    # bright crown bevel on the front top lip
    pygame.draw.line(surf, (255, 232, 168),
                     (cx - top_half, top_y), (cx + top_half, top_y), 3)

    # Left flank catches the upper-left light; right flank falls into shadow.
    lit = pygame.Surface((W, h), pygame.SRCALPHA)
    pygame.draw.polygon(lit, (255, 236, 180, 40), [
        (cx - top_half, 0), (cx - top_half + 14, 0),
        (cx - bot_half + 14, h), (cx - bot_half, h)])
    lit.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lit, (0, top_y))
    shade = pygame.Surface((W, h), pygame.SRCALPHA)
    pygame.draw.polygon(shade, (10, 6, 22, 110), [
        (cx + top_half - 18, 0), (cx + top_half, 0),
        (cx + bot_half, h), (cx + bot_half - 18, h)])
    shade.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (0, top_y))


def _dust_ring(surf, cx, cy, R):
    """A settling dust ring kicked up where the badge just rose off the deck —
    a faint warm ellipse of motes, denser on the lit upper-left. Sells motion:
    the medal has only just lifted."""
    dust = pygame.Surface((W, H), pygame.SRCALPHA)
    rng = random.Random(71)
    for _ in range(46):
        a = rng.uniform(0, math.tau)
        rad = rng.uniform(R * 0.6, R * 1.35)
        x = cx + math.cos(a) * rad
        y = cy + math.sin(a) * rad * 0.38
        lit = (math.cos(a - math.radians(135)) + 1) * 0.5
        al = int(40 + 90 * lit)
        sz = rng.choice((1, 1, 2))
        pygame.draw.circle(dust, (255, 224, 170, al), (int(x), int(y)), sz)
    surf.blit(dust, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _motion_smear(surf, cx, cy, R):
    """A soft vertical motion smear trailing BELOW the hero — a faint
    downward-stretched gold ghost plus a couple of vertical light streaks, so
    the badge reads as still settling from its rise without ever rivalling the
    hero (it stays the single brightest shape, drawn on top afterwards)."""
    from game.achievement_icons import get_badge
    a0 = ach.BY_ID[demo_ids(2)[0]]
    badge = get_badge(a0.icon_key, R * 2, True, False)
    # one short downward-stretched ghost trailing strictly BELOW the badge —
    # clipped so nothing of it appears above the badge centre (which would read
    # as a second pale medal).
    gh_h = int(R * 1.5)
    ghost = pygame.transform.smoothscale(badge, (int(R * 2 * 0.8), gh_h))
    ghost = ghost.copy()
    ghost.set_alpha(28)
    gr = ghost.get_rect(midtop=(cx, int(cy + R * 0.2)))
    surf.blit(ghost, gr)
    # a faint upward speed streak above the badge (it rose UP, so the trail is
    # behind it) — short and soft so it never reads as a drip.
    streak = pygame.Surface((W, H), pygame.SRCALPHA)
    L = int(R * 0.9)
    for dx in (-R * 0.34, R * 0.06, R * 0.42):
        for i in range(L):
            a = int(26 * (1 - i / L))
            pygame.draw.line(streak, (255, 224, 160, a),
                             (int(cx + dx), int(cy + R * 0.4 + i)),
                             (int(cx + dx), int(cy + R * 0.4 + i)))
    surf.blit(streak, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def build():
    surf = pygame.Surface((W, H))

    ids = demo_ids(2)
    a0 = ach.BY_ID[ids[0]]
    a1 = ach.BY_ID[ids[1]]

    cx = W // 2

    # ── 1. Dissolve target: the real RUN SUMMARY, very dim, beneath the dark
    # room — a faint sense the ceremony sits IN FRONT of the score it hands to.
    base = render_backdrop().copy()
    base.set_alpha(6)
    surf.fill(_NIGHT_DEEP)
    surf.blit(base, (0, 0))

    badge_cy = 258
    floor_y = 566
    apex = (cx, -70)

    # ── 2. The spotlight cone (painted FIRST so the vignette can carve true
    # black margins around it without dimming the throat).
    cone_rows = _spotlight_cone(surf, apex, badge_cy, floor_y,
                                half_top=30, half_bot=150)

    # ── 3. Near-black vignette: corners to ~252 so the cone is unmistakably the
    # brightest object in the room.
    _radial_vignette(surf, cx, badge_cy, inner_r=40, outer_r=int(H * 0.50),
                     edge_col=_NIGHT_DEEP)

    # ── 4. The gold pedestal low in frame, rising out of the dark.
    ped_top = 470
    ped_bot = 560
    top_half, bot_half = 72, 116
    _pedestal(surf, cx, ped_top, ped_bot, top_half, bot_half)

    # secondary medal row along the deck (the 2-unlock case) — the hero is
    # echoed by one smaller companion medal so several unlocks read at a glance.
    sec_r = 22
    for dx in (top_half - 30,):
        draw_badge(surf, a1.icon_key,
                   pygame.Rect(cx + dx - sec_r, ped_top - 30, sec_r * 2, sec_r * 2),
                   True, False)

    # engraved title plate on the plinth front face
    plate = pygame.Rect(cx - 84, ped_top + 30, 168, 50)
    rounded_rect_grad(surf, plate, 10, (40, 28, 70), (14, 9, 38))
    pygame.draw.rect(surf, _GOLD_DEEP, plate, width=1, border_radius=10)
    _font(11, True)
    kf = _font(11, True)
    k = kf.render("COMMENDATION EARNED", True, _GOLD_PALE)
    k.set_alpha(220)
    surf.blit(k, k.get_rect(center=(cx, plate.y + 14)))
    _gold_text(surf, a0.title.upper(), (cx, plate.y + 34), 17)

    # ── 5. Behind-badge radiance + the flare so the hero is the brightest point.
    R = 60
    # A warm gold halo that hugs the medal — gold, not white, so the hero is a
    # hot focused point inside the cone rather than a milky cloud.
    blit_glow(surf, cx, badge_cy + 4, int(R * 0.95), (255, 168, 66), 54)
    blit_glow(surf, cx, badge_cy + 4, int(R * 0.62), (255, 204, 116), 76)

    # motion smear + dust ring (the medal just rose off the deck)
    _dust_ring(surf, cx, ped_top - 6, top_half)
    _motion_smear(surf, cx, badge_cy, R)

    # the struck medallion — the hero, floating above the plinth
    badge_rect = pygame.Rect(cx - R, badge_cy - R, R * 2, R * 2)
    draw_badge(surf, a0.icon_key, badge_rect, True, False)
    _crest_glint(surf, cx, badge_cy, R)

    # ── 6. Confetti — ONLY inside the cone (clipped per-flake to the cone rows)
    # so the dark margins stay clean and the volumetric read holds.
    from game.entities import CelebrationConfetti
    rng = random.Random(204)

    def _cone_half_at(y):
        if y < apex[1] or y > floor_y:
            return -1
        f = (y - apex[1]) / max(1, floor_y - apex[1])
        return 30 + (150 - 30) * f

    flakes = []
    for _ in range(70):
        # bias confetti toward the badge plane + below, so the throat above the
        # hero stays clean and the white flakes don't read as a pale cloud.
        y = rng.uniform(badge_cy - 70, floor_y - 30)
        half = _cone_half_at(y)
        if half <= 0:
            continue
        # keep a small inset so flakes don't kiss the cone edge / dark margin
        x = cx + rng.uniform(-half + 6, half - 6)
        col = rng.choice(CelebrationConfetti.COLOURS)
        ang = rng.uniform(0, math.tau)
        flakes.append((x, y, col, ang))
    conf = pygame.Surface((W, H), pygame.SRCALPHA)
    for (x, y, col, ang) in flakes:
        w, h = CelebrationConfetti.SIZE
        tile = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
        pygame.draw.rect(tile, col, (1, 1, w, h))
        rot = pygame.transform.rotate(tile, math.degrees(ang))
        # brighter near the throat, dimmer as the light dies toward the floor
        f = (y - badge_cy) / max(1, floor_y - badge_cy)
        rot.set_alpha(int(255 - 90 * max(0.0, f)))
        conf.blit(rot, rot.get_rect(center=(int(x), int(y))))
    surf.blit(conf, (0, 0))

    # ── 7. TAP TO CONTINUE — the bottom skip affordance.
    _pill_btn(surf, (cx, 612), "TAP TO CONTINUE", size=14, dim=True, shadow=False)

    # a faint downward chevron above the pill: it dissolves into the summary.
    chy = 590
    cline = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.lines(cline, (150, 138, 178, 90), False,
                      [(cx - 7, chy), (cx, chy + 5), (cx + 7, chy)], 2)
    surf.blit(cline, (0, 0))

    return surf


def main():
    surf = build()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "achievements", "unlock_notice",
                       "award_interstitial_v2", "pedestal-spotlight")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "round_1.png")
    pygame.image.save(surf, path)
    print(path)


if __name__ == "__main__":
    main()
