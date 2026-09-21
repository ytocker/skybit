"""THE FESTIVAL KIT — the night the weekend market puts on its show.

Per FESTIVAL_PLAN.md: the dragon parade's pearl-bearer and drum-and-cymbal
cart, the Monkey King troupe, the food-theatre stall overlays, walk-and-eat
hand props, the lantern arch, the daytime plant (the draped dragon-head cart
that arrives 148 seconds before the dragon dances) and the small-hours
residue set.

Contracts held throughout:
  * Night cap — every lit pixel routes through the family cap helpers, so the
    gold coin (≈230) stays the sole brightest object on screen.
  * Compositing — the parade support and the troupe stand on the near deck;
    the arch and the residue belong to the promenade layer, behind the
    pillars, the coins and the bird.
  * Determinism — no wall clock, no RNG in draw paths: every per-figure value
    is a stable hash of its index, so a frame renders identically on desktop
    and in WASM.

Callers (foreground_promenade / foreground_near_lane) import this module
inside functions, so the kit never participates in an import cycle.
"""
from __future__ import annotations

import math

import pygame

from game.config import W, GROUND_Y
from game import foreground_props as sp
from game import food_stalls as _food

NEAR_GROUND_Y = GROUND_Y + 43        # the near deck (638) — parade + crowd feet
FAR_BASE = GROUND_Y - 1              # the far deck the stalls/rig stand on (594)

NIGHT_GLOW_CAP = 150
SKIN = (222, 178, 132)
HALF_W = _food.HALF_W                # the shipped stall's half width (22)


def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _retint(col, night):
    """Cloth/skin cooled toward the night ground band (the promenade curve), with
    a soft pull-down for anything that would land over the cap."""
    if night <= 0.05:
        return col
    out = _mix(col, (78, 88, 118), min(0.38, 0.28 * night + 0.14))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _cap_to(col, ceil):
    y = _luma(col)
    if y <= ceil:
        return col
    k = ceil / y
    return (_clamp(col[0] * k), _clamp(col[1] * k), _clamp(col[2] * k))


def _cap150(col):
    return _cap_to(col, NIGHT_GLOW_CAP)


_wisp = _food._wisp                  # the town's one smoke/steam idiom


def _glow(surf, cx, cy, night, *, radius, peak, color):
    """Additive halo whose centre ADD is bounded by `peak` (the cached
    foreground_props halo bakes the falloff into RGB), gated to the dark hours
    so day frames never grow a white pool."""
    if night <= 0.40 or peak <= 1:
        return
    g = sp._warm_glow(radius, _cap150(color), peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1),
              special_flags=pygame.BLEND_RGB_ADD)


def _h(i, k):
    """A stable per-spark hash. Same value on every target, no RNG state."""
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1.0


# ── run state ────────────────────────────────────────────────────────────────
# The mask flag latches when the troupe act completes, so the souvenir can
# spread through the crowd for the rest of the night window.

_masks_on = False


def reset_run():
    global _masks_on
    _masks_on = False


def set_masks_on():
    global _masks_on
    _masks_on = True


def masks_active(phase):
    return _masks_on and (phase % 1.0) < 0.840


# ════════════════════════════════════════════════════════════════════════════
# A6 / A7 / A8 — DRAGON-PARADE SUPPORT: the pearl-bearer leading the head, the
# drum-and-cymbal cart leading the line, and the draped dragon-head handcart
# that plants the whole act 148 seconds before it dances.
# ════════════════════════════════════════════════════════════════════════════

def _person(surf, cx, feet, night, *, h=18, coat=(96, 104, 140), hair=(52, 42, 34),
            arms='down', face=1):
    """A civilian at the shared cast proportions — the parade support's extras
    (drummer, cymbals, puller) at the near lane's scale."""
    coat = _retint(coat, night)
    coat_dk = _shade(coat, -34)
    skin = _retint(SKIN, night)
    hair = _retint(hair, night)
    head_r = 3
    torso_h = int(h * 0.46)
    body_w = max(3, int(h * 0.26))
    torso_bot = feet - (h - torso_h - head_r * 2)
    torso_top = torso_bot - torso_h
    hy = torso_top - head_r
    for sgn in (-1, 1):
        pygame.draw.line(surf, coat_dk, (cx + sgn * 2, torso_bot), (cx + sgn * 2, feet), 2)
    pygame.draw.polygon(surf, coat, [
        (cx - body_w, torso_top), (cx + body_w, torso_top),
        (cx + body_w + 1, torso_bot), (cx - body_w - 1, torso_bot)])
    pygame.draw.polygon(surf, coat_dk, [
        (cx - body_w, torso_top), (cx + body_w, torso_top),
        (cx + body_w + 1, torso_bot), (cx - body_w - 1, torso_bot)], 1)
    sh_y = torso_top + 2
    if arms == 'up':
        for sgn in (-1, 1):
            pygame.draw.line(surf, coat, (cx + sgn * body_w, sh_y),
                             (cx + sgn * (body_w + 3), sh_y - 7), 2)
    elif arms == 'point':
        pygame.draw.line(surf, coat, (cx - body_w, sh_y), (cx - body_w - 6, sh_y - 6), 2)
        pygame.draw.line(surf, coat, (cx + body_w, sh_y), (cx + body_w + 2, sh_y + 5), 2)
    else:
        for sgn in (-1, 1):
            pygame.draw.line(surf, coat, (cx + sgn * body_w, sh_y),
                             (cx + sgn * (body_w + 1), sh_y + 6), 2)
    pygame.draw.circle(surf, skin, (cx, hy), head_r)
    pygame.draw.circle(surf, hair, (cx, hy - 1), head_r)
    pygame.draw.arc(surf, hair, (cx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                    math.radians(0), math.radians(180), 2)
    pygame.draw.circle(surf, (34, 24, 20), (cx + face, hy), 0)
    return hy, sh_y


def draw_pearl_bearer(surf, cx, night, t, *, feet=NEAR_GROUND_Y):
    """The pearl of wisdom on a pole ahead of the head, traced in a figure-8 at
    0.8 Hz. The pearl is the parade's LEAD object, not its brightest: capped at
    128 with a 24-luma halo budget so the 3 px pole stays legible through the
    glow and the fire keeps the top of the ladder."""
    _hy, sh_y = _person(surf, cx, feet, night, h=30, coat=(168, 74, 62), arms='up')
    ph = t * 0.8 * math.tau
    px = cx + 4 + int(math.sin(ph) * 9)
    py = feet - 56 + int(math.sin(ph * 2) * 6)
    pole = _retint((132, 100, 60), night)
    pygame.draw.line(surf, _shade(pole, -28), (cx + 3, sh_y - 6), (px, py + 5), 3)
    pygame.draw.line(surf, pole, (cx + 3, sh_y - 6), (px, py + 5), 1)
    _glow(surf, px, py, night, radius=8, peak=24, color=(150, 108, 54))
    amber = _cap_to((186, 138, 74), 128) if night > 0.05 else (216, 168, 96)
    pygame.draw.circle(surf, _shade(amber, -34), (px, py), 5)
    pygame.draw.circle(surf, amber, (px, py), 4)
    pygame.draw.circle(surf, _cap_to(_shade(amber, 22), 128), (px - 1, py - 1), 2)
    # the tassel that says a hand is swinging it, not that it floats
    pygame.draw.line(surf, _retint((172, 66, 56), night), (px, py + 4), (px - 2, py + 8), 1)


def _spoked_wheel(surf, cx, cy, r, night, *, far=False):
    """Iron tyre, light interior, three full-diameter spokes — the handcart
    wheel the market's own carts already use."""
    iron = _retint((70, 62, 56) if not far else (54, 48, 44), night)
    wood = _retint((150, 112, 66) if not far else (116, 86, 52), night)
    pygame.draw.circle(surf, iron, (cx, cy), r)
    pygame.draw.circle(surf, wood, (cx, cy), max(1, r - 1))
    for k in range(3):
        a = k * math.pi / 3.0
        dx, dy = math.cos(a) * (r - 1), math.sin(a) * (r - 1)
        pygame.draw.line(surf, iron, (cx - dx, cy - dy), (cx + dx, cy + dy), 1)
    pygame.draw.circle(surf, _shade(wood, -10), (cx, cy), 1)


def draw_drum_cart(surf, cx, night, t, *, feet=NEAR_GROUND_Y):
    """The barrel drum at 1.5x on a two-wheel chassis, drummer riding the bed,
    two flanking cymbal figures and a puller — the platform is dragged."""
    g = feet
    wood = _retint((132, 96, 56), night)
    wood_dk = _shade(wood, -30)
    wood_hi = _shade(wood, 18)
    _spoked_wheel(surf, cx + 8, g - 4, 4, night, far=True)
    bed_y = g - 11
    pygame.draw.polygon(surf, wood, [(cx - 18, bed_y), (cx + 18, bed_y),
                                     (cx + 18, bed_y + 4), (cx - 18, bed_y + 4)])
    pygame.draw.polygon(surf, wood_dk, [(cx - 18, bed_y), (cx + 18, bed_y),
                                        (cx + 18, bed_y + 4), (cx - 18, bed_y + 4)], 1)
    pygame.draw.line(surf, wood_hi, (cx - 17, bed_y), (cx + 17, bed_y), 1)
    # THE BARREL DRUM head-on, so the ivory head is the cart's one big shape
    # and the parade's rhythm has a face.
    drum = _mix(_retint((162, 62, 48), night), (70, 70, 96), 0.20 * night)
    dcx, dcy = cx - 2, bed_y - 15
    pygame.draw.ellipse(surf, _shade(drum, -26), (dcx - 17, dcy - 15, 34, 30))
    pygame.draw.ellipse(surf, drum, (dcx - 16, dcy - 14, 32, 28))
    head = _cap_to((200, 178, 142), 128) if night > 0.05 else (206, 186, 152)
    pygame.draw.ellipse(surf, head, (dcx - 13, dcy - 12, 26, 9))
    pygame.draw.ellipse(surf, _shade(head, -30), (dcx - 13, dcy - 12, 26, 9), 1)
    tack = _cap_to((176, 146, 88), 128) if night > 0.05 else (186, 156, 96)
    for ti in range(-3, 4):
        pygame.draw.circle(surf, tack, (dcx + ti * 4, dcy - 2), 1)
    pygame.draw.line(surf, _shade(drum, -34), (dcx - 15, dcy + 6), (dcx + 15, dcy + 6), 1)
    # the drummer STANDING on the bed — seated, he'd vanish behind a 30 px drum
    _person(surf, cx + 14, bed_y, night, h=26, coat=(96, 76, 128))
    for phi in (0.0, math.pi):
        travel = max(0.0, math.sin(t * 4.5 + phi))
        sy = dcy - 10 - int((1.0 - travel) * 7)
        sxs = dcx + (7 if phi else -7)
        pygame.draw.line(surf, _retint((176, 150, 100), night), (cx + 10, bed_y - 12), (sxs, sy), 2)
    # two flanking CYMBAL figures; the clash is a 1-frame capped ivory disc.
    # The clash halo lands FIRST, so the additive pass hits dark paving instead
    # of stacking on the already-capped disc.
    for sgn, phi in ((-1, 0.0), (1, 1.7)):
        fx = cx + sgn * 28
        _hy2, shy = _person(surf, fx, g, night, h=30,
                            coat=(70, 110, 150) if sgn < 0 else (150, 120, 70), arms='up')
        clash = math.sin(t * 4.5 + phi) > 0.86
        spread = 2 if clash else 6
        cy2 = shy - 8
        disc = _cap_to((190, 176, 130), 132) if night > 0.05 else (206, 190, 142)
        if clash:
            _glow(surf, fx, cy2, night, radius=6, peak=26, color=(140, 130, 100))
        for s2 in (-1, 1):
            pygame.draw.ellipse(surf, _shade(disc, -34),
                                (fx + s2 * spread - 4, cy2 - 3, 8, 7))
            pygame.draw.ellipse(surf, disc, (fx + s2 * spread - 3, cy2 - 2, 6, 5))
    _person(surf, cx - 32, g, night, h=30, coat=(120, 92, 74), arms='point')
    pygame.draw.line(surf, _retint((150, 132, 96), night),
                     (cx - 28, g - 12), (cx - 18, bed_y + 1), 1)
    _spoked_wheel(surf, cx - 6, g - 4, 5, night)
    sh = _mix(_retint((60, 52, 44), night), (0, 0, 0), 0.2)
    pygame.draw.line(surf, sh, (cx - 14, g), (cx + 14, g), 1)


def draw_draped_cart(surf, cx, night, t, *, feet=FAR_BASE):
    """The dragon's head rolling past under a red cloth, roped down, hours
    before it dances. The cloth TENTS over two horn nubs and a snout ridge —
    a lump that is obviously a head without ever showing a face."""
    g = feet
    wood = _retint((132, 96, 56), night)
    wood_dk = _shade(wood, -30)
    wood_hi = _shade(wood, 18)
    wr = 4
    axle_x, axle_y = cx - 3, g - wr
    _spoked_wheel(surf, axle_x + 4, axle_y - 2, wr - 1, night, far=True)
    bed_y = g - wr * 2 - 2
    x0, x1 = cx - 13, cx + 13
    pygame.draw.polygon(surf, wood, [(x0, bed_y), (x1, bed_y), (x1, bed_y + 3), (x0, bed_y + 3)])
    pygame.draw.polygon(surf, wood_dk, [(x0, bed_y), (x1, bed_y), (x1, bed_y + 3), (x0, bed_y + 3)], 1)
    pygame.draw.line(surf, wood_hi, (x0 + 1, bed_y), (x1 - 1, bed_y), 1)
    for off in (0, 2):
        pygame.draw.line(surf, wood_dk, (x1 - 1, bed_y + 1 + off), (x1 + 9, bed_y - 4 + off), 1)
    cloth = _retint((176, 56, 48), night)
    cloth_dk = _shade(cloth, -36)
    cloth_hi = _shade(cloth, 20)
    top = bed_y - 16
    silhouette = [
        (cx - 12, bed_y),
        (cx - 10, top + 9),
        (cx - 7, top + 3),           # LEFT HORN nub tenting the cloth
        (cx - 5, top + 6),
        (cx - 1, top),               # RIGHT HORN nub, taller
        (cx + 2, top + 5),
        (cx + 7, top + 6),           # brow shelf
        (cx + 11, top + 11),         # the SNOUT ridge running down-forward
        (cx + 13, bed_y),
    ]
    pygame.draw.polygon(surf, cloth_dk, [(p[0], p[1] + 1) for p in silhouette])
    pygame.draw.polygon(surf, cloth, silhouette)
    pygame.draw.lines(surf, cloth_hi, False,
                      [(cx - 7, top + 4), (cx - 1, top + 1), (cx + 7, top + 7)], 1)
    for k in range(-9, 12, 4):
        pygame.draw.line(surf, cloth_dk, (cx + k, bed_y), (cx + int(k * 0.85), top + 9), 1)
    # ropes lashing it to the bed — the detail that says "in transit, valuable"
    rope = _retint((178, 160, 118), night)
    pygame.draw.line(surf, rope, (cx - 12, bed_y - 5), (cx + 13, bed_y - 5), 1)
    pygame.draw.line(surf, rope, (cx - 3, top + 4), (cx - 6, bed_y), 1)
    pygame.draw.line(surf, rope, (cx - 3, top + 4), (cx + 6, bed_y), 1)
    _spoked_wheel(surf, axle_x, axle_y, wr, night)
    sh = _mix(_retint((60, 52, 44), night), (0, 0, 0), 0.2)
    pygame.draw.line(surf, sh, (axle_x - wr, g), (axle_x + wr, g), 1)


# ════════════════════════════════════════════════════════════════════════════
# A13 — THE LANTERN ARCH. Two poles and an arc of six lanterns spanning
# ~120 px, apex y=497 — the top_y the shipped night garland is already strung
# at, so the gateway hangs at a height the street already owns.
# ════════════════════════════════════════════════════════════════════════════

GARLAND_TOP_Y = 497


def draw_lantern_arch(surf, cx, night, t, *, span=120, apex=GARLAND_TOP_Y,
                      feet=FAR_BASE):
    g = feet
    pole = _retint((116, 88, 56), night)
    pole_dk = _shade(pole, -28)
    x0, x1 = cx - span // 2, cx + span // 2
    top = apex
    for px in (x0, x1):
        pygame.draw.line(surf, pole_dk, (px, g), (px, top + 12), 3)
        pygame.draw.line(surf, pole, (px, g), (px, top + 12), 1)
        pygame.draw.rect(surf, pole_dk, (px - 3, g - 2, 7, 2))
    # the arc — a shallow catenary of rope between the two pole heads
    arc = []
    for i in range(25):
        f = i / 24.0
        ax = x0 + f * span
        ay = top + 12 - math.sin(f * math.pi) * 12
        arc.append((int(ax), int(ay)))
    pygame.draw.lines(surf, _retint((92, 78, 58), night), False, arc, 2)
    pygame.draw.lines(surf, _retint((146, 126, 92), night), False, arc, 1)
    for k in range(6):
        f = 0.09 + k * 0.164
        i = int(f * 24)
        lx, ly = arc[i]
        sway = math.sin(t * 1.1 + k) * 1.0
        lx = int(lx + sway)
        pygame.draw.line(surf, _retint((70, 56, 44), night), (lx, ly), (lx, ly + 3), 1)
        shell = _cap150((150, 70, 60)) if night > 0.05 else (192, 92, 76)
        shell_lt = _cap150((150, 96, 80)) if night > 0.05 else (214, 130, 104)
        _glow(surf, lx, ly + 9, night, radius=8, peak=34, color=(150, 92, 56))
        pygame.draw.ellipse(surf, shell, (lx - 4, ly + 3, 8, 11))
        pygame.draw.ellipse(surf, shell_lt, (lx - 3, ly + 4, 6, 9))
        pygame.draw.rect(surf, _retint((50, 34, 26), night), (lx - 3, ly + 3, 6, 2))
        pygame.draw.rect(surf, _retint((50, 34, 26), night), (lx - 3, ly + 12, 6, 2))
        pygame.draw.line(surf, _retint((172, 66, 56), night), (lx, ly + 14), (lx, ly + 17), 1)


# ════════════════════════════════════════════════════════════════════════════
# A15 — THE RESIDUE SET. The festival hands back to the small hours with
# evidence, not a fade: the troupe's swept paper masks, left in the gutter.
# ════════════════════════════════════════════════════════════════════════════

def draw_dropped_mask(surf, x, night, *, flipped=False, feet=NEAR_GROUND_Y - 2):
    """A swept paper monkey mask lying in the gutter — the troupe's souvenir,
    two blocks and one show later. Face-up shows the gold; face-down shows the
    pale paper back and the snapped elastic."""
    y = feet
    if flipped:
        paper = _retint((198, 186, 160), night)
        pygame.draw.ellipse(surf, _shade(paper, -30), (x - 5, y - 3, 10, 6))
        pygame.draw.ellipse(surf, paper, (x - 4, y - 2, 8, 4))
        pygame.draw.line(surf, _retint((120, 108, 88), night), (x + 4, y - 1), (x + 9, y + 1), 1)
    else:
        gold = _cap_to(_retint((188, 158, 84), night), 132)
        pygame.draw.ellipse(surf, _shade(gold, -34), (x - 5, y - 3, 10, 6))
        pygame.draw.ellipse(surf, gold, (x - 4, y - 2, 8, 4))
        ruff = _retint((150, 70, 48), night)
        pygame.draw.arc(surf, ruff, (x - 6, y - 4, 12, 8), math.radians(150), math.radians(390), 1)
        for sgn in (-1, 1):
            pygame.draw.line(surf, ruff, (x + sgn * 2, y - 2), (x + sgn * 8, y - 4), 1)
        pygame.draw.circle(surf, (30, 24, 22), (x - 2, y), 0)
        pygame.draw.circle(surf, (30, 24, 22), (x + 1, y), 0)


# ════════════════════════════════════════════════════════════════════════════
# A9 / A10 — THE MONKEY KING TROUPE + THE PAPER MASK. Gold face, red-brown fur
# ruff, two long swept phoenix plumes: no other head in the game has two long
# curved antennae, so the act is identifiable from outline alone.
# ════════════════════════════════════════════════════════════════════════════

def draw_monkey_mask(surf, hx, hy, night, *, r=4, plume=0.0, plume_dir=1,
                     worn=True, sweep=1.0):
    """`sweep` trades plume RISE for plume REACH: at 1.0 the plumes stand off
    the brow; at 0.3 they lie back along the shoulders — what a head inside a
    horizontal spin actually does, and what keeps the crouched spin beat wide
    instead of tall."""
    gold = _cap_to(_retint((216, 178, 92), night), 132) if night > 0.05 else (224, 186, 96)
    gold_dk = _shade(gold, -40)
    ruff = _retint((156, 74, 46), night)
    ruff_dk = _shade(ruff, -26)
    # the fur ruff first, so it reads as a collar BEHIND the face
    for k, ang in enumerate(range(120, 421, 30)):
        rad = math.radians(ang)
        mx = hx + int(math.cos(rad) * (r + 1))
        my = hy + int(math.sin(rad) * (r + 1))
        pygame.draw.circle(surf, ruff_dk if k % 2 else ruff, (mx, my), 2)
    pygame.draw.circle(surf, gold_dk, (hx, hy), r)
    pygame.draw.circle(surf, gold, (hx, hy), max(1, r - 1))
    # the opera face: a red brow band + two eye slits + a peach-shaped snout
    pygame.draw.line(surf, _retint((178, 58, 48), night), (hx - r + 1, hy - 1), (hx + r - 1, hy - 1), 1)
    pygame.draw.circle(surf, (26, 20, 18), (hx - 1, hy), 0)
    pygame.draw.circle(surf, (26, 20, 18), (hx + 1, hy), 0)
    pygame.draw.line(surf, gold_dk, (hx - 1, hy + 2), (hx + 1, hy + 2), 1)
    # TWO LONG SWEPT PHOENIX PLUMES — the outline read; they lag the body on
    # the spin and the somersault, where most of the act's motion lives.
    pl = _cap_to(_retint((208, 188, 118), night), 128) if night > 0.05 else (218, 198, 124)
    pl_dk = _shade(pl, -46)
    for sgn in (-1, 1):
        pts = []
        for k in range(6):
            f = k / 5.0
            px = hx + sgn * (1 + f * (8 + (1.0 - sweep) * 7)) * plume_dir
            py = hy - r - 1 - f * 7 * sweep + math.sin(f * 2.6 + plume) * 2.2 * f * sweep
            pts.append((int(px), int(py)))
        pygame.draw.lines(surf, pl_dk, False, pts, 2)
        pygame.draw.lines(surf, pl, False, pts, 1)
        pygame.draw.circle(surf, pl, pts[-1], 1)
    if not worn:
        # pushed up: a chin strap dangling, so it reads as an object
        pygame.draw.line(surf, _retint((150, 132, 96), night), (hx - r, hy + 2), (hx - r - 1, hy + 6), 1)


def _acrobat(surf, cx, feet, night, *, h=20, t=0.0, torso=(196, 84, 62),
             lean=0, arms='down', legs='stand', head_at=None, plume_dir=1,
             sweep=1.0):
    """A Monkey King acrobat body. The red-and-gold sash is dealt identically
    to all three so the trio reads as one troupe while the three POSES stay
    unrelated."""
    tor = _retint(torso, night)
    tor_dk = _shade(tor, -36)
    gold = _cap_to(_retint((214, 182, 96), night), 130)
    body_w = 4
    torso_h = int(h * 0.44)
    torso_bot = feet - (h - torso_h - 8)
    torso_top = torso_bot - torso_h
    if legs == 'wide':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor_dk, (cx + sgn * 2, torso_bot),
                             (cx + sgn * 6, feet), 2)
    elif legs == 'brace':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor_dk, (cx + sgn * 2, torso_bot), (cx + sgn * 5, feet - 4), 2)
            pygame.draw.line(surf, tor_dk, (cx + sgn * 5, feet - 4), (cx + sgn * 4, feet), 2)
    elif legs == 'crouch':
        # a low horse stance: the knee goes OUT, not down — a crouch that only
        # shortens the figure makes it small; knees thrown wide make it WIDE,
        # which is the whole silhouette argument of the spin beat.
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor_dk, (cx + sgn * 2, torso_bot),
                             (cx + sgn * 9, torso_bot + 2), 3)
            pygame.draw.line(surf, tor_dk, (cx + sgn * 9, torso_bot + 2),
                             (cx + sgn * 8, feet), 2)
            pygame.draw.line(surf, tor_dk, (cx + sgn * 6, feet), (cx + sgn * 10, feet), 2)
    elif legs == 'none':
        pass
    else:
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor_dk, (cx + sgn * 2, torso_bot), (cx + sgn * 2, feet), 2)
    pygame.draw.polygon(surf, tor, [
        (cx - body_w + lean, torso_top), (cx + body_w + lean, torso_top),
        (cx + body_w, torso_bot), (cx - body_w, torso_bot)])
    pygame.draw.polygon(surf, tor_dk, [
        (cx - body_w + lean, torso_top), (cx + body_w + lean, torso_top),
        (cx + body_w, torso_bot), (cx - body_w, torso_bot)], 1)
    pygame.draw.line(surf, _retint((198, 62, 52), night),
                     (cx - body_w, torso_top + 5), (cx + body_w, torso_top + 1), 2)
    pygame.draw.line(surf, gold, (cx - body_w, torso_top + 6), (cx + body_w, torso_top + 2), 1)
    sh_y = torso_top + 2
    hx, hy = (cx + lean, torso_top - 4) if head_at is None else head_at
    if arms == 'staff':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor, (cx + sgn * body_w, sh_y), (cx + sgn * 5, sh_y + 2), 2)
    elif arms == 'up':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor, (cx + sgn * body_w, sh_y), (cx + sgn * 6, sh_y - 8), 2)
    elif arms == 'grip':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor, (cx + sgn * body_w, sh_y), (cx + sgn * 3, sh_y + 8), 2)
    elif arms == 'climb':
        pygame.draw.line(surf, tor, (cx - body_w, sh_y), (cx - 9, sh_y - 7), 2)
        pygame.draw.line(surf, tor, (cx + body_w, sh_y), (cx + 5, sh_y + 5), 2)
    else:
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor, (cx + sgn * body_w, sh_y), (cx + sgn * 4, sh_y + 6), 2)
    draw_monkey_mask(surf, hx, hy, night, r=4, plume=t * 3.0, plume_dir=plume_dir,
                     sweep=sweep)
    return sh_y


STAFF_R = 18


def beat_staff_spin(surf, cx, night, t, *, feet=NEAR_GROUND_Y):
    """BEAT 1 (2.0 s) — the staff spin. Silhouette event: a WIDE HORIZONTAL
    lens — the acrobat crouches into a low horse stance and the staff sweeps
    through it, so the pose is genuinely wider than it is tall and the plumes
    lie back instead of standing up."""
    sh_y = _acrobat(surf, cx, feet, night, h=22, t=t, legs='crouch',
                    arms='staff', sweep=0.30)
    spin = t * 3.0 * math.tau
    cy = sh_y + 1
    staff = _cap_to(_retint((198, 172, 104), night), 128)
    staff_dk = _shade(staff, -44)
    # the blur arc: a flattened 1 px ellipse the bar sweeps out — motion, not a
    # hoop the figure stands inside
    pygame.draw.ellipse(surf, staff_dk, (cx - STAFF_R, cy - 4, STAFF_R * 2, 9), 1)
    for k, a_off in enumerate((0.0, 0.35, 0.7)):
        a = spin - a_off
        ex = cx + math.cos(a) * (STAFF_R - 1)
        ey = cy + math.sin(a) * 3.4
        w = 2 if k == 0 else 1
        col = staff if k == 0 else staff_dk
        pygame.draw.line(surf, col, (cx - (ex - cx), cy - (ey - cy)), (ex, ey), w)
    # the banded ends of the Ruyi Jingu Bang — two gold cuffs, the only detail
    for sgn in (-1, 1):
        ex = cx + sgn * math.cos(spin) * (STAFF_R - 1)
        ey = cy + sgn * math.sin(spin) * 3.4
        pygame.draw.circle(surf, _cap_to(_retint((222, 188, 96), night), 128), (int(ex), int(ey)), 1)


def beat_tower(surf, cx, night, t, *, feet=NEAR_GROUND_Y):
    """BEAT 2 (2.4 s) — the two-man shoulder tower, the third acrobat climbing:
    a TALL VERTICAL column crossed by one diagonal limb, locked on a gong hit."""
    _acrobat(surf, cx, feet, night, h=19, t=t, legs='brace', arms='grip',
             torso=(178, 74, 56))
    top_feet = feet - 17
    sway = math.sin(t * 1.4) * 1.0
    _acrobat(surf, int(cx + sway), top_feet, night, h=17, t=t + 0.4, legs='stand',
             arms='up', torso=(206, 96, 62))
    # the climber, hooked on the base's left side, one arm reaching for the top
    _acrobat(surf, cx - 10, feet, night, h=17, t=t + 0.8, legs='none', arms='climb',
             torso=(190, 132, 62), plume_dir=-1)
    tor = _retint((190, 132, 62), night)
    pygame.draw.line(surf, tor, (cx - 10, feet - 12), (cx - 6, feet - 3), 2)
    pygame.draw.line(surf, tor, (cx - 10, feet - 10), (cx - 4, feet - 9), 2)


def beat_somersault(surf, cx, night, t, *, feet=NEAR_GROUND_Y, air=1.0):
    """BEAT 3 (1.5 s) — the dismount: a compact tucked BALL, AIRBORNE, with a
    visible gap of paving under it. Nothing else in the cast ever leaves the
    ground, so the beat is unmistakable even in one frame."""
    g = feet
    arc = math.sin(max(0.0, min(1.0, air)) * math.pi)
    bx = cx
    by = g - 6 - int(arc * 16)
    tor = _retint((196, 84, 62), night)
    tor_dk = _shade(tor, -36)
    gold = _cap_to(_retint((214, 182, 96), night), 130)
    spin = air * math.tau * 1.25
    pygame.draw.circle(surf, tor_dk, (bx, by), 7)
    pygame.draw.circle(surf, tor, (bx, by), 6)
    pygame.draw.arc(surf, gold, (bx - 6, by - 6, 13, 13), spin, spin + 2.4, 2)
    for k in (0, 1):
        a = spin + k * 2.1
        pygame.draw.line(surf, tor_dk, (bx + int(math.cos(a) * 3), by + int(math.sin(a) * 3)),
                         (bx + int(math.cos(a) * 7), by + int(math.sin(a) * 7)), 2)
    # the masked head tucked into the ball, plumes streaming out of the roll
    hx = bx + int(math.cos(spin + 3.4) * 4)
    hy = by + int(math.sin(spin + 3.4) * 4)
    draw_monkey_mask(surf, hx, hy, night, r=3, plume=spin, plume_dir=-1)
    # a compressed ground shadow keeps the ball ANCHORED while it is in air
    sh = pygame.Surface((16, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (10, 10, 16, int(90 * (1.0 - 0.5 * arc))), (0, 0, 16, 4))
    surf.blit(sh, (bx - 8, g - 2))


TROUPE_CYCLE = 5.9                   # spin 2.0 s · tower 2.4 s · somersault 1.5 s


def draw_troupe(surf, cx, night, t, *, feet=NEAR_GROUND_Y):
    """The three beats as ONE act: the troupe cycles spin -> tower ->
    somersault, so however long the square stays on screen it is mid-act."""
    tc = t % TROUPE_CYCLE
    if tc < 2.0:
        beat_staff_spin(surf, cx, night, t, feet=feet)
    elif tc < 4.4:
        beat_tower(surf, cx, night, t, feet=feet)
    else:
        beat_somersault(surf, cx, night, t, feet=feet, air=(tc - 4.4) / 1.5)


# ════════════════════════════════════════════════════════════════════════════
# A11 — FOOD THEATRE. Overlays on the SHIPPED stall shell, not new stalls:
# at the second crest the market gets more interesting as it gets slightly
# less crowded, because three stalls PERFORM.
# ════════════════════════════════════════════════════════════════════════════

TANGHULU_CAP_Y = 546


def theatre_noodle(surf, sx, night, t, *, base_y=FAR_BASE):
    """The NOODLE-PULLER: arms thrown wide with a dough ribbon doubling
    1 -> 2 -> 4 -> 8 on a 4-step 0.9 s cycle. On folds 2 and 4 the dough is
    genuinely THROWN — the loops arc up over the awning line, borrowing the
    ceiling the shipped steamer's stack already occupies."""
    cy = base_y - 15
    st = int((t / 0.225) % 4)
    strands = (1, 2, 4, 8)[st]
    throw = st in (1, 3)
    lift = (0, 8, 1, 8)[st]
    rise = (0, 38, 0, 40)[st]
    tor = _retint((150, 138, 120), night)
    body_top = cy - 13
    pygame.draw.polygon(surf, tor, [(sx - 4, body_top), (sx + 4, body_top),
                                    (sx + 5, cy), (sx - 5, cy)])
    pygame.draw.polygon(surf, _shade(tor, -34), [(sx - 4, body_top), (sx + 4, body_top),
                                                 (sx + 5, cy), (sx - 5, cy)], 1)
    skin = _retint(SKIN, night)
    pygame.draw.circle(surf, skin, (sx, body_top - 4), 3)
    pygame.draw.circle(surf, _retint((54, 44, 38), night), (sx, body_top - 4), 3, 1)
    span = 15
    lh = (sx - span, body_top - 1 - lift)
    rh = (sx + span, body_top - 1 - lift)
    pygame.draw.line(surf, tor, (sx - 4, body_top + 2), lh, 2)
    pygame.draw.line(surf, tor, (sx + 4, body_top + 2), rh, 2)
    pygame.draw.circle(surf, skin, lh, 1)
    pygame.draw.circle(surf, skin, rh, 1)
    dough = _cap_to(_retint((228, 218, 194), night), 130)
    dough_dk = _shade(dough, -40)
    # `strands` loops between the hands: folds 1 and 3 SAG; folds 2 and 4 are
    # thrown, so the same loops invert and arc up over the awning.
    for k in range(strands):
        sag = 8 - k * (6.0 / max(1, strands))
        amp = (rise - k * 1.8) if throw else sag
        pts = []
        for i in range(11):
            f = i / 10.0
            x = lh[0] + (rh[0] - lh[0]) * f
            bow = math.sin(f * math.pi) * amp
            yv = (lh[1] - bow - k * 0.9) if throw else (lh[1] + bow + k * 0.9)
            pts.append((int(x), int(yv)))
        pygame.draw.lines(surf, dough_dk if k % 2 else dough, False, pts, 1)
    board = _retint((150, 122, 84), night)
    pygame.draw.rect(surf, board, (sx - 12, cy - 3, 24, 3))
    if st in (1, 3):
        _wisp(surf, sx, cy - 4, t, n=2, rise=9, spread=1.6, peak_a=40, r0=1,
              sway=1.6, color=(216, 210, 198))


def theatre_sugar(surf, sx, night, t, *, base_y=FAR_BASE):
    """The SUGAR-PAINTER: seated, a wand over a flat slab, pouring an amber
    line-drawing that resolves into a disc on a stick. The pour is the ONE
    downward motion of the whole night, which is why it earns its contrast."""
    cy = base_y - 15
    ph = int((t / 1.4) % 3)
    slab = _cap_to(_retint((198, 194, 186), night), 126)
    pygame.draw.rect(surf, _shade(slab, -34), (sx - 8, cy - 5, 18, 5))
    pygame.draw.rect(surf, slab, (sx - 7, cy - 4, 16, 3))
    tor = _retint((110, 124, 148), night)
    seat_y = cy - 1
    pygame.draw.polygon(surf, _shade(tor, -30), [(sx - 16, seat_y), (sx - 6, seat_y),
                                                 (sx - 7, seat_y - 5), (sx - 15, seat_y - 5)])
    pygame.draw.rect(surf, tor, (sx - 16, cy - 13, 8, 9))
    pygame.draw.rect(surf, _shade(tor, -34), (sx - 16, cy - 13, 8, 9), 1)
    skin = _retint(SKIN, night)
    # A SEATED figure buys the vertical budget the lifted disc needs.
    pygame.draw.circle(surf, skin, (sx - 12, cy - 16), 3)
    pygame.draw.circle(surf, _retint((56, 46, 40), night), (sx - 12, cy - 16), 3, 1)
    amber = _cap_to(_retint((198, 146, 62), night), 126) if night > 0.05 else (214, 160, 68)
    if ph < 2:
        wand = (sx - 4 + ph * 4, cy - 11)
        pygame.draw.line(surf, tor, (sx - 9, cy - 11), wand, 2)
        pygame.draw.line(surf, _retint((140, 116, 78), night), wand, (wand[0] + 3, cy - 8), 1)
        # the falling thread of hot sugar + the trail already on the slab
        pygame.draw.line(surf, amber, (wand[0] + 3, cy - 8), (wand[0] + 3, cy - 5), 1)
        pts = [(sx - 6, cy - 4), (sx - 3, cy - 6), (sx, cy - 4), (sx + 3, cy - 6)]
        pygame.draw.lines(surf, amber, False, pts[:2 + ph * 2], 1)
        if ph == 1:
            pygame.draw.circle(surf, amber, (sx + 3, cy - 6), 1)
    else:
        # the FINISHED disc lifted on its stick — a lollipop of poured sugar
        pygame.draw.line(surf, tor, (sx - 9, cy - 11), (sx - 1, cy - 14), 2)
        pygame.draw.line(surf, _retint((150, 124, 82), night), (sx - 1, cy - 14), (sx + 4, cy - 16), 1)
        pygame.draw.circle(surf, _shade(amber, -40), (sx + 6, cy - 16), 4)
        pygame.draw.circle(surf, amber, (sx + 6, cy - 16), 3)
        pygame.draw.arc(surf, _shade(amber, -46), (sx + 3, cy - 19, 7, 7),
                        math.radians(200), math.radians(340), 1)


def theatre_tanghulu(surf, sx, night, t, *, base_y=FAR_BASE):
    """The TANGHULU RACK: a FREESTANDING straw pole planted at the stall's
    edge, skewers bristling — a spiky radially-symmetric silhouette the stall
    row does not otherwise contain, clear of the awning line so it reads
    against open sky."""
    g = base_y
    pole_x = sx + HALF_W + 11
    top = TANGHULU_CAP_Y + 2
    straw = _retint((186, 162, 104), night)
    pygame.draw.rect(surf, _shade(straw, -34), (pole_x - 4, top, 8, g - top))
    pygame.draw.rect(surf, straw, (pole_x - 3, top + 1, 6, g - top - 2))
    for k in range(6):
        pygame.draw.line(surf, _shade(straw, -28), (pole_x - 3, top + 6 + k * 7),
                         (pole_x + 2, top + 6 + k * 7), 1)
    pygame.draw.ellipse(surf, _shade(straw, 12), (pole_x - 4, top - 2, 9, 4))
    # a cross-foot on the paving: a tall pole has to read as PLANTED
    foot = _retint((120, 96, 62), night)
    pygame.draw.rect(surf, foot, (pole_x - 7, g - 3, 15, 3))
    pygame.draw.rect(surf, _shade(foot, -26), (pole_x - 7, g - 3, 15, 3), 1)
    stick = _retint((172, 148, 100), night)
    red = _cap_to(_retint((214, 58, 52), night), 120) if night > 0.05 else (222, 62, 54)
    red_dk = _shade(red, -38)
    # 5 skewers per side, splayed at alternating angles so no two overlap
    for k in range(5):
        for sgn in (-1, 1):
            ang = math.radians(20 + k * 13 + (6 if sgn > 0 else 0))
            ay = top + 5 + k * 4
            ex = pole_x + sgn * int(math.cos(ang) * 13)
            ey = ay - int(math.sin(ang) * 4)
            pygame.draw.line(surf, stick, (pole_x + sgn * 3, ay), (ex, ey), 1)
            for b in range(3):
                f = 0.45 + b * 0.26
                bx = int(pole_x + sgn * 3 + (ex - pole_x - sgn * 3) * f)
                by = int(ay + (ey - ay) * f)
                pygame.draw.circle(surf, red_dk, (bx, by), 2)
                pygame.draw.circle(surf, red, (bx, by), 1)
    _glow(surf, pole_x, top + 13, night, radius=8, peak=22, color=(140, 76, 60))


THEATRE_OVERLAYS = {
    'noodle': theatre_noodle,
    'sugar': theatre_sugar,
    'tanghulu': theatre_tanghulu,
}


# ════════════════════════════════════════════════════════════════════════════
# A12 — WALK-AND-EAT HAND PROPS. Four items that must read on an 18 px figure,
# so each is a different SHAPE EVENT, not a different colour: a horizontal
# bar, a pale dome, a vertical bead-stack, a stubby steaming block.
# ════════════════════════════════════════════════════════════════════════════

def draw_hand_food(surf, hx, hy, night, kind, face=1):
    if kind == 'skewer':
        stick = _retint((166, 140, 92), night)
        pygame.draw.line(surf, stick, (hx - 1, hy), (hx + face * 8, hy - 2), 1)
        meat = _retint((146, 84, 58), night)
        for k in range(3):
            mx = hx + face * (2 + k * 2)
            pygame.draw.rect(surf, meat, (mx, hy - 1 - k // 2, 2, 3))
            pygame.draw.line(surf, _shade(meat, 22), (mx, hy - 1 - k // 2), (mx + 1, hy - 1 - k // 2), 1)
    elif kind == 'bun':
        bun = _cap_to(_retint((228, 220, 202), night), 132)
        pygame.draw.circle(surf, _shade(bun, -30), (hx + face * 3, hy - 1), 3)
        pygame.draw.circle(surf, bun, (hx + face * 3, hy - 1), 2)
        pygame.draw.circle(surf, _shade(bun, -34), (hx + face * 3, hy - 3), 1)
    elif kind == 'tanghulu':
        # THE festival prop: three red beads on a stick — deliberately the
        # hottest of the four, and still capped well under the coin.
        stick = _retint((172, 148, 100), night)
        pygame.draw.line(surf, stick, (hx + face * 2, hy + 1), (hx + face * 2, hy - 9), 1)
        red = _cap_to(_retint((214, 58, 52), night), 120) if night > 0.05 else (222, 62, 54)
        for k in range(3):
            by = hy - 2 - k * 3
            pygame.draw.circle(surf, _shade(red, -34), (hx + face * 2, by), 2)
            pygame.draw.circle(surf, red, (hx + face * 2, by), 1)
    else:  # 'cup'
        cup = _cap_to(_retint((206, 200, 186), night), 130)
        pygame.draw.polygon(surf, cup, [(hx + face * 1, hy - 4), (hx + face * 5, hy - 4),
                                        (hx + face * 4, hy + 1), (hx + face * 2, hy + 1)])
        pygame.draw.polygon(surf, _shade(cup, -34), [(hx + face * 1, hy - 4), (hx + face * 5, hy - 4),
                                                     (hx + face * 4, hy + 1), (hx + face * 2, hy + 1)], 1)
        pygame.draw.line(surf, _retint((150, 90, 70), night),
                         (hx + face * 1, hy - 4), (hx + face * 5, hy - 4), 1)


HAND_FOODS = ('tanghulu', 'skewer', 'bun', 'cup')


# ════════════════════════════════════════════════════════════════════════════
# A14 — THE VENDOR STEP-OUT. For the seconds the dragon passes, the market
# withdraws its own signature: the vendor leaves the counter, stands BESIDE it
# at the front edge, faces the parade and puts a hand up over the brow.
# ════════════════════════════════════════════════════════════════════════════

def draw_vendor_stepout(surf, sx, night, t, *, feet=FAR_BASE):
    coat = _retint((150, 96, 74), night)
    coat_dk = _shade(coat, -34)
    skin = _retint(SKIN, night)
    hair = _retint((52, 42, 34), night)
    h = 19
    head_r = 3
    torso_h = int(h * 0.46)
    body_w = max(3, int(h * 0.26))
    torso_bot = feet - (h - torso_h - head_r * 2)
    torso_top = torso_bot - torso_h
    hy = torso_top - head_r
    for sgn in (-1, 1):
        pygame.draw.line(surf, coat_dk, (sx + sgn * 2, torso_bot), (sx + sgn * 2, feet), 2)
    pygame.draw.polygon(surf, coat, [
        (sx - body_w, torso_top), (sx + body_w, torso_top),
        (sx + body_w + 1, torso_bot), (sx - body_w - 1, torso_bot)])
    pygame.draw.polygon(surf, coat_dk, [
        (sx - body_w, torso_top), (sx + body_w, torso_top),
        (sx + body_w + 1, torso_bot), (sx - body_w - 1, torso_bot)], 1)
    ap = _retint((206, 196, 176), night)
    pygame.draw.rect(surf, ap, (sx - body_w + 1, torso_top + 3, body_w * 2 - 1, torso_h - 2))
    pygame.draw.rect(surf, _shade(ap, -34), (sx - body_w + 1, torso_top + 3, body_w * 2 - 1, torso_h - 2), 1)
    sh_y = torso_top + 2
    # one arm up over the brow — the shielding/waving step-out gesture
    pygame.draw.line(surf, coat, (sx + body_w, sh_y), (sx + 2, hy - 4), 2)
    pygame.draw.line(surf, skin, (sx + 2, hy - 4), (sx - 3, hy - 4), 2)
    pygame.draw.line(surf, coat, (sx - body_w, sh_y), (sx - body_w - 1, sh_y + 6), 2)
    pygame.draw.circle(surf, skin, (sx, hy), head_r)
    pygame.draw.circle(surf, hair, (sx, hy - 1), head_r)
    pygame.draw.arc(surf, hair, (sx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                    math.radians(0), math.radians(180), 2)
    pygame.draw.circle(surf, (34, 24, 20), (sx + 1, hy), 0)
