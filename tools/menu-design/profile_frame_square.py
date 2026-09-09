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

# The pick: L2 lifted 5px — square Rect(19, 204, 144, 144), tag seated flush
# in the inner rule's bottom-left corner at Rect(25, 320, 84, 22).
CHOSEN = ("L2", 5)

ROOF = 221            # cottage roof top — a frame below this crops it
STORE_TOP = 359       # STORE plank's rotated bbox — the floor for any drop

TAG_W, TAG_H = 84, 22


def _sq(left, top, side):
    return pygame.Rect(left, top, side, side)


# slug: (rect, thesis)
#
# All five sit LOWER than the previous round, with the tag moved off the cloud
# and down onto the frame's own bottom band. Two hard edges bracket how low a
# square can go: the cottage roof starts at y221, and the STORE plank's rotated
# bbox starts at y359. A frame that drops must therefore either grow — its top
# is pinned just over the roof while its bottom runs down — or crop the roof.
# L1-L4 grow; L5 is the one that crops, and is the only way to be both low and
# small.
PRESETS = {
    "L1": (_sq(22, 215, 138), "smallest square that still holds the whole roof"),
    "L2": (_sq(19, 209, 144), "one stop up top - 12px over the roof"),
    "L3": (_sq(16, 203, 150), "roomier again; 18px over the roof"),
    "L4": (_sq(13, 197, 156), "largest before the right rule reaches the right rope"),
    "L5": (_sq(29, 229, 124), "tight - smallest of the five; pays 8px of roof"),
}
def rect_for(slug, dy=0):
    """The option's square, lifted dy pixels. The tag hangs off the frame, so
    moving the frame moves the button with it — that is the whole point of
    anchoring it to the inner rule rather than to the cloud."""
    return PRESETS[slug][0].move(0, -dy)


def tag_for(fr):
    """On the frame's own bottom band, inside it, clear of the inner rule.

    Seated flush into the INNER rule's bottom-left corner — its first painted
    column sits directly against the inner rule's left run, its last row
    directly on that rule's bottom run. Nothing floats.

    The frames are then sized so this lands the tag just under the cloud: with
    every bottom pinned at y352 the tag occupies y325-346, three rows of sky
    below the cloud's y321 base.
    """
    inner = fr.inflate(-10, -10)
    t = pygame.Rect(0, 0, TAG_W, TAG_H)
    t.left = inner.left + 1
    t.bottom = inner.bottom - 1
    return t


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
    # A copy, not app.screen itself: every App() hands back the same display
    # surface, so the next render would repaint this one under the caller.
    return s.copy(), app.hud.menu_profile_rect, px


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
        roof_crop=max(0, fr.top - ROOF),
        store_clear=STORE_TOP - (fr.bottom - 1),
    )


def build(phase, slug, dy=0):
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
    fr = rect_for(slug, dy)
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


def verify(slug, pip=None, sub=None, dy=0):
    fr = rect_for(slug, dy)
    tag = tag_for(fr)
    pip = pip if pip is not None else _pip_pixels()
    sub = sub if sub is not None else _subtitle_bottom()
    cot = B.house_cottage_rect()
    cloud = B.cloud_rect()

    outside = [p for p in pip if not fr.collidepoint(p)]
    px = [x for x, y in pip]
    py = [y for x, y in pip]

    # The ropes only exist below their y316 cloud anchors, and the 8px corner
    # radius pulls the tag's end rows inside its rect, so measure the PAINTED
    # pixels — the rect overstates the tag's reach.
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

    # The tag deliberately laps the inner rule on the LEFT now, so a single
    # min() over all four sides would just report that on purpose. Left is an
    # offset from the frame's outer rule; the others stay clearances.
    inner = fr.inflate(-10, -10)
    fit = min(inner.right - 1 - (tag.right - 1), tag.top - inner.top)

    # The frame's own bottom rule now runs below the cloud, so it crosses the
    # rope columns; report where rather than pretending it does not.
    crossings = sum(1 for sgn in (-1, 1)
                    if fr.left <= _rope_x(sgn, fr.bottom - 1) <= fr.right - 1)
    # The right vertical can now reach past the right rope's run as well.
    right_rope = min(_rope_x(1, y) - (fr.right - 1)
                     for y in range(max(fr.top, 316), fr.bottom))
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
        roof_crop=max(0, fr.top - ROOF),
        store_clear=STORE_TOP - (fr.bottom - 1),
        subtitle_clear=fr.top - sub,
        rope_crossings=crossings,
        right_rule_v_rope=round(right_rope, 1),
        tag_touches_inner=(tag.left - 1 == inner.left,
                           tag.bottom + 1 == inner.bottom),
        tag_below_cloud=tag.top - (cloud.bottom - 1) - 1,
        tag_inside_frame=fit,
        tag_rope_clear=None if worst is None else round(worst, 1),
        tag_clears_pip=tag.top - max(py),
    )


if __name__ == "__main__":
    order = ["L1", "L2", "L3", "L4", "L5"]
    # Each row lifts the frame — and the tag riding its inner corner — by this
    # many pixels. 15 is the ceiling: L4 is the tallest square, and at -15 its
    # top rule sits 5px under the subtitle's ink.
    SHIFTS = [0, 5, 10, 15]
    pip, sub = _pip_pixels(), _subtitle_bottom()

    if os.environ.get("SHOWCASE"):
        F = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
        fh = pygame.font.Font(F, 20)
        fb = pygame.font.Font(F, 16)
        fl = pygame.font.Font(F, 15)
        fs = pygame.font.Font(F, 12)
        CW, CH = W, H
        PAD, GAP, LAB, HEAD, BAN, RGAP = 22, 14, 64, 52, 26, 20

        live_surf, live_fr, live_pip = build_shipped(0.20)
        cols = ["current"] + order
        ncol = len(cols)
        rowh = BAN + CH + LAB
        sheet = pygame.Surface((PAD * 2 + ncol * CW + (ncol - 1) * GAP,
                                PAD * 2 + HEAD + len(SHIFTS) * rowh
                                + (len(SHIFTS) - 1) * RGAP))
        sheet.fill((17, 17, 23))
        sheet.blit(fh.render(
            "SKYBIT · PROFILE frame · the same five, lifted row by row",
            True, (228, 204, 134)), (PAD, PAD))
        sheet.blit(fs.render(
            "top row is where the last round left it. Each row below lifts the square AND the tag riding its inner "
            "bottom-left corner by the stated amount. Columns are the five sizes; the leftmost panel is this branch's menu, repeated as a fixed anchor.",
            True, (150, 148, 142)), (PAD, PAD + 26))

        allstats = {}
        for r, dy in enumerate(SHIFTS):
            ry = PAD + HEAD + r * (rowh + RGAP)
            st0 = verify(order[0], pip, sub, dy)
            tb = st0["tag_below_cloud"]
            sub_min = min(verify(s_, pip, sub, dy)["subtitle_clear"] for s_ in order)
            banner = ("MOVED UP %d px%s      tag vs cloud base: %s"
                      "      tightest subtitle gap: %dpx"
                      % (dy, "   (as now)" if dy == 0 else "",
                         "%dpx below" % tb if tb >= 0 else "%dpx into it" % -tb,
                         sub_min))
            sheet.blit(fb.render(banner, True, (232, 206, 138) if dy == 0
                                 else (206, 200, 188)), (PAD, ry + 4))
            pygame.draw.line(sheet, (60, 60, 70), (PAD, ry + BAN - 4),
                             (sheet.get_width() - PAD, ry + BAN - 4), 1)

            y = ry + BAN
            for i, slug in enumerate(cols):
                x = PAD + i * (CW + GAP)
                if slug == "current":
                    sheet.blit(live_surf, (x, y))
                    pygame.draw.rect(sheet, (150, 122, 62), (x, y, CW, CH), 2)
                    t = fl.render("this branch's menu", True, (232, 206, 138))
                    sheet.blit(t, t.get_rect(midtop=(x + CW // 2, y + CH + 8)))
                    c = fs.render("unchanged reference", True, (156, 154, 148))
                    sheet.blit(c, c.get_rect(midtop=(x + CW // 2, y + CH + 28)))
                    continue

                sheet.blit(build(0.20, slug, dy), (x, y))
                pygame.draw.rect(sheet, (76, 76, 86), (x, y, CW, CH), 1)
                st = verify(slug, pip, sub, dy)
                allstats[(dy, slug)] = st
                t = fl.render("%s   %d x %d" % (slug, *st["side"]), True,
                              (240, 240, 246))
                sheet.blit(t, t.get_rect(midtop=(x + CW // 2, y + CH + 8)))
                c = fs.render("top y%d   bottom y%d" % (st["rect"][1], st["rect"][3]),
                              True, (156, 154, 148))
                sheet.blit(c, c.get_rect(midtop=(x + CW // 2, y + CH + 26)))
                bad = st["clip_px"] > 0 or st["roof_crop"] > 0
                m = ("Pip L%d R%d T%d B%d   roof %s   subtitle %dpx"
                     % (*st["pip"],
                        ("CUT %d" % st["roof_crop"]) if st["roof_crop"]
                        else "+%d" % st["cottage"][2],
                        st["subtitle_clear"]))
                c2 = fs.render(m, True, (214, 106, 96) if bad else (128, 186, 132))
                sheet.blit(c2, c2.get_rect(midtop=(x + CW // 2, y + CH + 44)))

        out = ("/home/user/skybit/docs/main-menu/harbour-post/"
               "profile-frame/square_showcase.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        pygame.image.save(sheet, out)
        print("saved", out, sheet.get_size())
        print("subtitle mass ends at y%d" % sub)
        for dy in SHIFTS:
            for s_ in order:
                st = allstats[(dy, s_)]
                print("  up%-3d %-3s rect=%s roof_cut=%d subtitle=%d tag_below_cloud=%d "
                      "store=%d pip_clip=%d"
                      % (dy, s_, st["rect"], st["roof_crop"], st["subtitle_clear"],
                         st["tag_below_cloud"], st["store_clear"], st["clip_px"]))
    elif os.environ.get("CONFIRM"):
        F = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
        fh = pygame.font.Font(F, 20)
        fl = pygame.font.Font(F, 15)
        fs = pygame.font.Font(F, 12)
        slug, dy = CHOSEN
        st = verify(slug, pip, sub, dy)
        fr, tag = rect_for(slug, dy), tag_for(rect_for(slug, dy))
        CW, CH, PAD, GAP, HEAD, LAB = W, H, 22, 14, 74, 46
        sheet = pygame.Surface((PAD * 2 + 2 * CW + GAP, PAD * 2 + HEAD + CH + LAB))
        sheet.fill((17, 17, 23))
        sheet.blit(fh.render("SKYBIT · PROFILE frame · chosen: %s lifted %dpx" % (slug, dy),
                             True, (228, 204, 134)), (PAD, PAD))
        sheet.blit(fs.render(
            "square %s   ·   tag %s, flush in the inner rule's bottom-left corner"
            % (tuple(fr), tuple(tag)), True, (150, 148, 142)), (PAD, PAD + 26))
        sheet.blit(fs.render(
            "Pip L%d R%d T%d B%d, uncut   ·   %dpx over the roof   ·   subtitle gap %dpx   "
            "·   STORE gap %dpx   ·   tag %dpx into the cloud's base"
            % (*st["pip"], st["cottage"][2], st["subtitle_clear"], st["store_clear"],
               -st["tag_below_cloud"]), True, (128, 186, 132)), (PAD, PAD + 46))
        for i, (ph, name) in enumerate(((0.20, "day"), (0.75, "night"))):
            x = PAD + i * (CW + GAP)
            y = PAD + HEAD
            sheet.blit(build(ph, slug, dy), (x, y))
            pygame.draw.rect(sheet, (76, 76, 86), (x, y, CW, CH), 1)
            t = fl.render(name, True, (240, 240, 246))
            sheet.blit(t, t.get_rect(midtop=(x + CW // 2, y + CH + 10)))
        out = ("/home/user/skybit/docs/main-menu/harbour-post/"
               "profile-frame/chosen_L2_up5.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        pygame.image.save(sheet, out)
        print("saved", out, sheet.get_size())
        print("frame", tuple(fr), "tag", tuple(tag))
        print(st)
    else:
        which = os.environ.get("OPTION", "L3")
        dy = int(os.environ.get("UP", "0"))
        out = os.environ.get("OUT", "/tmp/_pfsq_%s_%d.png" % (which, dy))
        pygame.image.save(build(float(os.environ.get("PHASE", "0.20")), which, dy), out)
        print("saved", out, verify(which, pip, sub, dy))
