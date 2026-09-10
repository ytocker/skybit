"""Scratch renderer for the `frost-lich` epic-boss concept (round 2).

An ancient FROZEN sorcerer-king: a gaunt skeletal monarch sealed in tattered
glacial robes, jagged crown, radiating cold light. The boss set's anti-titan —
the tallest, narrowest, most rigidly VERTICAL silhouette, built as an obelisk
column so it can't be confused with the bulky leviathan or a chibi clown.
Headless-safe (SDL_VIDEODRIVER=dummy).

Palette is biased hard to necro TEAL-CYAN on purpose: this is one of two undead
entries, and a sibling specter owns spectral pale-GREEN, so HUE is the only
thing that keeps them apart. Cyan glow carries the figure on a bright day sky;
deep frost-navy holds the silhouette at night while the cyan reads as light.

PROP DECISION (proven with the mirrored pillar-fit thumbnail below): the
signature prop is a SOUL-STANDARD — a tall bone pole topped by a caged glowing
soul-orb with a banner cloth hanging from the crossbar. It is the right prop
because it is already a vertical column, and the caged orb gives a strong, single
NODE: when the standard becomes the scrolling pillar (mirrored top+bottom around
the gap) the two orb-cages meet AT the gap, so the rhythm reads as "shaft → cage
NODE → gap → cage NODE → shaft" — a clean obstacle with the lit orb framing the
opening the bird must thread.

The scrolling pole is built from a STRICT repeating vertebra unit so any vertical
crop tiles seamlessly (the obstacle scrolls continuously); the gap-orb node is a
locked-size focal that is the brightest value in the whole asset.
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

# ── locked brief palette (BLUE/teal-biased on purpose) ───────────────────────
TEAL      = (120, 230, 224)   # necro teal-cyan — THE focal glow (NOT green)
TEAL_HOT  = (205, 252, 250)   # hottest soul-core, near-white cyan bloom
TEAL_DIM  = (52, 150, 156)    # teal in shadow / eye-socket fill
BONE       = (228, 222, 200)  # bone ivory — skull + shaft + crown shards
BONE_DK    = (150, 146, 132)  # bone in occlusion
BONE_HI    = (248, 246, 234)  # bone rim light
NAVY       = (28, 40, 72)      # deep frost-navy shadow — robe core + night hold
NAVY_DK    = (16, 24, 46)      # darkest robe occlusion / under-hem
ROBE_MID   = (44, 78, 112)     # robe mid where cyan ambient grazes the cloth
ROBE_HI    = (78, 140, 168)    # icy robe highlight, leans cyan not white

DAY_BG  = ((150, 205, 232), (96, 168, 214))   # bright sky → cyan glow still pops
NIGHT_BG = ((12, 16, 38), (26, 36, 66))        # dark sky → navy holds, cyan glows

# A bone vertebra repeats every VERT_PITCH px down the scrolling pole. Locking
# the pitch (instead of a per-row jitter) is what makes a vertical crop seamless.
VERT_PITCH = 12


def _lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _vgrad(surf, rect, top, bot):
    x, y, w, h = rect
    for i in range(h):
        pygame.draw.line(surf, _lerp(top, bot, i / max(1, h - 1)),
                         (x, y + i), (x + w - 1, y + i))


def _glow(surf, cx, cy, r, color, alpha=150, falloff=1.9):
    """Additive radial bloom — the soul-light reads as LIGHT, not flat paint."""
    g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    for rr in range(r, 0, -1):
        t = (rr / r) ** falloff
        a = int(alpha * (1 - t))
        pygame.draw.circle(g, (*color, max(0, a)), (r + 1, r + 1), rr)
    surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


# ── strict repeating bone-pole unit (seamless vertical tile) ─────────────────

def _bone_pole_segment(surf, cx, seg_top, half=5):
    """ONE vertebra. Drawn identically every VERT_PITCH px so the column tiles
    with no seam when scrolled: a flat bone shaft slab, a single carved disc, and
    ONE consistent rim-light edge on the same side every time. The disc sits at
    the same offset within every unit, so cropping anywhere lands mid-pattern."""
    # the shaft slab for this unit (fills the full pitch so units butt cleanly)
    pygame.draw.rect(surf, BONE, (cx - half, seg_top, half * 2, VERT_PITCH))
    # one carved vertebra disc, fixed offset inside the unit
    disc_y = seg_top + VERT_PITCH // 2
    pygame.draw.line(surf, BONE_DK, (cx - half, disc_y), (cx + half, disc_y), 2)
    pygame.draw.line(surf, NAVY_DK, (cx - half, seg_top), (cx + half, seg_top), 1)
    # ONE consistent rim-light edge (always the left) — identical per unit
    pygame.draw.line(surf, BONE_HI, (cx - half + 1, seg_top),
                     (cx - half + 1, seg_top + VERT_PITCH - 1), 1)


def _bone_pole(surf, cx, y0, y1, half=5):
    """Tile the vertebra unit from y0 to y1 on the EXACT VERT_PITCH grid so the
    phase is identical no matter where the run starts (top half mirrors bottom)."""
    # snap the first whole unit to the global pitch grid → phase is deterministic
    start = y0 - (y0 % VERT_PITCH)
    yy = start
    while yy < y1:
        _bone_pole_segment(surf, cx, yy, half)
        yy += VERT_PITCH


# ── soul-orb-in-cage primitive — the rhythmic NODE / pillar gap focal ────────

def _soul_cage(surf, cx, cy, r, ring=True):
    """A glowing cyan soul caged in bone claw-ribs. This is the BRIGHTEST value
    in the asset so it reads as the gap node on a busy day sky: layered cyan core
    + outer halo + an optional thin cyan containment ring for legibility."""
    # cold halo first so ribs + ring sit on top of the bloom. Kept TEAL-tinted
    # (not near-white) and falloff-tight so the caged structure stays legible —
    # an over-bright bloom blew the cage out into a featureless blob on day sky.
    _glow(surf, cx, cy, int(r * 1.9), TEAL, alpha=120, falloff=2.4)
    # the caged soul-orb: layered cyan core, hottest near-white at centre
    pygame.draw.circle(surf, TEAL_DIM, (cx, cy), r)
    pygame.draw.circle(surf, TEAL, (cx, cy), int(r * 0.80))
    pygame.draw.circle(surf, TEAL_HOT, (cx - 1, cy - 1), int(r * 0.46))
    # four curved bone ribs of the cage — claw-like, meeting at top + bottom
    for side in (-1, 1):
        pygame.draw.lines(surf, BONE, False, [
            (cx, cy - r - 3),
            (cx + side * int(r * 0.96), cy - int(r * 0.40)),
            (cx + side * int(r * 1.02), cy + int(r * 0.40)),
            (cx, cy + r + 3),
        ], 3)
        pygame.draw.lines(surf, BONE_HI, False, [
            (cx, cy - r - 3),
            (cx + side * int(r * 0.6), cy - int(r * 0.45)),
        ], 2)
    # cap knobs where the ribs bind, top + bottom — keeps the node symmetric
    for dy in (-r - 3, r + 3):
        pygame.draw.circle(surf, BONE, (cx, cy + dy), 4)
        pygame.draw.circle(surf, BONE_HI, (cx - 1, cy + dy - 1), 2)
    # thin 2px cyan containment ring so the orb stays legible against bright sky
    if ring:
        pygame.draw.circle(surf, TEAL_HOT, (cx, cy), r + 4, 2)


# ── the soul-standard prop (tall, vertical, top/bottom mirrorable) ───────────

def _soul_standard(surf, cx, top_y, bot_y, banner=True):
    """A bone pole crowned by a caged soul-orb, banner hanging from a crossbar.
    Pole uses the same strict vertebra unit as the scrolling pillar."""
    cage_r = 18
    cage_cy = top_y + cage_r + 6
    cross_y = cage_cy + cage_r + 16
    # the shaft: the strict repeating bone-vertebra column
    _bone_pole(surf, cx, top_y + cage_r * 2, bot_y, half=5)
    # crossbar holding the banner
    pygame.draw.line(surf, BONE, (cx - 22, cross_y), (cx + 22, cross_y), 4)
    for ex in (-22, 22):
        pygame.draw.circle(surf, BONE, (cx + ex, cross_y), 4)
        pygame.draw.circle(surf, TEAL, (cx + ex, cross_y), 2)  # cold finial light
    if banner:
        _banner(surf, cx, cross_y + 2)
    # the crowning caged soul drawn last so it sits over everything
    _soul_cage(surf, cx, cage_cy, cage_r)


def _banner(surf, cx, b_top):
    """A committed tapering war-banner: clear silhouette, a bright cyan soul-
    diamond glyph, and a FORKED (notched-V) bottom edge so it reads as a banner
    and not an ambiguous tab. Tapers inward toward the fork."""
    tw, bw = 20, 13                 # top half-width tapers to bottom half-width
    b_bot = b_top + 78
    fork = 14                       # depth of the central V notch
    pts = [
        (cx - tw, b_top), (cx + tw, b_top),
        (cx + bw, b_bot - 4),
        (cx + int(bw * 0.55), b_bot - fork),   # right prong tip
        (cx, b_bot - 4),                        # central notch
        (cx - int(bw * 0.55), b_bot - fork),   # left prong tip
        (cx - bw, b_bot - 4),
    ]
    pygame.draw.polygon(surf, NAVY, pts)
    # lit left edge so the cloth has form, not a flat slab
    pygame.draw.line(surf, ROBE_MID, (cx - tw + 2, b_top + 2),
                     (cx - bw + 2, b_bot - 8), 3)
    pygame.draw.line(surf, ROBE_HI, (cx - tw + 2, b_top + 2),
                     (cx - bw + 2, b_bot - 8), 1)
    # bright cyan soul-diamond glyph echoing the caged orb
    sx, sy = cx, b_top + 30
    _glow(surf, sx, sy, 12, TEAL, alpha=110, falloff=2.2)
    pygame.draw.polygon(surf, TEAL_DIM, [(sx, sy - 11), (sx + 8, sy),
                                         (sx, sy + 11), (sx - 8, sy)])
    pygame.draw.polygon(surf, TEAL, [(sx, sy - 8), (sx + 5, sy),
                                     (sx, sy + 8), (sx - 5, sy)])
    pygame.draw.polygon(surf, TEAL_HOT, [(sx, sy - 4), (sx + 2, sy),
                                         (sx, sy + 4), (sx - 2, sy)])


# ── crown + skull (must read MEAN in blackout at 1x) ─────────────────────────

def _crown(surf, cx, base_y, w, s):
    """THREE thick tapered crown shards — tall jagged center, shorter asymmetric
    flanks. SOLID blade-wedges only: no thin needles, NO ball finials (those
    revived a jester / insect-feeler read at night). Each shard carries enough
    base mass + height that the skull+crown cluster reads as a jagged CROWNED
    head even at ~58px 1× — the crown must survive small as hard as the skull."""
    band_h = int(8 * s)
    half = w // 2
    # dark solid crown-band behind the shards (KEEP)
    pygame.draw.rect(surf, NAVY_DK, (cx - half, base_y, w, band_h))
    pygame.draw.rect(surf, ROBE_MID, (cx - half, base_y, w, max(1, band_h - 3)))
    pygame.draw.line(surf, ROBE_HI, (cx - half, base_y + 1), (cx + half, base_y + 1), 1)
    # three shards: (x-offset, base half-width, height factor, lean) — asymmetric.
    # Base half-widths are deliberately FAT (the wedge keeps mass most of its
    # length and only points near the tip) so nothing reads as an antenna needle.
    shards = [
        (-int(half * 0.58), 11, 0.92, -1),   # left flank — broad, leans out
        (int(half * 0.04), 14, 1.50, 0),     # tall center — broadest, near-vertical
        (int(half * 0.62), 10, 0.74, 1),     # right flank — broad, shortest
    ]
    for ox, bw, hf, lean in shards:
        bx = cx + ox
        sh = int(44 * s * hf)
        tip = (bx + lean * int(5 * s), base_y - sh)   # lean tilts the blade
        bwp = max(2, int(bw * s))
        # a chunky neck high on the blade keeps the wedge thick most of its run,
        # so the silhouette stays a solid blade — it points only at the very tip
        neck = (bx + int((tip[0] - bx) * 0.62), base_y - int(sh * 0.62))
        nhw = max(1, int(bwp * 0.45))
        pygame.draw.polygon(surf, NAVY_DK, [
            (bx - bwp, base_y), (bx + bwp, base_y),
            (neck[0] + nhw, neck[1]), tip, (neck[0] - nhw, neck[1])])
        pygame.draw.polygon(surf, ROBE_MID, [
            (bx - bwp + 1, base_y), (bx + int(bwp * 0.35), base_y),
            (neck[0] + int(nhw * 0.4), neck[1]), tip])
        # cold rim catching the leading edge — a single 1px tip pixel only, NO
        # round bloom ball (that ball read as a jester finial in blackout)
        pygame.draw.line(surf, BONE_HI, (bx - bwp + 1, base_y - 2), tip, 1)
        pygame.draw.line(surf, TEAL_HOT, tip, (tip[0], tip[1] + 1), 1)


def _skull(surf, cx, cy, w, h):
    """Gaunt, NARROW, MEAN skull: tapered cranium, a downward-V brow ridge cast
    over the sockets, vertical-slit / angular-almond eye-glow, a hairline jaw +
    teeth notch. Built so the FACE reads as a scowl in blackout, not a cute oval."""
    half_w, half_h = w // 2, h // 2
    # cranial dome — narrowed + slightly egg-tapered so it leans vertical
    pygame.draw.ellipse(surf, BONE_DK, (cx - half_w, cy - half_h, w, h))
    pygame.draw.ellipse(surf, BONE, (cx - half_w + 1, cy - half_h + 1, w - 2, h - 2))
    pygame.draw.ellipse(surf, BONE_HI, (cx - half_w + 2, cy - half_h + 2,
                                        w - 8, h - 12), 1)
    # tapering gaunt jaw — narrow chin so the head leans vertical, not round
    jaw_top = cy + int(half_h * 0.30)
    chin_y = cy + int(half_h * 1.18)
    pygame.draw.polygon(surf, BONE, [
        (cx - int(half_w * 0.72), jaw_top),
        (cx + int(half_w * 0.72), jaw_top),
        (cx + int(half_w * 0.30), chin_y),
        (cx - int(half_w * 0.30), chin_y),
    ])
    pygame.draw.polygon(surf, BONE_DK, [
        (cx - int(half_w * 0.72), jaw_top),
        (cx - int(half_w * 0.30), chin_y),
        (cx - int(half_w * 0.16), chin_y),
        (cx - int(half_w * 0.56), jaw_top),
    ])
    # downward-V brow ridge — a single dark chevron pressing over both sockets.
    # This is the menace read: it makes the eyes look like a scowl in blackout.
    brow_y = cy - int(half_h * 0.30)
    pygame.draw.polygon(surf, NAVY_DK, [
        (cx - int(half_w * 0.74), brow_y - int(half_h * 0.10)),
        (cx, brow_y + int(half_h * 0.30)),                       # V dips center
        (cx + int(half_w * 0.74), brow_y - int(half_h * 0.10)),
        (cx + int(half_w * 0.62), brow_y + int(half_h * 0.04)),
        (cx, brow_y + int(half_h * 0.46)),
        (cx - int(half_w * 0.62), brow_y + int(half_h * 0.04)),
    ])
    # eye sockets: ANGULAR ALMOND slits canted inward (toward the nose) so they
    # read as an aggressive squint, each holding a burning cyan soul-flame
    ey = cy + int(half_h * 0.06)
    for side in (-1, 1):
        ex = cx + side * int(half_w * 0.40)
        almond = [
            (ex - side * 7, ey - 1),               # outer (slightly lower)
            (ex, ey - 5),                          # top peak
            (ex + side * 7, ey - 3),               # inner upper (raised → angry)
            (ex + side * 5, ey + 4),               # inner lower
            (ex - side * 6, ey + 4),               # outer lower
        ]
        pygame.draw.polygon(surf, NAVY_DK, almond)
        _glow(surf, ex, ey, 9, TEAL, alpha=180, falloff=1.8)
        # a vertical slit flame inside the socket (not a round dot)
        pygame.draw.polygon(surf, TEAL, [(ex, ey - 4), (ex + 2, ey),
                                         (ex, ey + 4), (ex - 2, ey)])
        pygame.draw.circle(surf, TEAL_HOT, (ex, ey), 2)
    # narrow nasal hollow
    pygame.draw.polygon(surf, NAVY_DK, [(cx, cy + int(half_h * 0.24)),
                                        (cx - 3, cy + int(half_h * 0.54)),
                                        (cx + 3, cy + int(half_h * 0.54))])
    # hairline jaw line + clenched teeth — a dark seam splits upper/lower jaw so
    # the skull has a mouth in blackout. FEWER, CHUNKIER notches (3–4 fat dark
    # gaps with a bright bone ridge between each) so the mean grin holds at 1×
    # instead of muddying into one dark smear.
    pygame.draw.line(surf, NAVY_DK, (cx - int(half_w * 0.5), jaw_top - 1),
                     (cx + int(half_w * 0.5), jaw_top - 1), 2)
    span = int(half_w * 0.46)
    n_tooth = 4                       # 4 chunky teeth → 3 gaps; reads as a grin
    step = (2 * span) / n_tooth
    for k in range(n_tooth):
        tx = int(-span + step * (k + 0.5))
        # bright bone tooth ridge — the extra value-step that keeps the row crisp
        pygame.draw.line(surf, BONE_HI, (cx + tx, jaw_top + 1),
                         (cx + tx, jaw_top + 5), 2)
        # fat dark gap on the right of each tooth (skip the last → row stays inset)
        if k < n_tooth - 1:
            gx = int(tx + step * 0.5)
            pygame.draw.line(surf, NAVY_DK, (cx + gx, jaw_top),
                             (cx + gx, jaw_top + 7), 2)


# ── the full frost-lich figure ───────────────────────────────────────────────

def draw_lich(surf, cx, ground_y, scale=1.0):
    """Assemble the obelisk monarch on a ground line. A tall narrow column: robe
    hem at the ground, robe tapering up to WIDE shoulders, skull + jagged crown
    spiking out the top, soul-standard held to one side as a second vertical line.
    The wide-shoulder → spiked-icicle-hem wedge is the anti-titan read."""
    s = scale
    fig_h = int(360 * s)
    top_y = ground_y - fig_h
    # ── the robe column: WIDE shoulders dropping to a narrower spiked hem.
    # Committing the wedge (broad top, daggered bottom) is the anti-titan move —
    # the figure points DOWN to the hem instead of bulking out like a leviathan.
    shoulder_y = top_y + int(fig_h * 0.30)
    hem_y = ground_y
    shoulder_half = int(48 * s)     # broadened ~20% over round 1
    hem_half = int(40 * s)          # narrower than shoulders → dramatic taper
    waist_y = shoulder_y + int((hem_y - shoulder_y) * 0.45)
    waist_half = int(30 * s)        # pinch the waist so the wedge is read clearly
    robe_pts = [
        (cx - shoulder_half, shoulder_y),
        (cx + shoulder_half, shoulder_y),
        (cx + waist_half, waist_y),
        (cx + hem_half, hem_y),
        (cx - hem_half, hem_y),
        (cx - waist_half, waist_y),
    ]

    def _robe_half(yy):
        if yy <= waist_y:
            t = (yy - shoulder_y) / max(1, waist_y - shoulder_y)
            return int(_lerp((shoulder_half, 0, 0), (waist_half, 0, 0), t)[0])
        t = (yy - waist_y) / max(1, hem_y - waist_y)
        return int(_lerp((waist_half, 0, 0), (hem_half, 0, 0), t)[0])

    # vertical body gradient clipped to the robe silhouette
    body = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for yy in range(shoulder_y, hem_y):
        t = (yy - shoulder_y) / max(1, hem_y - shoulder_y)
        col = _lerp(ROBE_MID, NAVY_DK, t ** 0.7)
        hw = _robe_half(yy)
        pygame.draw.line(body, col, (cx - hw, yy), (cx + hw, yy))
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), robe_pts)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (0, 0))
    # central cold seam of light down the robe (KEEP) — one clean cyan line
    pygame.draw.line(surf, ROBE_HI, (cx, shoulder_y + 4), (cx, hem_y - 6), 2)
    _glow(surf, cx, shoulder_y + int(fig_h * 0.34), int(22 * s), TEAL,
          alpha=40, falloff=2.6)
    # chest soul-orb — secondary focal (KEEP) seated where the seam crosses chest
    chest_cy = shoulder_y + int(fig_h * 0.30)
    _glow(surf, cx, chest_cy, int(18 * s), TEAL, alpha=120, falloff=2.1)
    pygame.draw.circle(surf, TEAL, (cx, chest_cy), int(9 * s))
    pygame.draw.circle(surf, TEAL_HOT, (cx, chest_cy - 1), int(4 * s))
    pygame.draw.polygon(surf, BONE, [(cx, chest_cy - int(13 * s)),
                                     (cx + int(13 * s), chest_cy),
                                     (cx, chest_cy + int(13 * s)),
                                     (cx - int(13 * s), chest_cy)], 2)
    # sparse long frost-folds — NOT busy texture
    for fx in (-int(hem_half * 0.6), int(hem_half * 0.6)):
        pygame.draw.line(surf, NAVY_DK,
                         (cx + int(fx * 0.4), waist_y),
                         (cx + fx, hem_y - 2), 2)
        pygame.draw.line(surf, ROBE_HI,
                         (cx + int(fx * 0.4) - 2, waist_y),
                         (cx + fx - 2, hem_y - 2), 1)
    # ── DEEP icicle-dagger hem — long sharp teeth, not a shallow zigzag fringe ──
    n = 5
    icic = [(cx - hem_half, hem_y - 8)]
    for k in range(n):
        x0 = cx - hem_half + int((k + 0.0) / n * hem_half * 2)
        x1 = cx - hem_half + int((k + 0.5) / n * hem_half * 2)
        x2 = cx - hem_half + int((k + 1.0) / n * hem_half * 2)
        icic.append((x0, hem_y - 4))
        icic.append((x1, hem_y + int(34 * s)))   # long dagger point
        icic.append((x2, hem_y - 4))
    icic.append((cx + hem_half, hem_y - 8))
    pygame.draw.polygon(surf, NAVY_DK, icic)
    # cold rim catching the leading edge of each icicle dagger
    for k in range(n):
        x1 = cx - hem_half + int((k + 0.5) / n * hem_half * 2)
        x0 = cx - hem_half + int((k + 0.0) / n * hem_half * 2)
        pygame.draw.line(surf, ROBE_HI, (x0, hem_y - 4), (x1, hem_y + int(34 * s)), 1)
    # ── high collar / mantle framing the skull, sweeping up into points ──
    coll = [
        (cx - shoulder_half, shoulder_y + int(8 * s)),
        (cx - int(shoulder_half * 0.5), shoulder_y - int(46 * s)),
        (cx, shoulder_y - int(22 * s)),
        (cx + int(shoulder_half * 0.5), shoulder_y - int(46 * s)),
        (cx + shoulder_half, shoulder_y + int(8 * s)),
    ]
    pygame.draw.polygon(surf, NAVY, coll)
    pygame.draw.lines(surf, ROBE_HI, False, coll[:3], 1)
    # skull seated in the collar
    skull_w, skull_h = int(40 * s), int(56 * s)   # narrowed ~15% (was 46 wide)
    skull_cy = shoulder_y - int(22 * s)
    _skull(surf, cx, skull_cy, skull_w, skull_h)
    # jagged crown above the skull
    _crown(surf, cx, skull_cy - int(skull_h * 0.55), int(skull_w * 1.15), s)
    # ── skeletal arm holding the soul-standard out to the figure's left ──
    hand_x = cx - int(70 * s)
    hand_y = shoulder_y + int(48 * s)
    pygame.draw.line(surf, NAVY, (cx - int(shoulder_half * 0.7), shoulder_y + int(22 * s)),
                     (hand_x, hand_y), int(10 * s))
    pygame.draw.line(surf, BONE, (hand_x, hand_y - int(12 * s)),
                     (hand_x, hand_y + int(10 * s)), int(7 * s))
    for fx in range(-3, 4, 3):
        pygame.draw.line(surf, BONE, (hand_x + fx, hand_y),
                         (hand_x + fx + 4, hand_y + 6), 2)
    # the standard itself — its own tall vertical line beside the figure
    _soul_standard(surf, hand_x, top_y - int(10 * s), ground_y, banner=True)


# ── pillar-fit proof: the standard mirrored into a top+bottom pillar pair ────

def draw_pillar_fit(surf, cx, top, bot, gap_cy, gap_h):
    """Prove the soul-standard becomes a clean scrolling pillar when mirrored
    around the gap. Top + bottom halves are EXACT mirror images: identical
    vertebra phase (driven off the shared pitch grid), identical-size cage NODE
    on each side. The cage is the brightest value and frames the opening."""
    gap_top = gap_cy - gap_h // 2
    gap_bot = gap_cy + gap_h // 2
    cage_r = 18                                   # locked, identical top + bottom
    # top pillar: cage node sits just above the gap, vertebra shaft above it
    top_cage_cy = gap_top - cage_r - 4
    _bone_pole(surf, cx, top, top_cage_cy - cage_r, half=5)
    _soul_cage(surf, cx, top_cage_cy, cage_r)
    # bottom pillar: EXACT mirror — same cage size, same shaft, same pitch phase
    bot_cage_cy = gap_bot + cage_r + 4
    _bone_pole(surf, cx, bot_cage_cy + cage_r, bot, half=5)
    _soul_cage(surf, cx, bot_cage_cy, cage_r)


# ── compose the review sheet ─────────────────────────────────────────────────

def main():
    pygame.init()
    W, H = 760, 860
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 22, 40))
    font = pygame.font.SysFont("dejavusans", 17, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)

    # two boss panels side by side: DAY (left) and NIGHT (right)
    panel_w, panel_h = 300, 470
    ground_y = 430
    for i, (label, bg) in enumerate([("DAY", DAY_BG), ("NIGHT", NIGHT_BG)]):
        px = 30 + i * (panel_w + 24)
        panel = pygame.Surface((panel_w, panel_h))
        _vgrad(panel, (0, 0, panel_w, panel_h), bg[0], bg[1])
        gcol = _lerp(bg[1], NAVY, 0.5)
        _vgrad(panel, (0, ground_y, panel_w, panel_h - ground_y),
               _lerp(gcol, NAVY, 0.3), NAVY_DK)
        pygame.draw.line(panel, _lerp(TEAL, gcol, 0.6),
                         (0, ground_y), (panel_w, ground_y), 2)
        draw_lich(panel, panel_w // 2 + 26, ground_y, scale=1.0)
        sheet.blit(panel, (px, 56))
        tag = font.render(label, True, TEAL_HOT)
        sheet.blit(tag, (px + 10, 60))

    # pillar-fit thumbnail (far right): mirrored standard → vertical pillar pair
    th_w, th_h = 110, 470
    thx = 30 + 2 * (panel_w + 24)
    if thx + th_w > W:
        th_w = W - thx - 20
    thumb = pygame.Surface((th_w, th_h))
    _vgrad(thumb, (0, 0, th_w, th_h), NIGHT_BG[0], NIGHT_BG[1])
    draw_pillar_fit(thumb, th_w // 2, 0, th_h, th_h // 2, 150)
    sheet.blit(thumb, (thx, 56))

    # ── 1x INSET row: the figure at true in-game size on day + night ──────────
    inset_y = 560
    inset_h = 230
    inset_w = 150
    pygame.draw.line(sheet, (60, 70, 96), (30, inset_y - 14), (W - 30, inset_y - 14), 1)
    itag = font.render("1×  IN-GAME SIZE  (player view)", True, BONE_HI)
    sheet.blit(itag, (30, inset_y - 8))
    # ~58px-tall figure (top of the in-game range): judge crown noise / orb
    # legibility / skull menace at the size the player actually sees
    in_scale = 0.16
    for j, (label, bg) in enumerate([("DAY", DAY_BG), ("NIGHT", NIGHT_BG)]):
        ix = 30 + j * (inset_w + 18)
        ins = pygame.Surface((inset_w, inset_h))
        _vgrad(ins, (0, 0, inset_w, inset_h), bg[0], bg[1])
        g_y = inset_h - 30
        _vgrad(ins, (0, g_y, inset_w, inset_h - g_y),
               _lerp(_lerp(bg[1], NAVY, 0.5), NAVY, 0.3), NAVY_DK)
        pygame.draw.line(ins, _lerp(TEAL, bg[1], 0.6), (0, g_y), (inset_w, g_y), 1)
        # two figures so spacing/repeat reads at native size
        draw_lich(ins, inset_w // 2 - 4, g_y, scale=in_scale)
        sheet.blit(ins, (ix, inset_y + 14))
        sheet.blit(small.render(label, True, TEAL_HOT), (ix + 6, inset_y + 18))

    # a 1x pillar-fit strip beside the figures so gap-orb legibility reads small
    psx = 30 + 2 * (inset_w + 18)
    pstrip = pygame.Surface((inset_w + 30, inset_h))
    _vgrad(pstrip, (0, 0, inset_w + 30, inset_h), DAY_BG[0], DAY_BG[1])
    # narrow it down so the bird-gap rhythm reads at true scroll width
    draw_pillar_fit(pstrip, (inset_w + 30) // 2, 0, inset_h, inset_h // 2 - 6, 64)
    sheet.blit(pstrip, (psx, inset_y + 14))
    sheet.blit(small.render("PILLAR 1× (day)", True, NAVY_DK), (psx + 6, inset_y + 18))

    # titles + captions
    title = font.render("FROST-LICH  —  epic boss  —  round 3", True, BONE_HI)
    sheet.blit(title, (30, 18))
    thtag = small.render("PILLAR-FIT", True, TEAL_HOT)
    sheet.blit(thtag, (thx + 4, 60))
    cap1 = small.render("Mean V-brow skull + 3-shard crown read in blackout; cyan soul-light, NOT green.",
                        True, (200, 210, 225))
    sheet.blit(cap1, (30, H - 38))
    cap2 = small.render("Strict 12px vertebra pole tiles seamlessly; locked-size cage-orb NODE is the gap.",
                        True, (200, 210, 225))
    sheet.blit(cap2, (30, H - 20))

    out = os.path.join(os.path.dirname(__file__), "..",
                       "docs", "epic_boss", "frost-lich", "round_3.png")
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
