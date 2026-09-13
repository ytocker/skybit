"""Look-dev mockup for the "Dice Clown" pre-warren clearing concept.

Before a Pagoda Warren route the parrot reaches a CLEARING WITH NO PAGODAS:
a large, charming, casual-game-friendly CLOWN stands on the ground and OFFERS
a glowing power-up DIE — taking the die rolls the route length. This script
renders ONE candidate sheet of 10 distinct clown archetypes, each cropped tight
so the clown fills the cell (chunky mascot proportions, presenting pose, one
gloved hand raised toward the die), with the real parrot flying in for scale.

Everything is drawn from pygame primitives — no PNG sprites. We import only the
REAL game helpers (the biome palette, the glow cache, the live parrot sprite)
and mutate no game state. Each cell is supersampled at 2x then smoothscaled down
for crisp anti-aliasing.

    PYTHONPATH=. python tools/render_clown_dice.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H, GROUND_Y
from game.draw import lerp_color, blit_glow
from game.parrot import get_parrot
from tools.render_warren_mockup import shaped_palette


# Day phase for the clearing — matches the warren mockup's DAY column so the
# sheet reads as the same world a beat before the corridor.
DAY_PHASE = 0.05

# Supersample factor: draw each cell at SS x then smoothscale down so every
# curved clown edge and pip is anti-aliased. Kept at the source resolution; the
# final per-cell display size (sw/sh) is ~2x round 2 so the sheet reads big.
SS = 2

# Each cell is a TIGHT crop around the figure rather than the full 360x640
# canvas — the clown should fill ~70-80% of the cell height, not float in a sea
# of empty sky. The viewport carries deliberate UPPER-RIGHT headroom so the
# offered die floats fully CLEAR of the head silhouette (like a takeable coin /
# surprise box hovering beside the clown), never occluding the face.
VIEW_W = 200
VIEW_H = 256
# Where the boots meet the ground inside the viewport (leaves a sliver of grass
# + cast shadow below). The figure sits low so the head lands in the middle band
# and the die can float in the clear upper-right corner.
VIEW_FEET_Y = VIEW_H - 26


# ── small colour helpers (local — never touch game state) ────────────────────

def _shade(c, d):
    return (max(0, min(255, int(c[0] + d))),
            max(0, min(255, int(c[1] + d))),
            max(0, min(255, int(c[2] + d))))


def _toward(c, t, f):
    return (int(c[0] + (t[0] - c[0]) * f),
            int(c[1] + (t[1] - c[1]) * f),
            int(c[2] + (t[2] - c[2]) * f))


def _outline_ellipse(surf, color, rect, oc=None, w=1):
    pygame.draw.ellipse(surf, color, rect)
    pygame.draw.ellipse(surf, oc or _shade(color, -70), rect, w)


def _poly(surf, color, pts, oc=None, w=1):
    pygame.draw.polygon(surf, color, pts)
    if oc is not False:
        pygame.draw.polygon(surf, oc or _shade(color, -70), pts, w)


# Shared ink / accent constants in the parrot family.
INK = (28, 22, 30)
WHITE = (250, 248, 244)
# Warm ivory face base — never dead chalk-white, so whiteface clowns read
# friendly rather than ghostly at scale.
IVORY = (248, 242, 230)
ROSY = (255, 150, 150)
# Top-left key light to match the coin/HUD lighting direction.
RIM = (255, 250, 235)


# ── chunky clown body kit ─────────────────────────────────────────────────────
# Every clown is composited from the same primitive vocabulary so the ten read
# as ONE family of casual-cute mascots. The build is intentionally CHUNKY (~4-5
# heads tall): thick limbs, rounded cuffs, gloved hands, big anchoring shoes —
# Crossy Road / Rayman / Patapon proportions, not realistic lankiness.

def _shadow(surf, cx, feet_y, w, alpha=105):
    """Soft drop shadow ellipse at the feet — grounds the figure."""
    sh = pygame.Surface((w, w // 3 + 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (20, 18, 26, alpha), sh.get_rect())
    surf.blit(sh, (cx - w // 2, feet_y - 5))


def _shoes(surf, cx, feet_y, sep, length, color, toe=None):
    """Big rounded clown shoes splayed left/right — the heavy anchoring
    footprint that sells a chunky mascot."""
    toe = toe or _shade(color, 35)
    for s in (-1, 1):
        bx = cx + s * sep
        shoe = pygame.Rect(0, 0, length, 18)
        if s < 0:
            shoe.topright = (bx + length // 3, feet_y)
        else:
            shoe.topleft = (bx - length // 3, feet_y)
        pygame.draw.ellipse(surf, _shade(color, -55), shoe)
        inner = shoe.inflate(-3, -3)
        pygame.draw.ellipse(surf, color, inner)
        # Lit toe-cap (top-left key) so the rounded shoe catches light.
        cap = pygame.Rect(0, 0, length // 2, 9)
        cap.center = (shoe.centerx + s * length // 6, shoe.top + 5)
        pygame.draw.ellipse(surf, toe, cap)


def _leg(surf, hip, ankle, w, color, stripe=None):
    """One thick tapered leg with a rounded cuff at the ankle."""
    pygame.draw.line(surf, _shade(color, -50), hip, ankle, w + 3)
    pygame.draw.line(surf, color, hip, ankle, w)
    # Top-left rim on the leg.
    pygame.draw.line(surf, _shade(color, 35),
                     (hip[0] - 1, hip[1]), (ankle[0] - 1, ankle[1] - 3),
                     max(1, w // 3))
    pygame.draw.circle(surf, _shade(color, -40), ankle, w // 2 + 2)
    if stripe is not None:
        pygame.draw.line(surf, stripe, hip, ankle, max(1, w // 3))


def _legs(surf, cx, hip_y, feet_y, sep, w, color, stripe=None):
    """Two chunky legs from hips to ankles, slight stance offset so the figure
    isn't a stiff symmetrical T."""
    for s in (-1, 1):
        hip = (cx + s * (sep - 4), hip_y)
        ankle = (cx + s * sep, feet_y - 9)
        _leg(surf, hip, ankle, w, color, stripe)


def _arm(surf, shoulder, hand, w, color, glove=(252, 250, 246), up=False):
    """A chunky tapered arm ending in a big round GLOVED hand. `up=True` is the
    presenting gesture: the hand opens toward the die above."""
    # Elbow bend so the limb reads as a real arm, not a noodle.
    mx = (shoulder[0] + hand[0]) // 2
    my = (shoulder[1] + hand[1]) // 2 + (-2 if up else 4)
    pygame.draw.line(surf, _shade(color, -50), shoulder, (mx, my), w + 3)
    pygame.draw.line(surf, _shade(color, -50), (mx, my), hand, w + 1)
    pygame.draw.line(surf, color, shoulder, (mx, my), w)
    pygame.draw.line(surf, color, (mx, my), hand, w - 1)
    # Rounded cuff at the wrist.
    pygame.draw.circle(surf, _shade(color, 30), (mx, my), w // 2 + 1)
    pygame.draw.circle(surf, (250, 250, 252), hand, w - 1)
    # Big round gloved hand with a darker keyline + top-left sheen.
    gr = w
    pygame.draw.circle(surf, _shade(glove, -55), hand, gr + 1)
    pygame.draw.circle(surf, glove, hand, gr)
    pygame.draw.circle(surf, RIM, (hand[0] - 2, hand[1] - 2), max(1, gr // 3))
    # Thumb nub for an open offering palm when raised.
    if up:
        pygame.draw.circle(surf, glove, (hand[0] - gr, hand[1] + 1),
                           max(2, gr // 2))
        pygame.draw.circle(surf, _shade(glove, -55),
                           (hand[0] - gr, hand[1] + 1), max(2, gr // 2), 1)


def _facet_body(surf, pts, base, *, top_left_lift=40):
    """Fill a costume panel with sculpted shading: the body fill, a lighter
    top-left facet, a soft underside shadow, and a left-edge rim — so the
    costume reads dimensional instead of flat."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    pygame.draw.polygon(surf, base, pts)
    # Underside shadow (bottom band).
    shade = pygame.Surface((maxx - minx + 2, maxy - miny + 2), pygame.SRCALPHA)
    band = pygame.Rect(0, (maxy - miny) * 2 // 3, maxx - minx + 2,
                       (maxy - miny) // 3 + 2)
    pygame.draw.rect(shade, (0, 0, 0, 55), band)
    shade.blit(_poly_mask(pts, minx, miny, maxx, maxy),
               (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shade, (minx, miny))
    # Top-left lit facet.
    lit = pygame.Surface((maxx - minx + 2, maxy - miny + 2), pygame.SRCALPHA)
    lit_c = _shade(base, top_left_lift)
    pygame.draw.polygon(lit, (*lit_c, 150),
                        [(p[0] - minx, p[1] - miny) for p in pts])
    facet = pygame.Surface((maxx - minx + 2, maxy - miny + 2), pygame.SRCALPHA)
    pygame.draw.polygon(facet, (255, 255, 255, 255),
                        [(0, 0), ((maxx - minx) * 2 // 3, 0),
                         (0, (maxy - miny) * 2 // 3)])
    lit.blit(facet, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lit, (minx, miny))
    # Crisp left-edge rim light so low-contrast costumes lift off the blue sky.
    pygame.draw.lines(surf, _shade(base, 55), False,
                      [(minx + 1, miny + 4), (minx + 1, maxy - 4)], 2)
    pygame.draw.polygon(surf, _shade(base, -65), pts, 2)


def _poly_mask(pts, minx, miny, maxx, maxy):
    m = pygame.Surface((maxx - minx + 2, maxy - miny + 2), pygame.SRCALPHA)
    pygame.draw.polygon(m, (255, 255, 255, 255),
                        [(p[0] - minx, p[1] - miny) for p in pts])
    return m


def _round_head(surf, cx, cy, r, skin, *, blush=True, white_face=False):
    """Round friendly head. Whiteface clowns get a warm IVORY base (never dead
    chalk-white). Always rosy-cheeked + a top-left rim + 2px keyline."""
    base = IVORY if white_face else skin
    pygame.draw.circle(surf, _shade(base, -55), (cx, cy), r + 1)
    pygame.draw.circle(surf, base, (cx, cy), r)
    # Top-left key sheen.
    sheen = pygame.Surface((r, r), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 70), sheen.get_rect())
    surf.blit(sheen, (cx - r + 2, cy - r + 2))
    # Soft underside shadow on the jaw.
    jaw = pygame.Surface((r * 2, r), pygame.SRCALPHA)
    pygame.draw.ellipse(jaw, (0, 0, 0, 35), (0, -r // 2, r * 2, r))
    surf.blit(jaw, (cx - r, cy + r // 3))
    pygame.draw.circle(surf, _shade(base, -55), (cx, cy), r, 2)
    if blush:
        for s in (-1, 1):
            pygame.draw.ellipse(surf, ROSY,
                                (cx + s * (r - 8) - 4, cy + 2, 9, 7))


def _eyes(surf, cx, cy, r, *, style="happy", color=INK):
    """Friendly eyes — NEVER empty dark sockets. styles: 'happy' upturned
    smile-arcs, 'dot' big highlighted pupils, 'sad' gentle downturn."""
    ex = max(5, r // 2)
    for s in (-1, 1):
        px = cx + s * ex
        if style == "happy":
            pygame.draw.arc(surf, color, (px - 5, cy - 3, 10, 9),
                            math.pi, math.tau, 3)
        elif style == "sad":
            # Gentle downturn but still soft rounded dots + highlight, not voids.
            pygame.draw.circle(surf, color, (px, cy), 3)
            pygame.draw.circle(surf, WHITE, (px - 1, cy - 2), 1)
            pygame.draw.arc(surf, color, (px - 5, cy - 6, 10, 8),
                            math.pi * 1.15, math.tau * 0.95, 1)
        else:  # dot
            pygame.draw.circle(surf, WHITE, (px, cy), 5)
            pygame.draw.circle(surf, _shade(color, 10), (px, cy + 1), 3)
            pygame.draw.circle(surf, WHITE, (px - 1, cy - 2), 2)


def _nose(surf, cx, cy, r, color=(232, 56, 56)):
    """The signature round ball nose, always with a specular dot."""
    pygame.draw.circle(surf, _shade(color, -60), (cx, cy), r + 1)
    pygame.draw.circle(surf, color, (cx, cy), r)
    pygame.draw.circle(surf, _shade(color, 100),
                       (cx - r // 2, cy - r // 2), max(1, r // 3))


def _smile(surf, cx, cy, w, color=(200, 60, 70)):
    """Big warm grin — always curved UP."""
    rect = (cx - w // 2, cy - w // 3, w, int(w * 0.85))
    pygame.draw.arc(surf, color, rect, math.pi * 1.05, math.tau * 0.97, 3)
    pygame.draw.arc(surf, _shade(color, 90), rect,
                    math.pi * 1.12, math.tau * 0.94, 1)


def _ruff(surf, cx, cy, r, color, lobes=11):
    """Ruffled neck collar — a ring of overlapping scallops with lit tops."""
    for i in range(lobes):
        a = i * math.tau / lobes
        lx = cx + math.cos(a) * r
        ly = cy + math.sin(a) * r * 0.5
        rad = r // 3 + 3
        pygame.draw.circle(surf, _shade(color, -50), (int(lx), int(ly)), rad)
        pygame.draw.circle(surf, color, (int(lx), int(ly)), rad - 1)
        pygame.draw.circle(surf, _shade(color, 45),
                           (int(lx) - 1, int(ly) - 1), max(1, rad // 3))
    pygame.draw.circle(surf, _shade(color, 35), (cx, cy), r // 2)
    pygame.draw.circle(surf, _shade(color, -30), (cx, cy), r // 2, 1)


def _pompoms(surf, cx, top_y, bot_y, color, n=3):
    """Vertical row of costume pom-pom buttons."""
    for i in range(n):
        t = i / max(1, n - 1)
        py = int(top_y + (bot_y - top_y) * t)
        pygame.draw.circle(surf, _shade(color, -55), (cx, py), 5)
        pygame.draw.circle(surf, color, (cx, py), 4)
        pygame.draw.circle(surf, _shade(color, 85), (cx - 1, py - 1), 2)


# ── the floating power-up DIE ─────────────────────────────────────────────────
# CONSISTENT across all ten cells (the clown varies, the die doesn't). It reads
# as a real power-up: a soft circular gold glow halo (BLEND_ADD via the cached
# glow surface), a gentle bob, classic d6 PIPS (never a printed number on the
# hero die), a top-left RIM LIGHT matching the coin/HUD key, and 4 orbiting
# sparkles. A small INSET in one or two cells shows the rolled RESULT number to
# hint the route-length mechanic.

# The hero die always shows the same face so it reads as one consistent prop.
HERO_PIPS = 5

_PIP_LAYOUT = {
    1: [(0.5, 0.5)],
    2: [(0.30, 0.30), (0.70, 0.70)],
    3: [(0.28, 0.28), (0.5, 0.5), (0.72, 0.72)],
    4: [(0.30, 0.30), (0.70, 0.30), (0.30, 0.70), (0.70, 0.70)],
    5: [(0.28, 0.28), (0.72, 0.28), (0.5, 0.5), (0.28, 0.72), (0.72, 0.72)],
    6: [(0.30, 0.26), (0.70, 0.26), (0.30, 0.5), (0.70, 0.5),
        (0.30, 0.74), (0.70, 0.74)],
}


def _draw_die_face(surf, cx, cy, size, *, pips=None, number=None,
                   body=(252, 250, 244), pip_col=(44, 40, 58)):
    """A single rounded-square die face with a top-left rim light, sculpted
    sheen, and either d6 pips or a roll number."""
    half = size // 2
    rect = pygame.Rect(cx - half, cy - half, size, size)
    # Soft cast shadow under the die for float.
    sh = pygame.Surface((size + 8, size // 2), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (20, 16, 30, 75), sh.get_rect())
    surf.blit(sh, (cx - half - 4, cy + half))
    br = size // 5
    # Body with a baked top-down sheen + a thin top-left rim highlight.
    pygame.draw.rect(surf, _shade(body, -70), rect, border_radius=br)
    inner = rect.inflate(-3, -3)
    pygame.draw.rect(surf, body, inner, border_radius=br)
    pygame.draw.rect(surf, _shade(body, 28),
                     pygame.Rect(inner.x, inner.y, inner.w, inner.h // 2),
                     border_radius=br)
    # Top-left rim light (matches coin/HUD key direction).
    pygame.draw.line(surf, RIM, (inner.left + br, inner.top + 1),
                     (inner.right - br, inner.top + 1), 2)
    pygame.draw.line(surf, RIM, (inner.left + 1, inner.top + br),
                     (inner.left + 1, inner.bottom - br), 2)
    pygame.draw.rect(surf, _shade(body, -80), rect, 2, border_radius=br)
    if number is not None:
        f = pygame.font.SysFont(None, int(size * 0.72), bold=True)
        txt = f.render(str(number), True, pip_col)
        surf.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
    elif pips is not None:
        pr = max(2, size // 8)
        for fx, fy in _PIP_LAYOUT[pips]:
            px = rect.x + int(fx * size)
            py = rect.y + int(fy * size)
            pygame.draw.circle(surf, _shade(pip_col, -25), (px, py), pr)
            pygame.draw.circle(surf, pip_col, (px, py), pr - 1)
            pygame.draw.circle(surf, _shade(pip_col, 130), (px - 1, py - 1), 1)


def draw_floating_die(surf, cx, base_y, pulse, *, show_inset=False,
                      halo_boost=0):
    """The complete power-up read: gold glow halo + gently bobbing pip-die +
    rim light + 4 orbiting sparkles. The die floats OFF to one side of the
    clown, clear of the head — a distinct takeable pickup the player reaches
    for. `show_inset` adds a tiny rolled-result chip to hint that the die
    resolves to a route-length number; `halo_boost` strengthens the gold glow
    for low-contrast clowns (e.g. Pierrot on pale sky)."""
    cy = int(base_y + math.sin(pulse * 1.1) * 3)
    size = 40  # ~ a clown head — a clear secondary focal.

    # Warm gold radial glow halo behind the die.
    glow_r = 42
    blit_glow(surf, cx, cy, glow_r, (255, 205, 85),
              alpha=min(255, 120 + halo_boost
                        + int(35 * (0.5 + 0.5 * math.sin(pulse * 1.3)))))
    blit_glow(surf, cx, cy, glow_r - 16, (255, 245, 200),
              alpha=min(255, 120 + halo_boost))

    _draw_die_face(surf, cx, cy, size, pips=HERO_PIPS)

    # Two-state hint: a small inset chip showing the die has tumbled to a
    # route-length RESULT — only in flagged cells so the hero die stays a pip
    # die. Pushed further out (up-right) so it never crowds the hero die.
    if show_inset:
        ins = 24
        ix, iy = cx + 40, cy - 36
        # Little motion-arc from the hero die to the result chip.
        for k in range(4):
            t = k / 4
            ax = int(cx + (ix - cx) * t)
            ay = int(cy + (iy - cy) * t) - int(9 * math.sin(t * math.pi))
            pygame.draw.circle(surf, (250, 225, 150), (ax, ay), max(1, 3 - k))
        _draw_die_face(surf, ix, iy, ins, number=27,
                       body=(255, 246, 224), pip_col=(190, 70, 40))

    # Sparkle twinkles orbiting the die — Coin sparkle style at staggered phases.
    for i in range(4):
        a = i * math.tau / 4 + pulse * 0.4
        rr = 30 + 4 * math.sin(pulse * 0.9 + i)
        sx = int(cx + math.cos(a) * rr)
        sy = int(cy + math.sin(a) * rr * 0.85)
        tw = 0.5 + 0.5 * math.sin(pulse * 2.0 + i * 1.7)
        al = int(110 + 130 * tw)
        sz = 3 + int(2 * tw)
        spark = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
        c = (255, 244, 200, al)
        pygame.draw.line(spark, c, (sz * 2, 0), (sz * 2, sz * 4), 1)
        pygame.draw.line(spark, c, (0, sz * 2), (sz * 4, sz * 2), 1)
        pygame.draw.circle(spark, (255, 255, 230, al), (sz * 2, sz * 2), sz)
        surf.blit(spark, (sx - sz * 2, sy - sz * 2),
                  special_flags=pygame.BLEND_ADD)


# ── the ten clowns ────────────────────────────────────────────────────────────
# Each draws ONE chunky clown standing at (cx, feet_y) with a PRESENTING pose:
# one gloved hand raised toward the die, weight on one leg, slight lean. All ten
# share the shoe/leg/arm/head kit but own a distinct silhouette via hat, collar,
# costume mass and palette. Right hand (cx + ...) reaches up to the die; the left
# rests on the hip / props a prop for an asymmetric, lively stance.

# Local convention: the die hovers above-right of the head; the raised hand
# reaches toward `hand_up`. Heads are big (~hr 22-27) for the 4-5-head build.


def clown_whiteface(surf, cx, feet_y, hand_up):
    """Elegant noble whiteface: warm-ivory face, tall blue cone hat, huge red
    ruff. Chunky tunic, presenting one gloved hand to the die."""
    hip_y = feet_y - 96
    _shoes(surf, cx, feet_y, 18, 34, (44, 64, 155))
    _legs(surf, cx, hip_y, feet_y, 13, 12, (236, 236, 242))
    _facet_body(surf, [(cx - 30, hip_y + 8), (cx + 30, hip_y + 8),
                       (cx + 19, hip_y - 56), (cx - 19, hip_y - 56)],
                (212, 44, 64))
    _pompoms(surf, cx, hip_y - 48, hip_y - 2, (250, 240, 120), 4)
    neck_y = hip_y - 56
    # Left hand on hip; right hand presents the die.
    _arm(surf, (cx - 24, hip_y - 46), (cx - 30, hip_y - 14), 8, (210, 44, 64))
    _arm(surf, (cx + 24, hip_y - 48), hand_up, 8, (210, 44, 64), up=True)
    _ruff(surf, cx, neck_y, 26, (236, 236, 246), lobes=13)
    hr = 23
    hy = neck_y - hr - 4
    _round_head(surf, cx, hy, hr, None, white_face=True, blush=False)
    # Trends austere otherwise — so give him the MOST blush of the set (big
    # warm cheek discs) and the widest up-curved grin so he reads unmistakably
    # playful, never uncanny.
    for s in (-1, 1):
        cheek = pygame.Surface((20, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(cheek, (255, 150, 150, 200), cheek.get_rect())
        surf.blit(cheek, (cx + s * (hr - 7) - 10, hy + 1))
    _eyes(surf, cx, hy - 2, hr, style="happy")
    for s in (-1, 1):
        pygame.draw.circle(surf, (212, 44, 64), (cx + s * 11, hy - 11), 2)
    _nose(surf, cx, hy + 5, 5, (222, 72, 92))
    _smile(surf, cx, hy + 12, 24, (210, 56, 76))
    tip = (cx + 7, hy - hr - 48)
    _facet_body(surf, [(cx - 18, hy - hr + 2), (cx + 18, hy - hr + 2), tip],
                (44, 74, 178), top_left_lift=55)
    pygame.draw.line(surf, (250, 230, 110),
                     (cx - 16, hy - hr - 5), (cx + 16, hy - hr - 5), 4)
    pygame.draw.circle(surf, (250, 240, 130), tip, 5)


def clown_auguste(surf, cx, feet_y, hand_up):
    """Classic Auguste: flesh face, big red ball nose, baggy mismatched suit,
    tiny derby, oversized bow tie. Chunky and beaming, offering the die."""
    hip_y = feet_y - 86
    _shoes(surf, cx, feet_y, 22, 40, (184, 62, 52))
    _legs(surf, cx, hip_y, feet_y, 15, 13, (92, 144, 212))
    _facet_body(surf, [(cx - 36, hip_y + 10), (cx + 36, hip_y + 10),
                       (cx + 23, hip_y - 50), (cx - 23, hip_y - 50)],
                (62, 122, 192))
    for s in (-1, 1):
        _poly(surf, (92, 184, 92),
              [(cx + s * 21, hip_y - 46), (cx + s * 5, hip_y - 46),
               (cx + s * 12, hip_y - 10)], oc=False)
    _pompoms(surf, cx, hip_y - 38, hip_y, (250, 230, 80), 3)
    _arm(surf, (cx - 28, hip_y - 44), (cx - 36, hip_y - 6), 9, (62, 122, 192))
    _arm(surf, (cx + 28, hip_y - 46), hand_up, 9, (62, 122, 192), up=True)
    neck_y = hip_y - 50
    for s in (-1, 1):
        _poly(surf, (240, 82, 72),
              [(cx, neck_y), (cx + s * 19, neck_y - 10),
               (cx + s * 19, neck_y + 10)])
    pygame.draw.circle(surf, (250, 230, 80), (cx, neck_y), 5)
    hr = 25
    hy = neck_y - hr - 2
    _round_head(surf, cx, hy, hr, (255, 207, 167))
    for s in (-1, 1):
        pygame.draw.ellipse(surf, WHITE, (cx + s * 11 - 7, hy - 11, 14, 13))
    _eyes(surf, cx, hy - 4, hr, style="dot")
    _nose(surf, cx, hy + 4, 9, (236, 44, 44))
    pygame.draw.ellipse(surf, WHITE, (cx - 14, hy + 10, 28, 14))
    _smile(surf, cx, hy + 12, 22, (210, 60, 70))
    pygame.draw.ellipse(surf, (72, 62, 62), (cx - 14, hy - hr - 1, 28, 7))
    pygame.draw.rect(surf, (72, 62, 62), (cx - 8, hy - hr - 12, 16, 12),
                     border_radius=3)
    pygame.draw.circle(surf, (240, 90, 80), (cx + 9, hy - hr - 7), 3)


def clown_strongman(surf, cx, feet_y, hand_up):
    """Circus STRONGMAN clown: barrel chest, striped singlet/leotard, handlebar
    moustache, tiny bowler, hoisting a comedic barbell in one hand while the
    other presents the die. Big bold silhouette, casual-friendly."""
    hip_y = feet_y - 84
    SKIN = (244, 188, 150)
    SUIT = (210, 70, 80)
    STRIPE = (250, 244, 232)
    _shoes(surf, cx, feet_y, 18, 32, (70, 60, 70))
    _legs(surf, cx, hip_y, feet_y, 16, 15, SKIN)
    # Barrel chest — a wide rounded torso, much broader than the others.
    body = [(cx - 38, hip_y + 6), (cx + 38, hip_y + 6),
            (cx + 30, hip_y - 58), (cx - 30, hip_y - 58)]
    _facet_body(surf, body, SUIT)
    # Bold vertical singlet stripe.
    pygame.draw.line(surf, STRIPE, (cx, hip_y - 56), (cx, hip_y + 4), 7)
    pygame.draw.line(surf, _shade(SUIT, -40), (cx + 5, hip_y - 56),
                     (cx + 5, hip_y + 4), 2)
    # Singlet straps over big rounded shoulders.
    for s in (-1, 1):
        pygame.draw.line(surf, SUIT, (cx + s * 22, hip_y - 56),
                         (cx + s * 10, hip_y - 40), 8)
    # Thick muscular arms. Left hoists a barbell overhead-ish; right offers die.
    bell_y = hip_y - 70
    _arm(surf, (cx - 28, hip_y - 50), (cx - 40, bell_y + 4), 12, SKIN,
         glove=SKIN)
    _arm(surf, (cx + 28, hip_y - 52), hand_up, 11, SKIN, glove=SKIN, up=True)
    # Comedic barbell in the left hand.
    bx = cx - 40
    pygame.draw.line(surf, (70, 72, 82), (bx - 16, bell_y), (bx + 16, bell_y), 5)
    for d in (-15, 15):
        pygame.draw.circle(surf, (54, 56, 66), (bx + d, bell_y), 11)
        pygame.draw.circle(surf, (92, 96, 108), (bx + d, bell_y), 9)
        pygame.draw.circle(surf, RIM, (bx + d - 3, bell_y - 3), 3)
    hr = 24
    hy = hip_y - 58 - hr + 8
    _round_head(surf, cx, hy, hr, SKIN)
    _eyes(surf, cx, hy - 3, hr, style="happy")
    # Big handlebar moustache.
    pygame.draw.arc(surf, (96, 60, 40), (cx - 14, hy + 4, 14, 11),
                    math.pi * 0.15, math.pi, 3)
    pygame.draw.arc(surf, (96, 60, 40), (cx, hy + 4, 14, 11), 0,
                    math.pi * 0.85, 3)
    pygame.draw.circle(surf, (96, 60, 40), (cx - 13, hy + 8), 2)
    pygame.draw.circle(surf, (96, 60, 40), (cx + 13, hy + 8), 2)
    _nose(surf, cx, hy + 3, 5, (230, 110, 110))
    _smile(surf, cx, hy + 12, 14, (180, 70, 70))
    # Tiny bowler perched on top.
    pygame.draw.ellipse(surf, (60, 52, 60), (cx - 13, hy - hr - 1, 26, 6))
    pygame.draw.rect(surf, (66, 58, 66), (cx - 8, hy - hr - 10, 16, 10),
                     border_radius=4)
    pygame.draw.circle(surf, (220, 70, 80), (cx + 7, hy - hr - 5), 2)


def clown_pierrot(surf, cx, feet_y, hand_up):
    """Soft, GENTLE Pierrot: loose ivory silk, black-button placket, skullcap,
    a single pale-blue teardrop. Warm not ghostly — still smiling softly while
    presenting the die."""
    hip_y = feet_y - 98
    SILK = (240, 240, 248)
    # Pale-on-pale vanished into the sky — paint a soft COOL-BLUE rim down the
    # whole left silhouette FIRST so the figure separates from the day sky.
    cool = (150, 192, 240)
    for pts in ([(cx - 36, hip_y + 14), (cx - 17, hip_y - 54)],):
        pygame.draw.line(surf, cool, pts[0], pts[1], 4)
    _shoes(surf, cx, feet_y, 15, 28, (236, 236, 242))
    _legs(surf, cx, hip_y, feet_y, 11, 13, (246, 246, 251))
    _facet_body(surf, [(cx - 36, hip_y + 14), (cx + 36, hip_y + 14),
                       (cx + 17, hip_y - 54), (cx - 17, hip_y - 54)],
                SILK, top_left_lift=18)
    pygame.draw.line(surf, cool, (cx - 35, hip_y + 12),
                     (cx - 16, hip_y - 52), 3)  # cool rim over the silk edge
    for i in range(3):
        by = hip_y - 40 + i * 16
        pygame.draw.circle(surf, (44, 44, 60), (cx, by), 5)
        pygame.draw.circle(surf, _shade((44, 44, 60), 60), (cx - 1, by - 1), 2)
    _arm(surf, (cx - 26, hip_y - 48), (cx - 34, hip_y - 8), 9, SILK,
         glove=(252, 252, 255))
    _arm(surf, (cx + 26, hip_y - 50), hand_up, 9, SILK,
         glove=(252, 252, 255), up=True)
    neck_y = hip_y - 54
    # One COLOURED accent: a soft cool-blue ruff (instead of pure white) plus a
    # blue chest pom so he isn't a colourless ghost.
    _ruff(surf, cx, neck_y, 24, (188, 214, 248), lobes=13)
    pygame.draw.circle(surf, (96, 150, 224), (cx, hip_y - 8), 6)
    pygame.draw.circle(surf, (150, 192, 240), (cx - 2, hip_y - 10), 2)
    hr = 23
    hy = neck_y - hr - 4
    _round_head(surf, cx, hy, hr, None, white_face=True, blush=True)
    # Cool-blue rim down the face's left edge so it reads against pale sky.
    pygame.draw.arc(surf, (150, 192, 240),
                    (cx - hr, hy - hr, hr * 2, hr * 2),
                    math.pi * 0.55, math.pi * 1.35, 2)
    _eyes(surf, cx, hy - 2, hr, style="sad")
    # Single pale teardrop — wistful, not creepy.
    pygame.draw.circle(surf, (120, 180, 235), (cx - 9, hy + 6), 2)
    pygame.draw.polygon(surf, (120, 180, 235),
                        [(cx - 10, hy + 3), (cx - 8, hy + 3), (cx - 9, hy + 7)])
    _nose(surf, cx, hy + 4, 5, (224, 130, 158))
    # Soft, faintly-upturned mouth so he reads sweet rather than mournful.
    pygame.draw.arc(surf, (180, 120, 140), (cx - 9, hy + 8, 18, 9),
                    math.pi * 1.08, math.tau * 0.95, 2)
    pygame.draw.ellipse(surf, (52, 52, 70), (cx - hr, hy - hr - 2, hr * 2, hr))
    pygame.draw.ellipse(surf, _shade((52, 52, 70), 40),
                        (cx - hr + 4, hy - hr, hr, hr // 2))


def clown_harlequin(surf, cx, feet_y, hand_up):
    """Mischievous Harlequin: tight diamond-patch motley, felt bicorne,
    half-mask. The benchmark — kept and scaled up, chunkier, presenting."""
    hip_y = feet_y - 96
    # Just TWO bold motley tones in a few LARGE diamonds — high value contrast,
    # with a lit top-left facet per diamond — instead of a busy fine grid.
    D_RED, D_GOLD = (208, 48, 70), (250, 198, 60)

    def _motley(rect):
        clip = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        step = rect.w // 2  # only ~2 columns of big diamonds
        for row in range(-1, rect.h // step + 2):
            for col in range(-1, rect.w // step + 2):
                dx = col * step + (step // 2 if row % 2 else 0)
                dy = row * step
                c = D_RED if (row + col) % 2 else D_GOLD
                pts = [(dx, dy - step // 2 - 2), (dx + step // 2 + 2, dy),
                       (dx, dy + step // 2 + 2), (dx - step // 2 - 2, dy)]
                pygame.draw.polygon(clip, _shade(c, -45), pts)
                pygame.draw.polygon(clip, c, [
                    (dx, dy - step // 2), (dx + step // 2, dy),
                    (dx, dy + step // 2), (dx - step // 2, dy)])
                # Lit top-left facet on each diamond for value pop.
                pygame.draw.polygon(clip, _shade(c, 55), [
                    (dx, dy - step // 2), (dx, dy), (dx - step // 2, dy)])
        return clip

    _shoes(surf, cx, feet_y, 16, 30, (42, 42, 58))
    _legs(surf, cx, hip_y, feet_y, 12, 12, (212, 52, 72), stripe=(250, 200, 62))
    body_rect = pygame.Rect(cx - 27, hip_y - 58, 54, 70)
    motley = _motley(body_rect)
    bmask = pygame.Surface(body_rect.size, pygame.SRCALPHA)
    _poly(bmask, (255, 255, 255),
          [(2, body_rect.h), (body_rect.w - 2, body_rect.h),
           (body_rect.w - 9, 0), (9, 0)], oc=False)
    motley.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(motley, body_rect.topleft)
    # Sculpt: top-left lit facet + underside shadow + left rim over the motley.
    lit = pygame.Surface(body_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(lit, (255, 255, 255, 60),
                        [(9, 0), (body_rect.w * 2 // 3, 0),
                         (2, body_rect.h * 2 // 3)])
    lit.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lit, body_rect.topleft)
    sh = pygame.Surface(body_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 50),
                     (0, body_rect.h * 2 // 3, body_rect.w, body_rect.h // 3))
    sh.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sh, body_rect.topleft)
    pygame.draw.polygon(surf, INK,
                        [(cx - 27, hip_y + 12), (cx + 27, hip_y + 12),
                         (cx + 18, hip_y - 58), (cx - 18, hip_y - 58)], 2)
    _arm(surf, (cx - 24, hip_y - 50), (cx - 32, hip_y - 8), 8, (212, 52, 72))
    _arm(surf, (cx + 24, hip_y - 52), hand_up, 8, (62, 142, 172), up=True)
    neck_y = hip_y - 58
    _ruff(surf, cx, neck_y, 20, (250, 245, 230), lobes=12)
    hr = 22
    hy = neck_y - hr - 2
    _round_head(surf, cx, hy, hr, (255, 211, 171))
    pygame.draw.ellipse(surf, (38, 38, 54), (cx - hr + 1, hy - 9, hr * 2 - 2, 15))
    for s in (-1, 1):
        pygame.draw.circle(surf, WHITE, (cx + s * 9, hy - 2), 4)
        pygame.draw.circle(surf, INK, (cx + s * 9 + s, hy - 1), 2)
        pygame.draw.circle(surf, WHITE, (cx + s * 9 - 1, hy - 3), 1)
    _nose(surf, cx, hy + 6, 6, (236, 92, 92))
    _smile(surf, cx, hy + 9, 18, (180, 70, 80))
    pygame.draw.polygon(surf, (92, 42, 112),
                        [(cx - 18, hy - hr + 3), (cx + 18, hy - hr + 3),
                         (cx + 9, hy - hr - 12), (cx - 9, hy - hr - 12)])
    pygame.draw.polygon(surf, _shade((92, 42, 112), 45),
                        [(cx - 18, hy - hr + 3), (cx - 4, hy - hr + 3),
                         (cx - 9, hy - hr - 12)])
    pygame.draw.polygon(surf, _shade((92, 42, 112), -55),
                        [(cx - 18, hy - hr + 3), (cx + 18, hy - hr + 3),
                         (cx + 9, hy - hr - 12), (cx - 9, hy - hr - 12)], 2)
    pygame.draw.line(surf, (250, 220, 90), (cx + 7, hy - hr - 10),
                     (cx + 18, hy - hr - 22), 3)


def clown_jester(surf, cx, feet_y, hand_up):
    """Court jester — clearly DIFFERENT from the Harlequin: a split two-tone
    body (left/right halves, NO diamonds), an exaggerated three-point belled
    cap, two-tone tights. Capering on one leg, presenting the die."""
    hip_y = feet_y - 92
    # Widen the value gap between the two halves — a DEEP plum vs a BRIGHT lime —
    # so the split reads crisply instead of muddying together.
    PURPLE, GREEN, GOLD = (86, 38, 138), (126, 214, 110), (250, 205, 72)
    _shoes(surf, cx, feet_y, 14, 26, (200, 62, 72), toe=(250, 210, 100))
    # Two-tone split tights.
    _leg(surf, (cx - 7, hip_y), (cx - 13, feet_y - 9), 12, PURPLE)
    _leg(surf, (cx + 7, hip_y), (cx + 13, feet_y - 9), 12, GREEN)
    # Split tunic — left purple half, right green half, NO diamond pattern.
    _facet_body(surf, [(cx - 28, hip_y + 10), (cx, hip_y + 10),
                       (cx, hip_y - 52), (cx - 18, hip_y - 52)], PURPLE)
    _facet_body(surf, [(cx, hip_y + 10), (cx + 28, hip_y + 10),
                       (cx + 18, hip_y - 52), (cx, hip_y - 52)], GREEN)
    # Crisp centre seam where the halves meet.
    pygame.draw.line(surf, (250, 248, 235), (cx, hip_y - 50), (cx, hip_y + 8), 2)
    for i in range(7):
        bx = cx - 21 + i * 7
        pygame.draw.circle(surf, GOLD, (bx, hip_y + 6), 3)
    # Arms swap the two-tone colours for a motley flourish.
    _arm(surf, (cx - 25, hip_y - 46), (cx - 33, hip_y - 6), 8, GREEN)
    _arm(surf, (cx + 25, hip_y - 48), hand_up, 8, PURPLE, up=True)
    neck_y = hip_y - 52
    for s in (-1, 0, 1):
        tx = cx + s * 15
        _poly(surf, GOLD, [(cx, neck_y), (tx - 6, neck_y + 16),
                           (tx + 6, neck_y + 16)], oc=_shade(GOLD, -60))
        pygame.draw.circle(surf, (240, 235, 200), (tx, neck_y + 17), 3)
    hr = 22
    hy = neck_y - hr
    _round_head(surf, cx, hy, hr, (255, 209, 169))
    _eyes(surf, cx, hy - 2, hr, style="happy")
    _nose(surf, cx, hy + 5, 6, (232, 72, 72))
    _smile(surf, cx, hy + 11, 18, (195, 60, 70))
    # Exaggerated three-point belled fool's cap, drooping points + big bells.
    pts = [(-1, PURPLE, -26, -30), (0, GOLD, 0, -38), (1, GREEN, 26, -30)]
    for s, col, dx, dy in pts:
        bx = cx + dx
        by = hy - hr + dy
        _poly(surf, col, [(cx - 16, hy - hr + 2), (cx + 16, hy - hr + 2),
                          (bx, by)], oc=_shade(col, -55))
        pygame.draw.circle(surf, (245, 240, 200), (bx, by), 4)
        pygame.draw.circle(surf, _shade((245, 240, 200), -50), (bx, by), 4, 1)


def clown_ringmaster(surf, cx, feet_y, hand_up):
    """Circus-host showman: top hat, red tailcoat with GOLD FROGGING +
    epaulets, big bow tie, white jodhpurs. Gestures a cane/whistle toward the
    die — pushed showman confidence."""
    hip_y = feet_y - 92
    RED, GOLD = (192, 42, 52), (242, 202, 92)
    _shoes(surf, cx, feet_y, 15, 28, (36, 33, 42))
    _legs(surf, cx, hip_y, feet_y, 13, 13, (246, 241, 236))
    _facet_body(surf, [(cx - 28, hip_y + 6), (cx + 28, hip_y + 6),
                       (cx + 20, hip_y - 56), (cx - 20, hip_y - 56)], RED)
    # Long pointed TAILCOAT tails sweeping down behind the legs — committed hard
    # so the silhouette is unmistakably a tailcoat, not a generic tunic.
    for s in (-1, 1):
        _poly(surf, _shade(RED, -30),
              [(cx + s * 6, hip_y + 2), (cx + s * 26, hip_y + 6),
               (cx + s * 16, hip_y + 40), (cx + s * 7, hip_y + 24)])
        pygame.draw.line(surf, GOLD, (cx + s * 24, hip_y + 8),
                         (cx + s * 15, hip_y + 36), 1)
    # White waistcoat V.
    _poly(surf, (245, 240, 232),
          [(cx - 10, hip_y - 50), (cx + 10, hip_y - 50), (cx, hip_y - 10)],
          oc=_shade((245, 240, 232), -50))
    # Bright diagonal SASH across the chest — the showman read at a glance.
    SASH = (236, 196, 70)
    _poly(surf, SASH,
          [(cx - 22, hip_y - 50), (cx - 14, hip_y - 52),
           (cx + 22, hip_y + 4), (cx + 14, hip_y + 6)],
          oc=_shade(SASH, -55))
    pygame.draw.line(surf, _shade(SASH, 70), (cx - 20, hip_y - 50),
                     (cx + 18, hip_y + 4), 1)
    # Gold frogging — horizontal braid rungs across the chest, over the sash.
    for i in range(4):
        ry = hip_y - 44 + i * 11
        pygame.draw.line(surf, GOLD, (cx - 11, ry), (cx + 11, ry), 3)
        for s in (-1, 1):
            pygame.draw.circle(surf, GOLD, (cx + s * 11, ry), 3)
    # Gold epaulets on the shoulders.
    for s in (-1, 1):
        pygame.draw.ellipse(surf, GOLD, (cx + s * 24 - 7, hip_y - 52, 14, 9))
        for fr in range(3):
            pygame.draw.line(surf, _shade(GOLD, -40),
                             (cx + s * 24 - 4 + fr * 3, hip_y - 44),
                             (cx + s * 24 - 5 + fr * 3, hip_y - 38), 2)
    # Left hand holds a cane; right presents toward the die with a whistle.
    _arm(surf, (cx - 26, hip_y - 48), (cx - 36, hip_y - 4), 9, RED)
    pygame.draw.line(surf, (230, 220, 200), (cx - 36, hip_y - 4),
                     (cx - 40, feet_y - 12), 3)
    pygame.draw.circle(surf, GOLD, (cx - 36, hip_y - 8), 3)
    _arm(surf, (cx + 26, hip_y - 50), hand_up, 9, RED, up=True)
    neck_y = hip_y - 54
    for s in (-1, 1):
        _poly(surf, GOLD, [(cx, neck_y), (cx + s * 15, neck_y - 9),
                           (cx + s * 15, neck_y + 9)])
    pygame.draw.circle(surf, _shade(GOLD, -50), (cx, neck_y), 3)
    hr = 22
    hy = neck_y - hr
    _round_head(surf, cx, hy, hr, (255, 207, 167))
    _eyes(surf, cx, hy - 2, hr, style="happy")
    pygame.draw.arc(surf, (92, 62, 42), (cx - 11, hy + 4, 11, 8), 0, math.pi, 3)
    pygame.draw.arc(surf, (92, 62, 42), (cx, hy + 4, 11, 8), 0, math.pi, 3)
    _nose(surf, cx, hy + 3, 5, (226, 112, 112))
    _smile(surf, cx, hy + 12, 14, (180, 70, 70))
    # Tall TOP HAT with a wide brim + red hatband — commits the showman read.
    pygame.draw.ellipse(surf, (26, 24, 32), (cx - 22, hy - hr - 1, 44, 10))
    pygame.draw.rect(surf, (36, 33, 44), (cx - 14, hy - hr - 36, 28, 36),
                     border_radius=3)
    pygame.draw.ellipse(surf, (44, 40, 52), (cx - 14, hy - hr - 39, 28, 8))
    pygame.draw.rect(surf, RED, (cx - 14, hy - hr - 12, 28, 7))
    pygame.draw.circle(surf, GOLD, (cx + 9, hy - hr - 9), 2)
    pygame.draw.rect(surf, _shade((36, 33, 44), 50),
                     (cx - 11, hy - hr - 33, 5, 27))


def clown_mascot(surf, cx, feet_y, hand_up):
    """Max casual-cute mascot — the FRIENDLINESS NORTH STAR: round chibi build,
    huge sparkly eyes, rosy cheeks. One stubby hand holds a balloon, the other
    reaches up to offer the die."""
    hip_y = feet_y - 70
    BODY = (98, 188, 222)
    _shoes(surf, cx, feet_y, 14, 26, (250, 210, 92))
    for s in (-1, 1):
        _leg(surf, (cx + s * 7, hip_y + 4), (cx + s * 10, feet_y - 9), 13, BODY)
    # Big round chibi belly-body.
    pygame.draw.circle(surf, _shade(BODY, -55), (cx, hip_y - 18), 34)
    pygame.draw.circle(surf, BODY, (cx, hip_y - 18), 32)
    pygame.draw.circle(surf, RIM, (cx - 12, hip_y - 30), 8)
    pygame.draw.ellipse(surf, (245, 250, 252), (cx - 16, hip_y - 24, 32, 30))
    _pompoms(surf, cx, hip_y - 32, hip_y, (240, 100, 110), 3)
    # Left stubby arm holds a balloon string; right offers the die.
    _arm(surf, (cx - 26, hip_y - 26), (cx - 38, hip_y - 40), 10, BODY,
         glove=BODY)
    pygame.draw.line(surf, (230, 230, 235), (cx - 38, hip_y - 40),
                     (cx - 44, hip_y - 96), 2)
    _outline_ellipse(surf, (236, 82, 96), (cx - 56, hip_y - 122, 26, 30),
                     oc=_shade((236, 82, 96), -55))
    pygame.draw.ellipse(surf, (255, 182, 188), (cx - 50, hip_y - 116, 8, 10))
    _arm(surf, (cx + 26, hip_y - 26), hand_up, 10, BODY, glove=BODY, up=True)
    hr = 27
    hy = hip_y - 50 - hr + 10
    _round_head(surf, cx, hy, hr, (255, 224, 192))
    _eyes(surf, cx, hy - 1, hr, style="dot")
    # Extra-big sparkly pupils for max cute.
    for s in (-1, 1):
        pygame.draw.circle(surf, WHITE, (cx + s * 11, hy - 1), 6)
        pygame.draw.circle(surf, (50, 45, 65), (cx + s * 11, hy + 1), 4)
        pygame.draw.circle(surf, WHITE, (cx + s * 11 - 2, hy - 3), 2)
    _nose(surf, cx, hy + 7, 5, (242, 122, 122))
    _smile(surf, cx, hy + 13, 18, (210, 90, 100))
    _poly(surf, (250, 200, 82),
          [(cx - 10, hy - hr + 3), (cx + 10, hy - hr + 3), (cx, hy - hr - 18)])
    pygame.draw.circle(surf, (240, 100, 110), (cx, hy - hr - 18), 3)


def clown_rainbow(surf, cx, feet_y, hand_up):
    """Classic party clown — DE-NOISED: ONE dominant blue body, rainbow only in
    the wig + ruff, face on a clean light field so the big grin survives. Huge
    floppy shoes, presenting the die."""
    hip_y = feet_y - 86
    BODY = (58, 112, 212)
    _shoes(surf, cx, feet_y, 24, 46, (222, 42, 52), toe=(250, 220, 92))
    _legs(surf, cx, hip_y, feet_y, 16, 14, (60, 112, 212))
    _facet_body(surf, [(cx - 34, hip_y + 10), (cx + 34, hip_y + 10),
                       (cx + 21, hip_y - 54), (cx - 21, hip_y - 54)], BODY)
    # White placket panel keeps the buttons + face field clean.
    _poly(surf, (244, 246, 250),
          [(cx - 9, hip_y - 52), (cx + 9, hip_y - 52),
           (cx + 7, hip_y + 6), (cx - 7, hip_y + 6)],
          oc=_shade((244, 246, 250), -45))
    # Rainbow lives in the trim, not the body: bright POM-POM buttons run the
    # full spectrum down the placket.
    RAINBOW = [(232, 52, 62), (245, 150, 60), (250, 212, 72),
               (92, 192, 102), (72, 140, 224), (150, 86, 200)]
    for i in range(4):
        c = RAINBOW[i]
        by = hip_y - 44 + i * 16
        pygame.draw.circle(surf, _shade(c, -50), (cx, by), 6)
        pygame.draw.circle(surf, c, (cx, by), 5)
        pygame.draw.circle(surf, _shade(c, 90), (cx - 2, by - 2), 2)
    _arm(surf, (cx - 28, hip_y - 48), (cx - 38, hip_y - 6), 9, BODY)
    _arm(surf, (cx + 28, hip_y - 50), hand_up, 9, BODY, up=True)
    # Rainbow CUFFS at both wrists — bright spectrum rings on the gloves.
    for s, (hx, hy0) in ((-1, (cx - 38, hip_y - 6)), (1, hand_up)):
        for j, rc in enumerate(RAINBOW[:3]):
            pygame.draw.circle(surf, rc, (hx, hy0 + 7 + j * 2), 9 - j, 2)
    neck_y = hip_y - 54
    # Rainbow RUFF — alternating spectrum scallops earn the "Rainbow" name while
    # the body stays one dominant blue and the face sits on a clean field.
    for i in range(12):
        a = i * math.tau / 12
        lx = cx + math.cos(a) * 25
        ly = neck_y + math.sin(a) * 12.5
        rc = RAINBOW[i % len(RAINBOW)]
        pygame.draw.circle(surf, _shade(rc, -50), (int(lx), int(ly)), 8)
        pygame.draw.circle(surf, rc, (int(lx), int(ly)), 7)
        pygame.draw.circle(surf, _shade(rc, 60),
                           (int(lx) - 2, int(ly) - 2), 2)
    pygame.draw.circle(surf, (244, 246, 250), (cx, neck_y), 12)
    pygame.draw.circle(surf, _shade((244, 246, 250), -35), (cx, neck_y), 12, 1)
    hr = 23
    hy = neck_y - hr - 6
    _round_head(surf, cx, hy, hr, (255, 228, 202))
    # Rainbow wig — fluffy tufts flanking a clean pate (rainbow lives HERE).
    wig = [(220, 62, 62), (245, 152, 62), (250, 216, 72),
           (92, 182, 102), (72, 132, 222)]
    for s in (-1, 1):
        for j, wc in enumerate(wig):
            wx = cx + s * (hr + 2 + j * 3)
            wy = hy - 4 + (j - 2) * 5
            pygame.draw.circle(surf, _shade(wc, -40), (wx, wy), 7)
            pygame.draw.circle(surf, wc, (wx, wy), 6)
            pygame.draw.circle(surf, _shade(wc, 60), (wx - 2, wy - 2), 2)
    _eyes(surf, cx, hy - 2, hr, style="happy")
    for s in (-1, 1):
        pygame.draw.arc(surf, (210, 62, 72),
                        (cx + s * 10 - 6, hy - 11, 12, 8), 0, math.pi, 2)
    _nose(surf, cx, hy + 4, 9, (236, 46, 46))
    pygame.draw.ellipse(surf, WHITE, (cx - 14, hy + 10, 28, 14))
    _smile(surf, cx, hy + 12, 22, (215, 55, 65))


def clown_windup(surf, cx, feet_y, hand_up):
    """Quirky wind-up tin clown — kept & scaled: riveted panels, wind key,
    antenna-ball, painted smile. Added a WARM red/gold accent + a strong
    LEFT RIM LIGHT so the cool metal lifts off the blue sky. Presenting the die."""
    hip_y = feet_y - 84
    TIN = (158, 182, 202)
    TIN_D = (98, 124, 150)
    TIN_L = (212, 226, 240)
    RED, GOLD = (214, 74, 74), (238, 202, 92)
    _shoes(surf, cx, feet_y, 15, 28, TIN_D, toe=(196, 210, 224))
    for s in (-1, 1):
        _leg(surf, (cx + s * 8, hip_y + 2), (cx + s * 11, feet_y - 9), 12, TIN)
    # Boxy riveted torso panel with a strong left rim.
    body = pygame.Rect(cx - 26, hip_y - 54, 52, 64)
    pygame.draw.rect(surf, TIN, body, border_radius=7)
    pygame.draw.rect(surf, _shade(TIN, 30),
                     (body.x + 4, body.y + 4, 11, body.h - 8), border_radius=5)
    pygame.draw.line(surf, TIN_L, (body.left + 1, body.top + 7),
                     (body.left + 1, body.bottom - 7), 3)  # left rim light
    pygame.draw.rect(surf, TIN_D, body, 2, border_radius=7)
    for fx, fy in ((0.12, 0.1), (0.88, 0.1), (0.12, 0.9), (0.88, 0.9),
                   (0.5, 0.1), (0.5, 0.9)):
        rx = body.x + int(fx * body.w)
        ry = body.y + int(fy * body.h)
        pygame.draw.circle(surf, TIN_D, (rx, ry), 2)
        pygame.draw.circle(surf, _shade(TIN, 60), (rx - 1, ry - 1), 1)
    # Warm painted chest gear-button + dial (the warm accent).
    pygame.draw.circle(surf, RED, (cx, hip_y - 22), 9)
    pygame.draw.circle(surf, _shade(RED, -60), (cx, hip_y - 22), 9, 2)
    pygame.draw.circle(surf, GOLD, (cx, hip_y - 22), 3)
    pygame.draw.circle(surf, RIM, (cx - 3, hip_y - 25), 2)
    # Wind-up key on the side.
    pygame.draw.line(surf, GOLD, (cx + 26, hip_y - 30), (cx + 38, hip_y - 30), 3)
    pygame.draw.circle(surf, GOLD, (cx + 40, hip_y - 30), 6, 2)
    pygame.draw.circle(surf, GOLD, (cx + 35, hip_y - 30), 6, 2)
    _arm(surf, (cx - 24, hip_y - 48), (cx - 34, hip_y - 8), 9, TIN,
         glove=(220, 232, 244))
    _arm(surf, (cx + 24, hip_y - 50), hand_up, 9, TIN,
         glove=(220, 232, 244), up=True)
    neck_y = hip_y - 54
    pygame.draw.rect(surf, TIN_D, (cx - 6, neck_y - 2, 12, 7))
    hr = 22
    hy = neck_y - hr - 2
    pygame.draw.circle(surf, _shade(TIN, 18), (cx, hy), hr)
    pygame.draw.circle(surf, TIN_L, (cx - hr // 2, hy - hr // 2), hr // 3)
    pygame.draw.circle(surf, TIN_D, (cx, hy), hr, 2)
    pygame.draw.line(surf, TIN_L, (cx - hr + 2, hy - hr // 2),
                     (cx - hr + 2, hy + hr // 2), 2)  # face left rim
    for s in (-1, 1):
        pygame.draw.circle(surf, (42, 48, 64), (cx + s * 8, hy - 2), 3)
        pygame.draw.circle(surf, WHITE, (cx + s * 8 - 1, hy - 3), 1)
        pygame.draw.circle(surf, (242, 132, 132), (cx + s * 12, hy + 5), 3)
    _nose(surf, cx, hy + 3, 5, RED)
    pygame.draw.arc(surf, (62, 68, 84), (cx - 9, hy + 5, 18, 10),
                    math.pi * 1.05, math.tau * 0.97, 2)
    pygame.draw.line(surf, TIN_D, (cx, hy - hr), (cx, hy - hr - 11), 2)
    pygame.draw.circle(surf, RED, (cx, hy - hr - 13), 5)
    pygame.draw.circle(surf, RIM, (cx - 2, hy - hr - 15), 1)


CLOWNS = [
    ("Whiteface", clown_whiteface),
    ("Auguste", clown_auguste),
    ("Strongman", clown_strongman),
    ("Pierrot", clown_pierrot),
    ("Harlequin", clown_harlequin),
    ("Court Jester", clown_jester),
    ("Ringmaster", clown_ringmaster),
    ("Cute Mascot", clown_mascot),
    ("Rainbow Party", clown_rainbow),
    ("Wind-up Tin", clown_windup),
]


# ── per-cell gameplay scene ──────────────────────────────────────────────────

def render_cell(draw_clown, idx, show_inset):
    """One TIGHTLY-CROPPED gameplay scene at SS supersample: just enough day sky
    to read 'clearing' + a sliver of grass + cast shadow, the chunky clown
    filling ~70-80% of the cell, the head-sized power-up die in the upper-centre
    focal slot, and the real parrot flying in for scale. Returns VIEW_W x VIEW_H."""
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * SS, VIEW_H * SS
    big = pygame.Surface((bw, bh))

    # Tight sky/ground crop: horizon sits just below the feet so the clown
    # dominates. Sky gradient samples the lower (brighter) end of the day sky so
    # the crop still reads as an open daytime clearing.
    g_y = int(VIEW_FEET_Y * SS) + 6 * SS
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)  # lower sky band = brighter clearing air
        c = lerp_color(palette['sky_mid'], palette['sky_bot'], t)
        pygame.draw.line(big, c, (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        c = lerp_color(palette['ground_top'], palette['ground_mid'], t)
        pygame.draw.line(big, c, (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    # A low soft hill band + a few grass tufts so the strip of ground reads as
    # an open clearing, not a flat bar.
    hill = pygame.Surface((bw, 30 * SS), pygame.SRCALPHA)
    hc = _shade(palette['ground_mid'], 22)
    for hx, hw, hh in ((40, 90, 18), (130, 110, 22), (185, 80, 16)):
        pygame.draw.ellipse(hill, (*hc, 160),
                            ((hx - hw) * SS, 0, hw * 2 * SS, hh * 2 * SS))
    big.blit(hill, (0, g_y - 14 * SS))
    tuft = _shade(palette['ground_top'], 22)
    rng = __import__('random').Random(idx * 131 + 7)
    for _ in range(10):
        tx = rng.randint(8, VIEW_W - 8) * SS
        ty = g_y + rng.randint(3, max(4, bh // SS - VIEW_FEET_Y - 4)) * SS
        for k in (-3, 0, 3):
            pygame.draw.line(big, tuft, (tx + k * SS, ty),
                             (tx + k * SS, ty - rng.randint(4, 7) * SS),
                             max(1, SS))

    # Figure + die + parrot on a 1x logical layer (simple coords), blitted up.
    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    # Figure nudged LEFT of centre so the die has clear sky in the upper-right
    # to float in, fully off the head silhouette.
    clown_cx = VIEW_W // 2 - 12
    feet_y = VIEW_FEET_Y
    _shadow(layer, clown_cx, feet_y, 96)

    # The die floats in the clear UPPER-RIGHT corner — well above and to the
    # side of every clown's head — so it reads as a separate takeable pickup,
    # never an occluding "dice head". The raised presenting hand reaches up
    # toward it from below-left (the clown-side base of the die).
    die_x = clown_cx + 66
    die_base_y = 46
    hand_up = (die_x - 26, die_base_y + 32)
    draw_clown(layer, clown_cx, feet_y, hand_up)

    pulse = idx * 1.7 + 2.0
    # Boost the gold halo for the pale Pierrot so the die pops off the sky.
    halo = 70 if idx == 3 else 0
    draw_floating_die(layer, die_x, die_base_y, pulse, show_inset=show_inset,
                      halo_boost=halo)

    # Real parrot flying in low from the left for scale/context — kept clear of
    # both the figure and the upper-right die.
    bird = get_parrot(1, 10)
    bird = pygame.transform.smoothscale(
        bird, (int(bird.get_width() * 0.92), int(bird.get_height() * 0.92)))
    layer.blit(bird, (22 - bird.get_width() // 2,
                      (feet_y - 64) - bird.get_height() // 2))

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    cols, rows = 5, 2
    # Look-dev sheet (docs only, never bundled) — render BIG (~2x round 2, cells
    # ~376px wide) so faceting, rim light and blush actually read. The source
    # viewport is supersampled then displayed at this larger size.
    sw, sh = int(VIEW_W * 1.88), int(VIEW_H * 1.88)

    PAD = 44
    GAP = 22
    TITLE_H = 92
    CAP_H = 40
    # Footer band carries the 1x in-game-scale legibility inset.
    FOOT_H = VIEW_H + 28

    canvas_w = PAD * 2 + cols * sw + (cols - 1) * GAP
    canvas_h = (PAD * 2 + TITLE_H + rows * (sh + CAP_H) + (rows - 1) * GAP
                + FOOT_H)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((24, 22, 30))

    f_title = pygame.font.SysFont(None, 70, bold=True)
    f_sub = pygame.font.SysFont(None, 34, bold=True)
    f_cap = pygame.font.SysFont(None, 40, bold=True)

    title = f_title.render("DICE CLOWN — pre-warren designs", True,
                           (250, 240, 210))
    canvas.blit(title, (PAD, PAD - 2))
    sub = f_sub.render(
        "clearing before the Pagoda Warren · the clown OFFERS the die (a "
        "takeable pickup, off the face) · take it to roll the route length",
        True, (190, 195, 205))
    canvas.blit(sub, (PAD, PAD + 50))

    # Show the rolled-result INSET in a couple of cells (Auguste, Cute Mascot)
    # to hint the route-length mechanic; the hero die stays pips everywhere.
    inset_cells = {1, 7}

    y0 = PAD + TITLE_H
    mascot_cell = None
    for i, (name, fn) in enumerate(CLOWNS):
        r, c = divmod(i, cols)
        cx = PAD + c * (sw + GAP)
        cy = y0 + r * (sh + CAP_H + GAP)
        cell = render_cell(fn, i, show_inset=(i in inset_cells))
        if i == 7:  # Cute Mascot — the placement template; keep at 1x for inset.
            mascot_cell = cell
        scaled = pygame.transform.smoothscale(cell, (sw, sh))
        pygame.draw.rect(canvas, (70, 76, 96),
                         pygame.Rect(cx - 1, cy - 1, sw + 2, sh + 2), 1)
        canvas.blit(scaled, (cx, cy))
        cap = f_cap.render(f"{i + 1}. {name}", True, (235, 225, 165))
        canvas.blit(cap, (cx + (sw - cap.get_width()) // 2, cy + sh + 6))

    # ONE 1x legibility inset proving the design still reads at in-game scale:
    # the Cute Mascot cell at its native VIEW_W x VIEW_H, in the footer band.
    if mascot_cell is not None:
        foot_y = y0 + rows * (sh + CAP_H) + (rows - 1) * GAP + 14
        ix = PAD
        pygame.draw.rect(canvas, (70, 76, 96),
                         pygame.Rect(ix - 2, foot_y - 2, VIEW_W + 4,
                                     VIEW_H + 4), 1)
        canvas.blit(mascot_cell, (ix, foot_y))
        tag = f_cap.render(
            "1x in-game scale (Cute Mascot) — die stays a clear takeable "
            "pickup, fully off the face", True, (200, 206, 216))
        canvas.blit(tag, (ix + VIEW_W + 24, foot_y + VIEW_H // 2 - 14))

    out_dir = os.path.join("docs", "clown_dice")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
