import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
import game.store_cards as sc
from game.store_cards import (cabochon, cabochon_glass, blit_thumb, facet_gem,
    chip_body_stops, vgrad_stops, soft_glow, drop_shadow, bevel_rim,
    top_sheen, contact_shadow, _ribbon, _name_on, state_chip,
    CARD_T, CARD_B, CABO_LO, CABO_HI, CARD_RING_DEEP, CARD_RING_BRIGHT, m, SS)
from game.hud import _font
from game.draw import lerp_color


# BLEND_ADD ignores per-pixel alpha, so many glow layers of a bright colour pile
# up to a flat white plateau. Feeding soft_glow deeply-dimmed ambers keeps the
# accumulated sum a warm gold instead of blowing to white.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)
sc.gloss_sweep = _gloss_sweep_fixed

GOLD_A_STOPS = [(0.00, (244, 192, 88)), (0.32, (228, 162, 56)),
                (0.66, (196, 124, 34)), (1.00, (150, 92, 18))]
GOLD_A_RIM_DARK = (86, 50, 8)
GOLD_A_RIM_BRIGHT = (255, 240, 190)
pal = {"gem": (255, 202, 104), "glow": (255, 168, 58), "deep": (150, 92, 22)}

GLOW_DEEP = (80, 48, 12)
GLOW_MID = (55, 33, 8)
GLOW_FAINT = (28, 17, 4)


def draw_panel(surf, ox, oy, affordable):
    """Rarity Altar confirm-purchase panel. ox/oy are the top-left of the
    360x640 virtual canvas this panel owns."""
    panel = pygame.Rect(ox + 20, oy + 25, 320, 590)

    # 1. scrim + faint background haze
    scrim = pygame.Surface((360, 640), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (ox, oy))
    haze = pygame.Surface((360, 640), pygame.SRCALPHA)
    for r, a in [(80, 8), (140, 5), (200, 3)]:
        soft_glow(haze, 180, 320, r, GLOW_FAINT, peak_alpha=a, layers=4)
    surf.blit(haze, (ox, oy))

    # 2. panel body
    body = vgrad_stops(panel.w, panel.h, 20,
                       [(0.0, CARD_T), (0.55, (20, 22, 58)), (1.0, CARD_B)],
                       alpha=255)
    surf.blit(body, panel.topleft)

    # 3. concentric altar radial glow — soft additive, deeply-dimmed colours
    altar_cx, altar_cy = panel.centerx, panel.y + 240
    glow_surf = pygame.Surface((panel.w, panel.h), pygame.SRCALPHA)
    rings = [
        (22,  GLOW_DEEP,  40, 5),
        (50,  GLOW_DEEP,  28, 6),
        (88,  GLOW_MID,   18, 6),
        (135, GLOW_MID,   10, 5),
        (182, GLOW_FAINT,  6, 4),
        (228, GLOW_FAINT,  3, 3),
    ]
    gx = altar_cx - panel.x
    gy = altar_cy - panel.y
    dim = 1.0 if affordable else 0.7
    for radius, color, alpha, layers in rings:
        soft_glow(glow_surf, gx, gy, radius, color,
                  peak_alpha=int(alpha * dim), layers=layers)
    surf.blit(glow_surf, panel.topleft, special_flags=pygame.BLEND_ADD)

    # 4. item disc — hero
    cx, cy = panel.centerx, panel.y + 155
    disc_halo = pygame.Surface((panel.w, panel.h), pygame.SRCALPHA)
    soft_glow(disc_halo, cx - panel.x, cy - panel.y, 155, GLOW_DEEP,
              peak_alpha=int(38 * dim), layers=7)
    surf.blit(disc_halo, panel.topleft, special_flags=pygame.BLEND_ADD)
    DS = 260 * 2 + 20 * 2
    ss = pygame.Surface((DS, DS), pygame.SRCALPHA)
    cabochon(ss, DS // 2, DS // 2, 260, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(ss, "skin_classic", DS // 2, DS // 2, int(260 * 1.5))
    cabochon_glass(ss, DS // 2, DS // 2, 260, tint=pal["gem"])
    out = pygame.transform.smoothscale(ss, (260, 260))
    surf.blit(out, out.get_rect(center=(cx, cy)))

    # 5. dais shelf bar
    shelf_y = cy + 130
    shelf_rect = pygame.Rect(panel.x + 16, shelf_y, panel.w - 32, 6)
    for sx in range(shelf_rect.w):
        t = abs(sx - shelf_rect.w / 2) / (shelf_rect.w / 2)
        col = lerp_color(pal["gem"], pal["deep"], t ** 0.8)
        pygame.draw.line(surf, col, (shelf_rect.x + sx, shelf_y),
                         (shelf_rect.x + sx, shelf_y + 5))
    pygame.draw.line(surf, CARD_RING_BRIGHT, shelf_rect.topleft, shelf_rect.topright)
    shadow_surf = pygame.Surface((shelf_rect.w, 10), pygame.SRCALPHA)
    for sy in range(10):
        a = int(80 * (1 - sy / 10))
        shadow_surf.fill((4, 4, 12, a), pygame.Rect(0, sy, shelf_rect.w, 1))
    surf.blit(shadow_surf, (shelf_rect.x, shelf_y + 6))

    # 6. facet gem corner
    facet_gem(surf, panel.right - 22, panel.y + 22, 14, pal["gem"], pal["deep"])

    # 7. item name nameplate — below the dais, does NOT bisect the disc
    np_y = shelf_y + 18
    np_rect = pygame.Rect(panel.centerx - 130, np_y, 260, 32)
    np_surf = pygame.Surface((260, 32), pygame.SRCALPHA)
    np_surf.fill((*CARD_B, 200))
    pygame.draw.rect(np_surf, (*CARD_RING_BRIGHT, 90), np_surf.get_rect(),
                     width=1, border_radius=6)
    name_txt = _font(12, True).render("Night Hawk", True, (246, 240, 216))
    np_surf.blit(name_txt, name_txt.get_rect(center=(130, 16)))
    surf.blit(np_surf, np_rect.topleft)

    # 8. ribbon + price chip
    info_y = np_y + 40
    info_ss = pygame.Surface((panel.w * SS, 100), pygame.SRCALPHA)
    _ribbon(info_ss, "LEGENDARY", panel.w * SS // 2, 24, panel.w * SS - m(28), pal)
    state_chip(info_ss, "skin_classic", panel.w * SS // 2, 72, False, False, m(22))
    info_out = pygame.transform.smoothscale(info_ss, (panel.w, 50))
    surf.blit(info_out, (panel.x, info_y))

    # 9. BUY button — wide golden slab
    bw, bh = 290, 56
    buy_rect = pygame.Rect(panel.centerx - bw // 2, panel.bottom - 70, bw, bh)
    if affordable:
        soft_glow(surf, panel.centerx, buy_rect.centery, 60, GLOW_DEEP,
                  peak_alpha=38, layers=6)
        btn = pygame.Surface((bw * SS, bh * SS), pygame.SRCALPHA)
        chip_body_stops(btn, btn.get_rect(), 28 * SS, GOLD_A_STOPS,
                        GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, gloss=65, gamma=1.06)
        buy_lbl = _font(int(20 * SS), True).render("BUY", True, (52, 28, 4))
        btn.blit(buy_lbl, buy_lbl.get_rect(center=(bw * SS // 2, bh * SS // 2)))
    else:
        btn = pygame.Surface((bw * SS, bh * SS), pygame.SRCALPHA)
        chip_body_stops(btn, btn.get_rect(), 28 * SS,
                        [(0, (48, 44, 58)), (1, (30, 28, 40))],
                        (60, 54, 72), (92, 84, 104), gloss=20, gamma=1.0)
        buy_lbl = _font(int(20 * SS), True).render("BUY", True, (120, 116, 134))
        btn.blit(buy_lbl, buy_lbl.get_rect(center=(bw * SS // 2, bh * SS // 2)))
        na = _font(9, True).render("NOT ENOUGH COINS", True, (150, 166, 190))
        surf.blit(na, na.get_rect(center=(panel.centerx, buy_rect.y - 10)))
    surf.blit(pygame.transform.smoothscale(btn, (bw, bh)), buy_rect.topleft)

    # 10. CANCEL — demoted, above BUY
    cw, ch = 120, 30
    can_rect = pygame.Rect(panel.centerx - cw // 2, buy_rect.y - 8 - ch, cw, ch)
    can_ss = pygame.Surface((cw * SS, ch * SS), pygame.SRCALPHA)
    chip_body_stops(can_ss, can_ss.get_rect(), 15 * SS,
                    [(0, (70, 62, 80)), (1, (44, 38, 56))],
                    (40, 34, 50), (126, 116, 138), gloss=20, gamma=1.0)
    can_lbl = _font(int(11 * SS), True).render("CANCEL", True, (160, 152, 170))
    can_ss.blit(can_lbl, can_lbl.get_rect(center=(cw * SS // 2, ch * SS // 2)))
    surf.blit(pygame.transform.smoothscale(can_ss, (cw, ch)), can_rect.topleft)

    # 11. frame
    drop_shadow(surf, panel, 20, blur=12, alpha=200, dy=6)
    bevel_rim(surf, panel, 20, deep=CARD_RING_DEEP, bright=CARD_RING_BRIGHT, w=2)
    top_sheen(surf, panel, 20, h=38, peak=55)

    return panel, altar_cx, altar_cy


canvas = pygame.Surface((740, 640), pygame.SRCALPHA)
canvas.fill((4, 4, 10, 255))

p_aff, acx, acy = draw_panel(canvas, 0, 0, affordable=True)
draw_panel(canvas, 380, 0, affordable=False)

# labels
lab = _font(13, True)
canvas.blit(lab.render("AFFORDABLE", True, (236, 202, 116)), (26, 6))
canvas.blit(lab.render("CAN'T AFFORD", True, (150, 166, 190)), (406, 6))

# radial smoothness verification (printed, not drawn)
for rr in [0, 20, 50, 100, 160]:
    px = canvas.get_at((acx + rr, acy))
    print(f"altar r={rr:3d}: {tuple(px)}")

os.makedirs("/home/user/skybit/docs/confirm_purchase_v2/rarity-altar", exist_ok=True)
pygame.image.save(canvas, "/home/user/skybit/docs/confirm_purchase_v2/rarity-altar/round_2.png")
print("saved")
