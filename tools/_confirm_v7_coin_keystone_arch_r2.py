#!/usr/bin/env python3
"""
coin-keystone-arch  ·  confirm_purchase_v7  ·  round 2

Raised gable crown now pokes 24 logical px above the hero disc; gold
bevel ridges resolve the ascending arch edges into a crisp Gothic point;
voussoir compression marks from the octagon's top facets sell the
keystone-wedge read; BUY and CANCEL piers carry distinct warm-amber vs
cool-indigo identities with pressable face insets; an ornamental gem
fills the inter-pier gap; octagon pushed to cy=230 opens an 8 px
breathing gap between disc bottom and octagon top.
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
    vgrad_stops, plain_text, m, SS, font,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
    GOLD_A_STOPS, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_GAMMA,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image


# ── mandatory gloss_sweep patch ───────────────────────────────────────────────
# BLEND_ADD reads RGB directly (source alpha is ignored), so sheen lives in
# the RGB channels of the sweep surface rather than the alpha channel.
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


# ── tier palette ──────────────────────────────────────────────────────────────
TIERS = [
    ("RARE",      "skin_wizard",    "720",
     {"gem": (108, 188, 252), "glow": (60, 140, 230), "deep": (18, 44, 90)}),
    ("EPIC",      "skin_prism",     "1,400",
     {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut", "2,600",
     {"gem": (255, 202, 104), "glow": (220, 160, 40), "deep": (90, 50, 0)}),
]
NAMES = {"RARE": "WIZARD", "EPIC": "PRISM", "LEGENDARY": "ASTRONAUT"}


# ── popup metrics (logical px; all geometry flows through m()) ─────────────────
POP_W, POP_H = 260, 442
CX = 130

PLATE_X = 10
PLATE_W = 240
CORNER  = 13

# Apex raised 37 px from round-1's 95 so the Gothic crown clears the hero
# disc's top edge (disc top ≈ y=82, apex at y=58 → 24 px above).
APEX_Y    = 58
SHOULDER_Y = 160
BOTTOM_Y  = 438
APEX_PT   = 22          # Bézier control-point half-spread at shoulder level

# Hero disc anchored at disc crown; disc bottom = 135+53 = 188.
R_DISC  = 53
CY_DISC = 135

# Octagon pushed 5 px lower than round-1 so its top (230−34=196) clears
# the disc bottom (188) by a clean 8 px gap.
KEY_CX, KEY_CY, KEY_R = 130, 230, 34


# ── geometry helpers ──────────────────────────────────────────────────────────
def _quad(p0, p1, p2, steps):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        pts.append((u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0],
                    u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1]))
    return pts


def _arc(cx, cy, r, a0, a1, steps):
    pts = []
    for i in range(steps + 1):
        a = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def arch_path():
    """Closed pointed-arch silhouette (device px), flat bottom.

    Shoulders at SHOULDER_Y; Bézier halves converge to APEX_Y so the Gothic
    point sits well above the hero disc rather than blending into it."""
    L   = m(PLATE_X)
    Rr  = m(PLATE_X + PLATE_W)
    cor = m(CORNER)
    aY  = m(APEX_Y)
    shY = m(SHOULDER_Y)
    bY  = m(BOTTOM_Y)
    cxd = m(CX)
    dx  = m(APEX_PT)

    pts = []
    # rounded top-left shoulder
    pts += _arc(L + cor, shY + cor, cor, 180, 270, 6)
    # left ascending arm → pointed apex
    pts += _quad((L + cor, shY), (cxd - dx, shY), (cxd, aY), 20)[1:]
    # right descending arm from apex
    pts += _quad((cxd, aY), (cxd + dx, shY), (Rr - cor, shY), 20)[1:]
    # rounded top-right shoulder + right side + flat bottom
    pts += _arc(Rr - cor, shY + cor, cor, 270, 360, 6)
    pts += _arc(Rr - cor, bY - cor, cor, 0, 90, 6)
    pts += _arc(L + cor, bY - cor, cor, 90, 180, 6)
    return pts


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _inset(pts, d):
    """Radial shrink toward centroid — sufficient for thin bevel strokes."""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    out = []
    for px, py in pts:
        vx, vy = cx - px, cy - py
        ln = math.hypot(vx, vy) or 1
        out.append((px + vx / ln * d, py + vy / ln * d))
    return out


# ── plate finish ──────────────────────────────────────────────────────────────
def poly_drop_shadow(base, pts, blur, alpha, dy):
    """Soft outer shadow for the free-form arch polygon."""
    minx, miny, maxx, maxy = _bbox(pts)
    pad = blur + dy + m(4)
    w = int(maxx - minx + pad * 2)
    h = int(maxy - miny + pad * 2)
    lp = [(p[0] - minx + pad, p[1] - miny + pad) for p in pts]
    shape = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(shape, (0, 0, 0, 255), lp)
    acc = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 1.7 / blur * 2.6)
        if a <= 0:
            continue
        tmp = shape.copy()
        tmp.fill((255, 255, 255, a), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 45):
            ox = int(round(i * math.cos(math.radians(ang))))
            oy = int(round(i * math.sin(math.radians(ang))))
            acc.blit(tmp, (ox, oy), special_flags=pygame.BLEND_RGBA_MAX)
    base.blit(acc, (int(minx - pad), int(miny - pad + dy)))


def poly_bevel(base, pts):
    """Emboss: bright inner stroke above dark outer keyline.

    Works on any closed polygon — arch outline or octagon."""
    minx, miny, maxx, maxy = _bbox(pts)
    pad = m(3)
    w = int(maxx - minx + pad * 2)
    h = int(maxy - miny + pad * 2)
    off = (int(minx - pad), int(miny - pad))
    inner = _inset(pts, m(2.2))
    lp_in = [(p[0] - off[0], p[1] - off[1]) for p in inner]
    hl = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(hl, (*CARD_RING_BRIGHT, 235), lp_in, width=max(1, m(1.4)))
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        a = int(255 * (1 - y / h) ** 1.5)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (w, y))
    hl.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(hl, off)
    pygame.draw.polygon(base, (4, 5, 16), pts, width=max(1, m(2)))


def masked_top_sheen(base, pts, mask, peak=58):
    """Glossy crown highlight clipped to the arch silhouette."""
    minx, miny, maxx, maxy = _bbox(pts)
    w = int(maxx - minx)
    h = int(maxy - miny)
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    span = int(h * 0.42)
    for y in range(span):
        a = int(peak * (1 - y / span) ** 1.4)
        pygame.draw.line(sheen, (255, 255, 255, a), (0, y), (w, y))
    sheen.blit(mask, (-int(minx), -int(miny)), special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(sheen, (int(minx), int(miny)))


# ── gable bevel highlights on ascending arch edges (note 1) ──────────────────
def _arch_gable_highlights(base):
    """Bright gold strokes covering the last 20 logical px of each ascending
    arch edge up to the apex — these two converging lines resolve the pointed
    crown as a crisp architectural ridge rather than a soft gradient fringe."""
    apex = (m(CX), m(APEX_Y))
    # Shoulders are roughly at the plate corners
    for sh in ((m(PLATE_X + CORNER), m(SHOULDER_Y)),
               (m(PLATE_X + PLATE_W - CORNER), m(SHOULDER_Y))):
        dx = apex[0] - sh[0]
        dy = apex[1] - sh[1]
        dist = math.hypot(dx, dy) or 1
        # Walk back 20 logical px from the apex along the edge direction
        sx = int(round(apex[0] - dx / dist * m(20)))
        sy = int(round(apex[1] - dy / dist * m(20)))
        hl = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        pygame.draw.line(hl, (*CARD_RING_BRIGHT, 200),
                         (sx, sy), apex, max(1, m(2)))
        base.blit(hl, (0, 0))


# ── voussoir compression lines from octagon top facets (note 2) ──────────────
def _voussoir_lines(base):
    """Four short radial stubs starting at the octagon's top facet edges and
    extending 5 logical px outward — masonry joint marks that converge into the
    keystone and sell the wedge-locking compression metaphor."""
    kcx = m(KEY_CX)
    kcy = m(KEY_CY)
    kr  = m(KEY_R)
    ext = m(5)
    # v7 (−135°), mid TL (−112.5°), mid TR (−67.5°), v1 (−45°)
    for deg in (-135.0, -112.5, -67.5, -45.0):
        rad = math.radians(deg)
        dx, dy = math.cos(rad), math.sin(rad)
        ex = int(round(kcx + kr * dx))
        ey = int(round(kcy + kr * dy))
        ox = int(round(kcx + (kr + ext) * dx))
        oy = int(round(kcy + (kr + ext) * dy))
        vl = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        pygame.draw.line(vl, (*CARD_RING_BRIGHT, 120),
                         (ex, ey), (ox, oy), max(1, m(1)))
        base.blit(vl, (0, 0))


# ── hero disc ─────────────────────────────────────────────────────────────────
def hero_disc(base, sid, gx, gy, r, pal):
    sc.cabochon(base, gx, gy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    sc.blit_thumb(base, sid, gx, gy, int(r * 1.5))
    sc.cabochon_glass(base, gx, gy, r, tint=pal["gem"])
    ring_w = max(3, m(3.0))
    pygame.draw.circle(base, pal["gem"], (gx, gy), r + ring_w // 2 + m(1), ring_w)
    pygame.draw.circle(base, lerp_color(pal["deep"], NEAR_BLACK, 0.35),
                       (gx, gy), r - m(1), max(1, m(1)))


# ── octagonal keystone medallion ──────────────────────────────────────────────
def octagon_pts(cx, cy, r):
    """8 vertices at radius r; vertex-0 at the top (point-up orientation)."""
    return [(cx + r * math.cos(math.radians(-90 + 45 * i)),
             cy + r * math.sin(math.radians(-90 + 45 * i))) for i in range(8)]


def keystone(base, pal, price_str):
    kcx, kcy, kr = m(KEY_CX), m(KEY_CY), m(KEY_R)

    # feathered aura
    sc._alpha_aura(base, kcx, kcy, m(KEY_R + 16), pal["glow"], peak=55, layers=15)

    # octagonal metallic face
    pts = octagon_pts(kcx, kcy, kr)
    minx, miny, maxx, maxy = _bbox(pts)
    w = int(maxx - minx) + 2
    h = int(maxy - miny) + 2
    stops = [(0.0, pal["deep"]),
             (0.5, pal["gem"]),
             (1.0, lerp_color(pal["gem"], WHITE, 0.30))]
    body = vgrad_stops(w, h, 0, stops, 255, gamma=1.08)
    fmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(fmask, (255, 255, 255, 255),
                        [(px - minx, py - miny) for px, py in pts])
    body.blit(fmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(body, (int(minx), int(miny)))

    # emboss + dark contact keyline
    poly_bevel(base, pts)
    pygame.draw.polygon(base, (4, 5, 16), pts, m(2))

    # shoulder gems flanking the keystone
    sc.facet_gem(base, m(103), kcy, m(6), pal["gem"], pal["deep"])
    sc.facet_gem(base, m(157), kcy, m(6), pal["gem"], pal["deep"])

    # coin face + price (y adjusted to follow the pushed-down octagon cy)
    sc.coin_glyph(base, kcx, kcy, m(26))
    plain_text(base, price_str, font(12), (kcx, m(234)), pal["gem"],
               shadow_a=150, weight=m(1.2), keyline=(6, 6, 16), kw=m(1.0))

    # voussoir compression stubs — drawn on top of the octagon face
    _voussoir_lines(base)


# ── pier button — differentiated BUY (warm) vs CANCEL (cool) (note 3) ────────
def pier(base, x, y, w, h, label, label_size, warm=False):
    """Tall arch pier-column button.

    warm=True (BUY): dark amber body, canonical gold capital, bright cream
    label — the gold/yes identity.
    warm=False (CANCEL): cool indigo body, muted bevel capital, dim label
    — the dark/no identity.

    Both have a 2 px inset pressable face so the active surface reads as a
    tappable button within the outer column frame."""
    rad = m(8)
    cap_h = m(10)

    if warm:
        fill_top   = (38, 30, 8)
        fill_bot   = (22, 17, 4)
        face_top   = (26, 20, 5)
        face_bot   = (14, 11, 2)
        label_col  = (250, 248, 240)
        bev_bright = CARD_RING_BRIGHT     # 3-tuple → bevel_rim adds alpha 220
        bev_dark   = CARD_RING_DEEP
    else:
        fill_top   = CARD_T
        fill_bot   = (16, 18, 40)
        face_top   = lerp_color(CARD_T, (0, 0, 0), 0.18)
        face_bot   = lerp_color((16, 18, 40), (0, 0, 0), 0.18)
        label_col  = (160, 164, 190)
        # 4-tuple so bevel_rim uses our explicit alpha (140 = muted)
        bev_bright = (*lerp_color(CARD_RING_BRIGHT, (200, 220, 255), 0.45), 140)
        bev_dark   = CARD_RING_DEEP

    # column shaft body
    body = vgrad_stops(w, h, 0, [(0.0, fill_top), (1.0, fill_bot)], 255, gamma=1.15)
    bmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(bmask, (255, 255, 255, 255), (0, 0, w, h),
                     border_top_left_radius=rad, border_top_right_radius=rad,
                     border_bottom_left_radius=m(3), border_bottom_right_radius=m(3))
    body.blit(bmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    base.blit(body, (x, y))

    # shaft bevel rim
    shaft_rect = pygame.Rect(x, y, w, h)
    sc.bevel_rim(base, shaft_rect, rad, bev_dark, bev_bright, max(1, m(2)))

    # pressable face — inset 2 px inside the shaft, sitting below the capital
    fi = m(2)
    face_x = x + fi
    face_y = y + cap_h + fi
    face_w = w - fi * 2
    face_h = h - cap_h - fi * 2
    face_rad = max(1, rad - m(1))
    face_surf = vgrad_stops(face_w, face_h, face_rad,
                            [(0.0, face_top), (1.0, face_bot)], 255, gamma=1.15)
    base.blit(face_surf, (face_x, face_y))

    # capital block — slightly wider cap crowning the column
    cap_w   = w + m(4)
    cap_rect = pygame.Rect(x + (w - cap_w) // 2, y, cap_w, cap_h)

    if warm:
        # Canonical gold fill for the BUY capital
        cbody = vgrad_stops(cap_w, cap_h, m(3), GOLD_A_STOPS, 255, gamma=GOLD_A_GAMMA)
        base.blit(cbody, cap_rect.topleft)
        sc.bevel_rim(base, cap_rect, m(3), GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT,
                     max(1, m(1.6)))
    else:
        # Muted indigo capital for CANCEL — alpha and bevel both dimmed
        cbody = vgrad_stops(cap_w, cap_h, m(3),
                            [(0.0, CARD_T), (1.0, CARD_B)], 190, gamma=1.15)
        base.blit(cbody, cap_rect.topleft)
        muted_bev = (*lerp_color(CARD_RING_BRIGHT, (180, 195, 230), 0.5), 140)
        sc.bevel_rim(base, cap_rect, m(3), CARD_RING_DEEP, muted_bev,
                     max(1, m(1.6)))

    # label centred on the pressable face
    plain_text(base, label, font(label_size), (x + w // 2, y + m(43)),
               label_col, shadow_a=150, weight=m(1.0),
               keyline=(6, 6, 16), kw=m(1.0))


# ── popup assembler ───────────────────────────────────────────────────────────
def _cancel_label():
    """Fit 'CANCEL' if the glyph clears the pier width, else fall back."""
    f = font(11)
    if sc._glyph_base("CANCEL", f, 0).get_width() <= m(84) - m(14):
        return "CANCEL", 11
    return "NO", 12


def render_popup(tier_word, sid, price, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    pts = arch_path()

    # 1) arch plate: drop shadow → indigo body → crown sheen → bevel
    poly_drop_shadow(big, pts, blur=m(8), alpha=165, dy=m(4))
    minx, miny, maxx, maxy = _bbox(pts)
    bw = int(maxx - minx) + m(2)
    bh = int(maxy - miny) + m(2)
    body = vgrad_stops(bw, bh, 0, [(0.0, CARD_T), (1.0, CARD_B)], 252, gamma=1.15)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - minx, p[1] - miny) for p in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(body, (int(minx), int(miny)))
    fmask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(fmask, (255, 255, 255, 255), pts)
    masked_top_sheen(big, pts, fmask, peak=60)
    poly_bevel(big, pts)

    # 2) hero disc seated in the arch crown
    hero_disc(big, sid, m(CX), m(CY_DISC), m(R_DISC), pal)

    # 3) bevel highlights on ascending arch edges — resolve the gable point
    _arch_gable_highlights(big)

    # 4) octagonal keystone (includes voussoir stubs on its outer top facets)
    keystone(big, pal, price)

    # 5) rarity lozenge in the spandrel below the keystone
    sc._ribbon_lozenge(big, tier_word, m(CX), m(292), m(PLATE_W - 60), pal)

    # 6) item name
    plain_text(big, NAMES[tier_word], font(14), (m(CX), m(320)), (250, 248, 240),
               shadow_a=150, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # 7) pier buttons — warm BUY (left) and cool CANCEL (right)
    pier(big, m(17), m(345), m(84), m(428 - 345), "BUY", 14, warm=True)
    clab, csize = _cancel_label()
    pier(big, m(159), m(345), m(84), m(428 - 345), clab, csize, warm=False)

    # 8) ornamental gem filling the gap between the two piers
    sc.facet_gem(big, m(130), m(394), m(6), pal["gem"], pal["deep"])

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── three-tier review strip, 2× LANCZOS ──────────────────────────────────────
GAP    = 12
MARGIN = 22
HEAD   = 58

CANVAS_W = MARGIN * 2 + POP_W * 3 + GAP * 2
CANVAS_H = HEAD + POP_H + 42

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((8, 8, 20))

title = _font(19, True).render(
    "confirm_purchase_v7  ·  coin-keystone-arch  ·  round 2", True, (232, 226, 208))
canvas.blit(title, (MARGIN, 14))
sub = _font(11, True).render(
    "raised gable · gold bevel ridge · voussoir joints · warm BUY / cool CANCEL · gem gap fill",
    True, (150, 156, 178))
canvas.blit(sub, (MARGIN, 37))

lab = _font(13, True)
for i, (word, sid, price, pal) in enumerate(TIERS):
    pop = render_popup(word, sid, price, pal)
    px = MARGIN + i * (POP_W + GAP)
    py = HEAD
    canvas.blit(pop, (px, py))
    t = lab.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(t, t.get_rect(midtop=(px + POP_W // 2, py + POP_H + 8)))

OUT = "/home/user/skybit/docs/confirm_purchase_v7/coin-keystone-arch/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Save base canvas first, then upscale 2× with LANCZOS for the review sheet
pygame.image.save(canvas, OUT)

img = Image.open(OUT)
w2, h2 = img.size[0] * 2, img.size[1] * 2
img2 = img.resize((w2, h2), Image.LANCZOS)
img2.save(OUT)
print("saved", OUT, img2.size)
print(f"arch apex y={APEX_Y} (above disc top y={CY_DISC - R_DISC})")
print(f"octagon top y={KEY_CY - KEY_R}, disc bottom y={CY_DISC + R_DISC}, gap={KEY_CY - KEY_R - (CY_DISC + R_DISC)} px")
