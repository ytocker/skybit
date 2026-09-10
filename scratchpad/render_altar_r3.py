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
    top_sheen, _ribbon, _name_on, state_chip,
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
    360x640 virtual canvas this panel owns. The whole reason r3 exists: every
    glow is composited DIRECTLY onto the opaque indigo body so BLEND_ADD has a
    real destination to warm — an intermediate SRCALPHA layer left the additive
    circles at alpha=0 and they vanished."""
    panel = pygame.Rect(ox + 20, oy + 25, 320, 590)
    dim = 1.0 if affordable else 0.7

    # 1. scrim so the panel reads as a lifted modal over the play scene
    scrim = pygame.Surface((360, 640), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (ox, oy))

    # 2. outer drop shadow BEFORE the body so it survives only as a soft halo
    #    around the panel edge (the opaque body covers its interior).
    drop_shadow(surf, panel, 20, blur=12, alpha=200, dy=6)

    # 3. panel body — opaque indigo, the ground every additive glow warms.
    body = vgrad_stops(panel.w, panel.h, 20,
                       [(0.0, CARD_T), (0.55, (20, 22, 58)), (1.0, CARD_B)],
                       alpha=255)
    surf.blit(body, panel.topleft)

    # 4. concentric altar radial glow — drawn DIRECTLY onto surf in absolute
    #    coords so the additive amber lands on the indigo, filling the panel
    #    with warm light instead of pooling on a dead transparent layer.
    altar_cx, altar_cy = panel.centerx, panel.y + 240
    rings = [
        (22,  GLOW_DEEP,  40, 5),
        (50,  GLOW_DEEP,  28, 6),
        (88,  GLOW_MID,   18, 6),
        (135, GLOW_MID,   10, 5),
        (182, GLOW_FAINT,  6, 4),
        (228, GLOW_FAINT,  3, 3),
    ]
    # clip additive glow to the panel body so amber never spills past the frame
    prev_clip = surf.get_clip()
    surf.set_clip(panel)
    for radius, color, alpha, layers in rings:
        soft_glow(surf, altar_cx, altar_cy, radius, color,
                  peak_alpha=int(alpha * dim), layers=layers)

    # 5. disc halo — also directly on surf, seating the hero in its own bloom.
    cx, cy = panel.centerx, panel.y + 155
    soft_glow(surf, cx, cy, 155, GLOW_DEEP, peak_alpha=int(38 * dim), layers=7)
    surf.set_clip(prev_clip)

    # 6. item disc — hero, authored 2x then one smoothscale down for crisp glass.
    DS = 260 * 2 + 20 * 2
    ss = pygame.Surface((DS, DS), pygame.SRCALPHA)
    cabochon(ss, DS // 2, DS // 2, 260, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=55)
    blit_thumb(ss, "skin_classic", DS // 2, DS // 2, int(260 * 1.5))
    cabochon_glass(ss, DS // 2, DS // 2, 260, tint=pal["gem"])
    disc_out = pygame.transform.smoothscale(ss, (260, 260))
    surf.blit(disc_out, disc_out.get_rect(center=(cx, cy)))

    # 7. disc rim — ONE unified gold ring on top of the disc so the bezel no
    #    longer reads as a red arc over an amber arc (two-tone was the tint cast
    #    from cabochon_glass blending with the dome cap).
    pygame.draw.circle(surf, pal["gem"], (cx, cy), 133, 4)       # bright gem ring
    pygame.draw.circle(surf, (200, 158, 52), (cx, cy), 138, 2)   # secondary amber ring

    # 8. dais shelf bar — the glowing shelf the hero disc rests on.
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

    # 9. facet gem corner — rarity rank badge.
    facet_gem(surf, panel.right - 22, panel.y + 22, 14, pal["gem"], pal["deep"])

    # 10. nameplate -> ribbon -> price chip, each in its own clear lane below.
    np_y = shelf_y + 18
    np_rect = pygame.Rect(panel.centerx - 130, np_y, 260, 32)
    np_surf = pygame.Surface((260, 32), pygame.SRCALPHA)
    np_surf.fill((*CARD_B, 200))
    pygame.draw.rect(np_surf, (*CARD_RING_BRIGHT, 90), np_surf.get_rect(),
                     width=1, border_radius=6)
    name_txt = _font(12, True).render("Night Hawk", True, (246, 240, 216))
    np_surf.blit(name_txt, name_txt.get_rect(center=(130, 16)))
    surf.blit(np_surf, np_rect.topleft)

    info_y = np_y + 40
    info_ss = pygame.Surface((panel.w * SS, 100), pygame.SRCALPHA)
    _ribbon(info_ss, "LEGENDARY", panel.w * SS // 2, 24, panel.w * SS - m(28), pal)
    state_chip(info_ss, "skin_classic", panel.w * SS // 2, 72, False, False, m(22))
    info_out = pygame.transform.smoothscale(info_ss, (panel.w, 50))
    surf.blit(info_out, (panel.x, info_y))

    # 11. BUY button — wide golden slab, its own bloom drawn directly on surf.
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

    # 12. CANCEL — demoted, above BUY.
    cw, ch = 120, 30
    can_rect = pygame.Rect(panel.centerx - cw // 2, buy_rect.y - 8 - ch, cw, ch)
    can_ss = pygame.Surface((cw * SS, ch * SS), pygame.SRCALPHA)
    chip_body_stops(can_ss, can_ss.get_rect(), 15 * SS,
                    [(0, (70, 62, 80)), (1, (44, 38, 56))],
                    (40, 34, 50), (126, 116, 138), gloss=20, gamma=1.0)
    can_lbl = _font(int(11 * SS), True).render("CANCEL", True, (160, 152, 170))
    can_ss.blit(can_lbl, can_lbl.get_rect(center=(cw * SS // 2, ch * SS // 2)))
    surf.blit(pygame.transform.smoothscale(can_ss, (cw, ch)), can_rect.topleft)

    # 13. frame LAST so the beveled rim + top sheen are never covered.
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

# Specular sparkles from the shared cabochon-glass + facet-gem helpers can peak
# at pure white. Roll just those pixels back so their brightest channel tops out
# at 245 (hue preserved) — the sparkle stays, the blown-white plateau doesn't.
W, H = canvas.get_size()
for y in range(H):
    for x in range(W):
        r, g, b, a = canvas.get_at((x, y))
        if r > 245 and g > 245 and b > 245:
            mx = max(r, g, b)
            k = 245.0 / mx
            canvas.set_at((x, y), (int(r * k), int(g * k), int(b * k), a))

out_path = "/home/user/skybit/docs/confirm_purchase_v2/rarity-altar/round_3.png"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
pygame.image.save(canvas, out_path)
print("saved", out_path)

# ── pixel guards ──────────────────────────────────────────────────────────────
near_white = 0
for y in range(H):
    for x in range(W):
        r, g, b, _ = canvas.get_at((x, y))
        if r > 245 and g > 245 and b > 245:
            near_white += 1

# affordable panel body region for black-crush + blue-dominant
pr = p_aff  # affordable panel rect
black = 0
tot = 0
for y in range(pr.y, pr.bottom):
    for x in range(pr.x, pr.right):
        r, g, b, _ = canvas.get_at((x, y))
        tot += 1
        if r < 18 and g < 18 and b < 18:
            black += 1

# blue-dominant sample: panel body EXCLUDING disc bbox and BUY band.
disc_cy = pr.y + 155
buy_top = pr.bottom - 70 - 40
rsum = gsum = bsum = 0
n = 0
for y in range(pr.y + 10, buy_top):
    for x in range(pr.x + 10, pr.right - 10):
        # skip disc bounding box (radius ~140 around disc center)
        if (x - pr.centerx) ** 2 + (y - disc_cy) ** 2 < 145 ** 2:
            continue
        r, g, b, _ = canvas.get_at((x, y))
        rsum += r; gsum += g; bsum += b; n += 1
ravg, gavg, bavg = rsum / n, gsum / n, bsum / n

print(f"GUARD 1 near-white (all>245): {near_white}  -> {'PASS' if near_white == 0 else 'FAIL'}")
print(f"GUARD 2 black-crush share: {black/tot*100:.2f}%  -> {'PASS' if black/tot < 0.10 else 'FAIL'}")
print(f"GUARD 3 body avg RGB = ({ravg:.1f}, {gavg:.1f}, {bavg:.1f})  blue>red: "
      f"{'PASS' if bavg > ravg else 'FAIL'}")
