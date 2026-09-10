#!/usr/bin/env python3
"""pedestal-pad confirm_purchase_v5 round 1 render.

Three tier panels side-by-side (RARE / EPIC / LEGENDARY). Each is a flat
rounded-rect plate card; the item disc sits on a RAISED circular pedestal pad
extruded ABOVE the plate face — a short cylinder standing proud, read via a lit
top-left crown rim, a side-wall gradient dark at its bottom edge, and a cast
contact shadow on the plate beneath it. The tier rim glow radiates OUTWARD
across the flat plate from the pedestal rim (additive annular bloom), and a
crisp gem ring rides the disc edge.
"""
import os, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, drop_shadow, bevel_rim, top_sheen, contact_shadow,
    plain_text, price_chip, chip_body_stops, chip_body, _stamp_bold,
    _glyph_base, font, m, SS,
    GOLD_A_STOPS, GOLD_A_RIM_DARK as GOLD_RIM_DK, GOLD_A_RIM_BRIGHT as GOLD_RIM_BR,
)
from game.hud import _font
from game.draw import lerp_color, WHITE, NEAR_BLACK


# BLEND_ADD ignores source alpha — keep the additive gloss sweep's intensity in
# RGB magnitude so gloss never blows the tier body to white.
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


# ── tier tracks ────────────────────────────────────────────────────────────────
TIERS = [
    ("RARE", "rare", "skin_wizard", "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC", "epic", "skin_prism", "1,400",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "legendary", "skin_aurora", "2,800",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]

PANEL_W, PANEL_H = 214, 306
CX = PANEL_W // 2
CARD_RAD = 16

R_DISC = 44          # item medallion
PAD_R = R_DISC + 15  # pedestal crown slightly larger than disc
PAD_H = 17           # extrusion height (crown sits this far above the plate face)
CY_TOP = 150         # crown-top centre y (logical)


# =============================================================================
# Gem-fill tier word — the dominant top focal
# =============================================================================
def gem_word(surf, txt, cx, cy, max_w, pal):
    """Tier word filled with the tier's own gem->deep vertical ramp, a bright
    crown edge, a crisp dark keyline and a soft drop shadow so it reads as the
    heavy first-glance focal above the pedestal."""
    sz = 30
    f = font(sz)
    while _glyph_base(txt, f, m(1.2)).get_width() > max_w and sz > 10:
        sz -= 1
        f = font(sz)
    base = _stamp_bold(_glyph_base(txt, f, m(1.2)), m(1.3))
    w, h = base.get_size()

    top = lerp_color(pal["gem"], WHITE, 0.40)
    grad = vgrad_stops(w, h, 0,
                       [(0.0, top), (0.42, pal["gem"]),
                        (1.0, lerp_color(pal["deep"], pal["gem"], 0.18))],
                       255, gamma=1.05)
    grad.blit(base, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    r = grad.get_rect(center=(cx, cy))

    # soft drop shadow first, then a crisp dark keyline the fill sits inside.
    sh = base.copy()
    sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sh.set_alpha(150)
    surf.blit(sh, (r.x, r.y + m(2)))
    kl = base.copy()
    kl.fill((4, 5, 16, 255), special_flags=pygame.BLEND_RGBA_MULT)
    p = m(1.1)
    for ang in range(0, 360, 45):
        surf.blit(kl, (r.x + int(round(p * math.cos(math.radians(ang)))),
                       r.y + int(round(p * math.sin(math.radians(ang))))))
    surf.blit(grad, r)


# =============================================================================
# Pedestal pad — a short cylinder extruded ABOVE the plate face
# =============================================================================
def pedestal(surf, cx, cy_top, pal):
    """Draw the raised pad: cast contact shadow on the plate, an extruded side
    wall (dark at its bottom edge), then a lit crown with a bright top-left rim.
    Depth reads UPWARD — the crown clearly stands proud of the plate."""
    # 1) cast shadow on the plate face, under + right of the pad (light top-left).
    sh_cy = cy_top + PAD_H + m(3)
    for i in range(m(9), 0, -1):
        a = int(120 * (i / m(9)) ** 1.7 / m(9) * 2.2)
        if a <= 0:
            continue
        rr = PAD_R + i
        s = pygame.Surface((rr * 2 + 2, int(rr * 1.5) + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, a), (1, 1, rr * 2, int(rr * 1.15)))
        surf.blit(s, (cx - rr - 1 + m(2), sh_cy - int(rr * 0.57)))

    # 2) side wall: stack circles from the bottom rim up to the crown so only the
    # lower crescent of each survives — a curved cylinder wall, darkest at its
    # foot. A top-left lit bias keeps the extrusion consistent with the light.
    wall_top = lerp_color(pal["deep"], pal["gem"], 0.16)
    wall_bot = lerp_color(pal["deep"], NEAR_BLACK, 0.55)
    for off in range(PAD_H, -1, -1):
        t = off / max(1, PAD_H)                     # 1 at foot .. 0 at crown
        col = lerp_color(wall_top, wall_bot, t ** 0.85)
        pygame.draw.circle(surf, col, (cx, cy_top + off), PAD_R)
    # lit sliver on the wall's upper-left, dark contact keyline at the very foot.
    pygame.draw.arc(surf, (*lerp_color(pal["gem"], WHITE, 0.25), 150),
                    (cx - PAD_R, cy_top - PAD_R, PAD_R * 2, PAD_R * 2),
                    math.radians(150), math.radians(205), max(1, m(1.4)))
    pygame.draw.arc(surf, (4, 6, 14),
                    (cx - PAD_R, cy_top + PAD_H - PAD_R, PAD_R * 2, PAD_R * 2),
                    math.radians(200), math.radians(340), max(1, m(1.6)))

    # 3) crown top face: a gently domed platform, tier-tinted, lit from top-left.
    face_ctr = lerp_color(pal["deep"], pal["gem"], 0.30)
    face_edge = lerp_color(pal["deep"], NEAR_BLACK, 0.18)
    for i in range(PAD_R, 0, -1):
        col = lerp_color(face_ctr, face_edge, (i / PAD_R) ** 1.5)
        pygame.draw.circle(surf, col, (cx, cy_top), i)
    # a bright top-left crown rim = the lit lip of the raised pad.
    rim = pygame.Surface((PAD_R * 2 + m(4), PAD_R * 2 + m(4)), pygame.SRCALPHA)
    rc = PAD_R + m(2)
    pygame.draw.arc(rim, (*lerp_color(pal["gem"], WHITE, 0.55), 235),
                    (rc - PAD_R, rc - PAD_R, PAD_R * 2, PAD_R * 2),
                    math.radians(96), math.radians(210), max(2, m(2.2)))
    surf.blit(rim, (cx - rc, cy_top - rc), special_flags=pygame.BLEND_ADD)
    # dark ambient occlusion where the disc will meet the crown.
    pygame.draw.circle(surf, (0, 0, 0, 120), (cx, cy_top), R_DISC + m(3),
                       max(1, m(2)))


def rim_bloom(surf, cx, cy, color):
    """Additive annular bloom spilling OUTWARD across the plate from the pedestal
    rim. BLEND_ADD ignores source alpha — intensity lives in RGB magnitude, so
    the tint values are kept small to avoid washing the plate white."""
    inner = PAD_R + m(1)
    for i in range(9, 0, -1):
        expand = int(m(24) * (9 - i + 0.5) / 9)
        outer = PAD_R + expand + 1
        frac = (9 - i) / 8
        col = tuple(max(0, int(c * (1 - frac) ** 1.6)) for c in color)
        if max(col) == 0:
            continue
        s = pygame.Surface((outer * 2 + 4, outer * 2 + 4), pygame.SRCALPHA)
        oc = outer + 2
        pygame.draw.circle(s, col, (oc, oc), outer)
        pygame.draw.circle(s, (0, 0, 0, 0), (oc, oc), inner)
        surf.blit(s, (cx - oc, cy - oc), special_flags=pygame.BLEND_ADD)


# =============================================================================
# One tier panel
# =============================================================================
def _confirm_chip(surf, cx, cy, h, pal):
    text = "CONFIRM"
    f = font(h * 0.46 / SS)
    nw = _glyph_base(text, f, m(1.4)).get_width()
    r = pygame.Rect(cx - (nw + m(40)) // 2, cy - h // 2, nw + m(40), h)
    chip_body_stops(surf, r, h // 2, GOLD_A_STOPS, GOLD_RIM_DK, GOLD_RIM_BR,
                    gloss=64, gamma=1.04)
    plain_text(surf, text, f, r.center, (54, 30, 4), shadow_a=0,
               tracking=m(1.4), weight=m(1.0))
    return r


def render_panel(tier_word, rarity, sid, price, pal):
    big = pygame.Surface((PANEL_W * SS, PANEL_H * SS), pygame.SRCALPHA)
    body = pygame.Rect(m(8), m(8), PANEL_W * SS - m(16), PANEL_H * SS - m(16))
    rad = m(CARD_RAD)

    # ── flat plate body ────────────────────────────────────────────────────────
    drop_shadow(big, body, rad, blur=m(7), alpha=155, dy=m(4))
    plate_t = lerp_color((28, 30, 62), pal["deep"], 0.30)
    plate_b = lerp_color((10, 11, 30), pal["deep"], 0.18)
    big.blit(vgrad_stops(body.w, body.h, rad, [(0.0, plate_t), (1.0, plate_b)],
                         255, gamma=1.14), body.topleft)
    top_sheen(big, body, rad, m(30), peak=46)
    contact_shadow(big, body, rad, m(9), alpha=110)
    pygame.draw.rect(big, (4, 5, 16), body, width=max(1, m(2)), border_radius=rad)
    bevel_rim(big, body, rad, (58, 48, 22), (*(236, 202, 116), 210), w=max(1, m(2)))
    tray = body.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*pal["gem"], 60), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))

    # ── tier word (dominant top focal) ─────────────────────────────────────────
    gem_word(big, tier_word, CX * SS, body.y + m(28), body.w - m(20), pal)

    cxd, cyd = CX * SS, m(CY_TOP)

    # ── rim glow radiating outward across the plate, BEFORE the pad covers it ───
    bloom_col = {"rare": (6, 15, 26), "epic": (15, 6, 24),
                 "legendary": (24, 16, 4)}[rarity]
    rim_bloom(big, cxd, cyd, bloom_col)

    # ── the raised pedestal pad ────────────────────────────────────────────────
    pedestal(big, cxd, cyd, pal)

    # ── the disc on the pad crown ──────────────────────────────────────────────
    sc.cabochon(big, cxd, cyd, m(R_DISC))
    try:
        t = sc.thumb(sid, int(m(R_DISC) * 1.5))
        boosted = t.copy()
        boosted.fill((18, 16, 8, 0), special_flags=pygame.BLEND_RGB_ADD)
        rt = boosted.get_rect(center=(cxd, cyd))
        big.blit(sc._rim_light(boosted), rt.topleft, special_flags=pygame.BLEND_ADD)
        big.blit(boosted, rt)
    except Exception:
        pygame.draw.circle(big, (*pal["gem"], 255), (cxd, cyd), int(m(R_DISC) * 0.7))
    sc.cabochon_glass(big, cxd, cyd, m(R_DISC), tint=pal["gem"])

    # crisp gem ring on the disc edge (part 2 of the two-part rim glow).
    pygame.draw.circle(big, lerp_color(pal["gem"], WHITE, 0.2), (cxd, cyd),
                       m(R_DISC) + m(1), max(2, m(2.4)))
    pygame.draw.circle(big, pal["deep"], (cxd, cyd), m(R_DISC) - m(1.4),
                       max(1, m(1)))

    # ── foot: price + confirm ──────────────────────────────────────────────────
    price_chip(big, cxd, body.bottom - m(56), price, m(22), affordable=True)
    _confirm_chip(big, cxd, body.bottom - m(24), m(24), pal)

    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


# =============================================================================
# Compose the three-panel review canvas
# =============================================================================
GAP = 18
MARGIN = 20
CANVAS_W = MARGIN * 2 + PANEL_W * 3 + GAP * 2
CANVAS_H = PANEL_H + 74
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    canvas.fill(lerp_color((14, 15, 30), (6, 6, 16), y / CANVAS_H), (0, y, CANVAS_W, 1))

title = _font(20, True)
tt = title.render("confirm_purchase_v5 - pedestal-pad - round 1", True, (224, 226, 240))
canvas.blit(tt, tt.get_rect(midtop=(CANVAS_W // 2, 12)))

lab = _font(13, True)
for i, (word, rarity, sid, price, pal) in enumerate(TIERS):
    panel = render_panel(word, rarity, sid, price, pal)
    px = MARGIN + i * (PANEL_W + GAP)
    py = 48
    canvas.blit(panel, (px, py))

out = "/home/user/skybit/docs/confirm_purchase_v5/pedestal-pad/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
