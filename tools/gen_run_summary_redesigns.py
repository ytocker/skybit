"""Five candidate redesigns of Skybit's RUN SUMMARY screen, rendered
at 720x1280 (2x the 360x640 game canvas, matching docs/menu_polish/).

Each design respects the established Pip Scarlet theme — gold, scarlet,
deep navy, Liberation Sans Bold, twinkling stars, mountain silhouettes —
but pushes the screen well past the current spreadsheet-of-stats look.

Sample data shared across all 5 mockups so they can be compared apples-
to-apples:
    score=23, best=42, time="1:27", coins=11, pillars=23,
    near_misses=3, powerups_picked={triple:1, magnet:1, ghost:1}

The script reuses every primitive in tools/gen_scarlet_set.py and adds a
few small parts (hex grade medal, stat tile, wax seal, perforated edge,
timeline pin, frosted glass panel) used only for these mockups.

Output: docs/run_summary_redesign/{v1..v5_*.png, contact_sheet.png}
"""

import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from game.powerup_help import _powerup_icon as _ingame_powerup_icon  # noqa
from game.entities import _get_coin_face as _ingame_coin_face  # noqa
from game.config import COIN_R  # noqa

SCALE = 2
W, H = 360 * SCALE, 640 * SCALE
OUT = os.path.join(os.path.dirname(__file__), "..", "docs",
                   "run_summary_redesign")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "game", "assets")
FONT_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
FONT_REG = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")

# Pip Scarlet palette (lifted from gen_scarlet_set.py / game/hud.py)
GOLD_BRIGHT = (240, 192, 64)
GOLD_MUTED = (216, 184, 85)
GOLD_DEEP = (180, 130, 20)
GOLD_PALE = (255, 232, 168)
SILVER = (210, 215, 225)
BRONZE = (200, 130, 64)
RED_OUTLINE = (168, 32, 16)
SCARLET_TOP = (240, 55, 55)
SCARLET_BOT = (148, 20, 20)
SCARLET_DEEP = (90, 14, 12)
SCARLET_SHADOW = (60, 8, 8)
PANEL_DARK = (12, 8, 38)
PANEL_LIGHTER = (26, 18, 62)
NIGHT_DEEP = (6, 1, 21)
NIGHT_MID = (22, 14, 58)
CREAM = (250, 238, 210)
NEAR_BLACK = (12, 8, 18)
TEAL_HINT = (74, 142, 168)
COIN_GOLD = (255, 210, 20)


# ── Shared sample run data ──────────────────────────────────────────────────

DATA = dict(
    score=23,
    best=42,
    new_best=False,
    time_str="1:27",
    duration_s=87,
    coins=11,
    coins_total=18,  # for percentage caption
    pillars=23,
    near_misses=3,
    flaps=127,
    biome_reached="GOLDEN HOUR",
    # Per-kind counts. Only kinds with count > 0 are rendered. Layout
    # has room for all 7 kinds (triple, magnet, slowmo, kfc, ghost,
    # grow, surprise) — the scarlet macaw can grab more than one of
    # the same kind in a long run, so counts can climb above 1.
    powerups_picked=[("triple", 2), ("magnet", 1), ("ghost", 1)],
    # Synthetic timeline events for v4 (seconds_into_run, kind):
    timeline=[
        (4, "coin"), (9, "coin"), (14, "powerup_triple"),
        (22, "coin"), (28, "near_miss"), (33, "coin"),
        (41, "powerup_magnet"), (50, "coin"), (58, "near_miss"),
        (66, "powerup_ghost"), (74, "coin"), (82, "near_miss"),
    ],
)


def grade_for(score: int) -> str:
    """Letter grade derived from final score."""
    if score >= 80:
        return "S"
    if score >= 50:
        return "A"
    if score >= 30:
        return "B"
    if score >= 15:
        return "C"
    if score >= 5:
        return "D"
    return "F"


# ── Primitives copied / adapted from gen_scarlet_set.py ─────────────────────

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
    print(f"  wrote {out} ({surf.get_width()}x{surf.get_height()})")


def sky_with_stars(surf, dim=0):
    gradient_v(surf, NIGHT_DEEP, NIGHT_MID)
    random.seed(42)
    for _ in range(220):
        x = random.randint(0, W - 1)
        y = random.randint(0, int(420 * SCALE))
        tier = random.choices([0, 1, 2, 3], weights=[64, 24, 9, 3])[0]
        r = (1 + tier) * SCALE
        a = random.randint(140, 255)
        if tier >= 2:
            halo = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
            for hr in range(r * 3, 0, -1):
                ha = int(22 * (1 - hr / (r * 3)))
                pygame.draw.circle(halo, (220, 230, 255, ha),
                                   (r * 3, r * 3), hr)
            surf.blit(halo, (x - r * 3, y - r * 3))
        d = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(d, (240, 240, 250, a), (r + 1, r + 1), r)
        surf.blit(d, (x - r - 1, y - r - 1))
    if dim:
        d = pygame.Surface((W, H), pygame.SRCALPHA)
        d.fill((0, 0, 0, dim))
        surf.blit(d, (0, 0))


def clouds(surf):
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


def backdrop(surf, dim=0):
    sky_with_stars(surf, dim=dim)
    clouds(surf)
    mountains_layered(surf)


def big_title(surf, text, center, size=60, fill=GOLD_BRIGHT,
              outline=RED_OUTLINE, px_scale=3):
    cx, cy = center
    f = font(size, True)
    img = f.render(text, True, fill)
    out = f.render(text, True, outline)
    sh = f.render(text, True, NEAR_BLACK)
    r = img.get_rect(center=(cx, cy))
    px = px_scale * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + 3 * SCALE, r.y + 5 * SCALE))
    surf.blit(img, r.topleft)
    return r


def subtitle(surf, text, center, size=16, fill=GOLD_BRIGHT,
             outline=RED_OUTLINE):
    cx, cy = center
    f = font(size, True)
    img = f.render(text, True, fill)
    out = f.render(text, True, outline)
    r = img.get_rect(center=(cx, cy))
    px = 2 * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    surf.blit(img, r.topleft)
    return r


def divider(surf, cy, width=140, color=GOLD_BRIGHT, alpha=120):
    line = pygame.Surface((width * SCALE, 1 * SCALE), pygame.SRCALPHA)
    line.fill((*color, alpha))
    surf.blit(line, line.get_rect(center=(W // 2, cy)))


def pill(surf, center, text, size=22, min_w=234, h=46, primary=False,
         text_color=CREAM):
    h *= SCALE
    cx, cy = center
    f = font(size, True)
    img = f.render(text, True, text_color)
    w = max(min_w * SCALE, img.get_width() + 50 * SCALE)
    x = cx - w // 2
    y = cy - h // 2
    if primary:
        glow = pygame.Surface((w + 28 * SCALE, h + 28 * SCALE),
                              pygame.SRCALPHA)
        for r in range(12 * SCALE, 0, -SCALE):
            a = int(48 * r / (12 * SCALE))
            pygame.draw.rect(glow, (*GOLD_BRIGHT, a // 4),
                             (14 * SCALE - r, 14 * SCALE - r,
                              w + r * 2, h + r * 2),
                             border_radius=(h + r * 2) // 2)
        surf.blit(glow, (x - 14 * SCALE, y - 14 * SCALE))
    sh = pygame.Surface((w + 4 * SCALE, h + 4 * SCALE), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, w + 4 * SCALE, h + 4 * SCALE),
                     border_radius=(h + 4 * SCALE) // 2)
    surf.blit(sh, (x - 2 * SCALE, y + 6 * SCALE))
    p = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = lerp(SCARLET_TOP, SCARLET_BOT, t)
        pygame.draw.line(p, (*c, 255), (0, yy), (w, yy))
    frost = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2):
        a = int(50 * (1 - yy / (h / 2)))
        pygame.draw.line(frost, (255, 245, 220, a), (0, yy), (w, yy))
    p.blit(frost, (0, 0))
    bsh = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h // 2, h):
        a = int(55 * (yy - h // 2) / (h / 2))
        pygame.draw.line(bsh, (0, 0, 0, a), (0, yy), (w, yy))
    p.blit(bsh, (0, 0))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=h // 2)
    p.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(p, GOLD_BRIGHT, (0, 0, w, h),
                     width=2 * SCALE, border_radius=h // 2)
    pygame.draw.line(p, (*GOLD_BRIGHT, 110),
                     (h // 2, 3 * SCALE),
                     (w - h // 2, 3 * SCALE), 1 * SCALE)
    surf.blit(p, (x, y))
    sh_img = f.render(text, True, SCARLET_SHADOW)
    sh_img.set_alpha(220)
    tr = img.get_rect(center=(cx, cy))
    surf.blit(sh_img, (tr.x + 2 * SCALE, tr.y + 2 * SCALE))
    surf.blit(img, tr)
    return pygame.Rect(x, y, w, h)


def outline_pill(surf, center, text, size=18, min_w=180, h=40):
    """Secondary outline-only pill — gold border, transparent body."""
    h *= SCALE
    cx, cy = center
    f = font(size, True)
    img = f.render(text, True, GOLD_BRIGHT)
    w = max(min_w * SCALE, img.get_width() + 36 * SCALE)
    x = cx - w // 2
    y = cy - h // 2
    p = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(p, (*PANEL_DARK, 180), (0, 0, w, h),
                     border_radius=h // 2)
    pygame.draw.rect(p, GOLD_BRIGHT, (0, 0, w, h),
                     width=2 * SCALE, border_radius=h // 2)
    surf.blit(p, (x, y))
    surf.blit(img, img.get_rect(center=(cx, cy)))
    return pygame.Rect(x, y, w, h)


def card(surf, rect, border_alpha=130, accent_alpha=110, alpha=220,
         radius=14):
    sh = pygame.Surface((rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90),
                     (0, 0, rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                     border_radius=radius * SCALE)
    surf.blit(sh, (rect.x - 2 * SCALE, rect.y + 4 * SCALE))
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*PANEL_DARK, alpha),
                     (0, 0, rect.w, rect.h),
                     border_radius=radius * SCALE)
    pygame.draw.rect(pnl, (*GOLD_BRIGHT, border_alpha),
                     (0, 0, rect.w, rect.h),
                     width=1 * SCALE, border_radius=radius * SCALE)
    accent = pygame.Surface((rect.w - 28 * SCALE, 2), pygame.SRCALPHA)
    accent.fill((*GOLD_BRIGHT, accent_alpha))
    pnl.blit(accent, (14 * SCALE, 4))
    pygame.draw.line(pnl, (255, 220, 140, 90),
                     (14 * SCALE, 2),
                     (rect.w - 14 * SCALE, 2), 1 * SCALE)
    surf.blit(pnl, rect.topleft)


def score_emblem(surf, cx, cy, r, label, value, with_ribbon=False):
    sh = pygame.Surface((r * 2 + 16, r * 2 + 16), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 95), (r + 8, r + 8), r + 2)
    surf.blit(sh, (cx - r - 8, cy - r + 4))
    pygame.draw.circle(surf, PANEL_DARK, (cx, cy), r)
    glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for rr in range(r - 6 * SCALE, 0, -SCALE):
        a = int(14 * (1 - rr / (r - 6 * SCALE)))
        pygame.draw.circle(glow, (255, 220, 140, a),
                           (r, r - r // 4), rr)
    surf.blit(glow, (cx - r, cy - r))
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), r, 3 * SCALE)
    pygame.draw.circle(surf, SCARLET_TOP, (cx, cy), r - 4 * SCALE, 2 * SCALE)
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), r - 9 * SCALE, 1 * SCALE)
    for ang_deg in range(0, 360, 12):
        a = math.radians(ang_deg - 90)
        x1 = cx + math.cos(a) * (r - 1 * SCALE)
        y1 = cy + math.sin(a) * (r - 1 * SCALE)
        x2 = cx + math.cos(a) * (r + 2 * SCALE)
        y2 = cy + math.sin(a) * (r + 2 * SCALE)
        pygame.draw.line(surf, GOLD_DEEP, (x1, y1), (x2, y2), 1 * SCALE)
    lbl_y = cy - int(r * 0.42)
    lf = font(13, True).render(label, True, GOLD_MUTED)
    lf.set_alpha(230)
    surf.blit(lf, lf.get_rect(center=(cx, lbl_y)))
    val_size = max(16, int(r * 0.55 / SCALE))
    vf = font(val_size, True).render(str(value), True, GOLD_BRIGHT)
    vs = font(val_size, True).render(str(value), True, NEAR_BLACK)
    vs.set_alpha(180)
    vr = vf.get_rect(center=(cx, cy + int(r * 0.15)))
    surf.blit(vs, (vr.x + 2 * SCALE, vr.y + 3 * SCALE))
    surf.blit(vf, vr)
    if with_ribbon:
        ribbon_pts = [
            (cx - int(r * 0.42), cy + r - 2 * SCALE),
            (cx + int(r * 0.42), cy + r - 2 * SCALE),
            (cx + int(r * 0.32), cy + r + 16 * SCALE),
            (cx, cy + r + 9 * SCALE),
            (cx - int(r * 0.32), cy + r + 16 * SCALE),
        ]
        pygame.draw.polygon(surf, SCARLET_TOP, ribbon_pts)
        pygame.draw.polygon(surf, SCARLET_SHADOW, ribbon_pts, 1 * SCALE)


# ── New small primitives used only by these mockups ─────────────────────────

def hex_medal(surf, cx, cy, size, letter, ring=GOLD_BRIGHT,
              face=PANEL_DARK, sub_label="RANK"):
    """Hex grade medal — beveled hexagon with a chunky letter inside."""
    s = size * SCALE
    pts = []
    for i in range(6):
        a = math.radians(60 * i - 90)
        pts.append((cx + math.cos(a) * s, cy + math.sin(a) * s))
    sh_pts = [(p[0], p[1] + 5 * SCALE) for p in pts]
    sh_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(sh_surf, (0, 0, 0, 110), sh_pts)
    surf.blit(sh_surf, (0, 0))
    pygame.draw.polygon(surf, face, pts)
    pygame.draw.polygon(surf, ring, pts, 3 * SCALE)
    inner_pts = []
    for i in range(6):
        a = math.radians(60 * i - 90)
        inner_pts.append((cx + math.cos(a) * (s - 6 * SCALE),
                          cy + math.sin(a) * (s - 6 * SCALE)))
    pygame.draw.polygon(surf, GOLD_DEEP, inner_pts, 1 * SCALE)
    # Top inner highlight
    pygame.draw.line(surf, GOLD_PALE,
                     (cx - s * 0.45, cy - s * 0.78),
                     (cx + s * 0.45, cy - s * 0.78), 1 * SCALE)
    # Letter
    letter_size = max(18, int(size * 0.85))
    lf = font(letter_size, True).render(letter, True, GOLD_BRIGHT)
    lo = font(letter_size, True).render(letter, True, RED_OUTLINE)
    lsh = font(letter_size, True).render(letter, True, NEAR_BLACK)
    lr = lf.get_rect(center=(cx, cy + 2 * SCALE))
    px = 2 * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(lo, (lr.x + ox, lr.y + oy))
    lsh.set_alpha(170)
    surf.blit(lsh, (lr.x + 1 * SCALE, lr.y + 2 * SCALE))
    surf.blit(lf, lr)
    if sub_label:
        sl = font(10, True).render(sub_label, True, GOLD_MUTED)
        sl.set_alpha(220)
        surf.blit(sl, sl.get_rect(center=(cx, cy + s + 12 * SCALE)))


def stat_icon(surf, kind, cx, cy, size):
    """Tiny gold glyph for stat tiles. kind: time | coin | pillar |
    bolt | crosshair | trophy | flag | skull."""
    s = size * SCALE
    if kind == "time":
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), s, 2 * SCALE)
        for ang in range(0, 360, 90):
            a = math.radians(ang - 90)
            x1 = cx + math.cos(a) * (s - 2 * SCALE)
            y1 = cy + math.sin(a) * (s - 2 * SCALE)
            x2 = cx + math.cos(a) * (s - 5 * SCALE)
            y2 = cy + math.sin(a) * (s - 5 * SCALE)
            pygame.draw.line(surf, GOLD_BRIGHT, (x1, y1), (x2, y2), 1 * SCALE)
        # Hands at 1:27 ish — hour to ~1, minute to ~5
        ha = math.radians(45 - 90)
        ma = math.radians(160 - 90)
        pygame.draw.line(surf, GOLD_BRIGHT, (cx, cy),
                         (cx + math.cos(ha) * s * 0.5,
                          cy + math.sin(ha) * s * 0.5), 2 * SCALE)
        pygame.draw.line(surf, GOLD_BRIGHT, (cx, cy),
                         (cx + math.cos(ma) * s * 0.7,
                          cy + math.sin(ma) * s * 0.7), 2 * SCALE)
        pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), 2 * SCALE)
    elif kind == "coin":
        # Use the actual in-game coin face — matches what the player
        # sees mid-flight (twisted-rope rim, gold gradient, embossed
        # parrot). Capped at the in-game native display size so the
        # coin reads at the same scale the player's eye is calibrated
        # to from gameplay (never blown up beyond its true on-screen
        # footprint).
        face = _ingame_coin_face()
        in_game_d = (COIN_R * 2 + 4) * SCALE
        target_d = min(int(s * 2.6), in_game_d)
        scaled = pygame.transform.smoothscale(face, (target_d, target_d))
        surf.blit(scaled, scaled.get_rect(center=(cx, cy)))
    elif kind == "pillar":
        # Small stone pillar silhouette
        w = s * 1.0
        pygame.draw.rect(surf, GOLD_BRIGHT,
                         (cx - w // 2, cy - s, w, s * 2),
                         border_radius=int(2 * SCALE))
        pygame.draw.rect(surf, GOLD_DEEP,
                         (cx - w // 2, cy - s, w, s * 2),
                         width=1 * SCALE, border_radius=int(2 * SCALE))
        # Cap
        pygame.draw.rect(surf, GOLD_BRIGHT,
                         (cx - w // 2 - 2 * SCALE, cy - s - 2 * SCALE,
                          w + 4 * SCALE, 4 * SCALE),
                         border_radius=int(1 * SCALE))
        pygame.draw.rect(surf, GOLD_DEEP,
                         (cx - w // 2 - 2 * SCALE, cy - s - 2 * SCALE,
                          w + 4 * SCALE, 4 * SCALE),
                         width=1 * SCALE, border_radius=int(1 * SCALE))
    elif kind == "flap":
        # Falcon wings — chosen variant. Inlined here at a slightly
        # compressed aspect ratio so the wingspan fits the tile width
        # and the vertical height matches the visual weight of the
        # clock/coin/pillar icons.
        for sign in (-1, 1):
            wing_pts = [
                (cx + sign * s * 0.04, cy - s * 0.30),
                (cx + sign * s * 0.30, cy - s * 0.60),
                (cx + sign * s * 0.80, cy - s * 0.62),
                (cx + sign * s * 1.20, cy - s * 0.18),
                (cx + sign * s * 1.35, cy + s * 0.10),
                (cx + sign * s * 1.05, cy + s * 0.20),
                (cx + sign * s * 0.95, cy + s * 0.50),
                (cx + sign * s * 0.65, cy + s * 0.25),
                (cx + sign * s * 0.45, cy + s * 0.35),
                (cx + sign * s * 0.22, cy + s * 0.12),
                (cx + sign * s * 0.04, cy + s * 0.00),
            ]
            pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
            pygame.draw.polygon(surf, GOLD_DEEP, wing_pts,
                                max(1, int(SCALE)))
            # Sleek diagonal feather lines for detail
            for sf, tf in [((0.20, -0.42), (1.30, 0.05)),
                           ((0.25, -0.32), (1.05, 0.18)),
                           ((0.30, -0.15), (0.85, 0.40)),
                           ((0.35, -0.00), (0.60, 0.25))]:
                pygame.draw.line(
                    surf, GOLD_DEEP,
                    (cx + sign * sf[0] * s, cy + sf[1] * s),
                    (cx + sign * tf[0] * s, cy + tf[1] * s),
                    max(1, int(SCALE)))
    elif kind == "bolt":
        pts = [(cx - s * 0.3, cy - s),
               (cx + s * 0.5, cy - s * 0.1),
               (cx + s * 0.05, cy - s * 0.05),
               (cx + s * 0.4, cy + s),
               (cx - s * 0.4, cy + s * 0.1),
               (cx + s * 0.1, cy + s * 0.05)]
        pygame.draw.polygon(surf, GOLD_BRIGHT, pts)
        pygame.draw.polygon(surf, GOLD_DEEP, pts, 1 * SCALE)
    elif kind == "crosshair":
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), s, 2 * SCALE)
        pygame.draw.line(surf, GOLD_BRIGHT,
                         (cx - s - 3 * SCALE, cy),
                         (cx + s + 3 * SCALE, cy), 1 * SCALE)
        pygame.draw.line(surf, GOLD_BRIGHT,
                         (cx, cy - s - 3 * SCALE),
                         (cx, cy + s + 3 * SCALE), 1 * SCALE)
        pygame.draw.circle(surf, SCARLET_TOP, (cx, cy), max(2, s // 3))
    elif kind == "flag":
        # Pole
        pygame.draw.line(surf, GOLD_BRIGHT,
                         (cx - s * 0.5, cy - s),
                         (cx - s * 0.5, cy + s), 2 * SCALE)
        # Banner
        pts = [(cx - s * 0.5, cy - s),
               (cx + s, cy - s * 0.5),
               (cx - s * 0.5, cy)]
        pygame.draw.polygon(surf, SCARLET_TOP, pts)
        pygame.draw.polygon(surf, GOLD_DEEP, pts, 1 * SCALE)
    elif kind == "skull":
        # Tiny stylised skull
        pygame.draw.circle(surf, CREAM, (cx, cy - 1 * SCALE), int(s * 0.85))
        pygame.draw.rect(surf, CREAM,
                         (cx - s * 0.5, cy + s * 0.3,
                          s, s * 0.5))
        pygame.draw.circle(surf, NEAR_BLACK,
                           (cx - int(s * 0.3), cy - 1 * SCALE),
                           max(2, int(s * 0.18)))
        pygame.draw.circle(surf, NEAR_BLACK,
                           (cx + int(s * 0.3), cy - 1 * SCALE),
                           max(2, int(s * 0.18)))
        pygame.draw.line(surf, NEAR_BLACK,
                         (cx - 2 * SCALE, cy + s * 0.45),
                         (cx + 2 * SCALE, cy + s * 0.45), 2 * SCALE)
    elif kind == "share":
        # Three connected dots — classic share glyph
        nodes = [
            (cx - s * 0.55, cy + s * 0.55),  # bottom-left
            (cx + s * 0.6,  cy),              # right
            (cx - s * 0.55, cy - s * 0.55),  # top-left
        ]
        pygame.draw.line(surf, GOLD_BRIGHT, nodes[0], nodes[1], 2 * SCALE)
        pygame.draw.line(surf, GOLD_BRIGHT, nodes[1], nodes[2], 2 * SCALE)
        for nx, ny in nodes:
            pygame.draw.circle(surf, GOLD_BRIGHT,
                               (int(nx), int(ny)), 4 * SCALE)
            pygame.draw.circle(surf, NEAR_BLACK,
                               (int(nx), int(ny)), 4 * SCALE, 1 * SCALE)


def draw_biome_icon(surf, biome_name, cx, cy, size):
    """Tiny glyph representing a biome phase. Drawn in gold so the chip
    keeps the established colour language regardless of which phase
    was reached."""
    s = size * SCALE
    name = (biome_name or "DAY").upper()
    if "NIGHT" in name:
        # Crescent moon
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), int(s))
        pygame.draw.circle(surf, PANEL_DARK,
                           (int(cx + s * 0.35), cy - int(s * 0.05)),
                           int(s * 0.85))
    elif "DUSK" in name or "PREDAWN" in name:
        # Half moon + small twinkle
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), int(s))
        pygame.draw.rect(surf, PANEL_DARK,
                         (cx - int(s), cy - int(s),
                          int(s), int(s * 2)))
        # Tiny star sparkle
        pygame.draw.circle(surf, GOLD_BRIGHT,
                           (int(cx + s * 1.2), int(cy - s * 0.6)),
                           1 * SCALE)
    elif "SUNRISE" in name or "SUNSET" in name:
        # Sun half on horizon — semi-circle + horizon line
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy + 1), int(s))
        pygame.draw.rect(surf, PANEL_DARK,
                         (cx - int(s) - 2, cy + 1,
                          int(s) * 2 + 4, int(s) + 4))
        pygame.draw.line(surf, GOLD_BRIGHT,
                         (cx - int(s * 1.4), cy + 1),
                         (cx + int(s * 1.4), cy + 1), 1 * SCALE)
        # Tiny rays
        for dx in (-int(s * 0.6), 0, int(s * 0.6)):
            pygame.draw.line(surf, GOLD_BRIGHT,
                             (cx + dx, cy - int(s) - 1 * SCALE),
                             (cx + dx, cy - int(s) - 4 * SCALE),
                             1 * SCALE)
    elif "GOLDEN" in name:
        # Low sun with horizontal rays
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy + 1), int(s * 0.85))
        for ang_deg in (-160, -110, -70, -20):
            a = math.radians(ang_deg)
            x1 = cx + math.cos(a) * (s + 1 * SCALE)
            y1 = cy + 1 + math.sin(a) * (s + 1 * SCALE)
            x2 = cx + math.cos(a) * (s + 4 * SCALE)
            y2 = cy + 1 + math.sin(a) * (s + 4 * SCALE)
            pygame.draw.line(surf, GOLD_BRIGHT, (x1, y1), (x2, y2),
                             1 * SCALE)
    else:  # DAY / default
        # Full sun with radial rays
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), int(s * 0.7))
        for ang_deg in range(0, 360, 45):
            a = math.radians(ang_deg)
            x1 = cx + math.cos(a) * (s * 0.85)
            y1 = cy + math.sin(a) * (s * 0.85)
            x2 = cx + math.cos(a) * (s * 1.2)
            y2 = cy + math.sin(a) * (s * 1.2)
            pygame.draw.line(surf, GOLD_BRIGHT, (x1, y1), (x2, y2),
                             1 * SCALE)


def biome_chip(surf, center, biome_name, sub_label="REACHED"):
    """Small pill showing the day-cycle phase the player flew through
    by the time the run ended. Sits beside the rank medal in the
    header strip."""
    cx, cy = center
    f = font(11, True)
    txt = f.render(biome_name, True, GOLD_BRIGHT)
    icon_box = 22 * SCALE
    pad_l = 8 * SCALE
    pad_r = 14 * SCALE
    chip_w = pad_l + icon_box + 4 * SCALE + txt.get_width() + pad_r
    chip_h = 32 * SCALE
    rect = pygame.Rect(cx - chip_w // 2, cy - chip_h // 2, chip_w, chip_h)
    # Shadow
    sh = pygame.Surface((chip_w + 4 * SCALE, chip_h + 4 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 110),
                     (0, 0, chip_w + 4 * SCALE, chip_h + 4 * SCALE),
                     border_radius=chip_h // 2)
    surf.blit(sh, (rect.x - 2 * SCALE, rect.y + 4 * SCALE))
    # Body
    body = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(body, (*PANEL_DARK, 230),
                     (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
    pygame.draw.rect(body, GOLD_BRIGHT,
                     (0, 0, chip_w, chip_h),
                     width=2 * SCALE, border_radius=chip_h // 2)
    # Top inner highlight
    pygame.draw.line(body, (*GOLD_PALE, 130),
                     (chip_h // 2, 3 * SCALE),
                     (chip_w - chip_h // 2, 3 * SCALE), 1 * SCALE)
    surf.blit(body, rect.topleft)
    # Icon (centered in icon_box)
    draw_biome_icon(surf, biome_name,
                    rect.x + pad_l + icon_box // 2,
                    rect.centery,
                    size=9)
    # Text
    tx = rect.x + pad_l + icon_box + 4 * SCALE
    surf.blit(txt, (tx, rect.centery - txt.get_height() // 2))
    # Small sub-label beneath
    if sub_label:
        sf = font(8, True).render(sub_label, True, GOLD_MUTED)
        sf.set_alpha(220)
        surf.blit(sf, sf.get_rect(center=(cx, rect.bottom + 12 * SCALE)))


# ── Wing variants for FLAPS tile (user is choosing between these) ──────────

BIRD_WING_BLUE   = ( 40, 100, 255)
BIRD_WING_DARK   = ( 20,  55, 180)
BIRD_TIP_GREEN   = ( 50, 220, 100)
BIRD_STRIPE      = (255, 200,  60)


def draw_wing_pip(surf, cx, cy, s):
    """Variant 1 — Pip's actual scarlet-macaw wing, mirrored for a pair.
    Faithful port of game/parrot.py::_build_wing: cobalt blue body,
    darker underside, lime-green primary tips, yellow secondary stripe,
    deep-blue feather divider lines."""
    # Source polygon lives on a 50×50 surface with the body anchor at
    # (24, 24) and the wing tip at (44, 13). We rebase so the anchor
    # lands on (cx, cy) and mirror x for the second wing.
    scale = s / 13.0
    for sign in (-1, 1):
        def P(x, y):
            return (cx + sign * (x - 24) * scale,
                    cy + (y - 24) * scale)
        # Drop shadow
        pygame.draw.polygon(surf, (0, 0, 0, 110), [
            P(24, 26), P(46, 14), P(50, 30), P(34, 44), P(18, 40)])
        # Main feather body (vivid blue)
        pygame.draw.polygon(surf, BIRD_WING_BLUE, [
            P(24, 24), P(44, 13), P(48, 28), P(32, 42), P(18, 36)])
        # Darker underside
        pygame.draw.polygon(surf, BIRD_WING_DARK, [
            P(24, 24), P(32, 42), P(18, 36)])
        # Primary feather tips (macaw green)
        pygame.draw.polygon(surf, BIRD_TIP_GREEN, [
            P(44, 13), P(50, 18), P(48, 28)])
        # Yellow secondary stripe
        pygame.draw.polygon(surf, BIRD_STRIPE, [
            P(42, 18), P(48, 22), P(46, 28), P(40, 24)])
        # Feather divider lines
        thick = max(1, int(scale * 0.9))
        pygame.draw.line(surf, BIRD_WING_DARK, P(26, 25), P(42, 18), thick)
        pygame.draw.line(surf, BIRD_WING_DARK, P(28, 30), P(44, 25), thick)
        pygame.draw.line(surf, BIRD_WING_DARK, P(30, 34), P(46, 32), thick)


def draw_wing_bird_silhouette(surf, cx, cy, s):
    """Variant 2 — Bird-in-flight silhouette seen from below. The
    universal "M-curve" wing shape used in every bird logo from
    Twitter to airline emblems. Reads as wings INSTANTLY because
    it's the silhouette every brain associates with birds."""
    thick = max(3, int(SCALE * 1.6))
    pts = [
        (cx - s * 1.10, cy - s * 0.05),
        (cx - s * 0.75, cy - s * 0.50),
        (cx - s * 0.35, cy - s * 0.15),
        (cx,            cy + s * 0.10),
        (cx + s * 0.35, cy - s * 0.15),
        (cx + s * 0.75, cy - s * 0.50),
        (cx + s * 1.10, cy - s * 0.05),
    ]
    pygame.draw.lines(surf, GOLD_BRIGHT, False, pts, thick)
    body_pts = [
        (cx - s * 1.00, cy + s * 0.00),
        (cx - s * 0.55, cy + s * 0.25),
        (cx + s * 0.55, cy + s * 0.25),
        (cx + s * 1.00, cy + s * 0.00),
    ]
    pygame.draw.lines(surf, GOLD_BRIGHT, False, body_pts,
                      max(2, int(SCALE)))


def _unused_angel_template(surf, cx, cy, s):  # kept for reference
    """Variant 2 — Classical angel: smooth leading edge, scalloped
    trailing edge with 5 feather tips, internal quill lines."""
    body_y_off = s * 0.08
    for sign in (-1, 1):
        wing_pts_factors = [
            (0.10, -0.05),
            (0.40, -0.55), (0.85, -0.65), (1.25, -0.55),
            (1.55, -0.20),
            (1.40, 0.10),  (1.35, 0.32),
            (1.15, 0.12),  (1.10, 0.40),
            (0.85, 0.18),  (0.80, 0.42),
            (0.55, 0.22),  (0.50, 0.40),
            (0.30, 0.22),  (0.28, 0.34),
            (0.10, 0.18),
        ]
        wing_pts = [(cx + sign * x * s, cy + y * s + body_y_off)
                    for x, y in wing_pts_factors]
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
        pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
        feather_quills = [
            ((1.10, -0.35), (1.32, 0.30)),
            ((0.90, -0.45), (1.07, 0.38)),
            ((0.65, -0.50), (0.78, 0.40)),
            ((0.42, -0.42), (0.48, 0.38)),
            ((0.22, -0.30), (0.27, 0.32)),
        ]
        for sf, tf in feather_quills:
            pygame.draw.line(
                surf, GOLD_DEEP,
                (cx + sign * sf[0] * s, cy + sf[1] * s + body_y_off),
                (cx + sign * tf[0] * s, cy + tf[1] * s + body_y_off),
                max(1, int(SCALE)))


def draw_wing_cherub(surf, cx, cy, s):
    """Variant 3 — Cherub / cupid wings: small, round, three-scallop
    pair extending outward from a tiny heart-shaped centre. The
    iconography you'd see on a stamp or a wax seal."""
    for sign in (-1, 1):
        scallops = [
            (0.20, -0.30, 0.45, -0.45, 0.60, -0.20),
            (0.20, -0.05, 0.55, -0.10, 0.75,  0.10),
            (0.20,  0.20, 0.50,  0.30, 0.65,  0.40),
        ]
        wing_pts = [(cx + sign * s * 0.05, cy - s * 0.25)]
        for ax, ay, bx, by, cx2, cy2 in scallops:
            wing_pts.append((cx + sign * s * ax, cy + s * ay))
            wing_pts.append((cx + sign * s * bx, cy + s * by))
            wing_pts.append((cx + sign * s * cx2, cy + s * cy2))
        wing_pts.append((cx + sign * s * 0.05, cy + s * 0.30))
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
        pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
        for ax, ay, bx, by, cx2, cy2 in scallops[:-1]:
            pygame.draw.line(
                surf, GOLD_DEEP,
                (cx + sign * s * ax, cy + s * ay),
                (cx + sign * s * cx2, cy + s * cy2),
                max(1, int(SCALE)))
    h = max(3, int(s * 0.18))
    pygame.draw.polygon(surf, GOLD_BRIGHT, [
        (cx - h, cy - 1), (cx, cy + h * 1.2), (cx + h, cy - 1),
        (cx + h * 0.5, cy - h * 0.7),
        (cx, cy - h * 0.3),
        (cx - h * 0.5, cy - h * 0.7),
    ])


def _unused_minimalist_template(surf, cx, cy, s):  # kept for reference
    """Variant 3 — Pure line-art: each wing is a single graceful curved
    stroke. The cleanest, most modern look — no fill, just an outline."""
    thick = max(3, int(SCALE * 2))
    for sign in (-1, 1):
        # Crisp single outline tracing leading-edge, tip, trailing-edge
        # back to body — like a stylised flat icon you'd see in a UI
        pts = [
            (cx + sign * s * 0.05, cy + s * 0.18),       # body bottom
            (cx + sign * s * 0.15, cy - s * 0.10),       # body top
            (cx + sign * s * 0.45, cy - s * 0.55),       # shoulder
            (cx + sign * s * 0.95, cy - s * 0.55),       # leading peak
            (cx + sign * s * 1.30, cy - s * 0.20),       # tip
            (cx + sign * s * 1.05, cy + s * 0.15),       # trailing curve
            (cx + sign * s * 0.55, cy + s * 0.30),       # trailing inner
            (cx + sign * s * 0.10, cy + s * 0.22),       # back to body
            (cx + sign * s * 0.05, cy + s * 0.18),
        ]
        pygame.draw.lines(surf, GOLD_BRIGHT, False, pts, thick)


def draw_wing_aviator_badge(surf, cx, cy, s):
    """Variant 4 — Aviator wings badge: classic military pilot wings.
    Wings extend HORIZONTALLY outward from a central insignia disc
    with a small star inside. The most universally recognised "wings"
    pictogram (military, airline, scouting)."""
    disc_r = max(3, int(s * 0.22))
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), disc_r + 1 * SCALE)
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), disc_r)
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), disc_r,
                       max(1, int(SCALE)))
    star_r = max(1, int(s * 0.10))
    star_pts = []
    for i in range(10):
        a = math.radians(i * 36 - 90)
        r = star_r if i % 2 == 0 else int(star_r * 0.45)
        star_pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    pygame.draw.polygon(surf, GOLD_DEEP, star_pts)
    for sign in (-1, 1):
        feathers = [
            (0.90, -0.32, 0.05),
            (1.10, -0.16, 0.06),
            (1.30,  0.00, 0.07),
            (1.10,  0.16, 0.06),
            (0.90,  0.32, 0.05),
        ]
        for length, y_off, thick_f in feathers:
            base_x = cx + sign * (disc_r + 1 * SCALE)
            tip_x = cx + sign * s * length
            y_mid = cy + s * y_off
            ht = s * thick_f
            pts = [
                (base_x, y_mid - ht * 0.5),
                (base_x + sign * s * length * 0.30, y_mid - ht),
                (tip_x - sign * s * 0.05, y_mid - ht * 0.4),
                (tip_x, y_mid),
                (tip_x - sign * s * 0.05, y_mid + ht * 0.4),
                (base_x + sign * s * length * 0.30, y_mid + ht),
                (base_x, y_mid + ht * 0.5),
            ]
            pygame.draw.polygon(surf, GOLD_BRIGHT, pts)
            pygame.draw.polygon(surf, GOLD_DEEP, pts, max(1, int(SCALE)))


def _unused_phoenix_template(surf, cx, cy, s):  # kept for reference
    """Variant 4 — Phoenix/flame wings: sharper, more aggressive
    angles. Trailing edge has long pointed flame-like feather tips."""
    for sign in (-1, 1):
        wing_pts = [
            (cx + sign * s * 0.08, cy - s * 0.05),
            (cx + sign * s * 0.30, cy - s * 0.55),
            (cx + sign * s * 0.65, cy - s * 0.70),
            (cx + sign * s * 1.10, cy - s * 0.55),
            (cx + sign * s * 1.55, cy - s * 0.15),
            (cx + sign * s * 1.30, cy + s * 0.05),
            (cx + sign * s * 1.50, cy + s * 0.40),
            (cx + sign * s * 1.05, cy + s * 0.08),
            (cx + sign * s * 1.15, cy + s * 0.50),
            (cx + sign * s * 0.75, cy + s * 0.12),
            (cx + sign * s * 0.80, cy + s * 0.55),
            (cx + sign * s * 0.45, cy + s * 0.20),
            (cx + sign * s * 0.40, cy + s * 0.45),
            (cx + sign * s * 0.18, cy + s * 0.25),
            (cx + sign * s * 0.08, cy + s * 0.10),
        ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
        pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
        # Internal diagonal feather lines (sharp, energetic)
        for sf, tf in [((0.30, -0.30), (1.40, 0.30)),
                       ((0.50, -0.50), (1.15, 0.40)),
                       ((0.75, -0.60), (0.85, 0.45)),
                       ((0.25, -0.15), (0.45, 0.40))]:
            pygame.draw.line(
                surf, GOLD_DEEP,
                (cx + sign * sf[0] * s, cy + sf[1] * s),
                (cx + sign * tf[0] * s, cy + tf[1] * s),
                max(1, int(SCALE)))


def draw_wing_feather(surf, cx, cy, s):
    """Variant 5 — Single feather quill: a stylised plume with a curved
    central spine and barb lines on each side. Universal feather icon
    (matches the Font Awesome / Lucide style)."""
    tip = (cx - s * 0.70, cy - s * 0.80)
    base = (cx + s * 0.45, cy + s * 0.90)
    blade_pts = [
        tip,
        (cx + s * 0.05, cy - s * 0.60),
        (cx + s * 0.50, cy - s * 0.20),
        (cx + s * 0.72, cy + s * 0.20),
        (cx + s * 0.62, cy + s * 0.60),
        base,
        (cx + s * 0.10, cy + s * 0.45),
        (cx - s * 0.20, cy + s * 0.05),
        (cx - s * 0.50, cy - s * 0.35),
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, blade_pts)
    pygame.draw.polygon(surf, GOLD_DEEP, blade_pts, max(1, int(SCALE)))
    pygame.draw.line(surf, GOLD_DEEP, tip, base,
                     max(2, int(SCALE * 1.4)))
    spine_segments = 8
    dx = base[0] - tip[0]
    dy = base[1] - tip[1]
    length = math.hypot(dx, dy)
    px = -dy / length
    py = dx / length
    for i in range(1, spine_segments):
        t = i / spine_segments
        sx = tip[0] + dx * t
        sy = tip[1] + dy * t
        barb_len = s * 0.30 * (1.0 - abs(t - 0.45) * 1.3)
        if barb_len < 2:
            continue
        for bsign in (-1, 1):
            tilt = 0.30
            bx = sx + bsign * (px * barb_len - (dx / length) * barb_len * tilt)
            by = sy + bsign * (py * barb_len - (dy / length) * barb_len * tilt)
            pygame.draw.line(surf, GOLD_DEEP, (sx, sy), (bx, by),
                             max(1, int(SCALE)))


def _unused_heraldic_template(surf, cx, cy, s):  # kept for reference
    """Variant 5 — Heraldic crest wings: three distinct stacked
    feather tiers per side, scalloped, very geometric. Reads like a
    military patch or coat of arms."""
    tiers = [
        # (length_factor, half_height, y_offset, scallop_count)
        (1.20, 0.18, -0.35, 3),  # top tier — shortest
        (1.40, 0.20,  0.00, 4),  # middle tier — widest
        (1.25, 0.18,  0.30, 3),  # bottom tier — medium
    ]
    for sign in (-1, 1):
        for length, half_h, y_off, n_scallops in tiers:
            # Build a wedge with scalloped trailing edge along bottom
            pts = [(cx + sign * s * 0.10, cy + s * (y_off - half_h)),  # body top
                   (cx + sign * s * length * 0.6,
                    cy + s * (y_off - half_h * 1.05)),                # outer top
                   (cx + sign * s * length, cy + s * y_off)]          # tip
            # Scalloped bottom going back to body
            for i in range(n_scallops + 1):
                t = 1.0 - i / n_scallops
                # Valley between feathers
                vx = cx + sign * s * length * t
                vy = cy + s * (y_off + half_h * 0.6)
                pts.append((vx, vy))
                # Feather tip (lower than valley)
                if i < n_scallops:
                    t_next = 1.0 - (i + 0.5) / n_scallops
                    tx = cx + sign * s * length * t_next
                    ty = cy + s * (y_off + half_h * 1.15)
                    pts.append((tx, ty))
            # Close back to body
            pts.append((cx + sign * s * 0.10, cy + s * (y_off + half_h)))
            pygame.draw.polygon(surf, GOLD_BRIGHT, pts)
            pygame.draw.polygon(surf, GOLD_DEEP, pts, max(1, int(SCALE)))


def draw_wing_butterfly(surf, cx, cy, s):
    """Variant 1 — Butterfly: two symmetric wing lobes per side
    (upper + lower) with a slim central body and antennae. Clean
    butterfly silhouette."""
    body_w = max(2, int(s * 0.08))
    body_h = int(s * 0.70)
    pygame.draw.ellipse(
        surf, GOLD_DEEP,
        (cx - body_w, cy - body_h // 2, body_w * 2, body_h))
    pygame.draw.line(
        surf, GOLD_DEEP,
        (cx - body_w, cy - body_h // 2),
        (int(cx - s * 0.35), int(cy - body_h // 2 - s * 0.25)),
        max(1, int(SCALE)))
    pygame.draw.line(
        surf, GOLD_DEEP,
        (cx + body_w, cy - body_h // 2),
        (int(cx + s * 0.35), int(cy - body_h // 2 - s * 0.25)),
        max(1, int(SCALE)))
    for sign in (-1, 1):
        upper_wing = [
            (cx + sign * body_w, cy - s * 0.25),
            (cx + sign * s * 0.35, cy - s * 0.70),
            (cx + sign * s * 0.85, cy - s * 0.60),
            (cx + sign * s * 1.10, cy - s * 0.25),
            (cx + sign * s * 0.95, cy + s * 0.00),
            (cx + sign * s * 0.55, cy + s * 0.05),
            (cx + sign * body_w, cy - s * 0.05),
        ]
        lower_wing = [
            (cx + sign * body_w, cy + s * 0.05),
            (cx + sign * s * 0.55, cy + s * 0.05),
            (cx + sign * s * 0.85, cy + s * 0.30),
            (cx + sign * s * 0.65, cy + s * 0.65),
            (cx + sign * s * 0.25, cy + s * 0.55),
            (cx + sign * body_w, cy + s * 0.30),
        ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, upper_wing)
        pygame.draw.polygon(surf, GOLD_DEEP, upper_wing, max(1, int(SCALE)))
        pygame.draw.polygon(surf, GOLD_BRIGHT, lower_wing)
        pygame.draw.polygon(surf, GOLD_DEEP, lower_wing, max(1, int(SCALE)))
        pygame.draw.circle(
            surf, GOLD_DEEP,
            (int(cx + sign * s * 0.65), int(cy - s * 0.35)),
            max(2, int(s * 0.10)))


def draw_bird_overhead(surf, cx, cy, s):
    """Variant 2 — Bird from above: the classic M-silhouette + body
    line of a bird in flight seen from below. Most iconic 'bird in
    flight' shape used in logos worldwide."""
    thick = max(3, int(SCALE * 1.6))
    pts = [
        (cx - s * 1.10, cy - s * 0.05),
        (cx - s * 0.75, cy - s * 0.50),
        (cx - s * 0.35, cy - s * 0.15),
        (cx,            cy + s * 0.10),
        (cx + s * 0.35, cy - s * 0.15),
        (cx + s * 0.75, cy - s * 0.50),
        (cx + s * 1.10, cy - s * 0.05),
    ]
    pygame.draw.lines(surf, GOLD_BRIGHT, False, pts, thick)
    body_pts = [
        (cx - s * 1.00, cy + s * 0.00),
        (cx - s * 0.55, cy + s * 0.25),
        (cx + s * 0.55, cy + s * 0.25),
        (cx + s * 1.00, cy + s * 0.00),
    ]
    pygame.draw.lines(surf, GOLD_BRIGHT, False, body_pts,
                      max(2, int(SCALE)))


def draw_bird_spread_eagle(surf, cx, cy, s):
    """Variant 3 — Spread eagle: full bird body with wings outstretched
    horizontally to each side. Has a body, head, and tail — reads as a
    raptor seen from below."""
    # Body (vertical oval) + head circle + small tail wedge
    body_w = max(3, int(s * 0.18))
    body_h = int(s * 0.6)
    pygame.draw.ellipse(
        surf, GOLD_BRIGHT,
        (cx - body_w, cy - body_h // 2, body_w * 2, body_h))
    pygame.draw.ellipse(
        surf, GOLD_DEEP,
        (cx - body_w, cy - body_h // 2, body_w * 2, body_h),
        max(1, int(SCALE)))
    # Head
    head_r = max(2, int(s * 0.13))
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy - body_h // 2 - head_r // 2),
                       head_r)
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy - body_h // 2 - head_r // 2),
                       head_r, max(1, int(SCALE)))
    # Tail (downward triangle below body)
    tail_pts = [
        (cx - body_w // 2, cy + body_h // 2 - 1 * SCALE),
        (cx + body_w // 2, cy + body_h // 2 - 1 * SCALE),
        (cx, cy + body_h // 2 + int(s * 0.30)),
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, tail_pts)
    pygame.draw.polygon(surf, GOLD_DEEP, tail_pts, max(1, int(SCALE)))
    # Wings: large outstretched horizontal triangles each side
    for sign in (-1, 1):
        wing = [
            (cx + sign * body_w, cy - s * 0.15),
            (cx + sign * s * 1.30, cy - s * 0.35),
            (cx + sign * s * 1.30, cy + s * 0.05),
            (cx + sign * body_w, cy + s * 0.15),
        ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing)
        pygame.draw.polygon(surf, GOLD_DEEP, wing, max(1, int(SCALE)))


def draw_bird_dove(surf, cx, cy, s):
    """Variant 4 — Stylised flying dove (peace-dove style): a single
    fluid bird silhouette with a curved body, raised wings, and a
    sweeping tail. Reads instantly as 'bird'."""
    # Body — single fluid polygon
    body_pts = [
        (cx - s * 0.95, cy + s * 0.10),    # tail tip
        (cx - s * 0.55, cy + s * 0.05),    # tail base upper
        (cx - s * 0.30, cy + s * 0.30),    # belly low
        (cx + s * 0.10, cy + s * 0.40),    # belly far
        (cx + s * 0.60, cy + s * 0.10),    # chest
        (cx + s * 0.95, cy - s * 0.20),    # head/beak tip
        (cx + s * 0.50, cy - s * 0.20),    # head back
        (cx + s * 0.10, cy - s * 0.05),    # neck back
        (cx - s * 0.10, cy - s * 0.20),    # wing-attach
        (cx - s * 0.30, cy + s * 0.00),    # back
        (cx - s * 0.55, cy + s * 0.15),    # tail base lower
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, body_pts)
    pygame.draw.polygon(surf, GOLD_DEEP, body_pts, max(1, int(SCALE)))
    # Raised wing — single sweeping curved shape above body
    wing_pts = [
        (cx - s * 0.05, cy - s * 0.15),
        (cx - s * 0.25, cy - s * 0.60),
        (cx + s * 0.20, cy - s * 0.85),
        (cx + s * 0.50, cy - s * 0.60),
        (cx + s * 0.45, cy - s * 0.30),
        (cx + s * 0.20, cy - s * 0.20),
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
    pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
    # Eye dot
    pygame.draw.circle(surf, GOLD_DEEP,
                       (int(cx + s * 0.65), int(cy - s * 0.18)),
                       max(1, int(s * 0.05)))


def draw_bird_wing_side(surf, cx, cy, s):
    """Variant 5 — Side view of a single bird wing: like the wing on a
    heraldic emblem. Smooth top edge, tapered tip, scalloped trailing
    edge with three feather notches."""
    # Single side-view wing pointing right (with mirror disabled)
    # Centered so the wing fills the icon area horizontally
    wing_pts = [
        (cx - s * 1.05, cy + s * 0.25),    # body attach bottom
        (cx - s * 0.85, cy - s * 0.20),    # body attach top
        (cx - s * 0.40, cy - s * 0.65),    # shoulder
        (cx + s * 0.20, cy - s * 0.70),    # leading edge
        (cx + s * 0.85, cy - s * 0.45),    # leading top
        (cx + s * 1.15, cy - s * 0.05),    # tip
        # Trailing edge with 3 feather notches
        (cx + s * 0.85, cy + s * 0.10),
        (cx + s * 0.95, cy + s * 0.45),    # feather tip 1
        (cx + s * 0.50, cy + s * 0.20),
        (cx + s * 0.60, cy + s * 0.55),    # feather tip 2
        (cx + s * 0.15, cy + s * 0.30),
        (cx + s * 0.20, cy + s * 0.55),    # feather tip 3
        (cx - s * 0.30, cy + s * 0.40),
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
    pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
    # 3 internal feather divider lines
    for sf, tf in [((-0.65, -0.30), (0.95, 0.40)),
                   ((-0.35, -0.50), (0.60, 0.50)),
                   ((+0.05, -0.55), (0.20, 0.50))]:
        pygame.draw.line(
            surf, GOLD_DEEP,
            (cx + sf[0] * s, cy + sf[1] * s),
            (cx + tf[0] * s, cy + tf[1] * s),
            max(1, int(SCALE)))


def _bird_body_and_head(surf, cx, cy, s, body_color=GOLD_BRIGHT,
                        outline=GOLD_DEEP, beak_color=None,
                        head_size=0.18, body_height=0.55):
    """Shared body + head + beak helper. Returns (head_y) so each
    variant can build its tail relative to the body."""
    beak_color = beak_color or outline
    # Body — vertical teardrop
    bh = s * body_height
    body_pts = [
        (cx - s * 0.18, cy - bh * 0.50),
        (cx - s * 0.22, cy + bh * 0.05),
        (cx - s * 0.16, cy + bh * 0.45),
        (cx + s * 0.16, cy + bh * 0.45),
        (cx + s * 0.22, cy + bh * 0.05),
        (cx + s * 0.18, cy - bh * 0.50),
    ]
    pygame.draw.polygon(surf, body_color, body_pts)
    pygame.draw.polygon(surf, outline, body_pts, max(1, int(SCALE)))
    # Head
    head_r = max(3, int(s * head_size))
    head_y = cy - bh * 0.50 - head_r * 0.6
    pygame.draw.circle(surf, body_color, (cx, int(head_y)), head_r)
    pygame.draw.circle(surf, outline, (cx, int(head_y)), head_r,
                       max(1, int(SCALE)))
    # Eye
    pygame.draw.circle(surf, outline,
                       (int(cx + head_r * 0.4),
                        int(head_y - head_r * 0.15)),
                       max(1, int(s * 0.04)))
    # Beak — small triangle pointing down
    beak_pts = [
        (cx - head_r * 0.30, head_y + head_r * 0.65),
        (cx + head_r * 0.30, head_y + head_r * 0.65),
        (cx, head_y + head_r * 1.20),
    ]
    pygame.draw.polygon(surf, beak_color, beak_pts)
    return head_y, bh


def draw_bird_eagle_detailed(surf, cx, cy, s):
    """Variant 1 — EAGLE: wide outstretched wings with five scalloped
    primary feathers each side, sharp head with beak, fan tail. The
    classic 'mighty eagle in flight' silhouette."""
    head_y, bh = _bird_body_and_head(surf, cx, cy, s)
    # Tail — short fan below body
    tail_pts = [
        (cx - s * 0.18, cy + bh * 0.40),
        (cx - s * 0.28, cy + s * 0.75),
        (cx - s * 0.10, cy + s * 0.80),
        (cx,            cy + s * 0.85),
        (cx + s * 0.10, cy + s * 0.80),
        (cx + s * 0.28, cy + s * 0.75),
        (cx + s * 0.18, cy + bh * 0.40),
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, tail_pts)
    pygame.draw.polygon(surf, GOLD_DEEP, tail_pts, max(1, int(SCALE)))
    # Tail feather divider lines
    for fx in (-0.10, 0.0, 0.10):
        pygame.draw.line(surf, GOLD_DEEP,
                         (cx + fx * s, cy + bh * 0.40),
                         (cx + fx * 1.5 * s, cy + s * 0.80),
                         max(1, int(SCALE)))
    # Wings — wide outstretched with scalloped trailing edge
    for sign in (-1, 1):
        wing_pts = [
            (cx + sign * s * 0.20, cy - s * 0.20),       # body attach top
            (cx + sign * s * 0.50, cy - s * 0.45),       # shoulder
            (cx + sign * s * 0.95, cy - s * 0.50),       # leading edge top
            (cx + sign * s * 1.40, cy - s * 0.30),       # near wingtip
            (cx + sign * s * 1.60, cy - s * 0.05),       # wingtip
            # Trailing edge with 5 primary feather tips
            (cx + sign * s * 1.45, cy + s * 0.10),
            (cx + sign * s * 1.50, cy + s * 0.40),       # primary 1
            (cx + sign * s * 1.20, cy + s * 0.15),
            (cx + sign * s * 1.20, cy + s * 0.45),       # primary 2
            (cx + sign * s * 0.95, cy + s * 0.20),
            (cx + sign * s * 0.90, cy + s * 0.45),       # primary 3
            (cx + sign * s * 0.70, cy + s * 0.20),
            (cx + sign * s * 0.60, cy + s * 0.40),       # primary 4
            (cx + sign * s * 0.45, cy + s * 0.18),
            (cx + sign * s * 0.35, cy + s * 0.35),       # primary 5
            (cx + sign * s * 0.22, cy + s * 0.15),       # body attach bot
        ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
        pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
        # Primary feather quill lines
        for sf, tf in [((0.35, -0.30), (1.48, 0.36)),
                       ((0.40, -0.30), (1.20, 0.42)),
                       ((0.45, -0.25), (0.88, 0.42)),
                       ((0.45, -0.18), (0.58, 0.38)),
                       ((0.45, -0.10), (0.34, 0.32))]:
            pygame.draw.line(
                surf, GOLD_DEEP,
                (cx + sign * sf[0] * s, cy + sf[1] * s),
                (cx + sign * tf[0] * s, cy + tf[1] * s),
                max(1, int(SCALE)))
        # Secondary feather hint — short curved line behind shoulder
        pygame.draw.lines(
            surf, GOLD_DEEP, False,
            [(cx + sign * s * 0.35, cy - s * 0.15),
             (cx + sign * s * 0.55, cy - s * 0.05),
             (cx + sign * s * 0.95, cy + s * 0.00),
             (cx + sign * s * 1.30, cy + s * 0.05)],
            max(1, int(SCALE)))


def draw_bird_falcon_swept(surf, cx, cy, s):
    """Variant 2 — FALCON: sleek pointed wings swept back, sharp
    forked tail, slim aerodynamic body. Sense of speed."""
    head_y, bh = _bird_body_and_head(surf, cx, cy, s, head_size=0.15,
                                     body_height=0.45)
    # Forked tail
    tail_pts = [
        (cx - s * 0.18, cy + bh * 0.40),
        (cx - s * 0.22, cy + s * 0.80),
        (cx - s * 0.04, cy + s * 0.65),
        (cx,            cy + s * 0.85),
        (cx + s * 0.04, cy + s * 0.65),
        (cx + s * 0.22, cy + s * 0.80),
        (cx + s * 0.18, cy + bh * 0.40),
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, tail_pts)
    pygame.draw.polygon(surf, GOLD_DEEP, tail_pts, max(1, int(SCALE)))
    # Wings — sweptback pointed silhouette, sharper trailing edge
    for sign in (-1, 1):
        wing_pts = [
            (cx + sign * s * 0.18, cy - s * 0.15),
            (cx + sign * s * 0.45, cy - s * 0.35),
            (cx + sign * s * 0.95, cy - s * 0.30),
            (cx + sign * s * 1.40, cy - s * 0.05),    # tip far back
            (cx + sign * s * 1.55, cy + s * 0.20),    # actual tip (swept)
            (cx + sign * s * 1.20, cy + s * 0.20),
            (cx + sign * s * 1.10, cy + s * 0.40),    # trailing flare
            (cx + sign * s * 0.75, cy + s * 0.25),
            (cx + sign * s * 0.55, cy + s * 0.30),
            (cx + sign * s * 0.22, cy + s * 0.10),
        ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
        pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
        # Sleek feather lines — diagonal from shoulder to tip
        for sf, tf in [((0.35, -0.25), (1.50, 0.15)),
                       ((0.40, -0.20), (1.30, 0.18)),
                       ((0.45, -0.10), (1.05, 0.32)),
                       ((0.50, -0.00), (0.75, 0.25))]:
            pygame.draw.line(
                surf, GOLD_DEEP,
                (cx + sign * sf[0] * s, cy + sf[1] * s),
                (cx + sign * tf[0] * s, cy + tf[1] * s),
                max(1, int(SCALE)))


def draw_bird_heraldic_eagle(surf, cx, cy, s):
    """Variant 3 — HERALDIC EAGLE: very symmetric, geometric. Wings
    raised slightly above horizontal in classic coat-of-arms pose.
    Three distinct tiers of feathers per wing, fan tail with notches."""
    head_y, bh = _bird_body_and_head(surf, cx, cy, s, body_height=0.50)
    # Squared fan tail
    tail_pts = [
        (cx - s * 0.20, cy + bh * 0.40),
        (cx - s * 0.30, cy + s * 0.75),
        (cx - s * 0.10, cy + s * 0.70),
        (cx,            cy + s * 0.80),
        (cx + s * 0.10, cy + s * 0.70),
        (cx + s * 0.30, cy + s * 0.75),
        (cx + s * 0.20, cy + bh * 0.40),
    ]
    pygame.draw.polygon(surf, GOLD_BRIGHT, tail_pts)
    pygame.draw.polygon(surf, GOLD_DEEP, tail_pts, max(1, int(SCALE)))
    # Tail feather lines
    for fx in (-0.12, -0.04, 0.04, 0.12):
        pygame.draw.line(surf, GOLD_DEEP,
                         (cx + fx * s, cy + bh * 0.40),
                         (cx + fx * 1.6 * s, cy + s * 0.74),
                         max(1, int(SCALE)))
    # Wings — three stacked feather tiers per side, raised pose
    for sign in (-1, 1):
        tiers = [
            (1.30, 0.18, -0.30, 4),  # top tier (shortest, highest)
            (1.50, 0.20, -0.05, 5),  # middle tier (longest)
            (1.30, 0.18,  0.20, 4),  # bottom tier
        ]
        for length, half_h, y_off, n_scallops in tiers:
            pts = [(cx + sign * s * 0.22, cy + s * (y_off - half_h)),
                   (cx + sign * s * length * 0.55,
                    cy + s * (y_off - half_h * 1.10)),
                   (cx + sign * s * length, cy + s * y_off)]
            for i in range(n_scallops + 1):
                t = 1.0 - i / n_scallops
                vx = cx + sign * s * length * t
                vy = cy + s * (y_off + half_h * 0.55)
                pts.append((vx, vy))
                if i < n_scallops:
                    t_next = 1.0 - (i + 0.5) / n_scallops
                    tx = cx + sign * s * length * t_next
                    ty = cy + s * (y_off + half_h * 1.10)
                    pts.append((tx, ty))
            pts.append((cx + sign * s * 0.22, cy + s * (y_off + half_h)))
            pygame.draw.polygon(surf, GOLD_BRIGHT, pts)
            pygame.draw.polygon(surf, GOLD_DEEP, pts, max(1, int(SCALE)))


def draw_bird_phoenix(surf, cx, cy, s):
    """Variant 4 — PHOENIX: ornate mythical bird with curled upward
    wing tips, long trailing tail plumes, regal pose. Decorative
    feather lines throughout."""
    head_y, bh = _bird_body_and_head(surf, cx, cy, s, head_size=0.16,
                                     body_height=0.50)
    # Long flowing tail plumes (multiple curved feathers below body)
    for sign in (-1, 0, 1):
        plume = [
            (cx + sign * s * 0.10, cy + bh * 0.35),
            (cx + sign * s * 0.30, cy + s * 0.55),
            (cx + sign * s * 0.45, cy + s * 0.85),
            (cx + sign * s * 0.55, cy + s * 1.00) if sign else
                (cx, cy + s * 0.95),
            (cx + sign * s * 0.25, cy + s * 0.80) if sign else
                (cx + s * 0.10, cy + s * 0.70),
            (cx + sign * s * 0.08, cy + s * 0.50) if sign else
                (cx - s * 0.10, cy + s * 0.70),
        ]
        # Center plume slightly different shape
        if sign == 0:
            plume = [
                (cx - s * 0.10, cy + bh * 0.35),
                (cx + s * 0.10, cy + bh * 0.35),
                (cx + s * 0.05, cy + s * 0.95),
                (cx - s * 0.05, cy + s * 0.95),
            ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, plume)
        pygame.draw.polygon(surf, GOLD_DEEP, plume, max(1, int(SCALE)))
    # Wings — outstretched with upward curled tips, decorative
    for sign in (-1, 1):
        wing_pts = [
            (cx + sign * s * 0.20, cy - s * 0.20),
            (cx + sign * s * 0.45, cy - s * 0.40),
            (cx + sign * s * 0.90, cy - s * 0.55),       # shoulder peak
            (cx + sign * s * 1.30, cy - s * 0.65),       # near tip
            (cx + sign * s * 1.55, cy - s * 0.50),       # upcurled tip
            (cx + sign * s * 1.40, cy - s * 0.25),       # back down
            # Trailing edge with 4 ornate plume tips
            (cx + sign * s * 1.20, cy + s * 0.05),
            (cx + sign * s * 1.30, cy + s * 0.35),       # plume tip 1
            (cx + sign * s * 1.00, cy + s * 0.05),
            (cx + sign * s * 1.05, cy + s * 0.40),       # plume tip 2
            (cx + sign * s * 0.75, cy + s * 0.08),
            (cx + sign * s * 0.75, cy + s * 0.40),       # plume tip 3
            (cx + sign * s * 0.50, cy + s * 0.08),
            (cx + sign * s * 0.45, cy + s * 0.32),       # plume tip 4
            (cx + sign * s * 0.25, cy + s * 0.10),
        ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
        pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
        # Ornate plume lines (curved)
        for sf, tf in [((0.40, -0.30), (1.30, 0.32)),
                       ((0.40, -0.30), (1.05, 0.38)),
                       ((0.45, -0.25), (0.75, 0.38)),
                       ((0.45, -0.18), (0.45, 0.30))]:
            pygame.draw.line(
                surf, GOLD_DEEP,
                (cx + sign * sf[0] * s, cy + sf[1] * s),
                (cx + sign * tf[0] * s, cy + tf[1] * s),
                max(1, int(SCALE)))
        # Decorative dots on shoulder
        pygame.draw.circle(surf, GOLD_DEEP,
                           (int(cx + sign * s * 0.55),
                            int(cy - s * 0.25)),
                           max(1, int(s * 0.04)))


def draw_bird_macaw_pip(surf, cx, cy, s):
    """Variant 5 — MACAW (Pip-style): both wings spread in Pip's
    colour palette. Scarlet red body, cobalt blue wings with lime
    green primary tips and a yellow secondary stripe — the same
    palette used for Pip in game/parrot.py."""
    SCARLET = (240, 55, 55)
    SCARLET_D = (170, 25, 25)
    BIRD_BLUE = (40, 100, 255)
    BIRD_BLUE_D = (20, 55, 180)
    BIRD_GREEN = (50, 220, 100)
    YELLOW = (255, 200, 60)
    BEAK = (255, 185, 0)
    BEAK_D = (200, 130, 0)
    BELLY = (255, 170, 50)
    # Body — scarlet teardrop
    bh = s * 0.55
    body_pts = [
        (cx - s * 0.20, cy - bh * 0.50),
        (cx - s * 0.24, cy + bh * 0.05),
        (cx - s * 0.18, cy + bh * 0.45),
        (cx + s * 0.18, cy + bh * 0.45),
        (cx + s * 0.24, cy + bh * 0.05),
        (cx + s * 0.20, cy - bh * 0.50),
    ]
    pygame.draw.polygon(surf, SCARLET, body_pts)
    pygame.draw.polygon(surf, SCARLET_D, body_pts, max(1, int(SCALE)))
    # Yellow belly patch
    belly_pts = [
        (cx - s * 0.14, cy + bh * 0.05),
        (cx + s * 0.14, cy + bh * 0.05),
        (cx + s * 0.10, cy + bh * 0.40),
        (cx - s * 0.10, cy + bh * 0.40),
    ]
    pygame.draw.polygon(surf, BELLY, belly_pts)
    # Head
    head_r = max(3, int(s * 0.18))
    head_y = cy - bh * 0.50 - head_r * 0.6
    pygame.draw.circle(surf, SCARLET, (cx, int(head_y)), head_r)
    pygame.draw.circle(surf, SCARLET_D, (cx, int(head_y)), head_r,
                       max(1, int(SCALE)))
    pygame.draw.circle(surf, (240, 240, 250),
                       (int(cx + head_r * 0.4),
                        int(head_y - head_r * 0.15)),
                       max(2, int(s * 0.05)))
    pygame.draw.circle(surf, NEAR_BLACK,
                       (int(cx + head_r * 0.45),
                        int(head_y - head_r * 0.10)),
                       max(1, int(s * 0.03)))
    # Beak
    beak_pts = [
        (cx - head_r * 0.35, head_y + head_r * 0.65),
        (cx + head_r * 0.35, head_y + head_r * 0.65),
        (cx, head_y + head_r * 1.30),
    ]
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.polygon(surf, BEAK_D, beak_pts, max(1, int(SCALE)))
    # Tail — short scarlet
    tail_pts = [
        (cx - s * 0.12, cy + bh * 0.40),
        (cx - s * 0.20, cy + s * 0.65),
        (cx - s * 0.05, cy + s * 0.75),
        (cx + s * 0.05, cy + s * 0.75),
        (cx + s * 0.20, cy + s * 0.65),
        (cx + s * 0.12, cy + bh * 0.40),
    ]
    pygame.draw.polygon(surf, SCARLET, tail_pts)
    pygame.draw.polygon(surf, SCARLET_D, tail_pts, max(1, int(SCALE)))
    # Wings — blue with green tips, yellow stripe, dark blue dividers
    for sign in (-1, 1):
        wing_pts = [
            (cx + sign * s * 0.22, cy - s * 0.15),
            (cx + sign * s * 0.45, cy - s * 0.40),
            (cx + sign * s * 0.95, cy - s * 0.50),
            (cx + sign * s * 1.35, cy - s * 0.30),
            (cx + sign * s * 1.55, cy - s * 0.05),
            (cx + sign * s * 1.45, cy + s * 0.15),
            (cx + sign * s * 1.10, cy + s * 0.20),
            (cx + sign * s * 0.70, cy + s * 0.20),
            (cx + sign * s * 0.32, cy + s * 0.10),
        ]
        pygame.draw.polygon(surf, BIRD_BLUE, wing_pts)
        pygame.draw.polygon(surf, BIRD_BLUE_D, wing_pts, max(1, int(SCALE)))
        # Underside (darker)
        underside_pts = [
            (cx + sign * s * 0.22, cy - s * 0.05),
            (cx + sign * s * 0.45, cy + s * 0.10),
            (cx + sign * s * 0.32, cy + s * 0.10),
        ]
        pygame.draw.polygon(surf, BIRD_BLUE_D, underside_pts)
        # Green tip patch (lime macaw primary)
        tip_pts = [
            (cx + sign * s * 1.30, cy - s * 0.35),
            (cx + sign * s * 1.55, cy - s * 0.05),
            (cx + sign * s * 1.40, cy + s * 0.05),
            (cx + sign * s * 1.25, cy - s * 0.10),
        ]
        pygame.draw.polygon(surf, BIRD_GREEN, tip_pts)
        # Yellow secondary stripe
        stripe_pts = [
            (cx + sign * s * 1.05, cy - s * 0.30),
            (cx + sign * s * 1.30, cy - s * 0.15),
            (cx + sign * s * 1.20, cy - s * 0.00),
            (cx + sign * s * 0.95, cy - s * 0.15),
        ]
        pygame.draw.polygon(surf, YELLOW, stripe_pts)
        # Feather divider lines
        for sf, tf in [((0.40, -0.30), (1.35, 0.10)),
                       ((0.45, -0.20), (1.10, 0.18)),
                       ((0.50, -0.10), (0.85, 0.18))]:
            pygame.draw.line(
                surf, BIRD_BLUE_D,
                (cx + sign * sf[0] * s, cy + sf[1] * s),
                (cx + sign * tf[0] * s, cy + tf[1] * s),
                max(1, int(SCALE * 1.2)))


def draw_wings_eagle(surf, cx, cy, s):
    """Variant 1 — Eagle wings only: broad outstretched pair with 5
    scalloped primary feathers per side and quill lines. The two
    shoulders almost touch in the middle."""
    for sign in (-1, 1):
        wing_pts = [
            (cx + sign * s * 0.04, cy - s * 0.25),
            (cx + sign * s * 0.30, cy - s * 0.50),
            (cx + sign * s * 0.80, cy - s * 0.55),
            (cx + sign * s * 1.30, cy - s * 0.40),
            (cx + sign * s * 1.55, cy - s * 0.10),
            (cx + sign * s * 1.45, cy + s * 0.05),
            (cx + sign * s * 1.50, cy + s * 0.35),    # feather tip 1
            (cx + sign * s * 1.20, cy + s * 0.10),
            (cx + sign * s * 1.20, cy + s * 0.42),    # feather tip 2
            (cx + sign * s * 0.95, cy + s * 0.15),
            (cx + sign * s * 0.90, cy + s * 0.45),    # feather tip 3
            (cx + sign * s * 0.65, cy + s * 0.18),
            (cx + sign * s * 0.55, cy + s * 0.42),    # feather tip 4
            (cx + sign * s * 0.30, cy + s * 0.15),
            (cx + sign * s * 0.20, cy + s * 0.35),    # feather tip 5
            (cx + sign * s * 0.04, cy + s * 0.20),
        ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
        pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
        # Quill lines
        for sf, tf in [((0.20, -0.30), (1.48, 0.32)),
                       ((0.25, -0.30), (1.20, 0.40)),
                       ((0.30, -0.25), (0.88, 0.42)),
                       ((0.30, -0.18), (0.54, 0.40)),
                       ((0.30, -0.10), (0.20, 0.32))]:
            pygame.draw.line(
                surf, GOLD_DEEP,
                (cx + sign * sf[0] * s, cy + sf[1] * s),
                (cx + sign * tf[0] * s, cy + tf[1] * s),
                max(1, int(SCALE)))
        # Secondary feather hint
        pygame.draw.lines(
            surf, GOLD_DEEP, False,
            [(cx + sign * s * 0.20, cy - s * 0.15),
             (cx + sign * s * 0.50, cy - s * 0.05),
             (cx + sign * s * 0.90, cy + s * 0.00),
             (cx + sign * s * 1.30, cy + s * 0.05)],
            max(1, int(SCALE)))


def draw_wings_falcon(surf, cx, cy, s):
    """Variant 2 — Falcon wings: slim, pointed, swept back. Aerodynamic
    silhouette without a body."""
    for sign in (-1, 1):
        wing_pts = [
            (cx + sign * s * 0.04, cy - s * 0.20),
            (cx + sign * s * 0.30, cy - s * 0.40),
            (cx + sign * s * 0.85, cy - s * 0.40),
            (cx + sign * s * 1.40, cy - s * 0.10),    # near tip
            (cx + sign * s * 1.60, cy + s * 0.15),    # sweptback tip
            (cx + sign * s * 1.25, cy + s * 0.20),
            (cx + sign * s * 1.10, cy + s * 0.40),    # trailing flare
            (cx + sign * s * 0.75, cy + s * 0.25),
            (cx + sign * s * 0.55, cy + s * 0.32),
            (cx + sign * s * 0.30, cy + s * 0.18),
            (cx + sign * s * 0.04, cy + s * 0.05),
        ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
        pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
        # Sleek diagonal feather lines
        for sf, tf in [((0.20, -0.28), (1.55, 0.10)),
                       ((0.25, -0.22), (1.30, 0.20)),
                       ((0.30, -0.12), (1.05, 0.32)),
                       ((0.35, -0.02), (0.75, 0.25))]:
            pygame.draw.line(
                surf, GOLD_DEEP,
                (cx + sign * sf[0] * s, cy + sf[1] * s),
                (cx + sign * tf[0] * s, cy + tf[1] * s),
                max(1, int(SCALE)))


def draw_wings_heraldic(surf, cx, cy, s):
    """Variant 3 — Heraldic wings: 3 stacked feather tiers per side,
    scalloped trailing edges, geometric coat-of-arms style."""
    for sign in (-1, 1):
        tiers = [
            (1.30, 0.18, -0.30, 4),
            (1.50, 0.20, -0.05, 5),
            (1.30, 0.18,  0.20, 4),
        ]
        for length, half_h, y_off, n_scallops in tiers:
            pts = [(cx + sign * s * 0.06, cy + s * (y_off - half_h)),
                   (cx + sign * s * length * 0.55,
                    cy + s * (y_off - half_h * 1.10)),
                   (cx + sign * s * length, cy + s * y_off)]
            for i in range(n_scallops + 1):
                t = 1.0 - i / n_scallops
                vx = cx + sign * s * length * t
                vy = cy + s * (y_off + half_h * 0.55)
                pts.append((vx, vy))
                if i < n_scallops:
                    t_next = 1.0 - (i + 0.5) / n_scallops
                    tx = cx + sign * s * length * t_next
                    ty = cy + s * (y_off + half_h * 1.10)
                    pts.append((tx, ty))
            pts.append((cx + sign * s * 0.06, cy + s * (y_off + half_h)))
            pygame.draw.polygon(surf, GOLD_BRIGHT, pts)
            pygame.draw.polygon(surf, GOLD_DEEP, pts, max(1, int(SCALE)))


def draw_wings_phoenix(surf, cx, cy, s):
    """Variant 4 — Phoenix wings: ornate, outstretched with upward
    curled tips and decorative trailing plumes."""
    for sign in (-1, 1):
        wing_pts = [
            (cx + sign * s * 0.06, cy - s * 0.25),
            (cx + sign * s * 0.30, cy - s * 0.45),
            (cx + sign * s * 0.85, cy - s * 0.60),       # shoulder peak
            (cx + sign * s * 1.30, cy - s * 0.70),       # near tip
            (cx + sign * s * 1.55, cy - s * 0.55),       # upcurled tip
            (cx + sign * s * 1.40, cy - s * 0.25),       # back down
            (cx + sign * s * 1.20, cy + s * 0.00),
            (cx + sign * s * 1.30, cy + s * 0.30),       # plume tip 1
            (cx + sign * s * 1.00, cy + s * 0.00),
            (cx + sign * s * 1.05, cy + s * 0.40),       # plume tip 2
            (cx + sign * s * 0.75, cy + s * 0.05),
            (cx + sign * s * 0.75, cy + s * 0.40),       # plume tip 3
            (cx + sign * s * 0.50, cy + s * 0.08),
            (cx + sign * s * 0.45, cy + s * 0.35),       # plume tip 4
            (cx + sign * s * 0.20, cy + s * 0.10),
            (cx + sign * s * 0.06, cy + s * 0.00),
        ]
        pygame.draw.polygon(surf, GOLD_BRIGHT, wing_pts)
        pygame.draw.polygon(surf, GOLD_DEEP, wing_pts, max(1, int(SCALE)))
        for sf, tf in [((0.25, -0.35), (1.30, 0.28)),
                       ((0.30, -0.30), (1.05, 0.36)),
                       ((0.35, -0.25), (0.75, 0.36)),
                       ((0.35, -0.18), (0.45, 0.30))]:
            pygame.draw.line(
                surf, GOLD_DEEP,
                (cx + sign * sf[0] * s, cy + sf[1] * s),
                (cx + sign * tf[0] * s, cy + tf[1] * s),
                max(1, int(SCALE)))
        pygame.draw.circle(surf, GOLD_DEEP,
                           (int(cx + sign * s * 0.50),
                            int(cy - s * 0.30)),
                           max(1, int(s * 0.04)))


def draw_wings_macaw(surf, cx, cy, s):
    """Variant 5 — Macaw wings (Pip-style): both wings spread, cobalt
    blue with lime green primary tips, yellow secondary stripe, dark
    blue feather divider lines. Matches game/parrot.py's palette."""
    BIRD_BLUE = (40, 100, 255)
    BIRD_BLUE_D = (20, 55, 180)
    BIRD_GREEN = (50, 220, 100)
    YELLOW = (255, 200, 60)
    for sign in (-1, 1):
        wing_pts = [
            (cx + sign * s * 0.06, cy - s * 0.20),
            (cx + sign * s * 0.32, cy - s * 0.45),
            (cx + sign * s * 0.90, cy - s * 0.55),
            (cx + sign * s * 1.35, cy - s * 0.35),
            (cx + sign * s * 1.55, cy - s * 0.05),
            (cx + sign * s * 1.45, cy + s * 0.15),
            (cx + sign * s * 1.10, cy + s * 0.20),
            (cx + sign * s * 0.70, cy + s * 0.22),
            (cx + sign * s * 0.32, cy + s * 0.12),
            (cx + sign * s * 0.06, cy + s * 0.00),
        ]
        pygame.draw.polygon(surf, BIRD_BLUE, wing_pts)
        pygame.draw.polygon(surf, BIRD_BLUE_D, wing_pts, max(1, int(SCALE)))
        # Underside shadow triangle near body
        pygame.draw.polygon(surf, BIRD_BLUE_D, [
            (cx + sign * s * 0.06, cy - s * 0.05),
            (cx + sign * s * 0.30, cy + s * 0.10),
            (cx + sign * s * 0.06, cy + s * 0.00),
        ])
        # Lime green primary tip patch
        tip_pts = [
            (cx + sign * s * 1.28, cy - s * 0.40),
            (cx + sign * s * 1.55, cy - s * 0.05),
            (cx + sign * s * 1.42, cy + s * 0.10),
            (cx + sign * s * 1.20, cy - s * 0.15),
        ]
        pygame.draw.polygon(surf, BIRD_GREEN, tip_pts)
        # Yellow secondary stripe
        stripe_pts = [
            (cx + sign * s * 1.02, cy - s * 0.35),
            (cx + sign * s * 1.28, cy - s * 0.20),
            (cx + sign * s * 1.18, cy - s * 0.02),
            (cx + sign * s * 0.92, cy - s * 0.18),
        ]
        pygame.draw.polygon(surf, YELLOW, stripe_pts)
        # Feather divider lines
        for sf, tf in [((0.25, -0.30), (1.32, 0.10)),
                       ((0.30, -0.20), (1.10, 0.18)),
                       ((0.35, -0.10), (0.85, 0.20))]:
            pygame.draw.line(
                surf, BIRD_BLUE_D,
                (cx + sign * sf[0] * s, cy + sf[1] * s),
                (cx + sign * tf[0] * s, cy + tf[1] * s),
                max(2, int(SCALE * 1.2)))


WING_VARIANTS = [
    ("1.  EAGLE",     "broad raptor, 5 feathers",   draw_wings_eagle),
    ("2.  FALCON",    "sweptback + aerodynamic",    draw_wings_falcon),
    ("3.  HERALDIC",  "3-tier crest wings",         draw_wings_heraldic),
    ("4.  PHOENIX",   "ornate, curled tips",        draw_wings_phoenix),
    ("5.  MACAW",     "Pip's colour palette",       draw_wings_macaw),
]


def render_wing_options():
    """Render a 720×1280 sheet showing all 5 wing options stacked
    vertically with labels, so the user can pick one."""
    s = pygame.Surface((W, H))
    backdrop(s, dim=70)
    big_title(s, "PICK A WING", (W // 2, 56 * SCALE), size=30, px_scale=3)
    row_h = (H - 100 * SCALE) // len(WING_VARIANTS)
    base_y = 110 * SCALE
    wing_scale = 36  # logical-ish "s" passed into the wing draw fn
    for i, (label, desc, draw_fn) in enumerate(WING_VARIANTS):
        row_cy = base_y + i * row_h + row_h // 2
        card_rect = pygame.Rect(20 * SCALE, base_y + i * row_h + 6 * SCALE,
                                W - 40 * SCALE, row_h - 12 * SCALE)
        card(s, card_rect, border_alpha=120, accent_alpha=80, alpha=200,
             radius=14)
        # Render the wing in the centre-left of the card
        wing_cx = card_rect.x + 120 * SCALE
        draw_fn(s, wing_cx, row_cy, wing_scale * SCALE)
        # Label (bold) + description (muted), both right-aligned with
        # plenty of card-width
        lf = font(16, True).render(label, True, GOLD_BRIGHT)
        lo = font(16, True).render(label, True, RED_OUTLINE)
        lr = lf.get_rect(midleft=(card_rect.x + 220 * SCALE,
                                  row_cy - 12 * SCALE))
        px = 2 * SCALE
        for ox in (-px, 0, px):
            for oy in (-px, 0, px):
                if ox or oy:
                    s.blit(lo, (lr.x + ox, lr.y + oy))
        s.blit(lf, lr)
        df = font(10, True).render(desc, True, GOLD_MUTED)
        df.set_alpha(220)
        s.blit(df, (card_rect.x + 220 * SCALE,
                    row_cy + 10 * SCALE))
    save("wing_options.png", s)
    # Cache-bust filename so the user definitely sees the latest version
    save("wing_options_r11.png", s)


def stat_tile_chunky(surf, rect, icon_kind, value, label, subline=None):
    """Chunky engraved stat tile used in v1 (Trophy Cinema)."""
    # Drop shadow
    sh = pygame.Surface((rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120),
                     (0, 0, rect.w + 4 * SCALE, rect.h + 4 * SCALE),
                     border_radius=10 * SCALE)
    surf.blit(sh, (rect.x - 2 * SCALE, rect.y + 4 * SCALE))
    # Body — vertical gradient from PANEL_LIGHTER to PANEL_DARK
    body = pygame.Surface(rect.size, pygame.SRCALPHA)
    for yy in range(rect.h):
        t = yy / max(1, rect.h - 1)
        c = lerp(PANEL_LIGHTER, PANEL_DARK, t)
        pygame.draw.line(body, (*c, 245), (0, yy), (rect.w, yy))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, rect.w, rect.h), border_radius=10 * SCALE)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Slimmer gold rim — lighter touch so the row reads as a refined
    # stat strip rather than a row of heavy bordered boxes
    pygame.draw.rect(body, (*GOLD_BRIGHT, 160), (0, 0, rect.w, rect.h),
                     width=1 * SCALE, border_radius=10 * SCALE)
    # Top inner highlight
    pygame.draw.line(body, (*GOLD_PALE, 100),
                     (10 * SCALE, 3 * SCALE),
                     (rect.w - 10 * SCALE, 3 * SCALE), 1 * SCALE)
    surf.blit(body, rect.topleft)
    # Icon — sized to read clearly without dominating the tile
    stat_icon(surf, icon_kind, rect.centerx, rect.y + 22 * SCALE,
              size=15)
    # Value
    vf = font(26, True).render(str(value), True, GOLD_BRIGHT)
    vs = font(26, True).render(str(value), True, NEAR_BLACK)
    vs.set_alpha(170)
    vy = rect.y + 54 * SCALE if subline else rect.y + 58 * SCALE
    vr = vf.get_rect(center=(rect.centerx, vy))
    surf.blit(vs, (vr.x + 1 * SCALE, vr.y + 2 * SCALE))
    surf.blit(vf, vr)
    # Optional subline — gold-muted caption directly below the value
    # (used for COINS to surface "61%" alongside the raw count)
    if subline:
        sf = font(11, True).render(subline, True, GOLD_MUTED)
        sf.set_alpha(230)
        surf.blit(sf, sf.get_rect(center=(rect.centerx,
                                          rect.y + 74 * SCALE)))
    # Label — shrinks one step if the longer captions would otherwise
    # crowd the tile edges
    max_label_w = rect.w - 10 * SCALE
    lbl_size = 12
    lf = font(lbl_size, True).render(label, True, GOLD_MUTED)
    while lf.get_width() > max_label_w and lbl_size > 10:
        lbl_size -= 1
        lf = font(lbl_size, True).render(label, True, GOLD_MUTED)
    lf.set_alpha(230)
    surf.blit(lf, lf.get_rect(center=(rect.centerx,
                                      rect.y + rect.h - 12 * SCALE)))


def powerup_chip(surf, cx, cy, kind, count, size=22):
    """Vertical chip — icon on top with breathing room, count rendered
    as clean gold text underneath. The count never overlaps the icon
    so even single-pixel power-up details (mushroom dot, ghost eye) stay
    fully readable."""
    icon_area = size * 2 * SCALE
    count_area = 18 * SCALE if size >= 18 else 16 * SCALE
    chip_w = icon_area
    chip_h = icon_area + count_area
    rect = pygame.Rect(cx - chip_w // 2, cy - chip_h // 2, chip_w, chip_h)
    body = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(body, (*PANEL_DARK, 220), (0, 0, rect.w, rect.h),
                     border_radius=int(8 * SCALE))
    pygame.draw.rect(body, (*GOLD_BRIGHT, 180), (0, 0, rect.w, rect.h),
                     width=1 * SCALE, border_radius=int(8 * SCALE))
    # Hairline divider between icon and count
    pygame.draw.line(body, (*GOLD_BRIGHT, 90),
                     (6 * SCALE, icon_area - 1 * SCALE),
                     (rect.w - 6 * SCALE, icon_area - 1 * SCALE),
                     1)
    surf.blit(body, rect.topleft)
    # Icon — centered in the upper area, with a touch of headroom
    _ingame_powerup_icon(surf, kind,
                         rect.centerx,
                         rect.y + icon_area // 2,
                         int(size * 1.55 * SCALE))
    # Count — clean gold text in the lower area, no badge
    if count and count > 0:
        cnt_size = 12 if size >= 18 else (11 if size >= 16 else 10)
        cf = font(cnt_size, True).render(f"×{count}", True, GOLD_BRIGHT)
        cs = font(cnt_size, True).render(f"×{count}", True, NEAR_BLACK)
        cs.set_alpha(170)
        cr = cf.get_rect(center=(rect.centerx,
                                 rect.y + icon_area + count_area // 2))
        surf.blit(cs, (cr.x + 1 * SCALE, cr.y + 1 * SCALE))
        surf.blit(cf, cr)


# ── DESIGN 1 — Trophy Cinema ────────────────────────────────────────────────

def draw_v1_trophy_cinema(surf, data):
    """Premium award-show: hex grade + massive engraved score plaque +
    chunky stat tile row + power-up chips + big primary CTA."""
    backdrop(surf, dim=60)
    # Soft radial vignette focus toward center
    vign = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(max(W, H), 0, -8 * SCALE):
        a = int(30 * (1 - r / max(W, H)))
        pygame.draw.circle(vign, (0, 0, 0, a),
                           (W // 2, H // 2 + 40 * SCALE), r)
    surf.blit(vign, (0, 0))

    # Title — canonical Skybit gold-on-red treatment, larger so it
    # owns the top of the screen
    big_title(surf, "RUN  SUMMARY", (W // 2, 56 * SCALE), size=34,
              px_scale=3)

    # The rank medal and biome chip are intentionally absent — both
    # ended up reading as "condition the game ended in" without much
    # actionable meaning. Removing them gives the plaque more room
    # to breathe at the top.

    # Hero score plaque — large rounded engraved panel
    plaque = pygame.Rect(36 * SCALE, 104 * SCALE,
                         W - 72 * SCALE, 156 * SCALE)
    # Outer drop shadow
    sh = pygame.Surface((plaque.w + 8 * SCALE, plaque.h + 10 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 130),
                     (0, 0, plaque.w + 8 * SCALE, plaque.h + 10 * SCALE),
                     border_radius=20 * SCALE)
    surf.blit(sh, (plaque.x - 4 * SCALE, plaque.y + 6 * SCALE))
    # Outer gold frame
    pygame.draw.rect(surf, GOLD_BRIGHT, plaque, border_radius=20 * SCALE)
    # Inner darker bevel
    inner = plaque.inflate(-8 * SCALE, -8 * SCALE)
    pygame.draw.rect(surf, GOLD_DEEP, inner, border_radius=16 * SCALE)
    # Engraved face
    face = inner.inflate(-6 * SCALE, -6 * SCALE)
    grad = pygame.Surface(face.size, pygame.SRCALPHA)
    for yy in range(face.h):
        t = yy / max(1, face.h - 1)
        c = lerp(PANEL_LIGHTER, NIGHT_DEEP, t)
        pygame.draw.line(grad, (*c, 255), (0, yy), (face.w, yy))
    mask = pygame.Surface(face.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, face.w, face.h), border_radius=12 * SCALE)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, face.topleft)
    # Subtle radial light from upper-left of face
    glow = pygame.Surface(face.size, pygame.SRCALPHA)
    for rr in range(int(face.w * 0.6), 0, -2 * SCALE):
        a = int(18 * (1 - rr / (face.w * 0.6)))
        pygame.draw.circle(glow, (255, 220, 140, a),
                           (int(face.w * 0.35), int(face.h * 0.25)), rr)
    glow.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(glow, face.topleft)
    # SCORE caption
    sc = font(15, True).render("F I N A L   S C O R E", True, GOLD_MUTED)
    sc.set_alpha(230)
    surf.blit(sc, sc.get_rect(center=(W // 2, plaque.y + 26 * SCALE)))
    # Massive engraved number
    big_num = str(data["score"])
    num_size = 88
    nf = font(num_size, True).render(big_num, True, GOLD_BRIGHT)
    no = font(num_size, True).render(big_num, True, RED_OUTLINE)
    nsh = font(num_size, True).render(big_num, True, NEAR_BLACK)
    deep_inner = font(num_size, True).render(big_num, True, GOLD_DEEP)
    nr = nf.get_rect(center=(W // 2, plaque.centery + 4 * SCALE))
    px = 4 * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(no, (nr.x + ox, nr.y + oy))
    nsh.set_alpha(180)
    surf.blit(nsh, (nr.x + 4 * SCALE, nr.y + 6 * SCALE))
    # Inset deep-gold layer underneath for engraved depth
    deep_inner.set_alpha(180)
    surf.blit(deep_inner, (nr.x - 1 * SCALE, nr.y - 1 * SCALE))
    surf.blit(nf, nr)
    # Best comparison line beneath number
    delta = data["score"] - data["best"]
    if data["new_best"]:
        cmp_text = f"NEW BEST  +{abs(delta)}"
        cmp_color = GOLD_BRIGHT
    else:
        cmp_text = f"BEST {data['best']}    {delta:+d}"
        cmp_color = GOLD_MUTED
    cf = font(13, True).render(cmp_text, True, cmp_color)
    cf.set_alpha(230)
    surf.blit(cf, cf.get_rect(center=(W // 2,
                                       plaque.bottom - 20 * SCALE)))

    # Stat tile row (4 tiles)
    coins_pct = (round(data["coins"] / data["coins_total"] * 100)
                 if data.get("coins_total") else None)
    coins_sub = f"{coins_pct}%" if coins_pct is not None else None
    tiles = [
        ("time", data["time_str"], "TIME", None),
        ("coin", data["coins"], "COINS", coins_sub),
        ("pillar", data["pillars"], "PILLARS", None),
        ("flap", data["flaps"], "FLAPS", None),
    ]
    tile_w = 78 * SCALE
    tile_h = 98 * SCALE
    tile_gap = 8 * SCALE
    total_w = len(tiles) * tile_w + (len(tiles) - 1) * tile_gap
    start_x = (W - total_w) // 2
    tile_y = 282 * SCALE
    for i, (k, v, lbl, sub) in enumerate(tiles):
        r = pygame.Rect(start_x + i * (tile_w + tile_gap), tile_y,
                        tile_w, tile_h)
        stat_tile_chunky(surf, r, k, v, lbl, subline=sub)

    # Power-ups row — compact strip: bare icons with a small "×N"
    # caption underneath, no chip frame. Same icon size whether 1 or 7
    # kinds were picked. Sized to fit all 7 in a single row at the 360
    # logical canvas (7 × 44 + 6 × 4 = 332 px → 28 px total margin).
    pu = [(k, c) for k, c in data["powerups_picked"] if c and c > 0]
    if pu:
        cap_y = 408 * SCALE
        cap2 = font(14, True).render("P O W E R - U P S   U S E D",
                                     True, GOLD_MUTED)
        cap2.set_alpha(230)
        surf.blit(cap2, cap2.get_rect(center=(W // 2, cap_y)))
        icon_logical = 24
        icon_box = icon_logical * 2 * SCALE
        gap = 4 * SCALE
        pitch = icon_box + gap
        total_w = len(pu) * icon_box + max(0, len(pu) - 1) * gap
        sx = (W - total_w) // 2 + icon_box // 2
        icon_cy = cap_y + 38 * SCALE
        for i, (kind, count) in enumerate(pu):
            cx = sx + i * pitch
            _ingame_powerup_icon(surf, kind, cx, icon_cy,
                                 int(icon_logical * 1.7 * SCALE))
            cf = font(14, True).render(f"×{count}", True, GOLD_BRIGHT)
            cs = font(14, True).render(f"×{count}", True, NEAR_BLACK)
            cs.set_alpha(170)
            cr = cf.get_rect(center=(cx, icon_cy
                                     + int(icon_logical * 0.95) * SCALE))
            surf.blit(cs, (cr.x + 1 * SCALE, cr.y + 1 * SCALE))
            surf.blit(cf, cr)

    # Primary CTA + secondary
    pill(surf, (W // 2, 568 * SCALE), "PLAY  AGAIN",
         size=23, min_w=246, h=54, primary=True)
    outline_pill(surf, (W // 2, 615 * SCALE), "MAIN MENU",
                 size=14, min_w=120, h=30)


# ── DESIGN 2 — Pip's Flight Log ─────────────────────────────────────────────

def draw_goggles_icon(surf, cx, cy, size):
    """Aviator goggles: two gold rings joined by a strap."""
    s = size * SCALE
    # Strap line
    pygame.draw.line(surf, GOLD_BRIGHT,
                     (cx - s * 1.5, cy), (cx + s * 1.5, cy), 2 * SCALE)
    for ox in (-s * 0.85, s * 0.85):
        # Lens body
        pygame.draw.circle(surf, NEAR_BLACK, (int(cx + ox), cy), int(s * 0.7))
        pygame.draw.circle(surf, GOLD_BRIGHT, (int(cx + ox), cy),
                           int(s * 0.7), 2 * SCALE)
        # Reflective glint
        pygame.draw.circle(surf, TEAL_HINT, (int(cx + ox - s * 0.18),
                                             int(cy - s * 0.18)),
                           int(s * 0.18))


def draw_perforation(surf, y, color=GOLD_BRIGHT, alpha=180):
    """Boarding-pass perforated edge — dotted line + half-circle notches
    cutting into the body from each side."""
    # Half-circle notches
    notch_r = 8 * SCALE
    pygame.draw.circle(surf, NIGHT_DEEP, (0, y), notch_r)
    pygame.draw.circle(surf, NIGHT_DEEP, (W, y), notch_r)
    # Outline notches with gold
    pygame.draw.arc(surf, color,
                    (-notch_r, y - notch_r, notch_r * 2, notch_r * 2),
                    -math.pi / 2, math.pi / 2, 1 * SCALE)
    pygame.draw.arc(surf, color,
                    (W - notch_r, y - notch_r, notch_r * 2, notch_r * 2),
                    math.pi / 2, math.pi * 3 / 2, 1 * SCALE)
    # Dotted line between notches
    x = notch_r + 6 * SCALE
    while x < W - notch_r - 6 * SCALE:
        pygame.draw.circle(surf, (*color, alpha), (x, y), 1 * SCALE)
        x += 7 * SCALE


def draw_wax_seal(surf, cx, cy, r, score):
    """Embossed gold-rim crimson wax seal with a chunky number inside."""
    # Splash blob behind seal — irregular crimson splash
    splash = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    random.seed(99)
    for i in range(8):
        a = math.radians(i * 45 + random.uniform(-10, 10))
        d = r * 1.2 + random.uniform(-r * 0.15, r * 0.25)
        x = r * 2 + math.cos(a) * d
        y = r * 2 + math.sin(a) * d
        pygame.draw.circle(splash, (*SCARLET_DEEP, 200), (x, y),
                           int(r * 0.5))
    surf.blit(splash, (cx - r * 2, cy - r * 2))
    # Seal disc
    pygame.draw.circle(surf, SCARLET_BOT, (cx, cy), r)
    pygame.draw.circle(surf, SCARLET_TOP, (cx - r // 4, cy - r // 4),
                       r - 2 * SCALE)
    pygame.draw.circle(surf, SCARLET_BOT, (cx, cy), r, 2 * SCALE)
    # Gold inner ring
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), int(r * 0.78),
                       2 * SCALE)
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), int(r * 0.78),
                       1 * SCALE)
    # Decorative ticks
    for ang in range(0, 360, 30):
        a = math.radians(ang - 90)
        x1 = cx + math.cos(a) * (r - 4 * SCALE)
        y1 = cy + math.sin(a) * (r - 4 * SCALE)
        x2 = cx + math.cos(a) * (r - 7 * SCALE)
        y2 = cy + math.sin(a) * (r - 7 * SCALE)
        pygame.draw.line(surf, GOLD_DEEP, (x1, y1), (x2, y2), 1 * SCALE)
    # Score text
    nf = font(28, True).render(str(score), True, GOLD_PALE)
    no = font(28, True).render(str(score), True, GOLD_DEEP)
    nr = nf.get_rect(center=(cx, cy))
    surf.blit(no, (nr.x + 1 * SCALE, nr.y + 2 * SCALE))
    surf.blit(nf, nr)
    # Tiny "PIP" arc above the number
    pf = font(8, True).render("· P I P ·", True, GOLD_PALE)
    surf.blit(pf, pf.get_rect(center=(cx, cy - int(r * 0.55))))


def draw_v2_pip_flight_log(surf, data):
    """Themed boarding-pass / aviator's logbook layout."""
    backdrop(surf, dim=70)

    # Header strip
    header = pygame.Rect(20 * SCALE, 28 * SCALE, W - 40 * SCALE, 78 * SCALE)
    # Shadow
    sh = pygame.Surface((header.w + 6 * SCALE, header.h + 8 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 130),
                     (0, 0, header.w + 6 * SCALE, header.h + 8 * SCALE),
                     border_radius=14 * SCALE)
    surf.blit(sh, (header.x - 3 * SCALE, header.y + 4 * SCALE))
    # Body — slight scarlet warm-tint navy
    hdr_body = pygame.Surface(header.size, pygame.SRCALPHA)
    for yy in range(header.h):
        t = yy / max(1, header.h - 1)
        c = lerp((20, 12, 48), (10, 6, 32), t)
        pygame.draw.line(hdr_body, (*c, 245), (0, yy), (header.w, yy))
    mask = pygame.Surface(header.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, header.w, header.h), border_radius=14 * SCALE)
    hdr_body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(hdr_body, GOLD_BRIGHT, (0, 0, header.w, header.h),
                     width=2 * SCALE, border_radius=14 * SCALE)
    # Top inner highlight
    pygame.draw.line(hdr_body, (*GOLD_PALE, 130),
                     (10 * SCALE, 4 * SCALE),
                     (header.w - 10 * SCALE, 4 * SCALE), 1 * SCALE)
    surf.blit(hdr_body, header.topleft)
    # Goggles icon left
    draw_goggles_icon(surf, header.x + 36 * SCALE,
                      header.centery, size=16)
    # Title
    tf = font(20, True).render("PIP'S  FLIGHT  LOG", True, GOLD_BRIGHT)
    to = font(20, True).render("PIP'S  FLIGHT  LOG", True, RED_OUTLINE)
    tr = tf.get_rect(midleft=(header.x + 76 * SCALE,
                              header.centery - 10 * SCALE))
    px = 2 * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(to, (tr.x + ox, tr.y + oy))
    surf.blit(tf, tr)
    # Subtitle in header
    sub = font(10, True).render("FLIGHT  No. 0023  ·  SKYBIT  EXPRESS",
                                True, GOLD_MUTED)
    sub.set_alpha(220)
    surf.blit(sub, (header.x + 76 * SCALE,
                    header.centery + 12 * SCALE))

    # Perforation
    perf_y = header.bottom + 10 * SCALE
    draw_perforation(surf, perf_y)

    # Body card
    body = pygame.Rect(20 * SCALE, perf_y + 12 * SCALE,
                       W - 40 * SCALE, 360 * SCALE)
    sh2 = pygame.Surface((body.w + 6 * SCALE, body.h + 8 * SCALE),
                         pygame.SRCALPHA)
    pygame.draw.rect(sh2, (0, 0, 0, 130),
                     (0, 0, body.w + 6 * SCALE, body.h + 8 * SCALE),
                     border_radius=14 * SCALE)
    surf.blit(sh2, (body.x - 3 * SCALE, body.y + 4 * SCALE))
    body_pnl = pygame.Surface(body.size, pygame.SRCALPHA)
    pygame.draw.rect(body_pnl, (*PANEL_DARK, 235),
                     (0, 0, body.w, body.h), border_radius=14 * SCALE)
    pygame.draw.rect(body_pnl, GOLD_BRIGHT, (0, 0, body.w, body.h),
                     width=2 * SCALE, border_radius=14 * SCALE)
    # Top + bottom inner accent rails
    pygame.draw.line(body_pnl, (*GOLD_BRIGHT, 130),
                     (10 * SCALE, 4 * SCALE),
                     (body.w - 10 * SCALE, 4 * SCALE), 1 * SCALE)
    surf.blit(body_pnl, body.topleft)

    # Stat rows — left-aligned labels, right-aligned values, divider lines
    rows = [
        ("DEPARTURE", "00 : 00"),
        ("DURATION", data["time_str"]),
        ("PILLARS  PASSED", str(data["pillars"])),
        ("COINS  COLLECTED", str(data["coins"])),
        ("NEAR  MISSES", str(data["near_misses"])),
    ]
    rows_top = body.y + 18 * SCALE
    rows_bot = body.bottom - 110 * SCALE
    row_h = (rows_bot - rows_top) // len(rows)
    for i, (lbl, val) in enumerate(rows):
        rcy = rows_top + i * row_h + row_h // 2
        # Stencil-style label
        lf = font(13, True).render(lbl, True, GOLD_MUTED)
        surf.blit(lf, (body.x + 22 * SCALE, rcy - lf.get_height() // 2))
        # Dotted leader between label and value
        dot_x = body.x + 22 * SCALE + lf.get_width() + 8 * SCALE
        end_x = body.right - 88 * SCALE
        while dot_x < end_x:
            pygame.draw.circle(surf, (*GOLD_DEEP, 180),
                               (dot_x, rcy), 1 * SCALE)
            dot_x += 6 * SCALE
        vf = font(15, True).render(val, True, GOLD_BRIGHT)
        vsh = font(15, True).render(val, True, NEAR_BLACK)
        vsh.set_alpha(170)
        vr = vf.get_rect(midright=(body.right - 22 * SCALE, rcy))
        surf.blit(vsh, (vr.x + 1 * SCALE, vr.y + 2 * SCALE))
        surf.blit(vf, vr)

    # Stamps row — actual powerup icons in small oval frames at the bottom
    pu = data["powerups_picked"]
    if pu:
        st_y = rows_bot + 14 * SCALE
        cap = font(10, True).render("S T A M P S", True, GOLD_MUTED)
        cap.set_alpha(220)
        surf.blit(cap, (body.x + 22 * SCALE, st_y - 4 * SCALE))
        st_size = 30 * SCALE
        st_gap = 10 * SCALE
        for i, (kind, count) in enumerate(pu):
            sx = body.x + 22 * SCALE + i * (st_size + st_gap) + st_size // 2
            sy = st_y + 32 * SCALE
            # Oval frame (slightly tilted by drawing rotated rect)
            pygame.draw.ellipse(surf, SCARLET_BOT,
                                (sx - st_size // 2 - 2 * SCALE,
                                 sy - st_size // 2 - 2 * SCALE,
                                 st_size + 4 * SCALE,
                                 st_size + 4 * SCALE))
            pygame.draw.ellipse(surf, GOLD_BRIGHT,
                                (sx - st_size // 2 - 2 * SCALE,
                                 sy - st_size // 2 - 2 * SCALE,
                                 st_size + 4 * SCALE,
                                 st_size + 4 * SCALE), 1 * SCALE)
            _ingame_powerup_icon(surf, kind, sx, sy, int(st_size * 0.95))

        # Wax seal on the right — pulled in from the edge so the splash
        # stays inside the body card
        seal_cx = body.right - 64 * SCALE
        seal_cy = st_y + 32 * SCALE
        draw_wax_seal(surf, seal_cx, seal_cy, r=36 * SCALE,
                      score=data["score"])

    # CTA — "FLY AGAIN" pill + "RETURN TO BASE" link
    pill(surf, (W // 2, body.bottom + 40 * SCALE), "FLY  AGAIN",
         size=23, min_w=240, h=52, primary=True)
    rb = font(13, True).render("· RETURN TO BASE ·", True, GOLD_MUTED)
    surf.blit(rb, rb.get_rect(center=(W // 2, body.bottom + 88 * SCALE)))


# ── DESIGN 3 — Constellation Wheel ──────────────────────────────────────────

def draw_dotted_arc_line(surf, x1, y1, x2, y2, color=GOLD_BRIGHT,
                          alpha=140, dot_r=1):
    """Dotted line from (x1,y1) to (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    n = max(1, int(length // (5 * SCALE)))
    for i in range(n + 1):
        t = i / n
        x = x1 + dx * t
        y = y1 + dy * t
        pygame.draw.circle(surf, (*color, alpha), (int(x), int(y)),
                           dot_r * SCALE)


def satellite_orb(surf, cx, cy, r, icon_kind, value, label):
    """Small circular orb showing an icon + value, label rendered outside."""
    # Shadow
    sh = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 120), (r + 4, r + 4), r + 1)
    surf.blit(sh, (cx - r - 4, cy - r + 3))
    # Body — radial-ish gradient (just two-tone fill)
    pygame.draw.circle(surf, PANEL_LIGHTER, (cx, cy), r)
    pygame.draw.circle(surf, PANEL_DARK, (cx, cy + 2 * SCALE), r - 2 * SCALE)
    # Gold ring
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), r, 2 * SCALE)
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), r - 3 * SCALE, 1 * SCALE)
    # Icon top
    stat_icon(surf, icon_kind, cx, cy - 8 * SCALE, size=7)
    # Value bottom
    vf = font(15, True).render(str(value), True, GOLD_BRIGHT)
    vs = font(15, True).render(str(value), True, NEAR_BLACK)
    vs.set_alpha(170)
    vr = vf.get_rect(center=(cx, cy + 9 * SCALE))
    surf.blit(vs, (vr.x + 1 * SCALE, vr.y + 2 * SCALE))
    surf.blit(vf, vr)


def draw_v3_constellation_wheel(surf, data):
    """Radial achievement layout — score medallion centered with stat
    satellites around it, dotted gold connecting lines."""
    backdrop(surf, dim=80)

    # Top: rank
    grade = grade_for(data["score"])
    hex_medal(surf, W // 2, 76 * SCALE, size=26, letter=grade,
              sub_label="R A N K")

    # Central score medallion — bigger than current
    cx, cy = W // 2, 320 * SCALE
    R = 90 * SCALE
    score_emblem(surf, cx, cy, R, "S C O R E", str(data["score"]))

    # BEST comparison ribbon hanging below the medallion
    delta = data["score"] - data["best"]
    if data["new_best"]:
        cmp_text = f"NEW BEST  +{abs(delta)}"
        cmp_bg, cmp_fg = SCARLET_TOP, GOLD_BRIGHT
    else:
        cmp_text = f"BEST  {data['best']}    {delta:+d}"
        cmp_bg, cmp_fg = SCARLET_BOT, CREAM
    cf = font(11, True).render(cmp_text, True, cmp_fg)
    chip_w = cf.get_width() + 22 * SCALE
    chip_h = cf.get_height() + 8 * SCALE
    chip_rect = pygame.Rect(W // 2 - chip_w // 2,
                            cy + R + 14 * SCALE,
                            chip_w, chip_h)
    pygame.draw.rect(surf, cmp_bg, chip_rect, border_radius=chip_h // 2)
    pygame.draw.rect(surf, GOLD_BRIGHT, chip_rect,
                     width=1 * SCALE, border_radius=chip_h // 2)
    surf.blit(cf, cf.get_rect(center=chip_rect.center))

    # Faint laurel wreath behind medallion
    for ang_deg in range(0, 360, 6):
        a = math.radians(ang_deg - 90)
        x = cx + math.cos(a) * (R + 12 * SCALE)
        y = cy + math.sin(a) * (R + 12 * SCALE)
        pygame.draw.circle(surf, (*GOLD_DEEP, 80), (int(x), int(y)),
                           1 * SCALE)

    # 4 satellite stat orbs around the medallion
    sats = [
        (math.radians(-130), "time", data["time_str"], "TIME"),
        (math.radians(-50), "coin", data["coins"], "COINS"),
        (math.radians(50), "pillar", data["pillars"], "PILLARS"),
        (math.radians(130), "crosshair", data["near_misses"], "MISSES"),
    ]
    sat_dist = R + 70 * SCALE
    sat_r = 30 * SCALE
    for ang, kind, val, lbl in sats:
        sx = cx + math.cos(ang) * sat_dist
        sy = cy + math.sin(ang) * sat_dist
        # Dotted line from medallion edge to orb edge
        edge_x = cx + math.cos(ang) * (R + 4 * SCALE)
        edge_y = cy + math.sin(ang) * (R + 4 * SCALE)
        orb_x = sx - math.cos(ang) * sat_r
        orb_y = sy - math.sin(ang) * sat_r
        draw_dotted_arc_line(surf, edge_x, edge_y, orb_x, orb_y,
                             color=GOLD_BRIGHT, alpha=160)
        satellite_orb(surf, int(sx), int(sy), sat_r, kind, val, lbl)
        # Label outside the orb
        # Position label radially outward
        label_x = sx + math.cos(ang) * (sat_r + 18 * SCALE)
        label_y = sy + math.sin(ang) * (sat_r + 18 * SCALE)
        lf = font(10, True).render(lbl, True, GOLD_MUTED)
        lf.set_alpha(220)
        surf.blit(lf, lf.get_rect(center=(int(label_x), int(label_y))))

    # Power-up row at bottom
    pu = data["powerups_picked"]
    if pu:
        bar_y = 510 * SCALE
        cap = font(10, True).render("P O W E R - U P S",
                                    True, GOLD_MUTED)
        cap.set_alpha(220)
        surf.blit(cap, cap.get_rect(center=(W // 2, bar_y - 4 * SCALE)))
        chip_size = 18
        chip_w = chip_size * 2 * SCALE + 8 * SCALE
        total_cw = len(pu) * chip_w + (len(pu) - 1) * 6 * SCALE
        sx = (W - total_cw) // 2 + chip_w // 2
        for i, (kind, count) in enumerate(pu):
            powerup_chip(surf, sx + i * (chip_w + 6 * SCALE),
                         bar_y + 28 * SCALE,
                         kind, count, size=chip_size)

    # Bottom: dual segmented buttons
    # Build a single capsule containing AGAIN | MENU
    seg_w = 280 * SCALE
    seg_h = 48 * SCALE
    seg_x = (W - seg_w) // 2
    seg_y = H - 78 * SCALE
    seg_rect = pygame.Rect(seg_x, seg_y, seg_w, seg_h)
    # Shadow
    sh = pygame.Surface((seg_w + 4 * SCALE, seg_h + 4 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 120),
                     (0, 0, seg_w + 4 * SCALE, seg_h + 4 * SCALE),
                     border_radius=seg_h // 2)
    surf.blit(sh, (seg_x - 2 * SCALE, seg_y + 4 * SCALE))
    # Capsule body
    capsule = pygame.Surface(seg_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(capsule, (*PANEL_DARK, 220),
                     (0, 0, seg_w, seg_h), border_radius=seg_h // 2)
    pygame.draw.rect(capsule, GOLD_BRIGHT, (0, 0, seg_w, seg_h),
                     width=2 * SCALE, border_radius=seg_h // 2)
    # Left half — primary scarlet fill
    half_w = seg_w // 2
    left_clip = pygame.Surface((half_w, seg_h), pygame.SRCALPHA)
    for yy in range(seg_h):
        t = yy / max(1, seg_h - 1)
        c = lerp(SCARLET_TOP, SCARLET_BOT, t)
        pygame.draw.line(left_clip, (*c, 255), (0, yy), (half_w, yy))
    mask = pygame.Surface(seg_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, seg_w, seg_h), border_radius=seg_h // 2)
    capsule.blit(left_clip, (0, 0))
    capsule.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Re-draw border
    pygame.draw.rect(capsule, GOLD_BRIGHT, (0, 0, seg_w, seg_h),
                     width=2 * SCALE, border_radius=seg_h // 2)
    # Divider line
    pygame.draw.line(capsule, GOLD_BRIGHT,
                     (half_w, 6 * SCALE), (half_w, seg_h - 6 * SCALE),
                     2 * SCALE)
    surf.blit(capsule, seg_rect.topleft)
    # Labels
    af = font(20, True).render("AGAIN", True, CREAM)
    surf.blit(af, af.get_rect(center=(seg_x + half_w // 2,
                                       seg_y + seg_h // 2)))
    mf = font(20, True).render("MENU", True, GOLD_BRIGHT)
    surf.blit(mf, mf.get_rect(center=(seg_x + half_w + half_w // 2,
                                       seg_y + seg_h // 2)))


# ── DESIGN 4 — Storyboard Strip ─────────────────────────────────────────────

def draw_v4_storyboard_strip(surf, data):
    """Vertical run timeline with score hero at top + delta chip."""
    backdrop(surf, dim=85)

    # Hero score — huge centered
    big_num = str(data["score"])
    nf = font(96, True).render(big_num, True, GOLD_BRIGHT)
    no = font(96, True).render(big_num, True, RED_OUTLINE)
    nsh = font(96, True).render(big_num, True, NEAR_BLACK)
    nr = nf.get_rect(center=(W // 2, 96 * SCALE))
    px = 4 * SCALE
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(no, (nr.x + ox, nr.y + oy))
    nsh.set_alpha(180)
    surf.blit(nsh, (nr.x + 4 * SCALE, nr.y + 6 * SCALE))
    surf.blit(nf, nr)

    cap = font(11, True).render("F I N A L   S C O R E", True, GOLD_MUTED)
    cap.set_alpha(220)
    surf.blit(cap, cap.get_rect(center=(W // 2, 36 * SCALE)))

    # Delta chip beside the score
    delta = data["score"] - data["best"]
    if data["new_best"]:
        chip_text = f"NEW BEST  +{abs(delta)}"
        chip_fg = GOLD_BRIGHT
        chip_bg = SCARLET_TOP
    else:
        chip_text = f"BEST {data['best']}    {delta:+d}"
        chip_fg = CREAM
        chip_bg = SCARLET_BOT
    chip_f = font(11, True).render(chip_text, True, chip_fg)
    chip_w = chip_f.get_width() + 18 * SCALE
    chip_h = chip_f.get_height() + 6 * SCALE
    chip_rect = pygame.Rect(W // 2 - chip_w // 2, 156 * SCALE,
                            chip_w, chip_h)
    pygame.draw.rect(surf, chip_bg, chip_rect, border_radius=chip_h // 2)
    pygame.draw.rect(surf, GOLD_BRIGHT, chip_rect,
                     width=1 * SCALE, border_radius=chip_h // 2)
    surf.blit(chip_f, chip_f.get_rect(center=chip_rect.center))

    # Section divider
    divider(surf, 188 * SCALE, width=200, color=GOLD_BRIGHT, alpha=120)

    # Two-column body: left=timeline, right=stats stack
    timeline_x = 105 * SCALE
    timeline_top = 218 * SCALE
    timeline_bot = 506 * SCALE
    timeline_h = timeline_bot - timeline_top

    # Timeline gold rail (dotted)
    yy = timeline_top
    while yy < timeline_bot:
        pygame.draw.circle(surf, (*GOLD_BRIGHT, 200),
                           (timeline_x, yy), 2 * SCALE)
        yy += 8 * SCALE

    # Start flag at top
    pygame.draw.circle(surf, SCARLET_TOP, (timeline_x, timeline_top),
                       6 * SCALE)
    pygame.draw.circle(surf, GOLD_BRIGHT, (timeline_x, timeline_top),
                       6 * SCALE, 1 * SCALE)
    sf = font(10, True).render("START", True, CREAM)
    surf.blit(sf, (timeline_x - 50 * SCALE,
                    timeline_top - sf.get_height() // 2))

    # End marker (skull / death)
    stat_icon(surf, "skull", timeline_x, timeline_bot, size=10)
    ef = font(10, True).render("END", True, CREAM)
    surf.blit(ef, (timeline_x - 50 * SCALE,
                    timeline_bot - ef.get_height() // 2))
    tf = font(9, True).render(data["time_str"], True, GOLD_MUTED)
    tf.set_alpha(220)
    surf.blit(tf, (timeline_x - 50 * SCALE,
                    timeline_bot + 10 * SCALE))

    # Timeline events
    duration = max(1, data["duration_s"])
    for sec, kind in data["timeline"]:
        ty = int(timeline_top + (sec / duration) * timeline_h)
        if kind == "coin":
            pygame.draw.circle(surf, COIN_GOLD,
                               (timeline_x + 14 * SCALE, ty), 3 * SCALE)
            pygame.draw.circle(surf, GOLD_DEEP,
                               (timeline_x + 14 * SCALE, ty),
                               3 * SCALE, 1 * SCALE)
        elif kind == "near_miss":
            pygame.draw.line(surf, SCARLET_TOP,
                             (timeline_x + 10 * SCALE, ty - 4 * SCALE),
                             (timeline_x + 18 * SCALE, ty + 4 * SCALE),
                             2 * SCALE)
            pygame.draw.line(surf, SCARLET_TOP,
                             (timeline_x + 10 * SCALE, ty + 4 * SCALE),
                             (timeline_x + 18 * SCALE, ty - 4 * SCALE),
                             2 * SCALE)
        elif kind.startswith("powerup_"):
            pkind = kind.split("_", 1)[1]
            # Branch from rail with a small connector line
            pygame.draw.line(surf, GOLD_BRIGHT,
                             (timeline_x + 4 * SCALE, ty),
                             (timeline_x + 24 * SCALE, ty), 1 * SCALE)
            _ingame_powerup_icon(surf, pkind,
                                 timeline_x + 38 * SCALE, ty,
                                 24 * SCALE)

    # Right-column stats stack
    stats_x = W - 80 * SCALE
    stats_top = timeline_top + 4 * SCALE
    stat_pitch = 56 * SCALE
    stats = [
        ("time", "TIME ALIVE", data["time_str"]),
        ("coin", "COINS", str(data["coins"])),
        ("pillar", "PILLARS", str(data["pillars"])),
        ("crosshair", "MISSES", str(data["near_misses"])),
    ]
    for i, (kind, lbl, val) in enumerate(stats):
        sy = stats_top + i * stat_pitch
        # Tile rect
        tile_rect = pygame.Rect(W - 130 * SCALE, sy,
                                118 * SCALE, 44 * SCALE)
        body = pygame.Surface(tile_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(body, (*PANEL_DARK, 200),
                         (0, 0, tile_rect.w, tile_rect.h),
                         border_radius=8 * SCALE)
        pygame.draw.rect(body, (*GOLD_BRIGHT, 130),
                         (0, 0, tile_rect.w, tile_rect.h),
                         width=1 * SCALE, border_radius=8 * SCALE)
        surf.blit(body, tile_rect.topleft)
        stat_icon(surf, kind, tile_rect.x + 16 * SCALE,
                  tile_rect.centery, size=8)
        lf = font(9, True).render(lbl, True, GOLD_MUTED)
        lf.set_alpha(220)
        surf.blit(lf, (tile_rect.x + 30 * SCALE,
                        tile_rect.y + 6 * SCALE))
        vf = font(16, True).render(val, True, GOLD_BRIGHT)
        vsh = font(16, True).render(val, True, NEAR_BLACK)
        vsh.set_alpha(170)
        vr = vf.get_rect(midleft=(tile_rect.x + 30 * SCALE,
                                   tile_rect.bottom - 14 * SCALE))
        surf.blit(vsh, (vr.x + 1 * SCALE, vr.y + 2 * SCALE))
        surf.blit(vf, vr)

    # Bottom CTA — primary pill + share button
    pill(surf, (W // 2 - 32 * SCALE, H - 76 * SCALE), "PLAY  AGAIN",
         size=21, min_w=200, h=48, primary=True)
    # Share circular icon button
    share_cx = W // 2 + 138 * SCALE
    share_cy = H - 76 * SCALE
    share_r = 22 * SCALE
    sh = pygame.Surface((share_r * 2 + 4 * SCALE,
                         share_r * 2 + 4 * SCALE), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 110),
                       (share_r + 2 * SCALE, share_r + 2 * SCALE),
                       share_r + 1 * SCALE)
    surf.blit(sh, (share_cx - share_r - 2 * SCALE,
                    share_cy - share_r + 2 * SCALE))
    pygame.draw.circle(surf, PANEL_DARK, (share_cx, share_cy), share_r)
    pygame.draw.circle(surf, GOLD_BRIGHT, (share_cx, share_cy),
                       share_r, 2 * SCALE)
    stat_icon(surf, "share", share_cx, share_cy, size=8)


# ── DESIGN 5 — Glass Hero ───────────────────────────────────────────────────

def draw_frosted_panel(surf, rect, source, dim_alpha=120,
                       border_color=GOLD_BRIGHT, border_alpha=140,
                       blur_passes=2):
    """Sample a region of `source`, apply cheap downscale-upscale blur,
    dim, and blit clipped to a rounded rectangle. Fakes a frosted-glass
    Gaussian blur within Pygame's primitive set."""
    # Sample source area
    src = source.subsurface(rect).copy()
    # Multi-pass blur via successive smoothscale down + up
    w, h = src.get_size()
    for _ in range(blur_passes):
        small = pygame.transform.smoothscale(src, (max(2, w // 6),
                                                    max(2, h // 6)))
        src = pygame.transform.smoothscale(small, (w, h))
    # Dim overlay
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((10, 6, 30, dim_alpha))
    src.blit(dim, (0, 0))
    # Subtle internal gradient (slight warm hint)
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        a = int(40 * (1 - t))
        pygame.draw.line(grad, (255, 220, 170, a), (0, yy), (w, yy))
    src.blit(grad, (0, 0))
    # Clip to rounded rect
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, w, h), border_radius=22 * SCALE)
    src.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(src, rect.topleft)
    # Border
    pygame.draw.rect(surf, (*border_color, border_alpha), rect,
                     width=1 * SCALE, border_radius=22 * SCALE)
    # Inner highlight rail
    pygame.draw.line(surf, (*GOLD_PALE, 140),
                     (rect.x + 16 * SCALE, rect.y + 5 * SCALE),
                     (rect.right - 16 * SCALE, rect.y + 5 * SCALE),
                     1 * SCALE)


def frosted_tile(surf, rect, icon_kind, value, label, source):
    """Smaller frosted tile used in v5 grid."""
    src = source.subsurface(rect).copy()
    w, h = src.get_size()
    for _ in range(2):
        small = pygame.transform.smoothscale(src, (max(2, w // 5),
                                                    max(2, h // 5)))
        src = pygame.transform.smoothscale(small, (w, h))
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((10, 6, 28, 150))
    src.blit(dim, (0, 0))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, w, h), border_radius=12 * SCALE)
    src.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(src, rect.topleft)
    pygame.draw.rect(surf, (*GOLD_BRIGHT, 130), rect,
                     width=1 * SCALE, border_radius=12 * SCALE)
    pygame.draw.line(surf, (*GOLD_PALE, 120),
                     (rect.x + 8 * SCALE, rect.y + 3 * SCALE),
                     (rect.right - 8 * SCALE, rect.y + 3 * SCALE),
                     1 * SCALE)
    # Icon
    stat_icon(surf, icon_kind, rect.x + 22 * SCALE,
              rect.centery, size=9)
    # Label top
    lf = font(9, True).render(label, True, GOLD_MUTED)
    lf.set_alpha(220)
    surf.blit(lf, (rect.x + 40 * SCALE, rect.y + 8 * SCALE))
    # Value bottom
    vf = font(20, True).render(str(value), True, GOLD_BRIGHT)
    vsh = font(20, True).render(str(value), True, NEAR_BLACK)
    vsh.set_alpha(170)
    vr = vf.get_rect(midleft=(rect.x + 40 * SCALE,
                               rect.bottom - 16 * SCALE))
    surf.blit(vsh, (vr.x + 1 * SCALE, vr.y + 2 * SCALE))
    surf.blit(vf, vr)


def draw_progress_arc(surf, cx, cy, r, fraction, thickness=4,
                      bg_color=GOLD_DEEP, fg_color=GOLD_BRIGHT):
    """Filled arc sweeping from -90 deg by `fraction` of full circle."""
    fraction = max(0.0, min(1.0, fraction))
    th = thickness * SCALE
    # Background ring
    pygame.draw.circle(surf, bg_color, (cx, cy), r, th)
    # Foreground arc — drawn as a series of small line segments
    start_a = -math.pi / 2
    end_a = start_a + 2 * math.pi * fraction
    steps = max(8, int(2 * math.pi * r * fraction / (2 * SCALE)))
    if steps == 0:
        return
    prev = (cx + math.cos(start_a) * r, cy + math.sin(start_a) * r)
    for i in range(1, steps + 1):
        t = i / steps
        a = start_a + (end_a - start_a) * t
        cur = (cx + math.cos(a) * r, cy + math.sin(a) * r)
        pygame.draw.line(surf, fg_color, prev, cur, th)
        prev = cur
    # End-cap dot
    pygame.draw.circle(surf, GOLD_PALE,
                       (int(prev[0]), int(prev[1])), int(th * 0.7))


def draw_v5_glass_hero(surf, data):
    """Modern minimal premium — frosted glass panel with massive hero
    number and a 2x2 stat tile grid."""
    # Render the night-sky background (no dim) so we can sample for blur
    backdrop(surf, dim=0)

    # Frosted main panel — leaves room for action bar below
    panel = pygame.Rect(24 * SCALE, 48 * SCALE,
                        W - 48 * SCALE, 480 * SCALE)
    # Drop shadow
    sh = pygame.Surface((panel.w + 8 * SCALE, panel.h + 12 * SCALE),
                        pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 130),
                     (0, 0, panel.w + 8 * SCALE, panel.h + 12 * SCALE),
                     border_radius=22 * SCALE)
    surf.blit(sh, (panel.x - 4 * SCALE, panel.y + 6 * SCALE))
    draw_frosted_panel(surf, panel, surf, dim_alpha=160)

    # Diagonal shine band sweeping across the panel
    shine = pygame.Surface(panel.size, pygame.SRCALPHA)
    for i in range(-panel.h // 2, panel.w // 2):
        # narrow diagonal band
        x1 = i + panel.h // 2
        y1 = 0
        x2 = i
        y2 = panel.h
        if 0 <= x1 < panel.w * 1.5 or 0 <= x2 < panel.w * 1.5:
            d_to_center = abs(i - panel.w // 4)
            band = max(0, 1 - d_to_center / (40 * SCALE))
            if band > 0:
                a = int(40 * band)
                pygame.draw.line(shine, (255, 240, 200, a),
                                 (x1, y1), (x2, y2), 1 * SCALE)
    mask = pygame.Surface(panel.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     (0, 0, panel.w, panel.h), border_radius=22 * SCALE)
    shine.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shine, panel.topleft)

    # Top label — sits above the progress arc with clear breathing room
    cap = font(12, True).render("F I N A L   S C O R E", True, GOLD_MUTED)
    cap.set_alpha(230)
    surf.blit(cap, cap.get_rect(center=(W // 2, panel.y + 32 * SCALE)))

    # Massive hero number (clean, less heavy outline)
    big_num = str(data["score"])
    nf = font(110, True).render(big_num, True, GOLD_PALE)
    nsh = font(110, True).render(big_num, True, NEAR_BLACK)
    nr = nf.get_rect(center=(W // 2, panel.y + 158 * SCALE))
    nsh.set_alpha(120)
    surf.blit(nsh, (nr.x + 5 * SCALE, nr.y + 8 * SCALE))
    # Inner-glow gold underlay (slight offset for soft halo)
    underlay = font(110, True).render(big_num, True, GOLD_BRIGHT)
    surf.blit(underlay, nr)
    surf.blit(nf, nr)

    # Progress arc around the number (score / best, max at NEW BEST)
    arc_cx = W // 2
    arc_cy = panel.y + 158 * SCALE
    arc_r = 100 * SCALE
    fraction = (1.0 if data["new_best"]
                else data["score"] / max(1, data["best"]))
    draw_progress_arc(surf, arc_cx, arc_cy, arc_r, fraction,
                      thickness=3,
                      bg_color=lerp(GOLD_DEEP, NIGHT_DEEP, 0.3),
                      fg_color=GOLD_BRIGHT)

    # Sub-caption underneath (best comparison)
    if data["new_best"]:
        sub_text = "NEW PERSONAL BEST"
        sub_color = GOLD_PALE
    else:
        sub_text = f"{data['score']} / {data['best']}  BEST"
        sub_color = GOLD_MUTED
    sf = font(12, True).render(sub_text, True, sub_color)
    sf.set_alpha(230)
    surf.blit(sf, sf.get_rect(center=(W // 2, panel.y + 278 * SCALE)))

    # 2x2 stat tile grid
    stats = [
        ("time", data["time_str"], "TIME"),
        ("coin", data["coins"], "COINS"),
        ("pillar", data["pillars"], "PILLARS"),
        ("crosshair", data["near_misses"], "MISSES"),
    ]
    grid_x = panel.x + 22 * SCALE
    grid_y = panel.y + 300 * SCALE
    grid_gap = 10 * SCALE
    tile_w = (panel.w - 44 * SCALE - grid_gap) // 2
    tile_h = 50 * SCALE
    for i, (kind, val, lbl) in enumerate(stats):
        col = i % 2
        row = i // 2
        r = pygame.Rect(grid_x + col * (tile_w + grid_gap),
                        grid_y + row * (tile_h + grid_gap),
                        tile_w, tile_h)
        frosted_tile(surf, r, kind, val, lbl, source=surf)

    # Power-up strip — sits inside the panel, above its bottom edge
    pu = data["powerups_picked"]
    if pu:
        cap2 = font(10, True).render("P O W E R - U P S",
                                     True, GOLD_MUTED)
        cap2.set_alpha(220)
        cap_y = grid_y + 2 * (tile_h + grid_gap) + 12 * SCALE
        surf.blit(cap2, cap2.get_rect(center=(W // 2, cap_y)))
        chip_size = 16
        chip_w = chip_size * 2 * SCALE + 8 * SCALE
        total_cw = len(pu) * chip_w + (len(pu) - 1) * 6 * SCALE
        sx = (W - total_cw) // 2 + chip_w // 2
        for i, (kind, count) in enumerate(pu):
            powerup_chip(surf, sx + i * (chip_w + 6 * SCALE),
                         cap_y + 26 * SCALE,
                         kind, count, size=chip_size)

    # Action bar BELOW the panel — primary scarlet + outline secondary
    cta_y = panel.bottom + 50 * SCALE
    pill(surf, (W // 2 - 86 * SCALE, cta_y), "PLAY  AGAIN",
         size=20, min_w=190, h=48, primary=True)
    outline_pill(surf, (W // 2 + 110 * SCALE, cta_y), "MENU",
                 size=16, min_w=120, h=42)


# ── Contact sheet ───────────────────────────────────────────────────────────

def make_contact_sheet(filenames, out_name="contact_sheet.png",
                       label_each=True):
    """Stitch all 5 designs into a horizontal strip with labels above
    each."""
    images = [pygame.image.load(os.path.join(OUT, f)) for f in filenames]
    iw, ih = images[0].get_size()
    label_h = 60 if label_each else 0
    margin = 24
    total_w = len(images) * iw + (len(images) + 1) * margin
    total_h = ih + label_h + margin * 2
    sheet = pygame.Surface((total_w, total_h))
    sheet.fill(NIGHT_DEEP)
    # Sparse stars on the sheet background
    random.seed(7)
    for _ in range(int(total_w * total_h / 1800)):
        x = random.randint(0, total_w - 1)
        y = random.randint(0, total_h - 1)
        a = random.randint(120, 200)
        pygame.draw.circle(sheet, (220, 230, 255), (x, y), 1)
        d = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(d, (220, 230, 255, a), (2, 2), 1)
        sheet.blit(d, (x - 1, y - 1))
    titles = [
        "v1 · Trophy Cinema",
        "v2 · Pip's Flight Log",
        "v3 · Constellation Wheel",
        "v4 · Storyboard Strip",
        "v5 · Glass Hero",
    ]
    f = pygame.font.Font(FONT_BOLD, 28)
    for i, img in enumerate(images):
        x = margin + i * (iw + margin)
        y = margin + label_h
        # Label
        if label_each:
            lf = f.render(titles[i], True, GOLD_BRIGHT)
            sheet.blit(lf, lf.get_rect(center=(x + iw // 2,
                                               margin + label_h // 2)))
        # Image with subtle border
        sheet.blit(img, (x, y))
        pygame.draw.rect(sheet, GOLD_BRIGHT,
                         (x - 2, y - 2, iw + 4, ih + 4), 2)
    pygame.image.save(sheet, os.path.join(OUT, out_name))
    print(f"  wrote {os.path.join(OUT, out_name)} "
          f"({total_w}x{total_h})")


# ── Render driver ───────────────────────────────────────────────────────────

VARIANTS = [
    ("v1_trophy_cinema.png", draw_v1_trophy_cinema),
    ("v1_trophy_cinema_r11.png", draw_v1_trophy_cinema),
    ("v2_pip_flight_log.png", draw_v2_pip_flight_log),
    ("v3_constellation_wheel.png", draw_v3_constellation_wheel),
    ("v4_storyboard_strip.png", draw_v4_storyboard_strip),
    ("v5_glass_hero.png", draw_v5_glass_hero),
]


def main():
    print(f"Rendering 5 run-summary mockups at {W}x{H}...")
    filenames = []
    for name, draw_fn in VARIANTS:
        s = pygame.Surface((W, H))
        draw_fn(s, DATA)
        save(name, s)
        filenames.append(name)
    print("Stitching contact sheet...")
    # Contact sheet only shows the canonical 5 (not cache-bust copies)
    sheet_files = [f for f in filenames
                   if not (f.endswith("_r2.png") or f.endswith("_r11.png"))]
    make_contact_sheet(sheet_files)
    # Worst-case stress test of v1: every kind picked at least once
    # so we can verify the chip row never overflows the screen.
    stress = dict(DATA)
    stress["powerups_picked"] = [
        ("triple", 3), ("magnet", 2), ("slowmo", 1),
        ("kfc", 1), ("ghost", 2), ("grow", 1), ("surprise", 1),
    ]
    s = pygame.Surface((W, H))
    draw_v1_trophy_cinema(s, stress)
    save("v1_trophy_cinema_all7_powerups.png", s)
    s = pygame.Surface((W, H))
    draw_v1_trophy_cinema(s, stress)
    save("v1_trophy_cinema_all7_powerups_r11.png", s)
    print("Rendering wing options sheet...")
    render_wing_options()
    print("Done.")


if __name__ == "__main__":
    main()
