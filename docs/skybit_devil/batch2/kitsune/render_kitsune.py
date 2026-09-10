"""
Kitsune — the nine-tailed fox-spirit shrine devil  [COOL GLOW: MINT-GREEN FOXFIRE]

Review-sheet renderer (headless). Draws the ONE locked concept from
batch2/brainstorm_locked15.md: a small SNOW-WHITE fox face with a sharp snout
and tall pointed ears over a slim, compact shrine-priestess haori body, fronted
by a WIDE bushy peacock FAN of nine tails (the dominant read) — the tails pushed
to a GREYER value so the white face pops forward, capped by a coordinated rhythm
of coral eye-spot tips. A tiny MINT-GREEN foxfire orb hovers by one ear. The
torii-gate prop mirrors into a repeatable vermilion shrine-pillar; all at large
+ 32px.

House grammar followed verbatim: chibi proportions, FLAT saturated fills + hard
ink keylines, form via the dark-core -> flat-fill -> top-left rim-sheen TRIAD,
silhouette POP via a 1px outline grown from the alpha mask, supersampled then
smoothscaled down. PINNED PALETTE hexes are used exactly so the foxfire stays
MINT-GREEN — distinct from Yurei's blue-cyan hitodama.

Round 2 fixes (AD critique): the fan was a thin spiky sunburst. It is rebuilt as
a true wide bushy peacock fan — broad scalloped lobes wider than the body is
tall, grouped so the eye reads ~5 lobes, in a GREYER value so the snow-white
face separates and reads as "small fox face in front of a wide fan."
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# ── PINNED PALETTE (verbatim from the locked brief) ──────────────────────────
FUR        = (240, 236, 232)   # snow-white fur base — RESERVED for the FACE
FUR_SH     = (180, 176, 178)   # cool-grey shade — now the TAIL-FAN body value
CORAL      = (238, 120,  72)   # coral-orange ear/tip accent
VERMILION  = (202,  72,  56)   # vermilion torii
MINT       = (150, 224, 196)   # MINT-GREEN foxfire glow (the cool glow)
GOLD       = (224, 186,  84)   # gold haori-trim
INK        = ( 28,  24,  26)   # keyline
SHEEN      = (255, 250, 248)   # top-left rim-sheen

# derived working tones (kept inside the pinned families)
CORAL_SH   = (186,  78,  44)
CORAL_HI   = (250, 168, 120)
VERM_SH    = (150,  46,  38)
VERM_HI    = (228, 112,  92)
GOLD_HI    = (248, 222, 150)
MINT_CORE  = (224, 252, 240)   # near-white foxfire heart
MINT_DEEP  = ( 96, 186, 158)

# tail-fan value lanes: the fan recedes below the snow-white face, so it is
# built one step DOWN in value from FUR. Greyer mid + a darker grey dark-core.
TAIL       = (198, 195, 198)   # tail body — between FUR and FUR_SH, clearly greyer than face
TAIL_SH    = (150, 148, 154)   # tail dark-core (the receded bed under the fan)
TAIL_HI    = (224, 222, 224)   # tail rim-sheen (still below snow-white)

NOSE       = ( 64,  52,  56)   # dark snout-tip / inner-mouth
HAORI_SH   = (162, 158, 162)

SS = 4   # supersample factor


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def grow_outline(src, color=INK, grow=1):
    """1px (post-downscale) ink keyline grown from the alpha mask, the way
    the house silhouette-POP works. Grown at supersample scale so the
    smoothscale carries it down to a crisp 1px."""
    g = grow * SS
    mask = pygame.mask.from_surface(src)
    out_surf = mask.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    w, h = src.get_size()
    canvas = pygame.Surface((w + 2 * g, h + 2 * g), pygame.SRCALPHA)
    for dx in range(-g, g + 1):
        for dy in range(-g, g + 1):
            if dx * dx + dy * dy <= g * g:
                canvas.blit(out_surf, (g + dx, g + dy))
    canvas.blit(src, (g, g))
    return canvas, g


def radial_glow(radius, color, alpha_center=200, falloff=2.0):
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        t = (r / radius) ** falloff
        a = int(alpha_center * (1 - t))
        pygame.draw.circle(s, (*color, max(0, min(255, a))), (c, c), r)
    return s


def smoothdown(surf, target_h):
    ow, oh = surf.get_size()
    scale = target_h / oh
    return pygame.transform.smoothscale(
        surf, (max(1, int(ow * scale)), max(1, int(oh * scale))))


def _foxfire(surf, ocx, ocy, orr, shadow_on=None):
    """A small MINT-GREEN foxfire flame-orb: a teardrop wisp + glow halo.
    Drawn warm-mint so it never reads as Yurei's bluer hitodama. Optionally
    drop-shadowed against the fur so it survives shrink as the one cool accent."""
    if shadow_on is not None:
        # soft dark disc behind the orb so the mint pops off white fur at 1x
        sh = radial_glow(orr + 4 * SS, (40, 44, 52), alpha_center=150, falloff=1.4)
        surf.blit(sh, (ocx - sh.get_width() // 2 + 2 * SS,
                       ocy - sh.get_height() // 2 + 2 * SS))
    glow = radial_glow(orr + 9 * SS, MINT, alpha_center=175, falloff=2.2)
    surf.blit(glow, (ocx - glow.get_width() // 2, ocy - glow.get_height() // 2),
              special_flags=pygame.BLEND_ADD)
    # teardrop flame body (tapered tail pointing up) — hard triad lobes
    flame = [
        (ocx, ocy - int(orr * 2.0)), (ocx + int(orr * 0.8), ocy - int(orr * 0.4)),
        (ocx + int(orr * 0.9), ocy + int(orr * 0.5)),
        (ocx, ocy + orr), (ocx - int(orr * 0.9), ocy + int(orr * 0.5)),
        (ocx - int(orr * 0.8), ocy - int(orr * 0.4)),
    ]
    pygame.draw.polygon(surf, MINT_DEEP, [(x + SS, y + SS) for (x, y) in flame])
    pygame.draw.polygon(surf, MINT, flame)
    pygame.draw.circle(surf, MINT_CORE, (ocx - orr // 4, ocy), int(orr * 0.55))
    pygame.draw.circle(surf, SHEEN, (ocx - orr // 3, ocy - orr // 4), int(orr * 0.22))


# ─────────────────────────────────────────────────────────────────────────────
#  THE NINE-TAIL FAN — a true wide BUSHY peacock fan.
#
#  Built so the EYE reads ~5 broad scalloped lobes (9 tails rendered, the inner
#  pairs overlapping their neighbours), each lobe a fat teardrop that is at least
#  as WIDE as it is tall near the tip. The fan is GREYER than the snow-white
#  face so the face pops forward; coral eye-spot tips ride the fan edge in a
#  matched rhythm — the peacock pattern, not a frost-spike mass.
# ─────────────────────────────────────────────────────────────────────────────

def _bushy_tail(s, P, hip_x, hip_y, ang, length, half_w_base, half_w_belly,
                belly_at, body, dark, sheen):
    """One fat teardrop tail lobe along `ang`. half_w_belly >= length*belly is
    what makes it BUSHY (wide near the tip), not a pin-thin triangle.
    Returns the tip + perpendicular so the caller can seat a coral eye-spot."""
    ca, sa = math.cos(ang), math.sin(ang)
    px_, py_ = -sa, ca   # perpendicular (fan width axis)

    def along(t, w):
        ax = hip_x + ca * length * t
        ay = hip_y + sa * length * t
        return (ax + px_ * w, ay + py_ * w)

    tipx = hip_x + ca * length
    tipy = hip_y + sa * length
    # rounded fat teardrop: narrow root -> wide belly (the bush) -> soft point
    left = [
        along(0.04, half_w_base * 0.55),
        along(0.22, half_w_base),
        along(belly_at - 0.10, half_w_belly * 0.96),
        along(belly_at, half_w_belly),
        along(belly_at + 0.14, half_w_belly * 0.88),
        along(0.92, half_w_belly * 0.40),
    ]
    right = [
        along(0.92, -half_w_belly * 0.40),
        along(belly_at + 0.14, -half_w_belly * 0.88),
        along(belly_at, -half_w_belly),
        along(belly_at - 0.10, -half_w_belly * 0.96),
        along(0.22, -half_w_base),
        along(0.04, -half_w_base * 0.55),
    ]
    poly = left + [(tipx, tipy)] + right
    # dark-core bed offset down-right (the receded shade under the bush)
    pygame.draw.polygon(s, dark, P([(x + 3, y + 3) for (x, y) in poly]))
    pygame.draw.polygon(s, body, P(poly))
    # top-left rim-sheen sliver along the leading edge of the lobe
    pygame.draw.polygon(s, sheen, P([
        along(0.20, half_w_base),
        along(belly_at, half_w_belly),
        along(belly_at, half_w_belly - 6),
        along(0.20, half_w_base - 4),
    ]))
    return (tipx, tipy), (px_, py_), (ca, sa)


def _coral_eyespot(s, P, tipx, tipy, ca, sa, px_, py_, length, hip_x, hip_y):
    """A matched coral teardrop riding the tip of a tail lobe — the peacock
    eye-spot. Same size on every lobe so the fan edge reads as a deliberate
    coral-tip rhythm."""
    # spot centred a little back from the very point so it reads as a cap
    cxs = hip_x + ca * length * 0.84
    cys = hip_y + sa * length * 0.84
    w = 12
    spot = [
        (cxs + px_ * w, cys + py_ * w),
        (cxs + ca * length * 0.0 + (tipx - cxs) * 0.85,
         cys + (tipy - cys) * 0.85),
        (tipx, tipy),
        (cxs + (tipx - cxs) * 0.85 - px_ * 0.0,
         cys + (tipy - cys) * 0.85),
        (cxs - px_ * w, cys - py_ * w),
    ]
    # simpler robust teardrop: belly ring + point
    spot = [
        (cxs + px_ * w, cys + py_ * w),
        (cxs + (tipx - cxs) * 0.5 + px_ * w * 0.6,
         cys + (tipy - cys) * 0.5 + py_ * w * 0.6),
        (tipx, tipy),
        (cxs + (tipx - cxs) * 0.5 - px_ * w * 0.6,
         cys + (tipy - cys) * 0.5 - py_ * w * 0.6),
        (cxs - px_ * w, cys - py_ * w),
    ]
    pygame.draw.polygon(s, CORAL_SH, P([(x + 2, y + 2) for (x, y) in spot]))
    pygame.draw.polygon(s, CORAL, P(spot))
    # bright top-left glint on the eye-spot
    pygame.draw.polygon(s, CORAL_HI, P([
        (cxs + px_ * w, cys + py_ * w),
        (cxs + (tipx - cxs) * 0.45 + px_ * w * 0.55,
         cys + (tipy - cys) * 0.45 + py_ * w * 0.55),
        (cxs + (tipx - cxs) * 0.45 + px_ * w * 0.15,
         cys + (tipy - cys) * 0.45 + py_ * w * 0.15),
        (cxs + px_ * w * 0.3, cys + py_ * w * 0.3),
    ]))


def draw_fan(s, P, hip_x, hip_y):
    """Nine bushy tails drawn back-to-front so the EYE reads ~5 broad lobes:
    outer pair, then mid pair, then inner pair tucked behind, then the three
    crown lobes on top. Wide spread + fat bellies = the peacock fan icon."""
    # tails ordered so overlapping ones layer outer->inner->crown
    # (deg measured from straight up = -90; symmetric spread ~196 deg, WIDE)
    spread = 196.0
    base_deg = -90
    n = 9

    # geometry tuned so the fan is WIDER than the body is tall and BUSHY:
    # belly half-width ~ 0.34 * length => each lobe is wider than tall near tip.
    def lobe_geom(frac):
        edge = abs(frac - 0.5) * 2.0          # 0 at centre, 1 at the rim
        # crown (centre) tails tallest, outer rim a touch shorter -> rounded arc
        length = 150 * (1.0 - 0.16 * edge)
        half_belly = length * 0.34
        half_base = 13
        belly_at = 0.60
        return length, half_base, half_belly, belly_at

    # draw order: rim -> mid -> crown so inner lobes overlap and group visually
    order = [0, 8, 1, 7, 2, 6, 3, 5, 4]
    tips = {}
    for i in order:
        frac = i / (n - 1)
        ang = math.radians(base_deg - spread / 2 + spread * frac)
        length, hb, hbel, bat = lobe_geom(frac)
        tip, (px_, py_), (ca, sa) = _bushy_tail(
            s, P, hip_x, hip_y, ang, length, hb, hbel, bat,
            TAIL, TAIL_SH, TAIL_HI)
        tips[i] = (tip, (px_, py_), (ca, sa), length)

    # coral eye-spots drawn AFTER all lobes so every tip rhythm sits on top
    for i in range(n):
        (tip, (px_, py_), (ca, sa), length) = tips[i]
        _coral_eyespot(s, P, tip[0], tip[1], ca, sa, px_, py_, length,
                       hip_x, hip_y)


# ─────────────────────────────────────────────────────────────────────────────
#  THE CREATURE — built large (supersampled), then outlined + downscaled.
#  Wide read: the GREYER bushy nine-tail FAN dominates; the snow-white fox face
#  sits in front of it.
# ─────────────────────────────────────────────────────────────────────────────

def build_kitsune(target_h=200):
    U = SS
    W, H = 340 * U, 250 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2
    # nudge the whole creature down so the high tail-fan crowns behind the head
    YOFF = 16

    def P(pts):
        return [(cx + int(x * U), int((y + YOFF) * U)) for (x, y) in pts]

    # ---- THE NINE-TAIL FAN (drawn FIRST, behind everything) --------------
    # Anchored at a LOW hip so the fan rises BEHIND and ABOVE the head, the
    # dominant wide bushy mass. Greyer than the face so the face pops forward.
    draw_fan(s, P, hip_x=0, hip_y=128)

    # ---- SHRINE-PRIESTESS HAORI BODY (slim + COMPACT, in front of fan) ----
    # Shortened ~15% per critique so the fan clearly dominates; weight-shifted
    # chibi body; white haori with vermilion + gold trim (the warm chest focal).
    body = P([
        (-24, 132), (-28, 152), (-22, 176), (-25, 188),
        (-7, 192), (0, 193), (7, 192), (25, 188),
        (22, 176), (28, 152), (24, 132),
    ])
    pygame.draw.polygon(s, HAORI_SH, [(x + 2 * U, y + 2 * U) for (x, y) in body])
    pygame.draw.polygon(s, FUR, body)
    # top-left rim-sheen on the left lapel
    pygame.draw.polygon(s, SHEEN, P([
        (-24, 134), (-27, 152), (-23, 176), (-17, 174),
        (-20, 152), (-18, 136),
    ]))
    # left-over-right haori crossover front (vermilion panel) — warm focal
    pygame.draw.polygon(s, VERM_SH, P([
        (-3, 136), (16, 144), (10, 184), (-3, 188),
    ]))
    pygame.draw.polygon(s, VERMILION, P([
        (-3, 136), (13, 143), (8, 181), (-3, 185),
    ]))
    pygame.draw.polygon(s, VERM_HI, P([
        (-3, 138), (8, 142), (4, 158), (-3, 158),
    ]))
    # gold sash / obi band at the waist (haori-trim)
    obi = P([(-26, 158), (26, 158), (24, 170), (-24, 170)])
    pygame.draw.polygon(s, GOLD, obi)
    pygame.draw.polygon(s, GOLD_HI, P([(-26, 158), (26, 158), (26, 162), (-26, 162)]))
    # gold collar trim down the crossover
    pygame.draw.line(s, GOLD, P([(-3, 136)])[0], P([(16, 144)])[0], int(2.5 * U))
    # little sleeve-paws (white fur) peeking from the sides
    for sx in (-1, 1):
        paw = P([
            (sx * 24, 160), (sx * 32, 166), (sx * 30, 180),
            (sx * 22, 178), (sx * 20, 168),
        ])
        pygame.draw.polygon(s, HAORI_SH, [(x + 2 * U, y + 2 * U) for (x, y) in paw])
        pygame.draw.polygon(s, FUR, paw)
        pygame.draw.polygon(s, CORAL, P([
            (sx * 32, 166), (sx * 30, 180), (sx * 25, 176), (sx * 28, 168),
        ]))

    # ---- THE FOX HEAD (big chibi head over the body) — SNOW-WHITE focal ---
    # Tall pointed EARS first (behind the cranium top), coral inner.
    for sx in (-1, 1):
        ear = P([
            (sx * 12, 56), (sx * 26, 4), (sx * 41, 40), (sx * 28, 56),
        ])
        pygame.draw.polygon(s, FUR_SH, [(x + 2 * U, y + 2 * U) for (x, y) in ear])
        pygame.draw.polygon(s, FUR, ear)
        # coral inner ear
        pygame.draw.polygon(s, CORAL_SH, P([
            (sx * 18, 50), (sx * 26, 16), (sx * 34, 42),
        ]))
        pygame.draw.polygon(s, CORAL, P([
            (sx * 19, 48), (sx * 26, 20), (sx * 32, 41),
        ]))
        if sx == -1:
            pygame.draw.polygon(s, SHEEN, P([
                (sx * 12, 54), (sx * 26, 6), (sx * 20, 30),
            ]))

    # Cranium / cheeks — a rounded fox head, pure snow-white so it separates
    # from the greyer fan behind it.
    head = P([
        (-31, 56), (-35, 36), (-27, 20), (-10, 11), (0, 10),
        (10, 11), (27, 20), (35, 36), (31, 56), (23, 76),
        (10, 90), (0, 94), (-10, 90), (-23, 76),
    ])
    pygame.draw.polygon(s, FUR_SH, [(x + 2 * U, y + 3 * U) for (x, y) in head])
    pygame.draw.polygon(s, FUR, head)
    # top-left rim-sheen on the cranium
    pygame.draw.polygon(s, SHEEN, P([
        (-31, 54), (-34, 36), (-26, 21), (-12, 12), (-14, 24),
        (-25, 32), (-28, 50),
    ]))
    # cool-grey cheek dark-core hollows
    for sx in (-1, 1):
        pygame.draw.polygon(s, FUR_SH, P([
            (sx * 29, 56), (sx * 31, 66), (sx * 21, 78), (sx * 19, 64),
        ]))

    # SHARP SNOUT pointing down-forward (the sharp-snout read).
    snout = P([
        (-12, 70), (12, 70), (8, 92), (0, 100), (-8, 92),
    ])
    pygame.draw.polygon(s, FUR, snout)
    pygame.draw.polygon(s, FUR_SH, P([
        (-8, 92), (0, 100), (8, 92), (4, 96), (0, 98), (-4, 96),
    ]))
    # dark nose tip
    pygame.draw.polygon(s, NOSE, P([
        (-5, 92), (5, 92), (3, 99), (0, 102), (-3, 99),
    ]))
    pygame.draw.circle(s, SHEEN, P([(-2, 93)])[0], int(1.4 * U))

    # eyes — sly upturned almond eyes (trickster squint).
    for sx in (-1, 1):
        eye = P([
            (sx * 8, 56), (sx * 22, 52), (sx * 24, 60), (sx * 12, 64),
        ])
        pygame.draw.polygon(s, INK, eye)
        # coral upper-lid liner (sly)
        pygame.draw.line(s, CORAL, P([(sx * 8, 55)])[0], P([(sx * 22, 51)])[0], int(2 * U))
        # gold-flecked iris glint
        pygame.draw.circle(s, GOLD, P([(sx * 16, 58)])[0], int(2.6 * U))
        pygame.draw.circle(s, SHEEN, P([(sx * 14, 56)])[0], int(1.2 * U))
    # coral cheek facial markings (kitsune tells)
    for sx in (-1, 1):
        pygame.draw.polygon(s, CORAL, P([
            (sx * 16, 68), (sx * 28, 64), (sx * 27, 70), (sx * 17, 73),
        ]))
    # forehead coral flame-mark (brow-blaze the AD asked to keep)
    pygame.draw.polygon(s, CORAL, P([
        (0, 24), (5, 36), (0, 32), (-5, 36),
    ]))

    # ---- THE FOXFIRE ORB hovering by the (viewer-right) ear --------------
    # Drop-shadowed against the fur so the lone mint accent survives shrink.
    _foxfire(s, cx + int(50 * U), int((26 + YOFF) * U), int(11 * U), shadow_on=True)

    # ---- ink keyline grown from the alpha mask + downscale ---------------
    outlined, _ = grow_outline(s, INK, grow=1)
    return smoothdown(outlined, target_h)


# ─────────────────────────────────────────────────────────────────────────────
#  THE PROP -> PILLAR — torii-GATE arch / shrine-pillar.  (unchanged — the AD
#  signed this off as done; only re-rendered for the comparison sheet.)
# ─────────────────────────────────────────────────────────────────────────────

def _shide(surf, x, y, P, w=5, h=14, n=4):
    """A zig-zag folded paper-charm (shide) hanging — cream lightning-fold."""
    for i in range(n):
        yy = y + i * h
        step = w if i % 2 == 0 else -w
        pygame.draw.polygon(surf, (236, 230, 222), P([
            (x, yy), (x + step, yy), (x + step, yy + h), (x, yy + h),
        ]))
        pygame.draw.polygon(surf, (200, 192, 182), P([
            (x + step, yy + h - 2), (x, yy + h - 2), (x, yy + h), (x + step, yy + h),
        ]))


def build_torii(target_h=210, as_pillar=False):
    """Render the torii prop. When `as_pillar`, mirror it into a clean
    repeatable shrine-PILLAR: the vermilion post repeats as the body, the
    lintel + shide-garland + fox-mask plaque is the detachable gap-edge cap."""
    U = SS
    W, H = 88 * U, 230 * U
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    cx = W // 2

    def P(pts):
        return [(cx + int(x * U), int(y * U)) for (x, y) in pts]

    post_w = 11
    if as_pillar:
        cap_y = 12
        shaft_top = 40
        shaft_bot = 224
    else:
        cap_y = 28
        shaft_top = 56
        shaft_bot = 222

    # ---- vermilion POST body (repeatable shaft) --------------------------
    post = P([(-post_w, shaft_top), (post_w, shaft_top),
              (int(post_w * 0.82), shaft_bot), (-int(post_w * 0.82), shaft_bot)])
    pygame.draw.polygon(s, VERM_SH, [(x + 2 * U, y) for (x, y) in post])
    pygame.draw.polygon(s, VERMILION, post)
    pygame.draw.polygon(s, VERM_HI, P([
        (-post_w, shaft_top), (-post_w + 3, shaft_top),
        (-int(post_w * 0.82) + 3, shaft_bot), (-int(post_w * 0.82), shaft_bot),
    ]))
    band_start = shaft_top + 14
    for by in range(band_start, shaft_bot - 8, 26):
        pygame.draw.rect(s, INK,
                         (cx - post_w * U, by * U, post_w * 2 * U, int(4 * U)))
        pygame.draw.rect(s, GOLD,
                         (cx - post_w * U, (by + 5) * U, post_w * 2 * U, int(1.5 * U)))

    # ---- LINTEL beams (kasagi top beam + nuki tie-beam) = gap-edge cap ----
    kasagi = P([
        (-40, cap_y - 9), (40, cap_y - 9), (44, cap_y - 14),
        (40, cap_y - 16), (-40, cap_y - 16), (-44, cap_y - 14),
    ])
    pygame.draw.polygon(s, VERM_SH, [(x + 2 * U, y + 2 * U) for (x, y) in kasagi])
    pygame.draw.polygon(s, VERMILION, kasagi)
    pygame.draw.polygon(s, VERM_HI, P([
        (-40, cap_y - 15), (40, cap_y - 15), (40, cap_y - 13), (-40, cap_y - 13),
    ]))
    nuki = P([(-34, cap_y), (34, cap_y), (34, cap_y + 8), (-34, cap_y + 8)])
    pygame.draw.polygon(s, VERM_SH, [(x + 2 * U, y + 2 * U) for (x, y) in nuki])
    pygame.draw.polygon(s, VERMILION, nuki)
    pygame.draw.polygon(s, VERM_HI, P([
        (-34, cap_y + 1), (34, cap_y + 1), (34, cap_y + 3), (-34, cap_y + 3),
    ]))
    pygame.draw.polygon(s, VERMILION, P([
        (-4, cap_y - 9), (4, cap_y - 9), (4, cap_y), (-4, cap_y),
    ]))
    for ex in (-42, 42):
        pygame.draw.rect(s, GOLD, P([(ex - 2, cap_y - 16)])[0]
                         + (int(4 * U), int(7 * U)))

    # ---- fox-mask PLAQUE hung on the centre strut (the cap focal) --------
    mask_cy = cap_y + 18
    pygame.draw.polygon(s, FUR_SH, P([(x + 1, y + 2) for (x, y) in [
        (-9, mask_cy - 8), (9, mask_cy - 8), (11, mask_cy + 2),
        (0, mask_cy + 14), (-11, mask_cy + 2)]]))
    pygame.draw.polygon(s, FUR, P([
        (-9, mask_cy - 8), (9, mask_cy - 8), (11, mask_cy + 2),
        (0, mask_cy + 14), (-11, mask_cy + 2)]))
    for sx in (-1, 1):
        pygame.draw.polygon(s, FUR, P([
            (sx * 5, mask_cy - 8), (sx * 11, mask_cy - 18), (sx * 11, mask_cy - 6)]))
        pygame.draw.polygon(s, CORAL, P([
            (sx * 7, mask_cy - 9), (sx * 10, mask_cy - 16), (sx * 10, mask_cy - 8)]))
    pygame.draw.polygon(s, SHEEN, P([
        (-9, mask_cy - 7), (-2, mask_cy - 8), (-5, mask_cy - 1)]))
    for sx in (-1, 1):
        pygame.draw.line(s, CORAL, P([(sx * 3, mask_cy - 3)])[0],
                         P([(sx * 8, mask_cy - 1)])[0], int(2 * U))
        pygame.draw.circle(s, INK, P([(sx * 5, mask_cy + 2)])[0], int(1.6 * U))
    pygame.draw.polygon(s, CORAL, P([
        (0, mask_cy + 3), (3, mask_cy + 9), (0, mask_cy + 7), (-3, mask_cy + 9)]))

    # ---- shide paper-charm garland hung from the nuki tie-beam -----------
    for hx in (-26, -13, 13, 26):
        _shide(s, hx, cap_y + 8, P, w=4, h=7, n=3)
    pygame.draw.line(s, GOLD, P([(-30, cap_y + 8)])[0], P([(30, cap_y + 8)])[0], int(2 * U))

    if as_pillar:
        _foxfire(s, cx + int(30 * U), int((shaft_bot - 6) * U), int(7 * U))
    else:
        for sx in (-1, 1):
            base = P([(sx * post_w - 3, shaft_bot - 2), (sx * post_w + 6, shaft_bot - 2),
                      (sx * post_w + 8, shaft_bot + 6), (sx * post_w - 5, shaft_bot + 6)])
            pygame.draw.polygon(s, FUR_SH, base)
            pygame.draw.polygon(s, lerp(FUR_SH, FUR, 0.4), P([
                (sx * post_w - 3, shaft_bot - 2), (sx * post_w + 6, shaft_bot - 2),
                (sx * post_w + 6, shaft_bot), (sx * post_w - 3, shaft_bot)]))

    outlined, _ = grow_outline(s, INK, grow=1)
    return smoothdown(outlined, target_h)


# ─────────────────────────────────────────────────────────────────────────────
#  SHEET COMPOSITION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    SHEET_W, SHEET_H = 860, 620
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    for y in range(SHEET_H):
        t = y / SHEET_H
        sheet.fill(lerp((44, 46, 58), (26, 28, 38), t), (0, y, SHEET_W, 1))

    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    small = pygame.font.SysFont("dejavusans", 13)
    tiny = pygame.font.SysFont("dejavusans", 11)

    def label(txt, x, y, f=small, col=(238, 234, 230)):
        sheet.blit(f.render(txt, True, (0, 0, 0)), (x + 1, y + 1))
        sheet.blit(f.render(txt, True, col), (x, y))

    label("KITSUNE — nine-tailed fox-spirit shrine devil  [COOL GLOW: MINT-GREEN FOXFIRE]  ·  round 2",
          16, 12, font)
    label("R2: fan rebuilt WIDE + BUSHY (peacock arc, reads ~5 lobes) · tails pushed GREYER so the snow-white face pops forward · coral eye-spot rhythm · compact body",
          16, 36, tiny, (188, 214, 200))

    # large creature
    big = build_kitsune(target_h=320)
    bx = 24
    by = 64
    sheet.blit(big, (bx, by))
    label("creature (large)", bx + big.get_width() // 2 - 42, by + big.get_height() + 2)

    # 32px creature read (3x nearest zoom + actual 32px) + a 2nd silhouette test
    small_creat = build_kitsune(target_h=32)
    sy = by + big.get_height() + 24
    zoom = pygame.transform.scale(small_creat,
                                  (small_creat.get_width() * 4,
                                   small_creat.get_height() * 4))
    zx = bx + 8
    sheet.blit(zoom, (zx, sy))
    sheet.blit(small_creat, (zx + zoom.get_width() + 18,
                             sy + zoom.get_height() - small_creat.get_height()))
    label("32px read (4x + actual): wide fan + small face dot", zx, sy + zoom.get_height() + 4, tiny)

    # large torii prop
    torii = build_torii(target_h=360, as_pillar=False)
    stx = 440
    sty = 60
    sheet.blit(torii, (stx, sty))
    label("torii-gate (prop)", stx + torii.get_width() // 2 - 36,
          sty + torii.get_height() + 2, tiny)

    # mirrored pillar
    pill = build_torii(target_h=360, as_pillar=True)
    px = 560
    sheet.blit(pill, (px, sty))
    label("-> PILLAR mirror", px - 2, sty + pill.get_height() + 2, tiny)
    label("(repeatable post +", px - 2, sty + pill.get_height() + 16, tiny,
          (196, 200, 170))
    label(" lintel+shide+mask cap)", px - 2, sty + pill.get_height() + 28, tiny,
          (196, 200, 170))

    # 32px prop / pillar reads
    torii32 = build_torii(target_h=32, as_pillar=False)
    pill32 = build_torii(target_h=32, as_pillar=True)
    z2 = pygame.transform.scale(torii32,
                                (torii32.get_width() * 3, torii32.get_height() * 3))
    z3 = pygame.transform.scale(pill32,
                                (pill32.get_width() * 3, pill32.get_height() * 3))
    zy = 64
    zx2 = 690
    sheet.blit(z2, (zx2, zy))
    sheet.blit(z3, (zx2 + z2.get_width() + 20, zy))
    sheet.blit(torii32, (zx2 + 6, zy + z2.get_height() + 8))
    sheet.blit(pill32, (zx2 + z2.get_width() + 26, zy + z2.get_height() + 8))
    label("32px torii / pillar", zx2, zy + z2.get_height() + 34, tiny)

    # palette swatch strip
    swatches = [
        ("face fur", FUR), ("tail fan", TAIL), ("tail-core", TAIL_SH),
        ("coral", CORAL), ("vermilion", VERMILION), ("mint-foxfire", MINT),
        ("gold", GOLD), ("ink", INK), ("sheen", SHEEN),
    ]
    swx, swy = 690, 318
    for i, (nm, col) in enumerate(swatches):
        ry = swy + i * 21
        pygame.draw.rect(sheet, col, (swx, ry, 26, 16))
        pygame.draw.rect(sheet, (10, 10, 14), (swx, ry, 26, 16), 1)
        label(nm, swx + 32, ry + 2, tiny)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_2.png")
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
