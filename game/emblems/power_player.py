"""Bespoke engraved center glyphs for the POWER PLAYER (gold) achievements.

These supersede the shared ``_glyph_powerup``/``_glyph_magnet``/``_glyph_kfc``
fallbacks so each medal's silhouette depicts THAT achievement's nature while
staying a struck-metal sibling of the rest of the family: bold filled polygons,
thick lines and discs authored in the passed ``col`` (the builder strokes a
dark inset down-right + lit body + up-left sheen for the engrave relief), and
saturated accents (KFC red, magnet poles) routed through ``_accent`` so a
dormant medal stays bronze-monochrome. Nothing here drops below ~5px detail.

Seven distinct silhouettes per the v2 LOCKED spec — anchor-sparkle, plate ring,
magnet, binder grid, fanned bucket, biting mouth, sparkle-vortex — so no two
read alike at the ~22px engrave size.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai


def _sparkle_pts(cx, cy, r, waist=0.26, reach=0.78):
    # The franchise four-point sparkle, parameterised so the family's anchor,
    # the bitten one and the vortex motes all share one star body.
    return [
        (cx, cy - r * reach), (cx + r * waist, cy - r * waist),
        (cx + r * reach, cy), (cx + r * waist, cy + r * waist),
        (cx, cy + r * reach), (cx - r * waist, cy + r * waist),
        (cx - r * reach, cy), (cx - r * waist, cy - r * waist),
    ]


# ── first_powerup — Power Up! ────────────────────────────────────────────────
def _glyph_first_powerup(surf, cx, cy, r, col):
    # The canonical four-point sparkle (the category anchor) with a small
    # up-chevron notched into its lower point — "your first power-up."
    star = _sparkle_pts(cx, cy - r * 0.06, r * 0.92)
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in star])
    # Up-arrow tucked under the sparkle's lower point so the read is "rising".
    w = max(3, int(r * 0.22))
    tip = (cx, int(cy + r * 0.30))
    pygame.draw.lines(surf, col, False, [
        (cx - int(r * 0.34), cy + int(r * 0.72)), tip,
        (cx + int(r * 0.34), cy + int(r * 0.72)),
    ], w)


# ── powerup_sampler — Buffet ─────────────────────────────────────────────────
def _glyph_sampler(surf, cx, cy, r, col):
    # A thin plate ring carrying FOUR IDENTICAL filled dots evenly spaced on it
    # — quantity-on-a-container, not shape variety (distinct morsels die at row
    # size). The ring keeps it a plate, not a magnet horseshoe.
    # Thin plate ring kept smaller, with four FAT dots ringed fully OUTSIDE it
    # and detached — so at 44px the read is four discrete blobs (count carries
    # it), not a single hollow diamond fused to the outline.
    ring_r = int(r * 0.52)
    pygame.draw.circle(surf, col, (cx, cy), ring_r, max(3, int(r * 0.11)))
    dot_r = max(5, int(r * 0.28))
    dot_orbit = ring_r + dot_r + max(2, int(r * 0.12))   # clear gap to the ring
    for i in range(4):
        a = -math.pi / 2 + i * math.pi / 2     # top, right, bottom, left
        dx = cx + int(math.cos(a) * dot_orbit)
        dy = cy + int(math.sin(a) * dot_orbit)
        pygame.draw.circle(surf, col, (dx, dy), dot_r)


# ── magnet_life — Animal Magnetism ───────────────────────────────────────────
def _glyph_magnet_life(surf, cx, cy, r, col):
    # A DOMINANT horseshoe magnet (poles DOWN) with banded red/steel pole-tips,
    # pulling ONE $ coin toward it on a single attraction-arc tick — "magnetism,
    # 15x". Pared to three elements so the horseshoe silhouette owns the glyph at
    # 44px. Red/steel poles via _accent (unlock-only).
    mx = cx - int(r * 0.10)
    my = cy - int(r * 0.22)
    rr = int(r * 0.46)
    leg_w = max(6, int(r * 0.30))
    bar = max(6, int(r * 0.32))
    top = my - int(r * 0.40)
    arc_rect = pygame.Rect(mx - rr, top, rr * 2, rr * 2)
    pygame.draw.arc(surf, col, arc_rect, math.radians(6), math.radians(174), bar)
    leg_top = top + rr
    leg_h = int(r * 0.50)
    for sgn in (-1, 1):
        lx = mx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, col, (lx, leg_top, leg_w, leg_h))
    tip_h = max(4, int(r * 0.20))
    for sgn, tip in ((-1, ai._accent((212, 64, 56))), (1, ai._accent((224, 228, 240)))):
        lx = mx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, tip, (lx, leg_top + leg_h, leg_w, tip_h))
    pole_y = leg_top + leg_h + tip_h
    # ONE $ coin being yanked toward the poles, parked just below-right.
    coin_x = cx + int(r * 0.50)
    coin_y = cy + int(r * 0.60)
    coin_r = int(r * 0.30)
    pygame.draw.circle(surf, col, (coin_x, coin_y), coin_r, max(2, int(r * 0.10)))
    f = ai._glyph_font(int(coin_r * 2.0))
    g = f.render("$", True, col)
    surf.blit(g, g.get_rect(center=(coin_x, coin_y)))
    # A SINGLE attraction-arc tick spanning the gap between the poles and coin.
    ax = mx - int(r * 0.20)
    pygame.draw.arc(surf, col, (ax, pole_y + int(r * 0.02),
                                int(r * 0.70), int(r * 0.50)),
                    math.radians(196), math.radians(330), max(3, int(r * 0.11)))


# ── powerup_collector — Gotta Grab 'Em All ───────────────────────────────────
def _glyph_collector(surf, cx, cy, r, col):
    # A rounded "binder" rectangle holding a 3x3 grid of IDENTICAL filled dots —
    # grid completeness (a full container of same dots), not pip variety. The
    # rectangular frame separates it from Buffet's plate RING.
    bw, bh = int(r * 1.56), int(r * 1.56)
    rect = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)
    pygame.draw.rect(surf, col, rect, max(3, int(r * 0.13)),
                     border_radius=max(2, int(r * 0.16)))
    dot_r = max(4, int(r * 0.16))
    span = r * 0.50          # grid pitch
    for gy in (-1, 0, 1):
        for gx in (-1, 0, 1):
            pygame.draw.circle(surf, col,
                               (cx + int(gx * span), cy + int(gy * span)), dot_r)


# ── greasy_fingers — Finger Lickin' ──────────────────────────────────────────
def _glyph_greasy(surf, cx, cy, r, col):
    # An UPRIGHT, symmetrical striped KFC bucket with THREE bold WEDGE-shaped
    # fries splayed above its dead-vertical rim — the upright stance is the whole
    # contrast with the Shame kfc_incident's tipped/spilled bucket. Red tub
    # accent via _accent (unlock-only).
    rim_y = int(cy - r * 0.02)
    # Three fat tapered fry wedges (wider at the splayed top, narrow where they
    # plant in the bucket), drawn FIRST so the rim overlaps their feet.
    base_x = cx
    base_y = rim_y + int(r * 0.06)
    half = max(3, int(r * 0.12))                 # fry half-width at the foot
    top_half = max(4, int(r * 0.17))             # fry half-width at the tip
    for ang in (-34, 0, 34):
        a = math.radians(ang - 90)               # splay up and out
        nx, ny = math.cos(a), math.sin(a)
        px, py = -ny, nx                         # across-fry normal
        fx = base_x + int(nx * 0)                # all rooted at the same foot row
        foot = (base_x, base_y)
        tip = (base_x + nx * r * 0.92, base_y + ny * r * 0.92)
        wedge = [
            (foot[0] + px * half,  foot[1] + py * half),
            (foot[0] - px * half,  foot[1] - py * half),
            (tip[0] - px * top_half, tip[1] - py * top_half),
            (tip[0] + px * top_half, tip[1] + py * top_half),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in wedge])
    # Dead-vertical, symmetrical bucket: a slightly tapered tub with a flat,
    # level rim cap — upright, never tilted.
    rim = [(cx - r * 0.54, rim_y - int(r * 0.10)),
           (cx + r * 0.54, rim_y - int(r * 0.10)),
           (cx + r * 0.54, rim_y + int(r * 0.06)),
           (cx - r * 0.54, rim_y + int(r * 0.06))]
    tub = [(cx - r * 0.50, rim_y + int(r * 0.06)),
           (cx + r * 0.50, rim_y + int(r * 0.06)),
           (cx + r * 0.38, cy + int(r * 0.78)),
           (cx - r * 0.38, cy + int(r * 0.78))]
    for poly in (tub, rim):
        pygame.draw.polygon(surf, ai._accent((214, 74, 60)),
                            [(int(x), int(y)) for x, y in poly])
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in poly],
                            max(2, int(r * 0.09)))
    # Two symmetric vertical bucket stripes so it reads as the striped tub.
    for dx in (-0.18, 0.18):
        x = int(cx + dx * r)
        pygame.draw.line(surf, col, (x, rim_y + int(r * 0.10)),
                         (x, int(cy + r * 0.70)), max(2, int(r * 0.08)))


# ── power_hungry / power_addict — appetite grows (shared helper) ─────────────
def _appetite(surf, cx, cy, r, col, stage):
    """One motif escalated by appetite: stage 0 (hungry) = an open jaw biting a
    single four-point sparkle with one bite-notch; stage 1 (addict) = a vortex
    of sparkles spiralling into a central one — one bite becomes a whirlpool."""
    if stage == 0:
        # A bold open maw (a filled Pac-Man-style jaw with a wedge bite missing)
        # CHOMPING a four-point sparkle wedged in its gape. The solid round jaw
        # reads as a mouth at row size where thin lip-arcs do not.
        jx, jy = cx - int(r * 0.20), cy + int(r * 0.04)
        jr = int(r * 0.74)
        # Filled disc, then the open wedge cut out (toward the upper-right, where
        # the sparkle sits) in the inset-shadow tone so the gape reads as a mouth.
        pygame.draw.circle(surf, col, (jx, jy), jr)
        gape = []
        a_lo, a_hi = math.radians(-44), math.radians(20)   # mouth opening, up-right
        gape.append((jx, jy))
        for i in range(9):
            a = a_lo + (a_hi - a_lo) * i / 8
            gape.append((jx + math.cos(a) * jr * 1.15, jy + math.sin(a) * jr * 1.15))
        pygame.draw.polygon(surf, ai._GLYPH_SH, [(int(x), int(y)) for x, y in gape])
        # A round eye-dot so the disc reads as a face/head, not a moon.
        pygame.draw.circle(surf, ai._GLYPH_SH,
                           (int(jx - jr * 0.18), int(jy - jr * 0.40)),
                           max(3, int(r * 0.13)))
        # The sparkle pushed INTO the gape (overlapping the mouth opening) and
        # enlarged, with one bold bite-notch missing from its NEAR (lower-left)
        # edge — the half toward the jaw — so it reads as "mouth devouring a
        # sparkle," not a lone Pac-Man beside a speck.
        sx, sy = cx + int(r * 0.30), cy - int(r * 0.20)
        sr = r * 0.66
        star = _sparkle_pts(sx, sy, sr)
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in star])
        pygame.draw.circle(surf, ai._GLYPH_SH,
                           (int(sx - sr * 0.52), int(sy + sr * 0.54)),
                           max(4, int(r * 0.28)))
    else:
        # Sparkle-WHIRLPOOL: ONE dominant central sparkle with three satellite
        # sparkles caught on a clear inward SPIRAL — each seated on a thick arc
        # that curls toward the centre, shrinking as it goes (a vortex, not a
        # sprinkle) — plus a bold simplified crown arc on top, so the
        # one-bite→whirlpool climb past power_hungry reads at chip size.
        cy_v = cy + int(r * 0.18)                       # seat below the crown
        # Spiral arms first so the satellites sit on top of their own tails.
        for i in range(3):
            a0 = -math.pi / 2 + i * (2 * math.pi / 3)   # arm start angle
            arc_r = int(r * (0.86 - i * 0.04))
            rect = pygame.Rect(cx - arc_r, cy_v - arc_r, arc_r * 2, arc_r * 2)
            # Each arm sweeps ~150° inward; same handedness for all three reads
            # as one rotating whirlpool.
            pygame.draw.arc(surf, col, rect, a0, a0 + math.radians(150),
                            max(2, int(r * 0.12)))
        # Dominant centre sparkle.
        cstar = _sparkle_pts(cx, cy_v, r * 0.56)
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in cstar])
        # Three satellite sparkles riding the spiral, shrinking toward centre.
        for i in range(3):
            a = -math.pi / 2 + i * (2 * math.pi / 3) + math.radians(150)
            rad = r * (0.84 - i * 0.06)
            mx = cx + math.cos(a) * rad
            my = cy_v + math.sin(a) * rad
            ms = r * (0.30 - i * 0.05)
            mote = _sparkle_pts(mx, my, ms)
            pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in mote])
        # Bold three-point crown seated on top — the L4 insatiable rung. Taller
        # spikes + a solid base band so the crown survives at chip size.
        cw = r * 0.64
        cyt = cy - int(r * 0.70)
        crown = [
            (cx - cw, cyt + r * 0.30),
            (cx - cw, cyt + r * 0.02),
            (cx - cw * 0.52, cyt + r * 0.20),
            (cx, cyt - r * 0.26),
            (cx + cw * 0.52, cyt + r * 0.20),
            (cx + cw, cyt + r * 0.02),
            (cx + cw, cyt + r * 0.30),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in crown])
        # Solid base band under the spikes so the crown reads as one mass.
        pygame.draw.rect(surf, col,
                         (int(cx - cw), int(cyt + r * 0.18),
                          int(cw * 2), max(3, int(r * 0.14))))


def _glyph_power_hungry(surf, cx, cy, r, col):
    _appetite(surf, cx, cy, r, col, stage=0)


def _glyph_power_addict(surf, cx, cy, r, col):
    _appetite(surf, cx, cy, r, col, stage=1)


GLYPHS = {
    "first_powerup": _glyph_first_powerup,
    "powerup_sampler": _glyph_sampler,
    "magnet_life": _glyph_magnet_life,
    "powerup_collector": _glyph_collector,
    "greasy_fingers": _glyph_greasy,
    "power_hungry": _glyph_power_hungry,
    "power_addict": _glyph_power_addict,
}
