"""
Faithful KFC logo prototype — rendered at large preview size and game sprite size.

Real logo facts (2018 current design):
  - Red trapezoidal badge (wider top, narrower bottom — bucket silhouette)
  - Three VERTICAL stripes: narrow red left | wide white center | narrow red right
  - Colonel Sanders: bold black-and-white line art portrait
      white pompadour hair, round black-framed glasses, white goatee (pointed),
      black bow tie (two triangles), red apron at bottom
  - "KFC" bold text BELOW the badge (not inside it)
  - Brand red: #E4002B = (228, 0, 43)
"""
import os, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

import pygame
pygame.init()

RED   = (228,  0,  43)   # KFC #E4002B
BLACK = (  0,  0,   0)
WHITE = (255, 255, 255)
BG    = ( 15,  10,  30)  # dark game background

os.makedirs("screenshots", exist_ok=True)


# ── Colonel Sanders portrait ──────────────────────────────────────────────────

def draw_colonel(surf, cx, top_y, badge_h, white_w):
    """
    Simplified Colonel Sanders — white oval head/hair block, round glasses,
    goatee, bow tie.  Rendered as bold black-on-white line art.
    """
    lw = max(1, badge_h // 42)

    # Combined head+hair oval occupies upper ~65% of badge
    head_w  = int(white_w * 0.70)
    head_h  = int(badge_h  * 0.62)
    head_cy = top_y + int(badge_h * 0.32)
    hr      = pygame.Rect(cx - head_w//2, head_cy - head_h//2, head_w, head_h)

    # Hair region = top 36% of the oval; face = remainder
    hair_line_y = head_cy - head_h//2 + int(head_h * 0.36)

    # Draw white oval (covers both hair and face zones)
    pygame.draw.ellipse(surf, WHITE, hr)
    pygame.draw.ellipse(surf, BLACK, hr, lw)

    # Width of oval at hair_line_y (for the dividing line endpoints)
    dy = abs(hair_line_y - head_cy) / (head_h / 2)
    if dy < 1.0:
        hw_at_line = int((head_w / 2) * math.sqrt(max(0.0, 1.0 - dy * dy)))
        pygame.draw.line(surf, BLACK,
                         (cx - hw_at_line, hair_line_y),
                         (cx + hw_at_line, hair_line_y), lw)

    # Small pompadour bump on top of oval (swept-up white hair)
    bump_r = max(2, int(head_w * 0.22))
    bump_cy = head_cy - head_h//2 - bump_r//3
    bump_cx = cx + int(head_w * 0.06)   # slightly off-center (swept to right)
    pygame.draw.circle(surf, WHITE, (bump_cx, bump_cy), bump_r)
    pygame.draw.circle(surf, BLACK, (bump_cx, bump_cy), bump_r, lw)

    # ── Glasses ───────────────────────────────────────────────────────────────
    face_zone_h = head_h - int(head_h * 0.36)      # height below hair_line
    eye_r   = max(2, int(head_w * 0.105))
    eye_y   = hair_line_y + int(face_zone_h * 0.20)
    eye_gap = int(head_w * 0.19)
    eye_lx  = cx - eye_gap
    eye_rx  = cx + eye_gap
    for ex in (eye_lx, eye_rx):
        pygame.draw.circle(surf, WHITE, (ex, eye_y), eye_r)
        pygame.draw.circle(surf, BLACK, (ex, eye_y), eye_r, max(1, int(eye_r * 0.42)))
    # Bridge
    pygame.draw.line(surf, BLACK,
                     (eye_lx + eye_r, eye_y), (eye_rx - eye_r, eye_y), lw)
    # Temple arms
    pygame.draw.line(surf, BLACK,
                     (eye_lx - eye_r, eye_y), (cx - head_w//2 + lw + 1, eye_y), lw)
    pygame.draw.line(surf, BLACK,
                     (eye_rx + eye_r, eye_y), (cx + head_w//2 - lw - 1, eye_y), lw)

    # ── Goatee ────────────────────────────────────────────────────────────────
    mouth_y     = hair_line_y + int(face_zone_h * 0.60)
    goatee_bot  = hair_line_y + int(face_zone_h * 0.86)
    goatee_hw   = max(2, int(head_w * 0.13))
    pygame.draw.polygon(surf, WHITE,
                        [(cx, goatee_bot), (cx - goatee_hw, mouth_y), (cx + goatee_hw, mouth_y)])
    pygame.draw.polygon(surf, BLACK,
                        [(cx, goatee_bot), (cx - goatee_hw, mouth_y), (cx + goatee_hw, mouth_y)], lw)

    # ── Bow tie ───────────────────────────────────────────────────────────────
    tie_cy = hair_line_y + int(face_zone_h * 0.73)
    tie_hw = max(2, int(head_w * 0.19))
    tie_hh = max(2, int(face_zone_h * 0.09))
    knot_r = max(1, tie_hh // 2)
    pygame.draw.polygon(surf, BLACK,
                        [(cx, tie_cy), (cx - tie_hw, tie_cy - tie_hh), (cx - tie_hw, tie_cy + tie_hh)])
    pygame.draw.polygon(surf, BLACK,
                        [(cx, tie_cy), (cx + tie_hw, tie_cy - tie_hh), (cx + tie_hw, tie_cy + tie_hh)])
    pygame.draw.circle(surf, BLACK, (cx, tie_cy), knot_r)


# ── KFC badge ─────────────────────────────────────────────────────────────────

def draw_kfc_badge(surf, cx, cy, badge_h):
    """
    Draw the KFC logo badge centered at (cx, cy) with given height.
    Correct structure: red trapezoid | white center | red side stripes | Colonel portrait | KFC text below.
    """
    lw      = max(1, badge_h // 42)
    top_w   = badge_h                  # roughly square at top
    bot_w   = int(badge_h * 0.58)     # narrower base (bucket silhouette)
    top_y   = cy - badge_h // 2
    bot_y   = cy + badge_h // 2

    side_px = max(2, int(top_w * 0.17))   # each red side stripe

    # Outer red trapezoid
    outer = [
        (cx - top_w//2, top_y),
        (cx + top_w//2, top_y),
        (cx + bot_w//2, bot_y),
        (cx - bot_w//2, bot_y),
    ]

    # White center trapezoid (inset by side_px on each side)
    wt_w = top_w - 2 * side_px
    wb_w = max(2, bot_w - 2 * side_px)
    white = [
        (cx - wt_w//2, top_y),
        (cx + wt_w//2, top_y),
        (cx + wb_w//2, bot_y),
        (cx - wb_w//2, bot_y),
    ]

    # Red apron — bottom 20% of the white zone (Colonel's red shirt visible)
    t = 0.80   # fraction from top where apron starts
    apron_top_y  = top_y + int(badge_h * t)
    apron_top_hw = int((wt_w // 2) * (1 - t) + (wb_w // 2) * t)
    apron = [
        (cx - apron_top_hw, apron_top_y),
        (cx + apron_top_hw, apron_top_y),
        (cx + wb_w // 2,    bot_y),
        (cx - wb_w // 2,    bot_y),
    ]

    # Drop shadow
    sh = pygame.Surface((top_w + 12, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 70), sh.get_rect())
    surf.blit(sh, (cx - top_w // 2 - 6, bot_y + 6))

    # 1. Red outer badge
    pygame.draw.polygon(surf, RED, outer)
    # 2. White center stripe
    pygame.draw.polygon(surf, WHITE, white)
    # 3. Red apron
    pygame.draw.polygon(surf, RED, apron)
    # 4. Colonel portrait
    draw_colonel(surf, cx, top_y, badge_h, wt_w)
    # 5. Outlines
    pygame.draw.polygon(surf, BLACK, outer,  lw)
    pygame.draw.polygon(surf, BLACK, white,  max(1, lw - 1))
    pygame.draw.line(surf, BLACK,
                     (cx - apron_top_hw, apron_top_y),
                     (cx + apron_top_hw, apron_top_y), max(1, lw - 1))

    # 6. "KFC" bold text below badge
    fs = max(10, int(badge_h * 0.22))
    try:
        font = pygame.font.SysFont("Arial Black", fs, bold=True)
    except Exception:
        font = pygame.font.SysFont(None, fs + 6, bold=True)
    txt = font.render("KFC", True, RED)
    surf.blit(txt, (cx - txt.get_width() // 2, bot_y + lw + 4))


# ── Render ────────────────────────────────────────────────────────────────────

W, H = 700, 320
canvas = pygame.Surface((W, H))
canvas.fill(BG)

# Large preview (left half)
LARGE_H = 220
draw_kfc_badge(canvas, 175, 148, LARGE_H)

# Game-size badge zoomed x6 (right half)
GAME_H = 32
ZOOM   = 6
ss = pygame.Surface((GAME_H * 2 + 10, GAME_H * 2 + 36), pygame.SRCALPHA)
ss.fill(BG)
draw_kfc_badge(ss, GAME_H + 5, GAME_H + 6, GAME_H)
zoomed = pygame.transform.scale_by(ss, ZOOM)
canvas.blit(zoomed, (380, H // 2 - zoomed.get_height() // 2))

# Labels
lf = pygame.font.SysFont(None, 22)
canvas.blit(lf.render("Preview (large)", True, (180, 180, 200)), (110, 14))
canvas.blit(lf.render(f"Game sprite x{ZOOM}",  True, (180, 180, 200)), (470, 14))
pygame.draw.line(canvas, (50, 50, 80), (360, 10), (360, H - 10), 1)

out = "screenshots/kfc_faithful.png"
pygame.image.save(canvas, out)
print(f"  saved {out}")
pygame.quit()
