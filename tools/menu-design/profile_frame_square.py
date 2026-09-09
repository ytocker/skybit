"""PROFILE frame — five SQUARE options, all obeying the same three rules:
the frame is a true square, its bottom edge closes just below the cloud's
base, and the PROFILE tag hangs directly under it.

The style is untouched — thin gold double rule, top sheen, brass tag. Only the
square's side length and its horizontal anchor vary between the five.

Two facts set the whole envelope. The cloud's base is y321, so a bottom edge
"just below the cloud" lands at y324; and the subtitle's mass ends at y178, so
the top edge cannot rise past ~y188. That fixes the side length between 104
(the smallest square that still reaches over the cottage roof at y221) and 136.
Every option below lives in that band.

It also means the cloud, 160px wide, is wider than any square that fits, so it
spills past the right-hand rule in all five — the cottage sits left of the
cloud's centre, and the square has to cover the cottage.

    OPTION=S1..S5 python3 tools/menu-design/profile_frame_square.py
    SHOWCASE=1    python3 tools/menu-design/profile_frame_square.py
"""
import os
import sys
import math

_ROOT = "/home/user/skybit"
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "tools", "menu-design"))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame                                        # noqa: E402
import profile_frame_variants as PF                   # noqa: E402

B = PF.B
_hud = B._hud
GOLD_MID, GOLD_BRIGHT, GOLD_PALE = B.GOLD_MID, B.GOLD_BRIGHT, B.GOLD_PALE
GOLD_DEEP = B.GOLD_DEEP
W, H = 360, 640

BOTTOM = 324          # 3px under the cloud's measured base (y321)

# The tag rides the cloud's lower-left lobe, inside the frame, rather than
# hanging under it. One fixed rect for all five: it is anchored to the cloud,
# which never moves, so the tag reads as pinned to the same spot however the
# square around it is sized.
#
# The cloud is a lens, not a box. Its left edge runs x40 at y296, pinches to
# x55 at y299, opens to x28 by y306, holds that to y315, then closes fast —
# x38 at y316, x66 at y320. So the lowest a left-anchored tag can sit and stay
# on cloud mass is a bottom edge at y316, and the 8px corner radius carries the
# top-left arc over the y299-302 pinch.
TAG = pygame.Rect(42, 295, 84, 22)


def _sq(left, top, side):
    return pygame.Rect(left, top, side, side)


# slug: (rect, thesis)
PRESETS = {
    "S1": (_sq(27, 217, 108), "crop - tightest square that still clears the roof"),
    "S2": (_sq(25, 207, 118), "poise - a stop roomier, weighted to the cottage"),
    "S3": (_sq(28, 199, 126), "parrot - centred on Pip; equal air either side of him"),
    "S4": (_sq(16, 189, 136), "grand - largest that clears the subtitle"),
    "S5": (_sq(28, 189, 136), "island - same size, pushed right to hold more cloud"),
}


def tag_for(fr):
    """Same seat on the cloud for every option — see TAG."""
    return pygame.Rect(TAG)


def draw_frame(surf, fr, tag):
    """The accepted construction, verbatim. Only fr/tag change."""
    pygame.draw.rect(surf, GOLD_MID, fr, width=1, border_radius=13)
    pygame.draw.rect(surf, GOLD_BRIGHT, fr.inflate(-10, -10), width=1,
                     border_radius=8)
    pygame.draw.line(surf, (*GOLD_PALE, 200), (fr.left + 14, fr.top + 2),
                     (fr.right - 14, fr.top + 2), 1)

    pygame.draw.rect(surf, GOLD_DEEP, tag, border_radius=8)
    pygame.draw.rect(surf, GOLD_MID, tag.inflate(-3, -3), border_radius=7)
    pygame.draw.line(surf, GOLD_PALE, (tag.left + 8, tag.top + 3),
                     (tag.right - 8, tag.top + 3), 1)
    pygame.draw.line(surf, (86, 60, 16), (tag.left + 8, tag.bottom - 3),
                     (tag.right - 8, tag.bottom - 3), 1)
    inset = tag.inflate(-7, -7)
    pygame.draw.rect(surf, (52, 34, 14), inset, border_radius=5)
    # 12/1 rather than the old 13/2: on this shorter tag the recess is 77px
    # wide and PROFILE at 13/2 plus the triangle measures 84.
    lx = inset.centerx - 6
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery + 1), 12,
                        color=(34, 20, 8), track=1, alpha=150)
    _hud._tracked_label(surf, "PROFILE", (lx, inset.centery), 12,
                        color=GOLD_PALE, track=1, alpha=250)
    _hud._profile_tri(surf, inset.right - 9, inset.centery, 4, GOLD_PALE)
    return fr.union(tag)


def build_shipped(phase):
    """The live menu, exactly as scenes.py draws STATE_MENU — hud.draw_menu
    owns the veil, the profile card, the START pill and the plank chain. This
    is the thing the five squares are proposals against, so it is rendered
    through the shipping code path rather than re-mocked."""
    from game.scenes import App, STATE_MENU
    from game.world import World
    from game import biome as _biome
    from game import foreground
    from game.config import W as GW, H as GH

    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.state = STATE_MENU
    app.world = World()
    for _ in range(40):
        app.world.world_idle_tick(1 / 60)
    app.world.biome_time = phase * _biome.CYCLE_SECONDS
    app.world.weather.wetness = 0.0
    app.world.bird.frame_t = 0.0

    s = app.screen
    app._draw_background(s)
    foreground.draw_near_lane(s, app.world.bg_scroll, app.world.biome_palette,
                              app.world.biome_phase, app.world.biome_time)
    house = B._intro.get_sprite("skyhouse_post")
    s.blit(house, (int(GW * 0.30) - house.get_width() // 2,
                   int(GH * 0.42) - house.get_height() // 2))
    app.world.bird.draw(s, 0, 0)
    app.hud.draw_menu(s, 1 / 60, app.best)

    # Same draw call on its own layer: the margin table has to be measured
    # against the silhouette this panel actually shows.
    pip = pygame.Surface((GW, GH), pygame.SRCALPHA)
    app.world.bird.draw(pip, 0, 0)
    m = pygame.mask.from_surface(pip, threshold=8)
    px = [(x, y) for x in range(GW) for y in range(200, 340) if m.get_at((x, y))]
    return s, app.hud.menu_profile_rect, px


def shipped_stats(fr, px):
    xs = [x for x, y in px]
    ys = [y for x, y in px]
    return dict(
        side=(fr.width, fr.height),
        square=fr.width == fr.height,
        rect=(fr.left, fr.top, fr.right - 1, fr.bottom - 1),
        clip_px=len([p for p in px if not fr.collidepoint(p)]),
        pip=(min(xs) - fr.left, fr.right - 1 - max(xs),
             min(ys) - fr.top, fr.bottom - 1 - max(ys)),
        cottage=(0, 0, B.house_cottage_rect().top - fr.top),
        below_cloud=fr.bottom - 1 - (B.cloud_rect().bottom - 1),
    )


def build(phase, slug):
    import random
    from game.scenes import App, STATE_MENU
    from game.world import World
    from game import biome as _biome
    from game import foreground
    from game.config import W as GW, H as GH

    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.state = STATE_MENU
    app.world = World()
    for _ in range(40):
        app.world.world_idle_tick(1 / 60)
    app.world.biome_time = phase * _biome.CYCLE_SECONDS
    app.world.weather.wetness = 0.0
    app.world.bird.frame_t = 0.0
    app.world.bird.x = B.PIP_CX
    app.world.bird.y = B.PIP_CY

    pal = _biome.palette_for_phase(phase)
    surf = app.screen
    app._draw_background(surf)
    foreground.draw_near_lane(surf, app.world.bg_scroll, pal, 0.0,
                              app.world.biome_time)
    dim = pygame.Surface((GW, GH), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    surf.blit(dim, (0, 0))
    rng = random.Random(42)
    stars = [(rng.randint(8, GW - 8), rng.randint(8, GH - 180),
              rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28))
             for _ in range(38)]
    _hud._draw_overlay_stars(surf, stars, 0.0)
    _hud._draw_mountain_silhouette(surf, alpha=180)
    surf.blit(B._intro.get_sprite("skyhouse_post"), B.house_topleft())
    app.world.bird.draw(surf)
    chain = B.draw_signchain(surf)
    tails = chain.pop("_tails")
    B.draw_start_B(surf, tails)
    fr = PRESETS[slug][0]
    draw_frame(surf, fr, tag_for(fr))
    _hud._outlined_text(surf, "SKYBIT", (GW // 2, 112), size=72, px=3,
                        shadow_offset=(2, 3))
    _hud._outlined_text(surf, "POCKET  SKY  FLYER", (GW // 2, 168),
                        size=20, px=2, shadow_offset=(1, 2))
    return surf


def _pip_pixels():
    """Pip's TRUE opaque silhouette at the menu respawn point — his bounding
    box understates the frame's job by several pixels."""
    from game.world import World
    from game.config import H as GH, BIRD_X
    w = World()
    w.bird.x, w.bird.y, w.bird.frame_t = BIRD_X, GH * 0.42, 0.0
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    w.bird.draw(s)
    m = pygame.mask.from_surface(s, threshold=8)
    return [(x, y) for x in range(40, 150) for y in range(220, 320)
            if m.get_at((x, y))]


def _subtitle_bottom():
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    _hud._outlined_text(s, "SKYBIT", (W // 2, 112), size=72, px=3,
                        shadow_offset=(2, 3))
    _hud._outlined_text(s, "POCKET  SKY  FLYER", (W // 2, 168), size=20, px=2,
                        shadow_offset=(1, 2))
    rs = pygame.mask.from_surface(s, 8).get_bounding_rects()
    r = rs[0]
    for o in rs[1:]:
        r = r.union(o)
    return r.bottom - 1


def _rope_x(sgn, y):
    """draw_signchain's own anchor -> hook interpolation. Colour-matching the
    rope false-positives on Pip's orange plumage, so use the formula."""
    ax = 42 if sgn < 0 else 173
    cx, cy, ang, w, h = 102, 386, -3.0, 172, 44
    rad = math.radians(-ang)
    ox = sgn * (w * 0.36)
    hx = cx + ox * math.cos(rad)
    hy = cy + ox * math.sin(rad) - h * 0.5
    return ax + (y - 316) / (hy - 316) * (hx - ax)


def verify(slug, pip=None, sub=None):
    fr = PRESETS[slug][0]
    tag = tag_for(fr)
    pip = pip if pip is not None else _pip_pixels()
    sub = sub if sub is not None else _subtitle_bottom()
    cot = B.house_cottage_rect()
    cloud = B.cloud_rect()

    outside = [p for p in pip if not fr.collidepoint(p)]
    px = [x for x, y in pip]
    py = [y for x, y in pip]

    # The ropes only exist below their y316 cloud anchors, so only the tag's
    # bottom rows can foul them.
    shape = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(shape, (255, 255, 255), tag, border_radius=8)
    worst = float("inf")
    for y in range(max(tag.top, 316), tag.bottom):
        row = [x for x in range(tag.left, tag.right) if shape.get_at((x, y))[3] > 8]
        if row:
            worst = min(worst, min(row) - _rope_x(-1, y),
                        _rope_x(1, y) - max(row))
    if worst == float("inf"):
        worst = None

    # The tag now sits INSIDE the frame, so the number that matters is its
    # clearance to the inner gold rule, not to the outer one.
    inner = fr.inflate(-10, -10)
    fit = min(tag.left - inner.left, inner.right - 1 - (tag.right - 1),
              tag.top - inner.top, inner.bottom - 1 - (tag.bottom - 1))

    house = B._intro.get_sprite("skyhouse_post")
    hx, hy = B.house_topleft()
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    lay.blit(house, (hx, hy))
    on = sum(1 for x in range(tag.left, tag.right)
             for y in range(tag.top, tag.bottom) if lay.get_at((x, y))[3] > 8)
    return dict(
        side=(fr.width, fr.height),
        square=fr.width == fr.height,
        rect=(fr.left, fr.top, fr.right - 1, fr.bottom - 1),
        clip_px=len(outside),
        pip=(min(px) - fr.left, fr.right - 1 - max(px),
             min(py) - fr.top, fr.bottom - 1 - max(py)),
        cottage=(cot.left - fr.left, fr.right - 1 - (cot.right - 1),
                 cot.top - fr.top),
        below_cloud=fr.bottom - 1 - (cloud.bottom - 1),
        cloud_spill_r=max(0, (cloud.right - 1) - (fr.right - 1)),
        subtitle_clear=fr.top - sub,
        tag_inside_frame=fit,
        tag_on_cloud="%d%%" % round(100 * on / (tag.width * tag.height)),
        tag_rope_clear=None if worst is None else round(worst, 1),
        tag_clears_pip=min(y for x, y in pip) if False else tag.top - max(py),
    )


if __name__ == "__main__":
    order = ["S1", "S2", "S3", "S4", "S5"]
    pip, sub = _pip_pixels(), _subtitle_bottom()
    stats = {s: verify(s, pip, sub) for s in order}

    if os.environ.get("SHOWCASE"):
        F = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
        fh = pygame.font.Font(F, 20)
        fl = pygame.font.Font(F, 15)
        fs = pygame.font.Font(F, 12)
        CW, CH = W, H
        PAD, GAP, LAB, HEAD = 22, 14, 66, 52

        live_surf, live_fr, live_pip = build_shipped(0.20)
        stats["current"] = shipped_stats(live_fr, live_pip)
        panels = [("current", live_surf,
                   "the live game menu today - not square, not keyed to the cloud")]
        panels += [(s, None, PRESETS[s][1]) for s in order]

        n = len(panels)
        sheet = pygame.Surface((PAD * 2 + n * CW + (n - 1) * GAP,
                                PAD * 2 + HEAD + CH + LAB))
        sheet.fill((17, 17, 23))
        sheet.blit(fh.render("SKYBIT · PROFILE frame · five squares, tag on the cloud",
                             True, (228, 204, 134)), (PAD, PAD))
        sheet.blit(fs.render(
            "leftmost is the menu on this branch. Every option after it: a true square, bottom edge 3px under "
            "the cloud's base (y324), and the PROFILE tag seated on the cloud's lower-left lobe inside the frame.",
            True, (150, 148, 142)), (PAD, PAD + 26))

        y = PAD + HEAD
        for i, (slug, surf, thesis) in enumerate(panels):
            if surf is None:
                surf = build(0.20, slug)
            x = PAD + i * (CW + GAP)
            sheet.blit(surf, (x, y))
            live = slug == "current"
            pygame.draw.rect(sheet, (150, 122, 62) if live else (76, 76, 86),
                             (x, y, CW, CH), 2 if live else 1)
            st = stats[slug]
            t = fl.render("%s   %d x %d" % (slug, *st["side"]), True,
                          (232, 206, 138) if live else (240, 240, 246))
            sheet.blit(t, t.get_rect(midtop=(x + CW // 2, y + CH + 8)))
            c = fs.render(thesis, True, (156, 154, 148))
            sheet.blit(c, c.get_rect(midtop=(x + CW // 2, y + CH + 28)))
            bad = st["clip_px"] > 0
            m = "Pip  L%d R%d T%d B%d      roof gap %d      outside frame %d px" % (
                *st["pip"], st["cottage"][2], st["clip_px"])
            c2 = fs.render(m, True, (214, 106, 96) if bad else (128, 186, 132))
            sheet.blit(c2, c2.get_rect(midtop=(x + CW // 2, y + CH + 46)))

        out = ("/home/user/skybit/docs/main-menu/harbour-post/"
               "profile-frame/square_showcase.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        pygame.image.save(sheet, out)
        print("saved", out, sheet.get_size())
        order = ["current"] + order
    else:
        which = os.environ.get("OPTION", "S3")
        out = os.environ.get("OUT", "/tmp/_pfsq_%s.png" % which)
        pygame.image.save(build(float(os.environ.get("PHASE", "0.20")), which), out)
        print("saved", out)

    print("subtitle mass ends at y%d" % sub)
    for s in order:
        print("%-8s %s" % (s, stats[s]))
