"""Generate the full v1 ROYAL UI set — 8 screens at 720x1280.

Refines the v1 ROYAL primitives from `tools/gen_menu_themes.py:v1_royal()`
and lifts them to module-level reusable helpers. Adjustments vs the
original v1 ROYAL mockup:

  * Drops the noisy filigree-dot rows along the top/bottom of the
    frame — they read as clutter at small size.
  * Pills default to a single gold rim (the double-rim is reserved
    for primary glowing buttons).
  * Medallion interior uses canonical `PANEL_DARK` (12, 8, 38)
    instead of the ad-hoc (60, 40, 80) so the whole UI sits in the
    same colour family.
  * Tighter spacing rhythm + better typography hierarchy.
  * Refined ribbon tail (slimmer, more elegant).
  * Higher resolution (720x1280, 2x the game canvas).

Outputs in `docs/menu_redesign_v4/`:
  v1_royal.png              — Main menu  (refreshed)
  v1_royal_pause.png        — Pause overlay
  v1_royal_stats.png        — Run summary
  v1_royal_gameover.png     — Game over (NEW BEST variant)
  v1_royal_name_entry.png   — Top 10 qualifier name entry
  v1_royal_leaderboard.png  — TOP 10 ranking
  v1_royal_powerups.png     — Power-ups help grid
  v1_royal_intro.png        — How-to-play title card
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

# 2x the game canvas
SCALE = 2
W, H = 360 * SCALE, 640 * SCALE
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "menu_redesign_v4")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "game", "assets")
FONT_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
FONT_REG  = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")

# Skybit canonical palette
GOLD_BRIGHT   = (240, 192,  64)
GOLD_MUTED    = (216, 184,  85)
GOLD_DEEP     = (180, 130,  20)
GOLD_DARK     = (140,  96,  14)
SILVER        = (210, 215, 225)
SILVER_DARK   = (130, 140, 160)
BRONZE        = (200, 130,  64)
BRONZE_DARK   = (130,  76,  30)
RED_OUTLINE   = (168,  32,  16)
ORANGE_BORDER = (232, 104,  40)
BTN_TOP       = (200,  64,  24)
BTN_BOT       = (126,  28,   2)
RIBBON_RED    = (200,  50,  50)
RIBBON_DARK   = (140,  20,  20)
PANEL_DARK    = ( 12,   8,  38)
PANEL_LIGHTER = ( 24,  18,  58)
NIGHT_DEEP    = (  6,   1,  21)
NIGHT_MID     = ( 22,  14,  58)
WHITE         = (245, 245, 245)
NEAR_BLACK    = ( 12,   8,  18)


# ── Core helpers ────────────────────────────────────────────────────────────

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


def save(name, surf):
    out = os.path.join(OUT, name)
    pygame.image.save(surf, out)
    print(f"  wrote {out} ({W}x{H})")


# ── Skybit night-sky background + mountain silhouettes ──────────────────────

def night_sky(surf, dim=0):
    gradient_v(surf, NIGHT_DEEP, NIGHT_MID)
    random.seed(42)
    for _ in range(180):
        x = random.randint(0, W - 1)
        y = random.randint(0, int(420 * SCALE))
        r = random.choice([1, 1, 1, 2]) * SCALE
        a = random.randint(120, 255)
        d = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(d, (240, 240, 250, a), (r + 1, r + 1), r)
        surf.blit(d, (x - r - 1, y - r - 1))
    # Faint cloud puffs
    for cx, cy, cw in [(60, 90, 100), (260, 70, 110), (320, 160, 80)]:
        cs = pygame.Surface((cw * SCALE, 30 * SCALE), pygame.SRCALPHA)
        pygame.draw.ellipse(cs, (40, 30, 70, 80),
                            (0, 0, cw * SCALE, 28 * SCALE))
        surf.blit(cs, (cx * SCALE - cw * SCALE // 2, cy * SCALE - 14 * SCALE))
    if dim:
        d = pygame.Surface((W, H), pygame.SRCALPHA)
        d.fill((0, 0, 0, dim))
        surf.blit(d, (0, 0))


def mountains(surf, alpha=200):
    far_pts = [(0, 640), (0, 490), (60, 420), (120, 450), (200, 375),
               (280, 430), (360, 360), (360, 400), (360, 640)]
    near_pts = [(0, 640), (0, 530), (80, 505), (160, 520), (240, 490),
                (320, 510), (360, 495), (360, 640)]
    m = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(m, (14, 26, 50, alpha),
                        [(x * SCALE, y * SCALE) for x, y in far_pts])
    pygame.draw.polygon(m, (10, 18, 36, alpha),
                        [(x * SCALE, y * SCALE) for x, y in near_pts])
    surf.blit(m, (0, 0))


# ── ROYAL primitives (refined, module-level) ────────────────────────────────

def royal_frame(surf):
    """Outer gold-leaf border + corner medallions only — no busy filigree."""
    # Outer thick stroke
    outer = pygame.Rect(8 * SCALE, 8 * SCALE,
                        W - 16 * SCALE, H - 16 * SCALE)
    pygame.draw.rect(surf, GOLD_DARK, outer,
                     width=4 * SCALE, border_radius=12 * SCALE)
    # Inner thin stroke
    inner = pygame.Rect(14 * SCALE, 14 * SCALE,
                        W - 28 * SCALE, H - 28 * SCALE)
    pygame.draw.rect(surf, GOLD_BRIGHT, inner,
                     width=2 * SCALE, border_radius=10 * SCALE)
    # Corner medallions — slightly smaller, more deliberate
    for cx, cy in [(22 * SCALE, 22 * SCALE),
                   (W - 22 * SCALE, 22 * SCALE),
                   (22 * SCALE, H - 22 * SCALE),
                   (W - 22 * SCALE, H - 22 * SCALE)]:
        pygame.draw.circle(surf, PANEL_DARK, (cx, cy), 10 * SCALE)
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), 10 * SCALE, 2 * SCALE)
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), 3 * SCALE)


def royal_title(surf, text, center, size=68):
    """Beveled gold-on-red: thick red halo + dark-gold underlay +
    black shadow + gold-bright fill + faint top highlight."""
    cx, cy = center
    f = font(size, True)
    base = f.render(text, True, GOLD_BRIGHT)
    rect = base.get_rect(center=(cx, cy))
    # Thick red outline halo
    out_red = f.render(text, True, RED_OUTLINE)
    for r in range(5 * SCALE, 0, -1 * SCALE):
        for ang in range(0, 360, 30):
            ox = int(math.cos(math.radians(ang)) * r)
            oy = int(math.sin(math.radians(ang)) * r)
            out_red.set_alpha(80 if r > 2 * SCALE else 255)
            surf.blit(out_red, (rect.x + ox, rect.y + oy))
    out_red.set_alpha(255)
    # Dark-gold underlay
    sh = f.render(text, True, GOLD_DEEP)
    surf.blit(sh, (rect.x + 3 * SCALE, rect.y + 5 * SCALE))
    # Soft black drop
    bk = f.render(text, True, NEAR_BLACK)
    bk.set_alpha(180)
    surf.blit(bk, (rect.x + 4 * SCALE, rect.y + 7 * SCALE))
    # Fill
    surf.blit(base, rect.topleft)
    # Top edge highlight
    hl = f.render(text, True, (255, 240, 180))
    hl.set_alpha(80)
    surf.blit(hl, (rect.x, rect.y - 1 * SCALE))
    return rect


def royal_subtitle(surf, text, center, size=18):
    cx, cy = center
    f = font(size, True)
    img = f.render(text, True, GOLD_BRIGHT)
    out = f.render(text, True, RED_OUTLINE)
    r = img.get_rect(center=(cx, cy))
    px = 2 * SCALE
    for ox, oy in [(-px, 0), (px, 0), (0, -px), (0, px)]:
        surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)


def royal_divider(surf, cy, width=110):
    """Two gold hairlines with a tiny diamond ornament between them."""
    half = width * SCALE // 2
    pygame.draw.line(surf, GOLD_BRIGHT,
                     (W // 2 - half, cy), (W // 2 - 10 * SCALE, cy),
                     1 * SCALE)
    pygame.draw.line(surf, GOLD_BRIGHT,
                     (W // 2 + 10 * SCALE, cy), (W // 2 + half, cy),
                     1 * SCALE)
    pygame.draw.polygon(surf, GOLD_BRIGHT,
                        [(W // 2, cy - 4 * SCALE),
                         (W // 2 + 5 * SCALE, cy),
                         (W // 2, cy + 4 * SCALE),
                         (W // 2 - 5 * SCALE, cy)])


def royal_pill(surf, center, text, big=False, primary=False, w_min=220):
    """Red-gradient pill. Single gold rim by default; double-rim + glow
    when `primary` (used for the main action button)."""
    h = (52 if big else 42) * SCALE
    sz = 22 if big else 17
    f = font(sz, True)
    img = f.render(text, True, WHITE)
    w = max(w_min * SCALE, img.get_width() + 48 * SCALE)
    cx, cy = center
    x = cx - w // 2
    y = cy - h // 2

    if primary:
        # Outer glow halo
        glow = pygame.Surface((w + 24 * SCALE, h + 24 * SCALE),
                              pygame.SRCALPHA)
        for r in range(10 * SCALE, 0, -SCALE):
            a = int(50 * r / (10 * SCALE))
            pygame.draw.rect(glow, (255, 220, 130, a // 4),
                             (12 * SCALE - r, 12 * SCALE - r,
                              w + r * 2, h + r * 2),
                             border_radius=(h + r * 2) // 2)
        surf.blit(glow, (x - 12 * SCALE, y - 12 * SCALE))
        # Outer gold ring (double-rim)
        pygame.draw.rect(surf, GOLD_BRIGHT,
                         (x - 3 * SCALE, y - 3 * SCALE,
                          w + 6 * SCALE, h + 6 * SCALE),
                         border_radius=(h + 6 * SCALE) // 2)
        pygame.draw.rect(surf, GOLD_DARK,
                         (x - 3 * SCALE, y - 3 * SCALE,
                          w + 6 * SCALE, h + 6 * SCALE),
                         width=1 * SCALE,
                         border_radius=(h + 6 * SCALE) // 2)
        # Inner gap
        pygame.draw.rect(surf, NEAR_BLACK,
                         (x - 1 * SCALE, y - 1 * SCALE,
                          w + 2 * SCALE, h + 2 * SCALE),
                         border_radius=(h + 2 * SCALE) // 2)

    # Pill body — gradient + frost highlight, clipped to rounded shape
    pill = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = lerp(BTN_TOP, BTN_BOT, t)
        pygame.draw.line(pill, (*c, 255), (0, yy), (w, yy))
    frost = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2):
        a = int(45 * (1 - yy / (h / 2)))
        pygame.draw.line(frost, (255, 255, 255, a), (0, yy), (w, yy))
    pill.blit(frost, (0, 0))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=h // 2)
    pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Single gold rim
    pygame.draw.rect(pill, GOLD_BRIGHT, (0, 0, w, h),
                     width=2 * SCALE, border_radius=h // 2)
    # Bottom inner shadow
    sb = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 3, h):
        a = int(40 * (yy - h // 3) / (h - h // 3))
        pygame.draw.line(sb, (0, 0, 0, a), (0, yy), (w, yy))
    sb.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pill.blit(sb, (0, 0))
    surf.blit(pill, (x, y))

    # Text — gold-bright with soft drop shadow
    sh = f.render(text, True, NEAR_BLACK)
    sh.set_alpha(180)
    ir = img.get_rect(center=center)
    surf.blit(sh, (ir.x + 1 * SCALE, ir.y + 2 * SCALE))
    surf.blit(img, ir.topleft)
    return pygame.Rect(x, y, w, h)


def royal_medallion(surf, cx, cy, r, label=None, value=None,
                    with_trophy=False, with_ribbon=True,
                    interior=PANEL_DARK, ring=GOLD_BRIGHT,
                    ring_inner=GOLD_DEEP):
    """Ornate medallion: dark-purple interior + thick gold ring +
    thin inner gold ring + radial laurel ticks + label/value or trophy.
    Optional red ribbon tail beneath."""
    # Interior
    pygame.draw.circle(surf, interior, (cx, cy), r)
    # Subtle inner radial highlight
    hl = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    for rr in range(int(r * 0.7), 0, -2):
        a = int(15 * (1 - rr / (r * 0.7)))
        pygame.draw.circle(hl, (255, 230, 170, a),
                           (r + 2, r + 2 - r // 3), rr)
    surf.blit(hl, (cx - r - 2, cy - r - 2))
    # Thick outer gold ring
    pygame.draw.circle(surf, ring, (cx, cy), r, 3 * SCALE)
    # Thin inner gold ring at 85% radius
    inner_r = int(r * 0.85)
    pygame.draw.circle(surf, ring_inner, (cx, cy), inner_r, 1 * SCALE)
    # Radial laurel ticks between the two rings
    for ang_deg in range(0, 360, 15):
        a = math.radians(ang_deg)
        x1 = cx + math.cos(a) * inner_r
        y1 = cy + math.sin(a) * inner_r
        x2 = cx + math.cos(a) * (r - 1 * SCALE)
        y2 = cy + math.sin(a) * (r - 1 * SCALE)
        pygame.draw.line(surf, ring, (x1, y1), (x2, y2), 1 * SCALE)

    # Centre content
    if with_trophy:
        # Slightly raise the label, drop the trophy
        if label:
            lf = font(10, True).render(label, True, GOLD_BRIGHT)
            surf.blit(lf, lf.get_rect(center=(cx, cy - r * 0.45)))
        draw_trophy(surf, cx, cy + r * 0.18, r // 4)
    else:
        if label:
            lf = font(10, True).render(label, True, GOLD_BRIGHT)
            surf.blit(lf, lf.get_rect(center=(cx, cy - r * 0.4)))
        if value is not None:
            vf = font(28, True).render(str(value), True, GOLD_BRIGHT)
            shv = font(28, True).render(str(value), True, NEAR_BLACK)
            shv.set_alpha(180)
            vr = vf.get_rect(center=(cx, cy + r * 0.18))
            surf.blit(shv, (vr.x + 1, vr.y + 2))
            surf.blit(vf, vr)

    # Ribbon tail beneath
    if with_ribbon:
        ribbon_pts = [
            (cx - r * 0.4, cy + r - 2 * SCALE),
            (cx + r * 0.4, cy + r - 2 * SCALE),
            (cx + r * 0.3, cy + r + 14 * SCALE),
            (cx,           cy + r + 8 * SCALE),
            (cx - r * 0.3, cy + r + 14 * SCALE),
        ]
        pygame.draw.polygon(surf, RIBBON_RED, ribbon_pts)
        pygame.draw.polygon(surf, RIBBON_DARK, ribbon_pts, 1 * SCALE)
        # Highlight stripe down centre of ribbon
        pygame.draw.line(surf, (255, 110, 100),
                         (cx, cy + r - 2 * SCALE),
                         (cx, cy + r + 8 * SCALE), 1 * SCALE)


def royal_card(surf, rect, border_alpha=200):
    """Dark-purple panel with a 2-px gold-leaf border. Reused for
    stat rows, leaderboard rows, instruction cards, power-up tiles."""
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*PANEL_DARK, 230),
                     (0, 0, rect.w, rect.h),
                     border_radius=10 * SCALE)
    pygame.draw.rect(pnl, (*GOLD_BRIGHT, border_alpha),
                     (0, 0, rect.w, rect.h),
                     width=2 * SCALE,
                     border_radius=10 * SCALE)
    # Top inner highlight
    pygame.draw.line(pnl, (*GOLD_BRIGHT, 110),
                     (10 * SCALE, 3 * SCALE),
                     (rect.w - 10 * SCALE, 3 * SCALE), 1 * SCALE)
    surf.blit(pnl, rect.topleft)


def royal_ribbon_banner(surf, cx, cy, text, w=160):
    """Hanging gold-cloth banner with notched ends + red trim lines.
    Used for NEW BEST!, EFFECTS LAST 8 SECONDS, etc."""
    w *= SCALE
    h = 28 * SCALE
    x = cx - w // 2
    y = cy - h // 2
    # Cloth body
    body_pts = [
        (x + 12 * SCALE, y),
        (x + w - 12 * SCALE, y),
        (x + w, y + h // 2),
        (x + w - 12 * SCALE, y + h),
        (x + 12 * SCALE, y + h),
        (x, y + h // 2),
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, body_pts)
    pygame.draw.polygon(surf, GOLD_DARK, body_pts, 2 * SCALE)
    # Red trim lines along top + bottom edges
    pygame.draw.line(surf, RIBBON_DARK,
                     (x + 12 * SCALE, y + 3 * SCALE),
                     (x + w - 12 * SCALE, y + 3 * SCALE), 1 * SCALE)
    pygame.draw.line(surf, RIBBON_DARK,
                     (x + 12 * SCALE, y + h - 4 * SCALE),
                     (x + w - 12 * SCALE, y + h - 4 * SCALE), 1 * SCALE)
    # Text
    tf = font(13, True).render(text, True, NEAR_BLACK)
    surf.blit(tf, tf.get_rect(center=(cx, cy)))


def draw_trophy(surf, cx, cy, size):
    s = int(size)
    cup_top_y = int(cy - s + 2)
    cup_bot_y = int(cy + 2)
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
    sw = max(3, s // 5)
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - sw // 2, cup_bot_y, sw, s // 2))
    bw = s * 2
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - bw // 2, cup_bot_y + s // 2, bw, max(2, s // 4)))
    pygame.draw.rect(surf, GOLD_BRIGHT,
                     (cx - bw // 2 - 2, cup_bot_y + s // 2 + max(2, s // 4),
                      bw + 4, max(2, s // 5)))


def royal_nameplate(surf, rect, sample_text=""):
    """Engraved gold-rim nameplate with corner rivets. Used for the
    name-entry input field."""
    # Plate
    pygame.draw.rect(surf, GOLD_BRIGHT, rect,
                     border_radius=8 * SCALE)
    inner = rect.inflate(-6 * SCALE, -6 * SCALE)
    pygame.draw.rect(surf, PANEL_DARK, inner,
                     border_radius=6 * SCALE)
    pygame.draw.rect(surf, GOLD_DEEP, rect, width=2 * SCALE,
                     border_radius=8 * SCALE)
    # Top inner highlight
    pygame.draw.line(surf, (255, 240, 180, 220),
                     (rect.x + 10 * SCALE, rect.y + 3 * SCALE),
                     (rect.right - 10 * SCALE, rect.y + 3 * SCALE), 1 * SCALE)
    # Corner rivets
    for rx, ry in [(rect.x + 8 * SCALE, rect.y + 8 * SCALE),
                   (rect.right - 8 * SCALE, rect.y + 8 * SCALE),
                   (rect.x + 8 * SCALE, rect.bottom - 8 * SCALE),
                   (rect.right - 8 * SCALE, rect.bottom - 8 * SCALE)]:
        pygame.draw.circle(surf, GOLD_DARK, (rx, ry), 3 * SCALE)
        pygame.draw.circle(surf, GOLD_BRIGHT, (rx, ry), 3 * SCALE, 1 * SCALE)
        pygame.draw.circle(surf, (255, 240, 180),
                           (rx - 1 * SCALE, ry - 1 * SCALE), 1 * SCALE)
    if sample_text:
        tf = font(28, True).render(sample_text, True, GOLD_BRIGHT)
        sh = font(28, True).render(sample_text, True, NEAR_BLACK)
        sh.set_alpha(180)
        tr = tf.get_rect(center=rect.center)
        surf.blit(sh, (tr.x + 1 * SCALE, tr.y + 2 * SCALE))
        surf.blit(tf, tr)


# ── Procedural power-up icons (small enough for a medallion centre) ──────────

def icon_triple(surf, cx, cy, r):
    """Three small gold coins."""
    for dx, dy in [(-r * 0.5, r * 0.1), (0, -r * 0.3), (r * 0.5, r * 0.1)]:
        pygame.draw.circle(surf, GOLD_BRIGHT,
                           (int(cx + dx), int(cy + dy)), int(r * 0.35))
        pygame.draw.circle(surf, GOLD_DARK,
                           (int(cx + dx), int(cy + dy)), int(r * 0.35), 1 * SCALE)
        sf = font(11, True).render("$", True, (40, 110, 40))
        surf.blit(sf, sf.get_rect(center=(int(cx + dx), int(cy + dy))))


def icon_magnet(surf, cx, cy, r):
    """Red horseshoe magnet."""
    inner_r = int(r * 0.6)
    outer_r = int(r * 0.95)
    # Outer arc (red horseshoe)
    pygame.draw.arc(surf, (200, 50, 40),
                    (cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2),
                    math.pi, 2 * math.pi, int(r * 0.3))
    # Silver tips
    pygame.draw.rect(surf, SILVER,
                     (cx - outer_r, cy - 2, outer_r - inner_r + 1, 6 * SCALE))
    pygame.draw.rect(surf, SILVER,
                     (cx + inner_r - 1, cy - 2,
                      outer_r - inner_r + 1, 6 * SCALE))


def icon_slowmo(surf, cx, cy, r):
    """Hourglass."""
    w = int(r * 0.7)
    h = int(r * 1.1)
    top = [(cx - w, cy - h // 2), (cx + w, cy - h // 2),
           (cx + 2 * SCALE, cy), (cx - 2 * SCALE, cy)]
    bot = [(cx - 2 * SCALE, cy), (cx + 2 * SCALE, cy),
           (cx + w, cy + h // 2), (cx - w, cy + h // 2)]
    pygame.draw.polygon(surf, (180, 90, 220), top)
    pygame.draw.polygon(surf, (180, 90, 220), bot)
    pygame.draw.polygon(surf, GOLD_BRIGHT, top, 2 * SCALE)
    pygame.draw.polygon(surf, GOLD_BRIGHT, bot, 2 * SCALE)


def icon_kfc(surf, cx, cy, r):
    """Red+white striped bucket."""
    bw = int(r * 1.0)
    bh = int(r * 1.0)
    pts = [(cx - bw // 2, cy - bh // 2),
           (cx + bw // 2, cy - bh // 2),
           (cx + bw // 2 - 3 * SCALE, cy + bh // 2),
           (cx - bw // 2 + 3 * SCALE, cy + bh // 2)]
    pygame.draw.polygon(surf, (210, 60, 60), pts)
    pygame.draw.polygon(surf, NEAR_BLACK, pts, 1 * SCALE)
    # Stripes
    for k in range(3):
        y = cy - bh // 2 + (k + 1) * bh // 4
        pygame.draw.line(surf, (250, 240, 230),
                         (cx - bw // 2 + 2 * SCALE, y),
                         (cx + bw // 2 - 2 * SCALE, y), 2 * SCALE)


def icon_ghost(surf, cx, cy, r):
    """Pale-blue ghost sheet shape."""
    w = int(r * 1.1)
    h = int(r * 1.2)
    top_arc = pygame.Rect(cx - w // 2, cy - h // 2, w, h * 2 // 3)
    pygame.draw.ellipse(surf, (200, 230, 255), top_arc)
    pygame.draw.rect(surf, (200, 230, 255),
                     (cx - w // 2, cy - h // 4, w, h // 2))
    # Wavy bottom hem
    bw = w // 4
    for i in range(4):
        bx = cx - w // 2 + i * bw
        pygame.draw.ellipse(surf, (200, 230, 255),
                            (bx, cy + h // 4, bw, h // 5))
    # Eyes
    pygame.draw.circle(surf, NEAR_BLACK,
                       (cx - w // 4, cy - h // 12), 2 * SCALE)
    pygame.draw.circle(surf, NEAR_BLACK,
                       (cx + w // 4, cy - h // 12), 2 * SCALE)


def icon_grow(surf, cx, cy, r):
    """Mushroom with cream stem + wine cap + spots."""
    cap_w = int(r * 1.2)
    cap_h = int(r * 0.7)
    pygame.draw.ellipse(surf, (125, 30, 45),
                        (cx - cap_w // 2, cy - cap_h - 1 * SCALE,
                         cap_w, cap_h * 2))
    # Clip to top half by drawing a stem rect below
    stem_w = int(r * 0.5)
    stem_h = int(r * 0.6)
    pygame.draw.rect(surf, (245, 230, 200),
                     (cx - stem_w // 2, cy + 2 * SCALE, stem_w, stem_h))
    # Cream spots on the cap
    for dx, dy, rr in [(-cap_w // 4, -cap_h // 3, 3),
                       (0, -cap_h // 4, 4),
                       (cap_w // 5, -cap_h // 3, 3)]:
        pygame.draw.circle(surf, (255, 235, 175),
                           (cx + dx, cy + dy), rr * SCALE // 2 + SCALE)


def icon_surprise(surf, cx, cy, r):
    """Wrapped gift box with red ribbon + bow + ? mark."""
    w = int(r * 1.2)
    h = int(r * 1.1)
    box = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    pygame.draw.rect(surf, PANEL_LIGHTER, box, border_radius=2 * SCALE)
    pygame.draw.rect(surf, GOLD_BRIGHT, box, width=1 * SCALE,
                     border_radius=2 * SCALE)
    # Red ribbon vertical
    pygame.draw.rect(surf, RIBBON_RED,
                     (cx - 2 * SCALE, box.y, 4 * SCALE, box.h))
    # ? mark
    qf = font(20, True).render("?", True, GOLD_BRIGHT)
    surf.blit(qf, qf.get_rect(center=(cx + 8 * SCALE, cy)))


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 1 — MAIN MENU
# ─────────────────────────────────────────────────────────────────────────────
def screen_main_menu():
    s = pygame.Surface((W, H))
    night_sky(s)
    mountains(s, alpha=200)
    royal_frame(s)

    royal_title(s, "SKYBIT", (W // 2, 130 * SCALE), size=72)
    royal_subtitle(s, "POCKET  SKY  FLYER",
                   (W // 2, 188 * SCALE), size=18)
    royal_divider(s, 212 * SCALE, width=110)

    royal_pill(s, (W // 2, 280 * SCALE), "TAP TO START", big=True, primary=True)
    royal_pill(s, (W // 2, 348 * SCALE), "HOW TO PLAY")
    royal_pill(s, (W // 2, 408 * SCALE), "POWER-UPS")

    # BEST + TOP 10 medallions at the bottom
    cy = 510 * SCALE
    royal_medallion(s, 90 * SCALE, cy, 44 * SCALE,
                    label="BEST", value="42")
    royal_medallion(s, W - 90 * SCALE, cy, 44 * SCALE,
                    label="TOP 10", with_trophy=True)

    save("v1_royal.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 2 — PAUSE OVERLAY
# ─────────────────────────────────────────────────────────────────────────────
def screen_pause():
    s = pygame.Surface((W, H))
    night_sky(s, dim=100)  # darkened — overlays gameplay
    mountains(s, alpha=160)
    royal_frame(s)

    # Live score medallion centred above the title
    royal_medallion(s, W // 2, 138 * SCALE, 50 * SCALE,
                    label="SCORE", value="12", with_ribbon=False)

    royal_title(s, "PAUSED", (W // 2, 248 * SCALE), size=64)
    royal_subtitle(s, "TAKE  A  BREATH", (W // 2, 300 * SCALE), size=15)
    royal_divider(s, 322 * SCALE, width=90)

    royal_pill(s, (W // 2, 390 * SCALE), "RESUME", big=True, primary=True)
    royal_pill(s, (W // 2, 458 * SCALE), "RESTART RUN")
    royal_pill(s, (W // 2, 518 * SCALE), "MAIN MENU")

    # Key-hint at bottom
    hint = font(11, True).render("TAP  ·  P  ·  ESC", True, GOLD_MUTED)
    hint.set_alpha(180)
    s.blit(hint, hint.get_rect(center=(W // 2, 588 * SCALE)))

    save("v1_royal_pause.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 3 — RUN SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
def screen_stats():
    s = pygame.Surface((W, H))
    night_sky(s)
    mountains(s, alpha=180)
    royal_frame(s)

    royal_title(s, "RUN  SUMMARY", (W // 2, 70 * SCALE), size=36)

    # Big score medallion
    royal_medallion(s, W // 2, 168 * SCALE, 64 * SCALE,
                    label="SCORE", value="23")

    # Stats card
    rows = [
        ("TIME  ALIVE",     "1 : 27"),
        ("COINS",           "11"),
        ("PILLARS  CLEARED", "23"),
        ("POWER-UPS",       "3"),
        ("NEAR  MISSES",    "3"),
    ]
    card_rect = pygame.Rect(36 * SCALE, 270 * SCALE,
                            W - 72 * SCALE, 220 * SCALE)
    royal_card(s, card_rect)
    row_h = card_rect.h // len(rows)
    for i, (label, value) in enumerate(rows):
        rcy = card_rect.y + i * row_h + row_h // 2
        # Divider between rows
        if i > 0:
            pygame.draw.line(s, (*GOLD_BRIGHT, 60),
                             (card_rect.x + 14 * SCALE,
                              card_rect.y + i * row_h),
                             (card_rect.right - 14 * SCALE,
                              card_rect.y + i * row_h),
                             1 * SCALE)
        lf = font(13, True).render(label, True, GOLD_MUTED)
        s.blit(lf, (card_rect.x + 18 * SCALE,
                    rcy - lf.get_height() // 2))
        vf = font(16, True).render(value, True, GOLD_BRIGHT)
        s.blit(vf, (card_rect.right - 18 * SCALE - vf.get_width(),
                    rcy - vf.get_height() // 2))

    royal_pill(s, (W // 2, 540 * SCALE), "TAP  TO  CONTINUE", primary=True)

    save("v1_royal_stats.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 4 — GAME OVER (NEW BEST variant)
# ─────────────────────────────────────────────────────────────────────────────
def screen_gameover():
    s = pygame.Surface((W, H))
    night_sky(s, dim=70)
    mountains(s, alpha=180)
    royal_frame(s)

    royal_title(s, "GAME  OVER", (W // 2, 90 * SCALE), size=44)

    # NEW BEST! ribbon banner
    royal_ribbon_banner(s, W // 2, 158 * SCALE, "NEW  BEST!", w=160)

    # Score medallion with filigree burst
    msc = W // 2, 280 * SCALE
    # Filigree burst — 16 small gold flourishes radiating
    for i in range(16):
        ang = i * (2 * math.pi / 16)
        d = 88 * SCALE
        x = msc[0] + math.cos(ang) * d
        y = msc[1] + math.sin(ang) * d
        # Tiny gold star/diamond
        for dx, dy in [(0, -3 * SCALE), (3 * SCALE, 0),
                       (0, 3 * SCALE), (-3 * SCALE, 0)]:
            pygame.draw.line(s, GOLD_BRIGHT, (x, y), (x + dx, y + dy),
                             1 * SCALE)
        pygame.draw.circle(s, GOLD_BRIGHT, (int(x), int(y)), 1 * SCALE)
    royal_medallion(s, msc[0], msc[1], 60 * SCALE,
                    label="SCORE", value="23")

    royal_pill(s, (W // 2, 460 * SCALE), "TAP  TO  RETRY",
               big=True, primary=True)
    royal_pill(s, (W // 2, 526 * SCALE), "MAIN  MENU")

    save("v1_royal_gameover.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 5 — NAME ENTRY
# ─────────────────────────────────────────────────────────────────────────────
def screen_name_entry():
    s = pygame.Surface((W, H))
    night_sky(s, dim=60)
    mountains(s, alpha=170)
    royal_frame(s)

    # Trophy with halo at the top
    tcx, tcy = W // 2, 110 * SCALE
    halo = pygame.Surface((140 * SCALE, 140 * SCALE), pygame.SRCALPHA)
    for r in range(60 * SCALE, 0, -2 * SCALE):
        a = int(35 * (1 - r / (60 * SCALE)))
        pygame.draw.circle(halo, (255, 220, 130, a),
                           (70 * SCALE, 70 * SCALE), r)
    s.blit(halo, (tcx - 70 * SCALE, tcy - 70 * SCALE))
    draw_trophy(s, tcx, tcy, 22 * SCALE)

    royal_title(s, "TOP  10  COURIER", (W // 2, 220 * SCALE), size=28)
    royal_subtitle(s, "ENTER  YOUR  NAME",
                   (W // 2, 264 * SCALE), size=14)
    royal_divider(s, 288 * SCALE, width=90)

    # Engraved nameplate
    plate = pygame.Rect(W // 2 - 142 * SCALE, 322 * SCALE,
                        284 * SCALE, 64 * SCALE)
    royal_nameplate(s, plate, sample_text="PIP")

    # Submit + Skip pills side-by-side
    btn_w = 130
    gap = 14 * SCALE
    left_cx = W // 2 - btn_w * SCALE // 2 - gap // 2
    right_cx = W // 2 + btn_w * SCALE // 2 + gap // 2
    royal_pill(s, (W // 2, 446 * SCALE), "SUBMIT",
               big=True, primary=True, w_min=200)
    royal_pill(s, (W // 2, 512 * SCALE), "SKIP", w_min=200)

    save("v1_royal_name_entry.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 6 — LEADERBOARD
# ─────────────────────────────────────────────────────────────────────────────
def screen_leaderboard():
    s = pygame.Surface((W, H))
    night_sky(s, dim=40)
    mountains(s, alpha=170)
    royal_frame(s)

    # Title flanked by twin trophies
    royal_title(s, "TOP  10", (W // 2, 70 * SCALE), size=42)
    for side in (-1, 1):
        tx = W // 2 + side * 110 * SCALE
        draw_trophy(s, tx, 70 * SCALE, 16 * SCALE)
    royal_subtitle(s, "C O U R I E R S", (W // 2, 116 * SCALE), size=12)
    royal_divider(s, 136 * SCALE, width=90)

    # 10 ranked entries
    entries = [
        ("Hawkins",   148),
        ("Garrick",   132),
        ("Atticus",   117),
        ("Mira",      104),
        ("Quill",      96),
        ("Bo",         83),
        ("Pip",        42, True),  # player row
        ("Wren",       38),
        ("Stilt",      29),
        ("Cinder",     18),
    ]
    # Normalise to (name, score, is_player)
    entries = [(e[0], e[1], len(e) == 3 and e[2]) for e in entries]
    list_top = 160 * SCALE
    list_bot = H - 56 * SCALE
    row_h = (list_bot - list_top) // len(entries)
    for i, (name, score, is_player) in enumerate(entries):
        rect = pygame.Rect(28 * SCALE,
                           list_top + i * row_h + 2 * SCALE,
                           W - 56 * SCALE, row_h - 4 * SCALE)
        if is_player:
            # Wider gold-bright border
            pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(pnl, (*PANEL_DARK, 230),
                             (0, 0, rect.w, rect.h),
                             border_radius=10 * SCALE)
            pygame.draw.rect(pnl, GOLD_BRIGHT,
                             (0, 0, rect.w, rect.h),
                             width=3 * SCALE,
                             border_radius=10 * SCALE)
            pygame.draw.line(pnl, (*GOLD_BRIGHT, 130),
                             (10 * SCALE, 4 * SCALE),
                             (rect.w - 10 * SCALE, 4 * SCALE), 1 * SCALE)
            s.blit(pnl, rect.topleft)
        else:
            royal_card(s, rect, border_alpha=120)

        # Rank badge on the left
        rcx = rect.x + rect.h // 2 + 4 * SCALE
        rcy = rect.centery
        rank = i + 1
        if rank <= 3:
            # Medal palettes
            if rank == 1:
                ring, ring_in = GOLD_BRIGHT, GOLD_DEEP
                interior = lerp(GOLD_BRIGHT, NEAR_BLACK, 0.7)
            elif rank == 2:
                ring, ring_in = SILVER, SILVER_DARK
                interior = lerp(SILVER, NEAR_BLACK, 0.75)
            else:
                ring, ring_in = BRONZE, BRONZE_DARK
                interior = lerp(BRONZE, NEAR_BLACK, 0.75)
            br = rect.h // 2 - 6 * SCALE
            pygame.draw.circle(s, interior, (rcx, rcy), br)
            pygame.draw.circle(s, ring, (rcx, rcy), br, 2 * SCALE)
            # Laurel ticks
            for ang_deg in range(0, 360, 30):
                a = math.radians(ang_deg)
                x1 = rcx + math.cos(a) * (br - 3 * SCALE)
                y1 = rcy + math.sin(a) * (br - 3 * SCALE)
                x2 = rcx + math.cos(a) * (br - 1 * SCALE)
                y2 = rcy + math.sin(a) * (br - 1 * SCALE)
                pygame.draw.line(s, ring, (x1, y1), (x2, y2), 1 * SCALE)
            # Rank glyph
            rf = font(14, True).render(str(rank), True, ring)
            s.blit(rf, rf.get_rect(center=(rcx, rcy)))
        else:
            # Plain gold ring
            br = rect.h // 2 - 7 * SCALE
            pygame.draw.circle(s, PANEL_LIGHTER, (rcx, rcy), br)
            pygame.draw.circle(s, GOLD_BRIGHT, (rcx, rcy), br, 1 * SCALE)
            rf = font(13, True).render(str(rank), True, GOLD_BRIGHT)
            s.blit(rf, rf.get_rect(center=(rcx, rcy)))

        # Name centre-left
        nf = font(14, True).render(name, True,
                                   GOLD_BRIGHT if is_player else WHITE)
        nr = nf.get_rect(midleft=(rcx + rect.h // 2 + 4 * SCALE, rcy))
        s.blit(nf, nr)

        # YOU tag for the player row
        if is_player:
            tag_w = 36 * SCALE
            tag_h = 16 * SCALE
            tag_rect = pygame.Rect(
                nr.right + 8 * SCALE, rcy - tag_h // 2,
                tag_w, tag_h)
            pygame.draw.rect(s, GOLD_BRIGHT, tag_rect,
                             border_radius=tag_h // 2)
            tt = font(9, True).render("YOU", True, NEAR_BLACK)
            s.blit(tt, tt.get_rect(center=tag_rect.center))

        # Score right
        sf = font(16, True).render(str(score), True, GOLD_BRIGHT)
        s.blit(sf, sf.get_rect(midright=(rect.right - 16 * SCALE, rcy)))

    # Bottom prompt
    hint = font(11, True).render("TAP  TO  MENU", True, GOLD_MUTED)
    hint.set_alpha(200)
    s.blit(hint, hint.get_rect(center=(W // 2, H - 30 * SCALE)))

    save("v1_royal_leaderboard.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 7 — POWER-UPS HELP
# ─────────────────────────────────────────────────────────────────────────────
def screen_powerups():
    s = pygame.Surface((W, H))
    night_sky(s, dim=40)
    mountains(s, alpha=170)
    royal_frame(s)

    royal_title(s, "POWER-UPS", (W // 2, 66 * SCALE), size=36)
    royal_subtitle(s, "C O L L E C T   T O   B O O S T",
                   (W // 2, 106 * SCALE), size=11)
    royal_divider(s, 124 * SCALE, width=80)

    # 2x3 grid of power-up tiles
    items = [
        ("TRIPLE",  "3x  COIN  VALUE",  icon_triple),
        ("MAGNET",  "PULL  NEARBY  $",  icon_magnet),
        ("SLOW-MO", "TIME  SLOWS",      icon_slowmo),
        ("KFC",     "FAT-PIPE  GAPS",   icon_kfc),
        ("GHOST",   "PASS  THROUGH",    icon_ghost),
        ("GROW",    "BIG  BIRD",        icon_grow),
    ]
    cols = 2
    cell_w = (W - 56 * SCALE) // cols - 8 * SCALE
    cell_h = 104 * SCALE
    cell_gap_x = 12 * SCALE
    cell_gap_y = 10 * SCALE
    grid_top = 144 * SCALE
    grid_left = 28 * SCALE
    for i, (name, desc, icon_fn) in enumerate(items):
        col = i % cols
        row = i // cols
        x = grid_left + col * (cell_w + cell_gap_x)
        y = grid_top + row * (cell_h + cell_gap_y)
        rect = pygame.Rect(x, y, cell_w, cell_h)
        royal_card(s, rect, border_alpha=170)
        # Icon medallion
        icx = rect.centerx
        icy = rect.y + 32 * SCALE
        pygame.draw.circle(s, PANEL_LIGHTER, (icx, icy), 22 * SCALE)
        pygame.draw.circle(s, GOLD_BRIGHT, (icx, icy), 22 * SCALE, 2 * SCALE)
        icon_fn(s, icx, icy, 18 * SCALE)
        # Name
        nf = font(13, True).render(name, True, GOLD_BRIGHT)
        s.blit(nf, nf.get_rect(center=(rect.centerx, rect.y + 68 * SCALE)))
        # Description
        df = font(10, True).render(desc, True, GOLD_MUTED)
        s.blit(df, df.get_rect(center=(rect.centerx, rect.y + 88 * SCALE)))

    # Surprise box — wider card below the 3-row grid
    sb_y = grid_top + 3 * (cell_h + cell_gap_y) + 2 * SCALE
    sb_rect = pygame.Rect(28 * SCALE, sb_y, W - 56 * SCALE, 56 * SCALE)
    royal_card(s, sb_rect, border_alpha=180)
    icon_surprise(s, sb_rect.x + 28 * SCALE, sb_rect.centery, 16 * SCALE)
    nf = font(13, True).render("SURPRISE  BOX", True, GOLD_BRIGHT)
    s.blit(nf, (sb_rect.x + 60 * SCALE,
                sb_rect.centery - 11 * SCALE))
    df = font(10, True).render("RANDOM  ·  ANY  OF  THE  ABOVE",
                               True, GOLD_MUTED)
    s.blit(df, (sb_rect.x + 60 * SCALE,
                sb_rect.centery + 4 * SCALE))

    # Footer ribbon banner with the duration note
    royal_ribbon_banner(s, W // 2, sb_y + 80 * SCALE,
                        "EFFECTS  LAST  8  SECONDS", w=200)

    save("v1_royal_powerups.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 8 — HOW TO PLAY
# ─────────────────────────────────────────────────────────────────────────────
def screen_intro():
    s = pygame.Surface((W, H))
    night_sky(s)
    mountains(s, alpha=180)
    royal_frame(s)

    royal_title(s, "HOW  TO  PLAY", (W // 2, 95 * SCALE), size=36)
    royal_subtitle(s, "A  POCKET  COURIER'S  GUIDE",
                   (W // 2, 138 * SCALE), size=12)
    royal_divider(s, 160 * SCALE, width=90)

    # 3 numbered ROYAL cards
    steps = [
        ("1", "FLAP",    "TAP  ·  CLICK  ·  SPACE"),
        ("2", "THREAD",  "AVOID  THE  PILLARS"),
        ("3", "COLLECT", "COINS  &  POWER-UPS"),
    ]
    card_top = 200 * SCALE
    card_h = 88 * SCALE
    card_gap = 14 * SCALE
    for i, (num, head, body) in enumerate(steps):
        rect = pygame.Rect(40 * SCALE,
                           card_top + i * (card_h + card_gap),
                           W - 80 * SCALE, card_h)
        royal_card(s, rect, border_alpha=180)
        # Number medallion on the left
        ncx = rect.x + 38 * SCALE
        ncy = rect.centery
        pygame.draw.circle(s, GOLD_BRIGHT, (ncx, ncy), 24 * SCALE)
        pygame.draw.circle(s, GOLD_DEEP, (ncx, ncy), 24 * SCALE, 2 * SCALE)
        nf = font(24, True).render(num, True, NEAR_BLACK)
        s.blit(nf, nf.get_rect(center=(ncx, ncy)))
        # Head
        hf = font(18, True).render(head, True, GOLD_BRIGHT)
        s.blit(hf, (rect.x + 80 * SCALE, rect.y + 22 * SCALE))
        # Body
        bf = font(13, True).render(body, True, GOLD_MUTED)
        s.blit(bf, (rect.x + 80 * SCALE, rect.y + 52 * SCALE))

    royal_pill(s, (W // 2, H - 84 * SCALE),
               "TAP  TO  BEGIN", big=True, primary=True)

    save("v1_royal_intro.png", s)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Generating ROYAL UI set at {W}x{H}...")
    screen_main_menu()
    screen_pause()
    screen_stats()
    screen_gameover()
    screen_name_entry()
    screen_leaderboard()
    screen_powerups()
    screen_intro()
    print("Done.")
