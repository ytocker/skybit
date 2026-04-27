"""
KFC powerup preview — loads the real KFC logo PNG, wraps it in a white
circle (with subtle red glow), and renders a side-by-side preview at
game-sprite scale and at a larger display size.
"""
import os, math
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "offscreen"

import pygame
pygame.init()
pygame.display.set_mode((1, 1))   # needed for convert_alpha() in offscreen mode

BG      = ( 15,  10,  30)
RED_KFC = (228,   0,  43)
WHITE   = (255, 255, 255)
GOLD    = (255, 210,  60)

os.makedirs("screenshots", exist_ok=True)

logo_raw = pygame.image.load("game/assets/kfc_logo.png").convert_alpha()


def draw_kfc_powerup(surf, cx, cy, r, pulse=0.0):
    """
    Draw KFC powerup at (cx, cy).
    r  = radius of the white badge circle
    pulse = 0..2π  animation phase
    """
    # ── Soft drop shadow ──────────────────────────────────────────────────────
    sh_w = int(r * 2.8)
    sh_h = int(r * 0.6)
    sh = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 80), sh.get_rect())
    surf.blit(sh, (cx - sh_w // 2, cy + r + 2))

    # ── Pulsing red glow ring ─────────────────────────────────────────────────
    glow_a = int(55 + 30 * math.sin(pulse))
    glow_r = r + 4 + int(2 * math.sin(pulse * 1.3))
    glow = pygame.Surface(((glow_r + 2) * 2, (glow_r + 2) * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*RED_KFC, glow_a), (glow_r + 2, glow_r + 2), glow_r + 2)
    surf.blit(glow, (cx - glow_r - 2, cy - glow_r - 2))

    # ── White circle background ───────────────────────────────────────────────
    # Thin dark outline for separation from background
    pygame.draw.circle(surf, (40, 40, 60),  (cx, cy), r + 2)
    pygame.draw.circle(surf, WHITE,         (cx, cy), r + 1)

    # ── KFC logo scaled to fit inside the circle ──────────────────────────────
    logo_size = int(r * 1.72)          # logo is square-ish; fill circle tightly
    logo = pygame.transform.smoothscale(logo_raw, (logo_size, logo_size))

    # Clip the logo to the white circle so corners don't bleed outside
    clip_surf = pygame.Surface((logo_size, logo_size), pygame.SRCALPHA)
    cx_l, cy_l = logo_size // 2, logo_size // 2
    pygame.draw.circle(clip_surf, (255, 255, 255, 255), (cx_l, cy_l), logo_size // 2)
    clipped = logo.copy()
    clipped.blit(clip_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    surf.blit(clipped, (cx - logo_size // 2, cy - logo_size // 2))


# ─── Render ───────────────────────────────────────────────────────────────────

PANEL_W, PANEL_H = 680, 260
canvas = pygame.Surface((PANEL_W, PANEL_H))
canvas.fill(BG)

# Large preview
draw_kfc_powerup(canvas, 140, 120, r=90, pulse=0.8)

# Medium preview
draw_kfc_powerup(canvas, 380, 120, r=45, pulse=0.0)

# Game-size preview (r≈16) zoomed ×5
GAME_R = 16
ZOOM   = 5
ss_size = (GAME_R + 10) * 2
ss = pygame.Surface((ss_size, ss_size), pygame.SRCALPHA)
ss.fill(BG)
draw_kfc_powerup(ss, ss_size // 2, ss_size // 2, r=GAME_R, pulse=1.2)
zoomed = pygame.transform.scale_by(ss, ZOOM)
canvas.blit(zoomed, (490, PANEL_H // 2 - zoomed.get_height() // 2))

# Labels
lf = pygame.font.SysFont(None, 20)
canvas.blit(lf.render("Large",        True, (160, 160, 180)), ( 110, 12))
canvas.blit(lf.render("Medium",       True, (160, 160, 180)), ( 355, 12))
canvas.blit(lf.render(f"Game ×{ZOOM}", True, (160, 160, 180)), ( 545, 12))

out = "screenshots/kfc_preview.png"
pygame.image.save(canvas, out)
print(f"  saved {out}")
pygame.quit()
