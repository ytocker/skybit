"""
Game entities: Bird, Pipe, Coin, Mushroom, Particle, FloatText.
All drawing is smooth (gradients, alpha, glows) — no pixel art.

Pipes are sandstone pillars topped with living vegetation, re-tinted by the
active biome palette. Coins are slow-rotating metallic gold discs with
embossed detail.
"""
import math
import random
import pygame

from game.config import (
    W, H, GRAVITY, FLAP_V, MAX_FALL,
    BIRD_X, BIRD_R, PIPE_W, COIN_R, MUSHROOM_R, GROUND_Y,
)
from game.draw import (
    blit_glow, draw_pillar_mist,
    rounded_rect, lerp_color,
    COIN_GOLD, COIN_DARK,
    MUSH_CAP, MUSH_CAP2, MUSH_SPOT, MUSH_STEM,
    PARTICLE_GOLD, PARTICLE_ORNG, PARTICLE_WHT, PARTICLE_CRIM,
    NEAR_BLACK, WHITE,
)
from game import parrot
from game.pillar_variants import draw_pillar_pair

# ── KFC logo sprite (lazy-loaded once at first draw) ─────────────────────────
_kfc_sprite: "pygame.Surface | None" = None

def _get_kfc_sprite() -> "pygame.Surface":
    global _kfc_sprite
    if _kfc_sprite is None:
        import os
        r         = MUSHROOM_R + 2
        logo_size = int(r * 2.4)
        path      = os.path.join(os.path.dirname(__file__), "assets", "kfc_logo.jpg")
        raw = pygame.image.load(path)
        # Crop to square (center crop on the wider axis)
        rw, rh = raw.get_size()
        side = min(rw, rh)
        crop = pygame.Surface((side, side))
        crop.blit(raw, (-(rw - side) // 2, -(rh - side) // 2))
        # Scale 38% larger so the white outer ring is pushed outside the circle mask
        zoomed_size = int(logo_size * 1.38)
        scaled = pygame.transform.smoothscale(crop, (zoomed_size, zoomed_size))
        # Convert to SRCALPHA so the circle mask can punch out corners
        logo = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
        offset = (logo_size - zoomed_size) // 2
        logo.blit(scaled, (offset, offset))
        mask = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255),
                           (logo_size // 2, logo_size // 2), logo_size // 2)
        logo.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        _kfc_sprite = logo
    return _kfc_sprite


# Default pillar palette (fallback when no biome provided).
_DEFAULT_PILLAR = {
    'stone_light':     (225, 195, 155),
    'stone_mid':       (175, 140, 105),
    'stone_dark':      (95, 70, 55),
    'stone_accent':    (255, 220, 170),
    'foliage_top':     (140, 220, 110),
    'foliage_mid':     (70, 170, 75),
    'foliage_dark':    (30, 100, 50),
    'foliage_accent':  (255, 240, 120),
}


# ── Bird ─────────────────────────────────────────────────────────────────────

class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = H * 0.42
        self.vy = 0.0
        self.alive = True
        self.frame_t = 0.0
        self.flap_boost = 0.0
        self.kfc_active = False
        self.ghost_active = False
        self.grow_active = False

    @property
    def tilt_deg(self):
        # Clamp the downward dive so a fast-falling bird doesn't read as
        # already crashing (REVIEW.md feedback).
        t = max(-0.5, min(0.75, self.vy / 500.0))
        return -t * 55.0

    def flap(self):
        if self.alive:
            self.vy = FLAP_V
            self.flap_boost = 0.45

    def update(self, dt):
        self.vy = min(self.vy + GRAVITY * dt, MAX_FALL)
        self.y += self.vy * dt

        base_hz = 9.0 + self.flap_boost * 20.0
        if self.vy < -100:
            base_hz += 3.0
        elif self.vy > 200:
            base_hz = max(3.0, base_hz - 4.0)
        self.frame_t = (self.frame_t + dt * base_hz)
        self.flap_boost = max(0.0, self.flap_boost - dt * 1.8)

    def draw(self, surf, shake_x=0, shake_y=0):
        frame_idx = int(self.frame_t) % len(parrot.FRAMES)
        if self.kfc_active:
            img = parrot.get_fried_parrot(frame_idx, self.tilt_deg)
        elif self.ghost_active:
            img = parrot.get_ghost_parrot(frame_idx, self.tilt_deg)
        else:
            img = parrot.get_parrot(frame_idx, self.tilt_deg)
        if self.grow_active:
            from game.config import GROW_SCALE
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * GROW_SCALE), int(h * GROW_SCALE)))
        r = img.get_rect(center=(self.x + shake_x, self.y + shake_y))
        surf.blit(img, r.topleft)


# ── Pipe (nature pillar) ─────────────────────────────────────────────────────

class Pipe:
    """Sandstone pillar column. Each instance picks one of 8 visual variants
    (original + 7 sketched picks) deterministically from its seed, so the
    vegetation and ornament arrangement is stable across frames."""

    def __init__(self, x: float, gap_y: float, gap_h: float):
        self.x = x
        self.gap_y = gap_y
        self.gap_h = gap_h
        self.scored = False
        self.is_rush = False
        # Per-instance random seed → chooses variant + stable decoration seed
        self.seed = random.randint(0, 0xFFFFFF)

    @property
    def top_rect(self):
        return pygame.Rect(int(self.x), 0, PIPE_W, int(self.gap_y - self.gap_h / 2))

    @property
    def bot_rect(self):
        top = int(self.gap_y + self.gap_h / 2)
        return pygame.Rect(int(self.x), top, PIPE_W, GROUND_Y - top)

    def off_screen(self):
        return self.x + PIPE_W + 8 < 0

    def collides_circle(self, cx, cy, r):
        return self.top_rect.colliderect(pygame.Rect(cx - r, cy - r, r * 2, r * 2)) or \
               self.bot_rect.colliderect(pygame.Rect(cx - r, cy - r, r * 2, r * 2))

    def draw(self, surf, palette=None):
        palette = palette or _DEFAULT_PILLAR
        draw_pillar_pair(surf, self.top_rect, self.bot_rect, palette, self.seed)
        # Mist halo at the base where the bottom pillar meets the ground
        bot = self.bot_rect
        draw_pillar_mist(surf, bot.x + bot.width // 2, bot.bottom, bot.width, alpha=110)


# ── Coin ─────────────────────────────────────────────────────────────────────

class Coin:
    """Slow-rotating gold parrot medallion, drawn with no halo or glow.

    Every frame the coin is drawn directly onto the target surface as an
    ellipse squeezed horizontally by |cos(spin)|. No cached face, no
    smoothscale blur, no radial aura — the silhouette you see is the
    silhouette you collect (COIN_R governs both).
    """

    SPIN_RATE = 1.1  # ≈ 5.7 seconds per full rotation

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spin = random.uniform(0, math.tau)
        self.collected = False
        self.float_t = random.uniform(0, math.tau)

    def update(self, dt):
        self.spin = (self.spin + dt * self.SPIN_RATE) % math.tau
        self.float_t += dt

    def draw(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.float_t * 2.2) * 2)
        cos_s = math.cos(self.spin)
        r = COIN_R
        rx = max(1, int(abs(cos_s) * r))

        if abs(cos_s) <= 0.35:
            # Edge-on sliver — a thin gold bar with dark rim, no detail.
            pygame.draw.ellipse(surf, COIN_DARK,
                                (cx - rx - 1, cy - r, (rx + 1) * 2, r * 2))
            pygame.draw.ellipse(surf, COIN_GOLD,
                                (cx - rx, cy - r, rx * 2, r * 2))
            return

        # Face-on: dark rim → gold body. Both are ellipses that share the
        # same horizontal squeeze, so the coin shape IS its silhouette.
        pygame.draw.ellipse(surf, COIN_DARK,
                            (cx - rx - 1, cy - r - 1,
                             (rx + 1) * 2, (r + 1) * 2))
        pygame.draw.ellipse(surf, COIN_GOLD,
                            (cx - rx, cy - r, rx * 2, r * 2))

        # Embossed parrot silhouette — only when mostly face-on so it
        # doesn't smear across a squeezed ellipse.
        if abs(cos_s) > 0.75:
            emboss = (140, 85, 0)
            pygame.draw.ellipse(surf, emboss, (cx - 2, cy - 1, 7, 5))     # body
            pygame.draw.circle(surf, emboss, (cx - 1, cy - 3), 3)         # head
            pygame.draw.polygon(surf, emboss,                              # hooked beak
                                [(cx - 3, cy - 3), (cx - 6, cy - 2), (cx - 3, cy - 1)])
            pygame.draw.circle(surf, COIN_GOLD, (cx, cy - 4), 1)          # eye


# ── PowerUp ──────────────────────────────────────────────────────────────────

class PowerUp:
    """A collectible buff. `kind` selects visuals and pickup effect:
       triple  — red mushroom, 3x coin value for TRIPLE_DURATION
       magnet  — red horseshoe, pulls coins in for MAGNET_DURATION
       slowmo  — purple hourglass, 0.5x world scroll for SLOWMO_DURATION
    """
    def __init__(self, x, y, kind="triple"):
        self.x = x
        self.y = y
        self.kind = kind
        self.collected = False
        self.pulse = 0.0

    def update(self, dt):
        self.pulse += dt * 3.5

    def draw(self, surf):
        if self.kind == "triple":
            self._draw_mushroom(surf)
        elif self.kind == "magnet":
            self._draw_magnet(surf)
        elif self.kind == "slowmo":
            self._draw_slowmo(surf)
        elif self.kind == "kfc":
            self._draw_kfc(surf)
        elif self.kind == "ghost":
            self._draw_ghost(surf)
        elif self.kind == "grow":
            self._draw_grow(surf)

    # ── sprite variants ─────────────────────────────────────────────────────
    def _draw_mushroom(self, surf):
        cx = int(self.x)
        cy = int(self.y)

        # Stem with vivid highlight
        stem = pygame.Rect(cx - 7, cy, 14, 13)
        rounded_rect(surf, stem, 5, MUSH_STEM, 255)
        pygame.draw.line(surf, (255, 255, 230), (cx - 4, cy + 2), (cx - 4, cy + 11), 2)
        pygame.draw.line(surf, (200, 180, 145), (cx + 3, cy + 2), (cx + 3, cy + 11), 1)
        # Stem base shadow
        sh = pygame.Surface((16, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 120), sh.get_rect())
        surf.blit(sh, (cx - 8, cy + 11))

        # Cap shadow (under)
        cap_rect = pygame.Rect(cx - MUSHROOM_R - 1, cy - MUSHROOM_R + 2, (MUSHROOM_R + 1) * 2, MUSHROOM_R + 5)
        sh = pygame.Surface((cap_rect.width + 8, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
        surf.blit(sh, (cap_rect.x - 4, cy - 2))

        # Cap base (deep crimson outline) then vivid red
        pygame.draw.ellipse(surf, (130, 10, 20), cap_rect.inflate(2, 2))
        pygame.draw.ellipse(surf, MUSH_CAP,     cap_rect)
        # Upper highlight arc (hot pink / orange)
        hi = pygame.Rect(cap_rect.x + 3, cap_rect.y + 2, cap_rect.width - 6, 7)
        pygame.draw.ellipse(surf, MUSH_CAP2, hi)
        # Specular sheen
        sh2 = pygame.Surface((cap_rect.width - 14, 3), pygame.SRCALPHA)
        pygame.draw.ellipse(sh2, (255, 230, 220, 200), sh2.get_rect())
        surf.blit(sh2, (cap_rect.x + 7, cap_rect.y + 3))

        # Spots with a soft ring so they read clearly
        for sx, sy, sr in ((cx - 7, cy - 5, 3),
                           (cx + 6, cy - 7, 4),
                           (cx + 2, cy + 1, 3),
                           (cx - 3, cy + 2, 2)):
            pygame.draw.circle(surf, (220, 190, 200), (sx, sy), sr + 1)
            pygame.draw.circle(surf, MUSH_SPOT,       (sx, sy), sr)

    def _draw_magnet(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.1) * 3)   # float bob

        outer_r = 13
        inner_r = 6
        arch_cy = cy - 3
        leg_bot = cy + 12

        # Drop shadow
        sh = pygame.Surface((outer_r * 3, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
        surf.blit(sh, (cx - outer_r - outer_r // 2, leg_bot + 4))

        # Build the horseshoe on an SRCALPHA scratch surface so the hollow
        # can be punched cleanly with alpha=0 overdraw.
        sz  = 42
        scx = sz // 2
        scy = outer_r + 4

        scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)

        # Dark shadow rim
        pygame.draw.circle(scratch, (80, 5, 8), (scx, scy), outer_r + 2)
        pygame.draw.rect(scratch, (80, 5, 8),
                         (scx - outer_r - 2, scy,
                          (outer_r + 2) * 2, leg_bot - arch_cy + 4))

        # Vivid crimson body
        RED_HI = (235, 35, 45)
        pygame.draw.circle(scratch, RED_HI, (scx, scy), outer_r + 1)
        pygame.draw.rect(scratch, RED_HI,
                         (scx - outer_r - 1, scy,
                          (outer_r + 1) * 2, leg_bot - arch_cy + 3))

        # Specular sheen across arch top
        sheen = pygame.Surface((outer_r * 2 - 2, outer_r - 1), pygame.SRCALPHA)
        pygame.draw.ellipse(sheen, (255, 160, 165, 140), sheen.get_rect())
        scratch.blit(sheen, (scx - outer_r + 1, 3))

        # Highlight rings
        pygame.draw.circle(scratch, (255, 95, 95), (scx, scy), inner_r + 1, 2)
        pygame.draw.circle(scratch, (255, 85, 85), (scx, scy), outer_r, 2)

        # Punch inner hollow
        pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), inner_r)
        # Punch gap between legs
        pygame.draw.rect(scratch, (0, 0, 0, 0),
                         (scx - inner_r, scy, inner_r * 2, sz - scy))

        surf.blit(scratch, (cx - scx, arch_cy - scy))

        # Chrome pole tips
        left_cx  = cx - inner_r - (outer_r - inner_r) // 2
        right_cx = cx + inner_r + (outer_r - inner_r) // 2
        arm_w    = outer_r - inner_r
        for tip_cx in (left_cx, right_cx):
            pygame.draw.rect(surf, (40, 42, 60),
                             (tip_cx - arm_w // 2 - 1, leg_bot - 4, arm_w + 2, 9),
                             border_radius=4)
            pygame.draw.rect(surf, (195, 210, 232),
                             (tip_cx - arm_w // 2,     leg_bot - 3, arm_w,     7),
                             border_radius=3)
            pygame.draw.rect(surf, (238, 246, 255),
                             (tip_cx - arm_w // 2 + 1, leg_bot - 3, arm_w - 2, 3),
                             border_radius=2)

        # Animated lightning arc between poles
        arc_y0  = leg_bot + 6
        arc_pts = [(left_cx, arc_y0)]
        for i in range(1, 6):
            t = i / 6
            x = int(left_cx + (right_cx - left_cx) * t)
            y = int(arc_y0 + math.sin(self.pulse * 11 + i * 1.7) * 4)
            arc_pts.append((x, y))
        arc_pts.append((right_cx, arc_y0))
        arc_surf = pygame.Surface((right_cx - left_cx + 8, 16), pygame.SRCALPHA)
        shifted = [(p[0] - left_cx + 4, p[1] - arc_y0 + 4) for p in arc_pts]
        if len(shifted) >= 2:
            pygame.draw.lines(arc_surf, (100, 195, 255, 200), False, shifted, 2)
        surf.blit(arc_surf, (left_cx - 4, arc_y0 - 4))

    def _draw_slowmo(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.7) * 3)
        R = MUSHROOM_R  # 14

        # Drop shadow
        sh_w = R * 2 + 6
        sh = pygame.Surface((sh_w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 75), sh.get_rect())
        surf.blit(sh, (cx - sh_w // 2, cy + R + 2))

        # Clock face on scratch SRCALPHA surface for clean edges
        PAD = 2
        D = (R + PAD) * 2
        g = pygame.Surface((D, D), pygame.SRCALPHA)
        gc = (D // 2, D // 2)

        # Outer shadow ring
        pygame.draw.circle(g, (15, 0, 35, 200), gc, R + 1)
        # Bezel: two rings for a bevelled metallic look
        pygame.draw.circle(g, (195, 135, 255, 255), gc, R)
        pygame.draw.circle(g, (130, 70, 195, 255), gc, R - 1)
        # Deep purple face
        pygame.draw.circle(g, (42, 10, 70, 255), gc, R - 2)
        # Slightly lighter inner face
        pygame.draw.circle(g, (62, 20, 98, 255), gc, R - 4)

        # Top-left specular highlight
        hl = pygame.Surface((D, D), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 230, 255, 60), (gc[0] - 2, gc[1] - 3), R - 5)
        g.blit(hl, (0, 0))

        # Tick marks: 4 major (every 3rd) + 8 minor
        for i in range(12):
            ang = math.pi * 2 * i / 12 - math.pi / 2
            major = (i % 3 == 0)
            r_out = R - 2
            r_in  = r_out - (3 if major else 2)
            x1 = gc[0] + math.cos(ang) * r_out
            y1 = gc[1] + math.sin(ang) * r_out
            x2 = gc[0] + math.cos(ang) * r_in
            y2 = gc[1] + math.sin(ang) * r_in
            col = (230, 200, 255, 240) if major else (165, 125, 210, 160)
            pygame.draw.line(g, col, (int(x1), int(y1)), (int(x2), int(y2)),
                             2 if major else 1)

        # Hour hand — short, thick, slow
        hr_ang = self.pulse * 0.15 - math.pi / 2
        hx = int(gc[0] + math.cos(hr_ang) * (R - 7))
        hy = int(gc[1] + math.sin(hr_ang) * (R - 7))
        pygame.draw.line(g, (250, 225, 255, 255), gc, (hx, hy), 3)

        # Minute hand — long, thinner
        min_ang = self.pulse * 1.1 - math.pi / 2
        mx = int(gc[0] + math.cos(min_ang) * (R - 4))
        my = int(gc[1] + math.sin(min_ang) * (R - 4))
        pygame.draw.line(g, (200, 155, 255, 255), gc, (mx, my), 2)

        # Sweep hand — thinnest, amber, fastest (adds drama)
        sec_ang = self.pulse * 3.8 - math.pi / 2
        sx = int(gc[0] + math.cos(sec_ang) * (R - 3))
        sy = int(gc[1] + math.sin(sec_ang) * (R - 3))
        pygame.draw.line(g, (255, 185, 60, 215), gc, (sx, sy), 1)

        # Center pin
        pygame.draw.circle(g, (255, 240, 255, 255), gc, 2)
        pygame.draw.circle(g, (155, 95, 220, 255), gc, 1)

        surf.blit(g, (cx - D // 2, cy - D // 2))


    def _draw_kfc(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 0.9) * 2.5)
        r  = MUSHROOM_R + 2

        # Drop shadow
        sh_w = int(r * 2.8)
        sh = pygame.Surface((sh_w, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 80), sh.get_rect())
        surf.blit(sh, (cx - sh_w // 2, cy + r + 2))

        # KFC logo (real image, pre-scaled & circle-clipped)
        logo = _get_kfc_sprite()
        surf.blit(logo, (cx - logo.get_width() // 2, cy - logo.get_height() // 2))

    def _draw_ghost(self, surf):
        cx = int(self.x)
        # Supernatural wafting bob: two overlaid frequencies
        cy = int(self.y + math.sin(self.pulse * 0.9) * 4
                        + math.sin(self.pulse * 1.8) * 1.5)

        DARK     = (32,  52, 120, 255)
        BODY     = (205, 228, 255, 235)
        EYE_W    = (252, 254, 255, 255)
        EYE_IRIS = (50,  110, 220, 255)
        EYE_PUP  = (12,  18,  60,  255)

        # Drop shadow
        sh = pygame.Surface((32, 7), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 70), sh.get_rect())
        surf.blit(sh, (cx - 16, cy + 19))

        # ── Classic ghost silhouette on scratch SRCALPHA surface ──────────────
        # 28 × 36 px sprite; head centre at local (14, 12).
        GW, GH   = 28, 36
        gcx      = GW // 2    # 14
        gcy      = 12         # head-circle centre y
        hr       = 12         # head radius
        body_y2  = 26         # y where straight sides end, scallop starts

        # Scalloped-skirt polygon: 3 hanging bumps with 2 concave indents.
        scallop = [
            (1,        body_y2),
            (6,        GH - 4),          # left bump
            (11,       body_y2 + 4),     # indent 1
            (gcx,      GH - 4),          # centre bump
            (GW - 12,  body_y2 + 4),     # indent 2
            (GW - 7,   GH - 4),          # right bump
            (GW - 2,   body_y2),
        ]
        # Expanded by 1 px for the outline pass
        scallop_o = [
            (0,        body_y2),
            (6,        GH - 3),
            (10,       body_y2 + 4),
            (gcx,      GH - 3),
            (GW - 11,  body_y2 + 4),
            (GW - 7,   GH - 3),
            (GW,       body_y2),
        ]

        g = pygame.Surface((GW, GH), pygame.SRCALPHA)

        # Outline pass
        pygame.draw.circle(g, DARK, (gcx, gcy), hr + 1)
        pygame.draw.rect(g, DARK, (0, gcy, GW, body_y2 - gcy + 1))
        pygame.draw.polygon(g, DARK, scallop_o)

        # Body fill
        pygame.draw.circle(g, BODY, (gcx, gcy), hr)
        pygame.draw.rect(g, BODY, (1, gcy, GW - 2, body_y2 - gcy))
        pygame.draw.polygon(g, BODY, scallop)

        # Eyes: white → iris → pupil → specular dot
        for ex in (gcx - 5, gcx + 5):
            ey = gcy - 1
            pygame.draw.circle(g, EYE_W,    (ex,     ey    ), 4)
            pygame.draw.circle(g, EYE_IRIS, (ex + 1, ey + 1), 3)
            pygame.draw.circle(g, EYE_PUP,  (ex + 1, ey + 1), 1)
            pygame.draw.circle(g, (255, 255, 255, 200), (ex - 1, ey - 2), 1)

        # Blit: head-circle centre aligns with (cx, cy)
        surf.blit(g, (cx - gcx, cy - gcy))


    def _draw_grow(self, surf):
        cx = int(self.x)
        cy = int(self.y + math.sin(self.pulse * 1.2) * 2)

        # Tiny parrot silhouette in the centre — simplified macaw face/body.
        BIRD_BODY  = (240,  55,  55)
        BIRD_BELLY = (255, 130,  90)
        BIRD_BEAK  = (255, 195,  60)
        BIRD_WING  = ( 40, 100, 255)
        BIRD_OUT   = ( 80,  10,  18)
        SHADES     = ( 20,  18,  30)

        # Body ellipse + 1px outline
        body_rect = pygame.Rect(cx - 8, cy - 6, 16, 14)
        pygame.draw.ellipse(surf, BIRD_OUT,  body_rect.inflate(2, 2))
        pygame.draw.ellipse(surf, BIRD_BODY, body_rect)
        # Belly highlight
        pygame.draw.ellipse(surf, BIRD_BELLY, pygame.Rect(cx - 4, cy - 1, 9, 6))
        # Wing tick (blue patch)
        pygame.draw.circle(surf, BIRD_OUT,  (cx + 2, cy + 1), 4)
        pygame.draw.circle(surf, BIRD_WING, (cx + 2, cy + 1), 3)
        # Aviator sunglasses bar across the eye line
        pygame.draw.rect(surf, SHADES, (cx - 6, cy - 4, 11, 3), border_radius=1)
        # Beak hooked downward
        pygame.draw.polygon(surf, BIRD_OUT,
                            [(cx - 9, cy - 1), (cx - 12, cy + 1), (cx - 8, cy + 2)])
        pygame.draw.polygon(surf, BIRD_BEAK,
                            [(cx - 9, cy - 1), (cx - 11, cy + 1), (cx - 8, cy + 1)])

        # Two upward green chevrons flanking the bird, oscillating ±2px.
        ARROW_HI  = (50, 220, 100)
        ARROW_OUT = (28, 160,  70)
        oy = int(math.sin(self.pulse * 2.4) * 2)
        for sign in (-1, 1):
            ax = cx + sign * 14
            ay = cy + oy
            outline = [
                (ax,     ay - 9),
                (ax + 6, ay - 2),
                (ax + 3, ay - 2),
                (ax + 3, ay + 6),
                (ax - 3, ay + 6),
                (ax - 3, ay - 2),
                (ax - 6, ay - 2),
            ]
            pygame.draw.polygon(surf, ARROW_OUT, outline)
            inner = [
                (ax,     ay - 7),
                (ax + 4, ay - 3),
                (ax + 2, ay - 3),
                (ax + 2, ay + 5),
                (ax - 2, ay + 5),
                (ax - 2, ay - 3),
                (ax - 4, ay - 3),
            ]
            pygame.draw.polygon(surf, ARROW_HI, inner)


# Back-compat alias — some callers (e.g. snapshot/playtest scripts) still say Mushroom.
Mushroom = PowerUp


# ── Particle ─────────────────────────────────────────────────────────────────

class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "life_max", "r", "color", "gravity")

    def __init__(self, x, y, vx, vy, life, r, color, gravity=900.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.life_max = life
        self.r = r
        self.color = color
        self.gravity = gravity

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)
        a = int(255 * t)
        rr = max(1, int(self.r * (0.4 + 0.6 * t)))
        s = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, a), (rr + 1, rr + 1), rr)
        surf.blit(s, (int(self.x - rr - 1), int(self.y - rr - 1)), special_flags=pygame.BLEND_ADD)


# ── CloudPuff ────────────────────────────────────────────────────────────────

class CloudPuff:
    """Expanding, fading cloud circle for the transformation poof effect.
    Uses normal alpha blend (not additive) so it looks like white smoke."""
    __slots__ = ("x", "y", "vx", "vy", "life", "life_max", "r_start", "r_end", "color")

    def __init__(self, x, y, vx, vy, life, r_start, r_end, color):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.life = self.life_max = life
        self.r_start, self.r_end = r_start, r_end
        self.color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)          # 1→0 as puff dies
        alpha = int(200 * t)
        r = max(1, int(self.r_start + (self.r_end - self.r_start) * (1.0 - t)))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r + 1, r + 1), r)
        surf.blit(s, (int(self.x - r - 1), int(self.y - r - 1)))


# ── FloatText ────────────────────────────────────────────────────────────────

_float_font_cache: dict = {}

import os as _os

_FLOAT_FONT_DIR = _os.path.join(_os.path.dirname(__file__), "assets")
_FLOAT_BOLD = _os.path.join(_FLOAT_FONT_DIR, "LiberationSans-Bold.ttf")
_FLOAT_REG  = _os.path.join(_FLOAT_FONT_DIR, "LiberationSans-Regular.ttf")


def _get_float_font(size, bold=True):
    key = (size, bold)
    f = _float_font_cache.get(key)
    if f is None:
        path = _FLOAT_BOLD if bold else _FLOAT_REG
        f = pygame.font.Font(path, size)
        _float_font_cache[key] = f
    return f


class FloatText:
    __slots__ = ("text", "x", "y", "vy", "life", "life_max", "color", "size")

    def __init__(self, text, x, y, color, size=22, life=1.0, vy=-60):
        self.text = text
        self.x = x
        self.y = y
        self.vy = vy
        self.life = life
        self.life_max = life
        self.color = color
        self.size = size

    def update(self, dt):
        self.y += self.vy * dt
        self.vy += 40.0 * dt
        self.life -= dt

    def alive(self):
        return self.life > 0

    def draw(self, surf):
        t = max(0.0, self.life / self.life_max)
        a = int(255 * min(1.0, t * 2))
        font = _get_float_font(self.size)
        shadow = font.render(self.text, True, NEAR_BLACK)
        text = font.render(self.text, True, self.color)
        shadow.set_alpha(a)
        text.set_alpha(a)
        r = text.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(shadow, (r.x + 2, r.y + 2))
        surf.blit(text, r.topleft)
