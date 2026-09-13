"""Polish the v3 menu to extraordinary — 5 subtle refinement directions.

Each variant keeps the EXACT v3 layout (deep navy night sky + SKYBIT
gold-on-red title + POCKET SKY FLYER subtitle + orange divider + three
red-gradient pill buttons + BEST/TOP 10 twin panels + mountain
silhouettes) and pushes one polish axis. No new frames, no new
ornaments, no new themes — just better-rendered v3.

Output: 720x1280 PNGs (2x v3 canvas) for crisp display on web/mobile.
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

# 2x v3 canvas for higher-resolution mockups
SCALE = 2
W, H = 360 * SCALE, 640 * SCALE
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "menu_polish")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "game", "assets")
FONT_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
FONT_REG  = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")

# ── v3 canonical palette (mirrors game/hud.py:29-37) ────────────────────────
GOLD_BRIGHT   = (240, 192,  64)
GOLD_MUTED    = (216, 184,  85)
GOLD_DEEP     = (180, 130,  20)
RED_OUTLINE   = (168,  32,  16)
ORANGE_BORDER = (232, 104,  40)
BTN_TOP       = (200,  64,  24)
BTN_BOT       = (126,  28,   2)
PANEL_DARK    = ( 12,   8,  38)
NIGHT_DEEP    = (  6,   1,  21)
NIGHT_MID     = ( 22,  14,  58)
WHITE         = (245, 245, 245)
NEAR_BLACK    = ( 12,   8,  18)


def font(size, bold=True):
    return pygame.font.Font(FONT_BOLD if bold else FONT_REG, int(size * SCALE))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def gradient_v(surf, top, bot, rect=None):
    r = rect or surf.get_rect()
    for y in range(r.height):
        t = y / max(1, r.height - 1)
        c = lerp(top, bot, t)
        pygame.draw.line(surf, c, (r.x, r.y + y), (r.x + r.width - 1, r.y + y))


# ── v3 base elements (canonical recipes from game/hud.py) ───────────────────

def v3_title(surf, cx, cy, size=68):
    """Canonical SKYBIT — gold fill, red 3px-offset outline, dark shadow.
    Renders crisp at 2x because pygame freetype is vector-based."""
    f = font(size, True)
    img = f.render("SKYBIT", True, GOLD_BRIGHT)
    out = f.render("SKYBIT", True, RED_OUTLINE)
    sh  = f.render("SKYBIT", True, NEAR_BLACK)
    r = img.get_rect(center=(cx, cy))
    px = 3 * SCALE
    for ox, oy in [(-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)]:
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + 3 * SCALE, r.y + 5 * SCALE))
    surf.blit(img, r.topleft)
    return r


def v3_subtitle(surf, cx, cy, size=22):
    f = font(size, True)
    img = f.render("POCKET  SKY  FLYER", True, GOLD_BRIGHT)
    out = f.render("POCKET  SKY  FLYER", True, RED_OUTLINE)
    sh  = f.render("POCKET  SKY  FLYER", True, NEAR_BLACK)
    r = img.get_rect(center=(cx, cy))
    px = 2 * SCALE
    for ox, oy in [(-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)]:
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + 2 * SCALE, r.y + 3 * SCALE))
    surf.blit(img, r.topleft)
    return r


def v3_divider(surf, cy, width=140, color=ORANGE_BORDER, alpha=120):
    line = pygame.Surface((width * SCALE, 1 * SCALE), pygame.SRCALPHA)
    line.fill((*color, alpha))
    surf.blit(line, line.get_rect(center=(W // 2, cy)))


def v3_pill(surf, center, text, size=22, min_w=220, h=46,
            alpha=255, accent=ORANGE_BORDER):
    """v3 red-gradient pill with orange border + white text."""
    h *= SCALE
    f = font(size, True)
    img = f.render(text, True, WHITE)
    w = max(min_w * SCALE, img.get_width() + 44 * SCALE)
    pill = pygame.Surface((w, h), pygame.SRCALPHA)
    # Gradient
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = lerp(BTN_TOP, BTN_BOT, t)
        pygame.draw.line(pill, (*c, 255), (0, yy), (w, yy))
    # Mask
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=h // 2)
    pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Border
    pygame.draw.rect(pill, (*accent, 255), (0, 0, w, h), width=2 * SCALE,
                     border_radius=h // 2)
    # Top sheen
    pygame.draw.line(pill, (255, 255, 255, 40), (h // 2, 2 * SCALE),
                     (w - h // 2, 2 * SCALE), 1 * SCALE)
    pill.set_alpha(alpha)
    cx, cy = center
    surf.blit(pill, (cx - w // 2, cy - h // 2))
    ir = img.get_rect(center=(cx, cy))
    surf.blit(img, ir.topleft)
    return pygame.Rect(cx - w // 2, cy - h // 2, w, h)


def v3_panel(surf, rect, label, value=None, with_trophy=False,
             border_alpha=80, accent=ORANGE_BORDER):
    """v3 dark-purple panel with a faint orange top-edge accent."""
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*PANEL_DARK, 190), (0, 0, rect.w, rect.h),
                     border_radius=14 * SCALE)
    pygame.draw.rect(pnl, (*accent, border_alpha),
                     (0, 0, rect.w, rect.h), width=1 * SCALE,
                     border_radius=14 * SCALE)
    accent_strip = pygame.Surface((rect.w - 28 * SCALE, 2), pygame.SRCALPHA)
    accent_strip.fill((*accent, 80))
    pnl.blit(accent_strip, (14 * SCALE, 3))
    surf.blit(pnl, rect.topleft)
    lf = font(12, False).render(label, True, GOLD_MUTED)
    lf.set_alpha(180)
    surf.blit(lf, lf.get_rect(center=(rect.centerx, rect.y + 14 * SCALE)))
    if value is not None:
        vf = font(22, True).render(str(value), True, GOLD_BRIGHT)
        surf.blit(vf, vf.get_rect(center=(rect.centerx, rect.y + 34 * SCALE)))
    if with_trophy:
        draw_trophy(surf, rect.centerx, rect.y + 36 * SCALE, 9 * SCALE)


def draw_trophy(surf, cx, cy, size):
    """Procedural gold trophy — same shape as game/hud.py:_draw_trophy."""
    s = size
    cup_top_y = cy - s + int(2 * SCALE)
    cup_bot_y = cy + int(2 * SCALE)
    pts = [(cx - s, cup_top_y), (cx + s, cup_top_y),
           (cx + s - 3, cup_bot_y), (cx - s + 3, cup_bot_y)]
    pygame.draw.polygon(surf, GOLD_BRIGHT, pts)
    pygame.draw.polygon(surf, GOLD_DEEP, pts, 1)
    # Handles
    h_w = max(4, s // 4)
    pygame.draw.arc(surf, GOLD_BRIGHT,
                    (cx - s - h_w, cup_top_y + 2, h_w * 2, s),
                    math.pi / 2, math.pi * 3 / 2, 2)
    pygame.draw.arc(surf, GOLD_BRIGHT,
                    (cx + s - h_w, cup_top_y + 2, h_w * 2, s),
                    -math.pi / 2, math.pi / 2, 2)
    # Stem + base
    sw = max(3, s // 5)
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - sw // 2, cup_bot_y, sw, s // 2))
    bw = s * 2
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - bw // 2, cup_bot_y + s // 2, bw, max(2, s // 4)))
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - bw // 2 - 2, cup_bot_y + s // 2 + max(2, s // 4),
                      bw + 4, max(2, s // 5)))


# ── Mountain silhouettes (v3 polygon shape, scaled) ─────────────────────────

def mountains(surf, alpha=200, layers=2, atmospheric_haze=False):
    """Two-layer (or three-layer) parallax mountain silhouette."""
    # Scale all v3 mountain points by SCALE
    far_pts = [(0, 640), (0, 490), (60, 420), (120, 450), (200, 375),
               (280, 430), (360, 360), (360, 400), (360, 640)]
    near_pts = [(0, 640), (0, 530), (80, 505), (160, 520), (240, 490),
                (320, 510), (360, 495), (360, 640)]
    if layers == 3:
        # Add a deepest layer behind for atmospheric depth
        deepest = [(0, 640), (0, 460), (50, 410), (110, 430), (170, 380),
                   (230, 415), (290, 380), (360, 410), (360, 640)]
        scaled = [(x * SCALE, y * SCALE) for x, y in deepest]
        col = (18, 28, 60) if atmospheric_haze else (14, 26, 50)
        m = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(m, (*col, alpha - 60), scaled)
        surf.blit(m, (0, 0))
    scaled_far = [(x * SCALE, y * SCALE) for x, y in far_pts]
    scaled_near = [(x * SCALE, y * SCALE) for x, y in near_pts]
    m = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(m, (14, 26, 50, alpha), scaled_far)
    pygame.draw.polygon(m, (10, 18, 36, alpha), scaled_near)
    surf.blit(m, (0, 0))
    if atmospheric_haze:
        # Soft horizontal haze band where mountains meet the sky
        haze = pygame.Surface((W, 80 * SCALE), pygame.SRCALPHA)
        for yy in range(80 * SCALE):
            a = int(34 * (1 - yy / (80 * SCALE)))
            pygame.draw.line(haze, (60, 90, 140, a), (0, yy), (W, yy))
        surf.blit(haze, (0, 360 * SCALE))


# ── Base v3 background (sky + stars + cloud puffs) ──────────────────────────

def v3_base_sky(surf, density=1.0, big_stars=False):
    gradient_v(surf, NIGHT_DEEP, NIGHT_MID)
    # Stars
    random.seed(42)
    n = int(120 * density)
    for _ in range(n):
        x = random.randint(0, W - 1)
        y = random.randint(0, int(380 * SCALE))
        r = random.choice([1, 1, 1, 2]) * SCALE
        a = random.randint(120, 255)
        d = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(d, (240, 240, 250, a), (r + 1, r + 1), r)
        surf.blit(d, (x - r - 1, y - r - 1))
    if big_stars:
        # A few cross-flared sparkle stars for premium polish
        for cx, cy in [(40, 100), (320, 80), (50, 250), (310, 230), (180, 50)]:
            cx *= SCALE; cy *= SCALE
            r = 3 * SCALE
            pygame.draw.circle(surf, (255, 250, 230), (cx, cy), r)
            for dx, dy in [(-9 * SCALE, 0), (9 * SCALE, 0),
                           (0, -9 * SCALE), (0, 9 * SCALE)]:
                pygame.draw.aaline(surf, (255, 250, 230, 200),
                                   (cx, cy), (cx + dx, cy + dy))
    # Cloud puffs (faint, navy-tinted)
    for cx, cy, cw in [(60, 90, 100), (260, 70, 110), (320, 160, 80)]:
        cs = pygame.Surface((cw * SCALE, 30 * SCALE), pygame.SRCALPHA)
        pygame.draw.ellipse(cs, (40, 30, 70, 80), (0, 0, cw * SCALE, 28 * SCALE))
        pygame.draw.ellipse(cs, (50, 36, 78, 100),
                            (cw * SCALE // 4, 4 * SCALE,
                             cw * SCALE - cw * SCALE // 2, 20 * SCALE))
        surf.blit(cs, (cx * SCALE - cw * SCALE // 2, cy * SCALE - 14 * SCALE))


# ── Twin BEST + TOP 10 panels — canonical v3 layout (scaled) ─────────────────

def v3_bottom_panels(surf, accent=ORANGE_BORDER, border_alpha=80):
    panel_w = 132 * SCALE
    gap = 8 * SCALE
    total = panel_w * 2 + gap
    left_x = (W - total) // 2
    cy = H - 86 * SCALE
    # BEST
    best_rect = pygame.Rect(left_x, cy - 24 * SCALE, panel_w, 48 * SCALE)
    v3_panel(surf, best_rect, "B E S T", value="42",
             border_alpha=border_alpha, accent=accent)
    # TOP 10
    top_rect = pygame.Rect(left_x + panel_w + gap, cy - 24 * SCALE,
                           panel_w, 48 * SCALE)
    v3_panel(surf, top_rect, "T O P  10", with_trophy=True,
             border_alpha=border_alpha, accent=accent)


# ── The 3 pills + their layout — canonical v3 vertical stacking ─────────────

def v3_pills(surf, primary_kwargs=None, accent=ORANGE_BORDER):
    primary_kwargs = primary_kwargs or {}
    # v3 places the three pills above the bottom panels; the primary is
    # the brightest and bottom of the trio is anchored 14 px above
    # the BEST/TOP 10 row.
    primary_y = 280 * SCALE
    spacing = 60 * SCALE
    v3_pill(surf, (W // 2, primary_y), "TAP TO START",
            size=22, min_w=220, h=48, accent=accent, **primary_kwargs)
    v3_pill(surf, (W // 2, primary_y + spacing), "HOW TO PLAY",
            size=18, min_w=220, h=42, accent=accent)
    v3_pill(surf, (W // 2, primary_y + 2 * spacing), "POWER-UPS",
            size=18, min_w=220, h=42, accent=accent)


def save(name, surf):
    out = os.path.join(OUT, name)
    pygame.image.save(surf, out)
    print(f"  wrote {out} ({W}x{H})")


# ─────────────────────────────────────────────────────────────────────────────
# POLISH 1 — CINEMATIC SKY  (deeper atmosphere, 3 mountain layers, soft moon)
# ─────────────────────────────────────────────────────────────────────────────
def polish_1_cinematic_sky():
    s = pygame.Surface((W, H))
    # Deeper, more atmospheric gradient — keeps v3 navy tones but
    # adds a hint of warmth low in the sky (just before mountains)
    stops = [(4, 0, 16), (16, 10, 48), (30, 22, 76), (40, 28, 70)]
    seg = H // (len(stops) - 1)
    for i in range(len(stops) - 1):
        for y in range(seg):
            t = y / max(1, seg - 1)
            c = lerp(stops[i], stops[i + 1], t)
            pygame.draw.line(s, c, (0, i * seg + y), (W, i * seg + y))

    # Soft full moon top-right (very subtle, not a focal hero)
    moon_cx, moon_cy = 320 * SCALE, 80 * SCALE
    glow = pygame.Surface((110 * SCALE, 110 * SCALE), pygame.SRCALPHA)
    for r in range(50 * SCALE, 0, -2 * SCALE):
        a = int(28 * (1 - r / (50 * SCALE)))
        pygame.draw.circle(glow, (255, 235, 200, a),
                           (55 * SCALE, 55 * SCALE), r)
    s.blit(glow, (moon_cx - 55 * SCALE, moon_cy - 55 * SCALE))
    pygame.draw.circle(s, (250, 245, 220), (moon_cx, moon_cy), 14 * SCALE)
    pygame.draw.circle(s, (220, 215, 195),
                       (moon_cx + 4 * SCALE, moon_cy - 2 * SCALE), 11 * SCALE)

    # Premium stars: 4 size tiers, twinkle halos on big ones
    random.seed(42)
    for _ in range(180):
        x = random.randint(0, W - 1)
        y = random.randint(0, 380 * SCALE)
        tier = random.choices([0, 1, 2, 3], weights=[60, 25, 10, 5])[0]
        r = (1 + tier) * SCALE
        a = random.randint(140, 255)
        if tier >= 2:
            # Halo on bigger stars
            halo = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(halo, (220, 230, 255, 60),
                               (r * 2, r * 2), r * 2)
            s.blit(halo, (x - r * 2, y - r * 2))
        d = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(d, (240, 240, 250, a), (r + 1, r + 1), r)
        s.blit(d, (x - r - 1, y - r - 1))

    # Refined cloud puffs (slightly more transparent + softer edges)
    for cx, cy, cw in [(60, 90, 100), (260, 70, 110), (320, 160, 80)]:
        cs = pygame.Surface((cw * SCALE, 36 * SCALE), pygame.SRCALPHA)
        # Multi-layer puff
        for rr, dy in [(cw // 2, 18), (cw // 3, 14), (cw // 4, 10)]:
            for j in range(rr, 0, -2):
                a = int(20 * (1 - j / rr))
                pygame.draw.ellipse(cs, (50, 36, 78, a),
                                    (cw * SCALE // 2 - j * SCALE,
                                     dy * SCALE - j * SCALE // 2,
                                     j * 2 * SCALE, j * SCALE))
        s.blit(cs, (cx * SCALE - cw * SCALE // 2, cy * SCALE - 18 * SCALE))

    # Title — canonical v3, with a subtle moonlight rim on top edge
    r = v3_title(s, W // 2, 126 * SCALE, size=72)
    moon_rim = font(72, True).render("SKYBIT", True, (200, 220, 255))
    moon_rim.set_alpha(40)
    s.blit(moon_rim, (r.x, r.y - 1 * SCALE))
    v3_subtitle(s, W // 2, 184 * SCALE, size=22)
    v3_divider(s, 208 * SCALE, width=140)

    # 3 mountain layers with atmospheric haze
    mountains(s, alpha=200, layers=3, atmospheric_haze=True)

    v3_pills(s)
    v3_bottom_panels(s)
    save("polish_1_cinematic_sky.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# POLISH 2 — REFINED GLASS  (glassy pills + glassmorphic panels)
# ─────────────────────────────────────────────────────────────────────────────
def polish_2_refined_glass():
    s = pygame.Surface((W, H))
    v3_base_sky(s, density=1.2, big_stars=True)
    mountains(s, alpha=200, layers=2)

    # Title — canonical
    v3_title(s, W // 2, 126 * SCALE, size=72)
    v3_subtitle(s, W // 2, 184 * SCALE, size=22)
    v3_divider(s, 208 * SCALE, width=140)

    # Pills with glass treatment — same red gradient, plus inner glow +
    # soft drop shadow + frost highlight on top edge
    def glass_pill(center, text, size, min_w, h):
        h *= SCALE
        f = font(size, True)
        img = f.render(text, True, WHITE)
        w = max(min_w * SCALE, img.get_width() + 44 * SCALE)
        # Soft drop shadow — a single rounded-rect copy of the pill,
        # offset down + slightly larger, low alpha. No expanding stack
        # (that produces angular bleed-through).
        sh_off = 8 * SCALE
        sh_w = w + 4 * SCALE
        sh_h = h + 4 * SCALE
        shadow = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 70), (0, 0, sh_w, sh_h),
                         border_radius=sh_h // 2)
        s.blit(shadow, (center[0] - sh_w // 2,
                        center[1] - sh_h // 2 + sh_off))
        # Pill body — v3 red gradient, fully opaque
        pill = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = lerp(BTN_TOP, BTN_BOT, t)
            pygame.draw.line(pill, (*c, 255), (0, yy), (w, yy))
        # Frost overlay on its own surface (so it BLITS with proper
        # alpha blending rather than replacing pill pixels)
        frost = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h // 2):
            a = int(55 * (1 - yy / (h / 2)))
            pygame.draw.line(frost, (255, 255, 255, a), (0, yy), (w, yy))
        pill.blit(frost, (0, 0))
        # Rounded mask clips both layers at once
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                         border_radius=h // 2)
        pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Border
        pygame.draw.rect(pill, ORANGE_BORDER, (0, 0, w, h),
                         width=2 * SCALE, border_radius=h // 2)
        s.blit(pill, (center[0] - w // 2, center[1] - h // 2))
        # Text
        ir = img.get_rect(center=center)
        sh = f.render(text, True, NEAR_BLACK)
        sh.set_alpha(160)
        s.blit(sh, (ir.x + 1 * SCALE, ir.y + 2 * SCALE))
        s.blit(img, ir.topleft)

    primary_y = 280 * SCALE
    spacing = 60 * SCALE
    glass_pill((W // 2, primary_y), "TAP TO START", 22, 220, 48)
    glass_pill((W // 2, primary_y + spacing), "HOW TO PLAY", 18, 220, 42)
    glass_pill((W // 2, primary_y + 2 * spacing), "POWER-UPS", 18, 220, 42)

    # Glassmorphic BEST + TOP 10 panels — much more transparent + subtle inner glow
    panel_w = 132 * SCALE
    gap = 8 * SCALE
    total = panel_w * 2 + gap
    left_x = (W - total) // 2
    cy = H - 86 * SCALE

    def glass_panel(rect, label, value=None, with_trophy=False):
        pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
        # Translucent dark fill (lower alpha)
        pygame.draw.rect(pnl, (*PANEL_DARK, 130), (0, 0, rect.w, rect.h),
                         border_radius=14 * SCALE)
        # Inner glow
        glow_r = pygame.Surface(rect.size, pygame.SRCALPHA)
        for r in range(8 * SCALE, 0, -SCALE):
            a = int(20 * r / (8 * SCALE))
            pygame.draw.rect(glow_r, (255, 230, 180, a),
                             (4 * SCALE, 4 * SCALE,
                              rect.w - 8 * SCALE, rect.h - 8 * SCALE),
                             border_radius=10 * SCALE)
        pnl.blit(glow_r, (0, 0))
        # Frosted top strip
        frost = pygame.Surface((rect.w, rect.h // 2), pygame.SRCALPHA)
        for yy in range(rect.h // 2):
            a = int(35 * (1 - yy / (rect.h / 2)))
            pygame.draw.line(frost, (255, 255, 255, a), (0, yy), (rect.w, yy))
        fm = pygame.Surface((rect.w, rect.h // 2), pygame.SRCALPHA)
        pygame.draw.rect(fm, (255, 255, 255, 255),
                         (0, -rect.h // 2, rect.w, rect.h),
                         border_radius=14 * SCALE)
        frost.blit(fm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pnl.blit(frost, (0, 0))
        # Border — light gold to read as glass-rim
        pygame.draw.rect(pnl, (240, 192, 64, 180),
                         (0, 0, rect.w, rect.h), width=1 * SCALE,
                         border_radius=14 * SCALE)
        s.blit(pnl, rect.topleft)
        lf = font(12, False).render(label, True, GOLD_MUTED)
        lf.set_alpha(220)
        s.blit(lf, lf.get_rect(center=(rect.centerx, rect.y + 14 * SCALE)))
        if value:
            vf = font(22, True).render(value, True, GOLD_BRIGHT)
            s.blit(vf, vf.get_rect(center=(rect.centerx, rect.y + 34 * SCALE)))
        if with_trophy:
            draw_trophy(s, rect.centerx, rect.y + 36 * SCALE, 9 * SCALE)

    br = pygame.Rect(left_x, cy - 24 * SCALE, panel_w, 48 * SCALE)
    glass_panel(br, "B E S T", value="42")
    tr = pygame.Rect(left_x + panel_w + gap, cy - 24 * SCALE,
                     panel_w, 48 * SCALE)
    glass_panel(tr, "T O P  10", with_trophy=True)

    save("polish_2_refined_glass.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# POLISH 3 — STAGE LIGHT  (radial spotlight glow behind the title)
# ─────────────────────────────────────────────────────────────────────────────
def polish_3_stage_light():
    s = pygame.Surface((W, H))
    v3_base_sky(s, density=1.1)

    # Big subtle radial spotlight behind the title — warm gold halo,
    # very wide and very faint so it reads as ambient stage light
    halo = pygame.Surface((W, 300 * SCALE), pygame.SRCALPHA)
    for r in range(220 * SCALE, 0, -4 * SCALE):
        a = int(4 * (1 - r / (220 * SCALE)))  # very subtle
        pygame.draw.circle(halo, (255, 200, 100, a),
                           (W // 2, 150 * SCALE), r)
    s.blit(halo, (0, 0))

    # Rim light on mountain tops (very thin warm line)
    mountains(s, alpha=200, layers=2)
    rim = pygame.Surface((W, 6 * SCALE), pygame.SRCALPHA)
    for y in range(6 * SCALE):
        a = int(60 * (1 - y / (6 * SCALE)))
        pygame.draw.line(rim, (255, 200, 120, a), (0, y), (W, y))
    s.blit(rim, (0, 488 * SCALE))

    # Title
    v3_title(s, W // 2, 126 * SCALE, size=72)
    v3_subtitle(s, W // 2, 184 * SCALE, size=22)
    v3_divider(s, 208 * SCALE, width=140)

    # Pills with subtle drop shadow (depth)
    def shadowed_pill(center, text, size, min_w, h):
        # Drop shadow first
        h_px = h * SCALE
        f = font(size, True)
        w = max(min_w * SCALE, f.size(text)[0] + 44 * SCALE)
        sh_off = 6 * SCALE
        shadow = pygame.Surface((w + 4 * SCALE, h_px + sh_off),
                                pygame.SRCALPHA)
        for j in range(sh_off, 0, -SCALE):
            a = int(50 * j / sh_off)
            pygame.draw.rect(shadow, (0, 0, 0, a),
                             (2 * SCALE, j, w, h_px),
                             border_radius=h_px // 2)
        s.blit(shadow, (center[0] - w // 2 - 2 * SCALE,
                        center[1] - h_px // 2))
        v3_pill(s, center, text, size=size, min_w=min_w, h=h)

    primary_y = 280 * SCALE
    spacing = 60 * SCALE
    shadowed_pill((W // 2, primary_y), "TAP TO START", 22, 220, 48)
    shadowed_pill((W // 2, primary_y + spacing), "HOW TO PLAY", 18, 220, 42)
    shadowed_pill((W // 2, primary_y + 2 * spacing), "POWER-UPS", 18, 220, 42)

    v3_bottom_panels(s)
    save("polish_3_stage_light.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# POLISH 4 — LIVING SCENE  (Pip flying behind title + shooting star)
# ─────────────────────────────────────────────────────────────────────────────
def polish_4_living_scene():
    s = pygame.Surface((W, H))
    v3_base_sky(s, density=1.2, big_stars=True)

    # Shooting star streak top-left
    ss_x, ss_y = 70 * SCALE, 70 * SCALE
    for i in range(28):
        a = int(180 * (1 - i / 28))
        pygame.draw.line(s, (255, 250, 220, a),
                         (ss_x + i * 3 * SCALE, ss_y + i * 2 * SCALE),
                         (ss_x + (i + 1) * 3 * SCALE,
                          ss_y + (i + 1) * 2 * SCALE),
                         2 * SCALE)
    pygame.draw.circle(s, (255, 255, 230),
                       (ss_x + 28 * 3 * SCALE, ss_y + 28 * 2 * SCALE),
                       3 * SCALE)

    # Pip flying just below the subtitle, clearly visible in open sky
    pip_x = 280 * SCALE
    pip_y = 232 * SCALE
    # Body (scarlet)
    pygame.draw.ellipse(s, (220, 50, 50),
                        (pip_x - 12 * SCALE, pip_y - 9 * SCALE,
                         28 * SCALE, 18 * SCALE))
    # Tail
    pygame.draw.polygon(s, (200, 30, 30),
                        [(pip_x - 14 * SCALE, pip_y),
                         (pip_x - 28 * SCALE, pip_y - 5 * SCALE),
                         (pip_x - 24 * SCALE, pip_y + 5 * SCALE)])
    # Wing
    pygame.draw.polygon(s, (40, 100, 220),
                        [(pip_x - 2 * SCALE, pip_y - 4 * SCALE),
                         (pip_x + 8 * SCALE, pip_y - 16 * SCALE),
                         (pip_x + 14 * SCALE, pip_y - 4 * SCALE)])
    # Wing-tip green
    pygame.draw.polygon(s, (50, 220, 100),
                        [(pip_x + 8 * SCALE, pip_y - 16 * SCALE),
                         (pip_x + 14 * SCALE, pip_y - 13 * SCALE),
                         (pip_x + 14 * SCALE, pip_y - 4 * SCALE)])
    # Beak
    pygame.draw.polygon(s, (255, 200, 60),
                        [(pip_x + 14 * SCALE, pip_y - 2 * SCALE),
                         (pip_x + 22 * SCALE, pip_y),
                         (pip_x + 14 * SCALE, pip_y + 3 * SCALE)])
    # Sunglasses lens — small black square
    pygame.draw.rect(s, NEAR_BLACK,
                     (pip_x + 6 * SCALE, pip_y - 5 * SCALE,
                      6 * SCALE, 4 * SCALE))
    pygame.draw.line(s, GOLD_BRIGHT,
                     (pip_x + 6 * SCALE, pip_y - 5 * SCALE),
                     (pip_x + 12 * SCALE, pip_y - 5 * SCALE), 1)
    # Parcel trailing below
    pygame.draw.rect(s, (180, 130, 80),
                     (pip_x - 6 * SCALE, pip_y + 10 * SCALE,
                      12 * SCALE, 10 * SCALE))
    pygame.draw.line(s, (200, 50, 50),
                     (pip_x, pip_y + 10 * SCALE),
                     (pip_x, pip_y + 20 * SCALE), 2 * SCALE)
    # Motion trail dots
    for i in range(10):
        a = int(80 * (1 - i / 10))
        pygame.draw.circle(s, (240, 245, 255, a),
                           (pip_x - 18 * SCALE - i * 5 * SCALE,
                            pip_y - 2 * SCALE),
                           1 * SCALE)

    mountains(s, alpha=200, layers=2)

    # Title — canonical
    v3_title(s, W // 2, 126 * SCALE, size=72)
    v3_subtitle(s, W // 2, 184 * SCALE, size=22)
    v3_divider(s, 208 * SCALE, width=140)

    v3_pills(s)
    v3_bottom_panels(s)
    save("polish_4_living_scene.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# POLISH 5 — MICRO ORNAMENT  (tiny corner gold flourishes + refined details)
# ─────────────────────────────────────────────────────────────────────────────
def polish_5_micro_ornament():
    s = pygame.Surface((W, H))
    v3_base_sky(s, density=1.1, big_stars=True)
    mountains(s, alpha=200, layers=2)

    # Tiny gold corner flourishes — NOT a frame, just decorative corner marks
    # Each is a small L-shape with a dot, in the very corners
    def flourish(cx, cy, dx, dy):
        # L-shape in gold
        pygame.draw.line(s, GOLD_BRIGHT,
                         (cx, cy), (cx + dx * 18 * SCALE, cy), 2)
        pygame.draw.line(s, GOLD_BRIGHT,
                         (cx, cy), (cx, cy + dy * 18 * SCALE), 2)
        # Dot at the corner
        pygame.draw.circle(s, GOLD_BRIGHT, (cx, cy), 2 * SCALE)
        # Inner accent dot offset
        pygame.draw.circle(s, GOLD_DEEP,
                           (cx + dx * 8 * SCALE, cy + dy * 8 * SCALE),
                           1 * SCALE)

    pad = 22 * SCALE
    flourish(pad, pad, +1, +1)
    flourish(W - pad, pad, -1, +1)
    flourish(pad, H - pad, +1, -1)
    flourish(W - pad, H - pad, -1, -1)

    # Title — canonical
    v3_title(s, W // 2, 126 * SCALE, size=72)
    v3_subtitle(s, W // 2, 184 * SCALE, size=22)

    # Replace orange divider with a hairline gold underline (slightly more elegant)
    line = pygame.Surface((150 * SCALE, 1 * SCALE), pygame.SRCALPHA)
    line.fill((*GOLD_BRIGHT, 140))
    s.blit(line, line.get_rect(center=(W // 2, 208 * SCALE)))
    # Tiny diamond accent in the middle
    pygame.draw.polygon(s, GOLD_BRIGHT,
                        [(W // 2, 206 * SCALE),
                         (W // 2 + 4 * SCALE, 208 * SCALE),
                         (W // 2, 210 * SCALE),
                         (W // 2 - 4 * SCALE, 208 * SCALE)])

    # Pills — canonical v3, but with gold-tinted accent border (not orange)
    primary_y = 280 * SCALE
    spacing = 60 * SCALE
    v3_pill(s, (W // 2, primary_y), "TAP TO START",
            size=22, min_w=220, h=48, accent=GOLD_DEEP)
    v3_pill(s, (W // 2, primary_y + spacing), "HOW TO PLAY",
            size=18, min_w=220, h=42, accent=GOLD_DEEP)
    v3_pill(s, (W // 2, primary_y + 2 * spacing), "POWER-UPS",
            size=18, min_w=220, h=42, accent=GOLD_DEEP)

    # BEST + TOP 10 panels with gold accent (instead of orange)
    v3_bottom_panels(s, accent=GOLD_BRIGHT, border_alpha=120)

    save("polish_5_micro_ornament.png", s)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Generating 5 polished v3-menu mockups at {W}x{H}...")
    polish_1_cinematic_sky()
    polish_2_refined_glass()
    polish_3_stage_light()
    polish_4_living_scene()
    polish_5_micro_ornament()
    print("Done.")
