"""Recipe-driven engine for the Skull-King stacked-skull PILLARS.

A pillar is an ordered RECIPE of element tokens (gap-edge -> far end) drawn from
the whole skull + ornament menagerie. Skulls stack densely; ORNAMENTS appear only
where the recipe places one (a bead/gem/ring seated between some skulls, once in a
while) -- there is no automatic per-seam bead collar. An optional SKEWER is a rod
threaded down the stack: it is drawn BEHIND the skulls (the skulls overlay it) and
shows through the small gaps the skewered stack leaves between tiers; only the
pointy TIP is drawn on top, poking into the gap. Every element draw + the bead /
gem / ring / sky helpers are reused from the existing harness. Design-only.

Token grammar (global IDs #1-#36):
  crown:0..5  palm:0..5  r9:0|1  new:<slug>  classic:<slug>  orn:<fn>
Skewer styles: plain | gem-tip | ring-washer | barbed | strand
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy"); os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = "/home/user/skybit"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import pygame
import render_skull_king_stack as RK     # loads the element draws + rod/bead/sky helpers
sk = RK.sk

SS, PIPE_W, R, S_UNIT = RK.SS, RK.PIPE_W, RK.R, RK.S_UNIT

_BEAD_FNS = {"bead_white", "bead_gold", "bead_cyan", "bead_darkblue"}


def _meta(token):
    """Final-px radius + role for one element. Skulls can be the lit focal; ornaments
    are smaller in-line tiers / occasional seam-joints."""
    if token.startswith("orn:"):
        fn = token.split(":", 1)[1]
        if fn in _BEAD_FNS:
            return dict(kind="bead", r=R * 0.36)
        if fn == "gem_thirdeye":
            return dict(kind="gem", r=R * 0.54)
        return dict(kind="ring", r=R * 0.58)        # ornament_necklace
    return dict(kind="skull", r=R * 0.96)


def draw_element(big, token, cx, cy, r_px, lit=False):
    """Dispatch a token to its existing draw fn. r_px is the final-px radius; it is
    converted to the supersampled `big` surface here (r = r_px*SS, s = r_px/12*SS)."""
    r = max(1, int(r_px * SS))
    s = (r_px / 12.0) * SS
    cx, cy = int(cx), int(cy)
    if token.startswith("crown:"):
        RK._crown_skull_straight(big, cx, cy, r, s, lit=lit, idx=int(token.split(":")[1]))
    elif token.startswith("palm:"):
        RK._palm_skull_bare(big, cx, cy, r, s, idx=int(token.split(":")[1]))
    elif token.startswith("r9:"):
        RK._crown_skull_orig(big, cx, cy, r, s, lit=bool(int(token.split(":")[1])))
    elif token.startswith("new:"):
        RK._NEW8[token.split(":", 1)[1]][0](big, cx, cy, r, s, lit)
    elif token.startswith("classic:"):
        RK._CLASSIC8[token.split(":", 1)[1]][0](big, cx, cy, r, s, lit)
    elif token.startswith("orn:"):
        getattr(RK._ORN_MOD, token.split(":", 1)[1])(big, cx, cy, r, s)
    else:
        raise ValueError("unknown element token: " + token)


# ── skewer rod styles ────────────────────────────────────────────────────────
def _rod_plain(big, cx, ya, yb):
    """A plain DARK bone rod (no gold marrow) — the crude spit; darker value so the
    column still holds against a bright sky."""
    s = S_UNIT * SS
    hw = RK._SK_HW
    y, h = int(min(ya, yb)), int(abs(yb - ya))
    pygame.draw.rect(big, sk.INK, (cx - hw - int(1.4 * s), y, 2 * (hw + int(1.4 * s)), h))
    pygame.draw.rect(big, sk.BONE_D, (cx - hw, y, 2 * hw, h))
    pygame.draw.rect(big, sk.BONE_SH, (cx - hw, y, max(1, int(1.6 * s)), h))


def _rod_gold(big, cx, ya, yb):
    """A thick, bright GOLD scepter core (the King's staff) — gold-dominant + WIDER
    than the bone rods, so it reads as a solid metal shaft, not a bead cord."""
    s = S_UNIT * SS
    hw = RK._SK_HW + int(1.6 * s)
    y, h = int(min(ya, yb)), int(abs(yb - ya))
    pygame.draw.rect(big, sk.INK, (cx - hw - int(1.4 * s), y, 2 * (hw + int(1.4 * s)), h))
    pygame.draw.rect(big, sk.GOLD_D, (cx - hw, y, 2 * hw, h))
    pygame.draw.rect(big, sk.GOLD, (cx - int(hw * 0.72), y, int(hw * 1.44), h))
    pygame.draw.rect(big, sk.GOLD_BR, (cx - int(hw * 0.30), y, int(hw * 0.60), h))


def _skewer_shaft(big, cx, ya, yb, style):
    if style == "plain":
        _rod_plain(big, cx, ya, yb)
    elif style == "gem-tip":
        _rod_gold(big, cx, ya, yb)
    elif style == "strand":
        s = S_UNIT * SS; hw = max(1, int(2.4 * s))      # thin dark thread under the bead cord
        y, h = int(min(ya, yb)), int(abs(yb - ya))
        pygame.draw.rect(big, sk.INK, (cx - hw, y, 2 * hw, h))
    else:
        RK._rod_seg(big, cx, ya, yb)                     # bone + gold marrow


def _skewer_behind(big, cx, centres, gap_edge, point_dir, style):
    """Rod shaft (+ threaded seam decoration) drawn BEHIND the skulls, so the skulls
    overlay it and it shows through the gaps between tiers. The shaft stops ~15px
    short of the gap edge, leaving clean room for the terminal TIP."""
    cx = int(cx); s = S_UNIT * SS
    near = (gap_edge - point_dir * 15) * SS              # stop short of the edge for the tip
    far = centres[-1] * SS
    _skewer_shaft(big, cx, near, far, style)
    seams = [(centres[i] + centres[i + 1]) / 2.0 for i in range(len(centres) - 1)]
    if style == "ring-washer":
        for ym in seams:                                 # a flat ring-eye washer in each gap
            RK._ORN_MOD.ornament_necklace(big, cx, int(ym * SS), int(R * 0.40 * SS), (R * 0.40 / 12.0) * SS)
    elif style == "plain":
        for k, ym in enumerate(seams):                   # occasional white beads (every other gap)
            if k % 2 == 0:
                sk.triad_circle(big, sk.BEAD, (cx, int(ym * SS)), max(2, int(3.2 * s)),
                                ow=max(1, int(1.0 * s)), core=False)
    elif style == "strand":                              # a continuous bone-white bead cord (the skewer)
        n = max(2, int(abs(far - near) / (7 * SS)))
        pts = [(cx, near + (far - near) * k / n) for k in range(n + 1)]
        sk.bead_strand(big, pts, int(3.8 * s), s, gold_every=99)


def _skewer_tip(big, cx, gap_edge, point_dir, style):
    """The skewer's terminal END, drawn ON TOP so it reads cleanly poking into the
    gap. Modelled on real skewer ends: a sharp steel POINT (plain), an open
    RING-LOOP handle (ring-washer), a JEWELLED finial in a gold cup (gem-tip), a
    barbed HARPOON head (barbed) and a flat PADDLE/oar (strand). `inward` is px
    measured from the gap edge (0 = at the edge, growing into the pillar)."""
    cx = int(cx); d = point_dir; s = S_UNIT * SS
    hw = RK._SK_HW

    def Y(inward):
        return int((gap_edge - d * inward) * SS)

    ow = max(1, int(1.2 * s))

    if style == "ring-washer":
        # an open gold RING-LOOP (the classic ring-handle skewer end), drawn as an
        # annulus so the hole shows sky -> reads as a loop, not a disc.
        ro, ri, rc = 8, 4, 10
        pygame.draw.circle(big, sk.INK, (cx, Y(rc)), int((ro + 1) * SS), int((ro - ri + 2) * SS))
        pygame.draw.circle(big, sk.GOLD, (cx, Y(rc)), int(ro * SS), int((ro - ri) * SS))
        pygame.draw.circle(big, sk.GOLD_BR, (cx - int(ro * 0.5 * SS), Y(rc) + int(ro * 0.4 * SS)),
                           max(1, int(1.8 * s)))
        return

    if style == "gem-tip":
        # a jewelled finial: a small gold socket-cup caps the rod, the cyan gem set in it
        cup = [(cx - hw, Y(17)), (cx + hw, Y(17)),
               (cx + int(hw * 1.6), Y(11)), (cx - int(hw * 1.6), Y(11))]
        sk.triad_blob(big, sk.GOLD, [(int(x), int(y)) for x, y in cup], ow=ow)
        RK._ORN_MOD.gem_thirdeye(big, cx, Y(8), int(6 * SS), (6 / 12.0) * SS)
        return

    if style == "strand":
        # a SPINDLE point (true to the pillar's name): a slim elongated lens that
        # swells at the middle and tapers to a sharp point at the gap — pointy, and
        # distinct from the plain wide-based triangle.
        w = int(hw * 1.5)
        spindle = [(cx, Y(1)), (cx + w, Y(8)), (cx, Y(17)), (cx - w, Y(8))]
        sk.triad_blob(big, sk.BONE, [(int(x), int(y)) for x, y in spindle], ow=ow)
        pygame.draw.line(big, sk.BONE_SH, (cx, Y(15)), (cx, Y(3)), max(1, int(1.0 * s)))
        return

    # plain -> sharp steel point ; barbed -> longer harpoon blade with backward barbs
    long = (style == "barbed")
    base = Y(17 if long else 16)
    point = Y(1)
    if long:
        # a bold leaf HARPOON blade with two recurved backward barbs at its base
        midw = int(hw * 2.4)
        blade = [(cx, point), (cx + midw, Y(10)), (cx + hw, base), (cx - hw, base), (cx - midw, Y(10))]
        sk.triad_blob(big, sk.BONE, [(int(x), int(y)) for x, y in blade], ow=ow)
        for sgn in (-1, 1):                              # recurved barbs flaring back from the base
            barb = [(cx + sgn * hw, base),
                    (cx + sgn * (hw + int(8 * SS)), Y(21)),
                    (cx + sgn * (hw + int(3 * SS)), Y(15))]
            sk.triad_blob(big, sk.BONE, [(int(x), int(y)) for x, y in barb], ow=ow)
        pygame.draw.line(big, sk.BONE_D, (cx, int(base)), (cx, int(point)), max(1, int(1.0 * s)))
    else:
        tri = [(cx - hw, base), (cx + hw, base), (cx, point)]
        sk.triad_blob(big, sk.BONE, [(int(x), int(y)) for x, y in tri], ow=ow)
        pygame.draw.line(big, sk.BONE_SH, (cx - int(hw * 0.35), int(base)), (cx, int(point)),
                         max(1, int(1.2 * s)))


def render_pillar_half(H, *, cap, recipe, with_skewer=False, skewer_style="plain",
                       focal_lit=True, lean=0.0, collar=None, margin_r=None):
    """One pillar half. cap='bottom' -> TOP pillar (gap below); cap='top' -> BOTTOM
    pillar (gap above). Recipe runs gap-edge -> far; element 0 = focal skull at the
    gap. Skewered stacks leave small gaps between tiers so the rod (drawn behind)
    shows through. `lean` jitters elements off-axis. `margin_r` (in units of R)
    overrides how far the focal skull sits off the gap edge — raise it when the
    focal skull has long downward appendages (e.g. fangs) so the tip clears it.
    `collar` is accepted but ignored (beads are explicit recipe elements now)."""
    big = pygame.Surface((PIPE_W * SS, H * SS), pygame.SRCALPHA)
    cx0 = PIPE_W * SS // 2
    metas = [_meta(t) for t in recipe]
    if margin_r is None:
        margin_r = 1.75 if with_skewer else 1.05
    margin = int(R * margin_r)
    if cap == "bottom":
        focal_y, step, point_dir, gap_edge = H - margin, -1, +1, H
    else:
        focal_y, step, point_dir, gap_edge = margin, +1, -1, 0

    # dense overlap for a solid plain tower; small GAPS for skewered so the rod shows
    factor = 1.14 if with_skewer else 0.84
    centres = [focal_y]
    for i in range(1, len(recipe)):
        spacing = (metas[i - 1]["r"] + metas[i]["r"]) * factor
        centres.append(centres[-1] + step * spacing)

    def ex(i):
        return cx0 + (0 if i == 0 else int(lean * R * SS) * (1 if i % 2 else -1))

    if with_skewer:
        _skewer_behind(big, cx0, centres, gap_edge, point_dir, skewer_style)

    for i in reversed(range(len(recipe))):               # far -> near: nearer overlaps toward the gap
        lit = (i == 0 and focal_lit and metas[i]["kind"] == "skull")
        draw_element(big, recipe[i], ex(i), centres[i] * SS, metas[i]["r"], lit=lit)

    if with_skewer:
        _skewer_tip(big, cx0, gap_edge, point_dir, skewer_style)

    return sk.grow_outline(pygame.transform.smoothscale(big, (PIPE_W, H)), sk.INK + (255,), 1)


def render_pair(recipe, *, with_skewer=False, skewer_style="plain", collar=None, lean=0.0,
                night=False, half_h=190, gap=150, pad=12, margin_r=None):
    """A full top+bottom pillar pair framing the gap, composited on sky."""
    top = render_pillar_half(half_h, cap="bottom", recipe=recipe, with_skewer=with_skewer,
                             skewer_style=skewer_style, lean=lean, margin_r=margin_r)
    bot = render_pillar_half(half_h, cap="top", recipe=recipe, with_skewer=with_skewer,
                             skewer_style=skewer_style, lean=lean, margin_r=margin_r)
    H = half_h * 2 + gap
    panel = RK._sky(PIPE_W + pad * 2, H, night=night)
    panel.blit(top, (pad, 0))
    panel.blit(bot, (pad, half_h + gap))
    return panel
