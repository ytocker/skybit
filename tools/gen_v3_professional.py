"""Generate a single professionally polished version of the current
v3 menu at 720x1280.

NOT a redesign. The exact v3 layout — deep navy night sky + SKYBIT
gold-on-red title + POCKET SKY FLYER subtitle + 3 red-gradient pill
buttons + BEST + TOP 10 twin panels + mountain silhouettes — held in
place. What changes is *execution quality*:

  Alignment fixes
  ───────────────
  * Colour palette held strictly to the canonical Skybit values
    (gold #F0C040 / orange #E86828 / red #A82010 / panel #0C0826).
    No ad-hoc tints.
  * Pill text: WHITE with a consistent 2-px dark-red drop shadow +
    a faint cream halo for a premium readable hierarchy.
  * Subtitle, BEST/TOP 10 labels, trophy: all locked to a single
    gold scale (BRIGHT for values, MUTED for labels) — no
    drifting tones.
  * Divider, top-of-panel accent strip, top of subtitle group all
    use the same orange `#E86828` at the same low alpha (60) so
    every minor accent line reads as one system.

  Premium polish
  ──────────────
  * 4-tier star rendering with subtle halos on the largest stars.
  * 3 mountain layers + a faint warm horizon haze where the
    silhouette meets the sky (gives depth without changing colours).
  * Pills gain a subtle inner top-edge frost highlight + a slim
    bottom-edge inner shadow for tactile depth.
  * Each pill also sits on a soft drop shadow, lifting it off the
    sky.
  * BEST + TOP 10 panels gain a hairline top-edge highlight + a
    deeper drop shadow underneath for the same lift.
  * Cloud puffs softened to multi-layer alpha so they feel like
    distant haze rather than blobby ellipses.

Output: docs/menu_polish/v3_professional.png  (720 x 1280)
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

SCALE = 2
W, H = 360 * SCALE, 640 * SCALE
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "menu_polish")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "game", "assets")
FONT_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
FONT_REG  = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")

# ── Skybit canonical palette — strict, no ad-hoc variations ─────────────────
GOLD_BRIGHT   = (240, 192,  64)
GOLD_MUTED    = (216, 184,  85)
GOLD_DEEP     = (180, 130,  20)
RED_OUTLINE   = (168,  32,  16)
RED_DEEP      = ( 90,  18,   8)
ORANGE_BORDER = (232, 104,  40)
# Pill body — refined wine/burgundy that sits in the night palette
# instead of popping out as a bright orange-red.
BTN_TOP       = (108,  32,  46)
BTN_BOT       = ( 54,  14,  26)
# Tertiary cream for pill text — premium, warm white that ties to the
# canonical gold without losing readability on the dark pill body.
PILL_TEXT     = (250, 238, 210)
PANEL_DARK    = ( 12,   8,  38)
NIGHT_DEEP    = (  6,   1,  21)
NIGHT_MID     = ( 22,  14,  58)
WHITE         = (245, 245, 245)
CREAM         = (250, 232, 196)
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


# ── Sky, stars, clouds, horizon haze, mountains ─────────────────────────────

def sky_with_stars(surf):
    gradient_v(surf, NIGHT_DEEP, NIGHT_MID)
    # 4-tier stars with halos on big ones
    random.seed(42)
    for _ in range(220):
        x = random.randint(0, W - 1)
        y = random.randint(0, int(420 * SCALE))
        tier = random.choices([0, 1, 2, 3], weights=[64, 24, 9, 3])[0]
        r = (1 + tier) * SCALE
        a = random.randint(140, 255)
        if tier >= 2:
            # Soft halo — multi-ring fall-off so it reads as glow not a circle
            halo = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
            for hr in range(r * 3, 0, -1):
                a = int(22 * (1 - hr / (r * 3)))
                pygame.draw.circle(halo, (220, 230, 255, a),
                                   (r * 3, r * 3), hr)
            surf.blit(halo, (x - r * 3, y - r * 3))
        d = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(d, (240, 240, 250, a), (r + 1, r + 1), r)
        surf.blit(d, (x - r - 1, y - r - 1))


def clouds(surf):
    # Softer multi-layer alpha puffs
    for cx, cy, cw in [(60, 90, 110), (260, 70, 120), (320, 165, 86)]:
        cs = pygame.Surface((cw * SCALE, 36 * SCALE), pygame.SRCALPHA)
        for radius, dy in [(cw // 2, 18), (cw // 3, 12), (cw // 4, 8)]:
            for j in range(radius, 0, -2):
                a = int(18 * (1 - j / radius))
                pygame.draw.ellipse(
                    cs, (50, 38, 78, a),
                    (cw * SCALE // 2 - j * SCALE,
                     dy * SCALE - j * SCALE // 2,
                     j * 2 * SCALE, j * SCALE))
        surf.blit(cs, (cx * SCALE - cw * SCALE // 2,
                       cy * SCALE - 18 * SCALE))


def mountains_layered(surf):
    """Three layers of v3 mountain silhouettes, scaled, with a faint
    warm horizon haze where they meet the sky."""
    deepest = [(0, 640), (0, 460), (50, 410), (110, 430), (170, 380),
               (230, 415), (290, 380), (360, 410), (360, 640)]
    far = [(0, 640), (0, 490), (60, 420), (120, 450), (200, 375),
           (280, 430), (360, 360), (360, 400), (360, 640)]
    near = [(0, 640), (0, 530), (80, 505), (160, 520), (240, 490),
            (320, 510), (360, 495), (360, 640)]

    m = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(m, (18, 28, 60, 160),
                        [(x * SCALE, y * SCALE) for x, y in deepest])
    pygame.draw.polygon(m, (14, 26, 50, 220),
                        [(x * SCALE, y * SCALE) for x, y in far])
    pygame.draw.polygon(m, (10, 18, 36, 235),
                        [(x * SCALE, y * SCALE) for x, y in near])
    surf.blit(m, (0, 0))

    # Faint warm horizon haze — soft 40-px gradient where mountains rise
    haze = pygame.Surface((W, 60 * SCALE), pygame.SRCALPHA)
    for yy in range(60 * SCALE):
        a = int(22 * (1 - yy / (60 * SCALE)))
        pygame.draw.line(haze, (60, 90, 140, a), (0, yy), (W, yy))
    surf.blit(haze, (0, 360 * SCALE))


# ── Title + subtitle + divider (canonical SKYBIT recipe) ────────────────────

def skybit_title(surf, cx, cy, size=72):
    f = font(size, True)
    img = f.render("SKYBIT", True, GOLD_BRIGHT)
    out = f.render("SKYBIT", True, RED_OUTLINE)
    sh  = f.render("SKYBIT", True, NEAR_BLACK)
    r = img.get_rect(center=(cx, cy))
    px = 3 * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + 3 * SCALE, r.y + 5 * SCALE))
    surf.blit(img, r.topleft)


def skybit_subtitle(surf, cx, cy, size=22):
    f = font(size, True)
    img = f.render("POCKET  SKY  FLYER", True, GOLD_BRIGHT)
    out = f.render("POCKET  SKY  FLYER", True, RED_OUTLINE)
    sh  = f.render("POCKET  SKY  FLYER", True, NEAR_BLACK)
    r = img.get_rect(center=(cx, cy))
    px = 2 * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + 2 * SCALE, r.y + 3 * SCALE))
    surf.blit(img, r.topleft)


def divider(surf, cy, width=140):
    """Gold hairline — matches the title fill + the panel accents so
    every minor line on the screen belongs to one gold accent system."""
    line = pygame.Surface((width * SCALE, 1 * SCALE), pygame.SRCALPHA)
    line.fill((*GOLD_BRIGHT, 120))
    surf.blit(line, line.get_rect(center=(W // 2, cy)))


# ── Pill — polished v3 button with consistent depth treatment ───────────────

def pill(surf, center, text, size=22, min_w=240, h=48, primary=False):
    """Red-gradient pill with orange border + white text + depth.
    `primary=True` adds a subtle orange outer glow so the main action
    reads as the bigger touch target without changing colour."""
    h *= SCALE
    cx, cy = center
    f = font(size, True)
    img = f.render(text, True, PILL_TEXT)
    w = max(min_w * SCALE, img.get_width() + 50 * SCALE)
    x = cx - w // 2
    y = cy - h // 2

    if primary:
        # Outer gold glow halo — very faint, falls off to invisible.
        # Uses GOLD_BRIGHT (canonical) so the halo reads as warm
        # rather than orange-plastic.
        glow = pygame.Surface((w + 28 * SCALE, h + 28 * SCALE),
                              pygame.SRCALPHA)
        for r in range(12 * SCALE, 0, -SCALE):
            a = int(40 * r / (12 * SCALE))
            pygame.draw.rect(glow, (*GOLD_BRIGHT, a // 4),
                             (14 * SCALE - r, 14 * SCALE - r,
                              w + r * 2, h + r * 2),
                             border_radius=(h + r * 2) // 2)
        surf.blit(glow, (x - 14 * SCALE, y - 14 * SCALE))

    # Soft drop shadow under the pill (single rounded blob offset down)
    sh = pygame.Surface((w + 4 * SCALE, h + 4 * SCALE), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90), (0, 0, w + 4 * SCALE, h + 4 * SCALE),
                     border_radius=(h + 4 * SCALE) // 2)
    surf.blit(sh, (x - 2 * SCALE, y + 6 * SCALE))

    # Pill body — v3 red gradient
    p = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = lerp(BTN_TOP, BTN_BOT, t)
        pygame.draw.line(p, (*c, 255), (0, yy), (w, yy))
    # Inner top-edge frost highlight (very subtle, drawn on its own surface
    # then blitted with proper alpha)
    frost = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2):
        a = int(50 * (1 - yy / (h / 2)))
        pygame.draw.line(frost, (255, 245, 220, a), (0, yy), (w, yy))
    p.blit(frost, (0, 0))
    # Bottom-edge inner shadow for dimension
    bsh = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2, h):
        a = int(50 * (yy - h // 2) / (h / 2))
        pygame.draw.line(bsh, (0, 0, 0, a), (0, yy), (w, yy))
    p.blit(bsh, (0, 0))
    # Rounded mask
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=h // 2)
    p.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Gold border — ties pills to the title fill + the BEST/TOP 10
    # accent system so every interactive surface speaks the same
    # gold-on-deep-night language.
    pygame.draw.rect(p, GOLD_BRIGHT, (0, 0, w, h),
                     width=2 * SCALE, border_radius=h // 2)
    # Thin inner gold hint at the very top inside the rim
    pygame.draw.line(p, (*GOLD_BRIGHT, 110),
                     (h // 2, 3 * SCALE),
                     (w - h // 2, 3 * SCALE), 1 * SCALE)
    surf.blit(p, (x, y))

    # Text — cream-white with a deep-burgundy shadow (in the family of
    # the pill body, not orange).
    shadow = f.render(text, True, (30, 8, 16))
    shadow.set_alpha(220)
    tr = img.get_rect(center=(cx, cy))
    surf.blit(shadow, (tr.x + 2 * SCALE, tr.y + 2 * SCALE))
    surf.blit(img, tr)


# ── BEST + TOP 10 — polished panel ──────────────────────────────────────────

def best_panel(surf, rect, label, value):
    # Drop shadow
    sh = pygame.Surface((rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                     border_radius=14 * SCALE)
    surf.blit(sh, (rect.x - 2 * SCALE, rect.y + 4 * SCALE))
    # Panel body
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*PANEL_DARK, 210),
                     (0, 0, rect.w, rect.h),
                     border_radius=14 * SCALE)
    # Gold edge stroke — matches the pill border + title fill
    pygame.draw.rect(pnl, (*GOLD_BRIGHT, 130),
                     (0, 0, rect.w, rect.h),
                     width=1 * SCALE, border_radius=14 * SCALE)
    # Top accent strip — gold to match the system
    accent = pygame.Surface((rect.w - 28 * SCALE, 2), pygame.SRCALPHA)
    accent.fill((*GOLD_BRIGHT, 110))
    pnl.blit(accent, (14 * SCALE, 4))
    # Hairline top highlight
    pygame.draw.line(pnl, (255, 220, 140, 90),
                     (14 * SCALE, 2),
                     (rect.w - 14 * SCALE, 2), 1 * SCALE)
    surf.blit(pnl, rect.topleft)
    # Label — gold-muted, letter-spaced (canonical "B E S T" style)
    lf = font(12, False).render(label, True, GOLD_MUTED)
    lf.set_alpha(220)
    surf.blit(lf, lf.get_rect(center=(rect.centerx, rect.y + 14 * SCALE)))
    # Value — gold-bright
    if value:
        vf = font(24, True).render(value, True, GOLD_BRIGHT)
        vs = font(24, True).render(value, True, NEAR_BLACK)
        vs.set_alpha(170)
        vr = vf.get_rect(center=(rect.centerx, rect.y + 34 * SCALE))
        surf.blit(vs, (vr.x + 1 * SCALE, vr.y + 2 * SCALE))
        surf.blit(vf, vr)


def top10_panel(surf, rect):
    # Drop shadow
    sh = pygame.Surface((rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                     border_radius=14 * SCALE)
    surf.blit(sh, (rect.x - 2 * SCALE, rect.y + 4 * SCALE))
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*PANEL_DARK, 210),
                     (0, 0, rect.w, rect.h),
                     border_radius=14 * SCALE)
    pygame.draw.rect(pnl, (*GOLD_BRIGHT, 130),
                     (0, 0, rect.w, rect.h),
                     width=1 * SCALE, border_radius=14 * SCALE)
    accent = pygame.Surface((rect.w - 28 * SCALE, 2), pygame.SRCALPHA)
    accent.fill((*GOLD_BRIGHT, 110))
    pnl.blit(accent, (14 * SCALE, 4))
    pygame.draw.line(pnl, (255, 220, 140, 90),
                     (14 * SCALE, 2),
                     (rect.w - 14 * SCALE, 2), 1 * SCALE)
    surf.blit(pnl, rect.topleft)
    lf = font(12, False).render("T O P  10", True, GOLD_MUTED)
    lf.set_alpha(220)
    surf.blit(lf, lf.get_rect(center=(rect.centerx, rect.y + 14 * SCALE)))
    draw_trophy(surf, rect.centerx, rect.y + 36 * SCALE, 10 * SCALE)


def draw_trophy(surf, cx, cy, size):
    s = int(size)
    cup_top_y = int(cy - s + 2)
    cup_bot_y = int(cy + 2)
    pts = [(cx - s, cup_top_y), (cx + s, cup_top_y),
           (cx + s - 3, cup_bot_y), (cx - s + 3, cup_bot_y)]
    pygame.draw.polygon(surf, GOLD_BRIGHT, pts)
    pygame.draw.polygon(surf, GOLD_DEEP, pts, 1)
    h_w = max(4, s // 4)
    pygame.draw.arc(surf, GOLD_BRIGHT,
                    (cx - s - h_w, cup_top_y + 2, h_w * 2, s),
                    math.pi / 2, math.pi * 3 / 2, 2)
    pygame.draw.arc(surf, GOLD_BRIGHT,
                    (cx + s - h_w, cup_top_y + 2, h_w * 2, s),
                    -math.pi / 2, math.pi / 2, 2)
    sw = max(3, s // 5)
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - sw // 2, cup_bot_y, sw, s // 2))
    bw = s * 2
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - bw // 2, cup_bot_y + s // 2, bw, max(2, s // 4)))
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - bw // 2 - 2, cup_bot_y + s // 2 + max(2, s // 4),
                      bw + 4, max(2, s // 5)))


# ─────────────────────────────────────────────────────────────────────────────

def main():
    s = pygame.Surface((W, H))

    # Background composition (back → front)
    sky_with_stars(s)
    clouds(s)
    mountains_layered(s)

    # Title
    skybit_title(s, W // 2, 130 * SCALE, size=74)
    skybit_subtitle(s, W // 2, 190 * SCALE, size=22)
    divider(s, 216 * SCALE, width=140)

    # 3 pills with consistent spacing — primary slightly larger + glow
    primary_y = 296 * SCALE
    pitch = 70 * SCALE
    pill(s, (W // 2, primary_y), "TAP TO START",
         size=23, min_w=246, h=54, primary=True)
    pill(s, (W // 2, primary_y + pitch), "HOW TO PLAY",
         size=20, min_w=234, h=46)
    pill(s, (W // 2, primary_y + 2 * pitch), "POWER-UPS",
         size=20, min_w=234, h=46)

    # BEST + TOP 10 twin panels
    panel_w = 144 * SCALE
    gap = 12 * SCALE
    total = panel_w * 2 + gap
    left_x = (W - total) // 2
    cy = H - 88 * SCALE
    best_panel(s,
               pygame.Rect(left_x, cy - 26 * SCALE, panel_w, 52 * SCALE),
               "B E S T", "42")
    top10_panel(s,
                pygame.Rect(left_x + panel_w + gap, cy - 26 * SCALE,
                            panel_w, 52 * SCALE))

    out = os.path.join(OUT, "v3_professional.png")
    pygame.image.save(s, out)
    print(f"wrote {out} ({W}x{H})")


if __name__ == "__main__":
    main()
