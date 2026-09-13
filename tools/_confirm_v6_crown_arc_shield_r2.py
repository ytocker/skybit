#!/usr/bin/env python3
"""crown-arc-shield confirm_purchase_v6 round 2.

Implements all art-director round-1 critique:
  1. Bloom fires 90-120 tier-excess above disc top: two BLEND_ADD layers — a tall
     vertical ellipse plume (centre nudged well above disc) plus a tight gem-tinted
     inner core — both on the opaque panel backdrop so the hue survives ADD.
  2. Legendary fixed to be the most radiant: the amber gem-core (255,202,104) is
     the hottest of the three; LEGENDARY also gets a 25% taller/wider plume.
  3. Confirm chip tinted per tier palette instead of universal warm gold.
  4. Ribbon shrunk to 1.3× — a compact secondary label, not a rival focal mass.
  5. Arc text uses a gentler radius (+22 logical px vs r1's +15) and font(11) so
     per-glyph rotation stays ≤ ~10° on short words like RARE.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, plain_text, _stamp_bold, _glyph_base, font, m, SS,
)
from game.hud import _font
from game.draw import lerp_color, WHITE, NEAR_BLACK


# Apply gloss_sweep monkey-patch BEFORE any render calls.
# BLEND_ADD reads only RGB, not source alpha; the original's alpha-based sweep
# writes alpha=0 into the destination, so the body reads dark on the panel.
# This version writes the ramp as RGB magnitude (all 255 alpha) clipped to the
# rounded-rect mask via BLEND_RGBA_MIN before the ADD blit.
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


# ── tier tracks (brief palette) ───────────────────────────────────────────────
TIERS = [
    ("RARE",      "rare",      "skin_wizard", "720",
     {"gem": (108, 188, 252), "glow": (60,  140, 230), "deep": (18,  44,  90)}),
    ("EPIC",      "epic",      "skin_prism",  "1,400",
     {"gem": (194, 122, 248), "glow": (150,  60, 220), "deep": (44,  10,  80)}),
    ("LEGENDARY", "legendary", "skin_aurora", "2,800",
     {"gem": (255, 202, 104), "glow": (220, 160,  40), "deep": (90,  50,   0)}),
]

PANEL_W, PANEL_H = 200, 340
BG_TOP, BG_BOT = (14, 15, 30), (6, 6, 16)
GAP = 16
MARGIN = 20
CANVAS_W = MARGIN * 2 + PANEL_W * 3 + GAP * 2
CANVAS_H = PANEL_H + 74
PANEL_Y = 48

# Shield geometry (logical px)
CARD_L, CARD_R = 14, 186
CARD_TOP = 88
SHOULDER_Y = 268
TIP_X, TIP_Y = 100, 322

R_DISC = 48      # hero disc radius (logical)
CY_DISC = 98     # disc centre y (logical); 40% of disc overhangs CARD_TOP


# =============================================================================
# Shield outline helpers
# =============================================================================
def _unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    l = math.hypot(dx, dy) or 1.0
    return dx / l, dy / l


def _fillet(P0, P1, P2, r, steps=12):
    """Circular-arc fillet rounding corner P1 between edges P0->P1 and P1->P2."""
    v1 = _unit(P1, P0)
    v2 = _unit(P1, P2)
    dot = max(-1.0, min(1.0, v1[0] * v2[0] + v1[1] * v2[1]))
    ang = math.acos(dot)
    if ang < 1e-3 or abs(ang - math.pi) < 1e-3:
        return [P1]
    tan = r / math.tan(ang / 2)
    t1 = (P1[0] + v1[0] * tan, P1[1] + v1[1] * tan)
    bis = (v1[0] + v2[0], v1[1] + v2[1])
    bl = math.hypot(*bis) or 1.0
    bis = (bis[0] / bl, bis[1] / bl)
    center = (P1[0] + bis[0] * r / math.sin(ang / 2),
              P1[1] + bis[1] * r / math.sin(ang / 2))
    t2 = (P1[0] + v2[0] * tan, P1[1] + v2[1] * tan)
    a1 = math.atan2(t1[1] - center[1], t1[0] - center[0])
    a2 = math.atan2(t2[1] - center[1], t2[0] - center[0])
    da = a2 - a1
    while da > math.pi:
        da -= 2 * math.pi
    while da < -math.pi:
        da += 2 * math.pi
    return [(center[0] + r * math.cos(a1 + da * i / steps),
             center[1] + r * math.sin(a1 + da * i / steps))
            for i in range(steps + 1)]


def shield_outline():
    A = (m(CARD_L),  m(CARD_TOP))
    B = (m(CARD_R),  m(CARD_TOP))
    C = (m(CARD_R),  m(SHOULDER_Y))
    T = (m(TIP_X),   m(TIP_Y))
    D = (m(CARD_L),  m(SHOULDER_Y))
    rc, rs, rt = m(15), m(9), m(12)
    out = []
    out += _fillet(D, A, B, rc)
    out += _fillet(A, B, C, rc)
    out += _fillet(B, C, T, rs)
    out += _fillet(C, T, D, rt)
    out += _fillet(T, D, A, rs)
    return out


def _centroid(pts):
    return (sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts))


# =============================================================================
# Tier bloom — two BLEND_ADD layers on the opaque panel backdrop.
#
# Layer 1 — outer vertical ellipse plume: tall so the coloured mass pools well
# above the disc into the headroom; slow falloff (^0.80) keeps the mid-zone
# bright rather than fading quickly from the centre.
#
# Layer 2 — inner gem-core: a compact radial circle at the disc centre using
# the tier's GEM colour (brighter than the glow). This is critical for
# LEGENDARY: glow=(220,160,40) has lower perceptual brightness than RARE blue
# or EPIC purple via BLEND_ADD on a dark background; the gem core (255,202,104)
# recovers that by adding a concentrated amber burst at the disc.
#
# plume_scale > 1.0 for LEGENDARY gives it the tallest/widest plume so it
# clearly out-reads the other two tiers.
# =============================================================================
def crown_glow(surf, cx, cy, r, glow_col, gem_col, plume_scale=1.0):
    px = int(r * 2.4 * plume_scale)
    py = int(r * 3.5 * plume_scale)
    steps = 52
    plume = pygame.Surface((px * 2 + 4, py * 2 + 4), pygame.SRCALPHA)
    pc_x, pc_y = px + 2, py + 2
    for i in range(steps, 0, -1):
        ex = int(px * i / steps)
        ey = int(py * i / steps)
        if ex <= 0 or ey <= 0:
            continue
        t = i / steps
        inten = (1.0 - t) ** 0.80
        col = tuple(max(0, min(255, int(c * inten))) for c in glow_col)
        pygame.draw.ellipse(plume, (*col, 255),
                            (pc_x - ex, pc_y - ey, ex * 2, ey * 2))
    # Centre the plume well above the disc so the bright body sits in headroom
    plume_cy = cy - int(r * 1.70 * plume_scale)
    pr = plume.get_rect(center=(cx, plume_cy))
    surf.blit(plume, pr.topleft, special_flags=pygame.BLEND_ADD)

    # Gem-core: saturated hue burst at disc centre
    cr_r = int(r * 1.35)
    core = pygame.Surface((cr_r * 2 + 4, cr_r * 2 + 4), pygame.SRCALPHA)
    cc = cr_r + 2
    for i in range(28, 0, -1):
        rad = int(cr_r * i / 28)
        if rad <= 0:
            continue
        t = i / 28
        inten = (1.0 - t) ** 1.05
        col = tuple(max(0, min(255, int(c * inten))) for c in gem_col)
        pygame.draw.circle(core, (*col, 255), (cc, cc), rad)
    cpos = core.get_rect(center=(cx, cy))
    surf.blit(core, cpos.topleft, special_flags=pygame.BLEND_ADD)


# =============================================================================
# Arc text — gentler radius and smaller font keep per-glyph rotation small.
# At font(11) and radius = R_DISC + 22, "RARE" (4 glyphs) spans ~28° total
# so the outermost glyph rotates only ~7° — smooth rather than jittery.
# =============================================================================
def _arc_glyph(ch, f, fill, key):
    base = _stamp_bold(f.render(ch, True, WHITE), m(1.0))
    w, h = base.get_size()
    pad = m(2)
    g = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    kl = base.copy()
    kl.fill((*key, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for ang in range(0, 360, 45):
        g.blit(kl, (pad + int(round(m(1) * math.cos(math.radians(ang)))),
                    pad + int(round(m(1) * math.sin(math.radians(ang))))))
    img = base.copy()
    img.fill((*fill, 255), special_flags=pygame.BLEND_RGBA_MULT)
    g.blit(img, (pad, pad))
    return g


def arc_text(surf, word, cx, cy, radius, pal):
    f = font(11)
    fill = lerp_color(pal["gem"], WHITE, 0.30)
    key  = lerp_color(pal["deep"], NEAR_BLACK, 0.35)
    glyphs = [_arc_glyph(ch, f, fill, key) for ch in word]
    widths = [g.get_width() for g in glyphs]
    track  = m(2)
    total  = sum(widths) + track * (len(glyphs) - 1)

    span_deg = math.degrees(total / radius)
    back = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(back,
                    (*lerp_color(pal["deep"], NEAR_BLACK, 0.2), 130),
                    (cx - radius, cy - radius, radius * 2, radius * 2),
                    math.radians(270 - span_deg * 0.6),
                    math.radians(270 + span_deg * 0.6),
                    max(2, m(10)))
    surf.blit(back, (0, 0))

    s = -total / 2.0
    for g, w in zip(glyphs, widths):
        sc_pos   = s + w / 2.0
        angle_rad = sc_pos / radius
        beta     = math.radians(270) + angle_rad
        x = cx + radius * math.cos(beta)
        y = cy + radius * math.sin(beta)
        rot = pygame.transform.rotate(g, -math.degrees(angle_rad))
        surf.blit(rot, rot.get_rect(center=(int(x), int(y))))
        s += w + track


# =============================================================================
# Compact rarity ribbon — 1.3× keeps it a legible secondary badge without
# becoming a third focal mass competing with the disc + arc crown above it.
# The rarity word is already stamped by sc._ribbon; the size reduction just
# resets the hierarchy so disc → arc text → ribbon (not disc = arc = ribbon).
# =============================================================================
def scaled_ribbon(surf, word, cx, cy, pal, scale=1.3):
    sw, sh = m(150), m(30)
    scratch = pygame.Surface((sw, sh), pygame.SRCALPHA)
    sc._ribbon(scratch, word, sw // 2, sh // 2, m(130), pal)
    bb = scratch.get_bounding_rect()
    if bb.width > 0 and bb.height > 0:
        scratch = scratch.subsurface(bb).copy()
    big = pygame.transform.smoothscale(
        scratch,
        (int(scratch.get_width() * scale), int(scratch.get_height() * scale)))
    surf.blit(big, big.get_rect(center=(cx, cy)))


# =============================================================================
# Per-tier confirm chip — body colour derived from the tier palette so each
# tier's call-to-action reads as part of its own colour system.
# RARE → blue pill, EPIC → purple pill, LEGENDARY → amber pill.
# =============================================================================
def tier_confirm_chip(surf, cx, cy, price, h, pal):
    gem   = pal["gem"]
    deep  = pal["deep"]
    top_c = lerp_color(deep, gem, 0.42)
    bot_c = lerp_color(deep, NEAR_BLACK, 0.12)
    rim_b = lerp_color(gem, WHITE, 0.28)
    rim_d = lerp_color(deep, NEAR_BLACK, 0.68)
    text_c = lerp_color(gem, WHITE, 0.52)
    coin_rim = lerp_color(gem, NEAR_BLACK, 0.28)

    coin_d = int(h * 0.66)
    pad    = m(13)
    gapc   = m(8)
    f      = font(h * 0.50 / SS)
    nw     = _glyph_base(price, f, 0).get_width() + m(2)
    w      = pad + coin_d + gapc + nw + pad
    r      = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    # chip_body_stops calls sc.gloss_sweep, which is already monkey-patched
    sc.chip_body_stops(surf, r, h // 2,
                       [(0.0, top_c), (1.0, bot_c)],
                       rim_d, rim_b, gloss=48, gamma=1.06)
    x = r.x + pad
    sc.coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2, rim=coin_rim)
    x += coin_d + gapc
    plain_text(surf, price, f, (x + nw // 2, cy), text_c,
               shadow_a=0, weight=m(1.0))
    return r


# =============================================================================
# One tier panel
# =============================================================================
def render_panel(word, rarity, sid, price, pal):
    big = pygame.Surface((PANEL_W * SS, PANEL_H * SS), pygame.SRCALPHA)
    # Fill opaque backdrop first so BLEND_ADD bloom has a real scene to add onto
    for ry in range(PANEL_H * SS):
        f = (PANEL_Y + ry / SS) / CANVAS_H
        big.fill(lerp_color(BG_TOP, BG_BOT, min(1.0, f)),
                 (0, ry, PANEL_W * SS, 1))

    outline = shield_outline()
    ctr     = _centroid(outline)

    # cast drop shadow
    dy = m(4)
    for i in range(m(8), 0, -1):
        a = int(160 * (i / m(8)) ** 1.7 / m(8) * 2.4)
        if a <= 0:
            continue
        pts = [(x - _unit((x, y), ctr)[0] * i,
                y - _unit((x, y), ctr)[1] * i + dy)
               for (x, y) in outline]
        pygame.draw.polygon(big, (0, 0, 0, a), pts)

    # shield body: tier-tinted vertical gradient masked to the heraldic silhouette
    bx, by = m(CARD_L), m(CARD_TOP)
    bw, bh = m(CARD_R) - m(CARD_L), m(TIP_Y) - m(CARD_TOP)
    plate_t = lerp_color((28, 30, 70), pal["deep"], 0.30)
    plate_b = lerp_color((12, 13, 38), pal["deep"], 0.18)
    grad  = vgrad_stops(bw, bh, 0, [(0.0, plate_t), (1.0, plate_b)], 255, gamma=1.15)
    local = [(x - bx, y - by) for (x, y) in outline]
    mask  = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sheen = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(m(40)):
        pygame.draw.line(sheen,
                         (255, 255, 255, int(58 * (1 - y / m(40)) ** 1.3)),
                         (0, y), (bw, y))
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    grad.blit(sheen, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    big.blit(grad, (bx, by))

    # shield edge: dark keyline + top-lit gold bevel + faint tier tray
    pygame.draw.polygon(big, (4, 5, 16), outline, width=max(1, m(2)))
    inset = [(x + _unit((x, y), ctr)[0] * m(2),
              y + _unit((x, y), ctr)[1] * m(2)) for (x, y) in outline]
    for j in range(len(inset)):
        x1, y1 = inset[j]
        x2, y2 = inset[(j + 1) % len(inset)]
        ny = ((y1 + y2) / 2 - by) / max(1, bh)
        a  = max(70, int(235 * (1 - ny) ** 1.1))
        pygame.draw.line(big, (236, 202, 116, a), (x1, y1), (x2, y2), max(1, m(2)))
    tray = [(x + _unit((x, y), ctr)[0] * m(5),
             y + _unit((x, y), ctr)[1] * m(5)) for (x, y) in outline]
    pygame.draw.polygon(big, (*pal["gem"], 55), tray, width=max(1, m(1)))

    cxd, cyd = m(TIP_X), m(CY_DISC)

    # tier bloom BEFORE the disc — fires upward into headroom; disc covers the
    # core at its centre but the plume reads freely above. LEGENDARY gets 25%
    # larger plume so it is unmistakably the most radiant panel.
    plume_scale = 1.25 if word == "LEGENDARY" else 1.0
    crown_glow(big, cxd, cyd, m(R_DISC), pal["glow"], pal["gem"],
               plume_scale=plume_scale)

    # hero disc
    sc.cabochon(big, cxd, cyd, m(R_DISC))
    try:
        sc.blit_thumb(big, sid, cxd, cyd, int(m(R_DISC) * 1.4))
    except Exception:
        pygame.draw.circle(big, (*pal["gem"], 255), (cxd, cyd),
                           int(m(R_DISC) * 0.7))
    sc.cabochon_glass(big, cxd, cyd, m(R_DISC), tint=pal["gem"])

    # arc-text crown — radius +22 logical px for a gentler per-glyph angle
    arc_text(big, word, cxd, cyd, m(R_DISC) + m(22), pal)

    # compact ribbon (1.3×) + name + tier-tinted confirm chip
    scaled_ribbon(big, word, cxd, m(178), pal)
    plain_text(big, sc._name(sid), font(15), (cxd, m(208)), (246, 244, 232),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    tier_confirm_chip(big, cxd, m(250), price, m(46), pal)

    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


# =============================================================================
# Canvas
# =============================================================================
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
for y in range(CANVAS_H):
    canvas.fill(lerp_color(BG_TOP, BG_BOT, y / CANVAS_H), (0, y, CANVAS_W, 1))

title = _font(20, True)
tt = title.render("confirm_purchase_v6 – crown-arc-shield – round 2",
                  True, (224, 226, 240))
canvas.blit(tt, tt.get_rect(midtop=(CANVAS_W // 2, 12)))

for i, (word, rarity, sid, price, pal) in enumerate(TIERS):
    panel = render_panel(word, rarity, sid, price, pal)
    px = MARGIN + i * (PANEL_W + GAP)
    canvas.blit(panel, (px, PANEL_Y))

out = "/home/user/skybit/docs/confirm_purchase_v6/crown-arc-shield/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print("saved", out, canvas.get_size())
