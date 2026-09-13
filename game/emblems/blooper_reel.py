"""Bespoke engraved center glyphs for the BLOOPER REEL (Wall of Shame).

Nine anti-trophy glyphs, drawn in the same single-colour engrave idiom as
``game/achievement_icons.py`` (a glyph is ``def _glyph_<id>(surf, cx, cy, r,
col)`` of bold filled polygons / thick lines / discs, stamped twice by the
builder for the struck-relief look). The tarnished cracked-pewter frame and
bronze drip supply the gloom — every glyph here puts the JOKE in the
silhouette so it reads as a comedic fail even rendered in flat pewter.

These are authored against the LOCKED v2 concepts: each id resolves to ONE
decisive shape (no figures-plus-props that mud at 44px). The two-tone accent
(the KFC box) routes through ``_accent`` so it stays bronze-monochrome until
the medal is earned — same rule the live module enforces.

Lives under ``tools/`` so it is never bundled; the render harness monkeypatches
``GLYPHS`` into the live module to preview the real medallion frame.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai

# Reuse the live module's engraved-shadow tone so the dark sockets/recesses in
# these glyphs match the cast-shadow pass the builder stamps around them.
_SH = ai._GLYPH_SH


def _glyph_goose_egg(surf, cx, cy, r, col):
    # A fat hollow zero — the egg ring IS the scoreless run. Dead-simple: the
    # emptiness is the whole joke, so nothing fills the centre. A short crack
    # bites the upper rim and one sad drip-tick hangs off the bottom.
    w = int(r * 0.78)
    h = int(r * 1.06)
    ring = max(4, r // 7)
    pygame.draw.ellipse(surf, col, (cx - w // 2, cy - h // 2, w, h), ring)
    # hairline crack splitting the top of the shell
    cxr = cx + int(r * 0.10)
    pygame.draw.lines(surf, _SH, False, [
        (cxr, cy - h // 2 + ring),
        (cxr - int(r * 0.10), cy - int(r * 0.18)),
        (cxr + int(r * 0.06), cy - int(r * 0.02)),
    ], max(2, r // 12))
    # one limp drip below — "nothing trickled out"
    by = cy + h // 2
    pygame.draw.line(surf, col, (cx, by), (cx, by + int(r * 0.30)), max(2, r // 12))
    pygame.draw.circle(surf, col, (cx, by + int(r * 0.34)), max(2, r // 11))


def _glyph_icarus(surf, cx, cy, r, col):
    # ONE drooping, shedding wing tilted downward beside a bold down-arrow — the
    # plummet, no figure (v2 lock). The wing sags up-top-left while the arrow
    # punches straight down on the right so the FALL reads even at 44px; a lone
    # feather peels off the wingtip.
    # Drooping wing occupying the upper-left: shoulder up-left, tip sagging down.
    sx, sy = cx - r * 0.78, cy - r * 0.52
    tx, ty = cx + r * 0.22, cy + r * 0.10
    cxp, cyp = cx - r * 0.36, cy - r * 0.78   # control bulges the camber up
    leading = []
    for i in range(9):
        t = i / 8
        mt = 1 - t
        bx = mt * mt * sx + 2 * mt * t * cxp + t * t * tx
        by = mt * mt * sy + 2 * mt * t * cyp + t * t * ty
        leading.append((bx, by))
    lobes = [
        (cx - r * 0.02, cy + r * 0.40),
        (cx - r * 0.36, cy + r * 0.30),
        (cx - r * 0.62, cy + r * 0.02),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in leading + lobes])
    # a shed feather drifting away below the wingtip
    fx, fy = cx - int(r * 0.04), cy + int(r * 0.50)
    pygame.draw.ellipse(surf, col, (fx, fy, max(5, int(r * 0.28)),
                                    max(4, int(r * 0.14))))
    # bold downward fall-arrow on the right — the unmistakable plummet
    w = max(4, r // 6)
    ax = cx + int(r * 0.52)
    pygame.draw.line(surf, col, (ax, cy - int(r * 0.60)),
                     (ax, cy + int(r * 0.62)), w)
    pygame.draw.lines(surf, col, False, [
        (ax - int(r * 0.30), cy + int(r * 0.24)),
        (ax, cy + int(r * 0.70)),
        (ax + int(r * 0.30), cy + int(r * 0.24)),
    ], w)


def _glyph_hummingbird(surf, cx, cy, r, col):
    # A panic-flap blur: a BOLD bird-body wedge with TWO thick, well-spaced
    # wing-arcs fanned off its shoulder — the "too many wings on one bird" joke.
    # Dropped from three arcs to two (three collapsed into a wifi/signal fan at
    # 44px) and anchored on a clear body so the bird is never lost.
    bx, by = cx + int(r * 0.30), cy + int(r * 0.10)
    # Bird body — a fat rightward teardrop, clearly the largest mass so the eye
    # locks onto a BIRD before it reads the flapping.
    body = [
        (bx - int(r * 0.14), by - int(r * 0.34)),
        (bx + int(r * 0.40), by - int(r * 0.04)),
        (bx + int(r * 0.12), by + int(r * 0.40)),
        (bx - int(r * 0.30), by + int(r * 0.16)),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in body])
    # eye dot + long needle beak so the body reads unmistakably as a hummingbird
    pygame.draw.circle(surf, _SH, (bx + int(r * 0.10), by - int(r * 0.08)),
                       max(2, r // 12))
    pygame.draw.polygon(surf, col, [
        (bx + int(r * 0.34), by - int(r * 0.12)),
        (bx + int(r * 0.74), by - int(r * 0.02)),
        (bx + int(r * 0.34), by + int(r * 0.04)),
    ])
    # TWO thick motion-blur wing arcs fanned up-left off the shoulder, spaced
    # far enough apart that they read as separate wing ghosts, not a signal fan.
    w = max(4, r // 7)
    sh = (bx - int(r * 0.22), by - int(r * 0.14))
    for sweep, rad in ((0.95, 0.58), (0.62, 0.94)):
        rect = pygame.Rect(sh[0] - int(r * rad), sh[1] - int(r * rad),
                           int(r * rad * 2), int(r * rad * 2))
        a0 = math.radians(105)
        a1 = math.radians(105 + 120 * sweep)
        pygame.draw.arc(surf, col, rect, a0, a1, w)
    # one jitter tick — the frantic shimmer, kept minimal so it doesn't crowd
    pygame.draw.line(surf, col, (bx - int(r * 0.46), by + int(r * 0.44)),
                     (bx - int(r * 0.66), by + int(r * 0.44)), max(2, r // 12))


def _glyph_denial(surf, cx, cy, r, col):
    # A sheet-ghost phasing INTO a pillar edge: the rounded-top scalloped ghost
    # half-overlaps a bold vertical wall on the right, with a "thunk" impact
    # burst where it hits. Ties to the Ghost power-up; the joke is phasing the
    # WRONG way — into the wall, not the gap.
    # the wall the ghost rams — a thick vertical bar on the right
    wall_x = cx + int(r * 0.46)
    wall_w = max(5, int(r * 0.26))
    pygame.draw.rect(surf, col, (wall_x, cy - int(r * 0.92), wall_w, int(r * 1.84)))
    # ghost body: rounded dome + scalloped hem, pushed left so it overlaps wall
    gx = cx - int(r * 0.18)
    gw = int(r * 0.92)
    top = cy - int(r * 0.62)
    dome = pygame.Rect(gx - gw // 2, top, gw, int(r * 0.92))
    pygame.draw.ellipse(surf, col, (dome.x, dome.y, dome.w, dome.h))
    pygame.draw.rect(surf, col, (dome.x, top + int(r * 0.30), gw, int(r * 0.62)))
    # scalloped hem — three bumps
    hy = top + int(r * 0.92)
    bump = gw // 3
    for i in range(3):
        bx = dome.x + bump // 2 + i * bump
        pygame.draw.circle(surf, col, (bx, hy), bump // 2 + 1)
    # carve the hem notches back out with the shadow tone
    for i in range(2):
        nx = dome.x + bump + i * bump
        pygame.draw.circle(surf, _SH, (nx, hy + int(r * 0.06)), bump // 3)
    # two dark eyes
    for dx in (-0.18, 0.14):
        pygame.draw.circle(surf, _SH, (gx + int(dx * r), top + int(r * 0.42)),
                           max(2, r // 9))
    # "thunk" impact burst where ghost meets wall
    ix, iy = wall_x, cy - int(r * 0.06)
    for a in (-0.5, 0.0, 0.5):
        ex = ix + int(math.cos(a) * r * 0.30)
        ey = iy + int(math.sin(a) * r * 0.30)
        pygame.draw.line(surf, col, (ix, iy), (ex, ey), max(2, r // 12))


def _glyph_kfc_incident(surf, cx, cy, r, col):
    # The fry bucket KNOCKED OVER — lying nearly on its side (~70° from upright)
    # with its mouth pointing DOWN-LEFT and fries spilling OUT in a directional
    # fan. Died in fry mode. The spill DIRECTION (out the down-tilted mouth)
    # sells "tipped over" rather than a bucket merely rotated. Distinct from the
    # upright greasy_fingers bucket; the red box accent stays bronze until earned.
    # The tub's local frame: +x runs base->mouth, +y across the mouth. We aim
    # +x down-left so the open mouth faces the ground.
    ang = math.radians(200)
    ca, sa = math.cos(ang), math.sin(ang)
    # Shift the whole bucket up-right so the spilled fan has room below-left.
    bcx, bcy = cx + int(r * 0.30), cy - int(r * 0.18)

    def rot(px, py):
        return (bcx + int(px * ca - py * sa), bcy + int(px * sa + py * ca))

    # Trapezoid tub — wide mouth (toward +x, now down-left), narrower base.
    mouth_l = rot(r * 0.60, -r * 0.52)
    mouth_r = rot(r * 0.60, r * 0.52)
    base_r = rot(-r * 0.34, r * 0.34)
    base_l = rot(-r * 0.34, -r * 0.34)
    tub = [mouth_l, mouth_r, base_r, base_l]
    pygame.draw.polygon(surf, ai._accent((214, 74, 60)), tub)
    pygame.draw.polygon(surf, col, tub, max(2, r // 14))
    # Mouth rim line so the open end reads as the opening the fries pour from.
    pygame.draw.line(surf, col, mouth_l, mouth_r, max(2, r // 13))
    # Fries spilling OUT of the mouth as a tight directional fan, all aimed
    # down-left (the way the bucket is pointing) — a spill, not scattered crumbs.
    mouth_c = rot(r * 0.60, 0)
    for da, ln in ((-0.34, 0.92), (-0.04, 1.02), (0.26, 0.88)):
        fa = ang + da             # roughly along +x, out the mouth, down-left
        sx = mouth_c[0] + int(math.cos(fa) * r * 0.06)
        sy = mouth_c[1] + int(math.sin(fa) * r * 0.06)
        ex = mouth_c[0] + int(math.cos(fa) * r * ln)
        ey = mouth_c[1] + int(math.sin(fa) * r * ln)
        pygame.draw.line(surf, col, (sx, sy), (ex, ey), max(3, r // 9))
    # grease-splat tick where the fries land
    gx, gy = cx - int(r * 0.46), cy + int(r * 0.66)
    pygame.draw.circle(surf, col, (gx, gy), max(3, r // 8))
    pygame.draw.circle(surf, col, (gx + int(r * 0.22), gy + int(r * 0.06)),
                       max(2, r // 13))


def _glyph_so_close(surf, cx, cy, r, col):
    # Abstract "this much" pinch (v2 lock — bars, not fingers): two short
    # HORIZONTAL opposed bars reaching in from left and right toward a clear
    # VERTICAL gap between their tips, with a near-miss spark pinched in the gap.
    # The pinch only reads when the gap is horizontal/obvious, so the bars lie
    # flat and almost meet. No vertical crossbar (that read as a plus/dagger).
    bar_h = max(5, int(r * 0.26))
    bar_len = int(r * 0.62)
    gap = int(r * 0.20)                            # the small horizontal gap
    # left bar reaching right toward the gap
    pygame.draw.rect(surf, col, (cx - gap // 2 - bar_len, cy - bar_h // 2,
                                 bar_len, bar_h), border_radius=max(1, r // 14))
    # right bar reaching left toward the gap
    pygame.draw.rect(surf, col, (cx + gap // 2, cy - bar_h // 2,
                                 bar_len, bar_h), border_radius=max(1, r // 14))
    # near-miss spark pinched in the gap — a compact 4-point twinkle
    s = int(r * 0.22)
    pygame.draw.line(surf, col, (cx, cy - s), (cx, cy + s), max(2, r // 13))
    pygame.draw.line(surf, col, (cx - int(s * 0.5), cy),
                     (cx + int(s * 0.5), cy), max(2, r // 13))
    for dx, dy in ((-0.62, -0.62), (0.62, -0.62), (-0.62, 0.62), (0.62, 0.62)):
        pygame.draw.line(surf, col, (cx, cy),
                         (cx + int(dx * s), cy + int(dy * s)), max(1, r // 18))


def _glyph_lottery_loser(surf, cx, cy, r, col):
    # The slot WINDOW frame with 3 bold MISMATCHED dots and a downward sad-tick.
    # The frame + tone carry it (v2 lock — don't render legible $ / star / skull
    # micro-symbols); the deliberate non-match (three different fills) reads as
    # the loss. A sad down-tick hangs under the window.
    fw = int(r * 1.56)
    fh = int(r * 1.00)
    fx = cx - fw // 2
    fy = cy - fh // 2 - int(r * 0.06)
    # slot-window frame — heavy bezel rectangle
    pygame.draw.rect(surf, col, (fx, fy, fw, fh), max(3, r // 9),
                     border_radius=max(2, r // 7))
    # two reel divider lines splitting the window into three cells
    for i in (1, 2):
        dx = fx + i * fw // 3
        pygame.draw.line(surf, col, (dx, fy + 2), (dx, fy + fh - 2), max(2, r // 14))
    # Three mismatched marks — three OBVIOUSLY different bold shapes so "none
    # match" reads at 44px: a solid DISC, an X-CROSS, and a horizontal BAR.
    # (A disc + hollow-ring pairing looked near-identical and lost the joke.)
    cyc = fy + fh // 2
    c0 = fx + fw // 6
    c1 = fx + fw // 2
    c2 = fx + 5 * fw // 6
    mr = max(4, int(r * 0.20))
    pygame.draw.circle(surf, col, (c0, cyc), mr)                       # disc
    xw = max(3, r // 11)                                               # X-cross
    pygame.draw.line(surf, col, (c1 - mr, cyc - mr), (c1 + mr, cyc + mr), xw)
    pygame.draw.line(surf, col, (c1 - mr, cyc + mr), (c1 + mr, cyc - mr), xw)
    pygame.draw.rect(surf, col, (c2 - mr, cyc - mr // 2, mr * 2, mr),  # bar
                     border_radius=max(1, r // 16))
    # Enlarged sad down-tick (a bold arrow) under the window — the loss.
    sx = cx
    sy = fy + fh + int(r * 0.08)
    aw = max(3, r // 10)
    pygame.draw.line(surf, col, (sx, sy), (sx, sy + int(r * 0.34)), aw)
    pygame.draw.lines(surf, col, False, [
        (sx - int(r * 0.18), sy + int(r * 0.16)),
        (sx, sy + int(r * 0.40)),
        (sx + int(r * 0.18), sy + int(r * 0.16)),
    ], aw)


def _glyph_the_49er(surf, cx, cy, r, col):
    # A snapped sandstone pillar with a small lamp-wisp floating just past its
    # broken top (v2 lock — NO numerals). The snapped shaft = the death at 49;
    # the unreachable genie lamp-wisp = the irony of the 50-pillar genie you
    # never reached.
    shaft_w = max(5, int(r * 0.34))
    px = cx - int(r * 0.22)
    base_y = cy + int(r * 0.84)
    cap_h = max(3, int(r * 0.16))
    cap_w = int(shaft_w * 1.5)
    # base block
    pygame.draw.rect(surf, col, (px - cap_w // 2, base_y - cap_h, cap_w, cap_h),
                     border_radius=max(1, r // 16))
    # lower (standing) stump of the shaft, with a jagged snapped top
    break_y = cy - int(r * 0.04)
    pygame.draw.rect(surf, col, (px - shaft_w // 2, break_y, shaft_w,
                                 base_y - cap_h - break_y))
    # jagged fracture across the break
    pygame.draw.polygon(surf, col, [
        (px - shaft_w // 2, break_y),
        (px - int(shaft_w * 0.12), break_y - int(r * 0.16)),
        (px + int(shaft_w * 0.18), break_y - int(r * 0.04)),
        (px + shaft_w // 2, break_y - int(r * 0.20)),
        (px + shaft_w // 2, break_y),
    ])
    # the toppled upper chunk, fallen aside (tilted) lower-left
    chunk = [
        (px - int(r * 0.58), cy + int(r * 0.30)),
        (px - int(r * 0.18), cy + int(r * 0.18)),
        (px - int(r * 0.06), cy + int(r * 0.52)),
        (px - int(r * 0.46), cy + int(r * 0.64)),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in chunk])
    # The unreachable genie LAMP floating past the broken top (upper-right) — a
    # clear, bold little lamp (rounded body + a triangular spout + a single wisp
    # dot), NOT a curling squiggle (the old thin ellipse + curl read as a music
    # note). The lamp = the genie at 50 the death-at-49 never reached.
    lcx, lcy = cx + int(r * 0.48), cy - int(r * 0.40)
    # Bold rounded body, taller than the old sliver so it reads as a vessel.
    pygame.draw.ellipse(surf, col, (lcx - int(r * 0.30), lcy - int(r * 0.14),
                                    int(r * 0.56), int(r * 0.32)))
    # Triangular spout flicking up to the right.
    pygame.draw.polygon(surf, col, [
        (lcx + int(r * 0.18), lcy - int(r * 0.04)),
        (lcx + int(r * 0.50), lcy - int(r * 0.22)),
        (lcx + int(r * 0.24), lcy + int(r * 0.08)),
    ])
    # Lid knob so the dome reads as a lamp lid.
    pygame.draw.circle(surf, col, (lcx - int(r * 0.04), lcy - int(r * 0.18)),
                       max(2, r // 13))
    # A single wisp dot drifting off the spout — the genie just out of reach.
    pygame.draw.circle(surf, col, (lcx + int(r * 0.44), lcy - int(r * 0.40)),
                       max(2, r // 12))


def _glyph_night_owl(surf, cx, cy, r, col):
    # An owl FACE with X-ed-out eyes and ear-tufts (v2 lock — DROP the moon).
    # A round head, two ear-tufts, two big X eyes joined by a brow ridge, and a
    # small beak. The X eyes = "the night got you" comedic-bleak read.
    head_r = int(r * 0.66)
    pygame.draw.circle(surf, col, (cx, cy + int(r * 0.04)), head_r, max(4, r // 8))
    # two ear-tufts poking up
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.42)
        ey = cy - int(r * 0.40)
        pygame.draw.polygon(surf, col, [
            (ex - int(r * 0.10), ey + int(r * 0.22)),
            (ex + sgn * int(r * 0.16), ey - int(r * 0.20)),
            (ex + int(r * 0.10), ey + int(r * 0.22)),
        ])
    # brow ridge joining the eyes (owl's signature facial-disc bar)
    pygame.draw.line(surf, col, (cx - int(r * 0.42), cy - int(r * 0.10)),
                     (cx + int(r * 0.42), cy - int(r * 0.10)), max(3, r // 11))
    # two X eyes
    ew = max(2, r // 11)
    ex_r = int(r * 0.20)
    for sgn in (-1, 1):
        exc = cx + sgn * int(r * 0.30)
        eyc = cy + int(r * 0.08)
        pygame.draw.line(surf, col, (exc - ex_r, eyc - ex_r),
                         (exc + ex_r, eyc + ex_r), ew)
        pygame.draw.line(surf, col, (exc - ex_r, eyc + ex_r),
                         (exc + ex_r, eyc - ex_r), ew)
    # small beak
    pygame.draw.polygon(surf, col, [
        (cx - int(r * 0.10), cy + int(r * 0.34)),
        (cx + int(r * 0.10), cy + int(r * 0.34)),
        (cx, cy + int(r * 0.54)),
    ])


GLYPHS = {
    "goose_egg": _glyph_goose_egg,
    "icarus": _glyph_icarus,
    "hummingbird": _glyph_hummingbird,
    "denial": _glyph_denial,
    "kfc_incident": _glyph_kfc_incident,
    "so_close": _glyph_so_close,
    "lottery_loser": _glyph_lottery_loser,
    "the_49er": _glyph_the_49er,
    "night_owl": _glyph_night_owl,
}
