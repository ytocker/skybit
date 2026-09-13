"""Look-dev mockup: the Warren Route SIGN (ROUND 1).

The "Pagoda Warren" route is a scripted run hosted by the Plum & Lime jester.
Its FIRST pagoda hangs a small sign from the top-gap rim that announces N —
how many pillars long the route is (an integer 10..25). Today's in-game sign
(game/warren_demo.py::draw_sign) reads amateur: an ADDITIVE gold glow that
blows out to a white blob over the pale sky, a flat tan plaque with a thin
border, and a low-res SysFont number.

This sheet explores FIVE distinct, high-craft sign FORMS — not five tweaks of
one plaque — each hung from a slice of the pagoda gap-rim so we can judge how
it reads on a bright daytime sky. The number N=18 is the hero value (two
digits); a small inset on each cell shows the single-digit case (N=8) so both
widths can be judged.

Craft rules honoured on every version (per the brief):
  - NO additive halo / NO white blob over the sky. Depth comes from bevels,
    carved relief, inner + drop shadow, emboss and ornament. Any glow used is
    NORMAL-blended, colour-keyed and tight (e.g. a lantern's interior light).
  - Each sign is composited on a SS=4 supersampled SRCALPHA canvas and
    smooth-scaled down for crisp anti-aliasing.
  - The number N is stamped with the vendored bold TTF (hud._font), with a
    thick colour edge + a soft drop shadow — the _draw_celebration recipe.
  - Procedural only; nothing is wired into the live game this round.

Palette ties to the clown host (plum 96,44,150 / lime 132,218,116 /
gold 250,205,72 / red-nose 232,72,72): ~2 of 5 lean clown, the rest stay warm
wood / festival-gold / temple with subtle clown accents.

    PYTHONPATH=. python tools/render_warren_sign.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()

from game import hud

SS = 4                                   # supersample factor for every sign
SKY = (150, 205, 235)                    # the bright daytime sky behind the rim

# Clown host palette.
PLUM = (96, 44, 150)
LIME = (132, 218, 116)
GOLD = (250, 205, 72)
REDN = (232, 72, 72)

# Warm-wood / temple tones.
WOOD = (146, 96, 54)
WOOD_D = (96, 58, 30)
WOOD_L = (196, 142, 88)
BRASS = (214, 168, 78)
BRASS_L = (248, 224, 150)
BRASS_D = (150, 104, 40)
CREAM = (250, 242, 222)
INK = (44, 30, 22)


def _sh(c, d):
    """Shade a colour by a signed delta on every channel (clamped)."""
    return (max(0, min(255, c[0] + d)),
            max(0, min(255, c[1] + d)),
            max(0, min(255, c[2] + d)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


# ── number stamp (the _draw_celebration recipe at sign scale) ────────────────

def _stamp_number(surf, txt, center, size, *, face, edge, edge_px=3,
                  shadow=True, shadow_a=110):
    """Stamp N with the vendored bold TTF: a soft drop shadow, a thick colour
    EDGE built from an 8-direction offset stamp, then the bright face on top.
    `size`/`edge_px` are in supersampled px (the caller already multiplied by
    SS). Mirrors warren_demo._draw_celebration's number recipe."""
    nf = hud._font(int(size), True)
    cx, cy = center
    if shadow:
        sh = nf.render(txt, True, (0, 0, 0))
        sh.set_alpha(shadow_a)
        surf.blit(sh, sh.get_rect(center=(cx + edge_px, cy + int(edge_px * 1.4))))
    eimg = nf.render(txt, True, edge)
    o = edge_px
    for ox, oy in ((-o, 0), (o, 0), (0, -o), (0, o),
                   (-o, -o), (o, -o), (-o, o), (o, o)):
        surf.blit(eimg, eimg.get_rect(center=(cx + ox, cy + oy)))
    fimg = nf.render(txt, True, face)
    r = fimg.get_rect(center=(cx, cy))
    surf.blit(fimg, r)
    return r


def _vgrad_rrect(surf, rect, radius, top, bot):
    """A vertical-gradient rounded rectangle painted directly (supersample
    space). Used for plaque/banner/tag bodies so they read sculpted, not flat."""
    x, y, w, h = rect
    r = min(radius, w // 2, h // 2)
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(h):
        c = _mix(top, bot, i / max(1, h - 1))
        pygame.draw.line(body, c, (0, i), (w, i))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=r)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x, y))


def _grain(surf, rect, base, n=22):
    """Faint wood-grain striations down a panel (subtle alpha streaks following
    the plank length) so carved wood reads as grain, not flat fill."""
    x, y, w, h = rect
    rng = _Rng(rect[0] * 131 + rect[1])
    for _ in range(n):
        gy = y + int(rng.f() * h)
        wob = 2 * SS
        col = _sh(base, -18 if rng.f() > 0.5 else 14)
        pts = [(x + 2 * SS + i, gy + int(math.sin(i * 0.02 + gy) * wob))
               for i in range(0, w - 4 * SS, 6 * SS)]
        if len(pts) >= 2:
            pygame.draw.lines(surf, (*col, 60), False, pts, max(1, SS // 2))


class _Rng:
    """Tiny deterministic LCG so each cell's grain/jewels are stable run-to-run
    without seeding the global random module."""

    def __init__(self, seed):
        self.s = seed & 0xFFFFFFFF

    def f(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 0x7FFFFFFF


def _stud(surf, x, y, r, col=BRASS):
    """A round brass corner stud: dark seat ring, body, top-left specular."""
    pygame.draw.circle(surf, _sh(col, -70), (x, y), r + SS // 2)
    pygame.draw.circle(surf, col, (x, y), r)
    pygame.draw.circle(surf, _sh(col, 70), (x - r // 3, y - r // 3), max(1, r // 2))


def _rope(surf, p0, p1, w, col=(150, 116, 64)):
    """A twisted cord/rope from rim to sign with a 2-strand twill read."""
    pygame.draw.line(surf, _sh(col, -45), p0, p1, w + SS)
    pygame.draw.line(surf, col, p0, p1, w)
    # Two short highlight ticks to suggest the twist of the strands.
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy) or 1
    nx, ny = -dy / ln, dx / ln
    for t in [i / 9 for i in range(1, 9)]:
        mx = p0[0] + dx * t
        my = p0[1] + dy * t
        pygame.draw.line(surf, _sh(col, 55),
                         (mx - nx * w * 0.3, my - ny * w * 0.3),
                         (mx + nx * w * 0.3, my + ny * w * 0.3), max(1, SS // 2))


def _hook(surf, x, y, col=BRASS):
    """A small brass eye-hook / ring the cord loops over the rim through."""
    pygame.draw.circle(surf, _sh(col, -60), (x, y), 5 * SS, 2 * SS)
    pygame.draw.circle(surf, col, (x, y), 5 * SS, max(1, SS))


# ── version A: rope-hung carved-wood plaque (warm wood + gold trim) ──────────

def sign_carved_wood(N, w, h):
    """Premium rope-hung carved hardwood plaque: bevelled rim, wood grain, a
    sunken gilt panel with an INCISED (carved-in) gold number, brass corner
    studs, finished with a small plum-ribbon clown accent at the top."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    rim_y = 8 * SS
    pw, ph = int(w * 0.78), int(h * 0.50)
    bx, by = cx - pw // 2, int(h * 0.30)

    for rx in (bx + 12 * SS, bx + pw - 12 * SS):
        _rope(s, (rx, rim_y), (rx, by + 3 * SS), max(2, 3 * SS))
        _hook(s, rx, by + 4 * SS, col=BRASS)

    # Drop shadow cast onto the sky so the plaque floats off the rim.
    drop = pygame.Surface((pw + 8 * SS, ph + 8 * SS), pygame.SRCALPHA)
    pygame.draw.rect(drop, (0, 0, 0, 70), drop.get_rect(),
                     border_radius=10 * SS)
    s.blit(drop, (bx - 2 * SS, by + 5 * SS))

    # Bevelled wood body: dark base for the bevel, then a slightly inset lit
    # face with a top-light gradient — emboss, not a flat fill.
    pygame.draw.rect(s, WOOD_D, (bx, by, pw, ph), border_radius=10 * SS)
    _vgrad_rrect(s, (bx + 3 * SS, by + 3 * SS, pw - 6 * SS, ph - 6 * SS),
                 8 * SS, WOOD_L, _sh(WOOD, -14))
    _grain(s, (bx + 3 * SS, by + 3 * SS, pw - 6 * SS, ph - 6 * SS), WOOD)
    # Top-left lit bevel edge + bottom-right shade so the plank reads raised.
    pygame.draw.line(s, (*_sh(WOOD_L, 40), 150), (bx + 4 * SS, by + 5 * SS),
                     (bx + pw - 6 * SS, by + 5 * SS), SS)
    pygame.draw.line(s, (*WOOD_D, 180), (bx + 4 * SS, by + ph - 5 * SS),
                     (bx + pw - 6 * SS, by + ph - 5 * SS), SS)

    # Sunken gilt panel (carved-in): a dark routed groove ring framing a gold
    # field, so the number sits in a recessed cartouche.
    px = bx + 12 * SS
    py = by + 11 * SS
    pwid = pw - 24 * SS
    phgt = ph - 22 * SS
    pygame.draw.rect(s, _sh(WOOD_D, -18), (px - 2 * SS, py - 2 * SS,
                     pwid + 4 * SS, phgt + 4 * SS), border_radius=6 * SS)
    _vgrad_rrect(s, (px, py, pwid, phgt), 5 * SS, BRASS_L, BRASS_D)
    pygame.draw.rect(s, _sh(BRASS_D, -30), (px, py, pwid, phgt),
                     width=SS, border_radius=5 * SS)

    # Incised gilt number: a dark carved core with a thin lit lip so it reads
    # CHISELLED into the gold, not printed on it.
    _stamp_number(s, str(N), (cx, py + phgt // 2), 40 * SS,
                  face=_sh(BRASS_D, -40), edge=BRASS_L, edge_px=SS,
                  shadow=True, shadow_a=90)

    # Brass corner studs.
    for sx in (bx + 9 * SS, bx + pw - 9 * SS):
        for sy in (by + 9 * SS, by + ph - 9 * SS):
            _stud(s, sx, sy, 3 * SS)

    # Small plum clown ribbon knotted over the top rail (subtle host accent).
    _ribbon(s, cx, by + 2 * SS, PLUM, GOLD, span=10 * SS)
    return s


def _ribbon(surf, cx, y, col, trim, span):
    """A small bow/ribbon: two angled tails + a centre knot, trimmed in `trim`."""
    for sgn in (-1, 1):
        pts = [(cx, y), (cx + sgn * span, y - span // 2),
               (cx + sgn * span, y + span // 2)]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _sh(col, -50), pts, max(1, SS // 2))
    pygame.draw.circle(surf, trim, (cx, y), max(2, span // 4))
    pygame.draw.circle(surf, _sh(trim, 60),
                       (cx - span // 8, y - span // 8), max(1, span // 8))


# ── version B: hanging cloth banner / scroll (CLOWN plum+lime+gold) ──────────

def sign_cloth_banner(N, w, h):
    """A hanging cloth scroll in the clown's plum body with a lime+gold border,
    a curled top rod with finials, a weighted scalloped hem, side tassels and a
    soft fabric fold (a vertical light/shade band) — embroidered gold number."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    rim_y = 6 * SS
    bw, bh = int(w * 0.56), int(h * 0.60)
    bx, by = cx - bw // 2, int(h * 0.24)

    # Top rod with rounded finials + the two cords up to the rim.
    rod_y = by - 4 * SS
    for rx in (bx + 4 * SS, bx + bw - 4 * SS):
        _rope(s, (rx, rim_y), (rx, rod_y), max(2, 2 * SS),
              col=_sh(GOLD, -30))
    pygame.draw.line(s, _sh(GOLD, -60), (bx - 6 * SS, rod_y),
                     (bx + bw + 6 * SS, rod_y), 5 * SS)
    pygame.draw.line(s, GOLD, (bx - 6 * SS, rod_y),
                     (bx + bw + 6 * SS, rod_y), 3 * SS)
    for fx in (bx - 6 * SS, bx + bw + 6 * SS):
        pygame.draw.circle(s, _sh(GOLD, -50), (fx, rod_y), 4 * SS)
        pygame.draw.circle(s, GOLD, (fx, rod_y), 3 * SS)
        pygame.draw.circle(s, BRASS_L, (fx - SS, rod_y - SS), SS)

    # Soft drop shadow.
    drop = pygame.Surface((bw, bh + 8 * SS), pygame.SRCALPHA)
    pygame.draw.rect(drop, (0, 0, 0, 60), drop.get_rect(), border_radius=4 * SS)
    s.blit(drop, (bx + 3 * SS, by + 5 * SS))

    # The plum cloth field with a gentle vertical fold-shade so it reads as
    # fabric, not card.
    _vgrad_rrect(s, (bx, by, bw, bh), 4 * SS, _sh(PLUM, 24), _sh(PLUM, -28))
    fold = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for i in range(bw):
        t = i / bw
        shade = int(60 * math.sin(t * math.pi * 2.2)) - 10
        a = max(0, min(90, abs(shade)))
        col = (255, 255, 255, a) if shade > 0 else (0, 0, 0, a)
        pygame.draw.line(fold, col, (i, 0), (i, bh))
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bw, bh),
                     border_radius=4 * SS)
    fold.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(fold, (bx, by))

    # Lime + gold embroidered double border.
    pygame.draw.rect(s, LIME, (bx + 3 * SS, by + 3 * SS, bw - 6 * SS,
                     bh - 6 * SS), width=2 * SS, border_radius=3 * SS)
    pygame.draw.rect(s, GOLD, (bx + 6 * SS, by + 6 * SS, bw - 12 * SS,
                     bh - 12 * SS), width=SS, border_radius=2 * SS)

    # Scalloped weighted hem with gold beads.
    hy = by + bh
    nb = 7
    for i in range(nb):
        hx = bx + 4 * SS + int((bw - 8 * SS) * i / (nb - 1))
        pygame.draw.circle(s, _sh(PLUM, -34), (hx, hy), 3 * SS)
        pygame.draw.circle(s, _sh(PLUM, 6), (hx, hy - SS), 2 * SS)
    # Side tassels.
    for tx in (bx, bx + bw):
        pygame.draw.line(s, _sh(GOLD, -30), (tx, by + bh - 8 * SS),
                         (tx, by + bh + 6 * SS), 2 * SS)
        pygame.draw.circle(s, GOLD, (tx, by + bh + 7 * SS), 3 * SS)
        for k in range(3):
            pygame.draw.line(s, _sh(GOLD, -20),
                             (tx, by + bh + 9 * SS),
                             (tx - 2 * SS + k * 2 * SS, by + bh + 14 * SS), SS)

    _stamp_number(s, str(N), (cx, by + bh // 2), 42 * SS,
                  face=GOLD, edge=_sh(PLUM, -40), edge_px=2 * SS,
                  shadow=True, shadow_a=120)
    return s


# ── version C: festival swallowtail pennant on a crossbar (festival gold) ────

def sign_pennant(N, w, h):
    """A crisp festival swallowtail PENNANT hung from a horizontal crossbar:
    deep festival-gold field with a maroon chevron band and a lime pip, a
    notched swallowtail fly, a lit top seam — clean carved number. Subtle clown
    plum on the crossbar caps."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    rim_y = 6 * SS
    # Crossbar.
    bx0, bx1 = int(w * 0.16), int(w * 0.84)
    bar_y = int(h * 0.22)
    cord_x = cx
    _rope(s, (cord_x, rim_y), (cord_x, bar_y - 3 * SS), max(2, 2 * SS),
          col=_sh(WOOD, -10))
    pygame.draw.line(s, WOOD_D, (bx0, bar_y), (bx1, bar_y), 5 * SS)
    pygame.draw.line(s, WOOD_L, (bx0, bar_y - SS), (bx1, bar_y - SS), 2 * SS)
    for ex in (bx0, bx1):
        pygame.draw.circle(s, PLUM, (ex, bar_y), 4 * SS)
        pygame.draw.circle(s, _sh(PLUM, 60), (ex - SS, bar_y - SS), 2 * SS)

    # Swallowtail pennant body hanging from the bar.
    pw = int(w * 0.58)
    ptop = bar_y + 2 * SS
    plen = int(h * 0.56)
    left = cx - pw // 2
    right = cx + pw // 2
    notch = int(pw * 0.20)
    tip_y = ptop + plen
    body = [(left, ptop), (right, ptop), (right, ptop + plen - notch),
            (cx, tip_y - notch), (left, ptop + plen - notch)]
    # Drop shadow of the pennant.
    sh_pts = [(px + 3 * SS, py + 4 * SS) for px, py in body]
    pygame.draw.polygon(s, (0, 0, 0, 60), sh_pts)
    # Field with a vertical light->shade fill via a clipped gradient pass.
    minx = min(p[0] for p in body)
    maxx = max(p[0] for p in body)
    miny = min(p[1] for p in body)
    maxy = max(p[1] for p in body)
    field = pygame.Surface((maxx - minx + 1, maxy - miny + 1), pygame.SRCALPHA)
    fh = field.get_height()
    for i in range(fh):
        col = _mix(_sh(GOLD, 28), _sh(GOLD, -44), i / max(1, fh - 1))
        pygame.draw.line(field, col, (0, i), (field.get_width(), i))
    fmask = pygame.Surface(field.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(fmask, (255, 255, 255, 255),
                        [(px - minx, py - miny) for px, py in body])
    field.blit(fmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(field, (minx, miny))
    # Maroon chevron band behind the number.
    band_y = ptop + int(plen * 0.30)
    chev = [(left + 4 * SS, band_y), (right - 4 * SS, band_y),
            (right - 4 * SS, band_y + 24 * SS), (cx, band_y + 30 * SS),
            (left + 4 * SS, band_y + 24 * SS)]
    pygame.draw.polygon(s, (132, 40, 46), chev)
    pygame.draw.polygon(s, _sh((132, 40, 46), 30), chev, max(1, SS))
    # Lime pip at the tail.
    pygame.draw.circle(s, LIME, (cx, ptop + plen - notch - 6 * SS), 4 * SS)
    pygame.draw.circle(s, _sh(LIME, 50),
                       (cx - SS, ptop + plen - notch - 7 * SS), 2 * SS)
    # Lit top seam + dark fly edges.
    pygame.draw.line(s, _sh(GOLD, 50), (left, ptop + SS), (right, ptop + SS), SS)
    pygame.draw.polygon(s, _sh(GOLD, -70), body, max(1, SS))
    # Brass ring grommets on the top edge.
    for gx in (left + 8 * SS, right - 8 * SS):
        pygame.draw.circle(s, BRASS, (gx, ptop + 4 * SS), 3 * SS, max(1, SS))

    _stamp_number(s, str(N), (cx, band_y + 13 * SS), 30 * SS,
                  face=CREAM, edge=(96, 26, 30), edge_px=2 * SS,
                  shadow=True, shadow_a=110)
    return s


# ── version D: paper-lantern hanging tag (CLOWN; interior light, NO halo) ────

def sign_lantern(N, w, h):
    """A round paper-lantern hanging tag glowing from WITHIN — the interior
    light is a NORMAL-blended warm radial painted INSIDE the lantern body only
    (clipped to the paper), never an additive disc over the sky. Plum cap +
    base, lime ribs, gold tassel; the number reads as a dark cut-out lit from
    behind the paper."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    rim_y = 6 * SS
    cy = int(h * 0.50)
    rw = int(w * 0.30)            # lantern half-width (slightly squashed sphere)
    rh = int(h * 0.30)

    # Cord from rim to the top cap.
    _rope(s, (cx, rim_y), (cx, cy - rh - 4 * SS), max(2, 2 * SS),
          col=_sh(GOLD, -30))

    # Soft contact shadow under the lantern (normal-blended, dark — not white).
    drop = pygame.Surface((rw * 2, rh), pygame.SRCALPHA)
    pygame.draw.ellipse(drop, (0, 0, 0, 55), drop.get_rect())
    s.blit(drop, (cx - rw, cy + rh - rh // 2 + 5 * SS))

    # Paper body: a warm paper gradient on the lantern itself. Interior glow is
    # a radial painted ONTO the body surface then clipped to the ellipse, so the
    # light lives INSIDE the paper and can never wash the sky.
    body = pygame.Surface((rw * 2 + 2, rh * 2 + 2), pygame.SRCALPHA)
    bc = (rw + 1, rh + 1)
    # Base paper (warm amber, plum-tinted toward the rim for the clown tie).
    for r in range(max(rw, rh), 0, -1):
        t = r / max(rw, rh)
        paper = _mix((255, 236, 170), (236, 150, 96), t)        # lit core -> warm edge
        paper = _mix(paper, _sh(PLUM, 40), 0.18 * t)            # subtle plum cool at rim
        pygame.draw.ellipse(body, paper,
                            (bc[0] - int(rw * t), bc[1] - int(rh * t),
                             int(rw * t) * 2, int(rh * t) * 2))
    # Lime vertical ribs (clipped by the body alpha at blit time via a mask).
    for i in range(-2, 3):
        rx = bc[0] + int(rw * i / 3)
        pygame.draw.line(body, (*_sh(LIME, -10), 120),
                         (rx, bc[1] - rh), (rx, bc[1] + rh), max(1, SS))
    # Two horizontal hoop wires.
    for hy in (bc[1] - rh // 2, bc[1] + rh // 2):
        pygame.draw.line(body, (*_sh(GOLD, -40), 110),
                         (bc[0] - rw, hy), (bc[0] + rw, hy), max(1, SS))
    # Clip everything to the ellipse so nothing leaks past the paper.
    emask = pygame.Surface(body.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(emask, (255, 255, 255, 255), emask.get_rect())
    body.blit(emask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Rim outline + a top-left specular sheen so the paper reads taut.
    pygame.draw.ellipse(body, _sh((236, 150, 96), -50), body.get_rect(),
                        max(1, SS))
    s.blit(body, (cx - rw - 1, cy - rh - 1))

    # Plum cap + base discs with gold collars.
    for sgn, yy in ((-1, cy - rh), (1, cy + rh)):
        cap = pygame.Rect(0, 0, rw, 7 * SS)
        cap.center = (cx, yy)
        pygame.draw.ellipse(s, _sh(PLUM, -20), cap)
        pygame.draw.ellipse(s, PLUM, cap.inflate(-2 * SS, -2 * SS))
        pygame.draw.line(s, GOLD, (cap.left + 2 * SS, cap.centery),
                         (cap.right - 2 * SS, cap.centery), max(1, SS))
    # Gold tassel under the base.
    pygame.draw.line(s, _sh(GOLD, -30), (cx, cy + rh + 2 * SS),
                     (cx, cy + rh + 8 * SS), 2 * SS)
    pygame.draw.circle(s, GOLD, (cx, cy + rh + 9 * SS), 3 * SS)
    for k in range(3):
        pygame.draw.line(s, _sh(GOLD, -10), (cx, cy + rh + 11 * SS),
                         (cx - 2 * SS + k * 2 * SS, cy + rh + 16 * SS), SS)

    # The number reads as a dark cut-out lit from behind the paper: a deep plum
    # face with a faint warm back-light edge (NOT a glow disc).
    _stamp_number(s, str(N), (cx, cy), 34 * SS,
                  face=(72, 30, 30), edge=(255, 226, 150), edge_px=SS,
                  shadow=False)
    return s


# ── version E: ornate gilt medallion / cartouche (temple gold + jewels) ──────

def sign_medallion(N, w, h):
    """An ornate gilt MEDALLION: a beaded brass outer ring, a scalloped sun-disc
    frame, a deep plum enamel centre, a small plum ribbon banner draped over the
    top, and four jewel cabochons (lime + red) at the cardinal points. The
    number is gilt with a dark engraved edge. Temple-gold lead with clown jewels."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    rim_y = 6 * SS
    cy = int(h * 0.52)
    R = int(min(w, h) * 0.30)

    # Twin cords to a top suspension ring.
    ring_y = cy - R - 6 * SS
    pygame.draw.circle(s, _sh(BRASS, -50), (cx, ring_y), 5 * SS, 2 * SS)
    pygame.draw.circle(s, BRASS, (cx, ring_y), 5 * SS, max(1, SS))
    for off in (-1, 1):
        _rope(s, (cx + off * 4 * SS, rim_y), (cx, ring_y - 4 * SS),
              max(2, 2 * SS), col=_sh(GOLD, -30))

    # Contact drop shadow.
    drop = pygame.Surface((R * 2 + 4 * SS, R * 2 + 4 * SS), pygame.SRCALPHA)
    pygame.draw.circle(drop, (0, 0, 0, 60), drop.get_rect().center, R)
    s.blit(drop, (cx - R + 3 * SS, cy - R + 5 * SS))

    # Scalloped sun-disc frame: a ring of rounded lobes radiating out.
    nl = 20
    for i in range(nl):
        a = i * math.tau / nl
        lx = cx + int(math.cos(a) * (R + 4 * SS))
        ly = cy + int(math.sin(a) * (R + 4 * SS))
        pygame.draw.circle(s, _sh(GOLD, -55), (lx, ly), 5 * SS)
        pygame.draw.circle(s, GOLD, (lx, ly), 4 * SS)
        pygame.draw.circle(s, BRASS_L, (lx - SS, ly - SS), max(1, SS))

    # Brass outer ring with a beaded inner edge (carved, top-lit).
    pygame.draw.circle(s, _sh(BRASS_D, -20), (cx, cy), R)
    pygame.draw.circle(s, BRASS_L, (cx, cy), R, 3 * SS)
    pygame.draw.circle(s, _sh(BRASS_D, -10), (cx, cy), R - 4 * SS, 2 * SS)
    nb = 28
    for i in range(nb):
        a = i * math.tau / nb
        bxp = cx + int(math.cos(a) * (R - 7 * SS))
        byp = cy + int(math.sin(a) * (R - 7 * SS))
        pygame.draw.circle(s, BRASS_L, (bxp, byp), max(1, SS))

    # Deep plum enamel centre with a radial value falloff (recessed dome).
    ir = R - 12 * SS
    for r in range(ir, 0, -1):
        t = r / ir
        col = _mix(_sh(PLUM, 30), _sh(PLUM, -40), t)
        pygame.draw.circle(s, col, (cx, cy), r)
    pygame.draw.circle(s, _sh(PLUM, -60), (cx, cy), ir, max(1, SS))

    # Four jewel cabochons at the cardinal points (lime N/S, red E/W).
    for i, col in enumerate((LIME, REDN, LIME, REDN)):
        a = i * math.pi / 2 - math.pi / 2
        jx = cx + int(math.cos(a) * (R - 7 * SS))
        jy = cy + int(math.sin(a) * (R - 7 * SS))
        pygame.draw.circle(s, _sh(col, -60), (jx, jy), 4 * SS)
        pygame.draw.circle(s, col, (jx, jy), 3 * SS)
        pygame.draw.circle(s, _sh(col, 90), (jx - SS, jy - SS), max(1, SS))

    # Plum ribbon banner draped across the top of the disc (host accent).
    bw = int(R * 1.5)
    bnr = pygame.Rect(0, 0, bw, 12 * SS)
    bnr.center = (cx, cy - R + 2 * SS)
    pygame.draw.rect(s, _sh(PLUM, -10), bnr, border_radius=3 * SS)
    pygame.draw.rect(s, GOLD, bnr, width=SS, border_radius=3 * SS)
    for sgn in (-1, 1):
        tail = [(bnr.centerx + sgn * bw // 2, bnr.top),
                (bnr.centerx + sgn * (bw // 2 + 6 * SS), bnr.top - 5 * SS),
                (bnr.centerx + sgn * (bw // 2 + 6 * SS), bnr.bottom + 3 * SS)]
        pygame.draw.polygon(s, _sh(PLUM, -30), tail)

    _stamp_number(s, str(N), (cx, cy + 2 * SS), 38 * SS,
                  face=GOLD, edge=_sh(PLUM, -50), edge_px=2 * SS,
                  shadow=True, shadow_a=110)
    return s


VERSIONS = [
    ("A", sign_carved_wood,
     "Rope-hung carved-wood plaque — warm wood + gilt, brass studs, plum ribbon"),
    ("B", sign_cloth_banner,
     "Hanging cloth scroll — CLOWN plum field, lime+gold border, tassels"),
    ("C", sign_pennant,
     "Festival swallowtail pennant — festival gold + maroon chevron, lime pip"),
    ("D", sign_lantern,
     "Paper-lantern tag — CLOWN, interior warm light (clipped, no halo)"),
    ("E", sign_medallion,
     "Ornate gilt medallion — temple gold, plum enamel, lime/red jewels"),
]


def _draw_rim_slice(cell, cw, top_h):
    """Paint the bright sky + a slice of the pagoda top-gap RIM the sign hangs
    from, so each sign is judged on the real backdrop (light blue sky over a
    curved sandstone eave). The sign hangs from the rim's underside."""
    # Sky gradient (slightly lighter toward the rim, like the live day sky).
    for y in range(cell.get_height()):
        t = y / cell.get_height()
        c = _mix(_sh(SKY, 18), _sh(SKY, -22), t)
        pygame.draw.line(cell, c, (0, y), (cw, y))
    # The eave: a broad sandstone arc spanning the cell top, curving down at the
    # sides like the underside of a pagoda gap, with a shaded soffit lip the
    # cords loop over.
    stone = (224, 192, 150)
    arc = pygame.Surface((cw, top_h * 3), pygame.SRCALPHA)
    pygame.draw.ellipse(arc, stone, (-cw // 3, -top_h * 2, cw + 2 * cw // 3,
                        top_h * 3))
    pygame.draw.ellipse(arc, _sh(stone, -36),
                        (-cw // 3, -top_h * 2 + top_h // 2,
                         cw + 2 * cw // 3, top_h * 3), 0)
    # Re-light the top of the eave.
    pygame.draw.ellipse(arc, stone, (-cw // 3, -top_h * 2,
                        cw + 2 * cw // 3, top_h * 3 - top_h // 2))
    cell.blit(arc, (0, 0))
    # Soffit shadow line under the rim where the sign attaches.
    pygame.draw.line(cell, _sh(stone, -55), (0, top_h), (cw, top_h), 2 * SS)
    pygame.draw.line(cell, (0, 0, 0, 60), (0, top_h + 2 * SS),
                     (cw, top_h + 2 * SS), SS)


def render_cell(label, fn, caption, N):
    """One full review cell: sky + pagoda rim backdrop, the hero N=18 sign hung
    from the rim, a small N=8 inset (to check single-digit width), and the
    label/caption — all composited at SS then smooth-scaled to the cell size."""
    CW, CH = 300, 360                                  # final cell px
    cw, ch = CW * SS, CH * SS
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    rim_h = int(ch * 0.10)
    _draw_rim_slice(cell, cw, rim_h)

    # Hero sign (N=18) hung from the rim.
    sign_w, sign_h = int(cw * 0.74), int(ch * 0.62)
    hero = fn(N, sign_w, sign_h)
    cell.blit(hero, (cw // 2 - sign_w // 2, rim_h - 6 * SS))

    # Single-digit inset (N=8) — a smaller copy on a softened panel bottom-right
    # so both number widths can be compared.
    iw, ih = int(cw * 0.30), int(ch * 0.26)
    ins = fn(8, int(iw * 2.1), int(ih * 2.1))
    ins = pygame.transform.smoothscale(ins, (iw, ih))
    panel = pygame.Rect(cw - iw - 8 * SS, ch - ih - 22 * SS, iw, ih)
    bgp = pygame.Surface((iw, ih), pygame.SRCALPHA)
    bgp.fill((255, 255, 255, 28))
    cell.blit(bgp, panel.topleft)
    cell.blit(ins, panel.topleft)
    itag = hud._font(9 * SS, True).render("N=8", True, (40, 40, 50))
    cell.blit(itag, (panel.x + 2 * SS, panel.y - 11 * SS))

    out = pygame.transform.smoothscale(cell, (CW, CH))

    # Label chip + caption, drawn at final res for crisp small text.
    chip = pygame.Rect(8, 8, 30, 26)
    pygame.draw.rect(out, (40, 30, 50), chip, border_radius=6)
    pygame.draw.rect(out, GOLD, chip, width=2, border_radius=6)
    lt = hud._font(20, True).render(label, True, GOLD)
    out.blit(lt, lt.get_rect(center=chip.center))
    cap = hud._font(12, True)
    # Wrap the caption to fit the cell width.
    words = caption.split()
    lines, cur = [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if cap.size(test)[0] > CW - 52:
            lines.append(cur)
            cur = wd
        else:
            cur = test
    if cur:
        lines.append(cur)
    for i, line in enumerate(lines[:3]):
        ct = cap.render(line, True, (28, 24, 36))
        sh = cap.render(line, True, (255, 255, 255))
        out.blit(sh, (45, 11 + i * 14))
        out.blit(ct, (44, 10 + i * 14))
    return out


def main():
    N = 18
    cells = [render_cell(lbl, fn, cap, N) for lbl, fn, cap in VERSIONS]
    CW, CH = cells[0].get_width(), cells[0].get_height()

    pad = 18
    title_h = 56
    cols = 3
    rows = 2
    sheet_w = cols * CW + (cols + 1) * pad
    sheet_h = title_h + rows * CH + (rows + 1) * pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((222, 226, 232))
    # Title bar.
    pygame.draw.rect(sheet, (38, 28, 52), (0, 0, sheet_w, title_h))
    tf = hud._font(30, True)
    title = "Warren Route Sign — Round 1"
    ti = tf.render(title, True, GOLD)
    sheet.blit(ti, (pad, (title_h - ti.get_height()) // 2))
    sub = hud._font(14, True).render(
        "Hero N=18 hung from a pagoda gap-rim  •  inset = single-digit N=8",
        True, (210, 210, 220))
    sheet.blit(sub, (pad + ti.get_width() + 18,
               (title_h - sub.get_height()) // 2 + 2))

    for i, cell in enumerate(cells):
        r, c = divmod(i, cols)
        x = pad + c * (CW + pad)
        y = title_h + pad + r * (CH + pad)
        pygame.draw.rect(sheet, (150, 150, 160), (x - 2, y - 2, CW + 4, CH + 4),
                         border_radius=6)
        sheet.blit(cell, (x, y))

    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs",
                           "warren_sign")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.normpath(os.path.join(out_dir, "round_1.png"))
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
