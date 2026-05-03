"""Five wild-but-still-mushroom grow-powerup variants — round 3.

Round 1 (committed 01a9281) — too similar to current Mario design.
Round 2 (committed 09d67c4) — abandoned the mushroom shape entirely.
Round 3 — keeps the wild round-2 themes but applies each to a CLEAR
mushroom silhouette: dome cap + stem + 4 canonical spots (theme-translated).

Each function has the same signature as `PowerUp._draw_mushroom`:

    fn(surf, cx, cy, pulse=0.0)

Imported by `tools/render_grow_gameplay.py`. Does NOT modify game code.
"""
import math
import pygame


SS = 3  # supersample factor for smooth curves

# ── Canonical mushroom geometry ────────────────────────────────────────────
# Match `game/entities.py:_draw_mushroom` so each variant reads as a mushroom
# with the same proportions as the current icon.
POWERUP_R = 14
CAP_W = (POWERUP_R + 1) * 2          # 30
CAP_H = POWERUP_R + 5                 # 19
CAP_DY = -POWERUP_R + 2               # cap_rect.y offset from cy → -12
STEM_W = 14
STEM_H = 13

# Same 4 spots as `_draw_mushroom`: (dx, dy, r). Preserving these is what
# anchors "this is a mushroom" — round 2 lost them.
CANONICAL_SPOTS = [(-7, -5, 3), (+6, -7, 4), (+2, +1, 3), (-3, +2, 2)]

# Default tan stem palette (mirrors game/draw.py MUSH_*).
MUSH_STEM_BODY = (245, 225, 195)
MUSH_STEM_HI   = (255, 255, 230)
MUSH_STEM_SH   = (200, 180, 145)


# ── Helpers ────────────────────────────────────────────────────────────────
def _hsv_to_rgb(h, s, v):
    i = int(h * 6); f = h * 6 - i
    p = v * (1 - s); q = v * (1 - f * s); t = v * (1 - (1 - f) * s)
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
    dst.blit(pygame.transform.smoothscale(src_big, (w, h)), (x, y))


def _cap_rect(cx, cy):
    """Canonical horizontal-oval dome rect — matches the current icon."""
    return pygame.Rect(cx - POWERUP_R - 1, cy + CAP_DY, CAP_W, CAP_H)


def _draw_standard_stem(surf, cx, cy,
                        body=MUSH_STEM_BODY, hi=MUSH_STEM_HI, sh=MUSH_STEM_SH):
    stem = pygame.Rect(cx - STEM_W // 2, cy, STEM_W, STEM_H)
    pygame.draw.rect(surf, body, stem, border_radius=5)
    pygame.draw.line(surf, hi, (cx - 4, cy + 2), (cx - 4, cy + 11), 2)
    pygame.draw.line(surf, sh, (cx + 3, cy + 2), (cx + 3, cy + 11), 1)


def _draw_canonical_spots(surf, cx, cy, fill, halo=None):
    """Stamp the 4 canonical mushroom spots in the requested fill colour
    (with an optional 1-px halo ring underneath for contrast)."""
    for dx, dy, r in CANONICAL_SPOTS:
        if halo is not None:
            pygame.draw.circle(surf, halo, (cx + dx, cy + dy), r + 1)
        pygame.draw.circle(surf, fill, (cx + dx, cy + dy), r)


# ── V1 — CRYSTAL MUSHROOM ──────────────────────────────────────────────────
def draw_v1_crystal(surf, cx, cy, pulse=0.0):
    """Mushroom dome cap with prismatic facets painted across the ellipse
    surface. Spots → bright crystalline starburst shines."""
    glow_t = 0.5 + 0.5 * math.sin(pulse * 1.4)

    # Soft cyan halo
    halo = pygame.Surface((48, 38), pygame.SRCALPHA)
    for r, a in ((22, int(30 + 20 * glow_t)),
                 (18, int(60 + 30 * glow_t)),
                 (14, int(95 + 40 * glow_t))):
        pygame.draw.ellipse(halo, (140, 220, 255, a),
                            pygame.Rect(24 - r, 19 - int(r * 0.7),
                                        r * 2, int(r * 1.4)))
    surf.blit(halo, (cx - 24, cy - 19 - 2))

    # Standard tan stem with cool blue inner sheen
    _draw_standard_stem(surf, cx, cy, hi=(220, 240, 255))

    # Cap supersampled
    cap_rect = _cap_rect(cx, cy)
    big_w, big_h = cap_rect.width + 4, cap_rect.height + 4
    big = _ss_surface(big_w, big_h)
    bcap = pygame.Rect(2 * SS, 2 * SS, cap_rect.width * SS, cap_rect.height * SS)

    # Outer dark rim
    pygame.draw.ellipse(big, (40, 60, 110), bcap.inflate(SS * 2, SS * 2))

    # Build base ellipse mask, then paint 6 prismatic facet wedges into it.
    cap_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(cap_mask, (255, 255, 255, 255), bcap)

    facets = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    bcx_full = bcap.centerx
    bcy_full = bcap.centery
    rx = bcap.width // 2 + SS * 4
    ry = bcap.height // 2 + SS * 4
    facet_hues = [0.55, 0.65, 0.78, 0.92, 0.08, 0.42]
    n = len(facet_hues)
    for i, h in enumerate(facet_hues):
        a0 = math.pi + i * (math.pi / n)         # left to right across the dome
        a1 = math.pi + (i + 1) * (math.pi / n)
        col = _hsv_to_rgb(h, 0.55, 0.95)
        # Radial wedge as a triangle to a far point on the ellipse boundary.
        p0 = (bcx_full + math.cos(a0) * rx, bcy_full + math.sin(a0) * ry)
        p1 = (bcx_full + math.cos(a1) * rx, bcy_full + math.sin(a1) * ry)
        pygame.draw.polygon(facets, col, [(bcx_full, bcy_full + ry), p0, p1])
        # Facet edge
        pygame.draw.line(facets, _hsv_to_rgb(h, 0.7, 0.55),
                         (bcx_full, bcy_full + ry), p0, 2)
    facets.blit(cap_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(facets, (0, 0))

    # Bright top sheen highlight
    sheen = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 255, 255, 180),
                        pygame.Rect(bcap.x + 4 * SS, bcap.y + 2 * SS,
                                    bcap.width - 8 * SS, 4 * SS))
    sheen.blit(cap_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # Cap rim line for definition
    pygame.draw.ellipse(big, (50, 70, 130), bcap, 2 * SS)

    _ss_blit(big, surf, cap_rect.x - 2, cap_rect.y - 2, big_w, big_h)

    # Crystalline spots — bright white shines with a tiny cyan halo and
    # a 4-spike sparkle cross overlayed on the largest one.
    for dx, dy, r in CANONICAL_SPOTS:
        sx, sy = cx + dx, cy + dy
        pygame.draw.circle(surf, (180, 230, 255), (sx, sy), r + 1)
        pygame.draw.circle(surf, (255, 255, 255), (sx, sy), r)
        # 4-point sparkle on each spot
        pygame.draw.line(surf, (255, 255, 255), (sx, sy - r - 1), (sx, sy + r + 1), 1)
        pygame.draw.line(surf, (255, 255, 255), (sx - r - 1, sy), (sx + r + 1, sy), 1)


# ── V2 — GALAXY MUSHROOM ───────────────────────────────────────────────────
def draw_v2_galaxy(surf, cx, cy, pulse=0.0):
    """Mushroom dome cap with a deep cosmic interior — spiral nebula and
    scattered stars. Spots → 4 brighter star clusters at the canonical
    positions so the mushroom-spot rhythm survives."""
    spin = pulse * 0.5
    glow_t = 0.5 + 0.5 * math.sin(pulse * 1.4)

    # Violet outer halo
    halo = pygame.Surface((52, 42), pygame.SRCALPHA)
    for r, a in ((24, int(30 + 20 * glow_t)),
                 (20, int(55 + 30 * glow_t)),
                 (16, int(90 + 40 * glow_t))):
        pygame.draw.ellipse(halo, (190, 130, 255, a),
                            pygame.Rect(26 - r, 21 - int(r * 0.7),
                                        r * 2, int(r * 1.4)))
    surf.blit(halo, (cx - 26, cy - 21 - 2))

    # Standard tan stem with two tiny twinkles
    _draw_standard_stem(surf, cx, cy)
    for sx, sy in ((cx - 3, cy + 4), (cx + 4, cy + 9)):
        pygame.draw.circle(surf, (255, 245, 220), (sx, sy), 1)

    # Cap supersampled
    cap_rect = _cap_rect(cx, cy)
    big_w, big_h = cap_rect.width + 4, cap_rect.height + 4
    big = _ss_surface(big_w, big_h)
    bcap = pygame.Rect(2 * SS, 2 * SS, cap_rect.width * SS, cap_rect.height * SS)

    pygame.draw.ellipse(big, (15, 8, 35), bcap.inflate(SS * 2, SS * 2))
    pygame.draw.ellipse(big, (40, 22, 75), bcap)

    cap_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(cap_mask, (255, 255, 255, 255), bcap)

    # Spiral nebula painted as colour-cycling dotted arms.
    nebula = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    ncx, ncy = bcap.centerx, bcap.centery
    rx, ry = bcap.width // 2, bcap.height // 2
    for arm in range(2):
        arm_phase = arm * math.pi
        for i in range(60):
            t = i / 60.0
            r = t * 0.9
            ang = arm_phase + t * 5.5 + spin
            px = ncx + math.cos(ang) * rx * r
            py = ncy + math.sin(ang) * ry * r
            hue = (0.78 + t * 0.25) % 1.0
            col = _hsv_to_rgb(hue, 0.65, 0.95)
            a = int(180 * (1 - t * 0.5))
            pygame.draw.circle(nebula, (*col, a),
                               (int(px), int(py)),
                               max(1, int(2 * SS - t * SS)))
    nebula.blit(cap_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(nebula, (0, 0))

    # Bright cosmic core
    core = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    for r, a in ((int(rx * 0.30), 90),
                 (int(rx * 0.20), 160),
                 (int(rx * 0.10), 240)):
        pygame.draw.circle(core, (255, 245, 220, a), (ncx, ncy), r)
    core.blit(cap_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(core, (0, 0))

    # Cap rim highlight
    pygame.draw.ellipse(big, (180, 130, 220), bcap, 2 * SS)
    pygame.draw.ellipse(big, (220, 180, 255),
                        pygame.Rect(bcap.x + 2 * SS, bcap.y + SS,
                                    bcap.width - 4 * SS, 4 * SS))

    _ss_blit(big, surf, cap_rect.x - 2, cap_rect.y - 2, big_w, big_h)

    # Spots → bright star clusters at canonical positions. Each is a tight
    # sparkle (cross + dot) so the spot rhythm is preserved.
    for dx, dy, r in CANONICAL_SPOTS:
        sx, sy = cx + dx, cy + dy
        # halo
        pygame.draw.circle(surf, (220, 200, 255), (sx, sy), r + 1)
        # bright body
        pygame.draw.circle(surf, (255, 255, 255), (sx, sy), r)
        # cross sparkle
        sl = r + 1
        pygame.draw.line(surf, (255, 255, 255), (sx - sl, sy), (sx + sl, sy), 1)
        pygame.draw.line(surf, (255, 255, 255), (sx, sy - sl), (sx, sy + sl), 1)


# ── V3 — MOLTEN LAVA MUSHROOM ──────────────────────────────────────────────
def draw_v3_lava(surf, cx, cy, pulse=0.0):
    """Mushroom dome cap as glowing volcanic rock with bright lava cracks
    snaking between the spots. Spots → glowing crater pits (dark-red disc
    with a hot orange centre). Tan stem with a thin glowing core seam."""
    glow_t = 0.5 + 0.5 * math.sin(pulse * 2.2)

    # Compact orange heat halo, cap-centred
    halo = pygame.Surface((50, 40), pygame.SRCALPHA)
    halo_cx, halo_cy = 25, 18
    for r, a in ((22, int(35 + 25 * glow_t)),
                 (18, int(70 + 35 * glow_t)),
                 (15, int(110 + 50 * glow_t))):
        pygame.draw.ellipse(halo, (255, 140, 50, a),
                            pygame.Rect(halo_cx - r, halo_cy - int(r * 0.65),
                                        r * 2, int(r * 1.3)))
    surf.blit(halo, (cx - halo_cx, cy - halo_cy + 2))

    # Tan stem with a hot core seam
    _draw_standard_stem(surf, cx, cy)
    pygame.draw.line(surf, (255, 200, 80), (cx, cy + 3), (cx, cy + 10), 1)

    # Cap supersampled — glowing volcanic dome
    cap_rect = _cap_rect(cx, cy)
    big_w, big_h = cap_rect.width + 4, cap_rect.height + 4
    big = _ss_surface(big_w, big_h)
    bcap = pygame.Rect(2 * SS, 2 * SS, cap_rect.width * SS, cap_rect.height * SS)

    pygame.draw.ellipse(big, (40, 18, 14), bcap.inflate(SS * 2, SS * 2))

    cap_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(cap_mask, (255, 255, 255, 255), bcap)

    # Volcanic vertical gradient: hot orange-red top → dark crust bottom.
    grad = pygame.Surface(bcap.size, pygame.SRCALPHA)
    for yy in range(bcap.height):
        t = yy / max(1, bcap.height - 1)
        if t < 0.45:
            u = t / 0.45
            col = (int(255 + (220 - 255) * u),
                   int(150 + ( 70 - 150) * u),
                   int( 60 + ( 30 -  60) * u))
        else:
            u = (t - 0.45) / 0.55
            col = (int(220 + ( 90 - 220) * u),
                   int( 70 + ( 25 -  70) * u),
                   int( 30 + ( 18 -  30) * u))
        pygame.draw.line(grad, col, (0, yy), (bcap.width, yy))
    inner_mask = pygame.Surface(bcap.size, pygame.SRCALPHA)
    pygame.draw.ellipse(inner_mask, (255, 255, 255, 255), inner_mask.get_rect())
    grad.blit(inner_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, bcap.topleft)

    # Lava cracks — branching from the cap centre, threading between the
    # canonical spot slots so they don't collide with the crater pits.
    bcx_full = bcap.centerx
    bcy_full = bcap.centery
    cracks = [
        ((-1, -1), [(-3, -2), (-2,  3), (-3,  1)]),
        (( 0,  0), [( 4, -3), ( 2,  3), ( 3,  1)]),
        ((-1, -1), [( 0,  4), ( 3,  2)]),
        (( 0,  0), [(-4,  3), (-3,  1)]),
    ]
    for layer_w, layer_col_a in (
        (5, (255, 100,  30, 110)),
        (3, (255, 200,  70, 200)),
        (1, (255, 255, 230, 255)),
    ):
        for start, segs in cracks:
            x = bcx_full + start[0] * SS
            y = bcy_full + start[1] * SS
            for dx, dy in segs:
                nx = x + dx * SS
                ny = y + dy * SS
                pygame.draw.line(big, layer_col_a, (x, y), (nx, ny),
                                 max(1, layer_w * SS // 2))
                x, y = nx, ny

    # Cap top sheen
    sheen = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 180, 200),
                        pygame.Rect(bcap.x + 4 * SS, bcap.y + 2 * SS,
                                    bcap.width - 8 * SS, 3 * SS))
    sheen.blit(cap_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(sheen, (0, 0))

    # Charred outline
    pygame.draw.ellipse(big, (40, 18, 14), bcap, 2 * SS)

    _ss_blit(big, surf, cap_rect.x - 2, cap_rect.y - 2, big_w, big_h)

    # Spots → glowing crater pits at the canonical positions.
    for dx, dy, r in CANONICAL_SPOTS:
        sx, sy = cx + dx, cy + dy
        pygame.draw.circle(surf, (60, 20, 18), (sx, sy), r + 1)   # rim
        pygame.draw.circle(surf, (110, 40, 30), (sx, sy), r)       # dark base
        pygame.draw.circle(surf, (255, 180,  60), (sx, sy), max(1, r - 1))
        pygame.draw.circle(surf, (255, 250, 220), (sx, sy), max(1, r - 2))


# ── V4 — HOLOGRAPHIC FOIL MUSHROOM ─────────────────────────────────────────
def draw_v4_holo(surf, cx, cy, pulse=0.0):
    """Mushroom dome cap with iridescent rainbow-foil bands and a diagonal
    specular streak. Spots → 4 mirror-chrome dots, each tinted a different
    rainbow hue. Silver chrome stem."""
    shift = (pulse * 0.18) % 1.0

    # Soft rainbow halo
    halo = pygame.Surface((52, 42), pygame.SRCALPHA)
    for i, r in enumerate((22, 18, 14)):
        hue = (shift + i * 0.18) % 1.0
        col = _hsv_to_rgb(hue, 0.45, 1.0)
        a = (35, 65, 100)[i]
        pygame.draw.ellipse(halo, (*col, a),
                            pygame.Rect(26 - r, 21 - int(r * 0.7),
                                        r * 2, int(r * 1.4)))
    surf.blit(halo, (cx - 26, cy - 21 - 2))

    # Chrome stem (silver gradient)
    stem_x = cx - STEM_W // 2
    pygame.draw.rect(surf, (30, 38, 60),
                     pygame.Rect(stem_x - 1, cy - 1, STEM_W + 2, STEM_H + 2),
                     border_radius=6)
    for yy in range(STEM_H):
        t = yy / max(1, STEM_H - 1)
        s = 0.5 + 0.5 * math.sin(t * math.pi * 2.0 + shift * math.tau)
        v = int(160 + 90 * s)
        pygame.draw.line(surf, (v, min(255, v + 5), min(255, v + 15)),
                         (stem_x + 1, cy + yy), (stem_x + STEM_W - 2, cy + yy))
    pygame.draw.rect(surf, (50, 60, 90),
                     pygame.Rect(stem_x, cy, STEM_W, STEM_H),
                     width=2, border_radius=5)
    pygame.draw.line(surf, (255, 255, 255),
                     (cx - 3, cy + 2), (cx - 3, cy + STEM_H - 3), 2)

    # Cap supersampled — iridescent dome
    cap_rect = _cap_rect(cx, cy)
    big_w, big_h = cap_rect.width + 4, cap_rect.height + 4
    big = _ss_surface(big_w, big_h)
    bcap = pygame.Rect(2 * SS, 2 * SS, cap_rect.width * SS, cap_rect.height * SS)

    pygame.draw.ellipse(big, (40, 50, 80), bcap.inflate(SS * 2, SS * 2))

    cap_mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(cap_mask, (255, 255, 255, 255), bcap)

    # Holographic horizontal bands cycling through HSV.
    grad = pygame.Surface(bcap.size, pygame.SRCALPHA)
    for yy in range(bcap.height):
        t = yy / max(1, bcap.height - 1)
        hue = (t * 1.1 + shift) % 1.0
        vmod = 0.7 + 0.3 * math.sin(t * math.pi * 3 + shift * math.tau * 2)
        col = _hsv_to_rgb(hue, 0.55, vmod)
        pygame.draw.line(grad, col, (0, yy), (bcap.width, yy))
    inner_mask = pygame.Surface(bcap.size, pygame.SRCALPHA)
    pygame.draw.ellipse(inner_mask, (255, 255, 255, 255), inner_mask.get_rect())
    grad.blit(inner_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(grad, bcap.topleft)

    # Diagonal specular streak
    streak = pygame.Surface(bcap.size, pygame.SRCALPHA)
    for k in range(bcap.width):
        for j in range(2 * SS):
            yy = int(k * 0.55) + j - bcap.height // 4
            if 0 <= yy < bcap.height:
                a = int(180 * (1 - j / (2 * SS)))
                streak.set_at((k, yy), (255, 255, 255, a))
    streak.blit(inner_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.blit(streak, bcap.topleft)

    pygame.draw.ellipse(big, (25, 30, 55), bcap, 2 * SS)

    _ss_blit(big, surf, cap_rect.x - 2, cap_rect.y - 2, big_w, big_h)

    # Spots → mirror-chrome dots, each rainbow-hue-tinted at the canonical
    # positions. Each is a small radial gradient ring (dark rim → tint
    # body → bright white centre) so they read as mirror balls.
    spot_hues = [0.55, 0.92, 0.15, 0.42]
    for (dx, dy, r), hue in zip(CANONICAL_SPOTS, spot_hues):
        sx, sy = cx + dx, cy + dy
        tint = _hsv_to_rgb((hue + shift) % 1.0, 0.55, 1.0)
        pygame.draw.circle(surf, (40, 50, 80),    (sx, sy), r + 1)
        pygame.draw.circle(surf, tint,            (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255), (sx - 1, sy - 1), max(1, r - 1))


# ── V5 — CLOUD-FLUFF MUSHROOM (Skybit-themed) ──────────────────────────────
def draw_v5_cloud(surf, cx, cy, pulse=0.0):
    """Mushroom silhouette ASSEMBLED from cloud-puff circles. Pale-pastel
    cloud-puff "spots" at the canonical positions (different pastel hues).
    Fluffy cloud-pillar stem with a soft sky-blue inner shadow. Tiny
    rainbow arc above."""
    pulse_v = 0.5 + 0.5 * math.sin(pulse * 2.0)

    # Tiny rainbow arc above the cap
    arc_rect = pygame.Rect(cx - 14, cy - 26, 28, 14)
    for i, col in enumerate(((255, 100, 100), (255, 180,  80),
                             (255, 240, 120), (120, 220, 130),
                             (110, 180, 255), (180, 130, 230))):
        r = arc_rect.inflate(-i * 2, -i * 2)
        if r.width > 4 and r.height > 4:
            pygame.draw.arc(surf, col, r,
                            math.radians(20), math.radians(160), 1)

    # Stem — fluffy cloud column. 3 stacked puffs to form a stem-shaped
    # rectangle silhouette while still reading as cloud.
    stem_puffs = [
        (cx - 4, cy + 3,  5),
        (cx + 4, cy + 3,  5),
        (cx - 3, cy + 9,  5),
        (cx + 3, cy + 9,  5),
        (cx,     cy + 12, 4),
    ]
    for px, py, pr in stem_puffs:
        pygame.draw.circle(surf, (220, 235, 250), (px, py), pr + 1)
    for px, py, pr in stem_puffs:
        pygame.draw.circle(surf, (255, 255, 255), (px, py), pr)
    # Sky-blue inner shadow on the right side
    pygame.draw.circle(surf, (200, 220, 240), (cx + 3, cy + 6), 2)

    # Cap — assembled from cloud puffs. Layout matches a horizontal-oval
    # dome so the silhouette reads as a mushroom cap.
    # Outer pale-blue rim first.
    cap_puffs = [
        (cx - 12, cy - 5, 5),
        (cx -  7, cy - 9, 6),
        (cx -  1, cy -10, 6),
        (cx +  6, cy - 9, 6),
        (cx + 12, cy - 5, 5),
        (cx -  9, cy - 2, 5),
        (cx -  3, cy - 4, 5),
        (cx +  3, cy - 4, 5),
        (cx +  9, cy - 2, 5),
        (cx,      cy - 1, 4),
    ]
    for px, py, pr in cap_puffs:
        pygame.draw.circle(surf, (215, 230, 248), (px, py), pr + 1)
    for px, py, pr in cap_puffs:
        pygame.draw.circle(surf, (255, 255, 255), (px, py), pr)
    # Soft pink underglow inside the cap (hints at the "red mushroom" colour
    # without breaking the cloud read)
    glow = pygame.Surface((28, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (255, 180, 200, int(80 + 50 * pulse_v)),
                        glow.get_rect())
    surf.blit(glow, (cx - 14, cy - 8))

    # Highlights on top puffs
    for px, py, pr in cap_puffs[:5]:
        pygame.draw.circle(surf, (255, 255, 255),
                           (px - pr // 3, py - pr // 3), max(1, pr // 3))

    # Spots → small pastel cloud puffs at the canonical positions, each in
    # a different pastel hue so the spot rhythm reads.
    spot_pastels = [(255, 200, 220), (200, 230, 255),
                    (255, 240, 200), (220, 240, 220)]
    for (dx, dy, r), col in zip(CANONICAL_SPOTS, spot_pastels):
        sx, sy = cx + dx, cy + dy
        pygame.draw.circle(surf, (180, 190, 210), (sx, sy), r + 1)
        pygame.draw.circle(surf, col,             (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255),
                           (sx - 1, sy - 1), max(1, r - 1))


VARIANTS = {
    1: ("1 — crystal",     draw_v1_crystal),
    2: ("2 — galaxy",      draw_v2_galaxy),
    3: ("3 — molten",      draw_v3_lava),
    4: ("4 — holo foil",   draw_v4_holo),
    5: ("5 — cloud-fluff", draw_v5_cloud),
}
