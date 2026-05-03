"""Five WILD grow-powerup concepts — high-detail, supersampled, visually
mind-blowing variants that abandon the standard Mario silhouette.

User feedback round 2: previous variants were too similar to the
original. This round goes wild — different shapes, different palettes,
different effects.

Each function has the same signature as `PowerUp._draw_mushroom`:

    fn(surf, cx, cy, pulse=0.0)

Centred on (cx, cy). Footprint roughly ±18 px from centre.

Imported by `tools/render_grow_gameplay.py`. Does NOT modify game code.
"""
import math
import pygame


SS = 3  # supersample factor for smooth curves


# ── Helpers ────────────────────────────────────────────────────────────────
def _hsv_to_rgb(h, s, v):
    """h in [0,1], s,v in [0,1] → (r,g,b) ints 0-255."""
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i %= 6
    if   i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else:        r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)


def _ss_surface(w, h):
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _ss_blit(src_big, dst, x, y, w, h):
    small = pygame.transform.smoothscale(src_big, (w, h))
    dst.blit(small, (x, y))


# ── V1 — CRYSTAL PRISM GEM ─────────────────────────────────────────────────
def draw_v1_crystal(surf, cx, cy, pulse=0.0):
    """Faceted hexagonal crystal cap with prismatic rainbow facets and a
    bright internal glow. Stem is a stack of crystalline rhombuses. No
    spots — replaced by sharp specular highlights on each facet edge."""
    glow_t = 0.5 + 0.5 * math.sin(pulse * 1.4)

    # Outer halo glow (cyan)
    halo = pygame.Surface((64, 64), pygame.SRCALPHA)
    for r, a in ((26, int(40 * glow_t)),
                 (20, int(75 * glow_t)),
                 (15, int(110 * glow_t))):
        pygame.draw.circle(halo, (140, 220, 255, a), (32, 28), r)
    surf.blit(halo, (cx - 32, cy - 28 - 4))

    # Crystalline stem — 2 stacked rhombuses (icy white-cyan)
    stem_pts_outer = [
        (cx,     cy + 14),
        (cx - 6, cy + 8),
        (cx - 5, cy + 1),
        (cx,     cy - 2),
        (cx + 5, cy + 1),
        (cx + 6, cy + 8),
    ]
    stem_pts_inner = [
        (cx,     cy + 12),
        (cx - 4, cy + 8),
        (cx - 3, cy + 2),
        (cx,     cy - 1),
        (cx + 3, cy + 2),
        (cx + 4, cy + 8),
    ]
    pygame.draw.polygon(surf, ( 60, 130, 180), stem_pts_outer)
    pygame.draw.polygon(surf, (200, 240, 255), stem_pts_inner)
    pygame.draw.line(surf, (255, 255, 255),
                     (cx - 1, cy + 1), (cx - 1, cy + 10), 1)
    pygame.draw.line(surf, ( 90, 160, 200),
                     (cx + 2, cy + 2), (cx + 2, cy + 9), 1)

    # Hexagonal faceted cap — drawn supersampled for clean edges.
    R = 17
    big = _ss_surface(R * 2 + 4, R * 2 + 4)
    bcx, bcy = (R + 2) * SS, (R + 2) * SS
    rs = R * SS

    # Hexagon vertices (flat-top, slightly squashed)
    verts = []
    for i in range(6):
        ang = math.radians(60 * i + 30)  # pointy sides L/R
        verts.append((
            bcx + math.cos(ang) * rs,
            bcy + math.sin(ang) * rs * 0.78,
        ))

    # Facet colours — prismatic
    # Top centre: bright white-cyan, fanning out into 6 facet triangles
    # with hue shifting around the rim.
    facet_hues = [0.55, 0.62, 0.78, 0.92, 0.08, 0.42]  # cyan→violet→pink→amber→teal
    centre = (bcx, bcy - rs * 0.05)
    for i in range(6):
        v1 = verts[i]
        v2 = verts[(i + 1) % 6]
        h = facet_hues[i]
        col = _hsv_to_rgb(h, 0.55, 0.95)
        dk  = _hsv_to_rgb(h, 0.70, 0.55)
        pygame.draw.polygon(big, col, [centre, v1, v2])
        # Thin dark facet edge
        pygame.draw.line(big, dk, v1, v2, 2)
        pygame.draw.line(big, dk, centre, v1, 1)

    # Bright top triangle highlight (the gem's "table")
    top_pts = [centre,
               ((verts[1][0] + verts[2][0]) / 2, (verts[1][1] + verts[2][1]) / 2),
               ((verts[0][0] + verts[1][0]) / 2, (verts[0][1] + verts[1][1]) / 2)]
    pygame.draw.polygon(big, (255, 255, 255, 180), top_pts)

    # Outer hexagon outline — bold dark for contrast
    pygame.draw.polygon(big, (35, 50, 90), verts, 3)

    # Inner glow core (pulses)
    core_a = int(120 + 90 * glow_t)
    core = pygame.Surface((rs, rs), pygame.SRCALPHA)
    pygame.draw.circle(core, (255, 255, 255, core_a),
                       (rs // 2, rs // 2), int(rs * 0.22))
    big.blit(core, (bcx - rs // 2, int(bcy - rs * 0.45)))

    _ss_blit(big, surf, cx - R - 2, cy - R, R * 2 + 4, R * 2 + 4)

    # Sparkle prick at top
    for ang_deg, dist in ((90, 16), (30, 14), (150, 14)):
        ang = math.radians(ang_deg)
        sx = cx + int(math.cos(ang) * dist) * 0
        sy = cy - int(dist * 0.7)
        # placed via direct top-right/top-left sparks instead
    for px, py in ((cx, cy - 17), (cx - 12, cy - 10), (cx + 12, cy - 11)):
        a = int(180 + 70 * glow_t)
        sp = pygame.Surface((7, 7), pygame.SRCALPHA)
        pygame.draw.line(sp, (255, 255, 255, a), (3, 0), (3, 6), 1)
        pygame.draw.line(sp, (255, 255, 255, a), (0, 3), (6, 3), 1)
        pygame.draw.circle(sp, (255, 255, 255, a), (3, 3), 1)
        surf.blit(sp, (px - 3, py - 3))


# ── V2 — GALAXY / NEBULA MUSHROOM ──────────────────────────────────────────
def draw_v2_galaxy(surf, cx, cy, pulse=0.0):
    """Cap is a deep cosmos: midnight purple base with a swirling spiral
    nebula in pink/violet/cyan, scattered white stars, and a brilliant
    glowing core. Stem is a starlit pillar with twinkles."""
    spin = pulse * 0.5
    glow_t = 0.5 + 0.5 * math.sin(pulse * 1.4)

    # Outer cosmic glow (violet halo so the dark cap reads on dark BG)
    halo = pygame.Surface((72, 56), pygame.SRCALPHA)
    for r, a in ((30, int(35 + 25 * glow_t)),
                 (24, int(60 + 35 * glow_t)),
                 (18, int(95 + 45 * glow_t))):
        pygame.draw.circle(halo, (190, 130, 255, a), (36, 26), r)
    surf.blit(halo, (cx - 36, cy - 26 - 4))

    # Stem — dark midnight blue with vertical gradient and tiny stars
    stem_w, stem_h = 14, 14
    stem_x = cx - stem_w // 2
    pygame.draw.rect(surf, (15, 10, 35),
                     pygame.Rect(stem_x - 1, cy - 1, stem_w + 2, stem_h + 2),
                     border_radius=6)
    for yy in range(stem_h):
        t = yy / max(1, stem_h - 1)
        col = (
            int( 80 + ( 35 -  80) * t),
            int( 65 + ( 28 -  65) * t),
            int(140 + ( 65 - 140) * t),
        )
        pygame.draw.line(surf, col,
                         (stem_x + 1, cy + yy), (stem_x + stem_w - 2, cy + yy))
    pygame.draw.rect(surf, (12, 8, 30),
                     pygame.Rect(stem_x, cy, stem_w, stem_h),
                     width=2, border_radius=5)
    # Stem stars
    for sx, sy in ((cx - 3, cy + 3), (cx + 3, cy + 7), (cx - 2, cy + 11),
                   (cx + 4, cy + 11)):
        pygame.draw.circle(surf, (255, 245, 220), (sx, sy), 1)

    # Cap — supersampled cosmic disc
    R = 17
    big = _ss_surface(R * 2 + 4, R * 2 + 4)
    bcx, bcy = (R + 2) * SS, (R + 2) * SS
    rs = R * SS

    cap_rect = pygame.Rect(2 * SS, 4 * SS, R * 2 * SS, int(R * 1.5 * SS))

    # Outer dark rim
    pygame.draw.ellipse(big, (15, 8, 35), cap_rect.inflate(SS * 2, SS * 2))
    # Base midnight purple disc
    pygame.draw.ellipse(big, (40, 22, 75), cap_rect)

    # Build the swirling nebula on a circular surface, then mask to ellipse.
    nebula = pygame.Surface((rs * 2, rs * 2), pygame.SRCALPHA)
    ncx, ncy = rs, rs
    # Plot spiral arms via dotted clouds
    for arm in range(2):
        arm_phase = arm * math.pi
        for i in range(80):
            t = i / 80.0
            r = t * rs * 0.95
            ang = arm_phase + t * 5.5 + spin
            px = ncx + math.cos(ang) * r
            py = ncy + math.sin(ang) * r * 0.7
            # Colour cycles along arm — magenta → violet → cyan
            hue = (0.78 + t * 0.25) % 1.0
            col = _hsv_to_rgb(hue, 0.65, 0.95)
            a = int(180 * (1 - t * 0.6))
            for jitter in (-2, 0, 2):
                pygame.draw.circle(
                    nebula, (*col, a // 2),
                    (int(px + jitter), int(py + jitter * 0.5)),
                    int(3 * SS - t * 2 * SS))
            pygame.draw.circle(
                nebula, (*col, a),
                (int(px), int(py)),
                max(1, int(2 * SS - t * SS)))

    # Mask nebula to the cap ellipse
    mask = pygame.Surface((rs * 2, rs * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255),
                        pygame.Rect(0, int(rs * 0.25),
                                    rs * 2, int(rs * 1.05)))
    nebula.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(nebula, (bcx - rs, bcy - rs))

    # Bright core
    core = pygame.Surface((rs, rs), pygame.SRCALPHA)
    for r, a in ((int(rs * 0.32), 90),
                 (int(rs * 0.22), 160),
                 (int(rs * 0.12), 240)):
        pygame.draw.circle(core, (255, 245, 220, a),
                           (rs // 2, rs // 2), r)
    big.blit(core, (bcx - rs // 2, bcy - int(rs * 0.45)))

    # Scattered stars (cross-shaped sparkles)
    star_positions = [
        (-12,  -6, 2), ( 10,  -8, 2), ( -4, -12, 1),
        (  6,  -2, 1), (-10,   2, 1), ( 12,   0, 2),
        ( -2,  -4, 1), (  2,   3, 1), (  0,  -9, 2),
    ]
    for dx, dy, sz in star_positions:
        sxp = bcx + dx * SS
        syp = bcy + dy * SS
        sl = sz * SS
        pygame.draw.line(big, (255, 255, 255), (sxp - sl, syp), (sxp + sl, syp), 1)
        pygame.draw.line(big, (255, 255, 255), (sxp, syp - sl), (sxp, syp + sl), 1)
        pygame.draw.circle(big, (255, 255, 255), (sxp, syp), max(1, sz))

    # Cap rim outline + highlight
    pygame.draw.ellipse(big, (180, 130, 220), cap_rect, 2 * SS)
    pygame.draw.ellipse(big, (220, 180, 255),
                        pygame.Rect(cap_rect.x + 2 * SS, cap_rect.y + SS,
                                    cap_rect.width - 4 * SS, 4 * SS))

    _ss_blit(big, surf, cx - R - 2, cy - R, R * 2 + 4, R * 2 + 4)


# ── V3 — MOLTEN LAVA / OBSIDIAN ────────────────────────────────────────────
def draw_v3_lava(surf, cx, cy, pulse=0.0):
    """Cap is dark cracked obsidian with glowing orange-yellow lava
    seams running through it (lightning-pattern). Heat-glow halo,
    rising ember sparks, dark stem with hot core."""
    glow_t = 0.5 + 0.5 * math.sin(pulse * 2.2)

    # Hot glow halo centred on the CAP (not above it). Bright orange
    # bleed sells the dome as molten / glowing.
    halo = pygame.Surface((60, 50), pygame.SRCALPHA)
    halo_cx, halo_cy = 30, 22
    for r, a in ((26, int(40 + 25 * glow_t)),
                 (22, int(80 + 35 * glow_t)),
                 (18, int(125 + 50 * glow_t))):
        pygame.draw.ellipse(halo, (255, 140, 50, a),
                            pygame.Rect(halo_cx - r, halo_cy - int(r * 0.65),
                                        r * 2, int(r * 1.3)))
    surf.blit(halo, (cx - halo_cx, cy - halo_cy + 2))

    # Stem — warm dark rock with a hot core seam
    stem = pygame.Rect(cx - 7, cy, 14, 13)
    pygame.draw.rect(surf, (30, 16, 14), stem.inflate(2, 2), border_radius=6)
    pygame.draw.rect(surf, (95, 55, 45), stem, border_radius=5)
    # Horizontal rock striations
    pygame.draw.line(surf, (60, 30, 25), (cx - 5, cy + 5), (cx + 5, cy + 5), 1)
    pygame.draw.line(surf, (60, 30, 25), (cx - 5, cy + 9), (cx + 5, cy + 9), 1)
    # Glowing core seam
    pygame.draw.line(surf, (255, 200, 80),
                     (cx - 1, cy + 2), (cx - 1, cy + 11), 2)
    pygame.draw.line(surf, (255, 245, 200),
                     (cx - 1, cy + 4), (cx - 1, cy + 9), 1)

    # Cap supersampled — GLOWING volcanic dome
    R = 17
    big = _ss_surface(R * 2 + 4, R * 2 + 4)
    cap_rect = pygame.Rect(2 * SS, 4 * SS, R * 2 * SS, int(R * 1.55 * SS))

    # Outline (charred crust)
    pygame.draw.ellipse(big, (40, 18, 14), cap_rect.inflate(SS * 2, SS * 2))
    # Vertical gradient: hot orange-red top → dark crust bottom.
    # This is the KEY change: cap body is warm/bright, not brown/dark.
    grad = pygame.Surface(cap_rect.size, pygame.SRCALPHA)
    for yy in range(cap_rect.height):
        t = yy / max(1, cap_rect.height - 1)
        if t < 0.45:
            u = t / 0.45
            col = (
                int(255 + (220 - 255) * u),
                int(150 + ( 70 - 150) * u),
                int( 60 + ( 30 -  60) * u),
            )
        else:
            u = (t - 0.45) / 0.55
            col = (
                int(220 + ( 90 - 220) * u),
                int( 70 + ( 25 -  70) * u),
                int( 30 + ( 18 -  30) * u),
            )
        pygame.draw.line(grad, col, (0, yy), (cap_rect.width, yy))
    mask = pygame.Surface(cap_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, cap_rect.topleft)

    # Lava seams — branching cracks. Drawn in 3 alpha layers for bloom.
    bcx, bcy = (R + 2) * SS, int((R - 5) * SS) + cap_rect.height // 2
    cracks = [
        # (start_off, segments [dx, dy])
        ((-12,  -2), [(2, -3), (3,  4), (4, -2), (4,  3)]),
        ((  0, -10), [(-2, 4), (3,  3), (-3, 4), (4,  2)]),
        ((  3,  -1), [(4, -2), (3,  4), (-2, 3)]),
        (( -6,   4), [(3,  2), (4, -1), (3,  3)]),
    ]
    # Bright crack layers — wide red bloom, mid yellow, hot white core.
    for layer_w, layer_col_a in (
        (6, (255, 100,  30, 110)),
        (4, (255, 200,  70, 200)),
        (2, (255, 255, 230, 255)),
    ):
        for start, segs in cracks:
            x = bcx + start[0] * SS
            y = bcy + start[1] * SS
            for dx, dy in segs:
                nx = x + dx * SS
                ny = y + dy * SS
                pygame.draw.line(big, layer_col_a,
                                 (x, y), (nx, ny), max(1, layer_w * SS // 2))
                x, y = nx, ny

    # Specular sheen across the dome top
    hi = pygame.Rect(cap_rect.x + 4 * SS, cap_rect.y + 2 * SS,
                     cap_rect.width - 8 * SS, 3 * SS)
    pygame.draw.ellipse(big, (255, 230, 180, 220), hi)

    # Mask anything outside the cap ellipse
    mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), cap_rect)
    big.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    # Re-draw a thin charred outline on top
    pygame.draw.ellipse(big, (40, 18, 14), cap_rect, 2 * SS)

    _ss_blit(big, surf, cx - R - 2, cy - R, R * 2 + 4, R * 2 + 4)

    # Rising embers above the cap
    for i in range(3):
        phase = pulse * 1.8 + i * 1.7
        rise = (phase % 2.0)
        if rise < 1.4:
            ex = cx + int(math.sin(phase * 1.3 + i) * 6) + (i - 1) * 5
            ey = cy - 14 - int(rise * 8)
            a = int(255 * (1 - rise / 1.4))
            es = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(es, (255, 200,  60, a), (2, 2), 2)
            pygame.draw.circle(es, (255, 240, 180, a), (2, 2), 1)
            surf.blit(es, (ex - 2, ey - 2))


# ── V4 — HOLOGRAPHIC IRIDESCENT FOIL ───────────────────────────────────────
def draw_v4_holo(surf, cx, cy, pulse=0.0):
    """Iridescent rainbow holographic foil cap — horizontal bands cycling
    through cyan → magenta → yellow → green. Mirror-chrome stem with a
    silver vertical gradient. Bright specular streak on the cap."""
    shift = (pulse * 0.18) % 1.0

    # Iridescent halo — soft rainbow ring so the cap reads on dark BG
    halo = pygame.Surface((68, 56), pygame.SRCALPHA)
    for i, r in enumerate((28, 24, 20)):
        hue = (shift + i * 0.18) % 1.0
        col = _hsv_to_rgb(hue, 0.45, 1.0)
        a = (40, 70, 110)[i]
        pygame.draw.ellipse(halo, (*col, a),
                            pygame.Rect(34 - r, 28 - int(r * 0.8),
                                        r * 2, int(r * 1.6)))
    surf.blit(halo, (cx - 34, cy - 28 - 4))

    # Chrome stem — silver gradient + dark outline
    stem_w, stem_h = 14, 14
    stem_x = cx - stem_w // 2
    pygame.draw.rect(surf, (30, 38, 60),
                     pygame.Rect(stem_x - 1, cy - 1, stem_w + 2, stem_h + 2),
                     border_radius=6)
    for yy in range(stem_h):
        t = yy / max(1, stem_h - 1)
        # silver: light → dim → light bands for chrome
        s = 0.5 + 0.5 * math.sin(t * math.pi * 2.0 + shift * math.tau)
        v = int(160 + 90 * s)
        pygame.draw.line(surf, (v, min(255, v + 5), min(255, v + 15)),
                         (stem_x + 1, cy + yy), (stem_x + stem_w - 2, cy + yy))
    pygame.draw.rect(surf, (50, 60, 90),
                     pygame.Rect(stem_x, cy, stem_w, stem_h),
                     width=2, border_radius=5)
    # Bright vertical chrome highlight
    pygame.draw.line(surf, (255, 255, 255),
                     (cx - 3, cy + 2), (cx - 3, cy + stem_h - 3), 2)

    # Cap supersampled — iridescent bands inside a TALL dome ellipse
    R = 17
    big = _ss_surface(R * 2 + 4, R * 2 + 6)
    cap_rect = pygame.Rect(2 * SS, 4 * SS, R * 2 * SS, int(R * 1.7 * SS))

    # Outer outline
    pygame.draw.ellipse(big, (40, 50, 80), cap_rect.inflate(SS * 2, SS * 2))

    # Build holographic gradient (horizontal bands of HSV-cycled colour)
    grad = pygame.Surface((cap_rect.width, cap_rect.height), pygame.SRCALPHA)
    for yy in range(cap_rect.height):
        t = yy / max(1, cap_rect.height - 1)
        hue = (t * 1.1 + shift) % 1.0
        # vertical sheen modulates value
        vmod = 0.7 + 0.3 * math.sin(t * math.pi * 3 + shift * math.tau * 2)
        col = _hsv_to_rgb(hue, 0.55, vmod)
        pygame.draw.line(grad, col, (0, yy), (cap_rect.width, yy))

    # Apply elliptical mask
    mask = pygame.Surface((cap_rect.width, cap_rect.height), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, cap_rect.topleft)

    # Diagonal specular streak (chrome highlight)
    streak = pygame.Surface((cap_rect.width, cap_rect.height), pygame.SRCALPHA)
    for k in range(cap_rect.width):
        # diagonal offset
        for j in range(3 * SS):
            yy = int(k * 0.55) + j - cap_rect.height // 4
            if 0 <= yy < cap_rect.height:
                a = int(180 * (1 - j / (3 * SS)))
                streak.set_at((k, yy), (255, 255, 255, a))
    streak.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(streak, cap_rect.topleft)

    # Bold rim
    pygame.draw.ellipse(big, (25, 30, 55), cap_rect, 2 * SS)

    _ss_blit(big, surf, cx - R - 2, cy - R, R * 2 + 4, R * 2 + 6)

    # 3 tiny rainbow sparkles around the cap
    for i in range(3):
        ang = pulse * 1.2 + i * (math.tau / 3)
        sx = cx + int(math.cos(ang) * 16)
        sy = cy - 4 + int(math.sin(ang) * 6) - 4
        col = _hsv_to_rgb((shift + i / 3) % 1.0, 0.7, 1.0)
        sp = pygame.Surface((5, 5), pygame.SRCALPHA)
        pygame.draw.line(sp, (*col, 230), (2, 0), (2, 4), 1)
        pygame.draw.line(sp, (*col, 230), (0, 2), (4, 2), 1)
        pygame.draw.circle(sp, (255, 255, 255, 255), (2, 2), 1)
        surf.blit(sp, (sx - 2, sy - 2))


# ── V5 — CLOUD HEART (Skybit-themed, sky-game appropriate) ─────────────────
def draw_v5_cloud_heart(surf, cx, cy, pulse=0.0):
    """The cap is a pillowy CLOUD shaped like a heart — multiple white
    puffs forming a heart silhouette. A glowing pink heart-core peeks
    through. Tiny rainbow arc above. Stem is a golden sunbeam."""
    pulse_v = 0.5 + 0.5 * math.sin(pulse * 2.0)

    # Tiny rainbow arc above
    arc_rect = pygame.Rect(cx - 14, cy - 26, 28, 18)
    for i, col in enumerate(((255, 100, 100), (255, 180,  80),
                             (255, 240, 120), (120, 220, 130),
                             (110, 180, 255), (180, 130, 230))):
        r = arc_rect.inflate(-i * 2, -i * 2)
        if r.width > 4 and r.height > 4:
            pygame.draw.arc(surf, col, r, math.radians(20), math.radians(160), 1)

    # Sunbeam stem — gold gradient, slightly tapered
    stem_h = 14
    for yy in range(stem_h):
        t = yy / max(1, stem_h - 1)
        col = (
            int(255 + (220 - 255) * t),
            int(220 + (160 - 220) * t),
            int( 80 + ( 40 -  80) * t),
        )
        w = 13 - int(t * 3)
        pygame.draw.line(surf, col,
                         (cx - w // 2, cy + yy), (cx + w // 2, cy + yy))
    pygame.draw.rect(surf, (180, 110, 20),
                     pygame.Rect(cx - 7, cy, 14, stem_h),
                     width=2, border_radius=5)
    pygame.draw.line(surf, (255, 250, 200),
                     (cx - 3, cy + 2), (cx - 3, cy + stem_h - 3), 2)

    # Heart-shaped cloud cap — drawn supersampled.
    R = 18
    big = _ss_surface(R * 2 + 6, R * 2 + 6)
    bcx = (R + 3) * SS
    bcy = (R + 3) * SS

    # Heart silhouette via two top circles + bottom triangle (filled)
    lobe_r = int(8 * SS)
    lobe_dx = int(7 * SS)
    lobe_y = bcy - int(7 * SS)
    pink_outline = (180, 30, 70)
    # Outer pink outline (slightly larger heart)
    out_lobe_r = lobe_r + int(1.5 * SS)
    pygame.draw.circle(big, pink_outline, (bcx - lobe_dx, lobe_y), out_lobe_r)
    pygame.draw.circle(big, pink_outline, (bcx + lobe_dx, lobe_y), out_lobe_r)
    pygame.draw.polygon(big, pink_outline, [
        (bcx - int(15 * SS), lobe_y + int(2 * SS)),
        (bcx + int(15 * SS), lobe_y + int(2 * SS)),
        (bcx, bcy + int(11 * SS)),
    ])

    # Pink heart core (glowing, smaller)
    pink_core_a = int(180 + 70 * pulse_v)
    core_r = lobe_r - int(1 * SS)
    core_layer = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(core_layer, (255, 130, 170, pink_core_a),
                       (bcx - lobe_dx, lobe_y), core_r)
    pygame.draw.circle(core_layer, (255, 130, 170, pink_core_a),
                       (bcx + lobe_dx, lobe_y), core_r)
    pygame.draw.polygon(core_layer, (255, 130, 170, pink_core_a), [
        (bcx - int(13 * SS), lobe_y + int(2 * SS)),
        (bcx + int(13 * SS), lobe_y + int(2 * SS)),
        (bcx, bcy + int(9 * SS)),
    ])
    big.blit(core_layer, (0, 0))

    # Cloud puffs forming the heart's outer surface — overlay fluffy white
    # circles around the heart silhouette so it reads as a CLOUD heart.
    puffs = [
        (bcx - int(10 * SS), lobe_y - int(3 * SS), int(6 * SS)),
        (bcx - int(5 * SS),  lobe_y - int(5 * SS), int(5 * SS)),
        (bcx + int(5 * SS),  lobe_y - int(5 * SS), int(5 * SS)),
        (bcx + int(10 * SS), lobe_y - int(3 * SS), int(6 * SS)),
        (bcx - int(11 * SS), lobe_y + int(1 * SS), int(5 * SS)),
        (bcx + int(11 * SS), lobe_y + int(1 * SS), int(5 * SS)),
        (bcx - int(7 * SS),  lobe_y + int(4 * SS), int(5 * SS)),
        (bcx + int(7 * SS),  lobe_y + int(4 * SS), int(5 * SS)),
        (bcx,                lobe_y + int(5 * SS), int(5 * SS)),
        (bcx - int(3 * SS),  lobe_y + int(8 * SS), int(4 * SS)),
        (bcx + int(3 * SS),  lobe_y + int(8 * SS), int(4 * SS)),
        (bcx,                lobe_y + int(11 * SS), int(3 * SS)),
    ]
    # Outer cloud rim (soft grey-pink)
    for px, py, pr in puffs:
        pygame.draw.circle(big, (240, 220, 230), (px, py), pr + int(0.8 * SS))
    # White cloud body
    for px, py, pr in puffs:
        pygame.draw.circle(big, (255, 255, 255), (px, py), pr)
    # Subtle highlights
    for px, py, pr in puffs[:6]:
        pygame.draw.circle(big, (255, 255, 255),
                           (px - pr // 4, py - pr // 3), pr // 3)

    # Re-stamp the pink core ON TOP at lower alpha so it glows through
    glow = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 90, 140, int(110 + 60 * pulse_v)),
                       (bcx, lobe_y + int(1 * SS)), int(5 * SS))
    big.blit(glow, (0, 0))

    _ss_blit(big, surf, cx - R - 3, cy - R - 3, R * 2 + 6, R * 2 + 6)

    # Floating heart sparkles
    for i in range(2):
        phase = pulse * 1.6 + i * 2.1
        if math.sin(phase) > 0:
            sx = cx + (-12 if i == 0 else 12)
            sy = cy - 10 + int(math.sin(phase) * -3)
            pygame.draw.circle(surf, (255, 130, 170), (sx, sy), 1)
            pygame.draw.circle(surf, (255, 220, 230), (sx - 1, sy - 1), 1)


VARIANTS = {
    1: ("1 — crystal gem",   draw_v1_crystal),
    2: ("2 — galaxy nebula", draw_v2_galaxy),
    3: ("3 — molten lava",   draw_v3_lava),
    4: ("4 — holo chrome",   draw_v4_holo),
    5: ("5 — cloud heart",   draw_v5_cloud_heart),
}
