"""Generate v4 menu redesign mockups — 5 massive upgrades of the original
v3 menu design.

Each variant keeps Skybit's brand identity (deep navy night sky,
gold-on-red `SKYBIT` title, orange-bordered red pill buttons, BEST +
TOP 10 panels, mountain silhouettes) and pushes ONE quality axis hard:

  v1 ROYAL     — luxury polish (gold leaf, bevels, medallions)
  v2 AVIATOR   — Pip's aviator identity (brass instruments, wings, beacons)
  v3 PARCEL    — courier theme (the menu IS a parcel envelope)
  v4 STARLIGHT — massively enhanced night sky (aurora, moon, constellations)
  v5 FESTIVAL  — monastery / prayer-flag world (lantern garlands, bunting)

All variants reuse the canonical Skybit palette
(`game/hud.py:29-37`) and the bundled Liberation Sans font.
"""
import math
import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()
pygame.display.set_mode((1, 1))

W, H = 360, 640
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "menu_redesign_v4")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "game", "assets")
FONT_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")
FONT_REG  = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")

# ── Skybit canonical palette ────────────────────────────────────────────────
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
CREAM         = (250, 232, 196)


# ── Helpers ─────────────────────────────────────────────────────────────────

def font(size, bold=True):
    return pygame.font.Font(FONT_BOLD if bold else FONT_REG, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def gradient_v(surf, top, bot, rect=None):
    r = rect or surf.get_rect()
    for y in range(r.height):
        t = y / max(1, r.height - 1)
        c = lerp(top, bot, t)
        pygame.draw.line(surf, c, (r.x, r.y + y), (r.x + r.width - 1, r.y + y))


def stroked_text(surf, txt, center, size, fill, outline, px=2,
                 shadow=(3, 5), shadow_alpha=170, bold=True):
    f = font(size, bold)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    for ox in (-px, 0, px):
        for oy in (-px, 0, px):
            if ox or oy:
                surf.blit(out, (r.x + ox, r.y + oy))
    if shadow:
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(shadow_alpha)
        surf.blit(sh, (r.x + shadow[0], r.y + shadow[1]))
    surf.blit(img, r.topleft)
    return r


def skybit_title(surf, cx, cy, size=68, px=3):
    """Canonical v3 gold-on-red title."""
    return stroked_text(surf, "SKYBIT", (cx, cy), size,
                        fill=GOLD_BRIGHT, outline=RED_OUTLINE,
                        px=px, shadow=(3, 5))


def skybit_subtitle(surf, cx, cy, size=20, px=2):
    return stroked_text(surf, "POCKET  SKY  FLYER", (cx, cy), size,
                        fill=GOLD_BRIGHT, outline=RED_OUTLINE,
                        px=px, shadow=(2, 3))


def night_sky(surf, top=NIGHT_DEEP, mid=NIGHT_MID, mountains=True):
    """Canonical v3 background: deep navy gradient + stars +
    mountain silhouette."""
    gradient_v(surf, top, mid)
    # Stars
    random.seed(42)
    for _ in range(120):
        x = random.randint(0, W - 1)
        y = random.randint(0, 380)
        r = random.choice([1, 1, 1, 2])
        a = random.randint(120, 255)
        col = (240, 240, 250)
        s_dot = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s_dot, (*col, a), (r + 1, r + 1), r)
        surf.blit(s_dot, (x - r - 1, y - r - 1))
    # Faint cloud puffs
    for cx, cy, cw in [(60, 90, 100), (260, 70, 110), (320, 160, 80)]:
        s_cloud = pygame.Surface((cw, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(s_cloud, (40, 30, 70, 80), (0, 0, cw, 28))
        pygame.draw.ellipse(s_cloud, (50, 36, 78, 100),
                            (cw // 4, 4, cw - cw // 2, 20))
        surf.blit(s_cloud, (cx - cw // 2, cy - 14))
    if mountains:
        # Far + near silhouettes — same shape as game/hud.py:209
        far = [(0, H), (0, 490), (60, 420), (120, 450), (200, 375),
               (280, 430), (360, 360), (W, 400), (W, H)]
        near = [(0, H), (0, 530), (80, 505), (160, 520), (240, 490),
                (320, 510), (W, 495), (W, H)]
        pygame.draw.polygon(surf, (14, 26, 50), far)
        pygame.draw.polygon(surf, (10, 18, 36), near)


def pill_btn(surf, center, text, size=22, w_min=240, h=52,
             text_color=WHITE, accent=ORANGE_BORDER, glow=False,
             inner_emboss=False):
    """v3-style orange-bordered red-gradient pill. Returns rect."""
    f = font(size, True)
    img = f.render(text, True, text_color)
    w = max(w_min, img.get_width() + 50)
    x = center[0] - w // 2
    y = center[1] - h // 2
    pill = pygame.Surface((w, h), pygame.SRCALPHA)
    # Gradient fill
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = lerp(BTN_TOP, BTN_BOT, t)
        pygame.draw.line(pill, (*c, 255), (0, yy), (w, yy))
    # Rounded mask
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=h // 2)
    pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Orange border
    pygame.draw.rect(pill, accent, (0, 0, w, h), width=2, border_radius=h // 2)
    # Inner highlight at top
    pygame.draw.line(pill, (255, 255, 255, 70),
                     (h // 2, 3), (w - h // 2, 3))
    if inner_emboss:
        pygame.draw.line(pill, (255, 255, 255, 35),
                         (h // 2, 5), (w - h // 2, 5))
        pygame.draw.line(pill, (0, 0, 0, 60),
                         (h // 2, h - 4), (w - h // 2, h - 4))
    surf.blit(pill, (x, y))
    if glow:
        # Soft outer halo
        for r in range(8, 0, -2):
            a = int(40 * (r / 8))
            halo = pygame.Surface((w + r * 2, h + r * 2), pygame.SRCALPHA)
            pygame.draw.rect(halo, (*accent, a),
                             (0, 0, w + r * 2, h + r * 2),
                             width=2, border_radius=(h + r * 2) // 2)
            surf.blit(halo, (x - r, y - r),
                      special_flags=pygame.BLEND_PREMULTIPLIED)
    # Text + drop shadow
    sh = f.render(text, True, NEAR_BLACK)
    sh.set_alpha(160)
    tr = img.get_rect(center=center)
    surf.blit(sh, (tr.x + 1, tr.y + 2))
    surf.blit(img, tr)
    return pygame.Rect(x, y, w, h)


def dark_panel(surf, rect, radius=14, alpha=210, accent=ORANGE_BORDER):
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*PANEL_DARK, alpha),
                     (0, 0, rect.w, rect.h), border_radius=radius)
    pygame.draw.rect(pnl, (*accent, 90),
                     (0, 0, rect.w, rect.h), width=1, border_radius=radius)
    pygame.draw.line(pnl, (*accent, 180),
                     (radius, 3), (rect.w - radius, 3))
    surf.blit(pnl, rect.topleft)


def draw_trophy(surf, cx, cy, size, color=GOLD_BRIGHT,
                shadow=(140, 90, 8)):
    s = size
    cup_top_y = cy - s + 2
    cup_bot_y = cy + 2
    pts = [(cx - s, cup_top_y), (cx + s, cup_top_y),
           (cx + s - 3, cup_bot_y), (cx - s + 3, cup_bot_y)]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, shadow, pts, 1)
    # Handles
    pygame.draw.arc(surf, color,
                    (cx - s - 6, cup_top_y, 8, s + 2),
                    math.pi / 2, math.pi * 3 / 2, 2)
    pygame.draw.arc(surf, color,
                    (cx + s - 2, cup_top_y, 8, s + 2),
                    -math.pi / 2, math.pi / 2, 2)
    # Stem + base
    pygame.draw.rect(surf, color, (cx - 2, cup_bot_y, 4, s // 2))
    pygame.draw.rect(surf, color,
                     (cx - s, cup_bot_y + s // 2, s * 2, 3))
    pygame.draw.rect(surf, color,
                     (cx - s - 1, cup_bot_y + s // 2 + 3, s * 2 + 2, 2))


def save(name, surf):
    out = os.path.join(OUT, name)
    pygame.image.save(surf, out)
    print(f"  wrote {out}")


# ─────────────────────────────────────────────────────────────────────────────
# Reusable ROYAL primitives (lifted from v1_royal so all 7 screens share them)
# ─────────────────────────────────────────────────────────────────────────────

def royal_frame(surf):
    """Gold-leaf outer + inner border + 4 corner medallions +
    top/bottom filigree dots. Draws on top of an existing background."""
    frame_outer = pygame.Rect(8, 8, W - 16, H - 16)
    pygame.draw.rect(surf, (140, 96, 14), frame_outer, width=4, border_radius=12)
    frame_inner = pygame.Rect(14, 14, W - 28, H - 28)
    pygame.draw.rect(surf, GOLD_BRIGHT, frame_inner, width=2, border_radius=10)
    for x in range(40, W - 40, 36):
        pygame.draw.circle(surf, GOLD_BRIGHT, (x, 22), 3, 1)
        pygame.draw.circle(surf, GOLD_BRIGHT, (x, H - 22), 3, 1)
        pygame.draw.line(surf, GOLD_BRIGHT, (x - 6, 22), (x - 3, 22), 1)
        pygame.draw.line(surf, GOLD_BRIGHT, (x + 3, 22), (x + 6, 22), 1)
        pygame.draw.line(surf, GOLD_BRIGHT, (x - 6, H - 22), (x - 3, H - 22), 1)
        pygame.draw.line(surf, GOLD_BRIGHT, (x + 3, H - 22), (x + 6, H - 22), 1)
    for cx, cy in [(20, 20), (W - 20, 20), (20, H - 20), (W - 20, H - 20)]:
        pygame.draw.circle(surf, (60, 40, 80), (cx, cy), 9)
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), 9, 2)
        pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), 3)


def royal_title(surf, text, center, size=68):
    """Beveled gold-on-red title — same recipe as the SKYBIT logo:
    thick red outline halo + dark-gold underlay + black shadow +
    gold-bright fill + subtle top-edge highlight."""
    f = font(size, True)
    base = f.render(text, True, GOLD_BRIGHT)
    base_rect = base.get_rect(center=center)
    out_red = f.render(text, True, RED_OUTLINE)
    for r in range(5, 0, -1):
        for ang in range(0, 360, 30):
            ox = int(math.cos(math.radians(ang)) * r)
            oy = int(math.sin(math.radians(ang)) * r)
            out_red.set_alpha(80 if r > 2 else 255)
            surf.blit(out_red, (base_rect.x + ox, base_rect.y + oy))
    out_red.set_alpha(255)
    sh = f.render(text, True, GOLD_DEEP)
    surf.blit(sh, (base_rect.x + 3, base_rect.y + 5))
    bk = f.render(text, True, NEAR_BLACK)
    bk.set_alpha(180)
    surf.blit(bk, (base_rect.x + 4, base_rect.y + 7))
    surf.blit(base, base_rect)
    hl = f.render(text, True, (255, 240, 180))
    hl.set_alpha(80)
    surf.blit(hl, (base_rect.x, base_rect.y - 1))
    return base_rect


def royal_divider(surf, cy, width=140):
    """Gold double-line with a diamond in the middle."""
    pygame.draw.line(surf, GOLD_BRIGHT,
                     (W // 2 - width // 2, cy),
                     (W // 2 - 14, cy), 1)
    pygame.draw.line(surf, GOLD_BRIGHT,
                     (W // 2 + 14, cy),
                     (W // 2 + width // 2, cy), 1)
    pygame.draw.polygon(surf, GOLD_BRIGHT,
                        [(W // 2, cy - 4), (W // 2 + 6, cy),
                         (W // 2, cy + 4), (W // 2 - 6, cy)])


def royal_pill(surf, center, text, big=False, w=250, glow=False,
               text_color=None):
    """Double-rim red pill: outer gold leaf + inner black gap +
    red gradient body + top sheen + bottom shadow. Returns rect."""
    h = 56 if big else 46
    sz = 22 if big else 18
    x = center[0] - w // 2
    y = center[1] - h // 2
    if glow:
        for r in range(10, 0, -2):
            a = int(40 * (r / 10))
            halo = pygame.Surface((w + r * 2 + 6, h + r * 2 + 6), pygame.SRCALPHA)
            pygame.draw.rect(halo, (*GOLD_BRIGHT, a),
                             (0, 0, w + r * 2 + 6, h + r * 2 + 6),
                             width=2, border_radius=(h + r * 2 + 6) // 2)
            surf.blit(halo, (x - r - 3, y - r - 3),
                      special_flags=pygame.BLEND_PREMULTIPLIED)
    # Outer gold ring
    pygame.draw.rect(surf, GOLD_BRIGHT, (x - 3, y - 3, w + 6, h + 6),
                     border_radius=(h + 6) // 2)
    pygame.draw.rect(surf, GOLD_DEEP, (x - 3, y - 3, w + 6, h + 6), width=1,
                     border_radius=(h + 6) // 2)
    # Inner black gap
    pygame.draw.rect(surf, NEAR_BLACK, (x - 1, y - 1, w + 2, h + 2),
                     border_radius=(h + 2) // 2)
    # Red gradient body
    pill = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = lerp(BTN_TOP, BTN_BOT, t)
        pygame.draw.line(pill, (*c, 255), (0, yy), (w, yy))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_radius=h // 2)
    pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.line(pill, (255, 255, 255, 110),
                     (h // 2, 3), (w - h // 2, 3), 2)
    pygame.draw.line(pill, (0, 0, 0, 80),
                     (h // 2, h - 4), (w - h // 2, h - 4))
    surf.blit(pill, (x, y))
    # Text
    col = text_color or GOLD_BRIGHT
    ti = font(sz, True).render(text, True, col)
    sh = font(sz, True).render(text, True, NEAR_BLACK)
    sh.set_alpha(180)
    tr = ti.get_rect(center=center)
    surf.blit(sh, (tr.x + 1, tr.y + 2))
    surf.blit(ti, tr)
    return pygame.Rect(x, y, w, h)


def royal_medallion(surf, cx, cy, r=44, label=None, value=None,
                    with_trophy=False, with_ribbon=True,
                    value_size=30, label_size=10):
    """Ornate gold medallion: dark-purple interior + thick gold ring +
    thin inner gold ring + radial laurel ticks + optional label/value
    or trophy + optional red ribbon tail."""
    pygame.draw.circle(surf, (60, 40, 80), (cx, cy), r)
    pygame.draw.circle(surf, GOLD_BRIGHT, (cx, cy), r, 3)
    pygame.draw.circle(surf, GOLD_DEEP, (cx, cy), r - 6, 1)
    for ang_deg in range(0, 360, 15):
        a = math.radians(ang_deg)
        x1 = cx + math.cos(a) * (r - 6)
        y1 = cy + math.sin(a) * (r - 6)
        x2 = cx + math.cos(a) * r
        y2 = cy + math.sin(a) * r
        pygame.draw.line(surf, GOLD_BRIGHT, (x1, y1), (x2, y2), 1)
    if label:
        lf = font(label_size, True).render(label, True, GOLD_BRIGHT)
        ly = cy - (r // 4) if value or with_trophy else cy
        surf.blit(lf, lf.get_rect(center=(cx, ly)))
    if value is not None:
        vf = font(value_size, True).render(str(value), True, GOLD_BRIGHT)
        vsh = font(value_size, True).render(str(value), True, NEAR_BLACK)
        vsh.set_alpha(180)
        vy = cy + (r // 5) if label else cy
        vr_rect = vf.get_rect(center=(cx, vy))
        surf.blit(vsh, (vr_rect.x + 1, vr_rect.y + 2))
        surf.blit(vf, vr_rect)
    elif with_trophy:
        draw_trophy(surf, cx, cy + (r // 4), max(8, r // 4))
    if with_ribbon:
        rw = int(r * 0.4)
        ry = cy + r - 2
        pygame.draw.polygon(surf, (200, 50, 40),
                            [(cx - rw, ry), (cx + rw, ry),
                             (cx + rw - 4, ry + 18),
                             (cx, ry + 12),
                             (cx - rw + 4, ry + 18)])
        pygame.draw.polygon(surf, (140, 20, 20),
                            [(cx - rw, ry), (cx + rw, ry),
                             (cx + rw - 4, ry + 18),
                             (cx, ry + 12),
                             (cx - rw + 4, ry + 18)], 1)


def royal_card(surf, rect, radius=12, alpha=215):
    """Dark-purple panel with a gold-leaf border. Used for stat rows,
    leaderboard rows, instruction cards, nameplate field, etc."""
    pnl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(pnl, (*PANEL_DARK, alpha),
                     (0, 0, rect.w, rect.h), border_radius=radius)
    pygame.draw.rect(pnl, GOLD_BRIGHT,
                     (0, 0, rect.w, rect.h), width=2, border_radius=radius)
    # Inner subtle highlight
    pygame.draw.line(pnl, (255, 240, 180, 90),
                     (radius, 3), (rect.w - radius, 3))
    surf.blit(pnl, rect.topleft)


def royal_ribbon_banner(surf, cx, cy, text, w=160, h=28):
    """Hanging cloth banner — gold body with darker scalloped ends,
    red trim, dark text. Used for 'NEW BEST!' and 'EFFECTS LAST 8 SECONDS'."""
    rect = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    # Body
    pygame.draw.rect(surf, GOLD_BRIGHT, rect)
    pygame.draw.rect(surf, GOLD_DEEP, rect, 2)
    # Notched ends
    pygame.draw.polygon(surf, (10, 8, 18),
                        [(rect.x, rect.y), (rect.x + 8, rect.centery),
                         (rect.x, rect.bottom)])
    pygame.draw.polygon(surf, (10, 8, 18),
                        [(rect.right, rect.y), (rect.right - 8, rect.centery),
                         (rect.right, rect.bottom)])
    # Red trim lines top + bottom
    pygame.draw.line(surf, (200, 50, 40),
                     (rect.x + 6, rect.y + 4), (rect.right - 6, rect.y + 4), 1)
    pygame.draw.line(surf, (200, 50, 40),
                     (rect.x + 6, rect.bottom - 4), (rect.right - 6, rect.bottom - 4), 1)
    ti = font(13, True).render(text, True, (90, 20, 10))
    surf.blit(ti, ti.get_rect(center=rect.center))


# ─────────────────────────────────────────────────────────────────────────────
# v1 — ROYAL: luxury polish
# ─────────────────────────────────────────────────────────────────────────────
def v1_royal():
    s = pygame.Surface((W, H))
    night_sky(s)

    # ── Gold-leaf decorative frame around the whole screen ──
    # Outer thick border + inner thin border with corner medallions
    frame_outer = pygame.Rect(8, 8, W - 16, H - 16)
    pygame.draw.rect(s, (140, 96, 14), frame_outer, width=4, border_radius=12)
    frame_inner = pygame.Rect(14, 14, W - 28, H - 28)
    pygame.draw.rect(s, GOLD_BRIGHT, frame_inner, width=2, border_radius=10)
    # Filigree along top + bottom inside the frame
    for x in range(40, W - 40, 36):
        # Tiny fleur ornaments
        pygame.draw.circle(s, GOLD_BRIGHT, (x, 22), 3, 1)
        pygame.draw.circle(s, GOLD_BRIGHT, (x, H - 22), 3, 1)
        pygame.draw.line(s, GOLD_BRIGHT, (x - 6, 22), (x - 3, 22), 1)
        pygame.draw.line(s, GOLD_BRIGHT, (x + 3, 22), (x + 6, 22), 1)
        pygame.draw.line(s, GOLD_BRIGHT, (x - 6, H - 22), (x - 3, H - 22), 1)
        pygame.draw.line(s, GOLD_BRIGHT, (x + 3, H - 22), (x + 6, H - 22), 1)
    # Corner medallions
    for cx, cy in [(20, 20), (W - 20, 20), (20, H - 20), (W - 20, H - 20)]:
        pygame.draw.circle(s, (60, 40, 80), (cx, cy), 9)
        pygame.draw.circle(s, GOLD_BRIGHT, (cx, cy), 9, 2)
        pygame.draw.circle(s, GOLD_BRIGHT, (cx, cy), 3)

    # ── Title with metallic gold-leaf bevel ──
    # Big title — multiple-pass treatment: thick red outline → dark gold
    # shadow → gold-bright fill → bright sheen line through the middle
    title_y = 130
    f = font(74, True)
    base = f.render("SKYBIT", True, GOLD_BRIGHT)
    base_rect = base.get_rect(center=(W // 2, title_y))
    # Bigger red outline halo
    out_red = f.render("SKYBIT", True, RED_OUTLINE)
    for r in range(5, 0, -1):
        for ang in range(0, 360, 30):
            ox = int(math.cos(math.radians(ang)) * r)
            oy = int(math.sin(math.radians(ang)) * r)
            out_red.set_alpha(80 if r > 2 else 255)
            s.blit(out_red, (base_rect.x + ox, base_rect.y + oy))
    out_red.set_alpha(255)
    # Dark-gold shadow underlay
    sh = f.render("SKYBIT", True, GOLD_DEEP)
    s.blit(sh, (base_rect.x + 3, base_rect.y + 5))
    # Black soft shadow
    bk = f.render("SKYBIT", True, NEAR_BLACK)
    bk.set_alpha(180)
    s.blit(bk, (base_rect.x + 4, base_rect.y + 7))
    s.blit(base, base_rect)
    # Subtle inner highlight on the top edge of each glyph — not a band
    hl = f.render("SKYBIT", True, (255, 240, 180))
    hl.set_alpha(80)
    s.blit(hl, (base_rect.x, base_rect.y - 1))
    # Sub
    skybit_subtitle(s, W // 2, 188, size=18)
    # Decorative divider — gold double-line with diamond
    pygame.draw.line(s, GOLD_BRIGHT, (W // 2 - 70, 210), (W // 2 - 14, 210), 1)
    pygame.draw.line(s, GOLD_BRIGHT, (W // 2 + 14, 210), (W // 2 + 70, 210), 1)
    pygame.draw.polygon(s, GOLD_BRIGHT,
                        [(W // 2, 206), (W // 2 + 6, 210), (W // 2, 214), (W // 2 - 6, 210)])

    # ── Buttons — embossed pills with gold double-rim ──
    def royal_pill(center, text, big=False):
        h = 56 if big else 46
        sz = 22 if big else 18
        w = 250
        x = center[0] - w // 2
        y = center[1] - h // 2
        # Outer gold ring
        pygame.draw.rect(s, GOLD_BRIGHT, (x - 3, y - 3, w + 6, h + 6),
                         border_radius=(h + 6) // 2)
        pygame.draw.rect(s, GOLD_DEEP, (x - 3, y - 3, w + 6, h + 6), width=1,
                         border_radius=(h + 6) // 2)
        # Inner gold ring
        pygame.draw.rect(s, NEAR_BLACK, (x - 1, y - 1, w + 2, h + 2),
                         border_radius=(h + 2) // 2)
        pill = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = lerp(BTN_TOP, BTN_BOT, t)
            pygame.draw.line(pill, (*c, 255), (0, yy), (w, yy))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=h // 2)
        pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Top sheen
        pygame.draw.line(pill, (255, 255, 255, 110), (h // 2, 3), (w - h // 2, 3), 2)
        # Bottom shadow
        pygame.draw.line(pill, (0, 0, 0, 80), (h // 2, h - 4), (w - h // 2, h - 4))
        s.blit(pill, (x, y))
        ti = font(sz, True).render(text, True, GOLD_BRIGHT)
        sh = font(sz, True).render(text, True, NEAR_BLACK)
        sh.set_alpha(180)
        tr = ti.get_rect(center=center)
        s.blit(sh, (tr.x + 1, tr.y + 2))
        s.blit(ti, tr)

    royal_pill((W // 2, 270), "TAP TO START", big=True)
    royal_pill((W // 2, 332), "HOW TO PLAY")
    royal_pill((W // 2, 388), "POWER-UPS")

    # ── BEST + TOP 10 as ornate medallions ──
    # Left medallion — BEST
    mcx_l, mcy = 90, 500
    pygame.draw.circle(s, (60, 40, 80), (mcx_l, mcy), 44)
    pygame.draw.circle(s, GOLD_BRIGHT, (mcx_l, mcy), 44, 3)
    pygame.draw.circle(s, GOLD_DEEP, (mcx_l, mcy), 38, 1)
    # Laurel-like ticks
    for ang_deg in range(0, 360, 15):
        a = math.radians(ang_deg)
        x1 = mcx_l + math.cos(a) * 38
        y1 = mcy + math.sin(a) * 38
        x2 = mcx_l + math.cos(a) * 44
        y2 = mcy + math.sin(a) * 44
        pygame.draw.line(s, GOLD_BRIGHT, (x1, y1), (x2, y2), 1)
    lbl = font(10, True).render("BEST", True, GOLD_BRIGHT)
    s.blit(lbl, lbl.get_rect(center=(mcx_l, mcy - 12)))
    val = font(30, True).render("42", True, GOLD_BRIGHT)
    sh = font(30, True).render("42", True, NEAR_BLACK)
    sh.set_alpha(180)
    vr = val.get_rect(center=(mcx_l, mcy + 8))
    s.blit(sh, (vr.x + 1, vr.y + 2))
    s.blit(val, vr)
    # Ribbon underneath
    pygame.draw.polygon(s, (200, 50, 40),
                        [(mcx_l - 18, mcy + 42), (mcx_l + 18, mcy + 42),
                         (mcx_l + 14, mcy + 60), (mcx_l, mcy + 54),
                         (mcx_l - 14, mcy + 60)])

    # Right medallion — TOP 10 with trophy
    mcx_r = W - 90
    pygame.draw.circle(s, (60, 40, 80), (mcx_r, mcy), 44)
    pygame.draw.circle(s, GOLD_BRIGHT, (mcx_r, mcy), 44, 3)
    pygame.draw.circle(s, GOLD_DEEP, (mcx_r, mcy), 38, 1)
    for ang_deg in range(0, 360, 15):
        a = math.radians(ang_deg)
        x1 = mcx_r + math.cos(a) * 38
        y1 = mcy + math.sin(a) * 38
        x2 = mcx_r + math.cos(a) * 44
        y2 = mcy + math.sin(a) * 44
        pygame.draw.line(s, GOLD_BRIGHT, (x1, y1), (x2, y2), 1)
    lbl = font(10, True).render("TOP 10", True, GOLD_BRIGHT)
    s.blit(lbl, lbl.get_rect(center=(mcx_r, mcy - 16)))
    draw_trophy(s, mcx_r, mcy + 10, 11)
    pygame.draw.polygon(s, (200, 50, 40),
                        [(mcx_r - 18, mcy + 42), (mcx_r + 18, mcy + 42),
                         (mcx_r + 14, mcy + 60), (mcx_r, mcy + 54),
                         (mcx_r - 14, mcy + 60)])

    save("v1_royal.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# v2 — AVIATOR
# ─────────────────────────────────────────────────────────────────────────────
def v2_aviator():
    s = pygame.Surface((W, H))
    night_sky(s)
    # Map-grid overlay — faint navigation lines
    grid = pygame.Surface((W, H), pygame.SRCALPHA)
    for x in range(0, W, 36):
        pygame.draw.line(grid, (60, 200, 220, 18), (x, 0), (x, 400), 1)
    for y in range(0, 400, 36):
        pygame.draw.line(grid, (60, 200, 220, 18), (0, y), (W, y), 1)
    s.blit(grid, (0, 0))
    # Compass rose (faint, top-right) — navigation feel
    cr_cx, cr_cy = W - 40, 50
    pygame.draw.circle(s, (255, 200, 80, 80), (cr_cx, cr_cy), 22, 1)
    for ang_deg in range(0, 360, 45):
        a = math.radians(ang_deg)
        x1 = cr_cx + math.cos(a) * 4
        y1 = cr_cy + math.sin(a) * 4
        x2 = cr_cx + math.cos(a) * 22
        y2 = cr_cy + math.sin(a) * 22
        pygame.draw.line(s, (240, 200, 110), (x1, y1), (x2, y2), 1)
    pygame.draw.polygon(s, RED_OUTLINE,
                        [(cr_cx, cr_cy - 22), (cr_cx - 4, cr_cy), (cr_cx + 4, cr_cy)])
    pygame.draw.polygon(s, GOLD_BRIGHT,
                        [(cr_cx, cr_cy + 22), (cr_cx - 4, cr_cy), (cr_cx + 4, cr_cy)])

    # ── Title with wings flanking it ──
    skybit_title(s, W // 2, 130, size=72, px=3)
    # Wings — feathered chevrons left and right of title
    def wing(cx, cy, dir):
        for i in range(5):
            length = 30 - i * 4
            y_off = i * 5
            pygame.draw.line(s, GOLD_BRIGHT,
                             (cx, cy + y_off - 8),
                             (cx + dir * length, cy + y_off - 4), 2)
            pygame.draw.line(s, GOLD_DEEP,
                             (cx, cy + y_off - 8),
                             (cx + dir * length, cy + y_off - 4), 1)
    wing(40, 130, +1)
    wing(W - 40, 130, -1)
    skybit_subtitle(s, W // 2, 188, size=20)
    # Decorative line with airplane glyph
    pygame.draw.line(s, GOLD_BRIGHT, (W // 2 - 70, 210), (W // 2 - 12, 210), 1)
    pygame.draw.line(s, GOLD_BRIGHT, (W // 2 + 12, 210), (W // 2 + 70, 210), 1)
    # Tiny plane silhouette in center
    pygame.draw.polygon(s, GOLD_BRIGHT,
                        [(W // 2 - 7, 210), (W // 2 + 6, 210),
                         (W // 2 + 8, 213), (W // 2 + 6, 210),
                         (W // 2 + 3, 208), (W // 2 + 3, 212)])
    pygame.draw.line(s, GOLD_BRIGHT, (W // 2 - 2, 207), (W // 2 + 2, 213), 1)

    # ── Buttons — brass-bordered enamel signs ──
    def brass_btn(center, text, big=False):
        h = 54 if big else 44
        sz = 20 if big else 17
        w = 250
        x = center[0] - w // 2
        y = center[1] - h // 2
        # Brass plate behind (slightly bigger, brass color)
        brass = pygame.Rect(x - 5, y - 5, w + 10, h + 10)
        pygame.draw.rect(s, GOLD_BRIGHT, brass, border_radius=(h + 10) // 2)
        pygame.draw.rect(s, GOLD_DEEP, brass, width=2, border_radius=(h + 10) // 2)
        # Rivet heads on corners
        for rx, ry in [(brass.x + 8, brass.y + brass.h // 2),
                       (brass.right - 8, brass.y + brass.h // 2)]:
            pygame.draw.circle(s, (160, 110, 30), (rx, ry), 3)
            pygame.draw.circle(s, (255, 240, 180), (rx - 1, ry - 1), 1)
        # Inner red enamel pill
        pill = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            t = yy / max(1, h - 1)
            c = lerp(BTN_TOP, BTN_BOT, t)
            pygame.draw.line(pill, (*c, 255), (0, yy), (w, yy))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=h // 2)
        pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.line(pill, (255, 255, 255, 110), (h // 2, 3), (w - h // 2, 3), 2)
        s.blit(pill, (x, y))
        ti = font(sz, True).render(text, True, WHITE)
        sh = font(sz, True).render(text, True, NEAR_BLACK)
        sh.set_alpha(180)
        tr = ti.get_rect(center=center)
        s.blit(sh, (tr.x + 1, tr.y + 2))
        s.blit(ti, tr)

    brass_btn((W // 2, 280), "TAP TO START", big=True)
    brass_btn((W // 2, 342), "HOW TO PLAY")
    brass_btn((W // 2, 396), "POWER-UPS")

    # ── BEST + TOP 10 — round brass instrument bezels ──
    def gauge_panel(cx, cy, label, value, with_trophy=False):
        r = 50
        pygame.draw.circle(s, GOLD_BRIGHT, (cx, cy), r + 3)
        pygame.draw.circle(s, GOLD_DEEP, (cx, cy), r + 3, 2)
        pygame.draw.circle(s, PANEL_DARK, (cx, cy), r)
        pygame.draw.circle(s, (60, 200, 220), (cx, cy), r, 1)
        # Inner tick marks
        for ang_deg in range(0, 360, 30):
            a = math.radians(ang_deg)
            x1 = cx + math.cos(a) * (r - 4)
            y1 = cy + math.sin(a) * (r - 4)
            x2 = cx + math.cos(a) * (r - 1)
            y2 = cy + math.sin(a) * (r - 1)
            pygame.draw.line(s, GOLD_MUTED, (x1, y1), (x2, y2), 1)
        # Rivets
        for ang_deg in (135, 225, 45, -45):
            a = math.radians(ang_deg)
            rx = cx + math.cos(a) * (r + 1)
            ry = cy + math.sin(a) * (r + 1)
            pygame.draw.circle(s, GOLD_DEEP, (int(rx), int(ry)), 2)
        # Label
        lb = font(10, True).render(label, True, GOLD_BRIGHT)
        s.blit(lb, lb.get_rect(center=(cx, cy - 22)))
        if with_trophy:
            draw_trophy(s, cx, cy + 8, 12)
        else:
            vf = font(32, True).render(value, True, GOLD_BRIGHT)
            sh = font(32, True).render(value, True, NEAR_BLACK)
            sh.set_alpha(160)
            vr = vf.get_rect(center=(cx, cy + 8))
            s.blit(sh, (vr.x + 1, vr.y + 2))
            s.blit(vf, vr)

    gauge_panel(86, 510, "BEST RUN", "42")
    gauge_panel(W - 86, 510, "TOP 10", "", with_trophy=True)

    # Tagline above gauges
    tagline = font(9, True).render("CAPTAIN  PIP  ·  SCARLET  SQUADRON",
                                   True, (200, 230, 240))
    tagline.set_alpha(200)
    s.blit(tagline, tagline.get_rect(center=(W // 2, 444)))

    save("v2_aviator.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# v3 — PARCEL: the menu is a wrapped parcel
# ─────────────────────────────────────────────────────────────────────────────
def v3_parcel():
    s = pygame.Surface((W, H))
    night_sky(s)

    # ── A wrapped-parcel envelope frame around the whole menu content ──
    # Inset kraft-tan envelope card with red ribbon cross
    env = pygame.Rect(20, 60, W - 40, H - 100)
    pygame.draw.rect(s, NEAR_BLACK, env.inflate(6, 6), border_radius=14)
    # Kraft body — gradient from warm tan to slightly darker
    body = pygame.Surface(env.size, pygame.SRCALPHA)
    for yy in range(env.h):
        t = yy / max(1, env.h - 1)
        c = lerp((215, 178, 130), (185, 140, 90), t)
        pygame.draw.line(body, (*c, 245), (0, yy), (env.w, yy))
    mask = pygame.Surface(env.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, env.w, env.h), border_radius=10)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(body, env.topleft)
    # Paper grain noise
    random.seed(8)
    for _ in range(800):
        x = random.randint(env.x + 4, env.right - 4)
        y = random.randint(env.y + 4, env.bottom - 4)
        if random.random() < 0.15:
            pygame.draw.circle(s, (160, 120, 80), (x, y), 1)
    # Dark border
    pygame.draw.rect(s, (90, 56, 30), env, 3, border_radius=10)

    # Red ribbon cross over the parcel
    rv_w = 26
    rv = pygame.Rect(env.centerx - rv_w // 2, env.y, rv_w, env.h)
    pygame.draw.rect(s, (200, 50, 50), rv)
    pygame.draw.line(s, (255, 110, 100), (rv.x + 4, rv.y), (rv.x + 4, rv.bottom), 2)
    pygame.draw.line(s, (140, 20, 20), (rv.right - 1, rv.y), (rv.right - 1, rv.bottom), 1)
    rh_w = 22
    # Horizontal ribbon — under the buttons area
    rh = pygame.Rect(env.x, 250 - rh_w // 2, env.w, rh_w)
    pygame.draw.rect(s, (200, 50, 50), rh)
    pygame.draw.line(s, (255, 110, 100), (rh.x, rh.y + 4), (rh.right, rh.y + 4), 2)
    pygame.draw.line(s, (140, 20, 20), (rh.x, rh.bottom - 1), (rh.right, rh.bottom - 1), 1)
    # Bow at the centre
    bow_y = 250 - rh_w // 2 - 6
    pygame.draw.ellipse(s, (200, 50, 50), (env.centerx - 30, bow_y - 22, 30, 36))
    pygame.draw.ellipse(s, (140, 20, 20), (env.centerx - 30, bow_y - 22, 30, 36), 2)
    pygame.draw.ellipse(s, (200, 50, 50), (env.centerx, bow_y - 22, 30, 36))
    pygame.draw.ellipse(s, (140, 20, 20), (env.centerx, bow_y - 22, 30, 36), 2)
    pygame.draw.rect(s, (200, 50, 50), (env.centerx - 6, bow_y - 6, 12, 18))
    pygame.draw.rect(s, (140, 20, 20), (env.centerx - 6, bow_y - 6, 12, 18), 1)

    # Corner postage stamps — small perforated squares in top corners
    def stamp(cx, cy, color, glyph):
        st = pygame.Rect(cx - 22, cy - 14, 44, 28)
        pygame.draw.rect(s, WHITE, st)
        pygame.draw.rect(s, NEAR_BLACK, st, 1)
        # Perforations
        for px_ in range(st.x + 2, st.right, 4):
            pygame.draw.circle(s, (215, 178, 130), (px_, st.y), 1)
            pygame.draw.circle(s, (215, 178, 130), (px_, st.bottom), 1)
        for py_ in range(st.y + 2, st.bottom, 4):
            pygame.draw.circle(s, (215, 178, 130), (st.x, py_), 1)
            pygame.draw.circle(s, (215, 178, 130), (st.right, py_), 1)
        # Inner color
        pygame.draw.rect(s, color, st.inflate(-6, -6))
        gf = font(11, True).render(glyph, True, WHITE)
        s.blit(gf, gf.get_rect(center=st.center))

    stamp(env.x + 30, env.y + 22, (60, 90, 160), "AIR")
    stamp(env.right - 30, env.y + 22, (200, 50, 50), "$5")

    # Postmark — circular black stamp lower-left, away from the title
    pm_cx, pm_cy = 78, 270
    pygame.draw.circle(s, NEAR_BLACK, (pm_cx, pm_cy), 28, 2)
    pygame.draw.circle(s, NEAR_BLACK, (pm_cx, pm_cy), 22, 1)
    pf = font(8, True).render("SKYBIT  AIR  MAIL", True, NEAR_BLACK)
    pf_r = pf.get_rect(center=(pm_cx, pm_cy - 9))
    s.blit(pf, pf_r)
    pf2 = font(10, True).render("·  V4  ·", True, NEAR_BLACK)
    s.blit(pf2, pf2.get_rect(center=(pm_cx, pm_cy)))
    pf3 = font(7, True).render("DELIVERED", True, NEAR_BLACK)
    s.blit(pf3, pf3.get_rect(center=(pm_cx, pm_cy + 9)))

    # ── Title — stamped/embossed onto the kraft above the bow ──
    skybit_title(s, W // 2, 130, size=66, px=3)
    skybit_subtitle(s, W // 2, 180, size=16)

    # ── Buttons — pill style sitting BELOW the bow ──
    pill_btn(s, (W // 2, 322), "TAP TO START", size=22, w_min=240, h=54, glow=True)
    pill_btn(s, (W // 2, 384), "HOW TO PLAY", size=18, w_min=240, h=46)
    pill_btn(s, (W // 2, 440), "POWER-UPS", size=18, w_min=240, h=46)

    # ── BEST + TOP 10 — wax-seal on the parcel ──
    # Left wax seal
    wcx, wcy = 70, 540
    pygame.draw.circle(s, (140, 20, 20), (wcx, wcy), 30)
    pygame.draw.circle(s, (200, 50, 40), (wcx, wcy), 28)
    pygame.draw.circle(s, (100, 10, 10), (wcx, wcy), 30, 2)
    # Drip
    pygame.draw.polygon(s, (160, 20, 20),
                        [(wcx + 28, wcy + 10), (wcx + 34, wcy + 22), (wcx + 22, wcy + 18)])
    bl = font(9, True).render("BEST", True, GOLD_BRIGHT)
    s.blit(bl, bl.get_rect(center=(wcx, wcy - 9)))
    vl = font(22, True).render("42", True, GOLD_BRIGHT)
    sh = font(22, True).render("42", True, NEAR_BLACK)
    sh.set_alpha(180)
    vr = vl.get_rect(center=(wcx, wcy + 7))
    s.blit(sh, (vr.x + 1, vr.y + 2))
    s.blit(vl, vr)

    # Right wax seal — TOP 10 with trophy
    tcx, tcy = W - 70, 540
    pygame.draw.circle(s, (140, 20, 20), (tcx, tcy), 30)
    pygame.draw.circle(s, (200, 50, 40), (tcx, tcy), 28)
    pygame.draw.circle(s, (100, 10, 10), (tcx, tcy), 30, 2)
    tl = font(9, True).render("TOP 10", True, GOLD_BRIGHT)
    s.blit(tl, tl.get_rect(center=(tcx, tcy - 11)))
    draw_trophy(s, tcx, tcy + 6, 9, color=GOLD_BRIGHT)

    save("v3_parcel.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# v4 — STARLIGHT: massively enhanced night sky
# ─────────────────────────────────────────────────────────────────────────────
def v4_starlight():
    s = pygame.Surface((W, H))
    # Background — slightly richer gradient than base
    gradient_v(s, (4, 0, 18), (28, 18, 70))

    # Aurora ribbons (subtle, behind stars)
    aurora = pygame.Surface((W, H), pygame.SRCALPHA)
    for col, base_y, amp, freq, sign in [
        ((40, 130, 90), 120, 50, 1.1, 1),
        ((90, 60, 160), 180, 40, 0.85, -1),
        ((150, 40, 110), 240, 30, 1.3, 1),
    ]:
        for w_ in range(12, 0, -2):
            pts_top, pts_bot = [], []
            for x in range(0, W + 1, 4):
                y_off = math.sin((x / W) * math.pi * freq) * amp * sign
                pts_top.append((x, base_y + y_off - w_ * 3))
                pts_bot.append((x, base_y + y_off + w_ * 3))
            pts = pts_top + list(reversed(pts_bot))
            a = max(2, 14 - w_)
            pygame.draw.polygon(aurora, (*col, a), pts)
    s.blit(aurora, (0, 0))

    # Stars — denser than v3
    random.seed(7)
    for _ in range(220):
        x = random.randint(0, W - 1)
        y = random.randint(0, 460)
        r = random.choices([1, 2, 3], weights=[8, 3, 1])[0]
        a = random.randint(140, 255)
        d = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(d, (240, 245, 255, a), (r + 1, r + 1), r)
        s.blit(d, (x - r - 1, y - r - 1))
    # Big "sparkle" stars with cross flares
    for cx, cy in [(40, 100), (310, 120), (60, 250), (300, 220),
                   (180, 60), (90, 380), (290, 340)]:
        pygame.draw.circle(s, (255, 250, 230), (cx, cy), 3)
        for dx, dy in [(-9, 0), (9, 0), (0, -9), (0, 9)]:
            pygame.draw.aaline(s, (255, 250, 230, 200),
                               (cx, cy), (cx + dx, cy + dy))

    # Full moon top-left
    moon_cx, moon_cy = 70, 80
    glow = pygame.Surface((140, 140), pygame.SRCALPHA)
    for r in range(68, 0, -3):
        a = int(50 * (1 - r / 68))
        pygame.draw.circle(glow, (255, 235, 180, a), (70, 70), r)
    s.blit(glow, (moon_cx - 70, moon_cy - 70))
    pygame.draw.circle(s, (250, 240, 215), (moon_cx, moon_cy), 22)
    pygame.draw.circle(s, (220, 210, 190), (moon_cx + 6, moon_cy - 4), 18)
    # Crater shadows
    pygame.draw.circle(s, (200, 195, 175), (moon_cx + 5, moon_cy + 2), 4)
    pygame.draw.circle(s, (200, 195, 175), (moon_cx - 3, moon_cy + 8), 3)

    # Shooting star — diagonal streak top-right
    ss_x, ss_y = 280, 60
    for i in range(20):
        a = int(180 * (1 - i / 20))
        pygame.draw.line(s, (255, 250, 220, a),
                         (ss_x + i * 3, ss_y + i * 2),
                         (ss_x + (i + 1) * 3, ss_y + (i + 1) * 2), 2)
    pygame.draw.circle(s, (255, 255, 230), (ss_x, ss_y), 3)

    # Constellation lines between sparkle stars
    constellation = [(40, 100), (180, 60), (310, 120),
                     (300, 220), (290, 340), (90, 380), (60, 250)]
    for i in range(len(constellation) - 1):
        pygame.draw.aaline(s, (140, 180, 240, 90),
                           constellation[i], constellation[i + 1])

    # Pip silhouette flying across, slightly behind the title
    pip_x, pip_y = 280, 168
    # Body
    pygame.draw.ellipse(s, (220, 50, 50), (pip_x - 10, pip_y - 8, 24, 16))
    # Tail
    pygame.draw.polygon(s, (200, 30, 30),
                        [(pip_x - 12, pip_y), (pip_x - 22, pip_y - 4), (pip_x - 20, pip_y + 4)])
    # Wing
    pygame.draw.polygon(s, (40, 100, 220),
                        [(pip_x - 2, pip_y - 4), (pip_x + 6, pip_y - 14),
                         (pip_x + 12, pip_y - 4)])
    # Beak
    pygame.draw.polygon(s, (255, 200, 60),
                        [(pip_x + 12, pip_y - 2), (pip_x + 18, pip_y),
                         (pip_x + 12, pip_y + 2)])
    # Parcel trailing
    pygame.draw.rect(s, (180, 130, 80), (pip_x - 6, pip_y + 8, 10, 10))
    pygame.draw.line(s, (200, 50, 50), (pip_x - 1, pip_y + 8), (pip_x - 1, pip_y + 18), 2)
    # Motion trail
    for i in range(8):
        a = int(50 * (1 - i / 8))
        pygame.draw.circle(s, (240, 245, 255, a),
                           (pip_x - 14 - i * 4, pip_y - 1), 1)

    # ── Title with stronger glow halo + sheen ──
    # Halo behind title
    halo = pygame.Surface((280, 110), pygame.SRCALPHA)
    for r in range(70, 0, -4):
        a = int(40 * (1 - r / 70))
        pygame.draw.ellipse(halo, (180, 220, 255, a),
                            (140 - r, 55 - r // 2, r * 2, r))
    s.blit(halo, (W // 2 - 140, 80))
    skybit_title(s, W // 2, 130, size=72, px=3)
    # Sub
    skybit_subtitle(s, W // 2, 192, size=20)
    # Aurora-colored divider
    line = pygame.Surface((180, 3), pygame.SRCALPHA)
    for x in range(180):
        t = x / 180
        c = lerp((40, 200, 180), (200, 80, 180), t)
        pygame.draw.line(line, (*c, 255), (x, 0), (x, 3))
    s.blit(line, line.get_rect(center=(W // 2, 216)))

    # ── Buttons — pills with cyan rim accent + soft outer glow ──
    pill_btn(s, (W // 2, 290), "TAP TO START", size=22, w_min=240, h=54,
             accent=ORANGE_BORDER, glow=True)
    pill_btn(s, (W // 2, 354), "HOW TO PLAY", size=18, w_min=240, h=44)
    pill_btn(s, (W // 2, 410), "POWER-UPS", size=18, w_min=240, h=44)

    # ── BEST + TOP 10 — glass panels with starlight bleeding through ──
    panel_w = 144
    gap = 12
    total = panel_w * 2 + gap
    left_x = (W - total) // 2
    cy = H - 80
    # BEST
    br = pygame.Rect(left_x, cy - 32, panel_w, 64)
    glass = pygame.Surface(br.size, pygame.SRCALPHA)
    pygame.draw.rect(glass, (*PANEL_DARK, 180), (0, 0, br.w, br.h), border_radius=14)
    pygame.draw.rect(glass, (200, 230, 255, 200), (0, 0, br.w, br.h), width=1, border_radius=14)
    pygame.draw.line(glass, (255, 255, 255, 120), (12, 3), (br.w - 12, 3))
    s.blit(glass, br.topleft)
    lf = font(10, False).render("B E S T", True, GOLD_MUTED)
    lf.set_alpha(220)
    s.blit(lf, lf.get_rect(center=(br.centerx, cy - 16)))
    vf = font(28, True).render("42", True, GOLD_BRIGHT)
    sh = font(28, True).render("42", True, NEAR_BLACK)
    sh.set_alpha(160)
    vr = vf.get_rect(center=(br.centerx, cy + 10))
    s.blit(sh, (vr.x + 1, vr.y + 2))
    s.blit(vf, vr)
    # TOP 10
    tr_rect = pygame.Rect(left_x + panel_w + gap, cy - 32, panel_w, 64)
    glass2 = pygame.Surface(tr_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(glass2, (*PANEL_DARK, 180), (0, 0, tr_rect.w, tr_rect.h), border_radius=14)
    pygame.draw.rect(glass2, (255, 200, 230, 200), (0, 0, tr_rect.w, tr_rect.h), width=1, border_radius=14)
    pygame.draw.line(glass2, (255, 255, 255, 120), (12, 3), (tr_rect.w - 12, 3))
    s.blit(glass2, tr_rect.topleft)
    tlf = font(10, False).render("T O P   10", True, GOLD_MUTED)
    tlf.set_alpha(220)
    s.blit(tlf, tlf.get_rect(center=(tr_rect.centerx, cy - 16)))
    draw_trophy(s, tr_rect.centerx, cy + 12, 12)

    save("v4_starlight.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# v5 — FESTIVAL: prayer-flag bunting + lantern garlands
# ─────────────────────────────────────────────────────────────────────────────
def v5_festival():
    s = pygame.Surface((W, H))
    night_sky(s)

    # Prayer-flag bunting strung across the top
    # Two strings — a flatter back string + draped front string
    flag_colors = [(220, 60, 60), (60, 140, 200), (240, 200, 70),
                   (60, 170, 100), (255, 130, 80)]
    # Back string
    for x in range(-10, W + 10, 22):
        ix = (x + 10) // 22
        y_off = int(4 * math.sin((x / W) * math.pi * 4))
        col = flag_colors[ix % len(flag_colors)]
        # Flag triangle pointing down
        pygame.draw.polygon(s, col,
                            [(x, 20 + y_off), (x + 18, 20 + y_off),
                             (x + 9, 40 + y_off)])
        pygame.draw.polygon(s, lerp(col, NEAR_BLACK, 0.3),
                            [(x, 20 + y_off), (x + 18, 20 + y_off),
                             (x + 9, 40 + y_off)], 1)
    # String passing through the flag tops
    for x in range(0, W, 2):
        y = 20 + int(4 * math.sin((x / W) * math.pi * 4))
        pygame.draw.circle(s, NEAR_BLACK, (x, y), 1)

    # Front draped string of lanterns just below title
    lantern_y = 222
    for i, x in enumerate(range(30, W - 20, 50)):
        y_off = int(8 * math.sin(i * 0.9))
        ly = lantern_y + y_off
        # String from above
        pygame.draw.line(s, NEAR_BLACK, (x + 9, 0), (x + 9, ly - 4), 1)
        # Lantern body
        col = (240, 80, 70) if i % 2 == 0 else (240, 160, 60)
        glow_r = pygame.Surface((38, 38), pygame.SRCALPHA)
        for rr in range(18, 0, -2):
            a = int(40 * (1 - rr / 18))
            pygame.draw.circle(glow_r, (*col, a), (19, 19), rr)
        s.blit(glow_r, (x - 10, ly - 19))
        pygame.draw.ellipse(s, col, (x, ly - 10, 18, 22))
        pygame.draw.ellipse(s, lerp(col, NEAR_BLACK, 0.45),
                            (x, ly - 10, 18, 22), 1)
        # Top cap + bottom cap
        pygame.draw.rect(s, (40, 22, 12), (x + 4, ly - 11, 10, 3))
        pygame.draw.rect(s, (40, 22, 12), (x + 4, ly + 10, 10, 3))
        # Inner glow line
        pygame.draw.line(s, (255, 240, 200), (x + 4, ly), (x + 14, ly), 1)
        # Tassel
        pygame.draw.line(s, GOLD_BRIGHT, (x + 9, ly + 13), (x + 9, ly + 20), 1)

    # Decorative monastery on the mountain silhouette
    # Replace one peak with a small monastery + flag
    mon_cx, mon_cy = 180, 365
    pygame.draw.polygon(s, (16, 24, 40),
                        [(mon_cx - 24, mon_cy + 10), (mon_cx + 24, mon_cy + 10),
                         (mon_cx + 18, mon_cy - 6), (mon_cx - 18, mon_cy - 6)])
    pygame.draw.polygon(s, (8, 14, 28),
                        [(mon_cx - 22, mon_cy - 6), (mon_cx + 22, mon_cy - 6),
                         (mon_cx, mon_cy - 22)])
    # Tiny window glow
    pygame.draw.rect(s, (255, 200, 100), (mon_cx - 3, mon_cy - 2, 6, 6))
    # Flag pole
    pygame.draw.line(s, (40, 30, 60), (mon_cx, mon_cy - 22), (mon_cx, mon_cy - 36), 1)
    pygame.draw.polygon(s, (200, 60, 60),
                        [(mon_cx, mon_cy - 36), (mon_cx + 8, mon_cy - 34), (mon_cx, mon_cy - 30)])

    # Rowan menhir on the right
    rmx, rmy = W - 50, 408
    pygame.draw.rect(s, (24, 32, 44), (rmx - 5, rmy, 10, 26))
    # Red berries
    for bx, by in [(rmx - 9, rmy - 6), (rmx - 5, rmy - 10), (rmx + 1, rmy - 8),
                   (rmx + 6, rmy - 12), (rmx + 10, rmy - 6), (rmx - 12, rmy - 14)]:
        pygame.draw.circle(s, (200, 50, 50), (bx, by), 2)

    # ── Title with extra ornamental flourishes ──
    skybit_title(s, W // 2, 140, size=70, px=3)
    skybit_subtitle(s, W // 2, 198, size=18)

    # ── Buttons — orange-bordered pills with prayer-flag pennants on the right ──
    def festival_pill(center, text, big=False):
        sz = 22 if big else 18
        h = 54 if big else 46
        rect = pill_btn(s, center, text, size=sz, w_min=240, h=h, glow=big)
        # Pennant attached to right side
        px_ = rect.right - 4
        py_ = rect.centery
        for i, c in enumerate([(220, 60, 60), (240, 200, 70), (60, 140, 200)]):
            pygame.draw.polygon(s, c,
                                [(px_ + i * 4 - 4, py_ - 6),
                                 (px_ + i * 4 + 4, py_ - 6),
                                 (px_ + i * 4, py_ + 2)])

    festival_pill((W // 2, 286), "TAP TO START", big=True)
    festival_pill((W // 2, 350), "HOW TO PLAY")
    festival_pill((W // 2, 406), "POWER-UPS")

    # ── BEST + TOP 10 — twin lanterns ──
    def lantern_panel(cx, cy, label, value, with_trophy=False):
        # Outer lantern silhouette (round)
        lw, lh = 130, 64
        rect = pygame.Rect(cx - lw // 2, cy - lh // 2, lw, lh)
        # Lantern outline (top + bottom caps + body)
        pygame.draw.rect(s, (40, 22, 12), (rect.x - 4, rect.y - 8, rect.w + 8, 6),
                         border_radius=2)
        pygame.draw.rect(s, (40, 22, 12), (rect.x - 4, rect.bottom + 2, rect.w + 8, 6),
                         border_radius=2)
        # Lantern body — red translucent glow
        glow = pygame.Surface(rect.size, pygame.SRCALPHA)
        for yy in range(rect.h):
            t = abs(yy - rect.h / 2) / (rect.h / 2)
            c = lerp((220, 80, 70), (140, 30, 30), t)
            pygame.draw.line(glow, (*c, 230), (0, yy), (rect.w, yy))
        mask = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.w, rect.h), border_radius=18)
        glow.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        pygame.draw.rect(glow, GOLD_BRIGHT, (0, 0, rect.w, rect.h), width=2, border_radius=18)
        s.blit(glow, rect.topleft)
        # Tassels
        pygame.draw.line(s, GOLD_BRIGHT, (rect.centerx - 6, rect.bottom + 8),
                         (rect.centerx - 6, rect.bottom + 18), 1)
        pygame.draw.line(s, GOLD_BRIGHT, (rect.centerx + 6, rect.bottom + 8),
                         (rect.centerx + 6, rect.bottom + 18), 1)
        # Label
        lf = font(10, True).render(label, True, GOLD_BRIGHT)
        s.blit(lf, lf.get_rect(center=(rect.centerx, rect.y + 12)))
        if with_trophy:
            draw_trophy(s, rect.centerx, rect.y + 36, 11)
        else:
            vf = font(26, True).render(value, True, GOLD_BRIGHT)
            sh = font(26, True).render(value, True, NEAR_BLACK)
            sh.set_alpha(180)
            vr = vf.get_rect(center=(rect.centerx, rect.y + 38))
            s.blit(sh, (vr.x + 1, vr.y + 2))
            s.blit(vf, vr)

    lantern_panel(94, 510, "BEST RUN", "42")
    lantern_panel(W - 94, 510, "TOP 10", "", with_trophy=True)

    save("v5_festival.png", s)


# ─────────────────────────────────────────────────────────────────────────────
# ROYAL — full UI set: 7 additional non-gameplay screens
# ─────────────────────────────────────────────────────────────────────────────

def royal_screen_pause():
    """Pause overlay — gameplay dimmed underneath, ROYAL chrome on top."""
    s = pygame.Surface((W, H))
    # Faux 'in-flight' background — same night sky, a bit darker (since
    # the overlay would normally dim the live gameplay scene).
    night_sky(s)
    # Dim layer
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 130))
    s.blit(dim, (0, 0))
    royal_frame(s)

    # Live-score medallion centred at top
    royal_medallion(s, W // 2, 110, r=40,
                    label="SCORE", value="17",
                    value_size=26, label_size=10, with_ribbon=False)

    # Title
    royal_title(s, "PAUSED", (W // 2, 220), size=58)
    royal_divider(s, 258, width=130)

    # Buttons — primary RESUME + two secondaries
    royal_pill(s, (W // 2, 320), "RESUME", big=True, glow=True)
    royal_pill(s, (W // 2, 388), "RESTART RUN")
    royal_pill(s, (W // 2, 448), "MAIN MENU")

    # Helper hint at the bottom
    hint = font(11, False).render("· TAP · P · ESC ·", True, GOLD_MUTED)
    hint.set_alpha(180)
    s.blit(hint, hint.get_rect(center=(W // 2, H - 60)))

    save("v1_royal_pause.png", s)


def royal_screen_stats():
    """Run-summary screen — big SCORE medallion + 5-row stats card."""
    s = pygame.Surface((W, H))
    night_sky(s)
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 90))
    s.blit(dim, (0, 0))
    royal_frame(s)

    # Title
    royal_title(s, "RUN  SUMMARY", (W // 2, 72), size=32)
    royal_divider(s, 100, width=160)

    # Big central SCORE medallion
    royal_medallion(s, W // 2, 180, r=58,
                    label="SCORE", value="23",
                    value_size=40, label_size=12, with_ribbon=True)

    # Stats card
    card = pygame.Rect(36, 290, W - 72, 230)
    royal_card(s, card, radius=14, alpha=225)
    rows = [
        ("TIME  ALIVE",     "1:27"),
        ("COINS",           "11"),
        ("PILLARS  CLEARED", "23"),
        ("POWER-UPS",       "3"),
        ("NEAR  MISSES",    "3"),
    ]
    row_h = (card.h - 24) // len(rows)
    for i, (label, value) in enumerate(rows):
        y = card.y + 12 + i * row_h + row_h // 2
        if i > 0:
            pygame.draw.line(s, (*GOLD_DEEP, 60),
                             (card.x + 16, y - row_h // 2),
                             (card.right - 16, y - row_h // 2), 1)
        lf = font(13, True).render(label, True, GOLD_MUTED)
        s.blit(lf, lf.get_rect(midleft=(card.x + 22, y)))
        vf = font(17, True).render(value, True, GOLD_BRIGHT)
        vsh = font(17, True).render(value, True, NEAR_BLACK)
        vsh.set_alpha(180)
        vr_rect = vf.get_rect(midright=(card.right - 22, y))
        s.blit(vsh, (vr_rect.x + 1, vr_rect.y + 2))
        s.blit(vf, vr_rect)

    # TAP TO CONTINUE prompt
    prompt = font(16, True).render("TAP  TO  CONTINUE", True, GOLD_BRIGHT)
    psh = font(16, True).render("TAP  TO  CONTINUE", True, NEAR_BLACK)
    psh.set_alpha(160)
    pr = prompt.get_rect(center=(W // 2, H - 60))
    s.blit(psh, (pr.x + 1, pr.y + 2))
    s.blit(prompt, pr)

    save("v1_royal_stats.png", s)


def royal_screen_gameover():
    """Game over — title + score medallion + NEW BEST burst + retry pill."""
    s = pygame.Surface((W, H))
    night_sky(s)
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 100))
    s.blit(dim, (0, 0))
    royal_frame(s)

    # Title
    royal_title(s, "GAME  OVER", (W // 2, 110), size=42)
    royal_divider(s, 144, width=170)

    # Filigree burst around the score medallion
    burst_cx, burst_cy = W // 2, 268
    for i in range(16):
        ang = i * (2 * math.pi / 16)
        rx = burst_cx + math.cos(ang) * 92
        ry = burst_cy + math.sin(ang) * 92
        # Small fleur shape (line + dot)
        pygame.draw.line(s, GOLD_BRIGHT, (burst_cx + math.cos(ang) * 76,
                                          burst_cy + math.sin(ang) * 76),
                         (rx, ry), 2)
        pygame.draw.circle(s, GOLD_BRIGHT, (int(rx), int(ry)), 3)
        pygame.draw.circle(s, GOLD_DEEP, (int(rx), int(ry)), 3, 1)

    # NEW BEST banner above medallion
    royal_ribbon_banner(s, W // 2, 184, "★  NEW  BEST!  ★", w=180, h=30)

    # Score medallion
    royal_medallion(s, burst_cx, burst_cy, r=64,
                    label="FINAL  SCORE", value="23",
                    value_size=44, label_size=11, with_ribbon=False)

    # Buttons
    royal_pill(s, (W // 2, 430), "TAP TO RETRY", big=True, glow=True)
    royal_pill(s, (W // 2, 500), "MAIN MENU")

    # Sub note for the non-new-best variant
    note = font(10, False).render(
        "(without 'NEW BEST', shows 'GAME OVER' + score only)",
        True, GOLD_MUTED)
    note.set_alpha(110)
    s.blit(note, note.get_rect(center=(W // 2, H - 60)))

    save("v1_royal_gameover.png", s)


def royal_screen_name_entry():
    """Top-10 qualification screen — trophy + engraved nameplate + 2 pills."""
    s = pygame.Surface((W, H))
    night_sky(s)
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    s.blit(dim, (0, 0))
    royal_frame(s)

    # Trophy with halo at top
    trophy_cy = 130
    halo = pygame.Surface((180, 180), pygame.SRCALPHA)
    for r in range(80, 0, -4):
        a = int(50 * (1 - r / 80))
        pygame.draw.circle(halo, (255, 220, 120, a), (90, 90), r)
    s.blit(halo, (W // 2 - 90, trophy_cy - 90))
    draw_trophy(s, W // 2, trophy_cy, 32)

    # Title
    royal_title(s, "TOP  10  COURIER", (W // 2, 242), size=26)
    sub = font(15, False).render("Enter  your  name", True, GOLD_MUTED)
    s.blit(sub, sub.get_rect(center=(W // 2, 280)))
    royal_divider(s, 306, width=140)

    # Engraved nameplate input field
    plate = pygame.Rect(W // 2 - 130, 332, 260, 60)
    # Outer gold rim
    pygame.draw.rect(s, GOLD_BRIGHT, plate.inflate(6, 6), border_radius=12)
    pygame.draw.rect(s, GOLD_DEEP, plate.inflate(6, 6), 1, border_radius=12)
    # Inner dark plate
    pygame.draw.rect(s, NEAR_BLACK, plate.inflate(2, 2), border_radius=10)
    pygame.draw.rect(s, PANEL_DARK, plate, border_radius=10)
    # Inner highlight at top
    pygame.draw.line(s, (255, 240, 180, 90),
                     (plate.x + 10, plate.y + 4),
                     (plate.right - 10, plate.y + 4))
    # Sample typed text
    name_text = font(28, True).render("PIP", True, GOLD_BRIGHT)
    sh = font(28, True).render("PIP", True, NEAR_BLACK)
    sh.set_alpha(180)
    nr = name_text.get_rect(center=plate.center)
    s.blit(sh, (nr.x + 1, nr.y + 2))
    s.blit(name_text, nr)
    # Tiny corner rivets
    for cx, cy in [(plate.x + 8, plate.y + 8), (plate.right - 8, plate.y + 8),
                   (plate.x + 8, plate.bottom - 8), (plate.right - 8, plate.bottom - 8)]:
        pygame.draw.circle(s, GOLD_BRIGHT, (cx, cy), 2)

    # Two pills — SUBMIT primary + SKIP secondary
    royal_pill(s, (W // 2, 452), "SUBMIT", big=True, glow=True, w=220)
    royal_pill(s, (W // 2, 514), "SKIP", w=220)

    save("v1_royal_name_entry.png", s)


def royal_screen_leaderboard():
    """TOP 10 leaderboard — title between trophies + 10 ranked rows."""
    s = pygame.Surface((W, H))
    night_sky(s)
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 110))
    s.blit(dim, (0, 0))
    royal_frame(s)

    # Header — TOP 10 flanked by trophies
    title_cy = 60
    draw_trophy(s, 56, title_cy, 18)
    draw_trophy(s, W - 56, title_cy, 18)
    royal_title(s, "TOP  10", (W // 2, title_cy), size=34)
    sub = font(11, True).render("COURIERS", True, GOLD_MUTED)
    s.blit(sub, sub.get_rect(center=(W // 2, title_cy + 28)))
    royal_divider(s, title_cy + 50, width=120)

    # 10 rows
    rows = [
        (1, "ARIA",       "98"),
        (2, "BRIK",       "91"),
        (3, "CASSI",      "87"),
        (4, "DANE",       "74"),
        (5, "EZRA",       "68"),
        (6, "FINN",       "61"),
        (7, "PIP",        "42"),   # the player
        (8, "GRETA",      "38"),
        (9, "HARLOW",     "31"),
        (10, "INDIGO",    "29"),
    ]
    rows_top = 130
    row_h = 40
    player_rank = 7
    for rank, name, score in rows:
        y = rows_top + (rank - 1) * row_h
        rect = pygame.Rect(28, y, W - 56, row_h - 6)
        royal_card(s, rect, radius=10, alpha=190)
        # Highlight the player's row
        if rank == player_rank:
            pygame.draw.rect(s, GOLD_BRIGHT, rect, 3, border_radius=10)
            # Inner soft glow
            glow = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(glow, (*GOLD_BRIGHT, 26),
                             (0, 0, rect.w, rect.h), border_radius=10)
            s.blit(glow, rect.topleft)

        # Rank badge — circle on the left
        badge_cx, badge_cy = rect.x + 24, rect.centery
        if rank == 1:
            badge_col = GOLD_BRIGHT
        elif rank == 2:
            badge_col = (200, 200, 215)  # silver
        elif rank == 3:
            badge_col = (200, 130, 60)   # bronze
        else:
            badge_col = GOLD_DEEP
        pygame.draw.circle(s, badge_col, (badge_cx, badge_cy), 14)
        pygame.draw.circle(s, NEAR_BLACK, (badge_cx, badge_cy), 14, 1)
        if rank <= 3:
            # Tick laurel
            for ang_deg in range(0, 360, 30):
                a = math.radians(ang_deg)
                x1 = badge_cx + math.cos(a) * 10
                y1 = badge_cy + math.sin(a) * 10
                x2 = badge_cx + math.cos(a) * 14
                y2 = badge_cy + math.sin(a) * 14
                pygame.draw.line(s, lerp(badge_col, NEAR_BLACK, 0.4),
                                 (x1, y1), (x2, y2), 1)
        rl = font(13, True).render(str(rank), True, NEAR_BLACK)
        s.blit(rl, rl.get_rect(center=(badge_cx, badge_cy)))

        # Name
        nf = font(15, True).render(name, True, GOLD_BRIGHT)
        s.blit(nf, nf.get_rect(midleft=(rect.x + 50, rect.centery)))
        # "YOU" tag for the player row
        if rank == player_rank:
            tag = pygame.Rect(rect.x + 50 + nf.get_width() + 8,
                              rect.centery - 8, 34, 16)
            pygame.draw.rect(s, GOLD_BRIGHT, tag, border_radius=4)
            yt = font(10, True).render("YOU", True, NEAR_BLACK)
            s.blit(yt, yt.get_rect(center=tag.center))

        # Score (right)
        sf = font(16, True).render(score, True, GOLD_BRIGHT)
        ssh = font(16, True).render(score, True, NEAR_BLACK)
        ssh.set_alpha(160)
        sr = sf.get_rect(midright=(rect.right - 20, rect.centery))
        s.blit(ssh, (sr.x + 1, sr.y + 2))
        s.blit(sf, sr)

    # TAP TO MENU
    prompt = font(13, True).render("TAP  TO  MENU", True, GOLD_BRIGHT)
    psh = font(13, True).render("TAP  TO  MENU", True, NEAR_BLACK)
    psh.set_alpha(160)
    pr = prompt.get_rect(center=(W // 2, H - 45))
    s.blit(psh, (pr.x + 1, pr.y + 2))
    s.blit(prompt, pr)

    save("v1_royal_leaderboard.png", s)


def royal_screen_powerups():
    """POWER-UPS help — 2x3 grid of medallion cards + surprise card + footer."""
    s = pygame.Surface((W, H))
    night_sky(s)
    dim = pygame.Surface((W, H), pygame.SRCALPHA)
    dim.fill((6, 1, 21, 100))
    s.blit(dim, (0, 0))
    royal_frame(s)

    # Title
    royal_title(s, "POWER-UPS", (W // 2, 60), size=32)
    royal_divider(s, 90, width=160)

    # 2x3 grid of medallion-cards
    powerups = [
        ("TRIPLE", "Coins x3",  "triple"),
        ("MAGNET", "Pull coins", "magnet"),
        ("SLOW-MO", "Time slows", "slowmo"),
        ("KFC",    "Tasty pillars", "kfc"),
        ("GHOST",  "Phase pillars", "ghost"),
        ("GROW",   "Big bird",  "grow"),
    ]
    grid_top = 116
    cell_w = (W - 80) // 2
    cell_h = 108
    for i, (name, desc, kind) in enumerate(powerups):
        col = i % 2
        row = i // 2
        x = 40 + col * (cell_w + 8)
        y = grid_top + row * (cell_h + 10)
        rect = pygame.Rect(x, y, cell_w - 8, cell_h)
        royal_card(s, rect, radius=12, alpha=220)
        # Inner medallion icon
        icon_cx = rect.x + rect.w // 2
        icon_cy = rect.y + 32
        pygame.draw.circle(s, (60, 40, 80), (icon_cx, icon_cy), 22)
        pygame.draw.circle(s, GOLD_BRIGHT, (icon_cx, icon_cy), 22, 2)
        # Per-kind procedural icon
        if kind == "triple":
            # Three small coins
            for ox in (-7, 0, 7):
                pygame.draw.circle(s, GOLD_BRIGHT, (icon_cx + ox, icon_cy), 6)
                pygame.draw.circle(s, GOLD_DEEP, (icon_cx + ox, icon_cy), 6, 1)
                df = font(8, True).render("$", True, (10, 60, 20))
                s.blit(df, df.get_rect(center=(icon_cx + ox, icon_cy)))
        elif kind == "magnet":
            # U-shaped horseshoe
            pygame.draw.arc(s, (220, 40, 40),
                            (icon_cx - 10, icon_cy - 12, 20, 22),
                            math.pi, 2 * math.pi, 5)
            pygame.draw.rect(s, (180, 180, 200), (icon_cx - 10, icon_cy - 2, 5, 6))
            pygame.draw.rect(s, (180, 180, 200), (icon_cx + 5, icon_cy - 2, 5, 6))
        elif kind == "slowmo":
            # Hourglass
            pygame.draw.polygon(s, (160, 100, 200),
                                [(icon_cx - 8, icon_cy - 10), (icon_cx + 8, icon_cy - 10),
                                 (icon_cx, icon_cy)])
            pygame.draw.polygon(s, (160, 100, 200),
                                [(icon_cx, icon_cy),
                                 (icon_cx + 8, icon_cy + 10), (icon_cx - 8, icon_cy + 10)])
            pygame.draw.line(s, (60, 40, 80), (icon_cx - 10, icon_cy - 11),
                             (icon_cx + 10, icon_cy - 11), 2)
            pygame.draw.line(s, (60, 40, 80), (icon_cx - 10, icon_cy + 11),
                             (icon_cx + 10, icon_cy + 11), 2)
        elif kind == "kfc":
            # Red KFC bucket
            pygame.draw.polygon(s, (220, 60, 60),
                                [(icon_cx - 10, icon_cy - 8), (icon_cx + 10, icon_cy - 8),
                                 (icon_cx + 7, icon_cy + 10), (icon_cx - 7, icon_cy + 10)])
            for yy in range(icon_cy - 6, icon_cy + 9, 4):
                pygame.draw.line(s, (250, 240, 230),
                                 (icon_cx - 9 + (yy - icon_cy) // 5,
                                  yy),
                                 (icon_cx + 9 - (yy - icon_cy) // 5, yy), 1)
        elif kind == "ghost":
            # Pale phantom
            pygame.draw.circle(s, (220, 220, 250), (icon_cx, icon_cy - 2), 10)
            pygame.draw.rect(s, (220, 220, 250),
                             (icon_cx - 10, icon_cy - 2, 20, 12))
            # Wavy bottom
            for k, dx in enumerate((-8, -4, 0, 4, 8)):
                yy = icon_cy + 12 + (3 if k % 2 == 0 else -1)
                pygame.draw.circle(s, (220, 220, 250), (icon_cx + dx, yy), 3)
            pygame.draw.circle(s, (40, 30, 70), (icon_cx - 4, icon_cy - 2), 2)
            pygame.draw.circle(s, (40, 30, 70), (icon_cx + 4, icon_cy - 2), 2)
        elif kind == "grow":
            # Witch hat
            pygame.draw.polygon(s, (125, 30, 45),
                                [(icon_cx, icon_cy - 12), (icon_cx + 9, icon_cy + 4),
                                 (icon_cx - 9, icon_cy + 4)])
            pygame.draw.rect(s, (245, 230, 200),
                             (icon_cx - 11, icon_cy + 4, 22, 4))
            pygame.draw.circle(s, (255, 235, 175), (icon_cx - 2, icon_cy - 2), 1)
            pygame.draw.circle(s, (255, 235, 175), (icon_cx + 3, icon_cy + 2), 1)
        # Name + description
        nf = font(13, True).render(name, True, GOLD_BRIGHT)
        s.blit(nf, nf.get_rect(center=(icon_cx, rect.y + 64)))
        df_ = font(11, False).render(desc, True, GOLD_MUTED)
        df_.set_alpha(220)
        s.blit(df_, df_.get_rect(center=(icon_cx, rect.y + 84)))

    # Surprise box card — wider, 7th item, with a ?
    sb_rect = pygame.Rect(40, grid_top + 3 * (cell_h + 10) + 8, W - 80, 64)
    royal_card(s, sb_rect, radius=12, alpha=225)
    # Left mini medallion
    pygame.draw.circle(s, (60, 40, 80),
                       (sb_rect.x + 36, sb_rect.centery), 20)
    pygame.draw.circle(s, GOLD_BRIGHT,
                       (sb_rect.x + 36, sb_rect.centery), 20, 2)
    qf = font(22, True).render("?", True, GOLD_BRIGHT)
    s.blit(qf, qf.get_rect(center=(sb_rect.x + 36, sb_rect.centery)))
    # Right text
    nf = font(15, True).render("SURPRISE  BOX", True, GOLD_BRIGHT)
    s.blit(nf, (sb_rect.x + 72, sb_rect.y + 12))
    df = font(11, False).render("Re-rolls into any power-up", True, GOLD_MUTED)
    s.blit(df, (sb_rect.x + 72, sb_rect.y + 36))

    # Footer banner
    royal_ribbon_banner(s, W // 2, H - 56, "EFFECTS  LAST  8  SECONDS",
                        w=240, h=26)

    save("v1_royal_powerups.png", s)


def royal_screen_intro():
    """HOW TO PLAY title card — 3 numbered instruction cards + start pill."""
    s = pygame.Surface((W, H))
    night_sky(s)
    royal_frame(s)

    # Title
    royal_title(s, "HOW  TO  PLAY", (W // 2, 90), size=32)
    royal_divider(s, 122, width=160)

    # 3 numbered instruction cards
    instructions = [
        ("01", "TAP · CLICK · SPACE — FLAP"),
        ("02", "THREAD THE PILLARS — CLEAR THE GAP"),
        ("03", "GRAB COINS & POWER-UPS — STACK A STREAK"),
    ]
    card_top = 174
    card_h = 76
    for i, (num, text) in enumerate(instructions):
        y = card_top + i * (card_h + 12)
        rect = pygame.Rect(28, y, W - 56, card_h)
        royal_card(s, rect, radius=12, alpha=215)
        # Big numeral on the left in a small medallion
        n_cx = rect.x + 32
        n_cy = rect.centery
        pygame.draw.circle(s, (60, 40, 80), (n_cx, n_cy), 22)
        pygame.draw.circle(s, GOLD_BRIGHT, (n_cx, n_cy), 22, 2)
        nf = font(22, True).render(num, True, GOLD_BRIGHT)
        nsh = font(22, True).render(num, True, NEAR_BLACK)
        nsh.set_alpha(180)
        nr = nf.get_rect(center=(n_cx, n_cy))
        s.blit(nsh, (nr.x + 1, nr.y + 2))
        s.blit(nf, nr)
        # Instruction text — split into two lines if too long
        text_x = rect.x + 64
        text_y = rect.centery
        # Try single line first
        tline = font(13, True).render(text, True, GOLD_BRIGHT)
        if tline.get_width() <= rect.w - 76:
            s.blit(tline, tline.get_rect(midleft=(text_x, text_y)))
        else:
            # Split at em-dash / first dash
            parts = text.split(" — ", 1)
            if len(parts) == 2:
                l1 = font(13, True).render(parts[0] + " —", True, GOLD_BRIGHT)
                l2 = font(13, True).render(parts[1], True, GOLD_MUTED)
                s.blit(l1, l1.get_rect(midleft=(text_x, text_y - 10)))
                s.blit(l2, l2.get_rect(midleft=(text_x, text_y + 10)))
            else:
                s.blit(tline, tline.get_rect(midleft=(text_x, text_y)))

    # Begin pill
    royal_pill(s, (W // 2, H - 80), "TAP TO BEGIN", big=True, glow=True)

    save("v1_royal_intro.png", s)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating Skybit v4 menu upgrade mockups...")
    v1_royal()
    v2_aviator()
    v3_parcel()
    v4_starlight()
    v5_festival()
    print("Generating ROYAL full-UI screen mockups...")
    royal_screen_pause()
    royal_screen_stats()
    royal_screen_gameover()
    royal_screen_name_entry()
    royal_screen_leaderboard()
    royal_screen_powerups()
    royal_screen_intro()
    print("Done.")
