import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import math
import game.store_cards as sc
from game.store_cards import (cabochon, cabochon_glass, blit_thumb, facet_gem,
    chip_body_stops, vgrad_stops, soft_glow, drop_shadow, bevel_rim,
    top_sheen, contact_shadow, plain_text, _ribbon, _name_on, state_chip,
    CARD_T, CARD_B, CABO_LO, CABO_HI, CARD_RING_DEEP, CARD_RING_BRIGHT, m, SS)
from game.hud import _font


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
# Red-biased amber so overlapping BLEND_ADD layers saturate toward hot gold, not
# the green-white a neutral warm hits once every channel maxes.
GLOW_WARM = (74, 34, 9)


def warm_ring(surf, cx, cy, r0, sigma, r_max, peak_rgb):
    """A Gaussian halo peaked at radius r0, painted onto ONE surface (step-1
    circles) and BLEND_ADD-ed a single time. A single blit is what keeps the
    aura from the runaway green-white that stacked soft_glow layers hit — the
    added colour never exceeds peak_rgb, and a red-biased peak stays hot-gold as
    it saturates. r0 sits just outside the disc so the energy hugs its rim."""
    c = r_max + 1
    aura = pygame.Surface((c * 2, c * 2), pygame.SRCALPHA)
    for i in range(r_max, 0, -1):
        t = math.exp(-((i - r0) / sigma) ** 2)
        col = (int(peak_rgb[0] * t), int(peak_rgb[1] * t), int(peak_rgb[2] * t))
        if max(col) <= 0:
            continue
        pygame.draw.circle(aura, (*col, 255), (c, c), i, 2)
    surf.blit(aura, (cx - c, cy - c), special_flags=pygame.BLEND_ADD)


def draw_diamond(surf, cx, cy, r, color):
    """A small filled rhombus bullet — the font lacks ◈, so the sci-fi marker is
    drawn instead of typed to avoid tofu boxes."""
    pygame.draw.polygon(surf, color,
                        [(cx, cy - r), (cx + r * 0.72, cy), (cx, cy + r),
                         (cx - r * 0.72, cy)])


def star_pts(cx, cy, ro, ri, n=5):
    pts = []
    for i in range(n * 2):
        rr = ro if i % 2 == 0 else ri
        a = -math.pi / 2 + i * math.pi / n
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def _star_glow(r, color):
    """A small filled 5-point star on its own tight surface (font has no ★)."""
    s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.polygon(s, color, star_pts(r + 1, r + 1, r, r * 0.44))
    return s


def build_status(text, mark_col, txt_col):
    """Compose "◈ BROADCAST ACTIVE ◈ LEGENDARY" with procedural diamonds so the
    marker glyphs render as real shapes rather than missing-glyph boxes."""
    f = _font(8, True)
    left, right = text
    ls = f.render(left, True, txt_col)
    rs = f.render(right, True, txt_col)
    dr = 3            # diamond radius
    gap = 6
    h = max(ls.get_height(), rs.get_height(), dr * 2)
    w = dr * 2 + gap + ls.get_width() + gap + dr * 2 + gap + rs.get_width() + gap + dr * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    x = dr
    draw_diamond(surf, x, h // 2, dr, mark_col)
    x += dr + gap
    surf.blit(ls, (x, (h - ls.get_height()) // 2))
    x += ls.get_width() + gap + dr
    draw_diamond(surf, x, h // 2, dr, mark_col)
    x += dr + gap
    surf.blit(rs, (x, (h - rs.get_height()) // 2))
    return surf


def render_panel(affordable):
    surf = pygame.Surface((360, 640), pygame.SRCALPHA)
    panel = pygame.Rect(10, 27, 340, 585)

    # 1. Scrim + panel body (holographic field ground).
    scrim = pygame.Surface((360, 640), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))
    # Cast shadow BEHIND the panel (drawn before the body so it never veils it).
    drop_shadow(surf, panel, 16, blur=10, alpha=180, dy=5)
    body = vgrad_stops(panel.w, panel.h, 16,
                       [(0.0, CARD_T), (0.6, (20, 22, 58)), (1.0, CARD_B)],
                       alpha=255)
    surf.blit(body, panel.topleft)

    # 2. Full-panel scanline shimmer — the panel IS the hologram field.
    # BLEND_ADD ignores source alpha, so intensity lives in the RGB itself: a
    # near-black gold that only whispers a horizontal scan texture.
    scan = pygame.Surface((panel.w, panel.h), pygame.SRCALPHA)
    scan.fill((0, 0, 0, 0))
    for sy in range(0, panel.h, 4):
        scan.fill((12, 9, 4, 255), pygame.Rect(0, sy, panel.w, 2))
    # Clip the shimmer to the rounded panel silhouette.
    smask = pygame.Surface((panel.w, panel.h), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(), border_radius=16)
    scan.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(scan, panel.topleft, special_flags=pygame.BLEND_ADD)

    # 3. Status line — sci-fi furniture above the disc.
    status_word = ("BROADCAST ACTIVE", "LEGENDARY") if affordable else \
                  ("BROADCAST STANDBY", "LOCKED")
    status_surf = build_status(status_word, pal["gem"], pal["gem"])
    status_surf.set_alpha(200 if affordable else 120)
    surf.blit(status_surf,
              status_surf.get_rect(center=(panel.centerx, panel.y + 20)))

    cx, cy = panel.centerx, panel.y + 195

    # 4. Broadcast aura BEHIND the disc (energy lives OUTSIDE the disc face).
    if affordable:
        # Outer broad field: controlled, sets the ambient glow of the broadcast.
        warm_ring(surf, cx, cy, r0=205, sigma=58, r_max=255, peak_rgb=(60, 30, 11))
        # Inner disc-rim halo: tight sigma so the energy hugs the disc edge and
        # falls off before the pedestal band below the disc — no white pooling.
        warm_ring(surf, cx, cy, r0=145, sigma=24, r_max=175, peak_rgb=(65, 32, 10))
    else:
        # Suspended broadcast: a faint, cold residual ring only.
        warm_ring(surf, cx, cy, r0=152, sigma=40, r_max=230, peak_rgb=(26, 30, 46))

    # Item disc — HERO, crisp, reads as ONE object.
    DS = 260 * 2 + 20 * 2
    ss_disc = pygame.Surface((DS, DS), pygame.SRCALPHA)
    cabochon(ss_disc, DS // 2, DS // 2, 260, CABO_LO, CABO_HI,
             ring=pal["gem"], ring_a=55)
    blit_thumb(ss_disc, "skin_classic", DS // 2, DS // 2, int(260 * 1.5))
    cabochon_glass(ss_disc, DS // 2, DS // 2, 260, tint=pal["gem"])
    disc_out = pygame.transform.smoothscale(ss_disc, (260, 260))
    disc_rect = disc_out.get_rect(center=(cx, cy))
    surf.blit(disc_out, disc_rect.topleft)

    # Disc-face shimmer — VERY subtle scan lines, only when broadcasting.
    # BLEND_ADD adds full RGB (ignores source alpha), so intensity must live in
    # the RGB: a near-black gold per row keeps the scan texture without blowout.
    if affordable:
        shimmer = pygame.Surface((260, 260), pygame.SRCALPHA)
        shimmer.fill((0, 0, 0, 0))
        for sy in range(0, 260, 6):
            shimmer.fill((28, 22, 10, 255), pygame.Rect(0, sy, 260, 1))
        mask = pygame.Surface((260, 260), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (130, 130), 130)
        shimmer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(shimmer, disc_rect.topleft, special_flags=pygame.BLEND_ADD)

    # 5. Flanking data readout — low-contrast telemetry over the hologram field.
    left_x = panel.x + 16
    for i, (label, value) in enumerate([("ITEM", "NIGHT HAWK"),
                                        ("TIER", "LEGENDARY")]):
        lbl = _font(7, True).render(label, True, (120, 112, 90))
        val = _font(8, True).render(value, True, (200, 185, 145))
        surf.blit(lbl, (left_x, cy - 62 + i * 30))
        surf.blit(val, (left_x, cy - 50 + i * 30))
    # RARITY row: four procedural stars, right-aligned (font has no ★).
    lbl = _font(7, True).render("RARITY", True, (120, 112, 90))
    surf.blit(lbl, (panel.right - 16 - lbl.get_width(), cy - 62))
    sr, sgap = 5, 13
    n_stars = 4
    star_row_w = (n_stars - 1) * sgap
    sx0 = panel.right - 16 - star_row_w
    for k in range(n_stars):
        surf.blit(_star_glow(sr, pal["gem"]),
                  (sx0 + k * sgap - sr - 1, cy - 50 + 2 - sr - 1))
    # PRICE row: number + a small drawn coin marker.
    lbl2 = _font(7, True).render("PRICE", True, (120, 112, 90))
    surf.blit(lbl2, (panel.right - 16 - lbl2.get_width(), cy - 62 + 30))
    val = _font(8, True).render("800", True, pal["gem"])
    facet_gem(surf, panel.right - 16 - 6, cy - 50 + 30 + val.get_height() // 2,
              5, pal["gem"], pal["deep"])
    surf.blit(val, (panel.right - 16 - 15 - val.get_width(), cy - 50 + 30))

    # 6. Info section (ribbon + name) below the disc.
    info_ss = pygame.Surface((panel.w * SS, 110), pygame.SRCALPHA)
    _ribbon(info_ss, "LEGENDARY", panel.w * SS // 2, 24, panel.w * SS - m(28), pal)
    _name_on(info_ss, "Night Hawk", panel.w * SS // 2, 68, panel.w * SS - m(20))
    info_out = pygame.transform.smoothscale(info_ss, (panel.w, 55))
    surf.blit(info_out, (panel.x, cy + 142))

    # 7. Price chip.
    pw, ph = 200, 28
    price_ss = pygame.Surface((pw * SS, ph * SS), pygame.SRCALPHA)
    sc.price_chip(price_ss, pw * SS // 2, ph * SS // 2, "800", m(22),
                  affordable=affordable)
    price_out = pygame.transform.smoothscale(price_ss, (pw, ph))
    surf.blit(price_out, price_out.get_rect(center=(panel.centerx, cy + 220)))

    # 8. BUY button — activation console.
    bw, bh = 230, 52
    buy_y = panel.bottom - 70
    buy_cx = panel.centerx
    btn = pygame.Surface((bw * SS, bh * SS), pygame.SRCALPHA)
    if affordable:
        # Activation bloom — single controlled radial (BLEND_ADD adds full RGB).
        warm_ring(surf, buy_cx, buy_y + bh // 2, r0=0, sigma=48, r_max=95,
                  peak_rgb=(66, 34, 12))
        chip_body_stops(btn, btn.get_rect(), 26 * SS, GOLD_A_STOPS,
                        GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, gloss=65, gamma=1.06)
        blabel = _font(int(18 * SS), True).render("BUY", True, (52, 28, 4))
    else:
        chip_body_stops(btn, btn.get_rect(), 26 * SS,
                        [(0, (48, 44, 58)), (1, (30, 28, 40))],
                        (60, 54, 72), (92, 84, 104), gloss=20, gamma=1.0)
        blabel = _font(int(18 * SS), True).render("BUY", True, (120, 116, 134))
    btn.blit(blabel, blabel.get_rect(center=(bw * SS // 2, bh * SS // 2)))
    surf.blit(pygame.transform.smoothscale(btn, (bw, bh)), (buy_cx - bw // 2, buy_y))

    if not affordable:
        nef = _font(9, True).render("NOT ENOUGH COINS", True, (150, 166, 190))
        surf.blit(nef, nef.get_rect(center=(buy_cx, buy_y - 10)))

    # 9. CANCEL (demoted) — cool slate so it sits clearly outside the gold family.
    cw, ch = 110, 30
    can_y = buy_y - 8 - ch
    if affordable:
        can_y = buy_y - 8 - ch
    else:
        can_y = buy_y - 26 - ch  # clear the NOT-ENOUGH-COINS line
    can = pygame.Surface((cw * SS, ch * SS), pygame.SRCALPHA)
    chip_body_stops(can, can.get_rect(), 15 * SS,
                    [(0, (52, 58, 78)), (1, (32, 36, 55))],
                    (38, 42, 60), (90, 96, 122), gloss=18, gamma=1.0)
    clabel = _font(int(11 * SS), True).render("CANCEL", True, (140, 148, 170))
    can.blit(clabel, clabel.get_rect(center=(cw * SS // 2, ch * SS // 2)))
    surf.blit(pygame.transform.smoothscale(can, (cw, ch)),
              (panel.centerx - cw // 2, can_y))

    # 10. Corner gem + frame (edge/top-only finishes, safe on top).
    facet_gem(surf, panel.right - 20, panel.y + 20, 12, pal["gem"], pal["deep"])
    bevel_rim(surf, panel, 16, deep=CARD_RING_DEEP, bright=CARD_RING_BRIGHT, w=2)
    top_sheen(surf, panel, 16, h=38, peak=50)
    return surf


def _verify(left):
    """Print the pixel checks the round demands, straight off the rendered
    AFFORDABLE panel (left half of the canvas)."""
    panel_y = 27
    cx, cy = 180, panel_y + 195

    # 1. Strip at y≈340 across x=100..260: no pure-white pixels.
    worst = None
    n_white = 0
    for y in range(335, 346):
        for x in range(100, 261):
            r, g, b, _ = left.get_at((x, y))
            if r > 250 and g > 250 and b > 250:
                n_white += 1
            s = r + g + b
            if worst is None or s > worst[0]:
                worst = (s, (x, y), (r, g, b))
    print("CHECK 1 — strip y=335..345, x=100..260:")
    print(f"  pure-white (R>250 & G>250 & B>250) pixel count: {n_white}")
    print(f"  brightest pixel in strip: {worst[2]} at {worst[1]}")

    # 2. Disc centre + 5 samples inside: none near-white.
    pts = [(cx, cy), (cx - 40, cy), (cx + 40, cy), (cx, cy - 40), (cx, cy + 40)]
    print("CHECK 2 — disc interior samples:")
    near_white = 0
    for p in pts:
        r, g, b, _ = left.get_at(p)
        nw = r > 250 and g > 250 and b > 250
        near_white += nw
        print(f"  {p}: ({r},{g},{b}){'  <-- NEAR WHITE' if nw else ''}")
    print(f"  near-white disc samples: {near_white}")

    # 3. CANCEL chip: blue > red (cool slate).
    buy_y = (panel_y + 585) - 70
    ch = 30
    can_cy = (buy_y - 8 - ch) + ch // 2
    r, g, b, _ = left.get_at((180, can_cy))
    print("CHECK 3 — CANCEL chip centre:")
    print(f"  ({r},{g},{b})  blue>red? {b > r}")


def main():
    left = render_panel(True)
    right = render_panel(False)
    canvas = pygame.Surface((740, 640))
    canvas.fill((4, 4, 10))
    canvas.blit(left, (0, 0))
    canvas.blit(right, (380, 0))
    # thin caption labels
    cap = _font(9, True)
    canvas.blit(cap.render("AFFORDABLE", True, (150, 160, 180)), (14, 622))
    canvas.blit(cap.render("CAN'T AFFORD", True, (150, 160, 180)), (394, 622))
    out = "/home/user/skybit/docs/confirm_purchase_v2/hologram-broadcast/round_3.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())
    print()
    _verify(left)


main()
