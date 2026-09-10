import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import sys
sys.path.insert(0, "/home/user/skybit")
import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

CARD_W_SS, CARD_H_SS = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS
inset = sc.m(sc._INSET)
rect_ss = pygame.Rect(inset, inset, CARD_W_SS - 2 * inset, CARD_H_SS - 2 * inset)


def render_card_clean(sid="skin_mummy"):
    sc._card_cache.clear()
    surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
    sc.draw_card(surf, sid, rect_ss, equipped=False, secret=False)
    return surf


# ── Baseline ──────────────────────────────────────────────────────────────────
baseline_ss = render_card_clean()

# ── dome-swell concept ──────────────────────────────────────────────────────────
# Portrait "swell" dome: taller ellipse replaces the circular cabochon so the
# hero reads bigger. KNOWN in this round: the ellipse bottom lands ~y134 SS,
# which crowds the ribbon lane (~y117) — flagged for the art-director pass; we
# render exactly as briefed and let the critique steer the fix.
ELL_CX, ELL_CY = 162, 60
ELL_RX, ELL_RY = 60, 74
HERO_PX = 104

orig_cabochon = sc.cabochon
orig_cabochon_glass = sc.cabochon_glass
orig_soft_glow = sc.soft_glow

# No-op the built-in circle dome so we can hand-draw the ellipse over the card.
sc.cabochon = lambda *a, **kw: None
sc.cabochon_glass = lambda *a, **kw: None
sc.soft_glow = lambda *a, **kw: None

orig_box = sc._BOX_PX
orig_dome_r = sc._DOME_R
sc._BOX_PX = HERO_PX
sc._DOME_R = ELL_RY  # any residual radius calc should key off the taller axis

sc._card_cache.clear()
concept_ss = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
sc.draw_card(concept_ss, "skin_mummy", rect_ss, equipped=False, secret=False)

# Restore module globals immediately so nothing else in-process is affected.
sc.cabochon = orig_cabochon
sc.cabochon_glass = orig_cabochon_glass
sc.soft_glow = orig_soft_glow
sc._BOX_PX = orig_box
sc._DOME_R = orig_dome_r
sc._card_cache.clear()

# 1. Soft radial glow behind the ellipse.
glow_surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
_gmin = min(ELL_RX, ELL_RY)
for i in range(_gmin, 0, -2):
    alpha = int(60 * i / _gmin)
    rx_i = int(ELL_RX * i / _gmin)
    ry_i = int(ELL_RY * i / _gmin)
    pygame.draw.ellipse(glow_surf, (80, 60, 20, alpha),
                        (ELL_CX - rx_i, ELL_CY - ry_i, rx_i * 2, ry_i * 2))
concept_ss.blit(glow_surf, (0, 0))

# 2. Ellipse body — fake a vertical gradient with per-scanline slices.
body_surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
CABO_LO = (28, 22, 44)
CABO_HI = (68, 54, 108)
for t in range(ELL_RY, -ELL_RY, -1):
    frac = (t + ELL_RY) / (2 * ELL_RY)  # 0 at top, 1 at bottom
    c = tuple(int(CABO_HI[i] * (1 - frac) + CABO_LO[i] * frac) for i in range(3))
    slice_rx = int(ELL_RX * (1 - (t / ELL_RY) ** 2) ** 0.5)
    if slice_rx > 0:
        pygame.draw.line(body_surf, (*c, 255),
                         (ELL_CX - slice_rx, ELL_CY + t),
                         (ELL_CX + slice_rx, ELL_CY + t))
concept_ss.blit(body_surf, (0, 0))

# 3. Hero thumbnail centred in the ellipse.
sc.blit_thumb(concept_ss, "skin_mummy", ELL_CX, ELL_CY, HERO_PX)

# 4. Glass sheen — bright top-left arc.
sheen_surf = pygame.Surface((CARD_W_SS, CARD_H_SS), pygame.SRCALPHA)
for angle_deg in range(-170, -10):
    angle = math.radians(angle_deg)
    sx = int(ELL_CX + (ELL_RX - 6) * math.cos(angle))
    sy = int(ELL_CY + (ELL_RY - 6) * math.sin(angle))
    alpha = int(90 * max(0, -math.cos(angle - math.pi * 1.25)))
    if alpha > 5:
        pygame.draw.circle(sheen_surf, (255, 248, 220, alpha), (sx, sy), 3)
concept_ss.blit(sheen_surf, (0, 0))

# 5. Gold bezel — two concentric ellipse strokes.
GOLD1 = (180, 148, 60)
GOLD2 = (140, 110, 40)
for rx_b, ry_b, col, w in [
    (ELL_RX, ELL_RY, GOLD1, 3),
    (ELL_RX + 3, ELL_RY + 3, GOLD2, 2),
]:
    pygame.draw.ellipse(concept_ss, col,
                        (ELL_CX - rx_b - w, ELL_CY - ry_b - w,
                         (rx_b + w) * 2, (ry_b + w) * 2), w)

# ── Comparison sheet ────────────────────────────────────────────────────────────
GAP, PAD, LABEL_H, HEADER_H = 8, 16, 28, 40
sheet_w = PAD * 2 + 2 * CARD_W_SS + GAP
sheet_h = (PAD * 2 + HEADER_H + LABEL_H + CARD_H_SS + GAP + LABEL_H
           + sc.CARD_H + PAD)
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((8, 8, 20))

fl = hud_font(14)
fh = hud_font(17)
title = fh.render("dome-swell  ·  baseline vs concept (skin_mummy)", True,
                  (240, 224, 180))
sheet.blit(title, (sheet_w // 2 - title.get_width() // 2,
                   (HEADER_H - title.get_height()) // 2))

for i, (lbl_text, surf) in enumerate(
        [("BASELINE (2x)", baseline_ss), ("DOME-SWELL (2x)", concept_ss)]):
    x = PAD + i * (CARD_W_SS + GAP)
    lbl = fl.render(lbl_text, True, (200, 210, 228))
    sheet.blit(lbl, (x + CARD_W_SS // 2 - lbl.get_width() // 2, PAD + HEADER_H))
    sheet.blit(surf, (x, PAD + HEADER_H + LABEL_H))

y1x = PAD + HEADER_H + LABEL_H + CARD_H_SS + GAP + LABEL_H
row_lbl = fl.render("at 1x  (162x100 final size)", True, (180, 180, 200))
sheet.blit(row_lbl, (PAD, y1x - LABEL_H))
for i, surf in enumerate([baseline_ss, concept_ss]):
    x = PAD + i * (CARD_W_SS + GAP)
    small = pygame.transform.smoothscale(surf, (sc.CARD_W, sc.CARD_H))
    sheet.blit(small, (x, y1x))

out = "/home/user/skybit/docs/store_card_size/dome_swell/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {sheet_w}x{sheet_h} -> {out}")
