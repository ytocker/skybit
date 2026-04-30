"""HUD: score, hi-score, coin count, power-up timer bar, pause button."""
import math
import os
import random
import pygame

from game.config import W, H, TRIPLE_DURATION, MAGNET_DURATION, SLOWMO_DURATION, KFC_DURATION, GHOST_DURATION, GROW_DURATION
from game.draw import (
    rounded_rect, rounded_rect_grad, lerp_color,
    UI_SCORE, UI_GOLD, UI_ORANGE, UI_SHADOW, UI_CREAM, UI_RED,
    COIN_GOLD, COIN_DARK,
    WHITE, NEAR_BLACK,
)
from game import parrot
from game.dollar_coin_glyphs import draw_coin_font_bold as _draw_dollar_coin_hud

_grow_parrot_hud: "pygame.Surface | None" = None

def _get_grow_parrot_hud() -> "pygame.Surface":
    global _grow_parrot_hud
    if _grow_parrot_hud is None:
        src = parrot.FRAMES[1]
        target_w = 16
        ratio = target_w / src.get_width()
        target_h = int(src.get_height() * ratio)
        _grow_parrot_hud = pygame.transform.smoothscale(src, (target_w, target_h))
    return _grow_parrot_hud

# ── Theme palette matching the HTML welcome screen ───────────────────────────
_GOLD_BRIGHT   = (240, 192,  64)   # #f0c040
_GOLD_MUTED    = (216, 184,  85)   # #d8b855
_RED_OUTLINE   = (168,  32,  16)   # #a82010
_ORANGE_BORDER = (232, 104,  40)   # #e86828
_BTN_TOP       = (200,  64,  24)   # #c84018
_BTN_BOT       = (126,  28,   2)   # #7e1c02
_PANEL_DARK    = ( 12,   8,  38)   # deep purple panel
_NIGHT_DEEP    = (  6,   1,  21)   # #060115


_fonts: dict = {}


# ── Theme drawing helpers ────────────────────────────────────────────────────

def _outlined_text(surf, txt, center, size, fill=_GOLD_BRIGHT,
                   outline=_RED_OUTLINE, px=3, shadow_offset=(3, 5)):
    """Gold text with red pixel outline — matches the welcome screen title."""
    f = _font(size, True)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    sh  = f.render(txt, True, NEAR_BLACK)
    r = img.get_rect(center=center)
    offsets = [(-px, 0), (px, 0), (0, -px), (0, px),
               (-px, -px), (px, -px), (-px, px), (px, px)]
    for ox, oy in offsets:
        surf.blit(out, (r.x + ox, r.y + oy))
    sh.set_alpha(170)
    surf.blit(sh, (r.x + shadow_offset[0], r.y + shadow_offset[1]))
    surf.blit(img, r.topleft)
    return r


def _pill_btn(surf, center, text, size=20, alpha=255, wide=False, min_width=None):
    """Styled pill button with red gradient fill + orange border (welcome theme).
    Returns the pygame.Rect of the rendered button so callers can hit-test
    clicks against it. `min_width` lets paired buttons (SUBMIT + SKIP) share
    one width regardless of label length."""
    f = _font(size, True)
    img = f.render(text, True, WHITE)
    pad_x = 64 if wide else 44
    pw = img.get_width() + pad_x
    if min_width is not None:
        pw = max(pw, min_width)
    ph = img.get_height() + 22
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    # Gradient fill
    for y in range(ph):
        t = y / max(1, ph - 1)
        c = lerp_color(_BTN_TOP, _BTN_BOT, t)
        pygame.draw.line(pill, c, (0, y), (pw - 1, y))
    # Rounded border mask
    mask = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, pw, ph),
                     border_radius=ph // 2)
    pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Orange border
    border = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(border, (*_ORANGE_BORDER, 255), (0, 0, pw, ph),
                     width=2, border_radius=ph // 2)
    pill.blit(border, (0, 0))
    # Inner highlight
    pygame.draw.line(pill, (255, 255, 255, 40), (ph // 2, 2), (pw - ph // 2, 2))
    ir = img.get_rect(center=(pw // 2, ph // 2))
    pill.blit(img, ir.topleft)
    pill.set_alpha(alpha)
    cx, cy = center
    top_left = (cx - pw // 2, cy - ph // 2)
    surf.blit(pill, top_left)
    return pygame.Rect(top_left[0], top_left[1], pw, ph)


def _dark_panel(surf, rect, radius=16, alpha=210):
    """Deep-purple frosted panel with faint orange top-edge accent."""
    rounded_rect(surf, rect, radius, _PANEL_DARK, alpha)
    # Thin orange accent line at the top
    accent = pygame.Surface((rect.width - radius * 2, 2), pygame.SRCALPHA)
    accent.fill((*_ORANGE_BORDER, 80))
    surf.blit(accent, (rect.x + radius, rect.y + 3))


def _draw_overlay_stars(surf, stars, t):
    """Twinkle star field. `stars` = list of (x,y,r,phase) from HUD.__init__."""
    for x, y, r, phase in stars:
        a = int(30 + 200 * (0.5 + 0.5 * math.sin(t * 1.4 + phase)))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, a), (r + 1, r + 1), r)
        surf.blit(s, (x - r - 1, y - r - 1))


def _draw_trophy(surf, cx, cy, size):
    """Gold procedural trophy icon. `size` is approximate half-height.
    Drawn fully symmetric about a vertical axis through (cx, cy):
      * Cup widths use the same ±half-width on left & right
      * Handles drawn on a temp surface and mirrored via transform.flip
      * Stem / base / foot use odd widths so they centre exactly
    """
    s = size
    # Surface big enough for cup (full width 2s) + handle ears + foot overflow.
    pad   = 6
    g_w   = (s + pad) * 2 + 1   # odd → exact centre column
    g_h   = s * 3 + 4
    g     = pygame.Surface((g_w, g_h), pygame.SRCALPHA)
    gx    = g_w // 2
    gy    = s + 2

    GOLD  = (240, 192,  64, 255)
    DARK  = (140,  90,   8, 255)
    WHITE = (255, 248, 200, 180)

    # ── Cup body — symmetric trapezoid (wider at top) ──────────────────────
    half_top = s
    half_bot = s - 3
    top_y = gy - s + 2
    bot_y = gy + 2
    cup_pts = [
        (gx - half_top, top_y),
        (gx + half_top, top_y),
        (gx + half_bot, bot_y),
        (gx - half_bot, bot_y),
    ]
    # Symmetric drop shadow — grow the silhouette down + on both sides
    cup_shadow = [
        (gx - half_top - 1, top_y + 1),
        (gx + half_top + 1, top_y + 1),
        (gx + half_bot + 1, bot_y + 1),
        (gx - half_bot - 1, bot_y + 1),
    ]
    pygame.draw.polygon(g, DARK, cup_shadow)
    pygame.draw.polygon(g, GOLD, cup_pts)
    # pygame.draw.polygon excludes the right/bottom boundary by convention,
    # which leaves a one-pixel gap on the right slope. Draw the slope as a
    # line explicitly so left/right edges are pixel-symmetric.
    pygame.draw.line(g, GOLD,
                     (gx + half_top, top_y),
                     (gx + half_bot, bot_y), 1)
    pygame.draw.line(g, WHITE,
                     (gx - half_top + 2, top_y + 1),
                     (gx + half_top - 2, top_y + 1), 1)

    # ── Handles — draw the left ear once, then horizontal-flip for right ──
    h_w  = 5
    h_h  = max(4, s - 2)
    h_y  = top_y + 2
    ear  = pygame.Surface((h_w, h_h), pygame.SRCALPHA)
    # Left half of an ellipse — gives a nice C-shape opening right
    pygame.draw.arc(ear, GOLD, (0, 0, h_w * 2 - 1, h_h),
                    math.pi * 0.5, math.pi * 1.5, 2)
    # Mirror about the cup's vertical centre. Left ear ends at gx - half_top;
    # right ear starts at gx + half_top + 1 so the two ears occupy mirrored
    # column ranges.
    left_ear_x  = gx - half_top - h_w + 1
    right_ear_x = gx + half_top
    g.blit(ear, (left_ear_x, h_y))
    g.blit(pygame.transform.flip(ear, True, False),
           (right_ear_x, h_y))

    # ── Stem — odd width, exact centre ────────────────────────────────────
    stem_w  = 3
    stem_h  = s // 2
    stem_x  = gx - stem_w // 2
    pygame.draw.rect(g, DARK,  (stem_x - 1, bot_y + 1, stem_w + 2, stem_h + 1))
    pygame.draw.rect(g, GOLD,  (stem_x,     bot_y,     stem_w,     stem_h))

    # ── Base + foot — both odd-width so they centre exactly ───────────────
    base_w = (s - 1) * 2 + 1
    base_x = gx - base_w // 2
    base_y = bot_y + stem_h
    pygame.draw.rect(g, DARK,  (base_x - 1, base_y + 1, base_w + 2, 4))
    pygame.draw.rect(g, GOLD,  (base_x,     base_y,     base_w,     3))

    foot_w = base_w + 2
    foot_x = gx - foot_w // 2
    pygame.draw.rect(g, DARK,  (foot_x - 1, base_y + 5, foot_w + 2, 3))
    pygame.draw.rect(g, GOLD,  (foot_x,     base_y + 4, foot_w,     2))

    surf.blit(g, (cx - gx, cy - gy))


def _draw_mountain_silhouette(surf, alpha=200):
    """Mountain silhouettes at the bottom — matches the welcome-screen SVG."""
    mtn = pygame.Surface((W, H), pygame.SRCALPHA)
    far = [(0,H),(0,490),(60,420),(120,450),(200,375),(280,430),
           (360,360),(W,400),(W,H)]
    near= [(0,H),(0,530),(80,505),(160,520),(240,490),(320,510),(W,495),(W,H)]
    pygame.draw.polygon(mtn, (14, 26, 12, alpha), far)
    pygame.draw.polygon(mtn, (10, 18,  8, alpha), near)
    surf.blit(mtn, (0, 0))


# Vendored Liberation Sans (metric-compatible Arial replacement) so the
# browser/pygbag build doesn't depend on a system font that isn't there.
_FONT_DIR = os.path.join(os.path.dirname(__file__), "assets")
_FONT_BOLD = os.path.join(_FONT_DIR, "LiberationSans-Bold.ttf")
_FONT_REG  = os.path.join(_FONT_DIR, "LiberationSans-Regular.ttf")


def _font(size, bold=True):
    k = (size, bold)
    f = _fonts.get(k)
    if f is None:
        path = _FONT_BOLD if bold else _FONT_REG
        f = pygame.font.Font(path, size)
        _fonts[k] = f
    return f


def _text(surf, txt, center, size=36, color=WHITE, shadow=True):
    f = _font(size, True)
    img = f.render(txt, True, color)
    r = img.get_rect(center=center)
    if shadow:
        sh = f.render(txt, True, NEAR_BLACK)
        sh.set_alpha(170)
        surf.blit(sh, (r.x + 2, r.y + 3))
    surf.blit(img, r.topleft)
    return r


def _coin_icon(surf, cx, cy, r=10):
    # Match in-world Coin.draw: dark rim + gold body + embossed parrot.
    # No halo, no pale highlight.
    pygame.draw.circle(surf, COIN_DARK, (cx, cy), r + 1)
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy), r)
    emboss = (140, 85, 0)
    pygame.draw.ellipse(surf, emboss, (cx - 2, cy - 1, 7, 5))
    pygame.draw.circle(surf, emboss, (cx - 1, cy - 3), 3)
    pygame.draw.polygon(surf, emboss,
                        [(cx - 3, cy - 3), (cx - 6, cy - 2), (cx - 3, cy - 1)])
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy - 4), 1)


def _draw_buff_icon(surf, rect, kind):
    """Tiny 20x20-ish icon for an active buff. Matches in-world sprites."""
    cx, cy = rect.center
    if kind == "grow":
        # Red mushroom cap + stem (Mario super-mushroom feel for the GROW power-up)
        pygame.draw.rect(surf, (245, 225, 195), (cx - 3, cy + 1, 6, 7), border_radius=1)
        pygame.draw.ellipse(surf, (130, 10, 20),
                            (cx - 9, cy - 6, 18, 10))
        pygame.draw.ellipse(surf, (220, 30, 30),
                            (cx - 8, cy - 5, 16, 8))
        pygame.draw.circle(surf, WHITE, (cx - 3, cy - 3), 1)
        pygame.draw.circle(surf, WHITE, (cx + 3, cy - 2), 1)
    elif kind == "magnet":
        # Polished horseshoe magnet — rendered at 2× on a scratch surface
        # so the arc smooths under `smoothscale`. Has a dark silhouette
        # outline, a vertical red gradient flesh, and steel-tipped poles
        # at the bottom with tiny field-line sparks above the prongs.
        OUTLINE = ( 38,   8,  16)
        RED_TOP = (245,  78,  64)   # sunlit upper arc
        RED_MID = (215,  38,  46)
        RED_BOT = (150,  16,  26)   # deep base of the legs
        STEEL_LT = (220, 226, 240)
        STEEL_DK = (108, 116, 138)
        FIELD    = (255, 230, 130)  # warm spark colour for the field hint

        SX = SY = 40                # 2× scratch
        m = pygame.Surface((SX, SY), pygame.SRCALPHA)

        # Outer silhouette in OUTLINE: top arc (filled circle) + leg slab.
        pygame.draw.circle(m, OUTLINE, (20, 18), 14)
        pygame.draw.rect(m, OUTLINE, (6, 18, 28, 18))

        # Red flesh — vertical gradient column-by-column under a circle mask.
        red_layer = pygame.Surface((SX, SY), pygame.SRCALPHA)
        for y in range(40):
            if y <= 18:
                col = lerp_color(RED_TOP, RED_MID, max(0.0, y / 18.0))
            else:
                col = lerp_color(RED_MID, RED_BOT, (y - 18) / 18.0)
            pygame.draw.line(red_layer, col, (0, y), (SX - 1, y))
        # Mask the gradient to the inset silhouette.
        mask = pygame.Surface((SX, SY), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (20, 18), 12)
        pygame.draw.rect(mask, (255, 255, 255, 255), (8, 18, 24, 16))
        red_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        m.blit(red_layer, (0, 0))

        # Carve the U cavity through OUTLINE + RED in one pass (alpha=0
        # writes "fully transparent" on SRCALPHA surfaces).
        pygame.draw.circle(m, (0, 0, 0, 0), (20, 18), 8)
        pygame.draw.rect(m, (0, 0, 0, 0), (12, 18, 16, 18))

        # Steel pole tips at the bottom of each leg.
        for lx in (6, 22):
            pygame.draw.rect(m, OUTLINE,  (lx, 30, 12, 6))
            pygame.draw.rect(m, STEEL_DK, (lx + 1, 31, 10, 4))
            pygame.draw.rect(m, STEEL_LT, (lx + 1, 31, 10, 1))

        # Sun glint along the upper-outer arc and a tiny highlight on the
        # left pole face — sells the metallic feel after smoothscale.
        pygame.draw.line(m, RED_TOP, (10, 12), (15,  6), 2)
        pygame.draw.line(m, STEEL_LT, (8, 32), (8, 35), 1)

        # Two faint magnetic-pull sparks above the poles.
        pygame.draw.line(m, FIELD, ( 8, 36), ( 6, 38), 1)
        pygame.draw.line(m, FIELD, (32, 36), (34, 38), 1)

        icon = pygame.transform.smoothscale(m, (rect.w, rect.h))
        surf.blit(icon, rect.topleft)
    elif kind == "slowmo":
        # Tiny clock face on SRCALPHA scratch
        r = 7
        D = r * 2 + 2
        mc = pygame.Surface((D, D), pygame.SRCALPHA)
        cc = (D // 2, D // 2)
        pygame.draw.circle(mc, (130, 65, 190, 255), cc, r)       # bezel
        pygame.draw.circle(mc, (42, 10, 70, 255), cc, r - 1)     # face
        # 4 major ticks
        for i in range(4):
            ang = math.pi / 2 * i - math.pi / 2
            x1 = cc[0] + math.cos(ang) * (r - 1)
            y1 = cc[1] + math.sin(ang) * (r - 1)
            x2 = cc[0] + math.cos(ang) * (r - 3)
            y2 = cc[1] + math.sin(ang) * (r - 3)
            pygame.draw.line(mc, (220, 190, 255, 230), (int(x1), int(y1)), (int(x2), int(y2)), 1)
        # Hour hand ~10 o'clock
        ha = math.pi * 2 * 10 / 12 - math.pi / 2
        pygame.draw.line(mc, (250, 225, 255, 255), cc,
                         (int(cc[0] + math.cos(ha) * 3), int(cc[1] + math.sin(ha) * 3)), 2)
        # Minute hand ~12 o'clock
        ma = -math.pi / 2
        pygame.draw.line(mc, (200, 155, 255, 255), cc,
                         (int(cc[0] + math.cos(ma) * 5), int(cc[1] + math.sin(ma) * 5)), 1)
        # Center dot
        pygame.draw.circle(mc, (255, 240, 255, 255), cc, 1)
        surf.blit(mc, (cx - D // 2, cy - D // 2))
    elif kind == "kfc":
        # Tiny red KFC bucket
        bw = 6
        bh = 7
        pts = [(cx - bw, cy - bh), (cx + bw, cy - bh),
               (cx + bw - 2, cy + bh), (cx - bw + 2, cy + bh)]
        pygame.draw.polygon(surf, (200, 18, 18), pts)
        pygame.draw.line(surf, WHITE,
                         (cx - bw + 1, cy), (cx + bw - 1, cy), 1)
        pygame.draw.rect(surf, (220, 35, 22),
                         (cx - bw - 1, cy - bh - 2, (bw + 1) * 2, 3),
                         border_radius=1)
    elif kind == "ghost":
        # Mini classic ghost: rounded head + straight sides + 3-bump skirt
        GW, GH = 20, 24
        gcx, gcy, hr = 10, 8, 8
        body_y2 = 16
        DARK_G = (32,  52, 120, 255)
        BODY_G = (205, 228, 255, 235)
        skirt   = [(1, body_y2), (4, GH-2), (8, body_y2+3),
                   (gcx, GH-2), (12, body_y2+3), (16, GH-2), (GW-1, body_y2)]
        skirt_o = [(0, body_y2), (4, GH-1), (7, body_y2+3),
                   (gcx, GH-1), (13, body_y2+3), (16, GH-1), (GW, body_y2)]
        mg = pygame.Surface((GW, GH), pygame.SRCALPHA)
        pygame.draw.circle(mg, DARK_G, (gcx, gcy), hr + 1)
        pygame.draw.rect(mg, DARK_G, (0, gcy, GW, body_y2 - gcy + 1))
        pygame.draw.polygon(mg, DARK_G, skirt_o)
        pygame.draw.circle(mg, BODY_G, (gcx, gcy), hr)
        pygame.draw.rect(mg, BODY_G, (1, gcy, GW - 2, body_y2 - gcy))
        pygame.draw.polygon(mg, BODY_G, skirt)
        for ex in (gcx - 3, gcx + 3):
            pygame.draw.circle(mg, (252, 254, 255, 255), (ex, gcy - 1), 3)
            pygame.draw.circle(mg, (50, 110, 220, 255),  (ex + 1, gcy), 2)
        surf.blit(mg, (cx - gcx, cy - gcy - 2))
    elif kind == "triple":
        # Gold coin with $ glyph — matches the in-world triple power-up icon.
        from game.config import POWERUP_R
        native = POWERUP_R * 2
        icon = pygame.Surface((native, native), pygame.SRCALPHA)
        _draw_dollar_coin_hud(icon, native // 2, native // 2, pulse=0.0)
        scaled = pygame.transform.smoothscale(icon, (20, 20))
        surf.blit(scaled, (cx - 10, cy - 10))


class PauseButton:
    def __init__(self):
        self.rect = pygame.Rect(W - 56, 12, 44, 44)
        self.hover = False

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surf, paused=False):
        rounded_rect(surf, self.rect, 10, _PANEL_DARK, 200)
        # Orange border ring
        border = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(border, (*_ORANGE_BORDER, 120), (0, 0, self.rect.width,
                         self.rect.height), border_radius=10, width=1)
        surf.blit(border, self.rect.topleft)
        cx, cy = self.rect.center
        if paused:
            pygame.draw.polygon(surf, _GOLD_BRIGHT, [
                (cx - 7, cy - 10),
                (cx - 7, cy + 10),
                (cx + 9, cy),
            ])
        else:
            pygame.draw.rect(surf, _GOLD_BRIGHT, (cx - 8, cy - 9, 5, 18), border_radius=2)
            pygame.draw.rect(surf, _GOLD_BRIGHT, (cx + 3, cy - 9, 5, 18), border_radius=2)


class HUD:
    def __init__(self):
        self.pause_btn = PauseButton()
        self.title_t = 0.0
        # Name-entry button rects — populated each frame by draw_name_entry,
        # read by scenes.py click-handling. Pre-init to empty rects so the
        # first click before any draw is harmless.
        self.name_submit_rect = pygame.Rect(0, 0, 0, 0)
        self.name_skip_rect   = pygame.Rect(0, 0, 0, 0)
        # Precompute star positions for overlay screens (seeded for consistency)
        rng = random.Random(42)
        self._stars = [
            (rng.randint(8, W - 8), rng.randint(8, H - 180),
             rng.choice((1, 1, 1, 2)), rng.uniform(0, 6.28))
            for _ in range(38)
        ]

    def draw_pause_overlay(self, surf):
        self.title_t += 1 / 60
        # Deep blue-purple dim
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 2, 28, 165))
        surf.blit(dim, (0, 0))

        cy = H // 2 - 20
        # Frosted panel behind the pause text
        panel = pygame.Rect(W // 2 - 120, cy - 48, 240, 100)
        _dark_panel(surf, panel, radius=20, alpha=200)

        pulse = 1.0 + math.sin(self.title_t * 2.6) * 0.04
        _outlined_text(surf, "PAUSED", (W // 2, cy),
                        size=int(52 * pulse), px=3)

        alpha = int(150 + math.sin(self.title_t * 3.6) * 90)
        _pill_btn(surf, (W // 2, cy + 72), "TAP · P · ESC", size=16, alpha=alpha)

    def draw_menu(self, surf, dt, best: int):
        self.title_t += dt
        # Night-sky tint overlay
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 1, 21, 110))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)

        # Floating title — sits above the gameplay-opener post-house +
        # Pip composition (cottage top is at y≈208) so the text never
        # crosses the parrot.
        pulse = 1.0 + math.sin(self.title_t * 2.4) * 0.04
        float_y = int(7 * math.sin(self.title_t * 1.8))
        _outlined_text(surf, "SKYBIT", (W // 2, 126 + float_y),
                        size=int(72 * pulse), px=3)

        # Subtitle — same gold-on-red outline as SKYBIT, just smaller and
        # with a tighter pixel outline so it reads as a partner line.
        _outlined_text(surf, "POCKET SKY FLYER", (W // 2, 184),
                        size=22, px=2, shadow_offset=(2, 3))

        # Divider
        pygame.draw.line(surf, (*_ORANGE_BORDER, 120),
                         (W // 2 - 70, 208), (W // 2 + 70, 208), 1)

        # Tap-to-play pill (pulsing)
        btn_alpha = int(180 + math.sin(self.title_t * 3.6) * 70)
        _pill_btn(surf, (W // 2, H - 158), "TAP  ·  SPACE  ·  CLICK",
                  size=18, alpha=btn_alpha)

        # Best score panel
        hi_rect = pygame.Rect(W // 2 - 72, H - 110, 144, 48)
        _dark_panel(surf, hi_rect, radius=14, alpha=190)
        lf = _font(12, False)
        lbl = lf.render("B E S T", True, _GOLD_MUTED)
        lbl.set_alpha(180)
        surf.blit(lbl, lbl.get_rect(center=(W // 2, H - 98)))
        vf = _font(22, True)
        val = vf.render(str(best), True, _GOLD_BRIGHT)
        surf.blit(val, val.get_rect(center=(W // 2, H - 78)))

        _draw_mountain_silhouette(surf, alpha=180)

    def draw_play(self, surf, world, best: int, paused: bool = False):
        # ── Score: centered, styled dark pill backdrop
        score_txt = str(world.score)
        cf = _font(48, True)
        img = cf.render(score_txt, True, WHITE)
        out = cf.render(score_txt, True, _GOLD_BRIGHT)
        sh  = cf.render(score_txt, True, NEAR_BLACK)
        r = img.get_rect(center=(W // 2, 72))
        back_w = max(r.width + 52, 80)
        back_h = r.height + 16
        back = pygame.Surface((back_w, back_h), pygame.SRCALPHA)
        pygame.draw.rect(back, (*_PANEL_DARK, 140), (0, 0, back_w, back_h),
                         border_radius=back_h // 2)
        pygame.draw.rect(back, (*_ORANGE_BORDER, 60), (0, 0, back_w, back_h),
                         border_radius=back_h // 2, width=1)
        surf.blit(back, (W // 2 - back_w // 2, r.y - 8))
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            surf.blit(out, (r.x + ox, r.y + oy))
        sh.set_alpha(160)
        surf.blit(sh, (r.x + 2, r.y + 3))
        surf.blit(img, r.topleft)

        # ── Pill alpha fades when bird is near top
        bird_y = world.bird.y
        if bird_y >= 80:
            ui_alpha = 255
        elif bird_y <= 20:
            ui_alpha = 40
        else:
            ui_alpha = int(40 + 215 * (bird_y - 20) / 60)

        # BEST pill — dark panel with orange border
        hi_pill = pygame.Surface((96, 36), pygame.SRCALPHA)
        pygame.draw.rect(hi_pill, (*_PANEL_DARK, 210), (0, 0, 96, 36), border_radius=10)
        pygame.draw.rect(hi_pill, (*_ORANGE_BORDER, 80), (0, 0, 96, 36),
                         border_radius=10, width=1)
        # Trophy icon — same procedural gold trophy used elsewhere in the
        # leaderboard / theme; replaces the previous star-stub emblem.
        _draw_trophy(hi_pill, 18, 18, 8)
        bf = _font(11, False)
        bl = bf.render("BEST", True, _GOLD_MUTED)
        hi_pill.blit(bl, bl.get_rect(center=(60, 11)))
        vf = _font(15, True)
        vl = vf.render(str(best), True, _GOLD_BRIGHT)
        hi_pill.blit(vl, vl.get_rect(center=(60, 25)))
        hi_pill.set_alpha(ui_alpha)
        surf.blit(hi_pill, (10, 14))

        # Coin pill
        cc_pill = pygame.Surface((90, 36), pygame.SRCALPHA)
        pygame.draw.rect(cc_pill, (*_PANEL_DARK, 190), (0, 0, 90, 36), border_radius=10)
        pygame.draw.rect(cc_pill, (*_ORANGE_BORDER, 70), (0, 0, 90, 36),
                         border_radius=10, width=1)
        _coin_icon(cc_pill, 18, 18, 10)
        _text(cc_pill, f"x{world.coin_count}", (56, 18),
              size=18, color=_GOLD_BRIGHT, shadow=False)
        cc_pill.set_alpha(ui_alpha)
        surf.blit(cc_pill, (W - 158, 14))

        # Pause button
        self.pause_btn.draw(surf, paused=paused)

        # "Get ready" prompt while the pre-start freeze is active.
        if world.ready_t > 0:
            pulse = 0.5 + 0.5 * math.sin(self.title_t * 5)
            alpha = int(180 + 60 * pulse)
            font_big = _font(22, True)
            label = font_big.render("TAP TO FLY", True, WHITE)
            label.set_alpha(alpha)
            lr = label.get_rect(center=(W // 2, 340))
            # dark plate behind for legibility
            plate = pygame.Surface((lr.width + 36, lr.height + 18),
                                   pygame.SRCALPHA)
            pygame.draw.ellipse(plate, (0, 0, 20, 140), plate.get_rect())
            surf.blit(plate, (W // 2 - plate.get_width() // 2,
                              lr.y - 9))
            surf.blit(label, lr.topleft)

        # Active-buff timer bars — every active power-up gets its own
        # progress bar at the top of the screen with the buff's logo on the
        # left. Stacks vertically when multiple are active. Each bar uses
        # the same gold → orange → red gradient as time depletes, and the
        # whole row pulses with a red ring in the final 25 % of duration.
        active = []
        if world.triple_timer > 0:
            active.append(("triple", world.triple_timer, TRIPLE_DURATION))
        if world.magnet_timer > 0:
            active.append(("magnet", world.magnet_timer, MAGNET_DURATION))
        if world.slowmo_timer > 0:
            active.append(("slowmo", world.slowmo_timer, SLOWMO_DURATION))
        if world.kfc_timer > 0:
            active.append(("kfc", world.kfc_timer, KFC_DURATION))
        if world.ghost_timer > 0:
            active.append(("ghost", world.ghost_timer, GHOST_DURATION))
        if world.grow_timer > 0:
            active.append(("grow", world.grow_timer, GROW_DURATION))

        if active:
            icon_size = 24
            bar_w     = 132
            bar_h     = 12
            row_gap   = 6
            row_pitch = max(icon_size, bar_h) + row_gap
            row_w     = icon_size + 6 + bar_w
            base_x    = (W - row_w) // 2
            top_y     = 128

            for i, (kind, remain, total) in enumerate(active):
                y = top_y + i * row_pitch
                # Icon plate on the left
                icon_rect = pygame.Rect(base_x, y - (icon_size - bar_h) // 2,
                                        icon_size, icon_size)
                rounded_rect(surf, icon_rect, 6, (15, 25, 60), 200)
                _draw_buff_icon(surf, icon_rect.inflate(-4, -4), kind)

                # Bar to the right of the icon
                bx = icon_rect.right + 6
                by = y
                frac = max(0.0, min(1.0, remain / total))
                track = pygame.Rect(bx - 2, by, bar_w + 4, bar_h)
                rounded_rect(surf, track, 6, (20, 25, 50), 200)
                # Gold → orange → red as remaining time decreases
                if frac > 0.5:
                    fill_lo, fill_hi = UI_ORANGE, UI_GOLD
                elif frac > 0.25:
                    t = (frac - 0.25) / 0.25
                    fill_lo = lerp_color(UI_RED, UI_ORANGE, t)
                    fill_hi = lerp_color(UI_ORANGE, UI_GOLD, t)
                else:
                    fill_lo = (180, 20, 20)
                    fill_hi = UI_RED
                fill = pygame.Rect(bx, by + 2, int(bar_w * frac), bar_h - 4)
                if fill.width > 0:
                    rounded_rect_grad(surf, fill, 4, fill_hi, fill_lo)
                # Time-remaining text inside the bar
                _text(surf, f"{remain:.1f}s",
                      (bx + bar_w // 2, by + bar_h // 2),
                      size=11, color=UI_CREAM, shadow=True)
                # Low-time pulse ring around the row when critical
                if frac < 0.25:
                    pulse = 0.5 + 0.5 * math.sin(self.title_t * 14)
                    ring_a = int(140 * pulse)
                    ring = pygame.Surface((bar_w + 10, bar_h + 6), pygame.SRCALPHA)
                    pygame.draw.rect(ring, (*UI_RED, ring_a), ring.get_rect(),
                                     border_radius=8, width=2)
                    surf.blit(ring, (bx - 5, by - 3))

        # Float texts
        for ft in world.float_texts:
            ft.draw(surf)

    def draw_stats(self, surf, world, dt, elapsed):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 1, 21, 190))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)
        # Mountain silhouette belongs to the backdrop — drawn here so the
        # score / stats cards layer on top instead of being clipped.
        _draw_mountain_silhouette(surf, alpha=160)

        # Slide-in animation from below
        slide_t = max(0.0, min(1.0, elapsed / 0.35))
        e = slide_t * slide_t * (3 - 2 * slide_t)
        card_y = int(58 + (1.0 - e) * 60)

        # Header — gold with red outline (matches the TOP 10 / WELCOME styling)
        _outlined_text(surf, "RUN SUMMARY", (W // 2, card_y + 4),
                        size=24, px=2, shadow_offset=(2, 3))

        # Score block — dark panel with the score number outlined like TOP 10
        score_panel = pygame.Rect(W // 2 - 80, card_y + 28, 160, 68)
        _dark_panel(surf, score_panel, radius=16, alpha=200)
        _outlined_text(surf, "S C O R E", (W // 2, card_y + 44),
                       size=12, px=1, shadow_offset=(1, 2))
        _outlined_text(surf, str(world.score), (W // 2, card_y + 76),
                       size=34, px=2, shadow_offset=(2, 3))

        # Stats card
        mins = int(world.time_alive) // 60
        secs = int(world.time_alive) % 60
        time_str = f"{mins}:{secs:02d}" if mins else f"{secs}s"
        rows = [
            ("Time alive",     time_str),
            ("Coins",          str(world.coin_count)),
            ("Pillars cleared", str(world.pillars_passed)),
            ("Power-ups",      str(sum(world.powerups_picked.values()))),
            ("Near misses",    str(world.near_misses)),
        ]

        row_h = 32
        card_rect = pygame.Rect(18, card_y + 114, W - 36, len(rows) * row_h + 20)
        _dark_panel(surf, card_rect, radius=16, alpha=210)

        ry = card_rect.y + 14
        for i, (label, value) in enumerate(rows):
            if i > 0:
                div = pygame.Surface((card_rect.width - 24, 1), pygame.SRCALPHA)
                div.fill((*_ORANGE_BORDER, 35))
                surf.blit(div, (card_rect.x + 12, ry - 4))
            # Per-character red-outline styling on every label and value —
            # same writing style as the TOP 10 / RUN SUMMARY headers, just
            # smaller. _outlined_text takes a centre point, so compute one
            # from the desired left/right anchor.
            kf = _font(13, True)
            klbl = kf.render(label.upper(), True, _GOLD_BRIGHT)
            kl_center = (card_rect.x + 16 + klbl.get_width() // 2, ry + klbl.get_height() // 2)
            _outlined_text(surf, label.upper(), kl_center,
                           size=13, px=1, shadow_offset=(1, 2))
            vf = _font(15, True)
            vimg = vf.render(value, True, _GOLD_BRIGHT)
            vr_center = (card_rect.right - 16 - vimg.get_width() // 2, ry + vimg.get_height() // 2)
            _outlined_text(surf, value, vr_center,
                           size=15, px=1, shadow_offset=(1, 2))
            ry += row_h

        # Tap-to-continue prompt — also outlined (gold + red) so every line
        # on the screen shares the same writing style.
        if elapsed >= 0.6:
            alpha = max(80, min(255, int(150 + math.sin(self.title_t * 4) * 90)))
            # Render the outlined text onto a temp surface so we can apply
            # the pulsing alpha to the whole stack at once.
            tmp_w, tmp_h = 280, 36
            tmp = pygame.Surface((tmp_w, tmp_h), pygame.SRCALPHA)
            _outlined_text(tmp, "TAP TO CONTINUE",
                           (tmp_w // 2, tmp_h // 2),
                           size=18, px=2, shadow_offset=(2, 3))
            tmp.set_alpha(alpha)
            surf.blit(tmp, tmp.get_rect(center=(W // 2, H - 50)))

    def draw_gameover(self, surf, dt, score: int, new_best: bool):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 1, 21, 195))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)

        if score > 0:
            # "GAME OVER" with red outline
            pulse_go = 1.0 + math.sin(self.title_t * 3.0) * 0.03
            _outlined_text(surf, "GAME  OVER", (W // 2, 172),
                            size=int(38 * pulse_go), px=3)

            # Decorative divider
            pygame.draw.line(surf, (*_ORANGE_BORDER, 140),
                             (W // 2 - 80, 200), (W // 2 + 80, 200), 1)

            # Score block
            score_panel = pygame.Rect(W // 2 - 90, 212, 180, 88)
            _dark_panel(surf, score_panel, radius=18, alpha=210)
            lf = _font(12, False)
            lbl = lf.render("S C O R E", True, _GOLD_MUTED)
            lbl.set_alpha(180)
            surf.blit(lbl, lbl.get_rect(center=(W // 2, 228)))
            pulse_sc = 1.0 + math.sin(self.title_t * 2.2) * 0.02
            sf = _font(int(52 * pulse_sc), True)
            sc = sf.render(str(score), True, _GOLD_BRIGHT)
            surf.blit(sc, sc.get_rect(center=(W // 2, 268)))

            if new_best:
                # Star burst dots around NEW BEST
                nb_cy = 332
                for i in range(8):
                    ang = (i / 8) * math.pi * 2 + self.title_t * 2
                    r = 28 + 4 * math.sin(self.title_t * 5 + i)
                    dx, dy = math.cos(ang) * r, math.sin(ang) * r
                    a = max(0, min(255, int(100 + 120 * math.sin(self.title_t * 4 + i * 0.8))))
                    s = pygame.Surface((4, 4), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*_GOLD_BRIGHT, a), (2, 2), 2)
                    surf.blit(s, (W // 2 + int(dx) - 2, nb_cy + int(dy) - 2))
                pulse_nb = 1.0 + math.sin(self.title_t * 6) * 0.1
                _outlined_text(surf, "NEW  BEST!", (W // 2, nb_cy),
                                size=int(22 * pulse_nb), fill=UI_ORANGE,
                                outline=_RED_OUTLINE, px=2)
        else:
            pulse = 1.0 + math.sin(self.title_t * 4) * 0.05
            _outlined_text(surf, "TRY  AGAIN!", (W // 2, H // 2 - 30),
                            size=int(30 * pulse), fill=UI_ORANGE,
                            outline=_RED_OUTLINE, px=2)

        btn_alpha = int(150 + math.sin(self.title_t * 4) * 90)
        _pill_btn(surf, (W // 2, H - 72), "TAP TO RETRY", size=19, alpha=btn_alpha)
        _draw_mountain_silhouette(surf, alpha=160)

    def draw_name_entry(self, surf, dt, buf: str):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((8, 3, 26, 240))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)

        # Trophy above the title — same emblem as the TOP 10 screen.
        _draw_trophy(surf, W // 2, H // 2 - 210, 18)

        # Title
        _outlined_text(surf, "Welcome to the TOP 10!", (W // 2, H // 2 - 150),
                       size=22, px=2, shadow_offset=(2, 3))

        # Trophy below the title — mirrors the one above.
        _draw_trophy(surf, W // 2, H // 2 - 100, 18)

        # Input field
        fw, fh = 284, 54
        fx, fy = W // 2 - fw // 2, H // 2 - 48
        field = pygame.Surface((fw, fh), pygame.SRCALPHA)
        pygame.draw.rect(field, (26, 15, 56, 255), (0, 0, fw, fh), border_radius=14)
        pygame.draw.rect(field, (*_ORANGE_BORDER, 220), (0, 0, fw, fh),
                         border_radius=14, width=2)
        # Inner highlight line at top
        pygame.draw.line(field, (255, 200, 100, 40), (14, 3), (fw - 14, 3))
        surf.blit(field, (fx, fy))

        # Typed text — no cursor
        tf = _font(26, True)
        if buf:
            txt = tf.render(buf, True, _GOLD_BRIGHT)
            surf.blit(txt, txt.get_rect(center=(W // 2, fy + fh // 2)))
        else:
            placeholder = _font(18, False).render("TYPE YOUR NAME…", True, _GOLD_MUTED)
            placeholder.set_alpha(100)
            surf.blit(placeholder, placeholder.get_rect(center=(W // 2, fy + fh // 2)))

        # Mountain silhouette belongs to the backdrop — drawn before the
        # buttons so SUBMIT / SKIP sit on top of any scenery, never behind it.
        _draw_mountain_silhouette(surf, alpha=160)

        # Paired action buttons. Identical size + fully opaque + no
        # animation so neither button visually overpowers the other.
        self.name_submit_rect = _pill_btn(
            surf, (W // 2, H // 2 + 34), "SUBMIT",
            size=18, alpha=255, min_width=200)
        self.name_skip_rect = _pill_btn(
            surf, (W // 2, H // 2 + 92), "SKIP",
            size=18, alpha=255, min_width=200)

    def draw_leaderboard(self, surf, dt, scores: list, player_rank: int,
                         loading: bool, cooldown: float):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 20, 200))
        surf.blit(dim, (0, 0))

        # Header: trophy icon — "TOP 10" — trophy icon
        _outlined_text(surf, "TOP 10", (W // 2, 46), size=32, px=3)
        for side in (-1, 1):
            tx = W // 2 + side * 88
            ty = 46
            _draw_trophy(surf, tx, ty, 18)

        card_x, card_w = 14, W - 28

        # Slide-in from below (title_t reset to 0 on state entry)
        slide_t = min(1.0, self.title_t / 0.4)
        e = slide_t * slide_t * (3 - 2 * slide_t)
        card_y = int(88 + (1.0 - e) * 80)

        if loading:
            _text(surf, "Fetching scores", (W // 2, card_y + 40), size=16,
                  color=UI_CREAM, shadow=True)
            dot_r = 6
            dot_gap = 22
            cx0 = W // 2 - dot_gap
            for i in range(3):
                a = int(80 + 160 * (0.5 + 0.5 * math.sin(self.title_t * 5 + i * math.pi / 1.5)))
                ds = pygame.Surface((dot_r * 2 + 2, dot_r * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(ds, (*UI_GOLD, a), (dot_r + 1, dot_r + 1), dot_r)
                surf.blit(ds, (cx0 + i * dot_gap - dot_r - 1, card_y + 70 - dot_r - 1))
        else:
            n = len(scores)
            if n == 0:
                _text(surf, "No scores yet!", (W // 2, card_y + 60),
                      size=18, color=UI_CREAM, shadow=True)
                _text(surf, "Be the first.", (W // 2, card_y + 94),
                      size=14, color=UI_CREAM, shadow=False)
            else:
                row_h = 46
                card_h = n * row_h + 14
                card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
                rounded_rect(surf, card_rect, 16, (10, 18, 48), 230)

                SILVER    = (185, 195, 205)
                BRONZE    = (185, 125,  55)
                BADGE_NAV = ( 25,  35,  70)

                f_badge = _font(13, True)
                f_name  = _font(16, False)
                f_you   = _font(10, True)
                f_score = _font(17, True)

                ry = card_y + 7
                for i, entry in enumerate(scores):
                    rank = i + 1
                    if rank == 1:
                        badge_col = UI_GOLD
                    elif rank == 2:
                        badge_col = SILVER
                    elif rank == 3:
                        badge_col = BRONZE
                    else:
                        badge_col = BADGE_NAV

                    is_player = (i == player_rank)
                    row_cy = ry + row_h // 2

                    if is_player:
                        hl = pygame.Surface((card_w - 8, row_h - 4), pygame.SRCALPHA)
                        hl.fill((15, 70, 20, 180))
                        surf.blit(hl, (card_x + 4, ry))
                        name_col  = UI_GOLD
                        score_col = UI_GOLD
                    else:
                        name_col  = WHITE
                        score_col = badge_col if rank <= 3 else UI_CREAM

                    badge_cx = card_x + 22
                    pygame.draw.circle(surf, badge_col, (badge_cx, row_cy), 14)
                    if rank <= 3:
                        pygame.draw.circle(surf, (0, 0, 0), (badge_cx, row_cy), 14, 1)
                    num_img = f_badge.render(str(rank), True,
                                             (25, 15, 0) if rank <= 3 else WHITE)
                    surf.blit(num_img, num_img.get_rect(center=(badge_cx, row_cy)))

                    nm = entry["name"][:10]
                    nm_img = f_name.render(nm, True, name_col)
                    nm_x = card_x + 44
                    surf.blit(nm_img, (nm_x, row_cy - nm_img.get_height() // 2))

                    if is_player:
                        you_img = f_you.render("YOU", True, WHITE)
                        pw = you_img.get_width() + 10
                        ph = you_img.get_height() + 6
                        px = nm_x + nm_img.get_width() + 7
                        py = row_cy - ph // 2
                        you_pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
                        rounded_rect(you_pill, you_pill.get_rect(), 4, (15, 100, 35), 220)
                        surf.blit(you_pill, (px, py))
                        surf.blit(you_img, (px + 5, py + 3))

                    sc_img = f_score.render(str(entry["score"]), True, score_col)
                    surf.blit(sc_img,
                              (card_x + card_w - 12 - sc_img.get_width(),
                               row_cy - sc_img.get_height() // 2))

                    if i < n - 1:
                        pygame.draw.line(surf, (25, 38, 75),
                                         (card_x + 8, ry + row_h - 1),
                                         (card_x + card_w - 8, ry + row_h - 1))
                    ry += row_h

        if cooldown <= 0:
            alpha = int(150 + math.sin(self.title_t * 4) * 90)
            f2 = _font(18, True)
            prompt = f2.render("TAP TO MENU", True, WHITE)
            prompt.set_alpha(alpha)
            pr = prompt.get_rect(center=(W // 2, H - 42))
            surf.blit(prompt, pr.topleft)
