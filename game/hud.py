"""HUD: score, hi-score, coin count, mushroom timer bar, combo, pause button."""
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


def _pill_btn(surf, center, text, size=20, alpha=255, wide=False):
    """Styled pill button with red gradient fill + orange border (welcome theme)."""
    f = _font(size, True)
    img = f.render(text, True, WHITE)
    pad_x = 64 if wide else 44
    pw = img.get_width() + pad_x
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
    surf.blit(pill, (cx - pw // 2, cy - ph // 2))


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
    """Gold procedural trophy icon. `size` is approximate half-height."""
    s = size
    g = pygame.Surface((s * 2 + 4, s * 2 + 4), pygame.SRCALPHA)
    gc = (s + 2, s + 2)
    GOLD  = (240, 192,  64, 255)
    DARK  = (140,  90,   8, 255)
    WHITE = (255, 248, 200, 180)

    # Cup body — rounded trapezoid
    cup_pts = [
        (gc[0] - s,     gc[1] - s + 2),
        (gc[0] + s,     gc[1] - s + 2),
        (gc[0] + s - 3, gc[1] + 2),
        (gc[0] - s + 3, gc[1] + 2),
    ]
    pygame.draw.polygon(g, DARK, [(x+1, y+1) for x, y in cup_pts])
    pygame.draw.polygon(g, GOLD, cup_pts)
    # Cup rim highlight
    pygame.draw.line(g, WHITE, (gc[0] - s + 2, gc[1] - s + 3),
                     (gc[0] + s - 2, gc[1] - s + 3), 1)
    # Handles — small arcs on each side
    for side in (-1, 1):
        hx = gc[0] + side * (s - 1)
        pygame.draw.arc(g, GOLD,
                        (hx - 4 if side == 1 else hx,
                         gc[1] - s + 4, 6, s - 2),
                        math.pi * 0.25, math.pi * 0.75 if side == -1 else math.pi * 1.75,
                        2)
    # Stem
    stem_x = gc[0] - 2
    stem_y = gc[1] + 2
    pygame.draw.rect(g, DARK,  (stem_x,     stem_y + 1, 5, s // 2 + 1))
    pygame.draw.rect(g, GOLD,  (stem_x + 1, stem_y,     3, s // 2))
    # Base
    base_y = gc[1] + 2 + s // 2
    pygame.draw.rect(g, DARK,  (gc[0] - s + 2, base_y + 1, (s - 1) * 2, 4))
    pygame.draw.rect(g, GOLD,  (gc[0] - s + 2, base_y,     (s - 1) * 2, 3))
    # Foot
    pygame.draw.rect(g, DARK,  (gc[0] - s + 1, base_y + 4, (s - 1) * 2 + 2, 3))
    pygame.draw.rect(g, GOLD,  (gc[0] - s + 1, base_y + 3, (s - 1) * 2 + 2, 3))

    surf.blit(g, (cx - s - 2, cy - s - 2))


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
        # Horseshoe U
        pygame.draw.arc(surf, (220, 30, 40),
                        (cx - 8, cy - 7, 16, 14),
                        math.pi, 2 * math.pi, 4)
        pygame.draw.rect(surf, (220, 30, 40), (cx - 8, cy, 3, 7))
        pygame.draw.rect(surf, (220, 30, 40), (cx + 5, cy, 3, 7))
        pygame.draw.rect(surf, (220, 220, 235), (cx - 8, cy + 4, 3, 3))
        pygame.draw.rect(surf, (220, 220, 235), (cx + 5, cy + 4, 3, 3))
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
        # Parrot in front of a tall green up-arrow backdrop (boost-feel for 3X coins).
        GREEN_HI  = ( 50, 220, 100)
        GREEN_OUT = ( 28, 160,  70)

        head_w  = 13
        shaft_w = 5
        total_h = 19
        head_h  = int(total_h * 0.42)
        top_y    = cy - total_h // 2
        head_bot = top_y + head_h
        bot_y    = cy + total_h // 2
        pts_out = [
            (cx,                  top_y),
            (cx + head_w // 2,    head_bot),
            (cx + shaft_w // 2,   head_bot),
            (cx + shaft_w // 2,   bot_y),
            (cx - shaft_w // 2,   bot_y),
            (cx - shaft_w // 2,   head_bot),
            (cx - head_w // 2,    head_bot),
        ]
        pygame.draw.polygon(surf, GREEN_OUT, pts_out)
        pts_in = [
            (cx,                      top_y + 1),
            (cx + head_w // 2 - 1,    head_bot - 1),
            (cx + shaft_w // 2 - 1,   head_bot - 1),
            (cx + shaft_w // 2 - 1,   bot_y - 1),
            (cx - shaft_w // 2 + 1,   bot_y - 1),
            (cx - shaft_w // 2 + 1,   head_bot - 1),
            (cx - head_w // 2 + 1,    head_bot - 1),
        ]
        pygame.draw.polygon(surf, GREEN_HI, pts_in)

        bird = _get_grow_parrot_hud()
        surf.blit(bird, (cx - bird.get_width() // 2, cy - bird.get_height() // 2))


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

        # Floating title
        pulse = 1.0 + math.sin(self.title_t * 2.4) * 0.04
        float_y = int(7 * math.sin(self.title_t * 1.8))
        _outlined_text(surf, "SKYBIT", (W // 2, 176 + float_y),
                        size=int(72 * pulse), px=3)

        # Subtitle
        sub_f = _font(14, False)
        sub = sub_f.render("P O C K E T   S K Y   F L Y E R", True, _GOLD_MUTED)
        sub.set_alpha(200)
        surf.blit(sub, sub.get_rect(center=(W // 2, 228)))

        # Divider
        pygame.draw.line(surf, (*_ORANGE_BORDER, 120),
                         (W // 2 - 70, 248), (W // 2 + 70, 248), 1)

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
        # Star icon
        cx, cy = 18, 18
        for i in range(5):
            ang = math.pi / 2 + i * 4 * math.pi / 5
            ang2 = ang + 2 * math.pi / 5
            r1, r2 = 8, 4
            x1 = cx + math.cos(ang)  * r1
            y1 = cy - math.sin(ang)  * r1
            x2 = cx + math.cos(ang2) * r2
            y2 = cy - math.sin(ang2) * r2
            if i == 0:
                pts = [(x1, y1)]
            else:
                pts += [(x2, y2), (x1, y1)]
        pts += [(cx + math.cos(math.pi / 2 + j * 4 * math.pi / 5) * [8, 4][j % 2],
                 cy - math.sin(math.pi / 2 + j * 4 * math.pi / 5) * [8, 4][j % 2])
                for j in range(1)]
        pygame.draw.circle(hi_pill, _GOLD_BRIGHT, (cx, cy), 7)
        pygame.draw.circle(hi_pill, _PANEL_DARK, (cx, cy), 4)
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

        # Mushroom (3x-coin) timer bar — depletes gold → orange → red so the
        # urgency is obvious at a glance. Pulses in the last two seconds.
        if world.triple_timer > 0:
            frac = world.triple_timer / TRIPLE_DURATION
            bw = 168
            bx = (W - bw) // 2
            by = 128
            # Label above the track
            label_col = UI_RED if frac < 0.25 else UI_ORANGE
            _text(surf, f"3X POWER  {world.triple_timer:.1f}s",
                  (W // 2, by - 10), size=13, color=label_col, shadow=True)
            # Track
            track_rect = pygame.Rect(bx - 2, by, bw + 4, 12)
            rounded_rect(surf, track_rect, 6, (20, 25, 50), 200)
            # Fill — color lerps with remaining time, pulses when critical
            if frac > 0.5:
                fill_lo = UI_ORANGE
                fill_hi = UI_GOLD
            elif frac > 0.25:
                t = (frac - 0.25) / 0.25
                fill_lo = lerp_color(UI_RED, UI_ORANGE, t)
                fill_hi = lerp_color(UI_ORANGE, UI_GOLD, t)
            else:
                fill_lo = (180, 20, 20)
                fill_hi = UI_RED
            fill = pygame.Rect(bx, by + 2, int(bw * frac), 8)
            if fill.width > 0:
                rounded_rect_grad(surf, fill, 4, fill_hi, fill_lo)
            # Low-time pulse ring
            if frac < 0.25:
                pulse = 0.5 + 0.5 * math.sin(self.title_t * 14)
                ring_a = int(140 * pulse)
                ring = pygame.Surface((bw + 10, 18), pygame.SRCALPHA)
                pygame.draw.rect(ring, (*UI_RED, ring_a), ring.get_rect(),
                                 border_radius=8, width=2)
                surf.blit(ring, (bx - 5, by - 3))

        # Active-buff strip (magnet + slowmo badges). Triple has its own
        # bigger timer bar above, so we don't duplicate it here.
        active = []
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
            slot_w, slot_h = 28, 32
            gap = 6
            strip_w = len(active) * slot_w + (len(active) - 1) * gap
            sx = (W - strip_w) // 2
            sy = H - 108
            for i, (kind, remain, total) in enumerate(active):
                r = pygame.Rect(sx + i * (slot_w + gap), sy, slot_w, slot_h)
                rounded_rect(surf, r, 6, (15, 25, 60), 190)
                _draw_buff_icon(surf, r.inflate(-6, -14).move(0, -2), kind)
                if remain is not None and total:
                    frac = max(0.0, min(1.0, remain / total))
                    bar_rect = pygame.Rect(r.x + 3, r.bottom - 6, r.width - 6, 3)
                    pygame.draw.rect(surf, (25, 25, 50), bar_rect, border_radius=1)
                    fw = int(bar_rect.width * frac)
                    if fw > 0:
                        pygame.draw.rect(surf, UI_GOLD,
                                         (bar_rect.x, bar_rect.y, fw, bar_rect.height),
                                         border_radius=1)

        # Combo badge bottom-center
        if world.combo >= 3 and world.combo_timer > 0:
            t = world.combo_timer / 1.6
            scale = 1.0 + math.sin(self.title_t * 12) * 0.08
            size = int(22 * scale)
            color = UI_ORANGE if world.combo < 5 else UI_RED
            f = _font(size, True)
            txt = f"X{world.combo} COMBO"
            img = f.render(txt, True, color)
            sh = f.render(txt, True, NEAR_BLACK)
            rr = img.get_rect(center=(W // 2, H - 60))
            sh.set_alpha(int(230 * t))
            img.set_alpha(int(255 * t))
            surf.blit(sh, (rr.x + 2, rr.y + 2))
            surf.blit(img, rr.topleft)

        # Float texts
        for ft in world.float_texts:
            ft.draw(surf)

    def draw_stats(self, surf, world, dt, elapsed):
        self.title_t += dt
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((6, 1, 21, 190))
        surf.blit(dim, (0, 0))

        _draw_overlay_stars(surf, self._stars, self.title_t)

        # Slide-in animation from below
        slide_t = max(0.0, min(1.0, elapsed / 0.35))
        e = slide_t * slide_t * (3 - 2 * slide_t)
        card_y = int(58 + (1.0 - e) * 60)

        # Header
        _outlined_text(surf, "RUN SUMMARY", (W // 2, card_y + 4),
                        size=24, px=2, shadow_offset=(2, 3))

        # Score block
        score_panel = pygame.Rect(W // 2 - 80, card_y + 28, 160, 68)
        _dark_panel(surf, score_panel, radius=16, alpha=200)
        lf = _font(12, False)
        lbl = lf.render("S C O R E", True, _GOLD_MUTED)
        lbl.set_alpha(180)
        surf.blit(lbl, lbl.get_rect(center=(W // 2, card_y + 44)))
        sf = _font(42, True)
        sc = sf.render(str(world.score), True, _GOLD_BRIGHT)
        surf.blit(sc, sc.get_rect(center=(W // 2, card_y + 76)))

        # Stats card
        mins = int(world.time_alive) // 60
        secs = int(world.time_alive) % 60
        time_str = f"{mins}:{secs:02d}" if mins else f"{secs}s"
        rows = [
            ("Coins",          str(world.coin_count)),
            ("Max combo",      f"x{world.max_combo}" if world.max_combo > 1 else "—"),
            ("Pillars cleared", str(world.pillars_passed)),
            ("Near misses",    str(world.near_misses)),
            ("Time alive",     time_str),
        ]
        total_pu = sum(world.powerups_picked.values())
        if total_pu > 0:
            rows.append(("Power-ups", str(total_pu)))

        row_h = 32
        card_rect = pygame.Rect(18, card_y + 114, W - 36, len(rows) * row_h + 20)
        _dark_panel(surf, card_rect, radius=16, alpha=210)

        f_key = _font(15, False)
        f_val = _font(17, True)
        ry = card_rect.y + 14
        for i, (label, value) in enumerate(rows):
            if i > 0:
                div = pygame.Surface((card_rect.width - 24, 1), pygame.SRCALPHA)
                div.fill((*_ORANGE_BORDER, 35))
                surf.blit(div, (card_rect.x + 12, ry - 4))
            k = f_key.render(label.upper(), True, _GOLD_MUTED)
            v = f_val.render(value, True, _GOLD_BRIGHT)
            surf.blit(k, (card_rect.x + 16, ry))
            vr = v.get_rect()
            vr.topright = (card_rect.right - 16, ry - 1)
            surf.blit(v, vr.topleft)
            ry += row_h

        if elapsed >= 0.6:
            alpha = max(60, min(220, int(130 + math.sin(self.title_t * 4) * 85)))
            _pill_btn(surf, (W // 2, H - 48), "TAP TO CONTINUE", size=17, alpha=alpha)

        _draw_mountain_silhouette(surf, alpha=160)

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

        # Title
        _outlined_text(surf, "ENTER YOUR NAME", (W // 2, H // 2 - 118),
                       size=24, px=2, shadow_offset=(2, 3))

        # Subtitle
        sf = _font(12, False)
        sub = sf.render("U P  T O  1 6  C H A R A C T E R S", True, _GOLD_MUTED)
        sub.set_alpha(170)
        surf.blit(sub, sub.get_rect(center=(W // 2, H // 2 - 86)))

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
            placeholder = _font(18, False).render("type your name…", True, _GOLD_MUTED)
            placeholder.set_alpha(100)
            surf.blit(placeholder, placeholder.get_rect(center=(W // 2, fy + fh // 2)))

        # Submit button (only active once something is typed)
        if buf.strip():
            alpha = int(190 + math.sin(self.title_t * 3.5) * 60)
            _pill_btn(surf, (W // 2, H // 2 + 34), "SUBMIT  ·  ENTER", size=17, alpha=alpha)
        else:
            _pill_btn(surf, (W // 2, H // 2 + 34), "SUBMIT  ·  ENTER", size=17, alpha=80)

        # Skip hint
        hf = _font(12, False)
        hint = hf.render("ESC to skip", True, _GOLD_MUTED)
        hint.set_alpha(110)
        surf.blit(hint, hint.get_rect(center=(W // 2, H // 2 + 78)))

        _draw_mountain_silhouette(surf, alpha=160)

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
