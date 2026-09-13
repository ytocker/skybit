"""
Five candidate ACHIEVEMENTS star emblems for the main-menu "AWARDS" tile.

Each star is the sibling of ``hud._draw_trophy`` on the TOP 10 tile, so it must
read at the same tiny scale (~18-20 px tall) yet stay razor-sharp. The whole
family is drawn SUPERSAMPLED — composited on a surface ``_SS``× the target box
with clean geometry, then ``smoothscale``d down — because raw polygon draws at
tile scale alias into jaggy edges. Same discipline the badge family uses.

Palette is locked to the menu's gold-on-navy family so the emblem sits with the
trophy as one set. Lighting is one fixed upper-left source across all five.
"""
import math
import pygame

_SS = 4  # supersample factor: draw big, smoothscale down for crisp rims

# Menu gold family (mirrors hud + trophy).
_GOLD        = (240, 192,  64)   # body gold  (_GOLD_BRIGHT)
_GOLD_HI     = (255, 230, 150)   # pale sheen / lit crest
_GOLD_HOT    = (255, 248, 222)   # specular hot-spot
_GOLD_LO     = (188, 138,  28)   # shadowed gold
_RIM         = (140,  90,   8)   # dark keyline rim
_RIM_DEEP    = (110,  72,   8)   # deepest recess


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _star_pts(cx, cy, R, r, n=5, rot_deg=-90):
    """2n vertices alternating outer radius R / inner radius r, first at `rot`."""
    pts = []
    for i in range(n * 2):
        ang = math.radians(rot_deg + i * 180.0 / n)
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    return pts


def _chaikin(pts, iters):
    """Corner-cutting subdivision — rounds a polygon while keeping silhouette."""
    for _ in range(iters):
        out = []
        n = len(pts)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        pts = out
    return pts


def _grad_star(box, poly, top_col, bot_col):
    """A vertical top→bottom gradient clipped to `poly` on a box×box surface."""
    grad = pygame.Surface((box, box), pygame.SRCALPHA)
    ys = [p[1] for p in poly]
    y0, y1 = min(ys), max(ys)
    span = max(1.0, y1 - y0)
    for yy in range(box):
        t = min(1.0, max(0.0, (yy - y0) / span))
        pygame.draw.line(grad, (*_lerp(top_col, bot_col, t), 255),
                         (0, yy), (box, yy))
    mask = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return grad


def _blit_ss(surf, ss, box, cx, cy):
    small = pygame.transform.smoothscale(ss, (box, box))
    surf.blit(small, (int(round(cx - box / 2)), int(round(cy - box / 2))))


# ── 1. Classic sharp 5-point ────────────────────────────────────────────────
# Clean iconic gold star: dark keyline rim, soft top-lit body gradient, one
# crisp upper-left specular streak. The plain, unmistakable "star". A few
# degrees off dead-vertical so it carries a hand-placed award feel rather than
# a stock app-store "rate us" glyph.
def draw_classic(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = B / 2
    Rs, rs = R * _SS, R * _SS * 0.42
    rot = -87.0  # nudged off vertical so it doesn't read as a stock rating star
    k = (Rs + 2.6 * _SS) / Rs  # thicker dark rim for more mass on the day sky
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    pygame.draw.polygon(ss, _RIM, _star_pts(c, c, Rs * k, rs * k, rot_deg=rot))
    body = _star_pts(c, c, Rs, rs, rot_deg=rot)
    pygame.draw.polygon(ss, _GOLD, body)
    ss.blit(_grad_star(B, body, _GOLD_HI, _GOLD_LO), (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)
    # Upper-left specular streak: the top point's left edge catches the light.
    top = body[0]
    left_inner = body[-1]
    mid = ((top[0] + left_inner[0]) / 2, (top[1] + left_inner[1]) / 2)
    pygame.draw.line(ss, _GOLD_HOT, top, mid, int(1.6 * _SS))
    pygame.draw.line(ss, _GOLD_HI, top, left_inner, int(1.0 * _SS))
    _blit_ss(surf, ss, box, cx, cy)


# ── 2. Struck-metal beveled ─────────────────────────────────────────────────
# An embossed medal star: each arm is split by a central ridge into a lit and a
# shadowed facet, shaded by the shared upper-left light — reads as raised metal.
def draw_beveled(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = (B / 2, B / 2)
    Rs, rs = R * _SS, R * _SS * 0.46
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    # Dark rim first (scaled-up star behind the facets).
    k = (Rs + 2.2 * _SS) / Rs
    pygame.draw.polygon(ss, _RIM, _star_pts(c[0], c[1], Rs * k, rs * k))

    light = (-0.55, -0.83)  # upper-left (screen y down → up is negative)
    outer = [(c[0] + Rs * math.cos(math.radians(-90 + 72 * i)),
              c[1] + Rs * math.sin(math.radians(-90 + 72 * i))) for i in range(5)]
    inner = [(c[0] + rs * math.cos(math.radians(-54 + 72 * i)),
              c[1] + rs * math.sin(math.radians(-54 + 72 * i))) for i in range(5)]
    # Each arm splits into two facets; push the lit/shadow contrast hard and
    # gamma-bias it toward the extremes so the emboss survives the downscale
    # and never muddies into the flat #1 star.
    for i in range(5):
        o = outer[i]
        il, ir = inner[(i - 1) % 5], inner[i]
        for tri in ((c, il, o), (c, o, ir)):
            mx = (tri[1][0] + tri[2][0]) / 2 - c[0]
            my = (tri[1][1] + tri[2][1]) / 2 - c[1]
            n = math.hypot(mx, my) or 1.0
            d = (mx / n) * light[0] + (my / n) * light[1]
            t = (d + 1) / 2
            t = t * t * (3 - 2 * t)          # smoothstep → snap to lit/shadow
            lit_hi = _lerp(_GOLD, _GOLD_HI, 1.0)
            pygame.draw.polygon(ss, _lerp(_RIM, lit_hi, t), tri)
    # Ridge keylines from centre to each tip sharpen the emboss.
    for o in outer:
        pygame.draw.line(ss, _RIM_DEEP, c, o, max(1, int(0.7 * _SS)))
    # A small, flush lit facet at the very centre — not a raised boss, so it
    # never punches through as a hole. One subtle sheen dot, upper-left only.
    pygame.draw.circle(ss, _GOLD_HI,
                       (int(c[0] - rs * 0.14), int(c[1] - rs * 0.14)),
                       int(rs * 0.12))
    _blit_ss(surf, ss, box, cx, cy)


# ── 3. Rounded / soft 5-point ───────────────────────────────────────────────
# A friendlier, chunkier star: Chaikin-rounded points, fatter arms, a soft
# top-lit body and a broad upper sheen. The "gummy" award star.
def draw_rounded(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = B / 2
    Rs, rs = R * _SS, R * _SS * 0.60  # fatter inner radius → chunkier arm mass
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    base = _star_pts(c, c, Rs, rs)
    body = _chaikin(base, 3)
    rim = _chaikin(_star_pts(c, c, Rs + 2.4 * _SS, rs + 2.4 * _SS), 3)
    pygame.draw.polygon(ss, _RIM, rim)
    pygame.draw.polygon(ss, _GOLD, body)
    ss.blit(_grad_star(B, body, _GOLD_HI, _GOLD_LO), (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)
    # Soft sheen: a pale rounded blob pulled toward centre so it lifts the body
    # without flattening the top-left lobe to white at tile size.
    sheen = pygame.Surface((B, B), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (*_GOLD_HOT, 120),
                        (c - Rs * 0.42, c - Rs * 0.52, Rs * 0.62, Rs * 0.54))
    mask = pygame.Surface((B, B), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), body)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(sheen, (0, 0))
    _blit_ss(surf, ss, box, cx, cy)


# ── 4. Sparkle / four-glint star ────────────────────────────────────────────
# A star, shining. A solid bright 4-point star body carries a dark keyline for
# weight; the four thin diagonal glints ride ON it as a sparkle accent, not as
# the whole mark — so it reads as a proper award star that happens to twinkle.
def draw_sparkle(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = B / 2
    Rs = R * _SS
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    # Solid 4-point body: a fat inner radius gives real star mass (no asterisk).
    ir = Rs * 0.40
    body = _star_pts(c, c, Rs, ir, n=4, rot_deg=-90)
    rim_k = (Rs + 2.4 * _SS) / Rs  # thick dark keyline for trophy-weight mass
    pygame.draw.polygon(ss, _RIM,
                        _star_pts(c, c, Rs * rim_k, ir * rim_k,
                                  n=4, rot_deg=-90))
    pygame.draw.polygon(ss, _GOLD, body)
    ss.blit(_grad_star(B, body, _GOLD_HI, _GOLD_LO), (0, 0),
            special_flags=pygame.BLEND_RGBA_MULT)

    # Diagonal sparkle glints ride on the body as short accent rays.
    for i in range(4):
        ang = math.radians(-45 + 90 * i)
        gl = Rs * 0.42
        p = (c + gl * math.cos(ang), c + gl * math.sin(ang))
        pygame.draw.line(ss, (*_GOLD_HI, 220), (c, c), p, max(1, int(0.8 * _SS)))

    # Bright core hotspot sells the shine, offset upper-left with the light.
    pygame.draw.circle(ss, _GOLD_HI, (int(c), int(c)), int(Rs * 0.20))
    pygame.draw.circle(ss, _GOLD_HOT,
                       (int(c - Rs * 0.06), int(c - Rs * 0.06)), int(Rs * 0.10))
    _blit_ss(surf, ss, box, cx, cy)


# ── 5. Star medallion ───────────────────────────────────────────────────────
# A star mounted on a small backing disc: the star is the hero — its own full
# dark keyline pops it off a deliberately darker, smaller coin so it never
# collides with the game's literal gold $ coins. The most "official" of the set.
def draw_medallion(surf, cx, cy, R=10):
    box = int(R * 2 + 8)
    B = box * _SS
    c = B / 2
    Rs = R * _SS
    ss = pygame.Surface((B, B), pygame.SRCALPHA)

    # Backing disc: smaller than the emblem box and one step darker than a coin
    # so it reads as a mount, not a collectible. Dark rim ring + top-lit body.
    dr = Rs * 0.86
    pygame.draw.circle(ss, _RIM_DEEP, (int(c), int(c)), int(dr + 1.4 * _SS))
    disc = pygame.Surface((B, B), pygame.SRCALPHA)
    for yy in range(B):
        t = min(1.0, max(0.0, (yy - (c - dr)) / (2 * dr)))
        pygame.draw.line(disc, (*_lerp(_GOLD, _GOLD_LO, t), 255),
                         (0, yy), (B, yy))
    dmask = pygame.Surface((B, B), pygame.SRCALPHA)
    pygame.draw.circle(dmask, (255, 255, 255, 255), (int(c), int(c)), int(dr))
    disc.blit(dmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ss.blit(disc, (0, 0))
    # Beaded inner keyline of the mount.
    pygame.draw.circle(ss, _RIM, (int(c), int(c)), int(dr), max(1, int(0.7 * _SS)))

    # Struck star — its OWN full dark keyline first, then beveled two-tone arms.
    sR = Rs * 0.66
    srr = sR * 0.46
    light = (-0.55, -0.83)
    kk = (sR + 1.8 * _SS) / sR
    pygame.draw.polygon(ss, _RIM, _star_pts(c, c, sR * kk, srr * kk))
    outer = [(c + sR * math.cos(math.radians(-90 + 72 * i)),
              c + sR * math.sin(math.radians(-90 + 72 * i))) for i in range(5)]
    inner = [(c + srr * math.cos(math.radians(-54 + 72 * i)),
              c + srr * math.sin(math.radians(-54 + 72 * i))) for i in range(5)]
    cc = (c, c)
    for i in range(5):
        o = outer[i]
        il, ir = inner[(i - 1) % 5], inner[i]
        for tri in ((cc, il, o), (cc, o, ir)):
            mx = (tri[1][0] + tri[2][0]) / 2 - c
            my = (tri[1][1] + tri[2][1]) / 2 - c
            n = math.hypot(mx, my) or 1.0
            d = (mx / n) * light[0] + (my / n) * light[1]
            pygame.draw.polygon(ss, _lerp(_GOLD_LO, _GOLD_HOT, (d + 1) / 2), tri)
    for o in outer:
        pygame.draw.line(ss, _RIM, cc, o, max(1, int(0.5 * _SS)))
    pygame.draw.circle(ss, _GOLD_HI,
                       (int(c - srr * 0.16), int(c - srr * 0.16)), int(srr * 0.14))
    _blit_ss(surf, ss, box, cx, cy)


STARS = [
    ("Classic sharp",   draw_classic),
    ("Struck bevel",    draw_beveled),
    ("Rounded soft",    draw_rounded),
    ("Sparkle glint",   draw_sparkle),
    ("Star medallion",  draw_medallion),
]
