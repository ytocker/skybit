"""
KFC circular logo draft — procedural pygame drawing.
Reference: circular sign with red fill, white outer ring,
Colonel Sanders portrait left-center, bold white "KFC" right side.
"""
import os, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
os.makedirs("screenshots", exist_ok=True)

RED    = (210,  18,  30)   # KFC red
WHITE  = (255, 255, 255)
CREAM  = (250, 248, 240)
SKIN   = (232, 180, 130)
SKIN_D = (198, 148,  98)
DARK   = ( 25,  20,  20)
GRAY   = ( 90,  90,  90)
BG     = ( 15,  10,  30)


def _ell(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color,
        (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def draw_colonel(surf, cx, cy, ir):
    """Draw simplified Colonel Sanders inside the red circle."""
    # Portrait is positioned slightly left of circle center
    px = cx - int(ir * 0.10)
    lw = max(1, ir // 30)

    # ── Hair (white pompadour, extends above face) ────────────────────────────
    hair_cy = cy - int(ir * 0.46)
    hair_rx = int(ir * 0.34)
    hair_ry = int(ir * 0.28)
    # hair base ellipse
    _ell(surf, WHITE, px, hair_cy + int(ir * 0.08), hair_rx, hair_ry)
    # left bump
    pygame.draw.circle(surf, WHITE, (px - int(ir * 0.14), hair_cy), int(ir * 0.22))
    # right bump (swept up higher)
    pygame.draw.circle(surf, WHITE, (px + int(ir * 0.10), hair_cy - int(ir * 0.04)), int(ir * 0.19))
    # hair outlines
    pygame.draw.circle(surf, DARK, (px - int(ir * 0.14), hair_cy), int(ir * 0.22), lw)
    pygame.draw.circle(surf, DARK, (px + int(ir * 0.10), hair_cy - int(ir * 0.04)), int(ir * 0.19), lw)
    _ell(surf, DARK, px, hair_cy + int(ir * 0.08), hair_rx, hair_ry, )

    # ── Face oval ─────────────────────────────────────────────────────────────
    face_ry = int(ir * 0.30)
    face_rx = int(ir * 0.25)
    face_cy = cy - int(ir * 0.10)
    _ell(surf, SKIN,   px, face_cy, face_rx, face_ry)
    _ell(surf, SKIN_D, px, face_cy + int(face_ry * 0.5), face_rx, int(face_ry * 0.5))  # chin shadow
    pygame.draw.ellipse(surf, DARK,
        (int(px - face_rx), int(face_cy - face_ry),
         int(face_rx * 2), int(face_ry * 2)), lw)

    # ── Glasses ───────────────────────────────────────────────────────────────
    eye_r  = max(2, int(ir * 0.07))
    eye_y  = face_cy - int(face_ry * 0.08)
    eye_lx = px - int(face_rx * 0.38)
    eye_rx = px + int(face_rx * 0.38)
    for ex in (eye_lx, eye_rx):
        pygame.draw.circle(surf, WHITE, (ex, eye_y), eye_r)
        pygame.draw.circle(surf, DARK,  (ex, eye_y), eye_r, max(1, int(eye_r * 0.42)))
    pygame.draw.line(surf, DARK, (eye_lx + eye_r, eye_y), (eye_rx - eye_r, eye_y), lw)
    pygame.draw.line(surf, DARK, (eye_lx - eye_r, eye_y), (px - face_rx + lw, eye_y), lw)
    pygame.draw.line(surf, DARK, (eye_rx + eye_r, eye_y), (px + face_rx - lw, eye_y), lw)

    # ── Goatee ────────────────────────────────────────────────────────────────
    gt_top = face_cy + int(face_ry * 0.30)
    gt_tip = face_cy + int(face_ry * 0.64)
    gt_hw  = max(2, int(face_rx * 0.28))
    pygame.draw.polygon(surf, WHITE,
        [(px, gt_tip), (px - gt_hw, gt_top), (px + gt_hw, gt_top)])
    pygame.draw.polygon(surf, DARK,
        [(px, gt_tip), (px - gt_hw, gt_top), (px + gt_hw, gt_top)], lw)

    # ── Bow tie ───────────────────────────────────────────────────────────────
    tie_cy = face_cy + int(face_ry * 0.50)
    tie_hw = max(2, int(face_rx * 0.30))
    tie_hh = max(2, int(ir * 0.05))
    pygame.draw.polygon(surf, DARK,
        [(px, tie_cy), (px - tie_hw, tie_cy - tie_hh), (px - tie_hw, tie_cy + tie_hh)])
    pygame.draw.polygon(surf, DARK,
        [(px, tie_cy), (px + tie_hw, tie_cy - tie_hh), (px + tie_hw, tie_cy + tie_hh)])
    pygame.draw.circle(surf, DARK, (px, tie_cy), max(1, tie_hh // 2))

    # ── White shirt collar ────────────────────────────────────────────────────
    collar_y = face_cy + int(face_ry * 0.52)
    collar_w = int(face_rx * 0.80)
    collar_h = int(ir * 0.14)
    _ell(surf, WHITE, px, collar_y + collar_h // 2, collar_w, collar_h)

    # ── Red apron with white vertical stripes (bottom of circle) ─────────────
    apron_top = cy + int(ir * 0.22)
    apron_bot = cy + int(ir * 0.90)
    apron_hw  = int(ir * 0.42)
    apron_h   = apron_bot - apron_top
    pygame.draw.rect(surf, RED,
        (cx - int(ir * 0.55), apron_top, int(ir * 1.1), apron_h))
    # White vertical stripes on apron
    stripe_w = max(1, int(ir * 0.045))
    for i in range(-3, 4):
        sx = px + i * int(ir * 0.12)
        pygame.draw.rect(surf, WHITE, (sx - stripe_w // 2, apron_top, stripe_w, apron_h))
    # Apron top edge (white trim line)
    pygame.draw.line(surf, WHITE,
        (cx - apron_hw, apron_top), (cx + apron_hw, apron_top), lw + 1)


def draw_kfc_circle(surf, cx, cy, r, pulse=0.0):
    """Full circular KFC logo at (cx, cy) with outer radius r."""
    lw = max(1, r // 18)

    # Drop shadow
    sh = pygame.Surface(((r + 6) * 2, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 70), sh.get_rect())
    surf.blit(sh, (cx - r - 6, cy + r + 3))

    # Optional pulsing glow
    glow_a = int(45 + 20 * math.sin(pulse * 2))
    glow_r = r + 3 + int(2 * math.sin(pulse * 1.4))
    glow = pygame.Surface(((glow_r + 2) * 2, (glow_r + 2) * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*RED, glow_a), (glow_r + 2, glow_r + 2), glow_r + 2)
    surf.blit(glow, (cx - glow_r - 2, cy - glow_r - 2))

    # Outer dark ring (separation from background)
    pygame.draw.circle(surf, (50, 50, 50), (cx, cy), r + lw)
    # White outer ring
    pygame.draw.circle(surf, CREAM, (cx, cy), r)
    # Red inner circle
    ir = int(r * 0.84)
    pygame.draw.circle(surf, RED, (cx, cy), ir)

    # Colonel Sanders portrait
    draw_colonel(surf, cx, cy, ir)

    # "KFC" bold text — right side of red circle
    fs = max(8, int(ir * 0.30))
    try:
        font = pygame.font.SysFont("Arial Black", fs, bold=True)
    except Exception:
        font = pygame.font.SysFont(None, fs + 4, bold=True)
    kfc = font.render("KFC", True, WHITE)
    kx = cx + int(ir * 0.44) - kfc.get_width() // 2
    ky = cy - kfc.get_height() // 2 - int(ir * 0.04)
    surf.blit(kfc, (kx, ky))

    # Re-draw white outer ring border (on top so it clips the Colonel overflow)
    pygame.draw.circle(surf, CREAM, (cx, cy), r, int(r * 0.16))
    pygame.draw.circle(surf, (50, 50, 50), (cx, cy), r + lw, lw)
    pygame.draw.circle(surf, (50, 50, 50), (cx, cy), ir, lw)


# ── Render preview ────────────────────────────────────────────────────────────

W, H = 720, 300
canvas = pygame.Surface((W, H))
canvas.fill(BG)

# Large
draw_kfc_circle(canvas, 130, 148, r=110, pulse=0.8)

# Medium
draw_kfc_circle(canvas, 350, 148, r=55, pulse=0.0)

# Game-size zoomed x6
GAME_R = 16
ZOOM   = 6
ss = pygame.Surface((GAME_R * 3, GAME_R * 3), pygame.SRCALPHA)
ss.fill(BG)
draw_kfc_circle(ss, GAME_R + GAME_R // 2, GAME_R + GAME_R // 2, GAME_R, pulse=1.2)
zoomed = pygame.transform.scale_by(ss, ZOOM)
canvas.blit(zoomed, (480, H // 2 - zoomed.get_height() // 2))

lf = pygame.font.SysFont(None, 20)
canvas.blit(lf.render("Large",         True, (170, 170, 190)), ( 90, 14))
canvas.blit(lf.render("Medium",        True, (170, 170, 190)), (322, 14))
canvas.blit(lf.render(f"Game ×{ZOOM}", True, (170, 170, 190)), (554, 14))

out = "screenshots/kfc_circle_draft.png"
pygame.image.save(canvas, out)
print(f"  saved {out}")
pygame.quit()
