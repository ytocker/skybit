"""Five WACKY mushroom-fungus variants — round 4.

Round 1 — too similar to current Mario.
Round 2 — abandoned the mushroom shape.
Round 3 — too uniform: all dome-cap + tan stem + 4 canonical spots.
Round 4 — embraces the actual diversity of fungi: tall witch-hat
liberty caps, coral-antler branching fungus, sprouting clusters,
veiled bell mushrooms, character-face mushrooms.

Each function has the same signature as `PowerUp._draw_mushroom`:

    fn(surf, cx, cy, pulse=0.0)

Imported by `tools/render_grow_gameplay.py`. Does NOT modify game code.
"""
import math
import pygame


SS = 3  # supersample factor for smooth curves


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


def _ss(w, h):
    return pygame.Surface((w * SS, h * SS), pygame.SRCALPHA)


def _ss_blit(big, dst, x, y, w, h):
    dst.blit(pygame.transform.smoothscale(big, (w, h)), (x, y))


# ── V1 — TALL WITCH-HAT (Liberty Cap) ──────────────────────────────────────
def draw_v1_witchhat(surf, cx, cy, pulse=0.0):
    """Tall pointy conical cap with a curled wavy rim, on a slim
    elongated stem. Inspired by Liberty-Cap / fairy mushrooms.
    Cap is tall + narrow — completely different silhouette from a
    standard dome."""
    glow_t = 0.5 + 0.5 * math.sin(pulse * 1.3)

    # Soft purple halo around the tall hat
    halo = pygame.Surface((40, 56), pygame.SRCALPHA)
    for r, a in ((22, int(28 + 16 * glow_t)),
                 (17, int(50 + 30 * glow_t)),
                 (13, int(80 + 40 * glow_t))):
        pygame.draw.ellipse(halo, (200, 130, 255, a),
                            pygame.Rect(20 - r, 28 - r, r * 2, r * 2))
    surf.blit(halo, (cx - 20, cy - 28))

    # Slim elongated stem — narrow at top, slight bulb at bottom
    W = _ss(20, 22)
    pygame.draw.polygon(W, (250, 235, 215), [
        (8 * SS,  0 * SS),
        (12 * SS, 0 * SS),
        (13 * SS, 12 * SS),
        (15 * SS, 18 * SS),
        (10 * SS, 21 * SS),
        ( 5 * SS, 18 * SS),
        ( 7 * SS, 12 * SS),
    ])
    # Stem outline
    pygame.draw.polygon(W, (170, 145, 110), [
        (8 * SS,  0 * SS),
        (12 * SS, 0 * SS),
        (13 * SS, 12 * SS),
        (15 * SS, 18 * SS),
        (10 * SS, 21 * SS),
        ( 5 * SS, 18 * SS),
        ( 7 * SS, 12 * SS),
    ], width=SS)
    # Stem highlight
    pygame.draw.line(W, (255, 250, 230),
                     (9 * SS, 2 * SS), (9 * SS, 18 * SS), SS)
    _ss_blit(W, surf, cx - 10, cy + 2, 20, 22)

    # Tall conical cap drawn supersampled — cone with curled rim.
    cap_h = 24
    cap_w = 22
    big = _ss(cap_w, cap_h + 4)

    # Cone body: tall triangle with rounded peak.
    cone_pts = [
        (cap_w // 2 * SS, 0),
        (int(cap_w * 0.86 * SS), int(cap_h * 0.78 * SS)),
        (int(cap_w * 0.95 * SS), int(cap_h * 0.92 * SS)),
        (int(cap_w * 0.05 * SS), int(cap_h * 0.92 * SS)),
        (int(cap_w * 0.14 * SS), int(cap_h * 0.78 * SS)),
    ]
    # Outer dark outline
    out_pts = [(p[0], p[1]) for p in cone_pts]
    pygame.draw.polygon(big, (90, 30, 50), out_pts)
    # Slightly inset main body
    inset_pts = [
        (cap_w // 2 * SS, 1 * SS),
        (int(cap_w * 0.82 * SS), int(cap_h * 0.78 * SS)),
        (int(cap_w * 0.91 * SS), int(cap_h * 0.90 * SS)),
        (int(cap_w * 0.09 * SS), int(cap_h * 0.90 * SS)),
        (int(cap_w * 0.18 * SS), int(cap_h * 0.78 * SS)),
    ]
    pygame.draw.polygon(big, (200, 60, 110), inset_pts)
    # Vertical highlight stripe (left side) suggests volumetric cone
    pygame.draw.polygon(big, (255, 130, 170), [
        (cap_w // 2 * SS - 1 * SS,           1 * SS),
        (int(cap_w * 0.32 * SS),             int(cap_h * 0.55 * SS)),
        (int(cap_w * 0.22 * SS),             int(cap_h * 0.85 * SS)),
        (int(cap_w * 0.34 * SS),             int(cap_h * 0.85 * SS)),
        (int(cap_w * 0.42 * SS),             int(cap_h * 0.55 * SS)),
    ])
    # Wavy curled rim — half-circles along the cap base
    rim_y = int(cap_h * 0.86 * SS)
    rim_w = int(cap_w * 0.86 * SS)
    rim_x = int(cap_w * 0.07 * SS)
    n_curls = 5
    curl_w = rim_w // n_curls
    for i in range(n_curls):
        center = (rim_x + i * curl_w + curl_w // 2,
                  int(cap_h * 0.93 * SS))
        pygame.draw.circle(big, (200, 60, 110), center, curl_w // 2)
        pygame.draw.circle(big, ( 90, 30,  50), center, curl_w // 2, SS)
        pygame.draw.circle(big, (255, 150, 180),
                           (center[0] - curl_w // 5, center[1] - curl_w // 5),
                           max(1, curl_w // 4))

    # Spots scattered down the cone (white with halo)
    for sx, sy, sr in (
        (int(cap_w * 0.50 * SS), int(cap_h * 0.18 * SS), int(1.5 * SS)),
        (int(cap_w * 0.62 * SS), int(cap_h * 0.42 * SS), int(2.0 * SS)),
        (int(cap_w * 0.40 * SS), int(cap_h * 0.62 * SS), int(1.8 * SS)),
        (int(cap_w * 0.70 * SS), int(cap_h * 0.72 * SS), int(1.5 * SS)),
    ):
        pygame.draw.circle(big, (255, 220, 230), (sx, sy), sr + SS // 2)
        pygame.draw.circle(big, (255, 255, 255), (sx, sy), sr)

    _ss_blit(big, surf, cx - cap_w // 2, cy - cap_h + 2, cap_w, cap_h + 4)


# ── V2 — CORAL ANTLER FUNGUS ───────────────────────────────────────────────
def draw_v2_coral(surf, cx, cy, pulse=0.0):
    """Branching coral / antler fungus — no traditional cap. Multiple
    forking arms in vivid orange-red rising from a bulbous base, with
    pale glowing tips. Inspired by coral fungus and lion's mane."""
    glow_t = 0.5 + 0.5 * math.sin(pulse * 2.0)

    # Outer warm halo
    halo = pygame.Surface((44, 44), pygame.SRCALPHA)
    for r, a in ((20, int(35 + 18 * glow_t)),
                 (16, int(60 + 30 * glow_t)),
                 (12, int(95 + 40 * glow_t))):
        pygame.draw.circle(halo, (255, 160, 100, a), (22, 22), r)
    surf.blit(halo, (cx - 22, cy - 22 + 2))

    # Bulb base sitting on the ground line at cy+13
    base_rect = pygame.Rect(cx - 9, cy + 5, 18, 10)
    pygame.draw.ellipse(surf, (180,  90,  50), base_rect.inflate(2, 2))
    pygame.draw.ellipse(surf, (240, 170, 110), base_rect)
    # Side dimple shadow
    pygame.draw.ellipse(surf, (200, 130,  80),
                        pygame.Rect(cx - 7, cy + 9, 14, 5))

    # 5 antler-branches, each with 1-2 forks. Drawn on a supersampled
    # surface for smooth tapered tips.
    big = _ss(36, 30)
    bcx = 18 * SS
    base_y = 24 * SS
    branches = [
        # (root_dx, [(seg_dx, seg_dy), ...]) — relative to bulb top
        (-12, [(-3, -6), (-2, -7),  (-3, -5)]),
        ( -6, [(-1, -8), ( 1, -9),  ( 2, -7)]),
        (  0, [( 0, -10), (-1, -10), ( 1, -8)]),
        (  6, [( 1, -8), ( 3, -8),  ( 2, -6)]),
        ( 12, [( 3, -6), ( 4, -7),  ( 3, -5)]),
    ]
    main_col   = (235,  85,  55)
    dark_col   = (140,  35,  25)
    tip_col    = (255, 220, 160)
    for root_dx, segs in branches:
        x = bcx + root_dx * SS
        y = base_y
        prev = (x, y)
        for i, (sdx, sdy) in enumerate(segs):
            nx = prev[0] + sdx * SS
            ny = prev[1] + sdy * SS
            w = max(SS, (3 - i) * SS)
            # outline pass
            pygame.draw.line(big, dark_col, prev, (nx, ny), w + SS)
            prev = (nx, ny)
        # main body second pass
        x = bcx + root_dx * SS
        y = base_y
        prev = (x, y)
        for i, (sdx, sdy) in enumerate(segs):
            nx = prev[0] + sdx * SS
            ny = prev[1] + sdy * SS
            w = max(SS, (3 - i) * SS)
            pygame.draw.line(big, main_col, prev, (nx, ny), w)
            prev = (nx, ny)
        # glowing tip
        pygame.draw.circle(big, dark_col, prev, int(2.4 * SS))
        pygame.draw.circle(big, tip_col,  prev, int(1.6 * SS))
        pygame.draw.circle(big, (255, 250, 220),
                           (prev[0] - SS // 2, prev[1] - SS // 2),
                           max(1, int(0.8 * SS)))

    _ss_blit(big, surf, cx - 18, cy - 6, 36, 30)


# ── V3 — CLUSTER OF 3 SPROUTS ──────────────────────────────────────────────
def draw_v3_cluster(surf, cx, cy, pulse=0.0):
    """3 little mushrooms growing together in a clump with grass blades
    at the base. One taller in the middle, two flanking shorter ones.
    Each is a tiny red mushroom with a single white spot."""
    bob_l = math.sin(pulse * 1.7) * 0.6
    bob_m = math.sin(pulse * 2.1 + 1.3) * 0.7
    bob_r = math.sin(pulse * 1.9 + 2.4) * 0.6

    # Soft warm halo
    halo = pygame.Surface((44, 36), pygame.SRCALPHA)
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.5)
    for r, a in ((20, int(28 + 16 * pulse_t)),
                 (16, int(55 + 30 * pulse_t))):
        pygame.draw.ellipse(halo, (255, 200, 200, a),
                            pygame.Rect(22 - r, 18 - int(r * 0.7),
                                        r * 2, int(r * 1.4)))
    surf.blit(halo, (cx - 22, cy - 18))

    # Grass tuft — 4-5 blades behind the cluster
    grass_col_dk = ( 60, 130,  60)
    grass_col_lt = (130, 200,  90)
    for bx, by, h, lean in (
        (cx - 11, cy + 13,  6, -1),
        (cx -  5, cy + 13,  8,  1),
        (cx +  3, cy + 13,  7, -1),
        (cx + 10, cy + 13,  6,  1),
    ):
        pygame.draw.line(surf, grass_col_dk,
                         (bx, by), (bx + lean, by - h), 2)
        pygame.draw.line(surf, grass_col_lt,
                         (bx, by), (bx + lean, by - h), 1)

    def _mini_mushroom(mx, my, scale=1.0,
                       cap_col=(225, 50, 55), cap_hi=(255, 110, 90),
                       stem_col=(245, 225, 195)):
        # Stem
        stem_w = max(2, int(5 * scale))
        stem_h = max(3, int(6 * scale))
        sr = pygame.Rect(mx - stem_w // 2, my, stem_w, stem_h)
        pygame.draw.rect(surf, (170, 140, 100), sr.inflate(2, 2),
                         border_radius=2)
        pygame.draw.rect(surf, stem_col, sr, border_radius=2)
        # Cap
        cap_w = max(6, int(11 * scale))
        cap_h = max(5, int(8 * scale))
        cap_r = pygame.Rect(mx - cap_w // 2, my - cap_h + 1, cap_w, cap_h)
        pygame.draw.ellipse(surf, ( 90, 20, 30), cap_r.inflate(2, 2))
        pygame.draw.ellipse(surf, cap_col, cap_r)
        pygame.draw.ellipse(surf, cap_hi,
                            pygame.Rect(cap_r.x + 1, cap_r.y + 1,
                                        cap_r.width - 2, max(2, cap_r.height // 2)))
        # Single white spot
        spot_r = max(1, int(1.6 * scale))
        pygame.draw.circle(surf, (220, 200, 210),
                           (mx + 1, cap_r.y + 2), spot_r + 1)
        pygame.draw.circle(surf, (255, 255, 255),
                           (mx + 1, cap_r.y + 2), spot_r)

    # Left small (cooler red)
    _mini_mushroom(cx - 9, cy + 5 + int(bob_l), scale=0.9,
                   cap_col=(220, 70, 80), cap_hi=(255, 130, 130))
    # Right small (orange-red)
    _mini_mushroom(cx + 9, cy + 6 + int(bob_r), scale=0.85,
                   cap_col=(235, 100, 50), cap_hi=(255, 160, 80))
    # Middle big (classic red, on top so it overlaps)
    _mini_mushroom(cx, cy + 1 + int(bob_m), scale=1.25)


# ── V4 — VEILED BELL MUSHROOM ──────────────────────────────────────────────
def draw_v4_bell_veil(surf, cx, cy, pulse=0.0):
    """Bell-shaped (rounded box) cap with an ornate frilly skirt/veil
    ring around the middle of the stem. Inspired by death-cap and other
    veiled fungi. Lavender / royal palette."""
    glow_t = 0.5 + 0.5 * math.sin(pulse * 1.6)

    # Cool violet halo
    halo = pygame.Surface((44, 50), pygame.SRCALPHA)
    for r, a in ((22, int(28 + 16 * glow_t)),
                 (17, int(55 + 30 * glow_t)),
                 (13, int(90 + 40 * glow_t))):
        pygame.draw.ellipse(halo, (170, 130, 230, a),
                            pygame.Rect(22 - r, 25 - int(r * 0.8),
                                        r * 2, int(r * 1.6)))
    surf.blit(halo, (cx - 22, cy - 25 + 2))

    # Stem — slim, ivory
    stem_w = 9
    stem_h = 16
    stem_x = cx - stem_w // 2
    stem_y = cy - 2
    pygame.draw.rect(surf, (160, 140, 180),
                     pygame.Rect(stem_x - 1, stem_y - 1, stem_w + 2, stem_h + 2),
                     border_radius=4)
    pygame.draw.rect(surf, (235, 220, 240),
                     pygame.Rect(stem_x, stem_y, stem_w, stem_h),
                     border_radius=3)
    pygame.draw.line(surf, (255, 245, 255),
                     (cx - 2, stem_y + 2), (cx - 2, stem_y + stem_h - 2), 2)

    # Frilly veil/skirt — wide horizontal scallop ring at mid-stem
    veil_y = stem_y + 9
    veil_w = 22
    veil_x = cx - veil_w // 2
    # Underside shadow
    pygame.draw.ellipse(surf, ( 90,  60, 120),
                        pygame.Rect(veil_x, veil_y, veil_w, 4))
    # Scalloped skirt — 6 little arches across the underside
    for i in range(6):
        bx = veil_x + 1 + int(i * (veil_w - 2) / 6)
        by = veil_y + 2
        pygame.draw.circle(surf, (200, 170, 230), (bx + 2, by + 2), 2)
        pygame.draw.circle(surf, (140, 100, 180), (bx + 2, by + 2), 2, 1)
    # Ring band on top
    pygame.draw.ellipse(surf, (200, 170, 230),
                        pygame.Rect(veil_x, veil_y - 1, veil_w, 3))
    pygame.draw.ellipse(surf, (140, 100, 180),
                        pygame.Rect(veil_x, veil_y - 1, veil_w, 3), 1)

    # Bell-shaped cap — rounded square, taller than typical dome
    cap_w = 26
    cap_h = 22
    big = _ss(cap_w + 4, cap_h + 6)
    bw = (cap_w + 4) * SS
    bh = (cap_h + 6) * SS
    cap_rect = pygame.Rect(2 * SS, 2 * SS, cap_w * SS, cap_h * SS)
    # Outline
    pygame.draw.rect(big, (60, 30, 90), cap_rect.inflate(2 * SS, 2 * SS),
                     border_top_left_radius=cap_w * SS // 2,
                     border_top_right_radius=cap_w * SS // 2,
                     border_bottom_left_radius=4 * SS,
                     border_bottom_right_radius=4 * SS)
    # Body
    pygame.draw.rect(big, (130,  80, 200), cap_rect,
                     border_top_left_radius=cap_w * SS // 2,
                     border_top_right_radius=cap_w * SS // 2,
                     border_bottom_left_radius=4 * SS,
                     border_bottom_right_radius=4 * SS)
    # Vertical gradient sheen on top
    sheen_rect = pygame.Rect(cap_rect.x + 3 * SS, cap_rect.y + 2 * SS,
                             cap_rect.width - 6 * SS, cap_rect.height // 2)
    sheen = pygame.Surface(sheen_rect.size, pygame.SRCALPHA)
    for yy in range(sheen_rect.height):
        a = int(180 * (1 - yy / sheen_rect.height))
        pygame.draw.line(sheen, (220, 170, 255, a),
                         (0, yy), (sheen_rect.width, yy))
    big.blit(sheen, sheen_rect.topleft)
    # Bright top crescent
    pygame.draw.ellipse(big, (240, 210, 255),
                        pygame.Rect(cap_rect.x + 5 * SS, cap_rect.y + 2 * SS,
                                    cap_rect.width - 10 * SS, 3 * SS))

    # Ornate cap markings — vertical "Y" ridge and 3 small gem dots
    pygame.draw.line(big, (90, 50, 150),
                     (cap_rect.centerx, cap_rect.y + 4 * SS),
                     (cap_rect.centerx, cap_rect.bottom - 5 * SS), SS * 2)
    pygame.draw.line(big, (90, 50, 150),
                     (cap_rect.centerx, cap_rect.y + cap_rect.height // 2),
                     (cap_rect.centerx - cap_rect.width // 4,
                      cap_rect.bottom - 5 * SS), SS * 2)
    pygame.draw.line(big, (90, 50, 150),
                     (cap_rect.centerx, cap_rect.y + cap_rect.height // 2),
                     (cap_rect.centerx + cap_rect.width // 4,
                      cap_rect.bottom - 5 * SS), SS * 2)

    # Three gold gem dots arrayed across the cap
    for gx_frac, gy_frac in ((0.30, 0.30), (0.50, 0.18), (0.70, 0.30)):
        gx = cap_rect.x + int(cap_rect.width * gx_frac)
        gy = cap_rect.y + int(cap_rect.height * gy_frac)
        pygame.draw.circle(big, (140,  80,  20), (gx, gy), int(2.0 * SS))
        pygame.draw.circle(big, (255, 220,  80), (gx, gy), int(1.4 * SS))
        pygame.draw.circle(big, (255, 250, 200),
                           (gx - SS // 2, gy - SS // 2), max(1, SS // 2))

    _ss_blit(big, surf, cx - cap_w // 2 - 2, cy - cap_h - 2,
             cap_w + 4, cap_h + 6)


# ── V5 — CHARACTER FACE MUSHROOM ───────────────────────────────────────────
def draw_v5_face(surf, cx, cy, pulse=0.0):
    """Cute kawaii character mushroom: round red cap with big anime
    eyes (with shines), pink blush cheeks, and a tiny smile. Reads as
    'this is a friend.'"""
    blink_t = (pulse * 1.4 + 3.7) % 6.28
    blink = math.sin(blink_t) > 0.96  # rare, snappy blink — phase-shifted
                                       # so the picker static frame at
                                       # pulse=1.2 shows open eyes.
    bob = int(math.sin(pulse * 2.0) * 0.8)

    # Soft pink halo
    halo = pygame.Surface((44, 44), pygame.SRCALPHA)
    pulse_t = 0.5 + 0.5 * math.sin(pulse * 1.6)
    for r, a in ((20, int(28 + 16 * pulse_t)),
                 (16, int(55 + 30 * pulse_t))):
        pygame.draw.ellipse(halo, (255, 180, 200, a),
                            pygame.Rect(22 - r, 22 - int(r * 0.7),
                                        r * 2, int(r * 1.4)))
    surf.blit(halo, (cx - 22, cy - 22 + bob))

    # Stem — chubby and short, with a tiny base
    stem = pygame.Rect(cx - 8, cy + bob, 16, 13)
    pygame.draw.rect(surf, (170, 140, 100), stem.inflate(2, 2),
                     border_radius=6)
    pygame.draw.rect(surf, (250, 235, 215), stem, border_radius=5)
    # Stem cheeks (lighter blob)
    pygame.draw.ellipse(surf, (255, 250, 235),
                        pygame.Rect(cx - 6, cy + 2 + bob, 12, 6))

    # Cap — large round, classic red gradient
    cap_w = 30
    cap_h = 20
    big = _ss(cap_w + 4, cap_h + 4)
    cap_rect = pygame.Rect(2 * SS, 2 * SS, cap_w * SS, cap_h * SS)
    pygame.draw.ellipse(big, (130, 20, 30), cap_rect.inflate(SS * 2, SS * 2))
    pygame.draw.ellipse(big, (230, 50, 55), cap_rect)
    pygame.draw.ellipse(big, (255, 100, 100),
                        pygame.Rect(cap_rect.x + 2 * SS, cap_rect.y + 2 * SS,
                                    cap_rect.width - 4 * SS, 7 * SS))
    pygame.draw.ellipse(big, (255, 200, 200),
                        pygame.Rect(cap_rect.x + 6 * SS, cap_rect.y + 2 * SS,
                                    cap_rect.width - 18 * SS, 3 * SS))
    _ss_blit(big, surf, cx - cap_w // 2 - 2, cy - cap_h + 2 + bob,
             cap_w + 4, cap_h + 4)

    # 2 small white spots on the cap (top-left + top-right of face)
    for sx_off, sy_off, sr in ((-12, -10, 2), (10, -11, 2)):
        pygame.draw.circle(surf, (210, 180, 200),
                           (cx + sx_off, cy + sy_off + bob), sr + 1)
        pygame.draw.circle(surf, (255, 255, 255),
                           (cx + sx_off, cy + sy_off + bob), sr)

    # ─── FACE on the lower half of the cap ───
    face_y = cy - 2 + bob

    # Pink blush cheeks
    for bx in (cx - 8, cx + 8):
        cheek = pygame.Surface((9, 5), pygame.SRCALPHA)
        pygame.draw.ellipse(cheek, (255, 130, 160, 170), cheek.get_rect())
        surf.blit(cheek, (bx - 4, face_y))

    # Big anime eyes: dark outline, bright pupils, two shine dots each
    eye_y = face_y - 1
    for ex in (cx - 5, cx + 5):
        if blink:
            # closed eye: small smiley arc
            pygame.draw.line(surf, (40, 20, 30),
                             (ex - 3, eye_y), (ex + 3, eye_y), 2)
        else:
            # iris dark + pupil
            pygame.draw.ellipse(surf, (30, 20, 35),
                                pygame.Rect(ex - 3, eye_y - 3, 6, 7))
            pygame.draw.ellipse(surf, (60, 30, 80),
                                pygame.Rect(ex - 2, eye_y - 2, 4, 5))
            # big shine
            pygame.draw.circle(surf, (255, 255, 255), (ex - 1, eye_y - 1), 1)
            # tiny lower shine
            pygame.draw.circle(surf, (255, 255, 255), (ex + 1, eye_y + 1), 1)

    # Smile — small upturned arc between the eyes
    pygame.draw.arc(surf, (40, 20, 30),
                    pygame.Rect(cx - 2, face_y + 1, 4, 4),
                    math.radians(200), math.radians(340), 2)


VARIANTS = {
    1: ("1 — witch-hat",  draw_v1_witchhat),
    2: ("2 — coral",      draw_v2_coral),
    3: ("3 — cluster",    draw_v3_cluster),
    4: ("4 — bell+veil",  draw_v4_bell_veil),
    5: ("5 — character",  draw_v5_face),
}
