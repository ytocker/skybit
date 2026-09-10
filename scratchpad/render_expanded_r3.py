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
    price_chip, chip_body_stops, vgrad_stops, soft_glow,
    drop_shadow, bevel_rim, top_sheen, contact_shadow, plain_text,
    _ribbon, font as ssfont,
    CARD_T, CARD_B, CABO_LO, CABO_HI, CARD_RING_DEEP, CARD_RING_BRIGHT, m, SS)
from game.hud import _font
from game.draw import lerp_color


# ── gloss_sweep fix (RGBA-min mask keeps the sweep inside the rounded body) ────
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

# ── legendary palette ─────────────────────────────────────────────────────────
GOLD_A_STOPS = [(0.00, (244, 192, 88)), (0.32, (228, 162, 56)),
                (0.66, (196, 124, 34)), (1.00, (150, 92, 18))]
GOLD_A_RIM_DARK = (86, 50, 8)
GOLD_A_RIM_BRIGHT = (255, 240, 190)
pal = {"gem": (255, 202, 104), "glow": (255, 168, 58), "deep": (150, 92, 22)}

# Warm dark glow tint: BLEND_ADD ignores per-pixel alpha and sums full RGB, so a
# bright tint stacked across layers clips straight to white. A dark bronze keeps
# multi-layer halos readable as warm light instead of blowing out.
GLOW_WARM = (118, 70, 22)


def ring_glow(surf, cx, cy, inner_r, outer_r, color, peak_alpha, layers):
    """A warm halo that hugs OUTSIDE a disc bezel. soft_glow draws filled circles
    whose inner layers would otherwise sit on the disc face and — because
    BLEND_ADD ignores alpha — clip the interior to white. Accumulating the glow on
    a scratch surface, punching out the disc, then compositing normally keeps the
    warmth as a rim ring only, never a blown-out face."""
    tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    soft_glow(tmp, cx, cy, outer_r, color, peak_alpha, layers)
    pygame.draw.circle(tmp, (0, 0, 0, 0), (cx, cy), inner_r)
    surf.blit(tmp, (0, 0))


def ss_widget(w_log, h_log, drawfn):
    """Author an SS-scale widget then downscale by 1/SS so its m()-based
    geometry lands at true logical size — the card pipeline's crisp-edge trick."""
    s = pygame.Surface((int(w_log * SS), int(h_log * SS)), pygame.SRCALPHA)
    drawfn(s, s.get_width() // 2, s.get_height() // 2)
    return pygame.transform.smoothscale(s, (int(w_log), int(h_log)))


def gold_name(canvas, text, cx, cy, size_logical, color):
    """Large bold gold item name — the second-loudest element on the card.
    Dark-indigo keyline (not gold) so it survives sitting over the gold ribbon
    band without smearing gold-on-gold."""
    f = ssfont(size_logical)
    w = f.size(text)[0] + m(12)
    h = f.get_height() + m(10)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    plain_text(s, text, f, (w // 2, h // 2), color, shadow_a=150,
               weight=m(1.1), keyline=(28, 30, 70), kw=m(1.1))
    small = pygame.transform.smoothscale(s, (w // SS, h // SS))
    canvas.blit(small, small.get_rect(center=(cx, cy)))


def draw_panel(canvas, ox, affordable):
    """One 360x640 confirm panel; origin x=ox on `canvas`."""
    # full-screen scrim
    scrim = pygame.Surface((360, 640), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    canvas.blit(scrim, (ox, 0))

    panel = pygame.Rect(ox + 10, 30, 340, 580)

    drop_shadow(canvas, panel, 17, blur=10, alpha=185, dy=5)

    # panel body — 3-stop indigo, lower band lifted so the sub-disc space
    # never reads as a dead void.
    canvas.blit(vgrad_stops(panel.w, panel.h, 17,
                            [(0.0, (28, 30, 70)), (0.6, (20, 22, 58)),
                             (1.0, (12, 13, 38))], alpha=255),
                panel.topleft)

    top_sheen(canvas, panel, 17, h=40, peak=60)
    contact_shadow(canvas, panel, 17, depth=9, alpha=110)
    bevel_rim(canvas, panel, 17, deep=CARD_RING_DEEP, bright=CARD_RING_BRIGHT, w=2)
    tray = panel.inflate(-8, -8)
    pygame.draw.rect(canvas, (*CARD_RING_BRIGHT, 80), tray, width=1, border_radius=13)

    cx = panel.centerx

    # ── HERO disc ─────────────────────────────────────────────────────────────
    # r108 (down from r130) so the name/ribbon/price/BUY/CANCEL stack below has
    # room to breathe instead of piling into the lower bevel.
    cy = panel.y + 165
    R_DISC = 108

    # warm ambient halo behind the disc (dark bronze, dim, few layers)
    soft_glow(canvas, cx, cy, 150, GLOW_WARM, peak_alpha=22, layers=5)

    DS = R_DISC * 2 * SS + 20 * 2
    ss = pygame.Surface((DS, DS), pygame.SRCALPHA)
    cabochon(ss, DS // 2, DS // 2, R_DISC * SS, CABO_LO, CABO_HI,
             ring=pal["gem"], ring_a=80)
    try:
        blit_thumb(ss, "skin_classic", DS // 2, DS // 2, int(R_DISC * SS * 1.5))
    except Exception:
        pygame.draw.circle(ss, (*pal["gem"], 255), (DS // 2, DS // 2),
                           int(R_DISC * SS * 0.7))
    cabochon_glass(ss, DS // 2, DS // 2, R_DISC * SS, tint=pal["gem"])
    disc = pygame.transform.smoothscale(ss, (R_DISC * 2, R_DISC * 2))
    canvas.blit(disc, disc.get_rect(center=(cx, cy)))
    disc_r = R_DISC

    # can't-afford: strong blue-indigo darken so the hero reads locked, not just
    # the button — an obvious non-colour affordability cue. Alpha pushed past the
    # first-pass 160 so the dimmed hero drops >50 luminance below the lit hero
    # (the delta at which the lock is unmistakable rather than a faint tint).
    if not affordable:
        dim = pygame.Surface((R_DISC * 2, R_DISC * 2), pygame.SRCALPHA)
        pygame.draw.circle(dim, (8, 12, 34, 215), (R_DISC, R_DISC), R_DISC)
        canvas.blit(dim, dim.get_rect(center=(cx, cy)))

    # faint warm ring hugging the bezel — marries the item art to the legendary
    # palette. Masked to the region OUTSIDE the disc so the additive glow can't
    # brighten (and blow out) the interior.
    ring_glow(canvas, cx, cy, disc_r, disc_r + 12, GLOW_WARM,
              peak_alpha=12, layers=3)

    # ── corner gem badges (both top corners) — unmistakable card DNA ───────────
    for gx in (panel.x + 20, panel.right - 20):
        gy = panel.y + 20
        soft_glow(canvas, gx, gy, 22, (85, 65, 18), peak_alpha=22, layers=4)
        facet_gem(canvas, gx, gy, 14, pal["gem"], pal["deep"])

    # ── name (gold, second-loudest) → ribbon → price chip ─────────────────────
    gold_name(canvas, "Night Hawk", cx, 338, 20, pal["gem"])

    ribbon = ss_widget(340, 26, lambda s, X, Y: _ribbon(
        s, "LEGENDARY", X, Y, s.get_width() - m(12), pal))
    canvas.blit(ribbon, ribbon.get_rect(center=(cx, 376)))

    chip = ss_widget(220, 32, lambda s, X, Y: price_chip(
        s, X, Y, "18,500", m(22), affordable=affordable))
    canvas.blit(chip, chip.get_rect(center=(cx, 416)))

    # ── BUY ────────────────────────────────────────────────────────────────────
    buy_rect = pygame.Rect(0, 0, 240, 52)
    buy_rect.centerx = cx
    buy_rect.top = 460
    buy_cx, buy_cy = buy_rect.center
    btn_ss = pygame.Surface((240 * SS, 52 * SS), pygame.SRCALPHA)
    if affordable:
        chip_body_stops(btn_ss, btn_ss.get_rect(), 26 * SS, GOLD_A_STOPS,
                        GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, gloss=65, gamma=1.06)
        buy_col = (52, 28, 4)
    else:
        chip_body_stops(btn_ss, btn_ss.get_rect(), 26 * SS,
                        [(0, (48, 44, 58)), (1, (30, 28, 40))],
                        (60, 54, 72), (92, 84, 104), gloss=20, gamma=1.0)
        buy_col = (120, 116, 134)
    lbl = _font(int(18 * SS), True).render("BUY", True, buy_col)
    btn_ss.blit(lbl, lbl.get_rect(center=(120 * SS, 26 * SS)))
    if affordable:
        soft_glow(canvas, buy_cx, buy_cy, 55, GLOW_WARM, peak_alpha=28, layers=5)
    buy_img = pygame.transform.smoothscale(btn_ss, (240, 52))
    canvas.blit(buy_img, buy_rect.topleft)

    # NOT ENOUGH COINS — rendered directly at logical size (no sub-legible
    # downscale) inside a dark plate with a faint gold keyline.
    if not affordable:
        warn_f = _font(13, True)
        warn = warn_f.render("NOT ENOUGH COINS", True, (220, 200, 160))
        wo = pygame.Surface((warn.get_width() + 12, warn.get_height() + 6),
                            pygame.SRCALPHA)
        wo.fill((12, 14, 32, 180))
        wo.blit(warn, (6, 3))
        pygame.draw.rect(wo, (*CARD_RING_BRIGHT, 60), wo.get_rect(),
                         width=1, border_radius=4)
        canvas.blit(wo, wo.get_rect(center=(cx, buy_rect.top - 14)))

    # ── CANCEL — demoted: low-sat, lifted off the bottom bevel ────────────────
    can_rect = pygame.Rect(0, 0, 116, 34)
    can_rect.centerx = cx
    can_rect.bottom = panel.bottom - 26
    can_ss = pygame.Surface((116 * SS, 34 * SS), pygame.SRCALPHA)
    chip_body_stops(can_ss, can_ss.get_rect(), 17 * SS,
                    [(0, (55, 50, 65)), (1, (38, 34, 50))],
                    (30, 26, 40), (90, 84, 100), gloss=18, gamma=1.0)
    clbl = _font(int(12 * SS), True).render("CANCEL", True, (160, 152, 170))
    can_ss.blit(clbl, clbl.get_rect(center=(58 * SS, 17 * SS)))
    can_img = pygame.transform.smoothscale(can_ss, (116, 34))
    canvas.blit(can_img, can_rect.topleft)

    # small state tag for the review sheet
    tag = _font(11, True).render("AFFORD" if affordable else "CAN'T AFFORD", True,
                                 (236, 202, 116))
    canvas.blit(tag, tag.get_rect(center=(cx, 14)))

    return cx, cy, R_DISC, buy_rect


canvas = pygame.Surface((740, 640))
canvas.fill((4, 4, 10))
aff = draw_panel(canvas, 0, True)
noaff = draw_panel(canvas, 380, False)

out = "/home/user/skybit/docs/confirm_purchase_v2/expanded-card/round_3.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())


# ── pixel verification guards ─────────────────────────────────────────────────
def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

acx, acy, adr, abuy = aff
ncx, ncy, ndr, nbuy = noaff

# 1) near-white inside affordable disc (allow tiny specular crescent < 2%)
near_white = 0
total = 0
disc_samples = []
for yy in range(acy - adr, acy + adr):
    for xx in range(acx - adr, acx + adr):
        if (xx - acx) ** 2 + (yy - acy) ** 2 > adr * adr:
            continue
        r, g, b, _ = canvas.get_at((xx, yy))
        total += 1
        disc_samples.append((r, g, b))
        if r > 250 and g > 250 and b > 250:
            near_white += 1
pct = 100.0 * near_white / max(1, total)
print(f"[1] near-white in affordable disc: {near_white}/{total} = {pct:.3f}% "
      f"(<=2% ok) -> {'PASS' if pct <= 2.0 else 'FAIL'}")

# 2) disc center legible (not pure white)
ctr = canvas.get_at((acx, acy))[:3]
print(f"[2] affordable disc center pixel {tuple(ctr)} -> "
      f"{'PASS' if tuple(ctr) != (255, 255, 255) else 'FAIL'}")

# 3) BUY chip warm gold (center row average)
rs = gs = bs = n = 0
for xx in range(abuy.left + 30, abuy.right - 30):
    r, g, b, _ = canvas.get_at((xx, abuy.centery))
    rs += r; gs += g; bs += b; n += 1
ar, ag, ab = rs / n, gs / n, bs / n
print(f"[3] BUY avg ({ar:.0f},{ag:.0f},{ab:.0f}) need R>180 B<100 -> "
      f"{'PASS' if ar > 180 and ab < 100 else 'FAIL'}")

# 4) can't-afford disc avg differs from affordable disc avg by >50 luminance
aff_lum = sum(lum(c) for c in disc_samples) / max(1, len(disc_samples))
nl = ntot = 0.0
for yy in range(ncy - ndr, ncy + ndr):
    for xx in range(ncx - ndr, ncx + ndr):
        if (xx - ncx) ** 2 + (yy - ncy) ** 2 > ndr * ndr:
            continue
        r, g, b, _ = canvas.get_at((xx, yy))
        nl += lum((r, g, b)); ntot += 1
noaff_lum = nl / max(1, ntot)
d = abs(aff_lum - noaff_lum)
print(f"[4] disc luminance afford={aff_lum:.1f} cant-afford={noaff_lum:.1f} "
      f"delta={d:.1f} need >50 -> {'PASS' if d > 50 else 'FAIL'}")
