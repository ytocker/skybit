"""
Five distinct procedural dollar-sign power-up icon concepts.

Each `draw_*` function paints an icon centered on (cx, cy) at the existing
power-up footprint (POWERUP_R = 14 from game.config), so any one of them
can later drop into entities.PowerUp without geometry changes. `pulse` is
the same 0..1+ phase advanced by `PowerUp.pulse` in-game; pass 0 for a
static frame.

NOTE: this module is preview-only. Nothing in game/ imports it yet — the
chosen variant gets wired into entities.PowerUp in a follow-up edit.
"""
import math
import pygame

from game.config import POWERUP_R
from game.draw import (
    rounded_rect, lerp_color, blit_glow,
    COIN_GOLD, COIN_DARK, WHITE, NEAR_BLACK, UI_GOLD,
)


# Bill-green palette shared by several variants.
BILL_GREEN_DK = (40, 110, 70)
BILL_GREEN    = (75, 165, 105)
BILL_GREEN_LT = (140, 215, 165)


# ── shared $-glyph helper ────────────────────────────────────────────────────

def _draw_dollar_glyph(surf, cx, cy, height, color, weight=2,
                       outline=None, outline_w=1):
    """Stylized $ glyph centered on (cx, cy). Two short verticals through the
    middle plus an S-curve made of two semicircle arcs. Width ≈ 0.6 * height."""
    h = max(8, int(height))
    w = max(4, int(h * 0.55))
    # Vertical bar through the centre, slightly extended top/bot.
    bar_top = (cx, cy - h // 2 - 1)
    bar_bot = (cx, cy + h // 2 + 1)
    if outline is not None:
        pygame.draw.line(surf, outline, bar_top, bar_bot, weight + outline_w * 2)
    pygame.draw.line(surf, color, bar_top, bar_bot, weight)

    # Two arcs forming the S-curve. Top arc opens down-right, bottom opens up-left.
    half = h // 2
    top_rect = pygame.Rect(cx - w // 2, cy - half, w, half)
    bot_rect = pygame.Rect(cx - w // 2, cy, w, half)
    # Outline pass first
    if outline is not None:
        pygame.draw.arc(surf, outline, top_rect.inflate(2, 2),
                        math.radians(20), math.radians(220), weight + outline_w * 2)
        pygame.draw.arc(surf, outline, bot_rect.inflate(2, 2),
                        math.radians(200), math.radians(400), weight + outline_w * 2)
    pygame.draw.arc(surf, color, top_rect,
                    math.radians(20), math.radians(220), weight)
    pygame.draw.arc(surf, color, bot_rect,
                    math.radians(200), math.radians(400), weight)


# ── V1 — gold coin disc with green $ ────────────────────────────────────────

def draw_coin(surf, cx, cy, pulse=0.0):
    r = POWERUP_R
    # Soft drop shadow
    sh = pygame.Surface((r * 2 + 6, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
    surf.blit(sh, (cx - r - 3, cy + r - 3))

    # Coin body — dark rim + gold fill + warm inner ring for depth
    pygame.draw.circle(surf, COIN_DARK, (cx, cy), r + 1)
    pygame.draw.circle(surf, COIN_GOLD, (cx, cy), r)
    pygame.draw.circle(surf, (255, 235, 110), (cx, cy), r - 3, 1)

    # Embossed dark-green $ shadow then bright green $.
    _draw_dollar_glyph(surf, cx + 1, cy + 1, height=int(r * 1.4),
                       color=BILL_GREEN_DK, weight=2)
    _draw_dollar_glyph(surf, cx,     cy,     height=int(r * 1.4),
                       color=BILL_GREEN,    weight=2,
                       outline=BILL_GREEN_DK, outline_w=1)

    # Specular pinprick highlight
    pygame.draw.circle(surf, WHITE, (cx - r // 2, cy - r // 2), 2)


# ── V2 — money bag (cloth sack) ─────────────────────────────────────────────

def draw_bag(surf, cx, cy, pulse=0.0):
    r = POWERUP_R
    # Drop shadow
    sh = pygame.Surface((r * 2 + 8, 7), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
    surf.blit(sh, (cx - r - 4, cy + r - 1))

    # Sack body — wider-bottom teardrop. Drawn as two stacked ellipses.
    body_dk = (95, 65, 35)
    body    = (150, 105, 60)
    body_lt = (200, 155, 95)
    body_rect = pygame.Rect(cx - r, cy - r // 3, r * 2, int(r * 1.7))
    # Outline + base
    pygame.draw.ellipse(surf, body_dk, body_rect.inflate(2, 2))
    pygame.draw.ellipse(surf, body,    body_rect)
    # Highlight on the upper-left curve
    hi = pygame.Rect(cx - r + 2, cy - r // 3 + 1, r, int(r * 0.55))
    pygame.draw.ellipse(surf, body_lt, hi)

    # Cinched neck — two ear-tufts at the top with a rope ring under them
    neck_y = cy - r // 3 - 2
    pygame.draw.polygon(surf, body_dk,
                        [(cx - r // 2, neck_y), (cx - 3, neck_y - 6),
                         (cx - 1, neck_y)])
    pygame.draw.polygon(surf, body_dk,
                        [(cx + r // 2, neck_y), (cx + 3, neck_y - 6),
                         (cx + 1, neck_y)])
    pygame.draw.polygon(surf, body,
                        [(cx - r // 2 + 1, neck_y), (cx - 3, neck_y - 5),
                         (cx - 1, neck_y)])
    pygame.draw.polygon(surf, body,
                        [(cx + r // 2 - 1, neck_y), (cx + 3, neck_y - 5),
                         (cx + 1, neck_y)])
    # Rope ring (darker band beneath the tufts)
    rope_rect = pygame.Rect(cx - r + 2, neck_y - 1, r * 2 - 4, 5)
    pygame.draw.ellipse(surf, body_dk, rope_rect)
    pygame.draw.ellipse(surf, (210, 180, 130), rope_rect.inflate(-2, -2))

    # White $ printed on the front of the bag
    _draw_dollar_glyph(surf, cx, cy + 4, height=int(r * 1.1),
                       color=WHITE, weight=2,
                       outline=NEAR_BLACK, outline_w=1)


# ── V3 — stack of bills ─────────────────────────────────────────────────────

def draw_bills(surf, cx, cy, pulse=0.0):
    r = POWERUP_R
    # Drop shadow under the stack
    sh = pygame.Surface((r * 2 + 8, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 130), sh.get_rect())
    surf.blit(sh, (cx - r - 4, cy + r - 4))

    # Three stacked banknote rectangles, slight horizontal offset per layer.
    bill_w = int(r * 2)
    bill_h = max(8, int(r * 0.85))
    layers = (
        (-3,  6, (28,  85,  55)),  # bottom-most, darkest
        ( 0,  2, (45, 130,  85)),
        ( 3, -3, BILL_GREEN),       # top, brightest — gets the $
    )
    for dx, dy, base in layers:
        rect = pygame.Rect(cx - bill_w // 2 + dx, cy - bill_h // 2 + dy,
                           bill_w, bill_h)
        rounded_rect(surf, rect, 3, NEAR_BLACK, 200)
        rounded_rect(surf, rect.inflate(-2, -2), 2, base, 255)
        # Inner border line for the "engraved" look
        pygame.draw.rect(surf, lerp_color(base, WHITE, 0.35),
                         rect.inflate(-6, -4), 1, border_radius=2)

    # $ on the top bill, plus a small "100" hint on either side.
    top_dx, top_dy = 3, -3
    bx = cx + top_dx
    by = cy + top_dy
    _draw_dollar_glyph(surf, bx, by, height=int(bill_h * 0.9),
                       color=BILL_GREEN_LT, weight=2,
                       outline=BILL_GREEN_DK, outline_w=1)
    # Tiny corner ticks evoking note serial-number marks
    pygame.draw.rect(surf, BILL_GREEN_LT,
                     (bx - bill_w // 2 + 3, by - bill_h // 2 + 2, 4, 2))
    pygame.draw.rect(surf, BILL_GREEN_LT,
                     (bx + bill_w // 2 - 7, by + bill_h // 2 - 4, 4, 2))


# ── V4 — neon glowing $ ─────────────────────────────────────────────────────

def draw_neon(surf, cx, cy, pulse=0.0):
    r = POWERUP_R
    # Pulsing scale
    p = 0.5 + 0.5 * math.sin(pulse)
    glow_r = r + 2 + int(p * 3)

    # Outer purple-pink halo
    blit_glow(surf, cx, cy, glow_r + 4, (200, 60, 220), alpha=140)
    # Mid cyan
    blit_glow(surf, cx, cy, glow_r,     (60, 200, 255), alpha=160)
    # Inner hot-white core
    blit_glow(surf, cx, cy, glow_r - 4, (255, 255, 255), alpha=200)

    # Solid neon-stroke $ on top: dark backing + cyan core + white inner highlight.
    h = int(r * 1.7)
    _draw_dollar_glyph(surf, cx, cy, height=h,
                       color=(20, 0, 40), weight=5)               # dark backing
    _draw_dollar_glyph(surf, cx, cy, height=h,
                       color=(120, 230, 255), weight=3)            # cyan body
    _draw_dollar_glyph(surf, cx, cy, height=h,
                       color=WHITE, weight=1)                     # white core


# ── V5 — faceted gem $ ──────────────────────────────────────────────────────

def draw_gem(surf, cx, cy, pulse=0.0):
    r = POWERUP_R

    # Soft green ground glow so the gem reads as luminous
    blit_glow(surf, cx, cy, r + 4, (80, 220, 140), alpha=120)

    # Diamond silhouette behind the $ — top/bottom triangles meeting at horizon
    gem_dk = (20, 70, 45)
    gem_md = (60, 170, 110)
    gem_lt = (170, 240, 200)
    top = [(cx, cy - r),
           (cx - r + 2, cy - 2),
           (cx + r - 2, cy - 2)]
    bot = [(cx, cy + r),
           (cx - r + 2, cy + 2),
           (cx + r - 2, cy + 2)]
    pygame.draw.polygon(surf, gem_dk, top)
    pygame.draw.polygon(surf, gem_dk, bot)
    # Lighter front facets
    pygame.draw.polygon(surf, gem_md,
                        [(cx, cy - r + 2), (cx - r + 4, cy - 1), (cx, cy)])
    pygame.draw.polygon(surf, gem_md,
                        [(cx, cy + r - 2), (cx - r + 4, cy + 1), (cx, cy)])
    # Brightest left highlight slice
    pygame.draw.polygon(surf, gem_lt,
                        [(cx, cy - r + 4), (cx - r + 6, cy), (cx - 2, cy - 1)])
    # Crisp facet edges
    for tri in (top, bot):
        pygame.draw.polygon(surf, NEAR_BLACK, tri, 1)
    pygame.draw.line(surf, gem_lt, (cx - r + 2, cy - 2), (cx + r - 2, cy - 2), 1)

    # White $ etched on the front
    _draw_dollar_glyph(surf, cx, cy, height=int(r * 1.3),
                       color=WHITE, weight=2,
                       outline=(20, 50, 35), outline_w=1)

    # Sparkle dot upper-right
    pygame.draw.line(surf, WHITE, (cx + r - 3, cy - r + 4),
                     (cx + r + 1, cy - r + 8), 1)
    pygame.draw.line(surf, WHITE, (cx + r + 1, cy - r + 4),
                     (cx + r - 3, cy - r + 8), 1)


# ── registry — used by the preview tool ─────────────────────────────────────

VARIANTS = (
    ("COIN",  draw_coin),
    ("BAG",   draw_bag),
    ("BILLS", draw_bills),
    ("NEON",  draw_neon),
    ("GEM",   draw_gem),
)
